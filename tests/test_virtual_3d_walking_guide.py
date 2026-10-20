"""
Automated Test Suite for Realistic 3D Human Walking Guide & Visual Navigation
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Adaptive Transit System

Validates:
1. Local metric 3D coordinate transformations and inverse projections.
2. Resampling of route polyline, station calculation, bearings, and smooth curvature.
3. Turn maneuver identification (Left, Right, Straight, Curve, Crosswalk, Arrival).
4. State machine transitions (IDLE, WALKING_STRAIGHT, APPROACHING_TURN, TURNING_LEFT,
   TURNING_RIGHT, WAITING_AT_CROSSING, CROSSING, ARRIVING, ARRIVED, PAUSED, ROUTE_UNAVAILABLE).
5. Continuity of character position along route (no teleportation).
6. Accessibility cues (tactile warning blister paving, drop-curb ramps, audible signals).
7. HTML/Three.js scene builder rendering, graceful fallbacks for missing/invalid routes,
   and separation of Demonstration Mode vs Live Navigation Mode.
"""

import pytest
import math
from src.virtual_3d_walking_guide import (
    WalkingGuideState,
    NavigationManeuver3D,
    Route3DPoint,
    Route3DGeometryEngine,
    WalkingGuideAnimationController,
    build_3d_walking_guide_html
)


# =============================================================================
# 1. 3D GEOMETRY ENGINE & PROJECTION TESTS
# =============================================================================

def test_lat_lon_to_local_3d_projection():
    """Verify conversion of GPS lat/lon to metric Cartesian coordinates."""
    origin_lat, origin_lon = 16.2335, 80.5505

    # Origin should project to (0, 0, 0)
    x0, y0, z0 = Route3DGeometryEngine.lat_lon_to_local_3d(origin_lat, origin_lon, origin_lat, origin_lon)
    assert abs(x0) < 0.001
    assert abs(z0) < 0.001

    # Point north by ~110.5 meters
    lat_north = origin_lat + 0.001
    xn, yn, zn = Route3DGeometryEngine.lat_lon_to_local_3d(lat_north, origin_lon, origin_lat, origin_lon)
    assert abs(xn) < 1.0
    assert zn < -100.0  # Northing is negative Z in Three.js camera coordinate space

    # Point east by ~107 meters
    lon_east = origin_lon + 0.001
    xe, ye, ze = Route3DGeometryEngine.lat_lon_to_local_3d(origin_lat, lon_east, origin_lat, origin_lon)
    assert xe > 90.0
    assert abs(ze) < 1.0


def test_inverse_projection_roundtrip():
    """Verify local 3D Cartesian coordinates can be accurately transformed back to lat/lon."""
    origin_lat, origin_lon = 16.2335, 80.5505
    test_lat, test_lon = 16.2380, 80.5550

    x, y, z = Route3DGeometryEngine.lat_lon_to_local_3d(test_lat, test_lon, origin_lat, origin_lon)
    reconstructed_lat, reconstructed_lon = Route3DGeometryEngine.local_3d_to_lat_lon(x, z, origin_lat, origin_lon)

    assert abs(reconstructed_lat - test_lat) < 1e-5
    assert abs(reconstructed_lon - test_lon) < 1e-5


