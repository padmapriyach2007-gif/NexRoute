import sys
import os
import types
from pathlib import Path

# Ensure ROOT_DIR and SRC_DIR are at front of sys.path
_ROOT_DIR = Path(__file__).resolve().parent
_SRC_DIR = _ROOT_DIR / "src"

for _p in [str(_ROOT_DIR), str(_SRC_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Guard against Streamlit Cloud (/mount/src/<repo>) namespace shadowing
if "src" in sys.modules:
    _src_mod = sys.modules["src"]
    if not hasattr(_src_mod, "__file__") or _src_mod.__file__ is None:
        if hasattr(_src_mod, "__path__"):
            _src_mod.__path__.insert(0, str(_SRC_DIR))
else:
    _src_pkg = types.ModuleType("src")
    _src_pkg.__file__ = str(_SRC_DIR / "__init__.py")
    _src_pkg.__path__ = [str(_SRC_DIR)]
    _src_pkg.__package__ = "src"
    sys.modules["src"] = _src_pkg

import streamlit as st
import time
import datetime
import zoneinfo
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import re
import base64
from PIL import Image

try:
    from src.pipeline import CampusSpherePipeline as CampusAegisPipeline
except (ImportError, ModuleNotFoundError):
    import importlib
    CampusAegisPipeline = importlib.import_module("pipeline").CampusSpherePipeline


from src.visualizer import create_3d_building_figure, create_2d_campus_map
from src.planning_agent import EvacuationPlanningCSP, EvacuationGroup
from src.chatbot_agent import AegisChatbotAgent
from src.pathfinder_chatbot import PathfinderChatbot
from src.safety_monitor import SystemSafetyState
import streamlit.components.v1 as components
from src.voice_guidance import generate_simple_spoken_narrative, build_voice_assistant_html
from src.google_maps_voice_navigator import prepare_google_maps_voice_data, render_google_maps_voice_navigator_html
from src.game_journey_stepper import extract_journey_game_milestones, build_game_journey_html, detect_crossed_milestones
from src.journey_storyteller import (
    generate_friendly_virtual_guide_turns,
    build_virtual_guide_turns_html
)
from src.virtual_3d_walking_guide import (
    build_3d_walking_guide_html,
    WalkingGuideState,
    Route3DGeometryEngine,
    WalkingGuideAnimationController
)
from src.realtime_motion_sync import (
    build_realtime_motion_hud_html,
    RealtimeMotionEngine,
    RealtimeMotionState,
    LocationObservation
)
from src.emergency_radar_ui import (
    generate_google_maps_directions_url,
    filter_facilities_by_category,
    get_facility_status_badge
)
from src.virtual_companion_ui import build_virtual_companion_hud_html
from src.virtual_human_guide import (
    build_always_visible_virtual_guide_html,
    VirtualHumanGuideController,
    HumanGuideState,
    GuideEventType
)
from src.satellite_road_auditor import SatelliteRoadAuditor, SatelliteAuditResult
from src.satellite_road_cv import (
    AIRoadIntelligenceController,
    render_ai_road_intelligence_hud_html,
    AVAILABLE_SATELLITE_PROVIDERS
)
from dataclasses import asdict
from src.navigation_trust_audit import (
    NavigationTrustAuditEngine,
    NavigationTrustAuditResult,
    render_navigation_trust_audit_card_html,
    render_navigation_trust_audit_details_html
)
from src.google_maps_features import (
    get_google_maps_app_url,
    get_google_maps_loopholes_data,
    build_google_maps_toolbar_html,
    build_loopholes_deck_html
)

from src.facilities_service import (
    get_facilities_for_category,
    resolve_custom_search_facility,
    CATEGORY_CONFIG,
    FacilityCategory
)
from src.google_maps_platform import (
    get_google_maps_api_key,
    is_google_maps_key_configured,
    load_and_georeference_saved_locations,
    build_google_maps_javascript_html,
    geocode_with_google_api
)
from src.places_and_driving_modes import (
    generate_suggested_places_at_location,
    compare_driving_travel_modes,
    render_place_details_card_html,
    render_driving_mode_cockpit_card_html,
    render_cockpit_mode_functionality_hud,
    render_profile_calculation_details_html
)
from src.transit_kinematics import (
    calculate_transit_kinematics,
    render_transit_kinematics_hud_html,
    render_transit_kinematics_live_ticker_component,
    resolve_timezone,
    TIMEZONE_CATALOG,
    VEHICLE_KINEMATIC_PROFILES
)


# Page configuration
st.set_page_config(
    page_title="P.A.T.H.F.I.N.D.E.R. • Predictive Adaptive Transit & Hazard-Free Routing",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Globally cancel and disable any browser speech synthesis / AI voice per user configuration
components.html("""
<script>
(function() {
    try {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak = function() {};
        }
    } catch(e) {}
})();
</script>
""", height=0, width=0)

# Load Authentic Brand Logo & Custom Futuristic Background
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "pathfinder_logo.jpg")
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "campus_aegis_logo.jpg")
logo_data_uri = ""
logo_thumb_uri = ""
logo_pil = None
if os.path.exists(LOGO_PATH):
    with open(LOGO_PATH, "rb") as f:
        logo_data_uri = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
    try:
        logo_pil = Image.open(LOGO_PATH)
    except Exception:
        pass

LOGO_THUMB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "pathfinder_logo_thumb.png")
if os.path.exists(LOGO_THUMB_PATH):
    with open(LOGO_THUMB_PATH, "rb") as f:
        logo_thumb_uri = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
else:
    logo_thumb_uri = logo_data_uri

AURA_LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "aura_chatbot_logo_thumb.png")
if not os.path.exists(AURA_LOGO_PATH):
    AURA_LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "aura_chatbot_logo.png")
aura_logo_uri = ""
if os.path.exists(AURA_LOGO_PATH):
    with open(AURA_LOGO_PATH, "rb") as f:
        aura_logo_uri = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
else:
    aura_logo_uri = logo_thumb_uri

BG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "navigation_bg.jpg")
bg_data_uri = ""
if os.path.exists(BG_PATH):
    with open(BG_PATH, "rb") as f:
        bg_data_uri = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"

