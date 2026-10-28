"""
OSRM Routing Provider
Fetches live route geometries, maneuvers, steps, and alternatives from OpenStreetMap OSRM.
"""

import json
import logging
import urllib.request
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple

from src.backend.config import settings
from src.backend.routing.provider_interface import (
    RoutingProvider, RoutingProfile, RouteObjective, RouteAlternative, Maneuver
)

logger = logging.getLogger("pathfinder.osrm")


class OSRMRoutingProvider(RoutingProvider):
    def __init__(self, base_url: Optional[str] = None, timeout_sec: Optional[float] = None):
        self.base_url = (base_url or settings.OSRM_BASE_URL).rstrip("/")
        self.timeout_sec = timeout_sec or settings.ROUTING_TIMEOUT_SEC

    def _map_profile(self, profile: RoutingProfile) -> str:
        if profile == RoutingProfile.WALKING:
            return "foot"
        elif profile == RoutingProfile.CYCLING:
            return "bike"
        return "driving"

    def calculate_route(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        profile: RoutingProfile = RoutingProfile.DRIVING,
        objective: RouteObjective = RouteObjective.FASTEST,
        avoid_tolls: bool = False,
        avoid_highways: bool = False
    ) -> List[RouteAlternative]:
        osrm_profile = self._map_profile(profile)
        # OSRM coordinates are formatted as {lon},{lat}
        url = (
            f"{self.base_url}/route/v1/{osrm_profile}/"
            f"{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
            f"?overview=full&geometries=geojson&steps=true&alternatives=true"
        )
        
        from src.backend.routing.route_cache import RouteCacheManager
        cache_mgr = RouteCacheManager.get_instance()
        cache_key = cache_mgr._generate_key(
            origin_lat, origin_lon, dest_lat, dest_lon,
            osrm_profile, f"tolls:{avoid_tolls}|hw:{avoid_highways}"
        )

        def _fetch_from_osrm() -> List[RouteAlternative]:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Pathfinder-NextGenMaps/2.5 (contact@pathfinder.org)"}
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_sec) as response:
                    if response.status != 200:
                        logger.warning(f"OSRM returned non-200 status {response.status}")
                        return []
                    payload = json.loads(response.read().decode("utf-8"))
            except Exception as e:
                logger.info(f"OSRM service unavailable ({e}). Falling back to internal engine.")
                return []

            if payload.get("code") != "Ok" or not payload.get("routes"):
                return []

            routes = []
            for idx, r in enumerate(payload["routes"]):
                geom = r.get("geometry", {})
                coords = geom.get("coordinates", [])  # [[lon, lat], ...]
                polyline = [(c[1], c[0]) for c in coords]
                distance_meters = float(r.get("distance", 0.0))
                duration_seconds = float(r.get("duration", 0.0))
                
                maneuvers = []
                summary_roads = []
                legs = r.get("legs", [])
                for leg in legs:
                    for step in leg.get("steps", []):
                        step_maneuver = step.get("maneuver", {})
                        road_name = step.get("name") or "Unnamed Road"
                        if road_name and road_name not in summary_roads and road_name != "Unnamed Road":
                            summary_roads.append(road_name)
                        maneuvers.append(Maneuver(
                            instruction=step_maneuver.get("type", "maneuver") + f" on {road_name}",
                            action_type=step_maneuver.get("modifier", step_maneuver.get("type", "continue")).upper(),
                            road_name=road_name,
                            distance_meters=float(step.get("distance", 0.0)),
                            duration_seconds=float(step.get("duration", 0.0)),
                            location=(step_maneuver.get("location", [origin_lon, origin_lat])[1], step_maneuver.get("location", [origin_lon, origin_lat])[0])
                        ))

                via_desc = f"Via {summary_roads[0]}" if summary_roads else f"Route Alternative #{idx + 1}"
                if len(summary_roads) > 1:
                    via_desc += f" & {summary_roads[1]}"

                routes.append(RouteAlternative(
                    route_id=f"osrm_route_{idx + 1}",
                    title=f"OSRM {osrm_profile.capitalize()} Route {idx + 1}",
                    summary=via_desc,
                    distance_meters=distance_meters,
                    duration_seconds=duration_seconds,
                    polyline=polyline,
                    maneuvers=maneuvers,
                    objective=objective,
                    confidence=0.92 if idx == 0 else 0.82
                ))
            return routes

        return cache_mgr.execute_single_flight(cache_key, _fetch_from_osrm, ttl_sec=900.0)

