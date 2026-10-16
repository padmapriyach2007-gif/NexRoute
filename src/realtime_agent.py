import time
from typing import Dict, List, Set, Tuple, Optional, Any
from src.search_engine import EvacuationSearchEngine, SearchResult

class HazardEvent:
    def __init__(self, hazard_id: str, location_name: str, hazard_type: str, severity: str, timestamp: float):
        self.hazard_id = hazard_id
        self.location_name = location_name
        self.hazard_type = hazard_type  # 'Smoke Infiltration', 'Class B Fire', 'Debris Blockage'
        self.severity = severity        # 'CRITICAL', 'WARNING', 'ISOLATED'
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "hazard_id": self.hazard_id,
            "location_name": self.location_name,
            "hazard_type": self.hazard_type,
            "severity": self.severity,
            "timestamp": time.strftime("%H:%M:%S", time.localtime(self.timestamp))
        }

class RealTimeEvacuationAgent:
    """
    Area 5: Real-Time Reactive AI Agent
    Monitors dynamic building environment, receives asynchronous hazard injections,
    updates graph topology in memory, and triggers deterministic sub-50ms path replanning.
    """
    def __init__(self, search_engine: EvacuationSearchEngine):
        self.search_engine = search_engine
        self.active_hazards: Dict[str, HazardEvent] = {}
        self.event_log: List[Dict[str, Any]] = []

    def inject_hazard(self, target_node: str, hazard_type: str = "Blocked by Smoke", severity: str = "CRITICAL") -> Dict[str, Any]:
        t0 = time.perf_counter()
        node_obj = self.search_engine.nodes.get(target_node)
        loc_name = node_obj.name if node_obj else target_node

        event = HazardEvent(
            hazard_id=target_node,
            location_name=loc_name,
            hazard_type=hazard_type,
            severity=severity,
            timestamp=time.time()
        )
        self.active_hazards[target_node] = event
        
        # Inject into graph engine
        self.search_engine.inject_hazard(target_node, is_blocked=True)

        t1 = time.perf_counter()
        replan_latency_ms = round((t1 - t0) * 1000.0, 3)

        log_entry = {
            "action": "HAZARD_INJECTED",
            "target": target_node,
            "location": loc_name,
            "type": hazard_type,
            "latency_ms": replan_latency_ms,
            "time": time.strftime("%H:%M:%S")
        }
        self.event_log.append(log_entry)

        return {
            "status": "HAZARD_ACTIVE",
            "node": target_node,
            "location_name": loc_name,
            "hazard_type": hazard_type,
            "injection_latency_ms": replan_latency_ms
        }

    def clear_hazard(self, target_node: str) -> Dict[str, Any]:
        if target_node in self.active_hazards:
            del self.active_hazards[target_node]
        self.search_engine.inject_hazard(target_node, is_blocked=False)
        
        self.event_log.append({
            "action": "HAZARD_CLEARED",
            "target": target_node,
            "time": time.strftime("%H:%M:%S")
        })
        return {"status": "HAZARD_CLEARED", "node": target_node}

    def clear_all(self):
        self.active_hazards.clear()
        self.search_engine.clear_hazards()
        self.event_log.append({
            "action": "ALL_HAZARDS_RESET",
            "time": time.strftime("%H:%M:%S")
        })

    def dynamic_replan(self, start_node: str, goal_node: str = "G_ASSEMBLY_N") -> Tuple[SearchResult, float]:
        """
        Calculates reactive rerouted evacuation path in real time (< 50ms).
        """
        t0 = time.perf_counter()
        result = self.search_engine.a_star_search(start_node, goal_node)
        t1 = time.perf_counter()
        total_replan_ms = round((t1 - t0) * 1000.0, 3)
        return result, total_replan_ms