def test_bearing_and_angle_difference():
    """Verify bearing computation and signed angular turn differences."""
    # Direct North: bearing should be ~0 deg
    b_north = Route3DGeometryEngine.calculate_bearing(16.0, 80.0, 16.01, 80.0)
    assert abs(b_north - 0.0) < 1.0 or abs(b_north - 360.0) < 1.0

    # Direct East: bearing should be ~90 deg
    b_east = Route3DGeometryEngine.calculate_bearing(16.0, 80.0, 16.0, 80.01)
    assert abs(b_east - 90.0) < 1.0

    # Direct South: bearing should be ~180 deg
    b_south = Route3DGeometryEngine.calculate_bearing(16.01, 80.0, 16.0, 80.0)
    assert abs(b_south - 180.0) < 1.0

    # Direct West: bearing should be ~270 deg
    b_west = Route3DGeometryEngine.calculate_bearing(16.0, 80.01, 16.0, 80.0)
    assert abs(b_west - 270.0) < 1.0

    # Turn from North (0 deg) to East (90 deg) is a +90 deg right turn
    assert Route3DGeometryEngine.calculate_angle_diff(0.0, 90.0) == 90.0

    # Turn from North (0 deg) to West (270 deg) is a -90 deg left turn
    assert Route3DGeometryEngine.calculate_angle_diff(0.0, 270.0) == -90.0


def test_clean_polyline_normalization():
    """Verify polyline normalization handles various coordinate formats and filters duplicates."""
    raw = [
        [16.2335, 80.5505],
        [16.2335001, 80.5505001],  # Duplicate (< 0.4m away)
        {"lat": 16.2350, "lon": 80.5520},
        (16.2370, 80.5540),
        "invalid_point"
    ]
    cleaned = Route3DGeometryEngine.clean_polyline(raw)
    assert len(cleaned) == 3
    assert cleaned[0] == (16.2335, 80.5505)
    assert cleaned[1] == (16.2350, 80.5520)
    assert cleaned[2] == (16.2370, 80.5540)


def test_resampled_3d_path_smoothness_and_no_teleportation():
    """Verify resampled 3D path provides smooth, continuous stationing without jumps/teleportation."""
    polyline = [
        (16.2335, 80.5505),
        (16.2350, 80.5505),  # Straight North ~165m
        (16.2350, 80.5520)   # Turn East ~160m
    ]
    resampled = Route3DGeometryEngine.generate_resampled_3d_path(polyline, resolution_m=2.0)
    assert len(resampled) > 50

    # Verify monotonic increasing stations
    for i in range(1, len(resampled)):
        prev_pt = resampled[i - 1]
        cur_pt = resampled[i]
        assert cur_pt.station_m > prev_pt.station_m

        # Verify step distance is smooth and continuous (no teleportation)
        dist_between = math.hypot(cur_pt.x - prev_pt.x, cur_pt.z - prev_pt.z)
        assert dist_between <= 2.8  # No large gaps


def test_curved_geometry_detection():
    """Verify curvature is properly calculated on road bends."""
    curved_poly = Route3DGeometryEngine.generate_synthetic_curved_polyline(
        origin_lat=16.2335, origin_lon=80.5505,
        dest_lat=16.2400, dest_lon=80.5570,
        num_points=15
    )
    resampled = Route3DGeometryEngine.generate_resampled_3d_path(curved_poly, resolution_m=2.0)

    # At least some points along the curve should have positive curvature
    curvatures = [pt.curvature for pt in resampled]
    assert any(c > 0.0 for c in curvatures)


# =============================================================================
# 2. MANEUVER EXTRACTION & ACCESSIBILITY TESTS
# =============================================================================

