"""
Centralized Internationalization (i18n) & Localization System for NexRoute
Supports 8 Languages with Native Scripts, Voice BCP-47 codes, Fallback Chains,
and Safe Dynamic Interpolation.

Supported Languages:
- English (en) — English
- Telugu (te) — తెలుగు
- Hindi (hi) — हिन्दी
- Tamil (ta) — தமிழ்
- Kannada (kn) — ಕನ್ನಡ
- Malayalam (ml) — മലയാളം
- Bengali (bn) — বাংলা
- Marathi (mr) — मराठी
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("pathfinder.i18n")

SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {"name": "English", "native": "English", "bcp47": "en-IN", "flag": "🌐"},
    "te": {"name": "Telugu", "native": "తెలుగు", "bcp47": "te-IN", "flag": "🇮🇳"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "bcp47": "hi-IN", "flag": "🇮🇳"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "bcp47": "ta-IN", "flag": "🇮🇳"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "bcp47": "kn-IN", "flag": "🇮🇳"},
    "ml": {"name": "Malayalam", "native": "മലയാളം", "bcp47": "ml-IN", "flag": "🇮🇳"},
    "bn": {"name": "Bengali", "native": "বাংলা", "bcp47": "bn-IN", "flag": "🇮🇳"},
    "mr": {"name": "Marathi", "native": "मराठी", "bcp47": "mr-IN", "flag": "🇮🇳"},
}

DEFAULT_LANGUAGE = "en"

def _load_locale_overrides():
    """Loads any user-supplied JSON files from locales/ directory."""
    locales_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "locales")
    if os.path.exists(locales_dir):
        for lang_code in SUPPORTED_LANGUAGES.keys():
            json_path = os.path.join(locales_dir, f"{lang_code}.json")
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            TRANSLATIONS.setdefault(lang_code, {}).update(data)
                except Exception as e:
                    logger.debug(f"Could not load locale override for {lang_code}: {e}")



# Complete built-in translations for high-reliability and zero network-dependency
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # App / Header / Sidebar
        "app.title": "NexRoute",
        "app.subtitle": "Predictive Adaptive Transit & Hazard-Free Intelligent Navigation",
        "app.telemetry": "Autonomous Multi-Corridor Safety Telemetry",
        "app.language": "Language",
        "app.distance_units": "Distance Units",
        "app.metric_km": "Kilometers (km)",
        "app.imperial_mi": "Miles (mi)",
        "app.active_standard": "Active Standard",
        "app.hazards": "Hazards",
        "app.closures": "Closures",
        "app.traffic": "Traffic",
        "app.priority": "Priority",
        "app.delays": "{count} Delays",
        "app.normal_flow": "Normal Flow",

        # Tabs
        "tab.copilot": "✨ AI Travel Copilot",
        "tab.navigation": "🧭 Map & Navigation",
        "tab.virtual_guide": "🚗 Virtual Guide",
        "tab.facilities": "🏥 Facilities",
        "tab.places": "🌟 Places & Sights",

        # Navigation & Inputs
        "nav.navigation": "Navigation",
        "nav.starting_point": "Starting Point",
        "nav.destination": "Destination",
        "nav.search_location": "Search Location",
        "nav.search_origin_placeholder": "Search origin or current GPS position...",
        "nav.search_dest_placeholder": "Search destination (e.g., Guntur, Vijayawada, Hospital)...",
        "nav.get_directions": "Get Directions",
        "nav.find_best_route": "Find Best Route",
        "nav.swap_locations": "Swap Starting Point & Destination",
        "nav.my_location": "My Location",
        "nav.route_found": "Route Found",
        "nav.gps_unavailable": "GPS Unavailable",
        "nav.gps_tracking_live": "Live GPS Tracking Active",
        "nav.rerouting": "Rerouting...",
        "nav.avoid_tolls": "Avoid Tolls",
        "nav.avoid_highways": "Avoid Highways",
        "nav.avoid_ferries": "Avoid Ferries",
        "nav.nearby_hospitals": "Nearby Hospitals",
        "nav.move_in_parallel": "Move in Parallel",
        "nav.traffic_stop": "Traffic Stop",
        "voice.turn_left_in": "In {dist}, turn left onto the road",
        "voice.turn_right_in": "In {dist}, turn right onto the road",
        "voice.arrived_at": "You have safely arrived at {dest}",
        "nav.objectives_title": "Routing Objectives",
        "nav.all_routes": "🌐 All Routes (Default)",
        "nav.all_routes_desc": "Displays all candidate routes simultaneously across the corridor",
        "nav.fastest": "⚡ Fastest Route",
        "nav.fastest_desc": "Minimizes transit duration & evades traffic",
        "nav.shortest": "📏 Shortest Route",
        "nav.shortest_desc": "Minimizes ground mileage & physical distance",
        "nav.balanced": "⚖️ Balanced Route",
        "nav.balanced_desc": "Harmonized 50/50 time & distance balance",
        "nav.accessible": "♿ Accessible Route",
        "nav.accessible_desc": "Prioritizes step-free paths & certified ramps",
        "nav.active_strategy": "ACTIVE STRATEGY",
        "nav.ai_preference": "AI PREFERENCE",
        "nav.speed_weight": "Speed Optimization Weight",
        "nav.distance_weight": "Distance Compression Weight",
        "nav.barrier_strictness": "Barrier Evasion Strictness",
        "nav.disambiguation_title": "Select Exact Intended Location",
        "nav.distance": "Distance",
        "nav.duration": "Duration",
        "nav.eta": "ETA",
        "nav.direct_route": "Direct Corridor",

        # Fleet & Modes
        "fleet.title": "Vehicle & Kinematics Mode",
        "fleet.driving": "Car / Driving",
        "fleet.bike": "Bike / Motorcycle",
        "fleet.walking": "Walking / Pedestrian",
        "fleet.bicycle": "Bicycle",
        "fleet.truck": "Truck / Logistics",
        "fleet.tractor": "Tractor / Farm",
        "fleet.flight": "Airway / Commercial Flight",
        "fleet.waterway": "Waterway / Maritime & Ferry",
        "fleet.speed_mode": "Speed Mode",
        "fleet.normal": "Normal Speed",
        "fleet.rush": "Express / Rush",
        "fleet.eco": "Eco-Friendly",

        # Virtual Guide & Companion
        "guide.title": "Virtual Guide Dashboard",
        "guide.section1_title": "Interactive Journey Progress",
        "guide.section2_title": "Virtual Vehicle Companion",
        "guide.section3_title": "Step-by-Step Maneuver Guide",
        "guide.section4_title": "3D Walking Perspective",
        "guide.move_parallel": "Move in Parallel",
        "guide.traffic_stop": "Traffic Stop",
        "guide.resume": "Resume Movement",
        "guide.reset": "Reset Journey",
        "guide.status": "Journey Status",
        "guide.status_stationary": "Stationary / Ready",
        "guide.status_in_transit": "In Transit • Moving",
        "guide.status_paused": "Paused (Traffic / Hazard)",
        "guide.status_arrived": "Arrived at Destination",
        "guide.speed": "Current Speed",
        "guide.remaining_dist": "Distance Remaining",
        "guide.remaining_time": "Time Remaining",
        "guide.checkpoint": "Checkpoint {current} of {total}",
        "guide.arrived": "You have arrived at your destination!",
        "guide.hazard_alert": "Caution: Hazard detected along route segment. Speed reduced.",

        # Maneuvers
        "maneuver.start": "Head out from {origin} onto {road}",
        "maneuver.turn_left": "Turn left onto {road}",
        "maneuver.turn_right": "Turn right onto {road}",
        "maneuver.straight": "Continue straight on {road}",
        "maneuver.keep_left": "Keep left onto {road}",
        "maneuver.keep_right": "Keep right onto {road}",
        "maneuver.take_exit": "Take the exit onto {road}",
        "maneuver.u_turn": "Make a U-turn onto {road}",
        "maneuver.roundabout": "At the roundabout, take exit {exit} onto {road}",
        "maneuver.arrive": "Safely arrive at {destination}",
        "maneuver.follow_route": "Follow the selected route along {road}",

        # Voice Guidance
        "voice.title": "Voice Guidance",
        "voice.enabled": "Voice Guidance Active",
        "voice.disabled": "Voice Guidance Muted",
        "voice.toggle": "Toggle Spoken Voice",
        "voice.speed": "Voice Speed",
        "voice.speed_normal": "1.0x Normal",
        "voice.speed_slow": "0.8x Slow & Clear",
        "voice.speed_fast": "1.2x Fast",
        "voice.unsupported": "Spoken voice for {lang} is not supported by your browser engine. Text guidance remains fully active.",
        "voice.speaking": "Speaking instruction...",

        # Facilities
        "fac.title": "Nearby Facilities",
        "fac.subtitle": "Emergency, refueling, medical, and rest facilities along your route",
        "fac.all": "🌐 All Facilities",
        "fac.hospitals": "🏥 Hospitals & Emergency",
        "fac.fuel": "⛽ Fuel & EV Charging",
        "fac.police": "👮 Police Stations",
        "fac.pharmacies": "💊 Pharmacies & Medical",
        "fac.food": "🍽️ Food & Restaurants",
        "fac.atm": "🏧 ATMs & Banking",
        "fac.restrooms": "🚻 Public Restrooms",
        "fac.supermarkets": "🛒 Supermarkets & Groceries",
        "fac.focus_map": "Focus Map",
        "fac.route_here": "Route Here",
        "fac.distance_km": "{dist} km away",
        "fac.none_found": "No nearby facilities found in this perimeter.",

        # Places
        "places.title": "Recommended Places Near Destination",
        "places.subtitle": "Authentic attractions, dining, and landmarks near {destination}",
        "places.no_rating": "Rating unavailable",
        "places.reviews": "{count} real Google reviews",
        "places.focus_map": "Focus Map",
        "places.route_here": "Route Here",

        # Road Intelligence & Hazards
        "hazard.title": "AI Road Intelligence",
        "hazard.all_clear": "🛡️ No hazards detected in checked area",
        "hazard.warning": "⚠️ Hazard Alert Ahead",
        "hazard.satellite": "AI Satellite Road Intelligence",
        "hazard.inspection": "Hazard Inspection",
        "hazard.route_status": "Route Status",
        "hazard.checked": "Checked & Verified",

        # Chatbot (A.U.R.A.)
        "chat.title": "A.U.R.A. Navigation Copilot",
        "chat.subtitle": "Adaptive User Route Assistant • Conversational AI",
        "chat.welcome": "👋 Greetings! I am A.U.R.A., your Adaptive User Route Assistant for NexRoute Ask me anything about routes, hazards, weather, or general knowledge!",
        "chat.placeholder": "Ask AURA...",
        "chat.send": "Send 🚀",
        "chat.reset": "🗑️ Reset Chat",
        "chat.active_provider": "Active Provider",
        "chat.quick_categories": "💡 Quick Copilot Categories:",
        "chat.quick_fastest": "⚡ Fastest Route",
        "chat.quick_compare": "🗺️ Compare Routes",
        "chat.quick_hazards": "🛡️ Check Hazards",
        "chat.quick_weather": "🌤️ Live Weather",
        "chat.quick_code": "💻 Code Helper",
        "chat.quick_story": "✍️ Creative Story",
        "chat.quick_food": "🍽️ Nearby Food",
        "chat.quick_emergency": "🏥 Emergency / SOS"
    },

    "te": {
        # App / Header / Sidebar (Telugu)
        "app.title": "NexRoute",
        "app.subtitle": "ప్రిడిక్టివ్ అడాప్టివ్ ట్రాన్సిట్ & హజార్డ్-ఫ్రీ ఇంటెలిజెంట్ నావిగేషన్",
        "app.telemetry": "స్వయంప్రతిపత్తి కలిగిన భద్రతా పర్యవేక్షణ వ్యవస్థ",
        "app.language": "భాషను ఎంచుకోండి",
        "app.distance_units": "దూర కొలతలు",
        "app.metric_km": "కిలోమీటర్లు (km)",
        "app.imperial_mi": "మైళ్ళు (mi)",
        "app.active_standard": "ప్రస్తుత కొలమానం",
        "app.hazards": "ప్రమాదాలు",
        "app.closures": "రోడ్డు మూసివేతలు",
        "app.traffic": "ట్రాఫిక్",
        "app.priority": "ప్రాధాన్యత",
        "app.delays": "{count} ఆలస్యాలు",
        "app.normal_flow": "సాధారణ రద్దీ",

        # Tabs
        "tab.copilot": "✨ AI ట్రావెల్ కోపైలట్",
        "tab.navigation": "🧭 మ్యాప్ & నావిగేషన్",
        "tab.virtual_guide": "🚗 వర్చువల్ గైడ్",
        "tab.facilities": "🏥 సదుపాయాలు",
        "tab.places": "🌟 దర్శనీయ స్థలాలు & ఆకర్షణలు",

        # Navigation & Inputs
        "nav.navigation": "నావిగేషన్",
        "nav.starting_point": "ప్రారంభ స్థానం",
        "nav.destination": "గమ్యస్థానం",
        "nav.search_location": "ప్రదేశాన్ని వెతకండి",
        "nav.search_origin_placeholder": "ప్రారంభ ప్రదేశం లేదా GPS స్థానాన్ని వెతకండి...",
        "nav.search_dest_placeholder": "గమ్యస్థానాన్ని వెతకండి (ఉదా: గుంటూరు, విజయవాడ, ఆసుపత్రి)...",
        "nav.get_directions": "దారి సూచనలు పొందండి",
        "nav.find_best_route": "ఉత్తమ మార్గాన్ని కనుగొనండి",
        "nav.swap_locations": "ప్రారంభ స్థానం & గమ్యస్థానాన్ని మార్చండి",
        "nav.my_location": "నా ప్రస్తుత స్థానం",
        "nav.route_found": "మార్గం కనుగొనబడింది",
        "nav.gps_unavailable": "GPS అందుబాటులో లేదు",
        "nav.gps_tracking_live": "ప్రత్యక్ష GPS కనెక్ట్ చేయబడింది",
        "nav.rerouting": "మరొక మార్గం లెక్కిస్తోంది...",
        "nav.avoid_tolls": "టోల్ రోడ్లను నివారించండి",
        "nav.avoid_highways": "హైవేలను నివారించండి",
        "nav.avoid_ferries": "ఫెర్రీ మార్గాలను నివారించండి",
        "nav.nearby_hospitals": "సమీపంలోని ఆసుపత్రులు",
        "nav.move_in_parallel": "వాహనంతో పాటు కదలిక ప్రారంభించండి",
        "nav.traffic_stop": "ట్రాఫిక్ కారణంగా ఆపండి",
        "voice.turn_left_in": "{dist} లో ఎడమవైపు తిరగండి",
        "voice.turn_right_in": "{dist} లో కుడివైపు తిరగండి",
        "voice.arrived_at": "మీరు సురక్షితంగా {dest} చేరుకున్నారు",
        "nav.objectives_title": "మార్గం ప్రాధాన్యతలు",
        "nav.all_routes": "🌐 అన్ని మార్గాలు (సాధారణ)",
        "nav.all_routes_desc": "ఈ ప్రాంతంలోని అన్ని అందుబాటులో ఉన్న మార్గాలను చూపిస్తుంది",
        "nav.fastest": "⚡ వేగవంతమైన మార్గం",
        "nav.fastest_desc": "ప్రయాణ సమయాన్ని మరియు ట్రాఫిక్‌ను తగ్గిస్తుంది",
        "nav.shortest": "📏 తక్కువ దూర మార్గం",
        "nav.shortest_desc": "భౌతిక దూరాన్ని మరియు మైలేజీని తగ్గిస్తుంది",
        "nav.balanced": "⚖️ సమతుల్య మార్గం",
        "nav.balanced_desc": "సమయం మరియు దూరం మధ్య సరైన సమతుల్యత",
        "nav.accessible": "♿ సులభ మార్గం (ర్యాంప్‌లు)",
        "nav.accessible_desc": "మెట్లు లేని, చక్రాల కుర్చీలకు అనుకూలమైన సురక్షిత మార్గాలు",
        "nav.active_strategy": "ప్రస్తుత వ్యూహం",
        "nav.ai_preference": "AI ఎంపిక",
        "nav.speed_weight": "వేగ ఆప్టిమైజేషన్ శాతం",
        "nav.distance_weight": "దూర తగ్గింపు శాతం",
        "nav.barrier_strictness": "అడ్డంకుల నివారణ ఖచ్చితత్వం",
        "nav.disambiguation_title": "మీరు వెళ్లాలనుకుంటున్న సరైన ప్రదేశాన్ని ఎంచుకోండి",
        "nav.distance": "దూరం",
        "nav.duration": "సమయం",
        "nav.eta": "చేరుకునే సమయం",
        "nav.direct_route": "ప్రత్యక్ష కారిడార్",

        # Fleet & Modes
        "fleet.title": "వాహనం మరియు వేగ ఎంపిక",
        "fleet.driving": "కారు / డ్రైవింగ్",
        "fleet.bike": "బైక్ / మోటార్ సైకిల్",
        "fleet.walking": "నడక / పాదచారులు",
        "fleet.bicycle": "సైకిల్",
        "fleet.truck": "ట్రక్ / సరుకు రవాణా",
        "fleet.tractor": "ట్రాక్టర్ / వ్యవసాయం",
        "fleet.speed_mode": "వేగ విధానం",
        "fleet.normal": "సాధారణ వేగం",
        "fleet.rush": "రద్దీ / ఎక్స్‌ప్రెస్",
        "fleet.eco": "పర్యావరణ హితం",

        # Virtual Guide & Companion
        "guide.title": "వర్చువల్ గైడ్ డ్యాష్‌బోర్డ్",
        "guide.section1_title": "ప్రత్యక్ష ప్రయాణ పురోగతి",
        "guide.section2_title": "వర్చువల్ వాహన సహచరుడు",
        "guide.section3_title": "దశలవారీ మలుపుల మార్గదర్శకత్వం",
        "guide.section4_title": "3D నడక దృశ్యం",
        "guide.move_parallel": "వాహనంతో పాటు కదలిక ప్రారంభించండి",
        "guide.traffic_stop": "ట్రాఫిక్ కారణంగా ఆపండి",
        "guide.resume": "ప్రయాణం కొనసాగించండి",
        "guide.reset": "ప్రయాణం మొదటికి మార్చండి",
        "guide.status": "ప్రయాణ స్థితి",
        "guide.status_stationary": "సిద్ధంగా ఉంది (ఆగి ఉంది)",
        "guide.status_in_transit": "ప్రయాణంలో ఉంది • కదులుతోంది",
        "guide.status_paused": "నిలిపివేయబడింది (ట్రాఫిక్/అడ్డంకి)",
        "guide.status_arrived": "గమ్యస్థానానికి చేరుకున్నారు",
        "guide.speed": "ప్రస్తుత వేగం",
        "guide.remaining_dist": "మిగిలిన దూరం",
        "guide.remaining_time": "మిగిలిన సమయం",
        "guide.checkpoint": "చెక్‌పాయింట్ {current} / {total}",
        "guide.arrived": "మీరు మీ గమ్యస్థానానికి చేరుకున్నారు!",
        "guide.hazard_alert": "హెచ్చరిక: ముందు మార్గంలో ప్రమాదం గుర్తించబడింది. వేగాన్ని తగ్గించండి.",

        # Maneuvers
        "maneuver.start": "{origin} నుండి {road} పైకి ప్రయాణం ప్రారంభించండి",
        "maneuver.turn_left": "{road} వైపు ఎడమకు తిరగండి",
        "maneuver.turn_right": "{road} వైపు కుడికి తిరగండి",
        "maneuver.straight": "{road} పై నేరుగా ముందుకు సాగండి",
        "maneuver.keep_left": "{road} పై ఎడమ వైపున కొనసాగండి",
        "maneuver.keep_right": "{road} పై కుడి వైపున కొనసాగండి",
        "maneuver.take_exit": "{road} వైపు నిష్క్రమించండి",
        "maneuver.u_turn": "{road} పై యూ-టర్న్ తీసుకోండి",
        "maneuver.roundabout": "రౌండ్‌ఎబౌట్ వద్ద {exit}వ నిష్క్రమణ తీసుకుని {road} పైకి వెళ్ళండి",
        "maneuver.arrive": "{destination} వద్దకు సురక్షితంగా చేరుకున్నారు",
        "maneuver.follow_route": "{road} గుండా ఎంచుకున్న మార్గాన్ని అనుసరించండి",

        # Voice Guidance
        "voice.title": "వాయిస్ గైడెన్స్ (ధ్వని సహాయం)",
        "voice.enabled": "వాయిస్ గైడెన్స్ ఆన్‌లో ఉంది",
        "voice.disabled": "వాయిస్ గైడెన్స్ నిలిపివేయబడింది",
        "voice.toggle": "వాయిస్ ఆన్/ఆఫ్ చేయండి",
        "voice.speed": "వాయిస్ వేగం",
        "voice.speed_normal": "1.0x సాధారణ వేగం",
        "voice.speed_slow": "0.8x నెమ్మదిగా & స్పష్టంగా",
        "voice.speed_fast": "1.2x వేగంగా",
        "voice.unsupported": "{lang} భాషకు మీ బ్రౌజర్ వాయిస్ మద్దతు ఇవ్వడం లేదు. స్క్రీన్ పై పాఠ్య సూచనలు యధావిధిగా పనిచేస్తాయి.",
        "voice.speaking": "మాట్లాడుతోంది...",

        # Facilities
        "fac.title": "సమీప సదుపాయాలు",
        "fac.subtitle": "మీ మార్గంలో అత్యవసర సేవలు, ఇంధనం, ఆసుపత్రులు మరియు విశ్రాంతి కేంద్రాలు",
        "fac.all": "🌐 అన్ని సదుపాయాలు",
        "fac.hospitals": "🏥 ఆసుపత్రులు & అత్యవసర సేవలు",
        "fac.fuel": "⛽ పెట్రోల్ బంకులు & EV ఛార్జింగ్",
        "fac.police": "👮 పోలీస్ స్టేషన్లు",
        "fac.pharmacies": "💊 మందుల దుకాణాలు (ఫార్మసీ)",
        "fac.food": "🍽️ రెస్టారెంట్లు & భోజన శాలలు",
        "fac.atm": "🏧 ఏటీఎంలు & బ్యాంకులు",
        "fac.restrooms": "🚻 పబ్లిక్ మరుగుదొడ్లు",
        "fac.focus_map": "మ్యాప్‌లో చూపించు",
        "fac.route_here": "ఇక్కడికి మార్గం చూపించు",
        "fac.distance_km": "{dist} కి.మీ దూరంలో ఉంది",
        "fac.none_found": "ఈ పరిధిలో ఎలాంటి సదుపాయాలు కనుగొనబడలేదు.",

        # Places
        "places.title": "గమ్యస్థాన సమీపంలోని ముఖ్య ఆకర్షణలు",
        "places.subtitle": "{destination} సమీపంలోని ప్రసిద్ధ ప్రదేశాలు, ఆహారం మరియు దర్శనీయ స్థలాలు",
        "places.no_rating": "రేటింగ్ అందుబాటులో లేదు",
        "places.reviews": "{count} నిజమైన గూగుల్ సమీక్షలు",
        "places.focus_map": "మ్యాప్‌లో చూపించు",
        "places.route_here": "ఇక్కడికి మార్గం చూపించు",

        # Road Intelligence & Hazards
        "hazard.title": "AI రోడ్డు భద్రతా విశ్లేషణ",
        "hazard.all_clear": "🛡️ తనిఖీ చేసిన ప్రాంతంలో ఎలాంటి ప్రమాదాలు లేవు",
        "hazard.warning": "⚠️ ముందు ప్రమాదం / అడ్డంకి ఉంది జాగ్రత్త",
        "hazard.satellite": "AI ఉపగ్రహ రోడ్డు విశ్లేషణ",
        "hazard.inspection": "ప్రమాద తనిఖీ",
        "hazard.route_status": "మార్గం స్థితి",
        "hazard.checked": "సురక్షితంగా ధృవీకరించబడింది",

        # Chatbot (A.U.R.A.)
        "chat.title": "A.U.R.A. నావిగేషన్ కోపైలట్",
        "chat.subtitle": "అడాప్టివ్ యూజర్ రూట్ అసిస్టెంట్ • స్మార్ట్ సంభాషణ సహాయకుడు",
        "chat.welcome": "👋 నమస్కారం! నేను A.U.R.A., NexRoute లో మీ ప్రయాణ సహాయకుడిని. మార్గాలు, భద్రత, వాతావరణం లేదా ఏదైనా సమాచారం కోసం నన్ను అడగండి!",
        "chat.placeholder": "AURA ని అడగండి...",
        "chat.send": "పంపండి 🚀",
        "chat.reset": "🗑️ చాట్ రీసెట్ చేయండి",
        "chat.active_provider": "ప్రస్తుత AI మోడల్",
        "chat.quick_categories": "💡 త్వరిత ప్రశ్నల విభాగాలు:",
        "chat.quick_fastest": "⚡ వేగవంతమైన మార్గం",
        "chat.quick_compare": "🗺️ మార్గాల పోలిక",
        "chat.quick_hazards": "🛡️ ప్రమాదాల తనిఖీ",
        "chat.quick_weather": "🌤️ వాతావరణం",
        "chat.quick_code": "💻 కోడింగ్ సహాయం",
        "chat.quick_story": "✍️ ప్రయాణ కథనం",
        "chat.quick_food": "🍽️ సమీప భోజనం",
        "chat.quick_emergency": "🏥 అత్యవసర సాయం"
    },

    "hi": {
        # App / Header / Sidebar (Hindi)
        "app.title": "NexRoute",
        "app.subtitle": "अनुमानात्मक अनुकूलनीय पारगमन और बाधा-मुक्त नेविगेशन",
        "app.telemetry": "स्वायत्त बहु-गलियारा सुरक्षा टेलीमेट्री",
        "app.language": "भाषा चुनें",
        "app.distance_units": "दूरी की इकाई",
        "app.metric_km": "किलोमीटर (km)",
        "app.imperial_mi": "मील (mi)",
        "app.active_standard": "सक्रिय मानक",
        "app.hazards": "खतरे",
        "app.closures": "सड़क बंद",
        "app.traffic": "यातायात",
        "app.priority": "प्राथमिकता",
        "app.delays": "{count} देरी",
        "app.normal_flow": "सामान्य प्रवाह",

        # Tabs
        "tab.copilot": "✨ AI ट्रैवल को-पायलट",
        "tab.navigation": "🧭 मैप और नेविगेशन",
        "tab.virtual_guide": "🚗 वर्चुअल गाइड",
        "tab.facilities": "🏥 सुविधाएं",
        "tab.places": "🌟 दर्शनीय स्थल और जगहें",

        # Navigation & Inputs
        "nav.navigation": "नेविगेशन",
        "nav.starting_point": "प्रारंभिक बिंदु",
        "nav.destination": "गंतव्य",
        "nav.search_location": "स्थान खोजें",
        "nav.search_origin_placeholder": "प्रारंभिक बिंदु या जीपीएस स्थान खोजें...",
        "nav.search_dest_placeholder": "गंतव्य स्थान खोजें (उदा. गुंटूर, विजयवाड़ा, अस्पताल)...",
        "nav.get_directions": "दिशा-निर्देश प्राप्त करें",
        "nav.find_best_route": "सर्वोत्तम मार्ग खोजें",
        "nav.swap_locations": "प्रारंभिक बिंदु और गंतव्य बदलें",
        "nav.my_location": "मेरा वर्तमान स्थान",
        "nav.route_found": "मार्ग मिल गया",
        "nav.gps_unavailable": "जीपीएस अनुपलब्ध है",
        "nav.gps_tracking_live": "लाइव जीपीएस ट्रैकिंग सक्रिय है",
        "nav.rerouting": "पुनर्मार्गण जारी...",
        "nav.avoid_tolls": "टोल से बचें",
        "nav.avoid_highways": "राजमार्ग से बचें",
        "nav.avoid_ferries": "नौका पार से बचें",
        "nav.objectives_title": "मार्ग के उद्देश्य",
        "nav.all_routes": "🌐 सभी मार्ग (डिफ़ॉल्ट)",
        "nav.all_routes_desc": "गलियारे के सभी उपलब्ध मार्गों को एक साथ दिखाता है",
        "nav.fastest": "⚡ सबसे तेज़ मार्ग",
        "nav.fastest_desc": "यात्रा के समय और ट्रैफिक को कम करता है",
        "nav.shortest": "📏 सबसे छोटा मार्ग",
        "nav.shortest_desc": "दूरी और माइलेज को कम करता है",
        "nav.balanced": "⚖️ संतुलित मार्ग",
        "nav.balanced_desc": "समय और दूरी का 50/50 सही संतुलन",
        "nav.accessible": "♿ सुगम्य मार्ग (रैंप)",
        "nav.accessible_desc": "कदम-मुक्त, व्हीलचेयर-अनुकूल प्रमाणित सुरक्षित रास्ते",
        "nav.active_strategy": "सक्रिय रणनीति",
        "nav.ai_preference": "एआई प्राथमिकता",
        "nav.speed_weight": "गति अनुकूलन भार",
        "nav.distance_weight": "दूरी संकुचन भार",
        "nav.barrier_strictness": "बाधा निवारण कड़ाई",
        "nav.disambiguation_title": "अपना सही गंतव्य चुनें",
        "nav.distance": "दूरी",
        "nav.duration": "समय",
        "nav.eta": "पहुंचने का समय",
        "nav.direct_route": "सीधा गलियारा",

        # Fleet & Modes
        "fleet.title": "वाहन और गति मोड",
        "fleet.driving": "कार / ड्राइविंग",
        "fleet.bike": "बाइक / मोटरसाइकिल",
        "fleet.walking": "पैदल / पैदल यात्री",
        "fleet.bicycle": "साइकिल",
        "fleet.truck": "ट्रक / माल ढुलाई",
        "fleet.tractor": "ट्रैक्टर / कृषि",
        "fleet.speed_mode": "गति मोड",
        "fleet.normal": "सामान्य गति",
        "fleet.rush": "द्रुत / एक्सप्रेस",
        "fleet.eco": "पर्यावरण अनुकूल",

        # Virtual Guide & Companion
        "guide.title": "वर्चुअल गाइड डैशबोर्ड",
        "guide.section1_title": "लाइव यात्रा प्रगति",
        "guide.section2_title": "वर्चुअल वाहन साथी",
        "guide.section3_title": "मोड़-दर-मोड़ मार्गदर्शन",
        "guide.section4_title": "3D पैदल दृश्य",
        "guide.move_parallel": "समानांतर गति शुरू करें",
        "guide.traffic_stop": "यातायात के कारण रोकें",
        "guide.resume": "यात्रा पुनः शुरू करें",
        "guide.reset": "यात्रा रीसेट करें",
        "guide.status": "यात्रा स्थिति",
        "guide.status_stationary": "तैयार / स्थिर",
        "guide.status_in_transit": "प्रगति पर • आगे बढ़ रहे हैं",
        "guide.status_paused": "रुका हुआ (यातायात/खतरा)",
        "guide.status_arrived": "गंतव्य पर पहुंच गए",
        "guide.speed": "वर्तमान गति",
        "guide.remaining_dist": "शेष दूरी",
        "guide.remaining_time": "शेष समय",
        "guide.checkpoint": "चेकपॉइंट {current} / {total}",
        "guide.arrived": "आप अपने गंतव्य पर पहुंच गए हैं!",
        "guide.hazard_alert": "चेतावनी: रास्ते में खतरा पाया गया है। गति कम करें।",

        # Maneuvers
        "maneuver.start": "{origin} से {road} पर आगे बढ़ें",
        "maneuver.turn_left": "{road} पर बाएं मुड़ें",
        "maneuver.turn_right": "{road} पर दाएं मुड़ें",
        "maneuver.straight": "{road} पर सीधे चलते रहें",
        "maneuver.keep_left": "{road} पर बाईं ओर रहें",
        "maneuver.keep_right": "{road} पर दाईं ओर रहें",
        "maneuver.take_exit": "{road} की ओर निकास लें",
        "maneuver.u_turn": "{road} पर यू-टर्न लें",
        "maneuver.roundabout": "गोलचक्कर में प्रवेश करें और {exit}वां निकास लेकर {road} पर जाएं",
        "maneuver.arrive": "{destination} पर सुरक्षित पहुंच गए",
        "maneuver.follow_route": "{road} पर चुने हुए मार्ग का पालन करें",

        # Voice Guidance
        "voice.title": "ध्वनि मार्गदर्शन",
        "voice.enabled": "ध्वनि मार्गदर्शन सक्रिय",
        "voice.disabled": "ध्वनि मार्गदर्शन म्यूट",
        "voice.toggle": "ध्वनि चालू/बंद करें",
        "voice.speed": "आवाज़ की गति",
        "voice.speed_normal": "1.0x सामान्य",
        "voice.speed_slow": "0.8x धीमा और स्पष्ट",
        "voice.speed_fast": "1.2x तेज़",
        "voice.unsupported": "आपके ब्राउज़र में {lang} के लिए आवाज़ उपलब्ध नहीं है। स्क्रीन पर निर्देश चालू रहेंगे।",
        "voice.speaking": "निर्देश बोला जा रहा है...",

        # Facilities
        "fac.title": "आस-पास की सुविधाएं",
        "fac.subtitle": "रास्ते में आपातकालीन सेवाएं, ईंधन, अस्पताल और विश्राम स्थल",
        "fac.all": "🌐 सभी सुविधाएं",
        "fac.hospitals": "🏥 अस्पताल और आपातकालीन",
        "fac.fuel": "⛽ ईंधन और ईवी चार्जिंग",
        "fac.police": "👮 पुलिस स्टेशन",
        "fac.pharmacies": "💊 दवाइयां और फार्मेसी",
        "fac.food": "🍽️ रेस्टोरेंट और भोजन",
        "fac.atm": "🏧 एटीएम और बैंक",
        "fac.restrooms": "🚻 सार्वजनिक शौचालय",
        "fac.focus_map": "नक्शे पर देखें",
        "fac.route_here": "यहाँ का मार्ग",
        "fac.distance_km": "{dist} किमी दूर",
        "fac.none_found": "इस क्षेत्र में कोई सुविधा नहीं मिली।",

        # Places
        "places.title": "गंतव्य के पास अनुशंसित स्थान",
        "places.subtitle": "{destination} के पास लोकप्रिय आकर्षण, भोजन और स्थल",
        "places.no_rating": "रेटिंग उपलब्ध नहीं",
        "places.reviews": "{count} वास्तविक गूगल समीक्षाएं",
        "places.focus_map": "नक्शे पर देखें",
        "places.route_here": "यहाँ का मार्ग",

        # Road Intelligence & Hazards
        "hazard.title": "एआई सड़क सुरक्षा विश्लेषण",
        "hazard.all_clear": "🛡️ जांचे गए क्षेत्र में कोई खतरा नहीं पाया गया",
        "hazard.warning": "⚠️ आगे खतरा / सड़क बाधा की चेतावनी",
        "hazard.satellite": "एआई उपग्रह सड़क विश्लेषण",
        "hazard.inspection": "खतरा निरीक्षण",
        "hazard.route_status": "मार्ग की स्थिति",
        "hazard.checked": "सुरक्षित और सत्यापित",

        # Chatbot (A.U.R.A.)
        "chat.title": "A.U.R.A. नेविगेशन सह-चालक",
        "chat.subtitle": "अनुकूलनीय उपयोगकर्ता मार्ग सहायक • संवादात्मक एआई",
        "chat.welcome": "👋 नमस्ते! मैं A.U.R.A. हूँ, NexRoute में आपका यात्रा साथी। मुझसे मार्ग, सुरक्षा, मौसम या सामान्य ज्ञान के बारे में कुछ भी पूछें!",
        "chat.placeholder": "AURA से पूछें...",
        "chat.send": "भेजें 🚀",
        "chat.reset": "🗑️ चैट रीसेट करें",
        "chat.active_provider": "सक्रिय एआई मॉडल",
        "chat.quick_categories": "💡 त्वरित श्रेणियां:",
        "chat.quick_fastest": "⚡ सबसे तेज़ मार्ग",
        "chat.quick_compare": "🗺️ मार्गों की तुलना",
        "chat.quick_hazards": "🛡️ खतरों की जांच",
        "chat.quick_weather": "🌤️ मौसम की जानकारी",
        "chat.quick_code": "💻 कोडिंग सहायता",
        "chat.quick_story": "✍️ यात्रा कहानी",
        "chat.quick_food": "🍽️ पास का खाना",
        "chat.quick_emergency": "🏥 आपातकालीन सहायता"
    },

    "ta": {
        # App / Header / Sidebar (Tamil)
        "app.title": "NexRoute",
        "app.subtitle": "முன்கணிப்பு தகவமைப்பு போக்குவரத்து & விபத்தில்லா நுண்ணறிவு வழிசெலுத்தல்",
        "app.telemetry": "தன்னாட்சி பாதுகாப்பு கண்காணிப்பு அமைப்பு",
        "app.language": "மொழியைத் தேர்வுசெய்க",
        "app.distance_units": "தூர அலகுகள்",
        "app.metric_km": "கிலோமீட்டர் (km)",
        "app.imperial_mi": "மைல் (mi)",
        "app.active_standard": "செயலில் உள்ள அளவு",
        "app.hazards": "ஆபத்துகள்",
        "app.closures": "சாலை மூடல்கள்",
        "app.traffic": "போக்குவரத்து",
        "app.priority": "முன்னுரிமை",
        "app.delays": "{count} தாமதங்கள்",
        "app.normal_flow": "சீரான ஓட்டம்",

        # Tabs
        "tab.copilot": "✨ AI பயண இணை பைலட்",
        "tab.navigation": "🧭 வரைபடம் & வழிசெலுத்தல்",
        "tab.virtual_guide": "🚗 மெய்நிகர் வழிகாட்டி",
        "tab.facilities": "🏥 வசதிகள்",
        "tab.places": "🌟 இடங்கள் & காட்சிகள்",

        # Navigation & Inputs
        "nav.navigation": "வழிசெலுத்தல்",
        "nav.starting_point": "தொடக்க இடம்",
        "nav.destination": "சேருமிடம்",
        "nav.search_location": "இடத்தைத் தேடுங்கள்",
        "nav.search_origin_placeholder": "தொடக்க இடம் அல்லது GPS இருப்பிடத்தைத் தேடுங்கள்...",
        "nav.search_dest_placeholder": "சேருமிடத்தைத் தேடுங்கள்...",
        "nav.get_directions": "திசைகளைப் பெறுக",
        "nav.find_best_route": "சிறந்த வழியைக் காண்க",
        "nav.swap_locations": "இடங்களை மாற்றவும்",
        "nav.my_location": "என் இருப்பிடம்",
        "nav.route_found": "வழி கண்டறியப்பட்டது",
        "nav.gps_unavailable": "GPS கிடைக்கவில்லை",
        "nav.gps_tracking_live": "நேரலை GPS இயக்கத்தில் உள்ளது",
        "nav.rerouting": "மறுவழியமைத்தல்...",
        "nav.avoid_tolls": "சுங்கச்சாவடிகளைத் தவிர்க்கவும்",
        "nav.avoid_highways": "நெடுஞ்சாலைகளைத் தவிர்க்கவும்",
        "nav.avoid_ferries": "படகுப் பாதைகளைத் தவிர்க்கவும்",
        "nav.objectives_title": "பாதை நோக்கங்கள்",
        "nav.all_routes": "🌐 அனைத்து வழிகள் (இயல்பு)",
        "nav.all_routes_desc": "அனைத்து மாற்றுப் பாதைகளையும் ஒரே நேரத்தில் காட்டுகிறது",
        "nav.fastest": "⚡ வேகமான வழி",
        "nav.fastest_desc": "பயண நேரத்தைக் குறைத்து போக்குவரத்து நெரிசலைத் தவிர்க்கிறது",
        "nav.shortest": "📏 குறுகிய வழி",
        "nav.shortest_desc": "தூரத்தைக் குறைக்கிறது",
        "nav.balanced": "⚖️ சமச்சீர் வழி",
        "nav.balanced_desc": "நேரம் மற்றும் தூரத்தின் சமநிலை",
        "nav.accessible": "♿ எளிதில் அணுகக்கூடிய வழி",
        "nav.accessible_desc": "படிகள் அற்ற சக்கர நாற்காலி பாதை",
        "nav.active_strategy": "செயலில் உள்ள திட்டம்",
        "nav.ai_preference": "AI முன்னுரிமை",
        "nav.speed_weight": "வேக மேம்பாட்டு விகிதம்",
        "nav.distance_weight": "தூரக் குறைப்பு விகிதம்",
        "nav.barrier_strictness": "தடை தவிர்ப்பு துல்லியம்",
        "nav.disambiguation_title": "சரியான சேருமிடத்தைத் தேர்ந்தெடுக்கவும்",
        "nav.distance": "தூரம்",
        "nav.duration": "நேரம்",
        "nav.eta": "சேரும் நேரம்",
        "nav.direct_route": "நேரடி வழித்தடம்",

        # Fleet & Modes
        "fleet.title": "வாகனம் மற்றும் வேகப் பாங்கு",
        "fleet.driving": "கார் / ஓட்டுதல்",
        "fleet.bike": "பைக் / மோட்டார் சைக்கிள்",
        "fleet.walking": "நடை / பாதசாரி",
        "fleet.bicycle": "மிதிவண்டி",
        "fleet.truck": "லாரி / சரக்கு",
        "fleet.tractor": "டிராக்டர் / விவசாயம்",
        "fleet.speed_mode": "வேகப் பாங்கு",
        "fleet.normal": "இயல்பான வேகம்",
        "fleet.rush": "விரைவு / எக்ஸ்பிரஸ்",
        "fleet.eco": "சுற்றுச்சூழல் நட்பு",

        # Virtual Guide & Companion
        "guide.title": "மெய்நிகர் வழிகாட்டி பலகை",
        "guide.section1_title": "நேரலை பயண முன்னேற்றம்",
        "guide.section2_title": "மெய்நிகர் வாகன தோழன்",
        "guide.section3_title": "திருப்ப வழிகாட்டுதல்",
        "guide.section4_title": "3D நடைபாதை தோற்றம்",
        "guide.move_parallel": "இணையாக நகரவும்",
        "guide.traffic_stop": "போக்குவரத்து நிறுத்தம்",
        "guide.resume": "பயணத்தைத் தொடரவும்",
        "guide.reset": "பயணத்தை மீட்டமைக்கவும்",
        "guide.status": "பயண நிலை",
        "guide.status_stationary": "தயாராக உள்ளது (நிறுத்தப்பட்டுள்ளது)",
        "guide.status_in_transit": "பயணத்தில் உள்ளது • நகர்கிறது",
        "guide.status_paused": "நிறுத்தப்பட்டது (போக்குவரத்து/ஆபத்து)",
        "guide.status_arrived": "சேருமிடம் அடைந்தது",
        "guide.speed": "தற்போதைய வேகம்",
        "guide.remaining_dist": "மீதமுள்ள தூரம்",
        "guide.remaining_time": "மீதமுள்ள நேரம்",
        "guide.checkpoint": "சோதனைச்சாவடி {current} / {total}",
        "guide.arrived": "நீங்கள் உங்கள் இலக்கை அடைந்துவிட்டீர்கள்!",
        "guide.hazard_alert": "எச்சரிக்கை: பாதையில் ஆபத்து உள்ளது. வேகத்தைக் குறைக்கவும்.",

        # Maneuvers
        "maneuver.start": "{origin} இலிருந்து {road} நோக்கி செல்லவும்",
        "maneuver.turn_left": "{road} மீது இடதுபுறம் திரும்பவும்",
        "maneuver.turn_right": "{road} மீது வலதுபுறம் திரும்பவும்",
        "maneuver.straight": "{road} வழியே நேராக தொடரவும்",
        "maneuver.keep_left": "{road} இல் இடதுபுறமாக செல்லவும்",
        "maneuver.keep_right": "{road} இல் வலதுபுறமாக செல்லவும்",
        "maneuver.take_exit": "{road} நோக்கி வெளியேறவும்",
        "maneuver.u_turn": "{road} இல் யு-டர்ன் எடுக்கவும்",
        "maneuver.roundabout": "சுற்றுவட்டத்தில் நுழைந்து {exit}வது வழியில் வெளியேறி {road} செல்லவும்",
        "maneuver.arrive": "{destination} பாதுகாப்பாக அடைந்தீர்கள்",
        "maneuver.follow_route": "{road} வழியே தேர்ந்தெடுக்கப்பட்ட பாதையைப் பின்தொடரவும்",

        # Voice Guidance
        "voice.title": "குரல் வழிகாட்டுதல்",
        "voice.enabled": "குரல் வழிகாட்டுதல் இயக்கத்தில் உள்ளது",
        "voice.disabled": "குரல் வழிகாட்டுதல் முடக்கப்பட்டது",
        "voice.toggle": "குரலை ஆன்/ஆஃப் செய்க",
        "voice.speed": "குரல் வேகம்",
        "voice.speed_normal": "1.0x இயல்பானது",
        "voice.speed_slow": "0.8x மெதுவாக & தெளிவாக",
        "voice.speed_fast": "1.2x வேகமாக",
        "voice.unsupported": "{lang} மொழிக்கு உங்கள் உலாவியில் குரல் வசதி இல்லை. உரை வழிகாட்டல் தொடர்ந்து செயல்படும்.",
        "voice.speaking": "வழிகாட்டுதல் பேசப்படுகிறது...",

        # Facilities
        "fac.title": "அருகிலுள்ள வசதிகள்",
        "fac.subtitle": "அவசர சேவை, எரிபொருள், மருத்துவமனை மற்றும் ஓய்வு மையங்கள்",
        "fac.all": "🌐 அனைத்து வசதிகள்",
        "fac.hospitals": "🏥 மருத்துவமனைகள் & அவசர சேவை",
        "fac.fuel": "⛽ எரிபொருள் & மின்சார வாகனம்",
        "fac.police": "👮 காவல் நிலையங்கள்",
        "fac.pharmacies": "💊 மருந்தகங்கள்",
        "fac.food": "🍽️ உணவகங்கள்",
        "fac.atm": "🏧 ஏடிஎம் & வங்கிகள்",
        "fac.restrooms": "🚻 கழிப்பறைகள்",
        "fac.focus_map": "வரைபடத்தில் காண்க",
        "fac.route_here": "இங்கு வழி காட்டவும்",
        "fac.distance_km": "{dist} கி.மீ தொலைவில்",
        "fac.none_found": "இப்பகுதியில் எந்த வசதிகளும் இல்லை.",

        # Places
        "places.title": "சேருமிடத்திற்கு அருகிலுள்ள இடங்கள்",
        "places.subtitle": "{destination} அருகிலுள்ள சுற்றுலாத் தலங்கள் மற்றும் உணவகங்கள்",
        "places.no_rating": "மதிப்பீடு இல்லை",
        "places.reviews": "{count} கூகிள் மதிப்புரைகள்",
        "places.focus_map": "வரைபடத்தில் காண்க",
        "places.route_here": "இங்கு வழி காட்டவும்",

        # Road Intelligence & Hazards
        "hazard.title": "AI சாலைப் பாதுகாப்பு நுண்ணறிவு",
        "hazard.all_clear": "🛡️ சோதனை செய்யப்பட்ட பகுதியில் எந்த ஆபத்தும் இல்லை",
        "hazard.warning": "⚠️ எச்சரிக்கை: பாதையில் ஆபத்து",
        "hazard.satellite": "செயற்கைக்கோள் சாலை நுண்ணறிவு",
        "hazard.inspection": "ஆபத்து ஆய்வு",
        "hazard.route_status": "பாதை நிலை",
        "hazard.checked": "பாதுகாப்பாக சரிபார்க்கப்பட்டது",

        # Chatbot (A.U.R.A.)
        "chat.title": "A.U.R.A. வழிசெலுத்தல் துணை",
        "chat.subtitle": "தகவமைப்பு பயனர் பாதை உதவியாளர் • உரையாடல் AI",
        "chat.welcome": "👋 வணக்கம்! நான் A.U.R.A., NexRoute இல் உங்கள் பயணத் துணை. வழிகள், பாதுகாப்பு, வானிலை பற்றி என்னிடம் கேளுங்கள்!",
        "chat.placeholder": "AURAவிடம் கேளுங்கள்...",
        "chat.send": "அனுப்பு 🚀",
        "chat.reset": "🗑️ அரட்டையை மீட்டமை",
        "chat.active_provider": "செயலில் உள்ள AI",
        "chat.quick_categories": "💡 விரைவு கேள்விகள்:",
        "chat.quick_fastest": "⚡ வேகமான வழி",
        "chat.quick_compare": "🗺️ பாதைகளை ஒப்பிடுக",
        "chat.quick_hazards": "🛡️ ஆபத்து சோதனை",
        "chat.quick_weather": "🌤️ நேரலை வானிலை",
        "chat.quick_code": "💻 நிரலாக்க உதவி",
        "chat.quick_story": "✍️ பயணக் கதை",
        "chat.quick_food": "🍽️ அருகிலுள்ள உணவகம்",
        "chat.quick_emergency": "🏥 அவசர உதவி"
    },

    "kn": {
        # App / Header / Sidebar (Kannada)
        "app.title": "NexRoute",
        "app.subtitle": "ಮುನ್ಸೂಚಕ ಹೊಂದಿಕೊಳ್ಳುವ ಸಾರಿಗೆ ಮತ್ತು ಅಪಾಯಮುಕ್ತ ಸ್ಮಾರ್ಟ್ ಸಂಚಾರ",
        "app.telemetry": "ಸ್ವಾಯತ್ತ ಸುರಕ್ಷತಾ ವ್ಯವಸ್ಥೆ",
        "app.language": "ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "app.distance_units": "ದೂರದ ಘಟಕಗಳು",
        "app.metric_km": "ಕಿಲೋಮೀಟರ್ (km)",
        "app.imperial_mi": "ಮೈಲಿ (mi)",
        "app.active_standard": "ಸಕ್ರಿಯ ಪ್ರಮಾಣ",
        "app.hazards": "ಅಪಾಯಗಳು",
        "app.closures": "ರಸ್ತೆ ಮುಚ್ಚುವಿಕೆ",
        "app.traffic": "ಸಂಚಾರ ದಟ್ಟಣೆ",
        "app.priority": "ಆದ್ಯತೆ",
        "app.delays": "{count} ವಿಳಂಬಗಳು",
        "app.normal_flow": "ಸಾಮಾನ್ಯ ಸಂಚಾರ",

        # Tabs
        "tab.copilot": "✨ AI ಟ್ರಾವೆಲ್ ಕೊ-ಪೈಲಟ್",
        "tab.navigation": "🧭 ನಕ್ಷೆ & ನ್ಯಾವಿಗೇಷನ್",
        "tab.virtual_guide": "🚗 ವರ್ಚುವಲ್ ಮಾರ್ಗದರ್ಶಿ",
        "tab.facilities": "🏥 ಸೌಲಭ್ಯಗಳು",
        "tab.places": "🌟 ಪ್ರಮುಖ ಸ್ಥಳಗಳು & ದೃಶ್ಯಗಳು",

        # Navigation & Inputs
        "nav.navigation": "ನ್ಯಾವಿಗೇಷನ್",
        "nav.starting_point": "ಪ್ರಾರಂಭ ಸ್ಥಳ",
        "nav.destination": "ಗಮ್ಯಸ್ಥಾನ",
        "nav.search_location": "ಸ್ಥಳವನ್ನು ಹುಡುಕಿ",
        "nav.search_origin_placeholder": "ಪ್ರಾರಂಭ ಸ್ಥಳ ಅಥವಾ GPS ಹುಡುಕಿ...",
        "nav.search_dest_placeholder": "ಗಮ್ಯಸ್ಥಾನವನ್ನು ಹುಡುಕಿ...",
        "nav.get_directions": "ದಿಕ್ಕುಗಳನ್ನು ಪಡೆಯಿರಿ",
        "nav.find_best_route": "ಉತ್ತಮ ಮಾರ್ಗ ಹುಡುಕಿ",
        "nav.swap_locations": "ಸ್ಥಳಗಳನ್ನು ಅದಲು ಬದಲು ಮಾಡಿ",
        "nav.my_location": "ನನ್ನ ಪ್ರಸ್ತುತ ಸ್ಥಳ",
        "nav.route_found": "ಮಾರ್ಗ ಕಂಡುಬಂದಿದೆ",
        "nav.gps_unavailable": "GPS ಲಭ್ಯವಿಲ್ಲ",
        "nav.gps_tracking_live": "ಲೈವ್ GPS ಸಕ್ರಿಯವಾಗಿದೆ",
        "nav.rerouting": "ಮರುಮಾರ್ಗ ಮಾಡಲಾಗುತ್ತಿದೆ...",
        "nav.avoid_tolls": "ಟೋಲ್ ತಪ್ಪಿಸಿ",
        "nav.avoid_highways": "ಹೆದ್ದಾರಿ ತಪ್ಪಿಸಿ",
        "nav.avoid_ferries": "ದೋಣಿ ತಪ್ಪಿಸಿ",
        "nav.objectives_title": "ಮಾರ್ಗದ ಆದ್ಯತೆಗಳು",
        "nav.all_routes": "🌐 ಎಲ್ಲ ಮಾರ್ಗಗಳು (ಸಾಮಾನ್ಯ)",
        "nav.all_routes_desc": "ಲಭ್ಯವಿರುವ ಎಲ್ಲ ಪರ್ಯಾಯ ಮಾರ್ಗಗಳನ್ನು ಒಟ್ಟಿಗೆ ತೋರಿಸುತ್ತದೆ",
        "nav.fastest": "⚡ ಅತಿವೇಗದ ಮಾರ್ಗ",
        "nav.fastest_desc": "ಸಮಯ ಮತ್ತು ಟ್ರಾಫಿಕ್ ಕಡಿಮೆ ಮಾಡುತ್ತದೆ",
        "nav.shortest": "📏 ಚಿಕ್ಕ ಮಾರ್ಗ",
        "nav.shortest_desc": "ದೂರ ಮತ್ತು ಮೈಲೇಜ್ ಉಳಿಸುತ್ತದೆ",
        "nav.balanced": "⚖️ ಸಮತೋಲಿತ ಮಾರ್ಗ",
        "nav.balanced_desc": "ಸಮಯ ಮತ್ತು ದೂರದ ಸಮತೋಲನ",
        "nav.accessible": "♿ ಅಡೆತಡೆ ರಹಿತ ಮಾರ್ಗ",
        "nav.accessible_desc": "ಮೆಟ್ಟಿಲುಗಳಿಲ್ಲದ ವೀಲ್‌ಚೇರ್ ಸ್ನೇಹಿ ಸುರಕ್ಷಿತ ಹಾದಿ",
        "nav.active_strategy": "ಸಕ್ರಿಯ ತಂತ್ರ",
        "nav.ai_preference": "AI ಆದ್ಯತೆ",
        "nav.speed_weight": "ವೇಗ ಆಪ್ಟಿಮೈಸೇಶನ್ ತೂಕ",
        "nav.distance_weight": "ದೂರ ಸಂಕೋಚನ ತೂಕ",
        "nav.barrier_strictness": "ಅಡೆತಡೆ ನಿವಾರಣೆಯ ಕಟ್ಟುನಿಟ್ಟು",
        "nav.disambiguation_title": "ನಿಮ್ಮ ಸರಿಯಾದ ಗಮ್ಯಸ್ಥಾನವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "nav.distance": "ದೂರ",
        "nav.duration": "ಸಮಯ",
        "nav.eta": "ತಲುಪುವ ಸಮಯ",
        "nav.direct_route": "ನೇರ ಮಾರ್ಗ",

        # Fleet & Modes
        "fleet.title": "ವಾಹನ ಮತ್ತು ವೇಗ ಮೋಡ್",
        "fleet.driving": "ಕಾರು / ಡ್ರೈವಿಂಗ್",
        "fleet.bike": "ಬೈಕ್ / ಮೋಟಾರ್ ಸೈಕಲ್",
        "fleet.walking": "ನಡಿಗೆ / ಪಾದಚಾರಿ",
        "fleet.bicycle": "ಸೈಕಲ್",
        "fleet.truck": "ಟ್ರಕ್ / ಸರಕು ಸಾಗಣೆ",
        "fleet.tractor": "ಟ್ರಾಕ್ಟರ್ / ಕೃಷಿ",
        "fleet.speed_mode": "ವೇಗ ಮೋಡ್",
        "fleet.normal": "ಸಾಮಾನ್ಯ ವೇಗ",
        "fleet.rush": "ವೇಗದ ಓಡಾಟ",
        "fleet.eco": "ಪರಿಸರ ಸ್ನೇಹಿ",

        # Virtual Guide & Companion
        "guide.title": "ವರ್ಚುವಲ್ ಗೈಡ್ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "guide.section1_title": "ಲೈವ್ ಪ್ರಯಾಣ ಪ್ರಗತಿ",
        "guide.section2_title": "ವರ್ಚುವಲ್ ವಾಹನ ಸಂಗಾತಿ",
        "guide.section3_title": "ಹಂತ ಹಂತದ ತಿರುವು ಮಾರ್ಗದರ್ಶನ",
        "guide.section4_title": "3D ನಡಿಗೆ ನೋಟ",
        "guide.move_parallel": "ಜೊತೆಗೆ ಚಲನೆ ಪ್ರಾರಂಭಿಸಿ",
        "guide.traffic_stop": "ಟ್ರಾಫಿಕ್ ಕಾರಣದಿಂದ ನಿಲ್ಲಿಸಿ",
        "guide.resume": "ಪ್ರಯಾಣ ಮುಂದುವರಿಸಿ",
        "guide.reset": "ಮರುಹೊಂದಿಸಿ",
        "guide.status": "ಪ್ರಯಾಣ ಸ್ಥಿತಿ",
        "guide.status_stationary": "ಸಿದ್ಧವಾಗಿದೆ (ನಿಲ್ಲಿಸಲಾಗಿದೆ)",
        "guide.status_in_transit": "ಚಲನೆಯಲ್ಲಿದೆ",
        "guide.status_paused": "ತಾತ್ಕಾಲಿಕವಾಗಿ ನಿಲ್ಲಿಸಲಾಗಿದೆ",
        "guide.status_arrived": "ಗಮ್ಯಸ್ಥಾನ ತಲುಪಿದೆ",
        "guide.speed": "ಪ್ರಸ್ತುತ ವೇಗ",
        "guide.remaining_dist": "ಉಳಿದ ದೂರ",
        "guide.remaining_time": "ಉಳಿದ ಸಮಯ",
        "guide.checkpoint": "ಚೆಕ್‌ಪಾಯಿಂಟ್ {current} / {total}",
        "guide.arrived": "ನೀವು ನಿಮ್ಮ ಗಮ್ಯಸ್ಥಾನವನ್ನು ತಲುಪಿದ್ದೀರಿ!",
        "guide.hazard_alert": "ಎಚ್ಚರಿಕೆ: ಮುಂದೆ ಅಪಾಯವಿದೆ. ವೇಗ ಕಡಿಮೆ ಮಾಡಿ.",

        # Maneuvers
        "maneuver.start": "{origin} ನಿಂದ {road} ಕಡೆಗೆ ಮುಂದುವರಿಯಿರಿ",
        "maneuver.turn_left": "{road} ಕಡೆಗೆ ಎಡಕ್ಕೆ ತಿರುಗಿ",
        "maneuver.turn_right": "{road} ಕಡೆಗೆ ಬಲಕ್ಕೆ ತಿರುಗಿ",
        "maneuver.straight": "{road} ನಲ್ಲಿ ನೇರವಾಗಿ ಮುಂದುವರಿಯಿರಿ",
        "maneuver.keep_left": "{road} ನಲ್ಲಿ ಎಡಭಾಗದಲ್ಲೇ ಇರಿ",
        "maneuver.keep_right": "{road} ನಲ್ಲಿ ಬಲಭಾಗದಲ್ಲೇ ಇರಿ",
        "maneuver.take_exit": "{road} ಕಡೆಗೆ ನಿರ್ಗಮಿಸಿ",
        "maneuver.u_turn": "{road} ನಲ್ಲಿ ಯು-ಟರ್ನ್ ತೆಗೆದುಕೊಳ್ಳಿ",
        "maneuver.roundabout": "ವೃತ್ತ ಪ್ರವೇಶಿಸಿ {exit}ನೇ ನಿರ್ಗಮನ ತೆಗೆದುಕೊಂಡು {road} ಕಡೆಗೆ ಹೋಗಿ",
        "maneuver.arrive": "{destination} ತಲುಪಿದ್ದೀರಿ",
        "maneuver.follow_route": "{road} ನಲ್ಲಿ ಆಯ್ಕೆಮಾಡಿದ ಮಾರ್ಗವನ್ನು ಅನುಸರಿಸಿ",

        # Voice Guidance
        "voice.title": "ಧ್ವನಿ ಮಾರ್ಗದರ್ಶನ",
        "voice.enabled": "ಧ್ವನಿ ಮಾರ್ಗದರ್ಶನ ಸಕ್ರಿಯವಾಗಿದೆ",
        "voice.disabled": "ಧ್ವನಿ ಮಾರ್ಗದರ್ಶನ ಸ್ಥಗಿತಗೊಂಡಿದೆ",
        "voice.toggle": "ಧ್ವನಿ ಆನ್/ಆಫ್",
        "voice.speed": "ಧ್ವನಿ ವೇಗ",
        "voice.speed_normal": "1.0x ಸಾಮಾನ್ಯ",
        "voice.speed_slow": "0.8x ನಿಧಾನ ಮತ್ತು ಸ್ಪಷ್ಟ",
        "voice.speed_fast": "1.2x ವೇಗ",
        "voice.unsupported": "{lang} ಭಾಷೆಗೆ ನಿಮ್ಮ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಧ್ವನಿ ಸೌಲಭ್ಯ ಲಭ್ಯವಿಲ್ಲ. ಪಠ್ಯ ಮಾರ್ಗದರ್ಶನ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ.",
        "voice.speaking": "ಮಾತನಾಡುತ್ತಿದೆ...",

        # Facilities
        "fac.title": "ಹತ್ತಿರದ ಸೌಲಭ್ಯಗಳು",
        "fac.subtitle": "ತುರ್ತು ಸೇವೆಗಳು, ಇಂಧನ, ಆಸ್ಪತ್ರೆಗಳು ಮತ್ತು ವಿಶ್ರಾಂತಿ ಸ್ಥಳಗಳು",
        "fac.all": "🌐 ಎಲ್ಲ ಸೌಲಭ್ಯಗಳು",
        "fac.hospitals": "🏥 ಆಸ್ಪತ್ರೆಗಳು & ತುರ್ತು ಸೇವೆ",
        "fac.fuel": "⛽ ಇಂಧನ & ಇವಿ ಚಾರ್ಜಿಂಗ್",
        "fac.police": "👮 ಪೊಲೀಸ್ ಠಾಣೆಗಳು",
        "fac.pharmacies": "💊 ಔಷಧಿ ಅಂಗಡಿಗಳು",
        "fac.food": "🍽️ ಆಹಾರ & ಉಪಾಹಾರ ಗೃಹಗಳು",
        "fac.atm": "🏧 ಎಟಿಎಂ & ಬ್ಯಾಂಕುಗಳು",
        "fac.restrooms": "🚻 ಸಾರ್ವಜನಿಕ ಶೌಚಾಲಯಗಳು",
        "fac.focus_map": "ನಕ್ಷೆಯಲ್ಲಿ ನೋಡಿ",
        "fac.route_here": "ಇಲ್ಲಿಗೆ ಮಾರ್ಗ",
        "fac.distance_km": "{dist} ಕಿ.ಮೀ ದೂರ",
        "fac.none_found": "ಈ ವ್ಯಾಪ್ತಿಯಲ್ಲಿ ಯಾವುದೇ ಸೌಲಭ್ಯಗಳಿಲ್ಲ.",

        # Places
        "places.title": "ಗಮ್ಯಸ್ಥಾನದ ಸಮೀಪದ ಶಿಫಾರಸು ಸ್ಥಳಗಳು",
        "places.subtitle": "{destination} ಸಮೀಪದ ಪ್ರವಾಸಿ ತಾಣಗಳು ಮತ್ತು ಆಹಾರ",
        "places.no_rating": "ರೇಟಿಂಗ್ ಲಭ್ಯವಿಲ್ಲ",
        "places.reviews": "{count} ಗೂಗಲ್ ವಿಮರ್ಶೆಗಳು",
        "places.focus_map": "ನಕ್ಷೆಯಲ್ಲಿ ನೋಡಿ",
        "places.route_here": "ಇಲ್ಲಿಗೆ ಮಾರ್ಗ",

        # Road Intelligence & Hazards
        "hazard.title": "AI ರಸ್ತೆ ಸುರಕ್ಷತಾ ವಿಶ್ಲೇಷಣೆ",
        "hazard.all_clear": "🛡️ ತಪಾಸಣೆ ಮಾಡಿದ ಪ್ರದೇಶದಲ್ಲಿ ಯಾವುದೇ ಅಪಾಯವಿಲ್ಲ",
        "hazard.warning": "⚠️ ಎಚ್ಚರಿಕೆ: ಮುಂದೆ ಅಪಾಯವಿದೆ",
        "hazard.satellite": "ಎಐ ಉಪಗ್ರಹ ರಸ್ತೆ ವಿಶ್ಲೇಷಣೆ",
        "hazard.inspection": "ಅಪಾಯ ಪರಿಶೀಲನೆ",
        "hazard.route_status": "ಮಾರ್ಗದ ಸ್ಥಿತಿ",
        "hazard.checked": "ಪರಿಶೀಲಿಸಲಾಗಿದೆ ಮತ್ತು ಸುರಕ್ಷಿತ",

        # Chatbot (A.U.R.A.)
        "chat.title": "A.U.R.A. ನ್ಯಾವಿಗೇಷನ್ ಸಹಾಯಕ",
        "chat.subtitle": "ಸ್ಮಾರ್ಟ್ ಸಂಭಾಷಣಾ AI ಸಹಾಯಕ",
        "chat.welcome": "👋 ನಮಸ್ಕಾರ! ನಾನು A.U.R.A., NexRoute ನಲ್ಲಿ ನಿಮ್ಮ ಮಾರ್ಗದರ್ಶಿ. ಮಾರ್ಗ, ಸುರಕ್ಷತೆ ಅಥವಾ ಹವಾಮಾನದ ಬಗ್ಗೆ ಕೇಳಿ!",
        "chat.placeholder": "AURA ಅನ್ನು ಕೇಳಿ...",
        "chat.send": "ಕಳುಹಿಸಿ 🚀",
        "chat.reset": "🗑️ ಚಾಟ್ ಮರುಹೊಂದಿಸಿ",
        "chat.active_provider": "ಸಕ್ರಿಯ AI",
        "chat.quick_categories": "💡 ತ್ವರಿತ ಪ್ರಶ್ನೆಗಳು:",
        "chat.quick_fastest": "⚡ ಅತಿವೇಗದ ಮಾರ್ಗ",
        "chat.quick_compare": "🗺️ ಮಾರ್ಗಗಳ ಹೋಲಿಕೆ",
        "chat.quick_hazards": "🛡️ ಅಪಾಯ ತಪಾಸಣೆ",
        "chat.quick_weather": "🌤️ ಹವಾಮಾನ ಮಾಹಿತಿ",
        "chat.quick_code": "💻 ಕೋಡಿಂಗ್ ಸಹಾಯ",
        "chat.quick_story": "✍️ ಪ್ರಯಾಣ ಕಥೆ",
        "chat.quick_food": "🍽️ ಹತ್ತಿರದ ಊಟ",
        "chat.quick_emergency": "🏥 ತುರ್ತು ನೆರವು"
    },

    "ml": {
        # App / Header / Sidebar (Malayalam)
        "app.title": "NexRoute",
        "app.subtitle": "അഡാപ്റ്റീവ് ട്രാൻസിറ്റ് & അപകടരഹിത നാവിഗേഷൻ",
        "app.telemetry": "സുരക്ഷാ നിരീക്ഷണ സംവിധാനം",
        "app.language": "ഭാഷ തിരഞ്ഞെടുക്കുക",
        "app.distance_units": "ദൂര യൂണിറ്റ്",
        "app.metric_km": "കിലോമീറ്റർ (km)",
        "app.imperial_mi": "മൈൽ (mi)",
        "app.active_standard": "സജീവ അളവ്",
        "app.hazards": "അപകടങ്ങൾ",
        "app.closures": "റോഡ് തടസ്സങ്ങൾ",
        "app.traffic": "ട്രാഫിക്",
        "app.priority": "മുൻഗണന",
        "app.delays": "{count} കാലതാമസങ്ങൾ",
        "app.normal_flow": "സാധാരണ ഒഴുക്ക്",

        # Tabs
        "tab.copilot": "✨ AI ട്രാവൽ കോ-പൈലറ്റ്",
        "tab.navigation": "🧭 മാപ്പ് & നാവിഗേഷൻ",
        "tab.virtual_guide": "🚗 വെർച്വಲ್ ഗൈഡ്",
        "tab.facilities": "🏥 സേവനങ്ങൾ",
        "tab.places": "🌟 സ്ഥലങ്ങളും കാഴ്ചകളും",

        # Navigation & Inputs
        "nav.navigation": "നാവിഗേഷൻ",
        "nav.starting_point": "തുടങ്ങുന്ന സ്ഥലം",
        "nav.destination": "ലക്ഷ്യസ്ഥാനം",
        "nav.search_location": "സ്ഥലം തിരയുക",
        "nav.search_origin_placeholder": "തുടങ്ങുന്ന സ്ഥലം അല്ലെങ്കിൽ GPS തിരയുക...",
        "nav.search_dest_placeholder": "ലക്ഷ്യസ്ഥാനം തിരയുക...",
        "nav.get_directions": "വഴി അറിയുക",
        "nav.find_best_route": "മികച്ച വഴി കണ്ടെത്തുക",
        "nav.swap_locations": "സ്ഥലങ്ങൾ മാറ്റുക",
        "nav.my_location": "എന്റെ ലൊക്കേഷൻ",
        "nav.route_found": "വഴി കണ്ടെത്തി",
        "nav.gps_unavailable": "GPS ലഭ്യമല്ല",
        "nav.gps_tracking_live": "ലൈവ് GPS സജീവമാണ്",
        "nav.rerouting": "പുതിയ വഴി മാറ്റുന്നു...",
        "nav.avoid_tolls": "ടോൾ ഒഴിവാക്കുക",
        "nav.avoid_highways": "ഹൈവേ ഒഴിവാക്കുക",
        "nav.avoid_ferries": "ഫെറി ഒഴിവാക്കുക",
        "nav.objectives_title": "യാത്രാ മുൻഗണനകൾ",
        "nav.all_routes": "🌐 എല്ലാ വഴികളും (ഡിഫോൾട്ട്)",
        "nav.all_routes_desc": "എല്ലാ ഇതര വഴികളും ഒരുമിച്ച് കാണിക്കുന്നു",
        "nav.fastest": "⚡ ഏറ്റവും വേഗതയേറിയ വഴി",
        "nav.fastest_desc": "യാത്രാ സമയം കുറയ്ക്കുകയും ട്രാഫിക് ഒഴിവാക്കുകയും ചെയ്യുന്നു",
        "nav.shortest": "📏 ഏറ്റവും ചെറിയ ദൂരം",
        "nav.shortest_desc": "ദൂരം കുറയ്ക്കുന്നു",
        "nav.balanced": "⚖️ തുല്യമായ വഴി",
        "nav.balanced_desc": "സമയവും ദൂരവും തുല്യമായി പരിഗണിക്കുന്നു",
        "nav.accessible": "♿ തടസ്സമില്ലാത്ത വഴി",
        "nav.accessible_desc": "പടികളില്ലാത്ത വീൽചെയർ സൗഹൃദ പാത",
        "nav.active_strategy": "സജീവ തന്ത്രം",
        "nav.ai_preference": "AI മുൻഗണന",
        "nav.speed_weight": "വേഗത ഒപ്റ്റിമൈസേഷൻ ഭാരം",
        "nav.distance_weight": "ദൂരം ചുരുക്കൽ ഭാരം",
        "nav.barrier_strictness": "തടസ്സങ്ങൾ ഒഴിവാക്കൽ കൃത്യത",
        "nav.disambiguation_title": "ശരിയായ സ്ഥലം തിരഞ്ഞെടുക്കുക",
        "nav.distance": "ദൂരം",
        "nav.duration": "സമയം",
        "nav.eta": "എത്തിച്ചേരുന്ന സമയം",
        "nav.direct_route": "നേരിട്ടുള്ള വഴി",

        # Fleet & Modes
        "fleet.title": "വാഹനവും വേഗതയും",
        "fleet.driving": "കാർ / ഡ്രൈവിംഗ്",
        "fleet.bike": "ബൈക്ക് / മോട്ടോർസൈക്കിൾ",
        "fleet.walking": "നടത്തം / കാൽനട",
        "fleet.bicycle": "സൈക്കിൾ",
        "fleet.truck": "ട്രക്ക് / ലോജിസ്റ്റിക്സ്",
        "fleet.tractor": "ട്രാക്ടർ / കൃഷി",
        "fleet.speed_mode": "വേഗത രീതി",
        "fleet.normal": "സാധാരണ വേഗത",
        "fleet.rush": "എക്സ്പ്രസ്സ് വേഗത",
        "fleet.eco": "പരിസ്ഥിതി സൗഹൃദം",

        # Virtual Guide & Companion
        "guide.title": "വെർച്വൽ ഗൈഡ് ഡാഷ്‌ബോർഡ്",
        "guide.section1_title": "ലൈവ് യാത്രാ പുരോഗതി",
        "guide.section2_title": "വെർച്വൽ യാത്രാ സഹായി",
        "guide.section3_title": "ഘട്ടങ്ങൾ തിരിച്ചുള്ള വഴി",
        "guide.section4_title": "3D നടത്ത ദൃശ്യം",
        "guide.move_parallel": "സമാന്തരമായി മുന്നോട്ട് നീങ്ങുക",
        "guide.traffic_stop": "ട്രാഫിക് കാരണം നിർത്തുക",
        "guide.resume": "തുടരുക",
        "guide.reset": "റീസെറ്റ് ചെയ്യുക",
        "guide.status": "യാത്രാ നില",
        "guide.status_stationary": "തയ്യാറാണ് (നിർത്തിയിരിക്കുന്നു)",
        "guide.status_in_transit": "യാത്രയിൽ • നീങ്ങുന്നു",
        "guide.status_paused": "താൽക്കാലികമായി നിർത്തി",
        "guide.status_arrived": "ലക്ഷ്യസ്ഥാനത്ത് എത്തി",
        "guide.speed": "നിലവിലെ വേഗത",
        "guide.remaining_dist": "ബാക്കി ദൂരം",
        "guide.remaining_time": "ബാക്കി സമയം",
        "guide.checkpoint": "ചെക്ക്‌പോയിന്റ് {current} / {total}",
        "guide.arrived": "നിങ്ങൾ ലക്ഷ്യസ്ഥാനത്ത് എത്തിച്ചേർന്നു!",
        "guide.hazard_alert": "മുന്നറിയിപ്പ്: റോഡിൽ തടസ്സമുണ്ട്. വേഗത കുറയ്ക്കുക.",

        # Maneuvers
        "maneuver.start": "{origin}-ൽ നിന്ന് {road} ഭാഗത്തേക്ക് നീങ്ങുക",
        "maneuver.turn_left": "{road}-ലേക്ക് ഇടത്തോട്ട് തിരിയുക",
        "maneuver.turn_right": "{road}-ലേക്ക് വലത്തോട്ട് തിരിയുക",
        "maneuver.straight": "{road}-ലൂടെ നേരെ മുന്നോട്ട് പോവുക",
        "maneuver.keep_left": "{road}-ൽ ഇടതുവശം ചേർന്ന് പോവുക",
        "maneuver.keep_right": "{road}-ൽ വലതുവശം ചേർന്ന് പോവുക",
        "maneuver.take_exit": "{road}-ലേക്ക് എക്സിറ്റ് എടുക്കുക",
        "maneuver.u_turn": "{road}-ൽ യു-ടേൺ എടുക്കുക",
        "maneuver.roundabout": "റൗണ്ട് എബൗട്ടിലൂടെ {exit}-ാം എക്സിറ്റ് എടുത്ത് {road}-ലേക്ക് പോവുക",
        "maneuver.arrive": "{destination}-ൽ സുരക്ഷിതമായി എത്തിച്ചേർന്നു",
        "maneuver.follow_route": "{road}-ലൂടെ തിരഞ്ഞെടുത്ത വഴി പിന്തുടരുക",

        # Voice Guidance
        "voice.title": "ശബ്ദ നിർദ്ദേശങ്ങൾ",
        "voice.enabled": "വോയ്സ് ഗൈഡൻസ് സജീവമാണ്",
        "voice.disabled": "വോയ്സ് ഗൈഡൻസ് ഓഫാണ്",
        "voice.toggle": "ശബ്ദം ഓൺ/ഓഫ് ചെയ്യുക",
        "voice.speed": "വോയ്സ് വേഗത",
        "voice.speed_normal": "1.0x സാധാരണ വേഗത",
        "voice.speed_slow": "0.8x പതുക്കെ & വ്യക്തമായി",
        "voice.speed_fast": "1.2x വേഗത്തിൽ",
        "voice.unsupported": "{lang} ഭാഷയിൽ നിങ്ങളുടെ ബ്രൗസറിൽ ശബ്ദം ലഭ്യമല്ല. വാചക നിർദ്ദേശങ്ങൾ ലഭ്യമാണ്.",
        "voice.speaking": "നിർദ്ദേശം സംസാരിക്കുന്നു...",

        # Facilities
        "fac.title": "അടുത്തുള്ള സേവനങ്ങൾ",
        "fac.subtitle": "അടിയന്തര സേവനങ്ങൾ, ഇന്ധനം, ആശുപത്രികൾ, വിശ്രമ കേന്ദ്രങ്ങൾ",
        "fac.all": "🌐 എല്ലാ സേവനങ്ങളും",
        "fac.hospitals": "🏥 ആശുപത്രികൾ",
        "fac.fuel": "⛽ ഇന്ധന പമ്പ് & ഇവി ചാർജിങ്",
        "fac.police": "👮 പോലീസ് സ്റ്റേഷൻ",
        "fac.pharmacies": "💊 മെഡിക്കൽ ഷോപ്പുകൾ",
        "fac.food": "🍽️ ഭക്ഷണശാലകൾ",
        "fac.atm": "🏧 എടിഎം & ബാങ്കുകൾ",
        "fac.restrooms": "🚻 ശൗചാലയങ്ങൾ",
        "fac.focus_map": "മാപ്പിൽ കാണുക",
        "fac.route_here": "ഇവിടേക്ക് വഴി",
        "fac.distance_km": "{dist} കി.മീ ദൂരം",
        "fac.none_found": "ഈ പ്രദേശത്ത് സേവനങ്ങളൊന്നും കണ്ടെത്തിയില്ല.",

        # Places
        "places.title": "ലക്ഷ്യസ്ഥാനത്തിനടുത്തുള്ള സ്ഥലങ്ങൾ",
        "places.subtitle": "{destination} സമീപമുള്ള പ്രശസ്ത സ്ഥലങ്ങളും ഭക്ഷണശാലകളും",
        "places.no_rating": "റേറ്റിംഗ് ലഭ്യമല്ല",
        "places.reviews": "{count} ഗൂഗിൾ അവലോകനങ്ങൾ",
        "places.focus_map": "മാപ്പിൽ കാണുക",
        "places.route_here": "ഇവിടേക്ക് വഴി",

        # Road Intelligence & Hazards
        "hazard.title": "AI റോഡ് സുരക്ഷാ നിരീക്ഷണം",
        "hazard.all_clear": "🛡️ പരിശോധിച്ച സ്ഥലത്ത് അപകടങ്ങളൊന്നുമില്ല",
        "hazard.warning": "⚠️ മുന്നറിയിപ്പ്: റോഡിൽ തടസ്സം",
        "hazard.satellite": "എഐ ഉപഗ്രഹ റോഡ് വിശകലനം",
        "hazard.inspection": "അപകട പരിശോധന",
        "hazard.route_status": "റോഡ് നില",
        "hazard.checked": "സുരക്ഷിതമെന്ന് പരിശോധിച്ചു",

        # Chatbot (A.U.R.A.)
        "chat.title": "A.U.R.A. നാവിഗേഷൻ സഹായകൻ",
        "chat.subtitle": "സ്മാർട്ട് സംഭാഷണ AI അസിസ്റ്റന്റ്",
        "chat.welcome": "👋 നമസ്കാരം! ഞാൻ A.U.R.A., NexRoute-ൽ നിങ്ങളുടെ യാത്രാ സഹായി. റൂട്ടുകൾ, സുരക്ഷ, കാലാവസ്ഥ എന്നിവയെക്കുറിച്ച് എന്നോട് ചോദിക്കാം!",
        "chat.placeholder": "AURA-യോട് ചോദിക്കുക...",
        "chat.send": "അയക്കുക 🚀",
        "chat.reset": "🗑️ ചാറ്റ് റീസെറ്റ് ചെയ്യുക",
        "chat.active_provider": "സജീവ AI",
        "chat.quick_categories": "💡 പ്രധാന ചോദ്യങ്ങൾ:",
        "chat.quick_fastest": "⚡ വേഗതയേറിയ വഴി",
        "chat.quick_compare": "🗺️ വഴികൾ താരതമ്യം ചെയ്യുക",
        "chat.quick_hazards": "🛡️ അപകട പരിശോധന",
        "chat.quick_weather": "🌤️ കാലാവസ്ഥ",
        "chat.quick_code": "💻 കോഡിംഗ് സഹായം",
        "chat.quick_story": "✍️ യാത്രാ കഥ",
        "chat.quick_food": "🍽️ അടുത്തുള്ള ഭക്ഷണം",
        "chat.quick_emergency": "🏥 അടിയന്തര സഹായം"
    },

    "bn": {
        # App / Header / Sidebar (Bengali)
        "app.title": "NexRoute",
        "app.subtitle": "ভবিষ্যদ্বাণীমূলক ট্রানজিট ও ঝুঁকিমুক্ত বুদ্ধিমান নেভিগেশন",
        "app.telemetry": "স্বয়ংক্রিয় বহুমুখী নিরাপত্তা পর্যবেক্ষণ",
        "app.language": "ভাষা নির্বাচন করুন",
        "app.distance_units": "দূরত্বের একক",
        "app.metric_km": "কিলোমিটার (km)",
        "app.imperial_mi": "মাইল (mi)",
        "app.active_standard": "বর্তমান মান",
        "app.hazards": "বিপদ",
        "app.closures": "রাস্তা বন্ধ",
        "app.traffic": "যানজট",
        "app.priority": "অগ্রাধিকার",
        "app.delays": "{count} বিলম্ব",
        "app.normal_flow": "স্বাভাবিক চলাচল",

        # Tabs
        "tab.copilot": "✨ AI ট্রাভেল কো-পাইলট",
        "tab.navigation": "🧭 মানচিত্র ও ন্যাভিগেশন",
        "tab.virtual_guide": "🚗 ভার্চুয়াল গাইড",
        "tab.facilities": "🏥 পরিষেবা",
        "tab.places": "🌟 দর্শনীয় স্থানসমূহ",

        # Navigation & Inputs
        "nav.navigation": "ন্যাভিগেশন",
        "nav.starting_point": "শুরু স্থান",
        "nav.destination": "গন্তব্য",
        "nav.search_location": "স্থান খুঁজুন",
        "nav.search_origin_placeholder": "শুরু স্থান বা জিপিএস অবস্থান খুঁজুন...",
        "nav.search_dest_placeholder": "গন্তব্য স্থান খুঁজুন...",
        "nav.get_directions": "দিকনির্দেশ পান",
        "nav.find_best_route": "সেরা পথ খুঁজুন",
        "nav.swap_locations": "স্থান অদলবদল করুন",
        "nav.my_location": "আমার বর্তমান অবস্থান",
        "nav.route_found": "পথ পাওয়া গেছে",
        "nav.gps_unavailable": "GPS অনুপলব্ধ",
        "nav.gps_tracking_live": "লাইভ GPS সক্রিয় আছে",
        "nav.rerouting": "পুনঃপথ তৈরি হচ্ছে...",
        "nav.avoid_tolls": "টোল এড়িয়ে চলুন",
        "nav.avoid_highways": "হাইওয়ে এড়িয়ে চলুন",
        "nav.avoid_ferries": "ফেরি এড়িয়ে চলুন",
        "nav.objectives_title": "রুটের উদ্দেশ্য",
        "nav.all_routes": "🌐 সব পথ (ডিফল্ট)",
        "nav.all_routes_desc": "উপলব্ধ সব বিকল্প পথ একসাথে দেখায়",
        "nav.fastest": "⚡ দ্রুততম পথ",
        "nav.fastest_desc": "যাত্রার সময় এবং যানজট কমায়",
        "nav.shortest": "📏 সবচেয়ে ছোট পথ",
        "nav.shortest_desc": "দূরত্ব কমায়",
        "nav.balanced": "⚖️ ভারসাম্যপূর্ণ পথ",
        "nav.balanced_desc": "সময় ও দূরত্বের সঠিক ভারসাম্য",
        "nav.accessible": "♿ বাধারহিত পথ",
        "nav.accessible_desc": "সিঁড়িবিহীন হুইলচেয়ার বান্ধব নিরাপদ পথ",
        "nav.active_strategy": "সক্রিয় কৌশল",
        "nav.ai_preference": "এআই পছন্দ",
        "nav.speed_weight": "গতি অপ্টিমাইজেশন ওজন",
        "nav.distance_weight": "দূরত্ব সংকোচন ওজন",
        "nav.barrier_strictness": "বাধা পরিহারের কড়াকড়ি",
        "nav.disambiguation_title": "সঠিক স্থানটি বেছে নিন",
        "nav.distance": "দূরত্ব",
        "nav.duration": "সময়",
        "nav.eta": "পৌঁছানোর সময়",
        "nav.direct_route": "সরাসরি করিডোর",

        # Fleet & Modes
        "fleet.title": "যানবাহন ও গতি মোড",
        "fleet.driving": "গাড়ি / ড্রাইভিং",
        "fleet.bike": "বাইক / মোটরসাইকেল",
        "fleet.walking": "হাঁটা / পথচারী",
        "fleet.bicycle": "সাইকেল",
        "fleet.truck": "ট্রাক / পরিবহন",
        "fleet.tractor": "ট্র্যাক্টর / কৃষি",
        "fleet.speed_mode": "গতি মোড",
        "fleet.normal": "স্বাভাবিক গতি",
        "fleet.rush": "দ্রুত এক্সপ্রেস",
        "fleet.eco": "পরিবেশ বান্ধব",

        # Virtual Guide & Companion
        "guide.title": "ভার্চুয়াল গাইড ড্যাশবোর্ড",
        "guide.section1_title": "সরাসরি যাত্রার অগ্রগতি",
        "guide.section2_title": "ভার্চুয়াল গাড়ির সঙ্গী",
        "guide.section3_title": "ধাপে ধাপে দিকনির্দেশনা",
        "guide.section4_title": "3D হাঁটার দৃশ্য",
        "guide.move_parallel": "একসাথে এগিয়ে যান",
        "guide.traffic_stop": "যানজটের জন্য থামুন",
        "guide.resume": "যাত্রা পুনরায় চালু করুন",
        "guide.reset": "রিসেট করুন",
        "guide.status": "যাত্রার অবস্থা",
        "guide.status_stationary": "প্রস্তুত (থেমে আছে)",
        "guide.status_in_transit": "চলমান • এগিয়ে যাচ্ছেন",
        "guide.status_paused": "স্থগিত (যানজট/বিপদ)",
        "guide.status_arrived": "গন্তব্যে পৌঁছে গেছেন",
        "guide.speed": "বর্তমান গতি",
        "guide.remaining_dist": "বাকি দূরত্ব",
        "guide.remaining_time": "বাকি সময়",
        "guide.checkpoint": "চেকপয়েন্ট {current} / {total}",
        "guide.arrived": "আপনি আপনার গন্তব্যে পৌঁছে গেছেন!",
        "guide.hazard_alert": "সতর্কতা: সামনে বিপদের ঝুঁকি রয়েছে। গতি কমান।",

        # Maneuvers
        "maneuver.start": "{origin} থেকে {road}-এর দিকে যান",
        "maneuver.turn_left": "{road}-এ বাঁয়ে ঘুরুন",
        "maneuver.turn_right": "{road}-এ ডানে ঘুরুন",
        "maneuver.straight": "{road}-এ সোজা চলতে থাকুন",
        "maneuver.keep_left": "{road}-এ বাঁ দিক ধরে রাখুন",
        "maneuver.keep_right": "{road}-এ ডান দিক ধরে রাখুন",
        "maneuver.take_exit": "{road}-এর দিকে প্রস্থান নিন",
        "maneuver.u_turn": "{road}-এ ইউ-টার্ন নিন",
        "maneuver.roundabout": "গোলচত্বরে প্রবেশ করে {exit}তম প্রস্থান নিয়ে {road}-এ যান",
        "maneuver.arrive": "{destination}-এ নিরাপদে পৌঁছেছেন",
        "maneuver.follow_route": "{road} দিয়ে নির্বাচিত পথ অনুসরণ করুন",

        # Voice Guidance
        "voice.title": "ভয়েস নির্দেশিকা",
        "voice.enabled": "ভয়েস নির্দেশিকা সক্রিয়",
        "voice.disabled": "ভয়েস নির্দেশিকা বন্ধ",
        "voice.toggle": "ভয়েস অন/অফ করুন",
        "voice.speed": "ভয়েসের গতি",
        "voice.speed_normal": "1.0x স্বাভাবিক",
        "voice.speed_slow": "0.8x ধীর ও স্পষ্ট",
        "voice.speed_fast": "1.2x দ্রুত",
        "voice.unsupported": "{lang} ভাষার ভয়েস ব্রাউজারে উপলব্ধ নেই। পাঠ্য নির্দেশিকা সক্রিয় থাকবে।",
        "voice.speaking": "নির্দেশ বলা হচ্ছে...",

        # Facilities
        "fac.title": "কাছাকাছি পরিষেবা",
        "fac.subtitle": "জরুরি সেবা, জ্বালানি, হাসপাতাল ও বিশ্রামাগার",
        "fac.all": "🌐 সব পরিষেবা",
        "fac.hospitals": "🏥 হাসপাতাল ও জরুরি পরিষেবা",
        "fac.fuel": "⛽ জ্বালানি ও ইভি চার্জিং",
        "fac.police": "👮 পুলিশ স্টেশন",
        "fac.pharmacies": "💊 ফার্মেসি",
        "fac.food": "🍽️ খাবার ও রেস্তোরাঁ",
        "fac.atm": "🏧 এটিএম ও ব্যাংক",
        "fac.restrooms": "🚻 পাবলিক বিশ্রামাগার",
        "fac.focus_map": "ম্যাপে দেখুন",
        "fac.route_here": "এখানে পথ দেখান",
        "fac.distance_km": "{dist} কিমি দূরে",
        "fac.none_found": "এই এলাকায় কোনো পরিষেবা পাওয়া যায়নি।",

        # Places
        "places.title": "গন্তব্যের কাছাকাছি দর্শনীয় স্থান",
        "places.subtitle": "{destination}-এর কাছাকাছি জনপ্রিয় স্থান ও রেস্তোরাঁ",
        "places.no_rating": "রেটিং অনুপলব্ধ",
        "places.reviews": "{count} গুগল পর্যালোচনা",
        "places.focus_map": "ম্যাপে দেখুন",
        "places.route_here": "এখানে পথ দেখান",

        # Road Intelligence & Hazards
        "hazard.title": "AI সড়ক নিরাপত্তা বিশ্লেষণ",
        "hazard.all_clear": "🛡️ তল্লাশি করা অঞ্চলে কোনো বিপদ পাওয়া যায়নি",
        "hazard.warning": "⚠️ সামনে বিপদের সতর্কতা",
        "hazard.satellite": "এআই স্যাটেলাইট রোড বিশ্লেষণ",
        "hazard.inspection": "বিপদ পর্যবেক্ষণ",
        "hazard.route_status": "রুটের অবস্থা",
        "hazard.checked": "যাচাইকৃত ও নিরাপদ",

        # Chatbot (A.U.R.A.)
        "chat.title": "A.U.R.A. ন্যাভিগেশন কো-পাইলট",
        "chat.subtitle": "বুদ্ধিমান এআই কথোপকথন সহকারী",
        "chat.welcome": "👋 নমস্কার! আমি A.U.R.A., NexRoute-এ আপনার ভ্রমণ সঙ্গী। রুট, নিরাপত্তা বা সাধারণ তথ্যের জন্য আমাকে জিজ্ঞাসা করুন!",
        "chat.placeholder": "AURA-কে জিজ্ঞাসা করুন...",
        "chat.send": "পাঠান 🚀",
        "chat.reset": "🗑️ চ্যাট রিসেট করুন",
        "chat.active_provider": "সক্রিয় এআই",
        "chat.quick_categories": "💡 দ্রুত প্রশ্নসমূহ:",
        "chat.quick_fastest": "⚡ দ্রুততম পথ",
        "chat.quick_compare": "🗺️ পথের তুলনা",
        "chat.quick_hazards": "🛡️ বিপদ পরীক্ষা",
        "chat.quick_weather": "🌤️ আবহাওয়া",
        "chat.quick_code": "💻 কোডিং সাহায্য",
        "chat.quick_story": "✍️ ভ্রমণের গল্প",
        "chat.quick_food": "🍽️ কাছাকাছি খাবার",
        "chat.quick_emergency": "🏥 জরুরি সাহায্য"
    },

    "mr": {
        # App / Header / Sidebar (Marathi)
        "app.title": "NexRoute",
        "app.subtitle": "पूर्वानुमानित अनुकूलनीय वाहतूक व अडथळामुक्त बुद्धिमान नेव्हिगेशन",
        "app.telemetry": "स्वायत्त बहु-मार्गिका सुरक्षा टेलिमेट्री",
        "app.language": "भाषा निवडा",
        "app.distance_units": "अंतराचे एकक",
        "app.metric_km": "किलोमीटर (km)",
        "app.imperial_mi": "मैल (mi)",
        "app.active_standard": "सक्रिय प्रमाण",
        "app.hazards": "धोके",
        "app.closures": "रस्ते बंद",
        "app.traffic": "वाहतूक",
        "app.priority": "प्राधान्यता",
        "app.delays": "{count} विलंब",
        "app.normal_flow": "सुरळीत वाहतूक",

        # Tabs
        "tab.copilot": "✨ AI ट्रॅव्हल सह-वैमानिक",
        "tab.navigation": "🧭 नकाशा आणि नेव्हिगेशन",
        "tab.virtual_guide": "🚗 व्हर्च्युअल मार्गदर्शक",
        "tab.facilities": "🏥 सुविधा",
        "tab.places": "🌟 प्रेक्षणीय स्थळे",

        # Navigation & Inputs
        "nav.navigation": "नेव्हिगेशन",
        "nav.starting_point": "प्रारंभ स्थान",
        "nav.destination": "गंतव्य स्थान",
        "nav.search_location": "ठिकाण शोधा",
        "nav.search_origin_placeholder": "प्रारंभ स्थान किंवा GPS स्थान शोधा...",
        "nav.search_dest_placeholder": "गंतव्य स्थान शोधा...",
        "nav.get_directions": "दिशा मिळवा",
        "nav.find_best_route": "सर्वोत्तम मार्ग शोधा",
        "nav.swap_locations": "ठिकाणे बदला",
        "nav.my_location": "माझे चालू स्थान",
        "nav.route_found": "मार्ग सापडला",
        "nav.gps_unavailable": "GPS उपलब्ध नाही",
        "nav.gps_tracking_live": "थेट GPS सक्रिय आहे",
        "nav.rerouting": "पुन्हा मार्ग बदलत आहे...",
        "nav.avoid_tolls": "टोल टाळा",
        "nav.avoid_highways": "महामार्ग टाळा",
        "nav.avoid_ferries": "फेरी टाळा",
        "nav.objectives_title": "मार्गाचे प्राधान्य",
        "nav.all_routes": "🌐 सर्व मार्ग (डिफॉल्ट)",
        "nav.all_routes_desc": "सर्व उपलब्ध पर्यायी मार्ग एकाच वेळी दाखवतो",
        "nav.fastest": "⚡ सर्वात वेगवान मार्ग",
        "nav.fastest_desc": "प्रवासाची वेळ आणि वाहतूक कोंडी कमी करतो",
        "nav.shortest": "📏 सर्वात कमी अंतर",
        "nav.shortest_desc": "भौतिक अंतर कमी करतो",
        "nav.balanced": "⚖️ संतुलित मार्ग",
        "nav.balanced_desc": "वेळ आणि अंतराचा योग्य समतोल",
        "nav.accessible": "♿ अडथळामुक्त मार्ग",
        "nav.accessible_desc": "पायऱ्या नसलेले सुरक्षित व्हीलचेअर मार्ग",
        "nav.active_strategy": "सक्रिय रणनीती",
        "nav.ai_preference": "AI प्राधान्य",
        "nav.speed_weight": "वेग अनुकूलन वजन",
        "nav.distance_weight": "अंतर संकुचन वजन",
        "nav.barrier_strictness": "अडथळा निवारण अचूकता",
        "nav.disambiguation_title": "योग्य ठिकाण निवडा",
        "nav.distance": "अंतर",
        "nav.duration": "वेळ",
        "nav.eta": "पोहोचण्याची वेळ",
        "nav.direct_route": "थेट कॉरिडॉर",

        # Fleet & Modes
        "fleet.title": "वाहन आणि वेग मोड",
        "fleet.driving": "कार / ड्रायव्हिंग",
        "fleet.bike": "बाईक / मोटरसायकल",
        "fleet.walking": "चालणे / पादचारी",
        "fleet.bicycle": "सायकल",
        "fleet.truck": "ट्रक / मालवाहतूक",
        "fleet.tractor": "ट्रॅक्टर / शेती",
        "fleet.speed_mode": "वेग मोड",
        "fleet.normal": "सामान्य वेग",
        "fleet.rush": "जलद गती",
        "fleet.eco": "पर्यावरणपूरक",

        # Virtual Guide & Companion
        "guide.title": "व्हर्च्युअल गाईड डॅशबोर्ड",
        "guide.section1_title": "थेट प्रवास प्रगती",
        "guide.section2_title": "व्हर्च्युअल वाहन सोबती",
        "guide.section3_title": "वळणावळणाचे मार्गदर्शन",
        "guide.section4_title": "3D चालण्याचे दृश्य",
        "guide.move_parallel": "समांतर हालचाल सुरू करा",
        "guide.traffic_stop": "वाहतूक थांबा",
        "guide.resume": "प्रवास सुरू ठेवा",
        "guide.reset": "पुन्हा सुरू करा",
        "guide.status": "प्रवासाची स्थिती",
        "guide.status_stationary": "तयार / स्थिर",
        "guide.status_in_transit": "प्रवासात आहे",
        "guide.status_paused": "थांबवले (वाहतूक/धोका)",
        "guide.status_arrived": "गंतव्यस्थानी पोहोचले",
        "guide.speed": "सध्याचा वेग",
        "guide.remaining_dist": "उर्वरित अंतर",
        "guide.remaining_time": "उर्वरित वेळ",
        "guide.checkpoint": "चेकपॉइंट {current} / {total}",
        "guide.arrived": "तुम्ही तुमच्या गंतव्यस्थानी पोहोचला आहात!",
        "guide.hazard_alert": "सावधान: पुढे धोका आढळला आहे. वेग कमी करा.",

        # Maneuvers
        "maneuver.start": "{origin} वरून {road} कडे प्रवास सुरू करा",
        "maneuver.turn_left": "{road} वर डावीकडे वळा",
        "maneuver.turn_right": "{road} वर उजवीकडे वळा",
        "maneuver.straight": "{road} वर सरळ पुढे जात राहा",
        "maneuver.keep_left": "{road} वर डाव्या बाजूने चला",
        "maneuver.keep_right": "{road} वर उजव्या बाजूने चला",
        "maneuver.take_exit": "{road} कडे एक्झिट घ्या",
        "maneuver.u_turn": "{road} वर यू-टर्न घ्या",
        "maneuver.roundabout": "गोलचक्करमध्ये जाऊन {exit}वी एक्झिट घेऊन {road} वर जा",
        "maneuver.arrive": "{destination} येथे सुरक्षित पोहोचलात",
        "maneuver.follow_route": "{road} वरून निवडलेल्या मार्गाचे अनुसरण करा",

        # Voice Guidance
        "voice.title": "आवाज मार्गदर्शन",
        "voice.enabled": "आवाज मार्गदर्शन सुरू आहे",
        "voice.disabled": "आवाज मार्गदर्शन बंद",
        "voice.toggle": "आवाज चालू/बंद करा",
        "voice.speed": "आवाजाचा वेग",
        "voice.speed_normal": "1.0x सामान्य",
        "voice.speed_slow": "0.8x हळू आणि स्पष्ट",
        "voice.speed_fast": "1.2x जलद",
        "voice.unsupported": "{lang} भाषेसाठी ब्राऊझरमध्ये आवाज उपलब्ध नाही. मजकूर सूचना सुरू राहतील.",
        "voice.speaking": "सूचना बोलली जात आहे...",

        # Facilities
        "fac.title": "जवळील सुविधा",
        "fac.subtitle": "आपत्कालीन सेवा, इंधन, रुग्णालये व विश्रामगृहे",
        "fac.all": "🌐 सर्व सुविधा",
        "fac.hospitals": "🏥 रुग्णालये व आपत्कालीन",
        "fac.fuel": "⛽ इंधन व ईव्ही चार्जिंग",
        "fac.police": "👮 पोलीस ठाणे",
        "fac.pharmacies": "💊 औषध दुकाने",
        "fac.food": "🍽️ उपहारगृहे व हॉटेल्स",
        "fac.atm": "🏧 एटीएम व बँका",
        "fac.restrooms": "🚻 सार्वजनिक स्वच्छतागृहे",
        "fac.focus_map": "नकाशावर पहा",
        "fac.route_here": "येथे मार्ग काढा",
        "fac.distance_km": "{dist} किमी अंतरावर",
        "fac.none_found": "या परिसरात कोणतीही सुविधा आढळली नाही.",

        # Places
        "places.title": "गंतव्यस्थानाजवळील शिफारस केलेली ठिकाणे",
        "places.subtitle": "{destination} जवळील लोकप्रिय आकर्षणे व खाद्यपदार्थ",
        "places.no_rating": "रेटिंग उपलब्ध नाही",
        "places.reviews": "{count} खरी गुगल पुनरावलोकने",
        "places.focus_map": "नकाशावर पहा",
        "places.route_here": "येथे मार्ग काढा",

        # Road Intelligence & Hazards
        "hazard.title": "AI रस्ता सुरक्षा विश्लेषण",
        "hazard.all_clear": "🛡️ तपासलेल्या भागात कोणताही धोका आढळला नाही",
        "hazard.warning": "⚠️ पुढे धोका / रस्त्यात अडथळा",
        "hazard.satellite": "एआय उपग्रह रस्ता बुद्धिमत्ता",
        "hazard.inspection": "धोका तपासणी",
        "hazard.route_status": "मार्गाची स्थिती",
        "hazard.checked": "सुरक्षित आणि सत्यापित",

        # Chatbot (A.U.R.A.)
        "chat.title": "A.U.R.A. नेव्हिगेशन सह-पायलट",
        "chat.subtitle": "बुद्धिमान एआय संभाषण सहाय्यक",
        "chat.welcome": "👋 नमस्कार! मी A.U.R.A., NexRoute मध्ये तुमचा प्रवास साथी. मार्ग, सुरक्षा किंवा माहितीसाठी मला विचारा!",
        "chat.placeholder": "AURA ला विचारा...",
        "chat.send": "पाठवा 🚀",
        "chat.reset": "🗑️ चॅट रीसेट करा",
        "chat.active_provider": "सक्रिय एआय मॉडेल",
        "chat.quick_categories": "💡 महत्त्वाचे प्रश्न:",
        "chat.quick_fastest": "⚡ सर्वात वेगवान मार्ग",
        "chat.quick_compare": "🗺️ मार्गांची तुलना",
        "chat.quick_hazards": "🛡️ धोके तपासा",
        "chat.quick_weather": "🌤️ हवामान",
        "chat.quick_code": "💻 कोडिंग मदत",
        "chat.quick_story": "✍️ प्रवास कथा",
        "chat.quick_food": "🍽️ जवळील जेवण",
        "chat.quick_emergency": "🏥 आपत्कालीन मदत"
    }
}


def get_current_language() -> str:
    """Returns the current language code from Streamlit session_state or default."""
    try:
        import streamlit as st
        if "app_language" in st.session_state and st.session_state.app_language in SUPPORTED_LANGUAGES:
            return st.session_state.app_language
    except Exception:
        pass
    return DEFAULT_LANGUAGE


def set_current_language(lang_code: str) -> None:
    """Sets the current language in Streamlit session_state."""
    if lang_code in SUPPORTED_LANGUAGES:
        try:
            import streamlit as st
            st.session_state.app_language = lang_code
        except Exception:
            pass


def get_bcp47_code(lang_code: Optional[str] = None) -> str:
    """Returns the BCP-47 speech synthesis code for Web Speech API."""
    c = lang_code or get_current_language()
    info = SUPPORTED_LANGUAGES.get(c, SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE])
    return info.get("bcp47", "en-IN")


def get_language_native_name(lang_code: Optional[str] = None) -> str:
    """Returns the native name of the language (e.g. తెలుగు for te)."""
    c = lang_code or get_current_language()
    info = SUPPORTED_LANGUAGES.get(c, SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE])
    return info.get("native", "English")


def t(key: str, *args, default: Optional[str] = None, lang: Optional[str] = None, **kwargs) -> str:
    """
    Main translation lookup function.
    - Resolves language (explicit via positional arg, kwarg 'lang', or session state).
    - Supports default fallback string (positional arg, kwarg 'default', or kwarg 'fallback').
    - Highly resilient: safely accepts any permutation of (key, default, lang) or (key, lang, default).
    - Looks up key in language table with fallback chain to English, default string, or title-cased key.
    - Safely interpolates kwargs placeholders e.g. {count}, {street}, {dist}.
    - Always returns a string, never raises TypeError or returns None.
    """
    fallback_val = default if default is not None else kwargs.get("fallback")
    actual_lang = lang

    # Parse variable positional arguments safely
    if args:
        if len(args) == 1:
            a0 = args[0]
            if isinstance(a0, str) and a0 in SUPPORTED_LANGUAGES and actual_lang is None:
                actual_lang = a0
            elif fallback_val is None and a0 is not None:
                fallback_val = str(a0)
        elif len(args) >= 2:
            a0, a1 = args[0], args[1]
            if isinstance(a0, str) and a0 in SUPPORTED_LANGUAGES:
                if actual_lang is None:
                    actual_lang = a0
                if fallback_val is None and a1 is not None:
                    fallback_val = str(a1)
            else:
                if fallback_val is None and a0 is not None:
                    fallback_val = str(a0)
                if actual_lang is None and isinstance(a1, str) and a1 in SUPPORTED_LANGUAGES:
                    actual_lang = a1

    target_lang = actual_lang or get_current_language()
    if target_lang not in SUPPORTED_LANGUAGES:
        target_lang = DEFAULT_LANGUAGE

    # Look up in target language
    lang_dict = TRANSLATIONS.get(target_lang, {})
    template = lang_dict.get(key)

    if template is None:
        try:
            _load_locale_overrides()
            lang_dict = TRANSLATIONS.get(target_lang, {})
            template = lang_dict.get(key)
        except Exception:
            pass

    # Fallback to English
    if template is None:
        template = TRANSLATIONS.get(DEFAULT_LANGUAGE, {}).get(key)

    # Fallback to caller-provided default or humanized key
    if template is None:
        template = fallback_val if fallback_val is not None else key.split(".")[-1].replace("_", " ").title()

    if template is None:
        template = str(key)

    template = str(template)

    # Interpolate
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            # Safe replacement if format throws KeyError on extra braces
            res = template
            for k, v in kwargs.items():
                if k not in ("default", "fallback"):
                    res = res.replace("{" + str(k) + "}", str(v))
            return res

    return template


def get_supported_languages() -> Dict[str, Dict[str, str]]:
    """Returns the dictionary of all supported languages and their metadata."""
    return SUPPORTED_LANGUAGES


def format_distance(dist_km: float, unit: str = "km", lang: Optional[str] = None) -> str:
    """Formats distance with localized numerals/units."""
    # Gracefully handle caller swapping unit and lang
    if unit in SUPPORTED_LANGUAGES and (lang is None or lang not in SUPPORTED_LANGUAGES):
        actual_lang = unit
        actual_unit = lang or "km"
    else:
        actual_lang = lang or get_current_language()
        actual_unit = unit or "km"

    if str(actual_unit).lower() in ("miles", "mi", "mile"):
        val = round(dist_km * 0.621371, 1)
        unit_str = "mi" if actual_lang == "en" else t("app.imperial_mi", lang=actual_lang)
    else:
        val = round(dist_km, 1)
        unit_str = "km" if actual_lang == "en" else "కి.మీ" if actual_lang == "te" else "किमी" if actual_lang in ("hi", "mr") else "கி.மீ" if actual_lang == "ta" else "ಕಿ.ಮೀ" if actual_lang == "kn" else "കി.മീ" if actual_lang == "ml" else "কিমি" if actual_lang == "bn" else "km"
    return f"{val} {unit_str}"


def format_duration(duration_min: float, lang: Optional[str] = None) -> str:
    """Formats travel duration in natural localized terms."""
    curr_lang = lang or get_current_language()
    mins = max(1, int(round(duration_min)))
    if mins < 60:
        if curr_lang == "te":
            return f"{mins} నిమిషాలు"
        elif curr_lang in ("hi", "mr"):
            return f"{mins} मिनट"
        elif curr_lang == "ta":
            return f"{mins} நிமிடங்கள்"
        elif curr_lang == "kn":
            return f"{mins} ನಿಮಿಷಗಳು"
        elif curr_lang == "ml":
            return f"{mins} മിനിറ്റ്"
        elif curr_lang == "bn":
            return f"{mins} মিনিট"
        return f"{mins} min" if mins == 1 else f"{mins} mins"
    
    hrs = mins // 60
    rem = mins % 60
    if curr_lang == "te":
        return f"{hrs} గంటల {rem} నిమిషాలు" if rem else f"{hrs} గంటలు"
    elif curr_lang in ("hi", "mr"):
        return f"{hrs} घंटे {rem} मिनट" if rem else f"{hrs} घंटे"
    elif curr_lang == "ta":
        return f"{hrs} மணி {rem} நிமிடங்கள்" if rem else f"{hrs} மணி"
    elif curr_lang == "kn":
        return f"{hrs} ಗಂಟೆ {rem} ನಿಮಿಷಗಳು" if rem else f"{hrs} ಗಂಟೆ"
    elif curr_lang == "ml":
        return f"{hrs} മണിക്കൂർ {rem} മിനിറ്റ്" if rem else f"{hrs} മണിക്കൂർ"
    elif curr_lang == "bn":
        return f"{hrs} ঘণ্টা {rem} মিনিট" if rem else f"{hrs} ঘণ্টা"
    return f"{hrs} hr {rem} min" if rem else f"{hrs} hr"


# Auto-load locale JSON overrides if present

# Enrich built-in TRANSLATIONS with core multilingual keys
for _l_code, _entries in {'en': {'nav.route_corridor': 'Route Corridor', 'nav.active_path': 'Active Path', 'nav.route_endpoints': 'Route Endpoints', 'nav.live_map_hud': 'Live Map HUD', 'nav.distance': 'Distance', 'nav.est_time': 'Est. Time', 'nav.mode': 'Mode', 'nav.fit_route': 'Fit Route', 'nav.tour': '🚀 Tour', 'nav.all_routes_desc': 'Predictive Adaptive Navigation & Live Corridor Routing', 'tab.selected_place': '📍 Selected Place / Marker', 'tab.route_details': 'ℹ️ Route Details', 'aura.chip_route': '🗺️ Route', 'aura.chip_places': '📍 Places', 'aura.chip_plan': '✈️ Plan', 'aura.chip_cost': '⛽ Cost', 'aura.chip_stays': '🏨 Stays', 'aura.chip_ask': '💬 Ask', 'aura.chip_clear': '🗑️ Clear', 'aura.welcome_badge': '🤖 AURA READY', 'aura.welcome_msg': "👋 <b>Hi! I'm Aura</b>, your intelligent AI travel assistant for <b>NexRoute</b>.<br><br>I can help you plan trips, find optimal routes, discover nearby places & halfway stops, estimate fuel and tolls, and answer any travel or everyday questions.<br><br>Where would you like to explore today?", 'places.header_sub': 'Discover useful places near your location or along your selected route.', 'copilot.header_sub': 'Autonomous Trip Planning & Itinerary Studio'}, 'te': {'nav.route_corridor': 'మార్గ కారిడార్', 'nav.active_path': 'క్రియాశీల మార్గం', 'nav.route_endpoints': 'మార్గం చివరలు', 'nav.live_map_hud': 'లైవ్ మ్యాప్ HUD', 'nav.distance': 'దూరం', 'nav.est_time': 'అంచనా సమయం', 'nav.mode': 'ప్రయాణ విధానం', 'nav.fit_route': 'మ్యాప్\u200cలో చూపించు', 'nav.tour': '🚀 టూర్', 'nav.all_routes_desc': 'ప్రిడిక్టివ్ అడాప్టివ్ నావిగేషన్ మరియు లైవ్ కారిడార్ రూటింగ్', 'tab.selected_place': '📍 ఎంచుకున్న ప్రదేశం', 'tab.route_details': 'ℹ️ మార్గం వివరాలు', 'aura.chip_route': '🗺️ మార్గం', 'aura.chip_places': '📍 స్థలాలు', 'aura.chip_plan': '✈️ ప్రణాళిక', 'aura.chip_cost': '⛽ ఖర్చు', 'aura.chip_stays': '🏨 బస', 'aura.chip_ask': '💬 అడగండి', 'aura.chip_clear': '🗑️ క్లియర్', 'aura.welcome_badge': '🤖 AURA సిద్ధంగా ఉంది', 'aura.welcome_msg': '👋 <b>నమస్కారం! నేను ఔరా</b>, <b>NexRoute</b> యొక్క మీ తెలివైన AI ప్రయాణ సహాయకురాలిని.<br><br>నేను మీకు ప్రయాణ ప్రణాళికలు, సరైన మార్గాలు, సమీపంలోని దర్శనీయ ప్రదేశాలు, ఇంధన అంచనా మరియు అన్ని ప్రయాణ సందేహాలను నివృత్తి చేయడంలో సహాయపడతాను.<br><br>ఈరోజు మీరు ఎక్కడికి ప్రయాణించాలనుకుంటున్నారు?', 'places.header_sub': 'మీ ప్రస్తుత స్థానం లేదా ఎంచుకున్న మార్గంలో ఉపయోగకరమైన ప్రదేశాలను అన్వేషించండి.', 'copilot.header_sub': 'స్వయంప్రతిపత్త ట్రిప్ ప్లానింగ్ & ప్రయాణ ప్రణాళిక స్టూడియో'}, 'hi': {'nav.route_corridor': 'रूट कॉरिडोर', 'nav.active_path': 'सक्रिय मार्ग', 'nav.route_endpoints': 'मार्ग के छोर', 'nav.live_map_hud': 'लाइव मैप HUD', 'nav.distance': 'दूरी', 'nav.est_time': 'अनुमानित समय', 'nav.mode': 'यात्रा साधन', 'nav.fit_route': 'मार्ग फिट करें', 'nav.tour': '🚀 टूर', 'nav.all_routes_desc': 'सटीक अनुकूलनीय नेविगेशन एवं लाइव कॉरिडोर रूटिंग', 'tab.selected_place': '📍 चयनित स्थान', 'tab.route_details': 'ℹ️ मार्ग विवरण', 'aura.chip_route': '🗺️ मार्ग', 'aura.chip_places': '📍 स्थान', 'aura.chip_plan': '✈️ योजना', 'aura.chip_cost': '⛽ लागत', 'aura.chip_stays': '🏨 आवास', 'aura.chip_ask': '💬 पूछें', 'aura.chip_clear': '🗑️ साफ़ करें', 'aura.welcome_badge': '🤖 AURA तैयार है', 'aura.welcome_msg': '👋 <b>नमस्ते! मैं ऑरा हूँ</b>, <b>NexRoute</b> के लिए आपकी बुद्धिमान AI यात्रा सहायक।<br><br>मैं आपको यात्रा योजना बनाने, सर्वोत्तम मार्ग खोजने, आस-पास के स्थानों की खोज करने, ईंधन और टोल का अनुमान लगाने और यात्रा संबंधी किसी भी प्रश्न का उत्तर देने में मदद कर सकती हूँ।<br><br>आज आप कहाँ घूमना चाहेंगे?', 'places.header_sub': 'अपने स्थान के पास या अपने चयनित मार्ग पर उपयोगी स्थानों की खोज करें।', 'copilot.header_sub': 'स्वायत्त यात्रा योजना और यात्रा कार्यक्रम स्टूडियो'}, 'ta': {'nav.route_corridor': 'பயணப் பாதை', 'nav.active_path': 'செயலில் உள்ள பாதை', 'nav.route_endpoints': 'பாதை முனைகள்', 'nav.live_map_hud': 'நேரலை வரைபட HUD', 'nav.distance': 'தூரம்', 'nav.est_time': 'மதிப்பிடப்பட்ட நேரம்', 'nav.mode': 'பயண முறை', 'nav.fit_route': 'பாதையை காட்டு', 'nav.tour': '🚀 சுற்றுலா', 'nav.all_routes_desc': 'முன்கணிப்பு தகவமைப்பு வழிசெலுத்தல் மற்றும் நேரலை பாதை வழிகாட்டல்', 'tab.selected_place': '📍 தேர்ந்தெடுக்கப்பட்ட இடம்', 'tab.route_details': 'ℹ️ பாதை விவரங்கள்', 'aura.chip_route': '🗺️ வழி', 'aura.chip_places': '📍 இடங்கள்', 'aura.chip_plan': '✈️ திட்டம்', 'aura.chip_cost': '⛽ செலவு', 'aura.chip_stays': '🏨 தங்குமிடம்', 'aura.chip_ask': '💬 கேளுங்கள்', 'aura.chip_clear': '🗑️ அழி', 'aura.welcome_badge': '🤖 AURA தயார்', 'aura.welcome_msg': '👋 <b>வணக்கம்! நான் ஆரா</b>, <b>NexRoute</b> இன் உங்கள் அறிவார்ந்த AI பயண உதவியாளர்.<br><br>பயணத் திட்டமிடல், சிறந்த வழிகள், அருகிலுள்ள இடங்கள், எரிபொருள் மதிப்பீடு மற்றும் அனைத்துப் பயணக் கேள்விகளுக்கும் உதவ நான் தயாராக உள்ளேன்.<br><br>இன்று நீங்கள் எங்கு செல்ல விரும்புகிறீர்கள்?', 'places.header_sub': 'உங்கள் இருப்பிடத்திற்கு அருகில் அல்லது தேர்ந்தெடுக்கப்பட்ட பாதையில் உள்ள இடங்களைக் கண்டறியவும்.', 'copilot.header_sub': 'தானியங்கி பயணத் திட்டமிடல் மற்றும் பயண அட்டவணை அரங்கம்'}, 'kn': {'nav.route_corridor': 'ಮಾರ್ಗ ಕಾರಿಡಾರ್', 'nav.active_path': 'ಸಕ್ರಿಯ ಮಾರ್ಗ', 'nav.route_endpoints': 'ಮಾರ್ಗದ ತುದಿಗಳು', 'nav.live_map_hud': 'ಲೈವ್ ಮ್ಯಾಪ್ HUD', 'nav.distance': 'ದೂರ', 'nav.est_time': 'ಅಂದಾಜು ಸಮಯ', 'nav.mode': 'ಪ್ರಯಾಣ ಮಾದರಿ', 'nav.fit_route': 'ಮಾರ್ಗ ಹೊಂದಿಸಿ', 'nav.tour': '🚀 ಪ್ರವಾಸ', 'nav.all_routes_desc': 'ಹೊಂದಾಣಿಕೆಯ ಸಂಚರಣೆ ಮತ್ತು ನೇರ ಕಾರಿಡಾರ್ ಮಾರ್ಗ ರಚನೆ', 'tab.selected_place': '📍 ಆಯ್ಕೆಮಾಡಿದ ಸ್ಥಳ', 'tab.route_details': 'ℹ️ ಮಾರ್ಗದ ವಿವರಗಳು', 'aura.chip_route': '🗺️ ಮಾರ್ಗ', 'aura.chip_places': '📍 ಸ್ಥಳಗಳು', 'aura.chip_plan': '✈️ ಯೋಜನೆ', 'aura.chip_cost': '⛽ ವೆಚ್ಚ', 'aura.chip_stays': '🏨 ವಸತಿ', 'aura.chip_ask': '💬 ಕೇಳಿ', 'aura.chip_clear': '🗑️ ತೆರವುಗೊಳಿಸಿ', 'aura.welcome_badge': '🤖 AURA ಸಿದ್ಧವಾಗಿದೆ', 'aura.welcome_msg': '👋 <b>ನಮಸ್ಕಾರ! ನಾನು ಔರಾ</b>, <b>NexRoute</b> ಗಾಗಿ ನಿಮ್ಮ ಬುದ್ಧಿವಂತ AI ಪ್ರಯಾಣ ಸಹಾಯಕ.<br><br>ಪ್ರಯಾಣ ಯೋಜನೆ, ಸೂಕ್ತ ಮಾರ್ಗಗಳು, ಹತ್ತಿರದ ಸ್ಥಳಗಳು ಮತ್ತು ಇಂಧನ ವೆಚ್ಚದ ಅಂದಾಜಿನಲ್ಲಿ ನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ.<br><br>ಇಂದು ನೀವು ಎಲ್ಲಿಗೆ ಪ್ರಯಾಣಿಸಲು ಬಯಸುತ್ತೀರಿ?', 'places.header_sub': 'ನಿಮ್ಮ ಸ್ಥಳದ ಸಮೀಪ ಅಥವಾ ನೀವು ಆಯ್ಕೆಮಾಡಿದ ಮಾರ್ಗದಲ್ಲಿ ಉಪಯುಕ್ತ ಸ್ಥಳಗಳನ್ನು ಅನ್ವೇಷಿಸಿ.', 'copilot.header_sub': 'ಸ್ವಾಯತ್ತ ಪ್ರವಾಸ ಯೋಜನೆ ಮತ್ತು ವಿವರಣಾ ಸ್ಟುಡಿಯೋ'}, 'ml': {'nav.route_corridor': 'റൂട്ട് കോറിഡോർ', 'nav.active_path': 'സജീവ റൂട്ട്', 'nav.route_endpoints': 'റൂട്ട് അറ്റങ്ങൾ', 'nav.live_map_hud': 'ലൈവ് മാപ്പ് HUD', 'nav.distance': 'ദൂരം', 'nav.est_time': 'കണക്കാക്കിയ സമയം', 'nav.mode': 'യാത്രാ മോഡ്', 'nav.fit_route': 'റൂട്ട് ഫിറ്റ് ചെയ്യുക', 'nav.tour': '🚀 ടൂർ', 'nav.all_routes_desc': 'പ്രിഡിക്റ്റീവ് അഡാപ്റ്റീവ് നാവിഗേഷനും ലൈവ് റൂട്ടിംഗും', 'tab.selected_place': '📍 തിരഞ്ഞെടുത്ത സ്ഥലം', 'tab.route_details': 'ℹ️ റൂട്ട് വിശദാംശങ്ങൾ', 'aura.chip_route': '🗺️ റൂട്ട്', 'aura.chip_places': '📍 സ്ഥലങ്ങൾ', 'aura.chip_plan': '✈️ പ്ലാൻ', 'aura.chip_cost': '⛽ ചെലവ്', 'aura.chip_stays': '🏨 താമസസ്ഥലം', 'aura.chip_ask': '💬 ചോദിക്കുക', 'aura.chip_clear': '🗑️ മായ്ക്കുക', 'aura.welcome_badge': '🤖 AURA തയ്യാറാണ്', 'aura.welcome_msg': '👋 <b>നമസ്കാരം! ഞാൻ ഔറ</b>, <b>NexRoute</b> നായുള്ള നിങ്ങളുടെ ഇന്റലിജന്റ് AI യാത്രാ സഹായി.<br><br>യാത്രാ പ്ലാനിംഗ്, മികച്ച റൂട്ടുകൾ, അടുത്തുള്ള സ്ഥലങ്ങൾ, ഇന്ധന ചെലവ് എന്നിവ കണ്ടെത്താൻ ഞാൻ സഹായിക്കാം.<br><br>ഇന്ന് നിങ്ങൾ എവിടേക്ക് യാത്ര ചെയ്യാൻ ആഗ്രഹിക്കുന്നു?', 'places.header_sub': 'നിങ്ങളുടെ ലൊക്കേഷന് അടുത്തുള്ളതോ അല്ലെങ്കിൽ റൂട്ടിലുള്ളതോ ആയ പ്രധാന സ്ഥലങ്ങൾ കണ്ടെത്തുക.', 'copilot.header_sub': 'യാത്രാ പ്ലാനിംഗ് & യാത്രാവിവരണം സ്റ്റുഡിയോ'}, 'bn': {'nav.route_corridor': 'রুট করিডোর', 'nav.active_path': 'সক্রিয় পথ', 'nav.route_endpoints': 'রুটের প্রান্ত', 'nav.live_map_hud': 'লাইভ ম্যাপ HUD', 'nav.distance': 'দূরত্ব', 'nav.est_time': 'আনুমানিক সময়', 'nav.mode': 'ভ্রমণ মাধ্যম', 'nav.fit_route': 'রুট ফিট করুন', 'nav.tour': '🚀 ট্যুর', 'nav.all_routes_desc': 'ভবিষ্যদ্বাণীমূলক অভিযোজিত নেভিগেশন এবং লাইভ রুট প্ল্যানিং', 'tab.selected_place': '📍 নির্বাচিত স্থান', 'tab.route_details': 'ℹ️ রুটের বিবরণ', 'aura.chip_route': '🗺️ রুট', 'aura.chip_places': '📍 স্থান', 'aura.chip_plan': '✈️ পরিকল্পনা', 'aura.chip_cost': '⛽ খরচ', 'aura.chip_stays': '🏨 হোটেল', 'aura.chip_ask': '💬 জিজ্ঞাসা', 'aura.chip_clear': '🗑️ পরিষ্কার', 'aura.welcome_badge': '🤖 AURA প্রস্তুত', 'aura.welcome_msg': '👋 <b>নমস্কার! আমি অরা</b>, <b>NexRoute</b> এর জন্য আপনার বুদ্ধিমান AI ভ্রমণ সহকারী।<br><br>আমি আপনাকে ভ্রমণের পরিকল্পনা করতে, সেরা রুট খুঁজে পেতে এবং নিকটবর্তী স্থান আবিষ্কার করতে সাহায্য করতে পারি।<br><br>আজ আপনি কোথায় ভ্রমণ করতে চান?', 'places.header_sub': 'আপনার অবস্থানের কাছাকাছি বা নির্বাচিত রুটের সাথে দরকারী স্থানগুলি খুঁজুন।', 'copilot.header_sub': 'স্বয়ংক্রিয় ভ্রমণ পরিকল্পনা ও ভ্রমণসূচি স্টুডিও'}, 'mr': {'nav.route_corridor': 'मार्ग कॉरिडॉर', 'nav.active_path': 'सक्रिय मार्ग', 'nav.route_endpoints': 'मार्गाची टोके', 'nav.live_map_hud': 'लाइव्ह नकाशा HUD', 'nav.distance': 'अंतर', 'nav.est_time': 'अंदाजे वेळ', 'nav.mode': 'प्रवास मोड', 'nav.fit_route': 'मार्ग फिट करा', 'nav.tour': '🚀 टूर', 'nav.all_routes_desc': 'अचूक अनुकूलनक्षम नेव्हिगेशन आणि थेट मार्ग नियोजन', 'tab.selected_place': '📍 निवडलेले ठिकाण', 'tab.route_details': 'ℹ️ मार्ग तपशील', 'aura.chip_route': '🗺️ मार्ग', 'aura.chip_places': '📍 ठिकाणे', 'aura.chip_plan': '✈️ योजना', 'aura.chip_cost': '⛽ खर्च', 'aura.chip_stays': '🏨 मुक्काम', 'aura.chip_ask': '💬 विचारा', 'aura.chip_clear': '🗑️ साफ करा', 'aura.welcome_badge': '🤖 AURA सज्ज आहे', 'aura.welcome_msg': '👋 <b>नमस्कार! मी ऑरा आहे</b>, <b>NexRoute</b> साठी तुमची बुद्धिमान AI प्रवास सहाय्यक.<br><br>मी तुम्हाला प्रवासाचे नियोजन, सर्वोत्तम मार्ग, जवळची ठिकाणे आणि इंधन खर्चाचा अंदाज लावण्यात मदत करू शकते.<br><br>आज तुम्हाला कुठे प्रवास करायचा आहे?', 'places.header_sub': 'तुमच्या स्थानाजवळील किंवा निवडलेल्या मार्गावरील उपयुक्त ठिकाणे शोधा.', 'copilot.header_sub': 'स्वायत्त सहल नियोजन आणि प्रवास कार्यक्रम स्टुडिओ'}}.items():
    if _l_code in TRANSLATIONS:
        TRANSLATIONS[_l_code].update(_entries)

try:
    _load_locale_overrides()
except Exception:
    pass
