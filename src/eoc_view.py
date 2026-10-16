"""
CampusAegis 2.0 • Emergency Operations Center (E.O.C.) & Tactical Hazard Map
Streamlit Component View providing:
1. Executive Threat Assessment & HUD Metrics
2. Tactical Leaflet Hazard Cartography with spatial buffer zones
3. Real-Time Incident Injection & CAD Emergency Feed Ingestion
4. Active Hazards Inventory & Direct Resolution Controls
5. Human-In-The-Loop (HITL) Operator Override Console (NFPA Life Safety Audit Trail)
6. Multi-Channel Emergency Communication Dispatcher (PA, Signage, Mobile, Dashboard)
7. REST API Server & Android Client Gateway Status
"""

import streamlit as st
import time
from typing import Dict, Any, List, Optional
from streamlit_folium import st_folium

from src.hazard_map import HazardMap, GeographicHazard, HazardSeverity
from src.operator_manager import OperatorManager
from src.communication_adapters import MultiChannelDispatcher, DeliveryStatus
from src.road_condition_manager import RoadConditionManager
from src.map_service import MapService

PRESET_LOCATIONS = {
    "📍 Vignan Main Entrance Arch (Vadlamudi)": (16.2325, 80.5490, "Vadlamudi Main Road"),
    "📍 NTR Central Library & Chemical Engg Loop": (16.2338, 80.5512, "Campus Ring Road East"),
    "📍 Tenali Canal Bund Road Corridor": (16.2410, 80.5315, "Tenali Canal Bund Road"),
    "📍 NH-16 Bypass Expressway Bridge": (16.2890, 80.4550, "NH-16 Bypass Expressway"),
    "📍 Arundelpet Commercial Center (Guntur)": (16.3075, 80.4350, "Arundelpet Main Road"),
    "📍 Brodipet Transit Corridor (Guntur)": (16.3015, 80.4420, "Brodipet 4th Lane"),
    "📍 Sangam Jagarlamudi Junction": (16.2350, 80.5050, "State Highway 48"),
    "📍 Custom GPS Coordinates...": (16.2335, 80.5505, "Custom Corridor"),
}


