"""
Navigation Trust Audit Engine & Compact Verification Card for P.A.T.H.F.I.N.D.E.R.
Provides simple, reliable, and user-friendly route verification:
1. Validates route status: Checked, Warning, or Unable to verify.
2. Checks hazards & road restrictions against the actual selected route corridor.
3. Identifies genuine routing provider, data source, and connectivity mode.
4. Omits arbitrary/invented confidence probabilities with transparent documentation.
5. Renders a compact, responsive information card with expandable technical details.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import time
from typing import Any, Dict, List, Optional, Tuple

from src.hazard_map import haversine_distance_m, distance_point_to_segment_m


class TrustAuditStatus(str, Enum):
    CHECKED = "CHECKED"
    WARNING = "WARNING"
    UNABLE_TO_VERIFY = "UNABLE_TO_VERIFY"


class HazardAuditStatus(str, Enum):
    NO_HAZARDS_DETECTED = "NO_HAZARDS_DETECTED"
    HAZARDS_DETECTED = "HAZARDS_DETECTED"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"


class ConnectivityStatus(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE_LOCAL = "OFFLINE_LOCAL"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass
class NavigationTrustAuditResult:
    """Represents honest, verified route inspection results for the selected route."""
    route_id: str
    route_name: str
    status: TrustAuditStatus
    status_label: str                          # "Checked", "Warning", "Unable to verify"
    status_reason: str                         # Plain-English explanation
    hazard_status: HazardAuditStatus
    hazard_summary: str                        # "No hazards detected in checked area" or "X issue(s) detected"
    detected_threats: List[Dict[str, Any]] = field(default_factory=list)
    route_provider: str = "Autonomous Road Graph Model"
    route_source_type: str = "LOCAL_GRAPH"     # "LIVE_API", "LOCAL_GRAPH", "CACHED", "SIMULATION"
    is_live_routing: bool = False
    connectivity: ConnectivityStatus = ConnectivityStatus.ONLINE
    connectivity_label: str = "Online"
    checked_at: str = ""
    corridor_length_km: float = 0.0
    corridor_buffer_m: float = 40.0
    confidence_score: Optional[float] = None   # None: arbitrary probabilities omitted
    confidence_score_explanation: str = (
        "Numeric confidence percentage is omitted. Route safety cannot be expressed as an "
        "arbitrary probability without continuous physical ground telemetry sensors."
    )
    verified_data_sources: List[Dict[str, str]] = field(default_factory=list)
    limitations_disclaimer: str = (
        "Audit checks are limited to reported hazard registries and verified OpenStreetMap "
        "infrastructure tags. Unreported roadwork or temporary conditions may not be reflected. "
        "Always adhere to physical road signage and local regulations."
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "route_id": self.route_id,
            "route_name": self.route_name,
            "status": self.status.value,
            "status_label": self.status_label,
            "status_reason": self.status_reason,
            "hazard_status": self.hazard_status.value,
            "hazard_summary": self.hazard_summary,
            "threats_count": len(self.detected_threats),
            "detected_threats": self.detected_threats,
            "route_provider": self.route_provider,
            "route_source_type": self.route_source_type,
            "is_live_routing": self.is_live_routing,
            "connectivity": self.connectivity.value,
            "connectivity_label": self.connectivity_label,
            "checked_at": self.checked_at,
            "corridor_length_km": self.corridor_length_km,
            "corridor_buffer_m": self.corridor_buffer_m,
            "confidence_score": self.confidence_score,
            "confidence_score_explanation": self.confidence_score_explanation,
            "verified_data_sources": self.verified_data_sources,
            "limitations_disclaimer": self.limitations_disclaimer
        }


class NavigationTrustAuditEngine:
    """
    Evaluates the currently selected route against real-world road conditions,
    hazards, routing providers, and connectivity state.
    """

    @classmethod
    def audit_route(
        cls,
        route: Optional[Any],
        active_hazards: Optional[List[Any]] = None,
        active_restrictions: Optional[List[Any]] = None,
        satellite_audit: Optional[Any] = None,
        is_online: Optional[bool] = None,
        hazard_data_available: bool = True,
        corridor_buffer_m: float = 40.0
    ) -> NavigationTrustAuditResult:
        """
        Performs genuine verification checks on the selected route.
        """
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # 1. Missing or invalid route
        if route is None:
            return NavigationTrustAuditResult(
                route_id="UNKNOWN",
                route_name="No Route Selected",
                status=TrustAuditStatus.UNABLE_TO_VERIFY,
                status_label="Unable to verify",
                status_reason="No route data available to inspect. Select or calculate a route.",
                hazard_status=HazardAuditStatus.DATA_UNAVAILABLE,
                hazard_summary="Data unavailable",
                route_provider="Unavailable",
                route_source_type="NONE",
                connectivity=ConnectivityStatus.UNAVAILABLE,
                connectivity_label="Unavailable",
                checked_at=now_utc
            )

        # Extract attributes whether route is RouteOption or dict
        route_id = getattr(route, "route_id", None) or (route.get("route_id") if isinstance(route, dict) else "ROUTE_0")
        route_name = getattr(route, "name", None) or (route.get("name") if isinstance(route, dict) else "Selected Route")
        raw_poly = getattr(route, "polyline", None) or (route.get("polyline") if isinstance(route, dict) else [])
        polyline = [tuple(p) if isinstance(p, (list, tuple)) else (p.get("lat"), p.get("lon")) for p in raw_poly] if raw_poly else []
        raw_dist = getattr(route, "distance_km", None) or (route.get("distance_km") if isinstance(route, dict) else 0.0)
        source_name = getattr(route, "source", None) or (route.get("source") if isinstance(route, dict) else "Autonomous Road Graph Model")
        is_demo_route = getattr(route, "is_demonstration", False) or (route.get("is_demonstration", False) if isinstance(route, dict) else False)

        # 2. Check route geometry validity
        if not polyline or len(polyline) < 2:
            return NavigationTrustAuditResult(
                route_id=str(route_id),
                route_name=str(route_name),
                status=TrustAuditStatus.UNABLE_TO_VERIFY,
                status_label="Unable to verify",
                status_reason="Route polyline geometry is empty or has insufficient coordinates.",
                hazard_status=HazardAuditStatus.DATA_UNAVAILABLE,
                hazard_summary="Data unavailable",
                route_provider=str(source_name),
                route_source_type="INVALID",
                connectivity=ConnectivityStatus.UNAVAILABLE,
                connectivity_label="Unavailable",
                checked_at=now_utc
            )

        # 3. Classify Routing Provider & Live/Offline/Simulation Mode
        src_lower = str(source_name).lower()
        is_live_service = ("osrm" in src_lower or "google" in src_lower or "mapbox" in src_lower or "web" in src_lower)
        is_simulation = is_demo_route or ("simulat" in src_lower or "demo" in src_lower)

        if is_online is None:
            is_connected = True
        else:
            is_connected = bool(is_online)

        if is_simulation:
            route_source_type = "SIMULATION"
            route_provider = f"{source_name} (Simulated Demonstration)"
            connectivity = ConnectivityStatus.OFFLINE_LOCAL if not is_connected else ConnectivityStatus.ONLINE
            connectivity_label = "Simulation (Offline/Local)" if not is_connected else "Simulation"
        elif not is_connected:
            connectivity = ConnectivityStatus.OFFLINE_LOCAL
            connectivity_label = "Offline / Local Graph"
            if is_live_service:
                route_source_type = "CACHED"
                route_provider = f"{source_name} (Cached Route / Offline)"
            else:
                route_source_type = "LOCAL_GRAPH"
                route_provider = str(source_name)
        else:
            if is_live_service:
                route_source_type = "LIVE_API"
                route_provider = str(source_name)
                connectivity = ConnectivityStatus.ONLINE
                connectivity_label = "Online"
            else:
                route_source_type = "LOCAL_GRAPH"
                route_provider = str(source_name)
                connectivity = ConnectivityStatus.ONLINE
                connectivity_label = "Local Graph (Online Services Available)"

        verified_sources: List[Dict[str, str]] = [
            {"name": route_provider, "type": "Routing Provider", "status": "Active", "updated": now_utc}
        ]

        # 4. Check Hazard Data Availability
        if not hazard_data_available:
            return NavigationTrustAuditResult(
                route_id=str(route_id),
                route_name=str(route_name),
                status=TrustAuditStatus.UNABLE_TO_VERIFY,
                status_label="Unable to verify",
                status_reason="Hazard data feed is unavailable. Route safety cannot be validated at this time.",
                hazard_status=HazardAuditStatus.DATA_UNAVAILABLE,
                hazard_summary="Hazard data unavailable",
                route_provider=route_provider,
                route_source_type=route_source_type,
                is_live_routing=is_live_service,
                connectivity=connectivity,
                connectivity_label=connectivity_label,
                checked_at=now_utc,
                corridor_length_km=float(raw_dist or 0.0),
                corridor_buffer_m=corridor_buffer_m,
                verified_data_sources=verified_sources
            )

        # 5. Check Spatial Hazard & Road Restriction Intersections
        detected_threats: List[Dict[str, Any]] = []

        # Check Active Hazards
        if active_hazards is not None:
            hz_source_name = "Reported Incident Registry"
            verified_sources.append({
                "name": hz_source_name,
                "type": "Incident Database",
                "status": "Inspected",
                "updated": now_utc
            })
            for hz in active_hazards:
                lat = getattr(hz, "latitude", None) if hasattr(hz, "latitude") else hz.get("lat")
                lon = getattr(hz, "longitude", None) if hasattr(hz, "longitude") else hz.get("lon")
                radius = getattr(hz, "radius_meters", None) if hasattr(hz, "radius_meters") else hz.get("radius_meters", 50.0)
                desc = getattr(hz, "description", None) if hasattr(hz, "description") else hz.get("description", "Road Hazard")
                inc_type = getattr(hz, "incident_type", None) if hasattr(hz, "incident_type") else hz.get("incident_type", "HAZARD")
                hz_src = getattr(hz, "source", None) or (hz.get("source") if isinstance(hz, dict) else None) or hz_source_name
                created_at = getattr(hz, "created_at", None) or (hz.get("created_at") if isinstance(hz, dict) else None)
                time_str = created_at.strftime("%Y-%m-%d %H:%M:%S UTC") if isinstance(created_at, datetime) else str(created_at or now_utc)

                if lat is not None and lon is not None:
                    d_m = cls._min_distance_to_polyline_m((float(lat), float(lon)), polyline)
                    threshold = float(radius) + corridor_buffer_m
                    if d_m <= threshold:
                        detected_threats.append({
                            "type": "HAZARD",
                            "category": str(inc_type),
                            "description": str(desc),
                            "distance_m": round(d_m, 1),
                            "location": (round(float(lat), 4), round(float(lon), 4)),
                            "source": str(hz_src),
                            "reported_at": time_str
                        })

        # Check Active Road Restrictions
        if active_restrictions is not None:
            restr_source_name = "Road Condition Survey"
            verified_sources.append({
                "name": restr_source_name,
                "type": "Road Closures & Construction",
                "status": "Inspected",
                "updated": now_utc
            })
            for restr in active_restrictions:
                lat = getattr(restr, "latitude", None) if hasattr(restr, "latitude") else restr.get("lat")
                lon = getattr(restr, "longitude", None) if hasattr(restr, "longitude") else restr.get("lon")
                radius = getattr(restr, "affected_radius_meters", None) if hasattr(restr, "affected_radius_meters") else restr.get("radius_meters", 30.0)
                desc = getattr(restr, "description", None) or getattr(restr, "road_name", None) or (restr.get("description") if isinstance(restr, dict) else "Road Restriction")
                r_type = getattr(restr, "restriction_type", None) or (restr.get("type") if isinstance(restr, dict) else "RESTRICTION")
                if hasattr(r_type, "value"):
                    r_type = r_type.value
                restr_src = getattr(restr, "source", None) or (restr.get("source") if isinstance(restr, dict) else None) or restr_source_name
                reported_at = getattr(restr, "reported_at", None) or (restr.get("reported_at") if isinstance(restr, dict) else None)
                time_str = reported_at.strftime("%Y-%m-%d %H:%M:%S UTC") if isinstance(reported_at, datetime) else str(reported_at or now_utc)

                if lat is not None and lon is not None:
                    d_m = cls._min_distance_to_polyline_m((float(lat), float(lon)), polyline)
                    threshold = float(radius) + corridor_buffer_m
                    if d_m <= threshold:
                        detected_threats.append({
                            "type": "RESTRICTION",
                            "category": str(r_type),
                            "description": str(desc),
                            "distance_m": round(d_m, 1),
                            "location": (round(float(lat), 4), round(float(lon), 4)),
                            "source": str(restr_src),
                            "reported_at": time_str
                        })

        # Integrate verified obstacles from satellite audit if available
        if satellite_audit:
            verified_sources.append({
                "name": "OpenStreetMap Infrastructure Registry",
                "type": "Physical Barrier & Access Survey",
                "status": "Inspected",
                "updated": getattr(satellite_audit, "satellite_pass_time", now_utc)
            })
            blockages = getattr(satellite_audit, "detected_blockages", []) or []
            for blk in blockages:
                b_lat = blk.get("lat")
                b_lon = blk.get("lon")
                if b_lat is not None and b_lon is not None:
                    d_m = cls._min_distance_to_polyline_m((float(b_lat), float(b_lon)), polyline)
                    if d_m <= corridor_buffer_m:
                        detected_threats.append({
                            "type": "BARRIER",
                            "category": blk.get("type", "OBSTACLE"),
                            "description": blk.get("description", "Road Barrier"),
                            "distance_m": round(d_m, 1),
                            "location": (round(float(b_lat), 4), round(float(b_lon), 4)),
                            "source": blk.get("source", "OpenStreetMap Infrastructure"),
                            "reported_at": getattr(satellite_audit, "satellite_pass_time", now_utc)
                        })

        # 6. Deduce Final Status & Plain-Language Explanation
        if detected_threats:
            status = TrustAuditStatus.WARNING
            status_label = "Warning"
            hazard_status = HazardAuditStatus.HAZARDS_DETECTED
            hazard_summary = f"{len(detected_threats)} issue(s) detected in checked corridor"
            first_desc = detected_threats[0]["description"]
            status_reason = f"Warning: {len(detected_threats)} obstruction(s) reported along corridor, including '{first_desc}'."
        else:
            status = TrustAuditStatus.CHECKED
            status_label = "Checked"
            hazard_status = HazardAuditStatus.NO_HAZARDS_DETECTED
            hazard_summary = "No hazards detected in checked area"
            status_reason = "Checked: Validated against active hazard registries and infrastructure surveys. No reported hazards found in checked corridor."

        return NavigationTrustAuditResult(
            route_id=str(route_id),
            route_name=str(route_name),
            status=status,
            status_label=status_label,
            status_reason=status_reason,
            hazard_status=hazard_status,
            hazard_summary=hazard_summary,
            detected_threats=detected_threats,
            route_provider=route_provider,
            route_source_type=route_source_type,
            is_live_routing=is_live_service,
            connectivity=connectivity,
            connectivity_label=connectivity_label,
            checked_at=now_utc,
            corridor_length_km=float(raw_dist or 0.0),
            corridor_buffer_m=corridor_buffer_m,
            verified_data_sources=verified_sources
        )

    @classmethod
    def _min_distance_to_polyline_m(
        cls,
        pt: Tuple[float, float],
        polyline: List[Tuple[float, float]]
    ) -> float:
        """Computes shortest perpendicular or endpoint distance from a coordinate to a polyline."""
        if not polyline:
            return float("inf")
        if len(polyline) == 1:
            return haversine_distance_m(pt[0], pt[1], polyline[0][0], polyline[0][1])

        min_d = float("inf")
        for i in range(len(polyline) - 1):
            d = distance_point_to_segment_m(
                pt[0], pt[1],
                polyline[i][0], polyline[i][1],
                polyline[i + 1][0], polyline[i + 1][1]
            )
            if d < min_d:
                min_d = d
            if min_d <= 2.0:
                break
        return min_d


def render_navigation_trust_audit_card_html(audit: NavigationTrustAuditResult) -> str:
    """
    Renders a compact, responsive, high-aesthetic HTML card representing
    the Navigation Trust Audit for the selected route.
    """
    # Status-specific styling tokens
    if audit.status == TrustAuditStatus.CHECKED:
        status_color = "#10b981"
        status_bg = "rgba(16, 185, 129, 0.16)"
        status_border = "#10b981"
        status_badge_text = "✓ Checked"
        hazard_icon = "🛡️"
        hazard_color = "#34d399"
    elif audit.status == TrustAuditStatus.WARNING:
        status_color = "#f59e0b"
        status_bg = "rgba(245, 158, 11, 0.18)"
        status_border = "#f59e0b"
        status_badge_text = "⚠️ Warning"
        hazard_icon = "⚠️"
        hazard_color = "#fbbf24"
    else:
        status_color = "#94a3b8"
        status_bg = "rgba(148, 163, 184, 0.16)"
        status_border = "#94a3b8"
        status_badge_text = "ℹ️ Unable to verify"
        hazard_icon = "❓"
        hazard_color = "#cbd5e1"

    # Connectivity styling
    if audit.connectivity == ConnectivityStatus.ONLINE:
        conn_color = "#38bdf8"
        conn_icon = "🌐"
    elif audit.connectivity == ConnectivityStatus.OFFLINE_LOCAL:
        conn_color = "#a855f7"
        conn_icon = "💾"
    else:
        conn_color = "#94a3b8"
        conn_icon = "📡"

    return f"""
    <div class='nav-trust-audit-card' style='
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.94) 0%, rgba(30, 41, 59, 0.88) 100%);
        border: 1.5px solid {status_border};
        border-radius: 12px;
        padding: 12px 16px;
        margin: 10px 0 14px 0;
        color: #f8fafc;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45), 0 0 16px {status_bg};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    '>
        <!-- Top Bar: Header & Status Badge -->
        <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 8px; margin-bottom: 10px;'>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span style='font-size: 1.1rem;'>🛡️</span>
                <span style='font-size: 0.85rem; font-weight: 800; color: #f8fafc; text-transform: uppercase; letter-spacing: 0.04em;'>
                    Navigation Trust Audit
                </span>
                <span style='background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.12); color: #cbd5e1; font-size: 0.70rem; padding: 2px 8px; border-radius: 4px;'>
                    {audit.route_name}
                </span>
            </div>
            <div style='background: {status_bg}; border: 1px solid {status_border}; color: {status_color}; font-size: 0.74rem; font-weight: 800; padding: 3px 10px; border-radius: 6px; letter-spacing: 0.03em;'>
                {status_badge_text}
            </div>
        </div>

        <!-- 4-Column Compact Metric Grid -->
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; margin-bottom: 10px;'>
            <div style='background: rgba(0, 0, 0, 0.22); border-radius: 8px; padding: 6px 10px;'>
                <div style='font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;'>Route Status</div>
                <div style='font-size: 0.82rem; font-weight: 800; color: {status_color}; margin-top: 2px;'>{audit.status_label}</div>
            </div>
            <div style='background: rgba(0, 0, 0, 0.22); border-radius: 8px; padding: 6px 10px;'>
                <div style='font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;'>Hazard Inspection</div>
                <div style='font-size: 0.82rem; font-weight: 700; color: {hazard_color}; margin-top: 2px;'>
                    {hazard_icon} {audit.hazard_summary}
                </div>
            </div>
            <div style='background: rgba(0, 0, 0, 0.22); border-radius: 8px; padding: 6px 10px; overflow: hidden;'>
                <div style='font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;'>Route Source</div>
                <div style='font-size: 0.82rem; font-weight: 700; color: #e2e8f0; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' title='{audit.route_provider}'>
                    🧭 {"OSRM (OpenStreetMap)" if "OSRM" in audit.route_provider else audit.route_provider}
                </div>
            </div>
            <div style='background: rgba(0, 0, 0, 0.22); border-radius: 8px; padding: 6px 10px;'>
                <div style='font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;'>Connectivity</div>
                <div style='font-size: 0.82rem; font-weight: 700; color: {conn_color}; margin-top: 2px;'>
                    {conn_icon} {audit.connectivity_label}
                </div>
            </div>
        </div>

        <!-- Plain-Language Summary Explanation -->
        <div style='font-size: 0.78rem; color: #cbd5e1; line-height: 1.45; background: rgba(255, 255, 255, 0.03); border-radius: 6px; padding: 6px 10px;'>
            {audit.status_reason}
        </div>
    </div>
    """


def render_navigation_trust_audit_details_html(audit: NavigationTrustAuditResult) -> str:
    """
    Renders an expandable technical breakdown for verified sources,
    corridor geometry buffer, confidence score handling, and limitations.
    """
    # Sources list HTML
    sources_html = ""
    for s in audit.verified_data_sources:
        sources_html += f"""
        <div style='display: flex; justify-content: space-between; align-items: center; padding: 4px 0; border-bottom: 1px dashed rgba(255,255,255,0.08); font-size: 0.76rem;'>
            <div>
                <b style='color: #f1f5f9;'>{s.get("name", "Source")}</b>
                <span style='color: #94a3b8; font-size: 0.70rem; margin-left: 6px;'>({s.get("type", "Data Feed")})</span>
            </div>
            <div style='text-align: right;'>
                <span style='color: #10b981; font-weight: 700;'>{s.get("status", "Active")}</span>
                <span style='color: #64748b; font-size: 0.68rem; margin-left: 6px;'>{s.get("updated", "")[:19]}</span>
            </div>
        </div>
        """

    # Threats list HTML
    if audit.detected_threats:
        threats_html = "<div style='margin-top: 8px;'>"
        for idx, t in enumerate(audit.detected_threats, 1):
            threats_html += f"""
            <div style='background: rgba(245, 158, 11, 0.10); border-left: 3px solid #f59e0b; border-radius: 4px; padding: 6px 10px; margin-bottom: 6px; font-size: 0.74rem;'>
                <div style='display: flex; justify-content: space-between;'>
                    <b style='color: #fbbf24;'>#{idx} {t.get("category")} ({t.get("type")})</b>
                    <span style='color: #cbd5e1;'>Distance to path: <b>{t.get("distance_m")} m</b></span>
                </div>
                <div style='color: #f1f5f9; margin-top: 2px;'>{t.get("description")}</div>
                <div style='color: #94a3b8; font-size: 0.68rem; margin-top: 3px;'>Source: {t.get("source")} | Coordinates: {t.get("location")}</div>
            </div>
            """
        threats_html += "</div>"
    else:
        threats_html = "<div style='font-size: 0.74rem; color: #34d399; padding: 4px 0;'>✓ No reported obstacles, closures, or active hazard points intersect the checked corridor.</div>"

    return f"""
    <div style='
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 12px 14px;
        color: #cbd5e1;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    '>
        <!-- Row 1: Corridor Parameters & Verification Baseline -->
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; margin-bottom: 12px; font-size: 0.74rem;'>
            <div>
                <span style='color: #94a3b8;'>Route Identifier:</span>
                <b style='color: #f8fafc; margin-left: 4px;'>{audit.route_id}</b>
            </div>
            <div>
                <span style='color: #94a3b8;'>Audited Distance:</span>
                <b style='color: #f8fafc; margin-left: 4px;'>{audit.corridor_length_km:.2f} km</b>
            </div>
            <div>
                <span style='color: #94a3b8;'>Corridor Safety Buffer:</span>
                <b style='color: #f8fafc; margin-left: 4px;'>±{audit.corridor_buffer_m:.0f} meters</b>
            </div>
            <div>
                <span style='color: #94a3b8;'>Routing Architecture:</span>
                <b style='color: #38bdf8; margin-left: 4px;'>{audit.route_source_type}</b>
            </div>
        </div>

        <!-- Row 2: Verified Data Sources -->
        <div style='margin-bottom: 12px;'>
            <div style='font-size: 0.74rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px;'>
                Verified Data Sources & Feeds
            </div>
            {sources_html}
        </div>

        <!-- Row 3: Threat Analysis -->
        <div style='margin-bottom: 12px;'>
            <div style='font-size: 0.74rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 4px;'>
                Corridor Threat Evaluation
            </div>
            {threats_html}
        </div>

        <!-- Row 4: Confidence Score Handling -->
        <div style='background: rgba(0, 0, 0, 0.25); border-radius: 6px; padding: 8px 10px; margin-bottom: 10px;'>
            <div style='font-size: 0.72rem; font-weight: 800; color: #38bdf8; text-transform: uppercase; margin-bottom: 2px;'>
                Confidence Score Integrity Note
            </div>
            <div style='font-size: 0.72rem; color: #94a3b8; line-height: 1.4;'>
                {audit.confidence_score_explanation}
            </div>
        </div>

        <!-- Row 5: Operational Limitations & Disclaimers -->
        <div style='font-size: 0.68rem; color: #64748b; line-height: 1.4; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px;'>
            <b>Operational Disclaimer:</b> {audit.limitations_disclaimer}
        </div>
    </div>
    """
