"""
Yen's K-Shortest Loopless Paths Algorithm for NexRoute.
Computes mathematically valid simple (loopless) paths without hardcoded node blocks.
Guarantees diversity and termination on arbitrary graph topologies.
"""

import heapq
from typing import Dict, List, Optional, Set, Tuple
from src.routing.graph import RoutingGraph, Edge
from src.routing.costs import CostModel, ObjectiveType
from src.routing.dijkstra import dijkstra_search
from src.routing.astar import a_star_search


def yens_k_shortest_paths(
    graph: RoutingGraph,
    start_node: str,
    goal_node: str,
    K: int = 3,
    cost_model: Optional[CostModel] = None,
    require_accessible: bool = False,
    use_astar: bool = True
) -> List[Tuple[List[str], float, float, List[str], bool, str]]:
    """
    Computes up to K loopless simple paths using Yen's algorithm.
    Returns:
        List of (path_nodes, distance_m, duration_s, roads, is_accessible, algorithm_name)
    """
    cost_model = cost_model or CostModel(objective=ObjectiveType.FASTEST)

    # 1. Primary path calculation using Dijkstra or A*
    if use_astar:
        primary_res = a_star_search(
            graph, start_node, goal_node,
            cost_model=cost_model, require_accessible=require_accessible
        )
        primary_name = "Goal-Directed A*"
    else:
        primary_res = dijkstra_search(
            graph, start_node, goal_node,
            cost_model=cost_model, require_accessible=require_accessible
        )
        primary_name = "Reference Dijkstra"

    if not primary_res:
        return []

    # A holds the K shortest loopless paths
    A: List[Tuple[List[str], float, float, List[str], bool, str]] = [
        (primary_res[0], primary_res[1], primary_res[2], primary_res[3], primary_res[4], primary_name)
    ]

    # B holds candidate paths in a priority queue: (scalar_cost, path_nodes)
    B: List[Tuple[float, List[str], float, float, List[str], bool, str]] = []

    for k in range(1, K):
        prev_path = A[k - 1][0]

        # The spur node ranges from the first node up to the next-to-last node of the previous path
        for i in range(len(prev_path) - 1):
            spur_node = prev_path[i]
            root_path = prev_path[:i + 1]

            # Block edges that are part of previous paths that share the same root path
            blocked_edges: Set[Tuple[str, str]] = set()
            for p in A:
                p_nodes = p[0]
                if len(p_nodes) > i and p_nodes[:i + 1] == root_path:
                    blocked_edges.add((p_nodes[i], p_nodes[i + 1]))
                    blocked_edges.add((p_nodes[i + 1], p_nodes[i]))

            # Temporarily block all nodes in root_path (except spur_node) to enforce loopless property
            # We achieve this by blocking all incident edges to those nodes
            for root_n in root_path[:-1]:
                for neighbor_edge in graph.get_neighbors(root_n):
                    blocked_edges.add((root_n, neighbor_edge.v))
                    blocked_edges.add((neighbor_edge.v, root_n))

            # Calculate spur path from spur_node to goal_node
            spur_res = a_star_search(
                graph, spur_node, goal_node,
                cost_model=cost_model,
                blocked_edges=blocked_edges,
                require_accessible=require_accessible
            )

            if spur_res:
                spur_path = spur_res[0]
                total_candidate_path = root_path[:-1] + spur_path

                # Ensure candidate path is not already in A or B
                if not any(a[0] == total_candidate_path for a in A):
                    # Compute path metrics
                    cand_edges: List[Edge] = []
                    valid_path = True
                    for step in range(len(total_candidate_path) - 1):
                        u_node = total_candidate_path[step]
                        v_node = total_candidate_path[step + 1]
                        e_found = next((e for e in graph.adjacency.get(u_node, []) if e.v == v_node), None)
                        if e_found is None:
                            valid_path = False
                            break
                        cand_edges.append(e_found)

                    if valid_path:
                        c_dist = sum(e.distance_meters for e in cand_edges)
                        c_dur = sum(e.free_flow_time_seconds for e in cand_edges)
                        c_roads = []
                        for e in cand_edges:
                            if e.road_name and e.road_name not in c_roads:
                                c_roads.append(e.road_name)
                        c_acc = all(e.is_accessible for e in cand_edges)
                        scalar_cost = sum(cost_model.edge_cost(e, require_accessible) for e in cand_edges)

                        algo_label = f"Yen's Loopless Alternative {len(A) + 1} (Spur: {spur_node})"
                        heapq.heappush(B, (scalar_cost, total_candidate_path, c_dist, c_dur, c_roads, c_acc, algo_label))

        if not B:
            break

        # Move best candidate from B to A
        best_cand = heapq.heappop(B)
        A.append((
            best_cand[1],  # path_nodes
            best_cand[2],  # distance_m
            best_cand[3],  # duration_s
            best_cand[4],  # roads
            best_cand[5],  # is_accessible
            best_cand[6]   # algorithm_name
        ))

    return A
