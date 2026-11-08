"""
NexRoute — AURA JARVIS-Style Welcome Screen & Autonomous Voice Assistant Activation
Provides a futuristic startup welcome experience with animated circular AURA avatar,
ambient cyan/electric-blue particle aura, real-time waveform visualizer,
Web Speech API speech synthesis & recognition, multilingual time-aware greetings,
autoplay restriction resilience, and instant command dispatching to the application.
"""

import json
import datetime
from typing import Optional, Dict, Any


def get_aura_startup_greeting(lang: str = "en", user_name: str = "Boss") -> str:
    """
    Returns a contextual, time-aware welcoming greeting in the chosen language.
    """
    now_hour = datetime.datetime.now().hour
    if 5 <= now_hour < 12:
        tod = "morning"
    elif 12 <= now_hour < 17:
        tod = "afternoon"
    elif 17 <= now_hour < 22:
        tod = "evening"
    else:
        tod = "night"

    greetings_map = {
        "en": {
            "morning": f"Good morning, {user_name}! Welcome to NexRoute. I'm AURA, your intelligent travel assistant. Where shall we explore today?",
            "afternoon": f"Good afternoon, {user_name}! Welcome back to NexRoute. I'm AURA, your personal route copilot. Ready for your next journey?",
            "evening": f"Good evening, {user_name}! Welcome to NexRoute. I'm AURA, your intelligent travel assistant. What should I do for you today?",
            "night": f"Hello, {user_name}! Welcome to NexRoute. I'm AURA, your intelligent travel assistant. What should I do for you tonight?"
        },
        "te": {
            "morning": f"శుభోదయం, {user_name}! నెక్స్‌రూట్‌కి స్వాగతం. నేను AURA, మీ ఇంటెలిజెంట్ ట్రావెల్ అసిస్టెంట్. ఈరోజు మనం ఎక్కడికి వెళ్దాం?",
            "afternoon": f"నమస్కారం, {user_name}! నెక్స్‌రూట్‌కి స్వాగతం. నేను AURA, మీ ప్రయాణ సహచరిని. మీ తదుపరి ప్రయాణానికి సిద్ధమా?",
            "evening": f"శుభ సాయంత్రం, {user_name}! నెక్స్‌రూట్‌కి స్వాగతం. నేను AURA, మీ స్మార్ట్ గైడ్. ఈరోజు నేను మీకు ఎలా సహాయపడగలను?",
            "night": f"నమస్కారం, {user_name}! నెక్స్‌రూట్‌కి స్వాగతం. నేను AURA. మీ రాత్రి ప్రయాణానికి రూట్ సిద్ధం చేయమంటారా?"
        },
        "hi": {
            "morning": f"सुप्रभात, {user_name}! नेक्स-रूट में आपका स्वागत है। मैं AURA हूँ, आपका स्मार्ट यात्रा सहायक। आज हम कहाँ चलें?",
            "afternoon": f"नमस्ते, {user_name}! नेक्स-रूट में आपका स्वागत है। मैं AURA हूँ। क्या आप अपनी अगली यात्रा के लिए तैयार हैं?",
            "evening": f"शुभ संध्या, {user_name}! नेक्स-रूट में आपका स्वागत है। मैं AURA हूँ। आज मैं आपके लिए क्या कर सकता हूँ?",
            "night": f"नमस्ते, {user_name}! नेक्स-रूट में आपका स्वागत है। मैं AURA हूँ। आपकी यात्रा को सुरक्षित और तेज़ बनाने के लिए तैयार हूँ।"
        },
        "ta": {
            "morning": f"காலை வணக்கம், {user_name}! நெக்ஸ்-ரூட்டிற்கு நல்வரவு. நான் AURA, உங்கள் பயண வழிகாட்டி. இன்று எங்கு செல்லலாம்?",
            "afternoon": f"வணக்கம், {user_name}! நெக்ஸ்-ரூட்டிற்கு நல்வரவு. நான் AURA. உங்கள் அடுத்த பயணத்திற்கு தயாரா?",
            "evening": f"மாலை வணக்கம், {user_name}! நெக்స్-ரூட்டிற்கு நல்வரவு. நான் AURA. இன்று நான் என்ன செய்ய வேண்டும்?",
            "night": f"வணக்கம், {user_name}! நெக்ஸ்-ரூட்டிற்கு நல்வரவு. நான் AURA. உங்கள் பயணத்திற்கு உதவ காத்திருக்கிறேன்."
        },
        "kn": {
            "morning": f"ಶುಭೋದಯ, {user_name}! ನೆಕ್ಸ್-ರೂಟ್‌ಗೆ ಸುಸ್ವಾಗತ. ನಾನು AURA, ನಿಮ್ಮ ಸ್ಮಾರ್ಟ್ ಪ್ರಯಾಣ ಸಹಾಯಕ.",
            "afternoon": f"ನಮಸ್ಕಾರ, {user_name}! ನೆಕ್ಸ್-ರೂಟ್‌ಗೆ ಸುಸ್ವಾಗತ. ನಾನು AURA, ನಿಮ್ಮ ಮುಂದಿನ ಪ್ರಯಾಣಕ್ಕೆ ಸಿದ್ಧರಿದ್ದೀರಾ?",
            "evening": f"ಶುಭ ಸಂಜೆ, {user_name}! ನೆಕ್ಸ್-ರೂಟ್‌ಗೆ ಸುಸ್ವಾಗತ. ನಾನು AURA. ಇಂದು ನಾನು ನಿಮಗಾಗಿ ಏನು ಮಾಡಬೇಕು?",
            "night": f"ನಮಸ್ಕಾರ, {user_name}! ನೆಕ್ಸ್-ರೂಟ್‌ಗೆ ಸುಸ್ವಾಗತ. ನಾನು AURA, ನಿಮ್ಮ ಪ್ರಯಾಣ ಸುಖಕರವಾಗಿರಲಿ."
        },
        "ml": {
            "morning": f"സുപ്രഭാതം, {user_name}! നെക്സ്-റൂട്ടിലേക്ക് സ്വാഗതം. ഞാൻ AURA, നിങ്ങളുടെ സ്മാർട്ട് യാത്രാ സഹായി.",
            "afternoon": f"നമസ്കാരം, {user_name}! നെക്സ്-റൂട്ടിലേക്ക് സ്വാഗതം. ഞാൻ AURA, യാത്രാവിവരങ്ങൾ പങ്കുവെക്കാം.",
            "evening": f"ശുഭ സായാഹ്നം, {user_name}! നെക്സ്-റൂട്ടിലേക്ക് സ്വാഗതം. ഞാൻ AURA. എന്ത് സഹായമാണ് വേണ്ടത്?",
            "night": f"നമസ്കാരം, {user_name}! നെക്സ്-റൂട്ടിലേക്ക് സ്വാഗതം. ഞാൻ AURA, രാത്രിയാത്രകൾ സുരക്ഷിതമാക്കാം."
        }
    }

    lang_bundle = greetings_map.get(lang, greetings_map["en"])
    return lang_bundle.get(tod, greetings_map["en"]["morning"])


