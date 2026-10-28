"""
FastAPI REST API Server for CampusAegis / P.A.T.H.F.I.N.D.E.R.
Provides:
1. Legacy v1 Endpoints (Android client & Dashboard backward compatibility):
   - GET  /api/health
   - POST /api/geocode
   - POST /api/route
   - GET  /api/hazards
   - POST /api/simulate-emergency
   - POST /api/register-device
   - GET  /api/notifications
2. Production-Ready Next-Generation Maps v2 Endpoints (/api/v2/*):
   - Auth, JWT, Roles, Preferences (/api/v2/auth/*)
   - Advanced Multi-Criteria Routing, Dynamic Reroute, Costs (/api/v2/routes/*)
   - Real-Time Road Intelligence, Community Reports, Scoring (/api/v2/road-conditions/*)
   - Place Discovery, Explainable Ranking, Comparisons (/api/v2/places/*)
   - Real-World Arrival, Entrances, Parking, Last 300m (/api/v2/arrival/*)
   - Multimodal Public Transit & Ride-Hail Itineraries (/api/v2/multimodal/*)
   - Vehicle Constraints & EV Supercharging Planner (/api/v2/vehicles/*)
   - Weather-Aware Routing & Hazard Alerts (/api/v2/weather/*)
   - Collaborative Maps, Stops, Voting, Audit Logs (/api/v2/collaborative/*)
   - Camera-Assisted Visual Navigation & Landmarks (/api/v2/visual-nav/*)
   - Tool-Driven AI Trip-Planning Agent (/api/v2/ai-planner/*)
   - Offline Map Packages, Checksums, Manifests (/api/v2/offline/*)
   - Data Ingestion & Digital Twin Sync (/api/v2/ingestion/*)
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.map_service import MapService
from src.hazard_map import HazardMap, GeographicHazard, HazardSeverity
from src.route_engine import RealWorldRouteEngine, TravelMode
from src.safety_route_filter import SafetyRouteFilter
from src.notification_service import NotificationService, NotificationPriority

# Next-Gen Backend Modules
from src.backend.database.migrations import run_migrations
from src.backend.database.seed_data import seed_database
from src.backend.api.v2_router import v2_router
from src.backend.api.routes_spec_endpoints import spec_router

app = FastAPI(
    title="P.A.T.H.F.I.N.D.E.R. Next-Generation Maps & Real-World Navigation Backend",
    version="2.5.0",
    description="Autonomous emergency-aware routing, digital twin road intelligence, multi-entrance arrival, multimodal itineraries, and AI trip planning."
)

# Scalability, Rate Limiting & Overload Protection Middleware
from src.backend.security.rate_limiter import ScalabilityProtectionMiddleware

app.add_middleware(
    ScalabilityProtectionMiddleware,
    max_request_bytes=3 * 1024 * 1024,
    general_rate_limit=120,
    strict_rate_limit=30,
    max_concurrent_requests=64
)

# CORS middleware for mobile and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup lifecycle to run database migrations and seed baseline records
@app.on_event("startup")
def on_startup():
    run_migrations()
    seed_database()

from src.backend.api.health_router import health_router

# Mount Specification Core Endpoints & Next-Gen v2 APIRouter
app.include_router(health_router)
app.include_router(spec_router)
app.include_router(v2_router)

# Global singleton services (v1 compatibility)
map_service = MapService()
hazard_map = HazardMap()
route_engine = RealWorldRouteEngine()
safety_filter = SafetyRouteFilter(hazard_map)
notification_service = NotificationService()


# Request / Response Schemas
class GeocodeRequest(BaseModel):
    query: str


class RouteRequest(BaseModel):
    origin_lat: float
    origin_lon: float
    dest_lat: float
    dest_lon: float
    mode: str = "driving"
    require_accessible: bool = False


class SimulateEmergencyRequest(BaseModel):
    incident_type: str = "FIRE_DETECTED"
    severity: str = "HIGH"
    latitude: float
    longitude: float
    radius_meters: float = 200.0
    description: str = "Simulated road hazard incident"
    affected_road_name: Optional[str] = None


class RegisterDeviceRequest(BaseModel):
    user_id: str
    device_token: str


@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "system": "CampusAegis / P.A.T.H.F.I.N.D.E.R. Dual-Core Engine",
        "version": "2.5.0",
        "active_hazards": len(hazard_map.get_active_hazards())
    }


@app.get("/api/v2/system/status")
def system_v2_status():
    return {
        "status": "OPERATIONAL",
        "version": "2.5.0",
        "features": {
            "advanced_routing": True,
            "realtime_road_intelligence": True,
            "multi_entrance_arrival": True,
            "ai_place_discovery": True,
            "multimodal_transit_planner": True,
            "accessibility_constraints": True,
            "vehicle_aware_ev_planner": True,
            "weather_aware_routing": True,
            "collaborative_maps": True,
            "camera_visual_navigation": True,
            "ai_trip_planning_agent": True,
            "offline_map_packages": True,
            "data_ingestion_framework": True
        }
    }


@app.post("/api/geocode")
def geocode_place(req: GeocodeRequest):
    coords = map_service.geocode(req.query)
    if not coords:
        raise HTTPException(status_code=404, detail="Location not found")
    lat = coords["lat"] if isinstance(coords, dict) else coords[0]
    lon = coords["lon"] if isinstance(coords, dict) else coords[1]
    return {"query": req.query, "latitude": lat, "longitude": lon}


@app.get("/api/autocomplete")
def autocomplete_places(
    q: str = Query(..., min_length=1, description="Search query string"),
    limit: int = Query(7, ge=1, le=20, description="Max suggestions to return"),
    origin_lat: Optional[float] = Query(None, ge=-90.0, le=90.0),
    origin_lon: Optional[float] = Query(None, ge=-180.0, le=180.0)
):
    """
    Search-as-you-type autocomplete endpoint with structured location details,
    category badges, coordinate validation, and optional geographic distance relevance.
    """
    orig_coords = (origin_lat, origin_lon) if origin_lat is not None and origin_lon is not None else None
    results = map_service.get_disambiguation_candidates(q, limit=limit, origin_coords=orig_coords)
    return {
        "query": q,
        "count": len(results),
        "suggestions": results
    }



@app.post("/api/route")
def calculate_safety_routes(req: RouteRequest):
    mode = TravelMode.WALKING if req.mode.lower() == "walking" else TravelMode.DRIVING
    candidates = route_engine.calculate_routes(
        req.origin_lat, req.origin_lon,
        req.dest_lat, req.dest_lon,
        mode=mode
    )
    evaluated = safety_filter.evaluate_candidate_routes(
        candidates,
        require_accessible=req.require_accessible
    )
    return {
        "candidate_count": len(candidates),
        "eligible_routes": [r.to_dict() for r in evaluated if r.is_eligible],
        "excluded_routes": [r.to_dict() for r in evaluated if not r.is_eligible],
        "has_verified_route": any(r.is_eligible for r in evaluated)
    }


@app.get("/api/hazards")
def get_active_hazards():
    return [h.to_dict() for h in hazard_map.get_active_hazards()]


@app.post("/api/simulate-emergency")
def inject_simulated_emergency(req: SimulateEmergencyRequest):
    import uuid
    hazard = GeographicHazard(
        hazard_id=f"SIM_{uuid.uuid4().hex[:6]}",
        incident_type=req.incident_type,
        severity=HazardSeverity[req.severity.upper()],
        latitude=req.latitude,
        longitude=req.longitude,
        radius_meters=req.radius_meters,
        description=f"[SIMULATED] {req.description}",
        affected_road_name=req.affected_road_name,
        source="DASHBOARD_SIMULATION"
    )
    hazard_map.add_hazard(hazard)

    # Autonomous notification generation
    notif = notification_service.send_emergency_alert(
        target_user_id="all_active_users",
        title=f"Emergency Alert: {req.incident_type}",
        body=f"Hazard reported near ({req.latitude:.4f}, {req.longitude:.4f}). Routes in this corridor are blocked.",
        incident_type=req.incident_type,
        route_affected=True,
        alternative_available=True,
        priority=NotificationPriority.HIGH
    )

    return {
        "hazard": hazard.to_dict(),
        "dispatched_notification": notif.to_dict()
    }


@app.post("/api/register-device")
def register_device(req: RegisterDeviceRequest):
    notification_service.register_device(req.user_id, req.device_token)
    return {"status": "REGISTERED", "user_id": req.user_id}


@app.get("/api/notifications")
def get_notifications():
    return [n.to_dict() for n in notification_service.get_notification_history()]
