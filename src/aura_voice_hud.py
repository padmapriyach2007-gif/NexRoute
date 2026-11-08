"""
NexRoute — AURA Global JARVIS-Style Voice Assistant HUD & Holographic Interface
Provides a futuristic circular avatar, real-time waveform visualizer,
Web Speech API speech synthesis & recognition, multilingual command routing,
hands-free wake word, push-to-talk, and seamless application integration.
"""

import json
from typing import Optional, Dict, Any


def render_aura_jarvis_hud_html(
    current_lang: str = "en",
    voice_enabled: bool = True,
    wake_word_enabled: bool = False,
    active_state: str = "idle",
    last_spoken_text: str = "",
    last_transcript: str = "",
    bot_logo_uri: Optional[str] = None
) -> str:
    """
    Builds the standalone futuristic JARVIS-style HUD with responsive
    Web Speech API STT and TTS, real-time waveform canvas, and voice command dispatching.
    """
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

    return f"""<!DOCTYPE html>
<html lang="{current_lang}">
<head>
<meta charset="utf-8">
<style>
* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    user-select: none;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
}}
body {{
    background: transparent;
    overflow: hidden;
    color: #f8fafc;
}}
.aura-jarvis-card {{
    background: radial-gradient(120% 120% at 50% 0%, rgba(15, 23, 42, 0.96) 0%, rgba(3, 7, 18, 0.98) 100%);
    border: 1.5px solid rgba(56, 189, 248, 0.45);
    border-radius: 20px;
    padding: 16px;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.75), 0 0 30px rgba(0, 240, 255, 0.22);
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    width: 100%;
    max-width: 440px;
    margin: 0 auto;
}}

/* Arc Reactor Avatar */
.aura-avatar-wrapper {{
    position: relative;
    width: 88px;
    height: 88px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 10px;
    cursor: pointer;
}}
.aura-pulse-ring {{
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 2px solid rgba(0, 240, 255, 0.6);
    animation: auraPulse 2.4s infinite ease-out;
}}
.aura-core-circle {{
    width: 72px;
    height: 72px;
    border-radius: 50%;
    background: radial-gradient(circle, #0284c7 0%, #0369a1 40%, #082f49 100%);
    border: 2.5px solid #38bdf8;
    box-shadow: 0 0 24px rgba(0, 240, 255, 0.75), inset 0 0 16px rgba(0, 240, 255, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    z-index: 2;
}}
.aura-core-circle.listening {{
    border-color: #34d399;
    box-shadow: 0 0 32px rgba(52, 211, 153, 0.9), inset 0 0 20px rgba(52, 211, 153, 0.6);
    animation: listeningPulse 1.2s infinite ease-in-out;
}}
.aura-core-circle.speaking {{
    border-color: #f59e0b;
    box-shadow: 0 0 32px rgba(245, 158, 11, 0.9), inset 0 0 20px rgba(245, 158, 11, 0.6);
    animation: speakingPulse 0.9s infinite alternate;
}}
.aura-icon-glyph {{
    font-size: 32px;
    filter: drop-shadow(0 0 8px rgba(255,255,255,0.7));
}}

@keyframes auraPulse {{
    0% {{ transform: scale(0.9); opacity: 0.9; }}
    50% {{ transform: scale(1.22); opacity: 0.35; }}
    100% {{ transform: scale(1.35); opacity: 0; }}
}}
@keyframes listeningPulse {{
    0% {{ transform: scale(1); }}
    50% {{ transform: scale(1.08); }}
    100% {{ transform: scale(1); }}
}}
@keyframes speakingPulse {{
    0% {{ transform: scale(1); }}
    100% {{ transform: scale(1.06); }}
}}

/* Assistant Header & Status Badge */
.aura-header {{
    text-align: center;
    margin-bottom: 8px;
}}
.aura-title {{
    font-size: 1.05rem;
    font-weight: 900;
    letter-spacing: 1.5px;
    background: linear-gradient(135deg, #38bdf8 0%, #00f0ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-transform: uppercase;
}}
.aura-status-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(14, 165, 233, 0.15);
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 0.72rem;
    font-weight: 800;
    color: #38bdf8;
    margin-top: 4px;
}}
.status-indicator-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #00f0ff;
    box-shadow: 0 0 8px #00f0ff;
}}

/* Equalizer Waveform Canvas */
.waveform-container {{
    width: 100%;
    height: 38px;
    background: rgba(2, 6, 23, 0.65);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 8px;
    margin: 8px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}}
canvas#auraWaveformCanvas {{
    width: 100%;
    height: 100%;
}}

/* Dialogue Transcript Box */
.aura-dialogue-box {{
    width: 100%;
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 10px;
    padding: 10px 12px;
    font-size: 0.82rem;
    line-height: 1.35;
    color: #e2e8f0;
    min-height: 48px;
    max-height: 90px;
    overflow-y: auto;
    margin-bottom: 10px;
    text-align: center;
}}

/* Interactive Control Bar */
.aura-control-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 6px;
    width: 100%;
    margin-bottom: 10px;
}}
.hud-btn {{
    background: rgba(30, 41, 59, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 10px;
    color: #f1f5f9;
    font-size: 0.74rem;
    font-weight: 700;
    padding: 7px 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
}}
.hud-btn:hover {{
    background: rgba(56, 189, 248, 0.22);
    border-color: #38bdf8;
    color: #38bdf8;
}}
.hud-btn.primary {{
    background: linear-gradient(135deg, #0284c7 0%, #00f0ff 100%);
    color: #030712;
    border: none;
    box-shadow: 0 0 14px rgba(0, 240, 255, 0.45);
}}
.hud-btn.primary:hover {{
    transform: scale(1.02);
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.75);
}}

/* Quick Command Action Chips */
.quick-chips-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    justify-content: center;
    width: 100%;
    margin-top: 4px;
}}
.cmd-chip {{
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 14px;
    padding: 3px 9px;
    font-size: 0.69rem;
    color: #94a3b8;
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
}}
.cmd-chip:hover {{
    background: rgba(56, 189, 248, 0.2);
    border-color: #38bdf8;
    color: #38bdf8;
    transform: translateY(-1px);
}}
</style>
</head>
<body>

<div class="aura-jarvis-card" id="auraJarvisCard">
    <!-- Circular Avatar with Pulse Rings -->
    <div class="aura-avatar-wrapper" id="auraAvatarWrapper" onclick="toggleListening()">
        <div class="aura-pulse-ring"></div>
        <div class="aura-core-circle" id="auraCore">
            <span class="aura-icon-glyph" id="auraGlyph">🤖</span>
        </div>
    </div>

    <!-- Title and Status -->
    <div class="aura-header">
        <div class="aura-title">AURA • JARVIS COPILOT</div>
        <div class="aura-status-pill" id="auraStatusPill">
            <span class="status-indicator-dot" id="statusDot"></span>
            <span id="statusText">AURA STANDBY</span>
        </div>
    </div>

    <!-- Dialogue Box -->
    <div class="aura-dialogue-box" id="auraDialogue">
        Hello, Boss! I'm AURA, your personal NexRoute assistant. What would you like me to do?
    </div>

    <!-- Live Animated Waveform -->
    <div class="waveform-container">
        <canvas id="auraWaveformCanvas"></canvas>
    </div>

    <!-- Controls -->
    <div class="aura-control-grid">
        <button class="hud-btn primary" id="btnMicAction" onclick="toggleListening()">
            🎙️ Speak
        </button>
        <button class="hud-btn" id="btnSilence" onclick="silenceAssistant()">
            🔇 Silence
        </button>
        <button class="hud-btn" id="btnOpenChat" onclick="openFullChatbot()">
            💬 Chatbot
        </button>
    </div>

    <!-- Quick Voice Command Suggestions -->
    <div class="quick-chips-row">
        <span class="cmd-chip" onclick="dispatchDirectCommand('Open navigation')">🧭 Navigation</span>
        <span class="cmd-chip" onclick="dispatchDirectCommand('Switch to satellite view')">🛰️ Satellite</span>
        <span class="cmd-chip" onclick="dispatchDirectCommand('Show my current location')">📍 My Location</span>
        <span class="cmd-chip" onclick="dispatchDirectCommand('Find hospitals nearby')">🏥 Hospitals</span>
        <span class="cmd-chip" onclick="dispatchDirectCommand('Find petrol stations nearby')">⛽ Fuel</span>
        <span class="cmd-chip" onclick="dispatchDirectCommand('Fit route')">🔍 Fit Route</span>
        <span class="cmd-chip" onclick="dispatchDirectCommand('Calculate fuel expenses')">⛽ Fuel Calc</span>
    </div>
</div>

<script>
(function() {{
    var activeLang = {json.dumps(current_lang)};
    var bcp47Lang = {json.dumps(bcp47_code)};
    var voiceGreetingEnabled = {json.dumps(bool(voice_enabled))};
    var isListening = false;
    var isSpeaking = false;
    var recognition = null;
    var synthesis = window.speechSynthesis;
    var currentUtterance = null;
    var canvas = document.getElementById('auraWaveformCanvas');
    var ctx = canvas ? canvas.getContext('2d') : null;
    var animFrame = null;
    var wavePhase = 0;

    // Initialize Canvas Dimensions
    function initCanvas() {{
        if (!canvas) return;
        canvas.width = canvas.offsetWidth || 340;
        canvas.height = canvas.offsetHeight || 38;
    }}
    initCanvas();
    window.addEventListener('resize', initCanvas);

    // Waveform Animation Loop
    function drawWaveform() {{
        if (!ctx || !canvas) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        var bars = 28;
        var barWidth = canvas.width / bars - 3;
        var midY = canvas.height / 2;

        for (var i = 0; i < bars; i++) {{
            var factor = Math.sin(wavePhase + (i * 0.35));
            var amplitude = (isListening || isSpeaking) ? Math.abs(factor) * (midY - 4) + 4 : 3;
            var barHeight = Math.max(3, amplitude);

            var grad = ctx.createLinearGradient(0, midY - barHeight, 0, midY + barHeight);
            if (isListening) {{
                grad.addColorStop(0, '#34d399');
                grad.addColorStop(1, '#059669');
            }} else if (isSpeaking) {{
                grad.addColorStop(0, '#f59e0b');
                grad.addColorStop(1, '#d97706');
            }} else {{
                grad.addColorStop(0, '#38bdf8');
                grad.addColorStop(1, '#0284c7');
            }}

            ctx.fillStyle = grad;
            ctx.fillRect(i * (barWidth + 3) + 2, midY - barHeight / 2, barWidth, barHeight);
        }}
        wavePhase += (isListening || isSpeaking) ? 0.15 : 0.04;
        animFrame = requestAnimationFrame(drawWaveform);
    }}
    drawWaveform();

    // Assistant State Management
    function setAssistantState(state, text) {{
        var core = document.getElementById('auraCore');
        var dot = document.getElementById('statusDot');
        var statusLabel = document.getElementById('statusText');
        var micBtn = document.getElementById('btnMicAction');
        var glyph = document.getElementById('auraGlyph');

        if (core) {{
            core.classList.remove('listening', 'speaking');
            if (state === 'listening') core.classList.add('listening');
            if (state === 'speaking') core.classList.add('speaking');
        }}

        if (dot) {{
            if (state === 'listening') dot.style.background = '#34d399';
            else if (state === 'speaking') dot.style.background = '#f59e0b';
            else if (state === 'processing') dot.style.background = '#a855f7';
            else dot.style.background = '#00f0ff';
        }}

        if (statusLabel) statusLabel.innerText = state.toUpperCase();
        if (glyph) {{
            if (state === 'listening') glyph.innerText = '🎙️';
            else if (state === 'speaking') glyph.innerText = '🔊';
            else glyph.innerText = '🤖';
        }}
        if (micBtn) {{
            micBtn.innerHTML = (state === 'listening') ? '⏹️ Stop' : '🎙️ Speak';
        }}
        if (text) {{
            var box = document.getElementById('auraDialogue');
            if (box) box.innerText = text;
        }}
    }}

    // Spoken Audio Output (SpeechSynthesis)
    window.speakAssistant = function(text, onEndCallback) {{
        if (!synthesis || !voiceGreetingEnabled) {{
            if (onEndCallback) onEndCallback();
            return;
        }}
        try {{
            synthesis.cancel();
            isSpeaking = true;
            setAssistantState('speaking', text);

            currentUtterance = new SpeechSynthesisUtterance(text);
            currentUtterance.lang = bcp47Lang;
            currentUtterance.rate = 1.02;
            currentUtterance.pitch = 1.0;

            var voices = synthesis.getVoices();
            var matchedVoice = voices.find(function(v) {{
                return v.lang && (v.lang === bcp47Lang || v.lang.startsWith(activeLang));
            }});
            if (matchedVoice) currentUtterance.voice = matchedVoice;

            currentUtterance.onend = function() {{
                isSpeaking = false;
                setAssistantState('idle');
                if (onEndCallback) onEndCallback();
            }};
            currentUtterance.onerror = function() {{
                isSpeaking = false;
                setAssistantState('idle');
                if (onEndCallback) onEndCallback();
            }};
            synthesis.speak(currentUtterance);
        }} catch(e) {{
            isSpeaking = false;
            setAssistantState('idle');
        }}
    }};

    // Silence
    window.silenceAssistant = function() {{
        if (synthesis) synthesis.cancel();
        if (recognition && isListening) {{
            try {{ recognition.stop(); }} catch(e) {{}}
        }}
        isSpeaking = false;
        isListening = false;
        setAssistantState('idle', 'Silenced. Standing by for commands.');
    }};

    // Dispatch Command to Parent Application
    window.dispatchDirectCommand = function(cmdText) {{
        if (!cmdText || !cmdText.trim()) return;
        setAssistantState('processing', 'Executing: "' + cmdText + '"');

        // 1. PostMessage to Parent Window
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

        // 2. Set Streamlit Query Params to execute real action
        try {{
            var targetWin = window.parent || window.top || window;
            var currentHref = '';
            try {{ currentHref = targetWin.location.href; }} catch(e) {{ currentHref = window.location.href; }}
            var url = new URL(currentHref);
            url.searchParams.set('aura_cmd', cmdText.trim());
            try {{
                targetWin.location.href = url.toString();
            }} catch(eNav) {{
                window.location.href = url.toString();
            }}
        }} catch(eParam) {{}}
    }};

    // Web Speech API Voice Recognition
    window.toggleListening = function() {{
        if (isListening) {{
            if (recognition) try {{ recognition.stop(); }} catch(e) {{}}
            isListening = false;
            setAssistantState('idle');
            return;
        }}

        var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {{
            setAssistantState('idle', 'Voice recognition requires Chrome, Edge, or Safari.');
            return;
        }}

        try {{
            recognition = new SpeechRecognition();
            recognition.lang = bcp47Lang;
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onstart = function() {{
                isListening = true;
                setAssistantState('listening', 'Listening for your command...');
            }};

            recognition.onresult = function(event) {{
                isListening = false;
                var transcript = event.results[0][0].transcript;
                if (transcript) {{
                    setAssistantState('processing', 'Heard: "' + transcript + '"');
                    dispatchDirectCommand(transcript);
                }}
            }};

            recognition.onerror = function(err) {{
                isListening = false;
                setAssistantState('idle', 'Voice input error or mic permission denied.');
            }};

            recognition.onend = function() {{
                isListening = false;
                if (!isSpeaking) setAssistantState('idle');
            }};

            recognition.start();
        }} catch(eStart) {{
            isListening = false;
            setAssistantState('idle', 'Microphone not accessible.');
        }}
    }};

    // Open Chatbot
    window.openFullChatbot = function() {{
        dispatchDirectCommand('Open chatbot');
    }};

    // Initial greeting on load
    setTimeout(function() {{
        if (voiceGreetingEnabled) {{
            var greetText = {json.dumps(last_spoken_text)} || "Hello, Boss! I'm AURA, your personal NexRoute assistant. What would you like me to do?";
            window.speakAssistant(greetText);
        }}
    }}, 600);

}})();
</script>

</body>
</html>
"""


