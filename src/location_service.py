"""
Location Service for CampusAegis / PROJECT AI
Manages GPS coordinate tracking, manual origin selection, permission states,
accuracy thresholds, stale location detection, and real-time movement kinematics.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import math
from typing import Any, Dict, List, Optional, Tuple


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates spherical distance between two geographic coordinates in meters."""
    r_earth = 6371000.0  # Mean radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r_earth * c


def calculate_bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes forward azimuth angle between two points on the WGS-84 sphere in degrees (0-360)."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)
    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360.0) % 360.0


def bearing_to_cardinal(deg: float) -> str:
    """Maps azimuth angle to standard 16-point cardinal compass direction."""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = int((deg + 11.25) / 22.5) % 16
    return directions[idx]


class LocationPermissionStatus(Enum):
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    RESTRICTED = "RESTRICTED"
    NOT_REQUESTED = "NOT_REQUESTED"


class LocationSource(Enum):
    GPS = "GPS"
    NETWORK = "NETWORK"
    MANUAL_PIN = "MANUAL_PIN"
    GEOCODED_SEARCH = "GEOCODED_SEARCH"
    SIMULATED = "SIMULATED"
    REAL_DEVICE_HTML5 = "REAL_DEVICE_HTML5"


@dataclass
class LocationReading:
    latitude: float
    longitude: float
    accuracy_meters: float
    timestamp: datetime
    source: LocationSource
    speed_mps: Optional[float] = None
    bearing_deg: Optional[float] = None
    label: str = "Current Location"

    @property
    def coordinates(self) -> Tuple[float, float]:
        return (self.latitude, self.longitude)

    @property
    def speed_kmh(self) -> float:
        return (self.speed_mps * 3.6) if self.speed_mps is not None else 0.0

    @property
    def heading_cardinal(self) -> str:
        return bearing_to_cardinal(self.bearing_deg) if self.bearing_deg is not None else "N"

    def is_stale(self, max_age_seconds: float = 120.0) -> bool:
        """Determines if the reading is older than the allowed freshness window."""
        now = datetime.now(timezone.utc)
        age = (now - self.timestamp).total_seconds()
        return age > max_age_seconds

    def is_accurate_enough(self, max_acceptable_accuracy_m: float = 50.0) -> bool:
        """Checks if GPS error radius is within acceptable limits."""
        return self.accuracy_meters <= max_acceptable_accuracy_m


