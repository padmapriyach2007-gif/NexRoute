"""
CampusAegis (A.E.G.I.S.) Autonomous Alert & Guidance Engine
Produces location-specific hazard warnings, visual evacuation guidance, and simulated PA announcements.

Core Safety Principles (Section 4):
1. Hazard warnings and evacuation routing are strictly separate decisions:
   The system warns people away from a known hazard even when no verified evacuation route exists.
2. It must never invent an alternative route merely to avoid showing an error.
3. If information is insufficient, state that the route is unverified and request human safety-officer review.
4. Avoid telling people to enter an area based only on the absence of a detected hazard.
5. All transmissions in this prototype are SIMULATED and auditable.
"""

from typing import Dict, List, Optional, Any
import time
from src.route_evaluator import RouteSafetyReport
from src.campus_graph import CampusNode
from src.communication_adapters import MultiChannelDispatcher, DeliveryStatus, OutboundMessage


class AlertManager:
    def __init__(self, nodes: Dict[str, CampusNode]):
        self.nodes = nodes
        self.dispatcher = MultiChannelDispatcher()
        self.active_hazard_warnings: List[Dict[str, Any]] = []
        self.active_guidance_directives: List[Dict[str, Any]] = []
        self.alert_history: List[Dict[str, Any]] = []

    def build_corridor_fire_warning(self, zone_name: str, floor: int) -> str:
        """Section 4: Explicit Fire in Corridor Warning"""
        return (
            f"EMERGENCY WARNING: Fire reported in the corridor at {zone_name} (Floor {floor}). "
            f"Do not enter this corridor. Follow official evacuation instructions and use only a route "
            f"confirmed as available by the emergency system."
        )

    def build_uncertain_hazard_warning(self, zone_name: str, floor: int) -> str:
        """Section 4: Explicit Uncertain Hazard Warning"""
        return (
            f"SAFETY WARNING: A possible hazard has been reported in {zone_name} (Floor {floor}). "
            f"Avoid entering the affected area and follow instructions from authorized safety personnel. "
            f"The safe route has not yet been verified."
        )

    def build_blocked_route_warning(self, previous_route_name: str, zone_name: str) -> str:
        """Section 4: Explicit Blocked Route Update Warning"""
        return (
            f"ROUTE UPDATE: The previously suggested route via {previous_route_name} is no longer available. "
            f"Stop following the outdated route guidance and wait for updated instructions or follow the "
            f"campus's approved emergency procedure."
        )

    def build_communication_failure_warning(self) -> str:
        """Section 4: Explicit Communication Failure Warning"""
        return (
            "COMMUNICATION WARNING: Automatic guidance delivery could not be confirmed due to a network communication failure. "
            "The control dashboard has recorded the failure. Operators must engage local backup emergency radios."
        )

    def generate_hazard_warning(
        self,
        event_type: str,
        location_id: str,
        location_name: str,
        floor: int,
        severity: str,
        is_uncertain: bool = False
    ) -> Dict[str, Any]:
        """
        Generates an autonomous hazard warning independent of route availability.
        Warns occupants away from the hazard immediately.
        """
        if is_uncertain:
            body = self.build_uncertain_hazard_warning(location_name or location_id, floor)
            headline = f"⚠️ SAFETY WARNING: UNVERIFIED HAZARD IN {location_name.upper()}"
        elif "FIRE" in event_type or "SMOKE" in event_type:
            body = self.build_corridor_fire_warning(location_name or location_id, floor)
            headline = f"🚨 EMERGENCY WARNING: FIRE DETECTED IN {location_name.upper()}"
        else:
            body = f"EMERGENCY ADVISORY: {event_type} reported at {location_name} (Floor {floor}). Do not approach."
            headline = f"🚨 HAZARD ALERT: {event_type}"

        # Dispatch via multi-channel adapters
        dispatched_msgs = self.dispatcher.broadcast(
            target_zone=location_name or location_id,
            floor=floor,
            headline=headline,
            body=body,
            severity=severity
        )

        warning_entry = {
            "time": time.strftime("%H:%M:%S"),
            "headline": headline,
            "body": body,
            "zone": location_name or location_id,
            "floor": f"Floor {floor}",
            "severity": severity,
            "is_uncertain": is_uncertain,
            "dispatched_channels": [m.to_dict() for m in dispatched_msgs]
        }

        self.active_hazard_warnings.append(warning_entry)
        self.alert_history.append(warning_entry)
        return warning_entry

    def generate_guidance(
        self,
        route_report: RouteSafetyReport,
        origin_id: str,
        goal_id: str,
        hazard_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates actionable evacuation guidance ONLY when verified, or explicit shelter-in-place instructions.
        """
        origin_node = self.nodes.get(origin_id)
        goal_node = self.nodes.get(goal_id)

        origin_name = origin_node.name if origin_node else origin_id
        goal_name = goal_node.name if goal_node else goal_id
        floor_num = origin_node.floor if origin_node else 0

        # Construct concise directives based on RouteSafetyReport status
        if route_report.status == "NO_VERIFIED_ROUTE":
            large_signage = f"🚨 ALL CORRIDORS BLOCKED • SHELTER IN PLACE (FLOOR {floor_num})"
            headline = "ATTENTION ALL OCCUPANTS: EMERGENCY IN PROGRESS"
            broadcast_msg = (
                f"Attention in {origin_name} (Floor {floor_num}). No verified safe evacuation route currently exists. "
                f"Do not enter corridors. Seal doors immediately with damp materials. Stay low. "
                f"Stand by for authorized emergency response personnel."
            )
            color_theme = "#ef4444"
            action_code = "SHELTER_IN_PLACE"

        elif route_report.status == "CONDITIONAL_ALTERNATIVE":
            large_signage = f"⚠️ PROCEED WITH CAUTION VIA ALTERNATIVE TO {goal_name.upper()}"
            headline = "ADVISORY: REVISED ROUTE (UNVERIFIED HAZARDS NEARBY)"
            broadcast_msg = (
                f"Attention in {origin_name}. An incident is active in adjacent zones. "
                f"Primary egress is blocked. Proceed with caution along secondary corridors toward {goal_name}. "
                f"Do not use elevators. Assist individuals requiring mobility accommodations."
            )
            color_theme = "#f59e0b"
            action_code = "CAUTION_EGRESS"

        else:  # VERIFIED_SAFE
            large_signage = f"🟢 VERIFIED ROUTE OPEN ➔ PROCEED TO {goal_name.upper()}"
            headline = "EMERGENCY GUIDANCE: EVACUATION ORDER"
            broadcast_msg = (
                f"Attention occupants in {origin_name}. Follow the green illuminated egress path to {goal_name}. "
                f"Estimated distance is {round(route_report.cost_meters, 0)} meters. Keep stairwell handrails clear."
            )
            color_theme = "#10b981"
            action_code = "PROCEED_ORDERLY"

        # Directional Step-by-Step Waypoint Guidance
        directional_steps = []
        if route_report.path and len(route_report.path) > 1:
            for idx in range(len(route_report.path) - 1):
                curr_nid = route_report.path[idx]
                next_nid = route_report.path[idx + 1]
                c_node = self.nodes.get(curr_nid)
                n_node = self.nodes.get(next_nid)
                
                c_name = c_node.name if c_node else curr_nid
                n_name = n_node.name if n_node else next_nid
                
                if c_node and n_node and c_node.floor != n_node.floor:
                    direction_str = f"Descend stairwell from Floor {c_node.floor} to Floor {n_node.floor} via {n_name}"
                else:
                    direction_str = f"Walk from {c_name} to {n_name}"
                
                directional_steps.append({
                    "step_number": idx + 1,
                    "from_node": c_name,
                    "to_node": n_name,
                    "instruction": direction_str,
                    "floor": n_node.floor if n_node else 0
                })

        # Transmit via MultiChannelDispatcher
        dispatched_msgs = self.dispatcher.broadcast(
            target_zone=origin_name,
            floor=floor_num,
            headline=headline,
            body=broadcast_msg,
            severity=route_report.status
        )

        guidance_record = {
            "time": time.strftime("%H:%M:%S"),
            "large_signage": large_signage,
            "headline": headline,
            "broadcast_text": broadcast_msg,
            "color_theme": color_theme,
            "action_code": action_code,
            "directional_steps": directional_steps,
            "speech_synth_text": broadcast_msg,
            "dispatched_channels": [m.to_dict() for m in dispatched_msgs]
        }

        self.active_guidance_directives = [guidance_record]
        self.alert_history.append(guidance_record)
        return guidance_record

    def clear(self):
        self.active_hazard_warnings.clear()
        self.active_guidance_directives.clear()
        self.alert_history.clear()
        self.dispatcher.clear()
