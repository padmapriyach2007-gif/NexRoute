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

    window.toggleContinuousMode = function() {{
        continuousMode = !continuousMode;
        window.togglePersistentVoiceSession();
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

    window.toggleContinuousMode = function() {{
        continuousMode = !continuousMode;
        window.togglePersistentVoiceSession();
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


def get_chatbot_copilot_greeting(lang: str = "en") -> str:
    """
    Dedicated greeting for the AURA Travel Copilot Chatbot.
    Spoken automatically once when the chatbot interface opens.
    "Hello! I'm AURA, your travel copilot. What would you like to know today?"
    """
    greetings = {
        "en": "Hello! I'm AURA, your travel copilot. What would you like to know today?",
        "te": "హలో! నేను AURA, మీ ట్రావెల్ కోపైలట్. ఈరోజు మీరు ఏమి తెలుసుకోవాలనుకుంటున్నారు?",
        "hi": "नमस्ते! मैं ऑरा (AURA) हूँ, आपका ट्रैवल कोपायलट। आज आप क्या जानना चाहते हैं?",
        "ta": "வணக்கம்! நான் AURA, உங்கள் பயணக் கோபிலட். இன்று நீங்கள் என்ன தெரிந்து கொள்ள விரும்புகிறீர்கள்?",
        "kn": "ಹಲೋ! ನಾನು AURA, ನಿಮ್ಮ ಪ್ರಯಾಣ ಸಹಾಯಕ. ಇಂದು ನೀವು ಏನನ್ನು ತಿಳಿದುಕೊಳ್ಳಲು ಬಯಸುತ್ತೀರಿ?",
        "ml": "ഹലോ! ഞാൻ നിങ്ങളുടെ ട്രാവൽ കോപൈലറ്റ് AURA ആണ്. ഇന്ന് നിങ്ങൾക്ക് എന്താണ് അറിയേണ്ടത്?",
        "bn": "হ্যালো! আমি AURA, আপনার ভ্রমণ সহকারী। আজ আপনি কী জানতে চান?",
        "mr": "नमस्कार! मी AURA, तुमचा ट्रॅव्हल को-पायलट. आज तुम्हाला काय जाणून घ्यायचे आहे?",
        "es": "¡Hola! Soy AURA, tu copiloto de viajes. ¿Qué te gustaría saber hoy?",
        "fr": "Bonjour ! Je suis AURA, votre copilote de voyage. Que souhaitez-vous savoir aujourd'hui ?",
        "de": "Hallo! Ich bin AURA, Ihr Reise-Copilot. Was möchten Sie heute wissen?",
        "ja": "こんにちは！私は旅行コパイロットのAURAです。今日は何について知りたいですか？"
    }
    return greetings.get(lang, greetings["en"])


def render_jarvis_chatbot_hud_html(
    current_lang: str = "en",
    bot_logo_uri: Optional[str] = None,
    auto_greeting_text: str = "",
    last_response_text: str = "",
    key_prefix: str = "main",
    voice_enabled: bool = True,
    continuous_mode: bool = False,
    *args,
    **kwargs
) -> str:
    """
    Renders the dedicated AURA Travel Copilot Chatbot voice HUD and audio engine.
    Completely isolated from the Main Dashboard JARVIS assistant.
    Features:
    - Dedicated greeting: "Hello! I'm AURA, your travel copilot. What would you like to know today?"
    - Automatic speech reading of generated chatbot answers.
    - Automatic Voice Activity Detection (VAD) with configurable silence stopping.
    - State machine: INACTIVE, INITIALIZING, GREETING, IDLE, LISTENING, PROCESSING, SPEAKING, PAUSED, STOPPED.
    - Zero interference audio mutex lock with dashboard assistant.
    """
    bcp47_map = {
        "en": "en-IN",
        "te": "te-IN",
        "hi": "hi-IN",
        "ta": "ta-IN",
        "kn": "kn-IN",
        "ml": "ml-IN",
        "bn": "bn-IN",
        "mr": "mr-IN",
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

    initial_voice_state = "true" if voice_enabled else "false"

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
        background: radial-gradient(circle at 20% 50%, rgba(14, 28, 54, 0.96) 0%, rgba(3, 7, 18, 0.98) 100%);
        border: 1.5px solid rgba(0, 240, 255, 0.40);
        border-radius: 16px;
        padding: 8px 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.65), 0 0 18px rgba(0, 240, 255, 0.15);
        backdrop-filter: blur(14px);
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
        transition: border-color 0.3s ease;
    }}

    @keyframes spinArc {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}

    .avatar-circle {{
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: radial-gradient(circle, #0284c7 0%, #030712 100%);
        border: 1.5px solid #00f0ff;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.55);
        overflow: hidden;
    }}

    .jarvis-avatar-img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
    }}

    /* Title & Live Status */
    .info-center {{
        display: flex;
        flex-direction: column;
        flex: 1 1 auto;
        min-width: 140px;
        gap: 2px;
    }}

    .brand-title-line {{
        display: flex;
        align-items: center;
        gap: 6px;
    }}

    .brand-name {{
        font-size: 0.76rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: 0.04em;
    }}

    .brand-subtitle {{
        font-size: 0.58rem;
        font-weight: 700;
        color: #38bdf8;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.06em;
    }}

    .status-and-wave-row {{
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .status-badge {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.60rem;
        font-weight: 800;
        padding: 2px 7px;
        border-radius: 6px;
        border: 1px solid;
        letter-spacing: 0.04em;
        white-space: nowrap;
        transition: all 0.25s ease;
    }}

    .status-badge.idle {{
        background: rgba(56, 189, 248, 0.15);
        border-color: rgba(56, 189, 248, 0.45);
        color: #38bdf8;
    }}

    .status-badge.listening {{
        background: rgba(0, 240, 255, 0.20);
        border-color: #00f0ff;
        color: #00f0ff;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.35);
    }}

    .status-badge.thinking {{
        background: rgba(168, 85, 247, 0.20);
        border-color: #a855f7;
        color: #c084fc;
        box-shadow: 0 0 10px rgba(168, 85, 247, 0.35);
    }}

    .status-badge.speaking {{
        background: rgba(56, 189, 248, 0.20);
        border-color: #38bdf8;
        color: #38bdf8;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.35);
    }}

    .status-badge.paused {{
        background: rgba(245, 158, 11, 0.20);
        border-color: #f59e0b;
        color: #fbbf24;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.35);
    }}

    .status-badge.offline {{
        background: rgba(239, 68, 68, 0.15);
        border-color: #ef4444;
        color: #f87171;
    }}

    .waveform-canvas-box {{
        flex: 1 1 auto;
        height: 20px;
        min-width: 45px;
        background: rgba(3, 7, 18, 0.55);
        border-radius: 6px;
        border: 1px solid rgba(56, 189, 248, 0.22);
        display: flex;
        align-items: center;
        overflow: hidden;
    }}

    #auraJarvisWaveform {{
        width: 100%;
        height: 100%;
    }}

    /* Action Buttons: Smart Session Toggle, End Session, Voice Mute */
    .controls-right {{
        display: flex;
        align-items: center;
        gap: 6px;
        flex: 0 0 auto;
    }}

    /* Primary Persistent Voice Session Button */
    .btn-session-main {{
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.22) 0%, rgba(2, 132, 199, 0.40) 100%);
        border: 1.5px solid #00f0ff;
        border-radius: 8px;
        padding: 5px 12px;
        color: #00f0ff;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        white-space: nowrap;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.30);
        transition: all 0.2s ease;
    }}

    .btn-session-main:hover {{
        transform: translateY(-1px) scale(1.03);
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.65);
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

    /* End Session Action */
    .btn-session-end {{
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.45);
        border-radius: 8px;
        padding: 5px 8px;
        color: #f87171;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
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
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.45);
    }}

    .btn-pill-toggle {{
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 8px;
        padding: 5px 8px;
        color: #cbd5e1;
        font-size: 0.68rem;
        font-weight: 700;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        white-space: nowrap;
        transition: all 0.2s ease;
    }}

    .btn-pill-toggle:hover {{
        color: #f1f5f9;
        border-color: #00f0ff;
        background: rgba(0, 240, 255, 0.12);
    }}

    .btn-pill-toggle.active {{
        background: rgba(0, 240, 255, 0.18);
        border-color: #00f0ff;
        color: #00f0ff;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.25);
    }}
