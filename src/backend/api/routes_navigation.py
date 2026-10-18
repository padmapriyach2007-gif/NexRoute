"""
Live Virtual Travel Companion & Navigation Sessions API Router
Provides RESTful endpoints for session lifecycle, real-time location stream processing,
interactive journey timeline, and destination arrival.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.backend.database.connection import get_db
from src.backend.database.models import NavigationSession, User
from src.backend.auth.security import get_current_user_optional
from src.backend.navigation.companion_service import CompanionService


router = APIRouter(prefix="/navigation", tags=["Live Virtual Travel Companion"])


# =============================================================================
# Request & Response Schemas
# =============================================================================

class CreateSessionRequest(BaseModel):
    origin_name: str
    origin_latitude: float
    origin_longitude: float
    destination_name: str
    destination_latitude: float
    destination_longitude: float
    travel_mode: str = "walking"  # walking, running, driving, cycling, motorcycle, transit
    polyline: Optional[List[List[float]]] = None
    steps: Optional[List[Dict[str, Any]]] = None
    entrance_id: Optional[str] = None


class LocationObservationRequest(BaseModel):
    latitude: float
    longitude: float
    speed_kmh: float = 0.0
    heading: Optional[float] = None
    accuracy_meters: float = 5.0
    is_known_traffic_zone: bool = False
    timestamp: Optional[datetime] = None


class ConfirmActionRequest(BaseModel):
    action_name: str
    details: Optional[str] = None


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/sessions")
def create_navigation_session(
    req: CreateSessionRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Creates a new navigation session with ordered steps, checkpoints,
    and initializes the Live Virtual Travel Companion.
    """
    try:
        user_id = current_user.id if current_user else None
        session = CompanionService.create_session(
            db=db,
            origin_name=req.origin_name,
            origin_lat=req.origin_latitude,
            origin_lon=req.origin_longitude,
            dest_name=req.destination_name,
            dest_lat=req.destination_latitude,
            dest_lon=req.destination_longitude,
            travel_mode=req.travel_mode,
            polyline=req.polyline,
            steps_data=req.steps,
            entrance_id=req.entrance_id,
            user_id=user_id
        )
        return CompanionService.get_session_telemetry(session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sessions/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Retrieves current session state, telemetry, and timeline."""
    session = db.query(NavigationSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Navigation session not found")
    return CompanionService.get_session_telemetry(session)


@router.post("/sessions/{session_id}/start")
def start_navigation(session_id: str, db: Session = Depends(get_db)):
    """Starts live navigation for the session."""
    try:
        session = CompanionService.start_session(db, session_id)
        return CompanionService.get_session_telemetry(session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sessions/{session_id}/pause")
def pause_navigation(session_id: str, db: Session = Depends(get_db)):
    """Pauses live navigation."""
    try:
        session = CompanionService.pause_session(db, session_id)
        return CompanionService.get_session_telemetry(session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sessions/{session_id}/resume")
def resume_navigation(session_id: str, db: Session = Depends(get_db)):
    """Resumes paused navigation."""
    try:
        session = CompanionService.resume_session(db, session_id)
        return CompanionService.get_session_telemetry(session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sessions/{session_id}/cancel")
def cancel_navigation(session_id: str, db: Session = Depends(get_db)):
    """Cancels active navigation."""
    try:
        session = CompanionService.cancel_session(db, session_id)
        return CompanionService.get_session_telemetry(session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/sessions/{session_id}/steps")
def get_session_steps(session_id: str, db: Session = Depends(get_db)):
    """Returns ordered journey steps and checkpoints with completion status."""
    session = db.query(NavigationSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Navigation session not found")

    telem = CompanionService.get_session_telemetry(session)
    return telem["timeline"]


@router.post("/sessions/{session_id}/location")
def update_location(
    session_id: str,
    req: LocationObservationRequest,
    db: Session = Depends(get_db)
):
    """
    Submits a real-time location observation from the client device:
    - Filters GPS noise
    - Updates travel state machine
    - Matches to route polyline
    - Detects crossed checkpoints and completed steps
    - Returns updated companion telemetry
    """
    try:
        telemetry = CompanionService.process_location_update(
            db=db,
            session_id=session_id,
            latitude=req.latitude,
            longitude=req.longitude,
            speed_kmh=req.speed_kmh,
            heading=req.heading,
            accuracy_meters=req.accuracy_meters,
            timestamp=req.timestamp,
            is_known_traffic_zone=req.is_known_traffic_zone
        )
        return telemetry
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sessions/{session_id}/confirm_action")
def confirm_action(
    session_id: str,
    req: ConfirmActionRequest,
    db: Session = Depends(get_db)
):
    """Manually confirms an action (e.g. boarded bus, passed turn)."""
    try:
        telemetry = CompanionService.confirm_manual_action(
            db=db,
            session_id=session_id,
            action_name=req.action_name,
            details=req.details
        )
        return telemetry
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/sessions/{session_id}/summary")
def get_journey_summary(session_id: str, db: Session = Depends(get_db)):
    """Returns final journey completion summary."""
    session = db.query(NavigationSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Navigation session not found")

    elapsed_seconds = 0.0
    if session.started_at:
        end_time = session.ended_at or datetime.now(timezone.utc)
        elapsed_seconds = (end_time - session.started_at).total_seconds()

    return {
        "session_id": session.id,
        "status": session.status,
        "is_completed": session.status == "ARRIVED",
        "origin_name": session.origin_name,
        "destination_name": session.dest_name,
        "travel_mode": session.travel_mode,
        "total_distance_meters": session.total_distance_meters,
        "completed_steps_count": session.completed_steps_count,
        "total_steps_count": session.total_steps_count,
        "elapsed_seconds": round(elapsed_seconds, 1),
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "ended_at": session.ended_at.isoformat() if session.ended_at else None
    }
