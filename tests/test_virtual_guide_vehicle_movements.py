"""
Unit and integration tests for realistic movements of the virtual guide (Aura)
and all 10 selectable transportation modes in the Route Journey Pipeline.
"""

import pytest
from src.vehicle_navigation_controller import (
    TransportationMode,
    VehicleModeConfig,
    VehicleModeManager
)
from src.aura_journey_engine import (
    AuraJourneyStage,
    AuraPose,
    AuraManeuverStep,
    ManeuverSequenceBuilder,
    build_aura_journey_cockpit_html
)


def _sample_maneuvers():
    raw_maneuvers = [
        {"instruction": "Head northeast on MG Road", "road": "MG Road", "distance": 500, "duration": 60, "type": "depart"},
        {"instruction": "Turn right onto Church Street", "road": "Church Street", "distance": 1200, "duration": 150, "type": "turn-right"},
        {"instruction": "Arrive at destination", "road": "Destination", "distance": 0, "duration": 0, "type": "arrive"}
    ]
    return ManeuverSequenceBuilder.build_sequence(
        steps=raw_maneuvers,
        origin_label="MG Road",
        dest_label="Church Street",
        total_distance_m=1700.0,
        travel_mode="car"
    )


def test_all_ten_vehicle_toolbar_buttons():
    """Verify all 10 travel vehicles exist with proper buttons and data-mode attributes."""
    steps = _sample_maneuvers()
    html = build_aura_journey_cockpit_html(
        origin_name="Suddapalli",
        dest_name="Sangam Jagarlamudi",
        travel_mode="car",
        total_distance_km=4.6,
        total_duration_mins=8.0,
        maneuvers=steps
    )

    expected_modes = ["CAR", "BIKE", "BUS", "BICYCLE", "WALK", "TRUCK", "TRACTOR", "FLIGHT", "WATERWAY", "TRAIN"]
    for mode in expected_modes:
        assert f"id='btn-veh-{mode}'" in html, f"Missing toolbar button for mode {mode}"
        assert f"data-mode='{mode}'" in html, f"Missing data-mode attribute for {mode}"
        assert f"window.switchVehicleMode(\"{mode}\")" in html, f"Missing switchVehicleMode onclick for {mode}"


def test_initial_vehicle_mode_active_highlight():
    """Verify that when a mode is specified, its button is given the active class."""
    steps = _sample_maneuvers()

    # Test CAR
    html_car = build_aura_journey_cockpit_html(
        origin_name="A", dest_name="B", travel_mode="car",
        total_distance_km=5.0, total_duration_mins=10.0, maneuvers=steps
    )
    assert "id='btn-veh-CAR' class='btn-action-pill btn-veh-selector active'" in html_car
    assert "VEHICLE: CAR" in html_car

    # Test BIKE
    html_bike = build_aura_journey_cockpit_html(
        origin_name="A", dest_name="B", travel_mode="bike",
        total_distance_km=5.0, total_duration_mins=10.0, maneuvers=steps
    )
    assert "id='btn-veh-BIKE' class='btn-action-pill btn-veh-selector active'" in html_bike
    assert "VEHICLE: BIKE" in html_bike

    # Test WALK
    html_walk = build_aura_journey_cockpit_html(
        origin_name="A", dest_name="B", travel_mode="walking",
        total_distance_km=1.0, total_duration_mins=15.0, maneuvers=steps
    )
    assert "id='btn-veh-WALK' class='btn-action-pill btn-veh-selector active'" in html_walk
    assert "VEHICLE: WALK" in html_walk


def test_scenic_canvas_multi_modal_vehicle_suite():
    """Verify that the 2.5D scenic canvas engine contains realistic rendering for all 10 vehicles."""
    steps = _sample_maneuvers()
    html = build_aura_journey_cockpit_html(
        origin_name="A", dest_name="B", travel_mode="car",
        total_distance_km=5.0, total_duration_mins=10.0, maneuvers=steps
    )

    # Verify 2.5D engine has realistic vehicle branches
    assert "drawCuteAuraDriver" in html
    assert "drawSpinningWheel" in html
    assert "drawHeadlightBeams" in html
    assert "suspensionBob" in html
    assert "wheelAngle" in html

    # Verify vehicle rendering sections
    assert "curMode === 'WALK'" in html
    assert "curMode === 'BIKE'" in html
    assert "curMode === 'BUS'" in html
    assert "curMode === 'BICYCLE'" in html
    assert "curMode === 'TRUCK'" in html
    assert "curMode === 'TRACTOR'" in html
    assert "curMode === 'FLIGHT'" in html
    assert "curMode === 'WATERWAY'" in html
    assert "curMode === 'TRAIN'" in html


def test_threejs_render_loop_kinematics_guard():
    """Verify Three.js render loop guards walking strides so vehicle postures are preserved."""
    steps = _sample_maneuvers()
    html = build_aura_journey_cockpit_html(
        origin_name="A", dest_name="B", travel_mode="car",
        total_distance_km=5.0, total_duration_mins=10.0, maneuvers=steps
    )

    assert "isWalkingMode" in html
    assert "window.activeVehicleController.updateKinematics" in html
    assert "window.activeVehicleController.setMode" in html


def test_switch_vehicle_mode_js_runtime():
    """Verify window.switchVehicleMode updates active button, HUD badge, controller, and plays chime."""
    steps = _sample_maneuvers()
    html = build_aura_journey_cockpit_html(
        origin_name="A", dest_name="B", travel_mode="car",
        total_distance_km=5.0, total_duration_mins=10.0, maneuvers=steps
    )

    assert "window.switchVehicleMode = function" in html
    assert "btn-veh-selector" in html
    assert "hud-vehicle-mode" in html
    assert "AudioContext" in html

