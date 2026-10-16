# PROJECT AUDIT: CampusAegis 2.0
## An AI-Powered, Real-Time Adaptive Navigation and Multi-Objective Route Optimization System

**Audit Date:** 2026-10-14  
**Auditor:** Senior Systems & Algorithm Architect  
**Project Name:** CampusAegis 2.0  
**Tagline:** Smarter Routes. Adaptive Decisions. Better Journeys.  

---

## 1. Executive Summary

CampusAegis 2.0 is transitioning from an emergency-evacuation prototype into an **intelligent, real-time adaptive navigation and multi-objective route optimization platform**. The system's primary mission is daily and regional geographic journey optimization—finding optimal paths, comparing distinct alternatives, balancing travel time versus distance versus accessibility, monitoring journeys in real time, and dynamically recalculating routes when traffic or road restrictions change.

All disaster/emergency hazard simulator artifacts (fires, earthquakes, gas plumes, panic protocols) are being removed from the primary navigation interface. Instead, the platform focuses on standard, robust transportation intelligence: verified road restrictions, construction/lane closures, congestion updates, multi-criteria route scoring, and truthful data provenance.

---

## 2. Inventory of Existing Codebase

### Entry Points & Core Application
- **`app.py`**: Streamlit responsive web application. Previously contained emergency-evacuation HUD banners, hazard injection tools, and disaster scenarios.
  - *Action:* Refactor into a clean, modern navigation interface featuring:
    1. Interactive real-world Leaflet map with multi-route overlays.
    2. Multi-Objective Route Optimization panel (Fastest, Shortest, Balanced, Accessible).
    3. Live journey tracking (movement kinematics, velocity, heading, breadcrumbs).
    4. Autonomous navigation notifications (traffic delays, faster bypass suggestions, restriction updates).
    5. Situational Algorithm Benchmark with dynamic trade-off explanations.
- **`run.bat`**: Windows quick-launch script for the Streamlit web server.

### Geospatial & Routing Layer (`src/`)
- **`route_engine.py`**: Queries OpenStreetMap OSRM live routing API with autonomous high-fidelity regional synthetic road curves for offline execution. Supports driving and walking profiles, distance, duration, and turn summaries.
  - *Status:* Working and verified. Will be extended with multi-objective route scoring and custom cost weighting.
- **`map_service.py`**: Folium Leaflet map renderer. Previously rendered hazard circles and emergency barricades.
  - *Action:* Remove hazard styling; replace with road restriction icons (maintenance, roadwork, toll indicators), multi-route color coding (Primary Emerald, Alternative Cyan, Congested Amber), and traveler breadcrumbs.
- **`location_service.py`**: Live GPS coordinate tracker, accuracy filters, staleness detection, and real movement kinematics ($v = \Delta d / \Delta t$, forward azimuth bearing $\theta$, cardinal headings).
  - *Status:* Working and fully verified.
- **`notification_service.py`**: Event-driven notification manager with delivery lifecycle states (`GENERATED`, `QUEUED`, `SUBMISSION_ACCEPTED`, `USER_ACKNOWLEDGED`).
  - *Action:* Shift event taxonomy from disaster alarms to navigation notifications (e.g., `FASTER_ROUTE_AVAILABLE`, `CONGESTION_DETECTED`, `ROAD_RESTRICTION_AHEAD`, `ROUTE_RECALCULATED`).

### Optimization & Algorithm Engine (`src/`)
- **`search_engine.py` & `campus_graph.py`**: Graph-based pathfinding implementing A* Search, Dijkstra's algorithm, and Greedy Best-First Search on 3D topological networks.
  - *Status:* Formally tested and working. Provides baseline optimality verification.
- **`adaptive_algorithm_selector.py`**: Evaluates travel parameters (distance, road restrictions, in-transit state) to recommend the optimal algorithm (Safety A*, Bidirectional A*, Yen's K-Shortest, D* Lite).
  - *Action:* Refactor rationale text to remove hazard language and emphasize routing performance, compute latency, and multi-route alternatives.

### Legacy Hazard Modules (To be decoupled or removed from active UI)
- `src/hazard_data_model.py`, `src/hazard_source_manager.py`, `src/simulation_engine.py`, `src/hazard_mode_manager.py`, `src/hazard_map.py`: Implemented real USGS and simulated hazard feeds.
  - *Decision:* Decouple from primary UI and routing pipeline. Replace with `RoadConditionManager` managing verified road closures, construction zones, and traffic delays without disaster terminology.

---

## 3. Implemented Architecture: The Three Operating Modes

To guarantee truthful data provenance and zero fabricated observations:

1. **Mode A: Live Routing Mode**
   - Ingests actual OSM geographic road networks and live OSRM routing.
   - Uses real travel-time calculations.
   - Status clearly marked: `Using OSRM Live Road Network`.
2. **Mode B: Standard Routing Mode**
   - High-fidelity offline graph routing when external routing servers are unreachable or rate-limited.
   - Status clearly marked: `Standard Routing Mode (Local Road Graph)`.
3. **Mode C: Controlled Demonstration Mode**
   - Repeatable scenarios for presentations, algorithm evaluation, and testing.
   - Clearly labeled with persistent `DEMO DATA — NOT LIVE` indicator.
   - Scenarios:
     - Scenario 1: Nominal Transit (Compare Fastest vs Shortest).
     - Scenario 2: Traffic Congestion on Arterial Highway (Dynamic Reroute).
     - Scenario 3: Road Maintenance Closure (Bypass Selection).
     - Scenario 4: Multi-Objective Weight Shift (Preference Tuning).
     - Scenario 5: In-Transit Rerouting (Live Journey Recalculation).
     - Scenario 6: All Access Routes Closed (Destination Unreachable).
     - Scenario 7: Wheelchair Accessible Routing Constraint.
     - Scenario 8: Provider Timeout & Graceful Local Fallback.

---

## 4. Multi-Objective Scoring Model

Routes are ranked according to a normalized cost function:

$$\text{Score}(R) = w_{\text{time}} \cdot \left(\frac{T(R)}{T_{\min}}\right) + w_{\text{dist}} \cdot \left(\frac{D(R)}{D_{\min}}\right) + P_{\text{preference}}(R) + P_{\text{restriction}}(R)$$

Where:
- $\tilde{T} = T(R) / T_{\min}$ is the normalized travel time.
- $\tilde{D} = D(R) / D_{\min}$ is the normalized distance.
- $w_{\text{time}}, w_{\text{dist}}$ sum to $1.0$.
- Hard restrictions (closures, non-accessible segments when accessibility is required) assign an infinite cost, disqualifying the route.
