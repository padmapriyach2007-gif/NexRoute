"""
AI Trip-Planning Agent API Router
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.backend.database.connection import get_db
from src.backend.ai_agent.trip_planner_agent import TripPlannerAgent

router = APIRouter(prefix="/ai-planner", tags=["AI Trip-Planning Agent"])


class PlanTripRequest(BaseModel):
    prompt: str
    user_latitude: float = 16.2335
    user_longitude: float = 80.5505
    days: int = 1
    preferred_mode: str = "driving"


@router.post("/plan-trip")
def plan_ai_trip(req: PlanTripRequest, db: Session = Depends(get_db)):
    agent = TripPlannerAgent(db)
    itinerary = agent.plan_trip(
        prompt=req.prompt,
        user_lat=req.user_latitude,
        user_lon=req.user_longitude,
        days=req.days,
        preferred_mode=req.preferred_mode
    )
    return itinerary
