"""
CampusAegis (A.E.G.I.S.) Sensor Simulator
Simulates IoT telemetry sensors: optical smoke detectors, thermal heat sensors,
chemical vapor monitors, door contact sensors, and network heartbeat pings.
Allows injecting normal readings, critical alarms, stale data, contradictory sensor readings, and offline sensors.
"""

from typing import Dict, List, Optional, Any
import time
import random
from src.event_models import EmergencyEvent, EventType, EventSeverity
from src.event_manager import EventManager


class SensorDevice:
    def __init__(self, sensor_id: str, sensor_type: str, location_id: str, floor: int, location_name: str = ""):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type  # 'SMOKE', 'HEAT', 'CHEM_VOC', 'DOOR', 'CAMERA'
        self.location_id = location_id
        self.floor = floor
        self.location_name = location_name
        self.is_online = True
        self.last_reading_time = time.time()
        self.last_value = 0.0
        self.health_status = "HEALTHY"  # 'HEALTHY', 'STALE', 'CONFLICT', 'OFFLINE'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "type": self.sensor_type,
            "location_id": self.location_id,
            "location_name": self.location_name,
            "floor": self.floor,
            "online": self.is_online,
            "health": self.health_status,
            "last_value": self.last_value,
            "last_seen_sec_ago": round(time.time() - self.last_reading_time, 1)
        }


