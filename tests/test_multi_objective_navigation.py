"""
Automated Pytest Suite for Multi-Objective Route Optimization, Road Restrictions,
and Truthful Provenance Boundaries in CampusAegis 2.0.
"""

import pytest
from src.route_engine import RouteOption, RealWorldRouteEngine, TravelMode
from src.road_condition_model import (
    RoadRestriction,
    TrafficCondition,
    RestrictionType,
    TrafficSeverity,
    OperatingMode,
    OptimizationObjective
)
from src.road_condition_manager import RoadConditionManager
from src.multi_objective_router import MultiObjectiveRouter, RouteEligibilityStatus


@pytest.fixture
def sample_routes():
    """Provides three distinct synthetic candidate routes for scoring tests."""
    r1 = RouteOption(
        route_id="route_fast_highway",
        name="Highway Express",
        mode=TravelMode.DRIVING,
        distance_meters=18500.0,
        duration_seconds=1200.0,  # 20.0 min (Fastest, but longer distance)
        polyline=[(16.2335, 80.5505), (16.2100, 80.5900), (16.2600, 80.6000), (16.3067, 80.4365)],
        summary_roads=["NH-16 Bypass Expressway"],
        is_accessible=True
    )
    r2 = RouteOption(
        route_id="route_short_arterial",
        name="Direct Arterial Cut",
        mode=TravelMode.DRIVING,
        distance_meters=14200.0,  # 14.2 km (Shortest, but 26.0 min slower due to signals)
        duration_seconds=1560.0,
        polyline=[(16.2335, 80.5505), (16.2600, 80.5000), (16.3067, 80.4365)],
        summary_roads=["Vadlamudi - Narakodur Main Rd"],
        is_accessible=True
    )
    r3 = RouteOption(
        route_id="route_scenic_local",
        name="Canal Local Road",
        mode=TravelMode.DRIVING,
        distance_meters=16000.0,
        duration_seconds=1800.0,  # 30.0 min, contains non-accessible bridge stairs
        polyline=[(16.2335, 80.5505), (16.2800, 80.4800), (16.3067, 80.4365)],
        summary_roads=["Tenali Canal Bund Road"],
        is_accessible=False
    )
    return [r1, r2, r3]


def test_fastest_objective_ranks_highway_first(sample_routes):
    mgr = RoadConditionManager(OperatingMode.LIVE_ROUTING)
    router = MultiObjectiveRouter(mgr)

    ranked = router.evaluate_and_rank_routes(sample_routes, objective=OptimizationObjective.FASTEST)
    assert len(ranked) == 3
    # Highway Express should be Rank 1 because it has the lowest duration (20 min)
    assert ranked[0].route.route_id == "route_fast_highway"
    assert ranked[0].rank == 1
    assert "lowest travel time" in ranked[0].recommendation_explanation.lower()
    assert ranked[0].is_eligible is True


def test_shortest_objective_ranks_arterial_first(sample_routes):
    mgr = RoadConditionManager(OperatingMode.LIVE_ROUTING)
    router = MultiObjectiveRouter(mgr)

    ranked = router.evaluate_and_rank_routes(sample_routes, objective=OptimizationObjective.SHORTEST)
    assert len(ranked) == 3
    # Direct Arterial Cut should be Rank 1 because it has the shortest distance (14.2 km)
    assert ranked[0].route.route_id == "route_short_arterial"
    assert ranked[0].rank == 1
    assert "shortest physical distance" in ranked[0].recommendation_explanation.lower()
    assert ranked[0].is_eligible is True


def test_accessible_objective_excludes_inaccessible_pathways(sample_routes):
    mgr = RoadConditionManager(OperatingMode.LIVE_ROUTING)
    router = MultiObjectiveRouter(mgr)

    ranked = router.evaluate_and_rank_routes(
        sample_routes,
        objective=OptimizationObjective.ACCESSIBLE,
        require_accessible=True
    )
    # Canal Local Road is not accessible, so it must be marked ineligible
    inaccessible = next(r for r in ranked if r.route.route_id == "route_scenic_local")
    assert inaccessible.is_eligible is False
    assert inaccessible.status == RouteEligibilityStatus.INACCESSIBLE
    assert any("stairs" in r.lower() or "accessible" in r.lower() for r in inaccessible.rejection_reasons)


