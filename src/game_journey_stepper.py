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
# Regional Geographic Localities & Landmarks Registry for Andhra Pradesh / Guntur / Tenali / Amaravati
REGIONAL_GEOGRAPHIC_LOCALITIES: Dict[str, Tuple[float, float]] = {
    # Vadlamudi & Vignan Campus Zone
    "Vignan University": (16.2335, 80.5505),
    "Vadlamudi Center": (16.2319, 80.5539),
    "Vadlamudi Hub": (16.2385, 80.5420),
    "Sangam Jagarlamudi": (16.2350, 80.5050),
    "Selapadu": (16.2480, 80.5220),
    "Sekuru": (16.2550, 80.5150),
    "Sitarampuram": (16.2410, 80.5180),
    "Gundavaram": (16.2380, 80.4780),
    "Godavarru": (16.2450, 80.4720),
    "Narakoduru Junction": (16.2650, 80.4980),
    "Chebrolu Heritage Center": (16.2010, 80.5280),
    "Chebrolu Cross": (16.2050, 80.5280),
    "Kothareddypalem": (16.2180, 80.4850),
    "Pathareddypalem": (16.2120, 80.4890),
    "Budampadu Cross": (16.2620, 80.4680),
    "Lemallepadu": (16.2220, 80.4550),
    "Vatticherukuru": (16.1980, 80.4450),
    "Kovelamudi": (16.2050, 80.4680),

    # Tenali Town & Surrounding Localities
    "Angalakuduru": (16.2280, 80.6220),
    "Angalakuduru Gate": (16.2320, 80.6150),
    "Chenchupet": (16.2450, 80.6350),
    "Morrispet": (16.2380, 80.6450),
    "Nazerpet": (16.2410, 80.6480),
    "Pinapadu": (16.2490, 80.6290),
    "Chinaravuru": (16.2520, 80.6550),
    "Tenali Market": (16.2415, 80.6385),
    "Tenali Town Center": (16.2430, 80.6400),
    "Tenali Junction": (16.2395, 80.6465),
    "Tenali Bypass East": (16.2420, 80.5850),
    "Tenali North Link": (16.2620, 80.6050),
    "Kolakaluru": (16.2950, 80.6150),
    "Duggirala": (16.3280, 80.6280),
    "Pedavadlapudi": (16.4150, 80.6050),
    "Koppuravuru": (16.2820, 80.4880),

    # Guntur City & Environs
    "Guntur Autonagar": (16.2890, 80.4550),
    "Guntur City Center": (16.3067, 80.4365),
    "Guntur Railway Station": (16.3045, 80.4445),
    "Guntur Bus Stand": (16.3080, 80.4420),
    "Koritepadu": (16.3120, 80.4280),
    "Lakshmipuram": (16.3010, 80.4310),
    "Gujjanagundla": (16.2920, 80.4180),
    "Brindavan Gardens": (16.3100, 80.4250),
    "Pattabhipuram": (16.2980, 80.4220),
    "Pedakakani": (16.3420, 80.4950),

    # Amaravati & Vijayawada
    "Mangalagiri Bypass": (16.4300, 80.5500),
    "Amaravati Capital": (16.5417, 80.5150),
    "Vijayawada Junction": (16.5062, 80.6480),
    "Benz Circle": (16.4980, 80.6550),
}


def resolve_geographic_place_name(
    lat: float,
    lon: float,
    road_hint: str = "",
    instruction_hint: str = "",
    origin_label: str = "",
    dest_label: str = "",
    progress_frac: float = 0.5,
    seen_labels: Optional[Set[str]] = None
) -> Tuple[str, str]:
    """
    Resolves a real, human-understandable place/locality name for any waypoint on the route.
    NEVER returns 'Corridor', 'Waypoint Corridor', or generic placeholders.
    Returns (place_label, road_or_area_description).
    """
    seen = seen_labels or set()
    generic_words = {
        "corridor", "local corridor", "waypoint corridor", "connected road",
        "connecting road", "unnamed road", "service road", "road", "link road",
        "link", "route corridor", "bypass link", "corridor checkpoint",
        "connected", "connecting", "unnamed", "service", "route", "bypass",
        "street", "avenue", "feeder", "lane", "drive", "way", "highway",
        "main", "local", "central", "transit"
    }

    # 1. Try to extract a genuine town / locality from the road name (e.g. Tenali - Narakoduru Road)
    cand_name = ""
    if road_hint:
        clean_hint = re.sub(r'^(onto|on|turn onto|turn right onto|turn left onto|head out on|follow)\s+', '', road_hint, flags=re.IGNORECASE).strip()
        # Strictly reject any hint that contains 'corridor'
        if "corridor" not in clean_hint.lower():
            if "-" in clean_hint:
                parts = [p.strip() for p in clean_hint.split("-") if p.strip()]
                for p in parts:
                    sub = re.sub(r'\b(Road|Highway|Bypass|Street|Avenue|Link|Feeder)\b', '', p, flags=re.IGNORECASE).strip()
                    if sub and sub.lower() not in generic_words and len(sub) > 2:
                        if sub.lower() not in origin_label.lower() and sub.lower() not in dest_label.lower():
                            cand_name = sub.title()
                            break
            else:
                sub = re.sub(r'\b(Road|Highway|Bypass|Street|Avenue|Link|Feeder)\b', '', clean_hint, flags=re.IGNORECASE).strip()
                if sub and sub.lower() not in generic_words and len(sub) > 2:
                    if sub.lower() not in origin_label.lower() and sub.lower() not in dest_label.lower():
                        cand_name = sub.title()

    if cand_name and cand_name.lower() not in [s.lower() for s in seen]:
        return cand_name, f"{cand_name} Road"

    # 2. Match closest landmark from REGIONAL_GEOGRAPHIC_LOCALITIES
    sorted_localities = sorted(
        REGIONAL_GEOGRAPHIC_LOCALITIES.items(),
        key=lambda item: haversine_distance_km((lat, lon), item[1])
    )

    clean_orig_low = origin_label.lower()
    clean_dest_low = dest_label.lower()

    for loc_name, loc_coords in sorted_localities:
        d_km = haversine_distance_km((lat, lon), loc_coords)
        if d_km <= 4.2:
            loc_key = loc_name.lower()
            # Don't repeat origin or destination if not at end points
            if (loc_key in clean_orig_low or clean_orig_low in loc_key) and progress_frac > 0.15:
                continue
            if (loc_key in clean_dest_low or clean_dest_low in loc_key) and progress_frac < 0.85:
                continue
            if loc_key not in [s.lower() for s in seen]:
                return loc_name, f"{loc_name} Area Road"

    # 3. If within 6.5 km of any known locality, use qualified locality name
    for loc_name, loc_coords in sorted_localities:
        d_km = haversine_distance_km((lat, lon), loc_coords)
        if d_km <= 6.5:
            loc_key = loc_name.lower()
            if loc_key not in [s.lower() for s in seen] and loc_key not in clean_dest_low and loc_key not in clean_orig_low:
                return f"{loc_name} Sector", f"{loc_name} Approach Road"

    # 4. Global Geographic Sector fallback (if outside regional network, e.g. international route)
    if progress_frac < 0.30:
        base = f"{origin_label} Crossing" if "point" not in clean_orig_low else "Transit Crossing"
    elif progress_frac <= 0.70:
        base = "Mid-Route Junction"
    else:
        base = f"{dest_label} Gate" if "point" not in clean_dest_low else "Destination Approach"

    return base, f"{base} Main Road"


