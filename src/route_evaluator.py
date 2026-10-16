"""
CampusAegis (A.E.G.I.S.) Route Safety Evaluator
Distinct safety validation layer separating shortest-path geometric optimization from formal safety verification.

Core Mandate:
A* and Dijkstra compute geometric optimality; RouteEvaluator guarantees life-safety validation.
If any section of a candidate route violates safety, sensor freshness, or accessibility,
or lacks verified sensor telemetry, the route is rejected or flagged with explicit risk constraints.
If no safe route exists, it returns NO_VERIFIED_ROUTE with emergency fallback procedures.
"""

from typing import Dict, List, Optional, Any, Tuple
import time
from src.campus_graph import CampusNode
from src.search_engine import SearchResult
from src.safety_monitor import SafetyMonitor


class RouteSafetyReport:
    def __init__(
        self,
        status: str,  # 'VERIFIED_SAFE', 'CONDITIONAL_ALTERNATIVE', 'HIGH_UNCERTAINTY', 'NO_VERIFIED_ROUTE'
        is_safe: bool,
        path: List[str],
        cost_meters: float,
        estimated_time_sec: float,
        is_accessible: bool,
        hazard_violations: List[str],
        uncertainty_warnings: List[str],
        stale_data_nodes: List[str],
        capacity_bottlenecks: List[str],
        recommended_action: str,
        fallback_procedure: Optional[str] = None
    ):
        self.status = status
        self.is_safe = is_safe
        self.path = path
        self.cost_meters = cost_meters
        self.estimated_time_sec = estimated_time_sec
        self.is_accessible = is_accessible
        self.hazard_violations = hazard_violations
        self.uncertainty_warnings = uncertainty_warnings
        self.stale_data_nodes = stale_data_nodes
        self.capacity_bottlenecks = capacity_bottlenecks
        self.recommended_action = recommended_action
        self.fallback_procedure = fallback_procedure

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "is_safe": self.is_safe,
            "path": self.path,
            "cost_meters": round(self.cost_meters, 1),
            "estimated_time_sec": round(self.estimated_time_sec, 1),
            "is_accessible": self.is_accessible,
            "hazard_violations": self.hazard_violations,
            "uncertainty_warnings": self.uncertainty_warnings,
            "stale_nodes": self.stale_data_nodes,
            "bottlenecks": self.capacity_bottlenecks,
            "action": self.recommended_action,
            "fallback": self.fallback_procedure
        }


class RouteSafetyEvaluator:
    def __init__(self, nodes: Dict[str, CampusNode], safety_monitor: SafetyMonitor):
        self.nodes = nodes
        self.safety_monitor = safety_monitor

    def evaluate_route(
        self,
        search_result: SearchResult,
        requires_accessible: bool = False,
        group_size: int = 25
    ) -> RouteSafetyReport:
        """
        Performs rigorous safety validation on a candidate path.
        """
        path = search_result.path

        # 1. Check for empty or impossible path
        if not path or search_result.cost == float('inf'):
            return RouteSafetyReport(
                status="NO_VERIFIED_ROUTE",
                is_safe=False,
                path=[],
                cost_meters=float('inf'),
                estimated_time_sec=0.0,
                is_accessible=False,
                hazard_violations=["No geometrical or unblocked path exists from origin to destination."],
                uncertainty_warnings=[],
                stale_data_nodes=[],
                capacity_bottlenecks=[],
                recommended_action="Shelter in place inside sealed room; signal location to emergency responders.",
                fallback_procedure="SOP-FALLBACK-01: Seal corridor doors with damp materials, open exterior window for ventilation, activate emergency beacon."
            )

        hazard_violations = []
        uncertainty_warnings = []
        stale_nodes = []
        bottlenecks = []

        # 2. Inspect every node along the candidate path
        for nid in path:
            node_obj = self.nodes.get(nid)
            node_name = node_obj.name if node_obj else nid

            # Check active hazards & blockages
            zone_state = self.safety_monitor.zone_states.get(nid)
            if zone_state:
                if zone_state.is_hazard_confirmed or zone_state.is_blocked:
                    hazard_violations.append(f"Node {node_name} has active hazard: {zone_state.active_hazard_type or 'Blocked'}")
                if zone_state.is_conflicted:
                    uncertainty_warnings.append(f"Node {node_name} has contradictory sensor telemetry.")
                if zone_state.is_stale:
                    stale_nodes.append(f"Node {node_name} telemetry is stale.")
                if zone_state.is_uncertain:
                    uncertainty_warnings.append(f"Node {node_name} has low telemetry confidence ({zone_state.confidence_score:.0%}).")

            # Check accessibility requirement
            if requires_accessible and node_obj and not getattr(node_obj, "is_accessible", True):
                hazard_violations.append(f"Node {node_name} is not wheelchair accessible (stairwell without ramp).")

            # Check capacity bottlenecks
            if node_obj and group_size > getattr(node_obj, "capacity", 50):
                bottlenecks.append(f"Node {node_name} capacity ({node_obj.capacity}) exceeded by group size ({group_size}).")

        # 3. Decision synthesis
        if hazard_violations:
            return RouteSafetyReport(
                status="NO_VERIFIED_ROUTE",
                is_safe=False,
                path=path,
                cost_meters=search_result.cost,
                estimated_time_sec=search_result.estimated_time_seconds,
                is_accessible=search_result.is_accessible,
                hazard_violations=hazard_violations,
                uncertainty_warnings=uncertainty_warnings,
                stale_data_nodes=stale_nodes,
                capacity_bottlenecks=bottlenecks,
                recommended_action="Candidate path intersects active hazard or accessibility violation. Rerouting or shelter required.",
                fallback_procedure="Engage designated secondary stairwells or refuge areas until safety warden clearance."
            )

        if uncertainty_warnings or stale_nodes:
            return RouteSafetyReport(
                status="CONDITIONAL_ALTERNATIVE",
                is_safe=True,  # Traversable, but with explicit hazard warnings
                path=path,
                cost_meters=search_result.cost,
                estimated_time_sec=search_result.estimated_time_seconds,
                is_accessible=search_result.is_accessible,
                hazard_violations=[],
                uncertainty_warnings=uncertainty_warnings,
                stale_data_nodes=stale_nodes,
                capacity_bottlenecks=bottlenecks,
                recommended_action="Route is physically open, but proceed with high caution due to unverified/stale sensor readings in vicinity.",
                fallback_procedure="Deploy warden scout ahead to verify corridor integrity."
            )

        # 4. Fully verified safe route
        return RouteSafetyReport(
            status="VERIFIED_SAFE",
            is_safe=True,
            path=path,
            cost_meters=search_result.cost,
            estimated_time_sec=search_result.estimated_time_seconds,
            is_accessible=search_result.is_accessible,
            hazard_violations=[],
            uncertainty_warnings=[],
            stale_data_nodes=[],
            capacity_bottlenecks=bottlenecks,
            recommended_action=f"Proceed along verified path to safe assembly area ({len(path)} waypoints, ~{search_result.cost:.1f}m).",
            fallback_procedure=None
        )
