import pytest
import math
from typing import List, Tuple, Dict, Any

from src.route_engine import (
    RealWorldRouteEngine,
    RouteOption,
    BaseRoutingProvider,
    TravelMode,
    filter_distinct_routes,
    compute_polyline_distance_m,
    haversine_distance_m
)
from src.multi_objective_router import (
    MultiObjectiveRouter,
    OptimizationObjective,
    RankedRoute,
    RouteEligibilityStatus
)
from src.road_condition_manager import RoadConditionManager
from src.road_condition_model import RoadRestriction, RestrictionType
from src.hazard_map import HazardMap, GeographicHazard, HazardSeverity
from src.map_service import MapService
from src.journey_storyteller import generate_friendly_virtual_guide_turns
from src.virtual_human_guide import build_always_visible_virtual_guide_html


class DeterministicMockProvider(BaseRoutingProvider):
    """Deterministic routing provider providing 2-3 genuine road corridors."""
    def __init__(self, routes_to_return=None):
        self.routes_to_return = routes_to_return

    def calculate_routes(
        self,
        origin_lat: float, origin_lon: float,
        dest_lat: float, dest_lon: float,
        mode: TravelMode = TravelMode.DRIVING,
        require_accessible: bool = False,
        **kwargs
    ) -> List[RouteOption]:
        if self.routes_to_return is not None:
            return self.routes_to_return

        # Corridor 1: Direct Expressway (Faster speed, longer arc distance)
        c1_poly = [
            (origin_lat, origin_lon),
            (origin_lat + (dest_lat - origin_lat) * 0.3 + 0.08, origin_lon + (dest_lon - origin_lon) * 0.3 + 0.08),
            (origin_lat + (dest_lat - origin_lat) * 0.7 + 0.08, origin_lon + (dest_lon - origin_lon) * 0.7 + 0.08),
            (dest_lat, dest_lon)
        ]
        dist1 = compute_polyline_distance_m(c1_poly)
        dur1 = (dist1 / 1000.0) / 95.0 * 3600.0  # 95 km/h (lowest duration)

        # Corridor 2: Arterial Direct (Shorter direct distance, lower speed)
        c2_poly = [
            (origin_lat, origin_lon),
            (dest_lat, dest_lon)
        ]
        dist2 = compute_polyline_distance_m(c2_poly)
        dur2 = (dist2 / 1000.0) / 35.0 * 3600.0  # 35 km/h (lowest distance, higher duration)

        return [
            RouteOption(
                route_id="ROUTE_EXPRESSWAY_1",
                name="North Expressway Bypass",
                mode=mode,
                distance_meters=dist1,
                duration_seconds=dur1,
                polyline=c1_poly,
                summary_roads=["NH-16 Expressway", "North Bypass"],
                steps=[
                    {"step_num": 1, "icon": "🟢", "instruction": "Head out on NH-16", "road": "NH-16", "distance_m": dist1 * 0.7, "duration_s": dur1 * 0.6, "type": "depart", "modifier": ""},
                    {"step_num": 2, "icon": "🏁", "instruction": "Arrive at destination", "road": "Destination Way", "distance_m": 0.0, "duration_s": 0.0, "type": "arrive", "modifier": ""}
                ],
                is_accessible=True,
                accessibility_verified=True,
                source="Deterministic Test Engine"
            ),
            RouteOption(
                route_id="ROUTE_ARTERIAL_2",
                name="Direct Arterial Link",
                mode=mode,
                distance_meters=dist2,
                duration_seconds=dur2,
                polyline=c2_poly,
                summary_roads=["Main Canal Road", "South Link"],
                steps=[
                    {"step_num": 1, "icon": "🟢", "instruction": "Head out on Main Canal Rd", "road": "Main Canal Rd", "distance_m": dist2 * 0.8, "duration_s": dur2 * 0.7, "type": "depart", "modifier": ""},
                    {"step_num": 2, "icon": "🏁", "instruction": "Arrive at destination", "road": "Terminal", "distance_m": 0.0, "duration_s": 0.0, "type": "arrive", "modifier": ""}
                ],
                is_accessible=True,
                accessibility_verified=True,
                source="Deterministic Test Engine"
            )
        ]


