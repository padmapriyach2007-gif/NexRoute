"""
NexRoute — AURA Global Jarvis-Style Voice Command Dispatcher & Intelligent Controller
Translates natural-language voice & text commands into real application actions,
map controls, route planning, nearby search, facility filters, and conversational intelligence.
Supports English, Telugu, Hindi, Tamil, Kannada, Malayalam, and mixed colloquial phrasing.
"""

import re
import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("nexroute.aura_dispatcher")


class AuraCommandType(str, Enum):
    NAVIGATE_TAB = "NAVIGATE_TAB"
    MAP_STYLE = "MAP_STYLE"
    MAP_ACTION = "MAP_ACTION"
    ROUTE_ACTION = "ROUTE_ACTION"
    FACILITY_SEARCH = "FACILITY_SEARCH"
    TRAVEL_TOOL = "TRAVEL_TOOL"
    VOICE_CONTROL = "VOICE_CONTROL"
    GENERAL_CHAT = "GENERAL_CHAT"
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
        success: bool = True
    ):
        self.command_type = command_type
        self.spoken_response = spoken_response
        self.text_response = text_response
        self.action_name = action_name
        self.ui_updates = ui_updates or {}
        self.requires_confirmation = requires_confirmation
        self.confirmation_prompt = confirmation_prompt
        self.success = success

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command_type": self.command_type.value,
            "spoken_response": self.spoken_response,
            "text_response": self.text_response,
            "action_name": self.action_name,
            "ui_updates": self.ui_updates,
            "requires_confirmation": self.requires_confirmation,
            "confirmation_prompt": self.confirmation_prompt,
            "success": self.success
        }