def render_aura_welcome_hud(
    current_lang: str = "en",
    auto_speak: bool = True,
    bot_logo_uri: Optional[str] = None,
    user_name: str = "Boss"
) -> str:
    """
    Renders the futuristic JARVIS-style welcome screen HTML component with
    interactive particle canvas, audio waveform visualizer, responsive speech engine,
    and instantaneous Streamlit application command routing.
    """
    greeting_text = get_aura_startup_greeting(current_lang, user_name)

    bcp47_map = {
        "en": "en-IN",
        "te": "te-IN",
        "hi": "hi-IN",
        "ta": "ta-IN",
        "kn": "kn-IN",
        "ml": "ml-IN",
        "es": "es-ES",
        "fr": "fr-FR",
        "de": "de-DE",
        "ja": "ja-JP"
    }
    bcp47_code = bcp47_map.get(current_lang, "en-IN")

    avatar_markup = (
        f'<img src="{bot_logo_uri}" class="avatar-core-img" alt="AURA Mascot" />'
        if bot_logo_uri
        else '<div class="avatar-core-disc">⚡</div>'
    )

    return f"""<!DOCTYPE html>
<html lang="{current_lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700;800&display=swap');

    * {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
        user-select: none;
    }}

    body {{
        background: transparent;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #f8fafc;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 10px;
        min-height: 440px;
        overflow: hidden;
    }}

    /* Futuristic HUD Glassmorphism Card */
    .aura-welcome-panel {{
        position: relative;
        width: 100%;
        max-width: 820px;
        background: radial-gradient(circle at 50% 15%, rgba(14, 28, 54, 0.94) 0%, rgba(3, 7, 18, 0.98) 100%);
        border: 1.5px solid rgba(0, 240, 255, 0.38);
        border-radius: 22px;
        padding: 24px 28px;
        box-shadow: 0 16px 50px rgba(0, 0, 0, 0.8), 0 0 32px rgba(0, 240, 255, 0.18);
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        backdrop-filter: blur(20px);
        overflow: hidden;
    }}

    /* Top Corner Holographic Accents */
    .aura-welcome-panel::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #00f0ff 50%, transparent 100%);
        opacity: 0.85;
    }}

    /* Header Bar: Brand + Quick Dismiss */
    .welcome-top-row {{
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }}

    .brand-pill {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(0, 240, 255, 0.10);
        border: 1px solid rgba(0, 240, 255, 0.35);
        border-radius: 9999px;
        padding: 4px 14px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 800;
        color: #00f0ff;
        letter-spacing: 0.08em;
    }}

    .brand-pulse-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00f0ff;
        box-shadow: 0 0 10px #00f0ff;
        animation: dotGlow 1.4s infinite ease-in-out;
    }}

    @keyframes dotGlow {{
        0%, 100% {{ transform: scale(0.9); opacity: 0.6; }}
        50% {{ transform: scale(1.3); opacity: 1; box-shadow: 0 0 16px #00f0ff; }}
    }}

    .status-badge {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.70rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        color: #34d399;
        letter-spacing: 0.06em;
        transition: all 0.3s ease;
    }}

    /* Arc Reactor Circular Assistant Avatar */
    .avatar-wrapper {{
        position: relative;
        width: 96px;
        height: 96px;
        margin: 4px 0 14px 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .arc-reactor-ring-outer {{
        position: absolute;
        inset: -6px;
        border-radius: 50%;
        border: 1.5px dashed rgba(0, 240, 255, 0.45);
        animation: spinClockwise 14s linear infinite;
    }}

    .arc-reactor-ring-mid {{
        position: absolute;
        inset: -1px;
        border-radius: 50%;
        border: 2px solid rgba(56, 189, 248, 0.6);
        box-shadow: 0 0 24px rgba(0, 240, 255, 0.35);
        animation: ringPulse 2.4s infinite ease-in-out;
    }}

    .avatar-core-circle {{
        width: 76px;
        height: 76px;
        border-radius: 50%;
        background: radial-gradient(circle, #0284c7 0%, #030712 90%);
        border: 2px solid #00f0ff;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.6);
        z-index: 2;
        overflow: hidden;
    }}

    .avatar-core-img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
    }}

    .avatar-core-disc {{
        font-size: 32px;
        color: #00f0ff;
        filter: drop-shadow(0 0 8px #00f0ff);
    }}

    @keyframes spinClockwise {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}

    @keyframes ringPulse {{
        0%, 100% {{ transform: scale(0.98); opacity: 0.7; }}
        50% {{ transform: scale(1.05); opacity: 1; }}
    }}

    /* Title & Spoken Greeting Headline */
    .greeting-headline {{
        font-size: 1.25rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.01em;
        line-height: 1.45;
        max-width: 680px;
        margin-bottom: 12px;
        text-shadow: 0 2px 14px rgba(0, 240, 255, 0.25);
    }}

    .greeting-subtext {{
        font-size: 0.82rem;
        color: #94a3b8;
        margin-bottom: 16px;
        max-width: 600px;
        line-height: 1.5;
    }}

    /* Audio Waveform Canvas */
    .waveform-container {{
        width: 100%;
        max-width: 480px;
        height: 38px;
        background: rgba(3, 7, 18, 0.6);
        border: 1px solid rgba(0, 240, 255, 0.22);
        border-radius: 12px;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }}

    #auraWaveCanvas {{
        width: 100%;
        height: 100%;
    }}

    /* Primary Action Buttons */
    .action-buttons-row {{
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        justify-content: center;
        margin-bottom: 18px;
    }}

    .btn-aura-primary {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #00f0ff 0%, #0284c7 100%);
        color: #030712;
        font-weight: 800;
        font-size: 0.88rem;
        padding: 10px 22px;
        border-radius: 9999px;
        border: none;
        cursor: pointer;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.45);
        transition: all 0.25s ease;
    }}

    .btn-aura-primary:hover {{
        transform: translateY(-2px) scale(1.03);
        box-shadow: 0 0 30px rgba(0, 240, 255, 0.75);
    }}

    .btn-aura-secondary {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(15, 23, 42, 0.85);
        color: #38bdf8;
        font-weight: 700;
        font-size: 0.86rem;
        padding: 10px 20px;
        border-radius: 9999px;
        border: 1px solid rgba(56, 189, 248, 0.4);
        cursor: pointer;
        transition: all 0.25s ease;
    }}

    .btn-aura-secondary:hover {{
        background: rgba(56, 189, 248, 0.16);
        border-color: #00f0ff;
        color: #ffffff;
        transform: translateY(-2px);
    }}

    .btn-aura-skip {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: transparent;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.84rem;
        padding: 10px 18px;
        border-radius: 9999px;
        border: 1px solid rgba(148, 163, 184, 0.25);
        cursor: pointer;
        transition: all 0.2s ease;
    }}

    .btn-aura-skip:hover {{
        background: rgba(255, 255, 255, 0.08);
        color: #f1f5f9;
        border-color: rgba(255, 255, 255, 0.4);
    }}

    /* Quick Voice Chips Row */
    .quick-chips-grid {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        max-width: 740px;
        margin-top: 4px;
    }}

    .chip-item {{
        background: rgba(15, 23, 42, 0.80);
        border: 1px solid rgba(56, 189, 248, 0.28);
        border-radius: 8px;
        padding: 5px 12px;
        font-size: 0.74rem;
        font-weight: 600;
        color: #cbd5e1;
        cursor: pointer;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }}

    .chip-item:hover {{
        background: rgba(0, 240, 255, 0.16);
        border-color: #00f0ff;
        color: #ffffff;
        transform: translateY(-1px);
    }}

    /* Control Toolbar (Auto-greeting switch + Mute) */
    .controls-toolbar {{
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 18px;
        padding-top: 14px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        font-size: 0.74rem;
        color: #64748b;
    }}

    .switch-label {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        color: #94a3b8;
    }}

    .switch-label input {{
        cursor: pointer;
        accent-color: #00f0ff;
    }}

    .live-transcript-box {{
        margin-top: 10px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.76rem;
        color: #38bdf8;
        min-height: 20px;
        line-height: 1.4;
    }}
</style>
</head>
<body>

<div class="aura-welcome-panel" id="welcomePanel">
    <!-- Top Row -->
    <div class="welcome-top-row">
        <div class="brand-pill">
            <span class="brand-pulse-dot"></span>
            AURA • JARVIS AI COPILOT
        </div>
        <div class="status-badge" id="statusBadge">
            ● IDLE • READY
        </div>
    </div>

    <!-- Animated Arc Reactor Avatar -->
    <div class="avatar-wrapper" onclick="startVoiceRecognition()">
        <div class="arc-reactor-ring-outer"></div>
        <div class="arc-reactor-ring-mid" id="avatarMidRing"></div>
        <div class="avatar-core-circle">
            {avatar_markup}
        </div>
    </div>

    <!-- Spoken Greeting Headline -->
    <h1 class="greeting-headline" id="greetingHeadline">
        "{greeting_text}"
    </h1>
    <p class="greeting-subtext">
        Natural voice-controlled travel platform. Say a command or select an option below to begin your journey.
    </p>

    <!-- Synchronized Audio Waveform Visualizer -->
    <div class="waveform-container">
        <canvas id="auraWaveCanvas"></canvas>
    </div>

    <!-- Live Transcript / Assistant Speech Box -->
    <div class="live-transcript-box" id="transcriptBox">
        Ready for voice interaction, Boss.
    </div>

    <!-- Primary Action Buttons -->
    <div class="action-buttons-row">
        <button class="btn-aura-primary" id="btnVoiceMic" onclick="startVoiceRecognition()">
            🎙️ Start Voice Command
        </button>
        <button class="btn-aura-secondary" id="btnPlayGreeting" onclick="playVoiceGreeting(true)">
            🔊 Play Greeting
        </button>
        <button class="btn-aura-skip" onclick="dismissWelcomeScreen()">
            🚀 Enter NexRoute
        </button>
    </div>

    <!-- Quick Voice Chips -->
    <div class="quick-chips-grid">
        <span class="chip-item" onclick="dispatchWelcomeCommand('Open navigation')">🧭 Open Navigation</span>
        <span class="chip-item" onclick="dispatchWelcomeCommand('Switch to satellite view')">🛰️ Satellite View</span>
        <span class="chip-item" onclick="dispatchWelcomeCommand('Show my current location')">📍 Current Location</span>
        <span class="chip-item" onclick="dispatchWelcomeCommand('Find hospitals nearby')">🏥 Find Hospitals</span>
        <span class="chip-item" onclick="dispatchWelcomeCommand('Find petrol stations nearby')">⛽ Fuel Stations</span>
        <span class="chip-item" onclick="dispatchWelcomeCommand('Fit route')">🔍 Fit Route</span>
        <span class="chip-item" onclick="dispatchWelcomeCommand('Calculate fuel expenses')">⛽ Calculate Fuel</span>
        <span class="chip-item" onclick="dispatchWelcomeCommand('Open chatbot')">💬 Open Chatbot</span>
    </div>

    <!-- Bottom Controls Toolbar -->
    <div class="controls-toolbar">
        <label class="switch-label">
            <input type="checkbox" id="chkAutoGreeting" onchange="toggleAutoGreetingPref(this.checked)" checked />
            Enable Automatic Voice Greeting on Startup
        </label>
        <div style="display: flex; gap: 12px; align-items: center;">
            <button onclick="stopAssistantSpeech()" style="background:transparent; border:none; color:#64748b; cursor:pointer; font-size:0.74rem;">
                🔇 Mute
            </button>
            <span style="color: #475569;">|</span>
            <button onclick="dismissWelcomeScreen()" style="background:transparent; border:none; color:#38bdf8; cursor:pointer; font-weight:700; font-size:0.74rem;">
                Skip to Dashboard →
            </button>
        </div>
    </div>
</div>

<script>
(function() {{
    var activeLang = {json.dumps(current_lang)};
    var bcp47Lang = {json.dumps(bcp47_code)};
    var autoSpeak = {json.dumps(bool(auto_speak))};
    var spokenGreeting = {json.dumps(greeting_text)};

    var isListening = false;
    var isSpeaking = false;
    var recognition = null;
    var synthesis = window.speechSynthesis;
    var currentUtterance = null;
    var canvas = document.getElementById('auraWaveCanvas');
    var ctx = canvas ? canvas.getContext('2d') : null;
    var animationId = null;

    // Load auto-greeting preference
    var savedAutoPref = localStorage.getItem('aura_auto_greeting_enabled');
    var autoPrefCheckbox = document.getElementById('chkAutoGreeting');
    if (savedAutoPref !== null && autoPrefCheckbox) {{
        autoPrefCheckbox.checked = (savedAutoPref === 'true');
    }}

    window.toggleAutoGreetingPref = function(enabled) {{
        localStorage.setItem('aura_auto_greeting_enabled', String(enabled));
        try {{
            var pWin = window.parent || window.top;
            if (pWin && pWin !== window) {{
                pWin.postMessage({{
                    type: 'AURA_AUTO_GREETING_PREF',
                    enabled: enabled
                }}, '*');
            }}
        }} catch(e) {{}}
    }};

    // UI Status Helpers
    function setAssistantState(state, message) {{
        var badge = document.getElementById('statusBadge');
        var midRing = document.getElementById('avatarMidRing');
        var transBox = document.getElementById('transcriptBox');
        if (transBox && message) transBox.innerText = message;

        if (state === 'listening') {{
            if (badge) {{
                badge.innerText = '🎙️ LISTENING, BOSS...';
                badge.style.background = 'rgba(0, 240, 255, 0.22)';
                badge.style.borderColor = '#00f0ff';
                badge.style.color = '#00f0ff';
            }}
            if (midRing) midRing.style.boxShadow = '0 0 35px #00f0ff';
        }} else if (state === 'speaking') {{
            if (badge) {{
                badge.innerText = '🔊 SPEAKING...';
                badge.style.background = 'rgba(56, 189, 248, 0.22)';
                badge.style.borderColor = '#38bdf8';
                badge.style.color = '#38bdf8';
            }}
            if (midRing) midRing.style.boxShadow = '0 0 30px #38bdf8';
        }} else if (state === 'processing') {{
            if (badge) {{
                badge.innerText = '⚡ EXECUTING COMMAND...';
                badge.style.background = 'rgba(168, 85, 247, 0.22)';
                badge.style.borderColor = '#a855f7';
                badge.style.color = '#c084fc';
            }}
            if (midRing) midRing.style.boxShadow = '0 0 30px #a855f7';
        }} else if (state === 'error') {{
            if (badge) {{
                badge.innerText = '⚠️ NOTICE';
                badge.style.background = 'rgba(239, 68, 68, 0.22)';
                badge.style.borderColor = '#ef4444';
                badge.style.color = '#f87171';
            }}
        }} else {{
            if (badge) {{
                badge.innerText = '● IDLE • READY';
                badge.style.background = 'rgba(16, 185, 129, 0.15)';
                badge.style.borderColor = '#10b981';
                badge.style.color = '#34d399';
            }}
            if (midRing) midRing.style.boxShadow = '0 0 20px rgba(0, 240, 255, 0.35)';
        }}
    }}

    // Waveform Animation Loop
    function resizeCanvas() {{
        if (!canvas) return;
        canvas.width = canvas.parentElement.clientWidth || 400;
        canvas.height = canvas.parentElement.clientHeight || 38;
    }}
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    var wavePhase = 0;
    function drawWave() {{
        if (!ctx || !canvas) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        var numPoints = 64;
        var step = canvas.width / numPoints;
        var midY = canvas.height / 2;

        var baseAmp = isSpeaking ? 14 : (isListening ? 10 : 3.5);
        var freq = isSpeaking ? 0.16 : (isListening ? 0.22 : 0.08);

        ctx.beginPath();
        ctx.strokeStyle = isSpeaking ? '#00f0ff' : (isListening ? '#38bdf8' : 'rgba(56, 189, 248, 0.45)');
        ctx.lineWidth = isSpeaking || isListening ? 2.5 : 1.5;
        ctx.shadowBlur = isSpeaking ? 16 : (isListening ? 12 : 4);
        ctx.shadowColor = '#00f0ff';

        for (var i = 0; i <= numPoints; i++) {{
            var x = i * step;
            var envelope = Math.sin((i / numPoints) * Math.PI);
            var y = midY + Math.sin(i * freq + wavePhase) * (baseAmp * envelope);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }}
        ctx.stroke();

        wavePhase += isSpeaking ? 0.22 : (isListening ? 0.16 : 0.04);
        animationId = requestAnimationFrame(drawWave);
    }}
    drawWave();

    // Text-to-Speech Engine
    window.playVoiceGreeting = function(forced) {{
        if (!synthesis) return;
        try {{
            synthesis.cancel();
            var textToSpeak = spokenGreeting;
            currentUtterance = new SpeechSynthesisUtterance(textToSpeak);
            currentUtterance.lang = bcp47Lang;
            currentUtterance.rate = 1.0;
            currentUtterance.pitch = 1.02;

            currentUtterance.onstart = function() {{
                isSpeaking = true;
                setAssistantState('speaking', 'AURA: "' + textToSpeak + '"');
            }};

            currentUtterance.onend = function() {{
                isSpeaking = false;
                setAssistantState('idle', 'Awaiting your command, Boss.');
            }};

            currentUtterance.onerror = function(err) {{
                isSpeaking = false;
                setAssistantState('idle', 'Click "Play Greeting" or start voice command.');
            }};

            synthesis.speak(currentUtterance);
        }} catch(e) {{
            isSpeaking = false;
            setAssistantState('idle');
        }}
    }};

    window.stopAssistantSpeech = function() {{
        if (synthesis) synthesis.cancel();
        isSpeaking = false;
        setAssistantState('idle', 'Audio muted.');
    }};

    // Voice Command Dispatching (Executes Real Streamlit Application Actions)
    window.dispatchWelcomeCommand = function(cmdText) {{
        if (!cmdText || !cmdText.trim()) return;
        setAssistantState('processing', 'Executing command: "' + cmdText + '"');

        // 1. PostMessage to Parent Application
        try {{
            var pWin = window.parent || window.top;
            if (pWin && pWin !== window) {{
                pWin.postMessage({{
                    type: 'AURA_GLOBAL_VOICE_COMMAND',
                    command: cmdText.trim(),
                    lang: activeLang
                }}, '*');
            }}
        }} catch(ePost) {{}}

        // 2. Safely sync Streamlit Query Params to trigger backend action and close welcome HUD
        try {{
            var targetWin = window.parent || window.top || window;
            var currentHref = '';
            try {{ currentHref = targetWin.location.href; }} catch(e) {{ currentHref = window.location.href; }}
            var url = new URL(currentHref);
            url.searchParams.set('aura_cmd', cmdText.trim());
            url.searchParams.set('close_welcome', 'true');
            try {{
                targetWin.location.href = url.toString();
            }} catch(eNav) {{
                window.location.href = url.toString();
            }}
        }} catch(eParam) {{}}
    }};

    // Dismiss Welcome Screen without executing any command
    window.dismissWelcomeScreen = function() {{
        stopAssistantSpeech();
        try {{
            var pWin = window.parent || window.top;
            if (pWin && pWin !== window) {{
                pWin.postMessage({{ type: 'CLOSE_AURA_WELCOME' }}, '*');
            }}
        }} catch(e) {{}}

        try {{
            var targetWin = window.parent || window.top || window;
            var currentHref = '';
            try {{ currentHref = targetWin.location.href; }} catch(e) {{ currentHref = window.location.href; }}
            var url = new URL(currentHref);
            url.searchParams.set('close_welcome', 'true');
            try {{
                targetWin.location.href = url.toString();
            }} catch(eNav) {{
                window.location.href = url.toString();
            }}
        }} catch(eParam) {{}}
    }};

    // Voice Recognition (Speech-to-Text)
    window.startVoiceRecognition = function() {{
        stopAssistantSpeech();

        var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {{
            setAssistantState('error', 'Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.');
            return;
        }}

        if (isListening && recognition) {{
            try {{ recognition.stop(); }} catch(e) {{}}
            isListening = false;
            setAssistantState('idle', 'Listening cancelled.');
            return;
        }}

        try {{
            recognition = new SpeechRecognition();
            recognition.lang = bcp47Lang;
            recognition.continuous = false;
            recognition.interimResults = false;

            recognition.onstart = function() {{
                isListening = true;
                setAssistantState('listening', 'Listening, Boss... Speak your command now.');
            }};

            recognition.onresult = function(event) {{
                isListening = false;
                var transcript = event.results[0][0].transcript;
                if (transcript) {{
                    setAssistantState('processing', 'Heard: "' + transcript + '"');
                    dispatchWelcomeCommand(transcript);
                }}
            }};

            recognition.onerror = function(err) {{
                isListening = false;
                setAssistantState('error', 'Microphone error or permission denied. Please allow microphone access.');
            }};

            recognition.onend = function() {{
                isListening = false;
                if (!isSpeaking) setAssistantState('idle');
            }};

            recognition.start();
        }} catch(eStart) {{
            isListening = false;
            setAssistantState('error', 'Could not access microphone: ' + eStart.message);
        }}
    }};

    // Initial Startup Welcome Greeting Trigger (Autoplay safe)
    if (autoSpeak) {{
        setTimeout(function() {{
            var isPrefEnabled = (localStorage.getItem('aura_auto_greeting_enabled') !== 'false');
            if (isPrefEnabled) {{
                window.playVoiceGreeting(false);
            }}
        }}, 400);
    }}

}})();
</script>
</body>
</html>
"""
