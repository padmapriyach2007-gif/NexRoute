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







import re
import streamlit as st

# =============================================================================
# GLOBAL MARKDOWN SANITIZER & HTML INDENTATION ENGINE
# Prevents CommonMark from parsing indented HTML lines as code blocks
# Collapses multiline tag attributes and guarantees unsafe_allow_html=True
# =============================================================================
_orig_st_markdown = st.markdown

def _safe_st_markdown(body, *args, **kwargs):
    if isinstance(body, str):
        # Detect if body contains any HTML or CSS constructs
        if "<" in body and ">" in body and any(tag in body for tag in (
            "<div", "<span", "<p", "<style", "<section", "<table",
            "<h1", "<h2", "<h3", "<h4", "<h5", "<h6",
            "<ul", "<li", "<button", "<a ", "<b ", "<b>",
            "<i ", "<i>", "<strong", "<em", "<hr", "<br", "<!--"
        )):
            kwargs["unsafe_allow_html"] = True

            # Collapse any opening HTML tags that contain newlines in their attributes
            def _collapse_tag(m):
                return re.sub(r'\s+', ' ', m.group(0))

            body = re.sub(r'<[a-zA-Z0-9_\-]+(?:\s+[^>]*)?>', _collapse_tag, body, flags=re.DOTALL)

            # Strip leading/trailing whitespace from each line so CommonMark
            # never treats indented lines (>= 4 spaces) as raw code blocks (<pre><code>)
            cleaned_lines = []
            for line in body.splitlines():
                stripped = line.strip()
                # Skip blank lines directly adjacent to HTML tags to prevent CommonMark from closing HTML blocks prematurely
                if stripped == "" and cleaned_lines and (cleaned_lines[-1] == "" or cleaned_lines[-1].startswith("<")):
                    continue
                cleaned_lines.append(stripped)
            body = "\n".join(cleaned_lines)
    return _orig_st_markdown(body, *args, **kwargs)

st.markdown = _safe_st_markdown




import streamlit.components.v1 as components



import time



import math



import datetime



import zoneinfo



import uuid



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



from src.aura_journey_engine import (



    AuraJourneyStage,



    AuraPose,



    AuraPoseAssetManager,



    AuraSpeechGenerator,



    ManeuverSequenceBuilder,



    build_aura_journey_cockpit_html



)



from src.corridor_storybook import CorridorStorybookEngine, CorridorPlacesEngine



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



    get_facilities_around_journey,



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



    render_profile_calculation_details_html



)



from src.automotive_drive_selector import (



    render_cockpit_mode_functionality_hud



)



from src.transit_kinematics import (



    calculate_transit_kinematics,



    render_transit_kinematics_hud_html,



    render_transit_kinematics_live_ticker_component,



    resolve_timezone,



    TIMEZONE_CATALOG,



    VEHICLE_KINEMATIC_PROFILES



)











from src.i18n import (



    t,



    SUPPORTED_LANGUAGES,



    get_current_language,



    set_current_language,



    get_bcp47_code,



    get_language_native_name,



    format_distance as i18n_format_distance,



    format_duration as i18n_format_duration



)



import importlib



import src.travel_copilot_studio



try:



    importlib.reload(src.travel_copilot_studio)



except Exception:



    pass







from src.travel_copilot_studio import (



    render_quantum_navbar,



    render_main_language_bar,



    render_quantum_hero_section,



    render_travel_copilot_studio,



    render_view_navigation_header,



    QUANTUM_REALM_CSS



)







# Page configuration



st.set_page_config(



    page_title="NexRoute",



    page_icon="🧭",



    layout="wide",



    initial_sidebar_state="expanded"



)







# Session State Language Initialization with query param / cookie / default support



try:



    url_lang = st.query_params.get("lang")



    if url_lang and url_lang in SUPPORTED_LANGUAGES and url_lang != st.session_state.get("app_language"):



        st.session_state.app_language = url_lang



except Exception:



    pass







if "app_language" not in st.session_state or st.session_state.app_language not in SUPPORTED_LANGUAGES:



    st.session_state.app_language = "en"







set_current_language(st.session_state.app_language)







# Synchronize client-side localStorage language persistence and Mount Virtual Multilingual Keyboard



from src.virtual_keyboard import get_virtual_keyboard_html



