"""
CampusAegis (A.E.G.I.S.) Communication Adapters
Simulates multi-channel emergency communication adapters for institutional dissemination:
  1. Dashboard Alert Adapter
  2. Simulated Public-Address (PA) Announcement Adapter
  3. Visual Signage Display Adapter
  4. Simulated Mobile Notification Adapter

Prototype Boundary & Safety Notice:
All adapters in this prototype are SIMULATED and log delivery records in memory.
No physical hardware, physical campus loudspeakers, GSM SMS gateways, or municipal alarms are activated.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
import time
import uuid


class DeliveryStatus(str, Enum):
    GENERATED = "GENERATED"
    QUEUED = "QUEUED"
    SIMULATED = "SIMULATED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    FAILED = "FAILED"


class OutboundMessage:
    def __init__(
        self,
        channel: str,
        target_zone: str,
        floor: int,
        headline: str,
        body: str,
        severity: str,
        delivery_status: DeliveryStatus = DeliveryStatus.GENERATED,
        is_simulated: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.message_id = f"MSG-{uuid.uuid4().hex[:8].upper()}"
        self.channel = channel
        self.target_zone = target_zone
        self.floor = floor
        self.headline = headline
        self.body = body
        self.severity = severity
        self.delivery_status = delivery_status
        self.is_simulated = is_simulated
        self.timestamp = time.time()
        self.failure_reason: Optional[str] = None
        self.metadata = metadata or {}

    def formatted_time(self) -> str:
        return time.strftime("%H:%M:%S", time.localtime(self.timestamp))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.message_id,
            "time": self.formatted_time(),
            "channel": self.channel,
            "target_zone": self.target_zone,
            "floor": f"Floor {self.floor}",
            "headline": self.headline,
            "body": self.body,
            "severity": self.severity,
            "status": self.delivery_status.value,
            "simulated": self.is_simulated,
            "failure_reason": self.failure_reason
        }


class BaseCommunicationAdapter:
    def __init__(self, channel_name: str):
        self.channel_name = channel_name
        self.is_online = True
        self.outbox_history: List[OutboundMessage] = []

    def transmit(self, target_zone: str, floor: int, headline: str, body: str, severity: str) -> OutboundMessage:
        msg = OutboundMessage(
            channel=self.channel_name,
            target_zone=target_zone,
            floor=floor,
            headline=headline,
            body=body,
            severity=severity,
            delivery_status=DeliveryStatus.QUEUED,
            is_simulated=True
        )

        if not self.is_online:
            msg.delivery_status = DeliveryStatus.FAILED
            msg.failure_reason = f"Channel {self.channel_name} communication link offline."
        else:
            # Successfully simulated
            msg.delivery_status = DeliveryStatus.SIMULATED

        self.outbox_history.append(msg)
        return msg


class DashboardAlertAdapter(BaseCommunicationAdapter):
    def __init__(self):
        super().__init__("DASHBOARD_LIVE_FEED")


class SimulatedPublicAddressAdapter(BaseCommunicationAdapter):
    def __init__(self):
        super().__init__("SIMULATED_PUBLIC_ADDRESS")


class VisualSignageAdapter(BaseCommunicationAdapter):
    def __init__(self):
        super().__init__("VISUAL_DIGITAL_SIGNAGE")


class SimulatedMobileNotificationAdapter(BaseCommunicationAdapter):
    def __init__(self):
        super().__init__("SIMULATED_MOBILE_PUSH")


class MultiChannelDispatcher:
    """Coordinates transmission across all defined communication adapters."""
    def __init__(self):
        self.dashboard_adapter = DashboardAlertAdapter()
        self.pa_adapter = SimulatedPublicAddressAdapter()
        self.signage_adapter = VisualSignageAdapter()
        self.mobile_adapter = SimulatedMobileNotificationAdapter()

    def broadcast(
        self,
        target_zone: str,
        floor: int,
        headline: str,
        body: str,
        severity: str,
        channels: Optional[List[str]] = None
    ) -> List[OutboundMessage]:
        results = []
        # Broadcast to all simulated channels
        results.append(self.dashboard_adapter.transmit(target_zone, floor, headline, body, severity))
        results.append(self.pa_adapter.transmit(target_zone, floor, headline, body, severity))
        results.append(self.signage_adapter.transmit(target_zone, floor, headline, body, severity))
        results.append(self.mobile_adapter.transmit(target_zone, floor, headline, body, severity))
        return results

    @property
    def push_adapter(self) -> BaseCommunicationAdapter:
        return self.mobile_adapter

    def simulate_channel_outage(self, channel: str, is_down: bool = True):
        """Toggles individual channel online status for fault-tolerance simulations."""
        ch = channel.lower()
        if "pa" in ch:
            self.pa_adapter.is_online = not is_down
        elif "sign" in ch:
            self.signage_adapter.is_online = not is_down
        elif "mob" in ch or "push" in ch:
            self.mobile_adapter.is_online = not is_down
        elif "dash" in ch:
            self.dashboard_adapter.is_online = not is_down

    def simulate_communication_failure(self):
        """Simulates network bus crash affecting outbound channels."""
        self.pa_adapter.is_online = False
        self.signage_adapter.is_online = False
        self.mobile_adapter.is_online = False

    def restore_communication(self):
        self.pa_adapter.is_online = True
        self.signage_adapter.is_online = True
        self.mobile_adapter.is_online = True

    def get_all_dispatched(self, limit: int = 50) -> List[Dict[str, Any]]:
        combined = (
            self.dashboard_adapter.outbox_history +
            self.pa_adapter.outbox_history +
            self.signage_adapter.outbox_history +
            self.mobile_adapter.outbox_history
        )
        combined.sort(key=lambda m: m.timestamp, reverse=True)
        return [m.to_dict() for m in combined[:limit]]

    def clear(self):
        self.dashboard_adapter.outbox_history.clear()
        self.pa_adapter.outbox_history.clear()
        self.signage_adapter.outbox_history.clear()
        self.mobile_adapter.outbox_history.clear()
        self.restore_communication()
