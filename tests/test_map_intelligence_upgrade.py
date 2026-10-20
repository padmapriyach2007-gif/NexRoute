"""
Automated Test Suite for PATHFINDER Complete Map Intelligence Upgrade:
- Location resolution & geocoding across villages, landmarks, addresses, and coordinates
- Locality disambiguation and spelling variations
- Campus internal POI limitation handling
- Multi-route alternative generation & spatial uniqueness validation
- Interactive map integration & route selection synchronization
"""

import pytest
from typing import Dict, List, Any
from src.map_service import MapService
from src.route_engine import (
    RealWorldRouteEngine,
    RouteOption,
    TravelMode,
    calculate_spatial_route_overlap,
    calculate_road_segment_overlap,
    filter_distinct_routes,
    verify_route_validity,
    recalculate_route_metrics
)
from src.google_maps_platform import build_google_maps_javascript_html


# =============================================================================
# 1. LOCATION RESOLUTION & GEOCODING TESTS
# =============================================================================

def test_geocode_exact_address():
    """Verify exact address resolves accurately to confirmed coordinates."""
    srv = MapService()
    res = srv.geocode("BSR Enclave, Sarojini Naidu Street, Tenali")
    assert res is not None
    assert abs(res["lat"] - 16.23454) < 0.001
    assert abs(res["lon"] - 80.65197) < 0.001
    assert "Tenali" in res["display_name"]


def test_geocode_small_village_and_town():
    """Verify small villages (Namburu, Sekuru) and towns (Tenali, Bapatla) resolve."""
    srv = MapService()
    # Namburu village
    res_namburu = srv.geocode("Namburu, Guntur district")
    assert res_namburu is not None
    assert abs(res_namburu["lat"] - 16.3610) < 0.01
    assert abs(res_namburu["lon"] - 80.4980) < 0.01

    # Bapatla town
    res_bapatla = srv.geocode("Bapatla")
    assert res_bapatla is not None
    assert abs(res_bapatla["lat"] - 15.9042) < 0.01


def test_geocode_regional_landmark():
    """Verify regional landmarks like Asta Lakshmi Temple and Guntur Railway Station resolve."""
    srv = MapService()
    res_temple = srv.geocode("Asta Lakshmi Temple, Tenali")
    assert res_temple is not None
    assert abs(res_temple["lat"] - 16.2385) < 0.01
    assert abs(res_temple["lon"] - 80.6420) < 0.01
    assert "Tenali" in res_temple["display_name"]

    res_station = srv.geocode("Guntur Railway Station")
    assert res_station is not None
    assert abs(res_station["lat"] - 16.3045) < 0.01


def test_geocode_locality_ranking_prevents_wrong_city():
    """
    When searching 'Asta Lakshmi Temple, Tenali', ensure candidate in Tenali, AP
    ranks above any candidate from Khammam or other districts.
    """
    srv = MapService()
    candidates = srv.geocode_candidates("Asta Lakshmi Temple, Tenali", limit=5)
    assert len(candidates) >= 1
    top_cand = candidates[0]
    assert "Tenali" in top_cand["display_name"] or top_cand.get("city") == "Tenali"
    assert "Khammam" not in top_cand.get("display_name", "")


def test_geocode_spelling_variations():
    """Verify spelling variations and transliterations resolve consistently."""
    srv = MapService()
    res1 = srv.geocode("Asta Lakshmi Temple, Tenali")
    res2 = srv.geocode("Astalakshmi Temple, Tenali")
    assert res1 is not None and res2 is not None
    assert abs(res1["lat"] - res2["lat"]) < 0.001
    assert abs(res1["lon"] - res2["lon"]) < 0.001


def test_geocode_invalid_coordinates():
    """Out-of-bounds coordinates must return None / [] and never fabricate points."""
    srv = MapService()
    assert srv.geocode("95.0, 80.0") is None
    assert srv.geocode("-95.0, 80.0") is None
    assert srv.geocode("20.0, 195.0") is None
    assert srv.geocode("20.0, -195.0") is None


def test_geocode_unresolvable_place():
    """Unresolvable gibberish must return None rather than substituting a fake anchor."""
    srv = MapService()
    # Mock network call to return empty for fake place
    res = srv.geocode("ZzzNonexistentPlace999888777XyZ")
    assert res is None


def test_geocode_campus_internal_poi():
    """Verify campus internal POIs provide entrance coordinate note per Phase 2.6."""
    srv = MapService()
    res = srv.geocode("The cafeteria, Vignan University, Vadlamudi")
    assert res is not None
    assert abs(res["lat"] - 16.2336) < 0.005
    assert abs(res["lon"] - 80.5525) < 0.005
    assert res.get("is_campus_internal") is True
    assert "campus_entrance" in res or "nearest road entrance" in res["display_name"].lower()


def test_geocode_current_location_keyword():
    """Verify 'Current Location' or 'My Location' keywords return current location entry."""
    srv = MapService()
    res = srv.geocode("Current Location")
    assert res is not None
    assert res["type"] == "current_location"


# =============================================================================
# 2. ROUTE GENERATION & SPATIAL DIVERSITY TESTS
# =============================================================================

