"""
Transit Kinematics & Creative Departure ETA Engine
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Real-Time Adaptive Navigation

Calculates physically accurate travel duration and arrival ETA based on:
1. Calibrated vehicle cruising speed profiles (Car, Bike, Bus, Truck, Tractor, Bicycle, Walk).
2. Road network distance and live GPS telemetry velocity.
3. Interactive departure offset scheduling (Now, +15m, +30m, +60m) with date rollover detection.
4. Fuel / energy consumption and carbon footprint estimates.
5. High-visibility Cyber-Cockpit glassmorphic telemetry HUD.
"""

from dataclasses import dataclass
import datetime
from typing import Any, Dict, Optional, Tuple
import zoneinfo


TIMEZONE_CATALOG: Dict[str, Dict[str, str]] = {
    "Asia/Kolkata": {"label": "🧭 IST • India (UTC+5:30)", "abbr": "IST", "utc_offset": "+05:30", "city": "India", "icon": "🧭"},
    "AUTO": {"label": "⚡ Auto-Detect Local Device Time", "abbr": "AUTO", "utc_offset": "Auto", "city": "Local Auto", "icon": "⚡"},
    "UTC": {"label": "🌐 UTC • Universal Coordinated Time", "abbr": "UTC", "utc_offset": "+00:00", "city": "Global UTC", "icon": "🌐"},
    "America/New_York": {"label": "🗽 EST • New York / US East (UTC-5)", "abbr": "EST", "utc_offset": "-05:00", "city": "New York", "icon": "🗽"},
    "America/Chicago": {"label": "🏙️ CST • Chicago / US Central (UTC-6)", "abbr": "CST", "utc_offset": "-06:00", "city": "Chicago", "icon": "🏙️"},
    "America/Los_Angeles": {"label": "🌴 PST • Los Angeles / US West (UTC-8)", "abbr": "PST", "utc_offset": "-08:00", "city": "Los Angeles", "icon": "🌴"},
    "Europe/London": {"label": "🕰️ GMT • London / UK (UTC+0)", "abbr": "GMT", "utc_offset": "+00:00", "city": "London", "icon": "🕰️"},
    "Europe/Paris": {"label": "🏛️ CET • Paris / Berlin / Europe (UTC+1)", "abbr": "CET", "utc_offset": "+01:00", "city": "Paris", "icon": "🏛️"},
    "Asia/Dubai": {"label": "🕌 GST • Dubai / Gulf (UTC+4)", "abbr": "GST", "utc_offset": "+04:00", "city": "Dubai", "icon": "🕌"},
    "Asia/Singapore": {"label": "🦁 SGT • Singapore (UTC+8)", "abbr": "SGT", "utc_offset": "+08:00", "city": "Singapore", "icon": "🦁"},
    "Asia/Tokyo": {"label": "⛩️ JST • Tokyo / Japan (UTC+9)", "abbr": "JST", "utc_offset": "+09:00", "city": "Tokyo", "icon": "⛩️"},
    "Australia/Sydney": {"label": "🦘 AEST • Sydney / Australia (UTC+10)", "abbr": "AEST", "utc_offset": "+10:00", "city": "Sydney", "icon": "🦘"},
}


def resolve_timezone(tz_key: Optional[str] = None) -> Tuple[datetime.tzinfo, str, str]:
    """
    Resolves timezone object, abbreviation and human-readable label.
    Supports 'AUTO' for user device local timezone detection,
    defaulting to Asia/Kolkata (IST) if unspecified.
    """
    key = tz_key or "Asia/Kolkata"
    if key == "AUTO":
        try:
            local_now = datetime.datetime.now().astimezone()
            tz = local_now.tzinfo
            abbr = local_now.tzname() or "LOCAL"
            return tz, abbr, "⚡ Auto-Detect Local Device Time"
        except Exception:
            pass
    if key in TIMEZONE_CATALOG:
        cfg = TIMEZONE_CATALOG[key]
        try:
            tz = zoneinfo.ZoneInfo(key)
            return tz, cfg["abbr"], cfg["label"]
        except Exception:
            pass
    try:
        tz = zoneinfo.ZoneInfo(key)
        now_probe = datetime.datetime.now(tz)
        abbr = now_probe.tzname() or "LOC"
        return tz, abbr, key
    except Exception:
        tz = zoneinfo.ZoneInfo("Asia/Kolkata")
        return tz, "IST", TIMEZONE_CATALOG["Asia/Kolkata"]["label"]