def test_road_closure_hard_constraint_exclusion(sample_routes):
    mgr = RoadConditionManager(OperatingMode.CONTROLLED_DEMO)
    # Place a hard closure on Highway Express unique waypoint
    target_pt = sample_routes[0].polyline[1]  # (16.2100, 80.5900)
    mgr.add_restriction(RoadRestriction(
        restriction_id="RESTR_MAINTENANCE_01",
        restriction_type=RestrictionType.ROAD_CLOSURE,
        road_name="NH-16 Bypass Expressway",
        latitude=target_pt[0],
        longitude=target_pt[1],
        affected_radius_meters=150.0,
        description="Bridge Deck Resurfacing",
        is_hard_closure=True,
        is_demonstration=True
    ))

    router = MultiObjectiveRouter(mgr)
    ranked = router.evaluate_and_rank_routes(sample_routes, objective=OptimizationObjective.FASTEST)

    # Highway Express must now be rejected despite having lower travel time
    restr_route = next(r for r in ranked if r.route.route_id == "route_fast_highway")
    assert restr_route.is_eligible is False
    assert restr_route.status == RouteEligibilityStatus.RESTRICTED_CLOSURE

    # The top eligible route should now be the Direct Arterial Cut
    eligible = [r for r in ranked if r.is_eligible]
    assert len(eligible) >= 1
    assert eligible[0].route.route_id == "route_short_arterial"


def test_mode_boundary_prevents_demo_data_in_live_mode():
    mgr = RoadConditionManager(OperatingMode.LIVE_ROUTING)
    assert mgr.operating_mode == OperatingMode.LIVE_ROUTING

    demo_restr = RoadRestriction(
        restriction_id="DEMO_TEST_01",
        restriction_type=RestrictionType.ROAD_WORK,
        road_name="Demo Road",
        latitude=16.25,
        longitude=80.50,
        affected_radius_meters=100.0,
        is_demonstration=True
    )
    # Adding demo restriction to LIVE_ROUTING must be rejected
    added = mgr.add_restriction(demo_restr)
    assert added is False
    assert len(mgr.get_active_restrictions()) == 0

    # Switching to demo mode allows demo data
    mgr.set_mode(OperatingMode.CONTROLLED_DEMO)
    added_in_demo = mgr.add_restriction(demo_restr)
    assert added_in_demo is True
    assert len(mgr.get_active_restrictions()) == 1

    # Indicator must clearly state DEMO DATA — NOT LIVE
    indicator = mgr.get_mode_indicator()
    assert indicator["is_demo"] is True
    assert "DEMO DATA — NOT LIVE" in indicator["label"]


def test_traffic_delay_incorporation(sample_routes):
    mgr = RoadConditionManager(OperatingMode.CONTROLLED_DEMO)
    # Add a 10-minute traffic delay to Highway Express summary road
    mgr.add_traffic_condition(TrafficCondition(
        segment_id="TRAF_01",
        road_name="NH-16 Bypass Expressway",
        delay_minutes=10.0,  # +10 minutes
        speed_factor=0.5,
        severity=TrafficSeverity.HEAVY,
        is_demonstration=True
    ))

    router = MultiObjectiveRouter(mgr)
    ranked = router.evaluate_and_rank_routes(sample_routes, objective=OptimizationObjective.FASTEST)

    highway = next(r for r in ranked if r.route.route_id == "route_fast_highway")
    # Base duration was 20 min (1200s), with +10 min traffic delay = 30.0 min
    assert highway.effective_duration_minutes == pytest.approx(30.0, rel=0.05)


def test_safety_hazard_detection_disqualifies_route_before_recommendation(sample_routes):
    from src.hazard_map import HazardMap, GeographicHazard, HazardSeverity
    hazard_map = HazardMap()
    mgr = RoadConditionManager(OperatingMode.LIVE_ROUTING)
    router = MultiObjectiveRouter(road_condition_manager=mgr, hazard_map=hazard_map)

    # Route 1 (route_fast_highway) is normally the fastest route.
    # We place a critical chemical fire hazard directly on route 1's waypoint.
    target_pt = sample_routes[0].polyline[1]  # (16.2100, 80.5900)
    hazard_map.add_hazard(GeographicHazard(
        hazard_id="HAZ_CRITICAL_01",
        incident_type="CHEMICAL_FIRE",
        severity=HazardSeverity.CRITICAL,
        latitude=target_pt[0],
        longitude=target_pt[1],
        radius_meters=300.0,
        description="Toxic tanker fire blocking expressway"
    ))

    # Evaluate routes with hazard detection
    ranked = router.evaluate_and_rank_routes(sample_routes, objective=OptimizationObjective.FASTEST)

    # Route 1 must be flagged as unsafe and disqualified
    r1 = next(r for r in ranked if r.route.route_id == "route_fast_highway")
    assert r1.is_safe is False
    assert r1.is_eligible is False
    assert r1.status == RouteEligibilityStatus.HAZARD_BLOCKED
    assert len(r1.detected_hazards) > 0
    assert any("CHEMICAL_FIRE" in reason for reason in r1.rejection_reasons)

    # Best route recommendation (Rank 1) must now be Route 2 (the verified safe corridor)
    assert ranked[0].route.route_id == "route_short_arterial"
    assert ranked[0].is_safe is True
    assert ranked[0].is_eligible is True
    assert ranked[0].rank == 1
