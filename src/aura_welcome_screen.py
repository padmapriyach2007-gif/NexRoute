"""
NexRoute — AURA Autonomous JARVIS-Style Voice Assistant & Controller
Full real-time voice assistant engine providing:
1. Automatic time-appropriate greeting on launch with autoplay fallback.
2. Real-time microphone listening via Web Speech API (webkitSpeechRecognition) with continuous listening.
3. Audible SpeechSynthesis output with natural Jarvis pitch/rate and Chrome GC bug prevention.
4. Seamless React WebSocket communication bridge to Streamlit without disruptive browser page reloads.
5. Internal section navigation across Navigation, My Trips, Hotels, Flights, Restaurants, Profile, Settings, and Home.
6. Unified state management across both Main Dashboard and sub-navigation views.
"""

import json
import datetime
from typing import Optional, Dict, Any


def get_aura_startup_greeting(lang: str = "en", user_name: str = "Boss") -> str:
    """
    Returns the exact time-appropriate JARVIS greeting.
    - Morning (5:00 - 11:59): Good morning, Boss! Welcome to NexRoute. How can I help you?
    - Afternoon (12:00 - 16:59): Good afternoon, Boss! Welcome to NexRoute. How can I help you?
    - Evening (17:00 - 4:59): Good evening, Boss! Welcome to NexRoute. How can I help you?
    No extra promotional, tutorial, or introductory sentences.
    """
    now_hour = datetime.datetime.now().hour
    if 5 <= now_hour < 12:
        tod_en = "Good morning"
        tod_te = "శుభోదయం"
        tod_hi = "शुभ प्रभात"
        tod_ta = "காலை வணக்கம்"
        tod_kn = "ಶುಭೋದಯ"
        tod_ml = "സുപ്രഭാതം"
    elif 12 <= now_hour < 17:
        tod_en = "Good afternoon"
        tod_te = "నమస్కారం"
        tod_hi = "नमस्ते"
        tod_ta = "மதிய வணக்கம்"
        tod_kn = "ನಮಸ್ಕಾರ"
        tod_ml = "നമസ്കാരം"
    else:
        tod_en = "Good evening"
        tod_te = "శుభ సాయంత్రం"
        tod_hi = "शुभ संध्या"
        tod_ta = "மாலை வணக்கம்"
        tod_kn = "ಶುಭ ಸಂಜೆ"
        tod_ml = "ശുഭ സാయాഹ്നം"

    if lang == "te":
        return f"{tod_te}, {user_name}! నెక్స్‌రూట్‌కి స్వాగతం. నేను మీకు ఎలా సహాయపడగలను?"
    elif lang == "hi":
        return f"{tod_hi}, {user_name}! नेक्स्ट-रूट में आपका स्वागत है। मैं आपकी क्या मदद कर सकता हूँ?"
    elif lang == "ta":
        return f"{tod_ta}, {user_name}! நெக்ஸ்-ரூட்டிற்கு நல்வரவு. நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?"
    elif lang == "kn":
        return f"{tod_kn}, {user_name}! ನೆಕ್ಸ್-ರೂಟ್‌ಗೆ ಸುಸ್ವಾಗತ. ನಾನು మీకు ఎలా సహాయం చేయాలి?"
    elif lang == "ml":
        return f"{tod_ml}, {user_name}! നെക്സ്-റൂട്ടിലേക്ക് സ്വാഗതം. ഞാൻ എന്ത് സഹായമാണ് ചെയ്യേണ്ടത്?"
    else:
        return f"{tod_en}, {user_name}! Welcome to NextRoute. How can I help you?"


def render_aura_welcome_hud(
    current_lang: str = "en",
    auto_speak: bool = True,
    bot_logo_uri: Optional[str] = None,
    user_name: str = "Boss",
    compact: bool = False
) -> str:
    """
    Renders the autonomous JARVIS-style voice assistant HUD for NexRoute.
    Supports full mode (Main Dashboard hero panel) and compact mode (persistent navigation bar).
    Features real Web Speech API speech-to-text, SpeechSynthesis audio output, real-time waveform canvas,
    permission handling, zero-reload WebSocket command execution, and continuous conversational listening.
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
        else '<span style="color: #00f0ff; font-size: 24px; font-weight: 900;">⚡</span>'
    )

    if compact:
        # Sleek compact HUD for persistent voice control in sub-navigation views
        return f"""<!DOCTYPE html>
