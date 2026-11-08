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
    - Morning (5:00 - 11:59): Good morning, Boss! Welcome to NextRoute. How can I help you?
    - Afternoon (12:00 - 16:59): Good afternoon, Boss! Welcome to NextRoute. How can I help you?
    - Evening (17:00 - 4:59): Good evening, Boss! Welcome to NextRoute. How can I help you?
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
    Renders the autonomous JARVIS-style voice assistant HUD for NextRoute.
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

    # Full Futuristic JARVIS Welcome HUD for Main Dashboard
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

    .aura-welcome-panel {{
        position: relative;
        width: 100%;
        max-width: 860px;
        background: radial-gradient(circle at 50% 20%, rgba(14, 28, 54, 0.95) 0%, rgba(3, 7, 18, 0.98) 100%);
        border: 1.5px solid rgba(0, 240, 255, 0.38);
        border-radius: 20px;
        padding: 16px 24px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.75), 0 0 28px rgba(0, 240, 255, 0.16);
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        backdrop-filter: blur(20px);
        overflow: hidden;
    }}

    .aura-welcome-panel::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #00f0ff 50%, transparent 100%);
        opacity: 0.9;
    }}

    .welcome-top-row {{
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }}

    .brand-pill {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(0, 240, 255, 0.10);
        border: 1px solid rgba(0, 240, 255, 0.35);
        border-radius: 9999px;
        padding: 3px 12px;
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
        font-size: 0.68rem;
        font-weight: 700;
        padding: 3px 11px;
        border-radius: 9999px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        color: #34d399;
        letter-spacing: 0.06em;
        transition: all 0.3s ease;
    }}

    .avatar-wrapper {{
        position: relative;
        width: 66px;
        height: 66px;
        margin: 2px 0 6px 0;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }}

    .arc-reactor-ring-outer {{
        position: absolute;
        inset: -5px;
        border-radius: 50%;
        border: 1.5px dashed rgba(0, 240, 255, 0.45);
        animation: spinClockwise 14s linear infinite;
    }}

    .arc-reactor-ring-mid {{
        position: absolute;
        inset: -1px;
        border-radius: 50%;
        border: 2px solid rgba(56, 189, 248, 0.6);
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.35);
        animation: ringPulse 2.4s infinite ease-in-out;
        transition: box-shadow 0.3s ease;
    }}

    .avatar-core-circle {{
        width: 54px;
        height: 54px;
        border-radius: 50%;
        background: radial-gradient(circle, #0284c7 0%, #030712 90%);
        border: 2px solid #00f0ff;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 16px rgba(0, 240, 255, 0.6);
        z-index: 2;
        overflow: hidden;
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

    @keyframes ringPulse {{
        0%, 100% {{ transform: scale(1); opacity: 0.8; }}
        50% {{ transform: scale(1.05); opacity: 1; }}
    }}

    .greeting-headline {{
        font-size: 1.05rem;
        font-weight: 800;
        color: #f8fafc;
        margin: 2px 0 4px 0;
        line-height: 1.3;
        letter-spacing: -0.01em;
        background: linear-gradient(135deg, #ffffff 0%, #38bdf8 60%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .waveform-container {{
        width: 100%;
        max-width: 520px;
        height: 24px;
        margin: 3px 0 5px 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    #auraWaveCanvas {{
        width: 100%;
        height: 100%;
        display: block;
    }}

    .live-transcript-box {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.74rem;
        color: #38bdf8;
        min-height: 18px;
        line-height: 1.35;
        letter-spacing: 0.02em;
    }}
</style>
</head>
<body>

<div class="aura-welcome-panel" id="welcomePanel">
    <div class="welcome-top-row">
        <div class="brand-pill">
            <span class="brand-pulse-dot"></span>
            AURA • JARVIS AI COPILOT
        </div>
        <div class="status-badge" id="statusBadge">
            ● IDLE • READY
        </div>
    </div>

    <div class="avatar-wrapper" onclick="window.AURA_TOGGLE_MIC()" title="Click to speak with AURA">
        <div class="arc-reactor-ring-outer"></div>
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
        Ready for voice command, Boss.
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
    speech recognition, and React WebSocket communication bridge to Streamlit.
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
            if (midRing) midRing.style.boxShadow = '0 0 32px #00f0ff';
        }} else if (state === 'speaking') {{
            if (badge) {{
                badge.innerText = '🔊 SPEAKING...';
                badge.style.background = 'rgba(56, 189, 248, 0.22)';
                badge.style.borderColor = '#38bdf8';
                badge.style.color = '#38bdf8';
            }}
            if (midRing) midRing.style.boxShadow = '0 0 28px #38bdf8';
        }} else if (state === 'processing') {{
            if (badge) {{
                badge.innerText = '⚡ EXECUTING...';
                badge.style.background = 'rgba(168, 85, 247, 0.22)';
                badge.style.borderColor = '#a855f7';
                badge.style.color = '#c084fc';
            }}
            if (midRing) midRing.style.boxShadow = '0 0 28px #a855f7';
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
            if (midRing) midRing.style.boxShadow = '0 0 16px rgba(0, 240, 255, 0.35)';
        }}
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

        var baseAmp = isSpeaking ? 10 : (isListening ? 7 : 2.2);
        var freq = isSpeaking ? 0.18 : (isListening ? 0.24 : 0.08);

        ctx.beginPath();
        ctx.strokeStyle = isSpeaking ? '#00f0ff' : (isListening ? '#38bdf8' : 'rgba(56, 189, 248, 0.45)');
        ctx.lineWidth = isSpeaking || isListening ? 2.2 : 1.4;
        ctx.shadowBlur = isSpeaking ? 14 : (isListening ? 10 : 3);
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

    // Universal Speech Synthesis Engine (Handles Chrome GC, resume, and voice load bugs)
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

                // Select preferred natural voice if available
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
                }}

                // Safety watchdog timer: Chrome can silently pause or stall blocked synthesis indefinitely!
                var safetyTimeoutMs = Math.max(3200, (textToSpeak || '').length * 85);
                var watchdogTimer = setTimeout(function() {{
                    console.warn("[AURA] Speech synthesis timeout / autoplay restriction encountered. Proceeding to listening.");
                    finishUtterance();
                }}, safetyTimeoutMs);

                utterance.onstart = function() {{
                    isSpeaking = true;
                    setAssistantState('speaking', 'AURA: "' + textToSpeak + '"');
                }};

                utterance.onend = function() {{
                    finishUtterance();
                }};

                utterance.onerror = function(err) {{
                    finishUtterance();
                }};

                // Pin utterance to window so Chrome Garbage Collector does not drop it mid-speech
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

    // Real-Time Speech Recognition Engine (Speech-to-Text)
    function startVoiceListening() {{
        if (isSpeaking || isProcessing) return;

        var SpeechRec = null;
        try {{
            SpeechRec = (pWin && (pWin.SpeechRecognition || pWin.webkitSpeechRecognition)) ||
                        window.SpeechRecognition || window.webkitSpeechRecognition;
        }} catch(e) {{
            SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        }}

        if (!SpeechRec) {{
            setAssistantState('error', 'Speech recognition not supported in browser. Use Chrome or Edge.');
            return;
        }}

        // Stop any previous active recognition instance
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
                isListening = true;
                setAssistantState('listening', 'Listening, Boss... Speak your command.');
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

                if (interimTranscript && !finalTranscript) {{
                    var tBox = document.getElementById('transcriptBox');
                    if (tBox) tBox.innerText = '🎙️ "' + interimTranscript.trim() + '"';
                }}

                if (finalTranscript && finalTranscript.trim()) {{
                    var cleanFinal = finalTranscript.trim();
                    try {{ recognition.stop(); }} catch(e) {{}}
                    isListening = false;
                    handleRecognizedVoiceCommand(cleanFinal);
                }}
            }};

            recognition.onerror = function(event) {{
                if (event.error === 'no-speech') {{
                    // No speech within silence window is normal; keep listening
                    return;
                }} else if (event.error === 'not-allowed') {{
                    isListening = false;
                    setAssistantState('error', 'Microphone blocked. Please allow mic permissions in your address bar.');
                }} else if (event.error === 'network') {{
                    isListening = false;
                    setAssistantState('error', 'Speech recognition network error. Reconnecting...');
                    setTimeout(startVoiceListening, 1500);
                }} else {{
                    isListening = false;
                }}
            }};

            recognition.onend = function() {{
                isListening = false;
                // Auto-restart listening if not currently speaking or executing command
                if (!isSpeaking && !isProcessing) {{
                    setTimeout(function() {{
                        if (!isSpeaking && !isProcessing) {{
                            startVoiceListening();
                        }}
                    }}, 350);
                }}
            }};

            recognition.start();
        }} catch(err) {{
            isListening = false;
            setAssistantState('error', 'Microphone error: ' + (err.message || 'Check browser permissions'));
        }}
    }}

    window.AURA_TOGGLE_MIC = function() {{
        if (synthesis && (synthesis.speaking || synthesis.paused)) {{
            try {{ synthesis.cancel(); }} catch(e) {{}}
            isSpeaking = false;
        }}
        if (isListening && recognition) {{
            try {{ recognition.stop(); }} catch(e) {{}}
            isListening = false;
            setAssistantState('idle', 'Listening paused.');
        }} else {{
            if (synthesis && synthesis.paused) {{
                try {{ synthesis.resume(); }} catch(e) {{}}
            }}
            startVoiceListening();
        }}
    }};

    // Zero-Reload WebSocket Command Execution Bridge to Streamlit
    function sendCommandToStreamlit(cmdText, cmdId) {{
        try {{
            // 1. Direct WebSocket transmission through Streamlit hidden React input
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

        // 2. Fallback to URL searchParams navigation if bridge not mounted
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
        setAssistantState('processing', 'YOU: "' + cmdText + '"');

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
        }} else {{
            spokenResponse = "Processing: " + cmdText.substring(0, 28);
        }}

        var cmdId = 'cmd_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5);

        // 1. Speak response aloud immediately
        speakJarvis(spokenResponse, function() {{
            isProcessing = false;
            // 2. Automatically resume listening for the next voice command
            setTimeout(function() {{
                startVoiceListening();
            }}, 400);
        }});

        // 3. Simultaneously dispatch to Streamlit without reloading the page
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
                setAssistantState('idle', 'Ready for voice commands.');
                // Even if already greeted in previous tab run, start listening immediately!
                setTimeout(startVoiceListening, 500);
                return;
            }}
        }} catch(e) {{}}

        if (!shouldAutoSpeak) {{
            greetingTriggered = true;
            setAssistantState('idle', 'Ready for voice commands.');
            setTimeout(startVoiceListening, 500);
            return;
        }}

        greetingTriggered = true;
        try {{ sessionStorage.setItem(sessionKey, 'true'); }} catch(e) {{}}

        // Speak the natural initial greeting:
        // "Good morning, Boss! Welcome to NextRoute. How can I help you?"
        speakJarvis(initialGreetingText, function() {{
            greetingActuallySpoken = true;
            // Immediately after greeting finishes, activate microphone for voice commands!
            setTimeout(function() {{
                startVoiceListening();
            }}, 350);
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
                setTimeout(startVoiceListening, 350);
            }});
        }} else if (!isListening && !isSpeaking) {{
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
                // Close the temporary test stream immediately
                stream.getTracks().forEach(function(track) {{ track.stop(); }});
                // Launch greeting
                setTimeout(triggerStartupGreeting, 300);
            }})
            .catch(function(err) {{
                console.warn("[AURA] Mic permission notice:", err);
                // Still attempt greeting even if mic is denied initially
                setTimeout(triggerStartupGreeting, 300);
            }});
    }} else {{
        setTimeout(triggerStartupGreeting, 300);
    }}

}})();
</script>
"""
