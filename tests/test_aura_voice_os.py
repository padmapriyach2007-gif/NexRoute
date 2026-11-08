# -*- coding: utf-8 -*-
"""
Comprehensive Voice Operating System Test Suite for AURA.
Validates natural-language commands and real state execution for:
- Endpoints (Clear all, clear start, clear dest, focus start, focus dest, fit both)
- 10 Travel vehicle modes
- Route alternative selection (Route 1 Cyan, Route 2 Orange, Route 3 Purple, fastest, shortest)
- 3D Virtual Guide & Tours (start, stop, pause, resume, next, prev, toggle 3D)
- Map Controls & 9 POI Categories (satellite, roadmap, hybrid, terrain, dark, zoom, center GPS, fullscreen)
- Places & Recommended Places (open Nth recommendation, save, unsave, lore, categories, radius)
- Multi-Action Sequencing
- Multilingual / Telugu commands
"""

import pytest
from src.aura_command_dispatcher import (
    AuraGlobalCommandDispatcher,
    AuraCommandType,
    AuraExecutionResult,
)


class TestAuraVoiceOS:

    @pytest.fixture
    def empty_session(self):
        return {
            "user_live_coords": (16.25806, 80.63609),
            "user_live_label": "Ithanagar",
            "selected_dest_coords": (16.5417, 80.5150),
            "selected_dest_label": "Amaravati",
            "routes_generated": True,
            "cached_candidate_routes": [{"id": "route_1"}, {"id": "route_2"}],
            "cached_nearby_places": [
                {"name": "Sri Krishna Vilas", "lat": 16.2375, "lon": 80.5535, "category": "Dining"},
                {"name": "IndianOil Swagat", "lat": 16.2385, "lon": 80.5545, "category": "Fuel"},
                {"name": "Chaturmukha Brahma Shrine", "lat": 16.2405, "lon": 80.5555, "category": "Attractions"}
            ],
            "saved_locations": [],
            "current_step_index": 0,
            "companion_3d_mode": True,
            "virtual_guide_moving": False,
            "aura_journey_active": False,
        }

    # =========================================================================
    # 1. ENDPOINT CLEARING & FOCUSING (Requirement 4)
    # =========================================================================
    def test_clear_all_locations_english(self, empty_session):
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Clear all locations", lang="en")
        assert res.command_type == AuraCommandType.CLEAR_LOCATIONS
        assert res.ui_updates.get("trigger_clear_all_locations") is True

        AuraGlobalCommandDispatcher.apply_execution_result(res, empty_session)
        assert empty_session["user_live_coords"] is None
        assert empty_session["selected_dest_coords"] is None
        assert empty_session["cached_candidate_routes"] is None
        assert empty_session["routes_generated"] is False

    def test_clear_all_locations_telugu(self, empty_session):
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("రూట్ క్లియర్", lang="te")
        assert res.command_type == AuraCommandType.CLEAR_LOCATIONS
        assert res.ui_updates.get("trigger_clear_all_locations") is True

    def test_clear_start_point(self, empty_session):
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Clear starting point", lang="en")
        assert res.command_type == AuraCommandType.CLEAR_ORIGIN
        assert res.ui_updates.get("trigger_clear_start") is True

        AuraGlobalCommandDispatcher.apply_execution_result(res, empty_session)
        assert empty_session["user_live_coords"] is None
        assert empty_session["selected_dest_coords"] is not None

    def test_clear_destination(self, empty_session):
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Clear destination", lang="en")
        assert res.command_type == AuraCommandType.CLEAR_DESTINATION
        assert res.ui_updates.get("trigger_clear_dest") is True

        AuraGlobalCommandDispatcher.apply_execution_result(res, empty_session)
        assert empty_session["selected_dest_coords"] is None
        assert empty_session["user_live_coords"] is not None

    def test_focus_start_and_destination(self, empty_session):
        res_s = AuraGlobalCommandDispatcher.parse_and_dispatch("Focus on start point", lang="en")
        assert res_s.command_type == AuraCommandType.MAP_FOCUS_START
        assert res_s.ui_updates.get("trigger_focus_start") is True

        AuraGlobalCommandDispatcher.apply_execution_result(res_s, empty_session)
        assert empty_session.get("map_focus_target") == "start"

        res_d = AuraGlobalCommandDispatcher.parse_and_dispatch("Focus destination", lang="en")
        assert res_d.command_type == AuraCommandType.MAP_FOCUS_DESTINATION
        assert res_d.ui_updates.get("trigger_focus_dest") is True

        AuraGlobalCommandDispatcher.apply_execution_result(res_d, empty_session)
        assert empty_session.get("map_focus_target") == "destination"

    def test_fit_both_endpoints(self, empty_session):
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Fit both on map", lang="en")
        assert res.command_type == AuraCommandType.MAP_FIT_BOUNDS
        assert res.ui_updates.get("trigger_fit_both") is True

        AuraGlobalCommandDispatcher.apply_execution_result(res, empty_session)
        assert empty_session.get("auto_fit_bounds") is True

    # =========================================================================
    # 2. VEHICLE MODE SELECTION (All 10 Modes)
    # =========================================================================
    @pytest.mark.parametrize("query,expected_mode", [
        ("Change vehicle mode to car", "CAR"),
        ("Switch to bike mode", "BIKE"),
        ("Select bus mode", "BUS"),
        ("Switch to bicycle", "BICYCLE"),
        ("Set travel mode to walk", "WALK"),
        ("Switch to truck mode", "TRUCK"),
        ("Select tractor mode", "TRACTOR"),
        ("Switch mode to flight", "FLIGHT"),
        ("Use boat mode", "WATERWAY"),
        ("Switch to train mode", "TRAIN"),
    ])
    def test_vehicle_modes(self, query, expected_mode, empty_session):
        res = AuraGlobalCommandDispatcher.parse_and_dispatch(query, lang="en")
        assert res.command_type == AuraCommandType.SELECT_VEHICLE
        assert res.ui_updates["selected_travel_mode"] == expected_mode

    # =========================================================================
    # 3. ROUTE ALTERNATIVES SELECTION (Route 1 Cyan, Route 2 Orange, Route 3 Purple)
    # =========================================================================
    def test_route_alternative_selection_english(self, empty_session):
        # Route 1 Cyan
        r1 = AuraGlobalCommandDispatcher.parse_and_dispatch("Choose Route 1", lang="en")
        assert r1.command_type == AuraCommandType.ROUTE_SELECT_ALTERNATIVE
        assert r1.ui_updates["focused_route_id"] == "route_1"

        # Route 2 Orange
        r2 = AuraGlobalCommandDispatcher.parse_and_dispatch("Select Route 2", lang="en")
        assert r2.command_type == AuraCommandType.ROUTE_SELECT_ALTERNATIVE
        assert r2.ui_updates["focused_route_id"] == "route_2"

        # Route 3 Purple
        r3 = AuraGlobalCommandDispatcher.parse_and_dispatch("Take Route 3", lang="en")
        assert r3.command_type == AuraCommandType.ROUTE_SELECT_ALTERNATIVE
        assert r3.ui_updates["focused_route_id"] == "route_3"

    def test_route_alternative_selection_telugu(self, empty_session):
        r1_te = AuraGlobalCommandDispatcher.parse_and_dispatch("రూట్ 1 ఎంచుకో", lang="te")
        assert r1_te.command_type == AuraCommandType.ROUTE_SELECT_ALTERNATIVE
        assert r1_te.ui_updates["focused_route_id"] == "route_1"

        r2_te = AuraGlobalCommandDispatcher.parse_and_dispatch("రెండవ రూట్", lang="te")
        assert r2_te.command_type == AuraCommandType.ROUTE_SELECT_ALTERNATIVE
        assert r2_te.ui_updates["focused_route_id"] == "route_2"

    def test_route_priority_modes(self):
        r_f = AuraGlobalCommandDispatcher.parse_and_dispatch("Choose fastest route", lang="en")
        assert r_f.command_type == AuraCommandType.CHANGE_ROUTE_PRIORITY
        assert r_f.ui_updates["active_objective"] == "FASTEST"

        r_s = AuraGlobalCommandDispatcher.parse_and_dispatch("Choose shortest route", lang="en")
        assert r_s.command_type == AuraCommandType.CHANGE_ROUTE_PRIORITY
        assert r_s.ui_updates["active_objective"] == "SHORTEST"

    # =========================================================================
    # 4. 3D VIRTUAL GUIDE & TOURS (Requirement 11)
    # =========================================================================
    def test_virtual_tour_lifecycle(self, empty_session):
        # Start Tour
        start_res = AuraGlobalCommandDispatcher.parse_and_dispatch("Start the virtual tour", lang="en")
        assert start_res.command_type == AuraCommandType.VIRTUAL_TOUR_START
        AuraGlobalCommandDispatcher.apply_execution_result(start_res, empty_session)
        assert empty_session["aura_journey_active"] is True
        assert empty_session["virtual_guide_moving"] is True
        assert empty_session["current_view"] == "virtual_guide"

        # Pause Tour
        pause_res = AuraGlobalCommandDispatcher.parse_and_dispatch("Pause tour", lang="en")
        assert pause_res.command_type == AuraCommandType.VIRTUAL_TOUR_PAUSE
        AuraGlobalCommandDispatcher.apply_execution_result(pause_res, empty_session)
        assert empty_session["virtual_guide_moving"] is False

        # Resume Tour
        resume_res = AuraGlobalCommandDispatcher.parse_and_dispatch("Resume tour", lang="en")
        assert resume_res.command_type == AuraCommandType.VIRTUAL_TOUR_RESUME
        AuraGlobalCommandDispatcher.apply_execution_result(resume_res, empty_session)
        assert empty_session["virtual_guide_moving"] is True

        # Next Step
        next_res = AuraGlobalCommandDispatcher.parse_and_dispatch("Next attraction", lang="en")
        assert next_res.command_type == AuraCommandType.VIRTUAL_TOUR_STEP_NEXT
        AuraGlobalCommandDispatcher.apply_execution_result(next_res, empty_session)
        assert empty_session["current_step_index"] == 1

        # Previous Step
        prev_res = AuraGlobalCommandDispatcher.parse_and_dispatch("Previous step", lang="en")
        assert prev_res.command_type == AuraCommandType.VIRTUAL_TOUR_STEP_PREV
        AuraGlobalCommandDispatcher.apply_execution_result(prev_res, empty_session)
        assert empty_session["current_step_index"] == 0

        # Stop Tour
        stop_res = AuraGlobalCommandDispatcher.parse_and_dispatch("Stop the tour", lang="en")
        assert stop_res.command_type == AuraCommandType.VIRTUAL_TOUR_STOP
        AuraGlobalCommandDispatcher.apply_execution_result(stop_res, empty_session)
        assert empty_session["aura_journey_active"] is False
        assert empty_session["virtual_guide_moving"] is False

    def test_virtual_tour_telugu(self, empty_session):
        start_te = AuraGlobalCommandDispatcher.parse_and_dispatch("టూర్ ప్రారంభించు", lang="te")
        assert start_te.command_type == AuraCommandType.VIRTUAL_TOUR_START

        next_te = AuraGlobalCommandDispatcher.parse_and_dispatch("తరువాతి దశ", lang="te")
        assert next_te.command_type == AuraCommandType.VIRTUAL_TOUR_STEP_NEXT

        toggle_3d = AuraGlobalCommandDispatcher.parse_and_dispatch("3d మోడ్ మార్చు", lang="te")
        assert toggle_3d.command_type == AuraCommandType.VIRTUAL_TOUR_TOGGLE_3D

    # =========================================================================
    # 5. MAP CONTROLS & POI CATEGORIES (Requirement 10)
    # =========================================================================
    def test_map_layer_controls(self, empty_session):
        sat = AuraGlobalCommandDispatcher.parse_and_dispatch("Switch to satellite view", lang="en")
        assert sat.command_type == AuraCommandType.MAP_SET_LAYER
        assert sat.ui_updates["map_style"] == "satellite_hybrid"

        road = AuraGlobalCommandDispatcher.parse_and_dispatch("Switch to roadmap view", lang="en")
        assert road.command_type == AuraCommandType.MAP_SET_LAYER
        assert road.ui_updates["map_style"] == "google_maps_road"

        terr = AuraGlobalCommandDispatcher.parse_and_dispatch("Switch to terrain view", lang="en")
        assert terr.command_type == AuraCommandType.MAP_SET_LAYER
        assert terr.ui_updates["map_style"] == "terrain"

    def test_map_actions(self, empty_session):
        loc = AuraGlobalCommandDispatcher.parse_and_dispatch("My location", lang="en")
        assert loc.command_type == AuraCommandType.MAP_ACTION
        assert loc.ui_updates.get("trigger_map_center_user") is True

        fs = AuraGlobalCommandDispatcher.parse_and_dispatch("Toggle full screen", lang="en")
        assert fs.command_type == AuraCommandType.MAP_ACTION
        assert fs.ui_updates.get("trigger_map_fullscreen") is True

    def test_map_poi_categories(self, empty_session):
        sm = AuraGlobalCommandDispatcher.parse_and_dispatch("Show nearby supermarkets", lang="en")
        assert sm.command_type == AuraCommandType.MAP_CATEGORY_FILTER
        assert sm.ui_updates["trigger_map_category"] == "SUPERMARKETS"

        atm = AuraGlobalCommandDispatcher.parse_and_dispatch("Show nearby ATMs", lang="en")
        assert atm.command_type == AuraCommandType.MAP_CATEGORY_FILTER
        assert atm.ui_updates["trigger_map_category"] == "ATMS"

        clear_cat = AuraGlobalCommandDispatcher.parse_and_dispatch("Clear category filter", lang="en")
        assert clear_cat.command_type == AuraCommandType.MAP_CATEGORY_FILTER
        assert clear_cat.ui_updates["trigger_map_category"] == "NONE"

    # =========================================================================
    # 6. PLACES & RECOMMENDED PLACES (Requirement 8)
    # =========================================================================
    def test_places_and_favorites(self, empty_session):
        # Open 1st recommendation
        rec1 = AuraGlobalCommandDispatcher.parse_and_dispatch("Open the first recommendation", lang="en")
        assert rec1.command_type == AuraCommandType.PLACES_OPEN_CARD
        assert rec1.ui_updates["card_index"] == 0

        AuraGlobalCommandDispatcher.apply_execution_result(rec1, empty_session)
        assert empty_session["current_selected_place"]["name"] == "Sri Krishna Vilas"

        # Save to favorites
        save_p = AuraGlobalCommandDispatcher.parse_and_dispatch("Save this place", lang="en")
        assert save_p.command_type == AuraCommandType.PLACES_SAVE_FAVORITE
        AuraGlobalCommandDispatcher.apply_execution_result(save_p, empty_session)
        assert len(empty_session["saved_locations"]) == 1
        assert empty_session["saved_locations"][0]["name"] == "Sri Krishna Vilas"

        # Remove from favorites
        unsave_p = AuraGlobalCommandDispatcher.parse_and_dispatch("Remove from favorites", lang="en")
        assert unsave_p.command_type == AuraCommandType.PLACES_REMOVE_FAVORITE
        AuraGlobalCommandDispatcher.apply_execution_result(unsave_p, empty_session)
        assert len(empty_session["saved_locations"]) == 0

    def test_places_lore_and_navigation(self, empty_session):
        lore = AuraGlobalCommandDispatcher.parse_and_dispatch("Tell me about this place", lang="en")
        assert lore.command_type == AuraCommandType.PLACES_EXPLORE_LORE
        AuraGlobalCommandDispatcher.apply_execution_result(lore, empty_session)
        assert empty_session.get("corridor_show_lore_expanded") is True

        empty_session["current_selected_place"] = {"name": "Amaravati Temple", "lat": 16.57, "lon": 80.35}
        nav = AuraGlobalCommandDispatcher.parse_and_dispatch("Navigate to this place", lang="en")
        assert nav.command_type == AuraCommandType.PLACES_EXPLORE_PLACE
        AuraGlobalCommandDispatcher.apply_execution_result(nav, empty_session)
        assert empty_session["selected_dest_coords"] == (16.57, 80.35)

    def test_places_radius_and_categories(self, empty_session):
        rad = AuraGlobalCommandDispatcher.parse_and_dispatch("Set search radius to 25 km", lang="en")
        assert rad.command_type == AuraCommandType.PLACES_SET_RADIUS
        assert rad.ui_updates["places_search_radius_km"] == 25

        attr = AuraGlobalCommandDispatcher.parse_and_dispatch("Show famous attractions", lang="en")
        assert attr.command_type == AuraCommandType.PLACES_SET_CATEGORY
        assert attr.ui_updates["places_active_category"] == "Famous Attractions"

    # =========================================================================
    # 7. MULTI-ACTION SEQUENCING (Requirement 13)
    # =========================================================================
    def test_multi_action_sequence_english(self, empty_session):
        query = "Start from Ithanagar, navigate to Amaravati, set vehicle to bike, choose fastest route and start navigation"
        res = AuraGlobalCommandDispatcher.parse_and_dispatch(query, lang="en")
        assert res.command_type == AuraCommandType.MULTI_ACTION_SEQUENCE
        assert res.ui_updates["selected_travel_mode"] == "BIKE"
        assert res.ui_updates["active_objective"] == "FASTEST"
        assert res.ui_updates["aura_journey_active"] is True
        assert res.ui_updates["virtual_guide_moving"] is True
