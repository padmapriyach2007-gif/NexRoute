"""
Test Suite for Virtual Guide Unlock and Navigation Redirection Flow
Verifies:
1. Virtual Guide unlocks when start/stop locations or active routes exist.
2. Direct dynamic fallback from coordinates to calculate active route on the fly.
3. tab_guide is present in navigation st.tabs in app.py.
4. Launch 3D Virtual Guide & Storyteller CTA button and redirection in navigation.
5. Quick header navigation between Virtual Guide and Navigation Map.
"""

import pytest
import streamlit as st
from unittest.mock import MagicMock
from src.route_engine import RouteOption, TravelMode
from src.multi_objective_router import RankedRoute, RouteEligibilityStatus


def test_resolve_active_route_from_session_state():
    from app import resolve_virtual_guide_active_route

    dummy_route = RouteOption(
        route_id="dummy_r1",
        name="Test Corridor",
        mode=TravelMode.DRIVING,
        distance_meters=5000.0,
        duration_seconds=600.0,
        polyline=[[16.233, 80.548], [16.240, 80.555]],
        summary_roads=["Main Road"],
        source="test"
    )
    dummy_item = RankedRoute(
        route=dummy_route,
        rank=1,
        is_eligible=True,
        status=RouteEligibilityStatus.ELIGIBLE,
        composite_score=1.0,
        effective_duration_minutes=10.0,
        effective_distance_km=5.0,
        time_savings_minutes_vs_slowest=0.0,
        distance_diff_km_vs_shortest=0.0
    )

    st.session_state["active_route_item"] = dummy_item
    resolved = resolve_virtual_guide_active_route()
    assert resolved is not None
    assert resolved.route.route_id == "dummy_r1"


def test_resolve_active_route_from_selected_route_object():
    from app import resolve_virtual_guide_active_route

    st.session_state["active_route_item"] = None
    dummy_route = RouteOption(
        route_id="dummy_selected",
        name="Selected Expressway",
        mode=TravelMode.DRIVING,
        distance_meters=12000.0,
        duration_seconds=900.0,
        polyline=[[16.233, 80.548], [16.300, 80.600]],
        summary_roads=["Expressway A"],
        source="test"
    )
    st.session_state["selected_route_object"] = dummy_route

    resolved = resolve_virtual_guide_active_route()
    assert resolved is not None
    assert resolved.route.route_id == "dummy_selected"
    assert resolved.effective_distance_km == 12.0
    assert resolved.effective_duration_minutes == 15.0


def test_resolve_active_route_empty_when_no_route():
    from app import resolve_virtual_guide_active_route

    st.session_state["active_route_item"] = None
    st.session_state["selected_route_object"] = None
    st.session_state["cached_candidate_routes"] = None
    st.session_state["user_live_coords"] = None
    st.session_state["selected_dest_coords"] = None

    resolved = resolve_virtual_guide_active_route()
    assert resolved is None


def test_app_file_contains_tab_guide_and_redirection_cta():
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Verify clean tabs in st.tabs (Virtual Guide tab removed from top tab bar as requested)
    assert "tab_nav, tab_fac = st.tabs([nav_tab_lbl, fac_tab_lbl])" in content

    # Verify Launch 3D Virtual Guide CTA in tab_nav
    assert "btn_nav_launch_virtual_guide_hud" in content
    assert "st.session_state.current_view = \"virtual_guide\"" in content
    assert "st.session_state[\"active_route_item\"] = active_route_item" in content


def test_header_contains_back_to_map_in_guide_view():
    from src.travel_copilot_studio import render_view_navigation_header
    with open("src/travel_copilot_studio.py", "r", encoding="utf-8") as f:
        studio_content = f.read()

    assert 'def render_view_navigation_header' in studio_content
    assert 'btn_back_to_dash_' in studio_content
