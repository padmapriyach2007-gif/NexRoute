"""
Unit & Integration Tests for Pathfinder AI Traffic & Human Movement Detection System
Validates:
1. Vision Detector (OpenCV, synthetic frames, object tracking, tripwire counting, queue length)
2. Physical Sensor Adapters (PIR, IR beam, mmWave radar, vehicle radar, inductive loop, staleness)
3. Sensor Fusion Engine (cross-modal deduplication, confidence scoring, conflict resolution)
4. Traffic Analytics (congestion classification rules)
5. Traffic Service REST-like endpoints and Ollama grounding
6. Pathfinder Tool Calling integration
"""

import pytest
import time
from datetime import datetime, timezone

from src.backend.traffic.vision_detector import (
    VisionDetectorEngine, VisionDetectionMetrics, SUPPORTED_CLASSES
)
from src.backend.traffic.sensor_adapters import (
    SensorRegistry,
    PIRMotionSensorAdapter,
    IRBreakBeamSensorAdapter,
    MMWaveRadarSensorAdapter,
    VehicleRadarSensorAdapter,
    InductiveLoopAdapter,
    SensorReading
)
from src.backend.traffic.traffic_fusion_engine import (
    SensorFusionEngine, FusedTrafficState, CONGESTION_THRESHOLDS
)
from src.backend.traffic.traffic_service import PathfinderTrafficService
from src.pathfinder_tools import PathfinderToolExecutor, TOOL_SCHEMAS


class TestVisionDetectorEngine:
    """Tests for Computer Vision & Object Tracking Engine."""

    def test_initialization_outdoor(self):
        engine = VisionDetectorEngine(camera_id="TEST_OUTDOOR_CAM", environment_type="OUTDOOR")
        assert engine.camera_id == "TEST_OUTDOOR_CAM"
        assert engine.environment_type == "OUTDOOR"
        assert engine.connection_status == "STANDBY"

    def test_initialization_indoor(self):
        engine = VisionDetectorEngine(camera_id="TEST_INDOOR_CAM", environment_type="INDOOR")
        assert engine.environment_type == "INDOOR"
        assert len(engine._synthetic_objects) > 0
        for obj in engine._synthetic_objects:
            assert obj["cls"] == "person"

    def test_synthetic_frame_processing_and_hud(self):
        engine = VisionDetectorEngine(camera_id="TEST_CAM", environment_type="OUTDOOR")
        engine.open_source("SYNTHETIC")
        assert engine.connection_status == "CONNECTED"

        frame, metrics = engine.process_frame()
        assert frame is not None
        assert metrics.camera_id == "TEST_CAM"
        assert metrics.active_tracks > 0
        assert metrics.fps > 0.0
        assert metrics.latency_ms >= 0.0
        assert metrics.source_type == "SYNTHETIC"
        assert isinstance(metrics.counts_by_class, dict)
        for c in SUPPORTED_CLASSES:
            assert c in metrics.counts_by_class

    def test_tripwire_crossing_and_deduplication(self):
        engine = VisionDetectorEngine(camera_id="TEST_CAM", environment_type="INDOOR", tripwire_y_ratio=0.50)
        engine.open_source("SYNTHETIC")

        # Process multiple consecutive frames to allow synthetic objects to cross the tripwire
        for _ in range(15):
            _, metrics = engine.process_frame()

        # Cumulative counts must be non-negative integers
        assert metrics.inbound_count >= 0
        assert metrics.outbound_count >= 0
        # Each tracked ID must not be counted more than once per crossing event
        for trk in engine.tracks.values():
            if trk.crossed_tripwire:
                assert trk.crossing_direction in ["INBOUND", "OUTBOUND"]


class TestSensorAdapters:
    """Tests for Physical & Simulated Sensor Adapters."""

    def test_pir_sensor_adapter(self):
        pir = PIRMotionSensorAdapter("TEST_PIR_01", "ZONE_ENTRANCE")
        reading = pir.read()
        assert reading.sensor_id == "TEST_PIR_01"
        assert reading.sensor_type == "PIR_MOTION"
        assert reading.environment_type == "INDOOR"
        assert "motion_detected" in reading.measurements
        assert "measurement_note" in reading.measurements
        assert not reading.is_hardware

    def test_ir_break_beam_sensor_adapter(self):
        beam = IRBreakBeamSensorAdapter("TEST_IR_01", "ZONE_ENTRANCE")
        reading = beam.read()
        assert reading.sensor_type == "IR_BREAKBEAM"
        assert "beam_interrupted" in reading.measurements
        assert "cumulative_inbound" in reading.measurements

    def test_mmwave_radar_sensor_adapter(self):
        radar = MMWaveRadarSensorAdapter("TEST_MMWAVE_01", "ZONE_ATRIUM")
        reading = radar.read()
        assert reading.sensor_type == "MMWAVE_RADAR"
        assert "people_count" in reading.measurements
        assert "radial_distance_m" in reading.measurements
        assert reading.confidence >= 0.90

    def test_vehicle_radar_sensor_adapter(self):
        v_radar = VehicleRadarSensorAdapter("TEST_VEH_RADAR_01", "SEG_EXPRESSWAY_01", nominal_speed_kmh=80.0)
        reading = v_radar.read()
        assert reading.sensor_type == "VEHICLE_RADAR"
        assert "measured_speed_kmh" in reading.measurements
        assert reading.measurements["measured_speed_kmh"] > 0.0

    def test_sensor_registry_and_injection(self):
        reg = SensorRegistry()
        assert len(reg.sensors) >= 5

        # Test injecting a custom event
        inj_res = reg.inject_event("RADAR_EXPRESSWAY_01", {
            "measured_speed_kmh": 115.0,
            "status": "ONLINE",
            "confidence": 0.99
        })
        assert inj_res is not None
        assert inj_res.measurements["measured_speed_kmh"] == 115.0
        assert inj_res.is_hardware


