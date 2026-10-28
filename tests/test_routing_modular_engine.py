"""
Unit and Integration Test Suite for the Modular Routing Engine (src/routing/).
Validates Dijkstra reference, Admissible A*, Bidirectional A*, Loopless Yen's KSP,
3-State Accessibility Constraints, Dynamic Incident Replanning, and Multi-Objective Scoring.
"""

import pytest
import math
from src.routing.graph import RoutingGraph, Node, Edge, haversine_distance_m
from src.routing.costs import CostModel, ObjectiveType
from src.routing.dijkstra import dijkstra_search
from src.routing.astar import a_star_search, bidirectional_a_star_search
from src.routing.alternatives import yens_k_shortest_paths
from src.routing.accessibility import (
    AccessibilityState,
    AccessibilityConstraintMode,
    AccessibilityConstraintEngine
)
from src.routing.rerouting import DynamicReplanner, IncidentZone
from src.routing.ranking import MultiObjectiveRanker, RouteScoringWeights


@pytest.fixture
def sample_routing_graph():
    r"""
    Constructs a deterministic synthetic grid network with alternate corridors:
          (N2)----1000m----(N3)
         /                    \
       800m                  800m
       /                        \
    (N1)---------1500m----------(N4)
       \                        /
       900m                  900m
         \                    /
          (N5)----1200m----(N6)
    """
    g = RoutingGraph()
    g.add_node("N1", 16.2300, 80.5400)
    g.add_node("N2", 16.2380, 80.5450)
    g.add_node("N3", 16.2380, 80.5550)
    g.add_node("N4", 16.2300, 80.5600)
    g.add_node("N5", 16.2220, 80.5450)
    g.add_node("N6", 16.2220, 80.5550)

    # Central corridor: N1 -> N4 (1500m, 50 km/h)
    g.add_edge("N1", "N4", distance_meters=1500.0, speed_kmh=50.0, road_name="Central Expressway", is_accessible=True)

    # Northern corridor: N1 -> N2 -> N3 -> N4 (800 + 1000 + 800 = 2600m, 80 km/h)
    g.add_edge("N1", "N2", distance_meters=800.0, speed_kmh=80.0, road_name="North Ring A", is_accessible=True)
    g.add_edge("N2", "N3", distance_meters=1000.0, speed_kmh=80.0, road_name="North Ring B", is_accessible=True)
    g.add_edge("N3", "N4", distance_meters=800.0, speed_kmh=80.0, road_name="North Ring C", is_accessible=True)

    # Southern corridor: N1 -> N5 -> N6 -> N4 (900 + 1200 + 900 = 3000m, 40 km/h with stairs on N5->N6)
    g.add_edge("N1", "N5", distance_meters=900.0, speed_kmh=40.0, road_name="South Canal A", is_accessible=True)
    g.add_edge("N5", "N6", distance_meters=1200.0, speed_kmh=40.0, road_name="South Canal B (Stairs)", is_accessible=False, stairs=True)
    g.add_edge("N6", "N4", distance_meters=900.0, speed_kmh=40.0, road_name="South Canal C", is_accessible=True)

    return g


# =============================================================================
# 1. GRAPH PRIMITIVES & NON-NEGATIVE VALIDATION
# =============================================================================

def test_graph_edge_non_negative_constraints():
    g = RoutingGraph()
    g.add_node("A", 16.0, 80.0)
    g.add_node("B", 16.1, 80.1)

    with pytest.raises(ValueError, match="Edge distance cannot be negative"):
        g.add_edge("A", "B", distance_meters=-50.0, speed_kmh=40.0)

    with pytest.raises(ValueError, match="Edge speed must be strictly positive"):
        g.add_edge("A", "B", distance_meters=500.0, speed_kmh=0.0)


def test_graph_nearest_node_snapping(sample_routing_graph):
    # Query point close to N2 (16.2380, 80.5450)
    nearest = sample_routing_graph.nearest_node(16.2381, 80.5451)
    assert nearest == "N2"