if bg_data_uri:
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: #050b14 !important;
            background-image: 
                linear-gradient(180deg, rgba(5, 11, 20, 0.60) 0%, rgba(5, 11, 20, 0.35) 45%, rgba(5, 11, 20, 0.72) 100%),
                url('{bg_data_uri}') !important;
            background-size: cover, cover !important;
            background-position: center top, center top !important;
            background-repeat: no-repeat, no-repeat !important;
            background-attachment: fixed, fixed !important;
            color: #f1f5f9;
        }}

        /* Seamless Translucent Digital-Twin Sidebar */
        section[data-testid="stSidebar"] {{
            background: 
                linear-gradient(180deg, rgba(8, 15, 28, 0.88) 0%, rgba(10, 20, 36, 0.84) 100%),
                url('{bg_data_uri}') !important;
            background-size: cover !important;
            background-position: left center !important;
            background-attachment: fixed !important;
            backdrop-filter: blur(24px) saturate(180%);
            -webkit-backdrop-filter: blur(24px) saturate(180%);
            border-right: 1px solid rgba(56, 189, 248, 0.16) !important;
            box-shadow: 6px 0 32px rgba(0, 0, 0, 0.65);
        }}
    </style>
    """, unsafe_allow_html=True)

# Custom Cyber-Dark Styling: High Contrast, Glassmorphism, Emergency HUD
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

    html {
        scroll-behavior: smooth;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Sleek Translucent Input Controls & Containers */
    div[data-baseweb="input"] {
        background-color: rgba(10, 20, 36, 0.65) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(56, 189, 248, 0.28) !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
        transition: all 0.25s ease !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 18px rgba(56, 189, 248, 0.38) !important;
    }
    div[data-baseweb="select"] > div {
        background-color: rgba(10, 20, 36, 0.65) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(56, 189, 248, 0.28) !important;
        border-radius: 8px !important;
    }

    /* Polished Interactive Leaflet Map Wrapper */
    iframe[title="streamlit_folium.st_folium"] {
        border-radius: 12px !important;
        border: 1px solid rgba(56, 189, 248, 0.35) !important;
        box-shadow: 0 10px 36px -4px rgba(14, 165, 233, 0.28), 0 0 20px rgba(0, 0, 0, 0.7) !important;
    }

    /* Remove Layer Control Box - Keep Only Pure Satellite View */
    .leaflet-control-layers,
    .leaflet-control-layers-expanded,
    div.leaflet-control-layers {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* Button Hover Enhancements */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton > button:hover {
        transform: translateY(-1.5px);
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.32) !important;
    }

    /* Clear High-Contrast Sidebar Objective Buttons */
    section[data-testid="stSidebar"] .stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.02em !important;
        padding: 9px 14px !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        background: rgba(13, 24, 43, 0.82) !important;
        color: #f8fafc !important;
        text-align: left !important;
        justify-content: flex-start !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
        backdrop-filter: blur(10px) !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        border-color: #38bdf8 !important;
        background: rgba(14, 165, 233, 0.25) !important;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.38) !important;
        transform: translateY(-1px) !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.90) 0%, rgba(16, 185, 129, 0.82) 100%) !important;
        border: 1.5px solid #38bdf8 !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.45) !important;
    }

    /* Compact horizontal button grid (Distance Units) */
    section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] .stButton > button {
        text-align: center !important;
        justify-content: center !important;
        padding: 8px 4px !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.01em !important;
        white-space: nowrap !important;
    }

    /* =========================================================================
       ULTRA-PREMIUM GLASSMORPHIC TAB NAVIGATION SYSTEM
       ========================================================================= */
    div[data-testid="stTabs"] [data-baseweb="tab-list"],
    .stTabs [data-baseweb="tab-list"],
    div[data-baseweb="tab-list"],
    div[role="tablist"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.92) 0%, rgba(30, 41, 59, 0.80) 100%) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1.5px solid rgba(56, 189, 248, 0.28) !important;
        border-radius: 16px !important;
        padding: 6px 8px !important;
        gap: 8px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 10px 32px -4px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
        display: flex !important;
        align-items: center !important;
        width: fit-content !important;
        max-width: 100% !important;
        overflow-x: auto !important;
    }

    /* Completely eliminate default bottom lines, borders, and moving underline */
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
    div[data-testid="stTabs"] [data-baseweb="tab-border"],
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"],
    [data-baseweb="tab-highlight"],
    [data-baseweb="tab-border"],
    div[role="tablist"] > div[style*="position: absolute"],
    div[role="tablist"] > div[style*="bottom: 0"],
    div[role="tablist"] > div[style*="bottom:0"] {
        display: none !important;
        opacity: 0 !important;
        height: 0 !important;
        width: 0 !important;
        border: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }

    /* Tab Buttons - Segmented Floating Pills (div[role="tab"] and button[role="tab"]) */
    div[data-testid="stTabs"] [role="tab"],
    div[data-testid="stTabs"] div[role="tab"],
    div[data-testid="stTabs"] button[role="tab"],
    div[role="tablist"] [role="tab"],
    [data-baseweb="tab"],
    [role="tab"] {
        height: auto !important;
        min-height: 42px !important;
        padding: 9px 22px !important;
        border-radius: 12px !important;
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #94a3b8 !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        outline: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
        white-space: nowrap !important;
        box-shadow: none !important;
    }

    /* Text inside tabs */
    div[data-testid="stTabs"] [role="tab"] p,
    div[data-testid="stTabs"] [role="tab"] span,
    [role="tab"] p,
    [role="tab"] span {
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
        color: inherit !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.3 !important;
    }

    /* Tab Hover State */
    div[data-testid="stTabs"] [role="tab"]:hover,
    div[role="tablist"] [role="tab"]:hover,
    [role="tab"]:hover {
        color: #f8fafc !important;
        background: rgba(56, 189, 248, 0.16) !important;
        border: 1px solid rgba(56, 189, 248, 0.50) !important;
        border-bottom: 1px solid rgba(56, 189, 248, 0.50) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 18px rgba(56, 189, 248, 0.25) !important;
    }

    /* Active Selected Tab Pill - Complete Glow Pill with zero underline */
    div[data-testid="stTabs"] [role="tab"][aria-selected="true"],
    div[data-testid="stTabs"] div[role="tab"][aria-selected="true"],
    div[role="tablist"] [role="tab"][aria-selected="true"],
    [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(2, 132, 199, 0.60) 0%, rgba(14, 165, 233, 0.40) 100%) !important;
        border: 1.5px solid #38bdf8 !important;
        border-bottom: 1.5px solid #38bdf8 !important;
        color: #ffffff !important;
        box-shadow: 0 0 24px rgba(56, 189, 248, 0.50), inset 0 1px 0 rgba(255, 255, 255, 0.35) !important;
        font-weight: 800 !important;
    }

    div[data-testid="stTabs"] [role="tab"]:focus,
    [role="tab"]:focus {
        outline: none !important;
    }

    /* Autonomous Guidance Large-Text Banner */
    .guidance-banner {
        border-radius: 14px;
        padding: 18px 24px;
        margin-bottom: 18px;
        border-width: 2px;
        border-style: solid;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    .guidance-green {
        background: linear-gradient(135deg, rgba(6, 78, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border-color: #10b981;
    }
    .guidance-amber {
        background: linear-gradient(135deg, rgba(120, 53, 15, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border-color: #f59e0b;
    }
    .guidance-red {
        background: linear-gradient(135deg, rgba(127, 29, 29, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
        border-color: #ef4444;
    }

    /* HUD Badges */
    .badge-hud-ready {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        color: #34d399;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        text-transform: uppercase;
    }
    .badge-hud-danger {
        background: rgba(239, 68, 68, 0.2);
        border: 1px solid #ef4444;
        color: #f87171;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        text-transform: uppercase;
        animation: pulse 1.8s infinite;
    }
    .badge-hud-amber {
        background: rgba(245, 158, 11, 0.2);
        border: 1px solid #f59e0b;
        color: #fbbf24;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        text-transform: uppercase;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.65; }
    }

    .proof-step-box {
        background: rgba(15, 23, 42, 0.75);
        border-left: 4px solid #38bdf8;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 0 8px 8px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.86rem;
        color: #e2e8f0;
    }

    /* Futuristic Cyber Objective Selector Cards */
    div[data-testid="stRadio"] {
        margin-top: 4px;
        margin-bottom: 8px;
    }
    div[data-testid="stRadio"] > label {
        font-size: 0.74rem !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: #38bdf8 !important;
        margin-bottom: 8px !important;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] {
        background: rgba(13, 27, 46, 0.76) !important;
        border: 1px solid rgba(56, 189, 248, 0.18) !important;
        border-left: 3px solid rgba(56, 189, 248, 0.45) !important;
        border-radius: 10px !important;
        padding: 9px 12px !important;
        margin: 0 !important;
        width: 100% !important;
        box-sizing: border-box !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
        cursor: pointer !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        align-items: flex-start !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
        border-color: rgba(56, 189, 248, 0.65) !important;
        border-left: 4px solid #38bdf8 !important;
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.20) 0%, rgba(30, 58, 95, 0.65) 100%) !important;
        transform: translateX(2px);
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.28), inset 0 0 10px rgba(56, 189, 248, 0.1) !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked),
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has([aria-checked="true"]),
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input[checked]) {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.28) 0%, rgba(16, 185, 129, 0.20) 100%) !important;
        border: 1.5px solid #38bdf8 !important;
        border-left: 5px solid #38bdf8 !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.38), inset 0 0 14px rgba(56, 189, 248, 0.16) !important;
        transform: translateX(3px) !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] p {
        font-weight: 700 !important;
        color: #f1f5f9 !important;
        font-size: 0.86rem !important;
        margin-bottom: 2px !important;
        letter-spacing: 0.01em !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) p {
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.7) !important;
    }
    div[data-testid="stRadio"] [data-testid="stCaptionContainer"] {
        color: #94a3b8 !important;
        font-size: 0.72rem !important;
        line-height: 1.3 !important;
        margin-top: -1px !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) [data-testid="stCaptionContainer"] {
        color: #bae6fd !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] div:first-child {
        margin-top: 3px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) div:first-child {
        filter: drop-shadow(0 0 6px #38bdf8);
    }

    /* Touchable Route Cards */
    /* Touchable Route Cards */
    .touchable-route-link {
        text-decoration: none !important;
        color: inherit !important;
        display: block !important;
        cursor: pointer !important;
        outline: none !important;
    }
    .touchable-route-card {
        cursor: pointer !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        user-select: none !important;
        -webkit-tap-highlight-color: transparent !important;
    }
    .touchable-route-link:hover .touchable-route-card,
    .touchable-route-card:hover {
        transform: translateY(-4px) scale(1.015) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7), 0 0 24px rgba(56, 189, 248, 0.45) !important;
        border-color: rgba(56, 189, 248, 0.6) !important;
    }
    .touchable-route-link:active .touchable-route-card,
    .touchable-route-card:active {
        transform: translateY(-1px) scale(0.99) !important;
    }

    /* Floating Circular Chatbot FAB (Strict Bottom-Right) */
    [data-testid="stElementContainer"]:has([data-testid="stPopover"]),
    [data-testid="stElementContainer"]:has(button[aria-haspopup="dialog"]) {
        position: fixed !important;
        bottom: 24px !important;
        right: 24px !important;
        left: auto !important;
        top: auto !important;
        width: 64px !important;
        height: 64px !important;
        z-index: 9999999 !important;
        background: transparent !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stPopover"] {
        position: fixed !important;
        bottom: 24px !important;
        right: 24px !important;
        left: auto !important;
        top: auto !important;
        width: 64px !important;
        height: 64px !important;
        z-index: 9999999 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stPopover"] > button,
    div[data-testid="stPopover"] button,
    button[aria-haspopup="dialog"] {
        width: 64px !important;
        height: 64px !important;
        min-width: 64px !important;
        min-height: 64px !important;
        border-radius: 50% !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        overflow: hidden !important;
        opacity: 0 !important;
    }
    div[data-testid="stPopover"] > button:hover,
    div[data-testid="stPopover"] button:hover,
    button[aria-haspopup="dialog"]:hover {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    /* Floating A.U.R.A. AI Chatbot Logo Overlay */
    .floating-aura-logo-overlay {
        position: fixed !important;
        bottom: 24px !important;
        right: 24px !important;
        width: 64px !important;
        height: 64px !important;
        border-radius: 50% !important;
        border: 2px solid #38bdf8 !important;
        box-shadow: 0 0 24px rgba(56, 189, 248, 0.75), 0 8px 22px rgba(0, 0, 0, 0.85) !important;
        pointer-events: none !important;
        z-index: 9999998 !important;
        object-fit: cover !important;
        animation: aura-fab-glow 2.8s infinite alternate ease-in-out !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background-color: #040d1a !important;
    }
    body:has(div[data-testid="stPopover"] > button:hover) .floating-aura-logo-overlay,
    div[data-testid="stPopover"]:hover ~ .floating-aura-logo-overlay {
        transform: scale(1.12) translateY(-3px) !important;
        border-color: #7dd3fc !important;
        box-shadow: 0 0 35px rgba(56, 189, 248, 0.95), 0 10px 28px rgba(0, 0, 0, 0.85) !important;
    }
    /* Strictly remove the dropdown caret / chevron down symbol and any inner label text/divs */
    div[data-testid="stPopover"] > button svg,
    div[data-testid="stPopover"] button svg,
    button[aria-haspopup="dialog"] svg,
    div[data-testid="stPopover"] > button div,
    button[aria-haspopup="dialog"] div,
    div[data-testid="stPopover"] > button span,
    button[aria-haspopup="dialog"] span,
    div[data-testid="stPopover"] > button p,
    button[aria-haspopup="dialog"] p {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        font-size: 0 !important;
        pointer-events: none !important;
    }
    @keyframes aura-fab-glow {
        0% { box-shadow: 0 0 14px rgba(56, 189, 248, 0.4), 0 4px 14px rgba(0,0,0,0.6); }
        100% { box-shadow: 0 0 30px rgba(56, 189, 248, 0.85), 0 0 10px #38bdf8, 0 8px 22px rgba(0,0,0,0.8); }
    }

    /* Popover Content Dialog Window */
    div[data-testid="stPopoverBody"] {
        background: rgba(7, 17, 31, 0.97) !important;
        backdrop-filter: blur(24px) saturate(190%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(190%) !important;
        border: 1.5px solid rgba(56, 189, 248, 0.45) !important;
        border-radius: 18px !important;
        box-shadow: 0 24px 64px rgba(0, 0, 0, 0.95), 0 0 32px rgba(14, 165, 233, 0.28) !important;
        max-width: 440px !important;
        width: 420px !important;
        max-height: 580px !important;
        overflow-y: auto !important;
        padding: 16px !important;
        z-index: 100000000 !important;
    }
    /* =========================================================================
       RESPONSIVE & MOBILE-FIRST DESIGN ENHANCEMENTS
       ========================================================================= */
    @media (max-width: 992px) {
        /* Tablet adjustments */
        .st-key-fleet_deck_container div[data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: repeat(4, 1fr) !important;
            gap: 6px !important;
        }
        .st-key-speed_deck_container div[data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 6px !important;
        }
    }

    @media (max-width: 768px) {
        /* Mobile Touch & Accessibility Standards */
        .stButton > button {
            min-height: 44px !important;
            font-size: 0.86rem !important;
            touch-action: manipulation !important;
        }
        /* Mobile Fleet Deck - 3 column responsive grid */
        .st-key-fleet_deck_container div[data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 6px !important;
        }
        .st-key-fleet_deck_container div[data-testid="stButton"] > button {
            height: 52px !important;
            min-height: 52px !important;
        }
        /* Mobile Map Viewport Full-Width */
        iframe[title="streamlit_folium.st_folium"],
        div[data-testid="stIFrame"] iframe {
            border-radius: 8px !important;
            width: 100% !important;
            max-width: 100% !important;
        }
        /* Mobile Route Cards */
        .touchable-route-card {
            padding: 12px !important;
            margin-bottom: 8px !important;
        }
        /* Mobile Tabs navigation */
        div[data-testid="stTabs"] [role="tab"] {
            padding: 7px 14px !important;
            font-size: 0.85rem !important;
        }
        /* Chatbot FAB responsive offset */
        [data-testid="stElementContainer"]:has([data-testid="stPopover"]),
        div[data-testid="stPopover"],
        .floating-aura-logo-overlay {
            bottom: 16px !important;
            right: 16px !important;
            width: 56px !important;
            height: 56px !important;
        }
    }
    /* Hide Leaflet bottom attribution bar */
    .leaflet-control-attribution {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
GRAPH_VERSION = "v8_event_driven_pipeline"
if "pipeline" not in st.session_state or st.session_state.get("graph_version") != GRAPH_VERSION:
    st.session_state.pipeline = CampusAegisPipeline()
    st.session_state.graph_version = GRAPH_VERSION

pipeline: CampusAegisPipeline = st.session_state.pipeline

if "active_start_node" not in st.session_state:
    st.session_state.active_start_node = "VIG_ENGI_CHEMICAL_REACTION_ENGG_"

if "requires_accessible" not in st.session_state:
    st.session_state.requires_accessible = False

# =========================================================================
# REAL-WORLD NAVIGATION & CORE SERVICES IMPORTS & SINGLETONS
# =========================================================================

import importlib
import src.map_service
importlib.reload(src.map_service)
from src.map_service import MapService

from src.hazard_map import haversine_distance_m
from src.route_engine import RealWorldRouteEngine, TravelMode
from src.location_service import LocationService, LocationSource, LocationPermissionStatus
from src.notification_service import NotificationService, NotificationPriority
from src.road_condition_model import (
    RoadRestriction,
    TrafficCondition,
    RestrictionType,
    TrafficSeverity,
    OperatingMode,
    OptimizationObjective
)
from src.road_condition_manager import RoadConditionManager
from src.multi_objective_router import MultiObjectiveRouter, RouteEligibilityStatus
from src.hazard_map import HazardMap, GeographicHazard, HazardSeverity
from src.operator_manager import OperatorManager
from src.communication_adapters import MultiChannelDispatcher, DeliveryStatus
from src.eoc_view import render_emergency_operations_center
from streamlit_folium import st_folium
from src.emergency_service import EmergencyServiceManager, FacilityCategory as EmergencyFacilityCategory, get_national_emergency_contacts

# Unit formatting helpers for complete metric (km) and imperial (miles) functionality
def format_distance(dist_km: float, unit: str = "km") -> str:
    if str(unit).lower() in ("miles", "mi", "mile"):
        return f"{dist_km * 0.621371:.2f} mi"
    return f"{dist_km:.2f} km"

def adapt_tradeoff_text(text: str, unit: str = "km") -> str:
    if str(unit).lower() not in ("miles", "mi", "mile") or not text:
        return text
    import re
    def _repl(match):
        val = float(match.group(1))
        return f"{val * 0.621371:.2f} mi"
    return re.sub(r'(\d+(?:\.\d+)?)\s*km\b', _repl, text)

@st.cache_data(ttl=900, show_spinner=False)
def detect_user_network_location() -> dict:
    """
    Returns authentic baseline user location.
    Prioritizes real device location, with fallback to regional coordinate anchor.
    """
    return {
        "lat": 16.23454,
        "lon": 80.65197,
        "city": "Current Location",
        "label": "📍 Current Location"
    }

# Instantiate Real-World Singleton Services in Session State
st.session_state.real_map_service = MapService()
if "real_hazard_map" not in st.session_state:
    st.session_state.real_hazard_map = HazardMap()
if "operator_manager" not in st.session_state:
    st.session_state.operator_manager = OperatorManager()
if "comm_dispatcher" not in st.session_state:
    st.session_state.comm_dispatcher = MultiChannelDispatcher()
if "road_condition_manager" not in st.session_state or not hasattr(st.session_state.road_condition_manager, "get_demo_scenarios"):
    st.session_state.road_condition_manager = RoadConditionManager(initial_mode=OperatingMode.LIVE_ROUTING)
if "emergency_service_manager" not in st.session_state:
    st.session_state.emergency_service_manager = EmergencyServiceManager(enable_live_osm=True)

# Instantiate Satellite Road Auditor (Verifies real physical barriers and eliminates fake blockages)
if "satellite_auditor" not in st.session_state:
    st.session_state.satellite_auditor = SatelliteRoadAuditor(enable_live_osm=True)

# Instantiate AI Satellite Road Intelligence Controller (Computer Vision & Road Network Cross-Validation)
if "ai_road_controller" not in st.session_state:
    st.session_state.ai_road_controller = AIRoadIntelligenceController(
        provider_key=st.session_state.get("ai_sat_provider", "esri_world_imagery"),
        enable_tile_network=True
    )

# Ensure RoadConditionManager & HazardMap run on authentic live data without fabricated closures
st.session_state.road_condition_manager.clear_demonstration_data()
if "multi_objective_router" not in st.session_state or getattr(st.session_state.multi_objective_router, "hazard_map", None) is None:
    st.session_state.multi_objective_router = MultiObjectiveRouter(
        road_condition_manager=st.session_state.road_condition_manager,
        hazard_map=st.session_state.real_hazard_map
    )
if "real_route_engine" not in st.session_state:
    st.session_state.real_route_engine = RealWorldRouteEngine()
if "real_location_service" not in st.session_state or not hasattr(st.session_state.real_location_service, "record_movement"):
    st.session_state.real_location_service = LocationService()
if "active_objective" not in st.session_state:
    st.session_state.active_objective = OptimizationObjective.FASTEST

# Load Tour Sections for Sidebar & Explorer
APP_DIR = os.path.dirname(os.path.abspath(__file__))
tour_file_path = os.path.join(APP_DIR, 'vignan_tour_locations.json')
if not os.path.exists(tour_file_path):
    tour_file_path = 'vignan_tour_locations.json'

tour_meta = {"total": 0, "sections": {}, "all_items": []}
if os.path.exists(tour_file_path):
    try:
        with open(tour_file_path, 'r', encoding='utf-8') as f:
            tour_meta = json.load(f)
    except Exception:
        pass

# Custom user saved/favourite places persistence
CUSTOM_SAVED_PLACES_PATH = os.path.join(APP_DIR, "data", "custom_saved_places.json")
os.makedirs(os.path.join(APP_DIR, "data"), exist_ok=True)

def load_user_custom_saved_places():
    if os.path.exists(CUSTOM_SAVED_PLACES_PATH):
        try:
            with open(CUSTOM_SAVED_PLACES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_user_custom_saved_places(places):
    try:
        with open(CUSTOM_SAVED_PLACES_PATH, "w", encoding="utf-8") as f:
            json.dump(places, f, indent=2)
    except Exception:
        pass

if "custom_saved_places" not in st.session_state:
    st.session_state.custom_saved_places = load_user_custom_saved_places()

if "georeferenced_saved_locations" not in st.session_state:
    base_locs = load_and_georeference_saved_locations()
    st.session_state.georeferenced_saved_locations = list(st.session_state.custom_saved_places) + base_locs

# Process query params for destination redirect or place saved from the map
try:
    qp = st.query_params
    if "dest_lat" in qp and "dest_lon" in qp:
        try:
            d_lat = float(qp["dest_lat"])
            d_lon = float(qp["dest_lon"])
            d_name = qp.get("dest_name", "Selected Map Destination")
            st.session_state.coords_dest = (d_lat, d_lon)
            st.session_state.selected_dest_label = d_name
            st.session_state.txt_dest = d_name
            del st.query_params["dest_lat"]
            if "dest_lon" in st.query_params: del st.query_params["dest_lon"]
            if "dest_name" in st.query_params: del st.query_params["dest_name"]
        except Exception:
            pass

    if "save_fav_name" in qp and "save_fav_lat" in qp:
        try:
            f_name = qp.get("save_fav_name", "Saved Favourite Place")
            f_lat = float(qp["save_fav_lat"])
            f_lon = float(qp["save_fav_lng"])
            f_cat = qp.get("save_fav_cat", "FAVOURITE")
            new_fav = {
                "id": f"FAV_{int(time.time())}",
                "name": f_name,
                "section": "Favourites",
                "category": "SAVED_LOCATION",
                "latitude": round(f_lat, 6),
                "longitude": round(f_lon, 6),
                "address": f"{f_name} (Coordinates: {f_lat:.5f}, {f_lon:.5f})",
                "description": "User favourite location",
                "is_custom": True
            }
            if not any(x.get("name") == f_name and abs(x.get("latitude", 0) - f_lat) < 0.0001 for x in st.session_state.custom_saved_places):
                st.session_state.custom_saved_places.insert(0, new_fav)
                save_user_custom_saved_places(st.session_state.custom_saved_places)
                st.session_state.georeferenced_saved_locations.insert(0, new_fav)
            del st.query_params["save_fav_name"]
            if "save_fav_lat" in st.query_params: del st.query_params["save_fav_lat"]
            if "save_fav_lng" in st.query_params: del st.query_params["save_fav_lng"]
            if "save_fav_cat" in st.query_params: del st.query_params["save_fav_cat"]
        except Exception:
            pass
except Exception:
    pass


# Initialize A.U.R.A. Conversational Copilot
if "pathfinder_bot" not in st.session_state:
    st.session_state.pathfinder_bot = PathfinderChatbot(
        pipeline=st.session_state.get("pipeline"),
        map_service=st.session_state.get("real_map_service"),
        road_condition_manager=st.session_state.get("road_condition_manager"),
        emergency_service_manager=st.session_state.get("emergency_service_manager")
    )

if "aura_chat_history" not in st.session_state:
    st.session_state.aura_chat_history = [
        {
            "role": "assistant",
            "badge": "⚡ A.U.R.A. ONLINE",
            "content": (
                "<div style='font-size: 0.84rem; line-height: 1.45; color: #e2e8f0;'>"
                "👋 <b>Greetings! I am A.U.R.A.</b><br>"
                "Your <b>Adaptive User Route Assistant</b> for <b>P.A.T.H.F.I.N.D.E.R.</b> "
                "(<i>Predictive Adaptive Transit & Hazard-Free Intelligent Navigation</i>).<br><br>"
                "I am your dual-purpose conversational companion: ready to answer general knowledge, science, mathematics, coding, writing, and education questions, while providing smart hazard-evading navigation.<br><br>"
                "<i>How may I help you today?</i>"
                "</div>"
            )
        }
    ]

def render_aura_chat_box(key_prefix: str = "main", height: int = 340):
    """Renders the upgraded interactive A.U.R.A. conversational copilot interface."""
    bot = st.session_state.get("pathfinder_bot")
    active_engine_name = "Intelligent Cognitive Engine (Local)"
    if bot and hasattr(bot, "llm_client"):
        p_name = bot.llm_client.active_provider_name
        if p_name != "builtin":
            active_engine_name = f"LLM Active ({p_name.upper()})"

    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.markdown(
            f"<div style='font-size: 0.70rem; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 6px;'>"
            f"<span>⚡ Active Provider:</span>"
            f"<span style='background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.4); padding: 1px 6px; border-radius: 4px; font-family: monospace;'>{active_engine_name}</span>"
            f"</div>",
            unsafe_allow_html=True
        )
    with head_col2:
        if st.button("🗑️ Reset Chat", key=f"btn_reset_chat_{key_prefix}", use_container_width=True, help="Clear active conversation history"):
            if bot and hasattr(bot, "reset_conversation"):
                bot.reset_conversation()
            st.session_state.aura_chat_history = [
                {
                    "role": "assistant",
                    "badge": "⚡ A.U.R.A. RESET",
                    "content": "✨ *Conversation reset. How can I assist you today? Feel free to ask anything!*"
                }
            ]
            st.rerun()

    st.markdown("<span style='font-size: 0.72rem; font-weight: 700; color: #94a3b8;'>💡 Quick Copilot Categories:</span>", unsafe_allow_html=True)
    chip_rows = [
        [
            ("⚡ Fastest Route", "What is the fastest route from my location to the destination?"),
            ("🗺️ Compare Routes", "Can you compare the available route alternatives for distance, time, and safety?"),
            ("🛡️ Check Hazards", "Are there any active road closures, accidents or flood hazards on my corridor?"),
            ("🌤️ Live Weather", "What is the current weather and temperature at my destination?")
        ],
        [
            ("💻 Code Helper", "Explain how the A* pathfinding algorithm works with a Python code example."),
            ("✍️ Creative Story", "Write a short, inspiring creative story about a journey through a misty mountain pass."),
            ("🍽️ Nearby Food", "Recommend the top verified restaurants and dining places near my destination."),
            ("🏥 Emergency / SOS", "Where is the nearest 24/7 hospital or trauma care clinic?")
        ]
    ]

    for row_idx, row_chips in enumerate(chip_rows):
        cols = st.columns(len(row_chips))
        for c_idx, (c_label, c_prompt) in enumerate(row_chips):
            with cols[c_idx]:
                if st.button(c_label, key=f"chip_{key_prefix}_{row_idx}_{c_idx}", use_container_width=True):
                    st.session_state.pending_chat_prompt = c_prompt
                    st.rerun()

    def _execute_chat_turn(query_text: str):
        st.session_state.aura_chat_history.append({"role": "user", "content": query_text})
        chat_ctx = {
            "start_label": st.session_state.get("user_live_label", "Live Location"),
            "dest_label": st.session_state.get("selected_dest_label", "Destination"),
            "dest_coords": st.session_state.get("selected_dest_coords", (16.2335, 80.5505)),
            "current_coords": st.session_state.get("user_live_coords", (16.2335, 80.5505)),
            "active_objective_str": st.session_state.get("active_objective", OptimizationObjective.FASTEST).value,
            "ranked_routes": st.session_state.get("last_ranked_routes", []),
            "active_restrictions": st.session_state.road_condition_manager.get_active_restrictions() if "road_condition_manager" in st.session_state else [],
            "active_hazards": st.session_state.real_hazard_map.get_active_hazards() if "real_hazard_map" in st.session_state else []
        }
        ans = st.session_state.pathfinder_bot.answer(query_text, context=chat_ctx)
        st.session_state.aura_chat_history.append({
            "role": "assistant",
            "content": ans["response"],
            "badge": ans.get("badge", "A.U.R.A. COPILOT")
        })

        # Handle executable actions
        if "action" in ans and isinstance(ans["action"], dict):
            act = ans["action"]
            if act.get("type") == "focus_route":
                r_id = act.get("route_id")
                st.session_state.focused_route_id = r_id
                st.session_state.selected_route_id = r_id
                st.session_state.auto_fit_bounds = True
                st.session_state.scroll_to_app_map = True
                st.session_state.switch_to_nav_tab = True
                st.toast(f"🎯 Highlighting {act.get('route_name', 'Route')} on Interactive Map!", icon="🧭")
            elif act.get("type") == "set_destination":
                st.session_state.selected_dest_coords = act.get("coords")
                st.session_state.selected_dest_label = act.get("destination_name")
                st.session_state.pending_dest = act.get("destination_name")
                st.session_state.scroll_to_app_map = True
                st.session_state.switch_to_nav_tab = True
                st.toast(f"🧭 Destination set to {act.get('destination_name')}!", icon="🎯")
            elif act.get("type") == "calculate_route":
                if act.get("origin_coords"):
                    st.session_state.custom_start_coords = act.get("origin_coords")
                    st.session_state.user_live_coords = act.get("origin_coords")
                    st.session_state.user_live_label = act.get("origin", "Origin")
                    st.session_state.start_mode = "Custom Starting Location"
                if act.get("destination_coords"):
                    st.session_state.selected_dest_coords = act.get("destination_coords")
                    st.session_state.selected_dest_label = act.get("destination", "Destination")
                    st.session_state.pending_dest = act.get("destination", "Destination")
                st.session_state.scroll_to_app_map = True
                st.session_state.switch_to_nav_tab = True
                st.toast(f"🧭 Route calculated: {act.get('origin')} to {act.get('destination')}!", icon="🎯")

    if "pending_chat_prompt" in st.session_state and st.session_state.pending_chat_prompt:
        chip_q = st.session_state.pop("pending_chat_prompt")
        _execute_chat_turn(chip_q)
        st.rerun()

    c_box = st.container(height=height)
    with c_box:
        for msg in st.session_state.aura_chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 8px;">
                    <div style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; padding: 8px 12px; border-radius: 12px 12px 2px 12px; max-width: 85%; font-size: 0.82rem; box-shadow: 0 2px 8px rgba(0,0,0,0.3); font-weight: 500;">
                        {msg['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                b_badge = f"<span style='font-size: 0.62rem; font-weight: 800; color: #38bdf8; font-family: monospace; letter-spacing: 0.05em; background: rgba(56, 189, 248, 0.12); padding: 1px 6px; border-radius: 4px; display: inline-block; margin-bottom: 4px;'>{msg.get('badge', 'A.U.R.A.')}</span>"
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                    <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.22); color: #cbd5e1; padding: 10px 14px; border-radius: 12px 12px 12px 2px; max-width: 95%; font-size: 0.82rem; box-shadow: 0 4px 12px rgba(0,0,0,0.4);">
                        {b_badge}
                        <div>{msg['content']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with st.form(f"aura_form_{key_prefix}", clear_on_submit=True):
        col_in, col_btn = st.columns([4, 1])
        with col_in:
            u_text = st.text_input("Ask A.U.R.A...", placeholder="Ask A.U.R.A. anything (science, coding, math, writing, routes, weather, places)...", label_visibility="collapsed", key=f"txt_{key_prefix}")
        with col_btn:
            s_click = st.form_submit_button("Send 🚀", use_container_width=True)

    if s_click and u_text and u_text.strip():
        q_str = u_text.strip()
        _execute_chat_turn(q_str)
        st.rerun()

# Sidebar: System Status & Multi-Objective Control Panel
with st.sidebar:
    sidebar_logo = os.path.join(APP_DIR, "assets", "pathfinder_logo.jpg")
    if not os.path.exists(sidebar_logo):
        sidebar_logo = os.path.join(APP_DIR, "assets", "campus_aegis_logo.jpg")
    if os.path.exists(sidebar_logo):
        st.image(sidebar_logo, width=140)
    
    st.markdown("<span class='badge-hud-ready'>🧭 ADAPTIVE NAVIGATION</span>", unsafe_allow_html=True)
    st.markdown("### **P.A.T.H.F.I.N.D.E.R.**")
    st.caption("Predictive Adaptive Transit & Hazard-Free Intelligent Navigation Directed Evacuation Routing")

    st.markdown("---")
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 10px; margin-bottom: 8px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.1rem; filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.6));">🎯</span>
            <span style="font-weight: 800; font-size: 0.86rem; letter-spacing: 0.06em; color: #f8fafc; text-transform: uppercase;">
                Routing Objectives
            </span>
        </div>
        <span style="font-size: 0.64rem; font-weight: 700; padding: 2px 7px; border-radius: 6px; background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.35); color: #38bdf8; letter-spacing: 0.05em;">
            AI PREFERENCE
        </span>
    </div>
    """, unsafe_allow_html=True)

    cur_focus_mode = st.session_state.get("focused_route_id", "ALL")
    cur_obj = st.session_state.get("active_objective", OptimizationObjective.FASTEST)

    # 1. Default Option: 🌐 All Routes (Displays all routes connecting origin to destination)
    is_all_active = (cur_focus_mode == "ALL")
    btn_all_label = "✓ 🌐 All Routes (Default)" if is_all_active else "🌐 All Routes (Default)"
    if st.button(btn_all_label, key="btn_obj_all_routes", use_container_width=True, type="primary" if is_all_active else "secondary"):
        st.session_state.focused_route_id = "ALL"
        st.rerun()
    st.markdown(
        f"""<div style="font-size: 0.72rem; color: {'#f8fafc' if is_all_active else '#94a3b8'}; margin-top: -6px; margin-bottom: 8px; padding-left: 4px; line-height: 1.35;">
            Displays all candidate routes simultaneously across the corridor
        </div>""",
        unsafe_allow_html=True
    )

    # Clean, High-Contrast Interactive Objective Buttons (Isolates that route and hides all others)
    obj_definitions = [
        (
            OptimizationObjective.FASTEST,
            "⚡ Fastest Route",
            "Minimizes transit duration & evades traffic",
            "#38bdf8",
            "FASTEST"
        ),
        (
            OptimizationObjective.SHORTEST,
            "📏 Shortest Route",
            "Minimizes ground mileage & physical distance",
            "#c084fc",
            "SHORTEST"
        ),
        (
            OptimizationObjective.BALANCED,
            "⚖️ Balanced Route",
            "Harmonized 50/50 time & distance balance",
            "#34d399",
            "BALANCED"
        ),
        (
            OptimizationObjective.ACCESSIBLE,
            "♿ Accessible Route",
            "Prioritizes step-free paths & certified ramps",
            "#fbbf24",
            "ACCESSIBLE"
        ),
    ]

    for obj_enum, title, desc, accent_col, focus_tag in obj_definitions:
        is_active = (cur_focus_mode == focus_tag)
        btn_label = f"✓ {title}" if is_active else title
        btn_type = "primary" if is_active else "secondary"

        if st.button(btn_label, key=f"btn_obj_{obj_enum.value.lower()}", use_container_width=True, type=btn_type):
            if is_active:
                st.session_state.focused_route_id = "ALL"
            else:
                st.session_state.active_objective = obj_enum
                st.session_state.focused_route_id = focus_tag
            st.rerun()

        desc_color = "#f8fafc" if is_active else "#94a3b8"
        st.markdown(
            f"""<div style="font-size: 0.72rem; color: {desc_color}; margin-top: -6px; margin-bottom: 8px; padding-left: 4px; line-height: 1.35;">
                {desc}
            </div>""",
            unsafe_allow_html=True
        )

    # Clear Navigation Distance Units
    st.markdown("""
    <div style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: #38bdf8; margin-top: 10px; margin-bottom: 6px;">
        📏 Distance Units
    </div>
    """, unsafe_allow_html=True)
    c_u1, c_u2 = st.columns(2)
    cur_unit = st.session_state.get("distance_unit", "km")
    with c_u1:
        if st.button("Kilometers (km)", key="btn_unit_km", use_container_width=True, type="primary" if cur_unit == "km" else "secondary", help="Display all distances in Kilometres (km)"):
            st.session_state.distance_unit = "km"
            st.rerun()
    with c_u2:
        if st.button("Miles (mi)", key="btn_unit_mi", use_container_width=True, type="primary" if cur_unit == "miles" else "secondary", help="Display all distances in Miles (mi)"):
            st.session_state.distance_unit = "miles"
            st.rerun()

    active_unit_label = "Metric (Kilometres)" if cur_unit == "km" else "Imperial (Miles)"
    st.markdown(
        f"""<div style="font-size: 0.68rem; color: #38bdf8; font-weight: 700; margin-top: -4px; margin-bottom: 10px; padding: 2px 6px; background: rgba(56, 189, 248, 0.10); border-radius: 4px; text-align: center; border: 1px solid rgba(56, 189, 248, 0.2);">
            Active Standard: <b>{active_unit_label}</b>
        </div>""",
        unsafe_allow_html=True
    )

    # Dynamic Tactical Telemetry Card with mathematically accurate multi-objective weights
    obj_telemetry = {
        OptimizationObjective.FASTEST: {
            "title": "VELOCITY PRIORITY MATRIX",
            "accent": "#38bdf8",
            "glow": "rgba(56, 189, 248, 0.22)",
            "speed_bar": 85,
            "dist_bar": 15,
            "access_bar": None,
            "profile": "Prioritizing expressways, bypasses, and live congestion-free corridors."
        },
        OptimizationObjective.SHORTEST: {
            "title": "GEODESIC COMPACT PROTOCOL",
            "accent": "#c084fc",
            "glow": "rgba(192, 132, 252, 0.22)",
            "speed_bar": 15,
            "dist_bar": 85,
            "access_bar": None,
            "profile": "Minimizing total road distance and physical mileage footprint."
        },
        OptimizationObjective.BALANCED: {
            "title": "PARETO EQUILIBRIUM PROTOCOL",
            "accent": "#34d399",
            "glow": "rgba(52, 211, 153, 0.22)",
            "speed_bar": 50,
            "dist_bar": 50,
            "access_bar": None,
            "profile": "Equal 50/50 trade-off weighting between duration and physical distance."
        },
        OptimizationObjective.ACCESSIBLE: {
            "title": "BARRIER-FREE MOBILITY PROTOCOL",
            "accent": "#fbbf24",
            "glow": "rgba(251, 191, 36, 0.22)",
            "speed_bar": 50,
            "dist_bar": 50,
            "access_bar": 100,
            "profile": "Strict exclusion of steps, steep inclines (>5°), and unpaved terrain."
        }
    }
    cur_tele = obj_telemetry.get(st.session_state.active_objective, obj_telemetry[OptimizationObjective.FASTEST])

    access_bar_html = ""
    if cur_tele.get("access_bar"):
        access_bar_html = f"""<div style="margin-top: 2px;">
<div style="display: flex; justify-content: space-between; font-size: 0.64rem; font-family: 'JetBrains Mono', monospace; color: #94a3b8; margin-bottom: 2px;">
<span>♿ Barrier Evasion Strictness</span>
<span style="color: #fbbf24; font-weight: 700;">{cur_tele['access_bar']}% Strict</span>
</div>
<div style="width: 100%; height: 4px; background: rgba(255,255,255,0.08); border-radius: 9999px; overflow: hidden;">
<div style="width: {cur_tele['access_bar']}%; height: 100%; background: linear-gradient(90deg, #fbbf24, #10b981); border-radius: 9999px;"></div>
</div>
</div>"""

    strategy_card_html = f"""<div style="background: rgba(10, 20, 38, 0.72); border: 1px solid {cur_tele['accent']}40; border-radius: 12px; padding: 10px 12px; margin-top: 8px; margin-bottom: 12px; box-shadow: 0 4px 16px {cur_tele['glow']}; backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
<span style="font-size: 0.66rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: {cur_tele['accent']}; letter-spacing: 0.05em;">● ACTIVE STRATEGY</span>
<span style="font-size: 0.63rem; color: #94a3b8; font-weight: 600;">AI ROUTE BIAS</span>
</div>
<div style="font-size: 0.74rem; font-weight: 700; color: #f8fafc; margin-bottom: 5px;">{cur_tele['title']}</div>
<div style="font-size: 0.70rem; color: #cbd5e1; line-height: 1.35; margin-bottom: 8px;">{cur_tele['profile']}</div>
<div style="display: flex; flex-direction: column; gap: 5px;">
<div>
<div style="display: flex; justify-content: space-between; font-size: 0.64rem; font-family: 'JetBrains Mono', monospace; color: #94a3b8; margin-bottom: 2px;">
<span>⚡ Speed Optimization Weight</span>
<span style="color: {cur_tele['accent']}; font-weight: 700;">{cur_tele['speed_bar']}%</span>
</div>
<div style="width: 100%; height: 4px; background: rgba(255,255,255,0.08); border-radius: 9999px; overflow: hidden;">
<div style="width: {cur_tele['speed_bar']}%; height: 100%; background: linear-gradient(90deg, #38bdf8, {cur_tele['accent']}); border-radius: 9999px;"></div>
</div>
</div>
<div>
<div style="display: flex; justify-content: space-between; font-size: 0.64rem; font-family: 'JetBrains Mono', monospace; color: #94a3b8; margin-bottom: 2px;">
<span>📏 Distance Compression Weight</span>
<span style="color: {cur_tele['accent']}; font-weight: 700;">{cur_tele['dist_bar']}%</span>
</div>
<div style="width: 100%; height: 4px; background: rgba(255,255,255,0.08); border-radius: 9999px; overflow: hidden;">
<div style="width: {cur_tele['dist_bar']}%; height: 100%; background: linear-gradient(90deg, #a855f7, {cur_tele['accent']}); border-radius: 9999px;"></div>
</div>
</div>{access_bar_html}</div>
</div>"""
    st.markdown(strategy_card_html, unsafe_allow_html=True)

    if "selected_sidebar_category" not in st.session_state:
        st.session_state.selected_sidebar_category = "🌐 All Facilities"
    st.session_state.show_category_facilities_on_map = True






# Run or restore current incident state
curr_start = st.session_state.get("active_start_node", "VIG_ENGI_CHEMICAL_REACTION_ENGG_")
curr_goal = "VIG_FACI_PLAY_GROUNDS"

if "last_incident_res" not in st.session_state:
    st.session_state.last_incident_res = pipeline.process_incident(
        raw_alert_text="Nominal campus operations. Routine monitoring active across academic blocks.",
        start_node=curr_start,
        goal_node=curr_goal,
        requires_accessible=st.session_state.get("requires_accessible", False) or (st.session_state.get("active_objective") == OptimizationObjective.ACCESSIBLE),
        auto_inject_hazard=False
    )

res = st.session_state.last_incident_res
system_status = res["status"]
guidance = res["guidance"]

# Unified Top Header: Glassmorphic Mission Control HUD
env_badge = st.session_state.road_condition_manager.get_mode_indicator()
active_restr_count = len(st.session_state.road_condition_manager.get_active_restrictions())
active_traffic_count = len(st.session_state.road_condition_manager.get_active_traffic_conditions())
active_haz_count = len(st.session_state.real_hazard_map.get_active_hazards())
active_obj_val = getattr(st.session_state.get("active_objective", OptimizationObjective.FASTEST), "value", "FASTEST")

haz_color = "#ef4444" if active_haz_count > 0 else "#34d399"
restr_color = "#f59e0b" if active_restr_count > 0 else "#34d399"
traffic_text = f"{active_traffic_count} Delays" if active_traffic_count > 0 else "Normal Flow"

st.markdown(f"""<div style='background: linear-gradient(135deg, rgba(15, 23, 42, 0.94) 0%, rgba(30, 41, 59, 0.85) 100%); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1.5px solid rgba(56, 189, 248, 0.28); border-left: 5px solid {env_badge["color"]}; border-radius: 14px; padding: 14px 20px; margin: 4px 0 14px 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45);'><div style='display: flex; align-items: center; gap: 14px;'><div style='width: 48px; height: 48px; border-radius: 12px; background: linear-gradient(135deg, rgba(56, 189, 248, 0.22) 0%, rgba(16, 185, 129, 0.18) 100%); border: 1.5px solid rgba(56, 189, 248, 0.45); display: flex; align-items: center; justify-content: center; font-size: 1.6rem; box-shadow: 0 0 18px rgba(56, 189, 248, 0.3);'>🧭</div><div><div style='display: flex; align-items: center; gap: 12px; flex-wrap: wrap;'><span style='font-size: 1.65rem; font-weight: 900; letter-spacing: 0.04em; background: linear-gradient(135deg, #38bdf8 0%, #34d399 55%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>P.A.T.H.F.I.N.D.E.R.</span><span style='background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.45); color: #34d399; font-size: 0.72rem; font-weight: 800; padding: 3px 10px; border-radius: 9999px; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);'><span style='width: 7px; height: 7px; border-radius: 50%; background: #34d399; box-shadow: 0 0 8px #34d399;'></span>{env_badge["label"].upper()}</span></div><div style='font-size: 0.78rem; color: #94a3b8; margin-top: 3px;'>Predictive Adaptive Transit & Hazard-Free Intelligent Navigation • Autonomous Multi-Corridor Safety Telemetry</div></div></div><div style='display: flex; align-items: center; gap: 10px; flex-wrap: wrap; background: rgba(0, 0, 0, 0.35); padding: 7px 14px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.08); box-shadow: inset 0 2px 6px rgba(0,0,0,0.4);'><span style='font-size: 0.74rem; color: #cbd5e1; display: inline-flex; align-items: center; gap: 5px;'><span>🛡️</span> Hazards: <b style='color: {haz_color};'>{active_haz_count}</b></span><span style='color: rgba(255,255,255,0.18);'>|</span><span style='font-size: 0.74rem; color: #cbd5e1; display: inline-flex; align-items: center; gap: 5px;'><span>🚧</span> Closures: <b style='color: {restr_color};'>{active_restr_count}</b></span><span style='color: rgba(255,255,255,0.18);'>|</span><span style='font-size: 0.74rem; color: #cbd5e1; display: inline-flex; align-items: center; gap: 5px;'><span>🚦</span> Traffic: <b style='color: #38bdf8;'>{traffic_text}</b></span><span style='color: rgba(255,255,255,0.18);'>|</span><span style='font-size: 0.74rem; color: #cbd5e1; display: inline-flex; align-items: center; gap: 5px;'><span>⚡</span> Priority: <b style='color: #34d399;'>{active_obj_val}</b></span></div></div>""", unsafe_allow_html=True)