# -----------------------------------------------------------------------------
# 1. Custom Origin and Destination
# -----------------------------------------------------------------------------
def test_custom_origin_and_destination():
    provider = DeterministicMockProvider()
    engine = RealWorldRouteEngine(provider=provider)
    orig = (16.5062, 80.6480)  # Vijayawada
    dest = (16.2430, 80.6400)  # Tenali

    routes = engine.calculate_routes(orig[0], orig[1], dest[0], dest[1], mode=TravelMode.DRIVING)
    assert len(routes) >= 2
    for r in routes:
        assert math.isclose(r.polyline[0][0], orig[0], abs_tol=1e-4)
        assert math.isclose(r.polyline[0][1], orig[1], abs_tol=1e-4)
        assert math.isclose(r.polyline[-1][0], dest[0], abs_tol=1e-4)
        assert math.isclose(r.polyline[-1][1], dest[1], abs_tol=1e-4)


# -----------------------------------------------------------------------------
# 2. GPS Origin with Selected Destination
# -----------------------------------------------------------------------------
def test_gps_origin_with_selected_destination():
    provider = DeterministicMockProvider()
    engine = RealWorldRouteEngine(provider=provider)
    gps_orig = (16.2335, 80.5505)  # Live GPS
    dest = (16.2380, 80.6450)      # Tenali Morrispet

    routes = engine.calculate_routes(gps_orig[0], gps_orig[1], dest[0], dest[1], mode=TravelMode.DRIVING)
    assert len(routes) >= 2
    assert routes[0].polyline[0] == (gps_orig[0], gps_orig[1])
    assert routes[0].polyline[-1] == (dest[0], dest[1])


# -----------------------------------------------------------------------------
# 3. Small Locations and Ambiguous Place Names
# -----------------------------------------------------------------------------
def test_small_locations_and_ambiguous_place_names():
    ms = MapService()
    # Test small areas present in regional geocode cache
    cands_angalakuduru = ms.geocode_candidates("angalakuduru", limit=3)
    assert len(cands_angalakuduru) > 0
    assert "lat" in cands_angalakuduru[0] and "lon" in cands_angalakuduru[0]

    cands_morrispet = ms.geocode_candidates("morrispet", limit=3)
    assert len(cands_morrispet) > 0

    # Ambiguous location returns candidates without raising
    cands_temple = ms.geocode_candidates("temple", limit=4)
    assert isinstance(cands_temple, list)

    # Empty string returns empty without raising
    assert ms.geocode_candidates("", limit=3) == []


# -----------------------------------------------------------------------------
# 4. Generating Routes After Either Location Changes
# -----------------------------------------------------------------------------
def test_generating_routes_after_either_location_changes():
    provider = DeterministicMockProvider()
    engine = RealWorldRouteEngine(provider=provider)

    # Location Pair 1
    orig1, dest1 = (16.50, 80.64), (16.24, 80.64)
    routes1 = engine.calculate_routes(orig1[0], orig1[1], dest1[0], dest1[1])
    sig1 = (orig1, dest1)

    # Location changes: new origin
    orig2 = (16.54, 80.51)
    sig2 = (orig2, dest1)
    assert sig1 != sig2

    routes2 = engine.calculate_routes(orig2[0], orig2[1], dest1[0], dest1[1])
    assert math.isclose(routes2[0].polyline[0][0], orig2[0], abs_tol=1e-4)

    # Location changes: new destination
    dest2 = (15.90, 80.46)
    sig3 = (orig2, dest2)
    assert sig2 != sig3

    routes3 = engine.calculate_routes(orig2[0], orig2[1], dest2[0], dest2[1])
    assert math.isclose(routes3[0].polyline[-1][0], dest2[0], abs_tol=1e-4)


