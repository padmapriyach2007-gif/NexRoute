# Pathfinder: Architecture, System Design & Setup Guide
## AI-Powered Navigation, Hybrid Traffic Intelligence & Smart Travel Platform

---

## 1. System Vision & Architecture

**Pathfinder** is an enterprise-grade, geospatial navigation and intelligent travel platform designed for high-reliability routing, multimodal itinerary planning, sensor-fused traffic intelligence, and privacy-preserving location services.

```
                              ┌────────────────────────────────────────────────────────┐
                              │           Pathfinder Web & Mobile Frontend             │
                              │       (Streamlit Responsive / Native Android)          │
                              └──────────────────────────┬─────────────────────────────┘
                                                         │ REST & WebSocket
                                                         ▼
                              ┌────────────────────────────────────────────────────────┐
                              │            FastAPI REST Server (src/api_server.py)     │
                              └──────────┬───────────────────────────────┬─────────────┘
                                         │                               │
                ┌────────────────────────┴──────────────┐   ┌────────────┴─────────────┐
                ▼                                       ▼   ▼                          ▼
┌───────────────────────────────┐       ┌───────────────────────┐   ┌──────────────────────────┐
│   Traffic Intelligence Engine │       │ Multi-Objective Router│   │ AI Travel Assistant Engine│
│ - Sensor Fusion (GPS+Radar)   │       │ - Fastest / Shortest  │   │ - Natural Language Agent │
│ - k-Anonymity (k>=3 threshold)│       │ - Uncertainty Penalty │   │ - Tool Calling           │
│ - AI Multi-Horizon Predictor  │       │ - Turn-by-Turn Engine │   │ - Verified Fact Retrieval│
│ - Empirical Evaluation Engine │       │ - OSRM + OSM Carto    │   │ - Medical/Safety Caution │
└───────────────┬───────────────┘       └───────────┬───────────┘   └────────────┬─────────────┘
                │                                   │                            │
                └────────────────────────┬──────────┴────────────────────────────┘
                                         ▼
                        ┌─────────────────────────────────┐
                        │      PostgreSQL + PostGIS       │
                        │    (or SQLite fallback in dev)  │
                        └─────────────────────────────────┘
```

---

## 2. Core Functional Modules

### A. Modular Traffic Intelligence (`src/backend/traffic/`)
1. **Sensor Fusion Service (`fusion_service.py`)**:
   - Ingests telemetry from consenting GPS users, roadside radar sensors, and municipal incident feeds.
   - Rejects GPS drift (<4 km/h), invalid horizontal accuracy (>50m), and impossible velocity (>180 km/h).
   - Enforces $k$-anonymity ($k \ge 3$ distinct contributors) before publishing unblended crowd speeds.
   - Applies exponential time-decay weighting ($\tau = 180\text{s}$) to prioritize fresh observations.
2. **AI Traffic Prediction Service (`prediction_service.py`)**:
   - Evaluates multi-horizon forecasts at **+15, +30, and +60 minutes**.
   - Combines short-term autoregressive persistence with diurnal historical harmonic curves.
   - Computes 95% confidence intervals and incorporates environmental weather dampening (e.g., -15% speed in rain, -30% in storms).
3. **Traffic Model Evaluation Pipeline (`evaluation_pipeline.py`)**:
   - Evaluates predicted vs observed travel times on held-out test splits.
   - Reports Mean Absolute Error (MAE), Median Absolute Error (MedAE), ETA error distribution ($P_{50}, P_{90}, P_{95}$), and Congestion Classification $F_1$ score.
   - Directly compares:
     1. Historical-Only Baseline
     2. GPS-Only Telemetry
     3. Pathfinder Hybrid Traffic Model

### B. Multi-Objective Routing (`src/backend/routing/` & `src/route_engine.py`)
- Calculates candidate routes across travel modes (Driving, Walking, Cycling, Transit).
- Evaluates candidate routes using the composite objective:
  $$\text{Route Cost} = \text{Travel Time} + (w_{\text{uncertainty}} \times \text{Uncertainty Penalty}) + P_{\text{preference}} + P_{\text{restrictions}}$$
- Configurable uncertainty penalty weight ($w_{\text{uncertainty}} \in [0.0, 1.0]$, default 0.25).
- Toll avoidance, highway avoidance, and wheelchair accessibility constraints.

### C. Conversational Travel Assistant (A.U.R.A.) (`src/pathfinder_chatbot.py`)
- Tool-driven natural language planning grounded in real database POIs, live Open-Meteo weather, and OSRM route calculations.
- Prompt injection defense, privacy isolation, and medical/legal advisory disclaimers.

---

## 3. Quickstart & Installation

### Prerequisites
- Python 3.10+ (tested through Python 3.14)
- Git

### Step 1: Clone & Environment Setup
```bash
git clone <repo-url> pathfinder
cd pathfinder
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Environment Configuration
Copy the template configuration file:
```bash
cp .env.example .env
```
Key configuration parameters:
| Parameter | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/pathfinder_maps.db` | Primary database URI (SQLite or PostgreSQL) |
| `JWT_SECRET_KEY` | Managed secret string | Auth token encryption key |
| `OSRM_BASE_URL` | `https://router.project-osrm.org` | OpenStreetMap OSRM routing endpoint |
| `GOOGLE_MAPS_API_KEY` | Empty (Optional) | Optional Google Maps Platform key |
| `TRAFFIC_FUSION_K_ANONYMITY_THRESHOLD` | `3` | Minimum contributors for live publishing |
| `TRAFFIC_UNCERTAINTY_PENALTY_WEIGHT` | `0.25` | Weight for route uncertainty penalty |

### Step 3: Run the Full Test Suite
```bash
python -m pytest
```

### Step 4: Launch the Applications

**Run the Streamlit Web Application:**
```bash
streamlit run app.py --server.port 8501
```
Navigate to `http://localhost:8501`.

**Run the FastAPI REST Backend Server:**
```bash
python -m uvicorn src.api_server:app --host 0.0.0.0 --port 8000 --reload
```
Interactive OpenAPI Swagger docs will be available at `http://localhost:8000/docs`.

---

## 4. Production Deployment & Database Migrations

For production setups with high concurrency:
1. **PostgreSQL + PostGIS Database**:
   ```env
   DATABASE_URL=postgresql://pathfinder:secure_password@postgres.internal:5432/pathfinder_db
   ```
2. **Migrations & Seed Data**:
   Database tables are automatically migrated and seeded with baseline road segments and regional facilities at FastAPI server startup via `run_migrations()` and `seed_database()`.
