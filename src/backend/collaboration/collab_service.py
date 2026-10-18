"""
Collaborative Maps & Trip Planning Service
Manages multi-user shared itineraries, stop sequencing, destination voting,
collaborative notes, role-based access control, and audit logs.
"""

import secrets
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from src.backend.database.models import (
    CollaborativeMap, MapMember, CollaborativeStop, StopVote, CollabAuditLog, User
)


class CollaborativeService:
    @staticmethod
    def create_collaborative_map(
        db: Session,
        owner_id: str,
        title: str,
        description: Optional[str] = None
    ) -> CollaborativeMap:
        token = secrets.token_urlsafe(24)
        collab_map = CollaborativeMap(
            owner_id=owner_id,
            title=title,
            description=description,
            share_token=token
        )
        db.add(collab_map)
        db.flush()

        # Add owner as OWNER member
        owner_member = MapMember(
            map_id=collab_map.id,
            user_id=owner_id,
            role="OWNER"
        )
        db.add(owner_member)

        # Audit log
        audit = CollabAuditLog(
            map_id=collab_map.id,
            user_id=owner_id,
            action="MAP_CREATED",
            details={"title": title}
        )
        db.add(audit)
        db.commit()
        db.refresh(collab_map)
        return collab_map

    @staticmethod
    def add_stop(
        db: Session,
        map_id: str,
        user_id: str,
        title: str,
        latitude: float,
        longitude: float,
        notes: Optional[str] = None,
        sequence_order: Optional[int] = None
    ) -> CollaborativeStop:
        # Check permissions
        member = db.query(MapMember).filter(
            MapMember.map_id == map_id, MapMember.user_id == user_id
        ).first()
        if not member or member.role not in ("OWNER", "EDITOR"):
            raise PermissionError("User does not have editor permission for this collaborative map")

        # Determine sequence order if not specified
        if sequence_order is None:
            existing_count = db.query(CollaborativeStop).filter(
                CollaborativeStop.map_id == map_id
            ).count()
            sequence_order = existing_count + 1

        stop = CollaborativeStop(
            map_id=map_id,
            suggested_by_id=user_id,
            title=title,
            latitude=latitude,
            longitude=longitude,
            notes=notes,
            sequence_order=sequence_order
        )
        db.add(stop)
        db.flush()

        audit = CollabAuditLog(
            map_id=map_id,
            user_id=user_id,
            action="ADD_STOP",
            details={"stop_id": stop.id, "title": title}
        )
        db.add(audit)
        db.commit()
        db.refresh(stop)
        return stop

    @staticmethod
    def vote_on_stop(
        db: Session,
        stop_id: str,
        user_id: str,
        vote_value: int
    ) -> CollaborativeStop:
        stop = db.query(CollaborativeStop).filter(CollaborativeStop.id == stop_id).first()
        if not stop:
            raise ValueError(f"Stop {stop_id} not found")

        existing_vote = db.query(StopVote).filter(
            StopVote.stop_id == stop_id, StopVote.user_id == user_id
        ).first()

        if existing_vote:
            existing_vote.vote_value = vote_value
        else:
            vote = StopVote(stop_id=stop_id, user_id=user_id, vote_value=vote_value)
            db.add(vote)

        db.flush()

        # Recalculate total vote score
        all_votes = db.query(StopVote).filter(StopVote.stop_id == stop_id).all()
        stop.vote_score = sum(v.vote_value for v in all_votes)

        db.commit()
        db.refresh(stop)
        return stop