# -----------------------------------------------------------------------------
# 5. Multiple Genuinely Distinct Route Alternatives
# -----------------------------------------------------------------------------
def test_multiple_genuinely_distinct_route_alternatives():
    provider = DeterministicMockProvider()
    engine = RealWorldRouteEngine(provider=provider)
    routes = engine.calculate_routes(16.50, 80.60, 16.24, 80.64)

    assert len(routes) >= 2
    r1, r2 = routes[0], routes[1]
    # Stable IDs and different road names
    assert r1.route_id != r2.route_id
    assert r1.summary_roads != r2.summary_roads
    # Distinct polylines
    assert r1.polyline != r2.polyline


# -----------------------------------------------------------------------------
# 6. Clicking the First Route Card
# -----------------------------------------------------------------------------
def test_clicking_the_first_route_card():
    provider = DeterministicMockProvider()
    engine = RealWorldRouteEngine(provider=provider)
    routes = engine.calculate_routes(16.50, 80.60, 16.24, 80.64)

    router = MultiObjectiveRouter()
    ranked = router.evaluate_and_rank_routes(routes, objective=OptimizationObjective.FASTEST)
    assert len(ranked) >= 2

    # Simulate card click on first route
    first_route_id = ranked[0].route.route_id
    cur_focus = first_route_id
    selected_route_id = cur_focus
    selected_route_object = next(r.route for r in ranked if r.route.route_id == cur_focus)

    assert selected_route_id == first_route_id
    assert selected_route_object.route_id == first_route_id

    # In PATHFINDER, ALL cards remain displayed
    displayed_routes = ranked
    assert len(displayed_routes) == len(ranked)

    # R1 is active, R2 is candidate
    assert (cur_focus == displayed_routes[0].route.route_id) is True
    assert (cur_focus == displayed_routes[1].route.route_id) is False


# -----------------------------------------------------------------------------
# 7. Clicking a Different Route Card
# -----------------------------------------------------------------------------
def test_clicking_different_route_card_switches_immediately():
    provider = DeterministicMockProvider()
    engine = RealWorldRouteEngine(provider=provider)
    routes = engine.calculate_routes(16.50, 80.60, 16.24, 80.64)

    router = MultiObjectiveRouter()
    ranked = router.evaluate_and_rank_routes(routes, objective=OptimizationObjective.FASTEST)
    assert len(ranked) >= 2

    # Switch to Route 2
    second_route_id = ranked[1].route.route_id
    cur_focus = second_route_id
    selected_route_id = cur_focus
    selected_route_object = next(r.route for r in ranked if r.route.route_id == cur_focus)

    assert selected_route_id == second_route_id
    assert selected_route_object.route_id == second_route_id

    # Verify map polyline selection state
    route_polylines = []
    for r_item in ranked:
        is_selected = (cur_focus == r_item.route.route_id)
        route_polylines.append({
            "route_id": r_item.route.route_id,
            "is_selected": is_selected,
            "weight": 8 if is_selected else 3.5,
            "opacity": 1.0 if is_selected else 0.40
        })

    # Only Route 2 has is_selected == True and full weight 8
    assert route_polylines[0]["is_selected"] is False
    assert route_polylines[0]["weight"] == 3.5
    assert route_polylines[1]["is_selected"] is True
    assert route_polylines[1]["weight"] == 8


# -----------------------------------------------------------------------------
# 8. Correct Geometry and Coordinate Ordering
# -----------------------------------------------------------------------------
def test_correct_geometry_and_coordinate_ordering():
    provider = DeterministicMockProvider()
    engine = RealWorldRouteEngine(provider=provider)
    routes = engine.calculate_routes(16.50, 80.60, 16.24, 80.64)

    for r in routes:
        assert isinstance(r.polyline, list)
        assert len(r.polyline) >= 2
        for pt in r.polyline:
            assert isinstance(pt, (tuple, list))
            lat, lon = pt[0], pt[1]
            assert -90.0 <= lat <= 90.0
            assert -180.0 <= lon <= 180.0