class LocationService:
    """
    Coordinates platform GPS, manual coordinate overrides, and privacy-conscious tracking.
    Complies with Android location guidelines: does not track unless journey is active.
    Calculates live user movement kinematics, bearing, and route traversal.
    """

    def __init__(self, default_lat: float = 16.2335, default_lon: float = 80.5505):
        self.permission_status = LocationPermissionStatus.NOT_REQUESTED
        self._current_reading: Optional[LocationReading] = None
        self._is_active_journey: bool = False
        self._default_coords = (default_lat, default_lon)
        self._movement_trail: List[Tuple[float, float]] = [(default_lat, default_lon)]
        self._total_distance_covered_m: float = 0.0

    def set_permission(self, status: LocationPermissionStatus):
        self.permission_status = status

    def start_journey_tracking(self):
        """Enables active location updates for the active route only."""
        self._is_active_journey = True

    def stop_journey_tracking(self):
        """Halts tracking immediately to conserve battery and protect privacy."""
        self._is_active_journey = False

    def record_movement(
        self,
        lat: float,
        lon: float,
        accuracy_m: float = 10.0,
        source: LocationSource = LocationSource.GPS,
        timestamp: Optional[datetime] = None,
        speed_mps: Optional[float] = None,
        label: str = "Live Movement Position"
    ) -> LocationReading:
        """
        Dynamically calculates movement kinematics (distance delta, instantaneous speed, and bearing)
        between the previous reading and new coordinate.
        """
        now = timestamp or datetime.now(timezone.utc)
        bearing = None
        calc_speed_mps = speed_mps

        if self._current_reading is not None:
            prev = self._current_reading
            dist_delta_m = haversine_distance_m(prev.latitude, prev.longitude, lat, lon)
            self._total_distance_covered_m += dist_delta_m

            if dist_delta_m > 1.0:  # Moved more than 1 meter
                bearing = calculate_bearing_deg(prev.latitude, prev.longitude, lat, lon)
                time_delta_sec = max(0.2, (now - prev.timestamp).total_seconds())
                if calc_speed_mps is None:
                    calc_speed_mps = dist_delta_m / time_delta_sec

        reading = LocationReading(
            latitude=lat,
            longitude=lon,
            accuracy_meters=accuracy_m,
            timestamp=now,
            source=source,
            speed_mps=calc_speed_mps if calc_speed_mps is not None else 0.0,
            bearing_deg=bearing if bearing is not None else 0.0,
            label=label
        )
        self._current_reading = reading
        self._movement_trail.append((lat, lon))
        return reading

    def update_gps_location(
        self,
        lat: float,
        lon: float,
        accuracy_m: float = 10.0,
        speed_mps: Optional[float] = None,
        source: LocationSource = LocationSource.GPS
    ) -> LocationReading:
        """Updates the current reading from GPS hardware or network provider."""
        if self.permission_status != LocationPermissionStatus.GRANTED:
            raise PermissionError("Location permission is not GRANTED.")
        return self.record_movement(lat, lon, accuracy_m=accuracy_m, source=source, speed_mps=speed_mps, label="Live GPS Location")

    def set_manual_location(self, lat: float, lon: float, label: str = "Manual Pin Origin") -> LocationReading:
        """Allows traveler to manually select starting point without GPS permission."""
        reading = LocationReading(
            latitude=lat,
            longitude=lon,
            accuracy_meters=0.0,  # Exact pin drop
            timestamp=datetime.now(timezone.utc),
            source=LocationSource.MANUAL_PIN,
            speed_mps=0.0,
            bearing_deg=0.0,
            label=label
        )
        self._current_reading = reading
        self._movement_trail = [(lat, lon)]
        self._total_distance_covered_m = 0.0
        return reading

    def get_movement_trail(self) -> List[Tuple[float, float]]:
        """Returns ordered list of historical movement coordinates."""
        return list(self._movement_trail)

    def get_total_distance_covered_m(self) -> float:
        """Returns cumulative meters traveled during the active session."""
        return float(self._total_distance_covered_m)

    def advance_along_polyline(
        self,
        polyline: List[Tuple[float, float]],
        current_idx: int,
        step_nodes: int = 1,
        simulated_speed_kmh: float = 40.0
    ) -> Tuple[LocationReading, int, float, bool]:
        """
        Advances the traveler along an active route polyline.
        Returns: (Updated LocationReading, next_polyline_index, remaining_distance_m, has_arrived)
        """
        if not polyline:
            curr = self.get_effective_location()[0]
            return curr, 0, 0.0, True

        next_idx = min(len(polyline) - 1, current_idx + step_nodes)
        target_pt = polyline[next_idx]
        has_arrived = (next_idx >= len(polyline) - 1)

        speed_mps = simulated_speed_kmh / 3.6
        reading = self.record_movement(
            lat=target_pt[0],
            lon=target_pt[1],
            accuracy_m=5.0,
            source=LocationSource.SIMULATED,
            speed_mps=speed_mps,
            label=f"In Transit (Waypoint {next_idx+1}/{len(polyline)})"
        )

        # Calculate remaining distance from target_pt to end of polyline
        remaining_m = 0.0
        for i in range(next_idx, len(polyline) - 1):
            remaining_m += haversine_distance_m(
                polyline[i][0], polyline[i][1],
                polyline[i+1][0], polyline[i+1][1]
            )

        return reading, next_idx, remaining_m, has_arrived

    def get_effective_location(self) -> Tuple[LocationReading, str]:
        """
        Returns the best available location reading and a status message.
        Falls back to default reference point if GPS is unavailable or denied.
        """
        if self._current_reading is not None:
            if self._current_reading.source == LocationSource.GPS:
                if self._current_reading.is_stale():
                    return self._current_reading, "GPS location is stale (>120s old). Consider manual pin."
                if not self._current_reading.is_accurate_enough(100.0):
                    return self._current_reading, "GPS accuracy is low (>100m error margin)."
                return self._current_reading, "Live GPS active."
            return self._current_reading, f"Using {self._current_reading.source.value}."

        # Default fallback if nothing set yet
        default_reading = LocationReading(
            latitude=self._default_coords[0],
            longitude=self._default_coords[1],
            accuracy_meters=8.0,
            timestamp=datetime.now(timezone.utc),
            source=LocationSource.SIMULATED,
            speed_mps=0.0,
            bearing_deg=0.0,
            label="Default Campus Reference (Vignan University)"
        )
        return default_reading, "No GPS stream detected; defaulted to reference point."

    def check_off_route(
        self,
        current_lat: float,
        current_lon: float,
        polyline: List[Tuple[float, float]],
        threshold_meters: float = 60.0
    ) -> Tuple[bool, float]:
        """
        Calculates the minimum distance from traveler's live position to any segment
        of the active route polyline. If distance exceeds threshold, signals off-route rerouting.
        Returns: (is_off_route, min_distance_meters)
        """
        if not polyline or len(polyline) < 2:
            return False, 0.0

        min_dist = float("inf")
        for i in range(len(polyline) - 1):
            p1 = polyline[i]
            p2 = polyline[i + 1]
            # Flat planar approximation for short segments
            lat_mid = math.radians((p1[0] + p2[0]) / 2.0)
            m_per_deg_lat = 111132.92
            m_per_deg_lon = 111412.84 * math.cos(lat_mid)

            ax, ay = p1[1] * m_per_deg_lon, p1[0] * m_per_deg_lat
            bx, by = p2[1] * m_per_deg_lon, p2[0] * m_per_deg_lat
            px, py = current_lon * m_per_deg_lon, current_lat * m_per_deg_lat

            ab_dx, ab_dy = bx - ax, by - ay
            seg_len_sq = ab_dx * ab_dx + ab_dy * ab_dy

            if seg_len_sq == 0:
                dist = math.hypot(px - ax, py - ay)
            else:
                t = max(0.0, min(1.0, ((px - ax) * ab_dx + (py - ay) * ab_dy) / seg_len_sq))
                dist = math.hypot(px - (ax + t * ab_dx), py - (ay + t * ab_dy))

            if dist < min_dist:
                min_dist = dist

        return (min_dist > threshold_meters), round(min_dist, 1)

