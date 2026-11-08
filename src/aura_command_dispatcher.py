"""
NexRoute — AURA Global Jarvis-Style Voice Command Dispatcher & Intelligent Application Controller
Transforms the AURA / JARVIS voice assistant into a FULL UNIVERSAL APPLICATION CONTROLLER.

Understands natural language commands across all 8 supported NextRoute languages
(English, Telugu, Hindi, Tamil, Kannada, Malayalam, Bengali, Marathi) and controls
every module, page, feature, setting, vehicle mode, navigation state, and 3D companion.

Architecture:
Speech Recognition -> NLU -> Intent + Parameters -> Command Validation -> Action Dispatcher
-> Existing Application Functions & Session State -> Synchronize UI + 3D Cockpit -> Multilingual Confirmation
"""

import re
import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("nexroute.aura_dispatcher")


class AuraCommandType(str, Enum):
    # Core Application Controller Intents
    OPEN_MODULE = "OPEN_MODULE"
    CLOSE_MODULE = "CLOSE_MODULE"
    SWITCH_PAGE = "SWITCH_PAGE"
    SET_APPLICATION_LANGUAGE = "SET_APPLICATION_LANGUAGE"
    SET_THEME = "SET_THEME"
    UPDATE_SETTING = "UPDATE_SETTING"
    UPDATE_USER_PREFERENCE = "UPDATE_USER_PREFERENCE"

    # Location & Route Planning Intents
    SET_ORIGIN = "SET_ORIGIN"
    SET_DESTINATION = "SET_DESTINATION"
    USE_CURRENT_LOCATION = "USE_CURRENT_LOCATION"
    SWAP_LOCATIONS = "SWAP_LOCATIONS"
    ADD_WAYPOINT = "ADD_WAYPOINT"
    REMOVE_WAYPOINT = "REMOVE_WAYPOINT"

    # Navigation Lifecycle Intents
    START_NAVIGATION = "START_NAVIGATION"
    STOP_NAVIGATION = "STOP_NAVIGATION"
    PAUSE_NAVIGATION = "PAUSE_NAVIGATION"
    RESUME_NAVIGATION = "RESUME_NAVIGATION"

    # Transport & Route Optimization Intents
    SELECT_VEHICLE = "SELECT_VEHICLE"
    SELECT_ROUTE = "SELECT_ROUTE"
    CHANGE_ROUTE_PRIORITY = "CHANGE_ROUTE_PRIORITY"
    RECALCULATE_ROUTE = "RECALCULATE_ROUTE"
    SHOW_ALTERNATIVE_ROUTES = "SHOW_ALTERNATIVE_ROUTES"

    # Map Controls
    FIT_MAP = "FIT_MAP"
    ZOOM_MAP = "ZOOM_MAP"
    MAP_STYLE = "MAP_STYLE"
    MAP_ACTION = "MAP_ACTION"

    # 3D Virtual Guide & Cockpit Controls
    TOGGLE_3D_MODE = "TOGGLE_3D_MODE"
    CONTROL_3D_COMPANION = "CONTROL_3D_COMPANION"

    # Travel Modules Intents
    SEARCH_HOTEL = "FACILITY_SEARCH"       # Compatible alias for tests
    FACILITY_SEARCH = "FACILITY_SEARCH"
    SEARCH_FLIGHT = "SEARCH_FLIGHT"
    SEARCH_RESTAURANT = "SEARCH_RESTAURANT"
    OPEN_MY_TRIPS = "OPEN_MY_TRIPS"
    SAVE_TRIP = "SAVE_TRIP"
    SEARCH_SAVED_LOCATIONS = "SEARCH_SAVED_LOCATIONS"
    OPEN_PROFILE = "OPEN_PROFILE"

    # Chained Multi-Action Sequences
    MULTI_ACTION_SEQUENCE = "MULTI_ACTION_SEQUENCE"

    # Assistant & Conversational Help Intents
    VOICE_CONTROL = "VOICE_CONTROL"
    APPLICATION_HELP = "APPLICATION_HELP"
    GENERAL_TRAVEL_QUESTION = "GENERAL_TRAVEL_QUESTION"
    GENERAL_CHAT = "GENERAL_CHAT"

    # Legacy & Backward-Compatibility aliases
    NAVIGATE_TAB = "NAVIGATE_TAB"
    ROUTE_ACTION = "ROUTE_ACTION"
    TRAVEL_TOOL = "TRAVEL_TOOL"
    UNKNOWN = "UNKNOWN"


class AuraExecutionResult:
    def __init__(
        self,
        command_type: AuraCommandType,
        spoken_response: str,
        text_response: str,
        action_name: str = "none",
        ui_updates: Optional[Dict[str, Any]] = None,
        requires_confirmation: bool = False,
        confirmation_prompt: Optional[str] = None,
        success: bool = True,
        actions_executed: Optional[List[Dict[str, Any]]] = None
    ):
        self.command_type = command_type
        self.spoken_response = spoken_response
        self.text_response = text_response
        self.action_name = action_name
        self.ui_updates = ui_updates or {}
        self.requires_confirmation = requires_confirmation
        self.confirmation_prompt = confirmation_prompt
        self.success = success
        self.actions_executed = actions_executed or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command_type": self.command_type.value,
            "spoken_response": self.spoken_response,
            "text_response": self.text_response,
            "action_name": self.action_name,
            "ui_updates": self.ui_updates,
            "requires_confirmation": self.requires_confirmation,
            "confirmation_prompt": self.confirmation_prompt,
            "success": self.success,
            "actions_executed": self.actions_executed
        }


