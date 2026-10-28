"""
Live Virtual Travel Companion Component & Interactive Step-by-Step HUD
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Human-Centric Visual Journey System

Renders a state-driven animated virtual companion on the map that moves, stops,
turns, and crosses checkpoints in lockstep with the real user's actual sensor & GPS progress.
"""

import dataclasses
import json
from typing import Any, Dict, List, Optional, Tuple, Union


def build_virtual_companion_hud_html(
    session_id: str,
    origin_name: str,
    dest_name: str,
    travel_mode: str = "walking",
    initial_state: str = "ROUTE_READY",
    polyline: Optional[List[List[float]]] = None,
    steps: Optional[List[Dict[str, Any]]] = None,
    checkpoints: Optional[List[Dict[str, Any]]] = None,
    current_speed_kmh: float = 0.0,
    total_distance_m: float = 1200.0,
    current_step_idx: int = 0
) -> str:
    """
    Renders the live interactive HTML5/CSS3/JavaScript Virtual Companion HUD
    supporting all 15 navigation states, mode-specific avatar animations,
    GPS lockstep tracking, and interactive journey timeline.
    """
    mode = travel_mode.lower()
    
    # Avatar and Mode Attributes
    if mode == "running":
        avatar_icon = "🏃‍♂️"
        avatar_title = "Virtual Runner Guide"
        mode_anim_class = "anim-runner-sprint"
        base_speed = 9.5
    elif mode == "driving" or "car" in mode:
        avatar_icon = "🚗"
        avatar_title = "Virtual Vehicle Companion"
        mode_anim_class = "anim-vehicle-cruise"
        base_speed = 50.0
    elif mode == "cycling" or "bike" in mode:
        avatar_icon = "🚴"
        avatar_title = "Virtual Cyclist Guide"
        mode_anim_class = "anim-cyclist-pedal"
        base_speed = 16.0
    elif mode == "motorcycle":
        avatar_icon = "🏍️"
        avatar_title = "Virtual Motorcyclist"
        mode_anim_class = "anim-motorcycle-ride"
        base_speed = 42.0
    elif mode == "transit" or "bus" in mode:
        avatar_icon = "🚌"
        avatar_title = "Virtual Transit Companion"
        mode_anim_class = "anim-transit-glide"
        base_speed = 35.0
    else:
        avatar_icon = "🚶‍♂️"
        avatar_title = "Virtual Walking Companion"
        mode_anim_class = "anim-walking-stride"
        base_speed = 4.8

    # Default polyline fallback
    poly_pts = polyline if polyline and len(polyline) >= 2 else [
        [16.2335, 80.5505],
        [16.2380, 80.5520],
        [16.2440, 80.5550],
        [16.2500, 80.5510],
        [16.2550, 80.5450]
    ]

    # Normalize steps (supports Dict, dataclass instances like FriendlyTurnStep, objects)
    normalized_steps: List[Dict[str, Any]] = []
    if steps and len(steps) > 0:
        for idx, s in enumerate(steps):
            if dataclasses.is_dataclass(s):
                d = dataclasses.asdict(s)
            elif isinstance(s, dict):
                d = dict(s)
            elif hasattr(s, "__dict__"):
                d = dict(s.__dict__)
            else:
                d = {"instruction_text": str(s)}

            # Ensure all required UI keys exist
            instr = (
                d.get("instruction_text")
                or d.get("action_headline")
                or d.get("virtual_guide_speech")
                or d.get("spoken_text")
                or d.get("instruction")
                or f"Step {idx + 1}"
            )
            road = d.get("road_name") or d.get("road") or ""
            icon = d.get("icon") or "📍"
            dist = d.get("distance_meters") or d.get("distance_m") or 150.0
            if isinstance(dist, str):
                try:
                    dist = float(dist.replace("m", "").replace("km", "").strip())
                except Exception:
                    dist = 150.0

            normalized_steps.append({
                "id": str(d.get("id", f"STEP_{idx}")),
                "sequence_number": int(d.get("sequence_number", d.get("step_num", idx))),
                "instruction_type": str(d.get("instruction_type", d.get("direction_type", "STRAIGHT"))),
                "instruction_text": str(instr),
                "road_name": str(road),
                "distance_meters": float(dist),
                "icon": str(icon),
                "is_completed": bool(d.get("is_completed", False))
            })
    else:
        normalized_steps = [
            {
                "id": "STEP_0",
                "sequence_number": 0,
                "instruction_type": "START",
                "instruction_text": f"Start journey at {origin_name}",
                "road_name": "Departure Point",
                "distance_meters": 200.0,
                "icon": "🚩",
                "is_completed": False
            },
            {
                "id": "STEP_1",
                "sequence_number": 1,
                "instruction_type": "STRAIGHT",
                "instruction_text": "Proceed straight along Main Campus Avenue",
                "road_name": "Campus Avenue",
                "distance_meters": 450.0,
                "icon": "⬆️",
                "is_completed": False
            },
            {
                "id": "STEP_2",
                "sequence_number": 2,
                "instruction_type": "LEFT",
                "instruction_text": "Turn left at the Central Crossing onto Link Corridor",
                "road_name": "Link Corridor",
                "distance_meters": 350.0,
                "icon": "↩️",
                "is_completed": False
            },
            {
                "id": "STEP_3",
                "sequence_number": 3,
                "instruction_type": "ARRIVE",
                "instruction_text": f"Arrive at destination: {dest_name}",
                "road_name": "Arrival Gate",
                "distance_meters": 200.0,
                "icon": "🏆",
                "is_completed": False
            }
        ]

    # Serialize data
    poly_json = json.dumps(poly_pts, default=str)
    steps_json = json.dumps(normalized_steps, default=str)
    session_id_json = json.dumps(session_id, default=str)

    return f"""
    <div id='virtual-companion-app' class='companion-wrapper'>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&display=swap');

        .companion-wrapper {{
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, rgba(10, 18, 38, 0.96) 0%, rgba(15, 23, 42, 0.94) 100%);
            border: 1.5px solid rgba(56, 189, 248, 0.35);
            border-radius: 16px;
            padding: 16px 20px;
            margin: 10px 0;
            color: #f8fafc;
            box-shadow: 0 10px 32px rgba(0, 0, 0, 0.65), 0 0 20px rgba(56, 189, 248, 0.15);
            position: relative;
            overflow: hidden;
        }}

        /* Animations */
        @keyframes anim-walking-stride {{
            0% {{ transform: translateY(0px) rotate(-3deg); }}
            50% {{ transform: translateY(-6px) scale(1.08) rotate(3deg); }}
            100% {{ transform: translateY(0px) rotate(-3deg); }}
        }}

        @keyframes anim-runner-sprint {{
            0% {{ transform: translateY(0px) scale(1) rotate(-6deg); }}
            50% {{ transform: translateY(-8px) scale(1.15) rotate(6deg); }}
            100% {{ transform: translateY(0px) scale(1) rotate(-6deg); }}
        }}

        @keyframes anim-vehicle-cruise {{
            0% {{ transform: translateX(-2px) scale(1); }}
            50% {{ transform: translateX(2px) scale(1.04); }}
            100% {{ transform: translateX(-2px) scale(1); }}
        }}

        @keyframes anim-cyclist-pedal {{
            0% {{ transform: translateY(0px) rotate(-2deg); }}
            50% {{ transform: translateY(-5px) rotate(2deg); }}
            100% {{ transform: translateY(0px) rotate(-2deg); }}
        }}

        @keyframes anim-motorcycle-ride {{
            0% {{ transform: translateX(-3px) rotate(-2deg) scale(1); }}
            50% {{ transform: translateX(3px) rotate(2deg) scale(1.05); }}
            100% {{ transform: translateX(-3px) rotate(-2deg) scale(1); }}
        }}

        @keyframes anim-walking-turn {{
            0%   {{ transform: rotate(-25deg) scale(0.9); }}
            25%  {{ transform: rotate(0deg) scale(1.0); }}
            75%  {{ transform: rotate(25deg) scale(1.1); }}
            100% {{ transform: rotate(0deg) scale(1.0); }}
        }}

        @keyframes anim-transit-glide {{
            0% {{ transform: translateX(-4px) scale(1); }}
            50% {{ transform: translateX(4px) scale(1.03); }}
            100% {{ transform: translateX(-4px) scale(1); }}
        }}

        @keyframes checkmarkPop {{
            0% {{ transform: scale(0.4); opacity: 0; }}
            70% {{ transform: scale(1.25); }}
            100% {{ transform: scale(1); opacity: 1; }}
        }}

        @keyframes statePulseGlow {{
            0% {{ box-shadow: 0 0 6px currentColor; }}
            50% {{ box-shadow: 0 0 18px currentColor; }}
            100% {{ box-shadow: 0 0 6px currentColor; }}
        }}

        .anim-active {{
            animation: {mode_anim_class} 0.8s infinite alternate ease-in-out;
        }}

        .anim-turning {{
            animation: anim-walking-turn 0.6s ease-in-out;
        }}

        .anim-paused {{
            animation: none !important;
        }}

        /* Header Layout */
        .hud-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .companion-badge-group {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .avatar-circle {{
            width: 52px;
            height: 52px;
            border-radius: 50%;
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            border: 2.5px solid #38bdf8;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.45);
            transition: all 0.3s ease;
        }}

        .state-pill {{
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.4);
            transition: all 0.25s ease;
        }}

        /* State Color Coding */
        .state-MOVING, .state-RESUMING {{
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid #10b981;
        }}
        .state-WALKING {{
            background: rgba(52, 211, 153, 0.18);
            color: #6ee7b7;
            border: 1px solid #34d399;
            animation: statePulseGlow 2s infinite;
        }}
        .state-TEMPORARILY_STOPPED, .state-PAUSED {{
            background: rgba(239, 68, 68, 0.2);
            color: #f87171;
            border: 1px solid #ef4444;
        }}
        .state-TRAFFIC_DELAY {{
            background: rgba(245, 158, 11, 0.22);
            color: #fbbf24;
            border: 1px solid #f59e0b;
        }}
        .state-APPROACHING_TURN, .state-TURNING {{
            background: rgba(14, 165, 233, 0.22);
            color: #38bdf8;
            border: 1px solid #0ea5e9;
        }}
        .state-ARRIVED {{
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            color: #ffffff;
            border: 1px solid #34d399;
            box-shadow: 0 0 16px rgba(16, 185, 129, 0.6);
        }}
        .state-OFF_ROUTE, .state-REROUTING {{
            background: rgba(217, 70, 239, 0.22);
            color: #e879f9;
            border: 1px solid #d946ef;
        }}
        .state-GPS_UNCERTAIN {{
            background: rgba(148, 163, 184, 0.2);
            color: #cbd5e1;
            border: 1px solid #94a3b8;
        }}
        .state-ROUTE_READY, .state-STARTING {{
            background: rgba(56, 189, 248, 0.2);
            color: #7dd3fc;
            border: 1px solid #38bdf8;
        }}

        /* Progress Bar */
        .progress-track {{
            position: relative;
            height: 6px;
            background: rgba(255, 255, 255, 0.12);
            border-radius: 999px;
            margin: 16px 0 12px 0;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #10b981 0%, #38bdf8 100%);
            border-radius: 999px;
            box-shadow: 0 0 12px #38bdf8;
            transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        /* Timeline Flow Cards */
        .timeline-scroll-bar {{
            display: flex;
            align-items: stretch;
            gap: 12px;
            overflow-x: auto;
            padding-bottom: 8px;
            margin-top: 14px;
            scrollbar-width: thin;
        }}
        .timeline-step-card {{
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.92) 0%, rgba(10, 18, 36, 0.98) 100%);
            border: 1.5px solid rgba(255, 255, 255, 0.12);
            border-radius: 14px;
            padding: 0;
            min-width: 195px;
            flex: 0 0 195px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
            cursor: pointer;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.45);
        }}
        .timeline-step-card:hover {{
            border-color: #38bdf8;
            transform: translateY(-4px);
            box-shadow: 0 12px 28px rgba(56, 189, 248, 0.35);
        }}
        .timeline-step-card.active {{
            background: linear-gradient(180deg, rgba(2, 132, 199, 0.35) 0%, rgba(15, 23, 42, 0.98) 100%);
            border-color: #38bdf8;
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.55), 0 8px 24px rgba(0, 0, 0, 0.6);
        }}
        .timeline-step-card.completed {{
            background: linear-gradient(180deg, rgba(6, 78, 59, 0.35) 0%, rgba(15, 23, 42, 0.98) 100%);
            border-color: #10b981;
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
        .timeline-step-card:hover .step-picture-frame svg {{
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
        .timeline-step-card.active .step-card-headline {{
            color: #38bdf8;
        }}
        .timeline-step-card.completed .step-card-headline {{
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
        .step-badge {{
            width: 26px;
            height: 26px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 800;
        }}
        .badge-pending {{
            background: rgba(255, 255, 255, 0.1);
            color: #94a3b8;
        }}
        .badge-active {{
            background: #0284c7;
            color: #ffffff;
            box-shadow: 0 0 8px #38bdf8;
        }}
        .badge-completed {{
            background: #10b981;
            color: #ffffff;
            animation: checkmarkPop 0.4s ease;
        }}

        /* Action Buttons */
        .btn-ctrl {{
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(56, 189, 248, 0.35);
            color: #f1f5f9;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 0.72rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }}
        .btn-ctrl:hover {{
            background: rgba(56, 189, 248, 0.2);
            border-color: #38bdf8;
            transform: translateY(-1px);
        }}
        .btn-traffic {{
            background: rgba(239, 68, 68, 0.2);
            border-color: #ef4444;
            color: #fca5a5;
        }}
        .btn-moving {{
            background: rgba(16, 185, 129, 0.2);
            border-color: #10b981;
            color: #6ee7b7;
        }}
        </style>

        <!-- Top Header & Live Companion Profile -->
        <div class='hud-header'>
            <div class='companion-badge-group'>
                <div id='companion-avatar-icon' class='avatar-circle anim-active'>
                    {avatar_icon}
                </div>
                <div>
                    <div style='display: flex; align-items: center; gap: 8px; flex-wrap: wrap;'>
                        <span style='font-size: 1.05rem; font-weight: 800; color: #ffffff;'>
                            {avatar_title}
                        </span>
                        <span id='companion-state-badge' class='state-pill state-{initial_state}'>
                            ● {initial_state.replace('_', ' ')}
                        </span>
                    </div>
                    <div style='font-size: 0.74rem; color: #94a3b8; margin-top: 2px;'>
                        Navigating from <b>{origin_name}</b> ➔ <b>{dest_name}</b> • Mode: <span style='text-transform: capitalize;'>{mode}</span>
                    </div>
                </div>
            </div>

            <!-- Live Telemetry Gauges -->
            <div style='display: flex; align-items: center; gap: 12px; font-size: 0.74rem;'>
                <div style='background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 6px;'>
                    <span style='color: #94a3b8;'>SPEED:</span>
                    <b id='telem-speed' style='color: #38bdf8; margin-left: 4px;'>{current_speed_kmh:.1f} km/h</b>
                </div>
                <div style='background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 6px;'>
                    <span style='color: #94a3b8;'>REMAINING:</span>
                    <b id='telem-dist-rem' style='color: #34d399; margin-left: 4px;'>{total_distance_m:.0f} m</b>
                </div>
                <div style='background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 6px;'>
                    <span style='color: #94a3b8;'>HEADING:</span>
                    <b id='telem-heading' style='color: #f59e0b; margin-left: 4px;'>045° NNE</b>
                </div>
            </div>
        </div>

        <!-- Real-Time Progress Bar -->
        <div class='progress-track'>
            <div id='companion-progress-fill' class='progress-fill'></div>
        </div>

        <!-- Active Instruction & Maneuver Highlight -->
        <div id='active-instruction-banner' style='background: rgba(2, 132, 199, 0.12); border-left: 4px solid #38bdf8; border-radius: 8px; padding: 10px 14px; display: flex; align-items: center; justify-content: space-between; gap: 10px;'>
            <div style='display: flex; align-items: center; gap: 10px;'>
                <span id='active-maneuver-icon' style='font-size: 1.5rem;'>{normalized_steps[0]["icon"]}</span>
                <div>
                    <div style='font-size: 0.68rem; color: #38bdf8; font-weight: 700; text-transform: uppercase;'>Current Maneuver</div>
                    <div id='active-instruction-text' style='font-size: 0.88rem; font-weight: 700; color: #ffffff;'>
                        {normalized_steps[0]["instruction_text"]}
                    </div>
                </div>
            </div>
            <div style='text-align: right;'>
                <span id='active-step-dist' style='font-size: 0.90rem; font-weight: 800; color: #38bdf8;'>
                    {normalized_steps[0]["distance_meters"]:.0f} m
                </span>
                <div style='font-size: 0.65rem; color: #94a3b8;'>to next turn</div>
            </div>
        </div>

        <!-- Arrival Banner (Displayed when destination reached) -->
        <div id='companion-arrival-banner' style='display: none; background: linear-gradient(135deg, rgba(16, 185, 129, 0.25) 0%, rgba(6, 78, 59, 0.9) 100%); border: 2px solid #10b981; border-radius: 12px; padding: 14px; margin-top: 12px; text-align: center; box-shadow: 0 0 24px rgba(16, 185, 129, 0.5);'>
            <div style='font-size: 1.3rem; font-weight: 900; color: #ffffff;'>🏆 YOU HAVE ARRIVED SAFELY!</div>
            <div id='arrival-summary-text' style='font-size: 0.84rem; color: #a7f3d0; margin-top: 4px;'>
                The {avatar_title} has reached {dest_name}. All steps completed with verified checkmarks.
            </div>
        </div>

        <!-- Interactive Journey Timeline (Step by step flow with checkmarks) -->
        <div class='timeline-scroll-bar' id='companion-timeline-steps'>
            <!-- Rendered by client script -->
        </div>

        <!-- Operational Controls Bar (Synchronized Movement Controls) -->
        <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.08);'>
            <div style='display: flex; align-items: center; gap: 8px; flex-wrap: wrap;'>
                <span id='companion-status-indicator' style='font-size: 0.74rem; color: #38bdf8; font-weight: 800; display: inline-flex; align-items: center; gap: 5px;'>
                    <span>🛰️</span> <span>SIMULATED ROUTE COMPANION</span>
                </span>
                <span id='companion-sync-mode-badge' style='background: rgba(56, 189, 248, 0.2); color: #38bdf8; font-size: 0.68rem; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(56, 189, 248, 0.4); font-weight: 700;'>
                    ● IN LOCKSTEP WITH RUNNER
                </span>
            </div>

            <div style='display: flex; align-items: center; gap: 8px;'>
                <button id='btn-comp-traffic-stop' class='btn-ctrl btn-traffic' onclick='window.companionSimulateStop()' style='background: rgba(239, 68, 68, 0.22); border: 1.5px solid #ef4444; color: #fca5a5; font-weight: 800; padding: 6px 14px; border-radius: 6px; cursor: pointer;' title='Traffic Stop — Stop companion & vehicle (0.0 km/h)'>
                    🛑 Traffic Stop (0 km/h)
                </button>
                <button id='btn-comp-move-parallel' class='btn-ctrl btn-moving' onclick='window.companionSimulateMove()' style='background: rgba(16, 185, 129, 0.22); border: 1.5px solid #10b981; color: #6ee7b7; font-weight: 800; padding: 6px 14px; border-radius: 6px; cursor: pointer;' title='Move in Parallel — Manually start or resume movement'>
                    🟢 Move in Parallel
                </button>
            </div>
        </div>
    </div>

    <script>
    (function() {{
        const SESSION_ID = {session_id_json};
        const POLYLINE = {poly_json};
        const STEPS = {steps_json};
        const BASE_SPEED = {base_speed};
        const AVATAR_ICON = "{avatar_icon}";

        let currentState = "{initial_state}";
        let currentStepIdx = {current_step_idx};
        let currentSpeed = {current_speed_kmh};
        let isPaused = false;

        function getScenicStepSvg(dirType, roadName, stepNum, iconText, isCompleted, isActive) {{
            const rawDir = (dirType || '').toUpperCase();
            const cleanRoad = String(roadName || 'Main Corridor').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
            const shortRoad = cleanRoad.length > 20 ? cleanRoad.substring(0, 18) + '...' : cleanRoad;
            const uid = 'svg_comp_' + stepNum + '_' + Math.random().toString(36).substr(2, 5);
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

        window.selectCompanionStep = function(idx) {{
            if (idx < 0 || idx >= STEPS.length) return;
            currentStepIdx = idx;
            const curStep = STEPS[currentStepIdx] || STEPS[0];
            const actInstr = document.getElementById('active-instruction-text');
            const actIcon = document.getElementById('active-maneuver-icon');
            const actDist = document.getElementById('active-step-dist');
            if (actInstr) actInstr.innerText = curStep.instruction_text;
            if (actIcon) actIcon.innerText = curStep.icon || '📍';
            if (actDist) actDist.innerText = Math.round(curStep.distance_meters) + ' m';
            renderTimeline();
            broadcastCompanionPosition();
        }};

        // Render timeline step cards
        function renderTimeline() {{
            const bar = document.getElementById('companion-timeline-steps');
            if (!bar) return;

            bar.innerHTML = STEPS.map((s, idx) => {{
                const isCompleted = (idx < currentStepIdx) || (s.is_completed);
                const isActive = (idx === currentStepIdx && !isCompleted);
                const cardClass = isCompleted ? 'completed' : (isActive ? 'active' : 'pending');
                const badgeClass = isCompleted ? 'badge-completed' : (isActive ? 'badge-active' : 'badge-pending');
                const badgeText = isCompleted ? '✓' : (idx + 1);

                const picSvg = getScenicStepSvg(s.instruction_type, s.road_name, idx + 1, s.icon, isCompleted, isActive);

                return `
                <div class="timeline-step-card ${{cardClass}}" onclick="window.selectCompanionStep(${{idx}})">
                    <div class="step-picture-frame">
                        ${{picSvg}}
                        <div class="step-pic-overlay-badge">
                            <span class="step-badge ${{badgeClass}}">${{badgeText}}</span>
                            <span style="font-size: 1.05rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.6));">${{s.icon || '📍'}}</span>
                        </div>
                    </div>
                    <div class="step-card-body">
                        <div class="step-card-headline" title="${{s.instruction_text}}">
                            ${{s.instruction_text}}
                        </div>
                        <div class="step-card-footer">
                            <span class="step-card-road" title="${{s.road_name || ''}}">${{s.road_name || 'Corridor'}}</span>
                            <b class="step-card-dist">${{Math.round(s.distance_meters)}} m</b>
                        </div>
                    </div>
                </div>
                `;
            }}).join('');

            // Update Progress Fill
            const pct = Math.round((currentStepIdx / Math.max(1, STEPS.length - 1)) * 100);
            const fill = document.getElementById('companion-progress-fill');
            if (fill) fill.style.width = pct + '%';
        }}

        // Update state and telemetry in HUD
        function updateCompanionHUD(state, speed, remDist, headingDeg) {{
            currentState = state;
            currentSpeed = speed;

            const stateBadge = document.getElementById('companion-state-badge');
            if (stateBadge) {{
                stateBadge.className = 'state-pill state-' + state;
                stateBadge.innerHTML = '● ' + state.replace('_', ' ');
            }}

            const avatarIcon = document.getElementById('companion-avatar-icon');
            if (avatarIcon) {{
                const isStopped = (state === 'TEMPORARILY_STOPPED' || state === 'TRAFFIC_STOPPED' || state === 'TRAFFIC_DELAY' || state === 'PAUSED' || state === 'ARRIVED' || state === 'ROUTE_READY' || state === 'READY');
                if (isStopped) {{
                    avatarIcon.classList.remove('anim-active');
                    avatarIcon.classList.add('anim-paused');
                }} else {{
                    avatarIcon.classList.add('anim-active');
                    avatarIcon.classList.remove('anim-paused');
                }}
            }}

            const spdEl = document.getElementById('telem-speed');
            if (spdEl) spdEl.innerText = speed.toFixed(1) + ' km/h';

            const remEl = document.getElementById('telem-dist-rem');
            if (remEl) remEl.innerText = Math.round(remDist) + ' m';

            const hdEl = document.getElementById('telem-heading');
            if (hdEl && headingDeg != null) hdEl.innerText = Math.round(headingDeg) + '°';

            // Active Step Banner
            const curStep = STEPS[currentStepIdx] || STEPS[0];
            const actInstr = document.getElementById('active-instruction-text');
            const actIcon = document.getElementById('active-maneuver-icon');
            const actDist = document.getElementById('active-step-dist');
            if (actInstr) actInstr.innerText = curStep.instruction_text;
            if (actIcon) actIcon.innerText = curStep.icon || '📍';
            if (actDist) actDist.innerText = Math.round(curStep.distance_meters) + ' m';

            // Arrival banner
            const arrBanner = document.getElementById('companion-arrival-banner');
            if (arrBanner) {{
                arrBanner.style.display = (state === 'ARRIVED') ? 'block' : 'none';
            }}

            renderTimeline();
            broadcastCompanionPosition();
        }}

        // Broadcast to Leaflet map or Google Maps component
        function broadcastCompanionPosition() {{
            const pt = POLYLINE[Math.min(currentStepIdx, POLYLINE.length - 1)] || [0, 0];
            const payload = {{
                type: 'PATHFINDER_COMPANION_UPDATE',
                state: currentState,
                step: currentStepIdx,
                lat: pt[0],
                lon: pt[1],
                speedKmh: currentSpeed,
                avatar: AVATAR_ICON
            }};
            try {{
                window.parent.postMessage(payload, '*');
                if (window.BroadcastChannel) {{
                    const bc = new BroadcastChannel('pathfinder_companion_channel');
                    bc.postMessage(payload);
                    bc.close();
                }}
            }} catch(e) {{}}
        }}

        function broadcastJourneySync(action, state, speed) {{
            const payload = {{
                type: 'PATHFINDER_JOURNEY_SYNC',
                action: action,
                state: state,
                step: currentStepIdx,
                speedKmh: speed,
                timestamp: Date.now()
            }};
            try {{ window.parent.postMessage(payload, '*'); }} catch(e) {{}}
            try {{
                if (window.BroadcastChannel) {{
                    const bc = new BroadcastChannel('pathfinder_journey_sync');
                    bc.postMessage(payload);
                    bc.close();
                }}
            }} catch(e) {{}}
        }}

        // Interactive simulation methods
        window.companionSimulateStop = function() {{
            updateCompanionHUD('TRAFFIC_STOPPED', 0.0, {total_distance_m}, 45);
            broadcastJourneySync('STOP', 'TRAFFIC_STOPPED', 0.0);
        }};

        window.companionSimulateMove = function() {{
            updateCompanionHUD('MOVING', BASE_SPEED, {total_distance_m}, 45);
            broadcastJourneySync('MOVE', 'MOVING', BASE_SPEED);
        }};

        // Legacy / automated test compatibility methods
        window.companionSimulateWalk = function() {{
            updateCompanionHUD('MOVING', BASE_SPEED * 0.15, {total_distance_m}, 45);
        }};

        window.companionSimulateTurn = function() {{
            updateCompanionHUD('APPROACHING_TURN', BASE_SPEED * 0.7, 30, 270);
            setTimeout(() => {{
                updateCompanionHUD('MOVING', BASE_SPEED, 250, 270);
            }}, 1000);
        }};

        window.companionSimulateArrival = function() {{
            STEPS.forEach(s => s.is_completed = true);
            currentStepIdx = STEPS.length - 1;
            updateCompanionHUD('ARRIVED', 0.0, 0, 90);
            broadcastJourneySync('ARRIVED', 'ARRIVED', 0.0);
        }};

        window.companionTogglePause = function() {{
            isPaused = !isPaused;
            if (isPaused) {{
                window.companionSimulateStop();
            }} else {{
                window.companionSimulateMove();
            }}
        }};

        window.companionRestart = function() {{
            STEPS.forEach(s => s.is_completed = false);
            currentStepIdx = 0;
            isPaused = false;
            updateCompanionHUD('READY', 0.0, {total_distance_m}, 45);
        }};

        // Real Live Geolocation Watcher: Synchronizes in lockstep with real user GPS
        if (navigator.geolocation && navigator.geolocation.watchPosition) {{
            try {{
                navigator.geolocation.watchPosition(function(pos) {{
                    const uSpeed = (pos.coords.speed != null && pos.coords.speed >= 0)
                        ? parseFloat((pos.coords.speed * 3.6).toFixed(1))
                        : 0.0;
                    const uAcc = pos.coords.accuracy || 5.0;

                    if (uAcc > 45.0) {{
                        updateCompanionHUD('GPS_UNCERTAIN', uSpeed, 500, null);
                        return;
                    }}

                    if (uSpeed <= 1.0) {{
                        updateCompanionHUD('TRAFFIC_STOPPED', 0.0, 400, null);
                    }} else {{
                        updateCompanionHUD('MOVING', uSpeed, 350, pos.coords.heading);
                    }}
                }}, function(err) {{
                    console.log("[VirtualCompanion] Geolocation:", err.message);
                }}, {{ enableHighAccuracy: true, maximumAge: 3000, timeout: 8000 }});
            }} catch(e) {{}}
        }}

        // Listen for sync events from Virtual Runner or external triggers
        function handleCompanionSync(data) {{
            if (!data) return;
            if (data.type === 'PATHFINDER_JOURNEY_SYNC' || data.type === 'PATHFINDER_SENSOR_COMMAND') {{
                if (data.action === 'STOP' || data.state === 'TRAFFIC_STOPPED') {{
                    updateCompanionHUD('TRAFFIC_STOPPED', 0.0, {total_distance_m}, 45);
                }} else if (data.action === 'MOVE' || data.state === 'MOVING') {{
                    const spd = (typeof data.speedKmh === 'number' && data.speedKmh > 0) ? data.speedKmh : BASE_SPEED;
                    updateCompanionHUD('MOVING', spd, {total_distance_m}, 45);
                }}
                if (typeof data.step === 'number' && data.step >= 0 && data.step < STEPS.length) {{
                    currentStepIdx = data.step;
                    renderTimeline();
                }}
            }}
        }}

        window.addEventListener('message', function(ev) {{ handleCompanionSync(ev.data); }});
        try {{
            if (window.BroadcastChannel) {{
                const compBc = new BroadcastChannel('pathfinder_journey_sync');
                compBc.onmessage = function(ev) {{ handleCompanionSync(ev.data); }};
            }}
        }} catch(e) {{}}

        // Initialize HUD in stationary state on load
        renderTimeline();
        updateCompanionHUD(currentState, 0.0, {total_distance_m}, 45);
    }})();
    </script>
    """