VEHICLE_KINEMATIC_PROFILES: Dict[str, Dict[str, Any]] = {
    "CAR": {
        "name": "Car / Sedan",
        "emoji": "🚗",
        "speed_kmh": 75.0,
        "speed_range": "70 - 90 km/h",
        "desc": "Automobile • Rapid Arterials & Expressways",
        "badge": "🚗 Fast Highway Transit",
        "fuel_name": "Petrol",
        "consumption_per_100km": 6.8,
        "energy_unit": "L",
        "co2_g_km": 120,
        "color": "#38bdf8",
        "bg_glow": "rgba(56, 189, 248, 0.15)",
        "border_color": "rgba(56, 189, 248, 0.45)"
    },
    "BIKE": {
        "name": "Bike / Motorcycle",
        "emoji": "🏍️",
        "speed_kmh": 60.0,
        "speed_range": "50 - 70 km/h",
        "desc": "Motorcycle / Scooter • Agile Lane Traversal",
        "badge": "🏍️ Agile Transit",
        "fuel_name": "Petrol",
        "consumption_per_100km": 2.6,
        "energy_unit": "L",
        "co2_g_km": 48,
        "color": "#f59e0b",
        "bg_glow": "rgba(245, 158, 11, 0.15)",
        "border_color": "rgba(245, 158, 11, 0.45)"
    },
    "BUS": {
        "name": "Transit Bus",
        "emoji": "🚌",
        "speed_kmh": 42.0,
        "speed_range": "35 - 50 km/h",
        "desc": "Transit Bus • Wide Corridor & Commercial Arterials",
        "badge": "🚌 Public Transit Corridor",
        "fuel_name": "Diesel",
        "consumption_per_100km": 1.4,  # Per passenger equivalent
        "energy_unit": "L (shared)",
        "co2_g_km": 32,
        "color": "#a855f7",
        "bg_glow": "rgba(168, 85, 247, 0.15)",
        "border_color": "rgba(168, 85, 247, 0.45)"
    },
    "TRUCK": {
        "name": "Heavy Truck",
        "emoji": "🚚",
        "speed_kmh": 50.0,
        "speed_range": "40 - 60 km/h",
        "desc": "Heavy Commercial • Industrial Bypass & Broad Highways",
        "badge": "🚚 Heavy Transport",
        "fuel_name": "Diesel",
        "consumption_per_100km": 24.5,
        "energy_unit": "L",
        "co2_g_km": 380,
        "color": "#f97316",
        "bg_glow": "rgba(249, 115, 22, 0.15)",
        "border_color": "rgba(249, 115, 22, 0.45)"
    },
    "TRACTOR": {
        "name": "Agricultural Tractor",
        "emoji": "🚜",
        "speed_kmh": 22.0,
        "speed_range": "18 - 25 km/h",
        "desc": "Rural & Agricultural • Secondary Rural Links & Bunds",
        "badge": "🚜 Agro Rural Transit",
        "fuel_name": "Diesel",
        "consumption_per_100km": 13.0,
        "energy_unit": "L",
        "co2_g_km": 210,
        "color": "#eab308",
        "bg_glow": "rgba(234, 179, 8, 0.15)",
        "border_color": "rgba(234, 179, 8, 0.45)"
    },
    "BICYCLE": {
        "name": "Pedal Bicycle",
        "emoji": "🚴",
        "speed_kmh": 16.0,
        "speed_range": "14 - 20 km/h",
        "desc": "Bicycle • Step-Free Local Paths & Green Corridors",
        "badge": "🚴 Eco Cycleway",
        "fuel_name": "Human Caloric Burn",
        "consumption_per_100km": 2200.0,
        "energy_unit": "kcal",
        "co2_g_km": 0,
        "color": "#10b981",
        "bg_glow": "rgba(16, 185, 129, 0.15)",
        "border_color": "rgba(16, 185, 129, 0.45)"
    },
    "WALK": {
        "name": "Pedestrian Walkway",
        "emoji": "🚶",
        "speed_kmh": 4.8,
        "speed_range": "4.2 - 5.5 km/h",
        "desc": "Pedestrian • Safe Walkways, Sidewalks & Step-Free Crossings",
        "badge": "🚶 Pedestrian Walkway",
        "fuel_name": "Active Walking Energy",
        "consumption_per_100km": 3100.0,
        "energy_unit": "kcal",
        "co2_g_km": 0,
        "color": "#ec4899",
        "bg_glow": "rgba(236, 72, 153, 0.15)",
        "border_color": "rgba(236, 72, 153, 0.45)"
    }
}


