"""
Graph modeling primitives for NexRoute.
Enforces non-negative edge attributes, geographic coordinate snapping,
and immutability during path search.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes Great-Circle distance between two coordinates in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    return R * c


@dataclass(frozen=True)
class Node:
    """Represents a vertex in the routing network."""
    node_id: str
    lat: float
    lon: float
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Edge:
    """Represents a directed road/path link between two vertices."""
    u: str
    v: str
    distance_meters: float
    speed_kmh: float
    road_name: str = "Unnamed Link"
    is_accessible: bool = True
    attributes: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.distance_meters < 0:
            raise ValueError(f"Edge distance cannot be negative: {self.distance_meters}")
        if self.speed_kmh <= 0:
            raise ValueError(f"Edge speed must be strictly positive: {self.speed_kmh}")

    @property
    def free_flow_time_seconds(self) -> float:
        speed_mps = max(0.1, self.speed_kmh * (1000.0 / 3600.0))
        return self.distance_meters / speed_mps


class RoutingGraph:
    """
    Directional, attributed routing graph with strict non-negative edge constraints.
    Supports incident blocking and nearest-neighbor geographic snapping.
    """

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.adjacency: Dict[str, List[Edge]] = {}
        self.reverse_adjacency: Dict[str, List[Edge]] = {}

    def add_node(self, node_id: str, lat: float, lon: float, **attributes) -> Node:
        node = Node(node_id=node_id, lat=lat, lon=lon, attributes=attributes)
        self.nodes[node_id] = node
        if node_id not in self.adjacency:
            self.adjacency[node_id] = []
        if node_id not in self.reverse_adjacency:
            self.reverse_adjacency[node_id] = []
        return node

    def add_edge(
        self,
        u: str,
        v: str,
        distance_meters: float,
        speed_kmh: float,
        road_name: str = "Road",
        is_accessible: bool = True,
        bidirectional: bool = True,
        **attributes
    ) -> Edge:
        if u not in self.nodes or v not in self.nodes:
            raise KeyError(f"Both endpoints must exist in graph: {u} -> {v}")

        forward_edge = Edge(
            u=u, v=v,
            distance_meters=distance_meters,
            speed_kmh=speed_kmh,
            road_name=road_name,
            is_accessible=is_accessible,
            attributes=attributes
        )
        self.adjacency[u].append(forward_edge)
        self.reverse_adjacency[v].append(forward_edge)

        if bidirectional:
            backward_edge = Edge(
                u=v, v=u,
                distance_meters=distance_meters,
                speed_kmh=speed_kmh,
                road_name=road_name,
                is_accessible=is_accessible,
                attributes=attributes
            )
            self.adjacency[v].append(backward_edge)
            self.reverse_adjacency[u].append(backward_edge)

        return forward_edge

    def get_neighbors(
        self,
        u: str,
        blocked_edges: Optional[Set[Tuple[str, str]]] = None,
        reverse: bool = False
    ) -> List[Edge]:
        """Returns valid outgoing (or incoming if reverse=True) edges for node u."""
        edges = self.reverse_adjacency.get(u, []) if reverse else self.adjacency.get(u, [])
        if not blocked_edges:
            return edges

        valid = []
        for e in edges:
            edge_tuple = (e.u, e.v)
            sorted_tuple = tuple(sorted([e.u, e.v]))
            if edge_tuple not in blocked_edges and sorted_tuple not in blocked_edges:
                valid.append(e)
        return valid

    def nearest_node(self, lat: float, lon: float) -> Optional[str]:
        """Finds closest node in the graph using Great-Circle distance."""
        if not self.nodes:
            return None
        best_node = None
        min_dist = float("inf")
        for node_id, node in self.nodes.items():
            d = haversine_distance_m(lat, lon, node.lat, node.lon)
            if d < min_dist:
                min_dist = d
                best_node = node_id
        return best_node

    @property
    def max_speed_kmh(self) -> float:
        """Finds the maximum speed on any edge in the network (for admissible time heuristics)."""
        max_s = 50.0
        for edge_list in self.adjacency.values():
            for e in edge_list:
                if e.speed_kmh > max_s:
                    max_s = e.speed_kmh
        return max_s
