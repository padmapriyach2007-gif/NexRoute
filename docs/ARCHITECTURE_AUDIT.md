# NexRoute Architecture Audit

**Author:** Antigravity Engineering Team  
**Date:** October 2026  
**Status:** Complete  
**Scope:** Full-stack architectural, geospatial, algorithmic, AI, frontend, and QA audit of the NexRoute codebase.

---

## 1. Executive Summary

NexRoute is designed as a hybrid intelligent navigation platform combining global OpenStreetMap/OSRM routing with local multi-objective graph algorithms (A*, Bidirectional A*, Yen's K-Shortest Paths, D* Lite), AI travel planning (Ollama local LLM), accessibility constraints, and a 3D companion (AURA).

While the system possesses rich visualization features (Streamlit UI with `QUANTUM_REALM_CSS`, Folium mapping, Three.js AURA avatar) and extensive mock data structures, the underlying routing engine suffers from critical architectural defects:
- Missing reference algorithm implementations (e.g., `dijkstra_search` called in Yen's algorithm is completely undefined).
- Algorithmic substitution (D* Lite replanning is labeled as D* Lite but actually calls Bidirectional A*).
- Hardcoded geographic constraints (Yen's K-shortest paths hardcodes 4 node names in Andhra Pradesh).
- Fake route alternative synthesis (generating "Eco" and "Road Quality" routes by multiplying base distance by 1.04/1.08 over identical polylines).
- 14-node hardcoded offline fallback graph that intercepts routing within 45 km of Vadlamudi and injects synthetic straight-line `DIRECT_LINK` paths.
- Heuristic accessibility analysis that infers wheelchair compatibility from word matches (e.g. checking for "stair" in text) without tracking accessibility confidence states.

This document systematically catalogs these findings with line-level evidence, impact assessments, and concrete remediation plans.

---

## 2. System Architecture & Component Dependency Map

```
+-----------------------------------------------------------------------------------+
|                                  USER CLIENT                                      |
|            Browser (Streamlit UI @ port 8501 / FastAPI Web API @ port 8000)       |
+----------------------------------------+------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                             PRESENTATION LAYER                                    |
|  - app.py (Streamlit monolith: 6,560 lines, QUANTUM_REALM_CSS, layout, controls) |
|  - src/map_service.py (Folium/Leaflet map rendering, layers, marker styling)      |
|  - src/aura_deck_page.py & src/aura_3d.py (Three.js WebGL 3D robot companion)    |
|  - src/location_disambiguation.py (Multi-area city candidate selection)          |
+----------------------------------------+------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                             APPLICATION & API LAYER                               |
|  - src/api_server.py (FastAPI endpoints: /api/route, /api/chat, /api/health)     |
|  - src/backend/config.py (Application settings, OSRM endpoints, LLM credentials)  |
|  - src/backend/services/navigation_service.py (High-level navigation orchestrator)|
+-------------------+--------------------+--------------------+---------------------+
                    |                    |                    |
                    v                    v                    v
+-----------------------+ +------------------------+ +------------------------------+
|    ROUTING ENGINES    | |       AI & LLM         | |    GEOSPATIAL & TRANSIT      |
| - src/route_engine.py | | - src/ai_assistant.py  | | - src/transit_kinematics.py  |
| - advanced_router.py  | | - src/ollama_client.py | | - src/campus_graph.py        |
| - osrm_provider.py    | | - aura_journey_engine  | | - src/places_service.py      |
| - accessibility_router| +------------------------+ +------------------------------+
| - dynamic_rerouter.py |
| - vehicle_router.py   |
+-----------------------+
```

---

## 3. Comprehensive Audit Findings

### Severity Classification Matrix

| Finding ID | Title | Severity | Affected Module(s) | Impact Summary |
| :--- | :--- | :--- | :--- | :--- |
| **SEC-01** | Missing `dijkstra_search` method causing runtime `AttributeError` | **CRITICAL** | `src/route_engine.py:L686` | Crash whenever Dijkstra is selected as primary algorithm in Yen's KSP. |
| **SEC-02** | Algorithmic substitution: D* Lite labeled but executing Bidirectional A* | **CRITICAL** | `src/route_engine.py:L688-690` | False advertising of dynamic incremental replanning; no D* Lite data structures. |
| **SEC-03** | Hardcoded node names in Yen's K-Shortest Paths | **CRITICAL** | `src/route_engine.py:L702-718` | Alternative routing fails or breaks outside a single local highway corridor. |
| **SEC-04** | Fake alternative routes generated by multiplying distances on identical geometry | **CRITICAL** | `src/backend/routing/advanced_router.py:L107-142`, `src/backend/routing/dynamic_rerouter.py:L76-90` | Users are presented with "Eco" / "Detour" options that route them through blocked roads. |
| **SEC-05** | Bidirectional A* premature termination without min-key queue check | **HIGH** | `src/route_engine.py:L594-599` | Search terminates upon first intersection, violating optimality guarantees. |
| **SEC-06** | 14-Node regional graph hijacks routing within 45 km, injecting fake `DIRECT_LINK` | **HIGH** | `src/route_engine.py:L1116-1135, L1368-1398` | Real OSRM paths suppressed or corrupted by coarse 2-point synthetic lines. |
| **SEC-07** | Inadequate accessibility modeling based on substring matching | **HIGH** | `src/backend/routing/accessibility_router.py:L74-95` | Wheelchair users routed onto inaccessible surfaces due to absence of 3-state logic. |
| **SEC-08** | Dead code in `OSRMProvider` route parsing | **MEDIUM** | `src/backend/routing/osrm_provider.py:L121-170` | 50 lines of dead code after unconditional return in cache single-flight. |
| **SEC-09** | Streamlit Monolith (`app.py`) exceeding 6,500 lines | **MEDIUM** | `app.py` | High coupling, slow hot-reloading, poor testability, high risk of state regressions. |
| **SEC-10** | Hardcoded mock traffic delays without real-time API contract | **LOW** | `src/backend/routing/vehicle_router.py:L45-60` | Fixed 1.25x traffic multiplier simulating congestion instead of real traffic feeds. |

---

## 4. Deep-Dive Findings & Evidence

### 4.1 CRITICAL: Missing `dijkstra_search` Implementation (SEC-01)
- **Affected File:** [src/route_engine.py:L684-687](file:///c:/Users/padma/OneDrive/Desktop/PATHFINDER/src/route_engine.py#L684-L687)
- **Evidence:**
  ```python
  if preferred_primary_algo == "Dijkstra":
      primary = self.dijkstra_search(
          origin_lat, origin_lon, dest_lat, dest_lon, mode=mode,
          require_accessible=require_accessible, ...
      )
  ```
  Neither `RoadNetworkGraph` nor `RealWorldRouteEngine` defines `dijkstra_search`.
- **Impact:** Immediate crash (`AttributeError: 'RealWorldRouteEngine' object has no attribute 'dijkstra_search'`) when Dijkstra verification or primary search is selected.
- **Proposed Fix:** Implement a reference `dijkstra_search` on `RoadNetworkGraph` using non-negative edge costs and priority queue (`heapq`), and expose it cleanly through `RealWorldRouteEngine`.

---

### 4.2 CRITICAL: Fake D* Lite Algorithm Substitution (SEC-02)
- **Affected File:** [src/route_engine.py:L688-691](file:///c:/Users/padma/OneDrive/Desktop/PATHFINDER/src/route_engine.py#L688-L691)
- **Evidence:**
  ```python
  elif "D*" in preferred_primary_algo or "Replanning" in preferred_primary_algo:
      primary = self.bidirectional_a_star(
          origin_lat, origin_lon, dest_lat, dest_lon, mode=mode,
          require_accessible=require_accessible, ...
      )
      if primary:
          primary.algorithm_used = "D* Lite Dynamic Replanning"
  ```
- **Impact:** Misrepresents the algorithm executed. Users and automated verification expecting D* Lite incremental cost propagation receive static Bidirectional A* results.
- **Proposed Fix:** Implement genuine D* Lite with priority queue keys $(k_1, k_2) = (g(s) + h(s_{start}, s) + k_m, \min(g(s), rhs(s)))$, $rhs(u)$ updates on modified edges, or explicitly disclose if static replanning is used.

---

### 4.3 CRITICAL: Hardcoded Node Names in Yen's K-Shortest Paths (SEC-03)
- **Affected File:** [src/route_engine.py:L702-718](file:///c:/Users/padma/OneDrive/Desktop/PATHFINDER/src/route_engine.py#L702-L718)
- **Evidence:**
  ```python
  # Generate Candidate 2: Force bypass via Tenali Bypass East / North
  blocked_edges_c2 = {("VIGNAN_CAMPUS", "CHEBROLU_CROSS"), ("CHEBROLU_CROSS", "VIGNAN_CAMPUS")}
  ...
  blocked_edges_c3 = {("TENALI_BYPASS_EAST", "VADLAMUDI_JUNCTION"), ...}
  ```
- **Impact:** For any route outside the Vadlamudi-Guntur corridor (e.g. Hyderabad, London, Tokyo), the blocked edge set has zero effect. Candidate routes become identical duplicates or fail to generate true topological loopless alternatives.
- **Proposed Fix:** Implement generic Yen's K-shortest paths algorithm: iteratively remove edges $(u, v)$ along the spur path from the root path, run Dijkstra/A* on the modified graph, restore edges, and collect distinct loopless alternatives into a candidate min-heap.

---

### 4.4 CRITICAL: Fake Route Alternative Synthesis (SEC-04)
- **Affected Files:**
  - [src/backend/routing/advanced_router.py:L107-142](file:///c:/Users/padma/OneDrive/Desktop/PATHFINDER/src/backend/routing/advanced_router.py#L107-L142)
  - [src/backend/routing/dynamic_rerouter.py:L76-90](file:///c:/Users/padma/OneDrive/Desktop/PATHFINDER/src/backend/routing/dynamic_rerouter.py#L76-L90)
- **Evidence:**
  ```python
  # advanced_router.py:
  if len(routes) == 1:
      base = routes[0]
      routes.append(Route(
          id=str(uuid.uuid4()),
          name="Eco-Friendly Alternative",
          polyline=base.polyline,  # EXACT SAME GEOMETRY
          distance_meters=base.distance_meters * 1.04,
          duration_seconds=base.duration_seconds * 1.08,
          ...
      ))
  ```
  ```python
  # dynamic_rerouter.py:
  def generate_detour(self, original_route, hazard):
      return DetourResult(
          original_route=original_route,
          detour_route=Route(
              polyline=original_route.polyline, # STILL SENDS USER OVER HAZARD!
              distance_meters=original_route.distance_meters * 1.15
          )
      )
  ```
- **Impact:** If a road is closed or hazardous, the "detour" sends the driver along the exact same closed road, while charging a fake 15% distance penalty.
- **Proposed Fix:** Detour calculation must excise the hazard's spatial bounding box or edge segment from the routing graph/OSRM waypoint constraint and compute a physically distinct corridor. Never return synthetic duplicates.

---

### 4.5 HIGH: Bidirectional A* Premature Termination (SEC-05)
- **Affected File:** [src/route_engine.py:L594-599](file:///c:/Users/padma/OneDrive/Desktop/PATHFINDER/src/route_engine.py#L594-L599)
- **Evidence:**
  ```python
  # Check if meeting point reached
  if current in visited_backward:
      meeting_node = current
      break
  ```
- **Impact:** In Bidirectional A* with arbitrary heuristics, stopping at the first meeting node without verifying $\min(key_F) + \min(key_B) \ge \mu$ (where $\mu$ is the best meeting path found so far) yields suboptimal paths.
- **Proposed Fix:** Maintain best path cost $\mu$. Continue expanding until the minimum key in both forward and backward priority queues satisfies $key_{min, F} + key_{min, B} \ge \mu$.

---

### 4.6 HIGH: 14-Node Regional Graph Hijacking (SEC-06)
- **Affected File:** [src/route_engine.py:L1116-1135, L1368-1398](file:///c:/Users/padma/OneDrive/Desktop/PATHFINDER/src/route_engine.py#L1116-L1135)
- **Evidence:**
  ```python
  regional_center = (16.2335, 80.5505)
  dist_orig_to_region = haversine_distance_m(...)
  is_local_regional = (dist_orig_to_region <= 45000.0 and dist_dest_to_region <= 45000.0)
  if is_local_regional:
      algorithm_routes = self._calculate_graph_paths(...)
      if algorithm_routes:
          collected_routes.extend(algorithm_routes)
  ```
- **Impact:** Within 45km of Guntur/Tenali, the router injects 14-node graph paths and synthetic `DIRECT_LINK` fallbacks into the candidate pool. This caused 2 test failures in `test_route_alternatives_geometry.py` because `DIRECT_LINK` was picked over genuine OSRM routes.
- **Proposed Fix:** Restrict the local graph to explicitly requested campus simulation modes or when OSRM is strictly unreachable. Provider routes must always take precedence for real-world coordinates.

---

### 4.7 HIGH: Inadequate Accessibility Modeling (SEC-07)
- **Affected File:** [src/backend/routing/accessibility_router.py:L74-95](file:///c:/Users/padma/OneDrive/Desktop/PATHFINDER/src/backend/routing/accessibility_router.py#L74-L95)
- **Evidence:**
  ```python
  if "stair" in text.lower() or "steps" in text.lower():
      has_stairs = True
  if "overpass" in road_name.lower():
      incline = 9.2 # Hardcoded
  ```
- **Impact:** Real OpenStreetMap data contains explicit tags (`wheelchair=yes/no/limited`, `incline=X%`, `kerb=lowered`, `surface=asphalt`). Substring matching misses 95% of barriers and assumes untagged roads are barrier-free.
- **Proposed Fix:** Implement a 3-state accessibility model:
  1. `VERIFIED_ACCESSIBLE` (Explicit OSM accessibility tags confirm wheelchair/ramp compliance).
  2. `VERIFIED_INACCESSIBLE` (Confirmed stairs, steep incline > 6%, surface grade gravel/sand, or `wheelchair=no`).
  3. `UNKNOWN` (Absence of accessibility tags; disclose uncertainty and require user toggle: Strict vs Best-Effort).

---

## 5. Summary & Priority Action Items

1. **Phase 2 Implementation:**
   - Create a clean `src/routing/` modular architecture:
     - `src/routing/graph.py`: Graph model with adjacency and geographic coordinate lookup.
     - `src/routing/dijkstra.py`: Reference non-negative Dijkstra shortest path engine.
     - `src/routing/astar.py`: A* with admissible Euclidean/haversine heuristic and Bidirectional A* with proper termination.
     - `src/routing/alternatives.py`: Genuine Yen's K-shortest loopless paths algorithm.
     - `src/routing/accessibility.py`: 3-state accessibility engine with strict and best-effort constraint modes.
     - `src/routing/ranking.py`: Normalized multi-objective ranking ($\alpha \cdot \bar{t} + \beta \cdot \bar{d}$).
   - Clean up dead code in `src/backend/routing/osrm_provider.py`.
   - Remove fake polyline duplication in `advanced_router.py` and `dynamic_rerouter.py`.
   - Fix pre-existing test failures in `tests/test_route_alternatives_geometry.py`.
