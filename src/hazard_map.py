"""
Hazard Map & Geographic Impact Analysis for CampusAegis / PROJECT AI
Maps emergency reports to real-world coordinates, spatial buffers, road closures,
and calculates intersection with travel routes (polylines).
"""

import math
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class HazardSpatialType(Enum):
    POINT_BUFFER = "POINT_BUFFER"
    ROAD_SEGMENT = "ROAD_SEGMENT"
    BUILDING_ZONE = "BUILDING_ZONE"
    POLYGON = "POLYGON"


class HazardSeverity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class GeographicHazard:
    hazard_id: str
    incident_type: str
    severity: HazardSeverity
    latitude: float
    longitude: float
    radius_meters: float
    description: str
    is_confirmed: bool = True
    is_active: bool = True
    affected_road_name: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    uncertainty_score: float = 0.0  # 0.0 = completely certain, 1.0 = highly uncertain
    confidence_level: float = 1.0   # 1.0 = verified official, 0.5 = crowd report
    is_demonstration: bool = False  # Flag demonstration vs live incident data
    country: Optional[str] = None
    source: str = "EMERGENCY_FEED"

    def __post_init__(self):
        if self.uncertainty_score > 0.0 and self.confidence_level == 1.0:
            self.confidence_level = max(0.0, min(1.0, 1.0 - self.uncertainty_score))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hazard_id": self.hazard_id,
            "incident_type": self.incident_type,
            "severity": self.severity.value,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "radius_meters": self.radius_meters,
            "description": self.description,
            "is_confirmed": self.is_confirmed,
            "is_active": self.is_active,
            "affected_road_name": self.affected_road_name,
            "uncertainty_score": self.uncertainty_score,
            "confidence_level": self.confidence_level,
            "is_demonstration": self.is_demonstration,
            "country": self.country,
            "source": self.source,
        }


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two GPS coordinates in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def distance_point_to_segment_m(
    p_lat: float, p_lon: float,
    a_lat: float, a_lon: float,
    b_lat: float, b_lon: float
) -> float:
    """Calculates the minimum distance in meters from a point P to a line segment AB."""
    # Approximate using flat planar projection scaled by latitude for short segments
    lat_mid = math.radians((a_lat + b_lat) / 2.0)
    m_per_deg_lat = 111132.92
    m_per_deg_lon = 111412.84 * math.cos(lat_mid)

    ax, ay = a_lon * m_per_deg_lon, a_lat * m_per_deg_lat
    bx, by = b_lon * m_per_deg_lon, b_lat * m_per_deg_lat
    px, py = p_lon * m_per_deg_lon, p_lat * m_per_deg_lat

    ab_dx, ab_dy = bx - ax, by - ay
    seg_len_sq = ab_dx * ab_dx + ab_dy * ab_dy

    if seg_len_sq == 0:
        return math.hypot(px - ax, py - ay)

    # Project point P onto segment AB
    t = ((px - ax) * ab_dx + (py - ay) * ab_dy) / seg_len_sq
    t = max(0.0, min(1.0, t))

    closest_x = ax + t * ab_dx
    closest_y = ay + t * ab_dy

    return math.hypot(px - closest_x, py - closest_y)


class HazardMap:
    """
    Manages active geographic hazards, road closures, and spatial impact zones.
    """

    def __init__(self):
        self._hazards: Dict[str, GeographicHazard] = {}
        self._road_closures: List[str] = []

    def add_hazard(self, hazard: GeographicHazard):
        self._hazards[hazard.hazard_id] = hazard
        if hazard.affected_road_name and hazard.is_active:
            self._road_closures.append(hazard.affected_road_name.lower())

    def clear_hazard(self, hazard_id: str) -> bool:
        if hazard_id in self._hazards:
            h = self._hazards[hazard_id]
            h.is_active = False
            if h.affected_road_name and h.affected_road_name.lower() in self._road_closures:
                self._road_closures.remove(h.affected_road_name.lower())
            return True
        return False

    def clear_all_hazards(self):
        """Clears all active hazards and road closures."""
        self._hazards.clear()
        self._road_closures.clear()

    def get_active_hazards(self) -> List[GeographicHazard]:
        return [h for h in self._hazards.values() if h.is_active]

    def get_hazards_in_bounding_box(
        self,
        min_lat: float, min_lon: float,
        max_lat: float, max_lon: float
    ) -> List[GeographicHazard]:
        """Filters active hazards residing within a geographic coordinate envelope."""
        return [
            h for h in self.get_active_hazards()
            if min_lat <= h.latitude <= max_lat and min_lon <= h.longitude <= max_lon
        ]

    def ingest_external_alerts(self, alerts: List[Dict[str, Any]]) -> int:
        """
        Ingests real-time external hazard feeds (e.g., weather warnings, accident feeds, civil defense).
        Returns the count of successfully ingested active incidents.
        """
        count = 0
        for item in alerts:
            try:
                hid = item.get("hazard_id") or f"EXT_{int(time.time())}_{count}"
                sev_str = str(item.get("severity", "HIGH")).upper()
                sev = HazardSeverity[sev_str] if sev_str in HazardSeverity.__members__ else HazardSeverity.HIGH
                h = GeographicHazard(
                    hazard_id=hid,
                    incident_type=item.get("incident_type", "INCIDENT"),
                    severity=sev,
                    latitude=float(item["latitude"]),
                    longitude=float(item["longitude"]),
                    radius_meters=float(item.get("radius_meters", 150.0)),
                    description=item.get("description", "Reported incident"),
                    affected_road_name=item.get("affected_road_name"),
                    confidence_level=float(item.get("confidence_level", 0.9)),
                    is_demonstration=bool(item.get("is_demonstration", False)),
                    source=item.get("source", "EXTERNAL_ALERT_FEED")
                )
                self.add_hazard(h)
                count += 1
            except Exception:
                continue
        return count

    def check_route_hazards(
        self,
        polyline: List[Tuple[float, float]],
        safety_buffer_m: float = 50.0
    ) -> List[Dict[str, Any]]:
        """
        Tests whether any active hazard intersects or encroaches within the safety buffer
        of any segment in the route polyline.

        Returns a list of conflict details:
        [{'hazard': GeographicHazard, 'min_distance_m': float, 'is_direct_hit': bool}]
        """
        conflicts = []
        active_hazards = self.get_active_hazards()

        if not polyline or len(polyline) < 2:
            return conflicts

        for hazard in active_hazards:
            hazard_threshold = hazard.radius_meters + safety_buffer_m
            min_dist = float("inf")

            for i in range(len(polyline) - 1):
                p1 = polyline[i]
                p2 = polyline[i + 1]
                dist = distance_point_to_segment_m(
                    hazard.latitude, hazard.longitude,
                    p1[0], p1[1],
                    p2[0], p2[1]
                )
                if dist < min_dist:
                    min_dist = dist

            if min_dist <= hazard_threshold:
                conflicts.append({
                    "hazard": hazard,
                    "min_distance_m": round(min_dist, 1),
                    "is_direct_hit": min_dist <= hazard.radius_meters,
                    "incident_type": hazard.incident_type,
                    "severity": hazard.severity.value,
                    "description": hazard.description
                })

        return conflicts
