"""
Accessible Voice Guidance Engine for P.A.T.H.F.I.N.D.E.R.
Specifically engineered for blind persons, visually impaired travelers,
and individuals with limited education or literacy.

Features:
1. Ultra-Simple Spoken Natural Language (zero technical jargon, zero complex math terms)
2. Landmark-oriented, reassuring turn-by-turn spoken guidance
3. Proactive, clear warnings about road blockages or hazards in plain terms
4. Built-in Web Speech API audio player with Play, Pause, Stop, Replay, and Slow/Clear speech pacing
5. High-contrast, large-font live spoken captions for low-vision travelers
"""

from typing import Dict, Any, List, Optional
from src.i18n import get_current_language, get_bcp47_code, t, format_distance, format_duration


def generate_simple_spoken_narrative(
    origin_name: str,
    destination_name: str,
    route_name: str = "Recommended Open Road",
    distance_km: float = 0.0,
    duration_min: float = 0.0,
    summary_roads: Optional[List[str]] = None,
    active_restrictions: Optional[List[Any]] = None,
    active_hazards: Optional[List[Any]] = None,
    travel_mode: str = "Driving",
    unit: str = "km",
    lang: Optional[str] = None
) -> str:
    """
    Produces ultra-clear, simple, reassuring spoken text designed for
    effortless comprehension by blind persons and non-technical travelers worldwide.
    Supports configurable distance units ('km' or 'miles') and international road names.
    """
    clean_origin = (
        origin_name
        .replace("My Current Location", "your current location")
        .replace("📍", "")
        .replace("(", "")
        .replace(")", "")
        .strip()
    )
    clean_dest = (
        destination_name
        .replace("Map Pin", "your destination")
        .replace("🏁", "")
        .replace("(", "")
        .replace(")", "")
        .strip()
    )

    # Time in natural spoken words
    approx_time = max(1, round(duration_min))
    if approx_time >= 60:
        hrs = approx_time // 60
        mins = approx_time % 60
        time_phrase = f"{hrs} hour{'s' if hrs > 1 else ''} and {mins} minutes" if mins > 0 else f"{hrs} hour{'s' if hrs > 1 else ''}"
    else:
        time_phrase = f"{approx_time} minutes" if approx_time > 1 else "1 minute"

    # Configurable Distance in natural spoken words (Kilometres or Miles)
    if unit.lower() in ("miles", "mi", "mile"):
        dist_val = round(distance_km * 0.621371, 1)
        dist_phrase = f"{dist_val} miles"
    else:
        dist_val = round(distance_km, 1)
        dist_phrase = f"{dist_val} kilometers"

    # International road name phonetic substitutions for clear speech synthesis
    via_phrase = ""
    if summary_roads and len(summary_roads) > 0:
        clean_roads = []
        for r in summary_roads[:3]:
            spoken_r = (
                r.replace("SH-", "State Highway ")
                .replace("NH-", "National Highway ")
                .replace("US-", "U.S. Route ")
                .replace("I-", "Interstate ")
                .replace("M1", "M One Motorway")
                .replace("M25", "M Twenty-Five Motorway")
                .replace("M4", "M Four Motorway")
                .replace("A1", "A One Road")
                .replace("Rd", "Road")
                .replace("Ave", "Avenue")
                .replace("St", "Street")
                .replace("Blvd", "Boulevard")
                .replace("Pkwy", "Parkway")
                .replace("Expwy", "Expressway")
            )
            clean_roads.append(spoken_r)
        via_phrase = f"by taking {' and then '.join(clean_roads)}"
    else:
        via_phrase = "along the main connecting roadway"

    # Dynamic Hazard & Restriction Explanation in plain, reassuring terms
    hazard_speech = ""
    alert_details = []
    if active_restrictions:
        for r in active_restrictions:
            r_road = getattr(r, "road_name", "the highway")
            r_desc = getattr(r, "description", "road maintenance")
            alert_details.append(f"{r_desc} on {r_road}")

    if active_hazards:
        for h in active_hazards:
            h_type = h.get("incident_type") if isinstance(h, dict) else getattr(h, "incident_type", "hazard")
            h_desc = h.get("description") if isinstance(h, dict) else getattr(h, "description", "incident")
            alert_details.append(f"{h_type.lower()}: {h_desc}")

    if alert_details:
        joined_alerts = "; ".join(alert_details[:2])
        hazard_speech = (
            f"Safety notice: A travel restriction has been detected: {joined_alerts}. "
            "Do not worry. Our navigation system has already selected an open, safe alternative path around it."
        )
    else:
        hazard_speech = "Good news: All roads on your route are currently reported open and clear."

    curr_lang = lang or get_current_language()

    # Multilingual Spoken Narrative Templates
    if curr_lang == "te":
        narrative = (
            f"నమస్కారం. ఇది మీ ఆడియో నావిగేషన్ గైడ్. మీరు స్క్రీన్ చూడవలసిన అవసరం లేకుండా సురక్షితంగా ప్రయాణించవచ్చు. "
            f"మీరు {clean_origin} నుండి బయలుదేరుతున్నారు. మీ గమ్యస్థానం {clean_dest}. "
            f"మీ ప్రయాణ విధానం {travel_mode}. ఉత్తమ మరియు సురక్షితమైన మార్గం సిద్ధంగా ఉంది. "
            f"మొత్తం దూరం సుమారు {dist_phrase}, అంచనా సమయం {time_phrase}. "
            f"{hazard_speech} "
            f"మొదటి దశ: {clean_origin} నుండి ప్రధాన రహదారిపైకి బయలుదేరండి. "
            f"రెండవ దశ: {via_phrase} వెంట ముందుకు సాగండి. "
            f"మూడవ దశ: {clean_dest} వైపు ప్రయాణించండి, మీ గమ్యస్థానం ఎదురుగా ఉంటుంది. "
            f"మీ ప్రయాణం సురక్షితంగా మరియు సుఖవంతంగా సాగాలని కోరుకుంటున్నాము!"
        )
    elif curr_lang == "hi":
        narrative = (
            f"नमस्ते। यह आपका ऑडियो नेविगेशन गाइड है। "
            f"आप {clean_origin} से प्रस्थान कर रहे हैं। आपका गंतव्य {clean_dest} है। "
            f"आपका यात्रा साधन {travel_mode} है। सर्वोत्तम और सुरक्षित मार्ग तैयार है। "
            f"कुल दूरी लगभग {dist_phrase} है, और अनुमानित यात्रा समय {time_phrase} है। "
            f"{hazard_speech} "
            f"पहला चरण: {clean_origin} से मुख्य सड़क की ओर बढ़ें। "
            f"दूसरा चरण: {via_phrase} के साथ आगे बढ़ें। "
            f"तीसरा चरण: {clean_dest} की ओर बढ़ते रहें, आपका गंतव्य सीधे आगे होगा। "
            f"आपकी यात्रा मंगलमय और सुरक्षित हो!"
        )
    elif curr_lang == "ta":
        narrative = (
            f"வணக்கம். இது உங்கள் ஆடியோ வழிசெலுத்தல் வழிகாட்டி. "
            f"நீங்கள் {clean_origin} இலிருந்து தொடங்குகிறீர்கள். உங்கள் இலக்கு {clean_dest}. "
            f"பயண முறை {travel_mode}. சிறந்த மற்றும் பாதுகாப்பான வழி தயாராக உள்ளது. "
            f"மொத்த தூரம் சுமார் {dist_phrase}, பயண நேரம் {time_phrase}. "
            f"{hazard_speech} இனிய மற்றும் பாதுகாப்பான பயணம் அமைய வாழ்த்துகள்!"
        )
    elif curr_lang == "kn":
        narrative = (
            f"ನಮಸ್ಕಾರ. ಇದು ನಿಮ್ಮ ಆಡಿಯೋ ನ್ಯಾವಿಗೇಷನ್ ಮಾರ್ಗದರ್ಶಿ. "
            f"ನೀವು {clean_origin} ನಿಂದ ಪ್ರಾರಂಭಿಸುತ್ತಿದ್ದೀರಿ. ನಿಮ್ಮ ಗಮ್ಯಸ್ಥಾನ {clean_dest}. "
            f"ಪ್ರಯಾಣ ವಿಧಾನ {travel_mode}. ಸುರಕ್ಷಿತ ಮಾರ್ಗ ಸಿದ್ಧವಾಗಿದೆ. "
            f"ಒಟ್ಟು ದೂರ ಸುಮಾರು {dist_phrase}, ಅಂದಾಜು ಸಮಯ {time_phrase}. "
            f"{hazard_speech} ನಿಮ್ಮ ಪ್ರಯಾಣ ಸುಖಕರವಾಗಿರಲಿ!"
        )
    elif curr_lang == "ml":
        narrative = (
            f"നമസ്കാരം. ഇത് നിങ്ങളുടെ ഓഡിയോ നാവിഗേഷൻ ഗൈഡാണ്. "
            f"നിങ്ങൾ {clean_origin} ൽ നിന്ന് ആരംഭിക്കുന്നു. നിങ്ങളുടെ ലക്ഷ്യസ്ഥാനം {clean_dest} ആണ്. "
            f"ആകെ ദൂരം ഏകദേശം {dist_phrase}, യാത്രാ സമയം {time_phrase}. "
            f"{hazard_speech} ശുഭയാത്ര നേരുന്നു!"
        )
    elif curr_lang == "bn":
        narrative = (
            f"নমস্কার। এটি আপনার অডিও নেভিগেশন গাইড। "
            f"আপনি {clean_origin} থেকে শুরু করছেন। আপনার গন্তব্য {clean_dest}। "
            f"মোট দূরত্ব প্রায় {dist_phrase}, আনুমানিক সময় {time_phrase}. "
            f"{hazard_speech} আপনার যাত্রা শুভ ও নিরাপদ হোক!"
        )
    elif curr_lang == "mr":
        narrative = (
            f"नमस्कार. हे आपले ऑडिओ नेव्हिगेशन मार्गदर्शक आहे. "
            f"आपण {clean_origin} येथून निघत आहात. आपले गंतव्य {clean_dest} आहे. "
            f"एकूण अंतर सुमारे {dist_phrase} आहे, अंदाजे वेळ {time_phrase} आहे. "
            f"{hazard_speech} आपला प्रवास सुखकर व सुरक्षित होवो!"
        )
    else:
        narrative = (
        f"Hello. This is your audio navigation guide. I will read your route aloud in simple steps so you do not need to look at the screen. "
        f"You are starting from {clean_origin}. Your destination is {clean_dest}. "
        f"Your travel mode is {travel_mode}. "
        f"The best and safest route is ready. The total distance is about {dist_phrase}, and your estimated travel time is approximately {time_phrase}. "
        f"{hazard_speech} "
        f"Here are your easy steps to follow. "
        f"Step one: Start moving from {clean_origin} onto the connecting road. "
        f"Step two: Continue {via_phrase}. Follow road markings and stay on the clear corridor. "
        f"Step three: Keep heading towards {clean_dest}. As you get closer, your arrival point will be directly ahead. "
        f"We will monitor the road for you. If traffic conditions change, we will guide you. Have a very safe and comfortable journey!"
    )

    return narrative


