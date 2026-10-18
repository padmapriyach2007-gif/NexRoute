"""
Comprehensive Integration and Unit Tests for Next-Generation Maps Backend
Validates Auth, Routing, Road Intelligence, Entrances, Place Discovery,
Multimodal Itineraries, Weather, Vehicle/EV Planning, Collaborative Maps,
Visual Nav, Offline Packages, Ingestion, and FastAPI Endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from src.api_server import app
from src.backend.database.connection import SessionLocal
from src.backend.database.migrations import run_migrations
from src.backend.database.seed_data import seed_database
from src.backend.auth.security import hash_password, verify_password, create_access_token
from src.backend.routing.advanced_router import AdvancedRouter
from src.backend.routing.provider_interface import RoutingProfile, RouteObjective
from src.backend.routing.dynamic_rerouter import DynamicRerouter
from src.backend.routing.vehicle_router import VehicleRouter
from src.backend.routing.accessibility_router import AccessibilityRouter
from src.backend.road_intelligence.condition_service import RoadConditionService
from src.backend.road_intelligence.reliability_scorer import ReliabilityScorer
from src.backend.place_discovery.discovery_service import PlaceDiscoveryService
from src.backend.arrival.entrance_service import EntranceService
from src.backend.multimodal.journey_planner import MultimodalJourneyPlanner
from src.backend.weather.weather_service import WeatherService
from src.backend.collaboration.collab_service import CollaborativeService
from src.backend.visual_navigation.visual_nav_service import VisualNavigationService
from src.backend.ai_agent.trip_planner_agent import TripPlannerAgent
from src.backend.offline.package_service import OfflinePackageService
from src.backend.ingestion.data_ingestion import DataIngestionEngine


@pytest.fixture(scope="module")
def test_setup():
    run_migrations()
    seed_database()
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# =============================================================================
# 1. AUTHENTICATION & SECURITY TESTS
# =============================================================================

def test_password_hashing():
    pwd = "SecurePassword2026!"
    hashed = hash_password(pwd)
    assert hashed.startswith("pbkdf2:sha256:100000$")
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_auth_endpoints(client):
    # Login as seeded demo user
    resp = client.post("/api/v2/auth/login", json={
        "email": "user@pathfinder.org",
        "password": "UserPassword123!"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    token = data["access_token"]

    # Access protected profile
    headers = {"Authorization": f"Bearer {token}"}
    prof_resp = client.get("/api/v2/auth/me", headers=headers)
    assert prof_resp.status_code == 200
    assert prof_resp.json()["email"] == "user@pathfinder.org"

    # Unauthorized access rejection
    unauth_resp = client.get("/api/v2/auth/me")
    assert unauth_resp.status_code == 401


# =============================================================================
# 2. ADVANCED MULTI-CRITERIA ROUTING TESTS
# =============================================================================

def test_multi_objective_route_calculation(test_setup):
    router = AdvancedRouter()
    # Route from Vignan University to Tenali
    routes = router.calculate_multimodal_routes(
        origin_lat=16.2335, origin_lon=80.5505,
        dest_lat=16.2420, dest_lon=80.6450,
        profile=RoutingProfile.DRIVING,
        objective=RouteObjective.FASTEST
    )
    assert len(routes) >= 2
    r0 = routes[0]
    assert r0.distance_km > 0
    assert r0.duration_minutes > 0
    assert r0.estimated_fuel_litres > 0
    assert r0.estimated_fuel_cost_inr > 0


def test_accessibility_audit():
    acc_router = AccessibilityRouter()
    router = AdvancedRouter()
    routes = router.calculate_multimodal_routes(
        16.2335, 80.5505, 16.2348, 80.5515,
        profile=RoutingProfile.WALKING,
        require_accessible=True
    )
    audit = acc_router.evaluate_route_accessibility(routes[0])
    assert "is_wheelchair_accessible" in audit
    assert "accessibility_confidence" in audit
    assert audit["accessibility_confidence"] >= 0.5


def test_vehicle_restrictions_and_ev_charging(test_setup):
    db = test_setup
    veh_router = VehicleRouter()
    from src.backend.database.models import VehicleProfile
    ev = db.query(VehicleProfile).filter(VehicleProfile.vehicle_type == "EV").first()
    assert ev is not None

    router = AdvancedRouter()
    routes = router.calculate_multimodal_routes(16.2335, 80.5505, 16.3067, 80.4365)
    ev_plan = veh_router.plan_ev_charging_stops(routes[0], ev, db)
    assert "requires_charging" in ev_plan
    assert "charging_stops" in ev_plan


def test_dynamic_reroute_detour():
    from src.backend.database.models import RoadConditionReport
    from datetime import datetime, timedelta, timezone

    active_hazard = RoadConditionReport(
        id="TEST_HAZARD_1",
        category="ROAD_CLOSURE",
        severity="HIGH",
        status="VERIFIED",
        latitude=16.2360,
        longitude=80.5460,
        affected_radius_meters=100.0,
        road_name="Vadlamudi Crossing",
        description="Active closure",
        confidence_score=0.95,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=5)
    )

    rerouter = DynamicRerouter()
    polyline = [(16.2335, 80.5505), (16.2360, 80.5460), (16.2385, 80.5420)]
    conflicts = rerouter.detect_conflicts(polyline, [active_hazard])
    assert len(conflicts) >= 1
    assert conflicts[0]["is_blocking"] is True


# =============================================================================
# 3. REAL-TIME ROAD INTELLIGENCE TESTS
# =============================================================================

def test_road_condition_report_lifecycle(test_setup):
    import uuid
    db = test_setup
    import random
    unique_suffix = uuid.uuid4().hex[:8]
    test_lat = 30.0 + random.uniform(0.1, 10.0)
    test_lon = 70.0 + random.uniform(0.1, 10.0)

    # 1. Create report
    report1, is_new1 = RoadConditionService.create_or_corroborate_report(
        db=db,
        reporter_id=None,
        reporter_type="COMMUNITY",
        category="POTHOLE",
        severity="MEDIUM",
        latitude=test_lat,
        longitude=test_lon,
        description=f"Deep pothole near entrance gate {unique_suffix}",
        road_name="Campus Arterial"
    )
    assert is_new1 is True
    assert report1.status in ("PENDING", "VERIFIED")

    # 2. Duplicate detection (within 50 meters of same category)
    report2, is_new2 = RoadConditionService.create_or_corroborate_report(
        db=db,
        reporter_id=None,
        reporter_type="COMMUNITY",
        category="POTHOLE",
        severity="MEDIUM",
        latitude=test_lat + 0.0001,
        longitude=test_lon + 0.0001,
        description=f"Confirming severe pothole here {unique_suffix}"
    )
    assert is_new2 is False  # Clustered as corroboration
    assert report2.id == report1.id
    assert report2.upvotes >= 2

    # 3. Community confirmation
    updated = RoadConditionService.confirm_or_dispute_report(
        db, report1.id, user_id=None, confirmation_type="STILL_PRESENT"
    )
    assert updated.upvotes >= 3


# =============================================================================
# 4. REAL-WORLD ARRIVAL & ENTRANCE NAVIGATION TESTS
# =============================================================================

def test_arrival_entrance_selection(test_setup):
    db = test_setup
    from src.backend.database.models import Place
    place = db.query(Place).filter(Place.category == "UNIVERSITY").first()
    assert place is not None

    # Driving mode -> should select MAIN or VEHICLE entrance
    ent_driving = EntranceService.select_optimal_entrance(place, travel_mode="driving")
    assert ent_driving is not None
    assert ent_driving.entrance_type in ("MAIN", "VEHICLE")

    # Emergency mode -> should select EMERGENCY entrance
    ent_er = EntranceService.select_optimal_entrance(place, is_emergency=True)
    assert ent_er is not None
    assert ent_er.entrance_type == "EMERGENCY"

    # Final approach plan
    plan = EntranceService.plan_final_approach(db, place.id, 16.2330, 80.5500, travel_mode="driving")
    assert "selected_entrance" in plan
    assert "last_300m_walking_steps" in plan
    assert len(plan["last_300m_walking_steps"]) > 0


# =============================================================================
# 5. AI-POWERED PLACE DISCOVERY TESTS
# =============================================================================

def test_natural_language_place_search(test_setup):
    db = test_setup
    query = "Find a quiet cafe with wifi, outlets and parking"
    results = PlaceDiscoveryService.search_and_rank(
        db, query, user_lat=16.2335, user_lon=80.5505, radius_km=15.0
    )
    assert len(results) > 0
    top_hit = results[0]
    assert "match_score" in top_hit
    assert "match_explanation" in top_hit
    assert top_hit["match_score"] > 0


def test_place_comparison(test_setup):
    db = test_setup
    from src.backend.database.models import Place
    places = db.query(Place).limit(2).all()
    p_ids = [p.id for p in places]

    comparison = PlaceDiscoveryService.compare_places(db, p_ids, 16.2335, 80.5505)
    assert comparison["comparison_count"] == 2
    assert len(comparison["places"]) == 2


# =============================================================================
# 6. MULTIMODAL JOURNEY PLANNING TESTS
# =============================================================================

def test_multimodal_planner(test_setup):
    db = test_setup
    options = MultimodalJourneyPlanner.plan_multimodal_itinerary(
        db,
        origin_lat=16.2335, origin_lon=80.5505,
        dest_lat=16.2420, dest_lon=80.6450
    )
    assert len(options) >= 1
    # Check legs and fare
    opt = options[0]
    assert "total_duration_minutes" in opt
    assert "total_fare_inr" in opt
    assert len(opt["legs"]) > 0


# =============================================================================
# 7. WEATHER INTEGRATION TESTS
# =============================================================================

def test_weather_observation():
    weather = WeatherService.get_weather_at_location(16.2335, 80.5505)
    assert "temperature_celsius" in weather
    assert "weather_description" in weather
    assert "hazard_warnings" in weather


# =============================================================================
# 8. COLLABORATIVE MAPS TESTS
# =============================================================================

def test_collaborative_map_workflow(test_setup):
    db = test_setup
    from src.backend.database.models import User
    user = db.query(User).first()

    collab_map = CollaborativeService.create_collaborative_map(
        db, owner_id=user.id, title="Weekend Road Trip to Guntur"
    )
    assert collab_map.id is not None
    assert collab_map.share_token is not None

    stop = CollaborativeService.add_stop(
        db, map_id=collab_map.id, user_id=user.id,
        title="Artisan Coffee Roastery",
        latitude=16.2370, longitude=80.5440,
        notes="Breakfast stop"
    )
    assert stop.id is not None
    assert stop.sequence_order == 1

    voted_stop = CollaborativeService.vote_on_stop(
        db, stop_id=stop.id, user_id=user.id, vote_value=1
    )
    assert voted_stop.vote_score == 1


# =============================================================================
# 9. VISUAL & CAMERA-ASSISTED NAVIGATION TESTS
# =============================================================================

def test_visual_landmarks_in_viewport(test_setup):
    db = test_setup
    # Pointing camera towards Vignan Main Gateway Arch (heading 90 degrees)
    landmarks = VisualNavigationService.get_landmarks_in_camera_view(
        db,
        user_lat=16.2320,
        user_lon=80.5480,
        user_heading_degrees=90.0,
        camera_fov_degrees=65.0,
        max_distance_meters=1000.0
    )
    assert len(landmarks) > 0
    top_lm = landmarks[0]
    assert "screen_x_normalized" in top_lm
    assert "visual_cue_description" in top_lm
    assert "turn_reference_instruction" in top_lm


# =============================================================================
# 10. AI TRIP-PLANNING AGENT TESTS
# =============================================================================

def test_ai_trip_planner_agent(test_setup):
    db = test_setup
    agent = TripPlannerAgent(db)
    itinerary = agent.plan_trip(
        prompt="Plan a 1-day academic and culinary tour around Vignan University and Tenali with vegetarian dining",
        user_lat=16.2335,
        user_lon=80.5505,
        days=1,
        preferred_mode="driving"
    )
    assert "itinerary_title" in itinerary
    assert "stops" in itinerary
    assert len(itinerary["stops"]) > 0
    assert "metrics" in itinerary
    assert itinerary["metrics"]["total_distance_km"] > 0
    assert "agent_explanation" in itinerary


# =============================================================================
# 11. OFFLINE MAP PACKAGE TESTS
# =============================================================================

def test_offline_package_generation(test_setup):
    db = test_setup
    packages = OfflinePackageService.list_available_packages(db)
    assert len(packages) >= 1
    pkg = packages[0]

    bundle = OfflinePackageService.generate_package_payload(db, pkg["package_id"])
    assert bundle["format"] == "PathfinderOfflineMapBundle"
    assert "feature_collection" in bundle
    assert "offline_capabilities" in bundle


# =============================================================================
# 12. DATA INGESTION ENGINE TESTS
# =============================================================================

def test_data_ingestion_with_provenance(test_setup):
    import uuid
    db = test_setup
    unique_name = f"Tenali Town Clock Tower {uuid.uuid4().hex[:6]}"
    records = [
        {
            "name": unique_name,
            "category": "LANDMARK",
            "latitude": 16.2425,
            "longitude": 80.6455,
            "address": "Bazaar Street, Tenali",
            "rating": 4.6,
            "amenities": ["photography", "heritage"]
        }
    ]
    job = DataIngestionEngine.ingest_poi_dataset(db, records, provider_name="OPEN_STREET_MAP")
    assert job.status == "COMPLETED"
    assert job.records_ingested >= 1


# =============================================================================
# 13. REST API ENDPOINT INTEGRATION TESTS
# =============================================================================

def test_api_v2_system_status(client):
    resp = client.get("/api/v2/system/status")
    assert resp.status_code == 200
    assert resp.json()["status"] == "OPERATIONAL"
    assert resp.json()["features"]["advanced_routing"] is True


def test_api_v2_routes_calculate(client):
    payload = {
        "origin_latitude": 16.2335,
        "origin_longitude": 80.5505,
        "destination_latitude": 16.2420,
        "destination_longitude": 80.6450,
        "travel_mode": "driving",
        "objective": "fastest"
    }
    resp = client.post("/api/v2/routes/calculate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert len(data["routes"]) >= 1


def test_api_v2_place_discovery_endpoint(client):
    resp = client.get("/api/v2/places/discover?query=cafe+with+wifi&latitude=16.2335&longitude=80.5505")
    assert resp.status_code == 200
    data = resp.json()
    assert "places" in data
    assert len(data["places"]) > 0


def test_api_v2_road_condition_report_and_query(client):
    post_resp = client.post("/api/v2/road-conditions/report", json={
        "category": "FLOODING",
        "severity": "HIGH",
        "latitude": 16.2355,
        "longitude": 80.5485,
        "description": "Flash waterlogging on campus approach",
        "affected_radius_meters": 75.0
    })
    assert post_resp.status_code == 200
    report_id = post_resp.json()["report"]["id"]

    # Query by radius
    rad_resp = client.get(f"/api/v2/road-conditions/radius?latitude=16.2355&longitude=80.5485&radius_meters=500")
    assert rad_resp.status_code == 200
    reports = rad_resp.json()
    assert any(r["id"] == report_id for r in reports)
