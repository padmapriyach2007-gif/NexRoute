"""
CampusAegis (A.E.G.I.S.) Scenario Manager
Provides 12 deterministic, repeatable emergency scenarios for live demonstration,
stress-testing, and rigorous safety verification.

Scenarios (Section 11):
  1. Single fire in a corridor.
  2. Fire with a blocked staircase.
  3. Two simultaneous hazards.
  4. Unavailable emergency exit.
  5. Conflicting sensor readings.
  6. Stale sensor data.
  7. Sensor offline.
  8. Communication failure.
  9. No route passing the model's safety checks (NO_VERIFIED_ROUTE).
  10. Accessible-route constraint.
  11. Changing hazard requiring route recalculation.
  12. Hazard clearance and incident resolution.
"""

from typing import Dict, Any, Optional
import time


class EmergencyScenario:
    def __init__(
        self,
        scenario_id: str,
        name: str,
        category: str,
        description: str,
        origin_node: str,
        goal_node: str,
        requires_accessible: bool = False,
        expected_outcome: str = ""
    ):
        self.scenario_id = scenario_id
        self.name = name
        self.category = category
        self.description = description
        self.origin_node = origin_node
        self.goal_node = goal_node
        self.requires_accessible = requires_accessible
        self.expected_outcome = expected_outcome