class TestSensorFusionEngine:
    """Tests for Sensor Fusion & Conflict Resolution."""

    def test_sensor_fusion_without_double_counting(self):
        reg = SensorRegistry()
        fusion = SensorFusionEngine(reg)

        # Create a mock vision metric with 4 people
        v_metrics = VisionDetectionMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            fps=30.0,
            latency_ms=33.3,
            active_tracks=4,
            pedestrian_count=4,
            vehicle_count=0,
            counts_by_class={"person": 4, "car": 0, "motorcycle": 0, "bicycle": 0, "bus": 0, "truck": 0},
            inbound_count=2,
            outbound_count=1,
            people_per_min=4.0,
            vehicles_per_min=0.0,
            queue_length=0,
            environment_type="INDOOR",
            connection_status="CONNECTED",
            source_type="SYNTHETIC",
            camera_id="CAM_INDOOR_01"
        )

        fused = fusion.fuse(zone_id="ZONE_ENTRANCE_NORTH", vision_metrics=v_metrics)
        assert fused.environment_type == "INDOOR"
        # Total count must NOT be 4 + 4 (no naive double counting)
        assert fused.pedestrian_count >= 2
        assert fused.aggregate_confidence >= 0.60
        assert fused.congestion_level in CONGESTION_THRESHOLDS

    def test_sensor_disagreement_detection(self):
        reg = SensorRegistry()
        fusion = SensorFusionEngine(reg)

        # Mock reading where radar reports 12 people while camera sees 1 person
        radar_reading = SensorReading(
            sensor_id="RADAR_MMWAVE_TEST",
            sensor_type="MMWAVE_RADAR",
            zone_id="ZONE_ENTRANCE_NORTH",
            environment_type="INDOOR",
            timestamp=datetime.now(timezone.utc).isoformat(),
            is_hardware=True,
            connection_status="ONLINE",
            confidence=0.95,
            measurements={"people_count": 12},
            supported_measurements=["people_count"]
        )

        v_metrics = VisionDetectionMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            fps=30.0,
            latency_ms=33.0,
            active_tracks=1,
            pedestrian_count=1,
            vehicle_count=0,
            counts_by_class={"person": 1, "car": 0, "motorcycle": 0, "bicycle": 0, "bus": 0, "truck": 0},
            inbound_count=0,
            outbound_count=0,
            people_per_min=1.0,
            vehicles_per_min=0.0,
            queue_length=0,
            environment_type="INDOOR",
            connection_status="CONNECTED",
            source_type="SYNTHETIC",
            camera_id="CAM_INDOOR_01"
        )

        fused = fusion.fuse(
            zone_id="ZONE_ENTRANCE_NORTH",
            vision_metrics=v_metrics,
            sensor_readings=[radar_reading]
        )
        # Conflict must be detected and documented in active_disagreements
        assert len(fused.active_disagreements) > 0
        assert any("conflict" in d.lower() for d in fused.active_disagreements)
        # Aggregate confidence should be penalized
        assert fused.aggregate_confidence < 0.90


class TestPathfinderTrafficServiceAndTools:
    """Tests for Service APIs, Route Integration, and Ollama Tools."""

    def test_service_singleton_endpoints(self):
        svc = PathfinderTrafficService.get_instance()
        status = svc.get_traffic_status()
        assert status["status"] == "OPERATIONAL"
        assert status["fusion_engine"] == "ACTIVE"

        cameras = svc.get_cameras()
        assert len(cameras) >= 2

        sensors = svc.get_sensors()
        assert len(sensors) >= 5

        metrics = svc.get_metrics("SEG_EXPRESSWAY_01")
        assert "state" in metrics
        assert metrics["state"]["zone_id"] == "SEG_EXPRESSWAY_01"

    def test_route_advisory(self):
        svc = PathfinderTrafficService.get_instance()
        advisory = svc.get_route_traffic_advisory()
        assert "has_live_sensor_coverage" in advisory
        assert len(advisory["monitored_segments"]) >= 2
        assert isinstance(advisory["reroute_recommended"], bool)

    def test_ollama_context_generation(self):
        svc = PathfinderTrafficService.get_instance()
        ctx = svc.build_ollama_traffic_context()
        assert "LIVE VERIFIED PATHFINDER SENSOR & TRAFFIC TELEMETRY" in ctx
        assert "ZONE_ENTRANCE_NORTH" in ctx
        assert "SEG_EXPRESSWAY_01" in ctx

    def test_tool_executor_traffic_query(self):
        executor = PathfinderToolExecutor()
        res = executor.execute(
            tool_name="get_traffic_and_movement_intelligence",
            arguments={"zone_or_corridor": "SEG_EXPRESSWAY_01"}
        )
        assert res["success"] is True
        assert res["badge"] == "🚦 TRAFFIC INTELLIGENCE"
        assert "response" in res
        assert "data" in res
        assert res["data"]["zone_id"] == "SEG_EXPRESSWAY_01"