</style>
</head>
<body>

<div class="jarvis-hud-card">
    <!-- Circular Avatar with Orbiting Ring -->
    <div class="avatar-pod" onclick="togglePersistentVoiceSession()" title="Click to Speak or Pause AURA Chatbot Voice">
        <div class="arc-spin-ring" id="avatarArcRing"></div>
        <div class="avatar-circle">
            {avatar_markup}
        </div>
    </div>

    <!-- Center Info + Status + Waveform -->
    <div class="info-center">
        <div class="brand-title-line">
            <span class="brand-name">AURA • AI Guide • Travel Copilot</span>
            <span class="brand-subtitle">INTELLIGENT CHATBOT VOICE</span>
        </div>
        <div class="status-and-wave-row">
            <span class="status-badge idle" id="jarvisStatusBadge">● IDLE • READY</span>
            <div class="waveform-canvas-box">
                <canvas id="auraJarvisWaveform"></canvas>
            </div>
        </div>
    </div>

    <!-- Right Controls: Smart Session Toggle, End Session, Voice Audio Toggle -->
    <div class="controls-right">
        <!-- Smart Persistent Session Toggle: START AURA / PAUSE / RESUME -->
        <button class="btn-session-main" id="btnSessionToggle" onclick="togglePersistentVoiceSession()" title="Click to Speak to AURA Chatbot">
            🎙️ START AURA
        </button>
        <!-- End Session Button -->
        <button class="btn-session-end" id="btnEndSession" onclick="endVoiceSession()" title="End Voice Session (Offline)">
            ⏹ END
        </button>
        <!-- Voice Audio ON/OFF -->
        <button class="btn-pill-toggle active" id="btnVoiceToggle" onclick="toggleVoiceEnabled()" title="Toggle Spoken Speech Output">
            🔊 Voice
        </button>
        <!-- Replay Last Response -->
        <button class="btn-pill-toggle" id="btnReplayAudio" onclick="replayLastResponse()" title="Replay Last Answer Aloud">
            🔄 Replay
        </button>
    </div>
