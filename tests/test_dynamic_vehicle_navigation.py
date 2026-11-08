"""
Unit and Integration Tests for Dynamic Vehicle Mode-Based Virtual Guide Navigation
and Automatic Route Appearance Upon Location Selection.
"""

import pytest
from src.vehicle_navigation_controller import (
    TransportationMode,
    VehicleModeConfig,
    VehicleModeManager
)


def test_transportation_modes_enum():
    """Verify all transportation modes are enumerated."""
    modes = [m.value for m in TransportationMode]
    expected = ["CAR", "BIKE", "BUS", "FLIGHT", "WATERWAY", "TRUCK", "TRACTOR", "BICYCLE", "WALK", "TAXI", "TRAIN", "METRO"]
    for exp in expected:
        assert exp in modes, f"Mode {exp} must be defined in TransportationMode enum"


def test_vehicle_mode_manager_canonical_mapping():
    """Verify normalization and aliases map to valid configurations."""
    test_cases = [
        ("car", "CAR"),
        ("AUTOMOBILE", "CAR"),
        ("CAB", "TAXI"),
        ("taxi", "TAXI"),
        ("motorcycle", "BIKE"),
        ("bike", "BIKE"),
        ("scooter", "BIKE"),
        ("bus", "BUS"),
        ("transit", "BUS"),
        ("bicycle", "BICYCLE"),
        ("cycle", "BICYCLE"),
        ("pedestrian", "WALK"),
        ("walking", "WALK"),
        ("truck", "TRUCK"),
        ("lorry", "TRUCK"),
        ("tractor", "TRACTOR"),
        ("flight", "FLIGHT"),
        ("airplane", "FLIGHT"),
        ("waterway", "WATERWAY"),
        ("boat", "WATERWAY"),
        ("ferry", "WATERWAY"),
        ("train", "TRAIN"),
        ("rail", "TRAIN"),
        ("subway", "METRO"),
        ("metro", "METRO")
    ]
    for raw_input, expected_key in test_cases:
        config = VehicleModeManager.get_config(raw_input)
        assert config is not None, f"Config for {raw_input} must not be None"
        assert config.mode_id == expected_key, f"Expected {expected_key} for input {raw_input}, got {config.mode_id}"


def test_vehicle_mode_kinematics_and_camera():
    """Verify that every vehicle mode has speed, camera, and seat configuration."""
    all_modes = VehicleModeManager.get_all_configs()
    valid_poses = {"captain", "seated_car", "walking", "elevated_cab", "riding_moto", "cycling", "pilot"}
    for mode_id, cfg in all_modes.items():
        assert isinstance(cfg, VehicleModeConfig)
        assert cfg.default_speed_kmh > 0
        assert cfg.speed_factor > 0
        assert len(cfg.camera_offset) == 3
        assert len(cfg.camera_look_at) == 3
        assert len(cfg.seat_offset) == 3
        assert cfg.guide_pose in valid_poses


def test_threejs_vehicle_suite_js_generation():
    """Verify client-side Three.js vehicle suite code is properly generated."""
    js_code = VehicleModeManager.generate_threejs_vehicle_suite_js()
    assert "VehicleController" in js_code
    assert "VehicleModelLoader" in js_code
    assert "VirtualGuidePoseController" in js_code
    assert "VehicleModeManager" in js_code
    assert "buildVehicle" in js_code
    assert "updateKinematics" in js_code
    assert "setMode" in js_code


def test_auto_routes_generated_guard_in_app():
    """Verify that app.py has the automatic route appearance trigger when both coords are present."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # The guard ensures routes_generated is automatically enabled without requiring button clicks
    assert 'st.session_state.routes_generated = True' in content
    assert 'coords_orig and coords_dest and coords_orig != coords_dest' in content

    # Check that map-picking-card is hidden in google_maps_platform.py
    with open("src/google_maps_platform.py", "r", encoding="utf-8") as f_gmap:
        gmap_content = f_gmap.read()
    assert 'map-picking-card' in gmap_content
    assert 'display: none !important;' in gmap_content


def test_query_params_sync_destination_in_app():
    """Verify query params handling updates txt_dest, txt_orig and clears pending confirmation flags."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Verify txt_dest synchronization
    assert 'st.session_state.txt_dest = q_dest_name' in content
    assert 'st.session_state.txt_dest = p_name' in content
    assert 'st.session_state.dest_pending_confirmation = False' in content

    # Verify txt_orig synchronization
    assert 'st.session_state.txt_orig = q_orig_name' in content
    assert 'st.session_state.txt_orig = p_name' in content
    assert 'st.session_state.orig_pending_confirmation = False' in content


def test_global_route_engine_all_modes():
    """Verify route engine produces valid candidate routes across multiple modes."""
    from src.route_engine import RealWorldRouteEngine, TravelMode
    engine = RealWorldRouteEngine()

    # Test Flight
    flight_routes = engine.calculate_routes(17.3850, 78.4867, 12.9716, 77.5946, mode=TravelMode.FLIGHT)
    assert len(flight_routes) >= 3, "Flight mode must produce at least 3 airway corridors"
    assert any("FL330" in r.name or "Airway" in r.name for r in flight_routes)

    # Test Waterway
    water_routes = engine.calculate_routes(18.9220, 72.8347, 15.4909, 73.8278, mode=TravelMode.WATERWAY)
    assert len(water_routes) >= 2, "Waterway mode must produce at least 2 maritime corridors"
    assert any("Waterway" in r.name or "Channel" in r.name for r in water_routes)

    # Test Taxi and Train speed multipliers / properties
    taxi_routes = engine.calculate_routes(17.3850, 78.4867, 17.4000, 78.4900, mode=TravelMode.TAXI)
    assert len(taxi_routes) >= 1
    train_routes = engine.calculate_routes(17.3850, 78.4867, 17.4000, 78.4900, mode=TravelMode.TRAIN)
    assert len(train_routes) >= 1


def test_aura_journey_cockpit_vehicle_integration():
    """Verify 3D cockpit HTML includes vehicle suite, HUD badge, and active vehicle controller."""
    from src.aura_journey_engine import build_aura_journey_cockpit_html, ManeuverSequenceBuilder
    maneuvers = ManeuverSequenceBuilder.build_sequence(
        steps=[],
        origin_label="Hyderabad",
        dest_label="Bengaluru",
        total_distance_m=560000.0,
        travel_mode="car"
    )
    html = build_aura_journey_cockpit_html(
        origin_name="Hyderabad",
        dest_name="Bengaluru",
        travel_mode="car",
        total_distance_km=560.0,
        total_duration_mins=480.0,
        maneuvers=maneuvers
    )
    assert "VehicleController" in html
    assert "activeVehicleController" in html
    assert "hud-vehicle-mode" in html
    assert "switchVehicleMode" in html


def test_virtual_human_guide_vehicle_overlay():
    """Verify 2D articulated guide HTML includes dynamic vehicle cockpit rendering."""
    from src.virtual_human_guide import build_always_visible_virtual_guide_html
    html = build_always_visible_virtual_guide_html(
        origin_name="Mumbai",
        dest_name="Goa",
        travel_mode="bike"
    )
    assert "isVehicleMode" in html
    assert "isCycling" in html
    assert "isMotorbike" in html
    assert "DYNAMIC 2D VEHICLE COCKPIT" in html
