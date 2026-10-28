# Pathfinder REST API Specification
## Standard Specification Endpoints (Phase 12 / Section 26 & Traffic Intelligence)

---

### Overview
The Pathfinder REST API exposes authenticated, validated, and privacy-preserving endpoints for routing, place discovery, traffic telemetry fusion, AI forecasting, community incident reporting, and location sharing.

Base URL: `http://localhost:8000/api`

---

## 1. System Health & Diagnostics

### `GET /api/health`
Returns system status, active database backend, and service versions.
- **Request:** None
- **Response `200 OK`:**
  ```json
  {
    "status": "HEALTHY",
    "version": "2.5.0",
    "environment": "development",
    "database": "sqlite",
    "providers": {
      "routing": "OSRM (OpenStreetMap)",
      "geocoding": "Nominatim / Photon",
      "weather": "Open-Meteo"
    }
  }
  ```

---

## 2. Places & Discovery

### `GET /api/places/search`
Text search for points of interest, landmarks, addresses, and venues.
- **Query Parameters:**
  - `q` (string, required): Search query (e.g., `"hospital"`, `"Vadlamudi"`)
  - `latitude` (float, optional): User origin latitude for distance sorting
  - `longitude` (float, optional): User origin longitude
  - `limit` (int, default: 10): Maximum results to return
- **Response `200 OK`:**
  ```json
  {
    "query": "hospital",
    "count": 2,
    "results": [
      {
        "id": "pl_hosp_01",
        "name": "Pathfinder Central Hospital",
        "category": "HOSPITAL",
        "latitude": 16.2340,
        "longitude": 80.5510,
        "address": "Medical Enclave, Central Ave",
        "rating": 4.8,
        "distance_km": 1.2
      }
    ]
  }
  ```

### `GET /api/places/nearby`
Spatial radius search for places around GPS coordinates.
- **Query Parameters:**
  - `latitude` (float, required): Center latitude
  - `longitude` (float, required): Center longitude
  - `radius_km` (float, default: 5.0): Search radius
  - `category` (string, optional): `"hospitals"`, `"pharmacies"`, `"ev_charging"`, `"petrol"`, `"restaurants"`, `"parking"`
- **Response `200 OK`:**
  ```json
  {
    "center": { "latitude": 16.2335, "longitude": 80.5505 },
    "radius_km": 5.0,
    "category": "hospitals",
    "count": 4,
    "places": [ ... ]
  }
  ```

---

## 3. Multi-Objective Routing & Alternatives

### `POST /api/routes/alternatives`
Computes candidate route alternatives comparing travel times, traffic delays, and uncertainty penalties.
- **Request Body:**
  ```json
  {
    "origin_latitude": 16.2335,
    "origin_longitude": 80.5505,
    "destination_latitude": 16.2500,
    "destination_longitude": 80.5700,
    "travel_mode": "driving",
    "objective": "fastest",
    "avoid_tolls": false,
    "avoid_highways": false,
    "uncertainty_penalty_weight": 0.25
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "origin": [16.2335, 80.5505],
    "destination": [16.2500, 80.5700],
    "alternatives_count": 3,
    "routes": [
      {
        "route_id": "ROUTE_ALT_1",
        "name": "Express Corridor Bypass",
        "rank": 1,
        "is_recommended": true,
        "distance_km": 8.4,
        "expected_travel_time_minutes": 14.2,
        "traffic_delay_minutes": 1.1,
        "uncertainty_score": 0.05,
        "route_cost": 14.33,
        "tolls_present": false,
        "toll_cost_inr": 0.0,
        "road_quality_score": 0.94,
        "polyline": [ [16.2335, 80.5505], [16.2500, 80.5700] ],
        "turn_instructions": [ "Head north on Main Avenue", "Merge onto Express Corridor" ]
      }
    ]
  }
  ```

---

## 4. Traffic Intelligence & AI Forecasting

### `GET /api/traffic/segments`
Retrieves fused traffic states for all monitored road segments.
- **Query Parameters:** `limit` (int, default: 50)
- **Response `200 OK`:**
  ```json
  {
    "count": 4,
    "segments": [
      {
        "segment_id": "SEG_EXPRESSWAY_01",
        "name": "Pathfinder Central Expressway (NH-16)",
        "road_type": "MOTORWAY",
        "current_speed_kmh": 82.5,
        "free_flow_speed_kmh": 90.0,
        "congestion_level": "FREE_FLOW",
        "congestion_color": "green",
        "confidence_score": 0.88,
        "prediction_uncertainty": 0.12,
        "distinct_contributors": 4,
        "source_provenance": "LIVE_CROWD_FUSED"
      }
    ],
    "legend": {
      "green": "Free-flowing traffic (>85% free-flow speed)",
      "amber": "Moderate delay (55-85% free-flow speed)",
      "red": "Heavy congestion (30-55% free-flow speed)",
      "dark_red": "Severe delay / standstill (<30% free-flow speed)",
      "grey": "Insufficient telemetry or unmonitored"
    }
  }
  ```

### `GET /api/traffic/predict`
AI speed & travel time forecasting across 15, 30, and 60-minute horizons.
- **Query Parameters:**
  - `segment_id` (string, required): Target road segment
  - `horizon_minutes` (int, default: 15): `15`, `30`, or `60`
  - `weather` (string, optional): `"Clear"`, `"Rain"`, `"Storm"`, `"Fog"`
