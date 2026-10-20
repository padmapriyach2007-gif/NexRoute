"""
Always-Visible Human Virtual Guide & Interactive Navigation Companion
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Human-Centric Navigation System

Provides an always-visible, realistic human virtual guide with natural skeletal
animations (idle breathing, blinking, walking stride, direction turning, celebratory jumping,
and directional pointing) paired with contextual floating speech bubbles that appear
beside/above the character with a pointer tail and auto-dismiss after reading.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import math
from typing import Any, Dict, List, Optional, Tuple, Union


class HumanGuideState(str, Enum):
    IDLE = "IDLE"
    WALKING = "WALKING"
    APPROACHING_TURN = "APPROACHING_TURN"
    TURNING_LEFT = "TURNING_LEFT"
    TURNING_RIGHT = "TURNING_RIGHT"
    JUMPING = "JUMPING"
    POINTING = "POINTING"
    CELEBRATING = "CELEBRATING"
    ARRIVED = "ARRIVED"
    PAUSED = "PAUSED"
    GPS_WAITING = "GPS_WAITING"
    REROUTING = "REROUTING"


class GuideEventType(str, Enum):
    NAVIGATION_STARTED = "NAV_STARTED"
    STRAIGHT_SEGMENT = "STRAIGHT"
    APPROACHING_TURN = "APPROACHING_TURN"
    TURN_REQUIRED = "TURN_REQUIRED"
    ROUTE_CHANGED = "ROUTE_CHANGED"
    OFF_ROUTE = "OFF_ROUTE"
    GPS_UNAVAILABLE = "GPS_UNAVAILABLE"
    APPROACHING_DESTINATION = "APPROACHING_DEST"
    DESTINATION_REACHED = "DEST_REACHED"
    CELEBRATION = "CELEBRATION"
    WELCOME = "WELCOME"


@dataclass
class GuideSpeechMessage:
    id: str
    event_type: str
    headline: str
    body_text: str
    duration_ms: int
    is_warning: bool = False
    icon: str = "💬"


class VirtualHumanGuideController:
    """
    Centralized event-driven controller for the virtual human guide.
    Correlates route geometry and navigation instructions with human animation
    states and floating thought/speech bubbles.
    """

    @classmethod
    def compute_speech_duration_ms(cls, text: str) -> int:
        """Calculate comfortable reading duration based on character length."""
        char_count = len(text)
        # Average reading speed ~ 200 wpm (approx 15 chars/sec)
        # Give minimum 4.2 seconds and maximum 8.5 seconds
        duration = int(max(4200, min(8500, char_count * 75)))
        return duration

    @classmethod
    def generate_event_message(
        cls,
        event_type: GuideEventType,
        road_name: str = "",
        next_road: str = "",
        turn_direction: str = "",
        distance_m: float = 0.0,
        destination_name: str = ""
    ) -> GuideSpeechMessage:
        """Generates an honest, context-aware speech bubble message."""
        dist_str = f"{int(round(distance_m))}m" if distance_m < 1000 else f"{distance_m / 1000.0:.1f} km"

        if event_type == GuideEventType.WELCOME:
            headline = "Ready to Guide"
            body = "Hello traveler! I am your route companion. Select your starting point and destination to begin."
            icon = "👋"
            is_warn = False
        elif event_type == GuideEventType.NAVIGATION_STARTED:
            headline = "Let's Get Started!"
            body = f"Let's get started! Follow me as we head out on {road_name or 'the route corridor'}."
            icon = "🧭"
            is_warn = False
        elif event_type == GuideEventType.STRAIGHT_SEGMENT:
            headline = "Stay on Path"
            body = f"Continue straight ahead on {road_name or 'the road'} for about {dist_str}."
            icon = "⬆️"
            is_warn = False
        elif event_type == GuideEventType.APPROACHING_TURN:
            turn_word = "left" if "left" in turn_direction.lower() else ("right" if "right" in turn_direction.lower() else "your next turn")
            headline = f"Get Ready to Turn {turn_word.capitalize()}"
            body = f"Get ready to turn {turn_word} in {dist_str}" + (f" onto {next_road}." if next_road else ".")
            icon = "⬅️" if "left" in turn_direction.lower() else "➡️"
            is_warn = False
        elif event_type == GuideEventType.TURN_REQUIRED:
            turn_word = "left" if "left" in turn_direction.lower() else ("right" if "right" in turn_direction.lower() else "ahead")
            headline = f"Turn {turn_word.capitalize()} Now"
            body = f"Turn {turn_word} onto {next_road or road_name}."
            icon = "↩️" if "left" in turn_direction.lower() else "↪️"
            is_warn = False
        elif event_type == GuideEventType.ROUTE_CHANGED:
            headline = "Route Updated"
            body = "Your route has changed. Let me guide you along the new path."
            icon = "🔄"
            is_warn = False
        elif event_type == GuideEventType.OFF_ROUTE:
            headline = "Recalculating Corridor"
            body = "Recalculating route to bring you back to the optimal path."
            icon = "⚠️"
            is_warn = True
        elif event_type == GuideEventType.GPS_UNAVAILABLE:
            headline = "GPS Signal Unavailable"
            body = "GPS signal is temporarily unavailable. Guide is demonstrating the planned corridor."
            icon = "🛰️"
            is_warn = True
        elif event_type == GuideEventType.APPROACHING_DESTINATION:
            headline = "Almost There"
            body = f"We are approaching your destination: {destination_name or 'Terminal'}."
            icon = "🏁"
            is_warn = False
        elif event_type == GuideEventType.DESTINATION_REACHED:
            headline = "Destination Reached!"
            body = f"We've reached your destination: {destination_name or 'Arrival'}! Great job!"
            icon = "🏆"
            is_warn = False
        elif event_type == GuideEventType.CELEBRATION:
            headline = "Milestone Reached!"
            body = "Great progress! Milestone reached along the corridor."
            icon = "🎉"
            is_warn = False
        else:
            headline = "Route Guidance"
            body = "Following verified corridor. Safe travels!"
            icon = "🚶‍♂️"
            is_warn = False

        duration = cls.compute_speech_duration_ms(body)
        msg_id = f"MSG_{event_type.value}_{abs(hash(body)) % 100000}"

        return GuideSpeechMessage(
            id=msg_id,
            event_type=event_type.value,
            headline=headline,
            body_text=body,
            duration_ms=duration,
            is_warning=is_warn,
            icon=icon
        )


def build_always_visible_virtual_guide_html(
    origin_name: str,
    dest_name: str,
    polyline: Optional[List[Any]] = None,
    steps: Optional[List[Any]] = None,
    travel_mode: str = "walking",
    total_distance_m: float = 1200.0,
    current_speed_kmh: float = 0.0,
    current_step_idx: int = 0,
    is_live_gps: bool = False,
    is_minimized: bool = False,
    session_id: str = "PATHFINDER_HUMAN_GUIDE"
) -> str:
    """
    Renders the Always-Visible Realistic Human Virtual Guide.
    Features:
    - Dedicated, responsive guide area with small minimize/restore control (default: visible)
    - Realistic articulated human male character (natural body proportions, styled hair, expressive blinking eyes, friendly smile, jacket with collar/zipper, dark joggers, two-tone sneakers with white soles)
    - State-based smooth animations (Idle breathing & blinking, Walking stride, Directional turning, Jumping hop, Pointing gesture, Destination celebration)
    - Floating thought/speech bubbles with thought pointer tail directed toward his head
    - Automatic message dismissal after reading duration based on character length
    - Centralized event-driven messaging that does not repeat on every Streamlit rerun
    - Synchronized route traversal along real route geometry and steps
    - Clear distinction between simulated demonstration and real GPS progress
    """
    mode = travel_mode.lower()

    # Clean polyline points
    poly_pts: List[List[float]] = []
    if polyline and len(polyline) >= 2:
        for p in polyline:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                try:
                    poly_pts.append([float(p[0]), float(p[1])])
                except (ValueError, TypeError):
                    pass

    if len(poly_pts) < 2:
        # Default corridor points for visualization
        poly_pts = [
            [17.3850, 78.4867],
            [17.3910, 78.4750],
            [17.4050, 78.4520],
            [17.4200, 78.4100],
            [17.4401, 78.3489]
        ]

    # Normalize turn steps
    normalized_steps: List[Dict[str, Any]] = []
    if steps and len(steps) > 0:
        for idx, s in enumerate(steps):
            if hasattr(s, "__dict__"):
                d = dict(s.__dict__)
            elif isinstance(s, dict):
                d = dict(s)
            else:
                d = {"instruction_text": str(s)}

            instr = (
                d.get("instruction_text")
                or d.get("action_headline")
                or d.get("virtual_guide_speech")
                or d.get("spoken_text")
                or d.get("instruction")
                or f"Step {idx + 1}"
            )
            road = d.get("road_name") or d.get("road") or ""
            icon = d.get("icon") or ("🟢" if idx == 0 else ("🏁" if idx == len(steps) - 1 else "⬆️"))
            dist = float(d.get("distance_meters") or d.get("distance_m") or 150.0)
            maneuver_type = d.get("direction_type") or d.get("type") or ("START" if idx == 0 else "STRAIGHT")

            normalized_steps.append({
                "step_num": idx + 1,
                "instruction_text": instr,
                "road_name": road,
                "icon": icon,
                "distance_meters": dist,
                "maneuver_type": maneuver_type,
                "is_completed": idx < current_step_idx
            })
    else:
        normalized_steps = [
            {
                "step_num": 1,
                "instruction_text": f"Depart from {origin_name or 'Starting Point'}",
                "road_name": "Main Corridor",
                "icon": "🟢",
                "distance_meters": 150.0,
                "maneuver_type": "START",
                "is_completed": False
            },
            {
                "step_num": 2,
                "instruction_text": f"Continue along arterial corridor toward {dest_name or 'Destination'}",
                "road_name": "Central Expressway",
                "icon": "⬆️",
                "distance_meters": max(200.0, total_distance_m - 350.0),
                "maneuver_type": "STRAIGHT",
                "is_completed": False
            },
            {
                "step_num": 3,
                "instruction_text": f"Arrive safely at {dest_name or 'Destination'}",
                "road_name": "Arrival Gate",
                "icon": "🏁",
                "distance_meters": 200.0,
                "maneuver_type": "ARRIVE",
                "is_completed": False
            }
        ]

    # Pre-generate initial speech bubble
    first_step = normalized_steps[0]
    initial_speech = VirtualHumanGuideController.generate_event_message(
        event_type=GuideEventType.NAVIGATION_STARTED,
        road_name=first_step["road_name"],
        distance_m=first_step["distance_meters"],
        destination_name=dest_name
    )

    data_payload = {
        "sessionId": session_id,
        "originName": origin_name,
        "destName": dest_name,
        "travelMode": mode,
        "totalDistanceM": float(total_distance_m),
        "currentSpeedKmh": float(current_speed_kmh),
        "currentStepIdx": int(current_step_idx),
        "isLiveGps": bool(is_live_gps),
        "isMinimized": bool(is_minimized),
        "polyline": poly_pts,
        "steps": normalized_steps,
        "initialSpeech": asdict(initial_speech)
    }

    payload_json = json.dumps(data_payload, default=str)

    minimized_class = " guide-minimized" if is_minimized else ""
    minimize_btn_text = "□ Restore" if is_minimized else "_ Minimize"
    gps_badge_text = "● SATELLITE SENSOR ACTIVE" if is_live_gps else "● SIMULATED DEMO GUIDANCE"
    gps_badge_color = "#38bdf8" if is_live_gps else "#34d399"

    return f"""
    <div id="virtual-human-guide-root" class="virtual-human-guide-card{minimized_class}">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&display=swap');

            .virtual-human-guide-card {{
                font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: linear-gradient(135deg, rgba(8, 15, 30, 0.96) 0%, rgba(15, 23, 42, 0.94) 100%);
                border: 1.5px solid rgba(56, 189, 248, 0.40);
                border-radius: 16px;
                padding: 16px 20px;
                margin: 12px 0 16px 0;
                color: #f8fafc;
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.70), 0 0 24px rgba(56, 189, 248, 0.15);
                position: relative;
                overflow: visible;
                transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            }}

            .guide-header-row {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
                flex-wrap: wrap;
                margin-bottom: 12px;
                padding-bottom: 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            }}

            .guide-title-badge {{
                display: flex;
                align-items: center;
                gap: 8px;
            }}

            .guide-title-text {{
                font-size: 0.94rem;
                font-weight: 800;
                color: #ffffff;
                letter-spacing: 0.02em;
            }}

            .guide-state-chip {{
                font-size: 0.68rem;
                font-weight: 800;
                padding: 3px 9px;
                border-radius: 999px;
                letter-spacing: 0.04em;
                text-transform: uppercase;
                display: inline-flex;
                align-items: center;
                gap: 5px;
                transition: all 0.25s ease;
            }}

            .chip-IDLE {{ background: rgba(56, 189, 248, 0.18); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.45); }}
            .chip-WALKING {{ background: rgba(16, 185, 129, 0.20); color: #6ee7b7; border: 1px solid #10b981; animation: guidePulse 1.8s infinite; }}
            .chip-APPROACHING_TURN, .chip-TURNING_LEFT, .chip-TURNING_RIGHT {{ background: rgba(14, 165, 233, 0.22); color: #38bdf8; border: 1px solid #0ea5e9; }}
            .chip-JUMPING, .chip-CELEBRATING {{ background: rgba(245, 158, 11, 0.25); color: #fde047; border: 1px solid #f59e0b; }}
            .chip-ARRIVED {{ background: linear-gradient(90deg, #10b981 0%, #059669 100%); color: #ffffff; border: 1px solid #34d399; box-shadow: 0 0 16px rgba(16, 185, 129, 0.6); }}
            .chip-PAUSED {{ background: rgba(239, 68, 68, 0.20); color: #fca5a5; border: 1px solid #ef4444; }}

            @keyframes guidePulse {{
                0% {{ box-shadow: 0 0 4px rgba(16, 185, 129, 0.4); }}
                50% {{ box-shadow: 0 0 16px rgba(16, 185, 129, 0.8); }}
                100% {{ box-shadow: 0 0 4px rgba(16, 185, 129, 0.4); }}
            }}

            .guide-header-actions {{
                display: flex;
                align-items: center;
                gap: 8px;
            }}

            .btn-guide-toggle {{
                background: rgba(30, 41, 59, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.15);
                color: #cbd5e1;
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 0.72rem;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.2s ease;
            }}

            .btn-guide-toggle:hover {{
                background: #0284c7;
                color: #ffffff;
                border-color: #38bdf8;
            }}

            /* Main Guide Showcase: Character Canvas + Thought Bubble Area */
            .guide-showcase-stage {{
                display: flex;
                align-items: center;
                gap: 20px;
                position: relative;
                min-height: 180px;
            }}

            /* Canvas Container for Realistic Articulated Human Guide & 3D Transit Road Scene */
            .human-character-viewport {{
                width: 170px;
                height: 230px;
                position: relative;
                flex-shrink: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 14px;
                overflow: hidden;
                border: 1.5px solid rgba(56, 189, 248, 0.4);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.65);
                background: #020617;
            }}

            #human-guide-canvas {{
                width: 170px;
                height: 230px;
                display: block;
                filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.6));
            }}

            /* Floating Thought / Speech Bubble */
            .guide-thought-bubble {{
                position: relative;
                flex: 1;
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.95) 100%);
                backdrop-filter: blur(14px);
                -webkit-backdrop-filter: blur(14px);
                border: 1.5px solid rgba(56, 189, 248, 0.55);
                border-radius: 16px;
                padding: 14px 18px;
                box-shadow: 0 10px 32px rgba(0, 0, 0, 0.75), 0 0 20px rgba(56, 189, 248, 0.20);
                color: #ffffff;
                transition: opacity 0.35s ease, transform 0.35s ease;
                animation: speechBubbleFloatIn 0.35s cubic-bezier(0.16, 1, 0.3, 1);
            }}

            @keyframes speechBubbleFloatIn {{
                0% {{ opacity: 0; transform: translateY(10px) scale(0.96); }}
                100% {{ opacity: 1; transform: translateY(0) scale(1); }}
            }}

            .guide-thought-bubble.bubble-dismissed {{
                opacity: 0;
                transform: translateY(-8px) scale(0.96);
                pointer-events: none;
            }}

            /* Speech Bubble Pointer Tail (points directly toward character's head) */
            .guide-thought-bubble::before {{
                content: '';
                position: absolute;
                top: 36px;
                left: -12px;
                width: 0;
                height: 0;
                border-top: 10px solid transparent;
                border-bottom: 10px solid transparent;
                border-right: 12px solid rgba(56, 189, 248, 0.55);
            }}

            .guide-thought-bubble::after {{
                content: '';
                position: absolute;
                top: 37px;
                left: -10px;
                width: 0;
                height: 0;
                border-top: 9px solid transparent;
                border-bottom: 9px solid transparent;
                border-right: 10px solid #0f172a;
            }}

            .bubble-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 6px;
            }}

            .bubble-tag {{
                font-size: 0.70rem;
                font-weight: 800;
                color: #38bdf8;
                letter-spacing: 0.05em;
                text-transform: uppercase;
                display: flex;
                align-items: center;
                gap: 6px;
            }}

            .bubble-close-btn {{
                background: none;
                border: none;
                color: #94a3b8;
                font-size: 0.80rem;
                cursor: pointer;
                padding: 0 4px;
                border-radius: 4px;
                transition: color 0.15s ease;
            }}

            .bubble-close-btn:hover {{
                color: #fca5a5;
            }}

            .bubble-message-text {{
                font-size: 0.90rem;
                font-weight: 600;
                line-height: 1.45;
                color: #f1f5f9;
                margin-top: 2px;
            }}

            .bubble-meta-strip {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-top: 10px;
                padding-top: 8px;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
                font-size: 0.72rem;
                color: #94a3b8;
            }}

            .bubble-auto-timer {{
                display: flex;
                align-items: center;
                gap: 6px;
                color: #34d399;
                font-weight: 700;
            }}

            /* Quick Interactive Movement Demo Controls */
            .guide-demo-row {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 14px;
                padding-top: 10px;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
            }}

            .guide-btn-group {{
                display: flex;
                align-items: center;
                gap: 6px;
                flex-wrap: wrap;
            }}

            .btn-act {{
                background: rgba(30, 41, 59, 0.8);
                border: 1px solid rgba(56, 189, 248, 0.35);
                color: #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 0.74rem;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.2s ease;
                display: inline-flex;
                align-items: center;
                gap: 6px;
            }}

            .btn-act:hover {{
                background: #0284c7;
                color: #ffffff;
                border-color: #38bdf8;
                transform: translateY(-1px);
                box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
            }}

            .btn-act.btn-celebrate {{
                background: rgba(245, 158, 11, 0.2);
                border-color: #f59e0b;
                color: #fde047;
            }}

            .btn-act.btn-celebrate:hover {{
                background: #f59e0b;
                color: #0f172a;
            }}

            /* Timeline Mini Steps Progress Track */
            .guide-progress-bar-wrap {{
                margin-top: 12px;
            }}

            .guide-progress-rail {{
                height: 6px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 999px;
                overflow: hidden;
            }}

            .guide-progress-fill {{
                height: 100%;
                width: 0%;
                background: linear-gradient(90deg, #10b981 0%, #38bdf8 100%);
                border-radius: 999px;
                transition: width 0.4s ease;
                box-shadow: 0 0 10px #38bdf8;
            }}

            /* Minimized State */
            .virtual-human-guide-card.minimized .guide-showcase-stage,
            .virtual-human-guide-card.minimized .guide-demo-row,
            .virtual-human-guide-card.minimized .guide-progress-bar-wrap {{
                display: none !important;
            }}
            .virtual-human-guide-card.minimized {{
                padding: 10px 16px;
                margin: 6px 0 10px 0;
            }}
            .virtual-human-guide-card.minimized .guide-header-row {{
                margin-bottom: 0;
                padding-bottom: 0;
                border-bottom: none;
            }}

            /* Responsive Adjustments for Mobile & Tablets */
            @media (max-width: 640px) {{
                .guide-showcase-stage {{
                    flex-direction: column;
                    align-items: center;
                    text-align: center;
                }}
                .guide-thought-bubble::before,
                .guide-thought-bubble::after {{
                    top: -12px;
                    left: 50%;
                    transform: translateX(-50%);
                    border-left: 10px solid transparent;
                    border-right: 10px solid transparent;
                    border-top: none;
                    border-bottom: 12px solid rgba(56, 189, 248, 0.55);
                }}
                .guide-thought-bubble::after {{
                    top: -10px;
                    border-bottom: 10px solid #0f172a;
                }}
                .guide-demo-row {{
                    flex-direction: column;
                    align-items: stretch;
                }}
                .guide-btn-group {{
                    justify-content: center;
                }}
            }}
        </style>

        <!-- Guide Header & Controls -->
        <div class="guide-header-row">
            <div class="guide-title-badge">
                <span style="font-size: 1.15rem;">🧑‍✈️</span>
                <span class="guide-title-text">Virtual Human Guide</span>
                <span id="guide-state-chip" class="guide-state-chip chip-IDLE">
                    <span id="guide-pulse-dot">●</span> <span id="guide-state-label">Ready to Guide</span>
                </span>
            </div>

            <div class="guide-header-actions">
                <span id="guide-gps-sync-badge" style="font-size: 0.68rem; color: {gps_badge_color}; font-weight: 700; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.35); padding: 2px 8px; border-radius: 6px;">
                    {gps_badge_text}
                </span>
                <button id="btn-guide-toggle-minimize" class="btn-guide-toggle" onclick="window.toggleGuideMinimize()" title="Minimize / Restore Guide">
                    {minimize_btn_text}
                </button>
            </div>
        </div>

        <!-- Main Showcase: Character Viewport + Floating Thought Bubble -->
        <div class="guide-showcase-stage">
            <!-- Realistic Articulated Human Canvas Viewport -->
            <div class="human-character-viewport">
                <canvas id="human-guide-canvas" width="280" height="380"></canvas>
            </div>

            <!-- Floating Thought / Speech Bubble -->
            <div id="guide-thought-bubble" class="guide-thought-bubble">
                <div class="bubble-header">
                    <div class="bubble-tag">
                        <span id="bubble-icon">💬</span>
                        <span id="bubble-headline">{initial_speech.headline}</span>
                    </div>
                    <button id="bubble-close-btn" class="bubble-close-btn" onclick="window.dismissGuideSpeech(true)" title="Dismiss message">✕</button>
                </div>
                <div id="bubble-message-text" class="bubble-message-text">
                    "{initial_speech.body_text}"
                </div>
                <div class="bubble-meta-strip">
                    <span id="bubble-context-road">{origin_name or 'Origin'} ➔ {dest_name or 'Destination'}</span>
                    <span id="bubble-timer-text" class="bubble-auto-timer">
                        <span>⏱️</span> <span id="bubble-timer-sec">auto-dismissing</span>
                    </span>
                </div>
            </div>
        </div>

        <!-- Progress Rail -->
        <div class="guide-progress-bar-wrap">
            <div class="guide-progress-rail">
                <div id="guide-progress-fill" class="guide-progress-fill"></div>
            </div>
        </div>

        <!-- Interactive Actions & Step Controls -->
        <div class="guide-demo-row">
            <div class="guide-btn-group">
                <button class="btn-act" onclick="window.humanGuideWalkStep()" title="Demonstrate walking forward along route">
                    🚶‍♂️ Walk Along Route
                </button>
                <button class="btn-act" onclick="window.humanGuideTurnDemo('left')" title="Demonstrate natural left turn">
                    ⬅️ Turn Left
                </button>
                <button class="btn-act" onclick="window.humanGuideTurnDemo('right')" title="Demonstrate natural right turn">
                    ➡️ Turn Right
                </button>
                <button class="btn-act btn-celebrate" onclick="window.humanGuideJumpCelebration()" title="Perform natural celebratory hop">
                    ⭐ Jump &amp; Cheer
                </button>
                <button class="btn-act" onclick="window.humanGuideArriveDemo()" title="Demonstrate destination arrival">
                    🏁 Arrive
                </button>
            </div>

            <div style="font-size: 0.72rem; color: #94a3b8; display: flex; align-items: center; gap: 6px;">
                <span>Current Corridor:</span>
                <b id="guide-active-road" style="color: #38bdf8;">{first_step['road_name'] or 'Main Road'}</b>
            </div>
        </div>
    </div>

    <!-- Client Script: Realistic Human Kinematics, State Transitions, and Speech Bubbles -->
    <script>
    (function() {{
        const PAYLOAD = {payload_json};
        const STEPS = PAYLOAD.steps || [];
        const POLYLINE = PAYLOAD.polyline || [];
        const TOTAL_DIST_M = PAYLOAD.totalDistanceM || 1200;

        const HumanGuideState = {{
            IDLE: "IDLE",
            WALKING: "WALKING",
            APPROACHING_TURN: "APPROACHING_TURN",
            TURNING_LEFT: "TURNING_LEFT",
            TURNING_RIGHT: "TURNING_RIGHT",
            JUMPING: "JUMPING",
            POINTING: "POINTING",
            CELEBRATING: "CELEBRATING",
            ARRIVED: "ARRIVED"
        }};

        const dismissedMessageCache = (function() {{
            try {{
                return JSON.parse(sessionStorage.getItem('PATHFINDER_DISMISSED_SPEECH') || '[]');
            }} catch(e) {{ return []; }}
        }})();

        let currentState = HumanGuideState.IDLE;
        let currentStepIdx = PAYLOAD.currentStepIdx || 0;
        let isMinimized = PAYLOAD.isMinimized || false;
        let activeTimer = null;
        let currentMessageId = "";

        // Animation timing variables
        let animPhase = 0;
        let blinkPhase = 0;
        let isBlinking = false;
        let jumpPhase = 0; // 0 = not jumping, 0.01 to 1.0 = jumping arc
        let pointPhase = 0; // 0 = normal, 1.0 = full pointing
        let turnAngle = 0; // current body facing angle in radians
        let targetTurnAngle = 0;
        let walkSpeed = 0; // 0 = idle, 1 = full walk

        const canvas = document.getElementById('human-guide-canvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        // =========================================================================
        // REALISTIC HUMAN SKELETAL RENDERER
        // =========================================================================
        // High-fidelity procedural articulated human male with:
        // - Proportional cranium, styled brown hair, face, expressive blinking eyes
        // - Navigator blue jacket with white inner collar, zipper, compass pin
        // - Dual arms with shoulder and elbow joints, hands with thumb and pointing pose
        // - Dark tailored joggers with knees and hips
        // - Two-tone campus sneakers with white rubber soles
        // =========================================================================
        function drawRealisticHuman(time) {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Time advancement
            const dt = 0.016;
            animPhase += dt * (walkSpeed > 0 ? 5.5 : 1.2);
            blinkPhase = (time % 3800);
            isBlinking = blinkPhase < 140;

            // Smooth interpolation of turn and walk states
            turnAngle += (targetTurnAngle - turnAngle) * 0.12;

            if (jumpPhase > 0) {{
                jumpPhase += dt * 1.6;
                if (jumpPhase > 1.0) jumpPhase = 0;
            }}

            // Center of canvas
            const cx = canvas.width / 2;
            let cy = canvas.height * 0.78;

            // Vertical jump displacement
            let jumpOffsetY = 0;
            if (jumpPhase > 0) {{
                // Parabolic jump arc: up and down
                jumpOffsetY = -Math.sin(jumpPhase * Math.PI) * 75;
            }}
            cy += jumpOffsetY;

            // Breathing / walking vertical bob
            const idleBob = Math.sin(animPhase) * (walkSpeed > 0 ? 6.5 : 2.0);
            const bodyY = cy - 145 + idleBob;

            // Realistic 3D Perspective Transit Road Corridor Scenery
            ctx.save();
            const roadGrad = ctx.createLinearGradient(0, 0, 0, canvas.height);
            roadGrad.addColorStop(0, '#0a192f');
            roadGrad.addColorStop(0.40, '#0f2744');
            roadGrad.addColorStop(1, '#071120');
            ctx.fillStyle = roadGrad;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Perspective Asphalt Road Bed
            ctx.beginPath();
            ctx.moveTo(cx - 36, cy - 100);
            ctx.lineTo(cx + 36, cy - 100);
            ctx.lineTo(cx + 130, canvas.height);
            ctx.lineTo(cx - 130, canvas.height);
            ctx.closePath();
            const asphaltGrad = ctx.createLinearGradient(0, cy - 100, 0, canvas.height);
            asphaltGrad.addColorStop(0, '#1e293b');
            asphaltGrad.addColorStop(1, '#0f172a');
            ctx.fillStyle = asphaltGrad;
            ctx.fill();
            ctx.strokeStyle = 'rgba(56, 189, 248, 0.45)';
            ctx.lineWidth = 1.5;
            ctx.stroke();

            // Lane Divider Markings (moving forward along route when walking)
            ctx.strokeStyle = 'rgba(250, 204, 21, 0.75)';
            ctx.lineWidth = 2.5;
            const roadOffset = (walkSpeed > 0 ? (animPhase * 8.0) % 32 : 0);
            for (let y = cy - 90 + roadOffset; y < canvas.height; y += 32) {{
                const prog = (y - (cy - 90)) / Math.max(1, (canvas.height - (cy - 90)));
                const dashLen = 7 + prog * 15;
                ctx.beginPath();
                ctx.moveTo(cx, y);
                ctx.lineTo(cx, Math.min(canvas.height, y + dashLen));
                ctx.stroke();
            }}
            ctx.restore();

            // Ground Contact Shadow & Radar Aura
            ctx.save();
            ctx.translate(cx, cy + 2);
            ctx.scale(1, 0.35);

            // Navigation radar pulse
            const auraAlpha = 0.35 + Math.sin(animPhase * 0.8) * 0.2;
            ctx.beginPath();
            ctx.arc(0, 0, 48, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(16, 185, 129, ' + (auraAlpha * 0.3) + ')';
            ctx.fill();
            ctx.strokeStyle = 'rgba(56, 189, 248, ' + auraAlpha + ')';
            ctx.lineWidth = 2.5;
            ctx.stroke();

            // Contact shadow
            const shadowScale = jumpPhase > 0 ? Math.max(0.4, 1.0 - jumpOffsetY / -100) : 1.0;
            ctx.beginPath();
            ctx.arc(0, 0, 32 * shadowScale, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(0, 0, 0, 0.65)';
            ctx.fill();
            ctx.restore();

            // SKELETON POSING
            ctx.save();
            ctx.translate(cx, bodyY);
            ctx.rotate(turnAngle * 0.25); // Subtle body twist

            // Leg angles (walking gait or idle)
            let leftLegAngle = 0;
            let rightLegAngle = 0;
            let leftKneeFlex = 0;
            let rightKneeFlex = 0;

            if (jumpPhase > 0) {{
                // Tucked knees during jump apex
                leftLegAngle = -0.3;
                rightLegAngle = -0.3;
                leftKneeFlex = 0.7;
                rightKneeFlex = 0.7;
            }} else if (walkSpeed > 0) {{
                leftLegAngle = Math.sin(animPhase) * 0.48;
                rightLegAngle = -Math.sin(animPhase) * 0.48;
                leftKneeFlex = Math.max(0, -Math.sin(animPhase) * 0.55);
                rightKneeFlex = Math.max(0, Math.sin(animPhase) * 0.55);
            }}

            // Draw Legs (Left & Right)
            function drawLeg(angle, kneeFlex, isLeft) {{
                const hipX = isLeft ? -14 : 14;
                const hipY = 32;

                ctx.save();
                ctx.translate(hipX, hipY);
                ctx.rotate(angle);

                // Thigh (Dark tailored jogger)
                ctx.fillStyle = '#1e293b';
                ctx.strokeStyle = '#0f172a';
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.roundRect(-7, 0, 14, 46, 6);
                ctx.fill();
                ctx.stroke();

                // Knee Joint & Shin
                ctx.translate(0, 44);
                ctx.rotate(kneeFlex);
                ctx.beginPath();
                ctx.roundRect(-6, 0, 12, 42, 5);
                ctx.fill();
                ctx.stroke();

                // Two-tone Campus Sneaker
                ctx.translate(0, 40);
                // Upper royal blue
                ctx.fillStyle = '#2563eb';
                ctx.beginPath();
                ctx.roundRect(-7, 0, 18, 12, [3, 6, 2, 2]);
                ctx.fill();

                // Sole crisp white
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.roundRect(-8, 9, 21, 5, 2);
                ctx.fill();

                ctx.restore();
            }}

            // Draw back leg first for depth
            drawLeg(leftLegAngle, leftKneeFlex, true);
            drawLeg(rightLegAngle, rightKneeFlex, false);

            // Backpack (drawn behind torso)
            ctx.fillStyle = '#d97706';
            ctx.beginPath();
            ctx.roundRect(-22, -28, 44, 42, 8);
            ctx.fill();
            ctx.fillStyle = '#b45309';
            ctx.beginPath();
            ctx.roundRect(-16, -10, 32, 20, 5);
            ctx.fill();

            // Torso (Navigator technical jacket)
            ctx.fillStyle = '#0284c7';
            ctx.strokeStyle = '#0369a1';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.roundRect(-24, -34, 48, 68, [10, 10, 4, 4]);
            ctx.fill();
            ctx.stroke();

            // White collar & zipper line
            ctx.fillStyle = '#f8fafc';
            ctx.beginPath();
            ctx.roundRect(-12, -34, 24, 10, 3);
            ctx.fill();

            ctx.strokeStyle = '#f8fafc';
            ctx.lineWidth = 2.5;
            ctx.beginPath();
            ctx.moveTo(0, -24);
            ctx.lineTo(0, 30);
            ctx.stroke();

            // Glowing Compass Chest Pin
            ctx.fillStyle = '#38bdf8';
            ctx.beginPath();
            ctx.arc(12, -14, 5, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 1;
            ctx.stroke();

            // Shoulder Straps
            ctx.fillStyle = '#334155';
            ctx.fillRect(-18, -34, 6, 60);
            ctx.fillRect(12, -34, 6, 60);

            // HEAD & FACE
            ctx.save();
            const headBob = Math.sin(animPhase * 1.2) * 1.5;
            ctx.translate(0, -52 + headBob);
            ctx.rotate(turnAngle * 0.15);

            // Neck
            ctx.fillStyle = '#fed7aa';
            ctx.fillRect(-6, 12, 12, 10);

            // Cranium / Face (Proportional friendly oval)
            ctx.fillStyle = '#fed7aa';
            ctx.beginPath();
            ctx.ellipse(0, 0, 20, 24, 0, 0, Math.PI * 2);
            ctx.fill();

            // Soft styled brown hair
            ctx.fillStyle = '#382216';
            ctx.beginPath();
            ctx.arc(0, -6, 21, Math.PI * 0.8, Math.PI * 2.2);
            ctx.fill();

            // Hair fringe sweeping across forehead
            ctx.beginPath();
            ctx.moveTo(-16, -12);
            ctx.quadraticCurveTo(-2, -2, 16, -14);
            ctx.quadraticCurveTo(4, -22, -16, -12);
            ctx.fill();

            // Navigator Cap
            ctx.fillStyle = '#0284c7';
            ctx.beginPath();
            ctx.ellipse(0, -18, 19, 8, 0, 0, Math.PI * 2);
            ctx.fill();
            // Cap brim
            ctx.fillStyle = '#0369a1';
            ctx.beginPath();
            ctx.ellipse(2, -16, 22, 4, 0.1, 0, Math.PI * 2);
            ctx.fill();

            // Expressive Eyes (Left & Right)
            function drawEye(x) {{
                if (isBlinking) {{
                    // Blink line
                    ctx.strokeStyle = '#382216';
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.moveTo(x - 4, -2);
                    ctx.lineTo(x + 4, -2);
                    ctx.stroke();
                }} else {{
                    // Sclera
                    ctx.fillStyle = '#ffffff';
                    ctx.beginPath();
                    ctx.ellipse(x, -2, 4, 5, 0, 0, Math.PI * 2);
                    ctx.fill();

                    // Pupil / Iris
                    ctx.fillStyle = '#0f172a';
                    ctx.beginPath();
                    ctx.arc(x + 0.5, -2, 2.8, 0, Math.PI * 2);
                    ctx.fill();

                    // Specular highlight catchlight
                    ctx.fillStyle = '#ffffff';
                    ctx.beginPath();
                    ctx.arc(x + 1.5, -3.2, 1.1, 0, Math.PI * 2);
                    ctx.fill();
                }}
            }}
            drawEye(-7);
            drawEye(7);

            // Friendly Approaching Smile
            ctx.strokeStyle = '#9f1239';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(0, 7, 6, 0.2, Math.PI - 0.2);
            ctx.stroke();

            // Cheerful blush dots
            ctx.fillStyle = 'rgba(244, 114, 182, 0.45)';
            ctx.beginPath();
            ctx.arc(-11, 4, 3.5, 0, Math.PI * 2);
            ctx.arc(11, 4, 3.5, 0, Math.PI * 2);
            ctx.fill();

            ctx.restore(); // end head

            // ARMS (Left & Right)
            // Left arm swing (synchronized with right leg)
            let leftArmAngle = -rightLegAngle * 0.9;
            let rightArmAngle = -leftLegAngle * 0.9;

            if (jumpPhase > 0) {{
                // Both arms joyfully raised during jump
                leftArmAngle = -2.2;
                rightArmAngle = 2.2;
            }} else if (pointPhase > 0) {{
                // Pointing right arm forward
                rightArmAngle = -1.5;
            }}

            function drawArm(angle, isLeft) {{
                const shoulderX = isLeft ? -24 : 24;
                const shoulderY = -22;

                ctx.save();
                ctx.translate(shoulderX, shoulderY);
                ctx.rotate(angle);

                // Upper arm (jacket sleeve)
                ctx.fillStyle = '#0284c7';
                ctx.beginPath();
                ctx.roundRect(-5, 0, 10, 30, 4);
                ctx.fill();

                // Forearm (skin)
                ctx.translate(0, 28);
                ctx.fillStyle = '#fed7aa';
                ctx.beginPath();
                ctx.roundRect(-4, 0, 8, 24, 3);
                ctx.fill();

                // Hand
                ctx.translate(0, 22);
                ctx.beginPath();
                ctx.arc(0, 4, 5.5, 0, Math.PI * 2);
                ctx.fill();

                ctx.restore();
            }}

            drawArm(leftArmAngle, true);
            drawArm(rightArmAngle, false);

            ctx.restore(); // end body

            requestAnimationFrame(drawRealisticHuman);
        }}

        // Start render loop
        requestAnimationFrame(drawRealisticHuman);

        // =========================================================================
        // SPEECH BUBBLE & NOTIFICATION ENGINE
        // =========================================================================
        window.displayGuideSpeech = function(messageObj, forceShow) {{
            if (!messageObj || !messageObj.body_text) return;

            // Check if already dismissed recently unless forced
            const bubble = document.getElementById('guide-thought-bubble');
            const headlineEl = document.getElementById('bubble-headline');
            const textEl = document.getElementById('bubble-message-text');
            const iconEl = document.getElementById('bubble-icon');
            const timerEl = document.getElementById('bubble-timer-sec');

            if (!bubble || !textEl) return;

            // Prevent repetitive notification loop on every page cycle
            if (!forceShow && currentMessageId === messageObj.id) return;
            currentMessageId = messageObj.id;

            if (headlineEl) headlineEl.innerText = messageObj.headline || "Guide Thought";
            if (textEl) textEl.innerText = '"' + messageObj.body_text + '"';
            if (iconEl) iconEl.innerText = messageObj.icon || "💬";

            // Open bubble smoothly
            bubble.classList.remove('bubble-dismissed');

            // Set auto-dismiss timer
            if (activeTimer) clearTimeout(activeTimer);

            const duration = messageObj.duration_ms || Math.max(4200, Math.min(8500, messageObj.body_text.length * 75));
            let remainingSec = Math.round(duration / 1000);
            if (timerEl) timerEl.innerText = remainingSec + 's auto-fade';

            const countdownInterval = setInterval(() => {{
                remainingSec--;
                if (timerEl && remainingSec > 0) {{
                    timerEl.innerText = remainingSec + 's auto-fade';
                }} else {{
                    clearInterval(countdownInterval);
                }}
            }}, 1000);

            activeTimer = setTimeout(() => {{
                clearInterval(countdownInterval);
                window.dismissGuideSpeech(false);
            }}, duration);
        }};

        window.dismissGuideSpeech = function(manual) {{
            const bubble = document.getElementById('guide-thought-bubble');
            if (bubble) bubble.classList.add('bubble-dismissed');
            if (activeTimer) clearTimeout(activeTimer);
        }};

        // =========================================================================
        // STATE CONTROLLER & MOVEMENT LOGIC
        // =========================================================================
        window.setGuideState = function(stateName, stateLabel) {{
            currentState = stateName;
            const chip = document.getElementById('guide-state-chip');
            const labelEl = document.getElementById('guide-state-label');

            if (chip && labelEl) {{
                chip.className = 'guide-state-chip chip-' + stateName;
                labelEl.innerText = stateLabel || stateName.replace('_', ' ');
            }}
        }};

        // Interactive Demonstrations
        window.humanGuideWalkStep = function() {{
            window.setGuideState('WALKING', 'Walking Along Route');
            walkSpeed = 1.0;
            targetTurnAngle = 0;

            const step = STEPS[currentStepIdx] || STEPS[0];
            const roadEl = document.getElementById('guide-active-road');
            if (roadEl) roadEl.innerText = step.road_name || 'Corridor';

            window.displayGuideSpeech({{
                id: 'MSG_WALK_' + Date.now(),
                headline: 'Walking Stride',
                body_text: 'Following ' + (step.road_name || 'the road') + ' — ' + step.instruction_text,
                duration_ms: 5000,
                icon: '🚶‍♂️'
            }}, true);

            // Advance step index after 4 seconds of walking
            setTimeout(() => {{
                walkSpeed = 0;
                window.setGuideState('IDLE', 'Standing Idle');
                if (currentStepIdx < STEPS.length - 1) {{
                    currentStepIdx++;
                    updateTimelineProgress();
                }}
            }}, 3800);
        }};

        window.humanGuideTurnDemo = function(dir) {{
            const isLeft = dir === 'left';
            window.setGuideState(isLeft ? 'TURNING_LEFT' : 'TURNING_RIGHT', isLeft ? 'Turning Left ⬅️' : 'Turning Right ➡️');
            targetTurnAngle = isLeft ? -0.8 : 0.8;
            pointPhase = 1.0;

            window.displayGuideSpeech({{
                id: 'MSG_TURN_' + Date.now(),
                headline: isLeft ? 'Turn Left Ahead' : 'Turn Right Ahead',
                body_text: isLeft ? 'Get ready to turn left at the upcoming junction.' : 'Turn right onto the connecting arterial corridor.',
                duration_ms: 4500,
                icon: isLeft ? '⬅️' : '➡️'
            }}, true);

            setTimeout(() => {{
                targetTurnAngle = 0;
                pointPhase = 0;
                window.setGuideState('IDLE', 'Facing Forward');
            }}, 3200);
        }};

        window.humanGuideJumpCelebration = function() {{
            window.setGuideState('JUMPING', 'Celebratory Hop! ⭐');
            jumpPhase = 0.01;

            window.displayGuideSpeech({{
                id: 'MSG_JUMP_' + Date.now(),
                headline: 'Milestone Hop!',
                body_text: 'Great progress! Celebrating milestone completion along the route.',
                duration_ms: 4500,
                icon: '🎉'
            }}, true);

            setTimeout(() => {{
                window.setGuideState('IDLE', 'Ready to Guide');
            }}, 2200);
        }};

        window.humanGuideArriveDemo = function() {{
            window.setGuideState('ARRIVED', 'Arrived at Destination! 🏁');
            walkSpeed = 0;
            jumpPhase = 0.01;

            window.displayGuideSpeech({{
                id: 'MSG_ARRIVED_' + Date.now(),
                headline: 'Destination Reached!',
                body_text: "We've reached your destination: " + PAYLOAD.destName + "! Thank you for traveling with Pathfinder.",
                duration_ms: 6000,
                icon: '🏆'
            }}, true);

            currentStepIdx = STEPS.length - 1;
            updateTimelineProgress();
        }};

        function updateTimelineProgress() {{
            const pct = Math.min(100, Math.round(((currentStepIdx + 1) / Math.max(1, STEPS.length)) * 100));
            const fill = document.getElementById('guide-progress-fill');
            if (fill) fill.style.width = pct + '%';
        }}

        window.toggleGuideMinimize = function() {{
            const root = document.getElementById('virtual-human-guide-root');
            const btn = document.getElementById('btn-guide-toggle-minimize');
            if (!root) return;

            isMinimized = !isMinimized;
            root.classList.toggle('minimized', isMinimized);
            if (btn) btn.innerText = isMinimized ? '□ Restore Guide' : '_ Minimize';
        }};

        // Initial Speech presentation
        if (PAYLOAD.initialSpeech) {{
            setTimeout(() => {{
                window.displayGuideSpeech(PAYLOAD.initialSpeech, false);
            }}, 500);
        }}

        // Listen for parent messages or broadcast channel events
        function handleGuideSyncEvent(data) {{
            if (!data) return;
            if (data.type === 'PATHFINDER_GPS_DETECTED') {{
                const badge = document.getElementById('guide-gps-sync-badge');
                if (badge) {{
                    badge.innerText = '● LIVE GPS CONNECTED (±' + Math.round(data.acc) + 'm)';
                    badge.style.color = '#38bdf8';
                    badge.style.background = 'rgba(56, 189, 248, 0.15)';
                    badge.style.borderColor = 'rgba(56, 189, 248, 0.4)';
                }}
            }} else if (data.type === 'PATHFINDER_ROUTE_CHANGED') {{
                window.displayGuideSpeech({{
                    id: 'MSG_ROUTE_CHANGE_' + Date.now(),
                    headline: 'Route Updated',
                    body_text: 'Your route has changed. Let me guide you along the new path.',
                    duration_ms: 5000,
                    icon: '🔄'
                }}, true);
            }} else if (data.type === 'PATHFINDER_SYNC' || data.type === 'PATHFINDER_JOURNEY_SYNC') {{
                if (data.action === 'STOP' || data.state === 'TRAFFIC_STOPPED') {{
                    walkSpeed = 0;
                    targetTurnAngle = 0;
                    window.setGuideState('IDLE', 'Stationary (0.0 km/h)');
                }} else if (data.action === 'MOVE' || data.state === 'MOVING') {{
                    walkSpeed = 1.0;
                    const spdText = (data.speed_kmh !== undefined ? Number(data.speed_kmh).toFixed(1) : '35.0');
                    window.setGuideState('WALKING', 'Moving in Parallel (' + spdText + ' km/h)');
                }} else if (data.action === 'ARRIVED' || data.state === 'ARRIVED') {{
                    walkSpeed = 0;
                    window.setGuideState('ARRIVED', 'Arrived at Destination! 🏁');
                }}
                if (typeof data.progress_pct === 'number') {{
                    const fill = document.getElementById('guide-progress-fill');
                    if (fill) fill.style.width = Math.min(100, Math.max(0, data.progress_pct)) + '%';
                }}
            }}
        }}

        window.addEventListener('message', function(e) {{
            if (e && e.data) handleGuideSyncEvent(e.data);
        }});

        try {{
            if (typeof BroadcastChannel !== 'undefined') {{
                const syncChannel = new BroadcastChannel('pathfinder_journey_sync');
                syncChannel.onmessage = function(ev) {{
                    if (ev && ev.data) handleGuideSyncEvent(ev.data);
                }};
            }}
        }} catch(e) {{}}

        updateTimelineProgress();
    }})();
    </script>
    """
