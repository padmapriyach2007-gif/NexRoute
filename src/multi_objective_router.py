"""
Multi-Objective Route Optimization & Trade-Off Scoring Engine for CampusAegis 2.0
Implements normalized mathematical scoring across:
- Travel time (T)
- Travel distance (D)
- User objective preferences (Fastest, Shortest, Balanced, Accessible)
- Verified road restrictions and closures (hard constraints)
Generates dynamic, human-readable trade-off explanations comparing alternatives.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from src.route_engine import RouteOption, TravelMode
from src.road_condition_model import OptimizationObjective, RoadRestriction, TrafficCondition
from src.road_condition_manager import RoadConditionManager
from src.hazard_map import HazardMap


class RouteEligibilityStatus(Enum):
    ELIGIBLE = "ROUTE_ELIGIBLE"
    RESTRICTED_CLOSURE = "ROUTE_RESTRICTED_CLOSURE"
    HAZARD_BLOCKED = "ROUTE_HAZARD_BLOCKED"
    INACCESSIBLE = "ROUTE_INACCESSIBLE"
    NO_ROUTE_AVAILABLE = "NO_ROUTE_AVAILABLE"


@dataclass
class RankedRoute:
    """
    Represents an evaluated and scored route option with clear trade-off rationale.
    """
    route: RouteOption
    rank: int                                  # 1 = Top Recommended
    is_eligible: bool                          # True if no hard constraints violated
    status: RouteEligibilityStatus
    composite_score: float                     # Lower is better (normalized cost)
    effective_duration_minutes: float          # Including traffic delays
    effective_distance_km: float
    time_savings_minutes_vs_slowest: float
    distance_diff_km_vs_shortest: float
    rejection_reasons: List[str] = field(default_factory=list)
    detected_restrictions: List[Dict[str, Any]] = field(default_factory=list)
    detected_hazards: List[Dict[str, Any]] = field(default_factory=list)
    traffic_delays: List[TrafficCondition] = field(default_factory=list)
    is_safe: bool = True
    recommendation_explanation: str = ""       # Dynamic human-readable reason
    key_trade_offs: List[str] = field(default_factory=list)
    accessibility_verified: bool = False
    accessibility_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "route_id": self.route.route_id,
            "name": self.route.name,
            "rank": self.rank,
            "is_eligible": self.is_eligible,
            "is_safe": self.is_safe,
            "status": self.status.value,
            "composite_score": round(self.composite_score, 3),
            "duration_minutes": round(self.effective_duration_minutes, 1),
            "distance_km": round(self.effective_distance_km, 2),
            "time_savings_minutes": round(self.time_savings_minutes_vs_slowest, 1),
            "distance_diff_km": round(self.distance_diff_km_vs_shortest, 2),
            "recommendation_explanation": self.recommendation_explanation,
            "key_trade_offs": self.key_trade_offs,
            "rejection_reasons": self.rejection_reasons,
            "hazard_count": len(self.detected_hazards),
            "summary_roads": self.route.summary_roads,
            "is_accessible": self.route.is_accessible,
            "accessibility_verified": self.accessibility_verified,
            "accessibility_notes": self.accessibility_notes
        }


class MultiObjectiveRouter:
    """
    Evaluates candidate routes against verified road restrictions, spatial hazards,
    traffic conditions, and user multi-objective optimization preferences.
    """

    def __init__(
        self,
        road_condition_manager: Optional[RoadConditionManager] = None,
        hazard_map: Optional[HazardMap] = None
    ):
        self.condition_manager = road_condition_manager or RoadConditionManager()
        self.hazard_map = hazard_map

    def evaluate_and_rank_routes(
        self,
        candidate_routes: List[RouteOption],
        objective: OptimizationObjective = OptimizationObjective.FASTEST,
        require_accessible: bool = False
    ) -> List[RankedRoute]:
        """
        Ranks candidate routes using the normalized multi-objective scoring model:
        Score = w_time * (T / T_min) + w_dist * (D / D_min) + Penalties
        """
        if not candidate_routes:
            return []

        # 1. Weight Configuration based on User Objective
        if objective == OptimizationObjective.FASTEST:
            w_time, w_dist = 0.85, 0.15
        elif objective == OptimizationObjective.SHORTEST:
            w_time, w_dist = 0.15, 0.85
        elif objective == OptimizationObjective.BALANCED:
            w_time, w_dist = 0.50, 0.50
        elif objective == OptimizationObjective.ACCESSIBLE:
            w_time, w_dist = 0.50, 0.50
            require_accessible = True
        else:
            w_time, w_dist = 0.70, 0.30

        # 2. First Pass: Apply Traffic Delays & Detect Hard Restrictions
        evaluated_items = []
        for r in candidate_routes:
            # Check traffic delays
            extra_delay_sec, matched_traffic = self.condition_manager.calculate_traffic_delay_seconds(r.summary_roads)
            total_duration_sec = r.duration_seconds + extra_delay_sec

            # Check road restrictions (closures, roadwork)
            conflicts = self.condition_manager.check_route_restrictions(r.polyline)
            hard_closures = [c for c in conflicts if c["is_hard_closure"]]

            # Check spatial hazards (fire, chemical leaks, floods, structural collapse)
            hazard_conflicts = []
            if self.hazard_map:
                hazard_conflicts = self.hazard_map.check_route_hazards(r.polyline, safety_buffer_m=60.0)

            reasons = []
            is_eligible = True
            is_safe = True
            status = RouteEligibilityStatus.ELIGIBLE

            if hard_closures:
                is_eligible = False
                is_safe = False
                status = RouteEligibilityStatus.RESTRICTED_CLOSURE
                for c in hard_closures:
                    reasons.append(f"Road restriction: {c['road_name']} ({c['description'] or c['type']})")

            if hazard_conflicts:
                is_eligible = False
                is_safe = False
                status = RouteEligibilityStatus.HAZARD_BLOCKED
                for hc in hazard_conflicts:
                    reasons.append(f"Active Hazard: {hc['incident_type']} ({hc['description']}) within {hc['min_distance_m']}m")

            # Check Accessibility Constraints
            if require_accessible and not r.is_accessible:
                is_eligible = False
                status = RouteEligibilityStatus.INACCESSIBLE
                reasons.append("Non-accessible pathway (contains stairs or barriers)")

            evaluated_items.append({
                "route": r,
                "is_eligible": is_eligible,
                "is_safe": is_safe,
                "status": status,
                "reasons": reasons,
                "conflicts": conflicts,
                "hazards": hazard_conflicts,
                "traffic": matched_traffic,
                "duration_min": total_duration_sec / 60.0,
                "distance_km": r.distance_km
            })

        # 3. Normalization Baseline (min time and min distance among eligible routes)
        eligible_items = [item for item in evaluated_items if item["is_eligible"]]
        if eligible_items:
            min_time = min(item["duration_min"] for item in eligible_items)
            min_dist = min(item["distance_km"] for item in eligible_items)
            max_time = max(item["duration_min"] for item in eligible_items)
        else:
            # Fallback when all routes are restricted
            min_time = min(item["duration_min"] for item in evaluated_items)
            min_dist = min(item["distance_km"] for item in evaluated_items)
            max_time = max(item["duration_min"] for item in evaluated_items)

        # Protect against division by zero
        min_time = max(0.1, min_time)
        min_dist = max(0.1, min_dist)

        # 4. Compute Normalized Composite Scores
        for item in evaluated_items:
            norm_time = item["duration_min"] / min_time
            norm_dist = item["distance_km"] / min_dist

            if not item["is_eligible"]:
                score = 999.0 + norm_time
            else:
                score = w_time * norm_time + w_dist * norm_dist
            item["score"] = score

        # 5. Sort: Eligible first by score, then ineligible
        sorted_items = sorted(
            evaluated_items,
            key=lambda x: (not x["is_eligible"], x["score"])
        )

        # 6. Generate Dynamic Explanations and Trade-Off Summaries
        ranked_routes: List[RankedRoute] = []
        for rank_idx, item in enumerate(sorted_items, start=1):
            r = item["route"]
            is_winner = (rank_idx == 1 and item["is_eligible"])

            time_diff = round(item["duration_min"] - min_time, 1)
            dist_diff = round(item["distance_km"] - min_dist, 2)
            time_savings = round(max_time - item["duration_min"], 1)

            # Build Trade-Off Bullet Points
            trade_offs = []
            if not item["is_eligible"]:
                if item["reasons"]:
                    trade_offs.append(f"⛔ {item['reasons'][0]}")
                if time_diff < 0:
                    trade_offs.append(f"⚡ Direct corridor ({abs(time_diff)} mins faster, but blocked)")
                elif time_diff > 0:
                    trade_offs.append(f"⏱️ +{time_diff} mins slower than open routes")
                trade_offs.append("🔄 Rerouted to verified safe corridor")
            else:
                if time_diff == 0:
                    trade_offs.append("⚡ Fastest available option")
                else:
                    trade_offs.append(f"⏱️ +{time_diff} mins slower than fastest route")

                if dist_diff == 0:
                    trade_offs.append("📏 Shortest available path")
                else:
                    trade_offs.append(f"🛣️ +{dist_diff} km longer distance")

                if item["traffic"]:
                    total_delay = sum(tc.delay_minutes for tc in item["traffic"])
                    trade_offs.append(f"🚗 Contains +{round(total_delay, 1)} mins traffic delay")

            # Build Objective Explanation
            if not item["is_eligible"]:
                explanation = f"Excluded: {'; '.join(item['reasons'])}"
            elif is_winner:
                if objective == OptimizationObjective.FASTEST:
                    explanation = f"Recommended: Lowest travel time ({round(item['duration_min'], 1)} mins). Fastest route among available alternatives."
                elif objective == OptimizationObjective.SHORTEST:
                    explanation = f"Recommended: Shortest physical distance ({round(item['distance_km'], 1)} km). Optimizes fuel and travel length."
                elif objective == OptimizationObjective.ACCESSIBLE:
                    if getattr(r, "accessibility_verified", False):
                        explanation = f"Recommended: Certified wheelchair accessible corridor with balanced travel time ({round(item['duration_min'], 1)} mins)."
                    else:
                        explanation = f"Recommended: Best step-free alternative ({round(item['duration_min'], 1)} mins). Note: sidewalk curb cuts and step-free conditions are unverified on general road networks."
                else:
                    explanation = f"Recommended: Optimal balance between travel time ({round(item['duration_min'], 1)} mins) and distance ({round(item['distance_km'], 1)} km)."
            else:
                explanation = f"Alternative Option: {trade_offs[0]} | {trade_offs[1]}."

            ranked_routes.append(RankedRoute(
                route=r,
                rank=rank_idx,
                is_eligible=item["is_eligible"],
                status=item["status"],
                composite_score=item["score"],
                effective_duration_minutes=item["duration_min"],
                effective_distance_km=item["distance_km"],
                time_savings_minutes_vs_slowest=time_savings,
                distance_diff_km_vs_shortest=dist_diff,
                rejection_reasons=item["reasons"],
                detected_restrictions=item["conflicts"],
                detected_hazards=item["hazards"],
                traffic_delays=item["traffic"],
                is_safe=item["is_safe"],
                recommendation_explanation=explanation,
                key_trade_offs=trade_offs,
                accessibility_verified=getattr(r, "accessibility_verified", False),
                accessibility_notes=getattr(r, "accessibility_notes", "")
            ))

        return ranked_routes
