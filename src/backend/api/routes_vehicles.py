"""
Vehicle Profiles & EV Planning API Router
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.backend.database.connection import get_db
from src.backend.database.models import User, VehicleProfile
from src.backend.auth.security import get_current_user
from src.backend.routing.vehicle_router import VehicleRouter
from src.backend.routing.provider_interface import RouteAlternative

router = APIRouter(prefix="/vehicles", tags=["Vehicle-Aware Routing & EV Planning"])
vehicle_router = VehicleRouter()


class CreateVehicleRequest(BaseModel):
    name: str
    vehicle_type: str  # CAR, MOTORCYCLE, EV, BICYCLE, COMMERCIAL_TRUCK
    fuel_type: str = "PETROL"
    fuel_efficiency_km_per_litre: float = 15.0
    battery_capacity_kwh: float = 0.0
    electric_range_km: float = 0.0
    current_charge_percent: float = 100.0
    connector_type: str = "CCS2"
    height_meters: float = 1.5
    weight_tons: float = 1.5
    is_commercial: bool = False
    is_default: bool = False


class PlanEVStopsRequest(BaseModel):
    vehicle_id: str
    route_distance_km: float
    origin_latitude: float = 16.2335
    origin_longitude: float = 80.5505


@router.post("/")
def create_vehicle_profile(
    req: CreateVehicleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    veh = VehicleProfile(
        user_id=current_user.id,
        name=req.name,
        vehicle_type=req.vehicle_type.upper(),
        fuel_type=req.fuel_type.upper(),
        fuel_efficiency_km_per_litre=req.fuel_efficiency_km_per_litre,
        battery_capacity_kwh=req.battery_capacity_kwh,
        electric_range_km=req.electric_range_km,
        current_charge_percent=req.current_charge_percent,
        connector_type=req.connector_type,
        height_meters=req.height_meters,
        weight_tons=req.weight_tons,
        is_commercial=req.is_commercial,
        is_default=req.is_default
    )
    db.add(veh)
    db.commit()
    db.refresh(veh)
    return {"message": "Vehicle profile created successfully", "vehicle_id": veh.id}


@router.get("/")
def list_user_vehicles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vehicles = db.query(VehicleProfile).filter(VehicleProfile.user_id == current_user.id).all()
    return [
        {
            "id": v.id,
            "name": v.name,
            "vehicle_type": v.vehicle_type,
            "fuel_type": v.fuel_type,
            "fuel_efficiency_km_per_litre": v.fuel_efficiency_km_per_litre,
            "battery_capacity_kwh": v.battery_capacity_kwh,
            "electric_range_km": v.electric_range_km,
            "current_charge_percent": v.current_charge_percent,
            "connector_type": v.connector_type,
            "height_meters": v.height_meters,
            "weight_tons": v.weight_tons,
            "is_default": v.is_default
        }
        for v in vehicles
    ]


@router.post("/plan-ev-stops")
def plan_ev_charging_stops(
    req: PlanEVStopsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vehicle = db.query(VehicleProfile).filter(
        VehicleProfile.id == req.vehicle_id,
        VehicleProfile.user_id == current_user.id
    ).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    from src.backend.routing.provider_interface import RouteAlternative, RouteObjective
    dummy = RouteAlternative(
        route_id="EV_EVAL",
        title="EV Route",
        objective=RouteObjective.FASTEST,
        distance_meters=req.route_distance_km * 1000.0,
        duration_seconds=req.route_distance_km * 70.0,
        polyline=[(req.origin_latitude, req.origin_longitude)]
    )

    plan = vehicle_router.plan_ev_charging_stops(dummy, vehicle, db)
    return plan
