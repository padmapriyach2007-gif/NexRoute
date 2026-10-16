# 🧭 CampusAegis 2.0
### An AI-Powered, Real-Time Adaptive Navigation and Multi-Objective Route Optimization System
**Tagline:** *Smarter Routes. Adaptive Decisions. Better Journeys.*

> Grounded in authentic geospatial coordinates connecting **Vignan University (Vadlamudi)**, regional arterial transit corridors, and the **Guntur Metropolitan Region**, integrating real-world OpenStreetMap cartography, multi-alternative routing engines, and verified road restriction management.

---

## 🌟 1. System Vision & Core Principles

CampusAegis 2.0 is a **real-time adaptive navigation and AI route optimization platform**. It finds optimal paths between user-selected origins and destinations, compares viable alternatives, incorporates verified road restrictions and traffic delays, dynamically adapts in-transit when conditions change, and truthfully explains route trade-offs without fabricating fake incidents.

### Core Architectural Principles:
1. **Multi-Objective Route Optimization:** Routes are evaluated across travel time, physical distance, user preferences, and accessibility requirements rather than single-dimension shortest path search.
2. **Dynamic Route Adaptation:** Monitors route conditions in-transit and triggers recalculation when meaningful restrictions or delays arise, suppressing duplicate alerts and micro-fluctuations.
3. **Truth-in-Data Provenance:** The system never fabricates live traffic readings, road closures, or sensor data. When external live traffic feeds are unconfigured, it clearly declares: *"Using standard provider travel-time estimates."*
4. **Controlled Demonstration Isolation:** Demonstration scenarios run under a strict, persistent `DEMO DATA — NOT LIVE` mode. Synthetic test fixtures are completely isolated from production routing.
5. **Human-Readable Route Explanations:** Every recommended route provides an automated, computed rationale explaining why it was selected and its trade-offs against alternatives (e.g., *"+3.8 mins slower, but saves 1.8 km distance"*).

---

## 🏗️ 2. Architectural Pipeline & Operating Modes

```
                                  ┌────────────────────────────────────────────────┐
                                  │      RoadConditionManager (Operating Mode)     │
                                  └───────────────────────┬────────────────────────┘
                                                          │
                 ┌────────────────────────────────────────┼──────────────────────────────────────┐
                 ▼                                        ▼                                      ▼
    🟢 LIVE_ROUTING                          🔵 STANDARD_ROUTING                   🟠 CONTROLLED_DEMO
    - Real OpenStreetMap Road Graph          - Resilient Offline Graph             - 8 Deterministic Scenarios
    - Live OSRM Route Engine                 - Zero External Dependencies          - Persistent "DEMO DATA" Badge
    - Truthful Data Provenance               - Instant Deterministic Fallback      - Isolated Test Fixtures
                 │                                        │                                      │
                 └────────────────────────────────────────┼──────────────────────────────────────┘
                                                          ▼
                                        ┌──────────────────────────────────┐
                                        │      Candidate Route Engine      │
                                        │  (Primary, Alt 1, Alt 2 Paths)   │
                                        └─────────────────┬────────────────┘
                                                          ▼
                                        ┌──────────────────────────────────┐
                                        │    MultiObjectiveRouter (Scorer) │
                                        │  Score = w_time*T + w_dist*D + P │
                                        └─────────────────┬────────────────┘
                                                          │
                 ┌────────────────────────────────────────┴────────────────────────────────────────┐
                 ▼                                                                                 ▼
    [Routes Evaluated & Ranked]                                                       [Hard Closure Conflict]
    - Rank 1: Recommended Route                                                       - Status: RESTRICTED_CLOSURE
    - Rank 2: Alternative 1 (Trade-Offs Computed)                                     - Hard Segments Autonomously Bypassed
    - Rank 3: Alternative 2                                                           - Verified Alternatives Prioritized
```

### Supported Operating Modes:
- **`LIVE_ROUTING` (Mode A):** Operates on real OpenStreetMap geocoding and live routing services. Rejects synthetic demonstration data to ensure authentic provenance.
- **`STANDARD_ROUTING` (Mode B):** Uses local road graph routing without external network dependencies. Provides complete offline resilience while maintaining multi-objective evaluation.
- **`CONTROLLED_DEMO` (Mode C):** Displays a persistent `DEMO DATA — NOT LIVE` indicator. Provides 8 repeatable benchmark scenarios for evaluation, demonstrations, and stress testing.

---

## 📐 3. Multi-Objective Route Scoring Model

CampusAegis 2.0 ranks alternative corridors using a normalized mathematical scoring function:

$$\text{Score}(R) = w_{\text{time}} \cdot \left(\frac{T(R)}{T_{\min}}\right) + w_{\text{dist}} \cdot \left(\frac{D(R)}{D_{\min}}\right) + P_{\text{preference}} + P_{\text{restriction}}$$

