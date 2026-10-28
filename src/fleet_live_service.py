"""
P.A.T.H.F.I.N.D.E.R. • Real-Time Multi-User Fleet & Convoy Location Sharing Service
CampusAegis / P.A.T.H.F.I.N.D.E.R. Architecture

Provides thread-safe multi-user live location tracking, group convoy coordination,
peer-to-peer distance computation, and live spatial synchronization across concurrent user sessions.
"""

import math
import time
import json
import uuid
import logging
import threading
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("pathfinder.fleet_service")


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two geographic coordinates in kilometers."""
    try:
        r = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2.0) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(r * c, 3)
    except Exception:
        return 0.0


def format_distance_label(dist_km: float) -> str:
    """Formats distance nicely into meters or kilometers."""
    if dist_km < 1.0:
        return f"{int(dist_km * 1000)} m"
    return f"{dist_km:.1f} km"


def calculate_bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates bearing angle in degrees from point 1 to point 2."""
    try:
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_lambda = math.radians(lon2 - lon1)
        y = math.sin(delta_lambda) * math.cos(phi2)
        x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
        theta = math.atan2(y, x)
        return (math.degrees(theta) + 360.0) % 360.0
    except Exception:
        return 0.0


def cardinal_direction(bearing_deg: float) -> str:
    """Converts a bearing in degrees to a 16-wind cardinal direction."""
    cardinals = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = int((bearing_deg + 11.25) / 22.5) % 16
    return cardinals[idx]


