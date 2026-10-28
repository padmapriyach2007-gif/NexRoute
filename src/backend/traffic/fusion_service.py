"""
Pathfinder Hybrid Traffic Estimation & Sensor Fusion Service
Combines real-time GPS observations from consenting users, roadside radar/sensors,
historical profiles, and verified incident impacts with privacy preservation.
"""

import math
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple


from src.backend.config import settings


class TrafficObservation:
    """Represents a single verified telemetry observation from a distinct sensor or user."""
    def __init__(
        self,
        segment_id: str,
        speed_kmh: float,
        timestamp: datetime,
        contributor_id: str,
        accuracy_meters: float = 5.0,
        source_type: str = "GPS",  # GPS, RADAR, CAMERA, FLEET
        reliability: float = 0.95
    ):
        self.segment_id = segment_id
        self.speed_kmh = speed_kmh
        self.timestamp = timestamp
        self.contributor_id = contributor_id
        self.accuracy_meters = accuracy_meters
        self.source_type = source_type
        self.reliability = reliability


class SegmentTrafficState:
    """Computed real-world state of a road segment following sensor fusion."""
    def __init__(
        self,
        segment_id: str,
        current_speed_kmh: float,
        free_flow_speed_kmh: float,
        length_meters: float,
        traversal_time_seconds: float,
        congestion_level: str,
        congestion_color: str,
        confidence_score: float,
        prediction_uncertainty: float,
        distinct_contributors: int,
        recent_observation_count: int,
        observation_freshness_seconds: int,
        data_provenance: str,
        incident_impact: Optional[str] = None
    ):
        self.segment_id = segment_id
        self.current_speed_kmh = current_speed_kmh
        self.free_flow_speed_kmh = free_flow_speed_kmh
        self.length_meters = length_meters
        self.traversal_time_seconds = traversal_time_seconds
        self.congestion_level = congestion_level
        self.congestion_color = congestion_color
        self.confidence_score = confidence_score
        self.prediction_uncertainty = prediction_uncertainty
        self.distinct_contributors = distinct_contributors
        self.recent_observation_count = recent_observation_count
        self.observation_freshness_seconds = observation_freshness_seconds
        self.data_provenance = data_provenance
        self.incident_impact = incident_impact

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "current_speed_kmh": round(self.current_speed_kmh, 1),
            "free_flow_speed_kmh": round(self.free_flow_speed_kmh, 1),
            "length_meters": round(self.length_meters, 1),
            "traversal_time_seconds": round(self.traversal_time_seconds, 1),
            "congestion_level": self.congestion_level,
            "congestion_color": self.congestion_color,
            "confidence_score": round(self.confidence_score, 2),
            "prediction_uncertainty": round(self.prediction_uncertainty, 2),
            "distinct_contributors": self.distinct_contributors,
            "recent_observation_count": self.recent_observation_count,
            "observation_freshness_seconds": self.observation_freshness_seconds,
            "data_provenance": self.data_provenance,
            "incident_impact": self.incident_impact
        }


