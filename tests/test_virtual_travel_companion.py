"""
Automated Test Suite for Live Virtual Travel Companion & Journey Visualization
Tests the navigation state machine, GPS noise handling, map-matching,
checkpoint and step completion, multi-mode companions, and backend APIs.
"""

import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from src.api_server import app
from src.backend.database.connection import SessionLocal, Base, engine
from src.backend.database.models import NavigationSession, NavigationRouteStep, NavigationCheckpoint
from src.backend.navigation.state_machine import NavigationState, NavigationStateMachine
from src.backend.navigation.progress_service import (
    ProgressProcessingService,
    haversine_distance_m,
    calculate_bearing_degrees
)
from src.backend.navigation.companion_service import CompanionService, MODE_AVATAR_CONFIG
from src.virtual_companion_ui import build_virtual_companion_hud_html


@pytest.fixture(scope="module")
def db_session():
    from src.backend.database.migrations import run_migrations
    run_migrations()
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="module")
def api_client():
    from src.backend.database.migrations import run_migrations
    run_migrations()
    with TestClient(app) as client:
        yield client


# =============================================================================
# 1. NAVIGATION STATE MACHINE TESTS
# =============================================================================

def test_state_machine_valid_and_invalid_transitions():
    sm = NavigationStateMachine(NavigationState.IDLE)
    assert sm.current_state == NavigationState.IDLE

    # Valid: IDLE -> ROUTE_READY -> STARTING -> MOVING
    ok, st = sm.transition_to(NavigationState.ROUTE_READY)
    assert ok and st == NavigationState.ROUTE_READY

    ok, st = sm.transition_to(NavigationState.STARTING)
    assert ok and st == NavigationState.STARTING

    ok, st = sm.transition_to(NavigationState.MOVING)
    assert ok and st == NavigationState.MOVING

    # Invalid: MOVING directly to IDLE without ARRIVED or CANCELLED
    ok, st = sm.transition_to(NavigationState.IDLE)
    assert not ok
    assert st == NavigationState.MOVING


def test_state_machine_speed_hysteresis_and_traffic_stop():
    sm = NavigationStateMachine(NavigationState.MOVING)

    # 1 observation of 0 km/h: hysteresis does not trigger stop yet
    st1 = sm.evaluate_observation(speed_kmh=0.0, accuracy_meters=5.0)
    assert st1 == NavigationState.MOVING

    # 2nd consecutive observation of 0 km/h: triggers TEMPORARILY_STOPPED
    st2 = sm.evaluate_observation(speed_kmh=0.0, accuracy_meters=5.0)
    assert st2 == NavigationState.TEMPORARILY_STOPPED

    # Known traffic zone causes TRAFFIC_DELAY
    sm.consecutive_stops = 2
    st_traffic = sm.evaluate_observation(speed_kmh=0.0, accuracy_meters=5.0, is_known_traffic_zone=True)
    assert st_traffic == NavigationState.TRAFFIC_DELAY

    # Speed resumes (> 1.8 km/h): triggers RESUMING
    st_resuming = sm.evaluate_observation(speed_kmh=4.5, accuracy_meters=5.0)
    assert st_resuming == NavigationState.RESUMING

    # Next observation confirms MOVING
    st_moving = sm.evaluate_observation(speed_kmh=4.5, accuracy_meters=5.0)
    assert st_moving == NavigationState.MOVING


def test_state_machine_gps_accuracy_filtering():
    sm = NavigationStateMachine(NavigationState.MOVING)

    # Poor GPS accuracy (> 45m) enters GPS_UNCERTAIN
    st_unc = sm.evaluate_observation(speed_kmh=4.0, accuracy_meters=60.0)
    assert st_unc == NavigationState.GPS_UNCERTAIN

    # When accuracy returns to normal (<= 45m), state recovers
    st_rec = sm.evaluate_observation(speed_kmh=4.0, accuracy_meters=5.0)
    assert st_rec == NavigationState.MOVING


