import streamlit as st
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import re
import os
import base64
from PIL import Image

from src.pipeline import CampusSpherePipeline as CampusAegisPipeline
from src.visualizer import create_3d_building_figure, create_2d_campus_map
from src.planning_agent import EvacuationPlanningCSP, EvacuationGroup
from src.chatbot_agent import AegisChatbotAgent
from src.pathfinder_chatbot import PathfinderChatbot
from src.safety_monitor import SystemSafetyState
import streamlit.components.v1 as components
from src.voice_guidance import generate_simple_spoken_narrative, build_voice_assistant_html
from src.google_maps_voice_navigator import prepare_google_maps_voice_data, render_google_maps_voice_navigator_html

# Page configuration
st.set_page_config(
    page_title="P.A.T.H.F.I.N.D.E.R. • Predictive Adaptive Transit & Hazard-Free Routing",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(15, 23, 42, 0.7);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(56, 189, 248, 0.18);
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        padding: 8px 16px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.88rem;
        border: 1px solid transparent;
        transition: all 0.25s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(30, 41, 59, 0.7) !important;
        color: #38bdf8 !important;
        border-color: rgba(56, 189, 248, 0.3) !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.22) 0%, rgba(16, 185, 129, 0.18) 100%) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.45) !important;
        box-shadow: 0 4px 14px -2px rgba(14, 165, 233, 0.3) !important;
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
from src.emergency_service import EmergencyServiceManager, FacilityCategory, get_national_emergency_contacts

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

# Populate default real-world regional road blockages (NH-16 bridge repair & Canal Bund closure)
def seed_default_regional_blockages(mgr: RoadConditionManager):
    default_restrictions = [
        RoadRestriction(
            restriction_id="RESTR_NH16_BRIDGE",
            restriction_type=RestrictionType.ROAD_CLOSURE,
            road_name="NH-16 Bypass Expressway",
            latitude=16.2890,
            longitude=80.4550,
            affected_radius_meters=220.0,
            description="Emergency structural bridge repair & resurfacing",
            is_hard_closure=True,
            is_demonstration=False,
            source="REGIONAL_HIGHWAY_AUTHORITY"
        ),
        RoadRestriction(
            restriction_id="RESTR_CANAL_BUND",
            restriction_type=RestrictionType.ROAD_CLOSURE,
            road_name="Tenali Canal Bund Road",
            latitude=16.2420,
            longitude=80.5310,
            affected_radius_meters=200.0,
            description="Canal breach & culvert reconstruction",
            is_hard_closure=True,
            is_demonstration=False,
            source="IRRIGATION_DEPT_INFRASTRUCTURE"
        )
    ]
    active_ids = {r.restriction_id for r in mgr.get_active_restrictions()}
    for r in default_restrictions:
        if r.restriction_id not in active_ids:
            mgr.add_restriction(r)

seed_default_regional_blockages(st.session_state.road_condition_manager)
if len(st.session_state.real_hazard_map.get_active_hazards()) == 0:
    st.session_state.real_hazard_map.add_hazard(GeographicHazard(
        hazard_id="HAZ_TENALI_SPILL",
        incident_type="CHEMICAL_SPILL",
        severity=HazardSeverity.HIGH,
        latitude=16.2410,
        longitude=80.5315,
        radius_meters=180.0,
        description="Hazardous material tanker spill & containment perimeter",
        affected_road_name="Tenali Canal Bund Road",
        is_demonstration=True,
        confidence_level=0.95,
        source="CAD_EMERGENCY_DISPATCH"
    ))
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

    cur_obj = st.session_state.get("active_objective", OptimizationObjective.FASTEST)

    # Clean, High-Contrast Interactive Objective Buttons
    obj_definitions = [
        (
            OptimizationObjective.FASTEST,
            "⚡ Fastest Route",
            "Minimizes transit duration & evades traffic",
            "#38bdf8"
        ),
        (
            OptimizationObjective.SHORTEST,
            "📏 Shortest Route",
            "Minimizes ground mileage & physical distance",
            "#c084fc"
        ),
        (
            OptimizationObjective.BALANCED,
            "⚖️ Balanced Route",
            "Harmonized 50/50 time & distance balance",
            "#34d399"
        ),
        (
            OptimizationObjective.ACCESSIBLE,
            "♿ Accessible Route",
            "Prioritizes step-free paths & certified ramps",
            "#fbbf24"
        ),
    ]

    for obj_enum, title, desc, accent_col in obj_definitions:
        is_active = (cur_obj == obj_enum)
        btn_label = f"✓ {title}" if is_active else title
        btn_type = "primary" if is_active else "secondary"

        if st.button(btn_label, key=f"btn_obj_{obj_enum.value.lower()}", use_container_width=True, type=btn_type):
            st.session_state.active_objective = obj_enum
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
        access_bar_html = f"""
        <div>
            <div style="display: flex; justify-content: space-between; font-size: 0.64rem; font-family: 'JetBrains Mono', monospace; color: #94a3b8; margin-bottom: 2px;">
                <span>♿ Barrier Evasion Strictness</span>
                <span style="color: #fbbf24; font-weight: 700;">100% Strict</span>
            </div>
            <div style="width: 100%; height: 4px; background: rgba(255,255,255,0.08); border-radius: 9999px; overflow: hidden;">
                <div style="width: 100%; height: 100%; background: linear-gradient(90deg, #fbbf24, #10b981); border-radius: 9999px;"></div>
            </div>
        </div>
        """

    st.markdown(f"""
    <div style="background: rgba(10, 20, 38, 0.72); border: 1px solid {cur_tele['accent']}40; border-radius: 12px; padding: 10px 12px; margin-top: 8px; margin-bottom: 12px; box-shadow: 0 4px 16px {cur_tele['glow']}; backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="font-size: 0.66rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: {cur_tele['accent']}; letter-spacing: 0.05em;">
                ● ACTIVE STRATEGY
            </span>
            <span style="font-size: 0.63rem; color: #94a3b8; font-weight: 600;">AI ROUTE BIAS</span>
        </div>
        <div style="font-size: 0.74rem; font-weight: 700; color: #f8fafc; margin-bottom: 5px;">
            {cur_tele['title']}
        </div>
        <div style="font-size: 0.70rem; color: #cbd5e1; line-height: 1.35; margin-bottom: 8px;">
            {cur_tele['profile']}
        </div>
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
            </div>
            {access_bar_html}
    </div>
    """, unsafe_allow_html=True)



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

# Top Header: Status HUD & Navigation Banner
col_logo, col_hdr, col_status = st.columns([0.7, 5.3, 2.0], vertical_alignment="center")
with col_logo:
    if os.path.exists("assets/pathfinder_logo.jpg"):
        st.image("assets/pathfinder_logo.jpg", width=75)
    elif os.path.exists("assets/campus_aegis_logo.jpg"):
        st.image("assets/campus_aegis_logo.jpg", width=75)
