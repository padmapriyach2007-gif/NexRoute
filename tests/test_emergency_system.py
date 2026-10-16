"""
Comprehensive Unit & Integration Test Suite for CampusAegis (A.E.G.I.S.)
Verifies all 15 critical safety, event processing, graph pathfinding, logic deduction,
CSP scheduling, accessibility, sensor uncertainty, and degradation requirements.
"""

import pytest
import time
from src.event_models import EmergencyEvent, EventType, EventSeverity
from src.event_manager import EventManager
from src.sensor_simulator import SensorSimulator
from src.safety_monitor import SafetyMonitor
from src.search_engine import EvacuationSearchEngine
from src.route_evaluator import RouteSafetyEvaluator
from src.planning_agent import EvacuationPlanningCSP, EvacuationGroup
from src.knowledge_agent import KnowledgeBase
from src.pipeline import CampusSpherePipeline


@pytest.fixture
def pipeline():
    p = CampusSpherePipeline()
    p.reset_baseline()
    return p


# 1. A normal route is found in a valid test graph
def test_normal_route_found(pipeline):
    start = "VIG_ENGI_CHEMICAL_REACTION_ENGG_"
    goal = "VIG_FACI_PLAY_GROUNDS"
    res = pipeline.search_engine.a_star_search(start, goal)
    assert res.success is True
    assert len(res.path) > 1
    assert res.cost < float('inf')
    assert res.path[0] == start
    assert res.path[-1] == goal


# 2. A blocked edge or node is excluded from route planning
def test_blocked_node_excluded(pipeline):
    start = "VIG_ENGI_CHEMICAL_REACTION_ENGG_"
    goal = "VIG_FACI_PLAY_GROUNDS"
    
    # Base route uses Stairwell A or B
    res_base = pipeline.search_engine.a_star_search(start, goal)
    assert res_base.success is True
    
    # Block a node that was on the path
    node_to_block = res_base.path[1]
    pipeline.search_engine.inject_hazard(node_to_block, is_blocked=True)
    
    # Rerun search
    res_rerouted = pipeline.search_engine.a_star_search(start, goal)
    if res_rerouted.success:
        assert node_to_block not in res_rerouted.path


# 3. A new hazard triggers route reassessment
def test_hazard_triggers_reassessment(pipeline):
    start = "VIG_ENGI_PROCESS_DYNAMICS_AND_CO"
    goal = "VIG_FACI_PLAY_GROUNDS"
    
    res1 = pipeline.search_engine.a_star_search(start, goal)
    cost1 = res1.cost
    
    # Block primary stairwell
    pipeline.sensor_simulator.trigger_staircase_blocked("CHEM_STAIR_A_F2", "Stairwell A", 2)
    
    res2 = pipeline.search_engine.a_star_search(start, goal)
    # The new path should avoid Stairwell A
    assert "CHEM_STAIR_A_F2" not in res2.path
    if res2.success:
        assert res2.cost >= cost1


# 4. A stale reading does not establish that an area is safe
def test_stale_reading_not_safe(pipeline):
    monitor = pipeline.safety_monitor
    loc_id = "CHEM_STAIR_A_F2"
    
    # Inject stale reading
    pipeline.sensor_simulator.trigger_stale_reading(loc_id, "Stairwell A", 2, stale_seconds=300.0)
    
    is_safe, explanation = monitor.is_zone_verified_safe(loc_id)
    assert is_safe is False
    assert "stale" in explanation.lower() or "unresolved" in explanation.lower() or "not" in explanation.lower()


# 5. Conflicting sensors create an uncertainty warning
def test_conflicting_sensors_warning(pipeline):
    monitor = pipeline.safety_monitor
    loc_id = "HUB_CENTRAL_PLAZA"
    
    pipeline.sensor_simulator.trigger_sensor_conflict(loc_id, "Central Plaza", 0)
    warnings = monitor.get_active_warnings()
    
    assert any(w["type"] == "SENSOR_CONFLICT" for w in warnings)
    is_safe, explanation = monitor.is_zone_verified_safe(loc_id)
    assert is_safe is False
    assert "conflict" in explanation.lower() or "contradictory" in explanation.lower()


# 6. Duplicate events do not corrupt state (Idempotency)
def test_duplicate_events_idempotent(pipeline):
    em = pipeline.event_manager
    initial_count = len(em.event_history)
    
    event_payload = {
        "event_type": EventType.FIRE_DETECTED,
        "location_id": "VIG_ENGI_CHEMICAL_REACTION_ENGG_",
        "floor": 2,
        "source_id": "TEST_SENSOR_01",
        "severity": EventSeverity.CRITICAL
    }
    
    # First ingestion
    e1 = em.validate_and_ingest(event_payload)
    assert e1 is not None
    count_after_first = len(em.event_history)
    assert count_after_first == initial_count + 1
    
    # Immediate duplicate ingestion
    e2 = em.validate_and_ingest(event_payload)
    assert e2 is None  # Dropped as duplicate
    assert len(em.event_history) == count_after_first