def get_jarvis_startup_greeting(lang: str = "en", user_name: str = "Boss") -> str:
    """
    Returns the time-appropriate startup greeting matching:
    'Good morning, Boss! Welcome to NextRoute. How can I help you?'
    """
    import datetime
    now_hour = datetime.datetime.now().hour
    if 5 <= now_hour < 12:
        tod_en = "Good morning"
        tod_te = "శుభోదయం"
        tod_hi = "सुप्रभात"
        tod_ta = "காலை வணக்கம்"
        tod_kn = "ಶುಭೋದಯ"
        tod_ml = "സുപ്രഭാതം"
    elif 12 <= now_hour < 17:
        tod_en = "Good afternoon"
        tod_te = "నమస్కారం"
        tod_hi = "नमस्ते"
        tod_ta = "வணக்கம்"
        tod_kn = "ನಮಸ್ಕಾರ"
        tod_ml = "നമസ്കാരം"
    elif 17 <= now_hour < 22:
        tod_en = "Good evening"
        tod_te = "శుభ సాయంత్రం"
        tod_hi = "शुभ संध्या"
        tod_ta = "மாலை வணக்கம்"
        tod_kn = "ಶುಭ ಸಂಜೆ"
        tod_ml = "ശുഭ സായാഹ്നം"
    else:
        tod_en = "Good evening"
        tod_te = "శుభ సాయంత్రం"
        tod_hi = "शुभ संध्या"
        tod_ta = "மாலை வணக்கம்"
        tod_kn = "ಶುಭ ಸಂಜೆ"
        tod_ml = "ശുഭ സായാഹ്നം"

    if lang == "te":
        return f"{tod_te}, {user_name}! నెక్స్‌రూట్‌కి స్వాగతం. నేను మీకు ఎలా సహాయపడగలను?"
    elif lang == "hi":
        return f"{tod_hi}, {user_name}! नेक्स-रूट में आपका स्वागत है। मैं आपकी क्या मदद कर सकता हूँ?"
    elif lang == "ta":
        return f"{tod_ta}, {user_name}! நெக்ஸ்-ரூட்டிற்கு நல்வரவு. நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?"
    elif lang == "kn":
        return f"{tod_kn}, {user_name}! ನೆಕ್ಸ್-ರೂಟ್‌ಗೆ ಸುಸ್ವಾಗತ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?"
    elif lang == "ml":
        return f"{tod_ml}, {user_name}! നെക്സ്-റൂട്ടിലേക്ക് സ്വാഗതം. ഞാൻ എങ്ങനെ സഹായിക്കണം?"
    else:
        return f"{tod_en}, {user_name}! Welcome to NextRoute. How can I help you?"


