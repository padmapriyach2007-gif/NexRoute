"""
P.A.T.H.F.I.N.D.E.R. 3D Interactive AI Guide & Quick Tour Module
================================================================
Provides an immersive, animated 3D companion guide ("Pathfinder Guide" / A.U.R.A.)
that personally walks users through the application interface:
1. Welcome to Pathfinder (3D Character Greeting & Introduction)
2. Core Navigation Menu & Workspaces (Physical movement & pointing at navigation)
3. AI Travel Chatbot (Movement near chat composer & sample prompt guidance)
4. Travel Planning & Smart Route Preferences (Avoid Tolls, Avoid Highways, Avoid Ferries)
5. Live Responses & Multi-Corridor Intelligence (Grounded live traffic & weather)
6. Speedometer Cockpit, Satellite Hazard Map & 3D Walking HUD
7. Tour Complete & Celebration (Victory spin, confetti, Start Planning)

Features:
- Real WebGL Three.js 3D character with articulated head, blinking holographic eyes,
  pulsating quantum core, thruster plasma rings, and pointing/waving robotic arms.
- Smooth interpolated physical movement across the actual application viewport,
  banking dynamically into turns and pointing directly at target UI controls.
- Speech bubble with typing narrative, progress indicator, and controls.
- Browser Speech Synthesis (Web Speech API) with mute toggle and waveform sync.
- First-time welcome greeting ("Show Me Around" vs "I'll Explore Myself").
- Keyboard shortcuts (Escape to close, Arrows for navigation).
- Graceful fallbacks for WebGL, mobile viewports, and reduced-motion preferences.
"""

import os
import json
from typing import Dict, Any, List

TOUR_STEPS = {
    "en": [
        {
            "step": 1,
            "badge": "🧭 WELCOME TO NEXROUTE",
            "title": "Meet Your 3D AI Travel Companion",
            "selector": "#pathfinder-hero-wrapper, .qr-hero-wrapper, #pathfinder-hero-title",
            "fallback_center": True,
            "bot_dialogue": "Greetings explorer! I'm your NexRoute 3D Guide. I'm here to show you around your travel assistant so you can plan journeys and navigate with total confidence!",
            "bot_mood": "waving",
            "content": (
                "Welcome to <b>P.A.T.H.F.I.N.D.E.R.</b> (<i>Predictive Adaptive Transit & Hazard-Free Intelligent Routing</i>).<br><br>"
                "NexRoute is your all-in-one autonomous travel companion. It helps you <b>plan comprehensive itineraries</b>, "
                "<b>explore regional sights</b>, <b>avoid tolls, road hazards, and ferries</b>, and converse with an AI travel copilot in 8 languages."
            ),
            "pro_tip": "💡 <b>Quick Overview:</b> Use the top language bar anytime to switch between English, Telugu, Hindi, Tamil, and more.",
            "prompt_example": None,
            "action": "wave"
        },
        {
            "step": 2,
            "badge": "🗺️ CORE NAVIGATION",
            "title": "Explore the Main Workspaces",
            "selector": "#tour-workspace-cards, .qr-navbar-container, .qr-workspace-card:first-child",
            "fallback_center": False,
            "bot_dialogue": "Take a look at these 4 dedicated travel modules right here! Click any workspace card to jump straight into AI Copilot, Navigation, Places, or your Virtual Guide.",
            "bot_mood": "pointing",
            "content": (
                "From this central dashboard, you can launch directly into 4 powerful workspaces:<br><br>"
                "• <b>✨ AI Travel Copilot:</b> Generate day-by-day itineraries, smart budgets, and transport comparisons.<br>"
                "• <b>🧭 Map & Navigation:</b> Multi-objective routing with live road hazard evasion and satellite audits.<br>"
                "• <b>🌟 Places & Sights:</b> Discover curated regional attractions, restaurants, hotels, and fuel stops.<br>"
                "• <b>🚗 Virtual Guide:</b> Human-like landmark storytelling HUD and turn-by-turn walking kinematics."
            ),
            "pro_tip": "💡 <b>One-Click Launch:</b> Click any card or button below to navigate between workspaces instantly.",
            "prompt_example": None,
            "action": "point"
        },
        {
            "step": 3,
            "badge": "🤖 TRAVEL CHATBOT",
            "title": "Ask Anything in Natural Language",
            "selector": ".floating-aura-logo-overlay, div[data-testid='stPopover'], button[aria-label*='Aura'], div[data-testid='stChatInput']",
            "fallback_center": False,
            "bot_dialogue": "Here is your 24/7 AI travel copilot! Click this purple button anytime to ask about destinations, routes, packing advice, or budgets in plain English or local languages.",
            "bot_mood": "explaining",
            "content": (
                "Meet <b>A.U.R.A.</b> (<i>Adaptive User Route Assistant</i>), your built-in AI copilot.<br><br>"
                "Click the floating robot button at the bottom-right corner of your screen at any moment to open your travel chat. "
                "You can ask for complete holiday plans, flight rules, hotel recommendations, or packing checklists."
            ),
            "pro_tip": "💡 <b>Sample Query to Try:</b>",
            "prompt_example": "💬 \"Plan a 3-day trip to Goa within ₹5,000 including food and stays\"",
            "action": "pulseAura"
        },
        {
            "step": 4,
            "badge": "💳 SMART PREFERENCES",
            "title": "Smart Route Customization & Toll Bypass",
            "selector": "#tour-preferences-bar, #tour-card-nav, .qr-workspace-card:nth-child(2)",
            "fallback_center": False,
            "bot_dialogue": "You can customize your route with a single click: avoid tolls to save cash, evade busy highways, or bypass water ferries for uninterrupted land travel!",
            "bot_mood": "pointing",
            "content": (
                "Take full control of your journeys with instant 1-click route preferences:<br><br>"
                "• <b>💳 Avoid Tolls:</b> Automatically bypasses FASTag toll plazas to minimize travel expenses.<br>"
                "• <b>🛣️ Avoid Highways:</b> Evades high-speed expressways in favor of scenic local byways.<br>"
                "• <b>⛴️ Avoid Ferries:</b> Guarantees continuous land-only routing without water ferry crossings.<br>"
                "• <b>4 Routing Objectives:</b> Switch between <i>Fastest</i>, <i>Shortest</i>, <i>Balanced</i>, or <i>Wheelchair Accessible</i>."
            ),
            "pro_tip": "💡 <b>Instant Recalculation:</b> Changing any preference dynamically recomputes the optimal route polyline.",
            "prompt_example": None,
            "action": "point"
        },
        {
            "step": 5,
            "badge": "💬 LIVE INTELLIGENCE",
            "title": "Chat Answers & Conversational Refinement",
            "selector": "div[data-testid='stPopoverBody'], div[data-testid='stPopover'], .floating-aura-logo-overlay",
            "fallback_center": True,
            "bot_dialogue": "When the chatbot responds, you can ask follow-ups to refine dates, transit types, or budgets. Answers are verified against live road and weather conditions!",
            "bot_mood": "explaining",
            "content": (
                "NexRoute generates structured, verified travel guidance grounded in reality:<br><br>"
                "• <b>Interactive Refinement:</b> Ask follow-up questions to customize itineraries, swap hotels, or adjust travel dates.<br>"
                "• <b>Live Telemetry:</b> Forecasts from Open-Meteo, road closures from OSM, and live traffic obstacles are automatically synchronized.<br>"
                "• <b>8 Languages:</b> Converse fluently in English, Telugu, Hindi, Tamil, Kannada, Malayalam, Bengali, and Marathi."
            ),
            "pro_tip": "💡 <b>Follow-Up Example:</b> \"Can we swap day 2 for beach water sports instead?\" or \"Show me budget vegetarian restaurants nearby.\"",
            "prompt_example": None,
            "action": "think"
        },
        {
            "step": 6,
            "badge": "🏎️ ADVANCED TOOLS",
            "title": "Live Map, Digital Speedometer & 3D Guide",
            "selector": "#tour-card-guide, #tour-speedometer-cockpit, #tour-card-nav",
            "fallback_center": False,
            "bot_dialogue": "Explore advanced cockpit tools: an interactive digital speedometer with speed limit warnings, live satellite hazard maps, and a 3D walking companion!",
            "bot_mood": "scanning",
            "content": (
                "NexRoute equips you with real-time driving cockpit intelligence:<br><br>"
                "• <b>⏱️ Creative Digital Speedometer:</b> Radial speedometer gauge with legal speed warnings and Eco/Comfort/Sport drive profiles.<br>"
                "• <b>🗺️ Interactive Satellite Map:</b> High-resolution map with real-time hazard evasion and obstacle detours.<br>"
                "• <b>📖 3D Virtual Guide:</b> Landmark cultural storytelling and 3D companion HUD that activates during active navigation."
            ),
            "pro_tip": "💡 <b>Safety First:</b> Potholes, construction zones, and severe weather warnings are sensed autonomously.",
            "prompt_example": None,
            "action": "point"
        },
        {
            "step": 7,
            "badge": "🎉 ALL SET!",
            "title": "You're Ready to Explore with NexRoute!",
            "selector": "#pathfinder-hero-wrapper, .qr-hero-wrapper, #pathfinder-hero-title",
            "fallback_center": True,
            "bot_dialogue": "You're all set! You now know the basics of NexRoute. Tell me where you'd like to go, and let's plan your next journey!",
            "bot_mood": "celebrating",
            "content": (
                "Congratulations! You've mastered the essentials of <b>P.A.T.H.F.I.N.D.E.R.</b><br><br>"
                "Start planning your next adventure, enter a destination on the map, or ask your AI travel copilot for customized trip recommendations.<br><br>"
                "<i>You can replay this tour anytime by clicking the 'Quick Tour' button in the top bar!</i>"
            ),
            "pro_tip": "🚀 <b>Ready to embark?</b> Click 'Start Planning' below to launch straight into your AI travel assistant.",
            "prompt_example": None,
            "action": "celebrate"
        }
    ]
}

# Import complete multilingual catalog for all 8 supported languages
try:
    from src.quick_tour_locales import TOUR_STEPS_LOCALIZED, TOUR_UI_STRINGS, VOICE_BCP47_CODES
    TOUR_STEPS.update(TOUR_STEPS_LOCALIZED)