def test_maneuver_sequence_left_right_straight_and_crossings():
    """Verify turn maneuvers are classified correctly with crossings, ramps, and instructions."""
    steps = [
        {"instruction": "Start along Departure Corridor", "road": "Campus Ave", "distance_m": 120.0},
        {"instruction": "Turn left at Central Junction onto Link Road", "road": "Link Road", "distance_m": 180.0},
        {"instruction": "Continue straight along Link Road", "road": "Link Road", "distance_m": 220.0},
        {"instruction": "Turn right toward East Gate", "road": "East Approach", "distance_m": 140.0},
        {"instruction": "Arrive safely at East Campus Terminal", "road": "Terminal", "distance_m": 20.0}
    ]
    polyline = [
        (16.2335, 80.5505),
        (16.2360, 80.5520),
        (16.2380, 80.5540)
    ]
    maneuvers = Route3DGeometryEngine.build_maneuvers(
        steps=steps,
        polyline=polyline,
        total_distance_m=680.0,
        origin_name="Main Gate",
        dest_name="East Terminal"
    )

    assert len(maneuvers) == 5

    # 1. Step 0: START
    assert maneuvers[0].direction_type == "START"
    assert maneuvers[0].start_station_m == 0.0

    # 2. Step 1: LEFT TURN with crossing at junction
    assert maneuvers[1].direction_type == "LEFT"
    assert maneuvers[1].turn_angle_deg == -90.0
    assert maneuvers[1].has_crossing is True
    assert "left" in maneuvers[1].headline.lower()

    # 3. Step 2: STRAIGHT
    assert maneuvers[2].direction_type == "STRAIGHT"

    # 4. Step 3: RIGHT TURN with crossing at junction
    assert maneuvers[3].direction_type == "RIGHT"
    assert maneuvers[3].turn_angle_deg == 90.0
    assert maneuvers[3].has_crossing is True
    assert "right" in maneuvers[3].headline.lower()

    # 5. Step 4: ARRIVE
    assert maneuvers[4].direction_type == "ARRIVE"
    assert "arrive" in maneuvers[4].headline.lower()


def test_accessibility_tactile_and_ramp_notes_populated():
    """Verify that every maneuver includes accessible guidance notes and tactile paving indicators."""
    steps = [
        {"instruction": "Head out on accessible walkway", "distance_m": 100.0},
        {"instruction": "Turn left at crossing", "distance_m": 150.0},
        {"instruction": "Arrive at building", "distance_m": 50.0}
    ]
    maneuvers = Route3DGeometryEngine.build_maneuvers(steps, [(16.0, 80.0), (16.01, 80.01)], total_distance_m=300.0)

    for m in maneuvers:
        assert m.accessible_guidance != ""
        assert m.tactile_crossing_note != ""
        assert m.what_to_look_for != ""


# =============================================================================
# 3. ANIMATION STATE MACHINE & CONTROLLER TESTS
# =============================================================================

def test_controller_evaluates_straight_walking():
    """Verify forward walking state when traveling along a straight corridor."""
    steps = [
        {"instruction": "Proceed straight along Main Boulevard", "distance_m": 300.0},
        {"instruction": "Arrive at terminal", "distance_m": 10.0}
    ]
    maneuvers = Route3DGeometryEngine.build_maneuvers(steps, [(16.0, 80.0), (16.01, 80.0)], total_distance_m=310.0)
    controller = WalkingGuideAnimationController(maneuvers, total_distance_m=310.0)

    # At station 50m (in the middle of straight corridor)
    state, speed, active_m = controller.evaluate_state(station_m=50.0)
    assert state == WalkingGuideState.WALKING_STRAIGHT
    assert speed >= 1.2  # Normal walking speed (~1.35 m/s)


def test_controller_evaluates_turn_approach_and_execution():
    """Verify deceleration and state transitions when approaching and executing a left turn."""
    steps = [
        {"instruction": "Turn left at junction into Side Avenue", "direction_type": "LEFT", "distance_m": 100.0},
        {"instruction": "Arrive at terminal", "distance_m": 10.0}
    ]
    maneuvers = Route3DGeometryEngine.build_maneuvers(steps, [(16.0, 80.0), (16.01, 80.0)], total_distance_m=110.0)
    controller = WalkingGuideAnimationController(maneuvers, total_distance_m=110.0)

    # 10m before junction (station 90m): approaching turn, slows down
    st_appr, sp_appr, _ = controller.evaluate_state(station_m=90.0)
    assert st_appr == WalkingGuideState.APPROACHING_TURN
    assert sp_appr < 1.35

    # At junction (station 99m): turning left
    st_turn, sp_turn, _ = controller.evaluate_state(station_m=99.0)
    assert st_turn == WalkingGuideState.TURNING_LEFT
    assert sp_turn < sp_appr  # Slowest speed during turning arc


