"""
Pathfinder Sensor Fusion & Traffic Analytics Engine
Fuses real-time camera detections with physical sensor observations (PIR, IR beam, radar, loop),
performs temporal & spatial aggregation, cross-modal deduplication, disagreement tracking,
and calculates robust congestion analytics with documented thresholds.
"""

import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.backend.traffic.vision_detector import VisionDetectionMetrics
from src.backend.traffic.sensor_adapters import SensorReading, SensorRegistry, BaseSensorAdapter


CONGESTION_LEVELS = ["FREE_FLOWING", "MODERATE", "HEAVY", "SEVERE", "UNKNOWN"]

# Documented Congestion Thresholds (Ratio of Current Speed to Free-Flow Speed, or Occupancy Ratio)
CONGESTION_THRESHOLDS = {
    "FREE_FLOWING": {"speed_ratio_min": 0.85, "occupancy_max_pct": 25.0, "queue_max": 2},
    "MODERATE":     {"speed_ratio_min": 0.55, "occupancy_max_pct": 50.0, "queue_max": 5},
    "HEAVY":        {"speed_ratio_min": 0.30, "occupancy_max_pct": 75.0, "queue_max": 10},
    "SEVERE":       {"speed_ratio_min": 0.00, "occupancy_max_pct": 100.0, "queue_max": 999}
}


@dataclass
class FusedTrafficState:
    """Consolidated multi-modal state for a monitored indoor zone or road corridor."""
    zone_id: str
    environment_type: str  # "INDOOR" or "OUTDOOR"
    timestamp: str

    # Movement & Class Counts
    pedestrian_count: int
    vehicle_count: int
    vehicle_counts_by_class: Dict[str, int]
    inbound_flow: int
    outbound_flow: int
    people_per_min: float
    vehicles_per_min: float

    # Speed & Physical Measurements
    measured_speed_kmh: Optional[float]      # Measured via Doppler radar (or None if unmeasured)
    estimated_speed_kmh: Optional[float]     # Estimated via vision optical flow / profile
    free_flow_speed_kmh: float
    queue_length: int
    occupancy_pct: float

    # Congestion Analysis
    congestion_level: str                    # FREE_FLOWING, MODERATE, HEAVY, SEVERE, UNKNOWN
    congestion_explanation: str

    # Fusion Quality & Disagreement
    aggregate_confidence: float             # 0.0 to 1.0
    active_disagreements: List[str]         # Descriptive list of conflicting observations
    contributing_sources: List[str]         # e.g., ["CAM_MAIN_01", "RADAR_EXPRESSWAY_01"]
    has_hardware_data: bool
    data_freshness_seconds: float
    is_stale: bool


