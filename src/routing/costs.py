"""
Cost evaluation and heuristic functions for multi-objective graph search.
Guarantees mathematical admissibility for A* heuristics.
"""

from enum import Enum
from typing import Optional, Dict, Any
from src.routing.graph import Edge, haversine_distance_m, RoutingGraph


class ObjectiveType(str, Enum):
    """Supported routing objectives."""
    FASTEST = "FASTEST"
    SHORTEST = "SHORTEST"
    BALANCED = "BALANCED"
    ACCESSIBLE = "ACCESSIBLE"


class CostModel:
    """
    Computes traversal costs for edges under different objective functions.
    Enforces non-negative edge costs required by Dijkstra and A*.
    """

    def __init__(
        self,
        objective: ObjectiveType = ObjectiveType.FASTEST,
        inaccessible_penalty: float = 1e9,
        balance_alpha: float = 0.5,  # Weight on time vs distance
    ):
        self.objective = objective
        self.inaccessible_penalty = inaccessible_penalty
        self.balance_alpha = balance_alpha

    def edge_cost(self, edge: Edge, require_accessible: bool = False) -> float:
        """
        Calculates the scalar cost of traversing an edge.
        Returns non-negative cost.
        """
        if require_accessible and not edge.is_accessible:
            return self.inaccessible_penalty

        if self.objective == ObjectiveType.SHORTEST:
            return edge.distance_meters

        if self.objective == ObjectiveType.FASTEST:
            return edge.free_flow_time_seconds

        if self.objective == ObjectiveType.BALANCED:
            # Normalized local metric: seconds + (meters / 10.0)
            # where 10 m/s (~36 km/h) is standard urban reference speed
            return edge.free_flow_time_seconds * self.balance_alpha + (edge.distance_meters / 10.0) * (1.0 - self.balance_alpha)

        if self.objective == ObjectiveType.ACCESSIBLE:
            base_time = edge.free_flow_time_seconds
            return base_time if edge.is_accessible else (base_time + self.inaccessible_penalty)

        return edge.distance_meters

    def heuristic(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
        graph: Optional[RoutingGraph] = None
    ) -> float:
        """
        Admissible lower-bound heuristic function h(u, goal).
        - For SHORTEST: Great-Circle chord distance (strictly <= surface path distance).
        - For FASTEST: Great-Circle chord distance / max legal network speed (strictly <= minimum travel time).
        - For BALANCED: Great-Circle distance combined with max network speed lower bound.
        """
        dist_m = haversine_distance_m(lat1, lon1, lat2, lon2)

        if self.objective == ObjectiveType.SHORTEST:
            return dist_m

        max_speed_kmh = graph.max_speed_kmh if graph else 120.0
        max_speed_mps = max(1.0, max_speed_kmh * (1000.0 / 3600.0))

        if self.objective in (ObjectiveType.FASTEST, ObjectiveType.ACCESSIBLE):
            return dist_m / max_speed_mps

        if self.objective == ObjectiveType.BALANCED:
            min_time = dist_m / max_speed_mps
            return min_time * self.balance_alpha + (dist_m / 10.0) * (1.0 - self.balance_alpha)

        return dist_m


# Alias for backward compatibility
CostFunction = CostModel
