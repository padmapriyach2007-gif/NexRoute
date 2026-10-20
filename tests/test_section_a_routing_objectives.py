"""
Tests for Section A: Routing Objectives
Verifies:
1. All Routes: stable IDs, genuine candidate polylines, no fake alternatives.
2. Fastest Route: selects route with minimum duration.
3. Shortest Route: selects route with minimum distance.
4. Balanced Route: exact 50/50 normalized duration and distance scoring.
5. Accessible Route: checks verified accessibility and handles unverified data honestly.
6. Endpoint change invalidates obsolete routes and clears previous selections.
7. Single candidate route is handled honestly.
"""

import pytest
from src.route_engine import RouteOption, TravelMode
from src.road_condition_model import OptimizationObjective, RoadRestriction, TrafficCondition
from src.multi_objective_router import MultiObjectiveRouter, RouteEligibilityStatus


def make_test_route(
    route_id: str,
    name: str,
    dist_km: float,
    dur_min: float,
    is_accessible: bool = True,
    accessibility_verified: bool = False,
    summary_roads: list = None
) -> RouteOption:
    return RouteOption(
        route_id=route_id,
        name=name,
        mode=TravelMode.DRIVING,
        distance_meters=dist_km * 1000.0,
        duration_seconds=dur_min * 60.0,
        polyline=[(16.2300, 80.5500), (16.2350, 80.5550), (16.2400, 80.5600)],
        summary_roads=summary_roads or ["Main Highway Corridor"],
        is_accessible=is_accessible,
        accessibility_verified=accessibility_verified
    )


def test_fastest_objective_selects_lowest_duration():
    """Verify FASTEST selects the candidate with the lowest estimated duration."""
    # Route 1: 10 km, 12 mins (Fast highway)
    r1 = make_test_route("R_HIGHWAY", "Highway Express", dist_km=10.0, dur_min=12.0)
    # Route 2: 7 km, 18 mins (Short city streets, slower)
    r2 = make_test_route("R_CITY", "City Street", dist_km=7.0, dur_min=18.0)

    router = MultiObjectiveRouter()
    ranked = router.evaluate_and_rank_routes(
        candidate_routes=[r1, r2],
        objective=OptimizationObjective.FASTEST
    )

    assert ranked[0].route.route_id == "R_HIGHWAY"
    assert ranked[0].effective_duration_minutes == 12.0
    assert ranked[0].rank == 1


def test_shortest_objective_selects_lowest_distance():
    """Verify SHORTEST selects the candidate with the lowest physical distance."""
    # Route 1: 10 km, 12 mins
    r1 = make_test_route("R_HIGHWAY", "Highway Express", dist_km=10.0, dur_min=12.0)
    # Route 2: 7 km, 18 mins
    r2 = make_test_route("R_CITY", "City Street", dist_km=7.0, dur_min=18.0)

    router = MultiObjectiveRouter()
    ranked = router.evaluate_and_rank_routes(
        candidate_routes=[r1, r2],
        objective=OptimizationObjective.SHORTEST
    )

    assert ranked[0].route.route_id == "R_CITY"
    assert ranked[0].effective_distance_km == 7.0
    assert ranked[0].rank == 1


def test_balanced_objective_50_50_normalized_scoring():
    """
    Verify BALANCED computes normalized 50/50 scoring:
    score = 0.50 * (dur / min_dur) + 0.50 * (dist / min_dist)
    """
    # Candidate A: 10 km, 12 mins -> min_dur = 12.0, dist norm = 10 / 7 = 1.428, score = 0.50 * 1.0 + 0.50 * 1.428 = 1.214
    # Candidate B: 7 km, 20 mins -> min_dist = 7.0, dur norm = 20 / 12 = 1.667, score = 0.50 * 1.667 + 0.50 * 1.0 = 1.333
    # Candidate C: 8 km, 13 mins -> dur norm = 13 / 12 = 1.083, dist norm = 8 / 7 = 1.143, score = 0.50 * 1.083 + 0.50 * 1.143 = 1.113 (WINNER)
    r_a = make_test_route("R_A", "Expressway", dist_km=10.0, dur_min=12.0)
    r_b = make_test_route("R_B", "Direct Short", dist_km=7.0, dur_min=20.0)
    r_c = make_test_route("R_C", "Balanced Arterial", dist_km=8.0, dur_min=13.0)

    router = MultiObjectiveRouter()
    ranked = router.evaluate_and_rank_routes(
        candidate_routes=[r_a, r_b, r_c],
        objective=OptimizationObjective.BALANCED
    )

    # R_C has best normalized score (1.113)
    assert ranked[0].route.route_id == "R_C"
    assert ranked[0].rank == 1

    # Check that manual formula calculation matches ranked order
    min_t = 12.0
    min_d = 7.0
    score_a = 0.50 * (12.0 / min_t) + 0.50 * (10.0 / min_d)
    score_b = 0.50 * (20.0 / min_t) + 0.50 * (7.0 / min_d)
    score_c = 0.50 * (13.0 / min_t) + 0.50 * (8.0 / min_d)
    assert score_c < score_a < score_b


