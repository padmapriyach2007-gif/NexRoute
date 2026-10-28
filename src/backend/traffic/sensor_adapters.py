"""
Pathfinder Physical Sensor Integration & Modular Sensor Adapters
Defines standard hardware and simulated sensor adapters for:
- PIR Motion Sensors (Indoor motion presence)
- IR Break-Beam Sensors (Doorway crossing)
- mmWave Radar Sensors (Indoor people-counting & velocity)
- Vehicle Radar Sensors (Outdoor vehicle speed & direction)
- Inductive-Loop Vehicle Detectors (Roadway occupancy & axle count)
- MQTT/Network Gateway interface for physical microcontrollers
"""

import time
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class SensorReading:
    """Standardized normalized sensor reading payload."""
    sensor_id: str
    sensor_type: str
    zone_id: str
    environment_type: str  # "INDOOR" or "OUTDOOR"
    timestamp: str
    is_hardware: bool       # False = Simulated, True = Physical Hardware
    connection_status: str  # "ONLINE", "DEGRADED", "OFFLINE"
    confidence: float       # 0.0 to 1.0
    measurements: Dict[str, Any]
    supported_measurements: List[str]
    raw_payload: Optional[Dict[str, Any]] = None


class BaseSensorAdapter(ABC):
    """Abstract base class for all physical and simulated sensor adapters."""

    def __init__(
        self,
        sensor_id: str,
        sensor_type: str,
        zone_id: str,
        environment_type: str,
        is_hardware: bool = False,
        supported_measurements: Optional[List[str]] = None
    ):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.zone_id = zone_id
        self.environment_type = environment_type.upper()
        self.is_hardware = is_hardware
        self.supported_measurements = supported_measurements or []
        self.connection_status = "ONLINE"
        self.confidence = 0.95 if is_hardware else 0.88
        self.last_reading: Optional[SensorReading] = None
        self._stale_threshold_seconds: float = 30.0

    @abstractmethod
    def read(self) -> SensorReading:
        """Fetches the latest reading from hardware or simulation generator."""
        pass

    def ingest_event(self, raw_data: Dict[str, Any]) -> SensorReading:
        """Parses an incoming hardware packet (MQTT, Serial, REST webhook)."""
        reading = self._parse_hardware_payload(raw_data)
        self.last_reading = reading
        return reading

    def is_stale(self) -> bool:
        """Checks if sensor data is older than the staleness threshold."""
        if not self.last_reading:
            return True
        try:
            ts = datetime.fromisoformat(self.last_reading.timestamp.replace("Z", "+00:00"))
            age = (datetime.now(timezone.utc) - ts).total_seconds()
            return age > self._stale_threshold_seconds
        except Exception:
            return False

    def _parse_hardware_payload(self, raw_data: Dict[str, Any]) -> SensorReading:
        """Default parser for incoming network/serial frames."""
        now_iso = datetime.now(timezone.utc).isoformat()
        measurements = raw_data.get("measurements", raw_data)
        return SensorReading(
            sensor_id=self.sensor_id,
            sensor_type=self.sensor_type,
            zone_id=self.zone_id,
            environment_type=self.environment_type,
            timestamp=raw_data.get("timestamp", now_iso),
            is_hardware=True,
            connection_status=raw_data.get("status", "ONLINE"),
            confidence=float(raw_data.get("confidence", 0.95)),
            measurements=measurements,
            supported_measurements=self.supported_measurements,
            raw_payload=raw_data
        )


# =========================================================================
# 1. PIR MOTION SENSOR ADAPTER (INDOOR)
# =========================================================================
class PIRMotionSensorAdapter(BaseSensorAdapter):
    """
    Passive Infrared (PIR) Sensor Adapter for basic indoor movement detection.
    IMPORTANT: Never reported as a people counter or speed detector.
    """

    def __init__(self, sensor_id: str, zone_id: str, is_hardware: bool = False):
        super().__init__(
            sensor_id=sensor_id,
            sensor_type="PIR_MOTION",
            zone_id=zone_id,
            environment_type="INDOOR",
            is_hardware=is_hardware,
            supported_measurements=["motion_detected", "pulse_intensity", "zone_active"]
        )

    def read(self) -> SensorReading:
        now_iso = datetime.now(timezone.utc).isoformat()
        motion = random.random() < 0.70
        reading = SensorReading(
            sensor_id=self.sensor_id,
            sensor_type=self.sensor_type,
            zone_id=self.zone_id,
            environment_type=self.environment_type,
            timestamp=now_iso,
            is_hardware=self.is_hardware,
            connection_status=self.connection_status,
            confidence=0.85,
            measurements={
                "motion_detected": motion,
                "pulse_intensity": round(random.uniform(0.65, 0.98), 2) if motion else 0.0,
                "zone_active": motion,
                "measurement_note": "Binary presence indicator only (non-counting sensor)"
            },
            supported_measurements=self.supported_measurements
        )
        self.last_reading = reading
        return reading


