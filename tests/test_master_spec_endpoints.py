"""
Automated Test Suite for Pathfinder Master Specification Endpoints (Phase 12 / Section 26)
Verifies:
1.  GET    /api/health
2.  GET    /api/places/search
3.  GET    /api/places/nearby
4.  POST   /api/routes/alternatives
5.  GET    /api/traffic/segments
6.  GET    /api/traffic/segments/{segment_id}
7.  POST   /api/location/contribution
8.  POST   /api/incidents
9.  GET    /api/incidents/nearby
10. POST   /api/location-sharing/sessions
11. DELETE /api/location-sharing/sessions/{session_id}
12. GET    /api/user/saved-places
13. POST   /api/user/saved-places
14. DELETE /api/user/saved-places/{place_id}
15. GET    /api/user/preferences
16. PATCH  /api/user/preferences
"""

import pytest
from fastapi.testclient import TestClient
from src.api_server import app
from src.backend.auth.security import create_access_token
from src.backend.database.connection import get_db, engine, Base
from src.backend.database.models import User, UserPreferences, RoadSegment, Place

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    # Ensure test user exists
    user = db.query(User).filter(User.email == "spec_tester@pathfinder.org").first()
    if not user:
        user = User(
            id="user_spec_test_001",
            email="spec_tester@pathfinder.org",
            username="spectester",
            hashed_password="mockhashedpassword123",
            full_name="Spec Quality Tester",
            role="USER"
        )
        db.add(user)
        prefs = UserPreferences(user_id=user.id, default_routing_profile="FASTEST")
        db.add(prefs)
        db.commit()

    # Ensure test road segment exists
    seg = db.query(RoadSegment).filter(RoadSegment.id == "SEG_SPEC_MAIN_01").first()
    if not seg:
        seg = RoadSegment(
            id="SEG_SPEC_MAIN_01",
            name="Pathfinder Central Expressway",
            road_type="PRIMARY",
            start_latitude=16.2335,
            start_longitude=80.5505,
            end_latitude=16.2400,
            end_longitude=80.5600,
            length_meters=1400.0,
            speed_limit_kmh=60.0,
            surface_quality=0.92,
            geometry_polyline=[[16.2335, 80.5505], [16.2400, 80.5600]]
        )
        db.add(seg)
        db.commit()

    # Ensure test place exists
    pl = db.query(Place).filter(Place.name == "Pathfinder Central Hospital").first()
    if not pl:
        pl = Place(
            id="pl_spec_hosp_01",
            name="Pathfinder Central Hospital",
            category="HOSPITAL",
            latitude=16.2340,
            longitude=80.5510,
            address="Medical Enclave, Central Ave",
            city="Guntur",
            rating=4.8
        )
        db.add(pl)
        db.commit()

    yield db


def get_auth_headers():
    token = create_access_token({"sub": "user_spec_test_001", "email": "spec_tester@pathfinder.org", "role": "USER"})
    return {"Authorization": f"Bearer {token}"}


def test_1_get_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert "version" in data


def test_2_get_places_search():
    res = client.get("/api/places/search?q=hospital")
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == "hospital"
    assert "results" in data


def test_3_get_places_nearby():
    res = client.get("/api/places/nearby?latitude=16.2335&longitude=80.5505&radius_km=10.0")
    assert res.status_code == 200
    data = res.json()
    assert "places" in data
    assert data["radius_km"] == 10.0