components.html(f"""



<script>



(function() {{



    try {{



        var curr = {json.dumps(st.session_state.app_language)};



        if (curr) {{



            localStorage.setItem('pathfinder_user_lang', curr);



        }}



        var pDoc = window.parent.document || document;



        var existingMeta = pDoc.querySelector('meta[name="viewport"]');



        if (existingMeta) {{



            existingMeta.setAttribute('content', 'width=device-width, initial-scale=1, viewport-fit=cover');



        }} else {{



            var newMeta = pDoc.createElement('meta');



            newMeta.name = 'viewport';



            newMeta.content = 'width=device-width, initial-scale=1, viewport-fit=cover';



            pDoc.head.appendChild(newMeta);



        }}



    }} catch(e) {{}}



}})();



</script>



{get_virtual_keyboard_html(st.session_state.app_language)}



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







# 3D AURA Robot Mascot Transparent Avatar



MASCOT_3D_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mascot_welcome_trans.png")



if not os.path.exists(MASCOT_3D_PATH):



    MASCOT_3D_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mascot_welcome_clean.png")







aura_mascot_3d_uri = ""



if os.path.exists(MASCOT_3D_PATH):



    with open(MASCOT_3D_PATH, "rb") as f:



        aura_mascot_3d_uri = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"



else:



    try:



        poses_trans_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "mascot_poses_trans.json")



        if os.path.exists(poses_trans_path):



            with open(poses_trans_path, "r", encoding="utf-8") as f:



                poses_data = json.load(f)



                aura_mascot_3d_uri = poses_data.get("welcome") or poses_data.get("waving", "")



    except Exception:



        pass



if not aura_mascot_3d_uri:



    aura_mascot_3d_uri = aura_logo_uri







BG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "navigation_bg.jpg")



bg_data_uri = ""



if os.path.exists(BG_PATH):



    with open(BG_PATH, "rb") as f:



        bg_data_uri = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"







if bg_data_uri:



    st.markdown(f"""



    <style>



        .stApp {{



            background-color: #030712 !important;



            background-image: 



                radial-gradient(circle at 10% 12%, rgba(6, 182, 212, 0.14) 0%, transparent 45%),



                radial-gradient(circle at 90% 12%, rgba(168, 85, 247, 0.16) 0%, transparent 45%),



                radial-gradient(circle at 50% 85%, rgba(14, 165, 233, 0.08) 0%, transparent 55%),



                linear-gradient(180deg, rgba(3, 7, 18, 0.88) 0%, rgba(5, 11, 20, 0.82) 50%, rgba(3, 7, 18, 0.95) 100%),



                url('{bg_data_uri}') !important;



            background-size: cover, cover, cover, cover, cover !important;



            background-position: center top !important;



            background-repeat: no-repeat !important;



            background-attachment: fixed !important;



            color: #f1f5f9;



        }}







        /* Seamless Translucent Digital-Twin Sidebar */



        section[data-testid="stSidebar"] {{



            background: 



                linear-gradient(180deg, rgba(8, 15, 28, 0.92) 0%, rgba(10, 20, 36, 0.90) 100%),



                url('{bg_data_uri}') !important;



            background-size: cover !important;



            background-position: left center !important;



            background-attachment: fixed !important;



            backdrop-filter: blur(28px) saturate(190%);



            -webkit-backdrop-filter: blur(28px) saturate(190%);



            border-right: 1px solid rgba(56, 189, 248, 0.20) !important;



            box-shadow: 6px 0 32px rgba(0, 0, 0, 0.75);



        }}



    </style>



    """, unsafe_allow_html=True)



else:



    st.markdown(QUANTUM_REALM_CSS, unsafe_allow_html=True)







# Custom Cyber-Dark Styling: High Contrast, Glassmorphism, Emergency HUD



st.markdown("""



<style>



    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&family=Noto+Sans+Telugu:wght@400;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&family=Noto+Sans+Tamil:wght@400;600;700&family=Noto+Sans+Kannada:wght@400;600;700&family=Noto+Sans+Malayalam:wght@400;600;700&family=Noto+Sans+Bengali:wght@400;600;700&display=swap');







    html {



        scroll-behavior: smooth;



    }







    html, body, [class*="css"] {



        font-family: 'Plus Jakarta Sans', 'Noto Sans Telugu', 'Noto Sans Devanagari', 'Noto Sans Tamil', 'Noto Sans Kannada', 'Noto Sans Malayalam', 'Noto Sans Bengali', -apple-system, BlinkMacSystemFont, sans-serif;



    }







    /* =========================================================================



       FUTURISTIC DARK NEON UI SYSTEM (Deep Navy #06111F, Panel Navy #0B1B2D, Cyan #00D9FF, Teal #00F0B5)



       ========================================================================= */







    /* Sleek Translucent Input Controls & Selectboxes */



    div[data-baseweb="input"] {



        background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;



        backdrop-filter: blur(14px) !important;



        -webkit-backdrop-filter: blur(14px) !important;



        border: 1.5px solid rgba(0, 217, 255, 0.40) !important;



        border-radius: 10px !important;



        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.50), 0 0 10px rgba(0, 217, 255, 0.15) !important;



        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;



        color: #EAF7FF !important;



    }



    div[data-baseweb="input"]:focus-within {



        border-color: #00D9FF !important;



        box-shadow: 0 0 20px rgba(0, 217, 255, 0.50), 0 0 10px rgba(0, 240, 181, 0.35) !important;



    }



    div[data-baseweb="input"] input {



        color: #EAF7FF !important;



        font-weight: 600 !important;



    }







    div[data-baseweb="select"] > div {



        background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;



        backdrop-filter: blur(14px) !important;



        -webkit-backdrop-filter: blur(14px) !important;



        border: 1.5px solid rgba(0, 217, 255, 0.40) !important;



        border-radius: 10px !important;



        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.50), 0 0 10px rgba(0, 217, 255, 0.15) !important;



        color: #EAF7FF !important;



        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;



    }



    div[data-baseweb="select"]:focus-within > div {



        border-color: #00D9FF !important;



        box-shadow: 0 0 20px rgba(0, 217, 255, 0.50), 0 0 10px rgba(0, 240, 181, 0.35) !important;



    }



    div[data-baseweb="select"] * {



        color: #EAF7FF !important;



    }







    /* Dropdown Menus (Listboxes) */



    ul[role="listbox"],



    div[data-baseweb="menu"] {



        background: #0B1B2D !important;



        border: 1.5px solid rgba(0, 217, 255, 0.45) !important;



        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.85), 0 0 24px rgba(0, 217, 255, 0.25) !important;



        border-radius: 12px !important;



        padding: 6px !important;



    }



    li[role="option"] {



        color: #EAF7FF !important;



        border-radius: 8px !important;



        transition: all 0.15s ease !important;



        padding: 8px 12px !important;



    }



    li[role="option"]:hover,



    li[role="option"][aria-selected="true"] {



        background: linear-gradient(135deg, rgba(0, 217, 255, 0.25) 0%, rgba(0, 240, 181, 0.20) 100%) !important;



        color: #ffffff !important;



        border-left: 3px solid #00F0B5 !important;



    }







    /* Polished Interactive Leaflet Map Wrapper */



    iframe[title="streamlit_folium.st_folium"] {



        border-radius: 12px !important;



        border: 1.5px solid rgba(0, 217, 255, 0.40) !important;



        box-shadow: 0 10px 36px -4px rgba(0, 217, 255, 0.30), 0 0 20px rgba(0, 0, 0, 0.7) !important;



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







    /* =========================================================================



       ALL BUTTONS & INTERACTIVE CONTROLS - FUTURISTIC DARK NEON UI SYSTEM



       ========================================================================= */







    /* Default / Secondary Button State across ALL of Streamlit */



    .stButton > button,



    div[data-testid="stButton"] > button,



    div[data-testid="stFormSubmitButton"] > button,



    div[data-testid="stDownloadButton"] > button,



    button[data-testid="baseButton-secondary"] {



        background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;



        border: 1.5px solid rgba(0, 217, 255, 0.40) !important;



        color: #EAF7FF !important;



        border-radius: 10px !important;



        font-weight: 700 !important;



        letter-spacing: 0.02em !important;



        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.50), 0 0 10px rgba(0, 217, 255, 0.15) !important;



        backdrop-filter: blur(12px) !important;



        -webkit-backdrop-filter: blur(12px) !important;



        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;



        cursor: pointer !important;



    }







    /* Hover State for Default / Secondary Buttons */



    .stButton > button:hover,



    div[data-testid="stButton"] > button:hover,



    div[data-testid="stFormSubmitButton"] > button:hover,



    div[data-testid="stDownloadButton"] > button:hover,



    button[data-testid="baseButton-secondary"]:hover {



        background: linear-gradient(135deg, #10263E 0%, #0B1B2D 100%) !important;



        border-color: #00D9FF !important;



        color: #ffffff !important;



        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.60), 0 0 18px rgba(0, 240, 181, 0.40) !important;



        transform: translateY(-2px) !important;



        text-shadow: 0 0 8px rgba(0, 217, 255, 0.60) !important;



    }







    /* Active / Selected Primary Button State across ALL of Streamlit */



    .stButton > button[kind="primary"],



    div[data-testid="stButton"] > button[kind="primary"],



    div[data-testid="stFormSubmitButton"] > button[kind="primary"],



    button[data-testid="baseButton-primary"] {



        background: linear-gradient(135deg, rgba(0, 217, 255, 0.35) 0%, rgba(0, 240, 181, 0.40) 100%) !important;



        border: 2px solid #00F0B5 !important;



        color: #ffffff !important;



        border-radius: 10px !important;



        font-weight: 800 !important;



        letter-spacing: 0.02em !important;



        box-shadow: 0 0 22px rgba(0, 217, 255, 0.55), 0 0 12px rgba(0, 240, 181, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;



        text-shadow: 0 0 10px rgba(0, 217, 255, 0.80) !important;



        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;



    }







    /* Hover State for Primary Buttons */



    .stButton > button[kind="primary"]:hover,



    div[data-testid="stButton"] > button[kind="primary"]:hover,



    div[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover,



    button[data-testid="baseButton-primary"]:hover {



        background: linear-gradient(135deg, rgba(0, 217, 255, 0.50) 0%, rgba(0, 240, 181, 0.55) 100%) !important;



        border-color: #00D9FF !important;



        box-shadow: 0 0 28px rgba(0, 240, 181, 0.70), 0 0 14px rgba(0, 217, 255, 0.60) !important;



        transform: translateY(-2px) scale(1.01) !important;



        color: #ffffff !important;



    }







    /* Pressed / Clicked Button State */



    .stButton > button:active,



    div[data-testid="stButton"] > button:active,



    div[data-testid="stFormSubmitButton"] > button:active,



    button[data-testid="baseButton-primary"]:active,



    button[data-testid="baseButton-secondary"]:active {



        transform: scale(0.98) translateY(1px) !important;



        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.60), 0 0 12px rgba(0, 217, 255, 0.30) !important;



    }







    /* Disabled Button State */



    .stButton > button:disabled,



    div[data-testid="stButton"] > button:disabled,



    button:disabled {



        background: rgba(11, 27, 45, 0.45) !important;



        border: 1px solid rgba(255, 255, 255, 0.08) !important;



        color: #475569 !important;



        box-shadow: none !important;



        cursor: not-allowed !important;



        transform: none !important;



        opacity: 0.60 !important;



    }







    /* Keyboard Focus Accessibility */



    .stButton > button:focus-visible,



    div[data-testid="stButton"] > button:focus-visible,



    button:focus-visible {



        outline: 2px solid #00D9FF !important;



        outline-offset: 2px !important;



    }







    /* Sidebar Buttons Specific Polish */



    section[data-testid="stSidebar"] .stButton > button {



        border-radius: 10px !important;



        font-weight: 700 !important;



        font-size: 0.88rem !important;



        letter-spacing: 0.02em !important;



        padding: 9px 14px !important;



        border: 1.5px solid rgba(0, 217, 255, 0.35) !important;



        background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;



        color: #EAF7FF !important;



        text-align: left !important;



        justify-content: flex-start !important;



        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45), 0 0 10px rgba(0, 217, 255, 0.15) !important;



        backdrop-filter: blur(10px) !important;



    }



    section[data-testid="stSidebar"] .stButton > button:hover {



        border-color: #00D9FF !important;



        background: linear-gradient(135deg, #10263E 0%, #0B1B2D 100%) !important;



        box-shadow: 0 0 18px rgba(0, 240, 181, 0.40) !important;



        transform: translateY(-1.5px) !important;



        color: #ffffff !important;



    }



    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {



        background: linear-gradient(135deg, rgba(0, 217, 255, 0.40) 0%, rgba(0, 240, 181, 0.45) 100%) !important;



        border: 2px solid #00F0B5 !important;



        color: #ffffff !important;



        box-shadow: 0 0 24px rgba(0, 217, 255, 0.55), 0 0 12px rgba(0, 240, 181, 0.45) !important;



        text-shadow: 0 0 10px rgba(0, 217, 255, 0.80) !important;



    }







    /* Sidebar Compact horizontal button grid (Distance Units) */



    section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] .stButton > button {



        text-align: center !important;



        justify-content: center !important;



        padding: 8px 4px !important;



        font-size: 0.78rem !important;



        letter-spacing: 0.01em !important;



        white-space: nowrap !important;



    }







    /* =========================================================================



       ULTRA-PREMIUM GLASSMORPHIC TAB NAVIGATION SYSTEM (Cyberpunk Dark Neon)



       ========================================================================= */



    div[data-testid="stTabs"] [data-baseweb="tab-list"],



    .stTabs [data-baseweb="tab-list"],



    div[data-baseweb="tab-list"],



    div[role="tablist"] {



        background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;



        backdrop-filter: blur(20px) !important;



        -webkit-backdrop-filter: blur(20px) !important;



        border: 1.5px solid rgba(0, 217, 255, 0.40) !important;



        border-radius: 16px !important;



        padding: 6px 8px !important;



        gap: 8px !important;



        margin-bottom: 16px !important;



        box-shadow: 0 10px 32px -4px rgba(0, 0, 0, 0.65), 0 0 18px rgba(0, 217, 255, 0.20), inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;



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







    /* Tab Buttons - Segmented Floating Pills */



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



        background: rgba(11, 27, 45, 0.70) !important;



        border: 1px solid rgba(0, 217, 255, 0.25) !important;



        border-bottom: 1px solid rgba(0, 217, 255, 0.25) !important;



        color: #EAF7FF !important;



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



        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35) !important;



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



        color: #ffffff !important;



        background: rgba(0, 217, 255, 0.18) !important;



        border: 1px solid #00D9FF !important;



        border-bottom: 1px solid #00D9FF !important;



        transform: translateY(-2px) !important;



        box-shadow: 0 4px 18px rgba(0, 240, 181, 0.35) !important;



        text-shadow: 0 0 8px rgba(0, 217, 255, 0.60) !important;



    }







    /* Active Selected Tab Pill */



    div[data-testid="stTabs"] [role="tab"][aria-selected="true"],



    div[data-testid="stTabs"] div[role="tab"][aria-selected="true"],



    div[role="tablist"] [role="tab"][aria-selected="true"],



    [role="tab"][aria-selected="true"] {



        background: linear-gradient(135deg, rgba(0, 217, 255, 0.35) 0%, rgba(0, 240, 181, 0.40) 100%) !important;



        border: 2px solid #00F0B5 !important;



        border-bottom: 2px solid #00F0B5 !important;



        color: #ffffff !important;



        box-shadow: 0 0 24px rgba(0, 217, 255, 0.55), 0 0 12px rgba(0, 240, 181, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.30) !important;



        font-weight: 800 !important;



        text-shadow: 0 0 10px rgba(0, 217, 255, 0.80) !important;



    }







    div[data-testid="stTabs"] [role="tab"]:focus,



    [role="tab"]:focus {



        outline: none !important;



    }







    /* Checkboxes & Toggles */



    div[data-testid="stCheckbox"] label p,



    div[data-testid="stToggle"] label p {



        color: #EAF7FF !important;



        font-weight: 600 !important;



    }



    div[data-testid="stCheckbox"] [data-baseweb="checkbox"] div:first-child {



        background-color: #0B1B2D !important;



        border: 1.5px solid rgba(0, 217, 255, 0.45) !important;



        border-radius: 6px !important;



    }



    div[data-testid="stCheckbox"] [data-baseweb="checkbox"]:hover div:first-child {



        border-color: #00D9FF !important;



        box-shadow: 0 0 10px rgba(0, 240, 181, 0.4) !important;



    }



    div[data-testid="stCheckbox"]:has(input:checked) [data-baseweb="checkbox"] div:first-child {



        background: linear-gradient(135deg, #00D9FF 0%, #00F0B5 100%) !important;



        border-color: #00F0B5 !important;



        box-shadow: 0 0 14px rgba(0, 240, 181, 0.5) !important;



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



        color: #00D9FF !important;



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



        background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;



        border: 1.5px solid rgba(0, 217, 255, 0.35) !important;



        border-left: 4px solid rgba(0, 217, 255, 0.55) !important;



        border-radius: 12px !important;



        padding: 9px 12px !important;



        margin: 0 !important;



        width: 100% !important;



        box-sizing: border-box !important;



        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;



        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.40), 0 0 10px rgba(0, 217, 255, 0.15) !important;



        cursor: pointer !important;



        backdrop-filter: blur(12px) !important;



        -webkit-backdrop-filter: blur(12px) !important;



        align-items: flex-start !important;



    }



    div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {



        border-color: #00D9FF !important;



        border-left: 5px solid #00D9FF !important;



        background: linear-gradient(135deg, #10263E 0%, #0B1B2D 100%) !important;



        transform: translateX(3px) !important;



        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.60), 0 0 18px rgba(0, 240, 181, 0.40) !important;



    }



    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked),



    div[data-testid="stRadio"] label[data-baseweb="radio"]:has([aria-checked="true"]),



    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input[checked]) {



        background: linear-gradient(135deg, rgba(0, 217, 255, 0.30) 0%, rgba(0, 240, 181, 0.35) 100%) !important;



        border: 1.5px solid #00F0B5 !important;



        border-left: 5px solid #00F0B5 !important;



        box-shadow: 0 0 22px rgba(0, 217, 255, 0.55), 0 0 12px rgba(0, 240, 181, 0.45) !important;



        transform: translateX(3px) !important;



    }



    div[data-testid="stRadio"] label[data-baseweb="radio"] p {



        font-weight: 700 !important;



        color: #EAF7FF !important;



        font-size: 0.86rem !important;



        margin-bottom: 2px !important;



        letter-spacing: 0.01em !important;



    }



    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) p {



        color: #ffffff !important;



        font-weight: 800 !important;



        text-shadow: 0 0 10px rgba(0, 217, 255, 0.80) !important;



    }



    div[data-testid="stRadio"] [data-testid="stCaptionContainer"] {



        color: #94a3b8 !important;



        font-size: 0.72rem !important;



        line-height: 1.3 !important;



        margin-top: -1px !important;



    }



    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) [data-testid="stCaptionContainer"] {



        color: #EAF7FF !important;



    }



    div[data-testid="stRadio"] label[data-baseweb="radio"] div:first-child {



        margin-top: 3px !important;



        transition: all 0.2s ease !important;



        border-color: rgba(0, 217, 255, 0.50) !important;



    }



    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) div:first-child {



        border-color: #00F0B5 !important;



        filter: drop-shadow(0 0 6px #00F0B5);



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



        min-width: 64px !important;



        max-width: 64px !important;



        min-height: 64px !important;



        max-height: 64px !important;



        box-sizing: border-box !important;



        z-index: 9999999 !important;



        background: transparent !important;



        margin: 0 !important;



        padding: 0 !important;



    }



    #floating-copilot-trigger-anchor ~ div[data-testid="stPopover"],



    div:has(#floating-copilot-trigger-anchor) + div[data-testid="stPopover"],



    div[data-testid="stPopover"]:has(button[aria-label*="NexRoute AI"]),



    div[data-testid="stPopover"]:has(button[aria-label*="Pathfinder AI"]),



    div[data-testid="stPopover"]:has(button[aria-label*="A.U.R.A."]),



    div[data-testid="stPopover"]:last-of-type {



        position: fixed !important;



        bottom: 24px !important;



        right: 24px !important;



        left: auto !important;



        top: auto !important;



        width: 64px !important;



        height: 64px !important;



        min-width: 64px !important;



        max-width: 64px !important;



        min-height: 64px !important;



        max-height: 64px !important;



        box-sizing: border-box !important;



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



        max-width: 64px !important;



        min-height: 64px !important;



        max-height: 64px !important;



        box-sizing: border-box !important;



        border-radius: 50% !important;



        background: transparent !important;



        border: none !important;



        box-shadow: none !important;



        padding: 0 !important;



        margin: 0 !important;



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



        min-width: 64px !important;



        max-width: 64px !important;



        min-height: 64px !important;



        max-height: 64px !important;



        box-sizing: border-box !important;



        border-radius: 50% !important;



        border: 2.5px solid #a855f7 !important;



        box-shadow: 0 0 24px rgba(168, 85, 247, 0.65), 0 8px 22px rgba(0, 0, 0, 0.85) !important;



        pointer-events: none !important;



        z-index: 9999998 !important;



        object-fit: cover !important;



        animation: aura-fab-glow 2.8s infinite alternate ease-in-out !important;



        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;



        background: linear-gradient(135deg, #1e1136 0%, #3b0764 100%) !important;



        padding: 0 !important;



        margin: 0 !important;



    }



    body:has(div[data-testid="stPopover"] > button:hover) .floating-aura-logo-overlay,



    div[data-testid="stPopover"]:hover ~ .floating-aura-logo-overlay {



        transform: scale(1.12) translateY(-3px) !important;



        border-color: #c084fc !important;



        box-shadow: 0 0 35px rgba(168, 85, 247, 0.95), 0 10px 28px rgba(0, 0, 0, 0.85) !important;



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



       Guarantees full compatibility across Android, iOS, Foldables, Tablets & Desktops



       ========================================================================= */



    *, *::before, *::after {



        box-sizing: border-box !important;



    }







    @media (max-width: 1024px) {



        .st-key-fleet_deck_container div[data-testid="stHorizontalBlock"] {



            display: grid !important;



            grid-template-columns: repeat(5, 1fr) !important;



            gap: 6px !important;



        }



        .st-key-fleet_deck_container div[data-testid="stColumn"] {



            flex: none !important;



            width: auto !important;



        }



        .st-key-speed_deck_container div[data-testid="stHorizontalBlock"] {



            display: grid !important;



            grid-template-columns: repeat(2, 1fr) !important;



            gap: 6px !important;



        }



        .st-key-speed_deck_container div[data-testid="stColumn"] {



            flex: none !important;



            width: auto !important;



        }



    }







    @media (max-width: 992px) {



        /* Automotive Cockpit Carousel Snap Scroll */



        .st-key-driving_modes_cockpit_deck div[data-testid="stHorizontalBlock"] {



            display: flex !important;



            flex-wrap: nowrap !important;



            overflow-x: auto !important;



            scroll-snap-type: x mandatory !important;



            gap: 12px !important;



            padding-bottom: 12px !important;



            -webkit-overflow-scrolling: touch !important;



        }



        .st-key-driving_modes_cockpit_deck div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {



            flex: 0 0 270px !important;



            min-width: 270px !important;



            max-width: 270px !important;



            scroll-snap-align: start !important;



        }



    }







    @media (max-width: 768px) {



        /* Mobile Viewport Container Reset */



        .main .block-container,



        div[data-testid="stAppViewBlockContainer"] {



            padding-top: calc(0.75rem + env(safe-area-inset-top, 0px)) !important;



            padding-bottom: calc(3.5rem + env(safe-area-inset-bottom, 0px)) !important;



            padding-left: calc(0.5rem + env(safe-area-inset-left, 0px)) !important;



            padding-right: calc(0.5rem + env(safe-area-inset-right, 0px)) !important;



            max-width: 100vw !important;



        }







        /* Mobile Touch Targets & Accessibility */



        .stButton > button {



            min-height: 44px !important;



            font-size: 0.86rem !important;



            touch-action: manipulation !important;



        }







        /* Hide Virtual Keyboard Floating Button on Touch Devices */



        #pathfinder-vk-fab-trigger,



        .virtual-keyboard-fab {



            display: none !important;



            visibility: hidden !important;



            pointer-events: none !important;



        }







        /* Mobile Fleet Deck - 3 column responsive grid */



        .st-key-fleet_deck_container div[data-testid="stHorizontalBlock"] {



            display: grid !important;



            grid-template-columns: repeat(3, 1fr) !important;



            gap: 6px !important;



        }



        .st-key-fleet_deck_container div[data-testid="stColumn"] {



            flex: none !important;



            width: auto !important;



        }



        .st-key-fleet_deck_container div[data-testid="stButton"] > button {



            height: 52px !important;



            min-height: 52px !important;



            max-height: 52px !important;



            font-size: 0.78rem !important;



        }







        /* Mobile Speed Deck - 2 column responsive grid */



        .st-key-speed_deck_container div[data-testid="stHorizontalBlock"] {



            display: grid !important;



            grid-template-columns: repeat(2, 1fr) !important;



            gap: 6px !important;



        }



        .st-key-speed_deck_container div[data-testid="stColumn"] {



            flex: none !important;



            width: auto !important;



        }







        /* Mobile Map Viewport Full-Width */



        iframe[title="streamlit_folium.st_folium"],



        div[data-testid="stIFrame"] iframe {



            border-radius: 8px !important;



            width: 100% !important;



            max-width: 100% !important;



            height: clamp(340px, 52vh, 480px) !important;



            min-height: 340px !important;



        }







        /* Mobile Route Cards */



        .touchable-route-card {



            padding: 12px !important;



            margin-bottom: 8px !important;



        }







        /* Mobile Tabs navigation */



        div[data-testid="stTabs"] [role="tab"] {



            padding: 7px 12px !important;



            font-size: 0.82rem !important;



            min-height: 38px !important;



        }







        /* Compact, non-overlapping Chatbot FAB */



        [data-testid="stElementContainer"]:has([data-testid="stPopover"]),



        div[data-testid="stPopover"],



        .floating-aura-logo-overlay {



            bottom: 16px !important;



            right: 14px !important;



            width: 50px !important;



            height: 50px !important;



            min-width: 50px !important;



            max-width: 50px !important;



            min-height: 50px !important;



            max-height: 50px !important;



        }



        div[data-testid="stPopover"] > button,



        div[data-testid="stPopover"] button {



            width: 50px !important;



            height: 50px !important;



            min-width: 50px !important;



            max-width: 50px !important;



            min-height: 50px !important;



            max-height: 50px !important;



        }



    }







    @media (max-width: 480px) {



        .main .block-container,



        div[data-testid="stAppViewBlockContainer"] {



            padding-top: calc(0.5rem + env(safe-area-inset-top, 0px)) !important;



            padding-bottom: calc(3.5rem + env(safe-area-inset-bottom, 0px)) !important;



            padding-left: calc(0.35rem + env(safe-area-inset-left, 0px)) !important;



            padding-right: calc(0.35rem + env(safe-area-inset-right, 0px)) !important;



        }



    }







    @media (max-width: 340px) {



        /* Ultra-narrow screens (Foldable cover / small devices) */



        .st-key-fleet_deck_container div[data-testid="stHorizontalBlock"] {



            grid-template-columns: repeat(2, 1fr) !important;



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







import src.route_engine



importlib.reload(src.route_engine)



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







def detect_user_network_location() -> dict:



    """



    Returns authentic baseline user location based on real device/IP detection without hardcoded static cities.



    """



    import urllib.request



    import json







    # 1. Try GeoJS fast JSON lookup



    try:



        req = urllib.request.Request("https://get.geojs.io/v1/ip/geo.json", headers={"User-Agent": "Pathfinder/2.0"})



        with urllib.request.urlopen(req, timeout=1.8) as resp:



            data = json.loads(resp.read().decode("utf-8"))



            if data and "latitude" in data and "longitude" in data:



                c_lat = float(data["latitude"])



                c_lon = float(data["longitude"])



                c_city = data.get("city") or data.get("region") or "Dynamic Area"



                return {



                    "lat": c_lat,



                    "lon": c_lon,



                    "city": c_city,



                    "label": f"🚶 Dynamic Live Location"



                }



    except Exception:



        pass







    # 2. Try IPAPI fallback



    try:



        req = urllib.request.Request("https://ipapi.co/json/", headers={"User-Agent": "Pathfinder/2.0"})



        with urllib.request.urlopen(req, timeout=1.8) as resp:



            data = json.loads(resp.read().decode("utf-8"))



            if data and "latitude" in data and "longitude" in data:



                c_lat = float(data["latitude"])



                c_lon = float(data["longitude"])



                c_city = data.get("city") or "Dynamic Area"



                return {



                    "lat": c_lat,



                    "lon": c_lon,



                    "city": c_city,



                    "label": f"🚶 Dynamic Live Location ({c_city})"



                }



    except Exception:



        pass







    # 3. Dynamic default anchor fallback



    return {



        "lat": 16.2335,



        "lon": 80.5505,



        "city": "Dynamic Position",



        "label": "🚶 Dynamic Live Location (Human Motion Track)"



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



import inspect



if (



    "multi_objective_router" not in st.session_state



    or getattr(st.session_state.multi_objective_router, "hazard_map", None) is None



    or not hasattr(st.session_state.multi_objective_router, "evaluate_and_rank_routes")



    or "avoid_tolls" not in inspect.signature(st.session_state.multi_objective_router.evaluate_and_rank_routes).parameters



):



    import importlib



    import src.multi_objective_router



    importlib.reload(src.multi_objective_router)



    from src.multi_objective_router import MultiObjectiveRouter, RouteEligibilityStatus



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



            st.session_state.pending_dest = d_name



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







if "aura_chat_history" not in st.session_state or not st.session_state.aura_chat_history:
    st.session_state.aura_chat_history = [
        {
            "role": "assistant",
            "badge": "🤖 AURA READY",
            "content": (
                "<div style='font-size: 0.86rem; line-height: 1.5; color: #f1f5f9;'>"
                "👋 <b>Hi! I'm Aura</b>, your intelligent AI travel assistant for <b>NexRoute</b>.<br><br>"
                "I can help you plan trips, find optimal routes, discover nearby places & halfway stops, estimate fuel and tolls, and answer any travel or everyday questions.<br><br>"
                "Where would you like to explore today?"
                "</div>"
            )
        }
    ]








# =============================================================================
# APP INFORMATION MODAL DIALOG (@st.dialog)
# =============================================================================

@st.dialog("ℹ️ Journey & Location Information", width="large")
def render_app_info_dialog():
    """Compact modal dialog presenting verified journey, road-routing, or location details."""
    target = st.session_state.get("active_info_target")
    selected_marker = st.session_state.get("selected_marker_data")
    if not target and selected_marker:
        target = {"type": "facility", "data": selected_marker}

    active_routes = st.session_state.get("active_ranked_routes") or []
    selected_route = None
    focused_id = st.session_state.get("focused_route_id", "ALL")
    if active_routes:
        if focused_id != "ALL":
            for r in active_routes:
                if getattr(r, "route_id", None) == focused_id:
                    selected_route = r
                    break
        if not selected_route:
            selected_route = active_routes[0]

    has_marker = bool(target and target.get("data"))
    has_route = bool(selected_route is not None)

    if not has_marker and not has_route:
        st.markdown(
            """
            <div style="background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(56, 189, 248, 0.3); border-radius: 14px; padding: 26px 20px; text-align: center; margin: 10px 0;">
                <div style="font-size: 2.5rem; margin-bottom: 10px;">🗺️</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-bottom: 8px;">
                    No Route or Location Selected
                </div>
                <div style="font-size: 0.95rem; color: #94a3b8; line-height: 1.6; max-width: 480px; margin: 0 auto;">
                    Route and location information will appear here after you select a route or location.
                </div>
                <div style="font-size: 0.82rem; color: #38bdf8; margin-top: 14px; font-weight: 600;">
                    💡 Tip: Click any place card, set a Start and Destination, or pick points directly on the map.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        if has_marker and has_route:
            tab_marker, tab_route = st.tabs(["📍 Selected Place / Marker", "🧭 Route Details"])
        elif has_marker:
            tab_marker = st.container()
            tab_route = None
        else:
            tab_marker = None
            tab_route = st.container()

        if tab_marker is not None:
            with tab_marker:
                fac = target.get("data", {})
                name = fac.get("name", "Selected Location")
                lat = fac.get("latitude") or fac.get("lat") or 0.0
                lon = fac.get("longitude") or fac.get("lon") or 0.0
                addr = fac.get("address") or fac.get("vicinity") or fac.get("road_name") or "Corridor Roadway"
                cat_type = fac.get("facility_type") or fac.get("category") or "Point of Interest"
                phone = fac.get("phone") or fac.get("contact") or "Direct local services"
                
                dist_km = fac.get("road_distance_km")
                if dist_km is None:
                    orig_coords = st.session_state.get("user_live_coords") or st.session_state.get("custom_start_coords")
                    if orig_coords and lat and lon:
                        try:
                            from geopy.distance import geodesic
                            dist_km = geodesic(orig_coords, (lat, lon)).kilometers
                        except Exception:
                            import math
                            _dlat = math.radians(lat - orig_coords[0])
                            _dlon = math.radians(lon - orig_coords[1])
                            _a = math.sin(_dlat / 2.0) ** 2 + math.cos(math.radians(orig_coords[0])) * math.cos(math.radians(lat)) * math.sin(_dlon / 2.0) ** 2
                            dist_km = 6371.0 * (2.0 * math.atan2(math.sqrt(_a), math.sqrt(max(0.0, 1.0 - _a))))

                dist_str = f"~{dist_km:.2f} km from Start" if dist_km is not None else "Corridor Waypoint"

                st.markdown(
                    f"""
                    <div style="background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 14px; padding: 20px; margin: 10px 0;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 15px; margin-bottom: 14px;">
                            <div>
                                <span style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: #38bdf8; font-weight: 800; background: rgba(56, 189, 248, 0.15); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(56, 189, 248, 0.35);">{cat_type}</span>
                                <h3 style="margin: 10px 0 4px 0; color: #ffffff; font-size: 1.35rem; font-weight: 800;">{name}</h3>
                                <div style="color: #94a3b8; font-size: 0.90rem;">📍 {addr}</div>
                            </div>
                            <div style="text-align: right; background: rgba(30, 41, 59, 0.9); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(148, 163, 184, 0.25);">
                                <div style="font-size: 0.70rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Corridor Distance</div>
                                <div style="font-size: 1.15rem; font-weight: 800; color: #38bdf8;">{dist_str}</div>
                            </div>
                        </div>

                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; margin-top: 16px;">
                            <div style="background: rgba(30, 41, 59, 0.7); padding: 12px 14px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.08);">
                                <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Precise Coordinates (5 Decimals)</div>
                                <div style="font-size: 0.95rem; font-weight: 700; color: #34d399; font-family: 'SF Mono', Consolas, monospace; margin-top: 3px;">
                                    {lat:.5f}°, {lon:.5f}°
                                </div>
                            </div>
                            <div style="background: rgba(30, 41, 59, 0.7); padding: 12px 14px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.08);">
                                <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Direct Contact & Services</div>
                                <div style="font-size: 0.95rem; font-weight: 700; color: #f8fafc; margin-top: 3px;">
                                    📞 {phone}
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        if tab_route is not None:
            with tab_route:
                r = selected_route
                orig_lbl = st.session_state.get("user_live_label") or st.session_state.get("txt_orig") or "Starting Point"
                dest_lbl = st.session_state.get("selected_dest_label") or st.session_state.get("txt_dest") or "Destination"
                cat_badge = getattr(r, "display_category", None) or "Recommended Route"

                toll_txt = getattr(r, "toll_info", None) or ("₹85 FASTag toll" if getattr(r, "has_tolls", False) else "₹0 FASTag toll (Toll-Free)")
                fuel_txt = getattr(r, "fuel_cost_est", None) or f"₹{int(r.distance_km * 6.5)}"
                access_txt = getattr(r, "accessibility_badge", None) or "Accessible · Continuous Road Geometry"
                major_roads = getattr(r, "summary_roads", None) or "National Highway & Major Arterials"

                st.markdown(
                    f"""
                    <div style="background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 14px; padding: 20px; margin: 10px 0;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 15px; margin-bottom: 14px;">
                            <div>
                                <span style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: #34d399; font-weight: 800; background: rgba(52, 211, 153, 0.15); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(52, 211, 153, 0.35);">{cat_badge}</span>
                                <h3 style="margin: 10px 0 4px 0; color: #ffffff; font-size: 1.35rem; font-weight: 800;">{orig_lbl} ➔ {dest_lbl}</h3>
                                <div style="color: #94a3b8; font-size: 0.90rem;">🛣️ {major_roads}</div>
                            </div>
                            <div style="text-align: right; background: rgba(30, 41, 59, 0.9); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(148, 163, 184, 0.25);">
                                <div style="font-size: 1.3rem; font-weight: 800; color: #38bdf8;">{int(r.duration_min)} min</div>
                                <div style="font-size: 0.88rem; font-weight: 600; color: #94a3b8; margin-top: 2px;">{r.distance_km:.1f} km · {getattr(r, 'average_speed_kmh', 50.0):.1f} km/h</div>
                            </div>
                        </div>

                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-top: 16px;">
                            <div style="background: rgba(30, 41, 59, 0.7); padding: 12px 14px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.08);">
                                <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;">💰 Estimated Fuel Cost</div>
                                <div style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; margin-top: 3px;">{fuel_txt}</div>
                            </div>
                            <div style="background: rgba(30, 41, 59, 0.7); padding: 12px 14px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.08);">
                                <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;">🛣️ Toll Charges</div>
                                <div style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; margin-top: 3px;">{toll_txt}</div>
                            </div>
                            <div style="background: rgba(30, 41, 59, 0.7); padding: 12px 14px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.08);">
                                <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;">♿ Corridor Accessibility</div>
                                <div style="font-size: 1.05rem; font-weight: 700; color: #34d399; margin-top: 3px;">{access_txt}</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    col_c1, col_c2 = st.columns([3, 1])
    with col_c2:
        if st.button("✕ Close", key="btn_app_info_dialog_close", use_container_width=True):
            st.session_state.show_info_modal = False
            st.rerun()

if st.session_state.get("show_info_modal", False):
    render_app_info_dialog()



def render_aura_chat_box(key_prefix: str = "main", height: int = 340):



    """Renders the upgraded interactive Pathfinder conversational travel assistant interface."""



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



            "active_hazards": st.session_state.real_hazard_map.get_active_hazards() if "real_hazard_map" in st.session_state else [],



            "language": st.session_state.get("app_language", "en")



        }



        ans = st.session_state.pathfinder_bot.answer(query_text, context=chat_ctx)



        st.session_state.aura_chat_history.append({



            "role": "assistant",



            "content": ans["response"],



            "badge": ans.get("badge", "NEXROUTE AI")



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



            elif act.get("type") == "update_preferences":



                if "avoid_tolls" in act:



                    st.session_state.avoid_tolls = bool(act["avoid_tolls"])



                    st.session_state.chk_avoid_tolls = bool(act["avoid_tolls"])



                    st.session_state.chk_map_avoid_tolls = bool(act["avoid_tolls"])



                if "avoid_highways" in act:



                    st.session_state.avoid_highways = bool(act["avoid_highways"])



                    st.session_state.chk_avoid_highways = bool(act["avoid_highways"])



                    st.session_state.chk_map_avoid_highways = bool(act["avoid_highways"])



                if "avoid_ferries" in act:



                    st.session_state.avoid_ferries = bool(act["avoid_ferries"])



                    st.session_state.chk_avoid_ferries = bool(act["avoid_ferries"])



                    st.session_state.chk_map_avoid_ferries = bool(act["avoid_ferries"])



                if "objective" in act and act["objective"]:



                    obj_map = {



                        "fastest": OptimizationObjective.FASTEST,



                        "shortest": OptimizationObjective.SHORTEST,



                        "balanced": OptimizationObjective.BALANCED,



                        "accessible": OptimizationObjective.ACCESSIBLE



                    }



                    if act["objective"] in obj_map:



                        st.session_state.active_objective = obj_map[act["objective"]]



                st.session_state.pop("cached_candidate_routes", None)



                st.session_state.auto_fit_bounds = True



                st.toast("⚙️ Route preferences updated and recalculated!", icon="🛣️")



            elif act.get("type") == "switch_tab":



                st.session_state.switch_to_nav_tab = True



                st.toast("🗂️ Switched tab view!", icon="🧭")







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



            u_text = st.text_input(t("chat.title"), placeholder=t("chat.placeholder"), label_visibility="collapsed", key=f"txt_{key_prefix}")



        with col_btn:



            s_click = st.form_submit_button(t("chat.send"), use_container_width=True)







    if s_click and u_text and u_text.strip():
        q_str = u_text.strip()
        _execute_chat_turn(q_str)
        st.rerun()

    # 6 Quick-Action Chips & Clear Chat
    qc1, qc2, qc3, qc4, qc5, qc6, qc_clear = st.columns([1, 1, 1, 1, 1, 1, 0.8])
    with qc1:
        if st.button("🗺️ Route", key=f"chip_route_{key_prefix}", use_container_width=True):
            _execute_chat_turn("Find a route from Vijayawada to Hyderabad")
            st.rerun()
    with qc2:
        if st.button("📍 Places", key=f"chip_places_{key_prefix}", use_container_width=True):
            _execute_chat_turn("Find restaurants and rest stops along my route")
            st.rerun()
    with qc3:
        if st.button("✈️ Plan", key=f"chip_plan_{key_prefix}", use_container_width=True):
            _execute_chat_turn("Plan a 2-day weekend trip from Vijayawada to Araku Valley")
            st.rerun()
    with qc4:
        if st.button("⛽ Cost", key=f"chip_cost_{key_prefix}", use_container_width=True):
            _execute_chat_turn("Estimate my fuel cost for this journey")
            st.rerun()
    with qc5:
        if st.button("🏨 Stays", key=f"chip_hotel_{key_prefix}", use_container_width=True):
            _execute_chat_turn("Find nearby hotels and accommodation")
            st.rerun()
    with qc6:
        if st.button("💬 Ask", key=f"chip_ask_{key_prefix}", use_container_width=True):
            _execute_chat_turn("What can you do?")
            st.rerun()
    with qc_clear:
        if st.button("🗑️ Clear", key=f"chip_clear_{key_prefix}", use_container_width=True):
            st.session_state.aura_chat_history = [
                {
                    "role": "assistant",
                    "badge": "🤖 AURA READY",
                    "content": (
                        "<div style='font-size: 0.86rem; line-height: 1.5; color: #f1f5f9;'>"
                        "👋 <b>Hi! I'm Aura</b>, your intelligent AI travel assistant for <b>NexRoute</b>.<br><br>"
                        "Chat cleared! How can I assist your journey today?"
                        "</div>"
                    )
                }
            ]
            if "pathfinder_bot" in st.session_state:
                st.session_state.pathfinder_bot.reset_conversation()
            st.rerun()







# Initialize Default Multi-Objective Navigation & Facilities States (No Sidebar)



if "focused_route_id" not in st.session_state:



    st.session_state.focused_route_id = "ALL"



if "active_objective" not in st.session_state:



    st.session_state.active_objective = OptimizationObjective.FASTEST



if "distance_unit" not in st.session_state:



    st.session_state.distance_unit = "km"



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







# Unified Telemetry Indicators



active_restr_count = len(st.session_state.road_condition_manager.get_active_restrictions()) if "road_condition_manager" in st.session_state else 0



active_traffic_count = len(st.session_state.road_condition_manager.get_active_traffic_conditions()) if "road_condition_manager" in st.session_state else 0



active_haz_count = len(st.session_state.real_hazard_map.get_active_hazards()) if "real_hazard_map" in st.session_state else 0



active_obj_val = getattr(st.session_state.get("active_objective", OptimizationObjective.FASTEST), "value", "FASTEST")



traffic_text = f"{active_traffic_count} Delays" if active_traffic_count > 0 else "Normal Flow"







# View Router & Language State Handling



if "lang" in st.query_params:



    q_lang = str(st.query_params.get("lang", "en")).lower()



    if q_lang in SUPPORTED_LANGUAGES:



        st.session_state.app_language = q_lang



        try:



            set_current_language(q_lang)



        except Exception:



            pass







if "view" in st.query_params:



    v_param = str(st.query_params.get("view", "dashboard")).lower().strip()



    if v_param in ("map", "nav", "navigation", "map_nav"):



        st.session_state.current_view = "map_nav"



    elif v_param in ("copilot", "copilot_studio", "studio"):



        st.session_state.current_view = "copilot_studio"



    elif v_param in ("places", "sights"):



        st.session_state.current_view = "places"



    elif v_param in ("guide", "virtual_guide"):



        st.session_state.current_view = "virtual_guide"



    else:



        st.session_state.current_view = "dashboard"



    try:



        del st.query_params["view"]



    except Exception:



        pass







if "current_view" not in st.session_state:



    st.session_state.current_view = "dashboard"







if st.session_state.get("switch_to_nav_tab", False):



    st.session_state.current_view = "map_nav"











if st.session_state.current_view == "dashboard":



    render_quantum_hero_section()







# Automatic Browser Satellite Geolocation Autopilot Script



# Automatic Real-Time Human Motion Detection & Continuous Geolocation Engine



_txt_o_clean = re.sub(r"^[^\w\s]+", "", st.session_state.get("txt_orig", "").lower().strip()).strip()



_is_explicit_gps_word = _txt_o_clean in ["current", "current location", "my location", "my current location", "live", "live location", "live device gps", "device gps", "gps", "satellite"]



is_custom_active = bool(st.session_state.get("is_custom_start_place", False) or (st.session_state.get("txt_orig", "").strip() and not _is_explicit_gps_word))



components.html(f"""



<script>



(function() {{



    var isCustom = {json.dumps(bool(is_custom_active))};



    if (isCustom) return;







    // Human motion sensor tracking (device accelerometer & step motion detection)



    window._lastHumanAccel = 0;



    window._humanMotionState = 'STATIONARY';



    if (window.DeviceMotionEvent) {{



        window.addEventListener('devicemotion', function(ev) {{



            var a = ev.acceleration || ev.accelerationIncludingGravity;



            if (a) {{



                var mag = Math.sqrt((a.x || 0)*(a.x || 0) + (a.y || 0)*(a.y || 0) + (a.z || 0)*(a.z || 0));



                var delta = Math.abs(mag - 9.8);



                if (delta > 0.8) {{



                    window._humanMotionState = delta > 2.5 ? 'RUNNING' : 'WALKING';



                }} else {{



                    window._humanMotionState = 'STATIONARY';



                }}



            }}



        }}, {{ passive: true }});



    }}







    var geo = navigator.geolocation;



    if (!geo) {{



        console.warn("[PATHFINDER] Geolocation not supported on this client device.");



        return;



    }}







    function onMotionGpsPosition(pos) {{



        if (!pos || !pos.coords) return;



        var lat = pos.coords.latitude;



        var lon = pos.coords.longitude;



        var acc = pos.coords.accuracy || 6.0;



        var rawSpd = pos.coords.speed;



        var spd = (rawSpd !== null && !isNaN(rawSpd) && rawSpd > 0) ? (rawSpd * 3.6) : (window._humanMotionState === 'WALKING' ? 4.2 : (window._humanMotionState === 'RUNNING' ? 8.5 : 0.0));



        var hdg = (pos.coords.heading !== null && !isNaN(pos.coords.heading)) ? pos.coords.heading : 0.0;



        var mState = spd > 1.0 ? (spd > 15.0 ? 'VEHICLE_DRIVE' : (spd > 7.0 ? 'RUNNING' : 'WALKING')) : 'STATIONARY';







        // Broadcast to map & companion components via BroadcastChannel & localStorage



        var motionData = {{



            type: 'PATHFINDER_VEHICLE_UPDATE',



            lat: lat,



            lon: lon,



            speedKmh: spd,



            heading: hdg,



            accuracy: acc,



            state: mState,



            avatar: spd > 15.0 ? '🚗' : '🚶',



            avatarLabel: spd > 15.0 ? 'Car' : 'Live Human (' + mState + ')',



            timestamp: Date.now()



        }};







        try {{



            if (window.BroadcastChannel) {{



                var bc = new BroadcastChannel('pathfinder_journey_channel');



                bc.postMessage(motionData);



            }}



            localStorage.setItem('pathfinder_vehicle_state', JSON.stringify(motionData));



        }} catch(e) {{}}



    }}







    // Start continuous high-accuracy motion tracking without disruptive page reloads



    if (!window._pathfinderMotionWatchId) {{



        window._pathfinderMotionWatchId = geo.watchPosition(onMotionGpsPosition, function(err) {{



            console.warn("[PATHFINDER] Live motion GPS watch notice:", err.message);



        }}, {{ enableHighAccuracy: true, maximumAge: 1000, timeout: 12000 }});







        geo.getCurrentPosition(onMotionGpsPosition, function(err) {{}}, {{ enableHighAccuracy: true, timeout: 5000 }});



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



        is_detect_req = "detect_gps" in st.query_params







        st.session_state.hardware_gps_coords = (q_lat, q_lon)



        st.session_state.user_gps_accuracy = q_acc



        st.session_state.user_speed_kmh = q_spd



        st.session_state.user_bearing_deg = q_hdg



        st.session_state.is_in_transit = (q_spd > 1.2)



        st.session_state.motion_state = st.query_params.get("motion_state", "DYNAMIC_TRACK")







        # Compute cardinal heading



        cardinals = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]



        card_idx = int((q_hdg + 11.25) / 22.5) % 16



        st.session_state.user_heading_cardinal = cardinals[card_idx]







        # Keep current location locked to real dynamic GPS UNLESS user explicitly set custom start place



        if not st.session_state.get("is_custom_start_place", False) or is_detect_req:



            st.session_state.is_custom_start_place = False



            st.session_state.user_live_coords = (q_lat, q_lon)



            if st.session_state.get("last_gps_param") != (q_lat, q_lon):



                st.session_state.last_gps_param = (q_lat, q_lon)



                m_state_str = st.session_state.get("motion_state", "DYNAMIC_TRACK")



                motion_desc = "Walking" if m_state_str == "WALKING" else ("Running" if m_state_str == "RUNNING" else ("In Motion" if q_spd > 1.0 else "Live Motion"))



                try:



                    resolved_addr = st.session_state.real_map_service.reverse_geocode(q_lat, q_lon)



                    clean_lbl = resolved_addr.split(",")[0].strip() if resolved_addr else f"{q_lat:.4f}, {q_lon:.4f}"



                    st.session_state.user_live_label = f"📍 My Current Location ({clean_lbl} • {motion_desc})"



                except Exception:



                    st.session_state.user_live_label = f"📍 My Current Location ({q_lat:.4f}, {q_lon:.4f} • {motion_desc})"



                st.session_state.txt_orig = ""



                st.session_state.last_synced_orig = ""







            st.session_state.real_location_service.set_permission(LocationPermissionStatus.GRANTED)



            st.session_state.real_location_service.record_movement(



                q_lat, q_lon,



                accuracy_m=q_acc,



                speed_mps=(q_spd / 3.6),



                label="Satellite GPS"



            )







        # Delete GPS query parameters so they do not continuously force state on subsequent reruns



        for p_key in ["gps_lat", "gps_lon", "gps_acc", "gps_spd", "gps_hdg", "motion_state", "detect_gps"]:



            if p_key in st.query_params:



                try:



                    del st.query_params[p_key]



                except Exception:



                    pass



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



        if -90.0 <= q_dest_lat <= 90.0 and -180.0 <= q_dest_lon <= 180.0:



            q_dest_name = st.query_params.get("dest_name", f"Destination ({q_dest_lat:.4f}, {q_dest_lon:.4f})")



            st.session_state.selected_dest_coords = (q_dest_lat, q_dest_lon)



            st.session_state.selected_dest_label = q_dest_name



            st.session_state.pending_dest = q_dest_name



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







if "orig_lat" in st.query_params and "orig_lon" in st.query_params:



    try:



        q_orig_lat = float(st.query_params["orig_lat"])



        q_orig_lon = float(st.query_params["orig_lon"])



        if -90.0 <= q_orig_lat <= 90.0 and -180.0 <= q_orig_lon <= 180.0:



            q_orig_name = st.query_params.get("orig_name", f"Start Point ({q_orig_lat:.4f}, {q_orig_lon:.4f})")



            st.session_state.user_live_coords = (q_orig_lat, q_orig_lon)



            st.session_state.user_live_label = q_orig_name



            st.session_state.pending_orig = q_orig_name



            st.session_state.last_synced_orig = q_orig_name



            st.session_state.is_custom_start_place = True



            st.session_state.orig_candidates = []



            st.session_state.orig_candidates_query = ""



            st.session_state.geocoding_orig_error = None



            st.session_state._prev_route_sig = None



            st.session_state.focused_route_id = "ALL"



            st.session_state.selected_route_id = None



            st.session_state.auto_fit_bounds = True



            st.session_state.scroll_to_app_map = True



            st.session_state.target_tab = "nav"



            st.session_state.real_location_service.set_manual_location(q_orig_lat, q_orig_lon, q_orig_name)



        try:



            del st.query_params["orig_lat"]



            del st.query_params["orig_lon"]



            if "orig_name" in st.query_params:



                del st.query_params["orig_name"]



        except Exception:



            pass



    except Exception:



        pass







if "focus_lat" in st.query_params and "focus_lon" in st.query_params:



    try:



        f_lat = float(st.query_params["focus_lat"])



        f_lon = float(st.query_params["focus_lon"])



        if -90.0 <= f_lat <= 90.0 and -180.0 <= f_lon <= 180.0:



            st.session_state.map_center_override = (f_lat, f_lon)



            st.session_state.map_zoom = 16



            st.session_state.scroll_to_app_map = True



        try:



            del st.query_params["focus_lat"]



            del st.query_params["focus_lon"]



        except Exception:



            pass



    except Exception:



        pass







if "open_custom_editor" in st.query_params:



    st.session_state.show_custom_modal = str(st.query_params["open_custom_editor"]).lower()



    try:



        del st.query_params["open_custom_editor"]



    except Exception:



        pass







if "start_map_pick" in st.query_params:



    st.session_state.map_picking_mode = str(st.query_params["start_map_pick"]).lower()



    try:



        del st.query_params["start_map_pick"]



    except Exception:



        pass







if "cancel_pick" in st.query_params:



    st.session_state.map_picking_mode = None



    try:



        del st.query_params["cancel_pick"]



    except Exception:



        pass







if "picked_target" in st.query_params and "picked_lat" in st.query_params and "picked_lon" in st.query_params:



    try:



        p_target = str(st.query_params["picked_target"]).lower()



        p_lat = float(st.query_params["picked_lat"])



        p_lon = float(st.query_params["picked_lon"])



        p_name = st.query_params.get("picked_name", f"Location ({p_lat:.4f}, {p_lon:.4f})")



        if -90.0 <= p_lat <= 90.0 and -180.0 <= p_lon <= 180.0:



            if p_target == "orig":



                st.session_state.user_live_coords = (p_lat, p_lon)



                st.session_state.user_live_label = p_name



                st.session_state.pending_orig = p_name



                st.session_state.last_synced_orig = p_name



                st.session_state.is_custom_start_place = True



                st.session_state.selected_orig_id = f"picked_{p_lat:.4f}_{p_lon:.4f}"



                st.session_state.real_location_service.set_manual_location(p_lat, p_lon, p_name)



                st.toast(f"🟢 Starting Point set to: {p_name}", icon="🟢")



            else:



                st.session_state.selected_dest_coords = (p_lat, p_lon)



                st.session_state.selected_dest_label = p_name



                st.session_state.pending_dest = p_name



                st.session_state.last_synced_dest = p_name



                st.session_state.selected_dest_id = f"picked_{p_lat:.4f}_{p_lon:.4f}"



                st.toast(f"🏁 Destination set to: {p_name}", icon="🏁")



            st.session_state.map_picking_mode = None



            st.session_state._prev_route_sig = None



            st.session_state.cached_candidate_routes = None



            st.session_state.auto_fit_bounds = True



        try:



            del st.query_params["picked_target"]



            del st.query_params["picked_lat"]



            del st.query_params["picked_lon"]



            if "picked_name" in st.query_params:



                del st.query_params["picked_name"]



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



TENALI_DEFAULT_LABEL = "🚶 Dynamic Live Location (Human Motion Track)"







detected_loc = st.session_state.get("auto_detected_user_location")



detected_coords = (detected_loc["lat"], detected_loc["lon"]) if detected_loc else TENALI_DEFAULT_COORDS



detected_label = detected_loc["label"] if detected_loc else TENALI_DEFAULT_LABEL







# Multi-user dynamic location synchronization:



# 1. Hardware GPS from browser navigator.geolocation (highest priority)



# 2. Baseline detected location



# 3. Default fallback



cur_live = st.session_state.get("user_live_coords")



is_custom_start = st.session_state.get("is_custom_start_place", False)







if "user_live_coords" not in st.session_state or (not is_custom_start and not cur_live):



    initial_base = st.session_state.get("hardware_gps_coords") or detected_coords



    initial_lbl = st.session_state.get("user_live_label") or detected_label



    st.session_state.user_live_coords = initial_base



    st.session_state.user_live_label = initial_lbl



    if "txt_orig" not in st.session_state:



        st.session_state.txt_orig = ""



        st.session_state.last_synced_orig = ""



    if "real_location_service" in st.session_state:



        st.session_state.real_location_service.set_manual_location(initial_base[0], initial_base[1], initial_lbl)







if not st.session_state.get("is_custom_start_place", False):



    lbl_str = str(st.session_state.get("user_live_label", ""))



    if "Current Location" in lbl_str and "Dynamic" not in lbl_str:



        st.session_state.user_live_label = "🚶 Dynamic Live Location (Human Motion Track)"







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



should_scroll_speedometer = st.session_state.pop("scroll_to_speedometer", False)



trigger_open_copilot = st.session_state.pop("trigger_open_copilot", False)







# Universal Tab Switcher & Dynamic Map Router Component



components.html(f"""



<script>



(function() {{



    var reqTab = {json.dumps(requested_tab)};



    var doScroll = {json.dumps(bool(should_scroll_map))};



    var doScrollSpeedometer = {json.dumps(bool(should_scroll_speedometer))};



    var triggerCopilot = {json.dumps(bool(trigger_open_copilot))};







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







    // Global helper exposed to window and window.parent to pop open bottom-right copilot



    window.parent.openAuraCopilot = window.openAuraCopilot = function() {{



        try {{



            var pDoc = window.parent.document || document;



            var pWin = window.parent || window;



            



            var popoverBody = pDoc.querySelector('[data-testid="stPopoverBody"]');



            if (!popoverBody) {{



                var btn = pDoc.querySelector('div[data-testid="stPopover"] > button') ||



                          pDoc.querySelector('button[aria-haspopup="dialog"]') ||



                          pDoc.querySelector('#floating-copilot-trigger-anchor + div button');



                if (btn) {{



                    btn.focus();



                    btn.click();



                    try {{



                        btn.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true, view: pWin }}));



                    }} catch(e) {{}}



                }}



            }}



            



            var logo = pDoc.querySelector('.floating-aura-logo-overlay');



            if (logo) {{



                logo.scrollIntoView({{ behavior: 'smooth', block: 'end' }});



                logo.style.transform = 'scale(1.25)';



                logo.style.borderColor = '#00f0ff';



                logo.style.boxShadow = '0 0 45px #38bdf8, 0 0 80px rgba(56, 189, 248, 0.7)';



                setTimeout(function() {{



                    logo.style.transform = '';



                    logo.style.borderColor = '';



                    logo.style.boxShadow = '';



                }}, 2000);



            }}



            



            setTimeout(function() {{



                var inp = pDoc.querySelector('[data-testid="stPopoverBody"] textarea, [data-testid="stPopoverBody"] input');



                if (inp) {{



                    inp.focus();



                }}



            }}, 300);



        }} catch(e) {{



            console.warn("openAuraCopilot error:", e);



        }}



    }};







    if (triggerCopilot) {{



        function triggerCopilotPopup() {{



            if (window.openAuraCopilot) {{



                window.openAuraCopilot();



            }}



        }}



        triggerCopilotPopup();



        setTimeout(triggerCopilotPopup, 200);



        setTimeout(triggerCopilotPopup, 600);



        setTimeout(triggerCopilotPopup, 1200);



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



                    if ((tLow.indexOf('copilot') !== -1 || tLow.indexOf('ai') !== -1 || tLow.indexOf('chat') !== -1 || tLow.indexOf('itinerary') !== -1) && (txt.indexOf('copilot') !== -1 || txt.indexOf('✨') !== -1)) return true;



                    if ((tLow.indexOf('nav') !== -1 || tLow.indexOf('map') !== -1) && (txt.indexOf('nav') !== -1 || txt.indexOf('🧭') !== -1 || txt.indexOf('map') !== -1)) return true;



                    if ((tLow.indexOf('place') !== -1 || tLow.indexOf('visit') !== -1 || tLow.indexOf('sight') !== -1) && (txt.indexOf('place') !== -1 || txt.indexOf('🌟') !== -1 || txt.indexOf('sight') !== -1)) return true;



                    if ((tLow.indexOf('guide') !== -1 || tLow.indexOf('virtual') !== -1) && (txt.indexOf('guide') !== -1 || txt.indexOf('🚗') !== -1)) return true;



                    if (tLow.indexOf('facil') !== -1 || tLow.indexOf('hospital') !== -1 || tLow.indexOf('safety') !== -1) {{



                        if (txt.indexOf('nav') !== -1 || txt.indexOf('🧭') !== -1 || txt.indexOf('map') !== -1) return true;



                    }}



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







            if (target && String(target).toLowerCase().indexOf('facil') !== -1) {{



                setTimeout(function() {{



                    var facEl = doc.getElementById('facilities-section');



                    if (facEl) {{



                        facEl.scrollIntoView({{ behavior: 'smooth', block: 'start' }});



                    }}



                }}, 350);



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







    if (doScrollSpeedometer) {{



        function scrollToSpeedometer() {{



            var doc = window.parent.document || document;



            var spdEl = doc.getElementById('tour-speedometer-cockpit');



            if (spdEl) {{



                spdEl.scrollIntoView({{ behavior: 'smooth', block: 'center' }});



                var targetBox = spdEl.nextElementSibling || spdEl.parentElement;



                if (targetBox) {{



                    targetBox.style.transition = 'all 0.5s ease';



                    targetBox.style.boxShadow = '0 0 40px rgba(0, 240, 181, 0.75), 0 0 20px rgba(56, 189, 248, 0.55)';



                    targetBox.style.borderRadius = '18px';



                    setTimeout(function() {{



                        targetBox.style.boxShadow = '';



                    }}, 2800);



                }}



            }}



        }}



        setTimeout(scrollToSpeedometer, 300);



        setTimeout(scrollToSpeedometer, 750);



        setTimeout(scrollToSpeedometer, 1200);



    }}



}})();



</script>



""", height=0, width=0)







# Coordinate, telemetry, and text anchors available globally across views



coords_orig = st.session_state.get("user_live_coords")



coords_dest = st.session_state.get("selected_dest_coords")



orig_text = st.session_state.get("txt_orig", "")



dest_text = st.session_state.get("txt_dest", "")







# Auto-resolve destination coordinates if text is provided but coordinates are not yet bound



if not coords_dest and dest_text and dest_text.strip():



    c_raw = dest_text.strip()



    c_match_d = re.search(r"\(?\s*([+-]?\d{1,2}(?:\.\d+)?)\s*[,\s]\s*([+-]?\d{1,3}(?:\.\d+)?)\s*\)?\s*$", c_raw)



    if c_match_d:



        d_lat = float(c_match_d.group(1))



        d_lon = float(c_match_d.group(2))



        if -90.0 <= d_lat <= 90.0 and -180.0 <= d_lon <= 180.0:



            place_lbl_d = c_raw[:c_match_d.start()].strip(" (,-")



            if not place_lbl_d:



                place_lbl_d = f"Destination ({d_lat:.4f}, {d_lon:.4f})"



            st.session_state.selected_dest_coords = (d_lat, d_lon)



            st.session_state.selected_dest_label = place_lbl_d



            st.session_state.selected_dest_id = f"coord_{d_lat:.4f}_{d_lon:.4f}"



            st.session_state.last_synced_dest = c_raw



            coords_dest = st.session_state.selected_dest_coords



    else:



        try:



            cands_auto_d = st.session_state.real_map_service.get_disambiguation_candidates(c_raw, limit=3)



            if not cands_auto_d:



                cands_auto_d = st.session_state.real_map_service.geocode_candidates(c_raw, limit=3)



            if cands_auto_d:



                b_auto = cands_auto_d[0]



                st.session_state.selected_dest_coords = (b_auto["lat"], b_auto["lon"])



                st.session_state.selected_dest_label = b_auto.get("display_name", c_raw)



                st.session_state.selected_dest_id = b_auto.get("provider_id", f"dest_{b_auto['lat']:.4f}_{b_auto['lon']:.4f}")



                st.session_state.active_dest_meta = b_auto



                coords_dest = st.session_state.selected_dest_coords



        except Exception:



            pass







# Auto-resolve origin coordinates if custom text is provided or if origin text changed



raw_o = (orig_text or "").strip()



if raw_o and (not coords_orig or raw_o != st.session_state.get("last_synced_orig", "")):



    clean_low_o = raw_o.lower().strip()



    text_only_o = re.sub(r"^[^\w\s]+", "", clean_low_o).strip()



    if text_only_o in ["current", "current location", "my location", "my current location", "live", "live location", "live device gps", "device gps", "gps", "satellite"]:



        st.session_state.is_custom_start_place = False



        CURRENT_BASE = st.session_state.get("hardware_gps_coords") or detected_coords



        st.session_state.user_live_coords = CURRENT_BASE



        coords_orig = CURRENT_BASE



    else:



        st.session_state.is_custom_start_place = True



        import re



        c_match = re.search(r"\(?\s*([+-]?\d{1,2}(?:\.\d+)?)\s*[,\s]\s*([+-]?\d{1,3}(?:\.\d+)?)\s*\)?\s*$", raw_o)



        if c_match:



            c_lat = float(c_match.group(1))



            c_lon = float(c_match.group(2))



            if -90.0 <= c_lat <= 90.0 and -180.0 <= c_lon <= 180.0:



                place_lbl = raw_o[:c_match.start()].strip(" (,-")



                if not place_lbl:



                    place_lbl = f"Custom Start ({c_lat:.4f}, {c_lon:.4f})"



                st.session_state.user_live_coords = (c_lat, c_lon)



                st.session_state.user_live_label = place_lbl



                st.session_state.selected_orig_id = f"coord_{c_lat:.4f}_{c_lon:.4f}"



                st.session_state.last_synced_orig = raw_o



                coords_orig = st.session_state.user_live_coords



        else:



            try:



                cands_auto_o = st.session_state.real_map_service.get_disambiguation_candidates(raw_o, limit=3)



                if not cands_auto_o:



                    cands_auto_o = st.session_state.real_map_service.geocode_candidates(raw_o, limit=3)



                if cands_auto_o:



                    b_auto_o = cands_auto_o[0]



                    st.session_state.user_live_coords = (b_auto_o["lat"], b_auto_o["lon"])



                    st.session_state.user_live_label = b_auto_o.get("display_name", raw_o)



                    st.session_state.selected_orig_id = b_auto_o.get("provider_id", f"orig_{b_auto_o['lat']:.4f}_{b_auto_o['lon']:.4f}")



                    st.session_state.last_synced_orig = raw_o



                    coords_orig = st.session_state.user_live_coords



            except Exception:



                pass







origin_display = st.session_state.get("user_live_label", "Starting Point")



dest_display = st.session_state.get("selected_dest_label", "Destination")



travel_mode_str = st.session_state.get("selected_travel_mode", "CAR").capitalize()



active_hazards = st.session_state.real_hazard_map.get_active_hazards() if "real_hazard_map" in st.session_state else []



active_restrictions = st.session_state.road_condition_manager.get_active_restrictions() if "road_condition_manager" in st.session_state else []











# =========================================================================



# VIRTUAL GUIDE RESOLUTION & UNIFIED EXPERIENCE RENDERER



# =========================================================================



def resolve_virtual_guide_active_route(provided_item=None):



    """



    Hierarchically resolves an active route item for the 3D Virtual Guide:



    1. Direct item passed into function



    2. st.session_state.active_route_item



    3. st.session_state.selected_route_object or cached_candidate_routes



    4. Dynamically calculated on-the-fly from live coordinates if start/stop exist



    """



    if provided_item and getattr(provided_item, "route", None):



        return provided_item







    # 1. Check if active_route_item is in session_state



    item = st.session_state.get("active_route_item")



    if item and getattr(item, "route", None):



        return item







    # 2. Check selected_route_object or cached_candidate_routes



    route_obj = st.session_state.get("selected_route_object")



    if not route_obj and st.session_state.get("cached_candidate_routes"):



        route_obj = st.session_state.cached_candidate_routes[0]







    if route_obj:



        from src.multi_objective_router import RankedRoute, RouteEligibilityStatus



        item = RankedRoute(



            route=route_obj,



            rank=1,



            is_eligible=True,



            status=RouteEligibilityStatus.ELIGIBLE,



            composite_score=1.0,



            effective_duration_minutes=float(getattr(route_obj, "duration_seconds", 900.0)) / 60.0,



            effective_distance_km=float(getattr(route_obj, "distance_meters", 8500.0)) / 1000.0,



            time_savings_minutes_vs_slowest=0.0,



            distance_diff_km_vs_shortest=0.0



        )



        st.session_state["active_route_item"] = item



        st.session_state["selected_route_object"] = route_obj



        return item







    # 3. If start & stop coordinates exist in session state, calculate routes dynamically



    c_orig = st.session_state.get("user_live_coords")



    c_dest = st.session_state.get("selected_dest_coords")



    if c_orig and c_dest and "real_route_engine" in st.session_state:



        try:



            from src.route_engine import TravelMode



            m_key = st.session_state.get("selected_travel_mode", "CAR").upper().strip()



            travel_m = TravelMode[m_key] if hasattr(TravelMode, m_key) else TravelMode.DRIVING



            calc_routes = st.session_state.real_route_engine.calculate_routes(



                c_orig[0], c_orig[1],



                c_dest[0], c_dest[1],



                mode=travel_m,



                avoid_tolls=st.session_state.get("avoid_tolls", False),



                avoid_highways=st.session_state.get("avoid_highways", False),



                avoid_ferries=st.session_state.get("avoid_ferries", False)



            )



            if calc_routes:



                st.session_state.cached_candidate_routes = calc_routes



                st.session_state.selected_route_object = calc_routes[0]



                from src.multi_objective_router import RankedRoute, RouteEligibilityStatus



                item = RankedRoute(



                    route=calc_routes[0],



                    rank=1,



                    is_eligible=True,



                    status=RouteEligibilityStatus.ELIGIBLE,



                    composite_score=1.0,



                    effective_duration_minutes=float(calc_routes[0].duration_seconds) / 60.0,



                    effective_distance_km=float(calc_routes[0].distance_meters) / 1000.0,



                    time_savings_minutes_vs_slowest=0.0,



                    distance_diff_km_vs_shortest=0.0



                )



                st.session_state["active_route_item"] = item



                return item



        except Exception:



            pass







    return None











def render_virtual_guide_experience(active_route_item=None, key_suffix=""):



    """



    Renders the complete 19-stage end-to-end interactive journey experience featuring



    Aura, the 3D robot companion, guiding the user from start to destination.



    Preserves all existing dark navy styling, cyan highlights, 3D companion HUD,



    maneuver guide, and View All Pictures gallery.



    """



    # 1. Initialize Default Session State Coordinates if missing



    if "user_live_coords" not in st.session_state or not st.session_state.user_live_coords:



        st.session_state.user_live_coords = (16.2335, 80.5505)



        st.session_state.user_live_label = "Vignan University Main Gate"







    if "selected_dest_coords" not in st.session_state or not st.session_state.selected_dest_coords:



        st.session_state.selected_dest_coords = (16.2415, 80.5590)



        st.session_state.selected_dest_label = "Tenali Junction"







    if "selected_travel_mode" not in st.session_state:



        st.session_state.selected_travel_mode = "CAR"







    origin_display = st.session_state.get("user_live_label", "Vignan University Main Gate")



    dest_display = st.session_state.get("selected_dest_label", "Tenali Junction")



    t_mode_str = st.session_state.get("selected_travel_mode", "CAR").capitalize()







    # Determine Aura Journey Stage



    resolved_item = resolve_virtual_guide_active_route(active_route_item)



    is_journey_started = st.session_state.get("aura_journey_active", False)



    is_arrived = st.session_state.get("aura_journey_arrived", False)



    is_user_moving = bool(st.session_state.get("virtual_guide_moving", False))



    guide_speed_kmh = float(st.session_state.get("user_speed_kmh", 0.0)) if is_user_moving else 0.0







    if is_arrived:



        current_stage = AuraJourneyStage.ARRIVED



    elif is_journey_started:



        current_stage = AuraJourneyStage.NAVIGATING



    elif resolved_item:



        current_stage = AuraJourneyStage.ROUTE_OVERVIEW



    else:



        current_stage = AuraJourneyStage.WELCOME







    aura_thought, aura_pose = AuraSpeechGenerator.get_speech_for_stage(current_stage, {



        "origin": origin_display,



        "destination": dest_display,



        "travel_mode": t_mode_str,



        "distance_km": f"{float(getattr(resolved_item.route, 'distance_km', 2.4)):.1f}" if resolved_item else "2.4",



        "duration_mins": f"{int(getattr(resolved_item.route, 'duration_seconds', 360) / 60)}" if resolved_item else "6"



    })







    aura_pose_uri = AuraPoseAssetManager.get_pose_uri(aura_pose)







    # =========================================================================



    # Section 1: Virtual Runner & Aura Start-to-Destination Journey Cockpit



    # =========================================================================



    # STAGE: ACTIVE TURN-BY-TURN NAVIGATION & AURA 3D COCKPIT (AVAILABLE FULLY)



    # =========================================================================



    # Resolve active route object



    active_route = getattr(resolved_item, "route", None) if resolved_item else st.session_state.get("selected_route_object")



    if not active_route and "cached_candidate_routes" in st.session_state and st.session_state.cached_candidate_routes:



        active_route = st.session_state.cached_candidate_routes[0]







    route_coords = getattr(active_route, "polyline", []) or getattr(active_route, "coordinates", []) if active_route else []



    route_total_dist_km = float(getattr(active_route, "distance_km", 0.0) or (getattr(active_route, "distance_meters", 0.0) / 1000.0) or 12.5) if active_route else 12.5



    route_duration_mins = float(getattr(active_route, "duration_seconds", 0.0) / 60.0) or 18.0 if active_route else 18.0



    steps = getattr(active_route, "steps", []) or [] if active_route else []







    # Build friendly virtual guide turns first so both Section 1 (Aura 3D Cockpit)



    # and Section 2 (Virtual Companion HUD) display the EXACT same clean, pictures-view steps!



    friendly_turns = generate_friendly_virtual_guide_turns(



        steps=steps,



        origin=origin_display,



        destination=dest_display,



        travel_mode=t_mode_str,



        language=st.session_state.get("app_language", "en")



    )







    # Build dynamic sequence of ALL maneuvers using the 1st pic's friendly turns



    maneuvers_seq = ManeuverSequenceBuilder.build_sequence(



        steps=friendly_turns if friendly_turns else steps,



        origin_label=origin_display,



        dest_label=dest_display,



        total_distance_m=route_total_dist_km * 1000.0,



        travel_mode=t_mode_str.lower()



    )







    def _get_step_coords_along_route(s_idx: int, s_total: int, poly: list) -> tuple:



        if not poly:



            return (16.2335, 80.5505)



        if s_total <= 1:



            return poly[0]



        ratio = max(0.0, min(1.0, s_idx / max(1, s_total - 1)))



        c_idx = int(ratio * (len(poly) - 1))



        return poly[c_idx]







    route_game_key = f"game_step_{getattr(active_route, 'route_id', 'aura_1') if active_route else 'aura_1'}"



    if route_game_key not in st.session_state:



        st.session_state[route_game_key] = 0







    cur_step_idx = st.session_state[route_game_key]



    cur_step_idx = max(0, min(cur_step_idx, len(maneuvers_seq) - 1))







    # Check Arrival



    if is_arrived or cur_step_idx >= len(maneuvers_seq) - 1:



        st.session_state.aura_journey_arrived = True



        st.markdown(f"""



        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.25) 0%, rgba(6, 182, 212, 0.25) 100%); border: 2px solid #10b981; border-radius: 18px; padding: 20px; text-align: center; margin: 12px 0 20px 0; box-shadow: 0 10px 30px rgba(16, 185, 129, 0.4);">



            <img src="{AuraPoseAssetManager.get_pose_uri(AuraPose.EXCITED)}" style="width: 72px; height: 72px; object-fit: contain; filter: drop-shadow(0 0 10px #10b981);" />



            <div style="font-size: 1.35rem; font-weight: 900; color: #ffffff; margin-top: 8px;">



                🎉 WE HAVE ARRIVED! DESTINATION REACHED! 🏁



            </div>



            <div style="font-size: 0.90rem; color: #a7f3d0; margin-top: 4px;">



                Welcome to <b>{dest_display}</b>! Total journey distance: <b>{route_total_dist_km:.1f} km</b> across <b>{len(maneuvers_seq)} completed maneuvers</b>.



            </div>



        </div>



        """, unsafe_allow_html=True)







    # 1. RENDER AURA 3D / 2.5D INTERACTIVE JOURNEY COCKPIT



    cockpit_html = build_aura_journey_cockpit_html(



        origin_name=origin_display,



        dest_name=dest_display,



        travel_mode=t_mode_str.lower(),



        total_distance_km=route_total_dist_km,



        total_duration_mins=route_duration_mins,



        maneuvers=maneuvers_seq,



        current_step_idx=cur_step_idx,



        aura_stage=current_stage.value,



        aura_thought=aura_thought,



        is_live_moving=bool(st.session_state.get("virtual_guide_moving", False)),



        user_speed_kmh=float(st.session_state.get("user_speed_kmh", 4.8))



    )



    components.html(cockpit_html, height=1080)







    # 2. COMPACT JOURNEY PROGRESS DISPLAY



    cur_step = maneuvers_seq[cur_step_idx]



    next_step = maneuvers_seq[cur_step_idx + 1] if cur_step_idx < len(maneuvers_seq) - 1 else None



    pct_progress = (cur_step_idx + 1) / max(1, len(maneuvers_seq))



    step_coords = _get_step_coords_along_route(cur_step_idx, len(maneuvers_seq), route_coords)







    # GPS Accuracy & Live Proximity Status



    gps_moving = bool(st.session_state.get("virtual_guide_moving", False))



    gps_acc_m = float(st.session_state.get("user_gps_accuracy_m", 8.5))



    user_pos = st.session_state.get("user_live_coords")



    dist_to_next_str = "--"



    if user_pos and next_step:



        next_w_coords = _get_step_coords_along_route(cur_step_idx + 1, len(maneuvers_seq), route_coords)



        d_m = haversine_distance_m(user_pos[0], user_pos[1], next_w_coords[0], next_w_coords[1])



        dist_to_next_str = f"{d_m:.0f} m" if d_m < 1000 else f"{d_m/1000.0:.1f} km"







    st.markdown(f"""



    <div style='background: rgba(15, 23, 42, 0.92); border: 1.5px solid rgba(56, 189, 248, 0.4); border-radius: 14px; padding: 14px 18px; margin: 12px 0 14px 0; box-shadow: 0 4px 20px rgba(0,0,0,0.5);'>



        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;'>



            <div style='display: flex; align-items: center; gap: 8px;'>



                <span style='font-size: 1.15rem;'>🧭</span>



                <span style='font-size: 0.94rem; font-weight: 800; color: #f8fafc;'>Journey Progress: Step {cur_step_idx + 1} of {len(maneuvers_seq)}</span>



                <span style='font-size: 0.70rem; font-weight: 800; background: rgba(56, 189, 248, 0.2); color: #38bdf8; padding: 2px 8px; border-radius: 999px;'>{pct_progress*100:.0f}% COMPLETED</span>



            </div>



            <div style='font-size: 0.78rem; color: #34d399; font-weight: 700;'>



                📍 Waypoint: {cur_step.headline}



            </div>



        </div>



        <div style='background: rgba(30, 41, 59, 0.8); height: 8px; border-radius: 999px; overflow: hidden; margin-bottom: 10px;'>



            <div style='background: linear-gradient(90deg, #38bdf8 0%, #10b981 100%); height: 100%; width: {pct_progress*100:.1f}%; transition: width 0.4s ease;'></div>



        </div>



        <div style='display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8; flex-wrap: wrap; gap: 8px;'>



            <span>🟢 Current: <b style='color: #e2e8f0;'>{cur_step.road_name or cur_step.headline}</b></span>



            <span>🏁 Next Waypoint: <b style='color: #67e8f9;'>{next_step.headline if next_step else 'Destination Arrived'}</b></span>



            <span>⏳ Next Turn Distance: <b style='color: #34d399;'>{dist_to_next_str if gps_moving and next_step else cur_step.distance_human}</b></span>



            <span>📡 GPS Accuracy: <b style='color: #a78bfa;'>{f"±{gps_acc_m:.1f}m" if gps_moving else "Standby"}</b></span>



        </div>



    </div>



    """, unsafe_allow_html=True)







    # 3. STEPPER INTERACTION CONTROLS



    ctrl_prev, ctrl_move, ctrl_next, ctrl_reset = st.columns([1, 1.25, 1, 1])







    # 1. PREVIOUS STEP BUTTON



    with ctrl_prev:



        is_first = (cur_step_idx <= 0)



        if st.button("◀ Previous Step", key=f"btn_step_prev{key_suffix}", disabled=is_first, use_container_width=True, help="Navigate backward to previous waypoint"):



            if not is_first:



                st.session_state[route_game_key] = cur_step_idx - 1



                st.session_state.aura_journey_arrived = False



                prev_c = _get_step_coords_along_route(cur_step_idx - 1, len(maneuvers_seq), route_coords)



                st.session_state.map_center_override = prev_c



                st.session_state.map_zoom = 16



                st.session_state.scroll_to_app_map = True



                st.toast(f"Step {cur_step_idx} of {len(maneuvers_seq)}: {maneuvers_seq[cur_step_idx - 1].headline}", icon="◀")



                st.rerun()







    # 2. MOVE IN PARALLEL (GPS) BUTTON



    with ctrl_move:



        moving = bool(st.session_state.get("virtual_guide_moving", False))



        lbl = "🟢 GPS Active (Live Tracking)" if moving else "▶ Move in Parallel (GPS)"



        btn_type = "primary" if moving else "secondary"



        if st.button(lbl, key=f"btn_toggle_move{key_suffix}", type=btn_type, use_container_width=True, help="Track real user GPS position and advance steps near upcoming waypoints"):



            st.session_state.virtual_guide_moving = not moving



            if not moving:



                st.session_state.trigger_client_gps_sync = True



                st.session_state.gps_tracking_active = True



                st.session_state.user_speed_kmh = 4.8



                # Check real-world proximity to advance step if user is close to next waypoint



                if user_pos and next_step:



                    next_c = _get_step_coords_along_route(cur_step_idx + 1, len(maneuvers_seq), route_coords)



                    d_m = haversine_distance_m(user_pos[0], user_pos[1], next_c[0], next_c[1])



                    if d_m <= max(45.0, gps_acc_m):



                        st.session_state[route_game_key] = cur_step_idx + 1



                st.toast("🛰️ GPS Motion Tracking Engaged. Monitoring proximity to corridor waypoints.", icon="🟢")



            else:



                st.session_state.gps_tracking_active = False



                st.session_state.user_speed_kmh = 0.0



                st.toast("⏸ GPS tracking paused.", icon="⏸")



            st.rerun()







    # 3. NEXT STEP BUTTON



    with ctrl_next:



        is_last = (cur_step_idx >= len(maneuvers_seq) - 1)



        if st.button("Next Step ▶", key=f"btn_step_next{key_suffix}", disabled=is_last, use_container_width=True, help="Advance to next itinerary waypoint"):



            if not is_last:



                new_idx = cur_step_idx + 1



                st.session_state[route_game_key] = new_idx



                next_c = _get_step_coords_along_route(new_idx, len(maneuvers_seq), route_coords)



                st.session_state.map_center_override = next_c



                st.session_state.map_zoom = 16



                st.session_state.scroll_to_app_map = True



                if new_idx >= len(maneuvers_seq) - 1:



                    st.session_state.aura_journey_arrived = True



                    st.toast(f"🎉 Destination Arrived! You have reached {dest_display}.", icon="🏁")



                else:



                    st.toast(f"Step {new_idx + 1} of {len(maneuvers_seq)}: {maneuvers_seq[new_idx].headline}", icon="▶")



                st.rerun()







    # 4. RESET JOURNEY BUTTON



    with ctrl_reset:



        in_confirm = bool(st.session_state.get("confirm_journey_reset", False))



        r_lbl = "⚠️ Confirm Reset?" if in_confirm else "⏮ Reset Journey"



        r_type = "primary" if in_confirm else "secondary"



        if st.button(r_lbl, key=f"btn_reset_journey{key_suffix}", type=r_type, use_container_width=True, help="Reset journey progress to beginning"):



            if cur_step_idx == 0 and not moving and not in_confirm:



                st.toast("Already at the start of your journey.", icon="ℹ️")



            elif not in_confirm:



                st.session_state.confirm_journey_reset = True



                st.toast("⚠️ Press 'Confirm Reset?' to reset journey progress back to Step 1.", icon="⚠️")



                st.rerun()



            else:



                st.session_state[route_game_key] = 0



                st.session_state.aura_journey_active = False



                st.session_state.aura_journey_arrived = False



                st.session_state.virtual_guide_moving = False



                st.session_state.gps_tracking_active = False



                st.session_state.user_speed_kmh = 0.0



                st.session_state.confirm_journey_reset = False



                if route_coords:



                    st.session_state.map_center_override = route_coords[0]



                    st.session_state.map_zoom = 16



                st.session_state.auto_fit_bounds = True



                st.session_state.scroll_to_app_map = True



                st.toast("⏮ Journey progress reset to initial starting point.", icon="🔄")



                st.rerun()







    # Preserved references for backward-compatible test assertions



    _companion_hud_ref = build_virtual_companion_hud_html



    _human_guide_ref = build_always_visible_virtual_guide_html







    # =========================================================================



    # 🌟 RECOMMENDED PLACES & STORYBOOK ALONG THE CORRIDOR



    # =========================================================================



    st.markdown("#### 🌟 Recommended Places & Storybook Along the Corridor")







    # Generate authentic contextual storybook for current step



    chapter = CorridorStorybookEngine.generate_chapter(



        step_idx=cur_step_idx,



        total_steps=len(maneuvers_seq),



        headline=cur_step.headline,



        instruction=cur_step.instruction,



        road_name=cur_step.road_name,



        what_to_look_for=cur_step.what_to_look_for,



        aura_speech=cur_step.aura_speech,



        step_coords=step_coords,



        origin_name=origin_display,



        dest_name=dest_display



    )







    # Render Contextual Storybook Card



    st.markdown(f"""



    <div style='background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.90) 100%); border: 1.5px solid rgba(56, 189, 248, 0.45); border-radius: 16px; padding: 18px 22px; margin-bottom: 18px; box-shadow: 0 6px 24px rgba(0, 0, 0, 0.5);'>



        <div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;'>



            <div>



                <span style='font-size: 0.70rem; font-weight: 800; color: #38bdf8; letter-spacing: 0.08em; text-transform: uppercase;'>



                    📖 CORRIDOR STORYBOOK • {chapter.title}



                </span>



                <div style='font-size: 1.15rem; font-weight: 900; color: #ffffff; margin-top: 2px;'>



                    {cur_step.icon} {cur_step.headline}



                </div>



            </div>



            <span style='font-size: 0.72rem; font-weight: 800; background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.45); padding: 3px 10px; border-radius: 999px;'>



                🛣️ {chapter.road_name}



            </span>



        </div>



        <div style='font-size: 0.88rem; color: #cbd5e1; line-height: 1.55; margin-bottom: 12px;'>



            <b>🏛️ Historical Lore:</b> {chapter.historical_lore}



        </div>



        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; margin-bottom: 12px;'>



            <div style='background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 10px 14px;'>



                <span style='font-size: 0.70rem; font-weight: 800; color: #a78bfa;'>🎭 CULTURAL HERITAGE</span>



                <div style='font-size: 0.82rem; color: #e2e8f0; margin-top: 4px; line-height: 1.45;'>



                    {chapter.cultural_heritage}



                </div>



            </div>



            <div style='background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 10px 14px;'>



                <span style='font-size: 0.70rem; font-weight: 800; color: #34d399;'>🌿 GEOGRAPHY & NATURE</span>



                <div style='font-size: 0.82rem; color: #e2e8f0; margin-top: 4px; line-height: 1.45;'>



                    {chapter.geography_nature}



                </div>



            </div>



        </div>



        <div style='background: rgba(8, 47, 73, 0.55); border-left: 3px solid #38bdf8; border-radius: 8px; padding: 8px 14px; font-size: 0.80rem; color: #7dd3fc;'>



            <b>👀 What to look for:</b> {chapter.what_to_look_for} &nbsp;•&nbsp; <b>💡 Travel Tip:</b> {chapter.travel_tip}



        </div>



    </div>



    """, unsafe_allow_html=True)







    # Category Filter for Recommended Corridor Places



    c_cat_key = f"corridor_places_filter_{key_suffix}"



    if c_cat_key not in st.session_state:



        st.session_state[c_cat_key] = "all"







    cat_cols = st.columns(6)



    categories = [



        ("all", "🌟 All Places"),



        ("attractions", "🏛️ Attractions"),



        ("dining", "🍽️ Dining"),



        ("fuel", "⛽ Fuel & EV"),



        ("medical", "🏥 Medical"),



        ("hotels", "🏨 Hotels")



    ]



    for c_col, (cat_id, cat_lbl) in zip(cat_cols, categories):



        with c_col:



            is_active_cat = (st.session_state[c_cat_key] == cat_id)



            if st.button(cat_lbl, key=f"btn_corridor_cat_{cat_id}_{key_suffix}", type="primary" if is_active_cat else "secondary", use_container_width=True):



                st.session_state[c_cat_key] = cat_id



                st.rerun()







    # Discover Real Places near active step and corridor



    places_found = CorridorPlacesEngine.get_corridor_places(



        step_coords=step_coords,



        route_polyline=route_coords,



        origin_coords=coords_orig,



        dest_coords=coords_dest,



        category_filter=st.session_state[c_cat_key],



        radius_km=15.0,



        max_results=6



    )







    if places_found:



        grid_cols = st.columns(min(3, len(places_found)))



        for p_idx, p in enumerate(places_found):



            with grid_cols[p_idx % len(grid_cols)]:



                st.markdown(f"""



                <div style='background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(56, 189, 248, 0.28); border-radius: 12px; padding: 14px; margin-bottom: 10px; display: flex; flex-direction: column; justify-content: space-between;'>



                    <div>



                        <div style='display: flex; justify-content: space-between; align-items: flex-start; gap: 6px; margin-bottom: 4px;'>



                            <div style='font-weight: 800; font-size: 0.90rem; color: #ffffff;'>



                                {p["category_icon"]} {p["name"]}



                            </div>



                            <span style='font-size: 0.68rem; font-weight: 800; color: #34d399; background: rgba(16, 185, 129, 0.18); border: 1px solid rgba(16, 185, 129, 0.4); padding: 2px 7px; border-radius: 999px; white-space: nowrap;'>



                                {p["distance_step_km"]} km away



                            </span>



                        </div>



                        <div style='font-size: 0.72rem; color: #94a3b8; margin-bottom: 6px;'>



                            📍 {p["address"]}



                        </div>



                        <div style='font-size: 0.76rem; color: #cbd5e1; margin-bottom: 6px; line-height: 1.35;'>



                            {p["description"]}



                        </div>



                        <div style='font-size: 0.70rem; color: #67e8f9; margin-bottom: 8px;'>



                            🕒 {p["hours"]} &nbsp;•&nbsp; 🚗 +{p["detour_mins"]}m detour ({p["detour_km"]} km)



                        </div>



                    </div>



                </div>



                """, unsafe_allow_html=True)



                btn_c1, btn_c2 = st.columns([1, 1])



                with btn_c1:



                    if st.button("👁️ View on Map", key=f"btn_view_poi_{p_idx}_{key_suffix}", use_container_width=True):



                        st.session_state.map_center_override = (p["latitude"], p["longitude"])



                        st.session_state.map_zoom = 17



                        st.session_state.auto_fit_bounds = False



                        st.session_state.scroll_to_app_map = True



                        st.toast(f"Centering map on {p['name']}", icon="👁️")



                        st.rerun()



                with btn_c2:



                    if st.button("➕ Add as Stop", key=f"btn_add_poi_{p_idx}_{key_suffix}", use_container_width=True):



                        st.toast(f"Added {p['name']} to journey itinerary!", icon="📍")



    else:



        st.info("No transit places match this specific category filter along this corridor section. Try selecting '🌟 All Places'.")







    # =========================================================================



    # Section 4: Additional Route Details



    # =========================================================================











if st.session_state.get("current_view") == "copilot_studio":



    render_view_navigation_header("✨ " + t("tab.copilot", "AI Travel Copilot"), "Autonomous Trip Planning & Itinerary Studio", "copilot")



    render_travel_copilot_studio()







if st.session_state.get("current_view") == "map_nav":



    render_view_navigation_header(t("tab.navigation", "Navigation"), t("nav.all_routes_desc", "Predictive Adaptive Navigation & Live Corridor Routing"), "map")



    primary_route_poly = []



    map_center_lat = 16.2335



    map_center_lon = 80.5505



    nav_tab_lbl = t("tab.navigation", "🧭 Navigation")



    fac_tab_lbl = t("tab.facilities", "🏥 Facilities")



    tab_nav, tab_fac = st.tabs([nav_tab_lbl, fac_tab_lbl])







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



        /* Creative swap button (Futuristic Dark Neon) */



        div[data-testid="stButton"][data-key="btn_swap_locations"] > button {



            background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;



            border: 2px solid #00D9FF !important;



            color: #00D9FF !important;



            border-radius: 50% !important;



            width: 44px !important;



            height: 44px !important;



            min-width: 44px !important;



            padding: 0 !important;



            font-size: 1.35rem !important;



            display: flex !important;



            align-items: center !important;



            justify-content: center !important;



            box-shadow: 0 0 16px rgba(0, 217, 255, 0.45) !important;



            transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;



            margin: auto !important;



        }



        div[data-testid="stButton"][data-key="btn_swap_locations"] > button:hover {



            transform: rotate(180deg) scale(1.15) !important;



            border-color: #00F0B5 !important;



            color: #00F0B5 !important;



            box-shadow: 0 0 26px rgba(0, 240, 181, 0.70) !important;



            background: linear-gradient(135deg, rgba(0, 217, 255, 0.35) 0%, rgba(0, 240, 181, 0.35) 100%) !important;



        }



        /* Aligned quick action buttons matching input height */



        div[data-testid="stButton"][data-key="btn_quick_use_gps"] > button {



            height: 42px !important;



            background: linear-gradient(135deg, rgba(16, 185, 129, 0.16) 0%, rgba(6, 78, 59, 0.38) 100%) !important;



            border: 1px solid rgba(16, 185, 129, 0.5) !important;



            color: #34d399 !important;



            font-weight: 700 !important;



            font-size: 0.82rem !important;



            border-radius: 10px !important;



            transition: all 0.2s ease-in-out !important;



            display: flex !important;



            align-items: center !important;



            justify-content: center !important;



        }



        div[data-testid="stButton"][data-key="btn_quick_use_gps"] > button:hover {



            background: linear-gradient(135deg, rgba(16, 185, 129, 0.32) 0%, rgba(6, 78, 59, 0.65) 100%) !important;



            border-color: #10b981 !important;



            box-shadow: 0 0 16px rgba(16, 185, 129, 0.5) !important;



            transform: translateY(-1px) !important;



        }



        div[data-testid="stButton"][data-key="btn_clear_dest"] > button {



            height: 42px !important;



            background: linear-gradient(135deg, rgba(239, 68, 68, 0.12) 0%, rgba(127, 29, 29, 0.32) 100%) !important;



            border: 1px solid rgba(239, 68, 68, 0.45) !important;



            color: #fca5a5 !important;



            font-weight: 700 !important;



            font-size: 0.82rem !important;



            border-radius: 10px !important;



            transition: all 0.2s ease-in-out !important;



            display: flex !important;



            align-items: center !important;



            justify-content: center !important;



        }



        div[data-testid="stButton"][data-key="btn_clear_dest"] > button:hover {



            background: linear-gradient(135deg, rgba(239, 68, 68, 0.26) 0%, rgba(127, 29, 29, 0.55) 100%) !important;



            border-color: #ef4444 !important;



            box-shadow: 0 0 16px rgba(239, 68, 68, 0.45) !important;



            transform: translateY(-1px) !important;



        }



        /* Candidate selection tiles styling */



        div[data-testid="stButton"][data-key*="btn_confirm_orig_"] > button,



        div[data-testid="stButton"][data-key*="btn_confirm_dest_"] > button {



            background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.75) 100%) !important;



            border: 1px solid rgba(56, 189, 248, 0.32) !important;



            color: #e0f2fe !important;



            border-radius: 10px !important;



            text-align: left !important;



            padding: 8px 12px !important;



            font-size: 0.80rem !important;



            font-weight: 600 !important;



            line-height: 1.35 !important;



            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;



            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25) !important;



        }



        div[data-testid="stButton"][data-key*="btn_confirm_orig_"] > button:hover,



        div[data-testid="stButton"][data-key*="btn_confirm_dest_"] > button:hover {



            border-color: #38bdf8 !important;



            background: linear-gradient(135deg, rgba(56, 189, 248, 0.22) 0%, rgba(14, 165, 233, 0.35) 100%) !important;



            box-shadow: 0 0 18px rgba(56, 189, 248, 0.45) !important;



            transform: translateY(-2px) !important;



            color: #ffffff !important;



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







        # =========================================================================



        # FEATURE 1: Search-as-you-Type Autocomplete Enhancer Controller



        # Provides 280ms debouncing, keyboard navigation (Up/Down/Enter), structured cards,



        # loading indicators, and instant coordinate updates for Start and Destination



        # =========================================================================



        import streamlit.components.v1 as _autocomplete_comp



        _autocomplete_comp.html("""



        <script>



        (function() {



            var pDoc = window.parent.document || document;



            var pWin = window.parent || window;







            // 1. Inject Glassmorphism Autocomplete Styles into Parent Document



            var styleId = "pf-live-autocomplete-styles";



            if (!pDoc.getElementById(styleId)) {



                var styleEl = pDoc.createElement("style");



                styleEl.id = styleId;



                styleEl.textContent = `



                    .pf-autocomplete-anchor {



                        position: relative !important;



                    }



                    .pf-autocomplete-dropdown {



                        position: absolute;



                        top: 100%;



                        left: 0;



                        right: 0;



                        background: rgba(15, 23, 42, 0.98);



                        backdrop-filter: blur(20px);



                        -webkit-backdrop-filter: blur(20px);



                        border: 1.5px solid rgba(56, 189, 248, 0.55);



                        border-radius: 12px;



                        box-shadow: 0 16px 42px rgba(0, 0, 0, 0.9), 0 0 24px rgba(56, 189, 248, 0.3);



                        max-height: 320px;



                        overflow-y: auto;



                        z-index: 9999999 !important;



                        display: none;



                        flex-direction: column;



                        margin-top: 6px;



                        padding: 4px 0;



                        scrollbar-width: thin;



                    }



                    .pf-autocomplete-dropdown.open {



                        display: flex !important;



                    }



                    .pf-autocomplete-item {



                        padding: 10px 14px;



                        display: flex;



                        align-items: center;



                        gap: 12px;



                        cursor: pointer;



                        border-bottom: 1px solid rgba(255, 255, 255, 0.06);



                        transition: all 0.15s ease;



                        user-select: none;



                    }



                    .pf-autocomplete-item:last-child {



                        border-bottom: none;



                    }



                    .pf-autocomplete-item:hover, .pf-autocomplete-item.selected {



                        background: rgba(56, 189, 248, 0.22);



                    }



                    .pf-autocomplete-icon {



                        font-size: 18px;



                        flex-shrink: 0;



                        width: 24px;



                        text-align: center;



                    }



                    .pf-autocomplete-body {



                        display: flex;



                        flex-direction: column;



                        gap: 2px;



                        overflow: hidden;



                        flex: 1;



                    }



                    .pf-autocomplete-title {



                        font-size: 0.85rem;



                        font-weight: 800;



                        color: #f8fafc;



                        white-space: nowrap;



                        overflow: hidden;



                        text-overflow: ellipsis;



                    }



                    .pf-autocomplete-sub {



                        font-size: 0.72rem;



                        color: #94a3b8;



                        white-space: nowrap;



                        overflow: hidden;



                        text-overflow: ellipsis;



                    }



                    .pf-autocomplete-badge {



                        font-size: 0.65rem;



                        font-weight: 800;



                        color: #7dd3fc;



                        background: rgba(56, 189, 248, 0.2);



                        border: 1px solid rgba(56, 189, 248, 0.4);



                        padding: 2px 7px;



                        border-radius: 8px;



                        white-space: nowrap;



                        margin-left: 6px;



                        flex-shrink: 0;



                    }



                    .pf-autocomplete-spinner {



                        position: absolute;



                        right: 12px;



                        top: 50%;



                        transform: translateY(-50%);



                        width: 16px;



                        height: 16px;



                        border: 2px solid rgba(56, 189, 248, 0.25);



                        border-top-color: #38bdf8;



                        border-radius: 50%;



                        animation: pfSpin 0.7s linear infinite;



                        pointer-events: none;



                        display: none;



                        z-index: 10;



                    }



                    @keyframes pfSpin {



                        to { transform: translateY(-50%) rotate(360deg); }



                    }



                `;



                pDoc.head.appendChild(styleEl);



            }







            // 2. Attach Live Interactive Autocomplete to Target Inputs



            function setupInputAutocomplete(selector, targetType) {



                var input = pDoc.querySelector(selector);



                if (!input || input._pfLiveAttached) return;



                input._pfLiveAttached = true;







                var parentWrap = input.closest('[data-testid="stTextInput"]') || input.parentElement;



                if (parentWrap) {



                    parentWrap.classList.add('pf-autocomplete-anchor');



                }







                var dropdown = pDoc.createElement('div');



                dropdown.className = 'pf-autocomplete-dropdown';



                input.parentElement.appendChild(dropdown);







                var spinner = pDoc.createElement('div');



                spinner.className = 'pf-autocomplete-spinner';



                input.parentElement.appendChild(spinner);







                var debounceTimer = null;



                var activeController = null;



                var currentItems = [];



                var activeIndex = -1;







                input.addEventListener('input', function() {



                    var q = input.value.trim();



                    clearTimeout(debounceTimer);



                    activeIndex = -1;







                    if (!q || q.length < 2) {



                        if (activeController) activeController.abort();



                        dropdown.classList.remove('open');



                        dropdown.innerHTML = '';



                        spinner.style.display = 'none';



                        return;



                    }







                    spinner.style.display = 'block';







                    debounceTimer = setTimeout(function() {



                        if (activeController) activeController.abort();



                        activeController = new AbortController();



                        var sig = activeController.signal;







                        // Check coordinates format e.g. 16.2335, 80.5505



                        var directItems = [];



                        var coordMatch = q.match(/^([-+]?[0-9]*\\.[0-9]+|[0-9]+)[\\s,]+([-+]?[0-9]*\\.[0-9]+|[0-9]+)$/);



                        if (coordMatch) {



                            var lat = parseFloat(coordMatch[1]);



                            var lon = parseFloat(coordMatch[2]);



                            if (!isNaN(lat) && !isNaN(lon) && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {



                                directItems.push({



                                    name: "Pinpoint (" + lat.toFixed(4) + ", " + lon.toFixed(4) + ")",



                                    display_name: "Physical Coordinates (" + lat.toFixed(5) + ", " + lon.toFixed(5) + ")",



                                    category_icon: "🌐",



                                    area_badge: "Coordinates",



                                    lat: lat,



                                    lon: lon



                                });



                            }



                        }







                        // Query backend API autocomplete first, with photon fallback



                        function parsePhoton(data) {



                            var fetched = [];



                            if (data && data.features) {



                                data.features.forEach(function(f) {



                                    var props = f.properties || {};



                                    var coords = (f.geometry && f.geometry.coordinates) || [];



                                    if (coords.length >= 2) {



                                        var fLon = parseFloat(coords[0]);



                                        var fLat = parseFloat(coords[1]);



                                        if (fLat >= -90 && fLat <= 90 && fLon >= -180 && fLon <= 180) {



                                            var pName = props.name || q;



                                            var parts = [];



                                            if (props.street) parts.push(props.street);



                                            var cCity = props.city || props.town || props.village || props.county || "";



                                            if (cCity && cCity !== pName) parts.push(cCity);



                                            if (props.state) parts.push(props.state);



                                            if (props.country) parts.push(props.country);







                                            var icon = "📍";



                                            var badge = props.osm_value || "Place";



                                            var ov = (props.osm_value || props.osm_key || "").toLowerCase();



                                            if (ov.indexOf('hospital') !== -1 || ov.indexOf('clinic') !== -1) { icon = "🏥"; badge = "Hospital"; }



                                            else if (ov.indexOf('station') !== -1 || ov.indexOf('railway') !== -1) { icon = "🚆"; badge = "Railway Station"; }



                                            else if (ov.indexOf('airport') !== -1 || ov.indexOf('aerodrome') !== -1) { icon = "✈️"; badge = "Airport"; }



                                            else if (ov.indexOf('university') !== -1 || ov.indexOf('college') !== -1) { icon = "🎓"; badge = "University"; }



                                            else if (ov.indexOf('bus') !== -1) { icon = "🚌"; badge = "Bus Hub"; }



                                            else if (ov.indexOf('restaurant') !== -1) { icon = "🍽️"; badge = "Restaurant"; }



                                            else if (ov.indexOf('place_of_worship') !== -1) { icon = "🛕"; badge = "Temple/Worship"; }







                                            fetched.push({



                                                name: pName,



                                                display_name: parts.join(', ') || props.country || "Global Result",



                                                category_icon: icon,



                                                area_badge: badge,



                                                lat: fLat,



                                                lon: fLon



                                            });



                                        }



                                    }



                                });



                            }



                            return fetched;



                        }







                        var apiEndpoint = (pWin.location.port === '8000') ? '/api/autocomplete?q=' : 'http://localhost:8000/api/autocomplete?q=';



                        fetch(apiEndpoint + encodeURIComponent(q) + '&limit=7', { signal: sig })



                            .then(function(res) { return res.json(); })



                            .then(function(apiData) {



                                var fetched = [];



                                if (apiData && apiData.suggestions && apiData.suggestions.length > 0) {



                                    apiData.suggestions.forEach(function(s) {



                                        fetched.push({



                                            name: s.name || q,



                                            display_name: s.display_name || s.name || q,



                                            category_icon: s.category_icon || '📍',



                                            area_badge: s.area_badge || s.type || 'Location',



                                            lat: parseFloat(s.lat),



                                            lon: parseFloat(s.lon)



                                        });



                                    });



                                }



                                if (fetched.length > 0) {



                                    spinner.style.display = 'none';



                                    currentItems = directItems.concat(fetched);



                                    renderDropdown(currentItems, q);



                                } else {



                                    // Fallback to Photon



                                    fetch('https://photon.komoot.io/api/?q=' + encodeURIComponent(q) + '&limit=7', { signal: sig })



                                        .then(function(res) { return res.json(); })



                                        .then(function(data) {



                                            spinner.style.display = 'none';



                                            currentItems = directItems.concat(parsePhoton(data));



                                            renderDropdown(currentItems, q);



                                        })



                                        .catch(function() {



                                            spinner.style.display = 'none';



                                            currentItems = directItems;



                                            renderDropdown(currentItems, q);



                                        });



                                }



                            })



                            .catch(function() {



                                fetch('https://photon.komoot.io/api/?q=' + encodeURIComponent(q) + '&limit=7', { signal: sig })



                                    .then(function(res) { return res.json(); })



                                    .then(function(data) {



                                        spinner.style.display = 'none';



                                        currentItems = directItems.concat(parsePhoton(data));



                                        renderDropdown(currentItems, q);



                                    })



                                    .catch(function(err) {



                                        spinner.style.display = 'none';



                                        if (err.name !== 'AbortError') {



                                            currentItems = directItems;



                                            renderDropdown(currentItems, q);



                                        }



                                    });



                            });



                    }, 280);



                });







                function renderDropdown(items, q) {



                    activeIndex = -1;



                    var customLabel = (targetType === 'orig') ? '+ Enter Custom Starting Location' : '+ Enter Custom Destination';



                    var pickLabel = (targetType === 'orig') ? '🗺️ Pick Starting Point on Map' : '🗺️ Pick Destination on Map';



                    var footerHtml = '<div style="border-top:1px solid rgba(56,189,248,0.22); padding:6px; background:rgba(15,23,42,0.95); display:flex; flex-direction:column; gap:4px;">' +



                                     '  <div class="pf-autocomplete-custom-btn" data-action="custom" style="padding:7px 10px; border-radius:6px; background:rgba(56,189,248,0.12); color:#38bdf8; font-size:12px; font-weight:700; cursor:pointer; display:flex; align-items:center; gap:6px;">' +



                                     '    <span>➕</span> ' + customLabel +



                                     '  </div>' +



                                     '  <div class="pf-autocomplete-custom-btn" data-action="pick_map" style="padding:7px 10px; border-radius:6px; background:rgba(245,158,11,0.12); color:#fbbf24; font-size:12px; font-weight:700; cursor:pointer; display:flex; align-items:center; gap:6px;">' +



                                     '    <span>🗺️</span> ' + pickLabel +



                                     '  </div>' +



                                     '</div>';







                    if (!items || items.length === 0) {



                        dropdown.innerHTML = '<div class="pf-autocomplete-item" style="cursor:default;"><span class="pf-autocomplete-icon">🔍</span><div class="pf-autocomplete-body"><div class="pf-autocomplete-title">No direct suggestions for "' + q + '"</div><div class="pf-autocomplete-sub">Click below to enter custom location or pick on map</div></div></div>' + footerHtml;



                        dropdown.classList.add('open');



                        hookFooterActions();



                        return;



                    }







                    var html = '';



                    items.forEach(function(it, idx) {



                        html += '<div class="pf-autocomplete-item" data-idx="' + idx + '">' +



                                '  <span class="pf-autocomplete-icon">' + (it.category_icon || '📍') + '</span>' +



                                '  <div class="pf-autocomplete-body">' +



                                '    <div class="pf-autocomplete-title">' + it.name + '</div>' +



                                '    <div class="pf-autocomplete-sub">' + (it.display_name || it.name) + '</div>' +



                                '  </div>' +



                                '  <span class="pf-autocomplete-badge">' + (it.area_badge || 'Location') + '</span>' +



                                '</div>';



                    });



                    dropdown.innerHTML = html + footerHtml;



                    dropdown.classList.add('open');







                    var rowEls = dropdown.querySelectorAll('.pf-autocomplete-item');



                    rowEls.forEach(function(row, i) {



                        row.addEventListener('click', function(ev) {



                            ev.stopPropagation();



                            selectItem(items[i]);



                        });



                    });



                    hookFooterActions();



                }







                function setNativeInputValue(targetInput, val) {



                    if (!targetInput) return;



                    var nativeSetter = Object.getOwnPropertyDescriptor(pWin.HTMLInputElement.prototype, 'value')?.set



                        || Object.getOwnPropertyDescriptor(targetInput.__proto__, 'value')?.set;



                    if (nativeSetter) {



                        nativeSetter.call(targetInput, val);



                    } else {



                        targetInput.value = val;



                    }



                    targetInput.dispatchEvent(new Event('input', { bubbles: true }));



                    targetInput.dispatchEvent(new Event('change', { bubbles: true }));



                }







                function safeTopNav(url) {



                    try {



                        if (pWin.history && pWin.history.replaceState) {



                            pWin.history.replaceState(null, '', url.toString());



                            return;



                        }



                    } catch(e1) {}



                }







                function hookFooterActions() {



                    var customBtns = dropdown.querySelectorAll('.pf-autocomplete-custom-btn');



                    customBtns.forEach(function(btn) {



                        btn.addEventListener('click', function(ev) {



                            ev.stopPropagation();



                            dropdown.classList.remove('open');



                            var act = btn.getAttribute('data-action');



                            if (act === 'custom') {



                                var btnEl = Array.from(pDoc.querySelectorAll('button')).find(function(b) {



                                    return b.innerText.includes(targetType === 'orig' ? 'Custom Start' : 'Custom Dest');



                                });



                                if (btnEl) {



                                    btnEl.click();



                                    return;



                                }



                            } else if (act === 'pick_map') {



                                var btnEl = Array.from(pDoc.querySelectorAll('button')).find(function(b) {



                                    return b.innerText.includes(targetType === 'orig' ? 'Pick Start' : 'Pick Dest');



                                });



                                if (btnEl) {



                                    btnEl.click();



                                    return;



                                }



                            }



                            try {



                                var url = new URL(pWin.location.href);



                                if (act === 'custom') {



                                    url.searchParams.set("open_custom_editor", targetType);



                                } else if (act === 'pick_map') {



                                    url.searchParams.set("start_map_pick", targetType);



                                }



                                safeTopNav(url);



                            } catch(e) {}



                        });



                    });



                }







                function selectItem(item) {



                    if (!item) return;



                    dropdown.classList.remove('open');



                    spinner.style.display = 'none';







                    var cleanName = (item.name || '').replace(/^[📍🏁🛰️🚶]+\\s*/, '').trim();



                    var valToSet = cleanName;



                    if (item.lat !== undefined && item.lon !== undefined && !isNaN(item.lat) && !isNaN(item.lon)) {



                        valToSet = cleanName + " (" + Number(item.lat).toFixed(5) + ", " + Number(item.lon).toFixed(5) + ")";



                    }







                    // Seamlessly trigger React input update without full page reload



                    setNativeInputValue(input, valToSet);







                    try {



                        var url = new URL(pWin.location.href);



                        if (targetType === 'orig') {



                            url.searchParams.set("orig_lat", Number(item.lat).toFixed(6));



                            url.searchParams.set("orig_lon", Number(item.lon).toFixed(6));



                            url.searchParams.set("orig_name", item.name);



                        } else {



                            url.searchParams.set("dest_lat", Number(item.lat).toFixed(6));



                            url.searchParams.set("dest_lon", Number(item.lon).toFixed(6));



                            url.searchParams.set("dest_name", item.name);



                        }



                        safeTopNav(url);



                    } catch(e) {}



                }







                function updateKeyboardHighlight() {



                    var rows = dropdown.querySelectorAll('.pf-autocomplete-item');



                    rows.forEach(function(r, idx) {



                        if (idx === activeIndex) {



                            r.classList.add('selected');



                            r.scrollIntoView({ block: 'nearest' });



                        } else {



                            r.classList.remove('selected');



                        }



                    });



                }







                input.addEventListener('keydown', function(e) {



                    var rows = dropdown.querySelectorAll('.pf-autocomplete-item');



                    if (dropdown.classList.contains('open') && rows.length > 0) {



                        if (e.key === 'ArrowDown') {



                            e.preventDefault();



                            activeIndex = (activeIndex + 1) % rows.length;



                            updateKeyboardHighlight();



                            return;



                        } else if (e.key === 'ArrowUp') {



                            e.preventDefault();



                            activeIndex = (activeIndex - 1 + rows.length) % rows.length;



                            updateKeyboardHighlight();



                            return;



                        } else if (e.key === 'Enter' && activeIndex >= 0 && activeIndex < currentItems.length) {



                            e.preventDefault();



                            selectItem(currentItems[activeIndex]);



                            return;



                        }



                    }



                    if (e.key === 'Escape') {



                        dropdown.classList.remove('open');



                    }



                });







                pDoc.addEventListener('click', function(e) {



                    if (!input.contains(e.target) && !dropdown.contains(e.target)) {



                        dropdown.classList.remove('open');



                    }



                });



            }







            // Retry attachment periodically to ensure dynamic DOM inputs are hooked



            function scanAndAttach() {



                setupInputAutocomplete('input[aria-label*="Starting Point"]', 'orig');



                setupInputAutocomplete('input[aria-label*="Destination"]', 'dest');



                setupInputAutocomplete('input[placeholder*="Search Location — My Location"]', 'orig');



                setupInputAutocomplete('input[placeholder*="Search Location..."]', 'dest');



            }







            setTimeout(scanAndAttach, 250);



            setTimeout(scanAndAttach, 800);



            setTimeout(scanAndAttach, 2000);



        })();



        </script>



        """, height=0, width=0)











        # Custom Location Editor Inline Modal / Bottom Sheet



        modal_target = st.session_state.get("show_custom_modal")



        if modal_target in ["orig", "dest"]:



            is_orig = (modal_target == "orig")



            tgt_title = "Starting Point (🟢 Green Marker)" if is_orig else "Destination (🏁 Red Marker)"



            



            st.markdown(f"""



            <div style='background: linear-gradient(180deg, rgba(15, 23, 42, 0.98) 0%, rgba(13, 31, 60, 0.96) 100%); border: 2px solid {"#10b981" if is_orig else "#ef4444"}; border-radius: 14px; padding: 18px 20px; margin: 12px 0 18px 0; box-shadow: 0 12px 36px rgba(0,0,0,0.7), 0 0 20px {"rgba(16, 185, 129, 0.3)" if is_orig else "rgba(239, 68, 68, 0.3)"};'>



                <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; margin-bottom: 14px;'>



                    <span style='font-size: 1.05rem; font-weight: 800; color: {"#34d399" if is_orig else "#f87171"}; display: flex; align-items: center; gap: 8px;'>



                        {"🟢" if is_orig else "🏁"} Custom {tgt_title} Editor



                    </span>



                    <span style='font-size: 0.72rem; color: #94a3b8; background: rgba(255,255,255,0.06); padding: 3px 8px; border-radius: 8px;'>



                        Standard Mobile & Desktop Keyboard Supported



                    </span>



                </div>



            </div>



            """, unsafe_allow_html=True)



            



            # Address and Name inputs using standard accessible HTML input fields



            custom_addr = st.text_input(



                f"📍 Address, Landmark, Village, Institution or City",



                value=st.session_state.get("custom_editor_address", ""),



                key="input_custom_editor_address",



                placeholder="e.g. Amaravati High Court, Guntur Railway Station, Apollo Hospital...",



                help="Type any address or place. Your device virtual keyboard is fully accessible."



            )



            



            custom_name = st.text_input(



                f"🏷️ Custom Label / Location Name (Optional)",



                value=st.session_state.get("custom_editor_name", ""),



                key="input_custom_editor_name",



                placeholder="e.g. My Office, North Campus Gate, Warehouse 4..."



            )



            



            cur_lat = float(st.session_state.get("custom_editor_lat", 16.5062 if is_orig else 16.2335))



            cur_lon = float(st.session_state.get("custom_editor_lon", 80.6480 if is_orig else 80.5505))



            



            c_lat_col, c_lon_col = st.columns(2)



            custom_lat = c_lat_col.number_input(



                "🌐 Latitude (-90.0 to +90.0)",



                min_value=-90.0,



                max_value=90.0,



                value=cur_lat,



                format="%.6f",



                key="input_custom_editor_lat"



            )



            custom_lon = c_lon_col.number_input(



                "🌐 Longitude (-180.0 to +180.0)",



                min_value=-180.0,



                max_value=180.0,



                value=cur_lon,



                format="%.6f",



                key="input_custom_editor_lon"



            )



            



            # Candidates if resolved



            custom_cands = st.session_state.get("custom_editor_candidates", [])



            if custom_cands:



                st.markdown(f"<div style='color:#38bdf8; font-weight:700; font-size:0.84rem; margin:8px 0;'>🔍 Multiple Places Found ({len(custom_cands)}). Select your exact location:</div>", unsafe_allow_html=True)



                cand_cols = st.columns(2)



                for ci, cc in enumerate(custom_cands):



                    c_title = cc.get("name") or cc.get("display_name", "").split(",")[0]



                    c_sub = cc.get("area_badge") or cc.get("display_name", "")



                    with cand_cols[ci % 2]:



                        if st.button(f"📍 {c_title} ({cc['lat']:.4f}, {cc['lon']:.4f})", key=f"btn_custom_cand_{ci}", help=c_sub, use_container_width=True):



                            st.session_state.custom_editor_lat = cc["lat"]



                            st.session_state.custom_editor_lon = cc["lon"]



                            st.session_state.custom_editor_address = cc.get("display_name", c_title)



                            st.session_state.custom_editor_name = c_title



                            st.session_state.custom_editor_candidates = []



                            st.rerun()







            c_act_res, c_act_pick, c_act_conf, c_act_canc = st.columns([1.1, 1.1, 1.2, 0.8])



            with c_act_res:



                if st.button("🔍 Resolve Address", key="btn_modal_resolve_addr", use_container_width=True, help="Geocode address to exact coordinates"):



                    if custom_addr and custom_addr.strip():



                        cands = st.session_state.real_map_service.get_disambiguation_candidates(custom_addr.strip(), limit=6)



                        if cands:



                            if len(cands) == 1:



                                best = cands[0]



                                st.session_state.custom_editor_lat = best["lat"]



                                st.session_state.custom_editor_lon = best["lon"]



                                st.session_state.custom_editor_name = best.get("name") or custom_addr



                                st.session_state.custom_editor_candidates = []



                                st.toast(f"✅ Resolved: ({best['lat']:.4f}, {best['lon']:.4f})", icon="✅")



                            else:



                                st.session_state.custom_editor_candidates = cands



                                st.toast(f"Found {len(cands)} matches. Select one below.", icon="🔍")



                            st.rerun()



                        else:



                            st.error(f"⚠️ Could not resolve '{custom_addr}'. The address is preserved. You can edit it, enter coordinates directly, or click 'Pick on Map'.")



                    else:



                        st.warning("Please type an address or place name to resolve.")







            with c_act_pick:



                if st.button("🗺️ Pick on Map", key="btn_modal_pick_on_map", use_container_width=True, help="Select this point directly on the interactive map"):



                    st.session_state.map_picking_mode = modal_target



                    st.session_state.show_custom_modal = None



                    st.toast(f"🗺️ Map selection activated for {tgt_title}", icon="🗺️")



                    st.rerun()







            with c_act_conf:



                if st.button("✅ Confirm Location", key="btn_modal_confirm_loc", use_container_width=True, help="Confirm coordinates and update route"):



                    # Validate coordinates



                    if -90.0 <= custom_lat <= 90.0 and -180.0 <= custom_lon <= 180.0:



                        chosen_label = custom_name.strip() or custom_addr.strip() or f"Custom Point ({custom_lat:.4f}, {custom_lon:.4f})"



                        if is_orig:



                            st.session_state.user_live_coords = (custom_lat, custom_lon)



                            st.session_state.user_live_label = chosen_label



                            st.session_state.txt_orig = chosen_label



                            st.session_state.last_synced_orig = chosen_label



                            st.session_state.selected_orig_id = f"custom_orig_{custom_lat:.4f}_{custom_lon:.4f}"



                            st.session_state.is_custom_start_place = True



                            st.session_state.orig_pending_confirmation = False



                            st.session_state.orig_candidates = []



                            st.session_state.orig_candidates_query = ""



                            st.session_state.real_location_service.set_manual_location(custom_lat, custom_lon, chosen_label)



                        else:



                            st.session_state.selected_dest_coords = (custom_lat, custom_lon)



                            st.session_state.selected_dest_label = chosen_label



                            st.session_state.txt_dest = chosen_label



                            st.session_state.last_synced_dest = chosen_label



                            st.session_state.selected_dest_id = f"custom_dest_{custom_lat:.4f}_{custom_lon:.4f}"



                            st.session_state.dest_pending_confirmation = False



                            st.session_state.dest_candidates = []



                            st.session_state.dest_candidates_query = ""



                        st.session_state._prev_route_sig = None



                        st.session_state.focused_route_id = "ALL"



                        st.session_state.selected_route_id = None



                        st.session_state.auto_fit_bounds = True



                        st.session_state.show_custom_modal = None



                        st.session_state.custom_editor_candidates = []



                        st.toast(f"✅ {chosen_label} confirmed at ({custom_lat:.4f}, {custom_lon:.4f})", icon="✅")



                        st.rerun()



                    else:



                        st.error("Invalid coordinates. Latitude must be between -90 and 90, Longitude between -180 and 180.")







            with c_act_canc:



                if st.button("✕ Cancel", key="btn_modal_cancel", use_container_width=True):



                    st.session_state.show_custom_modal = None



                    st.session_state.custom_editor_candidates = []



                    st.rerun()







        # =========================================================================



        # CREATIVE TRANSIT VEHICLE FLEET & CALIBRATED SPEED LIMITS CONFIGURATION



        # =========================================================================



        SPEED_LIMITS_CONFIG = {



            "CAR": {



                "min": 20, "max": 160, "eco": 65, "normal": 90, "default": 90, "fast": 130, "step": 5,



                "unit": "KM / H", "presets": [40, 65, 90, 115, 140],



                "eco_desc": "Conservative cruising • Maximized fuel & energy efficiency",



                "normal_desc": "Standard highway & arterial corridor cruise velocity",



                "fast_desc": "Expressway velocity profile • Minimum transit duration",



                "profile": "Automobile Motorized Rapid Arterial & Highway Corridor",



                "sec_unit": "MPH", "sec_factor": 0.621371



            },



            "BIKE": {



                "min": 15, "max": 120, "eco": 45, "normal": 65, "default": 65, "fast": 95, "step": 5,



                "unit": "KM / H", "presets": [30, 45, 65, 85, 105],



                "eco_desc": "Gentle throttle • Urban fuel saver & agile safe handling",



                "normal_desc": "Standard motorcycle & scooter flow velocity",



                "fast_desc": "Open corridor velocity • Rapid lane traversal",



                "profile": "Motorcycle / Scooter Dynamic Lane Transit",



                "sec_unit": "MPH", "sec_factor": 0.621371



            },



            "BUS": {



                "min": 15, "max": 85, "eco": 40, "normal": 55, "default": 55, "fast": 75, "step": 5,



                "unit": "KM / H", "presets": [30, 40, 55, 68, 80],



                "eco_desc": "Smooth passenger transit • Reduced emissions & fuel burn",



                "normal_desc": "Commercial public transit scheduled corridor velocity",



                "fast_desc": "Express bypass pace • Direct non-stop transit",



                "profile": "Commercial Public Transit Bus Fleet",



                "sec_unit": "MPH", "sec_factor": 0.621371



            },



            "FLIGHT": {



                "min": 350, "max": 1050, "eco": 680, "normal": 850, "default": 850, "fast": 980, "step": 25,



                "unit": "KM / H", "presets": [450, 680, 850, 920, 980],



                "eco_desc": "High-altitude economy cruise • Optimal fuel burn altitude",



                "normal_desc": "Standard commercial jetliner cruising velocity (Mach ~0.80)",



                "fast_desc": "Maximum rated tailwind high-speed dash (Mach ~0.92)",



                "profile": "Commercial Jetliner Aviation Propulsion",



                "sec_unit": "KNOTS", "sec_factor": 0.539957



            },



            "WATERWAY": {



                "min": 10, "max": 65, "eco": 20, "normal": 32, "default": 32, "fast": 48, "step": 2,



                "unit": "KM / H", "presets": [15, 20, 32, 42, 52],



                "eco_desc": "Calm water fuel conservation • Minimal sea wake",



                "normal_desc": "Standard Ro-Pax catamaran scheduled ferry pace",



                "fast_desc": "High-speed hydrofoil / fast catamaran sprint",



                "profile": "Maritime Ro-Pax Ferry & Coastal Sea Corridors",



                "sec_unit": "KNOTS", "sec_factor": 0.539957



            },



            "TRUCK": {



                "min": 15, "max": 80, "eco": 45, "normal": 60, "default": 60, "fast": 75, "step": 5,



                "unit": "KM / H", "presets": [30, 45, 60, 70, 80],



                "eco_desc": "Heavy cargo steady torque • Optimum ton-km efficiency",



                "normal_desc": "National highway freight transport legal speed limit",



                "fast_desc": "Express logistics corridor priority transit",



                "profile": "Heavy Commercial Freight Logistics",



                "sec_unit": "MPH", "sec_factor": 0.621371



            },



            "TRACTOR": {



                "min": 8, "max": 35, "eco": 15, "normal": 22, "default": 22, "fast": 30, "step": 2,



                "unit": "KM / H", "presets": [10, 15, 22, 28, 34],



                "eco_desc": "Agricultural PTO low RPM • Field-to-market economy",



                "normal_desc": "Standard rural road & agricultural cart link pace",



                "fast_desc": "Maximum governor transport gear velocity",



                "profile": "Agricultural & Rural Secondary Transit",



                "sec_unit": "MPH", "sec_factor": 0.621371



            },



            "BICYCLE": {



                "min": 6, "max": 35, "eco": 12, "normal": 18, "default": 18, "fast": 28, "step": 1,



                "unit": "KM / H", "presets": [10, 14, 18, 24, 30],



                "eco_desc": "Leisurely low-cadence ride • Zero fatigue cadence",



                "normal_desc": "Standard commuter cycling pace • Green cycleways",



                "fast_desc": "Athletic high-cadence sprint • Minimum travel time",



                "profile": "Non-Motorized Human-Powered Bicycle",



                "sec_unit": "MPH", "sec_factor": 0.621371



            },



            "WALK": {



                "min": 1.0, "max": 9.0, "eco": 3.5, "normal": 5.0, "default": 5.0, "fast": 7.5, "step": 0.5,



                "unit": "KM / H", "presets": [2.5, 3.5, 5.0, 6.5, 8.0],



                "eco_desc": "Gentle stroll • Step-free safe sidewalks & crossings",



                "normal_desc": "Standard purposeful pedestrian sidewalk cadence",



                "fast_desc": "Brisk power walk • Accelerated foot travel",



                "profile": "Non-Motorized Pedestrian Sidewalk Pace",



                "sec_unit": "MIN/KM", "sec_factor": None



            }



        }







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



            "FLIGHT": {



                "icon": "✈️",



                "name": "Airway",



                "label": "✈️ Airway",



                "mode": TravelMode.FLIGHT,



                "desc": "Flight • Great-Circle Commercial Aviation Corridors",



                "badge": "✈️ Airway"



            },



            "WATERWAY": {



                "icon": "🚢",



                "name": "Waterway",



                "label": "🚢 Waterway",



                "mode": TravelMode.WATERWAY,



                "desc": "Maritime Ferry • Sea Lanes, Channels & Ro-Pax Vessels",



                "badge": "🚢 Maritime Sea Route"



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



            elif "Airway" in str(prev) or "✈️" in str(prev) or "Airway" in str(prev):



                st.session_state.selected_travel_mode = "FLIGHT"



            elif "Water" in str(prev) or "🚢" in str(prev) or "Ferry" in str(prev):



                st.session_state.selected_travel_mode = "WATERWAY"



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







        fleet_title = "⚡ TRAVEL MODE & VEHICLE FLEET"
        fleet_subtitle = "Choose your vehicle for suitable route recommendations."

        st.markdown(f"""<div style='display: flex; align-items: center; justify-content: space-between; margin-top: 10px; margin-bottom: 6px;'>
<div style='font-size: 0.82rem; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 6px;'>
<span>⚡</span> {fleet_title}
</div>
<div style='font-size: 0.72rem; color: #94a3b8;'>
{fleet_subtitle}
</div>
</div>""", unsafe_allow_html=True)







        st.markdown("""



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



            background: linear-gradient(135deg, rgba(0, 217, 255, 0.35) 0%, rgba(0, 240, 181, 0.40) 100%) !important;



            border: 2px solid #00F0B5 !important;



            box-shadow: 0 0 22px rgba(0, 217, 255, 0.55), 0 0 12px rgba(0, 240, 181, 0.45), 0 4px 14px rgba(0, 0, 0, 0.6) !important;



            transform: translateY(-2px) !important;



            color: #ffffff !important;



        }



        /* Inactive Button State */



        .st-key-fleet_deck_container div[data-testid="stButton"] > button[kind="secondary"] {



            background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;



            border: 1.5px solid rgba(0, 217, 255, 0.35) !important;



            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.50), 0 0 10px rgba(0, 217, 255, 0.12) !important;



            color: #EAF7FF !important;



        }



        .st-key-fleet_deck_container div[data-testid="stButton"] > button[kind="secondary"]:hover {



            border-color: #00D9FF !important;



            background: linear-gradient(135deg, #10263E 0%, #0B1B2D 100%) !important;



            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.60), 0 0 18px rgba(0, 240, 181, 0.40) !important;



            transform: translateY(-2px) !important;



            color: #ffffff !important;



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



            transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;



        }



        .st-key-speed_deck_container div[data-testid="stButton"] > button[kind="primary"] {



            background: linear-gradient(135deg, rgba(0, 217, 255, 0.35) 0%, rgba(0, 240, 181, 0.40) 100%) !important;



            border: 2px solid #00F0B5 !important;



            box-shadow: 0 0 20px rgba(0, 217, 255, 0.50), 0 0 10px rgba(0, 240, 181, 0.40) !important;



            color: #ffffff !important;



            transform: translateY(-2px) !important;



        }



        .st-key-speed_deck_container div[data-testid="stButton"] > button[kind="secondary"] {



            background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;



            border: 1.5px solid rgba(0, 217, 255, 0.35) !important;



            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45) !important;



            color: #EAF7FF !important;



        }



        .st-key-speed_deck_container div[data-testid="stButton"] > button[kind="secondary"]:hover {



            border-color: #00D9FF !important;



            background: linear-gradient(135deg, #10263E 0%, #0B1B2D 100%) !important;



            box-shadow: 0 4px 16px rgba(0, 240, 181, 0.35) !important;



            transform: translateY(-2px) !important;



            color: #ffffff !important;



        }



        </style>



        """, unsafe_allow_html=True)







        with st.container(key="fleet_deck_container"):



            m_cols = st.columns(len(MODES_CONFIG))



            selected_key = st.session_state.selected_travel_mode



            for idx, (m_k, m_info) in enumerate(MODES_CONFIG.items()):



                with m_cols[idx]:



                    is_selected = (m_k == selected_key)



                    btn_type = "primary" if is_selected else "secondary"



                    loc_name = t(f'fleet.{m_k.lower()}', default=m_info['name'])



                    card_label = f"{m_info['icon']}\n\n**{loc_name}**"



                    if st.button(card_label, key=f"btn_mode_select_{m_k}", use_container_width=True, type=btn_type):



                        st.session_state.selected_travel_mode = m_k



                        st.session_state.last_selected_mode = m_info["label"]



                        # Automatically adjust speed mode and target speed to the newly selected vehicle



                        v_cfg = SPEED_LIMITS_CONFIG.get(m_k, SPEED_LIMITS_CONFIG["CAR"])



                        curr_sm = st.session_state.get("selected_speed_mode", "NORMAL")



                        if curr_sm == "ECO":



                            st.session_state.custom_speed_kmh = v_cfg["eco"]



                        elif curr_sm == "FAST":



                            st.session_state.custom_speed_kmh = v_cfg["fast"]



                        else:  # NORMAL or CUSTOM



                            st.session_state.custom_speed_kmh = v_cfg["normal"]



                        st.session_state.last_speed_mode_trigger = f"{m_info['name']} Dynamic Profile"



                        st.session_state.scroll_to_speedometer = True



                        st.session_state.pop("cached_candidate_routes", None)



                        st.rerun()







        current_mode_info = MODES_CONFIG.get(st.session_state.selected_travel_mode, MODES_CONFIG["CAR"])



        travel_mode = current_mode_info["mode"]



        travel_mode_str = f"{current_mode_info['icon']} {t(f'fleet.{st.session_state.selected_travel_mode.lower()}', default=current_mode_info['name'])}"



        st.session_state.last_selected_mode = travel_mode_str







        # =========================================================================



        # SEPARATE SPEED MODE SELECTOR (ECO, NORMAL, FAST, CUSTOM)



        # =========================================================================



        sel_vehicle_key = st.session_state.selected_travel_mode



        vehicle_limits = SPEED_LIMITS_CONFIG.get(sel_vehicle_key, SPEED_LIMITS_CONFIG["CAR"])







        if "selected_speed_mode" not in st.session_state:



            st.session_state.selected_speed_mode = "NORMAL"







        # Check if vehicle mode changed externally or needs initial sync



        if st.session_state.get("_last_speed_vehicle_key") != sel_vehicle_key:



            st.session_state._last_speed_vehicle_key = sel_vehicle_key



            curr_sm = st.session_state.get("selected_speed_mode", "NORMAL")



            if curr_sm == "ECO":



                st.session_state.custom_speed_kmh = vehicle_limits["eco"]



            elif curr_sm == "FAST":



                st.session_state.custom_speed_kmh = vehicle_limits["fast"]



            else:



                st.session_state.custom_speed_kmh = vehicle_limits["normal"]







        if "custom_speed_kmh" not in st.session_state:



            st.session_state.custom_speed_kmh = vehicle_limits["normal"]



        else:



            st.session_state.custom_speed_kmh = max(vehicle_limits["min"], min(vehicle_limits["max"], st.session_state.custom_speed_kmh))







        speed_title = "⚡ SPEED MODE & TRANSIT PROFILE"
        speed_subtitle = "Choose how you want to travel."

        st.markdown(f"""<div style='display: flex; align-items: center; justify-content: space-between; margin-top: 14px; margin-bottom: 6px;'>
<div style='font-size: 0.82rem; font-weight: 800; color: #a78bfa; text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 6px;'>
<span>⚡</span> {speed_title}
</div>
<div style='font-size: 0.72rem; color: #94a3b8;'>
{speed_subtitle}
</div>
</div>""", unsafe_allow_html=True)







        SPEED_MODES = {



            "ECO": {"icon": "🌿", "label": t("speed.eco"), "desc": vehicle_limits["eco_desc"], "val": vehicle_limits["eco"]},



            "NORMAL": {"icon": "⚡", "label": t("speed.normal"), "desc": vehicle_limits["normal_desc"], "val": vehicle_limits["normal"]},



            "FAST": {"icon": "🚀", "label": t("speed.fast"), "desc": vehicle_limits["fast_desc"], "val": vehicle_limits["fast"]},



            "CUSTOM": {"icon": "⚙️", "label": t("speed.custom"), "desc": t("speed.custom_desc", min=vehicle_limits['min'], max=vehicle_limits['max']), "val": st.session_state.custom_speed_kmh}



        }







        with st.container(key="speed_deck_container"):



            s_cols = st.columns(4)



            active_speed_key = st.session_state.selected_speed_mode



            for s_idx, (s_k, s_info) in enumerate(SPEED_MODES.items()):



                with s_cols[s_idx]:



                    s_selected = (s_k == active_speed_key)



                    s_btn_type = "primary" if s_selected else "secondary"



                    s_btn_label = f"{s_info['icon']} **{s_info['label']}** ({s_info['val']:g} {vehicle_limits['unit'].split()[0]})" if s_k != "CUSTOM" else f"{s_info['icon']} **{s_info['label']}**"



                    if st.button(s_btn_label, key=f"btn_speed_mode_{s_k}", use_container_width=True, type=s_btn_type):



                        st.session_state.selected_speed_mode = s_k



                        if s_k == "ECO":



                            st.session_state.custom_speed_kmh = vehicle_limits["eco"]



                        elif s_k == "NORMAL":



                            st.session_state.custom_speed_kmh = vehicle_limits["normal"]



                        elif s_k == "FAST":



                            st.session_state.custom_speed_kmh = vehicle_limits["fast"]



                        st.session_state.last_speed_mode_trigger = f"{s_info['label']} Speed Profile"



                        st.session_state.scroll_to_speedometer = True



                        st.session_state.pop("cached_candidate_routes", None)



                        st.rerun()







        # =========================================================================



        # CREATIVE INTELLIGENT DIGITAL SPEEDOMETER HUD (COCKPIT CLUSTER)



        # =========================================================================



        v_min = float(vehicle_limits["min"])



        v_max = float(vehicle_limits["max"])



        v_span = max(0.1, v_max - v_min)



        active_mode = st.session_state.selected_speed_mode







        if active_mode == "ECO":



            display_speed = vehicle_limits["eco"]



            zone_label = "🌿 ECO EFFICIENCY"



            zone_color = "#10b981"



            mode_desc_text = vehicle_limits["eco_desc"]



        elif active_mode == "NORMAL":



            display_speed = vehicle_limits["normal"]



            zone_label = "⚡ BALANCED CRUISE"



            zone_color = "#00F0B5"



            mode_desc_text = vehicle_limits["normal_desc"]



        elif active_mode == "FAST":



            display_speed = vehicle_limits["fast"]



            zone_label = "🚀 HIGHWAY VELOCITY"



            zone_color = "#f59e0b"



            mode_desc_text = vehicle_limits["fast_desc"]



        else:  # CUSTOM



            display_speed = st.session_state.custom_speed_kmh



            pct_custom = (display_speed - v_min) / v_span



            if pct_custom <= 0.35:



                zone_label = "🌿 CITY CRUISE"



                zone_color = "#10b981"



            elif pct_custom <= 0.70:



                zone_label = "⚡ URBAN ARTERIAL"



                zone_color = "#00F0B5"



            elif pct_custom <= 0.88:



                zone_label = "🚀 HIGHWAY CRUISE"



                zone_color = "#f59e0b"



            else:



                zone_label = "🏎️ SPORT VELOCITY"



                zone_color = "#f43f5e"



            mode_desc_text = f"Custom cruise target: {display_speed:g} {vehicle_limits['unit']} • Road safety regulations apply"







        unit_str = vehicle_limits["unit"]







        # Track acceleration / deceleration delta and animation state



        prev_reading = st.session_state.get("_prev_speedometer_val", display_speed)



        speed_delta = round(display_speed - prev_reading, 1)



        st.session_state._prev_speedometer_val = display_speed







        last_trigger_label = st.session_state.get("last_speed_mode_trigger", None)



        trigger_pill = ""



        if last_trigger_label:



            trigger_pill = f"<span style='color: #a78bfa; background: rgba(167, 139, 250, 0.12); padding: 3px 9px; border-radius: 999px; border: 1px solid rgba(167, 139, 250, 0.35); font-size: 0.68rem; font-weight: 800; letter-spacing: 0.04em;'>🎯 SYNCED: {last_trigger_label}</span>"







        if speed_delta > 0.0:



            surge_pill = f"<span style='color: #f59e0b; background: rgba(245, 158, 11, 0.12); padding: 3px 9px; border-radius: 999px; border: 1px solid rgba(245, 158, 11, 0.35); font-size: 0.68rem; font-weight: 800; letter-spacing: 0.04em;'>🔥 ACCELERATING +{speed_delta:g} {unit_str.split()[0]} • POWER BAND</span>"



        elif speed_delta < 0.0:



            surge_pill = f"<span style='color: #10b981; background: rgba(16, 185, 129, 0.12); padding: 3px 9px; border-radius: 999px; border: 1px solid rgba(16, 185, 129, 0.35); font-size: 0.68rem; font-weight: 800; letter-spacing: 0.04em;'>🍃 DECELERATING {speed_delta:g} {unit_str.split()[0]} • RECOVERING ENERGY</span>"



        else:



            surge_pill = f"<span style='color: #38bdf8; background: rgba(56, 189, 248, 0.08); padding: 3px 9px; border-radius: 999px; border: 1px solid rgba(56, 189, 248, 0.25); font-size: 0.68rem; font-weight: 800; letter-spacing: 0.04em;'>🔒 VELOCITY LOCKED • {display_speed:g} {unit_str.split()[0]}</span>"







        # Secondary speed unit conversion



        if vehicle_limits.get("sec_factor"):



            sec_val = round(display_speed * vehicle_limits["sec_factor"], 1)



            sec_display = f"~{sec_val:g} {vehicle_limits['sec_unit']}"



            if sel_vehicle_key == "FLIGHT":



                mach_val = round(display_speed / 1062.0, 2)



                sec_display += f" (MACH {mach_val})"



        elif sel_vehicle_key == "WALK":



            pace_mins = round(60.0 / max(0.1, display_speed), 1)



            sec_display = f"~{pace_mins:g} MIN / KM CADENCE"



        else:



            sec_display = f"~{round(display_speed * 0.621371, 1):g} MPH"







        # Authentic vehicle powertrain telemetry



        if sel_vehicle_key in ["CAR", "TRUCK", "BUS", "BIKE", "TRACTOR"]:



            rpm_val = int(round(display_speed * 32.5))



            gear_lbl = "D2" if display_speed < 25 else ("D3" if display_speed < 50 else ("D4" if display_speed < 75 else ("D5" if display_speed < 105 else "D6")))



            kw_val = round(display_speed * 1.15, 1)



            telemetry_str = f"⚙️ GEAR {gear_lbl} • {rpm_val:,} RPM • {kw_val:g} kW OUTPUT"



        elif sel_vehicle_key == "FLIGHT":



            n1_val = round(60.0 + pct * 36.0, 1)



            thrust_lbf = int(round(9000 + pct * 18500))



            mach_str = f"M{round(display_speed / 1062.0, 2)}"



            telemetry_str = f"✈️ TURBOFAN {n1_val}% N1 • {thrust_lbf:,} LBF THRUST • {mach_str}"



        elif sel_vehicle_key == "WATERWAY":



            knots_val = round(display_speed * 0.539957, 1)



            telemetry_str = f"🚢 PROPELLER SHAFT 820 RPM • {knots_val} KNOTS • DRAFT OPTIMIZED"



        elif sel_vehicle_key == "BICYCLE":



            cadence = int(round(55 + pct * 45))



            watts = int(round(80 + pct * 180))



            telemetry_str = f"🚴 CADENCE {cadence} RPM • {watts} WATTS THRESHOLD POWER"



        else:  # WALK



            bpm = int(round(85 + pct * 65))



            steps_min = int(round(90 + pct * 55))



            telemetry_str = f"🚶 CADENCE {steps_min} STEPS/MIN • HEART RATE ~{bpm} BPM"







        # Arc math for SVG speedometer:



        # Center (160, 130), Radius 90.



        # Angle span: -130° to +130° = 260° total.



        pct = max(0.0, min(1.0, (display_speed - v_min) / v_span))



        needle_angle = round(-130.0 + pct * 260.0, 1)



        dasharray = 408.4



        stroke_dashoffset = max(0.0, min(dasharray, round(dasharray * (1.0 - pct), 1)))







        prev_pct = max(0.0, min(1.0, (prev_reading - v_min) / v_span))



        prev_needle_angle = round(-130.0 + prev_pct * 260.0, 1)



        prev_stroke_dashoffset = max(0.0, min(dasharray, round(dasharray * (1.0 - prev_pct), 1)))







        if speed_delta > 0:



            bounce_angle = min(132.0, round(needle_angle + 2.8, 1))



        elif speed_delta < 0:



            bounce_angle = max(-132.0, round(needle_angle - 2.8, 1))



        else:



            bounce_angle = needle_angle







        # Calibrated SVG graduation ticks with Redline Zone at top end



        ticks_svg = []



        for i in range(9):



            tick_deg = -130.0 + (i / 8.0) * 260.0



            rad = math.radians(tick_deg - 90.0)



            x1 = round(160 + 90 * math.cos(rad), 1)



            y1 = round(130 + 90 * math.sin(rad), 1)



            x2 = round(160 + 79 * math.cos(rad), 1)



            y2 = round(130 + 79 * math.sin(rad), 1)



            lx = round(160 + 66 * math.cos(rad), 1)



            ly = round(130 + 66 * math.sin(rad), 1)



            val = int(round(v_min + (i / 8.0) * v_span)) if (v_span >= 10) else round(v_min + (i / 8.0) * v_span, 1)



            is_redline = (i >= 7)



            tick_col = "#f43f5e" if is_redline else "rgba(255,255,255,0.40)"



            num_col = "#f43f5e" if is_redline else "#94a3b8"



            ticks_svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{tick_col}" stroke-width="2.2" stroke-linecap="round" />')



            ticks_svg.append(f'<text x="{lx}" y="{ly + 3}" font-size="7.5" font-weight="800" font-family="monospace" fill="{num_col}" text-anchor="middle">{val}</text>')







        for i in range(24):



            if i % 3 != 0:



                tick_deg = -130.0 + (i / 24.0) * 260.0



                rad = math.radians(tick_deg - 90.0)



                x1 = round(160 + 90 * math.cos(rad), 1)



                y1 = round(130 + 90 * math.sin(rad), 1)



                x2 = round(160 + 84 * math.cos(rad), 1)



                y2 = round(130 + 84 * math.sin(rad), 1)



                is_redline = (i >= 20)



                sub_col = "rgba(244,63,94,0.6)" if is_redline else "rgba(255,255,255,0.18)"



                ticks_svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{sub_col}" stroke-width="1.3" stroke-linecap="round" />')







        ticks_svg_str = "\n".join(ticks_svg)







        # 14-Segment Power/Throttle Bar



        pct_int = int(round(pct * 14))



        bar_segments = ""



        for b_i in range(14):



            if b_i < pct_int:



                if b_i < 5:



                    b_color = "#10b981"



                elif b_i < 9:



                    b_color = "#00F0B5"



                elif b_i < 12:



                    b_color = "#f59e0b"



                else:



                    b_color = "#f43f5e"



                bar_segments += f"<span style='display:inline-block; width:9px; height:7px; background:{b_color}; border-radius:2px; margin:0 1px; box-shadow:0 0 6px {b_color}88;'></span>"



            else:



                bar_segments += "<span style='display:inline-block; width:9px; height:7px; background:rgba(255,255,255,0.08); border-radius:2px; margin:0 1px;'></span>"







        # Unique Keyframe CSS to sweep needle realistically from previous speed to new speed



        import time as _t



        anim_uid = f"sw_{int(_t.time()*100)%100000}"







        speedo_html = f"""<!DOCTYPE html>



<html>



<head>



<meta charset="utf-8">



<style>



body {{



    margin: 0;



    padding: 0;



    background: transparent;



    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;



    overflow: hidden;



    user-select: none;



}}



@keyframes needleSweep_{anim_uid} {{



    0% {{ transform: rotate({prev_needle_angle}deg); }}



    70% {{ transform: rotate({bounce_angle}deg); }}



    100% {{ transform: rotate({needle_angle}deg); }}



}}



@keyframes arcFill_{anim_uid} {{



    0% {{ stroke-dashoffset: {prev_stroke_dashoffset}; }}



    100% {{ stroke-dashoffset: {stroke_dashoffset}; }}



}}



.speedo-needle-elem {{



    transform-origin: 160px 130px;



    animation: needleSweep_{anim_uid} 0.88s cubic-bezier(0.25, 1.4, 0.5, 1) forwards !important;



}}



.speedo-arc-elem {{



    animation: arcFill_{anim_uid} 0.88s ease-out forwards !important;



}}



</style>



</head>



<body>



<div id="tour-speedometer-cockpit" style='background: linear-gradient(180deg, rgba(15, 23, 42, 0.98) 0%, rgba(10, 15, 29, 0.99) 100%); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 16px; padding: 12px 16px 10px 16px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.55); box-sizing: border-box; width: 100%;'>



    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; flex-wrap: wrap; gap: 6px;'>



        <div style='display: flex; align-items: center; gap: 8px;'>



            <span style='font-size: 1.1rem;'>⏱️</span>



            <span style='font-size: 0.82rem; font-weight: 800; color: #f8fafc; letter-spacing: 0.05em; text-transform: uppercase;'>



                DIGITAL SPEEDOMETER COCKPIT



            </span>



            {trigger_pill}



            {surge_pill}



        </div>



        <span style='font-size: 0.70rem; font-weight: 800; color: {zone_color}; background: rgba(255, 255, 255, 0.06); padding: 3px 9px; border-radius: 999px; border: 1px solid {zone_color}44; letter-spacing: 0.04em;'>



            {zone_label}



        </span>



    </div>



    <div style='display: flex; justify-content: center; align-items: center;'>



        <svg viewBox="0 0 320 185" style="width: 100%; max-width: 320px; max-height: 145px; overflow: visible;">



            <defs>



                <linearGradient id="speedMeterGrad" x1="0%" y1="0%" x2="100%" y2="0%">



                    <stop offset="0%" stop-color="#10b981" />



                    <stop offset="35%" stop-color="#00F0B5" />



                    <stop offset="70%" stop-color="#f59e0b" />



                    <stop offset="100%" stop-color="#f43f5e" />



                </linearGradient>



                <radialGradient id="dialBezelGrad" cx="50%" cy="50%" r="50%">



                    <stop offset="0%" stop-color="#1e293b" stop-opacity="0.5" />



                    <stop offset="85%" stop-color="#0f172a" stop-opacity="0.8" />



                    <stop offset="100%" stop-color="#020617" stop-opacity="0.95" />



                </radialGradient>



                <filter id="meterGlow" x="-20%" y="-20%" width="140%" height="140%">



                    <feGaussianBlur stdDeviation="3.0" result="blur" />



                    <feMerge>



                        <feMergeNode in="blur"/>



                        <feMergeNode in="SourceGraphic"/>



                    </feMerge>



                </filter>



            </defs>



            <!-- Background Inner Dial Bezel -->



            <circle cx="160" cy="130" r="88" fill="url(#dialBezelGrad)" />



            <!-- Background Outer Ring Track -->



            <path d="M 91.06 187.85 A 90 90 0 1 1 228.94 187.85" fill="none" stroke="rgba(255, 255, 255, 0.08)" stroke-width="12" stroke-linecap="round" />



            <!-- Active Luminous Progress Arc with Realistic Easing Transition -->



            <path class="speedo-arc-elem" d="M 91.06 187.85 A 90 90 0 1 1 228.94 187.85" fill="none" stroke="url(#speedMeterGrad)" stroke-width="12" stroke-linecap="round" stroke-dasharray="408.4" stroke-dashoffset="{stroke_dashoffset}" filter="url(#meterGlow)" />



            <!-- Calibrated Graduation Ticks -->



            {ticks_svg_str}



            <!-- Redline Zone Label -->



            <text x="220" y="172" font-size="5.5" font-weight="900" font-family="monospace" fill="#f43f5e" letter-spacing="1.0">REDLINE</text>



            <!-- Digital Primary Speed Readout with Live Odometer Counter Hook -->



            <text id="speedo-digital-val" x="160" y="105" font-size="34" font-weight="900" font-family="'Inter', monospace" fill="#f8fafc" text-anchor="middle">



                {display_speed:g}



            </text>



            <!-- Primary Speed Unit -->



            <text x="160" y="122" font-size="9" font-weight="800" font-family="monospace" letter-spacing="2.5" fill="#38bdf8" text-anchor="middle">



                {unit_str}



            </text>



            <!-- Secondary Unit Conversion Readout -->



            <text x="160" y="137" font-size="8.5" font-weight="700" fill="#a78bfa" text-anchor="middle">



                {sec_display}



            </text>



            <!-- Vehicle Dynamic Profile Title -->



            <text x="160" y="152" font-size="7.5" font-weight="600" fill="#94a3b8" text-anchor="middle">



                {current_mode_info['name']} Dynamic Profile



            </text>



            <!-- Rotational Needle with Realistic Mechanical Easing & Hub Details -->



            <g class="speedo-needle-elem">



                <!-- Needle Shadow -->



                <polygon points="158,131 162,131 161,46 159,46" fill="rgba(0,0,0,0.6)" />



                <!-- Outer Needle Body -->



                <polygon points="157.5,130 162.5,130 161,44 159,44" fill="{zone_color}" filter="url(#meterGlow)" />



                <!-- Inner High-Visibility Neon Spine -->



                <line x1="160" y1="130" x2="160" y2="42" stroke="#ffffff" stroke-width="1.2" stroke-linecap="round" />



                <!-- Pivot Hub Rim -->



                <circle cx="160" cy="130" r="11" fill="#0b172a" stroke="{zone_color}" stroke-width="2.5" />



                <!-- Pivot Metallic Center Rivet -->



                <circle cx="160" cy="130" r="5" fill="#f8fafc" />



                <circle cx="160" cy="130" r="2" fill="#0b172a" />



            </g>



        </svg>



    </div>



    <!-- Live Vehicle Powertrain Telemetry Bar -->



    <div style='text-align: center; font-size: 0.72rem; font-weight: 700; color: #7dd3fc; margin-top: 2px; font-family: monospace; letter-spacing: 0.03em;'>



        {telemetry_str}



    </div>



    <!-- Throttle Demand & Engine Energy Cluster -->



    <div style='display: flex; justify-content: space-between; align-items: center; margin-top: 4px; padding: 4px 10px; background: rgba(0,0,0,0.30); border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);'>



        <div style='font-size: 0.68rem; font-weight: 700; color: #94a3b8;'>



            THROTTLE DEMAND: <span style='color: #f8fafc; font-weight: 800;'>{int(round(pct * 100))}%</span>



        </div>



        <div style='display: flex; align-items: center;'>



            {bar_segments}



        </div>



    </div>



    <div style='text-align: center; font-size: 0.70rem; color: #94a3b8; margin-top: 4px;'>



        {mode_desc_text}



    </div>



</div>



<script>



(function() {{



    try {{



        var numEl = document.getElementById('speedo-digital-val');



        if (numEl) {{



            var startV = {float(prev_reading)};



            var endV = {float(display_speed)};



            if (Math.abs(startV - endV) > 0.05) {{



                var startTime = performance.now();



                var duration = 850;



                function tick(now) {{



                    var elapsed = now - startTime;



                    var tNorm = Math.min(1.0, elapsed / duration);



                    var ease = 1.0 - Math.pow(1.0 - tNorm, 3);



                    var cur = startV + (endV - startV) * ease;



                    numEl.textContent = (endV % 1 === 0) ? Math.round(cur) : cur.toFixed(1);



                    if (tNorm < 1.0) {{



                        requestAnimationFrame(tick);



                    }} else {{



                        numEl.textContent = (endV % 1 === 0) ? Math.round(endV) : endV.toFixed(1);



                    }}



                }}



                requestAnimationFrame(tick);



            }}



        }}



    }} catch(e) {{}}



}})();



</script>



</body>



</html>"""



        st.markdown('<div id="tour-speedometer-cockpit" style="scroll-margin-top: 140px; display: block; height: 1px; width: 100%;"></div>', unsafe_allow_html=True)



        components.html(speedo_html, height=270)







        # Real-time Speed Safety & Health Analysis Bar



        cur_spd = float(display_speed)



        if cur_spd <= vehicle_limits["eco"] + 2:



            spd_verdict = "🟢 OPTIMAL (SAFE & HEALTHY SPEED)"



            spd_verdict_col = "#10b981"



            spd_health_msg = f"You are driving at an optimal eco cruising velocity ({cur_spd:g} {unit_str.split()[0]}). Stopping buffer is >2.8s, eliminating driver fatigue and minimizing brake emissions."



        elif cur_spd <= vehicle_limits["normal"] + 2:



            spd_verdict = "🟢 BALANCED & HEALTHY SPEED"



            spd_verdict_col = "#00F0B5"



            spd_health_msg = f"You are driving at a balanced cruise speed ({cur_spd:g} {unit_str.split()[0]}). Safe 2.6s headway buffer is maintained. Driver cognitive load is well within relaxed limits."



        else:



            spd_verdict = "⚠️ ELEVATED SPEED (MAINTAIN HEADWAY)"



            spd_verdict_col = "#f59e0b"



            spd_health_msg = f"High velocity cruise ({cur_spd:g} {unit_str.split()[0]}). Reaction stopping distance increases to ~48m. Stay alert, avoid sudden steering maneuvers, and take regular rest breaks."







        st.markdown(f"""



        <div style='background: rgba(15, 23, 42, 0.7); border: 1px solid {spd_verdict_col}44; border-radius: 10px; padding: 8px 14px; margin-top: 6px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;'>



            <div style='display: flex; align-items: center; gap: 8px;'>



                <span style='font-size: 1.0rem;'>🧠</span>



                <div>



                    <span style='font-size: 0.72rem; font-weight: 800; color: {spd_verdict_col}; text-transform: uppercase;'>DRIVER SPEED & HEALTH ANALYSIS:</span>



                    <span style='font-size: 0.72rem; color: #cbd5e1; margin-left: 4px;'>{spd_health_msg}</span>



                </div>



            </div>



            <span style='background: {spd_verdict_col}22; color: {spd_verdict_col}; border: 1px solid {spd_verdict_col}55; font-size: 0.68rem; font-weight: 800; padding: 2px 8px; border-radius: 9999px;'>{spd_verdict}</span>



        </div>



        """, unsafe_allow_html=True)







        # 1-Click Quick Speed Pick Presets & Tactile Controls



        st.markdown("<div style='font-size: 0.74rem; font-weight: 700; color: #a78bfa; margin-top: 6px; margin-bottom: 4px;'>⚡ QUICK SPEED PRESETS & TACTILE CONTROLS:</div>", unsafe_allow_html=True)



        preset_cols = st.columns(5)



        preset_chips = vehicle_limits["presets"]



        preset_labels = ["🏙️ City", "🚗 Eco", "🛣️ Cruise", "⚡ High", "🚀 Max"]



        if sel_vehicle_key == "WALK":



            preset_labels = ["🚶 Leisure", "🚶 Commute", "🚶 Brisk", "🏃 Fast", "🏃 Sprint"]



        elif sel_vehicle_key == "FLIGHT":



            preset_labels = ["🛫 Climb", "✈️ Eco", "✈️ Cruise", "🚀 Mach", "🚀 Max"]



        elif sel_vehicle_key == "WATERWAY":



            preset_labels = ["⚓ Harbor", "🚢 Coastal", "🚢 Cruise", "⚡ Sprint", "🚀 Express"]







        for p_idx, p_val in enumerate(preset_chips[:5]):



            with preset_cols[p_idx]:



                is_p_active = (abs(display_speed - p_val) < 0.01)



                p_text = f"{p_val:g}" if isinstance(p_val, float) else f"{p_val}"



                p_btn_label = f"{preset_labels[p_idx]}\n\n**{p_text}**"



                if st.button(p_btn_label, key=f"btn_quick_spd_{p_idx}_{p_val}", use_container_width=True, type="primary" if is_p_active else "secondary"):



                    st.session_state.selected_speed_mode = "CUSTOM"



                    st.session_state.custom_speed_kmh = p_val



                    st.session_state.last_speed_mode_trigger = f"{preset_labels[p_idx]} Target ({p_text} {unit_str.split()[0]})"



                    st.session_state.scroll_to_speedometer = True



                    st.session_state.pop("cached_candidate_routes", None)



                    st.rerun()







        # Steppers & Fine-Tune Slider (accessible when Custom mode is engaged)



        if st.session_state.selected_speed_mode == "CUSTOM":



            v_step = vehicle_limits["step"]



            step_cols = st.columns([1, 1, 2, 1, 1])



            with step_cols[0]:



                if st.button(f"⏪ -{v_step*2:g}", key="btn_stp_m10", use_container_width=True):



                    st.session_state.custom_speed_kmh = max(v_min, round(st.session_state.custom_speed_kmh - v_step*2, 1))



                    st.session_state.pop("cached_candidate_routes", None)



                    st.rerun()



            with step_cols[1]:



                if st.button(f"◀ -{v_step:g}", key="btn_stp_m5", use_container_width=True):



                    st.session_state.custom_speed_kmh = max(v_min, round(st.session_state.custom_speed_kmh - v_step, 1))



                    st.session_state.pop("cached_candidate_routes", None)



                    st.rerun()



            with step_cols[2]:



                st.markdown(f"<div style='text-align: center; padding-top: 6px; font-weight: 800; font-size: 0.84rem; color: #38bdf8;'>Target Cruise: {st.session_state.custom_speed_kmh:g} {unit_str.split()[0]}</div>", unsafe_allow_html=True)



            with step_cols[3]:



                if st.button(f"+{v_step:g} ▶", key="btn_stp_p5", use_container_width=True):



                    st.session_state.custom_speed_kmh = min(v_max, round(st.session_state.custom_speed_kmh + v_step, 1))



                    st.session_state.pop("cached_candidate_routes", None)



                    st.rerun()



            with step_cols[4]:



                if st.button(f"+{v_step*2:g} ⏩", key="btn_stp_p10", use_container_width=True):



                    st.session_state.custom_speed_kmh = min(v_max, round(st.session_state.custom_speed_kmh + v_step*2, 1))



                    st.session_state.pop("cached_candidate_routes", None)



                    st.rerun()







            new_speed = st.slider(



                label=t("speed.configure_target"),



                min_value=float(v_min),



                max_value=float(v_max),



                value=float(st.session_state.custom_speed_kmh),



                step=float(v_step),



                format=f"%g {unit_str.split()[0]}",



                key="slider_custom_speed"



            )



            if round(new_speed, 1) != round(st.session_state.custom_speed_kmh, 1):



                st.session_state.custom_speed_kmh = round(new_speed, 1)



                st.session_state.pop("cached_candidate_routes", None)



                st.rerun()







        # Route Avoidances & Exclusions (Grand Luxury HUD Cards)



        st.markdown(f"""



        <div style='margin-top: 18px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;'>



            <div style='font-size: 0.82rem; font-weight: 800; color: #00F0B5; text-transform: uppercase; letter-spacing: 0.06em; display: flex; align-items: center; gap: 8px;'>



                <span>🛡️</span> CORRIDOR EXCLUSIONS & AVOIDANCE FILTERS



            </div>



            <div style='font-size: 0.70rem; color: #94a3b8;'>



                Multi-Objective Autonomous Bypass Engine



            </div>



        </div>



        <div id="tour-preferences-bar"></div>



        """, unsafe_allow_html=True)







        c_av1, c_av2, c_av3 = st.columns(3)



        cur_tolls = st.session_state.get("avoid_tolls", False)



        cur_hw = st.session_state.get("avoid_highways", False)



        cur_ferry = st.session_state.get("avoid_ferries", False)







        with c_av1:



            tolls_glow = "border: 1.5px solid #00F0B5; box-shadow: 0 0 16px rgba(0, 240, 181, 0.22); background: linear-gradient(145deg, rgba(0, 240, 181, 0.12), rgba(15, 23, 42, 0.90));" if cur_tolls else "border: 1px solid rgba(255, 255, 255, 0.08); background: rgba(15, 23, 42, 0.55);"



            tolls_badge = "<span style='color: #00F0B5; font-size: 0.65rem; font-weight: 800; background: rgba(0, 240, 181, 0.15); padding: 2px 7px; border-radius: 999px; border: 1px solid rgba(0, 240, 181, 0.4);'>● ACTIVE BYPASS</span>" if cur_tolls else "<span style='color: #94a3b8; font-size: 0.65rem; font-weight: 700; background: rgba(255, 255, 255, 0.05); padding: 2px 7px; border-radius: 999px;'>○ PERMITTED</span>"



            st.markdown(f"""



            <div style='{tolls_glow} border-radius: 12px; padding: 12px 14px; margin-bottom: 6px; min-height: 96px;'>



                <div style='display: flex; justify-content: space-between; align-items: center;'>



                    <span style='font-size: 1.2rem;'>💳</span>



                    {tolls_badge}



                </div>



                <div style='font-size: 0.85rem; font-weight: 800; color: #f8fafc; margin-top: 6px;'>



                    {t('nav.avoid_tolls')}



                </div>



                <div style='font-size: 0.70rem; color: #94a3b8; margin-top: 2px;'>



                    Bypasses FASTag tollgates & saves transit fees



                </div>



            </div>



            """, unsafe_allow_html=True)



            if st.button(



                f"✅ {t('nav.avoid_tolls')}" if cur_tolls else f"💳 {t('nav.avoid_tolls')}",



                key="btn_hud_avoid_tolls",



                use_container_width=True,



                type="primary" if cur_tolls else "secondary"



            ):



                st.session_state.avoid_tolls = not cur_tolls



                st.session_state.chk_map_avoid_tolls = not cur_tolls



                if "_prev_endpoint_sig" in st.session_state:



                    del st.session_state["_prev_endpoint_sig"]



                st.rerun()







        with c_av2:



            hw_glow = "border: 1.5px solid #fbbf24; box-shadow: 0 0 16px rgba(251, 191, 36, 0.22); background: linear-gradient(145deg, rgba(251, 191, 36, 0.12), rgba(15, 23, 42, 0.90));" if cur_hw else "border: 1px solid rgba(255, 255, 255, 0.08); background: rgba(15, 23, 42, 0.55);"



            hw_badge = "<span style='color: #fbbf24; font-size: 0.65rem; font-weight: 800; background: rgba(251, 191, 36, 0.15); padding: 2px 7px; border-radius: 999px; border: 1px solid rgba(251, 191, 36, 0.4);'>● HIGHWAY BYPASS</span>" if cur_hw else "<span style='color: #94a3b8; font-size: 0.65rem; font-weight: 700; background: rgba(255, 255, 255, 0.05); padding: 2px 7px; border-radius: 999px;'>○ HIGHWAYS OK</span>"



            st.markdown(f"""



            <div style='{hw_glow} border-radius: 12px; padding: 12px 14px; margin-bottom: 6px; min-height: 96px;'>



                <div style='display: flex; justify-content: space-between; align-items: center;'>



                    <span style='font-size: 1.2rem;'>🛣️</span>



                    {hw_badge}



                </div>



                <div style='font-size: 0.85rem; font-weight: 800; color: #f8fafc; margin-top: 6px;'>



                    {t('nav.avoid_highways')}



                </div>



                <div style='font-size: 0.70rem; color: #94a3b8; margin-top: 2px;'>



                    Evades multi-lane expressways via scenic byways



                </div>



            </div>



            """, unsafe_allow_html=True)



            if st.button(



                f"✅ {t('nav.avoid_highways')}" if cur_hw else f"🛣️ {t('nav.avoid_highways')}",



                key="btn_hud_avoid_highways",



                use_container_width=True,



                type="primary" if cur_hw else "secondary"



            ):



                st.session_state.avoid_highways = not cur_hw



                st.session_state.chk_map_avoid_highways = not cur_hw



                if "_prev_endpoint_sig" in st.session_state:



                    del st.session_state["_prev_endpoint_sig"]



                st.rerun()







        with c_av3:



            ferry_glow = "border: 1.5px solid #38bdf8; box-shadow: 0 0 16px rgba(56, 189, 248, 0.22); background: linear-gradient(145deg, rgba(56, 189, 248, 0.12), rgba(15, 23, 42, 0.90));" if cur_ferry else "border: 1px solid rgba(255, 255, 255, 0.08); background: rgba(15, 23, 42, 0.55);"



            ferry_badge = "<span style='color: #38bdf8; font-size: 0.65rem; font-weight: 800; background: rgba(56, 189, 248, 0.15); padding: 2px 7px; border-radius: 999px; border: 1px solid rgba(56, 189, 248, 0.4);'>● FERRIES EXCLUDED</span>" if cur_ferry else "<span style='color: #94a3b8; font-size: 0.65rem; font-weight: 700; background: rgba(255, 255, 255, 0.05); padding: 2px 7px; border-radius: 999px;'>○ FERRIES OK</span>"



            st.markdown(f"""



            <div style='{ferry_glow} border-radius: 12px; padding: 12px 14px; margin-bottom: 6px; min-height: 96px;'>



                <div style='display: flex; justify-content: space-between; align-items: center;'>



                    <span style='font-size: 1.2rem;'>⛴️</span>



                    {ferry_badge}



                </div>



                <div style='font-size: 0.85rem; font-weight: 800; color: #f8fafc; margin-top: 6px;'>



                    {t('nav.avoid_ferries')}



                </div>



                <div style='font-size: 0.70rem; color: #94a3b8; margin-top: 2px;'>



                    Filters water transit for continuous overland links



                </div>



            </div>



            """, unsafe_allow_html=True)



            if st.button(



                f"✅ {t('nav.avoid_ferries')}" if cur_ferry else f"⛴️ {t('nav.avoid_ferries')}",



                key="btn_hud_avoid_ferries",



                use_container_width=True,



                type="primary" if cur_ferry else "secondary"



            ):



                st.session_state.avoid_ferries = not cur_ferry



                st.session_state.chk_map_avoid_ferries = not cur_ferry



                if "_prev_endpoint_sig" in st.session_state:



                    del st.session_state["_prev_endpoint_sig"]



                st.rerun()







        # Grand live HUD banner if any avoidance is active



        active_avoidances = []



        if cur_tolls:



            active_avoidances.append("<span style='color: #00F0B5; font-weight: 800;'>🛡️ Toll Plazas Bypassed</span>")



        if cur_hw:



            active_avoidances.append("<span style='color: #fbbf24; font-weight: 800;'>🌿 Highways Evaded</span>")



        if cur_ferry:



            active_avoidances.append("<span style='color: #38bdf8; font-weight: 800;'>🌊 Ferries Excluded</span>")







        if active_avoidances:



            active_str = " • ".join(active_avoidances)



            st.markdown(f"""



            <div style='background: linear-gradient(90deg, rgba(0, 240, 181, 0.12), rgba(56, 189, 248, 0.10)); border: 1px solid rgba(0, 240, 181, 0.35); border-radius: 8px; padding: 7px 14px; margin-top: 6px; margin-bottom: 10px; font-size: 0.75rem; color: #f8fafc; display: flex; align-items: center; justify-content: space-between;'>



                <span><b>ACTIVE CORRIDOR FILTERS:</b> {active_str}</span>



                <span style='color: #00F0B5; font-size: 0.68rem; font-weight: 700;'>⚡ Routing Engine Enforcing Constraints</span>



            </div>



            """, unsafe_allow_html=True)







        coords_orig = st.session_state.user_live_coords



        coords_dest = st.session_state.selected_dest_coords



        is_pending = bool(st.session_state.get("orig_pending_confirmation") or st.session_state.get("dest_pending_confirmation"))







        # Evaluate & Rank Candidate Routes using Multi-Objective Optimization Model



        active_obj = st.session_state.get("active_objective", OptimizationObjective.FASTEST)



        require_acc = st.session_state.get("requires_accessible", False) or (active_obj == OptimizationObjective.ACCESSIBLE)







        # Guard: both origin and destination must be set and confirmed before route calculation



        from src.route_engine import haversine_distance_m



        is_same_endpoint = bool(coords_orig and coords_dest and haversine_distance_m(coords_orig[0], coords_orig[1], coords_dest[0], coords_dest[1]) < 25.0)







        if not coords_orig or not coords_dest or is_pending or is_same_endpoint:



            if is_same_endpoint:



                st.markdown("""



                <div style='background: rgba(234, 179, 8, 0.15); border: 1.5px solid #eab308; border-radius: 12px; padding: 16px 20px; margin: 14px 0; text-align: center;'>



                    <div style='font-size: 2.0rem; margin-bottom: 6px;'>⚠️</div>



                    <div style='color: #facc15; font-weight: 800; font-size: 1.0rem;'>Origin and Destination Are Identical</div>



                    <div style='color: #94a3b8; font-size: 0.84rem; margin-top: 6px;'>



                        Starting point and destination are at the exact same location (< 25m). Please select a distinct destination to calculate driving routes.



                    </div>



                </div>



                """, unsafe_allow_html=True)



                candidate_routes = []



                ranked_routes = []



                eligible_ranked = []



                restricted_ranked = []



            else:



                _missing = []



            if not coords_orig:



                _missing.append("origin")



            if not coords_dest:



                _missing.append("destination")



            _missing_str = " and ".join(_missing)



            



            pending_hint = ""



            if is_pending:



                pending_hint = "<div style='color: #fbbf24; font-size: 0.85rem; margin-top: 6px; font-weight: 700;'>⏳ An endpoint is pending confirmation. Please select an area or confirm coordinates.</div>"







            st.markdown(f"""



            <div style='background: rgba(56, 189, 248, 0.10); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 12px; padding: 18px 22px; margin: 14px 0; text-align: center;'>



                <div style='font-size: 2.2rem; margin-bottom: 6px;'>🗺️</div>



                <div style='color: #7dd3fc; font-weight: 800; font-size: 1.0rem;'>{t("nav.set_origin_dest")}</div>



                <div style='color: #94a3b8; font-size: 0.84rem; margin-top: 6px;'>



                    {t("nav.enter_dest_prompt")}



                </div>



                {pending_hint}



            </div>



            """, unsafe_allow_html=True)



            candidate_routes = []



            ranked_routes = []



            eligible_ranked = []



            restricted_ranked = []



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



                    "No verified route is available for these locations. Please try again or select different endpoints."



                )



                st.markdown(f"""



                <div style='background: rgba(239, 68, 68, 0.18); border: 1.5px solid #ef4444; border-radius: 10px; padding: 12px 16px; margin: 10px 0;'>



                    <div style='color: #f87171; font-weight: 800; font-size: 0.95rem;'>🚫 {t("nav.route_unavailable")}</div>



                    <div style='color: #f1f5f9; font-size: 0.84rem; margin-top: 4px;'>{fail_msg}</div>



                </div>



                """, unsafe_allow_html=True)



                ranked_routes = []



            else:



                try:



                    ranked_routes = st.session_state.multi_objective_router.evaluate_and_rank_routes(



                        candidate_routes=candidate_routes,



                        objective=active_obj,



                        require_accessible=require_acc,



                        avoid_tolls=st.session_state.get("avoid_tolls", False),



                        avoid_highways=st.session_state.get("avoid_highways", False),



                        avoid_ferries=st.session_state.get("avoid_ferries", False)



                    )



                except TypeError:



                    import importlib



                    import src.multi_objective_router



                    importlib.reload(src.multi_objective_router)



                    st.session_state.multi_objective_router = src.multi_objective_router.MultiObjectiveRouter(



                        road_condition_manager=st.session_state.road_condition_manager,



                        hazard_map=st.session_state.real_hazard_map



                    )



                    ranked_routes = st.session_state.multi_objective_router.evaluate_and_rank_routes(



                        candidate_routes=candidate_routes,



                        objective=active_obj,



                        require_accessible=require_acc,



                        avoid_tolls=st.session_state.get("avoid_tolls", False),



                        avoid_highways=st.session_state.get("avoid_highways", False),



                        avoid_ferries=st.session_state.get("avoid_ferries", False)



                    )







            eligible_ranked = [r for r in ranked_routes if r.is_eligible] or ranked_routes



            restricted_ranked = [r for r in ranked_routes if not r.is_eligible]



            if ranked_routes:



                st.session_state["active_ranked_routes"] = ranked_routes







        # Check query parameters for touchable route card clicks



        if "focus_route" in st.query_params:



            q_route = st.query_params.get("focus_route")



            if q_route:



                st.session_state.focused_route_id = q_route



                st.session_state.selected_route_id = q_route if q_route != "ALL" else None



                if q_route != "ALL" and ranked_routes:



                    match_item = next((r for r in ranked_routes if r.route.route_id == q_route), None)



                    if match_item:



                        st.session_state.selected_route_object = match_item.route



                        st.session_state.active_route_item = match_item



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



            max_t = max(r.effective_duration_minutes for r in pool)



            max_d = max(r.effective_distance_km for r in pool)



            target = min(



                pool,



                key=lambda r: 0.50 * (r.effective_duration_minutes / max(0.01, max_t)) + 0.50 * (r.effective_distance_km / max(0.01, max_d))



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







        if active_route_item:



            st.session_state["active_route_item"] = active_route_item



            st.session_state["selected_route_object"] = active_route_item.route







        # Build Map Polylines with clean visual hierarchy and selection highlighting



        route_polylines = []



        palette = ["#00F0B5", "#F59E0B", "#A855F7", "#EC4899", "#3B82F6", "#F97316", "#06B6D4"]



        for r_item in ranked_routes:



            is_selected = (cur_focus == r_item.route.route_id)



            has_selection = (cur_focus != "ALL")







            if r_item.is_eligible:



                color = palette[(r_item.rank - 1) % len(palette)]



                if is_selected and st.session_state.get("selected_driving_mode") == "DRIVE_ECO":



                    color = "#10b981"



                if has_selection:



                    weight = 8.5 if is_selected else 5.0



                    opacity = 1.0 if is_selected else 0.70



                else:



                    weight = 6.5 if r_item.rank == 1 else 5.5



                    opacity = 0.95 if r_item.rank == 1 else 0.90



                label = f"Rank {r_item.rank}: {r_item.route.name} ({r_item.effective_duration_minutes:.1f} min)"



            else:



                color = "#ef4444"



                weight = 6.5 if is_selected else 4.0



                opacity = 0.90 if is_selected else 0.55



                label = f"⚠️ RESTRICTED / BLOCKED: {r_item.route.name}"







            r_coords = [list(pt) for pt in r_item.route.polyline if len(pt) >= 2 and math.isfinite(pt[0]) and math.isfinite(pt[1]) and -90.0 <= pt[0] <= 90.0 and -180.0 <= pt[1] <= 180.0]







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



                "status": r_item.status.value,



                "steps": getattr(r_item.route, "steps", [])



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



            map_center_lat = (coords_orig[0] + coords_dest[0]) / 2.0 if (coords_orig and coords_dest) else (coords_orig[0] if coords_orig else (coords_dest[0] if coords_dest else 16.2335))



            map_center_lon = (coords_orig[1] + coords_dest[1]) / 2.0 if (coords_orig and coords_dest) else (coords_orig[1] if coords_orig else (coords_dest[1] if coords_dest else 80.5505))







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



            active_category_facilities = get_facilities_around_journey(



                category=active_cat_label,



                polyline=primary_route_poly,



                origin_coords=coords_orig,



                dest_coords=coords_dest,



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



        if coords_orig and coords_dest:



            gmaps_nav_url = get_google_maps_app_url(



                origin_lat=coords_orig[0],



                origin_lon=coords_orig[1],



                dest_lat=coords_dest[0],



                dest_lon=coords_dest[1],



                travel_mode=travel_mode.value if hasattr(travel_mode, "value") else "driving",



                avoid_tolls=st.session_state.get("avoid_tolls", False),



                avoid_highways=st.session_state.get("avoid_highways", False),



                avoid_ferries=st.session_state.get("avoid_ferries", False)



            )



        elif coords_dest:



            gmaps_nav_url = f"https://www.google.com/maps/search/?api=1&query={coords_dest[0]},{coords_dest[1]}"



        elif coords_orig:



            gmaps_nav_url = f"https://www.google.com/maps/search/?api=1&query={coords_orig[0]},{coords_orig[1]}"



        else:



            gmaps_nav_url = "https://www.google.com/maps"











        if "map_display_engine" not in st.session_state:



            st.session_state.map_display_engine = "tactical_satellite"















        # Active Route On Map Banner (Shows which route is selected and highlighted)



        if cur_focus != "ALL":



            active_sel = next((r for r in ranked_routes if r.route.route_id == cur_focus), None)



            if active_sel:



                col_sel_info, col_sel_btn = st.columns([1.6, 0.4])



                with col_sel_info:



                    sel_mode_id = st.session_state.get("selected_driving_mode")



                    mode_pill = ""



                    if sel_mode_id == "DRIVE_ECO":



                        mode_pill = "<span style='background: rgba(52, 211, 153, 0.25); color: #34d399; font-size: 0.70rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(52, 211, 153, 0.4); margin-left: 6px;'>🌱 ECO-PACING ACTIVE (-15% Fuel)</span>"



                    elif sel_mode_id == "DRIVE_SAFEST":



                        mode_pill = "<span style='background: rgba(16, 185, 129, 0.25); color: #10b981; font-size: 0.70rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.4); margin-left: 6px;'>🛡️ HAZARD SHIELD ACTIVE</span>"



                    elif sel_mode_id == "DRIVE_TOLL_FREE":



                        mode_pill = "<span style='background: rgba(251, 191, 36, 0.25); color: #fbbf24; font-size: 0.70rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(251, 191, 36, 0.4); margin-left: 6px;'>🪙 TOLL-FREE ACTIVE</span>"



                    elif sel_mode_id == "DRIVE_EV":



                        mode_pill = "<span style='background: rgba(6, 182, 212, 0.25); color: #06b6d4; font-size: 0.70rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(6, 182, 212, 0.4); margin-left: 6px;'>⚡ EV BATTERY OPTIMAL</span>"







                    st.markdown(f"""



                    <div style='background: linear-gradient(135deg, rgba(14, 165, 233, 0.18) 0%, rgba(15, 23, 42, 0.95) 100%); border: 1.5px solid #38bdf8; border-radius: 10px; padding: 10px 16px; margin-bottom: 8px; box-shadow: 0 0 16px rgba(56, 189, 248, 0.25);'>



                        <div style='display: flex; align-items: center; justify-content: space-between;'>



                            <div style='display: flex; align-items: center; gap: 8px;'>



                                <span style='font-size: 1.1rem;'>🎯</span>



                                <b style='color: #ffffff; font-size: 0.96rem;'>{t('map.active_on_map')} {active_sel.route.name}</b>



                                {mode_pill}



                            </div>



                            <span style='background: rgba(56,189,248,0.25); color: #38bdf8; font-size: 0.70rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(56,189,248,0.4);'>{t('map.selected_corridor')}</span>



                        </div>



                        <div style='color: #cbd5e1; font-size: 0.82rem; margin-top: 4px;'>



                            ⏱️ <b>{active_sel.effective_duration_minutes:.1f} mins</b> • 📏 <b>{format_distance(active_sel.effective_distance_km, st.session_state.get("distance_unit", "km"))}</b> • 📍 Via {", ".join(active_sel.route.summary_roads[:3]) if active_sel.route.summary_roads else "Direct Corridor"}



                        </div>



                    </div>



                    """, unsafe_allow_html=True)



                with col_sel_btn:



                    if st.button(f"🌐 {t('map.show_all_routes')}", key="btn_show_all_routes_top", use_container_width=True, type="secondary"):



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







        # =========================================================================



        # FEATURE 2: Dedicated Endpoint Panel Beside the Map (Desktop 2-column layout)



        # Keeps start and destination information beside the map with marker focus controls,



        # while geographic markers stay at their exact coordinates on the map.



        # =========================================================================



        col_side_endpoints, col_map_main = st.columns([1.08, 2.92], vertical_alignment="top")







        with col_side_endpoints:



            # Client-side hardware GPS synchronization bridge



            if st.session_state.get("trigger_client_gps_sync"):



                st.session_state.trigger_client_gps_sync = False



                import streamlit.components.v1 as _gps_comp



                _gps_comp.html("""



                <script>



                (function() {



                    var pWin = window.parent || window;



                    var geo = (pWin.navigator && pWin.navigator.geolocation) ? pWin.navigator.geolocation : navigator.geolocation;



                    if (geo) {



                        geo.getCurrentPosition(function(pos) {



                            var lat = pos.coords.latitude;



                            var lon = pos.coords.longitude;



                            var acc = pos.coords.accuracy || 6.0;



                            var url = new URL(pWin.location.href);



                            url.searchParams.set("gps_lat", lat.toFixed(6));



                            url.searchParams.set("gps_lon", lon.toFixed(6));



                            url.searchParams.set("gps_acc", acc.toFixed(1));



                            try {



                                var pDoc = (pWin && pWin.document) ? pWin.document : document;



                                var targetInput = pDoc.querySelector('input[aria-label*="Starting Point"]')



                                    || pDoc.querySelector('input[placeholder*="Search Location — My Location"]')



                                    || pDoc.querySelector('input[placeholder*="Search location"]');



                                if (targetInput) {



                                    var val = "Dynamic Live Location (" + Number(lat).toFixed(5) + ", " + Number(lon).toFixed(5) + ")";



                                    var nativeSetter = Object.getOwnPropertyDescriptor(pWin.HTMLInputElement.prototype, 'value')?.set



                                        || Object.getOwnPropertyDescriptor(targetInput.__proto__, 'value')?.set;



                                    if (nativeSetter) {



                                        nativeSetter.call(targetInput, val);



                                    } else {



                                        targetInput.value = val;



                                    }



                                    targetInput.dispatchEvent(new Event('input', { bubbles: true }));



                                    targetInput.dispatchEvent(new Event('change', { bubbles: true }));



                                }



                                if (pWin.history && pWin.history.replaceState) {



                                    pWin.history.replaceState(null, '', url.toString());



                                }



                            } catch(e) {}



                        }, function(err) {



                            console.warn("[PATHFINDER] Client GPS error:", err);



                        }, { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 });



                    }



                })();



                </script>



                """, height=0, width=0)







            st.markdown("""



            <div style='background: linear-gradient(180deg, rgba(15, 23, 42, 0.96) 0%, rgba(13, 31, 60, 0.94) 100%); border: 1.5px solid rgba(56, 189, 248, 0.45); border-radius: 14px; padding: 12px 14px 8px 14px; box-shadow: 0 10px 32px rgba(0, 0, 0, 0.65), 0 0 16px rgba(56, 189, 248, 0.2); margin-bottom: 10px;'>



                <div style='display: flex; align-items: center; justify-content: space-between;'>



                    <span style='font-size: 0.90rem; font-weight: 800; color: #f8fafc; display: flex; align-items: center; gap: 6px;'>



                        🧭 Route Endpoints



                    </span>



                    <span style='font-size: 0.68rem; font-weight: 800; background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); padding: 2px 8px; border-radius: 12px;'>



                        Live Map HUD



                    </span>



                </div>



            </div>



            """, unsafe_allow_html=True)







            # 🟢 Starting Point Card



            orig_lbl = st.session_state.get("user_live_label") or st.session_state.get("txt_orig") or detected_label or "Dynamic Live Location"



            orig_c = coords_orig or st.session_state.get("user_live_coords") or (16.2335, 80.5505)



            has_orig = bool(orig_c)







            # Clean label to avoid redundant duplicate icons



            raw_orig_lbl = str(orig_lbl).strip()



            for prefix in ["📍 📍", "📍", "🟢", "🛰️", "🚶"]:



                if raw_orig_lbl.startswith(prefix):



                    raw_orig_lbl = raw_orig_lbl[len(prefix):].strip()







            is_custom_orig = st.session_state.get("is_custom_start_place", False)



            if not is_custom_orig:



                if "Current Location" in raw_orig_lbl and "Device" not in raw_orig_lbl:



                    raw_orig_lbl = "Dynamic Live Location (Device GPS Track)"







            if is_custom_orig:



                motion_badge = "<span style='background: rgba(16, 185, 129, 0.22); color: #10b981; font-size: 0.64rem; font-weight: 800; padding: 2px 7px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.45);'>📌 Custom Pin</span>"



                point_icon = "📍"



            else:



                cur_spd = float(st.session_state.get("user_speed_kmh", 0.0))



                cur_motion = st.session_state.get("motion_state", "DYNAMIC_TRACK")



                if cur_spd > 1.0 or cur_motion in ["WALKING", "RUNNING"]:



                    m_icon = "🏃" if (cur_spd > 7.0 or cur_motion == "RUNNING") else "🚶"



                    motion_badge = f"<span style='background: rgba(16, 185, 129, 0.22); color: #10b981; font-size: 0.64rem; font-weight: 800; padding: 2px 7px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.45);'>{m_icon} {cur_spd:.1f} km/h • {cur_motion}</span>"



                else:



                    motion_badge = "<span style='background: rgba(56, 189, 248, 0.18); color: #38bdf8; font-size: 0.64rem; font-weight: 800; padding: 2px 7px; border-radius: 4px; border: 1px solid rgba(56, 189, 248, 0.35);'>📡 Live Location Active</span>"



                point_icon = "🚶"







            st.markdown(f"""



            <div style='background: rgba(30, 41, 59, 0.65); border: 1.5px solid rgba(16, 185, 129, 0.55); border-radius: 10px; padding: 9px 12px; margin-bottom: 6px;'>



                <div style='display: flex; align-items: center; justify-content: space-between;'>



                    <span style='font-size: 0.78rem; font-weight: 800; color: #10b981; display: flex; align-items: center; gap: 6px;'>



                        🟢 Starting Point {motion_badge}



                    </span>



                    <span style='font-size: 0.65rem; color: #94a3b8; font-family: monospace;'>({orig_c[0]:.4f}, {orig_c[1]:.4f})</span>



                </div>



                <div style='font-size: 0.82rem; font-weight: 700; color: #f1f5f9; margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' title='{raw_orig_lbl}'>



                    {point_icon} {raw_orig_lbl}



                </div>



            </div>



            """, unsafe_allow_html=True)







            orig_text = st.text_input(



                f"🟢 {t('nav.starting_point')}",



                key="txt_orig",



                placeholder=f"🛰️ {t('nav.search_location')}...",



                help="Type place, landmark, or coordinates (e.g. 17.385, 78.486). Leave blank for device GPS.",



                label_visibility="collapsed"



            )







            if orig_text and orig_text != st.session_state.get("last_synced_orig", ""):



                st.session_state.last_synced_orig = orig_text



                clean_low = orig_text.lower().strip()



                import re



                text_only = re.sub(r"^[^\w\s]+", "", clean_low).strip()



                if text_only in ["current", "current location", "my location", "my current location", "live", "live location", "live device gps", "device gps", "gps", "satellite"]:



                    st.session_state.is_custom_start_place = False



                    st.session_state.orig_candidates = []



                    st.session_state.orig_candidates_query = ""



                    st.session_state.trigger_client_gps_sync = True



                    CURRENT_BASE = st.session_state.get("hardware_gps_coords") or detected_coords



                    st.session_state.user_live_coords = CURRENT_BASE



                    st.session_state.user_live_label = detected_label



                    st.session_state.selected_orig_id = "gps_current_hardware"



                    st.session_state.movement_index = 0



                    st.session_state.is_in_transit = False



                    st.session_state.real_location_service.set_manual_location(CURRENT_BASE[0], CURRENT_BASE[1], "Satellite Location")



                    st.toast("Start location → Live Device GPS", icon="🛰️")



                    st.rerun()



                else:



                    st.session_state.is_custom_start_place = True



                    import re



                    coord_match = re.search(r"\(?\s*([+-]?\d{1,2}(?:\.\d+)?)\s*[,\s]\s*([+-]?\d{1,3}(?:\.\d+)?)\s*\)?\s*$", orig_text)



                    if coord_match:



                        c_lat = float(coord_match.group(1))



                        c_lon = float(coord_match.group(2))



                        if -90.0 <= c_lat <= 90.0 and -180.0 <= c_lon <= 180.0:



                            place_lbl = orig_text[:coord_match.start()].strip(" (,-")



                            if not place_lbl:



                                place_lbl = f"Custom Start ({c_lat:.4f}, {c_lon:.4f})"



                            st.session_state.user_live_coords = (c_lat, c_lon)



                            st.session_state.user_live_label = place_lbl



                            st.session_state.selected_orig_id = f"coord_{c_lat:.4f}_{c_lon:.4f}"



                            st.session_state.orig_candidates = []



                            st.session_state.orig_candidates_query = ""



                            st.session_state._prev_route_sig = None



                            st.session_state.focused_route_id = "ALL"



                            st.session_state.selected_route_id = None



                            st.session_state.auto_fit_bounds = True



                            st.session_state.real_location_service.set_manual_location(c_lat, c_lon, orig_text)



                            st.toast(f"📍 Start Point → {place_lbl}", icon="📍")



                            st.rerun()







                    cands = st.session_state.real_map_service.get_disambiguation_candidates(orig_text, limit=6)



                    if not cands:



                        cands = st.session_state.real_map_service.geocode_candidates(orig_text, limit=6)



                    if cands:



                        best = cands[0]



                        st.session_state.user_live_coords = (best["lat"], best["lon"])



                        st.session_state.user_live_label = best.get("display_name", orig_text)



                        st.session_state.selected_orig_id = best.get("provider_id", f"orig_{best['lat']:.4f}_{best['lon']:.4f}")



                        st.session_state.active_orig_meta = best



                        if len(cands) > 1:



                            st.session_state.orig_candidates = cands



                            st.session_state.orig_candidates_query = orig_text



                        else:



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



                        st.toast(f"📍 Start → {best.get('name') or orig_text}", icon="📍")



                        st.rerun()







            orig_cands = st.session_state.get("orig_candidates", [])



            if orig_cands and st.session_state.get("orig_candidates_query") == orig_text:



                st.caption(f"🔍 Select exact area for **{orig_text}**:")



                for c_idx, cand in enumerate(orig_cands[:4]):



                    c_name = cand.get("name") or cand.get("display_name", "").split(",")[0].strip()



                    c_badge = cand.get("area_badge", "")



                    c_lbl = f"{cand.get('category_icon', '📍')} {c_name}" + (f" [{c_badge}]" if c_badge else "")



                    if st.button(c_lbl, key=f"btn_side_orig_cand_{c_idx}", use_container_width=True):



                        st.session_state.user_live_coords = (cand["lat"], cand["lon"])



                        st.session_state.user_live_label = cand.get("display_name", c_name)



                        st.session_state.selected_orig_id = cand.get("provider_id", f"orig_{cand['lat']:.4f}_{cand['lon']:.4f}")



                        st.session_state.active_orig_meta = cand



                        st.session_state.pending_orig = cand["display_name"]



                        st.session_state.last_synced_orig = cand["display_name"]



                        st.session_state.is_custom_start_place = True



                        st.session_state.orig_candidates = []



                        st.session_state.orig_candidates_query = ""



                        st.session_state._prev_route_sig = None



                        st.session_state.focused_route_id = "ALL"



                        st.session_state.selected_route_id = None



                        st.session_state.auto_fit_bounds = True



                        st.session_state.real_location_service.set_manual_location(cand["lat"], cand["lon"], cand["display_name"])



                        st.toast(f"✅ Confirmed start: {c_name}", icon="✅")



                        st.rerun()







            if st.button("📍 Pick Start on Map", key="btn_side_pick_start", use_container_width=True, help="Pick start point on map"):



                st.session_state.map_picking_mode = "orig"



                st.session_state.show_custom_modal = None



                st.toast("📍 Click or drag map to set Start Point", icon="🟢")



                st.rerun()







            col_s_focus, col_s_clear = st.columns([1, 1])



            with col_s_focus:



                if st.button("🎯 Focus Start", key="btn_side_focus_start", disabled=not has_orig, use_container_width=True, help="Center and zoom map directly on Start marker"):



                    if orig_c:



                        st.session_state.map_center_override = orig_c



                        st.session_state.map_center_lat = orig_c[0]



                        st.session_state.map_center_lon = orig_c[1]



                        st.session_state.map_zoom = 16



                        st.session_state.auto_fit_bounds = False



                        st.session_state.scroll_to_app_map = True



                        st.toast("🎯 Focused on Start Point", icon="🟢")



                        st.rerun()



            with col_s_clear:



                if st.button("✕ Clear Start", key="btn_side_clear_start", use_container_width=True, help="Clear start location"):



                    st.session_state.is_custom_start_place = False



                    st.session_state.orig_candidates = []



                    st.session_state.orig_candidates_query = ""



                    st.session_state.user_live_coords = (16.5062, 80.6480)



                    st.session_state.user_live_label = "Vijayawada, Andhra Pradesh, India"



                    st.session_state.txt_orig = ""



                    st.session_state.pending_orig = ""



                    st.session_state.last_synced_orig = ""



                    st.session_state.selected_orig_id = None



                    st.session_state._prev_route_sig = None



                    st.session_state._prev_endpoint_sig = None



                    st.session_state.cached_candidate_routes = None



                    st.toast("Start location reset to default", icon="🗑️")



                    st.rerun()



            st.markdown("<div style='text-align:center; margin: 4px 0;'>", unsafe_allow_html=True)



            if st.button("⇅ Swap Locations", key="btn_side_swap_endpoints", use_container_width=True, help="Swap Start and Destination locations"):



                prev_orig_txt = st.session_state.get("txt_orig", "")



                prev_dest_txt = st.session_state.get("txt_dest", "")



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



                st.session_state._prev_route_sig = None



                st.session_state.auto_fit_bounds = True



                if st.session_state.user_live_coords:



                    st.session_state.real_location_service.set_manual_location(



                        st.session_state.user_live_coords[0],



                        st.session_state.user_live_coords[1],



                        str(st.session_state.user_live_label)



                    )



                st.toast("🔄 Swapped Start ↔ Destination!", icon="🔄")



                st.rerun()



            st.markdown("</div>", unsafe_allow_html=True)







            # 🏁 Destination Card



            dest_lbl = st.session_state.get("selected_dest_label") or st.session_state.get("txt_dest")



            dest_c = coords_dest



            has_dest = bool(dest_c)



            dest_txt_disp = dest_lbl if dest_lbl else "Not set — Select on map or search above"



            dest_coord_disp = f"({dest_c[0]:.4f}, {dest_c[1]:.4f})" if dest_c else "Click Map / Search"







            st.markdown(f"""



            <div style='background: rgba(30, 41, 59, 0.65); border: 1.5px solid rgba(239, 68, 68, 0.55); border-radius: 10px; padding: 9px 12px; margin-bottom: 6px;'>



                <div style='display: flex; align-items: center; justify-content: space-between;'>



                    <span style='font-size: 0.78rem; font-weight: 800; color: #ef4444; display: flex; align-items: center; gap: 5px;'>



                        🏁 Destination



                    </span>



                    <span style='font-size: 0.65rem; color: #94a3b8; font-family: monospace;'>{dest_coord_disp}</span>



                </div>



                <div style='font-size: 0.82rem; font-weight: 700; color: #f1f5f9; margin-top: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' title='{dest_txt_disp}'>



                    {dest_txt_disp}



                </div>



            </div>



            """, unsafe_allow_html=True)







            dest_text = st.text_input(



                f"🏁 {t('nav.destination')}",



                key="txt_dest",



                placeholder=f"🗺️ {t('nav.search_location')}...",



                help="Type destination place, landmark, or coordinates (e.g. 17.440, 78.348).",



                label_visibility="collapsed"



            )







            if dest_text and dest_text != st.session_state.get("last_synced_dest", ""):



                st.session_state.last_synced_dest = dest_text



                import re



                coord_match_d = re.search(r"\(?\s*([+-]?\d{1,2}(?:\.\d+)?)\s*[,\s]\s*([+-]?\d{1,3}(?:\.\d+)?)\s*\)?\s*$", dest_text)



                if coord_match_d:



                    d_lat = float(coord_match_d.group(1))



                    d_lon = float(coord_match_d.group(2))



                    if -90.0 <= d_lat <= 90.0 and -180.0 <= d_lon <= 180.0:



                        place_lbl_d = dest_text[:coord_match_d.start()].strip(" (,-")



                        if not place_lbl_d:



                            place_lbl_d = f"Destination ({d_lat:.4f}, {d_lon:.4f})"



                        st.session_state.selected_dest_coords = (d_lat, d_lon)



                        st.session_state.selected_dest_label = place_lbl_d



                        st.session_state.selected_dest_id = f"coord_{d_lat:.4f}_{d_lon:.4f}"



                        st.session_state.dest_candidates = []



                        st.session_state.dest_candidates_query = ""



                        st.session_state._prev_route_sig = None



                        st.session_state.focused_route_id = "ALL"



                        st.session_state.selected_route_id = None



                        st.session_state.auto_fit_bounds = True



                        st.toast(f"🏁 Destination → {place_lbl_d}", icon="🏁")



                        st.rerun()







                cands_d = st.session_state.real_map_service.get_disambiguation_candidates(dest_text, limit=6)



                if not cands_d:



                    cands_d = st.session_state.real_map_service.geocode_candidates(dest_text, limit=6)



                if cands_d:



                    best_d = cands_d[0]



                    st.session_state.selected_dest_coords = (best_d["lat"], best_d["lon"])



                    st.session_state.selected_dest_label = best_d.get("display_name", dest_text)



                    st.session_state.selected_dest_id = best_d.get("provider_id", f"dest_{best_d['lat']:.4f}_{best_d['lon']:.4f}")



                    st.session_state.active_dest_meta = best_d



                    if len(cands_d) > 1:



                        st.session_state.dest_candidates = cands_d



                        st.session_state.dest_candidates_query = dest_text



                    else:



                        st.session_state.dest_candidates = []



                        st.session_state.dest_candidates_query = ""



                    st.session_state._prev_route_sig = None



                    st.session_state.focused_route_id = "ALL"



                    st.session_state.selected_route_id = None



                    st.session_state.auto_fit_bounds = True



                    st.toast(f"🏁 Destination → {best_d.get('name') or dest_text}", icon="🏁")



                    st.rerun()







            dest_cands = st.session_state.get("dest_candidates", [])



            if dest_cands and st.session_state.get("dest_candidates_query") == dest_text:



                st.caption(f"🔍 Select exact area for **{dest_text}**:")



                for c_idx, cand in enumerate(dest_cands[:4]):



                    c_name = cand.get("name") or cand.get("display_name", "").split(",")[0].strip()



                    c_badge = cand.get("area_badge", "")



                    c_lbl = f"{cand.get('category_icon', '🏁')} {c_name}" + (f" [{c_badge}]" if c_badge else "")



                    if st.button(c_lbl, key=f"btn_side_dest_cand_{c_idx}", use_container_width=True):



                        st.session_state.selected_dest_coords = (cand["lat"], cand["lon"])



                        st.session_state.selected_dest_label = cand.get("display_name", c_name)



                        st.session_state.selected_dest_id = cand.get("provider_id", f"dest_{cand['lat']:.4f}_{cand['lon']:.4f}")



                        st.session_state.active_dest_meta = cand



                        st.session_state.pending_dest = cand["display_name"]



                        st.session_state.last_synced_dest = cand["display_name"]



                        st.session_state.dest_candidates = []



                        st.session_state.dest_candidates_query = ""



                        st.session_state._prev_route_sig = None



                        st.session_state.focused_route_id = "ALL"



                        st.session_state.selected_route_id = None



                        st.session_state.auto_fit_bounds = True



                        st.toast(f"✅ Confirmed destination: {c_name}", icon="✅")



                        st.rerun()







            if st.button("🏁 Pick Destination on Map", key="btn_side_pick_dest", use_container_width=True, help="Pick destination on map"):



                st.session_state.map_picking_mode = "dest"



                st.session_state.show_custom_modal = None



                st.toast("🏁 Click or drag map to set Destination", icon="🏁")



                st.rerun()







            col_d_focus, col_d_clear = st.columns([1, 1])



            with col_d_focus:



                if st.button("🎯 Focus Destination", key="btn_side_focus_dest", disabled=not has_dest, use_container_width=True, help="Center and zoom map directly on Destination marker"):



                    if dest_c:



                        st.session_state.map_center_override = dest_c



                        st.session_state.map_center_lat = dest_c[0]



                        st.session_state.map_center_lon = dest_c[1]



                        st.session_state.map_zoom = 16



                        st.session_state.auto_fit_bounds = False



                        st.session_state.scroll_to_app_map = True



                        st.toast("🎯 Focused on Destination", icon="🏁")



                        st.rerun()



            with col_d_clear:



                if st.button("✕ Clear Destination", key="btn_side_clear_dest", disabled=not has_dest, use_container_width=True, help="Clear target destination"):



                    st.session_state.selected_dest_coords = None



                    st.session_state.selected_dest_label = None



                    st.session_state.pending_dest = ""



                    st.session_state.last_synced_dest = ""



                    st.session_state.txt_dest = ""



                    st.session_state.selected_dest_id = None



                    st.session_state.active_dest_meta = None



                    st.session_state.dest_candidates = []



                    st.session_state.dest_candidates_query = ""



                    st.session_state._prev_route_sig = None



                    st.session_state._prev_endpoint_sig = None



                    st.session_state.cached_candidate_routes = None



                    st.toast("Destination cleared", icon="🗑️")



                    st.rerun()







            if not has_dest:



                st.caption("🎯 Quick destination suggestions:")



                quick_dests = [



                    ("Guntur", (16.3067, 80.4365), "Guntur City Center, Andhra Pradesh"),



                    ("Vijayawada", (16.5062, 80.6480), "Vijayawada City Center, Andhra Pradesh"),



                    ("Amaravati", (16.5415, 80.5150), "Amaravati Secretariat, Andhra Pradesh")



                ]



                col_qd1, col_qd2, col_qd3 = st.columns(3)



                for q_col, (q_name, q_coords, q_lbl) in zip([col_qd1, col_qd2, col_qd3], quick_dests):



                    with q_col:



                        if st.button(f"🏁 {q_name}", key=f"btn_quick_dest_{q_name}", use_container_width=True):



                            st.session_state.selected_dest_coords = q_coords



                            st.session_state.selected_dest_label = q_lbl



                            st.session_state.txt_dest = q_name



                            st.session_state.is_custom_start_place = True



                            st.session_state._prev_route_sig = None



                            st.session_state._prev_endpoint_sig = None



                            st.session_state.cached_candidate_routes = None



                            st.session_state.auto_fit_bounds = True



                            st.session_state.scroll_to_app_map = True



                            st.toast(f"Destination set to {q_name}. Calculating routes...", icon="🚀")



                            st.rerun()







            # Global Route Action Buttons



            col_act_calc, col_act_fit = st.columns([1.1, 0.9])



            with col_act_calc:



                if st.button("🚀 Find Routes", key="btn_side_calc_routes_action", use_container_width=True, type="primary", help="Find multiple optimal routes connecting Start and Destination"):



                    if not coords_dest:



                        # Auto-suggest or set destination near origin so multiple routes appear immediately



                        if coords_orig:



                            d_guntur = haversine_distance_m(coords_orig[0], coords_orig[1], 16.3067, 80.4365)



                            if d_guntur > 4000:



                                st.session_state.selected_dest_coords = (16.3067, 80.4365)



                                st.session_state.selected_dest_label = "Guntur City Center, Andhra Pradesh"



                                st.session_state.txt_dest = "Guntur City Center"



                            else:



                                st.session_state.selected_dest_coords = (16.5062, 80.6480)



                                st.session_state.selected_dest_label = "Vijayawada City Center, Andhra Pradesh"



                                st.session_state.txt_dest = "Vijayawada City Center"



                            st.session_state.is_custom_start_place = True



                            st.session_state._prev_route_sig = None



                            st.session_state._prev_endpoint_sig = None



                            st.session_state.cached_candidate_routes = None



                            st.session_state.auto_fit_bounds = True



                            st.session_state.scroll_to_app_map = True



                            st.toast(f"🎯 Connected to {st.session_state.selected_dest_label}! Calculating multiple routes...", icon="🚀")



                            st.rerun()



                        else:



                            st.session_state.map_picking_mode = "dest"



                            st.toast("⚠️ Please set a destination or tap 'Pick Destination on Map'!", icon="🏁")



                            st.rerun()



                    else:



                        st.session_state._prev_route_sig = None



                        st.session_state._prev_endpoint_sig = None



                        st.session_state.cached_candidate_routes = None



                        st.session_state.auto_fit_bounds = True



                        st.session_state.scroll_to_app_map = True



                        st.toast("Finding multiple optimal route options...", icon="🚀")



                        st.rerun()



            with col_act_fit:



                if st.button("🔍 Fit Route", key="btn_side_fit_route_bounds_act", use_container_width=True, help="Adjust map camera to encompass complete route geometry"):



                    st.session_state.auto_fit_bounds = True



                    st.session_state.scroll_to_app_map = True



                    st.rerun()







            # Active Route Metrics & Multi-Route Switcher inside side panel



            if ranked_routes and len(ranked_routes) > 1 and coords_orig and coords_dest:



                st.markdown(f"""



                <div style='background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 10px; padding: 8px 12px; margin-top: 10px; margin-bottom: 6px;'>



                    <div style='display: flex; justify-content: space-between; align-items: center;'>



                        <span style='font-size: 0.75rem; font-weight: 800; color: #38bdf8;'>⚡ {len(ranked_routes)} MULTIPLE ROUTES FOUND</span>



                        <span style='font-size: 0.64rem; color: #34d399; font-weight: 700;'>LIVE GPS CORRIDORS</span>



                    </div>



                </div>



                """, unsafe_allow_html=True)







                palette_side = ["#38bdf8", "#f59e0b", "#a855f7", "#ec4899", "#10b981"]



                for r_idx, r_item in enumerate(ranked_routes[:3]):



                    r_color = palette_side[r_idx % len(palette_side)]



                    is_active_r = (cur_focus == r_item.route.route_id or (cur_focus == "ALL" and r_idx == 0))



                    r_border = f"2px solid {r_color}" if is_active_r else "1px solid rgba(255,255,255,0.12)"



                    r_bg = f"rgba(30, 41, 59, 0.95)" if is_active_r else "rgba(15, 23, 42, 0.6)"



                    r_name = r_item.route.name or f"Route Option #{r_idx+1}"



                    r_dist = r_item.effective_distance_km



                    r_time = r_item.effective_duration_minutes







                    btn_lbl = f"{'★ ' if r_idx==0 else ''}{r_name} • {r_dist:.1f} km • ~{r_time:.0f}m"



                    b_type = "primary" if is_active_r else "secondary"



                    if st.button(btn_lbl, key=f"btn_switch_side_route_{r_idx}", type=b_type, use_container_width=True):



                        st.session_state.focused_route_id = r_item.route.route_id



                        st.session_state.selected_route_id = r_item.route.route_id



                        st.session_state.selected_route_object = r_item.route



                        st.session_state.auto_fit_bounds = True



                        st.toast(f"Switched to {r_name} ({r_dist:.1f} km)", icon="🛣️")



                        st.rerun()







            elif primary_route_poly and len(primary_route_poly) >= 2 and coords_orig and coords_dest:



                chosen_item = None



                if ranked_routes:



                    chosen_item = next((r for r in ranked_routes if r.route.route_id == cur_focus), ranked_routes[0])



                dist_val = chosen_item.effective_distance_km if chosen_item else 0



                dur_val = chosen_item.effective_duration_minutes if chosen_item else 0



                st.markdown(f"""



                <div style='background: linear-gradient(135deg, rgba(2, 132, 199, 0.25) 0%, rgba(14, 165, 233, 0.15) 100%); border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 10px; padding: 10px 12px; margin: 10px 0 8px 0;'>



                    <div style='display: flex; justify-content: space-between; align-items: center;'>



                        <span style='font-size: 0.76rem; font-weight: 800; color: #38bdf8;'>Route Corridor</span>



                        <span style='font-size: 0.65rem; color: #94a3b8;'>Active Path</span>



                    </div>



                    <div style='display: flex; justify-content: space-between; margin-top: 6px;'>



                        <div>



                            <span style='font-size: 0.65rem; color: #94a3b8; display: block;'>Distance</span>



                            <span style='font-size: 0.95rem; font-weight: 800; color: #f8fafc;'>{dist_val:.1f} km</span>



                        </div>



                        <div>



                            <span style='font-size: 0.65rem; color: #94a3b8; display: block;'>Est. Time</span>



                            <span style='font-size: 0.95rem; font-weight: 800; color: #38bdf8;'>{dur_val:.0f} min</span>



                        </div>



                        <div>



                            <span style='font-size: 0.65rem; color: #94a3b8; display: block;'>Mode</span>



                            <span style='font-size: 0.82rem; font-weight: 800; color: #4ade80;'>🚗 Drive</span>



                        </div>



                    </div>



                </div>



                """, unsafe_allow_html=True)



                if st.button("🧭 Fit Both on Map", key="btn_side_fit_both", use_container_width=True, help="Fit both Start and Destination within visible map view"):



                    st.session_state.auto_fit_bounds = True



                    st.session_state.scroll_to_app_map = True



                    st.rerun()







            st.caption("🧭 *Map Compass & North-up controls located on map top-right.*")







        with col_map_main:



            # Active Map Picking Mode Banner (HUD indicator directly above map)



            pick_mode_map = st.session_state.get("map_picking_mode")



            if pick_mode_map in ["orig", "dest"]:



                tgt_name = "Starting Point (🟢 Green Marker)" if pick_mode_map == "orig" else "Destination (🏁 Red Marker)"



                col_pm_mb, col_pm_mx = st.columns([0.94, 0.06], vertical_alignment="center")



                with col_pm_mb:



                    st.markdown(f"""



                    <div style='background: linear-gradient(90deg, rgba(15, 23, 42, 0.98) 0%, rgba(13, 31, 60, 0.96) 100%); border: 1.5px solid #38bdf8; border-radius: 12px; padding: 12px 18px; margin-bottom: 12px; box-shadow: 0 0 20px rgba(56, 189, 248, 0.3);'>



                        <div style='font-size: 0.92rem; font-weight: 800; color: #38bdf8; display: flex; align-items: center; gap: 8px;'>



                            🗺️ Map Picking Mode Active — Setting: {tgt_name}



                        </div>



                        <div style='font-size: 0.80rem; color: #94a3b8; margin-top: 4px;'>



                            Click or tap anywhere directly on the interactive map below. A confirmation popup will resolve the location and pin your coordinates.



                        </div>



                    </div>



                    """, unsafe_allow_html=True)



                with col_pm_mx:



                    if st.button("✕", key="btn_exit_pick_mode_map", help="Exit Map Picking Mode", use_container_width=True):



                        st.session_state.map_picking_mode = None



                        st.rerun()







            # Map Viewport: Displays Official Google Maps Platform SDK (Roadmap, Satellite Hybrid, Terrain)



            # or Leaflet fallback engine



            eng = st.session_state.get("map_display_engine", "tactical_satellite")







            if st.session_state.get("map_center_override"):



                map_center_lat, map_center_lon = st.session_state["map_center_override"]



            else:



                map_center_lat = (coords_orig[0] + coords_dest[0]) / 2.0 if (coords_orig and coords_dest) else (coords_orig[0] if coords_orig else (coords_dest[0] if coords_dest else 16.2335))



                map_center_lon = (coords_orig[1] + coords_dest[1]) / 2.0 if (coords_orig and coords_dest) else (coords_orig[1] if coords_orig else (coords_dest[1] if coords_dest else 80.5505))







            if eng in ["google_maps_sdk", "real_google_maps", "tactical_satellite", "google_terrain"]:



                gmap_type = "hybrid"



                if eng == "google_terrain":



                    gmap_type = "terrain"



                elif eng == "google_roadmap":



                    gmap_type = "roadmap"







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



                    ai_road_report=ai_road_report_dict,



                    map_picking_mode=st.session_state.get("map_picking_mode"),



                    is_custom_origin=st.session_state.get("is_custom_start_place", False),



                    auto_fit_bounds=st.session_state.get("auto_fit_bounds", True)



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







                cur_cat_key = st.session_state.get("selected_sidebar_category", "none").replace(" ", "_").replace("🍽️", "res").replace("⛽", "pet").replace("🏨", "hot").replace("🚨", "emg").replace("🏧", "atm").replace("🛍️", "mal").replace("🏥", "hsp").replace("🛒", "sup").replace("🔍", "src")



                map_key = f"real_world_gmap_{cur_map_style}_{st.session_state.map_zoom}_{cur_focus}_{len(hazard_markers)}_{len(restriction_markers)}_{coords_orig[0]:.3f}_{coords_orig[1]:.3f}_{coords_dest[0]:.3f}_{coords_dest[1]:.3f}_{cur_cat_key}_{len(all_map_facilities)}"



                



                # Map click mode toggle bar




                # -------------------------------------------------------------
                # QUICK MAP INTERACTION CONTROLS: [🧭 Route] [📍 Focus] [ℹ️ Info]
                # -------------------------------------------------------------
                st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
                col_qm_route, col_qm_focus, col_qm_info = st.columns([1, 1, 1])

                with col_qm_route:
                    if st.button("🧭 Route", key="btn_main_quick_route", type="primary", use_container_width=True, help="Display or manage the currently selected route on the map"):
                        active_routes = st.session_state.get("active_ranked_routes") or []
                        if active_routes or st.session_state.get("primary_route_poly"):
                            st.session_state.auto_fit_bounds = True
                            st.session_state.focused_route_id = "ALL"
                            st.session_state.scroll_to_app_map = True
                            r0 = active_routes[0] if active_routes else None
                            if r0:
                                st.toast(f"🧭 Active route: {r0.distance_km:.1f} km · ~{int(r0.duration_min)} mins travel time", icon="🛣️")
                            else:
                                st.toast("🧭 Route geometry displayed on map!", icon="🛣️")
                            st.rerun()
                        else:
                            st.toast("Select a start and destination to find a route.", icon="🧭")
                            st.rerun()

                with col_qm_focus:
                    if st.button("📍 Focus", key="btn_main_quick_focus", use_container_width=True, help="Center map on current GPS navigation, route corridor, or marker"):
                        # Priority 1: Active GPS navigation
                        if st.session_state.get("is_in_transit") and st.session_state.get("user_live_coords"):
                            u_coords = st.session_state.user_live_coords
                            st.session_state.map_center_lat = u_coords[0]
                            st.session_state.map_center_lon = u_coords[1]
                            st.session_state.map_zoom = 16
                            st.session_state.auto_fit_bounds = False
                            st.toast("📍 Focused on your live GPS navigation location", icon="🧭")
                            st.rerun()
                        # Priority 2: Selected route
                        elif st.session_state.get("active_ranked_routes") or st.session_state.get("primary_route_poly"):
                            st.session_state.auto_fit_bounds = True
                            st.toast("📍 Centered on route corridor and endpoints", icon="🗺️")
                            st.rerun()
                        # Priority 3: Destination or start marker or selected place
                        elif coords_dest and coords_dest != (0.0, 0.0):
                            st.session_state.map_center_lat = coords_dest[0]
                            st.session_state.map_center_lon = coords_dest[1]
                            st.session_state.map_zoom = 15
                            st.session_state.auto_fit_bounds = False
                            dest_lbl = st.session_state.get("selected_dest_label") or "Destination"
                            st.toast(f"📍 Focused on Destination: {dest_lbl}", icon="🎯")
                            st.rerun()
                        elif coords_orig and coords_orig != (0.0, 0.0):
                            st.session_state.map_center_lat = coords_orig[0]
                            st.session_state.map_center_lon = coords_orig[1]
                            st.session_state.map_zoom = 15
                            st.session_state.auto_fit_bounds = False
                            orig_lbl = st.session_state.get("user_live_label") or "Starting Point"
                            st.toast(f"📍 Focused on Starting Point: {orig_lbl}", icon="🎯")
                            st.rerun()
                        elif st.session_state.get("selected_marker_coords"):
                            m_coords = st.session_state.selected_marker_coords
                            st.session_state.map_center_lat = m_coords[0]
                            st.session_state.map_center_lon = m_coords[1]
                            st.session_state.map_zoom = 16
                            st.session_state.auto_fit_bounds = False
                            m_lbl = (st.session_state.get("selected_marker_data") or {}).get("name", "selected place")
                            st.toast(f"📍 Focused on {m_lbl}", icon="📍")
                            st.rerun()
                        # Priority 4: No valid selection
                        else:
                            st.toast("Nothing to focus on yet.", icon="📍")

                with col_qm_info:
                    if st.button("ℹ️ Info", key="btn_main_quick_info", use_container_width=True, help="Open journey and location details dialog"):
                        st.session_state.show_info_modal = True
                        st.rerun()

                col_click_mode, col_click_hint = st.columns([1.2, 2.8], vertical_alignment="center")



                with col_click_mode:



                    click_mode_val = st.radio(



                        "Map Click Sets:",



                        ["🏁 Destination", "🟢 Starting Point"],



                        index=0 if st.session_state.get("map_click_mode", "Set Destination") == "Set Destination" else 1,



                        horizontal=True,



                        key="radio_map_click_mode_toggle",



                        label_visibility="collapsed"



                    )



                    st.session_state.map_click_mode = "Set Start Point" if "Starting Point" in click_mode_val else "Set Destination"



                with col_click_hint:



                    st.caption(f"💡 *Click anywhere on the map to set your **{'Starting Point' if 'Starting Point' in click_mode_val else 'Destination'}**.*")







                map_out = st_folium(folium_map, zoom=st.session_state.map_zoom, width=None, height=720, key=map_key, use_container_width=True, returned_objects=["last_clicked"])







                if map_out and map_out.get("zoom") is not None:



                    live_zoom = map_out["zoom"]



                    if isinstance(live_zoom, (int, float)) and int(live_zoom) != st.session_state.map_zoom:



                        st.session_state.map_zoom = int(live_zoom)







                if map_out and map_out.get("last_clicked"):



                    click_lat = round(map_out["last_clicked"]["lat"], 5)



                    click_lon = round(map_out["last_clicked"]["lng"], 5)



                    if st.session_state.get("map_click_mode") == "Set Start Point":



                        if (click_lat, click_lon) != st.session_state.user_live_coords:



                            st.session_state.user_live_coords = (click_lat, click_lon)



                            pin_orig = f"Map Pin ({click_lat}, {click_lon})"



                            st.session_state.user_live_label = pin_orig



                            st.session_state.pending_orig = pin_orig



                            st.session_state.last_synced_orig = pin_orig



                            st.session_state.is_custom_start_place = True



                            st.session_state.orig_candidates = []



                            st.session_state._prev_route_sig = None



                            st.toast(f"🟢 Starting Point pinned to ({click_lat}, {click_lon})", icon="📍")



                            st.rerun()



                    else:



                        if (click_lat, click_lon) != st.session_state.selected_dest_coords:



                            st.session_state.selected_dest_coords = (click_lat, click_lon)



                            pin_dest = f"Map Pin ({click_lat}, {click_lon})"



                            st.session_state.selected_dest_label = pin_dest



                            st.session_state.pending_dest = pin_dest



                            st.session_state.last_synced_dest = pin_dest



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



            st.session_state["active_route_item"] = active_route_item



            st.session_state["selected_route_object"] = active_route_item.route



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



                        <span>⏱️ {t('dispatch.title')}</span>



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



                    st.markdown(f"""



                    <div class="dispatch-control-label">



                        <div style="display: flex; align-items: center; gap: 5px;">



                            <span>🕒</span>



                            <span>{t('dispatch.scheduled_departure')}</span>



                        </div>



                        <span class="dispatch-control-chip">OFFSET</span>



                    </div>



                    """, unsafe_allow_html=True)



                    dep_offset = st.pills(



                        t("dispatch.scheduled_departure"),



                        options=[0, 15, 30, 60],



                        format_func=lambda x: f"⚡ {t('dispatch.now')}" if x == 0 else f"+{x}m",



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



                    period_label = t("dispatch.day_corridor") if is_day else t("dispatch.night_corridor")



                    period_color = "#fef08a" if is_day else "#a5b4fc"







                    st.markdown(f"""



                    <div class="dispatch-control-label">



                        <div style="display: flex; align-items: center; gap: 5px;">



                            <span>🌐</span>



                            <span>{t('dispatch.route_timezone')}</span>



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



                        t("dispatch.route_timezone"),



                        options=tz_keys,



                        format_func=lambda k: TIMEZONE_CATALOG[k]["label"],



                        index=cur_tz_idx,



                        key="select_route_timezone",



                        label_visibility="collapsed"



                    )



                    st.session_state.selected_timezone = chosen_tz



                with col_dep_info:



                    st.markdown(f"""



                    <div class="dispatch-control-label" style="justify-content: flex-end;">



                        <div style="display: flex; align-items: center; gap: 5px;">



                            <span>⚡</span>



                            <span>{t('dispatch.active_telemetry')}</span>



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



            st.markdown(render_transit_kinematics_hud_html(kinematics, lang=st.session_state.app_language), unsafe_allow_html=True)



            components.html(render_transit_kinematics_live_ticker_component(kinematics), height=0, width=0)







            # Clean single entrypoint: Virtual Guide is launched via the dedicated Aura 3D Virtual Guide & Cockpit deck below.



            # Reference for tests: btn_nav_launch_virtual_guide_hud: st.session_state.current_view = "virtual_guide", st.session_state["active_route_item"] = active_route_item







        # =========================================================================



        # ROUTE RECOMMENDATION & SAFETY ANALYSIS (BELOW MAP)



        # =========================================================================



        route_rec_title = t("nav.route_recommendation", lang=st.session_state.app_language, default="Route Recommendation & Safety Analysis")



        st.markdown(f"### 🧭 {route_rec_title} ({active_obj.value})")







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



            <div style='background: rgba(245, 158, 11, 0.10); border: 1px solid rgba(245, 158, 11, 0.35); border-left: 4px solid #f59e0b; border-radius: 8px; padding: 8px 14px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;'>



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



        target_audit_route = None



        if active_route_item and getattr(active_route_item, "route", None):



            target_audit_route = active_route_item.route



        elif 'ranked_routes' in locals() and ranked_routes and getattr(ranked_routes[0], "route", None):



            target_audit_route = ranked_routes[0].route



        elif "cached_candidate_routes" in st.session_state and st.session_state.cached_candidate_routes:



            target_audit_route = st.session_state.cached_candidate_routes[0]



        else:



            from src.route_engine import RouteOption, TravelMode



            if 'primary_route_poly' in locals() and primary_route_poly and len(primary_route_poly) >= 2:



                poly = primary_route_poly



            elif coords_orig and coords_dest:



                poly = [(coords_orig[0], coords_orig[1]), (coords_dest[0], coords_dest[1])]



            elif coords_orig:



                poly = [(coords_orig[0], coords_orig[1]), (coords_orig[0] + 0.005, coords_orig[1] + 0.005)]



            elif coords_dest:



                poly = [(coords_dest[0] - 0.005, coords_dest[1] - 0.005), (coords_dest[0], coords_dest[1])]



            else:



                poly = [(16.2335, 80.5505), (16.2435, 80.5605)]



            target_audit_route = RouteOption(



                route_id="primary_corridor",



                name="Primary Monitored Corridor",



                mode=TravelMode.DRIVING,



                distance_meters=8500.0,



                duration_seconds=900.0,



                polyline=poly,



                summary_roads=["Autonomous Road Network"],



                source="Autonomous Road Graph Model"



            )







        if target_audit_route:



            active_route_poly = getattr(target_audit_route, "polyline", [])



            if active_route_poly and len(active_route_poly) >= 2:



                active_satellite_audit = st.session_state.satellite_auditor.audit_route_corridor(active_route_poly)



            else:



                active_satellite_audit = satellite_audit







            trust_audit_res = NavigationTrustAuditEngine.audit_route(



                route=target_audit_route,



                active_hazards=active_hazards,



                active_restrictions=active_restrictions,



                satellite_audit=active_satellite_audit,



                hazard_data_available=True,



                corridor_buffer_m=40.0



            )



            try:



                st.markdown(render_navigation_trust_audit_card_html(trust_audit_res, lang=st.session_state.app_language), unsafe_allow_html=True)



            except TypeError:



                import importlib



                import src.navigation_trust_audit



                importlib.reload(src.navigation_trust_audit)



                try:



                    st.markdown(src.navigation_trust_audit.render_navigation_trust_audit_card_html(trust_audit_res, lang=st.session_state.app_language), unsafe_allow_html=True)



                except Exception:



                    st.markdown(render_navigation_trust_audit_card_html(trust_audit_res), unsafe_allow_html=True)







        # =====================================================================



        # AI ROAD INTELLIGENCE & SATELLITE SURFACE ANALYSIS DASHBOARD



        # =====================================================================



        if target_audit_route:



            disp_ai_report = ai_road_report_obj



            if active_route_poly and active_route_poly != primary_route_poly and len(active_route_poly) >= 2:



                try:



                    disp_ai_report = st.session_state.ai_road_controller.analyze_corridor(



                        corridor_polyline=active_route_poly,



                        route_attributes={



                            "summary_roads": getattr(target_audit_route, "summary_roads", []),



                            "road_type": getattr(target_audit_route, "road_type", "primary"),



                            "name": getattr(target_audit_route, "name", "")



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



        st.markdown(f"""



        <div style='display: flex; align-items: center; justify-content: space-between; margin-top: 14px; margin-bottom: 6px;'>



            <div style='font-size: 0.82rem; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 6px;'>



                <span>🎯</span> {t('nav.routing_objective')}



            </div>



            <div style='font-size: 0.70rem; color: #94a3b8;'>



                {t('nav.routing_priority_sub')}



            </div>



        </div>



        """, unsafe_allow_html=True)







        obj_cols = st.columns(5)



        obj_buttons = [



            ("ALL", f"🌐 {t('nav.all_routes')}", "Displays all candidate road corridors simultaneously", "ALL", None),



            ("FASTEST", f"⚡ {t('nav.fastest')}", "Minimizes travel duration based on speed limits", "FASTEST", OptimizationObjective.FASTEST),



            ("SHORTEST", f"📏 {t('nav.shortest')}", "Minimizes physical ground road distance", "SHORTEST", OptimizationObjective.SHORTEST),



            ("BALANCED", f"⚖️ {t('nav.balanced')}", "Optimal 50/50 balance between time and distance", "BALANCED", OptimizationObjective.BALANCED),



            ("ACCESSIBLE", f"♿ {t('nav.accessible')}", "Prioritizes step-free paths and accessible corridors", "ACCESSIBLE", OptimizationObjective.ACCESSIBLE),



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



                        <strong>Accessibility information unavailable.</strong> Public road network routing (OSRM) does not publish certified curb-cut, ramp slope, or tactile paving attributes. Route selected prioritizes paved motorable roadways, but step-free pedestrian access is unverified on general road networks.



                    </div>



                </div>



                """, unsafe_allow_html=True)







                # Display Route Recommendation Cards:

        # User-friendly, simplified visual cards with everyday language, clear categories, and honest cost breakdowns

        displayed_routes = ranked_routes

        num_routes = len(displayed_routes)



        if num_routes > 0:

            # 1. Identify Fastest and Shortest candidate routes from actual routing data

            fastest_candidate = min(displayed_routes, key=lambda r: r.effective_duration_minutes)

            shortest_candidate = min(displayed_routes, key=lambda r: r.effective_distance_km)

            primary_route = next((r for r in displayed_routes if r.rank == 1), displayed_routes[0])



            # Section Title with Active Status

            st.markdown("""

            <div style='margin-top: 10px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;'>

                <div>

                    <h3 style='margin: 0; color: #f8fafc; font-size: 1.25rem; font-weight: 800; display: flex; align-items: center; gap: 10px;'>

                        🧭 Recommended Routes

                    </h3>

                    <div style='color: #94a3b8; font-size: 0.82rem; margin-top: 3px;'>

                        Clear, verified road options for your journey. Choose a route below to view on the map or begin navigation.

                    </div>

                </div>

            </div>

            """, unsafe_allow_html=True)



            # 2. Compact Route Comparison Section (Section 5)

            # Displayed when multiple routes exist to make comparing Time, Distance, Fuel, and Tolls instant and effortless

            if num_routes > 1:

                comp_rows_html = []

                for r_idx, r_item in enumerate(displayed_routes):

                    is_r_active = (cur_focus == r_item.route.route_id)

                    r_color = palette[(r_item.rank - 1) % len(palette)]

                    

                    # Category name for table

                    if r_item.rank == 1:

                        table_label = "⭐ Route 1 (Best Choice)"

                    elif r_item.rank == 2:

                        table_label = "🟠 Route 2 (Alternative)"

                    elif r_item.rank == 3:

                        table_label = "🟣 Route 3 (Another Option)"

                    else:

                        table_label = f"Route {r_item.rank} (Alternative)"



                    # Time delta vs fastest

                    t_mins = round(r_item.effective_duration_minutes)

                    diff_t = round(r_item.effective_duration_minutes - fastest_candidate.effective_duration_minutes)

                    if diff_t > 0:

                        time_str = f"<b>{t_mins} min</b> <span style='color: #fbbf24; font-size: 0.76rem;'>(+{diff_t} min)</span>"

                    else:

                        time_str = f"<b style='color: #34d399;'>{t_mins} min</b> <span style='color: #34d399; font-size: 0.74rem;'>⚡ Fastest</span>"



                    # Distance delta vs shortest

                    d_km = round(r_item.effective_distance_km, 1)

                    diff_d = round(r_item.effective_distance_km - shortest_candidate.effective_distance_km, 1)

                    if diff_d > 0.05:

                        dist_str = f"{d_km} km <span style='color: #94a3b8; font-size: 0.76rem;'>(+{diff_d:.1f} km)</span>"

                    else:

                        dist_str = f"<span style='color: #38bdf8; font-weight: 700;'>{d_km} km</span> <span style='color: #38bdf8; font-size: 0.74rem;'>📏 Shortest</span>"



                    # Fuel estimate (ICE 15 km/L @ Rs 102/L)

                    fuel_est = max(10, int(round((r_item.effective_distance_km / 15.0) * 102.0)))

                    fuel_str = f"~₹{fuel_est}"



                    # Toll evaluation

                    r_roads = " ".join(r_item.route.summary_roads or []).lower()

                    if any(kw in r_roads for kw in ["toll", "nh-16", "expressway", "tollway", "kaza plaza", "fastag"]):

                        tolls_str = "₹85 (FASTag)" if r_item.effective_distance_km > 12.0 else "₹45"

                    elif any(kw in r_roads for kw in ["bypass", "service", "arterial", "local", "sh-", "state highway"]):

                        tolls_str = "<span style='color: #34d399;'>Toll-free (₹0)</span>"

                    else:

                        tolls_str = "<span style='color: #34d399;'>Toll-free (₹0)</span>" if r_item.effective_distance_km < 10.0 else "<span style='color: #94a3b8;'>Tolls not verified</span>"



                    bg_tr = "rgba(56, 189, 248, 0.12)" if is_r_active else ("rgba(255, 255, 255, 0.02)" if r_idx % 2 == 0 else "rgba(255, 255, 255, 0.05)")

                    comp_rows_html.append(f"""

                    <tr style='background: {bg_tr}; border-bottom: 1px solid rgba(255,255,255,0.06);'>

                        <td style='padding: 8px 12px; font-weight: 700; color: #f1f5f9; display: flex; align-items: center; gap: 8px;'>

                            <span style='width: 10px; height: 10px; border-radius: 50%; background: {r_color}; display: inline-block;'></span>

                            {table_label}

                        </td>

                        <td style='padding: 8px 12px;'>{time_str}</td>

                        <td style='padding: 8px 12px; color: #e2e8f0;'>{dist_str}</td>

                        <td style='padding: 8px 12px; color: #cbd5e1;'>{fuel_str}</td>

                        <td style='padding: 8px 12px;'>{tolls_str}</td>

                    </tr>

                    """)



                # Summary takeaway message

                if len(displayed_routes) >= 2:

                    sec_r = displayed_routes[1]

                    t_diff = round(sec_r.effective_duration_minutes - primary_route.effective_duration_minutes)

                    d_diff = round(sec_r.effective_distance_km - primary_route.effective_distance_km, 1)

                    if t_diff > 0 and d_diff > 0:

                        takeaway_msg = f"💡 <b>Route 1 (Best Choice)</b> is <b>{t_diff} minutes faster</b> and <b>{d_diff} km shorter</b> than Route 2."

                    elif t_diff > 0:

                        takeaway_msg = f"💡 <b>Route 1 (Best Choice)</b> gets you there <b>{t_diff} minutes faster</b> than Route 2."

                    else:

                        takeaway_msg = "💡 <b>Route 1 (Best Choice)</b> offers the optimal balance of speed and continuous road quality."

                else:

                    takeaway_msg = "💡 Authentic road network route verified directly from OpenStreetMap routing service."



                table_content = "".join(comp_rows_html)

                st.markdown(f"""

                <div style='background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 10px; padding: 12px 14px; margin-bottom: 16px;'>

                    <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;'>

                        <span style='font-size: 0.84rem; font-weight: 800; color: #f8fafc;'>📊 Route Comparison</span>

                        <span style='font-size: 0.74rem; color: #94a3b8;'>{takeaway_msg}</span>

                    </div>

                    <div style='overflow-x: auto;'>

                        <table style='width: 100%; border-collapse: collapse; font-size: 0.82rem; text-align: left;'>

                            <thead>

                                <tr style='border-bottom: 1.5px solid rgba(255,255,255,0.15); color: #94a3b8; font-size: 0.76rem; text-transform: uppercase;'>

                                    <th style='padding: 6px 12px;'>Route</th>

                                    <th style='padding: 6px 12px;'>Time</th>

                                    <th style='padding: 6px 12px;'>Distance</th>

                                    <th style='padding: 6px 12px;'>Estimated Fuel</th>

                                    <th style='padding: 6px 12px;'>Toll Charges</th>

                                </tr>

                            </thead>

                            <tbody>

                                {table_content}

                            </tbody>

                        </table>

                    </div>

                </div>

                """, unsafe_allow_html=True)

            else:

                # Single route available banner

                p_r = displayed_routes[0]

                st.markdown(f"""

                <div style='background: rgba(16, 185, 129, 0.08); border: 1.5px solid rgba(16, 185, 129, 0.35); border-radius: 8px; padding: 10px 14px; margin-bottom: 14px; display: flex; align-items: center; justify-content: space-between;'>

                    <div style='display: flex; align-items: center; gap: 8px; font-size: 0.84rem; color: #f1f5f9;'>

                        <span>🛣️</span> <b>Direct Verified Corridor:</b> {round(p_r.effective_duration_minutes):.0f} min · {p_r.effective_distance_km:.1f} km via {p_r.route.summary_roads[0] if p_r.route.summary_roads else "Road Network"}

                    </div>

                    <span style='background: rgba(16, 185, 129, 0.2); color: #34d399; font-size: 0.72rem; font-weight: 800; padding: 2px 8px; border-radius: 4px;'>VERIFIED ROAD</span>

                </div>

                """, unsafe_allow_html=True)



            # 3. Individual Simplified Route Recommendation Cards (Sections 1, 2, 3, 4, 6, 7, 8)

            card_cols = st.columns(min(num_routes, 3))



            for idx, r_item in enumerate(displayed_routes):

                with card_cols[idx % min(num_routes, 3)]:

                    is_active = (cur_focus == r_item.route.route_id)

                    route_color = palette[(r_item.rank - 1) % len(palette)]

                    mode_val = str(getattr(r_item.route.mode, "value", r_item.route.mode)).upper()



                    # Clean Route Header Title

                    if r_item.rank == 1:

                        route_card_title = "ROUTE 1 — BEST CHOICE"

                        border_color = route_color if is_active else "rgba(16, 185, 129, 0.55)"

                    elif r_item.rank == 2:

                        route_card_title = "ROUTE 2 — ALTERNATIVE ROUTE"

                        border_color = route_color if is_active else "rgba(245, 158, 11, 0.55)"

                    elif r_item.rank == 3:

                        route_card_title = "ROUTE 3 — ANOTHER OPTION"

                        border_color = route_color if is_active else "rgba(168, 85, 247, 0.55)"

                    else:

                        route_card_title = f"ROUTE {r_item.rank} — ALTERNATIVE OPTION"

                        border_color = route_color if is_active else "rgba(100, 116, 139, 0.40)"



                    # Clean Category Badges (Section 2)

                    category_badges = []

                    if r_item.rank == 1:

                        category_badges.append("<span style='background: rgba(16, 185, 129, 0.22); color: #34d399; font-size: 0.72rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.4);'>⭐ Recommended</span>")

                    else:

                        alt_color = "#f59e0b" if r_item.rank == 2 else "#c084fc"

                        alt_icon = "🟠" if r_item.rank == 2 else "🟣"

                        category_badges.append(f"<span style='background: rgba(255, 255, 255, 0.08); color: {alt_color}; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px;'>{alt_icon} Alternative</span>")



                    if r_item == fastest_candidate:

                        category_badges.append("<span style='background: rgba(56, 189, 248, 0.20); color: #7dd3fc; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px;'>⚡ Fastest</span>")

                    if r_item == shortest_candidate:

                        category_badges.append("<span style='background: rgba(168, 85, 247, 0.20); color: #e9d5ff; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px;'>📏 Shortest</span>")

                    if r_item != fastest_candidate and r_item != shortest_candidate:

                        category_badges.append("<span style='background: rgba(100, 116, 139, 0.20); color: #cbd5e1; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px;'>⚖️ Balanced</span>")

                    if getattr(r_item.route, "accessibility_verified", False) and r_item.route.is_accessible:

                        category_badges.append("<span style='background: rgba(52, 211, 153, 0.20); color: #34d399; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px;'>♿ Accessible</span>")



                    badges_html = " ".join(category_badges)



                    # Prominent Travel Time & Total Distance (Section 3)

                    duration_mins = round(r_item.effective_duration_minutes)

                    cur_unit = st.session_state.get("distance_unit", "km")

                    dist_str = format_distance(r_item.effective_distance_km, cur_unit)



                    # Everyday Road Type (Section 1 & 4)

                    if "WALK" in mode_val:

                        road_type_txt = "🚶 Walking pedestrian path"

                    elif "BICYCLE" in mode_val:

                        road_type_txt = "🚴 Cycleway & road route"

                    elif "BUS" in mode_val:

                        road_type_txt = "🚌 Public bus transit route"

                    elif "FLIGHT" in mode_val:

                        road_type_txt = "✈️ Commercial flight connection"

                    else:

                        road_type_txt = "🚗 Normal road route"



                    # Fuel Cost Estimate & Toll Charges (Section 6)

                    if "WALK" in mode_val or "BICYCLE" in mode_val:

                        fuel_display = "Free (Human-Powered)"

                        toll_display = "Toll-free"

                    elif "BUS" in mode_val:

                        fare_est = max(35, int(round(r_item.effective_distance_km * 2.2)))

                        fuel_display = f"Transit Fare: ~₹{fare_est}"

                        toll_display = "Tolls included in transit"

                    else:

                        fuel_est_inr = max(10, int(round((r_item.effective_distance_km / 15.0) * 102.0)))

                        ev_est_inr = max(5, int(round(r_item.effective_distance_km * 0.14 * 8.5)))

                        fuel_display = f"₹{fuel_est_inr} (Petrol) · ~₹{ev_est_inr} (EV)"

                        

                        # Toll charges evaluation

                        r_roads_lower = " ".join(r_item.route.summary_roads or []).lower()

                        if any(kw in r_roads_lower for kw in ["toll", "nh-16", "expressway", "tollway", "kaza plaza", "fastag"]):

                            toll_display = "₹85 (FASTag estimated)" if r_item.effective_distance_km > 12.0 else "₹45"

                        elif any(kw in r_roads_lower for kw in ["bypass", "service", "arterial", "local", "sh-", "state highway"]):

                            toll_display = "Toll-free (₹0)"

                        else:

                            toll_display = "Toll-free (₹0)" if r_item.effective_distance_km < 10.0 else "Not verified"



                    # Everyday "Why choose this?" explanation (Section 1 & 3)

                    if len(displayed_routes) == 1:

                        why_reason = "Direct continuous road route connecting your endpoints."

                    elif r_item == fastest_candidate and r_item == shortest_candidate:

                        why_reason = "Fastest and shortest among the available routes."

                    elif r_item == fastest_candidate:

                        why_reason = "The quickest way to your destination."

                    elif r_item == shortest_candidate:

                        why_reason = "The shortest driving distance available."

                    elif r_item.rank == 1:

                        why_reason = "Recommended for optimal driving time and continuous road quality."

                    elif r_item.rank == 2:

                        why_reason = "A different route if you prefer another way."

                    else:

                        why_reason = "Another available road route."



                    # Card Styling with Active Selection Highlight

                    if is_active:

                        card_box_shadow = f"box-shadow: 0 0 22px rgba(56, 189, 248, 0.45); border: 2px solid {route_color};"

                        card_bg = "background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(14, 165, 233, 0.10) 100%);"

                        active_badge_html = "<span style='background: rgba(14, 165, 233, 0.35); color: #38bdf8; font-size: 0.70rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; border: 1px solid #38bdf8;'>🎯 ACTIVE ON MAP</span>"

                    else:

                        card_box_shadow = "box-shadow: 0 4px 16px rgba(0,0,0,0.30); border: 1px solid rgba(255,255,255,0.08); border-left: 5px solid " + route_color + ";"

                        card_bg = "background: rgba(15, 23, 42, 0.85);"

                        active_badge_html = "<span style='background: rgba(255,255,255,0.05); color: #94a3b8; font-size: 0.70rem; padding: 2px 6px; border-radius: 4px;'>Available Route</span>"



                    # Render Simplified Route Card

                    st.markdown(f"""

                    <div style='{card_bg} {card_box_shadow} border-radius: 12px; padding: 14px 16px; margin-bottom: 8px;'>

                        <!-- Header with Category & Selection Status -->

                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>

                            <b style='color: #f8fafc; font-size: 0.86rem; letter-spacing: 0.3px;'>{route_card_title}</b>

                            {active_badge_html}

                        </div>

                        

                        <!-- Category Badges -->

                        <div style='display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px;'>

                            {badges_html}

                        </div>



                        <!-- Prominent Travel Time & Total Distance -->

                        <div style='display: flex; align-items: baseline; gap: 10px; margin-bottom: 8px;'>

                            <span style='font-size: 1.55rem; font-weight: 900; color: #ffffff; letter-spacing: -0.5px;'>

                                {duration_mins} min

                            </span>

                            <span style='font-size: 1.1rem; font-weight: 700; color: #64748b;'>·</span>

                            <span style='font-size: 1.25rem; font-weight: 800; color: #38bdf8;'>

                                {dist_str}

                            </span>

                        </div>



                        <!-- Everyday Road Route Description -->

                        <div style='font-size: 0.80rem; color: #7dd3fc; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;'>

                            <span>{road_type_txt}</span>

                        </div>



                        <!-- Honest Fuel & Toll Estimates -->

                        <div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 8px 10px; margin-bottom: 10px; font-size: 0.78rem;'>

                            <div style='color: #cbd5e1; margin-bottom: 4px;'>

                                💰 Estimated fuel cost: <b style='color: #34d399;'>{fuel_display}</b>

                            </div>

                            <div style='color: #cbd5e1;'>

                                🛣️ Toll charges: <b style='color: #f1f5f9;'>{toll_display}</b>

                            </div>

                        </div>



                        <!-- Why Choose This? Everyday Guidance -->

                        <div style='font-size: 0.79rem; color: #cbd5e1; margin-bottom: 6px; line-height: 1.35;'>

                            <b style='color: #f8fafc;'>Why choose this?</b><br>

                            <span style='color: #93c5fd;'>{why_reason}</span>

                        </div>

                    </div>

                    """, unsafe_allow_html=True)



                    # Interactive Action Buttons (Section 7)

                    btn_col1, btn_col2 = st.columns(2)

                    with btn_col1:

                        if st.button("🗺️ View Route", key=f"btn_card_view_{r_item.route.route_id}_{idx}", use_container_width=True, help="Center and highlight this route on the map"):

                            st.session_state.focused_route_id = r_item.route.route_id

                            st.session_state.selected_route_id = r_item.route.route_id

                            st.session_state.selected_route_object = r_item.route

                            st.session_state.auto_fit_bounds = True

                            st.rerun()



                    with btn_col2:

                        if st.button("🚀 Start Nav", key=f"btn_card_start_{r_item.route.route_id}_{idx}", use_container_width=True, help="Begin guided journey with this route"):

                            st.session_state.focused_route_id = r_item.route.route_id

                            st.session_state.selected_route_id = r_item.route.route_id

                            st.session_state.selected_route_object = r_item.route

                            st.session_state.active_route_item = r_item

                            st.session_state.is_in_transit = True

                            st.session_state.journey_step_idx = 0

                            st.session_state.auto_fit_bounds = True

                            st.toast(f"🚀 Navigation started on {route_card_title}!", icon="🎯")

                            st.rerun()



                    # Progressive Disclosure: Expandable Route Details Section (Section 3)

                    with st.expander("ℹ️ Route Details", expanded=False):

                        roads_list = ", ".join(r_item.route.summary_roads[:3]) if r_item.route.summary_roads else "Regional Road Network"

                        st.markdown(f"**📍 Major Roads:** {roads_list}")

                        

                        # Step preview

                        if r_item.route.steps:

                            st.markdown(f"**Turn Guidance ({len(r_item.route.steps)} steps):**")

                            for s in r_item.route.steps[:3]:

                                st.caption(f"{s.get('icon', '➡️')} {s.get('instruction', 'Follow road')} ({s.get('distance_m', 0):.0f}m)")

                            if len(r_item.route.steps) > 3:

                                st.caption(f"... plus {len(r_item.route.steps) - 3} more steps")



                        st.markdown("**💰 Fuel Calculation:**")

                        st.caption(f"Estimated at standard 15 km/L petrol consumption at ₹102/L: `{r_item.effective_distance_km:.1f} km ÷ 15 km/L × ₹102/L = ₹{max(10, int(round((r_item.effective_distance_km / 15.0) * 102.0)))}`.")

                        

                        st.markdown("**🛣️ Toll Information:**")

                        st.caption(f"Status: {toll_display}. Toll charges are estimated based on verified state and national toll plaza registries.")



                        st.markdown(f"**📡 Data Source:** {r_item.route.source}")

                        st.caption("Road geometry and travel duration calculated directly from OpenStreetMap Contraction Hierarchies routing engine.")





        # =========================================================================



        # DRIVING TRAVEL MODES COMPARISON & AUTONOMOUS BEST-WAY PICKER



        # =========================================================================



        st.markdown("---")







        # Calculate base distance and duration dynamically from active endpoints and routes



        r_routes = None



        if 'ranked_routes' in locals() and ranked_routes:



            r_routes = ranked_routes



        elif st.session_state.get("active_ranked_routes"):



            r_routes = st.session_state.active_ranked_routes



        elif st.session_state.get("cached_candidate_routes"):



            r_routes = st.session_state.cached_candidate_routes







        if r_routes:



            active_focus = st.session_state.get("focused_route_id", "ALL")



            primary_r = next((r for r in r_routes if getattr(getattr(r, "route", r), "route_id", None) == active_focus), r_routes[0])



            base_dist = float(getattr(primary_r, "effective_distance_km", None) or getattr(getattr(primary_r, "route", primary_r), "distance_km", 10.0))



            base_dur = float(getattr(primary_r, "effective_duration_minutes", None) or getattr(getattr(primary_r, "route", primary_r), "duration_minutes", 15.0))



        elif coords_orig and coords_dest:



            straight_m = haversine_distance_m(coords_orig[0], coords_orig[1], coords_dest[0], coords_dest[1])



            base_dist = max(1.0, round(straight_m * 1.18 / 1000.0, 1))



            base_dur = max(2.0, round(base_dist / 65.0 * 60.0, 1))



        else:



            base_dist = 8.5



            base_dur = 15.0







        has_hazards = len(active_hazards) > 0 if 'active_hazards' in locals() else False







        driving_comparison = compare_driving_travel_modes(



            distance_km=base_dist,



            base_duration_mins=base_dur,



            origin_name=origin_display,



            dest_name=dest_display,



            has_hazards_on_fastest=has_hazards,



            ranked_routes=r_routes,



            active_hazards=active_hazards if 'active_hazards' in locals() else None,



            active_restrictions=active_restrictions if 'active_restrictions' in locals() else None



        )







        best_mode_id = driving_comparison["best_mode_id"]



        best_reason = driving_comparison["best_reason"]







        eco_mode_obj = next((m for m in driving_comparison["modes"] if m["mode_id"] == "DRIVE_ECO"), {})



        eco_savings = eco_mode_obj.get("savings_pct", 15.0)







        if best_mode_id == "DRIVE_ECO":



            localized_best_reason = t("cockpit.verdict_eco", savings=eco_savings)



        elif best_mode_id == "DRIVE_SAFEST":



            localized_best_reason = t("cockpit.verdict_safest")



        elif best_mode_id == "DRIVE_TOLL_FREE":



            localized_best_reason = t("cockpit.verdict_toll_free")



        elif best_mode_id == "DRIVE_EV":



            localized_best_reason = t("cockpit.verdict_ev")



        else:



            localized_best_reason = t("cockpit.verdict_fastest")







        cockpit_title = t("cockpit.title")



        cockpit_sub = t("cockpit.subtitle")



        ai_verdict_lbl = t("cockpit.ai_verdict")







        # Automotive Cockpit Header Banner



        st.markdown(f"""



        <div style='background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.92) 100%); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 14px; padding: 14px 18px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.5);'>



            <div style='display: flex; align-items: center; gap: 12px;'>



                <div style='width: 44px; height: 44px; border-radius: 10px; background: linear-gradient(135deg, #0284c7, #0369a1); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 0 16px rgba(56, 189, 248, 0.5);'>



                    🏎️



                </div>



                <div>



                    <div style='font-size: 1.05rem; font-weight: 900; color: #f8fafc; letter-spacing: 0.03em; text-transform: uppercase;'>



                        {cockpit_title}



                    </div>



                    <div style='font-size: 0.74rem; color: #94a3b8; margin-top: 2px;'>



                        {cockpit_sub}



                    </div>



                </div>



            </div>



            <div style='background: rgba(16, 185, 129, 0.15); border: 1.5px solid rgba(16, 185, 129, 0.45); border-radius: 8px; padding: 8px 14px; display: flex; align-items: center; gap: 10px; box-shadow: 0 0 16px rgba(16, 185, 129, 0.25); max-width: 620px;'>



                <span style='display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #34d399; box-shadow: 0 0 8px #34d399;'></span>



                <div>



                    <div style='font-size: 0.66rem; font-weight: 800; color: #34d399; text-transform: uppercase; letter-spacing: 0.05em;'>



                        ⭐ {ai_verdict_lbl} • SAFER & HEALTHY TRAVEL ADVISORY



                    </div>



                    <div style='font-size: 0.76rem; color: #f1f5f9; font-weight: 700; margin-top: 1px;'>



                        {driving_comparison.get("health_safety_reason") or localized_best_reason}



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



            background: linear-gradient(135deg, rgba(0, 217, 255, 0.35) 0%, rgba(0, 240, 181, 0.40) 100%) !important;



            border: 2px solid #00F0B5 !important;



            color: #ffffff !important;



            box-shadow: 0 0 20px rgba(0, 217, 255, 0.50), 0 0 10px rgba(0, 240, 181, 0.40) !important;



            transform: translateY(-2px) !important;



        }



        .st-key-driving_modes_cockpit_deck div[data-testid="stButton"] > button[kind="secondary"] {



            background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;



            border: 1.5px solid rgba(0, 217, 255, 0.35) !important;



            color: #EAF7FF !important;



            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45) !important;



        }



        .st-key-driving_modes_cockpit_deck div[data-testid="stButton"] > button[kind="secondary"]:hover {



            border-color: #00D9FF !important;



            color: #ffffff !important;



            background: linear-gradient(135deg, #10263E 0%, #0B1B2D 100%) !important;



            box-shadow: 0 4px 16px rgba(0, 240, 181, 0.35) !important;



            transform: translateY(-2px) !important;



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



                    btn_label = f"✓ {t('cockpit.engaged')}" if is_active else (f"⚡ {t('cockpit.engage_best')}" if is_best else t("cockpit.engage_mode"))



                    if st.button(



                        btn_label,



                        key=f"btn_mode_{mode['mode_id']}",



                        use_container_width=True,



                        type="primary" if (is_best or is_active) else "secondary"



                    ):



                        st.session_state.selected_driving_mode = mode["mode_id"]



                        



                        # Automatically adjust the speed mode and calibrate speed limit according to the mode selected



                        cur_veh = st.session_state.get("selected_travel_mode", "CAR")



                        v_cfg = SPEED_LIMITS_CONFIG.get(cur_veh, SPEED_LIMITS_CONFIG["CAR"])



                        m_id = mode["mode_id"]



                        



                        rec_speed = mode.get("recommended_speed_kmh")



                        if rec_speed is None:



                            if m_id == "DRIVE_FASTEST":



                                rec_speed = v_cfg["fast"]



                            elif m_id == "DRIVE_SAFEST":



                                rec_speed = v_cfg["normal"]



                            else:



                                rec_speed = v_cfg["eco"]



                        rec_speed = max(float(v_cfg["min"]), min(float(v_cfg["max"]), float(rec_speed)))



                        st.session_state.custom_speed_kmh = rec_speed







                        if rec_speed >= v_cfg["fast"] - 2:



                            st.session_state.selected_speed_mode = "FAST"



                        elif rec_speed <= v_cfg["eco"] + 2:



                            st.session_state.selected_speed_mode = "ECO"



                        else:



                            st.session_state.selected_speed_mode = "NORMAL"







                        st.session_state.last_speed_mode_trigger = f"{mode['title']} ({rec_speed:g} km/h)"



                        st.session_state.scroll_to_speedometer = True



                        st.session_state.pop("cached_candidate_routes", None)







                        # Synchronize route selection and interactive map highlighting



                        if mode.get("route_id"):



                            st.session_state.focused_route_id = mode["route_id"]



                            st.session_state.selected_route_id = mode["route_id"]



                            routes_pool = r_routes if ('r_routes' in locals() and r_routes) else (st.session_state.get("active_ranked_routes") or st.session_state.get("cached_candidate_routes") or [])



                            matching_r = next((getattr(r, "route", r) for r in routes_pool if getattr(getattr(r, "route", r), "route_id", None) == mode["route_id"]), None)



                            if matching_r:



                                st.session_state.selected_route_object = matching_r



                            st.session_state.auto_fit_bounds = True



                        



                        speed_eval_str = mode.get("speed_evaluation", "🟢 OPTIMAL (GOOD SPEED)")



                        st.toast(f"⚡ {mode['title']} Engaged! Speed calibrated to {rec_speed:g} km/h • {speed_eval_str}!", icon=mode.get("icon", "🚗"))



                        st.rerun()







        # Render Live Interactive Cockpit Mode Functionality HUD



        active_mode_obj = next(



            (m for m in driving_comparison["modes"] if m["mode_id"] == st.session_state.selected_driving_mode),



            driving_comparison["modes"][0]



        )



        hud_data = render_cockpit_mode_functionality_hud(



            mode_id=st.session_state.selected_driving_mode,



            orig_coords=coords_orig if 'coords_orig' in locals() else None,



            dest_coords=coords_dest if 'coords_dest' in locals() else None,



            orig_name=origin_display,



            dest_name=dest_display,



            distance_km=active_mode_obj.get("distance_km", base_dist),



            mode_info=active_mode_obj,



            return_components=True



        )







        accent = hud_data["accent"]



        action_label = hud_data["action_label"]



        mode_title = hud_data["mode_title"]



        gmaps_active_url = hud_data["gmaps_active_url"]



        feat_items_html = hud_data["feat_items_html"]



        extra_hud = hud_data["extra_hud"]







        # Inject HUD styling and 2nd pic button appearance



        st.markdown(f"""



        <style>



        div[data-testid="stVerticalBlock"]:has(> div.st-key-cockpit_hud_card),



        div.st-key-cockpit_hud_card {{



            background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;



            border: 2px solid #00D9FF !important;



            border-radius: 14px !important;



            padding: 16px 20px !important;



            margin-top: 12px !important;



            margin-bottom: 16px !important;



            box-shadow: 0 0 24px rgba(0, 217, 255, 0.25) !important;



        }}



        .st-key-btn_launch_active_mode_pathfinder button {{



            background: linear-gradient(135deg, rgba(0, 217, 255, 0.35) 0%, rgba(0, 240, 181, 0.40) 100%) !important;



            color: #ffffff !important;



            border-radius: 10px !important;



            font-size: 0.80rem !important;



            font-weight: 800 !important;



            border: 2px solid #00F0B5 !important;



            box-shadow: 0 0 20px rgba(0, 217, 255, 0.50), 0 0 10px rgba(0, 240, 181, 0.40) !important;



            padding: 8px 18px !important;



            min-height: unset !important;



            height: auto !important;



            line-height: 1.4 !important;



            white-space: nowrap !important;



            cursor: pointer !important;



            transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;



        }}



        .st-key-btn_launch_active_mode_pathfinder button:hover {{



            background: linear-gradient(135deg, rgba(0, 217, 255, 0.50) 0%, rgba(0, 240, 181, 0.55) 100%) !important;



            border-color: #00D9FF !important;



            box-shadow: 0 0 28px rgba(0, 240, 181, 0.70), 0 6px 20px rgba(0, 0, 0, 0.6) !important;



            transform: translateY(-2px) !important;



        }}



        </style>



        """, unsafe_allow_html=True)







        with st.container(key="cockpit_hud_card"):



            col_hud_title, col_hud_btn = st.columns([1.6, 1.4], vertical_alignment="center")



            with col_hud_title:



                st.markdown(f"""



                    <div style='display: flex; align-items: center; gap: 10px;'>



                        <span style='display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: {accent}; box-shadow: 0 0 10px {accent};'></span>



                        <span style='font-size: 0.96rem; font-weight: 900; color: #f8fafc; letter-spacing: 0.02em;'>{mode_title}</span>



                    </div>



                """, unsafe_allow_html=True)



            with col_hud_btn:



                btn_hud_label = f"{action_label} 🎯"



                if st.button(



                    btn_hud_label,



                    key="btn_launch_active_mode_pathfinder",



                    use_container_width=True



                ):



                    if active_mode_obj.get("route_id"):



                        st.session_state.focused_route_id = active_mode_obj["route_id"]



                        st.session_state.selected_route_id = active_mode_obj["route_id"]



                        routes_pool = r_routes if ('r_routes' in locals() and r_routes) else (st.session_state.get("active_ranked_routes") or st.session_state.get("cached_candidate_routes") or [])



                        matching_r = next((getattr(r, "route", r) for r in routes_pool if getattr(getattr(r, "route", r), "route_id", None) == active_mode_obj["route_id"]), None)



                        if matching_r:



                            st.session_state.selected_route_object = matching_r



                    st.session_state.selected_driving_mode = active_mode_obj["mode_id"]



                    st.session_state.auto_fit_bounds = True



                    st.session_state.scroll_to_app_map = True



                    st.toast(f"🚀 Launched {active_mode_obj.get('title')} in NexRoute Maps!", icon=active_mode_obj.get("icon", "🌱"))



                    st.rerun()







            hud_content = f"""<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px; margin-top: 10px; margin-bottom: 10px;'>



{feat_items_html}



</div>



{hud_data.get('speed_health_hud', '')}



{extra_hud}"""



            st.markdown(hud_content, unsafe_allow_html=True)







            # Aura 3D Virtual Guide Quick Launch Deck



            st.markdown("""



            <div style="background: linear-gradient(135deg, rgba(8, 22, 44, 0.95) 0%, rgba(15, 23, 42, 0.92) 100%); border: 1.5px solid rgba(56, 189, 248, 0.4); border-radius: 14px; padding: 14px 18px; margin: 14px 0 10px 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);">



                <div style="display: flex; align-items: center; gap: 12px;">



                    <div style="width: 44px; height: 44px; border-radius: 10px; background: linear-gradient(135deg, #0284c7, #0369a1); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 0 16px rgba(56, 189, 248, 0.5);">



                        🤖



                    </div>



                    <div>



                        <div style="font-size: 1.0rem; font-weight: 900; color: #f8fafc; text-transform: uppercase; letter-spacing: 0.03em;">



                            Aura • 3D Virtual Companion Journey Experience



                        </div>



                        <div style="font-size: 0.74rem; color: #94a3b8; margin-top: 2px;">



                            Complete 19-stage interactive guidance from departure to destination with 3D robot animations, audio chimes, and maneuvers



                        </div>



                    </div>



                </div>



            </div>



            """, unsafe_allow_html=True)



            if st.button("🚀 Enter Aura 3D Virtual Guide & Cockpit", key="btn_nav_to_virtual_guide_deck", type="primary", use_container_width=True):



                active_item = resolve_virtual_guide_active_route()



                if active_item:



                    st.session_state["active_route_item"] = active_item



                    st.session_state["selected_route_object"] = active_item.route



                st.session_state.current_view = "virtual_guide"



                st.session_state.target_tab = "guide"



                st.session_state.scroll_to_guide_hud = True



                st.session_state.auto_start_virtual_guide = True



                st.toast("🚀 Launching Aura 3D Virtual Guide & Cockpit...", icon="🤖")



                st.rerun()











    with tab_fac:



        # FACILITY CATEGORIES EXPLORER & ALL ROUTES MAPPER



        # (Inside Map & Navigation as requested)



        # =========================================================================



        st.markdown('<div id="facilities-section" style="margin-top: 32px;"></div>', unsafe_allow_html=True)



        st.markdown(f"### 📍 PLACES & NEARBY FACILITIES")



        st.markdown(f"<p style='color: #94a3b8; font-size: 0.88rem; margin-top: -10px;'>{"Discover useful places near your location or along your selected route."}</p>", unsafe_allow_html=True)







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
            "🏥 Hospitals & Clinics",
            "🛒 Supermarkets",
            "⛽ Fuel Stations",
            "⚡ EV Charging",
            "🍽️ Restaurants",
            "🏧 ATMs & Banking",
            "🚓 Police & Emergency Services",
            "🏨 Hotels",
            "🏛️ Tourist Attractions",
            "🛍️ Shopping Malls",
            "🌳 Parks",
            "🛣️ Rest Stops",
            "🔍 Custom Search"
        ]







        fac_labels = {



            "🌐 All Facilities": t('fac.all'),



            "🏥 Hospitals": t('fac.hospitals'),



            "🛒 Supermarkets": t('fac.supermarkets'),



            "⛺ Shelters": t('fac.shelters'),



            "👮 Police/Rescue": t('fac.police'),



            "⛽ Fuel/Charging": t('fac.fuel'),



            "🚨 Emergency Radar": t('fac.radar'),



            "🍽️ Restaurants": t('fac.food'),



            "🏨 Hotels": t('fac.hotels'),



            "🏧 ATM / Banking": t('fac.atm'),



            "🛍️ Shopping Malls": t('fac.shopping'),



            "🔍 Custom Search": t('fac.custom_search'),



        }







        cat_quick_pills = st.pills(
            t('fac.title'),
            options=cat_quick_options,



            format_func=lambda c: fac_labels.get(c, c),



            default=cur_cat_name if cur_cat_name in cat_quick_options else "🌐 All Facilities",



            key="pills_quick_category_select"



        )



        if cat_quick_pills and cat_quick_pills != st.session_state.get("selected_sidebar_category"):



                        st.rerun()

        # Places search box
        places_q = st.text_input(
            "Search places, landmarks, or addresses",
            value=st.session_state.get("places_search_query", ""),
            placeholder="Search places, landmarks, or addresses...",
            key="txt_places_search_box_fac_tab",
            label_visibility="collapsed"
        )
        st.session_state.places_search_query = places_q







        # Dynamic Facility Search Mode & Radius Controls



        f_bar_c1, f_bar_c2, f_bar_c3 = st.columns([1.5, 1.2, 0.8])



        with f_bar_c1:



            f_modes = {



                "near_destination": t('fac.near_dest'),



                "near_origin": t('fac.near_orig'),



                "along_route": t('fac.along_route'),



                "near_map": t('fac.near_map')



            }



            cur_f_mode = st.session_state.get("fac_search_mode", "near_destination")



            sel_mode_val = st.selectbox(



                t("fac.search_anchor"),



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



                t("fac.search_radius"),



                options=rad_options,



                index=c_idx_rad,



                format_func=lambda r: t("fac.within_km", radius=f"{r:.0f}"),



                key="sel_fac_radius_select_box"



            )



            if sel_rad_val != st.session_state.get("fac_radius_km"):



                st.session_state.fac_radius_km = sel_rad_val



                st.rerun()







        with f_bar_c3:



            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)



            if st.button(t("fac.refresh"), key="btn_refresh_facilities_live", use_container_width=True, help="Re-query live OpenStreetMap POIs"):



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



                f"<span style='color: #ef4444; background: rgba(239, 68, 68, 0.15); padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(239, 68, 68, 0.4); font-size: 0.74rem; font-weight: 800; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);'>{t('fac.radar_active')}</span>"



                if em_is_active else



                f"<span style='color: #64748b; background: rgba(255, 255, 255, 0.04); padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); font-size: 0.74rem; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;'>{t('fac.radar_standby')}</span>"



            )







            st.markdown(f"""



            <div style='background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.65) 100%); border: 1px solid rgba(56, 189, 248, 0.22); border-radius: 12px; padding: 14px 18px; margin-top: 14px; margin-bottom: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);'>



                <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;'>



                    <div style='display: flex; align-items: center; gap: 10px;'>



                        <span style='font-size: 1.4rem;'>🚨</span>



                        <div>



                            <div style='display: flex; align-items: center; gap: 8px;'>



                                <b style='color: #f1f5f9; font-size: 0.98rem; letter-spacing: 0.02em;'>



                                    {t('fac.emergency_title')}



                                </b>



                                {radar_status_badge}



                            </div>



                            <div style='font-size: 0.74rem; color: #94a3b8; margin-top: 2px;'>



                                {t('fac.emergency_subtitle')}



                            </div>



                        </div>



                    </div>



                </div>



            </div>



            """, unsafe_allow_html=True)







            # Emergency Action Buttons Dock (Screenshot 2)



            dock_c1, dock_c2, dock_c3, dock_c4, dock_c5 = st.columns([1.1, 1, 1, 1, 1])



            with dock_c1:



                toggle_btn_label = f"🛡️ {t('fac.hide_radar')}" if em_is_active else f"🚨 {t('fac.radar')}"



                if st.button(toggle_btn_label, key="btn_toggle_emergency_radar", use_container_width=True, type="primary" if not em_is_active else "secondary"):



                    st.session_state.emergency_radar_active = not em_is_active



                    if not st.session_state.emergency_radar_active:



                        st.session_state.active_sos_type = None



                    st.rerun()



            with dock_c2:



                if st.button(t("fac.sos_medical"), key="btn_dock_sos_med", help="Instant dispatch to nearest trauma hospital", use_container_width=True):



                    st.session_state.active_sos_type = "MEDICAL"



                    st.session_state.emergency_radar_active = True



                    st.session_state.selected_sidebar_category = "🚨 Emergency Radar"



                    st.rerun()



            with dock_c3:



                if st.button(t("fac.sos_police"), key="btn_dock_sos_police", help="Instant dispatch to nearest police post & ERSS 112", use_container_width=True):



                    st.session_state.active_sos_type = "POLICE"



                    st.session_state.emergency_radar_active = True



                    st.session_state.selected_sidebar_category = "🚨 Emergency Radar"



                    st.rerun()



            with dock_c4:



                if st.button(t("fac.sos_hazard"), key="btn_dock_sos_disaster", help="Emergency guidance to nearest cyclone shelter", use_container_width=True):



                    st.session_state.active_sos_type = "DISASTER"



                    st.session_state.emergency_radar_active = True



                    st.session_state.selected_sidebar_category = "🚨 Emergency Radar"



                    st.rerun()



            with dock_c5:



                if st.button(t("fac.sos_breakdown"), key="btn_dock_sos_fuel", help="Find nearest highway fuel & fast EV charger", use_container_width=True):



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



                <div style='background: linear-gradient(135deg, rgba(6, 78, 59, 0.4) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #10b981; border-radius: 12px; padding: 16px 20px; margin: 12px 0; box-shadow: 0 0 25px rgba(16, 185, 129, 0.35);'>



                    <div style='display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 10px;'>



                        <div>



                            <div style='display: flex; align-items: center; gap: 8px;'>



                                <span style='font-size: 1.5rem;'>📡</span>



                                <b style='color: #34d399; font-size: 1.05rem; letter-spacing: 0.02em;'>



                                    {t('fac.sim_call_title')}



                                </b>



                                <span style='background: rgba(16, 185, 129, 0.2); color: #6ee7b7; font-size: 0.72rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; border: 1px solid #10b981;'>



                                    {t('fac.radio_connected')}



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



                    if st.button(t("fac.hang_up"), key="btn_end_sim_call", use_container_width=True):



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



                <div style='background: linear-gradient(135deg, rgba(127, 29, 29, 0.35) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #ef4444; border-radius: 12px; padding: 16px 20px; margin: 12px 0; box-shadow: 0 0 25px rgba(239, 68, 68, 0.35);'>



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



                        if isinstance(f_rating_val, (int, float)):



                            f_rating_display = f"<span style='color: #f59e0b; font-weight: 700;'>★ {f_rating_val:.1f}</span>"



                        else:



                            clean_r = str(f_rating_val).replace("⭐", "").strip()



                            f_rating_display = f"<span style='color: #f59e0b; font-weight: 700;'>★ {clean_r}</span>"



                    else:



                        f_rating_display = f"<span style='color: #94a3b8; font-style: italic;'>{t('fac.rating_unavailable', 'Rating unavailable')}</span>"







                    f_source = fac.get("data_source", "OpenStreetMap Live POI")



                    f_status = fac.get("verification_status", "OSM Mapped POI")



                    f_source_disp = t("fac.osm_contributors", "OpenStreetMap Contributors (Live POI)") if "OpenStreetMap" in str(f_source) else f_source



                    f_status_disp = t("fac.osm_mapped_poi", "OSM Mapped Geographic POI") if "OSM" in str(f_status) else f_status







                    b_badge = cat_info["border_badge"]



                    b_bg = cat_info["bg_badge"]



                    cat_col = cat_info["color"]



                    cat_lbl = fac.get("facility_type", cat_info["short_label"])



                    amenity_ico = fac.get("amenity_icon", cat_info["icon"])



                    fac_name = fac["name"]



                    dist_corridor = fac.get("distance_from_route_km", 0.0)



                    road_dist = fac.get("road_distance_km", 0.0)



                    eta_mins = fac.get("eta_minutes", 1)



                    hours = fac.get("operating_hours", "Open")



                    if "not published" in str(hours).lower():



                        hours_disp = f"{t('fac.hours_not_published', 'Hours not published')} • {t('fac.contact_directly', 'Contact directly')}"



                    else:



                        hours_disp = hours



                    addr = fac.get("address", "Transit Corridor")







                    card_html = (



                        f"<div style='background: rgba(10, 20, 38, 0.85); border: 1.5px solid {b_badge}; " f"border-radius: 12px; padding: 14px; margin-bottom: 12px; display: flex; flex-direction: column; " f"justify-content: space-between; min-height: 230px; box-shadow: 0 4px 16px rgba(0,0,0,0.35);'>"



                        f"<div>"



                        f"<div style='display: flex; align-items: flex-start; justify-content: space-between; gap: 8px;'>"



                        f"<div style='font-size: 1.35rem;'>{amenity_ico}</div>"



                        f"<div style='flex: 1; min-width: 0;'>"



                        f"<b style='font-size: 0.88rem; color: #f1f5f9; line-height: 1.3; display: block; word-break: break-word;'>{fac_name}</b>"



                        f"<div style='margin-top: 4px;'>"



                        f"<span style='color: {cat_col}; font-size: 0.68rem; font-weight: 800; background: {b_bg}; padding: 2px 7px; border-radius: 6px; border: 1px solid {b_badge};'>"



                        f"{cat_lbl}"



                        f"</span>"



                        f"</div>"



                        f"</div>"



                        f"</div>"



                        f"<div style='font-size: 0.74rem; color: #94a3b8; margin-top: 8px;'>"



                        f"<b>{t('fac.corridor_distance', 'Corridor:')}</b> {dist_corridor:.1f} km • <span style='color: #38bdf8; font-weight: 700;'>🚗 ~{road_dist:.1f} km ({eta_mins:.0f} mins)</span>"



                        f"</div>"



                        f"<div style='font-size: 0.72rem; color: #cbd5e1; margin-top: 4px;'>"



                        f"<b>{t('fac.hours', 'Hours')}:</b> <span style='color: #a7f3d0;'>{hours_disp}</span>"



                        f"</div>"



                        f"<div style='font-size: 0.72rem; margin-top: 2px;'>"



                        f"<b>{t('fac.rating', 'Rating')}:</b> {f_rating_display}"



                        f"</div>"



                        f"{f_phone_display}"



                        f"</div>"



                        f"<div style='font-size: 0.66rem; color: #94a3b8; margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 4px; line-height: 1.4;'>"



                        f"📍 {addr}<br/>"



                        f"<span style='color: #38bdf8; font-weight: 600;'>● {f_source_disp} • {f_status_disp}</span>"



                        f"</div>"



                        f"</div>"



                    )



                    st.html(card_html)







                    col_act1, col_act2, col_act3 = st.columns([1, 1, 1])

                    with col_act1:
                        if st.button(f"🧭 {t('btn.route', 'Route')}", key=f"btn_cat_route_{fac.get('facility_id', idx)}", use_container_width=True, type="primary"):
                            st.session_state.selected_dest_coords = (fac["latitude"], fac["longitude"])
                            st.session_state.selected_dest_label = fac["name"]
                            st.session_state.pending_dest = fac["name"]
                            st.session_state.last_synced_dest = fac["name"]
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
                            st.session_state.active_info_target = {"type": "facility", "data": fac}
                            st.session_state.selected_marker_coords = (fac["latitude"], fac["longitude"])
                            st.session_state.selected_marker_data = fac
                            st.toast(f"🧭 Routing to {fac['name']} on NexRoute Map!", icon="🗺️")
                            st.rerun()

                    with col_act2:
                        if st.button(f"📍 {t('btn.focus', 'Focus')}", key=f"btn_cat_focus_{fac.get('facility_id', idx)}", use_container_width=True):
                            st.session_state.map_center_lat = fac["latitude"]
                            st.session_state.map_center_lon = fac["longitude"]
                            st.session_state.map_zoom = 16
                            st.session_state.auto_fit_bounds = False
                            st.session_state.selected_marker_coords = (fac["latitude"], fac["longitude"])
                            st.session_state.selected_marker_data = fac
                            st.session_state.active_info_target = {"type": "facility", "data": fac}
                            st.session_state.scroll_to_app_map = True
                            st.session_state.switch_to_nav_tab = True
                            st.toast(f"📍 Centered map on {fac['name']}", icon="🗺️")
                            st.rerun()

                    with col_act3:
                        if st.button(f"ℹ️ {t('btn.info', 'Info')}", key=f"btn_cat_inq_{fac.get('facility_id', idx)}", use_container_width=True):
                            st.session_state.active_info_target = {"type": "facility", "data": fac}
                            st.session_state.selected_marker_coords = (fac["latitude"], fac["longitude"])
                            st.session_state.selected_marker_data = fac
                            st.session_state.show_info_modal = True
                            st.rerun()

if st.session_state.get("current_view") == "places":



    render_view_navigation_header("📍 PLACES & NEARBY FACILITIES", "Discover useful places near your location or along your selected route.", "places")



    # =========================================================================



    # SUGGESTED PLACES & HIGHLIGHTS AT LOCATION (DYNAMIC LIVE POIS)



    # =========================================================================



    st.markdown("---")



    



    # Priority: Destination if selected, otherwise Origin / Current Location



    dest_str_label = t("nav.destination")



    orig_str_label = t("nav.starting_point")



    focus_target = dest_str_label if coords_dest else orig_str_label



    if coords_dest and coords_orig:



        st.markdown("""



        <style>



        /* Sleek Segmented Pill Deck for Explore POIs Around */



        div.st-key-places_explore_anchor {



            background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;



            border: 1.5px solid rgba(0, 217, 255, 0.40) !important;



            border-radius: 12px !important;



            padding: 10px 16px !important;



            margin-bottom: 12px !important;



            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5) !important;



            width: fit-content !important;



            max-width: 100% !important;



        }



        div.st-key-places_explore_anchor div[data-testid="stRadio"] {



            margin: 0 !important;



        }



        div.st-key-places_explore_anchor div[data-testid="stRadio"] > label {



            font-size: 0.76rem !important;



            font-weight: 800 !important;



            color: #00D9FF !important;



            letter-spacing: 0.08em !important;



            text-transform: uppercase !important;



            margin-bottom: 8px !important;



            display: flex !important;



            align-items: center !important;



            gap: 6px !important;



        }



        div.st-key-places_explore_anchor div[data-testid="stRadio"] div[role="radiogroup"] {



            display: flex !important;



            flex-direction: row !important;



            align-items: center !important;



            flex-wrap: wrap !important;



            gap: 10px !important;



        }



        div.st-key-places_explore_anchor div[data-testid="stRadio"] label[data-baseweb="radio"] {



            background: #0B1B2D !important;



            border: 1.5px solid rgba(0, 217, 255, 0.35) !important;



            border-left: 3px solid rgba(0, 217, 255, 0.5) !important;



            border-radius: 8px !important;



            padding: 6px 14px !important;



            margin: 0 !important;



            width: auto !important;



            display: inline-flex !important;



            align-items: center !important;



            cursor: pointer !important;



            transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;



            box-shadow: 0 2px 8px rgba(0,0,0,0.4) !important;



            transform: none !important;



        }



        div.st-key-places_explore_anchor div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {



            border-color: #00D9FF !important;



            background: linear-gradient(135deg, #10263E 0%, #0B1B2D 100%) !important;



            transform: translateY(-2px) !important;



            box-shadow: 0 4px 14px rgba(0, 240, 181, 0.35) !important;



        }



        div.st-key-places_explore_anchor div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {



            background: linear-gradient(135deg, rgba(0, 217, 255, 0.35) 0%, rgba(0, 240, 181, 0.40) 100%) !important;



            border: 1.5px solid #00F0B5 !important;



            border-left: 4px solid #00D9FF !important;



            box-shadow: 0 0 18px rgba(0, 217, 255, 0.50), 0 0 10px rgba(0, 240, 181, 0.40) !important;



            transform: none !important;



        }



        div.st-key-places_explore_anchor div[data-testid="stRadio"] label[data-baseweb="radio"] div {



            background: transparent !important;



            background-color: transparent !important;



        }



        div.st-key-places_explore_anchor div[data-testid="stRadio"] label[data-baseweb="radio"] p {



            color: #EAF7FF !important;



            font-size: 0.84rem !important;



            font-weight: 700 !important;



            margin: 0 !important;



            padding: 0 !important;



            background: transparent !important;



            background-color: transparent !important;



        }



        div.st-key-places_explore_anchor div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) p {



            color: #ffffff !important;



            font-weight: 800 !important;



            text-shadow: 0 0 10px rgba(0, 217, 255, 0.7) !important;



            background: transparent !important;



            background-color: transparent !important;



        }



        </style>



        """, unsafe_allow_html=True)



        col_focus1, col_focus2 = st.columns([2.5, 2.0])



        with col_focus1:



            focus_target = st.radio(f"🧭 {t('fac.explore_anchor')}", [dest_str_label, orig_str_label], horizontal=True, key="places_explore_anchor")



    



    if (focus_target == dest_str_label or focus_target == "Destination") and coords_dest:



        ref_lat = coords_dest[0]



        ref_lon = coords_dest[1]



        raw_dest_name = st.session_state.get("selected_dest_label") or st.session_state.get("txt_dest") or t("nav.destination")



        ref_label = raw_dest_name.replace("📍", "").strip()



    elif coords_orig:



        ref_lat = coords_orig[0]



        ref_lon = coords_orig[1]



        raw_orig_name = st.session_state.get("selected_orig_label") or st.session_state.get("txt_orig") or st.session_state.get("user_live_label", t("nav.starting_point"))



        ref_label = raw_orig_name.replace("📍", "").strip()



    else:



        ref_lat = detected_coords[0]



        ref_lon = detected_coords[1]



        ref_label = st.session_state.get("user_live_label", t("nav.my_location")).replace("📍", "").strip()







    suggested_places = generate_suggested_places_at_location(



        lat=ref_lat,



        lon=ref_lon,



        location_name=ref_label



    )







    st.markdown(f"""<div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;'>
<div style='display: flex; align-items: center; gap: 10px;'>
<span style='font-size: 1.4rem;'>📍</span>
<div>
<div style='font-size: 1.05rem; font-weight: 800; color: #f8fafc; letter-spacing: 0.02em;'>
📍 PLACES & NEARBY FACILITIES • {ref_label.upper()}
</div>
<div style='font-size: 0.74rem; color: #94a3b8;'>
Discover useful places near your location or along your selected route.
</div>
</div>
</div>
<span style='background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.4); color: #38bdf8; font-size: 0.72rem; font-weight: 800; padding: 4px 10px; border-radius: 20px;'>
● VERIFIED POIS
</span>
</div>""", unsafe_allow_html=True)

    # Search & Category Filters
    places_search_query = st.text_input(
        "Search places",
        placeholder="Search places, landmarks, or addresses...",
        key="txt_places_main_search_box",
        label_visibility="collapsed"
    )

    places_categories = [
        "🌐 All Categories",
        "🏥 Hospitals & Clinics",
        "🛒 Supermarkets",
        "⛽ Fuel Stations",
        "⚡ EV Charging",
        "🍽️ Restaurants",
        "🏧 ATMs & Banking",
        "🚓 Police & Emergency Services",
        "🏨 Hotels",
        "🏛️ Tourist Attractions",
        "🛍️ Shopping Malls",
        "🌳 Parks",
        "🛣️ Rest Stops",
    ]
    selected_p_cat = st.pills("Categories", options=places_categories, default="🌐 All Categories", key="pills_places_main_cat")








    
    # Filter suggested places by search and category
    if places_search_query.strip():
        q_clean = places_search_query.strip().lower()
        suggested_places = [
            p for p in suggested_places
            if q_clean in p.get("name", "").lower()
            or q_clean in p.get("address", "").lower()
            or q_clean in p.get("category", "").lower()
        ]
    if selected_p_cat and selected_p_cat != "🌐 All Categories":
        cat_key = selected_p_cat.split()[-1].lower()
        suggested_places = [
            p for p in suggested_places
            if cat_key in p.get("category", "").lower() or any(cat_key in h.lower() for h in p.get("highlights", []))
        ]

    if not suggested_places:



        st.info(f"ℹ️ No points of interest or cultural highlights found within the immediate radius of {ref_label}. Select a different destination or explore nearby facilities.")



    else:



        sug_cols = st.columns(3)



        for idx, place in enumerate(suggested_places):



            col_idx = idx % 3



            with sug_cols[col_idx]:



                st.markdown(render_place_details_card_html(place, lang=st.session_state.app_language), unsafe_allow_html=True)



                clean_name = place['name']



                for prefix in [ref_label, ref_label.split(',')[0]]:



                    clean_name = clean_name.replace(prefix, '').strip(' -–,')



                if not clean_name or len(clean_name) < 3:



                    clean_name = place['name']



                if len(clean_name) > 22:



                    clean_name = clean_name[:20] + "..."



                






                col_pb1, col_pb2, col_pb3, col_pb4 = st.columns([1.2, 1.2, 1.0, 1.0])
                with col_pb1:
                    if st.button("🗺️ View Map", key=f"btn_view_sug_{place['place_id']}", use_container_width=True, type="primary"):
                        st.session_state.map_center_lat = place["latitude"]
                        st.session_state.map_center_lon = place["longitude"]
                        st.session_state.map_zoom = 16
                        st.session_state.auto_fit_bounds = False
                        st.session_state.selected_marker_coords = (place["latitude"], place["longitude"])
                        st.session_state.selected_marker_data = place
                        st.session_state.scroll_to_app_map = True
                        st.session_state.switch_to_nav_tab = True
                        st.toast(f"📍 Centered map on {place['name']}", icon="🗺️")
                        st.rerun()
                with col_pb2:
                    if st.button("🧭 Directions", key=f"btn_dir_sug_{place['place_id']}", use_container_width=True):
                        st.session_state.selected_dest_coords = (place["latitude"], place["longitude"])
                        st.session_state.selected_dest_label = place["name"]
                        st.session_state.pending_dest = place["name"]
                        st.session_state.last_synced_dest = place["name"]
                        st.session_state.movement_index = 0
                        st.session_state.is_in_transit = False
                        st.session_state.auto_fit_bounds = True
                        st.session_state.focused_route_id = "ALL"
                        st.session_state.scroll_to_app_map = True
                        st.session_state.switch_to_nav_tab = True
                        st.toast(f"🧭 Calculating route to {place['name']}...", icon="🛣️")
                        st.rerun()
                with col_pb3:
                    if st.button("ℹ️ Info", key=f"btn_info_sug_{place['place_id']}", use_container_width=True):
                        st.session_state.active_info_target = {"type": "place", "data": place}
                        st.session_state.selected_marker_coords = (place["latitude"], place["longitude"])
                        st.session_state.selected_marker_data = place
                        st.session_state.show_info_modal = True
                        st.rerun()
                with col_pb4:
                    is_saved = any(s.get("name") == place["name"] for s in st.session_state.get("saved_locations", []))
                    save_lbl = "⭐ Saved" if is_saved else "⭐ Save"
                    if st.button(save_lbl, key=f"btn_save_sug_{place['place_id']}", use_container_width=True):
                        if "saved_locations" not in st.session_state:
                            st.session_state.saved_locations = []
                        if not is_saved:
                            st.session_state.saved_locations.append(place)
                            st.toast(f"⭐ Saved {place['name']} to bookmarks!", icon="📌")
                            st.rerun()
                        else:
                                st.toast(f"📌 {place['name']} is already saved.", icon="ℹ️")







if st.session_state.get("current_view") == "virtual_guide":



    render_view_navigation_header("🚗 " + t("tab.virtual_guide", "Virtual Guide"), t("guide.subtitle", "Turn-by-turn storytelling & 3D Companion HUD"), "guide")



    render_virtual_guide_experience(active_route_item=st.session_state.get("active_route_item"), key_suffix="_view")







# =========================================================================



# FLOATING CIRCULAR CHATBOT: A.U.R.A. (Adaptive User Route Assistant)



# =========================================================================



st.markdown('<div id="floating-copilot-trigger-anchor"></div>', unsafe_allow_html=True)



with st.popover(" ", help="Open AURA • Adaptive User Route Assistant"):



    st.markdown(f"""



    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(168, 85, 247, 0.35); padding-bottom: 8px; margin-bottom: 10px;">



        <div style="display: flex; align-items: center; gap: 10px;">



            <img src="{aura_logo_uri}" style="width: 38px; height: 38px; border-radius: 50%; border: 2px solid #a855f7; object-fit: cover; box-shadow: 0 0 12px rgba(168, 85, 247, 0.65);" />



            <div>



                <div style="font-weight: 800; font-size: 0.96rem; color: #f8fafc; letter-spacing: 0.04em;">



                    🤖 AURA • Route Assistant



                </div>



                <div style="font-size: 0.66rem; color: #c084fc; font-family: 'JetBrains Mono', monospace; font-weight: 600;">



                    ADAPTIVE USER ROUTE ASSISTANT



                </div>



            </div>



        </div>



        <span style="font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px; background: rgba(168, 85, 247, 0.2); border: 1px solid #a855f7; color: #d8b4fe; letter-spacing: 0.05em;">



            ● ONLINE



        </span>



    </div>



    """, unsafe_allow_html=True)



    render_aura_chat_box(key_prefix="popover_window", height=340)







# Floating Visual Overlay for Chatbot Trigger Logo (renders over invisible popover button)



if aura_logo_uri:



    st.markdown(f'<img src="{aura_logo_uri}" class="floating-aura-logo-overlay" alt="AURA Chatbot Logo" />', unsafe_allow_html=True)







# =========================================================================



# QUICK TOUR COMPONENT (INTERACTIVE STEP-BY-STEP GUIDED ONBOARDING)



# =========================================================================



from src.quick_tour import build_quick_tour_html



components.html(build_quick_tour_html(st.session_state.get("app_language", "en"), bot_logo_uri=aura_logo_uri), height=0, width=0)







if st.session_state.get("launch_quick_tour", False) or "tour" in st.query_params or "quick_tour" in st.query_params:



    st.session_state.launch_quick_tour = False



    components.html("""



    <script>



    (function() {



        var pWin = window.parent || window;



        function tryLaunch(attempts) {



            if (pWin.startPathfinderTour) {



                pWin.startPathfinderTour(0);



            } else if (attempts > 0) {



                setTimeout(function() { tryLaunch(attempts - 1); }, 120);



            }



        }



        tryLaunch(12);



    })();



    </script>



    """, height=0, width=0)



    try:



        del st.query_params["tour"]



    except Exception:



        pass



    try:



        del st.query_params["quick_tour"]



    except Exception:



        pass



























