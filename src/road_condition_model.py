"""
Road Condition and Navigation Constraint Data Model for CampusAegis 2.0
Provides truthful, normalized data representations for:
- Verified road closures and maintenance restrictions
- Traffic delays and congestion factors
- Multi-objective optimization preferences
- Operating modes (LIVE_ROUTING, STANDARD_ROUTING, CONTROLLED_DEMO)
Zero synthetic hazards or simulated disasters.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class OperatingMode(Enum):
    LIVE_ROUTING = "LIVE_ROUTING"          # Live OSM road graph + live routing API
    STANDARD_ROUTING = "STANDARD_ROUTING"  # Resilient offline local road graph routing
    CONTROLLED_DEMO = "CONTROLLED_DEMO"    # Labeled demonstration fixtures (NOT LIVE)


class RestrictionType(Enum):
    ROAD_WORK = "ROAD_WORK"                    # Maintenance, resurfacing, utility repair
    LANE_CLOSURE = "LANE_CLOSURE"              # Partial capacity reduction
    ROAD_CLOSURE = "ROAD_CLOSURE"              # Full segment closed to vehicular traffic
    BRIDGE_MAINTENANCE = "BRIDGE_MAINTENANCE"  # Structural inspection / maintenance
    WEIGHT_LIMIT = "WEIGHT_LIMIT"              # Vehicle restriction
    PEDESTRIAN_ONLY = "PEDESTRIAN_ONLY"        # Inaccessible to motor vehicles
    STAIRS_NO_RAMP = "STAIRS_NO_RAMP"          # Inaccessible to wheelchairs


class TrafficSeverity(Enum):
    CLEAR = "CLEAR"            # Free flow (1.0x baseline travel time)
    MODERATE = "MODERATE"      # Slowdown (1.25x baseline travel time)
    HEAVY = "HEAVY"            # Severe congestion (1.6x baseline travel time)
    STANDSTILL = "STANDSTILL"  # Gridlock (2.5x baseline travel time)


class OptimizationObjective(Enum):
    FASTEST = "FASTEST"        # Minimize travel time (time weight = 0.85, distance weight = 0.15)
    SHORTEST = "SHORTEST"      # Minimize distance (time weight = 0.15, distance weight = 0.85)
    BALANCED = "BALANCED"      # Equal balance (time weight = 0.50, distance weight = 0.50)
    ACCESSIBLE = "ACCESSIBLE"  # Strict accessibility hard constraints


@dataclass
class RoadRestriction:
    """
    Represents a verified physical road restriction, construction work, or closure.
    """
    restriction_id: str
    restriction_type: RestrictionType
    road_name: str
    latitude: float
    longitude: float
    affected_radius_meters: float = 80.0
    description: str = ""
    is_hard_closure: bool = True               # If True, vehicles cannot traverse
    accessible_to_wheelchairs: bool = False
    source: str = "OFFICIAL_TRANSIT_FEED"
    is_demonstration: bool = False
    reported_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "restriction_id": self.restriction_id,
            "restriction_type": self.restriction_type.value,
            "road_name": self.road_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "radius_meters": self.affected_radius_meters,
            "description": self.description,
            "is_hard_closure": self.is_hard_closure,
            "accessible_to_wheelchairs": self.accessible_to_wheelchairs,
            "source": self.source,
            "is_demonstration": self.is_demonstration,
            "reported_at": self.reported_at.isoformat()
        }


@dataclass
class TrafficCondition:
    """
    Represents verified traffic speed factor and delay on a road segment.
    """
    segment_id: str
    road_name: str
    severity: TrafficSeverity
    delay_minutes: float = 0.0
    speed_factor: float = 1.0  # 1.0 = normal, 0.5 = half speed
    source: str = "TRANSIT_TELEMETRY"
    is_demonstration: bool = False
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "road_name": self.road_name,
            "severity": self.severity.value,
            "delay_minutes": round(self.delay_minutes, 1),
            "speed_factor": round(self.speed_factor, 2),
            "source": self.source,
            "is_demonstration": self.is_demonstration,
            "updated_at": self.updated_at.isoformat()
        }