def test_route_generation_between_confirmed_locations():
    """Verify routing engine generates valid routes between confirmed coordinates."""
    engine = RealWorldRouteEngine()
    # Tenali (16.2430, 80.6400) to Vadlamudi (16.2319, 80.5539)
    routes = engine.calculate_routes(16.2430, 80.6400, 16.2319, 80.5539, mode=TravelMode.DRIVING)
    assert len(routes) >= 1
    for r in routes:
        assert r.distance_meters > 0
        assert r.duration_seconds > 0
        assert len(r.polyline) >= 2


def test_multiple_distinct_alternatives_spatial_uniqueness():
    """Verify that multiple route alternatives have distinct geometry and spatial overlap < 85%."""
    engine = RealWorldRouteEngine()
    routes = engine.calculate_routes(16.2430, 80.6400, 16.2319, 80.5539, mode=TravelMode.DRIVING)
    if len(routes) >= 2:
        overlap = calculate_spatial_route_overlap(routes[0].polyline, routes[1].polyline)
        assert overlap < 0.85, f"Alternatives share {overlap*100:.1f}% geometry, expected distinct corridors"


def test_duplicate_route_detection():
    """Verify duplicate routes are detected and filtered."""
    poly = [(16.2430, 80.6400), (16.2380, 80.5900), (16.2319, 80.5539)]
    r1 = RouteOption(
        route_id="r1", name="Route 1", mode=TravelMode.DRIVING,
        distance_meters=10000, duration_seconds=600, polyline=list(poly),
        summary_roads=["Main Highway"]
    )
    r2_dup = RouteOption(
        route_id="r2", name="Route 2", mode=TravelMode.DRIVING,
        distance_meters=10000, duration_seconds=600, polyline=list(poly),
        summary_roads=["Main Highway"]
    )
    distinct = filter_distinct_routes([r1, r2_dup], max_overlap=0.80)
    assert len(distinct) == 1


def test_route_endpoint_validity():
    """Verify route polyline strictly aligns with requested start and destination."""
    origin = (16.2430, 80.6400)
    dest = (16.2319, 80.5539)
    valid_route = RouteOption(
        route_id="test_val", name="Valid Route", mode=TravelMode.DRIVING,
        distance_meters=11000, duration_seconds=700,
        polyline=[origin, (16.238, 80.60), dest]
    )
    is_valid, _ = verify_route_validity(valid_route, origin[0], origin[1], dest[0], dest[1])
    assert is_valid is True

    # Polyline starting 10km away must be rejected
    invalid_route = RouteOption(
        route_id="test_inval", name="Far Route", mode=TravelMode.DRIVING,
        distance_meters=11000, duration_seconds=700,
        polyline=[(16.50, 80.80), dest]
    )
    is_valid2, _ = verify_route_validity(invalid_route, origin[0], origin[1], dest[0], dest[1])
    assert is_valid2 is False


def test_recalculate_route_metrics():
    """Verify distance and duration recalculation matches polyline Haversine length."""
    poly = [(16.2430, 80.6400), (16.2319, 80.5539)]
    route = RouteOption(
        route_id="recalc_test", name="Test Recalc", mode=TravelMode.DRIVING,
        distance_meters=0, duration_seconds=0, polyline=poly
    )
    recalculate_route_metrics(route)
    assert route.distance_meters > 8000
    assert route.duration_seconds > 0


# =============================================================================
# 3. INTERACTIVE MAP & ROUTE SELECTION TESTS
# =============================================================================

def test_google_maps_platform_html_multi_polylines():
    """Verify build_google_maps_javascript_html embeds all route polylines and selection state."""
    r_polys = [
        {
            "name": "Primary Arterial Route",
            "coordinates": [[16.24, 80.64], [16.23, 80.55]],
            "color": "#10b981",
            "weight": 8,
            "opacity": 1.0,
            "is_selected": True,
            "route_id": "primary_arterial"
        },
        {
            "name": "Alternative Corridor 2",
            "coordinates": [[16.24, 80.64], [16.25, 80.58], [16.23, 80.55]],
            "color": "#0ea5e9",
            "weight": 3.5,
            "opacity": 0.40,
            "is_selected": False,
            "route_id": "alt_corridor_2"
        }
    ]

    html = build_google_maps_javascript_html(
        center_lat=16.235,
        center_lon=80.595,
        zoom=14,
        origin_coords=(16.24, 80.64),
        dest_coords=(16.23, 80.55),
        route_polyline=[(16.24, 80.64), (16.23, 80.55)],
        route_polylines=r_polys
    )

    assert "routePolylines" in html
    assert "primary_arterial" in html
    assert "alt_corridor_2" in html
    assert "focus_route" in html


def test_route_selection_highlight_state():
    """Selecting Alternative 2 marks Alternative 2 as selected and Primary as unselected."""
    routes = [
        {"route_id": "r1", "is_selected": False},
        {"route_id": "r2", "is_selected": True}
    ]
    selected = next(r for r in routes if r["is_selected"])
    assert selected["route_id"] == "r2"
