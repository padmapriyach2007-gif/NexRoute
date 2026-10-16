"""
FastAPI REST API Server for CampusAegis / PROJECT AI
Provides backend endpoints for Android app and dashboard:
- GET  /api/health
- POST /api/geocode
- POST /api/route
- GET  /api/hazards
- POST /api/simulate-emergency
- POST /api/register-device
- GET  /api/notifications
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.map_service import MapService
from src.hazard_map import HazardMap, GeographicHazard, HazardSeverity
from src.route_engine import RealWorldRouteEngine, TravelMode
from src.safety_route_filter import SafetyRouteFilter
from src.notification_service import NotificationService, NotificationPriority

app = FastAPI(
    title="CampusAegis Real-World Emergency Navigation API",
    version="2.0.0",
    description="Autonomous emergency-aware routing and alert dispatch backend."
)

# Global singleton services
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
        "system": "CampusAegis Decision Support Prototype",
        "active_hazards": len(hazard_map.get_active_hazards())
    }


@app.post("/api/geocode")
def geocode_place(req: GeocodeRequest):
    coords = map_service.geocode(req.query)
    if not coords:
        raise HTTPException(status_code=404, detail="Location not found")
    return {"query": req.query, "latitude": coords[0], "longitude": coords[1]}


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