@dataclass
class TransitKinematics:
    mode_key: str
    vehicle_name: str
    vehicle_emoji: str
    speed_kmh: float
    speed_range_str: str
    distance_km: float
    distance_formatted: str
    duration_minutes: float
    duration_formatted: str
    duration_verbose: str
    departure_offset_minutes: int
    departure_time_str: str
    departure_pill_label: str
    eta_time_str: str
    eta_badge_str: str
    eta_day_offset_str: str
    energy_estimate_str: str
    co2_str: str
    profile: Dict[str, Any]
    timezone_name: str = "Asia/Kolkata"
    timezone_abbr: str = "IST"
    timezone_label: str = "🧭 IST • India (UTC+5:30)"


def calculate_transit_kinematics(
    mode_key: str,
    distance_km: float,
    engine_duration_minutes: float = 0.0,
    departure_offset_minutes: int = 0,
    now_dt: Optional[datetime.datetime] = None,
    distance_unit: str = "km",
    live_speed_kmh: float = 0.0,
    timezone_name: str = "Asia/Kolkata"
) -> TransitKinematics:
    """
    Calculates accurate transit kinematics considering the active vehicle and speed.
    """
    clean_key = mode_key.upper().strip()
    if clean_key not in VEHICLE_KINEMATIC_PROFILES:
        for k in VEHICLE_KINEMATIC_PROFILES:
            if k in clean_key:
                clean_key = k
                break
        else:
            clean_key = "CAR"

    profile = VEHICLE_KINEMATIC_PROFILES[clean_key]
    calibrated_speed = profile["speed_kmh"]

    # Calculate accurate duration
    # If the user is driving a CAR and engine has real OSRM speed, check consistency:
    if clean_key == "CAR" and engine_duration_minutes > 0 and distance_km > 0:
        eff_speed = distance_km / (engine_duration_minutes / 60.0)
        if 20.0 <= eff_speed <= 130.0:
            active_speed = round(eff_speed, 1)
            active_dur_mins = engine_duration_minutes
        else:
            active_speed = calibrated_speed
            active_dur_mins = (distance_km / calibrated_speed) * 60.0
    else:
        # Compute exact vehicle speed duration
        active_speed = calibrated_speed
        active_dur_mins = (distance_km / max(calibrated_speed, 1.0)) * 60.0

    # If live GPS velocity is substantial and active, reflect live velocity in display
    if live_speed_kmh > 2.0:
        active_speed = round(live_speed_kmh, 1)

    # Format Duration
    total_mins = int(round(active_dur_mins))
    days = total_mins // (24 * 60)
    rem_mins = total_mins % (24 * 60)
    hours = rem_mins // 60
    mins = rem_mins % 60

    if days > 0:
        dur_formatted = f"{days}d {hours}h {mins}m"
        dur_verbose = f"{days} day{'s' if days > 1 else ''}, {hours} hr{'s' if hours != 1 else ''} {mins} min"
    elif hours > 0:
        dur_formatted = f"{hours}h {mins}m"
        dur_verbose = f"{hours} hr{'s' if hours != 1 else ''} {mins} min"
    else:
        dur_formatted = f"{max(mins, 1)} min"
        dur_verbose = f"{max(mins, 1)} minutes"

    # Departure & Arrival Timing with Real-Time Timezone Resolution
    tz_info, tz_abbr, tz_label = resolve_timezone(timezone_name)
    if now_dt is None:
        now_dt = datetime.datetime.now(tz_info)
    elif now_dt.tzinfo is None:
        now_dt = now_dt.replace(tzinfo=tz_info)
    else:
        now_dt = now_dt.astimezone(tz_info)

    dep_dt = now_dt + datetime.timedelta(minutes=departure_offset_minutes)
    arr_dt = dep_dt + datetime.timedelta(minutes=active_dur_mins)

    dep_time_str = dep_dt.strftime("%I:%M %p")
    arr_time_str = arr_dt.strftime("%I:%M %p")

    # Day offset calculation
    day_diff = (arr_dt.date() - dep_dt.date()).days
    if day_diff == 0:
        eta_day_offset_str = ""
        eta_badge_str = "Real-Time" if departure_offset_minutes == 0 else f"+{departure_offset_minutes}m offset"
    elif day_diff == 1:
        eta_day_offset_str = "+1 day"
        eta_badge_str = f"Arrives Next Day (+{day_diff}d)"
    else:
        eta_day_offset_str = f"+{day_diff} days"
        eta_badge_str = f"Arrives in {day_diff} days"

    # Energy / Fuel Estimate
    consumption_rate = profile["consumption_per_100km"]
    total_energy = (distance_km / 100.0) * consumption_rate
    energy_unit = profile["energy_unit"]
    if "kcal" in energy_unit:
        energy_str = f"~{int(total_energy):,} {energy_unit}"
    else:
        energy_str = f"~{total_energy:.1f} {energy_unit} {profile['fuel_name']}"

    # Carbon Footprint
    co2_g_km = profile["co2_g_km"]
    if co2_g_km == 0:
        co2_str = "0 kg CO₂ (Zero Emission 🍃)"
    else:
        total_co2_kg = (distance_km * co2_g_km) / 1000.0
        co2_str = f"~{total_co2_kg:.1f} kg CO₂"

    # Distance formatting
    if distance_unit.lower() in ["mi", "miles"]:
        dist_val = distance_km * 0.621371
        dist_str = f"{dist_val:.2f} mi"
    else:
        dist_str = f"{distance_km:.2f} km"

    pill_label = "⚡ Now" if departure_offset_minutes == 0 else f"+{departure_offset_minutes}m"

    return TransitKinematics(
        mode_key=clean_key,
        vehicle_name=profile["name"],
        vehicle_emoji=profile["emoji"],
        speed_kmh=active_speed,
        speed_range_str=profile["speed_range"],
        distance_km=distance_km,
        distance_formatted=dist_str,
        duration_minutes=active_dur_mins,
        duration_formatted=dur_formatted,
        duration_verbose=dur_verbose,
        departure_offset_minutes=departure_offset_minutes,
        departure_time_str=dep_time_str,
        departure_pill_label=pill_label,
        eta_time_str=arr_time_str,
        eta_badge_str=eta_badge_str,
        eta_day_offset_str=eta_day_offset_str,
        energy_estimate_str=energy_str,
        co2_str=co2_str,
        profile=profile,
        timezone_name=timezone_name,
        timezone_abbr=tz_abbr,
        timezone_label=tz_label
    )