def test_controller_evaluates_crossing_stop_and_cross():
    """Verify pedestrian stop at curb ramp, waiting for signal, and safe crossing."""
    steps = [
        {"instruction": "Cross pedestrian zebra crossing at intersection", "direction_type": "CROSSING", "distance_m": 100.0},
        {"instruction": "Arrive at destination", "distance_m": 20.0}
    ]
    maneuvers = Route3DGeometryEngine.build_maneuvers(steps, [(16.0, 80.0), (16.01, 80.0)], total_distance_m=120.0)
    controller = WalkingGuideAnimationController(maneuvers, total_distance_m=120.0)

    # 2m before junction (station 98m): waiting at drop-curb ramp
    st_wait, sp_wait, _ = controller.evaluate_state(station_m=98.0)
    assert st_wait == WalkingGuideState.WAITING_AT_CROSSING
    assert sp_wait == 0.0  # Must be stopped!

    # On the zebra crosswalk (station 101m): crossing street
    st_cross, sp_cross, _ = controller.evaluate_state(station_m=101.0)
    assert st_cross == WalkingGuideState.CROSSING
    assert sp_cross > 0.0


def test_controller_evaluates_destination_arrival():
    """Verify arrival detection and deceleration at destination threshold."""
    steps = [
        {"instruction": "Walk to destination", "distance_m": 200.0},
        {"instruction": "Safely arrive at terminal", "direction_type": "ARRIVE", "distance_m": 10.0}
    ]
    maneuvers = Route3DGeometryEngine.build_maneuvers(steps, [(16.0, 80.0), (16.01, 80.0)], total_distance_m=210.0)
    controller = WalkingGuideAnimationController(maneuvers, total_distance_m=210.0)

    # Station 202m (within 8m of destination): ARRIVING
    st_arriving, sp_arriving, _ = controller.evaluate_state(station_m=202.0)
    assert st_arriving == WalkingGuideState.ARRIVING
    assert sp_arriving < 1.0

    # Station 209m (within 2.5m of destination): ARRIVED
    st_arrived, sp_arrived, _ = controller.evaluate_state(station_m=209.0)
    assert st_arrived == WalkingGuideState.ARRIVED
    assert sp_arrived == 0.0


def test_controller_pausing_and_resuming():
    """Verify pause state stops movement and preserves active position."""
    steps = [{"instruction": "Walk forward", "distance_m": 100.0}]
    maneuvers = Route3DGeometryEngine.build_maneuvers(steps, [(16.0, 80.0), (16.01, 80.0)], total_distance_m=100.0)
    controller = WalkingGuideAnimationController(maneuvers, total_distance_m=100.0)

    # Normal movement
    st_normal, sp_normal, _ = controller.evaluate_state(station_m=40.0, is_paused=False)
    assert st_normal == WalkingGuideState.WALKING_STRAIGHT
    assert sp_normal > 0.0

    # Paused state
    st_paused, sp_paused, m_paused = controller.evaluate_state(station_m=40.0, is_paused=True)
    assert st_paused == WalkingGuideState.PAUSED
    assert sp_paused == 0.0
    assert m_paused is not None  # Preserves maneuver context


# =============================================================================
# 4. HTML BUILDER & CLIENT COMPONENT TESTS
# =============================================================================

