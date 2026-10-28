# NexRoute Implementation Roadmap

**Version:** 2.0  
**Status:** In Execution  
**Target:** Production-grade Intelligent Navigation Engine  

---

## 1. Roadmap Architecture

The NexRoute overhaul is structured across 6 targeted execution phases. Each phase establishes clean, test-driven interfaces and eliminates legacy mocks or shortcuts.

```
+--------------------------------------------------------------------------------+
| PHASE 1: Audit & Discovery (Completed)                                         |
| -> Architecture audit, limitation catalog, and dependency map                 |
+--------------------------------------------------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
| PHASE 2: Core Multi-Objective Routing Engine (Current)                         |
| -> Refactor src/routing/ modules                                               |
| -> Dijkstra reference, Admissible A*, Bidirectional A* termination             |
| -> Generic Yen's K-Shortest Loopless Paths (eliminate hardcoded node blocks)   |
| -> 3-State Accessibility Engine (Verified, Inaccessible, Unknown)              |
| -> Normalized multi-objective scoring (Fastest, Shortest, Balanced)           |
+--------------------------------------------------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
| PHASE 3: Geographic Data, Providers & Live Traffic                             |
| -> Unified BaseRoutingProvider contract (OSRM, local graph, hybrid)           |
| -> Transparent data source tagging and offline boundary detection             |
| -> Eliminate fake synthetic routes (no duplicate polylines with 1.04x dist)   |
| -> Real-time traffic integration contract with fallback confidence levels     |
+--------------------------------------------------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
| PHASE 4: Dynamic Replanning & Detour Engine                                    |
| -> Spatial bounding box / polygon road block excision                         |
| -> Genuine corridor detours around incidents                                  |
| -> D* Lite incremental cost propagation on local graphs                        |
+--------------------------------------------------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
| PHASE 5: User Experience, AURA 3D & Multilingual Localization                  |
| -> Synchronized route card selection & polyline highlight                     |
| -> Smooth Three.js AURA companion animations                                   |
| -> Full localization across 8 supported Indian languages                      |
+--------------------------------------------------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
| PHASE 6: Testing, Benchmarking & Deployment Readiness                          |
| -> 100% test pass rate across all 521+ automated tests                        |
| -> Algorithm performance benchmarks (runtime ms, node expansions)              |
| -> Docker & production service configuration                                   |
+--------------------------------------------------------------------------------+
```

---

## 2. Phase-by-Phase Execution Details

### Phase 2: Core Routing Engine Refactoring
- **Goal:** Replace brittle, coupled routing code with modular algorithms backed by rigorous mathematical guarantees.
- **Key Modules in `src/routing/`:**
  - `graph.py`: Node, Edge, and Graph definitions with non-negative weight checks.
  - `costs.py`: Configurable edge weight models (Time, Distance, Accessibility penalties).
  - `dijkstra.py`: Reference shortest-path implementation with heap priority queue.
  - `astar.py`: A* with Euclidean/Haversine heuristic lower bound and verified Bidirectional A*.
  - `alternatives.py`: Loopless Yen's K-Shortest Paths without hardcoded coordinate assumptions.
  - `accessibility.py`: Constraint-based route verification with 3 states: `VERIFIED_ACCESSIBLE`, `VERIFIED_INACCESSIBLE`, `UNKNOWN`.
  - `ranking.py`: Multi-objective score function:
    $$\text{Score}(r) = \alpha \cdot \frac{T(r) - T_{\min}}{T_{\max} - T_{\min} + \epsilon} + \beta \cdot \frac{D(r) - D_{\min}}{D_{\max} - D_{\min} + \epsilon}$$
- **Verification Criteria:**
  - Zero test failures in `tests/test_route_alternatives_geometry.py`.
  - Dijkstra and A* produce identical shortest-path distances on identical graphs.

### Phase 3: Real-World Geographic Data & Traffic Providers
- **Goal:** Clean separation between graph algorithms and external navigation services (OSRM).
- **Actions:**
  - Clean up dead code in `src/backend/routing/osrm_provider.py`.
  - Fix local regional fallback in `src/route_engine.py`: Never let a coarse 14-node regional graph overwrite or preempt a successful global OSRM route.
  - Eliminate fake synthetic alternatives in `src/backend/routing/advanced_router.py` (which multiplied polyline lengths by 1.04/1.08 over identical coordinates).
- **Verification Criteria:**
  - A single distinct route returned by OSRM remains a single distinct route without fabricated duplicates.

### Phase 4: Dynamic Replanning & Detour Engine
- **Goal:** Real-world incident avoidance and true incremental graph replanning.
- **Actions:**
  - Implement spatial road-hazard intersection in `dynamic_rerouter.py`: excise segments within the hazard radius.
  - Re-route around blocked segments via spatial spur points or secondary waypoint routing rather than returning the blocked polyline with a distance multiplier.
- **Verification Criteria:**
  - Detour polyline never intersects the hazard buffer zone.

### Phase 5: AI Travel Assistance & AURA 3D Companion
- **Goal:** Seamless integration of LLM journey summaries and responsive 3D WebGL avatar.
- **Actions:**
  - Verify Ollama client fallback to structured rules when offline.
  - Ensure AURA canvas properly resizes and responds to navigation milestones.
  - Confirm localized strings for all 8 target languages (en, te, hi, ta, kn, ml, bn, mr).

### Phase 6: QA, Benchmarking & Deployment
- **Goal:** Absolute reliability and transparent performance metrics.
- **Actions:**
  - Benchmark Dijkstra vs A* vs Bidirectional A* runtime and node visits.
  - Run the entire test suite (521+ tests) with zero failures.
