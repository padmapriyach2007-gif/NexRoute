"""
Unified API v2 Router
Mounts all Next-Generation Maps backend modules under /api/v2.
"""

from fastapi import APIRouter

from src.backend.api.routes_auth import router as auth_router
from src.backend.api.routes_routing import router as routing_router
from src.backend.api.routes_road_intel import router as road_intel_router
from src.backend.api.routes_places import router as places_router
from src.backend.api.routes_arrival import router as arrival_router
from src.backend.api.routes_multimodal import router as multimodal_router
from src.backend.api.routes_vehicles import router as vehicles_router
from src.backend.api.routes_weather import router as weather_router
from src.backend.api.routes_collab import router as collab_router
from src.backend.api.routes_visual import router as visual_router
from src.backend.api.routes_ai_planner import router as ai_planner_router
from src.backend.api.routes_offline import router as offline_router
from src.backend.api.routes_ingestion import router as ingestion_router
from src.backend.api.routes_navigation import router as navigation_router

v2_router = APIRouter(prefix="/api/v2")

v2_router.include_router(auth_router)
v2_router.include_router(routing_router)
v2_router.include_router(road_intel_router)
v2_router.include_router(places_router)
v2_router.include_router(arrival_router)
v2_router.include_router(multimodal_router)
v2_router.include_router(vehicles_router)
v2_router.include_router(weather_router)
v2_router.include_router(collab_router)
v2_router.include_router(visual_router)
v2_router.include_router(ai_planner_router)
v2_router.include_router(offline_router)
v2_router.include_router(ingestion_router)
v2_router.include_router(navigation_router)
