"""
CampusAegis (A.E.G.I.S.) Safety Monitor & Uncertainty Engine
Evaluates telemetry freshness, tracks sensor health, detects conflicting reports,
computes zone uncertainty scores, and triggers graceful degradation with fail-safe fallbacks.

Guiding Life-Safety Principle:
Absence of data or silence from a sensor MUST NEVER be interpreted as evidence that an area is safe.
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Any, Tuple
import time
from src.event_models import EmergencyEvent, EventType, EventSeverity


class SystemSafetyState(str, Enum):
    NORMAL = "NORMAL"
    ALERT_ACTIVE = "ALERT_ACTIVE"
    ROUTE_RECALCULATION = "ROUTE_RECALCULATION"
    ROUTE_VERIFIED_BY_MODEL = "ROUTE_VERIFIED_BY_MODEL"
    NO_VERIFIED_ROUTE = "NO_VERIFIED_ROUTE"
    SENSOR_UNCERTAIN = "SENSOR_UNCERTAIN"
    COMMUNICATION_DEGRADED = "COMMUNICATION_DEGRADED"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    INCIDENT_RESOLVED = "INCIDENT_RESOLVED"


class ZoneSafetyState:
    def __init__(self, location_id: str, location_name: str, floor: int):
        self.location_id = location_id
        self.location_name = location_name
        self.floor = floor
        self.is_hazard_confirmed = False
        self.is_blocked = False
        self.is_uncertain = False
        self.is_stale = False
        self.is_conflicted = False
        self.active_hazard_type: Optional[str] = None
        self.active_severity: EventSeverity = EventSeverity.INFO
        self.confidence_score: float = 1.0  # 1.0 = verified certain, < 0.5 = uncertain
        self.last_updated: float = time.time()
        self.evidence_log: List[str] = []
        self.uncertainty_reasons: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "location_id": self.location_id,
            "name": self.location_name,
            "floor": self.floor,
            "confirmed_hazard": self.is_hazard_confirmed,
            "blocked": self.is_blocked,
            "uncertain": self.is_uncertain,
            "stale": self.is_stale,
            "conflicted": self.is_conflicted,
            "hazard_type": self.active_hazard_type or "None",
            "severity": self.active_severity.value,
            "confidence": f"{self.confidence_score:.0%}",
            "age_seconds": round(time.time() - self.last_updated, 1),
            "reasons": self.uncertainty_reasons
        }


class SafetyMonitor:
    def __init__(self, stale_threshold_seconds: float = 120.0):
        self.stale_threshold_seconds = stale_threshold_seconds
        self.zone_states: Dict[str, ZoneSafetyState] = {}
        self.active_warnings: List[Dict[str, Any]] = []
        self.network_connected = True
        self.fallback_mode_active = False

    def get_or_create_zone(self, location_id: str, location_name: str = "", floor: int = 0) -> ZoneSafetyState:
        if location_id not in self.zone_states:
            self.zone_states[location_id] = ZoneSafetyState(location_id, location_name, floor)
        return self.zone_states[location_id]

    def process_event(self, event: EmergencyEvent) -> Dict[str, Any]:
        """
        Ingests emergency event, updates zone safety states, evaluates uncertainty,
        and generates warnings if conditions degrade.
        """
        zone = self.get_or_create_zone(event.location_id, event.location_name, event.floor)
        zone.last_updated = time.time()
        now = time.time()

        evidence_str = f"[{event.formatted_time()}] {event.event_type.value}: {event.description or 'Event logged'} (Conf: {event.confidence:.0%})"
        zone.evidence_log.append(evidence_str)

        # 1. Hazard detections
        if event.event_type in (
            EventType.FIRE_DETECTED,
            EventType.SMOKE_DETECTED,
            EventType.CHEMICAL_HAZARD_DETECTED,
            EventType.CORRIDOR_BLOCKED,
            EventType.STAIRCASE_BLOCKED,
            EventType.EXIT_UNAVAILABLE,
            EventType.MANUAL_EMERGENCY_ALERT
        ):
            zone.is_hazard_confirmed = True
            zone.is_blocked = True
            zone.active_hazard_type = event.event_type.value
            zone.active_severity = event.severity
            zone.confidence_score = event.confidence
            zone.is_uncertain = False

        # 2. Sensor conflict
        elif event.event_type == EventType.SENSOR_CONFLICT:
            zone.is_conflicted = True
            zone.is_uncertain = True
            zone.confidence_score = min(zone.confidence_score, 0.40)
            reason = f"Sensors in conflict at {zone.location_name}. Contradictory readings prevent verified safety clearance."
            zone.uncertainty_reasons.append(reason)
            self._add_warning("SENSOR_CONFLICT", reason, zone.location_id)

        # 3. Stale readings
        elif event.event_type == EventType.SENSOR_READING_STALE:
            zone.is_stale = True
            zone.is_uncertain = True
            zone.confidence_score = min(zone.confidence_score, 0.35)
            reason = f"Sensor telemetry for {zone.location_name} is stale. Missing recent heartbeat."
            zone.uncertainty_reasons.append(reason)
            self._add_warning("STALE_DATA", reason, zone.location_id)

        # 4. Sensor offline
        elif event.event_type == EventType.SENSOR_OFFLINE:
            zone.is_uncertain = True
            zone.confidence_score = 0.0
            reason = f"Sensor at {zone.location_name} went OFFLINE. Cannot guarantee safe passage."
            zone.uncertainty_reasons.append(reason)
            self._add_warning("SENSOR_OFFLINE", reason, zone.location_id)

        # 5. Network / Communication failure
        elif event.event_type == EventType.COMMUNICATION_FAILURE:
            self.network_connected = False
            self.fallback_mode_active = True
            reason = f"Campus emergency communications bus failure detected. Engaging fail-safe emergency fallback protocol."
            self._add_warning("COMMUNICATION_FAILURE", reason, event.location_id)

        # 6. Hazard cleared
        elif event.event_type == EventType.HAZARD_CLEARED:
            # Physical clearance by human safety inspector
            zone.is_hazard_confirmed = False
            zone.is_blocked = False
            zone.is_uncertain = False
            zone.is_stale = False
            zone.is_conflicted = False
            zone.active_hazard_type = None
            zone.confidence_score = 1.0
            zone.uncertainty_reasons.clear()
            self._remove_warning_for_location(zone.location_id)

        return zone.to_dict()

    def check_staleness(self) -> List[str]:
        """
        Periodically checks all zones for unrefreshed telemetry exceeding the stale threshold.
        """
        now = time.time()
        stale_zones = []
        for loc_id, zone in self.zone_states.items():
            if zone.is_hazard_confirmed:
                # If a hazard was confirmed, it does not become safe merely by getting old!
                continue
            if (now - zone.last_updated) > self.stale_threshold_seconds and not zone.is_stale:
                zone.is_stale = True
                zone.is_uncertain = True
                zone.confidence_score = 0.30
                warn_msg = f"Zone {zone.location_name} ({loc_id}) has no fresh telemetry for >{int(self.stale_threshold_seconds)}s."
                zone.uncertainty_reasons.append(warn_msg)
                self._add_warning("STALE_DATA", warn_msg, loc_id)
                stale_zones.append(loc_id)
        return stale_zones

    def is_zone_verified_safe(self, location_id: str) -> Tuple[bool, str]:
        """
        Determines if a location can be verified safe.
        Returns: (is_safe, explanation)
        """
        zone = self.zone_states.get(location_id)
        if not zone:
            # Unknown location has no safety verification
            return False, f"Location '{location_id}' has no verified sensor monitoring data."

        if zone.is_blocked or zone.is_hazard_confirmed:
            return False, f"Location '{zone.location_name}' has active confirmed hazard: {zone.active_hazard_type}."

        if zone.is_conflicted:
            return False, f"Location '{zone.location_name}' has unresolved conflicting sensor readings."

        if zone.is_stale:
            return False, f"Telemetry for '{zone.location_name}' is stale; safe status cannot be confirmed."

        if zone.is_uncertain or zone.confidence_score < 0.5:
            return False, f"Confidence for '{zone.location_name}' is insufficient ({zone.confidence_score:.0%})."

        return True, f"Location '{zone.location_name}' verified clear by active sensors."

    def _add_warning(self, warn_type: str, message: str, location_id: str):
        self.active_warnings.append({
            "type": warn_type,
            "message": message,
            "location_id": location_id,
            "time": time.strftime("%H:%M:%S")
        })

    def _remove_warning_for_location(self, location_id: str):
        self.active_warnings = [w for w in self.active_warnings if w["location_id"] != location_id]

    def get_active_warnings(self) -> List[Dict[str, Any]]:
        return list(reversed(self.active_warnings))

    def reset(self):
        self.zone_states.clear()
        self.active_warnings.clear()
        self.network_connected = True
        self.fallback_mode_active = False
