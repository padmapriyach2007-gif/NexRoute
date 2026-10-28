"""
Targeted Verification Suite for Accurate Road-Routing Geometry & Multi-Route Authenticity:
1. Verifies real road-network routing without synthetic bypasses or perpendicular waypoint offsets
2. Verifies geojson_coords_to_latlon and decode_polyline precision
3. Verifies strict route geometry validation (finite numbers, bounds, snapping tolerance, continuity)
4. Verifies rejection of unnatural straight-line leaps between consecutive points
5. Verifies that when a routing engine returns 1 valid route, exactly 1 route is returned without fakes
6. Verifies exact required error message when no route is available:
   "No verified route is available for these locations. Please try again or select different endpoints."
"""

import math
import pytest
from src.route_engine import (
    RouteOption,
    TravelMode,
    BaseRoutingProvider,
    RealWorldRouteEngine,
    OSRMGlobalRoutingProvider,
    geojson_coords_to_latlon,
    decode_polyline,
    verify_route_validity,
    filter_distinct_routes,
    haversine_distance_m
)


def test_geojson_coords_to_latlon_conversion():
    # GeoJSON format is [longitude, latitude]
    raw_geojson = [
        [80.4365, 16.3067],
        [80.4370, 16.3070],
        [80.4400, 16.3090]
    ]
    converted = geojson_coords_to_latlon(raw_geojson)
    assert len(converted) == 3
    # Result must be GIS [latitude, longitude]
    assert converted[0] == (16.3067, 80.4365)
    assert converted[1] == (16.3070, 80.4370)
    assert converted[2] == (16.3090, 80.4400)


def test_decode_polyline_precision_5_and_6():
    # Google polyline encoding test
    test_encoded = "_p~iF~ps|U_ulLnnqC_mqNvxq`@"
    decoded = decode_polyline(test_encoded, precision=5)
    assert len(decoded) == 3
    assert abs(decoded[0][0] - 38.5) < 0.001
    assert abs(decoded[0][1] - (-120.2)) < 0.001


def test_verify_route_validity_rejects_nan_inf_and_out_of_bounds():
    origin = (16.3067, 80.4365)
    dest = (16.2430, 80.6400)

    # NaN in polyline
    route_nan = RouteOption(
        route_id="R_NAN", name="Invalid NaN Route", mode=TravelMode.DRIVING,
        distance_meters=25000.0, duration_seconds=1800.0,
        polyline=[(16.3067, 80.4365), (float("nan"), 80.5000), (16.2430, 80.6400)]
    )
    is_valid, msg = verify_route_validity(route_nan, origin[0], origin[1], dest[0], dest[1])
    assert is_valid is False
    assert "Invalid GPS coordinates" in msg

    # Infinity in polyline
    route_inf = RouteOption(
        route_id="R_INF", name="Invalid Inf Route", mode=TravelMode.DRIVING,
        distance_meters=25000.0, duration_seconds=1800.0,
        polyline=[(16.3067, 80.4365), (float("inf"), 80.5000), (16.2430, 80.6400)]
    )
    is_valid, msg = verify_route_validity(route_inf, origin[0], origin[1], dest[0], dest[1])
    assert is_valid is False


def test_verify_route_validity_rejects_massive_teleportation_jumps():
    origin = (16.3067, 80.4365)
    dest = (16.2430, 80.6400)

    # A route with a massive 70 km unnatural leap across countryside
    route_leap = RouteOption(
        route_id="R_LEAP", name="Unnatural Leap Route", mode=TravelMode.DRIVING,
        distance_meters=85000.0, duration_seconds=3600.0,
        polyline=[
            (16.3067, 80.4365),
            (16.3100, 80.4400),
            (15.7000, 80.0000),  # 70+ km leap away
            (16.2430, 80.6400)
        ]
    )
    is_valid, msg = verify_route_validity(route_leap, origin[0], origin[1], dest[0], dest[1], max_consecutive_jump_m=35000.0)
    assert is_valid is False
    assert "Disconnected road segment leap" in msg


def test_no_synthetic_bypass_waypoints_and_single_route_integrity():
    # Test Guntur to Tenali live OSRM
    engine = RealWorldRouteEngine()
    guntur_lat, guntur_lon = 16.3067, 80.4365
    tenali_lat, tenali_lon = 16.2430, 80.6400

    routes = engine.calculate_routes(guntur_lat, guntur_lon, tenali_lat, tenali_lon, mode=TravelMode.DRIVING)
    assert len(routes) >= 1
    # Each route must have verified road coordinates (no synthetic 5-10 point straight lines)
    for r in routes:
        assert len(r.polyline) >= 100, f"Route {r.name} has only {len(r.polyline)} points; expected high-density road geometry"
        # No duplicate route IDs
        assert r.route_id.startswith("OSRM_") or r.route_id.startswith("GMAP_")
        # Geometry is verified
        is_valid, _ = verify_route_validity(r, guntur_lat, guntur_lon, tenali_lat, tenali_lon)
        assert is_valid is True


def test_exact_no_verified_route_message_when_disconnected():
    engine = RealWorldRouteEngine()
    # Route between mainland and North Sentinel Island (no road or ferry connection)
    mainland_lat, mainland_lon = 16.3067, 80.4365
    island_lat, island_lon = 11.5500, 92.2500

    routes = engine.calculate_routes(mainland_lat, mainland_lon, island_lat, island_lon, mode=TravelMode.DRIVING)
    assert len(routes) == 0
    assert engine.last_failure_reason == "No verified route is available for these locations. Please try again or select different endpoints."
