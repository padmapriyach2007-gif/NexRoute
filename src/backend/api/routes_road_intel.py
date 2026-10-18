"""
Real-Time Road Intelligence API Router
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.backend.database.connection import get_db
from src.backend.database.models import User, RoadConditionReport
from src.backend.auth.security import get_current_user_optional, get_current_user
from src.backend.road_intelligence.condition_service import RoadConditionService
from src.backend.road_intelligence.spatial_query import (
    find_reports_in_radius, find_reports_along_corridor
)

router = APIRouter(prefix="/road-conditions", tags=["Real-Time Road Intelligence"])


class CreateReportRequest(BaseModel):
    category: str  # POTHOLE, FLOODING, ROAD_CLOSURE, ACCIDENT, BROKEN_SIGNAL, DANGEROUS_TURN, PEDESTRIAN_HAZARD, POOR_LIGHTING
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    latitude: float
    longitude: float
    description: str
    road_name: Optional[str] = None
    photo_url: Optional[str] = None
    affected_radius_meters: float = 50.0


class ConfirmReportRequest(BaseModel):
    confirmation_type: str  # STILL_PRESENT, CLEARED, DISPUTE, ABUSE
    notes: Optional[str] = None


class CorridorQueryRequest(BaseModel):
    polyline: List[List[float]]
    corridor_meters: float = 100.0
    include_pending: bool = True


@router.post("/report")
def submit_road_condition_report(
    req: CreateReportRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    reporter_id = current_user.id if current_user else None
    reporter_type = current_user.role if current_user else "COMMUNITY"

    report, is_new = RoadConditionService.create_or_corroborate_report(
        db=db,
        reporter_id=reporter_id,
        reporter_type=reporter_type,
        category=req.category,
        severity=req.severity,
        latitude=req.latitude,
        longitude=req.longitude,
        description=req.description,
        road_name=req.road_name,
        photo_url=req.photo_url,
        affected_radius_meters=req.affected_radius_meters
    )

    return {
        "status": "RECORDED",
        "is_new_report": is_new,
        "action": "CREATED_NEW_REPORT" if is_new else "CORROBORATED_EXISTING_INCIDENT",
        "report": {
            "id": report.id,
            "category": report.category,
            "severity": report.severity,
            "status": report.status,
            "confidence_score": report.confidence_score,
            "upvotes": report.upvotes,
            "road_name": report.road_name,
            "description": report.description,
            "location": {"latitude": report.latitude, "longitude": report.longitude},
            "expires_at": report.expires_at.isoformat()
        }
    }


@router.post("/{report_id}/confirm")
def confirm_or_dispute_report(
    report_id: str,
    req: ConfirmReportRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None
    try:
        report = RoadConditionService.confirm_or_dispute_report(
            db=db,
            report_id=report_id,
            user_id=user_id,
            confirmation_type=req.confirmation_type,
            notes=req.notes
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "status": "UPDATED",
        "report_id": report.id,
        "new_status": report.status,
        "confidence_score": report.confidence_score,
        "upvotes": report.upvotes,
        "downvotes": report.downvotes,
        "dispute_count": report.dispute_count
    }


@router.get("/radius")
def query_reports_by_radius(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius_meters: float = Query(default=1000.0),
    include_pending: bool = Query(default=True),
    db: Session = Depends(get_db)
):
    results = find_reports_in_radius(
        db, latitude, longitude, radius_meters, include_pending=include_pending
    )

    return [
        {
            "id": r.id,
            "category": r.category,
            "severity": r.severity,
            "status": r.status,
            "confidence_score": r.confidence_score,
            "distance_meters": round(dist, 1),
            "description": r.description,
            "road_name": r.road_name,
            "location": {"latitude": r.latitude, "longitude": r.longitude},
            "created_at": r.created_at.isoformat(),
            "expires_at": r.expires_at.isoformat()
        }
        for r, dist in results
    ]


@router.post("/corridor")
def query_reports_along_corridor(
    req: CorridorQueryRequest,
    db: Session = Depends(get_db)
):
    polyline_tuples = [(p[0], p[1]) for p in req.polyline]
    results = find_reports_along_corridor(
        db, polyline_tuples, corridor_meters=req.corridor_meters, include_pending=req.include_pending
    )

    return {
        "incident_count": len(results),
        "incidents": [
            {
                "id": r.id,
                "category": r.category,
                "severity": r.severity,
                "status": r.status,
                "confidence_score": r.confidence_score,
                "distance_to_route_meters": round(dist, 1),
                "description": r.description,
                "road_name": r.road_name,
                "location": {"latitude": r.latitude, "longitude": r.longitude}
            }
            for r, dist in results
        ]
    }


@router.post("/cleanup-expired")
def trigger_expiry_cleanup(db: Session = Depends(get_db)):
    expired_count = RoadConditionService.expire_stale_reports(db)
    return {"message": "Expired reports cleaned up", "expired_count": expired_count}