class SensorSimulator:
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.sensors: Dict[str, SensorDevice] = {}
        self._initialize_default_sensors()

    def _initialize_default_sensors(self):
        """Sets up key sensor coverage across high-risk campus zones and stairwells."""
        default_configs = [
            # Chemical Block Floor 2
            ("SNS-SMK-CHEM-F2", "SMOKE", "CHEM_STAIR_A_F2", 2, "Chem Block Stairwell A (North)"),
            ("SNS-SMK-CHEM-F2B", "SMOKE", "CHEM_STAIR_B_F2", 2, "Chem Block Stairwell B (South)"),
            ("SNS-VOC-CHEM-201", "CHEM_VOC", "VIG_ENGI_CHEMICAL_REACTION_ENG", 2, "Chemical Reaction Engg Lab"),
            ("SNS-HEAT-CHEM-202", "HEAT", "VIG_ENGI_PROCESS_DYNAMICS_CONTROL", 1, "Process Dynamics Lab"),
            
            # CSE & Library Floor 1
            ("SNS-SMK-CSE-F1", "SMOKE", "CSE_STAIR_F1", 1, "CSE Department Stairwell"),
            ("SNS-HEAT-CSE-NET", "HEAT", "VIG_ENGI_ADVANCED_NETWORKING_LAB", 1, "Advanced Networking Lab"),
            ("SNS-SMK-LIB-F1", "SMOKE", "VIG_LIBR_DIGITAL_LIBRARY_SECTION", 1, "Digital Library Section"),

            # Ground Floor Arterials & Central Quad
            ("SNS-SMK-QUAD-F0", "SMOKE", "HUB_CENTRAL_PLAZA", 0, "Central Quadrangle Plaza"),
            ("SNS-HEAT-EEE-F0", "HEAT", "VIG_ENGI_POWER_SYSTEMS_SIMULATION", 0, "Power Systems Lab"),
            ("SNS-DOOR-ASSEMBLY", "DOOR", "VIG_FACI_PLAY_GROUNDS", 0, "Play Grounds Main Assembly Gate")
        ]

        for sid, stype, loc_id, fl, name in default_configs:
            self.sensors[sid] = SensorDevice(sid, stype, loc_id, fl, name)

    def trigger_smoke_detection(self, sensor_id: str, obscuration_pct: float = 85.0) -> Optional[EmergencyEvent]:
        sensor = self.sensors.get(sensor_id)
        if not sensor:
            return None
        sensor.last_reading_time = time.time()
        sensor.last_value = obscuration_pct
        sensor.health_status = "ALARM"

        event_data = {
            "event_type": EventType.SMOKE_DETECTED,
            "location_id": sensor.location_id,
            "location_name": sensor.location_name,
            "floor": sensor.floor,
            "source_id": sensor.sensor_id,
            "severity": EventSeverity.CRITICAL if obscuration_pct > 70 else EventSeverity.HIGH,
            "sensor_value": obscuration_pct,
            "sensor_unit": "% obscuration/m",
            "confidence": 0.95,
            "description": f"Optical obscuration threshold exceeded ({obscuration_pct}%) at {sensor.location_name}."
        }
        return self.event_manager.validate_and_ingest(event_data)

    def trigger_chemical_spill(self, location_id: str, location_name: str, floor: int, ppm: float = 340.0) -> Optional[EmergencyEvent]:
        event_data = {
            "event_type": EventType.CHEMICAL_HAZARD_DETECTED,
            "location_id": location_id,
            "location_name": location_name,
            "floor": floor,
            "source_id": "SNS-VOC-CHEM-201",
            "severity": EventSeverity.CRITICAL,
            "sensor_value": ppm,
            "sensor_unit": "ppm",
            "confidence": 0.98,
            "description": f"Toxic airborne volatile chemical fumes detected ({ppm} ppm) exceeding OSHA IDLH thresholds."
        }
        return self.event_manager.validate_and_ingest(event_data)

    def trigger_staircase_blocked(self, location_id: str, location_name: str, floor: int, reason: str = "Dense Smoke Infiltration") -> Optional[EmergencyEvent]:
        event_data = {
            "event_type": EventType.STAIRCASE_BLOCKED,
            "location_id": location_id,
            "location_name": location_name,
            "floor": floor,
            "source_id": "STAIR_OPTICAL_GRID",
            "severity": EventSeverity.CRITICAL,
            "confidence": 0.99,
            "description": f"{location_name} marked non-traversable due to: {reason}."
        }
        return self.event_manager.validate_and_ingest(event_data)

    def trigger_corridor_blocked(self, location_id: str, location_name: str, floor: int, reason: str = "Ceiling Structural Collapse") -> Optional[EmergencyEvent]:
        event_data = {
            "event_type": EventType.CORRIDOR_BLOCKED,
            "location_id": location_id,
            "location_name": location_name,
            "floor": floor,
            "source_id": "STRUCTURAL_MONITOR",
            "severity": EventSeverity.HIGH,
            "confidence": 0.95,
            "description": f"Passage through {location_name} blocked by {reason}."
        }
        return self.event_manager.validate_and_ingest(event_data)

    def trigger_sensor_conflict(self, location_id: str, location_name: str, floor: int) -> Optional[EmergencyEvent]:
        """
        Simulates two sensors at same location contradicting each other:
        Sensor A says smoke alarm (100%), Sensor B says completely clean (0%).
        """
        event_data = {
            "event_type": EventType.SENSOR_CONFLICT,
            "location_id": location_id,
            "location_name": location_name,
            "floor": floor,
            "source_id": "TELEMETRY_CROSS_CHECK",
            "severity": EventSeverity.MEDIUM,
            "confidence": 0.40,
            "description": f"Contradictory telemetry at {location_name}: Smoke Detector reports 88% obscuration, but Thermal & Secondary Optical report ambient normal. Area status UNCERTAIN."
        }
        return self.event_manager.validate_and_ingest(event_data)

    def trigger_stale_reading(self, location_id: str, location_name: str, floor: int, stale_seconds: float = 300.0) -> Optional[EmergencyEvent]:
        """Simulates sensor whose heartbeat has not updated for > 5 minutes."""
        past_time = time.time() - stale_seconds
        event_data = {
            "event_type": EventType.SENSOR_READING_STALE,
            "location_id": location_id,
            "location_name": location_name,
            "floor": floor,
            "source_id": "HEARTBEAT_SUPERVISOR",
            "timestamp": past_time,
            "severity": EventSeverity.MEDIUM,
            "confidence": 0.30,
            "description": f"Sensor telemetry at {location_name} is stale ({int(stale_seconds)}s overdue). Area cannot be certified safe."
        }
        return self.event_manager.validate_and_ingest(event_data)

    def trigger_sensor_offline(self, sensor_id: str) -> Optional[EmergencyEvent]:
        sensor = self.sensors.get(sensor_id)
        if not sensor:
            return None
        sensor.is_online = False
        sensor.health_status = "OFFLINE"

        event_data = {
            "event_type": EventType.SENSOR_OFFLINE,
            "location_id": sensor.location_id,
            "location_name": sensor.location_name,
            "floor": sensor.floor,
            "source_id": sensor.sensor_id,
            "severity": EventSeverity.MEDIUM,
            "confidence": 0.0,
            "description": f"Telemetry loss: Sensor {sensor.sensor_id} ({sensor.location_name}) is OFFLINE. Presuming unverified hazard."
        }
        return self.event_manager.validate_and_ingest(event_data)

    def trigger_communication_failure(self, campus_wing: str = "Dept of Chemical Engineering") -> Optional[EmergencyEvent]:
        event_data = {
            "event_type": EventType.COMMUNICATION_FAILURE,
            "location_id": "COMM_BUS_NORTH",
            "location_name": f"{campus_wing} Substation Comms Bus",
            "floor": 0,
            "source_id": "NETWORK_SUPERVISOR",
            "severity": EventSeverity.HIGH,
            "confidence": 0.20,
            "description": f"Communication bus failure in {campus_wing}. Telemetry severed. Autonomous fallback rules engaged."
        }
        return self.event_manager.validate_and_ingest(event_data)

    def trigger_hazard_cleared(self, location_id: str, location_name: str, floor: int) -> Optional[EmergencyEvent]:
        event_data = {
            "event_type": EventType.HAZARD_CLEARED,
            "location_id": location_id,
            "location_name": location_name,
            "floor": floor,
            "source_id": "SAFETY_INSPECTOR_MANUAL",
            "severity": EventSeverity.INFO,
            "confidence": 1.0,
            "description": f"Physical safety inspection confirmed {location_name} hazard cleared and corridor re-opened."
        }
        return self.event_manager.validate_and_ingest(event_data)