<html lang="{current_lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800&family=JetBrains+Mono:wght@600;700&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; user-select: none; }}
    body {{
        background: transparent;
        font-family: 'Inter', sans-serif;
        color: #f8fafc;
        padding: 2px 4px;
        overflow: hidden;
    }}
    .aura-compact-panel {{
        background: radial-gradient(circle at 15% 50%, rgba(14, 28, 54, 0.95) 0%, rgba(3, 7, 18, 0.98) 100%);
        border: 1.5px solid rgba(0, 240, 255, 0.35);
        border-radius: 14px;
        padding: 6px 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6), 0 0 16px rgba(0, 240, 255, 0.12);
        backdrop-filter: blur(12px);
    }}
    .avatar-pod {{
        position: relative;
        width: 36px;
        height: 36px;
        min-width: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }}
    .arc-spin-ring {{
        position: absolute;
        inset: -2px;
        border-radius: 50%;
        border: 1.5px dashed #00f0ff;
        animation: spinArc 10s linear infinite;
    }}
    @keyframes spinArc {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    .avatar-inner-circle {{
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: radial-gradient(circle, #0284c7 0%, #030712 100%);
        border: 1.5px solid #00f0ff;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }}
    .avatar-inner-circle img {{ width: 100%; height: 100%; object-fit: cover; }}
    .hud-center {{
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 2px;
        overflow: hidden;
    }}
    .hud-status-row {{
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .hud-status-badge {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.64rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 9999px;
        background: rgba(16, 185, 129, 0.18);
        border: 1px solid #10b981;
        color: #34d399;
        letter-spacing: 0.05em;
        white-space: nowrap;
    }}
    .hud-transcript-text {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.70rem;
        color: #38bdf8;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .hud-waveform {{
        width: 140px;
        height: 18px;
        min-width: 100px;
    }}
    #auraWaveCanvas {{ width: 100%; height: 100%; display: block; }}
</style>
</head>
<body>
<div class="aura-compact-panel">
    <div class="avatar-pod" onclick="window.AURA_TOGGLE_MIC()" title="Click to speak with AURA">
        <div class="arc-spin-ring"></div>
        <div class="avatar-inner-circle">{avatar_markup}</div>
    </div>
    <div class="hud-center">
        <div class="hud-status-row">
            <span style="font-weight: 800; font-size: 0.76rem; color: #f8fafc; letter-spacing: 0.04em;">AURA • JARVIS COPILOT</span>
            <span class="hud-status-badge" id="statusBadge">● IDLE • READY</span>
        </div>
        <div class="hud-transcript-text" id="transcriptBox">Voice navigation active. Speak anytime, Boss.</div>
    </div>
    <div class="hud-waveform">
        <canvas id="auraWaveCanvas"></canvas>
    </div>
</div>
{_build_jarvis_controller_script(current_lang, bcp47_code, auto_speak, greeting_text)}
</body>
</html>"""

    # Full Futuristic Holographic JARVIS Welcome HUD & Command Center for Main Dashboard
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
        padding: 4px;
        overflow: hidden;
    }}

    .aura-command-center {{
        position: relative;
        width: 100%;
        max-width: 880px;
        background: radial-gradient(ellipse 90% 70% at 50% 10%, rgba(14, 30, 68, 0.94) 0%, rgba(4, 9, 24, 0.98) 100%);
        border: 1.5px solid rgba(0, 240, 255, 0.32);
        border-radius: 22px;
        padding: 14px 22px 16px 22px;
        box-shadow: 0 16px 45px rgba(0, 0, 0, 0.85), 0 0 35px rgba(0, 240, 255, 0.14), inset 0 0 24px rgba(56, 189, 248, 0.05);
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        backdrop-filter: blur(24px);
        overflow: hidden;
    }}

    /* Futuristic Top Neon Edge Glow */
    .aura-command-center::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 8%;
        right: 8%;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #00f0ff 25%, #818cf8 50%, #00f0ff 75%, transparent 100%);
        opacity: 0.95;
        box-shadow: 0 0 12px #00f0ff;
    }}

    /* Subtle Holographic Grid Pattern */
    .holo-grid-overlay {{
        position: absolute;
        inset: 0;
        background-image: 
            linear-gradient(rgba(0, 240, 255, 0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 240, 255, 0.035) 1px, transparent 1px);
        background-size: 28px 28px;
        pointer-events: none;
        opacity: 0.7;
    }}

    /* Atmospheric Glow Behind Assistant */
    .holo-ambient-flare {{
        position: absolute;
        top: 35%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 320px;
        height: 180px;
        background: radial-gradient(circle, rgba(0, 240, 255, 0.16) 0%, rgba(129, 140, 248, 0.10) 45%, transparent 75%);
        filter: blur(36px);
        pointer-events: none;
        z-index: 1;
    }}

    /* 1. TOP COMMAND DECK */
    .command-top-row {{
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        position: relative;
        z-index: 2;
    }}

    .brand-cluster {{
        display: inline-flex;
        align-items: center;
        gap: 9px;
        text-align: left;
    }}

    .brand-compass-icon {{
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        filter: drop-shadow(0 0 8px rgba(0, 240, 255, 0.6));
    }}

    .brand-titles {{
        display: flex;
        flex-direction: column;
    }}

    .brand-nexroute-title {{
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        font-weight: 900;
        letter-spacing: 0.18em;
        background: linear-gradient(135deg, #ffffff 0%, #38bdf8 60%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.1;
    }}

    .brand-nexroute-sub {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.58rem;
        font-weight: 700;
        color: #38bdf8;
        letter-spacing: 0.12em;
        opacity: 0.85;
    }}

    .brand-pill {{
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: rgba(0, 240, 255, 0.08);
        border: 1px solid rgba(0, 240, 255, 0.32);
        border-radius: 9999px;
        padding: 3px 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        font-weight: 800;
        color: #00f0ff;
        letter-spacing: 0.08em;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.15);
    }}

    .status-badge {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid #475569;
        color: #94a3b8;
        letter-spacing: 0.05em;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
        white-space: nowrap;
    }}

    .status-badge.listening {{
        background: rgba(0, 240, 255, 0.22);
        border-color: #00f0ff;
        color: #00f0ff;
        box-shadow: 0 0 14px rgba(0, 240, 255, 0.45);
    }}

    .status-badge.thinking {{
        background: rgba(168, 85, 247, 0.22);
        border-color: #a855f7;
        color: #c084fc;
        box-shadow: 0 0 14px rgba(168, 85, 247, 0.45);
    }}

    .status-badge.speaking {{
        background: rgba(56, 189, 248, 0.22);
        border-color: #38bdf8;
        color: #38bdf8;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.45);
    }}

    .status-badge.paused {{
        background: rgba(245, 158, 11, 0.22);
        border-color: #f59e0b;
        color: #fbbf24;
        box-shadow: 0 0 14px rgba(245, 158, 11, 0.45);
    }}

    .status-badge.offline {{
        background: rgba(239, 68, 68, 0.16);
        border-color: #ef4444;
        color: #f87171;
    }}

    /* Smart Persistent Session Toggle Controls */
    .top-right-controls {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }}

    .btn-session-main {{
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.22) 0%, rgba(2, 132, 199, 0.40) 100%);
        border: 1.5px solid #00f0ff;
        border-radius: 9999px;
        padding: 3px 12px;
        color: #00f0ff;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.67rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        white-space: nowrap;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.35);
        transition: all 0.2s ease;
    }}

    .btn-session-main:hover {{
        transform: translateY(-1px) scale(1.04);
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.70);
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.35) 0%, rgba(2, 132, 199, 0.55) 100%);
    }}

    .btn-session-main.pause {{
        border-color: #f59e0b;
        color: #fbbf24;
        background: rgba(245, 158, 11, 0.22);
        box-shadow: 0 0 12px rgba(245, 158, 11, 0.35);
    }}

    .btn-session-main.resume {{
        border-color: #10b981;
        color: #34d399;
        background: rgba(16, 185, 129, 0.22);
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.35);
    }}

    .btn-session-end {{
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.45);
        border-radius: 9999px;
        padding: 3px 9px;
        color: #f87171;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        font-weight: 700;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 3px;
        white-space: nowrap;
        transition: all 0.2s ease;
    }}

    .btn-session-end:hover {{
        background: rgba(239, 68, 68, 0.30);
        color: #ffffff;
        border-color: #ef4444;
        box-shadow: 0 0 14px rgba(239, 68, 68, 0.45);
    }}

    /* 2. CENTRAL HOLOGRAPHIC AI REACTOR AVATAR */
    .avatar-stage {{
        position: relative;
        width: 104px;
        height: 104px;
        margin: 2px 0 6px 0;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 2;
    }}

    .arc-reactor-ring-outer {{
        position: absolute;
        inset: -10px;
        border-radius: 50%;
        border: 1.5px dashed rgba(0, 240, 255, 0.5);
        animation: spinClockwise 18s linear infinite;
        box-shadow: 0 0 18px rgba(0, 240, 255, 0.2);
    }}

    .telemetry-ring-segments {{
        position: absolute;
        inset: -4px;
        border-radius: 50%;
        border: 1.5px dotted rgba(129, 140, 248, 0.6);
        animation: spinCounterClockwise 12s linear infinite;
    }}

    .arc-reactor-ring-mid {{
        position: absolute;
        inset: 1px;
        border-radius: 50%;
        border: 2px solid rgba(56, 189, 248, 0.85);
        box-shadow: 0 0 24px rgba(0, 240, 255, 0.45);
        animation: reactorPulse 2.8s infinite ease-in-out;
        transition: all 0.35s ease;
    }}

    .avatar-core-circle {{
        width: 82px;
        height: 82px;
        border-radius: 50%;
        background: radial-gradient(circle at 50% 30%, #0369a1 0%, #0284c7 35%, #030712 90%);
        border: 2.2px solid #00f0ff;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 22px rgba(0, 240, 255, 0.7);
        z-index: 3;
        overflow: hidden;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}

    .avatar-stage:hover .avatar-core-circle {{
        transform: scale(1.04);
        box-shadow: 0 0 32px #00f0ff;
    }}

    .avatar-core-img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
    }}

    @keyframes spinClockwise {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}

    @keyframes spinCounterClockwise {{
        from {{ transform: rotate(360deg); }}
        to {{ transform: rotate(0deg); }}
    }}

    @keyframes reactorPulse {{
        0%, 100% {{ transform: scale(1); opacity: 0.85; }}
        50% {{ transform: scale(1.04); opacity: 1; box-shadow: 0 0 30px rgba(0, 240, 255, 0.65); }}
    }}

    /* 3. GREETING HEADLINE */
    .greeting-headline {{
        font-size: 1.12rem;
        font-weight: 800;
        color: #f8fafc;
        margin: 2px 0 2px 0;
        line-height: 1.35;
        letter-spacing: -0.01em;
        background: linear-gradient(135deg, #ffffff 0%, #38bdf8 55%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        z-index: 2;
    }}

    /* 4. WAVEFORM & LIVE TELEMETRY */
    .waveform-container {{
        width: 100%;
        max-width: 480px;
        height: 22px;
        margin: 2px 0 2px 0;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 2;
    }}

    #auraWaveCanvas {{
        width: 100%;
        height: 100%;
        display: block;
    }}

    .live-transcript-box {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #38bdf8;
        min-height: 18px;
        line-height: 1.35;
        letter-spacing: 0.02em;
        z-index: 2;
        margin-bottom: 8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 600px;
    }}

    /* 5. FLOATING GLASSMORPHISM SHORTCUT CARDS */
    .shortcut-cards-grid {{
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 8px;
        width: 100%;
        max-width: 840px;
        z-index: 2;
    }}

    .shortcut-card {{
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(56, 189, 248, 0.22);
        border-radius: 12px;
        padding: 7px 8px;
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        backdrop-filter: blur(12px);
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: left;
    }}

    .shortcut-card:hover {{
        background: rgba(20, 35, 68, 0.85);
        border-color: #00f0ff;
        box-shadow: 0 4px 16px rgba(0, 240, 255, 0.28), 0 0 10px rgba(0, 240, 255, 0.15);
        transform: translateY(-2.5px);
    }}

    .shortcut-icon-pod {{
        width: 26px;
        height: 26px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.95rem;
        border: 1px solid;
        flex-shrink: 0;
    }}

    .shortcut-info {{
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }}

    .shortcut-title {{
        font-size: 0.76rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.2;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .shortcut-hint {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.58rem;
        color: #94a3b8;
        line-height: 1.15;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    @media (max-width: 768px) {{
        .shortcut-cards-grid {{
            grid-template-columns: repeat(3, 1fr);
            gap: 6px;
        }}
        .brand-nexroute-title {{
            font-size: 0.85rem;
        }}
        .greeting-headline {{
            font-size: 1.0rem;
        }}
    }}

    @media (max-width: 480px) {{
        .shortcut-cards-grid {{
            grid-template-columns: repeat(2, 1fr);
            gap: 6px;
        }}
        .brand-nexroute-sub {{
            display: none;
        }}
    }}
</style>
</head>
<body>

<div class="aura-command-center" id="welcomePanel">
    <div class="holo-grid-overlay"></div>
    <div class="holo-ambient-flare"></div>

    <!-- 1. Top Command Deck Header -->
    <div class="command-top-row">
        <div class="brand-cluster">
            <div class="brand-compass-icon">
                <svg width="28" height="28" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="17" cy="17" r="15" stroke="url(#cGrad)" stroke-width="1.6" stroke-dasharray="3 3.5"/>
                    <circle cx="17" cy="17" r="9" stroke="rgba(0, 240, 255, 0.45)" stroke-width="1.2"/>
                    <polygon points="17,4 20.5,17 17,30 13.5,17" fill="url(#cGrad)" opacity="0.95"/>
                    <polygon points="17,4 20.5,17 17,17" fill="#ffffff" opacity="0.85"/>
                    <circle cx="17" cy="17" r="2.8" fill="#ffffff"/>
                    <defs>
                        <linearGradient id="cGrad" x1="0" y1="0" x2="34" y2="34" gradientUnits="userSpaceOnUse">
                            <stop offset="0%" stop-color="#00f0ff"/>
                            <stop offset="50%" stop-color="#38bdf8"/>
                            <stop offset="100%" stop-color="#818cf8"/>
                        </linearGradient>
                    </defs>
                </svg>
            </div>
            <div class="brand-titles">
                <span class="brand-nexroute-title">NEXROUTE</span>
                <span class="brand-nexroute-sub">AUTONOMOUS SATELLITE TRAVEL</span>
            </div>
        </div>

        <div class="brand-pill">
            AURA • JARVIS AI COPILOT
        </div>

        <div class="top-right-controls">
            <!-- Persistent Smart Voice Session Toggle -->
            <button class="btn-session-main start" id="btnSessionToggle" onclick="window.togglePersistentVoiceSession()" title="Start / Pause Continuous Voice Session">
                ▶ START AURA
            </button>
            <!-- End Session Button -->
            <button class="btn-session-end" id="btnEndSession" onclick="window.endVoiceSession()" style="display: none;" title="End Voice Session (Offline)">
                ⏹ END
            </button>
            <div class="status-badge offline" id="statusBadge">
                ● AURA OFFLINE
            </div>
        </div>
    </div>

    <!-- 2. Central Holographic AURA Avatar Reactor -->
    <div class="avatar-stage" onclick="window.togglePersistentVoiceSession()" title="Click to speak with AURA">
        <div class="arc-reactor-ring-outer"></div>
        <div class="telemetry-ring-segments"></div>
        <div class="arc-reactor-ring-mid" id="avatarMidRing"></div>
        <div class="avatar-core-circle">
            {avatar_markup}
        </div>
    </div>

    <!-- 3. Dynamic Welcome Greeting Headline -->
    <h1 class="greeting-headline" id="greetingHeadline">
        "{greeting_text}"
    </h1>

    <!-- 4. Real-Time Audio Waveform Canvas -->
    <div class="waveform-container">
        <canvas id="auraWaveCanvas"></canvas>
    </div>

    <!-- 5. Live Speech Transcript Pod -->
    <div class="live-transcript-box" id="transcriptBox">
        Ready for voice command, Boss. Speak anytime or tap a shortcut below.
    </div>

    <!-- 6. Floating Glassmorphism Navigation Shortcuts -->
    <div class="shortcut-cards-grid">
        <div class="shortcut-card" onclick="window.dispatchCardNav('Open navigation')" title="Jump to Navigation & Live Corridor Routing">
            <div class="shortcut-icon-pod" style="background: rgba(0, 240, 255, 0.14); border-color: #00f0ff; color: #00f0ff;">🧭</div>
            <div class="shortcut-info">
                <span class="shortcut-title">Navigation</span>
                <span class="shortcut-hint">Corridor Routing</span>
            </div>
        </div>
        <div class="shortcut-card" onclick="window.dispatchCardNav('Show my trips')" title="Open Autonomous Trips & Itineraries">
            <div class="shortcut-icon-pod" style="background: rgba(129, 140, 248, 0.14); border-color: #818cf8; color: #818cf8;">✈️</div>
            <div class="shortcut-info">
                <span class="shortcut-title">My Trips</span>
                <span class="shortcut-hint">Itinerary Studio</span>
            </div>
        </div>
        <div class="shortcut-card" onclick="window.dispatchCardNav('Show hotels')" title="Find Nearby Hotels & Accommodations">
            <div class="shortcut-icon-pod" style="background: rgba(245, 158, 11, 0.14); border-color: #f59e0b; color: #fbbf24;">🏨</div>
            <div class="shortcut-info">
                <span class="shortcut-title">Hotels</span>
                <span class="shortcut-hint">Stays & Resorts</span>
            </div>
        </div>
        <div class="shortcut-card" onclick="window.dispatchCardNav('Open flights')" title="Launch Flight Corridor Planner">
            <div class="shortcut-icon-pod" style="background: rgba(56, 189, 248, 0.14); border-color: #38bdf8; color: #38bdf8;">🛫</div>
            <div class="shortcut-info">
                <span class="shortcut-title">Flights</span>
                <span class="shortcut-hint">Air Corridors</span>
            </div>
        </div>
        <div class="shortcut-card" onclick="window.dispatchCardNav('Show restaurants')" title="Discover Food & Dining Along Route">
            <div class="shortcut-icon-pod" style="background: rgba(236, 72, 153, 0.14); border-color: #ec4899; color: #f472b6;">🍽️</div>
            <div class="shortcut-info">
                <span class="shortcut-title">Restaurants</span>
                <span class="shortcut-hint">Dining & Food</span>
            </div>
        </div>
        <div class="shortcut-card" onclick="window.dispatchCardNav('Go to my profile')" title="View Profile & Settings">
            <div class="shortcut-icon-pod" style="background: rgba(16, 185, 129, 0.14); border-color: #10b981; color: #34d399;">👤</div>
            <div class="shortcut-info">
                <span class="shortcut-title">Profile</span>
                <span class="shortcut-hint">User Account</span>
            </div>
        </div>
    </div>
</div>

{_build_jarvis_controller_script(current_lang, bcp47_code, auto_speak, greeting_text)}
</body>
</html>
"""


def _build_jarvis_controller_script(
    current_lang: str,
    bcp47_code: str,
    auto_speak: bool,
    greeting_text: str
) -> str:
    """
    Builds the JavaScript controller script that handles speech synthesis,
    speech recognition, continuous voice loop, voice activity detection,
    intelligent mid-speech interruption, and React WebSocket communication bridge to Streamlit.
    """
    return f"""
<script>
(function() {{
    var activeLang = {json.dumps(current_lang)};
    var bcp47Lang = {json.dumps(bcp47_code)};
    var shouldAutoSpeak = {json.dumps(bool(auto_speak))};
    var initialGreetingText = {json.dumps(greeting_text)};

    var pWin = window;
    var pDoc = document;
    try {{
        if (window.parent && window.parent !== window) {{
            var d = window.parent.document;
            if (d) {{
                pWin = window.parent;
                pDoc = d;
            }}
        }}
    }} catch(e) {{
        pWin = window;
        pDoc = document;
    }}

    // Central Persistent State: 'INACTIVE', 'LISTENING', 'PROCESSING', 'SPEAKING', 'PAUSED', 'STOPPED'
    var sessionState = localStorage.getItem('aura_persistent_voice_state') || (shouldAutoSpeak ? 'LISTENING' : 'INACTIVE');
    if (sessionState === 'SPEAKING' || sessionState === 'PROCESSING') {{
        sessionState = 'LISTENING';
    }}

    var isListening = false;
    var isSpeaking = false;
    var isProcessing = false;
    var recognition = null;
    var synthesis = null;
    try {{
        synthesis = (pWin && pWin.speechSynthesis) || window.speechSynthesis;
    }} catch(e) {{
        synthesis = window.speechSynthesis;
    }}

    var canvas = document.getElementById('auraWaveCanvas');
    var ctx = canvas ? canvas.getContext('2d') : null;
    var animationId = null;

    var silenceTimer = null;
    var vadTimeoutMs = 1400; // 1.4s silence threshold for natural speech
    var currentSpeechBuffer = '';
    var restartDebounceTimer = null;

    // UI Status & Control State Synchronization
    function updateUIForState(state, message) {{
        var badge = document.getElementById('statusBadge');
        var btnToggle = document.getElementById('btnSessionToggle');
        var btnEnd = document.getElementById('btnEndSession');
        var midRing = document.getElementById('avatarMidRing');
        var transBox = document.getElementById('transcriptBox');

        if (transBox && message) transBox.innerText = message;

        if (state === 'LISTENING') {{
            isListening = true;
            isSpeaking = false;
            isProcessing = false;
            if (badge) {{
                badge.className = 'status-badge listening';
                badge.innerText = '🎙️ LISTENING, BOSS...';
            }}
            if (btnToggle) {{
                btnToggle.className = 'btn-session-main pause';
                btnToggle.innerHTML = '⏸ PAUSE';
            }}
            if (btnEnd) btnEnd.style.display = 'inline-flex';
            if (midRing) midRing.style.boxShadow = '0 0 32px #00f0ff';
        }} else if (state === 'SPEAKING') {{
            isListening = false;
            isSpeaking = true;
            isProcessing = false;
            if (badge) {{
                badge.className = 'status-badge speaking';
                badge.innerText = '🔊 SPEAKING...';
            }}
            if (btnToggle) {{
                btnToggle.className = 'btn-session-main pause';
                btnToggle.innerHTML = '⏸ PAUSE';
            }}
            if (btnEnd) btnEnd.style.display = 'inline-flex';
            if (midRing) midRing.style.boxShadow = '0 0 28px #38bdf8';
        }} else if (state === 'PROCESSING') {{
            isListening = false;
            isSpeaking = false;
            isProcessing = true;
            if (badge) {{
                badge.className = 'status-badge thinking';
                badge.innerText = '⚡ THINKING...';
            }}
            if (btnToggle) {{
                btnToggle.className = 'btn-session-main pause';
                btnToggle.innerHTML = '⏸ PAUSE';
            }}
            if (btnEnd) btnEnd.style.display = 'inline-flex';
            if (midRing) midRing.style.boxShadow = '0 0 28px #a855f7';
        }} else if (state === 'PAUSED') {{
            isListening = false;
            isSpeaking = false;
            isProcessing = false;
            if (badge) {{
                badge.className = 'status-badge paused';
                badge.innerText = '⏸️ PAUSED';
            }}
            if (btnToggle) {{
                btnToggle.className = 'btn-session-main resume';
                btnToggle.innerHTML = '▶ RESUME';
            }}
            if (btnEnd) btnEnd.style.display = 'inline-flex';
            if (midRing) midRing.style.boxShadow = '0 0 16px rgba(245, 158, 11, 0.45)';
        }} else {{
            // STOPPED or INACTIVE
            isListening = false;
            isSpeaking = false;
            isProcessing = false;
            if (badge) {{
                badge.className = 'status-badge offline';
                badge.innerText = '● AURA OFFLINE';
            }}
            if (btnToggle) {{
                btnToggle.className = 'btn-session-main start';
                btnToggle.innerHTML = '▶ START AURA';
            }}
            if (btnEnd) btnEnd.style.display = 'none';
            if (midRing) midRing.style.boxShadow = '0 0 16px rgba(0, 240, 255, 0.35)';
        }}
    }}

    function setSessionState(newState, message) {{
        sessionState = newState;
        localStorage.setItem('aura_persistent_voice_state', newState);
        updateUIForState(newState, message);
    }}

    // Real-Time Canvas Waveform Animation
    function resizeCanvas() {{
        if (!canvas) return;
        canvas.width = canvas.parentElement.clientWidth || 360;
        canvas.height = canvas.parentElement.clientHeight || 24;
    }}
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    var wavePhase = 0;
    function drawWave() {{
        if (!ctx || !canvas) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        var numPoints = 48;
        var step = canvas.width / numPoints;
        var midY = canvas.height / 2;

        var baseAmp = isSpeaking ? 10 : (isListening ? 7 : (isProcessing ? 4.5 : 2.0));
        var freq = isSpeaking ? 0.18 : (isListening ? 0.24 : (isProcessing ? 0.36 : 0.08));

        ctx.beginPath();
        ctx.strokeStyle = isSpeaking ? '#00f0ff' : (isListening ? '#38bdf8' : (isProcessing ? '#c084fc' : 'rgba(100, 116, 139, 0.4)'));
        ctx.lineWidth = isSpeaking || isListening ? 2.2 : 1.4;
        ctx.shadowBlur = isSpeaking ? 14 : (isListening ? 10 : 2);
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

    // Universal Speech Synthesis Engine with Voices Cache
    function ensureVoices(callback) {{
        if (!synthesis) return callback([]);
        var voices = [];
        try {{ voices = synthesis.getVoices(); }} catch(e) {{}}
        if (voices && voices.length > 0) {{
            callback(voices);
        }} else {{
            var fired = false;
            var timer = setTimeout(function() {{
                if (!fired) {{
                    fired = true;
                    try {{ callback(synthesis.getVoices() || []); }} catch(e) {{ callback([]); }}
                }}
            }}, 250);
            try {{
                synthesis.onvoiceschanged = function() {{
                    if (!fired) {{
                        fired = true;
                        clearTimeout(timer);
                        callback(synthesis.getVoices() || []);
                    }}
                }};
            }} catch(e) {{}}
        }}
    }}

    // Voice Synthesis with Automatic Return to Listening Loop
    function speakJarvis(textToSpeak, onDone) {{
        if (!synthesis) {{
            if (onDone) onDone();
            return;
        }}
        try {{
            if (synthesis.speaking || synthesis.paused) {{
                try {{ synthesis.cancel(); }} catch(e) {{}}
            }}

            ensureVoices(function(voices) {{
                var utterance = new SpeechSynthesisUtterance(textToSpeak);
                utterance.lang = bcp47Lang;
                utterance.rate = 1.0;
                utterance.pitch = 1.02;

                if (voices && voices.length > 0) {{
                    var prefix = bcp47Lang.split('-')[0];
                    var voiceMatch = voices.find(function(v) {{ return v.lang === bcp47Lang; }}) ||
                                     voices.find(function(v) {{ return v.lang.startsWith(prefix); }});
                    if (voiceMatch) utterance.voice = voiceMatch;
                }}

                var doneHandled = false;
                function finishUtterance() {{
                    if (doneHandled) return;
                    doneHandled = true;
                    if (watchdogTimer) clearTimeout(watchdogTimer);
                    isSpeaking = false;
                    try {{ window.__AURA_CURRENT_UTTERANCE__ = null; }} catch(e) {{}}

                    if (onDone) onDone();

                    // AUTOMATIC RETURN TO LISTENING LOOP
                    if (sessionState !== 'PAUSED' && sessionState !== 'STOPPED' && sessionState !== 'INACTIVE') {{
                        setTimeout(function() {{
                            if (sessionState !== 'PAUSED' && sessionState !== 'STOPPED') {{
                                startVoiceListening();
                            }}
                        }}, 350); // 350ms delay to clear acoustic echo
                    }}
                }}

                var safetyTimeoutMs = Math.max(3200, (textToSpeak || '').length * 85);
                var watchdogTimer = setTimeout(function() {{
                    console.warn("[AURA] Speech synthesis timeout / watchdog reached.");
                    finishUtterance();
                }}, safetyTimeoutMs);

                utterance.onstart = function() {{
                    setSessionState('SPEAKING', 'AURA: "' + textToSpeak + '"');
                }};

                utterance.onend = function() {{
                    finishUtterance();
                }};

                utterance.onerror = function(err) {{
                    finishUtterance();
                }};

                try {{ window.__AURA_CURRENT_UTTERANCE__ = utterance; }} catch(e) {{}}

                if (synthesis.paused) {{
                    try {{ synthesis.resume(); }} catch(e) {{}}
                }}
                synthesis.speak(utterance);
            }});
        }} catch(e) {{
            isSpeaking = false;
            if (onDone) onDone();
        }}
    }}

    // Stop ongoing speech immediately
    function stopOngoingSpeech() {{
        if (synthesis) synthesis.cancel();
        isSpeaking = false;
    }}

    // Real-Time Speech Recognition Engine with VAD and Interruption
    function startVoiceListening() {{
        if (sessionState === 'PAUSED' || sessionState === 'STOPPED') return;

        var SpeechRec = null;
        try {{
            SpeechRec = (pWin && (pWin.SpeechRecognition || pWin.webkitSpeechRecognition)) ||
                        window.SpeechRecognition || window.webkitSpeechRecognition;
        }} catch(e) {{
            SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        }}

        if (!SpeechRec) {{
            setSessionState('INACTIVE', 'Speech recognition not supported in browser. Use Chrome or Edge.');
            return;
        }}

        if (recognition) {{
            try {{ recognition.abort(); }} catch(e) {{}}
            recognition = null;
        }}

        try {{
            recognition = new SpeechRec();
            recognition.lang = bcp47Lang;
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.maxAlternatives = 1;

            recognition.onstart = function() {{
                setSessionState('LISTENING', 'Listening, Boss... Speak your command.');
            }};

            recognition.onspeechstart = function() {{
                // INTELLIGENT INTERRUPTION: user started speaking while AURA is talking
                if (isSpeaking) {{
                    console.log("[AURA] User speech detected during TTS: interrupting immediately!");
                    stopOngoingSpeech();
                    setSessionState('LISTENING', 'Listening, Boss... Speak your command.');
                }}
            }};

            recognition.onresult = function(event) {{
                var interimTranscript = '';
                var finalTranscript = '';

                for (var i = event.resultIndex; i < event.results.length; ++i) {{
                    if (event.results[i].isFinal) {{
                        finalTranscript += event.results[i][0].transcript;
                    }} else {{
                        interimTranscript += event.results[i][0].transcript;
                    }}
                }}

                var rawText = (finalTranscript || interimTranscript || '').trim();
                var lowerText = rawText.toLowerCase();

                // INTELLIGENT INTERRUPTION CHECK: cancel ongoing audio immediately
                if (isSpeaking && rawText.length > 0) {{
                    console.log("[AURA] Voice interruption triggered:", rawText);
                    stopOngoingSpeech();
                    setSessionState('LISTENING', 'Listening, Boss... Speak your command.');

                    if (/^(wait|stop talking|hold on|listen to me|cancel that|be quiet|silence|pause)$/i.test(lowerText)) {{
                        currentSpeechBuffer = '';
                        var tBox = document.getElementById('transcriptBox');
                        if (tBox) tBox.innerText = 'Listening, Boss... Speak your command.';
                        return;
                    }}
                }}

                if (sessionState !== 'LISTENING') return;

                if (rawText.length > 0) {{
                    currentSpeechBuffer = rawText;
                    var tBox = document.getElementById('transcriptBox');
                    if (tBox) tBox.innerText = '🎙️ "' + rawText + '"';

                    if (silenceTimer) clearTimeout(silenceTimer);

                    // If final phrase received, check for voice commands like pause/resume/end
                    if (finalTranscript.trim().length > 0) {{
                        var finalCmd = finalTranscript.trim();
                        currentSpeechBuffer = '';

                        // Immediate local handling of Voice Session commands
                        if (/^(pause(\\s+the)?(\\s+voice)?(\\s+assistant)?|pause\\s+listening|hold\\s+on)$/i.test(finalCmd.toLowerCase())) {{
                            pauseVoiceSession();
                            return;
                        }}
                        if (/^(stop(\\s+the)?(\\s+voice)?(\\s+assistant)?|end\\s+session|aura\\s+offline|close\\s+assistant)$/i.test(finalCmd.toLowerCase())) {{
                            endVoiceSession();
                            return;
                        }}

                        // Submit to NexRoute engine
                        setSessionState('PROCESSING', 'YOU: "' + finalCmd + '"');
                        try {{ recognition.stop(); }} catch(e) {{}}
                        handleRecognizedVoiceCommand(finalCmd);
                    }} else {{
                        // VAD silence detection for interim speech
                        silenceTimer = setTimeout(function() {{
                            if (currentSpeechBuffer.length > 0 && sessionState === 'LISTENING') {{
                                var pendingText = currentSpeechBuffer;
                                currentSpeechBuffer = '';
                                setSessionState('PROCESSING', 'YOU: "' + pendingText + '"');
                                try {{ recognition.stop(); }} catch(e) {{}}
                                handleRecognizedVoiceCommand(pendingText);
                            }}
                        }}, vadTimeoutMs);
                    }}
                }}
            }};

            recognition.onerror = function(event) {{
                if (event.error === 'no-speech') {{
                    return;
                }} else if (event.error === 'not-allowed') {{
                    alert('Microphone blocked. Please allow mic permissions in your address bar.');
                    pauseVoiceSession();
                }} else if (event.error === 'network') {{
                    if (sessionState === 'LISTENING') {{
                        setTimeout(startVoiceListening, 1500);
                    }}
                }}
            }};

            recognition.onend = function() {{
                if (sessionState === 'LISTENING') {{
                    if (restartDebounceTimer) clearTimeout(restartDebounceTimer);
                    restartDebounceTimer = setTimeout(function() {{
                        if (sessionState === 'LISTENING') {{
                            try {{ recognition.start(); }} catch(e) {{}}
                        }}
                    }}, 250);
                }}
            }};

            recognition.start();
        }} catch(err) {{
            console.warn("[AURA] Could not start speech recognition:", err);
        }}
    }}

    // -------------------------------------------------------------------------
    // PERSISTENT SESSION CONTROLS: START, PAUSE, RESUME, END
    // -------------------------------------------------------------------------
    window.startVoiceSession = function() {{
        setSessionState('LISTENING');
        startVoiceListening();
    }};

    window.pauseVoiceSession = function() {{
        setSessionState('PAUSED', 'Voice session paused. Click RESUME to continue.');
        stopOngoingSpeech();
        if (recognition) {{
            try {{ recognition.abort(); }} catch(e) {{}}
        }}
        if (silenceTimer) clearTimeout(silenceTimer);
        currentSpeechBuffer = '';
    }};

    window.resumeVoiceSession = function() {{
        setSessionState('LISTENING', 'Listening, Boss... Speak your command.');
        startVoiceListening();
    }};

    window.endVoiceSession = function() {{
        setSessionState('STOPPED', 'AURA is offline. Click START AURA to begin voice session.');
        stopOngoingSpeech();
        if (recognition) {{
            try {{ recognition.abort(); }} catch(e) {{}}
            recognition = null;
        }}
        if (silenceTimer) clearTimeout(silenceTimer);
        currentSpeechBuffer = '';
    }};

    // Smart Toggle: Transitions through Inactive/Stopped -> Listening -> Paused -> Resume
    window.togglePersistentVoiceSession = function() {{
        if (sessionState === 'INACTIVE' || sessionState === 'STOPPED') {{
            startVoiceSession();
        }} else if (sessionState === 'LISTENING' || sessionState === 'PROCESSING' || sessionState === 'SPEAKING') {{
            pauseVoiceSession();
        }} else if (sessionState === 'PAUSED') {{
            resumeVoiceSession();
        }}
    }};

    // Backward-compatibility alias
    window.AURA_TOGGLE_MIC = window.togglePersistentVoiceSession;

    window.dispatchCardNav = function(phrase) {{
        stopOngoingSpeech();
        setSessionState('PROCESSING', 'Executing: ' + phrase);
        handleRecognizedVoiceCommand(phrase);
    }};

    // Zero-Reload WebSocket Command Execution Bridge to Streamlit
    function sendCommandToStreamlit(cmdText, cmdId) {{
        try {{
            var bridgeInput = pDoc.querySelector('input[aria-label="AURA_VOICE_COMMAND_BRIDGE"]') ||
                              pDoc.querySelector('input[data-testid*="aura_voice_cmd_sink"]');

            if (bridgeInput) {{
                var payload = JSON.stringify({{ id: cmdId, cmd: cmdText }});
                var nativeSetter = Object.getOwnPropertyDescriptor(pWin.HTMLInputElement.prototype, 'value')?.set ||
                                   Object.getOwnPropertyDescriptor(bridgeInput.__proto__, 'value')?.set;
                if (nativeSetter) {{
                    nativeSetter.call(bridgeInput, payload);
                }} else {{
                    bridgeInput.value = payload;
                }}
                bridgeInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                bridgeInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                bridgeInput.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }}));
                return true;
            }}
        }} catch(eBridge) {{
            console.warn("[AURA Bridge] React dispatch fallback:", eBridge);
        }}

        try {{
            var currentHref = '';
            try {{ currentHref = pWin.location.href; }} catch(e) {{ currentHref = window.location.href; }}
            var url = new URL(currentHref);
            url.searchParams.set('aura_cmd', cmdText);
            try {{
                pWin.location.href = url.toString();
            }} catch(eNav) {{
                window.location.href = url.toString();
            }}
        }} catch(eUrl) {{}}
        return false;
    }}

    // Real-Time Command Intent & Concise Confirmation Speech
    function handleRecognizedVoiceCommand(cmdText) {{
        isProcessing = true;
        setSessionState('PROCESSING', 'YOU: "' + cmdText + '"');

        var lower = cmdText.toLowerCase();
        var spokenResponse = "";

        // Exact Intent Mapping (from user specifications)
        if (lower.indexOf("navigation") !== -1 || lower.indexOf("nav") !== -1 || lower.indexOf("map") !== -1) {{
            spokenResponse = "Opening navigation.";
        }} else if (lower.indexOf("booking") !== -1 || lower.indexOf("reservation") !== -1) {{
            spokenResponse = "Opening your bookings.";
        }} else if (lower.indexOf("trip") !== -1 || lower.indexOf("copilot") !== -1 || lower.indexOf("itinerar") !== -1) {{
            spokenResponse = "Here are your trips.";
        }} else if (lower.indexOf("hotel") !== -1 || lower.indexOf("lodg") !== -1) {{
            spokenResponse = "Let's find hotels.";
        }} else if (lower.indexOf("flight") !== -1 || lower.indexOf("airplane") !== -1) {{
            spokenResponse = "Opening flight planner.";
        }} else if (lower.indexOf("restaurant") !== -1 || lower.indexOf("food") !== -1 || lower.indexOf("cafe") !== -1) {{
            spokenResponse = "Finding nearby restaurants.";
        }} else if (lower.indexOf("setting") !== -1 || lower.indexOf("preference") !== -1) {{
            spokenResponse = "Opening settings.";
        }} else if (lower.indexOf("profile") !== -1 || lower.indexOf("account") !== -1) {{
            spokenResponse = "Opening your profile.";
        }} else if (lower.indexOf("back") !== -1 || lower.indexOf("previous") !== -1) {{
            spokenResponse = "Going back.";
        }} else if (lower.indexOf("home") !== -1 || lower.indexOf("dashboard") !== -1) {{
            spokenResponse = "Returning to home dashboard.";
        }} else if (lower.indexOf("place") !== -1 || lower.indexOf("saved") !== -1 || lower.indexOf("sight") !== -1) {{
            spokenResponse = "Opening saved places.";
        }} else if (lower.indexOf("guide") !== -1) {{
            spokenResponse = "Opening virtual guide.";
        }} else if (lower.indexOf("chat") !== -1 || lower.indexOf("aura") !== -1) {{
            spokenResponse = "AURA chatbot is ready.";
        }} else if (lower.indexOf("satellite") !== -1) {{
            spokenResponse = "Switched to satellite view.";
        }} else if (lower.indexOf("hospital") !== -1) {{
            spokenResponse = "Locating hospitals and medical centers.";
        }} else if (lower.indexOf("petrol") !== -1 || lower.indexOf("fuel") !== -1) {{
            spokenResponse = "Locating fuel stations.";
        }} else if (lower.indexOf("where am i") !== -1 || lower.indexOf("location") !== -1) {{
            spokenResponse = "Locating your current coordinates.";
        }} else if (lower.indexOf("alternative") !== -1 || lower.indexOf("routes") !== -1) {{
            spokenResponse = "Showing alternative routes, Boss.";
        }} else if (lower.indexOf("bicycle") !== -1 || lower.indexOf("bike") !== -1 || lower.indexOf("car") !== -1) {{
            spokenResponse = "Updating transportation mode, Boss.";
        }} else {{
            spokenResponse = "Processing: " + cmdText.substring(0, 28);
        }}

        var cmdId = 'cmd_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5);

        // 1. Speak response aloud immediately (and auto return to listening on end)
        speakJarvis(spokenResponse, function() {{
            isProcessing = false;
        }});

        // 2. Simultaneously dispatch to Streamlit without reloading the page
        sendCommandToStreamlit(cmdText, cmdId);
    }}

    // Automatic Startup Greeting & Autoplay Unlock Fallback
    var greetingTriggered = false;
    var greetingActuallySpoken = false;

    function triggerStartupGreeting() {{
        if (greetingTriggered) return;

        var sessionKey = 'aura_session_greeted_' + activeLang;
        try {{
            if (sessionStorage.getItem(sessionKey) === 'true') {{
                greetingTriggered = true;
                if (sessionState === 'LISTENING') {{
                    setTimeout(startVoiceListening, 450);
                }}
                return;
            }}
        }} catch(e) {{}}

        if (!shouldAutoSpeak) {{
            greetingTriggered = true;
            if (sessionState === 'LISTENING') {{
                setTimeout(startVoiceListening, 450);
            }}
            return;
        }}

        greetingTriggered = true;
        try {{ sessionStorage.setItem(sessionKey, 'true'); }} catch(e) {{}}

        // Speak the natural initial greeting:
        // "Good morning, Boss! Welcome to NexRoute. How can I help you?"
        speakJarvis(initialGreetingText, function() {{
            greetingActuallySpoken = true;
            // Immediately after greeting finishes, activate microphone for voice commands!
            if (sessionState !== 'PAUSED' && sessionState !== 'STOPPED') {{
                setSessionState('LISTENING');
                setTimeout(startVoiceListening, 350);
            }}
        }});
    }}

    // Minimal first-interaction fallback (unblocks speech if browser blocks autoplay before user touch)
    function unlockAudioOnFirstInteraction() {{
        if (synthesis && synthesis.paused) {{
            try {{ synthesis.resume(); }} catch(e) {{}}
        }}
        if (!greetingActuallySpoken && shouldAutoSpeak) {{
            greetingActuallySpoken = true;
            speakJarvis(initialGreetingText, function() {{
                if (sessionState !== 'PAUSED' && sessionState !== 'STOPPED') {{
                    setSessionState('LISTENING');
                    setTimeout(startVoiceListening, 350);
                }}
            }});
        }} else if (sessionState === 'LISTENING' && !isListening && !isSpeaking) {{
            startVoiceListening();
        }}

        window.removeEventListener('click', unlockAudioOnFirstInteraction);
        window.removeEventListener('keydown', unlockAudioOnFirstInteraction);
        window.removeEventListener('touchstart', unlockAudioOnFirstInteraction);
        try {{
            pDoc.removeEventListener('click', unlockAudioOnFirstInteraction);
            pDoc.removeEventListener('keydown', unlockAudioOnFirstInteraction);
            pDoc.removeEventListener('touchstart', unlockAudioOnFirstInteraction);
        }} catch(e) {{}}
    }}

    window.addEventListener('click', unlockAudioOnFirstInteraction);
    window.addEventListener('keydown', unlockAudioOnFirstInteraction);
    window.addEventListener('touchstart', unlockAudioOnFirstInteraction);
    try {{
        pDoc.addEventListener('click', unlockAudioOnFirstInteraction);
        pDoc.addEventListener('keydown', unlockAudioOnFirstInteraction);
        pDoc.addEventListener('touchstart', unlockAudioOnFirstInteraction);
    }} catch(e) {{}}

    // Prompt microphone permissions explicitly on startup
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
        navigator.mediaDevices.getUserMedia({{ audio: true }})
            .then(function(stream) {{
                stream.getTracks().forEach(function(track) {{ track.stop(); }});
                setTimeout(triggerStartupGreeting, 300);
            }})
            .catch(function(err) {{
                console.warn("[AURA] Mic permission notice:", err);
                setTimeout(triggerStartupGreeting, 300);
            }});
    }} else {{
        setTimeout(triggerStartupGreeting, 300);
    }}

    // Initialize UI for current state
    updateUIForState(sessionState);

}})();
</script>
"""
