"""
Live Virtual Travel Companion Orchestrator & Session Service
Coordinates navigation sessions, step progression, checkpoint completion,
state machine transitions, and companion telemetry for all transport modes.
"""

from datetime import datetime, timezone
import json
import uuid
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from src.backend.database.models import (
    NavigationSession,
    NavigationRouteStep,
    NavigationCheckpoint,
    NavigationProgressEvent,
    PlaceEntrance
)
from src.backend.navigation.state_machine import NavigationState, NavigationStateMachine
from src.backend.navigation.progress_service import (
    ProgressProcessingService,
    haversine_distance_m,
    calculate_bearing_degrees
)


# Avatar and Animation configuration by mode
MODE_AVATAR_CONFIG = {
    "walking": {
        "avatar_icon": "🚶‍♂️",
        "avatar_name": "Virtual Walking Companion",
        "movement_anim": "walkingStride",
        "default_speed_kmh": 4.8,
        "step_radius_m": 35.0
    },
    "running": {
        "avatar_icon": "🏃‍♂️",
        "avatar_name": "Virtual Human Runner",
        "movement_anim": "runningSprint",
        "default_speed_kmh": 9.5,
        "step_radius_m": 45.0
    },
    "driving": {
        "avatar_icon": "🚗",
        "avatar_name": "Virtual Vehicle Companion",
        "movement_anim": "vehicleDrive",
        "default_speed_kmh": 50.0,
        "step_radius_m": 75.0
    },
    "cycling": {
        "avatar_icon": "🚴",
        "avatar_name": "Virtual Cyclist Guide",
        "movement_anim": "cyclingPedal",
        "default_speed_kmh": 16.0,
        "step_radius_m": 45.0
    },
    "motorcycle": {
        "avatar_icon": "🏍️",
        "avatar_name": "Virtual Motorcyclist",
        "movement_anim": "motorcycleRide",
        "default_speed_kmh": 42.0,
        "step_radius_m": 60.0
    },
    "transit": {
        "avatar_icon": "🚌",
        "avatar_name": "Virtual Public Transit Navigator",
        "movement_anim": "transitGlide",
        "default_speed_kmh": 35.0,
        "step_radius_m": 50.0
    }
}


