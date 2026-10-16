"""
Unit Tests for Google Maps & Swiggy-Style AI Voice Navigation Engine
"""

import pytest
from src.google_maps_voice_navigator import (
    haversine_m,
    slice_polyline_into_small_routes,
    build_spoken_instruction,
    prepare_google_maps_voice_data,
    render_google_maps_voice_navigator_html
)
from src.route_engine import RouteOption, TravelMode
from src.multi_objective_router import RankedRoute, RouteEligibilityStatus


def test_haversine_distance():
    p1 = (16.2335, 80.5505)
    p2 = (16.2435, 80.5605)
    d = haversine_m(p1, p2)
    assert d > 1000  # greater than 1km
    assert d < 3000


def test_slice_polyline_into_small_routes():
    polyline = [
        [16.230, 80.550],
        [16.232, 80.552],
        [16.235, 80.555],
        [16.238, 80.558],
        [16.240, 80.560]
    ]
    steps = [
        {"step_num": 1, "road": "Road A", "distance_m": 500},
        {"step_num": 2, "road": "Road B", "distance_m": 800}
    ]
    segments = slice_polyline_into_small_routes(polyline, steps)
    assert len(segments) == 2
    assert len(segments[0]) >= 2
    assert len(segments[1]) >= 2


def test_build_spoken_instruction():
    step = {"instruction": "Turn left onto Tenali Road", "road": "Tenali Road", "distance_m": 2400}
    next_step = {"instruction": "Continue onto Main Corridor", "road": "Main Corridor", "distance_m": 800}

    spoken = build_spoken_instruction(step, next_step, is_first=False, is_last=False)
    assert "In 2.4 kilometers" in spoken
    assert "Turn left onto Tenali Road" in spoken
    assert "Main Corridor" in spoken


def test_prepare_and_render_google_maps_voice_data():
    sample_route = RouteOption(
        route_id="ROUTE_TEST_1",
        name="Tenali Rapid Bypass (Primary Arterial)",
        mode=TravelMode.WALKING,
        distance_meters=2500.0,
        duration_seconds=1800.0,
        polyline=[[16.2335, 80.5505], [16.2380, 80.5550], [16.2420, 80.5600]],
        summary_roads=["Vadlamudi Road", "Tenali Expressway"],
        steps=[
            {"step_num": 1, "icon": "🟢", "instruction": "Head out on Vadlamudi Road", "road": "Vadlamudi Road", "distance_m": 1000},
            {"step_num": 2, "icon": "⬅️", "instruction": "Turn left onto Tenali Expressway", "road": "Tenali Expressway", "distance_m": 1500}
        ]
    )

    sample_ranked = RankedRoute(
        route=sample_route,
        rank=1,
        is_eligible=True,
        status=RouteEligibilityStatus.ELIGIBLE,
        composite_score=1.0,
        effective_duration_minutes=30.0,
        effective_distance_km=2.5,
        time_savings_minutes_vs_slowest=0.0,
        distance_diff_km_vs_shortest=0.0
    )

    nav_data = prepare_google_maps_voice_data(
        active_route_item=sample_ranked,
        origin_label="Vignan University",
        destination_label="Tenali Junction",
        unit="km",
        auto_start=True
    )

    assert nav_data["default_avatar"] == "boy"
    assert len(nav_data["steps"]) == 2
    assert "Tenali Expressway" in nav_data["steps"][1]["road"]
    assert "Starting navigation" in nav_data["initial_spoken"]

    html = render_google_maps_voice_navigator_html(nav_data, height=540)
    assert "gmaps-nav-container" in html
    assert "small-boy-marker" in html
    assert "speechSynthesis" in html
    assert "Swiggy" in html
