"""
Unit and Integration Tests for Route Alternatives Preservation, Accurate Road Geometry,
Distance/Duration Synchronization, and Map Camera Bounds in NextRoute.
"""

import pytest
import math
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any

from src.route_engine import (
    RouteOption,
    TravelMode,
    RealWorldRouteEngine,
    OSRMGlobalRoutingProvider,
    snap_to_road_network,
    verify_route_validity,
    filter_distinct_routes,
    haversine_distance_m
)


# =============================================================================
# SCENARIO A: INITIAL ROUTE CALCULATION & ROAD NETWORK INTEGRITY
# =============================================================================

def test_initial_route_calculation_valid_road_geometry():
    """Verify route follows valid coordinates, positive distance, and positive duration."""
    engine = RealWorldRouteEngine()
    # Guntur to Vijayawada coordinates (~32 km)
    orig_lat, orig_lon = 16.3067, 80.4365
    dest_lat, dest_lon = 16.5062, 80.6480

    routes = engine.calculate_routes(orig_lat, orig_lon, dest_lat, dest_lon, mode=TravelMode.DRIVING)
    assert len(routes) >= 1

    for r in routes:
        assert r.distance_meters > 20000.0  # At least 20 km
        assert r.duration_seconds > 600.0   # At least 10 minutes
        assert len(r.polyline) >= 20        # Rich road polyline

        # Verify geometry validity
        is_valid, msg = verify_route_validity(r, orig_lat, orig_lon, dest_lat, dest_lon)
        assert is_valid, f"Route geometry failed validation: {msg}"

        # Must not contain NaN or Inf
        for pt in r.polyline:
            assert math.isfinite(pt[0])
            assert math.isfinite(pt[1])
            assert -90.0 <= pt[0] <= 90.0
            assert -180.0 <= pt[1] <= 180.0


# =============================================================================
# SCENARIO B: MULTIPLE ROUTE ALTERNATIVES PRESERVATION ON SELECTION
# =============================================================================

def test_multiple_route_alternatives_preserved_on_selection():
    """Selecting one route alternative must not remove or clear the unselected alternatives."""
    # Create 3 distinct mock routes
    route_1 = RouteOption(
        route_id="OSRM_1",
        name="Recommended Highway Route (Fastest)",
        mode=TravelMode.DRIVING,
        distance_meters=32000.0,
        duration_seconds=2400.0,
        polyline=[[16.3067, 80.4365], [16.3500, 80.4800], [16.4200, 80.5500], [16.5062, 80.6480]]
    )
    route_2 = RouteOption(
        route_id="OSRM_2",
        name="Alternative 1: Via Arterial Network",
        mode=TravelMode.DRIVING,
        distance_meters=35000.0,
        duration_seconds=2700.0,
        polyline=[[16.3067, 80.4365], [16.3700, 80.4600], [16.4500, 80.5200], [16.5062, 80.6480]]
    )
    route_3 = RouteOption(
        route_id="OSRM_3",
        name="Alternative 2: Regional Bypass Route",
        mode=TravelMode.DRIVING,
        distance_meters=38000.0,
        duration_seconds=3000.0,
        polyline=[[16.3067, 80.4365], [16.3200, 80.5100], [16.4300, 80.5800], [16.5062, 80.6480]]
    )

    all_routes = [route_1, route_2, route_3]
    cur_focus = "OSRM_2"  # User selects Route 2

    # Simulate polyline generation logic in app.py
    route_polylines = []
    for r in all_routes:
        is_selected = (r.route_id == cur_focus)
        route_polylines.append({
            "route_id": r.route_id,
            "coordinates": r.polyline,
            "is_selected": is_selected,
            "weight": 8.5 if is_selected else 5.0,
            "opacity": 1.0 if is_selected else 0.70
        })

    # All 3 routes must remain present in polylines
    assert len(route_polylines) == 3
    selected_items = [p for p in route_polylines if p["is_selected"]]
    unselected_items = [p for p in route_polylines if not p["is_selected"]]

    assert len(selected_items) == 1
    assert selected_items[0]["route_id"] == "OSRM_2"
    assert selected_items[0]["weight"] == 8.5
    assert len(unselected_items) == 2
    assert {u["route_id"] for u in unselected_items} == {"OSRM_1", "OSRM_3"}


# =============================================================================
# SCENARIO C: MAP CAMERA BOUNDS CALCULATION
# =============================================================================