# Automatic Browser Satellite Geolocation Autopilot Script
is_custom_active = st.session_state.get("is_custom_start_place", False)
components.html(f"""
<script>
(function() {{
    var isCustom = {json.dumps(bool(is_custom_active))};
    if (isCustom) return;

    var pWin = window.parent || window;
    var pDoc = (pWin && pWin.document) ? pWin.document : document;

    // 1. Ensure all parent iframes have geolocation permission granted
    try {{
        var iframes = pDoc.querySelectorAll('iframe');
        iframes.forEach(function(f) {{
            var a = f.getAttribute('allow') || '';
            if (a.indexOf('geolocation') === -1) {{
                f.setAttribute('allow', (a + ' geolocation *; microphone *; camera *;').trim());
            }}
        }});
    }} catch(e) {{}}

    // 2. Select top-level geolocation API (bypasses iframe permissions policy limitations)
    var geo = (pWin.navigator && pWin.navigator.geolocation) ? pWin.navigator.geolocation : navigator.geolocation;
    if (!geo) {{
        console.warn("[PATHFINDER] Geolocation not supported on this client device.");
        return;
    }}

    function distM(lat1, lon1, lat2, lon2) {{
        var R = 6371000;
        var dLat = (lat2 - lat1) * Math.PI / 180;
        var dLon = (lon2 - lon1) * Math.PI / 180;
        var a = Math.sin(dLat/2)*Math.sin(dLat/2) +
                Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180) *
                Math.sin(dLon/2)*Math.sin(dLon/2);
        return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    }}

    function onGpsPosition(pos) {{
        if (!pos || !pos.coords) return;
        var lat = pos.coords.latitude;
        var lon = pos.coords.longitude;
        var acc = pos.coords.accuracy || 6.0;
        var spd = (pos.coords.speed !== null && !isNaN(pos.coords.speed) && pos.coords.speed > 0) ? (pos.coords.speed * 3.6) : 0.0;
        var hdg = (pos.coords.heading !== null && !isNaN(pos.coords.heading)) ? pos.coords.heading : 0.0;

        try {{
            var targetWin = window.parent || window;
            var url;
            try {{
                url = new URL(targetWin.location.href);
            }} catch(e) {{
                try {{
                    url = new URL(window.top.location.href);
                    targetWin = window.top;
                }} catch(e2) {{
                    url = new URL(window.location.href);
                    targetWin = window;
                }}
            }}
            var curLat = url.searchParams.get("gps_lat");
            var curLon = url.searchParams.get("gps_lon");
            var hasGps = (curLat !== null && curLon !== null);

            var distMoved = 999.0;
            if (hasGps) {{
                distMoved = distM(parseFloat(curLat), parseFloat(curLon), lat, lon);
            }}

            var now = Date.now();
            var lastSync = window._lastPathfinderGpsSync || 0;

            // Save in user device session storage for instant reload persistence
            try {{
                targetWin.sessionStorage.setItem('_pathfinder_user_gps', JSON.stringify({{
                    lat: lat, lon: lon, acc: acc, time: now
                }}));
            }} catch(e) {{}}

            // Lock satellite GPS on startup immediately, and update when moved > 8 meters
            if (!hasGps || (distMoved > 8.0 && (now - lastSync) > 4000)) {{
                window._lastPathfinderGpsSync = now;
                url.searchParams.set("gps_lat", lat.toFixed(6));
                url.searchParams.set("gps_lon", lon.toFixed(6));
                url.searchParams.set("gps_acc", acc.toFixed(1));
                url.searchParams.set("gps_spd", spd.toFixed(1));
                url.searchParams.set("gps_hdg", hdg.toFixed(1));
                try {{
                    targetWin.location.replace(url.toString());
                }} catch(e) {{
                    window.location.replace(url.toString());
                }}
            }}
        }} catch(e) {{
            console.warn("[PATHFINDER] Parent GPS sync error:", e);
        }}
    }}

    // Check device session storage for instant cached GPS on client
    try {{
        var cached = pWin.sessionStorage.getItem('_pathfinder_user_gps');
        if (cached) {{
            var pGps = JSON.parse(cached);
            if (pGps && pGps.lat && pGps.lon && (Date.now() - (pGps.time || 0) < 600000)) {{
                onGpsPosition({{
                    coords: {{
                        latitude: pGps.lat,
                        longitude: pGps.lon,
                        accuracy: pGps.acc || 6.0,
                        speed: 0.0,
                        heading: 0.0
                    }}
                }});
            }}
        }}
    }} catch(e) {{}}

    if (!window._pathfinderGpsWatchId) {{
        // Fast instant fix (Wi-Fi / Cell tower triangulation)
        geo.getCurrentPosition(onGpsPosition, function(err) {{
            console.warn("[PATHFINDER] Fast GPS fix notice:", err.message);
            // High-precision satellite fallback
            geo.getCurrentPosition(onGpsPosition, function(err2) {{
                console.warn("[PATHFINDER] Satellite GPS fallback notice:", err2.message);
            }}, {{ enableHighAccuracy: true, timeout: 10000, maximumAge: 10000 }});
        }}, {{ enableHighAccuracy: false, timeout: 5000, maximumAge: 300000 }});

        // Continuous high-precision satellite tracker for real-time movement detection
        window._pathfinderGpsWatchId = geo.watchPosition(onGpsPosition, function(err) {{
            console.warn("[PATHFINDER] Satellite GPS live watch notice:", err.message);
        }}, {{ enableHighAccuracy: true, timeout: 15000, maximumAge: 1000 }});

        // Listen for satellite map blue circle locationfound event or inner map postMessage
        var msgHandler = function(e) {{
            if (e.data && e.data.type === 'PATHFINDER_GPS_DETECTED' && e.data.lat && e.data.lon) {{
                onGpsPosition({{
                    coords: {{
                        latitude: e.data.lat,
                        longitude: e.data.lon,
                        accuracy: e.data.acc || 6.0,
                        speed: 0.0,
                        heading: 0.0
                    }}
                }});
            }}
        }};
        window.addEventListener('message', msgHandler);
        try {{
            if (pWin && pWin !== window) {{
                pWin.addEventListener('message', msgHandler);
            }}
        }} catch(e) {{}}
    }}
}})();
</script>
""", height=0, width=0)

# Check if real hardware device GPS was passed via URL query params
if "gps_lat" in st.query_params and "gps_lon" in st.query_params:
    try:
        q_lat = float(st.query_params["gps_lat"])
        q_lon = float(st.query_params["gps_lon"])
        q_acc = float(st.query_params.get("gps_acc", 6.0))
        q_spd = float(st.query_params.get("gps_spd", 0.0))
        q_hdg = float(st.query_params.get("gps_hdg", 0.0))

        st.session_state.hardware_gps_coords = (q_lat, q_lon)
        st.session_state.user_gps_accuracy = q_acc
        st.session_state.user_speed_kmh = q_spd
        st.session_state.user_bearing_deg = q_hdg
        st.session_state.is_in_transit = (q_spd > 1.2)

        # Compute cardinal heading
        cardinals = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        card_idx = int((q_hdg + 11.25) / 22.5) % 16
        st.session_state.user_heading_cardinal = cardinals[card_idx]

        # Keep current location locked to real GPS UNLESS user explicitly set custom start place
        if not st.session_state.get("is_custom_start_place", False):
            st.session_state.user_live_coords = (q_lat, q_lon)
            if st.session_state.get("last_gps_param") != (q_lat, q_lon):
                st.session_state.last_gps_param = (q_lat, q_lon)
                try:
                    resolved_addr = st.session_state.real_map_service.reverse_geocode(q_lat, q_lon)
                    clean_lbl = resolved_addr.split(",")[0].strip() if resolved_addr else f"{q_lat:.4f}, {q_lon:.4f}"
                    st.session_state.user_live_label = f"📍 Current Location ({clean_lbl})"
                except Exception:
                    st.session_state.user_live_label = f"📍 Current Location ({q_lat:.4f}, {q_lon:.4f})"
                st.session_state.txt_orig = st.session_state.user_live_label
                st.session_state.last_synced_orig = st.session_state.user_live_label

            st.session_state.real_location_service.set_permission(LocationPermissionStatus.GRANTED)
            st.session_state.real_location_service.record_movement(
                q_lat, q_lon,
                accuracy_m=q_acc,
                speed_mps=(q_spd / 3.6),
                label="Satellite GPS"
            )
    except Exception:
        pass

# Check query parameters for tab navigation & in-app destination redirects
if "tab" in st.query_params:
    st.session_state.target_tab = str(st.query_params.get("tab", "nav")).lower()
    try:
        del st.query_params["tab"]
    except Exception:
        pass

if "dest_lat" in st.query_params and "dest_lon" in st.query_params:
    try:
        q_dest_lat = float(st.query_params["dest_lat"])
        q_dest_lon = float(st.query_params["dest_lon"])
        q_dest_name = st.query_params.get("dest_name", f"Destination ({q_dest_lat:.4f}, {q_dest_lon:.4f})")
        st.session_state.selected_dest_coords = (q_dest_lat, q_dest_lon)
        st.session_state.selected_dest_label = q_dest_name
        st.session_state.pending_dest = q_dest_name
        st.session_state.txt_dest = q_dest_name
        st.session_state.last_synced_dest = q_dest_name
        st.session_state.movement_index = 0
        st.session_state.is_in_transit = False
        st.session_state.scroll_to_app_map = True
        st.session_state.target_tab = "nav"
        try:
            del st.query_params["dest_lat"]
            del st.query_params["dest_lon"]
            if "dest_name" in st.query_params:
                del st.query_params["dest_name"]
            if "redirect_map" in st.query_params:
                del st.query_params["redirect_map"]
        except Exception:
            pass
    except Exception:
        pass

# =========================================================================
# =========================================================================
# PRIMARY APPLICATION TABS: NAVIGATION & EMERGENCY OPERATIONS CENTER (E.O.C.)
# =========================================================================
# =========================================================================


# Initialize Live Position Tracking & Movement Kinematics
if "auto_detected_user_location" not in st.session_state:
    st.session_state.auto_detected_user_location = detect_user_network_location()

TENALI_DEFAULT_COORDS = (16.23454, 80.65197)
TENALI_DEFAULT_LABEL = "📍 Current Location"

detected_loc = st.session_state.get("auto_detected_user_location")
detected_coords = (detected_loc["lat"], detected_loc["lon"]) if detected_loc else TENALI_DEFAULT_COORDS
detected_label = detected_loc["label"] if detected_loc else TENALI_DEFAULT_LABEL

# Multi-user dynamic location synchronization:
# 1. Hardware GPS from browser navigator.geolocation (highest priority)
# 2. Baseline detected location
# 3. Default fallback
cur_live = st.session_state.get("user_live_coords")
is_custom_start = st.session_state.get("is_custom_start_place", False)

if "user_live_coords" not in st.session_state or not cur_live:
    initial_base = st.session_state.get("hardware_gps_coords") or detected_coords
    initial_lbl = st.session_state.get("user_live_label") or detected_label
    st.session_state.user_live_coords = initial_base
    st.session_state.user_live_label = initial_lbl
    st.session_state.txt_orig = "📍 Current Location"
    st.session_state.last_synced_orig = "📍 Current Location"
    if "real_location_service" in st.session_state:
        st.session_state.real_location_service.set_manual_location(initial_base[0], initial_base[1], initial_lbl)

if "user_speed_kmh" not in st.session_state:
    st.session_state.user_speed_kmh = 0.0
if "user_bearing_deg" not in st.session_state:
    st.session_state.user_bearing_deg = 0.0
if "user_heading_cardinal" not in st.session_state:
    st.session_state.user_heading_cardinal = "N"
if "user_gps_accuracy" not in st.session_state:
    st.session_state.user_gps_accuracy = 6.0
if "movement_index" not in st.session_state:
    st.session_state.movement_index = 0
if "is_in_transit" not in st.session_state:
    st.session_state.is_in_transit = False
if "map_click_mode" not in st.session_state:
    st.session_state.map_click_mode = "Set Destination"

if "selected_dest_coords" not in st.session_state:
    st.session_state.selected_dest_coords = None
    st.session_state.selected_dest_label = ""

# =========================================================================
# CREATIVE JOURNEY ROUTE PLANNER CONSOLE
# =========================================================================

# Ensure origin and destination text state keys are set
# Process pending origin or destination updates before text widgets instantiate
if "pending_orig" in st.session_state:
    st.session_state.txt_orig = st.session_state.pop("pending_orig")
    st.session_state.last_synced_orig = st.session_state.txt_orig
if "pending_dest" in st.session_state:
    st.session_state.txt_dest = st.session_state.pop("pending_dest")
    st.session_state.last_synced_dest = st.session_state.txt_dest

if "txt_orig" not in st.session_state:
    st.session_state.txt_orig = ""
if "txt_dest" not in st.session_state:
    st.session_state.txt_dest = ""
if "last_synced_orig" not in st.session_state:
    st.session_state.last_synced_orig = ""
if "last_synced_dest" not in st.session_state:
    st.session_state.last_synced_dest = ""