- **Response `200 OK`:**
  ```json
  {
    "segment_id": "SEG_EXPRESSWAY_01",
    "horizon_minutes": 15,
    "target_time": "2026-10-22T23:30:00Z",
    "expected_speed_kmh": 78.4,
    "expected_travel_time_seconds": 146.9,
    "prediction_interval": {
      "lower_bound_kmh": 70.2,
      "upper_bound_kmh": 86.6
    },
    "confidence_score": 0.84,
    "model_version": "Pathfinder-AI-Traffic-v2.5",
    "input_data_freshness_seconds": 45
  }
  ```

### `POST /api/traffic/evaluate`
Executes the empirical traffic model evaluation benchmark across held-out datasets.
- **Query Parameters:** `samples` (int, default: 120)
- **Response `200 OK`:**
  ```json
  {
    "sample_count": 120,
    "models": {
      "historical_baseline": {
        "mae_speed_kmh": 14.85,
        "mae_travel_time_seconds": 38.4,
        "congestion_classification_f1": 0.742
      },
      "gps_only_baseline": {
        "mae_speed_kmh": 11.20,
        "mae_travel_time_seconds": 29.1,
        "congestion_classification_f1": 0.810
      },
      "hybrid_traffic_model": {
        "mae_speed_kmh": 6.45,
        "medae_speed_kmh": 4.80,
        "mae_travel_time_seconds": 14.2,
        "eta_error_distribution_seconds": { "p50": 9.4, "p90": 28.5, "p95": 36.2 },
        "congestion_classification_f1": 0.925,
        "sparse_coverage_mae_kmh": 8.10
      }
    },
    "conclusion": "Pathfinder Hybrid Model achieved 6.45 km/h MAE, reducing travel-time error by 63.0%."
  }
  ```

---

## 5. Anonymous Location Contribution (Privacy-Preserving)

### `POST /api/location/contribution`
Submits pseudonymous vehicle telemetry for sensor fusion.
- Pedestrian drift (<4.0 km/h) is automatically down-weighted from motor traffic.
- Never retains user accounts or identity references with coordinates.
- **Request Body:**
  ```json
  {
    "latitude": 16.2335,
    "longitude": 80.5505,
    "speed_kmh": 42.5,
    "heading": 120.0,
    "accuracy_meters": 4.5,
    "road_segment_id": "SEG_EXPRESSWAY_01"
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "status": "ACCEPTED",
    "inferred_mode": "VEHICLE",
    "is_downweighted_from_vehicle_traffic": false,
    "privacy_guarantee": "No personal identifier retained. Pseudonymous aggregation active."
  }
  ```

---

## 6. Community Incidents & Road Intelligence

### `POST /api/incidents`
Reports accidents, potholes, closures, or flooding. Automatically deduplicates nearby reports.
- **Request Body:**
  ```json
  {
    "category": "POTHOLE",
    "severity": "MEDIUM",
    "latitude": 16.2350,
    "longitude": 80.5520,
    "description": "Crater in left lane near turn",
    "road_name": "Tenali Road"
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "status": "CREATED",
    "incident_id": "rep_93182",
    "category": "POTHOLE",
    "severity": "MEDIUM",
    "confidence_score": 0.65,
    "expires_at": "2026-10-25T23:00:00Z"
  }
  ```

### `GET /api/incidents/nearby`
Retrieves verified and active incidents within a spatial radius.
- **Query Parameters:** `latitude`, `longitude`, `radius_km` (default: 10.0)

---

## 7. Explicit Location Sharing

### `POST /api/location-sharing/sessions`
Creates an opt-in, time-limited live location sharing link.
- **Request Body:**
  ```json
  {
    "recipient_identifier": "Family Contact (+91 9876543210)",
    "duration_minutes": 60,
    "current_lat": 16.2335,
    "current_lon": 80.5505
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "session_id": "sess_89102",
    "sharing_token": "a8fbc72910...",
    "recipient": "Family Contact (+91 9876543210)",
    "duration_minutes": 60,
    "expires_at": "2026-10-23T00:15:00Z",
    "shareable_url": "/share-location?token=a8fbc72910...",
    "status": "ACTIVE"
  }
  ```

### `GET /api/location-sharing/view/{token}`
Recipient viewer endpoint verifying token authenticity and remaining lifespan.
- **Response `200 OK`:**
  ```json
  {
    "recipient": "Family Contact (+91 9876543210)",
    "latitude": 16.2335,
    "longitude": 80.5505,
    "status": "ACTIVE",
    "time_remaining_seconds": 3410
  }
  ```

### `DELETE /api/location-sharing/sessions/{session_id}`
Immediately terminates and revokes an active sharing session.

---

## 8. User Preferences & Saved Places

- `GET /api/user/saved-places`: Lists saved locations (Home, Work, Custom).
- `POST /api/user/saved-places`: Saves a new custom place.
- `DELETE /api/user/saved-places/{place_id}`: Deletes a saved place.
- `GET /api/user/preferences`: Retrieves routing defaults and vehicle profile.
- `PATCH /api/user/preferences`: Updates user preferences (avoid tolls, avoid highways, accessible mode).
