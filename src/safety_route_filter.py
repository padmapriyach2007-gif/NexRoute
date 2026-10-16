"""
Safety Route Filter for CampusAegis / PROJECT AI
Applies two-stage safety-constrained routing:
Stage 1: Hard constraint exclusion (confirmed hazards, closed roads, travel mode violations).
Stage 2: Route optimization & comparative ranking of eligible routes.

Explicitly classifies routes into:
- ROUTE_ELIGIBLE
- ROUTE_CONTAINS_CONFIRMED_HAZARD
- ROUTE_CONTAINS_CLOSURE
- ROUTE_INFORMATION_INSUFFICIENT
- ROUTE_DATA_STALE
- NO_VERIFIED_ROUTE
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from src.hazard_map import HazardMap
from src.route_engine import RouteOption


class RouteSafetyStatus(Enum):
    ROUTE_ELIGIBLE = "ROUTE_ELIGIBLE"
    ROUTE_CONTAINS_CONFIRMED_HAZARD = "ROUTE_CONTAINS_CONFIRMED_HAZARD"
    ROUTE_CONTAINS_CLOSURE = "ROUTE_CONTAINS_CLOSURE"
    ROUTE_INFORMATION_INSUFFICIENT = "ROUTE_INFORMATION_INSUFFICIENT"
    ROUTE_DATA_STALE = "ROUTE_DATA_STALE"
    NO_VERIFIED_ROUTE = "NO_VERIFIED_ROUTE"


@dataclass
class EvaluatedRoute:
    route: RouteOption
    status: RouteSafetyStatus
    is_eligible: bool
    rejection_reasons: List[str] = field(default_factory=list)
    detected_hazards: List[Dict[str, Any]] = field(default_factory=list)
    safety_score: float = 1.0  # 1.0 = verified clean, 0.0 = lethal / impassable
    uncertainty_level: str = "LOW"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "route_id": self.route.route_id,
            "name": self.route.name,
            "mode": self.route.mode.value,
            "distance_km": self.route.distance_km,
            "duration_minutes": self.route.duration_minutes,
            "status": self.status.value,
            "is_eligible": self.is_eligible,
            "rejection_reasons": self.rejection_reasons,
            "hazard_count": len(self.detected_hazards),
            "safety_score": self.safety_score,
            "uncertainty_level": self.uncertainty_level,
        }


class SafetyRouteFilter:
    """
    Evaluates candidate routes against active hazards and road closures.
    Hard safety constraints are NEVER bypassed by distance or speed scores.
    """

    def __init__(self, hazard_map: HazardMap):
        self.hazard_map = hazard_map

    def evaluate_candidate_routes(
        self,
        candidate_routes: List[RouteOption],
        require_accessible: bool = False,
        safety_buffer_m: float = 60.0
    ) -> List[EvaluatedRoute]:
        """
        Evaluates and classifies every candidate route option.
        Returns all evaluated routes, marked as either eligible or excluded with explicit reasons.
        """
        evaluated = []

        for r in candidate_routes:
            reasons = []
            status = RouteSafetyStatus.ROUTE_ELIGIBLE
            is_eligible = True

            # Check Accessibility
            if require_accessible and not r.is_accessible:
                is_eligible = False
                status = RouteSafetyStatus.ROUTE_INFORMATION_INSUFFICIENT
                reasons.append("Route does not guarantee step-free accessibility.")

            # Check Road Closures
            for road in r.summary_roads:
                if road.lower() in self.hazard_map._road_closures:
                    is_eligible = False
                    status = RouteSafetyStatus.ROUTE_CONTAINS_CLOSURE
                    reasons.append(f"Contains officially closed road segment: {road}")

            # Check Spatial Hazards along Polyline
            conflicts = self.hazard_map.check_route_hazards(r.polyline, safety_buffer_m=safety_buffer_m)
            if conflicts:
                is_eligible = False
                status = RouteSafetyStatus.ROUTE_CONTAINS_CONFIRMED_HAZARD
                for c in conflicts:
                    reasons.append(
                        f"Passes within {c['min_distance_m']}m of {c['severity']} {c['incident_type']} ({c['description']})"
                    )

            score = 1.0 if is_eligible else 0.0

            evaluated.append(EvaluatedRoute(
                route=r,
                status=status,
                is_eligible=is_eligible,
                rejection_reasons=reasons,
                detected_hazards=conflicts,
                safety_score=score,
                uncertainty_level="LOW" if not conflicts else "CRITICAL"
            ))

        # Rank eligible routes: shortest distance first
        evaluated.sort(key=lambda x: (not x.is_eligible, x.route.distance_meters))
        return evaluated
