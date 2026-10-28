# NexRoute Known Limitations & Operational Constraints

**Version:** 2.0  
**Status:** Public Technical Disclosure  

---

## 1. Overview & Policy on Truth in Capability

NexRoute prioritizes mathematical and empirical honesty. Navigation products often obscure limitations behind opaque confidence scores or simulated alternatives. This document discloses the exact boundaries of NexRoute's current data sources, algorithms, offline coverage, and hardware dependencies.

---

## 2. Geographic & Routing Data Limitations

### 2.1 Public OSRM Service Constraints
- **Data Source:** OpenStreetMap global planet extract processed by the public OSRM demo server (`router.project-osrm.org`).
- **Rate Limits & Availability:** The public OSRM demo server enforces request rate limits (typically ~1 request per second with throttling on high bursts). In production deployments, NexRoute must connect to a dedicated, self-hosted OSRM backend via `OSRM_BASE_URL`.
- **Turn Restrictions & Real-Time Closures:** Turn restrictions reflect the OSM database at the time of the latest tile build (weekly or monthly). Emergency construction closures and temporary traffic diversions are not in the OSM base tiles unless provided via live incident feeds.

### 2.2 Offline Operation & Regional Graph Bounds
- **Built-in Offline Graph:** The embedded graph in `src/route_engine.py` represents a selected regional road network (Andhra Pradesh / Guntur / Tenali corridor) containing ~14 core junctions and campus nodes.
- **Global Offline Routing:** NexRoute cannot route offline across arbitrary global coordinates (e.g., Paris or New York) without either:
  1. An active network connection to an OSRM instance.
  2. A locally installed OSRM routing server with the relevant `.osrm` binary tiles.
- **System Behavior:** When outside the local graph bounds without OSRM connectivity, NexRoute explicitly reports `RoutingOfflineError` or `NoRouteFoundError` rather than silently fabricating a straight line.

---

## 3. Real-Time Traffic Information

### 3.1 Live Traffic Probe Data
- **Current Status:** OpenStreetMap does not natively collect or distribute live vehicle probe telemetry (unlike Google Maps or Apple Maps, which ingest GPS feeds from millions of active smartphones).
- **Congestion Estimation:** In the absence of a licensed commercial traffic telemetry provider (e.g., TomTom Traffic API, HERE Traffic API), travel durations are estimated using speed profiles calibrated to highway classifications (motorway, trunk, primary, secondary, residential) and intersection friction factors.
- **Transparency Guarantee:** NexRoute always labels durations as **"Model Estimated Time"** when commercial probe telemetry is absent, and never claims real-time traffic accuracy unless backed by an authenticated traffic provider feed.

---

## 4. Accessibility Data in OpenStreetMap

### 4.1 Tag Sparsity
- **The Challenge:** While OpenStreetMap provides rich tagging schemas (`wheelchair=yes|no|limited`, `incline=*`, `kerb=lowered|raised`, `surface=*`), sidewalk and wheelchair accessibility attributes are sparse in many developing regions and residential roads.
- **The Three-State Constraint Principle:**
  NexRoute categorizes every road segment into three explicit states:
  1. `VERIFIED_ACCESSIBLE`: Explicit OSM tags confirm step-free access, slope <= 6%, and asphalt/concrete surface.
  2. `VERIFIED_INACCESSIBLE`: Explicit tags identify stairs, steps, escalators without lifts, stiles, or slopes > 8%.
  3. `UNKNOWN`: Road or pedestrian link lacks accessibility annotations.
- **Operational Modes:**
  - **Strict Mode:** Rejects any path containing `VERIFIED_INACCESSIBLE` or `UNKNOWN` segments. (Guarantees safety, but may report "No accessible route found" in sparsely tagged areas).
  - **Best-Effort Mode:** Avoids `VERIFIED_INACCESSIBLE` segments while traversing `UNKNOWN` segments with explicit disclosure of unverified segments to the traveler.

---

## 5. Algorithmic Characteristics & Trade-offs

### 5.1 Yen's K-Shortest Loopless Paths
- **Computational Complexity:** $O(K \cdot |V| \cdot (|E| + |V| \log |V|))$. On large graphs with thousands of nodes, computing $K \ge 5$ loopless paths can incur noticeable latency.
- **Corridor Diversity:** Yen's algorithm generates the mathematically $K$-shortest paths, which can often differ by only a single side-street block. NexRoute applies spatial corridor filtering ($\le 80\%$ overlap) to ensure that displayed alternatives offer genuine route choices.

### 5.2 Heuristic Admissibility
- For distance-based A*, the Haversine great-circle distance is strictly admissible since no surface path can be shorter than the great circle chord.
- For time-based A*, the heuristic must divide great-circle distance by the maximum legal network speed $v_{\max}$ (e.g., 120 km/h). Using average speed violates admissibility and can cause A* to return suboptimal routes.

---

## 6. AI Travel Assistance (Ollama)

### 6.1 Local LLM Performance
- NexRoute supports Ollama (`llama3`, `mistral`, `phi3`) for generating localized cultural travel tips, budget estimates, and itinerary summaries.
- **Hardware Dependency:** Inference latency depends directly on host hardware:
  - With GPU acceleration (NVIDIA CUDA): Response time 1.5s - 3s.
  - CPU-only execution: Response time 8s - 25s.
- **Resilience:** If Ollama is unavailable or times out, NexRoute falls back to deterministic rule-based travel advisories without breaking the user experience.
