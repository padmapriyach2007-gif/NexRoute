"""
Normalized Multi-Objective Route Scoring and Pareto-Dominance Ranking.
Ensures scale-independent balancing between travel time, distance, and safety.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional
from src.routing.costs import ObjectiveType


@dataclass
class RouteScoringWeights:
    """Configurable weights for multi-objective optimization."""
    time_weight: float = 0.50
    distance_weight: float = 0.50
    safety_weight: float = 0.00
    accessibility_weight: float = 0.00

    def __post_init__(self):
        total = self.time_weight + self.distance_weight + self.safety_weight + self.accessibility_weight
        if total <= 0:
            raise ValueError("Sum of scoring weights must be strictly positive")
        # Normalize weights so they sum to 1.0
        self.time_weight /= total
        self.distance_weight /= total
        self.safety_weight /= total
        self.accessibility_weight /= total


@dataclass
class ScoredRoute:
    route: Any
    rank: int
    normalized_time: float
    normalized_distance: float
    composite_score: float
    is_pareto_optimal: bool
    objective_used: ObjectiveType


class MultiObjectiveRanker:
    """
    Ranks alternative routes using normalized multi-objective scoring.
    Normalizes time and distance to [0, 1] relative to the candidate set:
        score(r) = alpha * norm_time + beta * norm_distance + gamma * safety_penalty
    Lower score is superior.
    Identifies Pareto-efficient candidates where neither time nor distance can be
    improved without degrading the other.
    """

    def __init__(self, default_weights: Optional[RouteScoringWeights] = None):
        self.default_weights = default_weights or RouteScoringWeights()

    def rank_routes(
        self,
        routes: List[Any],
        objective: ObjectiveType = ObjectiveType.BALANCED,
        custom_weights: Optional[RouteScoringWeights] = None
    ) -> List[ScoredRoute]:
        """
        Scores and sorts candidate routes.
        Each candidate route must have .distance_meters and .duration_seconds.
        """
        if not routes:
            return []

        if len(routes) == 1:
            return [ScoredRoute(
                route=routes[0],
                rank=1,
                normalized_time=0.0,
                normalized_distance=0.0,
                composite_score=0.0,
                is_pareto_optimal=True,
                objective_used=objective
            )]

        times = [float(getattr(r, "duration_seconds", 0.0)) for r in routes]
        dists = [float(getattr(r, "distance_meters", 0.0)) for r in routes]

        min_t, max_t = min(times), max(times)
        min_d, max_d = min(dists), max(dists)

        range_t = max_t - min_t
        range_d = max_d - min_d
        eps = 1e-6

        # Determine effective weights based on objective
        if objective == ObjectiveType.FASTEST:
            weights = RouteScoringWeights(time_weight=1.0, distance_weight=0.0)
        elif objective == ObjectiveType.SHORTEST:
            weights = RouteScoringWeights(time_weight=0.0, distance_weight=1.0)
        elif objective == ObjectiveType.BALANCED:
            weights = custom_weights or self.default_weights
        else:
            weights = custom_weights or self.default_weights

        scored_candidates = []
        for r, t, d in zip(routes, times, dists):
            norm_t = (t - min_t) / (range_t + eps) if range_t > 0 else 0.0
            norm_d = (d - min_d) / (range_d + eps) if range_d > 0 else 0.0

            composite = (weights.time_weight * norm_t) + (weights.distance_weight * norm_d)
            scored_candidates.append({
                "route": r,
                "time": t,
                "dist": d,
                "norm_t": round(norm_t, 4),
                "norm_d": round(norm_d, 4),
                "score": round(composite, 5)
            })

        # Identify Pareto non-dominated routes
        for item in scored_candidates:
            t_i, d_i = item["time"], item["dist"]
            dominated = False
            for other in scored_candidates:
                t_j, d_j = other["time"], other["dist"]
                # other dominates item if other is <= in both and < in at least one
                if (t_j <= t_i and d_j <= d_i) and (t_j < t_i or d_j < d_i):
                    dominated = True
                    break
            item["is_pareto"] = not dominated

        # Sort by composite score ascending (lowest score is best)
        scored_candidates.sort(key=lambda x: (x["score"], x["time"], x["dist"]))

        results: List[ScoredRoute] = []
        for idx, item in enumerate(scored_candidates):
            results.append(ScoredRoute(
                route=item["route"],
                rank=idx + 1,
                normalized_time=item["norm_t"],
                normalized_distance=item["norm_d"],
                composite_score=item["score"],
                is_pareto_optimal=item["is_pareto"],
                objective_used=objective
            ))

        return results
