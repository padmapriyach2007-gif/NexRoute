"""
Pathfinder Traffic Intelligence & Human Movement Detection System UI Studio
Combines:
1. Camera-Based AI Detection (OpenCV, Multi-Object Tracking, Line-Crossing, In/Out Counts, Queues, FPS)
2. Physical Sensor Fleet (PIR, IR Break-Beam, mmWave Radar, Vehicle Radar, Inductive Loop)
3. Sensor Fusion & Disagreement Resolution (Cross-Modal Deduplication, Confidence Scoring, Conflict Alerts)
4. Traffic Analytics & AI Forecasting (Multi-Horizon Predictions, Segments, Empirical Benchmarks)
5. Map Routing Integration & Ollama AI Retrieval Grounding
"""

import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import streamlit as st

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    CV2_AVAILABLE = False
    cv2 = None
    np = None

from src.backend.traffic.fusion_service import (
    TrafficFusionService, TrafficObservation, SegmentTrafficState
)
from src.backend.traffic.prediction_service import (
    TrafficPredictionService, PredictionResult
)
from src.backend.traffic.evaluation_pipeline import (
    TrafficEvaluationPipeline, EvaluationBenchmarkResult
)
from src.backend.traffic.vision_detector import (
    VisionDetectorEngine, VisionDetectionMetrics, SUPPORTED_CLASSES
)
from src.backend.traffic.sensor_adapters import (
    SensorRegistry, BaseSensorAdapter, SensorReading
)
from src.backend.traffic.traffic_fusion_engine import (
    SensorFusionEngine, FusedTrafficState, CONGESTION_THRESHOLDS
)
from src.backend.traffic.traffic_service import PathfinderTrafficService

# Reference road segments
DEMO_SEGMENTS = [
    {
        "id": "SEG_EXPRESSWAY_01",
        "name": "NexRoute Central Expressway (NH-16)",
        "road_type": "MOTORWAY",
        "free_flow_kmh": 90.0,
        "length_meters": 3200.0,
        "default_quality": 0.96
    },
    {
        "id": "SEG_GUNTUR_BYPASS",
        "name": "Guntur Metropolitan Ring Bypass",
        "road_type": "PRIMARY",
        "free_flow_kmh": 65.0,
        "length_meters": 2400.0,
        "default_quality": 0.90
    },
    {
        "id": "SEG_TENALI_HIGHWAY",
        "name": "Tenali Arterial Transit Highway",
        "road_type": "PRIMARY",
        "free_flow_kmh": 55.0,
        "length_meters": 1800.0,
        "default_quality": 0.85
    },
    {
        "id": "SEG_VADLAMUDI_LINK",
        "name": "Vadlamudi University Link Road",
        "road_type": "SECONDARY",
        "free_flow_kmh": 40.0,
        "length_meters": 1200.0,
        "default_quality": 0.82
    }
]