# =========================================================================
# 2. IR BREAK-BEAM SENSOR ADAPTER (INDOOR / DOORWAYS)
# =========================================================================
class IRBreakBeamSensorAdapter(BaseSensorAdapter):
    """
    Infrared Break-Beam Sensor Adapter for doorway & corridor crossing detection.
    Supports directional entry/exit pulse measurement.
    """

    def __init__(self, sensor_id: str, zone_id: str, is_hardware: bool = False):
        super().__init__(
            sensor_id=sensor_id,
            sensor_type="IR_BREAKBEAM",
            zone_id=zone_id,
            environment_type="INDOOR",
            is_hardware=is_hardware,
            supported_measurements=["beam_interrupted", "crossing_direction", "break_duration_ms", "crossing_pulse"]
        )
        self._cumulative_inbound: int = 0
        self._cumulative_outbound: int = 0

    def read(self) -> SensorReading:
        now_iso = datetime.now(timezone.utc).isoformat()
        is_break = random.random() < 0.35
        direction = random.choice(["INBOUND", "OUTBOUND"]) if is_break else None
        if is_break:
            if direction == "INBOUND":
                self._cumulative_inbound += 1
            else:
                self._cumulative_outbound += 1

        reading = SensorReading(
            sensor_id=self.sensor_id,
            sensor_type=self.sensor_type,
            zone_id=self.zone_id,
            environment_type=self.environment_type,
            timestamp=now_iso,
            is_hardware=self.is_hardware,
            connection_status=self.connection_status,
            confidence=0.92,
            measurements={
                "beam_interrupted": is_break,
                "crossing_direction": direction,
                "break_duration_ms": random.randint(180, 420) if is_break else 0,
                "cumulative_inbound": self._cumulative_inbound,
                "cumulative_outbound": self._cumulative_outbound
            },
            supported_measurements=self.supported_measurements
        )
        self.last_reading = reading
        return reading


# =========================================================================
# 3. mmWAVE RADAR SENSOR ADAPTER (INDOOR / CROWD)
# =========================================================================
class MMWaveRadarSensorAdapter(BaseSensorAdapter):
    """
    60GHz/77GHz mmWave Micro-Radar for indoor people counting, tracking, and micro-velocity.
    """

    def __init__(self, sensor_id: str, zone_id: str, is_hardware: bool = False):
        super().__init__(
            sensor_id=sensor_id,
            sensor_type="MMWAVE_RADAR",
            zone_id=zone_id,
            environment_type="INDOOR",
            is_hardware=is_hardware,
            supported_measurements=["people_count", "radial_distance_m", "micro_velocity_mps", "crowd_density_level"]
        )

    def read(self) -> SensorReading:
        now_iso = datetime.now(timezone.utc).isoformat()
        count = random.randint(2, 8)
        reading = SensorReading(
            sensor_id=self.sensor_id,
            sensor_type=self.sensor_type,
            zone_id=self.zone_id,
            environment_type=self.environment_type,
            timestamp=now_iso,
            is_hardware=self.is_hardware,
            connection_status=self.connection_status,
            confidence=0.94,
            measurements={
                "people_count": count,
                "radial_distance_m": round(random.uniform(1.2, 5.8), 2),
                "micro_velocity_mps": round(random.uniform(0.6, 1.4), 2),
                "crowd_density_level": "LOW" if count < 4 else ("MODERATE" if count < 7 else "HIGH")
            },
            supported_measurements=self.supported_measurements
        )
        self.last_reading = reading
        return reading


# =========================================================================
# 4. VEHICLE RADAR SENSOR ADAPTER (OUTDOOR / HIGHWAY)
# =========================================================================
class VehicleRadarSensorAdapter(BaseSensorAdapter):
    """
    24GHz/77GHz Doppler Vehicle Speed Radar for road corridors and intersections.
    Provides verified physical speed and directional approach vectors.
    """

    def __init__(self, sensor_id: str, zone_id: str, nominal_speed_kmh: float = 80.0, is_hardware: bool = False):
        super().__init__(
            sensor_id=sensor_id,
            sensor_type="VEHICLE_RADAR",
            zone_id=zone_id,
            environment_type="OUTDOOR",
            is_hardware=is_hardware,
            supported_measurements=["measured_speed_kmh", "approach_direction", "target_range_m", "doppler_confidence"]
        )
        self.nominal_speed_kmh = nominal_speed_kmh

    def read(self) -> SensorReading:
        now_iso = datetime.now(timezone.utc).isoformat()
        speed = max(15.0, round(random.gauss(self.nominal_speed_kmh, 12.0), 1))
        reading = SensorReading(
            sensor_id=self.sensor_id,
            sensor_type=self.sensor_type,
            zone_id=self.zone_id,
            environment_type=self.environment_type,
            timestamp=now_iso,
            is_hardware=self.is_hardware,
            connection_status=self.connection_status,
            confidence=0.96,
            measurements={
                "measured_speed_kmh": speed,
                "approach_direction": random.choice(["APPROACHING", "RECEDING"]),
                "target_range_m": round(random.uniform(12.0, 85.0), 1),
                "doppler_confidence": round(random.uniform(0.91, 0.99), 2)
            },
            supported_measurements=self.supported_measurements
        )
        self.last_reading = reading
        return reading


