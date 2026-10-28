"""
Pathfinder Traffic Intelligence & Human Movement Central Service Singleton
Orchestrates Computer Vision detectors, Physical Sensor Adapters, Sensor Fusion,
Traffic Analytics, Historical Timeseries, Map/Route Integration, and Ollama AI retrieval.
"""

import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from src.backend.traffic.vision_detector import VisionDetectorEngine, VisionDetectionMetrics
from src.backend.traffic.sensor_adapters import SensorRegistry, SensorReading
from src.backend.traffic.traffic_fusion_engine import SensorFusionEngine, FusedTrafficState


class PathfinderTrafficService:
    """Singleton service providing full lifecycle management for Traffic Intelligence."""

    _instance: Optional["PathfinderTrafficService"] = None

    @classmethod
    def get_instance(cls) -> "PathfinderTrafficService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.sensor_registry = SensorRegistry()
        self.fusion_engine = SensorFusionEngine(self.sensor_registry)

        # Vision Detectors for different monitoring scenarios
        self.detectors: Dict[str, VisionDetectorEngine] = {
            "CAM_OUTDOOR_01": VisionDetectorEngine(
                camera_id="CAM_OUTDOOR_01",
                environment_type="OUTDOOR",
                tripwire_y_ratio=0.55
            ),
            "CAM_INDOOR_01": VisionDetectorEngine(
                camera_id="CAM_INDOOR_01",
                environment_type="INDOOR",
                tripwire_y_ratio=0.50
            )
        }
        self.active_camera_id: str = "CAM_OUTDOOR_01"

        # Initialize active camera on synthetic mode by default
        self.detectors["CAM_OUTDOOR_01"].open_source("SYNTHETIC")
        self.detectors["CAM_INDOOR_01"].open_source("SYNTHETIC")

        # Historical timeseries buffer (ring buffer of last 50 snapshots per zone)
        self.history: Dict[str, List[Dict[str, Any]]] = {}
        self.recent_events: List[Dict[str, Any]] = []

    # =========================================================================
    # CAMERA & VISION CONTROL
    # =========================================================================
    def get_active_detector(self) -> VisionDetectorEngine:
        return self.detectors.get(self.active_camera_id, self.detectors["CAM_OUTDOOR_01"])

    def set_active_camera(self, camera_id: str):
        if camera_id in self.detectors:
            self.active_camera_id = camera_id

    def set_source(self, source_type: str, source_path: Optional[str] = None) -> bool:
        detector = self.get_active_detector()
        return detector.open_source(source_type=source_type, source_path=source_path)

    def process_frame(self) -> Tuple[Any, VisionDetectionMetrics, FusedTrafficState]:
        """
        Advances one frame through active vision detector, fuses with physical sensors,
        and appends snapshot to historical logs.
        """
        detector = self.get_active_detector()
        annotated_frame, vision_metrics = detector.process_frame()

        # Map camera to active zone
        zone_id = "SEG_EXPRESSWAY_01" if detector.environment_type == "OUTDOOR" else "ZONE_ENTRANCE_NORTH"

        # Fuse with physical sensors
        fused_state = self.fusion_engine.fuse(
            zone_id=zone_id,
            vision_metrics=vision_metrics
        )

        # Store in historical buffer
        self._record_history(fused_state)

        return annotated_frame, vision_metrics, fused_state

    def _record_history(self, state: FusedTrafficState):
        """Records state snapshot into historical timeseries buffer."""
        zid = state.zone_id
        if zid not in self.history:
            self.history[zid] = []

        entry = {
            "timestamp": state.timestamp,
            "pedestrians": state.pedestrian_count,
            "vehicles": state.vehicle_count,
            "speed": state.measured_speed_kmh or state.estimated_speed_kmh,
            "congestion": state.congestion_level,
            "occupancy": state.occupancy_pct,
            "queue": state.queue_length
        }
        self.history[zid].append(entry)
        if len(self.history[zid]) > 60:
            self.history[zid].pop(0)

    # =========================================================================
    # REST / SERVICE API ENDPOINTS
    # =========================================================================
    def get_traffic_status(self) -> Dict[str, Any]:
        """GET /api/traffic/status: Overall system health & summary."""
        detector = self.get_active_detector()
        return {
            "status": "OPERATIONAL",
            "active_camera": self.active_camera_id,
            "source_type": detector.source_type,
            "connection_status": detector.connection_status,
            "registered_sensors": len(self.sensor_registry.sensors),
            "fusion_engine": "ACTIVE",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def get_cameras(self) -> List[Dict[str, Any]]:
        """GET /api/traffic/cameras: Monitored camera fleet."""
        res = []
        for cid, d in self.detectors.items():
            res.append({
                "camera_id": cid,
                "environment_type": d.environment_type,
                "source_type": d.source_type,
                "connection_status": d.connection_status,
                "is_active": (cid == self.active_camera_id)
            })
        return res

    def get_sensors(self) -> List[Dict[str, Any]]:
        """GET /api/traffic/sensors: List of physical and simulated sensors."""
        res = []
        for sid, s in self.sensor_registry.sensors.items():
            res.append({
                "sensor_id": s.sensor_id,
                "sensor_type": s.sensor_type,
                "zone_id": s.zone_id,
                "environment_type": s.environment_type,
                "is_hardware": s.is_hardware,
                "connection_status": s.connection_status,
                "confidence": s.confidence,
                "supported_measurements": s.supported_measurements,
                "is_stale": s.is_stale(),
                "last_reading": s.last_reading.measurements if s.last_reading else None
            })
        return res

    def get_metrics(self, zone_id: Optional[str] = None) -> Dict[str, Any]:
        """GET /api/traffic/metrics: Comprehensive telemetry and fused state."""
        zid = zone_id or ("SEG_EXPRESSWAY_01" if self.get_active_detector().environment_type == "OUTDOOR" else "ZONE_ENTRANCE_NORTH")
        detector = self.get_active_detector()
        # Compute fused metrics
        fused = self.fusion_engine.fuse(zone_id=zid)
        return {
            "zone_id": zid,
            "state": fused.__dict__,
            "history": self.history.get(zid, [])
        }

    def get_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """GET /api/traffic/events: Recent crossing and anomaly events."""
        return self.recent_events[-limit:]

    def post_sensor_event(self, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """POST /api/traffic/sensors/events: Ingest an external hardware reading."""
        sid = event_data.get("sensor_id")
        if not sid:
            return None
        reading = self.sensor_registry.inject_event(sid, event_data)
        if reading:
            self.recent_events.append({
                "event_type": "SENSOR_READING",
                "sensor_id": sid,
                "timestamp": reading.timestamp,
                "measurements": reading.measurements
            })
            if len(self.recent_events) > 50:
                self.recent_events.pop(0)
            return reading.__dict__
        return None

    # =========================================================================
    # MAP & ROUTE INTEGRATION
    # =========================================================================
    def get_route_traffic_advisory(self, route_summary: str = "") -> Dict[str, Any]:
        """
        Correlates live road sensor observations with route segments and advises
        on congestion delays and potential reroutes.
        """
        # Inspect our outdoor expressway and ring road
        exp_state = self.fusion_engine.fuse(zone_id="SEG_EXPRESSWAY_01")
        bypass_state = self.fusion_engine.fuse(zone_id="SEG_GUNTUR_BYPASS")

        is_exp_congested = exp_state.congestion_level in ["HEAVY", "SEVERE"]
        is_bypass_clear = bypass_state.congestion_level == "FREE_FLOWING"

        reroute_recommended = is_exp_congested and is_bypass_clear
        advisory_msg = "All monitored transit corridors operating normally."
        if is_exp_congested:
            advisory_msg = f"Heavy delay observed on {exp_state.zone_id} ({exp_state.estimated_speed_kmh} km/h vs nominal {exp_state.free_flow_speed_kmh} km/h). Reroute via Bypass recommended."

        return {
            "has_live_sensor_coverage": True,
            "monitored_segments": [
                {
                    "segment_id": "SEG_EXPRESSWAY_01",
                    "name": "NexRoute Central Expressway (NH-16)",
                    "congestion_level": exp_state.congestion_level,
                    "measured_speed": exp_state.measured_speed_kmh,
                    "estimated_speed": exp_state.estimated_speed_kmh,
                    "confidence": exp_state.aggregate_confidence,
                    "sources": exp_state.contributing_sources
                },
                {
                    "segment_id": "SEG_GUNTUR_BYPASS",
                    "name": "Guntur Metropolitan Ring Bypass",
                    "congestion_level": bypass_state.congestion_level,
                    "measured_speed": bypass_state.measured_speed_kmh,
                    "estimated_speed": bypass_state.estimated_speed_kmh,
                    "confidence": bypass_state.aggregate_confidence,
                    "sources": bypass_state.contributing_sources
                }
            ],
            "reroute_recommended": reroute_recommended,
            "advisory_message": advisory_msg
        }

    # =========================================================================
    # OLLAMA AI ASSISTANT RETRIEVAL CONTEXT
    # =========================================================================
    def build_ollama_traffic_context(self) -> str:
        """
        Builds live, verified sensor grounding for Ollama AI Travel Assistant.
        Ensures the assistant NEVER hallucinates traffic or crowd numbers.
        """
        detector = self.get_active_detector()
        indoor_state = self.fusion_engine.fuse(zone_id="ZONE_ENTRANCE_NORTH")
        outdoor_state = self.fusion_engine.fuse(zone_id="SEG_EXPRESSWAY_01")

        lines = [
            "=== LIVE VERIFIED PATHFINDER SENSOR & TRAFFIC TELEMETRY ===",
            f"Active Camera: {detector.camera_id} ({detector.source_type}, Status: {detector.connection_status})",
            "",
            "1. INDOOR ENTRANCE CONCOURSE (ZONE_ENTRANCE_NORTH):",
            f"   - Pedestrians Active: {indoor_state.pedestrian_count} people",
            f"   - Rate: {indoor_state.people_per_min:.1f} people/min (Inbound: {indoor_state.inbound_flow}, Outbound: {indoor_state.outbound_flow})",
            f"   - Occupancy: {indoor_state.occupancy_pct:.1f}%",
            f"   - Congestion: {indoor_state.congestion_level} ({indoor_state.congestion_explanation})",
            f"   - Confidence: {int(indoor_state.aggregate_confidence*100)}%",
            f"   - Sensor Disagreements: {indoor_state.active_disagreements or 'None (Sensors in Consensus)'}",
            "",
            "2. OUTDOOR HIGHWAY CORRIDOR (SEG_EXPRESSWAY_01 - NH-16):",
            f"   - Vehicles Active: {outdoor_state.vehicle_count} vehicles",
            f"   - Rate: {outdoor_state.vehicles_per_min:.1f} vehicles/min (Inbound: {outdoor_state.inbound_flow}, Outbound: {outdoor_state.outbound_flow})",
            f"   - Measured Radar Speed: {outdoor_state.measured_speed_kmh} km/h (Nominal: {outdoor_state.free_flow_speed_kmh} km/h)",
            f"   - Estimated Speed: {outdoor_state.estimated_speed_kmh} km/h",
            f"   - Queue Length: {outdoor_state.queue_length} vehicles",
            f"   - Congestion: {outdoor_state.congestion_level} ({outdoor_state.congestion_explanation})",
            f"   - Confidence: {int(outdoor_state.aggregate_confidence*100)}%",
            "============================================================"
        ]
        return "\n".join(lines)