def render_transit_kinematics_hud_html(kin: TransitKinematics, lang: Optional[str] = None) -> str:
    """
    Renders a stunning Cyber-Glassmorphic HUD displaying accurate vehicle speed,
    calibrated travel duration, departure time, and arrival ETA.
    """
    try:
        from src.i18n import t, get_current_language
        actual_lang = lang or get_current_language()
    except Exception:
        actual_lang = lang or "en"
        def t(k, default="", lang=None): return default

    p = kin.profile
    border_col = p["border_color"]
    glow_bg = p["bg_glow"]
    theme_col = p["color"]

    # Localize departure label if "Now"
    dep_label = kin.departure_pill_label
    if "Now" in dep_label:
        dep_label = f"⚡ {t('dispatch.now', lang=actual_lang, default='Now')}"

    # Localize ETA badge (e.g. Arrives Next Day (+1d) or Same-Day Arrival)
    eta_badge = kin.eta_badge_str
    if "Next Day" in eta_badge:
        eta_badge = t("hud.arrives_next_day", lang=actual_lang, default="Arrives Next Day (+1d)")
    elif "Same-Day" in eta_badge:
        eta_badge = t("hud.same_day_arrive", lang=actual_lang, default="Same-Day Arrival")

    # Localize vehicle name
    veh_name_disp = t(f"fleet.{kin.vehicle_name.lower()}", lang=actual_lang, default=kin.vehicle_name)

    day_offset_badge = ""
    if kin.eta_day_offset_str:
        day_offset_badge = f"""
        <span style='background: rgba(239, 68, 68, 0.25); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.5); font-size: 0.68rem; font-weight: 800; padding: 2px 7px; border-radius: 4px; margin-left: 6px; letter-spacing: 0.04em;'>
            {t("hud.arrives_next_day", lang=actual_lang, default=kin.eta_day_offset_str)}
        </span>
        """

    hud_title = t("hud.kinematics_title", lang=actual_lang, default="TRANSIT KINEMATICS & REAL-TIME ARRIVAL HUD")
    corridor_physics_lbl = t("hud.corridor_physics", lang=actual_lang, default="Corridor Physics:")
    departure_time_lbl = t("hud.departure_time", lang=actual_lang, default="DEPARTURE TIME")
    live_satellite_clock_lbl = t("hud.live_satellite_clock", lang=actual_lang, default="Live Satellite Clock")
    speed_time_lbl = t("hud.speed_and_time", lang=actual_lang, default="SPEED & ACCURATE TIME")
    cruise_lbl = t("hud.cruise", lang=actual_lang, default="Cruise:")
    calibrated_physics_lbl = t("hud.calibrated_physics", lang=actual_lang, default="Calibrated Physics")
    eta_lbl = t("hud.eta", lang=actual_lang, default="ESTIMATED ARRIVAL (ETA)")
    total_leg_lbl = t("hud.total_leg", lang=actual_lang, default="Total Leg:")

    raw_html = f"""
<div style=' background: linear-gradient(135deg, rgba(15, 23, 42, 0.90) 0%, rgba(30, 41, 59, 0.82) 100%); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); border: 1.5px solid {border_col}; box-shadow: 0 10px 32px rgba(0, 0, 0, 0.45), inset 0 1px 1px rgba(255, 255, 255, 0.1); border-radius: 14px; padding: 16px 20px; margin: 10px 0 16px 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; '>
    <!-- Header Banner -->
    <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 10px; margin-bottom: 14px;'>
        <div style='display: flex; align-items: center; gap: 10px;'>
            <span style=' display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: {theme_col}; box-shadow: 0 0 10px {theme_col}; '></span>
            <span style='font-size: 0.76rem; font-weight: 900; color: #f8fafc; letter-spacing: 0.08em; text-transform: uppercase;'>
                ⚡ {hud_title}
            </span>
            <span style=' background: {glow_bg}; color: {theme_col}; border: 1px solid {border_col}; font-size: 0.72rem; font-weight: 800; padding: 2px 9px; border-radius: 12px; '>
                {kin.vehicle_emoji} {veh_name_disp}
            </span>
        </div>
        <div style='font-size: 0.72rem; color: #94a3b8; display: flex; align-items: center; gap: 6px;'>
            <span>{corridor_physics_lbl}</span>
            <span style='color: #f1f5f9; font-weight: 600;'>{p["desc"].split("•")[0].strip()}</span>
        </div>
    </div>

    <!-- 3-Segment Cockpit Telemetry Grid -->
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px;'>
        
        <!-- Segment 1: Departure Schedule -->
        <div style=' background: rgba(10, 18, 35, 0.65); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 10px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between; '>
            <div>
                <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;'>
                    <span style='font-size: 0.70rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em;'>
                        🕒 {departure_time_lbl}
                    </span>
                    <div style='display: flex; align-items: center; gap: 4px;'>
                        <span style=' background: rgba(147, 51, 234, 0.2); color: #c084fc; font-size: 0.65rem; font-weight: 800; padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(168, 85, 247, 0.4); '>
                            🌐 {kin.timezone_abbr}
                        </span>
                        <span style=' background: rgba(56, 189, 248, 0.16); color: #38bdf8; font-size: 0.68rem; font-weight: 800; padding: 1px 7px; border-radius: 4px; border: 1px solid rgba(56, 189, 248, 0.3); '>
                            {dep_label}
                        </span>
                    </div>
                </div>
                <div style='display: flex; align-items: baseline; gap: 6px;'>
                    <span id='hud-live-departure-clock' data-offset='{kin.departure_offset_minutes}' data-tz='{kin.timezone_name}' style='font-size: 1.85rem; font-weight: 900; color: #ffffff; letter-spacing: -0.02em; line-height: 1.1;'>
                        {kin.departure_time_str}
                    </span>
                    <span style='font-size: 0.82rem; font-weight: 700; color: #a78bfa;'>
                        {kin.timezone_abbr}
                    </span>
                </div>
            </div>
            <div style='margin-top: 10px; padding-top: 8px; border-top: 1px dashed rgba(255, 255, 255, 0.08); font-size: 0.70rem; color: #94a3b8; display: flex; justify-content: space-between; align-items: center;'>
                <span>{kin.timezone_label.split("•")[0].strip()}</span>
                <span id='hud-live-satellite-clock' style='color: #34d399; font-weight: 700;'>● {live_satellite_clock_lbl}</span>
            </div>
        </div>

        <!-- Segment 2: Vehicle Speed & Accurate Travel Duration -->
        <div style=' background: rgba(10, 18, 35, 0.65); border: 1.5px solid {border_col}; border-radius: 10px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between; position: relative; overflow: hidden; '>
            <div>
                <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;'>
                    <span style='font-size: 0.70rem; font-weight: 800; color: {theme_col}; text-transform: uppercase; letter-spacing: 0.05em;'>
                        ⚡ {speed_time_lbl}
                    </span>
                    <span style=' background: {glow_bg}; color: {theme_col}; font-size: 0.68rem; font-weight: 800; padding: 1px 7px; border-radius: 4px; border: 1px solid {border_col}; '>
                        {kin.speed_kmh:.1f} km/h
                    </span>
                </div>
                
                <div style='display: flex; align-items: baseline; gap: 8px;'>
                    <div style='font-size: 1.85rem; font-weight: 900; color: #f8fafc; letter-spacing: -0.02em; line-height: 1.1;'>
                        {kin.duration_formatted}
                    </div>
                    <div style='font-size: 0.78rem; font-weight: 700; color: #94a3b8;'>
                        ({kin.duration_verbose})
                    </div>
                </div>
            </div>

            <div style='margin-top: 10px; padding-top: 8px; border-top: 1px dashed rgba(255, 255, 255, 0.08); font-size: 0.70rem; color: #94a3b8; display: flex; justify-content: space-between; align-items: center;'>
                <span>{cruise_lbl} <b style='color: #f1f5f9;'>{kin.speed_range_str}</b></span>
                <span style='color: {theme_col}; font-weight: 700;'>{calibrated_physics_lbl}</span>
            </div>
        </div>

        <!-- Segment 3: Estimated Arrival (ETA) & Distance -->
        <div style=' background: rgba(10, 18, 35, 0.65); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 10px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between; '>
            <div>
                <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;'>
                    <span style='font-size: 0.70rem; font-weight: 800; color: #34d399; text-transform: uppercase; letter-spacing: 0.05em;'>
                        🎯 {eta_lbl}
                    </span>
                    <div style='display: flex; align-items: center; gap: 4px;'>
                        <span style=' background: rgba(147, 51, 234, 0.2); color: #c084fc; font-size: 0.65rem; font-weight: 800; padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(168, 85, 247, 0.4); '>
                            {kin.timezone_abbr}
                        </span>
                        <span style=' background: rgba(16, 185, 129, 0.16); color: #34d399; font-size: 0.68rem; font-weight: 800; padding: 1px 7px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.35); '>
                            ● {eta_badge}
                        </span>
                    </div>
                </div>

                <div style='display: flex; align-items: baseline; gap: 6px;'>
                    <span id='hud-live-eta-clock' data-dur='{kin.duration_minutes}' style='font-size: 1.85rem; font-weight: 900; color: #ffffff; letter-spacing: -0.02em; line-height: 1.1;'>
                        {kin.eta_time_str}
                    </span>
                    <span style='font-size: 0.82rem; font-weight: 700; color: #34d399;'>
                        {kin.timezone_abbr}
                    </span>
                    {day_offset_badge}
                </div>
            </div>

            <div style='margin-top: 10px; padding-top: 8px; border-top: 1px dashed rgba(255, 255, 255, 0.08); font-size: 0.70rem; color: #94a3b8; display: flex; justify-content: space-between; align-items: center;'>
                <span>{total_leg_lbl} <b style='color: #38bdf8;'>{kin.distance_formatted}</b></span>
                <span style='color: #cbd5e1;'>{kin.energy_estimate_str}</span>
            </div>
        </div>

    </div>
</div>
"""
    return "\n".join(line.strip() for line in raw_html.splitlines() if line.strip())