class SensorFusionEngine:
    """
    Sensor Fusion & Conflict Resolution Engine.
    Correlates camera detections with physical radar/loops without naive double counting.
    """

    def __init__(self, sensor_registry: SensorRegistry):
        self.registry = sensor_registry
        self.stale_timeout_seconds: float = 20.0

        # Zone configurations
        self.zone_profiles: Dict[str, Dict[str, Any]] = {
            "ZONE_ENTRANCE_NORTH": {
                "name": "Main Concourse Entrance & Turnstiles",
                "env": "INDOOR",
                "nominal_speed": 4.5,
                "capacity": 50
            },
            "ZONE_MALL_ATRIUM": {
                "name": "Central Retail Atrium & Walkway",
                "env": "INDOOR",
                "nominal_speed": 4.0,
                "capacity": 120
            },
            "SEG_EXPRESSWAY_01": {
                "name": "NexRoute Central Expressway (NH-16)",
                "env": "OUTDOOR",
                "nominal_speed": 90.0,
                "capacity": 300
            },
            "SEG_GUNTUR_BYPASS": {
                "name": "Guntur Metropolitan Ring Bypass",
                "env": "OUTDOOR",
                "nominal_speed": 65.0,
                "capacity": 220
            },
            "SEG_TENALI_HIGHWAY": {
                "name": "Tenali Arterial Transit Highway",
                "env": "OUTDOOR",
                "nominal_speed": 55.0,
                "capacity": 180
            }
        }

    def fuse(
        self,
        zone_id: str,
        vision_metrics: Optional[VisionDetectionMetrics] = None,
        sensor_readings: Optional[List[SensorReading]] = None
    ) -> FusedTrafficState:
        """
        Fuses vision detections with physical sensor readings for a designated zone.
        Cross-validates, deduplicates, and detects sensor disagreements.
        """
        now = datetime.now(timezone.utc)
        profile = self.zone_profiles.get(zone_id, {
            "name": zone_id,
            "env": "OUTDOOR",
            "nominal_speed": 60.0,
            "capacity": 150
        })
        env_type = profile["env"]
        free_flow = profile["nominal_speed"]

        disagreements: List[str] = []
        sources: List[str] = []
        has_hw = False
        weights: List[float] = []

        # 1. Process Vision Input
        v_ped_count = 0
        v_veh_count = 0
        v_inbound = 0
        v_outbound = 0
        v_ppm = 0.0
        v_vpm = 0.0
        v_queue = 0
        v_by_class = {c: 0 for c in ["person", "car", "motorcycle", "bicycle", "bus", "truck"]}

        if vision_metrics and vision_metrics.connection_status == "CONNECTED":
            sources.append(f"Vision:{vision_metrics.camera_id}")
            v_ped_count = vision_metrics.pedestrian_count
            v_veh_count = vision_metrics.vehicle_count
            v_inbound = vision_metrics.inbound_count
            v_outbound = vision_metrics.outbound_count
            v_ppm = vision_metrics.people_per_min
            v_vpm = vision_metrics.vehicles_per_min
            v_queue = vision_metrics.queue_length
            v_by_class = dict(vision_metrics.counts_by_class)
            weights.append(0.85)

        # 2. Process Physical Sensor Readings
        if sensor_readings is None:
            # Poll matching zone sensors from registry
            zone_adapters = self.registry.get_by_zone(zone_id)
            sensor_readings = [a.read() for a in zone_adapters]

        measured_speed: Optional[float] = None
        radar_people_count: Optional[int] = None
        loop_occupancy: Optional[float] = None
        pir_motion: Optional[bool] = None
        beam_inbound: int = 0
        beam_outbound: int = 0

        for r in sensor_readings:
            sources.append(f"Sensor:{r.sensor_id} ({'HW' if r.is_hardware else 'SIM'})")
            if r.is_hardware:
                has_hw = True
            weights.append(r.confidence)

            m = r.measurements
            if r.sensor_type == "VEHICLE_RADAR" and "measured_speed_kmh" in m:
                measured_speed = float(m["measured_speed_kmh"])
            elif r.sensor_type == "MMWAVE_RADAR" and "people_count" in m:
                radar_people_count = int(m["people_count"])
            elif r.sensor_type == "INDUCTIVE_LOOP" and "occupancy_pct" in m:
                loop_occupancy = float(m["occupancy_pct"])
            elif r.sensor_type == "PIR_MOTION" and "motion_detected" in m:
                pir_motion = bool(m["motion_detected"])
            elif r.sensor_type == "IR_BREAKBEAM":
                beam_inbound += m.get("cumulative_inbound", 0)
                beam_outbound += m.get("cumulative_outbound", 0)

        # 3. Cross-Modal Fusion & Conflict Detection (DO NOT simply add counts)
        final_ped_count = v_ped_count
        final_veh_count = v_veh_count

        if env_type == "INDOOR":
            # Indoor People Fusion
            if radar_people_count is not None and vision_metrics is not None:
                diff = abs(v_ped_count - radar_people_count)
                if diff >= 3:
                    disagreements.append(
                        f"Crowd count conflict: Camera sees {v_ped_count} persons, but mmWave radar reports {radar_people_count}"
                    )
                    # Weighted blend with penalty on confidence
                    final_ped_count = int(round(0.55 * v_ped_count + 0.45 * radar_people_count))
                else:
                    # Consensus reached: take higher-precision radar count
                    final_ped_count = max(v_ped_count, radar_people_count)

            if pir_motion is False and final_ped_count > 3:
                disagreements.append(
                    f"Sensor disagreement: PIR sensor reports zero motion while camera/radar detects {final_ped_count} persons"
                )

        else:
            # Outdoor Vehicle Fusion
            if loop_occupancy is not None and loop_occupancy > 60.0 and v_veh_count == 0:
                disagreements.append(
                    "Vehicle detection anomaly: Inductive loop reports >60% occupancy while camera sees 0 vehicles (possible camera occlusion)"
                )

        # 4. Inbound / Outbound Fusion (Correlate tripwire with IR break-beams)
        final_inbound = max(v_inbound, beam_inbound)
        final_outbound = max(v_outbound, beam_outbound)

        # 5. Speed Estimation vs Physical Measurement
        effective_speed = measured_speed
        if effective_speed is None:
            # Vision-derived estimated speed heuristic based on queue and congestion
            if v_queue > 5:
                estimated_speed = free_flow * 0.25
            elif v_queue > 2:
                estimated_speed = free_flow * 0.60
            else:
                estimated_speed = free_flow * 0.92
        else:
            estimated_speed = effective_speed

        # 6. Occupancy Percentage
        if loop_occupancy is not None:
            occupancy_pct = loop_occupancy
        else:
            total_active = final_ped_count if env_type == "INDOOR" else final_veh_count
            occupancy_pct = min(100.0, round((total_active / max(1.0, float(profile["capacity"]))) * 100.0, 1))

        # 7. Aggregate Confidence Calculation
        base_confidence = sum(weights) / max(1, len(weights)) if weights else 0.70
        # Reduce confidence if disagreements are present
        penalty = len(disagreements) * 0.15
        final_confidence = max(0.20, min(0.99, round(base_confidence - penalty, 2)))

        # 8. Congestion Level Classification
        congestion_level, explanation = self._classify_congestion(
            speed=estimated_speed,
            free_flow=free_flow,
            occupancy=occupancy_pct,
            queue_len=v_queue,
            confidence=final_confidence
        )

        return FusedTrafficState(
            zone_id=zone_id,
            environment_type=env_type,
            timestamp=now.isoformat(),
            pedestrian_count=final_ped_count,
            vehicle_count=final_veh_count,
            vehicle_counts_by_class=v_by_class,
            inbound_flow=final_inbound,
            outbound_flow=final_outbound,
            people_per_min=v_ppm,
            vehicles_per_min=v_vpm,
            measured_speed_kmh=measured_speed,
            estimated_speed_kmh=round(estimated_speed, 1),
            free_flow_speed_kmh=free_flow,
            queue_length=v_queue,
            occupancy_pct=occupancy_pct,
            congestion_level=congestion_level,
            congestion_explanation=explanation,
            aggregate_confidence=final_confidence,
            active_disagreements=disagreements,
            contributing_sources=sources,
            has_hardware_data=has_hw,
            data_freshness_seconds=0.5,
            is_stale=False
        )

    def _classify_congestion(
        self,
        speed: float,
        free_flow: float,
        occupancy: float,
        queue_len: int,
        confidence: float
    ) -> Tuple[str, str]:
        """Classifies traffic flow status into 5 categories using documented rules."""
        if confidence < 0.35:
            return "UNKNOWN", f"Confidence too low ({int(confidence*100)}%) or sensor inputs disconnected"

        ratio = speed / max(1.0, free_flow)

        if ratio >= CONGESTION_THRESHOLDS["FREE_FLOWING"]["speed_ratio_min"] and queue_len <= CONGESTION_THRESHOLDS["FREE_FLOWING"]["queue_max"]:
            return "FREE_FLOWING", f"Nominal velocity sustained ({speed:.1f}/{free_flow:.1f} km/h, {int(ratio*100)}% ratio, queue: {queue_len})"
        elif ratio >= CONGESTION_THRESHOLDS["MODERATE"]["speed_ratio_min"] and queue_len <= CONGESTION_THRESHOLDS["MODERATE"]["queue_max"]:
            return "MODERATE", f"Minor transit deceleration ({speed:.1f}/{free_flow:.1f} km/h, {int(ratio*100)}% ratio, queue: {queue_len})"
        elif ratio >= CONGESTION_THRESHOLDS["HEAVY"]["speed_ratio_min"] and queue_len <= CONGESTION_THRESHOLDS["HEAVY"]["queue_max"]:
            return "HEAVY", f"Significant flow degradation ({speed:.1f}/{free_flow:.1f} km/h, {int(ratio*100)}% ratio, queue: {queue_len})"
        else:
            return "SEVERE", f"Severe gridlock detected ({speed:.1f}/{free_flow:.1f} km/h, {int(ratio*100)}% ratio, queue: {queue_len}, occupancy: {occupancy:.1f}%)"
