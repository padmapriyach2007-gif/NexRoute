"""
Unified Hazard Data Model for CampusAegis v2.0
Defines normalized schemas for real, simulated, and hybrid public safety hazards.
Supports spatial geometries (points, circular buffers, road segments, polygons).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid


class EnvironmentMode(str, Enum):
    REAL = "REAL"
    SIMULATED = "SIMULATED"
    HYBRID = "HYBRID"


class OperatingMode(str, Enum):
    REAL_HAZARD_MODE = "REAL_HAZARD_MODE"
    SIMULATION_MODE = "SIMULATION_MODE"
    HYBRID_MODE = "HYBRID_MODE"


class HazardType(str, Enum):
    # Structural & Urban
    BUILDING_FIRE = "BUILDING_FIRE"
    WILDFIRE = "WILDFIRE"
    SMOKE_PLUME = "SMOKE_PLUME"
    CHEMICAL_LEAK = "CHEMICAL_LEAK"
    GAS_LEAK = "GAS_LEAK"
    
    # Infrastructure & Roads
    FLOODED_ROAD = "FLOODED_ROAD"
    ROAD_CAVE_IN = "ROAD_CAVE_IN"
    ROAD_CLOSURE = "ROAD_CLOSURE"
    VEHICLE_ACCIDENT = "VEHICLE_ACCIDENT"
    BRIDGE_DAMAGE = "BRIDGE_DAMAGE"
    
    # Building Access & Indoor
    BLOCKED_EXIT = "BLOCKED_EXIT"
    BLOCKED_STAIRCASE = "BLOCKED_STAIRCASE"
    BLOCKED_CORRIDOR = "BLOCKED_CORRIDOR"
    SHELTER_CLOSURE = "SHELTER_CLOSURE"
    
    # Natural & Environmental
    SEVERE_WEATHER = "SEVERE_WEATHER"
    EARTHQUAKE = "EARTHQUAKE"
    
    # Telemetry & Sensor Anomalies
    SENSOR_FAILURE = "SENSOR_FAILURE"
    DELAYED_FEED = "DELAYED_FEED"
    CONFLICTING_REPORTS = "CONFLICTING_REPORTS"
    RESOLVED_INCIDENT = "RESOLVED_INCIDENT"
    UNKNOWN_HAZARD = "UNKNOWN_HAZARD"


class HazardSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class VerificationStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    CONFIRMED = "CONFIRMED"
    CONFLICTING = "CONFLICTING"
    STALE = "STALE"
    RESOLVED = "RESOLVED"


class IncidentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    UNDER_EVALUATION = "UNDER_EVALUATION"
    CONTAINED = "CONTAINED"
    RESOLVED = "RESOLVED"
    EXPIRED = "EXPIRED"


class GeometryType(str, Enum):
    POINT_BUFFER = "POINT_BUFFER"
    ROAD_SEGMENT = "ROAD_SEGMENT"
    POLYGON = "POLYGON"


@dataclass
class HazardGeometry:
    geometry_type: GeometryType
    latitude: float
    longitude: float
    radius_meters: float = 150.0
    coordinates_polygon: Optional[List[Tuple[float, float]]] = None
    road_coordinates: Optional[List[Tuple[float, float]]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.geometry_type.value,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "radius_meters": self.radius_meters,
            "polygon": self.coordinates_polygon,
            "road_coordinates": self.road_coordinates
        }


@dataclass
class UnifiedIncident:
    """
    Standardized, normalized incident structure adhering to Section 4 of CampusAegis v2.0.
    Maintains strict source provenance and environment isolation.
    """
    incident_id: str
    external_source_id: str
    source_name: str
    source_type: str  # e.g., "USGS_EARTHQUAKE", "OPEN_METEO", "MUNICIPAL_DISPATCH", "SIMULATOR"
    environment: EnvironmentMode
    hazard_type: HazardType
    geometry: HazardGeometry
    affected_radius_meters: float
    severity: HazardSeverity
    confidence: float  # 0.0 to 1.0
    verification_status: VerificationStatus
    incident_status: IncidentStatus
    observed_at: datetime
    published_at: Optional[datetime] = None
    received_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    affected_road_segments: List[str] = field(default_factory=list)
    affected_buildings: List[str] = field(default_factory=list)
    source_url: Optional[str] = None
    resolution_reason: Optional[str] = None
    raw_payload: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_simulated(self) -> bool:
        return self.environment == EnvironmentMode.SIMULATED or "SIMULATED" in self.incident_id

    @property
    def is_active(self) -> bool:
        if self.incident_status in (IncidentStatus.RESOLVED, IncidentStatus.EXPIRED):
            return False
        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
            return False
        return True

    def validate(self) -> Tuple[bool, List[str]]:
        """Validates all coordinates, timestamps, and confidence bounds."""
        errors = []
        lat = self.geometry.latitude
        lon = self.geometry.longitude
        if not (-90.0 <= lat <= 90.0):
            errors.append(f"Latitude out of range [-90, 90]: {lat}")
        if not (-180.0 <= lon <= 180.0):
            errors.append(f"Longitude out of range [-180, 180]: {lon}")
        if not (0.0 <= self.confidence <= 1.0):
            errors.append(f"Confidence out of range [0.0, 1.0]: {self.confidence}")
        if self.affected_radius_meters < 0:
            errors.append(f"Radius cannot be negative: {self.affected_radius_meters}")
        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "external_source_id": self.external_source_id,
            "source_name": self.source_name,
            "source_type": self.source_type,
            "environment": self.environment.value,
            "hazard_type": self.hazard_type.value,
            "geometry": self.geometry.to_dict(),
            "affected_radius_meters": self.affected_radius_meters,
            "severity": self.severity.value,
            "confidence": round(self.confidence, 2),
            "verification_status": self.verification_status.value,
            "incident_status": self.incident_status.value,
            "observed_at": self.observed_at.isoformat(),
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "received_at": self.received_at.isoformat(),
            "last_updated_at": self.last_updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "affected_road_segments": self.affected_road_segments,
            "affected_buildings": self.affected_buildings,
            "source_url": self.source_url,
            "resolution_reason": self.resolution_reason,
            "is_simulated": self.is_simulated
        }
