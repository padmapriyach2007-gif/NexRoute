"""
CampusAegis (A.E.G.I.S.) Master Autonomous Pipeline Coordinator
Seamlessly orchestrates:
  1. Event Ingestion, Validation & Deduplication (EventManager)
  2. Sensor Simulation & IoT Telemetry (SensorSimulator)
  3. Hazard Freshness & Uncertainty Monitoring (SafetyMonitor)
  4. Deductive Horn-Clause Reasoning & Backward Validation (KnowledgeBase)
  5. Dynamic 3D Multi-Floor Heuristic Route Optimization (EvacuationSearchEngine)
  6. Independent Route Safety Certification & Fallback Layer (RouteSafetyEvaluator)
  7. Anti-Stampede CSP Evacuation Scheduling (EvacuationPlanningCSP)
  8. Autonomous Signage & Public-Address Guidance (AlertManager)
  9. Human-In-The-Loop Incident Review & Audit Logging (OperatorManager)
  10. Deterministic Repeatable Scenario Management (ScenarioManager)
"""

import time
from typing import Dict, Any, List, Optional, Set

from src.campus_graph import build_campus_building
from src.search_engine import EvacuationSearchEngine, SearchResult
from src.knowledge_agent import KnowledgeBase
from src.planning_agent import EvacuationPlanningCSP, EvacuationGroup
from src.rag_agent import LocalRAGAgent
from src.realtime_agent import RealTimeEvacuationAgent
from src.event_models import EmergencyEvent, EventType, EventSeverity
from src.event_manager import EventManager
from src.sensor_simulator import SensorSimulator
from src.safety_monitor import SafetyMonitor
from src.route_evaluator import RouteSafetyEvaluator, RouteSafetyReport
from src.alert_manager import AlertManager
from src.operator_manager import OperatorManager


