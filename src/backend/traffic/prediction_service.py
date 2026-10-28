"""
Pathfinder AI Traffic Prediction Service
Provides predictive travel time and speed forecasting across 15, 30, and 60-minute
time horizons using historical harmonic profiles, live telemetry trends, weather,
and active road incident dampening.
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
from src.backend.traffic.fusion_service import TrafficFusionService, SegmentTrafficState


class PredictionResult:
    """Encapsulates a forward-looking traffic forecast for a given time horizon."""
    def __init__(
        self,
        segment_id: str,
        horizon_minutes: int,
        target_time: datetime,
        expected_speed_kmh: float,
        expected_travel_time_seconds: float,
        prediction_interval_lower_kmh: float,
        prediction_interval_upper_kmh: float,
        confidence_score: float,
        model_version: str = "Pathfinder-AI-Traffic-v2.5",
        input_data_freshness_seconds: int = 60,
        weather_impact: Optional[str] = None
    ):
        self.segment_id = segment_id
        self.horizon_minutes = horizon_minutes
        self.target_time = target_time
        self.expected_speed_kmh = expected_speed_kmh
        self.expected_travel_time_seconds = expected_travel_time_seconds
        self.prediction_interval_lower_kmh = prediction_interval_lower_kmh
        self.prediction_interval_upper_kmh = prediction_interval_upper_kmh
        self.confidence_score = confidence_score
        self.model_version = model_version
        self.input_data_freshness_seconds = input_data_freshness_seconds
        self.weather_impact = weather_impact

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "horizon_minutes": self.horizon_minutes,
            "target_time": self.target_time.isoformat(),
            "expected_speed_kmh": round(self.expected_speed_kmh, 1),
            "expected_travel_time_seconds": round(self.expected_travel_time_seconds, 1),
            "prediction_interval": {
                "lower_bound_kmh": round(self.prediction_interval_lower_kmh, 1),
                "upper_bound_kmh": round(self.prediction_interval_upper_kmh, 1)
            },
            "confidence_score": round(self.confidence_score, 2),
            "model_version": self.model_version,
            "input_data_freshness_seconds": self.input_data_freshness_seconds,
            "weather_impact": self.weather_impact
        }


class TrafficPredictionService:
    """
    AI Traffic Forecaster.
    Combines:
    - Autoregressive short-term live persistence (dominates at 15m)
    - Mean-reverting historical harmonic patterns (dominates at 60m)
    - Environmental dampening (e.g. rain, low visibility)
    - Road category congestion elasticity
    """

    SUPPORTED_HORIZONS = [15, 30, 60]
    MODEL_VERSION = "Pathfinder-AI-Traffic-v2.5"

    @classmethod
    def predict_segment_traffic(
        cls,
        segment_id: str,
        free_flow_speed_kmh: float,
        length_meters: float,
        road_class: str = "PRIMARY",
        horizon_minutes: int = 15,
        weather_condition: Optional[str] = None,
        active_incident_severity: Optional[str] = None
    ) -> PredictionResult:
        """
        Generates predictive speed and travel time for a specified time horizon.
        """
        if horizon_minutes not in cls.SUPPORTED_HORIZONS:
            # Snap to closest supported horizon
            horizon_minutes = min(cls.SUPPORTED_HORIZONS, key=lambda x: abs(x - horizon_minutes))

        now = datetime.now(timezone.utc)
        target_time = now + timedelta(minutes=horizon_minutes)

        # 1. Get Current Fused State
        current_state = TrafficFusionService.estimate_segment_traffic(
            segment_id=segment_id,
            free_flow_speed_kmh=free_flow_speed_kmh,
            length_meters=length_meters,
            road_class=road_class,
            active_incident_severity=active_incident_severity
        )

        current_speed = current_state.current_speed_kmh
        freshness = current_state.observation_freshness_seconds

        # 2. Compute Historical Speed at Target Future Time
        future_hist_speed = TrafficFusionService._compute_historical_baseline(
            free_flow=free_flow_speed_kmh,
            road_class=road_class,
            dt=target_time
        )

        # 3. Time-Horizon Weighting:
        # At 15m: 65% current speed + 35% target historical
        # At 30m: 40% current speed + 60% target historical
        # At 60m: 15% current speed + 85% target historical
        if horizon_minutes == 15:
            alpha = 0.65
        elif horizon_minutes == 30:
            alpha = 0.40
        else:
            alpha = 0.15

        base_predicted_speed = (alpha * current_speed) + ((1.0 - alpha) * future_hist_speed)

        # 4. Environmental & Weather Dampening
        weather_desc = None
        weather_factor = 1.0
        if weather_condition:
            w_lower = weather_condition.lower()
            if "storm" in w_lower or "heavy rain" in w_lower or "flood" in w_lower:
                weather_factor = 0.70
                weather_desc = "Heavy precipitation dampening (-30% speed)"
            elif "rain" in w_lower or "shower" in w_lower:
                weather_factor = 0.85
                weather_desc = "Wet road surface dampening (-15% speed)"
            elif "fog" in w_lower or "mist" in w_lower:
                weather_factor = 0.80
                weather_desc = "Reduced visibility dampening (-20% speed)"

        predicted_speed = base_predicted_speed * weather_factor

        # 5. Incident dissipation or persistence
        if active_incident_severity:
            # Severe incidents persist across horizons; minor incidents dissipate by 60m
            if horizon_minutes == 60 and active_incident_severity.upper() in ("LOW", "CONGESTION"):
                predicted_speed = max(predicted_speed, future_hist_speed * 0.90)

        # Clamp speed
        predicted_speed = max(3.0, min(free_flow_speed_kmh, predicted_speed))

        # 6. Prediction Interval (95% bounds expand with time horizon)
        # Horizon 15m: ±10% margin, 30m: ±18%, 60m: ±25%
        margin_percent = 0.08 + (0.003 * horizon_minutes)
        margin_kmh = predicted_speed * margin_percent
        lower_bound = max(2.5, predicted_speed - margin_kmh)
        upper_bound = min(free_flow_speed_kmh, predicted_speed + margin_kmh)

        # 7. Confidence Score (decays gently with forecast horizon)
        base_confidence = current_state.confidence_score
        horizon_penalty = 0.0035 * horizon_minutes
        confidence = max(0.40, base_confidence - horizon_penalty)

        # 8. Expected Travel Time
        speed_mps = max(0.5, predicted_speed * (1000.0 / 3600.0))
        expected_travel_time = length_meters / speed_mps

        return PredictionResult(
            segment_id=segment_id,
            horizon_minutes=horizon_minutes,
            target_time=target_time,
            expected_speed_kmh=predicted_speed,
            expected_travel_time_seconds=expected_travel_time,
            prediction_interval_lower_kmh=lower_bound,
            prediction_interval_upper_kmh=upper_bound,
            confidence_score=confidence,
            model_version=cls.MODEL_VERSION,
            input_data_freshness_seconds=freshness,
            weather_impact=weather_desc
        )

    @classmethod
    def predict_multi_horizon(
        cls,
        segment_id: str,
        free_flow_speed_kmh: float,
        length_meters: float,
        road_class: str = "PRIMARY",
        weather_condition: Optional[str] = None,
        active_incident_severity: Optional[str] = None
    ) -> Dict[str, Any]:
        """Returns predictions for 15m, 30m, and 60m horizons in a single consolidated report."""
        horizons = {}
        for h in cls.SUPPORTED_HORIZONS:
            pred = cls.predict_segment_traffic(
                segment_id=segment_id,
                free_flow_speed_kmh=free_flow_speed_kmh,
                length_meters=length_meters,
                road_class=road_class,
                horizon_minutes=h,
                weather_condition=weather_condition,
                active_incident_severity=active_incident_severity
            )
            horizons[f"{h}m"] = pred.to_dict()

        return {
            "segment_id": segment_id,
            "road_class": road_class,
            "free_flow_speed_kmh": free_flow_speed_kmh,
            "model_version": cls.MODEL_VERSION,
            "horizons": horizons
        }
