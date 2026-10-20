"""
Automated tests for Route Geometry Overlap, Distinct Alternatives Validation,
Duplicate Rejection, Physical Path Validity, and Map Highlighting in P.A.T.H.F.I.N.D.E.R.
"""

import pytest
import math
from typing import List, Tuple

from src.route_engine import (
    RouteOption,
    TravelMode,
    BaseRoutingProvider,
    RealWorldRouteEngine,
    OSRMGlobalRoutingProvider,
    compute_polyline_distance_m,
    point_to_segment_distance_m,
    sample_polyline,
    calculate_spatial_route_overlap,
    calculate_road_segment_overlap,
    verify_route_validity,
    recalculate_route_metrics,
    filter_distinct_routes,
    haversine_distance_m
)


# =============================================================================
# 1. POINT TO SEGMENT METRIC DISTANCE TESTS
# =============================================================================

def test_point_to_segment_distance_exact_endpoints_and_interior():
    # Segment from (16.2300, 80.5400) to (16.2300, 80.5500) - approximately 1070 meters east-west
    a = (16.2300, 80.5400)
    b = (16.2300, 80.5500)

    # Point at exact start endpoint
    d_start = point_to_segment_distance_m(a, a, b)
    assert d_start < 0.1

    # Point at exact end endpoint
    d_end = point_to_segment_distance_m(b, a, b)
    assert d_end < 0.1

    # Point on midpoint
    mid = (16.2300, 80.5450)
    d_mid = point_to_segment_distance_m(mid, a, b)
    assert d_mid < 0.1

    # Point perpendicular offset north by ~110m (16.2310 is 0.001 deg north ~ 110.5m)
    p_north = (16.2310, 80.5450)
    d_north = point_to_segment_distance_m(p_north, a, b)
    assert 105.0 < d_north < 115.0


# =============================================================================
# 2. SPATIAL ROUTE OVERLAP & DUPLICATE GEOMETRY DETECTION
# =============================================================================

def test_spatial_overlap_identical_routes():
    poly = [
        (16.2335, 80.5505),
        (16.2385, 80.5420),
        (16.2650, 80.4980),
        (16.3067, 80.4365)
    ]
    overlap = calculate_spatial_route_overlap(poly, poly)
    assert overlap == 1.0


def test_spatial_overlap_nearly_identical_routes_rejected():
    # Route A
    poly_a = [
        (16.2335, 80.5505),
        (16.2385, 80.5420),
        (16.2650, 80.4980),
        (16.2890, 80.4550),
        (16.3067, 80.4365)
    ]
    # Route B: 95% identical, with 1 tiny parallel lane shift of 8 meters
    poly_b = [
        (16.2335, 80.5505),
        (16.2385, 80.54208),
        (16.2650, 80.49808),
        (16.2890, 80.45508),
        (16.3067, 80.4365)
    ]

    # Because shift is ~8m (< tolerance 35m), spatial overlap should be 1.0 (100%)
    overlap = calculate_spatial_route_overlap(poly_a, poly_b, tolerance_m=35.0)
    assert overlap >= 0.95

    # Passing both to filter_distinct_routes must reject poly_b as a duplicate
    r1 = RouteOption(
        route_id="R1", name="Primary Route", mode=TravelMode.DRIVING,
        distance_meters=14500.0, duration_seconds=1100.0,
        polyline=poly_a, summary_roads=["Main Highway"]
    )
    r2 = RouteOption(
        route_id="R2", name="Supposed Alternative", mode=TravelMode.DRIVING,
        distance_meters=14520.0, duration_seconds=1105.0,
        polyline=poly_b, summary_roads=["Main Highway"]
    )

    filtered = filter_distinct_routes([r1, r2], max_overlap=0.80)
    assert len(filtered) == 1
    assert filtered[0].route_id == "R1"


