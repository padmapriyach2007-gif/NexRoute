"""
NexRoute — AURA Autonomous JARVIS-Style Voice Assistant & Controller
Full real-time voice assistant engine providing:
1. Automatic time-appropriate greeting on launch with autoplay fallback.
2. Real-time microphone listening via Web Speech API (webkitSpeechRecognition) with continuous listening.
3. Audible SpeechSynthesis output with natural Jarvis pitch/rate and Chrome GC bug prevention.
4. Seamless React WebSocket communication bridge to Streamlit without disruptive browser page reloads.
5. Internal section navigation across Navigation, Hotels, Flights, Restaurants, Profile, Settings, and Home.
6. Unified state management across both Main Dashboard and sub-navigation views.
"""

import json
import datetime
from typing import Optional, Dict, Any
from src.i18n import t


def get_aura_startup_greeting(lang: str = "en", user_name: str = "Boss") -> str:
    """
    Returns the exact time-appropriate JARVIS greeting based on local time:
    - Morning (5:00 - 11:59): Good morning, Boss! Welcome to NextRoute. How can I help you?
    - Afternoon (12:00 - 16:59): Good afternoon, Boss! Welcome to NextRoute. What can I do for you?
    - Evening (17:00 - 20:59): Good evening, Boss! Welcome to NextRoute. How can I help you?
    - Night (21:00 - 4:59): Hello, Boss! Welcome back to NextRoute. How can I assist you tonight?
    """
    now_hour = datetime.datetime.now().hour
    if 5 <= now_hour < 12:
        period = "morning"
    elif 12 <= now_hour < 17:
        period = "afternoon"
    elif 17 <= now_hour < 21:
        period = "evening"
    else:
        period = "night"

    greetings_table = {
        "en": {
            "morning": f"Good morning, {user_name}! Welcome to NextRoute. I'm AURA, your autonomous travel assistant. How can I help you?",
            "afternoon": f"Good afternoon, {user_name}! Welcome to NextRoute. I'm AURA, your autonomous travel assistant. What can I do for you?",
            "evening": f"Good evening, {user_name}! Welcome to NextRoute. I'm AURA, your autonomous travel assistant. How can I help you?",
            "night": f"Hello, {user_name}! Welcome back to NextRoute. I'm AURA, your autonomous travel assistant. How can I assist you tonight?"
        },
        "te": {
            "morning": f"శుభోదయం, {user_name}! నెక్స్‌రూట్‌కి స్వాగతం. నేను మీకు ఎలా సహాయపడగలను?",
            "afternoon": f"శుభ మధ్యాహ్నం, {user_name}! నెక్స్‌రూట్‌కి స్వాగతం. మీ కోసం నేను ఏమి చేయగలను?",
            "evening": f"శుభ సాయంత్రం, {user_name}! నెక్స్‌రూట్‌కి స్వాగతం. నేను మీకు ఎలా సహాయపడగలను?",
            "night": f"నమస్కారం, {user_name}! నెక్స్‌రూట్‌కి తిరిగి స్వాగతం. ఈ రాత్రి నేను మీకు ఎలా సహాయపడగలను?"
        },
        "hi": {
            "morning": f"शुभ प्रभात, {user_name}! नेक्स्ट-रूट में आपका स्वागत है। मैं आपकी क्या मदद कर सकता हूँ?",
            "afternoon": f"शुभ दोपहर, {user_name}! नेक्स्ट-रूट में आपका स्वागत है। मैं आपके लिए क्या कर सकता हूँ?",
            "evening": f"शुभ संध्या, {user_name}! नेक्स्ट-रूट में आपका स्वागत है। मैं आपकी क्या मदद कर सकता हूँ?",
            "night": f"नमस्ते, {user_name}! नेक्स्ट-रूट में पुनः स्वागत है। आज रात मैं आपकी क्या सहायता कर सकता हूँ?"
        },
        "ta": {
            "morning": f"காலை வணக்கம், {user_name}! நெக்ஸ்ட்-ரூட்டிற்கு நல்வரவு. நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?",
            "afternoon": f"மதிய வணக்கம், {user_name}! நெக்ஸ்ட்-ரூட்டிற்கு நல்வரவு. உங்களுக்காக நான் என்ன செய்ய முடியும்?",
            "evening": f"மாலை வணக்கம், {user_name}! நெக்ஸ்ட்-ரூட்டிற்கு நல்வரவு. நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?",
            "night": f"வணக்கம், {user_name}! நெக்ஸ்ட்-ரூட்டிற்கு மீண்டும் நல்வரவு. இன்று இரவு நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?"
        },
        "kn": {
            "morning": f"ಶುಭೋದಯ, {user_name}! ನೆಕ್ಸ್ಟ್‌-ರೂಟ್‌ಗೆ ಸುಸ್ವಾಗತ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?",
            "afternoon": f"ಶುಭ ಮಧ್ಯಾಹ್ನ, {user_name}! ನೆಕ್ಸ್ಟ್‌-ರೂಟ್‌ಗೆ ಸುಸ್ವಾಗತ. ನಿಮಗಾಗಿ ನಾನು ಏನು ಮಾಡಲಿ?",
            "evening": f"ಶುಭ ಸಂಜೆ, {user_name}! ನೆಕ್ಸ್ಟ್‌-ರೂಟ್‌ಗೆ ಸುಸ್ವಾಗತ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?",
            "night": f"ನಮಸ್ಕಾರ, {user_name}! ನೆಕ್ಸ್ಟ್‌-ರೂಟ್‌ಗೆ ಮತ್ತೆ ಸುಸ್ವಾಗತ. ಇಂದು ರಾತ್ರಿ ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?"
        },
        "ml": {
            "morning": f"സുപ്രഭാതം, {user_name}! നെക്സ്റ്റ്-റൂട്ടിലേക്ക് സ്വാഗതം. ഞാൻ എങ്ങനെ സഹായിക്കണം?",
            "afternoon": f"ശുഭ ഉച്ചതിരിഞ്ഞ്, {user_name}! നെക്സ്റ്റ്-റൂട്ടിലേക്ക് സ്വാഗതം. ഞാൻ എന്താണ് ചെയ്യേണ്ടത്?",
            "evening": f"ശുഭ സായാഹ്നം, {user_name}! നെക്സ്റ്റ്-റൂട്ടിലേക്ക് സ്വാഗതം. ഞാൻ എങ്ങനെ സഹായിക്കണം?",
            "night": f"ഹലോ, {user_name}! നെക്സ്റ്റ്-റൂട്ടിലേക്ക് വീണ്ടും സ്വാഗതം. ഇന്ന് രാത്രി ഞാൻ എങ്ങനെ സഹായിക്കണം?"
        },
        "bn": {
            "morning": f"সুপ্রভাত, {user_name}! নেক্সটরুটে স্বাগতম। আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
            "afternoon": f"শুভ অপরাহ্ন, {user_name}! নেক্সটরুটে স্বাগতম। আমি আপনার জন্য কি করতে পারি?",
            "evening": f"শুভ সন্ধ্যা, {user_name}! নেক্সটরুটে স্বাগতম। আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
            "night": f"হ্যালো, {user_name}! নেক্সটরুটে আবার স্বাগতম। আজ রাতে আমি আপনাকে কীভাবে সাহায্য করতে পারি?"
        },
        "mr": {
            "morning": f"शुभ सकाळ, {user_name}! नेक्स्ट-रूट मध्ये आपले स्वागत आहे. मी आपली काय मदत करू शकतो?",
            "afternoon": f"शुभ दुपार, {user_name}! नेक्स्ट-रूट मध्ये आपले स्वागत आहे. मी आपल्यासाठी काय करू शकतो?",
            "evening": f"शुभ संध्याकाळ, {user_name}! नेक्स्ट-रूट मध्ये आपले स्वागत आहे. मी आपली काय मदत करू शकतो?",
            "night": f"नमस्कार, {user_name}! नेक्स्ट-रूट मध्ये पुन्हा स्वागत आहे. आज रात्री मी आपली कशी मदत करू शकतो?"
        }
    }

    lang_map = greetings_table.get(lang, greetings_table["en"])
    return lang_map.get(period, lang_map["morning"])
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

    # Dynamic Multilingual Localization for all AURA HUD words & labels
    brand_title = t("aura.brand_title", default="NEXROUTE", lang=current_lang)
    txt_state_init = t("aura.state_initializing", default="● INITIALIZING", lang=current_lang)
    txt_state_greet = t("aura.state_greeting", default="● GREETING", lang=current_lang)
    txt_state_wake = t("aura.state_wake_standby", default="● WAKE-WORD STANDBY", lang=current_lang)
    txt_state_list = t("aura.state_listening", default="● LISTENING...", lang=current_lang)
    txt_state_silence = t("aura.state_silence_detected", default="● SILENCE DETECTED", lang=current_lang)
    txt_state_proc = t("aura.state_processing", default="● PROCESSING...", lang=current_lang)
    txt_state_spk = t("aura.state_speaking", default="● SPEAKING...", lang=current_lang)
    txt_state_err = t("aura.state_error", default="● ERROR", lang=current_lang)
    txt_state_stop = t("aura.state_stopped", default="● STOPPED", lang=current_lang)
    txt_mic_act = t("aura.mic_active", default="🎙️ MIC: ACTIVE", lang=current_lang)
    txt_mic_std = t("aura.mic_standby", default="🎙️ MIC: STANDBY", lang=current_lang)
    txt_mic_mut = t("aura.mic_muted", default="🔇 MIC: MUTED", lang=current_lang)
    txt_mic_den = t("aura.mic_denied", default="⚠️ MIC: DENIED", lang=current_lang)
    txt_prompt_wake = t("aura.prompt_wake_standby", default='Say "Hey AURA" or click avatar to speak...', lang=current_lang)
    txt_prompt_silence = t("aura.prompt_silence", default="Silence detected. Finalizing command...", lang=current_lang)
    txt_wake_ack = t("aura.wake_word_ack", default="Yes, Boss?", lang=current_lang)
    brand_sub = t("aura.brand_sub", default="AUTONOMOUS SATELLITE TRAVEL", lang=current_lang)
    brand_pill = t("aura.brand_pill", default="AURA", lang=current_lang)
    btn_start_txt = t("aura.btn_speak", default="🎙️ SPEAK", lang=current_lang)
    btn_end_txt = t("aura.btn_end", default="⏹ END", lang=current_lang)
    status_idle_txt = t("aura.status_idle", default="● IDLE • READY", lang=current_lang)
    transcript_ready_txt = t("aura.transcript_ready", default="Ready for your command, Boss. Speak anytime or select an orbital module.", lang=current_lang)

    nav_title = t("nav.module_title", default="Navigation", lang=current_lang)
    nav_sub = t("nav.module_sub", default="CORRIDOR ROUTING", lang=current_lang)
    hotels_title = t("hotels.module_title", default="Hotels", lang=current_lang)
    hotels_sub = t("hotels.module_sub", default="STAYS & RESORTS", lang=current_lang)
    flights_title = t("flights.module_title", default="Flights", lang=current_lang)
    flights_sub = t("flights.module_sub", default="AIR CORRIDORS", lang=current_lang)
    food_title = t("food.module_title", default="Restaurants", lang=current_lang)
    food_sub = t("food.module_sub", default="DINING & FOOD", lang=current_lang)

    bcp47_map = {
        "en": "en-IN",
        "te": "te-IN",
        "hi": "hi-IN",
        "ta": "ta-IN",
        "kn": "kn-IN",
        "ml": "ml-IN",
        "bn": "bn-IN",
        "mr": "mr-IN"
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
            <span style="font-weight: 800; font-size: 0.76rem; color: #f8fafc; letter-spacing: 0.04em;">AURA</span>
            <span class="hud-status-badge" id="statusBadge">{status_idle_txt}</span>
        </div>
        <div class="hud-transcript-text" id="transcriptBox">{transcript_ready_txt}</div>
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
        max-width: 100%;
        background: radial-gradient(ellipse 90% 70% at 50% 10%, rgba(14, 30, 68, 0.94) 0%, rgba(4, 9, 24, 0.98) 100%);
        border: 1.5px solid rgba(0, 240, 255, 0.32);
        border-radius: 22px;
        padding: 14px 20px 16px 20px;
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

    .status-badge.offline,
    .status-badge.stopped {{
        background: rgba(239, 68, 68, 0.16);
        border-color: #ef4444;
        color: #f87171;
    }}

    .status-badge.initializing {{
        background: rgba(14, 165, 233, 0.2);
        border-color: #0ea5e9;
        color: #38bdf8;
        box-shadow: 0 0 12px rgba(14, 165, 233, 0.4);
    }}

    .status-badge.greeting {{
        background: rgba(168, 85, 247, 0.22);
        border-color: #a855f7;
        color: #c084fc;
        box-shadow: 0 0 14px rgba(168, 85, 247, 0.45);
    }}

    .status-badge.wake-standby {{
        background: rgba(0, 240, 255, 0.14);
        border-color: #00f0ff;
        color: #38bdf8;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.3);
    }}

    .status-badge.silence-detected {{
        background: rgba(251, 191, 36, 0.2);
        border-color: #f59e0b;
        color: #fef08a;
        box-shadow: 0 0 14px rgba(245, 158, 11, 0.45);
    }}

    .status-badge.error {{
        background: rgba(239, 68, 68, 0.25);
        border-color: #ef4444;
        color: #fca5a5;
        box-shadow: 0 0 16px rgba(239, 68, 68, 0.55);
    }}

    /* Hardware Microphone Telemetry Pill */
    .mic-status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid #334155;
        color: #94a3b8;
        white-space: nowrap;
        transition: all 0.3s ease;
    }}

    .mic-status-pill.active {{
        border-color: #00f0ff;
        color: #00f0ff;
        background: rgba(0, 240, 255, 0.18);
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.35);
    }}

    .mic-status-pill.standby {{
        border-color: #38bdf8;
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.12);
    }}

    .mic-status-pill.muted {{
        border-color: #f59e0b;
        color: #fbbf24;
        background: rgba(245, 158, 11, 0.12);
    }}

    .mic-status-pill.denied {{
        border-color: #ef4444;
        color: #f87171;
        background: rgba(239, 68, 68, 0.2);
    }}

    .mic-indicator-dot {{
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: currentColor;
        display: inline-block;
    }}

    .mic-status-pill.active .mic-indicator-dot {{
        animation: blipPulse 1.1s infinite;
    }}

    /* 9-State Avatar Reactor Animation Classes */
    @keyframes avatarBreathing {{
        0%, 100% {{
            box-shadow: 0 0 18px rgba(0, 240, 255, 0.28);
            transform: scale(1);
        }}
        50% {{
            box-shadow: 0 0 34px rgba(0, 240, 255, 0.62);
            transform: scale(1.025);
        }}
    }}

    @keyframes pulseCyanWave {{
        0%, 100% {{
            box-shadow: 0 0 25px rgba(0, 240, 255, 0.7);
            transform: scale(1.015);
        }}
        50% {{
            box-shadow: 0 0 48px rgba(0, 240, 255, 0.95);
            transform: scale(1.055);
        }}
    }}

    @keyframes rotateDigitalRings {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}

    @keyframes voiceWaveModulation {{
        0%, 100% {{
            box-shadow: 0 0 22px rgba(56, 189, 248, 0.6);
            transform: scale(1.01);
        }}
        50% {{
            box-shadow: 0 0 42px rgba(56, 189, 248, 0.92);
            transform: scale(1.045);
        }}
    }}

    @keyframes errorWarningPulse {{
        0%, 100% {{
            box-shadow: 0 0 16px rgba(239, 68, 68, 0.4);
        }}
        50% {{
            box-shadow: 0 0 34px rgba(239, 68, 68, 0.88);
        }}
    }}

    .avatar-stage.state-initializing {{
        animation: avatarBreathing 2.5s ease-in-out infinite;
    }}

    .avatar-stage.state-greeting {{
        animation: voiceWaveModulation 1s ease-in-out infinite;
    }}

    .avatar-stage.state-wake-word-standby,
    .avatar-stage.state-wake_word_standby {{
        animation: avatarBreathing 3s ease-in-out infinite;
    }}

    .avatar-stage.state-listening {{
        animation: pulseCyanWave 1.2s ease-in-out infinite;
    }}

    .avatar-stage.state-silence-detected,
    .avatar-stage.state-silence_detected {{
        animation: avatarBreathing 1.2s ease-in-out infinite;
    }}

    .avatar-stage.state-processing .arc-reactor-ring-outer {{
        animation: rotateDigitalRings 0.9s linear infinite !important;
    }}

    .avatar-stage.state-speaking {{
        animation: voiceWaveModulation 0.8s ease-in-out infinite;
    }}

    .avatar-stage.state-error {{
        animation: errorWarningPulse 1.4s ease-in-out infinite;
    }}

    .avatar-stage.state-stopped {{
        opacity: 0.55;
    }}

    /* Smart Persistent Session Toggle Controls */
    .top-right-controls {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        flex-wrap: wrap;
        justify-content: flex-end;
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
        font-size: 1.08rem;
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
        max-width: 440px;
        height: 20px;
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
        font-size: 0.70rem;
        color: #38bdf8;
        min-height: 18px;
        line-height: 1.35;
        letter-spacing: 0.02em;
        z-index: 2;
        margin-bottom: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 520px;
    }}

    /* =========================================================================
       5. HOLOGRAPHIC AI TRAVEL COMMAND CENTER & ORBITAL NAVIGATION STAGE
       ========================================================================= */
    .holo-orbital-stage {{
        position: relative;
        width: 100%;
        max-width: 860px;
        min-height: 330px;
        height: 330px;
        margin-top: 2px;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 2;
    }}

    /* Ambient SVG Orbital Rings & Energy Beams Layer */
    .holo-orbital-svg {{
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 1;
        overflow: visible;
    }}

    .orbital-ring {{
        fill: none;
        stroke: rgba(0, 229, 255, 0.24);
        stroke-dasharray: 4 6;
        animation: rotateOrbitalRing 60s linear infinite;
        transform-origin: 440px 140px;
    }}

    .orbital-ring-mid {{
        fill: none;
        stroke: rgba(139, 92, 246, 0.18);
        stroke-dasharray: 3 9;
        animation: rotateOrbitalRingCounter 45s linear infinite;
        transform-origin: 440px 140px;
    }}

    .orbital-ring-outer {{
        fill: none;
        stroke: rgba(0, 255, 198, 0.12);
        stroke-dasharray: 6 12;
    }}

    @keyframes rotateOrbitalRing {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}

    @keyframes rotateOrbitalRingCounter {{
        from {{ transform: rotate(360deg); }}
        to {{ transform: rotate(0deg); }}
    }}

    /* SVG Energy Conduit Lines connecting Central AI to Modules */
    .energy-conduit-base {{
        fill: none;
        stroke: rgba(0, 229, 255, 0.16);
        stroke-width: 1.5;
        stroke-linecap: round;
        transition: all 0.3s ease;
    }}

    .energy-conduit-pulse {{
        fill: none;
        stroke-width: 2.2;
        stroke-linecap: round;
        stroke-dasharray: 8 20;
        animation: conduitStream 2.4s linear infinite;
        opacity: 0.75;
        transition: all 0.3s ease;
    }}

    @keyframes conduitStream {{
        from {{ stroke-dashoffset: 56; }}
        to {{ stroke-dashoffset: 0; }}
    }}

    .beam-active .energy-conduit-base {{
        stroke-width: 2.8;
        opacity: 1;
        filter: drop-shadow(0 0 8px #00e5ff);
    }}

    .beam-active .energy-conduit-pulse {{
        stroke-width: 3.5;
        opacity: 1;
        stroke-dasharray: 12 12;
        animation-duration: 1.2s;
    }}

    /* Central AURA Node in Command Stage */
    .aura-center-node {{
        position: absolute;
        left: 50%;
        top: 40%;
        transform: translate(-50%, -50%);
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        z-index: 5;
        pointer-events: auto;
    }}

    /* Container for Modules */
    .holo-modules-container {{
        position: contents;
    }}

    /* Floating Holographic Travel Modules */
    .holo-module-node {{
        position: absolute;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 8px 14px 8px 10px;
        background: rgba(6, 16, 31, 0.82);
        border: 1.2px solid rgba(0, 229, 255, 0.32);
        border-radius: 9999px;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.65), 0 0 16px rgba(0, 229, 255, 0.12), inset 0 0 10px rgba(0, 229, 255, 0.05);
        cursor: pointer;
        z-index: 6;
        transition: all 0.28s cubic-bezier(0.2, 0.8, 0.2, 1);
        text-decoration: none;
    }}

    .holo-module-node:hover {{
        transform: translateY(-4px) scale(1.06);
        border-color: #00e5ff;
        background: rgba(10, 25, 52, 0.94);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.8), 0 0 24px rgba(0, 229, 255, 0.45), inset 0 0 14px rgba(0, 255, 198, 0.2);
    }}

    .holo-module-node.active-node {{
        border-color: #00ffc6;
        background: rgba(4, 30, 50, 0.96);
        box-shadow: 0 0 28px rgba(0, 255, 198, 0.65);
    }}

    /* Distinct Position Coordinates - Symmetrical 4-Quadrant Orbital Matrix */
    .node-nav {{
        left: clamp(15px, 4%, 45px);
        top: 24px;
        --node-glow: #00e5ff;
        border-color: rgba(0, 229, 255, 0.38);
    }}
    .node-nav:hover {{
        border-color: #00e5ff;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.8), 0 0 24px rgba(0, 229, 255, 0.5);
    }}

    .node-hotels {{
        right: clamp(15px, 4%, 45px);
        top: 24px;
        --node-glow: #f59e0b;
        border-color: rgba(245, 158, 11, 0.38);
    }}
    .node-hotels:hover {{
        border-color: #fbbf24;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.8), 0 0 24px rgba(245, 158, 11, 0.5);
    }}

    .node-flights {{
        right: clamp(15px, 4%, 45px);
        bottom: 24px;
        --node-glow: #00ffc6;
        border-color: rgba(0, 255, 198, 0.38);
    }}
    .node-flights:hover {{
        border-color: #00ffc6;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.8), 0 0 24px rgba(0, 255, 198, 0.5);
    }}

    .node-food {{
        left: clamp(15px, 4%, 45px);
        bottom: 24px;
        --node-glow: #ec4899;
        border-color: rgba(236, 72, 153, 0.38);
    }}
    .node-food:hover {{
        border-color: #f472b6;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.8), 0 0 24px rgba(236, 72, 153, 0.5);
    }}

    /* Icon Glyphs */
    .holo-glyph-disc {{
        position: relative;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: radial-gradient(circle, rgba(15, 23, 42, 0.9) 0%, rgba(2, 8, 18, 0.95) 100%);
        border: 1.4px solid currentColor;
        box-shadow: 0 0 12px rgba(0, 0, 0, 0.5);
        flex-shrink: 0;
        transition: all 0.25s ease;
    }}

    .holo-module-node:hover .holo-glyph-disc {{
        transform: scale(1.08);
        box-shadow: 0 0 16px currentColor;
    }}

    .holo-glyph-reticle {{
        position: absolute;
        inset: -3px;
        border-radius: 50%;
        border: 1px dashed currentColor;
        opacity: 0.45;
        animation: spinGlyphReticle 10s linear infinite;
    }}

    @keyframes spinGlyphReticle {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}

    /* Text Telemetry */
    .holo-node-meta {{
        display: flex;
        flex-direction: column;
        text-align: left;
    }}

    .holo-node-title {{
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.15;
        letter-spacing: 0.02em;
    }}

    .holo-node-sub {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.56rem;
        font-weight: 700;
        color: #38bdf8;
        letter-spacing: 0.06em;
        line-height: 1.15;
    }}

    .holo-status-blip {{
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: #00ffc6;
        box-shadow: 0 0 6px #00ffc6;
        margin-left: 2px;
        animation: blipPulse 1.8s infinite ease-in-out;
    }}

    @keyframes blipPulse {{
        0%, 100% {{ opacity: 0.4; transform: scale(0.9); }}
        50% {{ opacity: 1; transform: scale(1.2); }}
    }}

    /* =========================================================================
       COMPREHENSIVE RESPONSIVE DESIGN (ALL MOBILES, TABLETS & FOLDABLES)
       Supports: Ultra-compact (320px–375px), Standard (376px–480px),
       Phablets/Foldables (481px–768px), and Tablets (769px–820px)
       ========================================================================= */
    @media (max-width: 820px) {{
        .aura-command-center {{
            padding: 12px 14px 16px 14px;
            border-radius: 18px;
        }}

        .command-top-row {{
            flex-wrap: wrap;
            gap: 8px;
            justify-content: space-between;
            align-items: center;
        }}

        .brand-cluster {{
            flex: 0 1 auto;
        }}

        .top-right-controls {{
            flex: 0 0 auto;
            gap: 6px;
        }}

        .brand-pill {{
            order: 3;
            width: 100%;
            justify-content: center;
            margin-top: 4px;
            font-size: 0.64rem;
            padding: 3px 8px;
        }}

        .holo-orbital-stage {{
            height: auto;
            min-height: unset;
            display: flex;
            flex-direction: column;
            gap: 12px;
            padding: 4px 0;
        }}

        .holo-orbital-svg {{
            display: none;
        }}

        .aura-center-node {{
            position: relative;
            left: unset;
            top: unset;
            transform: none;
            margin: 0 auto 6px auto;
        }}

        .holo-modules-container {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 8px;
            width: 100%;
            box-sizing: border-box;
        }}

        .holo-module-node {{
            position: relative;
            left: unset !important;
            right: unset !important;
            top: unset !important;
            bottom: unset !important;
            transform: none !important;
            width: 100% !important;
            min-width: 0 !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
            padding: 8px 10px !important;
            gap: 8px !important;
            border-radius: 14px !important;
            touch-action: manipulation !important;
            -webkit-tap-highlight-color: transparent !important;
        }}

        .btn-session-main {{
            min-height: 38px;
            padding: 4px 11px;
            font-size: 0.65rem;
            touch-action: manipulation;
        }}

        .btn-session-end {{
            min-height: 38px;
            padding: 4px 9px;
            font-size: 0.64rem;
            touch-action: manipulation;
        }}
    }}

    @media (max-width: 540px) {{
        .aura-command-center {{
            padding: 10px 10px 14px 10px;
            border-radius: 16px;
        }}
        .brand-compass-icon {{
            width: 26px;
            height: 26px;
        }}
        .brand-compass-icon svg {{
            width: 26px;
            height: 26px;
        }}
        .brand-nexroute-title {{
            font-size: 0.82rem;
            letter-spacing: 0.12em;
        }}
        .brand-nexroute-sub {{
            display: none;
        }}
        .greeting-headline {{
            font-size: 0.88rem;
            line-height: 1.35;
        }}
        .live-transcript-box {{
            font-size: 0.72rem;
            padding: 6px 10px;
            max-width: 100%;
        }}
        .holo-module-node {{
            padding: 6px 8px !important;
            gap: 6px !important;
            border-radius: 12px !important;
        }}
        .holo-glyph-disc {{
            width: 28px !important;
            height: 28px !important;
            min-width: 28px !important;
        }}
        .holo-glyph-disc svg {{
            width: 16px !important;
            height: 16px !important;
        }}
        .holo-node-title {{
            font-size: 0.74rem !important;
        }}
        .top-right-controls {{
            gap: 4px !important;
        }}
        .btn-session-main {{
            font-size: 0.60rem !important;
            padding: 2px 8px !important;
        }}
        .btn-session-end {{
            font-size: 0.60rem !important;
            padding: 2px 7px !important;
        }}
        .status-badge {{
            font-size: 0.58rem !important;
            padding: 2px 7px !important;
        }}
        .holo-node-sub {{
            font-size: 0.50rem !important;
        }}
    }}

    @media (max-width: 375px) {{
        .aura-command-center {{
            padding: 8px 8px 12px 8px !important;
            border-radius: 14px !important;
        }}
        .brand-nexroute-title {{
            font-size: 0.75rem !important;
            letter-spacing: 0.08em !important;
        }}
        .status-badge {{
            font-size: 0.56rem !important;
            padding: 2px 6px !important;
        }}
        .btn-session-main {{
            font-size: 0.58rem !important;
            padding: 2px 7px !important;
        }}
        .avatar-stage {{
            width: 84px !important;
            height: 84px !important;
        }}
        .holo-modules-container {{
            gap: 5px !important;
        }}
        .holo-node-title {{
            font-size: 0.68rem !important;
        }}
        .holo-node-sub {{
            font-size: 0.46rem !important;
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
                <span class="brand-nexroute-title">{brand_title}</span>
                <span class="brand-nexroute-sub">{brand_sub}</span>
            </div>
        </div>

        <div class="brand-pill">
            {brand_pill}
        </div>

        <div class="top-right-controls">
            <!-- Microphone Permission & Real-Time Activity State Indicator -->
            <div class="mic-status-pill standby" id="micStatusIndicator" title="Microphone permission & hardware state">
                <span class="mic-indicator-dot"></span>
                <span id="micStatusText">{txt_mic_std}</span>
            </div>
            <!-- Persistent Smart Voice Session Toggle -->
            <button class="btn-session-main start" id="btnSessionToggle" onclick="window.togglePersistentVoiceSession()" title="Start / Pause Continuous Voice Session">
                {btn_start_txt}
            </button>
            <!-- End Session Button -->
            <button class="btn-session-end" id="btnEndSession" onclick="window.endVoiceSession()" style="display: none;" title="End Voice Session (Offline)">
                {btn_end_txt}
            </button>
            <div class="status-badge wake-standby" id="statusBadge">
                {txt_state_wake}
            </div>
        </div>
    </div>

    <!-- 2. Holographic AI Travel Command Center / Orbital Stage -->
    <div class="holo-orbital-stage" id="orbitalStage">
        <!-- Background SVG Radar, Orbital Rings & Neural Energy Beams -->
        <svg class="holo-orbital-svg" viewBox="0 0 880 340" preserveAspectRatio="none">
            <defs>
                <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
                <linearGradient id="gradNav" x1="1" y1="0" x2="0" y2="0">
                    <stop offset="0%" stop-color="#00e5ff" stop-opacity="0.9" />
                    <stop offset="100%" stop-color="#00e5ff" stop-opacity="0.3" />
                </linearGradient>
                <linearGradient id="gradHotels" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.9" />
                    <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.3" />
                </linearGradient>
                <linearGradient id="gradFlights" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#00ffc6" stop-opacity="0.9" />
                    <stop offset="100%" stop-color="#00ffc6" stop-opacity="0.3" />
                </linearGradient>
                <linearGradient id="gradFood" x1="1" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#ec4899" stop-opacity="0.9" />
                    <stop offset="100%" stop-color="#ec4899" stop-opacity="0.3" />
                </linearGradient>
            </defs>

            <!-- Concentric Holographic Orbital Rings -->
            <ellipse cx="440" cy="140" rx="360" ry="145" class="orbital-ring-outer" />
            <ellipse cx="440" cy="140" rx="260" ry="110" class="orbital-ring-mid" />
            <circle cx="440" cy="140" r="105" class="orbital-ring" />

            <!-- Four Neural Energy Connecting Beams (Center 440, 140 to each 4-Quadrant Module) -->
            <!-- 1. Navigation (Upper-Left) -->
            <g id="beam-nav">
                <path d="M 440 140 L 195 50" class="energy-conduit-base" />
                <path d="M 440 140 L 195 50" class="energy-conduit-pulse" stroke="url(#gradNav)" />
            </g>
            <!-- 2. Hotels (Upper-Right) -->
            <g id="beam-hotels">
                <path d="M 440 140 L 685 50" class="energy-conduit-base" />
                <path d="M 440 140 L 685 50" class="energy-conduit-pulse" stroke="url(#gradHotels)" />
            </g>
            <!-- 3. Flights (Lower-Right) -->
            <g id="beam-flights">
                <path d="M 440 140 L 685 230" class="energy-conduit-base" />
                <path d="M 440 140 L 685 230" class="energy-conduit-pulse" stroke="url(#gradFlights)" />
            </g>
            <!-- 4. Restaurants (Lower-Left) -->
            <g id="beam-food">
                <path d="M 440 140 L 195 230" class="energy-conduit-base" />
                <path d="M 440 140 L 195 230" class="energy-conduit-pulse" stroke="url(#gradFood)" />
            </g>
        </svg>

        <!-- Central Holographic AURA Avatar Reactor & Live Telemetry -->
        <div class="aura-center-node">
            <div class="avatar-stage" onclick="window.togglePersistentVoiceSession()" title="Click to speak with AURA">
                <div class="arc-reactor-ring-outer"></div>
                <div class="telemetry-ring-segments"></div>
                <div class="arc-reactor-ring-mid" id="avatarMidRing"></div>
                <div class="avatar-core-circle">
                    {avatar_markup}
                </div>
            </div>

            <h1 class="greeting-headline" id="greetingHeadline">
                "{greeting_text}"
            </h1>

            <div class="waveform-container">
                <canvas id="auraWaveCanvas"></canvas>
            </div>

            <div class="live-transcript-box" id="transcriptBox">
                {transcript_ready_txt}
            </div>
        </div>

        <!-- Four Floating Holographic Travel Modules -->
        <div class="holo-modules-container">
            <!-- 1. Navigation Module -->
            <div class="holo-module-node node-nav"
                 onclick="window.dispatchCardNav('Open navigation', this)"
                 onmouseenter="window.highlightOrbitalBeam('beam-nav', true)"
                 onmouseleave="window.highlightOrbitalBeam('beam-nav', false)"
                 title="Open Corridor Routing Navigation">
                <div class="holo-glyph-disc" style="color: #00e5ff;">
                    <div class="holo-glyph-reticle"></div>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00e5ff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10" stroke-dasharray="3 3"/>
                        <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" fill="rgba(0, 229, 255, 0.45)"/>
                        <circle cx="12" cy="12" r="1.8" fill="#ffffff"/>
                    </svg>
                </div>
                <div class="holo-node-meta">
                    <span class="holo-node-title">{nav_title}</span>
                    <span class="holo-node-sub">{nav_sub}</span>
                </div>
                <div class="holo-status-blip" style="background: #00e5ff; box-shadow: 0 0 8px #00e5ff;"></div>
            </div>

            <!-- 2. Hotels Module -->
            <div class="holo-module-node node-hotels"
                 onclick="window.dispatchCardNav('Show hotels', this)"
                 onmouseenter="window.highlightOrbitalBeam('beam-hotels', true)"
                 onmouseleave="window.highlightOrbitalBeam('beam-hotels', false)"
                 title="Search Stays & Accommodations">
                <div class="holo-glyph-disc" style="color: #f59e0b;">
                    <div class="holo-glyph-reticle"></div>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M4 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16"/>
                        <path d="M16 11h4a2 2 0 0 1 2 2v8"/>
                        <rect x="7.5" y="7" width="2" height="2" fill="#fbbf24"/>
                        <rect x="11.5" y="7" width="2" height="2" fill="#fbbf24"/>
                        <rect x="7.5" y="12" width="2" height="2" fill="#fbbf24"/>
                        <rect x="11.5" y="12" width="2" height="2" fill="#fbbf24"/>
                        <line x1="2" y1="21" x2="22" y2="21"/>
                    </svg>
                </div>
                <div class="holo-node-meta">
                    <span class="holo-node-title">{hotels_title}</span>
                    <span class="holo-node-sub" style="color: #fbbf24;">{hotels_sub}</span>
                </div>
                <div class="holo-status-blip" style="background: #f59e0b; box-shadow: 0 0 8px #f59e0b;"></div>
            </div>

            <!-- 3. Flights Module -->
            <div class="holo-module-node node-flights"
                 onclick="window.dispatchCardNav('Open flights', this)"
                 onmouseenter="window.highlightOrbitalBeam('beam-flights', true)"
                 onmouseleave="window.highlightOrbitalBeam('beam-flights', false)"
                 title="Launch Air Corridor Planner">
                <div class="holo-glyph-disc" style="color: #00ffc6;">
                    <div class="holo-glyph-reticle"></div>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00ffc6" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3.5c-.5-.5-2.5 0-4 1.5L13.5 8.5 5.3 6.7c-.8-.2-1.5.3-1.6 1.1-.1.4.1.9.4 1.2l4.8 4.8-3.4 3.4-2.5-.5c-.4-.1-.8.1-1 .4l-.3.4c-.3.4-.2.9.2 1.2l3.4 2.4 2.4 3.4c.3.4.8.5 1.2.2l.4-.3c.3-.2.5-.6.4-1l-.5-2.5 3.4-3.4 4.8 4.8c.3.3.8.5 1.2.4.8-.1 1.3-.8 1.1-1.6z"/>
                    </svg>
                </div>
                <div class="holo-node-meta">
                    <span class="holo-node-title">{flights_title}</span>
                    <span class="holo-node-sub" style="color: #00ffc6;">{flights_sub}</span>
                </div>
                <div class="holo-status-blip" style="background: #00ffc6; box-shadow: 0 0 8px #00ffc6;"></div>
            </div>

            <!-- 4. Restaurants Module -->
            <div class="holo-module-node node-food"
                 onclick="window.dispatchCardNav('Show restaurants', this)"
                 onmouseenter="window.highlightOrbitalBeam('beam-food', true)"
                 onmouseleave="window.highlightOrbitalBeam('beam-food', false)"
                 title="Find Dining & Restaurants Along Route">
                <div class="holo-glyph-disc" style="color: #ec4899;">
                    <div class="holo-glyph-reticle"></div>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f472b6" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M3 17h18"/>
                        <path d="M5 17a7 7 0 0 1 14 0"/>
                        <circle cx="12" cy="7" r="1.5" fill="#f472b6"/>
                        <path d="M4 20h16"/>
                        <circle cx="12" cy="13" r="1" fill="#ffffff"/>
                    </svg>
                </div>
                <div class="holo-node-meta">
                    <span class="holo-node-title">{food_title}</span>
                    <span class="holo-node-sub" style="color: #f472b6;">{food_sub}</span>
                </div>
                <div class="holo-status-blip" style="background: #ec4899; box-shadow: 0 0 8px #ec4899;"></div>
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
    intelligent mid-speech interruption, silence detection, and React WebSocket communication bridge to Streamlit.
    """
    txt_state_init = t("aura.state_initializing", default="● INITIALIZING", lang=current_lang)
    txt_state_greet = t("aura.state_greeting", default="● GREETING", lang=current_lang)
    txt_state_wake = t("aura.state_wake_standby", default="● WAKE-WORD STANDBY", lang=current_lang)
    txt_state_list = t("aura.state_listening", default="● LISTENING...", lang=current_lang)
    txt_state_silence = t("aura.state_silence_detected", default="● SILENCE DETECTED", lang=current_lang)
    txt_state_proc = t("aura.state_processing", default="● PROCESSING...", lang=current_lang)
    txt_state_spk = t("aura.state_speaking", default="● SPEAKING...", lang=current_lang)
    txt_state_err = t("aura.state_error", default="● ERROR", lang=current_lang)
    txt_state_stop = t("aura.state_stopped", default="● STOPPED", lang=current_lang)
    txt_mic_act = t("aura.mic_active", default="🎙️ MIC: ACTIVE", lang=current_lang)
    txt_mic_std = t("aura.mic_standby", default="🎙️ MIC: STANDBY", lang=current_lang)
    txt_mic_mut = t("aura.mic_muted", default="🔇 MIC: MUTED", lang=current_lang)
    txt_mic_den = t("aura.mic_denied", default="⚠️ MIC: DENIED", lang=current_lang)
    txt_prompt_wake = t("aura.prompt_wake_standby", default='Say "Hey AURA" or click avatar to speak...', lang=current_lang)
    txt_prompt_silence = t("aura.prompt_silence", default="Silence detected. Finalizing command...", lang=current_lang)
    txt_wake_ack = t("aura.wake_word_ack", default="Yes, Boss?", lang=current_lang)

    return f"""
<script>
(function() {{
    var activeLang = {json.dumps(current_lang)};
    var bcp47Lang = {json.dumps(bcp47_code)};
    var shouldAutoSpeak = {json.dumps(bool(auto_speak))};
    var initialGreetingText = {json.dumps(greeting_text)};

    // Localized 9 Voice States
    var txtInit = {json.dumps(txt_state_init)};
    var txtGreeting = {json.dumps(txt_state_greet)};
    var txtWakeStandby = {json.dumps(txt_state_wake)};
    var txtListening = {json.dumps(txt_state_list)};
    var txtSilence = {json.dumps(txt_state_silence)};
    var txtProcessing = {json.dumps(txt_state_proc)};
    var txtSpeaking = {json.dumps(txt_state_spk)};
    var txtError = {json.dumps(txt_state_err)};
    var txtStopped = {json.dumps(txt_state_stop)};

    // Localized Mic States
    var txtMicActive = {json.dumps(txt_mic_act)};
    var txtMicStandby = {json.dumps(txt_mic_std)};
    var txtMicMuted = {json.dumps(txt_mic_mut)};
    var txtMicDenied = {json.dumps(txt_mic_den)};

    // Localized Prompts & Wake Acks
    var txtPromptWake = {json.dumps(txt_prompt_wake)};
    var txtPromptSilence = {json.dumps(txt_prompt_silence)};
    var txtWakeAck = {json.dumps(txt_wake_ack)};
    var txtPaused = {json.dumps(t("aura.status_paused", default="⏸️ PAUSED", lang=current_lang))};
    var txtIdlePrompt = {json.dumps(t("aura.status_idle_prompt", default="Ready for your command... Speak or click avatar.", lang=current_lang))};
    var txtBtnPause = {json.dumps(t("aura.btn_pause", default="⏸ PAUSE", lang=current_lang))};
    var txtBtnResume = {json.dumps(t("aura.btn_resume", default="▶ RESUME", lang=current_lang))};
    var txtBtnSpeak = {json.dumps(t("aura.btn_speak", default="🎙️ SPEAK", lang=current_lang))};
    var txtBtnStart = {json.dumps(t("aura.btn_start", default="▶ START AURA", lang=current_lang))};

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

    // -------------------------------------------------------------------------
    // Configurable Voice & Silence Detection Thresholds (2.0s VAD Window)
    // -------------------------------------------------------------------------
    var voiceConfig = {{
        silenceThresholdMs: 2000,        // 2.0s Intelligent Silence Detection threshold
        vadTimeoutMs: 2000,              // Backward-compatibility alias
        extendedSilenceMs: 7500,         // Extended silence: return to wake-word standby
        maxUtteranceDurationMs: 15000,   // Max duration per utterance
        wakeWordEnabled: true,           // Continuous wake-word scanning ("Hey AURA")
        autoStopOnSilence: true,         // Automatically finalize mic recording on silence
        autoRestartAfterResponse: true,  // Automatically return to wake-word standby loop
        preventEmptyTranscriptions: true // Discard empty transcriptions
    }};

    // -------------------------------------------------------------------------
    // Time-Appropriate Dynamic Greeting
    // -------------------------------------------------------------------------
    function getClientLocalGreeting(lang, userName) {{
        var h = new Date().getHours();
        var period = 'morning';
        if (h >= 5 && h < 12) period = 'morning';
        else if (h >= 12 && h < 17) period = 'afternoon';
        else if (h >= 17 && h < 21) period = 'evening';
        else period = 'night';

        var greetings = {{
            en: {{
                morning: "Good morning, " + userName + "! Welcome to NextRoute. I'm AURA, your autonomous travel assistant. How can I help you?",
                afternoon: "Good afternoon, " + userName + "! Welcome to NextRoute. I'm AURA, your autonomous travel assistant. What can I do for you?",
                evening: "Good evening, " + userName + "! Welcome to NextRoute. I'm AURA, your autonomous travel assistant. How can I help you?",
                night: "Hello, " + userName + "! Welcome back to NextRoute. I'm AURA, your autonomous travel assistant. How can I assist you tonight?"
            }},
            te: {{
                morning: "శుభోదయం, " + userName + "! నెక్స్‌రూట్‌కి స్వాగతం. నేను మీ ఆటోనామస్ ట్రావెల్ అసిస్టెంట్ AURA. నేను మీకు ఎలా సహాయపడగలను?",
                afternoon: "శుభ మధ్యాహ్నం, " + userName + "! నెక్స్‌రూట్‌కి స్వాగతం. నేను మీ ఆటోనామస్ ట్రావెల్ అసిస్టెంట్ AURA. మీ కోసం నేను ఏమి చేయగలను?",
                evening: "శుభ సాయంత్రం, " + userName + "! నెక్స్‌రూట్‌కి స్వాగతం. నేను మీ ఆటోనామస్ ట్రావెల్ అసిస్టెంట్ AURA. నేను మీకు ఎలా సహాయపడగలను?",
                night: "నమస్కారం, " + userName + "! నెక్స్‌రూట్‌కి తిరిగి స్వాగతం. నేను మీ ఆటోనామస్ ట్రావెల్ అసిస్టెంట్ AURA. ఈ రాత్రి నేను మీకు ఎలా సహాయపడగలను?"
            }},
            hi: {{
                morning: "शुभ प्रभात, " + userName + "! नेक्स्ट-रूट में आपका स्वागत है। मैं AURA, आपका ऑटोनॉमस ट्रैवल असिस्टेंट हूँ। मैं आपकी क्या मदद कर सकता हूँ?",
                afternoon: "शुभ दोपहर, " + userName + "! नेक्स्ट-रूट में आपका स्वागत है। मैं AURA, आपका ऑटोनॉमस ट्रैवल असिस्टेंट हूँ। मैं आपके लिए क्या कर सकता हूँ?",
                evening: "शुभ संध्या, " + userName + "! नेक्स्ट-रूट में आपका स्वागत है। मैं AURA, आपका ऑटोनॉमस ट्रैवल असिस्टेंट हूँ। मैं आपकी क्या मदद कर सकता हूँ?",
                night: "नमस्ते, " + userName + "! नेक्स्ट-रूट में पुनः स्वागत है। मैं AURA, आपका ऑटोनॉमस ट्रैवल असिस्टेंट हूँ। आज रात मैं आपकी क्या सहायता कर सकता हूँ?"
            }},
            ta: {{
                morning: "காலை வணக்கம், " + userName + "! நெக்ஸ்ட்-ரூட்டிற்கு நல்வரவு. நான் உங்கள் பயண உதவியாளர் AURA. நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?",
                afternoon: "மதிய வணக்கம், " + userName + "! நெக்ஸ்ட்-ரூட்டிற்கு நல்வரவு. நான் உங்கள் பயண உதவியாளர் AURA. உங்களுக்காக நான் என்ன செய்ய முடியும்?",
                evening: "மாலை வணக்கம், " + userName + "! நெக்ஸ்ட்-ரூட்டிற்கு நல்வரவு. நான் உங்கள் பயண உதவியாளர் AURA. நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?",
                night: "வணக்கம், " + userName + "! நெக்ஸ்ட்-ரூட்டிற்கு மீண்டும் நல்வரவு. நான் உங்கள் பயண உதவியாளர் AURA. இன்று இரவு நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?"
            }},
            kn: {{
                morning: "ಶುಭೋದಯ, " + userName + "! ನೆಕ್ಸ್ಟ್‌-ರೂಟ್‌ಗೆ ಸುಸ್ವಾಗತ. ನಾನು AURA, ನಿಮ್ಮ ಸ್ವಾಯತ್ತ ಪ್ರಯಾಣ ಸಹಾಯಕ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?",
                afternoon: "ಶುಭ ಮಧ್ಯಾಹ್ನ, " + userName + "! ನೆಕ್ಸ್ಟ್‌-ರೂಟ್‌ಗೆ ಸುಸ್ವಾಗತ. ನಾನು AURA, ನಿಮ್ಮ ಸ್ವಾಯತ್ತ ಪ್ರಯಾಣ ಸಹಾಯಕ. ನಿಮಗಾಗಿ ನಾನು ಏನು ಮಾಡಲಿ?",
                evening: "ಶುಭ ಸಂಜೆ, " + userName + "! ನೆಕ್ಸ್ಟ್‌-ರೂಟ್‌ಗೆ ಸುಸ್ವಾಗತ. ನಾನು AURA, ನಿಮ್ಮ ಸ್ವಾಯತ್ತ ಪ್ರಯಾಣ ಸಹಾಯಕ. ನಾನು మీకు ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?",
                night: "ನಮಸ್ಕಾರ, " + userName + "! ನೆಕ್ಸ್ಟ್‌-ರೂಟ್‌ಗೆ ಮತ್ತೆ ಸುಸ್ವಾಗತ. ನಾನು AURA, ನಿಮ್ಮ ಸ್ವಾಯತ್ತ ಪ್ರಯಾಣ ಸಹಾಯಕ. ಇಂದು ರಾತ್ರಿ ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?"
            }},
            ml: {{
                morning: "സുപ്രഭാതം, " + userName + "! നെക്സ്റ്റ്-റൂട്ടിലേക്ക് സ്വാഗതം. ഞാൻ AURA, നിങ്ങളുടെ സ്വയംഭരണ യാത്രാ സഹായി. ഞാൻ എങ്ങനെ സഹായിക്കണം?",
                afternoon: "ശുഭ ഉച്ചതിരിഞ്ഞ്, " + userName + "! നെക്സ്റ്റ്-റൂട്ടിലേക്ക് സ്വാഗതം. ഞാൻ AURA. ഞാൻ എന്താണ് ചെയ്യേണ്ടത്?",
                evening: "ശുഭ സായാഹ്നം, " + userName + "! നെക്സ്റ്റ്-റൂട്ടിലേക്ക് സ്വാഗതം. ഞാൻ AURA. ഞാൻ എങ്ങനെ സഹായിക്കണം?",
                night: "ഹലോ, " + userName + "! നെക്സ്റ്റ്-റൂട്ടിലേക്ക് വീണ്ടും സ്വാഗതം. ഞാൻ AURA. ഇന്ന് രാത്രി ഞാൻ എങ്ങനെ സഹായിക്കണം?"
            }},
            bn: {{
                morning: "সুপ্রভাত, " + userName + "! নেক্সটরুটে স্বাগতম। আমি AURA, আপনার স্বয়ংক্রিয় ভ্রমণ সহায়ক। আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
                afternoon: "শুভ অপরাহ্ন, " + userName + "! নেক্সটরুটে স্বাগতম। আমি আপনার জন্য কি করতে পারি?",
                evening: "শুভ সন্ধ্যা, " + userName + "! নেক্সটরুটে স্বাগতম। আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
                night: "হ্যালো, " + userName + "! নেক্সটরুটে আবার স্বাগতম। আজ রাতে আমি আপনাকে কীভাবে সাহায্য করতে পারি?"
            }},
            mr: {{
                morning: "शुभ सकाळ, " + userName + "! नेक्स्ट-रूट मध्ये आपले स्वागत आहे. मी AURA, आपला स्वायत्त प्रवास सहाय्यक. मी आपली काय मदत करू शकतो?",
                afternoon: "शुभ दुपार, " + userName + "! नेक्स्ट-रूट मध्ये आपले स्वागत आहे. मी आपल्यासाठी काय करू शकतो?",
                evening: "शुभ संध्याकाळ, " + userName + "! नेक्स्ट-रूट मध्ये आपले स्वागत आहे. मी आपली काय मदत करू शकतो?",
                night: "नमस्कार, " + userName + "! नेक्स्ट-रूट मध्ये पुन्हा स्वागत आहे. आज रात्री मी आपली कशी मदत करू शकतो?"
            }}
        }};

        var langObj = greetings[lang] || greetings['en'];
        return langObj[period] || langObj['morning'];
    }}

    var clientGreeting = getClientLocalGreeting(activeLang, "Boss");
    var greetingHeadlineElem = document.getElementById('greetingHeadline');
    if (greetingHeadlineElem) {{
        greetingHeadlineElem.innerText = '"' + clientGreeting + '"';
    }}

    // Localized Wake-Word Acknowledgments
    var wakeWordAcks = {{
        en: "Yes, Boss?",
        te: "చెప్పండి బాస్?",
        hi: "हाँ, बॉस?",
        ta: "சொல்லுங்கள் பாஸ்?",
        kn: "ಹೇಳಿ ಬಾಸ್?",
        ml: "പറയൂ ബോസ്?",
        bn: "বলুন বস?",
        mr: "बोला बॉस?"
    }};

    // -------------------------------------------------------------------------
    // Multilingual Wake-Word Detector across all 8 supported languages:
    // English, Telugu, Hindi, Tamil, Kannada, Malayalam, Bengali, Marathi
    // Robust against single-word "aura", phonetic variants (ora, aora, oura),
    // punctuation suffixes (aura.), and regional language transcriptions
    // -------------------------------------------------------------------------
    function isWakeWordPhrase(text, lang) {{
        if (!text) return false;
        var clean = text.toLowerCase()
            .replace(/[.,\\/#!$%\\^&\\*;:{{}}=\\-_`~()?\"'’]/g, ' ')
            .replace(/\\s+/g, ' ')
            .trim();
        if (!clean) return false;

        // 1. English + universal phonetic transcriptions of "Aura"
        if (/(^|\\s)(hey\\s+aura|hi\\s+aura|hello\\s+aura|ok\\s+aura|okay\\s+aura|wake\\s+up\\s+aura|aura\\s+wake\\s+up|aura|ora|aora|oura|aurah|aurora|arua|ahura)($|\\s)/i.test(clean)) return true;

        // 2. Telugu (ఆరా, ఔరా, ఓరా, ఆర, హే ఆరా, మేల్కొను ఆరా, నమస్తే ఆరా)
        if (/(హే\\s*ఆరా|ఆరా|ఔరా|ఓరా|ఆర|మేల్కొను\\s*ఆరా|నమస్తే\\s*ఆరా)/.test(clean)) return true;

        // 3. Hindi (हे ऑरा, ऑरा, आरा, ओरा, और, जागो ऑरा, नमस्ते ऑरा)
        if (/(हे\\s*ऑरा|ऑरा|आरा|ओरा|और|जागो\\s*ऑरा|नमस्ते\\s*ऑरा)/.test(clean)) return true;

        // 4. Tamil (ஹே ஆரா, ஆரா, ஒரா, ஔரா, எழுந்திரு ஆரா, வணக்கம் ஆரா)
        if (/(ஹே\\s*ஆரா|ஆரா|ஒரா|ஔரா|எழுந்திரு\\s*ஆரா|வணக்கம்\\s*ஆரா)/.test(clean)) return true;

        // 5. Kannada (ಹೇ ಔರಾ, ಔರಾ, ಆರಾ, ಒರಾ, ಎಚ್ಚರಾಗು ಔರಾ, ನಮಸ್ಕಾರ ಔರಾ)
        if (/(ಹೇ\\s*ಔರಾ|ಔರಾ|ಆರಾ|ಒರಾ|ಎಚ್ಚರಾಗು\\s*ಔರಾ|ನಮಸ್ಕಾರ\\s*ಔರಾ)/.test(clean)) return true;

        // 6. Malayalam (ഹേ ഓറ, ഓറ, ആറ, ഒറ, ഉണരുക ഓറ, നമസ്കാരം ഓറ)
        if (/(ഹേ\\s*ഓറ|ഓറ|ആറ|ഒറ|ഉണരുക\\s*ഓറ|നമസ്കാരം\\s*ഓറ)/.test(clean)) return true;

        // 7. Bengali (হে অরা, অরা, আরা, জেগে ওঠো অরা, নমস্কার অরা)
        if (/(হে\\s*অরা|অরা|আরা|জেগে\\s*ওঠো\\s*অরা|নমস্কার\\s*অরা)/.test(clean)) return true;

        // 8. Marathi (हे ऑरा, ऑरा, आरा, जागृत व्हा ऑरा, नमस्कार ऑरा)
        if (/(हे\\s*ऑरा|ऑरा|आरा|जागृत\\s*व्हा\\s*ऑरा|नमस्कार\\s*ऑरा)/.test(clean)) return true;

        return false;
    }}

    function extractCommandAfterWakeWord(text) {{
        if (!text) return '';
        var replaced = text
            .replace(/^[.,\\/#!$%\\^&\\*;:{{}}=\\-_`~()?\"'’\\s]+/g, '')
            .replace(/^(hey\\s+aura|hi\\s+aura|hello\\s+aura|ok\\s+aura|okay\\s+aura|wake\\s+up\\s+aura|aura\\s+wake\\s+up|aura|ora|aora|oura|aurah|aurora|arua|ahura)[,\\s:]*/i, '')
            .replace(/^(హే\\s*ఆరా|ఆరా|ఔరా|ఓరా|ఆర|మేల్కొను\\s*ఆరా|నమస్తే\\s*ఆరా)[,\\s:]*/, '')
            .replace(/^(हे\\s*ऑरा|ऑरा|आरा|ओरा|और|जागो\\s*ऑरा|नमस्ते\\s*ऑरा)[,\\s:]*/, '')
            .replace(/^(ஹே\\s*ஆரா|ஆரா|ஒரா|ஔரா|எழுந்திரு\\s*ஆரா|வணக்கம்\\s*ஆரா)[,\\s:]*/, '')
            .replace(/^(ಹೇ\\s*ಔರಾ|ಔರಾ|ಆರಾ|ಒರಾ|ಎಚ್ಚರಾಗು\\s*ಔರಾ|ನಮಸ್ಕಾರ\\s*ಔರಾ)[,\\s:]*/, '')
            .replace(/^(ഹേ\\s*ഓറ|ഓറ|ആറ|ഒറ|ഉണരുക\\s*ഓറ|നമസ്കാരം\\s*ഓറ)[,\\s:]*/, '')
            .replace(/^(হে\\s*অরা|অরা|আরা|জেগে\\s*ওঠো\\s*অরা|নমস্কার\\s*অরা)[,\\s:]*/, '')
            .replace(/^(हे\\s*ऑरा|ऑरा|आरा|जागृत\\s*व्हा\\s*ऑरा|नमस्कार\\s*ऑरा)[,\\s:]*/, '');
        return replaced.replace(/^[.,\\/#!$%\\^&\\*;:{{}}=\\-_`~()?\"'’\\s]+/g, '').trim();
    }}

    // -------------------------------------------------------------------------
    // Exact 9-State Central Voice State Machine:
    // 1. INITIALIZING
    // 2. GREETING
    // 3. WAKE_WORD_STANDBY
    // 4. LISTENING
    // 5. SILENCE_DETECTED
    // 6. PROCESSING
    // 7. SPEAKING
    // 8. ERROR
    // 9. STOPPED
    // -------------------------------------------------------------------------
    var STATE_INITIALIZING = 'INITIALIZING';
    var STATE_GREETING = 'GREETING';
    var STATE_WAKE_WORD_STANDBY = 'WAKE_WORD_STANDBY';
    var STATE_LISTENING = 'LISTENING';
    var STATE_SILENCE_DETECTED = 'SILENCE_DETECTED';
    var STATE_PROCESSING = 'PROCESSING';
    var STATE_SPEAKING = 'SPEAKING';
    var STATE_ERROR = 'ERROR';
    var STATE_STOPPED = 'STOPPED';

    var sessionState = localStorage.getItem('aura_persistent_voice_state') || STATE_WAKE_WORD_STANDBY;
    if (sessionState === 'IDLE' || sessionState === 'SPEAKING' || sessionState === 'PROCESSING' || sessionState === 'SILENCE_DETECTED') {{
        sessionState = STATE_WAKE_WORD_STANDBY;
    }}

    // Explicit Independent Dashboard Voice States
    var dashboardIsListening = false;
    var dashboardTranscript = '';
    var dashboardVoiceActive = false;
    var dashboardRecognition = null;
    var dashboardSpeechOutput = null;

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

    var silenceTimer = null;         // 2.0s Intelligent Silence Detection Timer
    var extendedSilenceTimer = null; // Extended timeout timer
    var currentSpeechBuffer = '';
    var restartDebounceTimer = null;
    var commandDispatchLock = false; // Prevent double execution of identical command

    // Hardware Microphone Status Updater
    function setMicStatus(status) {{
        var pill = document.getElementById('micStatusIndicator');
        var txt = document.getElementById('micStatusText');
        if (!pill || !txt) return;
        pill.className = 'mic-status-pill ' + status.toLowerCase();
        if (status === 'ACTIVE') txt.innerText = txtMicActive;
        else if (status === 'STANDBY') txt.innerText = txtMicStandby;
        else if (status === 'MUTED') txt.innerText = txtMicMuted;
        else if (status === 'DENIED') txt.innerText = txtMicDenied;
    }}

    // -------------------------------------------------------------------------
    // UI Status & Avatar Reactor State Synchronization
    // -------------------------------------------------------------------------
    function updateUIForState(state, message) {{
        var badge = document.getElementById('statusBadge');
        var btnToggle = document.getElementById('btnSessionToggle');
        var btnEnd = document.getElementById('btnEndSession');
        var midRing = document.getElementById('avatarMidRing');
        var transBox = document.getElementById('transcriptBox');
        var avatarStage = document.querySelector('.avatar-stage');

        if (transBox && message) transBox.innerText = message;

        // Apply avatar animation class
        if (avatarStage) {{
            avatarStage.className = 'avatar-stage state-' + state.toLowerCase().replace(/_/g, '-');
        }}

        if (state === STATE_INITIALIZING) {{
            isListening = false;
            isSpeaking = false;
            isProcessing = false;
            if (badge) {{
                badge.className = 'status-badge initializing';
                badge.innerText = txtInit;
            }}
            setMicStatus('STANDBY');
            if (midRing) midRing.style.boxShadow = '0 0 16px #0ea5e9';
        }} else if (state === STATE_GREETING) {{
            isListening = false;
            isSpeaking = true;
            isProcessing = false;
            if (badge) {{
                badge.className = 'status-badge greeting';
                badge.innerText = txtGreeting;
            }}
            if (btnToggle) {{
                btnToggle.className = 'btn-session-main pause';
                btnToggle.innerHTML = txtBtnPause;
            }}
            if (btnEnd) btnEnd.style.display = 'inline-flex';
            setMicStatus('STANDBY');
            if (midRing) midRing.style.boxShadow = '0 0 28px #a855f7';
        }} else if (state === STATE_WAKE_WORD_STANDBY) {{
            isListening = true;
            isSpeaking = false;
            isProcessing = false;
            if (badge) {{
                badge.className = 'status-badge wake-standby';
                badge.innerText = txtWakeStandby;
            }}
            if (btnToggle) {{
                btnToggle.className = 'btn-session-main start';
                btnToggle.innerHTML = txtBtnSpeak;
            }}
            if (btnEnd) btnEnd.style.display = 'inline-flex';
            setMicStatus('STANDBY');
            if (midRing) midRing.style.boxShadow = '0 0 18px rgba(0, 240, 255, 0.45)';
        }} else if (state === STATE_LISTENING) {{
            isListening = true;
            isSpeaking = false;
            isProcessing = false;
            if (badge) {{
                badge.className = 'status-badge listening';
                badge.innerText = txtListening;
            }}
            if (btnToggle) {{
                btnToggle.className = 'btn-session-main pause';
                btnToggle.innerHTML = txtBtnPause;
            }}
            if (btnEnd) btnEnd.style.display = 'inline-flex';
            setMicStatus('ACTIVE');
            if (midRing) midRing.style.boxShadow = '0 0 32px #00f0ff';
        }} else if (state === STATE_SILENCE_DETECTED) {{
            isListening = false;
            isSpeaking = false;
            isProcessing = true;
            if (badge) {{
                badge.className = 'status-badge silence-detected';
                badge.innerText = txtSilence;
            }}
            setMicStatus('STANDBY');
            if (midRing) midRing.style.boxShadow = '0 0 24px #f59e0b';
        }} else if (state === STATE_PROCESSING) {{
            isListening = false;
            isSpeaking = false;
            isProcessing = true;
            if (badge) {{
                badge.className = 'status-badge thinking';
                badge.innerText = txtProcessing;
            }}
            if (btnToggle) {{
                btnToggle.className = 'btn-session-main pause';
                btnToggle.innerHTML = txtBtnPause;
            }}
            if (btnEnd) btnEnd.style.display = 'inline-flex';
            setMicStatus('STANDBY');
            if (midRing) midRing.style.boxShadow = '0 0 28px #a855f7';
        }} else if (state === STATE_SPEAKING) {{
            isListening = false;
            isSpeaking = true;
            isProcessing = false;
            if (badge) {{
                badge.className = 'status-badge speaking';
                badge.innerText = txtSpeaking;
            }}
            if (btnToggle) {{
                btnToggle.className = 'btn-session-main pause';
                btnToggle.innerHTML = txtBtnPause;
            }}
            if (btnEnd) btnEnd.style.display = 'inline-flex';
            setMicStatus('STANDBY');
            if (midRing) midRing.style.boxShadow = '0 0 28px #38bdf8';
        }} else if (state === STATE_ERROR) {{
            isListening = false;
            isSpeaking = false;
            isProcessing = false;
            if (badge) {{
                badge.className = 'status-badge error';
                badge.innerText = txtError;
            }}
            setMicStatus('DENIED');
            if (btnEnd) btnEnd.style.display = 'inline-flex';
            if (midRing) midRing.style.boxShadow = '0 0 24px #ef4444';
        }} else {{
            // STOPPED or PAUSED
            isListening = false;
            isSpeaking = false;
            isProcessing = false;
            if (badge) {{
                badge.className = 'status-badge stopped';
                badge.innerText = txtStopped;
            }}
            if (btnToggle) {{
                btnToggle.className = 'btn-session-main start';
                btnToggle.innerHTML = txtBtnStart;
            }}
            if (btnEnd) btnEnd.style.display = 'none';
            setMicStatus('MUTED');
            if (midRing) midRing.style.boxShadow = '0 0 10px rgba(100, 116, 139, 0.3)';
        }}
    }}

    function setSessionState(newState, message) {{
        sessionState = newState;
        try {{ localStorage.setItem('aura_persistent_voice_state', newState); }} catch(e) {{}}
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

        var baseAmp = isSpeaking ? 10 : (isListening ? (sessionState === STATE_LISTENING ? 8 : 3.5) : (isProcessing ? 4.5 : 1.2));
        var freq = isSpeaking ? 0.18 : (isListening ? (sessionState === STATE_LISTENING ? 0.24 : 0.12) : 0.08);

        ctx.beginPath();
        ctx.strokeStyle = isSpeaking ? '#00f0ff' : (sessionState === STATE_LISTENING ? '#00f0ff' : (sessionState === STATE_WAKE_WORD_STANDBY ? '#38bdf8' : '#a855f7'));
        ctx.lineWidth = isSpeaking || sessionState === STATE_LISTENING ? 2.2 : 1.4;
        ctx.shadowBlur = isSpeaking ? 14 : (sessionState === STATE_LISTENING ? 12 : 4);
        ctx.shadowColor = '#00f0ff';

        for (var i = 0; i <= numPoints; i++) {{
            var x = i * step;
            var envelope = Math.sin((i / numPoints) * Math.PI);
            var y = midY + Math.sin(i * freq + wavePhase) * (baseAmp * envelope);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }}
        ctx.stroke();

        wavePhase += isSpeaking ? 0.22 : (sessionState === STATE_LISTENING ? 0.18 : 0.05);
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

    function selectNaturalVoiceForLang(voices, bcp47, langCode) {{
        if (!voices || voices.length === 0) return null;
        var bcp47Lower = (bcp47 || 'en-IN').toLowerCase();
        var prefix = (langCode || 'en').toLowerCase();

        var preferredKeywords = {{
            te: ["mohan", "chitra", "తెలుగు", "telugu"],
            hi: ["hemant", "kalpana", "हिन्दी", "hindi", "swara", "madhur", "lekha"],
            ta: ["valluvar", "pallavi", "தமிழ்", "tamil"],
            kn: ["gagan", "sapna", "ಕನ್ನಡ", "kannada"],
            ml: ["midhun", "sobhana", "മലയാളം", "malayalam"],
            bn: ["bashkar", "tanishaa", "বাংলা", "bengali", "bangla"],
            mr: ["manohar", "aarohi", "मराठी", "marathi"],
            en: ["ravi", "heera", "natural", "neural", "google", "david", "guy", "george", "samantha"]
        }};

        var targetKeywords = preferredKeywords[prefix] || [prefix];

        // Priority 1: Match preferred voice keywords AND language tag
        for (var i = 0; i < voices.length; i++) {{
            var v = voices[i];
            var vLang = (v.lang || '').toLowerCase();
            var vName = (v.name || '').toLowerCase();
            if (vLang === bcp47Lower || vLang.indexOf(prefix) === 0) {{
                for (var k = 0; k < targetKeywords.length; k++) {{
                    if (vName.indexOf(targetKeywords[k]) !== -1) {{
                        return v;
                    }}
                }}
            }}
        }}

        // Priority 2: Match any voice matching the exact BCP-47 tag
        for (var j = 0; j < voices.length; j++) {{
            if ((voices[j].lang || '').toLowerCase() === bcp47Lower) {{
                return voices[j];
            }}
        }}

        // Priority 3: Match any voice starting with primary language prefix
        for (var m = 0; m < voices.length; m++) {{
            if ((voices[m].lang || '').toLowerCase().indexOf(prefix) === 0) {{
                return voices[m];
            }}
        }}

        if (prefix === 'en') return voices[0] || null;
        return null;
    }}

    // Voice Synthesis with Mutex Audio Lock
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
                var selVoice = selectNaturalVoiceForLang(voices, bcp47Lang, activeLang);
                if (!selVoice && activeLang !== 'en') {{
                    console.warn("[AURA] Speech synthesis voice for " + activeLang + " is not installed on this browser. Displaying text response.");
                    setSessionState(STATE_WAKE_WORD_STANDBY, 'Voice for ' + activeLang.toUpperCase() + ' unavailable. Text is displayed.');
                    if (onDone) onDone();
                    return;
                }}

                var utterance = new SpeechSynthesisUtterance(textToSpeak);
                utterance.lang = bcp47Lang;
                utterance.rate = 1.0;
                utterance.pitch = 1.02;
                if (selVoice) utterance.voice = selVoice;

                var doneHandled = false;
                function finishUtterance() {{
                    if (doneHandled) return;
                    doneHandled = true;
                    try {{ localStorage.setItem('aura_active_speaker', 'none'); }} catch(e) {{}}
                    if (watchdogTimer) clearTimeout(watchdogTimer);
                    isSpeaking = false;
                    try {{ window.__AURA_CURRENT_UTTERANCE__ = null; }} catch(e) {{}}

                    if (onDone) onDone();

                    // AUTOMATIC RETURN TO WAKE-WORD STANDBY LOOP
                    if (sessionState !== STATE_STOPPED && sessionState !== 'PAUSED') {{
                        setTimeout(function() {{
                            if (sessionState !== STATE_STOPPED) {{
                                setSessionState(STATE_WAKE_WORD_STANDBY, txtPromptWake);
                                startVoiceListening();
                            }}
                        }}, 400); // 400ms delay to clear acoustic echo
                    }}
                }}

                var safetyTimeoutMs = Math.max(3200, (textToSpeak || '').length * 85);
                var watchdogTimer = setTimeout(function() {{
                    console.warn("[AURA] Speech synthesis timeout / watchdog reached.");
                    finishUtterance();
                }}, safetyTimeoutMs);

                utterance.onstart = function() {{
                    try {{ localStorage.setItem('aura_active_speaker', 'dashboard'); }} catch(e) {{}}
                    setSessionState(STATE_SPEAKING, 'AURA: "' + textToSpeak + '"');
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

    function stopOngoingSpeech() {{
        try {{ localStorage.setItem('aura_active_speaker', 'none'); }} catch(e) {{}}
        if (synthesis) synthesis.cancel();
        isSpeaking = false;
    }}

    // Extended Silence Handler: stops active listening and returns to wake-word standby
    function resetExtendedSilenceTimer() {{
        if (extendedSilenceTimer) clearTimeout(extendedSilenceTimer);
        if (!voiceConfig.autoStopOnSilence) return;
        extendedSilenceTimer = setTimeout(function() {{
            if (sessionState === STATE_LISTENING) {{
                console.log("[AURA] Extended silence timeout reached (7.5s). Entering Wake-Word Standby.");
                currentSpeechBuffer = '';
                setSessionState(STATE_WAKE_WORD_STANDBY, txtPromptWake);
            }}
        }}, voiceConfig.extendedSilenceMs);
    }}

    // Real-Time Speech Recognition Engine with Wake-Word & 2.0s Silence VAD
    function startVoiceListening() {{
        if (sessionState === STATE_STOPPED || sessionState === 'PAUSED') return;

        var SpeechRec = null;
        try {{
            SpeechRec = (pWin && (pWin.SpeechRecognition || pWin.webkitSpeechRecognition)) ||
                        window.SpeechRecognition || window.webkitSpeechRecognition;
        }} catch(e) {{
            SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        }}

        if (!SpeechRec) {{
            setSessionState(STATE_ERROR, 'Speech recognition not supported in browser. Use Chrome or Edge.');
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
            dashboardRecognition = recognition;
            dashboardSpeechOutput = synthesis;

            recognition.onstart = function() {{
                setMicStatus(sessionState === STATE_LISTENING ? 'ACTIVE' : 'STANDBY');
                resetExtendedSilenceTimer();
            }};

            recognition.onspeechstart = function() {{
                if (extendedSilenceTimer) clearTimeout(extendedSilenceTimer);

                // INTERRUPTION: user speaks while AURA is talking
                if (isSpeaking) {{
                    console.log("[AURA] User speech detected during TTS: interrupting immediately!");
                    stopOngoingSpeech();
                    setSessionState(STATE_LISTENING, txtListening);
                }}
            }};

            recognition.onresult = function(event) {{
                if (extendedSilenceTimer) clearTimeout(extendedSilenceTimer);

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

                // Chatbot audio mutual exclusion lock
                try {{
                    if (localStorage.getItem('aura_active_speaker') === 'chatbot') {{
                        return;
                    }}
                }} catch(eAudioLock) {{}}

                // VOICE INTERRUPTION CHECK
                if (isSpeaking && rawText.length > 0) {{
                    stopOngoingSpeech();
                    setSessionState(STATE_LISTENING, txtListening);
                }}

                // -----------------------------------------------------------------
                // WAKE-WORD DETECTION in WAKE_WORD_STANDBY
                // -----------------------------------------------------------------
                if (sessionState === STATE_WAKE_WORD_STANDBY) {{
                    if (isWakeWordPhrase(rawText, activeLang)) {{
                        console.log("[AURA] Wake-Word detected!", rawText);
                        var extractedCmd = extractCommandAfterWakeWord(rawText);

                        if (extractedCmd.length > 0) {{
                            // User said wake-word + command in one sentence ("Hey AURA find hospitals")
                            setSessionState(STATE_LISTENING, '🎙️ "' + extractedCmd + '"');
                            currentSpeechBuffer = extractedCmd;
                            if (silenceTimer) clearTimeout(silenceTimer);

                            // Start 2.0s silence timer on the extracted command
                            silenceTimer = setTimeout(function() {{
                                executeFinalCommand(currentSpeechBuffer);
                            }}, voiceConfig.silenceThresholdMs);
                        }} else {{
                            // User spoke only wake-word ("Hey AURA") -> Acknowledge and listen!
                            setSessionState(STATE_LISTENING, txtListening);
                            currentSpeechBuffer = '';
                            var ackPhrase = wakeWordAcks[activeLang] || txtWakeAck;
                            speakJarvis(ackPhrase, function() {{
                                setSessionState(STATE_LISTENING, txtListening);
                                resetExtendedSilenceTimer();
                            }});
                        }}
                    }}
                    return;
                }}

                // -----------------------------------------------------------------
                // ACTIVE LISTENING with 2.0s Silence Detection
                // -----------------------------------------------------------------
                if (sessionState === STATE_LISTENING) {{
                    if (rawText.length > 0) {{
                        currentSpeechBuffer = rawText;
                        var tBox = document.getElementById('transcriptBox');
                        if (tBox) tBox.innerText = '🎙️ "' + rawText + '"';

                        if (silenceTimer) clearTimeout(silenceTimer);

                        // If browser marked phrase final
                        if (finalTranscript.trim().length > 0) {{
                            var finalCmd = finalTranscript.trim();
                            currentSpeechBuffer = finalCmd;

                            // Immediate local handling of Voice Session control commands
                            if (/^(pause(\\\\s+the)?(\\\\s+voice)?(\\\\s+assistant)?|pause\\\\s+listening|hold\\\\s+on)$/i.test(finalCmd.toLowerCase())) {{
                                pauseVoiceSession();
                                return;
                            }}
                            if (/^(stop(\\\\s+the)?(\\\\s+voice)?(\\\\s+assistant)?|end\\\\s+session|aura\\\\s+offline|close\\\\s+assistant)$/i.test(finalCmd.toLowerCase())) {{
                                endVoiceSession();
                                return;
                            }}

                            // Finalize on 2.0s silence or short final transition
                            silenceTimer = setTimeout(function() {{
                                executeFinalCommand(finalCmd);
                            }}, 300);
                        }} else {{
                            // Interim speech: start 2000ms silence detection timer
                            silenceTimer = setTimeout(function() {{
                                if (currentSpeechBuffer.length > 0) {{
                                    executeFinalCommand(currentSpeechBuffer);
                                }}
                            }}, voiceConfig.silenceThresholdMs);
                        }}
                    }}
                }}
            }};

            function executeFinalCommand(cmdText) {{
                var cleanCmd = (cmdText || '').trim();
                if (!cleanCmd || cleanCmd.length < 2 || commandDispatchLock) return;

                commandDispatchLock = true;
                currentSpeechBuffer = '';
                if (silenceTimer) clearTimeout(silenceTimer);
                if (extendedSilenceTimer) clearTimeout(extendedSilenceTimer);

                // Transition through SILENCE_DETECTED to PROCESSING
                setSessionState(STATE_SILENCE_DETECTED, txtPromptSilence);
                setTimeout(function() {{
                    setSessionState(STATE_PROCESSING, 'YOU: "' + cleanCmd + '"');
                    try {{ recognition.stop(); }} catch(e) {{}}
                    handleRecognizedVoiceCommand(cleanCmd);
                    setTimeout(function() {{ commandDispatchLock = false; }}, 1200);
                }}, 250);
            }}

            recognition.onerror = function(event) {{
                if (event.error === 'no-speech') {{
                    if (sessionState === STATE_LISTENING) {{
                        setSessionState(STATE_WAKE_WORD_STANDBY, txtPromptWake);
                    }}
                    return;
                }} else if (event.error === 'not-allowed') {{
                    setMicStatus('DENIED');
                    setSessionState(STATE_ERROR, 'Microphone permission required. Please allow mic in address bar.');
                    pauseVoiceSession();
                }} else if (event.error === 'network') {{
                    if (sessionState === STATE_LISTENING || sessionState === STATE_WAKE_WORD_STANDBY) {{
                        setTimeout(startVoiceListening, 1500);
                    }}
                }}
            }};

            recognition.onend = function() {{
                if (sessionState === STATE_LISTENING || sessionState === STATE_WAKE_WORD_STANDBY) {{
                    if (restartDebounceTimer) clearTimeout(restartDebounceTimer);
                    restartDebounceTimer = setTimeout(function() {{
                        if (sessionState === STATE_LISTENING || sessionState === STATE_WAKE_WORD_STANDBY) {{
                            try {{
                                recognition.start();
                            }} catch(e) {{
                                startVoiceListening();
                            }}
                        }}
                    }}, 250);
                }}
            }};

            recognition.start();
        }} catch(err) {{
            console.warn("[AURA] Could not start speech recognition:", err);
            setSessionState(STATE_WAKE_WORD_STANDBY, txtPromptWake);
        }}
    }}

    // Tab visibility handling: suspend recognition when tab is hidden, resume on foreground
    document.addEventListener('visibilitychange', function() {{
        if (document.hidden) {{
            if (recognition && sessionState === STATE_WAKE_WORD_STANDBY) {{
                try {{ recognition.abort(); }} catch(e) {{}}
            }}
        }} else {{
            if (sessionState === STATE_WAKE_WORD_STANDBY || sessionState === STATE_LISTENING) {{
                setTimeout(startVoiceListening, 300);
            }}
        }}
    }});

    // -------------------------------------------------------------------------
    // INDEPENDENT DASHBOARD VOICE EVENT HANDLERS
    // -------------------------------------------------------------------------
    function startDashboardVoice() {{
        dashboardVoiceActive = true;
        dashboardIsListening = true;
        isListening = true;
        setSessionState(STATE_LISTENING, txtListening);
        startVoiceListening();
    }}

    function stopDashboardVoice() {{
        dashboardVoiceActive = false;
        dashboardIsListening = false;
        isListening = false;
        setSessionState(STATE_STOPPED, 'Voice session paused. Click RESUME or speak to continue.');
        stopOngoingSpeech();
        if (dashboardRecognition) {{
            try {{ dashboardRecognition.abort(); }} catch(e) {{}}
        }}
        if (silenceTimer) clearTimeout(silenceTimer);
        if (extendedSilenceTimer) clearTimeout(extendedSilenceTimer);
        currentSpeechBuffer = '';
    }}

    function handleDashboardTranscript(rawTranscript) {{
        dashboardTranscript = rawTranscript;
        var tBox = document.getElementById('transcriptBox');
        if (tBox && rawTranscript) tBox.innerText = '🎙️ "' + rawTranscript + '"';
    }}

    function handleDashboardVoiceError(error) {{
        dashboardIsListening = false;
        isListening = false;
        if (error && (error.error === 'not-allowed' || error === 'not-allowed')) {{
            setMicStatus('DENIED');
            setSessionState(STATE_ERROR, 'Microphone permission required. Please allow mic in address bar.');
            stopDashboardVoice();
        }} else if (error && error.error === 'no-speech') {{
            if (sessionState === STATE_LISTENING) {{
                setSessionState(STATE_WAKE_WORD_STANDBY, txtPromptWake);
            }}
        }}
    }}

    function speakDashboardVoice(textToSpeak, onDone) {{
        speakJarvis(textToSpeak, onDone);
    }}

    // Backward-compatible global controls
    window.startDashboardVoice = startDashboardVoice;
    window.stopDashboardVoice = stopDashboardVoice;
    window.handleDashboardTranscript = handleDashboardTranscript;
    window.handleDashboardVoiceError = handleDashboardVoiceError;
    window.speakDashboardVoice = speakDashboardVoice;

    window.startVoiceSession = startDashboardVoice;
    window.pauseVoiceSession = stopDashboardVoice;
    window.resumeVoiceSession = function() {{
        setSessionState(STATE_WAKE_WORD_STANDBY, txtPromptWake);
        startVoiceListening();
    }};
    window.endVoiceSession = stopDashboardVoice;

    window.pauseVoiceSession = function() {{
        setSessionState(STATE_STOPPED, 'Voice session paused. Click RESUME or speak to continue.');
        stopOngoingSpeech();
        if (recognition) {{
            try {{ recognition.abort(); }} catch(e) {{}}
        }}
        if (silenceTimer) clearTimeout(silenceTimer);
        if (extendedSilenceTimer) clearTimeout(extendedSilenceTimer);
        currentSpeechBuffer = '';
    }};

    window.resumeVoiceSession = function() {{
        setSessionState(STATE_WAKE_WORD_STANDBY, txtPromptWake);
        startVoiceListening();
    }};

    window.endVoiceSession = function() {{
        setSessionState(STATE_STOPPED, 'AURA is offline. Click START AURA to begin voice session.');
        stopOngoingSpeech();
        if (recognition) {{
            try {{ recognition.abort(); }} catch(e) {{}}
            recognition = null;
        }}
        if (silenceTimer) clearTimeout(silenceTimer);
        if (extendedSilenceTimer) clearTimeout(extendedSilenceTimer);
        currentSpeechBuffer = '';
    }};

    window.togglePersistentVoiceSession = function() {{
        if (sessionState === STATE_STOPPED || sessionState === 'PAUSED' || sessionState === STATE_ERROR) {{
            startVoiceSession();
        }} else if (sessionState === STATE_LISTENING || sessionState === STATE_PROCESSING || sessionState === STATE_SPEAKING) {{
            pauseVoiceSession();
        }} else if (sessionState === STATE_WAKE_WORD_STANDBY) {{
            // Manual click when in standby -> trigger direct active listening
            startVoiceSession();
        }}
    }};

    // Backward-compatibility alias
    window.AURA_TOGGLE_MIC = window.togglePersistentVoiceSession;

    // EXPORT useDashboardVoice() independent module / custom hook
    window.useDashboardVoice = function() {{
        return {{
            type: 'dashboard_voice',
            dashboardIsListening: dashboardIsListening,
            dashboardTranscript: dashboardTranscript,
            dashboardVoiceActive: dashboardVoiceActive,
            dashboardRecognition: dashboardRecognition,
            dashboardSpeechOutput: dashboardSpeechOutput,
            isListening: function() {{ return dashboardIsListening; }},
            getTranscript: function() {{ return dashboardTranscript; }},
            isVoiceActive: function() {{ return dashboardVoiceActive; }},
            getRecognition: function() {{ return dashboardRecognition; }},
            getSpeechOutput: function() {{ return dashboardSpeechOutput; }},
            getState: function() {{ return sessionState; }},
            startDashboardVoice: startDashboardVoice,
            stopDashboardVoice: stopDashboardVoice,
            handleDashboardTranscript: handleDashboardTranscript,
            handleDashboardVoiceError: handleDashboardVoiceError,
            speakDashboardVoice: speakDashboardVoice,
            startListening: startDashboardVoice,
            stopListening: stopDashboardVoice,
            speak: speakDashboardVoice,
            setWakeWordEnabled: function(val) {{ voiceConfig.wakeWordEnabled = !!val; }},
            isWakeWordStandby: function() {{ return sessionState === STATE_WAKE_WORD_STANDBY; }},
            isAudioLocked: function() {{
                try {{ return localStorage.getItem('aura_active_speaker') === 'chatbot'; }} catch(e) {{ return false; }}
            }}
        }};
    }};

    // Cleanup and lifecycle on unmount
    window.addEventListener('beforeunload', function() {{ stopDashboardVoice(); }});
    window.addEventListener('pagehide', function() {{ stopDashboardVoice(); }});

    window.highlightOrbitalBeam = function(beamId, active) {{
        try {{
            var beam = document.getElementById(beamId);
            if (beam) {{
                if (active) {{
                    beam.classList.add('beam-active');
                }} else {{
                    beam.classList.remove('beam-active');
                }}
            }}
        }} catch(e) {{}}
    }};

    window.dispatchCardNav = function(phrase, nodeElem) {{
        try {{
            if (nodeElem) {{
                document.querySelectorAll('.holo-module-node').forEach(function(el) {{ el.classList.remove('active-node'); }});
                nodeElem.classList.add('active-node');
            }}
        }} catch(e) {{}}
        stopOngoingSpeech();
        setSessionState(STATE_PROCESSING, 'Executing: ' + phrase);
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

    // Real-Time Command Intent & Dynamic Spoken Voice Feedback
    function handleRecognizedVoiceCommand(rawCmd) {{
        var cmd = (rawCmd || '').trim();
        if (!cmd) {{
            setSessionState(STATE_WAKE_WORD_STANDBY, txtPromptWake);
            return;
        }}

        var cmdId = 'aura_vcmd_' + Date.now();
        var lower = cmd.toLowerCase();

        var spokenResponse = "Processing command.";
        if (/navigation|navigate|route|map|directions/i.test(lower)) {{
            spokenResponse = "Opening navigation.";
        }} else if (/hotel|stay|resort|accommodation/i.test(lower)) {{
            spokenResponse = "Let's find hotels.";
        }} else if (/flight|airline|fly|airport/i.test(lower)) {{
            spokenResponse = "Opening flight planner.";
        }} else if (/restaurant|food|dining|eat|cafe/i.test(lower)) {{
            spokenResponse = "Finding nearby restaurants.";
        }} else if (/profile|account|my account/i.test(lower)) {{
            spokenResponse = "Opening your profile.";
        }} else if (/booking|bookings|reservation/i.test(lower)) {{
            spokenResponse = "Opening your bookings.";
        }} else if (/trips|itinerary/i.test(lower)) {{
            spokenResponse = "Here are your trips.";
        }} else if (/back|previous/i.test(lower)) {{
            spokenResponse = "Going back.";
        }} else if (/home|dashboard|main/i.test(lower)) {{
            spokenResponse = "Returning to home dashboard.";
        }} else if (/settings|config|preferences/i.test(lower)) {{
            spokenResponse = "Opening settings.";
        }}

        var dispatched = sendCommandToStreamlit(cmd, cmdId);

        speakJarvis(spokenResponse, function() {{
            setSessionState(STATE_WAKE_WORD_STANDBY, txtPromptWake);
            setTimeout(startVoiceListening, 400);
        }});
    }}

    // -------------------------------------------------------------------------
    // Automatic Startup Greeting with Autoplay Recovery
    // -------------------------------------------------------------------------
    var greetingTriggered = false;
    var greetingActuallySpoken = false;

    function triggerStartupGreeting() {{
        if (greetingTriggered) return;
        var sessionKey = 'aura_greeted_' + activeLang;
        try {{
            if (sessionStorage.getItem(sessionKey) === 'true') {{
                greetingTriggered = true;
                setSessionState(STATE_WAKE_WORD_STANDBY, txtPromptWake);
                setTimeout(startVoiceListening, 300);
                return;
            }}
        }} catch(e) {{}}

        if (!shouldAutoSpeak) {{
            greetingTriggered = true;
            setSessionState(STATE_WAKE_WORD_STANDBY, txtPromptWake);
            setTimeout(startVoiceListening, 300);
            return;
        }}

        greetingTriggered = true;
        try {{ sessionStorage.setItem(sessionKey, 'true'); }} catch(e) {{}}

        setSessionState(STATE_GREETING, clientGreeting);

        speakJarvis(clientGreeting, function() {{
            greetingActuallySpoken = true;
            // After greeting finishes, automatically enter Wake-Word Standby Loop
            setSessionState(STATE_WAKE_WORD_STANDBY, txtPromptWake);
            setTimeout(startVoiceListening, 350);
        }});
    }}

    // Minimal first-interaction fallback (unblocks speech if browser blocks autoplay before user touch)
    function unlockAudioOnFirstInteraction() {{
        if (synthesis && synthesis.paused) {{
            try {{ synthesis.resume(); }} catch(e) {{}}
        }}
        if (!greetingActuallySpoken && shouldAutoSpeak) {{
            greetingActuallySpoken = true;
            setSessionState(STATE_GREETING, clientGreeting);
            speakJarvis(clientGreeting, function() {{
                setSessionState(STATE_WAKE_WORD_STANDBY, txtPromptWake);
                setTimeout(startVoiceListening, 350);
            }});
        }} else if (sessionState === STATE_WAKE_WORD_STANDBY && !isListening && !isSpeaking) {{
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
