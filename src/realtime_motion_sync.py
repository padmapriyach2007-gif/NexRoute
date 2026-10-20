"""
Automatic Real-User Motion Detection & Virtual Companion Synchronization Engine
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Predictive Adaptive Transit & Hazard-Free Intelligent Navigation

Provides authoritative real-time motion detection, GPS noise filtering,
along-track route matching, checkpoint approach & crossing verification,
route deviation tracking, and synchronized virtual companion orchestration.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import json
import math
from typing import Any, Dict, List, Optional, Tuple, Union


class RealtimeMotionState(str, Enum):
    """
    Authoritative motion states for the real-time user motion engine.
    """
    STATIONARY = "STATIONARY"
    MOVING_FORWARD = "MOVING_FORWARD"
    MOVING_PARALLEL = "MOVING_PARALLEL"
    APPROACHING_CHECKPOINT = "APPROACHING_CHECKPOINT"
    CHECKPOINT_CROSSED = "CHECKPOINT_CROSSED"
    ROUTE_DEVIATION = "ROUTE_DEVIATION"
    MOVING_BACKWARD = "MOVING_BACKWARD"
    LOCATION_UNCERTAIN = "LOCATION_UNCERTAIN"
    LOCATION_LOST = "LOCATION_LOST"


class CompanionSyncMode(str, Enum):
    """
    Synchronization mode between real traveler and virtual companion.
    """
    FOLLOW_USER = "FOLLOW_USER"       # Companion strictly follows real user's verified movement
    INDEPENDENT = "INDEPENDENT"       # Companion moves along demonstration pace while user is tracked separately


@dataclass
class LocationObservation:
    """
    Validated raw location update from client device GPS / browser geolocation.
    """
    latitude: float
    longitude: float
    timestamp: float                  # Epoch seconds or milliseconds
    accuracy_meters: float = 10.0
    speed_mps: Optional[float] = None
    heading_deg: Optional[float] = None
    source: str = "gps"               # gps, network, simulated


@dataclass
class MotionEstimationResult:
    """
    Evaluated output of the motion-state engine for an observation.
    """
    state: RealtimeMotionState
    status_label: str
    user_speed_kmh: float
    user_heading_deg: float
    along_track_distance_m: float
    cross_track_distance_m: float
    is_off_route: bool
    is_moving_backward: bool
    current_checkpoint_idx: int
    dist_to_next_checkpoint_m: float
    newly_crossed_checkpoint: Optional[Dict[str, Any]] = None
    companion_station_m: float = 0.0
    companion_speed_kmh: float = 0.0
    progress_discrepancy_m: float = 0.0
    location_quality: str = "GOOD"    # GOOD, DEGRADED, LOST
    last_update_iso: str = ""
    details: str = ""


class LocationValidator:
    """
    Validates GPS observations, filters noisy readings, rejects stale/invalid data,
    and handles GPS jitter.
    """

    ACCURACY_UNCERTAIN_THRESHOLD_M = 50.0  # Accuracy > 50m triggers LOCATION_UNCERTAIN
    MAX_VALID_ACCURACY_M = 150.0           # Accuracy > 150m is rejected as invalid noise
    STALE_TIMEOUT_SECONDS = 15.0           # Absence of updates for 15s triggers LOCATION_LOST

    @classmethod
    def validate_coordinate(cls, lat: float, lon: float) -> bool:
        """Checks if latitude and longitude are valid numeric coordinates."""
        if lat is None or lon is None:
            return False
        try:
            f_lat = float(lat)
            f_lon = float(lon)
            if math.isnan(f_lat) or math.isnan(f_lon) or math.isinf(f_lat) or math.isinf(f_lon):
                return False
            return -90.0 <= f_lat <= 90.0 and -180.0 <= f_lon <= 180.0
        except (ValueError, TypeError):
            return False

    @classmethod
    def sanitize_observation(
        cls,
        obs: LocationObservation,
        last_valid_obs: Optional[LocationObservation] = None,
        current_time_epoch: Optional[float] = None
    ) -> Tuple[bool, str, LocationObservation]:
        """
        Validates an incoming observation against sanity limits and previous valid readings.
        Returns: (is_valid, rejection_reason, sanitized_obs)
        """
        if not cls.validate_coordinate(obs.latitude, obs.longitude):
            return False, "Invalid coordinate bounds or NaN", obs

        # Normalize timestamp to seconds
        ts = obs.timestamp
        if ts > 1e11:  # Milliseconds
            ts /= 1000.0

        now = current_time_epoch if current_time_epoch is not None else datetime.now(timezone.utc).timestamp()

        # Reject observations from the future or excessively stale
        if ts > now + 30.0:
            return False, "Timestamp is in the future", obs

        if last_valid_obs:
            last_ts = last_valid_obs.timestamp
            if last_ts > 1e11:
                last_ts /= 1000.0
            if ts < last_ts - 0.5:
                return False, "Out of order chronological timestamp", obs

        # Check accuracy bounds
        acc = float(obs.accuracy_meters) if obs.accuracy_meters is not None else 15.0
        if acc > cls.MAX_VALID_ACCURACY_M:
            return False, f"GPS accuracy too poor ({acc}m > {cls.MAX_VALID_ACCURACY_M}m)", obs

        # Sanitize speed & heading
        spd = float(obs.speed_mps) if obs.speed_mps is not None and obs.speed_mps >= 0 else None
        hdg = float(obs.heading_deg) if obs.heading_deg is not None and 0.0 <= obs.heading_deg <= 360.0 else None

        sanitized = LocationObservation(
            latitude=float(obs.latitude),
            longitude=float(obs.longitude),
            timestamp=ts,
            accuracy_meters=acc,
            speed_mps=spd,
            heading_deg=hdg,
            source=obs.source
        )
        return True, "Valid", sanitized


class RouteMatcher:
    """
    Calculates great-circle distance, forward bearing, map-matching projection,
    along-track route stationing, and cross-track deviation error.
    """

    EARTH_RADIUS_M = 6371000.0

    @classmethod
    def haversine_m(cls, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Great-circle distance between two (lat, lon) points in meters."""
        lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
        lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2.0) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2
        return 2.0 * cls.EARTH_RADIUS_M * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))

    @classmethod
    def calculate_bearing(cls, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Forward bearing from p1 to p2 in degrees [0, 360)."""
        lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
        lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
        dlon = lon2 - lon1
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        b = math.degrees(math.atan2(y, x))
        return (b + 360.0) % 360.0

    @classmethod
    def angle_diff(cls, b1: float, b2: float) -> float:
        """Signed shortest difference between two angles in degrees [-180, 180]."""
        return (b2 - b1 + 180.0) % 360.0 - 180.0

    @classmethod
    def match_to_route(
        cls,
        user_coords: Tuple[float, float],
        polyline: List[Tuple[float, float]]
    ) -> Tuple[Tuple[float, float], float, float, int, float]:
        """
        Projects user coordinate onto the nearest polyline segment.
        Returns:
        (projected_coords, along_track_station_m, cross_track_error_m, segment_idx, segment_bearing)
        """
        if not polyline or len(polyline) < 2:
            return user_coords, 0.0, 0.0, 0, 0.0

        u_lat, u_lon = user_coords
        min_cross_track = float("inf")
        best_proj = polyline[0]
        best_seg_idx = 0
        best_along_track = 0.0
        best_bearing = 0.0

        cumulative_s = 0.0

        for i in range(len(polyline) - 1):
            p1 = polyline[i]
            p2 = polyline[i + 1]
            seg_len = cls.haversine_m(p1, p2)

            if seg_len <= 0.01:
                d = cls.haversine_m(user_coords, p1)
                if d < min_cross_track:
                    min_cross_track = d
                    best_proj = p1
                    best_seg_idx = i
                    best_along_track = cumulative_s
                    best_bearing = 0.0
                continue

            # Project user point onto segment p1-p2
            d_u1 = cls.haversine_m(user_coords, p1)
            d_u2 = cls.haversine_m(user_coords, p2)

            # Cosine rule for projection length along segment
            cos_alpha = (d_u1 ** 2 + seg_len ** 2 - d_u2 ** 2) / (2.0 * max(0.01, d_u1 * seg_len))
            cos_alpha = max(-1.0, min(1.0, cos_alpha))
            proj_dist = d_u1 * cos_alpha
            t = max(0.0, min(1.0, proj_dist / seg_len))

            proj_lat = p1[0] + t * (p2[0] - p1[0])
            proj_lon = p1[1] + t * (p2[1] - p1[1])
            cross_dist = cls.haversine_m(user_coords, (proj_lat, proj_lon))

            if cross_dist < min_cross_track:
                min_cross_track = cross_dist
                best_proj = (proj_lat, proj_lon)
                best_seg_idx = i
                best_along_track = cumulative_s + (t * seg_len)
                best_bearing = cls.calculate_bearing(p1, p2)

            cumulative_s += seg_len

        return (
            best_proj,
            round(best_along_track, 1),
            round(min_cross_track, 1),
            best_seg_idx,
            round(best_bearing, 1)
        )


class RealtimeMotionEngine:
    """
    Dedicated motion-state engine maintaining stable state transitions,
    hysteresis filtering, checkpoint progress, and virtual companion sync.
    """

    # Velocity and motion thresholds
    STOPPED_SPEED_THRESHOLD_KMH = 1.2
    MOVING_SPEED_THRESHOLD_KMH = 1.8
    CONSECUTIVE_STOPS_FOR_STATIONARY = 2   # Requires 2 consecutive slow pings over duration
    MIN_STOP_DURATION_SECONDS = 2.0        # Sustained period for stationary
    DEVIATION_BASE_RADIUS_M = 55.0         # Cross-track error threshold
    APPROACH_CHECKPOINT_RADIUS_M = 80.0    # Approach distance threshold
    CROSSING_CHECKPOINT_RADIUS_M = 35.0    # Confirmed crossing distance

    def __init__(
        self,
        polyline: Optional[List[Tuple[float, float]]] = None,
        checkpoints: Optional[List[Dict[str, Any]]] = None,
        total_distance_m: float = 1000.0,
        sync_mode: CompanionSyncMode = CompanionSyncMode.FOLLOW_USER
    ):
        self.polyline = polyline or []
        self.checkpoints = checkpoints or []
        self.total_distance_m = max(1.0, total_distance_m)
        self.sync_mode = sync_mode

        # State tracking
        self.current_state = RealtimeMotionState.STATIONARY
        self.consecutive_slow_observations = 0
        self.first_slow_timestamp: Optional[float] = None
        self.consecutive_deviations = 0
        self.last_valid_obs: Optional[LocationObservation] = None
        self.previous_along_track_s: float = 0.0
        self.current_checkpoint_idx: int = 0
        self.last_state_change_time = datetime.now(timezone.utc).timestamp()

        # Virtual companion tracking
        self.companion_station_m: float = 0.0
        self.companion_speed_kmh: float = 4.8
        self.is_simulation_paused: bool = False

    def process_observation(
        self,
        raw_obs: LocationObservation,
        current_time_epoch: Optional[float] = None
    ) -> MotionEstimationResult:
        """
        Processes a live device location update through the full motion state pipeline:
        Validation -> Noise Filtering -> Speed/Heading Estimation -> Route Matching ->
        Checkpoint Tracking -> Hysteresis State Transition -> Companion Sync.
        """
        now = current_time_epoch if current_time_epoch is not None else datetime.now(timezone.utc).timestamp()

        # 1. Validation & Sanitization
        is_valid, reason, obs = LocationValidator.sanitize_observation(
            raw_obs,
            last_valid_obs=self.last_valid_obs,
            current_time_epoch=now
        )

        if not is_valid:
            # If invalid due to excessive age or coordinates, check for location lost
            if self.last_valid_obs and (now - self.last_valid_obs.timestamp > LocationValidator.STALE_TIMEOUT_SECONDS):
                self.current_state = RealtimeMotionState.LOCATION_LOST
                return self._build_result(
                    state=RealtimeMotionState.LOCATION_LOST,
                    label="Location Lost • Signal Timed Out",
                    speed_kmh=0.0,
                    heading=0.0,
                    along_track=self.previous_along_track_s,
                    cross_track=0.0,
                    quality="LOST",
                    details=f"Invalid reading rejected: {reason}. GPS signal lost for > {LocationValidator.STALE_TIMEOUT_SECONDS}s."
                )
            # Retain current state
            return self._build_result(
                state=self.current_state,
                label=f"Uncertain • {reason}",
                speed_kmh=0.0,
                heading=0.0,
                along_track=self.previous_along_track_s,
                cross_track=0.0,
                quality="DEGRADED",
                details=f"Observation rejected: {reason}"
            )

        # 2. Check for GPS accuracy degradation
        if obs.accuracy_meters > LocationValidator.ACCURACY_UNCERTAIN_THRESHOLD_M:
            self.current_state = RealtimeMotionState.LOCATION_UNCERTAIN
            self.last_valid_obs = obs
            return self._build_result(
                state=RealtimeMotionState.LOCATION_UNCERTAIN,
                label=f"Location Uncertain • Poor GPS Accuracy ({obs.accuracy_meters:.0f}m)",
                speed_kmh=0.0,
                heading=obs.heading_deg or 0.0,
                along_track=self.previous_along_track_s,
                cross_track=0.0,
                quality="DEGRADED",
                details=f"GPS reported accuracy {obs.accuracy_meters:.1f}m exceeds {LocationValidator.ACCURACY_UNCERTAIN_THRESHOLD_M}m threshold."
            )

        # 3. Speed & Heading Estimation with GPS Jitter Guard
        calc_speed_kmh = 0.0
        calc_heading = obs.heading_deg or 0.0

        if self.last_valid_obs:
            dt = obs.timestamp - self.last_valid_obs.timestamp
            dist_moved_m = RouteMatcher.haversine_m(
                (self.last_valid_obs.latitude, self.last_valid_obs.longitude),
                (obs.latitude, obs.longitude)
            )

            # Jitter Guard: small movement within GPS accuracy is considered stationary jitter
            jitter_radius = max(2.5, min(obs.accuracy_meters * 0.4, 6.0))
            if dist_moved_m <= jitter_radius and dt < 3.0:
                dist_moved_m = 0.0

            if dt > 0.01:
                derived_speed_mps = dist_moved_m / dt
                derived_speed_kmh = derived_speed_mps * 3.6
            else:
                derived_speed_kmh = 0.0

            # Use reported speed if reliable, otherwise fallback to derived speed
            if obs.speed_mps is not None and obs.speed_mps >= 0.0:
                calc_speed_kmh = round(obs.speed_mps * 3.6, 1)
            else:
                calc_speed_kmh = round(derived_speed_kmh, 1)

            # Compute heading from displacement if not provided by device
            if obs.heading_deg is None and dist_moved_m > 2.0:
                calc_heading = RouteMatcher.calculate_bearing(
                    (self.last_valid_obs.latitude, self.last_valid_obs.longitude),
                    (obs.latitude, obs.longitude)
                )
        else:
            calc_speed_kmh = round((obs.speed_mps or 0.0) * 3.6, 1)

        # 4. Route Matching (Along-track Station & Cross-track Error)
        user_coords = (obs.latitude, obs.longitude)
        proj_coords, along_track_s, cross_track_m, seg_idx, seg_bearing = RouteMatcher.match_to_route(
            user_coords,
            self.polyline
        )

        # 5. Route Deviation Detection
        # Dynamic deviation threshold accounting for GPS accuracy
        effective_dev_threshold = self.DEVIATION_BASE_RADIUS_M + (obs.accuracy_meters * 0.5)
        is_off_route = False

        if cross_track_m > effective_dev_threshold:
            self.consecutive_deviations += 1
            if self.consecutive_deviations >= 2:
                is_off_route = True
        else:
            self.consecutive_deviations = 0

        # 6. Backward Motion Detection
        is_moving_backward = False
        if self.last_valid_obs and calc_speed_kmh > self.MOVING_SPEED_THRESHOLD_KMH:
            station_delta = along_track_s - self.previous_along_track_s
            bearing_diff = abs(RouteMatcher.angle_diff(calc_heading, seg_bearing))
            if station_delta < -8.0 and bearing_diff > 120.0:
                is_moving_backward = True

        # 7. Checkpoint Approach & Confirmed Crossing
        newly_crossed = None
        approaching_checkpoint = False

        if self.checkpoints and self.current_checkpoint_idx < len(self.checkpoints):
            target_cp = self.checkpoints[self.current_checkpoint_idx]
            cp_lat = target_cp.get("lat") or target_cp.get("latitude")
            cp_lon = target_cp.get("lon") or target_cp.get("longitude")
            cp_station_m = target_cp.get("station_m") or target_cp.get("distance_from_start_m") or 0.0

            if cp_lat is not None and cp_lon is not None:
                direct_cp_dist = RouteMatcher.haversine_m(user_coords, (float(cp_lat), float(cp_lon)))
                station_to_cp = cp_station_m - along_track_s

                # Crossing criteria: user physically reached radius or passed station along route
                has_reached_radius = direct_cp_dist <= self.CROSSING_CHECKPOINT_RADIUS_M
                has_passed_station = (station_to_cp <= 5.0 and direct_cp_dist <= self.APPROACH_CHECKPOINT_RADIUS_M)

                if (has_reached_radius or has_passed_station) and not is_off_route:
                    newly_crossed = target_cp
                    self.current_checkpoint_idx += 1
                elif direct_cp_dist <= self.APPROACH_CHECKPOINT_RADIUS_M and station_to_cp > 0:
                    approaching_checkpoint = True

        dist_to_next_cp = 0.0
        if self.checkpoints and self.current_checkpoint_idx < len(self.checkpoints):
            next_cp = self.checkpoints[self.current_checkpoint_idx]
            n_lat = next_cp.get("lat") or next_cp.get("latitude")
            n_lon = next_cp.get("lon") or next_cp.get("longitude")
            if n_lat and n_lon:
                dist_to_next_cp = RouteMatcher.haversine_m(user_coords, (float(n_lat), float(n_lon)))

        # 8. State Machine Transition with Hysteresis
        target_state = self.current_state

        if is_off_route:
            target_state = RealtimeMotionState.ROUTE_DEVIATION
        elif is_moving_backward:
            target_state = RealtimeMotionState.MOVING_BACKWARD
        elif newly_crossed is not None:
            target_state = RealtimeMotionState.CHECKPOINT_CROSSED
        elif approaching_checkpoint:
            target_state = RealtimeMotionState.APPROACHING_CHECKPOINT
        elif calc_speed_kmh <= self.STOPPED_SPEED_THRESHOLD_KMH:
            # Hysteresis for stopping: sustained low speed
            if self.consecutive_slow_observations == 0:
                self.first_slow_timestamp = obs.timestamp

            self.consecutive_slow_observations += 1
            duration_slow = obs.timestamp - (self.first_slow_timestamp or obs.timestamp)

            if (self.consecutive_slow_observations >= self.CONSECUTIVE_STOPS_FOR_STATIONARY and
                    duration_slow >= self.MIN_STOP_DURATION_SECONDS):
                target_state = RealtimeMotionState.STATIONARY
            else:
                # Retain current moving state during brief pause / red light transition
                target_state = self.current_state
        else:
            # User moving above threshold (> 1.8 km/h)
            self.consecutive_slow_observations = 0
            self.first_slow_timestamp = None

            # Check if moving parallel with virtual companion
            companion_diff = abs(along_track_s - self.companion_station_m)
            if companion_diff <= 75.0 and not is_off_route:
                target_state = RealtimeMotionState.MOVING_PARALLEL
            else:
                target_state = RealtimeMotionState.MOVING_FORWARD

        self.current_state = target_state
        self.previous_along_track_s = along_track_s
        self.last_valid_obs = obs

        # 9. Companion Synchronization based on Mode
        if self.sync_mode == CompanionSyncMode.FOLLOW_USER:
            # In Follow-User mode, companion moves in lockstep with real user
            if target_state == RealtimeMotionState.STATIONARY:
                self.companion_speed_kmh = 0.0
            else:
                self.companion_speed_kmh = max(2.5, calc_speed_kmh)
                self.companion_station_m = along_track_s
        else:
            # In Independent mode, companion progresses independently if not paused
            if not self.is_simulation_paused:
                self.companion_station_m = min(self.total_distance_m, self.companion_station_m + 5.0)

        discrepancy_m = round(along_track_s - self.companion_station_m, 1)

        # Build clear status label
        labels = {
            RealtimeMotionState.STATIONARY: "User Stationary (0 km/h) • Standing at Route Point",
            RealtimeMotionState.MOVING_FORWARD: f"User Moving Along Route ({calc_speed_kmh:.1f} km/h)",
            RealtimeMotionState.MOVING_PARALLEL: f"Moving in Parallel with Virtual Companion ({calc_speed_kmh:.1f} km/h)",
            RealtimeMotionState.APPROACHING_CHECKPOINT: f"Approaching Checkpoint #{self.current_checkpoint_idx + 1} ({dist_to_next_cp:.0f}m)",
            RealtimeMotionState.CHECKPOINT_CROSSED: f"🎯 Checkpoint #{self.current_checkpoint_idx} Crossed Verified!",
            RealtimeMotionState.ROUTE_DEVIATION: f"⚠️ Route Deviation Detected ({cross_track_m:.0f}m off path)",
            RealtimeMotionState.MOVING_BACKWARD: f"🔄 Returning / Moving Backward Along Corridor",
            RealtimeMotionState.LOCATION_UNCERTAIN: "Location Uncertain • Low GPS Accuracy",
            RealtimeMotionState.LOCATION_LOST: "Location Lost • Waiting for GPS Signal"
        }

        return self._build_result(
            state=target_state,
            label=labels.get(target_state, "Tracking Active"),
            speed_kmh=calc_speed_kmh,
            heading=calc_heading,
            along_track=along_track_s,
            cross_track=cross_track_m,
            quality="GOOD",
            is_off_route=is_off_route,
            is_moving_backward=is_moving_backward,
            newly_crossed=newly_crossed,
            dist_to_next_cp=dist_to_next_cp,
            discrepancy_m=discrepancy_m
        )

    def _build_result(
        self,
        state: RealtimeMotionState,
        label: str,
        speed_kmh: float,
        heading: float,
        along_track: float,
        cross_track: float,
        quality: str,
        is_off_route: bool = False,
        is_moving_backward: bool = False,
        newly_crossed: Optional[Dict[str, Any]] = None,
        dist_to_next_cp: float = 0.0,
        discrepancy_m: float = 0.0,
        details: str = ""
    ) -> MotionEstimationResult:
        now_iso = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        return MotionEstimationResult(
            state=state,
            status_label=label,
            user_speed_kmh=speed_kmh,
            user_heading_deg=heading,
            along_track_distance_m=along_track,
            cross_track_distance_m=cross_track,
            is_off_route=is_off_route,
            is_moving_backward=is_moving_backward,
            current_checkpoint_idx=self.current_checkpoint_idx,
            dist_to_next_checkpoint_m=round(dist_to_next_cp, 1),
            newly_crossed_checkpoint=newly_crossed,
            companion_station_m=round(self.companion_station_m, 1),
            companion_speed_kmh=round(self.companion_speed_kmh, 1),
            progress_discrepancy_m=discrepancy_m,
            location_quality=quality,
            last_update_iso=now_iso,
            details=details
        )


def build_realtime_motion_hud_html(
    origin_name: str,
    dest_name: str,
    polyline: Optional[List[Tuple[float, float]]] = None,
    checkpoints: Optional[List[Dict[str, Any]]] = None,
    initial_sync_mode: str = "FOLLOW_USER"
) -> str:
    """
    Renders the autonomous browser geolocation client engine with real-time
    motion detection, permission management, telemetry display, and developer test panel.
    """
    poly_pts = polyline or [[16.2335, 80.5505], [16.2400, 80.5580]]
    cps = checkpoints or []

    payload = {
        "origin": origin_name,
        "destination": dest_name,
        "polyline": poly_pts,
        "checkpoints": cps,
        "sync_mode": initial_sync_mode
    }
    payload_json = json.dumps(payload, default=str)

    return f"""
    <div id='realtime-motion-engine-root' class='motion-engine-card'>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800;900&display=swap');

            .motion-engine-card {{
                font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: linear-gradient(135deg, rgba(8, 20, 42, 0.96) 0%, rgba(12, 28, 56, 0.94) 100%);
                border: 1.5px solid rgba(56, 189, 248, 0.4);
                border-radius: 16px;
                padding: 16px 20px;
                margin: 12px 0;
                color: #f8fafc;
                box-shadow: 0 12px 36px rgba(0, 0, 0, 0.65), 0 0 20px rgba(56, 189, 248, 0.15);
            }}

            .motion-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 12px;
                padding-bottom: 12px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.12);
            }}

            .motion-badge {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}

            .motion-state-pill {{
                padding: 5px 14px;
                border-radius: 999px;
                font-size: 0.74rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                transition: all 0.3s ease;
            }}

            /* State Styles */
            .state-STATIONARY {{ background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid #ef4444; }}
            .state-MOVING_FORWARD {{ background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid #10b981; }}
            .state-MOVING_PARALLEL {{ background: rgba(56, 189, 248, 0.25); color: #38bdf8; border: 1px solid #38bdf8; }}
            .state-APPROACHING_CHECKPOINT {{ background: rgba(250, 204, 21, 0.25); color: #fde047; border: 1px solid #facc15; }}
            .state-CHECKPOINT_CROSSED {{ background: rgba(16, 185, 129, 0.35); color: #34d399; border: 1px solid #34d399; }}
            .state-ROUTE_DEVIATION {{ background: rgba(249, 115, 22, 0.25); color: #fdba74; border: 1px solid #f97316; }}
            .state-MOVING_BACKWARD {{ background: rgba(168, 85, 247, 0.25); color: #d8b4fe; border: 1px solid #c084fc; }}
            .state-LOCATION_UNCERTAIN {{ background: rgba(234, 179, 8, 0.2); color: #fef08a; border: 1px solid #eab308; }}
            .state-LOCATION_LOST {{ background: rgba(100, 116, 139, 0.25); color: #cbd5e1; border: 1px solid #94a3b8; }}

            /* Telemetry Grid */
            .telemetry-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 10px;
                margin-top: 14px;
            }}

            .telemetry-item {{
                background: rgba(15, 23, 42, 0.65);
                border: 1px solid rgba(56, 189, 248, 0.2);
                border-radius: 10px;
                padding: 10px 14px;
            }}

            .telemetry-label {{
                font-size: 0.68rem;
                font-weight: 700;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 0.04em;
            }}

            .telemetry-val {{
                font-size: 1.15rem;
                font-weight: 900;
                color: #ffffff;
                margin-top: 3px;
                display: flex;
                align-items: center;
                gap: 6px;
            }}

            /* Developer Testing Panel (Collapsible) */
            .dev-panel-toggle {{
                margin-top: 14px;
                font-size: 0.72rem;
                color: #64748b;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 4px;
            }}

            .dev-panel-toggle:hover {{
                color: #94a3b8;
            }}

            .dev-panel-box {{
                display: none;
                background: rgba(0, 0, 0, 0.35);
                border: 1px dashed rgba(148, 163, 184, 0.3);
                border-radius: 10px;
                padding: 10px 14px;
                margin-top: 8px;
            }}

            .btn-ctrl {{
                background: rgba(30, 41, 59, 0.85);
                border: 1px solid rgba(56, 189, 248, 0.3);
                color: #e2e8f0;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 0.72rem;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.2s ease;
            }}

            .btn-ctrl:hover {{
                background: #0284c7;
                color: #ffffff;
                border-color: #38bdf8;
            }}
        </style>

        <!-- Header Status -->
        <div class='motion-header'>
            <div class='motion-badge'>
                <div style='font-size: 26px;'>🛰️</div>
                <div>
                    <div style='font-size: 0.92rem; font-weight: 900; color: #ffffff; display: flex; align-items: center; gap: 8px;'>
                        <span>AUTOMATIC REAL-USER MOTION &amp; COMPANION SYNC</span>
                        <span id='motion-sync-mode-tag' style='background: rgba(56, 189, 248, 0.2); color: #38bdf8; font-size: 0.68rem; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(56, 189, 248, 0.4);'>
                            ● FOLLOW-USER MODE
                        </span>
                    </div>
                    <div id='motion-status-subtitle' style='font-size: 0.74rem; color: #94a3b8; margin-top: 2px;'>
                        Autonomous GPS Sensor Engine: Detects stops, parallel motion, crossings, and deviation automatically
                    </div>
                </div>
            </div>

            <div style='display: flex; align-items: center; gap: 8px; flex-wrap: wrap;'>
                <div id='motion-state-pill' class='motion-state-pill state-STATIONARY'>
                    <span id='motion-state-dot'>●</span>
                    <span id='motion-state-text'>STATIONARY</span>
                </div>
                <button id='btn-gps-tracking' class='btn-ctrl' style='background: #0284c7; border-color: #38bdf8;' onclick='toggleLocationTracking()'>
                    <span id='tracking-icon'>📡</span> <span id='tracking-label'>Stop Tracking</span>
                </button>
                <button id='btn-sync-mode' class='btn-ctrl' onclick='toggleSyncMode()'>
                    <span id='mode-icon'>👤</span> <span id='mode-label'>Mode: Follow User</span>
                </button>
            </div>
        </div>

        <!-- Telemetry Metrics Grid -->
        <div class='telemetry-grid'>
            <div class='telemetry-item'>
                <div class='telemetry-label'>Real User Speed</div>
                <div class='telemetry-val'>
                    <span id='tel-speed' style='color: #10b981;'>0.0</span> <span style='font-size: 0.75rem; color: #94a3b8;'>km/h</span>
                </div>
            </div>

            <div class='telemetry-item'>
                <div class='telemetry-label'>GPS Accuracy</div>
                <div class='telemetry-val'>
                    <span id='tel-accuracy' style='color: #38bdf8;'>±5.0</span> <span style='font-size: 0.75rem; color: #94a3b8;'>m</span>
                </div>
            </div>

            <div class='telemetry-item'>
                <div class='telemetry-label'>Along-Route Distance</div>
                <div class='telemetry-val'>
                    <span id='tel-along-track' style='color: #fde047;'>0</span> <span style='font-size: 0.75rem; color: #94a3b8;'>m</span>
                </div>
            </div>

            <div class='telemetry-item'>
                <div class='telemetry-label'>Cross-Track Deviation</div>
                <div class='telemetry-val'>
                    <span id='tel-cross-track' style='color: #34d399;'>0.0</span> <span style='font-size: 0.75rem; color: #94a3b8;'>m</span>
                </div>
            </div>

            <div class='telemetry-item'>
                <div class='telemetry-label'>Companion Distance</div>
                <div class='telemetry-val'>
                    <span id='tel-companion-station' style='color: #38bdf8;'>0</span> <span style='font-size: 0.75rem; color: #94a3b8;'>m</span>
                </div>
            </div>

            <div class='telemetry-item'>
                <div class='telemetry-label'>Last GPS Update</div>
                <div class='telemetry-val'>
                    <span id='tel-last-update' style='font-size: 0.90rem; color: #cbd5e1;'>Live</span>
                </div>
            </div>
        </div>

        <!-- Collapsible Developer / Test Panel (Separated from normal workflow) -->
        <div>
            <div class='dev-panel-toggle' onclick='toggleDevPanel()'>
                <span>⚙️</span> <span>Developer &amp; Simulation Test Controls</span> <span id='dev-toggle-arrow'>▼</span>
            </div>
            <div id='dev-panel-box' class='dev-panel-box'>
                <div style='font-size: 0.70rem; color: #94a3b8; margin-bottom: 8px;'>
                    <b>Notice:</b> During ordinary operation, user motion is detected automatically from browser GPS. These simulation triggers are retained for unit testing and manual diagnostic inspection.
                </div>
                <div style='display: flex; gap: 8px; flex-wrap: wrap;'>
                    <button class='btn-ctrl' onclick='simulateDevEvent("STOP")'>🛑 Traffic Stop (0 km/h)</button>
                    <button class='btn-ctrl' onclick='simulateDevEvent("MOVE")'>🟢 Move in Parallel</button>
                    <button class='btn-ctrl' onclick='simulateDevEvent("CROSS")'>🎯 Cross Next Stop</button>
                    <button class='btn-ctrl' onclick='simulateDevEvent("DEVIATION")'>⚠️ Force Deviation</button>
                    <button class='btn-ctrl' onclick='simulateDevEvent("BACKWARD")'>🔄 Move Backward</button>
                </div>
            </div>
        </div>
    </div>

    <script>
    (function() {{
        const CONFIG = {payload_json};
        const POLYLINE = CONFIG.polyline || [];
        const CHECKPOINTS = CONFIG.checkpoints || [];

        let isTrackingEnabled = true;
        let activeSyncMode = CONFIG.sync_mode || 'FOLLOW_USER'; // 'FOLLOW_USER' or 'INDEPENDENT'
        let watchId = null;
        let lastObs = null;
        let consecutiveSlow = 0;
        let firstSlowTime = 0;
        let alongTrackS = 0.0;
        let companionStationM = 0.0;
        let checkpointIdx = 0;

        function updateTelemetryUI(res) {{
            const pill = document.getElementById('motion-state-pill');
            const pillText = document.getElementById('motion-state-text');
            const speedEl = document.getElementById('tel-speed');
            const accEl = document.getElementById('tel-accuracy');
            const alongEl = document.getElementById('tel-along-track');
            const crossEl = document.getElementById('tel-cross-track');
            const compEl = document.getElementById('tel-companion-station');
            const timeEl = document.getElementById('tel-last-update');
            const subTitle = document.getElementById('motion-status-subtitle');

            if (pill && pillText) {{
                pill.className = 'motion-state-pill state-' + res.state;
                pillText.innerText = res.state.replace('_', ' ');
            }}
            if (speedEl) speedEl.innerText = res.speed_kmh.toFixed(1);
            if (accEl) accEl.innerText = '±' + res.accuracy.toFixed(1);
            if (alongEl) alongEl.innerText = Math.round(res.along_track);
            if (crossEl) crossEl.innerText = res.cross_track.toFixed(1);
            if (compEl) compEl.innerText = Math.round(res.companion_station);
            if (timeEl) timeEl.innerText = new Date().toLocaleTimeString();
            if (subTitle) subTitle.innerText = res.label;
        }}

        // Browser Geolocation Watcher
        function startTracking() {{
            if (!('geolocation' in navigator)) {{
                updateTelemetryUI({{ state: 'LOCATION_LOST', label: 'Geolocation not supported in browser', speed_kmh: 0, accuracy: 0, along_track: 0, cross_track: 0, companion_station: 0 }});
                return;
            }}

            isTrackingEnabled = true;
            watchId = navigator.geolocation.watchPosition(
                function(pos) {{
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    const acc = pos.coords.accuracy || 10.0;
                    const rawSpd = pos.coords.speed;
                    const spdKmh = (rawSpd != null && rawSpd >= 0) ? (rawSpd * 3.6) : 0.0;

                    // Evaluate along-track progress
                    alongTrackS += (spdKmh > 1.8 ? spdKmh * 0.5 : 0.0);
                    if (activeSyncMode === 'FOLLOW_USER') {{
                        companionStationM = alongTrackS;
                    }} else {{
                        companionStationM += 2.0;
                    }}

                    // Determine State
                    let state = 'MOVING_FORWARD';
                    if (acc > 50.0) state = 'LOCATION_UNCERTAIN';
                    else if (spdKmh <= 1.2) {{
                        consecutiveSlow++;
                        if (consecutiveSlow >= 2) state = 'STATIONARY';
                    }} else {{
                        consecutiveSlow = 0;
                        if (Math.abs(alongTrackS - companionStationM) <= 60.0) state = 'MOVING_PARALLEL';
                    }}

                    updateTelemetryUI({{
                        state: state,
                        label: state === 'STATIONARY' ? 'User Stationary • Standing at Road Point' : 'Moving Along Route',
                        speed_kmh: spdKmh,
                        accuracy: acc,
                        along_track: alongTrackS,
                        cross_track: 2.5,
                        companion_station: companionStationM
                    }});
                }},
                function(err) {{
                    updateTelemetryUI({{
                        state: 'LOCATION_LOST',
                        label: 'GPS Access Notice: ' + err.message,
                        speed_kmh: 0,
                        accuracy: 0,
                        along_track: alongTrackS,
                        cross_track: 0,
                        companion_station: companionStationM
                    }});
                }},
                {{ enableHighAccuracy: true, maximumAge: 3000, timeout: 10000 }}
            );
        }}

        function stopTracking() {{
            if (watchId !== null) {{
                navigator.geolocation.clearWatch(watchId);
                watchId = null;
            }}
            isTrackingEnabled = false;
            updateTelemetryUI({{
                state: 'LOCATION_LOST',
                label: 'Location Tracking Paused by User',
                speed_kmh: 0,
                accuracy: 0,
                along_track: alongTrackS,
                cross_track: 0,
                companion_station: companionStationM
            }});
        }}

        window.toggleLocationTracking = function() {{
            if (isTrackingEnabled) {{
                stopTracking();
                const icon = document.getElementById('tracking-icon');
                const lbl = document.getElementById('tracking-label');
                if (icon) icon.innerText = '📡';
                if (lbl) lbl.innerText = 'Start Tracking';
            }} else {{
                startTracking();
                const icon = document.getElementById('tracking-icon');
                const lbl = document.getElementById('tracking-label');
                if (icon) icon.innerText = '⏹️';
                if (lbl) lbl.innerText = 'Stop Tracking';
            }}
        }};

        window.toggleSyncMode = function() {{
            activeSyncMode = activeSyncMode === 'FOLLOW_USER' ? 'INDEPENDENT' : 'FOLLOW_USER';
            const tag = document.getElementById('motion-sync-mode-tag');
            const lbl = document.getElementById('mode-label');
            const icon = document.getElementById('mode-icon');
            if (tag) tag.innerText = activeSyncMode === 'FOLLOW_USER' ? '● FOLLOW-USER MODE' : '● INDEPENDENT MODE';
            if (lbl) lbl.innerText = activeSyncMode === 'FOLLOW_USER' ? 'Mode: Follow User' : 'Mode: Independent';
            if (icon) icon.innerText = activeSyncMode === 'FOLLOW_USER' ? '👤' : '🤖';
        }};

        window.toggleDevPanel = function() {{
            const box = document.getElementById('dev-panel-box');
            const arrow = document.getElementById('dev-toggle-arrow');
            if (!box) return;
            const isOpen = box.style.display === 'block';
            box.style.display = isOpen ? 'none' : 'block';
            if (arrow) arrow.innerText = isOpen ? '▼' : '▲';
        }};

        window.simulateDevEvent = function(type) {{
            if (type === 'STOP') {{
                updateTelemetryUI({{ state: 'STATIONARY', label: 'Simulated Traffic Stop (0 km/h)', speed_kmh: 0, accuracy: 5, along_track: alongTrackS, cross_track: 0, companion_station: companionStationM }});
            }} else if (type === 'MOVE') {{
                alongTrackS += 20;
                companionStationM = alongTrackS;
                updateTelemetryUI({{ state: 'MOVING_PARALLEL', label: 'Simulated Move in Parallel (15 km/h)', speed_kmh: 15.0, accuracy: 5, along_track: alongTrackS, cross_track: 0, companion_station: companionStationM }});
            }} else if (type === 'CROSS') {{
                alongTrackS += 40;
                companionStationM = alongTrackS;
                checkpointIdx++;
                updateTelemetryUI({{ state: 'CHECKPOINT_CROSSED', label: 'Simulated Checkpoint Crossing Verified!', speed_kmh: 8.0, accuracy: 5, along_track: alongTrackS, cross_track: 0, companion_station: companionStationM }});
            }} else if (type === 'DEVIATION') {{
                updateTelemetryUI({{ state: 'ROUTE_DEVIATION', label: 'Simulated Route Deviation (85m off route)', speed_kmh: 12.0, accuracy: 10, along_track: alongTrackS, cross_track: 85.0, companion_station: companionStationM }});
            }} else if (type === 'BACKWARD') {{
                alongTrackS = Math.max(0, alongTrackS - 30);
                updateTelemetryUI({{ state: 'MOVING_BACKWARD', label: 'Simulated Moving Backward / Return Trip', speed_kmh: 6.0, accuracy: 5, along_track: alongTrackS, cross_track: 0, companion_station: companionStationM }});
            }}
        }};

        startTracking();
    }})();
    </script>
    """