def render_emergency_operations_center(
    hazard_map: HazardMap,
    operator_manager: OperatorManager,
    comm_dispatcher: MultiChannelDispatcher,
    road_condition_manager: RoadConditionManager,
    map_service: MapService
):
    """
    Renders the complete Emergency Operations Center (E.O.C.) dashboard inside Streamlit.
    """
    active_hazards = hazard_map.get_active_hazards()
    active_closures = [r for r in road_condition_manager.get_active_restrictions() if r.is_hard_closure]
    audit_trail = operator_manager.get_audit_trail(limit=50)
    dispatches = comm_dispatcher.get_all_dispatched(limit=50)

    has_critical = any(h.severity == HazardSeverity.CRITICAL for h in active_hazards)
    has_high = any(h.severity == HazardSeverity.HIGH for h in active_hazards)

    if has_critical:
        defcon_badge = "<span class='badge-hud-danger'>🚨 DEFCON 1 • MAXIMUM ALERT — CRITICAL HAZARD ACTIVE</span>"
        border_color = "#ef4444"
        bg_gradient = "linear-gradient(135deg, rgba(127, 29, 29, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)"
    elif has_high or len(active_hazards) > 0:
        defcon_badge = "<span class='badge-hud-danger'>⚠️ DEFCON 2 • ELEVATED HAZARD — ACTIVE ROAD CONFLICT</span>"
        border_color = "#f97316"
        bg_gradient = "linear-gradient(135deg, rgba(124, 45, 18, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)"
    elif len(active_closures) > 0:
        defcon_badge = "<span class='badge-hud-amber'>⚠️ DEFCON 3 • CAUTION — MONITORING SPATIAL BUFFER</span>"
        border_color = "#f59e0b"
        bg_gradient = "linear-gradient(135deg, rgba(120, 53, 15, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%)"
    else:
        defcon_badge = "<span class='badge-hud-ready'>🟢 DEFCON 4 • NOMINAL — ALL CORRIDORS SECURE</span>"
        border_color = "#10b981"
        bg_gradient = "linear-gradient(135deg, rgba(6, 78, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%)"

    st.markdown(f"""
    <div style="border-radius: 14px; padding: 18px 24px; margin-bottom: 20px; border: 2px solid {border_color}; background: {bg_gradient}; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <div style="font-size: 1.35rem; font-weight: 800; color: #f8fafc; letter-spacing: -0.02em; display: flex; align-items: center; gap: 10px;">
                    <span>🚨 CampusAegis Emergency Operations Center (E.O.C.)</span>
                </div>
                <div style="font-size: 0.82rem; color: #cbd5e1; margin-top: 4px;">
                    Autonomous Spatial Hazard Cartography • Human-In-The-Loop Life Safety Overrides • Multi-Channel Broadcast Console
                </div>
            </div>
            <div>
                {defcon_badge}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Top Executive HUD Metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    crit_count = sum(1 for h in active_hazards if h.severity in [HazardSeverity.HIGH, HazardSeverity.CRITICAL])
    m1.metric(
        "⚠️ Active Hazards",
        f"{len(active_hazards)} Incidents",
        delta=f"↑ {crit_count} High/Crit" if crit_count > 0 else None,
        delta_color="inverse"
    )
    m2.metric(
        "🛑 Road Closures",
        f"{len(active_closures)} Impassable",
        delta=f"↑ {len(active_closures)} Total Restr" if len(active_closures) > 0 else None,
        delta_color="inverse"
    )
    m3.metric(
        "👮 Operator Logs",
        f"{len(audit_trail)} Recorded",
        delta="NFPA Compliant"
    )
    m4.metric(
        "📡 Broadcasts",
        f"{len(dispatches)} Dispatched",
        delta="4 Channels Active"
    )
    m5.metric(
        "🔌 REST API Gateway",
        "Port 8000 / FastAPI",
        delta="Android Ready"
    )

    st.markdown("---")

    # Interactive Tactical Map
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.25rem;">🗺️</span>
            <span style="font-weight: 800; font-size: 1.05rem; color: #f8fafc;">
                Tactical Hazard Cartography & Spatial Buffer Impact Zones
            </span>
        </div>
        <span style="font-size: 0.72rem; font-weight: 700; color: #38bdf8; background: rgba(56, 189, 248, 0.15); padding: 3px 10px; border-radius: 6px; border: 1px solid rgba(56, 189, 248, 0.3);">
            SATELLITE HYBRID HUD
        </span>
    </div>
    """, unsafe_allow_html=True)

    c_map_ctrl1, c_map_ctrl2, c_map_ctrl3, c_map_ctrl4 = st.columns([2, 1, 1, 1])
    with c_map_ctrl1:
        map_focus = st.selectbox(
            "Quick Cartographic Focus:",
            [
                "Regional Overview (Vadlamudi - Guntur Corridor)",
                "Vignan University Campus Zone",
                "Tenali Regional Approach",
                "Guntur Metropolitan Center"
            ],
            index=0,
            label_visibility="collapsed"
        )
    with c_map_ctrl2:
        if st.button("🔄 Refresh Radar", key="btn_refresh_eoc_map", use_container_width=True):
            st.rerun()
    with c_map_ctrl3:
        if st.button("📡 Ingest Batch Feed", key="btn_quick_batch", use_container_width=True, help="Simulate batch CAD emergency feed ingestion"):
            ingest_simulated_cad_feed(hazard_map, operator_manager, comm_dispatcher)
            st.rerun()
    with c_map_ctrl4:
        if st.button("🧹 Clear All Incidents", key="btn_quick_clear_all", use_container_width=True, help="Resolve all hazards & restore clear road networks"):
            hazard_map.clear_all_hazards()
            operator_manager.record_override(
                route_or_zone_id="ALL_ZONES",
                override_action="FULL_EMERGENCY_RESET",
                reason="Operator cleared all active spatial hazards."
            )
            st.success("All hazards resolved and road network returned to nominal clear flow.")
            st.rerun()

    # Center coords based on focus
    if "Vignan" in map_focus:
        c_lat, c_lon, zoom_level = 16.2335, 80.5505, 16
    elif "Tenali" in map_focus:
        c_lat, c_lon, zoom_level = 16.2410, 80.5315, 15
    elif "Guntur" in map_focus:
        c_lat, c_lon, zoom_level = 16.3067, 80.4365, 14
    else:
        c_lat, c_lon, zoom_level = 16.2700, 80.4935, 12

    # Prepare data for map renderer
    haz_dicts = []
    for h in active_hazards:
        haz_dicts.append({
            "lat": h.latitude,
            "lon": h.longitude,
            "radius_meters": h.radius_meters,
            "incident_type": h.incident_type,
            "severity": h.severity.value,
            "description": h.description,
            "affected_road_name": h.affected_road_name or "Regional Corridor",
            "source": h.source,
            "confidence_level": h.confidence_level
        })

    closure_dicts = []
    for cl in active_closures:
        closure_dicts.append({
            "type": cl.restriction_type.value,
            "road_name": cl.road_name,
            "description": cl.description,
            "is_hard_closure": True
        })

    if hasattr(map_service, "render_hazard_map"):
        eoc_folium = map_service.render_hazard_map(
            center_lat=c_lat,
            center_lon=c_lon,
            zoom=zoom_level,
            hazards=haz_dicts,
            road_closures=closure_dicts,
            map_style="satellite_hybrid"
        )
    else:
        eoc_folium = map_service.create_interactive_map(
            center_lat=c_lat,
            center_lon=c_lon,
            zoom=zoom_level,
            hazards=haz_dicts,
            road_closures=closure_dicts,
            map_style="satellite_hybrid"
        )

    st_folium(
        eoc_folium,
        width=None,
        height=460,
        key=f"eoc_map_{c_lat}_{c_lon}_{len(active_hazards)}",
        use_container_width=True
    )

    st.markdown("---")

    # Incident Management Split: Injection Form vs Active Incident List
    c_inject, c_list = st.columns([1, 1], gap="large")

    with c_inject:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
            <span style="font-size: 1.2rem;">⚡</span>
            <span style="font-weight: 700; font-size: 0.98rem; color: #f8fafc; text-transform: uppercase; letter-spacing: 0.05em;">
                Inject New Geographic Incident
            </span>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_inject_hazard", clear_on_submit=False):
            f_type = st.selectbox(
                "Incident Classification:",
                [
                    "🔥 FIRE_DETECTED",
                    "🌊 FLASH_FLOOD",
                    "☣️ CHEMICAL_SPILL",
                    "🚧 ROAD_CAVE_IN",
                    "💥 STRUCTURAL_COLLAPSE",
                    "🚗 MULTI_VEHICLE_COLLISION",
                    "⚡ ELECTRICAL_GRID_FAILURE"
                ],
                index=0
            )
            f_severity = st.selectbox(
                "Hazard Severity Level:",
                ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                index=1
            )
            f_loc_preset = st.selectbox(
                "Corridor / Landmark Location:",
                list(PRESET_LOCATIONS.keys()),
                index=0
            )

            p_lat, p_lon, p_road = PRESET_LOCATIONS[f_loc_preset]

            c_lat_inp, c_lon_inp = st.columns(2)
            with c_lat_inp:
                f_lat = st.number_input("Latitude:", value=p_lat, format="%.5f")
            with c_lon_inp:
                f_lon = st.number_input("Longitude:", value=p_lon, format="%.5f")

            f_radius = st.slider("Hazard Safety Buffer Radius (meters):", min_value=50, max_value=800, value=250, step=25)
            f_road = st.text_input("Affected Road Corridor:", value=p_road)
            f_desc = st.text_area("Incident Summary Details:", value=f"Reported {f_type.split()[-1]} incident obstructing traffic.")
            f_conf = st.slider("Sensor / Confidence Level:", min_value=0.1, max_value=1.0, value=0.95, step=0.05)

            submitted = st.form_submit_button("🚨 Inject Hazard Into Live Network", type="primary", use_container_width=True)
            if submitted:
                clean_type = f_type.split()[-1]
                hid = f"HAZ_{int(time.time())}_{clean_type[:4]}"
                new_hazard = GeographicHazard(
                    hazard_id=hid,
                    incident_type=clean_type,
                    severity=HazardSeverity[f_severity],
                    latitude=f_lat,
                    longitude=f_lon,
                    radius_meters=float(f_radius),
                    description=f_desc,
                    affected_road_name=f_road,
                    confidence_level=f_conf,
                    is_demonstration=True,
                    source="EOC_OPERATOR_CONSOLE"
                )
                hazard_map.add_hazard(new_hazard)
                operator_manager.record_override(
                    route_or_zone_id=f_road or hid,
                    override_action=f"INJECT_HAZARD_{clean_type}",
                    reason=f"Operator manual incident injection: {f_desc} ({f_radius}m buffer)"
                )
                comm_dispatcher.broadcast(
                    target_zone=f_road or "CAMPUS_VICINITY",
                    floor=0,
                    headline=f"EMERGENCY ALERT: {clean_type} at {f_road}",
                    body=f"Hazard perimeter established ({f_radius}m). Route reassessment enforced.",
                    severity=f_severity
                )
                st.toast(f"Incident {hid} injected! Corridor {f_road} blocked.", icon="🚨")
                st.rerun()

    with c_list:
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.2rem;">📋</span>
                <span style="font-weight: 700; font-size: 0.98rem; color: #f8fafc; text-transform: uppercase; letter-spacing: 0.05em;">
                    Active Incident Inventory ({len(active_hazards)})
                </span>
            </div>
            <span style="font-size: 0.70rem; color: #94a3b8; font-family: monospace;">REAL-TIME BUFFER TRACKER</span>
        </div>
        """, unsafe_allow_html=True)

        if not active_hazards:
            st.markdown("""
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 24px; text-align: center; margin-top: 10px;">
                <span style="font-size: 2rem;">✅</span>
                <div style="font-weight: 700; color: #34d399; font-size: 1.05rem; margin-top: 8px;">Zero Active Incidents</div>
                <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 4px;">
                    All regional roads, campus gates, and arterial highway corridors are currently safe and verified clear.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for h in active_hazards:
                sev_color = "#ef4444" if h.severity == HazardSeverity.CRITICAL else "#f97316" if h.severity == HazardSeverity.HIGH else "#f59e0b"
                icon = "🔥" if "FIRE" in h.incident_type else "🌊" if "FLOOD" in h.incident_type else "☣️" if "CHEM" in h.incident_type else "⚠️"

                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.25); border-left: 4px solid {sev_color}; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 800; font-size: 0.92rem; color: #f8fafc;">
                            {icon} {h.incident_type} <span style="font-size: 0.72rem; color: {sev_color}; font-weight: 700; background: rgba(0,0,0,0.4); padding: 2px 6px; border-radius: 4px;">{h.severity.value}</span>
                        </span>
                        <span style="font-family: monospace; font-size: 0.72rem; color: #38bdf8;">ID: {h.hazard_id}</span>
                    </div>
                    <div style="font-size: 0.80rem; color: #cbd5e1; margin-top: 6px;">
                        <b>Location:</b> {h.affected_road_name or 'Unspecified'} ({h.latitude:.4f}, {h.longitude:.4f})<br>
                        <b>Radius:</b> {h.radius_meters:.0f}m Buffer | <b>Confidence:</b> {int(h.confidence_level * 100)}% | <b>Source:</b> {h.source}<br>
                        <b>Details:</b> {h.description}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                c_btn1, c_btn2, c_btn3 = st.columns(3)
                with c_btn1:
                    if st.button("✅ Clear Hazard", key=f"btn_clr_{h.hazard_id}", use_container_width=True):
                        hazard_map.clear_hazard(h.hazard_id)
                        operator_manager.record_override(
                            route_or_zone_id=h.affected_road_name or h.hazard_id,
                            override_action="CLEAR_HAZARD",
                            reason=f"Operator verified hazard {h.hazard_id} neutralized."
                        )
                        st.toast(f"Hazard {h.hazard_id} cleared.", icon="✅")
                        st.rerun()
                with c_btn2:
                    if st.button("👁️ Acknowledge", key=f"btn_ack_{h.hazard_id}", use_container_width=True):
                        operator_manager.record_acknowledgment(
                            incident_id=h.hazard_id,
                            operator_name="Safety Watch Officer"
                        )
                        st.toast(f"Hazard {h.hazard_id} acknowledged by operator.", icon="👁️")
                with c_btn3:
                    if st.button("🚨 Escalate", key=f"btn_esc_{h.hazard_id}", use_container_width=True):
                        operator_manager.record_escalation(
                            zone_id=h.affected_road_name or h.hazard_id,
                            reason=f"Escalated {h.incident_type} to emergency services"
                        )
                        comm_dispatcher.broadcast(
                            target_zone="REGIONAL_RESPONSE",
                            floor=0,
                            headline=f"DISPATCH ESCALATION: {h.incident_type}",
                            body=f"Incident {h.hazard_id} escalated to civil defense.",
                            severity="CRITICAL"
                        )
                        st.toast(f"Hazard {h.hazard_id} escalated to civil defense!", icon="🚨")

    st.markdown("---")

    # Human-In-The-Loop (HITL) Operator Overrides (NFPA Life Safety Audit Trail)
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.25rem;">👮</span>
            <span style="font-weight: 800; font-size: 1.05rem; color: #f8fafc;">
                Human-In-The-Loop (HITL) Life Safety Operator Console
            </span>
        </div>
        <span style="font-size: 0.72rem; font-weight: 700; color: #34d399; background: rgba(16, 185, 129, 0.15); padding: 3px 10px; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.3);">
            NFPA 101 LIFE SAFETY AUDIT COMPLIANT
        </span>
    </div>
    """, unsafe_allow_html=True)

    c_op_form, c_op_trail = st.columns([1, 1], gap="large")

    with c_op_form:
        st.markdown("<div style='font-weight: 700; font-size: 0.88rem; color: #38bdf8; text-transform: uppercase;'>Record Operator Manual Override</div>", unsafe_allow_html=True)
        with st.form("form_operator_override", clear_on_submit=False):
            op_name = st.text_input("Watch Officer Name & Badge:", value="Officer R. Sharma • Badge #7419")
            op_target = st.selectbox(
                "Target Corridor / Campus Zone:",
                [
                    "Tenali Canal Bund Road Corridor",
                    "NH-16 Bypass Expressway",
                    "Vignan Main University Gate (Vadlamudi)",
                    "Chemical Reaction Engineering Loop",
                    "Guntur Arundelpet Transit Corridor",
                    "Sangam Jagarlamudi Junction"
                ],
                index=0
            )
            op_action = st.selectbox(
                "Authorized Control Action:",
                [
                    "HARD_BLOCK_CORRIDOR_EVACUATION",
                    "FORCE_DETOUR_AROUND_HAZARD",
                    "OVERRIDE_ALLOW_RESTRICTED_TRANSIT",
                    "DEPLOY_RAPID_TRAFFIC_CONES",
                    "TRIGGER_CAMPUS_WIDE_SHELTER_IN_PLACE"
                ],
                index=0
            )
            op_reason = st.text_area(
                "Regulatory Justification (Mandatory for Audit Trail):",
                value="Visual confirmation of lane obstruction; rerouting transit traffic away from potential hazard area."
            )
            btn_op_submit = st.form_submit_button("📝 Commit Operator Override to Immutable Audit Log", use_container_width=True)
            if btn_op_submit:
                if not op_reason.strip():
                    st.error("Audit failure: Life Safety Code requires a non-empty operator justification rationale.")
                else:
                    operator_manager.record_override(
                        route_or_zone_id=op_target,
                        override_action=op_action,
                        reason=op_reason,
                        operator_name=op_name
                    )
                    comm_dispatcher.broadcast(
                        target_zone=op_target,
                        floor=0,
                        headline=f"OPERATOR OVERRIDE: {op_action}",
                        body=f"{op_reason} (Authorized by {op_name})",
                        severity="HIGH"
                    )
                    st.success(f"Override committed to audit log by {op_name}!")
                    st.rerun()

    with c_op_trail:
        st.markdown("<div style='font-weight: 700; font-size: 0.88rem; color: #38bdf8; text-transform: uppercase;'>Immutable Operator Action Audit Trail</div>", unsafe_allow_html=True)
        if not audit_trail:
            st.info("No operator actions recorded in this session yet.")
        else:
            with st.container(height=320):
                for rec in audit_trail:
                    act_type = rec.get("action", "")
                    tag_col = "#ef4444" if "OVERRIDE" in act_type else "#f59e0b" if "ACK" in act_type else "#38bdf8"
                    tag_icon = "🔴 OVERRIDE" if "OVERRIDE" in act_type else "🟡 ACK" if "ACK" in act_type else "🔵 LOG"

                    st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 6px; padding: 8px 12px; margin-bottom: 6px; font-size: 0.78rem;">
                        <div style="display: flex; justify-content: space-between; color: #94a3b8; font-family: monospace;">
                            <span>⏱️ {rec.get('time', '')} | <b>{rec.get('operator', '')}</b></span>
                            <span style="color: {tag_col}; font-weight: 700;">{tag_icon}</span>
                        </div>
                        <div style="margin-top: 4px; color: #f8fafc; font-weight: 600;">
                            Target: {rec.get('target', '')} • Action: {act_type}
                        </div>
                        <div style="margin-top: 2px; color: #cbd5e1; font-style: italic;">
                            "{rec.get('reason', '')}"
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("---")

    # Multi-Channel Emergency Broadcast Console
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.25rem;">📡</span>
            <span style="font-weight: 800; font-size: 1.05rem; color: #f8fafc;">
                Multi-Channel Emergency Communication Dispatcher
            </span>
        </div>
        <span style="font-size: 0.72rem; font-weight: 700; color: #38bdf8; background: rgba(56, 189, 248, 0.15); padding: 3px 10px; border-radius: 6px; border: 1px solid rgba(56, 189, 248, 0.3);">
            4 SYNCHRONIZED CHANNELS
        </span>
    </div>
    """, unsafe_allow_html=True)

    c_ch1, c_ch2, c_ch3, c_ch4 = st.columns(4)
    with c_ch1:
        st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 8px; padding: 10px; text-align: center;">
            <div style="font-size: 1.2rem;">🖥️</div>
            <div style="font-weight: 700; font-size: 0.82rem; color: #f8fafc;">Dashboard Live Feed</div>
            <div style="font-size: 0.68rem; color: #34d399; font-weight: 800; margin-top: 2px;">● ONLINE</div>
        </div>
        """, unsafe_allow_html=True)

    pa_online = getattr(getattr(comm_dispatcher, 'pa_adapter', None), 'is_online', True)
    sig_online = getattr(getattr(comm_dispatcher, 'signage_adapter', None), 'is_online', True)
    mob_adapter = getattr(comm_dispatcher, 'push_adapter', getattr(comm_dispatcher, 'mobile_adapter', None))
    mob_online = getattr(mob_adapter, 'is_online', True) if mob_adapter else True

    with c_ch2:
        col_pa = "#34d399" if pa_online else "#ef4444"
        txt_pa = "● ONLINE" if pa_online else "✕ LINK DOWN"
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid {col_pa}; border-radius: 8px; padding: 10px; text-align: center;">
            <div style="font-size: 1.2rem;">📢</div>
            <div style="font-weight: 700; font-size: 0.82rem; color: #f8fafc;">Public Address (PA)</div>
            <div style="font-size: 0.68rem; color: {col_pa}; font-weight: 800; margin-top: 2px;">{txt_pa}</div>
        </div>
        """, unsafe_allow_html=True)

    with c_ch3:
        col_sig = "#34d399" if sig_online else "#ef4444"
        txt_sig = "● ONLINE" if sig_online else "✕ LINK DOWN"
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid {col_sig}; border-radius: 8px; padding: 10px; text-align: center;">
            <div style="font-size: 1.2rem;">📺</div>
            <div style="font-weight: 700; font-size: 0.82rem; color: #f8fafc;">Digital Visual Signage</div>
            <div style="font-size: 0.68rem; color: {col_sig}; font-weight: 800; margin-top: 2px;">{txt_sig}</div>
        </div>
        """, unsafe_allow_html=True)

    with c_ch4:
        col_mob = "#34d399" if mob_online else "#ef4444"
        txt_mob = "● ONLINE" if mob_online else "✕ LINK DOWN"
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid {col_mob}; border-radius: 8px; padding: 10px; text-align: center;">
            <div style="font-size: 1.2rem;">📱</div>
            <div style="font-weight: 700; font-size: 0.82rem; color: #f8fafc;">Mobile Push Alerts</div>
            <div style="font-size: 0.68rem; color: {col_mob}; font-weight: 800; margin-top: 2px;">{txt_mob}</div>
        </div>
        """, unsafe_allow_html=True)

    c_bcast_form, c_bcast_log = st.columns([1, 1], gap="large")

    with c_bcast_form:
        st.markdown("<div style='font-weight: 700; font-size: 0.88rem; color: #38bdf8; text-transform: uppercase; margin-top: 10px;'>Transmit Institutional Emergency Broadcast</div>", unsafe_allow_html=True)
        with st.form("form_emergency_broadcast", clear_on_submit=False):
            bc_target = st.text_input("Target Audience / Geographic Sector:", value="All Active Travelers & Campus Corridors")
            bc_floor = st.number_input("Floor / Level Designation (0=Ground):", min_value=-1, max_value=8, value=0)
            bc_sev = st.selectbox("Broadcast Priority Level:", ["CRITICAL", "HIGH", "MEDIUM", "LOW"], index=0)
            bc_head = st.text_input("Alert Headline:", value="URGENT: HAZARDOUS TRAVEL INCIDENT REPORTED")
            bc_body = st.text_area("Spoken / Display Message Body:", value="Hazard buffer established near transit intersection. Follow alternate navigation routes immediately.")

            btn_bcast = st.form_submit_button("📡 Broadcast Alert Across All 4 Adapters", type="primary", use_container_width=True)
            if btn_bcast:
                comm_dispatcher.broadcast(
                    target_zone=bc_target,
                    floor=bc_floor,
                    headline=bc_head,
                    body=bc_body,
                    severity=bc_sev
                )
                operator_manager.record_override(
                    route_or_zone_id=bc_target,
                    override_action="EMERGENCY_BROADCAST",
                    reason=f"Alert dispatched: {bc_head}"
                )
                st.toast(f"Broadcasted to 4 channels: {bc_head}", icon="📡")
                st.rerun()

        c_fault1, c_fault2 = st.columns(2)
        with c_fault1:
            if st.button("⚠️ Simulate Bus Outage", key="btn_sim_outage", use_container_width=True, help="Simulates hardware communication failure"):
                comm_dispatcher.simulate_channel_outage("pa", is_down=True)
                comm_dispatcher.simulate_channel_outage("signage", is_down=True)
                comm_dispatcher.simulate_channel_outage("push", is_down=True)
                st.warning("Simulated comms bus outage triggered. PA, Signage, and Mobile links down.")
                st.rerun()
        with c_fault2:
            if st.button("🔄 Restore Channels", key="btn_restore_channels", use_container_width=True, help="Restores all communication links"):
                comm_dispatcher.simulate_channel_outage("pa", is_down=False)
                comm_dispatcher.simulate_channel_outage("signage", is_down=False)
                comm_dispatcher.simulate_channel_outage("push", is_down=False)
                st.success("All institutional communication links restored online.")
                st.rerun()

    with c_bcast_log:
        st.markdown("<div style='font-weight: 700; font-size: 0.88rem; color: #38bdf8; text-transform: uppercase; margin-top: 10px;'>Broadcast Outbox Transmission Log</div>", unsafe_allow_html=True)
        if not dispatches:
            st.info("No broadcasts sent yet. Use the form on the left to transmit an institutional alert.")
        else:
            with st.container(height=320):
                for d in dispatches:
                    st_val = d.get("status", "")
                    col_st = "#34d399" if st_val == DeliveryStatus.DELIVERED.value else "#ef4444"
                    st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 6px; padding: 8px 12px; margin-bottom: 6px; font-size: 0.78rem;">
                        <div style="display: flex; justify-content: space-between; color: #94a3b8; font-family: monospace;">
                            <span>⏱️ {d.get('time', '')} | Channel: <b>{d.get('channel', '')}</b></span>
                            <span style="color: {col_st}; font-weight: 800;">{st_val}</span>
                        </div>
                        <div style="margin-top: 3px; color: #f8fafc; font-weight: 700;">
                            {d.get('headline', '')}
                        </div>
                        <div style="margin-top: 2px; color: #cbd5e1; font-size: 0.74rem;">
                            Target: {d.get('target_zone', '')} • {d.get('body', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("---")

    # FastAPI REST Gateway Summary
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.25rem;">📱</span>
            <span style="font-weight: 800; font-size: 1.05rem; color: #f8fafc;">
                FastAPI REST Server & Android Companion App Gateway
            </span>
        </div>
        <span style="font-size: 0.72rem; font-weight: 700; color: #34d399; background: rgba(16, 185, 129, 0.15); padding: 3px 10px; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.3);">
            FULL BACKEND COMPATIBILITY
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        The CampusAegis system provides a full asynchronous REST backend (`src/api_server.py`) serving external clients, field devices, and the Android mobile navigation client:
        
        - **`GET  /api/health`**: Real-time system health and active hazard metrics.
        - **`POST /api/geocode`**: Nominatim and offline pre-cached geocoding.
        - **`POST /api/route`**: Multi-objective routing with automatic safety filtering.
        - **`GET  /api/hazards`**: Active spatial buffers, road closures, and severity.
        - **`POST /api/simulate-emergency`**: Dispatches alerts and establishes buffers.
        - **`POST /api/register-device`**: Links Android push device tokens.
        - **`GET  /api/notifications`**: Ingests notification transmission lifecycle.
    """)

    c_api1, c_api2 = st.columns(2)
    with c_api1:
        st.markdown("**Launch REST Server (CLI)**:")
        st.code("python -m uvicorn src.api_server:app --port 8000 --reload", language="bash")
    with c_api2:
        st.markdown("**Test Active Hazards Endpoint**:")
        st.code("curl http://localhost:8000/api/hazards", language="bash")


def ingest_simulated_cad_feed(
    hazard_map: HazardMap,
    operator_manager: OperatorManager,
    comm_dispatcher: MultiChannelDispatcher
):
    """
    Simulates real-time Computer-Aided Dispatch (CAD) external 911 / emergency feeds.
    """
    simulated_batch = [
        {
            "hazard_id": f"CAD_{int(time.time())}_FIRE",
            "incident_type": "FIRE_DETECTED",
            "severity": "CRITICAL",
            "latitude": 16.2340,
            "longitude": 80.5498,
            "radius_meters": 220.0,
            "description": "Structural fire alert in Chemical Engineering research wing.",
            "affected_road_name": "Chemical Reaction Engineering Loop",
            "confidence_level": 0.98,
            "is_demonstration": True,
            "source": "CAMPUS_CAD_FIRE_DISPATCH"
        },
        {
            "hazard_id": f"CAD_{int(time.time())}_COLLISION",
            "incident_type": "MULTI_VEHICLE_COLLISION",
            "severity": "HIGH",
            "latitude": 16.2890,
            "longitude": 80.4550,
            "radius_meters": 300.0,
            "description": "Multi-vehicle freight collision blocking both eastbound expressway lanes.",
            "affected_road_name": "NH-16 Bypass Expressway",
            "confidence_level": 0.92,
            "is_demonstration": True,
            "source": "HIGHWAY_PATROL_TELEMETRY"
        },
        {
            "hazard_id": f"CAD_{int(time.time())}_FLOOD",
            "incident_type": "FLASH_FLOOD",
            "severity": "HIGH",
            "latitude": 16.2415,
            "longitude": 80.5310,
            "radius_meters": 250.0,
            "description": "Canal overflow inundation making low-lying road impassable.",
            "affected_road_name": "Tenali Canal Bund Road",
            "confidence_level": 0.88,
            "is_demonstration": True,
            "source": "IRRIGATION_CIVIL_DEFENSE"
        }
    ]

    count = hazard_map.ingest_external_alerts(simulated_batch)
    operator_manager.record_override(
        route_or_zone_id="REGIONAL_NETWORK",
        override_action="BATCH_CAD_INGESTION",
        reason=f"Ingested {count} active incidents from simulated CAD emergency feed."
    )
    comm_dispatcher.broadcast(
        target_zone="REGIONAL_NETWORK",
        floor=0,
        headline="CAD INCIDENT FEED INGESTED",
        body=f"{count} real-time hazard buffers established across regional transit corridors.",
        severity="HIGH"
    )
    st.toast(f"Ingested {count} active emergency incidents from CAD feed!", icon="📡")
