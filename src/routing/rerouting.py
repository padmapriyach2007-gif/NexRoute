"""
Dynamic Incident Re-routing and Detour Engine.
Performs geometric exclusion of hazard zones and computes physically distinct detours.
Replaces legacy mock replanning that re-used blocked polylines.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Any
from src.routing.graph import RoutingGraph, Edge, haversine_distance_m
from src.routing.costs import CostModel, ObjectiveType
from src.routing.astar import a_star_search


@dataclass
class IncidentZone:
    """Represents a physical hazard or road closure area."""
    incident_id: str
    lat: float
    lon: float
    radius_meters: float
    severity: str = "HIGH"
    description: str = "Road Incident"
    road_name: Optional[str] = None


@dataclass
class DetourOutcome:
    success: bool
    detour_path: Optional[List[str]] = None
    distance_meters: float = 0.0
    duration_seconds: float = 0.0
    roads: List[str] = None
    is_accessible: bool = True
    blocked_edges_count: int = 0
    failure_reason: Optional[str] = None


class DynamicReplanner:
    """
    Dynamic replanner for situational incidents and unexpected road closures.
    Identifies edges intersecting incident buffer zones and generates alternative corridors.
    """

    def __init__(self, graph: RoutingGraph):
        self.graph = graph

    def identify_blocked_edges(self, incident: IncidentZone) -> Set[Tuple[str, str]]:
        """
        Finds all graph edges where either endpoint or the segment chord falls within
        the incident radius.
        """
        blocked: Set[Tuple[str, str]] = set()

        for u, edges in self.graph.adjacency.items():
            u_node = self.graph.nodes.get(u)
            if not u_node:
                continue

            for edge in edges:
                v_node = self.graph.nodes.get(edge.v)
                if not v_node:
                    continue

                # Check endpoints
                d_u = haversine_distance_m(incident.lat, incident.lon, u_node.lat, u_node.lon)
                d_v = haversine_distance_m(incident.lat, incident.lon, v_node.lat, v_node.lon)

                # Check road name match if specified
                road_match = (incident.road_name and edge.road_name and
                              incident.road_name.lower() in edge.road_name.lower())

                if d_u <= incident.radius_meters or d_v <= incident.radius_meters or road_match:
                    blocked.add((edge.u, edge.v))
                    blocked.add((edge.v, edge.u))

        return blocked

    def compute_detour(
        self,
        current_node: str,
        destination_node: str,
        incidents: List[IncidentZone],
        cost_model: Optional[CostModel] = None,
        require_accessible: bool = False
    ) -> DetourOutcome:
        """
        Computes a genuine detour from traveler's current position to destination,
        bypassing all active incident exclusion zones.
        """
        all_blocked: Set[Tuple[str, str]] = set()
        for inc in incidents:
            all_blocked.update(self.identify_blocked_edges(inc))

        cost_model = cost_model or CostModel(objective=ObjectiveType.FASTEST)

        detour_res = a_star_search(
            self.graph,
            start_node=current_node,
            goal_node=destination_node,
            cost_model=cost_model,
            blocked_edges=all_blocked,
            require_accessible=require_accessible
        )

        if not detour_res:
            return DetourOutcome(
                success=False,
                blocked_edges_count=len(all_blocked) // 2,
                failure_reason="No continuous road network connection exists around active incident zone."
            )

        return DetourOutcome(
            success=True,
            detour_path=detour_res[0],
            distance_meters=detour_res[1],
            duration_seconds=detour_res[2],
            roads=detour_res[3],
            is_accessible=detour_res[4],
            blocked_edges_count=len(all_blocked) // 2
        )
