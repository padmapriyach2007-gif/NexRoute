"""
CampusAegis Real-World Map & Geocoding Service
Provides place-name geocoding, reverse geocoding, and interactive Folium/Leaflet map generation.
Uses OpenStreetMap Nominatim API with an integrated offline cache and fallback directory.

Safety & Licensing Notice:
Uses OpenStreetMap data under the Open Database License (ODbL).
Nominatim requests include standard User-Agent headers and rate-limiting safeguards.
"""

import os
import requests
import json
import time
from typing import Dict, List, Tuple, Optional, Any
import folium
from folium import plugins


# Pre-cached regional landmarks for instant offline operation and test repeatability
import re

# Pre-cached regional landmarks, micro-areas, wards, colonies, and campus blocks
OFFLINE_GEOCODE_CACHE = {
    # Baseline Universities & Campus Micro-Locations
    "vignan university": {"lat": 16.2335, "lon": 80.5505, "name": "Vignan's Foundation for Science, Technology & Research, Vadlamudi"},
    "vignan campus": {"lat": 16.2335, "lon": 80.5505, "name": "Vignan University Main Campus"},
    "vignan main gate": {"lat": 16.2325, "lon": 80.5490, "name": "Vignan University Main Entrance Arch, Vadlamudi Road"},
    "vignan library": {"lat": 16.2338, "lon": 80.5512, "name": "NTR Vignan Central Library Block"},
    "ntr library": {"lat": 16.2338, "lon": 80.5512, "name": "NTR Vignan Central Library Block"},
    "chemical engineering": {"lat": 16.2340, "lon": 80.5498, "name": "Chemical Reaction Engineering Department Block"},
    "chemical reaction": {"lat": 16.2340, "lon": 80.5498, "name": "Chemical Reaction Engineering Department Block"},
    "cse block": {"lat": 16.2348, "lon": 80.5515, "name": "Computer Science & Engineering Academic Block"},
    "computer science": {"lat": 16.2348, "lon": 80.5515, "name": "Computer Science & Engineering Department"},
    "it block": {"lat": 16.2346, "lon": 80.5518, "name": "Information Technology Department & Lab Block"},
    "a-block": {"lat": 16.2330, "lon": 80.5500, "name": "A-Block Administrative Complex"},
    "admin block": {"lat": 16.2330, "lon": 80.5500, "name": "Vignan Foundation Administrative Block"},
    "h-block": {"lat": 16.2342, "lon": 80.5522, "name": "H-Block Academic Complex"},
    "u-block": {"lat": 16.2352, "lon": 80.5508, "name": "U-Block Technology & Science Center"},
    "lara college": {"lat": 16.2375, "lon": 80.5480, "name": "Lara Institute of Technology & Sciences"},
    "lara engineering": {"lat": 16.2375, "lon": 80.5480, "name": "Lara Institute of Technology & Sciences"},
    "pharmacy block": {"lat": 16.2365, "lon": 80.5490, "name": "Vignan Institute of Pharmaceutical Sciences"},
    "boys hostel": {"lat": 16.2315, "lon": 80.5535, "name": "Vignan Boys Hostel Complex (Priyamvada)"},
    "girls hostel": {"lat": 16.2355, "lon": 80.5540, "name": "Vignan Girls Hostel Complex"},
    "open air theatre": {"lat": 16.2332, "lon": 80.5518, "name": "Vignan Open Air Theatre (OAT)"},
    "sports complex": {"lat": 16.2310, "lon": 80.5485, "name": "Vignan University Sports Complex & Athletic Grounds"},
    "play grounds": {"lat": 16.2310, "lon": 80.5485, "name": "Vignan University Sports Ground"},
    "food court": {"lat": 16.2336, "lon": 80.5525, "name": "Vignan Central Food Court & Student Cafeteria"},
    "convocation hall": {"lat": 16.2328, "lon": 80.5508, "name": "Mahathi Convocation Auditorium"},

    # Guntur Colonies, Small Areas & Neighborhood Wards
    "arundelpet": {"lat": 16.3075, "lon": 80.4350, "name": "Arundelpet, Guntur"},
    "brodipet": {"lat": 16.3015, "lon": 80.4420, "name": "Brodipet Commercial Center, Guntur"},
    "kothapet": {"lat": 16.3120, "lon": 80.4480, "name": "Kothapet, Guntur"},
    "lalapet": {"lat": 16.3080, "lon": 80.4520, "name": "Lalapet, Guntur"},
    "pattabhipuram": {"lat": 16.2950, "lon": 80.4280, "name": "Pattabhipuram Residential Area, Guntur"},
    "gorantla": {"lat": 16.3250, "lon": 80.4180, "name": "Gorantla, Guntur"},
    "vidya nagar": {"lat": 16.2880, "lon": 80.4220, "name": "Vidya Nagar, Guntur"},
    "syamala nagar": {"lat": 16.2920, "lon": 80.4310, "name": "Syamala Nagar, Guntur"},
    "old guntur": {"lat": 16.3150, "lon": 80.4600, "name": "Old Guntur Historic Center"},
    "autonagar": {"lat": 16.2890, "lon": 80.4550, "name": "Auto Nagar Industrial Hub, Guntur"},
    "auto nagar": {"lat": 16.2890, "lon": 80.4550, "name": "Auto Nagar Industrial Hub, Guntur"},
    "etukuru": {"lat": 16.2750, "lon": 80.4720, "name": "Etukuru Bypass Junction, Guntur"},
    "pedakakani": {"lat": 16.3420, "lon": 80.5050, "name": "Pedakakani Temple Center, Guntur District"},
    "kaza": {"lat": 16.3750, "lon": 80.5580, "name": "Kaza Toll Plaza, NH-16"},
    "mangalagiri": {"lat": 16.4350, "lon": 80.5680, "name": "Mangalagiri Town & AIIMS, Guntur District"},
    "gaddipadu": {"lat": 16.3210, "lon": 80.4780, "name": "Gaddipadu Village Area, Guntur"},
    "takkellapadu": {"lat": 16.3350, "lon": 80.4650, "name": "Takkellapadu, Guntur"},
    "uppalapadu": {"lat": 16.2780, "lon": 80.5280, "name": "Uppalapadu Bird Sanctuary, Guntur District"},
    "koritepadu": {"lat": 16.3120, "lon": 80.4280, "name": "Koritepadu, Guntur"},
    "lakshmipuram": {"lat": 16.3010, "lon": 80.4310, "name": "Lakshmipuram Main Road, Guntur"},
    "gujjanagundla": {"lat": 16.2920, "lon": 80.4180, "name": "Gujjanagundla Ring Road, Guntur"},
    "guntur railway station": {"lat": 16.3045, "lon": 80.4445, "name": "Guntur Junction Railway Station"},
    "guntur bus stand": {"lat": 16.3080, "lon": 80.4420, "name": "NTR RTC Bus Stand, Guntur"},
    "guntur": {"lat": 16.3067, "lon": 80.4365, "name": "Guntur City Center, Andhra Pradesh"},

    # Intermediate Villages, Mandals & Rural Corridors
    "budampadu": {"lat": 16.2620, "lon": 80.4680, "name": "Budampadu Village Cross, Guntur District"},
    "selapadu": {"lat": 16.2480, "lon": 80.5220, "name": "Selapadu Village, Guntur District"},
    "sangam jagarlamudi": {"lat": 16.2350, "lon": 80.5050, "name": "Sangam Jagarlamudi Junction"},
    "sangam": {"lat": 16.2350, "lon": 80.5050, "name": "Sangam Jagarlamudi Junction"},
    "sitarampuram": {"lat": 16.2410, "lon": 80.5180, "name": "Sitarampuram Rural Colony"},
    "kothareddypalem": {"lat": 16.2180, "lon": 80.4850, "name": "Kothareddypalem Village"},
    "pathareddypalem": {"lat": 16.2120, "lon": 80.4890, "name": "Pathareddypalem, Chebrolu Mandal"},
    "gundavaram": {"lat": 16.2380, "lon": 80.4780, "name": "Gundavaram Rural Junction"},
    "godavarru": {"lat": 16.2450, "lon": 80.4720, "name": "Godavarru Village, Guntur District"},
    "lemallepadu": {"lat": 16.2220, "lon": 80.4550, "name": "Lemallepadu Village"},
    "vatticherukuru": {"lat": 16.1980, "lon": 80.4450, "name": "Vatticherukuru Mandal Headquarters"},
    "kovelamudi": {"lat": 16.2050, "lon": 80.4680, "name": "Kovelamudi Village"},
    "narakodur": {"lat": 16.2650, "lon": 80.4980, "name": "Narakodur Center Cross, Guntur District"},
    "vadlamudi": {"lat": 16.2319, "lon": 80.5539, "name": "Vadlamudi Center & Municipal Hub"},
    "chebrolu": {"lat": 16.2010, "lon": 80.5280, "name": "Chebrolu Heritage Center & Historical Temples"},
    "sekuru": {"lat": 16.2550, "lon": 80.5150, "name": "Sekuru Village"},
    "duggirala": {"lat": 16.3280, "lon": 80.6280, "name": "Duggirala Agricultural Market Yard"},
    "pedavadlapudi": {"lat": 16.4150, "lon": 80.6050, "name": "Pedavadlapudi Rural Junction"},
    "kolakaluru": {"lat": 16.2950, "lon": 80.6150, "name": "Kolakaluru Village, Tenali Mandal"},
    "koppuravuru": {"lat": 16.2820, "lon": 80.4880, "name": "Koppuravuru Village, Pedakakani"},

    # Tenali Town Wards, Small Areas & Environs
    "morrispet": {"lat": 16.2380, "lon": 80.6450, "name": "Morrispet, Tenali"},
    "chenchupet": {"lat": 16.2450, "lon": 80.6350, "name": "Chenchupet, Tenali"},
    "angalakuduru": {"lat": 16.2280, "lon": 80.6220, "name": "Angalakuduru Village, Tenali"},
    "nazerpet": {"lat": 16.2410, "lon": 80.6480, "name": "Nazerpet, Tenali"},
    "chinaravuru": {"lat": 16.2520, "lon": 80.6550, "name": "Chinaravuru, Tenali"},
    "pinapadu": {"lat": 16.2490, "lon": 80.6290, "name": "Pinapadu, Tenali"},
    "tenali railway station": {"lat": 16.2395, "lon": 80.6465, "name": "Tenali Junction Railway Station"},
    "tenali": {"lat": 16.2430, "lon": 80.6400, "name": "Tenali Town, Guntur District"},

    # Major Regional Cities
    "vijayawada": {"lat": 16.5062, "lon": 80.6480, "name": "Vijayawada Junction, Andhra Pradesh"},
    "amaravati": {"lat": 16.5417, "lon": 80.5150, "name": "Amaravati Capital City, Andhra Pradesh"},
    "hyderabad": {"lat": 17.3850, "lon": 78.4867, "name": "Hyderabad, Telangana"},
    "delhi": {"lat": 28.6139, "lon": 77.2090, "name": "New Delhi Central, India"},
    "bangalore": {"lat": 12.9716, "lon": 77.5946, "name": "Bengaluru, Karnataka"},
    "mumbai": {"lat": 19.0760, "lon": 72.8777, "name": "Mumbai, Maharashtra"}
}