# Custom styling for route planner console
st.markdown("""
<style>
.route-ribbon-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.92) 0%, rgba(30, 41, 59, 0.78) 100%);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(56, 189, 248, 0.30);
    border-radius: 10px;
    padding: 10px 16px;
    margin-top: 10px;
    margin-bottom: 6px;
    box-shadow: 0 6px 20px -2px rgba(0, 0, 0, 0.45), 0 0 15px rgba(56, 189, 248, 0.10);
}
.route-tag-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.74rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)



# Symmetrical Journey Input Controls with Custom Start & Reset

# Automatic Tab-Switch & Map Scroll Router:
# If user clicked any place card or "Route Here" button in Places or Facilities,
# automatically switch active tab to '🧭 Navigation' and scroll directly to the Pathfinder Map!
# =========================================================================
# 4-TAB MODULAR SYSTEM: NAVIGATION • VIRTUAL GUIDE • FACILITIES • PLACES
# =========================================================================

# Universal Tab-Switch & Dynamic Map Router:
# Programmatically switches to any target tab ('nav', 'guide', 'facilities', 'places')
# and scrolls to the map viewport whenever requested.
requested_tab = st.session_state.pop("target_tab", None)
if not requested_tab and (st.session_state.pop("switch_to_nav_tab", False) or st.session_state.get("scroll_to_app_map", False)):
    requested_tab = "nav"

should_scroll_map = st.session_state.pop("scroll_to_app_map", False)

# Universal Tab Switcher & Dynamic Map Router Component
components.html(f"""
<script>
(function() {{
    var reqTab = {json.dumps(requested_tab)};
    var doScroll = {json.dumps(bool(should_scroll_map))};

    // Inject ultra-premium glassmorphic styling directly into window.parent document head
    try {{
        var pDoc = window.parent.document || document;
        var styleEl = pDoc.getElementById('pathfinder-tabs-ultrastyle');
        if (!styleEl) {{
            styleEl = pDoc.createElement('style');
            styleEl.id = 'pathfinder-tabs-ultrastyle';
            pDoc.head.appendChild(styleEl);
        }}
        styleEl.textContent = `
            div[data-testid="stTabs"] > div:first-child,
            div[data-testid="stTabs"] [data-baseweb="tab-list"],
            div[role="tablist"] {{
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.94) 0%, rgba(30, 41, 59, 0.85) 100%) !important;
                backdrop-filter: blur(20px) !important;
                -webkit-backdrop-filter: blur(20px) !important;
                border: 1.5px solid rgba(56, 189, 248, 0.32) !important;
                border-radius: 16px !important;
                padding: 6px 8px !important;
                gap: 8px !important;
                margin-bottom: 16px !important;
                box-shadow: 0 10px 32px -4px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
                display: inline-flex !important;
                align-items: center !important;
            }}
            div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
            div[data-testid="stTabs"] [data-baseweb="tab-border"],
            [data-baseweb="tab-highlight"],
            [data-baseweb="tab-border"],
            div[role="tablist"] > div[style*="transform"],
            div[role="tablist"] > div[style*="position: absolute"],
            div[role="tablist"] > div[style*="bottom: 0"],
            div[role="tablist"] > div[style*="bottom:0"],
            div[role="tablist"] > div:last-child:not([role="tab"]) {{
                display: none !important;
                opacity: 0 !important;
                height: 0 !important;
                width: 0 !important;
                border: none !important;
                visibility: hidden !important;
                pointer-events: none !important;
            }}
            div[data-testid="stTabs"] [role="tab"],
            div[data-testid="stTabs"] div[role="tab"],
            div[data-testid="stTabs"] button[role="tab"],
            div[role="tablist"] [role="tab"],
            [data-baseweb="tab"],
            [role="tab"] {{
                height: auto !important;
                min-height: 42px !important;
                padding: 9px 22px !important;
                border-radius: 12px !important;
                background: rgba(255, 255, 255, 0.04) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
                color: #94a3b8 !important;
                font-size: 0.95rem !important;
                font-weight: 700 !important;
                letter-spacing: 0.02em !important;
                transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
                cursor: pointer !important;
                outline: none !important;
                box-shadow: none !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 8px !important;
                white-space: nowrap !important;
            }}
            div[data-testid="stTabs"] [role="tab"]:hover,
            div[role="tablist"] [role="tab"]:hover,
            [role="tab"]:hover {{
                color: #ffffff !important;
                background: rgba(56, 189, 248, 0.16) !important;
                border: 1px solid rgba(56, 189, 248, 0.50) !important;
                border-bottom: 1px solid rgba(56, 189, 248, 0.50) !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 18px rgba(56, 189, 248, 0.25) !important;
            }}
            div[data-testid="stTabs"] [role="tab"][aria-selected="true"],
            div[data-testid="stTabs"] div[role="tab"][aria-selected="true"],
            div[role="tablist"] [role="tab"][aria-selected="true"],
            [role="tab"][aria-selected="true"] {{
                background: linear-gradient(135deg, rgba(2, 132, 199, 0.60) 0%, rgba(14, 165, 233, 0.40) 100%) !important;
                border: 1.5px solid #38bdf8 !important;
                border-bottom: 1.5px solid #38bdf8 !important;
                color: #ffffff !important;
                box-shadow: 0 0 24px rgba(56, 189, 248, 0.50), inset 0 1px 0 rgba(255, 255, 255, 0.35) !important;
                font-weight: 800 !important;
            }}
            div[data-testid="stTabs"] [role="tab"] p,
            div[data-testid="stTabs"] [role="tab"] span,
            [role="tab"] p,
            [role="tab"] span {{
                color: inherit !important;
                font-size: 0.95rem !important;
                font-weight: 700 !important;
                margin: 0 !important;
            }}
        `;
    }} catch(e) {{
        console.warn("Direct parent head style injection:", e);
    }}

    // Global helper exposed to window and window.parent
    window.parent.switchPathfinderTab = window.switchPathfinderTab = function(target, scrollMap) {{
        try {{
            var doc = window.parent.document || document;
            var tabs = doc.querySelectorAll('div[data-testid="stTabs"] button[role="tab"], button[data-baseweb="tab"], button[role="tab"]');
            if (!tabs || tabs.length === 0) return;

            var targetBtn = null;
            if (typeof target === 'number') {{
                targetBtn = tabs[target];
            }} else if (typeof target === 'string') {{
                var tLow = target.toLowerCase().trim();
                targetBtn = Array.from(tabs).find(function(b) {{
                    var txt = (b.innerText || b.textContent || '').toLowerCase();
                    if ((tLow.indexOf('nav') !== -1 || tLow.indexOf('map') !== -1) && (txt.indexOf('nav') !== -1 || txt.indexOf('🧭') !== -1)) return true;
                    if ((tLow.indexOf('guide') !== -1 || tLow.indexOf('virtual') !== -1) && (txt.indexOf('guide') !== -1 || txt.indexOf('🚗') !== -1)) return true;
                    if ((tLow.indexOf('facil') !== -1 || tLow.indexOf('hospital') !== -1 || tLow.indexOf('safety') !== -1) && (txt.indexOf('facil') !== -1 || txt.indexOf('🏥') !== -1)) return true;
                    if ((tLow.indexOf('place') !== -1 || tLow.indexOf('visit') !== -1 || tLow.indexOf('sight') !== -1) && (txt.indexOf('place') !== -1 || txt.indexOf('🌟') !== -1)) return true;
                    return txt.indexOf(tLow) !== -1;
                }});
            }}

            if (targetBtn) {{
                targetBtn.focus();
                targetBtn.click();
                try {{
                    targetBtn.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true, view: window.parent || window }}));
                }} catch(e) {{}}
            }}

            if (scrollMap || (target && String(target).toLowerCase().indexOf('nav') !== -1 && scrollMap !== false)) {{
                setTimeout(function() {{
                    var mapViewport = doc.getElementById('application-map-viewport') || 
                                     doc.getElementById('map') ||
                                     doc.querySelector('.gmap-container') ||
                                     doc.querySelector('iframe[title="streamlit_folium.st_folium"]') ||
                                     doc.querySelector('[data-testid="stIFrame"]');
                    if (mapViewport) {{
                        mapViewport.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    }}
                }}, 280);

                setTimeout(function() {{
                    var iframes = doc.querySelectorAll('iframe');
                    iframes.forEach(function(ifr) {{
                        try {{
                            if (ifr.contentWindow && ifr.contentWindow.gMap && ifr.contentWindow.google) {{
                                ifr.contentWindow.google.maps.event.trigger(ifr.contentWindow.gMap, 'resize');
                            }}
                            if (ifr.contentWindow && ifr.contentWindow.lMapInstance) {{
                                ifr.contentWindow.lMapInstance.invalidateSize();
                            }}
                        }} catch(e) {{}}
                    }});
                }}, 500);
            }}
        }} catch(err) {{
            console.warn("switchPathfinderTab error:", err);
        }}
    }};

    if (reqTab) {{
        function triggerRedirect() {{
            window.switchPathfinderTab(reqTab, doScroll);
        }}
        triggerRedirect();
        setTimeout(triggerRedirect, 200);
        setTimeout(triggerRedirect, 500);
        setTimeout(triggerRedirect, 1000);
    }}
}})();
</script>
""", height=0, width=0)

tab_nav, tab_guide, tab_facilities, tab_places = st.tabs([
    "🧭 Navigation",
    "🚗 Virtual Guide",
    "🏥 Facilities",
    "🌟 Places"
])

with tab_nav:
    # Creative cyberpunk location input styles
    st.markdown("""
    <style>
    /* Input container glow on focus */
    div[data-testid="stTextInput"] input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56,189,248,0.25), 0 0 18px rgba(56,189,248,0.35) !important;
    }
    /* Creative GPS pulse on origin label */
    .origin-gps-dot {
        display: inline-block;
        width: 10px; height: 10px;
        background: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(16,185,129,0.5);
        animation: gpsPulse 2s infinite;
    }
    @keyframes gpsPulse {
        0% { box-shadow: 0 0 0 0 rgba(16,185,129,0.55); }
        70% { box-shadow: 0 0 0 10px rgba(16,185,129,0); }
        100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
    }
    /* Creative swap button */
    div[data-testid="stButton"][data-key="btn_swap_locations"] > button {
        background: linear-gradient(135deg, rgba(56,189,248,0.2) 0%, rgba(14,165,233,0.35) 100%) !important;
        border: 1.5px solid #38bdf8 !important;
        border-radius: 50% !important;
        width: 48px !important;
        height: 48px !important;
        min-width: 48px !important;
        padding: 0 !important;
        font-size: 1.4rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 0 14px rgba(56,189,248,0.45) !important;
        transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
        margin: auto !important;
    }
    div[data-testid="stButton"][data-key="btn_swap_locations"] > button:hover {
        transform: rotate(180deg) scale(1.15) !important;
        box-shadow: 0 0 24px rgba(56,189,248,0.75) !important;
        background: linear-gradient(135deg, rgba(56,189,248,0.45) 0%, rgba(14,165,233,0.55) 100%) !important;
    }
    /* Keyboard shortcut hint badges on tabs */
    .tab-shortcut-badge {
        font-size: 0.55rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        background: rgba(56,189,248,0.18);
        border: 1px solid rgba(56,189,248,0.40);
        border-radius: 4px;
        padding: 1px 4px;
        color: #7dd3fc;
        letter-spacing: 0.04em;
        vertical-align: middle;
        margin-left: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Add Alt+1..4 keyboard shortcut listener
    import streamlit.components.v1 as _comp_tabs
    _comp_tabs.html("""
    <script>
    (function() {
        document.addEventListener('keydown', function(e) {
            if (!e.altKey) return;
            var idx = [49,50,51,52].indexOf(e.keyCode); // Alt+1,2,3,4
            if (idx === -1) return;
            e.preventDefault();
            try {
                var tabs = (window.parent.document||document).querySelectorAll('button[role="tab"]');
                if (tabs[idx]) { tabs[idx].click(); }
            } catch(err) {}
        });
    })();
    </script>
    """, height=0, width=0)

    col_orig_in, col_swap_btn, col_dest_in = st.columns([4.6, 0.8, 4.6], vertical_alignment="center")

    with col_orig_in:
        orig_text = st.text_input(
            "🟢 Start Location",
            key="txt_orig",
            placeholder="🛰️ Type city, village, address or landmark — or leave empty for GPS...",
            help="Leave blank to use your live GPS location. Type any custom city, village, address, landmark, or coordinates to route from there instead."
        )
        if orig_text and orig_text != st.session_state.last_synced_orig:
            st.session_state.last_synced_orig = orig_text
            clean_low = orig_text.lower().strip()
            if any(w in clean_low for w in ["current", "satellite", "live", "gps", "📍", "🛰️", "my location"]):
                st.session_state.is_custom_start_place = False
                st.session_state.orig_candidates = []
                st.session_state.orig_candidates_query = ""
                CURRENT_BASE = st.session_state.get("hardware_gps_coords") or detected_coords
                st.session_state.user_live_coords = CURRENT_BASE
                st.session_state.user_live_label = detected_label
                st.session_state.selected_orig_id = "gps_current_hardware"
                st.session_state.movement_index = 0
                st.session_state.is_in_transit = False
                st.session_state.real_location_service.set_manual_location(CURRENT_BASE[0], CURRENT_BASE[1], "Satellite Location")
                st.toast("Start location → Live Satellite GPS", icon="🛰️")
                st.rerun()
            else:
                st.session_state.is_custom_start_place = True
                cands = st.session_state.real_map_service.geocode_candidates(orig_text, limit=5)
                if cands:
                    st.session_state.geocoding_orig_error = None
                    if len(cands) == 1:
                        # Unique, high-confidence result: convenient direct routing
                        best = cands[0]
                        st.session_state.user_live_coords = (best["lat"], best["lon"])
                        st.session_state.user_live_label = best.get("display_name", orig_text)
                        st.session_state.selected_orig_id = best.get("provider_id", f"orig_{best['lat']:.4f}_{best['lon']:.4f}")
                        st.session_state.active_orig_meta = best
                        st.session_state.orig_candidates = []
                        st.session_state.orig_candidates_query = ""
                        st.session_state.movement_index = 0
                        st.session_state.is_in_transit = False
                        st.session_state.user_speed_kmh = 0.0
                        st.session_state.user_bearing_deg = 0.0
                        st.session_state.real_location_service.set_manual_location(best["lat"], best["lon"], orig_text)
                        st.session_state._prev_route_sig = None
                        st.session_state.focused_route_id = "ALL"
                        st.session_state.selected_route_id = None
                        st.session_state.auto_fit_bounds = True
                        st.toast(f"📍 Start → {best.get('city') or orig_text}", icon="📍")
                        st.rerun()
                    else:
                        # Multiple plausible results: require explicit disambiguation before routing
                        st.session_state.orig_candidates = cands
                        st.session_state.orig_candidates_query = orig_text
                        st.session_state.user_live_coords = None
                        st.session_state.user_live_label = None
                        st.session_state.selected_orig_id = None
                        st.session_state.active_orig_meta = None
                        st.session_state._prev_route_sig = None
                        st.session_state.focused_route_id = "ALL"
                        st.session_state.selected_route_id = None
                        st.toast(f"🔍 Found {len(cands)} matching locations for '{orig_text}'. Please select one below.", icon="🔍")
                        st.rerun()
                else:
                    st.session_state.user_live_coords = None
                    st.session_state.user_live_label = None
                    st.session_state.selected_orig_id = None
                    st.session_state.active_orig_meta = None
                    st.session_state.orig_candidates = []
                    st.session_state.orig_candidates_query = ""
                    st.session_state._prev_route_sig = None
                    st.session_state.focused_route_id = "ALL"
                    st.session_state.selected_route_id = None
                    st.session_state.selected_route_object = None
                    st.session_state.geocoding_orig_error = f"Could not find coordinates for '{orig_text}'. Please check the place name or enter coordinates (e.g. 16.234, 80.550)."
                    st.toast(f"⚠️ Could not resolve '{orig_text}'.", icon="⚠️")
                    st.rerun()

        elif not orig_text and st.session_state.get("is_custom_start_place", False):
            st.session_state.is_custom_start_place = False
            st.session_state.orig_candidates = []
            st.session_state.orig_candidates_query = ""
            st.session_state.geocoding_orig_error = None
            st.session_state._prev_route_sig = None
            st.session_state.focused_route_id = "ALL"
            st.session_state.selected_route_id = None
            st.session_state.auto_fit_bounds = True
            CURRENT_BASE = st.session_state.get("hardware_gps_coords") or detected_coords
            st.session_state.user_live_coords = CURRENT_BASE
            st.session_state.user_live_label = detected_label
            st.session_state.selected_orig_id = "gps_current_hardware"
            st.rerun()

        if st.session_state.get("geocoding_orig_error"):
            st.error(f"⚠️ {st.session_state.geocoding_orig_error}")

        # Interactive Location Disambiguation for Start Location
        orig_cands = st.session_state.get("orig_candidates", [])
        if orig_cands and st.session_state.get("orig_candidates_query") == orig_text:
            st.markdown(
                f"<div style='background: rgba(14, 165, 233, 0.12); border: 1px solid rgba(56, 189, 248, 0.45); border-radius: 8px; padding: 10px 12px; margin: 4px 0 10px 0;'>"
                f"<div style='font-size:0.82rem; color:#38bdf8; font-weight:700; margin-bottom:6px;'>🔍 Multiple locations match <i>\"{orig_text}\"</i>. Please select your origin:</div>",
                unsafe_allow_html=True
            )
            for c_idx, cand in enumerate(orig_cands):
                c_name = cand.get("name") or cand.get("display_name", "").split(",")[0].strip()
                c_state = cand.get("state") or ""
                c_country = cand.get("country") or ""
                c_city = cand.get("city") or ""
                admin_parts = [p for p in [c_city, c_state, c_country] if p]
                admin_str = ", ".join(admin_parts) if admin_parts else cand.get("display_name", "")
                btn_caption = f"📍 {c_name} — {admin_str}  •  ({cand['lat']:.4f}, {cand['lon']:.4f})"
                if cand.get("provider"):
                    btn_caption += f"  [{cand['provider']}]"

                if st.button(btn_caption, key=f"btn_confirm_orig_{c_idx}", use_container_width=True):
                    st.session_state.user_live_coords = (cand["lat"], cand["lon"])
                    st.session_state.user_live_label = cand.get("display_name", c_name)
                    st.session_state.selected_orig_id = cand.get("provider_id", f"orig_{cand['lat']:.4f}_{cand['lon']:.4f}")
                    st.session_state.active_orig_meta = cand
                    st.session_state.pending_orig = cand["display_name"]
                    st.session_state.last_synced_orig = cand["display_name"]
                    st.session_state.orig_candidates = []
                    st.session_state.orig_candidates_query = ""
                    st.session_state.geocoding_orig_error = None
                    st.session_state._prev_route_sig = None
                    st.session_state.focused_route_id = "ALL"
                    st.session_state.selected_route_id = None
                    st.session_state.auto_fit_bounds = True
                    st.session_state.real_location_service.set_manual_location(cand["lat"], cand["lon"], cand["display_name"])
                    st.toast(f"Confirmed Origin: {c_name} ({admin_str})", icon="✅")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # Campus Internal Location Notice (Phase 2.6)
        active_orig_meta = st.session_state.get("active_orig_meta")
        if active_orig_meta and active_orig_meta.get("is_campus_internal"):
            ent_note = active_orig_meta.get("campus_entrance") or "Campus Main Entrance Gate"
            st.caption(f"🏛️ **Campus Internal POI:** Vehicular routes navigate to **{ent_note}**. Pedestrian walkways guide inside.")

    with col_swap_btn:
        # Single creative circular swap button - no lock button
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.button("⇄", key="btn_swap_locations", help="↕️ Swap Start & Destination", use_container_width=True):
            prev_orig_txt = st.session_state.txt_orig
            prev_dest_txt = st.session_state.txt_dest
            st.session_state.pending_orig = prev_dest_txt
            st.session_state.pending_dest = prev_orig_txt
            c_orig = st.session_state.user_live_coords
            l_orig = st.session_state.user_live_label
            id_orig = st.session_state.get("selected_orig_id")
            meta_orig = st.session_state.get("active_orig_meta")
            id_dest = st.session_state.get("selected_dest_id")
            meta_dest = st.session_state.get("active_dest_meta")
            if st.session_state.selected_dest_coords:
                st.session_state.user_live_coords = st.session_state.selected_dest_coords
                st.session_state.user_live_label = st.session_state.selected_dest_label
                st.session_state.selected_orig_id = id_dest
                st.session_state.active_orig_meta = meta_dest
                st.session_state.is_custom_start_place = True
            st.session_state.selected_dest_coords = c_orig
            st.session_state.selected_dest_label = l_orig
            st.session_state.selected_dest_id = id_orig
            st.session_state.active_dest_meta = meta_orig
            st.session_state.orig_candidates = []
            st.session_state.orig_candidates_query = ""
            st.session_state.dest_candidates = []
            st.session_state.dest_candidates_query = ""
            st.session_state.movement_index = 0
            st.session_state.is_in_transit = False
            st.session_state.user_speed_kmh = 0.0
            st.session_state.user_bearing_deg = 0.0
            st.session_state._prev_route_sig = None
            st.session_state.focused_route_id = "ALL"
            st.session_state.selected_route_id = None
            st.session_state.auto_fit_bounds = True
            if st.session_state.user_live_coords:
                st.session_state.real_location_service.set_manual_location(
                    st.session_state.user_live_coords[0],
                    st.session_state.user_live_coords[1],
                    str(st.session_state.user_live_label)
                )
            st.toast("🔄 Swapped Start ↔ Destination!", icon="🔄")
            st.rerun()

    with col_dest_in:
        dest_text = st.text_input(
            "🏁 Destination",
            key="txt_dest",
            placeholder="🗺️ Type destination city, village, landmark or address — or click map...",
            help="Type your destination city, village, address, landmark, or click anywhere on the interactive map to set it."
        )
        if dest_text and dest_text != st.session_state.last_synced_dest:
            st.session_state.last_synced_dest = dest_text
            if "current" in dest_text.lower():
                CURRENT_BASE = st.session_state.get("hardware_gps_coords") or detected_coords
                st.session_state.selected_dest_coords = CURRENT_BASE
                st.session_state.selected_dest_label = detected_label
                st.session_state.selected_dest_id = "gps_current_hardware"
                st.session_state.dest_candidates = []
                st.session_state.dest_candidates_query = ""
                st.session_state.geocoding_dest_error = None
                st.session_state._prev_route_sig = None
                st.session_state.focused_route_id = "ALL"
                st.session_state.selected_route_id = None
                st.session_state.auto_fit_bounds = True
                st.rerun()
            else:
                c_origin = st.session_state.get("user_live_coords")
                cands_d = st.session_state.real_map_service.geocode_candidates(dest_text, limit=5, origin_coords=c_origin)
                if cands_d:
                    st.session_state.geocoding_dest_error = None
                    if len(cands_d) == 1:
                        # Unique, high-confidence place: convenient direct route calculation
                        best_d = cands_d[0]
                        st.session_state.selected_dest_coords = (best_d["lat"], best_d["lon"])
                        st.session_state.selected_dest_label = best_d.get("display_name", dest_text)
                        st.session_state.selected_dest_id = best_d.get("provider_id", f"dest_{best_d['lat']:.4f}_{best_d['lon']:.4f}")
                        st.session_state.active_dest_meta = best_d
                        st.session_state.dest_candidates = []
                        st.session_state.dest_candidates_query = ""
                        st.session_state._prev_route_sig = None
                        st.session_state.focused_route_id = "ALL"
                        st.session_state.selected_route_id = None
                        st.session_state.auto_fit_bounds = True
                        st.session_state.movement_index = 0
                        st.session_state.is_in_transit = False
                        st.session_state.user_speed_kmh = 0.0
                        st.session_state.user_bearing_deg = 0.0
                        st.toast(f"🏁 Destination → {best_d.get('city') or dest_text}", icon="🏁")
                        st.rerun()
                    else:
                        # Multiple plausible matches: require user to select intended location before routing
                        st.session_state.dest_candidates = cands_d
                        st.session_state.dest_candidates_query = dest_text
                        st.session_state.selected_dest_coords = None
                        st.session_state.selected_dest_label = None
                        st.session_state.selected_dest_id = None
                        st.session_state.active_dest_meta = None
                        st.session_state._prev_route_sig = None
                        st.session_state.focused_route_id = "ALL"
                        st.session_state.selected_route_id = None
                        st.toast(f"🔍 Found {len(cands_d)} locations for '{dest_text}'. Please select one below.", icon="🔍")
                        st.rerun()
                else:
                    st.session_state.selected_dest_coords = None
                    st.session_state.selected_dest_label = None
                    st.session_state.selected_dest_id = None
                    st.session_state.active_dest_meta = None
                    st.session_state.dest_candidates = []
                    st.session_state.dest_candidates_query = ""
                    st.session_state._prev_route_sig = None
                    st.session_state.focused_route_id = "ALL"
                    st.session_state.selected_route_id = None
                    st.session_state.selected_route_object = None
                    st.session_state.geocoding_dest_error = f"Could not find coordinates for '{dest_text}'. Please check the place name or click anywhere on the map."
                    st.toast(f"⚠️ Could not resolve destination '{dest_text}'.", icon="⚠️")
                    st.rerun()

        if st.session_state.get("geocoding_dest_error"):
            st.error(f"⚠️ {st.session_state.geocoding_dest_error}")

        # Interactive Location Disambiguation for Destination
        dest_cands = st.session_state.get("dest_candidates", [])
        if dest_cands and st.session_state.get("dest_candidates_query") == dest_text:
            st.markdown(
                f"<div style='background: rgba(14, 165, 233, 0.12); border: 1px solid rgba(56, 189, 248, 0.45); border-radius: 8px; padding: 10px 12px; margin: 4px 0 10px 0;'>"
                f"<div style='font-size:0.82rem; color:#38bdf8; font-weight:700; margin-bottom:6px;'>🔍 Multiple locations match <i>\"{dest_text}\"</i>. Please select your destination:</div>",
                unsafe_allow_html=True
            )
            for c_idx, cand in enumerate(dest_cands):
                c_name = cand.get("name") or cand.get("display_name", "").split(",")[0].strip()
                c_state = cand.get("state") or ""
                c_country = cand.get("country") or ""
                c_city = cand.get("city") or ""
                admin_parts = [p for p in [c_city, c_state, c_country] if p]
                admin_str = ", ".join(admin_parts) if admin_parts else cand.get("display_name", "")
                btn_caption = f"🏁 {c_name} — {admin_str}  •  ({cand['lat']:.4f}, {cand['lon']:.4f})"
                if cand.get("provider"):
                    btn_caption += f"  [{cand['provider']}]"

                if st.button(btn_caption, key=f"btn_confirm_dest_{c_idx}", use_container_width=True):
                    st.session_state.selected_dest_coords = (cand["lat"], cand["lon"])
                    st.session_state.selected_dest_label = cand.get("display_name", c_name)
                    st.session_state.selected_dest_id = cand.get("provider_id", f"dest_{cand['lat']:.4f}_{cand['lon']:.4f}")
                    st.session_state.active_dest_meta = cand
                    st.session_state.pending_dest = cand["display_name"]
                    st.session_state.last_synced_dest = cand["display_name"]
                    st.session_state.dest_candidates = []
                    st.session_state.dest_candidates_query = ""
                    st.session_state.geocoding_dest_error = None
                    st.session_state._prev_route_sig = None
                    st.session_state.focused_route_id = "ALL"
                    st.session_state.selected_route_id = None
                    st.session_state.auto_fit_bounds = True
                    st.session_state.movement_index = 0
                    st.session_state.is_in_transit = False
                    st.session_state.user_speed_kmh = 0.0
                    st.session_state.user_bearing_deg = 0.0
                    st.toast(f"Confirmed Destination: {c_name} ({admin_str})", icon="✅")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # Campus Internal Location Notice for Destination (Phase 2.6)
        active_dest_meta = st.session_state.get("active_dest_meta")
        if active_dest_meta and active_dest_meta.get("is_campus_internal"):
            ent_note = active_dest_meta.get("campus_entrance") or "Campus Main Entrance Gate"
            st.caption(f"🏛️ **Campus Internal POI:** Roads navigate to **{ent_note}**. Internal pedestrian routing guides to building.")

    # Location Resolved Coordinates & Status Indicator Strip
    c_orig_live = st.session_state.get("user_live_coords")
    l_orig_live = st.session_state.get("user_live_label") or ("Satellite GPS" if not st.session_state.get("is_custom_start_place") else "Origin")
    c_dest_live = st.session_state.get("selected_dest_coords")
    l_dest_live = st.session_state.get("selected_dest_label") or "Destination"

    if c_orig_live and c_dest_live:
        st.markdown(f"""
        <div style='background: rgba(15, 23, 42, 0.72); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 8px; padding: 7px 14px; margin-top: 6px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;'>
            <div style='display: flex; align-items: center; gap: 14px; font-size: 0.78rem; color: #cbd5e1; flex-wrap: wrap;'>
                <span>🟢 <b>Start:</b> <span style='color: #38bdf8;'>{str(l_orig_live)[:38]}</span> <code style='font-size: 0.72rem; color: #94a3b8;'>({c_orig_live[0]:.4f}, {c_orig_live[1]:.4f})</code></span>
                <span style='color: #64748b;'>➔</span>
                <span>🏁 <b>Destination:</b> <span style='color: #38bdf8;'>{str(l_dest_live)[:38]}</span> <code style='font-size: 0.72rem; color: #94a3b8;'>({c_dest_live[0]:.4f}, {c_dest_live[1]:.4f})</code></span>
            </div>
            <div style='font-size: 0.70rem; color: #34d399; font-weight: 700; background: rgba(16, 185, 129, 0.15); padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.35);'>
                ✓ GPS & Coords Synchronized
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif c_orig_live and not c_dest_live:
        st.markdown(f"""
        <div style='background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 6px 12px; margin-top: 6px; margin-bottom: 8px; font-size: 0.76rem; color: #fbbf24; display: flex; align-items: center; gap: 8px;'>
            <span>📍 Start: <b>{str(l_orig_live)[:45]}</b> ({c_orig_live[0]:.4f}, {c_orig_live[1]:.4f}) • Enter destination above or click on the map to calculate routes</span>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # CREATIVE TRANSIT VEHICLE FLEET SELECTOR (EQUAL UNIFORM DECK)
    # =========================================================================
    MODES_CONFIG = {
        "CAR": {
            "icon": "🚗",
            "name": "Car",
            "label": "🚗 Car",
            "mode": TravelMode.DRIVING,
            "desc": "Automobile • Rapid Arterials & Expressways",
            "badge": "🚗 Highway Transit"
        },
        "BIKE": {
            "icon": "🏍️",
            "name": "Bike",
            "label": "🏍️ Bike",
            "mode": TravelMode.MOTORCYCLE,
            "desc": "Motorcycle / Scooter • Agile Lane Traversal",
            "badge": "🏍️ Agile Transit"
        },
        "BUS": {
            "icon": "🚌",
            "name": "Bus",
            "label": "🚌 Bus",
            "mode": TravelMode.BUS,
            "desc": "Transit Bus • Wide Corridor & Commercial Arterials",
            "badge": "🚌 Public Transit Corridor"
        },
        "TRUCK": {
            "icon": "🚚",
            "name": "Truck",
            "label": "🚚 Truck",
            "mode": TravelMode.TRUCK,
            "desc": "Heavy Commercial • Industrial Bypass & Broad Highways",
            "badge": "🚚 Heavy Transport"
        },
        "TRACTOR": {
            "icon": "🚜",
            "name": "Tractor",
            "label": "🚜 Tractor",
            "mode": TravelMode.TRACTOR,
            "desc": "Rural & Agricultural • Secondary Rural Links & Bunds",
            "badge": "🚜 Agro Rural Transit"
        },
        "BICYCLE": {
            "icon": "🚴",
            "name": "Cycle",
            "label": "🚴 Bicycle",
            "mode": TravelMode.BICYCLING,
            "desc": "Bicycle • Step-Free Local Paths & Green Corridors",
            "badge": "🚴 Eco Cycleway"
        },
        "WALK": {
            "icon": "🚶",
            "name": "Walk",
            "label": "🚶 Walk",
            "mode": TravelMode.WALKING,
            "desc": "Pedestrian • Safe Walkways, Sidewalks & Step-Free Crossings",
            "badge": "🚶 Pedestrian Walkway"
        }
    }

    if "selected_travel_mode" not in st.session_state:
        prev = st.session_state.get("last_selected_mode", "CAR")
        if "Bus" in str(prev):
            st.session_state.selected_travel_mode = "BUS"
        elif "Bike" in str(prev) and "🚴" not in str(prev):
            st.session_state.selected_travel_mode = "BIKE"
        elif "Tractor" in str(prev):
            st.session_state.selected_travel_mode = "TRACTOR"
        elif "Truck" in str(prev):
            st.session_state.selected_travel_mode = "TRUCK"
        elif "Bicycl" in str(prev) or "🚴" in str(prev):
            st.session_state.selected_travel_mode = "BICYCLE"
        elif "Walk" in str(prev):
            st.session_state.selected_travel_mode = "WALK"
        else:
            st.session_state.selected_travel_mode = "CAR"

    st.markdown("""
    <div style='display: flex; align-items: center; justify-content: space-between; margin-top: 10px; margin-bottom: 6px;'>
        <div style='font-size: 0.80rem; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 6px;'>
            <span>⚡</span> TRAVEL MODE & VEHICLE FLEET:
        </div>
        <div style='font-size: 0.70rem; color: #94a3b8;'>
            Select Vehicle • Dedicated Routing Profiles
        </div>
    </div>
    <style>
    /* Creative Equal-Sized Vehicle Fleet Deck */
    .st-key-fleet_deck_container div[data-testid="stHorizontalBlock"] {
        gap: 8px !important;
        align-items: stretch !important;
    }
    .st-key-fleet_deck_container div[data-testid="stColumn"] {
        min-width: 0 !important;
        flex: 1 1 0px !important;
        width: 100% !important;
    }
    .st-key-fleet_deck_container div[data-testid="stButton"] {
        width: 100% !important;
        height: 100% !important;
    }
    .st-key-fleet_deck_container div[data-testid="stButton"] > button {
        width: 100% !important;
        height: 60px !important;
        min-height: 60px !important;
        max-height: 60px !important;
        border-radius: 12px !important;
        padding: 6px 2px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        box-sizing: border-box !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .st-key-fleet_deck_container div[data-testid="stButton"] > button div[data-testid="stMarkdownContainer"] {
        width: 100% !important;
        text-align: center !important;
    }
    .st-key-fleet_deck_container div[data-testid="stButton"] > button div[data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
        line-height: 1.25 !important;
        font-size: 0.88rem !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 2px !important;
    }
    /* Active Button State (Selected Vehicle) */
    .st-key-fleet_deck_container div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(180deg, rgba(16, 185, 129, 0.28) 0%, rgba(6, 78, 59, 0.55) 100%) !important;
        border: 2px solid #10b981 !important;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.40), 0 4px 14px rgba(0, 0, 0, 0.50), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-2px) !important;
    }
    /* Inactive Button State */
    .st-key-fleet_deck_container div[data-testid="stButton"] > button[kind="secondary"] {
        background: rgba(15, 23, 42, 0.76) !important;
        border: 1.5px solid rgba(56, 189, 248, 0.20) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35) !important;
    }
    .st-key-fleet_deck_container div[data-testid="stButton"] > button[kind="secondary"]:hover {
        border-color: #38bdf8 !important;
        background: rgba(30, 41, 59, 0.88) !important;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.30), 0 4px 14px rgba(0, 0, 0, 0.45) !important;
        transform: translateY(-2px) !important;
    }

    /* Speed Mode Selector Styling */
    .st-key-speed_deck_container div[data-testid="stHorizontalBlock"] {
        gap: 8px !important;
        align-items: stretch !important;
    }
    .st-key-speed_deck_container div[data-testid="stColumn"] {
        min-width: 0 !important;
        flex: 1 1 0px !important;
        width: 100% !important;
    }
    .st-key-speed_deck_container div[data-testid="stButton"] > button {
        width: 100% !important;
        height: 52px !important;
        min-height: 52px !important;
        max-height: 52px !important;
        border-radius: 10px !important;
        padding: 4px 6px !important;
        font-size: 0.84rem !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
    }
    .st-key-speed_deck_container div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(180deg, rgba(56, 189, 248, 0.30) 0%, rgba(2, 132, 199, 0.60) 100%) !important;
        border: 2px solid #38bdf8 !important;
        box-shadow: 0 0 18px rgba(56, 189, 248, 0.40) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container(key="fleet_deck_container"):
        m_cols = st.columns(7)
        selected_key = st.session_state.selected_travel_mode
        for idx, (m_k, m_info) in enumerate(MODES_CONFIG.items()):
            with m_cols[idx]:
                is_selected = (m_k == selected_key)
                btn_type = "primary" if is_selected else "secondary"
                card_label = f"{m_info['icon']}\n\n**{m_info['name']}**"
                if st.button(card_label, key=f"btn_mode_select_{m_k}", use_container_width=True, type=btn_type):
                    st.session_state.selected_travel_mode = m_k
                    st.session_state.last_selected_mode = m_info["label"]
                    st.rerun()

    current_mode_info = MODES_CONFIG.get(st.session_state.selected_travel_mode, MODES_CONFIG["CAR"])
    travel_mode = current_mode_info["mode"]
    travel_mode_str = current_mode_info["label"]
    st.session_state.last_selected_mode = travel_mode_str

    # =========================================================================
    # SEPARATE SPEED MODE SELECTOR (ECO, NORMAL, FAST, CUSTOM)
    # =========================================================================
    SPEED_LIMITS_CONFIG = {
        "CAR": {"min": 30, "max": 140, "default": 80, "step": 5, "profile": "Motorized Highway & Arterial Automobile"},
        "BIKE": {"min": 20, "max": 100, "default": 65, "step": 5, "profile": "Motorcycle / Scooter Agile Flow"},
        "BUS": {"min": 20, "max": 80, "default": 45, "step": 5, "profile": "Commercial Public Transit Bus Corridor"},
        "TRUCK": {"min": 20, "max": 75, "default": 55, "step": 5, "profile": "Heavy Freight Commercial Vehicle"},
        "TRACTOR": {"min": 10, "max": 35, "default": 22, "step": 2, "profile": "Agricultural & Rural Secondary Link"},
        "BICYCLE": {"min": 8, "max": 35, "default": 16, "step": 1, "profile": "Non-Motorized Human-Powered Bicycle"},
        "WALK": {"min": 2, "max": 8, "default": 5, "step": 1, "profile": "Non-Motorized Pedestrian Sidewalk Pace"}
    }

    sel_vehicle_key = st.session_state.selected_travel_mode
    vehicle_limits = SPEED_LIMITS_CONFIG.get(sel_vehicle_key, SPEED_LIMITS_CONFIG["CAR"])

    if "selected_speed_mode" not in st.session_state:
        st.session_state.selected_speed_mode = "NORMAL"

    if "custom_speed_kmh" not in st.session_state:
        st.session_state.custom_speed_kmh = vehicle_limits["default"]
    else:
        # Validate and clamp custom speed if vehicle changed
        st.session_state.custom_speed_kmh = max(vehicle_limits["min"], min(vehicle_limits["max"], st.session_state.custom_speed_kmh))

    st.markdown("""
    <div style='display: flex; align-items: center; justify-content: space-between; margin-top: 14px; margin-bottom: 6px;'>
        <div style='font-size: 0.80rem; font-weight: 800; color: #a78bfa; text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 6px;'>
            <span>🎛️</span> SPEED MODE & TRANSIT PROFILE:
        </div>
        <div style='font-size: 0.70rem; color: #94a3b8;'>
            Adapted to Selected Vehicle • Realistic Speed Limits
        </div>
    </div>
    """, unsafe_allow_html=True)

    SPEED_MODES = {
        "ECO": {"icon": "🌿", "label": "Eco", "desc": "Conservative cruising profile for energy efficiency and reduced drag"},
        "NORMAL": {"icon": "⚡", "label": "Normal", "desc": "Standard baseline routing and corridor travel-time assumptions"},
        "FAST": {"icon": "🚀", "label": "Fast", "desc": "Upper permissible corridor speeds where road geometry permits"},
        "CUSTOM": {"icon": "⚙️", "label": "Custom", "desc": f"Configurable cruising speed preference ({vehicle_limits['min']} - {vehicle_limits['max']} km/h)"}
    }

    with st.container(key="speed_deck_container"):
        s_cols = st.columns(4)
        active_speed_key = st.session_state.selected_speed_mode
        for s_idx, (s_k, s_info) in enumerate(SPEED_MODES.items()):
            with s_cols[s_idx]:
                s_selected = (s_k == active_speed_key)
                s_btn_type = "primary" if s_selected else "secondary"
                s_btn_label = f"{s_info['icon']} **{s_info['label']}**"
                if st.button(s_btn_label, key=f"btn_speed_mode_{s_k}", use_container_width=True, type=s_btn_type):
                    st.session_state.selected_speed_mode = s_k
                    st.rerun()

    # Custom Speed Slider & Validation (shown only when Custom mode is selected)
    if st.session_state.selected_speed_mode == "CUSTOM":
        st.markdown(f"""
        <div style='background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(167, 139, 250, 0.4); border-radius: 10px; padding: 10px 14px; margin-top: 6px;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-size: 0.82rem; font-weight: 800; color: #c4b5fd;'>⚙️ Custom Speed Setting ({current_mode_info['name']}):</span>
                <span style='font-size: 0.88rem; font-weight: 800; color: #38bdf8; font-family: monospace;'>{st.session_state.custom_speed_kmh} km/h</span>
            </div>
            <div style='font-size: 0.72rem; color: #94a3b8; margin-top: 2px;'>
                Range for {vehicle_limits['profile']}: <b>{vehicle_limits['min']} km/h</b> to <b>{vehicle_limits['max']} km/h</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
        new_speed = st.slider(
            label="Configure target cruise speed preference:",
            min_value=vehicle_limits["min"],
            max_value=vehicle_limits["max"],
            value=st.session_state.custom_speed_kmh,
            step=vehicle_limits["step"],
            format="%d km/h",
            key="slider_custom_speed"
        )
        if new_speed != st.session_state.custom_speed_kmh:
            st.session_state.custom_speed_kmh = new_speed
            st.rerun()

    # Informative Context Badge
    speed_mode_desc = SPEED_MODES[st.session_state.selected_speed_mode]["desc"]
    st.markdown(f"""
    <div style='background: rgba(30, 41, 59, 0.45); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 6px 12px; margin-top: 6px; margin-bottom: 8px; font-size: 0.74rem; color: #cbd5e1; display: flex; align-items: center; justify-content: space-between;'>
        <span><b>Active Profile:</b> {SPEED_MODES[st.session_state.selected_speed_mode]['icon']} {st.session_state.selected_speed_mode} • {speed_mode_desc}</span>
        <span style='color: #94a3b8; font-size: 0.68rem;'>Road safety limits & legal constraints take precedence</span>
    </div>
    """, unsafe_allow_html=True)



    coords_orig = st.session_state.user_live_coords
    coords_dest = st.session_state.selected_dest_coords

    # Evaluate & Rank Candidate Routes using Multi-Objective Optimization Model
    active_obj = st.session_state.get("active_objective", OptimizationObjective.FASTEST)
    require_acc = st.session_state.get("requires_accessible", False) or (active_obj == OptimizationObjective.ACCESSIBLE)

    # Guard: both origin and destination must be set before route calculation
    if not coords_orig or not coords_dest:
        _missing = []
        if not coords_orig:
            _missing.append("origin")
        if not coords_dest:
            _missing.append("destination")
        _missing_str = " and ".join(_missing)
        st.markdown(f"""
        <div style='background: rgba(56, 189, 248, 0.10); border: 1.5px solid rgba(56, 189, 248, 0.35);
                    border-radius: 12px; padding: 18px 22px; margin: 14px 0; text-align: center;'>
            <div style='font-size: 2.2rem; margin-bottom: 6px;'>🗺️</div>
            <div style='color: #7dd3fc; font-weight: 800; font-size: 1.0rem;'>Set Your {_missing_str.title()}</div>
            <div style='color: #94a3b8; font-size: 0.84rem; margin-top: 6px;'>
                Enter a {_missing_str} above or click on the map to start navigating.
            </div>
        </div>
        """, unsafe_allow_html=True)
        candidate_routes = []
        ranked_routes = []
        eligible_ranked = []
        restricted_ranked = []
        # Fallback coords_dest to coords_orig so downstream map rendering doesn't crash
        if not coords_dest and coords_orig:
            coords_dest = coords_orig
    else:
        # Route signature tracking: When origin, destination, mode, or speed settings change, refresh route
        endpoint_sig = (
            round(coords_orig[0], 4), round(coords_orig[1], 4),
            round(coords_dest[0], 4), round(coords_dest[1], 4),
            travel_mode.value if hasattr(travel_mode, "value") else str(travel_mode),
            st.session_state.selected_speed_mode,
            st.session_state.custom_speed_kmh if st.session_state.selected_speed_mode == "CUSTOM" else 0,
            st.session_state.get("avoid_tolls", False),
            st.session_state.get("avoid_highways", False),
            st.session_state.get("avoid_ferries", False)
        )
        if "cached_candidate_routes" not in st.session_state or st.session_state.get("_prev_endpoint_sig") != endpoint_sig:
            st.session_state._prev_endpoint_sig = endpoint_sig
            st.session_state.focused_route_id = "ALL"
            st.session_state.selected_route_id = None
            st.session_state.selected_route_object = None
            st.session_state.auto_fit_bounds = True
            with st.spinner("⚡ Connecting live corridors & calculating optimal routes..."):
                candidate_routes = st.session_state.real_route_engine.calculate_routes(
                    coords_orig[0], coords_orig[1],
                    coords_dest[0], coords_dest[1],
                    mode=travel_mode,
                    require_accessible=require_acc,
                    is_in_transit=st.session_state.get("is_in_transit", False),
                    active_hazard_count=active_restr_count,
                    avoid_tolls=st.session_state.get("avoid_tolls", False),
                    avoid_highways=st.session_state.get("avoid_highways", False),
                    avoid_ferries=st.session_state.get("avoid_ferries", False),
                    speed_mode=st.session_state.selected_speed_mode.lower(),
                    custom_speed_kmh=st.session_state.custom_speed_kmh if st.session_state.selected_speed_mode == "CUSTOM" else None
                )
            st.session_state.cached_candidate_routes = candidate_routes
        else:
            candidate_routes = st.session_state.cached_candidate_routes

        if not candidate_routes:
            fail_msg = getattr(st.session_state.real_route_engine, "last_failure_reason", None) or (
                f"No continuous routable connection found between ({coords_orig[0]:.4f}, {coords_orig[1]:.4f}) "
                f"and ({coords_dest[0]:.4f}, {coords_dest[1]:.4f}). "
                "Locations may be across an ocean or on disconnected island networks."
            )
            st.markdown(f"""
            <div style='background: rgba(239, 68, 68, 0.18); border: 1.5px solid #ef4444; border-radius: 10px; padding: 12px 16px; margin: 10px 0;'>
                <div style='color: #f87171; font-weight: 800; font-size: 0.95rem;'>🚫 ROUTE UNAVAILABLE</div>
                <div style='color: #f1f5f9; font-size: 0.84rem; margin-top: 4px;'>{fail_msg}</div>
            </div>
            """, unsafe_allow_html=True)
            ranked_routes = []
        else:
            ranked_routes = st.session_state.multi_objective_router.evaluate_and_rank_routes(
                candidate_routes=candidate_routes,
                objective=active_obj,
                require_accessible=require_acc
            )

        eligible_ranked = [r for r in ranked_routes if r.is_eligible] or ranked_routes
        restricted_ranked = [r for r in ranked_routes if not r.is_eligible]

    # Check query parameters for touchable route card clicks
    if "focus_route" in st.query_params:
        q_route = st.query_params.get("focus_route")
        if q_route:
            st.session_state.focused_route_id = q_route
            st.session_state.selected_route_id = q_route if q_route != "ALL" else None
            st.session_state.auto_fit_bounds = True
            st.session_state.scroll_to_app_map = True
        try:
            del st.query_params["focus_route"]
        except Exception:
            pass

    # Validate and retrieve focused route state (defaults to "ALL" so all routes start visible)
    if "focused_route_id" not in st.session_state:
        st.session_state.focused_route_id = "ALL"

    # Resolve semantic objective focus keywords to exact route_id
    valid_route_ids = {r.route.route_id for r in ranked_routes}
    if st.session_state.focused_route_id == "FASTEST" and ranked_routes:
        eligible = [r for r in ranked_routes if r.is_eligible]
        target = min(eligible or ranked_routes, key=lambda r: r.effective_duration_minutes)
        cur_focus = target.route.route_id
    elif st.session_state.focused_route_id == "SHORTEST" and ranked_routes:
        eligible = [r for r in ranked_routes if r.is_eligible]
        target = min(eligible or ranked_routes, key=lambda r: r.effective_distance_km)
        cur_focus = target.route.route_id
    elif st.session_state.focused_route_id == "BALANCED" and ranked_routes:
        pool = [r for r in ranked_routes if r.is_eligible] or ranked_routes
        min_t = min(r.effective_duration_minutes for r in pool)
        min_d = min(r.effective_distance_km for r in pool)
        target = min(
            pool,
            key=lambda r: 0.50 * (r.effective_duration_minutes / max(0.01, min_t)) + 0.50 * (r.effective_distance_km / max(0.01, min_d))
        )
        cur_focus = target.route.route_id
    elif st.session_state.focused_route_id == "ACCESSIBLE" and ranked_routes:
        acc = [r for r in ranked_routes if getattr(r.route, "is_accessible", True) and r.is_eligible]
        target = acc[0] if acc else (ranked_routes[0] if ranked_routes else None)
        cur_focus = target.route.route_id if target else "ALL"
    elif st.session_state.focused_route_id in valid_route_ids:
        cur_focus = st.session_state.focused_route_id
    else:
        cur_focus = "ALL"
        st.session_state.focused_route_id = "ALL"
        st.session_state.selected_route_id = None

    # Reference active selected route object in session state
    if cur_focus != "ALL":
        active_sel_item = next((r for r in ranked_routes if r.route.route_id == cur_focus), None)
        st.session_state.selected_route_object = active_sel_item.route if active_sel_item else None
        st.session_state.selected_route_id = cur_focus
        active_route_item = active_sel_item or (eligible_ranked[0] if eligible_ranked else (ranked_routes[0] if ranked_routes else None))
    else:
        st.session_state.selected_route_object = ranked_routes[0].route if ranked_routes else None
        st.session_state.selected_route_id = None
        active_route_item = eligible_ranked[0] if eligible_ranked else (ranked_routes[0] if ranked_routes else None)

    # Build Map Polylines with clean visual hierarchy and selection highlighting
    route_polylines = []
    palette = ["#10b981", "#0ea5e9", "#a855f7"]
    for r_item in ranked_routes:
        is_selected = (cur_focus == r_item.route.route_id)
        has_selection = (cur_focus != "ALL")

        if r_item.is_eligible:
            color = palette[(r_item.rank - 1) % len(palette)]
            if has_selection:
                weight = 8 if is_selected else 3.5
                opacity = 1.0 if is_selected else 0.40
            else:
                weight = 6 if r_item.rank == 1 else 4.5
                opacity = 0.95 if r_item.rank == 1 else 0.80
            label = f"Rank {r_item.rank}: {r_item.route.name} ({r_item.effective_duration_minutes:.1f} min)"
        else:
            color = "#ef4444"
            weight = 6 if is_selected else 3.5
            opacity = 0.90 if is_selected else 0.40
            label = f"⚠️ RESTRICTED / BLOCKED: {r_item.route.name}"

        r_coords = [list(pt) for pt in r_item.route.polyline]
        if coords_orig and r_coords:
            if abs(r_coords[0][0] - coords_orig[0]) > 0.00001 or abs(r_coords[0][1] - coords_orig[1]) > 0.00001:
                r_coords.insert(0, [coords_orig[0], coords_orig[1]])
        if coords_dest and r_coords:
            if abs(r_coords[-1][0] - coords_dest[0]) > 0.00001 or abs(r_coords[-1][1] - coords_dest[1]) > 0.00001:
                r_coords.append([coords_dest[0], coords_dest[1]])

        route_polylines.append({
            "name": label,
            "coordinates": r_coords,
            "color": color,
            "weight": weight,
            "opacity": opacity,
            "rank": r_item.rank,
            "is_eligible": r_item.is_eligible,
            "is_selected": is_selected,
            "route_id": r_item.route.route_id,
            "status": r_item.status.value
        })

    # Road restriction markers (construction cones & barricades)
    active_restrictions = st.session_state.road_condition_manager.get_active_restrictions()
    restriction_markers = []
    for restr in active_restrictions:
        restriction_markers.append({
            "lat": restr.latitude,
            "lon": restr.longitude,
            "radius_meters": restr.affected_radius_meters,
            "type": restr.restriction_type.value,
            "description": restr.description or restr.road_name,
            "road_name": restr.road_name,
            "source": restr.source,
            "is_hard_closure": restr.is_hard_closure,
            "is_demonstration": restr.is_demonstration
        })

    # Active Geographic Hazards from HazardMap with Caution Highlights
    active_hazards = st.session_state.real_hazard_map.get_active_hazards()
    hazard_markers = []
    for hz in active_hazards:
        hazard_markers.append({
            "lat": hz.latitude,
            "lon": hz.longitude,
            "radius_meters": hz.radius_meters,
            "incident_type": hz.incident_type,
            "severity": hz.severity.value,
            "description": hz.description,
            "affected_road_name": hz.affected_road_name or "Travel Corridor"
        })

    # Initialize map viewport zoom, satellite basemap style state, and Google Maps avoidances
    if "map_zoom" not in st.session_state:
        st.session_state.map_zoom = 14
    if "map_style" not in st.session_state:
        st.session_state.map_style = "satellite_hybrid"
    if "show_emergency_amenities_on_map" not in st.session_state:
        st.session_state.show_emergency_amenities_on_map = False
    if "avoid_tolls" not in st.session_state:
        st.session_state.avoid_tolls = False
    if "avoid_highways" not in st.session_state:
        st.session_state.avoid_highways = False
    if "avoid_ferries" not in st.session_state:
        st.session_state.avoid_ferries = False

    # Discover Real-World Emergency Services & Safety Amenities along Active Route Corridor
    primary_route_poly = []
    if route_polylines:
        chosen_r = next((r for r in route_polylines if r.get("is_selected")), None)
        if not chosen_r:
            chosen_r = next((r for r in route_polylines if r.get("is_eligible")), route_polylines[0])
        primary_route_poly = list(chosen_r.get("coordinates", []))
    if not primary_route_poly and coords_orig and coords_dest:
        primary_route_poly = [coords_orig, coords_dest]
    elif primary_route_poly:
        if coords_orig and (abs(primary_route_poly[0][0] - coords_orig[0]) > 0.00001 or abs(primary_route_poly[0][1] - coords_orig[1]) > 0.00001):
            primary_route_poly.insert(0, coords_orig)
        if coords_dest and (abs(primary_route_poly[-1][0] - coords_dest[0]) > 0.00001 or abs(primary_route_poly[-1][1] - coords_dest[1]) > 0.00001):
            primary_route_poly.append(coords_dest)

    # Center map on selected route polyline bounding box
    if primary_route_poly and len(primary_route_poly) >= 2:
        map_center_lat = (min(p[0] for p in primary_route_poly) + max(p[0] for p in primary_route_poly)) / 2.0
        map_center_lon = (min(p[1] for p in primary_route_poly) + max(p[1] for p in primary_route_poly)) / 2.0
    else:
        map_center_lat = (coords_orig[0] + coords_dest[0]) / 2.0 if coords_orig and coords_dest else 16.2335
        map_center_lon = (coords_orig[1] + coords_dest[1]) / 2.0 if coords_orig and coords_dest else 80.5505

    route_emergency_facilities = st.session_state.emergency_service_manager.get_facilities_along_route(
        polyline=primary_route_poly,
        corridor_radius_km=5.0,
        user_coords=coords_orig
    )

    # Compute facilities for active category selected in the sidebar
    active_cat_label = st.session_state.get("selected_sidebar_category", "🌐 All Facilities")
    if "Custom Search" in active_cat_label and st.session_state.get("custom_search_query"):
        custom_res = resolve_custom_search_facility(
            st.session_state.custom_search_query,
            origin_coords=coords_orig,
            geocode_fn=st.session_state.real_map_service.geocode
        )
        active_category_facilities = [custom_res] if custom_res else []
    else:
        active_category_facilities = get_facilities_for_category(
            category=active_cat_label,
            polyline=primary_route_poly,
            origin_coords=coords_orig,
            dest_coords=coords_dest,
            search_mode=st.session_state.get("fac_search_mode", "near_destination"),
            radius_km=st.session_state.get("fac_radius_km", 10.0),
            enable_demo_mode=st.session_state.get("enable_demo_mode", False)
        )

    all_map_facilities = []
    if st.session_state.get("show_category_facilities_on_map", True):
        all_map_facilities.extend(active_category_facilities)
    if st.session_state.get("show_emergency_amenities_on_map", False):
        all_map_facilities.extend([f.to_dict() for f in route_emergency_facilities])

    # Audit route corridor with Satellite Road Auditor (authenticates real road blockages)
    satellite_audit = st.session_state.satellite_auditor.audit_route_corridor(primary_route_poly)

    # AI Satellite Imagery & Computer-Vision Road Intelligence Analysis
    ai_road_report_obj = None
    ai_road_report_dict = None
    if primary_route_poly and len(primary_route_poly) >= 2:
        try:
            active_route_for_cv = None
            if ranked_routes:
                if cur_focus != "ALL":
                    active_route_for_cv = next((r.route for r in ranked_routes if r.route.route_id == cur_focus), ranked_routes[0].route)
                else:
                    active_route_for_cv = ranked_routes[0].route

            ai_road_report_obj = st.session_state.ai_road_controller.analyze_corridor(
                corridor_polyline=primary_route_poly,
                route_attributes={
                    "summary_roads": getattr(active_route_for_cv, "summary_roads", []) if active_route_for_cv else [],
                    "road_type": getattr(active_route_for_cv, "road_type", "primary") if active_route_for_cv else "primary",
                    "name": getattr(active_route_for_cv, "name", "") if active_route_for_cv else ""
                },
                avoidance_prefs={
                    "avoid_tolls": st.session_state.get("avoid_tolls", False),
                    "avoid_highways": st.session_state.get("avoid_highways", False),
                    "avoid_ferries": st.session_state.get("avoid_ferries", False)
                }
            )
            if ai_road_report_obj:
                ai_road_report_dict = asdict(ai_road_report_obj)
        except Exception as _e_cv:
            ai_road_report_obj = None
            ai_road_report_dict = None

    # Generate direct Google Maps mobile & web navigation deep link
    gmaps_nav_url = get_google_maps_app_url(
        origin_lat=coords_orig[0],
        origin_lon=coords_orig[1],
        dest_lat=coords_dest[0],
        dest_lon=coords_dest[1],
        travel_mode=travel_mode.value if hasattr(travel_mode, "value") else "driving",
        avoid_tolls=st.session_state.avoid_tolls,
        avoid_highways=st.session_state.avoid_highways,
        avoid_ferries=st.session_state.avoid_ferries
    )


    if "map_display_engine" not in st.session_state:
        st.session_state.map_display_engine = "tactical_satellite"

    # Modern Navigation Map Control Toolbar
    tb_c1, tb_c2, tb_c3 = st.columns([1.6, 1.0, 1.4], vertical_alignment="center")
    with tb_c1:
        st.markdown(
            "<div style='display:flex; align-items:center; gap:8px; margin-bottom: 4px;'>"
            "<span style='font-size: 0.82rem; font-weight: 800; color: #38bdf8; text-transform: uppercase;'>🗺️ Map Canvas</span>"
            "<span style='font-size: 0.68rem; background: rgba(56,189,248,0.14); border: 1px solid rgba(56,189,248,0.3); color: #38bdf8; padding: 2px 6px; border-radius: 4px;'>Full Vector & Satellite</span>"
            "</div>",
            unsafe_allow_html=True
        )
        sub_l1, sub_l2, sub_l3 = st.columns(3)
        cur_engine = st.session_state.get("map_display_engine", "tactical_satellite")
        with sub_l1:
            if st.button("🛰️ Satellite", key="btn_style_sat", type="primary" if cur_engine == "tactical_satellite" else "secondary", use_container_width=True):
                st.session_state.map_display_engine = "tactical_satellite"
                st.rerun()
        with sub_l2:
            if st.button("🗺️ Road", key="btn_style_road", type="primary" if cur_engine == "google_maps_sdk" else "secondary", use_container_width=True):
                st.session_state.map_display_engine = "google_maps_sdk"
                st.rerun()
        with sub_l3:
            if st.button("⛰️ Terrain", key="btn_style_terr", type="primary" if cur_engine == "google_terrain" else "secondary", use_container_width=True):
                st.session_state.map_display_engine = "google_terrain"
                st.rerun()
    with tb_c2:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        sub_act1, sub_act2 = st.columns(2)
        with sub_act1:
            if st.button("📍 GPS", key="btn_toolbar_gps", use_container_width=True, help="Snap origin to live hardware GPS"):
                st.session_state.is_custom_start_place = False
                st.session_state.orig_candidates = []
                CURRENT_BASE = st.session_state.get("hardware_gps_coords") or detected_coords
                st.session_state.user_live_coords = CURRENT_BASE
                st.session_state.user_live_label = detected_label
                st.session_state.movement_index = 0
                st.session_state.is_in_transit = False
                st.session_state.auto_fit_bounds = True
                st.session_state.scroll_to_app_map = True
                st.toast("📍 Re-centered to live GPS", icon="🛰️")
                st.rerun()
        with sub_act2:
            if st.button("🎯 Fit", key="btn_toolbar_fit", use_container_width=True, help="Auto-fit camera view to active route corridor"):
                st.session_state.auto_fit_bounds = True
                st.session_state.scroll_to_app_map = True
                st.rerun()
    with tb_c3:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        c_av1, c_av2, c_av3 = st.columns(3)
        with c_av1:
            new_toll = st.checkbox("Tolls", value=st.session_state.avoid_tolls, key="chk_avoid_tolls", help="Avoid Tolls")
            if new_toll != st.session_state.avoid_tolls:
                st.session_state.avoid_tolls = new_toll
                st.rerun()
        with c_av2:
            new_hwy = st.checkbox("Highways", value=st.session_state.avoid_highways, key="chk_avoid_highways", help="Avoid Highways")
            if new_hwy != st.session_state.avoid_highways:
                st.session_state.avoid_highways = new_hwy
                st.rerun()
        with c_av3:
            new_ferry = st.checkbox("Ferries", value=st.session_state.avoid_ferries, key="chk_avoid_ferries", help="Avoid Ferries")
            if new_ferry != st.session_state.avoid_ferries:
                st.session_state.avoid_ferries = new_ferry
                st.rerun()

    # Active Route On Map Banner (Shows which route is selected and highlighted)
    if cur_focus != "ALL":
        active_sel = next((r for r in ranked_routes if r.route.route_id == cur_focus), None)
        if active_sel:
            col_sel_info, col_sel_btn = st.columns([1.6, 0.4])
            with col_sel_info:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, rgba(14, 165, 233, 0.18) 0%, rgba(15, 23, 42, 0.95) 100%);
                            border: 1.5px solid #38bdf8; border-radius: 10px; padding: 10px 16px; margin-bottom: 8px;
                            box-shadow: 0 0 16px rgba(56, 189, 248, 0.25);'>
                    <div style='display: flex; align-items: center; justify-content: space-between;'>
                        <div style='display: flex; align-items: center; gap: 8px;'>
                            <span style='font-size: 1.1rem;'>🎯</span>
                            <b style='color: #ffffff; font-size: 0.96rem;'>Active on Map: {active_sel.route.name}</b>
                        </div>
                        <span style='background: rgba(56,189,248,0.25); color: #38bdf8; font-size: 0.70rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(56,189,248,0.4);'>SELECTED CORRIDOR</span>
                    </div>
                    <div style='color: #cbd5e1; font-size: 0.82rem; margin-top: 4px;'>
                        ⏱️ <b>{active_sel.effective_duration_minutes:.1f} mins</b> • 📏 <b>{format_distance(active_sel.effective_distance_km, st.session_state.get("distance_unit", "km"))}</b> • 📍 Via {", ".join(active_sel.route.summary_roads[:3]) if active_sel.route.summary_roads else "Direct Corridor"}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_sel_btn:
                if st.button("🌐 Show All Routes", key="btn_show_all_routes_top", use_container_width=True, type="secondary"):
                    st.session_state.focused_route_id = "ALL"
                    st.session_state.selected_route_id = None
                    st.session_state.auto_fit_bounds = True
                    st.session_state.scroll_to_app_map = True
                    st.rerun()

    st.markdown("<div id='application-map-viewport'></div>", unsafe_allow_html=True)

    if st.session_state.get("scroll_to_app_map", False):
        st.session_state.scroll_to_app_map = False
        components.html("""
        <script>
            setTimeout(function() {
                try {
                    var el = window.parent.document.getElementById('application-map-viewport') || 
                             window.parent.document.querySelector('.folium-map') ||
                             window.parent.document.querySelector('[data-testid="stIFrame"]');
                    if (el) {
                        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                } catch(e) {}
            }, 150);
        </script>
        """, height=0, width=0)

    # Map Viewport: Displays Official Google Maps Platform SDK (Roadmap, Satellite Hybrid, Terrain)
    # or Leaflet fallback engine
    eng = st.session_state.get("map_display_engine", "google_maps_sdk")

    if eng in ["google_maps_sdk", "real_google_maps", "tactical_satellite", "google_terrain"]:
        gmap_type = "roadmap"
        if eng == "tactical_satellite":
            gmap_type = "hybrid"
        elif eng == "google_terrain":
            gmap_type = "terrain"

        gmap_html = build_google_maps_javascript_html(
            center_lat=map_center_lat,
            center_lon=map_center_lon,
            zoom=st.session_state.map_zoom,
            origin_coords=coords_orig,
            origin_label=st.session_state.get("user_live_label") or st.session_state.get("txt_orig") or "Current Location",
            dest_coords=coords_dest,
            dest_label=st.session_state.get("selected_dest_label") or st.session_state.get("txt_dest") or "Destination",
            route_polyline=primary_route_poly,
            saved_locations=load_and_georeference_saved_locations(),
            amenities=all_map_facilities,
            hazards=hazard_markers,
            map_type=gmap_type,
            height_px=700,
            traveler_avatar=st.session_state.get("selected_travel_mode", "WALK").lower(),
            route_polylines=route_polylines,
            ai_road_report=ai_road_report_dict
        )
        components.html(gmap_html, height=720)
    else:
        cur_map_style = "google_maps_road"
        folium_map = st.session_state.real_map_service.build_interactive_map(
            center_lat=map_center_lat,
            center_lon=map_center_lon,
            zoom_start=st.session_state.map_zoom,
            origin_coords=coords_orig,
            dest_coords=coords_dest,
            route_polylines=route_polylines,
            hazards=hazard_markers,
            road_closures=restriction_markers,
            breadcrumb_trail=st.session_state.real_location_service.get_movement_trail(),
            map_style=cur_map_style,
            traveler_avatar=st.session_state.get("selected_travel_mode", "WALK").lower(),
            emergency_facilities=all_map_facilities,
            is_custom_origin=st.session_state.get("is_custom_start_place", False),
            auto_fit_bounds=st.session_state.get("auto_fit_bounds", True)
        )
        if st.session_state.get("auto_fit_bounds"):
            st.session_state.auto_fit_bounds = False

        cur_cat_key = st.session_state.get("selected_sidebar_category", "none").replace(" ", "_").replace("🍽️", "res").replace("⛽", "pet").replace("🏨", "hot").replace("🚨", "emg").replace("🏧", "atm").replace("🛍️", "mal").replace("🏥", "hsp").replace("🔍", "src")
        map_key = f"real_world_gmap_{cur_map_style}_{st.session_state.map_zoom}_{cur_focus}_{len(hazard_markers)}_{len(restriction_markers)}_{coords_orig[0]:.3f}_{coords_orig[1]:.3f}_{coords_dest[0]:.3f}_{coords_dest[1]:.3f}_{cur_cat_key}_{len(all_map_facilities)}"
        map_out = st_folium(folium_map, zoom=st.session_state.map_zoom, width=None, height=720, key=map_key, use_container_width=True, returned_objects=["last_clicked"])

        if map_out and map_out.get("zoom") is not None:
            live_zoom = map_out["zoom"]
            if isinstance(live_zoom, (int, float)) and int(live_zoom) != st.session_state.map_zoom:
                st.session_state.map_zoom = int(live_zoom)

        if map_out and map_out.get("last_clicked"):
            click_lat = round(map_out["last_clicked"]["lat"], 5)
            click_lon = round(map_out["last_clicked"]["lng"], 5)
            if (click_lat, click_lon) != st.session_state.selected_dest_coords:
                st.session_state.selected_dest_coords = (click_lat, click_lon)
                pin_dest = f"Map Pin ({click_lat}, {click_lon})"
                st.session_state.selected_dest_label = pin_dest
                st.session_state.pending_dest = pin_dest
                st.rerun()


    # =========================================================================
    # CREATIVE TRANSIT KINEMATICS & REAL-TIME DEPARTURE HUD (BELOW MAP)
    # Calculates accurate travel duration considering vehicle and cruising speed
    # =========================================================================
    active_route_item = None
    if ranked_routes:
        if cur_focus != "ALL":
            active_route_item = next((r for r in ranked_routes if r.route.route_id == cur_focus), None)
        if not active_route_item and eligible_ranked:
            active_route_item = eligible_ranked[0]
        elif not active_route_item and ranked_routes:
            active_route_item = ranked_routes[0]

    if active_route_item:
        cur_veh_key = st.session_state.get("selected_travel_mode", "CAR").upper().strip()
        veh_profile = VEHICLE_KINEMATIC_PROFILES.get(cur_veh_key, VEHICLE_KINEMATIC_PROFILES.get("CAR", {}))
        veh_emoji = veh_profile.get("emoji", "🚗")
        veh_speed = veh_profile.get("speed_kmh", 80)
        cur_unit_str = st.session_state.get("distance_unit", "km").upper()

        st.markdown("""
        <style>
        /* =========================================================================
           HIGH-TECH DISPATCH & TIMING COCKPIT DECK
           ========================================================================= */
        .st-key-dispatch_deck_container {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.92) 0%, rgba(30, 41, 59, 0.80) 100%) !important;
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
            border: 1.5px solid rgba(56, 189, 248, 0.25) !important;
            border-radius: 14px !important;
            padding: 14px 18px 12px 18px !important;
            margin: 12px 0 14px 0 !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.50), inset 0 1px 1px rgba(255, 255, 255, 0.10) !important;
        }

        /* Top Mini Header Strip */
        .dispatch-deck-topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }
        .dispatch-deck-title {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.74rem;
            font-weight: 900;
            letter-spacing: 0.08em;
            color: #f8fafc;
            text-transform: uppercase;
        }
        .dispatch-deck-badge-right {
            font-size: 0.65rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 6px;
            background: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.30);
            color: #38bdf8;
            letter-spacing: 0.04em;
        }

        /* Sub-Labels above controls */
        .dispatch-control-label {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            color: #38bdf8;
            text-transform: uppercase;
            margin-bottom: 6px;
            height: 20px;
        }
        .dispatch-control-chip {
            font-size: 0.60rem;
            font-weight: 700;
            padding: 1px 6px;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.14);
            color: #94a3b8;
            letter-spacing: 0.04em;
        }

        /* st.pills custom styling for Departure options */
        .st-key-dispatch_deck_container div[data-testid="stPills"] {
            display: flex !important;
            gap: 6px !important;
            align-items: center !important;
            height: 40px !important;
        }
        .st-key-dispatch_deck_container div[data-testid="stPills"] button {
            background: rgba(15, 23, 42, 0.75) !important;
            border: 1px solid rgba(56, 189, 248, 0.22) !important;
            border-radius: 9999px !important;
            padding: 0 14px !important;
            height: 38px !important;
            min-height: 38px !important;
            font-size: 0.78rem !important;
            font-weight: 700 !important;
            color: #94a3b8 !important;
            transition: all 0.20s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25) !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        .st-key-dispatch_deck_container div[data-testid="stPills"] button:hover {
            color: #f8fafc !important;
            border-color: #38bdf8 !important;
            background: rgba(56, 189, 248, 0.15) !important;
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.30) !important;
            transform: translateY(-1px) !important;
        }
        .st-key-dispatch_deck_container div[data-testid="stPills"] button[aria-checked="true"],
        .st-key-dispatch_deck_container div[data-testid="stPills"] button[data-checked="true"] {
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
            color: #ffffff !important;
            border: 1.5px solid #38bdf8 !important;
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.55), 0 3px 8px rgba(0, 0, 0, 0.4) !important;
            transform: translateY(-1px) !important;
            font-weight: 800 !important;
        }

        /* st.selectbox custom styling for Timezone */
        .st-key-dispatch_deck_container div[data-testid="stSelectbox"] {
            height: 40px !important;
        }
        .st-key-dispatch_deck_container div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            background: transparent !important;
        }
        .st-key-dispatch_deck_container div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background: rgba(15, 23, 42, 0.85) !important;
            border: 1.5px solid rgba(56, 189, 248, 0.35) !important;
            border-radius: 10px !important;
            color: #f8fafc !important;
            font-size: 0.82rem !important;
            font-weight: 700 !important;
            height: 38px !important;
            min-height: 38px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35) !important;
            transition: all 0.20s ease !important;
        }
        .st-key-dispatch_deck_container div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {
            border-color: #38bdf8 !important;
            background: rgba(30, 41, 59, 0.95) !important;
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.40) !important;
            transform: translateY(-1px) !important;
        }

        /* Creative Sci-Fi Glassmorphic BaseWeb Timezone Popover */
        div[data-baseweb="popover"] {
            border-radius: 14px !important;
            overflow: hidden !important;
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.85), 0 0 24px rgba(56, 189, 248, 0.25) !important;
        }
        div[data-baseweb="popover"] > div {
            background: #0b1120 !important;
            border: 1px solid rgba(56, 189, 248, 0.35) !important;
            border-radius: 14px !important;
            backdrop-filter: blur(18px) !important;
        }
        div[data-baseweb="popover"] [role="listbox"] {
            background: transparent !important;
            padding: 6px !important;
            max-height: 290px !important;
        }
        div[data-baseweb="popover"] [role="option"] {
            background: transparent !important;
            border-radius: 8px !important;
            margin: 3px 0 !important;
            padding: 9px 14px !important;
            color: #cbd5e1 !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
            transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1) !important;
            border-left: 3px solid transparent !important;
        }
        div[data-baseweb="popover"] [role="option"]:hover {
            background: linear-gradient(90deg, rgba(56, 189, 248, 0.18) 0%, rgba(14, 165, 233, 0.05) 100%) !important;
            color: #38bdf8 !important;
            border-left: 3px solid #38bdf8 !important;
            padding-left: 18px !important;
            box-shadow: inset 0 0 12px rgba(56, 189, 248, 0.12) !important;
        }
        div[data-baseweb="popover"] [role="option"][aria-selected="true"] {
            background: linear-gradient(90deg, rgba(56, 189, 248, 0.28) 0%, rgba(14, 165, 233, 0.12) 100%) !important;
            color: #ffffff !important;
            border-left: 3px solid #00f2fe !important;
            font-weight: 700 !important;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.3) !important;
        }

        /* Topbar Global Corridor Clocks */
        .dispatch-world-ticker {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 0.68rem;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            color: #94a3b8;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 9999px;
            padding: 3px 12px;
        }
        .ticker-item {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            color: #cbd5e1;
        }
        .ticker-city {
            color: #38bdf8;
            font-weight: 800;
            font-size: 0.62rem;
            letter-spacing: 0.05em;
        }
        .ticker-sep {
            color: rgba(56, 189, 248, 0.35);
        }

        /* Live Celestial Time Capsule */
        .dispatch-tz-live-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 2px 9px;
            border-radius: 9999px;
            background: rgba(30, 41, 59, 0.85);
            border: 1px solid rgba(56, 189, 248, 0.35);
            font-size: 0.66rem;
            font-weight: 700;
            color: #e2e8f0;
            letter-spacing: 0.03em;
            font-family: 'JetBrains Mono', monospace;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
        }
        .live-blink-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #10b981;
            box-shadow: 0 0 8px #10b981;
            display: inline-block;
            animation: tzBlink 1.8s infinite ease-in-out;
        }
        @keyframes tzBlink {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.35; transform: scale(0.8); }
        }

        /* Right Telemetry Capsule Container */
        .dispatch-telemetry-capsule {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 8px;
            height: 40px;
        }
        .telemetry-chip-box {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 12px;
            border-radius: 10px;
            font-size: 0.76rem;
            font-weight: 700;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.30);
            height: 38px;
            box-sizing: border-box;
        }
        .telemetry-chip-veh {
            background: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.35);
            color: #7dd3fc;
        }
        .telemetry-chip-speed {
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.35);
            color: #6ee7b7;
            font-family: 'JetBrains Mono', monospace;
        }
        .telemetry-chip-dist {
            background: rgba(168, 85, 247, 0.12);
            border: 1px solid rgba(168, 85, 247, 0.35);
            color: #d8b4fe;
            font-family: 'JetBrains Mono', monospace;
        }
        </style>
        """, unsafe_allow_html=True)

        with st.container(key="dispatch_deck_container"):
            try:
                ist_dt = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata"))
                lon_dt = datetime.datetime.now(zoneinfo.ZoneInfo("Europe/London"))
                nyc_dt = datetime.datetime.now(zoneinfo.ZoneInfo("America/New_York"))
                tyo_dt = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Tokyo"))
                ist_str = ist_dt.strftime("%I:%M %p")
                lon_str = lon_dt.strftime("%I:%M %p")
                nyc_str = nyc_dt.strftime("%I:%M %p")
                tyo_str = tyo_dt.strftime("%I:%M %p")
            except Exception:
                ist_str = nyc_str = lon_str = tyo_str = "--:--"

            st.markdown(f"""
            <div class="dispatch-deck-topbar">
                <div class="dispatch-deck-title">
                    <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #38bdf8; box-shadow: 0 0 8px #38bdf8;"></span>
                    <span>⏱️ TEMPORAL DISPATCH & CORRIDOR TIMEZONE DECK</span>
                </div>
                <div class="dispatch-world-ticker" title="Live Global Corridor Reference Clocks">
                    <span class="ticker-item"><span class="ticker-city">IST</span> {ist_str}</span>
                    <span class="ticker-sep">•</span>
                    <span class="ticker-item"><span class="ticker-city">LON</span> {lon_str}</span>
                    <span class="ticker-sep">•</span>
                    <span class="ticker-item"><span class="ticker-city">NYC</span> {nyc_str}</span>
                    <span class="ticker-sep">•</span>
                    <span class="ticker-item"><span class="ticker-city">TYO</span> {tyo_str}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_dep_pills, col_tz_select, col_dep_info = st.columns([0.33, 0.39, 0.28], vertical_alignment="top")
            with col_dep_pills:
                st.markdown("""
                <div class="dispatch-control-label">
                    <div style="display: flex; align-items: center; gap: 5px;">
                        <span>🕒</span>
                        <span>Scheduled Departure</span>
                    </div>
                    <span class="dispatch-control-chip">OFFSET</span>
                </div>
                """, unsafe_allow_html=True)
                dep_offset = st.pills(
                    "Scheduled Departure",
                    options=[0, 15, 30, 60],
                    format_func=lambda x: "⚡ Now" if x == 0 else f"+{x}m",
                    default=0,
                    key="pills_nav_departure_offset",
                    label_visibility="collapsed"
                ) or 0
            with col_tz_select:
                cur_active_tz = st.session_state.get("selected_timezone", "Asia/Kolkata")
                tz_info, tz_abbr, tz_label = resolve_timezone(cur_active_tz)
                now_in_tz = datetime.datetime.now(tz_info)
                tz_time_str = now_in_tz.strftime("%I:%M %p")
                hour_val = now_in_tz.hour
                is_day = 6 <= hour_val < 18
                celestial_icon = "☀️" if is_day else "🌙"
                period_label = "Day Corridor" if is_day else "Night Corridor"
                period_color = "#fef08a" if is_day else "#a5b4fc"

                st.markdown(f"""
                <div class="dispatch-control-label">
                    <div style="display: flex; align-items: center; gap: 5px;">
                        <span>🌐</span>
                        <span>Route Timezone</span>
                    </div>
                    <span class="dispatch-tz-live-badge" title="Live Corridor Time & Operations Cycle">
                        <span class="live-blink-dot"></span>
                        <span style="color: {period_color}; font-weight: 800;">{celestial_icon} {tz_time_str} {tz_abbr}</span>
                        <span style="opacity: 0.7; font-size: 0.60rem;">• {period_label}</span>
                    </span>
                </div>
                """, unsafe_allow_html=True)
                tz_keys = list(TIMEZONE_CATALOG.keys())
                if "selected_timezone" not in st.session_state:
                    st.session_state.selected_timezone = "Asia/Kolkata"
                cur_tz_idx = tz_keys.index(st.session_state.selected_timezone) if st.session_state.selected_timezone in tz_keys else 0
                chosen_tz = st.selectbox(
                    "Route Timezone",
                    options=tz_keys,
                    format_func=lambda k: TIMEZONE_CATALOG[k]["label"],
                    index=cur_tz_idx,
                    key="select_route_timezone",
                    label_visibility="collapsed"
                )
                st.session_state.selected_timezone = chosen_tz
            with col_dep_info:
                st.markdown("""
                <div class="dispatch-control-label" style="justify-content: flex-end;">
                    <div style="display: flex; align-items: center; gap: 5px;">
                        <span>⚡</span>
                        <span>Active Telemetry Profile</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(
                    f"""<div class="dispatch-telemetry-capsule">
                        <div class="telemetry-chip-box telemetry-chip-veh" title="Active Fleet Mode">
                            <span>{veh_emoji}</span>
                            <span>{travel_mode_str}</span>
                        </div>
                        <div class="telemetry-chip-box telemetry-chip-speed" title="Calibrated Cruising Speed">
                            <span>{veh_speed} km/h</span>
                        </div>
                        <div class="telemetry-chip-box telemetry-chip-dist" title="Display Distance Unit">
                            <span>{cur_unit_str}</span>
                        </div>
                    </div>""",
                    unsafe_allow_html=True
                )

        cur_veh_key = st.session_state.get("selected_travel_mode", "CAR")
        cur_unit = st.session_state.get("distance_unit", "km")
        active_kin_dur = active_route_item.effective_duration_minutes
        sel_drive = st.session_state.get("selected_driving_mode")
        if cur_veh_key == "CAR" and sel_drive:
            if sel_drive == "DRIVE_ECO":
                active_kin_dur *= 1.08
            elif sel_drive == "DRIVE_SAFEST":
                active_kin_dur *= 1.04
            elif sel_drive == "DRIVE_TOLL_FREE":
                active_kin_dur *= 1.15
            elif sel_drive == "DRIVE_EV":
                active_kin_dur *= 1.02

        kinematics = calculate_transit_kinematics(
            mode_key=cur_veh_key,
            distance_km=active_route_item.effective_distance_km,
            engine_duration_minutes=active_kin_dur,
            departure_offset_minutes=dep_offset,
            distance_unit=cur_unit,
            live_speed_kmh=st.session_state.get("user_speed_kmh", 0.0),
            timezone_name=st.session_state.get("selected_timezone", "Asia/Kolkata")
        )
        st.markdown(render_transit_kinematics_hud_html(kinematics), unsafe_allow_html=True)
        components.html(render_transit_kinematics_live_ticker_component(kinematics), height=0, width=0)

    # =========================================================================
    # ROUTE RECOMMENDATION & SAFETY ANALYSIS (BELOW MAP)
    # =========================================================================
    st.markdown(f"### 🧭 Route Recommendation & Safety Analysis ({active_obj.value})")

    # Pre-Route Safety & Hazard Clearance Assessment
    unsafe_routes = [r for r in ranked_routes if not r.is_eligible or not getattr(r, "is_safe", True)]
    hazard_routes = [r for r in ranked_routes if not getattr(r, "is_safe", True) or len(getattr(r, "detected_hazards", [])) > 0]
    has_eligible = len(eligible_ranked) > 0

    if not has_eligible and ranked_routes:
        eligible_ranked = ranked_routes
        st.markdown("""
        <div style='background: rgba(56, 189, 248, 0.08); border: 1.5px solid rgba(56, 189, 248, 0.3); border-radius: 10px; padding: 10px 16px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;'>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span style='font-size: 1.2rem;'>ℹ️</span>
                <span style='color: #e2e8f0; font-size: 0.84rem; font-weight: 700;'>Corridor Navigation Active • Real-world road network trajectory evaluated and verified.</span>
            </div>
            <span style='background: rgba(56, 189, 248, 0.15); color: #38bdf8; font-size: 0.70rem; font-weight: 800; padding: 3px 8px; border-radius: 6px;'>VERIFIED ROUTE</span>
        </div>
        """, unsafe_allow_html=True)
    elif unsafe_routes:
        # Single, sleek, non-redundant safety detour pill
        first_threat = unsafe_routes[0]
        hazard_road = (first_threat.route.summary_roads[0] if first_threat.route.summary_roads else "Corridor").split("-")[0].strip()
        restr_summary = first_threat.rejection_reasons[0].split("(")[0].replace("Road restriction:", "").replace("Active Hazard:", "").strip() if first_threat.rejection_reasons else "Active Hazard"

        st.markdown(f"""
        <div style='background: rgba(245, 158, 11, 0.10); border: 1px solid rgba(245, 158, 11, 0.35); border-left: 4px solid #f59e0b;
                    border-radius: 8px; padding: 8px 14px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;'>
            <div style='display: flex; align-items: center; gap: 8px; font-size: 0.82rem;'>
                <span style='font-size: 1.1rem;'>🛡️</span>
                <span style='color: #fde68a;'><b>Autonomous Safety Detour:</b> Bypassed <b>{restr_summary}</b>. Prioritizing <b>{len(eligible_ranked)} safe, open corridor(s)</b>.</span>
            </div>
            <span style='background: rgba(16, 185, 129, 0.18); color: #34d399; font-size: 0.70rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.3);'>
                ✓ SAFE DETOUR ACTIVE
            </span>
        </div>
        """, unsafe_allow_html=True)
    # Navigation Trust Audit (Compact Verified Route Information Card for Selected Route)
    if active_route_item and active_route_item.route:
        active_route_poly = getattr(active_route_item.route, "polyline", [])
        if active_route_poly and len(active_route_poly) >= 2:
            active_satellite_audit = st.session_state.satellite_auditor.audit_route_corridor(active_route_poly)
        else:
            active_satellite_audit = satellite_audit

        trust_audit_res = NavigationTrustAuditEngine.audit_route(
            route=active_route_item.route,
            active_hazards=active_hazards,
            active_restrictions=active_restrictions,
            satellite_audit=active_satellite_audit,
            hazard_data_available=True,
            corridor_buffer_m=40.0
        )
        st.markdown(render_navigation_trust_audit_card_html(trust_audit_res), unsafe_allow_html=True)
        with st.expander("🔍 View Route Verification Details & Technical Limitations", expanded=False):
            st.markdown(render_navigation_trust_audit_details_html(trust_audit_res), unsafe_allow_html=True)

        # =====================================================================
        # AI ROAD INTELLIGENCE & SATELLITE SURFACE ANALYSIS DASHBOARD
        # =====================================================================
        disp_ai_report = ai_road_report_obj
        if active_route_poly and active_route_poly != primary_route_poly and len(active_route_poly) >= 2:
            try:
                disp_ai_report = st.session_state.ai_road_controller.analyze_corridor(
                    corridor_polyline=active_route_poly,
                    route_attributes={
                        "summary_roads": getattr(active_route_item.route, "summary_roads", []),
                        "road_type": getattr(active_route_item.route, "road_type", "primary"),
                        "name": getattr(active_route_item.route, "name", "")
                    },
                    avoidance_prefs={
                        "avoid_tolls": st.session_state.get("avoid_tolls", False),
                        "avoid_highways": st.session_state.get("avoid_highways", False),
                        "avoid_ferries": st.session_state.get("avoid_ferries", False)
                    }
                )
            except Exception:
                disp_ai_report = ai_road_report_obj

        if disp_ai_report is not None:
            with st.expander("🛰️ AI Road Intelligence & Satellite Surface Analysis", expanded=False):
                # Satellite Source & Provenance Bar
                st.markdown("""
                <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;'>
                    <div style='font-size: 0.82rem; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.05em;'>
                        🛰️ Satellite Imagery Provider & Calibrated Computer Vision
                    </div>
                    <span style='font-size: 0.70rem; background: rgba(56,189,248,0.15); border: 1px solid rgba(56,189,248,0.3); color: #38bdf8; padding: 2px 6px; border-radius: 4px;'>
                        ODbL / CC BY 4.0 Compliant
                    </span>
                </div>
                """, unsafe_allow_html=True)

                col_sat1, col_sat2 = st.columns([1.2, 1.0])
                with col_sat1:
                    prov_keys = list(AVAILABLE_SATELLITE_PROVIDERS.keys())
                    prov_names = [AVAILABLE_SATELLITE_PROVIDERS[k].name for k in prov_keys]
                    curr_p_idx = prov_keys.index(st.session_state.get("ai_sat_provider", "esri_world_imagery")) if st.session_state.get("ai_sat_provider") in prov_keys else 0
                    sel_prov_name = st.selectbox(
                        "Satellite Imagery Source",
                        options=prov_names,
                        index=curr_p_idx,
                        key="sel_sat_imagery_provider",
                        help="Legitimate satellite & aerial imagery provider with documented licensing, attribution, and spatial calibration."
                    )
                    sel_prov_key = prov_keys[prov_names.index(sel_prov_name)]
                    if sel_prov_key != st.session_state.get("ai_sat_provider"):
                        st.session_state.ai_sat_provider = sel_prov_key
                        st.session_state.ai_road_controller.set_provider(sel_prov_key)
                        st.rerun()

                with col_sat2:
                    p_meta = AVAILABLE_SATELLITE_PROVIDERS[st.session_state.get("ai_sat_provider", "esri_world_imagery")]
                    st.markdown(f"""
                    <div style='background: rgba(15,23,42,0.7); border: 1px solid rgba(56,189,248,0.25); border-radius: 8px; padding: 8px 12px; font-size: 0.75rem; color: #94a3b8;'>
                        <div><b>Capture Freshness:</b> <span style='color: #38bdf8;'>{p_meta.freshness_note}</span></div>
                        <div><b>Attribution:</b> {p_meta.attribution}</div>
                        <div><b>Licensing:</b> <span style='color: #a78bfa;'>{p_meta.license}</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                # Avoidance Preferences Cross-Validation Advisory
                if disp_ai_report.avoidance_compliance.get("warnings"):
                    for w in disp_ai_report.avoidance_compliance["warnings"]:
                        st.markdown(f"""
                        <div style='background: rgba(245,158,11,0.12); border-left: 3px solid #f59e0b; padding: 8px 12px; border-radius: 6px; font-size: 0.78rem; color: #fbbf24; margin: 6px 0;'>
                            ⚠️ <b>Avoidance Limitation:</b> {w}
                        </div>
                        """, unsafe_allow_html=True)

                # High-Tech Telemetry HUD
                st.markdown(render_ai_road_intelligence_hud_html(disp_ai_report), unsafe_allow_html=True)

                # Detected Features Structured Ledger
                st.markdown("<div style='font-size: 0.82rem; font-weight: 700; color: #f1f5f9; margin-top: 12px; margin-bottom: 6px;'>📍 Georeferenced Detections & Corroboration Audit</div>", unsafe_allow_html=True)
                for feat in disp_ai_report.detected_features:
                    is_corrob = "Corroborated" in feat.verification_status
                    is_unver = "unverified" in feat.verification_status
                    status_color = "#10b981" if is_corrob else ("#38bdf8" if is_unver else "#f59e0b")
                    badge_bg = "rgba(16,185,129,0.15)" if is_corrob else ("rgba(56,189,248,0.15)" if is_unver else "rgba(245,158,11,0.15)")
                    
                    st.markdown(f"""
                    <div style='background: rgba(30,41,59,0.5); border: 1px solid rgba(148,163,184,0.15); border-radius: 8px; padding: 8px 12px; margin-bottom: 6px; font-size: 0.78rem;'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <span style='font-weight: 700; color: #e2e8f0;'>{feat.feature_id.upper()} • {feat.category.replace('_', ' ').title()}</span>
                            <span style='background: {badge_bg}; color: {status_color}; font-weight: 700; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem;'>{feat.verification_status}</span>
                        </div>
                        <div style='color: #94a3b8; margin-top: 3px;'>
                            📍 Coordinate: <code>{feat.coordinates[0]:.5f}, {feat.coordinates[1]:.5f}</code> | Confidence: <b>{feat.confidence*100:.1f}%</b> | Source: <em>{feat.imagery_source}</em>
                        </div>
                        <div style='color: #cbd5e1; margin-top: 3px;'>
                            {feat.details}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # =========================================================================
    # MULTI-OBJECTIVE ROUTING SEGMENTED SELECTOR (MAIN PAGE & MOBILE ADAPTIVE)
    # =========================================================================
    st.markdown("""
    <div style='display: flex; align-items: center; justify-content: space-between; margin-top: 14px; margin-bottom: 6px;'>
        <div style='font-size: 0.82rem; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 6px;'>
            <span>🎯</span> ROUTING OBJECTIVE & CANDIDATE RANKING:
        </div>
        <div style='font-size: 0.70rem; color: #94a3b8;'>
            Select Priority • Instant Map Synchronization
        </div>
    </div>
    """, unsafe_allow_html=True)

    obj_cols = st.columns(5)
    obj_buttons = [
        ("ALL", "🌐 All Routes", "Displays all candidate road corridors simultaneously", "ALL", None),
        ("FASTEST", "⚡ Fastest", "Minimizes travel duration based on speed limits", "FASTEST", OptimizationObjective.FASTEST),
        ("SHORTEST", "📏 Shortest", "Minimizes physical ground road distance", "SHORTEST", OptimizationObjective.SHORTEST),
        ("BALANCED", "⚖️ Balanced", "Optimal 50/50 balance between time and distance", "BALANCED", OptimizationObjective.BALANCED),
        ("ACCESSIBLE", "♿ Accessible", "Prioritizes step-free paths and accessible corridors", "ACCESSIBLE", OptimizationObjective.ACCESSIBLE),
    ]

    for o_idx, (o_key, o_label, o_help, o_focus, o_enum) in enumerate(obj_buttons):
        with obj_cols[o_idx]:
            if o_key == "ALL":
                is_active_obj = (st.session_state.get("focused_route_id") == "ALL")
            else:
                is_active_obj = (st.session_state.get("focused_route_id") == o_focus) or (
                    st.session_state.get("active_objective") == o_enum and st.session_state.get("focused_route_id") != "ALL"
                )
            btn_t = "primary" if is_active_obj else "secondary"
            if st.button(o_label, key=f"btn_main_obj_{o_key}", use_container_width=True, type=btn_t, help=o_help):
                if o_enum is not None:
                    st.session_state.active_objective = o_enum
                st.session_state.focused_route_id = o_focus
                if o_focus == "ALL":
                    st.session_state.selected_route_id = None
                st.session_state.auto_fit_bounds = True
                st.session_state.scroll_to_app_map = True
                st.rerun()

    # Informative disclaimer for ACCESSIBLE routing limitation
    if active_obj == OptimizationObjective.ACCESSIBLE or st.session_state.get("focused_route_id") == "ACCESSIBLE":
        if active_route_item and not (getattr(active_route_item.route, "accessibility_verified", False) or getattr(active_route_item, "accessibility_verified", False)):
            st.markdown("""
            <div style='background: rgba(245, 158, 11, 0.10); border: 1.5px solid rgba(245, 158, 11, 0.35); border-radius: 8px; padding: 8px 14px; margin-top: 8px; margin-bottom: 8px;'>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <span style='font-size: 1.1rem;'>♿</span>
                    <b style='color: #fbbf24; font-size: 0.82rem;'>Provider Accessibility Data Limitation</b>
                </div>
                <div style='color: #cbd5e1; font-size: 0.74rem; margin-top: 3px; line-height: 1.4;'>
                    Public road network routing (OSRM) does not publish certified curb-cut, ramp slope, or tactile paving attributes. Route selected prioritizes paved motorable roadways, but step-free pedestrian access is unverified on general road networks.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Display Route Recommendation Cards:
    # Always keep ALL candidate routes visible side-by-side and interactive
    displayed_routes = ranked_routes
    num_routes = len(displayed_routes)
    primary_ref = next((r for r in ranked_routes if r.rank == 1), ranked_routes[0]) if ranked_routes else None

    # Compute fastest and shortest candidates from the actual candidate set
    fastest_candidate = min(ranked_routes, key=lambda r: r.effective_duration_minutes) if ranked_routes else None
    shortest_candidate = min(ranked_routes, key=lambda r: r.effective_distance_km) if ranked_routes else None

    if num_routes > 0:
        card_cols = st.columns(min(num_routes, 3))
        for idx, r_item in enumerate(displayed_routes):
            with card_cols[idx % min(num_routes, 3)]:
                is_active = (cur_focus == r_item.route.route_id)
                target_focus = r_item.route.route_id
                short_name = r_item.route.name.split("(")[0].strip()

                is_safe_route = getattr(r_item, "is_safe", True) and r_item.is_eligible and len(getattr(r_item, "detected_hazards", [])) == 0
                if is_safe_route:
                    safety_badge = "<span style='background: rgba(16, 185, 129, 0.2); color: #34d399; font-size: 0.70rem; font-weight: 700; padding: 2px 8px; border-radius: 4px;'>🛡️ NO REPORTED HAZARDS</span>"
                    card_border = "#10b981" if is_active else "#38bdf8"
                    if len(ranked_routes) == 1:
                        rank_badge = "⭐ SOLE ROUTE"
                    elif r_item == fastest_candidate and r_item == shortest_candidate:
                        rank_badge = "⭐ FASTEST & SHORTEST"
                    elif r_item.rank == 1:
                        rank_badge = "⭐ BEST MATCH"
                    else:
                        rank_badge = f"Alternative {r_item.rank}"
                elif not getattr(r_item, "is_safe", True):
                    safety_badge = "<span style='background: rgba(239, 68, 68, 0.25); color: #f87171; font-size: 0.70rem; font-weight: 700; padding: 2px 8px; border-radius: 4px;'>⚠️ BLOCKED EN ROUTE</span>"
                    card_border = "#ef4444"
                    rank_badge = "RESTRICTED (HAZARD)"
                else:
                    safety_badge = "<span style='background: rgba(245, 158, 11, 0.25); color: #fbbf24; font-size: 0.70rem; font-weight: 700; padding: 2px 8px; border-radius: 4px;'>🚧 ROAD CLOSURE</span>"
                    card_border = "#ef4444"
                    rank_badge = "RESTRICTED (CLOSURE)"

                # Map Presentation Status Indicator & Visual Focus
                if is_active:
                    map_status_badge = "<span style='background: rgba(14, 165, 233, 0.35); color: #38bdf8; font-size: 0.70rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; border: 1.5px solid #38bdf8; box-shadow: 0 0 12px rgba(56, 189, 248, 0.5);'>🎯 ACTIVE ON MAP</span>"
                    card_opacity = "1.0"
                    card_extra_border = f"border-left: 5px solid {card_border}; border-top: 2px solid #38bdf8; border-right: 2px solid #38bdf8; border-bottom: 2px solid #38bdf8; box-shadow: 0 0 25px rgba(56, 189, 248, 0.45); background: rgba(14, 165, 233, 0.12);"
                else:
                    map_status_badge = "<span style='background: rgba(100, 116, 139, 0.20); color: #cbd5e1; font-size: 0.70rem; font-weight: 700; padding: 2px 6px; border-radius: 4px;'>CANDIDATE</span>"
                    card_opacity = "0.90"
                    card_extra_border = f"border-left: 5px solid {card_border}; border-top: 1px solid rgba(255,255,255,0.08); border-right: 1px solid rgba(255,255,255,0.08); border-bottom: 1px solid rgba(255,255,255,0.08);"

                cur_unit = st.session_state.get("distance_unit", "km")
                dist_display = format_distance(r_item.effective_distance_km, cur_unit)

                # Calculate accurate delta differences vs Primary Route 1
                if primary_ref and r_item.rank > 1:
                    delta_dist = r_item.effective_distance_km - primary_ref.effective_distance_km
                    delta_dur = r_item.effective_duration_minutes - primary_ref.effective_duration_minutes
                    sign_dist = "+" if delta_dist >= 0 else "-"
                    sign_dur = "+" if delta_dur >= 0 else "-"
                    dur_color = "#34d399" if delta_dur < -0.05 else ("#94a3b8" if abs(delta_dur) <= 0.2 else "#fbbf24")
                    dist_color = "#34d399" if delta_dist < -0.05 else ("#94a3b8" if abs(delta_dist) <= 0.1 else "#38bdf8")
                    diff_pill = f"<span style='background: rgba(255, 255, 255, 0.08); font-size: 0.74rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.12);'><b style='color: {dur_color};'>⏱️ {sign_dur}{abs(delta_dur):.1f} min</b> &nbsp;|&nbsp; <b style='color: {dist_color};'>📏 {sign_dist}{format_distance(abs(delta_dist), cur_unit)}</b></span>"
                elif len(ranked_routes) == 1:
                    diff_pill = "<span style='background: rgba(16, 185, 129, 0.18); color: #34d399; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px;'>✓ SOLE ROUTE</span>"
                else:
                    diff_pill = "<span style='background: rgba(16, 185, 129, 0.22); color: #34d399; font-size: 0.72rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.35);'>⭐ FASTEST BASELINE</span>"

                if is_safe_route:
                    if len(ranked_routes) == 1:
                        creative_takeaway = "💡 <b>Single Direct Route:</b> This is the only distinct physical road corridor connecting origin and destination."
                    elif r_item.rank == 1:
                        creative_takeaway = "💡 <b>Recommended Choice:</b> Optimal balance of transit speed and clear, uninterrupted pavement."
                    else:
                        creative_takeaway = "💡 <b>Alternative Bypass:</b> Secondary viable option with open traffic flow."
                else:
                    closure_name = r_item.rejection_reasons[0].split("(")[0].replace("Road restriction:", "").replace("Active Hazard:", "").strip() if r_item.rejection_reasons else "Road closure"
                    creative_takeaway = f"⛔ <b>Impassable:</b> Confirmed blockage at {closure_name}."

                feature_chips = []
                if is_safe_route:
                    feature_chips.append("<span style='background: rgba(56, 189, 248, 0.12); color: #38bdf8; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px;'>⚡ Clear Corridor</span>")
                    if r_item == fastest_candidate:
                        feature_chips.append("<span style='background: rgba(56, 189, 248, 0.22); color: #7dd3fc; font-size: 0.72rem; font-weight: 700; padding: 2px 6px; border-radius: 4px;'>⏱️ Fastest</span>")
                    if r_item == shortest_candidate:
                        feature_chips.append("<span style='background: rgba(168, 85, 247, 0.22); color: #c084fc; font-size: 0.72rem; font-weight: 700; padding: 2px 6px; border-radius: 4px;'>📏 Shortest</span>")
                    if r_item.route.is_accessible:
                        if getattr(r_item.route, "accessibility_verified", False) or getattr(r_item, "accessibility_verified", False):
                            feature_chips.append("<span style='background: rgba(52, 211, 153, 0.15); color: #34d399; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px;'>♿ Step-Free</span>")
                        else:
                            feature_chips.append("<span style='background: rgba(245, 158, 11, 0.15); color: #fbbf24; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px;'>♿ Paved Road</span>")
                else:
                    feature_chips.append("<span style='background: rgba(239, 68, 68, 0.15); color: #f87171; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px;'>⚠️ Impassable</span>")
                    feature_chips.append("<span style='background: rgba(245, 158, 11, 0.15); color: #fbbf24; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px;'>🔄 Detour Active</span>")

                chips_html = " ".join(feature_chips)

                # Identify distinct roads unique to this alternative route
                if primary_ref and r_item.rank > 1 and primary_ref.route.summary_roads:
                    distinct_roads = [rd for rd in r_item.route.summary_roads if rd and rd not in primary_ref.route.summary_roads]
                    if distinct_roads:
                        via_roads_html = f"<b style='color: #38bdf8;'>{', '.join(distinct_roads[:2])}</b> <span style='color: #64748b;'>(via {', '.join(r_item.route.summary_roads[:2])})</span>"
                    else:
                        via_roads_html = f"<span style='color: #94a3b8;'>{', '.join(r_item.route.summary_roads[:2]) if r_item.route.summary_roads else 'Direct Corridor'}</span>"
                else:
                    via_roads_html = f"<span style='color: #94a3b8;'>{', '.join(r_item.route.summary_roads[:2]) if r_item.route.summary_roads else 'Direct Corridor'}</span>"

                mode_str = str(getattr(r_item.route.mode, "value", r_item.route.mode)).upper()
                if "TRACTOR" in mode_str:
                    vehicle_badge = "🚜 Tractor Mode"
                elif "MOTORCYCLE" in mode_str or "BIKE" in mode_str:
                    vehicle_badge = "🏍️ Bike / Scooter"
                elif "TRUCK" in mode_str:
                    vehicle_badge = "🚚 Heavy Truck"
                elif "WALK" in mode_str:
                    vehicle_badge = "🚶‍♂️ Small Boy (Swiggy/Zomato)"
                elif "BICYCLE" in mode_str:
                    vehicle_badge = "🚴 Bicycle"
                else:
                    vehicle_badge = "🚗 Driving Car"

                # Render 100% Clickable & Touch-Selectable Route Card
                route_card_html = f"""<a href="#application-map-viewport" class="touchable-route-link" data-target-focus="{target_focus}" title="{r_item.route.name}">
    <div class="touchable-route-card" data-path-idx="{idx + 1}" data-route-id="{r_item.route.route_id}" data-target-focus="{target_focus}"
    style='background: rgba(10, 20, 38, 0.75); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
    {card_extra_border}
    border-radius: 10px; padding: 14px 16px; margin-bottom: 6px; box-shadow: 0 4px 18px rgba(0,0,0,0.35);
    opacity: {card_opacity}; cursor: pointer;'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
    <b style='color: #f1f5f9; font-size: 0.96rem;'>{r_item.route.name}</b>
    <div style='display: flex; align-items: center; gap: 8px;'>
    {map_status_badge}
    <span style='font-size: 0.70rem; color: {card_border}; font-weight: 800; text-transform: uppercase;'>{rank_badge}</span>
    </div>
    </div>
    <div style='display: flex; align-items: center; justify-content: space-between; margin-top: 6px; margin-bottom: 8px;'>
    {safety_badge}
    <div>{chips_html}</div>
    </div>
    <div style='display: flex; align-items: center; justify-content: space-between; font-size: 0.90rem; color: #cbd5e1; margin-bottom: 8px; background: rgba(255,255,255,0.03); padding: 6px 10px; border-radius: 6px;'>
    <div style='display: flex; gap: 14px;'>
    <span>⏱️ <b>{r_item.effective_duration_minutes:.1f} mins</b></span>
    <span>📏 <b>{dist_display}</b></span>
    </div>
    <div>{diff_pill}</div>
    </div>
    <div style='font-size: 0.80rem; color: #93c5fd; margin-bottom: 8px; line-height: 1.4;'>
    {creative_takeaway}
    </div>
    <div style='font-size: 0.72rem; color: #64748b; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px;'>
    📍 Via: {via_roads_html}
    </div>
    </div>
    </a>"""
                st.markdown("\n".join(line.strip() for line in route_card_html.splitlines() if line.strip()), unsafe_allow_html=True)

                # Dedicated Native Select / Highlight Control
                if is_active:
                    if st.button("🎯 Active on Map • Show All Routes", key=f"btn_route_sel_{r_item.route.route_id}_{idx}", type="primary", use_container_width=True):
                        st.session_state.focused_route_id = "ALL"
                        st.session_state.selected_route_id = None
                        st.session_state.auto_fit_bounds = True
                        st.session_state.scroll_to_app_map = True
                        st.rerun()
                else:
                    if st.button("🗺️ Select Route & View on Map", key=f"btn_route_sel_{r_item.route.route_id}_{idx}", type="secondary", use_container_width=True):
                        st.session_state.focused_route_id = r_item.route.route_id
                        st.session_state.selected_route_id = r_item.route.route_id
                        st.session_state.selected_route_object = r_item.route
                        st.session_state.auto_fit_bounds = True
                        st.session_state.scroll_to_app_map = True
                        st.rerun()

        # Invisible bridge component: binds clicks on the cards directly to Streamlit route selection
        import streamlit.components.v1 as components
        components.html("""
        <script>
        (function() {
            function bindCards() {
                try {
                    const pDoc = window.parent.document;
                    if (!pDoc) return;
                    const cards = pDoc.querySelectorAll('.touchable-route-card');
                    cards.forEach(card => {
                        if (card.dataset.touchBound === "true") return;
                        card.dataset.touchBound = "true";
                        card.style.cursor = "pointer";
                        card.addEventListener('click', function(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            // Directly click the button in the same column
                            const col = card.closest('[data-testid="column"]');
                            const btn = col ? col.querySelector('button') : null;
                            if (btn) {
                                btn.click();
                            } else {
                                const targetFocus = card.getAttribute('data-target-focus');
                                if (targetFocus) {
                                    const url = new URL(window.parent.location.href);
                                    url.searchParams.set("focus_route", targetFocus);
                                    window.parent.location.replace(url.toString());
                                }
                            }
                        });
                    });
                } catch(err) {
                    console.error("Card click binding error:", err);
                }
            }
            bindCards();
            setTimeout(bindCards, 200);
            setTimeout(bindCards, 500);
            setTimeout(bindCards, 1000);
            try {
                const observer = new MutationObserver(bindCards);
                observer.observe(window.parent.document.body, { childList: true, subtree: true });
            } catch(e) {}
        })();
        </script>
        """, height=0, width=0)




    # =========================================================================
    # DRIVING TRAVEL MODES COMPARISON & AUTONOMOUS BEST-WAY PICKER
    # =========================================================================
    st.markdown("---")

    # Calculate base distance and duration
    base_dist = active_route_item.effective_distance_km if ('active_route_item' in locals() and active_route_item) else 8.5
    base_dur = active_route_item.effective_duration_minutes if ('active_route_item' in locals() and active_route_item) else 15.0
    has_hazards = len(active_hazards) > 0 if 'active_hazards' in locals() else False

    driving_comparison = compare_driving_travel_modes(
        distance_km=base_dist,
        base_duration_mins=base_dur,
        origin_name=origin_display if 'origin_display' in locals() else "Origin",
        dest_name=dest_display if 'dest_display' in locals() else "Destination",
        has_hazards_on_fastest=has_hazards,
        ranked_routes=ranked_routes if 'ranked_routes' in locals() else None,
        active_hazards=active_hazards if 'active_hazards' in locals() else None,
        active_restrictions=active_restrictions if 'active_restrictions' in locals() else None
    )

    best_mode_id = driving_comparison["best_mode_id"]
    best_reason = driving_comparison["best_reason"]

    # Automotive Cockpit Header Banner
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.92) 100%);
                border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 14px; padding: 14px 18px; margin-bottom: 16px;
                display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.5);'>
        <div style='display: flex; align-items: center; gap: 12px;'>
            <div style='width: 44px; height: 44px; border-radius: 10px; background: linear-gradient(135deg, #0284c7, #0369a1); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 0 16px rgba(56, 189, 248, 0.5);'>
                🏎️
            </div>
            <div>
                <div style='font-size: 1.05rem; font-weight: 900; color: #f8fafc; letter-spacing: 0.03em; text-transform: uppercase;'>
                    AUTOMOTIVE COCKPIT DRIVE SELECTOR & AI STRATEGY
                </div>
                <div style='font-size: 0.74rem; color: #94a3b8; margin-top: 2px;'>
                    5 calibrated powertrain & routing profiles • Dynamic speed, energy, and safety trade-off telemetry
                </div>
            </div>
        </div>
        <div style='background: rgba(16, 185, 129, 0.15); border: 1.5px solid rgba(16, 185, 129, 0.45); border-radius: 8px; padding: 8px 14px; display: flex; align-items: center; gap: 10px; box-shadow: 0 0 16px rgba(16, 185, 129, 0.25);'>
            <span style='display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #34d399; box-shadow: 0 0 8px #34d399;'></span>
            <div>
                <div style='font-size: 0.66rem; font-weight: 800; color: #34d399; text-transform: uppercase; letter-spacing: 0.05em;'>
                    ⭐ AI COPILOT VERDICT
                </div>
                <div style='font-size: 0.76rem; color: #f1f5f9; font-weight: 700; margin-top: 1px;'>
                    {best_reason}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "selected_driving_mode" not in st.session_state:
        st.session_state.selected_driving_mode = best_mode_id

    st.markdown("""
    <style>
    /* Equal Height Alignment for Driving Modes Cockpit Deck */
    .st-key-driving_modes_cockpit_deck div[data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
        gap: 10px !important;
    }
    .st-key-driving_modes_cockpit_deck div[data-testid="stColumn"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        min-width: 0 !important;
    }
    .st-key-driving_modes_cockpit_deck div[data-testid="stButton"] {
        margin-top: 8px !important;
        width: 100% !important;
    }
    .st-key-driving_modes_cockpit_deck div[data-testid="stButton"] > button {
        height: 40px !important;
        min-height: 40px !important;
        border-radius: 10px !important;
        font-size: 0.78rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.02em !important;
        transition: all 0.20s ease !important;
        width: 100% !important;
    }
    .st-key-driving_modes_cockpit_deck div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.35) 0%, rgba(5, 150, 105, 0.65) 100%) !important;
        border: 1.5px solid #10b981 !important;
        color: #ffffff !important;
        box-shadow: 0 0 14px rgba(16, 185, 129, 0.40) !important;
    }
    .st-key-driving_modes_cockpit_deck div[data-testid="stButton"] > button[kind="secondary"] {
        background: rgba(15, 23, 42, 0.78) !important;
        border: 1px solid rgba(56, 189, 248, 0.22) !important;
        color: #94a3b8 !important;
    }
    .st-key-driving_modes_cockpit_deck div[data-testid="stButton"] > button[kind="secondary"]:hover {
        border-color: #38bdf8 !important;
        color: #f8fafc !important;
        background: rgba(56, 189, 248, 0.12) !important;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.25) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container(key="driving_modes_cockpit_deck"):
        dm_cols = st.columns(5)
        for idx, mode in enumerate(driving_comparison["modes"]):
            is_active = (st.session_state.selected_driving_mode == mode["mode_id"])
            is_best = mode["is_best"]

            with dm_cols[idx]:
                card_html = render_driving_mode_cockpit_card_html(mode, is_active=is_active, is_best=is_best)
                st.markdown(card_html, unsafe_allow_html=True)
                btn_label = "✓ Engaged" if is_active else ("⚡ Engage Best" if is_best else "Engage Mode")
                if st.button(
                    btn_label,
                    key=f"btn_mode_{mode['mode_id']}",
                    use_container_width=True,
                    type="primary" if (is_best or is_active) else "secondary"
                ):
                    st.session_state.selected_driving_mode = mode["mode_id"]
                    # Synchronize route selection and interactive map highlighting
                    if mode.get("route_id"):
                        st.session_state.focused_route_id = mode["route_id"]
                        st.session_state.selected_route_id = mode["route_id"]
                        matching_r = next((r.route for r in ranked_routes if r.route.route_id == mode["route_id"]), None)
                        if matching_r:
                            st.session_state.selected_route_object = matching_r
                        st.session_state.auto_fit_bounds = True
                        st.session_state.scroll_to_app_map = True
                    st.toast(f"Engaged {mode['title']} on route {mode.get('route_id', 'corridor')}!", icon=mode["icon"])
                    st.rerun()

    # Render Live Interactive Cockpit Mode Functionality HUD
    active_mode_obj = next(
        (m for m in driving_comparison["modes"] if m["mode_id"] == st.session_state.selected_driving_mode),
        driving_comparison["modes"][0]
    )
    st.markdown(
        render_cockpit_mode_functionality_hud(
            mode_id=st.session_state.selected_driving_mode,
            orig_coords=coords_orig if 'coords_orig' in locals() else None,
            dest_coords=coords_dest if 'coords_dest' in locals() else None,
            orig_name=origin_display if 'origin_display' in locals() else "Origin",
            dest_name=dest_display if 'dest_display' in locals() else "Destination",
            distance_km=active_mode_obj.get("distance_km", base_dist),
            mode_info=active_mode_obj
        ),
        unsafe_allow_html=True
    )

    # Data-Quality Audit: View calculation details & statistical provenance
    with st.expander("🔬 View Calculation Details & Statistical Provenance", expanded=False):
        audit_cols = st.columns(len(driving_comparison["modes"]))
        for col_idx, m_item in enumerate(driving_comparison["modes"]):
            with audit_cols[col_idx]:
                st.markdown(f"<b>{m_item['title']}</b>", unsafe_allow_html=True)

with tab_guide:
    st.markdown("### 🚗 Virtual Guide & Interactive 3D Journey Simulation")
    if "active_route_item" in locals() and active_route_item:
        clean_route_name = active_route_item.route.name.split("(")[0].strip()
        if len(active_hazards) > 0 or len(active_restrictions) > 0:
            hazard_detour_phrase = f"safely evading {len(active_hazards) + len(active_restrictions)} verified corridor obstacle(s)"
        else:
            hazard_detour_phrase = "corridor clear of reported road closures or hazards on current satellite pass"

        # Maneuver Steps List
        steps = getattr(active_route_item.route, "steps", [])
        if not steps:
            roads_list = active_route_item.route.summary_roads or ["Regional Main Road"]
            steps = [
                {"step_num": 1, "icon": "🟢", "instruction": f"Head out on {roads_list[0]}", "road": roads_list[0], "distance_m": active_route_item.route.distance_meters / max(len(roads_list), 1)},
                {"step_num": 2, "icon": "🏁", "instruction": "Arrive at destination safe terminal", "road": roads_list[-1], "distance_m": 0}
            ]

        # Route coordinates & distances
        route_coords = getattr(active_route_item.route, "polyline", []) or getattr(active_route_item.route, "coordinates", [])
        route_total_dist_km = float(getattr(active_route_item.route, "distance_km", 0.0) or (getattr(active_route_item.route, "distance_meters", 0.0) / 1000.0) or 1.0)

        origin_display = st.session_state.get("user_live_label", "Starting Point")
        dest_display = st.session_state.get("selected_dest_label", "Destination")

        # Dynamically extract milestones for ANY global coordinates
        journey_milestones = extract_journey_game_milestones(
            origin_label=origin_display,
            dest_label=dest_display,
            polyline=route_coords,
            steps=steps,
            total_distance_km=route_total_dist_km
        )

        # Manage step state keyed to active route
        route_game_key = f"game_step_{active_route_item.route.route_id}"
        if route_game_key not in st.session_state:
            st.session_state[route_game_key] = 0

        cur_game_idx = st.session_state[route_game_key]
        cur_game_idx = max(0, min(cur_game_idx, len(journey_milestones) - 1))

        # Automatic Satellite Motion & Milestone Crossing Detection
        user_current_pt = coords_orig if coords_orig else detected_coords
        auto_step_idx, newly_crossed_m, detected_place_summary = detect_crossed_milestones(
            user_coords=user_current_pt,
            current_step=cur_game_idx,
            milestones=journey_milestones,
            polyline=route_coords
        )

        # Automatically advance checkpoint if user crossed any stop during travel!
        if auto_step_idx > cur_game_idx:
            cur_game_idx = auto_step_idx
            st.session_state[route_game_key] = auto_step_idx
            if newly_crossed_m:
                st.toast(f"🏃 Satellite GPS: Crossed {newly_crossed_m.label}! Character hopped forward.", icon="🎯")

        st.session_state[route_game_key] = cur_game_idx

        friendly_turns = generate_friendly_virtual_guide_turns(
            steps=steps,
            origin=origin_display,
            destination=dest_display,
            travel_mode=travel_mode_str
        )

        # =========================================================================
        # SECTION 1 — VIRTUAL RUNNER & ROUTE PROCESS BANNER
        # =========================================================================
        st.markdown("#### 🏃 Section 1: Virtual Runner & Route Process Banner")
        game_avatar = st.session_state.get("selected_travel_mode", "WALK").lower()
        # Initial state must always be stationary until user explicitly clicks Move in Parallel
        is_user_moving = bool(st.session_state.get("virtual_guide_moving", False))
        guide_speed_kmh = float(st.session_state.get("user_speed_kmh", 0.0)) if is_user_moving else 0.0

        game_html = build_game_journey_html(
            milestones=journey_milestones,
            current_step=cur_game_idx,
            traveler_avatar=game_avatar,
            auto_voice=False,
            detected_place=detected_place_summary,
            is_moving=is_user_moving,
            user_speed_kmh=guide_speed_kmh,
            polyline=route_coords,
            auto_drive=False
        )
        components.html(game_html, height=340)

        # =========================================================================
        # SECTION 2 — VIRTUAL VEHICLE COMPANION (EXPANDED BY DEFAULT)
        # =========================================================================
        st.markdown("#### 🚗 Section 2: Virtual Vehicle Companion")
        companion_hud = build_virtual_companion_hud_html(
            session_id=f"SESS_{route_game_key}",
            origin_name=origin_display,
            dest_name=dest_display,
            travel_mode=travel_mode_str.lower(),
            initial_state="MOVING" if is_user_moving else "ROUTE_READY",
            polyline=route_coords,
            steps=friendly_turns,
            current_speed_kmh=guide_speed_kmh,
            total_distance_m=route_total_dist_km * 1000.0,
            current_step_idx=cur_game_idx
        )
        components.html(companion_hud, height=315)

        # =========================================================================
        # SECTION 3 — VIRTUAL GUIDE & REALISTIC 3D SCENE
        # =========================================================================
        st.markdown("#### 🧑‍✈️ Section 3: Virtual Human Guide & Realistic 3D Scenery")
        always_visible_guide_tab_html = build_always_visible_virtual_guide_html(
            origin_name=origin_display,
            dest_name=dest_display,
            polyline=route_coords,
            steps=friendly_turns if friendly_turns else steps,
            travel_mode=travel_mode_str.lower(),
            total_distance_m=route_total_dist_km * 1000.0,
            current_speed_kmh=guide_speed_kmh,
            current_step_idx=cur_game_idx,
            is_live_gps=bool(guide_speed_kmh > 0 and not st.session_state.get("is_simulation_mode", True)),
            session_id=f"GUIDE_TAB_{route_game_key}"
        )
        components.html(always_visible_guide_tab_html, height=460)

        # =========================================================================
        # SECTION 4 — ADDITIONAL ROUTE DETAILS & MANEUVERS
        # =========================================================================
        with st.expander("📖 Section 4: Additional Route Details, Landmark Storybook & Maneuvers", expanded=False):
            turns_guide_html = build_virtual_guide_turns_html(
                friendly_turns=friendly_turns,
                origin=origin_display,
                destination=dest_display,
                travel_mode=travel_mode_str
            )
            components.html(turns_guide_html, height=620)

    else:
        # Standby Virtual Human Guide when no route is active yet
        origin_standby_disp = st.session_state.get("user_live_label", "Starting Point")
        dest_standby_disp = st.session_state.get("selected_dest_label", "Destination")
        nav_mode_str = st.session_state.get("selected_travel_mode", "CAR").lower()
        st.markdown("#### 🏃 Section 1: Virtual Runner & Route Process Banner")
        st.info("🧭 Select an origin and destination in the Navigation tab to initialize your Virtual Runner & Route Process Banner.")
        st.markdown("#### 🚗 Section 2: Virtual Vehicle Companion")
        st.info("🚗 Companion HUD will activate when a route is configured.")
        st.markdown("#### 🧑‍✈️ Section 3: Virtual Guide Scene")
        always_visible_standby_html = build_always_visible_virtual_guide_html(
            origin_name=origin_standby_disp,
            dest_name=dest_standby_disp,
            polyline=[],
            steps=[],
            travel_mode=nav_mode_str,
            total_distance_m=0.0,
            current_speed_kmh=0.0,
            current_step_idx=0,
            is_live_gps=False,
            session_id="STANDBY_GUIDE_TAB"
        )
        components.html(always_visible_standby_html, height=460)

        st.info("🧭 Select an origin and destination in the Navigation tab to synchronize live corridor turns and checkpoints with your Virtual Guide.")
        if st.button("🧭 Go to Navigation Tab & Select Route", key="btn_guide_redirect_nav", type="primary"):
            st.session_state.target_tab = "nav"
            st.session_state.scroll_to_app_map = True
            st.rerun()

with tab_facilities:
    st.markdown("### 🏥 Facility Categories Explorer & Emergency Radar")

    # FACILITY CATEGORIES EXPLORER & ALL ROUTES MAPPER
    # (Linked directly to sidebar selection, showing all facilities & candidate routes)
    # =========================================================================
    st.markdown("---")
    cur_cat_name = st.session_state.get("selected_sidebar_category", "🌐 All Facilities")

    user_current_lat = coords_orig[0] if coords_orig else detected_coords[0]
    user_current_lon = coords_orig[1] if coords_orig else detected_coords[1]
    nat_emergency = get_national_emergency_contacts(user_current_lat, user_current_lon)

    # Quick Category Switcher Tabs on Main Page
    cat_quick_options = [
        "🌐 All Facilities",
        "🏥 Hospitals",
        "⛺ Shelters",
        "👮 Police/Rescue",
        "⛽ Fuel/Charging",
        "🚨 Emergency Radar",
        "🍽️ Restaurants",
        "🏨 Hotels",
        "🏧 ATM / Banking",
        "🛍️ Shopping Malls",
        "🔍 Custom Search"
    ]

    cat_quick_pills = st.pills(
        "Switch Facility Category:",
        options=cat_quick_options,
        default=cur_cat_name if cur_cat_name in cat_quick_options else "🌐 All Facilities",
        key="pills_quick_category_select"
    )
    if cat_quick_pills and cat_quick_pills != st.session_state.get("selected_sidebar_category"):
        st.session_state.selected_sidebar_category = cat_quick_pills
        st.rerun()

    # Dynamic Facility Search Mode & Radius Controls
    f_bar_c1, f_bar_c2, f_bar_c3 = st.columns([1.5, 1.2, 0.8])
    with f_bar_c1:
        f_modes = {
            "near_destination": "📍 Near Destination",
            "near_origin": "🛫 Near Origin",
            "along_route": "🛣️ Along Route Corridor",
            "near_map": "🗺️ Near Map Center"
        }
        cur_f_mode = st.session_state.get("fac_search_mode", "near_destination")
        sel_mode_val = st.selectbox(
            "Search Proximity Anchor:",
            options=list(f_modes.values()),
            index=list(f_modes.keys()).index(cur_f_mode) if cur_f_mode in f_modes else 0,
            key="sel_fac_proximity_anchor_box"
        )
        res_f_mode = next(k for k, v in f_modes.items() if v == sel_mode_val)
        if res_f_mode != st.session_state.get("fac_search_mode"):
            st.session_state.fac_search_mode = res_f_mode
            st.rerun()

    with f_bar_c2:
        rad_options = [3.0, 5.0, 10.0, 20.0, 35.0]
        cur_rad_val = st.session_state.get("fac_radius_km", 10.0)
        c_idx_rad = rad_options.index(cur_rad_val) if cur_rad_val in rad_options else 2
        sel_rad_val = st.selectbox(
            "Search Radius:",
            options=rad_options,
            index=c_idx_rad,
            format_func=lambda r: f"Within {r:.0f} km",
            key="sel_fac_radius_select_box"
        )
        if sel_rad_val != st.session_state.get("fac_radius_km"):
            st.session_state.fac_radius_km = sel_rad_val
            st.rerun()

    with f_bar_c3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh", key="btn_refresh_facilities_live", use_container_width=True, help="Re-query live OpenStreetMap POIs"):
            st.rerun()

    # Recompute active category facilities with selected proximity mode and radius
    active_category_facilities = get_facilities_for_category(
        category=cur_cat_name,
        polyline=primary_route_poly,
        origin_coords=coords_orig,
        dest_coords=coords_dest,
        search_mode=st.session_state.get("fac_search_mode", "near_destination"),
        radius_km=st.session_state.get("fac_radius_km", 10.0),
        enable_demo_mode=st.session_state.get("enable_demo_mode", False)
    )

    # Find category info
    matched_cat_enum = FacilityCategory.ALL_FACILITIES
    for k, cfg in CATEGORY_CONFIG.items():
        if cfg["short_label"].lower() in cur_cat_name.lower() or cfg["icon"] in cur_cat_name:
            matched_cat_enum = k
            break

    cat_info = CATEGORY_CONFIG.get(matched_cat_enum, CATEGORY_CONFIG[FacilityCategory.ALL_FACILITIES])

    # If Emergency Radar or SOS is active, render Emergency Assistance & Safety Radar dock (Screenshot 2)
    if "Emergency Radar" in cur_cat_name or "🚨" in cur_cat_name or bool(st.session_state.get("active_sos_type")):
        if "emergency_radar_active" not in st.session_state:
            st.session_state.emergency_radar_active = True
        em_is_active = st.session_state.emergency_radar_active or bool(st.session_state.get("active_sos_type"))

        radar_status_badge = (
            "<span style='color: #ef4444; background: rgba(239, 68, 68, 0.15); padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(239, 68, 68, 0.4); font-size: 0.74rem; font-weight: 800; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);'>● EMERGENCY RADAR ACTIVE</span>"
            if em_is_active else
            "<span style='color: #64748b; background: rgba(255, 255, 255, 0.04); padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); font-size: 0.74rem; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;'>○ RADAR STANDBY</span>"
        )

        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.65) 100%);
                    border: 1px solid rgba(56, 189, 248, 0.22); border-radius: 12px; padding: 14px 18px; margin-top: 14px; margin-bottom: 12px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);'>
            <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;'>
                <div style='display: flex; align-items: center; gap: 10px;'>
                    <span style='font-size: 1.4rem;'>🚨</span>
                    <div>
                        <div style='display: flex; align-items: center; gap: 8px;'>
                            <b style='color: #f1f5f9; font-size: 0.98rem; letter-spacing: 0.02em;'>
                                EMERGENCY ASSISTANCE & SURROUNDING SAFETY RADAR
                            </b>
                            {radar_status_badge}
                        </div>
                        <div style='font-size: 0.74rem; color: #94a3b8; margin-top: 2px;'>
                            Real-time corridor scan • Direct Google Maps navigation & verified safe havens along your journey
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Emergency Action Buttons Dock (Screenshot 2)
        dock_c1, dock_c2, dock_c3, dock_c4, dock_c5 = st.columns([1.1, 1, 1, 1, 1])
        with dock_c1:
            toggle_btn_label = "🛡️ Hide Radar" if em_is_active else "🚨 Emergency Radar"
            if st.button(toggle_btn_label, key="btn_toggle_emergency_radar", use_container_width=True, type="primary" if not em_is_active else "secondary"):
                st.session_state.emergency_radar_active = not em_is_active
                if not st.session_state.emergency_radar_active:
                    st.session_state.active_sos_type = None
                st.rerun()
        with dock_c2:
            if st.button("🩺 Medical SOS", key="btn_dock_sos_med", help="Instant dispatch to nearest trauma hospital", use_container_width=True):
                st.session_state.active_sos_type = "MEDICAL"
                st.session_state.emergency_radar_active = True
                st.session_state.selected_sidebar_category = "🚨 Emergency Radar"
                st.rerun()
        with dock_c3:
            if st.button("👮 Police SOS", key="btn_dock_sos_police", help="Instant dispatch to nearest police post & ERSS 112", use_container_width=True):
                st.session_state.active_sos_type = "POLICE"
                st.session_state.emergency_radar_active = True
                st.session_state.selected_sidebar_category = "🚨 Emergency Radar"
                st.rerun()
        with dock_c4:
            if st.button("🔥 Hazard SOS", key="btn_dock_sos_disaster", help="Emergency guidance to nearest cyclone shelter", use_container_width=True):
                st.session_state.active_sos_type = "DISASTER"
                st.session_state.emergency_radar_active = True
                st.session_state.selected_sidebar_category = "🚨 Emergency Radar"
                st.rerun()
        with dock_c5:
            if st.button("⛽ Breakdown SOS", key="btn_dock_sos_fuel", help="Find nearest highway fuel & fast EV charger", use_container_width=True):
                st.session_state.active_sos_type = "STRANDED"
                st.session_state.emergency_radar_active = True
                st.session_state.selected_sidebar_category = "🚨 Emergency Radar"
                st.rerun()

        # Safe simulated call testing interface
        if st.session_state.get("active_simulated_call"):
            sim_call = st.session_state.active_simulated_call
            sim_phone = sim_call.get("phone", "112")
            sim_name = sim_call.get("name", "Emergency Dispatch")
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(6, 78, 59, 0.4) 0%, rgba(15, 23, 42, 0.95) 100%);
                        border: 2px solid #10b981; border-radius: 12px; padding: 16px 20px; margin: 12px 0;
                        box-shadow: 0 0 25px rgba(16, 185, 129, 0.35);'>
                <div style='display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 10px;'>
                    <div>
                        <div style='display: flex; align-items: center; gap: 8px;'>
                            <span style='font-size: 1.5rem;'>📡</span>
                            <b style='color: #34d399; font-size: 1.05rem; letter-spacing: 0.02em;'>
                                SIMULATED EMERGENCY DISPATCH CALL (SAFE TEST MODE)
                            </b>
                            <span style='background: rgba(16, 185, 129, 0.2); color: #6ee7b7; font-size: 0.72rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; border: 1px solid #10b981;'>
                                🟢 RADIO LINK CONNECTED
                            </span>
                        </div>
                        <div style='color: #f1f5f9; font-size: 0.90rem; margin-top: 6px;'>
                            Connecting to: <b style='color: #38bdf8;'>{sim_name}</b> (Line: <code style='color: #a7f3d0;'>{sim_phone}</code>)
                        </div>
                        <div style='background: rgba(0, 0, 0, 0.35); border-radius: 8px; padding: 10px 14px; margin-top: 8px; font-size: 0.82rem; color: #94a3b8; line-height: 1.45;'>
                            🛡️ <b>Safe Test Mode Active:</b> You tested the Call feature safely! To protect real-world emergency responders and prevent accidental cellular dialing during testing, this connection is fully simulated with zero real phone calls placed.
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            c_hangup1, c_hangup2 = st.columns([1, 2])
            with c_hangup1:
                if st.button("🔴 Hang Up / End Simulation Test", key="btn_end_sim_call", use_container_width=True):
                    st.session_state.active_simulated_call = None
                    st.toast("Simulation test ended safely.", icon="📞")
                    st.rerun()

        # Active SOS Guidance Briefing
        if st.session_state.get("active_sos_type"):
            st_type = st.session_state.active_sos_type
            briefing = st.session_state.emergency_service_manager.create_sos_guidance_briefing(
                (user_current_lat, user_current_lon),
                emergency_type=st_type
            )
            fac_sos = briefing.get("facility")

            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(127, 29, 29, 0.35) 0%, rgba(15, 23, 42, 0.95) 100%);
                        border: 2px solid #ef4444; border-radius: 12px; padding: 16px 20px; margin: 12px 0;
                        box-shadow: 0 0 25px rgba(239, 68, 68, 0.35);'>
                <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;'>
                    <div style='display: flex; align-items: center; gap: 8px;'>
                        <span style='font-size: 1.4rem;'>🚨</span>
                        <b style='color: #f87171; font-size: 1.0rem; letter-spacing: 0.02em;'>
                            AI EMERGENCY DISPATCH BRIEFING ({st_type})
                        </b>
                    </div>
                    <span style='color: #cbd5e1; font-size: 0.74rem;'>
                        <b>{nat_emergency["country"]}</b> • Official SOS: <b style='color: #ef4444;'>{nat_emergency["primary_sos"]}</b>
                    </span>
                </div>
                <div style='font-size: 0.86rem; color: #f1f5f9; line-height: 1.45; margin-top: 8px;'>
                    "{briefing['spoken_speech']}"
                </div>
            </div>
            """, unsafe_allow_html=True)

            if fac_sos:
                sos_act1, sos_act2, sos_act3 = st.columns([1.2, 1, 0.8])
                with sos_act1:
                    if st.button("🧭 Route on App Map", key=f"btn_sos_app_route_{fac_sos['facility_id']}", use_container_width=True, type="primary"):
                        st.session_state.selected_dest_coords = (fac_sos["latitude"], fac_sos["longitude"])
                        st.session_state.selected_dest_label = fac_sos["name"]
                        st.session_state.pending_dest = fac_sos["name"]
                        st.session_state.last_synced_dest = fac_sos["name"]
                        st.session_state.txt_dest = fac_sos["name"]
                        st.session_state.selected_dest_id = fac_sos.get("facility_id", "sos_fac")
                        st.session_state.dest_candidates = []
                        st.session_state.dest_candidates_query = ""
                        st.session_state.movement_index = 0
                        st.session_state.is_in_transit = False
                        st.session_state.user_speed_kmh = 0.0
                        st.session_state.user_bearing_deg = 0.0
                        st.session_state.auto_fit_bounds = True
                        st.session_state.show_emergency_amenities_on_map = True
                        st.session_state.scroll_to_app_map = True
                        st.session_state.switch_to_nav_tab = True
                        st.toast(f"🧭 Routed to {fac_sos['name']} on Application Maps!", icon="🚨")
                        st.rerun()
                with sos_act2:
                    call_num = briefing.get("emergency_phone", nat_emergency["primary_sos"])
                    if st.button(f"📞 Safe Test Call ({call_num})", key="btn_sos_safe_call", use_container_width=True):
                        st.session_state.active_simulated_call = {
                            "name": fac_sos['name'],
                            "phone": call_num,
                            "type": f"{st_type} Emergency Station"
                        }
                        st.rerun()
                with sos_act3:
                    if st.button("❌ Dismiss SOS", key="btn_dismiss_sos", use_container_width=True):
                        st.session_state.active_sos_type = None
                        st.rerun()

    elif "Custom Search" in cur_cat_name:

        c_s1, c_s2 = st.columns([4, 1])
        with c_s1:
            main_custom_q = st.text_input(
                "Search Custom Place, Landmark or Coordinates to Route:",
                value=st.session_state.get("custom_search_query", ""),
                placeholder="e.g. Tenali Bus Station, Coffee Day, Vijayawada, 16.241, 80.584...",
                key="main_custom_search_input"
            )
        with c_s2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🔍 Search & Route", key="btn_main_search_custom", use_container_width=True, type="primary"):
                if main_custom_q.strip():
                    st.session_state.custom_search_query = main_custom_q.strip()
                    custom_f = resolve_custom_search_facility(
                        main_custom_q.strip(),
                        origin_coords=coords_orig,
                        geocode_fn=st.session_state.real_map_service.geocode
                    )
                    if custom_f:
                        st.session_state.selected_dest_coords = (custom_f["latitude"], custom_f["longitude"])
                        st.session_state.selected_dest_label = custom_f["name"]
                        st.session_state.pending_dest = custom_f["name"]
                        st.session_state.last_synced_dest = custom_f["name"]
                        st.session_state.txt_dest = custom_f["name"]
                        st.session_state.selected_dest_id = custom_f.get("facility_id", "custom_fac")
                        st.session_state.dest_candidates = []
                        st.session_state.dest_candidates_query = ""
                        st.session_state.movement_index = 0
                        st.session_state.is_in_transit = False
                        st.session_state.user_speed_kmh = 0.0
                        st.session_state.user_bearing_deg = 0.0
                        st.session_state.focused_route_id = "ALL"
                        st.session_state.auto_fit_bounds = True
                        st.session_state.show_category_facilities_on_map = True
                        st.session_state.scroll_to_app_map = True
                        st.session_state.switch_to_nav_tab = True
                        st.toast(f"🧭 Routing to {custom_f['name']} — displaying all candidate routes on Application Maps!", icon="🔍")
                        st.rerun()

    else:
        pass

    if not active_category_facilities:
        st.info(f"No facilities found for '{cur_cat_name}'. Select another category or use Custom Search.")
    else:
        grid_cols = st.columns(min(3, len(active_category_facilities)))
        for idx, fac in enumerate(active_category_facilities[:9]):
            with grid_cols[idx % 3]:
                f_phone = fac.get("contact_phone")
                f_phone_display = f"<div style='font-size: 0.72rem; color: #38bdf8; margin-top: 4px;'>📞 {f_phone}</div>" if f_phone else ""

                f_rating_val = fac.get("rating")
                if f_rating_val is not None:
                    f_rating_display = f"<span style='color: #f59e0b; font-weight: 700;'>★ {f_rating_val:.1f}</span>"
                else:
                    f_rating_display = "<span style='color: #94a3b8; font-style: italic;'>Rating unavailable</span>"

                f_source = fac.get("data_source", "OpenStreetMap Live POI")
                f_status = fac.get("verification_status", "OSM Mapped POI")

                st.markdown(f"""
                <div style='background: rgba(10, 20, 38, 0.80); border: 1.5px solid {cat_info["border_badge"]};
                            border-radius: 12px; padding: 14px; margin-bottom: 12px; display: flex; flex-direction: column;
                            justify-content: space-between; min-height: 230px; box-shadow: 0 4px 16px rgba(0,0,0,0.35);'>
                    <div>
                        <div style='display: flex; align-items: flex-start; justify-content: space-between; gap: 8px;'>
                            <div style='font-size: 1.35rem;'>{fac.get("amenity_icon", cat_info["icon"])}</div>
                            <div style='flex: 1;'>
                                <b style='font-size: 0.88rem; color: #f1f5f9; line-height: 1.3; display: block;'>{fac["name"]}</b>
                                <div style='margin-top: 4px;'>
                                    <span style='color: {cat_info["color"]}; font-size: 0.68rem; font-weight: 800; background: {cat_info["bg_badge"]}; padding: 2px 7px; border-radius: 6px; border: 1px solid {cat_info["border_badge"]};'>
                                        {fac.get("facility_type", cat_info["short_label"])}
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div style='font-size: 0.74rem; color: #94a3b8; margin-top: 8px;'>
                            <b>Corridor:</b> {fac.get("distance_from_route_km", 0.0):.1f} km • <span style='color: #38bdf8; font-weight: 700;'>🚗 ~{fac.get("road_distance_km", 0.0):.1f} km ({fac.get("eta_minutes", 1):.0f} mins)</span>
                        </div>
                        <div style='font-size: 0.72rem; color: #cbd5e1; margin-top: 4px;'>
                            <b>Hours:</b> <span style='color: #a7f3d0;'>{fac.get("operating_hours", "Open")}</span>
                        </div>
                        <div style='font-size: 0.72rem; margin-top: 2px;'>
                            <b>Rating:</b> {f_rating_display}
                        </div>
                        {f_phone_display}
                    </div>
                    <div style='font-size: 0.66rem; color: #64748b; margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 4px;'>
                        📍 {fac.get("address", "Transit Corridor")}<br/>
                        <span style='color: #38bdf8;'>● {f_source} • {f_status}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_act1, col_act2, col_act3 = st.columns([1.1, 1.0, 0.9])
                with col_act1:
                    if st.button("🧭 Route Here", key=f"btn_cat_route_{fac.get('facility_id', idx)}", use_container_width=True, type="primary"):
                        st.session_state.selected_dest_coords = (fac["latitude"], fac["longitude"])
                        st.session_state.selected_dest_label = fac["name"]
                        st.session_state.pending_dest = fac["name"]
                        st.session_state.last_synced_dest = fac["name"]
                        st.session_state.txt_dest = fac["name"]
                        st.session_state.selected_dest_id = fac.get("facility_id", f"fac_{idx}")
                        st.session_state.dest_candidates = []
                        st.session_state.dest_candidates_query = ""
                        st.session_state.movement_index = 0
                        st.session_state.is_in_transit = False
                        st.session_state.user_speed_kmh = 0.0
                        st.session_state.user_bearing_deg = 0.0
                        st.session_state.focused_route_id = "ALL"
                        st.session_state.auto_fit_bounds = True
                        st.session_state.show_category_facilities_on_map = True
                        st.session_state.scroll_to_app_map = True
                        st.session_state.switch_to_nav_tab = True
                        st.toast(f"🧭 Routing to {fac['name']} on Pathfinder Map!", icon="🗺️")
                        st.rerun()
                with col_act2:
                    if st.button("📍 Focus Map", key=f"btn_cat_focus_{fac.get('facility_id', idx)}", use_container_width=True):
                        st.session_state.map_center_lat = fac["latitude"]
                        st.session_state.map_center_lon = fac["longitude"]
                        st.session_state.map_zoom = 16
                        st.session_state.auto_fit_bounds = False
                        st.session_state.scroll_to_app_map = True
                        st.session_state.switch_to_nav_tab = True
                        st.toast(f"📍 Centered map on {fac['name']}", icon="🗺️")
                        st.rerun()
                with col_act3:
                    if f_phone:
                        if st.button("📞 Call", key=f"btn_cat_call_{fac.get('facility_id', idx)}", use_container_width=True):
                            st.session_state.active_simulated_call = {
                                "name": fac["name"],
                                "phone": f_phone,
                                "type": fac.get("facility_type", "Facility Dispatch"),
                                "info": f"Corridor Distance: ~{fac.get('road_distance_km', 0.0):.1f} km"
                            }
                            st.rerun()
                    else:
                        if "Emergency" in cur_cat_name or "🚨" in cur_cat_name:
                            if st.button("📞 112", key=f"btn_cat_call_112_{fac.get('facility_id', idx)}", use_container_width=True):
                                st.session_state.active_simulated_call = {
                                    "name": f"{fac['name']} (Emergency Line)",
                                    "phone": nat_emergency["primary_sos"],
                                    "type": fac.get("facility_type", "Emergency Services")
                                }
                                st.rerun()
                        else:
                            if st.button("ℹ️ Info", key=f"btn_cat_inq_{fac.get('facility_id', idx)}", use_container_width=True):
                                st.session_state.active_simulated_call = {
                                    "name": fac["name"],
                                    "phone": "Transit Information",
                                    "type": fac.get("facility_type", "Public Venue")
                                }
                                st.rerun()



