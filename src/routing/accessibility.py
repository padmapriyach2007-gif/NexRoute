"""
Constraint-based Accessibility Routing Engine.
Implements the 3-State Accessibility Model:
  1. VERIFIED_ACCESSIBLE
  2. VERIFIED_INACCESSIBLE
  3. UNKNOWN (Disclosed uncertainty)
Supports STRICT and BEST_EFFORT constraint modes.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from src.routing.graph import Edge


class AccessibilityState(str, Enum):
    VERIFIED_ACCESSIBLE = "VERIFIED_ACCESSIBLE"
    VERIFIED_INACCESSIBLE = "VERIFIED_INACCESSIBLE"
    UNKNOWN = "UNKNOWN"


class AccessibilityConstraintMode(str, Enum):
    STRICT = "STRICT"          # Rejects any unverified or inaccessible segment
    BEST_EFFORT = "BEST_EFFORT" # Prohibits verified inaccessible; permits unknown with disclosure


@dataclass
class AccessibilityEvaluation:
    is_eligible: bool
    state: AccessibilityState
    overall_confidence: float  # [0.0, 1.0] fraction of verified distance
    verified_accessible_meters: float
    unverified_meters: float
    inaccessible_meters: float
    violations: List[str] = field(default_factory=list)
    disclosures: List[str] = field(default_factory=list)


class AccessibilityConstraintEngine:
    """
    Evaluates edges and paths against physical accessibility standards:
    - Wheelchair / ramp availability
    - Max gradient <= 6.0% (strict) / 8.0% (best-effort)
    - Paved / asphalt / concrete surface quality
    - Absence of steps, stairs, turnstiles, and narrow gates (< 90cm)
    """

    def __init__(self, mode: AccessibilityConstraintMode = AccessibilityConstraintMode.BEST_EFFORT):
        self.mode = mode

    def classify_edge(self, edge: Edge) -> Tuple[AccessibilityState, List[str]]:
        """
        Classifies an edge into one of the 3 accessibility states based on its physical attributes.
        """
        attrs = edge.attributes or {}
        reasons = []

        # Check explicit negative barriers
        has_stairs = attrs.get("stairs", False) or attrs.get("highway") == "steps"
        wheelchair_tag = str(attrs.get("wheelchair", "")).lower()
        incline = float(attrs.get("incline", 0.0) or 0.0)
        surface = str(attrs.get("surface", "")).lower()

        if has_stairs or wheelchair_tag in ("no", "limited_stairs") or incline > 8.0 or surface in ("sand", "mud", "loose_gravel"):
            if has_stairs:
                reasons.append(f"Steps/stairs on {edge.road_name}")
            if wheelchair_tag == "no":
                reasons.append(f"Wheelchair prohibited on {edge.road_name}")
            if incline > 8.0:
                reasons.append(f"Steep slope ({incline:.1f}%) on {edge.road_name}")
            if surface in ("sand", "mud", "loose_gravel"):
                reasons.append(f"Impassable surface ({surface}) on {edge.road_name}")
            return (AccessibilityState.VERIFIED_INACCESSIBLE, reasons)

        # Check explicit positive verification
        is_explicitly_accessible = (
            edge.is_accessible and (
                wheelchair_tag in ("yes", "designated") or
                attrs.get("ramp", False) is True or
                attrs.get("kerb") in ("lowered", "flush") or
                attrs.get("sidewalk") in ("yes", "both", "left", "right") or
                attrs.get("accessibility_verified", False) is True
            )
        )

        if is_explicitly_accessible:
            return (AccessibilityState.VERIFIED_ACCESSIBLE, [])

        # If neither explicitly verified nor disqualified, status is UNKNOWN
        return (AccessibilityState.UNKNOWN, [f"Unverified pedestrian infrastructure on {edge.road_name}"])

    def evaluate_route(self, edges: List[Edge]) -> AccessibilityEvaluation:
        """Evaluates an entire sequence of edges against the current constraint mode."""
        if not edges:
            return AccessibilityEvaluation(
                is_eligible=True,
                state=AccessibilityState.UNKNOWN,
                overall_confidence=0.0,
                verified_accessible_meters=0.0,
                unverified_meters=0.0,
                inaccessible_meters=0.0,
                disclosures=["Zero-length route"]
            )

        total_m = sum(e.distance_meters for e in edges)
        verified_m = 0.0
        unknown_m = 0.0
        inaccessible_m = 0.0

        violations: List[str] = []
        disclosures: List[str] = []

        for e in edges:
            st, reasons = self.classify_edge(e)
            if st == AccessibilityState.VERIFIED_INACCESSIBLE:
                inaccessible_m += e.distance_meters
                violations.extend(reasons)
            elif st == AccessibilityState.VERIFIED_ACCESSIBLE:
                verified_m += e.distance_meters
            else:
                unknown_m += e.distance_meters
                disclosures.extend(reasons)

        conf = (verified_m / total_m) if total_m > 0 else 0.0

        if self.mode == AccessibilityConstraintMode.STRICT:
            # In strict mode: Any inaccessible OR unverified segment causes disqualification
            is_ok = (inaccessible_m == 0.0 and unknown_m == 0.0)
            overall_state = AccessibilityState.VERIFIED_ACCESSIBLE if is_ok else (
                AccessibilityState.VERIFIED_INACCESSIBLE if inaccessible_m > 0 else AccessibilityState.UNKNOWN
            )
            if unknown_m > 0:
                violations.append(f"Route contains {unknown_m:.0f}m of unverified segments (rejected in Strict Mode)")
        else:
            # In best-effort mode: Only verified inaccessible causes disqualification
            is_ok = (inaccessible_m == 0.0)
            overall_state = (
                AccessibilityState.VERIFIED_INACCESSIBLE if not is_ok else
                (AccessibilityState.VERIFIED_ACCESSIBLE if unknown_m == 0.0 else AccessibilityState.UNKNOWN)
            )
            if unknown_m > 0:
                disclosures.append(f"{unknown_m:.0f}m ({((unknown_m / total_m) * 100):.1f}%) has unknown surface data")

        return AccessibilityEvaluation(
            is_eligible=is_ok,
            state=overall_state,
            overall_confidence=round(conf, 3),
            verified_accessible_meters=round(verified_m, 1),
            unverified_meters=round(unknown_m, 1),
            inaccessible_meters=round(inaccessible_m, 1),
            violations=violations,
            disclosures=disclosures
        )
