"""
CampusAegis (A.E.G.I.S.) Event Manager
Validates, deduplicates, records, and dispatches emergency events.
Ensures idempotent processing so duplicate sensor readings do not cause redundant state churn.
"""

from typing import List, Dict, Callable, Optional, Set, Any
import time
import logging
from src.event_models import EmergencyEvent, EventType, EventSeverity

logger = logging.getLogger("CampusAegis.EventManager")


class EventManager:
    def __init__(self, deduplication_window_seconds: float = 5.0):
        self.deduplication_window_seconds = deduplication_window_seconds
        self.event_history: List[EmergencyEvent] = []
        self.subscribers: List[Callable[[EmergencyEvent], None]] = []
        self._recent_event_fingerprints: Dict[str, float] = {}
        self.rejected_events: List[Dict[str, Any]] = []

    def register_subscriber(self, callback: Callable[[EmergencyEvent], None]) -> None:
        """Register a handler callback invoked upon new valid unique event."""
        if callback not in self.subscribers:
            self.subscribers.append(callback)

    def _generate_fingerprint(self, event: EmergencyEvent) -> str:
        """
        Creates a uniqueness fingerprint based on event type, location, and severity.
        If an event with same fingerprint arrives within the deduplication window, it is considered duplicate.
        """
        return f"{event.event_type.value}:{event.location_id}:{event.severity.value}"

    def validate_and_ingest(self, event_data: Dict[str, Any]) -> Optional[EmergencyEvent]:
        """
        Validates raw payload, builds EmergencyEvent, verifies deduplication,
        records in history, and dispatches to subscribers.
        """
        try:
            event = EmergencyEvent(**event_data)
        except Exception as e:
            err_msg = f"Malformed event payload rejected: {e}. Payload: {event_data}"
            logger.warning(err_msg)
            self.rejected_events.append({
                "payload": event_data,
                "reason": str(e),
                "timestamp": time.time()
            })
            return None

        # Check for deduplication
        fp = self._generate_fingerprint(event)
        now = time.time()
        last_seen = self._recent_event_fingerprints.get(fp)

        # Allow HAZARD_CLEARED to always process, but deduplicate identical consecutive alarms
        if last_seen and (now - last_seen < self.deduplication_window_seconds) and event.event_type != EventType.HAZARD_CLEARED:
            logger.info(f"Duplicate event ignored (fingerprint {fp}) within {self.deduplication_window_seconds}s window.")
            return None

        # Update deduplication cache
        self._recent_event_fingerprints[fp] = now
        # Clean up old fingerprints
        self._cleanup_fingerprints(now)

        # Record in history
        self.event_history.append(event)
        logger.info(f"Accepted event: {event.to_summary()}")

        # Dispatch to subscribers
        for sub in self.subscribers:
            try:
                sub(event)
            except Exception as ex:
                logger.error(f"Error in event subscriber {sub}: {ex}", exc_info=True)

        return event

    def _cleanup_fingerprints(self, current_time: float):
        expired = [
            k for k, v in self._recent_event_fingerprints.items()
            if (current_time - v) > (self.deduplication_window_seconds * 3)
        ]
        for k in expired:
            del self._recent_event_fingerprints[k]

    def get_timeline(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns chronological list of recent events formatted for dashboard displays."""
        events = self.event_history[-limit:]
        return [
            {
                "id": e.event_id,
                "time": e.formatted_time(),
                "type": e.event_type.value,
                "location": e.location_name or e.location_id,
                "floor": f"Floor {e.floor}",
                "severity": e.severity.value,
                "confidence": f"{e.confidence:.0%}",
                "description": e.description or e.to_summary()
            }
            for e in reversed(events)
        ]

    def clear(self):
        self.event_history.clear()
        self._recent_event_fingerprints.clear()
        self.rejected_events.clear()
