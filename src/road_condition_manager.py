"""
Road Condition and Navigation Constraint Manager for CampusAegis 2.0
Manages verified road closures, construction zones, traffic delays, and operating modes.
Performs spatial collision detection against route polylines and maintains strict data provenance.
"""

import math
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

from src.road_condition_model import (
    RoadRestriction,
    TrafficCondition,
    RestrictionType,
    TrafficSeverity,
    OperatingMode
)
from src.hazard_map import distance_point_to_segment_m, haversine_distance_m


class RoadConditionManager:
    """
    Central manager for verified road restrictions, construction updates, and traffic conditions.
    Enforces mode boundaries (LIVE_ROUTING, STANDARD_ROUTING, CONTROLLED_DEMO).
    """

    def __init__(self, initial_mode: OperatingMode = OperatingMode.LIVE_ROUTING):
        self.operating_mode: OperatingMode = initial_mode
        self._restrictions: Dict[str, RoadRestriction] = {}
        self._traffic_conditions: Dict[str, TrafficCondition] = {}
        self.active_demo_scenario: Optional[str] = None

    def set_mode(self, mode: OperatingMode):
        self.operating_mode = mode
        # In LIVE_ROUTING, remove any demonstration fixtures immediately
        if self.operating_mode == OperatingMode.LIVE_ROUTING:
            self.clear_demonstration_data()

    def add_restriction(self, restriction: RoadRestriction) -> bool:
        if self.operating_mode == OperatingMode.LIVE_ROUTING and restriction.is_demonstration:
            # Reject demonstration data in live mode
            return False
        self._restrictions[restriction.restriction_id] = restriction
        return True

    def remove_restriction(self, restriction_id: str) -> bool:
        if restriction_id in self._restrictions:
            del self._restrictions[restriction_id]
            return True
        return False

    def add_traffic_condition(self, traffic: TrafficCondition) -> bool:
        if self.operating_mode == OperatingMode.LIVE_ROUTING and traffic.is_demonstration:
            return False
        self._traffic_conditions[traffic.segment_id] = traffic
        return True

    def clear_all(self):
        self._restrictions.clear()
        self._traffic_conditions.clear()
        self.active_demo_scenario = None

    def clear_demonstration_data(self):
        self._restrictions = {k: v for k, v in self._restrictions.items() if not v.is_demonstration}
        self._traffic_conditions = {k: v for k, v in self._traffic_conditions.items() if not v.is_demonstration}
        self.active_demo_scenario = None

    def get_active_restrictions(self) -> List[RoadRestriction]:
        return list(self._restrictions.values())

    def get_active_traffic_conditions(self) -> List[TrafficCondition]:
        return list(self._traffic_conditions.values())

    def check_route_restrictions(
        self,
        polyline: List[Tuple[float, float]],
        safety_clearance_m: float = 30.0
    ) -> List[Dict[str, Any]]:
        """
        Tests whether any active road restriction intersects the route polyline.
        Returns a list of conflicts with distance and restriction metadata.
        """
        conflicts = []
        if not polyline or len(polyline) < 2:
            return conflicts

        for r in self._restrictions.values():
            threshold_m = r.affected_radius_meters + safety_clearance_m
            min_dist = float("inf")

            for i in range(len(polyline) - 1):
                p1 = polyline[i]
                p2 = polyline[i + 1]
                dist = distance_point_to_segment_m(
                    r.latitude, r.longitude,
                    p1[0], p1[1],
                    p2[0], p2[1]
                )
                if dist < min_dist:
                    min_dist = dist

            if min_dist <= threshold_m:
                conflicts.append({
                    "restriction": r,
                    "min_distance_m": round(min_dist, 1),
                    "is_hard_closure": r.is_hard_closure,
                    "road_name": r.road_name,
                    "description": r.description,
                    "type": r.restriction_type.value
                })

        return conflicts

    def calculate_traffic_delay_seconds(
        self,
        summary_roads: List[str]
    ) -> Tuple[float, List[TrafficCondition]]:
        """
        Calculates additional travel time delay caused by verified traffic on route segments.
        """
        delay_sec = 0.0
        matched_conditions = []
        road_names_lower = [r.lower() for r in summary_roads]

        for tc in self._traffic_conditions.values():
            for road in road_names_lower:
                if tc.road_name.lower() in road or road in tc.road_name.lower():
                    delay_sec += tc.delay_minutes * 60.0
                    matched_conditions.append(tc)
                    break

        return delay_sec, matched_conditions

    # =========================================================================
    # REPEATABLE CONTROLLED DEMONSTRATION SCENARIOS (Section 12)
    # Explicitly labeled synthetic fixtures for demonstration and testing.
    # =========================================================================

    def load_demo_scenario(self, scenario_id: int) -> Dict[str, Any]:
        """
        Loads one of the deterministic demonstration scenarios (DEMO DATA — NOT LIVE).
        """
        self.clear_all()
        meta = {"scenario_id": scenario_id, "name": "", "description": ""}

        if scenario_id == 1:
            meta["name"] = "Nominal Road Conditions (Clear Flow)"
            meta["description"] = "All regional highways and arterial roads open with standard travel times."
            self.active_demo_scenario = meta["name"]

        elif scenario_id == 2:
            meta["name"] = "Traffic Congestion on Main Highway (Recalculate to Bypass)"
            meta["description"] = "Heavy congestion delay (+8 mins) on Tenali - Guntur Highway; North Bypass becomes fastest."
            self.add_traffic_condition(TrafficCondition(
                segment_id="DEMO_TRAFFIC_HIGHWAY",
                road_name="Tenali - Guntur Highway",
                severity=TrafficSeverity.HEAVY,
                delay_minutes=8.5,
                speed_factor=0.45,
                source="DEMO_TRAFFIC_TELEMETRY",
                is_demonstration=True
            ))
            self.active_demo_scenario = meta["name"]

        elif scenario_id == 3:
            meta["name"] = "Road Maintenance Closure on Arterial Corridor"
            meta["description"] = "Bridge resurfacing blocks Main Avenue; system hard-excludes corridor and switches to verified alternative."
            self.add_restriction(RoadRestriction(
                restriction_id="DEMO_RESTRICT_MAINTENANCE",
                restriction_type=RestrictionType.ROAD_WORK,
                road_name="Tenali - Guntur Highway",
                latitude=16.2798,
                longitude=80.4568,
                affected_radius_meters=350.0,
                description="Scheduled Asphalt Resurfacing & Bridge Joint Repair",
                is_hard_closure=True,
                source="DEMO_HIGHWAY_AUTHORITY",
                is_demonstration=True
            ))
            self.active_demo_scenario = meta["name"]

        elif scenario_id == 4:
            meta["name"] = "Multi-Objective Preference Shift (Shortest vs Fastest)"
            meta["description"] = "Demonstrates how user preference weights re-rank routes based on time vs distance trade-offs."
            self.active_demo_scenario = meta["name"]

        elif scenario_id == 5:
            meta["name"] = "In-Transit Rerouting Trigger (Dynamic Recalculation)"
            meta["description"] = "Simulates a sudden lane restriction appearing ahead during navigation, triggering automatic reroute."
            self.add_restriction(RoadRestriction(
                restriction_id="DEMO_IN_TRANSIT_RESTRICT",
                restriction_type=RestrictionType.LANE_CLOSURE,
                road_name="Campus Main Avenue",
                latitude=16.2750,
                longitude=80.4850,
                affected_radius_meters=200.0,
                description="Utility Pipe Maintenance Single-Lane Closure",
                is_hard_closure=True,
                source="DEMO_MUNICIPAL_WORKS",
                is_demonstration=True
            ))
            self.active_demo_scenario = meta["name"]

        elif scenario_id == 6:
            meta["name"] = "All Corridors to Destination Restricted (Destination Unreachable)"
            meta["description"] = "Simulates all access approaches closed for municipal maintenance; system refuses to fabricate an unsafe path."
            for idx, (c_lat, c_lon, name) in enumerate([
                (16.3040, 80.4350, "South Approach"),
                (16.3090, 80.4370, "North Approach"),
                (16.3060, 80.4410, "East Approach"),
                (16.3070, 80.4310, "West Approach"),
            ]):
                self.add_restriction(RoadRestriction(
                    restriction_id=f"DEMO_CLOSURE_{idx}",
                    restriction_type=RestrictionType.ROAD_CLOSURE,
                    road_name=name,
                    latitude=c_lat,
                    longitude=c_lon,
                    affected_radius_meters=550.0,
                    description=f"Municipal Infrastructure Work on {name}",
                    is_hard_closure=True,
                    source="DEMO_WORKS_FEED",
                    is_demonstration=True
                ))
            self.active_demo_scenario = meta["name"]

        elif scenario_id == 7:
            meta["name"] = "Accessibility Constraint (Wheelchair Mode)"
            meta["description"] = "Excludes stairs and uneven steps; selects certified wheelchair ramp corridors."
            self.add_restriction(RoadRestriction(
                restriction_id="DEMO_ACCESSIBILITY_BARRIER",
                restriction_type=RestrictionType.STAIRS_NO_RAMP,
                road_name="Campus Pedestrian Walkway",
                latitude=16.2340,
                longitude=80.5510,
                affected_radius_meters=60.0,
                description="Outdoor Staircase without Ramp Access",
                is_hard_closure=True,
                accessible_to_wheelchairs=False,
                source="DEMO_FACILITY_AUDIT",
                is_demonstration=True
            ))
            self.active_demo_scenario = meta["name"]

        elif scenario_id == 8:
            meta["name"] = "Provider Timeout & Offline Fallback"
            meta["description"] = "Simulates external routing server timeout; demonstrates graceful fallback to local road graph."
            self.active_demo_scenario = meta["name"]

        return meta

    def get_demo_scenarios(self) -> List[Dict[str, Any]]:
        """Returns catalog of all 8 controlled demonstration benchmark scenarios."""
        return [
            {"id": 1, "name": "Nominal Road Conditions (Clear Flow)", "description": "All regional highways and arterial roads open with standard travel times."},
            {"id": 2, "name": "Traffic Congestion on Main Highway", "description": "Heavy congestion delay (+8 mins) on Tenali Highway; North Bypass becomes fastest."},
            {"id": 3, "name": "Road Maintenance Closure on Arterial Corridor", "description": "Bridge resurfacing blocks Main Avenue; system hard-excludes corridor and switches to verified alternative."},
            {"id": 4, "name": "Multi-Objective Preference Shift (Shortest vs Fastest)", "description": "Demonstrates how user preference weights re-rank routes based on time vs distance trade-offs."},
            {"id": 5, "name": "In-Transit Rerouting Trigger (Dynamic Recalculation)", "description": "Simulates a sudden lane restriction appearing ahead during navigation, triggering automatic reroute."},
            {"id": 6, "name": "All Corridors to Destination Restricted", "description": "Simulates all access approaches closed for municipal maintenance; system refuses to fabricate an unsafe path."},
            {"id": 7, "name": "Accessibility Constraint (Wheelchair Mode)", "description": "Excludes stairs and uneven steps; selects certified wheelchair ramp corridors."},
            {"id": 8, "name": "Provider Timeout & Offline Fallback", "description": "Simulates external routing server timeout; demonstrates graceful fallback to local road graph."}
        ]

    def get_mode_indicator(self) -> Dict[str, Any]:
        """Provides environment badge metadata."""
        if self.operating_mode == OperatingMode.LIVE_ROUTING:
            return {
                "mode": self.operating_mode.value,
                "label": "🟢 LIVE ROUTING MODE",
                "color": "#10b981",
                "badge_css": "background: rgba(16, 185, 129, 0.18); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4);",
                "description": "Operating on live OpenStreetMap road network and real provider routing data.",
                "is_demo": False
            }
        elif self.operating_mode == OperatingMode.STANDARD_ROUTING:
            return {
                "mode": self.operating_mode.value,
                "label": "🔵 STANDARD ROUTING MODE",
                "color": "#38bdf8",
                "badge_css": "background: rgba(56, 189, 248, 0.18); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4);",
                "description": "Using resilient offline local road network. Zero external network dependency.",
                "is_demo": False
            }
        else:
            return {
                "mode": self.operating_mode.value,
                "label": "🟠 DEMO DATA — NOT LIVE",
                "color": "#f59e0b",
                "badge_css": "background: rgba(245, 158, 11, 0.22); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.6);",
                "description": f"Controlled demonstration environment active ({self.active_demo_scenario or 'Custom Demo'}). Not live traffic.",
                "is_demo": True
            }
