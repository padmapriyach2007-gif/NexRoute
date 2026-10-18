"""
Road Condition Service
Handles report creation with duplicate clustering, community confirmations,
status lifecycle management, and audit tracking.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from src.hazard_map import haversine_distance_m
from src.backend.config import settings
from src.backend.database.models import (
    RoadConditionReport, ReportConfirmation, ReportAuditLog
)
from src.backend.road_intelligence.reliability_scorer import ReliabilityScorer
from src.backend.road_intelligence.spatial_query import (
    find_reports_in_radius, find_reports_along_corridor
)


class RoadConditionService:
    @staticmethod
    def create_or_corroborate_report(
        db: Session,
        reporter_id: Optional[str],
        reporter_type: str,
        category: str,
        severity: str,
        latitude: float,
        longitude: float,
        description: str,
        road_name: Optional[str] = None,
        photo_url: Optional[str] = None,
        affected_radius_meters: float = 50.0
    ) -> Tuple[RoadConditionReport, bool]:
        """
        Creates a new road report or corroborates an existing nearby report.
        Returns (report, is_new_report).
        """
        # Duplicate detection check: find active reports of same category within duplicate threshold
        nearby = find_reports_in_radius(
            db, latitude, longitude, settings.REPORT_DUPLICATE_DISTANCE_METERS, include_pending=True
        )
        
        duplicate_match = None
        for r, dist in nearby:
            if r.category.upper() == category.upper() and r.status in ("PENDING", "VERIFIED"):
                duplicate_match = r
                break

        if duplicate_match:
            # Corroborate existing report instead of creating duplicate clutter
            duplicate_match.upvotes += 1
            conf = ReportConfirmation(
                report_id=duplicate_match.id,
                user_id=reporter_id,
                confirmation_type="STILL_PRESENT",
                notes=f"Corroborating report: {description[:100]}"
            )
            db.add(conf)

            # Recalculate confidence
            duplicate_match.confidence_score = ReliabilityScorer.calculate_confidence_score(
                duplicate_match.reporter_type,
                duplicate_match.created_at,
                duplicate_match.upvotes,
                duplicate_match.downvotes,
                duplicate_match.dispute_count,
                is_verified_by_admin=(duplicate_match.reporter_type in ("POLICE", "MUNICIPAL", "VERIFIED_OPERATOR"))
            )

            # Update status if threshold met
            new_status = ReliabilityScorer.determine_status_transition(
                duplicate_match.status, duplicate_match.confidence_score,
                duplicate_match.dispute_count, is_expired=False
            )
            if new_status != duplicate_match.status:
                audit = ReportAuditLog(
                    report_id=duplicate_match.id,
                    action="STATUS_CHANGED",
                    old_status=duplicate_match.status,
                    new_status=new_status,
                    performed_by="SYSTEM_CONSENSUS",
                    details={"reason": "Community confirmations reached confidence threshold"}
                )
                db.add(audit)
                duplicate_match.status = new_status
                if new_status == "VERIFIED":
                    duplicate_match.verified_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(duplicate_match)
            return duplicate_match, False

        # Create brand-new report
        created_now = datetime.now(timezone.utc)
        expires_at = ReliabilityScorer.calculate_default_expiration(category, created_now)
        initial_confidence = ReliabilityScorer.calculate_confidence_score(
            reporter_type, created_now, upvotes=1, downvotes=0, dispute_count=0,
            is_verified_by_admin=(reporter_type in ("POLICE", "MUNICIPAL", "VERIFIED_OPERATOR"))
        )

        initial_status = "VERIFIED" if initial_confidence >= 0.85 else "PENDING"
        verified_time = created_now if initial_status == "VERIFIED" else None

        new_report = RoadConditionReport(
            reporter_id=reporter_id,
            reporter_type=reporter_type,
            category=category.upper(),
            severity=severity.upper(),
            status=initial_status,
            latitude=latitude,
            longitude=longitude,
            affected_radius_meters=affected_radius_meters,
            road_name=road_name,
            description=description,
            photo_url=photo_url,
            confidence_score=initial_confidence,
            upvotes=1,
            downvotes=0,
            dispute_count=0,
            created_at=created_now,
            expires_at=expires_at,
            verified_at=verified_time
        )
        db.add(new_report)
        db.flush()

        audit = ReportAuditLog(
            report_id=new_report.id,
            action="CREATED",
            old_status=None,
            new_status=initial_status,
            performed_by=reporter_type,
            details={"initial_confidence": initial_confidence}
        )
        db.add(audit)
        db.commit()
        db.refresh(new_report)
        return new_report, True

    @staticmethod
    def confirm_or_dispute_report(
        db: Session,
        report_id: str,
        user_id: Optional[str],
        confirmation_type: str,
        notes: Optional[str] = None
    ) -> RoadConditionReport:
        report = db.query(RoadConditionReport).filter(RoadConditionReport.id == report_id).first()
        if not report:
            raise ValueError(f"Report {report_id} not found")

        conf = ReportConfirmation(
            report_id=report.id,
            user_id=user_id,
            confirmation_type=confirmation_type.upper(),
            notes=notes
        )
        db.add(conf)

        if confirmation_type.upper() in ("STILL_PRESENT", "CONFIRM"):
            report.upvotes += 1
        elif confirmation_type.upper() in ("CLEARED", "RESOLVED"):
            report.status = "RESOLVED"
            report.resolved_at = datetime.now(timezone.utc)
        elif confirmation_type.upper() in ("DISPUTE", "ABUSE"):
            report.downvotes += 1
            report.dispute_count += 1

        # Recalculate confidence
        report.confidence_score = ReliabilityScorer.calculate_confidence_score(
            report.reporter_type,
            report.created_at,
            report.upvotes,
            report.downvotes,
            report.dispute_count,
            is_verified_by_admin=(report.reporter_type in ("POLICE", "MUNICIPAL", "VERIFIED_OPERATOR"))
        )

        new_status = ReliabilityScorer.determine_status_transition(
            report.status, report.confidence_score, report.dispute_count, is_expired=False
        )
        if new_status != report.status:
            audit = ReportAuditLog(
                report_id=report.id,
                action="STATUS_CHANGED",
                old_status=report.status,
                new_status=new_status,
                performed_by=user_id or "COMMUNITY",
                details={"confirmation_type": confirmation_type, "new_confidence": report.confidence_score}
            )
            db.add(audit)
            report.status = new_status
            if new_status == "VERIFIED":
                report.verified_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def expire_stale_reports(db: Session) -> int:
        """Batch job to transition past-expiry reports to EXPIRED status."""
        now = datetime.now(timezone.utc)
        stale = db.query(RoadConditionReport).filter(
            RoadConditionReport.status.in_(["PENDING", "VERIFIED"]),
            RoadConditionReport.expires_at <= now
        ).all()

        count = len(stale)
        for r in stale:
            r.status = "EXPIRED"
            audit = ReportAuditLog(
                report_id=r.id,
                action="EXPIRED",
                old_status="VERIFIED",
                new_status="EXPIRED",
                performed_by="CRON_EXPIRATION_WORKER",
                details={"expired_at": now.isoformat()}
            )
            db.add(audit)
        db.commit()
        return count