# =============================================================================
# 2. DIJKSTRA VS A* OPTIMALITY VERIFICATION
# =============================================================================

def test_dijkstra_and_astar_produce_identical_shortest_paths(sample_routing_graph):
    cost_shortest = CostModel(objective=ObjectiveType.SHORTEST)

    dijkstra_res = dijkstra_search(sample_routing_graph, "N1", "N4", cost_model=cost_shortest)
    astar_res = a_star_search(sample_routing_graph, "N1", "N4", cost_model=cost_shortest)

    assert dijkstra_res is not None
    assert astar_res is not None

    # Both must find the direct 1500m path: ["N1", "N4"]
    assert dijkstra_res[0] == ["N1", "N4"]
    assert astar_res[0] == ["N1", "N4"]
    assert math.isclose(dijkstra_res[1], 1500.0, rel_tol=1e-5)
    assert math.isclose(astar_res[1], 1500.0, rel_tol=1e-5)


def test_fastest_objective_picks_higher_speed_corridor(sample_routing_graph):
    # Northern corridor (2600m @ 80 km/h = 117s) vs Central (1500m @ 50 km/h = 108s)
    cost_fastest = CostModel(objective=ObjectiveType.FASTEST)
    res = a_star_search(sample_routing_graph, "N1", "N4", cost_model=cost_fastest)

    assert res is not None
    assert res[0] == ["N1", "N4"]
    assert math.isclose(res[2], 1500.0 / (50.0 * 1000.0 / 3600.0), rel_tol=1e-3)


def test_bidirectional_astar_matches_unidirectional(sample_routing_graph):
    cost_model = CostModel(objective=ObjectiveType.FASTEST)
    uni_res = a_star_search(sample_routing_graph, "N1", "N4", cost_model=cost_model)
    bi_res = bidirectional_a_star_search(sample_routing_graph, "N1", "N4", cost_model=cost_model)

    assert uni_res is not None
    assert bi_res is not None
    assert uni_res[0] == bi_res[0]
    assert math.isclose(uni_res[1], bi_res[1], rel_tol=1e-4)


# =============================================================================
# 3. YEN'S K-SHORTEST LOOPLESS PATHS
# =============================================================================

def test_yens_k_shortest_paths_loopless_candidates(sample_routing_graph):
    # Ask for K=3 loopless paths from N1 to N4
    cost_model = CostModel(objective=ObjectiveType.SHORTEST)
    alternatives = yens_k_shortest_paths(sample_routing_graph, "N1", "N4", K=3, cost_model=cost_model)

    assert len(alternatives) == 3

    # Primary shortest: N1 -> N4 (1500m)
    assert alternatives[0][0] == ["N1", "N4"]
    assert math.isclose(alternatives[0][1], 1500.0)

    # 2nd shortest: N1 -> N2 -> N3 -> N4 (2600m)
    assert alternatives[1][0] == ["N1", "N2", "N3", "N4"]
    assert math.isclose(alternatives[1][1], 2600.0)

    # 3rd shortest: N1 -> N5 -> N6 -> N4 (3000m)
    assert alternatives[2][0] == ["N1", "N5", "N6", "N4"]
    assert math.isclose(alternatives[2][1], 3000.0)

    # Verify all paths are simple/loopless (no duplicate nodes in any path)
    for p_nodes, _, _, _, _, _ in alternatives:
        assert len(p_nodes) == len(set(p_nodes))


# =============================================================================
# 4. ACCESSIBILITY THREE-STATE CONSTRAINT ENGINE
# =============================================================================