class CampusSpherePipeline:
    def __init__(self):
        # 1. Base Graph & Search
        self.search_engine = EvacuationSearchEngine()
        self.nodes = self.search_engine.nodes
        self.base_edges = self.search_engine.base_edges

        # 2. Safety & Event Core
        self.event_manager = EventManager()
        self.safety_monitor = SafetyMonitor(stale_threshold_seconds=120.0)
        self.sensor_simulator = SensorSimulator(self.event_manager)

        # 3. Reasoning & SOPs
        self.knowledge_base = KnowledgeBase()
        self.rag_agent = LocalRAGAgent()

        # 4. Route Evaluation & Guidance
        self.route_evaluator = RouteSafetyEvaluator(self.nodes, self.safety_monitor)
        self.alert_manager = AlertManager(self.nodes)
        self.operator_manager = OperatorManager()

        # 5. Legacy agent adapter (for compatibility with existing UI)
        self.realtime_agent = RealTimeEvacuationAgent(self.search_engine)

        # 6. Scenario Manager
        from src.scenario_manager import ScenarioManager
        self.scenario_manager = ScenarioManager(self)

        # Register event subscriber: when an event is accepted, update safety monitor & graph
        self.event_manager.register_subscriber(self._on_emergency_event)

        # Performance metrics container
        self.last_metrics: Dict[str, Any] = {}

    def _on_emergency_event(self, event: EmergencyEvent):
        """Internal callback invoked automatically on every accepted event."""
        # 1. Update safety monitor zone state
        self.safety_monitor.process_event(event)

        # 2. If hazard confirmed, block in graph engine
        if event.event_type in (
            EventType.FIRE_DETECTED,
            EventType.SMOKE_DETECTED,
            EventType.CHEMICAL_HAZARD_DETECTED,
            EventType.CORRIDOR_BLOCKED,
            EventType.STAIRCASE_BLOCKED,
            EventType.EXIT_UNAVAILABLE
        ):
            self.search_engine.inject_hazard(event.location_id, is_blocked=True)
            self.realtime_agent.inject_hazard(event.location_id, hazard_type=event.event_type.value, severity=event.severity.value)

        elif event.event_type == EventType.HAZARD_CLEARED:
            self.search_engine.inject_hazard(event.location_id, is_blocked=False)
            self.realtime_agent.clear_hazard(event.location_id)

    def process_incident(
        self,
        raw_alert_text: str,
        start_node: Optional[str] = None,
        goal_node: str = "VIG_FACI_PLAY_GROUNDS",
        requires_accessible: bool = False,
        auto_inject_hazard: bool = True
    ) -> Dict[str, Any]:
        """
        Executes the full end-to-end event-driven emergency assessment pipeline.
        Records exact monotonic latencies for all stages.
        """
        t_start_total = time.perf_counter()

        # --- Stage 1: Local RAG & Incident Text Extraction ---
        t0_rag = time.perf_counter()
        rag_output = self.rag_agent.parse_incident_alert(raw_alert_text)
        t1_rag = time.perf_counter()
        rag_latency_ms = round((t1_rag - t0_rag) * 1000.0, 3)

        extracted_facts = set(rag_output["extracted_facts"])
        hazard_floor = rag_output["detected_floor"]

        # Default start node if not passed explicitly
        if not start_node:
            start_node = rag_output.get("detected_node_id", "VIG_ENGI_CHEMICAL_REACTION_ENGG_")
        if start_node not in self.nodes:
            start_node = "VIG_ENGI_CHEMICAL_REACTION_ENGG_"

        # --- Stage 2: Horn-Clause Deductive Reasoning ---
        t0_kb = time.perf_counter()
        deduced_facts, proof_trace = self.knowledge_base.forward_chain(extracted_facts)
        
        # Determine deduced severity level
        severity_level = "Level 1 (Standard Advisory)"
        if "Severity(Level_3_Critical_Emergency)" in deduced_facts:
            severity_level = "Level 3 (Campus-Wide Critical Emergency)"
        elif "Severity(Level_2_Hazard)" in deduced_facts:
            severity_level = "Level 2 (Severe Hazard / Containment Required)"

        # Backward Chaining: Validate mandatory containment criteria
        mandatory_criterion = "Criteria(Mandatory_Isolation_Valve_Shut)"
        proof_tree = self.knowledge_base.backward_chain(mandatory_criterion, deduced_facts)
        t1_kb = time.perf_counter()
        kb_latency_ms = round((t1_kb - t0_kb) * 1000.0, 3)

        # --- Stage 3: Auto-inject detected blockage from alert if configured ---
        if auto_inject_hazard and rag_output["stair_blocked"] and rag_output["blocked_stair_id"]:
            blocked_id = rag_output["blocked_stair_id"]
            node_name = self.nodes[blocked_id].name if blocked_id in self.nodes else blocked_id
            self.sensor_simulator.trigger_staircase_blocked(
                location_id=blocked_id,
                location_name=node_name,
                floor=hazard_floor,
                reason="Alert-reported smoke infiltration"
            )

        # --- Stage 4: Heuristic Route Search ---
        t0_search = time.perf_counter()
        search_result = self.search_engine.a_star_search(
            start=start_node,
            goal=goal_node,
            requires_accessible=requires_accessible,
            avoid_elevators=True
        )
        benchmark_results = self.search_engine.run_benchmark(start_node, goal_node)
        t1_search = time.perf_counter()
        search_latency_ms = round((t1_search - t0_search) * 1000.0, 3)

        # --- Stage 5: Independent Route Safety Evaluation ---
        t0_eval = time.perf_counter()
        route_safety_report = self.route_evaluator.evaluate_route(
            search_result=search_result,
            requires_accessible=requires_accessible,
            group_size=30
        )
        t1_eval = time.perf_counter()
        eval_latency_ms = round((t1_eval - t0_eval) * 1000.0, 3)

        # --- Stage 6: Anti-Stampede CSP Evacuation Scheduling ---
        t0_csp = time.perf_counter()
        compromised_stair = "Stairwell A" if rag_output["stair_blocked"] else "None"
        groups = [
            EvacuationGroup("Floor_0", "Ground Level Occupants", 0, 45, requires_accessible=False, is_hazard_origin=(hazard_floor == 0)),
            EvacuationGroup("Floor_1", "1st Floor (CSE/Library)", 1, 55, requires_accessible=False, is_hazard_origin=(hazard_floor == 1)),
            EvacuationGroup("Floor_2", "2nd Floor (Chemical Block)", 2, 40, requires_accessible=requires_accessible, is_hazard_origin=(hazard_floor == 2)),
        ]
        csp_planner = EvacuationPlanningCSP(hazard_floor=hazard_floor, compromised_stairwell=compromised_stair, groups=groups)
        csp_result = csp_planner.solve()
        t1_csp = time.perf_counter()
        csp_latency_ms = round((t1_csp - t0_csp) * 1000.0, 3)

        # --- Stage 7: Autonomous Guidance & Simulated PA Generation ---
        t0_alert = time.perf_counter()
        guidance = self.alert_manager.generate_guidance(
            route_report=route_safety_report,
            origin_id=start_node,
            goal_id=goal_node,
            hazard_type=rag_output.get("hazard_type")
        )
        t1_alert = time.perf_counter()
        alert_latency_ms = round((t1_alert - t0_alert) * 1000.0, 3)

        t_end_total = time.perf_counter()
        total_pipeline_latency_ms = round((t_end_total - t_start_total) * 1000.0, 3)

        # Record system performance metrics
        self.last_metrics = {
            "total_latency_ms": total_pipeline_latency_ms,
            "rag_latency_ms": rag_latency_ms,
            "kb_latency_ms": kb_latency_ms,
            "search_latency_ms": search_latency_ms,
            "eval_latency_ms": eval_latency_ms,
            "csp_latency_ms": csp_latency_ms,
            "alert_latency_ms": alert_latency_ms,
            "nodes_in_graph": len(self.nodes),
            "edges_in_graph": len(self.base_edges),
            "blocked_nodes_count": len(self.search_engine.blocked_nodes)
        }

        # Determine System Safety Status state
        system_status = self._determine_system_status(route_safety_report)

        return {
            "status": system_status,
            "rag": rag_output,
            "knowledge": {
                "initial_facts": list(extracted_facts),
                "deduced_facts": list(deduced_facts),
                "severity_level": severity_level,
                "proof_trace": [step.to_string() for step in proof_trace],
                "backward_chain_tree": proof_tree
            },
            "navigation": {
                "start_node": start_node,
                "goal_node": goal_node,
                "requires_accessible": requires_accessible,
                "evacuation_route": search_result.to_dict(),
                "safety_report": route_safety_report.to_dict(),
                "benchmark": {alg: res.to_dict() for alg, res in benchmark_results.items()}
            },
            "csp": csp_result,
            "guidance": guidance,
            "realtime": {
                "active_hazards": [h.to_dict() for h in self.realtime_agent.active_hazards.values()],
                "event_log": self.realtime_agent.event_log
            },
            "safety_monitor": {
                "warnings": self.safety_monitor.get_active_warnings(),
                "network_connected": self.safety_monitor.network_connected,
                "fallback_active": self.safety_monitor.fallback_mode_active
            },
            "timeline": self.event_manager.get_timeline(limit=30),
            "operator_audit": self.operator_manager.get_audit_trail(limit=20),
            "metrics": self.last_metrics
        }

    def _determine_system_status(self, safety_report: RouteSafetyReport) -> str:
        if not self.safety_monitor.network_connected or self.safety_monitor.fallback_mode_active:
            return "COMMUNICATION_DEGRADED"
        if safety_report.status == "NO_VERIFIED_ROUTE":
            return "NO_VERIFIED_ROUTE"
        if self.safety_monitor.active_warnings:
            first_warn = self.safety_monitor.active_warnings[0]["type"]
            if first_warn in ("SENSOR_CONFLICT", "STALE_DATA", "SENSOR_OFFLINE"):
                return "SENSOR_UNCERTAIN"
            return "HUMAN_REVIEW_REQUIRED"
        if safety_report.status == "VERIFIED_SAFE" and self.search_engine.blocked_nodes:
            return "ROUTE_VERIFIED_BY_MODEL"
        if safety_report.status == "CONDITIONAL_ALTERNATIVE":
            return "HUMAN_REVIEW_REQUIRED"
        if self.search_engine.blocked_nodes:
            return "ALERT_ACTIVE"
        return "NORMAL"

    def reset_baseline(self):
        """Resets all hazards, safety monitor, events, and operator state to pristine normal readiness."""
        self.search_engine.clear_hazards()
        self.realtime_agent.clear_all()
        self.safety_monitor.reset()
        self.event_manager.clear()
        self.alert_manager.clear()
        self.operator_manager.reset()