def test_state_machine_turn_approaching_and_turning():
    sm = NavigationStateMachine(NavigationState.MOVING)

    # Approaching turn within 50m
    st_app = sm.evaluate_observation(speed_kmh=4.0, accuracy_meters=5.0, dist_to_turn_meters=35.0)
    assert st_app == NavigationState.APPROACHING_TURN

    # Executing turn at intersection
    st_turn = sm.evaluate_observation(speed_kmh=3.0, accuracy_meters=5.0, is_at_turn=True)
    assert st_turn == NavigationState.TURNING

    # Completing turn back to moving corridor
    st_mov = sm.evaluate_observation(speed_kmh=4.5, accuracy_meters=5.0, dist_to_turn_meters=None, is_at_turn=False)
    assert st_mov == NavigationState.MOVING


# =============================================================================
# 2. PROGRESS PROCESSING & MAP-MATCHING TESTS
# =============================================================================

def test_map_matching_and_bearing():
    polyline = [
        [16.2335, 80.5505],
        [16.2400, 80.5520],
        [16.2500, 80.5550]
    ]
    # Point near first segment
    matched_lat, matched_lon, dist_m, seg_idx = ProgressProcessingService.match_to_polyline(
        16.2350, 80.5510, polyline
    )
    assert dist_m < 80.0
    assert seg_idx == 0

    # Calculate bearing
    bearing = calculate_bearing_degrees((16.2335, 80.5505), (16.2400, 80.5520))
    assert 0.0 <= bearing <= 360.0


def test_entrance_and_destination_arrival():
    dest_pos = (16.2550, 80.5450)
    entrance_pos = (16.2548, 80.5448)

    # Far from destination
    arrived, at_ent, msg = ProgressProcessingService.evaluate_arrival(
        user_lat=16.2300, user_lon=80.5500,
        dest_lat=dest_pos[0], dest_lon=dest_pos[1],
        entrance_coords=entrance_pos
    )
    assert not arrived

    # At building entrance
    arrived_ent, at_ent, msg = ProgressProcessingService.evaluate_arrival(
        user_lat=entrance_pos[0] + 0.00005, user_lon=entrance_pos[1],
        dest_lat=dest_pos[0], dest_lon=dest_pos[1],
        entrance_coords=entrance_pos
    )
    assert arrived_ent and at_ent
    assert "Entrance" in msg


# =============================================================================
# 3. BACKEND SESSION LIFECYCLE & API TESTS
# =============================================================================

def test_navigation_session_api_lifecycle(api_client):
    # 1. Create Session
    payload = {
        "origin_name": "Vignan Main Gate",
        "origin_latitude": 16.2335,
        "origin_longitude": 80.5505,
        "destination_name": "Narakoduru Center",
        "destination_latitude": 16.2550,
        "destination_longitude": 80.5450,
        "travel_mode": "running",
        "polyline": [
            [16.2335, 80.5505],
            [16.2400, 80.5520],
            [16.2480, 80.5540],
            [16.2550, 80.5450]
        ]
    }
    res = api_client.post("/api/v2/navigation/sessions", json=payload)
    assert res.status_code == 200
    data = res.json()
    session_id = data["session_id"]
    assert data["status"] == "ROUTE_READY"
    assert data["avatar"]["icon"] == "🏃‍♂️"
    assert len(data["timeline"]["steps"]) >= 3

    # 2. Start Session
    res_start = api_client.post(f"/api/v2/navigation/sessions/{session_id}/start")
    assert res_start.status_code == 200
    assert res_start.json()["status"] == "STARTING"

    # 3. Submit Moving Location Update
    loc_payload = {
        "latitude": 16.2340,
        "longitude": 80.5507,
        "speed_kmh": 9.2,
        "accuracy_meters": 4.0
    }
    res_loc = api_client.post(f"/api/v2/navigation/sessions/{session_id}/location", json=loc_payload)
    assert res_loc.status_code == 200
    loc_data = res_loc.json()
    assert loc_data["status"] == "MOVING"
    assert loc_data["position"]["speed_kmh"] == 9.2

    # 4. Submit Traffic Stop Observation (speed 0)
    api_client.post(f"/api/v2/navigation/sessions/{session_id}/location", json={
        "latitude": 16.2340, "longitude": 80.5507, "speed_kmh": 0.0, "accuracy_meters": 4.0
    })
    res_stop = api_client.post(f"/api/v2/navigation/sessions/{session_id}/location", json={
        "latitude": 16.2340, "longitude": 80.5507, "speed_kmh": 0.0, "accuracy_meters": 4.0
    })
    assert res_stop.json()["status"] == "TEMPORARILY_STOPPED"
    assert res_stop.json()["avatar"]["is_stopped"] is True

    # 5. Confirm Manual Action
    res_act = api_client.post(f"/api/v2/navigation/sessions/{session_id}/confirm_action", json={
        "action_name": "CROSSED_CHECKPOINT",
        "details": "Verified crossing milestone"
    })
    assert res_act.status_code == 200

    # 6. Pause and Resume
    res_pause = api_client.post(f"/api/v2/navigation/sessions/{session_id}/pause")
    assert res_pause.status_code == 200
    assert res_pause.json()["status"] == "PAUSED"

    res_resume = api_client.post(f"/api/v2/navigation/sessions/{session_id}/resume")
    assert res_resume.status_code == 200
    assert res_resume.json()["status"] == "RESUMING"

    # 7. Final Arrival
    res_arr = api_client.post(f"/api/v2/navigation/sessions/{session_id}/location", json={
        "latitude": 16.2550,
        "longitude": 80.5450,
        "speed_kmh": 0.0,
        "accuracy_meters": 5.0
    })
    assert res_arr.json()["status"] == "ARRIVED"
    assert res_arr.json()["arrival"]["is_arrived"] is True

    # 8. Journey Summary
    res_sum = api_client.get(f"/api/v2/navigation/sessions/{session_id}/summary")
    assert res_sum.status_code == 200
    sum_data = res_sum.json()
    assert sum_data["is_completed"] is True
    assert sum_data["origin_name"] == "Vignan Main Gate"