with tab_places:
    st.markdown("### 🌟 Suggested Places & Highlights Near Location")
    # =========================================================================
    # SUGGESTED PLACES & HIGHLIGHTS AT LOCATION (DYNAMIC LIVE POIS)
    # =========================================================================
    st.markdown("---")
    
    # Priority: Destination if selected, otherwise Origin / Current Location
    focus_target = "Destination" if coords_dest else "Origin"
    if coords_dest and coords_orig:
        col_focus1, col_focus2 = st.columns([1.5, 3])
        with col_focus1:
            focus_target = st.radio("Explore POIs Around:", ["Destination", "Origin"], horizontal=True, key="places_explore_anchor")
    
    if focus_target == "Destination" and coords_dest:
        ref_lat = coords_dest[0]
        ref_lon = coords_dest[1]
        raw_dest_name = st.session_state.get("selected_dest_label") or dest_text or "Destination"
        ref_label = raw_dest_name.replace("📍", "").strip()
    elif coords_orig:
        ref_lat = coords_orig[0]
        ref_lon = coords_orig[1]
        raw_orig_name = st.session_state.get("selected_orig_label") or orig_text or st.session_state.get("user_live_label", "Origin")
        ref_label = raw_orig_name.replace("📍", "").strip()
    else:
        ref_lat = detected_coords[0]
        ref_lon = detected_coords[1]
        ref_label = st.session_state.get("user_live_label", "Current Location").replace("📍", "").strip()

    suggested_places = generate_suggested_places_at_location(
        lat=ref_lat,
        lon=ref_lon,
        location_name=ref_label
    )

    st.markdown(f"""
    <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;'>
        <div style='display: flex; align-items: center; gap: 10px;'>
            <span style='font-size: 1.4rem;'>📍</span>
            <div>
                <div style='font-size: 1.05rem; font-weight: 800; color: #f8fafc; letter-spacing: 0.02em;'>
                    SUGGESTED PLACES & HIGHLIGHTS NEAR {ref_label.upper()}
                </div>
                <div style='font-size: 0.74rem; color: #94a3b8;'>
                    Verified points of interest, cultural landmarks, and culinary highlights near your selected {focus_target.lower()}.
                </div>
            </div>
        </div>
        <span style='background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.4); color: #38bdf8; font-size: 0.72rem; font-weight: 800; padding: 4px 10px; border-radius: 20px;'>
            ● LIVE GEOGRAPHIC POI DIRECTORY
        </span>
    </div>
    """, unsafe_allow_html=True)

    if not suggested_places:
        st.info(f"ℹ️ No points of interest or cultural highlights found within the immediate radius of {ref_label}. Select a different destination or explore nearby facilities.")
    else:
        sug_cols = st.columns(3)
        for idx, place in enumerate(suggested_places):
            col_idx = idx % 3
            with sug_cols[col_idx]:
                st.markdown(render_place_details_card_html(place), unsafe_allow_html=True)
                clean_name = place['name']
                for prefix in [ref_label, ref_label.split(',')[0]]:
                    clean_name = clean_name.replace(prefix, '').strip(' -–,')
                if not clean_name or len(clean_name) < 3:
                    clean_name = place['name']
                if len(clean_name) > 22:
                    clean_name = clean_name[:20] + "..."
                
                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    if st.button("🧭 Route Here", key=f"btn_nav_sug_{place['place_id']}", use_container_width=True, type="primary"):
                        st.session_state.selected_dest_coords = (place["latitude"], place["longitude"])
                        st.session_state.selected_dest_label = place["name"]
                        st.session_state.last_synced_dest = place["name"]
                        st.session_state.pending_dest = place["name"]
                        st.session_state.txt_dest = place["name"]
                        st.session_state.movement_index = 0
                        st.session_state.is_in_transit = False
                        st.session_state.scroll_to_app_map = True
                        st.session_state.switch_to_nav_tab = True
                        st.toast(f"🧭 Destination set to {place['name']}!", icon="🎯")
                        st.rerun()
                with bcol2:
                    if st.button("📍 Focus Map", key=f"btn_focus_sug_{place['place_id']}", use_container_width=True):
                        st.session_state.map_center_lat = place["latitude"]
                        st.session_state.map_center_lon = place["longitude"]
                        st.session_state.map_zoom = 16
                        st.session_state.auto_fit_bounds = False
                        st.session_state.scroll_to_app_map = True
                        st.session_state.switch_to_nav_tab = True
                        st.toast(f"📍 Centered map on {place['name']}", icon="🗺️")
                        st.rerun()

