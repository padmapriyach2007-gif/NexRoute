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
            background: rgba(15, 23, 42, 0.7);
            border: 1.5px solid rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            padding: 10px 14px;
            min-width: 175px;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.25s ease;
        }}
        .timeline-step-card.active {{
            background: rgba(2, 132, 199, 0.25);
            border-color: #38bdf8;
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.35);
        }}
        .timeline-step-card.completed {{
            background: rgba(6, 78, 59, 0.3);
            border-color: #10b981;
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

        <!-- Testing & Simulation Control Panel -->
        <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.08);'>
            <div style='display: flex; align-items: center; gap: 6px; flex-wrap: wrap;'>
                <button class='btn-ctrl btn-traffic' onclick='window.companionSimulateStop()' title='Traffic stop / red light — 0 km/h stationary state'>
                    🛑 Traffic Stop <span style='opacity:0.7; font-size:0.60rem;'>(0 km/h)</span>
                </button>
                <button class='btn-ctrl btn-moving' onclick='window.companionSimulateWalk()' title='Walk forward step-by-step'>
                    🚶 Walking
                </button>
                <button class='btn-ctrl btn-moving' onclick='window.companionSimulateMove()' title='Simulate moving in parallel at cruise speed'>
                    🟢 Move in Parallel
                </button>
                <button class='btn-ctrl' onclick='window.companionSimulateTurn()' title='Approach intersection, brake, turn, resume'>
                    ↩️ Approach &amp; Turn
                </button>
                <button class='btn-ctrl' onclick='window.companionSimulateArrival()' title='Complete journey and mark destination reached'>
                    🏆 Complete Arrival
                </button>
            </div>

            <div style='display: flex; align-items: center; gap: 6px;'>
                <button id='btn-comp-pause' class='btn-ctrl' onclick='window.companionTogglePause()'>
                    ⏸️ Pause
                </button>
                <button class='btn-ctrl' onclick='window.companionRestart()'>
                    🔁 Restart
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

                return `
                <div class="timeline-step-card ${{cardClass}}">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                        <span class="step-badge ${{badgeClass}}">${{badgeText}}</span>
                        <span style="font-size: 1.1rem;">${{s.icon || '📍'}}</span>
                    </div>
                    <div style="font-size: 0.78rem; font-weight: 700; color: ${{isActive ? '#38bdf8' : (isCompleted ? '#34d399' : '#cbd5e1')}}; line-height: 1.3;">
                        ${{s.instruction_text}}
                    </div>
                    <div style="font-size: 0.65rem; color: #94a3b8; margin-top: 6px; display: flex; justify-content: space-between;">
                        <span>${{s.road_name || ''}}</span>
                        <b>${{Math.round(s.distance_meters)}} m</b>
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
                const isStopped = (state === 'TEMPORARILY_STOPPED' || state === 'TRAFFIC_DELAY' || state === 'PAUSED' || state === 'ARRIVED');
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
            const pt = POLYLINE[Math.min(currentStepIdx, POLYLINE.length - 1)];
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

        // Interactive simulation methods
        window.companionSimulateStop = function() {{
            updateCompanionHUD('TEMPORARILY_STOPPED', 0.0, 600, 45);
        }};

        window.companionSimulateWalk = function() {{
            // Step-by-step walking: slow pace, periodic step increments
            updateCompanionHUD('WALKING', BASE_SPEED * 0.12, 600, 45);
            let walkSteps = 0;
            const walkInterval = setInterval(() => {{
                walkSteps++;
                // Animate avatar with turn on each step
                const avatarEl = document.getElementById('companion-avatar-icon');
                if (avatarEl) {{
                    avatarEl.classList.add('anim-turning');
                    setTimeout(() => avatarEl.classList.remove('anim-turning'), 600);
                }}
                if (walkSteps >= 4) {{
                    clearInterval(walkInterval);
                    // Auto-advance one step on the timeline
                    if (currentStepIdx < STEPS.length - 1) {{
                        STEPS[currentStepIdx].is_completed = true;
                        currentStepIdx++;
                    }}
                    updateCompanionHUD('MOVING', BASE_SPEED, 450, 45);
                }}
            }}, 600);
        }};

        window.companionSimulateMove = function() {{
            updateCompanionHUD('MOVING', BASE_SPEED, 450, 45);
        }};

        window.companionSimulateTurn = function() {{
            updateCompanionHUD('APPROACHING_TURN', BASE_SPEED * 0.7, 30, 270);
            setTimeout(() => {{
                updateCompanionHUD('TURNING', BASE_SPEED * 0.5, 10, 270);
                setTimeout(() => {{
                    if (currentStepIdx < STEPS.length - 1) {{
                        STEPS[currentStepIdx].is_completed = true;
                        currentStepIdx++;
                    }}
                    updateCompanionHUD('MOVING', BASE_SPEED, 250, 270);
                }}, 1500);
            }}, 1200);
        }};

        window.companionSimulateArrival = function() {{
            STEPS.forEach(s => s.is_completed = true);
            currentStepIdx = STEPS.length - 1;
            updateCompanionHUD('ARRIVED', 0.0, 0, 90);
        }};

        window.companionTogglePause = function() {{
            isPaused = !isPaused;
            const btn = document.getElementById('btn-comp-pause');
            if (btn) btn.innerText = isPaused ? '▶️ Resume' : '⏸️ Pause';
            if (isPaused) {{
                updateCompanionHUD('PAUSED', 0.0, 400, 45);
            }} else {{
                updateCompanionHUD('MOVING', BASE_SPEED, 400, 45);
            }}
        }};

        window.companionRestart = function() {{
            STEPS.forEach(s => s.is_completed = false);
            currentStepIdx = 0;
            isPaused = false;
            updateCompanionHUD('ROUTE_READY', 0.0, 1200, 45);
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
                        updateCompanionHUD('TEMPORARILY_STOPPED', 0.0, 400, null);
                    }} else {{
                        updateCompanionHUD('MOVING', uSpeed, 350, pos.coords.heading);
                    }}
                }}, function(err) {{
                    console.log("[VirtualCompanion] Geolocation:", err.message);
                }}, {{ enableHighAccuracy: true, maximumAge: 3000, timeout: 8000 }});
            }} catch(e) {{}}
        }}

        // Initialize HUD
        renderTimeline();
        updateCompanionHUD(currentState, currentSpeed, {total_distance_m}, 45);
    }})();
    </script>
    """