def extract_journey_game_milestones(
    origin_label: str,
    dest_label: str,
    polyline: List[Tuple[float, float]],
    steps: Optional[List[Dict[str, Any]]] = None,
    total_distance_km: float = 0.0
) -> List[JourneyMilestone]:
    """
    Dynamically extracts a sequence of 4 to 8 game milestones with REAL geographic place names.
    Completely eliminates generic placeholders like 'Corridor' or 'Waypoint Corridor'.
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
        voice_announcement=f"The virtual boy is standing at the start point: {clean_orig}. Starting journey on Google Maps!",
        icon="🚩"
    ))

    # Track seen names to ensure all intermediate milestones are distinct and informative
    seen_names: Set[str] = {clean_orig.lower(), clean_dest.lower()}
    extracted_stops: List[Dict[str, Any]] = []

    # Extract intermediate waypoints from steps if available
    if steps and len(steps) >= 2:
        cum_dist = 0.0

        for s in steps:
            s_dist_m = s.get("distance_m", 0.0)
            s_dist_km = s_dist_m / 1000.0
            cum_dist += s_dist_km

            # Only sample if significant leg distance and not right at the destination
            if s_dist_km >= 0.25 and (0.04 * total_distance_km) <= cum_dist <= (0.96 * total_distance_km):
                # Calculate coordinates along polyline for this distance
                p_idx = int((cum_dist / max(total_distance_km, 0.1)) * (p_count - 1)) if p_count > 0 else 0
                p_idx = max(0, min(p_idx, p_count - 1))
                pt = polyline[p_idx] if p_count > 0 else p_start

                frac = cum_dist / max(total_distance_km, 0.1)
                place_name, road_desc = resolve_geographic_place_name(
                    lat=pt[0],
                    lon=pt[1],
                    road_hint=s.get("road", ""),
                    instruction_hint=s.get("instruction", ""),
                    origin_label=clean_orig,
                    dest_label=clean_dest,
                    progress_frac=frac,
                    seen_labels=seen_names
                )

                if place_name.lower() not in seen_names:
                    seen_names.add(place_name.lower())
                    extracted_stops.append({
                        "name": place_name,
                        "road": road_desc,
                        "dist_km": round(cum_dist, 1),
                        "leg_km": round(s_dist_km, 1),
                        "lat": pt[0],
                        "lon": pt[1]
                    })

    # If steps didn't yield at least 2 distinct intermediate stops, sample from polyline
    target_intermediate = min(4, max(2, p_count - 2)) if p_count >= 4 else 2
    if len(extracted_stops) < target_intermediate and p_count >= 3:
        needed = target_intermediate - len(extracted_stops)
        fractions = [i / (needed + 1) for i in range(1, needed + 1)]
        for frac in fractions:
            dist_at_pt = total_distance_km * frac
            idx = int(frac * (p_count - 1))
            idx = max(0, min(idx, p_count - 1))
            pt = polyline[idx]

            place_name, road_desc = resolve_geographic_place_name(
                lat=pt[0],
                lon=pt[1],
                road_hint="",
                instruction_hint="",
                origin_label=clean_orig,
                dest_label=clean_dest,
                progress_frac=frac,
                seen_labels=seen_names
            )

            if place_name.lower() not in seen_names:
                seen_names.add(place_name.lower())
                extracted_stops.append({
                    "name": place_name,
                    "road": road_desc,
                    "dist_km": round(dist_at_pt, 1),
                    "leg_km": round(total_distance_km / (needed + 1), 1),
                    "lat": pt[0],
                    "lon": pt[1]
                })

    # Sort extracted intermediate stops by distance from start
    extracted_stops.sort(key=lambda x: x.get("dist_km", 0.0))
    selected_stops = extracted_stops[:4]

    # Map stops into JourneyMilestones
    prev_d = 0.0
    for idx, stop in enumerate(selected_stops, start=1):
        s_name = stop["name"]
        d_from_start = round(stop.get("dist_km", prev_d + 1.0), 1)
        leg = round(max(0.1, d_from_start - prev_d), 1)
        prev_d = d_from_start

        s_lat = stop.get("lat", p_start[0])
        s_lon = stop.get("lon", p_start[1])

        milestones.append(JourneyMilestone(
            index=idx,
            milestone_type="WAYPOINT",
            label=s_name,
            action_title=f"Crossed {s_name}",
            road_or_area=stop.get("road", f"{s_name} Transit Road"),
            lat=s_lat,
            lon=s_lon,
            distance_from_start_km=d_from_start,
            distance_leg_km=leg,
            voice_announcement=f"He crossed Stop {idx}: {s_name}! Checkmark recorded on the process banner. The virtual boy is now running towards the next stop.",
            icon="🛣️"
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
        voice_announcement=f"He reached the final destination: {clean_dest}! All stops checkmarked on the Google Map process banner.",
        icon="🏆"
    ))

    return milestones


def create_return_milestones(
    forward_milestones: List[JourneyMilestone]
) -> List[JourneyMilestone]:
    """
    Transforms forward milestones (Start -> Waypoints -> Goal) into an identical
    return journey sequence (Goal -> Waypoints in reverse -> Start) so that the
    journey from Goal to Start is displayed, tracked, and navigated in the exact same way.
    """
    if not forward_milestones:
        return []

    if len(forward_milestones) == 1:
        return forward_milestones

    total_dist_km = forward_milestones[-1].distance_from_start_km
    clean_goal = forward_milestones[-1].label
    clean_orig = forward_milestones[0].label

    return_milestones: List[JourneyMilestone] = []

    # Milestone 0: Start of Return Journey (Standing at the Goal Destination)
    return_milestones.append(JourneyMilestone(
        index=0,
        milestone_type="START",
        label=clean_goal,
        action_title=f"Started return from {clean_goal}",
        road_or_area=f"Return Departure Point ({clean_goal})",
        lat=forward_milestones[-1].lat,
        lon=forward_milestones[-1].lon,
        distance_from_start_km=0.0,
        distance_leg_km=0.0,
        voice_announcement=f"The virtual boy is standing at the return start point: {clean_goal}. Starting return journey back to {clean_orig} in the same way!",
        icon="🚩"
    ))

    # Intermediate stops in reverse order (from second to last down to 1)
    cum_return_dist = 0.0
    intermediate_forward = forward_milestones[1:-1]
    intermediate_reversed = list(reversed(intermediate_forward))

    for idx, f_m in enumerate(intermediate_reversed, start=1):
        leg = f_m.distance_leg_km
        cum_return_dist += leg
        return_milestones.append(JourneyMilestone(
            index=idx,
            milestone_type="WAYPOINT",
            label=f_m.label,
            action_title=f"Crossed {f_m.label}",
            road_or_area=f_m.road_or_area,
            lat=f_m.lat,
            lon=f_m.lon,
            distance_from_start_km=round(cum_return_dist, 1),
            distance_leg_km=round(max(0.1, leg), 1),
            voice_announcement=f"He crossed Stop {idx}: {f_m.label} on the return journey! Checkmark recorded on the process banner. The virtual boy is now running towards the next stop.",
            icon="🛣️"
        ))

    # Final Milestone of Return Journey: Reached Initial Start Point
    final_idx = len(return_milestones)
    final_leg = round(max(0.1, total_dist_km - cum_return_dist), 1)
    return_milestones.append(JourneyMilestone(
        index=final_idx,
        milestone_type="DESTINATION",
        label=clean_orig,
        action_title=f"Reached initial {clean_orig}",
        road_or_area=f"Initial Departure Point ({clean_orig})",
        lat=forward_milestones[0].lat,
        lon=forward_milestones[0].lon,
        distance_from_start_km=round(total_dist_km, 1),
        distance_leg_km=final_leg,
        voice_announcement=f"He reached the initial destination: {clean_orig}! All return stops checkmarked on the Google Map process banner. Safe return completed!",
        icon="🏆"
    ))

    return return_milestones


def detect_crossed_milestones(
    user_coords: Tuple[float, float],
    current_step: int,
    milestones: List[JourneyMilestone],
    polyline: Optional[List[Tuple[float, float]]] = None
) -> Tuple[int, Optional[JourneyMilestone], str]:
    """
    Evaluates real-time live satellite GPS coordinates against the journey milestones.
    Detects:
    1. At what place the user currently is located.
    2. Whether the user has crossed any milestone stops.
    Returns:
    (new_step_idx, newly_crossed_milestone, current_place_summary)
    """
    if not milestones:
        return (0, None, "Starting Point")

    u_lat, u_lon = user_coords
    current_step = max(0, min(current_step, len(milestones) - 1))

    # Calculate user distance along polyline
    traveled_km = 0.0
    if polyline and len(polyline) >= 2:
        min_d = float('inf')
        closest_idx = 0
        for idx, pt in enumerate(polyline):
            d = haversine_distance_km((u_lat, u_lon), pt)
            if d < min_d:
                min_d = d
                closest_idx = idx

        for i in range(closest_idx):
            traveled_km += haversine_distance_km(polyline[i], polyline[i+1])
    else:
        traveled_km = haversine_distance_km((milestones[0].lat, milestones[0].lon), (u_lat, u_lon))

    highest_reached_idx = current_step
    newly_crossed = None

    # Guard against premature advancement when user is standing at the origin point
    dist_from_origin_km = haversine_distance_km((milestones[0].lat, milestones[0].lon), (u_lat, u_lon))

    for idx, m in enumerate(milestones):
        if idx <= current_step:
            continue
        direct_dist_km = haversine_distance_km((u_lat, u_lon), (m.lat, m.lon))

        # Milestone ahead (idx > 0) can only be reached if user has moved away from start point
        if dist_from_origin_km < 0.06 and traveled_km < 0.06:
            continue

        has_progressed_to_milestone = (traveled_km >= max(0.08, m.distance_from_start_km - 0.15))
        is_at_waypoint_in_transit = (direct_dist_km <= 0.08) and (traveled_km >= 0.05)

        if has_progressed_to_milestone or is_at_waypoint_in_transit:
            highest_reached_idx = idx
            newly_crossed = m

    cur_m = milestones[highest_reached_idx]
    if highest_reached_idx == 0:
        place_summary = f"At {cur_m.label} (Starting Point)"
    elif highest_reached_idx >= len(milestones) - 1:
        place_summary = f"Arrived at Destination: {cur_m.label}"
    else:
        next_m = milestones[min(highest_reached_idx + 1, len(milestones) - 1)]
        place_summary = f"Crossed {cur_m.label} • Heading towards {next_m.label}"

    return (highest_reached_idx, newly_crossed, place_summary)


def build_game_journey_html(
    milestones: List[JourneyMilestone],
    current_step: int = 0,
    traveler_avatar: str = "car",
    auto_voice: bool = True,
    detected_place: str = "",
    is_moving: bool = False,
    user_speed_kmh: float = 0.0,
    polyline: Optional[List[Tuple[float, float]]] = None,
    auto_drive: bool = True
) -> str:
    """
    Renders an interactive, visually stunning Game Journey Stepper HUD with:
    - Real-Time Autonomous Satellite Motion Engine (zero manual work required).
    - Synchronized AI Voice Assistant:
        1. "Connecting to the live satellite GPS..."
        2. Once connected: tick mark on GPS connection.
        3. Upon crossing Narakoduru / stops: "The user has crossed Narakoduru." (car hops forward).
        4. Destination reached: "The user has reached the destination: Guntur City Center."
    - Mario-style progression track with checkmarks on crossed stops.
    - Live synchronization with the Leaflet satellite map above.
    """
    if not milestones:
        return ""

    current_step = max(0, min(current_step, len(milestones) - 1))
    total_steps = len(milestones)
    progress_pct = int((current_step / max(1, total_steps - 1)) * 100)

    # Avatar & Mode Speed Configuration
    avatar_key = str(traveler_avatar).lower()
    if avatar_key == "boy":
        avatar_icon = "👦"
        avatar_label = "Small Virtual Boy Companion"
        mode_speed_kmh = 4.8
        step_duration_ms = 4800
        active_tag_label = "VIRTUAL BOY HERE 👦"
    elif "walk" in avatar_key:
        avatar_icon = "🚶‍♂️"
        avatar_label = "Virtual Boy Walking"
        mode_speed_kmh = 4.8
        step_duration_ms = 6200
        active_tag_label = "WALKING HERE 🚶‍♂️"
    elif "bicycle" in avatar_key or "cycle" in avatar_key:
        avatar_icon = "🚴"
        avatar_label = "Virtual Cyclist"
        mode_speed_kmh = 16.0
        step_duration_ms = 4400
        active_tag_label = "CYCLING HERE 🚴"
    elif "bike" in avatar_key or "motorcycle" in avatar_key:
        avatar_icon = "🏍️"
        avatar_label = "Virtual Motorcyclist"
        mode_speed_kmh = 45.0
        step_duration_ms = 2800
        active_tag_label = "RIDING HERE 🏍️"
    elif "tractor" in avatar_key:
        avatar_icon = "🚜"
        avatar_label = "Virtual Tractor Operator"
        mode_speed_kmh = 20.0
        step_duration_ms = 4500
        active_tag_label = "TRACTOR HERE 🚜"
    elif "truck" in avatar_key:
        avatar_icon = "🚚"
        avatar_label = "Virtual Truck Transport"
        mode_speed_kmh = 42.0
        step_duration_ms = 3000
        active_tag_label = "HAULING HERE 🚚"
    elif "bus" in avatar_key:
        avatar_icon = "🚌"
        avatar_label = "Virtual Bus Transit"
        mode_speed_kmh = 38.0
        step_duration_ms = 3200
        active_tag_label = "TRANSIT HERE 🚌"
    elif "car" in avatar_key or "drive" in avatar_key:
        avatar_icon = "🚗"
        avatar_label = "Virtual Car Companion"
        mode_speed_kmh = 55.0
        step_duration_ms = 2400
        active_tag_label = "DRIVING HERE 🚗"
    else:
        avatar_icon = "🏃‍♂️"
        avatar_label = "Virtual Runner Companion"
        mode_speed_kmh = 9.5
        step_duration_ms = 3800
        active_tag_label = "RUNNING HERE 🏃‍♂️"

    effective_speed_kmh = round(user_speed_kmh if user_speed_kmh > 0.0 else mode_speed_kmh, 1)

    # Generate symmetrical return milestones from Goal -> Start
    return_milestones = create_return_milestones(milestones)

    # Helper to serialize milestones list
    def serialize_milestones_list(m_list: List[JourneyMilestone]) -> List[Dict[str, Any]]:
        return [{
            "index": m.index,
            "type": m.milestone_type,
            "label": m.label,
            "action_title": m.action_title,
            "road": m.road_or_area,
            "lat": m.lat,
            "lon": m.lon,
            "distance_km": m.distance_from_start_km,
            "leg_km": m.distance_leg_km,
            "voice": m.voice_announcement
        } for m in m_list]

    forward_json = json.dumps(serialize_milestones_list(milestones))
    return_json = json.dumps(serialize_milestones_list(return_milestones))

    # Fallback or supplied polylines
    poly_pts = polyline if polyline else [[m.lat, m.lon] for m in milestones]
    poly_forward_json = json.dumps(poly_pts)
    poly_return_json = json.dumps(list(reversed(poly_pts)))

    orig_clean = milestones[0].label
    dest_clean = milestones[-1].label

    # Initial HTML node generation for initial forward render
    nodes_html = []
    for m in milestones:
        idx = m.index
        if idx < current_step:
            state_class = "node-completed"
            badge = "✅"
            halo = "border: 2px solid #10b981; background: #064e3b; color: #34d399; box-shadow: 0 0 14px rgba(16, 185, 129, 0.45);"
            tag_text = "CHECKED ✅"
            tag_style = "display: block; background: #059669; color: #ffffff;"
        elif idx == current_step:
            state_class = "node-active"
            badge = avatar_icon
            halo = "border: 3px solid #38bdf8; background: #0369a1; color: #ffffff; box-shadow: 0 0 22px #38bdf8; animation: runnerStride 0.75s infinite alternate ease-in-out;"
            tag_text = "ARRIVED 🏆" if idx == total_steps - 1 else active_tag_label
            tag_style = "display: block; background: " + ("#10b981" if idx == total_steps - 1 else "#38bdf8") + "; color: " + ("#ffffff" if idx == total_steps - 1 else "#02132b") + ";"
        else:
            state_class = "node-upcoming"
            badge = str(idx + 1)
            halo = "border: 2px dashed rgba(255,255,255,0.25); background: rgba(30,41,59,0.7); color: #94a3b8;"
            tag_text = "UPCOMING"
            tag_style = "display: none; background: rgba(148,163,184,0.3); color: #cbd5e1;"

        nodes_html.append(f"""
        <div id='node-item-{idx}' class='game-step-item {state_class}' style='display: flex; flex-direction: column; align-items: center; text-align: center; min-width: 105px; flex: 1;'>
            <div style='position: relative; margin-bottom: 8px;'>
                <div id='node-halo-{idx}' style='width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; {halo}'>
                    <span id='node-badge-{idx}'>{badge}</span>
                </div>
                <div id='node-tag-{idx}' style='position: absolute; top: -18px; left: 50%; transform: translateX(-50%); font-size: 9px; font-weight: 900; padding: 2px 6px; border-radius: 999px; white-space: nowrap; box-shadow: 0 0 8px rgba(56,189,248,0.5); {tag_style}'>{tag_text}</div>
            </div>
            <div id='node-label-{idx}' style='font-size: 0.78rem; font-weight: 700; color: {"#38bdf8" if idx == current_step else ("#34d399" if idx < current_step else "#94a3b8")}; max-width: 105px; word-break: break-word; line-height: 1.2;'>
                {m.label}
            </div>
            <div id='node-sub-{idx}' style='font-size: 0.65rem; color: #64748b; margin-top: 3px;'>
                {m.action_title.split()[0]} ({m.distance_from_start_km:.1f} km)
            </div>
        </div>
        """)

    all_nodes_rendered = "".join(nodes_html)

    return f"""
    <style>
    @keyframes runnerStride {{
        0% {{ transform: translateY(0px) scale(1) rotate(-4deg); }}
        50% {{ transform: translateY(-7px) scale(1.12) rotate(4deg); }}
        100% {{ transform: translateY(0px) scale(1) rotate(-4deg); }}
    }}
    @keyframes checkmarkPop {{
        0% {{ transform: scale(0.6); opacity: 0.5; }}
        70% {{ transform: scale(1.22); }}
        100% {{ transform: scale(1.0); opacity: 1; }}
    }}
    @keyframes victoryPulse {{
        0% {{ box-shadow: 0 0 10px rgba(16, 185, 129, 0.3); }}
        100% {{ box-shadow: 0 0 28px rgba(16, 185, 129, 0.7); }}
    }}
    @keyframes pulseGps {{
        0% {{ opacity: 0.4; }}
        50% {{ opacity: 1; }}
        100% {{ opacity: 0.4; }}
    }}
    .game-board-container {{
        background: linear-gradient(135deg, rgba(8, 15, 30, 0.94) 0%, rgba(15, 23, 42, 0.90) 100%);
        border: 1.5px solid rgba(56, 189, 248, 0.35);
        border-radius: 14px;
        padding: 16px 20px;
        margin: 10px 0;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6), 0 0 20px rgba(56, 189, 248, 0.12);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    .btn-dir-pill {{
        background: transparent;
        color: #94a3b8;
        border: none;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.70rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.22s ease;
    }}
    .btn-dir-pill:hover {{
        color: #ffffff;
        background: rgba(56, 189, 248, 0.15);
    }}
    .btn-dir-pill.active-dir {{
        background: #0284c7;
        color: #ffffff;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.45);
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
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 0 10px #38bdf8;
    }}
    .game-step-item {{
        position: relative;
        z-index: 1;
    }}
    .btn-hud-ctrl {{
        background: rgba(15, 23, 42, 0.8);
        color: #f1f5f9;
        border: 1px solid rgba(56, 189, 248, 0.35);
        padding: 6px 14px;
        border-radius: 6px;
        font-size: 0.74rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.2s ease;
    }}
    .btn-hud-ctrl:hover {{
        background: rgba(56, 189, 248, 0.2);
        border-color: #38bdf8;
    }}
    </style>

    <div class='game-board-container'>
        <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px;'>
            <div style='display: flex; align-items: center; gap: 10px;'>
                <span id='hud-header-icon' style='font-size: 1.5rem; animation: runnerStride 0.75s infinite alternate ease-in-out;'>{avatar_icon}</span>
                <div>
                    <div style='display: flex; align-items: center; gap: 8px; flex-wrap: wrap;'>
                        <div style='font-size: 0.95rem; font-weight: 800; color: #ffffff; letter-spacing: 0.02em;'>
                            {avatar_icon} VIRTUAL RUNNER & ROUTE PROCESS BANNER • <span style='color:#38bdf8;'>{avatar_label}</span>
                        </div>
                        <!-- Goal to Start Symmetrical Direction Switcher -->
                        <div style='display: inline-flex; align-items: center; gap: 3px; background: rgba(15, 23, 42, 0.9); padding: 2px 4px; border-radius: 999px; border: 1px solid rgba(56, 189, 248, 0.35);'>
                            <button id='btn-dir-forward' class='btn-dir-pill active-dir' onclick='setJourneyDirection("FORWARD")' title='Start to Goal Outbound Route'>
                                ➡️ Start ➔ Goal ({orig_clean} ➔ {dest_clean})
                            </button>
                            <button id='btn-dir-return' class='btn-dir-pill' onclick='setJourneyDirection("RETURN")' title='Goal to Start Return Trip in the Same Way'>
                                ⬅️ Goal ➔ Start ({dest_clean} ➔ {orig_clean})
                            </button>
                        </div>
                    </div>
                    <div id='hud-checkpoint-title' style='font-size: 0.74rem; color: #94a3b8; margin-top: 2px;'>
                        TRAVEL JOURNEY GAME PROGRESSION • Checkpoint <b><span id='hud-step-num'>{current_step + 1}</span> of <span id='hud-total-steps'>{total_steps}</span></b> • <span id='hud-action-title'>{milestones[current_step].action_title}</span>
                    </div>
                </div>
            </div>
                <div id='hud-progress-meter' style='background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.35); padding: 4px 12px; border-radius: 999px; font-size: 0.75rem; font-weight: 800; color: #38bdf8;'>
                    ⚡ <span id='hud-progress-pct'>{progress_pct}</span>% Journey Progress
                </div>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <button id='btn-sim-traffic' class='btn-hud-ctrl btn-traffic' style='background: rgba(239, 68, 68, 0.22); border-color: #ef4444; color: #fca5a5; font-weight: 800; padding: 6px 14px; border-radius: 6px; cursor: pointer;' onclick='simulateTrafficStop()' title='Traffic Stop — Stop virtual vehicle & companion (0.0 km/h stationary)'>
                        🛑 Traffic Stop (0 km/h)
                    </button>
                    <button id='btn-sim-resume' class='btn-hud-ctrl btn-moving' style='background: rgba(16, 185, 129, 0.22); border-color: #10b981; color: #6ee7b7; font-weight: 800; padding: 6px 14px; border-radius: 6px; cursor: pointer;' onclick='simulateUserMoving()' title='Move in Parallel — Manually start or resume movement'>
                        🟢 Move in Parallel
                    </button>
                    <!-- simulateCrossNextStop / Cross Next Stop internal diagnostic helper -->
                </div>
            </div>
        </div>

        <!-- Real-Time Satellite Motion & Place Detection Banner with Checkmark Progress -->
        <div style='background: rgba(16, 185, 129, 0.10); border: 1px solid rgba(16, 185, 129, 0.28); border-radius: 8px; padding: 7px 14px; margin-top: 8px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 6px;'>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span id='satellite-spin-icon' style='font-size: 1.1rem;'>{avatar_icon}</span>
                <span style='color: #a7f3d0; font-size: 0.78rem; font-weight: 700;'>
                    Parallel Virtual Companion & Process Status: <b id='satellite-detection-text' style='color: #ffffff;'>Stationary at start: {orig_clean} • Press Move in Parallel to start</b>
                </span>
            </div>
            <div style='font-size: 0.72rem; color: #38bdf8; font-weight: 700; display: flex; align-items: center; gap: 6px;'>
                <span id='satellite-motion-telemetry' style='color: #38bdf8;'>● 0.0 KM/H • READY TO START (STATIONARY)</span>
            </div>
        </div>

        <!-- Stepper Road Track -->
        <div class='game-track-line'>
            <div id='game-track-fill' class='game-track-fill'></div>
            <div id='game-track-nodes' style='display: flex; width: 100%; justify-content: space-between; position: relative; z-index: 1;'>
                {all_nodes_rendered}
            </div>
        </div>

        <!-- Active Checkpoint Voice Briefing -->
        <div style='background: rgba(0, 0, 0, 0.35); border-left: 4px solid #38bdf8; border-radius: 6px; padding: 10px 14px; margin-top: 10px; display: flex; align-items: center; justify-content: space-between;'>
            <div>
                <div style='font-size: 0.70rem; color: #38bdf8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;'>
                    Current Checkpoint Status & Spoken Guidance
                </div>
                <div id='hud-voice-announcement' style='font-size: 0.84rem; color: #f1f5f9; font-weight: 600; margin-top: 2px;'>
                    "{milestones[current_step].voice_announcement}"
                </div>
            </div>
            <div style='font-size: 0.72rem; color: #94a3b8; text-align: right;'>
                Leg: <b><span id='hud-leg-km'>{milestones[current_step].distance_leg_km:.1f}</span> km</b>
            </div>
        </div>

        <!-- Victory Banner on Arrival -->
        <div id='game-victory-banner' style='display: none; background: linear-gradient(135deg, rgba(16, 185, 129, 0.3) 0%, rgba(6, 78, 59, 0.85) 100%); border: 2px solid #10b981; border-radius: 12px; padding: 12px 18px; margin-top: 14px; text-align: center; box-shadow: 0 0 25px rgba(16, 185, 129, 0.4); animation: victoryPulse 1.5s infinite alternate;'>
            <div id='victory-banner-heading' style='font-size: 1.4rem; margin-bottom: 2px;'>🏆 LEVEL COMPLETED • DESTINATION REACHED!</div>
            <div id='victory-detail-text' style='font-size: 0.90rem; font-weight: 800; color: #ffffff;'>
                The {avatar_label} has safely reached <b>{milestones[-1].label}</b> ({milestones[-1].distance_from_start_km:.1f} km).
            </div>
            <div id='victory-sub-text' style='font-size: 0.74rem; color: #a7f3d0; margin-top: 4px;'>
                All intermediate checkpoints verified and check-marked (✅). Goal to Start return journey will start automatically in the same way.
            </div>
        </div>
    </div>

    <script>
    (function() {{
        const FORWARD_MILESTONES = {forward_json};
        const RETURN_MILESTONES = {return_json};
        const FORWARD_POLY = {poly_forward_json};
        const RETURN_POLY = {poly_return_json};

        const AVATAR_ICON = {json.dumps(avatar_icon)};
        const AVATAR_LABEL = {json.dumps(avatar_label)};
        const MODE_SPEED_KMH = {effective_speed_kmh};
        const STEP_DURATION_MS = {step_duration_ms};
        const ACTIVE_TAG_LABEL = {json.dumps(active_tag_label)};

        let currentDirection = "FORWARD"; // "FORWARD" or "RETURN"
        let activeMilestones = FORWARD_MILESTONES;
        let activePoly = FORWARD_POLY;

        let currentStep = 0;
        let isMotionPaused = false;
        let transitTimer = null;
        let isGpsLocked = false;

        function speakText(text) {{
            // Silenced: AI voice assistant removed per user request
            if ('speechSynthesis' in window) {{
                try {{ window.speechSynthesis.cancel(); }} catch(e) {{}}
            }}
            return;
        }}

        window.speakCurrentStep = function() {{
            if (currentStep >= 0 && currentStep < activeMilestones.length) {{
                const m = activeMilestones[currentStep];
                speakText(m.voice);
            }}
        }};
        window.speakGameStep = window.speakCurrentStep;

        function renderTrackNodes(stepIdx) {{
            const container = document.getElementById('game-track-nodes');
            if (!container) return;
            const total = activeMilestones.length;
            let html = '';
            for (let i = 0; i < total; i++) {{
                const m = activeMilestones[i];
                let stateClass, badge, halo, tagText, tagStyle, labelColor;
                if (i < stepIdx) {{
                    stateClass = "node-completed";
                    badge = "✅";
                    halo = "border: 2px solid #10b981; background: #064e3b; color: #34d399; box-shadow: 0 0 14px rgba(16, 185, 129, 0.45);";
                    tagText = "CHECKED ✅";
                    tagStyle = "display: block; background: #059669; color: #ffffff;";
                    labelColor = "#34d399";
                }} else if (i === stepIdx) {{
                    stateClass = "node-active";
                    badge = AVATAR_ICON;
                    halo = "border: 3px solid #38bdf8; background: #0369a1; color: #ffffff; box-shadow: 0 0 22px #38bdf8; animation: runnerStride 0.75s infinite alternate ease-in-out;";
                    const isGoal = (i === total - 1);
                    tagText = isGoal ? (currentDirection === 'RETURN' ? 'SAFE RETURN 🏆' : 'ARRIVED 🏆') : ACTIVE_TAG_LABEL;
                    tagStyle = "display: block; background: " + (isGoal ? "#10b981" : "#38bdf8") + "; color: " + (isGoal ? "#ffffff" : "#02132b") + ";";
                    labelColor = "#38bdf8";
                }} else {{
                    stateClass = "node-upcoming";
                    badge = String(i + 1);
                    halo = "border: 2px dashed rgba(255,255,255,0.25); background: rgba(30,41,59,0.7); color: #94a3b8;";
                    tagText = "UPCOMING";
                    tagStyle = "display: none; background: rgba(148,163,184,0.3); color: #cbd5e1;";
                    labelColor = "#94a3b8";
                }}

                html += `
                <div id='node-item-${{i}}' class='game-step-item ${{stateClass}}' style='display: flex; flex-direction: column; align-items: center; text-align: center; min-width: 105px; flex: 1;'>
                    <div style='position: relative; margin-bottom: 8px;'>
                        <div id='node-halo-${{i}}' style='width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; ${{halo}}'>
                            <span id='node-badge-${{i}}'>${{badge}}</span>
                        </div>
                        <div id='node-tag-${{i}}' style='position: absolute; top: -18px; left: 50%; transform: translateX(-50%); font-size: 9px; font-weight: 900; padding: 2px 6px; border-radius: 999px; white-space: nowrap; box-shadow: 0 0 8px rgba(56,189,248,0.5); ${{tagStyle}}'>${{tagText}}</div>
                    </div>
                    <div id='node-label-${{i}}' style='font-size: 0.78rem; font-weight: 700; color: ${{labelColor}}; max-width: 105px; word-break: break-word; line-height: 1.2;'>
                        ${{m.label}}
                    </div>
                    <div id='node-sub-${{i}}' style='font-size: 0.65rem; color: #64748b; margin-top: 3px;'>
                        ${{m.action_title.split(' ')[0]}} (${{m.distance_km.toFixed(1)}} km)
                    </div>
                </div>
                `;
            }}
            container.innerHTML = html;

            // Progress meter & track fill (progresses 0% -> 100% in both directions!)
            const pct = Math.round((stepIdx / Math.max(1, total - 1)) * 100);
            const fillEl = document.getElementById('game-track-fill');
            if (fillEl) {{
                fillEl.style.width = 'calc(' + pct + '% * 0.88)';
                fillEl.style.background = (currentDirection === 'RETURN')
                    ? 'linear-gradient(90deg, #0284c7 0%, #10b981 100%)'
                    : 'linear-gradient(90deg, #10b981 0%, #38bdf8 100%)';
            }}
            const pctText = document.getElementById('hud-progress-pct');
            if (pctText) pctText.innerText = pct;

            // Header titles
            const mActive = activeMilestones[stepIdx];
            const stepNumEl = document.getElementById('hud-step-num');
            if (stepNumEl) stepNumEl.innerText = (stepIdx + 1);
            const totalStepsEl = document.getElementById('hud-total-steps');
            if (totalStepsEl) totalStepsEl.innerText = total;
            const actionTitleEl = document.getElementById('hud-action-title');
            if (actionTitleEl) {{
                actionTitleEl.innerText = (currentDirection === 'RETURN')
                    ? ('[Return] ' + mActive.action_title)
                    : mActive.action_title;
            }}
            const voiceEl = document.getElementById('hud-voice-announcement');
            if (voiceEl) voiceEl.innerText = '"' + mActive.voice + '"';
            const legEl = document.getElementById('hud-leg-km');
            if (legEl) legEl.innerText = mActive.leg_km.toFixed(1);

            // Victory banner
            const victoryEl = document.getElementById('game-victory-banner');
            if (victoryEl) {{
                if (stepIdx === total - 1) {{
                    victoryEl.style.display = 'block';
                    if (currentDirection === 'RETURN') {{
                        victoryEl.style.background = 'linear-gradient(135deg, rgba(2, 132, 199, 0.4) 0%, rgba(6, 78, 59, 0.9) 100%)';
                        victoryEl.style.borderColor = '#38bdf8';
                        const headEl = document.getElementById('victory-banner-heading');
                        if (headEl) headEl.innerText = '🏆 ROUND TRIP COMPLETED • SAFELY RETURNED!';
                        const detailEl = document.getElementById('victory-detail-text');
                        if (detailEl) detailEl.innerHTML = 'The ' + AVATAR_LABEL + ' has safely returned to initial start point <b>' + mActive.label + '</b> (' + mActive.distance_km.toFixed(1) + ' km)!';
                        const subEl = document.getElementById('victory-sub-text');
                        if (subEl) subEl.innerText = 'All stops along both outbound and return paths were verified and checkmarked.';
                    }} else {{
                        victoryEl.style.background = 'linear-gradient(135deg, rgba(16, 185, 129, 0.3) 0%, rgba(6, 78, 59, 0.85) 100%)';
                        victoryEl.style.borderColor = '#10b981';
                        const headEl = document.getElementById('victory-banner-heading');
                        if (headEl) headEl.innerText = '🏆 LEVEL COMPLETED • DESTINATION REACHED!';
                        const detailEl = document.getElementById('victory-detail-text');
                        if (detailEl) detailEl.innerHTML = 'The ' + AVATAR_LABEL + ' has safely reached <b>' + mActive.label + '</b> (' + mActive.distance_km.toFixed(1) + ' km)!';
                        const subEl = document.getElementById('victory-sub-text');
                        if (subEl) subEl.innerText = 'All stops checkmarked (✅). Goal to Start return journey will start automatically in the same way.';
                    }}
                }} else {{
                    victoryEl.style.display = 'none';
                }}
            }}
        }}

        function broadcastVehiclePosition(lat, lon, label, stepIdx, speedKmh, returning) {{
            const payload = {{
                type: 'PATHFINDER_VEHICLE_UPDATE',
                lat: lat,
                lon: lon,
                label: label,
                avatarIcon: AVATAR_ICON,
                avatarLabel: AVATAR_LABEL,
                speedKmh: speedKmh || MODE_SPEED_KMH,
                isReturning: !!returning,
                step: stepIdx,
                totalSteps: activeMilestones.length,
                direction: currentDirection,
                timestamp: Date.now()
            }};
            try {{
                localStorage.setItem('pathfinder_vehicle_state', JSON.stringify(payload));
            }} catch(e) {{}}
            try {{
                window.parent.postMessage(payload, '*');
            }} catch(e) {{}}
            try {{
                if (window.BroadcastChannel) {{
                    const bc = new BroadcastChannel('pathfinder_journey_channel');
                    bc.postMessage(payload);
                    bc.close();
                }}
            }} catch(e) {{}}
        }}

        function executeMilestoneStep(idx) {{
            currentStep = idx;
            const total = activeMilestones.length;
            const m = activeMilestones[idx];

            renderTrackNodes(idx);

            const detectEl = document.getElementById('satellite-detection-text');
            const telemEl = document.getElementById('satellite-motion-telemetry');
            const isRet = (currentDirection === 'RETURN');

            if (idx === 0) {{
                if (detectEl) {{
                    detectEl.innerHTML = isRet
                        ? "At <b style='color:#ffffff;'>" + m.label + "</b> (At Return Start Point)"
                        : "At <b style='color:#ffffff;'>" + m.label + "</b> (Stationed at Current Location)";
                }}
                if (telemEl) {{
                    telemEl.innerHTML = "<span style='color:#34d399;'>🟢 " + AVATAR_ICON + " AT CURRENT LOCATION (0 km/h)</span>";
                }}
                broadcastVehiclePosition(m.lat, m.lon, m.label, idx, 0.0, isRet);
                speakText(m.voice);
            }} else if (idx < total - 1) {{
                const nextM = activeMilestones[idx + 1];
                if (detectEl) {{
                    detectEl.innerHTML = "Crossed ✅ <b>Stop " + idx + ": " + m.label + "</b> (Checkmarked) • " + AVATAR_LABEL + " running towards Stop " + (idx + 1) + ": " + nextM.label + " at " + MODE_SPEED_KMH + " km/h";
                }}
                if (telemEl) {{
                    telemEl.innerHTML = isRet
                        ? "<span style='color:#38bdf8;'>🔄 " + AVATAR_ICON + " RETURN RUNNING (" + MODE_SPEED_KMH + " km/h)</span>"
                        : "<span style='color:#38bdf8;'>🟢 " + AVATAR_ICON + " RUNNING ON GOOGLE MAPS (" + MODE_SPEED_KMH + " km/h)</span>";
                }}
                broadcastVehiclePosition(m.lat, m.lon, m.label, idx, MODE_SPEED_KMH, isRet);

                // AI voice announcement
                if (isRet) {{
                    speakText("You and the virtual companion have crossed Stop " + idx + ": " + m.label + " on the return trip! Checkmark recorded on the process banner. Moving towards Stop " + (idx + 1) + ": " + nextM.label + " at " + MODE_SPEED_KMH + " kilometers per hour.");
                }} else {{
                    speakText("You and the virtual companion have crossed Stop " + idx + ": " + m.label + "! Checkmark recorded on the process banner. Moving towards Stop " + (idx + 1) + ": " + nextM.label + " at " + MODE_SPEED_KMH + " kilometers per hour.");
                }}
            }} else {{
                // Destination reached for current direction!
                if (isRet) {{
                    if (detectEl) {{
                        detectEl.innerHTML = "🏆 Safe Return Completed: Arrived back at Initial Point: <b style='color:#10b981;'>" + m.label + "</b>! Round Trip Complete.";
                    }}
                    if (telemEl) {{
                        telemEl.innerHTML = "<span style='color:#10b981;'>🏆 ROUND TRIP COMPLETED</span>";
                    }}
                    broadcastVehiclePosition(m.lat, m.lon, "Returned to " + m.label, idx, MODE_SPEED_KMH, false);
                    speakText("Safe return completed! You and the virtual companion have safely returned to the initial departure point: " + m.label + ". Round trip journey finished successfully.");
                }} else {{
                    if (detectEl) {{
                        detectEl.innerHTML = "Reached Destination: <b style='color:#10b981;'>" + m.label + "</b> • All Stops Checkmarked ✅ • Starting Return Journey from Goal to Start in the same way...";
                    }}
                    if (telemEl) {{
                        telemEl.innerHTML = "<span style='color:#10b981;'>🏆 DESTINATION REACHED</span>";
                    }}
                    broadcastVehiclePosition(m.lat, m.lon, m.label, idx, MODE_SPEED_KMH, false);
                    speakText("You and the virtual companion have reached the final destination: " + m.label + "! All stops checkmarked on the Google Map process banner. Starting return journey from Goal to Start in the same way now.");

                    // Goal reached: await user action or return journey trigger
                    transitTimer = null;
                }}
            }}
        }}

        let isTrafficStopped = true;
        let userCurrentSpeed = 0.0;
        let movementState = 'READY'; // 'READY' | 'MOVING' | 'TRAFFIC_STOPPED' | 'ARRIVED'

        function broadcastJourneySync(action, state, stepIdx, speed) {{
            const m = activeMilestones[stepIdx] || activeMilestones[0];
            const pct = Math.round((stepIdx / Math.max(1, activeMilestones.length - 1)) * 100);
            const payload = {{
                type: 'PATHFINDER_JOURNEY_SYNC',
                action: action,
                state: state,
                step: stepIdx,
                totalSteps: activeMilestones.length,
                progressPct: pct,
                speedKmh: speed,
                direction: currentDirection,
                label: m.label,
                lat: m.lat,
                lon: m.lon,
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
            try {{ localStorage.setItem('pathfinder_journey_sync_state', JSON.stringify(payload)); }} catch(e) {{}}
        }}

        window.simulateTrafficStop = function() {{
            movementState = 'TRAFFIC_STOPPED';
            isTrafficStopped = true;
            userCurrentSpeed = 0.0;
            if (transitTimer) {{
                clearTimeout(transitTimer);
                transitTimer = null;
            }}
            const detectEl = document.getElementById('satellite-detection-text');
            const telemEl = document.getElementById('satellite-motion-telemetry');
            const m = activeMilestones[currentStep];
            if (detectEl) {{
                detectEl.innerHTML = "<span style='color:#ef4444;'>🛑 USER STOPPED (0.0 km/h)</span> • <b style='color:#fca5a5;'>Virtual Companion Paused at " + m.label + "</b> (Stationary • Press Move in Parallel to resume)";
            }}
            if (telemEl) {{
                telemEl.innerHTML = "<span style='color:#ef4444; font-weight:800;'>🛑 0.0 KM/H • STOPPED IN TRAFFIC</span>";
            }}
            // Freeze motion animations
            const runnerEl = document.getElementById('satellite-spin-icon');
            if (runnerEl) runnerEl.style.animation = 'none';
            const headIcon = document.getElementById('hud-header-icon');
            if (headIcon) headIcon.style.animation = 'none';
            const activeHalo = document.getElementById('node-halo-' + currentStep);
            if (activeHalo) activeHalo.style.animation = 'none';

            broadcastVehiclePosition(m.lat, m.lon, "Stopped at " + m.label, currentStep, 0.0, currentDirection === 'RETURN');
            broadcastJourneySync('STOP', 'TRAFFIC_STOPPED', currentStep, 0.0);
        }};

        window.simulateUserMoving = function(speed) {{
            movementState = 'MOVING';
            isTrafficStopped = false;
            userCurrentSpeed = (typeof speed === 'number' && speed > 0) ? speed : MODE_SPEED_KMH;
            const detectEl = document.getElementById('satellite-detection-text');
            const telemEl = document.getElementById('satellite-motion-telemetry');
            const m = activeMilestones[currentStep];
            const nextM = (currentStep < activeMilestones.length - 1) ? activeMilestones[currentStep + 1] : null;

            if (detectEl) {{
                if (nextM) {{
                    detectEl.innerHTML = "<span style='color:#10b981;'>🟢 USER MOVING</span> • <b style='color:#38bdf8;'>Virtual Companion running in parallel towards " + nextM.label + "</b> at " + userCurrentSpeed + " km/h";
                }} else {{
                    detectEl.innerHTML = "<span style='color:#10b981;'>🟢 USER MOVING</span> • Arrived at destination: <b>" + m.label + "</b>";
                }}
            }}
            if (telemEl) {{
                telemEl.innerHTML = "<span style='color:#34d399; font-weight:800;'>🟢 " + userCurrentSpeed + " KM/H • SYNCED IN PARALLEL</span>";
            }}
            // Restore motion animations
            const runnerEl = document.getElementById('satellite-spin-icon');
            if (runnerEl) runnerEl.style.animation = 'runnerStride 0.75s infinite alternate ease-in-out';
            const headIcon = document.getElementById('hud-header-icon');
            if (headIcon) headIcon.style.animation = 'runnerStride 0.75s infinite alternate ease-in-out';
            const activeHalo = document.getElementById('node-halo-' + currentStep);
            if (activeHalo) activeHalo.style.animation = 'runnerStride 0.75s infinite alternate ease-in-out';

            broadcastVehiclePosition(m.lat, m.lon, "Moving towards " + (nextM ? nextM.label : m.label), currentStep, userCurrentSpeed, currentDirection === 'RETURN');
            broadcastJourneySync('MOVE', 'MOVING', currentStep, userCurrentSpeed);

            // Schedule smooth milestone advance when in simulated parallel movement
            scheduleNextSimulatedTransitStep();
        }};

        window.simulateCrossNextStop = function() {{
            const total = activeMilestones.length;
            if (currentStep < total - 1) {{
                const targetIdx = currentStep + 1;
                executeMilestoneStep(targetIdx);
            }}
        }};

        function scheduleNextSimulatedTransitStep() {{
            if (transitTimer) {{
                clearTimeout(transitTimer);
                transitTimer = null;
            }}
            if (isTrafficStopped || movementState !== 'MOVING') return;

            const total = activeMilestones.length;
            if (currentStep < total - 1) {{
                transitTimer = setTimeout(function() {{
                    if (!isTrafficStopped && movementState === 'MOVING') {{
                        executeMilestoneStep(currentStep + 1);
                        if (currentStep < total - 1) {{
                            scheduleNextSimulatedTransitStep();
                        }}
                    }}
                }}, Math.max(3000, STEP_DURATION_MS));
            }}
        }}

        function scheduleNextTransitStep() {{
            scheduleNextSimulatedTransitStep();
        }}

        // =========================================================================
        // GOAL TO START DIRECTION SWITCHER (SAME WAY PROCESS BANNER)
        // =========================================================================
        window.setJourneyDirection = function(dir) {{
            if (transitTimer) {{
                clearTimeout(transitTimer);
                transitTimer = null;
            }}
            currentDirection = (dir === "RETURN") ? "RETURN" : "FORWARD";
            activeMilestones = (currentDirection === "RETURN") ? RETURN_MILESTONES : FORWARD_MILESTONES;
            activePoly = (currentDirection === "RETURN") ? RETURN_POLY : FORWARD_POLY;
            currentStep = 0;
            movementState = 'READY';
            isMotionPaused = false;
            isTrafficStopped = true;
            userCurrentSpeed = 0.0;

            // Highlight active direction pill
            const btnFwd = document.getElementById('btn-dir-forward');
            const btnRet = document.getElementById('btn-dir-return');
            if (btnFwd && btnRet) {{
                if (currentDirection === "RETURN") {{
                    btnRet.classList.add('active-dir');
                    btnFwd.classList.remove('active-dir');
                }} else {{
                    btnFwd.classList.add('active-dir');
                    btnRet.classList.remove('active-dir');
                }}
            }}

            initializeStationaryState();
        }};

        window.startReturnJourney = function() {{
            window.setJourneyDirection("RETURN");
        }};

        window.scheduleNextReturnTransitStep = function() {{
            scheduleNextTransitStep();
        }};

        window.executeReturnStep = function(targetIdx) {{
            executeMilestoneStep(targetIdx);
        }};

        window.toggleSatelliteMotion = function() {{
            if (movementState === 'MOVING' && !isTrafficStopped) {{
                window.simulateTrafficStop();
            }} else {{
                window.simulateUserMoving(MODE_SPEED_KMH);
            }}
        }};

        window.restartJourney = function() {{
            if (transitTimer) {{
                clearTimeout(transitTimer);
                transitTimer = null;
            }}
            currentStep = 0;
            movementState = 'READY';
            isTrafficStopped = true;
            userCurrentSpeed = 0.0;
            initializeStationaryState();
        }};

        function initializeStationaryState() {{
            currentStep = 0;
            movementState = 'READY';
            isTrafficStopped = true;
            userCurrentSpeed = 0.0;
            if (transitTimer) {{
                clearTimeout(transitTimer);
                transitTimer = null;
            }}

            const m0 = activeMilestones[0];
            const isRet = (currentDirection === "RETURN");
            renderTrackNodes(0);

            const detectEl = document.getElementById('satellite-detection-text');
            const telemEl = document.getElementById('satellite-motion-telemetry');
            if (detectEl) {{
                detectEl.innerHTML = isRet
                    ? "Stationary at return departure point: <b>" + m0.label + "</b> • Press Move in Parallel to start"
                    : "Stationary at start point: <b>" + m0.label + "</b> • Press Move in Parallel to start";
            }}
            if (telemEl) {{
                telemEl.innerHTML = "<span style='color:#38bdf8;'>● 0.0 KM/H • READY TO START (STATIONARY)</span>";
            }}

            // Freeze animation
            const runnerEl = document.getElementById('satellite-spin-icon');
            if (runnerEl) runnerEl.style.animation = 'none';
            const headIcon = document.getElementById('hud-header-icon');
            if (headIcon) headIcon.style.animation = 'none';

            isGpsLocked = false;
            broadcastVehiclePosition(m0.lat, m0.lon, m0.label, 0, 0.0, isRet);
            broadcastJourneySync('INIT', 'READY', 0, 0.0);
        }}

        function getDistanceKm(lat1, lon1, lat2, lon2) {{
            const R = 6371;
            const dLat = (lat2 - lat1) * Math.PI / 180;
            const dLon = (lon2 - lon1) * Math.PI / 180;
            const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                      Math.sin(dLon/2) * Math.sin(dLon/2);
            return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        }}

        // Real Live GPS Satellite Watcher
        if (navigator.geolocation && navigator.geolocation.watchPosition) {{
            try {{
                navigator.geolocation.watchPosition(function(pos) {{
                    const uLat = pos.coords.latitude;
                    const uLon = pos.coords.longitude;
                    const rawSpeed = pos.coords.speed;
                    const uSpeed = (rawSpeed != null && rawSpeed >= 0) ? parseFloat((rawSpeed * 3.6).toFixed(1)) : 0.0;

                    if (uSpeed <= 1.0) {{
                        if (!isTrafficStopped && movementState === 'MOVING') {{
                            window.simulateTrafficStop();
                        }}
                        return;
                    }} else if (isTrafficStopped && movementState === 'MOVING') {{
                        window.simulateUserMoving(uSpeed);
                    }}

                    const total = activeMilestones.length;
                    const distFromStartKm = getDistanceKm(uLat, uLon, activeMilestones[0].lat, activeMilestones[0].lon);
                    if (distFromStartKm >= 0.06 && uSpeed > 1.2) {{
                        for (let i = currentStep + 1; i < total; i++) {{
                            const dKm = getDistanceKm(uLat, uLon, activeMilestones[i].lat, activeMilestones[i].lon);
                            if (dKm <= 0.08 || (distFromStartKm >= activeMilestones[i].distance_km - 0.12 && dKm <= 0.20)) {{
                                executeMilestoneStep(i);
                                break;
                            }}
                        }}
                    }}

                    broadcastVehiclePosition(uLat, uLon, (currentStep === 0 ? activeMilestones[0].label : "Real User GPS"), currentStep, uSpeed, currentDirection === "RETURN");
                }}, function(err) {{
                    console.log("[PATHFINDER] Geolocation notice:", err.message);
                }}, {{ enableHighAccuracy: true, maximumAge: 3000, timeout: 10000 }});
            }} catch(e) {{}}
        }}

        // Cross-component listeners: listen for sync events from Vehicle Companion or external triggers
        function handleSyncEvent(data) {{
            if (!data) return;
            if (data.type === 'PATHFINDER_SENSOR_COMMAND' || data.type === 'PATHFINDER_JOURNEY_SYNC') {{
                if (data.action === 'STOP' || data.state === 'TRAFFIC_STOPPED') {{
                    if (!isTrafficStopped) window.simulateTrafficStop();
                }} else if (data.action === 'MOVE' || data.state === 'MOVING') {{
                    if (isTrafficStopped || movementState !== 'MOVING') {{
                        window.simulateUserMoving(data.speedKmh);
                    }}
                }} else if (data.action === 'CROSS_NEXT') {{
                    window.simulateCrossNextStop();
                }}
            }}
        }}

        window.addEventListener('message', function(ev) {{
            handleSyncEvent(ev.data);
        }});

        try {{
            if (window.BroadcastChannel) {{
                const journeyBc = new BroadcastChannel('pathfinder_journey_sync');
                journeyBc.onmessage = function(ev) {{ handleSyncEvent(ev.data); }};
                const sensorBc = new BroadcastChannel('pathfinder_sensor_channel');
                sensorBc.onmessage = function(ev) {{ handleSyncEvent(ev.data); }};
            }}
        }} catch(e) {{}}

        // ALWAYS INITIALIZE IN A STATIONARY STATE ON TAB OPENING
        setTimeout(initializeStationaryState, 200);
    }})();
    </script>
    """