class AuraGlobalCommandDispatcher:
    """
    Central JARVIS-style Command Dispatcher for NexRoute.
    Processes natural voice commands, determines intent, and executes real application changes.
    """

    # Multilingual response templates (short, concise, natural Jarvis responses)
    RESPONSES = {
        "en": {
            "welcome": "Good morning, Boss! Welcome to NextRoute. How can I help you?",
            "nav_opened": "Opening navigation.",
            "trips_opened": "Here are your trips.",
            "bookings_opened": "Opening your bookings.",
            "hotels_opened": "Let's find hotels.",
            "flights_opened": "Opening flight planner.",
            "restaurants_opened": "Finding nearby restaurants.",
            "profile_opened": "Opening your profile.",
            "settings_opened": "Opening settings.",
            "back_opened": "Going back.",
            "home_opened": "Returning to home dashboard.",
            "chat_opened": "AURA chatbot is ready.",
            "facilities_opened": "Showing nearby emergency and travel amenities.",
            "places_opened": "Opening saved places.",
            "guide_opened": "Opening virtual guide.",
            "satellite_switched": "Switched to satellite view.",
            "roadmap_switched": "Switched to roadmap view.",
            "terrain_switched": "Switched to terrain view.",
            "gps_centered": "Locating your current coordinates.",
            "route_fitted": "Adjusting camera to frame route.",
            "dest_cleared": "Destination has been cleared.",
            "orig_cleared": "Starting point reset to live GPS.",
            "swapped": "Start and destination reversed.",
            "facility_found": "Locating {category} around your route corridor.",
            "fuel_tool": "Opening fuel calculations.",
            "confirm_clear_route": "Boss, are you sure you want to clear your active route?",
            "unrecognized": "Processing your query: \"{query}\".",
        },
        "te": {
            "welcome": "నమస్కారం, బాస్! నెక్స్‌రూట్‌కి స్వాగతం. నేను మీకు ఎలా సహాయపడగలను?",
            "nav_opened": "నావిగేషన్ తెరవబడింది.",
            "trips_opened": "మీ ట్రిప్స్ ఇక్కడ ఉన్నాయి.",
            "bookings_opened": "మీ బుకింగ్స్ తెరవబడ్డాయి.",
            "hotels_opened": "హోటళ్లు వెతుకుతున్నాను.",
            "flights_opened": "ఫ్లైట్ ప్లానర్ తెరుస్తున్నాను.",
            "restaurants_opened": "రెస్టారెంట్లు వెతుకుతున్నాను.",
            "profile_opened": "మీ ప్రొఫైల్ తెరవబడింది.",
            "settings_opened": "సెట్టింగ్స్ తెరవబడ్డాయి.",
            "back_opened": "వెనుకకు వెళ్తున్నాను.",
            "home_opened": "హోమ్ డ్యాష్‌బోర్డ్‌కి తిరిగి వెళ్తున్నాను.",
            "chat_opened": "AURA AI చాట్‌బాట్ సిద్ధంగా ఉంది, బాస్.",
            "facilities_opened": "సమీప అత్యవసర మరియు ప్రయాణ సౌకర్యాలు చూపిస్తున్నాను.",
            "places_opened": "సేవ్ చేసిన ప్రదేశాలు తెరవబడ్డాయి.",
            "guide_opened": "వర్చువల్ గైడ్ తెరవబడింది.",
            "satellite_switched": "శాటిలైట్ హైబ్రిడ్ వీక్షణకు మార్చబడింది.",
            "roadmap_switched": "రోడ్‌మ్యాప్ వీక్షణకు మార్చబడింది.",
            "terrain_switched": "టెర్రైన్ వీక్షణకు మార్చబడింది.",
            "gps_centered": "మీ ప్రస్తుత లైవ్ లొకేషన్‌ను గుర్తిస్తున్నాను.",
            "route_fitted": "మొత్తం రూట్ కనిపించేలా మ్యాప్ సర్దుబాటు చేశాను.",
            "dest_cleared": "గమ్యస్థానం క్లియర్ చేయబడింది.",
            "orig_cleared": "ప్రారంభ స్థానం లైవ్ GPS కి రీసెట్ చేయబడింది.",
            "swapped": "ప్రారంభ స్థానం మరియు గమ్యస్థానం మార్చబడ్డాయి.",
            "facility_found": "సమీపంలోని {category} వెతుకుతున్నాను.",
            "fuel_tool": "ఇంధనం మరియు టోల్ ఖర్చుల కాలిక్యులేటర్ తెరుస్తున్నాను.",
            "confirm_clear_route": "బాస్, మీరు నిజంగానే ఈ రూట్ క్లియర్ చేయాలనుకుంటున్నారా?",
            "unrecognized": "నేను విన్నాను: \"{query}\".",
        },
        "hi": {
            "welcome": "नमस्ते, बॉस! नेक्स्ट-रूट में आपका स्वागत है। मैं आपकी क्या मदद कर सकता हूँ?",
            "nav_opened": "नेविगेशन खोला जा रहा है।",
            "trips_opened": "ये रही आपकी यात्राएं।",
            "bookings_opened": "आपकी बुकिंग्स खोली जा रही हैं।",
            "hotels_opened": "होटल ढूंढे जा रहे हैं।",
            "flights_opened": "फ्लाइट प्लानर खोला जा रहा है।",
            "restaurants_opened": "रेस्टोरेंट ढूंढे जा रहे हैं।",
            "profile_opened": "आपकी प्रोफाइल खोली जा रही है।",
            "settings_opened": "सेटिंग्स खोली जा रही हैं।",
            "back_opened": "पीछे जा रहे हैं।",
            "home_opened": "होम डैशबोर्ड पर लौट रहे हैं।",
            "chat_opened": "AURA AI चैटबॉट तैयार है, बॉस।",
            "facilities_opened": "आस-पास की सुविधाएं दिखाई जा रही हैं।",
            "places_opened": "सहेजे गए स्थान खोले जा रहे हैं।",
            "guide_opened": "वर्चुअल गाइड खोला जा रहा है।",
            "satellite_switched": "सैटेलाइट दृश्य पर स्विच कर दिया गया है।",
            "roadmap_switched": "रोडमैप दृश्य पर स्विच कर दिया गया है।",
            "terrain_switched": "टेरेन दृश्य पर स्विच किया गया है।",
            "gps_centered": "आपकी वर्तमान लोकेशन पर मैप केंद्रित किया जा रहा है।",
            "route_fitted": "मार्ग मैप पर फ़िट कर दिया गया है।",
            "dest_cleared": "गंतव्य स्थान हटा दिया गया है।",
            "orig_cleared": "शुरुआती बिंदु लाइव GPS पर रीसेट किया गया है।",
            "swapped": "शुरुआत और गंतव्य स्थान आपस में बदल दिए गए हैं।",
            "facility_found": "निकटवर्ती {category} खोजे जा रहे हैं।",
            "fuel_tool": "ईंधन और टोल खर्च की गणना खोली जा रही है।",
            "confirm_clear_route": "बॉस, क्या आप वाकई सक्रिय मार्ग को हटाना चाहते हैं?",
            "unrecognized": "मैंने सुना: \"{query}\"।",
        },
        "ta": {
            "welcome": "வணக்கம், பாஸ்! நெக்ஸ்-ரூட்டிற்கு நல்வரவு. நான் உங்களுக்கு எப்படி உதவ முடியும்?",
            "nav_opened": "வழிசெலுத்தல் திறக்கப்படுகிறது.",
            "trips_opened": "உங்கள் பயணங்கள் இங்கே உள்ளன.",
            "bookings_opened": "உங்கள் முன்பதிவுகள் திறக்கப்படுகின்றன.",
            "hotels_opened": "விடுதிகள் தேடப்படுகின்றன.",
            "flights_opened": "விமான திட்டமிடுபவர் திறக்கப்படுகிறது.",
            "restaurants_opened": "உணவகங்கள் தேடப்படுகின்றன.",
            "profile_opened": "உங்கள் சுயவிவரம் திறக்கப்படுகிறது.",
            "settings_opened": "அமைப்புகள் திறக்கப்படுகின்றன.",
            "back_opened": "பின்செல்கிறது.",
            "home_opened": "முகப்புத் திரைக்கு திரும்புகிறது.",
            "chat_opened": "AURA AI சாட்பாட் தயாராக உள்ளது, பாஸ்.",
            "facilities_opened": "அருகிலுள்ள அவசர வசதிகள் காட்டப்படுகின்றன.",
            "places_opened": "சேமிக்கப்பட்ட இடங்கள் காட்டப்படுகின்றன.",
            "guide_opened": "வழிகாட்டி திறக்கப்படுகிறது.",
            "satellite_switched": "செயற்கைக்கோள் பார்வைக்கு மாற்றப்பட்டது.",
            "roadmap_switched": "சாலை வரைபட பார்வைக்கு மாற்றப்பட்டது.",
            "gps_centered": "உங்கள் நேரலை இருப்பிடம் கண்டறியப்படுகிறது.",
            "route_fitted": "முழு பாதை அமைக்கப்பட்டது.",
            "dest_cleared": "இலக்கு அழிக்கப்பட்டது.",
            "facility_found": "அருகிலுள்ள {category} தேடப்படுகிறது.",
            "unrecognized": "நான் கேட்டது: \"{query}\".",
        }
    }

    @classmethod
    def get_greeting(cls, lang: str = "en") -> str:
        lang_key = lang if lang in cls.RESPONSES else "en"
        return cls.RESPONSES[lang_key]["welcome"]

    @classmethod
    def parse_and_dispatch(
        cls,
        raw_query: str,
        context: Optional[Dict[str, Any]] = None,
        lang: str = "en"
    ) -> AuraExecutionResult:
        """
        Parses a natural-language voice command or query and maps it
        to a concrete application action and state update.
        """
        ctx = context or {}
        q = (raw_query or "").strip().lower()
        lang_key = lang if lang in cls.RESPONSES else "en"
        resp_bundle = cls.RESPONSES.get(lang_key, cls.RESPONSES["en"])

        if not q:
            return AuraExecutionResult(
                command_type=AuraCommandType.UNKNOWN,
                spoken_response=resp_bundle["welcome"],
                text_response=resp_bundle["welcome"],
                success=True
            )

        # ---------------------------------------------------------------------
        # 1. NAVIGATION TAB & APP SECTION CONTROLS (SINGLE MAIN APPLICATION)
        # ---------------------------------------------------------------------
        # 1.1 Navigation Tab / Map Section
        if (not re.search(r"\bmap\s+details\b", q)) and (
            any(k in q for k in ["నావిగేషన్", "నేవిగేషన్", "नेविगेशन", "வழிசெலுத்தல்"]) or (
                re.search(r"\b(open|let's\s+open|show|go\s+to|switch\s+to)\s+(the\s+)?(navigation(\s+tab)?|nav(\s+tab)?|map(\s+view|\s+tab)?|route\s+planner)\b", q)
                or re.search(r"^(navigation|nav|route\s+planner|open\s+map|show\s+map)$", q)
            )
        ):
            return AuraExecutionResult(
                command_type=AuraCommandType.NAVIGATE_TAB,
                spoken_response=resp_bundle.get("nav_opened", "Opening navigation."),
                text_response=f"🧭 {resp_bundle.get('nav_opened', 'Opening navigation.')}",
                action_name="switch_tab_nav",
                ui_updates={"current_view": "map_nav", "target_tab": "nav", "switch_to_nav_tab": True, "scroll_to_app_map": True}
            )

        # 1.2 My Trips / AI Travel Copilot Studio (Excludes "trip to [destination]")
        if not re.search(r"\b(trip\s+to|travel\s+to)\s+\w+", q) and (
            any(k in q for k in ["ట్రిప్స్", "యాత్రలు", "ट्रिप्स", "பயணங்கள்"]) or
            re.search(r"\b(open|show|go\s+to|view)\s+(my\s+)?(trips?|itinerar(y|ies)|travel\s+studio|copilot\s+studio)\b", q) or
            re.search(r"^(my\s+trips?|trips?|travel\s+studio|copilot\s+studio)$", q)
        ):
            return AuraExecutionResult(
                command_type=AuraCommandType.NAVIGATE_TAB,
                spoken_response=resp_bundle.get("trips_opened", "Here are your trips."),
                text_response=f"✨ {resp_bundle.get('trips_opened', 'Here are your trips.')}",
                action_name="switch_view_copilot_studio",
                ui_updates={"current_view": "copilot_studio"}
            )

        # 1.3 Hotels / Lodging
        if any(k in q for k in ["హోటల్", "లాడ్జి", "होटल", "தங்கும்"]) or re.search(
            r"\b(find|show|open|search\s+for)?\s*(nearby\s+)?(hotels?|lodges?|resorts?|stay|hotel)\b", q
        ):
            h_resp = resp_bundle.get("hotels_opened", "Let's find hotels.")
            return AuraExecutionResult(
                command_type=AuraCommandType.FACILITY_SEARCH,
                spoken_response=h_resp,
                text_response=f"🏨 {h_resp}",
                action_name="filter_facility_hotel",
                ui_updates={
                    "current_view": "map_nav",
                    "target_tab": "facilities",
                    "facility_filter": "hotel",
                    "show_emergency_amenities_on_map": True,
                    "scroll_to_app_map": True
                }
            )

        # 1.4 Flights / Aviation Transit
        if any(k in q for k in ["ఫ్లైట్స్", "విమానం", "उडान", "விமானம்"]) or re.search(
            r"\b(open|show|find|book)?\s*(the\s+)?(flights?|flight\s+planner|aviation|airplanes?|air\s+travel)\b", q
        ):
            return AuraExecutionResult(
                command_type=AuraCommandType.NAVIGATE_TAB,
                spoken_response=resp_bundle.get("flights_opened", "Opening flight planner."),
                text_response=f"✈️ {resp_bundle.get('flights_opened', 'Opening flight planner.')}",
                action_name="switch_travel_flights",
                ui_updates={"current_view": "copilot_studio", "selected_travel_mode": "FLIGHT", "transit_mode": "FLIGHT"}
            )

        # 1.5 Restaurants & Food
        if any(k in q for k in ["రెస్టారెంట్", "భోజనం", "भोजन", "உணவகம்"]) or re.search(
            r"\b(show|find|open|search\s+for)?\s*(nearby\s+)?(restaurants?|food|cafes?|dining)\b", q
        ):
            return AuraExecutionResult(
                command_type=AuraCommandType.FACILITY_SEARCH,
                spoken_response=resp_bundle.get("restaurants_opened", "Finding nearby restaurants."),
                text_response=f"🍽️ {resp_bundle.get('restaurants_opened', 'Finding nearby restaurants.')}",
                action_name="filter_facility_food",
                ui_updates={
                    "current_view": "map_nav",
                    "target_tab": "facilities",
                    "facility_filter": "food",
                    "show_emergency_amenities_on_map": True,
                    "scroll_to_app_map": True
                }
            )

        # 1.6 Profile & User Account
        if any(k in q for k in ["ప్రొఫైల్", "ఖాతా", "प्रोफाइल", "சுயவிவரம்"]) or re.search(
            r"\b(go\s+to|open|show|view)?\s*(my\s+)?(profile|account|user\s+profile)\b", q
        ):
            return AuraExecutionResult(
                command_type=AuraCommandType.NAVIGATE_TAB,
                spoken_response=resp_bundle.get("profile_opened", "Opening your profile."),
                text_response=f"👤 {resp_bundle.get('profile_opened', 'Opening your profile.')}",
                action_name="open_user_profile",
                ui_updates={"current_view": "dashboard", "show_user_profile_modal": True, "scroll_to_profile": True}
            )

        # 1.7 Chatbot / AURA Assistant
        if any(k in q for k in ["చాట్‌బాట్", "చాట్", "चैटबॉट", "சாட்பாட்"]) or re.search(
            r"\b(open\s+chat|open\s+chatbot|open\s+aura|talk\s+to\s+aura|ask\s+aura|assistant\s+chat)\b", q
        ):
            return AuraExecutionResult(
                command_type=AuraCommandType.NAVIGATE_TAB,
                spoken_response=resp_bundle.get("chat_opened", "AURA chatbot is ready."),
                text_response=f"💬 {resp_bundle.get('chat_opened', 'AURA chatbot is ready.')}",
                action_name="open_chatbot_drawer",
                ui_updates={"trigger_open_copilot": True, "aura_drawer_open": True, "target_tab": "chat"}
            )

        # 1.8 Nearby Facilities
        if any(k in q for k in ["సౌకర్యాలు", "సువిధా", "வசதிகள்"]) or re.search(
            r"\b(open\s+facilities|show\s+facilities|nearby\s+amenities|emergency\s+services)\b", q
        ):
            return AuraExecutionResult(
                command_type=AuraCommandType.NAVIGATE_TAB,
                spoken_response=resp_bundle["facilities_opened"],
                text_response=f"🏥 {resp_bundle['facilities_opened']}",
                action_name="switch_tab_facilities",
                ui_updates={"current_view": "map_nav", "target_tab": "facilities", "switch_to_nav_tab": True}
            )

        # 1.9 Saved Places / Sights
        if any(k in q for k in ["సేవ్ చేసిన", "సహేజే", "சேமிக்கப்பட்ட"]) or re.search(
            r"\b(open\s+saved\s+places|saved\s+locations|my\s+bookmarks|show\s+saved|open\s+places|show\s+places)\b", q
        ):
            return AuraExecutionResult(
                command_type=AuraCommandType.NAVIGATE_TAB,
                spoken_response=resp_bundle.get("places_opened", "Opening saved places."),
                text_response=f"⭐ {resp_bundle.get('places_opened', 'Opening saved places.')}",
                action_name="switch_view_places",
                ui_updates={"current_view": "places", "target_tab": "places"}
            )

        # 1.10 Virtual Guide
        if any(k in q for k in ["వర్చువల్ గైడ్", "गाइड", "வழிகாட்டி"]) or re.search(
            r"\b(open\s+virtual\s+guide|virtual\s+guide|3d\s+guide|companion\s+hud|guide\s+mode)\b", q
        ):
            return AuraExecutionResult(
                command_type=AuraCommandType.NAVIGATE_TAB,
                spoken_response=resp_bundle.get("guide_opened", "Opening virtual guide."),
                text_response=f"🚗 {resp_bundle.get('guide_opened', 'Opening virtual guide.')}",
                action_name="switch_view_guide",
                ui_updates={"current_view": "virtual_guide"}
            )

        # 1.11 Bookings / Reservations
        if any(k in q for k in ["బుకింగ్", "बुकिंग", "முன்பதிவு"]) or re.search(
            r"\b(open|show|view)?\s*(my\s+)?(bookings?|reservations?)\b", q
        ):
            return AuraExecutionResult(
                command_type=AuraCommandType.NAVIGATE_TAB,
                spoken_response=resp_bundle.get("bookings_opened", "Opening your bookings."),
                text_response=f"🎫 {resp_bundle.get('bookings_opened', 'Opening your bookings.')}",
                action_name="open_bookings",
                ui_updates={"current_view": "copilot_studio", "target_tab": "bookings"}
            )

        # 1.12 Go Back / Previous View
        if any(k in q for k in ["వెనుకకు", "పీచే", "பின்செல்"]) or re.search(
            r"\b(go\s+back|back|previous\s+(view|page|section)?)\b", q
        ):
            return AuraExecutionResult(
                command_type=AuraCommandType.NAVIGATE_TAB,
                spoken_response=resp_bundle.get("back_opened", "Going back."),
                text_response=f"↩️ {resp_bundle.get('back_opened', 'Going back.')}",
                action_name="navigate_go_back",
                ui_updates={"trigger_go_back": True}
            )

        # 1.13 Go Home / Main Dashboard
        if any(k in q for k in ["హోమ్", "డ్యాష్‌బోర్డ్", "होम", "முகப்பு"]) or re.search(
            r"\b(go\s+home|home|return\s+home|main\s+dashboard|dashboard)\b", q
        ):
            return AuraExecutionResult(
                command_type=AuraCommandType.NAVIGATE_TAB,
                spoken_response=resp_bundle.get("home_opened", "Returning to home dashboard."),
                text_response=f"🏠 {resp_bundle.get('home_opened', 'Returning to home dashboard.')}",
                action_name="navigate_home",
                ui_updates={"current_view": "dashboard", "target_tab": "nav"}
            )

        # 1.14 Settings / Preferences
        if any(k in q for k in ["సెట్టింగ్స్", "सेटिंग्स", "அமைப்புகள்"]) or re.search(
            r"\b(open\s+settings|settings|app\s+settings|preferences)\b", q
        ):
            return AuraExecutionResult(
                command_type=AuraCommandType.NAVIGATE_TAB,
                spoken_response=resp_bundle.get("settings_opened", "Opening settings."),
                text_response=f"⚙️ {resp_bundle.get('settings_opened', 'Opening settings.')}",
                action_name="open_settings",
                ui_updates={"current_view": "dashboard", "show_user_profile_modal": True, "scroll_to_profile": True}
            )

        # ---------------------------------------------------------------------
        # 2. MAP CONTROLS & CAMERA ACTIONS
        # ---------------------------------------------------------------------
        if any(k in q for k in ["శాటిలైట్", "సాటిలైట్", "सैटेलाइट", "उपग्रह", "செயற்கைக்கோள்"]) or re.search(r"\b(switch\s+to\s+satellite|satellite\s+view|satellite\s+mode|satellite\s+map)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.MAP_STYLE,
                spoken_response=resp_bundle["satellite_switched"],
                text_response=f"🛰️ {resp_bundle['satellite_switched']}",
                action_name="set_map_satellite",
                ui_updates={"map_engine": "google_satellite", "map_style": "satellite_hybrid", "scroll_to_app_map": True}
            )

        if any(k in q for k in ["రోడ్‌మ్యాప్", "రోడ్ మ్యాప్", "रोडमैप", "சாலை வரைபடம்"]) or re.search(r"\b(switch\s+to\s+(roadmap|road\s+map|vector\s+map|normal\s+view)|roadmap\s+view)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.MAP_STYLE,
                spoken_response=resp_bundle["roadmap_switched"],
                text_response=f"🗺️ {resp_bundle['roadmap_switched']}",
                action_name="set_map_roadmap",
                ui_updates={"map_engine": "google_roadmap", "map_style": "google_maps_road", "scroll_to_app_map": True}
            )

        if any(k in q for k in ["టెర్రైన్", "టెరైన్", "टेरेन", "நிலப்பரப்பு"]) or re.search(r"\b(switch\s+to\s+terrain|terrain\s+view|topography)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.MAP_STYLE,
                spoken_response=resp_bundle.get("terrain_switched", "Switched to elevation terrain map."),
                text_response="⛰️ Switched to elevation terrain map.",
                action_name="set_map_terrain",
                ui_updates={"map_engine": "google_terrain", "map_style": "terrain", "scroll_to_app_map": True}
            )

        if any(k in q for k in ["నా లొకేషన్", "మేరీ లోకేషన్", "मेरी लोकेशन", "என் இருப்பிடம்"]) or re.search(r"\b(show\s+my\s+current\s+location|where\s+am\s+i|locate\s+me|center\s+(on\s+)?my\s+location|current\s+location)\b", q):
            loc_updates = {"trigger_client_gps_sync": True, "scroll_to_app_map": True, "auto_fit_bounds": True}
            if ctx.get("user_coords"):
                loc_updates["map_center_override"] = ctx["user_coords"]
            return AuraExecutionResult(
                command_type=AuraCommandType.MAP_ACTION,
                spoken_response=resp_bundle["gps_centered"],
                text_response=f"📍 {resp_bundle['gps_centered']}",
                action_name="center_current_gps",
                ui_updates=loc_updates
            )

        if re.search(r"\b(fit\s+route|fit\s+bounds|show\s+full\s+route|show\s+whole\s+route|zoom\s+to\s+route|మొత్తం\s+రూట్|पूरा\s+रूट)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.MAP_ACTION,
                spoken_response=resp_bundle["route_fitted"],
                text_response=f"🔍 {resp_bundle['route_fitted']}",
                action_name="fit_route_bounds",
                ui_updates={"auto_fit_bounds": True, "scroll_to_app_map": True}
            )

        if re.search(r"\b(full\s*screen|go\s+full\s*screen|open\s+full\s*screen|toggle\s+full\s*screen|exit\s+full\s*screen)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.MAP_ACTION,
                spoken_response="Toggling full-screen map mode, Boss.",
                text_response="⛶ Toggling full screen map view...",
                action_name="toggle_fullscreen",
                ui_updates={"trigger_fullscreen": True, "scroll_to_app_map": True}
            )

        if re.search(r"\b(show\s+map\s+details|map\s+details|layer\s+details|traffic\s+details|transit\s+layers?)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.MAP_ACTION,
                spoken_response="Displaying map details and environmental layers, Boss.",
                text_response="🥞 Opening map details & environmental layers...",
                action_name="show_map_details",
                ui_updates={"trigger_layers_drawer": True, "scroll_to_app_map": True}
            )

        # ---------------------------------------------------------------------
        # 3. ROUTE ACTIONS & RECONFIGURATIONS
        # ---------------------------------------------------------------------
        if re.search(r"\b(clear\s+(my\s+)?destination|remove\s+destination|delete\s+destination|డెస్టినేషన్\s+తీసివేయి|गंतव्य\s+हटाओ)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.ROUTE_ACTION,
                spoken_response=resp_bundle["dest_cleared"],
                text_response=f"🗑️ {resp_bundle['dest_cleared']}",
                action_name="clear_destination",
                ui_updates={
                    "pending_dest": "",
                    "selected_dest_coords": None,
                    "selected_dest_label": "",
                    "routes_generated": False,
                    "cached_candidate_routes": None
                }
            )

        if re.search(r"\b(clear\s+(my\s+)?start|reset\s+start|reset\s+starting\s+point|ప్రారంభ\s+స్థానం\s+రీసెట్|शुरुआती\s+स्थान\s+हटाओ)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.ROUTE_ACTION,
                spoken_response=resp_bundle["orig_cleared"],
                text_response=f"📍 {resp_bundle['orig_cleared']}",
                action_name="clear_start_location",
                ui_updates={
                    "pending_orig": "",
                    "is_custom_start_place": False,
                    "routes_generated": False,
                    "cached_candidate_routes": None
                }
            )

        if re.search(r"\b(swap\s+(start\s+and\s+destination|locations)|reverse\s+route|తిప్పి\s+రాయు|उल्टा\s+करो)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.ROUTE_ACTION,
                spoken_response=resp_bundle["swapped"],
                text_response=f"⇅ {resp_bundle['swapped']}",
                action_name="swap_endpoints",
                ui_updates={"trigger_swap_endpoints": True}
            )

        if re.search(r"\b(add\s+a\s+stop(\s+to\s+my\s+route)?|add\s+stop|add\s+waypoint|intermediate\s+stop)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.ROUTE_ACTION,
                spoken_response="Intermediate stop selection activated. Click anywhere on the map or type a location, Boss.",
                text_response="🟣 Intermediate stop mode enabled. Select on map or search above.",
                action_name="add_intermediate_stop",
                ui_updates={"map_picking_mode": "stop", "target_tab": "nav", "scroll_to_app_map": True}
            )

        if re.search(r"\b(recalculate\s+routes?|find\s+new\s+routes?|refresh\s+routes?|మళ్ళీ\s+లెక్కించు|रूट\s+रिफ्रेश)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.ROUTE_ACTION,
                spoken_response="Recalculating all optimal routes across the road network.",
                text_response="⚡ Recalculating optimal road corridors...",
                action_name="recalculate_routes",
                ui_updates={
                    "routes_generated": True,
                    "_prev_route_sig": None,
                    "cached_candidate_routes": None,
                    "auto_fit_bounds": True
                }
            )

        # Destructive Confirmation check: "Clear active route" / "Cancel trip"
        if re.search(r"\b(clear\s+all\s+stops|clear\s+(active\s+)?route|cancel\s+(my\s+)?trip|రద్దు\s+చేయి|रद्द\s+करो)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.ROUTE_ACTION,
                spoken_response=resp_bundle["confirm_clear_route"],
                text_response=f"⚠️ {resp_bundle['confirm_clear_route']}",
                action_name="confirm_clear_trip",
                requires_confirmation=True,
                confirmation_prompt="Confirm clearing active trip and all stops?",
                ui_updates={
                    "pending_dest": "",
                    "selected_dest_coords": None,
                    "intermediate_stops": [],
                    "routes_generated": False
                }
            )

        # ---------------------------------------------------------------------
        # 4. NEARBY FACILITY & AMENITY SEARCHES
        # ---------------------------------------------------------------------
        fac_match = None
        cat_key = None
        cat_disp = "Facilities"

        if any(k in q for k in ["ఆసుపత్రి", "హాస్పిటల్", "अस्पताल", "மருத்துவமனை", "மருத்துவ"]) or re.search(r"\b(hospitals?|clinics?|doctors?|medical)\b", q):
            cat_key = "health"
            cat_disp = "hospitals and medical centers"
        elif any(k in q for k in ["పెట్రోల్", "డీజిల్", "पेट्रोल", "எரிபொருள்"]) or re.search(r"\b(petrol|diesel|fuel\s+stations?|gas\s+stations?|ev\s+charging)\b", q):
            cat_key = "fuel"
            cat_disp = "fuel and EV charging stations"
        elif any(k in q for k in ["రెస్టారెంట్", "హోటల్", "భోజనం", "भोजन", "உணவகம்"]) or re.search(r"\b(restaurants?|food|cafe|baker(y|ies)|coffee)\b", q):
            cat_key = "food"
            cat_disp = "restaurants and food spots"
        elif any(k in q for k in ["బ్యాంక్", "ఎటిఎం", "एटीएम", "बैंक", "வங்கி"]) or re.search(r"\b(atm|atms|banks?|cash\s+machine)\b", q):
            cat_key = "atm"
            cat_disp = "ATMs and bank branches"
        elif any(k in q for k in ["లాడ్జి", "రిసార్ట్", "होटल", "தங்கும்"]) or re.search(r"\b(hotels?|lodges?|resorts?|stay)\b", q):
            cat_key = "hotel"
            cat_disp = "hotels and lodges"

        if cat_key:
            msg = resp_bundle["facility_found"].format(category=cat_disp)
            return AuraExecutionResult(
                command_type=AuraCommandType.FACILITY_SEARCH,
                spoken_response=msg,
                text_response=f"🔍 {msg}",
                action_name=f"filter_facility_{cat_key}",
                ui_updates={
                    "target_tab": "facilities",
                    "facility_filter": cat_key,
                    "show_emergency_amenities_on_map": True
                }
            )

        # ---------------------------------------------------------------------
        # 5. TRAVEL TOOLS & CALCULATIONS
        # ---------------------------------------------------------------------
        if re.search(r"\b(calculate\s+fuel|fuel\s+expenses?|fuel\s+cost|toll\s+charges?|fuel\s+calculator|ఖర్చు|लागत)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.TRAVEL_TOOL,
                spoken_response=resp_bundle["fuel_tool"],
                text_response=f"⛽ {resp_bundle['fuel_tool']}",
                action_name="open_fuel_calculator",
                ui_updates={"show_fuel_modal": True, "target_tab": "nav"}
            )

        if re.search(r"\b(avoid\s+tolls?|toll\s+free)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.TRAVEL_TOOL,
                spoken_response="Toll avoidance enabled. Rerouting via toll-free corridors.",
                text_response="🚫 Toll avoidance active. Updating routes...",
                action_name="toggle_avoid_tolls",
                ui_updates={"avoid_tolls": True, "routes_generated": True, "cached_candidate_routes": None}
            )

        if re.search(r"\b(avoid\s+highways?|no\s+highways?)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.TRAVEL_TOOL,
                spoken_response="Highway avoidance enabled. Calculating alternate roads.",
                text_response="🛣️ Highway avoidance active. Updating routes...",
                action_name="toggle_avoid_highways",
                ui_updates={"avoid_highways": True, "routes_generated": True, "cached_candidate_routes": None}
            )

        # ---------------------------------------------------------------------
        # 6. ASSISTANT VOICE & SYSTEM CONTROLS
        # ---------------------------------------------------------------------
        if re.search(r"\b(stop\s+talking|be\s+quiet|silence|mute\s+voice|నిశ్శబ్దం|चुप\s+रहो)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.VOICE_CONTROL,
                spoken_response="",
                text_response="🔇 Voice speech silenced.",
                action_name="silence_speech",
                ui_updates={"voice_speech_active": False}
            )

        # ---------------------------------------------------------------------
        # 7. ROUTE DESTINATION VIA VOICE: "Navigate to [place]"
        # ---------------------------------------------------------------------
        nav_dest_match = re.search(r"\b(navigate\s+to|drive\s+to|go\s+to|directions?\s+to|take\s+me\s+to|route\s+to|plan\s+a\s+trip\s+to|plan\s+trip\s+to|trip\s+to)\s+(.+)", q)
        if nav_dest_match:
            dest_query = nav_dest_match.group(2).strip()
            # Exclude app tab names
            if dest_query not in ["navigation", "chatbot", "chat", "facilities", "map", "tools", "saved"]:
                clean_dest = dest_query.title()
                return AuraExecutionResult(
                    command_type=AuraCommandType.ROUTE_ACTION,
                    spoken_response=f"Setting destination to {clean_dest} and finding routes.",
                    text_response=f"🏁 Navigating to **{clean_dest}**...",
                    action_name="voice_set_destination",
                    ui_updates={
                        "pending_dest": dest_query,
                        "target_tab": "nav",
                        "active_trip_destination": clean_dest,
                        "aura_active_trip_context": {"destination": clean_dest, "query": raw_query},
                        "scroll_to_app_map": True
                    }
                )

        # ---------------------------------------------------------------------
        # 8. FALLBACK: GENERAL TRAVEL ADVICE & INTELLIGENT CHAT
        # ---------------------------------------------------------------------
        return AuraExecutionResult(
            command_type=AuraCommandType.GENERAL_CHAT,
            spoken_response=f"Processing your question about {raw_query[:35]}...",
            text_response=f"💬 Asking AURA Assistant: *\"{raw_query}\"*",
            action_name="delegate_to_chat_turn",
            ui_updates={"pending_chat_prompt": raw_query}
        )

    @classmethod
    def apply_execution_result(cls, result: AuraExecutionResult, session_state: Any) -> None:
        """
        Safely applies the resulting UI state mutations directly to streamlit's session_state.
        Ensures section switches occur within the single existing NextRoute application.
        """
        # Maintain navigation view history for "Go back"
        if "view_history" not in session_state:
            session_state["view_history"] = ["dashboard"]

        cur_view = session_state.get("current_view", "dashboard")
        if not session_state["view_history"] or session_state["view_history"][-1] != cur_view:
            session_state["view_history"].append(cur_view)

        if result.ui_updates.get("trigger_go_back"):
            history = session_state.get("view_history", [])
            if len(history) > 1:
                history.pop()  # Pop current
                session_state["current_view"] = history[-1]
            else:
                session_state["current_view"] = "dashboard"
            return

        for k, v in result.ui_updates.items():
            if k in ["txt_orig", "txt_dest"]:
                continue
            session_state[k] = v

        if result.ui_updates.get("current_view"):
            new_v = result.ui_updates["current_view"]
            if not session_state["view_history"] or session_state["view_history"][-1] != new_v:
                session_state["view_history"].append(new_v)

        if result.ui_updates.get("target_tab") in ["nav", "facilities"]:
            session_state["current_view"] = "map_nav"
            session_state["switch_to_nav_tab"] = True

        if result.ui_updates.get("trigger_swap_endpoints"):
            old_orig_coords = session_state.get("user_live_coords")
            old_orig_label = session_state.get("user_live_label", "")
            old_dest_coords = session_state.get("selected_dest_coords")
            old_dest_label = session_state.get("selected_dest_label", "")

            session_state["user_live_coords"] = old_dest_coords
            session_state["user_live_label"] = old_dest_label
            session_state["pending_orig"] = old_dest_label

            session_state["selected_dest_coords"] = old_orig_coords
            session_state["selected_dest_label"] = old_orig_label
            session_state["pending_dest"] = old_orig_label

            session_state["routes_generated"] = bool(old_dest_coords and old_orig_coords)
