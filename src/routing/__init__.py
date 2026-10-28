"""
NexRoute Clean Modular Routing Engine.
Provides mathematically rigorous graph construction, cost evaluation,
Dijkstra shortest-path reference, admissible A* and Bidirectional A*,
loopless Yen's K-Shortest Paths, 3-state accessibility constraints,
incident re-routing, and normalized multi-objective ranking.
"""

from src.routing.graph import RoutingGraph, Node, Edge
from src.routing.costs import CostFunction, CostModel, ObjectiveType
from src.routing.dijkstra import dijkstra_search
from src.routing.astar import a_star_search, bidirectional_a_star_search
from src.routing.alternatives import yens_k_shortest_paths
from src.routing.accessibility import (
    AccessibilityState,
    AccessibilityConstraintMode,
    AccessibilityConstraintEngine,
    AccessibilityEvaluation
)
from src.routing.rerouting import DynamicReplanner, IncidentZone
from src.routing.ranking import MultiObjectiveRanker, RouteScoringWeights

__all__ = [
    "RoutingGraph",
    "Node",
    "Edge",
    "CostFunction",
    "CostModel",
    "ObjectiveType",
    "dijkstra_search",
    "a_star_search",
    "bidirectional_a_star_search",
    "yens_k_shortest_paths",
    "AccessibilityState",
    "AccessibilityConstraintMode",
    "AccessibilityConstraintEngine",
    "AccessibilityEvaluation",
    "DynamicReplanner",
    "IncidentZone",
    "MultiObjectiveRanker",
    "RouteScoringWeights",
]
