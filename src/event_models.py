"""
CampusAegis (A.E.G.I.S.) Event Models
Defines standard schemas, event types, and validation rules for campus emergency events.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
import time
import uuid
from pydantic import BaseModel, Field, field_validator


class EventType(str, Enum):
    FIRE_DETECTED = "FIRE_DETECTED"
    SMOKE_DETECTED = "SMOKE_DETECTED"
    CHEMICAL_HAZARD_DETECTED = "CHEMICAL_HAZARD_DETECTED"
    CORRIDOR_BLOCKED = "CORRIDOR_BLOCKED"
    STAIRCASE_BLOCKED = "STAIRCASE_BLOCKED"
    EXIT_UNAVAILABLE = "EXIT_UNAVAILABLE"
    SENSOR_OFFLINE = "SENSOR_OFFLINE"
    SENSOR_READING_STALE = "SENSOR_READING_STALE"
    SENSOR_CONFLICT = "SENSOR_CONFLICT"
    HAZARD_CLEARED = "HAZARD_CLEARED"
    MANUAL_EMERGENCY_ALERT = "MANUAL_EMERGENCY_ALERT"
    COMMUNICATION_FAILURE = "COMMUNICATION_FAILURE"


class EventSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EmergencyEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"EVT-{uuid.uuid4().hex[:8].upper()}")
    event_type: EventType
    location_id: str
    location_name: str = ""
    floor: int = 0
    timestamp: float = Field(default_factory=time.time)
    source_id: str = "SYSTEM"
    severity: EventSeverity = EventSeverity.HIGH
    sensor_value: Optional[float] = None
    sensor_unit: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    description: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if v < 0.0 or v > 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v

    def formatted_time(self) -> str:
        return time.strftime("%H:%M:%S", time.localtime(self.timestamp))

    def to_summary(self) -> str:
        return f"[{self.formatted_time()}] {self.event_type.value} @ {self.location_name or self.location_id} (Floor {self.floor}) - Severity: {self.severity.value} (Conf: {self.confidence:.0%})"
