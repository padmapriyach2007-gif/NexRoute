"""
Tests for AURA / JARVIS Universal Full Application Voice Controller.
Validates that AURA can understand and execute commands controlling every module,
page, feature, vehicle, setting, and user interaction in NextRoute with multi-action chaining,
dependency ordering, geocoding resolution, action validation, and multilingual support.
"""

import pytest
from src.aura_command_dispatcher import AuraGlobalCommandDispatcher, AuraCommandType, AuraExecutionResult


class TestAuraFullApplicationVoiceController:
    """Comprehensive test suite for Universal NextRoute Voice Control."""

    # -------------------------------------------------------------------------
    # 1. SINGLE-ACTION APPLICATION COMMANDS (All Manual Interactions)
    # -------------------------------------------------------------------------
    def test_navigation_module_controls(self):
        """Voice command opens navigation module and switches to map view."""
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Open navigation")
        assert res.command_type in [AuraCommandType.OPEN_MODULE, AuraCommandType.NAVIGATE_TAB]
        assert res.ui_updates.get("current_view") == "map_nav"
        assert res.ui_updates.get("target_tab") == "nav"

    def test_destination_setting_and_geocoding(self):
        """'Take me to Hyderabad' geocodes destination and calculates routes."""
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Take me to Hyderabad")
        assert res.command_type == AuraCommandType.SET_DESTINATION
        assert res.ui_updates.get("selected_dest_coords") is not None
        assert "Hyderabad" in res.ui_updates.get("selected_dest_label", "")
        assert res.ui_updates.get("routes_generated") is True

    def test_vehicle_mode_selection(self):
        """Voice commands for selecting transportation modes."""
        for mode_phrase, expected_mode in [
            ("Change my vehicle to bike", "BIKE"),
            ("Switch to bus mode", "BUS"),
            ("Use walking mode", "WALK"),
            ("Change vehicle to flight", "FLIGHT"),
            ("Switch to train mode", "TRAIN")
        ]:
            res = AuraGlobalCommandDispatcher.parse_and_dispatch(mode_phrase)
            assert res.command_type == AuraCommandType.SELECT_VEHICLE
            assert res.ui_updates.get("selected_travel_mode") == expected_mode
            assert res.ui_updates.get("routes_generated") is True

    def test_my_trips_module(self):
        """'Open my trips' opens Copilot Studio & Itinerary studio."""
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Open my trips")
        assert res.command_type == AuraCommandType.OPEN_MY_TRIPS
        assert res.ui_updates.get("current_view") == "copilot_studio"

    def test_hotel_search_module(self):
        """'Find hotels' switches to facilities tab with hotel filter."""
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Find hotels")
        assert res.command_type in [AuraCommandType.SEARCH_HOTEL, AuraCommandType.FACILITY_SEARCH]
        assert res.ui_updates.get("facility_filter") == "hotel"
        assert res.ui_updates.get("current_view") == "map_nav"

    def test_flight_search_module(self):
        """'Show flights' switches to flight planning module."""
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Show flights")
        assert res.command_type == AuraCommandType.SEARCH_FLIGHT
        assert res.ui_updates.get("selected_travel_mode") == "FLIGHT"

    def test_restaurant_search_module(self):
        """'Find restaurants near me' filters facilities for dining."""
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Find restaurants near me")
        assert res.command_type == AuraCommandType.SEARCH_RESTAURANT
        assert res.ui_updates.get("facility_filter") == "food"

    def test_profile_and_account_module(self):
        """'Open my profile' triggers user profile modal."""
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Open my profile")
        assert res.command_type == AuraCommandType.OPEN_PROFILE
        assert res.ui_updates.get("show_user_profile_modal") is True

    def test_language_switch_command(self):
        """'Switch to Telugu' changes application language to 'te'."""
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Switch to Telugu")
        assert res.command_type == AuraCommandType.SET_APPLICATION_LANGUAGE
        assert res.ui_updates.get("app_language") == "te"

    def test_theme_switch_command(self):
        """'Switch to dark mode' activates dark theme."""
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Switch to dark mode")
        assert res.command_type == AuraCommandType.SET_THEME
        assert res.ui_updates.get("app_theme") == "dark"

    def test_3d_companion_toggle_and_camera_controls(self):
        """Controls 3D virtual guide companion and camera follow mode."""
        res_3d = AuraGlobalCommandDispatcher.parse_and_dispatch("Show the 3D guide")
        assert res_3d.command_type == AuraCommandType.TOGGLE_3D_MODE
        assert res_3d.ui_updates.get("companion_3d_mode") is True
        assert res_3d.ui_updates.get("enable_3d_companion") is True

        res_cam = AuraGlobalCommandDispatcher.parse_and_dispatch("Make the camera follow my vehicle")
        assert res_cam.command_type == AuraCommandType.CONTROL_3D_COMPANION
        assert res_cam.ui_updates.get("companion_camera_follow") is True

    def test_map_fitting_and_styles(self):
        """'Fit the entire route' and satellite view controls."""
        res_fit = AuraGlobalCommandDispatcher.parse_and_dispatch("Fit the entire route")
        assert res_fit.command_type == AuraCommandType.FIT_MAP
        assert res_fit.ui_updates.get("auto_fit_bounds") is True

        res_sat = AuraGlobalCommandDispatcher.parse_and_dispatch("Switch to satellite view")
        assert res_sat.command_type == AuraCommandType.MAP_STYLE
        assert res_sat.ui_updates.get("map_engine") == "google_satellite"

    def test_endpoint_swapping_and_current_location(self):
        """'Swap locations' and 'Use my current location'."""
        res_swap = AuraGlobalCommandDispatcher.parse_and_dispatch("Swap locations")
        assert res_swap.command_type == AuraCommandType.SWAP_LOCATIONS
        assert res_swap.ui_updates.get("trigger_swap_endpoints") is True

        res_loc = AuraGlobalCommandDispatcher.parse_and_dispatch("Use my current location")
        assert res_loc.command_type == AuraCommandType.USE_CURRENT_LOCATION
        assert res_loc.ui_updates.get("trigger_client_gps_sync") is True

    def test_route_priorities_and_alternatives(self):
        """Route optimization priorities and alternative routes."""
        res_short = AuraGlobalCommandDispatcher.parse_and_dispatch("Choose the shortest route")
        assert res_short.command_type == AuraCommandType.CHANGE_ROUTE_PRIORITY
        assert res_short.ui_updates.get("active_objective") == "SHORTEST"

        res_alt = AuraGlobalCommandDispatcher.parse_and_dispatch("Show all available routes")
        assert res_alt.command_type == AuraCommandType.SHOW_ALTERNATIVE_ROUTES
        assert res_alt.ui_updates.get("active_objective") == "all"

    # -------------------------------------------------------------------------
    # 2. MULTI-ACTION CHAINED VOICE COMMANDS (With Dependency Ordering)
    # -------------------------------------------------------------------------
    def test_multi_action_example_1(self):
        """
        User: 'Set my destination to Hyderabad, change my vehicle to car, choose the fastest route, and start navigation.'
        Verifies:
        1. Destination resolved & geocoded
        2. Vehicle set to CAR
        3. Fastest route priority chosen
        4. Navigation started & 3D companion synced
        5. Single unified spoken response
        """
        query = "Set my destination to Hyderabad, change my vehicle to car, choose the fastest route, and start navigation."
        res = AuraGlobalCommandDispatcher.parse_and_dispatch(query, context={"user_coords": (16.5, 80.6)}, lang="en")

        assert res.command_type == AuraCommandType.MULTI_ACTION_SEQUENCE
        assert res.success is True
        assert res.ui_updates.get("selected_dest_coords") is not None
        assert "Hyderabad" in res.ui_updates.get("selected_dest_label", "")
        assert res.ui_updates.get("selected_travel_mode") == "CAR"
        assert res.ui_updates.get("active_objective") == "FASTEST"
        assert res.ui_updates.get("aura_journey_active") is True
        assert res.ui_updates.get("virtual_guide_moving") is True
        assert res.ui_updates.get("companion_3d_mode") is True
        assert "Hyderabad" in res.spoken_response

    def test_multi_action_example_2(self):
        """
        User: 'Set my starting point to Vijayawada, destination to Guntur, select car mode, choose the fastest route, and start navigation.'
        Verifies:
        1. Starting point Vijayawada resolved & geocoded
        2. Destination Guntur resolved & geocoded
        3. Vehicle set to CAR
        4. Route priority set to FASTEST
        5. Navigation started
        """
        query = "Set my starting point to Vijayawada, destination to Guntur, select car mode, choose the fastest route, and start navigation."
        res = AuraGlobalCommandDispatcher.parse_and_dispatch(query, context={}, lang="en")

        assert res.command_type == AuraCommandType.MULTI_ACTION_SEQUENCE
        assert res.success is True
        assert res.ui_updates.get("user_live_coords") is not None
        assert "Vijayawada" in res.ui_updates.get("user_live_label", "")
        assert res.ui_updates.get("selected_dest_coords") is not None
        assert "Guntur" in res.ui_updates.get("selected_dest_label", "")
        assert res.ui_updates.get("selected_travel_mode") == "CAR"
        assert res.ui_updates.get("active_objective") == "FASTEST"
        assert res.ui_updates.get("aura_journey_active") is True

    # -------------------------------------------------------------------------
    # 3. ACTION VALIDATION AND SAFETY
    # -------------------------------------------------------------------------
    def test_start_navigation_safety_validation(self):
        """Cannot start navigation if no destination exists."""
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Start navigation", context={}, lang="en")
        assert res.command_type == AuraCommandType.START_NAVIGATION
        assert res.success is False
        assert "destination" in res.spoken_response.lower()

    def test_stop_navigation_when_idle(self):
        """Stopping navigation when idle provides clear, non-error feedback."""
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Stop navigation", context={"navigation_active": False}, lang="en")
        assert res.command_type == AuraCommandType.STOP_NAVIGATION
        assert res.success is True
        assert "idle" in res.spoken_response.lower()

    def test_stop_navigation_when_active(self):
        """Stopping navigation when active halts journey and GPS tracking."""
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Stop navigation", context={"navigation_active": True}, lang="en")
        assert res.command_type == AuraCommandType.STOP_NAVIGATION
        assert res.success is True
        assert res.ui_updates.get("aura_journey_active") is False
        assert res.ui_updates.get("virtual_guide_moving") is False

    # -------------------------------------------------------------------------
    # 4. APPLICATION STATE MUTATION & DISPATCHER APPLICATION
    # -------------------------------------------------------------------------
    def test_apply_execution_result_synchronizes_state(self):
        """apply_execution_result safely modifies session_state without DOM manipulation."""
        mock_session_state = {
            "current_view": "dashboard",
            "view_history": ["dashboard"],
            "selected_travel_mode": "WALK",
            "user_live_coords": (16.5, 80.6),
            "user_live_label": "Vijayawada",
            "selected_dest_coords": (17.3, 78.4),
            "selected_dest_label": "Hyderabad"
        }

        # Test Swap
        swap_res = AuraGlobalCommandDispatcher.parse_and_dispatch("Swap locations")
        AuraGlobalCommandDispatcher.apply_execution_result(swap_res, mock_session_state)
        assert mock_session_state["user_live_label"] == "Hyderabad"
        assert mock_session_state["selected_dest_label"] == "Vijayawada"

        # Test Multi-Action Application
        q = "Set my destination to Guntur, change my vehicle to bike, choose the fastest route, and start navigation."
        multi_res = AuraGlobalCommandDispatcher.parse_and_dispatch(q, context={"user_coords": (16.5, 80.6)}, lang="en")
        AuraGlobalCommandDispatcher.apply_execution_result(multi_res, mock_session_state)

        assert mock_session_state["current_view"] == "map_nav"
        assert mock_session_state["selected_travel_mode"] == "BIKE"
        assert mock_session_state["active_objective"] == "FASTEST"
        assert mock_session_state["aura_journey_active"] is True
        assert mock_session_state["virtual_guide_moving"] is True