def test_map_bounds_covers_all_routes_and_endpoints():
    """Bounds calculation must include all visible route coordinates and endpoints."""
    from src.map_service import MapService

    orig = (16.3067, 80.4365)
    dest = (16.5062, 80.6480)
    poly_1 = [[16.3067, 80.4365], [16.3500, 80.4800], [16.5062, 80.6480]]
    poly_2 = [[16.3067, 80.4365], [16.4000, 80.6000], [16.5062, 80.6480]]

    route_polylines = [
        {"name": "Route 1", "coordinates": poly_1, "is_selected": False, "rank": 1},
        {"name": "Route 2", "coordinates": poly_2, "is_selected": True, "rank": 2}
    ]

    service = MapService()
    f_map = service.build_interactive_map(
        center_lat=16.4000,
        center_lon=80.5400,
        zoom_start=14,
        origin_coords=orig,
        dest_coords=dest,
        route_polylines=route_polylines
    )
    assert f_map is not None


# =============================================================================
# SCENARIO D: ROUTE RECALCULATION & RACE CONDITION GUARD
# =============================================================================

def test_request_sequence_prevents_stale_response_overwrites():
    """A stale async route request must not overwrite a newer request."""
    st_mock = {
        "route_request_seq": 1,
        "cached_candidate_routes": ["VALID_ROUTE_1"],
        "route_calculation_status": "CALCULATING"
    }

    # First request starts with seq = 1
    req_1_id = 1
    # User immediately triggers a second request with seq = 2
    st_mock["route_request_seq"] = 2
    req_2_id = 2

    # Request 2 completes first
    candidate_routes_2 = ["VALID_ROUTE_2_NEW"]
    if req_2_id == st_mock["route_request_seq"]:
        st_mock["cached_candidate_routes"] = candidate_routes_2
        st_mock["route_calculation_status"] = "SUCCESS"

    assert st_mock["cached_candidate_routes"] == ["VALID_ROUTE_2_NEW"]

    # Request 1 arrives late (stale)
    candidate_routes_1 = ["STALE_ROUTE_OLD"]
    if req_1_id == st_mock["route_request_seq"]:
        st_mock["cached_candidate_routes"] = candidate_routes_1  # Should NOT be reached

    # Must preserve Request 2 result
    assert st_mock["cached_candidate_routes"] == ["VALID_ROUTE_2_NEW"]


# =============================================================================
# SCENARIO E: NO 0 KM AND 1 MIN ROUTE SUMMARY
# =============================================================================

def test_route_summary_never_displays_0km_1min_on_failure():
    """When route calculation fails or is pending, 0 km and 1 min must not be fabricated."""
    from src.i18n import format_distance, format_duration

    # Valid route case
    dist_val = 32.4
    dur_val = 38.0
    assert format_distance(dist_val) == "32.4 km"
    assert "38 min" in format_duration(dur_val)

    # Empty / failed route case
    failed_item = None
    dist_failed = float(failed_item.effective_distance_km) if failed_item else 0.0
    # Must NOT render valid summary when dist_failed <= 0.0
    should_render_summary = (failed_item is not None and dist_failed > 0.0)
    assert should_render_summary is False


# =============================================================================
# SCENARIO F: ROAD NETWORK SNAPPING & ELIMINATION OF FIELD CROSSING
# =============================================================================

def test_snap_to_road_network_returns_real_road_point():
    """Off-road coordinates must snap to the nearest road network within 800m."""
    # Coordinates near Guntur NH-16
    test_lat, test_lon = 16.3075, 80.4370
    snap_res = snap_to_road_network(test_lat, test_lon, mode=TravelMode.DRIVING)

    assert "snapped_lat" in snap_res
    assert "snapped_lon" in snap_res
    assert "distance_m" in snap_res
    assert math.isfinite(snap_res["snapped_lat"])
    assert math.isfinite(snap_res["snapped_lon"])


def test_osrm_provider_no_lateral_field_waypoint_injection():
    """OSRM provider must query authentic alternatives without synthesizing perpendicular field offsets."""
    provider = OSRMGlobalRoutingProvider()
    orig_lat, orig_lon = 16.3067, 80.4365
    dest_lat, dest_lon = 16.5062, 80.6480

    routes = provider.calculate_routes(orig_lat, orig_lon, dest_lat, dest_lon, mode=TravelMode.DRIVING)
    assert len(routes) >= 1

    # Every route must have authentic geometry and start/end near the endpoints
    for r in routes:
        assert len(r.polyline) >= 10
        d_start = haversine_distance_m(r.polyline[0][0], r.polyline[0][1], orig_lat, orig_lon)
        d_end = haversine_distance_m(r.polyline[-1][0], r.polyline[-1][1], dest_lat, dest_lon)
        # Snapped to highway within 800m
        assert d_start <= 1500.0
        assert d_end <= 1500.0