class ScenarioManager:
    def __init__(self, pipeline: Any):
        self.pipeline = pipeline
        self.scenarios: Dict[str, EmergencyScenario] = self._setup_scenarios()
        self.active_scenario: Optional[EmergencyScenario] = None

    def _setup_scenarios(self) -> Dict[str, EmergencyScenario]:
        return {
            "SCENARIO_1_SINGLE_FIRE": EmergencyScenario(
                scenario_id="SCENARIO_1_SINGLE_FIRE",
                name="Scenario 1: Single Fire in Corridor",
                category="Fire Hazard",
                description="Fire reported in the east corridor near Process Dynamics Lab (Floor 1). Reassesses paths and bypasses affected corridor.",
                origin_node="VIG_ENGI_CHEMICAL_REACTION_ENGG_",
                goal_node="VIG_FACI_PLAY_GROUNDS",
                requires_accessible=False,
                expected_outcome="Corridor blocked. Automatic warning generated. Path safely rerouted around affected corridor."
            ),
            "SCENARIO_2_BLOCKED_STAIRCASE": EmergencyScenario(
                scenario_id="SCENARIO_2_BLOCKED_STAIRCASE",
                name="Scenario 2: Fire with Blocked Staircase",
                category="Structural Chokepoint",
                description="Dense smoke infiltration in Chem Block Stairwell A (North). Egress shaft flagged non-traversable; system reroutes via Stairwell B (South).",
                origin_node="VIG_ENGI_CHEMICAL_REACTION_ENGG_",
                goal_node="VIG_FACI_PLAY_GROUNDS",
                requires_accessible=False,
                expected_outcome="Stairwell A excluded. Immediate reroute calculated via Stairwell B down to Play Grounds."
            ),
            "SCENARIO_3_MULTI_HAZARD": EmergencyScenario(
                scenario_id="SCENARIO_3_MULTI_HAZARD",
                name="Scenario 3: Two Simultaneous Hazards",
                category="Compound Crisis",
                description="Simultaneous volatile chemical spill in Chem Lab (Floor 2) and electrical panel fire in EEE Power Systems Lab (Floor 0). Concurrent isolation.",
                origin_node="VIG_ENGI_PROCESS_DYNAMICS_AND_CO",
                goal_node="VIG_FACI_PLAY_GROUNDS",
                requires_accessible=False,
                expected_outcome="Both hazard zones isolated simultaneously; path calculated avoiding both perimeters."
            ),
            "SCENARIO_4_UNAVAILABLE_EXIT": EmergencyScenario(
                scenario_id="SCENARIO_4_UNAVAILABLE_EXIT",
                name="Scenario 4: Unavailable Emergency Exit",
                category="Exit Chokepoint",
                description="Play Grounds Main Gate assembly exit blocked by maintenance equipment. System detects exit unavailability and reroutes to Transport Buses exit.",
                origin_node="HUB_CENTRAL_PLAZA",
                goal_node="VIG_FACI_TRANSPORT_BUSES",
                requires_accessible=False,
                expected_outcome="Exit unavailability flagged; traffic redirected to alternative designated campus exit."
            ),
            "SCENARIO_5_SENSOR_CONFLICT": EmergencyScenario(
                scenario_id="SCENARIO_5_SENSOR_CONFLICT",
                name="Scenario 5: Conflicting Sensor Readings",
                category="Telemetry Uncertainty",
                description="Smoke detector at Central Quad Plaza reports 88% obscuration, but thermal and secondary sensors report nominal ambient. Status marked SENSOR_UNCERTAIN.",
                origin_node="VIG_ENGI_ADVANCED_PROGRAMMING_NE",
                goal_node="VIG_FACI_PLAY_GROUNDS",
                requires_accessible=False,
                expected_outcome="Uncertainty warning displayed. System refuses to falsely certify route as safe."
            ),
            "SCENARIO_6_STALE_DATA": EmergencyScenario(
                scenario_id="SCENARIO_6_STALE_DATA",
                name="Scenario 6: Stale Sensor Data",
                category="Sensor Degradation",
                description="Corridor sensor telemetry heartbeat missing for > 5 minutes. Silence is not treated as safe; zone flagged STALE.",
                origin_node="CHEM_STAIR_A_F2",
                goal_node="VIG_FACI_PLAY_GROUNDS",
                requires_accessible=False,
                expected_outcome="Stale data warning generated. Route flagged as conditional with caution advisory."
            ),
            "SCENARIO_7_SENSOR_OFFLINE": EmergencyScenario(
                scenario_id="SCENARIO_7_SENSOR_OFFLINE",
                name="Scenario 7: Sensor Offline Failure",
                category="Hardware Loss",
                description="Key optical smoke sensor SNS-SMK-CHEM-F2 goes offline abruptly. System alerts operator and flags unmonitored zone.",
                origin_node="VIG_ENGI_CHEMICAL_REACTION_ENGG_",
                goal_node="VIG_FACI_PLAY_GROUNDS",
                requires_accessible=False,
                expected_outcome="Sensor offline alert logged. Confidence score set to 0.0% for affected zone."
            ),
            "SCENARIO_8_COMMUNICATION_FAILURE": EmergencyScenario(
                scenario_id="SCENARIO_8_COMMUNICATION_FAILURE",
                name="Scenario 8: Communication Failure (Bus Outage)",
                category="Degraded Infrastructure",
                description="Campus communications bus severed. Delivery of automated guidance cannot be confirmed. Dashboard engages fallback mode.",
                origin_node="VIG_ENGI_PROCESS_DYNAMICS_AND_CO",
                goal_node="VIG_FACI_PLAY_GROUNDS",
                requires_accessible=False,
                expected_outcome="Delivery failure visible on dashboard. Operators alerted to engage backup radios."
            ),
            "SCENARIO_9_NO_VERIFIED_ROUTE": EmergencyScenario(
                scenario_id="SCENARIO_9_NO_VERIFIED_ROUTE",
                name="Scenario 9: No Route Passing Safety Checks",
                category="Worst-Case Safety",
                description="Both Stairwell A and Stairwell B on Floor 2 compromised. All egress paths impassable. System asserts NO_VERIFIED_ROUTE.",
                origin_node="VIG_ENGI_CHEMICAL_REACTION_ENGG_",
                goal_node="VIG_FACI_PLAY_GROUNDS",
                requires_accessible=False,
                expected_outcome="Explicit NO_VERIFIED_ROUTE returned. Visual signage and audio PA broadcast Shelter-in-Place instructions."
            ),
            "SCENARIO_10_ACCESSIBILITY": EmergencyScenario(
                scenario_id="SCENARIO_10_ACCESSIBILITY",
                name="Scenario 10: Accessible-Route Constraint",
                category="Inclusive Safety",
                description="Occupant requiring wheelchair/accessible route needs egress. Elevators forbidden during fire; stairs impassable. System enforces accessibility rules.",
                origin_node="VIG_ENGI_ADVANCED_PROGRAMMING_NE",
                goal_node="VIG_FACI_PLAY_GROUNDS",
                requires_accessible=True,
                expected_outcome="Stairways excluded. Ground ramp / accessible exit path computed or escalation requested."
            ),
            "SCENARIO_11_CHANGING_HAZARD": EmergencyScenario(
                scenario_id="SCENARIO_11_CHANGING_HAZARD",
                name="Scenario 11: Changing Hazard Requiring Recalculation",
                category="Dynamic Evolution",
                description="Initial fire at Stairwell A prompts rerouting through Stairwell B; subsequent smoke flare-up in Central Plaza forces second dynamic recalculation.",
                origin_node="VIG_ENGI_CHEMICAL_REACTION_ENGG_",
                goal_node="VIG_FACI_PLAY_GROUNDS",
                requires_accessible=False,
                expected_outcome="Two successive real-time route adaptations in <50ms each."
            ),
            "SCENARIO_12_HAZARD_CLEARANCE": EmergencyScenario(
                scenario_id="SCENARIO_12_HAZARD_CLEARANCE",
                name="Scenario 12: Hazard Clearance & Incident Resolution",
                category="Recovery Workflow",
                description="Safety inspector physically confirms hazard extinguished and atmosphere ventilated. Formal clearance restores normal readiness.",
                origin_node="VIG_ENGI_CHEMICAL_REACTION_ENGG_",
                goal_node="VIG_FACI_PLAY_GROUNDS",
                requires_accessible=False,
                expected_outcome="Hazards cleared with explicit audit entry. System returns to NORMAL readiness."
            )
        }

    def inject_fire(self, location_id: str = "VIG_ENGI_CHEMICAL_REACTION_ENGG_", location_name: str = "Chemical Reaction Engg Lab", floor: int = 2) -> Dict[str, Any]:
        """
        Prominent Core Demonstration Action (Section 11):
        - A simulated fire event is created.
        - The affected zone is marked on the map.
        - An automatic warning is generated without any chatbot interaction.
        - Routes using the affected area are rejected.
        - The route planner recalculates alternatives.
        - The dashboard explains the resulting route decision.
        """
        # 1. Trigger simulated fire event
        self.pipeline.sensor_simulator.trigger_smoke_detection("SNS-SMK-CHEM-F2", obscuration_pct=95.0)
        self.pipeline.sensor_simulator.trigger_corridor_blocked(
            location_id=location_id,
            location_name=location_name,
            floor=floor,
            reason="Uncontrolled Class B Fire with Dense Smoke"
        )

        # 2. Automatically generate autonomous hazard warning
        self.pipeline.alert_manager.generate_hazard_warning(
            event_type="FIRE_DETECTED",
            location_id=location_id,
            location_name=location_name,
            floor=floor,
            severity="CRITICAL"
        )

        # 3. Recalculate pipeline
        alert_desc = f"Emergency Alert: Active fire and dense smoke detected at {location_name} (Floor {floor}). Immediate evacuation ordered."
        res = self.pipeline.process_incident(
            raw_alert_text=alert_desc,
            start_node=location_id,
            goal_node="VIG_FACI_PLAY_GROUNDS",
            requires_accessible=False,
            auto_inject_hazard=True
        )

        return res

    def execute_scenario(self, scenario_id: str) -> Dict[str, Any]:
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f"Unknown scenario ID: {scenario_id}")

        self.reset_all()
        self.active_scenario = scenario

        if scenario_id == "SCENARIO_1_SINGLE_FIRE":
            self.pipeline.sensor_simulator.trigger_corridor_blocked(
                "VIG_ENGI_PROCESS_DYNAMICS_AND_CO", "Process Dynamics Lab Corridor", 2, reason="Corridor Fire & Smoke"
            )

        elif scenario_id == "SCENARIO_2_BLOCKED_STAIRCASE":
            self.pipeline.sensor_simulator.trigger_staircase_blocked(
                "CHEM_STAIR_A_F2", "Chem Block Stairwell A (North)", 2, reason="Dense Smoke Infiltration"
            )

        elif scenario_id == "SCENARIO_3_MULTI_HAZARD":
            self.pipeline.sensor_simulator.trigger_chemical_spill(
                "VIG_ENGI_CHEMICAL_REACTION_ENGG_", "Chemical Reaction Engg Lab", 2, ppm=450.0
            )
            self.pipeline.sensor_simulator.trigger_corridor_blocked(
                "VIG_ENGI_POWER_SYSTEMS_LAB", "Power Systems Lab", 0, reason="Electrical Arc Fire"
            )

        elif scenario_id == "SCENARIO_4_UNAVAILABLE_EXIT":
            self.pipeline.sensor_simulator.trigger_corridor_blocked(
                "VIG_FACI_PLAY_GROUNDS", "Play Grounds Main Gate", 0, reason="Gate Structural Maintenance Blockade"
            )

        elif scenario_id == "SCENARIO_5_SENSOR_CONFLICT":
            self.pipeline.sensor_simulator.trigger_sensor_conflict(
                "HUB_CENTRAL_PLAZA", "Central Quadrangle Plaza", 0
            )

        elif scenario_id == "SCENARIO_6_STALE_DATA":
            self.pipeline.sensor_simulator.trigger_stale_reading(
                "CHEM_STAIR_A_F2", "Chem Block Stairwell A", 2, stale_seconds=360.0
            )

        elif scenario_id == "SCENARIO_7_SENSOR_OFFLINE":
            self.pipeline.sensor_simulator.trigger_sensor_offline("SNS-SMK-CHEM-F2")

        elif scenario_id == "SCENARIO_8_COMMUNICATION_FAILURE":
            self.pipeline.sensor_simulator.trigger_communication_failure("Chemical Engineering Block")
            self.pipeline.alert_manager.dispatcher.simulate_communication_failure()

        elif scenario_id == "SCENARIO_9_NO_VERIFIED_ROUTE":
            self.pipeline.sensor_simulator.trigger_staircase_blocked("CHEM_STAIR_A_F2", "Chem Stairwell A", 2)
            self.pipeline.sensor_simulator.trigger_staircase_blocked("CHEM_STAIR_B_F2", "Chem Stairwell B", 2)

        elif scenario_id == "SCENARIO_10_ACCESSIBILITY":
            pass

        elif scenario_id == "SCENARIO_11_CHANGING_HAZARD":
            # Initial Stairwell A blocked, then Central Plaza blocked
            self.pipeline.sensor_simulator.trigger_staircase_blocked("CHEM_STAIR_A_F2", "Chem Stairwell A", 2)
            self.pipeline.sensor_simulator.trigger_corridor_blocked("HUB_CENTRAL_PLAZA", "Central Quad Plaza", 0)

        elif scenario_id == "SCENARIO_12_HAZARD_CLEARANCE":
            # First trigger, then clear
            self.pipeline.sensor_simulator.trigger_hazard_cleared("CHEM_STAIR_A_F2", "Chem Stairwell A", 2)
            self.pipeline.operator_manager.record_acknowledgment("INCIDENT-RESOLVED", operator_name="Safety Marshal")

        res = self.pipeline.process_incident(
            raw_alert_text=scenario.description,
            start_node=scenario.origin_node,
            goal_node=scenario.goal_node,
            requires_accessible=scenario.requires_accessible,
            auto_inject_hazard=True
        )

        return {
            "scenario": {
                "id": scenario.scenario_id,
                "name": scenario.name,
                "category": scenario.category,
                "description": scenario.description,
                "expected": scenario.expected_outcome
            },
            "pipeline_result": res
        }

    def reset_all(self):
        self.active_scenario = None
        self.pipeline.reset_baseline()