def render_transit_kinematics_live_ticker_component(kin: TransitKinematics) -> str:
    """
    Renders an isolated, safe JavaScript live ticker for Streamlit components.html.
    Ticks every second, synchronizing Departure, ETA, and Satellite Clock in real time
    for the active timezone without any text leakage.
    """
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/></head>
<body style="margin:0; padding:0; background:transparent;">
<script>
(function() {{
    function pad(n) {{ return n < 10 ? '0' + n : '' + n; }}
    function formatTimeForTz(dateObj, tz) {{
        try {{
            var opt = {{ hour: '2-digit', minute: '2-digit', hour12: true }};
            if (tz && tz !== 'AUTO') opt.timeZone = tz;
            return new Intl.DateTimeFormat('en-US', opt).format(dateObj);
        }} catch(e) {{
            var h = dateObj.getHours();
            var m = dateObj.getMinutes();
            var ap = h >= 12 ? 'PM' : 'AM';
            h = h % 12; h = h ? h : 12;
            return pad(h) + ':' + pad(m) + ' ' + ap;
        }}
    }}
    function formatSec(dateObj, tz) {{
        try {{
            var opt = {{ hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true }};
            if (tz && tz !== 'AUTO') opt.timeZone = tz;
            return new Intl.DateTimeFormat('en-US', opt).format(dateObj);
        }} catch(e) {{ return ''; }}
    }}
    function updateLiveClocks() {{
        try {{
            var doc = window.parent ? window.parent.document : document;
            var depEl = doc.getElementById('hud-live-departure-clock');
            var etaEl = doc.getElementById('hud-live-eta-clock');
            var clockEl = doc.getElementById('hud-live-satellite-clock');
            if (!depEl || !etaEl) return;
            var offsetMins = parseInt(depEl.getAttribute('data-offset') || '0', 10);
            var durMins = parseFloat(etaEl.getAttribute('data-dur') || '0');
            var tzName = depEl.getAttribute('data-tz') || '{kin.timezone_name}';
            var now = new Date();
            var depTime = new Date(now.getTime() + offsetMins * 60000);
            var etaTime = new Date(depTime.getTime() + durMins * 60000);
            depEl.textContent = formatTimeForTz(depTime, tzName);
            etaEl.textContent = formatTimeForTz(etaTime, tzName);
            if (clockEl) {{
                var s = formatSec(now, tzName);
                clockEl.textContent = '● Live Satellite Clock' + (s ? (' (' + s + ')') : '');
            }}
        }} catch(err) {{}}
    }}
    updateLiveClocks();
    try {{
        if (window.parent && window.parent._hudClockTicker) {{
            clearInterval(window.parent._hudClockTicker);
        }}
        var ticker = setInterval(updateLiveClocks, 1000);
        if (window.parent) window.parent._hudClockTicker = ticker;
    }} catch(e) {{
        setInterval(updateLiveClocks, 1000);
    }}
}})();
</script>
</body>
</html>"""