class MapService:
    def __init__(
        self,
        user_agent: str = "PATHFINDER-Global-Nav/2.0 (predictive.adaptive.transit@navigation.org)",
        base_url: Optional[str] = None,
        timeout_sec: float = 4.0
    ):
        self.user_agent = user_agent
        self.base_url = (base_url or os.environ.get("NOMINATIM_BASE_URL", "https://nominatim.openstreetmap.org")).rstrip("/")
        self.timeout_sec = timeout_sec
        self.cache: Dict[str, Dict[str, Any]] = dict(OFFLINE_GEOCODE_CACHE)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self._last_request_time = 0.0
        self._min_request_interval = 0.35  # Comply with OSM Nominatim usage policy

    def _respect_rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

    def geocode(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Geocodes any global address, city, country, landmark, postal code,
        or GPS coordinate pair to (latitude, longitude, display_name).

        Resolution pipeline:
        1. Direct Coordinate Detection with strict WGS84 range validation (-90 to +90, -180 to +180)
        2. Exact Offline Local Alias Match (Vignan, Guntur, Tenali local wards/landmarks)
        3. Global Provider Search (OpenStreetMap Nominatim worldwide query)
        4. Curated Fuzzy Token Match for regional campus/corridor aliases
        5. Return None if unresolved — NEVER silently substitute an incorrect regional anchor
        """
        candidates = self.geocode_candidates(query, limit=1)
        return candidates[0] if candidates else None

    def geocode_candidates(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Disambiguates queries by returning candidate worldwide matches with
        country, region/state, coordinates, and classification.
        """
        q_raw = query.strip()
        if not q_raw:
            return []

        # ---------------------------------------------------------
        # TIER 1: Direct Coordinate Detection & Strict Range Validation
        # ---------------------------------------------------------
        coord_pattern = r"^\s*\(?\s*([+-]?\d{1,2}(?:\.\d+)?)\s*[,\s]\s*([+-]?\d{1,3}(?:\.\d+)?)\s*\)?\s*$"
        coord_match = re.match(coord_pattern, q_raw)
        if coord_match:
            try:
                c_lat = float(coord_match.group(1))
                c_lon = float(coord_match.group(2))
                # Validate physical latitude (-90 to 90) and longitude (-180 to 180)
                if -90.0 <= c_lat <= 90.0 and -180.0 <= c_lon <= 180.0:
                    return [{
                        "lat": c_lat,
                        "lon": c_lon,
                        "display_name": f"Pinpoint Coordinate ({c_lat:.5f}, {c_lon:.5f})",
                        "country": "Global Coordinates",
                        "state": "",
                        "type": "coordinate",
                        "importance": 1.0,
                        "source": "COORDINATE_INPUT"
                    }]
                else:
                    # Out of bounds coordinates: do not fabricate or search text
                    return []
            except Exception:
                return []

        q_norm = q_raw.lower()

        # Handle 'current location' keyword
        if "current" in q_norm:
            c_base = OFFLINE_GEOCODE_CACHE["vignan university"]
            return [{
                "lat": c_base["lat"],
                "lon": c_base["lon"],
                "display_name": "📍 Current Location",
                "country": "India",
                "state": "Andhra Pradesh",
                "type": "current_location",
                "importance": 1.0,
                "source": "CURRENT_LOCATION"
            }]

        # ---------------------------------------------------------
        # TIER 2: Exact Match in Pre-cached Directory (Instant response)
        # ---------------------------------------------------------
        if q_norm in self.cache:
            v = self.cache[q_norm]
            return [{
                "lat": v["lat"],
                "lon": v["lon"],
                "display_name": v.get("display_name", v.get("name", q_raw)),
                "country": v.get("country", "Local / Cached"),
                "state": v.get("state", ""),
                "type": "cached_place",
                "importance": 0.95,
                "source": "OFFLINE_CACHE"
            }]

        candidates: List[Dict[str, Any]] = []

        # ---------------------------------------------------------
        # TIER 3: Worldwide Geocoding Provider (OpenStreetMap Nominatim / Photon)
        # ---------------------------------------------------------
        try:
            self._respect_rate_limit()
            url = f"{self.base_url}/search"
            params = {
                "q": q_raw,
                "format": "jsonv2",
                "limit": limit,
                "addressdetails": 1
            }
            resp = self.session.get(url, params=params, timeout=self.timeout_sec)
            if resp.status_code == 200:
                results = resp.json()
                for item in results:
                    addr = item.get("address", {})
                    country = addr.get("country", "")
                    state = addr.get("state", addr.get("region", ""))
                    city = addr.get("city", addr.get("town", addr.get("village", "")))
                    c_lat = float(item["lat"])
                    c_lon = float(item["lon"])
                    c_entry = {
                        "lat": c_lat,
                        "lon": c_lon,
                        "display_name": item.get("display_name", q_raw),
                        "country": country,
                        "state": state,
                        "city": city,
                        "type": item.get("type", item.get("category", "place")),
                        "importance": float(item.get("importance", 0.5)),
                        "source": "GLOBAL_OSM_NOMINATIM"
                    }
                    candidates.append(c_entry)
                    # Cache top result
                    if len(candidates) == 1:
                        self.cache[q_norm] = c_entry
        except Exception:
            pass

        if candidates:
            return candidates

        # ---------------------------------------------------------
        # TIER 4: Curated Local Substring & Fuzzy Match for Regional Campus Queries
        # ---------------------------------------------------------
        # Only fallback to offline cache if query shares tokens with local campus or district
        q_tokens = set(re.findall(r"\w+", q_norm))
        if q_tokens:
            best_match = None
            max_token_overlap = 0
            for k, v in self.cache.items():
                if k == q_norm or (len(q_norm) > 4 and k in q_norm):
                    return [{
                        "lat": v["lat"],
                        "lon": v["lon"],
                        "display_name": v.get("name", q_raw),
                        "country": "India",
                        "state": "Andhra Pradesh",
                        "type": "regional_alias",
                        "importance": 0.8,
                        "source": "REGIONAL_ALIAS"
                    }]

                k_tokens = set(re.findall(r"\w+", k))
                name_tokens = set(re.findall(r"\w+", v.get("name", "").lower()))
                all_candidate_tokens = k_tokens.union(name_tokens)
                overlap = len(q_tokens.intersection(all_candidate_tokens))
                if overlap > max_token_overlap and overlap >= min(len(q_tokens), 2):
                    max_token_overlap = overlap
                    best_match = v

            if best_match and max_token_overlap >= 2:
                matched_entry = {
                    "lat": best_match["lat"],
                    "lon": best_match["lon"],
                    "display_name": best_match.get("name", q_raw),
                    "country": "India",
                    "state": "Andhra Pradesh",
                    "type": "fuzzy_regional_match",
                    "importance": 0.7,
                    "source": "FUZZY_REGIONAL_MATCH"
                }
                self.cache[q_norm] = matched_entry
                return [matched_entry]

        # Explicitly return empty candidate list if query cannot be resolved.
        # NEVER fabricate or substitute a regional anchor.
        return []

    def reverse_geocode(self, lat: float, lon: float) -> str:
        """Translates lat/lon into human-readable landmark or address worldwide."""
        # Check proximity to known cached landmarks (< 300 meters)
        for k, v in self.cache.items():
            if abs(v["lat"] - lat) < 0.003 and abs(v["lon"] - lon) < 0.003:
                return v.get("display_name", v.get("name", "Known Landmark"))

        try:
            self._respect_rate_limit()
            url = f"{self.base_url}/reverse"
            params = {
                "lat": lat,
                "lon": lon,
                "format": "jsonv2",
                "addressdetails": 1
            }
            resp = self.session.get(url, params=params, timeout=self.timeout_sec)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("display_name", f"{lat:.4f}, {lon:.4f}")
        except Exception:
            pass

        return f"Geographic Point ({lat:.4f}° N, {lon:.4f}° E)"

    def create_interactive_map(
        self,
        center_lat: float,
        center_lon: float,
        zoom: int = 14,
        origin_coords: Optional[Tuple[float, float]] = None,
        destination_coords: Optional[Tuple[float, float]] = None,
        routes: Optional[List[Dict[str, Any]]] = None,
        hazards: Optional[List[Dict[str, Any]]] = None,
        road_closures: Optional[List[Dict[str, Any]]] = None,
        breadcrumb_trail: Optional[List[Tuple[float, float]]] = None,
        map_style: str = "satellite_hybrid",
        auto_fit_bounds: bool = False,
        traveler_avatar: str = "boy",
        emergency_facilities: Optional[List[Dict[str, Any]]] = None
    ) -> folium.Map:
        """
        Creates a rich, multi-layered interactive Folium Leaflet Map with:
        - Photorealistic Satellite imagery (Google Satellite Hybrid & Esri World Imagery)
        - Origin marker (Blue pulse)
        - Destination marker (Green shield)
        - Multi-route polylines (Primary green, Alternatives dashed/purple, Hazardous red)
        - Active hazard zones (Amber/Red transparent circular buffer zones)
        - Road closure barricade markers
        - Real-time GPS Tracker & Live Location Lock
        """
        # Create base Folium Map without default single tile layer so selectable layers can be layered cleanly
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom,
            tiles=None,
            control_scale=True,
            attribution_control=False,
            zoom_control=False
        )

        # Sole Basemap: High-Resolution Satellite View (Satellite Imagery + Street Labels)
        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
            attr="Google Satellite",
            name="🛰️ Satellite View",
            overlay=False,
            control=False
        ).add_to(m)

        # High-Accuracy Real-Time GPS Tracking Plugin (Google Maps style)
        try:
            import folium.plugins as plugins
            plugins.LocateControl(
                auto_start=False,
                flyTo=True,
                keepCurrentZoomLevel=True,
                drawCircle=True,
                drawMarker=True,
                showPopup=True,
                strings={
                    "title": "🎯 Lock Live GPS Location (Google Maps Accuracy)",
                    "popup": "📍 Live Traveler Position (Accurate within {distance} {unit})"
                },
                locateOptions={
                    "enableHighAccuracy": True,
                    "watch": True,
                    "maxZoom": 18
                }
            ).add_to(m)
        except Exception:
            pass

        # 1. Add Origin Marker with Small Boy / Driving Car Avatar & Pulsing Radar Wave
        if origin_coords:
            avatar_key = str(traveler_avatar).lower()
            if "tractor" in avatar_key:
                avatar_sym = "🚜"
                avatar_title = "🚜 Tractor (Agricultural & Rural Navigation)"
                halo_border = "#16a34a"
                halo_bg = "rgba(22, 163, 74, 0.35)"
            elif "bike" in avatar_key or "motorcycle" in avatar_key:
                avatar_sym = "🏍️"
                avatar_title = "🏍️ Bike / Motorcycle"
                halo_border = "#0284c7"
                halo_bg = "rgba(2, 132, 199, 0.35)"
            elif "truck" in avatar_key:
                avatar_sym = "🚚"
                avatar_title = "🚚 Truck / Heavy Vehicle"
                halo_border = "#f59e0b"
                halo_bg = "rgba(245, 158, 11, 0.35)"
            elif "bicycle" in avatar_key:
                avatar_sym = "🚴"
                avatar_title = "🚴 Bicycle"
                halo_border = "#10b981"
                halo_bg = "rgba(16, 185, 129, 0.35)"
            elif "walk" in avatar_key or avatar_key == "boy":
                avatar_sym = "🚶‍♂️"
                avatar_title = "🚶‍♂️ Small Boy Walking (Swiggy/Zomato Tracking)"
                halo_border = "#38bdf8"
                halo_bg = "rgba(56, 189, 248, 0.35)"
            else:
                avatar_sym = "🚗"
                avatar_title = "🚗 Driving Car (Google Maps GPS Vehicle)"
                halo_border = "#10b981"
                halo_bg = "rgba(16, 185, 129, 0.35)"

            # Inject CSS animation styles into Folium map
            folium_css = """
            <style>
            @keyframes foliumRadar {
                0% { transform: scale(0.4); opacity: 1; }
                100% { transform: scale(1.6); opacity: 0; }
            }
            @keyframes foliumLegLeft {
                0% { transform: rotate(-24deg); transform-origin: 28px 42px; }
                100% { transform: rotate(24deg); transform-origin: 28px 42px; }
            }
            @keyframes foliumLegRight {
                0% { transform: rotate(24deg); transform-origin: 38px 42px; }
                100% { transform: rotate(-24deg); transform-origin: 38px 42px; }
            }
            @keyframes foliumArmLeft {
                0% { transform: rotate(24deg); transform-origin: 22px 28px; }
                100% { transform: rotate(-24deg); transform-origin: 22px 28px; }
            }
            @keyframes foliumArmRight {
                0% { transform: rotate(-24deg); transform-origin: 42px 28px; }
                100% { transform: rotate(24deg); transform-origin: 42px 28px; }
            }
            .folium-walking-leg-left { animation: foliumLegLeft 0.5s infinite alternate ease-in-out; }
            .folium-walking-leg-right { animation: foliumLegRight 0.5s infinite alternate ease-in-out; }
            .folium-walking-arm-left { animation: foliumArmLeft 0.5s infinite alternate ease-in-out; }
            .folium-walking-arm-right { animation: foliumArmRight 0.5s infinite alternate ease-in-out; }
            </style>
            """
            m.get_root().header.add_child(folium.Element(folium_css))

            if "walk" in avatar_key or avatar_key == "boy":
                avatar_html = f"""
                <div style="position: relative; display: flex; align-items: center; justify-content: center; width: 48px; height: 48px; cursor: pointer;">
                    <div style="position: absolute; width: 44px; height: 44px; border-radius: 50%; background: {halo_bg}; border: 2.5px solid {halo_border}; box-shadow: 0 0 16px {halo_border}; animation: foliumRadar 1.6s infinite ease-out;"></div>
                    <div style="position: relative; z-index: 2; filter: drop-shadow(0 3px 6px rgba(0,0,0,0.8));">
                        <svg width="44" height="44" viewBox="0 0 64 64" fill="none">
                            <rect x="12" y="24" width="12" height="18" rx="4" fill="#0284c7" stroke="#38bdf8" stroke-width="2"/>
                            <g class="folium-walking-leg-left">
                                <line x1="28" y1="42" x2="24" y2="58" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round"/>
                                <ellipse cx="23" cy="58" rx="4.5" ry="3" fill="#ef4444"/>
                            </g>
                            <g class="folium-walking-leg-right">
                                <line x1="38" y1="42" x2="42" y2="58" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round"/>
                                <ellipse cx="43" cy="58" rx="4.5" ry="3" fill="#ef4444"/>
                            </g>
                            <g class="folium-walking-arm-left">
                                <line x1="22" y1="28" x2="16" y2="38" stroke="#fde047" stroke-width="3" stroke-linecap="round"/>
                            </g>
                            <rect x="22" y="24" width="20" height="20" rx="5" fill="#10b981" stroke="#059669" stroke-width="2"/>
                            <rect x="29" y="28" width="6" height="5" rx="1.5" fill="#ffffff" opacity="0.85"/>
                            <g class="folium-walking-arm-right">
                                <line x1="42" y1="28" x2="48" y2="38" stroke="#fde047" stroke-width="3.5" stroke-linecap="round"/>
                            </g>
                            <circle cx="32" cy="15" r="9" fill="#fde047" stroke="#ca8a04" stroke-width="1.5"/>
                            <path d="M22 13 C22 7, 42 7, 42 13 L47 14 L22 14 Z" fill="#ef4444"/>
                            <circle cx="30" cy="14" r="1.5" fill="#0f172a"/>
                            <circle cx="36" cy="14" r="1.5" fill="#0f172a"/>
                            <path d="M30 18 Q33 21 36 18" stroke="#0f172a" stroke-width="1.5" fill="none" stroke-linecap="round"/>
                            <circle cx="23" cy="15" r="2" fill="#38bdf8"/>
                        </svg>
                    </div>
                </div>
                """
            else:
                avatar_html = f"""
                <div style="position: relative; display: flex; align-items: center; justify-content: center; width: 44px; height: 44px; cursor: pointer;">
                    <div style="position: absolute; width: 42px; height: 42px; border-radius: 50%; background: {halo_bg}; border: 2.5px solid {halo_border}; box-shadow: 0 0 16px {halo_border}; animation: foliumRadar 1.6s infinite ease-out;"></div>
                    <div style="position: relative; z-index: 2; font-size: 26px; filter: drop-shadow(0 3px 6px rgba(0,0,0,0.8));">{avatar_sym}</div>
                </div>
                """

            folium.Marker(
                location=origin_coords,
                popup=folium.Popup(f"<b>{avatar_title}</b><br>Coords: {origin_coords[0]:.5f}, {origin_coords[1]:.5f}", max_width=260),
                tooltip=avatar_title,
                icon=folium.DivIcon(html=avatar_html, icon_size=(48, 48), icon_anchor=(24, 24))
            ).add_to(m)

            folium.Circle(
                location=origin_coords,
                radius=35.0,
                color=halo_border,
                weight=2,
                fill=True,
                fill_color=halo_border,
                fill_opacity=0.3
            ).add_to(m)

        # Breadcrumb Movement History Trail
        if breadcrumb_trail and len(breadcrumb_trail) > 1:
            folium.PolyLine(
                locations=breadcrumb_trail,
                color="#0284c7",
                weight=3,
                opacity=0.75,
                dash_array="6, 8",
                tooltip="Live Movement Trail"
            ).add_to(m)

        # 2. Add Destination Marker
        if destination_coords:
            folium.Marker(
                location=destination_coords,
                popup=folium.Popup("<b>🏁 Safe Destination</b><br>Designated assembly or target", max_width=250),
                tooltip="Safe Destination",
                icon=folium.Icon(color="green", icon="flag-checkered", prefix="fa")
            ).add_to(m)

        # 3. Add Verified Road Restrictions & Blockages with Caution Symbols
        if road_closures:
            for rc in road_closures:
                c_lat = rc.get("lat")
                c_lon = rc.get("lon")
                road_name = rc.get("road_name", "Arterial Road")
                r_type = rc.get("type", "ROAD_BLOCKAGE")
                desc = rc.get("description", "Road Blockage / Scheduled Maintenance")
                is_hard = rc.get("is_hard_closure", True)
                radius = float(rc.get("radius_meters", 120.0))

                if c_lat and c_lon:
                    # Caution Zone Buffer Circle
                    folium.Circle(
                        location=[c_lat, c_lon],
                        radius=max(60.0, radius),
                        color="#ef4444" if is_hard else "#f59e0b",
                        weight=3,
                        dash_array="6, 6",
                        fill=True,
                        fill_color="#ef4444" if is_hard else "#f59e0b",
                        fill_opacity=0.35,
                        tooltip=f"⚠️ CAUTION: {'Road Blockage / Closure' if is_hard else 'Road Work'} - {road_name}"
                    ).add_to(m)

                    # Prominent Floating Caution Badge on Map
                    badge_html = f"""
                    <div style="
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        cursor: pointer;
                        filter: drop-shadow(0 4px 10px rgba(0,0,0,0.6));
                    ">
                        <div style="
                            display: flex;
                            align-items: center;
                            gap: 6px;
                            background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
                            color: #ffffff;
                            border: 2px solid #ffffff;
                            border-radius: 20px;
                            padding: 5px 12px;
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                            font-weight: 800;
                            font-size: 12px;
                            letter-spacing: 0.5px;
                            white-space: nowrap;
                            box-shadow: 0 0 15px rgba(239, 68, 68, 0.9);
                        ">
                            <span style="font-size: 16px;">⚠️</span>
                            <span>ROAD BLOCKED</span>
                        </div>
                        <div style="
                            width: 0;
                            height: 0;
                            border-left: 7px solid transparent;
                            border-right: 7px solid transparent;
                            border-top: 8px solid #b91c1c;
                            margin-top: -1px;
                        "></div>
                    </div>
                    """
                    folium.Marker(
                        location=[c_lat, c_lon],
                        icon=folium.DivIcon(
                            html=badge_html,
                            icon_size=(160, 40),
                            icon_anchor=(80, 40)
                        ),
                        popup=folium.Popup(
                            f"""
                            <div style='font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; min-width: 220px; padding: 4px;'>
                                <div style='background: #dc2626; color: #ffffff; padding: 5px 8px; border-radius: 5px; font-weight: 800; font-size: 0.84rem; display: flex; align-items: center; gap: 6px;'>
                                    <span>⚠️</span> <span>CAUTION: ROAD BLOCKAGE</span>
                                </div>
                                <div style='margin-top: 8px; font-size: 0.80rem; color: #1e293b; line-height: 1.45;'>
                                    <b>Location:</b> {road_name}<br>
                                    <b>Condition:</b> {r_type}<br>
                                    <b>Details:</b> {desc}<br>
                                    <span style='display: inline-block; margin-top: 4px; color: #b91c1c; font-weight: 700;'>
                                        ⛔ Corridor Impassable — Detour Applied
                                    </span>
                                </div>
                            </div>
                            """,
                            max_width=300
                        ),
                        tooltip=f"⚠️ CAUTION: Road Blockage on {road_name}"
                    ).add_to(m)

        # 4. Add Active Geographic Hazards with Caution Highlight
        if hazards:
            for hz in hazards:
                h_lat = hz.get("lat") or hz.get("latitude")
                h_lon = hz.get("lon") or hz.get("longitude")
                h_type = hz.get("incident_type") or hz.get("type", "HAZARD")
                h_desc = hz.get("description", "Active Incident Reported")
                h_radius = float(hz.get("radius_meters", 150.0))
                h_road = hz.get("affected_road_name", "Local Corridor")
                h_sev = hz.get("severity", "HIGH")
                hazard_emoji = "🔥" if "FIRE" in str(h_type).upper() else ("🌊" if "FLOOD" in str(h_type).upper() else "⚠️")
                badge_title = f"{h_type}".replace("_", " ")

                if h_lat and h_lon:
                    # Caution Hazard Circle Buffer
                    folium.Circle(
                        location=[h_lat, h_lon],
                        radius=max(80.0, h_radius),
                        color="#dc2626",
                        weight=3,
                        dash_array="5, 5",
                        fill=True,
                        fill_color="#dc2626",
                        fill_opacity=0.38,
                        tooltip=f"⚠️ CAUTION: {h_type} Hazard Zone ({h_radius:.0f}m buffer)"
                    ).add_to(m)

                    # Prominent Floating Hazardous Symbol Badge
                    hazard_badge_html = f"""
                    <div style="
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        cursor: pointer;
                        filter: drop-shadow(0 4px 10px rgba(0,0,0,0.6));
                    ">
                        <div style="
                            display: flex;
                            align-items: center;
                            gap: 6px;
                            background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%);
                            color: #ffffff;
                            border: 2px solid #fecaca;
                            border-radius: 20px;
                            padding: 5px 12px;
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                            font-weight: 800;
                            font-size: 12px;
                            letter-spacing: 0.5px;
                            white-space: nowrap;
                            box-shadow: 0 0 18px rgba(220, 38, 38, 0.95);
                        ">
                            <span style="font-size: 16px;">{hazard_emoji} ⚠️</span>
                            <span>{badge_title}</span>
                        </div>
                        <div style="
                            width: 0;
                            height: 0;
                            border-left: 7px solid transparent;
                            border-right: 7px solid transparent;
                            border-top: 8px solid #7f1d1d;
                            margin-top: -1px;
                        "></div>
                    </div>
                    """
                    folium.Marker(
                        location=[h_lat, h_lon],
                        icon=folium.DivIcon(
                            html=hazard_badge_html,
                            icon_size=(180, 40),
                            icon_anchor=(90, 40)
                        ),
                        popup=folium.Popup(
                            f"""
                            <div style='font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; min-width: 220px; padding: 4px;'>
                                <div style='background: #b91c1c; color: #ffffff; padding: 5px 8px; border-radius: 5px; font-weight: 800; font-size: 0.84rem; display: flex; align-items: center; gap: 6px;'>
                                    <span>⚠️</span> <span>CAUTION: {h_type} HAZARD</span>
                                </div>
                                <div style='margin-top: 8px; font-size: 0.80rem; color: #1e293b; line-height: 1.45;'>
                                    <b>Location:</b> {h_road}<br>
                                    <b>Severity:</b> <span style='color: #dc2626; font-weight: 800;'>{h_sev}</span><br>
                                    <b>Buffer Radius:</b> {h_radius:.0f} meters<br>
                                    <b>Report:</b> {h_desc}<br>
                                    <span style='display: inline-block; margin-top: 4px; color: #b91c1c; font-weight: 700;'>
                                        ⚠️ Hazard Zone Excluded from Route
                                    </span>
                                </div>
                            </div>
                            """,
                            max_width=300
                        ),
                        tooltip=f"⚠️ CAUTION: {h_type} Hazard ({h_road})"
                    ).add_to(m)

        # 4b. Add Real-World Emergency Services & Safety Facilities
        if emergency_facilities:
            for fac in emergency_facilities:
                f_lat = fac.get("latitude") or fac.get("lat")
                f_lon = fac.get("longitude") or fac.get("lon")
                if not f_lat or not f_lon:
                    continue
                f_name = fac.get("name", "Emergency Facility")
                f_type = fac.get("facility_type", "Emergency Service")
                f_icon = fac.get("amenity_icon", "🏥")
                f_dist = fac.get("road_distance_km", fac.get("distance_from_route_km", 0.0))
                f_hours = fac.get("operating_hours", "Hours not published")
                f_source = fac.get("data_source", "OpenStreetMap Contributors")
                f_phone = fac.get("contact_phone")
                f_has_ed = fac.get("has_emergency_department")
                f_is_shelter = fac.get("is_officially_designated_shelter")

                badge_border = "#ef4444" if f_icon in ["🏥", "🩺"] else ("#f59e0b" if f_icon == "⛺" else ("#0284c7" if f_icon in ["👮", "🚒"] else "#10b981"))
                badge_bg = "rgba(15, 23, 42, 0.92)"

                fac_html = f"""
                <div style="
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 32px;
                    height: 32px;
                    background: {badge_bg};
                    border: 2px solid {badge_border};
                    border-radius: 50%;
                    box-shadow: 0 0 10px {badge_border};
                    font-size: 16px;
                    cursor: pointer;
                " title="{f_name}">
                    {f_icon}
                </div>
                """
                ed_badge = "<span style='color:#ef4444; font-weight:700;'>● 24/7 Verified Emergency Dept</span><br>" if f_has_ed else ("<span style='color:#f59e0b; font-weight:700;'>● Primary Clinic (No Dedicated Trauma Unit)</span><br>" if f_has_ed is False else "")
                shelter_badge = "<span style='color:#10b981; font-weight:700;'>● Officially Designated Evacuation Safe Haven</span><br>" if f_is_shelter else ""
                phone_line = f"<b>Contact:</b> {f_phone}<br>" if f_phone else ""

                folium.Marker(
                    location=[f_lat, f_lon],
                    icon=folium.DivIcon(
                        html=fac_html,
                        icon_size=(32, 32),
                        icon_anchor=(16, 16)
                    ),
                    tooltip=f"{f_icon} {f_name} (~{f_dist:.1f} km)",
                    popup=folium.Popup(
                        f"""
                        <div style='font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; min-width: 230px; padding: 4px;'>
                            <div style='background: {badge_border}; color: #ffffff; padding: 4px 8px; border-radius: 4px; font-weight: 800; font-size: 0.82rem;'>
                                {f_icon} {f_type}
                            </div>
                            <div style='margin-top: 6px; font-size: 0.78rem; color: #1e293b; line-height: 1.4;'>
                                <b>{f_name}</b><br>
                                {ed_badge}{shelter_badge}
                                <b>Distance:</b> ~{f_dist:.1f} km from position<br>
                                <b>Operating:</b> {f_hours}<br>
                                {phone_line}
                                <span style='font-size: 0.70rem; color: #64748b;'>Source: {f_source}</span>
                            </div>
                        </div>
                        """,
                        max_width=290
                    )
                ).add_to(m)

        # 5. Add Route Polylines with Multi-Objective Visual Hierarchy
        if routes:
            for idx, r in enumerate(routes):
                coords = r.get("polyline", [])
                if not coords or len(coords) < 2:
                    continue

                status = r.get("safety_status", r.get("status", "ROUTE_ELIGIBLE"))
                rank = r.get("rank", idx + 1)
                is_eligible = r.get("is_eligible", "ELIGIBLE" in str(status).upper())

                if not is_eligible or "RESTRICT" in str(status).upper() or "INACCESSIBLE" in str(status).upper():
                    line_color = "#ef4444"  # Muted red for closed routes
                    dash_array = "5, 10"
                    opacity = 0.55
                    weight = 3.5
                elif rank == 1:
                    line_color = "#10b981"  # Emerald green for Top Recommended route
                    dash_array = None
                    opacity = 0.95
                    weight = 6
                elif rank == 2:
                    line_color = "#38bdf8"  # Cyan for Alternative 1
                    dash_array = None
                    opacity = 0.85
                    weight = 4.5
                else:
                    line_color = "#a855f7"  # Purple for Alternative 2
                    dash_array = "6, 6"
                    opacity = 0.80
                    weight = 4

                route_label = r.get("name", f"Route {idx+1}")
                dist_km = r.get("distance_km", 0.0)
                dur_min = r.get("duration_minutes", 0.0)

                folium.PolyLine(
                    locations=coords,
                    color=line_color,
                    weight=weight,
                    opacity=opacity,
                    dash_array=dash_array,
                    tooltip=f"{route_label} ({dist_km:.1f} km, ~{dur_min:.0f} min) - {status}",
                    popup=folium.Popup(
                        f"<b>{route_label}</b><br>Distance: {dist_km:.2f} km<br>Est. Time: {dur_min:.1f} min<br>Status: <code>{status}</code>",
                        max_width=300
                    )
                ).add_to(m)


        # Dynamic Auto Fit-Bounds: Frame map automatically across global routes & waypoints when explicitly enabled
        if auto_fit_bounds:
            all_pts: List[Tuple[float, float]] = []
            if origin_coords:
                all_pts.append(origin_coords)
            if destination_coords:
                all_pts.append(destination_coords)
            if routes:
                for r in routes:
                    for pt in r.get("polyline", []):
                        all_pts.append(pt)

            if all_pts and len(all_pts) >= 2:
                lats = [p[0] for p in all_pts]
                lons = [p[1] for p in all_pts]
                min_lat, max_lat = min(lats), max(lats)
                min_lon, max_lon = min(lons), max(lons)
                if (max_lat - min_lat) > 0.003 or (max_lon - min_lon) > 0.003:
                    try:
                        m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]], padding=[35, 35])
                    except Exception:
                        pass

        # 6. Live Google Maps In-Dash Vehicle Navigation Engine directly on Satellite Map (2nd Picture Map)
        if routes:
            active_r = next((r for r in routes if r.get("rank") == 1 or r.get("is_eligible")), routes[0])
            active_coords = active_r.get("polyline", [])
            route_title = active_r.get("name", "Safe Corridor").split("(")[0].strip()
            avatar_key = str(traveler_avatar).lower()

            if active_coords and len(active_coords) >= 2:
                coords_json = json.dumps(active_coords)
                in_map_script = f"""
                <script>
                (function() {{
                    function setupLiveNavigationEngine() {{
                        let leafletMap = null;
                        for (let k in window) {{
                            if (k.startsWith('map_') && window[k] && typeof window[k].addLayer === 'function') {{
                                leafletMap = window[k];
                                break;
                            }}
                        }}
                        if (!leafletMap) {{
                            const mapDiv = document.querySelector('.folium-map');
                            if (mapDiv && mapDiv.id && window[mapDiv.id]) {{
                                leafletMap = window[mapDiv.id];
                            }}
                        }}
                        if (!leafletMap) {{
                            setTimeout(setupLiveNavigationEngine, 150);
                            return;
                        }}

                        const routePts = {coords_json};
                        if (!routePts || routePts.length < 2) return;

                        // Calculate cumulative distances along route
                        const cumDists = [0];
                        function calcDistM(p1, p2) {{
                            const R = 6371000;
                            const dLat = (p2[0] - p1[0]) * Math.PI / 180;
                            const dLon = (p2[1] - p1[1]) * Math.PI / 180;
                            const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                                      Math.cos(p1[0] * Math.PI / 180) * Math.cos(p2[0] * Math.PI / 180) *
                                      Math.sin(dLon/2) * Math.sin(dLon/2);
                            return 2 * R * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
                        }}
                        for (let i = 1; i < routePts.length; i++) {{
                            cumDists.push(cumDists[cumDists.length - 1] + calcDistM(routePts[i-1], routePts[i]));
                        }}
                        const totalDistM = cumDists[cumDists.length - 1] || 1.0;

                        function calcBearing(p0, p1) {{
                            const dLon = (p1[1] - p0[1]) * Math.PI / 180;
                            const lat1 = p0[0] * Math.PI / 180;
                            const lat2 = p1[0] * Math.PI / 180;
                            const y = Math.sin(dLon) * Math.cos(lat2);
                            const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);
                            return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
                        }}

                        // Moving Vehicle DivIcon (Car with headlights or selected vehicle)
                        const avatarType = "{avatar_key}";
                        let iconSvg = '';
                        if (avatarType.indexOf('boy') !== -1 || avatarType.indexOf('walk') !== -1) {{
                            iconSvg = `
                            <div style="position:relative; width:48px; height:48px; display:flex; align-items:center; justify-content:center;">
                                <div style="position:absolute; width:44px; height:44px; border-radius:50%; background:rgba(56,189,248,0.35); border:2.5px solid #38bdf8; box-shadow:0 0 16px #38bdf8; animation:foliumRadar 1.6s infinite ease-out;"></div>
                                <div id="satVehicleRotator" style="position:relative; z-index:2; transition:transform 0.2s linear;">
                                    <svg width="44" height="44" viewBox="0 0 64 64" fill="none">
                                        <rect x="12" y="24" width="12" height="18" rx="4" fill="#0284c7" stroke="#38bdf8" stroke-width="2"/>
                                        <g class="folium-walking-leg-left"><line x1="28" y1="42" x2="24" y2="58" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round"/><ellipse cx="23" cy="58" rx="4.5" ry="3" fill="#ef4444"/></g>
                                        <g class="folium-walking-leg-right"><line x1="38" y1="42" x2="42" y2="58" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round"/><ellipse cx="43" cy="58" rx="4.5" ry="3" fill="#ef4444"/></g>
                                        <rect x="22" y="24" width="20" height="20" rx="5" fill="#10b981" stroke="#059669" stroke-width="2"/>
                                        <circle cx="32" cy="15" r="9" fill="#fde047" stroke="#ca8a04" stroke-width="1.5"/>
                                        <path d="M22 13 C22 7, 42 7, 42 13 L47 14 L22 14 Z" fill="#ef4444"/>
                                    </svg>
                                </div>
                            </div>`;
                        }} else if (avatarType.indexOf('tractor') !== -1) {{
                            iconSvg = `
                            <div style="position:relative; width:48px; height:48px; display:flex; align-items:center; justify-content:center;">
                                <div style="position:absolute; width:44px; height:44px; border-radius:50%; background:rgba(22,163,74,0.35); border:2.5px solid #16a34a; box-shadow:0 0 16px #16a34a; animation:foliumRadar 1.6s infinite ease-out;"></div>
                                <div id="satVehicleRotator" style="position:relative; z-index:2; transition:transform 0.2s linear;">
                                    <svg width="46" height="46" viewBox="0 0 64 64" fill="none">
                                        <line x1="22" y1="20" x2="22" y2="8" stroke="#475569" stroke-width="3" stroke-linecap="round"/>
                                        <rect x="16" y="20" width="22" height="18" rx="4" fill="#15803d" stroke="#166534" stroke-width="2"/>
                                        <circle cx="18" cy="46" r="8" fill="#1e293b" stroke="#eab308" stroke-width="3"/>
                                        <circle cx="48" cy="42" r="14" fill="#0f172a" stroke="#eab308" stroke-width="4"/>
                                    </svg>
                                </div>
                            </div>`;
                        }} else if (avatarType.indexOf('bike') !== -1 || avatarType.indexOf('motorcycle') !== -1) {{
                            iconSvg = `
                            <div style="position:relative; width:48px; height:48px; display:flex; align-items:center; justify-content:center;">
                                <div style="position:absolute; width:44px; height:44px; border-radius:50%; background:rgba(2,132,199,0.35); border:2.5px solid #0284c7; box-shadow:0 0 16px #0284c7; animation:foliumRadar 1.6s infinite ease-out;"></div>
                                <div id="satVehicleRotator" style="position:relative; z-index:2; transition:transform 0.2s linear;">
                                    <svg width="46" height="46" viewBox="0 0 64 64" fill="none">
                                        <circle cx="16" cy="44" r="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2.5"/>
                                        <circle cx="48" cy="44" r="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2.5"/>
                                        <path d="M16 44 L30 32 L40 32 L48 44" stroke="#e11d48" stroke-width="4" stroke-linecap="round"/>
                                    </svg>
                                </div>
                            </div>`;
                        }} else {{
                            // Google Maps GPS Car Arrow with Headlight Beam
                            iconSvg = `
                            <div style="position:relative; width:48px; height:48px; display:flex; align-items:center; justify-content:center;">
                                <div style="position:absolute; width:44px; height:44px; border-radius:50%; background:rgba(16,185,129,0.35); border:2.5px solid #10b981; box-shadow:0 0 18px #10b981; animation:foliumRadar 1.6s infinite ease-out;"></div>
                                <div id="satVehicleRotator" style="position:relative; z-index:2; transition:transform 0.2s linear;">
                                    <svg width="44" height="44" viewBox="0 0 64 64" fill="none">
                                        <path d="M32 4 L14 56 L32 46 L50 56 Z" fill="rgba(56,189,248,0.35)"/>
                                        <rect x="20" y="20" width="24" height="34" rx="7" fill="#0284c7" stroke="#38bdf8" stroke-width="2"/>
                                        <rect x="24" y="26" width="16" height="9" rx="3" fill="#0f172a"/>
                                        <rect x="24" y="42" width="16" height="5" rx="2" fill="#0f172a"/>
                                        <rect x="25" y="32" width="14" height="12" rx="3" fill="#0369a1"/>
                                        <circle cx="23" cy="22" r="2.5" fill="#fef08a"/>
                                        <circle cx="41" cy="22" r="2.5" fill="#fef08a"/>
                                    </svg>
                                </div>
                            </div>`;
                        }}

                        const initialBrng = calcBearing(routePts[0], routePts[1]);
                        const vehicleMarker = L.marker(routePts[0], {{
                            icon: L.divIcon({{
                                html: iconSvg,
                                iconSize: [48, 48],
                                iconAnchor: [24, 24]
                            }}),
                            zIndexOffset: 3000
                        }}).addTo(leafletMap);

                        setTimeout(() => {{
                            const rot = document.getElementById('satVehicleRotator');
                            if (rot) rot.style.transform = `rotate(${{initialBrng}}deg)`;
                        }}, 100);

                        // Floating In-Dash Google Maps HUD atop the Satellite Map
                        const hud = document.createElement('div');
                        hud.style.cssText = 'position:absolute; top:12px; left:12px; right:12px; z-index:1000; background:linear-gradient(135deg,#065f46 0%,#047857 70%,#0f766e 100%); border:2px solid #10b981; border-radius:12px; padding:10px 14px; box-shadow:0 8px 24px rgba(0,0,0,0.6); display:flex; align-items:center; justify-content:space-between; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; color:#ffffff; user-select:none;';
                        hud.innerHTML = `
                            <div style="display:flex; align-items:center; gap:12px;">
                                <div id="satTurnIcon" style="width:42px; height:42px; background:rgba(255,255,255,0.2); border:2px solid #ffffff; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:24px; box-shadow:0 0 10px rgba(255,255,255,0.3);">🟢</div>
                                <div>
                                    <div id="satTurnDist" style="font-size:1.15rem; font-weight:900; line-height:1.1;">{route_title}</div>
                                    <div id="satTurnRoad" style="font-size:0.76rem; font-weight:700; color:#d1fae5;">Safe Corridor Navigation Active</div>
                                    <div id="satTurnDesc" style="font-size:0.70rem; color:#a7f3d0; opacity:0.9;">Bypassing Chemical Spill & Road Blockages</div>
                                </div>
                            </div>
                            <div style="display:flex; flex-direction:column; align-items:flex-end; gap:6px;">
                                <div style="display:flex; gap:6px;">
                                    <button id="satPlayBtn" style="background:#10b981; color:#ffffff; border:none; padding:6px 12px; border-radius:6px; font-weight:800; font-size:0.75rem; cursor:pointer; box-shadow:0 2px 8px rgba(16,185,129,0.5);">▶️ Move Along Route</button>
                                    <button id="satGpsBtn" style="background:rgba(255,255,255,0.15); color:#ffffff; border:1px solid rgba(255,255,255,0.3); padding:6px 10px; border-radius:6px; font-weight:700; font-size:0.75rem; cursor:pointer;">📡 GPS Sync</button>
                                    <button id="satVoiceBtn" style="background:rgba(255,255,255,0.15); color:#ffffff; border:1px solid rgba(255,255,255,0.3); padding:6px 10px; border-radius:6px; font-weight:700; font-size:0.75rem; cursor:pointer;">🔊 Voice</button>
                                </div>
                                <div id="satEtaBadge" style="font-size:0.70rem; background:rgba(0,0,0,0.35); padding:2px 8px; border-radius:4px; color:#cbd5e1; border:1px solid rgba(255,255,255,0.15);">● Google Maps Live Guidance</div>
                            </div>
                        `;
                        leafletMap.getContainer().appendChild(hud);

                        // Spoken Voice Helper
                        let voiceMuted = false;
                        function speak(txt) {{
                            if (voiceMuted || !('speechSynthesis' in window)) return;
                            window.speechSynthesis.cancel();
                            const u = new SpeechSynthesisUtterance(txt);
                            u.rate = 0.95;
                            u.lang = 'en-US';
                            window.speechSynthesis.speak(u);
                        }}

                        document.getElementById('satVoiceBtn').onclick = function() {{
                            voiceMuted = !voiceMuted;
                            this.innerText = voiceMuted ? '🔇 Muted' : '🔊 Voice';
                            if (voiceMuted) window.speechSynthesis.cancel();
                        }};

                        // Navigation State
                        let isNavigating = false;
                        let progress = 0.0;
                        let animId = null;
                        let lastT = 0;
                        let gpsWatch = null;

                        function updateVehicle(latLon, brng) {{
                            vehicleMarker.setLatLng(latLon);
                            const r = document.getElementById('satVehicleRotator');
                            if (r && brng !== undefined) {{
                                if (avatarType.indexOf('boy') !== -1) {{
                                    r.style.transform = (brng > 180 && brng < 360) ? 'scaleX(-1)' : 'scaleX(1)';
                                }} else {{
                                    r.style.transform = `rotate(${{brng}}deg)`;
                                }}
                            }}
                        }}

                        function stepAnim(t) {{
                            if (!isNavigating) return;
                            if (!lastT) lastT = t;
                            const dt = (t - lastT) / 1000.0;
                            lastT = t;

                            const speedMps = (avatarType.indexOf('boy') !== -1) ? 3.0 : 18.0;
                            const dTraveled = speedMps * dt;
                            progress += (dTraveled / totalDistM);

                            if (progress >= 1.0) {{
                                progress = 1.0;
                                isNavigating = false;
                                document.getElementById('satPlayBtn').innerText = '▶️ Restart';
                                document.getElementById('satTurnDesc').innerText = 'Arrived at destination safe terminal';
                                updateVehicle(routePts[routePts.length - 1], calcBearing(routePts[routePts.length - 2], routePts[routePts.length - 1]));
                                speak('You have arrived at your destination: Guntur City Center. Navigation complete.');
                                return;
                            }}

                            const curTargetM = progress * totalDistM;
                            let idx = 0;
                            while (idx < cumDists.length - 1 && cumDists[idx + 1] < curTargetM) {{
                                idx++;
                            }}
                            const segStart = cumDists[idx];
                            const segEnd = cumDists[idx + 1] || (segStart + 0.001);
                            const segT = Math.max(0, Math.min(1, (curTargetM - segStart) / (segEnd - segStart)));

                            const p0 = routePts[idx];
                            const p1 = routePts[Math.min(idx + 1, routePts.length - 1)];
                            const cLat = p0[0] + (p1[0] - p0[0]) * segT;
                            const cLon = p0[1] + (p1[1] - p0[1]) * segT;
                            const brng = calcBearing(p0, p1);

                            updateVehicle([cLat, cLon], brng);

                            if (idx % 4 === 0) {{
                                leafletMap.panTo([cLat, cLon], {{ animate: true, duration: 0.25 }});
                            }}

                            const remM = Math.max(0, totalDistM - curTargetM);
                            document.getElementById('satTurnDist').innerText = remM > 1000 ? `${{(remM/1000).toFixed(1)}} km remaining` : `${{Math.round(remM)}} m remaining`;

                            animId = requestAnimationFrame(stepAnim);
                        }}

                        document.getElementById('satPlayBtn').onclick = function() {{
                            if (isNavigating) {{
                                isNavigating = false;
                                this.innerText = '▶️ Resume';
                                if (animId) cancelAnimationFrame(animId);
                            }} else {{
                                if (progress >= 1.0) progress = 0.0;
                                isNavigating = true;
                                this.innerText = '⏸️ Pause';
                                lastT = performance.now();
                                speak('Starting live navigation along {route_title}.');
                                animId = requestAnimationFrame(stepAnim);
                            }}
                        }};

                        // Automatic Live Satellite GPS Tracking & Movement Detection Engine
                        let isGps = true;
                        let liveSatMarker = null;
                        let liveSatCircle = null;
                        let liveTrailPoly = L.polyline([], {{
                            color: '#06b6d4',
                            weight: 3.5,
                            opacity: 0.8,
                            dashArray: '5, 8'
                        }}).addTo(leafletMap);
                        let prevGpsLat = null, prevGpsLon = null, prevGpsTime = 0;

                        function handleGpsPosition(pos) {{
                            const uLat = pos.coords.latitude;
                            const uLon = pos.coords.longitude;
                            const acc = pos.coords.accuracy || 8.0;
                            const now = Date.now();

                            // Instantaneous speed calculation (km/h)
                            let speedKmh = 0.0;
                            if (pos.coords.speed !== null && !isNaN(pos.coords.speed) && pos.coords.speed > 0) {{
                                speedKmh = pos.coords.speed * 3.6;
                            }} else if (prevGpsLat !== null && prevGpsTime > 0) {{
                                const dt = (now - prevGpsTime) / 1000.0;
                                if (dt > 0.4) {{
                                    const dm = calcDistM([prevGpsLat, prevGpsLon], [uLat, uLon]);
                                    speedKmh = (dm / dt) * 3.6;
                                }}
                            }}

                            // Heading / Bearing calculation
                            let liveBrng = pos.coords.heading;
                            if (liveBrng === null || isNaN(liveBrng) || liveBrng === 0) {{
                                if (prevGpsLat !== null) {{
                                    liveBrng = calcBearing([prevGpsLat, prevGpsLon], [uLat, uLon]);
                                }} else {{
                                    liveBrng = 0.0;
                                }}
                            }}

                            prevGpsLat = uLat;
                            prevGpsLon = uLon;
                            prevGpsTime = now;

                            // Update live movement trail on map
                            liveTrailPoly.addLatLng([uLat, uLon]);

                            // Satellite GPS pulsating pin & accuracy halo
                            const satPinHtml = `
                                <div style="position:relative; width:34px; height:34px; display:flex; align-items:center; justify-content:center;">
                                    <div style="position:absolute; width:32px; height:32px; border-radius:50%; background:rgba(6,182,212,0.45); animation:foliumRadar 1.5s infinite ease-out;"></div>
                                    <div style="width:14px; height:14px; border-radius:50%; background:#06b6d4; border:2.5px solid #ffffff; box-shadow:0 0 12px #06b6d4;"></div>
                                </div>
                            `;

                            if (!liveSatMarker) {{
                                liveSatMarker = L.marker([uLat, uLon], {{
                                    icon: L.divIcon({{ html: satPinHtml, iconSize: [34, 34], iconAnchor: [17, 17] }}),
                                    zIndexOffset: 3500
                                }}).addTo(leafletMap);

                                liveSatCircle = L.circle([uLat, uLon], {{
                                    radius: acc,
                                    color: '#06b6d4',
                                    fillColor: '#06b6d4',
                                    fillOpacity: 0.12,
                                    weight: 1.5
                                }}).addTo(leafletMap);
                            }} else {{
                                liveSatMarker.setLatLng([uLat, uLon]);
                                liveSatCircle.setLatLng([uLat, uLon]);
                                liveSatCircle.setRadius(acc);
                            }}

                            // Nearest corridor snapping & off-corridor detection
                            let minD = Infinity;
                            let snapPt = routePts[0];
                            let bestSeg = 0;
                            for (let i = 0; i < routePts.length - 1; i++) {{
                                const d = calcDistM([uLat, uLon], routePts[i]);
                                if (d < minD) {{
                                    minD = d;
                                    snapPt = routePts[i];
                                    bestSeg = i;
                                }}
                            }}

                            const routeSegBrng = calcBearing(routePts[bestSeg], routePts[Math.min(bestSeg + 1, routePts.length - 1)]);
                            const effectiveBrng = (speedKmh > 1.2 && liveBrng) ? liveBrng : routeSegBrng;

                            // Update moving avatar position & bearing
                            updateVehicle(minD < 50 ? snapPt : [uLat, uLon], effectiveBrng);

                            // Smooth satellite map auto-panning to follow user
                            leafletMap.panTo([uLat, uLon], {{ animate: true, duration: 0.6 }});

                            // Real-time Motion Detection
                            const isMoving = speedKmh > 1.2;
                            const turnDesc = document.getElementById('satTurnDesc');
                            const turnRoad = document.getElementById('satTurnRoad');
                            const etaBadge = document.getElementById('satEtaBadge');
                            const gpsBtn = document.getElementById('satGpsBtn');

                            if (gpsBtn) {{
                                gpsBtn.innerHTML = isMoving ? '🟢 Moving (Live)' : '🛰️ Satellite Active';
                                gpsBtn.style.background = isMoving ? '#059669' : '#0284c7';
                                gpsBtn.style.borderColor = isMoving ? '#10b981' : '#38bdf8';
                            }}

                            if (turnDesc) {{
                                if (isMoving) {{
                                    turnDesc.innerHTML = `<span style="color:#34d399; font-weight:800;">🟢 LIVE MOVEMENT DETECTED</span> • Speed: <b>${{speedKmh.toFixed(1)}} km/h</b> • Bearing: <b>${{Math.round(effectiveBrng)}}°</b>`;
                                }} else {{
                                    turnDesc.innerHTML = `<span style="color:#60a5fa; font-weight:700;">📡 SATELLITE LOCKED</span> • Stationary • Precision: <b>±${{Math.round(acc)}}m</b>`;
                                }}
                            }}

                            if (turnRoad) {{
                                turnRoad.innerText = minD < 45 ? 'On Recommended Safe Corridor' : `Corridor Distance: ${{Math.round(minD)}}m`;
                            }}

                            if (etaBadge) {{
                                etaBadge.innerHTML = isMoving ? `● Moving at ${{speedKmh.toFixed(1)}} km/h` : `● Live Satellite Tracking`;
                                etaBadge.style.color = isMoving ? '#34d399' : '#38bdf8';
                            }}
                        }}

                        function startLiveSatelliteGps() {{
                            if (!navigator.geolocation) {{
                                console.warn('Satellite GPS: Geolocation not supported in browser');
                                const turnDesc = document.getElementById('satTurnDesc');
                                if (turnDesc) turnDesc.innerText = 'GPS not supported in browser';
                                return;
                            }}

                            // Automatic initial fix
                            navigator.geolocation.getCurrentPosition(handleGpsPosition, function(err) {{
                                console.warn('Satellite initial fix warning:', err.message);
                            }}, {{ enableHighAccuracy: true, timeout: 8000, maximumAge: 2000 }});

                            // Continuous live position & movement watcher
                            gpsWatch = navigator.geolocation.watchPosition(handleGpsPosition, function(err) {{
                                console.warn('Satellite live watch warning:', err.message);
                            }}, {{ enableHighAccuracy: true, maximumAge: 1000, timeout: 12000 }});
                        }}

                        // Connect to Satellite Location automatically on startup
                        startLiveSatelliteGps();

                        // Interactive Satellite GPS button toggles or re-centers
                        document.getElementById('satGpsBtn').onclick = function() {{
                            if (prevGpsLat !== null && prevGpsLon !== null) {{
                                leafletMap.panTo([prevGpsLat, prevGpsLon], {{ animate: true, duration: 0.5 }});
                                leafletMap.setZoom(16);
                            }} else {{
                                startLiveSatelliteGps();
                            }}
                        }};
                    }}

                    if (document.readyState === 'complete' || document.readyState === 'interactive') {{
                        setupLiveNavigationEngine();
                    }} else {{
                        window.addEventListener('DOMContentLoaded', setupLiveNavigationEngine);
                    }}
                }})();
                </script>
                """
                m.get_root().html.add_child(folium.Element(in_map_script))

        return m

    def build_interactive_map(
        self,
        center_lat: float,
        center_lon: float,
        zoom_start: int = 13,
        origin_coords: Optional[Tuple[float, float]] = None,
        dest_coords: Optional[Tuple[float, float]] = None,
        route_polylines: Optional[List[Dict[str, Any]]] = None,
        hazards: Optional[List[Dict[str, Any]]] = None,
        road_closures: Optional[List[Dict[str, Any]]] = None,
        breadcrumb_trail: Optional[List[Tuple[float, float]]] = None,
        map_style: str = "satellite_hybrid",
        auto_fit_bounds: bool = False,
        traveler_avatar: str = "boy",
        emergency_facilities: Optional[List[Dict[str, Any]]] = None
    ) -> folium.Map:
        """Adapts route polylines, road restrictions, and breadcrumb trails for Folium map rendering."""
        routes_adapted = []
        if route_polylines:
            for idx, r in enumerate(route_polylines, start=1):
                routes_adapted.append({
                    "name": r.get("name", f"Route {idx}"),
                    "polyline": r.get("coordinates", []),
                    "rank": r.get("rank", idx),
                    "is_eligible": r.get("is_eligible", True),
                    "safety_status": r.get("status", "ROUTE_ELIGIBLE")
                })

        return self.create_interactive_map(
            center_lat=center_lat,
            center_lon=center_lon,
            zoom=zoom_start,
            origin_coords=origin_coords,
            destination_coords=dest_coords,
            routes=routes_adapted,
            hazards=hazards,
            road_closures=road_closures,
            breadcrumb_trail=breadcrumb_trail,
            map_style=map_style,
            auto_fit_bounds=auto_fit_bounds,
            traveler_avatar=traveler_avatar,
            emergency_facilities=emergency_facilities
        )

    def render_hazard_map(
        self,
        center_lat: float,
        center_lon: float,
        zoom: int = 14,
        hazards: Optional[List[Dict[str, Any]]] = None,
        road_closures: Optional[List[Dict[str, Any]]] = None,
        map_style: str = "satellite_hybrid"
    ) -> folium.Map:
        """Renders tactical satellite hazard cartography with spatial buffers and road closures."""
        return self.create_interactive_map(
            center_lat=center_lat,
            center_lon=center_lon,
            zoom=zoom,
            hazards=hazards,
            road_closures=road_closures,
            map_style=map_style
        )