class CompanionService:
    """
    Core service for managing Navigation Sessions and live companion synchronization.
    """

    @classmethod
    def create_session(
        cls,
        db: Session,
        origin_name: str,
        origin_lat: float,
        origin_lon: float,
        dest_name: str,
        dest_lat: float,
        dest_lon: float,
        travel_mode: str = "walking",
        polyline: Optional[List[List[float]]] = None,
        steps_data: Optional[List[Dict[str, Any]]] = None,
        entrance_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> NavigationSession:
        """
        Initializes a new navigation session with ordered steps and checkpoints.
        """
        mode = travel_mode.lower()
        if mode not in MODE_AVATAR_CONFIG:
            mode = "walking"

        # Default polyline if not provided
        if not polyline or len(polyline) < 2:
            polyline = [
                [origin_lat, origin_lon],
                [(origin_lat + dest_lat) / 2.0, (origin_lon + dest_lon) / 2.0],
                [dest_lat, dest_lon]
            ]

        # Calculate initial total distance
        total_dist_m = 0.0
        for i in range(len(polyline) - 1):
            total_dist_m += haversine_distance_m(
                (polyline[i][0], polyline[i][1]),
                (polyline[i + 1][0], polyline[i + 1][1])
            )

        speed_ms = MODE_AVATAR_CONFIG[mode]["default_speed_kmh"] / 3.6
        total_dur_sec = round(total_dist_m / max(0.5, speed_ms), 0)

        session = NavigationSession(
            user_id=user_id,
            origin_name=origin_name,
            origin_lat=origin_lat,
            origin_lon=origin_lon,
            dest_name=dest_name,
            dest_lat=dest_lat,
            dest_lon=dest_lon,
            entrance_id=entrance_id,
            travel_mode=mode,
            status=NavigationState.ROUTE_READY.value,
            current_step_index=0,
            completed_steps_count=0,
            current_lat=origin_lat,
            current_lon=origin_lon,
            current_speed_kmh=0.0,
            current_heading=calculate_bearing_degrees((origin_lat, origin_lon), (polyline[1][0], polyline[1][1])),
            progress_percent=0.0,
            distance_remaining_meters=total_dist_m,
            duration_remaining_seconds=total_dur_sec,
            total_distance_meters=total_dist_m,
            total_duration_seconds=total_dur_sec,
            polyline_json=polyline,
            metadata_json={"avatar": MODE_AVATAR_CONFIG[mode]}
        )
        db.add(session)
        db.flush()

        # Build route steps
        steps_to_create = []
        if steps_data and len(steps_data) >= 1:
            for idx, s in enumerate(steps_data):
                step_key = f"STEP_{idx}"
                s_dist = float(s.get("distance_m", total_dist_m / len(steps_data)))
                s_dur = float(s.get("duration_s", total_dur_sec / len(steps_data)))
                s_lat = float(s.get("start_lat", polyline[min(idx, len(polyline) - 1)][0]))
                s_lon = float(s.get("start_lon", polyline[min(idx, len(polyline) - 1)][1]))
                e_lat = float(s.get("end_lat", polyline[min(idx + 1, len(polyline) - 1)][0]))
                e_lon = float(s.get("end_lon", polyline[min(idx + 1, len(polyline) - 1)][1]))

                step_obj = NavigationRouteStep(
                    session_id=session.id,
                    route_version=1,
                    sequence_number=idx,
                    step_key=step_key,
                    instruction_type=s.get("type", "STRAIGHT" if idx > 0 else "START"),
                    instruction_text=s.get("instruction", f"Proceed towards {dest_name}"),
                    road_name=s.get("road", "Main Corridor"),
                    start_lat=s_lat,
                    start_lon=s_lon,
                    end_lat=e_lat,
                    end_lon=e_lon,
                    distance_meters=s_dist,
                    duration_seconds=s_dur,
                    is_completed=False,
                    icon=s.get("icon", "📍"),
                    visual_cue=s.get("visual_cue")
                )
                steps_to_create.append(step_obj)
        else:
            # Generate representative steps along polyline
            step_count = min(6, max(3, len(polyline)))
            seg_len = max(1, len(polyline) // step_count)
            for i in range(step_count):
                p_start = polyline[min(i * seg_len, len(polyline) - 1)]
                p_end = polyline[min((i + 1) * seg_len, len(polyline) - 1)]
                leg_dist = haversine_distance_m((p_start[0], p_start[1]), (p_end[0], p_end[1]))
                leg_dur = round(leg_dist / max(0.5, speed_ms), 0)

                if i == 0:
                    instr_type = "START"
                    instr_text = f"Start journey from {origin_name}"
                    icon = "🚩"
                elif i == step_count - 1:
                    instr_type = "ARRIVE"
                    instr_text = f"Arrive at destination: {dest_name}"
                    icon = "🏆"
                else:
                    instr_type = "STRAIGHT" if i % 2 == 1 else "LEFT"
                    instr_text = f"Continue along corridor towards checkpoint {i + 1}"
                    icon = "➡️" if instr_type == "STRAIGHT" else "↩️"

                step_obj = NavigationRouteStep(
                    session_id=session.id,
                    route_version=1,
                    sequence_number=i,
                    step_key=f"STEP_{i}",
                    instruction_type=instr_type,
                    instruction_text=instr_text,
                    road_name=f"Segment {i + 1}",
                    start_lat=p_start[0],
                    start_lon=p_start[1],
                    end_lat=p_end[0],
                    end_lon=p_end[1],
                    distance_meters=round(leg_dist, 1),
                    duration_seconds=leg_dur,
                    is_completed=False,
                    icon=icon
                )
                steps_to_create.append(step_obj)

        db.add_all(steps_to_create)
        db.flush()

        session.total_steps_count = len(steps_to_create)
        if steps_to_create:
            session.current_step_id = steps_to_create[0].id

        # Build Checkpoints (Start, Intermediate, Destination)
        checkpoints_to_create = []
        for idx, step in enumerate(steps_to_create):
            cp_type = "START" if idx == 0 else ("DESTINATION" if idx == len(steps_to_create) - 1 else "TURN")
            cp_badge = "🚩" if idx == 0 else ("🏆" if idx == len(steps_to_create) - 1 else "🛣️")
            cp = NavigationCheckpoint(
                session_id=session.id,
                step_id=step.id,
                checkpoint_type=cp_type,
                name=f"Checkpoint {idx + 1}: {step.instruction_text}",
                latitude=step.start_lat,
                longitude=step.start_lon,
                sequence_number=idx,
                radius_meters=MODE_AVATAR_CONFIG[mode]["step_radius_m"],
                completion_action="AUTO_PROXIMITY",
                is_reached=False,
                display_badge=cp_badge
            )
            checkpoints_to_create.append(cp)

        db.add_all(checkpoints_to_create)
        db.commit()
        db.refresh(session)
        return session

    @classmethod
    def start_session(cls, db: Session, session_id: str) -> NavigationSession:
        """Starts active navigation for a session."""
        session = db.query(NavigationSession).filter_by(id=session_id).first()
        if not session:
            raise ValueError(f"Navigation session {session_id} not found")

        sm = NavigationStateMachine(NavigationState(session.status))
        success, next_state = sm.transition_to(NavigationState.STARTING, "User pressed Start Navigation")
        if success:
            session.status = next_state.value
            session.started_at = datetime.now(timezone.utc)

            event = NavigationProgressEvent(
                session_id=session.id,
                event_type="START",
                state=session.status,
                latitude=session.current_lat,
                longitude=session.current_lon,
                speed_kmh=0.0,
                heading=session.current_heading,
                step_index=0,
                details="Navigation session started"
            )
            db.add(event)
            db.commit()
            db.refresh(session)
        return session

    @classmethod
    def pause_session(cls, db: Session, session_id: str) -> NavigationSession:
        """Pauses an active navigation session."""
        session = db.query(NavigationSession).filter_by(id=session_id).first()
        if not session:
            raise ValueError(f"Navigation session {session_id} not found")

        sm = NavigationStateMachine(NavigationState(session.status))
        success, next_state = sm.transition_to(NavigationState.PAUSED, "User paused navigation")
        if success:
            session.status = next_state.value
            event = NavigationProgressEvent(
                session_id=session.id,
                event_type="PAUSE",
                state=session.status,
                latitude=session.current_lat,
                longitude=session.current_lon,
                speed_kmh=0.0,
                heading=session.current_heading,
                step_index=session.current_step_index,
                details="Navigation paused by user"
            )
            db.add(event)
            db.commit()
            db.refresh(session)
        return session

    @classmethod
    def resume_session(cls, db: Session, session_id: str) -> NavigationSession:
        """Resumes a paused navigation session."""
        session = db.query(NavigationSession).filter_by(id=session_id).first()
        if not session:
            raise ValueError(f"Navigation session {session_id} not found")

        sm = NavigationStateMachine(NavigationState(session.status))
        success, next_state = sm.transition_to(NavigationState.RESUMING, "User resumed navigation")
        if success:
            session.status = next_state.value
            event = NavigationProgressEvent(
                session_id=session.id,
                event_type="RESUME",
                state=session.status,
                latitude=session.current_lat,
                longitude=session.current_lon,
                speed_kmh=session.current_speed_kmh,
                heading=session.current_heading,
                step_index=session.current_step_index,
                details="Navigation resumed"
            )
            db.add(event)
            db.commit()
            db.refresh(session)
        return session

    @classmethod
    def cancel_session(cls, db: Session, session_id: str) -> NavigationSession:
        """Cancels an active navigation session."""
        session = db.query(NavigationSession).filter_by(id=session_id).first()
        if not session:
            raise ValueError(f"Navigation session {session_id} not found")

        session.status = NavigationState.CANCELLED.value
        session.ended_at = datetime.now(timezone.utc)
        event = NavigationProgressEvent(
            session_id=session.id,
            event_type="CANCEL",
            state=session.status,
            latitude=session.current_lat,
            longitude=session.current_lon,
            speed_kmh=0.0,
            heading=session.current_heading,
            step_index=session.current_step_index,
            details="Navigation cancelled"
        )
        db.add(event)
        db.commit()
        db.refresh(session)
        return session

    @classmethod
    def process_location_update(
        cls,
        db: Session,
        session_id: str,
        latitude: float,
        longitude: float,
        speed_kmh: float = 0.0,
        heading: Optional[float] = None,
        accuracy_meters: float = 5.0,
        timestamp: Optional[datetime] = None,
        is_known_traffic_zone: bool = False
    ) -> Dict[str, Any]:
        """
        Receives real-time location observation from client device:
        1. Validates and checks GPS accuracy.
        2. Map-matches coordinate onto active route polyline.
        3. Evaluates state machine transitions (MOVING, TEMPORARILY_STOPPED, TRAFFIC_DELAY, etc.).
        4. Detects checkpoint and step crossings (CHECKED ✅).
        5. Evaluates entrance/destination arrival.
        6. Updates remaining metrics and returns rich companion telemetry.
        """
        session = db.query(NavigationSession).filter_by(id=session_id).first()
        if not session:
            raise ValueError(f"Navigation session {session_id} not found")

        if session.status in (NavigationState.ARRIVED.value, NavigationState.CANCELLED.value):
            return cls.get_session_telemetry(session)

        now = timestamp or datetime.now(timezone.utc)
        polyline = session.polyline_json or []

        # 1. Map-Match Coordinate
        matched_lat, matched_lon, dist_to_route, seg_idx = ProgressProcessingService.match_to_polyline(
            latitude, longitude, polyline
        )

        # Off-Route Check
        off_route_thresh = (
            ProgressProcessingService.OFF_ROUTE_THRESHOLD_DRIVING_M
            if "drive" in session.travel_mode or "car" in session.travel_mode
            else ProgressProcessingService.OFF_ROUTE_THRESHOLD_WALKING_M
        )
        is_off_route = dist_to_route > off_route_thresh

        # 2. Check Arrival at Destination or Entrance
        entrance_coords = None
        if session.entrance_id:
            ent = db.query(PlaceEntrance).filter_by(id=session.entrance_id).first()
            if ent:
                entrance_coords = (ent.latitude, ent.longitude)

        is_arrived, is_at_entrance, arrival_msg = ProgressProcessingService.evaluate_arrival(
            user_lat=latitude,
            user_lon=longitude,
            dest_lat=session.dest_lat,
            dest_lon=session.dest_lon,
            entrance_coords=entrance_coords,
            travel_mode=session.travel_mode,
            accuracy_meters=accuracy_meters
        )

        # 3. Check Maneuver / Turn Proximity
        steps = session.steps
        dist_to_next_turn = None
        is_at_turn = False
        cur_step = steps[session.current_step_index] if session.current_step_index < len(steps) else None

        if cur_step and cur_step.instruction_type in ("LEFT", "RIGHT", "SLIGHT_LEFT", "SLIGHT_RIGHT", "U_TURN"):
            turn_pos = (cur_step.start_lat, cur_step.start_lon)
            d_turn = haversine_distance_m((matched_lat, matched_lon), turn_pos)
            dist_to_next_turn = d_turn
            if d_turn <= 22.0:
                is_at_turn = True

        # 4. Evaluate State Machine
        sm = NavigationStateMachine(NavigationState(session.status))
        sm.consecutive_stops = session.consecutive_stops_count
        sm.consecutive_moving = session.consecutive_moving_count

        new_state = sm.evaluate_observation(
            speed_kmh=speed_kmh,
            accuracy_meters=accuracy_meters,
            dist_to_turn_meters=dist_to_next_turn,
            is_at_turn=is_at_turn,
            is_off_route=is_off_route,
            is_arrived=is_arrived,
            is_known_traffic_zone=is_known_traffic_zone,
            is_manual_paused=(session.status == NavigationState.PAUSED.value)
        )

        # Persist counters
        session.consecutive_stops_count = sm.consecutive_stops
        session.consecutive_moving_count = sm.consecutive_moving
        old_state = session.status
        session.status = new_state.value

        # 5. Checkpoint & Step Completion Evaluation (ONLY when not stopped and not uncertain)
        newly_completed_steps = []
        if new_state not in (NavigationState.GPS_UNCERTAIN, NavigationState.OFF_ROUTE):
            # Checkpoint crossings
            checkpoints = session.checkpoints
            reached_cps = ProgressProcessingService.evaluate_checkpoints(
                matched_lat=matched_lat,
                matched_lon=matched_lon,
                checkpoints=checkpoints,
                current_step_idx=session.current_step_index
            )

            # Step Completion
            for idx in range(session.current_step_index, len(steps)):
                s = steps[idx]
                if s.is_completed:
                    continue

                d_end = haversine_distance_m((matched_lat, matched_lon), (s.end_lat, s.end_lon))
                # Complete if reached end of step or final arrival
                if d_end <= 35.0 or (is_arrived and idx == len(steps) - 1):
                    s.is_completed = True
                    s.completed_at = now
                    newly_completed_steps.append(s)
                    session.completed_steps_count += 1
                    if idx + 1 < len(steps):
                        session.current_step_index = idx + 1
                        session.current_step_id = steps[idx + 1].id
                else:
                    break

        # 6. Calculate Bearing & Metrics
        calc_heading = heading
        if calc_heading is None:
            if seg_idx < len(polyline) - 1:
                p_next = (polyline[seg_idx + 1][0], polyline[seg_idx + 1][1])
                calc_heading = calculate_bearing_degrees((matched_lat, matched_lon), p_next)
            else:
                calc_heading = session.current_heading

        rem_m, rem_sec, prog_pct = ProgressProcessingService.calculate_remaining_metrics(
            matched_lat=matched_lat,
            matched_lon=matched_lon,
            segment_idx=seg_idx,
            polyline=polyline,
            travel_mode=session.travel_mode
        )

        # 7. Update Session State
        session.current_lat = matched_lat
        session.current_lon = matched_lon
        session.current_speed_kmh = speed_kmh
        session.current_heading = calc_heading
        session.accuracy_meters = accuracy_meters
        session.distance_remaining_meters = rem_m
        session.duration_remaining_seconds = rem_sec
        session.progress_percent = 100.0 if is_arrived else prog_pct
        session.is_traffic_delay = (new_state == NavigationState.TRAFFIC_DELAY)

        if is_arrived and not session.ended_at:
            session.ended_at = now
            session.status = NavigationState.ARRIVED.value

        # 8. Record Progress Event (State changes, checkpoint completions, arrival)
        event_type = "MOVEMENT_UPDATE"
        if is_arrived:
            event_type = "ARRIVAL"
        elif new_state != NavigationState(old_state):
            event_type = f"STATE_CHANGE_TO_{new_state.value}"
        elif newly_completed_steps:
            event_type = "STEP_COMPLETED"

        event = NavigationProgressEvent(
            session_id=session.id,
            event_type=event_type,
            state=session.status,
            latitude=matched_lat,
            longitude=matched_lon,
            speed_kmh=speed_kmh,
            heading=calc_heading,
            accuracy_meters=accuracy_meters,
            step_index=session.current_step_index,
            details=arrival_msg or f"Speed: {speed_kmh:.1f} km/h • Remaining: {rem_m:.0f}m"
        )
        db.add(event)
        db.commit()
        db.refresh(session)

        return cls.get_session_telemetry(session, arrival_msg=arrival_msg)

    @classmethod
    def confirm_manual_action(
        cls,
        db: Session,
        session_id: str,
        action_name: str,
        details: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Confirms a manual checkpoint or step action (e.g., boarded bus, passed gate, entered lobby).
        """
        session = db.query(NavigationSession).filter_by(id=session_id).first()
        if not session:
            raise ValueError(f"Navigation session {session_id} not found")

        # Advance step upon manual confirmation
        steps = session.steps
        if session.current_step_index < len(steps):
            cur_s = steps[session.current_step_index]
            cur_s.is_completed = True
            cur_s.completed_at = datetime.now(timezone.utc)
            session.completed_steps_count += 1
            if session.current_step_index + 1 < len(steps):
                session.current_step_index += 1
                session.current_step_id = steps[session.current_step_index].id

        event = NavigationProgressEvent(
            session_id=session.id,
            event_type="MANUAL_ACTION_CONFIRMED",
            state=session.status,
            latitude=session.current_lat,
            longitude=session.current_lon,
            speed_kmh=session.current_speed_kmh,
            heading=session.current_heading,
            step_index=session.current_step_index,
            details=f"Manual action confirmed: {action_name}. {details or ''}"
        )
        db.add(event)
        db.commit()
        db.refresh(session)
        return cls.get_session_telemetry(session)

    @classmethod
    def get_session_telemetry(
        cls,
        session: NavigationSession,
        arrival_msg: str = ""
    ) -> Dict[str, Any]:
        """
        Assembles comprehensive telemetry for frontend Live Virtual Companion.
        """
        mode_cfg = MODE_AVATAR_CONFIG.get(session.travel_mode.lower(), MODE_AVATAR_CONFIG["walking"])
        steps_out = []
        for s in session.steps:
            steps_out.append({
                "id": s.id,
                "sequence_number": s.sequence_number,
                "step_key": s.step_key,
                "instruction_type": s.instruction_type,
                "instruction_text": s.instruction_text,
                "road_name": s.road_name,
                "distance_meters": s.distance_meters,
                "duration_seconds": s.duration_seconds,
                "is_completed": s.is_completed,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                "icon": s.icon,
                "visual_cue": s.visual_cue
            })

        checkpoints_out = []
        for cp in session.checkpoints:
            checkpoints_out.append({
                "id": cp.id,
                "name": cp.name,
                "type": cp.checkpoint_type,
                "sequence_number": cp.sequence_number,
                "latitude": cp.latitude,
                "longitude": cp.longitude,
                "is_reached": cp.is_reached,
                "reached_at": cp.reached_at.isoformat() if cp.reached_at else None,
                "badge": cp.display_badge
            })

        cur_step_obj = steps_out[session.current_step_index] if session.current_step_index < len(steps_out) else None

        return {
            "session_id": session.id,
            "status": session.status,
            "travel_mode": session.travel_mode,
            "avatar": {
                "icon": mode_cfg["avatar_icon"],
                "name": mode_cfg["avatar_name"],
                "animation": mode_cfg["movement_anim"],
                "is_stopped": session.status in (
                    NavigationState.TEMPORARILY_STOPPED.value,
                    NavigationState.TRAFFIC_DELAY.value,
                    NavigationState.PAUSED.value,
                    NavigationState.ARRIVED.value
                ),
                "heading": session.current_heading,
                "speed_kmh": session.current_speed_kmh
            },
            "position": {
                "latitude": session.current_lat,
                "longitude": session.current_lon,
                "heading": session.current_heading,
                "speed_kmh": session.current_speed_kmh,
                "accuracy_meters": session.accuracy_meters
            },
            "route": {
                "origin_name": session.origin_name,
                "dest_name": session.dest_name,
                "entrance_id": session.entrance_id,
                "polyline": session.polyline_json,
                "total_distance_meters": session.total_distance_meters,
                "total_duration_seconds": session.total_duration_seconds,
                "distance_remaining_meters": session.distance_remaining_meters,
                "duration_remaining_seconds": session.duration_remaining_seconds,
                "progress_percent": session.progress_percent
            },
            "timeline": {
                "current_step_index": session.current_step_index,
                "completed_steps_count": session.completed_steps_count,
                "total_steps_count": session.total_steps_count,
                "current_step": cur_step_obj,
                "steps": steps_out,
                "checkpoints": checkpoints_out
            },
            "arrival": {
                "is_arrived": session.status == NavigationState.ARRIVED.value,
                "message": arrival_msg or ("You have arrived safely!" if session.status == NavigationState.ARRIVED.value else "")
            }
        }
