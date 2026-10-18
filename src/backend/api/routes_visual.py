"""
Camera-Assisted Visual Navigation API Router
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.backend.database.connection import get_db
from src.backend.visual_navigation.visual_nav_service import VisualNavigationService

router = APIRouter(prefix="/visual-nav", tags=["Camera-Assisted Visual Navigation"])


@router.get("/landmarks")
def get_landmarks_in_viewport(
    latitude: float = Query(...),
    longitude: float = Query(...),
    heading_degrees: float = Query(..., description="Device camera heading compass bearing [0, 360)"),
    camera_fov_degrees: float = Query(default=65.0),
    max_distance_meters: float = Query(default=500.0),
    db: Session = Depends(get_db)
):
    landmarks = VisualNavigationService.get_landmarks_in_camera_view(
        db,
        user_lat=latitude,
        user_lon=longitude,
        user_heading_degrees=heading_degrees,
        camera_fov_degrees=camera_fov_degrees,
        max_distance_meters=max_distance_meters
    )
    return {
        "visible_landmarks_count": len([l for l in landmarks if l["is_in_camera_view"]]),
        "total_nearby_landmarks": len(landmarks),
        "landmarks": landmarks
    }
