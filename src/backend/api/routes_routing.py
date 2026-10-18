"""
Advanced Routing API Router
"""

from typing import Any, Dict, List, Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.backend.database.connection import get_db
from src.backend.database.models import User, VehicleProfile, SavedRoute, RoadConditionReport
from src.backend.auth.security import get_current_user_optional, get_current_user
from src.backend.routing.advanced_router import AdvancedRouter
from src.backend.routing.provider_interface import RoutingProfile, RouteObjective
from src.backend.routing.dynamic_rerouter import DynamicRerouter
from src.backend.routing.accessibility_router import AccessibilityRouter

router = APIRouter(prefix="/routes", tags=["Core Mapping & Advanced Routing"])
advanced_router = AdvancedRouter()
dynamic_rerouter = DynamicRerouter()
accessibility_router = AccessibilityRouter()


class RouteCalculationRequest(BaseModel):
    origin_latitude: float
    origin_longitude: float
    destination_latitude: float
    destination_longitude: float
    travel_mode: str = "driving"  # driving, walking, cycling, motorcycle, heavy_vehicle
    objective: str = "fastest"    # fastest, shortest, eco, fewer_tolls, road_quality
    avoid_tolls: bool = False
    avoid_highways: bool = False
    require_accessible: bool = False
    vehicle_id: Optional[str] = None


class DynamicRerouteRequest(BaseModel):
    polyline: List[List[float]]  # [[lat, lon], ...]
    route_id: Optional[str] = "ACTIVE_ROUTE"
    objective: str = "fastest"


class SaveRouteRequest(BaseModel):
    title: str
    origin_name: str
    origin_lat: float
    origin_lon: float
    dest_name: str
    dest_lat: float
    dest_lon: float
    travel_mode: str = "DRIVING"
    distance_km: float
    duration_minutes: float
    polyline: List[List[float]]


@router.post("/calculate")
def calculate_routes(
    req: RouteCalculationRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    # Map profile
    try:
        profile = RoutingProfile(req.travel_mode.lower())
    except ValueError:
        profile = RoutingProfile.DRIVING

    try:
        objective = RouteObjective(req.objective.lower())
    except ValueError:
        objective = RouteObjective.FASTEST

    # Load vehicle if provided
    vehicle = None
    if req.vehicle_id:
        vehicle = db.query(VehicleProfile).filter(VehicleProfile.id == req.vehicle_id).first()

    # User preferences
    user_prefs = current_user.preferences if current_user else None

    # Calculate routes
    routes = advanced_router.calculate_multimodal_routes(
        req.origin_latitude, req.origin_longitude,
        req.destination_latitude, req.destination_longitude,
        profile=profile,
        objective=objective,
        avoid_tolls=req.avoid_tolls,
        avoid_highways=req.avoid_highways,
        require_accessible=req.require_accessible,
        vehicle=vehicle,
        user_prefs=user_prefs
    )

    # Attach accessibility evaluations
    results = []
    for r in routes:
        r_dict = r.to_dict()
        acc_eval = accessibility_router.evaluate_route_accessibility(r, user_prefs)
        r_dict["accessibility_audit"] = acc_eval
        results.append(r_dict)

    return {
        "status": "SUCCESS",
        "route_count": len(results),
        "profile": profile.value,
        "routes": results
    }


@router.post("/dynamic-reroute")
def check_hazards_and_reroute(req: DynamicRerouteRequest, db: Session = Depends(get_db)):
    polyline_tuples = [(p[0], p[1]) for p in req.polyline]
    
    # Fetch active verified road reports
    active_reports = db.query(RoadConditionReport).filter(
        RoadConditionReport.status.in_(["VERIFIED", "PENDING"])
    ).all()

    conflicts = dynamic_rerouter.detect_conflicts(polyline_tuples, active_reports)
    has_blocking = any(c.get("is_blocking") for c in conflicts)

    detour = None
    if has_blocking:
        from src.backend.routing.provider_interface import RouteAlternative
        dummy = RouteAlternative(
            route_id=req.route_id or "CURRENT",
            title="Active Route",
            objective=RouteObjective.FASTEST,
            distance_meters=5000.0,
            duration_seconds=600.0,
            polyline=polyline_tuples,
            summary_roads=["Current Route Corridor"]
        )
        detour = dynamic_rerouter.generate_detour(dummy, conflicts, advanced_router)

    return {
        "route_compromised": has_blocking,
        "conflicts_count": len(conflicts),
        "conflicts": conflicts,
        "recommended_detour": detour.to_dict() if detour else None
    }


@router.post("/save")
def save_route(
    req: SaveRouteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    saved = SavedRoute(
        user_id=current_user.id,
        title=req.title,
        origin_name=req.origin_name,
        origin_lat=req.origin_lat,
        origin_lon=req.origin_lon,
        dest_name=req.dest_name,
        dest_lat=req.dest_lat,
        dest_lon=req.dest_lon,
        travel_mode=req.travel_mode,
        distance_km=req.distance_km,
        duration_minutes=req.duration_minutes,
        polyline=req.polyline
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return {"message": "Route saved successfully", "saved_route_id": saved.id}


@router.get("/saved")
def list_saved_routes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    routes = db.query(SavedRoute).filter(SavedRoute.user_id == current_user.id).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "origin_name": r.origin_name,
            "dest_name": r.dest_name,
            "travel_mode": r.travel_mode,
            "distance_km": r.distance_km,
            "duration_minutes": r.duration_minutes,
            "created_at": r.created_at.isoformat()
        }
        for r in routes
    ]