def build_voice_assistant_html(
    spoken_text: str,
    origin_name: str,
    destination_name: str,
    distance_km: float,
    duration_min: float,
    summary_roads: Optional[List[str]] = None,
    active_restrictions: Optional[List[Any]] = None,
    active_hazards: Optional[List[Any]] = None,
    unit: str = "km",
    lang: Optional[str] = None
) -> str:
    """
    Renders an advanced, deeply interactive Voice Navigation Assistant featuring:
    - Step-by-Step interactive audio guidance (Play, Prev, Next, Repeat step)
    - Animated live equalizer waveform visualizer during speech
    - Quick-Ask interactive query chips ("Hazards Ahead?", "Next Maneuver", "ETA & Distance", "GPS Status")
    - Hands-free microphone voice command recognition (Web Speech API)
    - Dynamic Voice Selection (system speech synthesis voices) & pace switcher
    - Screen-reader accessible and high-contrast styling
    """
    curr_lang = lang or get_current_language()
    bcp47_code = get_bcp47_code(curr_lang)
    clean_origin = origin_name.replace("My Current Location", "your current location").replace("📍", "").strip()
    clean_dest = destination_name.replace("Map Pin", "your destination").replace("🏁", "").strip()

    # Calculate distance and time strings
    approx_time = max(1, round(duration_min))
    if approx_time >= 60:
        hrs = approx_time // 60
        mins = approx_time % 60
        time_phrase = f"{hrs} hour{'s' if hrs > 1 else ''} and {mins} minutes" if mins > 0 else f"{hrs} hour{'s' if hrs > 1 else ''}"
    else:
        time_phrase = f"{approx_time} minutes" if approx_time > 1 else "1 minute"

    dist_val = round(distance_km * 0.621371, 1) if unit.lower() in ("miles", "mi", "mile") else round(distance_km, 1)
    dist_unit_str = "miles" if unit.lower() in ("miles", "mi", "mile") else "kilometers"
    dist_phrase = f"{dist_val} {dist_unit_str}"

    # Corridors
    if summary_roads and len(summary_roads) > 0:
        via_phrase = f"by following {' and then '.join(summary_roads[:3])}"
    else:
        via_phrase = "along the primary designated corridor"

    # Hazards
    alert_details = []
    if active_restrictions:
        for r in active_restrictions:
            r_road = getattr(r, "road_name", "the corridor")
            r_desc = getattr(r, "description", "road caution")
            alert_details.append(f"{r_desc} on {r_road}")
    if active_hazards:
        for h in active_hazards:
            h_type = h.get("incident_type") if isinstance(h, dict) else getattr(h, "incident_type", "hazard")
            h_desc = h.get("description") if isinstance(h, dict) else getattr(h, "description", "incident")
            alert_details.append(f"{h_type.lower()}: {h_desc}")

    if alert_details:
        hazard_speech = f"Caution: Travel restrictions detected: {'; '.join(alert_details[:2])}. An open, safe detour has been calculated."
    else:
        hazard_speech = "All designated travel corridors on your route are open and clear with no active hazards."

    step1_text = f"Step one: Depart from {clean_origin} and proceed onto the designated transit roadway."
    step2_text = f"Step two: Continue {via_phrase}. Follow road markings and stay on the clear corridor."
    step3_text = f"Step three: Safety clearance status. {hazard_speech}"
    step4_text = f"Step four: Approach {clean_dest}. Your destination will be directly ahead."

    safe_full = spoken_text.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
    safe_step1 = step1_text.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
    safe_step2 = step2_text.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
    safe_step3 = step3_text.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
    safe_step4 = step4_text.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
    safe_origin = clean_origin.replace('"', '\\"').replace("'", "\\'")
    safe_dest = clean_dest.replace('"', '\\"').replace("'", "\\'")
    safe_eta = f"Estimated arrival in {time_phrase}, covering {dist_phrase}."
    safe_hazards = hazard_speech.replace('"', '\\"').replace("'", "\\'")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        * {{
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            user-select: none;
        }}
        body {{
            margin: 0;
            padding: 4px;
            background: transparent;
            color: #f8fafc;
        }}
        .voice-card {{
            background: linear-gradient(135deg, rgba(8, 28, 52, 0.96) 0%, rgba(15, 23, 42, 0.98) 100%);
            border: 1.5px solid #38bdf8;
            border-radius: 12px;
            padding: 12px 14px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6), 0 0 20px rgba(56, 189, 248, 0.2);
        }}
        .voice-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            flex-wrap: wrap;
            gap: 6px;
        }}
        .voice-title {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 800;
            font-size: 0.98rem;
            color: #ffffff;
            letter-spacing: 0.02em;
        }}
        .equalizer-container {{
            display: inline-flex;
            align-items: flex-end;
            gap: 3px;
            height: 16px;
            margin-left: 4px;
        }}
        .eq-bar {{
            width: 3.5px;
            height: 4px;
            background: #38bdf8;
            border-radius: 2px;
            transition: height 0.15s ease;
        }}
        .speaking .eq-bar:nth-child(1) {{ animation: eqPulse 0.4s infinite alternate; }}
        .speaking .eq-bar:nth-child(2) {{ animation: eqPulse 0.6s infinite 0.1s alternate; }}
        .speaking .eq-bar:nth-child(3) {{ animation: eqPulse 0.5s infinite 0.2s alternate; }}
        .speaking .eq-bar:nth-child(4) {{ animation: eqPulse 0.7s infinite 0.15s alternate; }}
        .speaking .eq-bar:nth-child(5) {{ animation: eqPulse 0.45s infinite 0.05s alternate; }}
        @keyframes eqPulse {{
            0% {{ height: 4px; background: #38bdf8; }}
            100% {{ height: 16px; background: #10b981; box-shadow: 0 0 6px #10b981; }}
        }}
        .badge-group {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .accessible-badge {{
            background: rgba(16, 185, 129, 0.2);
            border: 1px solid #10b981;
            color: #34d399;
            font-size: 0.68rem;
            font-weight: 800;
            padding: 2px 7px;
            border-radius: 9999px;
            letter-spacing: 0.04em;
        }}
        .status-pill {{
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 6px;
            padding: 2px 8px;
            font-size: 0.70rem;
            font-family: monospace;
            font-weight: 700;
            color: #94a3b8;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }}
        .status-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #10b981;
            display: inline-block;
        }}
        .status-dot.active {{
            background: #38bdf8;
            box-shadow: 0 0 8px #38bdf8;
            animation: pulse 1s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.3); opacity: 0.6; }}
        }}
        .controls-row {{
            display: flex;
            gap: 6px;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 8px;
        }}
        .btn-action {{
            background: #0284c7;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 6px 11px;
            font-size: 0.80rem;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            transition: all 0.15s ease;
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.3);
        }}
        .btn-action:hover {{
            background: #38bdf8;
            color: #082f49;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.4);
        }}
        .btn-secondary {{
            background: rgba(30, 41, 59, 0.85);
            border: 1px solid rgba(56, 189, 248, 0.3);
            color: #e2e8f0;
        }}
        .btn-secondary:hover {{
            background: rgba(51, 65, 85, 0.95);
            color: #ffffff;
            border-color: #38bdf8;
        }}
        .btn-mic {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            border: 1px solid #34d399;
            color: #ffffff;
            font-weight: 800;
        }}
        .btn-mic:hover {{
            background: #34d399;
            color: #064e3b;
            box-shadow: 0 0 12px rgba(52, 211, 153, 0.6);
        }}
        .btn-mic.listening {{
            background: #ef4444 !important;
            border-color: #f87171 !important;
            color: #ffffff !important;
            animation: pulse 0.8s infinite;
        }}
        .steps-bar {{
            display: flex;
            gap: 6px;
            margin-bottom: 8px;
            background: rgba(15, 23, 42, 0.6);
            padding: 4px 6px;
            border-radius: 8px;
            border: 1px solid rgba(56, 189, 248, 0.2);
            overflow-x: auto;
        }}
        .step-chip {{
            flex: 1;
            min-width: 90px;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.73rem;
            font-weight: 700;
            background: rgba(30, 41, 59, 0.6);
            color: #94a3b8;
            border: 1px solid transparent;
            cursor: pointer;
            text-align: center;
            white-space: nowrap;
            transition: all 0.15s ease;
        }}
        .step-chip:hover {{
            background: rgba(51, 65, 85, 0.8);
            color: #38bdf8;
            border-color: rgba(56, 189, 248, 0.4);
        }}
        .step-chip.active {{
            background: rgba(2, 132, 199, 0.35);
            color: #38bdf8;
            border-color: #38bdf8;
            box-shadow: 0 0 8px rgba(56, 189, 248, 0.3);
        }}
        .query-bar {{
            display: flex;
            align-items: center;
            gap: 5px;
            margin-bottom: 8px;
            flex-wrap: wrap;
        }}
        .query-label {{
            font-size: 0.70rem;
            font-weight: 800;
            color: #38bdf8;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }}
        .query-btn {{
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 9999px;
            padding: 3px 9px;
            font-size: 0.72rem;
            font-weight: 600;
            color: #cbd5e1;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .query-btn:hover {{
            background: rgba(56, 189, 248, 0.2);
            border-color: #38bdf8;
            color: #ffffff;
            transform: scale(1.03);
        }}
        .caption-box {{
            background: rgba(0, 0, 0, 0.45);
            border-left: 3.5px solid #10b981;
            border-radius: 0 6px 6px 0;
            padding: 8px 10px;
            font-size: 0.82rem;
            line-height: 1.45;
            color: #f1f5f9;
            min-height: 48px;
            max-height: 72px;
            overflow-y: auto;
        }}
    </style>
    </head>
    <body>
    <div class="voice-card" role="region" aria-label="Interactive Voice Navigation Assistant">
        <div class="voice-header">
            <div class="voice-title">
                <span>🔊 AI Voice Navigator</span>
                <div id="eqWave" class="equalizer-container">
                    <div class="eq-bar"></div>
                    <div class="eq-bar"></div>
                    <div class="eq-bar"></div>
                    <div class="eq-bar"></div>
                    <div class="eq-bar"></div>
                </div>
            </div>
            <div class="badge-group">
                <span class="accessible-badge">♿ ACCESSIBLE • BLIND-FRIENDLY</span>
                <span class="status-pill">
                    <span id="statusDot" class="status-dot"></span>
                    <span id="speechStatus">READY</span>
                </span>
            </div>
        </div>

        <!-- Interactive Step Timeline Chips -->
        <div class="steps-bar">
            <div id="stepChip1" class="step-chip active" onclick="jumpToStep(1)">📍 1. Departure</div>
            <div id="stepChip2" class="step-chip" onclick="jumpToStep(2)">🛣️ 2. Corridor</div>
            <div id="stepChip3" class="step-chip" onclick="jumpToStep(3)">⚠️ 3. Safety</div>
            <div id="stepChip4" class="step-chip" onclick="jumpToStep(4)">🏁 4. Arrival</div>
        </div>

        <!-- Playback & Stepper Control Toolbar -->
        <div class="controls-row">
            <button id="btnPlayStep" class="btn-action" onclick="playCurrentStep()" title="Read active step aloud">
                <span>▶️ Play Step</span>
            </button>
            <button class="btn-action btn-secondary" onclick="prevStep()" title="Go to previous navigation step">
                <span>⏮️ Prev</span>
            </button>
            <button class="btn-action btn-secondary" onclick="nextStep()" title="Advance to next navigation step">
                <span>⏭️ Next</span>
            </button>
            <button class="btn-action btn-secondary" onclick="pauseOrResume()" title="Pause or Resume playback">
                <span id="pauseLabel">⏸️ Pause</span>
            </button>
            <button class="btn-action btn-secondary" onclick="stopAllSpeech()" title="Stop audio">
                <span>⏹️ Stop</span>
            </button>
            <button id="btnSpeed" class="btn-action btn-secondary" onclick="toggleSpeed()" title="Adjust speech pacing">
                <span id="speedLabel">🐢 0.85x Pace</span>
            </button>
            <button id="btnMic" class="btn-action btn-mic" onclick="toggleMic()" title="Speak voice commands (e.g., 'Hazards', 'ETA', 'Next')">
                <span id="micLabel">🎙️ Ask Navigator</span>
            </button>
        </div>

        <!-- Interactive Quick Voice Query Chips ("Ask Navigator") -->
        <div class="query-bar">
            <span class="query-label">💬 Quick Questions:</span>
            <button class="query-btn" onclick="askQuestion('hazards')">🚨 Hazards Ahead?</button>
            <button class="query-btn" onclick="askQuestion('next')">🛣️ Next Maneuver</button>
            <button class="query-btn" onclick="askQuestion('eta')">⏱️ ETA & Distance</button>
            <button class="query-btn" onclick="askQuestion('where')">📍 Where Am I?</button>
            <button class="query-btn" onclick="askQuestion('full')">📢 Full Briefing</button>
        </div>

        <!-- Spoken Text Caption View -->
        <div class="caption-box" id="captionText" aria-live="polite">
            <span style="color: #38bdf8; font-weight: 700;">Live Guidance:</span> <span id="captionBody">Select a step or tap <b>Play Step</b> to begin voice-guided navigation.</span>
        </div>
    </div>

    <script>
        const fullNarrative = "{safe_full}";
        const steps = [
            "{safe_step1}",
            "{safe_step2}",
            "{safe_step3}",
            "{safe_step4}"
        ];
        const answers = {{
            hazards: "{safe_hazards}",
            next: "{safe_step2}",
            eta: "{safe_eta}",
            where: "You are currently departing from {safe_origin}, navigating towards {safe_dest}.",
            full: fullNarrative
        }};

        let currentStepIndex = 0;
        let speechRate = 0.85;
        let isSpeaking = false;
        let isPaused = false;
        let recognition = null;
        let isListening = false;

        function updateUIStatus(status, isActive) {{
            const statusEl = document.getElementById('speechStatus');
            const dotEl = document.getElementById('statusDot');
            const eqEl = document.getElementById('eqWave');
            if (statusEl) statusEl.innerText = status;
            if (dotEl) {{
                if (isActive) dotEl.classList.add('active');
                else dotEl.classList.remove('active');
            }}
            if (eqEl) {{
                if (isActive) eqEl.classList.add('speaking');
                else eqEl.classList.remove('speaking');
            }}
        }}

        function setCaption(text) {{
            const el = document.getElementById('captionBody');
            if (el) el.innerText = text;
        }}

        function highlightStepChip(index) {{
            for (let i = 1; i <= 4; i++) {{
                const chip = document.getElementById('stepChip' + i);
                if (chip) {{
                    if (i === (index + 1)) chip.classList.add('active');
                    else chip.classList.remove('active');
                }}
            }}
        }}

        function speakText(text, onComplete) {{
            setCaption(text);
            if (!('speechSynthesis' in window)) {{
                if (onComplete) onComplete();
                return;
            }}
            try {{
                window.speechSynthesis.cancel();
                const utter = new SpeechSynthesisUtterance(text);
                utter.lang = '{bcp47_code}';
                utter.rate = speechRate;
                utter.pitch = 1.0;

                const voices = window.speechSynthesis.getVoices();
                const targetPrefix = utter.lang.split('-')[0].toLowerCase();
                let matched = null;
                for (let i = 0; i < voices.length; i++) {{
                    const vLang = (voices[i].lang || '').toLowerCase().replace('_', '-');
                    if (vLang === utter.lang.toLowerCase() || vLang.startsWith(targetPrefix)) {{
                        matched = voices[i];
                        break;
                    }}
                }}
                if (matched) utter.voice = matched;

                utter.onstart = function() {{
                    isSpeaking = true;
                    updateUIStatus('SPEAKING...', true);
                }};
                utter.onend = function() {{
                    isSpeaking = false;
                    updateUIStatus('READY', false);
                    if (onComplete) onComplete();
                }};
                utter.onerror = function() {{
                    isSpeaking = false;
                    updateUIStatus('READY', false);
                    if (onComplete) onComplete();
                }};

                window.speechSynthesis.speak(utter);
            }} catch(e) {{
                console.warn('SpeechSynthesis error:', e);
                isSpeaking = false;
                updateUIStatus('READY', false);
                if (onComplete) onComplete();
            }}
        }}

        function playCurrentStep() {{
            highlightStepChip(currentStepIndex);
            speakText(steps[currentStepIndex]);
        }}

        function jumpToStep(stepNumber) {{
            currentStepIndex = stepNumber - 1;
            highlightStepChip(currentStepIndex);
            speakText(steps[currentStepIndex]);
        }}

        function nextStep() {{
            if (currentStepIndex < steps.length - 1) {{
                currentStepIndex++;
            }} else {{
                currentStepIndex = 0; // loop
            }}
            highlightStepChip(currentStepIndex);
            speakText(steps[currentStepIndex]);
        }}

        function prevStep() {{
            if (currentStepIndex > 0) {{
                currentStepIndex--;
            }} else {{
                currentStepIndex = steps.length - 1;
            }}
            highlightStepChip(currentStepIndex);
            speakText(steps[currentStepIndex]);
        }}

        function pauseOrResume() {{
            if (!('speechSynthesis' in window)) return;
            const pauseLbl = document.getElementById('pauseLabel');
            if (isSpeaking && !isPaused) {{
                window.speechSynthesis.pause();
                isPaused = true;
                updateUIStatus('PAUSED', false);
                if (pauseLbl) pauseLbl.innerText = '▶️ Resume';
            }} else if (isPaused) {{
                window.speechSynthesis.resume();
                isPaused = false;
                isSpeaking = true;
                updateUIStatus('SPEAKING...', true);
                if (pauseLbl) pauseLbl.innerText = '⏸️ Pause';
            }} else {{
                playCurrentStep();
            }}
        }}

        function stopAllSpeech() {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
            }}
            isSpeaking = false;
            isPaused = false;
            updateUIStatus('STOPPED', false);
            const pauseLbl = document.getElementById('pauseLabel');
            if (pauseLbl) pauseLbl.innerText = '⏸️ Pause';
        }}

        function toggleSpeed() {{
            const lbl = document.getElementById('speedLabel');
            if (speechRate <= 0.88) {{
                speechRate = 1.0;
                if (lbl) lbl.innerText = '🚶 1.0x Pace';
            }} else if (speechRate <= 1.05) {{
                speechRate = 1.25;
                if (lbl) lbl.innerText = '⚡ 1.25x Pace';
            }} else {{
                speechRate = 0.85;
                if (lbl) lbl.innerText = '🐢 0.85x Pace';
            }}
            if (isSpeaking && !isPaused) {{
                playCurrentStep();
            }}
        }}

        function askQuestion(type) {{
            const ans = answers[type] || fullNarrative;
            updateUIStatus('ANSWERING...', true);
            speakText(ans);
        }}

        // Hands-Free Speech Recognition Listener
        function toggleMic() {{
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRec) {{
                alert('Voice command recognition is not supported in this browser. Please use Chrome or Edge.');
                return;
            }}

            const btn = document.getElementById('btnMic');
            const lbl = document.getElementById('micLabel');

            if (isListening) {{
                if (recognition) recognition.stop();
                isListening = false;
                if (btn) btn.classList.remove('listening');
                if (lbl) lbl.innerText = '🎙️ Ask Navigator';
                updateUIStatus('READY', false);
                return;
            }}

            try {{
                recognition = new SpeechRec();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = '{bcp47_code}';

                recognition.onstart = () => {{
                    isListening = true;
                    if (btn) btn.classList.add('listening');
                    if (lbl) lbl.innerText = '🔴 Listening...';
                    updateUIStatus('LISTENING...', true);
                    setCaption('Listening for your voice command (e.g., "Hazards", "ETA", "Next", "Repeat")...');
                }};

                recognition.onresult = (event) => {{
                    const transcript = event.results[0][0].transcript.toLowerCase();
                    setCaption('Heard: "' + transcript + '"');

                    const lower = transcript.toLowerCase();
                    const isHazards = /hazard|danger|caution|road|ప్రమాదం|హెచ్చరిక|खतरा|चेतावनी|ஆபத்து|எச்சரிக்கை|ಅಪಾಯ|ഹസാർഡ്|বিপদ|धोका/.test(lower);
                    const isEta = /time|eta|far|distance|దూరం|సమయం|समय|दूरी|நேரம்|தூரம்|ಸಮಯ|ದೂರ|സമയം|ദൂരം|সময়|দূরত্ব|वेळ|अंतर/.test(lower);
                    const isNext = /next|forward|తర్వాత|ముందుకు|अगला|आगे|அடுத்து|ಮುಂದೆ|അടുത്തത്|পরবর্তী|पुढे/.test(lower);
                    const isPrev = /prev|back|వెనుక|మునుపటి|पिछला|पीछे|முந்தைய|ಹಿಂದೆ|മുമ്പത്തെ|পূর্ববর্তী|मागे/.test(lower);
                    const isRepeat = /repeat|again|current|మళ్ళీ|ప్రస్తుత|फिर|पुनः|மீண்டும்|ಮತ್ತೊಮ್ಮೆ|വീണ്ടും|আবার|पुन्हा/.test(lower);
                    const isWhere = /where|location|ఎక్కడ|ప్రదేశం|कहाँ|स्थान|எங்கே|ఎಲ್ಲಿ|എവിടെ|কোথায়|कुठे/.test(lower);

                    if (isHazards) {{
                        askQuestion('hazards');
                    }} else if (isEta) {{
                        askQuestion('eta');
                    }} else if (isNext) {{
                        nextStep();
                    }} else if (isPrev) {{
                        prevStep();
                    }} else if (isRepeat) {{
                        playCurrentStep();
                    }} else if (isWhere) {{
                        askQuestion('where');
                    }} else {{
                        speakText(transcript);
                    }}
                }};

                recognition.onerror = (e) => {{
                    console.warn('Speech recognition error:', e);
                    isListening = false;
                    if (btn) btn.classList.remove('listening');
                    if (lbl) lbl.innerText = '🎙️ Ask Navigator';
                    updateUIStatus('READY', false);
                }};

                recognition.onend = () => {{
                    isListening = false;
                    if (btn) btn.classList.remove('listening');
                    if (lbl) lbl.innerText = '🎙️ Ask Navigator';
                }};

                recognition.start();
            }} catch (err) {{
                console.error(err);
                isListening = false;
                if (btn) btn.classList.remove('listening');
                if (lbl) lbl.innerText = '🎙️ Ask Navigator';
            }}
        }}
    </script>
    </body>
    </html>
    """

