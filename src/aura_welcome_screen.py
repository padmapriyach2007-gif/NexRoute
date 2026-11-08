"""
NexRoute — AURA JARVIS-Style AI Voice Assistant & Autonomous Controller
Fully integrated, automatic Jarvis-style AI voice copilot that greets on application launch,
continuously listens for natural voice commands, and navigates internal NextRoute sections
within the single main application without launching duplicate instances.
"""

import json
import datetime
from typing import Optional, Dict, Any


def get_aura_startup_greeting(lang: str = "en", user_name: str = "Boss") -> str:
    """
    Returns the exact time-appropriate JARVIS greeting.
    - Good morning (5:00 - 11:59)
    - Good afternoon (12:00 - 16:59)
    - Good evening (17:00 - 4:59)
    No extra promotional or introductory sentences.
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
        tod_ml = "ശുഭ സായാഹ്നം"

    if lang == "te":
        return f"{tod_te}, {user_name}! నెక్స్‌రూట్‌కి స్వాగతం. నేను మీకు ఎలా సహాయపడగలను?"
    elif lang == "hi":
        return f"{tod_hi}, {user_name}! नेक्स्ट-रूट में आपका स्वागत है। मैं आपकी क्या मदद कर सकता हूँ?"
    elif lang == "ta":
        return f"{tod_ta}, {user_name}! நெக்ஸ்-ரூட்டிற்கு நல்வரவு. நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?"
    elif lang == "kn":
        return f"{tod_kn}, {user_name}! ನೆಕ್ಸ್-ರೂಟ್‌ಗೆ ಸುಸ್ವಾಗತ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?"
    elif lang == "ml":
        return f"{tod_ml}, {user_name}! നെക്സ്-റൂട്ടിലേക്ക് സ്വാഗതം. ഞാൻ എന്ത് സഹായമാണ് ചെയ്യേണ്ടത്?"
    else:
        return f"{tod_en}, {user_name}! Welcome to NextRoute. How can I help you?"


def render_aura_welcome_hud(
    current_lang: str = "en",
    auto_speak: bool = True,
    bot_logo_uri: Optional[str] = None,
    user_name: str = "Boss"
) -> str:
    """
    Renders the streamlined futuristic JARVIS-style voice assistant HUD for NextRoute.
    Features the circular robot avatar, live waveform canvas, status pill, transcript box,
    automatic startup greeting, continuous speech recognition, and instant section navigation.
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
        else '<span style="color: #00f0ff; font-size: 26px; font-weight: 900;">⚡</span>'
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
        padding: 6px;
        overflow: hidden;
    }}

    /* Futuristic HUD Glassmorphism Card (Streamlined & Clean) */
    .aura-welcome-panel {{
        position: relative;
        width: 100%;
        max-width: 840px;
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

    /* Header Bar: Brand + Live Status Badge */
    .welcome-top-row {{
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
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

    /* Arc Reactor Circular Assistant Avatar */
    .avatar-wrapper {{
        position: relative;
        width: 68px;
        height: 68px;
        margin: 2px 0 8px 0;
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
        width: 56px;
        height: 56px;
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

    /* Spoken Greeting Headline */
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

    /* Synchronized Audio Waveform Visualizer */
    .waveform-container {{
        width: 100%;
        max-width: 520px;
        height: 26px;
        margin: 4px 0 6px 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    #auraWaveCanvas {{
        width: 100%;
        height: 100%;
        display: block;
    }}

    /* Minimal Voice Transcript Display */
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
    <!-- Top Row: Brand & Live Status Indicator -->
    <div class="welcome-top-row">
        <div class="brand-pill">
            <span class="brand-pulse-dot"></span>
            AURA • JARVIS AI COPILOT
        </div>
        <div class="status-badge" id="statusBadge">
            ● IDLE • READY
        </div>
    </div>

    <!-- Animated Arc Reactor Avatar (Click to Toggle Mic) -->
    <div class="avatar-wrapper" onclick="toggleVoiceListening()" title="Click to speak with AURA">
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

    <!-- Synchronized Audio Waveform Visualizer -->
    <div class="waveform-container">
        <canvas id="auraWaveCanvas"></canvas>
    </div>

    <!-- Minimal Voice Transcript Display -->
    <div class="live-transcript-box" id="transcriptBox">
        Ready for voice command, Boss.
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
    var isProcessing = false;
    var recognition = null;
    var synthesis = window.speechSynthesis;
    var currentUtterance = null;
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
                badge.innerText = '⚡ EXECUTING COMMAND...';
                badge.style.background = 'rgba(168, 85, 247, 0.22)';
                badge.style.borderColor = '#a855f7';
                badge.style.color = '#c084fc';
            }}
            if (midRing) midRing.style.boxShadow = '0 0 28px #a855f7';
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

    // Waveform Animation Loop
    function resizeCanvas() {{
        if (!canvas) return;
        canvas.width = canvas.parentElement.clientWidth || 400;
        canvas.height = canvas.parentElement.clientHeight || 26;
    }}
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    var wavePhase = 0;
    function drawWave() {{
        if (!ctx || !canvas) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        var numPoints = 50;
        var step = canvas.width / numPoints;
        var midY = canvas.height / 2;

        var baseAmp = isSpeaking ? 11 : (isListening ? 8 : 2.5);
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

    // Universal Speech Synthesis Function
    function speakText(textToSpeak, onCompleteCallback) {{
        if (!synthesis) {{
            if (onCompleteCallback) onCompleteCallback();
            return;
        }}
        try {{
            synthesis.cancel();
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
                if (onCompleteCallback) onCompleteCallback();
            }};

            currentUtterance.onerror = function() {{
                isSpeaking = false;
                if (onCompleteCallback) onCompleteCallback();
            }};

            synthesis.speak(currentUtterance);
        }} catch(e) {{
            isSpeaking = false;
            if (onCompleteCallback) onCompleteCallback();
        }}
    }}

    // Continuous Speech Recognition (Speech-to-Text)
    function startVoiceListening() {{
        if (isSpeaking || isProcessing) return;

        var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {{
            setAssistantState('idle', 'Ready for voice commands.');
            return;
        }}

        if (recognition) {{
            try {{ recognition.abort(); }} catch(e) {{}}
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
                if (transcript && transcript.trim()) {{
                    handleVoiceCommand(transcript.trim());
                }}
            }};

            recognition.onerror = function(err) {{
                isListening = false;
                setAssistantState('idle', 'Ready for voice commands.');
            }};

            recognition.onend = function() {{
                isListening = false;
                if (!isSpeaking && !isProcessing) {{
                    setAssistantState('idle', 'Ready for voice commands.');
                }}
            }};

            recognition.start();
        }} catch(e) {{
            isListening = false;
            setAssistantState('idle', 'Ready for voice commands.');
        }}
    }}

    window.toggleVoiceListening = function() {{
        if (isListening && recognition) {{
            try {{ recognition.stop(); }} catch(e) {{}}
            isListening = false;
            setAssistantState('idle', 'Listening paused.');
        }} else {{
            startVoiceListening();
        }}
    }};

    // Process Voice Command & Navigate Within Single NextRoute Application
    function handleVoiceCommand(cmdText) {{
        isProcessing = true;
        setAssistantState('processing', 'YOU: "' + cmdText + '"');

        var lower = cmdText.toLowerCase();
        var spokenResponse = "";

        if (lower.indexOf("navigation") !== -1 || lower.indexOf("nav") !== -1 || lower.indexOf("map") !== -1) {{
            spokenResponse = "Opening navigation.";
        }} else if (lower.indexOf("trip") !== -1 || lower.indexOf("copilot") !== -1 || lower.indexOf("itinerar") !== -1) {{
            spokenResponse = "Here are your trips.";
        }} else if (lower.indexOf("hotel") !== -1 || lower.indexOf("lodg") !== -1) {{
            spokenResponse = "Let's find hotels.";
        }} else if (lower.indexOf("flight") !== -1 || lower.indexOf("airplane") !== -1) {{
            spokenResponse = "Opening flight planner.";
        }} else if (lower.indexOf("restaurant") !== -1 || lower.indexOf("food") !== -1 || lower.indexOf("cafe") !== -1) {{
            spokenResponse = "Finding nearby restaurants.";
        }} else if (lower.indexOf("profile") !== -1 || lower.indexOf("account") !== -1) {{
            spokenResponse = "Opening your profile.";
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
            spokenResponse = "Processing: " + cmdText.substring(0, 30);
        }}

        // Speak the concise response immediately
        speakText(spokenResponse, function() {{
            isProcessing = false;
            // Continuous Voice Command Interaction: automatically resume listening
            setTimeout(function() {{
                startVoiceListening();
            }}, 600);
        }});

        // Dispatch command to parent NextRoute Streamlit application
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
    }}

    // Automatic Voice Greeting on Application Launch & Autoplay Fallback
    var greetingSpoken = false;

    function attemptStartupGreeting() {{
        if (greetingSpoken) return;
        var sessionGreetedKey = 'aura_session_greeted_' + activeLang;
        try {{
            if (sessionStorage.getItem(sessionGreetedKey) === 'true') {{
                greetingSpoken = true;
                setAssistantState('idle', 'Ready for voice commands.');
                return;
            }}
        }} catch(e) {{}}

        if (!autoSpeak) {{
            setAssistantState('idle', 'Ready for voice commands.');
            return;
        }}

        greetingSpoken = true;
        try {{ sessionStorage.setItem(sessionGreetedKey, 'true'); }} catch(e) {{}}

        // Speak initial greeting: "Good morning, Boss! Welcome to NextRoute. How can I help you?"
        speakText(spokenGreeting, function() {{
            // Immediately after greeting finishes, activate microphone for continuous commands!
            setTimeout(function() {{
                startVoiceListening();
            }}, 400);
        }});
    }}

    // Minimal First-Interaction Fallback (if browser blocks audible autoplay without user gesture)
    function onFirstUserInteraction() {{
        if (!greetingSpoken && autoSpeak) {{
            attemptStartupGreeting();
        }}
        window.removeEventListener('click', onFirstUserInteraction);
        window.removeEventListener('keydown', onFirstUserInteraction);
        window.removeEventListener('touchstart', onFirstUserInteraction);
        try {{
            var pWin = window.parent || window.top;
            if (pWin && pWin !== window) {{
                pWin.removeEventListener('click', onFirstUserInteraction);
                pWin.removeEventListener('keydown', onFirstUserInteraction);
                pWin.removeEventListener('touchstart', onFirstUserInteraction);
            }}
        }} catch(e) {{}}
    }}

    window.addEventListener('click', onFirstUserInteraction);
    window.addEventListener('keydown', onFirstUserInteraction);
    window.addEventListener('touchstart', onFirstUserInteraction);
    try {{
        var pWin = window.parent || window.top;
        if (pWin && pWin !== window) {{
            pWin.addEventListener('click', onFirstUserInteraction);
            pWin.addEventListener('keydown', onFirstUserInteraction);
            pWin.addEventListener('touchstart', onFirstUserInteraction);
        }}
    }} catch(e) {{}}

    // Automatic trigger on launch
    setTimeout(function() {{
        attemptStartupGreeting();
    }}, 400);

}})();
</script>
</body>
</html>
"""
