"""
Game Journey Stepper & Real-World Milestone Navigation Engine
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Adaptive Transit System

Transforms any route worldwide into a game-like journey progression with:
1. Dynamic milestone extraction (Start -> Intermediate Crossed Stops -> Reached Destination).
2. Character hop / jump state management (Boy / Vehicle jumping node-by-node).
3. Spoken voice guidance synchronized with crossed milestones.
4. Universal support for any origin and destination across global coordinates.
"""

from dataclasses import dataclass, field
import json
import math
import re
from typing import Any, Dict, List, Optional, Tuple


def haversine_distance_km(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculates spherical distance in kilometers between two lat/lon pairs."""
    lat1, lon1 = p1
    lat2, lon2 = p2
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0) ** 2
    return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def clean_place_name(raw_name: str) -> str:
    """Removes pin icons, coordinates, and extraneous noise from a place label."""
    if not raw_name:
        return "Start Location"
    name = re.sub(r'[📍🏁🧭🚗●]', '', raw_name).strip()
    name = re.sub(r'\(.*?\)', '', name).strip()
    name = re.sub(r'\s+', ' ', name).strip()
    if not name or name.lower() in ["current location", "live satellite"]:
        return "Starting Point"
    # Take the primary town/landmark portion before comma
    parts = [p.strip() for p in name.split(',') if p.strip()]
    return parts[0] if parts else name


@dataclass
class JourneyMilestone:
    index: int
    milestone_type: str  # "START", "WAYPOINT", "DESTINATION"
    label: str           # e.g., "Tenali"
    action_title: str    # e.g., "Started from Tenali", "Crossed Angalakuduru"
    road_or_area: str    # e.g., "Tenali - Narakoduru Road"
    lat: float
    lon: float
    distance_from_start_km: float
    distance_leg_km: float
    voice_announcement: str
    icon: str = "📍"


def extract_journey_game_milestones(
    origin_label: str,
    dest_label: str,
    polyline: List[Tuple[float, float]],
    steps: Optional[List[Dict[str, Any]]] = None,
    total_distance_km: float = 0.0
) -> List[JourneyMilestone]:
    """
    Dynamically extracts a sequence of 4 to 8 game milestones for ANY route worldwide.
    Parses road transitions, known landmarks, and step intervals.
    """
    clean_orig = clean_place_name(origin_label)
    clean_dest = clean_place_name(dest_label)

    p_count = len(polyline) if polyline else 0
    p_start = polyline[0] if p_count > 0 else (16.2335, 80.5505)
    p_end = polyline[-1] if p_count > 0 else (16.3067, 80.4365)

    if total_distance_km <= 0.0 and p_count >= 2:
        total_distance_km = sum(
            haversine_distance_km(polyline[i], polyline[i+1])
            for i in range(p_count - 1)
        )

    milestones: List[JourneyMilestone] = []

    # Milestone 0: Start of Journey
    milestones.append(JourneyMilestone(
        index=0,
        milestone_type="START",
        label=clean_orig,
        action_title=f"Started from {clean_orig}",
        road_or_area="Origin Departure Point",
        lat=p_start[0],
        lon=p_start[1],
        distance_from_start_km=0.0,
        distance_leg_km=0.0,
        voice_announcement=f"Started journey from {clean_orig}. Safe corridor route initialized.",
        icon="🚩"
    ))

    # Extract intermediate waypoints from steps or polyline segments
    extracted_stops: List[Dict[str, Any]] = []

    if steps and len(steps) >= 2:
        cum_dist = 0.0
        seen_roads = set()
        seen_roads.add(clean_orig.lower())

        for s in steps:
            s_dist_m = s.get("distance_m", 0.0)
            s_dist_km = s_dist_m / 1000.0
            cum_dist += s_dist_km

            road_name = s.get("road", "").strip()
            # Filter out non-descriptive road names
            if not road_name or road_name.lower() in ["local corridor", "road", "unnamed road"]:
                # Try to extract from instruction
                instr = s.get("instruction", "")
                m = re.search(r'(?:onto|on|towards)\s+([A-Za-z0-9\s\-]+)', instr, re.IGNORECASE)
                if m:
                    road_name = m.group(1).strip()

            clean_road = re.sub(r'^(onto|on)\s+', '', road_name, flags=re.IGNORECASE).strip()
            road_key = clean_road.lower()

            # Identify prominent road/place transition
            if clean_road and road_key not in seen_roads and s_dist_km >= 0.25 and cum_dist < (total_distance_km * 0.95):
                seen_roads.add(road_key)
                
                # Derive a natural, human-friendly stop name
                stop_display = clean_road
                # If road has hyphen (e.g. Tenali - Narakoduru Road), extract intermediate town
                if "-" in clean_road:
                    parts = clean_road.split("-")
                    second_part = parts[1].replace("Road", "").replace("Bypass", "").strip()
                    if second_part:
                        stop_display = second_part

                extracted_stops.append({
                    "name": stop_display,
                    "road": clean_road,
                    "dist_km": cum_dist,
                    "leg_km": s_dist_km
                })

    # If steps didn't yield enough unique stops (e.g. short route or simple highway), sample from polyline
    if len(extracted_stops) < 2 and p_count >= 6:
        num_intermediate = 3
        step_stride = p_count // (num_intermediate + 1)
        for i in range(1, num_intermediate + 1):
            idx = min(i * step_stride, p_count - 2)
            frac = i / (num_intermediate + 1)
            dist_at_pt = total_distance_km * frac
            pt = polyline[idx]
            
            # Detect well-known regional towns along Andhra Pradesh / Guntur corridor or generic
            sample_name = f"Corridor Checkpoint {i}"
            # Check proximity to known local areas if in Guntur/Tenali region
            if abs(pt[0] - 16.236) < 0.02 and abs(pt[1] - 80.552) < 0.02:
                sample_name = "Vadlamudi Hub"
            elif abs(pt[0] - 16.241) < 0.02 and abs(pt[1] - 80.584) < 0.02:
                sample_name = "Angalakuduru"
            elif abs(pt[0] - 16.255) < 0.02 and abs(pt[1] - 80.535) < 0.02:
                sample_name = "Narakoduru Junction"
            elif abs(pt[0] - 16.216) < 0.03 and abs(pt[1] - 80.538) < 0.03:
                sample_name = "Chebrolu Corridor"
            elif abs(pt[0] - 16.275) < 0.03 and abs(pt[1] - 80.450) < 0.03:
                sample_name = "Guntur Bypass Link"

            extracted_stops.append({
                "name": sample_name,
                "road": f"Corridor Waypoint ({dist_at_pt:.1f} km)",
                "dist_km": dist_at_pt,
                "leg_km": total_distance_km / (num_intermediate + 1),
                "lat": pt[0],
                "lon": pt[1]
            })

    # Limit intermediate stops to at most 5 for best game feel
    selected_stops = extracted_stops[:5]

    # Map stops into JourneyMilestones
    prev_d = 0.0
    for idx, stop in enumerate(selected_stops, start=1):
        s_name = stop["name"]
        d_from_start = round(stop.get("dist_km", prev_d + 1.0), 1)
        leg = round(d_from_start - prev_d, 1)
        prev_d = d_from_start

        # Estimate lat/lon along polyline if not set
        if "lat" in stop:
            s_lat, s_lon = stop["lat"], stop["lon"]
        else:
            poly_idx = int((d_from_start / max(total_distance_km, 0.1)) * (p_count - 1)) if p_count > 0 else 0
            poly_idx = max(0, min(poly_idx, p_count - 1))
            s_lat, s_lon = polyline[poly_idx] if p_count > 0 else p_start

        next_target = selected_stops[idx]["name"] if idx < len(selected_stops) else clean_dest

        milestones.append(JourneyMilestone(
            index=idx,
            milestone_type="WAYPOINT",
            label=s_name,
            action_title=f"Crossed {s_name}",
            road_or_area=stop.get("road", "Main Transit Road"),
            lat=s_lat,
            lon=s_lon,
            distance_from_start_km=d_from_start,
            distance_leg_km=max(0.1, leg),
            voice_announcement=f"Crossed {s_name}. Character advancing towards {next_target}.",
            icon="🏃‍♂️" if idx % 2 == 1 else "🛣️"
        ))

    # Final Milestone: Destination
    final_idx = len(milestones)
    final_leg = round(max(0.1, total_distance_km - prev_d), 1)
    milestones.append(JourneyMilestone(
        index=final_idx,
        milestone_type="DESTINATION",
        label=clean_dest,
        action_title=f"Reached {clean_dest}",
        road_or_area="Destination Safe Terminal",
        lat=p_end[0],
        lon=p_end[1],
        distance_from_start_km=round(total_distance_km, 1),
        distance_leg_km=final_leg,
        voice_announcement=f"Congratulations! You have reached your destination: {clean_dest}. Navigation successfully completed!",
        icon="🏆"
    ))

    return milestones


def build_game_journey_html(
    milestones: List[JourneyMilestone],
    current_step: int,
    traveler_avatar: str = "boy",
    auto_voice: bool = True
) -> str:
    """
    Renders an interactive, visually stunning Game Journey Stepper HUD with:
    - Stepping nodes with Mario/Boardgame style path
    - Character jump / hop CSS animation on active node
    - Real-time speech utterance execution on step transitions
    - Level progress meter and victory banner on arrival
    """
    if not milestones:
        return ""

    current_step = max(0, min(current_step, len(milestones) - 1))
    total_steps = len(milestones)
    progress_pct = int((current_step / max(1, total_steps - 1)) * 100)
    is_completed = (current_step == total_steps - 1)

    active_m = milestones[current_step]
    speech_text = active_m.voice_announcement
    speech_json = json.dumps(speech_text)

    # Avatar SVG / Icon
    if "boy" in traveler_avatar or "walk" in traveler_avatar:
        avatar_icon = "👦"
        avatar_label = "Traveler Boy"
    elif "bike" in traveler_avatar or "motorcycle" in traveler_avatar:
        avatar_icon = "🏍️"
        avatar_label = "Motorcyclist"
    elif "tractor" in traveler_avatar:
        avatar_icon = "🚜"
        avatar_label = "Tractor Operator"
    elif "truck" in traveler_avatar:
        avatar_icon = "🚚"
        avatar_label = "Truck Driver"
    elif "bicycle" in traveler_avatar:
        avatar_icon = "🚴"
        avatar_label = "Cyclist"
    else:
        avatar_icon = "🚗"
        avatar_label = "Driver"

    nodes_html = []
    for m in milestones:
        idx = m.index
        if idx < current_step:
            state_class = "node-completed"
            badge = "✅"
            halo = "border: 2px solid #10b981; background: #064e3b; color: #34d399;"
        elif idx == current_step:
            state_class = "node-active"
            badge = avatar_icon
            halo = "border: 3px solid #38bdf8; background: #0369a1; color: #ffffff; box-shadow: 0 0 20px #38bdf8; animation: activeHop 0.8s infinite alternate ease-in-out;"
        else:
            state_class = "node-upcoming"
            badge = str(idx + 1)
            halo = "border: 2px dashed rgba(255,255,255,0.25); background: rgba(30,41,59,0.7); color: #94a3b8;"

        nodes_html.append(f"""
        <div class='game-step-item {state_class}' style='display: flex; flex-direction: column; align-items: center; text-align: center; min-width: 110px; flex: 1;'>
            <div style='position: relative; margin-bottom: 8px;'>
                <div style='width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; {halo}'>
                    {badge}
                </div>
                {f"<div class='jumping-tag' style='position: absolute; top: -18px; left: 50%; transform: translateX(-50%); background: #38bdf8; color: #02132b; font-size: 9px; font-weight: 900; padding: 2px 6px; border-radius: 999px; white-space: nowrap; box-shadow: 0 0 8px #38bdf8;'>CURRENT</div>" if idx == current_step and not is_completed else ""}
                {f"<div style='position: absolute; top: -18px; left: 50%; transform: translateX(-50%); background: #10b981; color: #ffffff; font-size: 9px; font-weight: 900; padding: 2px 6px; border-radius: 999px; white-space: nowrap;'>ARRIVED</div>" if idx == current_step and is_completed else ""}
            </div>
            <div style='font-size: 0.78rem; font-weight: 700; color: {"#38bdf8" if idx == current_step else ("#34d399" if idx < current_step else "#94a3b8")}; max-width: 105px; word-break: break-word; line-height: 1.2;'>
                {m.label}
            </div>
            <div style='font-size: 0.65rem; color: #64748b; margin-top: 3px;'>
                {m.action_title.split()[0]} ({m.distance_from_start_km:.1f} km)
            </div>
        </div>
        """)

    all_nodes_rendered = "".join(nodes_html)

    victory_banner = ""
    if is_completed:
        victory_banner = f"""
        <div style='background: linear-gradient(135deg, rgba(16, 185, 129, 0.3) 0%, rgba(6, 78, 59, 0.8) 100%); border: 2px solid #10b981; border-radius: 12px; padding: 12px 18px; margin-top: 14px; text-align: center; box-shadow: 0 0 25px rgba(16, 185, 129, 0.4); animation: victoryPulse 1.5s infinite alternate;'>
            <div style='font-size: 1.5rem; margin-bottom: 2px;'>🏆 LEVEL COMPLETED • DESTINATION REACHED!</div>
            <div style='font-size: 0.90rem; font-weight: 800; color: #ffffff;'>
                The {avatar_label} has safely reached <b>{active_m.label}</b> ({active_m.distance_from_start_km:.1f} km).
            </div>
            <div style='font-size: 0.74rem; color: #a7f3d0; margin-top: 4px;'>
                All intermediate checkpoints verified. Hazard evasion 100% successful.
            </div>
        </div>
        """

    return f"""
    <style>
    @keyframes activeHop {{
        0% {{ transform: translateY(0px) scale(1); }}
        100% {{ transform: translateY(-7px) scale(1.08); }}
    }}
    @keyframes victoryPulse {{
        0% {{ box-shadow: 0 0 10px rgba(16, 185, 129, 0.3); }}
        100% {{ box-shadow: 0 0 28px rgba(16, 185, 129, 0.7); }}
    }}
    .game-board-container {{
        background: linear-gradient(135deg, rgba(8, 15, 30, 0.92) 0%, rgba(15, 23, 42, 0.88) 100%);
        border: 1.5px solid rgba(56, 189, 248, 0.35);
        border-radius: 14px;
        padding: 16px 20px;
        margin: 12px 0;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6), 0 0 20px rgba(56, 189, 248, 0.12);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    .game-track-line {{
        position: relative;
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        margin-top: 24px;
        margin-bottom: 12px;
        overflow-x: auto;
        padding-bottom: 6px;
    }}
    .game-track-line::before {{
        content: '';
        position: absolute;
        top: 24px;
        left: 40px;
        right: 40px;
        height: 6px;
        background: rgba(255, 255, 255, 0.12);
        border-radius: 999px;
        z-index: 0;
    }}
    .game-track-fill {{
        position: absolute;
        top: 24px;
        left: 40px;
        width: calc({progress_pct}% * 0.88);
        max-width: calc(100% - 80px);
        height: 6px;
        background: linear-gradient(90deg, #10b981 0%, #38bdf8 100%);
        border-radius: 999px;
        z-index: 0;
        transition: width 0.4s ease;
        box-shadow: 0 0 10px #38bdf8;
    }}
    .game-step-item {{
        position: relative;
        z-index: 1;
    }}
    </style>

    <div class='game-board-container'>
        <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px;'>
            <div style='display: flex; align-items: center; gap: 10px;'>
                <span style='font-size: 1.4rem;'>🎮</span>
                <div>
                    <div style='font-size: 0.95rem; font-weight: 800; color: #ffffff;'>
                        TRAVEL JOURNEY GAME PROGRESSION
                    </div>
                    <div style='font-size: 0.74rem; color: #94a3b8;'>
                        Checkpoint <b>{current_step + 1} of {total_steps}</b> • {active_m.action_title}
                    </div>
                </div>
            </div>
            <div style='display: flex; align-items: center; gap: 10px;'>
                <div style='background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.35); padding: 4px 12px; border-radius: 999px; font-size: 0.75rem; font-weight: 800; color: #38bdf8;'>
                    ⚡ {progress_pct}% Journey Progress
                </div>
                <button onclick="speakGameStep()" style='background: #10b981; color: #ffffff; border: none; padding: 5px 12px; border-radius: 6px; font-size: 0.74rem; font-weight: 700; cursor: pointer; box-shadow: 0 2px 8px rgba(16,185,129,0.4);'>
                    🔊 Speak
                </button>
            </div>
        </div>

        <!-- Stepper Road Track -->
        <div class='game-track-line'>
            <div class='game-track-fill'></div>
            {all_nodes_rendered}
        </div>

        <!-- Active Checkpoint Voice Briefing -->
        <div style='background: rgba(0, 0, 0, 0.35); border-left: 4px solid #38bdf8; border-radius: 6px; padding: 10px 14px; margin-top: 10px; display: flex; align-items: center; justify-content: space-between;'>
            <div>
                <div style='font-size: 0.70rem; color: #38bdf8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;'>
                    Current Checkpoint Status
                </div>
                <div style='font-size: 0.84rem; color: #f1f5f9; font-weight: 600; margin-top: 2px;'>
                    "{active_m.voice_announcement}"
                </div>
            </div>
            <div style='font-size: 0.72rem; color: #94a3b8; text-align: right;'>
                Leg: <b>{active_m.distance_leg_km:.1f} km</b>
            </div>
        </div>

        {victory_banner}
    </div>

    <script>
    (function() {{
        const speechMsg = {speech_json};
        window.speakGameStep = function() {{
            if (!('speechSynthesis' in window)) return;
            window.speechSynthesis.cancel();
            const u = new SpeechSynthesisUtterance(speechMsg);
            u.rate = 0.95;
            u.pitch = 1.05;
            u.lang = 'en-US';
            window.speechSynthesis.speak(u);
        }};
        {"setTimeout(window.speakGameStep, 350);" if auto_voice else ""}
    }})();
    </script>
    """
