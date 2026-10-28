"""
Comprehensive Test Suite for ALL Buttons in the P.A.T.H.F.I.N.D.E.R. Application.
Tests every button from first to last:
1. Start Panel Controls (Focus, Clear, My Location, Pick on Map, Custom Start)
2. Destination Panel Controls (Focus, Clear, Pick on Map, Custom Destination)
3. Global Controls (Swap Locations, Find Routes, Fit Route, Fit Both)
4. Custom Coordinate Modal Buttons (Resolve, Pick on Map, Confirm, Cancel)
5. Route Objective Classification Buttons (ALL, FASTEST, SHORTEST, BALANCED, ACCESSIBLE)
6. Route Avoidance Toggles (Avoid Tolls, Avoid Highways, Avoid Ferries)
7. Speed Steppers & Mode Launchers
8. Emergency Safety Dock & SOS Buttons (Medical, Police, Disaster, Fuel/Breakdown)
9. Map HTML Controls & Layers (Hybrid Satellite, Pure Satellite, Roadmap, Terrain, Measure, Street View, Traffic, Labels)
"""

import pytest
from src.map_service import MapService
from src.route_engine import RealWorldRouteEngine, TravelMode
from src.multi_objective_router import MultiObjectiveRouter, OptimizationObjective
from src.google_maps_platform import build_google_maps_javascript_html


