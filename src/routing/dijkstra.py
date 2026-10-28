"""
Reference Dijkstra Shortest-Path algorithm implementation.
Guarantees optimal paths on non-negative weighted graphs.
Serves as mathematical baseline to validate A* and heuristic search.
"""

import heapq
from typing import Dict, List, Optional, Set, Tuple
from src.routing.graph import RoutingGraph, Edge
from src.routing.costs import CostModel, ObjectiveType


def dijkstra_search(
    graph: RoutingGraph,
    start_node: str,
    goal_node: str,
    cost_model: Optional[CostModel] = None,
    blocked_edges: Optional[Set[Tuple[str, str]]] = None,
    require_accessible: bool = False
) -> Optional[Tuple[List[str], float, float, List[str], bool]]:
    """
    Standard Dijkstra search with non-negative edge weights.
    Returns:
        (path_nodes, total_distance_m, total_duration_s, road_names, is_accessible)
        or None if no path exists.
    """
    if start_node not in graph.nodes or goal_node not in graph.nodes:
        return None

    if start_node == goal_node:
        return ([start_node], 0.0, 0.0, [], True)

    cost_model = cost_model or CostModel(objective=ObjectiveType.FASTEST)
    blocked_edges = blocked_edges or set()

    # Priority queue stores: (cumulative_cost, node_id)
    pq: List[Tuple[float, str]] = []
    heapq.heappush(pq, (0.0, start_node))

    best_cost: Dict[str, float] = {start_node: 0.0}
    parent: Dict[str, Tuple[Optional[str], Optional[Edge]]] = {start_node: (None, None)}

    while pq:
        curr_cost, curr_node = heapq.heappop(pq)

        if curr_node == goal_node:
            break

        if curr_cost > best_cost.get(curr_node, float("inf")):
            continue

        for edge in graph.get_neighbors(curr_node, blocked_edges=blocked_edges):
            if require_accessible and not edge.is_accessible:
                continue

            e_cost = cost_model.edge_cost(edge, require_accessible=require_accessible)
            new_cost = curr_cost + e_cost

            if new_cost < best_cost.get(edge.v, float("inf")):
                best_cost[edge.v] = new_cost
                parent[edge.v] = (curr_node, edge)
                heapq.heappush(pq, (new_cost, edge.v))

    if goal_node not in parent or parent[goal_node][0] is None and start_node != goal_node:
        return None

    # Reconstruct path and metrics from predecessor tree
    path_nodes: List[str] = []
    path_edges: List[Edge] = []
    curr = goal_node

    while curr is not None:
        path_nodes.append(curr)
        prev_node, edge = parent.get(curr, (None, None))
        if edge is not None:
            path_edges.append(edge)
        curr = prev_node

    path_nodes.reverse()
    path_edges.reverse()

    total_dist = sum(e.distance_meters for e in path_edges)
    total_dur = sum(e.free_flow_time_seconds for e in path_edges)
    roads = []
    for e in path_edges:
        if e.road_name and e.road_name not in roads:
            roads.append(e.road_name)
    is_acc = all(e.is_accessible for e in path_edges)

    return (path_nodes, total_dist, total_dur, roads, is_acc)
