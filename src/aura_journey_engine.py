"""
P.A.T.H.F.I.N.D.E.R. • AURA Complete Start-to-Destination Journey Experience Engine
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Human-Centric Visual Journey System

Orchestrates the complete 19-stage end-to-end interactive journey experience featuring
Aura (the 3D robot companion) from initial welcome and location input to dynamic
turn-by-turn navigation, maneuver guide, storybook gallery, and arrival celebration.
"""

import os
import json
import math
import base64
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple, Union


class AuraJourneyStage(str, Enum):
    """The 19 stages of the end-to-end journey experience."""
    WELCOME = "WELCOME"
    START_INPUT = "START_INPUT"
    START_CONFIRMED = "START_CONFIRMED"
    DEST_INPUT = "DEST_INPUT"
    DEST_CONFIRMED = "DEST_CONFIRMED"
    MODE_SELECT = "MODE_SELECT"
    CALCULATING_ROUTES = "CALCULATING_ROUTES"
    ALTERNATIVES_READY = "ALTERNATIVES_READY"
    ROUTE_CHOSEN = "ROUTE_CHOSEN"
    ROUTE_OVERVIEW = "ROUTE_OVERVIEW"
    JOURNEY_CONFIRMED = "JOURNEY_CONFIRMED"
    NAVIGATING = "NAVIGATING"
    MANEUVER_APPROACHING = "MANEUVER_APPROACHING"
    LANDMARK_DISCOVERED = "LANDMARK_DISCOVERED"
    OFF_ROUTE = "OFF_ROUTE"
    NEAR_DESTINATION = "NEAR_DESTINATION"
    ARRIVED = "ARRIVED"
    JOURNEY_SUMMARY = "JOURNEY_SUMMARY"


class AuraPose(str, Enum):
    """Aura's distinct 3D / graphic character poses."""
    WELCOME = "welcome"
    POINTING = "pointing"
    THINKING = "thinking"
    EXCITED = "excited"
    TALKING = "talking"
    WAVING = "waving"


@dataclass
class AuraManeuverStep:
    """Rich maneuver model for every individual turn on the journey."""
    step_num: int
    total_steps: int
    direction_type: str  # START, STRAIGHT, LEFT, RIGHT, SLIGHT_LEFT, SLIGHT_RIGHT, SHARP_LEFT, SHARP_RIGHT, KEEP_LEFT, KEEP_RIGHT, MERGE, ROUNDABOUT, U_TURN, CROSSING, ARRIVE
    headline: str
    instruction: str
    spoken_text: str
    aura_speech: str
    road_name: str
    distance_m: float
    distance_human: str
    time_estimate: str
    icon: str
    aura_pose: AuraPose = AuraPose.TALKING
    what_to_look_for: str = ""
    accessible_guidance: str = ""
    roundabout_exit: Optional[int] = None
    coordinates: Optional[List[float]] = None
    status: str = "UPCOMING"  # COMPLETED, ACTIVE, UPCOMING


