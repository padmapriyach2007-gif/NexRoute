"""
Acceptance Test Suite for PATHFINDER Virtual Guide Dashboard UX Redesign & Movement Logic Fix

Covers:
1. Stationary on Tab Opening (speed 0.0 km/h, ready status, no auto-start)
2. Essential Movement Controls Only (Traffic Stop & Move in Parallel)
3. Synchronization between Runner and Vehicle Companion
4. Understandable Journey Direction mapping
5. Virtual Guide Scene (3D road scenery, full character visibility, no clipping)
6. Component Sizing and Overflow Prevention
7. Layout Ordering in app.py (Section 1 -> Section 2 -> Section 3 -> Section 4)
8. GPS & Speed Truthfulness
"""

import re
import pytest
from src.game_journey_stepper import (
    JourneyMilestone,
    build_game_journey_html,
    extract_journey_game_milestones
)
from src.virtual_companion_ui import build_virtual_companion_hud_html
from src.virtual_human_guide import build_always_visible_virtual_guide_html


@pytest.fixture
def sample_milestones():
    return [
        JourneyMilestone(
            index=0,
            milestone_type="START",
            label="Main Campus Gate",
            action_title="Started from Main Campus Gate",
            road_or_area="Transit Road",
            lat=16.2330,
            lon=80.5480,
            distance_from_start_km=0.0,
            distance_leg_km=0.0,
            voice_announcement="Started journey",
            icon="🟢"
        ),
        JourneyMilestone(
            index=1,
            milestone_type="WAYPOINT",
            label="Innovation Square Junction",
            action_title="Approaching Innovation Square",
            road_or_area="Campus Arterial",
            lat=16.2410,
            lon=80.5520,
            distance_from_start_km=1.2,
            distance_leg_km=1.2,
            voice_announcement="Waypoint reached",
            icon="➡️"
        ),
        JourneyMilestone(
            index=2,
            milestone_type="DESTINATION",
            label="Library Terminal Station",
            action_title="Arrived at Library",
            road_or_area="Terminal Loop",
            lat=16.2500,
            lon=80.5580,
            distance_from_start_km=2.5,
            distance_leg_km=1.3,
            voice_announcement="Reached destination",
            icon="🏁"
        )
    ]


# =============================================================================
# 1. STATIONARY ON TAB OPENING
# =============================================================================

def test_runner_initial_state_is_stationary(sample_milestones):
    """Opening the Virtual Guide tab must initialize the interface in a stationary state."""
    html = build_game_journey_html(
        milestones=sample_milestones,
        current_step=0,
        traveler_avatar="walk",
        is_moving=False,
        user_speed_kmh=0.0
    )
    assert "0.0 km/h" in html
    assert "Ready to Start" in html or "Stationary" in html
    # Movement state initialized to READY
    assert "movementState = 'READY'" in html or 'movementState = "READY"' in html


def test_companion_initial_state_is_stationary():
    """Virtual Vehicle Companion must initialize in a stationary state with speed 0.0."""
    html = build_virtual_companion_hud_html(
        session_id="TEST_SYNC",
        origin_name="Main Campus Gate",
        dest_name="Library Terminal Station",
        initial_state="ROUTE_READY",
        current_speed_kmh=0.0
    )
    assert "0.0 km/h" in html
    assert "Ready to Start" in html or "Stationary" in html or "ROUTE READY" in html


# =============================================================================
# 2. ESSENTIAL MANUAL MOVEMENT CONTROLS ONLY
# =============================================================================

def test_runner_has_only_essential_movement_controls(sample_milestones):
    """
    Virtual Runner banner must keep ONLY Traffic Stop and Move in Parallel.
    Removed redundant controls: Cross Next Stop dropdown/button, Pause Motion, Return Trip action button, Restart.
    """
    html = build_game_journey_html(
        milestones=sample_milestones,
        current_step=0,
        is_moving=False
    )
    # Essential buttons must be present
    assert "Traffic Stop" in html
    assert "Move in Parallel" in html

    # Redundant action buttons must NOT be present as button text
    assert ">Pause Motion<" not in html
    assert ">Restart<" not in html
    assert ">Cross Next Stop<" not in html


def test_companion_has_only_essential_movement_controls():
    """
    Virtual Vehicle Companion must keep ONLY Traffic Stop and Move in Parallel.
    Removed redundant controls: Walking, Approach & Turn, Complete Arrival, Pause, Restart.
    """
    html = build_virtual_companion_hud_html(
        session_id="TEST_CONTROLS",
        origin_name="Main Campus Gate",
        dest_name="Library Terminal Station"
    )
    # Essential buttons must be present
    assert "Traffic Stop" in html
    assert "Move in Parallel" in html

    # Redundant manual action buttons must NOT be present as interactive buttons
    assert ">Walking<" not in html
    assert ">Approach &amp; Turn<" not in html and ">Approach & Turn<" not in html
    assert ">Complete Arrival<" not in html
    assert ">Pause<" not in html
    assert ">Restart<" not in html


