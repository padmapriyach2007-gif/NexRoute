from typing import Dict, List, Set, Tuple, Optional

class HornRule:
    def __init__(self, rule_id: str, premises: List[str], conclusion: str, explanation: str):
        self.rule_id = rule_id
        self.premises = [p.strip() for p in premises]
        self.conclusion = conclusion.strip()
        self.explanation = explanation

    def __repr__(self):
        return f"{' ∧ '.join(self.premises)} → {self.conclusion}"


class ProofStep:
    def __init__(self, step_num: int, rule_id: str, premises: List[str], conclusion: str, explanation: str):
        self.step_num = step_num
        self.rule_id = rule_id
        self.premises = premises
        self.conclusion = conclusion
        self.explanation = explanation

    def to_string(self) -> str:
        premise_str = " ∧ ".join(self.premises)
        return f"Step {self.step_num} [{self.rule_id}]: {premise_str} ⇒ {self.conclusion}  ({self.explanation})"


class KnowledgeBase:
    def __init__(self):
        self.rules: List[HornRule] = []
        self._load_campus_emergency_rules()

    def _load_campus_emergency_rules(self):
        self.rules = [
            # Base Hazard Classification
            HornRule(
                "R1_CHEM_SMOKE",
                ["Observed(Smoke)", "Location(Chem_Lab)"],
                "Hazard(Chemical_Fume_Release)",
                "Smoke detected inside chemistry laboratory indicates hazardous airborne chemical fumes."
            ),
            HornRule(
                "R2_OPEN_FLAME",
                ["Observed(Open_Flame)", "Location(Chem_Lab)"],
                "Hazard(Class_B_Chemical_Fire)",
                "Open flames within chemistry laboratory constitute Class B flammable liquid fire hazard."
            ),
            HornRule(
                "R3_TOXIC_VAPOR",
                ["Hazard(Chemical_Fume_Release)", "Chemicals_Present(Volatile_Solvents)"],
                "Severity(Level_2_Hazard)",
                "Volatile solvents under active fume release escalate incident to Level 2 containment emergency."
            ),
            HornRule(
                "R4_FIRE_ESCALATION",
                ["Hazard(Class_B_Chemical_Fire)", "Severity(Level_2_Hazard)"],
                "Severity(Level_3_Critical_Emergency)",
                "Uncontrolled Class B fire with hazardous chemicals escalates to Level 3 Campus-Wide Alert."
            ),
            HornRule(
                "R5_VENT_SHUTDOWN",
                ["Severity(Level_2_Hazard)"],
                "Action(Trigger_HVAC_Containment_Cutoff)",
                "Level 2 airborne chemical alert mandates automated building HVAC shutoff to avoid toxic cross-floor circulation."
            ),
            HornRule(
                "R6_STAIR_A_SMOKE",
                ["Observed(Smoke_Infiltration)", "Stairwell_Status(Stairwell_A)"],
                "Condition(Stairwell_A_Compromised)",
                "Smoke detected inside Stairwell A shaft compromises north vertical egress."
            ),
            HornRule(
                "R7_REROUTE_STAIR_B",
                ["Condition(Stairwell_A_Compromised)"],
                "Protocol(Reroute_Evacuation_Via_Stairwell_B)",
                "Compromised Stairwell A requires rerouting all upper-floor occupants via Stairwell B (South)."
            ),
            HornRule(
                "R8_LAB_ISOLATION",
                ["Severity(Level_2_Hazard)"],
                "Criteria(Mandatory_Isolation_Valve_Shut)",
                "Protocol dictates isolation of gas supply valves prior to floor clearance."
            ),
            HornRule(
                "R9_POWER_CIRCUIT",
                ["Hazard(Class_B_Chemical_Fire)"],
                "Criteria(Trip_Wing_Main_Breaker)",
                "Electrical power trip required in laboratory wing to prevent electrical re-ignition."
            ),
            HornRule(
                "R10_WARDEN_DISPATCH",
                ["Severity(Level_2_Hazard)"],
                "Protocol(Dispatch_Hazmat_Certified_Warden)",
                "Hazardous environment requires warden certified in Level 2 Hazmat PPE."
            )
        ]

    def forward_chain(self, initial_facts: Set[str]) -> Tuple[Set[str], List[ProofStep]]:
        """
        Forward Chaining Inference Engine (Data-Driven Horn-Clause Deducer)
        Starts with observed incident facts, iteratively fires rules until no new facts can be deduced.
        Returns: (all_known_facts, step_by_step_proof_trace)
        """
        known_facts = set(initial_facts)
        proof_trace: List[ProofStep] = []
        fired_rules: Set[str] = set()
        step = 1

        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                if rule.rule_id in fired_rules:
                    continue
                # Check if all premises are satisfied
                if all(prem in known_facts for prem in rule.premises):
                    if rule.conclusion not in known_facts:
                        known_facts.add(rule.conclusion)
                        proof_trace.append(ProofStep(
                            step_num=step,
                            rule_id=rule.rule_id,
                            premises=rule.premises,
                            conclusion=rule.conclusion,
                            explanation=rule.explanation
                        ))
                        step += 1
                        fired_rules.add(rule.rule_id)
                        changed = True

        return known_facts, proof_trace

    def backward_chain(self, goal: str, known_facts: Set[str], depth: int = 0, visited: Optional[Set[str]] = None) -> Dict:
        """
        Backward Chaining Inference Engine (Goal-Directed Horn-Clause Validator)
        Validates whether mandatory containment criteria or safety goals hold true.
        Returns: Proof tree dictionary with status and sub-derivations.
        """
        if visited is None:
            visited = set()

        if goal in known_facts:
            return {
                "goal": goal,
                "status": "PROVED_FACT",
                "depth": depth,
                "explanation": f"'{goal}' is directly established as a known verified fact.",
                "children": []
            }

        if goal in visited:
            return {
                "goal": goal,
                "status": "FAILED_CYCLE",
                "depth": depth,
                "explanation": "Cyclic reasoning detected.",
                "children": []
            }

        visited.add(goal)

        # Look for rules concluding this goal
        candidate_rules = [r for r in self.rules if r.conclusion == goal]
        if not candidate_rules:
            return {
                "goal": goal,
                "status": "UNPROVED",
                "depth": depth,
                "explanation": f"No Horn clause in Knowledge Base establishes '{goal}'.",
                "children": []
            }

        for rule in candidate_rules:
            child_proofs = []
            all_premises_proved = True
            for premise in rule.premises:
                sub_proof = self.backward_chain(premise, known_facts, depth + 1, visited.copy())
                child_proofs.append(sub_proof)
                if sub_proof["status"] not in ("PROVED_FACT", "PROVED_DERIVED"):
                    all_premises_proved = False

            if all_premises_proved:
                return {
                    "goal": goal,
                    "status": "PROVED_DERIVED",
                    "rule_id": rule.rule_id,
                    "depth": depth,
                    "explanation": f"Proved via rule [{rule.rule_id}]: {rule.explanation}",
                    "children": child_proofs
                }

        return {
            "goal": goal,
            "status": "FAILED_PREMISES",
            "depth": depth,
            "explanation": f"Required premises for '{goal}' could not be validated against known facts.",
            "children": child_proofs if 'child_proofs' in locals() else []
        }