def render_traffic_intelligence_dashboard():
    """Renders the comprehensive NexRoute AI Traffic & Human Movement Detection System."""
    svc = PathfinderTrafficService.get_instance()

    # Glassmorphic Cockpit Header Banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.96) 0%, rgba(30, 41, 59, 0.90) 100%);
                border: 1.5px solid rgba(56, 189, 248, 0.40);
                border-radius: 16px;
                padding: 16px 22px;
                margin-bottom: 16px;
                box-shadow: 0 10px 32px rgba(0,0,0,0.55), 0 0 20px rgba(56, 189, 248, 0.15);
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 12px;">
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="font-size: 2.3rem; filter: drop-shadow(0 0 14px #38bdf8);">🚦</div>
            <div>
                <div style="font-size: 1.30rem; font-weight: 800; color: #f8fafc; letter-spacing: 0.03em;">
                    AI Traffic & Human Movement Detection System
                </div>
                <div style="font-size: 0.78rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">
                    Camera Computer Vision • Physical Sensor Adapters • Multi-Modal Sensor Fusion • Real-Time Tracking
                </div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; padding: 4px 10px; border-radius: 999px; display: flex; align-items: center; gap: 6px;">
                <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #10b981; box-shadow: 0 0 8px #10b981;"></span>
                <span style="font-size: 0.72rem; font-weight: 700; color: #34d399; font-family: monospace;">FUSION ONLINE</span>
            </div>
            <div style="background: rgba(56, 189, 248, 0.15); border: 1px solid #38bdf8; padding: 4px 10px; border-radius: 999px; display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 0.72rem; font-weight: 700; color: #7dd3fc; font-family: monospace;">CV TRACKER READY</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5-Tab Dedicated Studio Navigation
    t_vision, t_sensors, t_fusion, t_analytics, t_advisory = st.tabs([
        "📹 Camera Vision & Tracking",
        "📡 Physical Sensor Fleet",
        "⚖️ Sensor Fusion & Conflict Studio",
        "📊 Traffic Analytics & Predictor",
        "🗺️ Route Advisory & Ollama AI"
    ])

    # =========================================================================
    # TAB 1: CAMERA VISION & OBJECT TRACKING
    # =========================================================================
    with t_vision:
        st.markdown("### 🎥 Camera-Based AI Detection & Tracking Engine")
        st.caption("Supports local webcam, video files, RTSP/IP camera feeds, or synthetic simulation. ByteTrack-style temporary IDs with virtual line-crossing.")

        c_src, c_env, c_cam = st.columns([1.5, 1.2, 1.3])
        with c_src:
            source_choice = st.selectbox(
                "Video Input Source:",
                ["🧪 Synthetic AI Simulation (Zero-Hardware)", "🎥 Local Webcam", "📁 Upload Test Video", "🌐 IP Camera / RTSP Stream"],
                key="traffic_source_choice"
            )
        with c_env:
            env_choice = st.selectbox(
                "Environment Model:",
                ["OUTDOOR (Roads & Intersections)", "INDOOR (Buildings & Entrances)"],
                key="traffic_env_choice"
            )
        with c_cam:
            active_detector_key = "CAM_OUTDOOR_01" if "OUTDOOR" in env_choice else "CAM_INDOOR_01"
            svc.set_active_camera(active_detector_key)
            st.metric("Active Camera ID", active_detector_key, delta=env_choice.split()[0], delta_color="off")

        # Configure Source Parameters
        source_param = None
        if "Webcam" in source_choice:
            source_type = "WEBCAM"
            w_idx = st.text_input("Webcam Device Index (e.g., 0)", "0", key="webcam_idx")
            source_param = w_idx
        elif "Upload" in source_choice:
            source_type = "VIDEO_FILE"
            uploaded_vid = st.file_uploader("Upload MP4/AVI Video", type=["mp4", "avi", "mov"], key="traffic_vid_upload")
            if uploaded_vid is not None:
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tfile:
                    tfile.write(uploaded_vid.read())
                    source_param = tfile.name
        elif "RTSP" in source_choice:
            source_type = "RTSP"
            rtsp_url = st.text_input("RTSP Stream URL", "rtsp://192.168.1.100:554/stream1", key="traffic_rtsp_url")
            source_param = rtsp_url
        else:
            source_type = "SYNTHETIC"

        # Apply source change if modified
        detector = svc.get_active_detector()
        if detector.source_type != source_type or (source_param and detector.source_path != source_param):
            detector.open_source(source_type, source_param)

        # Controls & Sliders
        ctrl_c1, ctrl_c2, ctrl_c3, ctrl_c4 = st.columns([1.2, 1.2, 1.4, 1.2])
        with ctrl_c1:
            run_live = st.toggle("▶️ Stream Live Frames", value=True, key="traffic_run_live")
        with ctrl_c2:
            step_frame = st.button("⏭️ Step Next Frame", key="traffic_step_frame", use_container_width=True)
        with ctrl_c3:
            trip_y = st.slider("Tripwire Position (Y %)", 20, 80, int(detector.tripwire_y_ratio * 100), key="traffic_tripwire_slider")
            detector.tripwire_y_ratio = trip_y / 100.0
        with ctrl_c4:
            if st.button("🔄 Reset Counts", key="traffic_reset_counts", use_container_width=True):
                detector.total_inbound = 0
                detector.total_outbound = 0
                detector.counts_by_class = {c: 0 for c in SUPPORTED_CLASSES}
                st.toast("Telemetry counters reset to zero!", icon="🧹")

        # Process Single or Continuous Frame
        frame_img, v_metrics, fused_st = svc.process_frame()

        col_frame, col_telemetry = st.columns([1.7, 1.3])
        with col_frame:
            if frame_img is not None:
                st.image(frame_img, channels="BGR", use_container_width=True, caption=f"Live HUD Preview • {detector.camera_id} • Privacy Mode: Anonymous Temporary IDs (No Biometrics)")
            else:
                st.warning("No camera frame available. Please ensure webcam/video source is accessible.")

        with col_telemetry:
            st.markdown("#### ⚡ Real-Time Tracking Telemetry")
            m_c1, m_c2 = st.columns(2)
            with m_c1:
                st.metric("Pedestrians Active", v_metrics.pedestrian_count, f"{v_metrics.people_per_min:.1f} / min")
                st.metric("Inbound Crossed", v_metrics.inbound_count)
                st.metric("Processing FPS", f"{v_metrics.fps} FPS")
            with m_c2:
                st.metric("Vehicles Active", v_metrics.vehicle_count, f"{v_metrics.vehicles_per_min:.1f} / min")
                st.metric("Outbound Crossed", v_metrics.outbound_count)
                st.metric("Pipeline Latency", f"{v_metrics.latency_ms} ms")

            if v_metrics.queue_length > 0:
                st.warning(f"⚠️ **Vehicle Queue Detected:** {v_metrics.queue_length} stopped/slow vehicles in queue zone.")

            st.markdown("##### 🚗 Cumulative Counts by Object Class")
            cls_items = "".join([
                f"<div style='background: rgba(255,255,255,0.04); padding: 4px 8px; border-radius: 6px; font-size: 0.72rem;'>"
                f"<b style='color:#7dd3fc;'>{k.upper()}:</b> {v}</div>"
                for k, v in v_metrics.counts_by_class.items()
            ])
            st.markdown(f"<div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px;'>{cls_items}</div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 2: PHYSICAL SENSOR FLEET
    # =========================================================================
    with t_sensors:
        st.markdown("### 📡 Physical Sensor Integration & Hardware Adapters")
        st.caption("Standardized modular adapters for PIR motion, IR break-beam, mmWave radar, Doppler vehicle speed radar, and inductive loop detectors.")

        sensor_list = svc.get_sensors()
        s_cols = st.columns(3)

        for idx, s in enumerate(sensor_list):
            with s_cols[idx % 3]:
                hw_badge = "🟢 HARDWARE" if s["is_hardware"] else "🟡 SIMULATED"
                stale_badge = "🔴 STALE" if s["is_stale"] else "🟢 FRESH"
                meas_text = "<br>".join([f"• <b>{k}:</b> {v}" for k, v in (s["last_reading"] or {}).items() if k != "measurement_note"])
                note = (s["last_reading"] or {}).get("measurement_note", "")

                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(56, 189, 248, 0.25); border-radius: 12px; padding: 14px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 0.85rem; font-weight: 800; color: #f8fafc;">{s['sensor_id']}</span>
                        <span style="font-size: 0.65rem; background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 2px 6px; border-radius: 4px; font-family: monospace;">{s['sensor_type']}</span>
                    </div>
                    <div style="font-size: 0.70rem; color: #94a3b8; margin-bottom: 8px;">
                        Zone: <code style="color: #cbd5e1;">{s['zone_id']}</code> | Env: {s['environment_type']}
                    </div>
                    <div style="background: rgba(0, 0, 0, 0.3); border-radius: 8px; padding: 8px; font-size: 0.72rem; color: #e2e8f0; margin-bottom: 8px; min-height: 55px;">
                        {meas_text if meas_text else '<i>Waiting for first reading packet...</i>'}
                    </div>
                    {f"<div style='font-size: 0.65rem; color: #f59e0b; margin-bottom: 6px;'>⚠️ {note}</div>" if note else ""}
                    <div style="display: flex; justify-content: space-between; font-size: 0.68rem; color: #94a3b8; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px;">
                        <span>{hw_badge}</span>
                        <span>{stale_badge}</span>
                        <span>Conf: <b>{int(s['confidence']*100)}%</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### ⚡ Interactive Sensor Event Injection (Hardware Simulation Testing)")
        st.caption("Trigger or inject test events to observe real-time sensor fusion reactions without physical hardware.")

        inj_c1, inj_c2, inj_c3 = st.columns([1.5, 1.5, 1.0])
        with inj_c1:
            inj_sensor = st.selectbox("Target Sensor:", [s["sensor_id"] for s in sensor_list], key="inj_sensor_sel")
        with inj_c2:
            inj_val = st.number_input("Speed / Count / Pulse Value:", value=85.0, step=5.0, key="inj_val_input")
        with inj_c3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("📤 Inject Event", key="btn_inject_sensor_event", use_container_width=True, type="primary"):
                if "RADAR" in inj_sensor:
                    payload = {"measured_speed_kmh": inj_val, "status": "ONLINE", "confidence": 0.98}
                elif "MMWAVE" in inj_sensor:
                    payload = {"people_count": int(inj_val), "status": "ONLINE", "confidence": 0.95}
                elif "LOOP" in inj_sensor:
                    payload = {"occupancy_pct": inj_val, "status": "ONLINE", "confidence": 0.96}
                else:
                    payload = {"motion_detected": True, "pulse_intensity": 0.99, "status": "ONLINE"}

                res = svc.post_sensor_event({"sensor_id": inj_sensor, "measurements": payload})
                st.toast(f"Injected reading into {inj_sensor}!", icon="📡")
                st.rerun()

    # =========================================================================
    # TAB 3: SENSOR FUSION & CONFLICT STUDIO
    # =========================================================================
    with t_fusion:
        st.markdown("### ⚖️ Multi-Modal Sensor Fusion & Conflict Resolution")
        st.caption("Combines camera detections with physical radar and in-pavement loops. Deduplicates observations and explicitly flags conflicting readings.")

        f_zone = st.selectbox(
            "Select Evaluation Zone:",
            ["SEG_EXPRESSWAY_01", "SEG_GUNTUR_BYPASS", "ZONE_ENTRANCE_NORTH", "ZONE_MALL_ATRIUM"],
            key="fusion_zone_sel"
        )
        fused = svc.fusion_engine.fuse(zone_id=f_zone)

        col_f_summary, col_f_conflicts = st.columns([1.3, 1.2])

        with col_f_summary:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.92) 0%, rgba(30, 41, 59, 0.82) 100%);
                        border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 14px; padding: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div>
                        <div style="font-size: 1.05rem; font-weight: 800; color: #f8fafc;">{fused.zone_id}</div>
                        <div style="font-size: 0.72rem; color: #94a3b8;">Environment: {fused.environment_type}</div>
                    </div>
                    <span style="font-size: 0.72rem; font-weight: 800; color: #34d399; background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; padding: 3px 8px; border-radius: 8px;">
                        CONGESTION: {fused.congestion_level}
                    </span>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px;">
                    <div style="background: rgba(255,255,255,0.04); padding: 8px; border-radius: 8px;">
                        <div style="font-size: 0.68rem; color: #94a3b8;">FUSED ACTIVE COUNT</div>
                        <div style="font-size: 1.3rem; font-weight: 800; color: #38bdf8;">
                            {fused.pedestrian_count if fused.environment_type == 'INDOOR' else fused.vehicle_count}
                            <span style="font-size: 0.75rem; color: #94a3b8;">{('people' if fused.environment_type == 'INDOOR' else 'vehicles')}</span>
                        </div>
                    </div>
                    <div style="background: rgba(255,255,255,0.04); padding: 8px; border-radius: 8px;">
                        <div style="font-size: 0.68rem; color: #94a3b8;">VERIFIED / EST. SPEED</div>
                        <div style="font-size: 1.3rem; font-weight: 800; color: #34d399;">
                            {fused.measured_speed_kmh or fused.estimated_speed_kmh}
                            <span style="font-size: 0.75rem; color: #94a3b8;">km/h</span>
                        </div>
                    </div>
                </div>
                <div style="font-size: 0.75rem; color: #cbd5e1; margin-bottom: 8px;">
                    <b>Congestion Rule:</b> {fused.congestion_explanation}
                </div>
                <div style="font-size: 0.72rem; color: #94a3b8;">
                    <b>Contributing Sources:</b> {', '.join(fused.contributing_sources)}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_f_conflicts:
            st.markdown("#### 🔍 Disagreement & Health Watchdog")
            if fused.active_disagreements:
                for dis in fused.active_disagreements:
                    st.error(f"⚠️ **SENSOR CONFLICT DETECTED:** {dis}")
                st.caption("When sensors report conflicting observations, NexRoute lowers the overall confidence score rather than inventing a false consensus.")
            else:
                st.success("✅ **Sensor Consensus Optimal:** Camera detections and physical sensor telemetry correlate within valid tolerance limits.")

            st.metric("Aggregate Sensor Confidence", f"{int(fused.aggregate_confidence * 100)}%", delta=f"{len(fused.contributing_sources)} sources fused")

    # =========================================================================
    # TAB 4: TRAFFIC ANALYTICS & PREDICTOR
    # =========================================================================
    with t_analytics:
        st.markdown("### 📊 Corridor Analytics, AI Forecasting & Historical Benchmarks")
        st.caption("Inspects road telemetry, evaluates 15/30/60-minute predictions, and benchmarks model accuracy against empirical baselines.")

        col_inspect, col_pred = st.columns([1.1, 1.2])
        with col_inspect:
            st.markdown("#### 🔍 Live Road Segment Inspector")
            seg_options = {s["name"]: s for s in DEMO_SEGMENTS}
            selected_seg_name = st.selectbox("Select Road Corridor:", list(seg_options.keys()), key="traffic_seg_select_tab4")
            selected_seg = seg_options[selected_seg_name]

            state = TrafficFusionService.estimate_segment_traffic(
                segment_id=selected_seg["id"],
                free_flow_speed_kmh=selected_seg["free_flow_kmh"],
                length_meters=selected_seg["length_meters"],
                road_class=selected_seg["road_type"]
            )

            color_hex_map = {"green": "#22c55e", "amber": "#eab308", "red": "#ef4444", "dark_red": "#881337", "grey": "#64748b"}
            accent_color = color_hex_map.get(state.congestion_color, "#38bdf8")

            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.88); border: 1.5px solid {accent_color}; border-radius: 12px; padding: 14px; margin-top: 6px;">
                <div style="font-size: 1.05rem; font-weight: 800; color: #f8fafc;">{selected_seg['name']}</div>
                <div style="font-size: 0.72rem; color: #94a3b8; font-family: monospace;">ID: {selected_seg['id']} • {selected_seg['road_type']}</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px;">
                    <div>Speed: <b style="color: {accent_color}; font-size: 1.2rem;">{state.current_speed_kmh} km/h</b></div>
                    <div>Traversal: <b style="color: #38bdf8; font-size: 1.2rem;">{round(state.traversal_time_seconds / 60.0, 1)} min</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_pred:
            st.markdown("#### 🤖 AI Multi-Horizon Predictor")
            c_horiz, c_weath = st.columns(2)
            with c_horiz:
                horizon = st.select_slider("Horizon:", [15, 30, 60], value=15, format_func=lambda x: f"+{x}m", key="pred_horizon_tab4")
            with c_weath:
                weather_sel = st.selectbox("Weather:", ["Clear & Dry", "Light Rain", "Heavy Thunderstorm", "Dense Fog"], key="pred_weath_tab4")

            pred = TrafficPredictionService.predict_segment_traffic(
                segment_id=selected_seg["id"],
                free_flow_speed_kmh=selected_seg["free_flow_kmh"],
                length_meters=selected_seg["length_meters"],
                road_class=selected_seg["road_type"],
                horizon_minutes=horizon,
                weather_condition=weather_sel
            )

            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.88); border: 1.5px solid #a855f7; border-radius: 12px; padding: 14px; margin-top: 6px;">
                <div style="font-size: 0.95rem; font-weight: 800; color: #f8fafc;">Forecast at +{horizon}m ({pred.target_time.strftime('%H:%M UTC')})</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px;">
                    <div>Expected Speed: <b style="color: #c084fc; font-size: 1.2rem;">{pred.expected_speed_kmh} km/h</b></div>
                    <div>Travel Time: <b style="color: #38bdf8; font-size: 1.2rem;">{round(pred.expected_travel_time_seconds / 60.0, 1)} min</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # =========================================================================
    # TAB 5: ROUTE ADVISORY & OLLAMA AI ASSISTANT GROUNDING
    # =========================================================================
    with t_advisory:
        st.markdown("### 🗺️ Route Advisory & Ollama AI Travel Assistant Grounding")
        st.caption("Feeds validated live sensor observations into route planning and ensures the Ollama chatbot answers live traffic questions without hallucination.")

        adv = svc.get_route_traffic_advisory()
        if adv["reroute_recommended"]:
            st.warning(f"🚨 **REROUTE ADVISORY:** {adv['advisory_message']}")
        else:
            st.success(f"✅ **ROUTE CLEAR:** {adv['advisory_message']}")

        st.markdown("#### 🤖 Grounded Ollama Context (No Hallucination)")
        st.caption("Copy or inspect the exact live sensor state injected into the Ollama Travel Assistant prompt:")
        ollama_ctx = svc.build_ollama_traffic_context()
        st.code(ollama_ctx, language="yaml")