def test_build_3d_walking_guide_html_contains_required_elements():
    """Verify HTML component embeds Three.js, camera controllers, HUD, and accessibility controls."""
    origin = "Tenali Central Bus Station"
    dest = "Vignan University Main Gate"
    polyline = [
        [16.2435, 80.6405],
        [16.2450, 80.6420],
        [16.2470, 80.6450]
    ]
    steps = [
        {"instruction": "Head east along Station Road", "distance_m": 120.0},
        {"instruction": "Turn left onto Campus Corridor", "direction_type": "LEFT", "distance_m": 240.0},
        {"instruction": "Arrive at Main Gate", "direction_type": "ARRIVE", "distance_m": 40.0}
    ]

    html = build_3d_walking_guide_html(
        origin_name=origin,
        dest_name=dest,
        polyline=polyline,
        steps=steps,
        travel_mode="walking",
        total_distance_m=400.0
    )

    # Core elements
    assert "walking-guide-3d-root" in html
    assert "three.min.js" in html
    assert "viewport-3d-stage" in html
    assert "floating-instruction-card" in html
    assert "camera-toolbar" in html
    assert "crossing-banner" in html

    # Camera Modes
    assert "setCameraView" in html
    assert "cam-follow" in html
    assert "cam-instructor" in html
    assert "cam-drone" in html
    assert "cam-top" in html

    # 3D Kinematics and Character Logic
    assert "buildProceduralHumanoid" in html
    assert "animateCharacterLimbs" in html
    assert "gaitPhase" in html
    assert "TURNING_LEFT" in html
    assert "TURNING_RIGHT" in html
    assert "WAITING_AT_CROSSING" in html
    assert "CROSSING" in html

    # Accessibility & Zebra Crosswalks
    assert "buildZebraCrossing" in html
    assert "tactile" in html.lower()
    assert "drop-curb" in html.lower()

    # Voice & Audio Synthesis
    assert "speechSynthesis" in html
    assert "playSignalChime" in html

    # Resilient 2D Fallback
    assert "canvas-2d-fallback" in html
    assert "init2DFallback" in html


def test_build_3d_walking_guide_html_empty_inputs_graceful_fallback():
    """Verify build_3d_walking_guide_html succeeds gracefully with empty polyline and steps."""
    html = build_3d_walking_guide_html(
        origin_name="Start",
        dest_name="Destination",
        polyline=None,
        steps=None
    )
    assert "walking-guide-3d-root" in html
    assert "three.min.js" in html
    assert len(html) > 5000


def test_cute_human_character_features_in_html():
    """Verify cute, expressive human character elements: eyes, pupils, catchlights, smile, backpack, sneakers."""
    html = build_3d_walking_guide_html(
        origin_name="Admin Quad",
        dest_name="Library",
        polyline=[(16.2335, 80.5505), (16.2350, 80.5520)]
    )

    # Cute facial features
    assert "eyeWhiteL" in html
    assert "pupilL" in html
    assert "catchlightL" in html
    assert "leftEyelid" in html
    assert "rightEyelid" in html
    assert "smileMesh" in html
    assert "cheekL" in html
    assert "hairFringe" in html

    # Campus Explorer Attire
    assert "backpack" in html
    assert "compassBadge" in html
    assert "sneakerSole" in html


def test_natural_movement_and_animation_state_system():
    """Verify natural human movement system: jumping, blinking, idle breathing, and navigation states."""
    html = build_3d_walking_guide_html(
        origin_name="Campus West",
        dest_name="Innovation Hub",
        polyline=[(16.2335, 80.5505), (16.2350, 80.5520)]
    )

    # State machine and animations
    assert "triggerCuteHop" in html
    assert "JUMP_DURATION_MS" in html
    assert "blinkPhase" in html
    assert "state-JUMPING" in html
    assert "state-CELEBRATING" in html
    assert "state-ROUTE_DEVIATION" in html
    assert "btn-cute-hop" in html


def test_virtual_guide_box_alignment_and_responsive_layout():
    """Verify perfect box layout: no overlapping elements, clean padding, responsive margins."""
    html = build_3d_walking_guide_html(
        origin_name="Campus West",
        dest_name="Innovation Hub",
        polyline=[(16.2335, 80.5505), (16.2350, 80.5520)]
    )

    # Box alignment CSS rules
    assert "floating-instruction-card" in html
    assert "calc(100% - 130px)" in html
    assert "camera-toolbar" in html
    assert "@media (max-width: 680px)" in html

