"""
Real-Time Progress Processing & Map-Matching Service
Handles map-matching along route polyline, checkpoint completion,
step advancement, entrance arrival, and off-route detection.
"""

from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional, Tuple


def haversine_distance_m(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculates spherical distance in meters between two lat/lon pairs."""
    lat1, lon1 = p1
    lat2, lon2 = p2
    r = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0) ** 2
    return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))


def calculate_bearing_degrees(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculates forward azimuth / bearing in degrees [0, 360) from p1 to p2."""
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlon = lon2 - lon1
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    initial_bearing = math.atan2(y, x)
    degrees = (math.degrees(initial_bearing) + 360.0) % 360.0
    return round(degrees, 1)


class ProgressProcessingService:
    """
    Evaluates real-time location observations against active route and checkpoints.
    """

    OFF_ROUTE_THRESHOLD_WALKING_M = 65.0
    OFF_ROUTE_THRESHOLD_DRIVING_M = 150.0
    ARRIVAL_RADIUS_DESTINATION_M = 35.0
    ARRIVAL_RADIUS_ENTRANCE_M = 25.0
    TURN_APPROACH_RADIUS_M = 50.0

    @classmethod
    def match_to_polyline(
        cls,
        user_lat: float,
        user_lon: float,
        polyline: List[List[float]]
    ) -> Tuple[float, float, float, int]:
        """
        Projects user coordinate onto the nearest polyline segment.
        Returns: (matched_lat, matched_lon, min_distance_meters, segment_index)
        """
        if not polyline:
            return user_lat, user_lon, 0.0, 0

        if len(polyline) == 1:
            d = haversine_distance_m((user_lat, user_lon), (polyline[0][0], polyline[0][1]))
            return polyline[0][0], polyline[0][1], d, 0

        min_dist = float("inf")
        best_pt = (polyline[0][0], polyline[0][1])
        best_idx = 0

        for i in range(len(polyline) - 1):
            p1 = (polyline[i][0], polyline[i][1])
            p2 = (polyline[i + 1][0], polyline[i + 1][1])

            # Project onto segment p1-p2
            d12 = haversine_distance_m(p1, p2)
            if d12 <= 0.01:
                cand_dist = haversine_distance_m((user_lat, user_lon), p1)
                if cand_dist < min_dist:
                    min_dist = cand_dist
                    best_pt = p1
                    best_idx = i
                continue

            # Fractional projection
            du1 = haversine_distance_m((user_lat, user_lon), p1)
            du2 = haversine_distance_m((user_lat, user_lon), p2)

            # Cosine rule projection
            cos_theta = (du1 ** 2 + d12 ** 2 - du2 ** 2) / (2.0 * max(0.1, du1 * d12))
            cos_theta = max(-1.0, min(1.0, cos_theta))
            proj_len = du1 * cos_theta
            t = max(0.0, min(1.0, proj_len / d12))

            proj_lat = p1[0] + t * (p2[0] - p1[0])
            proj_lon = p1[1] + t * (p2[1] - p1[1])
            dist_to_proj = haversine_distance_m((user_lat, user_lon), (proj_lat, proj_lon))

            if dist_to_proj < min_dist:
                min_dist = dist_to_proj
                best_pt = (proj_lat, proj_lon)
                best_idx = i

        return best_pt[0], best_pt[1], round(min_dist, 1), best_idx

    @classmethod
    def evaluate_checkpoints(
        cls,
        matched_lat: float,
        matched_lon: float,
        checkpoints: List[Any],
        current_step_idx: int
    ) -> List[Any]:
        """
        Determines which checkpoints are newly reached based on proximity and sequence.
        Returns list of newly reached checkpoints.
        """
        now = datetime.now(timezone.utc)
        newly_reached = []

        for cp in checkpoints:
            if getattr(cp, "is_reached", False):
                continue

            cp_pos = (cp.latitude, cp.longitude)
            dist_m = haversine_distance_m((matched_lat, matched_lon), cp_pos)
            radius = getattr(cp, "radius_meters", 35.0)

            # Checkpoint reached if within radius and sequence is reachable
            if dist_m <= radius and cp.sequence_number <= current_step_idx + 2:
                cp.is_reached = True
                cp.reached_at = now
                newly_reached.append(cp)

        return newly_reached

    @classmethod
    def evaluate_arrival(
        cls,
        user_lat: float,
        user_lon: float,
        dest_lat: float,
        dest_lon: float,
        entrance_coords: Optional[Tuple[float, float]] = None,
        travel_mode: str = "walking",
        accuracy_meters: float = 5.0
    ) -> Tuple[bool, bool, str]:
        """
        Determines whether the user has truly arrived at destination or entrance.
        Returns: (is_arrived, is_at_entrance, arrival_message)
        """
        mode = travel_mode.lower()
        base_arrival_radius = cls.ARRIVAL_RADIUS_DESTINATION_M
        if "drive" in mode or "car" in mode:
            base_arrival_radius = 55.0

        effective_radius = max(base_arrival_radius, min(accuracy_meters * 1.5, 75.0))

        # Check entrance first if present
        if entrance_coords:
            d_entrance = haversine_distance_m((user_lat, user_lon), entrance_coords)
            if d_entrance <= cls.ARRIVAL_RADIUS_ENTRANCE_M + (accuracy_meters * 0.5):
                return True, True, "Arrived at Designated Accessible Building Entrance"

        # Check destination coordinates
        d_dest = haversine_distance_m((user_lat, user_lon), (dest_lat, dest_lon))
        if d_dest <= effective_radius:
            return True, False, "Arrived at Final Destination"

        return False, False, ""

    @classmethod
    def calculate_remaining_metrics(
        cls,
        matched_lat: float,
        matched_lon: float,
        segment_idx: int,
        polyline: List[List[float]],
        travel_mode: str = "walking"
    ) -> Tuple[float, float, float]:
        """
        Calculates:
        (distance_remaining_meters, duration_remaining_seconds, progress_percent)
        """
        if not polyline or len(polyline) < 2:
            return 0.0, 0.0, 100.0

        total_dist_m = 0.0
        for i in range(len(polyline) - 1):
            total_dist_m += haversine_distance_m(
                (polyline[i][0], polyline[i][1]),
                (polyline[i + 1][0], polyline[i + 1][1])
            )

        if total_dist_m <= 0.0:
            return 0.0, 0.0, 100.0

        # Distance from matched point to polyline[segment_idx + 1], then sum remainder
        rem_m = haversine_distance_m(
            (matched_lat, matched_lon),
            (polyline[segment_idx + 1][0], polyline[segment_idx + 1][1])
        )
        for i in range(segment_idx + 1, len(polyline) - 1):
            rem_m += haversine_distance_m(
                (polyline[i][0], polyline[i][1]),
                (polyline[i + 1][0], polyline[i + 1][1])
            )

        rem_m = max(0.0, min(total_dist_m, rem_m))
        progress_pct = max(0.0, min(100.0, round(((total_dist_m - rem_m) / total_dist_m) * 100.0, 1)))

        # Mode speeds in m/s
        mode_speeds = {
            "walking": 1.35,      # ~4.8 km/h
            "running": 2.7,       # ~9.7 km/h
            "cycling": 4.5,       # ~16.2 km/h
            "motorcycle": 11.0,   # ~40 km/h
            "driving": 13.8,      # ~50 km/h
            "transit": 10.0       # ~36 km/h
        }
        speed_ms = mode_speeds.get(travel_mode.lower(), 1.35)
        rem_sec = round(rem_m / speed_ms, 0)

        return round(rem_m, 1), rem_sec, progress_pct
