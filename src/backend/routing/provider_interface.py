"""
Routing Provider Abstraction Interface
Defines the standard contract for geospatial route calculation engines (OSRM, GraphHopper, Internal Graph).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class RoutingProfile(str, Enum):
    DRIVING = "driving"
    WALKING = "walking"
    CYCLING = "cycling"
    MOTORCYCLE = "motorcycle"
    HEAVY_VEHICLE = "heavy_vehicle"
    FLIGHT = "flight"
    WATERWAY = "waterway"


class RouteObjective(str, Enum):
    FASTEST = "fastest"
    SHORTEST = "shortest"
    ECO = "eco"
    FEWER_TOLLS = "fewer_tolls"
    ROAD_QUALITY = "road_quality"


@dataclass
class Maneuver:
    instruction: str
    action_type: str  # DEPART, TURN_LEFT, TURN_RIGHT, MERGE, ROUNDABOUT, ARRIVE
    road_name: str
    distance_meters: float
    duration_seconds: float
    location: Tuple[float, float]
    lane_guidance: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instruction": self.instruction,
            "action_type": self.action_type,
            "road_name": self.road_name,
            "distance_meters": round(self.distance_meters, 1),
            "duration_seconds": round(self.duration_seconds, 1),
            "location": {"latitude": self.location[0], "longitude": self.location[1]},
            "lane_guidance": self.lane_guidance
        }


@dataclass
class RouteAlternative:
    route_id: str
    title: str
    objective: RouteObjective
    distance_meters: float
    duration_seconds: float
    polyline: List[Tuple[float, float]]
    maneuvers: List[Maneuver] = field(default_factory=list)
    summary: str = ""
    summary_roads: List[str] = field(default_factory=list)
    has_tolls: bool = False
    toll_fee_inr: float = 0.0
    estimated_fuel_litres: float = 0.0
    estimated_fuel_cost_inr: float = 0.0
    estimated_ev_kwh: float = 0.0
    estimated_ev_cost_inr: float = 0.0
    road_quality_score: float = 0.85
    is_wheelchair_accessible: bool = True
    accessibility_confidence: float = 0.9  # 1.0 = verified, 0.5 = unverified
    confidence: float = 0.9
    provider_source: str = "OSRM"

    @property
    def distance_km(self) -> float:
        return round(self.distance_meters / 1000.0, 2)

    @property
    def duration_minutes(self) -> float:
        return round(self.duration_seconds / 60.0, 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "route_id": self.route_id,
            "title": self.title,
            "objective": self.objective.value if hasattr(self.objective, "value") else str(self.objective),
            "distance_km": self.distance_km,
            "duration_minutes": self.duration_minutes,
            "distance_meters": round(self.distance_meters, 1),
            "duration_seconds": round(self.duration_seconds, 1),
            "polyline": [[p[0], p[1]] for p in self.polyline],
            "polyline_count": len(self.polyline),
            "maneuvers": [m.to_dict() for m in self.maneuvers],
            "summary_roads": self.summary_roads,
            "cost_breakdown": {
                "has_tolls": self.has_tolls,
                "toll_fee_inr": self.toll_fee_inr,
                "fuel_litres": round(self.estimated_fuel_litres, 2),
                "fuel_cost_inr": round(self.estimated_fuel_cost_inr, 2),
                "ev_energy_kwh": round(self.estimated_ev_kwh, 2),
                "ev_cost_inr": round(self.estimated_ev_cost_inr, 2),
            },
            "quality_and_safety": {
                "road_quality_score": round(self.road_quality_score, 2),
                "is_wheelchair_accessible": self.is_wheelchair_accessible,
                "accessibility_confidence": round(self.accessibility_confidence, 2)
            },
            "provider_source": self.provider_source
        }


class RoutingProvider(ABC):
    @abstractmethod
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
        """Calculates routes using the underlying provider."""
        pass
