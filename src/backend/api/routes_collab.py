"""
Collaborative Maps API Router
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.backend.database.connection import get_db
from src.backend.database.models import User, CollaborativeMap
from src.backend.auth.security import get_current_user
from src.backend.collaboration.collab_service import CollaborativeService

router = APIRouter(prefix="/collaborative", tags=["Collaborative Maps & Trip Planning"])


class CreateMapRequest(BaseModel):
    title: str
    description: Optional[str] = None


class AddStopRequest(BaseModel):
    title: str
    latitude: float
    longitude: float
    notes: Optional[str] = None
    sequence_order: Optional[int] = None


class VoteStopRequest(BaseModel):
    vote_value: int  # +1 or -1


@router.post("/create")
def create_shared_map(
    req: CreateMapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    collab_map = CollaborativeService.create_collaborative_map(
        db, current_user.id, req.title, req.description
    )
    return {
        "message": "Collaborative map created",
        "map_id": collab_map.id,
        "share_token": collab_map.share_token
    }


@router.post("/{map_id}/stops")
def add_collaborative_stop(
    map_id: str,
    req: AddStopRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        stop = CollaborativeService.add_stop(
            db, map_id, current_user.id, req.title, req.latitude, req.longitude,
            notes=req.notes, sequence_order=req.sequence_order
        )
        return {
            "message": "Stop added successfully",
            "stop_id": stop.id,
            "title": stop.title,
            "sequence_order": stop.sequence_order
        }
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))


@router.post("/stops/{stop_id}/vote")
def vote_on_trip_stop(
    stop_id: str,
    req: VoteStopRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        stop = CollaborativeService.vote_on_stop(
            db, stop_id, current_user.id, req.vote_value
        )
        return {"stop_id": stop.id, "new_vote_score": stop.vote_score}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))


@router.get("/{map_id}")
def get_collaborative_map(
    map_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    collab_map = db.query(CollaborativeMap).filter(CollaborativeMap.id == map_id).first()
    if not collab_map:
        raise HTTPException(status_code=404, detail="Collaborative map not found")

    return {
        "id": collab_map.id,
        "title": collab_map.title,
        "description": collab_map.description,
        "share_token": collab_map.share_token,
        "stops": [
            {
                "id": s.id,
                "title": s.title,
                "sequence_order": s.sequence_order,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "notes": s.notes,
                "vote_score": s.vote_score
            }
            for s in collab_map.stops
        ],
        "members": [
            {
                "user_id": m.user_id,
                "role": m.role
            }
            for m in collab_map.members
        ]
    }