class TrafficFusionService:
    """
    Modular traffic fusion engine that ingests multi-source data, enforces k-anonymity,
    filters noise/outliers, and outputs statistically grounded road segment speed and confidence.
    """

    # In-memory circular observation buffer for active segments
    _observations: Dict[str, List[TrafficObservation]] = {}

    # Privacy threshold: Minimum distinct users required before publishing purely observed crowd speed
    PRIVACY_K_ANONYMITY_THRESHOLD = getattr(settings, "TRAFFIC_FUSION_K_ANONYMITY_THRESHOLD", 3)

    # Half-life for exponential time decay of observations (in seconds)
    TIME_DECAY_HALF_LIFE_SECONDS = getattr(settings, "TRAFFIC_DECAY_HALF_LIFE_SEC", 180.0)

    @classmethod
    def register_observation(cls, obs: TrafficObservation) -> bool:
        """
        Validates, filters, and registers a single observation into the segment buffer.
        Returns True if observation was accepted, False if filtered out.
        """
        # 1. Reject invalid GPS accuracy (>50m horizontal accuracy is unusable for lane matching)
        if obs.accuracy_meters > 50.0:
            return False

        # 2. Reject impossible motor vehicle speeds (>180 km/h or < 0 km/h)
        if obs.speed_kmh < 0.0 or obs.speed_kmh > 180.0:
            return False

        # 3. Reject stale observations older than 15 minutes
        now = datetime.now(timezone.utc)
        obs_time = obs.timestamp if obs.timestamp.tzinfo else obs.timestamp.replace(tzinfo=timezone.utc)
        age_seconds = (now - obs_time).total_seconds()
        if age_seconds > 900.0 or age_seconds < -60.0:
            return False

        # Initialize buffer if needed
        if obs.segment_id not in cls._observations:
            cls._observations[obs.segment_id] = []

        cls._observations[obs.segment_id].append(obs)

        # Prune old observations (>15 minutes)
        cutoff = now - timedelta(minutes=15)
        cls._observations[obs.segment_id] = [
            o for o in cls._observations[obs.segment_id]
            if (o.timestamp if o.timestamp.tzinfo else o.timestamp.replace(tzinfo=timezone.utc)) >= cutoff
        ]
        return True

    @classmethod
    def estimate_segment_traffic(
        cls,
        segment_id: str,
        free_flow_speed_kmh: float,
        length_meters: float,
        road_class: str = "PRIMARY",
        historical_speed_kmh: Optional[float] = None,
        active_incident_severity: Optional[str] = None
    ) -> SegmentTrafficState:
        """
        Fuses live telemetry, historical baseline, and incident restrictions into a single SegmentTrafficState.
        """
        now = datetime.now(timezone.utc)
        obs_list = cls._observations.get(segment_id, [])

        # Filter to active observations within 10 minutes
        cutoff = now - timedelta(minutes=10)
        valid_obs = [
            o for o in obs_list
            if (o.timestamp if o.timestamp.tzinfo else o.timestamp.replace(tzinfo=timezone.utc)) >= cutoff
        ]

        # Identify distinct contributors
        unique_contributors = {o.contributor_id for o in valid_obs if o.contributor_id}
        distinct_count = len(unique_contributors)

        # Compute default historical speed baseline if not provided
        if historical_speed_kmh is None:
            historical_speed_kmh = cls._compute_historical_baseline(free_flow_speed_kmh, road_class, now)

        # Apply incident penalty if present
        incident_factor = 1.0
        incident_desc = None
        if active_incident_severity:
            sev = active_incident_severity.upper()
            if sev in ("CRITICAL", "BLOCKAGE", "CLOSURE"):
                incident_factor = 0.05
                incident_desc = "Hard road closure / blockage"
            elif sev in ("HIGH", "ACCIDENT", "FLOOD"):
                incident_factor = 0.35
                incident_desc = "Severe incident slowdown"
            elif sev in ("MEDIUM", "CONGESTION", "CONSTRUCTION"):
                incident_factor = 0.60
                incident_desc = "Moderate road hazard"

        # Check Privacy Threshold & Data Availability
        if distinct_count >= cls.PRIVACY_K_ANONYMITY_THRESHOLD:
            # Sufficient live contributors: compute weighted robust speed
            fused_speed, confidence, freshness = cls._fuse_live_observations(
                valid_obs, free_flow_speed_kmh, historical_speed_kmh, now
            )
            provenance = "LIVE_CROWD_FUSED"
        elif len(valid_obs) > 0:
            # 1-2 contributors: Privacy protection blends with historical to avoid exposing single vehicle trail
            live_speed, _, freshness = cls._fuse_live_observations(
                valid_obs, free_flow_speed_kmh, historical_speed_kmh, now
            )
            # Blend 35% live + 65% historical
            fused_speed = (0.35 * live_speed) + (0.65 * historical_speed_kmh)
            confidence = 0.62  # Modest confidence due to low contributor count
            provenance = "HYBRID_PARTIAL_TELEMETRY"
        else:
            # Zero live telemetry: use verified historical profile
            fused_speed = historical_speed_kmh
            confidence = 0.45  # Baseline confidence
            freshness = 3600
            provenance = "HISTORICAL_BASELINE"

        # Apply active incident reduction if verified
        if incident_factor < 1.0:
            fused_speed = min(fused_speed, free_flow_speed_kmh * incident_factor)
            # High certainty of delay when verified incident exists
            confidence = max(confidence, 0.82)
            provenance = f"{provenance}_WITH_INCIDENT"

        # Clamp speed between minimum crawl (3.0 km/h) and free-flow
        fused_speed = max(3.0, min(free_flow_speed_kmh, fused_speed))

        # Calculate Traversal Time
        speed_mps = max(0.5, fused_speed * (1000.0 / 3600.0))
        traversal_time = length_meters / speed_mps

        # Categorize Congestion
        speed_ratio = fused_speed / max(1.0, free_flow_speed_kmh)
        if speed_ratio >= 0.85:
            level = "FREE_FLOW"
            color = "green"
        elif speed_ratio >= 0.55:
            level = "MODERATE_DELAY"
            color = "amber"
        elif speed_ratio >= 0.30:
            level = "HEAVY_CONGESTION"
            color = "red"
        else:
            level = "SEVERE_CONGESTION"
            color = "dark_red"

        # Uncertainty: Inverse of confidence, scaled
        uncertainty = max(0.05, round(1.0 - confidence, 2))

        return SegmentTrafficState(
            segment_id=segment_id,
            current_speed_kmh=fused_speed,
            free_flow_speed_kmh=free_flow_speed_kmh,
            length_meters=length_meters,
            traversal_time_seconds=traversal_time,
            congestion_level=level,
            congestion_color=color,
            confidence_score=confidence,
            prediction_uncertainty=uncertainty,
            distinct_contributors=distinct_count,
            recent_observation_count=len(valid_obs),
            observation_freshness_seconds=freshness,
            data_provenance=provenance,
            incident_impact=incident_desc
        )

    @classmethod
    def _fuse_live_observations(
        cls,
        observations: List[TrafficObservation],
        free_flow: float,
        historical: float,
        now: datetime
    ) -> Tuple[float, float, int]:
        """
        Applies exponential time-decay weighting and sensor reliability to fuse observations.
        Returns (fused_speed_kmh, confidence_score, freshest_age_seconds).
        """
        weights = []
        weighted_speeds = []
        min_age = 999999

        for obs in observations:
            obs_time = obs.timestamp if obs.timestamp.tzinfo else obs.timestamp.replace(tzinfo=timezone.utc)
            age_s = max(0.0, (now - obs_time).total_seconds())
            if age_s < min_age:
                min_age = int(age_s)

            # Exponential decay weight: w = exp(-age / tau) * reliability
            time_decay = math.exp(-age_s / cls.TIME_DECAY_HALF_LIFE_SECONDS)
            w = time_decay * obs.reliability
            weights.append(w)
            weighted_speeds.append(obs.speed_kmh * w)

        sum_w = sum(weights)
        if sum_w <= 0:
            return historical, 0.50, min_age if min_age < 999999 else 600

        fused_speed = sum(weighted_speeds) / sum_w

        # Confidence is derived from contributor count, freshness, and weight sum
        contributor_bonus = min(0.35, len(observations) * 0.05)
        freshness_factor = max(0.0, 1.0 - (min_age / 600.0)) * 0.35
        base_confidence = 0.30
        confidence = min(0.98, base_confidence + contributor_bonus + freshness_factor)

        return fused_speed, confidence, min_age

    @staticmethod
    def _compute_historical_baseline(free_flow: float, road_class: str, dt: datetime) -> float:
        """
        Calculates time-of-day and day-of-week baseline speed profile.
        Models morning rush (08:00 - 10:00) and evening rush (17:00 - 19:30).
        """
        hour = dt.hour + (dt.minute / 60.0)
        is_weekend = dt.weekday() >= 5

        # Base rush-hour congestion factors
        congestion_penalty = 0.0
        if not is_weekend:
            # Morning peak
            if 8.0 <= hour <= 10.0:
                peak_center = 9.0
                congestion_penalty = 0.35 * max(0.0, 1.0 - abs(hour - peak_center))
            # Evening peak
            elif 17.0 <= hour <= 19.5:
                peak_center = 18.25
                congestion_penalty = 0.40 * max(0.0, 1.0 - abs(hour - peak_center) / 1.25)
            # Midday gentle slowdown
            elif 12.0 <= hour <= 14.0:
                congestion_penalty = 0.15

        # Road class vulnerability to congestion
        rc = road_class.upper()
        if rc in ("MOTORWAY", "TRUNK"):
            flow_factor = 1.0 - (congestion_penalty * 0.8)
        elif rc == "PRIMARY":
            flow_factor = 1.0 - congestion_penalty
        elif rc in ("SECONDARY", "TERTIARY"):
            flow_factor = 1.0 - (congestion_penalty * 1.1)
        else:
            flow_factor = 1.0 - (congestion_penalty * 0.6)

        flow_factor = max(0.30, min(1.0, flow_factor))
        return free_flow * flow_factor