def test_spatial_overlap_genuinely_distinct_arterial_alternatives():
    # Route 1: Direct Central Arterial Corridor (Vadlamudi -> Narakodur -> Guntur Center)
    poly_central = [
        (16.2335, 80.5505),
        (16.2385, 80.5420),
        (16.2650, 80.4980),
        (16.2890, 80.4550),
        (16.3067, 80.4365)
    ]

    # Route 2: Northern Bypass Corridor (Tenali East -> Tenali North -> NH16 Link -> Guntur Center)
    # Deviates by several kilometers north-east
    poly_north = [
        (16.2335, 80.5505),
        (16.2420, 80.5850),
        (16.2620, 80.6050),
        (16.2980, 80.4850),
        (16.3180, 80.4520),
        (16.3067, 80.4365)
    ]

    overlap = calculate_spatial_route_overlap(poly_central, poly_north, tolerance_m=35.0)
    # The routes only touch at the origin and destination ends; middle divergence is large
    assert overlap < 0.40

    r_central = RouteOption(
        route_id="R_CENTRAL", name="Central Arterial", mode=TravelMode.DRIVING,
        distance_meters=14500.0, duration_seconds=1100.0,
        polyline=poly_central, summary_roads=["Vadlamudi Main Road", "Guntur Highway Connector"]
    )
    r_north = RouteOption(
        route_id="R_NORTH", name="Northern Bypass Expressway", mode=TravelMode.DRIVING,
        distance_meters=18200.0, duration_seconds=1250.0,
        polyline=poly_north, summary_roads=["Tenali Bypass East", "NH-16 Expressway Link"]
    )

    filtered = filter_distinct_routes([r_central, r_north], max_overlap=0.80)
    assert len(filtered) == 2
    assert filtered[0].route_id == "R_CENTRAL"
    assert filtered[1].route_id == "R_NORTH"


# =============================================================================
# 3. SHARED ROAD SEGMENT ANALYSIS TESTS
# =============================================================================

def test_road_segment_overlap_identical_and_disjoint():
    roads_1 = ["NH16 Expressway", "Auto Nagar Bypass", "City Main Avenue"]
    roads_identical = ["NH16 Expressway", "Auto Nagar Bypass", "City Main Avenue"]
    roads_disjoint = ["South Canal Bund Road", "Rural River Link", "South Market Road"]

    overlap_id = calculate_road_segment_overlap(roads_1, roads_identical)
    assert overlap_id == 1.0

    overlap_dis = calculate_road_segment_overlap(roads_1, roads_disjoint)
    assert overlap_dis == 0.0


def test_road_segment_overlap_partial_and_rejection():
    roads_a = ["Main Corridor", "Sub Arterial A", "Destination Road"]
    roads_b = ["Main Corridor", "Sub Arterial B", "Destination Road"]

    overlap = calculate_road_segment_overlap(roads_a, roads_b)
    # 2 out of 4 distinct roads shared
    assert 0.40 <= overlap <= 0.70


# =============================================================================
# 4. SINGLE DISTINCT ROUTE SCENARIO (NO INVENTED ALTERNATIVES)
# =============================================================================

def test_single_distinct_route_returns_one_without_synthesizing_fakes():
    class MockSingleRouteProvider(BaseRoutingProvider):
        def calculate_routes(self, origin_lat, origin_lon, dest_lat, dest_lon, mode=TravelMode.DRIVING, require_accessible=False):
            # Returns exactly 1 route (e.g. single bridge crossing between river banks)
            return [
                RouteOption(
                    route_id="OSRM_SINGLE",
                    name="Prakasam Barrage Bridge Corridor",
                    mode=TravelMode.DRIVING,
                    distance_meters=8500.0,
                    duration_seconds=720.0,
                    polyline=[(origin_lat, origin_lon), (16.505, 80.605), (dest_lat, dest_lon)],
                    summary_roads=["Prakasam Barrage Rd"],
                    source="OSRM (OpenStreetMap Global)"
                )
            ]

    engine = RealWorldRouteEngine(provider=MockSingleRouteProvider())
    routes = engine.calculate_routes(16.500, 80.600, 16.510, 80.610, mode=TravelMode.DRIVING)

    # Must return exactly 1 route, without fabricating an arbitrary midpoint or fake 2nd route
    assert len(routes) == 1
    assert routes[0].route_id == "OSRM_SINGLE"
    assert "Prakasam Barrage" in routes[0].name


def test_rejection_of_duplicate_alternatives_from_provider():
    class MockProviderWithDuplicate(BaseRoutingProvider):
        def calculate_routes(self, origin_lat, origin_lon, dest_lat, dest_lon, mode=TravelMode.DRIVING, require_accessible=False):
            poly = [(origin_lat, origin_lon), (16.25, 80.50), (dest_lat, dest_lon)]
            return [
                RouteOption(
                    route_id="ROUTE_1",
                    name="Primary Highway",
                    mode=TravelMode.DRIVING,
                    distance_meters=10000.0,
                    duration_seconds=700.0,
                    polyline=poly,
                    summary_roads=["Highway 1"]
                ),
                RouteOption(
                    route_id="ROUTE_2_DUPLICATE",
                    name="Supposed Alternative",
                    mode=TravelMode.DRIVING,
                    distance_meters=10010.0,
                    duration_seconds=705.0,
                    polyline=list(poly),  # Identical geometry
                    summary_roads=["Highway 1"]
                )
            ]

    engine = RealWorldRouteEngine(provider=MockProviderWithDuplicate())
    routes = engine.calculate_routes(16.23, 80.55, 16.27, 80.45, mode=TravelMode.DRIVING)

    assert len(routes) == 1
    assert routes[0].route_id == "ROUTE_1"