def test_accessibility_strict_vs_best_effort_modes(sample_routing_graph):
    # Southern path N1->N5->N6->N4 has stairs on N5->N6
    edges_south = [
        sample_routing_graph.adjacency["N1"][1], # N1->N5
        sample_routing_graph.adjacency["N5"][1], # N5->N6 (stairs)
        sample_routing_graph.adjacency["N6"][1], # N6->N4
    ]

    strict_engine = AccessibilityConstraintEngine(mode=AccessibilityConstraintMode.STRICT)
    best_effort_engine = AccessibilityConstraintEngine(mode=AccessibilityConstraintMode.BEST_EFFORT)

    eval_strict = strict_engine.evaluate_route(edges_south)
    eval_best_effort = best_effort_engine.evaluate_route(edges_south)

    # Both must detect the confirmed stairs and mark the route ineligible
    assert eval_strict.is_eligible is False
    assert eval_best_effort.is_eligible is False
    assert eval_strict.state == AccessibilityState.VERIFIED_INACCESSIBLE
    assert any("stairs" in v.lower() for v in eval_strict.violations)


def test_accessibility_strict_rejects_unverified_segments():
    g = RoutingGraph()
    g.add_node("U1", 10.0, 20.0)
    g.add_node("U2", 10.0, 20.1)
    # Edge with no explicit accessibility tags
    edge_unverified = g.add_edge("U1", "U2", distance_meters=500.0, speed_kmh=30.0, road_name="Unknown Alley")

    strict_engine = AccessibilityConstraintEngine(mode=AccessibilityConstraintMode.STRICT)
    best_effort_engine = AccessibilityConstraintEngine(mode=AccessibilityConstraintMode.BEST_EFFORT)

    eval_strict = strict_engine.evaluate_route([edge_unverified])
    eval_best = best_effort_engine.evaluate_route([edge_unverified])

    # Strict mode rejects unverified data to protect wheelchair users
    assert eval_strict.is_eligible is False
    assert eval_strict.state == AccessibilityState.UNKNOWN

    # Best-effort mode permits traversal with disclosed uncertainty
    assert eval_best.is_eligible is True
    assert eval_best.state == AccessibilityState.UNKNOWN
    assert len(eval_best.disclosures) > 0


# =============================================================================
# 5. DYNAMIC REPLANNER & INCIDENT EXCLUSION
# =============================================================================

def test_dynamic_replanner_bypasses_blocked_incident_zone(sample_routing_graph):
    replanner = DynamicReplanner(sample_routing_graph)

    # Place a critical hazard directly on the Central Expressway (N1 -> N4)
    hazard = IncidentZone(
        incident_id="HZ_OIL_SPILL",
        lat=16.2300,
        lon=80.5500,
        radius_meters=350.0,
        road_name="Central Expressway"
    )

    detour = replanner.compute_detour("N1", "N4", incidents=[hazard])

    assert detour.success is True
    # Central corridor must be blocked; replanner must take the Northern Ring road
    assert "Central Expressway" not in detour.roads
    assert detour.detour_path == ["N1", "N2", "N3", "N4"]


# =============================================================================
# 6. MULTI-OBJECTIVE SCORING & PARETO DOMINANCE
# =============================================================================

def test_multi_objective_normalized_scoring_and_pareto():
    class DummyRoute:
        def __init__(self, name, dist, dur):
            self.name = name
            self.distance_meters = dist
            self.duration_seconds = dur

    # Route A: 10 km, 15 min (900s)
    # Route B: 8 km, 20 min (1200s)
    # Route C: 12 km, 25 min (1500s) - dominated by both A and B!
    r_a = DummyRoute("Route A", 10000.0, 900.0)
    r_b = DummyRoute("Route B", 8000.0, 1200.0)
    r_c = DummyRoute("Route C", 12000.0, 1500.0)

    ranker = MultiObjectiveRanker()
    ranked = ranker.rank_routes([r_a, r_b, r_c], objective=ObjectiveType.BALANCED)

    assert len(ranked) == 3
    # Route C must NOT be Pareto optimal (dominated by A and B)
    c_eval = next(r for r in ranked if r.route.name == "Route C")
    assert c_eval.is_pareto_optimal is False

    # Route A and Route B must be Pareto optimal
    a_eval = next(r for r in ranked if r.route.name == "Route A")
    b_eval = next(r for r in ranked if r.route.name == "Route B")
    assert a_eval.is_pareto_optimal is True
    assert b_eval.is_pareto_optimal is True