class FleetLiveService:
    """
    Thread-safe global singleton registry managing live location sharing across
    concurrent user sessions, groups, convoys, and emergency response teams.
    """

    def __init__(self, stale_timeout_sec: int = 300):
        self._lock = threading.RLock()
        self.stale_timeout_sec = stale_timeout_sec
        # Structure: { room_code: { user_id: user_state_dict } }
        self._rooms: Dict[str, Dict[str, Dict[str, Any]]] = {}
        # Pre-seed a few illustrative simulated companions in demo rooms for immediate testing
        self._seed_demo_peers_if_needed()

    def _normalize_room(self, room_code: Optional[str]) -> str:
        clean = (room_code or "DEFAULT").strip().upper()
        return clean if clean else "DEFAULT"

    def _seed_demo_peers_if_needed(self):
        """Seeds dynamic demo peers around the transit corridor for immediate live preview."""
        with self._lock:
            demo_room = "DEMO-CONVOY"
            if demo_room not in self._rooms:
                now = time.time()
                self._rooms[demo_room] = {
                    "demo_peer_1": {
                        "user_id": "demo_peer_1",
                        "display_name": "Ravi (Support Car)",
                        "role": "support",
                        "avatar": "🚗",
                        "latitude": 16.2420,
                        "longitude": 80.6380,
                        "speed_kmh": 42.5,
                        "heading_deg": 65.0,
                        "status_msg": "En route on Tenali bypass",
                        "last_seen": now,
                        "is_active": True,
                        "is_simulated": True
                    },
                    "demo_peer_2": {
                        "user_id": "demo_peer_2",
                        "display_name": "Priya (Motorcycle Scout)",
                        "role": "scout",
                        "avatar": "🏍️",
                        "latitude": 16.2370,
                        "longitude": 80.6480,
                        "speed_kmh": 36.0,
                        "heading_deg": 120.0,
                        "status_msg": "Scouting ahead near Market Center",
                        "last_seen": now,
                        "is_active": True,
                        "is_simulated": True
                    },
                    "demo_peer_3": {
                        "user_id": "demo_peer_3",
                        "display_name": "Dr. Ananya (Emergency Medic)",
                        "role": "emergency",
                        "avatar": "🚑",
                        "latitude": 16.2335,
                        "longitude": 80.5505,
                        "speed_kmh": 0.0,
                        "heading_deg": 0.0,
                        "status_msg": "Stationary at Vignan Health Clinic",
                        "last_seen": now,
                        "is_active": True,
                        "is_simulated": True
                    }
                }

    def register_or_update(
        self,
        room_code: str,
        user_id: str,
        display_name: str,
        latitude: float,
        longitude: float,
        speed_kmh: float = 0.0,
        heading_deg: float = 0.0,
        avatar: str = "🚗",
        role: str = "traveler",
        status_msg: str = "Active",
        is_custom_start: bool = False
    ) -> Dict[str, Any]:
        """
        Updates the current user's live coordinates, speed, and status in the designated room.
        Thread-safe across all concurrent browser sessions.
        """
        room = self._normalize_room(room_code)
        now = time.time()

        user_data = {
            "user_id": str(user_id),
            "display_name": str(display_name or f"User-{str(user_id)[:4]}").strip(),
            "role": str(role or "traveler").lower(),
            "avatar": str(avatar or "🚗"),
            "latitude": float(latitude),
            "longitude": float(longitude),
            "speed_kmh": round(float(speed_kmh or 0.0), 1),
            "heading_deg": round(float(heading_deg or 0.0), 1),
            "status_msg": str(status_msg or "Active on route"),
            "last_seen": now,
            "is_active": True,
            "is_custom_start": is_custom_start,
            "room_code": room
        }

        with self._lock:
            if room not in self._rooms:
                self._rooms[room] = {}
            self._rooms[room][user_id] = user_data

        return user_data

    def get_room_members(
        self,
        room_code: str,
        exclude_user_id: Optional[str] = None,
        reference_lat: Optional[float] = None,
        reference_lon: Optional[float] = None,
        include_stale: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Returns all active members in the room, annotated with relative distances,
        bearings, and human-readable time deltas.
        """
        room = self._normalize_room(room_code)
        now = time.time()
        results: List[Dict[str, Any]] = []

        with self._lock:
            room_dict = self._rooms.get(room, {})
            for uid, data in list(room_dict.items()):
                # Exclude self if requested
                if exclude_user_id and str(uid) == str(exclude_user_id):
                    continue

                # Check stale threshold (unless demo simulated member)
                delta_sec = now - data.get("last_seen", 0)
                if not include_stale and not data.get("is_simulated", False) and delta_sec > self.stale_timeout_sec:
                    continue

                member = dict(data)
                member["seconds_ago"] = max(0, int(delta_sec))

                # Human readable last active string
                if member["seconds_ago"] < 10:
                    member["last_seen_str"] = "Just now"
                elif member["seconds_ago"] < 60:
                    member["last_seen_str"] = f"{member['seconds_ago']}s ago"
                else:
                    member["last_seen_str"] = f"{member['seconds_ago'] // 60}m ago"

                # Calculate relative distance and bearing if reference coordinates provided
                if reference_lat is not None and reference_lon is not None:
                    dist_km = haversine_distance_km(
                        reference_lat, reference_lon,
                        member["latitude"], member["longitude"]
                    )
                    bearing = calculate_bearing_deg(
                        reference_lat, reference_lon,
                        member["latitude"], member["longitude"]
                    )
                    cardinal = cardinal_direction(bearing)
                    member["distance_km"] = dist_km
                    member["distance_label"] = format_distance_label(dist_km)
                    member["bearing_deg"] = round(bearing, 1)
                    member["cardinal"] = cardinal
                    member["relative_location_str"] = f"{member['distance_label']} {cardinal}"
                else:
                    member["distance_km"] = 0.0
                    member["distance_label"] = "Unknown"
                    member["relative_location_str"] = "Active"

                results.append(member)

        # Sort by distance (closest first)
        results.sort(key=lambda m: m.get("distance_km", 9999.0))
        return results

    def leave_room(self, room_code: str, user_id: str) -> bool:
        """Removes a user from a room on disconnect or leave action."""
        room = self._normalize_room(room_code)
        with self._lock:
            if room in self._rooms and user_id in self._rooms[room]:
                del self._rooms[room][user_id]
                return True
        return False

    def list_rooms(self) -> List[Dict[str, Any]]:
        """Returns all currently active rooms and their member counts."""
        now = time.time()
        room_list = []
        with self._lock:
            for rcode, members in self._rooms.items():
                active_count = sum(
                    1 for m in members.values()
                    if (now - m.get("last_seen", 0) <= self.stale_timeout_sec) or m.get("is_simulated", False)
                )
                if active_count > 0:
                    room_list.append({
                        "room_code": rcode,
                        "active_count": active_count,
                        "members": [m["display_name"] for m in members.values()]
                    })
        return room_list

    def prune_stale_members(self) -> int:
        """Prunes inactive sessions to conserve memory."""
        now = time.time()
        pruned = 0
        with self._lock:
            for rcode in list(self._rooms.keys()):
                for uid, m in list(self._rooms[rcode].items()):
                    if not m.get("is_simulated", False) and (now - m.get("last_seen", 0) > self.stale_timeout_sec * 2):
                        del self._rooms[rcode][uid]
                        pruned += 1
                if not self._rooms[rcode]:
                    del self._rooms[rcode]
        return pruned


# Global singleton instance
_GLOBAL_FLEET_SERVICE: Optional[FleetLiveService] = None
_INIT_LOCK = threading.Lock()


def get_fleet_live_service() -> FleetLiveService:
    """Returns the process-wide FleetLiveService singleton."""
    global _GLOBAL_FLEET_SERVICE
    if _GLOBAL_FLEET_SERVICE is None:
        with _INIT_LOCK:
            if _GLOBAL_FLEET_SERVICE is None:
                _GLOBAL_FLEET_SERVICE = FleetLiveService()
    return _GLOBAL_FLEET_SERVICE
