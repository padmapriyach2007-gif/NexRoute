"""
Google Maps & Swiggy-Style AI Voice Navigation Engine for P.A.T.H.F.I.N.D.E.R.
CampusAegis Real-Time Navigation System

Features:
1. Turn-by-Turn AI Voice Guidance using Browser Web Speech Synthesis API (Google Maps style phrasing).
2. Live Animated Traveling Avatar:
   - "Small Boy Walking": Friendly walking boy with swinging legs/arms, backpack, cap, and Swiggy/Zomato style radar pulse.
   - "Driving Car": Google Maps GPS vehicle with headlight beam and 360 road alignment.
   - "Bike / Scooter", "Tractor", "Truck", "Bicycle": Dedicated transport symbols with road alignment.
3. Real-Time GPS Tracking & Route Snapping:
   - Snaps user GPS (via navigator.geolocation.watchPosition) to the nearest segment on the route polyline.
   - Rotates avatar to road bearing at every bend and turn.
   - Stops the character when the user stops (speed < 0.8 km/h or paused).
   - Off-route detection (>45m deviation) with visual warning and spoken voice prompt.
4. Step-by-Step Maneuver Highlighting:
   - Slices the polyline into individual maneuver legs ("small routes").
   - Highlights the active maneuver segment dynamically.
5. Voice Guidance Synchronization:
   - Speaks turn maneuvers in advance as the traveler approaches each turn.
   - Announces final arrival at destination.
"""

import json
import math
import re
from typing import Dict, Any, List, Optional, Tuple


