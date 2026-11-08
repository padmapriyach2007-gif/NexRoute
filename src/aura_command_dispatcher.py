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

    # Multilingual response templates
    RESPONSES = {
        "en": {
            "welcome": "Hello, Boss! I'm AURA, your personal NexRoute assistant. What would you like me to do?",
            "nav_opened": "Opening navigation dashboard.",
            "chat_opened": "AURA AI Chatbot is ready for you, Boss.",
            "facilities_opened": "Showing nearby emergency and travel amenities.",
            "places_opened": "Displaying saved and bookmark locations.",
            "satellite_switched": "Switched map view to satellite hybrid imagery.",
            "roadmap_switched": "Switched to high-contrast road vector map.",
            "terrain_switched": "Switched to elevation terrain map.",
            "gps_centered": "Locating your live coordinates and centering the map.",
            "route_fitted": "Adjusting map camera to frame the full route corridor.",
            "dest_cleared": "Destination has been cleared.",
            "orig_cleared": "Starting location reset to device live GPS.",
            "swapped": "Start and destination have been reversed.",
            "facility_found": "Locating {category} around your route corridor.",
            "fuel_tool": "Opening fuel economy and toll expense calculations.",
            "confirm_clear_route": "Boss, are you sure you want to clear your active route?",
            "unrecognized": "I heard: \"{query}\". How can I assist with your journey?",
        },
        "te": {
            "welcome": "నమస్కారం, బాస్! నేను AURA, మీ వ్యక్తిగత నెక్స్‌రూట్ అసిస్టెంట్. నేను మీకు ఎలా సహాయపడగలను?",
            "nav_opened": "నావిగేషన్ విభాగం తెరవబడింది.",
            "chat_opened": "AURA AI చాట్‌బాట్ సిద్ధంగా ఉంది, బాస్.",
            "facilities_opened": "సమీప అత్యవసర మరియు ప్రయాణ సౌకర్యాలు చూపిస్తున్నాను.",
            "places_opened": "సేవ్ చేసిన ప్రదేశాలు తెరవబడ్డాయి.",
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
            "unrecognized": "నేను విన్నాను: \"{query}\". మీ ప్రయాణంలో నేను ఎలా సహాయపడగలను?",
        },
        "hi": {
            "welcome": "नमस्ते, बॉस! मैं AURA हूँ, आपका व्यक्तिगत नेक्स-रूट सहायक। मैं आपके लिए क्या कर सकता हूँ?",
            "nav_opened": "नेविगेशन डैशबोर्ड खोला जा रहा है।",
            "chat_opened": "AURA AI चैटबॉट तैयार है, बॉस।",
            "facilities_opened": "आस-पास की आपातकालीन और यात्रा सुविधाएं दिखाई जा रही हैं।",
            "places_opened": "सहेजे गए स्थान खोले जा रहे हैं।",
            "satellite_switched": "सैटेलाइट हाइब्रिड दृश्य सक्रिय कर दिया गया है।",
            "roadmap_switched": "रोडमैप दृश्य पर स्विच कर दिया गया है।",
            "terrain_switched": "टेरेन दृश्य पर स्विच किया गया है।",
            "gps_centered": "आपकी वर्तमान लाइव लोकेशन पर मैप केंद्रित किया जा रहा है।",
            "route_fitted": "पूरे मार्ग को मैप पर फ़िट कर दिया गया है।",
            "dest_cleared": "गंतव्य स्थान हटा दिया गया है।",
            "orig_cleared": "शुरुआती बिंदु लाइव GPS पर रीसेट किया गया है।",
            "swapped": "शुरुआत और गंतव्य स्थान आपस में बदल दिए गए हैं।",
            "facility_found": "निकटवर्ती {category} खोजे जा रहे हैं।",
            "fuel_tool": "ईंधन और टोल खर्च की गणना खोली जा रही है।",
            "confirm_clear_route": "बॉस, क्या आप वाकई सक्रिय मार्ग को हटाना चाहते हैं?",
            "unrecognized": "मैंने सुना: \"{query}\"। मैं आपकी यात्रा में क्या मदद करूँ?",
        },
        "ta": {
            "welcome": "வணக்கம், பாஸ்! நான் AURA, உங்கள் தனிப்பட்ட NexRoute உதவியாளர். நான் உங்களுக்கு என்ன செய்ய வேண்டும்?",
            "nav_opened": "வழிசெலுத்தல் திறக்கப்படுகிறது.",
            "chat_opened": "AURA AI சாட்பாட் தயாராக உள்ளது, பாஸ்.",
            "facilities_opened": "அருகிலுள்ள அவசர வசதிகள் காட்டப்படுகின்றன.",
            "places_opened": "சேமிக்கப்பட்ட இடங்கள் காட்டப்படுகின்றன.",
            "satellite_switched": "செயற்கைக்கோள் பார்வைக்கு மாற்றப்பட்டது.",
            "roadmap_switched": "சாலை வரைபட பார்வைக்கு மாற்றப்பட்டது.",
            "gps_centered": "உங்கள் நேரலை இருப்பிடம் கண்டறியப்படுகிறது.",
            "route_fitted": "முழு பாதையையும் காட்டும் வகையில் வரைபடம் அமைக்கப்பட்டது.",
            "dest_cleared": "இலக்கு அழிக்கப்பட்டது.",
            "facility_found": "அருகிலுள்ள {category} தேடப்படுகிறது.",
            "unrecognized": "நான் கேட்டது: \"{query}\". உங்களுக்கு என்ன உதவி வேண்டும்?",
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
        # 1. NAVIGATION TAB & APP SECTION CONTROLS
        # ---------------------------------------------------------------------
        if any(k in q for k in ["నావిగేషన్", "నేవిగేషన్", "नेविगेशन", "வழிசெலுத்தல்"]) or re.search(r"\b(open\s+(navigation|nav|dashboard|map)|go\s+to\s+navigation|start\s+nav)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.NAVIGATE_TAB,
                spoken_response=resp_bundle["nav_opened"],
                text_response=f"🧭 {resp_bundle['nav_opened']}",
                action_name="switch_tab_nav",
                ui_updates={"target_tab": "nav", "scroll_to_app_map": True}
            )

        if any(k in q for k in ["చాట్‌బాట్", "చాట్", "चैटबॉट", "சாட்பாட்"]) or re.search(r"\b(open\s+chat|open\s+chatbot|open\s+aura|talk\s+to\s+aura|ask\s+aura|assistant\s+chat)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.NAVIGATE_TAB,
                spoken_response=resp_bundle["chat_opened"],
                text_response=f"💬 {resp_bundle['chat_opened']}",
                action_name="open_chatbot_drawer",
                ui_updates={"trigger_open_copilot": True, "aura_drawer_open": True, "target_tab": "chat"}
            )

        if any(k in q for k in ["సౌకర్యాలు", "సువిధా", "வசதிகள்"]) or re.search(r"\b(open\s+facilities|show\s+facilities|nearby\s+amenities|emergency\s+services)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.NAVIGATE_TAB,
                spoken_response=resp_bundle["facilities_opened"],
                text_response=f"🏥 {resp_bundle['facilities_opened']}",
                action_name="switch_tab_facilities",
                ui_updates={"target_tab": "facilities"}
            )

        if any(k in q for k in ["సేవ్ చేసిన", "సహేజే", "சேமிக்கப்பட்ட"]) or re.search(r"\b(open\s+saved\s+places|saved\s+locations|my\s+bookmarks|show\s+saved)\b", q):
            return AuraExecutionResult(
                command_type=AuraCommandType.NAVIGATE_TAB,
                spoken_response=resp_bundle["places_opened"],
                text_response=f"⭐ {resp_bundle['places_opened']}",
                action_name="switch_tab_saved",
                ui_updates={"target_tab": "places"}
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
        nav_dest_match = re.search(r"\b(navigate\s+to|drive\s+to|go\s+to|directions?\s+to|take\s+me\s+to|route\s+to)\s+(.+)", q)
        if nav_dest_match:
            dest_query = nav_dest_match.group(2).strip()
            # Exclude app tab names
            if dest_query not in ["navigation", "chatbot", "chat", "facilities", "map", "tools", "saved"]:
                return AuraExecutionResult(
                    command_type=AuraCommandType.ROUTE_ACTION,
                    spoken_response=f"Setting destination to {dest_query.title()} and finding routes.",
                    text_response=f"🏁 Navigating to **{dest_query.title()}**...",
                    action_name="voice_set_destination",
                    ui_updates={
                        "pending_dest": dest_query,
                        "target_tab": "nav",
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
        """
        for k, v in result.ui_updates.items():
            if k in ["txt_orig", "txt_dest"]:
                continue
            session_state[k] = v

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
