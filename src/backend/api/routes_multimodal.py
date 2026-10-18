"""
Multimodal Journey Planning API Router
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.backend.database.connection import get_db
from src.backend.multimodal.journey_planner import MultimodalJourneyPlanner

router = APIRouter(prefix="/multimodal", tags=["Multimodal Journey Planning"])


class MultimodalPlanRequest(BaseModel):
    origin_latitude: float
    origin_longitude: float
    destination_latitude: float
    destination_longitude: float
    departure_time: str = "08:00"


@router.post("/plan")
def plan_multimodal_journey(req: MultimodalPlanRequest, db: Session = Depends(get_db)):
    options = MultimodalJourneyPlanner.plan_multimodal_itinerary(
        db,
        origin_lat=req.origin_latitude,
        origin_lon=req.origin_longitude,
        dest_lat=req.destination_latitude,
        dest_lon=req.destination_longitude,
        departure_time_str=req.departure_time
    )
    return {
        "status": "SUCCESS",
        "itinerary_options_count": len(options),
        "options": options
    }