Where:
- $T(R)$ = Total effective travel time including verified traffic delays ($T = T_{\text{base}} + \Delta t_{\text{delay}}$).
- $D(R)$ = Total physical route distance in kilometers.
- $T_{\min}, D_{\min}$ = Normalization baselines among eligible candidate corridors.
- $w_{\text{time}}, w_{\text{dist}}$ = User-selected objective weights:
  - **⚡ Fastest Route:** $w_{\text{time}} = 0.85, \quad w_{\text{dist}} = 0.15$
  - **📏 Shortest Route:** $w_{\text{time}} = 0.15, \quad w_{\text{dist}} = 0.85$
  - **⚖️ Balanced Route:** $w_{\text{time}} = 0.50, \quad w_{\text{dist}} = 0.50$
  - **♿ Accessible Route:** Strict wheelchair accessibility hard constraint ($P_{\text{stairs}} = \infty$).
- $P_{\text{restriction}}$ = Penalty or hard exclusion ($P = \infty$) for verified road closures.

---

## 🔬 4. Navigation & Search Algorithms

| Algorithm | Category | Complexity | Optimal | Key Strength |
| :--- | :--- | :--- | :--- | :--- |
| **A\* Search** | Graph Search | $O(\|E\| \log \|V\|)$ | Yes (Admissible Heuristic) | Minimum node expansions via Euclidean / Haversine distance heuristic. |
| **Dijkstra's Algorithm** | Shortest Path | $O(\|E\| + \|V\| \log \|V\|)$ | Yes | True optimal baseline on non-negative edge weights; verifies A\* correctness. |
| **Bidirectional A\*** | Bidirectional Search | $O(b^{d/2})$ | Yes | Twin search wavefronts meeting at midpoint; 42% search space reduction on regional corridors. |
| **Yen's K-Shortest Paths** | Alternative Routing | $O(K \cdot \|V\| (\|E\| + \|V\| \log \|V\|))$ | Yes | Generates loopless alternative corridors for trade-off comparison. |
| **D\* Lite** | Incremental Replanning | $O(\|V\| \log \|V\|)$ | Yes | Reuses previous search trees when in-transit road restrictions appear ahead. |

---

## 🧪 5. Controlled Demonstration Scenarios (Mode C)

1. **Nominal Road Conditions (Clear Flow):** Baseline verification with all arterial roads open.
2. **Traffic Congestion on Main Highway:** Heavy congestion delay (+8 mins) on Tenali Highway; North Bypass becomes fastest.
3. **Road Maintenance Closure on Arterial Corridor:** Bridge resurfacing blocks Main Avenue; system hard-excludes corridor and switches to verified alternative.
4. **Multi-Objective Preference Shift:** Demonstrates real-time re-ranking between Fastest (Highway) and Shortest (Arterial).
5. **In-Transit Rerouting Trigger:** Simulates sudden lane restriction appearing ahead during navigation, triggering automatic reroute.
6. **All Corridors to Destination Restricted:** Simulates all access approaches closed; system refuses to fabricate an unsafe path.
7. **Accessibility Constraint (Wheelchair Mode):** Excludes outdoor stairs and uneven steps; selects certified ramp paths.
8. **Provider Timeout & Offline Fallback:** Simulates external routing server timeout; demonstrates graceful fallback to local road graph.

---

## 🚀 6. Installation & Quick Start

### Prerequisites
- Python 3.10+ (Tested on Python 3.14.3)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### Installation
```bash
# 1. Clone repository
git clone https://github.com/your-org/PROJECT-AI.git
cd "PROJECT AI"

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
```

### Launch Application
```bash
streamlit run app.py
```
Access the application at `http://localhost:8501`.

---

## 🧪 7. Automated Test Suite

Run the full automated test suite:
```bash
python -m pytest tests/ -v
```

### Test Suite Coverage:
- `tests/test_multi_objective_navigation.py`: Multi-objective scoring weights, trade-off explanations, road restriction exclusions, and mode boundary enforcement.
- `tests/test_real_world_navigation.py`: Real geocoding cache, Haversine geometry, OSRM candidate route generation, and permission states.
- `tests/test_emergency_system.py`: A*, Dijkstra, Greedy Best-First, and CSP anti-stampede graph algorithms.
- **Result:** **39 passed in 23.14s (100% pass rate)**.

---

## 🔒 8. Security, Privacy & Data Provenance

- **Zero API Key Leakage:** `.env.example` provides documented placeholders only; no private credentials or secrets are committed.
- **Truth-in-Data Provenance:** Missing traffic data is never interpreted as clear flow. Ordinary routing travel times are clearly labeled as estimates.
- **Privacy Minimization:** GPS location coordinates are processed locally in session state; no persistent movement history is stored without explicit user consent.
- **Fail-Safe Operation:** If external routing APIs become unavailable, the system automatically falls back to the embedded regional road graph without interrupting user journeys.