# =========================================================================
# 5. INDUCTIVE-LOOP DETECTOR ADAPTER (OUTDOOR / INTERSECTION)
# =========================================================================
class InductiveLoopAdapter(BaseSensorAdapter):
    """
    In-pavement electromagnetic inductive loop detector for roadway occupancy & queue monitoring.
    """

    def __init__(self, sensor_id: str, zone_id: str, is_hardware: bool = False):
        super().__init__(
            sensor_id=sensor_id,
            sensor_type="INDUCTIVE_LOOP",
            zone_id=zone_id,
            environment_type="OUTDOOR",
            is_hardware=is_hardware,
            supported_measurements=["occupancy_pct", "vehicle_present", "vehicle_rate_vpm"]
        )

    def read(self) -> SensorReading:
        now_iso = datetime.now(timezone.utc).isoformat()
        occ = round(random.uniform(12.0, 48.0), 1)
        reading = SensorReading(
            sensor_id=self.sensor_id,
            sensor_type=self.sensor_type,
            zone_id=self.zone_id,
            environment_type=self.environment_type,
            timestamp=now_iso,
            is_hardware=self.is_hardware,
            connection_status=self.connection_status,
            confidence=0.93,
            measurements={
                "occupancy_pct": occ,
                "vehicle_present": occ > 18.0,
                "vehicle_rate_vpm": round(occ * 0.45, 1)
            },
            supported_measurements=self.supported_measurements
        )
        self.last_reading = reading
        return reading


# =========================================================================
# MODULAR SENSOR REGISTRY & SIMULATION CONTROLLER
# =========================================================================
class SensorRegistry:
    """Central registry and manager for all hardware and simulated sensors."""

    def __init__(self):
        self.sensors: Dict[str, BaseSensorAdapter] = {}
        self._init_default_fleet()

    def _init_default_fleet(self):
        """Initializes default fleet of sensors covering both indoor and outdoor zones."""
        # Indoor Corridor & Entrance Fleet
        self.register(PIRMotionSensorAdapter("PIR_ENTRANCE_NORTH", "ZONE_ENTRANCE_NORTH", is_hardware=False))
        self.register(IRBreakBeamSensorAdapter("IR_DOOR_CONCOURSE", "ZONE_ENTRANCE_NORTH", is_hardware=False))
        self.register(MMWaveRadarSensorAdapter("RADAR_MMWAVE_ATRIUM", "ZONE_MALL_ATRIUM", is_hardware=False))

        # Outdoor Arterial & Highway Fleet
        self.register(VehicleRadarSensorAdapter("RADAR_EXPRESSWAY_01", "SEG_EXPRESSWAY_01", nominal_speed_kmh=88.0, is_hardware=False))
        self.register(InductiveLoopAdapter("LOOP_BYPASS_INTERSECT", "SEG_GUNTUR_BYPASS", is_hardware=False))
        self.register(VehicleRadarSensorAdapter("RADAR_TENALI_HWY", "SEG_TENALI_HIGHWAY", nominal_speed_kmh=52.0, is_hardware=False))

    def register(self, adapter: BaseSensorAdapter):
        """Registers a sensor adapter."""
        self.sensors[adapter.sensor_id] = adapter

    def get(self, sensor_id: str) -> Optional[BaseSensorAdapter]:
        """Retrieves a sensor by ID."""
        return self.sensors.get(sensor_id)

    def get_by_zone(self, zone_id: str) -> List[BaseSensorAdapter]:
        """Retrieves all sensors monitoring a specific zone."""
        return [s for s in self.sensors.values() if s.zone_id == zone_id]

    def poll_all(self) -> Dict[str, SensorReading]:
        """Polls readings from all registered sensors."""
        readings = {}
        for s_id, s in self.sensors.items():
            try:
                readings[s_id] = s.read()
            except Exception as e:
                pass
        return readings

    def inject_event(self, sensor_id: str, raw_payload: Dict[str, Any]) -> Optional[SensorReading]:
        """Manually injects or simulates a sensor event for interactive testing."""
        s = self.get(sensor_id)
        if s:
            return s.ingest_event(raw_payload)
        return None
