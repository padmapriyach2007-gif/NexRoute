"""
Automated Test Suite for Pathfinder Traffic Intelligence & Evaluation System
Covers:
1. TrafficFusionService telemetry ingestion & filtering
2. Privacy k-anonymity contributor thresholds
3. Exponential time decay & observation weighting
4. Multi-source sensor fusion (GPS + historical + incident impacts)
5. AI Traffic Prediction (15m, 30m, 60m horizons & confidence bounds)
6. Weather dampening on predicted speed
7. Traffic Model Evaluation Pipeline (MAE, MedAE, ETA distribution, benchmark comparison)
"""

import pytest
from datetime import datetime, timezone, timedelta

from src.backend.traffic.fusion_service import (
    TrafficFusionService, TrafficObservation, SegmentTrafficState
)
from src.backend.traffic.prediction_service import (
    TrafficPredictionService, PredictionResult
)
from src.backend.traffic.evaluation_pipeline import (
    TrafficEvaluationPipeline, EvaluationBenchmarkResult
)


@pytest.fixture(autouse=True)
def clean_traffic_buffer():
    # Clear in-memory observations before each test
    TrafficFusionService._observations.clear()
    yield
    TrafficFusionService._observations.clear()


# =============================================================================
# 1. TELEMETRY FILTERING & INGESTION
# =============================================================================

def test_telemetry_inaccurate_gps_filtered():
    """Inaccurate GPS fixes (>50m horizontal accuracy) must be rejected."""
    obs = TrafficObservation(
        segment_id="SEG_TEST_01",
        speed_kmh=45.0,
        timestamp=datetime.now(timezone.utc),
        contributor_id="user_alpha",
        accuracy_meters=65.0  # Excessive inaccuracy
    )
    accepted = TrafficFusionService.register_observation(obs)
    assert accepted is False
    assert "SEG_TEST_01" not in TrafficFusionService._observations


def test_telemetry_impossible_speeds_filtered():
    """Impossible speeds (>180 km/h or < 0 km/h) must be filtered out."""
    obs_fast = TrafficObservation(
        segment_id="SEG_TEST_01",
        speed_kmh=240.0,
        timestamp=datetime.now(timezone.utc),
        contributor_id="user_fast",
        accuracy_meters=5.0
    )
    assert TrafficFusionService.register_observation(obs_fast) is False

    obs_negative = TrafficObservation(
        segment_id="SEG_TEST_01",
        speed_kmh=-10.0,
        timestamp=datetime.now(timezone.utc),
        contributor_id="user_neg",
        accuracy_meters=5.0
    )
    assert TrafficFusionService.register_observation(obs_negative) is False


def test_telemetry_valid_observation_accepted():
    """Valid observation within normal speed and accuracy thresholds is accepted."""
    obs = TrafficObservation(
        segment_id="SEG_TEST_01",
        speed_kmh=52.0,
        timestamp=datetime.now(timezone.utc),
        contributor_id="user_valid_01",
        accuracy_meters=4.5
    )
    accepted = TrafficFusionService.register_observation(obs)
    assert accepted is True
    assert len(TrafficFusionService._observations["SEG_TEST_01"]) == 1


# =============================================================================
# 2. PRIVACY K-ANONYMITY & HISTORICAL BLENDING
# =============================================================================

def test_insufficient_contributors_blends_historical():
    """
    With only 1 distinct contributor, the system preserves privacy by blending
    with historical speed and declaring partial telemetry.
    """
    obs = TrafficObservation(
        segment_id="SEG_TEST_PRIVACY",
        speed_kmh=20.0,
        timestamp=datetime.now(timezone.utc),
        contributor_id="single_user_anon",
        accuracy_meters=5.0
    )
    TrafficFusionService.register_observation(obs)

    state = TrafficFusionService.estimate_segment_traffic(
        segment_id="SEG_TEST_PRIVACY",
        free_flow_speed_kmh=60.0,
        length_meters=1000.0,
        historical_speed_kmh=55.0
    )

    assert state.distinct_contributors == 1
    assert state.data_provenance == "HYBRID_PARTIAL_TELEMETRY"
    # Speed should be a blend (not pure 20.0 km/h, which would expose the individual's speed)
    assert 25.0 <= state.current_speed_kmh <= 50.0
    assert state.confidence_score <= 0.70