def haversine_m(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculates great-circle distance in meters between two lat/lon pairs."""
    lat1, lon1 = p1
    lat2, lon2 = p2
    r = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0) ** 2
    return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def slice_polyline_into_small_routes(
    polyline: List[List[float]],
    steps: List[Dict[str, Any]]
) -> List[List[List[float]]]:
    """
    Slices a continuous polyline into individual small-route segments matching each maneuver step.
    Ensures every maneuver has a dedicated, continuous coordinate corridor for high-fidelity visualization.
    """
    if not polyline or len(polyline) < 2:
        return [polyline for _ in steps]
    if not steps:
        return [polyline]

    total_steps = len(steps)
    if total_steps == 1:
        return [polyline]

    # Calculate cumulative distances along polyline
    cum_dists = [0.0]
    for i in range(1, len(polyline)):
        d = haversine_m(tuple(polyline[i - 1]), tuple(polyline[i]))
        cum_dists.append(cum_dists[-1] + d)

    total_poly_dist = cum_dists[-1] if cum_dists[-1] > 0 else 1.0

    # Calculate cumulative distance per step
    step_distances = [float(s.get("distance_m", 0.0)) for s in steps]
    sum_step_dists = sum(step_distances)

    segments = []
    curr_poly_idx = 0

    if sum_step_dists > 0 and len(polyline) > 2:
        # Scale step distances to match polyline total
        ratio = total_poly_dist / sum_step_dists
        cum_target = 0.0

        for s_idx, s in enumerate(steps):
            s_dist = float(s.get("distance_m", 0.0)) * ratio
            target_dist = cum_target + s_dist
            cum_target = target_dist

            # Find polyline index for this boundary
            end_idx = curr_poly_idx
            while end_idx < len(cum_dists) - 1 and cum_dists[end_idx] < target_dist:
                end_idx += 1

            if s_idx == total_steps - 1:
                end_idx = len(polyline) - 1

            # Ensure at least 2 points per segment
            seg = polyline[curr_poly_idx : max(curr_poly_idx + 2, end_idx + 1)]
            segments.append(seg)
            curr_poly_idx = end_idx
    else:
        # Fallback even partitioning
        pts_per_step = max(2, len(polyline) // total_steps)
        for s_idx in range(total_steps):
            start_i = s_idx * pts_per_step
            end_i = (s_idx + 1) * pts_per_step if s_idx < total_steps - 1 else len(polyline)
            seg = polyline[start_i : max(start_i + 2, end_i)]
            segments.append(seg)

    return segments


def build_spoken_instruction(step: Dict[str, Any], next_step: Optional[Dict[str, Any]], is_first: bool = False, is_last: bool = False) -> str:
    """Creates clear, natural Google Maps spoken turn announcements."""
    instr = step.get("instruction", "Proceed on route")
    road = step.get("road", "corridor")
    dist_m = float(step.get("distance_m", 0.0))

    if dist_m >= 1000:
        dist_str = f"{dist_m / 1000.0:.1f} kilometers"
    else:
        dist_str = f"{int(round(dist_m))} meters"

    if is_first:
        spoken = f"{instr}. Then continue for {dist_str}."
    elif is_last:
        spoken = f"In {dist_str}, you will reach your destination: {road}."
    else:
        spoken = f"In {dist_str}, {instr}."
        if next_step:
            next_road = next_step.get("road", "the road")
            spoken += f" Then continue toward {next_road}."

    return spoken


def prepare_google_maps_voice_data(
    active_route_item: Any,
    origin_label: str,
    destination_label: str,
    active_hazards: Optional[List[Any]] = None,
    active_restrictions: Optional[List[Any]] = None,
    unit: str = "km",
    auto_start: bool = True
) -> Dict[str, Any]:
    """Prepares structured, JSON-serializable navigation data for the live simulator."""
    route = getattr(active_route_item, "route", active_route_item)
    polyline = getattr(route, "polyline", [])
    raw_steps = getattr(route, "steps", [])

    clean_origin = origin_label.replace("My Current Location", "your location").replace("📍", "").strip()
    clean_dest = destination_label.replace("Map Pin", "your destination").replace("🏁", "").strip()

    # Determine default avatar and transport mode title based on route mode
    route_mode_str = str(getattr(route, "mode", "DRIVING")).upper()
    if "TRACTOR" in route_mode_str:
        default_avatar = "tractor"
        transport_title = "Tractor"
    elif "MOTORCYCLE" in route_mode_str or "BIKE" in route_mode_str:
        default_avatar = "bike"
        transport_title = "Motorcycle / Bike"
    elif "TRUCK" in route_mode_str:
        default_avatar = "truck"
        transport_title = "Heavy Truck"
    elif "WALK" in route_mode_str or "PEDESTRIAN" in route_mode_str:
        default_avatar = "boy"
        transport_title = "Walking"
    elif "BICYCLE" in route_mode_str:
        default_avatar = "bicycle"
        transport_title = "Bicycle"
    else:
        default_avatar = "car"
        transport_title = "Driving Car"

    # Ensure steps exist
    roads_list = getattr(route, "summary_roads", []) or ["Local Corridor"]
    if not raw_steps:
        raw_steps = [
            {"step_num": 1, "icon": "🟢", "instruction": f"Head out on {roads_list[0]}", "road": roads_list[0], "distance_m": getattr(route, "distance_meters", 1000.0) / max(len(roads_list), 1)},
            {"step_num": 2, "icon": "🏁", "instruction": f"Arrive at destination: {clean_dest}", "road": roads_list[-1], "distance_m": 0.0}
        ]

    # Slice polyline into small route segments
    segments = slice_polyline_into_small_routes(polyline, raw_steps)

    parsed_steps = []
    cum_m = 0.0
    for idx, s in enumerate(raw_steps):
        next_s = raw_steps[idx + 1] if idx + 1 < len(raw_steps) else None
        is_first = (idx == 0)
        is_last = (idx == len(raw_steps) - 1)

        spoken_text = build_spoken_instruction(s, next_s, is_first=is_first, is_last=is_last)
        s_dist_m = float(s.get("distance_m", 0.0))
        cum_m += s_dist_m
        s_dist_km = s_dist_m / 1000.0

        if unit == "miles":
            dist_display = f"{s_dist_km * 0.621371:.2f} mi" if s_dist_km >= 0.1 else f"{int(s_dist_m * 3.28084)} ft"
        else:
            dist_display = f"{s_dist_km:.2f} km" if s_dist_km >= 0.1 else f"{int(s_dist_m)} m"

        parsed_steps.append({
            "step_num": idx + 1,
            "icon": s.get("icon", "⬆️"),
            "instruction": s.get("instruction", "Proceed"),
            "road": s.get("road", "Main Corridor"),
            "distance_m": s_dist_m,
            "cumulative_distance_m": cum_m,
            "distance_display": dist_display,
            "spoken": spoken_text,
            "segment_coordinates": segments[idx] if idx < len(segments) else []
        })

    # Prepare spoken welcome announcement
    eff_dist_km = getattr(active_route_item, "effective_distance_km", getattr(route, "distance_km", 1.0))
    eff_dur_min = getattr(active_route_item, "effective_duration_minutes", getattr(route, "duration_minutes", 1.0))
    route_name = getattr(route, "name", "Safe Corridor")

    dur_round = max(1, round(eff_dur_min))
    time_phrase = f"{dur_round} minutes" if dur_round < 60 else f"{dur_round // 60} hours and {dur_round % 60} minutes"
    dist_phrase = f"{eff_dist_km:.1f} kilometers" if unit == "km" else f"{eff_dist_km * 0.621371:.1f} miles"

    initial_spoken_briefing = (
        f"Starting navigation in {transport_title} mode to {clean_dest} via {route_name.split('(')[0].strip()}. "
        f"The route is {dist_phrase}, estimated at {time_phrase}. "
        f"{parsed_steps[0]['spoken']}"
    )

    return {
        "route_id": getattr(route, "route_id", "route_1"),
        "route_name": route_name,
        "origin_label": clean_origin,
        "destination_label": clean_dest,
        "polyline": polyline,
        "steps": parsed_steps,
        "total_distance_km": eff_dist_km,
        "total_duration_minutes": eff_dur_min,
        "initial_spoken": initial_spoken_briefing,
        "default_avatar": default_avatar,
        "auto_start": auto_start,
        "unit": unit
    }


def render_google_maps_voice_navigator_html(nav_data: Dict[str, Any], height: int = 680) -> str:
    """
    Renders an ultra-rich Google Maps & Swiggy/Zomato style Live AI Voice Navigation Component.
    Runs smoothly inside Streamlit components.html.
    """
    json_data = json.dumps(nav_data)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    user-select: none;
  }}
  body {{
    background: #090d16;
    color: #f8fafc;
    overflow: hidden;
    padding: 6px;
  }}

  /* Main Wrapper */
  .gmaps-nav-container {{
    display: flex;
    flex-direction: column;
    height: {height - 12}px;
    background: linear-gradient(180deg, #0f172a 0%, #0a0e1a 100%);
    border: 1.5px solid rgba(56, 189, 248, 0.4);
    border-radius: 14px;
    overflow: hidden;
    position: relative;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7), 0 0 25px rgba(56, 189, 248, 0.15);
  }}

  /* Google Maps Live Turn Banner (Top HUD) */
  .gmaps-turn-banner {{
    background: linear-gradient(135deg, #065f46 0%, #047857 60%, #0f766e 100%);
    border-bottom: 2px solid #10b981;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    z-index: 1000;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
    transition: background 0.3s ease;
  }}
  .turn-left {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .turn-icon-box {{
    width: 46px;
    height: 46px;
    background: rgba(255, 255, 255, 0.2);
    border: 2px solid #ffffff;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    box-shadow: 0 0 12px rgba(255, 255, 255, 0.3);
  }}
  .turn-info {{
    display: flex;
    flex-direction: column;
  }}
  .turn-distance {{
    font-size: 1.35rem;
    font-weight: 900;
    color: #ffffff;
    line-height: 1.1;
    letter-spacing: -0.02em;
  }}
  .turn-instruction {{
    font-size: 0.90rem;
    font-weight: 700;
    color: #d1fae5;
    margin-top: 2px;
  }}
  .turn-road {{
    font-size: 0.74rem;
    color: #a7f3d0;
    opacity: 0.9;
  }}

  .turn-right-hud {{
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
  }}
  .next-preview {{
    font-size: 0.72rem;
    background: rgba(0, 0, 0, 0.35);
    padding: 3px 8px;
    border-radius: 6px;
    color: #cbd5e1;
    border: 1px solid rgba(255, 255, 255, 0.15);
  }}

  /* Swiggy/Zomato Live Tracking Sub-Bar */
  .swiggy-tracking-bar {{
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding: 6px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.76rem;
    z-index: 999;
  }}
  .swiggy-status {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .status-pulse-dot {{
    width: 9px;
    height: 9px;
    background: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 8px #10b981;
    animation: pulseDot 1.5s infinite;
  }}
  @keyframes pulseDot {{
    0% {{ transform: scale(0.9); opacity: 0.8; }}
    50% {{ transform: scale(1.3); opacity: 1; }}
    100% {{ transform: scale(0.9); opacity: 0.8; }}
  }}

  /* Voice Status & EQ Visualizer */
  .voice-eq-wrap {{
    display: inline-flex;
    align-items: flex-end;
    gap: 2.5px;
    height: 14px;
    margin-left: 6px;
  }}
  .voice-bar {{
    width: 3px;
    height: 4px;
    background: #38bdf8;
    border-radius: 1px;
    transition: height 0.1s ease;
  }}
  .voice-eq-wrap.speaking .voice-bar:nth-child(1) {{ animation: eqBar 0.5s infinite alternate; }}
  .voice-eq-wrap.speaking .voice-bar:nth-child(2) {{ animation: eqBar 0.7s infinite alternate 0.1s; }}
  .voice-eq-wrap.speaking .voice-bar:nth-child(3) {{ animation: eqBar 0.4s infinite alternate 0.2s; }}
  @keyframes eqBar {{
    0% {{ height: 3px; background: #38bdf8; }}
    100% {{ height: 14px; background: #10b981; }}
  }}

  /* Speedometer and Off-route Badge */
  .telemetry-badges {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .speed-pill {{
    background: rgba(56, 189, 248, 0.15);
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.35);
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 800;
    font-size: 0.72rem;
  }}
  .off-route-badge {{
    display: none;
    background: rgba(239, 68, 68, 0.25);
    border: 1.5px solid #ef4444;
    color: #fca5a5;
    font-size: 0.72rem;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 4px;
    animation: flashAlert 1s infinite alternate;
  }}
  @keyframes flashAlert {{
    0% {{ opacity: 0.7; }}
    100% {{ opacity: 1; }}
  }}

  /* Map Container */
  #gmaps-map {{
    flex: 1;
    width: 100%;
    min-height: 250px;
    background: #0b1120;
    position: relative;
    z-index: 10;
  }}

  /* Floating Controls Overlay (Google Maps Style) */
  .map-overlay-controls {{
    position: absolute;
    bottom: 95px;
    left: 12px;
    right: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 900;
    pointer-events: none;
  }}
  .avatar-switcher-group, .speed-switcher-group {{
    pointer-events: auto;
    background: rgba(15, 23, 42, 0.88);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 8px;
    padding: 3px;
    display: flex;
    gap: 3px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.5);
  }}
  .hud-btn {{
    background: transparent;
    border: none;
    color: #94a3b8;
    padding: 5px 9px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 4px;
  }}
  .hud-btn:hover {{
    color: #ffffff;
    background: rgba(255, 255, 255, 0.1);
  }}
  .hud-btn.active {{
    background: #0284c7;
    color: #ffffff;
    box-shadow: 0 0 8px rgba(2, 132, 199, 0.6);
  }}

  /* Bottom Console: Actions & Progress */
  .gmaps-bottom-console {{
    background: #090e1a;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding: 8px 12px;
    z-index: 1000;
  }}
  .progress-bar-wrap {{
    width: 100%;
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 8px;
  }}
  .progress-bar-fill {{
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #10b981 0%, #38bdf8 100%);
    border-radius: 3px;
    transition: width 0.3s ease;
    box-shadow: 0 0 8px rgba(56, 189, 248, 0.7);
  }}

  .actions-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    flex-wrap: wrap;
  }}
  .action-buttons {{
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .play-nav-btn {{
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: #ffffff;
    border: none;
    padding: 7px 14px;
    border-radius: 8px;
    font-weight: 800;
    font-size: 0.82rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 2px 10px rgba(16, 185, 129, 0.4);
    transition: transform 0.15s, background 0.2s;
  }}
  .play-nav-btn:hover {{
    transform: translateY(-1px);
    background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
  }}
  .sec-nav-btn {{
    background: rgba(255, 255, 255, 0.07);
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 6px 11px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.74rem;
    cursor: pointer;
    transition: all 0.2s;
  }}
  .sec-nav-btn:hover {{
    background: rgba(255, 255, 255, 0.15);
    color: #ffffff;
  }}
  .sec-nav-btn.active {{
    background: rgba(56, 189, 248, 0.35);
    border-color: #38bdf8;
    color: #38bdf8;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
  }}

  /* Spoken Subtitle Caption */
  .spoken-caption {{
    font-size: 0.73rem;
    color: #94a3b8;
    background: rgba(15, 23, 42, 0.6);
    padding: 4px 8px;
    border-radius: 6px;
    margin-top: 5px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    border-left: 3px solid #38bdf8;
  }}

  /* Custom Animated Leaflet Markers */
  /* 1. Small Boy Walking Avatar (Swiggy / Zomato reference) */
  .small-boy-marker {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    cursor: pointer;
  }}
  .radar-ring {{
    position: absolute;
    bottom: -4px;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: rgba(56, 189, 248, 0.35);
    border: 2px solid #38bdf8;
    animation: radarRipple 1.6s infinite ease-out;
    z-index: 1;
  }}
  .radar-ring.driving {{
    background: rgba(16, 185, 129, 0.35);
    border-color: #10b981;
  }}
  @keyframes radarRipple {{
    0% {{ transform: scale(0.3); opacity: 1; }}
    100% {{ transform: scale(1.6); opacity: 0; }}
  }}

  .avatar-rotator {{
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.25s linear;
    position: relative;
    z-index: 2;
  }}

  .avatar-character {{
    position: relative;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.6));
    animation: walkingBob 0.6s infinite alternate ease-in-out;
  }}
  .avatar-character.driving {{
    animation: drivingHum 0.3s infinite alternate ease-in-out;
  }}
  @keyframes walkingBob {{
    0% {{ transform: translateY(0px) rotate(-1deg); }}
    100% {{ transform: translateY(-3.5px) rotate(1deg); }}
  }}
  @keyframes drivingHum {{
    0% {{ transform: translateY(0px); }}
    100% {{ transform: translateY(-1.5px); }}
  }}

  /* Natural Walking Boy Limb Animations */
  .walking-leg-left {{
    transform-origin: 28px 42px;
    animation: legSwingLeft 0.5s infinite alternate ease-in-out;
  }}
  .walking-leg-right {{
    transform-origin: 38px 42px;
    animation: legSwingRight 0.5s infinite alternate ease-in-out;
  }}
  .walking-arm-left {{
    transform-origin: 22px 28px;
    animation: armSwingLeft 0.5s infinite alternate ease-in-out;
  }}
  .walking-arm-right {{
    transform-origin: 42px 28px;
    animation: armSwingRight 0.5s infinite alternate ease-in-out;
  }}
  @keyframes legSwingLeft {{
    0% {{ transform: rotate(-24deg); }}
    100% {{ transform: rotate(24deg); }}
  }}
  @keyframes legSwingRight {{
    0% {{ transform: rotate(24deg); }}
    100% {{ transform: rotate(-24deg); }}
  }}
  @keyframes armSwingLeft {{
    0% {{ transform: rotate(26deg); }}
    100% {{ transform: rotate(-26deg); }}
  }}
  @keyframes armSwingRight {{
    0% {{ transform: rotate(-26deg); }}
    100% {{ transform: rotate(26deg); }}
  }}

  /* Frozen state when user/character is stationary */
  .is-stopped .walking-leg-left,
  .is-stopped .walking-leg-right,
  .is-stopped .walking-arm-left,
  .is-stopped .walking-arm-right,
  .is-stopped .avatar-character {{
    animation-play-state: paused !important;
  }}

  /* Maneuver Steps Carousel Bar (Horizontal Scrollable) */
  .maneuver-steps-scroll {{
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding: 6px 0 2px 0;
    scrollbar-width: thin;
    scrollbar-color: #38bdf8 transparent;
  }}
  .step-pill {{
    flex: 0 0 auto;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 4px 10px;
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    font-size: 0.72rem;
    transition: all 0.2s;
  }}
  .step-pill:hover {{
    background: rgba(56, 189, 248, 0.15);
    border-color: #38bdf8;
  }}
  .step-pill.active {{
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.25) 0%, rgba(56, 189, 248, 0.25) 100%);
    border-color: #10b981;
    color: #ffffff;
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
  }}
</style>
</head>
<body>

<div class="gmaps-nav-container">
  <!-- Google Maps Turn Banner (Green Header) -->
  <div class="gmaps-turn-banner" id="turnBanner">
    <div class="turn-left">
      <div class="turn-icon-box" id="turnIconBox">🟢</div>
      <div class="turn-info">
        <div class="turn-distance" id="turnDistance">Starting...</div>
        <div class="turn-instruction" id="turnInstruction">Departing on safe corridor</div>
        <div class="turn-road" id="turnRoad">Initiating satellite guidance</div>
      </div>
    </div>
    <div class="turn-right-hud">
      <div class="next-preview" id="nextPreview">Then ➡️ in 1.2 km</div>
      <div style="font-size: 0.68rem; color: #a7f3d0; font-weight: 700;" id="hudEta">ETA: 32 mins</div>
    </div>
  </div>

  <!-- Swiggy / Zomato Style Live Delivery / Traveler Tracking Bar -->
  <div class="swiggy-tracking-bar">
    <div class="swiggy-status">
      <div class="status-pulse-dot" id="statusDot"></div>
      <span id="avatarStatusLabel">🚶‍♂️ Small Boy is moving on route • Swiggy/Zomato Tracker Active</span>
      <div class="voice-eq-wrap" id="voiceEq">
        <div class="voice-bar"></div>
        <div class="voice-bar"></div>
        <div class="voice-bar"></div>
      </div>
    </div>
    <div class="telemetry-badges">
      <div class="off-route-badge" id="offRouteBadge">⚠️ Off Route (>45m)</div>
      <div class="speed-pill" id="liveSpeedometer">🚶 5 km/h</div>
    </div>
  </div>

  <!-- Interactive Leaflet Map for Real-Time Path Rendering -->
  <div id="gmaps-map"></div>

  <!-- Floating HUD Avatar & Mode Switcher Overlay -->
  <div class="map-overlay-controls">
    <div class="avatar-switcher-group">
      <button class="hud-btn active" id="btnAvatarBoy" onclick="setAvatar('boy')">🚶 Boy</button>
      <button class="hud-btn" id="btnAvatarCar" onclick="setAvatar('car')">🚗 Car</button>
      <button class="hud-btn" id="btnAvatarBike" onclick="setAvatar('bike')">🏍️ Bike</button>
      <button class="hud-btn" id="btnAvatarTractor" onclick="setAvatar('tractor')">🚜 Tractor</button>
      <button class="hud-btn" id="btnAvatarTruck" onclick="setAvatar('truck')">🚚 Truck</button>
      <button class="hud-btn" id="btnAvatarBicycle" onclick="setAvatar('bicycle')">🚴 Cycle</button>
    </div>

    <div class="speed-switcher-group">
      <button class="hud-btn active" onclick="setSpeed(1, this)">1x</button>
      <button class="hud-btn" onclick="setSpeed(2, this)">2x</button>
      <button class="hud-btn" onclick="setSpeed(5, this)">5x</button>
    </div>
  </div>

  <!-- Bottom Navigation Control Console -->
  <div class="gmaps-bottom-console">
    <!-- Live Progress Bar -->
    <div class="progress-bar-wrap">
      <div class="progress-bar-fill" id="progressFill"></div>
    </div>
    <div style="display:flex; justify-content:space-between; font-size:0.72rem; color:#94a3b8; margin-bottom:6px;">
      <span id="transitProgressText">0% Completed</span>
      <span id="transitRemainingText">Calculating corridor...</span>
    </div>

    <div class="actions-row">
      <div class="action-buttons">
        <button class="play-nav-btn" id="btnPlayNav" onclick="togglePlay()">
          <span id="playIcon">▶️</span> <span id="playText">Start Navigation</span>
        </button>
        <button class="sec-nav-btn" id="btnGpsTrack" onclick="toggleGPSTracking()" title="Synchronize directly with physical device GPS">
          📡 Follow Live GPS
        </button>
        <button class="sec-nav-btn" onclick="restartNav()" title="Restart from beginning">🔁 Restart</button>
        <button class="sec-nav-btn" onclick="prevStep()" title="Previous turn">⏮️</button>
        <button class="sec-nav-btn" onclick="nextStep()" title="Next turn">⏭️</button>
        <button class="sec-nav-btn" id="btnVoiceToggle" onclick="toggleMute()" title="Mute/Unmute voice assistant">🔊 Audio ON</button>
      </div>

      <!-- Spoken text subtitle caption -->
      <div class="spoken-caption" id="spokenCaption">
        AI Voice Assistant ready. Tap Start Navigation or Follow Live GPS to guide step-by-step.
      </div>
    </div>

    <!-- Small Route Steps Selector -->
    <div class="maneuver-steps-scroll" id="stepsScroll"></div>
  </div>
</div>

<script>
  const navData = {json_data};
  const polyline = navData.polyline || [];
  const steps = navData.steps || [];

  let map = null;
  let fullPolylineLayer = null;
  let smallRouteHighlightLayer = null;
  let avatarMarker = null;

  let currentAvatar = navData.default_avatar || "boy";
  let isNavigating = false;
  let currentStepIdx = 0;
  let progressRatio = 0.0;
  let simSpeedMultiplier = 1;
  let isVoiceMuted = false;
  let currentSpeechUtterance = null;
  let animFrameId = null;

  // Flattened route path & cumulative distances
  let pathPoints = [];
  let cumDists = [0];
  let totalDistanceM = 1.0;

  // GPS Tracking State
  let isTrackingGPS = false;
  let gpsWatchId = null;
  let userSpeedKmh = 0.0;
  let lastGpsCoords = null;
  let lastGpsTimestamp = 0;
  let announcedSteps = new Set();
  let lastOffRouteAnnounceTime = 0;

  function initMap() {{
    if (!polyline || polyline.length === 0) return;

    pathPoints = polyline;
    for (let i = 1; i < pathPoints.length; i++) {{
      const d = calcDistanceM(pathPoints[i-1], pathPoints[i]);
      cumDists.push(cumDists[cumDists.length - 1] + d);
    }}
    totalDistanceM = cumDists[cumDists.length - 1] || 1.0;

    const startPt = pathPoints[0];
    const endPt = pathPoints[pathPoints.length - 1];
    const midLat = (startPt[0] + endPt[0]) / 2;
    const midLon = (startPt[1] + endPt[1]) / 2;

    map = L.map('gmaps-map', {{
      center: [midLat, midLon],
      zoom: 14,
      zoomControl: false,
      attributionControl: false
    }});

    // Modern CartoDB Voyager / Tactical Navigation style tiles
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png', {{
      maxZoom: 19,
      subdomains: 'abcd'
    }}).addTo(map);

    // Full Route Background line
    fullPolylineLayer = L.polyline(pathPoints, {{
      color: '#38bdf8',
      weight: 6,
      opacity: 0.65,
      lineCap: 'round'
    }}).addTo(map);

    // Dynamic Small Route Highlight Layer (Active Segment)
    smallRouteHighlightLayer = L.polyline([], {{
      color: '#10b981',
      weight: 9,
      opacity: 0.95,
      dashArray: '8, 8',
      lineCap: 'round'
    }}).addTo(map);

    // Origin Marker
    L.marker(startPt, {{
      icon: L.divIcon({{
        className: 'origin-marker',
        html: '<div style="background:#0284c7;color:#fff;border:2px solid #fff;border-radius:50%;width:22px;height:22px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:bold;box-shadow:0 0 10px #0284c7;">📍</div>',
        iconSize: [22, 22],
        iconAnchor: [11, 11]
      }})
    }}).addTo(map);

    // Destination Marker
    L.marker(endPt, {{
      icon: L.divIcon({{
        className: 'dest-marker',
        html: '<div style="background:#10b981;color:#fff;border:2px solid #fff;border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;font-size:14px;box-shadow:0 0 14px #10b981;">🏁</div>',
        iconSize: [26, 26],
        iconAnchor: [13, 13]
      }})
    }}).addTo(map);

    // Fit map bounds
    map.fitBounds(fullPolylineLayer.getBounds(), {{ padding: [30, 30] }});

    // Create Avatar Marker with initial road bearing
    const initialBearing = pathPoints.length > 1 ? calculateBearing(pathPoints[0], pathPoints[1]) : 0;
    createAvatarMarker(startPt, initialBearing);

    // Build Steps Scroll Bar
    buildStepsPills();

    // Set initial avatar state
    setAvatar(currentAvatar);

    // Update HUD for first step
    updateStepHUD(0, false);

    // Auto-start if requested
    if (navData.auto_start) {{
      setTimeout(() => {{
        startNavigation();
      }}, 600);
    }}
  }}

  function getAvatarHTML(type) {{
    if (type === 'boy') {{
      // Small Boy Walking Avatar with animated legs, swinging arms, backpack & Swiggy/Zomato pulse
      return `
        <div class="small-boy-marker is-stopped" id="avatarMarkerWrap">
          <div class="radar-ring"></div>
          <div class="avatar-rotator" id="avatarRotator">
            <div class="avatar-character">
              <svg width="48" height="48" viewBox="0 0 64 64" fill="none">
                <!-- Backpack -->
                <rect x="12" y="24" width="12" height="18" rx="4" fill="#0284c7" stroke="#38bdf8" stroke-width="2"/>
                <path d="M14 26 L14 40" stroke="#bae6fd" stroke-width="1.5"/>
                <!-- Left Leg with animated swing -->
                <g class="walking-leg-left">
                  <line x1="28" y1="42" x2="24" y2="58" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round"/>
                  <ellipse cx="23" cy="58" rx="4.5" ry="3" fill="#ef4444"/>
                </g>
                <!-- Right Leg with animated counter-swing -->
                <g class="walking-leg-right">
                  <line x1="38" y1="42" x2="42" y2="58" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round"/>
                  <ellipse cx="43" cy="58" rx="4.5" ry="3" fill="#ef4444"/>
                </g>
                <!-- Left Arm -->
                <g class="walking-arm-left">
                  <line x1="22" y1="28" x2="16" y2="38" stroke="#fde047" stroke-width="3" stroke-linecap="round"/>
                </g>
                <!-- Torso (Green Delivery/Swiggy T-Shirt) -->
                <rect x="22" y="24" width="20" height="20" rx="5" fill="#10b981" stroke="#059669" stroke-width="2"/>
                <rect x="29" y="28" width="6" height="5" rx="1.5" fill="#ffffff" opacity="0.85"/>
                <!-- Right Arm -->
                <g class="walking-arm-right">
                  <line x1="42" y1="28" x2="48" y2="38" stroke="#fde047" stroke-width="3.5" stroke-linecap="round"/>
                </g>
                <!-- Boy Head & Neck -->
                <circle cx="32" cy="15" r="9" fill="#fde047" stroke="#ca8a04" stroke-width="1.5"/>
                <!-- Red Cap with Visor -->
                <path d="M22 13 C22 7, 42 7, 42 13 L47 14 L22 14 Z" fill="#ef4444"/>
                <!-- Eyes & Friendly Smile -->
                <circle cx="30" cy="14" r="1.5" fill="#0f172a"/>
                <circle cx="36" cy="14" r="1.5" fill="#0f172a"/>
                <path d="M30 18 Q33 21 36 18" stroke="#0f172a" stroke-width="1.5" fill="none" stroke-linecap="round"/>
                <!-- Headset -->
                <circle cx="23" cy="15" r="2" fill="#38bdf8"/>
              </svg>
            </div>
          </div>
        </div>
      `;
    }} else if (type === 'tractor') {{
      // Tractor (Agricultural & Rural Transport)
      return `
        <div class="small-boy-marker" id="avatarMarkerWrap">
          <div class="radar-ring driving" style="border-color:#16a34a; background:rgba(22,163,74,0.35);"></div>
          <div class="avatar-rotator" id="avatarRotator">
            <div class="avatar-character driving">
              <svg width="48" height="48" viewBox="0 0 64 64" fill="none">
                <line x1="22" y1="20" x2="22" y2="8" stroke="#475569" stroke-width="3" stroke-linecap="round"/>
                <circle cx="22" cy="6" r="3" fill="#cbd5e1" opacity="0.8"/>
                <rect x="16" y="20" width="22" height="18" rx="4" fill="#15803d" stroke="#166534" stroke-width="2"/>
                <circle cx="16" cy="27" r="2.5" fill="#fef08a"/>
                <path d="M38 38 L38 12 L52 12 L52 38" stroke="#1e293b" stroke-width="3" stroke-linecap="round"/>
                <rect x="36" y="10" width="18" height="4" rx="2" fill="#ca8a04"/>
                <circle cx="45" cy="20" r="5" fill="#fde047"/>
                <circle cx="18" cy="46" r="8" fill="#1e293b" stroke="#eab308" stroke-width="3"/>
                <circle cx="18" cy="46" r="3" fill="#94a3b8"/>
                <circle cx="48" cy="42" r="14" fill="#0f172a" stroke="#eab308" stroke-width="4"/>
                <circle cx="48" cy="42" r="6" fill="#15803d"/>
              </svg>
            </div>
          </div>
        </div>
      `;
    }} else if (type === 'bike' || type === 'rider') {{
      // Bike / Motorcycle (Two-Wheeler)
      return `
        <div class="small-boy-marker" id="avatarMarkerWrap">
          <div class="radar-ring driving" style="border-color:#0284c7; background:rgba(2,132,199,0.35);"></div>
          <div class="avatar-rotator" id="avatarRotator">
            <div class="avatar-character driving">
              <svg width="46" height="46" viewBox="0 0 64 64" fill="none">
                <circle cx="16" cy="44" r="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2.5"/>
                <circle cx="48" cy="44" r="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2.5"/>
                <path d="M16 44 L30 32 L40 32 L48 44" stroke="#e11d48" stroke-width="4" stroke-linecap="round"/>
                <circle cx="35" cy="20" r="7" fill="#fde047" stroke="#0284c7" stroke-width="2"/>
                <path d="M35 15 L44 15" stroke="#ef4444" stroke-width="3" stroke-linecap="round"/>
                <circle cx="50" cy="36" r="3" fill="#fef08a"/>
              </svg>
            </div>
          </div>
        </div>
      `;
    }} else if (type === 'truck') {{
      // Heavy Truck
      return `
        <div class="small-boy-marker" id="avatarMarkerWrap">
          <div class="radar-ring driving" style="border-color:#f59e0b; background:rgba(245,158,11,0.35);"></div>
          <div class="avatar-rotator" id="avatarRotator">
            <div class="avatar-character driving">
              <svg width="50" height="50" viewBox="0 0 64 64" fill="none">
                <rect x="10" y="24" width="28" height="20" rx="3" fill="#f59e0b" stroke="#d97706" stroke-width="2"/>
                <rect x="38" y="28" width="16" height="16" rx="3" fill="#1e293b" stroke="#475569" stroke-width="2"/>
                <rect x="42" y="30" width="8" height="6" rx="1.5" fill="#38bdf8" opacity="0.9"/>
                <circle cx="18" cy="46" r="6" fill="#0f172a" stroke="#cbd5e1" stroke-width="2"/>
                <circle cx="32" cy="46" r="6" fill="#0f172a" stroke="#cbd5e1" stroke-width="2"/>
                <circle cx="46" cy="46" r="6" fill="#0f172a" stroke="#cbd5e1" stroke-width="2"/>
              </svg>
            </div>
          </div>
        </div>
      `;
    }} else if (type === 'bicycle') {{
      // Bicycle
      return `
        <div class="small-boy-marker" id="avatarMarkerWrap">
          <div class="radar-ring driving" style="border-color:#10b981; background:rgba(16,185,129,0.35);"></div>
          <div class="avatar-rotator" id="avatarRotator">
            <div class="avatar-character driving">
              <svg width="44" height="44" viewBox="0 0 64 64" fill="none">
                <circle cx="16" cy="44" r="9" fill="none" stroke="#10b981" stroke-width="3"/>
                <circle cx="48" cy="44" r="9" fill="none" stroke="#10b981" stroke-width="3"/>
                <path d="M16 44 L32 44 L40 30 L48 44 M32 44 L26 30 L40 30" stroke="#f1f5f9" stroke-width="2.5" stroke-linecap="round"/>
                <circle cx="28" cy="18" r="6" fill="#fde047"/>
              </svg>
            </div>
          </div>
        </div>
      `;
    }} else {{
      // Driving Car (Google Maps GPS Vehicle Arrow)
      return `
        <div class="small-boy-marker" id="avatarMarkerWrap">
          <div class="radar-ring driving"></div>
          <div class="avatar-rotator" id="avatarRotator">
            <div class="avatar-character driving">
              <svg width="46" height="46" viewBox="0 0 64 64" fill="none">
                <path d="M32 6 L14 54 L32 44 L50 54 Z" fill="rgba(56, 189, 248, 0.25)"/>
                <rect x="20" y="20" width="24" height="34" rx="7" fill="#0284c7" stroke="#38bdf8" stroke-width="2"/>
                <rect x="24" y="26" width="16" height="9" rx="3" fill="#0f172a"/>
                <rect x="24" y="42" width="16" height="5" rx="2" fill="#0f172a"/>
                <rect x="25" y="32" width="14" height="12" rx="3" fill="#0369a1"/>
                <circle cx="23" cy="22" r="2.5" fill="#fef08a"/>
                <circle cx="41" cy="22" r="2.5" fill="#fef08a"/>
                <circle cx="23" cy="52" r="2" fill="#ef4444"/>
                <circle cx="41" cy="52" r="2" fill="#ef4444"/>
              </svg>
            </div>
          </div>
        </div>
      `;
    }}
  }}

  function createAvatarMarker(latLon, initialBearing) {{
    avatarMarker = L.marker(latLon, {{
      icon: L.divIcon({{
        className: 'custom-traveler-avatar',
        html: getAvatarHTML(currentAvatar),
        iconSize: [48, 48],
        iconAnchor: [24, 24]
      }}),
      zIndexOffset: 1000
    }}).addTo(map);

    setTimeout(() => {{
      setAvatarRotation(initialBearing);
    }}, 100);
  }}

  function setAvatar(type) {{
    currentAvatar = type;
    const btnIds = ['btnAvatarCar', 'btnAvatarBike', 'btnAvatarTractor', 'btnAvatarTruck', 'btnAvatarBoy', 'btnAvatarBicycle'];
    btnIds.forEach(id => {{
      const b = document.getElementById(id);
      if (b) b.classList.remove('active');
    }});

    if (type === 'car') document.getElementById('btnAvatarCar')?.classList.add('active');
    else if (type === 'bike' || type === 'rider') document.getElementById('btnAvatarBike')?.classList.add('active');
    else if (type === 'tractor') document.getElementById('btnAvatarTractor')?.classList.add('active');
    else if (type === 'truck') document.getElementById('btnAvatarTruck')?.classList.add('active');
    else if (type === 'boy') document.getElementById('btnAvatarBoy')?.classList.add('active');
    else if (type === 'bicycle') document.getElementById('btnAvatarBicycle')?.classList.add('active');

    const statusLbl = document.getElementById('avatarStatusLabel');
    const spdLbl = document.getElementById('liveSpeedometer');

    if (type === 'tractor') {{
      statusLbl.innerText = "🚜 Tractor in transit • Safe rural corridor";
      spdLbl.innerText = "🚜 25 km/h";
    }} else if (type === 'bike' || type === 'rider') {{
      statusLbl.innerText = "🏍️ Bike / Motorcycle in transit • Live Route Alignment";
      spdLbl.innerText = "🏍️ 55 km/h";
    }} else if (type === 'truck') {{
      statusLbl.innerText = "🚚 Heavy Truck en route • Clearance verified";
      spdLbl.innerText = "🚚 40 km/h";
    }} else if (type === 'boy') {{
      statusLbl.innerText = "🚶‍♂️ Small Boy walking on route • Swiggy/Zomato Tracking Active";
      spdLbl.innerText = "🚶 5 km/h";
    }} else if (type === 'bicycle') {{
      statusLbl.innerText = "🚴 Bicycle en route • Eco-transit mode";
      spdLbl.innerText = "🚴 15 km/h";
    }} else {{
      statusLbl.innerText = "🚗 Driving Car en route • Google Maps Navigation Guidance";
      spdLbl.innerText = "🚗 60 km/h";
    }}

    if (avatarMarker) {{
      avatarMarker.setIcon(L.divIcon({{
        className: 'custom-traveler-avatar',
        html: getAvatarHTML(type),
        iconSize: [48, 48],
        iconAnchor: [24, 24]
      }}));
    }}
  }}

  function setAvatarRotation(bearing) {{
    const rotEl = document.getElementById('avatarRotator');
    if (!rotEl || bearing === undefined || bearing === null) return;

    if (currentAvatar === 'car' || currentAvatar === 'bike' || currentAvatar === 'tractor' || currentAvatar === 'truck' || currentAvatar === 'bicycle') {{
      // Full 360 degree vehicle alignment to road angle
      rotEl.style.transform = `rotate(${{bearing}}deg)`;
    }} else {{
      // Walking boy faces travel direction (flips horizontally if moving westward)
      const isWest = (bearing > 180 && bearing < 360);
      rotEl.style.transform = isWest ? 'scaleX(-1)' : 'scaleX(1)';
    }}
  }}

  function setSpeed(mult, btn) {{
    simSpeedMultiplier = mult;
    document.querySelectorAll('.speed-switcher-group .hud-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
  }}

  function buildStepsPills() {{
    const scrollBox = document.getElementById('stepsScroll');
    scrollBox.innerHTML = '';
    steps.forEach((s, idx) => {{
      const pill = document.createElement('div');
      pill.className = 'step-pill' + (idx === 0 ? ' active' : '');
      pill.id = 'stepPill_' + idx;
      pill.innerHTML = `<span>${{s.icon || '➡️'}}</span> <b>Step ${{s.step_num}}:</b> ${{s.road}} <span style="color:#38bdf8;">(${{s.distance_display}})</span>`;
      pill.onclick = () => jumpToStep(idx);
      scrollBox.appendChild(pill);
    }});
  }}

  function highlightStepPill(stepIdx) {{
    document.querySelectorAll('.step-pill').forEach((p, i) => {{
      p.classList.toggle('active', i === stepIdx);
    }});
    const activePill = document.getElementById('stepPill_' + stepIdx);
    if (activePill) {{
      activePill.scrollIntoView({{ behavior: 'smooth', inline: 'center' }});
    }}
  }}

  function updateStepHUD(stepIdx, speakAnnouncement = true) {{
    if (!steps || steps.length === 0) return;
    const s = steps[Math.min(stepIdx, steps.length - 1)];
    const nextS = steps[stepIdx + 1] || null;

    document.getElementById('turnIconBox').innerText = s.icon || '➡️';
    document.getElementById('turnDistance').innerText = s.distance_display || 'In 100 m';
    document.getElementById('turnInstruction').innerText = s.instruction || 'Continue';
    document.getElementById('turnRoad').innerText = `Road: ${{s.road}}`;

    if (nextS) {{
      document.getElementById('nextPreview').innerText = `Then ${{nextS.icon}} ${{nextS.instruction}} (${{nextS.distance_display}})`;
    }} else {{
      document.getElementById('nextPreview').innerText = `🏁 Final Leg to Destination`;
    }}

    // Highlight Small Route Segment on Map
    const segCoords = s.segment_coordinates || [];
    if (segCoords.length >= 2) {{
      smallRouteHighlightLayer.setLatLngs(segCoords);
    }}

    highlightStepPill(stepIdx);

    // Speak Turn Instruction using AI Voice Assistant
    if (speakAnnouncement && !isVoiceMuted) {{
      const textToSpeak = (stepIdx === 0 && isNavigating) ? navData.initial_spoken : s.spoken;
      speakAIVoice(textToSpeak);
    }}
  }}

  function speakAIVoice(text) {{
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    utterance.lang = 'en-US';

    const voices = window.speechSynthesis.getVoices();
    const naturalVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha')));
    if (naturalVoice) utterance.voice = naturalVoice;

    currentSpeechUtterance = utterance;

    const captionEl = document.getElementById('spokenCaption');
    if (captionEl) captionEl.innerText = text;

    utterance.onstart = () => {{
      document.getElementById('voiceEq').classList.add('speaking');
    }};
    utterance.onend = () => {{
      document.getElementById('voiceEq').classList.remove('speaking');
    }};
    utterance.onerror = () => {{
      document.getElementById('voiceEq').classList.remove('speaking');
    }};

    window.speechSynthesis.speak(utterance);
  }}

  function toggleMute() {{
    isVoiceMuted = !isVoiceMuted;
    const btn = document.getElementById('btnVoiceToggle');
    if (isVoiceMuted) {{
      btn.innerText = "🔇 Audio OFF";
      window.speechSynthesis.cancel();
      document.getElementById('voiceEq').classList.remove('speaking');
    }} else {{
      btn.innerText = "🔊 Audio ON";
      if (steps[currentStepIdx]) {{
        speakAIVoice(steps[currentStepIdx].spoken);
      }}
    }}
  }}

  function togglePlay() {{
    if (isNavigating) {{
      pauseNavigation();
    }} else {{
      startNavigation();
    }}
  }}

  function startNavigation() {{
    isNavigating = true;
    document.getElementById('playIcon').innerText = "⏸️";
    document.getElementById('playText').innerText = "Pause Navigation";
    document.getElementById('statusDot').style.background = "#10b981";

    const wrap = document.getElementById('avatarMarkerWrap');
    if (wrap) wrap.classList.remove('is-stopped');

    // Speak initial route briefing if at start
    if (progressRatio <= 0.05) {{
      speakAIVoice(navData.initial_spoken);
    }}

    lastTimestamp = performance.now();
    runAnimationLoop();
  }}

  function pauseNavigation() {{
    isNavigating = false;
    document.getElementById('playIcon').innerText = "▶️";
    document.getElementById('playText').innerText = "Resume Navigation";
    document.getElementById('statusDot').style.background = "#f59e0b";

    const wrap = document.getElementById('avatarMarkerWrap');
    if (wrap) wrap.classList.add('is-stopped');

    if (animFrameId) cancelAnimationFrame(animFrameId);
    window.speechSynthesis.pause();
  }}

  function restartNav() {{
    pauseNavigation();
    progressRatio = 0.0;
    currentStepIdx = 0;
    announcedSteps.clear();

    const startPt = pathPoints[0];
    const initialBearing = pathPoints.length > 1 ? calculateBearing(pathPoints[0], pathPoints[1]) : 0;
    updateAvatarPosition(startPt, initialBearing, false);

    updateStepHUD(0, false);
    document.getElementById('progressFill').style.width = '0%';
    document.getElementById('transitProgressText').innerText = '0% Completed';
    map.panTo(startPt);
    startNavigation();
  }}

  function jumpToStep(idx) {{
    currentStepIdx = idx;
    const s = steps[idx];
    if (s && s.segment_coordinates && s.segment_coordinates.length > 0) {{
      const pt = s.segment_coordinates[0];
      const bearing = s.segment_coordinates.length > 1 ? calculateBearing(s.segment_coordinates[0], s.segment_coordinates[1]) : 0;
      updateAvatarPosition(pt, bearing, isNavigating);
      map.panTo(pt);

      progressRatio = Math.max(0.0, Math.min(1.0, idx / Math.max(1, steps.length)));
      document.getElementById('progressFill').style.width = (progressRatio * 100) + '%';
      document.getElementById('transitProgressText').innerText = `${{Math.round(progressRatio * 100)}}% Completed`;
    }}
    updateStepHUD(idx, true);
  }}

  function nextStep() {{
    if (currentStepIdx < steps.length - 1) {{
      jumpToStep(currentStepIdx + 1);
    }}
  }}

  function prevStep() {{
    if (currentStepIdx > 0) {{
      jumpToStep(currentStepIdx - 1);
    }}
  }}

  function updateAvatarPosition(latLon, bearing, isMoving = true) {{
    if (avatarMarker) {{
      avatarMarker.setLatLng(latLon);
    }}
    const wrap = document.getElementById('avatarMarkerWrap');
    if (wrap) {{
      if (isMoving) {{
        wrap.classList.remove('is-stopped');
      }} else {{
        wrap.classList.add('is-stopped');
      }}
    }}
    setAvatarRotation(bearing);
  }}

  // Route Snapping & Projection Algorithm (Perpendicular Nearest Point)
  function projectPointOnSegment(p, p1, p2) {{
    const latMid = (p1[0] + p2[0]) / 2;
    const mPerDegLat = 111132.92;
    const mPerDegLon = 111412.84 * Math.cos(latMid * Math.PI / 180);

    const x1 = (p1[1] - p[1]) * mPerDegLon;
    const y1 = (p1[0] - p[0]) * mPerDegLat;
    const x2 = (p2[1] - p[1]) * mPerDegLon;
    const y2 = (p2[0] - p[0]) * mPerDegLat;

    const dx = x2 - x1;
    const dy = y2 - y1;
    const lenSq = dx * dx + dy * dy;

    if (lenSq === 0) {{
      return {{ pt: p1, distM: Math.hypot(x1, y1), t: 0 }};
    }}

    let t = -(x1 * dx + y1 * dy) / lenSq;
    t = Math.max(0, Math.min(1, t));

    const projLat = p1[0] + t * (p2[0] - p1[0]);
    const projLon = p1[1] + t * (p2[1] - p1[1]);
    const projX = x1 + t * dx;
    const projY = y1 + t * dy;
    const distM = Math.hypot(projX, projY);

    return {{ pt: [projLat, projLon], distM: distM, t: t }};
  }}

  function snapToRoute(lat, lon) {{
    if (!pathPoints || pathPoints.length < 2) return null;

    let minDistance = Infinity;
    let bestPoint = pathPoints[0];
    let bestSegIdx = 0;
    let bestT = 0;

    for (let i = 0; i < pathPoints.length - 1; i++) {{
      const res = projectPointOnSegment([lat, lon], pathPoints[i], pathPoints[i + 1]);
      if (res.distM < minDistance) {{
        minDistance = res.distM;
        bestPoint = res.pt;
        bestSegIdx = i;
        bestT = res.t;
      }}
    }}

    return {{
      snappedPt: bestPoint,
      distanceFromRouteM: minDistance,
      segIdx: bestSegIdx,
      t: bestT
    }};
  }}

  // Live Browser GPS Synchronization Mode
  function toggleGPSTracking() {{
    if (isTrackingGPS) {{
      stopGPSTracking();
    }} else {{
      startGPSTracking();
    }}
  }}

  function startGPSTracking() {{
    if (!navigator.geolocation) {{
      speakAIVoice("Device GPS is not supported by your browser. Running simulated route tracking.");
      return;
    }}
    if (isNavigating) pauseNavigation();

    isTrackingGPS = true;
    const btn = document.getElementById('btnGpsTrack');
    if (btn) btn.classList.add('active');
    document.getElementById('statusDot').style.background = "#38bdf8";
    speakAIVoice("Live GPS tracking synchronized. Character will now follow your physical walking position.");

    gpsWatchId = navigator.geolocation.watchPosition(
      onGPSLocationUpdate,
      onGPSError,
      {{ enableHighAccuracy: true, maximumAge: 1500, timeout: 12000 }}
    );
  }}

  function stopGPSTracking() {{
    isTrackingGPS = false;
    if (gpsWatchId) {{
      navigator.geolocation.clearWatch(gpsWatchId);
      gpsWatchId = null;
    }}
    const btn = document.getElementById('btnGpsTrack');
    if (btn) btn.classList.remove('active');
    document.getElementById('statusDot').style.background = "#10b981";
  }}

  function onGPSError(err) {{
    console.warn("GPS tracking error:", err);
    speakAIVoice("GPS signal interrupted. Resuming simulated corridor guidance.");
    stopGPSTracking();
  }}

  function onGPSLocationUpdate(pos) {{
    const rawLat = pos.coords.latitude;
    const rawLon = pos.coords.longitude;
    const rawSpeedMps = pos.coords.speed;
    const now = performance.now();

    if (rawSpeedMps !== null && rawSpeedMps >= 0) {{
      userSpeedKmh = rawSpeedMps * 3.6;
    }} else if (lastGpsCoords) {{
      const dt = (now - lastGpsTimestamp) / 1000.0;
      if (dt > 0.4) {{
        const d = calcDistanceM(lastGpsCoords, [rawLat, rawLon]);
        userSpeedKmh = (d / dt) * 3.6;
      }}
    }}
    lastGpsCoords = [rawLat, rawLon];
    lastGpsTimestamp = now;

    const snap = snapToRoute(rawLat, rawLon);
    if (!snap) return;

    const isStationary = (userSpeedKmh < 0.9);
    const spdLbl = document.getElementById('liveSpeedometer');
    if (spdLbl) {{
      spdLbl.innerText = isStationary ? '⏸️ Stopped (0 km/h)' : `🚶 ${{userSpeedKmh.toFixed(1)}} km/h`;
    }}

    // Check off-route status (>45 meters away)
    const offBadge = document.getElementById('offRouteBadge');
    if (snap.distanceFromRouteM > 45) {{
      if (offBadge) {{
        offBadge.style.display = 'block';
        offBadge.innerText = `⚠️ Off Route (${{Math.round(snap.distanceFromRouteM)}}m deviation)`;
      }}
      if (now - lastOffRouteAnnounceTime > 16000) {{
        lastOffRouteAnnounceTime = now;
        speakAIVoice(`Caution: You are ${{Math.round(snap.distanceFromRouteM)}} meters off the safe travel corridor.`);
      }}
    }} else {{
      if (offBadge) offBadge.style.display = 'none';
    }}

    // Calculate forward road heading
    const p0 = pathPoints[snap.segIdx];
    const p1 = pathPoints[Math.min(snap.segIdx + 1, pathPoints.length - 1)];
    const bearing = calculateBearing(p0, p1);

    // Update avatar position & movement state
    updateAvatarPosition(snap.snappedPt, bearing, !isStationary);
    map.panTo(snap.snappedPt, {{ animate: true, duration: 0.5 }});

    // Calculate distance traveled along route
    const segSpanDist = (cumDists[snap.segIdx + 1] || cumDists[snap.segIdx]) - cumDists[snap.segIdx];
    const traveledDistM = cumDists[snap.segIdx] + (snap.t * segSpanDist);
    progressRatio = Math.max(0, Math.min(1, traveledDistM / totalDistanceM));

    document.getElementById('progressFill').style.width = (progressRatio * 100) + '%';
    document.getElementById('transitProgressText').innerText = `${{Math.round(progressRatio * 100)}}% Completed`;

    checkTurnProximityAndSpeak(traveledDistM);
  }}

  // Turn Proximity Triggering: announces maneuvers ahead of turns
  function checkTurnProximityAndSpeak(traveledDistM) {{
    for (let i = 0; i < steps.length; i++) {{
      const s = steps[i];
      const stepTargetM = (s.cumulative_distance_m !== undefined) ? s.cumulative_distance_m : ((i + 1) / steps.length) * totalDistanceM;
      const distToTurn = stepTargetM - traveledDistM;

      if (distToTurn <= 90 && distToTurn > 25 && !announcedSteps.has(i + '_ahead')) {{
        announcedSteps.add(i + '_ahead');
        currentStepIdx = i;
        updateStepHUD(i, true);
        break;
      }} else if (distToTurn <= 20 && distToTurn >= -15 && !announcedSteps.has(i + '_now')) {{
        announcedSteps.add(i + '_now');
        currentStepIdx = i;
        updateStepHUD(i, true);
        break;
      }}
    }}
  }}

  // Simulation Animation Loop (Faithful to route bends and distance physics)
  let lastTimestamp = 0;
  function runAnimationLoop(timestamp) {{
    if (!isNavigating) return;

    if (!timestamp) timestamp = performance.now();
    const dt = (timestamp - lastTimestamp) / 1000.0;
    lastTimestamp = timestamp;

    // Realistic walking velocity: 4.8 km/h = 1.33 m/s scaled by sim multiplier
    const baseMps = (currentAvatar === 'boy') ? 1.33 : ((currentAvatar === 'tractor') ? 6.94 : 16.6);
    const deltaMeters = (baseMps * simSpeedMultiplier) * dt;

    let currentTraveledM = progressRatio * totalDistanceM + deltaMeters;
    progressRatio = Math.min(1.0, currentTraveledM / totalDistanceM);

    if (progressRatio >= 1.0) {{
      progressRatio = 1.0;
      isNavigating = false;
      document.getElementById('playIcon').innerText = "▶️";
      document.getElementById('playText').innerText = "Start Navigation";
      document.getElementById('progressFill').style.width = '100%';
      document.getElementById('transitProgressText').innerText = '100% Completed';

      const endPt = pathPoints[pathPoints.length - 1];
      const finalBearing = pathPoints.length > 1 ? calculateBearing(pathPoints[pathPoints.length - 2], endPt) : 0;
      updateAvatarPosition(endPt, finalBearing, false);

      speakAIVoice(`You have reached your safe destination: ${{navData.destination_label}}. Navigation completed.`);
      return;
    }}

    // Find current polyline segment matching traveled distance
    let idx = 0;
    while (idx < cumDists.length - 1 && cumDists[idx + 1] < currentTraveledM) {{
      idx++;
    }}

    const segStartDist = cumDists[idx];
    const segEndDist = cumDists[idx + 1] || (segStartDist + 0.001);
    const segT = Math.max(0, Math.min(1, (currentTraveledM - segStartDist) / (segEndDist - segStartDist)));

    const p0 = pathPoints[idx];
    const p1 = pathPoints[Math.min(idx + 1, pathPoints.length - 1)];
    const currentLat = p0[0] + (p1[0] - p0[0]) * segT;
    const currentLon = p0[1] + (p1[1] - p0[1]) * segT;

    const bearing = calculateBearing(p0, p1);
    updateAvatarPosition([currentLat, currentLon], bearing, true);

    // Keep map centered on traveler (Smooth Google Maps auto-follow)
    if (idx % 4 === 0) {{
      map.panTo([currentLat, currentLon], {{ animate: true, duration: 0.25 }});
    }}

    // Check turn maneuvers and speech triggers
    checkTurnProximityAndSpeak(currentTraveledM);

    // Update progress text and remaining leg
    const remainingM = Math.max(0, totalDistanceM - currentTraveledM);
    const remStr = (remainingM >= 1000) ? `${{(remainingM/1000).toFixed(1)}} km remaining` : `${{Math.round(remainingM)}} m remaining`;
    document.getElementById('progressFill').style.width = (progressRatio * 100) + '%';
    document.getElementById('transitProgressText').innerText = `${{Math.round(progressRatio * 100)}}% Completed`;
    document.getElementById('transitRemainingText').innerText = remStr;

    animFrameId = requestAnimationFrame(runAnimationLoop);
  }}

  // Bearing calculation (0-360 degrees forward azimuth)
  function calculateBearing(p0, p1) {{
    const dLon = (p1[1] - p0[1]) * Math.PI / 180;
    const lat1 = p0[0] * Math.PI / 180;
    const lat2 = p1[0] * Math.PI / 180;
    const y = Math.sin(dLon) * Math.cos(lat2);
    const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);
    const brng = Math.atan2(y, x) * 180 / Math.PI;
    return (brng + 360) % 360;
  }}

  // Haversine formula in JS
  function calcDistanceM(p1, p2) {{
    const R = 6371000;
    const dLat = (p2[0] - p1[0]) * Math.PI / 180;
    const dLon = (p2[1] - p1[1]) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(p1[0] * Math.PI / 180) * Math.cos(p2[0] * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }}

  window.addEventListener('DOMContentLoaded', initMap);
</script>
</body>
</html>
"""
