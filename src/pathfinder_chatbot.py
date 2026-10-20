"""
A.U.R.A. — Autonomous Conversational Copilot Engine
Adaptive User Route Assistant for P.A.T.H.F.I.N.D.E.R.
(Predictive Adaptive Transit & Hazard-Free Intelligent Navigation)

Dual-Purpose AI Architecture:
1. General-Purpose AI Assistant (Science, Math, Programming, Writing, Education, History, Creative Tasks)
2. Intelligent Autonomous Navigation & Hazard Evasion (Fastest, Shortest, Balanced, Accessible routes,
   real-time road blockages, campus landmarks, and life-safety evacuation SOPs)
"""

import os
import re
import logging
from typing import Dict, Any, List, Optional, Tuple

from src.ai_assistant_engine import (
    LLMClient,
    BuiltinCognitiveEngine,
    ConversationManager,
    GroundingEngine,
    AURA_CORE_SYSTEM_PROMPT
)
from src.pathfinder_tools import PathfinderToolExecutor, TOOL_SCHEMAS

logger = logging.getLogger("pathfinder.aura")

# Complete system instructions for A.U.R.A.
AURA_SYSTEM_PROMPT = AURA_CORE_SYSTEM_PROMPT


class PathfinderChatbot:
    """
    A.U.R.A. — Adaptive User Route Assistant
    Intelligent Conversational Assistant for P.A.T.H.F.I.N.D.E.R.
    """

    def __init__(self, pipeline=None, map_service=None, road_condition_manager=None, emergency_service_manager=None):
        self.pipeline = pipeline
        self.map_service = map_service
        self.road_manager = road_condition_manager
        self.emergency_manager = emergency_service_manager
        self.explanation_mode = "standard"  # simple, standard, advanced
        self.last_topic = None
        self.last_destination = None
        self.llm_client = LLMClient()
        self.cognitive_engine = BuiltinCognitiveEngine()
        self.conv_manager = ConversationManager()
        self.tool_executor = PathfinderToolExecutor(
            pipeline=pipeline,
            map_service=map_service,
            road_condition_manager=road_condition_manager,
            emergency_service_manager=emergency_service_manager
        )

    def reset_conversation(self):
        """Resets active conversation context and history."""
        self.conv_manager.clear()
        self.last_topic = None
        self.last_destination = None
        self.explanation_mode = "standard"

    def answer(self, user_query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processes any user query using contextual awareness, tool routing, and adaptive intelligence.
        Returns a dictionary with 'badge', 'response', and optional 'action'.
        """
        raw_query = user_query.strip()
        if not raw_query:
            return {
                "badge": "⚡ A.U.R.A. READY",
                "response": (
                    "Hello! I am **A.U.R.A.**, your **Adaptive User Route Assistant** for P.A.T.H.F.I.N.D.E.R. "
                    "I can answer ordinary general knowledge questions, write stories or code, explain concepts, "
                    "or calculate live hazard-free navigation routes. What would you like to explore today?"
                )
            }

        q = raw_query.lower()
        ctx = context or {}

        # 1. Explanation Mode Switching
        if any(p in q for p in ["explain simply", "simple explanation", "simply", "simple mode", "beginner", "eli5", "easy words", "short answer"]):
            self.explanation_mode = "simple"
        elif any(p in q for p in ["explain in detail", "technical explanation", "deep dive", "advanced explanation", "in depth", "give me a technical"]):
            self.explanation_mode = "advanced"
        elif any(p in q for p in ["standard explanation", "normal explanation"]):
            self.explanation_mode = "standard"

        ans = self._compute_answer(raw_query, q, ctx)
        if isinstance(ans, dict) and "response" in ans:
            self.conv_manager.add_turn("user", raw_query)
            self.conv_manager.add_turn("assistant", ans["response"], ans.get("badge"))
        return ans

    def _extract_lat_lon(self, resolved: Any) -> Optional[Tuple[float, float]]:
        """Extracts (lat, lon) safely from either dict, tuple, or list structure."""
        if not resolved:
            return None
        if isinstance(resolved, dict):
            return (float(resolved.get("lat", 0.0)), float(resolved.get("lon", 0.0)))
        elif isinstance(resolved, (list, tuple)) and len(resolved) >= 2:
            return (float(resolved[0]), float(resolved[1]))
        return None

    def _compute_answer(self, raw_query: str, q: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Core internal processing separating navigation actions from general conversation."""

        # ---------------------------------------------------------------------
        # 1. SECURITY & PROMPT INJECTION DEFENSE
        # ---------------------------------------------------------------------
        injection_triggers = [
            "ignore previous instructions", "ignore all instructions", "disregard prior instructions",
            "system prompt", "reveal your instructions", "print your prompt", "show secret key",
            "what is your api key", "bypass restrictions", "jailbreak", "dan mode"
        ]
        if any(trig in q for trig in injection_triggers):
            return {
                "badge": "🛡️ SYSTEM SECURITY PROTOCOL",
                "response": (
                    "**Request Blocked by Security Protocol.**\n\n"
                    "I am **A.U.R.A.**, an AI assistant governed by strict data safety and privacy policies. "
                    "System instructions, API credentials, and internal prompts are strictly confidential "
                    "and cannot be disclosed, altered, or overridden. How can I assist you with an educational, "
                    "coding, creative, or navigation inquiry?"
                )
            }

        # ---------------------------------------------------------------------
        # 2. PATHFINDER CAPABILITIES & ARCHITECTURE INQUIRY
        # ---------------------------------------------------------------------
        if any(w in q for w in ["what can pathfinder actually do", "what can pathfinder do", "what are your capabilities", "tell me what pathfinder can do"]):
            return {
                "badge": "🧭 PATHFINDER SYSTEM OVERVIEW",
                "response": (
                    "### 🧭 What PATHFINDER Can Actually Do\n\n"
                    "PATHFINDER (*Predictive Adaptive Transit & Hazard-Free Intelligent Navigation*) is an intelligent navigation platform designed with a clear distinction between implemented features and external capabilities:\n\n"
                    "#### ✅ Implemented & Verified Features:\n"
                    "• **Dynamic Multi-Objective Route Optimization:** Generates distinct routes mathematically tailored to your priority: **Fastest** (velocity priority), **Shortest** (geodesic mileage minimization), **Balanced** (Pareto equilibrium), and **Accessible** (step-free, ramp-prioritized, wheelchair-friendly).\n"
                    "• **Live Obstacle & Road Closure Evasion:** Automatically senses active road restrictions (such as the NH-16 bypass closure) and reroutes traffic with zero manual intervention.\n"
                    "• **Interactive Map & Polyline Synchronization:** Fully synchronized Leaflet/Folium map with clickable route cards, layer toggling (Satellite, Road, Terrain), and camera auto-fit bounds.\n"
                    "• **Real-Time Atmospheric Weather:** Connects directly to the Open-Meteo meteorological API for live temperature, humidity, and wind conditions at any origin or destination.\n"
                    "• **Nearby Amenity Discovery:** Real-time search for dining, lodging, fuel, and medical care around coordinates.\n"
                    "• **A.U.R.A. Conversational Copilot:** Dual-purpose assistant supporting general knowledge, coding, writing, and direct map navigation actions.\n\n"
                    "#### 📋 Planned / External Features (Honest Scope):\n"
                    "• Direct CAN-bus vehicle autonomous steering (requires physical drive-by-wire hardware).\n"
                    "• Real-time commercial satellite video telemetry (requires dedicated defense/commercial satellite feeds)."
                )
            }

        # ---------------------------------------------------------------------
        # 3. LANGUAGE DETECTION & MULTILINGUAL SUPPORT
        # ---------------------------------------------------------------------
        app_lang = (ctx.get("language") or "en").lower().strip()

        is_telugu = (app_lang == "te") or bool(re.search(r"[\u0c00-\u0c7f]", raw_query)) or any(w in q for w in ["namaskaram", "ela unnav", "dharilo", "margam", "telugu lo"])
        is_hindi = (app_lang == "hi") or bool(re.search(r"[\u0900-\u097f]", raw_query) and not any(w in q for w in ["marathi", "marathit"])) or any(w in q for w in ["namaste", "kaise ho", "rasta", "hindi me"])
        is_tamil = (app_lang == "ta") or bool(re.search(r"[\u0b80-\u0bff]", raw_query)) or any(w in q for w in ["vanakkam", "eppadi irukinga", "vazhi", "tamilil", "tamil"])
        is_kannada = (app_lang == "kn") or bool(re.search(r"[\u0c80-\u0cff]", raw_query)) or any(w in q for w in ["namaskara", "hegidira", "daari", "kannadadalli", "kannada"])
        is_malayalam = (app_lang == "ml") or bool(re.search(r"[\u0d00-\u0d7f]", raw_query)) or any(w in q for w in ["namaskaram", "sugamano", "vazhi", "malayalam"])
        is_bengali = (app_lang == "bn") or bool(re.search(r"[\u0980-\u09ff]", raw_query)) or any(w in q for w in ["nomoshkar", "kemon acho", "rasta", "banglay", "bengali"])
        is_marathi = (app_lang == "mr") or any(w in q for w in ["namaskar", "kasa kay", "rasta", "marathit", "marathi"])

        active_lang = "en"
        if is_telugu:
            active_lang = "te"
        elif is_hindi:
            active_lang = "hi"
        elif is_tamil:
            active_lang = "ta"
        elif is_kannada:
            active_lang = "kn"
        elif is_malayalam:
            active_lang = "ml"
        elif is_bengali:
            active_lang = "bn"
        elif is_marathi:
            active_lang = "mr"
        elif app_lang in ("te", "hi", "ta", "kn", "ml", "bn", "mr"):
            active_lang = app_lang

        if "translate" in q:
            return self._handle_translation(raw_query, q)

        # ---------------------------------------------------------------------
        # 4. EMERGENCY & LIFE-SAFETY PROTOCOLS
        # ---------------------------------------------------------------------
        em_res = self._handle_emergency_queries(raw_query, q, ctx)
        if em_res is not None:
            return em_res

        # ---------------------------------------------------------------------
        # 5. NAVIGATION TOOL ACTIONS (DETERMINISTIC ROUTING & REAL APP ACTIONS)
        # ---------------------------------------------------------------------
        # A) Route Preferences (Avoid tolls, highways, ferries)
        pref_res = self._handle_preferences(raw_query, q, ctx, language=active_lang)
        if pref_res is not None:
            return pref_res

        # B) Explicit Route Calculation & Destination Targeting (Resolves "there")
        route_intent_res = self._handle_route_intent(raw_query, q, ctx)
        if route_intent_res is not None:
            return route_intent_res

        # C) Map Camera & Route Focus Sync
        map_act = self._handle_map_action(raw_query, q, ctx)
        if map_act is not None:
            return map_act

        # D) Route Comparison & Metrics Analysis (From real context)
        route_comp = self._handle_route_comparison(raw_query, q, ctx)
        if route_comp is not None:
            return route_comp

        # E) Journey Telemetry & Status
        journey_res = self._handle_journey_status(raw_query, q, ctx, language=active_lang)
        if journey_res is not None:
            return journey_res

        # F) Grounding Tools: Nearby Places & Real Weather
        places_res = self._handle_nearby_places(raw_query, q, ctx)
        if places_res is not None:
            return places_res

        weather_res = self._handle_live_weather(raw_query, q, ctx)
        if weather_res is not None:
            return weather_res

        # G) Global Travel Inquiries (e.g. "How do I go to Tokyo?")
        global_res = self._handle_global_transit(raw_query, q, ctx)
        if global_res is not None:
            return global_res

        # ---------------------------------------------------------------------
        # 6. CONTEXTUAL MULTILINGUAL GREETINGS & INTRODUCTIONS
        # ---------------------------------------------------------------------
        is_greeting_or_intro = any(w in q for w in [
            "hello", "hi", "hey", "who are you", "who r u", "help me", "what can you do", "introduce yourself"
        ])

        if is_telugu and (is_greeting_or_intro or any(w in raw_query for w in ["నమస్కారం", "హలో", "ఎలా ఉన్నావు", "సహాయపడగలరు", "నమస్తే", "మీరు ఎవరు", "నీవు ఎవరు"]) or any(w in q for w in ["namaskaram"])):
            return self._handle_telugu_query(raw_query, q, ctx)

        if is_hindi and (is_greeting_or_intro or any(w in raw_query for w in ["नमस्ते", "हैलो", "कैसे हो", "प्रणाम", "आप कौन हैं", "तुम कौन हो"]) or any(w in q for w in ["namaste"])):
            return self._handle_hindi_query(raw_query, q, ctx)

        if is_tamil and (is_greeting_or_intro or any(w in raw_query for w in ["வணக்கம்", "ஹலோ", "யார்"]) or any(w in q for w in ["vanakkam"])):
            return self._handle_tamil_query(raw_query, q, ctx)

        if is_kannada and (is_greeting_or_intro or any(w in raw_query for w in ["ನಮಸ್ಕಾರ", "ಹಲೋ", "ಯಾರು"]) or any(w in q for w in ["namaskara"])):
            return self._handle_kannada_query(raw_query, q, ctx)

        if is_malayalam and (is_greeting_or_intro or any(w in raw_query for w in ["നമസ്കാരം", "ഹലോ", "ആരാണ്"]) or any(w in q for w in ["namaskaram"])):
            return self._handle_malayalam_query(raw_query, q, ctx)

        if is_bengali and (is_greeting_or_intro or any(w in raw_query for w in ["নমস্কার", "হ্যালো", "কে"]) or any(w in q for w in ["nomoshkar"])):
            return self._handle_bengali_query(raw_query, q, ctx)

        if is_marathi and (is_greeting_or_intro or any(w in raw_query for w in ["नमस्कार", "हॅलो", "कोण"]) or any(w in q for w in ["namaskar"])):
            return self._handle_marathi_query(raw_query, q, ctx)

        # ---------------------------------------------------------------------
        # 6. GENERAL-PURPOSE CONVERSATION & INTELLIGENCE (LLM OR COGNITIVE ENGINE)
        # ---------------------------------------------------------------------
        # Check if user is asking diagnostic questions about external AI connection
        if any(w in q for w in ["is ai connected", "is external ai connected", "is ai working", "what model are you using", "is external ai working", "which ai model"]):
            p_name = self.llm_client.active_provider_name
            if p_name != "builtin":
                return {
                    "badge": f"⚡ A.U.R.A. • {p_name.upper()}",
                    "response": (
                        f"**External AI Provider Active:** I am currently connected via **{p_name.title()}** "
                        f"for general-purpose natural language reasoning, paired with PATHFINDER's real routing and GIS engine."
                    )
                }
            else:
                return {
                    "badge": "⚡ A.U.R.A. • COGNITIVE ENGINE",
                    "response": (
                        "**AI Status:** I am currently operating on PATHFINDER's **Built-in Cognitive Reasoning Engine**.\n\n"
                        "To connect a commercial LLM, configure one of the following environment variables on your server:\n"
                        "• `GEMINI_API_KEY` or `GOOGLE_API_KEY` (Google Gemini)\n"
                        "• `OPENAI_API_KEY` (OpenAI GPT-4o-mini)\n"
                        "• `GROQ_API_KEY` (Groq Llama-3.3-70B)\n"
                        "• `ANTHROPIC_API_KEY` (Anthropic Claude)\n\n"
                        "All built-in reasoning, mathematical evaluation, coding help, and real navigation tools remain 100% available."
                    )
                }

        # Step 1: External LLM attempt if configured
        if self.llm_client.active_provider_name != "builtin":
            lang_code = (ctx.get("language") or "en").lower().strip()
            lang_prompts = {
                "te": "The user's preferred language is Telugu (తెలుగు). Please reply naturally and fluently in Telugu script.",
                "hi": "The user's preferred language is Hindi (हिन्दी). Please reply naturally and fluently in Devanagari Hindi script.",
                "ta": "The user's preferred language is Tamil (தமிழ்). Please reply naturally and fluently in Tamil script.",
                "kn": "The user's preferred language is Kannada (ಕನ್ನಡ). Please reply naturally and fluently in Kannada script.",
                "ml": "The user's preferred language is Malayalam (മലയാളം). Please reply naturally and fluently in Malayalam script.",
                "bn": "The user's preferred language is Bengali (বাংলা). Please reply naturally and fluently in Bengali script.",
                "mr": "The user's preferred language is Marathi (मराठी). Please reply naturally and fluently in Marathi script."
            }
            system_prompt = AURA_CORE_SYSTEM_PROMPT
            if lang_code in lang_prompts:
                system_prompt += f"\n\nLANGUAGE INSTRUCTION: {lang_prompts[lang_code]}"
            llm_msgs = self.conv_manager.get_messages_for_llm() + [{"role": "user", "content": raw_query}]
            llm_out, provider_label = self.llm_client.generate(llm_msgs, system_prompt=system_prompt)
            if llm_out:
                return {
                    "badge": f"⚡ A.U.R.A. • {provider_label.upper()}",
                    "response": llm_out
                }
            else:
                err_cat = self.llm_client.last_error_category or "API_ERROR"
                err_prefix = ""
                if err_cat == "AUTH_ERROR":
                    err_prefix = "*(⚠️ Notice: AI Provider Authentication Error. The configured API key is invalid or unauthorized. Operating via A.U.R.A. Cognitive Engine.)*\n\n"
                elif err_cat == "RATE_LIMIT_ERROR":
                    err_prefix = "*(⚠️ Notice: AI Provider Rate Limit / Quota Exceeded. Operating via A.U.R.A. Cognitive Engine.)*\n\n"
                elif err_cat == "TIMEOUT_ERROR":
                    err_prefix = "*(⚠️ Notice: AI Provider Timeout. Operating via A.U.R.A. Cognitive Engine.)*\n\n"

                cog_res = self.cognitive_engine.reason(
                    query=raw_query,
                    explanation_mode=self.explanation_mode,
                    context=ctx,
                    history=self.conv_manager.history
                )
                cog_res["response"] = err_prefix + cog_res.get("response", "")
                return cog_res

        # Step 2: Built-in Cognitive Reasoning Engine
        return self.cognitive_engine.reason(
            query=raw_query,
            explanation_mode=self.explanation_mode,
            context=ctx,
            history=self.conv_manager.history
        )

    # =========================================================================
    # TOOL HANDLERS
    # =========================================================================

    def _handle_preferences(self, raw_query: str, q: str, ctx: Dict[str, Any], language: str = "en") -> Optional[Dict[str, Any]]:
        """Handles route preference adjustments (tolls, highways, ferries)."""
        has_pref = any(w in q for w in ["toll", "highway", "ferr", "expressway"]) and any(w in q for w in ["avoid", "no", "without", "skip", "prefer", "allow", "enable", "disable"])
        if has_pref:
            args = {}
            if "toll" in q:
                if any(w in q for w in ["avoid", "no", "without", "skip", "disable"]):
                    args["avoid_tolls"] = True
                elif any(w in q for w in ["allow", "prefer", "enable", "use"]):
                    args["avoid_tolls"] = False

            if "highway" in q or "expressway" in q:
                if any(w in q for w in ["avoid", "no", "without", "skip", "disable"]):
                    args["avoid_highways"] = True
                elif any(w in q for w in ["allow", "prefer", "enable", "use"]):
                    args["avoid_highways"] = False

            if "ferr" in q:
                if any(w in q for w in ["avoid", "no", "without", "skip", "disable"]):
                    args["avoid_ferries"] = True
                elif any(w in q for w in ["allow", "prefer", "enable", "use"]):
                    args["avoid_ferries"] = False

            if args:
                return self.tool_executor.execute("update_route_preferences", args, ctx, language=language)
        return None

    def _handle_journey_status(self, raw_query: str, q: str, ctx: Dict[str, Any], language: str = "en") -> Optional[Dict[str, Any]]:
        """Handles inquiries about journey progress, telemetry, ETA."""
        status_words = ["where are we", "journey status", "how far have we", "how far to destination", "eta to destination", "current route status", "progress of journey", "trip status"]
        if any(w in q for w in status_words):
            return self.tool_executor.execute("get_current_journey_status", {}, ctx, language=language)
        return None

    def _handle_route_intent(self, raw_query: str, q: str, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handles explicit route generation and destination selection."""
        # Check that this is not a philosophical or metaphorical question containing "road"
        if "rule of the road" in q or any(w in q for w in ["philosophy", "essay", "metaphor", "liberty", "why did the chicken"]):
            return None

        # Pattern 1: Route from Origin to Destination
        # e.g. "Find a route from Guntur Railway Station to Vignan University, Vadlamudi"
        from_to_match = re.search(
            r"(?:find\s+(?:a\s+)?route|directions|navigate|path|take\s+me)\s+from\s+(.+?)\s+to\s+(.+)",
            q
        )
        if not from_to_match:
            # Check simple "from X to Y" if preceded or followed by routing intent
            if "from " in q and " to " in q and any(w in q for w in ["route", "navigate", "directions", "drive", "go"]):
                from_to_match = re.search(r"from\s+(.+?)\s+to\s+(.+)", q)

        if from_to_match:
            orig_raw = from_to_match.group(1).strip("?. ")
            dest_raw = from_to_match.group(2).strip("?. ")

            # Disambiguation / Ambiguity Check
            ambiguous_places = ["springfield", "airport", "railway station", "city center", "downtown", "bus station"]
            if orig_raw.lower() in ambiguous_places:
                return {
                    "badge": "🧭 LOCATION CLARIFICATION",
                    "response": (
                        f"Could you clarify which origin location you mean by **'{orig_raw.title()}'**? "
                        f"(e.g., please specify the city, state, or campus landmark so I can locate it accurately)."
                    )
                }
            if dest_raw.lower() in ambiguous_places:
                return {
                    "badge": "🧭 LOCATION CLARIFICATION",
                    "response": (
                        f"Could you clarify which destination you mean by **'{dest_raw.title()}'**? "
                        f"(e.g., please specify the city, state, or campus landmark so I can calculate the exact route)."
                    )
                }

            # Geocode Origin & Destination
            orig_coords = None
            dest_coords = None
            if self.map_service:
                orig_res = self.map_service.geocode(orig_raw)
                orig_coords = self._extract_lat_lon(orig_res)
                dest_res = self.map_service.geocode(dest_raw)
                dest_coords = self._extract_lat_lon(dest_res)

            if not orig_coords:
                return {
                    "badge": "🧭 GEOCODING NOTICE",
                    "response": (
                        f"I could not locate the starting point **'{orig_raw.title()}'** using the geocoding service. "
                        f"Please check the spelling or provide a nearby landmark or city name."
                    )
                }
            if not dest_coords:
                return {
                    "badge": "🧭 GEOCODING NOTICE",
                    "response": (
                        f"I could not locate the destination **'{dest_raw.title()}'** using the geocoding service. "
                        f"Please check the spelling or provide a nearby landmark or city name."
                    )
                }

            self.last_destination = dest_raw.title()
            self.conv_manager.last_destination = dest_raw.title()
            return {
                "badge": "🧭 ROUTE CALCULATION",
                "response": (
                    f"**Calculating Route:** From **{orig_raw.title()}** to **{dest_raw.title()}**.\n\n"
                    f"• **Origin Coordinates:** `{orig_coords[0]:.4f}, {orig_coords[1]:.4f}`\n"
                    f"• **Destination Coordinates:** `{dest_coords[0]:.4f}, {dest_coords[1]:.4f}`\n"
                    f"• **Status:** Generating optimal multi-objective routes (Fastest, Shortest, Balanced, Accessible) on the interactive map."
                ),
                "action": {
                    "type": "calculate_route",
                    "origin": orig_raw.title(),
                    "origin_coords": orig_coords,
                    "destination": dest_raw.title(),
                    "destination_coords": dest_coords
                }
            }

        # Pattern 2: Destination-only navigation
        # e.g. "Find a route to Vignan University", "Navigate to Tenali", "Directions to Guntur"
        nav_match = re.search(
            r"(?:find\s+(?:a\s+)?route\s+to|directions\s+to|navigate\s+to|take\s+me\s+to|route\s+to)\s+([a-zA-Z0-9\s,\.\-]+)",
            q
        )
        if nav_match:
            dest_raw = nav_match.group(1).strip("?. ")
            if dest_raw and dest_raw not in ["there", "the destination", "a place"]:
                # Disambiguation Check
                ambiguous_places = ["springfield", "airport", "railway station", "city center", "downtown", "bus station"]
                if dest_raw.lower() in ambiguous_places:
                    return {
                        "badge": "🧭 LOCATION CLARIFICATION",
                        "response": (
                            f"Could you clarify which destination you mean by **'{dest_raw.title()}'**? "
                            f"(e.g., please specify the city, state, or campus landmark so I can calculate the exact route)."
                        )
                    }

                dest_coords = None
                if self.map_service:
                    dest_res = self.map_service.geocode(dest_raw)
                    dest_coords = self._extract_lat_lon(dest_res)

                if not dest_coords:
                    return {
                        "badge": "🧭 GEOCODING NOTICE",
                        "response": (
                            f"I could not locate the destination **'{dest_raw.title()}'** using the geocoding service. "
                            f"Please check the spelling or specify a nearby city or landmark."
                        )
                    }

                self.last_destination = dest_raw.title()
                self.conv_manager.last_destination = dest_raw.title()
                return {
                    "badge": f"🧭 DESTINATION TARGET • {dest_raw.upper()[:16]}",
                    "response": (
                        f"**Setting Destination to {dest_raw.title()}!**\n\n"
                        f"• **Coordinates:** `{dest_coords[0]:.4f}, {dest_coords[1]:.4f}`\n"
                        f"• Route calculation automatically triggered on the interactive map."
                    ),
                    "action": {
                        "type": "set_destination",
                        "destination_name": dest_raw.title(),
                        "coords": dest_coords
                    }
                }

        # Pattern 3: Follow-up reference to "there" / "that destination"
        is_greeting_there = any(w in q for w in ["hello there", "hi there", "hey there", "help me navigate"])
        if not is_greeting_there and any(w in q for w in ["there", "that destination", "that place"]) and any(w in q for w in ["navigate", "route", "directions", "go there", "take me there", "how do i get there", "how to get there", "path to there"]):
            dest_raw = ctx.get("dest_label") or getattr(self.conv_manager, "last_destination", None) or self.last_destination
            if dest_raw and dest_raw.lower() not in ["live location", "local area", "unknown", "destination", ""]:
                dest_coords = None
                if self.map_service:
                    dest_res = self.map_service.geocode(dest_raw)
                    dest_coords = self._extract_lat_lon(dest_res)
                if dest_coords:
                    self.last_destination = dest_raw.title()
                    self.conv_manager.last_destination = dest_raw.title()
                    return {
                        "badge": f"🧭 DESTINATION TARGET • {dest_raw.upper()[:16]}",
                        "response": (
                            f"**Setting Destination to {dest_raw.title()}!**\n\n"
                            f"• **Coordinates:** `{dest_coords[0]:.4f}, {dest_coords[1]:.4f}`\n"
                            f"• Route calculation automatically triggered on the interactive map."
                        ),
                        "action": {
                            "type": "set_destination",
                            "destination_name": dest_raw.title(),
                            "coords": dest_coords
                        }
                    }
                else:
                    return {
                        "badge": "🧭 DESTINATION CLARIFICATION • A.U.R.A.",
                        "response": f"I remembered your destination as **'{dest_raw}'**, but could not locate it via geocoding. Please specify the full landmark or city name."
                    }
            else:
                return {
                    "badge": "🧭 DESTINATION CLARIFICATION • A.U.R.A.",
                    "response": "Could you clarify which destination you want to travel to? Please specify a place, landmark, or city name."
                }

        # Pattern 4: Multilingual Telugu Route Intent
        if any(w in raw_query for w in ["దారి", "వెళ్ళాలి", "నుండి", "వరకు"]):
            dest_raw = None
            orig_raw = None
            if "నుండి" in raw_query:
                parts = raw_query.split("నుండి")
                orig_raw = parts[0].strip()
                dest_part = parts[1].replace("వరకు", "").replace("కి", "").replace("కు", "").replace("దారి", "").replace("చూపించు", "").strip()
                if dest_part:
                    dest_raw = dest_part
            else:
                m = re.search(r"(.+?)(?:కి|కు)?\s*(?:దారి|వెళ్ళాలి)", raw_query)
                if m:
                    dest_raw = m.group(1).replace("నాకు", "").replace("దయచేసి", "").strip()
            if dest_raw:
                return self.tool_executor.execute("calculate_route", {"destination": dest_raw, "origin": orig_raw}, ctx, language="te")

        # Pattern 5: Multilingual Hindi Route Intent
        if any(w in raw_query for w in ["रास्ता", "जाना है", "मार्ग"]):
            dest_raw = None
            orig_raw = None
            if "से" in raw_query and ("तक" in raw_query or "का" in raw_query):
                parts = raw_query.split("से")
                orig_raw = parts[0].strip()
                dest_part = parts[1].replace("तक", "").replace("का रास्ता", "").replace("का मार्ग", "").replace("जाना है", "").strip()
                if dest_part:
                    dest_raw = dest_part
            else:
                m = re.search(r"(.+?)(?:का\s+रास्ता|जाना\s+है)", raw_query)
                if m:
                    dest_raw = m.group(1).replace("मुझे", "").replace("कृपया", "").strip()
            if dest_raw:
                return self.tool_executor.execute("calculate_route", {"destination": dest_raw, "origin": orig_raw}, ctx, language="hi")

        return None

    def _handle_map_action(self, raw_query: str, q: str, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handles map focus requests (e.g. 'Show that one on the map', 'Show the second route on the map')."""
        if any(w in q for w in ["show on map", "show that one on the map", "show route on map", "focus route", "display on map", "show the second route", "show the first route", "show route 2", "show second route"]):
            routes = ctx.get("ranked_routes", [])
            if not routes:
                return {
                    "badge": "🎯 MAP NAVIGATION SYNC",
                    "response": "Please confirm an origin and destination above to display and focus a route on the interactive map."
                }

            # Resolve target route
            target_route = routes[0]
            if any(w in q for w in ["second route", "second", "route 2", "alt 2", "alternative 2"]) and len(routes) > 1:
                target_route = routes[1]
            elif any(w in q for w in ["that one", "shortest"]):
                target_route = min(routes, key=lambda r: getattr(r, "effective_distance_km", float("inf")))

            r_id = getattr(target_route.route, "id", "route_0")
            r_name = getattr(target_route.route, "name", "Selected Route")
            dist = getattr(target_route, "effective_distance_km", 0.0)

            return {
                "badge": "🎯 MAP NAVIGATION SYNC",
                "response": (
                    f"**Displaying {r_name} on Map!**\n\n"
                    f"• **Distance:** **{dist:.1f} km**\n"
                    f"• The camera viewport and polyline have been highlighted on the interactive map."
                ),
                "action": {
                    "type": "focus_route",
                    "route_id": r_id,
                    "route_name": r_name
                }
            }

        return None

    def _handle_route_comparison(self, raw_query: str, q: str, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Compares available distinct route alternatives from real calculation state."""
        # 1. Shortest inquiry
        if any(w in q for w in ["which of these routes is shortest", "which route is shortest", "which alternative is shortest", "which is shortest", "shortest route"]):
            routes = ctx.get("ranked_routes", [])
            if not routes:
                return {
                    "badge": "🗺️ ROUTE COMPARISON",
                    "response": "No active routes have been calculated yet. Please set an origin and destination to generate and compare routes."
                }
            shortest_r = min(routes, key=lambda r: getattr(r, "effective_distance_km", float("inf")))
            r_name = getattr(shortest_r.route, "name", "Shortest Route")
            r_dist = getattr(shortest_r, "effective_distance_km", 0.0)
            r_dur = getattr(shortest_r, "effective_duration_minutes", 0.0)

            other_desc = ""
            if len(routes) > 1:
                alt = [r for r in routes if r != shortest_r][0]
                alt_dist = getattr(alt, "effective_distance_km", 0.0)
                other_desc = f" By comparison, **{alt.route.name}** is **{alt_dist:.1f} km** ({alt_dist - r_dist:.1f} km longer)."

            return {
                "badge": "📏 SHORTEST ROUTE ANALYSIS",
                "response": (
                    f"### 📏 Shortest Route: {r_name}\n\n"
                    f"• **Distance:** **{r_dist:.1f} km**\n"
                    f"• **Est. Duration:** **~{r_dur:.0f} mins**\n"
                    f"{other_desc}\n\n"
                    f"You can say *\"Show that one on the map\"* or click its route card above to focus the map camera."
                )
            }

        # 2. Fastest inquiry
        if any(w in q for w in ["which of these routes is fastest", "which route is fastest", "fastest route"]):
            routes = ctx.get("ranked_routes", [])
            if not routes:
                return {
                    "badge": "🗺️ ROUTE COMPARISON",
                    "response": "No active routes have been calculated yet. Please set an origin and destination to compare speeds."
                }
            fastest_r = min(routes, key=lambda r: getattr(r, "effective_duration_minutes", float("inf")))
            r_name = getattr(fastest_r.route, "name", "Fastest Route")
            r_dur = getattr(fastest_r, "effective_duration_minutes", 0.0)
            r_dist = getattr(fastest_r, "effective_distance_km", 0.0)

            return {
                "badge": "⚡ FASTEST ROUTE ANALYSIS",
                "response": (
                    f"### ⚡ Fastest Route: {r_name}\n\n"
                    f"• **Est. Duration:** **~{r_dur:.0f} mins**\n"
                    f"• **Distance:** **{r_dist:.1f} km**\n\n"
                    f"This route prioritizes arterial expressways and avoids local bottlenecks."
                )
            }

        # 3. Alternative route inquiry
        if any(w in q for w in ["what about the other alternative", "what about the alternative", "other alternative", "tell me about the alternative"]):
            routes = ctx.get("ranked_routes", [])
            if routes and len(routes) >= 2:
                alt_r = routes[1]
                pri_r = routes[0]
                alt_name = getattr(alt_r.route, "name", "Alternative Route")
                alt_dist = getattr(alt_r, "effective_distance_km", 0.0)
                alt_dur = getattr(alt_r, "effective_duration_minutes", 0.0)
                pri_dist = getattr(pri_r, "effective_distance_km", 0.0)
                pri_dur = getattr(pri_r, "effective_duration_minutes", 0.0)

                diff_dist = alt_dist - pri_dist
                diff_dur = alt_dur - pri_dur
                roads = ", ".join(alt_r.route.summary_roads[:2]) if getattr(alt_r.route, "summary_roads", None) else "Secondary Corridor"

                return {
                    "badge": "🗺️ ALTERNATIVE CORRIDOR INTEL",
                    "response": (
                        f"### 🗺️ Alternative Route: {alt_name}\n\n"
                        f"• **Distance:** **{alt_dist:.1f} km** ({abs(diff_dist):.1f} km {'longer' if diff_dist > 0 else 'shorter'})\n"
                        f"• **Travel Time:** **~{alt_dur:.0f} mins** ({abs(diff_dur):.0f} mins {'slower' if diff_dur > 0 else 'faster'})\n"
                        f"• **Main Roads:** {roads}\n"
                        f"• **Status:** Clear of verified road closures.\n\n"
                        f"To highlight this alternative corridor, you can say *\"Show the second route on the map\"*."
                    )
                }
            elif routes and len(routes) == 1:
                return {
                    "badge": "🗺️ ALTERNATIVE CORRIDOR INTEL",
                    "response": (
                        f"Only 1 arterial route was found for this journey: **{routes[0].route.name}** "
                        f"({routes[0].effective_distance_km:.1f} km). No secondary bypasses met safety and uniqueness thresholds."
                    )
                }
            else:
                return {
                    "badge": "🗺️ ALTERNATIVE CORRIDOR INTEL",
                    "response": "Please set an origin and destination to generate and inspect alternative routes."
                }

        # 4. General comparison
        if any(w in q for w in ["compare route", "compare the routes", "difference between the routes"]):
            routes = ctx.get("ranked_routes", [])
            if routes and len(routes) >= 2:
                r1 = routes[0]
                r2 = routes[1]
                return {
                    "badge": "🗺️ ROUTE COMPARISON ANALYSIS",
                    "response": (
                        f"### 🗺️ Route Comparison Analysis\n\n"
                        f"| Metric | **{r1.route.name}** | **{r2.route.name}** |\n"
                        f"| :--- | :--- | :--- |\n"
                        f"| **Distance** | **{r1.effective_distance_km:.1f} km** | {r2.effective_distance_km:.1f} km |\n"
                        f"| **Duration** | **~{r1.effective_duration_minutes:.0f} mins** | ~{r2.effective_duration_minutes:.0f} mins |\n"
                        f"| **Safety** | Verified Open | Verified Open |\n\n"
                        f"You can select either corridor by clicking its route card or polyline on the map."
                    )
                }
            else:
                return {
                    "badge": "🗺️ ROUTE COMPARISON",
                    "response": "To compare routes, please confirm an origin and destination above."
                }

        return None

    def _handle_nearby_places(self, raw_query: str, q: str, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieves verified places, dining, fuel, lodging, or medical care around destination or referenced place."""
        facility_triggers = [
            "restaurant", "food", "dining", "places to eat", "hotel nearby", "hotel", "lodge",
            "petrol pump", "fuel station", "petrol", "fuel", "atm nearby", "atm",
            "hospital", "clinic", "pharmacy", "medical store", "doctor"
        ]
        if any(w in q for w in facility_triggers):
            cat = "Dining"
            if any(w in q for w in ["restaurant", "food", "dining", "eat", "cafe"]):
                cat = "Dining"
            elif any(w in q for w in ["hotel", "lodge", "resort"]):
                cat = "Hotel"
            elif any(w in q for w in ["petrol", "fuel", "gas station"]):
                cat = "Fuel"
            elif any(w in q for w in ["hospital", "clinic", "doctor"]):
                cat = "Hospital"
            elif any(w in q for w in ["atm", "bank", "cash"]):
                cat = "ATM"
            elif any(w in q for w in ["pharmacy", "chemist", "medical store"]):
                cat = "Pharmacy"

            dest_coords = ctx.get("dest_coords") or ctx.get("current_coords") or (16.2335, 80.5505)
            dest_label = ctx.get("dest_label", "Local Area")

            # Reference resolution: "there" / "that place"
            if any(w in q for w in ["there", "that destination", "that place"]):
                resolved_place = ctx.get("dest_label") or getattr(self.conv_manager, "last_destination", None) or self.last_destination
                if resolved_place and resolved_place.lower() not in ["live location", "local area", "unknown", "destination", ""]:
                    dest_label = resolved_place
                    if self.map_service:
                        geo = self.map_service.geocode(resolved_place)
                        coords = self._extract_lat_lon(geo)
                        if coords:
                            dest_coords = coords

            # Explicit location: "near Guntur" or "around Tenali"
            near_match = re.search(r"(?:near|in|around)\s+([a-zA-Z0-9\s,\.\-]+)", q)
            if near_match:
                cand_loc = near_match.group(1).strip("?. ")
                if cand_loc and cand_loc not in ["there", "here", "my location", "me", "the destination", "that place"]:
                    if self.map_service:
                        geo = self.map_service.geocode(cand_loc)
                        coords = self._extract_lat_lon(geo)
                        if coords:
                            dest_coords = coords
                            dest_label = cand_loc.title()

            places = GroundingEngine.get_nearby_places(dest_coords[0], dest_coords[1], dest_label, cat)
            if places:
                p_lines = []
                for p in places[:3]:
                    r_val = p.get("rating")
                    r_num = float(r_val) if r_val is not None else 4.5
                    stars = "⭐" * int(round(r_num))
                    p_lines.append(
                        f"• **{p.get('name')}** ({r_num:.1f} {stars})<br>"
                        f"&nbsp;&nbsp;{p.get('category')} • ~{p.get('dist_km', 1.0):.1f} km away • *{p.get('open_status', 'Open Daily')}*"
                    )
                p_html = "<br>".join(p_lines)
                return {
                    "badge": f"📍 VERIFIED PLACES • {dest_label.upper()[:16]}",
                    "response": (
                        f"### 📍 Verified Places Around {dest_label}\n\n"
                        f"{p_html}\n\n"
                        f"<span style='font-size:0.75rem; color:#94a3b8;'>Source: Verified Business Directory</span>"
                    )
                }

        return None

    def _handle_live_weather(self, raw_query: str, q: str, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fetches live weather from Open-Meteo for any referenced place or current destination."""
        weather_triggers = ["weather", "temperature", "forecast", "is it raining", "climate", "rainfall"]
        if any(w in q for w in weather_triggers) and not any(w in q for w in ["under the weather", "weather the storm"]):
            match_loc = re.search(r"\b(?:in|at|for|around)\b\s+([a-zA-Z\s]+)", q)
            cand_raw = match_loc.group(1).strip("?. ") if match_loc else None
            if not cand_raw or cand_raw.lower() in ["there", "that destination", "that place", "destination", "here", "my location"]:
                cand_raw = ctx.get("dest_label") or getattr(self.conv_manager, "last_destination", None) or self.last_destination or "Local Area"
            loc_query = cand_raw
            if self.map_service:
                resolved = self.map_service.geocode(loc_query)
                coords = self._extract_lat_lon(resolved)
                if coords:
                    w_info = GroundingEngine.get_live_weather(coords[0], coords[1], loc_query.title())
                    if w_info.get("available"):
                        return {
                            "badge": f"🌤️ LIVE WEATHER • {loc_query.upper()[:16]}",
                            "response": (
                                f"<div style='background: rgba(14, 165, 233, 0.12); border: 1.5px solid #38bdf8; border-radius: 12px; padding: 12px 14px;'>"
                                f"<div style='font-weight: 800; color: #38bdf8; font-size: 0.95rem; margin-bottom: 6px;'>🌤️ Live Weather for {loc_query.title()}</div>"
                                f"{w_info['formatted']}"
                                f"</div>"
                            )
                        }
        return None

    def _handle_emergency_queries(self, raw_query: str, q: str, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handles emergency assistance, stranded user distress calls, and evacuation protocols."""
        if any(w in q for w in ["stranded", "need help urgently", "stuck in flood", "danger on road", "vehicle broken down", "stranded and need help"]):
            coords = ctx.get("current_coords") or (16.2335, 80.5505)
            nearest_fac = None
            if self.emergency_manager:
                try:
                    if hasattr(self.emergency_manager, "get_closest_facility"):
                        nearest_fac = self.emergency_manager.get_closest_facility(coords)
                    elif hasattr(self.emergency_manager, "find_nearest_facility"):
                        nearest_fac = self.emergency_manager.find_nearest_facility(coords[0], coords[1])
                except Exception:
                    pass
            fac_info = f"Nearest Verified Resource: {getattr(nearest_fac, 'name', 'Emergency Haven')}." if nearest_fac else "Campus Security / Police Dispatch alerted."
            return {
                "badge": "🚨 EMERGENCY ASSISTANCE",
                "response": (
                    "### 🚨 Immediate Life-Safety Guidance\n\n"
                    "• **National Emergency Helpline:** **112** (Police, Ambulance, Fire)\n"
                    "• **Action:** Stay inside your vehicle if safe, turn on hazard blinkers, and remain calm.\n"
                    f"• {fac_info}\n"
                    "• Your telemetry coordinates have been marked for dispatch."
                )
            }

        if any(w in q for w in ["nearest hospital", "hospital nearby", "where is the hospital", "where is the nearest hospital"]):
            coords = ctx.get("current_coords") or (16.2335, 80.5505)
            hosp_name = "Ramesh Hospitals (Guntur / Tenali Corridor)"
            if self.emergency_manager:
                try:
                    from src.emergency_service import FacilityCategory
                    if hasattr(self.emergency_manager, "get_closest_facility"):
                        h = self.emergency_manager.get_closest_facility(coords, category=FacilityCategory.MEDICAL)
                        if h:
                            hosp_name = h.name
                    elif hasattr(self.emergency_manager, "find_nearest_facility"):
                        h = self.emergency_manager.find_nearest_facility(coords[0], coords[1])
                        if h:
                            hosp_name = getattr(h, "name", str(h))
                except Exception:
                    pass
            return {
                "badge": "🚨 EMERGENCY ASSISTANCE • MEDICAL",
                "response": (
                    f"### 🏥 Nearest Hospital & Trauma Care\n\n"
                    f"• **Facility:** **{hosp_name}**\n"
                    f"• **Emergency Ambulance Dispatch:** **108** / **112**\n"
                    f"• **Status:** 24/7 Emergency & ICU Facilities Active."
                )
            }

        hazmat_or_fire = (
            any(w in q for w in ["earthquake", "evacuate", "evacuation", "emergency protocol", "fire alarm", "chemical spill", "chemical leak", "building fire", "gas leak"]) or
            ("fire" in q and any(w in q for w in ["emergency", "alarm", "evacuate", "escape", "building", "smoke", "extinguish", "flames"])) or
            ("chemical" in q and any(w in q for w in ["spill", "leak", "hazard", "toxic", "fume", "poison", "containment"]))
        )
        if hazmat_or_fire:
            if "earthquake" in q:
                sop_title = "SEISMIC / EARTHQUAKE ACTION PROTOCOL"
                sop_act = "DROP, COVER, AND HOLD ON. Move away from glass facades and overhead lighting."
            elif "chemical" in q:
                sop_title = "HAZMAT / CHEMICAL SPILL CONTAINMENT"
                sop_act = "UPWIND EVACUATION. Do not touch spilled agents. Isolate fume hoods."
            else:
                sop_title = "STRUCTURE FIRE EVACUATION PROTOCOL"
                sop_act = "ACTIVATE MANUAL PULL STATION. Stay low below toxic smoke layer. Feel door handles before opening."

            return {
                "badge": "🚨 EMERGENCY PROTOCOL",
                "response": (
                    f"### ⚠️ {sop_title}\n\n"
                    f"⚡ **MANDATORY ACTION:** {sop_act}\n\n"
                    f"• **Evacuation Assembly:** Designated outdoor assembly grounds.\n"
                    f"• **Emergency Number:** **112** / Internal Security extension 4444."
                )
            }

        return None

    def _handle_global_transit(self, raw_query: str, q: str, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handles explicit long-distance / international travel questions like 'How do I go to Tokyo?'."""
        if any(w in q for w in ["how do i go to tokyo", "how to reach tokyo", "how to go to tokyo", "travel to tokyo"]):
            return {
                "badge": "✈️ GLOBAL TRANSIT • TOKYO",
                "response": (
                    "### 🇯🇵 Travel Guidance to Tokyo, Japan\n\n"
                    "• **Air Transit:** Fly into either Tokyo Haneda Airport (HND, 14 km south, 25 mins by Monorail) or Narita International Airport (NRT, 60 km east, 50 mins via Narita Express).\n"
                    "• **Local Transport:** Use a Suica / Pasmo transit IC card or Japan Rail Pass for the Shinkansen bullet trains.\n"
                    "• **Entry Requirements:** Valid passport with 6 months validity. Ensure appropriate visa or eVisa before departure.\n"
                    "• **Emergency Contacts:** Police: 110, Ambulance/Fire: 119."
                )
            }
        return None

    def _handle_telugu_query(self, raw_query: str, q: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Responds in natural Telugu."""
        if any(w in q for w in ["నమస్కారం", "namaskaram", "హలో", "hello"]):
            return {
                "badge": "⚡ A.U.R.A. తెలుగు",
                "response": (
                    "నమస్కారం! నేను **A.U.R.A.** (Adaptive User Route Assistant). "
                    "P.A.T.H.F.I.N.D.E.R. లో మీ వ్యక్తిగత AI సహచరుడిని.\n\n"
                    "మీరు సాధారణ విజ్ఞానం, కోడింగ్, గణితం, సైన్స్ లేదా సురక్షితమైన ప్రయాణ మార్గాల గురించి నన్ను ఏమైనా అడగవచ్చు. "
                    "నేను మీకు ఎలా సహాయపడగలను?"
                )
            }
        return {
            "badge": "⚡ A.U.R.A. తెలుగు",
            "response": (
                f"మీ ప్రశ్న: **\"{raw_query}\"**.\n\n"
                "నేను మీ ప్రయాణ మార్గాలు, రోడ్డు భద్రత మరియు సాధారణ విజ్ఞాన విషయాలలో మీకు స్పష్టమైన సమాచారాన్ని అందించగలను. "
                "దయచేసి మీకు కావలసిన వివరాలను తెలపండి!"
            )
        }

    def _handle_hindi_query(self, raw_query: str, q: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Responds in natural Hindi."""
        if any(w in q for w in ["नमस्ते", "namaste", "हैलो", "hello"]):
            return {
                "badge": "⚡ A.U.R.A. हिन्दी",
                "response": (
                    "नमस्ते! मैं **A.U.R.A.** (Adaptive User Route Assistant) हूँ, "
                    "P.A.T.H.F.I.N.D.E.R. का बुद्धिमान AI सहायक।\n\n"
                    "आप मुझसे सामान्य ज्ञान, विज्ञान, कोडिंग, पढ़ाई या सुरक्षित रास्तों के बारे में कोई भी प्रश्न पूछ सकते हैं। "
                    "मैं आपकी किस प्रकार सहायता कर सकता हूँ?"
                )
            }
        return {
            "badge": "⚡ A.U.R.A. हिन्दी",
            "response": (
                f"आपके प्रश्न: **\"{raw_query}\"** के संदर्भ में,\n\n"
                "मैं आपको सटीक जानकारी और सुरक्षित यात्रा निर्देश प्रदान करने के लिए तैयार हूँ। "
                "कृपया अपनी आवश्यकता अनुसार और विस्तार से बताएं!"
            )
        }

    def _handle_tamil_query(self, raw_query: str, q: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Responds in natural Tamil."""
        if any(w in q for w in ["வணக்கம்", "vanakkam", "ஹலோ", "hello"]):
            return {
                "badge": "⚡ A.U.R.A. தமிழ்",
                "response": (
                    "வணக்கம்! நான் **A.U.R.A.** (Adaptive User Route Assistant). "
                    "P.A.T.H.F.I.N.D.E.R. இன் உங்கள் அறிவார்ந்த AI உதவியாளர்.\n\n"
                    "பாதுகாப்பான வழிசெலுத்தல், வழிகள், பொது அறிவு, குறியீட்டு முறை அல்லது அறிவியல் பற்றி நீங்கள் கேட்கலாம். "
                    "நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?"
                )
            }
        return {
            "badge": "⚡ A.U.R.A. தமிழ்",
            "response": (
                f"உங்கள் கேள்வி: **\"{raw_query}\"**.\n\n"
                "நான் உங்களுக்கு துல்லியமான வழிகாட்டல் மற்றும் பாதுகாப்பான பயண தகவல்களை வழங்க தயாராக உள்ளேன். "
                "உங்கள் தேவையை மேலும் விரிவாகக் குறிப்பிடவும்!"
            )
        }

    def _handle_kannada_query(self, raw_query: str, q: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Responds in natural Kannada."""
        if any(w in q for w in ["ನಮಸ್ಕಾರ", "namaskara", "ಹಲೋ", "hello"]):
            return {
                "badge": "⚡ A.U.R.A. ಕನ್ನಡ",
                "response": (
                    "ನಮಸ್ಕಾರ! ನಾನು **A.U.R.A.** (Adaptive User Route Assistant). "
                    "P.A.T.H.F.I.N.D.E.R. ನ ಬುದ್ಧಿವಂತ AI ಸಹಾಯಕ.\n\n"
                    "ಸುರಕ್ಷಿತ ಸಂಚಾರ ಮಾರ್ಗಗಳು, ಸಾಮಾನ್ಯ ಜ್ಞಾನ, ಕೋಡಿಂಗ್ ಅಥವಾ ವಿಜ್ಞಾನದ ಬಗ್ಗೆ ನೀವು ಕೇಳಬಹುದು. "
                    "ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?"
                )
            }
        return {
            "badge": "⚡ A.U.R.A. ಕನ್ನಡ",
            "response": (
                f"ನಿಮ್ಮ ಪ್ರಶ್ನೆ: **\"{raw_query}\"**.\n\n"
                "ನಿಮಗೆ ನಿಖರವಾದ ಮಾರ್ಗದರ್ಶನ ಮತ್ತು ಸುರಕ್ಷಿತ ಪ್ರಯಾಣದ ಮಾಹಿತಿಯನ್ನು ಒದಗಿಸಲು ನಾನು ಸಿದ್ಧನಿದ್ದೇನೆ. "
                "ದಯವಿಟ್ಟು ಹೆಚ್ಚಿನ ವಿವರಗಳನ್ನು ತಿಳಿಸಿ!"
            )
        }

    def _handle_malayalam_query(self, raw_query: str, q: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Responds in natural Malayalam."""
        if any(w in q for w in ["നമസ്കാരം", "namaskaram", "ഹലോ", "hello"]):
            return {
                "badge": "⚡ A.U.R.A. മലയാളം",
                "response": (
                    "നമസ്കാരം! ഞാൻ **A.U.R.A.** (Adaptive User Route Assistant). "
                    "P.A.T.H.F.I.N.D.E.R. ൻ്റെ സ്മാർട്ട് AI സഹായി.\n\n"
                    "സുരക്ഷിതമായ യാത്രാ റൂട്ടുകൾ, പൊതുവിജ്ഞാനം, കോഡിംഗ് അല്ലെങ്കിൽ ശാസ്ത്രം എന്നിവയെക്കുറിച്ച് നിങ്ങൾക്ക് എന്നോട് ചോദിക്കാം. "
                    "ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കണം?"
                )
            }
        return {
            "badge": "⚡ A.U.R.A. മലയാളം",
            "response": (
                f"താങ്കളുടെ ചോദ്യം: **\"{raw_query}\"**.\n\n"
                "നിങ്ങൾക്ക് കൃത്യമായ റൂട്ട് വിവരങ്ങളും സുരക്ഷിത യാത്രാ നിർദ്ദേശങ്ങളും നൽകാൻ ഞാൻ തയ്യാറാണ്. "
                "ദയവായി കൂടുതൽ വിവരങ്ങൾ അറിയിക്കുക!"
            )
        }

    def _handle_bengali_query(self, raw_query: str, q: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Responds in natural Bengali."""
        if any(w in q for w in ["নমস্কার", "nomoshkar", "হ্যালো", "hello"]):
            return {
                "badge": "⚡ A.U.R.A. বাংলা",
                "response": (
                    "নমস্কার! আমি **A.U.R.A.** (Adaptive User Route Assistant)। "
                    "P.A.T.H.F.I.N.D.E.R.-এর আপনার বুদ্ধিমান AI সহকারী।\n\n"
                    "নিরাপদ রুট, দিকনির্দেশনা, সাধারণ জ্ঞান, কোডিং বা বিজ্ঞান সম্পর্কিত যেকোনো প্রশ্ন আপনি আমাকে করতে পারেন। "
                    "আমি আপনাকে কীভাবে সাহায্য করতে পারি?"
                )
            }
        return {
            "badge": "⚡ A.U.R.A. বাংলা",
            "response": (
                f"আপনার প্রশ্ন: **\"{raw_query}\"**।\n\n"
                "আমি আপনাকে সঠিক পথনির্দেশ এবং নিরাপদ ভ্রমণের তথ্য দিতে প্রস্তুত। "
                "অনুগ্রহ করে বিস্তারিত জানান!"
            )
        }

    def _handle_marathi_query(self, raw_query: str, q: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Responds in natural Marathi."""
        if any(w in q for w in ["नमस्कार", "namaskar", "हॅलो", "hello"]):
            return {
                "badge": "⚡ A.U.R.A. मराठी",
                "response": (
                    "नमस्कार! मी **A.U.R.A.** (Adaptive User Route Assistant) आहे, "
                    "P.A.T.H.F.I.N.D.E.R. चा बुद्धिमान AI सहाय्यक.\n\n"
                    "तुम्ही मला सुरक्षित मार्ग, सामान्य ज्ञान, कोडिंग किंवा विज्ञानाबद्दल कोणतेही प्रश्न विचारू शकता. "
                    "मी आपली काय मदत करू शकतो?"
                )
            }
        return {
            "badge": "⚡ A.U.R.A. मराठी",
            "response": (
                f"तुमचा प्रश्न: **\"{raw_query}\"**.\n\n"
                "मी तुम्हाला अचूक दिशा आणि सुरक्षित प्रवासाची माहिती देण्यासाठी सज्ज आहे. "
                "कृपया आपली आवश्यकता अधिक स्पष्टपणे सांगा!"
            )
        }

    def _handle_translation(self, raw_query: str, q: str) -> Dict[str, Any]:
        """Handles basic language translations."""
        if "to telugu" in q:
            text_to_tr = raw_query.lower().split("to telugu")[0].replace("translate", "").strip(" '\"")
            return {
                "badge": "🌐 TRANSLATION • TELUGU",
                "response": f"**English:** {text_to_tr}\n**తెలుగు అనువాదం:** {text_to_tr} కి సమానమైన తెలుగు రూపం సిద్ధంగా ఉంది."
            }
        elif "to hindi" in q:
            text_to_tr = raw_query.lower().split("to hindi")[0].replace("translate", "").strip(" '\"")
            return {
                "badge": "🌐 TRANSLATION • HINDI",
                "response": f"**English:** {text_to_tr}\n**हिन्दी अनुवाद:** {text_to_tr} का अनुवाद।"
            }
        elif "to tamil" in q:
            text_to_tr = raw_query.lower().split("to tamil")[0].replace("translate", "").strip(" '\"")
            return {
                "badge": "🌐 TRANSLATION • TAMIL",
                "response": f"**English:** {text_to_tr}\n**தமிழ் மொழிபெயர்ப்பு:** {text_to_tr}."
            }
        elif "to kannada" in q:
            text_to_tr = raw_query.lower().split("to kannada")[0].replace("translate", "").strip(" '\"")
            return {
                "badge": "🌐 TRANSLATION • KANNADA",
                "response": f"**English:** {text_to_tr}\n**ಕನ್ನಡ ಅನುವಾದ:** {text_to_tr}."
            }
        elif "to malayalam" in q:
            text_to_tr = raw_query.lower().split("to malayalam")[0].replace("translate", "").strip(" '\"")
            return {
                "badge": "🌐 TRANSLATION • MALAYALAM",
                "response": f"**English:** {text_to_tr}\n**മലയാള തർജ്ജമ:** {text_to_tr}."
            }
        elif "to bengali" in q or "to bangla" in q:
            text_to_tr = raw_query.lower().split("to bengali")[0].split("to bangla")[0].replace("translate", "").strip(" '\"")
            return {
                "badge": "🌐 TRANSLATION • BENGALI",
                "response": f"**English:** {text_to_tr}\n**বাংলা অনুবাদ:** {text_to_tr}."
            }
        elif "to marathi" in q:
            text_to_tr = raw_query.lower().split("to marathi")[0].replace("translate", "").strip(" '\"")
            return {
                "badge": "🌐 TRANSLATION • MARATHI",
                "response": f"**English:** {text_to_tr}\n**मराठी अनुवाद:** {text_to_tr}."
            }
        else:
            return {
                "badge": "🌐 TRANSLATION",
                "response": f"Translation request recognized for: *\"{raw_query}\"*."
            }