def render_jarvis_chatbot_hud_html(
    current_lang: str = "en",
    bot_logo_uri: Optional[str] = None,
    auto_greeting_text: str = "",
    last_response_text: str = "",
    key_prefix: str = "main"
) -> str:
    """
    Renders the unified Jarvis Voice Assistant interface header for the AURA Chatbot.
    Features the circular robot avatar, live status indicators (LISTENING, THINKING, SPEAKING, IDLE),
    real-time canvas waveform, microphone voice input that automatically fills the chatbot prompt
    and submits to the agent, and audible Text-to-Speech playback.
    """
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
        f'<img src="{bot_logo_uri}" class="jarvis-avatar-img" alt="AURA Mascot" />'
        if bot_logo_uri
        else '<span style="color: #00f0ff; font-size: 20px; font-weight: 900;">⚡</span>'
    )

    return f"""<!DOCTYPE html>
<html lang="{current_lang}">
<head>
<meta charset="utf-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&family=JetBrains+Mono:wght@600;700;800&display=swap');

    * {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
        user-select: none;
    }}

    body {{
        background: transparent;
        font-family: 'Inter', -apple-system, sans-serif;
        color: #f8fafc;
        padding: 4px;
        overflow: hidden;
    }}

    .jarvis-hud-card {{
        background: radial-gradient(circle at 20% 50%, rgba(14, 28, 54, 0.95) 0%, rgba(3, 7, 18, 0.98) 100%);
        border: 1.5px solid rgba(0, 240, 255, 0.35);
        border-radius: 16px;
        padding: 8px 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6), 0 0 16px rgba(0, 240, 255, 0.12);
        backdrop-filter: blur(12px);
    }}

    /* Circular Avatar with Glowing Orbital Ring */
    .avatar-pod {{
        position: relative;
        width: 44px;
        height: 44px;
        min-width: 44px;
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

    @keyframes spinArc {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}

    .avatar-circle {{
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: radial-gradient(circle, #0284c7 0%, #030712 90%);
        border: 1.5px solid #00f0ff;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.5);
    }}

    .jarvis-avatar-img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
    }}

    /* Title & Status Area */
    .info-center {{
        flex: 1 1 auto;
        min-width: 0;
        display: flex;
        flex-direction: column;
        gap: 2px;
    }}

    .brand-title-line {{
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .brand-name {{
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 0.86rem;
        color: #ffffff;
        letter-spacing: 0.04em;
    }}

    .brand-subtitle {{
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.62rem;
        color: #38bdf8;
        letter-spacing: 0.06em;
    }}

    .status-and-wave-row {{
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 1px;
    }}

    .status-badge {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 1px 7px;
        border-radius: 6px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        color: #34d399;
        letter-spacing: 0.04em;
        white-space: nowrap;
        transition: all 0.25s ease;
    }}

    .waveform-canvas-box {{
        flex: 1 1 auto;
        height: 20px;
        min-width: 60px;
        background: rgba(3, 7, 18, 0.45);
        border-radius: 6px;
        border: 1px solid rgba(56, 189, 248, 0.20);
        display: flex;
        align-items: center;
        overflow: hidden;
    }}

    #auraJarvisWaveform {{
        width: 100%;
        height: 100%;
    }}

    /* Action Buttons */
    .controls-right {{
        display: flex;
        align-items: center;
        gap: 6px;
        flex: 0 0 auto;
    }}

    .btn-hud-mic {{
        background: linear-gradient(135deg, #00f0ff 0%, #0284c7 100%);
        border: none;
        border-radius: 50%;
        width: 34px;
        height: 34px;
        min-width: 34px;
        color: #030712;
        font-size: 1.05rem;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 0 14px rgba(0, 240, 255, 0.5);
        transition: all 0.2s ease;
    }}

    .btn-hud-mic:hover {{
        transform: scale(1.08);
        box-shadow: 0 0 22px rgba(0, 240, 255, 0.85);
    }}

    .btn-hud-silence {{
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 8px;
        padding: 5px 8px;
        color: #94a3b8;
        font-size: 0.72rem;
        font-weight: 700;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        transition: all 0.2s ease;
    }}

    .btn-hud-silence:hover {{
        color: #f1f5f9;
        border-color: #00f0ff;
        background: rgba(0, 240, 255, 0.12);
    }}
</style>
</head>
<body>

<div class="jarvis-hud-card">
    <!-- Circular Avatar with Orbiting Ring -->
    <div class="avatar-pod" onclick="toggleJarvisVoiceRecognition()" title="Click to speak">
        <div class="arc-spin-ring" id="avatarArcRing"></div>
        <div class="avatar-circle">
            {avatar_markup}
        </div>
    </div>

    <!-- Center Info + Status + Waveform -->
    <div class="info-center">
        <div class="brand-title-line">
            <span class="brand-name">AURA • AI Guide</span>
            <span class="brand-subtitle">JARVIS VOICE COPILOT</span>
        </div>
        <div class="status-and-wave-row">
            <span class="status-badge" id="jarvisStatusBadge">● IDLE • READY</span>
            <div class="waveform-canvas-box">
                <canvas id="auraJarvisWaveform"></canvas>
            </div>
        </div>
    </div>

    <!-- Right Controls: Mic & Silence -->
    <div class="controls-right">
        <button class="btn-hud-mic" id="btnJarvisMic" onclick="toggleJarvisVoiceRecognition()" title="Start Voice Input (Speak to AURA)">
            🎙️
        </button>
        <button class="btn-hud-silence" id="btnJarvisSilence" onclick="stopJarvisSpeech()" title="Stop Assistant Speech (Silence)">
            🔇 Silence
        </button>
    </div>
</div>

<script>
(function() {{
    var activeLang = {json.dumps(current_lang)};
    var bcp47Lang = {json.dumps(bcp47_code)};
    var autoGreeting = {json.dumps(auto_greeting_text)};
    var lastResponse = {json.dumps(last_response_text)};

    var isListening = false;
    var isSpeaking = false;
    var isThinking = false;
    var recognition = null;
    var synthesis = window.speechSynthesis;
    var canvas = document.getElementById('auraJarvisWaveform');
    var ctx = canvas ? canvas.getContext('2d') : null;

    function resizeCanvas() {{
        if (!canvas) return;
        canvas.width = canvas.parentElement.clientWidth || 240;
        canvas.height = canvas.parentElement.clientHeight || 20;
    }}
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    function setHudState(state, message) {{
        var badge = document.getElementById('jarvisStatusBadge');
        var micBtn = document.getElementById('btnJarvisMic');
        var arcRing = document.getElementById('avatarArcRing');

        if (state === 'listening') {{
            isListening = true;
            isSpeaking = false;
            isThinking = false;
            if (badge) {{
                badge.innerText = '🎙️ LISTENING, BOSS...';
                badge.style.background = 'rgba(0, 240, 255, 0.22)';
                badge.style.borderColor = '#00f0ff';
                badge.style.color = '#00f0ff';
            }}
            if (micBtn) micBtn.style.boxShadow = '0 0 25px #00f0ff';
            if (arcRing) arcRing.style.borderColor = '#00f0ff';
        }} else if (state === 'thinking') {{
            isListening = false;
            isSpeaking = false;
            isThinking = true;
            if (badge) {{
                badge.innerText = '⚡ THINKING, BOSS...';
                badge.style.background = 'rgba(168, 85, 247, 0.22)';
                badge.style.borderColor = '#a855f7';
                badge.style.color = '#c084fc';
            }}
            if (micBtn) micBtn.style.boxShadow = '0 0 15px #a855f7';
            if (arcRing) arcRing.style.borderColor = '#a855f7';
        }} else if (state === 'speaking') {{
            isListening = false;
            isSpeaking = true;
            isThinking = false;
            if (badge) {{
                badge.innerText = '🔊 SPEAKING...';
                badge.style.background = 'rgba(56, 189, 248, 0.22)';
                badge.style.borderColor = '#38bdf8';
                badge.style.color = '#38bdf8';
            }}
            if (micBtn) micBtn.style.boxShadow = '0 0 14px rgba(0, 240, 255, 0.5)';
            if (arcRing) arcRing.style.borderColor = '#38bdf8';
        }} else {{
            isListening = false;
            isSpeaking = false;
            isThinking = false;
            if (badge) {{
                badge.innerText = '● IDLE • READY';
                badge.style.background = 'rgba(16, 185, 129, 0.15)';
                badge.style.borderColor = '#10b981';
                badge.style.color = '#34d399';
            }}
            if (micBtn) micBtn.style.boxShadow = '0 0 14px rgba(0, 240, 255, 0.5)';
            if (arcRing) arcRing.style.borderColor = '#00f0ff';
        }}
    }}

    // Waveform Animation Loop
    var wavePhase = 0;
    function drawWave() {{
        if (!ctx || !canvas) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        var numPoints = 48;
        var step = canvas.width / numPoints;
        var midY = canvas.height / 2;

        var baseAmp = isSpeaking ? 8 : (isListening ? 6 : (isThinking ? 4 : 2));
        var freq = isSpeaking ? 0.22 : (isListening ? 0.30 : (isThinking ? 0.40 : 0.10));

        ctx.beginPath();
        ctx.strokeStyle = isSpeaking ? '#00f0ff' : (isListening ? '#38bdf8' : (isThinking ? '#c084fc' : 'rgba(56, 189, 248, 0.35)'));
        ctx.lineWidth = isSpeaking || isListening ? 2 : 1.2;
        ctx.shadowBlur = isSpeaking ? 10 : 2;
        ctx.shadowColor = '#00f0ff';

        for (var i = 0; i <= numPoints; i++) {{
            var x = i * step;
            var envelope = Math.sin((i / numPoints) * Math.PI);
            var y = midY + Math.sin(i * freq + wavePhase) * (baseAmp * envelope);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }}
        ctx.stroke();

        wavePhase += isSpeaking ? 0.24 : (isListening ? 0.18 : (isThinking ? 0.30 : 0.05));
        requestAnimationFrame(drawWave);
    }}
    drawWave();

    // Voice Synthesis
    window.speakJarvis = function(text) {{
        if (!synthesis || !text) return;
        try {{
            synthesis.cancel();
            var utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = bcp47Lang;
            utterance.rate = 1.02;
            utterance.pitch = 1.0;

            utterance.onstart = function() {{
                setHudState('speaking');
            }};

            utterance.onend = function() {{
                setHudState('idle');
            }};

            utterance.onerror = function() {{
                setHudState('idle');
            }};

            synthesis.speak(utterance);
        }} catch(e) {{
            setHudState('idle');
        }}
    }};

    window.stopJarvisSpeech = function() {{
        if (synthesis) synthesis.cancel();
        if (recognition && isListening) {{
            try {{ recognition.stop(); }} catch(e) {{}}
        }}
        setHudState('idle');
    }};

    // Speech-to-Text Recognition and Automatic Submission
    window.toggleJarvisVoiceRecognition = function() {{
        if (isListening) {{
            if (recognition) try {{ recognition.stop(); }} catch(e) {{}}
            setHudState('idle');
            return;
        }}

        stopJarvisSpeech();

        var SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRec) {{
            alert('Speech recognition is not supported in this browser. Please use Google Chrome, Microsoft Edge, or Safari.');
            return;
        }}

        try {{
            recognition = new SpeechRec();
            recognition.lang = bcp47Lang;
            recognition.continuous = false;
            recognition.interimResults = false;

            recognition.onstart = function() {{
                setHudState('listening');
            }};

            recognition.onresult = function(event) {{
                var transcript = event.results[0][0].transcript;
                if (transcript && transcript.trim()) {{
                    setHudState('thinking');
                    window.submitVoiceToExistingAgent(transcript.trim());
                }}
            }};

            recognition.onerror = function() {{
                setHudState('idle');
            }};

            recognition.onend = function() {{
                if (!isThinking && !isSpeaking) setHudState('idle');
            }};

            recognition.start();
        }} catch(e) {{
            setHudState('idle');
        }}
    }};

    // Populate existing input and automatically submit to existing AI agent
    window.submitVoiceToExistingAgent = function(transcript) {{
        // 1. Populate visible Streamlit text input box in the parent document
        try {{
            var pDoc = window.parent.document;
            var inputElements = pDoc.querySelectorAll('input[aria-label="Ask Aura"], input[placeholder*="Ask Aura"], .aura-chatgpt-composer-wrapper input');
            for (var i = 0; i < inputElements.length; i++) {{
                inputElements[i].value = transcript;
                inputElements[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                inputElements[i].dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
        }} catch(eDom) {{}}

        // 2. PostMessage to Parent Window
        try {{
            var pWin = window.parent || window.top;
            if (pWin && pWin !== window) {{
                pWin.postMessage({{
                    type: 'AURA_CHAT_SPEECH_SUBMIT',
                    prompt: transcript
                }}, '*');
            }}
        }} catch(ePost) {{}}

        // 3. Trigger immediate rerun with pending_chat_prompt
        try {{
            var targetWin = window.parent || window.top || window;
            var currentHref = '';
            try {{ currentHref = targetWin.location.href; }} catch(e) {{ currentHref = window.location.href; }}
            var url = new URL(currentHref);
            url.searchParams.set('pending_chat_prompt', transcript);
            try {{
                targetWin.location.href = url.toString();
            }} catch(eNav) {{
                window.location.href = url.toString();
            }}
        }} catch(eParam) {{}}
    }};

    // Initial load: Play startup greeting or latest response
    setTimeout(function() {{
        if (lastResponse && lastResponse.trim()) {{
            window.speakJarvis(lastResponse.trim());
        }} else if (autoGreeting && autoGreeting.trim()) {{
            window.speakJarvis(autoGreeting.trim());
        }}
    }}, 400);

}})();
</script>
</body>
</html>
"""
