"""
Unit and integration tests for AuraGlobalCommandDispatcher.
Verifies voice command parsing, tab navigation, map styles,
facility filtering, route operations, multilingual support, and state application.
"""

import pytest
from src.aura_command_dispatcher import (
    AuraGlobalCommandDispatcher,
    AuraCommandType,
    AuraExecutionResult,
)


class TestAuraCommandDispatcher:
    def test_navigate_tab_commands(self):
        ctx = {"active_tab": "nav"}

        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Open navigation", ctx)
        assert res.command_type == AuraCommandType.NAVIGATE_TAB
        assert res.ui_updates.get("target_tab") == "nav"

        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Open chatbot", ctx)
        assert res.command_type == AuraCommandType.NAVIGATE_TAB
        assert res.ui_updates.get("target_tab") == "chat"
        assert res.ui_updates.get("trigger_open_copilot") is True

        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Open saved places", ctx)
        assert res.command_type == AuraCommandType.NAVIGATE_TAB
        assert res.ui_updates.get("target_tab") == "places"

        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Open facilities", ctx)
        assert res.command_type == AuraCommandType.NAVIGATE_TAB
        assert res.ui_updates.get("target_tab") == "facilities"

    def test_map_style_commands(self):
        ctx = {"active_tab": "nav"}

        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Switch to satellite view", ctx)
        assert res.command_type == AuraCommandType.MAP_STYLE
        assert res.ui_updates.get("map_style") == "satellite_hybrid"

        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Switch to roadmap view", ctx)
        assert res.command_type == AuraCommandType.MAP_STYLE
        assert res.ui_updates.get("map_style") == "google_maps_road"

        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Show terrain view", ctx)
        assert res.command_type == AuraCommandType.MAP_STYLE
        assert res.ui_updates.get("map_style") == "terrain"

    def test_map_actions(self):
        ctx = {"active_tab": "nav", "user_coords": (16.2335, 80.5505)}

        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Show my current location", ctx)
        assert res.command_type == AuraCommandType.MAP_ACTION
        assert res.ui_updates.get("scroll_to_app_map") is True
        assert res.ui_updates.get("map_center_override") == (16.2335, 80.5505)

        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Fit route on map", ctx)
        assert res.command_type == AuraCommandType.MAP_ACTION
        assert res.ui_updates.get("auto_fit_bounds") is True

    def test_route_actions_clear_and_swap(self):
        ctx = {
            "active_tab": "nav",
            "user_coords": (16.22, 80.60),
            "dest_coords": (16.23, 80.55),
            "start_label": "Start Point",
            "dest_label": "End Point"
        }

        # Clear destination
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Clear my destination", ctx)
        assert res.command_type == AuraCommandType.ROUTE_ACTION
        assert res.ui_updates.get("selected_dest_coords") is None
        assert res.ui_updates.get("pending_dest") == ""

        # Clear start
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Clear my start location", ctx)
        assert res.command_type == AuraCommandType.ROUTE_ACTION
        assert res.ui_updates.get("user_live_coords") is None
        assert res.ui_updates.get("pending_orig") == ""

        # Swap locations
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Swap locations", ctx)
        assert res.command_type == AuraCommandType.ROUTE_ACTION
        assert res.ui_updates.get("trigger_swap_endpoints") is True

        # Test apply execution result for swap
        state = {
            "user_live_coords": (16.22, 80.60),
            "user_live_label": "Start Point",
            "selected_dest_coords": (16.23, 80.55),
            "selected_dest_label": "End Point"
        }
        AuraGlobalCommandDispatcher.apply_execution_result(res, state)
        assert state["user_live_coords"] == (16.23, 80.55)
        assert state["selected_dest_coords"] == (16.22, 80.60)

    def test_route_actions_destructive_confirmation(self):
        ctx = {"active_tab": "nav"}
        # Clearing all stops should require confirmation
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Clear all stops", ctx)
        assert res.command_type == AuraCommandType.ROUTE_ACTION
        assert res.requires_confirmation is True

    def test_voice_guided_navigation_to_place(self):
        ctx = {"active_tab": "nav"}
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Navigate to Vijayawada Railway Station", ctx)
        assert res.command_type == AuraCommandType.ROUTE_ACTION
        assert res.action_name == "voice_set_destination"
        assert res.ui_updates.get("pending_dest") == "vijayawada railway station"

    def test_nearby_facility_search(self):
        ctx = {"active_tab": "nav"}

        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Find hospitals nearby", ctx)
        assert res.command_type == AuraCommandType.FACILITY_SEARCH
        assert res.ui_updates.get("facility_filter") == "health"

        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Find petrol stations nearby", ctx)
        assert res.command_type == AuraCommandType.FACILITY_SEARCH
        assert res.ui_updates.get("facility_filter") == "fuel"

        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Find restaurants nearby", ctx)
        assert res.command_type == AuraCommandType.FACILITY_SEARCH
        assert res.ui_updates.get("facility_filter") == "food"

        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Find ATMs nearby", ctx)
        assert res.command_type == AuraCommandType.FACILITY_SEARCH
        assert res.ui_updates.get("facility_filter") == "atm"

    def test_travel_tools_and_preferences(self):
        ctx = {"active_tab": "nav"}

        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Calculate fuel expenses", ctx)
        assert res.command_type == AuraCommandType.TRAVEL_TOOL
        assert res.ui_updates.get("show_fuel_modal") is True

        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Avoid toll roads", ctx)
        assert res.command_type == AuraCommandType.TRAVEL_TOOL
        assert res.ui_updates.get("avoid_tolls") is True

    def test_multilingual_commands(self):
        ctx = {"active_tab": "nav"}

        # Telugu: Navigation
        res_te = AuraGlobalCommandDispatcher.parse_and_dispatch("నావిగేషన్ తెరువు", ctx, lang="te")
        assert res_te.command_type == AuraCommandType.NAVIGATE_TAB
        assert res_te.ui_updates.get("target_tab") == "nav"

        # Hindi: Satellite
        res_hi = AuraGlobalCommandDispatcher.parse_and_dispatch("सैटेलाइट दृश्य दिखाओ", ctx, lang="hi")
        assert res_hi.command_type == AuraCommandType.MAP_STYLE
        assert res_hi.ui_updates.get("map_style") == "satellite_hybrid"

        # Tamil: Hospitals
        res_ta = AuraGlobalCommandDispatcher.parse_and_dispatch("மருத்துவமனைகளை கண்டுபிடி", ctx, lang="ta")
        assert res_ta.command_type == AuraCommandType.FACILITY_SEARCH
        assert res_ta.ui_updates.get("facility_filter") == "health"

    def test_apply_execution_result_to_state(self):
        fake_state = {}
        res = AuraExecutionResult(
            command_type=AuraCommandType.NAVIGATE_TAB,
            action_name="switch_tab",
            spoken_response="Switching to Navigation view.",
            text_response="Navigating to navigation tab.",
            ui_updates={"target_tab": "nav", "scroll_to_app_map": True}
        )
        AuraGlobalCommandDispatcher.apply_execution_result(res, fake_state)
        assert fake_state.get("target_tab") == "nav"
        assert fake_state.get("scroll_to_app_map") is True