class AuraPoseAssetManager:
    """Manages cached base64 URIs for Aura's mascot poses."""
    _poses: Dict[str, str] = {}
    _loaded: bool = False

    @classmethod
    def load_poses(cls) -> Dict[str, str]:
        if cls._loaded and cls._poses:
            return cls._poses

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        poses_json_path = os.path.join(base_dir, "data", "mascot_poses_trans.json")
        assets_dir = os.path.join(base_dir, "assets")

        loaded = {}
        if os.path.exists(poses_json_path):
            try:
                with open(poses_json_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
            except Exception:
                pass

        # Fallback to direct PNG files in assets
        pose_files = {
            "welcome": "mascot_welcome_trans.png",
            "pointing": "mascot_pointing_trans.png",
            "thinking": "mascot_thinking_trans.png",
            "excited": "mascot_excited_trans.png",
            "talking": "mascot_talking_trans.png",
            "waving": "mascot_waving.png"
        }

        for pose_key, filename in pose_files.items():
            if pose_key not in loaded or not loaded[pose_key]:
                fpath = os.path.join(assets_dir, filename)
                if not os.path.exists(fpath):
                    fpath = os.path.join(assets_dir, filename.replace("_trans", "_clean"))
                if os.path.exists(fpath):
                    try:
                        with open(fpath, "rb") as img_file:
                            b64 = base64.b64encode(img_file.read()).decode("utf-8")
                            loaded[pose_key] = f"data:image/png;base64,{b64}"
                    except Exception:
                        pass

        cls._poses = loaded
        cls._loaded = True
        return cls._poses

    @classmethod
    def get_pose_uri(cls, pose: Union[AuraPose, str]) -> str:
        poses = cls.load_poses()
        key = pose.value if isinstance(pose, AuraPose) else str(pose).lower()
        return poses.get(key) or poses.get("welcome") or ""


class AuraSpeechGenerator:
    """Generates warm, expressive speech and thoughts matching actual journey events."""

    @staticmethod
    def get_speech_for_stage(stage: AuraJourneyStage, context: Optional[Dict[str, Any]] = None) -> Tuple[str, AuraPose]:
        ctx = context or {}
        orig = ctx.get("origin", "Start")
        dest = ctx.get("destination", "Destination")
        mode = ctx.get("travel_mode", "car").lower()
        dist = ctx.get("distance_km", "")
        time_est = ctx.get("duration_mins", "")

        if stage == AuraJourneyStage.WELCOME:
            return (
                "Hey, traveler! I'm Aura, your NexRoute companion. Where shall our adventure begin?",
                AuraPose.WAVING
            )
        elif stage == AuraJourneyStage.START_INPUT:
            return (
                "Let's choose our starting point. You can enter an address, a landmark, or use your current location.",
                AuraPose.POINTING
            )
        elif stage == AuraJourneyStage.START_CONFIRMED:
            return (
                f"Great! I've got our starting point at {orig}. Now let's choose where we're heading.",
                AuraPose.TALKING
            )
        elif stage == AuraJourneyStage.DEST_INPUT:
            return (
                "Where would you like to go? Tell me your destination and I'll help plan the journey.",
                AuraPose.POINTING
            )
        elif stage == AuraJourneyStage.DEST_CONFIRMED:
            return (
                f"Destination selected: {dest}! Let's find a suitable route.",
                AuraPose.THINKING
            )
        elif stage == AuraJourneyStage.MODE_SELECT:
            return (
                "How would you like to travel? I'll adjust the route to match your choice.",
                AuraPose.POINTING
            )
        elif stage == AuraJourneyStage.ALTERNATIVES_READY:
            return (
                "I've found some ways to get there. Let's choose the route that works best for you.",
                AuraPose.TALKING
            )
        elif stage == AuraJourneyStage.ROUTE_OVERVIEW:
            return (
                f"Route ready! {dist} km across approximately {time_est} mins. Ready to begin?",
                AuraPose.THINKING
            )
        elif stage == AuraJourneyStage.JOURNEY_CONFIRMED:
            return (
                "Ready? Let's begin our adventure. I'll guide you step by step.",
                AuraPose.WAVING
            )
        elif stage == AuraJourneyStage.NAVIGATING:
            return (
                "Our adventure is underway! Following the mapped corridor safely.",
                AuraPose.TALKING
            )
        elif stage == AuraJourneyStage.MANEUVER_APPROACHING:
            next_turn = ctx.get("next_turn", "the upcoming junction")
            return (
                f"We're getting closer to {next_turn}. Check the road signs ahead.",
                AuraPose.POINTING
            )
        elif stage == AuraJourneyStage.LANDMARK_DISCOVERED:
            landmark = ctx.get("landmark_name", "an interesting place")
            return (
                f"I found a landmark you might enjoy: {landmark} is just along our route!",
                AuraPose.TALKING
            )
        elif stage == AuraJourneyStage.OFF_ROUTE:
            return (
                "It looks like we're off the planned route. Let's find the way back.",
                AuraPose.THINKING
            )
        elif stage == AuraJourneyStage.NEAR_DESTINATION:
            return (
                f"Our destination {dest} is just ahead! Preparing for arrival.",
                AuraPose.TALKING
            )
        elif stage == AuraJourneyStage.ARRIVED:
            return (
                "We made it! You've reached your destination. Would you like to explore nearby places or plan your next adventure?",
                AuraPose.EXCITED
            )
        else:
            return ("Guiding you safely along your journey.", AuraPose.TALKING)


class ManeuverSequenceBuilder:
    """Builds the complete ordered sequence of maneuvers from actual route data."""

    @staticmethod
    def build_sequence(
        steps: List[Any],
        origin_label: str,
        dest_label: str,
        total_distance_m: float,
        travel_mode: str = "car"
    ) -> List[AuraManeuverStep]:
        clean_orig = origin_label.split(",")[0].strip() or "Departure Point"
        clean_dest = dest_label.split(",")[0].strip() or "Destination"

        if not steps or len(steps) < 2:
            # Fallback when provider returns empty steps list
            return [
                AuraManeuverStep(
                    step_num=1,
                    total_steps=3,
                    direction_type="START",
                    headline=f"Depart from {clean_orig}",
                    instruction=f"Head out from {clean_orig} along the main access corridor.",
                    spoken_text=f"Welcome! Let's begin our journey from {clean_orig}.",
                    aura_speech="Hello traveler! I am Aura, your companion. Let's head out together!",
                    road_name="Departure Access Corridor",
                    distance_m=round(total_distance_m * 0.15, 1),
                    distance_human=f"{round(total_distance_m * 0.15 / 1000.0, 1)} km",
                    time_estimate="2 mins",
                    icon="🟢",
                    aura_pose=AuraPose.WAVING,
                    what_to_look_for="Access gate, navigation signs, and paved roadway.",
                    status="ACTIVE"
                ),
                AuraManeuverStep(
                    step_num=2,
                    total_steps=3,
                    direction_type="STRAIGHT",
                    headline="Continue along Connecting Highway",
                    instruction=f"Follow the main corridor toward {clean_dest}.",
                    spoken_text=f"Continue straight ahead along the main road toward {clean_dest}.",
                    aura_speech="Cruising smoothly! The route ahead is clear and verified by satellite telemetry.",
                    road_name="Main Regional Highway",
                    distance_m=round(total_distance_m * 0.70, 1),
                    distance_human=f"{round(total_distance_m * 0.70 / 1000.0, 1)} km",
                    time_estimate="6 mins",
                    icon="⬆️",
                    aura_pose=AuraPose.TALKING,
                    what_to_look_for="Highway mile markers and overhead direction gantries.",
                    status="UPCOMING"
                ),
                AuraManeuverStep(
                    step_num=3,
                    total_steps=3,
                    direction_type="ARRIVE",
                    headline=f"Arrive safely at {clean_dest}",
                    instruction=f"Arrive at {clean_dest} terminal entrance plaza.",
                    spoken_text=f"You have safely arrived at {clean_dest}. Journey complete!",
                    aura_speech="Hooray! We made it! Thank you for traveling with NexRoute and Aura!",
                    road_name="Arrival Plaza Drive",
                    distance_m=round(total_distance_m * 0.15, 1),
                    distance_human="150 m",
                    time_estimate="1 min",
                    icon="🏁",
                    aura_pose=AuraPose.EXCITED,
                    what_to_look_for="Destination arrival arch, visitor parking, and main entrance.",
                    status="UPCOMING"
                )
            ]

        maneuvers: List[AuraManeuverStep] = []
        total_count = len(steps)

        for idx, s in enumerate(steps):
            step_no = idx + 1
            road = ""
            instruction = ""
            distance_m = 0.0

            # Handle object, dict, or dataclass instances (including FriendlyTurnStep)
            if isinstance(s, dict):
                road = s.get("road") or s.get("road_name") or "Regional Corridor"
                action_headline = s.get("action_headline")
                instruction = s.get("instruction") or action_headline or f"Continue along {road}"
                distance_m = float(s.get("distance_m", 0.0) or s.get("distance_meters", 0.0) or s.get("distance", 0.0))
                dir_type = s.get("direction_type") or s.get("type") or "STRAIGHT"
                icon = s.get("icon") or "⬆️"
                aura_speech_in = s.get("virtual_guide_speech") or s.get("spoken_text")
                look_for_in = s.get("what_to_look_for")
                dist_human_in = s.get("distance_human")
                time_est_in = s.get("time_estimate")
            else:
                road = getattr(s, "road_name", None) or getattr(s, "road", "Regional Corridor")
                action_headline = getattr(s, "action_headline", None)
                instruction = getattr(s, "instruction", None) or action_headline or f"Continue along {road}"
                distance_m = float(getattr(s, "distance_meters", 0.0) or getattr(s, "distance_m", 0.0) or getattr(s, "distance", 0.0))
                dir_type = getattr(s, "direction_type", None) or getattr(s, "type", "STRAIGHT")
                icon = getattr(s, "icon", "⬆️")
                aura_speech_in = getattr(s, "virtual_guide_speech", None) or getattr(s, "spoken_text", None)
                look_for_in = getattr(s, "what_to_look_for", None)
                dist_human_in = getattr(s, "distance_human", None)
                time_est_in = getattr(s, "time_estimate", None)

            # Combined analysis of direction, headline, and instruction text
            dir_str = str(dir_type).upper()
            action_head_str = str(action_headline or "").upper()
            instr_str = str(instruction or "").upper()
            combined_desc = f"{dir_str} {action_head_str} {instr_str}"

            exit_num = s.get("exit") if isinstance(s, dict) else getattr(s, "exit", None)
            pose = AuraPose.TALKING

            if step_no == 1 or "START" in combined_desc or "DEPART" in combined_desc:
                dir_upper = "START"
                icon = "🟢"
                pose = AuraPose.WAVING
                headline = action_headline or f"Depart from {clean_orig}"
                aura_msg = aura_speech_in or f"Ready to roll! We're departing {clean_orig}. Follow my lead!"
            elif step_no == total_count or "ARRIV" in combined_desc or "DEST" in combined_desc:
                dir_upper = "ARRIVE"
                icon = "🏁" if not icon or icon == "⬆️" else icon
                pose = AuraPose.EXCITED
                headline = action_headline or f"Arrive safely at {clean_dest}"
                aura_msg = aura_speech_in or f"We've arrived at {clean_dest}! Awesome travel adventure!"
            elif "ROUNDABOUT" in combined_desc:
                dir_upper = "ROUNDABOUT"
                icon = "🔄"
                pose = AuraPose.POINTING
                exit_str = f"take exit {exit_num} onto " if exit_num else "onto "
                headline = action_headline or f"Enter Roundabout and {exit_str}{road}"
                aura_msg = aura_speech_in or f"Entering roundabout. Yield to traffic and take exit {exit_num or 1} toward {road}."
            elif "KEEP" in combined_desc and "RIGHT" in combined_desc:
                dir_upper = "KEEP_RIGHT"
                icon = "↗️"
                pose = AuraPose.POINTING
                headline = action_headline or f"Keep Right toward {road}"
                aura_msg = aura_speech_in or f"Keep right along {road}."
            elif "KEEP" in combined_desc and "LEFT" in combined_desc:
                dir_upper = "KEEP_LEFT"
                icon = "↖️"
                pose = AuraPose.POINTING
                headline = action_headline or f"Keep Left toward {road}"
                aura_msg = aura_speech_in or f"Keep left along {road}."
            elif "LEFT" in combined_desc:
                dir_upper = "TURN_LEFT"
                icon = "⬅️"
                pose = AuraPose.POINTING
                headline = action_headline or f"Turn Left onto {road}"
                aura_msg = aura_speech_in or f"Prepare to turn left onto {road}. Signal early and check mirrors."
            elif "RIGHT" in combined_desc:
                dir_upper = "TURN_RIGHT"
                icon = "➡️"
                pose = AuraPose.POINTING
                headline = action_headline or f"Turn Right onto {road}"
                aura_msg = aura_speech_in or f"Approaching a right turn onto {road}. Keep to the right side of the road."
            elif "MERGE" in combined_desc:
                dir_upper = "MERGE"
                icon = "🔀"
                pose = AuraPose.POINTING
                headline = action_headline or f"Merge onto {road}"
                aura_msg = aura_speech_in or f"Merge smoothly onto {road} matching corridor speed."
            elif "FOLLOW" in combined_desc or "PROCEED" in combined_desc:
                dir_upper = "PROCEED"
                icon = "🧭" if not icon or icon == "⬆️" else icon
                pose = AuraPose.TALKING
                headline = action_headline or f"Follow {road}"
                aura_msg = aura_speech_in or f"Follow along {road}. Stay steady on course."
            else:
                dir_upper = "STRAIGHT"
                icon = "⬆️"
                pose = AuraPose.TALKING
                headline = action_headline or f"Proceed Straight on {road}"
                aura_msg = aura_speech_in or f"Cruising along {road}. The path is clear."

            dist_human = dist_human_in if dist_human_in else (f"{round(distance_m / 1000.0, 1)} km" if distance_m >= 1000.0 else f"{int(distance_m)} m")
            mins = max(1, round(distance_m / 450.0)) if "walk" in travel_mode.lower() else max(1, round(distance_m / 800.0))
            time_est = time_est_in if time_est_in else f"{mins} min{'s' if mins > 1 else ''}"
            look_for = look_for_in or f"Signposts for {road} and clear pedestrian markings."

            maneuvers.append(AuraManeuverStep(
                step_num=step_no,
                total_steps=total_count,
                direction_type=dir_upper,
                headline=headline,
                instruction=instruction,
                spoken_text=f"Step {step_no}: {headline}. {instruction}",
                aura_speech=aura_msg,
                road_name=road,
                distance_m=distance_m,
                distance_human=dist_human,
                time_estimate=time_est,
                icon=icon,
                aura_pose=pose,
                what_to_look_for=look_for,
                accessible_guidance="Step-free pathway with audible signal crosswalk.",
                roundabout_exit=int(exit_num) if exit_num else None,
                status="ACTIVE" if step_no == 1 else "UPCOMING"
            ))

        return maneuvers


def build_aura_journey_cockpit_html(
    origin_name: str,
    dest_name: str,
    travel_mode: str,
    total_distance_km: float,
    total_duration_mins: float,
    maneuvers: List[AuraManeuverStep],
    current_step_idx: int = 0,
    aura_stage: str = "NAVIGATING",
    aura_thought: str = "Our adventure is underway! Following the mapped corridor safely.",
    is_live_moving: bool = False,
    user_speed_kmh: float = 0.0,
    camera_mode: str = "drone",  # pov, drone, iso
    env_lighting: str = "day"    # day, sunset, night
) -> str:
    """
    Renders the complete high-fidelity Aura 3D / 2.5D Journey Cockpit HTML5/CSS3/JavaScript.
    Features:
    - Aura's animated Robot Mascot with glowing navigation stick & speech bubble
    - Dynamic Route Journey Pipeline showing all ordered maneuvers
    - Active maneuver banner with real distance countdown
    - 3D camera switcher (Driver POV, 3D Follow Drone, 3D Isometric Level)
    - Environment lighting switcher (Day, Sunset, Cyber Night)
    - Avatar action controls (Walk, Run, Turn, Jump, Cheer, Wave)
    - Integrated View All Pictures Journey Storybook Modal
    - Live audio synthesizer chime and SpeechSynthesis narration
    """
    poses = AuraPoseAssetManager.load_poses()
    mascot_waving = poses.get("waving", "")
    mascot_pointing = poses.get("pointing", "")
    mascot_excited = poses.get("excited", "")
    mascot_talking = poses.get("talking", "")
    mascot_welcome = poses.get("welcome", "")

    # Clean display strings
    clean_orig = origin_name.split(",")[0].strip() or "Starting Point"
    clean_dest = dest_name.split(",")[0].strip() or "Destination"

    # Real-time local timezone day / sunset / night detection
    from datetime import datetime
    now_dt = datetime.now()
    cur_hour = now_dt.hour + now_dt.minute / 60.0
    if 17.25 <= cur_hour < 19.35:
        auto_detected_env = "sunset"
        time_desc = f"{now_dt.strftime('%I:%M %p')} • Sunset"
    elif 6.0 <= cur_hour < 17.25:
        auto_detected_env = "day"
        time_desc = f"{now_dt.strftime('%I:%M %p')} • Day"
    else:
        auto_detected_env = "night"
        time_desc = f"{now_dt.strftime('%I:%M %p')} • Cyber Night"

    if env_lighting == "day" or not env_lighting:
        env_lighting = auto_detected_env

    # Serialize maneuvers for JavaScript reactivity
    maneuvers_payload = [asdict(m) for m in maneuvers]
    maneuvers_json = json.dumps(maneuvers_payload, default=str)

    active_step = maneuvers[current_step_idx] if 0 <= current_step_idx < len(maneuvers) else maneuvers[0]

    return f"""
    <div id='aura-journey-root' class='aura-journey-shell'>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap');

            html, body {{
                margin: 0 !important;
                padding: 0 !important;
                background: transparent !important;
                overflow-x: hidden !important;
                box-sizing: border-box !important;
            }}

            .aura-journey-shell {{
                font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: linear-gradient(135deg, #070f1e 0%, #0c1a30 50%, #061022 100%);
                border: 1.5px solid rgba(56, 189, 248, 0.45);
                border-radius: 20px;
                padding: 20px;
                margin: 0 0 10px 0;
                color: #f8fafc;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.85), 0 0 30px rgba(56, 189, 248, 0.15);
                position: relative;
                overflow: visible !important;
                box-sizing: border-box !important;
            }}

            /* Ambient glowing aura rings in background */
            .aura-journey-shell::before {{
                content: '';
                position: absolute;
                top: -80px;
                right: -80px;
                width: 240px;
                height: 240px;
                background: radial-gradient(circle, rgba(56, 189, 248, 0.18) 0%, transparent 70%);
                pointer-events: none;
            }}

            /* Top Stage & Header HUD */
            .aura-header-hud {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 12px;
                padding-bottom: 16px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.12);
            }}

            .aura-brand-group {{
                display: flex;
                align-items: center;
                gap: 14px;
            }}

            .aura-avatar-pod {{
                position: relative;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(56, 189, 248, 0.4) 0%, rgba(15, 23, 42, 0.95) 100%);
                border: 2.5px solid #38bdf8;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 0 20px rgba(56, 189, 248, 0.6);
                cursor: pointer;
                transition: transform 0.3s ease;
            }}
            .aura-avatar-pod:hover {{
                transform: scale(1.08);
            }}
            .aura-avatar-pod img {{
                width: 52px;
                height: 52px;
                object-fit: contain;
                filter: drop-shadow(0 0 6px rgba(56, 189, 248, 0.8));
            }}

            .aura-title-block {{
                display: flex;
                flex-direction: column;
                gap: 2px;
            }}

            .aura-stage-pill {{
                padding: 4px 12px;
                border-radius: 999px;
                font-size: 0.72rem;
                font-weight: 800;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: rgba(16, 185, 129, 0.2);
                color: #34d399;
                border: 1px solid rgba(16, 185, 129, 0.5);
            }}

            /* Interactive Aura Thought Bubble */
            .aura-thought-banner {{
                margin: 14px 0 10px 0;
                background: linear-gradient(90deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.7) 100%);
                border-left: 4px solid #38bdf8;
                border-radius: 12px;
                padding: 12px 18px;
                display: flex;
                align-items: center;
                gap: 14px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
            }}
            .aura-thought-text {{
                font-size: 0.90rem;
                font-weight: 600;
                color: #e2e8f0;
                line-height: 1.4;
                flex: 1;
            }}

            /* Real-Time Sensor Motion & Parallel Movement HUD Ribbon */
            .sensor-motion-hud {{
                margin: 0 0 14px 0;
                background: linear-gradient(90deg, rgba(15, 23, 42, 0.96) 0%, rgba(30, 41, 59, 0.92) 100%);
                border: 1px solid rgba(56, 189, 248, 0.35);
                border-radius: 12px;
                padding: 10px 16px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 12px;
                box-shadow: 0 4px 18px rgba(0, 0, 0, 0.45);
                flex-wrap: wrap;
            }}
            .sensor-motion-left, .sensor-motion-right {{
                display: flex;
                align-items: center;
                gap: 10px;
                flex-wrap: wrap;
            }}
            .sensor-status-badge {{
                display: inline-flex;
                align-items: center;
                gap: 7px;
                padding: 4px 11px;
                border-radius: 999px;
                font-size: 0.72rem;
                font-weight: 800;
                letter-spacing: 0.05em;
                background: rgba(100, 116, 139, 0.2);
                color: #94a3b8;
                border: 1px solid rgba(148, 163, 184, 0.4);
                transition: all 0.3s ease;
            }}
            .sensor-status-badge.moving {{
                background: rgba(16, 185, 129, 0.22);
                color: #34d399;
                border-color: rgba(16, 185, 129, 0.6);
                box-shadow: 0 0 12px rgba(16, 185, 129, 0.35);
            }}
            .sensor-status-badge.stationary {{
                background: rgba(245, 158, 11, 0.2);
                color: #fbbf24;
                border-color: rgba(245, 158, 11, 0.5);
            }}
            .sensor-status-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #94a3b8;
            }}
            .sensor-status-badge.moving .sensor-status-dot {{
                background: #10b981;
                box-shadow: 0 0 8px #10b981;
                animation: pulseSensorDot 1.4s infinite;
            }}
            .sensor-status-badge.stationary .sensor-status-dot {{
                background: #f59e0b;
            }}
            @keyframes pulseSensorDot {{
                0% {{ opacity: 1; transform: scale(1); }}
                50% {{ opacity: 0.35; transform: scale(1.3); }}
                100% {{ opacity: 1; transform: scale(1); }}
            }}
            .sensor-metric-chip {{
                display: inline-flex;
                align-items: center;
                gap: 5px;
                padding: 4px 10px;
                border-radius: 8px;
                background: rgba(15, 23, 42, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                font-size: 0.75rem;
            }}
            .sensor-step-countdown {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 4px 12px;
                border-radius: 8px;
                background: rgba(8, 47, 73, 0.6);
                border: 1px solid rgba(56, 189, 248, 0.35);
                font-size: 0.75rem;
            }}

            /* Dynamic Route Journey Pipeline (Horizontal Scroll) */
            .journey-pipeline-section {{
                margin: 16px 0;
            }}
            .pipeline-label-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 0.74rem;
                font-weight: 800;
                color: #94a3b8;
                letter-spacing: 0.05em;
                margin-bottom: 8px;
            }}
            .pipeline-track {{
                display: flex;
                gap: 10px;
                overflow-x: auto;
                padding: 6px 2px 12px 2px;
                scrollbar-width: thin;
                scrollbar-color: #38bdf8 rgba(15, 23, 42, 0.8);
            }}
            .pipeline-step-card {{
                flex: 0 0 195px;
                min-width: 195px;
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.92) 0%, rgba(10, 18, 36, 0.98) 100%);
                border: 1.5px solid rgba(255, 255, 255, 0.12);
                border-radius: 14px;
                padding: 0;
                cursor: pointer;
                transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                box-shadow: 0 6px 18px rgba(0, 0, 0, 0.45);
            }}
            .pipeline-step-card:hover {{
                border-color: #38bdf8;
                transform: translateY(-4px);
                box-shadow: 0 12px 28px rgba(56, 189, 248, 0.35);
            }}
            .pipeline-step-card.active {{
                border-color: #38bdf8;
                background: linear-gradient(180deg, rgba(2, 132, 199, 0.35) 0%, rgba(15, 23, 42, 0.98) 100%);
                box-shadow: 0 0 22px rgba(56, 189, 248, 0.6), 0 8px 24px rgba(0, 0, 0, 0.6);
            }}
            .pipeline-step-card.completed {{
                border-color: #10b981;
                background: linear-gradient(180deg, rgba(6, 78, 59, 0.35) 0%, rgba(15, 23, 42, 0.98) 100%);
                box-shadow: 0 0 16px rgba(16, 185, 129, 0.4);
            }}
            .step-picture-frame {{
                position: relative;
                width: 100%;
                height: 92px;
                overflow: hidden;
                background: #0f172a;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            }}
            .step-picture-frame svg {{
                transition: transform 0.4s ease;
            }}
            .pipeline-step-card:hover .step-picture-frame svg {{
                transform: scale(1.05);
            }}
            .step-pic-overlay-badge {{
                position: absolute;
                top: 6px;
                left: 6px;
                right: 6px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                pointer-events: none;
            }}
            .step-num-pill {{
                background: rgba(15, 23, 42, 0.85);
                backdrop-filter: blur(4px);
                border: 1px solid rgba(56, 189, 248, 0.6);
                color: #38bdf8;
                font-size: 0.68rem;
                font-weight: 800;
                padding: 2px 7px;
                border-radius: 999px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.5);
            }}
            .pipeline-step-card.active .step-num-pill {{
                background: #0284c7;
                color: #ffffff;
                border-color: #38bdf8;
                box-shadow: 0 0 10px #38bdf8;
            }}
            .pipeline-step-card.completed .step-num-pill {{
                background: #059669;
                color: #ffffff;
                border-color: #34d399;
            }}
            .step-icon-badge {{
                font-size: 1.05rem;
                filter: drop-shadow(0 2px 4px rgba(0,0,0,0.6));
            }}
            .step-card-body {{
                padding: 8px 10px 10px 10px;
                display: flex;
                flex-direction: column;
                gap: 3px;
                flex: 1;
                justify-content: space-between;
            }}
            .step-card-headline {{
                font-size: 0.78rem;
                font-weight: 700;
                color: #f1f5f9;
                line-height: 1.3;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
                overflow: hidden;
                min-height: 2.1em;
            }}
            .pipeline-step-card.active .step-card-headline {{
                color: #38bdf8;
            }}
            .pipeline-step-card.completed .step-card-headline {{
                color: #6ee7b7;
            }}
            .step-card-footer {{
                font-size: 0.67rem;
                color: #94a3b8;
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 4px;
                padding-top: 4px;
                border-top: 1px solid rgba(255, 255, 255, 0.06);
            }}
            .step-card-road {{
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 110px;
            }}
            .step-card-dist {{
                color: #38bdf8;
                font-weight: 800;
            }}

            /* Active Turn-by-Turn Card */
            .active-maneuver-stage {{
                background: rgba(15, 23, 42, 0.8);
                border: 2px solid #38bdf8;
                border-radius: 16px;
                padding: 18px;
                margin: 14px 0;
                display: flex;
                align-items: center;
                gap: 18px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
            }}
            .maneuver-big-icon {{
                width: 64px;
                height: 64px;
                border-radius: 14px;
                background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2.2rem;
                box-shadow: 0 0 16px rgba(56, 189, 248, 0.6);
            }}
            .maneuver-details {{
                flex: 1;
            }}
            .maneuver-headline {{
                font-size: 1.15rem;
                font-weight: 800;
                color: #ffffff;
            }}
            .maneuver-sub {{
                font-size: 0.85rem;
                color: #94a3b8;
                margin-top: 4px;
            }}
            .maneuver-dist-badge {{
                font-size: 1.6rem;
                font-weight: 900;
                color: #34d399;
                font-family: 'JetBrains Mono', monospace;
                text-align: right;
            }}

            /* 3D Scene Viewport */
            .aura-3d-scene-container {{
                position: relative;
                width: 100%;
                height: 360px;
                border-radius: 14px;
                overflow: hidden;
                margin: 14px 0;
                border: 1.5px solid rgba(56, 189, 248, 0.4);
                box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.85), 0 8px 24px rgba(0, 0, 0, 0.5);
                background: radial-gradient(circle at 50% 30%, #1e40af 0%, #030712 100%);
            }}
            #aura-threejs-canvas {{
                width: 100%;
                height: 100%;
                display: block;
            }}
            .scene-hud-overlay {{
                position: absolute;
                top: 10px;
                left: 14px;
                display: flex;
                gap: 8px;
                pointer-events: none;
                z-index: 10;
            }}
            .scene-badge {{
                background: rgba(15, 23, 42, 0.85);
                border: 1px solid rgba(16, 185, 129, 0.5);
                color: #34d399;
                font-size: 0.68rem;
                font-weight: 800;
                padding: 3px 8px;
                border-radius: 6px;
                display: flex;
                align-items: center;
                gap: 6px;
            }}
            .scene-cam-badge {{
                background: rgba(15, 23, 42, 0.85);
                border: 1px solid rgba(56, 189, 248, 0.4);
                color: #38bdf8;
                font-size: 0.68rem;
                font-weight: 800;
                padding: 3px 8px;
                border-radius: 6px;
            }}
            .pulse-dot {{
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: #34d399;
                box-shadow: 0 0 8px #34d399;
            }}

            /* Action Buttons & 3D Controls */
            .controls-toolbar {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 14px;
                padding-top: 14px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .btn-action-pill {{
                background: rgba(30, 41, 59, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 999px;
                padding: 6px 14px;
                font-size: 0.78rem;
                font-weight: 700;
                color: #f1f5f9;
                cursor: pointer;
                transition: all 0.2s ease;
                display: inline-flex;
                align-items: center;
                gap: 6px;
            }}
            .btn-action-pill:hover {{
                background: rgba(56, 189, 248, 0.25);
                border-color: #38bdf8;
                color: #38bdf8;
            }}
            .btn-action-pill.active {{
                background: #0284c7;
                border-color: #38bdf8;
                color: #ffffff;
                box-shadow: 0 0 12px rgba(56, 189, 248, 0.5);
            }}

            /* View All Pictures Modal */
            .gallery-modal-overlay {{
                display: none;
                position: fixed;
                inset: 0;
                background: rgba(3, 7, 18, 0.88);
                backdrop-filter: blur(8px);
                z-index: 99999;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .gallery-modal-card {{
                background: linear-gradient(135deg, #070f1e 0%, #0b172a 100%);
                border: 2px solid #38bdf8;
                border-radius: 20px;
                width: 92%;
                max-width: 1040px;
                max-height: 88vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                box-shadow: 0 24px 64px rgba(0, 0, 0, 0.9), 0 0 40px rgba(56, 189, 248, 0.25);
            }}
            .gallery-header {{
                padding: 16px 22px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: rgba(15, 23, 42, 0.8);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .gallery-content-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
                gap: 18px;
                padding: 22px;
                overflow-y: auto;
            }}
            .gallery-card-item {{
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(10, 18, 36, 0.98) 100%);
                border: 1.5px solid rgba(255, 255, 255, 0.12);
                border-radius: 16px;
                padding: 0;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                cursor: pointer;
            }}
            .gallery-card-item:hover {{
                border-color: #38bdf8;
                transform: translateY(-4px) scale(1.015);
                box-shadow: 0 16px 36px rgba(56, 189, 248, 0.35);
            }}
            .gallery-card-item.active {{
                border-color: #38bdf8;
                box-shadow: 0 0 24px rgba(56, 189, 248, 0.6);
            }}
        </style>

        <!-- Top Header & Brand -->
        <div class='aura-header-hud'>
            <div class='aura-brand-group'>
                <div class='aura-avatar-pod' onclick='triggerAuraAction("wave")' title='Click Aura to Wave!'>
                    <img id='aura-pod-img' src='{mascot_waving or mascot_welcome}' alt='Aura 3D Companion' />
                </div>
                <div class='aura-title-block'>
                    <div style='font-size: 1.05rem; font-weight: 900; color: #ffffff; display: flex; align-items: center; gap: 8px;'>
                        <span>AURA • 3D JOURNEY COMPANION</span>
                        <span class='aura-stage-pill'>● {aura_stage}</span>
                    </div>
                    <div style='font-size: 0.78rem; color: #94a3b8;'>
                        Guiding from <b>{clean_orig}</b> to <b>{clean_dest}</b> ({total_distance_km:.1f} km • ~{int(total_duration_mins)} min)
                    </div>
                </div>
            </div>

            <!-- Header Quick Actions -->
            <div style='display: flex; gap: 8px; align-items: center;'>
                <button class='btn-action-pill' onclick='toggleVoiceAudio()'>
                    <span id='audio-icon'>🔊</span> <span id='audio-text'>Voice: On</span>
                </button>
                <button class='btn-action-pill' onclick='openPicturesGallery()'>
                    <span>🖼️</span> <span>View All Pictures</span>
                </button>
            </div>
        </div>

        <!-- Aura Speech / Thoughts Banner -->
        <div class='aura-thought-banner'>
            <div style='font-size: 1.8rem;'>🤖</div>
            <div class='aura-thought-text' id='aura-thought-box'>
                <span style='color: #38bdf8; font-weight: 800;'>Aura says: </span>
                <span id='aura-speech-content'>{aura_thought}</span>
            </div>
        </div>

        <!-- Real-Time User Sensor Motion & Parallel Guide HUD Ribbon -->
        <div class='sensor-motion-hud' id='sensor-motion-hud-panel'>
            <div class='sensor-motion-left'>
                <div class='sensor-status-badge' id='sensor-status-badge'>
                    <span class='sensor-status-dot' id='sensor-status-dot'></span>
                    <span id='sensor-status-text'>SENSOR MOTION: STANDBY</span>
                </div>
                <div class='sensor-metric-chip'>
                    <span style='color: #94a3b8; font-size: 0.70rem;'>SPEED:</span>
                    <span id='sensor-speed-val' style='font-family: "JetBrains Mono", monospace; font-weight: 800; color: #38bdf8;'>0.0</span>
                    <span style='color: #94a3b8; font-size: 0.70rem;'>km/h</span>
                </div>
                <div class='sensor-metric-chip' id='sensor-cadence-chip'>
                    <span style='color: #94a3b8; font-size: 0.70rem;'>SOURCE:</span>
                    <span id='sensor-source-val' style='color: #a78bfa; font-weight: 700;'>🛰️ GPS & Accel</span>
                </div>
            </div>
            <div class='sensor-motion-right'>
                <div class='sensor-step-countdown'>
                    <span style='color: #94a3b8; font-size: 0.70rem;'>NEXT TURN STEP:</span>
                    <span id='step-remaining-dist' style='font-family: "JetBrains Mono", monospace; font-weight: 800; color: #34d399;'>{active_step.distance_human}</span>
                    <span id='step-countdown-time' style='font-size: 0.72rem; color: #67e8f9;'> (auto)</span>
                </div>
                <button class='btn-action-pill' id='btn-internal-move-toggle' onclick='toggleInternalMoveInParallel()' style='font-weight: 800; background: rgba(56, 189, 248, 0.2); border-color: rgba(56, 189, 248, 0.5);'>
                    <span id='btn-move-icon'>▶</span> <span id='btn-move-label'>Move in Parallel</span>
                </button>
            </div>
        </div>

        <!-- Dynamic Route Journey Pipeline (Every Turn Represented) -->
        <div class='journey-pipeline-section'>
            <div class='pipeline-label-row'>
                <span>ROUTE JOURNEY PIPELINE ({len(maneuvers)} ORDERED STEPS)</span>
                <span>STEP <span id='hud-active-step'>{current_step_idx + 1}</span> OF {len(maneuvers)}</span>
            </div>
            <div class='pipeline-track' id='pipeline-track-container'>
                <!-- Dynamically populated via JS -->
            </div>
        </div>

        <!-- 3D Three.js Animated Scene Viewport with Aura -->
        <div class='aura-3d-scene-container' id='aura-3d-scene-box'>
            <canvas id='aura-threejs-canvas'></canvas>
            <div class='scene-hud-overlay'>
                <div class='scene-badge'><span class='pulse-dot'></span> 3D RUNTIME ACTIVE</div>
                <div class='scene-cam-badge' id='hud-cam-mode'>CAM: 3D FOLLOW DRONE</div>
                <div class='scene-cam-badge' id='hud-env-mode'>ENV: DAY</div>
            </div>
        </div>

        <!-- Active Turn-by-Turn Maneuver Stage -->
        <div class='active-maneuver-stage' id='active-maneuver-box'>
            <div class='maneuver-big-icon' id='stage-icon'>{active_step.icon}</div>
            <div class='maneuver-details'>
                <div class='maneuver-headline' id='stage-headline'>{active_step.headline}</div>
                <div class='maneuver-sub' id='stage-sub'>{active_step.road_name} • {active_step.instruction}</div>
                <div style='font-size: 0.75rem; color: #38bdf8; margin-top: 4px;' id='stage-look'>👀 {active_step.what_to_look_for}</div>
            </div>
            <div>
                <div class='maneuver-dist-badge' id='stage-dist'>{active_step.distance_human}</div>
                <div style='font-size: 0.72rem; color: #94a3b8; text-align: right;' id='stage-time'>~{active_step.time_estimate}</div>
            </div>
        </div>

        <!-- 3D Camera & Avatar Action Toolbar -->
        <div class='controls-toolbar'>
            <!-- Avatar Actions -->
            <div style='display: flex; gap: 6px; align-items: center;'>
                <span style='font-size: 0.72rem; font-weight: 700; color: #94a3b8;'>AURA ACTIONS:</span>
                <button class='btn-action-pill' onclick='triggerAuraAction("walk")'>🚶 Walk</button>
                <button class='btn-action-pill' onclick='triggerAuraAction("run")'>🏃 Run</button>
                <button class='btn-action-pill' onclick='triggerAuraAction("jump")'>✨ Jump</button>
                <button class='btn-action-pill' onclick='triggerAuraAction("wave")'>👋 Wave</button>
            </div>

            <!-- 3D Camera Modes -->
            <div style='display: flex; gap: 6px; align-items: center;'>
                <span style='font-size: 0.72rem; font-weight: 700; color: #94a3b8;'>3D CAMERA:</span>
                <button id='cam-pov' class='btn-action-pill' onclick='setCameraPerspective("pov")'>🎥 Driver POV</button>
                <button id='cam-drone' class='btn-action-pill active' onclick='setCameraPerspective("drone")'>🚁 3D Follow Drone</button>
                <button id='cam-iso' class='btn-action-pill' onclick='setCameraPerspective("iso")'>🗺️ 3D Isometric</button>
            </div>

            <!-- Environment Lighting with Real-Time Zone Automatic Sync -->
            <div style='display: flex; gap: 6px; align-items: center;'>
                <span style='font-size: 0.72rem; font-weight: 700; color: #94a3b8;'>ENVIRONMENT:</span>
                <button id='env-auto' class='btn-action-pill active' onclick='toggleAutoRealTimeEnv()' title='Sync 3D Sky directly with real local timezone clock'>⚡ Auto ({time_desc})</button>
                <button id='env-day' class='btn-action-pill' onclick='setEnvLight("day")'>☀️ Day</button>
                <button id='env-sunset' class='btn-action-pill' onclick='setEnvLight("sunset")'>🌅 Sunset</button>
                <button id='env-night' class='btn-action-pill' onclick='setEnvLight("night")'>🌙 Cyber Night</button>
            </div>
        </div>

        <!-- View All Pictures Journey Storybook Modal -->
        <div id='pictures-modal' class='gallery-modal-overlay' onclick='if(event.target===this)closePicturesGallery()'>
            <div class='gallery-modal-card'>
                <div class='gallery-header'>
                    <div style='font-weight: 900; font-size: 1.1rem; color: #38bdf8; display: flex; align-items: center; gap: 8px;'>
                        <span>🖼️</span> <span>VIEW ALL PICTURES: COMPLETE ROUTE STORY</span>
                    </div>
                    <button class='btn-action-pill' onclick='closePicturesGallery()'>✕ Close</button>
                </div>
                <div class='gallery-content-grid' id='gallery-grid-items'>
                    <!-- Dynamically populated via JS -->
                </div>
            </div>
        </div>
    </div>

    <!-- Load Three.js library for high-performance 3D companion runtime -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

    <script>
    (function() {{
        const MANEUVERS = {maneuvers_json};
        let activeIdx = {current_step_idx};
        let isVoiceOn = true;
        let activeCam = "{camera_mode}";
        let activeEnv = "{env_lighting}";
        let currentAnimState = "walk";

        // Live Real-Time Motion Sensor Tracking State
        let isLiveMoving = {"true" if is_live_moving else "false"};
        let currentSpeedKmh = {user_speed_kmh if user_speed_kmh > 0 else 4.8};
        let motionState = isLiveMoving ? "MOVING" : "STATIONARY";
        let remainingStepM = (MANEUVERS[activeIdx] && MANEUVERS[activeIdx].distance_m && MANEUVERS[activeIdx].distance_m > 0) ? MANEUVERS[activeIdx].distance_m : 250;
        let motionSensorSource = "🛰️ GPS & Accel";
        let stepIntervalTimer = null;
        let lastGpsPos = null;
        let lastGpsTime = 0;
        let lastAccelMag = 9.8;
        let lastStepTimestamp = 0;
        let stepCountCadence = 0;

        const AURA_POSES = {{
            "welcome": "{mascot_welcome}",
            "pointing": "{mascot_pointing}",
            "thinking": "{poses.get('thinking', '')}",
            "excited": "{mascot_excited}",
            "talking": "{mascot_talking}",
            "waving": "{mascot_waving}"
        }};

        // Sound Synthesis for Pedestrian & Turn Chimes
        let audioCtx = null;
        function playChime(freq = 660) {{
            if (!isVoiceOn) return;
            try {{
                if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(freq * 1.5, audioCtx.currentTime + 0.12);
                gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.15);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.16);
            }} catch(e) {{}}
        }}

        function speakText(txt) {{
            if (!isVoiceOn || !('speechSynthesis' in window)) return;
            try {{
                window.speechSynthesis.cancel();
                const u = new SpeechSynthesisUtterance(txt);
                u.rate = 1.05;
                window.speechSynthesis.speak(u);
            }} catch(e) {{}}
        }}

        function getScenicStepSvg(dirType, roadName, stepNum, iconText, isCompleted, isActive) {{
            const rawDir = (dirType || '').toUpperCase();
            const cleanRoad = String(roadName || 'Main Corridor').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
            const shortRoad = cleanRoad.length > 20 ? cleanRoad.substring(0, 18) + '...' : cleanRoad;
            const uid = 'svg_' + stepNum + '_' + Math.random().toString(36).substr(2, 5);
            const labelBg = 'rgba(15, 23, 42, 0.88)';

            if (rawDir.includes('ARRIVE') || rawDir.includes('DEST')) {{
                return `
                <svg viewBox="0 0 200 92" width="100%" height="92" xmlns="http://www.w3.org/2000/svg" style="display:block; border-radius:12px 12px 0 0; overflow:hidden;">
                    <defs>
                        <linearGradient id="sky_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#0f172a"/>
                            <stop offset="50%" stop-color="#047857"/>
                            <stop offset="100%" stop-color="#10b981"/>
                        </linearGradient>
                        <linearGradient id="road_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#334155"/>
                            <stop offset="100%" stop-color="#1e293b"/>
                        </linearGradient>
                        <radialGradient id="sun_${{uid}}" cx="50%" cy="30%" r="50%">
                            <stop offset="0%" stop-color="#fef08a" stop-opacity="0.9"/>
                            <stop offset="50%" stop-color="#f59e0b" stop-opacity="0.4"/>
                            <stop offset="100%" stop-color="#10b981" stop-opacity="0"/>
                        </radialGradient>
                    </defs>
                    <rect width="200" height="92" fill="url(#sky_${{uid}})"/>
                    <circle cx="100" cy="36" r="38" fill="url(#sun_${{uid}})"/>
                    <polygon points="0,50 35,40 70,48 110,36 150,46 185,38 200,46 200,54 0,54" fill="#064e3b" opacity="0.7"/>
                    <rect y="48" width="200" height="44" fill="#065f46"/>
                    <polygon points="65,92 135,92 112,48 88,48" fill="url(#road_${{uid}})"/>
                    <line x1="100" y1="48" x2="100" y2="92" stroke="#34d399" stroke-width="2" stroke-dasharray="4,3"/>
                    <path d="M 75 92 L 75 40 Q 100 26 125 40 L 125 92" fill="none" stroke="#34d399" stroke-width="3.5"/>
                    <path d="M 78 43 Q 100 30 122 43" fill="none" stroke="#fef08a" stroke-width="1.8"/>
                    <rect x="80" y="30" width="40" height="10" rx="3" fill="#064e3b" stroke="#34d399" stroke-width="1"/>
                    <text x="100" y="37.5" font-size="5.5" font-weight="900" fill="#fef08a" text-anchor="middle" font-family="sans-serif">★ ARRIVAL ★</text>
                    <text x="68" y="42" font-size="11">🏁</text>
                    <text x="122" y="42" font-size="11">🏁</text>
                    <rect x="8" y="72" width="70" height="14" rx="3" fill="${{labelBg}}" stroke="#34d399" stroke-width="1"/>
                    <text x="43" y="82" font-size="6.5" font-weight="800" fill="#a7f3d0" text-anchor="middle" font-family="sans-serif">${{shortRoad}}</text>
                </svg>`;
            }} else if (rawDir.includes('LEFT')) {{
                return `
                <svg viewBox="0 0 200 92" width="100%" height="92" xmlns="http://www.w3.org/2000/svg" style="display:block; border-radius:12px 12px 0 0; overflow:hidden;">
                    <defs>
                        <linearGradient id="sky_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#0369a1"/>
                            <stop offset="100%" stop-color="#38bdf8"/>
                        </linearGradient>
                        <linearGradient id="road_${{uid}}" x1="0" y1="0" x2="1" y2="1">
                            <stop offset="0%" stop-color="#1e293b"/>
                            <stop offset="100%" stop-color="#334155"/>
                        </linearGradient>
                    </defs>
                    <rect width="200" height="92" fill="url(#sky_${{uid}})"/>
                    <circle cx="170" cy="20" r="13" fill="#fef08a" opacity="0.8"/>
                    <ellipse cx="140" cy="18" rx="18" ry="6" fill="#ffffff" opacity="0.6"/>
                    <rect y="46" width="200" height="46" fill="#0f766e"/>
                    <path d="M 0 50 Q 60 53 90 92 L 155 92 Q 120 46 0 42 Z" fill="url(#road_${{uid}})"/>
                    <path d="M 0 42 Q 120 46 155 92" fill="none" stroke="#64748b" stroke-width="2"/>
                    <path d="M 0 50 Q 60 53 90 92" fill="none" stroke="#64748b" stroke-width="2"/>
                    <path d="M 0 46 Q 90 50 122 92" fill="none" stroke="#fbbf24" stroke-width="2" stroke-dasharray="6,4"/>
                    <g transform="translate(68, 60) scale(0.6)">
                        <path d="M 28 35 C 28 20, 15 12, -2 12 L -2 18 L -18 8 L -2 -2 L -2 5 C 20 5, 36 15, 36 35 Z" fill="#ffffff" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.5))"/>
                    </g>
                    <line x1="8" y1="44" x2="16" y2="50" stroke="#ffffff" stroke-width="3"/>
                    <line x1="16" y1="44" x2="24" y2="50" stroke="#ffffff" stroke-width="3"/>
                    <line x1="24" y1="44" x2="32" y2="50" stroke="#ffffff" stroke-width="3"/>
                    <rect x="160" y="30" width="32" height="30" rx="2" fill="#1e293b" opacity="0.85"/>
                    <rect x="165" y="36" width="6" height="6" fill="#38bdf8" opacity="0.75"/>
                    <rect x="175" y="36" width="6" height="6" fill="#38bdf8" opacity="0.75"/>
                    <circle cx="148" cy="44" r="9" fill="#15803d"/>
                    <circle cx="148" cy="38" r="7" fill="#22c55e"/>
                    <line x1="38" y1="26" x2="38" y2="48" stroke="#475569" stroke-width="2"/>
                    <rect x="34" y="22" width="8" height="15" rx="2" fill="#0f172a"/>
                    <circle cx="38" cy="26" r="2" fill="#ef4444"/>
                    <circle cx="38" cy="30" r="2" fill="#f59e0b"/>
                    <circle cx="38" cy="35" r="2.5" fill="#22c55e"/>
                    <rect x="8" y="72" width="82" height="14" rx="3" fill="${{labelBg}}" stroke="#38bdf8" stroke-width="1"/>
                    <text x="49" y="82" font-size="6.5" font-weight="800" fill="#e0f2fe" text-anchor="middle" font-family="sans-serif">TURN LEFT • ${{shortRoad}}</text>
                </svg>`;
            }} else if (rawDir.includes('RIGHT')) {{
                return `
                <svg viewBox="0 0 200 92" width="100%" height="92" xmlns="http://www.w3.org/2000/svg" style="display:block; border-radius:12px 12px 0 0; overflow:hidden;">
                    <defs>
                        <linearGradient id="sky_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#0284c7"/>
                            <stop offset="100%" stop-color="#60a5fa"/>
                        </linearGradient>
                        <linearGradient id="road_${{uid}}" x1="0" y1="0" x2="1" y2="1">
                            <stop offset="0%" stop-color="#334155"/>
                            <stop offset="100%" stop-color="#1e293b"/>
                        </linearGradient>
                    </defs>
                    <rect width="200" height="92" fill="url(#sky_${{uid}})"/>
                    <circle cx="30" cy="20" r="13" fill="#fef08a" opacity="0.8"/>
                    <ellipse cx="60" cy="18" rx="18" ry="6" fill="#ffffff" opacity="0.6"/>
                    <rect y="46" width="200" height="46" fill="#0f766e"/>
                    <path d="M 45 92 Q 80 46 200 42 L 200 50 Q 140 53 110 92 Z" fill="url(#road_${{uid}})"/>
                    <path d="M 45 92 Q 80 46 200 42" fill="none" stroke="#64748b" stroke-width="2"/>
                    <path d="M 110 92 Q 140 53 200 50" fill="none" stroke="#64748b" stroke-width="2"/>
                    <path d="M 78 92 Q 110 50 200 46" fill="none" stroke="#fbbf24" stroke-width="2" stroke-dasharray="6,4"/>
                    <g transform="translate(115, 60) scale(0.6)">
                        <path d="M -28 35 C -28 20, -15 12, 2 12 L 2 18 L 18 8 L 2 -2 L 2 5 C -20 5, -36 15, -36 35 Z" fill="#ffffff" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.5))"/>
                    </g>
                    <line x1="168" y1="44" x2="176" y2="50" stroke="#ffffff" stroke-width="3"/>
                    <line x1="176" y1="44" x2="184" y2="50" stroke="#ffffff" stroke-width="3"/>
                    <line x1="184" y1="44" x2="192" y2="50" stroke="#ffffff" stroke-width="3"/>
                    <rect x="8" y="30" width="32" height="30" rx="2" fill="#1e293b" opacity="0.85"/>
                    <rect x="13" y="36" width="6" height="6" fill="#38bdf8" opacity="0.75"/>
                    <rect x="23" y="36" width="6" height="6" fill="#38bdf8" opacity="0.75"/>
                    <circle cx="52" cy="44" r="9" fill="#15803d"/>
                    <circle cx="52" cy="38" r="7" fill="#22c55e"/>
                    <line x1="158" y1="26" x2="158" y2="48" stroke="#475569" stroke-width="2"/>
                    <rect x="154" y="22" width="8" height="15" rx="2" fill="#0f172a"/>
                    <circle cx="158" cy="26" r="2" fill="#ef4444"/>
                    <circle cx="158" cy="30" r="2" fill="#f59e0b"/>
                    <circle cx="158" cy="35" r="2.5" fill="#22c55e"/>
                    <rect x="108" y="72" width="84" height="14" rx="3" fill="${{labelBg}}" stroke="#38bdf8" stroke-width="1"/>
                    <text x="150" y="82" font-size="6.5" font-weight="800" fill="#e0f2fe" text-anchor="middle" font-family="sans-serif">TURN RIGHT • ${{shortRoad}}</text>
                </svg>`;
            }} else if (rawDir.includes('START') || rawDir.includes('DEPART')) {{
                return `
                <svg viewBox="0 0 200 92" width="100%" height="92" xmlns="http://www.w3.org/2000/svg" style="display:block; border-radius:12px 12px 0 0; overflow:hidden;">
                    <defs>
                        <linearGradient id="sky_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#0284c7"/>
                            <stop offset="60%" stop-color="#38bdf8"/>
                            <stop offset="100%" stop-color="#bae6fd"/>
                        </linearGradient>
                        <linearGradient id="road_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#475569"/>
                            <stop offset="100%" stop-color="#1e293b"/>
                        </linearGradient>
                    </defs>
                    <rect width="200" height="92" fill="url(#sky_${{uid}})"/>
                    <ellipse cx="100" cy="44" rx="50" ry="15" fill="#fef08a" opacity="0.6"/>
                    <polygon points="10,44 25,34 35,44 50,30 65,44 80,36 95,44 110,32 130,44 150,37 170,44 190,34 195,44" fill="#0284c7" opacity="0.4"/>
                    <rect y="44" width="200" height="48" fill="#065f46"/>
                    <polygon points="40,92 160,92 106,44 94,44" fill="url(#road_${{uid}})"/>
                    <polygon points="26,92 40,92 94,44 88,44" fill="#64748b"/>
                    <polygon points="160,92 174,92 112,44 106,44" fill="#64748b"/>
                    <line x1="100" y1="44" x2="100" y2="92" stroke="#fbbf24" stroke-width="2" stroke-dasharray="6,4"/>
                    <rect x="74" y="58" width="52" height="6" rx="2" fill="#059669" stroke="#34d399" stroke-width="1.5"/>
                    <line x1="78" y1="64" x2="78" y2="88" stroke="#34d399" stroke-width="2.5"/>
                    <line x1="122" y1="64" x2="122" y2="88" stroke="#34d399" stroke-width="2.5"/>
                    <text x="100" y="63" font-size="5" font-weight="900" fill="#ffffff" text-anchor="middle" font-family="sans-serif">★ DEPARTURE GATE ★</text>
                    <circle cx="100" cy="72" r="5" fill="#10b981"/>
                    <circle cx="100" cy="72" r="2" fill="#ffffff"/>
                    <circle cx="20" cy="54" r="8" fill="#15803d"/><circle cx="20" cy="48" r="6" fill="#22c55e"/>
                    <circle cx="180" cy="54" r="8" fill="#15803d"/><circle cx="180" cy="48" r="6" fill="#22c55e"/>
                    <rect x="8" y="72" width="76" height="14" rx="3" fill="${{labelBg}}" stroke="#10b981" stroke-width="1"/>
                    <text x="46" y="82" font-size="6.5" font-weight="800" fill="#a7f3d0" text-anchor="middle" font-family="sans-serif">START • ${{shortRoad}}</text>
                </svg>`;
            }} else if (rawDir.includes('ROUNDABOUT')) {{
                return `
                <svg viewBox="0 0 200 92" width="100%" height="92" xmlns="http://www.w3.org/2000/svg" style="display:block; border-radius:12px 12px 0 0; overflow:hidden;">
                    <defs>
                        <linearGradient id="sky_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#0284c7"/>
                            <stop offset="100%" stop-color="#38bdf8"/>
                        </linearGradient>
                    </defs>
                    <rect width="200" height="92" fill="url(#sky_${{uid}})"/>
                    <rect y="42" width="200" height="50" fill="#065f46"/>
                    <ellipse cx="100" cy="68" rx="72" ry="23" fill="#334155" stroke="#64748b" stroke-width="2"/>
                    <ellipse cx="100" cy="68" rx="36" ry="11" fill="#15803d" stroke="#22c55e" stroke-width="2"/>
                    <circle cx="100" cy="66" r="5" fill="#f59e0b"/>
                    <ellipse cx="100" cy="68" rx="54" ry="17" fill="none" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="5,4"/>
                    <text x="60" y="70" font-size="10" fill="#ffffff">↺</text>
                    <text x="134" y="70" font-size="10" fill="#ffffff">↻</text>
                    <rect x="8" y="72" width="82" height="14" rx="3" fill="${{labelBg}}" stroke="#38bdf8" stroke-width="1"/>
                    <text x="49" y="82" font-size="6.5" font-weight="800" fill="#e0f2fe" text-anchor="middle" font-family="sans-serif">ROUNDABOUT • ${{shortRoad}}</text>
                </svg>`;
            }} else {{
                return `
                <svg viewBox="0 0 200 92" width="100%" height="92" xmlns="http://www.w3.org/2000/svg" style="display:block; border-radius:12px 12px 0 0; overflow:hidden;">
                    <defs>
                        <linearGradient id="sky_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#0284c7"/>
                            <stop offset="50%" stop-color="#38bdf8"/>
                            <stop offset="100%" stop-color="#7dd3fc"/>
                        </linearGradient>
                        <linearGradient id="road_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#475569"/>
                            <stop offset="100%" stop-color="#1e293b"/>
                        </linearGradient>
                    </defs>
                    <rect width="200" height="92" fill="url(#sky_${{uid}})"/>
                    <ellipse cx="60" cy="18" rx="20" ry="6" fill="#ffffff" opacity="0.75"/>
                    <ellipse cx="150" cy="14" rx="24" ry="7" fill="#ffffff" opacity="0.65"/>
                    <polygon points="0,44 40,34 90,42 140,32 180,40 200,36 200,46 0,46" fill="#0369a1" opacity="0.5"/>
                    <rect y="44" width="200" height="48" fill="#047857"/>
                    <polygon points="35,92 165,92 106,44 94,44" fill="url(#road_${{uid}})"/>
                    <polygon points="20,92 35,92 94,44 88,44" fill="#64748b"/>
                    <polygon points="165,92 180,92 112,44 106,44" fill="#64748b"/>
                    <line x1="100" y1="44" x2="100" y2="92" stroke="#fbbf24" stroke-width="2.5" stroke-dasharray="6,4"/>
                    <circle cx="22" cy="60" r="10" fill="#15803d"/><circle cx="22" cy="52" r="8" fill="#22c55e"/>
                    <circle cx="48" cy="50" r="6" fill="#15803d"/><circle cx="48" cy="45" r="4" fill="#22c55e"/>
                    <circle cx="178" cy="60" r="10" fill="#15803d"/><circle cx="178" cy="52" r="8" fill="#22c55e"/>
                    <circle cx="152" cy="50" r="6" fill="#15803d"/><circle cx="152" cy="45" r="4" fill="#22c55e"/>
                    <rect x="76" y="50" width="48" height="9" rx="2" fill="#0f172a" stroke="#38bdf8" stroke-width="1.2"/>
                    <text x="100" y="56.5" font-size="5" font-weight="900" fill="#38bdf8" text-anchor="middle" font-family="sans-serif">⬆ STRAIGHT AHEAD</text>
                    <rect x="8" y="72" width="76" height="14" rx="3" fill="${{labelBg}}" stroke="#38bdf8" stroke-width="1"/>
                    <text x="46" y="82" font-size="6.5" font-weight="800" fill="#e0f2fe" text-anchor="middle" font-family="sans-serif">${{shortRoad}}</text>
                </svg>`;
            }}
        }}

        // Render Pipeline Chips
        function renderPipeline() {{
            const cont = document.getElementById('pipeline-track-container');
            if (!cont) return;
            cont.innerHTML = '';

            MANEUVERS.forEach((m, idx) => {{
                const card = document.createElement('div');
                let cls = 'pipeline-step-card';
                const isCompleted = (idx < activeIdx);
                const isActive = (idx === activeIdx);
                if (isActive) cls += ' active';
                else if (isCompleted) cls += ' completed';
                card.className = cls;

                const picSvg = getScenicStepSvg(m.direction_type, m.road_name, m.step_num, m.icon, isCompleted, isActive);

                card.id = `step-card-${{idx}}`;
                card.innerHTML = `
                    <div class="step-picture-frame">
                        ${{picSvg}}
                        <div class="step-pic-overlay-badge">
                            <span class="step-num-pill">STEP ${{m.step_num}}</span>
                            <span class="step-icon-badge">${{m.icon}}</span>
                        </div>
                    </div>
                    <div class="step-card-body">
                        <div class="step-card-headline" title="${{m.headline}}">
                            ${{m.headline}}
                        </div>
                        <div class="step-card-footer">
                            <span class="step-card-road" title="${{m.road_name || ''}}">${{m.road_name || 'Corridor'}}</span>
                            <b class="step-card-dist">${{m.distance_human}}</b>
                        </div>
                    </div>
                `;

                card.onclick = () => selectStep(idx);
                cont.appendChild(card);
            }});
        }}

        window.selectStep = function(idx) {{
            if (idx < 0 || idx >= MANEUVERS.length) return;
            activeIdx = idx;
            const m = MANEUVERS[idx];

            // Update UI elements
            const hudStep = document.getElementById('hud-active-step');
            if (hudStep) hudStep.innerText = m.step_num;

            const iconEl = document.getElementById('stage-icon');
            if (iconEl) iconEl.innerText = m.icon;

            const headEl = document.getElementById('stage-headline');
            if (headEl) headEl.innerText = m.headline;

            const subEl = document.getElementById('stage-sub');
            if (subEl) subEl.innerText = `${{m.road_name}} • ${{m.instruction}}`;

            const distEl = document.getElementById('stage-dist');
            if (distEl) distEl.innerText = m.distance_human;

            const timeEl = document.getElementById('stage-time');
            if (timeEl) timeEl.innerText = `~${{m.time_estimate}}`;

            const lookEl = document.getElementById('stage-look');
            if (lookEl) lookEl.innerText = `👀 ${{m.what_to_look_for}}`;

            const speechEl = document.getElementById('aura-speech-content');
            if (speechEl) speechEl.innerText = m.aura_speech;

            // Trigger 2D Fallback Pose Matching
            const podImg = document.getElementById('aura-pod-img');
            const poseKey = m.aura_pose || (m.direction_type === 'ARRIVE' ? 'excited' : 'talking');
            if (podImg && AURA_POSES[poseKey]) {{
                podImg.src = AURA_POSES[poseKey];
            }}

            // Correlate 3D Animation State with Maneuver
            const dir = (m.direction_type || '').toUpperCase();
            if (dir === 'ARRIVE' || dir === 'DEST_REACHED') {{
                currentAnimState = 'arrive';
            }} else if (dir.includes('LEFT')) {{
                currentAnimState = 'turn_left';
            }} else if (dir.includes('RIGHT')) {{
                currentAnimState = 'turn_right';
            }} else if (dir === 'START') {{
                currentAnimState = 'wave';
            }} else if (dir.includes('ROUNDABOUT') || dir.includes('MERGE')) {{
                currentAnimState = 'turn_right';
            }} else {{
                currentAnimState = 'walk';
            }}

            playChime(660);
            speakText(m.spoken_text);
            renderPipeline();

            // Reset dynamic step countdown for newly activated maneuver
            remainingStepM = (m.distance_m && m.distance_m > 0) ? m.distance_m : 250;
            const remEl = document.getElementById('step-remaining-dist');
            if (remEl) remEl.innerText = m.distance_human || (remainingStepM + ' m');

            // Auto-scroll pipeline to center active card smoothly
            setTimeout(() => {{
                const activeCard = document.getElementById(`step-card-${{idx}}`);
                const cont = document.getElementById('pipeline-track-container');
                if (activeCard && cont) {{
                    const cardLeft = activeCard.offsetLeft;
                    const cardWidth = activeCard.offsetWidth;
                    const contWidth = cont.offsetWidth;
                    cont.scrollTo({{
                        left: cardLeft - (contWidth / 2) + (cardWidth / 2),
                        behavior: 'smooth'
                    }});
                }}
            }}, 50);
        }};

        window.triggerAuraAction = function(action) {{
            const podImg = document.getElementById('aura-pod-img');
            const speechEl = document.getElementById('aura-speech-content');

            if (action === 'wave') {{
                currentAnimState = 'wave';
                if (podImg && AURA_POSES.waving) podImg.src = AURA_POSES.waving;
                if (speechEl) speechEl.innerText = "Hey! I'm watching the road closely with you!";
                playChime(880);
                speakText("Hey! I'm watching the road closely with you!");
            }} else if (action === 'jump') {{
                currentAnimState = 'arrive';
                if (podImg && AURA_POSES.excited) podImg.src = AURA_POSES.excited;
                if (speechEl) speechEl.innerText = "Hooray! Great progress on our journey!";
                playChime(990);
                speakText("Hooray! Great progress on our journey!");
            }} else if (action === 'run') {{
                currentAnimState = 'run';
                if (podImg && AURA_POSES.pointing) podImg.src = AURA_POSES.pointing;
                if (speechEl) speechEl.innerText = "Picking up pace! Stay alert for corridor junctions.";
                playChime(750);
            }} else if (action === 'walk') {{
                currentAnimState = 'walk';
                if (podImg && AURA_POSES.talking) podImg.src = AURA_POSES.talking;
                if (speechEl) speechEl.innerText = "Walking comfortably along the designated route.";
                playChime(600);
            }}
        }};

        window.setCameraPerspective = function(mode) {{
            activeCam = mode;
            ['pov', 'drone', 'iso'].forEach(k => {{
                const btn = document.getElementById('cam-' + k);
                if (btn) btn.classList.remove('active');
            }});
            const btn = document.getElementById('cam-' + mode);
            if (btn) btn.classList.add('active');

            const camBadge = document.getElementById('hud-cam-mode');
            if (camBadge) {{
                camBadge.innerText = 'CAM: ' + (mode === 'pov' ? 'DRIVER POV' : (mode === 'iso' ? '3D ISOMETRIC' : '3D FOLLOW DRONE'));
            }}
        }};

        let isAutoRealTimeEnv = true;

        function getRealTimeEnv() {{
            const now = new Date();
            const h = now.getHours() + (now.getMinutes() / 60.0);
            if (h >= 17.25 && h < 19.35) {{
                return 'sunset';
            }} else if (h >= 6.0 && h < 17.25) {{
                return 'day';
            }} else {{
                return 'night';
            }}
        }}

        window.toggleAutoRealTimeEnv = function() {{
            isAutoRealTimeEnv = true;
            const env = getRealTimeEnv();
            window.setEnvLight(env, true);
        }};

        window.setEnvLight = function(env, fromAuto = false) {{
            if (!fromAuto) isAutoRealTimeEnv = false;
            activeEnv = env;
            ['day', 'sunset', 'night'].forEach(k => {{
                const btn = document.getElementById('env-' + k);
                if (btn) btn.classList.remove('active');
            }});
            const btn = document.getElementById('env-' + env);
            if (btn) btn.classList.add('active');

            const autoBtn = document.getElementById('env-auto');
            if (autoBtn) {{
                if (isAutoRealTimeEnv) autoBtn.classList.add('active');
                else autoBtn.classList.remove('active');
            }}

            const envBadge = document.getElementById('hud-env-mode');
            if (envBadge) {{
                envBadge.innerText = 'ENV: ' + env.toUpperCase() + (isAutoRealTimeEnv ? ' (REAL TIME)' : '');
            }}

            if (threeEnv) {{
                threeEnv.updateLighting(env);
            }}
        }};

        // =========================================================================
        // REAL USER MOTION SENSORS & AUTOMATIC VIRTUAL GUIDE STEPPING
        // =========================================================================
        function updateMotionUI(speedKmh, state, source) {{
            currentSpeedKmh = speedKmh;
            motionState = state;
            if (source) motionSensorSource = source;

            const speedEl = document.getElementById('sensor-speed-val');
            if (speedEl) speedEl.innerText = speedKmh > 0 ? speedKmh.toFixed(1) : "0.0";

            const statusBadge = document.getElementById('sensor-status-badge');
            const statusTxt = document.getElementById('sensor-status-text');
            if (statusBadge && statusTxt) {{
                if (state === 'MOVING') {{
                    statusBadge.className = 'sensor-status-badge moving';
                    statusTxt.innerText = 'SENSOR MOTION: MOVING';
                }} else {{
                    statusBadge.className = 'sensor-status-badge stationary';
                    statusTxt.innerText = 'SENSOR MOTION: STATIONARY';
                }}
            }}

            const srcEl = document.getElementById('sensor-source-val');
            if (srcEl) srcEl.innerText = motionSensorSource;

            const btnIcon = document.getElementById('btn-move-icon');
            const btnLbl = document.getElementById('btn-move-label');
            if (btnIcon && btnLbl) {{
                if (isLiveMoving) {{
                    btnIcon.innerText = '⏸';
                    btnLbl.innerText = 'Pause Guide';
                }} else {{
                    btnIcon.innerText = '▶';
                    btnLbl.innerText = 'Move in Parallel';
                }}
            }}

            // Dynamically synchronize 3D Companion Animation with motion state & speed
            if (state === 'MOVING') {{
                if (currentSpeedKmh > 11.0) {{
                    currentAnimState = 'run';
                }} else if (currentAnimState !== 'turn_left' && currentAnimState !== 'turn_right' && currentAnimState !== 'arrive') {{
                    currentAnimState = 'walk';
                }}
            }} else if (state === 'STATIONARY') {{
                if (currentAnimState === 'walk' || currentAnimState === 'run') {{
                    currentAnimState = 'wave';
                }}
            }}
        }}

        function calcHaversineMeters(lat1, lon1, lat2, lon2) {{
            const R = 6371e3;
            const p1 = lat1 * Math.PI / 180;
            const p2 = lat2 * Math.PI / 180;
            const dp = (lat2 - lat1) * Math.PI / 180;
            const dl = (lon2 - lon1) * Math.PI / 180;
            const a = Math.sin(dp / 2) * Math.sin(dp / 2) +
                      Math.cos(p1) * Math.cos(p2) *
                      Math.sin(dl / 2) * Math.sin(dl / 2);
            return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        }}

        function initSensorWatchers() {{
            // 1. Live Geolocation Watcher for Speed and Corridor Advancement
            if ('geolocation' in navigator) {{
                try {{
                    navigator.geolocation.watchPosition(
                        (pos) => {{
                            const now = Date.now();
                            let detectedSpeed = 0;
                            if (pos.coords.speed !== null && !isNaN(pos.coords.speed) && pos.coords.speed >= 0) {{
                                detectedSpeed = pos.coords.speed * 3.6; // convert m/s to km/h
                            }} else if (lastGpsPos && lastGpsTime > 0) {{
                                const dt = (now - lastGpsTime) / 1000;
                                if (dt >= 1.0) {{
                                    const dM = calcHaversineMeters(
                                        lastGpsPos.coords.latitude, lastGpsPos.coords.longitude,
                                        pos.coords.latitude, pos.coords.longitude
                                    );
                                    detectedSpeed = (dM / dt) * 3.6;
                                }}
                            }}
                            lastGpsPos = pos;
                            lastGpsTime = now;

                            if (detectedSpeed >= 1.2) {{
                                isLiveMoving = true;
                                updateMotionUI(detectedSpeed, 'MOVING', '🛰️ Live GPS Satellites');
                            }} else if (isLiveMoving && detectedSpeed < 0.6) {{
                                updateMotionUI(0.0, 'STATIONARY', '🛰️ Live GPS (Idle)');
                            }}
                        }},
                        (err) => {{
                            console.log('GPS Sensor notice:', err.message);
                        }},
                        {{ enableHighAccuracy: true, maximumAge: 1500, timeout: 6000 }}
                    );
                }} catch (e) {{
                    console.warn('Geolocation sensor error:', e);
                }}
            }}

            // 2. Physical Accelerometer & Device Motion for Step Cadence Detection
            if (window.DeviceMotionEvent) {{
                try {{
                    window.addEventListener('devicemotion', (evt) => {{
                        const acc = evt.accelerationIncludingGravity || evt.acceleration;
                        if (!acc) return;
                        const ax = acc.x || 0, ay = acc.y || 0, az = acc.z || 0;
                        const mag = Math.sqrt(ax * ax + ay * ay + az * az);
                        const delta = Math.abs(mag - lastAccelMag);
                        lastAccelMag = mag;

                        const now = Date.now();
                        // Physical step peak threshold
                        if (delta > 1.8 && (now - lastStepTimestamp) > 320) {{
                            const stepDt = (now - lastStepTimestamp) / 1000;
                            lastStepTimestamp = now;
                            if (stepDt < 2.0) {{
                                const spm = Math.round(60 / stepDt);
                                stepCountCadence = spm;
                                if (currentSpeedKmh < 1.0 || motionState === 'STATIONARY') {{
                                    const inferredSpeed = Math.min(12.0, Math.max(3.2, (spm * 0.72 * 60) / 1000));
                                    isLiveMoving = true;
                                    updateMotionUI(inferredSpeed, 'MOVING', `📱 Sensor Cadence (${{spm}} spm)`);
                                }}
                            }}
                        }}
                    }}, {{ passive: true }});
                }} catch (e) {{
                    console.warn('Accelerometer sensor error:', e);
                }}
            }}
        }}

        function startStepProgressionLoop() {{
            if (stepIntervalTimer) clearInterval(stepIntervalTimer);

            stepIntervalTimer = setInterval(() => {{
                if (!isLiveMoving) return;

                if (motionState === 'MOVING') {{
                    const speedMps = Math.max(1.2, currentSpeedKmh / 3.6);
                    // Dynamically decrement step distance according to sensor velocity
                    remainingStepM -= (speedMps * 1.0);

                    // Update UI countdown displays
                    const remEl = document.getElementById('step-remaining-dist');
                    const timeEl = document.getElementById('step-countdown-time');
                    const stageDistEl = document.getElementById('stage-dist');

                    const formattedDist = remainingStepM >= 1000 
                        ? (remainingStepM / 1000).toFixed(1) + ' km' 
                        : Math.max(0, Math.round(remainingStepM)) + ' m';

                    if (remEl) remEl.innerText = formattedDist;
                    if (stageDistEl) stageDistEl.innerText = formattedDist;

                    if (timeEl) {{
                        const secLeft = Math.max(0, Math.round(remainingStepM / speedMps));
                        timeEl.innerText = `(~${{secLeft}}s)`;
                    }}

                    // When step threshold reached (within 8 meters), AUTOMATICALLY MAKE THE NEXT STEP!
                    if (remainingStepM <= 8) {{
                        if (activeIdx < MANEUVERS.length - 1) {{
                            const nextIdx = activeIdx + 1;
                            selectStep(nextIdx);
                        }} else {{
                            // Destination reached!
                            isLiveMoving = false;
                            updateMotionUI(0.0, 'STATIONARY', '🏁 Destination Reached');
                            currentAnimState = 'arrive';
                            const thoughtEl = document.getElementById('aura-speech-content');
                            if (thoughtEl) {{
                                thoughtEl.innerText = '🎉 Congratulations! You have successfully reached your destination!';
                            }}
                            speakText('Congratulations! You have reached your destination.');
                            playChime(880);
                            setTimeout(() => playChime(1100), 200);
                        }}
                    }}
                }}
            }}, 1000);
        }}

        window.toggleInternalMoveInParallel = function() {{
            isLiveMoving = !isLiveMoving;
            if (isLiveMoving) {{
                if (typeof DeviceMotionEvent !== 'undefined' && typeof DeviceMotionEvent.requestPermission === 'function') {{
                    DeviceMotionEvent.requestPermission().catch(() => {{}});
                }}
                const spd = currentSpeedKmh > 0 ? currentSpeedKmh : 4.8;
                updateMotionUI(spd, 'MOVING', '🛰️ Parallel Sensor GPS');
                speakText("Moving in parallel. Sensor motion tracking active.");
                playChime(750);
            }} else {{
                updateMotionUI(0.0, 'STATIONARY', '⏸ Guide Paused');
                speakText("Virtual guide paused.");
                playChime(440);
            }}
        }};

        window.toggleVoiceAudio = function() {{
            isVoiceOn = !isVoiceOn;
            const icon = document.getElementById('audio-icon');
            const txt = document.getElementById('audio-text');
            if (icon) icon.innerText = isVoiceOn ? '🔊' : '🔇';
            if (txt) txt.innerText = isVoiceOn ? 'Voice: On' : 'Voice: Muted';
            if (!isVoiceOn && 'speechSynthesis' in window) window.speechSynthesis.cancel();
        }};

        window.openPicturesGallery = function() {{
            const modal = document.getElementById('pictures-modal');
            const grid = document.getElementById('gallery-grid-items');
            if (!modal || !grid) return;

            grid.innerHTML = '';
            MANEUVERS.forEach((m, idx) => {{
                const card = document.createElement('div');
                card.className = 'gallery-card-item' + (idx === activeIdx ? ' active' : '');
                const picSvg = getScenicStepSvg(m.direction_type, m.road_name, m.step_num, m.icon, idx < activeIdx, idx === activeIdx);
                card.innerHTML = `
                    <div class="step-picture-frame" style="height: 115px;">
                        ${{picSvg}}
                        <div class="step-pic-overlay-badge">
                            <span class="step-num-pill" style="font-size: 0.72rem; padding: 3px 9px;">SCENE #${{m.step_num}}</span>
                            <span class="step-icon-badge" style="font-size: 1.25rem;">${{m.icon}}</span>
                        </div>
                    </div>
                    <div style="padding: 12px 14px 14px 14px; display: flex; flex-direction: column; gap: 8px; flex: 1; justify-content: space-between;">
                        <div>
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 4px;">
                                <div style="font-size: 0.92rem; font-weight: 800; color: #ffffff; line-height: 1.35;">${{m.headline}}</div>
                                <span style="font-size: 0.70rem; font-weight: 800; color: #34d399; background: rgba(16, 185, 129, 0.18); border: 1px solid rgba(16, 185, 129, 0.4); padding: 2px 7px; border-radius: 999px; white-space: nowrap;">${{m.distance_human}}</span>
                            </div>
                            <div style="font-size: 0.76rem; color: #94a3b8; display: flex; align-items: center; gap: 6px;">
                                <span>🛣️ ${{m.road_name || 'Corridor Route'}}</span>
                                <span>•</span>
                                <span style="color: #38bdf8;">~${{m.time_estimate}}</span>
                            </div>
                        </div>

                        <!-- Creative Aura Guide Story Bubble -->
                        <div style="background: linear-gradient(135deg, rgba(14, 165, 233, 0.15) 0%, rgba(168, 85, 247, 0.12) 100%); border-left: 3px solid #38bdf8; border-radius: 8px; padding: 8px 10px; font-size: 0.75rem; color: #e2e8f0; line-height: 1.45;">
                            <div style="font-size: 0.68rem; font-weight: 800; color: #38bdf8; letter-spacing: 0.05em; display: flex; align-items: center; gap: 5px; margin-bottom: 2px;">
                                <span>🤖 AURA GUIDE NOTES</span>
                            </div>
                            <div style="color: #cbd5e1; font-style: italic;">"${{m.aura_speech}}"</div>
                            ${{m.what_to_look_for ? `<div style="margin-top: 4px; font-size: 0.70rem; color: #67e8f9; font-weight: 600;">👀 Look for: ${{m.what_to_look_for}}</div>` : ''}}
                        </div>

                        <button class="btn-action-pill" style="margin-top: 4px; width: 100%; justify-content: center; background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); border: none; box-shadow: 0 4px 12px rgba(56, 189, 248, 0.35); font-weight: 800;" onclick="selectStep(${{idx}}); closePicturesGallery();">
                            <span>🧭</span> Jump to Scene #${{m.step_num}}
                        </button>
                    </div>
                `;
                grid.appendChild(card);
            }});

            modal.style.display = 'flex';
        }};

        window.closePicturesGallery = function() {{
            const modal = document.getElementById('pictures-modal');
            if (modal) modal.style.display = 'none';
        }};

        // =========================================================================
        // THREE.JS 3D AURA ROBOT & ROADWAY SCENE ENGINE
        // =========================================================================
        let threeEnv = null;

        function initAuraThreeScene() {{
            const canvas = document.getElementById('aura-threejs-canvas');
            const container = document.getElementById('aura-3d-scene-box');
            if (!canvas || !container || typeof THREE === 'undefined') return;

            try {{
                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0x38bdf8);
                scene.fog = new THREE.FogExp2(0xc7d2fe, 0.0075);

                const width = container.clientWidth || 800;
                const height = container.clientHeight || 360;

                const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 800);
                const renderer = new THREE.WebGLRenderer({{ canvas: canvas, antialias: true, alpha: true, powerPreference: "high-performance" }});
                renderer.setSize(width, height);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                renderer.shadowMap.enabled = true;
                renderer.shadowMap.type = THREE.PCFSoftShadowMap;

                // -----------------------------------------------------------------
                // 1. ATMOSPHERIC NATURAL LIGHTING
                // -----------------------------------------------------------------
                // Natural Hemisphere Light (Sky Blue above + Fresh Grass bounce below)
                const hemiLight = new THREE.HemisphereLight(0x7dd3fc, 0x15803d, 0.85);
                scene.add(hemiLight);

                const ambientLight = new THREE.AmbientLight(0xffffff, 0.35);
                scene.add(ambientLight);

                // Directional Sunlight with Soft Shadows
                const dirLight = new THREE.DirectionalLight(0xfffaed, 1.35);
                dirLight.position.set(28, 52, 28);
                dirLight.castShadow = true;
                dirLight.shadow.mapSize.width = 1024;
                dirLight.shadow.mapSize.height = 1024;
                dirLight.shadow.camera.near = 0.5;
                dirLight.shadow.camera.far = 180;
                dirLight.shadow.camera.left = -35;
                dirLight.shadow.camera.right = 35;
                dirLight.shadow.camera.top = 35;
                dirLight.shadow.camera.bottom = -35;
                scene.add(dirLight);

                // -----------------------------------------------------------------
                // 2. DYNAMIC REALISTIC SKY DOME & CELESTIAL BODIES
                // -----------------------------------------------------------------
                function makeSkyTexture(topHex, midHex, botHex) {{
                    const sc = document.createElement('canvas');
                    sc.width = 128; sc.height = 256;
                    const sctx = sc.getContext('2d');
                    const grad = sctx.createLinearGradient(0, 0, 0, 256);
                    grad.addColorStop(0.0, topHex);
                    grad.addColorStop(0.55, midHex);
                    grad.addColorStop(1.0, botHex);
                    sctx.fillStyle = grad;
                    sctx.fillRect(0, 0, 128, 256);
                    const tex = new THREE.CanvasTexture(sc);
                    tex.generateMipmaps = false;
                    tex.minFilter = THREE.LinearFilter;
                    return tex;
                }}

                const skyGeo = new THREE.SphereGeometry(260, 32, 16);
                const skyMat = new THREE.MeshBasicMaterial({{
                    map: makeSkyTexture('#1d4ed8', '#38bdf8', '#e0f2fe'),
                    side: THREE.BackSide
                }});
                const skyMesh = new THREE.Mesh(skyGeo, skyMat);
                scene.add(skyMesh);

                // Sun & Moon
                const celestialGroup = new THREE.Group();
                const sunGeo = new THREE.CircleGeometry(7.0, 24);
                const sunMat = new THREE.MeshBasicMaterial({{ color: 0xfffae0, side: THREE.DoubleSide }});
                const sunMesh = new THREE.Mesh(sunGeo, sunMat);
                sunMesh.position.set(40, 68, 110);
                sunMesh.lookAt(0, 0, 0);
                celestialGroup.add(sunMesh);

                const sunGlowGeo = new THREE.CircleGeometry(16.0, 24);
                const sunGlowMat = new THREE.MeshBasicMaterial({{ color: 0xfef08a, transparent: true, opacity: 0.35, side: THREE.DoubleSide }});
                const sunGlowMesh = new THREE.Mesh(sunGlowGeo, sunGlowMat);
                sunGlowMesh.position.copy(sunMesh.position);
                sunGlowMesh.lookAt(0, 0, 0);
                celestialGroup.add(sunGlowMesh);

                const moonGeo = new THREE.CircleGeometry(5.5, 24);
                const moonMat = new THREE.MeshBasicMaterial({{ color: 0xf1f5f9, transparent: true, opacity: 0, side: THREE.DoubleSide }});
                const moonMesh = new THREE.Mesh(moonGeo, moonMat);
                moonMesh.position.set(-35, 55, 95);
                moonMesh.lookAt(0, 0, 0);
                celestialGroup.add(moonMesh);
                scene.add(celestialGroup);

                // Soft 3D Procedural Drifting Clouds
                const cloudGroup = new THREE.Group();
                const cloudGeo = new THREE.DodecahedronGeometry(1.6, 1);
                const cloudMat = new THREE.MeshStandardMaterial({{ color: 0xffffff, roughness: 0.95, transparent: true, opacity: 0.85 }});
                const cloudList = [];
                for (let c = 0; c < 9; c++) {{
                    const cluster = new THREE.Group();
                    const blobs = 5 + Math.floor(Math.random() * 4);
                    for (let b = 0; b < blobs; b++) {{
                        const puff = new THREE.Mesh(cloudGeo, cloudMat);
                        puff.position.set((Math.random() - 0.5) * 6, (Math.random() - 0.5) * 1.6, (Math.random() - 0.5) * 4);
                        const s = 1.3 + Math.random() * 1.9;
                        puff.scale.set(s, s * 0.5, s);
                        cluster.add(puff);
                    }}
                    cluster.position.set(-70 + Math.random() * 140, 26 + Math.random() * 16, -30 + Math.random() * 120);
                    cloudGroup.add(cluster);
                    cloudList.push({{ obj: cluster, speed: 0.012 + Math.random() * 0.016 }});
                }}
                scene.add(cloudGroup);

                // Twinkling Starfield (Active at Night)
                const starCount = 380;
                const starGeo = new THREE.BufferGeometry();
                const starPos = new Float32Array(starCount * 3);
                for (let i = 0; i < starCount; i++) {{
                    const u = Math.random();
                    const v = Math.random();
                    const theta = u * 2.0 * Math.PI;
                    const phi = Math.acos(2.0 * v - 1.0) * 0.48;
                    const r = 240;
                    starPos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
                    starPos[i * 3 + 1] = Math.abs(r * Math.cos(phi)) + 15;
                    starPos[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta);
                }}
                starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
                const starMat = new THREE.PointsMaterial({{ color: 0xffffff, size: 1.8, transparent: true, opacity: 0 }});
                const starField = new THREE.Points(starGeo, starMat);
                scene.add(starField);

                // -----------------------------------------------------------------
                // 3. LUSH CAMPUS LANDSCAPE & GRASS TERRAIN
                // -----------------------------------------------------------------
                function makeGrassTexture() {{
                    const gc = document.createElement('canvas');
                    gc.width = 256; gc.height = 256;
                    const gctx = gc.getContext('2d');
                    gctx.fillStyle = '#2d6a2e';
                    gctx.fillRect(0, 0, 256, 256);
                    for (let i = 0; i < 700; i++) {{
                        const gx = Math.random() * 256;
                        const gy = Math.random() * 256;
                        const gr = 2 + Math.random() * 5;
                        gctx.fillStyle = Math.random() > 0.5 ? 'rgba(54, 138, 56, 0.45)' : 'rgba(28, 77, 30, 0.45)';
                        gctx.beginPath();
                        gctx.arc(gx, gy, gr, 0, Math.PI * 2);
                        gctx.fill();
                    }}
                    const tex = new THREE.CanvasTexture(gc);
                    tex.wrapS = THREE.RepeatWrapping;
                    tex.wrapT = THREE.RepeatWrapping;
                    tex.repeat.set(36, 36);
                    return tex;
                }}

                const groundGeo = new THREE.PlaneGeometry(360, 360, 20, 20);
                const groundMat = new THREE.MeshStandardMaterial({{
                    map: makeGrassTexture(),
                    roughness: 0.95,
                    metalness: 0.05
                }});
                const groundMesh = new THREE.Mesh(groundGeo, groundMat);
                groundMesh.rotation.x = -Math.PI / 2;
                groundMesh.position.y = -0.05;
                groundMesh.receiveShadow = true;
                scene.add(groundMesh);

                // -----------------------------------------------------------------
                // 4. REALISTIC CURVING ROADWAY, CURBS, SIDEWALKS & MARKINGS
                // -----------------------------------------------------------------
                const roadGroup = new THREE.Group();
                const roadSplinePts = [];
                for (let i = 0; i <= 26; i++) {{
                    const z = (i - 8) * 4.5;
                    const x = Math.sin(i * 0.32) * 3.4;
                    roadSplinePts.push(new THREE.Vector3(x, 0, z));
                }}
                const roadSpline = new THREE.CatmullRomCurve3(roadSplinePts);

                // Main Asphalt Road Bed (Dark textured charcoal asphalt)
                const roadGeo = new THREE.TubeGeometry(roadSpline, 80, 2.7, 8, false);
                const roadMat = new THREE.MeshStandardMaterial({{ color: 0x1e242d, roughness: 0.86, metalness: 0.12 }});
                const roadMesh = new THREE.Mesh(roadGeo, roadMat);
                roadMesh.scale.set(1, 0.045, 1);
                roadMesh.receiveShadow = true;
                roadGroup.add(roadMesh);

                // Left & Right Raised Concrete Curbs
                const curbMat = new THREE.MeshStandardMaterial({{ color: 0x94a3b8, roughness: 0.75 }});
                const curbLeftGeo = new THREE.TubeGeometry(roadSpline, 80, 0.18, 6, false);
                const curbLeft = new THREE.Mesh(curbLeftGeo, curbMat);
                curbLeft.position.set(-2.7, 0.06, 0);
                roadGroup.add(curbLeft);

                const curbRight = new THREE.Mesh(curbLeftGeo, curbMat);
                curbRight.position.set(2.7, 0.06, 0);
                roadGroup.add(curbRight);

                // Left & Right Paved Sidewalks
                const swMat = new THREE.MeshStandardMaterial({{ color: 0x475569, roughness: 0.85 }});
                const swGeo = new THREE.TubeGeometry(roadSpline, 80, 1.25, 6, false);

                const swLeft = new THREE.Mesh(swGeo, swMat);
                swLeft.position.set(-3.85, 0.06, 0);
                swLeft.scale.set(1, 0.04, 1);
                roadGroup.add(swLeft);

                const swRight = new THREE.Mesh(swGeo, swMat);
                swRight.position.set(3.85, 0.06, 0);
                swRight.scale.set(1, 0.04, 1);
                roadGroup.add(swRight);

                // Road Edge Painted White Markings
                const edgeLineMat = new THREE.MeshBasicMaterial({{ color: 0xf8fafc }});
                const edgeLineGeo = new THREE.TubeGeometry(roadSpline, 80, 0.06, 4, false);

                const edgeL = new THREE.Mesh(edgeLineGeo, edgeLineMat);
                edgeL.position.set(-2.4, 0.06, 0);
                roadGroup.add(edgeL);

                const edgeR = new THREE.Mesh(edgeLineGeo, edgeLineMat);
                edgeR.position.set(2.4, 0.06, 0);
                roadGroup.add(edgeR);

                // Dashed Road Centerline
                const dashMat = new THREE.MeshBasicMaterial({{ color: 0xfbbf24 }});
                for (let s = 0; s < 40; s++) {{
                    if (s % 2 === 0) {{
                        const t = s / 40;
                        const pt = roadSpline.getPointAt(t);
                        const tan = roadSpline.getTangentAt(t);
                        const dashBox = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.02, 1.1), dashMat);
                        dashBox.position.set(pt.x, 0.065, pt.z);
                        dashBox.lookAt(pt.x + tan.x, 0.065, pt.z + tan.z);
                        roadGroup.add(dashBox);
                    }}
                }}

                // Glowing Cyan AR Trajectory Ribbon
                const ribbonGeo = new THREE.TubeGeometry(roadSpline, 80, 0.24, 6, false);
                const ribbonMat = new THREE.MeshBasicMaterial({{ color: 0x00f0ff, transparent: true, opacity: 0.92 }});
                const ribbonMesh = new THREE.Mesh(ribbonGeo, ribbonMat);
                ribbonMesh.position.y = 0.16;
                roadGroup.add(ribbonMesh);

                scene.add(roadGroup);

                // -----------------------------------------------------------------
                // 5. MODERN STREETLIGHTS & REALISTIC LAMP POSTS
                // -----------------------------------------------------------------
                const streetLampGroup = new THREE.Group();
                const lampLights = [];
                const poleMat = new THREE.MeshStandardMaterial({{ color: 0x1e293b, metalness: 0.7, roughness: 0.3 }});
                const lampHeadMat = new THREE.MeshStandardMaterial({{ color: 0x0f172a }});
                const lampGlassMat = new THREE.MeshBasicMaterial({{ color: 0xffffff }});

                const lampZList = [-22, -8, 8, 24, 40, 56, 72];
                lampZList.forEach((lz, idx) => {{
                    const t = Math.max(0, Math.min(1, (lz + 35) / 115));
                    const pt = roadSpline.getPointAt(t);
                    const side = (idx % 2 === 0) ? 1 : -1;
                    const postGroup = new THREE.Group();
                    postGroup.position.set(pt.x + side * 4.6, 0, pt.z);

                    // Vertical Steel Pole
                    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.09, 4.4, 12), poleMat);
                    pole.position.y = 2.2;
                    pole.castShadow = true;
                    postGroup.add(pole);

                    // Curved Top Arm
                    const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.05, 1.5, 8), poleMat);
                    arm.rotation.z = -side * 1.1;
                    arm.position.set(-side * 0.6, 4.4, 0);
                    postGroup.add(arm);

                    // Lamp Fixture
                    const head = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.14, 0.24), lampHeadMat);
                    head.position.set(-side * 1.25, 4.25, 0);
                    postGroup.add(head);

                    const glass = new THREE.Mesh(new THREE.PlaneGeometry(0.38, 0.20), lampGlassMat);
                    glass.rotation.x = Math.PI / 2;
                    glass.position.set(-side * 1.25, 4.17, 0);
                    postGroup.add(glass);

                    // Illuminating PointLight onto the asphalt
                    const pLight = new THREE.PointLight(0xfef08a, 0.0, 11, 1.6);
                    pLight.position.set(pt.x + side * 3.35, 4.1, pt.z);
                    scene.add(pLight);
                    lampLights.push({{ light: pLight, glass: glass }});

                    streetLampGroup.add(postGroup);
                }});
                scene.add(streetLampGroup);

                // -----------------------------------------------------------------
                // 6. LUSH TREES, FOLIAGE & BLOOMING SHRUBS
                // -----------------------------------------------------------------
                const foliageGroup = new THREE.Group();
                const treeSwayList = [];

                const trunkMat = new THREE.MeshStandardMaterial({{ color: 0x4a2e18, roughness: 0.9 }});
                const greenMats = [
                    new THREE.MeshStandardMaterial({{ color: 0x15803d, roughness: 0.82 }}),
                    new THREE.MeshStandardMaterial({{ color: 0x16a34a, roughness: 0.85 }}),
                    new THREE.MeshStandardMaterial({{ color: 0x14532d, roughness: 0.90 }}),
                    new THREE.MeshStandardMaterial({{ color: 0x166534, roughness: 0.84 }})
                ];
                const flowerMats = [
                    new THREE.MeshBasicMaterial({{ color: 0xf43f5e }}),
                    new THREE.MeshBasicMaterial({{ color: 0xfbbf24 }}),
                    new THREE.MeshBasicMaterial({{ color: 0xec4899 }})
                ];

                for (let s = 0; s < 36; s++) {{
                    const t = s / 36;
                    const pt = roadSpline.getPointAt(t);
                    const side = (s % 2 === 0) ? -1 : 1;
                    const dist = 5.6 + Math.random() * 3.5;

                    const tree = new THREE.Group();
                    tree.position.set(pt.x + side * dist, 0, pt.z + (Math.random() - 0.5) * 3);

                    const isPine = (s % 3 === 0);
                    const heightScale = 0.8 + Math.random() * 0.5;

                    if (isPine) {{
                        // Conifer / Pine Tree
                        const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.20, 2.2 * heightScale, 8), trunkMat);
                        trunk.position.y = 1.1 * heightScale;
                        tree.add(trunk);

                        const tiers = 3;
                        for (let tr = 0; tr < tiers; tr++) {{
                            const cMat = greenMats[tr % greenMats.length];
                            const cone = new THREE.Mesh(new THREE.ConeGeometry((1.6 - tr * 0.35) * heightScale, 1.8 * heightScale, 8), cMat);
                            cone.position.y = (1.8 + tr * 1.1) * heightScale;
                            cone.castShadow = true;
                            tree.add(cone);
                        }}
                    }} else {{
                        // Leafy Deciduous Canopy Tree
                        const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.24, 2.0 * heightScale, 8), trunkMat);
                        trunk.position.y = 1.0 * heightScale;
                        tree.add(trunk);

                        const crownMat = greenMats[s % greenMats.length];
                        const crown = new THREE.Mesh(new THREE.DodecahedronGeometry(1.6 * heightScale, 1), crownMat);
                        crown.position.y = 2.8 * heightScale;
                        crown.castShadow = true;
                        tree.add(crown);

                        const subCrown = new THREE.Mesh(new THREE.DodecahedronGeometry(1.1 * heightScale, 1), greenMats[(s + 1) % greenMats.length]);
                        subCrown.position.set(0.4 * heightScale, 3.4 * heightScale, 0.2 * heightScale);
                        tree.add(subCrown);
                    }}

                    // Shrub or blooming flower bush at the base
                    const shrub = new THREE.Mesh(new THREE.SphereGeometry(0.45 * heightScale, 8, 8), greenMats[2]);
                    shrub.position.set((Math.random() - 0.5) * 0.8, 0.25 * heightScale, (Math.random() - 0.5) * 0.8);
                    tree.add(shrub);

                    if (s % 2 === 0) {{
                        const fl = new THREE.Mesh(new THREE.DodecahedronGeometry(0.2, 0), flowerMats[s % flowerMats.length]);
                        fl.position.set(shrub.position.x + 0.1, 0.45 * heightScale, shrub.position.z + 0.1);
                        tree.add(fl);
                    }}

                    foliageGroup.add(tree);
                    treeSwayList.push({{ group: tree, phase: Math.random() * Math.PI * 2 }});
                }}
                scene.add(foliageGroup);

                // -----------------------------------------------------------------
                // 7. MODERN CAMPUS ARCHITECTURE & BACKGROUND BUILDINGS
                // -----------------------------------------------------------------
                const cityGroup = new THREE.Group();
                const windowMats = [];

                function makeBuildingWindowTexture(lit) {{
                    const wc = document.createElement('canvas');
                    wc.width = 64; wc.height = 128;
                    const wctx = wc.getContext('2d');
                    wctx.fillStyle = '#1e293b';
                    wctx.fillRect(0, 0, 64, 128);
                    for (let r = 0; r < 8; r++) {{
                        for (let c = 0; c < 4; c++) {{
                            if (lit) {{
                                const rand = Math.random();
                                wctx.fillStyle = rand > 0.4 ? '#fef08a' : (rand > 0.2 ? '#38bdf8' : '#0f172a');
                            }} else {{
                                wctx.fillStyle = Math.random() > 0.3 ? '#60a5fa' : '#334155';
                            }}
                            wctx.fillRect(c * 15 + 4, r * 15 + 6, 10, 10);
                        }}
                    }}
                    const tex = new THREE.CanvasTexture(wc);
                    tex.wrapS = THREE.RepeatWrapping;
                    tex.wrapT = THREE.RepeatWrapping;
                    return tex;
                }}

                const bldgColors = [0x1e293b, 0x334155, 0x0f172a, 0x1e242d, 0x475569];
                const bldgConfigs = [
                    {{ x: -18, z: -15, w: 9, d: 8, h: 14 }},
                    {{ x: -22, z: 12, w: 10, d: 9, h: 20 }},
                    {{ x: -19, z: 38, w: 8, d: 7, h: 16 }},
                    {{ x: -24, z: 65, w: 11, d: 10, h: 22 }},
                    {{ x: 19, z: -10, w: 9, d: 8, h: 15 }},
                    {{ x: 22, z: 18, w: 10, d: 9, h: 18 }},
                    {{ x: 20, z: 45, w: 8, d: 8, h: 13 }},
                    {{ x: 25, z: 72, w: 12, d: 10, h: 24 }},
                    {{ x: -32, z: 25, w: 14, d: 12, h: 28 }},
                    {{ x: 34, z: 32, w: 13, d: 11, h: 26 }}
                ];

                bldgConfigs.forEach((b, idx) => {{
                    const bGroup = new THREE.Group();
                    bGroup.position.set(b.x, 0, b.z);

                    const bMat = new THREE.MeshStandardMaterial({{
                        color: bldgColors[idx % bldgColors.length],
                        map: makeBuildingWindowTexture(false),
                        roughness: 0.65,
                        metalness: 0.2
                    }});
                    bMat.map.repeat.set(Math.ceil(b.w / 5), Math.ceil(b.h / 5));
                    windowMats.push(bMat);

                    const bMesh = new THREE.Mesh(new THREE.BoxGeometry(b.w, b.h, b.d), bMat);
                    bMesh.position.y = b.h / 2;
                    bMesh.castShadow = true;
                    bMesh.receiveShadow = true;
                    bGroup.add(bMesh);

                    // Modern Rooftop Parapet & Antenna
                    const roofTrim = new THREE.Mesh(new THREE.BoxGeometry(b.w + 0.4, 0.4, b.d + 0.4), new THREE.MeshStandardMaterial({{ color: 0x0f172a }}));
                    roofTrim.position.y = b.h + 0.2;
                    bGroup.add(roofTrim);

                    if (b.h > 16) {{
                        const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.12, 3.5, 6), new THREE.MeshStandardMaterial({{ color: 0x94a3b8 }}));
                        mast.position.y = b.h + 1.8;
                        bGroup.add(mast);

                        const beacon = new THREE.Mesh(new THREE.SphereGeometry(0.2, 8, 8), new THREE.MeshBasicMaterial({{ color: 0xef4444 }}));
                        beacon.position.y = b.h + 3.6;
                        bGroup.add(beacon);
                    }}

                    cityGroup.add(bGroup);
                }});
                scene.add(cityGroup);

                // Build Aura: Cute 3D Robot Companion with Glowing Navigation Stick
                const auraRoot = new THREE.Group();

                // Materials
                const chassisMat = new THREE.MeshStandardMaterial({{ color: 0x0f2b48, metalness: 0.8, roughness: 0.25 }});
                const glowCyanMat = new THREE.MeshStandardMaterial({{ color: 0x00f0ff, emissive: 0x00d9ff, emissiveIntensity: 0.8 }});
                const goldMat = new THREE.MeshStandardMaterial({{ color: 0xf59e0b, metalness: 0.9, roughness: 0.2 }});
                const visorScreenMat = new THREE.MeshStandardMaterial({{ color: 0x030712, roughness: 0.1 }});
                const eyeMat = new THREE.MeshBasicMaterial({{ color: 0x38bdf8 }});

                // Torso & Reactor Core
                const torso = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.32, 0.75, 20), chassisMat);
                torso.position.y = 0.95;
                auraRoot.add(torso);

                const coreReactor = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.04, 16), glowCyanMat);
                coreReactor.rotation.x = Math.PI / 2;
                coreReactor.position.set(0, 0.98, 0.33);
                auraRoot.add(coreReactor);

                // Head with Digital Visor Screen
                const headGroup = new THREE.Group();
                headGroup.position.set(0, 1.55, 0);

                const headChassis = new THREE.Mesh(new THREE.SphereGeometry(0.32, 24, 20), chassisMat);
                headGroup.add(headChassis);

                const visorScreen = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.20, 0.15), visorScreenMat);
                visorScreen.position.set(0, 0.02, 0.26);
                headGroup.add(visorScreen);

                // Glowing Digital Eyes
                const eyeL = new THREE.Mesh(new THREE.SphereGeometry(0.042, 12, 12), eyeMat);
                eyeL.position.set(-0.11, 0.04, 0.34);
                headGroup.add(eyeL);

                const eyeR = new THREE.Mesh(new THREE.SphereGeometry(0.042, 12, 12), eyeMat);
                eyeR.position.set(0.11, 0.04, 0.34);
                headGroup.add(eyeR);

                // Digital Smile
                const smile = new THREE.Mesh(new THREE.TorusGeometry(0.05, 0.012, 8, 16, Math.PI * 0.75), glowCyanMat);
                smile.rotation.x = Math.PI;
                smile.position.set(0, -0.04, 0.34);
                headGroup.add(smile);

                // Cute Antenna with glowing beacon tip
                const antennaStem = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.18, 8), goldMat);
                antennaStem.position.set(0, 0.38, 0);
                headGroup.add(antennaStem);

                const antennaOrb = new THREE.Mesh(new THREE.SphereGeometry(0.05, 12, 12), glowCyanMat);
                antennaOrb.position.set(0, 0.48, 0);
                headGroup.add(antennaOrb);

                auraRoot.add(headGroup);

                // Articulated Arms
                // Left Arm
                const armLGroup = new THREE.Group();
                armLGroup.position.set(-0.46, 1.15, 0);
                const armLMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.04, 0.48, 12), chassisMat);
                armLMesh.position.y = -0.22;
                armLGroup.add(armLMesh);
                auraRoot.add(armLGroup);

                // Right Arm (Holding Glowing Navigation Stick)
                const armRGroup = new THREE.Group();
                armRGroup.position.set(0.46, 1.15, 0);
                const armRMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.04, 0.48, 12), chassisMat);
                armRMesh.position.y = -0.22;
                armRGroup.add(armRMesh);

                // GLOWING NAVIGATION STICK (Aura's signature tool)
                const navStickGroup = new THREE.Group();
                navStickGroup.position.set(0, -0.42, 0.15);

                const stickShaft = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.85, 12), goldMat);
                navStickGroup.add(stickShaft);

                const stickCrystal = new THREE.Mesh(new THREE.SphereGeometry(0.09, 16, 16), glowCyanMat);
                stickCrystal.position.set(0, 0.45, 0);
                navStickGroup.add(stickCrystal);

                // PointLight emitted directly from the navigation stick
                const stickLight = new THREE.PointLight(0x00f0ff, 1.5, 4.0);
                stickLight.position.set(0, 0.45, 0);
                navStickGroup.add(stickLight);

                armRGroup.add(navStickGroup);
                auraRoot.add(armRGroup);

                // Articulated Legs & Magnetic Boots
                const legLGroup = new THREE.Group();
                legLGroup.position.set(-0.20, 0.58, 0);
                const legLMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.06, 0.52, 12), chassisMat);
                legLMesh.position.y = -0.25;
                legLGroup.add(legLMesh);
                const bootL = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.09, 0.22), glowCyanMat);
                bootL.position.set(0, -0.52, 0.04);
                legLGroup.add(bootL);
                auraRoot.add(legLGroup);

                const legRGroup = new THREE.Group();
                legRGroup.position.set(0.20, 0.58, 0);
                const legRMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.06, 0.52, 12), chassisMat);
                legRMesh.position.y = -0.25;
                legRGroup.add(legRMesh);
                const bootR = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.09, 0.22), glowCyanMat);
                bootR.position.set(0, -0.52, 0.04);
                legRGroup.add(bootR);
                auraRoot.add(legRGroup);

                // Glowing Aura Celebration Ring on Ground
                const ringGeo = new THREE.RingGeometry(0.4, 0.65, 24);
                const ringMat = new THREE.MeshBasicMaterial({{ color: 0x00f0ff, side: THREE.DoubleSide, transparent: true, opacity: 0.7 }});
                const auraRing = new THREE.Mesh(ringGeo, ringMat);
                auraRing.rotation.x = -Math.PI / 2;
                auraRing.position.y = 0.05;
                auraRoot.add(auraRing);

                scene.add(auraRoot);

                // Animation Clock
                let clock = new THREE.Clock();

                function renderLoop() {{
                    requestAnimationFrame(renderLoop);
                    const elapsed = clock.getElapsedTime();

                    // Procedural Skeletal Animations
                    if (currentAnimState === 'arrive') {{
                        // Celebratory Jumping & Dual Arm Waves
                        const hop = Math.abs(Math.sin(elapsed * 7.5)) * 0.45;
                        auraRoot.position.y = hop;
                        armRGroup.rotation.z = 0.8 + Math.sin(elapsed * 9) * 0.3;
                        armRGroup.rotation.x = -1.2;
                        armLGroup.rotation.z = -0.8 - Math.sin(elapsed * 9) * 0.3;
                        armLGroup.rotation.x = -1.2;
                        legLGroup.rotation.x = -hop * 0.5;
                        legRGroup.rotation.x = -hop * 0.5;
                        headGroup.rotation.y = Math.sin(elapsed * 4) * 0.25;
                        auraRing.scale.setScalar(1.0 + Math.sin(elapsed * 6) * 0.4);
                        auraRing.material.opacity = 0.9;
                    }} else if (currentAnimState === 'turn_left') {{
                        // Smoothly point stick to the left
                        auraRoot.position.y = 0;
                        auraRoot.rotation.y = THREE.MathUtils.lerp(auraRoot.rotation.y, 0.65, 0.1);
                        headGroup.rotation.y = 0.35;
                        armRGroup.rotation.z = -1.1; // Raise and point left
                        armRGroup.rotation.x = 0.6;
                        navStickGroup.rotation.z = -0.5;
                        armLGroup.rotation.x = 0.2;
                        legLGroup.rotation.x = Math.sin(elapsed * 3) * 0.2;
                        legRGroup.rotation.x = -Math.sin(elapsed * 3) * 0.2;
                        auraRing.material.opacity = 0.3;
                    }} else if (currentAnimState === 'turn_right') {{
                        // Smoothly point stick to the right
                        auraRoot.position.y = 0;
                        auraRoot.rotation.y = THREE.MathUtils.lerp(auraRoot.rotation.y, -0.65, 0.1);
                        headGroup.rotation.y = -0.35;
                        armRGroup.rotation.z = 1.2; // Raise and point right
                        armRGroup.rotation.x = 0.6;
                        navStickGroup.rotation.z = 0.5;
                        armLGroup.rotation.x = 0.2;
                        legLGroup.rotation.x = Math.sin(elapsed * 3) * 0.2;
                        legRGroup.rotation.x = -Math.sin(elapsed * 3) * 0.2;
                        auraRing.material.opacity = 0.3;
                    }} else if (currentAnimState === 'wave') {{
                        // Waving hello
                        auraRoot.position.y = 0;
                        auraRoot.rotation.y = THREE.MathUtils.lerp(auraRoot.rotation.y, 0, 0.1);
                        headGroup.rotation.y = Math.sin(elapsed * 3) * 0.15;
                        armRGroup.rotation.z = 1.3 + Math.sin(elapsed * 10) * 0.35;
                        armRGroup.rotation.x = 0.2;
                        armLGroup.rotation.x = 0.1;
                        legLGroup.rotation.x = 0;
                        legRGroup.rotation.x = 0;
                    }} else if (currentAnimState === 'run') {{
                        // High-speed Stride
                        const stride = Math.sin(elapsed * 10) * 0.85;
                        legLGroup.rotation.x = stride;
                        legRGroup.rotation.x = -stride;
                        armLGroup.rotation.x = -stride * 0.7;
                        armRGroup.rotation.x = stride * 0.7;
                        armRGroup.rotation.z = 0.2;
                        auraRoot.position.y = Math.abs(Math.sin(elapsed * 10)) * 0.12;
                        headGroup.rotation.y = 0;
                    }} else {{
                        // Natural Walking Stride
                        const stride = Math.sin(elapsed * 5.5) * 0.52;
                        legLGroup.rotation.x = stride;
                        legRGroup.rotation.x = -stride;
                        armLGroup.rotation.x = -stride * 0.6;
                        armRGroup.rotation.x = stride * 0.6;
                        armRGroup.rotation.z = 0.15;
                        auraRoot.position.y = Math.abs(Math.sin(elapsed * 5.5)) * 0.06;
                        headGroup.rotation.y = Math.sin(elapsed * 2.5) * 0.1;
                        auraRoot.rotation.y = THREE.MathUtils.lerp(auraRoot.rotation.y, 0, 0.1);
                        auraRing.material.opacity = 0.4;
                    }}

                    // Blinking Visor Eyes
                    const blinkScale = Math.sin(elapsed * 2.5) > 0.96 ? 0.1 : 1.0;
                    eyeL.scale.y = blinkScale;
                    eyeR.scale.y = blinkScale;

                    // Procedural Cloud Drifting
                    cloudList.forEach(c => {{
                        c.obj.position.x += c.speed;
                        if (c.obj.position.x > 85) c.obj.position.x = -85;
                    }});

                    // Gentle Foliage Wind Sway
                    treeSwayList.forEach(t => {{
                        t.group.rotation.z = Math.sin(elapsed * 1.8 + t.phase) * 0.024;
                    }});

                    // Camera Modes
                    if (activeCam === 'pov') {{
                        camera.position.set(0, 1.45, -1.8);
                        camera.lookAt(0, 1.3, 15);
                    }} else if (activeCam === 'iso') {{
                        camera.position.set(4.5, 5.2, -4.5);
                        camera.lookAt(0, 0.9, 2.0);
                    }} else {{
                        // 3D Follow Drone
                        camera.position.set(0, 2.3, -4.2);
                        camera.lookAt(0, 1.1, 3.0);
                    }}

                    renderer.render(scene, camera);
                }}

                renderLoop();

                // Environment Lighting Controller
                threeEnv = {{
                    updateLighting: function(env) {{
                        if (env === 'sunset') {{
                            scene.background = new THREE.Color(0xf97316);
                            scene.fog.color = new THREE.Color(0x6b21a8);
                            scene.fog.density = 0.009;
                            skyMesh.material.map = makeSkyTexture('#311042', '#ea580c', '#fde047');
                            hemiLight.color.setHex(0xfb923c);
                            hemiLight.groundColor.setHex(0x78350f);
                            hemiLight.intensity = 0.85;
                            ambientLight.color.setHex(0xfbbf24);
                            ambientLight.intensity = 0.45;
                            dirLight.color.setHex(0xf97316);
                            dirLight.intensity = 1.4;
                            dirLight.position.set(40, 22, 10);
                            sunMesh.material.opacity = 1.0;
                            sunGlowMesh.material.opacity = 0.55;
                            moonMesh.material.opacity = 0.2;
                            starMat.opacity = 0.15;
                            cloudMat.color.setHex(0xfca5a5);
                            lampLights.forEach(l => {{
                                l.light.intensity = 0.75;
                                l.glass.material.color.setHex(0xfde047);
                            }});
                            windowMats.forEach(m => {{ m.map = makeBuildingWindowTexture(true); }});
                        }} else if (env === 'night') {{
                            scene.background = new THREE.Color(0x020617);
                            scene.fog.color = new THREE.Color(0x030712);
                            scene.fog.density = 0.012;
                            skyMesh.material.map = makeSkyTexture('#020617', '#091124', '#0f172a');
                            hemiLight.color.setHex(0x0f172a);
                            hemiLight.groundColor.setHex(0x020617);
                            hemiLight.intensity = 0.35;
                            ambientLight.color.setHex(0x1e293b);
                            ambientLight.intensity = 0.25;
                            dirLight.color.setHex(0x38bdf8);
                            dirLight.intensity = 0.55;
                            dirLight.position.set(-25, 45, 20);
                            sunMesh.material.opacity = 0;
                            sunGlowMesh.material.opacity = 0;
                            moonMesh.material.opacity = 0.95;
                            starMat.opacity = 0.95;
                            cloudMat.color.setHex(0x334155);
                            lampLights.forEach(l => {{
                                l.light.intensity = 1.8;
                                l.glass.material.color.setHex(0xfef08a);
                            }});
                            windowMats.forEach(m => {{ m.map = makeBuildingWindowTexture(true); }});
                        }} else {{
                            // Day
                            scene.background = new THREE.Color(0x38bdf8);
                            scene.fog.color = new THREE.Color(0xc7d2fe);
                            scene.fog.density = 0.0075;
                            skyMesh.material.map = makeSkyTexture('#1d4ed8', '#38bdf8', '#e0f2fe');
                            hemiLight.color.setHex(0x7dd3fc);
                            hemiLight.groundColor.setHex(0x15803d);
                            hemiLight.intensity = 0.85;
                            ambientLight.color.setHex(0xffffff);
                            ambientLight.intensity = 0.35;
                            dirLight.color.setHex(0xfffaed);
                            dirLight.intensity = 1.35;
                            dirLight.position.set(28, 52, 28);
                            sunMesh.material.opacity = 1.0;
                            sunGlowMesh.material.opacity = 0.35;
                            moonMesh.material.opacity = 0;
                            starMat.opacity = 0;
                            cloudMat.color.setHex(0xffffff);
                            lampLights.forEach(l => {{
                                l.light.intensity = 0.0;
                                l.glass.material.color.setHex(0xffffff);
                            }});
                            windowMats.forEach(m => {{ m.map = makeBuildingWindowTexture(false); }});
                        }}
                    }}
                }};

                window.addEventListener('resize', () => {{
                    const w = container.clientWidth;
                    const h = container.clientHeight;
                    if (w && h) {{
                        camera.aspect = w / h;
                        camera.updateProjectionMatrix();
                        renderer.setSize(w, h);
                    }}
                }});
            }} catch(e) {{
                console.warn("Three.js init error:", e);
            }}
        }}

        function syncIframeHeight() {{
            try {{
                const root = document.getElementById('aura-journey-root');
                if (root) {{
                    const h = Math.ceil(root.getBoundingClientRect().height + 25);
                    if (window.frameElement) {{
                        window.frameElement.style.height = h + 'px';
                        window.frameElement.height = h;
                    }}
                    if (window.parent && window.parent !== window) {{
                        window.parent.postMessage({{ type: 'streamlit:setFrameHeight', height: h }}, '*');
                    }}
                }}
            }} catch(e) {{}}
        }}
        window.addEventListener('load', syncIframeHeight);
        window.addEventListener('resize', syncIframeHeight);
        setTimeout(syncIframeHeight, 100);
        setTimeout(syncIframeHeight, 400);
        setTimeout(syncIframeHeight, 1200);

        // Initialize
        renderPipeline();
        initSensorWatchers();
        startStepProgressionLoop();
        updateMotionUI(isLiveMoving ? currentSpeedKmh : 0.0, motionState, isLiveMoving ? '🛰️ Parallel Sensor GPS' : 'Sensor Ready');
        // Auto-synchronize real-time environment lighting
        setTimeout(() => {{
            const autoEnv = getRealTimeEnv();
            window.setEnvLight(autoEnv, true);
        }}, 120);
        setTimeout(initAuraThreeScene, 80);
    }})();
    </script>
    """
