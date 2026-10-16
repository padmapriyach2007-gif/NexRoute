"""
CampusAegis (A.E.G.I.S.) Human-In-The-Loop (HITL) Operator Manager
Manages control-room operator actions, incident acknowledgments, manual overrides with justifications,
and audit trails for compliance with safety standards (e.g. NFPA 101, Life Safety Codes).

Important Prototype Distinction:
All approvals and overrides are strictly software simulation state updates and decision-support records.
No physical equipment, mechanical actuators, or real building infrastructure are manipulated.
"""

from typing import List, Dict, Optional, Any
import time


class OperatorActionRecord:
    def __init__(
        self,
        action_type: str,  # 'ACKNOWLEDGE', 'OVERRIDE_ROUTE', 'ESCALATE_DISPATCH', 'MANUAL_HAZARD', 'RESET'
        operator_name: str,
        target_entity: str,
        justification: str,
        timestamp: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.action_type = action_type
        self.operator_name = operator_name
        self.target_entity = target_entity
        self.justification = justification
        self.timestamp = timestamp or time.time()
        self.metadata = metadata or {}

    def formatted_time(self) -> str:
        return time.strftime("%H:%M:%S", time.localtime(self.timestamp))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time": self.formatted_time(),
            "operator": self.operator_name,
            "action": self.action_type,
            "target": self.target_entity,
            "reason": self.justification,
            "details": self.metadata
        }


class OperatorManager:
    def __init__(self):
        self.action_log: List[OperatorActionRecord] = []
        self.acknowledged_incidents: Dict[str, OperatorActionRecord] = {}
        self.manual_overrides: Dict[str, OperatorActionRecord] = {}
        self.escalations: List[OperatorActionRecord] = []

    def record_acknowledgment(self, incident_id: str, operator_name: str = "Safety Officer") -> OperatorActionRecord:
        record = OperatorActionRecord(
            action_type="ACKNOWLEDGE",
            operator_name=operator_name,
            target_entity=incident_id,
            justification="Incident reviewed and acknowledged on command console."
        )
        self.acknowledged_incidents[incident_id] = record
        self.action_log.append(record)
        return record

    def record_override(
        self,
        route_or_zone_id: str,
        override_action: str,
        reason: str,
        operator_name: str = "Safety Officer"
    ) -> OperatorActionRecord:
        record = OperatorActionRecord(
            action_type=f"OVERRIDE: {override_action}",
            operator_name=operator_name,
            target_entity=route_or_zone_id,
            justification=reason,
            metadata={"override_action": override_action}
        )
        self.manual_overrides[route_or_zone_id] = record
        self.action_log.append(record)
        return record

    def record_escalation(
        self,
        zone_id: str,
        reason: str,
        operator_name: str = "Safety Officer"
    ) -> OperatorActionRecord:
        record = OperatorActionRecord(
            action_type="ESCALATE_TO_EMERGENCY_SERVICES",
            operator_name=operator_name,
            target_entity=zone_id,
            justification=reason
        )
        self.escalations.append(record)
        self.action_log.append(record)
        return record

    def get_audit_trail(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in reversed(self.action_log[-limit:])]

    def reset(self):
        self.action_log.clear()
        self.acknowledged_incidents.clear()
        self.manual_overrides.clear()
        self.escalations.clear()