# =============================================================================
# 3. SYNCHRONIZATION VIA CENTRAL MOVEMENT STATE MACHINE
# =============================================================================

def test_central_sync_broadcast_channel(sample_milestones):
    """
    Both visual representations must communicate via BroadcastChannel and window postMessage
    with synchronized states: READY, MOVING, TRAFFIC_STOPPED, ARRIVED.
    """
    runner_html = build_game_journey_html(
        milestones=sample_milestones,
        current_step=0,
        is_moving=False
    )
    companion_html = build_virtual_companion_hud_html(
        session_id="TEST_SYNC",
        origin_name="Main Campus Gate",
        dest_name="Library Terminal Station"
    )
    guide_html = build_always_visible_virtual_guide_html(
        origin_name="Main Campus Gate",
        dest_name="Library Terminal Station"
    )

    # All three components use the pathfinder_journey_sync channel
    assert "pathfinder_journey_sync" in runner_html
    assert "pathfinder_journey_sync" in companion_html
    assert "pathfinder_journey_sync" in guide_html

    # Check state machine states in runner
    assert "TRAFFIC_STOPPED" in runner_html
    assert "MOVING" in runner_html
    assert "ARRIVED" in runner_html


# =============================================================================
# 4. JOURNEY DIRECTION UNDERSTANDABILITY
# =============================================================================

def test_journey_direction_selector_uses_place_names(sample_milestones):
    """Start -> Goal and Goal -> Start must use real origin and destination place names."""
    origin = sample_milestones[0].label
    dest = sample_milestones[-1].label
    html = build_game_journey_html(
        milestones=sample_milestones
    )
    assert origin in html
    assert dest in html
    # Symmetrical direction toggle present
    assert "btn-dir-forward" in html
    assert "btn-dir-return" in html


# =============================================================================
# 5. VIRTUAL GUIDE SCENE REDESIGN & FULL CHARACTER VISIBILITY
# =============================================================================

def test_virtual_guide_scene_and_visibility():
    """
    Virtual Guide scene must render complete body without bottom cropping.
    Canvas height, perspective road surface, shoes, and ground contact shadow must be present.
    """
    html = build_always_visible_virtual_guide_html(
        origin_name="Tech Park",
        dest_name="Medical Center"
    )
    # Check canvas element attributes
    assert 'width="280"' in html
    assert 'height="380"' in html

    # Character anatomy checks
    assert "Two-tone Campus Sneaker" in html or "#2563eb" in html
    assert "Sole crisp white" in html or "#ffffff" in html
    assert "Contact shadow" in html or "Ground Contact Shadow" in html

    # Road scenery checks
    assert "Perspective Asphalt Road Bed" in html or "roadGrad" in html
    assert "Lane Divider Markings" in html


# =============================================================================
# 6. LAYOUT ORDERING & APP.PY INTEGRATION
# =============================================================================

def test_layout_ordering_in_app_file():
    """
    In app.py, Section 1 (Virtual Runner) must come before Section 2 (Virtual Vehicle Companion),
    Section 2 must come before Section 3 (Virtual Guide),
    and Section 3 must come before Section 4 (Additional Route Details).
    """
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Find locations of each section marker in app.py
    sec1_pos = content.find("Section 1: Virtual Runner")
    sec2_pos = content.find("Section 2: Virtual Vehicle Companion")
    sec3_pos = content.find("Section 3: Virtual Human Guide")
    sec4_pos = content.find("Section 4: Additional Route Details")

    assert sec1_pos != -1, "Section 1 must be present in app.py"
    assert sec2_pos != -1, "Section 2 must be present in app.py"
    assert sec3_pos != -1, "Section 3 must be present in app.py"
    assert sec4_pos != -1, "Section 4 must be present in app.py"

    assert sec1_pos < sec2_pos, "Section 1 must appear before Section 2"
    assert sec2_pos < sec3_pos, "Section 2 must appear before Section 3"
    assert sec3_pos < sec4_pos, "Section 3 must appear before Section 4"


def test_app_initial_state_is_stationary():
    """Verify that app.py initializes Virtual Guide tab in stationary state without auto-movement."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Verify that is_user_moving defaults to False
    assert 'is_user_moving = bool(st.session_state.get("virtual_guide_moving", False))' in content
    assert 'guide_speed_kmh = float(st.session_state.get("user_speed_kmh", 0.0)) if is_user_moving else 0.0' in content


# =============================================================================
# 7. GPS & SPEED TRUTHFULNESS
# =============================================================================

def test_gps_status_truthfulness():
    """Verify GPS status distinguishes simulation from live GPS."""
    # When simulated or stationary:
    html_sim = build_always_visible_virtual_guide_html(
        origin_name="Gate A",
        dest_name="Terminal B",
        is_live_gps=False,
        current_speed_kmh=0.0
    )
    assert "SIMULATED" in html_sim or "SIMULATION" in html_sim or "GPS Uncertain" in html_sim
    assert "GPS Locked" not in html_sim