</div>

<script>
(function() {{
    var activeLang = {json.dumps(current_lang)};
    var bcp47Lang = {json.dumps(bcp47_code)};
    var autoGreeting = {json.dumps(auto_greeting_text)};
    var lastResponse = {json.dumps(last_response_text)};

    var voiceEnabled = {initial_voice_state};

    // -------------------------------------------------------------------------
    // Configurable Voice & Silence Detection Thresholds
    // -------------------------------------------------------------------------
    var voiceConfig = {{
        silenceThresholdMs: 1400,        // Short pause: wait for sentence to finish
        vadTimeoutMs: 1400,              // Backward-compatibility alias
        extendedSilenceMs: 6000,         // Extended silence: stop active recording, enter IDLE
        maxUtteranceDurationMs: 15000,   // Max duration per utterance
        autoStopOnSilence: true,         // Automatically stop active mic recording on silence
        autoRestartAfterResponse: true,  // Automatically return to waiting state after response
        preventEmptyTranscriptions: true // Discard empty transcriptions
    }};

    // Central State Machine:
    // 'INACTIVE', 'INITIALIZING', 'GREETING', 'IDLE', 'LISTENING', 'PROCESSING', 'SPEAKING', 'PAUSED', 'STOPPED'
    var sessionState = 'IDLE';

    var isListening = false;
    var isSpeaking = false;
    var isThinking = false;
    var recognition = null;
    var synthesis = window.speechSynthesis;
    var canvas = document.getElementById('auraJarvisWaveform');
    var ctx = canvas ? canvas.getContext('2d') : null;

    var silenceTimer = null;
    var extendedSilenceTimer = null;
    var currentSpeechBuffer = '';
    var restartDebounceTimer = null;
    var cachedLastSpokenResponse = lastResponse || '';

    // Safe Cross-Origin Parent References
    var pWin = null;
    var pDoc = null;
    try {{
        pWin = window.parent || window.top;
        if (pWin) pDoc = pWin.document;
    }} catch(eSec) {{
        pWin = null;
        pDoc = null;
    }}

    function resizeCanvas() {{
        if (!canvas) return;
        canvas.width = canvas.parentElement.clientWidth || 240;
        canvas.height = canvas.parentElement.clientHeight || 20;
    }}
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    // Toggle Voice Output (TTS)
    window.toggleVoiceEnabled = function() {{
        voiceEnabled = !voiceEnabled;
        var btn = document.getElementById('btnVoiceToggle');
        if (btn) {{
            if (voiceEnabled) {{
                btn.className = 'btn-pill-toggle active';
                btn.innerHTML = '🔊 Voice';
            }} else {{
                btn.className = 'btn-pill-toggle';
                btn.innerHTML = '🔇 Mute';
                if (synthesis) synthesis.cancel();
            }}
        }}
    }};

    window.replayLastResponse = function() {{
        if (cachedLastSpokenResponse && cachedLastSpokenResponse.trim()) {{
            window.speakJarvis(cachedLastSpokenResponse.trim());
        }}
    }};

    // Update UI Elements matching the central State Machine
    function updateUIForState(state, message) {{
        var badge = document.getElementById('jarvisStatusBadge');
        var btnToggle = document.getElementById('btnSessionToggle');
        var btnEnd = document.getElementById('btnEndSession');
        var arcRing = document.getElementById('avatarArcRing');

        if (!badge || !btnToggle) return;

        if (state === 'GREETING') {{
            isListening = false;
            isSpeaking = true;
            isThinking = false;
            badge.className = 'status-badge speaking';
            badge.innerText = '🔊 GREETING...';
            btnToggle.className = 'btn-session-main pause';
            btnToggle.innerHTML = '⏸ PAUSE';
            if (btnEnd) btnEnd.style.display = 'inline-flex';
            if (arcRing) arcRing.style.borderColor = '#38bdf8';
        }} else if (state === 'LISTENING') {{
            isListening = true;
            isSpeaking = false;
            isThinking = false;
            badge.className = 'status-badge listening';
            badge.innerText = '🎙️ LISTENING...';
            btnToggle.className = 'btn-session-main pause';
            btnToggle.innerHTML = '⏸ PAUSE';
            if (btnEnd) btnEnd.style.display = 'inline-flex';
            if (arcRing) arcRing.style.borderColor = '#00f0ff';
        }} else if (state === 'PROCESSING') {{
            isListening = false;
            isSpeaking = false;
            isThinking = true;
            badge.className = 'status-badge thinking';
            badge.innerText = '⚡ THINKING...';
            btnToggle.className = 'btn-session-main pause';
            btnToggle.innerHTML = '⏸ PAUSE';
            if (btnEnd) btnEnd.style.display = 'inline-flex';
            if (arcRing) arcRing.style.borderColor = '#a855f7';
        }} else if (state === 'SPEAKING') {{
            isListening = false;
            isSpeaking = true;
            isThinking = false;
            badge.className = 'status-badge speaking';
            badge.innerText = '🔊 SPEAKING...';
            btnToggle.className = 'btn-session-main pause';
            btnToggle.innerHTML = '⏸ PAUSE';
            if (btnEnd) btnEnd.style.display = 'inline-flex';
            if (arcRing) arcRing.style.borderColor = '#38bdf8';
        }} else if (state === 'PAUSED') {{
            isListening = false;
            isSpeaking = false;
            isThinking = false;
            badge.className = 'status-badge paused';
            badge.innerText = '⏸️ PAUSED';
            btnToggle.className = 'btn-session-main resume';
            btnToggle.innerHTML = '▶ RESUME';
            if (btnEnd) btnEnd.style.display = 'inline-flex';
            if (arcRing) arcRing.style.borderColor = '#f59e0b';
        }} else if (state === 'IDLE') {{
            isListening = false;
            isSpeaking = false;
            isThinking = false;
            badge.className = 'status-badge idle';
            badge.innerText = '● IDLE • READY';
            btnToggle.className = 'btn-session-main start';
            btnToggle.innerHTML = '🎙️ SPEAK';
            if (btnEnd) btnEnd.style.display = 'inline-flex';
            if (arcRing) arcRing.style.borderColor = '#38bdf8';
        }} else {{
            // STOPPED or INACTIVE
            isListening = false;
            isSpeaking = false;
            isThinking = false;
            badge.className = 'status-badge offline';
            badge.innerText = '● AURA OFFLINE';
            btnToggle.className = 'btn-session-main start';
            btnToggle.innerHTML = '🎙️ SPEAK';
            if (btnEnd) btnEnd.style.display = 'none';
            if (arcRing) arcRing.style.borderColor = '#475569';
        }}
    }}

    function setSessionState(newState, message) {{
        sessionState = newState;
        try {{ sessionStorage.setItem('aura_persistent_voice_state', newState); }} catch(e) {{}}
        updateUIForState(newState, message);
    }}

    // Real-Time Waveform Animation
    var wavePhase = 0;
    function drawWave() {{
        if (!ctx || !canvas) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        var numPoints = 48;
        var step = canvas.width / numPoints;
        var midY = canvas.height / 2;

        var baseAmp = isSpeaking ? 8.5 : (isListening ? 6 : (isThinking ? 4.5 : 1.5));
        var freq = isSpeaking ? 0.24 : (isListening ? 0.28 : (isThinking ? 0.38 : 0.08));

        ctx.beginPath();
        ctx.strokeStyle = isSpeaking ? '#00f0ff' : (isListening ? '#38bdf8' : (isThinking ? '#c084fc' : (sessionState === 'IDLE' ? 'rgba(56, 189, 248, 0.55)' : 'rgba(100, 116, 139, 0.3)')));
        ctx.lineWidth = isSpeaking || isListening ? 2 : 1.2;
        ctx.shadowBlur = isSpeaking ? 10 : (isListening ? 6 : 0);
        ctx.shadowColor = '#00f0ff';

        for (var i = 0; i <= numPoints; i++) {{
            var x = i * step;
            var envelope = Math.sin((i / numPoints) * Math.PI);
            var y = midY + Math.sin(i * freq + wavePhase) * (baseAmp * envelope);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }}
        ctx.stroke();

        wavePhase += isSpeaking ? 0.24 : (isListening ? 0.18 : (isThinking ? 0.30 : 0.04));
        requestAnimationFrame(drawWave);
    }}
    drawWave();

    // Multilingual Natural Voice Selection for All 8 NextRoute Languages
    function getNaturalVoice(bcp47Code, langCode) {{
        if (!synthesis) return null;
        var voices = synthesis.getVoices();
        if (!voices || voices.length === 0) return null;
        var bcp47Lower = (bcp47Code || '').toLowerCase();
        var prefix = (langCode || bcp47Lower.split('-')[0]).toLowerCase();

        var preferredKeywords = {{
            te: ["mohan", "shruti", "తెలుగు", "telugu"],
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

        // Priority 2: Match any voice matching the exact BCP-47 tag (e.g., te-IN, hi-IN)
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

        // English fallback
        if (prefix === 'en') {{
            return voices[0] || null;
        }}

        // For non-English languages, do NOT fallback to an unrelated English voice
        return null;
    }}

    // Voice Synthesis with Automatic Return to Waiting State
    window.speakJarvis = function(text) {{
        if (!text || !voiceEnabled) {{
            setSessionState('IDLE');
            return;
        }}
        if (!synthesis) return;

        try {{
            synthesis.cancel();
            cachedLastSpokenResponse = text;

            var selVoice = getNaturalVoice(bcp47Lang, activeLang);
            if (!selVoice && activeLang !== 'en') {{
                console.warn("[AURA Chatbot] Speech synthesis voice for " + activeLang + " is not installed on this browser. Displaying text response.");
                setSessionState('IDLE');
                return;
            }}

            var utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = bcp47Lang;
            utterance.rate = 1.02;
            utterance.pitch = 1.0;
            if (selVoice) utterance.voice = selVoice;

            var speechWatchdog = null;

            utterance.onstart = function() {{
                try {{ localStorage.setItem('aura_active_speaker', 'chatbot'); }} catch(e) {{}}
                setSessionState('SPEAKING', '🔊 SPEAKING...');
                if (speechWatchdog) clearTimeout(speechWatchdog);
            }};

            utterance.onend = function() {{
                try {{ localStorage.setItem('aura_active_speaker', 'none'); }} catch(e) {{}}
                if (speechWatchdog) clearTimeout(speechWatchdog);
                // Return to IDLE / WAITING state when finished speaking
                setSessionState('IDLE');
            }};

            utterance.onerror = function(err) {{
                try {{ localStorage.setItem('aura_active_speaker', 'none'); }} catch(e) {{}}
                if (speechWatchdog) clearTimeout(speechWatchdog);
                setSessionState('IDLE');
            }};

            // Watchdog fallback
            speechWatchdog = setTimeout(function() {{
                try {{ localStorage.setItem('aura_active_speaker', 'none'); }} catch(e) {{}}
                setSessionState('IDLE');
            }}, Math.max(3500, text.length * 90));

            synthesis.speak(utterance);
        }} catch(e) {{
            setSessionState('IDLE');
        }}
    }};
    // Stop ongoing speech immediately
    window.stopJarvisSpeech = function() {{
        try {{ localStorage.setItem('aura_active_speaker', 'none'); }} catch(e) {{}}
        if (synthesis) synthesis.cancel();
        isSpeaking = false;
        setSessionState('IDLE');
    }};

    // -------------------------------------------------------------------------
    // Extended Silence Handler: stops active mic recording and enters IDLE
    // -------------------------------------------------------------------------
    function resetExtendedSilenceTimer() {{
        if (extendedSilenceTimer) clearTimeout(extendedSilenceTimer);
        if (!voiceConfig.autoStopOnSilence) return;
        extendedSilenceTimer = setTimeout(function() {{
            if (sessionState === 'LISTENING') {{
                console.log("[AURA Chatbot] Extended silence timeout reached (6s). Entering IDLE.");
                if (recognition) {{
                    try {{ recognition.stop(); }} catch(e) {{}}
                }}
                currentSpeechBuffer = '';
                setSessionState('IDLE');
            }}
        }}, voiceConfig.extendedSilenceMs);
    }}

    // Continuous Speech Recognition Engine with VAD, Silence Detection, and Interruption
    function startListening() {{
        if (sessionState === 'PAUSED' || sessionState === 'STOPPED') return;

        var SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRec) {{
            alert('Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.');
            setSessionState('INACTIVE');
            return;
        }}

        // Clean up previous recognition instance
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
                setSessionState('LISTENING');
                resetExtendedSilenceTimer();
            }};

            recognition.onspeechstart = function() {{
                if (extendedSilenceTimer) clearTimeout(extendedSilenceTimer);

                // INTELLIGENT INTERRUPTION: user started speaking while chatbot is talking
                if (isSpeaking) {{
                    console.log("[AURA Chatbot] User speech detected during TTS: interrupting immediately!");
                    window.stopJarvisSpeech();
                    setSessionState('LISTENING');
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

                // INTELLIGENT INTERRUPTION CHECK: cancel ongoing audio immediately
                if (isSpeaking && rawText.length > 0) {{
                    console.log("[AURA Chatbot] Voice interruption triggered:", rawText);
                    window.stopJarvisSpeech();
                    setSessionState('LISTENING');

                    if (/^(wait|stop talking|hold on|listen to me|cancel that|be quiet|silence|pause)$/i.test(lowerText)) {{
                        currentSpeechBuffer = '';
                        resetExtendedSilenceTimer();
                        return;
                    }}
                }}

                if (sessionState !== 'LISTENING' && sessionState !== 'IDLE') return;
                try {{
                    if (localStorage.getItem('aura_active_speaker') === 'dashboard') {{
                        // Main dashboard assistant is actively speaking; ignore input to prevent cross-assistant audio interference
                        return;
                    }}
                }} catch(eAudioLock) {{}}

                if (rawText.length > 0) {{
                    currentSpeechBuffer = rawText;
                    if (silenceTimer) clearTimeout(silenceTimer);

                    // If final phrase received, submit to chatbot agent
                    if (finalTranscript.trim().length > 0) {{
                        var finalCmd = finalTranscript.trim();
                        currentSpeechBuffer = '';

                        if (/^(pause(\s+the)?(\s+voice)?(\s+assistant)?|pause\s+listening|hold\s+on)$/i.test(finalCmd.toLowerCase())) {{
                            pauseVoiceSession();
                            return;
                        }}
                        if (/^(stop(\s+the)?(\s+voice)?(\s+assistant)?|end\s+session|aura\s+offline|close\s+assistant)$/i.test(finalCmd.toLowerCase())) {{
                            endVoiceSession();
                            return;
                        }}

                        setSessionState('PROCESSING');
                        try {{ recognition.stop(); }} catch(e) {{}}
                        window.submitVoiceToExistingAgent(finalCmd);
                    }} else {{
                        // VAD short pause silence detection (1.4s)
                        silenceTimer = setTimeout(function() {{
                            if (currentSpeechBuffer.length > 0 && (sessionState === 'LISTENING' || sessionState === 'IDLE')) {{
                                var pendingText = currentSpeechBuffer.trim();
                                currentSpeechBuffer = '';
                                if (pendingText.length >= 2) {{
                                    setSessionState('PROCESSING');
                                    try {{ recognition.stop(); }} catch(e) {{}}
                                    window.submitVoiceToExistingAgent(pendingText);
                                }}
                            }}
                        }}, voiceConfig.silenceThresholdMs);
                    }}
                }}
            }};

            recognition.onerror = function(err) {{
                if (err && err.error === 'not-allowed') {{
                    alert('Microphone access was denied. Please allow microphone permissions in address bar.');
                    pauseVoiceSession();
                    return;
                }}
                if (err && err.error === 'no-speech') {{
                    setSessionState('IDLE');
                    return;
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
        }} catch(e) {{
            console.warn("[AURA Chatbot] Could not start speech recognition:", e);
            setSessionState('IDLE');
        }}
    }}

    // -------------------------------------------------------------------------
    // PERSISTENT SESSION CONTROLS: START, PAUSE, RESUME, END
    // -------------------------------------------------------------------------
    window.startVoiceSession = function() {{
        setSessionState('LISTENING');
        startListening();
    }};

    window.pauseVoiceSession = function() {{
        setSessionState('PAUSED');
        window.stopJarvisSpeech();
        if (recognition) {{
            try {{ recognition.abort(); }} catch(e) {{}}
        }}
        if (silenceTimer) clearTimeout(silenceTimer);
        if (extendedSilenceTimer) clearTimeout(extendedSilenceTimer);
        currentSpeechBuffer = '';
    }};

    window.resumeVoiceSession = function() {{
        setSessionState('LISTENING');
        startListening();
    }};

    window.endVoiceSession = function() {{
        setSessionState('STOPPED');
        window.stopJarvisSpeech();
        if (recognition) {{
            try {{ recognition.abort(); }} catch(e) {{}}
            recognition = null;
        }}
        if (silenceTimer) clearTimeout(silenceTimer);
        if (extendedSilenceTimer) clearTimeout(extendedSilenceTimer);
        currentSpeechBuffer = '';
    }};

    window.togglePersistentVoiceSession = function() {{
        if (sessionState === 'INACTIVE' || sessionState === 'STOPPED' || sessionState === 'IDLE') {{
            startVoiceSession();
        }} else if (sessionState === 'LISTENING' || sessionState === 'PROCESSING' || sessionState === 'SPEAKING') {{
            pauseVoiceSession();
        }} else if (sessionState === 'PAUSED') {{
            resumeVoiceSession();
        }}
    }};

    // Backward-compatibility alias
    window.toggleJarvisVoiceRecognition = window.togglePersistentVoiceSession;

    // Zero-Reload WebSocket Bridge to NextRoute Chatbot Agent
    window.submitVoiceToExistingAgent = function(transcript) {{
        var cleanTranscript = (transcript || '').trim();
        if (!cleanTranscript) return;

        // 1. Direct WebSocket transmission through Streamlit hidden React input
        try {{
            if (pDoc && pWin) {{
                var chatBridgeInput = pDoc.querySelector('input[aria-label="AURA_CHAT_PROMPT_BRIDGE"]') ||
                                     pDoc.querySelector('input[data-testid*="aura_chat_prompt_sink"]');

                if (chatBridgeInput) {{
                    var cmdId = 'chat_' + Date.now();
                    var payload = JSON.stringify({{ id: cmdId, prompt: cleanTranscript }});
                    var nativeSetter = Object.getOwnPropertyDescriptor(pWin.HTMLInputElement.prototype, 'value')?.set ||
                                       Object.getOwnPropertyDescriptor(chatBridgeInput.__proto__, 'value')?.set;
                    if (nativeSetter) {{
                        nativeSetter.call(chatBridgeInput, payload);
                    }} else {{
                        chatBridgeInput.value = payload;
                    }}
                    chatBridgeInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    chatBridgeInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    chatBridgeInput.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }}));
                    return true;
                }}
            }}
        }} catch(eBridge) {{
            console.warn("[AURA Bridge] Zero-reload bridge notice:", eBridge);
        }}

        // 2. Fallback via URL searchParams navigation
        try {{
            var targetWin = pWin || window.top || window;
            var currentHref = '';
            try {{ currentHref = targetWin.location.href; }} catch(e) {{ currentHref = window.location.href; }}
            var url = new URL(currentHref);
            url.searchParams.set('pending_chat_prompt', cleanTranscript);
            try {{
                targetWin.location.href = url.toString();
            }} catch(eNav) {{
                window.location.href = url.toString();
            }}
        }} catch(eParam) {{}}
    }};

    // Unlock audio autoplay on first interaction
    var unlockAudioOnGesture = function() {{
        try {{
            if (synthesis && synthesis.paused) {{
                synthesis.resume();
            }}
        }} catch(e) {{}}
        window.removeEventListener('click', unlockAudioOnGesture);
        window.removeEventListener('keydown', unlockAudioOnGesture);
        window.removeEventListener('touchstart', unlockAudioOnGesture);
    }};
    window.addEventListener('click', unlockAudioOnGesture, {{ passive: true }});
    window.addEventListener('keydown', unlockAudioOnGesture, {{ passive: true }});
    window.addEventListener('touchstart', unlockAudioOnGesture, {{ passive: true }});

    // Initialize UI on load
    updateUIForState(sessionState);

    // Initial load: Play latest response or startup greeting automatically
    setTimeout(function() {{
        if (lastResponse && lastResponse.trim()) {{
            window.speakJarvis(lastResponse.trim());
        }} else if (autoGreeting && autoGreeting.trim()) {{
            setSessionState('GREETING');
            window.speakJarvis(autoGreeting.trim());
        }}
    }}, 400);

}})();
</script>
</body>
</html>
"""