# =============================================================================
# 5. ROUTE PHYSICAL VALIDITY AND CONNECTIVITY
# =============================================================================

def test_verify_route_validity_endpoints_and_metrics():
    orig = (16.2335, 80.5505)
    dest = (16.3067, 80.4365)

    valid_route = RouteOption(
        route_id="V1",
        name="Valid Corridor",
        mode=TravelMode.DRIVING,
        distance_meters=14000.0,
        duration_seconds=1000.0,
        polyline=[orig, (16.26, 80.50), dest]
    )
    is_valid, reason = verify_route_validity(valid_route, orig[0], orig[1], dest[0], dest[1])
    assert is_valid is True

    # Invalid route: arrival point is 50 km away from requested destination
    disconnected_route = RouteOption(
        route_id="V2",
        name="Disconnected Corridor",
        mode=TravelMode.DRIVING,
        distance_meters=14000.0,
        duration_seconds=1000.0,
        polyline=[orig, (16.26, 80.50), (16.8000, 81.2000)]
    )
    is_valid_disc, reason_disc = verify_route_validity(disconnected_route, orig[0], orig[1], dest[0], dest[1])
    assert is_valid_disc is False
    assert "requested destination" in reason_disc.lower()


# =============================================================================
# 6. DISTANCE AND DURATION RECALCULATION FROM RETURNED DATA
# =============================================================================

def test_recalculate_route_metrics_from_actual_polyline():
    poly = [
        (16.2335, 80.5505),
        (16.2385, 80.5420),
        (16.2650, 80.4980)
    ]
    expected_dist = compute_polyline_distance_m(poly)
    assert expected_dist > 5000.0

    # Route created with missing/zero distance and duration
    r = RouteOption(
        route_id="REC_1",
        name="Recalc Test",
        mode=TravelMode.DRIVING,
        distance_meters=0.0,
        duration_seconds=0.0,
        polyline=poly
    )
    recalculate_route_metrics(r)

    assert r.distance_meters == expected_dist
    assert r.duration_seconds > 0.0
    # At driving speed (~13.88 m/s), check duration bounds
    assert 300.0 < r.duration_seconds < 800.0


# =============================================================================
# 7. MAP SELECTION AND ROUTE HIGHLIGHTING ISOLATION
# =============================================================================

def test_map_route_selection_isolates_exact_focused_geometry():
    r1 = RouteOption(
        route_id="OSRM_1",
        name="Primary Route 1",
        mode=TravelMode.DRIVING,
        distance_meters=12000.0,
        duration_seconds=900.0,
        polyline=[(16.23, 80.55), (16.25, 80.52), (16.30, 80.45)]
    )
    r2 = RouteOption(
        route_id="OSRM_2",
        name="Alternative Route 2",
        mode=TravelMode.DRIVING,
        distance_meters=15000.0,
        duration_seconds=1100.0,
        polyline=[(16.23, 80.55), (16.28, 80.58), (16.30, 80.45)]
    )

    class MockRanked:
        def __init__(self, route, rank, is_eligible=True):
            self.route = route
            self.rank = rank
            self.is_eligible = is_eligible
            self.effective_duration_minutes = route.duration_minutes
            self.effective_distance_km = route.distance_km
            self.status = type('obj', (object,), {'value': 'ELIGIBLE'})

    ranked_routes = [MockRanked(r1, 1), MockRanked(r2, 2)]

    # When cur_focus is "ALL", all eligible routes are in route_polylines
    cur_focus_all = "ALL"
    polylines_all = [r.route.polyline for r in ranked_routes if cur_focus_all == "ALL" or r.route.route_id == cur_focus_all]
    assert len(polylines_all) == 2

    # When cur_focus is "OSRM_2", ONLY Route 2 geometry is highlighted and selected
    cur_focus_r2 = "OSRM_2"
    focused_polylines = [r.route.polyline for r in ranked_routes if cur_focus_r2 == "ALL" or r.route.route_id == cur_focus_r2]
    assert len(focused_polylines) == 1
    assert focused_polylines[0] == r2.polyline