# 7. Invalid events are rejected
def test_invalid_event_rejected(pipeline):
    em = pipeline.event_manager
    
    # Missing required field 'location_id' and invalid confidence
    invalid_payload = {
        "event_type": "FIRE_DETECTED",
        "confidence": 5.5  # Must be between 0.0 and 1.0
    }
    
    result = em.validate_and_ingest(invalid_payload)
    assert result is None
    assert len(em.rejected_events) > 0


# 8. An inaccessible route is not recommended for a user requiring accessibility
def test_inaccessible_route_excluded_for_wheelchair(pipeline):
    start = "VIG_ENGI_CHEMICAL_REACTION_ENGG_"  # On Floor 2
    goal = "VIG_FACI_PLAY_GROUNDS"
    
    # Floor 2 requires stairs to exit, so an accessible route without stairs is impossible
    res_acc = pipeline.search_engine.a_star_search(start, goal, requires_accessible=True)
    assert res_acc.success is False  # Cannot descend without stairs
    
    # However, ground floor location CAN reach play grounds without stairs
    ground_start = "VIG_ENGI_ADVANCED_PROGRAMMING_NE"
    res_ground_acc = pipeline.search_engine.a_star_search(ground_start, goal, requires_accessible=True)
    if res_ground_acc.success:
        assert all(pipeline.nodes[n].is_accessible for n in res_ground_acc.path)


# 9. CSP constraints are respected
def test_csp_constraints_respected(pipeline):
    planner = EvacuationPlanningCSP(hazard_floor=2, compromised_stairwell="Stairwell A")
    res = planner.solve()
    assert res["success"] is True
    
    solution = res["solution"]
    # Hazard floor must be Wave 1
    assert solution["Floor_2_Wave"] == 1
    # Hazmat warden must be assigned to hazard floor
    assert "Hazmat" in solution["Warden_Floor_2"]
    # All floor waves must be distinct to prevent crowd crush
    waves = [solution[k] for k in solution if "Wave" in k]
    assert len(waves) == len(set(waves))


# 10. Unsatisfiable scheduling is reported with transparent fallback
def test_unsatisfiable_csp_reports_fallback(pipeline):
    # Two hazard floors both requiring Wave 1 when only one can evacuate per wave
    groups = [
        EvacuationGroup("G1", "Lab Group 1", 2, 50, is_hazard_origin=True),
        EvacuationGroup("G2", "Lab Group 2", 1, 50, is_hazard_origin=True)
    ]
    planner = EvacuationPlanningCSP(hazard_floor=2, groups=groups)
    res = planner.solve()
    
    # Fallback protocol triggers because two immediate hazard origins cannot be artificially delayed
    assert res["is_fallback"] is True
    assert res["timeline"] is not None


# 11. A no-verified-route state is handled correctly
def test_no_verified_route_handled(pipeline):
    # Block both stairwells from Floor 2
    pipeline.search_engine.inject_hazard("CHEM_STAIR_A_F2", is_blocked=True)
    pipeline.search_engine.inject_hazard("CHEM_STAIR_B_F2", is_blocked=True)
    
    search_res = pipeline.search_engine.a_star_search("VIG_ENGI_CHEMICAL_REACTION_ENGG_", "VIG_FACI_PLAY_GROUNDS")
    safety_report = pipeline.route_evaluator.evaluate_route(search_res)
    
    assert safety_report.status == "NO_VERIFIED_ROUTE"
    assert safety_report.is_safe is False
    assert safety_report.fallback_procedure is not None
    assert "shelter" in safety_report.recommended_action.lower()


# 12. A simulated network outage is visible on the safety monitor
def test_simulated_network_outage(pipeline):
    pipeline.sensor_simulator.trigger_communication_failure()
    assert pipeline.safety_monitor.network_connected is False
    assert pipeline.safety_monitor.fallback_mode_active is True
    warnings = pipeline.safety_monitor.get_active_warnings()
    assert any(w["type"] == "COMMUNICATION_FAILURE" for w in warnings)


# 13. Decision explanations correspond to actual executed rules
def test_horn_clause_decision_explanations(pipeline):
    kb = pipeline.knowledge_base
    initial_facts = {"Observed(Smoke)", "Location(Chem_Lab)", "Chemicals_Present(Volatile_Solvents)"}
    
    deduced, trace = kb.forward_chain(initial_facts)
    assert "Hazard(Chemical_Fume_Release)" in deduced
    assert "Severity(Level_2_Hazard)" in deduced
    assert len(trace) >= 2
    
    # Verify backward chaining validation
    proof = kb.backward_chain("Criteria(Mandatory_Isolation_Valve_Shut)", deduced)
    assert proof["status"] in ("PROVED_FACT", "PROVED_DERIVED")


