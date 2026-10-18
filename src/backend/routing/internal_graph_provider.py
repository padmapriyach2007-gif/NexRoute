"""
Internal Graph Routing Provider
Wraps the project's internal graph-based routing algorithms (A*, Dijkstra, Yen's K-Shortest Paths)
and regional Andhra road network topology.
"""

from typing import List, Optional
from src.backend.routing.provider_interface import (
    RoutingProvider, RoutingProfile, RouteObjective, RouteAlternative, Maneuver
)
from src.route_engine import RealWorldRouteEngine, TravelMode, RouteOption


class InternalGraphRoutingProvider(RoutingProvider):
    def __init__(self):
        self.engine = RealWorldRouteEngine()

    def _map_mode(self, profile: RoutingProfile) -> TravelMode:
        if profile == RoutingProfile.WALKING:
            return TravelMode.WALKING
        elif profile == RoutingProfile.CYCLING:
            return TravelMode.BICYCLING
        elif profile == RoutingProfile.MOTORCYCLE:
            return TravelMode.MOTORCYCLE
        elif profile == RoutingProfile.HEAVY_VEHICLE:
            return TravelMode.TRUCK
        return TravelMode.DRIVING

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
        mode = self._map_mode(profile)
        candidates: List[RouteOption] = self.engine.calculate_routes(
            origin_lat, origin_lon, dest_lat, dest_lon, mode=mode
        )

        results = []
        for idx, c in enumerate(candidates):
            maneuvers = []
            for s in c.steps:
                loc = s.get("location", (origin_lat, origin_lon))
                if isinstance(loc, (list, tuple)) and len(loc) >= 2:
                    loc_tuple = (float(loc[0]), float(loc[1]))
                else:
                    loc_tuple = (origin_lat, origin_lon)

                maneuvers.append(Maneuver(
                    instruction=s.get("instruction", "Proceed"),
                    action_type="TURN",
                    road_name=s.get("road_name", "Local Road"),
                    distance_meters=float(s.get("distance_m", 500.0)),
                    duration_seconds=float(s.get("duration_s", 60.0)),
                    location=loc_tuple
                ))

            # Determine objective type
            if idx == 0:
                alt_obj = RouteObjective.FASTEST
            elif idx == 1:
                alt_obj = RouteObjective.ECO
            elif idx == 2:
                alt_obj = RouteObjective.SHORTEST
            else:
                alt_obj = RouteObjective.ROAD_QUALITY

            alt = RouteAlternative(
                route_id=f"GRAPH_{c.route_id}",
                title=c.name,
                objective=alt_obj,
                distance_meters=c.distance_meters,
                duration_seconds=c.duration_seconds,
                polyline=c.polyline,
                maneuvers=maneuvers,
                summary_roads=c.summary_roads,
                road_quality_score=0.90 if idx == 0 else 0.82,
                is_wheelchair_accessible=c.is_accessible,
                accessibility_confidence=1.0 if c.accessibility_verified else 0.7,
                provider_source=f"Autonomous Graph ({c.algorithm_used})"
            )
            results.append(alt)

        return results
