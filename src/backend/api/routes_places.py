"""
Place Discovery & Recommendations API Router
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.backend.database.connection import get_db
from src.backend.database.models import Place
from src.backend.place_discovery.discovery_service import PlaceDiscoveryService

router = APIRouter(prefix="/places", tags=["AI-Powered Place Discovery"])


class PlaceComparisonRequest(BaseModel):
    place_ids: List[str]
    user_latitude: float
    user_longitude: float


@router.get("/discover")
def discover_places(
    query: str = Query(..., description="Natural language search prompt, e.g. 'Quiet cafe with wifi, outlets and parking'"),
    latitude: float = Query(default=16.2335),
    longitude: float = Query(default=80.5505),
    radius_km: float = Query(default=15.0),
    limit: int = Query(default=10),
    db: Session = Depends(get_db)
):
    results = PlaceDiscoveryService.search_and_rank(
        db, query, latitude, longitude, radius_km=radius_km, limit=limit
    )
    return {
        "query": query,
        "result_count": len(results),
        "places": results
    }


@router.post("/compare")
def compare_places(
    req: PlaceComparisonRequest,
    db: Session = Depends(get_db)
):
    return PlaceDiscoveryService.compare_places(
        db, req.place_ids, req.user_latitude, req.user_longitude
    )


@router.get("/{place_id}")
def get_place_details(place_id: str, db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    return {
        "id": place.id,
        "name": place.name,
        "category": place.category,
        "rating": place.rating,
        "reviews_count": place.reviews_count,
        "price_level": place.price_level,
        "address": place.address,
        "description": place.description,
        "amenities": place.amenities,
        "is_accessible": place.is_accessible,
        "location": {"latitude": place.latitude, "longitude": place.longitude},
        "entrances": [
            {
                "id": e.id,
                "name": e.name,
                "type": e.entrance_type,
                "is_wheelchair_accessible": e.is_wheelchair_accessible,
                "coordinates": {"latitude": e.latitude, "longitude": e.longitude}
            }
            for e in place.entrances
        ],
        "parking": [
            {
                "id": p.id,
                "name": p.name,
                "capacity": p.capacity,
                "available_spaces": p.available_spaces,
                "has_ev_charging": p.has_ev_charging,
                "hourly_rate_inr": p.hourly_rate_inr
            }
            for p in place.parking_lots
        ]
    }