# 14. A scenario reset restores the expected baseline
def test_scenario_reset_restores_baseline(pipeline):
    # Inject hazard
    pipeline.sensor_simulator.trigger_smoke_detection("SNS-SMK-CHEM-F2")
    pipeline.sensor_simulator.trigger_communication_failure()
    assert len(pipeline.search_engine.blocked_nodes) > 0
    
    # Reset
    pipeline.reset_baseline()
    assert len(pipeline.search_engine.blocked_nodes) == 0
    assert pipeline.safety_monitor.network_connected is True
    assert len(pipeline.safety_monitor.get_active_warnings()) == 0
    assert len(pipeline.event_manager.event_history) == 0


# 15. Algorithm benchmark comparison consistency
def test_algorithm_benchmark(pipeline):
    start = "VIG_ENGI_CHEMICAL_REACTION_ENGG_"
    goal = "VIG_FACI_PLAY_GROUNDS"
    benchmark = pipeline.search_engine.run_benchmark(start, goal)
    
    assert "A* Search" in benchmark
    assert "Dijkstra" in benchmark
    assert "Greedy Best-First" in benchmark
    
    res_a = benchmark["A* Search"]
    res_d = benchmark["Dijkstra"]
    
    # A* and Dijkstra must find identical optimal shortest path length
    assert abs(res_a.cost - res_d.cost) < 1e-3
    # A* should explore fewer or equal nodes than Dijkstra
    assert res_a.nodes_explored <= res_d.nodes_explored


# 16. Prominent Demo Action: "Inject Fire" end-to-end execution
def test_inject_fire_prominent_action(pipeline):
    res = pipeline.scenario_manager.inject_fire(
        location_id="VIG_ENGI_CHEMICAL_REACTION_ENGG_",
        location_name="Chemical Reaction Engg Lab",
        floor=2
    )
    # Check that fire hazard was injected into search engine
    assert "VIG_ENGI_CHEMICAL_REACTION_ENGG_" in pipeline.search_engine.blocked_nodes
    # Check that autonomous guidance was generated
    assert res["guidance"] is not None
    assert len(res["guidance"]["large_signage"]) > 0
    # Check that event was logged into incident timeline
    assert any("FIRE" in e["type"] or "SMOKE" in e["type"] for e in res["timeline"])


# 17. Communication adapters transmission and failure tracking
def test_communication_adapters_delivery_and_failure(pipeline):
    dispatcher = pipeline.alert_manager.dispatcher
    
    # Normal broadcast: all channels should report SIMULATED
    msgs = dispatcher.broadcast("Chem Lab", 2, "FIRE WARNING", "Evacuate immediately", "CRITICAL")
    assert len(msgs) == 4
    assert all(m.delivery_status.value == "SIMULATED" for m in msgs)
    
    # Simulate communication bus failure: adapters should fail gracefully and report FAILED
    dispatcher.simulate_communication_failure()
    failed_msgs = dispatcher.broadcast("Chem Lab", 2, "FIRE WARNING", "Evacuate immediately", "CRITICAL")
    pa_msg = next(m for m in failed_msgs if m.channel == "SIMULATED_PUBLIC_ADDRESS")
    assert pa_msg.delivery_status.value == "FAILED"
    assert "offline" in pa_msg.failure_reason.lower()


# 18. Hazard warnings and evacuation routing are separate decisions
def test_separate_hazard_warning_and_routing(pipeline):
    # Total blockade on Floor 2: both stairs blocked
    pipeline.search_engine.inject_hazard("CHEM_STAIR_A_F2", is_blocked=True)
    pipeline.search_engine.inject_hazard("CHEM_STAIR_B_F2", is_blocked=True)
    
    # Generate explicit hazard warning for Chem Lab
    warn = pipeline.alert_manager.generate_hazard_warning(
        event_type="FIRE_DETECTED",
        location_id="VIG_ENGI_CHEMICAL_REACTION_ENGG_",
        location_name="Chemical Reaction Engg Lab",
        floor=2,
        severity="CRITICAL"
    )
    assert warn["headline"] is not None
    assert "FIRE" in warn["headline"]
    
    # Egress routing calculation should simultaneously report NO_VERIFIED_ROUTE
    search_res = pipeline.search_engine.a_star_search("VIG_ENGI_CHEMICAL_REACTION_ENGG_", "VIG_FACI_PLAY_GROUNDS")
    safety_rep = pipeline.route_evaluator.evaluate_route(search_res)
    assert safety_rep.status == "NO_VERIFIED_ROUTE"


# 19. Repeatable scenarios registration
def test_12_scenarios_registered(pipeline):
    scenarios = pipeline.scenario_manager.scenarios
    assert len(scenarios) >= 12
    assert "SCENARIO_1_SINGLE_FIRE" in scenarios
    assert "SCENARIO_9_NO_VERIFIED_ROUTE" in scenarios
    assert "SCENARIO_12_HAZARD_CLEARANCE" in scenarios