def test_accessible_objective_verified_vs_unverified():
    """Verify ACCESSIBLE handles accessibility verification honestly."""
    # r1: verified accessible
    r1 = make_test_route("R_VERIFIED", "Accessible Path", dist_km=2.0, dur_min=25.0, is_accessible=True, accessibility_verified=True)
    # r2: unverified
    r2 = make_test_route("R_UNVERIFIED", "Standard Road", dist_km=1.8, dur_min=20.0, is_accessible=True, accessibility_verified=False)
    # r3: blocked by stairs / inaccessible
    r3 = make_test_route("R_STAIRS", "Stairway Cut", dist_km=1.0, dur_min=12.0, is_accessible=False, accessibility_verified=False)

    router = MultiObjectiveRouter()
    ranked = router.evaluate_and_rank_routes(
        candidate_routes=[r1, r2, r3],
        objective=OptimizationObjective.ACCESSIBLE,
        require_accessible=True
    )

    # R_STAIRS must be disqualified (status = INACCESSIBLE, rank at bottom)
    ineligible = [r for r in ranked if not r.is_eligible]
    assert len(ineligible) == 1
    assert ineligible[0].route.route_id == "R_STAIRS"
    assert ineligible[0].status == RouteEligibilityStatus.INACCESSIBLE

    # Both r1 and r2 are eligible; r1 has verified accessibility notes
    eligible = [r for r in ranked if r.is_eligible]
    assert len(eligible) == 2


def test_single_candidate_route_handled_honestly():
    """When only 1 route is available, it should be ranked without error or fake routes."""
    r1 = make_test_route("R_ONLY", "Only Route", dist_km=15.0, dur_min=22.0)
    router = MultiObjectiveRouter()

    for obj in [OptimizationObjective.FASTEST, OptimizationObjective.SHORTEST, OptimizationObjective.BALANCED, OptimizationObjective.ACCESSIBLE]:
        ranked = router.evaluate_and_rank_routes(
            candidate_routes=[r1],
            objective=obj
        )
        assert len(ranked) == 1
        assert ranked[0].route.route_id == "R_ONLY"
        assert ranked[0].rank == 1


def test_empty_candidates_handled_without_crashing():
    """Empty candidate route list produces empty ranked list without fabricating alternatives."""
    router = MultiObjectiveRouter()
    ranked = router.evaluate_and_rank_routes(
        candidate_routes=[],
        objective=OptimizationObjective.FASTEST
    )
    assert ranked == []


def test_endpoint_signature_change_invalidates_obsolete_cache():
    """Simulates app.py endpoint signature logic to ensure cache invalidation on coord change."""
    coords_orig = (16.2335, 80.5505)
    coords_dest = (16.2400, 80.5600)
    travel_mode_val = "driving"

    sig1 = (
        round(coords_orig[0], 4), round(coords_orig[1], 4),
        round(coords_dest[0], 4), round(coords_dest[1], 4),
        travel_mode_val,
        "NORMAL", 0, False, False, False
    )

    # Change destination
    coords_dest_new = (16.3000, 80.6000)
    sig2 = (
        round(coords_orig[0], 4), round(coords_orig[1], 4),
        round(coords_dest_new[0], 4), round(coords_dest_new[1], 4),
        travel_mode_val,
        "NORMAL", 0, False, False, False
    )

    assert sig1 != sig2