class AuraGlobalCommandDispatcher:
    """
    Central Autonomous JARVIS Voice Application Controller for NextRoute.
    Translates natural-language single and multi-action voice commands into concrete
    application actions, state updates, map manipulations, routing, and 3D companion tracking.
    """

    SUPPORTED_LANGUAGES = ["en", "te", "hi", "ta", "kn", "ml", "bn", "mr"]

    # Multilingual response templates across all 8 supported NextRoute languages
    RESPONSES: Dict[str, Dict[str, str]] = {
        "en": {
            "welcome": "Good morning, Boss! Welcome to NextRoute. How can I help you?",
            "nav_opened": "Opening navigation.",
            "trips_opened": "Here are your trips and itinerary studio.",
            "bookings_opened": "Opening your bookings.",
            "hotels_opened": "Finding hotels and stays for your journey.",
            "flights_opened": "Opening flight corridors planner.",
            "restaurants_opened": "Finding nearby restaurants and food spots.",
            "profile_opened": "Opening your account profile and travel preferences.",
            "settings_opened": "Opening application settings.",
            "back_opened": "Going back to previous screen.",
            "home_opened": "Returning to home dashboard.",
            "chat_opened": "AURA Travel Copilot is ready.",
            "facilities_opened": "Showing nearby emergency and travel amenities.",
            "places_opened": "Opening your saved bookmarks and places.",
            "guide_opened": "Opening 3D virtual guide cockpit.",
            "satellite_switched": "Switched to satellite hybrid view.",
            "roadmap_switched": "Switched to roadmap view.",
            "terrain_switched": "Switched to terrain elevation view.",
            "gps_centered": "Centering map on your live GPS coordinates.",
            "route_fitted": "Adjusting camera to fit the complete route corridor.",
            "dest_cleared": "Destination has been cleared.",
            "orig_cleared": "Starting point reset to live GPS.",
            "swapped": "Start and destination locations swapped. Recalculating routes.",
            "facility_found": "Locating {category} around your route corridor.",
            "fuel_tool": "Opening fuel and toll expense calculator.",
            "confirm_clear_route": "Boss, are you sure you want to clear your active route?",
            "confirm_delete_trips": "Boss, are you sure you want to delete your saved trips? Please confirm.",
            "nav_started": "Navigation started. Guiding you along your corridor, Boss.",
            "nav_stopped": "Navigation stopped. Journey ended, Boss.",
            "nav_paused": "Navigation paused. Live tracking on standby.",
            "nav_resumed": "Navigation resumed. Live tracking active, Boss.",
            "nav_already_idle": "Navigation is currently idle, Boss.",
            "nav_missing_dest": "Please set a destination before starting navigation, Boss.",
            "vehicle_switched": "Vehicle mode switched to {vehicle}. Recalculating route.",
            "priority_fastest": "Optimizing for fastest route with minimum travel time.",
            "priority_shortest": "Optimizing for shortest physical road distance.",
            "priority_balanced": "Optimizing for balanced route between time and distance.",
            "priority_accessible": "Optimizing for step-free accessible road corridors.",
            "alt_routes_shown": "Displaying all available alternative route corridors.",
            "lang_switched": "NextRoute language switched to {lang}.",
            "theme_dark": "Dark mode enabled, Boss.",
            "theme_light": "Light mode enabled, Boss.",
            "3d_enabled": "3D virtual guide companion activated.",
            "3d_disabled": "Switched to 2.5D top-down view.",
            "camera_follow": "Camera locked to follow your vehicle.",
            "trip_saved": "Current route saved to My Trips.",
            "help_overview": "NextRoute supports complete voice control: destination navigation, vehicle modes, route priorities, 3D companion, hotels, flights, and settings.",
            "unrecognized": "Processing your query: \"{query}\".",
        },
        "te": {
            "welcome": "నమస్కారం, బాస్! నెక్స్‌రూట్‌కి స్వాగతం. నేను మీకు ఎలా సహాయపడగలను?",
            "nav_opened": "నావిగేషన్ తెరవబడింది.",
            "trips_opened": "మీ ట్రిప్స్ మరియు ఐటినెరరీ స్టూడియో ఇక్కడ ఉన్నాయి.",
            "bookings_opened": "మీ బుకింగ్స్ తెరవబడ్డాయి.",
            "hotels_opened": "హోటళ్లు మరియు బస వెతుకుతున్నాను.",
            "flights_opened": "ఫ్లైట్ ప్లానర్ తెరుస్తున్నాను.",
            "restaurants_opened": "సమీప రెస్టారెంట్లు మరియు ఆహార ప్రదేశాలు వెతుకుతున్నాను.",
            "profile_opened": "మీ ప్రొఫైల్ మరియు ప్రయాణ ప్రాధాన్యతలు తెరవబడ్డాయి.",
            "settings_opened": "అప్లికేషన్ సెట్టింగ్స్ తెరవబడ్డాయి.",
            "back_opened": "మునుపటి స్క్రీన్‌కు వెళ్తున్నాను.",
            "home_opened": "హోమ్ డ్యాష్‌బోర్డ్‌కి తిరిగి వెళ్తున్నాను.",
            "chat_opened": "AURA AI చాట్‌బాట్ సిద్ధంగా ఉంది, బాస్.",
            "facilities_opened": "సమీప అత్యవసర మరియు ప్రయాణ సౌకర్యాలు చూపిస్తున్నాను.",
            "places_opened": "సేవ్ చేసిన ప్రదేశాలు తెరవబడ్డాయి.",
            "guide_opened": "3D వర్చువల్ గైడ్ కాక్‌పిట్ తెరవబడింది.",
            "satellite_switched": "శాటిలైట్ హైబ్రిడ్ వీక్షణకు మార్చబడింది.",
            "roadmap_switched": "రోడ్‌మ్యాప్ వీక్షణకు మార్చబడింది.",
            "terrain_switched": "టెర్రైన్ వీక్షణకు మార్చబడింది.",
            "gps_centered": "మీ ప్రస్తుత లైవ్ GPS లొకేషన్‌ను గుర్తిస్తున్నాను.",
            "route_fitted": "మొత్తం రూట్ కనిపించేలా మ్యాప్ సర్దుబాటు చేశాను.",
            "dest_cleared": "గమ్యస్థానం క్లియర్ చేయబడింది.",
            "orig_cleared": "ప్రారంభ స్థానం లైవ్ GPS కి రీసెట్ చేయబడింది.",
            "swapped": "ప్రారంభ స్థానం మరియు గమ్యస్థానం మార్చబడ్డాయి. రూట్ మళ్లీ లెక్కిస్తున్నాను.",
            "facility_found": "సమీపంలోని {category} వెతుకుతున్నాను.",
            "fuel_tool": "ఇంధనం మరియు టోల్ ఖర్చుల కాలిక్యులేటర్ తెరుస్తున్నాను.",
            "confirm_clear_route": "బాస్, మీరు నిజంగానే ఈ రూట్ క్లియర్ చేయాలనుకుంటున్నారా?",
            "confirm_delete_trips": "బాస్, మీరు నిజంగానే మీ సేవ్ చేసిన ట్రిప్స్ తొలగించాలనుకుంటున్నారా?",
            "nav_started": "నావిగేషన్ ప్రారంభించబడింది. ప్రయాణం మొదలవుతోంది, బాస్.",
            "nav_stopped": "నావిగేషన్ నిలిపివేయబడింది, బాస్.",
            "nav_paused": "నావిగేషన్ విరామంలో ఉంది.",
            "nav_resumed": "నావిగేషన్ పునఃప్రారంభించబడింది, బాస్.",
            "nav_already_idle": "నావిగేషన్ ప్రస్తుతం నిలిపివేయబడి ఉంది, బాస్.",
            "nav_missing_dest": "నావిగేషన్ ప్రారంభించే ముందు దయచేసి గమ్యస్థానాన్ని చెప్పండి, బాస్.",
            "vehicle_switched": "వాహనం {vehicle} కు మార్చబడింది. రూట్ తిరిగి లెక్కిస్తున్నాను.",
            "priority_fastest": "అతి తక్కువ సమయంలో చేరే వేగవంతమైన రూట్ ఎంచుకున్నాను.",
            "priority_shortest": "అతి తక్కువ దూరపు రూట్ ఎంచుకున్నాను.",
            "priority_balanced": "సమయం మరియు దూరం సమతుల్యమైన రూట్ ఎంచుకున్నాను.",
            "priority_accessible": "సులభతరమైన రూట్ ఎంచుకున్నాను.",
            "alt_routes_shown": "అందుబాటులో ఉన్న అన్ని ప్రత్యామ్నాయ రూట్లను చూపిస్తున్నాను.",
            "lang_switched": "భాషను {lang} లోకి మార్చాను, బాస్.",
            "theme_dark": "డార్క్ మోడ్ ప్రారంభించబడింది, బాస్.",
            "theme_light": "లైట్ మోడ్ ప్రారంభించబడింది, బాస్.",
            "3d_enabled": "3D వర్చువల్ గైడ్ యాక్టివేట్ చేయబడింది.",
            "3d_disabled": "2.5D వీక్షణకు మార్చబడింది.",
            "camera_follow": "కెమెరా వాహనాన్ని అనుసరిస్తోంది.",
            "trip_saved": "రూట్ మై ట్రిప్స్‌లో సేవ్ చేయబడింది.",
            "help_overview": "నెక్స్‌రూట్ వాయిస్ కంట్రోల్ ద్వారా నావిగేషన్, వాహన మోడ్‌లు, హోటళ్లు, ఫ్లైట్లు మరియు సెట్టింగ్స్‌ను నియంత్రించవచ్చు.",
            "unrecognized": "నేను విన్నాను: \"{query}\".",
        },
        "hi": {
            "welcome": "नमस्ते, बॉस! नेक्स्ट-रूट में आपका स्वागत है। मैं आपकी क्या मदद कर सकता हूँ?",
            "nav_opened": "नेविगेशन खोला जा रहा है।",
            "trips_opened": "आपकी यात्राएं और यात्रा स्टूडियो खोले जा रहे हैं।",
            "bookings_opened": "आपकी बुकिंग्स खोली जा रही हैं।",
            "hotels_opened": "होटल और विश्राम स्थल ढूंढे जा रहे हैं।",
            "flights_opened": "फ्लाइट प्लानर खोला जा रहा है।",
            "restaurants_opened": "निकटवर्ती रेस्टोरेंट और भोजन स्थल ढूंढे जा रहे हैं।",
            "profile_opened": "आपकी प्रोफाइल और यात्रा प्राथमिकताएं खोली जा रही हैं।",
            "settings_opened": "ऐप सेटिंग्स खोली जा रही हैं।",
            "back_opened": "पिछली स्क्रीन पर वापस जा रहे हैं।",
            "home_opened": "होम डैशबोर्ड पर लौट रहे हैं।",
            "chat_opened": "AURA AI चैटबॉट तैयार है, बॉस।",
            "facilities_opened": "आस-पास की आपातकालीन और यात्रा सुविधाएं दिखाई जा रही हैं।",
            "places_opened": "सहेजे गए स्थान खोले जा रहे हैं।",
            "guide_opened": "3D वर्चुअल गाइड कॉकपिट खोला जा रहा है।",
            "satellite_switched": "सैटेलाइट हाइब्रिड दृश्य पर स्विच कर दिया गया है।",
            "roadmap_switched": "रोडमैप दृश्य पर स्विच कर दिया गया है।",
            "terrain_switched": "टेरेन एलिवेशन दृश्य पर स्विच किया गया है।",
            "gps_centered": "आपकी लाइव GPS लोकेशन पर मैप केंद्रित किया जा रहा है।",
            "route_fitted": "पूरा मार्ग मैप पर फ़िट कर दिया गया है।",
            "dest_cleared": "गंतव्य स्थान हटा दिया गया है।",
            "orig_cleared": "शुरुआती बिंदु लाइव GPS पर रीसेट किया गया है।",
            "swapped": "शुरुआत और गंतव्य बदल दिए गए हैं। मार्ग पुनः गणना की जा रही है।",
            "facility_found": "निकटवर्ती {category} खोजे जा रहे हैं।",
            "fuel_tool": "ईंधन और टोल खर्च की गणना खोली जा रही है।",
            "confirm_clear_route": "बॉस, क्या आप वाकई सक्रिय मार्ग को हटाना चाहते हैं?",
            "confirm_delete_trips": "बॉस, क्या आप सहेजी गई यात्राएं हटाना चाहते हैं? पुष्टि करें।",
            "nav_started": "नेविगेशन शुरू हो गया है। सुरक्षित यात्रा, बॉस।",
            "nav_stopped": "नेविगेशन रोक दिया गया है, बॉस।",
            "nav_paused": "नेविगेशन ठहराव पर है।",
            "nav_resumed": "नेविगेशन फिर से शुरू किया गया, बॉस।",
            "nav_already_idle": "नेविगेशन पहले से ही रुका हुआ है, बॉस।",
            "nav_missing_dest": "नेविगेशन शुरू करने से पहले कृपया गंतव्य बताएं, बॉस।",
            "vehicle_switched": "वाहन {vehicle} पर सेट किया गया है। मार्ग पुनः बनाया जा रहा है।",
            "priority_fastest": "न्यूनतम समय वाला सबसे तेज़ मार्ग चुना गया है।",
            "priority_shortest": "सबसे छोटी सड़क दूरी वाला मार्ग चुना गया है।",
            "priority_balanced": "समय और दूरी का संतुलित मार्ग चुना गया है।",
            "priority_accessible": "सुलभ मार्ग चुना गया है।",
            "alt_routes_shown": "सभी वैकल्पिक मार्ग दिखाए जा रहे हैं।",
            "lang_switched": "भाषा {lang} में बदल दी गई है, बॉस।",
            "theme_dark": "डार्क मोड सक्रिय किया गया, बॉस।",
            "theme_light": "लाइट मोड सक्रिय किया गया, बॉस।",
            "3d_enabled": "3D वर्चुअल गाइड चालू कर दिया गया है।",
            "3d_disabled": "2.5D दृश्य पर स्विच किया गया।",
            "camera_follow": "कैमरा आपके वाहन का अनुसरण कर रहा है।",
            "trip_saved": "सक्रिय मार्ग सुरक्षित कर लिया गया है।",
            "help_overview": "नेक्स्ट-रूट वॉइस कंट्रोल से नेविगेशन, वाहन, होटल, फ्लाइट्स और सेटिंग्स नियंत्रित कर सकते हैं।",
            "unrecognized": "मैंने सुना: \"{query}\"।",
        },
        "ta": {
            "welcome": "வணக்கம், பாஸ்! நெக்ஸ்-ரூட்டிற்கு நல்வரவு. நான் உங்களுக்கு எப்படி உதவ முடியும்?",
            "nav_opened": "வழிசெலுத்தல் திறக்கப்படுகிறது.",
            "trips_opened": "உங்கள் பயணங்கள் திறக்கப்படுகின்றன.",
            "bookings_opened": "முன்பதிவுகள் திறக்கப்படுகின்றன.",
            "hotels_opened": "விடுதிகள் தேடப்படுகின்றன.",
            "flights_opened": "விமான திட்டமிடுபவர் திறக்கப்படுகிறது.",
            "restaurants_opened": "உணவகங்கள் தேடப்படுகின்றன.",
            "profile_opened": "உங்கள் சுயவிவரம் திறக்கப்படுகிறது.",
            "settings_opened": "அமைப்புகள் திறக்கப்படுகின்றன.",
            "back_opened": "முந்தைய திரைக்கு செல்கிறது.",
            "home_opened": "முகப்புத் திரைக்கு திரும்புகிறது.",
            "chat_opened": "AURA AI சாட்பாட் தயாராக உள்ளது, பாஸ்.",
            "facilities_opened": "அருகிலுள்ள அவசர வசதிகள் காட்டப்படுகின்றன.",
            "places_opened": "சேமிக்கப்பட்ட இடங்கள் காட்டப்படுகின்றன.",
            "guide_opened": "3D வழிகாட்டி திறக்கப்படுகிறது.",
            "satellite_switched": "செயற்கைக்கோள் பார்வைக்கு மாற்றப்பட்டது.",
            "roadmap_switched": "சாலை வரைபட பார்வைக்கு மாற்றப்பட்டது.",
            "terrain_switched": "நிலப்பரப்பு பார்வைக்கு மாற்றப்பட்டது.",
            "gps_centered": "உங்கள் நேரலை இருப்பிடம் கண்டறியப்படுகிறது.",
            "route_fitted": "முழு பாதை அமைக்கப்பட்டது.",
            "dest_cleared": "இலக்கு அழிக்கப்பட்டது.",
            "orig_cleared": "தொடக்க புள்ளி மீட்டமைக்கப்பட்டது.",
            "swapped": "தொடக்கமும் இலக்கும் மாற்றப்பட்டன.",
            "facility_found": "அருகிலுள்ள {category} தேடப்படுகிறது.",
            "fuel_tool": "எரிபொருள் கால்குலேட்டர் திறக்கப்படுகிறது.",
            "confirm_clear_route": "பாஸ், நீங்கள் பாதையை அழிக்க விரும்புகிறீர்களா?",
            "confirm_delete_trips": "சேமிக்கப்பட்ட பயணங்களை நீக்க வேண்டுமா?",
            "nav_started": "வழிசெலுத்தல் தொடங்கியது. பாதுகாப்பான பயணம், பாஸ்.",
            "nav_stopped": "வழிசெலுத்தல் நிறுத்தப்பட்டது, பாஸ்.",
            "nav_paused": "வழிசெலுத்தல் இடைநிறுத்தப்பட்டது.",
            "nav_resumed": "வழிசெலுத்தல் தொடர்கிறது, பாஸ்.",
            "nav_already_idle": "வழிசெலுத்தல் தற்போது செயலிழந்துள்ளது, பாஸ்.",
            "nav_missing_dest": "வழிசெலுத்தலைத் தொடங்குவதற்கு முன் இலக்கை குறிப்பிடவும், பாஸ்.",
            "vehicle_switched": "வாகனம் {vehicle} க்கு மாற்றப்பட்டது.",
            "priority_fastest": "வேகமான பாதை தேர்ந்தெடுக்கப்பட்டது.",
            "priority_shortest": "குறுகிய பாதை தேர்ந்தெடுக்கப்பட்டது.",
            "priority_balanced": "சமநிலையான பாதை தேர்ந்தெடுக்கப்பட்டது.",
            "priority_accessible": "எளிதான அணுகல் பாதை தேர்ந்தெடுக்கப்பட்டது.",
            "alt_routes_shown": "அனைத்து மாற்றுப் பாதைகளும் காட்டப்படுகின்றன.",
            "lang_switched": "மொழி {lang} ஆக மாற்றப்பட்டது, பாஸ்.",
            "theme_dark": "இருண்ட பயன்முறை இயக்கப்பட்டது.",
            "theme_light": "வெளிச்ச பயன்முறை இயக்கப்பட்டது.",
            "3d_enabled": "3D வழிகாட்டி இயக்கப்பட்டது.",
            "3d_disabled": "2.5D பார்வைக்கு மாற்றப்பட்டது.",
            "camera_follow": "கேமரா வாகனத்தைப் பின்தொடர்கிறது.",
            "trip_saved": "பயணம் சேமிக்கப்பட்டது.",
            "help_overview": "நெக்ஸ்-ரூட் குரல் மூலம் வழிசெலுத்தல், வாகனம், விடுதிகள் மற்றும் அமைப்புகளை கட்டுப்படுத்தலாம்.",
            "unrecognized": "நான் கேட்டது: \"{query}\".",
        },
        "kn": {
            "welcome": "ನಮಸ್ಕಾರ, ಬಾಸ್! ನೆಕ್ಸ್ಟ್‌ರೂಟ್‌ಗೆ ಸುಸ್ವಾಗತ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?",
            "nav_opened": "ನ್ಯಾವಿಗೇಷನ್ ತೆರೆಯಲಾಗಿದೆ.",
            "trips_opened": "ನಿಮ್ಮ ಪ್ರವಾಸಗಳು ಇಲ್ಲಿವೆ.",
            "bookings_opened": "ಬುಕಿಂಗ್‌ಗಳು ತೆರೆಯಲ್ಪಟ್ಟಿವೆ.",
            "hotels_opened": "ಹೋಟೆಲ್‌ಗಳನ್ನು ಹುಡುಕಲಾಗುತ್ತಿದೆ.",
            "flights_opened": "ಫ್ಲೈಟ್ ಪ್ಲಾನರ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            "restaurants_opened": "ಹತ್ತಿರದ ರೆಸ್ಟೋರೆಂಟ್‌ಗಳನ್ನು ಹುಡುಕಲಾಗುತ್ತಿದೆ.",
            "profile_opened": "ನಿಮ್ಮ ಪ್ರೊಫೈಲ್ ತೆರೆಯಲಾಗಿದೆ.",
            "settings_opened": "ಸೆಟ್ಟಿಂಗ್‌ಗಳು ತೆರೆಯಲ್ಪಟ್ಟಿವೆ.",
            "back_opened": "ಹಿಂದಿನ ಪರದೆಗೆ ಹೋಗಲಾಗುತ್ತಿದೆ.",
            "home_opened": "ಮುಖಪುಟಕ್ಕೆ ಮರಳಲಾಗುತ್ತಿದೆ.",
            "chat_opened": "AURA AI ಚಾಟ್‌ಬಾಟ್ ಸಿದ್ಧವಾಗಿದೆ, ಬಾಸ್.",
            "facilities_opened": "ಹತ್ತಿರದ ಸೌಲಭ್ಯಗಳನ್ನು ತೋರಿಸಲಾಗುತ್ತಿದೆ.",
            "places_opened": "ಉಳಿಸಲಾದ ಸ್ಥಳಗಳು ತೆರೆಯಲ್ಪಟ್ಟಿವೆ.",
            "guide_opened": "3D ವರ್ಚುವಲ್ ಗೈಡ್ ತೆರೆಯಲಾಗಿದೆ.",
            "satellite_switched": "ಉಪಗ್ರಹ ನೋಟಕ್ಕೆ ಬದಲಾಯಿಸಲಾಗಿದೆ.",
            "roadmap_switched": "ರಸ್ತೆ ನಕ್ಷೆ ನೋಟಕ್ಕೆ ಬದಲಾಯಿಸಲಾಗಿದೆ.",
            "terrain_switched": "ಭೂಪ್ರದೇಶ ನೋಟಕ್ಕೆ ಬದಲಾಯಿಸಲಾಗಿದೆ.",
            "gps_centered": "ನಿಮ್ಮ ಲೈವ್ ಜಿಪಿಎಸ್ ಸ್ಥಳವನ್ನು ಪತ್ತೆಮಾಡಲಾಗುತ್ತಿದೆ.",
            "route_fitted": "ಸಂಪೂರ್ಣ ಮಾರ್ಗವನ್ನು ನಕ್ಷೆಯಲ್ಲಿ ತೋರಿಸಲಾಗಿದೆ.",
            "dest_cleared": "ಗಮ್ಯಸ್ಥಾನವನ್ನು ತೆರವುಗೊಳಿಸಲಾಗಿದೆ.",
            "orig_cleared": "ಆರಂಭಿಕ ಬಿಂದುವನ್ನು ಮರುಹೊಂದಿಸಲಾಗಿದೆ.",
            "swapped": "ಆರಂಭ ಮತ್ತು ಗಮ್ಯಸ್ಥಾನಗಳನ್ನು ಅದಲು-ಬದಲು ಮಾಡಲಾಗಿದೆ.",
            "facility_found": "ಹತ್ತಿರದ {category} ಹುಡುಕಲಾಗುತ್ತಿದೆ.",
            "fuel_tool": "ಇಂಧನ ವೆಚ್ಚದ ಕ್ಯಾಲ್ಕುಲೇಟರ್ ತೆರೆಯಲಾಗಿದೆ.",
            "confirm_clear_route": "ಬಾಸ್, ನೀವು ಖಚಿತವಾಗಿ ಮಾರ್ಗವನ್ನು ಅಳಿಸಲು ಬಯಸುವಿರಾ?",
            "confirm_delete_trips": "ಉಳಿಸಿದ ಪ್ರವಾಸಗಳನ್ನು ಅಳಿಸಲು ದೃಢೀಕರಿಸಿ.",
            "nav_started": "ನ್ಯಾವಿಗೇಷನ್ ಪ್ರಾರಂಭವಾಗಿದೆ. ಶುಭ ಪ್ರಯಾಣ, ಬಾಸ್.",
            "nav_stopped": "ನ್ಯಾವಿಗೇಷನ್ ನಿಲ್ಲಿಸಲಾಗಿದೆ, ಬಾಸ್.",
            "nav_paused": "ನ್ಯಾವಿಗೇಷನ್ ವಿರಾಮದಲ್ಲಿದೆ.",
            "nav_resumed": "ನ್ಯಾವಿಗೇಷನ್ ಮುಂದುವರಿದಿದೆ, ಬಾಸ್.",
            "nav_already_idle": "ನ್ಯಾವಿಗೇಷನ್ ಪ್ರಸ್ತುತ ಸ್ಥಗಿತಗೊಂಡಿದೆ, ಬಾಸ್.",
            "nav_missing_dest": "ದಯವಿಟ್ಟು ನ್ಯಾವಿಗೇಷನ್ ಪ್ರಾರಂಭಿಸುವ ಮೊದಲು ಗಮ್ಯಸ್ಥಾನವನ್ನು ತಿಳಿಸಿ, ಬಾಸ್.",
            "vehicle_switched": "ವಾಹನವನ್ನು {vehicle} ಗೆ ಬದಲಾಯಿಸಲಾಗಿದೆ.",
            "priority_fastest": "ಅತಿ ವೇಗದ ಮಾರ್ಗವನ್ನು ಆಯ್ಕೆಮಾಡಲಾಗಿದೆ.",
            "priority_shortest": "ಅತಿ ಕಡಿಮೆ ದೂರದ ಮಾರ್ಗವನ್ನು ಆಯ್ಕೆಮಾಡಲಾಗಿದೆ.",
            "priority_balanced": "ಸಮತೋಲಿತ ಮಾರ್ಗವನ್ನು ಆಯ್ಕೆಮಾಡಲಾಗಿದೆ.",
            "priority_accessible": "ಸುಲಭ ಮಾರ್ಗವನ್ನು ಆಯ್ಕೆಮಾಡಲಾಗಿದೆ.",
            "alt_routes_shown": "ಎಲ್ಲಾ ಪರ್ಯಾಯ ಮಾರ್ಗಗಳನ್ನು ತೋರಿಸಲಾಗುತ್ತಿದೆ.",
            "lang_switched": "ಭಾಷೆಯನ್ನು {lang} ಗೆ ಬದಲಾಯಿಸಲಾಗಿದೆ, ಬಾಸ್.",
            "theme_dark": "ಡಾರ್ಕ್ ಮೋಡ್ ಸಕ್ರಿಯಗೊಳಿಸಲಾಗಿದೆ.",
            "theme_light": "ಲೈಟ್ ಮೋಡ್ ಸಕ್ರಿಯಗೊಳಿಸಲಾಗಿದೆ.",
            "3d_enabled": "3D ವರ್ಚುವಲ್ ಗೈಡ್ ಸಕ್ರಿಯಗೊಳಿಸಲಾಗಿದೆ.",
            "3d_disabled": "2.5D ನೋಟಕ್ಕೆ ಬದಲಾಯಿಸಲಾಗಿದೆ.",
            "camera_follow": "ಕ್ಯಾಮರಾ ವಾಹನವನ್ನು ಹಿಂಬಾಲಿಸುತ್ತಿದೆ.",
            "trip_saved": "ಪ್ರವಾಸವನ್ನು ಉಳಿಸಲಾಗಿದೆ.",
            "help_overview": "ನೆಕ್ಸ್ಟ್‌ರೂಟ್ ವಾಯ್ಸ್ ಮೂಲಕ ನ್ಯಾವಿಗೇಷನ್, ವಾಹನ, ಹೋಟೆಲ್‌ಗಳು ಮತ್ತು ಸೆಟ್ಟಿಂಗ್‌ಗಳನ್ನು ನಿಯಂತ್ರಿಸಬಹುದು.",
            "unrecognized": "ನಾನು ಕೇಳಿದೆ: \"{query}\".",
        },
        "ml": {
            "welcome": "നമസ്കാരം, ബോസ്! നെക്സ്റ്റ് റൂട്ടിലേക്ക് സ്വാഗതം. ഞാൻ എങ്ങനെ സഹായിക്കണം?",
            "nav_opened": "നാവിഗേഷൻ തുറന്നു.",
            "trips_opened": "നിങ്ങളുടെ യാത്രകൾ ഇവിടെയുണ്ട്.",
            "bookings_opened": "ബുക്കിംഗുകൾ തുറന്നു.",
            "hotels_opened": "ഹോട്ടലുകൾ കണ്ടെത്തുന്നു.",
            "flights_opened": "ഫ്ലൈറ്റ് പ്ലാനർ തുറക്കുന്നു.",
            "restaurants_opened": "റസ്റ്റോറന്റുകൾ കണ്ടെത്തുന്നു.",
            "profile_opened": "പ്രൊഫൈൽ തുറന്നു.",
            "settings_opened": "സെറ്റിംഗ്സ് തുറന്നു.",
            "back_opened": "മുമ്പത്തെ സ്ക്രീനിലേക്ക് പോകുന്നു.",
            "home_opened": "ഹോം ഡാഷ്‌ബോർഡിലേക്ക് മടങ്ങുന്നു.",
            "chat_opened": "AURA AI ചാറ്റ്ബോട്ട് തയ്യാറാണ്, ബോസ്.",
            "facilities_opened": "സൗകര്യങ്ങൾ കാണിക്കുന്നു.",
            "places_opened": "സേവ് ചെയ്ത സ്ഥലങ്ങൾ തുറന്നു.",
            "guide_opened": "3D വെർച്വൽ ഗൈഡ് തുറന്നു.",
            "satellite_switched": "സാറ്റലൈറ്റ് കാഴ്ചയിലേക്ക് മാറ്റി.",
            "roadmap_switched": "റോഡ്മാപ്പ് കാഴ്ചയിലേക്ക് മാറ്റി.",
            "terrain_switched": "ഭൂപ്രകൃതി കാഴ്ചയിലേക്ക് മാറ്റി.",
            "gps_centered": "തത്സമയ ലൊക്കേഷൻ കണ്ടെത്തുന്നു.",
            "route_fitted": "റൂട്ട് മാപ്പിൽ ക്രമീകരിച്ചു.",
            "dest_cleared": "ലക്ഷ്യസ്ഥാനം മായ്ച്ചു.",
            "orig_cleared": "തുടക്ക സ്ഥലം പുനഃക്രമീകരിച്ചു.",
            "swapped": "തുടക്കവും ലക്ഷ്യസ്ഥാനവും മാറ്റി.",
            "facility_found": "{category} തിരയുന്നു.",
            "fuel_tool": "ഇന്ധന കാൽക്കുലേറ്റർ തുറന്നു.",
            "confirm_clear_route": "റൂട്ട് മായ്‌ക്കാൻ ആഗ്രഹിക്കുന്നുണ്ടോ?",
            "confirm_delete_trips": "യാത്രകൾ ഇല്ലാതാക്കാൻ സ്ഥിരീകരിക്കുക.",
            "nav_started": "നാവിഗേഷൻ ആരംഭിച്ചു. ശുഭയാത്ര, ബോസ്.",
            "nav_stopped": "നാവിഗേഷൻ നിർത്തി, ബോസ്.",
            "nav_paused": "നാവിഗേഷൻ താൽക്കാലികമായി നിർത്തി.",
            "nav_resumed": "നാവിഗേഷൻ പുനരാരംഭിച്ചു, ബോസ്.",
            "nav_already_idle": "നാവിഗേഷൻ നിലവിൽ നിശ്ചലമാണ്, ബോസ്.",
            "nav_missing_dest": "നാവിഗേഷൻ തുടങ്ങുന്നതിന് മുമ്പ് ലക്ഷ്യസ്ഥാനം വ്യക്തമാക്കൂ, ബോസ്.",
            "vehicle_switched": "വാഹനം {vehicle} ലേക്ക് മാറ്റി.",
            "priority_fastest": "ഏറ്റവും വേഗമേറിയ പാത തിരഞ്ഞെടുത്തു.",
            "priority_shortest": "ഏറ്റവും കുറഞ്ഞ ദൂരമുള്ള പാത തിരഞ്ഞെടുത്തു.",
            "priority_balanced": "സന്തുലിതമായ പാത തിരഞ്ഞെടുത്തു.",
            "priority_accessible": "എളുപ്പമുള്ള പാത തിരഞ്ഞെടുത്തു.",
            "alt_routes_shown": "എല്ലാ ഇതര പാതകളും കാണിക്കുന്നു.",
            "lang_switched": "ഭാഷ {lang} ലേക്ക് മാറ്റി, ബോസ്.",
            "theme_dark": "ഡാർക്ക് മോഡ് ഓണാക്കി.",
            "theme_light": "ലൈറ്റ് മോഡ് ഓണാക്കി.",
            "3d_enabled": "3D ഗൈഡ് സജീവമാക്കി.",
            "3d_disabled": "2.5D കാഴ്ചയിലേക്ക് മാറ്റി.",
            "camera_follow": "ക്യാമറ വാഹനം പിന്തുടരുന്നു.",
            "trip_saved": "യാത്ര സേവ് ചെയ്തു.",
            "help_overview": "വോയ്സ് വഴി നാവിഗേഷൻ, വാഹനം, ഹോട്ടലുകൾ, സെറ്റിംഗ്സ് എന്നിവ നിയന്ത്രിക്കാം.",
            "unrecognized": "ഞാൻ കേട്ടത്: \"{query}\".",
        },
        "bn": {
            "welcome": "নমস্কার, বস! নেক্সটরুটে স্বাগতম। আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
            "nav_opened": "ন্যাভিগেশন খোলা হয়েছে।",
            "trips_opened": "আপনার ট্রিপ এবং ভ্রমণ স্টুডিও খোলা হয়েছে।",
            "bookings_opened": "আপনার বুকিং খোলা হয়েছে।",
            "hotels_opened": "হোটেল এবং থাকার জায়গা অনুসন্ধান করা হচ্ছে।",
            "flights_opened": "ফ্লাইট প্ল্যানার খোলা হচ্ছে।",
            "restaurants_opened": "কাছের রেস্তোরাঁ খোঁজা হচ্ছে।",
            "profile_opened": "আপনার প্রোফাইল খোলা হয়েছে।",
            "settings_opened": "সেটিংস খোলা হয়েছে।",
            "back_opened": "পূর্ববর্তী স্ক্রিনে ফিরে যাওয়া হচ্ছে।",
            "home_opened": "হোম ড্যাশবোর্ডে ফিরে যাওয়া হচ্ছে।",
            "chat_opened": "AURA AI চ্যাটবট প্রস্তুত, বস।",
            "facilities_opened": "কাছের জরুরি সুবিধাসমূহ দেখানো হচ্ছে।",
            "places_opened": "সংরক্ষিত স্থানসমূহ খোলা হয়েছে।",
            "guide_opened": "3D ভার্চুয়াল গাইড খোলা হয়েছে।",
            "satellite_switched": "স্যাটেলাইট ভিউতে পরিবর্তন করা হয়েছে।",
            "roadmap_switched": "রোডম্যাপ ভিউতে পরিবর্তন করা হয়েছে।",
            "terrain_switched": "টেরেন ভিউতে পরিবর্তন করা হয়েছে।",
            "gps_centered": "আপনার লাইভ জিপিএস অবস্থান নির্ণয় করা হচ্ছে।",
            "route_fitted": "সম্পূর্ণ রুট ম্যাপে ফিট করা হয়েছে।",
            "dest_cleared": "গন্তব্য মুছে ফেলা হয়েছে।",
            "orig_cleared": "শুরুর স্থান রিসেট করা হয়েছে।",
            "swapped": "শুরু এবং গন্তব্য অদলবদল করা হয়েছে।",
            "facility_found": "কাছের {category} খোঁজা হচ্ছে।",
            "fuel_tool": "জ্বালানী ব্যয় ক্যালকুলেটর খোলা হচ্ছে।",
            "confirm_clear_route": "বস, আপনি কি নিশ্চিতভাবে সক্রিয় রুটটি পরিষ্কার করতে চান?",
            "confirm_delete_trips": "সংরক্ষিত ট্রিপ মুছে ফেলতে নিশ্চিত করুন।",
            "nav_started": "ন্যাভিগেশন শুরু হয়েছে। শুভ যাত্রা, বস।",
            "nav_stopped": "ন্যাভিগেশন বন্ধ করা হয়েছে, বস।",
            "nav_paused": "ন্যাভিগেশন স্থগিত করা হয়েছে।",
            "nav_resumed": "ন্যাভিগেশন পুনরায় শুরু করা হয়েছে, বস।",
            "nav_already_idle": "ন্যাভিগেশন বর্তমানে নিষ্ক্রিয় রয়েছে, বস।",
            "nav_missing_dest": "ন্যাভিগেশন শুরু করার আগে দয়া করে গন্তব্য উল্লেখ করুন, বস।",
            "vehicle_switched": "যানবাহন {vehicle}-এ পরিবর্তন করা হয়েছে।",
            "priority_fastest": "দ্রুততম রুট নির্বাচন করা হয়েছে।",
            "priority_shortest": "স্বল্পতম দূরত্বের রুট নির্বাচন করা হয়েছে।",
            "priority_balanced": "ভারসাম্যপূর্ণ রুট নির্বাচন করা হয়েছে।",
            "priority_accessible": "সহজগম্য রুট নির্বাচন করা হয়েছে।",
            "alt_routes_shown": "সকল বিকল্প রুট দেখানো হচ্ছে।",
            "lang_switched": "ভাষা {lang}-এ পরিবর্তন করা হয়েছে, বস।",
            "theme_dark": "ডার্ক মোড সক্রিয় করা হয়েছে।",
            "theme_light": "লাইট মোড সক্রিয় করা হয়েছে।",
            "3d_enabled": "3D গাইড সক্রিয় করা হয়েছে।",
            "3d_disabled": "2.5D ভিউতে পরিবর্তন করা হয়েছে।",
            "camera_follow": "ক্যামেরা যান অনুসরণ করছে।",
            "trip_saved": "রুট সংরক্ষিত হয়েছে।",
            "help_overview": "ভয়েসের মাধ্যমে ন্যাভিগেশন, যান, হোটেল ও সেটিংস নিয়ন্ত্রণ করা যায়।",
            "unrecognized": "আমি শুনেছি: \"{query}\"।",
        },
        "mr": {
            "welcome": "नमस्कार, बॉस! नेक्स्ट-रूटवर आपले स्वागत आहे. मी आपल्याला कशी मदत करू शकतो?",
            "nav_opened": "नॅव्हिगेशन उघडले आहे.",
            "trips_opened": "आपल्या सहली आणि ट्रिप स्टुडिओ येथे आहेत.",
            "bookings_opened": "आपली बुकिंग्ज उघडली आहेत.",
            "hotels_opened": "हॉटेल्स शोधत आहे.",
            "flights_opened": "फ्लाइट प्लॅनर उघडत आहे.",
            "restaurants_opened": "जवळची रेस्टॉरंट्स शोधत आहे.",
            "profile_opened": "आपले प्रोफाइल उघडले आहे.",
            "settings_opened": "अ‍ॅप सेटिंग्ज उघडली आहेत.",
            "back_opened": "मागील स्क्रीनवर परत जात आहे.",
            "home_opened": "होम डॅशबोर्डवर परत जात आहे.",
            "chat_opened": "AURA AI चॅटबॉट सज्ज आहे, बॉस.",
            "facilities_opened": "जवळपासच्या सुविधा दाखवत आहे.",
            "places_opened": "जतन केलेली ठिकाणे उघडली आहेत.",
            "guide_opened": "3D व्हर्च्युअल गाइड उघडले आहे.",
            "satellite_switched": "सॅटेलाइट दृश्यावर स्विच केले आहे.",
            "roadmap_switched": "रोडमॅप दृश्यावर स्विच केले आहे.",
            "terrain_switched": "टेरेन दृश्यावर स्विच केले आहे.",
            "gps_centered": "आपले थेट GPS स्थान शोधत आहे.",
            "route_fitted": "संपूर्ण मार्ग नकाशावर दाखवला आहे.",
            "dest_cleared": "गंतव्यस्थान हटवले आहे.",
            "orig_cleared": "सुरुवातीचे स्थान पूर्ववत केले आहे.",
            "swapped": "सुरुवात आणि गंतव्यस्थान बदलले आहे.",
            "facility_found": "जवळपासची {category} शोधत आहे.",
            "fuel_tool": "इंधन खर्च कॅल्क्युलेटर उघडत आहे.",
            "confirm_clear_route": "बॉस, आपण नक्की सक्रिय मार्ग हटवू इच्छिता?",
            "confirm_delete_trips": "जतन केलेल्या सहली हटवण्यासाठी पुष्टी करा.",
            "nav_started": "नॅव्हिगेशन सुरू झाले आहे. सुरक्षित प्रवास, बॉस.",
            "nav_stopped": "नॅव्हिगेशन थांबवले आहे, बॉस.",
            "nav_paused": "नॅव्हिगेशन थांबवले आहे.",
            "nav_resumed": "नॅव्हिगेशन पुन्हा सुरू केले आहे, बॉस.",
            "nav_already_idle": "नॅव्हिगेशन सध्या निष्क्रिय आहे, बॉस.",
            "nav_missing_dest": "नॅव्हिगेशन सुरू करण्यापूर्वी कृपया गंतव्यस्थान सांगा, बॉस.",
            "vehicle_switched": "वाहन {vehicle} वर सेट केले आहे.",
            "priority_fastest": "सर्वात वेगवान मार्ग निवडला आहे.",
            "priority_shortest": "सर्वात कमी अंतराचा मार्ग निवडला आहे.",
            "priority_balanced": "संतुलित मार्ग निवडला आहे.",
            "priority_accessible": "सुलभ मार्ग निवडला आहे.",
            "alt_routes_shown": "सर्व पर्यायी मार्ग दाखवले जात आहेत.",
            "lang_switched": "भाषा {lang} मध्ये बदलली आहे, बॉस.",
            "theme_dark": "डार्क मोड सक्षम केला आहे.",
            "theme_light": "लाइट मोड सक्षम केला आहे.",
            "3d_enabled": "3D व्हर्च्युअल गाइड सुरू केले आहे.",
            "3d_disabled": "2.5D दृश्यावर स्विच केले आहे.",
            "camera_follow": "कॅमेरा वाहनाचा पाठलाग करत आहे.",
            "trip_saved": "मार्ग जतन केला आहे.",
            "help_overview": "व्हॉइसद्वारे नॅव्हिगेशन, वाहने, हॉटेल्स आणि सेटिंग्ज नियंत्रित करता येतात.",
            "unrecognized": "मी ऐकले: \"{query}\".",
        }
    }

    # Vehicle mode mapping table
    VEHICLE_MODE_MAP: Dict[str, str] = {
        "car": "CAR", "automobile": "CAR", "drive": "CAR", "driving": "CAR", "taxi": "TAXI", "cab": "TAXI",
        "bike": "BIKE", "motorcycle": "BIKE", "scooter": "BIKE", "two wheeler": "BIKE", "twowheeler": "BIKE",
        "bus": "BUS", "transit": "BUS", "public transit": "BUS",
        "bicycle": "BICYCLE", "cycle": "BICYCLE", "cycling": "BICYCLE",
        "walk": "WALK", "walking": "WALK", "pedestrian": "WALK", "on foot": "WALK",
        "truck": "TRUCK", "heavy vehicle": "TRUCK", "lorry": "TRUCK",
        "tractor": "TRACTOR", "farm vehicle": "TRACTOR",
        "flight": "FLIGHT", "plane": "FLIGHT", "airplane": "FLIGHT", "aviation": "FLIGHT", "airway": "FLIGHT",
        "ship": "WATERWAY", "boat": "WATERWAY", "waterway": "WATERWAY", "ferry": "WATERWAY",
        "train": "TRAIN", "rail": "TRAIN", "railway": "TRAIN",
        "metro": "METRO", "subway": "METRO",
        # Multilingual Indic mappings
        "కారు": "CAR", "కార్": "CAR", "బైక్": "BIKE", "బస్సు": "BUS", "నడక": "WALK", "సైకిల్": "BICYCLE", "విమానం": "FLIGHT", "రైలు": "TRAIN",
        "कार": "CAR", "बाइक": "BIKE", "बस": "BUS", "पैदल": "WALK", "साइकिल": "BICYCLE", "विमान": "FLIGHT", "ट्रेन": "TRAIN"
    }

    # Language code mapping
    LANGUAGE_NAME_MAP: Dict[str, str] = {
        "english": "en", "en": "en",
        "telugu": "te", "తెలుగు": "te", "te": "te",
        "hindi": "hi", "हिन्दी": "hi", "हिंदी": "hi", "hi": "hi",
        "tamil": "ta", "தமிழ்": "ta", "ta": "ta",
        "kannada": "kn", "ಕನ್ನಡ": "kn", "kn": "kn",
        "malayalam": "ml", "മലയാളം": "ml", "ml": "ml",
        "bengali": "bn", "বাংলা": "bn", "bangla": "bn", "bn": "bn",
        "marathi": "mr", "मराठी": "mr", "mr": "mr"
    }

    @classmethod
    def get_greeting(cls, lang: str = "en") -> str:
        lang_key = lang if lang in cls.RESPONSES else "en"
        return cls.RESPONSES[lang_key]["welcome"]

    @classmethod
    def resolve_location(cls, query: str) -> Optional[Dict[str, Any]]:
        """
        Geocodes a location query using the application's actual MapService.
        Never invents coordinates; uses verified geocoding database or Nominatim.
        """
        if not query or not query.strip():
            return None
        clean_q = query.strip()
        try:
            from src.map_service import MapService
            ms = MapService()
            res = ms.geocode(clean_q)
            if res and isinstance(res, dict) and "lat" in res and "lon" in res:
                return {
                    "lat": float(res["lat"]),
                    "lon": float(res["lon"]),
                    "name": res.get("name") or res.get("display_name") or clean_q.title(),
                    "display_name": res.get("display_name") or res.get("name") or clean_q.title()
                }
        except Exception as e_geo:
            logger.warning("Geocoding failed for '%s': %s", clean_q, e_geo)
        return None

    @classmethod
    def parse_and_dispatch(
        cls,
        raw_query: str,
        context: Optional[Dict[str, Any]] = None,
        lang: str = "en"
    ) -> AuraExecutionResult:
        """
        Parses a natural-language voice command (single action or chained multi-action sequence)
        and returns a validated AuraExecutionResult with all concrete state updates.
        """
        ctx = context or {}
        q = (raw_query or "").strip()
        q_lower = q.lower()
        lang_key = lang if lang in cls.RESPONSES else "en"
        resp_bundle = cls.RESPONSES.get(lang_key, cls.RESPONSES["en"])

        if not q_lower:
            return AuraExecutionResult(
                command_type=AuraCommandType.UNKNOWN,
                spoken_response=resp_bundle["welcome"],
                text_response=resp_bundle["welcome"],
                success=True
            )

        # ---------------------------------------------------------------------
        # 1. MULTI-ACTION COMMAND DETECTION & DEPENDENCY ORDERING ENGINE
        # Example: "Set my destination to Hyderabad, change my vehicle to car, choose the fastest route, and start navigation."
        # Or: "Set starting point to Vijayawada, destination to Guntur, select car mode, choose fastest route, and start navigation."
        # ---------------------------------------------------------------------
        multi_action_result = cls._detect_and_handle_multi_action(q, q_lower, ctx, lang_key)
        if multi_action_result:
            return multi_action_result

        # ---------------------------------------------------------------------
        # 2. APPLICATION HELP & DISCOVERY
        # ---------------------------------------------------------------------
        if re.search(r"\b(how\s+do\s+i\s+use|how\s+to\s+use|features?\s+available|what\s+can\s+you\s+do|voice\s+commands?|help\s+me|help\s+menu|సహాయం|मदद)\b", q_lower):
            help_msg = resp_bundle["help_overview"]
            return AuraExecutionResult(
                command_type=AuraCommandType.APPLICATION_HELP,
                spoken_response=help_msg,
                text_response=f"ℹ️ **AURA Application Voice Controls:**\n\n• **Navigation:** \"Navigate to [City]\", \"Start navigation\", \"Stop navigation\", \"Recalculate route\"\n• **Locations:** \"Set starting point to [City]\", \"Swap locations\", \"Use current location\", \"Add stop\"\n• **Vehicles:** \"Change vehicle to car / bike / bus / walk / flight / train / truck\"\n• **Priorities:** \"Choose fastest / shortest / balanced route\", \"Show alternative routes\"\n• **Travel:** \"Find hotels\", \"Search flights\", \"Find restaurants\", \"Open my trips\", \"Open profile\"\n• **Settings:** \"Switch to Telugu / Hindi / Tamil / English\", \"Enable dark mode\", \"Fit route\"",
                action_name="show_application_help",
                ui_updates={"show_help_modal": True}
            )

        # ---------------------------------------------------------------------
        # 3. NAVIGATION MODULE & LIFECYCLE (OPEN / START / STOP / PAUSE / RESUME)
        # ---------------------------------------------------------------------
        # 3.0 Open Navigation Module / Map View
        if (not re.search(r"\bmap\s+details\b", q_lower)) and (
            any(k in q_lower for k in ["నావిగేషన్ తెరవు", "నేవిగేషన్", "नेविगेशन खोलो", "வழிசெலுத்தல்"]) or (
                re.search(r"\b(open|let's\s+open|show|go\s+to|switch\s+to)\s+(the\s+)?(navigation(\s+tab)?|nav(\s+tab)?|map(\s+view|\s+tab)?|route\s+planner)\b", q_lower)
                or re.search(r"^(navigation|nav|route\s+planner|open\s+map|show\s+map)$", q_lower)
            )
        ):
            return AuraExecutionResult(
                command_type=AuraCommandType.OPEN_MODULE,
                spoken_response=resp_bundle.get("nav_opened", "Opening navigation."),
                text_response=f"🧭 {resp_bundle.get('nav_opened', 'Opening navigation.')}",
                action_name="switch_tab_nav",
                ui_updates={"current_view": "map_nav", "target_tab": "nav", "switch_to_nav_tab": True, "scroll_to_app_map": True}
            )

        # 3.1 Start Navigation
        if re.search(r"\b(start\s+navigation|begin\s+navigation|start\s+trip|start\s+journey|start\s+driving|let's\s+go|నావిగేషన్\s+ప్రారంభించు|नेविगेशन\s+शुरू\s+करो)\b", q_lower):
            has_dest = bool(ctx.get("dest_coords") or ctx.get("dest_label"))
            if not has_dest:
                # Validation Failure: cannot start navigation without destination
                msg = resp_bundle["nav_missing_dest"]
                return AuraExecutionResult(
                    command_type=AuraCommandType.START_NAVIGATION,
                    spoken_response=msg,
                    text_response=f"⚠️ {msg}",
                    action_name="validate_navigation_missing_dest",
                    success=False
                )
            nav_msg = resp_bundle["nav_started"]
            return AuraExecutionResult(
                command_type=AuraCommandType.START_NAVIGATION,
                spoken_response=nav_msg,
                text_response=f"🧭 {nav_msg}",
                action_name="start_navigation",
                ui_updates={
                    "current_view": "map_nav",
                    "target_tab": "nav",
                    "aura_journey_active": True,
                    "virtual_guide_moving": True,
                    "gps_tracking_active": True,
                    "user_speed_kmh": 4.8,
                    "scroll_to_app_map": True,
                    "auto_fit_bounds": True
                }
            )

        # 3.2 Stop Navigation
        if re.search(r"\b(stop\s+navigation|end\s+navigation|cancel\s+navigation|stop\s+trip|end\s+journey|నావిగేషన్\s+ఆపు|नेविगेशन\s+रोको)\b", q_lower):
            is_active = bool(ctx.get("navigation_active", False))
            if not is_active:
                msg = resp_bundle["nav_already_idle"]
                return AuraExecutionResult(
                    command_type=AuraCommandType.STOP_NAVIGATION,
                    spoken_response=msg,
                    text_response=f"ℹ️ {msg}",
                    action_name="navigation_already_idle",
                    success=True
                )
            stop_msg = resp_bundle["nav_stopped"]
            return AuraExecutionResult(
                command_type=AuraCommandType.STOP_NAVIGATION,
                spoken_response=stop_msg,
                text_response=f"⏹️ {stop_msg}",
                action_name="stop_navigation",
                ui_updates={
                    "aura_journey_active": False,
                    "virtual_guide_moving": False,
                    "gps_tracking_active": False,
                    "user_speed_kmh": 0.0
                }
            )

        # 3.3 Pause Navigation
        if re.search(r"\b(pause\s+navigation|hold\s+navigation|take\s+a\s+break|నావిగేషన్\s+విరామం|नेविगेशन\s+ठहराव)\b", q_lower):
            pause_msg = resp_bundle["nav_paused"]
            return AuraExecutionResult(
                command_type=AuraCommandType.PAUSE_NAVIGATION,
                spoken_response=pause_msg,
                text_response=f"⏸️ {pause_msg}",
                action_name="pause_navigation",
                ui_updates={
                    "virtual_guide_moving": False,
                    "user_speed_kmh": 0.0
                }
            )

        # 3.4 Resume Navigation
        if re.search(r"\b(resume\s+navigation|continue\s+navigation|resume\s+journey|పునఃప్రారంభించు|नेविगेशन\s+फिर\s+शुरू\s+करो)\b", q_lower):
            resume_msg = resp_bundle["nav_resumed"]
            return AuraExecutionResult(
                command_type=AuraCommandType.RESUME_NAVIGATION,
                spoken_response=resume_msg,
                text_response=f"▶️ {resume_msg}",
                action_name="resume_navigation",
                ui_updates={
                    "aura_journey_active": True,
                    "virtual_guide_moving": True,
                    "gps_tracking_active": True,
                    "user_speed_kmh": 4.8
                }
            )

        # ---------------------------------------------------------------------
        # 4. LOCATION AND ENDPOINT MANAGEMENT (ORIGIN, DESTINATION, WAYPOINTS)
        # ---------------------------------------------------------------------
        # 4.1 Set Origin: "Set my starting point to Vijayawada" / "Start from Guntur"
        orig_match = re.search(r"\b(?:set\s+(?:my\s+)?(?:start(?:ing)?(?:\s+point|\s+location)?|origin)\s+to|start\s+from|from)\s+([a-zA-Z\s\u0C00-\u0C7F\u0900-\u097F]+?)(?:\s*[,.]|\s+and|\s+destination|$)", q, re.IGNORECASE)
        if orig_match:
            raw_orig = orig_match.group(1).strip()
            # Ignore if just the word "current location" or "here"
            if raw_orig.lower() not in ["here", "current location", "my location", "live location"]:
                geo_orig = cls.resolve_location(raw_orig)
                orig_label = geo_orig["display_name"] if geo_orig else raw_orig.title()
                orig_coords = (geo_orig["lat"], geo_orig["lon"]) if geo_orig else None
                spoken_msg = f"Starting point set to {orig_label}."
                return AuraExecutionResult(
                    command_type=AuraCommandType.SET_ORIGIN,
                    spoken_response=spoken_msg,
                    text_response=f"📍 Starting point set to **{orig_label}**.",
                    action_name="set_starting_point",
                    ui_updates={
                        "user_live_coords": orig_coords,
                        "user_live_label": orig_label,
                        "pending_orig": orig_label,
                        "txt_orig": orig_label,
                        "is_custom_start_place": True,
                        "cached_candidate_routes": None,
                        "routes_generated": bool(orig_coords and ctx.get("dest_coords")),
                        "scroll_to_app_map": True
                    }
                )

        # 4.2 Set Destination: "Take me to Hyderabad" / "Navigate to Hyderabad" / "Set destination to Hyderabad"
        dest_match = re.search(r"\b(?:set\s+(?:my\s+)?destination\s+to|navigate\s+to|drive\s+to|take\s+me\s+to|go\s+to|directions?\s+to|route\s+to|plan\s+(?:a\s+)?trip\s+to)\s+([a-zA-Z\s\u0C00-\u0C7F\u0900-\u097F]+)", q, re.IGNORECASE)
        if dest_match:
            dest_query = dest_match.group(1).strip()
            # Exclude app tab names from being treated as destination
            if dest_query.lower() not in ["navigation", "chatbot", "chat", "facilities", "map", "tools", "saved", "my trips", "trips", "profile", "my profile", "hotels", "flights", "restaurants", "settings", "my bookings", "bookings"]:
                geo_dest = cls.resolve_location(dest_query)
                dest_label = geo_dest["display_name"] if geo_dest else dest_query.title()
                dest_coords = (geo_dest["lat"], geo_dest["lon"]) if geo_dest else None
                spoken_msg = f"Destination set to {dest_label}. Finding optimal routes, Boss."
                return AuraExecutionResult(
                    command_type=AuraCommandType.SET_DESTINATION,
                    spoken_response=spoken_msg,
                    text_response=f"🏁 Destination set to **{dest_label}**. Calculating routes...",
                    action_name="voice_set_destination",
                    ui_updates={
                        "selected_dest_coords": dest_coords,
                        "selected_dest_label": dest_label,
                        "pending_dest": dest_label,
                        "txt_dest": dest_label,
                        "target_tab": "nav",
                        "current_view": "map_nav",
                        "active_trip_destination": dest_label,
                        "aura_active_trip_context": {"destination": dest_label, "coords": dest_coords},
                        "cached_candidate_routes": None,
                        "routes_generated": True,
                        "scroll_to_app_map": True,
                        "auto_fit_bounds": True
                    }
                )

        # 4.3 Use Current Location
        if re.search(r"\b(use\s+(my\s+)?current\s+location|use\s+gps|reset\s+start|లొకేషన్\s+వాడు|मेरी\s+लोकेशन)\b", q_lower):
            loc_updates = {"trigger_client_gps_sync": True, "is_custom_start_place": False, "pending_orig": "", "scroll_to_app_map": True}
            return AuraExecutionResult(
                command_type=AuraCommandType.USE_CURRENT_LOCATION,
                spoken_response=resp_bundle["orig_cleared"],
                text_response=f"📍 {resp_bundle['orig_cleared']}",
                action_name="use_current_location",
                ui_updates=loc_updates
            )

        # 4.4 Swap Locations
        if re.search(r"\b(swap\s+(start\s+and\s+destination|locations)|reverse\s+route|తిప్పి\s+రాయు|उल्टा\s+करो)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.SWAP_LOCATIONS,
                spoken_response=resp_bundle["swapped"],
                text_response=f"⇅ {resp_bundle['swapped']}",
                action_name="swap_endpoints",
                ui_updates={"trigger_swap_endpoints": True, "cached_candidate_routes": None, "routes_generated": True}
            )

        # 4.5 Add Waypoint / Stop
        if re.search(r"\b(add\s+a\s+stop|add\s+stop|add\s+waypoint|intermediate\s+stop|స్టాప్\s+జతచేయి)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.ADD_WAYPOINT,
                spoken_response="Intermediate stop selection activated. Click anywhere on the map or search a place, Boss.",
                text_response="🟣 Intermediate stop mode enabled. Select location on map or search bar.",
                action_name="add_intermediate_stop",
                ui_updates={"map_picking_mode": "stop", "target_tab": "nav", "scroll_to_app_map": True}
            )

        # 4.6 Remove Waypoint / Clear Stops
        if re.search(r"\b(remove\s+stop|clear\s+stops|delete\s+stops|స్టాప్స్\s+తొలగించు)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.REMOVE_WAYPOINT,
                spoken_response="All intermediate stops cleared from active route, Boss.",
                text_response="🗑️ Cleared all intermediate stops. Recalculating direct corridor...",
                action_name="clear_intermediate_stops",
                ui_updates={"intermediate_stops": [], "cached_candidate_routes": None, "routes_generated": True}
            )

        # ---------------------------------------------------------------------
        # 5. TRANSPORTATION & VEHICLE MODE CONTROLS
        # ---------------------------------------------------------------------
        veh_match = re.search(r"\b(?:change|switch|set|select|use)\s+(?:the\s+|my\s+)?(?:vehicle|transport(?:ation)?|travel)?\s*(?:mode\s+to|to\s+mode|to)?\s*(car|automobile|bike|motorcycle|scooter|bus|bicycle|cycle|walk|walking|pedestrian|truck|tractor|flight|plane|airway|waterway|boat|ferry|taxi|cab|train|rail|metro|subway)(?:\s+mode)?\b", q_lower)
        if veh_match:
            raw_v = veh_match.group(1).lower()
            sel_v = cls.VEHICLE_MODE_MAP.get(raw_v, "CAR")
            v_msg = resp_bundle["vehicle_switched"].format(vehicle=sel_v.title())
            return AuraExecutionResult(
                command_type=AuraCommandType.SELECT_VEHICLE,
                spoken_response=v_msg,
                text_response=f"🚗 Vehicle mode switched to **{sel_v}**. Recalculating routes & updating 3D companion...",
                action_name="switch_vehicle_mode",
                ui_updates={
                    "selected_travel_mode": sel_v,
                    "cached_candidate_routes": None,
                    "routes_generated": True,
                    "virtual_guide_moving": False
                }
            )

        # ---------------------------------------------------------------------
        # 6. ROUTE OPTIMIZATION PRIORITIES & ALTERNATIVE ROUTES
        # ---------------------------------------------------------------------
        if re.search(r"\b(choose|select|set|switch\s+to)?\s*(the\s+)?(fastest\s+route|quickest\s+route|minimum\s+time|వేగవంతమైన|सबसे\s+तेज़)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.CHANGE_ROUTE_PRIORITY,
                spoken_response=resp_bundle["priority_fastest"],
                text_response="⚡ Selected **FASTEST ROUTE** (Minimum duration).",
                action_name="set_priority_fastest",
                ui_updates={"active_objective": "FASTEST", "routes_generated": True, "cached_candidate_routes": None}
            )

        if re.search(r"\b(choose|select|set|switch\s+to)?\s*(the\s+)?(shortest\s+route|minimum\s+distance|తక్కువ\s+దూరం|सबसे\s+छोटा)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.CHANGE_ROUTE_PRIORITY,
                spoken_response=resp_bundle["priority_shortest"],
                text_response="📏 Selected **SHORTEST ROUTE** (Minimum road distance).",
                action_name="set_priority_shortest",
                ui_updates={"active_objective": "SHORTEST", "routes_generated": True, "cached_candidate_routes": None}
            )

        if re.search(r"\b(choose|select|set|switch\s+to)?\s*(the\s+)?(balanced\s+route|optimal\s+route|సమతుల్య|संतुलित)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.CHANGE_ROUTE_PRIORITY,
                spoken_response=resp_bundle["priority_balanced"],
                text_response="⚖️ Selected **BALANCED ROUTE** (50/50 time & distance balance).",
                action_name="set_priority_balanced",
                ui_updates={"active_objective": "BALANCED", "routes_generated": True, "cached_candidate_routes": None}
            )

        if re.search(r"\b(choose|select|set|switch\s+to)?\s*(the\s+)?(accessible\s+route|step\s*free\s+route|wheelchair\s+route)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.CHANGE_ROUTE_PRIORITY,
                spoken_response=resp_bundle["priority_accessible"],
                text_response="♿ Selected **ACCESSIBLE ROUTE** (Step-free accessible corridors).",
                action_name="set_priority_accessible",
                ui_updates={"active_objective": "ACCESSIBLE", "routes_generated": True, "cached_candidate_routes": None}
            )

        if re.search(r"\b(show|display|find|view)\s+(me\s+)?(all\s+)?(alternative|other|all|available)\s+(alternative\s+|available\s+)?routes?\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.SHOW_ALTERNATIVE_ROUTES,
                spoken_response=resp_bundle["alt_routes_shown"],
                text_response=f"🗺️ {resp_bundle['alt_routes_shown']}",
                action_name="show_alternative_routes",
                ui_updates={"active_objective": "all", "routes_generated": True, "cached_candidate_routes": None}
            )

        if re.search(r"\b(recalculate\s+routes?|find\s+new\s+routes?|refresh\s+routes?|మళ్ళీ\s+లెక్కించు|रूट\s+रिफ्रेश)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.RECALCULATE_ROUTE,
                spoken_response="Recalculating all optimal routes across the road network.",
                text_response="⚡ Recalculating optimal road corridors...",
                action_name="recalculate_routes",
                ui_updates={"routes_generated": True, "cached_candidate_routes": None, "auto_fit_bounds": True}
            )

        # ---------------------------------------------------------------------
        # 7. 3D VIRTUAL GUIDE & COMPANION CONTROLS
        # ---------------------------------------------------------------------
        if re.search(r"\b(show|activate|enable|open)\s+(the\s+)?(3d\s+guide|3d\s+companion|virtual\s+guide|3d\s+mode|3d\s+cockpit)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.TOGGLE_3D_MODE,
                spoken_response=resp_bundle["3d_enabled"],
                text_response=f"🚗 {resp_bundle['3d_enabled']}",
                action_name="enable_3d_companion",
                ui_updates={"current_view": "virtual_guide", "companion_3d_mode": True, "enable_3d_companion": True}
            )

        if re.search(r"\b(switch\s+to\s+2\.?5d|2\.?5d\s+mode|top\s+down\s+view|disable\s+3d)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.TOGGLE_3D_MODE,
                spoken_response=resp_bundle["3d_disabled"],
                text_response=f"🗺️ {resp_bundle['3d_disabled']}",
                action_name="switch_2_5d_mode",
                ui_updates={"companion_3d_mode": False}
            )

        if re.search(r"\b(make\s+the\s+camera\s+follow|camera\s+follow|follow\s+(my\s+)?vehicle|lock\s+camera)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.CONTROL_3D_COMPANION,
                spoken_response=resp_bundle["camera_follow"],
                text_response=f"📹 {resp_bundle['camera_follow']}",
                action_name="camera_follow_vehicle",
                ui_updates={"companion_camera_follow": True}
            )

        # ---------------------------------------------------------------------
        # 8. MAP VIEW CONTROLS & CAMERA STYLES
        # ---------------------------------------------------------------------
        if re.search(r"\b(fit\s+(?:the\s+)?(?:entire\s+|whole\s+|full\s+)?route|fit\s+bounds|show\s+full\s+route|show\s+whole\s+route|zoom\s+to\s+route|మొత్తం\s+రూట్|पूरा\s+रूट)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.FIT_MAP,
                spoken_response=resp_bundle["route_fitted"],
                text_response=f"🔍 {resp_bundle['route_fitted']}",
                action_name="fit_route_bounds",
                ui_updates={"auto_fit_bounds": True, "scroll_to_app_map": True}
            )

        if re.search(r"\b(zoom\s+in|magnify\s+map|closer\s+view)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.ZOOM_MAP,
                spoken_response="Zooming in on map view, Boss.",
                text_response="🔍 Zooming in...",
                action_name="zoom_in",
                ui_updates={"map_zoom_delta": 1, "scroll_to_app_map": True}
            )

        if re.search(r"\b(zoom\s+out|wider\s+view)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.ZOOM_MAP,
                spoken_response="Zooming out for broader overview, Boss.",
                text_response="🔍 Zooming out...",
                action_name="zoom_out",
                ui_updates={"map_zoom_delta": -1, "scroll_to_app_map": True}
            )

        if re.search(r"\b(switch\s+to\s+satellite|satellite\s+view|satellite\s+mode|satellite\s+map|శాటిలైట్)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.MAP_STYLE,
                spoken_response=resp_bundle["satellite_switched"],
                text_response=f"🛰️ {resp_bundle['satellite_switched']}",
                action_name="set_map_satellite",
                ui_updates={"map_engine": "google_satellite", "map_style": "satellite_hybrid", "scroll_to_app_map": True}
            )

        if re.search(r"\b(switch\s+to\s+(roadmap|road\s+map|vector\s+map|normal\s+view)|roadmap\s+view|రోడ్‌మ్యాప్)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.MAP_STYLE,
                spoken_response=resp_bundle["roadmap_switched"],
                text_response=f"🗺️ {resp_bundle['roadmap_switched']}",
                action_name="set_map_roadmap",
                ui_updates={"map_engine": "google_roadmap", "map_style": "google_maps_road", "scroll_to_app_map": True}
            )

        if re.search(r"\b(switch\s+to\s+terrain|terrain\s+view|topography|టెర్రైన్)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.MAP_STYLE,
                spoken_response=resp_bundle["terrain_switched"],
                text_response=f"⛰️ {resp_bundle['terrain_switched']}",
                action_name="set_map_terrain",
                ui_updates={"map_engine": "google_terrain", "map_style": "terrain", "scroll_to_app_map": True}
            )

        # ---------------------------------------------------------------------
        # 9. TRAVEL MODULES (HOTELS, FLIGHTS, RESTAURANTS, MY TRIPS, PROFILE)
        # ---------------------------------------------------------------------
        # 9.0 Travel Tools / Expense & Fuel Estimation
        if re.search(r"\b(calculate\s+fuel|fuel\s+expense|fuel\s+cost|trip\s+budget|travel\s+expense|estimate\s+cost|ఖర్చు|लागत)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.TRAVEL_TOOL,
                spoken_response="Opening travel expense and fuel calculator, Boss.",
                text_response="⛽ Opening fuel expense and travel cost calculator.",
                action_name="open_travel_tool_fuel",
                ui_updates={"current_view": "copilot_studio", "target_tab": "tools", "tool_tab": "fuel"}
            )

        # 9.0b Facilities / Hospitals / Emergency / Fuel / Police
        if re.search(r"\b(?:(?:find|show|open|search\s+for|nearby)\s+)?(hospitals?|clinics?|medical|doctors?|pharmacy|emergency|police\s+station|fuel\s+station|petrol\s+pump|gas\s+station|ఆసుపత్రి|अस्पताल)\b|\bnearby\s+(?:police|fuel|petrol)\b", q_lower):
            fac_filter = "health"
            if re.search(r"police", q_lower):
                fac_filter = "police"
            elif re.search(r"fuel|petrol|gas|diesel", q_lower):
                fac_filter = "fuel"
            return AuraExecutionResult(
                command_type=AuraCommandType.FACILITY_SEARCH,
                spoken_response="Displaying nearby facilities on map.",
                text_response=f"🏥 Displaying nearby {fac_filter} facilities.",
                action_name="filter_facility_search",
                ui_updates={
                    "current_view": "map_nav",
                    "target_tab": "facilities",
                    "facility_filter": fac_filter,
                    "show_emergency_amenities_on_map": True,
                    "scroll_to_app_map": True
                }
            )

        # 9.1 Hotels
        if re.search(r"\b(find|show|open|search\s+for)?\s*(nearby\s+)?(hotels?|lodges?|resorts?|stay|accommodation|హోటల్|होटल)\b", q_lower):
            price_match = re.search(r"(?:under|below|less than)\s+(\d+)", q_lower)
            p_val = int(price_match.group(1)) if price_match else None
            h_resp = resp_bundle["hotels_opened"]
            ui_u: Dict[str, Any] = {
                "current_view": "map_nav",
                "target_tab": "facilities",
                "facility_filter": "hotel",
                "show_emergency_amenities_on_map": True,
                "scroll_to_app_map": True
            }
            if p_val:
                ui_u["hotel_max_price"] = p_val
            return AuraExecutionResult(
                command_type=AuraCommandType.SEARCH_HOTEL,
                spoken_response=h_resp,
                text_response=f"🏨 {h_resp}",
                action_name="filter_facility_hotel",
                ui_updates=ui_u
            )

        # 9.2 Flights
        if re.search(r"\b(open|show|find|book)?\s*(the\s+)?(flights?|flight\s+planner|aviation|airplanes?|air\s+travel|ఫ్లైట్స్|उडान)\b", q_lower):
            fl_resp = resp_bundle["flights_opened"]
            return AuraExecutionResult(
                command_type=AuraCommandType.SEARCH_FLIGHT,
                spoken_response=fl_resp,
                text_response=f"✈️ {fl_resp}",
                action_name="switch_travel_flights",
                ui_updates={"current_view": "copilot_studio", "selected_travel_mode": "FLIGHT", "transit_mode": "FLIGHT"}
            )

        # 9.3 Restaurants & Dining
        if re.search(r"\b(show|find|open|search\s+for)?\s*(nearby\s+)?(restaurants?|food|cafes?|dining|vegetarian|భోజనం|रेस्टोरेंट)\b", q_lower):
            r_resp = resp_bundle["restaurants_opened"]
            return AuraExecutionResult(
                command_type=AuraCommandType.SEARCH_RESTAURANT,
                spoken_response=r_resp,
                text_response=f"🍽️ {r_resp}",
                action_name="filter_facility_food",
                ui_updates={
                    "current_view": "map_nav",
                    "target_tab": "facilities",
                    "facility_filter": "food",
                    "show_emergency_amenities_on_map": True,
                    "scroll_to_app_map": True
                }
            )

        # 9.4 My Trips / Itinerary Studio / Bookings
        if re.search(r"\b(open|show|go\s+to|view)\s+(my\s+)?(trips?|itinerar(?:y|ies)|travel\s+studio|copilot\s+studio|bookings?|ట్రిప్స్|यात्राएं)\b", q_lower):
            tr_resp = resp_bundle["trips_opened"]
            return AuraExecutionResult(
                command_type=AuraCommandType.OPEN_MY_TRIPS,
                spoken_response=tr_resp,
                text_response=f"✨ {tr_resp}",
                action_name="switch_view_copilot_studio",
                ui_updates={"current_view": "copilot_studio"}
            )

        # 9.5 Save Active Trip
        if re.search(r"\b(save\s+(this\s+)?trip|save\s+(my\s+)?journey|save\s+route|సేవ్\s+చేయి|सुरक्षित\s+करो)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.SAVE_TRIP,
                spoken_response=resp_bundle["trip_saved"],
                text_response=f"💾 {resp_bundle['trip_saved']}",
                action_name="save_active_trip",
                ui_updates={"trigger_save_active_trip": True}
            )

        # 9.6 Saved Places / Bookmarks
        if re.search(r"\b(open\s+saved\s+places|saved\s+locations|my\s+bookmarks|show\s+saved|open\s+places|show\s+places)\b", q_lower):
            pl_resp = resp_bundle["places_opened"]
            return AuraExecutionResult(
                command_type=AuraCommandType.SEARCH_SAVED_LOCATIONS,
                spoken_response=pl_resp,
                text_response=f"⭐ {pl_resp}",
                action_name="switch_view_places",
                ui_updates={"current_view": "places", "target_tab": "places"}
            )

        # 9.7 Profile & Travel Preferences
        if re.search(r"\b(go\s+to|open|show|view)?\s*(my\s+)?(profile|account|user\s+profile|travel\s+preferences|ప్రొఫైల్|प्रोफाइल)\b", q_lower):
            pr_resp = resp_bundle["profile_opened"]
            return AuraExecutionResult(
                command_type=AuraCommandType.OPEN_PROFILE,
                spoken_response=pr_resp,
                text_response=f"👤 {pr_resp}",
                action_name="open_user_profile",
                ui_updates={"current_view": "dashboard", "show_user_profile_modal": True, "scroll_to_profile": True}
            )

        # ---------------------------------------------------------------------
        # 10. APPLICATION SETTINGS, LANGUAGE, & THEME CONTROLS
        # ---------------------------------------------------------------------
        # 10.1 Language Switch: "Switch to Telugu" / "Change language to Hindi"
        lang_match = re.search(r"\b(?:switch|change|set)\s+(?:the\s+)?(?:app(?:lication)?\s+)?language\s+(?:to\s+)?(english|telugu|hindi|tamil|kannada|malayalam|bengali|bangla|marathi)\b", q_lower)
        if not lang_match:
            lang_match = re.search(r"\b(?:switch|change)\s+to\s+(english|telugu|hindi|tamil|kannada|malayalam|bengali|bangla|marathi)\b", q_lower)
        if lang_match:
            raw_lang_name = lang_match.group(1).lower()
            target_code = cls.LANGUAGE_NAME_MAP.get(raw_lang_name, "en")
            # Multilingual confirmation in target language
            t_bundle = cls.RESPONSES.get(target_code, cls.RESPONSES["en"])
            lang_display = raw_lang_name.title()
            conf_msg = t_bundle["lang_switched"].format(lang=lang_display)
            return AuraExecutionResult(
                command_type=AuraCommandType.SET_APPLICATION_LANGUAGE,
                spoken_response=conf_msg,
                text_response=f"🌐 {conf_msg}",
                action_name="set_application_language",
                ui_updates={"app_language": target_code}
            )

        # 10.2 Theme Control: Dark / Light Mode
        if re.search(r"\b(enable\s+dark\s+mode|switch\s+to\s+dark\s+mode|dark\s+theme|dark\s+mode)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.SET_THEME,
                spoken_response=resp_bundle["theme_dark"],
                text_response=f"🌙 {resp_bundle['theme_dark']}",
                action_name="set_theme_dark",
                ui_updates={"app_theme": "dark", "theme": "dark"}
            )

        if re.search(r"\b(enable\s+light\s+mode|switch\s+to\s+light\s+mode|light\s+theme|light\s+mode)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.SET_THEME,
                spoken_response=resp_bundle["theme_light"],
                text_response=f"☀️ {resp_bundle['theme_light']}",
                action_name="set_theme_light",
                ui_updates={"app_theme": "light", "theme": "light"}
            )

        # 10.3 Avoid Tolls & Highways
        if re.search(r"\b(avoid\s+tolls?|toll\s+free|no\s+tolls?)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.UPDATE_SETTING,
                spoken_response="Toll avoidance enabled. Rerouting via toll-free corridors.",
                text_response="🚫 Toll avoidance active. Updating routes...",
                action_name="toggle_avoid_tolls",
                ui_updates={"avoid_tolls": True, "routes_generated": True, "cached_candidate_routes": None}
            )

        if re.search(r"\b(avoid\s+highways?|no\s+highways?)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.UPDATE_SETTING,
                spoken_response="Highway avoidance enabled. Calculating alternate roads.",
                text_response="🛣️ Highway avoidance active. Updating routes...",
                action_name="toggle_avoid_highways",
                ui_updates={"avoid_highways": True, "routes_generated": True, "cached_candidate_routes": None}
            )

        # 10.4 General Settings / Preferences
        if re.search(r"\b(open\s+settings|app\s+settings|preferences|voice\s+settings|సెట్టింగ్స్|सेटिंग्स)\b", q_lower):
            s_resp = resp_bundle["settings_opened"]
            return AuraExecutionResult(
                command_type=AuraCommandType.OPEN_MODULE,
                spoken_response=s_resp,
                text_response=f"⚙️ {s_resp}",
                action_name="open_settings",
                ui_updates={"current_view": "dashboard", "show_user_profile_modal": True, "scroll_to_profile": True}
            )

        # 10.5 Navigation Back / Return Home
        if re.search(r"\b(go\s+back|back\s+button|previous\s+(?:view|screen|page)|వెనుకకు|पीछे)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.CLOSE_MODULE,
                spoken_response=resp_bundle["back_opened"],
                text_response=f"↩️ {resp_bundle['back_opened']}",
                action_name="navigate_go_back",
                ui_updates={"trigger_go_back": True}
            )

        if re.search(r"\b(go\s+home|home\s+dashboard|return\s+home|main\s+dashboard|హోమ్|होम)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.SWITCH_PAGE,
                spoken_response=resp_bundle["home_opened"],
                text_response=f"🏠 {resp_bundle['home_opened']}",
                action_name="navigate_home",
                ui_updates={"current_view": "dashboard", "target_tab": "nav"}
            )

        # ---------------------------------------------------------------------
        # 11. VOICE SESSION CONTROLS
        # ---------------------------------------------------------------------
        if re.search(r"\b(pause(\s+the)?\s*(?:assistant|voice|listening)?|hold\s+on|విరామం|रोकिए)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.VOICE_CONTROL,
                spoken_response="Voice session paused. Click resume or speak when ready, Boss.",
                text_response="⏸️ Voice session paused.",
                action_name="pause_voice_session",
                ui_updates={"aura_voice_session_state": "PAUSED"}
            )

        if re.search(r"\b(resume\s+voice|resume\s+listening|continue\s+listening)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.VOICE_CONTROL,
                spoken_response="Voice session resumed. I am listening, Boss.",
                text_response="🎙️ Voice session resumed.",
                action_name="resume_voice_session",
                ui_updates={"aura_voice_session_state": "LISTENING"}
            )

        if re.search(r"\b(end\s+voice|stop\s+voice|aura\s+offline|close\s+assistant|ఆపండి|बंद\s+करें)\b", q_lower):
            return AuraExecutionResult(
                command_type=AuraCommandType.VOICE_CONTROL,
                spoken_response="Voice session ended. AURA is offline. Safe travels, Boss.",
                text_response="⏹️ Voice session ended. AURA offline.",
                action_name="end_voice_session",
                ui_updates={"aura_voice_session_state": "STOPPED"}
            )

        # ---------------------------------------------------------------------
        # 12. FALLBACK: DELEGATE TO CHATBOT TRAVEL ADVICE
        # ---------------------------------------------------------------------
        return AuraExecutionResult(
            command_type=AuraCommandType.GENERAL_TRAVEL_QUESTION,
            spoken_response=f"Checking with AURA travel assistant regarding: {q[:35]}...",
            text_response=f"💬 Asking AURA Travel Copilot: *\"{q}\"*",
            action_name="delegate_to_chat_turn",
            ui_updates={"pending_chat_prompt": q}
        )

    # -------------------------------------------------------------------------
    # MULTI-ACTION PIPELINE & DEPENDENCY ORDERING ENGINE
    # -------------------------------------------------------------------------
    @classmethod
    def _detect_and_handle_multi_action(
        cls,
        raw_query: str,
        q_lower: str,
        ctx: Dict[str, Any],
        lang: str
    ) -> Optional[AuraExecutionResult]:
        """
        Detects if the query contains multiple actions and chains them in dependency order:
        Dependency Order:
          1. Origin resolution (SET_ORIGIN)
          2. Destination resolution (SET_DESTINATION)
          3. Transportation Mode (SELECT_VEHICLE)
          4. Route Priority / Objective (CHANGE_ROUTE_PRIORITY)
          5. Recalculate routes
          6. Start Navigation (START_NAVIGATION) & 3D Companion synchronization
        """
        actions_found: List[str] = []
        ui_updates: Dict[str, Any] = {}
        confirmations: List[str] = []
        action_records: List[Dict[str, Any]] = []

        # 1. Origin Detection
        orig_match = re.search(r"\b(?:set\s+(?:my\s+)?(?:start(?:ing)?(?:\s+point|\s+location)?|origin)\s+to|start\s+from|from|ప్రారంభ\s*స్థానం|శూరువాతి\s*స్థాన్|शुरुआती\s*स्थान)\s+([a-zA-Z\s\u0C00-\u0C7F\u0900-\u097F]+?)(?:\s*[,.]|\s+destination|\s+and|\s+change|\s+select|\s+choose|\s+start|\s+గమ్యస్థానం|\s+గమ్యం|\s+డెస్టినేషన్|\s+गंतव्य|\s+मंजिल|\s+और|\s+तथा|\s+మరియు|$)", raw_query, re.IGNORECASE)
        if orig_match:
            orig_raw = orig_match.group(1).strip()
            if orig_raw.lower() not in ["here", "my location", "current location"]:
                geo_o = cls.resolve_location(orig_raw)
                o_label = geo_o["display_name"] if geo_o else orig_raw.title()
                o_coords = (geo_o["lat"], geo_o["lon"]) if geo_o else None
                ui_updates.update({
                    "user_live_coords": o_coords,
                    "user_live_label": o_label,
                    "pending_orig": o_label,
                    "txt_orig": o_label,
                    "is_custom_start_place": True
                })
                actions_found.append("origin")
                confirmations.append(f"Starting point {o_label}")
                action_records.append({"action": "SET_ORIGIN", "value": o_label, "coords": o_coords})

        # 2. Destination Detection
        dest_match = re.search(r"\b(?:set\s+(?:my\s+)?destination\s+to|destination\s+to|navigate\s+to|take\s+me\s+to|drive\s+to|గమ్యస్థానం|గమ్యం|డెస్టినేషన్|డెస్టినేషన్\s+గా|गंतव्य|मंजिल|இலக்கு)\s+([a-zA-Z\s\u0C00-\u0C7F\u0900-\u097F]+?)(?:\s*[,.]|\s+change|\s+select|\s+choose|\s+and|\s+start|\s+సెట్|\s+చేసి|\s+కారు|\s+బైక్|\s+కార్|\s+सेट|\s+करो|\s+कार|\s+बाइक|\s+और|$)", raw_query, re.IGNORECASE)
        if not dest_match and not orig_match:
            dest_match = re.search(r"\b(?:go\s+to|travel\s+to)\s+([a-zA-Z\s\u0C00-\u0C7F\u0900-\u097F]+?)(?:\s*[,.]|\s+change|\s+select|\s+choose|\s+and|\s+start|\s+సెట్|\s+చేసి|\s+కారు|\s+బైక్|\s+కార్|\s+सेट|\s+करो|\s+कार|\s+बाइक|\s+और|$)", raw_query, re.IGNORECASE)
        if dest_match:
            dest_raw = dest_match.group(1).strip()
            dest_words = set(dest_raw.lower().split())
            is_veh = any(w in cls.VEHICLE_MODE_MAP for w in dest_words) or (dest_raw.lower() in cls.VEHICLE_MODE_MAP)
            if not is_veh and dest_raw.lower() not in ["navigation", "fastest", "shortest", "balanced"]:
                geo_d = cls.resolve_location(dest_raw)
                d_label = geo_d["display_name"] if geo_d else dest_raw.title()
                d_coords = (geo_d["lat"], geo_d["lon"]) if geo_d else None
                ui_updates.update({
                    "selected_dest_coords": d_coords,
                    "selected_dest_label": d_label,
                    "pending_dest": d_label,
                    "txt_dest": d_label,
                    "active_trip_destination": d_label
                })
                actions_found.append("destination")
                confirmations.append(f"destination {d_label}")
                action_records.append({"action": "SET_DESTINATION", "value": d_label, "coords": d_coords})

        # 3. Vehicle Mode Detection
        veh_match = re.search(r"(?:change|switch|set|select)?\s*(?:my\s+)?(?:vehicle|transport)?\s*(?:mode\s+to|to\s+mode|to)?\s*(?:\b|^|\s)(car|bike|motorcycle|bus|cycle|bicycle|walk|pedestrian|truck|tractor|flight|plane|train|ship|కారు|కార్|బైక్|బస్సు|నడక|సైకిల్|విమానం|రైలు|कार|बाइक|बस|पैदल|साइकिल|विमान|ट्रेन)(?:\b|$|\s|[,.])", q_lower)
        if veh_match:
            raw_v = veh_match.group(1).lower()
            sel_v = cls.VEHICLE_MODE_MAP.get(raw_v, "CAR")
            ui_updates["selected_travel_mode"] = sel_v
            actions_found.append("vehicle")
            confirmations.append(f"{sel_v.title()} mode")
            action_records.append({"action": "SELECT_VEHICLE", "value": sel_v})

        # 4. Route Priority / Objective Detection
        if re.search(r"(fastest\s+route|fastest|quickest|minimum\s+time|ఫాస్టెస్ట్|వేగవంతమైన|सबसे\s+तेज़|വേഗതയേറിയ|வேகமான)", q_lower):
            ui_updates["active_objective"] = "FASTEST"
            actions_found.append("priority")
            confirmations.append("fastest route")
            action_records.append({"action": "CHANGE_ROUTE_PRIORITY", "value": "FASTEST"})
        elif re.search(r"(shortest\s+route|shortest|minimum\s+distance|షార్టెస్ట్|తక్కువ\s+దూరం|सबसे\s+छोटा|കുറഞ്ഞ\s+ദൂരം|குறுகிய)", q_lower):
            ui_updates["active_objective"] = "SHORTEST"
            actions_found.append("priority")
            confirmations.append("shortest route")
            action_records.append({"action": "CHANGE_ROUTE_PRIORITY", "value": "SHORTEST"})
        elif re.search(r"(balanced\s+route|balanced|సమతుల్య|संतुलित)", q_lower):
            ui_updates["active_objective"] = "BALANCED"
            actions_found.append("priority")
            confirmations.append("balanced route")
            action_records.append({"action": "CHANGE_ROUTE_PRIORITY", "value": "BALANCED"})

        # 5. Navigation Start Detection
        if re.search(r"(start\s+navigation|begin\s+navigation|start\s+driving|let's\s+go|నావిగేషన్|ప్రారంభించు|ప్రారంభించండి|మొదలుపెట్టు|నేవిగేషన్|नेविगेशन\s*शुरू|வழிசெலுத்தலை\s+தொடங்கு|ನ್ಯಾವಿಗೇಷನ್\s+ಪ್ರಾರಂಭಿಸಿ)", q_lower):
            actions_found.append("start_navigation")

        # Must have at least 2 distinct actions to qualify as a multi-action sequence
        if len(actions_found) < 2:
            return None

        # Always trigger route recalculation and map synchronization
        ui_updates.update({
            "current_view": "map_nav",
            "target_tab": "nav",
            "routes_generated": True,
            "cached_candidate_routes": None,
            "auto_fit_bounds": True,
            "scroll_to_app_map": True
        })

        # Validate Navigation Start Dependency
        if "start_navigation" in actions_found:
            has_dest = bool(ui_updates.get("selected_dest_coords") or ctx.get("dest_coords") or ctx.get("dest_label"))
            if has_dest:
                ui_updates.update({
                    "aura_journey_active": True,
                    "virtual_guide_moving": True,
                    "gps_tracking_active": True,
                    "user_speed_kmh": 4.8,
                    "companion_3d_mode": True,
                    "enable_3d_companion": True
                })
                confirmations.append("starting navigation")
                action_records.append({"action": "START_NAVIGATION", "status": "ACTIVE"})
            else:
                confirmations.append("destination required before starting navigation")
                action_records.append({"action": "START_NAVIGATION", "status": "FAILED_MISSING_DESTINATION"})

        # Assemble unified confirmation message
        chain_summary = ", ".join(confirmations)
        if lang == "te":
            spoken_text = f"{chain_summary} విజయవంతంగా సెట్ చేసి నావిగేషన్ ప్రారంభించాను, బాస్."
        elif lang == "hi":
            spoken_text = f"{chain_summary} सेट कर दिया गया है और नेविगेशन शुरू है, बॉस।"
        elif lang == "ta":
            spoken_text = f"{chain_summary} அமைக்கப்பட்டு வழிசெலுத்தல் தொடங்கப்பட்டது, பாஸ்."
        elif lang == "kn":
            spoken_text = f"{chain_summary} ಹೊಂದಿಸಿ ನ್ಯಾವಿಗೇಷನ್ ಪ್ರಾರಂಭಿಸಲಾಗಿದೆ, ಬಾಸ್."
        else:
            spoken_text = f"Executing actions: {chain_summary}. Safe journey, Boss!"

        formatted_text = f"⚡ **Multi-Action Sequence Executed:**\n\n" + "\n".join([f"• {act['action']}: `{act.get('value', act.get('status'))}`" for act in action_records])

        return AuraExecutionResult(
            command_type=AuraCommandType.MULTI_ACTION_SEQUENCE,
            spoken_response=spoken_text,
            text_response=formatted_text,
            action_name="execute_multi_action_sequence",
            ui_updates=ui_updates,
            success=True,
            actions_executed=action_records
        )

    # -------------------------------------------------------------------------
    # STATE APPLICATION & UI SYNCHRONIZATION
    # -------------------------------------------------------------------------
    @classmethod
    def apply_execution_result(cls, result: AuraExecutionResult, session_state: Any) -> None:
        """
        Applies all UI state mutations safely to streamlit's session_state.
        Synchronizes views, endpoints, vehicles, routing, and 3D companion without DOM manipulation.
        """
        # Maintain navigation view history for "Go back"
        if "view_history" not in session_state:
            session_state["view_history"] = ["dashboard"]

        cur_view = session_state.get("current_view", "dashboard")
        if not session_state["view_history"] or session_state["view_history"][-1] != cur_view:
            session_state["view_history"].append(cur_view)

        # Handle Go Back action
        if result.ui_updates.get("trigger_go_back"):
            history = session_state.get("view_history", [])
            if len(history) > 1:
                history.pop()  # Pop current
                session_state["current_view"] = history[-1]
            else:
                session_state["current_view"] = "dashboard"
            return

        # Handle Swap Endpoints action
        if result.ui_updates.get("trigger_swap_endpoints"):
            old_orig_coords = session_state.get("user_live_coords")
            old_orig_label = session_state.get("user_live_label", "")
            old_dest_coords = session_state.get("selected_dest_coords")
            old_dest_label = session_state.get("selected_dest_label", "")

            session_state["user_live_coords"] = old_dest_coords
            session_state["user_live_label"] = old_dest_label
            session_state["pending_orig"] = old_dest_label
            session_state["txt_orig"] = old_dest_label
            session_state["is_custom_start_place"] = True

            session_state["selected_dest_coords"] = old_orig_coords
            session_state["selected_dest_label"] = old_orig_label
            session_state["pending_dest"] = old_orig_label
            session_state["txt_dest"] = old_orig_label

            session_state["routes_generated"] = bool(old_dest_coords and old_orig_coords)
            session_state["cached_candidate_routes"] = None

        # Apply all other UI updates
        for k, v in result.ui_updates.items():
            if k in ["trigger_go_back", "trigger_swap_endpoints"]:
                continue
            session_state[k] = v

        # If origin coords were updated, update real_location_service as well
        if "user_live_coords" in result.ui_updates and result.ui_updates["user_live_coords"]:
            c_coords = result.ui_updates["user_live_coords"]
            c_label = result.ui_updates.get("user_live_label", "Starting Point")
            if "real_location_service" in session_state and hasattr(session_state["real_location_service"], "set_manual_location"):
                try:
                    session_state["real_location_service"].set_manual_location(c_coords[0], c_coords[1], c_label)
                except Exception as e_loc:
                    logger.warning("Could not set manual location on LocationService: %s", e_loc)

        # Update view history if view changed
        if result.ui_updates.get("current_view"):
            new_v = result.ui_updates["current_view"]
            if not session_state["view_history"] or session_state["view_history"][-1] != new_v:
                session_state["view_history"].append(new_v)

        # Switch to Navigation / Map Section
        if result.ui_updates.get("target_tab") in ["nav", "facilities"]:
            session_state["current_view"] = "map_nav"
            session_state["switch_to_nav_tab"] = True
