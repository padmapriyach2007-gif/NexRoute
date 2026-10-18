"""
Real-World Arrival & Entrance Navigation API Router
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.backend.database.connection import get_db
from src.backend.arrival.entrance_service import EntranceService

router = APIRouter(prefix="/arrival", tags=["Real-World Arrival & Entrance Navigation"])


class ArrivalPlanRequest(BaseModel):
    place_id: str
    user_latitude: float = 16.2335
    user_longitude: float = 80.5505
    travel_mode: str = "driving"
    require_accessible: bool = False


@router.post("/plan")
def plan_arrival_and_entrance(req: ArrivalPlanRequest, db: Session = Depends(get_db)):
    try:
        plan = EntranceService.plan_final_approach(
            db=db,
            place_id=req.place_id,
            user_lat=req.user_latitude,
            user_lon=req.user_longitude,
            travel_mode=req.travel_mode,
            require_accessible=req.require_accessible
        )
        return plan
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