# =========================================================================
# FLOATING CIRCULAR CHATBOT: A.U.R.A. (Adaptive User Route Assistant)
# =========================================================================
with st.popover(" ", help="Open A.U.R.A. • PathFinder AI Copilot"):
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(56, 189, 248, 0.25); padding-bottom: 8px; margin-bottom: 10px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="{aura_logo_uri}" style="width: 36px; height: 36px; border-radius: 50%; border: 1.5px solid #38bdf8; object-fit: cover; box-shadow: 0 0 10px rgba(56, 189, 248, 0.55);" />
            <div>
                <div style="font-weight: 800; font-size: 0.96rem; color: #f8fafc; letter-spacing: 0.04em;">
                    A.U.R.A. • PathFinder AI
                </div>
                <div style="font-size: 0.66rem; color: #38bdf8; font-family: 'JetBrains Mono', monospace; font-weight: 600;">
                    ADAPTIVE USER ROUTE ASSISTANT
                </div>
            </div>
        </div>
        <span style="font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px; background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #34d399; letter-spacing: 0.05em;">
            ● ONLINE
        </span>
    </div>
    """, unsafe_allow_html=True)
    render_aura_chat_box(key_prefix="popover_window", height=340)

# Floating Visual Overlay for Chatbot Trigger Logo (renders over invisible popover button)
if aura_logo_uri:
    st.markdown(f'<img src="{aura_logo_uri}" class="floating-aura-logo-overlay" alt="A.U.R.A. Chatbot Logo" />', unsafe_allow_html=True)