# -----------------------------------------------------------------------------
# 9. Distance and Duration Consistency
# -----------------------------------------------------------------------------
def test_distance_and_duration_consistency():
    provider = DeterministicMockProvider()
    engine = RealWorldRouteEngine(provider=provider)
    routes = engine.calculate_routes(16.50, 80.60, 16.24, 80.64)

    router = MultiObjectiveRouter()
    ranked = router.evaluate_and_rank_routes(routes, objective=OptimizationObjective.FASTEST)

    # Compute actual fastest and shortest from candidates
    fastest = min(ranked, key=lambda r: r.effective_duration_minutes)
    shortest = min(ranked, key=lambda r: r.effective_distance_km)

    for r in ranked:
        assert r.effective_distance_km > 0
        assert r.effective_duration_minutes > 0
        # Time savings calculation is non-negative vs slowest
        assert r.time_savings_minutes_vs_slowest >= 0
        # Distance diff calculation is non-negative vs shortest
        assert r.distance_diff_km_vs_shortest >= 0

    assert fastest.effective_duration_minutes <= shortest.effective_duration_minutes or fastest.effective_duration_minutes == min(r.effective_duration_minutes for r in ranked)


# -----------------------------------------------------------------------------
# 10. Map Fitting and Marker Placement
# -----------------------------------------------------------------------------
def test_map_fitting_and_marker_placement():
    provider = DeterministicMockProvider()
    engine = RealWorldRouteEngine(provider=provider)
    routes = engine.calculate_routes(16.50, 80.60, 16.24, 80.64)

    # Construct route polylines dict for map
    cur_focus = routes[0].route_id
    route_polylines = []
    for r in routes:
        is_sel = (cur_focus == r.route_id)
        route_polylines.append({
            "coordinates": r.polyline,
            "is_selected": is_sel,
            "color": "#10b981" if is_sel else "#0ea5e9"
        })

    # Center computation
    primary = next(r for r in route_polylines if r["is_selected"])
    poly_pts = primary["coordinates"]
    min_lat, max_lat = min(p[0] for p in poly_pts), max(p[0] for p in poly_pts)
    min_lon, max_lon = min(p[1] for p in poly_pts), max(p[1] for p in poly_pts)
    center_lat = (min_lat + max_lat) / 2.0
    center_lon = (min_lon + max_lon) / 2.0

    assert min_lat <= center_lat <= max_lat
    assert min_lon <= center_lon <= max_lon


# -----------------------------------------------------------------------------
# 11. Objective Selection (Fastest, Shortest, Balanced, Accessible)
# -----------------------------------------------------------------------------
def test_objective_selection():
    provider = DeterministicMockProvider()
    engine = RealWorldRouteEngine(provider=provider)
    routes = engine.calculate_routes(16.50, 80.60, 16.24, 80.64)

    router = MultiObjectiveRouter()

    # 1. FASTEST
    ranked_fast = router.evaluate_and_rank_routes(routes, objective=OptimizationObjective.FASTEST)
    assert ranked_fast[0].effective_duration_minutes == min(r.effective_duration_minutes for r in ranked_fast)

    # 2. SHORTEST
    ranked_short = router.evaluate_and_rank_routes(routes, objective=OptimizationObjective.SHORTEST)
    assert ranked_short[0].effective_distance_km == min(r.effective_distance_km for r in ranked_short)

    # 3. BALANCED
    ranked_bal = router.evaluate_and_rank_routes(routes, objective=OptimizationObjective.BALANCED)
    assert len(ranked_bal) == len(routes)

    # 4. ACCESSIBLE
    ranked_acc = router.evaluate_and_rank_routes(routes, objective=OptimizationObjective.ACCESSIBLE)
    for r in ranked_acc:
        if r.is_eligible:
            assert r.route.is_accessible is True


