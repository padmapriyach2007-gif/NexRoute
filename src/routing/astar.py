"""
A* and Bidirectional A* search implementations.
Uses admissible heuristics (Haversine distance and maximum speed lower bounds)
and optimal stopping criteria for Bidirectional search.
"""

import heapq
from typing import Dict, List, Optional, Set, Tuple
from src.routing.graph import RoutingGraph, Edge
from src.routing.costs import CostModel, ObjectiveType


def a_star_search(
    graph: RoutingGraph,
    start_node: str,
    goal_node: str,
    cost_model: Optional[CostModel] = None,
    blocked_edges: Optional[Set[Tuple[str, str]]] = None,
    require_accessible: bool = False
) -> Optional[Tuple[List[str], float, float, List[str], bool]]:
    """
    Goal-directed A* search with strictly admissible lower-bound heuristic.
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

    goal_node_obj = graph.nodes[goal_node]
    h0 = cost_model.heuristic(
        graph.nodes[start_node].lat, graph.nodes[start_node].lon,
        goal_node_obj.lat, goal_node_obj.lon,
        graph=graph
    )

    # Priority queue stores: (f_score, g_score, current_node)
    frontier: List[Tuple[float, float, str]] = []
    heapq.heappush(frontier, (h0, 0.0, start_node))

    best_g: Dict[str, float] = {start_node: 0.0}
    parent: Dict[str, Tuple[Optional[str], Optional[Edge]]] = {start_node: (None, None)}

    while frontier:
        f, g, current = heapq.heappop(frontier)

        if current == goal_node:
            break

        if g > best_g.get(current, float("inf")):
            continue

        curr_obj = graph.nodes[current]
        for edge in graph.get_neighbors(current, blocked_edges=blocked_edges):
            if require_accessible and not edge.is_accessible:
                continue

            e_cost = cost_model.edge_cost(edge, require_accessible=require_accessible)
            new_g = g + e_cost

            if new_g < best_g.get(edge.v, float("inf")):
                best_g[edge.v] = new_g
                parent[edge.v] = (current, edge)
                n_obj = graph.nodes[edge.v]
                h = cost_model.heuristic(n_obj.lat, n_obj.lon, goal_node_obj.lat, goal_node_obj.lon, graph=graph)
                heapq.heappush(frontier, (new_g + h, new_g, edge.v))

    if goal_node not in parent or (parent[goal_node][0] is None and start_node != goal_node):
        return None

    # Reconstruct path
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


def bidirectional_a_star_search(
    graph: RoutingGraph,
    start_node: str,
    goal_node: str,
    cost_model: Optional[CostModel] = None,
    blocked_edges: Optional[Set[Tuple[str, str]]] = None,
    require_accessible: bool = False
) -> Optional[Tuple[List[str], float, float, List[str], bool]]:
    """
    Bidirectional A* with symmetric frontiers and guaranteed termination:
    Terminates when min_key_forward + min_key_backward >= best_path_cost (mu).
    """
    if start_node not in graph.nodes or goal_node not in graph.nodes:
        return None

    if start_node == goal_node:
        return ([start_node], 0.0, 0.0, [], True)

    cost_model = cost_model or CostModel(objective=ObjectiveType.FASTEST)
    blocked_edges = blocked_edges or set()

    start_c = graph.nodes[start_node]
    goal_c = graph.nodes[goal_node]

    # Forward search structures
    f_frontier: List[Tuple[float, float, str]] = []
    h_f0 = cost_model.heuristic(start_c.lat, start_c.lon, goal_c.lat, goal_c.lon, graph=graph)
    heapq.heappush(f_frontier, (h_f0, 0.0, start_node))
    f_g: Dict[str, float] = {start_node: 0.0}
    f_parent: Dict[str, Tuple[Optional[str], Optional[Edge]]] = {start_node: (None, None)}

    # Backward search structures
    b_frontier: List[Tuple[float, float, str]] = []
    h_b0 = cost_model.heuristic(goal_c.lat, goal_c.lon, start_c.lat, start_c.lon, graph=graph)
    heapq.heappush(b_frontier, (h_b0, 0.0, goal_node))
    b_g: Dict[str, float] = {goal_node: 0.0}
    b_parent: Dict[str, Tuple[Optional[str], Optional[Edge]]] = {goal_node: (None, None)}

    mu = float("inf")
    meeting_node: Optional[str] = None

    while f_frontier and b_frontier:
        # Check termination condition: if min f in both queues exceeds mu, optimal path found
        min_f_forward = f_frontier[0][0]
        min_f_backward = b_frontier[0][0]
        if min_f_forward >= mu and min_f_backward >= mu:
            break

        # Expand forward step
        _, curr_fg, u = heapq.heappop(f_frontier)
        if curr_fg <= f_g.get(u, float("inf")):
            for edge in graph.get_neighbors(u, blocked_edges=blocked_edges):
                if require_accessible and not edge.is_accessible:
                    continue
                v = edge.v
                tentative_g = curr_fg + cost_model.edge_cost(edge, require_accessible=require_accessible)
                if tentative_g < f_g.get(v, float("inf")):
                    f_g[v] = tentative_g
                    f_parent[v] = (u, edge)
                    h_v = cost_model.heuristic(graph.nodes[v].lat, graph.nodes[v].lon, goal_c.lat, goal_c.lon, graph=graph)
                    heapq.heappush(f_frontier, (tentative_g + h_v, tentative_g, v))
                    if v in b_g:
                        path_cost = tentative_g + b_g[v]
                        if path_cost < mu:
                            mu = path_cost
                            meeting_node = v

        # Expand backward step
        _, curr_bg, w = heapq.heappop(b_frontier)
        if curr_bg <= b_g.get(w, float("inf")):
            # In reverse adjacency, edge.u is incoming neighbor to w
            for edge in graph.get_neighbors(w, blocked_edges=blocked_edges, reverse=True):
                if require_accessible and not edge.is_accessible:
                    continue
                v = edge.u
                tentative_g = curr_bg + cost_model.edge_cost(edge, require_accessible=require_accessible)
                if tentative_g < b_g.get(v, float("inf")):
                    b_g[v] = tentative_g
                    b_parent[v] = (w, edge)
                    h_v = cost_model.heuristic(graph.nodes[v].lat, graph.nodes[v].lon, start_c.lat, start_c.lon, graph=graph)
                    heapq.heappush(b_frontier, (tentative_g + h_v, tentative_g, v))
                    if v in f_g:
                        path_cost = f_g[v] + tentative_g
                        if path_cost < mu:
                            mu = path_cost
                            meeting_node = v

    if meeting_node is None:
        # Fallback to standard A* if queues exhaust without meeting
        return a_star_search(graph, start_node, goal_node, cost_model, blocked_edges, require_accessible)

    # Reconstruct forward path from start to meeting_node
    f_path_nodes: List[str] = []
    f_edges: List[Edge] = []
    curr = meeting_node
    while curr is not None:
        f_path_nodes.append(curr)
        prev_node, edge = f_parent.get(curr, (None, None))
        if edge is not None:
            f_edges.append(edge)
        curr = prev_node
    f_path_nodes.reverse()
    f_edges.reverse()

    # Reconstruct backward path from meeting_node to goal
    b_path_nodes: List[str] = []
    b_edges: List[Edge] = []
    curr = meeting_node
    while curr != goal_node:
        next_node, edge = b_parent.get(curr, (None, None))
        if next_node is None or edge is None:
            break
        b_path_nodes.append(next_node)
        b_edges.append(edge)
        curr = next_node

    full_path_nodes = f_path_nodes + b_path_nodes
    full_edges = f_edges + b_edges

    total_dist = sum(e.distance_meters for e in full_edges)
    total_dur = sum(e.free_flow_time_seconds for e in full_edges)
    roads = []
    for e in full_edges:
        if e.road_name and e.road_name not in roads:
            roads.append(e.road_name)
    is_acc = all(e.is_accessible for e in full_edges)

    return (full_path_nodes, total_dist, total_dur, roads, is_acc)
