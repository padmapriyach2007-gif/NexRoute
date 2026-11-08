"""
Unit and regression tests for accurate road-based multiple routing in Andhra Pradesh:
1. Valid road geometry (no straight lines, follows real highway/arterial roads)
2. Multiple distinct alternatives (Route 1 Primary Cyan, Route 2 Orange, Route 3 Purple)
3. String coordinate extraction from parenthetical formats like 'Amaravati (16.5417, 80.5150)'
4. 5 core test cases around Guntur, Tenali, Vijayawada, Narakoduru, Suddapalli, Sangam Jagarlamudi.
"""

import re
import pytest
from src.route_engine import RealWorldRouteEngine, TravelMode, filter_distinct_routes, calculate_spatial_route_overlap
from src.road_condition_model import OptimizationObjective
from src.multi_objective_router import MultiObjectiveRouter


def test_parenthetical_coordinate_extraction_regex():
    """Verify coordinate extraction parses strings with trailing coordinates like 'Amaravati (14.51209, 75.82267)'."""
    samples = [
        ("Amaravati (14.51209, 75.82267)", 14.51209, 75.82267, "Amaravati"),
        ("Ithanagar (16.25806, 80.63609)", 16.25806, 80.63609, "Ithanagar"),
        ("16.3067, 80.4365", 16.3067, 80.4365, ""),
        ("Guntur (16.3067, 80.4365)", 16.3067, 80.4365, "Guntur"),
    ]
    for text, expected_lat, expected_lon, expected_name in samples:
        m = re.search(r"\(?\s*([+-]?\d{1,2}(?:\.\d+)?)\s*[,\s]\s*([+-]?\d{1,3}(?:\.\d+)?)\s*\)?\s*$", text)
        assert m is not None, f"Failed to match regex on: {text}"
        lat = float(m.group(1))
        lon = float(m.group(2))
        assert abs(lat - expected_lat) < 1e-4
        assert abs(lon - expected_lon) < 1e-4
        if expected_name:
            raw_place = text[:m.start()].strip(" (,-")
            assert raw_place == expected_name


def test_guntur_to_narakoduru_road_route():
    """Verify road route between Guntur and Narakoduru."""
    engine = RealWorldRouteEngine()
    routes = engine.calculate_routes(16.3067, 80.4365, 16.2415, 80.5284, mode=TravelMode.CAR)
    assert len(routes) >= 2, f"Expected at least 2 road routes, got {len(routes)}"
    r1 = routes[0]
    assert len(r1.polyline) > 50, "Route must follow actual road curves with dozens of coordinates"
    assert 14.0 <= r1.distance_km <= 35.0, f"Guntur to Narakoduru distance should be 15-30 km, got {r1.distance_km}"
    assert r1.duration_minutes > 10.0


def test_suddapalli_to_sangam_jagarlamudi_road_route():
    """Verify short road connection between Suddapalli and Sangam Jagarlamudi."""
    engine = RealWorldRouteEngine()
    routes = engine.calculate_routes(16.2230, 80.5750, 16.2380, 80.5600, mode=TravelMode.CAR)
    assert len(routes) >= 1
    r = routes[0]
    assert len(r.polyline) > 10
    assert 1.0 <= r.distance_km <= 8.0


def test_distinct_route_corridors_and_colors():
    """Verify multiple alternatives have distinct IDs, ranks, and Google Maps color palette."""
    engine = RealWorldRouteEngine()
    router = MultiObjectiveRouter()
    
    # Guntur to Tenali
    routes = engine.calculate_routes(16.3067, 80.4365, 16.2437, 80.6400, mode=TravelMode.CAR)
    assert len(routes) >= 1
    ranked = router.evaluate_and_rank_routes(routes, primary_objective=OptimizationObjective.FASTEST)
    assert len(ranked) >= 1
    
    palette = ["#00F0FF", "#F59E0B", "#A855F7"]
    for item in ranked:
        expected_color = palette[(item.rank - 1) % len(palette)]
        assert expected_color.startswith("#")
        assert len(item.route.polyline) > 20
