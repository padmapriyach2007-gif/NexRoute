"""
Reliability Scorer & Expiry Policy for Road Condition Reports
Implements multi-factor reliability scoring (freshness decay, reporter trust, community consensus)
and automated category-based lifecycle expiration.
"""

import math
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Tuple


CATEGORY_EXPIRATION_HOURS = {
    "ACCIDENT": 3,
    "BROKEN_SIGNAL": 8,
    "FLOODING": 12,
    "ROAD_CLOSURE": 168,      # 7 days
    "POTHOLE": 336,           # 14 days
    "DANGEROUS_TURN": 720,    # 30 days
    "PEDESTRIAN_HAZARD": 48,
    "POOR_LIGHTING": 336      # 14 days
}

REPORTER_BASE_WEIGHTS = {
    "POLICE": 0.98,
    "MUNICIPAL": 0.98,
    "VERIFIED_OPERATOR": 0.95,
    "SENSOR": 0.90,
    "TRUSTED_REPORTER": 0.80,
    "COMMUNITY": 0.50
}


class ReliabilityScorer:
    @staticmethod
    def calculate_default_expiration(category: str, created_at: datetime = None) -> datetime:
        base_time = created_at or datetime.now(timezone.utc)
        hours = CATEGORY_EXPIRATION_HOURS.get(category.upper(), 24)
        return base_time + timedelta(hours=hours)

    @staticmethod
    def calculate_confidence_score(
        reporter_type: str,
        created_at: datetime,
        upvotes: int,
        downvotes: int,
        dispute_count: int,
        is_verified_by_admin: bool = False
    ) -> float:
        """
        Calculates confidence score in range [0.05, 0.99] using:
        Confidence = BaseWeight * FreshnessFactor + CommunityConsensus - DisputePenalty
        """
        if is_verified_by_admin:
            return 0.98

        base_weight = REPORTER_BASE_WEIGHTS.get(reporter_type.upper(), 0.50)
        
        # Calculate freshness decay (half-life of 24 hours)
        now = datetime.now(timezone.utc)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        elapsed_hours = max(0.0, (now - created_at).total_seconds() / 3600.0)
        freshness_decay = math.exp(-0.028 * elapsed_hours)  # drops to ~0.5 after 24 hrs
        
        # Community consensus bonus (each confirmation adds weight, capped at +0.35)
        consensus_bonus = min(0.35, max(0, upvotes - 1) * 0.08)
        
        # Dispute and abuse penalty
        dispute_penalty = (downvotes * 0.10) + (dispute_count * 0.20)
        
        raw_score = (base_weight * freshness_decay) + consensus_bonus - dispute_penalty
        return round(max(0.05, min(0.99, raw_score)), 2)

    @staticmethod
    def determine_status_transition(
        current_status: str,
        confidence_score: float,
        dispute_count: int,
        is_expired: bool
    ) -> str:
        """Determines the appropriate lifecycle status for a report."""
        if is_expired:
            return "EXPIRED"
        if dispute_count >= 3 or confidence_score < 0.25:
            return "REJECTED"
        if confidence_score >= 0.75:
            return "VERIFIED"
        return current_status
