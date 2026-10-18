"""
Weather-Aware Routing API Router
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Query
from pydantic import BaseModel

from src.backend.weather.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["Weather-Aware & Environment-Aware Routing"])


class RouteCorridorWeatherRequest(BaseModel):
    polyline: List[List[float]]


@router.get("/current")
def get_current_weather(
    latitude: float = Query(default=16.2335),
    longitude: float = Query(default=80.5505)
):
    return WeatherService.get_weather_at_location(latitude, longitude)


@router.post("/corridor")
def get_route_weather_summary(req: RouteCorridorWeatherRequest):
    polyline_tuples = [(p[0], p[1]) for p in req.polyline]
    return WeatherService.evaluate_route_weather(polyline_tuples)