# =============================================================================
# 4. MULTI-MODE COMPANIONS & UI RENDERING TESTS
# =============================================================================

def test_multi_mode_companion_configurations():
    for mode in ["walking", "running", "driving", "cycling", "motorcycle", "transit"]:
        cfg = MODE_AVATAR_CONFIG[mode]
        assert "avatar_icon" in cfg
        assert "avatar_name" in cfg
        assert "movement_anim" in cfg
        assert cfg["default_speed_kmh"] > 0


def test_virtual_companion_hud_html_renders():
    html = build_virtual_companion_hud_html(
        session_id="SESS_TEST_01",
        origin_name="Tenali",
        dest_name="Vignan University",
        travel_mode="walking",
        initial_state="ROUTE_READY"
    )
    assert "Virtual Walking Companion" in html
    assert "🚶‍♂️" in html
    assert "state-ROUTE_READY" in html
    assert "companionSimulateStop" in html
    assert "companionSimulateMove" in html
    assert "companionSimulateArrival" in html
    assert "timeline-step-card" in html


def test_virtual_companion_hud_with_friendly_turn_steps():
    """Ensure FriendlyTurnStep dataclass objects serialize without TypeError."""
    from src.journey_storyteller import FriendlyTurnStep

    steps = [
        FriendlyTurnStep(
            step_num=1,
            total_steps=2,
            direction_type="START",
            action_headline="Depart from Hyderabad",
            virtual_guide_speech="Let's begin our journey from Hyderabad.",
            what_to_look_for="Main roadway signs",
            distance_human="500 m",
            time_estimate="2 mins",
            road_name="NH 65",
            icon="🟢",
            spoken_text="Depart on NH 65"
        ),
        FriendlyTurnStep(
            step_num=2,
            total_steps=2,
            direction_type="ARRIVE",
            action_headline="Arrive at Tenali Junction",
            virtual_guide_speech="We have safely reached Tenali Junction.",
            what_to_look_for="Welcome arch",
            distance_human="290 km",
            time_estimate="5 hours",
            road_name="Tenali Bypass",
            icon="🏆",
            spoken_text="Arrive at destination"
        )
    ]

    html = build_virtual_companion_hud_html(
        session_id="SESS_TEST_FRIENDLY_TURNS",
        origin_name="Hyderabad",
        dest_name="Tenali Junction",
        travel_mode="driving",
        initial_state="MOVING",
        steps=steps
    )
    assert "Depart from Hyderabad" in html
    assert "Arrive at Tenali Junction" in html
    assert "NH 65" in html
    assert "timeline-step-card" in html
