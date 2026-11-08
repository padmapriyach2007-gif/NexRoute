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
