"""
Emergency Radar & Safe Amenities Interactive UI Module for P.A.T.H.F.I.N.D.E.R.
Provides:
- One-click Emergency Action Radar toggle button.
- Creative, cute, and interactive safety amenity card deck (NO annoying dropdowns).
- Direct Google Maps route redirection ('Route Here').
- Safe Simulated Emergency Dispatch Calling (Test Mode: zero accidental external phone calls).
"""

import urllib.parse
from typing import Any, Dict, List, Optional, Tuple
from src.emergency_service import EmergencyFacility, FacilityCategory


def generate_google_maps_directions_url(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    dest_name: Optional[str] = None,
    travel_mode: str = "driving",
    avoid_tolls: bool = False,
    avoid_highways: bool = False,
    avoid_ferries: bool = False
) -> str:
    """
    Generates a direct Google Maps navigation URL with origin, destination, travel mode, and avoidances.
    Opens directly in Google Maps on desktop and mobile browsers.
    """
    base_url = "https://www.google.com/maps/dir/?api=1"
    clean_mode = "driving"
    if travel_mode in ("walking", "walk"):
        clean_mode = "walking"
    elif travel_mode in ("bicycling", "bicycle", "bike"):
        clean_mode = "bicycling"
    elif travel_mode in ("transit", "bus"):
        clean_mode = "transit"
    elif travel_mode in ("driving", "car", "motorcycle", "tractor", "truck"):
        clean_mode = "driving"

    params: Dict[str, str] = {
        "origin": f"{origin_lat:.6f},{origin_lon:.6f}",
        "destination": f"{dest_lat:.6f},{dest_lon:.6f}",
        "travelmode": clean_mode
    }
    avoids = []
    if avoid_tolls:
        avoids.append("tolls")
    if avoid_highways:
        avoids.append("highways")
    if avoid_ferries:
        avoids.append("ferries")
    if avoids:
        params["avoid"] = ",".join(avoids)

    return f"{base_url}&{urllib.parse.urlencode(params)}"


def filter_facilities_by_category(
    facilities: List[EmergencyFacility],
    category_filter: str
) -> List[EmergencyFacility]:
    """Filters facilities according to the selected category."""
    if not facilities:
        return []
    if category_filter == "ALL":
        return facilities
    elif category_filter == "MEDICAL":
        return [f for f in facilities if f.category == FacilityCategory.MEDICAL]
    elif category_filter == "SHELTER":
        return [f for f in facilities if f.category == FacilityCategory.SAFE_SHELTER]
    elif category_filter == "ASSISTANCE":
        return [f for f in facilities if f.category == FacilityCategory.EMERGENCY_ASSISTANCE]
    elif category_filter == "TRAVEL":
        return [f for f in facilities if f.category == FacilityCategory.TRAVEL_ASSISTANCE]
    return facilities


def get_facility_status_badge(fac: EmergencyFacility) -> str:
    """Returns a cute, styled status badge HTML for a safety facility."""
    if fac.has_emergency_department is True:
        return "<span style='color: #ef4444; font-size: 0.68rem; font-weight: 800; background: rgba(239, 68, 68, 0.15); padding: 2px 7px; border-radius: 6px; border: 1px solid rgba(239, 68, 68, 0.35); display: inline-flex; align-items: center; gap: 4px;'>🚨 24/7 VERIFIED EMERGENCY DEPT</span>"
    elif fac.has_emergency_department is False:
        return "<span style='color: #f59e0b; font-size: 0.68rem; font-weight: 800; background: rgba(245, 158, 11, 0.15); padding: 2px 7px; border-radius: 6px; border: 1px solid rgba(245, 158, 11, 0.35); display: inline-flex; align-items: center; gap: 4px;'>🩺 CLINIC / NON-TRAUMA</span>"
    elif fac.is_officially_designated_shelter is True:
        return "<span style='color: #10b981; font-size: 0.68rem; font-weight: 800; background: rgba(16, 185, 129, 0.15); padding: 2px 7px; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.35); display: inline-flex; align-items: center; gap: 4px;'>🛡️ DESIGNATED SAFE HAVEN</span>"
    elif fac.category == FacilityCategory.TRAVEL_ASSISTANCE and "EV" in fac.facility_type.upper():
        return "<span style='color: #38bdf8; font-size: 0.68rem; font-weight: 800; background: rgba(56, 189, 248, 0.15); padding: 2px 7px; border-radius: 6px; border: 1px solid rgba(56, 189, 248, 0.35); display: inline-flex; align-items: center; gap: 4px;'>⚡ FAST EV CHARGING</span>"
    else:
        return f"<span style='color: #38bdf8; font-size: 0.68rem; font-weight: 700; background: rgba(56, 189, 248, 0.1); padding: 2px 7px; border-radius: 6px; border: 1px solid rgba(56, 189, 248, 0.25);'>{fac.facility_type}</span>"