def test_4_post_routes_alternatives():
    payload = {
        "origin_latitude": 16.2335,
        "origin_longitude": 80.5505,
        "destination_latitude": 16.2500,
        "destination_longitude": 80.5700,
        "travel_mode": "driving",
        "objective": "fastest",
        "uncertainty_penalty_weight": 0.2
    }
    res = client.post("/api/routes/alternatives", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["alternatives_count"] >= 1
    assert "routes" in data
    assert "expected_travel_time_minutes" in data["routes"][0]


def test_5_get_traffic_segments():
    res = client.get("/api/traffic/segments?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "segments" in data
    assert "legend" in data


def test_6_get_traffic_segment_detail():
    res = client.get("/api/traffic/segments/SEG_SPEC_MAIN_01")
    assert res.status_code == 200
    data = res.json()
    assert data["segment_id"] == "SEG_SPEC_MAIN_01"
    assert data["name"] == "Pathfinder Central Expressway"
    assert "current_speed_kmh" in data


def test_7_post_location_contribution():
    payload = {
        "latitude": 16.2335,
        "longitude": 80.5505,
        "speed_kmh": 42.5,
        "heading": 120.0,
        "accuracy_meters": 4.2
    }
    res = client.post("/api/location/contribution", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ACCEPTED"
    assert data["inferred_mode"] == "VEHICLE"


def test_8_post_and_get_incidents():
    payload = {
        "category": "POTHOLE",
        "severity": "MEDIUM",
        "latitude": 16.2350,
        "longitude": 80.5520,
        "description": "Noticeable surface crater near intersection lane 2"
    }
    res = client.post("/api/incidents", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["CREATED", "CORROBORATED"]
    assert "incident_id" in data

    # 9. GET /api/incidents/nearby
    near_res = client.get("/api/incidents/nearby?latitude=16.2350&longitude=80.5520&radius_km=5.0")
    assert near_res.status_code == 200
    near_data = near_res.json()
    assert near_data["incident_count"] >= 1


def test_10_and_11_location_sharing_lifecycle():
    # 10. POST /api/location-sharing/sessions
    payload = {
        "recipient_identifier": "Family Contact (+91 9876543210)",
        "duration_minutes": 45,
        "current_lat": 16.2335,
        "current_lon": 80.5505
    }
    res = client.post("/api/location-sharing/sessions", json=payload)
    assert res.status_code == 200
    data = res.json()
    session_id = data["session_id"]
    assert data["status"] == "ACTIVE"
    assert "shareable_url" in data

    # 11. DELETE /api/location-sharing/sessions/{session_id}
    del_res = client.delete(f"/api/location-sharing/sessions/{session_id}")
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["status"] == "REVOKED"


def test_12_13_14_user_saved_places():
    headers = get_auth_headers()
    # 13. POST /api/user/saved-places
    create_payload = {
        "custom_label": "Vignan Innovation Hub",
        "latitude": 16.2345,
        "longitude": 80.5515,
        "address": "Vadlamudi Campus"
    }
    create_res = client.post("/api/user/saved-places", json=create_payload, headers=headers)
    assert create_res.status_code == 200
    place_id = create_res.json()["saved_place"]["id"]

    # 12. GET /api/user/saved-places
    list_res = client.get("/api/user/saved-places", headers=headers)
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert any(p["id"] == place_id for p in list_data["saved_places"])

    # 14. DELETE /api/user/saved-places/{place_id}
    del_res = client.delete(f"/api/user/saved-places/{place_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "DELETED"


def test_15_and_16_user_preferences():
    headers = get_auth_headers()
    # 15. GET /api/user/preferences
    get_res = client.get("/api/user/preferences", headers=headers)
    assert get_res.status_code == 200
    assert "preferences" in get_res.json()

    # 16. PATCH /api/user/preferences
    patch_payload = {
        "avoid_tolls": True,
        "avoid_highways": True,
        "default_routing_profile": "BALANCED"
    }
    patch_res = client.patch("/api/user/preferences", json=patch_payload, headers=headers)
    assert patch_res.status_code == 200
    updated_prefs = patch_res.json()["preferences"]
    assert updated_prefs["avoid_tolls"] is True
    assert updated_prefs["avoid_highways"] is True
    assert updated_prefs["default_routing_profile"] == "BALANCED"


def test_17_traffic_predict_and_evaluate():
    # Test traffic prediction for segment
    pred_res = client.get("/api/traffic/predict?segment_id=SEG_SPEC_MAIN_01&horizon_minutes=15")
    assert pred_res.status_code == 200
    pred_data = pred_res.json()
    assert pred_data["segment_id"] == "SEG_SPEC_MAIN_01"
    assert pred_data["horizon_minutes"] == 15
    assert "expected_speed_kmh" in pred_data
    assert "prediction_interval" in pred_data
    assert "confidence_score" in pred_data

    # Test comprehensive evaluation pipeline
    eval_res = client.post("/api/traffic/evaluate?samples=30")
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert "models" in eval_data
    assert "historical_baseline" in eval_data["models"]
    assert "gps_only_baseline" in eval_data["models"]
    assert "hybrid_traffic_model" in eval_data["models"]
    assert eval_data["models"]["hybrid_traffic_model"]["mae_speed_kmh"] >= 0.0
    assert "conclusion" in eval_data


def test_18_location_sharing_list_and_view():
    headers = get_auth_headers()
    # Create sharing session
    payload = {
        "recipient_identifier": "Friend Location Access",
        "duration_minutes": 30,
        "current_lat": 16.2335,
        "current_lon": 80.5505
    }
    create_res = client.post("/api/location-sharing/sessions", json=payload, headers=headers)
    assert create_res.status_code == 200
    token = create_res.json()["sharing_token"]
    session_id = create_res.json()["session_id"]

    # View location sharing session
    view_res = client.get(f"/api/location-sharing/view/{token}")
    assert view_res.status_code == 200
    view_data = view_res.json()
    assert view_data["status"] == "ACTIVE"
    assert view_data["latitude"] == 16.2335
    assert view_data["longitude"] == 80.5505
    assert view_data["time_remaining_seconds"] > 0

    # List active sessions
    list_res = client.get("/api/location-sharing/sessions", headers=headers)
    assert list_res.status_code == 200
    assert list_res.json()["count"] >= 1

    # Revoke
    del_res = client.delete(f"/api/location-sharing/sessions/{session_id}")
    assert del_res.status_code == 200