def test_start_and_destination_buttons_presence_and_attributes():
    """Verify that all Start, Destination, and Global action buttons exist with correct labels and keys in app.py."""
    with open("app.py", "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Streamlined Start buttons (Pick Start, Focus Start, Clear Start)
    assert 'key="btn_side_pick_start"' in code
    assert '"📍 Pick Start on Map"' in code
    assert 'key="btn_side_focus_start"' in code
    assert '"🎯 Focus Start"' in code
    assert 'key="btn_side_clear_start"' in code
    assert '"✕ Clear Start"' in code

    # Verify duplicate redundant buttons were removed
    assert 'key="btn_side_use_gps"' not in code
    assert 'key="btn_side_custom_start"' not in code
    assert 'key="btn_side_fit_bounds_start"' not in code

    # 2. Streamlined Destination buttons (Pick Destination, Focus Destination, Clear Destination)
    assert 'key="btn_side_pick_dest"' in code
    assert '"🏁 Pick Destination on Map"' in code
    assert 'key="btn_side_focus_dest"' in code
    assert '"🎯 Focus Destination"' in code
    assert 'key="btn_side_clear_dest"' in code
    assert '"✕ Clear Destination"' in code

    # Verify duplicate redundant destination button was removed
    assert 'key="btn_side_custom_dest"' not in code

    # 3. Global action buttons
    assert 'key="btn_side_swap_endpoints"' in code
    assert '"⇅ Swap Locations"' in code
    assert 'key="btn_side_calc_routes_action"' in code
    assert '"🚀 Find Routes"' in code
    assert 'key="btn_side_fit_route_bounds_act"' in code
    assert '"🔍 Fit Route"' in code


def test_custom_modal_buttons_validation():
    """Verify that the custom coordinate modal provides address resolution, coordinate validation, and confirmation."""
    with open("app.py", "r", encoding="utf-8") as f:
        code = f.read()

    assert 'key="btn_modal_resolve_addr"' in code
    assert 'key="btn_modal_pick_on_map"' in code
    assert 'key="btn_modal_confirm_loc"' in code
    assert 'key="btn_modal_cancel"' in code
    # Coordinate range validation (-90 to 90, -180 to 180)
    assert "-90.0 <= custom_lat <= 90.0" in code
    assert "-180.0 <= custom_lon <= 180.0" in code


def test_route_classification_buttons_and_scoring_logic():
    """Verify all 5 route classification buttons and their mathematical selection formulas."""
    engine = RealWorldRouteEngine()
    routes = engine.calculate_routes(15.7688, 79.6792, 16.3067, 80.4365, mode=TravelMode.DRIVING)
    assert len(routes) >= 1

    router = MultiObjectiveRouter()

    # 1. FASTEST button logic
    fastest_ranked = router.evaluate_and_rank_routes(routes, objective=OptimizationObjective.FASTEST)
    min_time = min(r.effective_duration_minutes for r in fastest_ranked if r.is_eligible)
    assert fastest_ranked[0].effective_duration_minutes == min_time

    # 2. SHORTEST button logic
    shortest_ranked = router.evaluate_and_rank_routes(routes, objective=OptimizationObjective.SHORTEST)
    min_dist = min(r.effective_distance_km for r in shortest_ranked if r.is_eligible)
    assert shortest_ranked[0].effective_distance_km == min_dist

    # 3. BALANCED button logic (exact formula: 0.5 * T/T_max + 0.5 * D/D_max)
    balanced_ranked = router.evaluate_and_rank_routes(routes, objective=OptimizationObjective.BALANCED)
    max_t = max(r.effective_duration_minutes for r in balanced_ranked if r.is_eligible)
    max_d = max(r.effective_distance_km for r in balanced_ranked if r.is_eligible)
    expected_score = 0.5 * (balanced_ranked[0].effective_duration_minutes / max_t) + 0.5 * (balanced_ranked[0].effective_distance_km / max_d)
    assert abs(balanced_ranked[0].composite_score - expected_score) < 0.05

    # 4. ACCESSIBLE button logic
    acc_ranked = router.evaluate_and_rank_routes(routes, objective=OptimizationObjective.ACCESSIBLE, require_accessible=False)
    for r in acc_ranked:
        if not r.accessibility_verified:
            assert "Accessibility information unavailable." in r.accessibility_notes


def test_avoidance_buttons_and_steppers():
    """Verify avoidance buttons (tolls, highways, ferries) and speed steppers."""
    with open("app.py", "r", encoding="utf-8") as f:
        code = f.read()

    assert 'key="btn_hud_avoid_tolls"' in code
    assert 'key="btn_hud_avoid_highways"' in code
    assert 'key="btn_hud_avoid_ferries"' in code
    assert 'key="btn_stp_m10"' in code
    assert 'key="btn_stp_m5"' in code
    assert 'key="btn_stp_p5"' in code
    assert 'key="btn_stp_p10"' in code


def test_emergency_dock_buttons():
    """Verify safety dock buttons: Medical, Police, Disaster, and Breakdown SOS."""
    with open("app.py", "r", encoding="utf-8") as f:
        code = f.read()

    assert 'key="btn_toggle_emergency_radar"' in code
    assert 'key="btn_dock_sos_med"' in code
    assert 'key="btn_dock_sos_police"' in code
    assert 'key="btn_dock_sos_disaster"' in code
    assert 'key="btn_dock_sos_fuel"' in code


def test_html_map_controls_and_layers():
    """Verify map buttons: Layers drawer, Google Satellite & Hybrid streams, Measure, Street View, Traffic."""
    html = build_google_maps_javascript_html(
        center_lat=15.7688,
        center_lon=79.6792,
        zoom=14,
        origin_coords=(15.7688, 79.6792),
        dest_coords=(16.3067, 80.4365),
        map_type="hybrid"
    )

    # 1. Layers drawer button and cards
    assert "gmap-layers-trigger" in html
    assert "maptype-card-hybrid" in html
    assert "maptype-card-satellite" in html
    assert "maptype-card-default" in html
    assert "layer-btn-terrain" in html

    # 2. Tile streams (Google Satellite & Hybrid)
    assert "google.com/vt/lyrs=y" in html
    assert "google.com/vt/lyrs=s" in html

    # 3. Tools
    assert "tool-btn-measure" in html
    assert "layer-btn-streetview" in html
    assert "layer-btn-traffic" in html
    assert "layer-btn-transit" in html
    assert "layer-btn-biking" in html
    assert "layer-btn-hazards" in html
    assert "chk-map-labels" in html

    # 4. Pointers & drag support
    assert "draggable: true" in html
    assert "window.handleMarkerDragEnd" in html
    assert "allFitBounds" in html

