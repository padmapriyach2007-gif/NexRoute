import heapq
import time
from typing import Dict, List, Tuple, Optional, Set
from src.campus_graph import CampusNode, build_campus_building

class SearchResult:
    def __init__(
        self,
        algorithm: str,
        path: List[str],
        cost: float,
        nodes_explored: int,
        latency_ms: float,
        explored_order: List[str],
        is_accessible: bool = True,
        estimated_time_seconds: float = 0.0
    ):
        self.algorithm = algorithm
        self.path = path
        self.cost = cost
        self.nodes_explored = nodes_explored
        self.latency_ms = latency_ms
        self.explored_order = explored_order
        self.is_accessible = is_accessible
        self.estimated_time_seconds = estimated_time_seconds
        self.success = len(self.path) > 0 and self.cost < float('inf')

    def to_dict(self):
        return {
            "algorithm": self.algorithm,
            "path": self.path,
            "cost_meters": round(self.cost, 2),
            "nodes_explored": self.nodes_explored,
            "latency_ms": round(self.latency_ms, 3),
            "path_length": len(self.path),
            "success": len(self.path) > 0,
            "is_accessible": self.is_accessible,
            "estimated_time_sec": round(self.estimated_time_seconds, 1)
        }

class EvacuationSearchEngine:
    def __init__(self):
        self.nodes, self.base_edges = build_campus_building()
        self.adjacency: Dict[str, List[Tuple[str, float]]] = {n: [] for n in self.nodes}
        self.dynamic_penalties: Dict[Tuple[str, str], float] = {}
        self.blocked_nodes: Set[str] = set()
        self.blocked_edges: Set[Tuple[str, str]] = set()
        self._rebuild_graph()

    def _rebuild_graph(self):
        self.adjacency = {n: [] for n in self.nodes}
        for u, v, weight in self.base_edges:
            w = weight
            edge_key = tuple(sorted([u, v]))
            if edge_key in self.blocked_edges:
                continue
            if edge_key in self.dynamic_penalties:
                w += self.dynamic_penalties[edge_key]
            
            self.adjacency[u].append((v, w))
            self.adjacency[v].append((u, w))

    def inject_hazard(self, node_or_edge: str, is_blocked: bool = True, penalty_meters: float = 1000.0):
        """
        Blocks or heavily penalizes a node or an edge (e.g. 'STAIR_A_F2' or 'STAIR_A_F1<->STAIR_A_F2')
        """
        if "<->" in node_or_edge:
            u, v = node_or_edge.split("<->")
            edge_key = tuple(sorted([u.strip(), v.strip()]))
            if is_blocked:
                self.blocked_edges.add(edge_key)
            else:
                self.blocked_edges.discard(edge_key)
        else:
            node_id = node_or_edge.strip()
            if is_blocked:
                self.blocked_nodes.add(node_id)
            else:
                self.blocked_nodes.discard(node_id)
        self._rebuild_graph()

    def clear_hazards(self):
        self.blocked_nodes.clear()
        self.blocked_edges.clear()
        self.dynamic_penalties.clear()
        self._rebuild_graph()

    def heuristic(self, current: str, goal: str) -> float:
        if current not in self.nodes or goal not in self.nodes:
            return 0.0
        return self.nodes[current].distance_to(self.nodes[goal])

    def _is_node_passable(self, node_id: str, requires_accessible: bool, avoid_elevators: bool) -> bool:
        if node_id in self.blocked_nodes:
            return False
        node_obj = self.nodes.get(node_id)
        if not node_obj:
            return False
        if requires_accessible and not getattr(node_obj, "is_accessible", True):
            return False
        if avoid_elevators and getattr(node_obj, "is_elevator", False):
            return False
        return True

    def _compute_path_travel_time(self, path: List[str]) -> float:
        total_time = 0.0
        for i in range(len(path) - 1):
            n1 = self.nodes.get(path[i])
            n2 = self.nodes.get(path[i+1])
            if n1 and n2:
                total_time += n1.travel_time_to(n2)
        return total_time

    def a_star_search(
        self,
        start: str,
        goal: str,
        requires_accessible: bool = False,
        avoid_elevators: bool = True
    ) -> SearchResult:
        """
        A* Search using f(n) = g(n) + h(n) with admissible 3D Euclidean heuristic.
        Supports accessibility and elevator safety constraints.
        """
        t0 = time.perf_counter()
        if not self._is_node_passable(start, requires_accessible, avoid_elevators) or \
           not self._is_node_passable(goal, requires_accessible, avoid_elevators):
            t1 = time.perf_counter()
            return SearchResult("A*", [], float('inf'), 0, (t1 - t0) * 1000.0, [], is_accessible=not requires_accessible)

        frontier: List[Tuple[float, float, str, List[str]]] = []  # (f, g, node, path)
        heapq.heappush(frontier, (self.heuristic(start, goal), 0.0, start, [start]))
        
        g_costs: Dict[str, float] = {start: 0.0}
        explored_order: List[str] = []
        visited_nodes: Set[str] = set()

        while frontier:
            f, g, current, path = heapq.heappop(frontier)

            if current in visited_nodes:
                continue
            visited_nodes.add(current)
            explored_order.append(current)

            if current == goal:
                t1 = time.perf_counter()
                travel_time = self._compute_path_travel_time(path)
                return SearchResult(
                    "A*",
                    path,
                    g,
                    len(visited_nodes),
                    (t1 - t0) * 1000.0,
                    explored_order,
                    is_accessible=all(getattr(self.nodes[p], "is_accessible", True) for p in path),
                    estimated_time_seconds=travel_time
                )

            for neighbor, weight in self.adjacency[current]:
                if not self._is_node_passable(neighbor, requires_accessible, avoid_elevators):
                    continue
                new_g = g + weight
                if neighbor not in g_costs or new_g < g_costs[neighbor]:
                    g_costs[neighbor] = new_g
                    new_f = new_g + self.heuristic(neighbor, goal)
                    heapq.heappush(frontier, (new_f, new_g, neighbor, path + [neighbor]))

        t1 = time.perf_counter()
        return SearchResult("A*", [], float('inf'), len(visited_nodes), (t1 - t0) * 1000.0, explored_order, is_accessible=False)

    def dijkstra_search(
        self,
        start: str,
        goal: str,
        requires_accessible: bool = False,
        avoid_elevators: bool = True
    ) -> SearchResult:
        """
        Dijkstra's Algorithm: Uninformed optimal search (equivalent to A* with h(n) = 0).
        """
        t0 = time.perf_counter()
        if not self._is_node_passable(start, requires_accessible, avoid_elevators) or \
           not self._is_node_passable(goal, requires_accessible, avoid_elevators):
            t1 = time.perf_counter()
            return SearchResult("Dijkstra", [], float('inf'), 0, (t1 - t0) * 1000.0, [], is_accessible=not requires_accessible)

        frontier: List[Tuple[float, str, List[str]]] = []  # (g, node, path)
        heapq.heappush(frontier, (0.0, start, [start]))
        
        g_costs: Dict[str, float] = {start: 0.0}
        explored_order: List[str] = []
        visited_nodes: Set[str] = set()

        while frontier:
            g, current, path = heapq.heappop(frontier)

            if current in visited_nodes:
                continue
            visited_nodes.add(current)
            explored_order.append(current)

            if current == goal:
                t1 = time.perf_counter()
                travel_time = self._compute_path_travel_time(path)
                return SearchResult(
                    "Dijkstra",
                    path,
                    g,
                    len(visited_nodes),
                    (t1 - t0) * 1000.0,
                    explored_order,
                    is_accessible=all(getattr(self.nodes[p], "is_accessible", True) for p in path),
                    estimated_time_seconds=travel_time
                )

            for neighbor, weight in self.adjacency[current]:
                if not self._is_node_passable(neighbor, requires_accessible, avoid_elevators):
                    continue
                new_g = g + weight
                if neighbor not in g_costs or new_g < g_costs[neighbor]:
                    g_costs[neighbor] = new_g
                    heapq.heappush(frontier, (new_g, neighbor, path + [neighbor]))

        t1 = time.perf_counter()
        return SearchResult("Dijkstra", [], float('inf'), len(visited_nodes), (t1 - t0) * 1000.0, explored_order, is_accessible=False)

    def greedy_best_first_search(
        self,
        start: str,
        goal: str,
        requires_accessible: bool = False,
        avoid_elevators: bool = True
    ) -> SearchResult:
        """
        Greedy Best-First Search: Guided purely by h(n).
        """
        t0 = time.perf_counter()
        if not self._is_node_passable(start, requires_accessible, avoid_elevators) or \
           not self._is_node_passable(goal, requires_accessible, avoid_elevators):
            t1 = time.perf_counter()
            return SearchResult("Greedy Best-First", [], float('inf'), 0, (t1 - t0) * 1000.0, [], is_accessible=not requires_accessible)

        frontier: List[Tuple[float, float, str, List[str]]] = []  # (h, g, node, path)
        heapq.heappush(frontier, (self.heuristic(start, goal), 0.0, start, [start]))
        
        explored_order: List[str] = []
        visited_nodes: Set[str] = set()

        while frontier:
            h, g, current, path = heapq.heappop(frontier)

            if current in visited_nodes:
                continue
            visited_nodes.add(current)
            explored_order.append(current)

            if current == goal:
                t1 = time.perf_counter()
                travel_time = self._compute_path_travel_time(path)
                return SearchResult(
                    "Greedy Best-First",
                    path,
                    g,
                    len(visited_nodes),
                    (t1 - t0) * 1000.0,
                    explored_order,
                    is_accessible=all(getattr(self.nodes[p], "is_accessible", True) for p in path),
                    estimated_time_seconds=travel_time
                )

            for neighbor, weight in self.adjacency[current]:
                if not self._is_node_passable(neighbor, requires_accessible, avoid_elevators):
                    continue
                if neighbor not in visited_nodes:
                    heapq.heappush(frontier, (self.heuristic(neighbor, goal), g + weight, neighbor, path + [neighbor]))

        t1 = time.perf_counter()
        return SearchResult("Greedy Best-First", [], float('inf'), len(visited_nodes), (t1 - t0) * 1000.0, explored_order, is_accessible=False)

    def run_benchmark(self, start: str, goal: str) -> Dict[str, SearchResult]:
        """
        Runs A*, Dijkstra, and Greedy Best-First on the identical problem instance for viva benchmarking.
        """
        res_astar = self.a_star_search(start, goal)
        res_dijkstra = self.dijkstra_search(start, goal)
        res_greedy = self.greedy_best_first_search(start, goal)

        return {
            "A* Search": res_astar,
            "Dijkstra": res_dijkstra,
            "Greedy Best-First": res_greedy
        }