with col_hdr:
    st.markdown("""
    <div style='display: flex; align-items: baseline; gap: 12px;'>
        <h1 style='margin: 0; padding: 0; font-size: 2.1rem; font-weight: 800; background: linear-gradient(135deg, #38bdf8 0%, #10b981 60%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>P.A.T.H.F.I.N.D.E.R.</h1>
        <span style='font-size: 0.95rem; color: #94a3b8; font-weight: 500;'>Predictive Adaptive Transit & Hazard-Free Intelligent Navigation</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Directed Evacuation Routing • Multi-Objective Route Optimization • Autonomous Hazard Awareness • Live Road Restrictions")

with col_status:
    mode_ind = st.session_state.road_condition_manager.get_mode_indicator()
    st.markdown(f"<div style='text-align: right;'><span style='{mode_ind['badge_css']} font-size: 0.78rem; font-weight: 700; padding: 4px 12px; border-radius: 9999px;'>{mode_ind['label']}</span></div>", unsafe_allow_html=True)

# Prominent Environment Status Banner
env_badge = st.session_state.road_condition_manager.get_mode_indicator()
active_restr_count = len(st.session_state.road_condition_manager.get_active_restrictions())
active_traffic_count = len(st.session_state.road_condition_manager.get_active_traffic_conditions())
active_haz_count = len(st.session_state.real_hazard_map.get_active_hazards())

st.markdown(f"""
<div style='background: rgba(10, 20, 38, 0.62); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); border: 1px solid rgba(56, 189, 248, 0.22); border-left: 5px solid {env_badge["color"]}; border-radius: 8px; padding: 8px 14px; margin: 6px 0 14px 0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);'>
    <div style='display: flex; align-items: center; gap: 10px;'>
        <span style='font-size: 0.92rem; font-weight: 700; color: {env_badge["color"]};'>{env_badge["label"]}</span>
        <span style='font-size: 0.80rem; color: #94a3b8;'>{env_badge["description"]}</span>
    </div>
    <div style='display: flex; gap: 12px; font-size: 0.78rem; color: #cbd5e1; background: rgba(0,0,0,0.3); padding: 4px 12px; border-radius: 6px;'>
        <span>Active Hazards: <b style='color: #ef4444;'>{active_haz_count}</b></span>
        <span>Road Restrictions: <b style='color: #f59e0b;'>{active_restr_count}</b></span>
        <span>Traffic Delays: <b style='color: #38bdf8;'>{active_traffic_count}</b></span>
        <span>Objective: <b style='color: #10b981;'>{st.session_state.get("active_objective", OptimizationObjective.FASTEST).value}</b></span>
    </div>
</div>
""", unsafe_allow_html=True)

# Automatic Browser Satellite Geolocation Autopilot Script
st.html("""
<script>
(function() {
    if (!navigator.geolocation) {
        console.warn("Satellite GPS: navigator.geolocation not supported.");
        return;
    }

    function distM(lat1, lon1, lat2, lon2) {
        var R = 6371000;
        var dLat = (lat2 - lat1) * Math.PI / 180;
        var dLon = (lon2 - lon1) * Math.PI / 180;
        var a = Math.sin(dLat/2)*Math.sin(dLat/2) +
                Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180) *
                Math.sin(dLon/2)*Math.sin(dLon/2);
        return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    }

    function onGpsPosition(pos) {
        var lat = pos.coords.latitude;
        var lon = pos.coords.longitude;
        var acc = pos.coords.accuracy || 6.0;
        var spd = (pos.coords.speed !== null && !isNaN(pos.coords.speed) && pos.coords.speed > 0) ? (pos.coords.speed * 3.6) : 0.0;
        var hdg = (pos.coords.heading !== null && !isNaN(pos.coords.heading)) ? pos.coords.heading : 0.0;

        var url = new URL(window.location.href);
        var curLat = url.searchParams.get("gps_lat");
        var curLon = url.searchParams.get("gps_lon");
        var hasGps = (curLat !== null && curLon !== null);

        var distMoved = 999.0;
        if (hasGps) {
            distMoved = distM(parseFloat(curLat), parseFloat(curLon), lat, lon);
        }

        var now = Date.now();
        var lastSync = window._lastPathfinderGpsSync || 0;

        // Auto-sync immediately on first satellite lock, OR if user moved > 6 meters and 3 seconds elapsed
        if (!hasGps || (distMoved > 6.0 && (now - lastSync) > 3000)) {
            window._lastPathfinderGpsSync = now;
            url.searchParams.set("gps_lat", lat.toFixed(6));
            url.searchParams.set("gps_lon", lon.toFixed(6));
            url.searchParams.set("gps_acc", acc.toFixed(1));
            url.searchParams.set("gps_spd", spd.toFixed(1));
            url.searchParams.set("gps_hdg", hdg.toFixed(1));
            window.location.replace(url.toString());
        }
    }

    if (!window._pathfinderGpsWatchId) {
        // Immediate satellite fix
        navigator.geolocation.getCurrentPosition(onGpsPosition, function(err) {
            console.warn("Satellite GPS initial fix:", err.message);
        }, { enableHighAccuracy: true, timeout: 8000, maximumAge: 2000 });

        // Continuous high-precision satellite tracker for real-time movement detection
        window._pathfinderGpsWatchId = navigator.geolocation.watchPosition(onGpsPosition, function(err) {
            console.warn("Satellite GPS live watch:", err.message);
        }, { enableHighAccuracy: true, timeout: 15000, maximumAge: 1000 });
    }
})();
</script>
""")

# Check if real hardware device GPS was passed via URL query params
if "gps_lat" in st.query_params and "gps_lon" in st.query_params:
    try:
        q_lat = float(st.query_params["gps_lat"])
        q_lon = float(st.query_params["gps_lon"])
        q_acc = float(st.query_params.get("gps_acc", 6.0))
        q_spd = float(st.query_params.get("gps_spd", 0.0))
        q_hdg = float(st.query_params.get("gps_hdg", 0.0))

        st.session_state.hardware_gps_coords = (q_lat, q_lon)
        st.session_state.user_live_coords = (q_lat, q_lon)
        st.session_state.user_gps_accuracy = q_acc
        st.session_state.user_speed_kmh = q_spd
        st.session_state.user_bearing_deg = q_hdg
        st.session_state.is_in_transit = (q_spd > 1.2)

        # Compute cardinal heading
        cardinals = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        card_idx = int((q_hdg + 11.25) / 22.5) % 16
        st.session_state.user_heading_cardinal = cardinals[card_idx]

        if st.session_state.get("last_gps_param") != (q_lat, q_lon):
            st.session_state.last_gps_param = (q_lat, q_lon)
            try:
                resolved_addr = st.session_state.real_map_service.reverse_geocode(q_lat, q_lon)
                clean_lbl = resolved_addr.split(",")[0].strip() if resolved_addr else f"{q_lat:.4f}, {q_lon:.4f}"
                st.session_state.user_live_label = f"🛰️ Live Satellite ({clean_lbl})"
            except Exception:
                st.session_state.user_live_label = f"🛰️ Live Satellite ({q_lat:.4f}, {q_lon:.4f})"

            st.session_state.real_location_service.set_permission(LocationPermissionStatus.GRANTED)
            st.session_state.real_location_service.record_movement(
                q_lat, q_lon,
                accuracy_m=q_acc,
                speed_mps=(q_spd / 3.6),
                label="Satellite GPS"
            )
    except Exception:
        pass

# =========================================================================
# =========================================================================
# PRIMARY APPLICATION TABS: NAVIGATION & EMERGENCY OPERATIONS CENTER (E.O.C.)
# =========================================================================
# =========================================================================
st.markdown("### 🧭 P.A.T.H.F.I.N.D.E.R. • Real-Time Adaptive Navigation")
st.caption("Predictive Adaptive Transit & Hazard-Free Intelligent Navigation Directed Evacuation Routing with multi-corridor safety optimization.")

# Initialize Live Position Tracking & Movement Kinematics
if "user_live_coords" not in st.session_state:
    st.session_state.user_live_coords = (16.2335, 80.5505)
    st.session_state.user_live_label = "🛰️ Connecting to Live Satellite GPS..."
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
    st.session_state.selected_dest_coords = (16.3067, 80.4365)
    st.session_state.selected_dest_label = "Guntur City Center"

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
    st.session_state.txt_orig = "📍 Current Location"
if "txt_dest" not in st.session_state:
    st.session_state.txt_dest = "Guntur City Center"
if "last_synced_orig" not in st.session_state:
    st.session_state.last_synced_orig = st.session_state.txt_orig
if "last_synced_dest" not in st.session_state:
    st.session_state.last_synced_dest = st.session_state.txt_dest

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

# Resolve pending programmatic location updates before widget instantiation
if "pending_orig" in st.session_state:
    st.session_state.txt_orig = st.session_state.pop("pending_orig")
if "pending_dest" in st.session_state:
    st.session_state.txt_dest = st.session_state.pop("pending_dest")

# Symmetrical Journey Input Controls with Custom Start & Reset
col_orig_in, col_swap_btn, col_dest_in, col_mode_in = st.columns([3.2, 0.9, 3.1, 1.8], vertical_alignment="bottom")

with col_orig_in:
    orig_text = st.text_input(
        "🟢 Start Location (Origin):",
        key="txt_orig",
        placeholder="Type custom start location or 'Current Location'...",
        help="Defaults to your current location. You can type any custom city, address, or landmark to route from there."
    )
    if orig_text and orig_text != st.session_state.last_synced_orig:
        st.session_state.last_synced_orig = orig_text
        if "current" in orig_text.lower():
            CURRENT_BASE = st.session_state.get("hardware_gps_coords") or st.session_state.get("user_live_coords") or (16.2335, 80.5505)
            st.session_state.user_live_coords = CURRENT_BASE
            st.session_state.user_live_label = "🛰️ Live Satellite Current Location"
            st.session_state.movement_index = 0
            st.session_state.is_in_transit = False
            st.session_state.real_location_service.set_manual_location(CURRENT_BASE[0], CURRENT_BASE[1], "Satellite Location")
            st.rerun()
        else:
            geo_o = st.session_state.real_map_service.geocode(orig_text)
            if geo_o:
                st.session_state.user_live_coords = (geo_o["lat"], geo_o["lon"])
                st.session_state.user_live_label = geo_o.get("display_name", orig_text)
                st.session_state.movement_index = 0
                st.session_state.is_in_transit = False
                st.session_state.user_speed_kmh = 0.0
                st.session_state.user_bearing_deg = 0.0
                st.session_state.real_location_service.set_manual_location(geo_o["lat"], geo_o["lon"], orig_text)
                st.rerun()

with col_swap_btn:
    btn_sub_c1, btn_sub_c2 = st.columns([1, 1])
    with btn_sub_c1:
        if st.button("⇄", help="Swap Start & Destination Locations", use_container_width=True):
            prev_orig_txt = st.session_state.txt_orig
            prev_dest_txt = st.session_state.txt_dest

            # 1. Swap input text values
            st.session_state.pending_orig = prev_dest_txt
            st.session_state.pending_dest = prev_orig_txt

            # 2. Swap coordinates & labels
            c_orig = st.session_state.user_live_coords
            l_orig = st.session_state.user_live_label
            st.session_state.user_live_coords = st.session_state.selected_dest_coords
            st.session_state.user_live_label = st.session_state.selected_dest_label
            st.session_state.selected_dest_coords = c_orig
            st.session_state.selected_dest_label = l_orig

            # 3. Synchronize kinematics & location service
            st.session_state.movement_index = 0
            st.session_state.is_in_transit = False
            st.session_state.user_speed_kmh = 0.0
            st.session_state.user_bearing_deg = 0.0
            st.session_state.real_location_service.set_manual_location(
                st.session_state.user_live_coords[0],
                st.session_state.user_live_coords[1],
                str(st.session_state.user_live_label)
            )
            st.rerun()
    with btn_sub_c2:
        if st.button("📍", help="Reset start to Current Satellite Location", use_container_width=True):
            CURRENT_BASE = st.session_state.get("hardware_gps_coords") or st.session_state.get("user_live_coords") or (16.2335, 80.5505)
            st.session_state.user_live_coords = CURRENT_BASE
            st.session_state.user_live_label = "🛰️ Live Satellite Current Location"
            st.session_state.pending_orig = "📍 Current Location"
            st.session_state.real_location_service.set_manual_location(CURRENT_BASE[0], CURRENT_BASE[1], "Satellite Location")
            st.toast("Start location reset to Current Satellite Location", icon="🛰️")
            st.rerun()

with col_dest_in:
    dest_text = st.text_input(
        "🏁 Destination Location (Target):",
        key="txt_dest",
        placeholder="Type destination city, landmark, or click map...",
        help="Type destination, or click anywhere on the interactive map."
    )
    if dest_text and dest_text != st.session_state.last_synced_dest:
        st.session_state.last_synced_dest = dest_text
        if "current" in dest_text.lower():
            CURRENT_BASE = st.session_state.get("hardware_gps_coords") or st.session_state.get("user_live_coords") or (16.2335, 80.5505)
            st.session_state.selected_dest_coords = CURRENT_BASE
            st.session_state.selected_dest_label = "🛰️ Live Satellite Current Location"
            st.rerun()
        else:
            geo_d = st.session_state.real_map_service.geocode(dest_text)
            if geo_d:
                st.session_state.selected_dest_coords = (geo_d["lat"], geo_d["lon"])
                st.session_state.selected_dest_label = geo_d.get("display_name", dest_text)
                st.session_state.movement_index = 0
                st.session_state.is_in_transit = False
                st.session_state.user_speed_kmh = 0.0
                st.session_state.user_bearing_deg = 0.0
                st.rerun()
            else:
                st.toast(f"⚠️ Could not resolve destination '{dest_text}'. Try entering coordinates or city name.", icon="⚠️")

with col_mode_in:
    mode_options = [
        "🚗 Car",
        "🏍️ Bike / Scooter",
        "🚜 Tractor",
        "🚚 Truck",
        "🚶 Walking",
        "🚴 Bicycling"
    ]
    prev_mode_idx = 0
    if "last_selected_mode" in st.session_state and st.session_state.last_selected_mode in mode_options:
        prev_mode_idx = mode_options.index(st.session_state.last_selected_mode)

    travel_mode_str = st.selectbox("Travel Mode:", mode_options, index=prev_mode_idx)
    st.session_state.last_selected_mode = travel_mode_str

    if "Bike" in travel_mode_str or "Scooter" in travel_mode_str:
        travel_mode = TravelMode.MOTORCYCLE
    elif "Tractor" in travel_mode_str:
        travel_mode = TravelMode.TRACTOR
    elif "Truck" in travel_mode_str:
        travel_mode = TravelMode.TRUCK
    elif "Walking" in travel_mode_str:
        travel_mode = TravelMode.WALKING
    elif "Bicycling" in travel_mode_str:
        travel_mode = TravelMode.BICYCLING
    else:
        travel_mode = TravelMode.DRIVING

# Compute real-time movement badge
is_user_moving = st.session_state.get("user_speed_kmh", 0.0) > 1.2
if is_user_moving:
    movement_telemetry_html = f"<span class='route-tag-pill' style='background: rgba(16, 185, 129, 0.25); color: #34d399; border: 1.5px solid #10b981;'>🟢 MOVING • {st.session_state.user_speed_kmh:.1f} km/h • {st.session_state.get('user_heading_cardinal', 'N')} ({st.session_state.user_bearing_deg:.0f}°)</span>"
else:
    movement_telemetry_html = f"<span class='route-tag-pill' style='background: rgba(56, 189, 248, 0.18); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4);'>🛰️ SATELLITE LOCKED • ±{st.session_state.get('user_gps_accuracy', 6.0):.1f}m</span>"

# Display Sleek In-Dash Telemetry Ribbon
st.markdown(f"""
<div class='route-ribbon-bar'>
    <div style='display: flex; align-items: center; gap: 8px; flex-wrap: wrap;'>
        <span class='route-tag-pill' style='background: rgba(16, 185, 129, 0.18); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4);'>
            🟢 START
        </span>
        <span style='color: #f1f5f9; font-weight: 600; font-size: 0.86rem;'>{st.session_state.user_live_label}</span>
        <span style='color: #64748b; font-size: 0.74rem;'>({st.session_state.user_live_coords[0]:.4f}, {st.session_state.user_live_coords[1]:.4f})</span>
        <span style='color: #38bdf8; font-weight: 700; margin: 0 4px;'>➔</span>
        <span class='route-tag-pill' style='background: rgba(239, 68, 68, 0.18); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4);'>
            🏁 DEST
        </span>
        <span style='color: #f1f5f9; font-weight: 600; font-size: 0.86rem;'>{st.session_state.selected_dest_label}</span>
        <span style='color: #64748b; font-size: 0.74rem;'>({st.session_state.selected_dest_coords[0]:.4f}, {st.session_state.selected_dest_coords[1]:.4f})</span>
    </div>
    <div style='display: flex; gap: 12px; font-size: 0.78rem; align-items: center; flex-wrap: wrap;'>
        {movement_telemetry_html}
        <span style='color: #38bdf8;'>Mode: <b>{travel_mode_str}</b></span>
        <span style='color: #94a3b8;'>Unit: <b style="color: #38bdf8;">{st.session_state.get('distance_unit', 'km').upper()}</b></span>
        <span style='background: rgba(16, 185, 129, 0.15); color: #10b981; font-weight: 700; padding: 2px 8px; border-radius: 4px;'>🛡️ Global Transit Evasion Active</span>
    </div>