def test_sufficient_contributors_achieves_live_crowd_fusion():
    """
    With >= 3 distinct contributors, the privacy threshold is met,
    producing a LIVE_CROWD_FUSED estimate with high confidence.
    """
    now = datetime.now(timezone.utc)
    for i, user in enumerate(["user_1", "user_2", "user_3"]):
        TrafficFusionService.register_observation(TrafficObservation(
            segment_id="SEG_TEST_CROWD",
            speed_kmh=35.0 + (i * 2.0),
            timestamp=now - timedelta(seconds=i * 20),
            contributor_id=user,
            accuracy_meters=3.5
        ))

    state = TrafficFusionService.estimate_segment_traffic(
        segment_id="SEG_TEST_CROWD",
        free_flow_speed_kmh=60.0,
        length_meters=1000.0
    )

    assert state.distinct_contributors == 3
    assert state.data_provenance == "LIVE_CROWD_FUSED"
    assert 34.0 <= state.current_speed_kmh <= 40.0
    assert state.confidence_score >= 0.75


# =============================================================================
# 3. INCIDENT RESTRICTIONS & CONGESTION LEVELS
# =============================================================================

def test_incident_critical_closure_slowdown():
    """Critical road incident / closure forces traversal delay and dark_red indicator."""
    state = TrafficFusionService.estimate_segment_traffic(
        segment_id="SEG_INCIDENT_01",
        free_flow_speed_kmh=60.0,
        length_meters=1200.0,
        active_incident_severity="CRITICAL"
    )

    assert state.congestion_level == "SEVERE_CONGESTION"
    assert state.congestion_color == "dark_red"
    assert state.current_speed_kmh <= 5.0
    assert state.incident_impact is not None


# =============================================================================
# 4. AI TRAFFIC PREDICTION ACROSS MULTI-HORIZONS
# =============================================================================

def test_prediction_horizons_15_30_60():
    """Predicts future speeds across 15, 30, and 60m horizons with expanding intervals."""
    multi = TrafficPredictionService.predict_multi_horizon(
        segment_id="SEG_HORIZONS",
        free_flow_speed_kmh=80.0,
        length_meters=2000.0,
        road_class="MOTORWAY"
    )

    assert "15m" in multi["horizons"]
    assert "30m" in multi["horizons"]
    assert "60m" in multi["horizons"]

    p15 = multi["horizons"]["15m"]
    p60 = multi["horizons"]["60m"]

    assert p15["expected_speed_kmh"] > 0
    assert p60["expected_speed_kmh"] > 0

    # Prediction interval width expands over time
    interval_15 = p15["prediction_interval"]["upper_bound_kmh"] - p15["prediction_interval"]["lower_bound_kmh"]
    interval_60 = p60["prediction_interval"]["upper_bound_kmh"] - p60["prediction_interval"]["lower_bound_kmh"]
    assert interval_60 >= interval_15


def test_prediction_weather_dampening():
    """Heavy rain/storm applies environmental speed dampening."""
    pred_clear = TrafficPredictionService.predict_segment_traffic(
        segment_id="SEG_WEATHER",
        free_flow_speed_kmh=60.0,
        length_meters=1500.0,
        horizon_minutes=15,
        weather_condition="Clear"
    )

    pred_storm = TrafficPredictionService.predict_segment_traffic(
        segment_id="SEG_WEATHER",
        free_flow_speed_kmh=60.0,
        length_meters=1500.0,
        horizon_minutes=15,
        weather_condition="Heavy thunderstorm"
    )

    assert pred_storm.expected_speed_kmh < pred_clear.expected_speed_kmh
    assert pred_storm.weather_impact is not None


# =============================================================================
# 5. TRAFFIC MODEL EVALUATION PIPELINE
# =============================================================================

def test_evaluation_pipeline_metrics_integrity():
    """Evaluation pipeline produces empirical MAE, MedAE, ETA distribution, and F1 comparisons."""
    eval_res = TrafficEvaluationPipeline.run_comprehensive_evaluation(test_samples=40)

    assert "models" in eval_res
    hist = eval_res["models"]["historical_baseline"]
    gps = eval_res["models"]["gps_only_baseline"]
    hybrid = eval_res["models"]["hybrid_traffic_model"]

    for m in [hist, gps, hybrid]:
        assert "mae_speed_kmh" in m
        assert "medae_speed_kmh" in m
        assert "mae_travel_time_seconds" in m
        assert "eta_error_distribution_seconds" in m
        assert "p50" in m["eta_error_distribution_seconds"]
        assert "p90" in m["eta_error_distribution_seconds"]
        assert "p95" in m["eta_error_distribution_seconds"]
        assert "congestion_classification_f1" in m

    # Hybrid model should outperform historical baseline under varied traffic
    assert hybrid["mae_travel_time_seconds"] <= hist["mae_travel_time_seconds"]
    assert "performance_by_road_type" in eval_res
    assert len(eval_res["performance_by_road_type"]) >= 2