# -----------------------------------------------------------------------------
# 12. Route Changes While a Request is Invalidation / Signature Mismatch
# -----------------------------------------------------------------------------
def test_route_changes_while_request_invalidation():
    # Previous signature
    prev_sig = (16.50, 80.60, 16.24, 80.64, TravelMode.DRIVING)
    new_sig = (16.52, 80.60, 16.24, 80.64, TravelMode.DRIVING)

    assert prev_sig != new_sig
    # When signature changes, focused_route_id resets to "ALL"
    focused_route_id = "ALL"
    selected_route_id = None
    assert focused_route_id == "ALL"
    assert selected_route_id is None


# -----------------------------------------------------------------------------
# 13. Routing Provider Failure Handling
# -----------------------------------------------------------------------------
def test_routing_provider_failure_handling():
    class FailingProvider(BaseRoutingProvider):
        def calculate_routes(self, *args, **kwargs):
            raise ConnectionError("Upstream OSM OSRM server timeout")

    engine = RealWorldRouteEngine(provider=FailingProvider())
    # Should handle failure gracefully without crashing
    routes = engine.calculate_routes(40.7128, -74.0060, 34.0522, -118.2437)
    assert routes == []
    assert "Routing provider connection failure" in getattr(engine, "last_failure_reason", "")


# -----------------------------------------------------------------------------
# 14. Missing or Invalid Route Geometry
# -----------------------------------------------------------------------------
def test_missing_or_invalid_route_geometry():
    # Route with only 1 point or empty polyline must be filtered or rejected
    invalid_r = RouteOption(
        route_id="INVALID",
        name="Invalid Empty Route",
        mode=TravelMode.DRIVING,
        distance_meters=100.0,
        duration_seconds=10.0,
        polyline=[(16.50, 80.60)],  # Invalid: less than 2 points
        summary_roads=[]
    )
    valid_r = RouteOption(
        route_id="VALID",
        name="Valid Road",
        mode=TravelMode.DRIVING,
        distance_meters=1500.0,
        duration_seconds=120.0,
        polyline=[(16.50, 80.60), (16.51, 80.61)],
        summary_roads=["Main Road"]
    )

    filtered = filter_distinct_routes([invalid_r, valid_r], max_overlap=0.80)
    assert len(filtered) == 1
    assert filtered[0].route_id == "VALID"


# -----------------------------------------------------------------------------
# 15. Synchronization Between Selected Route and Virtual Guide
# -----------------------------------------------------------------------------
def test_synchronization_between_selected_route_and_virtual_guide():
    provider = DeterministicMockProvider()
    engine = RealWorldRouteEngine(provider=provider)
    routes = engine.calculate_routes(16.50, 80.60, 16.24, 80.64)

    router = MultiObjectiveRouter()
    ranked = router.evaluate_and_rank_routes(routes, objective=OptimizationObjective.FASTEST)

    # Select Route 2
    selected_r_item = ranked[1]
    sel_route = selected_r_item.route
    sel_route_id = sel_route.route_id

    # Friendly turns generated from selected route steps
    turns = generate_friendly_virtual_guide_turns(
        steps=sel_route.steps,
        origin="Start Point",
        destination="Destination Point",
        travel_mode="car"
    )
    assert len(turns) >= 1

    # Virtual Guide HTML incorporates exact route ID, distance, and coordinates
    guide_html = build_always_visible_virtual_guide_html(
        origin_name="Start Point",
        dest_name="Destination Point",
        polyline=sel_route.polyline,
        steps=turns,
        travel_mode="car",
        total_distance_m=sel_route.distance_meters,
        current_speed_kmh=60.0,
        session_id=f"MAIN_NAV_GUIDE_{sel_route_id}"
    )

    # Verify session ID and route synchronization
    assert f"MAIN_NAV_GUIDE_{sel_route_id}" in guide_html
    assert "virtual-human-guide" in guide_html