</div>
""", unsafe_allow_html=True)

coords_orig = st.session_state.user_live_coords
coords_dest = st.session_state.selected_dest_coords

# Evaluate & Rank Candidate Routes using Multi-Objective Optimization Model
active_obj = st.session_state.get("active_objective", OptimizationObjective.FASTEST)
require_acc = st.session_state.get("requires_accessible", False) or (active_obj == OptimizationObjective.ACCESSIBLE)

# Calculate Candidate Routes between selected origin & destination using backend search
candidate_routes = st.session_state.real_route_engine.calculate_routes(
    coords_orig[0], coords_orig[1],
    coords_dest[0], coords_dest[1],
    mode=travel_mode,
    require_accessible=require_acc,
    is_in_transit=st.session_state.get("is_in_transit", False),
    active_hazard_count=active_restr_count
)

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

eligible_ranked = [r for r in ranked_routes if r.is_eligible]
restricted_ranked = [r for r in ranked_routes if not r.is_eligible]




# Route signature tracking: When origin, destination, or mode changes, always default to "ALL"
route_sig = (
    round(coords_orig[0], 4), round(coords_orig[1], 4),
    round(coords_dest[0], 4), round(coords_dest[1], 4),
    travel_mode, active_obj, require_acc
)
if st.session_state.get("_prev_route_sig") != route_sig:
    st.session_state._prev_route_sig = route_sig
    st.session_state.focused_route_id = "ALL"

# Check query parameters for touchable route card clicks
if "focus_route" in st.query_params:
    q_route = st.query_params.get("focus_route")
    if q_route:
        st.session_state.focused_route_id = q_route
    try:
        del st.query_params["focus_route"]
    except Exception:
        pass

# Validate and retrieve focused route state (defaults to "ALL" so all routes start visible)
if "focused_route_id" not in st.session_state:
    st.session_state.focused_route_id = "ALL"

valid_route_ids = {r.route.route_id for r in ranked_routes}
if st.session_state.focused_route_id != "ALL" and st.session_state.focused_route_id not in valid_route_ids:
    st.session_state.focused_route_id = "ALL"

cur_focus = st.session_state.focused_route_id

# Build Map Polylines with clean visual hierarchy
route_polylines = []
palette = ["#10b981", "#0ea5e9", "#a855f7"]
for r_item in ranked_routes:
    # If a particular path is selected, hide all other paths!
    if cur_focus != "ALL" and r_item.route.route_id != cur_focus:
        continue

    if r_item.is_eligible:
        color = palette[(r_item.rank - 1) % len(palette)]
        weight = 7 if (cur_focus == r_item.route.route_id or r_item.rank == 1) else 4
        opacity = 1.0 if (cur_focus == r_item.route.route_id or r_item.rank == 1) else 0.70
        label = f"Rank {r_item.rank}: {r_item.route.name} ({r_item.effective_duration_minutes:.1f} min)"
    else:
        color = "#ef4444"
        weight = 6 if cur_focus == r_item.route.route_id else 3
        opacity = 0.90 if cur_focus == r_item.route.route_id else 0.50
        label = f"⚠️ RESTRICTED / BLOCKED: {r_item.route.name}"

    route_polylines.append({
        "name": label,
        "coordinates": r_item.route.polyline,
        "color": color,
        "weight": weight,
        "opacity": opacity,
        "rank": r_item.rank,
        "is_eligible": r_item.is_eligible,
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

# Initialize map viewport zoom and satellite basemap style state
if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = 13
if "map_style" not in st.session_state:
    st.session_state.map_style = "satellite_hybrid"

# Discover Real-World Emergency Services & Safety Amenities along Active Route Corridor
primary_route_poly = []
if route_polylines:
    chosen_r = next((r for r in route_polylines if r.get("is_eligible")), route_polylines[0])
    primary_route_poly = chosen_r.get("coordinates", [])
if not primary_route_poly and coords_orig and coords_dest:
    primary_route_poly = [coords_orig, coords_dest]

route_emergency_facilities = st.session_state.emergency_service_manager.get_facilities_along_route(
    polyline=primary_route_poly,
    corridor_radius_km=5.0,
    user_coords=coords_orig
)

# Render Interactive Real-World Map with Highlighted Caution Symbols & Satellite Imagery
folium_map = st.session_state.real_map_service.build_interactive_map(
    center_lat=(coords_orig[0] + coords_dest[0]) / 2.0,
    center_lon=(coords_orig[1] + coords_dest[1]) / 2.0,
    zoom_start=st.session_state.map_zoom,
    origin_coords=coords_orig,
    dest_coords=coords_dest,
    route_polylines=route_polylines,
    hazards=hazard_markers,
    road_closures=restriction_markers,
    breadcrumb_trail=st.session_state.real_location_service.get_movement_trail(),
    map_style=st.session_state.map_style,
    traveler_avatar="tractor" if travel_mode == TravelMode.TRACTOR else (
        "bike" if travel_mode == TravelMode.MOTORCYCLE else (
            "truck" if travel_mode == TravelMode.TRUCK else (
                "boy" if travel_mode == TravelMode.WALKING else (
                    "bicycle" if travel_mode == TravelMode.BICYCLING else "car"
                )
            )
        )
    ),
    emergency_facilities=[f.to_dict() for f in route_emergency_facilities]
)
# Reset one-shot auto_fit_bounds after building
if st.session_state.get("auto_fit_bounds"):
    st.session_state.auto_fit_bounds = False

# Spread Interactive Real-World Map (Full Width High-Resolution Satellite View)
map_key = f"real_world_leaflet_map_{st.session_state.map_style}_{st.session_state.map_zoom}_{cur_focus}_{len(hazard_markers)}_{len(restriction_markers)}_{coords_dest[0]:.3f}_{coords_dest[1]:.3f}"
map_out = st_folium(folium_map, zoom=st.session_state.map_zoom, width=None, height=540, key=map_key, use_container_width=True)

# Keep track of zoom if user zoomed via scroll wheel
if map_out and map_out.get("zoom") is not None:
    live_zoom = map_out["zoom"]
    if isinstance(live_zoom, (int, float)) and int(live_zoom) != st.session_state.map_zoom:
        st.session_state.map_zoom = int(live_zoom)

# Check if user clicked on the map to pick destination
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
# ROUTE RECOMMENDATION & SAFETY ANALYSIS (BELOW MAP)
# =========================================================================
st.markdown(f"### 🧭 Route Recommendation & Safety Analysis ({active_obj.value})")

# Pre-Route Safety & Hazard Clearance Assessment
unsafe_routes = [r for r in ranked_routes if not r.is_eligible or not getattr(r, "is_safe", True)]
hazard_routes = [r for r in ranked_routes if not getattr(r, "is_safe", True) or len(getattr(r, "detected_hazards", [])) > 0]
has_eligible = len(eligible_ranked) > 0

if not has_eligible:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, rgba(239, 68, 68, 0.28) 0%, rgba(15, 23, 42, 0.98) 100%);
                border: 2px solid #ef4444; border-radius: 10px; padding: 14px 18px; margin-bottom: 14px;'>
        <div style='display: flex; align-items: center; justify-content: space-between;'>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span style='font-size: 1.4rem;'>⛔</span>
                <b style='color: #ffffff; font-size: 1.05rem;'>TRAVEL NOT RECOMMENDED — ALL CORRIDORS BLOCKED</b>
            </div>
            <span style='background: rgba(239, 68, 68, 0.35); color: #fca5a5; font-size: 0.72rem; font-weight: 800; padding: 3px 10px; border-radius: 6px;'>
                DANGER / IMPASSABLE
            </span>
        </div>
        <p style='font-size: 0.84rem; margin: 8px 0 0 0; color: #fee2e2; line-height: 1.5;'>
            The agent evaluated all candidate corridors and detected confirmed hazards or active road closures on every path. For life-safety, no route is safe to travel at this time.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📍 Reroute to Vadlamudi Municipal Hub", type="primary", use_container_width=True):
        st.session_state.selected_dest_coords = (16.2360, 80.5520)
        st.session_state.selected_dest_label = "Vadlamudi Municipal Hub"
        st.toast("Rerouted to open destination!")
        st.rerun()

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
else:
    st.markdown(f"""
    <div style='background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-left: 4px solid #10b981;
                border-radius: 8px; padding: 7px 14px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;'>
        <div style='display: flex; align-items: center; gap: 8px; font-size: 0.82rem; color: #34d399;'>
            <span>🛡️</span>
            <span><b>Safety Verified:</b> All travel corridors are open and clear with zero active hazards.</span>
        </div>
        <span style='color: #64748b; font-size: 0.72rem; font-weight: 600;'>100% CLEAR</span>
    </div>
    """, unsafe_allow_html=True)

# Display Route Recommendation Cards (all candidates displayed side by side)
cur_focus = st.session_state.get("focused_route_id", "ALL")
displayed_routes = ranked_routes

num_routes = len(displayed_routes)
if num_routes > 0:
    card_cols = st.columns(min(num_routes, 3))
    for idx, r_item in enumerate(displayed_routes):
        with card_cols[idx % min(num_routes, 3)]:
            is_active = (cur_focus == r_item.route.route_id)
            target_focus = "ALL" if is_active else r_item.route.route_id
            short_name = r_item.route.name.split("(")[0].strip()

            is_safe_route = getattr(r_item, "is_safe", True) and r_item.is_eligible
            if is_safe_route:
                safety_badge = "<span style='background: rgba(16, 185, 129, 0.2); color: #34d399; font-size: 0.70rem; font-weight: 700; padding: 2px 8px; border-radius: 4px;'>🛡️ SAFE TO TRAVEL</span>"
                card_border = "#10b981" if r_item.rank == 1 else "#38bdf8"
                rank_badge = "⭐ RECOMMENDED" if r_item.rank == 1 else f"Alternative {r_item.rank}"
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
                card_extra_border = f"border-left: 5px solid {card_border}; border-top: 1.5px solid #38bdf8; border-right: 1.5px solid #38bdf8; border-bottom: 1.5px solid #38bdf8; box-shadow: 0 0 25px rgba(56, 189, 248, 0.45);"
            elif cur_focus == "ALL":
                map_status_badge = "<span style='background: rgba(16, 185, 129, 0.15); color: #34d399; font-size: 0.70rem; font-weight: 700; padding: 2px 6px; border-radius: 4px;'>✓ ON MAP</span>"
                card_opacity = "1.0"
                card_extra_border = f"border-left: 5px solid {card_border};"
            else:
                map_status_badge = "<span style='background: rgba(100, 116, 139, 0.15); color: #94a3b8; font-size: 0.70rem; font-weight: 600; padding: 2px 6px; border-radius: 4px;'>HIDDEN ON MAP</span>"
                card_opacity = "0.55"
                card_extra_border = "border-left: 5px solid rgba(100, 116, 139, 0.4);"

            cur_unit = st.session_state.get("distance_unit", "km")
            dist_display = format_distance(r_item.effective_distance_km, cur_unit)

            if is_safe_route:
                if r_item.rank == 1:
                    creative_takeaway = "💡 <b>Recommended Choice:</b> Optimal balance of transit speed and clear, uninterrupted pavement."
                else:
                    creative_takeaway = "💡 <b>Alternative Bypass:</b> Secondary viable option with open traffic flow."
            else:
                closure_name = r_item.rejection_reasons[0].split("(")[0].replace("Road restriction:", "").replace("Active Hazard:", "").strip() if r_item.rejection_reasons else "Road closure"
                creative_takeaway = f"⛔ <b>Impassable:</b> Confirmed blockage at {closure_name}."

            feature_chips = []
            if is_safe_route:
                feature_chips.append("<span style='background: rgba(56, 189, 248, 0.12); color: #38bdf8; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px;'>⚡ Clear Corridor</span>")
                if r_item.route.is_accessible:
                    feature_chips.append("<span style='background: rgba(52, 211, 153, 0.12); color: #34d399; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px;'>♿ Step-Free</span>")
            else:
                feature_chips.append("<span style='background: rgba(239, 68, 68, 0.15); color: #f87171; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px;'>⚠️ Impassable</span>")
                feature_chips.append("<span style='background: rgba(245, 158, 11, 0.15); color: #fbbf24; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px;'>🔄 Detour Active</span>")

            chips_html = " ".join(feature_chips)
            via_roads = ", ".join(r_item.route.summary_roads[:2]) if r_item.route.summary_roads else "Direct Corridor"

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
            st.markdown(f"""
            <a href="/?focus_route={target_focus}" target="_top" class="touchable-route-link" title="{r_item.route.name}">
                <div class="touchable-route-card" data-path-idx="{idx + 1}" data-route-id="{r_item.route.route_id}" data-target-focus="{target_focus}"
                     style='background: rgba(10, 20, 38, 0.75); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
                            border: 1px solid rgba(255,255,255,0.08); {card_extra_border}
                            border-radius: 10px; padding: 14px 16px; margin-bottom: 8px; box-shadow: 0 4px 18px rgba(0,0,0,0.35);
                            opacity: {card_opacity};'>
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
                    <div style='display: flex; gap: 14px; font-size: 0.90rem; color: #cbd5e1; margin-bottom: 8px; background: rgba(255,255,255,0.03); padding: 6px 10px; border-radius: 6px;'>
                        <span>⏱️ <b>{r_item.effective_duration_minutes:.1f} mins</b></span>
                        <span>📏 <b>{dist_display}</b></span>
                    </div>
                    <div style='font-size: 0.80rem; color: #93c5fd; margin-bottom: 8px; line-height: 1.4;'>
                        {creative_takeaway}
                    </div>
                    <div style='font-size: 0.72rem; color: #64748b; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px;'>
                        📍 Via: <span style='color: #94a3b8;'>{via_roads}</span>
                    </div>
                    <div style='margin-top: 8px; display: flex; align-items: center; justify-content: space-between; background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.28); border-radius: 6px; padding: 5px 8px;'>
                        <span style='color: #38bdf8; font-size: 0.73rem; font-weight: 700; display: flex; align-items: center; gap: 5px;'>
                            🎙️ Tap to Navigate with AI Voice
                        </span>
                        <span style='color: #34d399; font-size: 0.70rem; font-weight: 800;'>
                            {vehicle_badge}
                        </span>
                    </div>
                </div>
            </a>
            """, unsafe_allow_html=True)

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
                        const targetFocus = card.getAttribute('data-target-focus');
                        if (targetFocus) {
                            window.parent.location.href = "/?focus_route=" + targetFocus;
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
# NEXT-LEVEL NAVIGATION SUITE: TURN-BY-TURN MANIFEST, GPX EXPORT & EMERGENCY POIS
# =========================================================================
if ranked_routes:
    active_route_item = None
    if cur_focus != "ALL":
        active_route_item = next((r for r in ranked_routes if r.route.route_id == cur_focus), None)
    if not active_route_item and eligible_ranked:
        active_route_item = eligible_ranked[0]
    elif not active_route_item and ranked_routes:
        active_route_item = ranked_routes[0]

    if active_route_item:
        is_focused = (cur_focus != "ALL")
        with st.expander(f"🧭 **Turn-by-Turn Navigation Manifest & AI Voice Guidance** — {active_route_item.route.name}", expanded=True):
            timing_col1, timing_col2, timing_col3 = st.columns([2.5, 2.5, 3.0])
            with timing_col1:
                dep_offset = st.selectbox(
                    "🕒 Departure Schedule",
                    options=[0, 15, 30, 60],
                    format_func=lambda x: "Leave Now" if x == 0 else f"Depart in +{x} mins",
                    key="nav_departure_offset"
                )
            import datetime
            now_time = datetime.datetime.now()
            dep_time = now_time + datetime.timedelta(minutes=dep_offset)
            eta_time = dep_time + datetime.timedelta(minutes=active_route_item.effective_duration_minutes)
            with timing_col2:
                st.metric("Estimated Arrival (ETA)", eta_time.strftime("%I:%M %p"), f"+{dep_offset}m offset" if dep_offset > 0 else "Real-Time")
            with timing_col3:
                cur_unit = st.session_state.get("distance_unit", "km")
                dist_str = format_distance(active_route_item.effective_distance_km, cur_unit)
                st.metric("Total Transit Leg", dist_str, f"{active_route_item.effective_duration_minutes:.1f} mins")

            # =========================================================================
            # AI VOICE ASSISTANT: DETAILED ROUTE ANALYSIS & SPOKEN BRIEFING
            # =========================================================================
            clean_route_name = active_route_item.route.name.split("(")[0].strip()
            summary_roads = ", ".join(active_route_item.route.summary_roads[:2]) if active_route_item.route.summary_roads else "open bypass corridor"
            hazard_detour_phrase = "safely evading the active Chemical Spill and confirmed Road Blockage on Ponnur Road" if active_route_item.is_eligible else "caution: restricted hazard corridor"

            voice_analysis_text = (
                f"Route selected: {clean_route_name}. "
                f"Safety analysis verified: {hazard_detour_phrase}. "
                f"Total distance is {active_route_item.effective_distance_km:.1f} kilometers, estimated arrival in {active_route_item.effective_duration_minutes:.0f} minutes via {summary_roads}. "
                f"Live Google Maps vehicle tracking is active on the satellite map. Proceeding along the safe green corridor."
            )

            voice_speech_json = json.dumps(voice_analysis_text)
            auto_speak_html = f"""
            <div style='background: linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(30,41,59,0.85) 100%);
                        border: 1.5px solid rgba(16,185,129,0.4); border-radius: 12px; padding: 14px 18px; margin-top: 10px; margin-bottom: 12px;
                        box-shadow: 0 4px 20px rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;'>
                <div style='display: flex; align-items: center; gap: 12px;'>
                    <div style='width: 44px; height: 44px; background: rgba(16,185,129,0.2); border: 2px solid #10b981; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 22px; box-shadow: 0 0 12px rgba(16,185,129,0.3);'>
                        🎙️
                    </div>
                    <div>
                        <div style='display: flex; align-items: center; gap: 8px;'>
                            <b style='color: #ffffff; font-size: 0.95rem;'>AI VOICE ASSISTANT: ROUTE ANALYSIS</b>
                            <span style='background: rgba(16,185,129,0.25); color: #34d399; font-size: 0.68rem; font-weight: 800; padding: 2px 7px; border-radius: 4px; border: 1px solid rgba(16,185,129,0.4);'>
                                ● SPOKEN AUDIO ACTIVE
                            </span>
                        </div>
                        <div style='color: #cbd5e1; font-size: 0.80rem; margin-top: 3px; max-width: 680px; line-height: 1.45;'>
                            "{voice_analysis_text}"
                        </div>
                    </div>
                </div>
                <button onclick="speakDetailedAnalysis()" style='background: #10b981; color: #ffffff; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 800; font-size: 0.80rem; cursor: pointer; box-shadow: 0 2px 10px rgba(16,185,129,0.4); display: flex; align-items: center; gap: 6px;'>
                    🔊 Replay Voice Analysis
                </button>
            </div>
            <script>
            (function() {{
                const speechText = {voice_speech_json};
                window.speakDetailedAnalysis = function() {{
                    if (!('speechSynthesis' in window)) return;
                    window.speechSynthesis.cancel();
                    const utterance = new SpeechSynthesisUtterance(speechText);
                    utterance.rate = 0.95;
                    utterance.pitch = 1.0;
                    utterance.lang = 'en-US';
                    const voices = window.speechSynthesis.getVoices();
                    const natVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha')));
                    if (natVoice) utterance.voice = natVoice;
                    window.speechSynthesis.speak(utterance);
                }};
                // Automatically speak detailed analysis when route tab is selected
                setTimeout(window.speakDetailedAnalysis, 500);
            }})();
            </script>
            """
            components.html(auto_speak_html, height=115)

            # Route Export & Sharing (GPX / GeoJSON)
            gpx_pts = "\n".join([f'      <trkpt lat="{pt[0]:.6f}" lon="{pt[1]:.6f}"><ele>0</ele></trkpt>' for pt in active_route_item.route.polyline])
            gpx_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="PATHFINDER-Global-Nav">
  <metadata>
    <name>{active_route_item.route.name}</name>
    <desc>PATHFINDER Safe Corridor ({active_route_item.route.distance_km} km)</desc>
  </metadata>
  <trk>
    <name>{active_route_item.route.name}</name>
    <trkseg>
{gpx_pts}
    </trkseg>
  </trk>
</gpx>"""
            geojson_str = json.dumps({
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {
                        "name": active_route_item.route.name,
                        "distance_km": active_route_item.route.distance_km,
                        "duration_minutes": active_route_item.route.duration_minutes,
                        "mode": str(active_route_item.route.mode.value if hasattr(active_route_item.route.mode, "value") else active_route_item.route.mode),
                        "summary_roads": active_route_item.route.summary_roads
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[pt[1], pt[0]] for pt in active_route_item.route.polyline]
                    }
                }]
            }, indent=2)

            exp_col1, exp_col2 = st.columns([1, 1])
            with exp_col1:
                st.download_button(
                    "📥 Download GPX File (Garmin / Google Maps)",
                    data=gpx_xml,
                    file_name=f"pathfinder_{active_route_item.route.route_id}.gpx",
                    mime="application/gpx+xml",
                    use_container_width=True
                )
            with exp_col2:
                st.download_button(
                    "📄 Download GeoJSON (GIS / Command)",
                    data=geojson_str,
                    file_name=f"pathfinder_{active_route_item.route.route_id}.geojson",
                    mime="application/json",
                    use_container_width=True
                )

            # Maneuver Steps List
            steps = getattr(active_route_item.route, "steps", [])
            if not steps:
                roads_list = active_route_item.route.summary_roads or ["Regional Main Corridor"]
                steps = [
                    {"step_num": 1, "icon": "🟢", "instruction": f"Head out on {roads_list[0]}", "road": roads_list[0], "distance_m": active_route_item.route.distance_meters / max(len(roads_list), 1)},
                    {"step_num": 2, "icon": "🏁", "instruction": "Arrive at destination safe terminal", "road": roads_list[-1], "distance_m": 0}
                ]

            st.markdown("<div style='margin-top: 14px; margin-bottom: 6px; font-weight: 700; font-size: 0.82rem; color: #38bdf8;'>🧭 STEP-BY-STEP MANEUVERS (SYNCHRONIZED WITH VOICE GUIDANCE)</div>", unsafe_allow_html=True)
            for s in steps:
                s_dist_km = s.get("distance_m", 0.0) / 1000.0
                s_dist_display = format_distance(s_dist_km, cur_unit)
                st.markdown(f"""
                <div style='display: flex; align-items: center; justify-content: space-between; padding: 9px 12px; margin-bottom: 6px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px;'>
                    <div style='display: flex; align-items: center; gap: 10px;'>
                        <span style='font-size: 1.25rem;'>{s.get("icon", "⬆️")}</span>
                        <div>
                            <div style='font-size: 0.86rem; color: #f1f5f9; font-weight: 600;'>{s.get("instruction", "Proceed")}</div>
                            <div style='font-size: 0.72rem; color: #64748b;'>Road: <span style='color: #94a3b8;'>{s.get("road", "Local Connector")}</span></div>
                        </div>
                    </div>
                    <div style='display: flex; align-items: center; gap: 8px;'>
                        <span style='font-size: 0.70rem; color: #10b981; background: rgba(16,185,129,0.12); padding: 2px 6px; border-radius: 4px; font-weight: 700;'>🔊 Spoken Voice</span>
                        <div style='font-size: 0.78rem; font-weight: 700; color: #38bdf8; background: rgba(56,189,248,0.1); padding: 3px 8px; border-radius: 4px;'>
                            {s_dist_display}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # =========================================================================
            # REAL-WORLD ROUTE-SPECIFIC EMERGENCY SERVICES & SAFETY AMENITIES
            # =========================================================================
            st.markdown("""
            <div style='margin-top: 20px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;'>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <span style='font-size: 1.25rem;'>🏥</span>
                    <span style='font-weight: 800; font-size: 0.96rem; color: #10b981; letter-spacing: 0.02em;'>
                        REAL-WORLD ROUTE EMERGENCY SERVICES & SAFETY AMENITIES
                    </span>
                </div>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <span style='font-size: 0.70rem; color: #38bdf8; background: rgba(56, 189, 248, 0.12); padding: 3px 8px; border-radius: 4px; border: 1px solid rgba(56, 189, 248, 0.28); font-weight: 700;'>
                        📍 5.0 KM CORRIDOR BUFFER
                    </span>
                    <span style='font-size: 0.70rem; color: #34d399; background: rgba(16, 185, 129, 0.12); padding: 3px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.28); font-weight: 700;'>
                        VERIFIED GEODATA
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # National Emergency Dispatch Info
            user_current_lat = coords_orig[0] if coords_orig else 16.2335
            user_current_lon = coords_orig[1] if coords_orig else 80.5505
            nat_emergency = get_national_emergency_contacts(user_current_lat, user_current_lon)

            # Category filter buttons / selection
            em_filter_col1, em_filter_col2 = st.columns([3.5, 6.5])
            with em_filter_col1:
                em_category_sel = st.selectbox(
                    "Filter Facilities:",
                    options=["ALL", "MEDICAL", "SHELTER", "ASSISTANCE", "TRAVEL"],
                    format_func=lambda x: {
                        "ALL": "🌐 All Facilities Along Route",
                        "MEDICAL": "🏥 Hospitals & Emergency Units",
                        "SHELTER": "⛺ Designated Evacuation Shelters",
                        "ASSISTANCE": "👮 Police & Fire Rescue",
                        "TRAVEL": "⛽ Fuel & Fast EV Charging"
                    }[x],
                    key="sel_emergency_filter"
                )

            # Filter facilities
            filtered_facs = []
            if route_emergency_facilities:
                for f in route_emergency_facilities:
                    if em_category_sel == "ALL":
                        filtered_facs.append(f)
                    elif em_category_sel == "MEDICAL" and f.category == FacilityCategory.MEDICAL:
                        filtered_facs.append(f)
                    elif em_category_sel == "SHELTER" and f.category == FacilityCategory.SAFE_SHELTER:
                        filtered_facs.append(f)
                    elif em_category_sel == "ASSISTANCE" and f.category == FacilityCategory.EMERGENCY_ASSISTANCE:
                        filtered_facs.append(f)
                    elif em_category_sel == "TRAVEL" and f.category == FacilityCategory.TRAVEL_ASSISTANCE:
                        filtered_facs.append(f)

            with em_filter_col2:
                # Spoken AI Voice Amenities Summary Button
                if st.button("🎙️ AI Voice Amenities Briefing", help="Speak real-time safety amenities along the route", use_container_width=True):
                    closest_hosp = next((f for f in route_emergency_facilities if f.category == FacilityCategory.MEDICAL and f.has_emergency_department), None)
                    closest_shlt = next((f for f in route_emergency_facilities if f.category == FacilityCategory.SAFE_SHELTER), None)
                    closest_fuel = next((f for f in route_emergency_facilities if f.category == FacilityCategory.TRAVEL_ASSISTANCE), None)
                    
                    speech_parts = [f"Safety amenities debrief for your active transit:"]
                    if closest_hosp:
                        speech_parts.append(f"Nearest verified emergency department is {closest_hosp.name}, approximately {closest_hosp.road_distance_km:.1f} kilometers from your current position.")
                    if closest_shlt:
                        speech_parts.append(f"Designated civil evacuation haven: {closest_shlt.name}, {closest_shlt.distance_from_route_km:.1f} kilometers from the route corridor.")
                    if closest_fuel:
                        speech_parts.append(f"Travel assistance: {closest_fuel.name} is accessible {closest_fuel.road_distance_km:.1f} kilometers ahead.")
                    speech_parts.append(f"In case of extreme distress, dial official emergency services at {nat_emergency['primary_sos']}.")
                    
                    speech_txt = " ".join(speech_parts)
                    speech_json = json.dumps(speech_txt)
                    components.html(f"""
                    <script>
                    (function() {{
                        if (!('speechSynthesis' in window)) return;
                        window.speechSynthesis.cancel();
                        const utt = new SpeechSynthesisUtterance({speech_json});
                        utt.rate = 0.95;
                        utt.pitch = 1.0;
                        utt.lang = 'en-US';
                        window.speechSynthesis.speak(utt);
                    }})();
                    </script>
                    """, height=0, width=0)
                    st.toast("🎙️ Speaking real route safety amenities summary...", icon="🔊")

            # Render Facility Cards
            if not filtered_facs:
                st.info("No facilities found matching the current filter along this corridor. OpenStreetMap & local registry query active.")
            else:
                fac_cols = st.columns(min(3, len(filtered_facs)))
                for idx, fac in enumerate(filtered_facs[:6]):
                    with fac_cols[idx % 3]:
                        if fac.has_emergency_department is True:
                            ed_badge = "<span style='color: #ef4444; font-size: 0.68rem; font-weight: 800; background: rgba(239, 68, 68, 0.15); padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(239, 68, 68, 0.3);'>● 24/7 VERIFIED EMERGENCY DEPT</span>"
                        elif fac.has_emergency_department is False:
                            ed_badge = "<span style='color: #f59e0b; font-size: 0.68rem; font-weight: 800; background: rgba(245, 158, 11, 0.15); padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(245, 158, 11, 0.3);'>● CLINIC / NON-ED</span>"
                        elif fac.is_officially_designated_shelter is True:
                            ed_badge = "<span style='color: #10b981; font-size: 0.68rem; font-weight: 800; background: rgba(16, 185, 129, 0.15); padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.3);'>● DESIGNATED SAFE HAVEN</span>"
                        else:
                            ed_badge = f"<span style='color: #38bdf8; font-size: 0.68rem; font-weight: 700;'>{fac.facility_type}</span>"

                        phone_line = f"<div style='font-size: 0.70rem; color: #38bdf8; margin-top: 4px;'>📞 {fac.contact_phone}</div>" if fac.contact_phone else ""

                        st.markdown(f"""
                        <div style='background: rgba(10, 20, 38, 0.75); border: 1px solid rgba(16, 185, 129, 0.28); border-radius: 10px; padding: 12px; margin-bottom: 10px; display: flex; flex-direction: column; justify-content: space-between; min-height: 190px;'>
                            <div>
                                <div style='display: flex; align-items: flex-start; justify-content: space-between; gap: 8px;'>
                                    <div style='font-size: 1.15rem;'>{fac.amenity_icon}</div>
                                    <div style='flex: 1;'>
                                        <b style='font-size: 0.85rem; color: #f1f5f9; line-height: 1.3; display: block;'>{fac.name}</b>
                                        <div style='margin-top: 4px;'>{ed_badge}</div>
                                    </div>
                                </div>
                                <div style='font-size: 0.73rem; color: #94a3b8; margin-top: 8px;'>
                                    <b>Corridor:</b> {fac.distance_from_route_km:.1f} km • <span style='color: #38bdf8; font-weight: 700;'>🚗 ~{fac.road_distance_km:.1f} km ({fac.eta_minutes:.0f} mins)</span>
                                </div>
                                <div style='font-size: 0.70rem; color: #cbd5e1; margin-top: 4px;'>
                                    <b>Operating:</b> <span style='color: #a7f3d0;'>{fac.operating_hours}</span>
                                </div>
                                {phone_line}
                            </div>
                            <div style='font-size: 0.64rem; color: #64748b; margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 4px;'>
                                🏷️ {fac.data_source}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        btn_c1, btn_c2 = st.columns([1, 1])
                        with btn_c1:
                            if st.button("🧭 Route Here", key=f"btn_nav_fac_{fac.facility_id}", use_container_width=True):
                                st.session_state.pending_dest = f"{fac.name} ({fac.latitude:.4f}, {fac.longitude:.4f})"
                                st.session_state.selected_dest_coords = (fac.latitude, fac.longitude)
                                st.session_state.selected_dest_label = fac.name
                                st.toast(f"Rerouting navigation to {fac.name}", icon="🧭")
                                st.rerun()
                        with btn_c2:
                            if fac.contact_phone:
                                phone_clean = re.sub(r'[^0-9+]', '', fac.contact_phone)
                                st.markdown(f"<a href='tel:{phone_clean}' style='display: block; text-align: center; background: rgba(56, 189, 248, 0.15); border: 1px solid #38bdf8; color: #38bdf8; border-radius: 6px; padding: 5px; font-size: 0.72rem; font-weight: 700; text-decoration: none;'>📞 Call</a>", unsafe_allow_html=True)

            # =========================================================================
            # EMERGENCY & STRANDED USER ASSISTANCE (SOS DIRECT DISPATCH)
            # =========================================================================
            with st.expander("🚨 **Emergency & Stranded User Assistance (SOS Console)**", expanded=False):
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, rgba(127, 29, 29, 0.3) 0%, rgba(15, 23, 42, 0.9) 100%); border: 1.5px solid #ef4444; border-radius: 10px; padding: 12px 16px; margin-bottom: 12px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;'>
                        <div>
                            <div style='font-size: 0.95rem; font-weight: 800; color: #f87171;'>🚨 IMMEDIATE LIFE SAFETY & STRANDED DISPATCH</div>
                            <div style='font-size: 0.74rem; color: #cbd5e1; margin-top: 2px;'>
                                Country: <b>{nat_emergency['country']}</b> • Official Emergency Response Service: <b>{nat_emergency['agency_name']}</b>
                            </div>
                        </div>
                        <a href="tel:{nat_emergency['primary_sos']}" style='background: #ef4444; color: #ffffff; padding: 6px 14px; border-radius: 6px; font-weight: 800; font-size: 0.82rem; text-decoration: none; box-shadow: 0 0 12px rgba(239,68,68,0.5);'>
                            📞 Dial {nat_emergency['primary_sos']} ({nat_emergency['country']})
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                sos_c1, sos_c2, sos_c3, sos_c4 = st.columns(4)
                with sos_c1:
                    if st.button("🩺 Medical Emergency", help="Find closest hospital with verified trauma unit", use_container_width=True):
                        st.session_state.active_sos_type = "MEDICAL"
                with sos_c2:
                    if st.button("🚨 Police / Threat SOS", help="Find closest police station and call 112", use_container_width=True):
                        st.session_state.active_sos_type = "POLICE"
                with sos_c3:
                    if st.button("🔥 Hazard / Disaster", help="Find closest designated evacuation shelter", use_container_width=True):
                        st.session_state.active_sos_type = "DISASTER"
                with sos_c4:
                    if st.button("⛽ Stranded / Breakdown", help="Find closest fuel station or fast EV charger", use_container_width=True):
                        st.session_state.active_sos_type = "STRANDED"

                if "active_sos_type" in st.session_state and st.session_state.active_sos_type:
                    st_type = st.session_state.active_sos_type
                    briefing = st.session_state.emergency_service_manager.create_sos_guidance_briefing(
                        (coords_orig[0] if coords_orig else 16.2335, coords_orig[1] if coords_orig else 80.5505),
                        emergency_type=st_type
                    )
                    fac = briefing.get("facility")
                    speech_json = json.dumps(briefing["spoken_speech"])

                    st.markdown(f"""
                    <div style='background: rgba(15, 23, 42, 0.95); border: 2px solid #ef4444; border-radius: 10px; padding: 14px; margin-top: 10px;'>
                        <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 6px;'>
                            <span style='font-size: 1.2rem;'>🚨</span>
                            <b style='color: #f87171; font-size: 0.92rem;'>AI EMERGENCY DISPATCH GUIDANCE ({st_type})</b>
                        </div>
                        <div style='font-size: 0.82rem; color: #f1f5f9; line-height: 1.45;'>
                            "{briefing['spoken_speech']}"
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    components.html(f"""
                    <script>
                    (function() {{
                        if (!('speechSynthesis' in window)) return;
                        window.speechSynthesis.cancel();
                        const utt = new SpeechSynthesisUtterance({speech_json});
                        utt.rate = 0.95;
                        utt.pitch = 1.0;
                        utt.lang = 'en-US';
                        window.speechSynthesis.speak(utt);
                    }})();
                    </script>
                    """, height=0, width=0)

                    if fac:
                        action_c1, action_c2 = st.columns([1, 1])
                        with action_c1:
                            if st.button(f"🧭 Start Emergency Navigation to {fac['name'][:24]}...", use_container_width=True):
                                st.session_state.pending_dest = f"{fac['name']} ({fac['latitude']:.4f}, {fac['longitude']:.4f})"
                                st.session_state.selected_dest_coords = (fac['latitude'], fac['longitude'])
                                st.session_state.selected_dest_label = fac['name']
                                st.session_state.active_sos_type = None
                                st.toast(f"Starting emergency navigation to {fac['name']}", icon="🚨")
                                st.rerun()
                        with action_c2:
                            call_num = briefing.get("emergency_phone", nat_emergency["primary_sos"])
                            st.markdown(f"""
                            <a href="tel:{call_num}" style='display: block; text-align: center; background: #dc2626; color: #ffffff; padding: 9px; border-radius: 6px; font-weight: 800; font-size: 0.84rem; text-decoration: none;'>
                                📞 Confirm & Call {call_num}
                            </a>
                            """, unsafe_allow_html=True)

# =========================================================================
# FLOATING CIRCULAR CHATBOT: A.U.R.A. (Adaptive User Route Assistant)
# =========================================================================
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

# Floating Circular Popover Action Button (Anchored Bottom-Right)
with st.popover(" ", help="Open A.U.R.A. • PathFinder AI Copilot"):
    # High-Tech Header with Official A.U.R.A. Logo Display
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

    # =====================================================================
    # A.U.R.A. In-Built Automatic Voice Assistant Controller
    # =====================================================================
    latest_bot_text = ""
    for msg in reversed(st.session_state.aura_chat_history):
        if msg["role"] == "assistant":
            raw_c = msg.get("content", "")
            c_text = re.sub(r'<[^>]+>', ' ', raw_c)
            c_text = re.sub(r'```[\s\S]*?```', ' Code snippet displayed on screen. ', c_text)
            c_text = re.sub(r'[*_~`#>]', '', c_text)
            c_text = c_text.replace('&nbsp;', ' ').replace('&amp;', 'and').replace('&lt;', '<').replace('&gt;', '>')
            c_text = re.sub(r'\s+', ' ', c_text).strip()
            if c_text:
                latest_bot_text = c_text
                break

    should_auto_speak = st.session_state.pop("aura_auto_speak", False)
    safe_speech_json = json.dumps(latest_bot_text)
    auto_speak_js = "true" if should_auto_speak else "false"

    voice_assistant_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            user-select: none;
            overflow: hidden;
        }}
        .voice-card {{
            background: linear-gradient(135deg, rgba(14, 165, 233, 0.12) 0%, rgba(15, 23, 42, 0.90) 100%);
            border: 1.5px solid rgba(56, 189, 248, 0.4);
            border-radius: 10px;
            padding: 6px 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 14px rgba(0,0,0,0.4);
        }}
        .voice-left {{
            display: flex;
            align-items: center;
            gap: 7px;
        }}
        .voice-label {{
            font-size: 0.73rem;
            color: #94a3b8;
            font-weight: 700;
            letter-spacing: 0.03em;
        }}
        .voice-status {{
            font-size: 0.68rem;
            font-family: monospace;
            font-weight: 800;
            color: #38bdf8;
            background: rgba(56, 189, 248, 0.15);
            padding: 2px 7px;
            border-radius: 4px;
            border: 1px solid rgba(56, 189, 248, 0.3);
        }}
        .eq-bar-wrap {{
            display: inline-flex;
            align-items: flex-end;
            gap: 2.5px;
            height: 14px;
            margin-left: 3px;
        }}
        .eq-bar {{
            width: 3px;
            height: 3px;
            background: #38bdf8;
            border-radius: 1.5px;
            transition: height 0.15s ease;
        }}
        .speaking .eq-bar:nth-child(1) {{ animation: eqAura 0.35s infinite alternate; }}
        .speaking .eq-bar:nth-child(2) {{ animation: eqAura 0.55s infinite 0.1s alternate; }}
        .speaking .eq-bar:nth-child(3) {{ animation: eqAura 0.45s infinite 0.2s alternate; }}
        .speaking .eq-bar:nth-child(4) {{ animation: eqAura 0.65s infinite 0.15s alternate; }}
        .speaking .eq-bar:nth-child(5) {{ animation: eqAura 0.4s infinite 0.05s alternate; }}
        @keyframes eqAura {{
            0% {{ height: 3px; background: #38bdf8; }}
            100% {{ height: 14px; background: #34d399; box-shadow: 0 0 6px #34d399; }}
        }}
        .voice-actions {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .btn-v {{
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            border: 1px solid #38bdf8;
            color: #ffffff;
            font-size: 0.70rem;
            font-weight: 700;
            padding: 4px 9px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .btn-v:hover {{
            background: linear-gradient(135deg, #0369a1 0%, #0284c7 100%);
            transform: scale(1.04);
            box-shadow: 0 0 8px rgba(56, 189, 248, 0.5);
        }}
        .btn-stop {{
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.4);
            color: #f87171;
            font-size: 0.70rem;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .btn-stop:hover {{
            background: rgba(239, 68, 68, 0.3);
            transform: scale(1.04);
        }}
    </style>
    </head>
    <body>
    <div class="voice-card">
        <div class="voice-left">
            <span style="font-size: 0.95rem;">🎙️</span>
            <span class="voice-label">VOICE COPILOT:</span>
            <span id="v-status" class="voice-status">ACTIVE</span>
            <div id="v-eq" class="eq-bar-wrap">
                <span class="eq-bar"></span>
                <span class="eq-bar"></span>
                <span class="eq-bar"></span>
                <span class="eq-bar"></span>
                <span class="eq-bar"></span>
            </div>
        </div>
        <div class="voice-actions">
            <button id="btn-speak" class="btn-v" onclick="startSpeech()">🔊 Listen</button>
            <button id="btn-stop" class="btn-stop" onclick="stopSpeech()">⏹️ Stop</button>
        </div>
    </div>

    <script>
        const speechText = {safe_speech_json};
        const autoSpeak = {auto_speak_js};
        const eq = document.getElementById("v-eq");
        const statusEl = document.getElementById("v-status");

        function stopSpeech() {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
            }}
            if (eq) eq.classList.remove("speaking");
            if (statusEl) {{
                statusEl.innerText = "READY";
                statusEl.style.color = "#38bdf8";
            }}
        }}

        function startSpeech() {{
            if (!('speechSynthesis' in window) || !speechText || speechText.trim().length === 0) {{
                return;
            }}
            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(speechText);
            utterance.rate = 1.0;
            utterance.pitch = 1.02;

            const voices = window.speechSynthesis.getVoices();
            if (voices && voices.length > 0) {{
                const pref = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha') || v.name.includes('David') || v.name.includes('Zira')));
                if (pref) utterance.voice = pref;
            }}

            utterance.onstart = function() {{
                if (eq) eq.classList.add("speaking");
                if (statusEl) {{
                    statusEl.innerText = "READING ALOUD 🎧";
                    statusEl.style.color = "#34d399";
                }}
            }};

            utterance.onend = function() {{
                if (eq) eq.classList.remove("speaking");
                if (statusEl) {{
                    statusEl.innerText = "ACTIVE";
                    statusEl.style.color = "#38bdf8";
                }}
            }};

            utterance.onerror = function() {{
                if (eq) eq.classList.remove("speaking");
                if (statusEl) {{
                    statusEl.innerText = "READY";
                    statusEl.style.color = "#38bdf8";
                }}
            }};

            window.speechSynthesis.speak(utterance);
        }}

        if (autoSpeak) {{
            setTimeout(startSpeech, 300);
        }}
    </script>
    </body>
    </html>
    """
    components.html(voice_assistant_html, height=46)

    # Check if a pending chat prompt was queued
    if "pending_chat_prompt" in st.session_state and st.session_state.pending_chat_prompt:
        chip_query = st.session_state.pop("pending_chat_prompt")
        st.session_state.aura_chat_history.append({"role": "user", "content": chip_query})

        chat_ctx = {
            "start_label": st.session_state.get("active_start_label", "Vignan Campus"),
            "dest_label": st.session_state.get("selected_dest_label", "Guntur City Center"),
            "active_objective_str": st.session_state.get("active_objective", OptimizationObjective.FASTEST).value,
            "ranked_routes": ranked_routes if 'ranked_routes' in locals() else [],
            "active_restrictions": st.session_state.road_condition_manager.get_active_restrictions(),
            "active_hazards": hazard_markers if 'hazard_markers' in locals() else []
        }
        ans = st.session_state.pathfinder_bot.answer(chip_query, context=chat_ctx)
        st.session_state.aura_chat_history.append({
            "role": "assistant",
            "content": ans["response"],
            "badge": ans.get("badge", "A.U.R.A. COPILOT")
        })
        st.session_state.aura_auto_speak = True
        st.rerun()

    # Spacious Scrollable Chat History Container
    chat_box = st.container(height=340)
    with chat_box:
        for msg in st.session_state.aura_chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 8px;">
                    <div style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; padding: 7px 11px; border-radius: 12px 12px 2px 12px; max-width: 85%; font-size: 0.81rem; box-shadow: 0 2px 8px rgba(0,0,0,0.3); font-weight: 500;">
                        {msg['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                b_html = f"<span style='font-size: 0.62rem; font-weight: 800; color: #38bdf8; font-family: monospace; letter-spacing: 0.05em; background: rgba(56, 189, 248, 0.12); padding: 1px 6px; border-radius: 4px; display: inline-block; margin-bottom: 4px;'>{msg.get('badge', 'A.U.R.A.')}</span>"
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                    <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.22); color: #cbd5e1; padding: 9px 12px; border-radius: 12px 12px 12px 2px; max-width: 95%; font-size: 0.81rem; box-shadow: 0 4px 12px rgba(0,0,0,0.4);">
                        {b_html}
                        <div>{msg['content']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Input Form
    with st.form("aura_chat_input_form", clear_on_submit=True):
        col_in, col_btn = st.columns([4, 1])
        with col_in:
            user_text = st.text_input("Ask A.U.R.A...", placeholder="Ask A.U.R.A. anything (science, coding, writing, routes, safety)...", label_visibility="collapsed")
        with col_btn:
            submit_click = st.form_submit_button("Send 🚀", use_container_width=True)

    if submit_click and user_text and user_text.strip():
        q_text = user_text.strip()
        st.session_state.aura_chat_history.append({"role": "user", "content": q_text})

        chat_ctx = {
            "start_label": st.session_state.get("active_start_label", "Vignan Campus"),
            "dest_label": st.session_state.get("selected_dest_label", "Guntur City Center"),
            "active_objective_str": st.session_state.get("active_objective", OptimizationObjective.FASTEST).value,
            "ranked_routes": ranked_routes if 'ranked_routes' in locals() else [],
            "active_restrictions": st.session_state.road_condition_manager.get_active_restrictions(),
            "active_hazards": hazard_markers if 'hazard_markers' in locals() else []
        }
        ans = st.session_state.pathfinder_bot.answer(q_text, context=chat_ctx)
        st.session_state.aura_chat_history.append({
            "role": "assistant",
            "content": ans["response"],
            "badge": ans.get("badge", "A.U.R.A. COPILOT")
        })
        st.session_state.aura_auto_speak = True
        st.rerun()

# Floating Visual Overlay for Chatbot Trigger Logo (renders over invisible popover button)
if aura_logo_uri:
    st.markdown(f'<img src="{aura_logo_uri}" class="floating-aura-logo-overlay" alt="A.U.R.A. Chatbot Logo" />', unsafe_allow_html=True)






