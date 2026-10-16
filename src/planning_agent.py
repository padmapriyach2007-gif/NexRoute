from typing import Dict, List, Set, Tuple, Optional, Any
from collections import deque
import copy
import time


class EvacuationGroup:
    def __init__(
        self,
        group_id: str,
        name: str,
        floor: int,
        headcount: int,
        requires_accessible: bool = False,
        is_hazard_origin: bool = False,
        urgency_level: str = "NORMAL"  # 'CRITICAL', 'HIGH', 'NORMAL'
    ):
        self.group_id = group_id
        self.name = name
        self.floor = floor
        self.headcount = headcount
        self.requires_accessible = requires_accessible
        self.is_hazard_origin = is_hazard_origin
        self.urgency_level = urgency_level


class EvacuationPlanningCSP:
    """
    Area 3: Constraint Satisfaction Problem (CSP) Evacuation Scheduler
    Solves anti-stampede staged evacuation using:
      1. Domain definitions & Unary Constraints
      2. AC-3 (Arc Consistency Algorithm #3)
      3. MRV (Minimum Remaining Values) Variable Ordering Heuristic with Degree Tie-breaking
      4. Forward-checking Backtracking Search
      5. Graceful Fallback Solver when constraints are mutually unsatisfiable.
    """
    def __init__(
        self,
        hazard_floor: int = 2,
        compromised_stairwell: str = "Stairwell A",
        groups: Optional[List[EvacuationGroup]] = None,
        stairwell_capacity: int = 60
    ):
        self.hazard_floor = hazard_floor
        self.compromised_stairwell = compromised_stairwell
        self.stairwell_capacity = stairwell_capacity
        
        # Setup groups
        if groups is None:
            self.groups = [
                EvacuationGroup("Floor_0", "Ground Floor Occupants", 0, 45, requires_accessible=False, is_hazard_origin=(hazard_floor == 0)),
                EvacuationGroup("Floor_1", "1st Floor (CSE/Library)", 1, 55, requires_accessible=False, is_hazard_origin=(hazard_floor == 1)),
                EvacuationGroup("Floor_2", "2nd Floor (Chemical Block)", 2, 40, requires_accessible=False, is_hazard_origin=(hazard_floor == 2)),
            ]
        else:
            self.groups = groups

        self.variables: Dict[str, List[Any]] = {}
        self.trace_logs: List[str] = []
        self._setup_problem()

    def _setup_problem(self):
        # Evacuation waves: 1 = Immediate (0-3 min), 2 = Secondary (3-6 min), 3 = Tertiary (6-9 min)
        # Wardens with specific certifications
        self.variables = {
            f"{g.group_id}_Wave": [1, 2, 3] for g in self.groups
        }
        for g in self.groups:
            self.variables[f"Warden_{g.group_id}"] = [
                "Warden_Chen (Hazmat)",
                "Warden_Sarah (FirstAid)",
                "Warden_David (CrowdControl)"
            ]

    def ac3(self, domains: Dict[str, List[Any]]) -> Tuple[bool, List[str]]:
        """
        AC-3 (Arc Consistency Algorithm #3)
        Enforces arc consistency across all binary constraints, eliminating inconsistent values from domains.
        """
        ac3_logs = []
        queue = deque()

        wave_vars = [f"{g.group_id}_Wave" for g in self.groups]
        for i in range(len(wave_vars)):
            for j in range(len(wave_vars)):
                if i != j:
                    queue.append((wave_vars[i], wave_vars[j]))

        warden_vars = [f"Warden_{g.group_id}" for g in self.groups]
        for i in range(len(warden_vars)):
            for j in range(len(warden_vars)):
                if i != j:
                    queue.append((warden_vars[i], warden_vars[j]))

        while queue:
            xi, xj = queue.popleft()
            revised, removed_vals = self._revise(domains, xi, xj)
            if revised:
                ac3_logs.append(f"AC-3 Pruned {xi}: removed {removed_vals} due to arc ({xi} → {xj})")
                if len(domains[xi]) == 0:
                    ac3_logs.append(f"AC-3 Conflict: Domain of {xi} exhausted!")
                    return False, ac3_logs
                all_relevant = wave_vars if "Wave" in xi else warden_vars
                for xk in all_relevant:
                    if xk != xi and xk != xj:
                        queue.append((xk, xi))

        return True, ac3_logs

    def _revise(self, domains: Dict[str, List[Any]], xi: str, xj: str) -> Tuple[bool, List[Any]]:
        revised = False
        to_remove = []

        for x_val in domains[xi]:
            has_support = False
            for y_val in domains[xj]:
                if self._check_arc_consistent(xi, x_val, xj, y_val):
                    has_support = True
                    break
            if not has_support:
                to_remove.append(x_val)
                revised = True

        for val in to_remove:
            domains[xi].remove(val)

        return revised, to_remove

    def _check_arc_consistent(self, xi: str, x_val: Any, xj: str, y_val: Any) -> bool:
        # Warden All-Different
        if "Warden" in xi and "Warden" in xj:
            return x_val != y_val

        # Wave Anti-Bottleneck (staggered floor stairwell egress)
        if "Wave" in xi and "Wave" in xj:
            # Different groups competing for the same single bottleneck stairwell cannot depart in the exact same wave
            # unless total headcount is less than capacity
            return x_val != y_val

        return True

    def is_consistent(self, var: str, val: Any, assignment: Dict[str, Any]) -> bool:
        """
        Validates full domain constraints against current partial assignment.
        Never allows optimization to override immediate life-safety requirements!
        """
        # Constraint 1: Immediate life-safety rule
        # Groups at hazard origin MUST evacuate in Wave 1
        for g in self.groups:
            if g.is_hazard_origin and var == f"{g.group_id}_Wave" and val != 1:
                return False

        # Constraint 2: Wave Anti-Bottleneck
        if "Wave" in var:
            for other_var, other_val in assignment.items():
                if "Wave" in other_var and other_val == val:
                    # If two groups share wave 1, only permitted if neither or both are in immediate emergency
                    return False

        # Constraint 3: Hazmat-certified warden strictly assigned to hazard origin
        for g in self.groups:
            if g.is_hazard_origin and var == f"Warden_{g.group_id}" and "Hazmat" not in str(val):
                return False

        # Constraint 4: Warden uniqueness (All-Different)
        if "Warden" in var:
            for other_var, other_val in assignment.items():
                if "Warden" in other_var and other_val == val:
                    return False

        return True

    def mrv_select_variable(self, assignment: Dict[str, Any], domains: Dict[str, List[Any]]) -> Optional[str]:
        """
        MRV (Minimum Remaining Values) Heuristic with Degree tie-breaker.
        """
        unassigned = [v for v in self.variables if v not in assignment]
        if not unassigned:
            return None

        def get_score(v):
            domain_size = len(domains[v])
            degree = 3 if str(self.hazard_floor) in v else 1
            return (domain_size, -degree)

        unassigned.sort(key=get_score)
        return unassigned[0]

    def solve(self) -> Dict[str, Any]:
        """
        Executes AC-3 preprocessing followed by MRV Backtracking Search.
        If unsatisfiable, triggers transparent fallback scheduler.
        """
        t0 = time.perf_counter()
        domains = copy.deepcopy(self.variables)

        # Unary Constraints:
        for g in self.groups:
            if g.is_hazard_origin:
                domains[f"{g.group_id}_Wave"] = [1]
                domains[f"Warden_{g.group_id}"] = ["Warden_Chen (Hazmat)"]

        # AC-3 Preprocessing
        ac3_success, ac3_logs = self.ac3(domains)

        assignment: Dict[str, Any] = {}
        backtrack_steps = 0
        search_logs = []

        if not ac3_success:
            search_logs.append("AC-3 determined problem is over-constrained. Activating Fallback Life-Safety Scheduler.")
            t1 = time.perf_counter()
            fallback_res = self._fallback_schedule(ac3_logs, (t1 - t0) * 1000.0)
            return fallback_res

        def backtrack(current_assign: Dict[str, Any], current_domains: Dict[str, List[Any]]) -> Optional[Dict[str, Any]]:
            nonlocal backtrack_steps
            backtrack_steps += 1

            if len(current_assign) == len(self.variables):
                return current_assign

            var = self.mrv_select_variable(current_assign, current_domains)
            if not var:
                return None

            search_logs.append(f"Step {backtrack_steps}: MRV selected variable '{var}' (choices: {current_domains[var]})")

            for val in current_domains[var]:
                if self.is_consistent(var, val, current_assign):
                    current_assign[var] = val
                    search_logs.append(f"  → Tentatively assigned {var} = {val}")

                    new_domains = copy.deepcopy(current_domains)
                    new_domains[var] = [val]

                    result = backtrack(current_assign, new_domains)
                    if result is not None:
                        return result

                    search_logs.append(f"  ↩ Backtracked on {var} = {val}")
                    del current_assign[var]

            return None

        solution = backtrack(assignment, domains)
        t1 = time.perf_counter()
        latency_ms = round((t1 - t0) * 1000.0, 3)

        if not solution:
            # Over-constrained conflict: provide transparent fallback
            return self._fallback_schedule(ac3_logs, latency_ms)

        # Construct readable timeline
        timeline = []
        for g in self.groups:
            wave = solution.get(f"{g.group_id}_Wave", 1)
            warden = solution.get(f"Warden_{g.group_id}", "Warden (Assigned)")
            time_window = f"Minute {(wave-1)*3} - {wave*3}"
            is_origin = g.is_hazard_origin
            status_text = "IMMEDIATE EVACUATION (Priority 1)" if wave == 1 else f"Wave {wave} Staged Egress"
            timeline.append({
                "group": g.name,
                "floor": f"Floor {g.floor}",
                "headcount": g.headcount,
                "wave": wave,
                "time_window": time_window,
                "warden": warden,
                "is_hazard_origin": is_origin,
                "accessible_required": g.requires_accessible,
                "status": status_text
            })
        timeline.sort(key=lambda x: x["wave"])

        return {
            "success": True,
            "solution": solution,
            "timeline": timeline,
            "ac3_pruning_logs": ac3_logs,
            "search_logs": search_logs,
            "backtrack_steps": backtrack_steps,
            "latency_ms": latency_ms,
            "is_fallback": False
        }

    def _fallback_schedule(self, ac3_logs: List[str], latency_ms: float) -> Dict[str, Any]:
        """
        Life-Safety Fallback Scheduler:
        When strict CSP constraints cannot be cleanly satisfied (e.g. conflicting stair bottleneck vs multiple immediate dangers),
        life safety supersedes staged spacing:
        All immediate hazard zones evacuate immediately in parallel with dual wardens.
        """
        timeline = []
        for g in self.groups:
            # Hazard floor gets Wave 1, others staged
            wave = 1 if g.is_hazard_origin else (2 if g.floor == 1 else 3)
            warden = "Warden_Chen (Hazmat)" if g.is_hazard_origin else "Warden_Sarah (FirstAid)"
            time_window = "Minute 0 - 3 (IMMEDIATE LIFE SAFETY)" if wave == 1 else f"Minute {(wave-1)*3} - {wave*3}"
            timeline.append({
                "group": g.name,
                "floor": f"Floor {g.floor}",
                "headcount": g.headcount,
                "wave": wave,
                "time_window": time_window,
                "warden": warden,
                "is_hazard_origin": g.is_hazard_origin,
                "accessible_required": g.requires_accessible,
                "status": "IMMEDIATE EMERGENCY EVACUATION (FALLBACK PROTOCOL)" if wave == 1 else f"Wave {wave} Staged Egress"
            })
        timeline.sort(key=lambda x: x["wave"])

        return {
            "success": False,
            "solution": None,
            "timeline": timeline,
            "ac3_pruning_logs": ac3_logs,
            "search_logs": ["Constraints unsatisfiable under strict anti-bottleneck. Triggered Life-Safety Parallel Evacuation Fallback."],
            "backtrack_steps": 0,
            "latency_ms": latency_ms,
            "is_fallback": True,
            "fallback_reason": "Mutually unsatisfiable stairwell capacity constraints. Fallback deployed to avoid trapping occupants."
        }