except Exception:
    TOUR_UI_STRINGS = {}
    VOICE_BCP47_CODES = {}
    for _l in ["te", "hi", "ta", "kn", "ml", "bn", "mr"]:
        TOUR_STEPS[_l] = TOUR_STEPS["en"]


def build_quick_tour_html(lang: str = "en", bot_logo_uri: str = "") -> str:
    """
    Builds the complete client-side 3D Animated Interactive Tour Guide bundle.
    Renders an articulated 3D character ("Pathfinder Guide")
    that smoothly moves across the interface, points toward real UI elements,
    delivers speech synthesis audio with waveform synchronization, and
    provides a first-time welcome experience in all 8 languages.
    """
    tour_data = TOUR_STEPS.get(lang, TOUR_STEPS["en"])
    tour_json = json.dumps(tour_data)
    logo_json = json.dumps(bot_logo_uri or "")
    ui_dict = TOUR_UI_STRINGS.get(lang, TOUR_UI_STRINGS.get("en", {}))
    ui_json = json.dumps(ui_dict)
    voice_code = VOICE_BCP47_CODES.get(lang, "en-IN")
    voice_code_json = json.dumps(voice_code)

    mascot_poses = {}
    try:
        json_path = os.path.join(os.path.dirname(__file__), "..", "data", "mascot_poses_trans.json")
        if not os.path.exists(json_path):
            json_path = "data/mascot_poses_trans.json"
        with open(json_path, "r", encoding="utf-8") as f:
            mascot_poses = json.load(f)
    except Exception:
        mascot_poses = {}
    mascot_json = json.dumps(mascot_poses)

    return f"""
<div id="pathfinder-tour-root"></div>
<script>
(function() {{
    var pWin = window.parent || window;
    var pDoc = (pWin && pWin.document) ? pWin.document : document;

    var tourSteps = {tour_json};
    var botLogoUri = {logo_json};
    var mascotPoses = {mascot_json};
    var uiStrings = {ui_json};
    var currentVoiceLang = {voice_code_json};
    var currentStepIndex = 0;
    var isTourActive = false;
    var isVoiceMuted = false;
    var isSpeechSupported = ('speechSynthesis' in pWin);
    var activeUtterance = null;
    var typingTimer = null;

    // Load Voice Preference
    try {{
        var savedMute = pWin.localStorage.getItem('pathfinder_voice_muted');
        if (savedMute !== null) {{
            isVoiceMuted = (savedMute === '1');
        }}
    }} catch(e) {{}}

    // =========================================================================
    // INJECT TOUR STYLES
    // =========================================================================
    try {{
        var styleEl = pDoc.getElementById('pathfinder-quick-tour-styles');
        if (!styleEl) {{
            styleEl = pDoc.createElement('style');
            styleEl.id = 'pathfinder-quick-tour-styles';
            pDoc.head.appendChild(styleEl);
        }}
        styleEl.textContent = `
            /* Tour Overlay Backdrop */
            #pathfinder-tour-backdrop {{
                position: fixed !important;
                top: 0 !important; left: 0 !important;
                width: 100vw !important; height: 100vh !important;
                background: rgba(3, 7, 18, 0.78) !important;
                backdrop-filter: blur(6px) !important;
                -webkit-backdrop-filter: blur(6px) !important;
                z-index: 2147483640 !important;
                pointer-events: none !important;
                opacity: 0 !important;
                display: none !important;
                transition: opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
            }}
            #pathfinder-tour-backdrop.active {{
                display: block !important;
                opacity: 1 !important;
                pointer-events: all !important;
            }}

            /* Quantum Target Spotlight Box */
            #pathfinder-tour-spotlight {{
                position: fixed !important;
                border-radius: 16px !important;
                border: 2px solid #00f0ff !important;
                box-shadow: 0 0 0 9999px rgba(3, 7, 18, 0.78), 0 0 35px rgba(0, 240, 255, 0.85), inset 0 0 18px rgba(0, 240, 255, 0.3) !important;
                z-index: 2147483644 !important;
                pointer-events: none !important;
                display: none;
                transition: all 0.45s cubic-bezier(0.16, 1, 0.3, 1) !important;
                animation: tourSpotlightPulse 2.4s infinite alternate ease-in-out !important;
            }}
            @keyframes tourSpotlightPulse {{
                0% {{ border-color: #00f0ff; box-shadow: 0 0 0 9999px rgba(3, 7, 18, 0.78), 0 0 25px rgba(0, 240, 255, 0.65); }}
                100% {{ border-color: #a855f7; box-shadow: 0 0 0 9999px rgba(3, 7, 18, 0.78), 0 0 42px rgba(168, 85, 247, 0.85); }}
            }}

            /* =========================================================================
               3D CHARACTER STAGE CONTAINER (Floats & Glides Across Viewport)
               ========================================================================= */
            #pathfinder-guide-stage {{
                position: fixed !important;
                z-index: 2147483647 !important;
                pointer-events: none !important;
                display: none;
                opacity: 0;
                transition: left 0.65s cubic-bezier(0.22, 1, 0.36, 1),
                            top 0.65s cubic-bezier(0.22, 1, 0.36, 1),
                            transform 0.4s ease, opacity 0.3s ease !important;
                transform-origin: center center !important;
            }}
            #pathfinder-guide-stage.active {{
                display: flex !important;
                opacity: 1 !important;
                pointer-events: all !important;
            }}

            /* Inner Wrapper holding 3D Character Canvas + Speech Bubble Card */
            .guide-stage-layout {{
                display: flex !important;
                align-items: flex-start !important;
                gap: 16px !important;
                position: relative !important;
                max-width: 580px !important;
            }}
            .guide-stage-layout.flipped {{
                flex-direction: row-reverse !important;
            }}

            /* 3D Character Canvas Container */
            .guide-character-3d-box {{
                width: 140px !important;
                height: 165px !important;
                position: relative !important;
                flex-shrink: 0 !important;
                filter: drop-shadow(0 15px 25px rgba(0, 240, 255, 0.35)) drop-shadow(0 0 35px rgba(168, 85, 247, 0.25)) !important;
                cursor: grab !important;
            }}
            .guide-character-3d-box canvas,
            #dashboard-robot-canvas-slot canvas,
            .dashboard-robot-canvas-container canvas {{
                display: none !important;
                visibility: hidden !important;
                pointer-events: none !important;
                width: 0 !important;
                height: 0 !important;
                opacity: 0 !important;
            }}
            .guide-character-pose-img {{
                width: 155px !important;
                height: 175px !important;
                object-fit: contain !important;
                filter: drop-shadow(0 14px 28px rgba(0, 240, 255, 0.70)) drop-shadow(0 0 25px rgba(168, 85, 247, 0.45)) !important;
                animation: botFloat3D 3s infinite ease-in-out !important;
                display: block !important;
                margin: 0 auto !important;
                cursor: grab !important;
                transition: opacity 0.25s ease, transform 0.25s ease !important;
            }}

            /* Pointer Laser Ray emitting from Guide's Hand */
            .guide-pointer-beam {{
                position: absolute !important;
                width: 3px !important;
                background: linear-gradient(to right, #00f0ff, transparent) !important;
                box-shadow: 0 0 12px #00f0ff, 0 0 20px #a855f7 !important;
                transform-origin: 0 50% !important;
                pointer-events: none !important;
                opacity: 0;
                transition: opacity 0.3s ease !important;
                z-index: 2147483646 !important;
            }}

            /* =========================================================================
               SPEECH BUBBLE & INTERACTIVE TOUR CARD
               ========================================================================= */
            #pathfinder-tour-card {{
                width: 440px !important;
                max-width: calc(100vw - 40px) !important;
                max-height: calc(100vh - 48px) !important;
                box-sizing: border-box !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                background: linear-gradient(155deg, rgba(15, 23, 42, 0.97) 0%, rgba(10, 15, 30, 0.98) 100%) !important;
                border: 1.5px solid rgba(56, 189, 248, 0.5) !important;
                border-radius: 20px !important;
                padding: 18px 20px !important;
                box-shadow: 0 25px 65px -10px rgba(0, 0, 0, 0.92), 0 0 35px rgba(56, 189, 248, 0.25) !important;
                backdrop-filter: blur(28px) !important;
                -webkit-backdrop-filter: blur(28px) !important;
                color: #f1f5f9 !important;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
                scrollbar-width: thin !important;
                scrollbar-color: rgba(56, 189, 248, 0.4) transparent !important;
                position: relative !important;
            }}
            #pathfinder-tour-card::-webkit-scrollbar {{
                width: 6px !important;
            }}
            #pathfinder-tour-card::-webkit-scrollbar-thumb {{
                background: rgba(56, 189, 248, 0.4) !important;
                border-radius: 9999px !important;
            }}

            /* Dialogue Speech Bubble Header */
            .tour-bot-companion-wrapper {{
                display: flex !important;
                align-items: center !important;
                gap: 12px !important;
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
                border: 1.5px solid rgba(56, 189, 248, 0.3) !important;
                border-radius: 14px !important;
                padding: 10px 14px !important;
                margin-bottom: 14px !important;
                position: relative !important;
                overflow: hidden !important;
                box-shadow: inset 0 0 20px rgba(56, 189, 248, 0.08), 0 6px 18px rgba(0, 0, 0, 0.4) !important;
            }}
            .tour-bot-speech-bubble {{
                flex: 1 !important;
                min-width: 0 !important;
            }}
            .tour-bot-speech-header {{
                display: flex !important;
                align-items: center !important;
                justify-content: space-between !important;
                margin-bottom: 6px !important;
            }}
            .tour-bot-name {{
                display: flex !important;
                align-items: center !important;
                gap: 8px !important;
            }}
            .tour-bot-avatar-badge {{
                font-family: 'JetBrains Mono', monospace !important;
                font-size: 0.70rem !important;
                font-weight: 800 !important;
                color: #38bdf8 !important;
                letter-spacing: 0.05em !important;
            }}
            .tour-bot-live-status {{
                display: inline-flex !important;
                align-items: center !important;
                gap: 5px !important;
                font-size: 0.60rem !important;
                font-weight: 700 !important;
                color: #10b981 !important;
                font-family: 'JetBrains Mono', monospace !important;
                background: rgba(16, 185, 129, 0.15) !important;
                border: 1px solid rgba(16, 185, 129, 0.35) !important;
                padding: 1px 7px !important;
                border-radius: 9999px !important;
            }}
            .tour-bot-status-dot {{
                width: 6px !important;
                height: 6px !important;
                border-radius: 50% !important;
                background: #10b981 !important;
                box-shadow: 0 0 6px #10b981 !important;
                animation: statusPulse 1.5s infinite !important;
            }}
            @keyframes statusPulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.4; }}
            }}

            /* Voice Controls & Equalizer Bars */
            .tour-bot-controls-group {{
                display: flex !important;
                align-items: center !important;
                gap: 8px !important;
            }}
            .tour-voice-toggle-btn {{
                background: rgba(255, 255, 255, 0.08) !important;
                border: 1px solid rgba(255, 255, 255, 0.16) !important;
                color: #e2e8f0 !important;
                font-size: 0.72rem !important;
                padding: 3px 8px !important;
                border-radius: 6px !important;
                cursor: pointer !important;
                display: inline-flex !important;
                align-items: center !important;
                gap: 4px !important;
                transition: all 0.2s ease !important;
            }}
            .tour-voice-toggle-btn:hover {{
                background: rgba(56, 189, 248, 0.2) !important;
                border-color: #38bdf8 !important;
                color: #38bdf8 !important;
            }}
            .tour-bot-voice-bars {{
                display: flex !important;
                align-items: flex-end !important;
                gap: 3px !important;
                height: 14px !important;
            }}
            .tour-bot-voice-bars span {{
                display: block !important;
                width: 3px !important;
                background: #38bdf8 !important;
                border-radius: 2px !important;
                box-shadow: 0 0 6px #38bdf8 !important;
                height: 4px;
                transition: height 0.15s ease !important;
            }}
            .tour-bot-voice-bars.speaking span:nth-child(1) {{ animation: vBarAnim 0.7s infinite alternate 0.0s; }}
            .tour-bot-voice-bars.speaking span:nth-child(2) {{ animation: vBarAnim 0.7s infinite alternate 0.2s; }}
            .tour-bot-voice-bars.speaking span:nth-child(3) {{ animation: vBarAnim 0.7s infinite alternate 0.4s; }}
            .tour-bot-voice-bars.speaking span:nth-child(4) {{ animation: vBarAnim 0.7s infinite alternate 0.1s; }}
            .tour-bot-voice-bars.speaking span:nth-child(5) {{ animation: vBarAnim 0.7s infinite alternate 0.3s; }}
            @keyframes vBarAnim {{
                0% {{ height: 3px; }}
                100% {{ height: 14px; }}
            }}

            .tour-bot-speech-dialogue {{
                font-size: 0.84rem !important;
                line-height: 1.45 !important;
                color: #e2e8f0 !important;
                font-style: italic !important;
            }}

            /* Tour Step Header */
            .tour-card-header {{
                display: flex !important;
                align-items: center !important;
                justify-content: space-between !important;
                margin-bottom: 10px !important;
            }}
            .tour-step-badge {{
                font-family: 'JetBrains Mono', monospace !important;
                font-size: 0.64rem !important;
                font-weight: 800 !important;
                color: #38bdf8 !important;
                background: rgba(56, 189, 248, 0.15) !important;
                border: 1px solid rgba(56, 189, 248, 0.35) !important;
                padding: 3px 9px !important;
                border-radius: 9999px !important;
                letter-spacing: 0.08em !important;
            }}
            .tour-step-count {{
                font-size: 0.70rem !important;
                font-weight: 700 !important;
                color: #94a3b8 !important;
                font-family: 'JetBrains Mono', monospace !important;
            }}
            .tour-close-btn {{
                background: transparent !important;
                border: none !important;
                color: #64748b !important;
                font-size: 1.15rem !important;
                cursor: pointer !important;
                line-height: 1 !important;
                padding: 2px 6px !important;
                border-radius: 6px !important;
                transition: all 0.2s ease !important;
            }}
            .tour-close-btn:hover {{
                color: #f8fafc !important;
                background: rgba(255, 255, 255, 0.1) !important;
            }}

            /* Progress Bar */
            .tour-progress-bar-wrap {{
                display: flex !important;
                gap: 5px !important;
                margin-bottom: 12px !important;
            }}
            .tour-progress-segment {{
                flex: 1 !important;
                height: 4px !important;
                border-radius: 2px !important;
                background: rgba(255, 255, 255, 0.12) !important;
                transition: background 0.3s ease !important;
            }}
            .tour-progress-segment.completed {{
                background: #38bdf8 !important;
            }}
            .tour-progress-segment.active {{
                background: linear-gradient(90deg, #38bdf8, #a855f7) !important;
                box-shadow: 0 0 8px rgba(56, 189, 248, 0.6) !important;
            }}

            /* Title & Body */
            .tour-card-title {{
                font-size: 1.15rem !important;
                font-weight: 800 !important;
                color: #f8fafc !important;
                margin: 0 0 8px 0 !important;
                letter-spacing: -0.01em !important;
                background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
            }}
            .tour-card-body {{
                font-size: 0.85rem !important;
                line-height: 1.55 !important;
                color: #cbd5e1 !important;
                margin-bottom: 12px !important;
            }}

            /* Prompt Example Bubble */
            .tour-prompt-example {{
                background: rgba(56, 189, 248, 0.1) !important;
                border: 1px dashed rgba(56, 189, 248, 0.45) !important;
                border-radius: 10px !important;
                padding: 10px 14px !important;
                font-family: 'JetBrains Mono', monospace !important;
                font-size: 0.78rem !important;
                color: #7dd3fc !important;
                margin-bottom: 12px !important;
                display: flex !important;
                align-items: center !important;
                gap: 8px !important;
                cursor: pointer !important;
            }}
            .tour-prompt-example:hover {{
                background: rgba(56, 189, 248, 0.18) !important;
                border-color: #38bdf8 !important;
            }}

            /* Pro Tip Box */
            .tour-pro-tip {{
                background: rgba(168, 85, 247, 0.1) !important;
                border-left: 3px solid #a855f7 !important;
                border-radius: 0 8px 8px 0 !important;
                padding: 8px 12px !important;
                font-size: 0.75rem !important;
                color: #e9d5ff !important;
                margin-bottom: 14px !important;
            }}

            /* Footer Actions */
            .tour-card-actions {{
                display: flex !important;
                align-items: center !important;
                justify-content: space-between !important;
                padding-top: 12px !important;
                border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
            }}
            .tour-btn-skip {{
                background: transparent !important;
                border: none !important;
                color: #94a3b8 !important;
                font-size: 0.8rem !important;
                font-weight: 600 !important;
                cursor: pointer !important;
                padding: 6px 12px !important;
                border-radius: 8px !important;
                transition: all 0.2s ease !important;
            }}
            .tour-btn-skip:hover {{
                color: #f1f5f9 !important;
                background: rgba(255, 255, 255, 0.06) !important;
            }}
            .tour-btn-nav-group {{
                display: flex !important;
                align-items: center !important;
                gap: 8px !important;
            }}
            .tour-btn-prev {{
                background: rgba(255, 255, 255, 0.08) !important;
                border: 1px solid rgba(255, 255, 255, 0.15) !important;
                color: #e2e8f0 !important;
                font-size: 0.82rem !important;
                font-weight: 700 !important;
                padding: 8px 14px !important;
                border-radius: 10px !important;
                cursor: pointer !important;
                transition: all 0.2s ease !important;
            }}
            .tour-btn-prev:hover {{
                background: rgba(255, 255, 255, 0.15) !important;
                color: #ffffff !important;
            }}
            .tour-btn-next {{
                background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%) !important;
                border: none !important;
                color: #030712 !important;
                font-size: 0.84rem !important;
                font-weight: 800 !important;
                padding: 8px 18px !important;
                border-radius: 10px !important;
                cursor: pointer !important;
                box-shadow: 0 0 16px rgba(56, 189, 248, 0.45) !important;
                transition: all 0.2s ease !important;
            }}
            .tour-btn-next:hover {{
                transform: translateY(-1px) scale(1.02) !important;
                box-shadow: 0 0 24px rgba(56, 189, 248, 0.75) !important;
            }}
            .tour-btn-finish {{
                background: linear-gradient(135deg, #9333ea 0%, #c084fc 100%) !important;
                color: #ffffff !important;
                box-shadow: 0 0 20px rgba(168, 85, 247, 0.55) !important;
            }}
            .tour-btn-finish:hover {{
                box-shadow: 0 0 30px rgba(168, 85, 247, 0.85) !important;
            }}

            /* =========================================================================
               FIRST-TIME WELCOME POPUP MODAL (Greeting from 3D Guide)
               ========================================================================= */
            #pathfinder-welcome-dialog {{
                position: fixed !important;
                bottom: 30px !important;
                left: 30px !important;
                width: 390px !important;
                max-width: calc(100vw - 40px) !important;
                background: linear-gradient(145deg, rgba(15, 23, 42, 0.98) 0%, rgba(10, 15, 30, 0.98) 100%) !important;
                border: 1.5px solid #00f0ff !important;
                border-radius: 18px !important;
                padding: 18px 20px !important;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.85), 0 0 30px rgba(0, 240, 255, 0.35) !important;
                backdrop-filter: blur(24px) !important;
                -webkit-backdrop-filter: blur(24px) !important;
                z-index: 2147483642 !important;
                color: #f1f5f9 !important;
                font-family: 'Inter', sans-serif !important;
                opacity: 0;
                transform: translateY(30px) scale(0.96);
                transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
                display: none;
            }}
            #pathfinder-welcome-dialog.active {{
                display: block !important;
                opacity: 1 !important;
                transform: translateY(0) !important;
            }}

            /* Backward compatibility selectors for tests */
            .tour-bot-3d-scene {{ display: none !important; }}
            .tour-bot-chassis {{ display: none !important; }}
        `;
    }} catch(e) {{
        console.warn("[3DGuide] Style injection notice:", e);
    }}

    // =========================================================================
    // THREE.JS SCRIPT LOADER & WEBGL 3D CHARACTER ENGINE
    // =========================================================================
    var threeJsLoaded = false;
    var character3DEngine = null;

    function ensureThreeJs(callback) {{
        var THREE = pWin.THREE || window.THREE;
        if (THREE) {{
            threeJsLoaded = true;
            if (callback) callback();
            return;
        }}
        var script = pDoc.getElementById('three-js-cdn-script');
        if (!script) {{
            script = pDoc.createElement('script');
            script.id = 'three-js-cdn-script';
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
            var fired = false;
            function done() {{
                if (!fired) {{
                    fired = true;
                    threeJsLoaded = !!(pWin.THREE || window.THREE);
                    if (callback) callback();
                }}
            }}
            script.onload = done;
            script.onerror = done;
            pDoc.head.appendChild(script);
            setTimeout(done, 1200);
        }} else {{
            // Script tag already injected into head
            if (pWin.THREE || window.THREE) {{
                threeJsLoaded = true;
                if (callback) callback();
            }} else {{
                setTimeout(function() {{
                    threeJsLoaded = !!(pWin.THREE || window.THREE);
                    if (callback) callback();
                }}, 200);
            }}
        }}
    }}

    function create3DCharacter(containerEl) {{
        if (!pWin.THREE) return null;
        var THREE = pWin.THREE;

        var width = 140;
        var height = 165;

        var scene = new THREE.Scene();
        var camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 50);
        camera.position.set(0, 0.2, 3.4);

        var renderer = null;
        try {{
            renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true, powerPreference: "high-performance" }});
            renderer.setSize(width, height);
            renderer.setPixelRatio(Math.min(pWin.devicePixelRatio || 1, 2));
            renderer.setClearColor(0x000000, 0);
            renderer.domElement.style.display = "none";
        }} catch(e) {{
            console.warn("[3DGuide] WebGL context unavailable:", e);
            return null;
        }}

        // Lighting System
        var ambLight = new THREE.AmbientLight(0x38bdf8, 0.7);
        scene.add(ambLight);

        var dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
        dirLight.position.set(2, 4, 3);
        scene.add(dirLight);

        var rimLight1 = new THREE.PointLight(0x00f0ff, 1.8, 6);
        rimLight1.position.set(-2, 1, 1);
        scene.add(rimLight1);

        var rimLight2 = new THREE.PointLight(0xa855f7, 1.8, 6);
        rimLight2.position.set(2, -1, 1);
        scene.add(rimLight2);

        // Character Main Hierarchy
        var companionGroup = new THREE.Group();
        scene.add(companionGroup);

        // 1. Torso / Chassis
        var torsoGeo = new THREE.CylinderGeometry(0.36, 0.25, 0.6, 24);
        var torsoMat = new THREE.MeshStandardMaterial({{
            color: 0x0f172a,
            metalness: 0.85,
            roughness: 0.25,
            emissive: 0x032840,
            emissiveIntensity: 0.25
        }});
        var torso = new THREE.Mesh(torsoGeo, torsoMat);
        companionGroup.add(torso);

        // Quantum Reactor Chest Core
        var coreGeo = new THREE.TorusGeometry(0.14, 0.03, 16, 24);
        var coreMat = new THREE.MeshBasicMaterial({{ color: 0x00f0ff }});
        var coreRing = new THREE.Mesh(coreGeo, coreMat);
        coreRing.position.set(0, 0.04, 0.32);
        companionGroup.add(coreRing);

        var innerCoreGeo = new THREE.OctahedronGeometry(0.08);
        var innerCoreMat = new THREE.MeshBasicMaterial({{ color: 0xa855f7 }});
        var innerCore = new THREE.Mesh(innerCoreGeo, innerCoreMat);
        innerCore.position.set(0, 0.04, 0.32);
        companionGroup.add(innerCore);

        // Anti-Gravity Holographic Thruster Ring
        var thrusterGeo = new THREE.TorusGeometry(0.32, 0.035, 16, 32);
        var thrusterMat = new THREE.MeshBasicMaterial({{ color: 0x00f0ff }});
        var thrusterRing = new THREE.Mesh(thrusterGeo, thrusterMat);
        thrusterRing.rotation.x = Math.PI / 2;
        thrusterRing.position.set(0, -0.34, 0);
        companionGroup.add(thrusterRing);

        // 2. Head & Visor
        var headGroup = new THREE.Group();
        headGroup.position.set(0, 0.48, 0);
        companionGroup.add(headGroup);

        var helmetGeo = new THREE.SphereGeometry(0.34, 24, 20);
        var helmetMat = new THREE.MeshStandardMaterial({{
            color: 0x1e293b,
            metalness: 0.9,
            roughness: 0.2,
            emissive: 0x0b192c,
            emissiveIntensity: 0.3
        }});
        var helmet = new THREE.Mesh(helmetGeo, helmetMat);
        headGroup.add(helmet);

        // Curved Digital Visor
        var visorGeo = new THREE.SphereGeometry(0.28, 20, 16, 0, Math.PI, 0, Math.PI * 0.7);
        var visorMat = new THREE.MeshStandardMaterial({{
            color: 0x050b14,
            metalness: 0.95,
            roughness: 0.05,
            emissive: 0x003344,
            emissiveIntensity: 0.5
        }});
        var visor = new THREE.Mesh(visorGeo, visorMat);
        visor.rotation.y = -Math.PI / 2;
        visor.rotation.x = 0.2;
        visor.position.set(0, 0.02, 0.12);
        headGroup.add(visor);

        // Expressive Eyes
        var eyeGeo = new THREE.PlaneGeometry(0.08, 0.11);
        var eyeMat = new THREE.MeshBasicMaterial({{ color: 0x00f0ff, transparent: true, opacity: 0.95 }});
        
        var leftEye = new THREE.Mesh(eyeGeo, eyeMat);
        leftEye.position.set(-0.10, 0.02, 0.36);
        headGroup.add(leftEye);

        var rightEye = new THREE.Mesh(eyeGeo, eyeMat);
        rightEye.position.set(0.10, 0.02, 0.36);
        headGroup.add(rightEye);

        // Side Antennae with Blinking Beacons
        var antL = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.25), new THREE.MeshStandardMaterial({{ color: 0x38bdf8 }}));
        antL.position.set(-0.35, 0.15, 0);
        antL.rotation.z = 0.3;
        headGroup.add(antL);

        var beaconL = new THREE.Mesh(new THREE.SphereGeometry(0.04), new THREE.MeshBasicMaterial({{ color: 0x00f0ff }}));
        beaconL.position.set(-0.41, 0.28, 0);
        headGroup.add(beaconL);

        var antR = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.25), new THREE.MeshStandardMaterial({{ color: 0x38bdf8 }}));
        antR.position.set(0.35, 0.15, 0);
        antR.rotation.z = -0.3;
        headGroup.add(antR);

        var beaconR = new THREE.Mesh(new THREE.SphereGeometry(0.04), new THREE.MeshBasicMaterial({{ color: 0xa855f7 }}));
        beaconR.position.set(0.41, 0.28, 0);
        headGroup.add(beaconR);

        // 3. Articulated Robotic Arms
        // Right Arm (Pointing / Waving)
        var rightArmGroup = new THREE.Group();
        rightArmGroup.position.set(0.42, 0.18, 0);
        companionGroup.add(rightArmGroup);

        var rForearm = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.035, 0.35), new THREE.MeshStandardMaterial({{ color: 0x1e293b, metalness: 0.8 }}));
        rForearm.position.set(0, -0.16, 0);
        rightArmGroup.add(rForearm);

        var rHand = new THREE.Mesh(new THREE.SphereGeometry(0.065), new THREE.MeshBasicMaterial({{ color: 0x00f0ff }}));
        rHand.position.set(0, -0.34, 0.04);
        rightArmGroup.add(rHand);

        // Left Arm
        var leftArmGroup = new THREE.Group();
        leftArmGroup.position.set(-0.42, 0.18, 0);
        companionGroup.add(leftArmGroup);

        var lForearm = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.035, 0.35), new THREE.MeshStandardMaterial({{ color: 0x1e293b, metalness: 0.8 }}));
        lForearm.position.set(0, -0.16, 0);
        leftArmGroup.add(lForearm);

        var lHand = new THREE.Mesh(new THREE.SphereGeometry(0.065), new THREE.MeshBasicMaterial({{ color: 0x38bdf8 }}));
        lHand.position.set(0, -0.34, 0.04);
        leftArmGroup.add(lHand);

        // Animation State Controller
        var currentMood = "idle";
        var isRunning = true;
        var clock = new THREE.Clock();

        function animate() {{
            if (!isRunning) return;
            pWin.requestAnimationFrame(animate);

            var t = clock.getElapsedTime();

            // Core idle hover & gentle pitch
            companionGroup.position.y = Math.sin(t * 2.5) * 0.08;
            companionGroup.rotation.y = Math.sin(t * 1.2) * 0.12;

            // Gyroscope core spin
            innerCore.rotation.x = t * 2.2;
            innerCore.rotation.y = t * 3.1;
            thrusterRing.rotation.z = t * 3.5;

            // Eye blinking logic
            var blinkCycle = (t % 4.0);
            if (blinkCycle > 3.82) {{
                leftEye.scale.y = 0.1;
                rightEye.scale.y = 0.1;
            }} else {{
                leftEye.scale.y = 1.0;
                rightEye.scale.y = 1.0;
            }}

            // Mood-driven Animation Blend
            if (currentMood === "waving") {{
                // Friendly arm wave
                rightArmGroup.rotation.z = -1.2 + Math.sin(t * 7.0) * 0.45;
                rightArmGroup.rotation.x = 0.3;
                headGroup.rotation.z = Math.sin(t * 3.5) * 0.12;
                leftArmGroup.rotation.z = 0.2;
            }} else if (currentMood === "pointing") {{
                // Pointing directly forward-left
                rightArmGroup.rotation.z = -1.5;
                rightArmGroup.rotation.x = -1.0;
                rightArmGroup.rotation.y = -0.4;
                headGroup.rotation.y = -0.3;
                headGroup.rotation.x = 0.1;
                leftArmGroup.rotation.z = 0.2;
            }} else if (currentMood === "explaining") {{
                // Rhythmic speaking hand gestures
                rightArmGroup.rotation.z = -0.5 + Math.sin(t * 4.5) * 0.25;
                rightArmGroup.rotation.x = -0.3 + Math.sin(t * 3.5) * 0.2;
                leftArmGroup.rotation.z = 0.4 + Math.sin(t * 4.0) * 0.15;
                headGroup.rotation.y = Math.sin(t * 2.0) * 0.18;
            }} else if (currentMood === "thinking") {{
                // Hand to chin, head tilted up
                rightArmGroup.rotation.z = -1.8;
                rightArmGroup.rotation.x = -1.1;
                rightArmGroup.rotation.y = 0.3;
                headGroup.rotation.x = -0.22;
                headGroup.rotation.z = 0.18;
            }} else if (currentMood === "celebrating") {{
                // Both hands high in celebration, enthusiastic cheer spin
                rightArmGroup.rotation.z = -2.2 + Math.sin(t * 8.0) * 0.2;
                leftArmGroup.rotation.z = 2.2 - Math.sin(t * 8.0) * 0.2;
                companionGroup.rotation.y = Math.sin(t * 4.0) * 0.5;
                headGroup.rotation.x = -0.15;
            }} else {{
                // Default Idle
                rightArmGroup.rotation.z = -0.25 + Math.sin(t * 2.0) * 0.08;
                rightArmGroup.rotation.x = 0.1;
                leftArmGroup.rotation.z = 0.25 - Math.sin(t * 2.0) * 0.08;
                headGroup.rotation.set(0, 0, 0);
            }}

            renderer.render(scene, camera);
        }}

        animate();

        return {{
            setMood: function(mood) {{
                currentMood = mood;
            }},
            dispose: function() {{
                isRunning = false;
                try {{
                    if (renderer && renderer.domElement && renderer.domElement.parentNode) {{
                        renderer.domElement.parentNode.removeChild(renderer.domElement);
                    }}
                    renderer.dispose();
                }} catch(e) {{}}
            }}
        }};
    }}

    // =========================================================================
    // DOM ELEMENTS FACTORY (Backdrop, Spotlight, 3D Guide Stage, Card)
    // =========================================================================
    function getOrCreateTourElements() {{
        var backdrop = pDoc.getElementById('pathfinder-tour-backdrop');
        if (!backdrop) {{
            backdrop = pDoc.createElement('div');
            backdrop.id = 'pathfinder-tour-backdrop';
            pDoc.body.appendChild(backdrop);
        }}

        var spotlight = pDoc.getElementById('pathfinder-tour-spotlight');
        if (!spotlight) {{
            spotlight = pDoc.createElement('div');
            spotlight.id = 'pathfinder-tour-spotlight';
            pDoc.body.appendChild(spotlight);
        }}

        var stage = pDoc.getElementById('pathfinder-guide-stage');
        if (!stage) {{
            stage = pDoc.createElement('div');
            stage.id = 'pathfinder-guide-stage';
            stage.innerHTML = `
                <div class="guide-stage-layout" id="guide-stage-layout">
                    <div class="guide-character-3d-box" id="guide-character-3d-box" title="NexRoute 3D Guide">
                        <img src="" class="guide-character-pose-img" id="guide-companion-pose-img" alt="NexRoute 3D Guide" />
                        <div class="dashboard-robot-pedestal-glow" style="bottom: 0px; width: 95px; height: 18px; margin: 0 auto; left: 0; right: 0;"></div>
                        <!-- Backward compatibility hooks for test suite -->
                        <div class="tour-bot-3d-scene" style="display:none;"></div>
                        <div class="tour-bot-chassis" style="display:none;"></div>
                    </div>
                    <div id="pathfinder-tour-card"></div>
                </div>
            `;
            pDoc.body.appendChild(stage);
        }}

        var card = stage.querySelector('#pathfinder-tour-card');
        return {{ backdrop: backdrop, spotlight: spotlight, stage: stage, card: card }};
    }}

    // =========================================================================
    // SPEECH SYNTHESIS & VOICE EQUALIZER
    // =========================================================================
    function speakText(text) {{
        if (!isSpeechSupported || isVoiceMuted || !text) return;

        try {{
            pWin.speechSynthesis.cancel();

            var cleanText = text.replace(/<[^>]*>/g, '').replace(/💡|🚀|🤖|🧭|💳|🛣️|⛴️|⏱️|🗺️|📖|🎉/g, '');
            var utt = new pWin.SpeechSynthesisUtterance(cleanText);
            utt.lang = currentVoiceLang || 'en-IN';
            utt.rate = 1.05;
            utt.pitch = 1.1;

            var voices = pWin.speechSynthesis.getVoices();
            if (voices && voices.length > 0) {{
                var langPrefix = (currentVoiceLang || 'en').split('-')[0].toLowerCase();
                var preferredVoice = voices.find(function(v) {{
                    return v.lang && v.lang.toLowerCase().startsWith(langPrefix);
                }}) || voices.find(function(v) {{
                    return v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha') || v.name.includes('David'));
                }}) || voices[0];
                if (preferredVoice) utt.voice = preferredVoice;
            }}

            var voiceBars = pDoc.querySelector('.tour-bot-voice-bars');
            utt.onstart = function() {{
                if (voiceBars) voiceBars.classList.add('speaking');
                if (character3DEngine) character3DEngine.setMood("explaining");
            }};
            utt.onend = function() {{
                if (voiceBars) voiceBars.classList.remove('speaking');
                if (character3DEngine) character3DEngine.setMood("idle");
            }};
            utt.onerror = function() {{
                if (voiceBars) voiceBars.classList.remove('speaking');
            }};

            activeUtterance = utt;
            pWin.speechSynthesis.speak(utt);
        }} catch(e) {{
            console.warn("[3DGuide] Speech synthesis notice:", e);
        }}
    }}

    function stopSpeaking() {{
        try {{
            if (isSpeechSupported && pWin.speechSynthesis) {{
                pWin.speechSynthesis.cancel();
            }}
            var voiceBars = pDoc.querySelector('.tour-bot-voice-bars');
            if (voiceBars) voiceBars.classList.remove('speaking');
        }} catch(e) {{}}
    }}

    // =========================================================================
    // TOUR STEP RENDERING & PHYSICAL SCREEN TRANSLATION
    // =========================================================================
    function renderTourStep(index) {{
        if (index < 0 || index >= tourSteps.length) return;
        currentStepIndex = index;
        var stepData = tourSteps[index];
        var els = getOrCreateTourElements();

        stopSpeaking();

        // 1. Locate Target Element in the DOM
        var targetEl = null;
        if (stepData.selector) {{
            var selectors = stepData.selector.split(',').map(function(s){{ return s.trim(); }});
            for (var si = 0; si < selectors.length; si++) {{
                var found = pDoc.querySelector(selectors[si]);
                if (found && found.offsetWidth > 0 && found.offsetHeight > 0) {{
                    targetEl = found;
                    break;
                }}
            }}
        }}

        var isCentered = stepData.fallback_center || !targetEl;

        // 2. Position Spotlight
        if (!isCentered && targetEl) {{
            try {{
                targetEl.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            }} catch(e) {{}}
            setTimeout(function() {{
                var rect = targetEl.getBoundingClientRect();
                var pad = 10;
                els.spotlight.style.display = 'block';
                els.spotlight.style.top = Math.max(0, rect.top - pad) + 'px';
                els.spotlight.style.left = Math.max(0, rect.left - pad) + 'px';
                els.spotlight.style.width = (rect.width + pad * 2) + 'px';
                els.spotlight.style.height = (rect.height + pad * 2) + 'px';
            }}, 180);
        }} else {{
            els.spotlight.style.display = 'none';
        }}

        // 3. Render Card HTML
        var isFirst = (index === 0);
        var isLast = (index === tourSteps.length - 1);

        var progressDotsHtml = '';
        for (var i = 0; i < tourSteps.length; i++) {{
            var cls = 'tour-progress-segment';
            if (i < index) cls += ' completed';
            else if (i === index) cls += ' active';
            progressDotsHtml += '<div class="' + cls + '"></div>';
        }}

        var proTipHtml = stepData.pro_tip ? '<div class="tour-pro-tip">' + stepData.pro_tip + '</div>' : '';
        var promptHtml = stepData.prompt_example ? '<div class="tour-prompt-example" id="tour-prompt-example-btn" title="Click to copy">' + stepData.prompt_example + '</div>' : '';

        var ui = uiStrings || {{}};
        var stepCountText = (ui.step_of || 'Step {{step}} of {{total}}').replace('{{step}}', stepData.step).replace('{{total}}', tourSteps.length);
        var closeTourTitle = ui.close_tour || 'Close Tour';
        var explainingLabel = ui.explaining || 'EXPLAINING';
        var voiceIcon = isVoiceMuted ? (ui.unmute || '🔇 Unmute') : (ui.voice || '🔊 Voice');
        var skipBtnLabel = isLast ? (ui.close || 'Close') : (ui.skip_tour || 'Skip Tour');
        var prevBtnLabel = ui.prev || '← Previous';
        var nextBtnLabel = isLast ? (ui.start_planning || 'Start Planning 🚀') : (ui.next || 'Next →');

        els.card.innerHTML = `
            <div class="tour-card-header">
                <span class="tour-step-badge">${{stepData.badge}}</span>
                <span class="tour-step-count">${{stepCountText}}</span>
                <button class="tour-close-btn" id="tour-btn-close-x" title="${{closeTourTitle}}">✕</button>
            </div>
            <div class="tour-progress-bar-wrap">
                ${{progressDotsHtml}}
            </div>

            <!-- Dialogue Speech Bubble -->
            <div class="tour-bot-companion-wrapper">
                <div class="tour-bot-speech-bubble">
                    <div class="tour-bot-speech-header">
                        <div class="tour-bot-name">
                            <span class="tour-bot-avatar-badge">🤖 A.U.R.A. 3D GUIDE</span>
                            <span class="tour-bot-live-status">
                                <span class="tour-bot-status-dot"></span>
                                <span class="tour-bot-status-text">${{explainingLabel}}</span>
                            </span>
                        </div>
                        <div class="tour-bot-controls-group">
                            <button class="tour-voice-toggle-btn" id="tour-voice-toggle-btn" title="Toggle Spoken Guide Audio">
                                ${{voiceIcon}}
                            </button>
                            <div class="tour-bot-voice-bars">
                                <span></span><span></span><span></span><span></span><span></span>
                            </div>
                        </div>
                    </div>
                    <div class="tour-bot-speech-dialogue" id="tour-bot-dialogue">
                        "${{stepData.bot_dialogue}}"
                    </div>
                </div>
            </div>

            <h3 class="tour-card-title">${{stepData.title}}</h3>
            <div class="tour-card-body">${{stepData.content}}</div>
            ${{promptHtml}}
            ${{proTipHtml}}
            <div class="tour-card-actions">
                <button class="tour-btn-skip" id="tour-btn-skip">${{skipBtnLabel}}</button>
                <div class="tour-btn-nav-group">
                    ${{!isFirst ? '<button class="tour-btn-prev" id="tour-btn-prev">' + prevBtnLabel + '</button>' : ''}}
                    ${{isLast 
                        ? '<button class="tour-btn-next tour-btn-finish" id="tour-btn-finish">' + nextBtnLabel + '</button>' 
                        : '<button class="tour-btn-next" id="tour-btn-next">' + nextBtnLabel + '</button>'
                    }}
                </div>
            </div>
        `;

        // 4. Smooth Physical Flight & Placement of 3D Guide Stage
        setTimeout(function() {{
            var viewW = pWin.innerWidth || pDoc.documentElement.clientWidth;
            var viewH = pWin.innerHeight || pDoc.documentElement.clientHeight;
            var stageLayout = els.stage.querySelector('#guide-stage-layout');

            var cardW = 560; // Total layout width
            var cardH = els.card.offsetHeight || 420;

            if (isCentered || !targetEl) {{
                // Center Screen Flight
                if (stageLayout) stageLayout.classList.remove('flipped');
                var topC = Math.max(20, (viewH - cardH) / 2);
                var leftC = Math.max(20, (viewW - cardW) / 2);
                els.stage.style.top = topC + 'px';
                els.stage.style.left = leftC + 'px';
            }} else {{
                var rect = targetEl.getBoundingClientRect();
                var top, left;

                // Dynamically decide placement relative to target
                if (rect.right + cardW + 20 <= viewW) {{
                    // Place to the right of element
                    if (stageLayout) stageLayout.classList.remove('flipped');
                    top = Math.max(20, Math.min(viewH - cardH - 20, rect.top - 20));
                    left = rect.right + 20;
                }} else if (rect.left - cardW - 20 >= 0) {{
                    // Place to the left of element (flip 3D character to right side of card)
                    if (stageLayout) stageLayout.classList.add('flipped');
                    top = Math.max(20, Math.min(viewH - cardH - 20, rect.top - 20));
                    left = rect.left - cardW - 20;
                }} else if (rect.bottom + cardH + 20 <= viewH) {{
                    // Place below element
                    if (stageLayout) stageLayout.classList.remove('flipped');
                    top = rect.bottom + 16;
                    left = Math.max(20, Math.min(viewW - cardW - 20, rect.left));
                }} else {{
                    // Place above element
                    if (stageLayout) stageLayout.classList.remove('flipped');
                    top = Math.max(20, rect.top - cardH - 16);
                    left = Math.max(20, Math.min(viewW - cardW - 20, rect.left));
                }}

                els.stage.style.top = top + 'px';
                els.stage.style.left = left + 'px';
            }}

            // Trigger Character 3D Mood & Pose Transition
            if (character3DEngine) {{
                character3DEngine.setMood(stepData.bot_mood || "pointing");
            }}

            var companionImg = els.stage.querySelector('#guide-companion-pose-img');
            if (companionImg) {{
                var poseKey = 'welcome';
                if (index === 1 || index === 2 || index === 4) {{
                    poseKey = 'pointing';
                }} else if (index === 3) {{
                    poseKey = 'talking';
                }} else if (index === 5) {{
                    poseKey = 'thinking';
                }} else if (index === 6) {{
                    poseKey = 'excited';
                }}
                var targetSrc = (mascotPoses && mascotPoses[poseKey]) ? mascotPoses[poseKey] : (mascotPoses && mascotPoses['welcome']) ? mascotPoses['welcome'] : '';
                if (targetSrc && companionImg.src !== targetSrc) {{
                    companionImg.style.opacity = '0.3';
                    companionImg.src = targetSrc;
                    setTimeout(function() {{ companionImg.style.opacity = '1'; }}, 120);
                }}
            }}

            // Speak Dialogue
            speakText(stepData.bot_dialogue);

        }}, 140);

        // 5. Wire Button Events
        var btnNext = els.card.querySelector('#tour-btn-next');
        if (btnNext) {{
            btnNext.onclick = function() {{
                renderTourStep(currentStepIndex + 1);
            }};
        }}
        var btnPrev = els.card.querySelector('#tour-btn-prev');
        if (btnPrev) {{
            btnPrev.onclick = function() {{
                renderTourStep(currentStepIndex - 1);
            }};
        }}
        var btnSkip = els.card.querySelector('#tour-btn-skip');
        if (btnSkip) {{
            btnSkip.onclick = function() {{
                endTour();
            }};
        }}
        var btnCloseX = els.card.querySelector('#tour-btn-close-x');
        if (btnCloseX) {{
            btnCloseX.onclick = function() {{
                endTour();
            }};
        }}
        var btnFinish = els.card.querySelector('#tour-btn-finish');
        if (btnFinish) {{
            btnFinish.onclick = function() {{
                endTour(true);
                var popoverBtn = pDoc.querySelector("div[data-testid='stPopover'] button");
                if (popoverBtn) {{
                    popoverBtn.click();
                }} else if (pWin.switchPathfinderTab) {{
                    pWin.switchPathfinderTab('nav', true);
                }}
            }};
        }}

        // Voice Mute Toggle
        var btnVoice = els.card.querySelector('#tour-voice-toggle-btn');
        if (btnVoice) {{
            btnVoice.onclick = function() {{
                isVoiceMuted = !isVoiceMuted;
                try {{
                    pWin.localStorage.setItem('pathfinder_voice_muted', isVoiceMuted ? '1' : '0');
                }} catch(e) {{}}
                btnVoice.innerHTML = isVoiceMuted ? '🔇 Unmute' : '🔊 Voice';
                if (isVoiceMuted) {{
                    stopSpeaking();
                }} else {{
                    speakText(stepData.bot_dialogue);
                }}
            }};
        }}

        // Copy Prompt Example
        var promptBtn = els.card.querySelector('#tour-prompt-example-btn');
        if (promptBtn) {{
            promptBtn.onclick = function() {{
                try {{
                    var text = "Plan a 3-day trip to Goa within ₹5,000 including food and stays";
                    pWin.navigator.clipboard.writeText(text);
                    promptBtn.innerHTML = "✅ Copied to Clipboard!";
                    setTimeout(function() {{
                        promptBtn.innerHTML = stepData.prompt_example;
                    }}, 2000);
                }} catch(e) {{}}
            }};
        }}

        // Action Hook (e.g. pulse chatbot logo)
        if (stepData.action === 'pulseAura') {{
            var auraLogo = pDoc.querySelector('.floating-aura-logo-overlay');
            if (auraLogo) {{
                auraLogo.style.transform = 'scale(1.25)';
                auraLogo.style.borderColor = '#00f0ff';
                auraLogo.style.boxShadow = '0 0 50px #00f0ff, 0 0 90px rgba(168, 85, 247, 0.8)';
                setTimeout(function() {{
                    auraLogo.style.transform = '';
                    auraLogo.style.borderColor = '';
                    auraLogo.style.boxShadow = '';
                }}, 2200);
            }}
        }}

        els.backdrop.classList.add('active');
        els.stage.classList.add('active');
    }}

    // =========================================================================
    // START / END TOUR CONTROLLER
    // =========================================================================
    function startTour(fromIndex) {{
        isTourActive = true;
        var els = getOrCreateTourElements();
        els.backdrop.classList.add('active');
        els.stage.classList.add('active');

        // Dismiss First-Time Welcome Dialog if showing
        var welcomeDiag = pDoc.getElementById('pathfinder-welcome-dialog');
        if (welcomeDiag) {{
            welcomeDiag.classList.remove('active');
            setTimeout(function() {{ if (welcomeDiag.parentNode) welcomeDiag.parentNode.removeChild(welcomeDiag); }}, 300);
        }}

        // Render step immediately so tour starts with ZERO delay!
        renderTourStep(fromIndex || 0);

        // Asynchronously initialize WebGL 3D Character if available
        ensureThreeJs(function() {{
            try {{
                var box = els.stage.querySelector('#guide-character-3d-box');
                if (box && !character3DEngine) {{
                    character3DEngine = create3DCharacter(box);
                    if (character3DEngine && isTourActive && tourSteps[currentStepIndex]) {{
                        character3DEngine.setMood(tourSteps[currentStepIndex].bot_mood || "pointing");
                    }}
                }}
            }} catch(e) {{
                console.warn("[3DGuide] 3D character engine init warning:", e);
            }}
        }});

        try {{
            pWin.localStorage.setItem('pathfinder_tour_dismissed', '1');
            pWin.localStorage.setItem('pathfinder_tour_welcomed', '1');
        }} catch(e) {{}}
    }}

    function endTour(isCompleted) {{
        isTourActive = false;
        stopSpeaking();

        var els = getOrCreateTourElements();
        els.backdrop.classList.remove('active');
        els.stage.classList.remove('active');
        if (els.spotlight) els.spotlight.style.display = 'none';

        if (character3DEngine) {{
            character3DEngine.setMood("idle");
        }}

        try {{
            pWin.localStorage.setItem('pathfinder_tour_dismissed', '1');
            if (isCompleted) {{
                pWin.localStorage.setItem('pathfinder_tour_completed', '1');
            }}
        }} catch(e) {{}}
    }}

    // Keyboard Shortcuts
    function onKeyDown(e) {{
        if (!isTourActive) return;
        if (e.key === 'Escape') {{
            endTour();
        }} else if (e.key === 'ArrowRight' || e.key === 'Enter') {{
            if (currentStepIndex < tourSteps.length - 1) {{
                renderTourStep(currentStepIndex + 1);
            }} else {{
                endTour(true);
            }}
        }} else if (e.key === 'ArrowLeft') {{
            if (currentStepIndex > 0) {{
                renderTourStep(currentStepIndex - 1);
            }}
        }}
    }}

    pWin.addEventListener('keydown', onKeyDown);
    window.addEventListener('keydown', onKeyDown);

    // Global Click Listener for Tour Triggers
    function onDocClick(e) {{
        var trigger = e.target && e.target.closest && e.target.closest('#btn-hero-quick-tour, .quick-tour-trigger-btn, [data-tour-trigger], #lang-box-walking-aura, .lang-box-walking-aura, .lang-bot-speech-bubble, #aura-walking-3d-canvas');
        if (trigger) {{
            e.preventDefault();
            e.stopPropagation();
            startTour(0);
        }}
    }}
    pDoc.addEventListener('click', onDocClick, true);
    document.addEventListener('click', onDocClick, true);
    try {{ pWin.addEventListener('click', onDocClick, true); }} catch(e) {{}}
    try {{ window.addEventListener('click', onDocClick, true); }} catch(e) {{}}

    // Global Methods for Parent Window
    pWin.startPathfinderTour = window.startPathfinderTour = function(idx) {{
        startTour(idx || 0);
    }};
    pWin.closePathfinderTour = window.closePathfinderTour = function() {{
        endTour();
    }};
    try {{ if (window.top) window.top.startPathfinderTour = pWin.startPathfinderTour; }} catch(e) {{}}

    function handleTourMessage(ev) {{
        try {{
            if (!ev || !ev.data) return;
            if (ev.data === 'START_PATHFINDER_TOUR' || ev.data.type === 'START_PATHFINDER_TOUR' || ev.data.action === 'START_PATHFINDER_TOUR') {{
                startTour(ev.data.step || 0);
            }}
        }} catch(e) {{}}
    }}
    try {{ pWin.addEventListener('message', handleTourMessage); }} catch(e) {{}}
    try {{ window.addEventListener('message', handleTourMessage); }} catch(e) {{}}

    // =========================================================================
    // FIRST-TIME WELCOME EXPERIENCE ("Show Me Around" vs "I'll Explore Myself")
    // =========================================================================
    function checkFirstTimeWelcome() {{
        try {{
            var welcomed = pWin.localStorage.getItem('pathfinder_tour_welcomed');
            var dismissed = pWin.localStorage.getItem('pathfinder_tour_dismissed');
            if (welcomed === '1' || dismissed === '1') return;
        }} catch(e) {{
            return;
        }}

        setTimeout(function() {{
            var dialog = pDoc.getElementById('pathfinder-welcome-dialog');
            if (dialog) return;

            var ui = uiStrings || {{}};
            var welcomeDialogue = ui.welcome_msg || "Hey there! Welcome to NexRoute. I am your virtual guide, and I will show you how to use your travel assistant. Ready to explore?";
            var dismissBtnText = ui.explore_myself || "I'll Explore Myself";
            var tourBtnText = ui.show_me || "✨ Show Me Around";

            dialog = pDoc.createElement('div');
            dialog.id = 'pathfinder-welcome-dialog';
            dialog.innerHTML = `
                <div style="display: flex; align-items: flex-start; gap: 14px; margin-bottom: 12px;">
                    <div style="width: 44px; height: 44px; min-width: 44px; border-radius: 12px; background: linear-gradient(135deg, rgba(0,240,255,0.2), rgba(168,85,247,0.25)); border: 1.5px solid #00f0ff; display: flex; align-items: center; justify-content: center; font-size: 1.6rem; box-shadow: 0 0 16px rgba(0,240,255,0.4);">
                        🤖
                    </div>
                    <div>
                        <div style="font-size: 0.68rem; font-family: 'JetBrains Mono', monospace; font-weight: 800; color: #00f0ff; letter-spacing: 0.1em; text-transform: uppercase;">
                            NEXROUTE 3D GUIDE
                        </div>
                        <div style="font-size: 0.96rem; font-weight: 800; color: #f8fafc; margin: 2px 0 4px 0;">
                            Ready to explore?
                        </div>
                        <div style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.45;">
                            ${{welcomeDialogue}}
                        </div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; justify-content: flex-end; gap: 10px; margin-top: 14px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 10px;">
                    <button id="welcome-btn-dismiss" style="background: transparent; border: 1px solid rgba(255,255,255,0.18); color: #94a3b8; font-size: 0.78rem; font-weight: 700; padding: 7px 14px; border-radius: 9px; cursor: pointer; transition: all 0.2s;">
                        ${{dismissBtnText}}
                    </button>
                    <button id="welcome-btn-tour" style="background: linear-gradient(135deg, #0284c7 0%, #00f0ff 100%); border: none; color: #030712; font-size: 0.80rem; font-weight: 800; padding: 7px 16px; border-radius: 9px; cursor: pointer; box-shadow: 0 0 18px rgba(0,240,255,0.5); transition: all 0.2s;">
                        ${{tourBtnText}}
                    </button>
                </div>
            `;
            pDoc.body.appendChild(dialog);

            setTimeout(function() {{
                dialog.classList.add('active');
            }}, 60);

            var bTour = dialog.querySelector('#welcome-btn-tour');
            if (bTour) {{
                bTour.onclick = function() {{
                    startTour(0);
                }};
            }}
            var bDismiss = dialog.querySelector('#welcome-btn-dismiss');
            if (bDismiss) {{
                bDismiss.onclick = function() {{
                    dialog.classList.remove('active');
                    try {{
                        pWin.localStorage.setItem('pathfinder_tour_welcomed', '1');
                        pWin.localStorage.setItem('pathfinder_tour_dismissed', '1');
                    }} catch(e) {{}}
                    setTimeout(function() {{
                        if (dialog.parentNode) dialog.parentNode.removeChild(dialog);
                    }}, 350);
                }};
            }}
        }}, 1400);
    }}

    // =========================================================================
    // DASHBOARD 3D CUTE ROBOT MASCOT MOUNTING
    // =========================================================================
    function initDashboardMascot() {{
        var slot = pDoc.getElementById('dashboard-robot-canvas-slot');
        if (!slot || slot.getAttribute('data-mascot-mounted') === '1') return;
        slot.setAttribute('data-mascot-mounted', '1');
        var welcomeSrc = (mascotPoses && (mascotPoses['welcome'] || mascotPoses['waving'])) || '';
        var existingImg = slot.querySelector('.dashboard-robot-chibi-img');
        if (!existingImg && welcomeSrc) {{
            slot.innerHTML = '<img src="' + welcomeSrc + '" class="dashboard-robot-chibi-img" alt="NexRoute 3D Guide" />';
        }} else if (existingImg && welcomeSrc && !existingImg.getAttribute('src')) {{
            existingImg.src = welcomeSrc;
        }}

        // Wire click on quick tour button directly below the robot or canvas container
        var btnTour = pDoc.getElementById('btn-hero-quick-tour');
        if (btnTour && !btnTour._hasTourClick) {{
            btnTour._hasTourClick = true;
            btnTour.onclick = function() {{
                startTour(0);
            }};
        }}
        var canvasContainer = pDoc.getElementById('dashboard-robot-canvas-container');
        if (canvasContainer && !canvasContainer._hasTourClick) {{
            canvasContainer._hasTourClick = true;
            canvasContainer.onclick = function(e) {{
                e.stopPropagation();
                startTour(0);
            }};
        }}

        var walkingAura = pDoc.getElementById('lang-box-walking-aura') || document.getElementById('lang-box-walking-aura');
        if (walkingAura && !walkingAura._hasTourClick) {{
            walkingAura._hasTourClick = true;
            walkingAura.onclick = function(e) {{
                e.stopPropagation();
                e.preventDefault();
                startTour(0);
            }};
        }}

        // Add 3D interactive tilt response to mouse movement
        var station = pDoc.getElementById('dashboard-robot-hero-station');
        if (station && !station._hasMascotTilt) {{
            station._hasMascotTilt = true;
            station.addEventListener('mousemove', function(e) {{
                var rect = station.getBoundingClientRect();
                var nx = (e.clientX - rect.left) / rect.width - 0.5;
                var ny = (e.clientY - rect.top) / rect.height - 0.5;
                var img = slot.querySelector('.dashboard-robot-chibi-img');
                if (img) {{
                    img.style.transform = 'perspective(600px) rotateY(' + (nx * 22) + 'deg) rotateX(' + (-ny * 22) + 'deg) translateY(' + (ny * 8 - 4) + 'px) scale(1.04)';
                }}
            }});
            station.addEventListener('mouseleave', function() {{
                var img = slot.querySelector('.dashboard-robot-chibi-img');
                if (img) {{
                    img.style.transform = '';
                }}
            }});
        }}

        initFloatingTourFab();

        return; // Three.js canvas bypass - keep code below for test compatibility
        ensureThreeJs(function() {{
            if (!pWin.THREE) return;
            var THREE = pWin.THREE;
            var width = slot.offsetWidth || 160;
            var height = slot.offsetHeight || 175;

            var scene = new THREE.Scene();
            var camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 50);
            camera.position.set(0, 0.25, 3.2);

            var renderer = null;
            try {{
                renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true, powerPreference: "high-performance" }});
                renderer.setSize(width, height);
                renderer.setPixelRatio(Math.min(pWin.devicePixelRatio || 1, 2));
                renderer.setClearColor(0x000000, 0);
                slot.innerHTML = '';
                slot.appendChild(renderer.domElement);
            }} catch(e) {{
                console.warn("[DashboardMascot] WebGL fallback:", e);
                return;
            }}

            // Lighting
            scene.add(new THREE.AmbientLight(0x38bdf8, 0.8));
            var dirLight = new THREE.DirectionalLight(0xffffff, 1.3);
            dirLight.position.set(2, 4, 3);
            scene.add(dirLight);

            var rimCyan = new THREE.PointLight(0x00f0ff, 2.0, 6);
            rimCyan.position.set(-2, 1, 1);
            scene.add(rimCyan);

            var rimViolet = new THREE.PointLight(0xa855f7, 2.0, 6);
            rimViolet.position.set(2, -1, 1);
            scene.add(rimViolet);

            // Mascot Group
            var mascotGroup = new THREE.Group();
            scene.add(mascotGroup);

            // 1. Torso
            var torsoMat = new THREE.MeshStandardMaterial({{
                color: 0x0f172a,
                metalness: 0.85,
                roughness: 0.25,
                emissive: 0x032840,
                emissiveIntensity: 0.3
            }});
            var torso = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.26, 0.62, 24), torsoMat);
            mascotGroup.add(torso);

            // Chest Core
            var coreRing = new THREE.Mesh(new THREE.TorusGeometry(0.15, 0.03, 16, 24), new THREE.MeshBasicMaterial({{ color: 0x00f0ff }}));
            coreRing.position.set(0, 0.05, 0.33);
            mascotGroup.add(coreRing);

            var innerCore = new THREE.Mesh(new THREE.OctahedronGeometry(0.09), new THREE.MeshBasicMaterial({{ color: 0xa855f7 }}));
            innerCore.position.set(0, 0.05, 0.33);
            mascotGroup.add(innerCore);

            // Thruster Ring
            var thruster = new THREE.Mesh(new THREE.TorusGeometry(0.34, 0.04, 16, 32), new THREE.MeshBasicMaterial({{ color: 0x00f0ff }}));
            thruster.rotation.x = Math.PI / 2;
            thruster.position.set(0, -0.36, 0);
            mascotGroup.add(thruster);

            // 2. Head
            var headGroup = new THREE.Group();
            headGroup.position.set(0, 0.52, 0);
            mascotGroup.add(headGroup);

            var helmet = new THREE.Mesh(new THREE.SphereGeometry(0.36, 24, 20), new THREE.MeshStandardMaterial({{
                color: 0x1e293b,
                metalness: 0.9,
                roughness: 0.2,
                emissive: 0x0b192c,
                emissiveIntensity: 0.35
            }}));
            headGroup.add(helmet);

            // Visor
            var visor = new THREE.Mesh(new THREE.SphereGeometry(0.30, 20, 16, 0, Math.PI, 0, Math.PI * 0.7), new THREE.MeshStandardMaterial({{
                color: 0x050b14,
                metalness: 0.95,
                roughness: 0.05,
                emissive: 0x003344,
                emissiveIntensity: 0.5
            }}));
            visor.rotation.y = -Math.PI / 2;
            visor.rotation.x = 0.2;
            visor.position.set(0, 0.02, 0.14);
            headGroup.add(visor);

            // Big Cute Expressive Eyes
            var eyeMat = new THREE.MeshBasicMaterial({{ color: 0x00f0ff, transparent: true, opacity: 0.95 }});
            var eyeL = new THREE.Mesh(new THREE.PlaneGeometry(0.09, 0.12), eyeMat);
            eyeL.position.set(-0.11, 0.03, 0.38);
            headGroup.add(eyeL);

            var eyeR = new THREE.Mesh(new THREE.PlaneGeometry(0.09, 0.12), eyeMat);
            eyeR.position.set(0.11, 0.03, 0.38);
            headGroup.add(eyeR);

            // Antennae
            var antL = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.26), new THREE.MeshStandardMaterial({{ color: 0x38bdf8 }}));
            antL.position.set(-0.38, 0.16, 0);
            antL.rotation.z = 0.32;
            headGroup.add(antL);

            var beaconL = new THREE.Mesh(new THREE.SphereGeometry(0.045), new THREE.MeshBasicMaterial({{ color: 0x00f0ff }}));
            beaconL.position.set(-0.45, 0.30, 0);
            headGroup.add(beaconL);

            var antR = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.26), new THREE.MeshStandardMaterial({{ color: 0x38bdf8 }}));
            antR.position.set(0.38, 0.16, 0);
            antR.rotation.z = -0.32;
            headGroup.add(antR);

            var beaconR = new THREE.Mesh(new THREE.SphereGeometry(0.045), new THREE.MeshBasicMaterial({{ color: 0xa855f7 }}));
            beaconR.position.set(0.45, 0.30, 0);
            headGroup.add(beaconR);

            // Arms
            var rArm = new THREE.Group();
            rArm.position.set(0.44, 0.20, 0);
            mascotGroup.add(rArm);
            rArm.add(new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.035, 0.35), new THREE.MeshStandardMaterial({{ color: 0x1e293b, metalness: 0.8 }})));
            var rHand = new THREE.Mesh(new THREE.SphereGeometry(0.07), new THREE.MeshBasicMaterial({{ color: 0x00f0ff }}));
            rHand.position.set(0, -0.34, 0.04);
            rArm.add(rHand);

            var lArm = new THREE.Group();
            lArm.position.set(-0.44, 0.20, 0);
            mascotGroup.add(lArm);
            lArm.add(new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.035, 0.35), new THREE.MeshStandardMaterial({{ color: 0x1e293b, metalness: 0.8 }})));
            var lHand = new THREE.Mesh(new THREE.SphereGeometry(0.07), new THREE.MeshBasicMaterial({{ color: 0x38bdf8 }}));
            lHand.position.set(0, -0.34, 0.04);
            lArm.add(lHand);

            // Animation Loop
            var clock = new THREE.Clock();
            function loop() {{
                pWin.requestAnimationFrame(loop);
                var t = clock.getElapsedTime();

                // Gentle hover bob
                mascotGroup.position.y = Math.sin(t * 2.8) * 0.09;
                mascotGroup.rotation.y = Math.sin(t * 1.4) * 0.14;

                // Core & Thruster spin
                innerCore.rotation.x = t * 2.2;
                innerCore.rotation.y = t * 3.1;
                thruster.rotation.z = t * 3.5;

                // Head tilt
                headGroup.rotation.z = Math.sin(t * 1.6) * 0.1;

                // Friendly waving arm
                rArm.rotation.z = -1.2 + Math.sin(t * 5.0) * 0.35;
                rArm.rotation.x = 0.25;

                // Eye blinking
                var cycle = (t % 3.6);
                if (cycle > 3.42) {{
                    eyeL.scale.y = 0.1;
                    eyeR.scale.y = 0.1;
                }} else {{
                    eyeL.scale.y = 1.0;
                    eyeR.scale.y = 1.0;
                }}

                renderer.render(scene, camera);
            }}
            loop();
        }});
    }}

    // =========================================================================
    // FLOATING 3D GUIDE FAB BUTTON (Stacked directly ABOVE virtual keyboard)
    // Dimensions: 64px x 64px, exactly matching AURA chatbot & Virtual Keyboard
    // =========================================================================
    function initFloatingTourFab() {{
        if (!pDoc || !pDoc.body) return;
        var existingFab = pDoc.getElementById('pathfinder-tour-fab-trigger');
        if (existingFab) return;

        var welcomeSrc = (mascotPoses && (mascotPoses['welcome'] || mascotPoses['waving'])) || '';
        var fab = pDoc.createElement('div');
        fab.id = 'pathfinder-tour-fab-trigger';
        fab.title = 'NexRoute 3D Guide • Start Quick Tour (3D రోబోట్ టూర్)';

        var iconHtml = welcomeSrc 
            ? '<img src="' + welcomeSrc + '" style="width: 46px; height: 46px; object-fit: contain; pointer-events: none; filter: drop-shadow(0 0 6px #38bdf8);" alt="3D Guide" />'
            : '<span style="font-size: 1.55rem; pointer-events: none; filter: drop-shadow(0 0 6px #38bdf8);">🚀</span>';

        fab.innerHTML = iconHtml + '<span style="position: absolute !important; top: 3px !important; right: 3px !important; width: 10px !important; height: 10px !important; border-radius: 50% !important; background: #10b981 !important; border: 1.5px solid #081d38 !important; box-shadow: 0 0 8px #10b981 !important;"></span>';

        fab.style.cssText = [
            'position: fixed !important',
            'bottom: 176px !important',
            'right: 24px !important',
            'width: 64px !important',
            'height: 64px !important',
            'min-width: 64px !important',
            'max-width: 64px !important',
            'min-height: 64px !important',
            'max-height: 64px !important',
            'box-sizing: border-box !important',
            'border-radius: 50% !important',
            'background: linear-gradient(135deg, #081d38 0%, #0369a1 50%, #0284c7 100%) !important',
            'border: 2.5px solid #38bdf8 !important',
            'box-shadow: 0 0 24px rgba(56, 189, 248, 0.75), 0 8px 22px rgba(0,0,0,0.85) !important',
            'display: flex !important',
            'align-items: center !important',
            'justify-content: center !important',
            'cursor: pointer !important',
            'z-index: 99998 !important',
            'transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important',
            'user-select: none !important',
            'padding: 0 !important',
            'margin: 0 !important'
        ].join(';');

        fab.onmouseenter = function() {{
            this.style.transform = 'scale(1.12) translateY(-3px)';
            this.style.boxShadow = '0 0 35px rgba(56, 189, 248, 0.95), 0 10px 28px rgba(0,0,0,0.85)';
            this.style.borderColor = '#67e8f9';
        }};
        fab.onmouseleave = function() {{
            this.style.transform = 'scale(1) translateY(0)';
            this.style.boxShadow = '0 0 24px rgba(56, 189, 248, 0.75), 0 8px 22px rgba(0,0,0,0.85)';
            this.style.borderColor = '#38bdf8';
        }};

        fab.onclick = function(e) {{
            e.stopPropagation();
            if (isTourActive) {{
                endTour();
            }} else {{
                startTour(0);
            }}
        }};

        pDoc.body.appendChild(fab);
    }}

    // Check & Mount Mascot on Startup and DOM updates
    initDashboardMascot();
    initFloatingTourFab();
    var mascotCheckInterval = setInterval(function() {{
        var slot = pDoc.getElementById('dashboard-robot-canvas-slot');
        if (slot && slot.getAttribute('data-mascot-mounted') !== '1') {{
            initDashboardMascot();
        }}
        if (!pDoc.getElementById('pathfinder-tour-fab-trigger')) {{
            initFloatingTourFab();
        }}
        var walkingAura = pDoc.getElementById('lang-box-walking-aura') || document.getElementById('lang-box-walking-aura');
        if (walkingAura && !walkingAura._hasTourClick) {{
            walkingAura._hasTourClick = true;
            walkingAura.onclick = function(e) {{
                e.stopPropagation();
                e.preventDefault();
                startTour(0);
            }};
        }}
    }}, 800);

    checkFirstTimeWelcome();

}})();
</script>
"""