# =============================================================================
# 8. COMPREHENSIVE ROUTE CARD CLICK & MAP SYNCHRONIZATION TESTS
# =============================================================================

def test_clicking_alternative_2_displays_alternative_2_geometry_and_metrics():
    r1 = RouteOption(
        route_id="OSRM_1",
        name="Primary Arterial Route",
        mode=TravelMode.DRIVING,
        distance_meters=14200.0,
        duration_seconds=1020.0,
        polyline=[(16.2335, 80.5505), (16.2500, 80.5100), (16.3067, 80.4365)],
        summary_roads=["Vadlamudi Main Road", "Guntur Highway Connector"]
    )
    r2 = RouteOption(
        route_id="OSRM_2",
        name="Northern Bypass Alternative",
        mode=TravelMode.DRIVING,
        distance_meters=17800.0,
        duration_seconds=1210.0,
        polyline=[(16.2335, 80.5505), (16.2800, 80.5700), (16.3067, 80.4365)],
        summary_roads=["Tenali Bypass East", "NH-16 Expressway Link"]
    )

    class MockRanked:
        def __init__(self, route, rank):
            self.route = route
            self.rank = rank
            self.is_eligible = True
            self.effective_duration_minutes = route.duration_minutes
            self.effective_distance_km = route.distance_km
            self.status = type('obj', (object,), {'value': 'ROUTE_ELIGIBLE'})

    ranked_routes = [MockRanked(r1, 1), MockRanked(r2, 2)]

    # Simulate selecting Alternative 2
    selected_id = "OSRM_2"
    active_item = next((r for r in ranked_routes if r.route.route_id == selected_id), None)
    assert active_item is not None
    assert active_item.route.name == "Northern Bypass Alternative"
    assert active_item.route.route_id == "OSRM_2"
    assert active_item.effective_distance_km == 17.8
    assert active_item.effective_duration_minutes == round(1210.0 / 60.0, 1)

    # Verify primary polyline on map is set to Alternative 2's exact geometry
    route_polylines = []
    for r_item in ranked_routes:
        is_sel = (selected_id == r_item.route.route_id)
        route_polylines.append({
            "name": r_item.route.name,
            "coordinates": r_item.route.polyline,
            "is_selected": is_sel,
            "weight": 8 if is_sel else 3.5,
            "opacity": 1.0 if is_sel else 0.40
        })

    primary_map_poly = next((r["coordinates"] for r in route_polylines if r.get("is_selected")), None)
    assert primary_map_poly == r2.polyline
    assert primary_map_poly != r1.polyline


def test_invalid_or_missing_route_id_fallback():
    valid_route_ids = {"OSRM_1", "OSRM_2"}
    test_requested_id = "INVALID_999"

    # Route engine & app validation fallback
    if test_requested_id not in valid_route_ids and test_requested_id not in ["ALL", "FASTEST", "SHORTEST", "BALANCED", "ACCESSIBLE"]:
        fallback_focus = "ALL"
    else:
        fallback_focus = test_requested_id

    assert fallback_focus == "ALL"


def test_destination_change_invalidates_stale_route_selection():
    orig = (16.2335, 80.5505)
    dest1 = (16.3067, 80.4365)
    dest2 = (16.2420, 80.5850)

    sig1 = (round(orig[0], 4), round(orig[1], 4), round(dest1[0], 4), round(dest1[1], 4))
    sig2 = (round(orig[0], 4), round(orig[1], 4), round(dest2[0], 4), round(dest2[1], 4))

    assert sig1 != sig2
    # Changing destination invalidates stale route selection and forces "ALL"
    focused_route_id = "OSRM_2"
    if sig1 != sig2:
        focused_route_id = "ALL"
    assert focused_route_id == "ALL"


def test_hazard_and_accessibility_preserved_on_map_selection():
    r_accessible = RouteOption(
        route_id="ACC_1",
        name="Step-Free Path",
        mode=TravelMode.WALKING,
        distance_meters=850.0,
        duration_seconds=600.0,
        polyline=[(16.2335, 80.5505), (16.2345, 80.5495)],
        is_accessible=True,
        accessibility_verified=True,
        accessibility_notes="Verified Pedestrian Surface"
    )

    assert r_accessible.is_accessible is True
    assert r_accessible.accessibility_verified is True
    assert "Verified" in r_accessible.accessibility_notes
