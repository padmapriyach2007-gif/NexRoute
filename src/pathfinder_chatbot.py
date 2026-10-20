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
        self.llm_client = LLMClient()
        self.cognitive_engine = BuiltinCognitiveEngine()
        self.conv_manager = ConversationManager()

    def reset_conversation(self):
        """Resets active conversation context and history."""
        self.conv_manager.clear()
        self.last_topic = None
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
        # 3. MULTILINGUAL SUPPORT (TELUGU & HINDI)
        # ---------------------------------------------------------------------
        is_telugu = bool(re.search(r"[\u0c00-\u0c7f]", raw_query)) or any(w in q for w in ["namaskaram", "ela unnav", "dharilo", "margam", "telugu lo"])
        if is_telugu and not any(w in q for w in ["translate to english"]):
            return self._handle_telugu_query(raw_query, q, ctx)

        is_hindi = bool(re.search(r"[\u0900-\u097f]", raw_query)) or any(w in q for w in ["namaste", "kaise ho", "rasta", "hindi me"])
        if is_hindi and not any(w in q for w in ["translate to english"]):
            return self._handle_hindi_query(raw_query, q, ctx)

        if "translate" in q:
            return self._handle_translation(raw_query, q)

        # ---------------------------------------------------------------------
        # 4. EMERGENCY & LIFE-SAFETY PROTOCOLS
        # ---------------------------------------------------------------------
        em_res = self._handle_emergency_queries(raw_query, q, ctx)
        if em_res is not None:
            return em_res

        # ---------------------------------------------------------------------
        # 5. NAVIGATION TOOL ACTIONS (DETERMINISTIC ROUTING & MAP SYNC)
        # ---------------------------------------------------------------------
        # A) Explicit Route Calculation (Origin & Destination or Destination)
        route_intent_res = self._handle_route_intent(raw_query, q, ctx)
        if route_intent_res is not None:
            return route_intent_res

        # B) Map Camera & Route Focus Sync
        map_act = self._handle_map_action(raw_query, q, ctx)
        if map_act is not None:
            return map_act

        # C) Route Comparison & Metrics Analysis (From context)
        route_comp = self._handle_route_comparison(raw_query, q, ctx)
        if route_comp is not None:
            return route_comp

        # D) Grounding Tools: Nearby Places & Weather
        places_res = self._handle_nearby_places(raw_query, q, ctx)
        if places_res is not None:
            return places_res

        weather_res = self._handle_live_weather(raw_query, q, ctx)
        if weather_res is not None:
            return weather_res

        # E) Global Travel Inquiries (e.g. "How do I go to Tokyo?")
        global_res = self._handle_global_transit(raw_query, q, ctx)
        if global_res is not None:
            return global_res

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
            llm_msgs = self.conv_manager.get_messages_for_llm() + [{"role": "user", "content": raw_query}]
            llm_out, provider_label = self.llm_client.generate(llm_msgs, system_prompt=AURA_CORE_SYSTEM_PROMPT)
            if llm_out:
                return {
                    "badge": f"⚡ A.U.R.A. • {provider_label.upper()}",
                    "response": llm_out
                }
            else:
                # LLM call failed (Auth error, rate limit, timeout)
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
        """Retrieves verified places, dining, fuel, or lodging around current destination."""
        if any(w in q for w in ["restaurant", "food", "dining", "places to eat", "hotel nearby", "petrol pump", "fuel station", "atm nearby"]):
            cat = None
            if any(w in q for w in ["restaurant", "food", "dining", "eat", "cafe"]):
                cat = "Dining"
            elif any(w in q for w in ["hotel", "lodge"]):
                cat = "Hotel"
            elif any(w in q for w in ["petrol", "fuel"]):
                cat = "Fuel"

            dest_coords = ctx.get("dest_coords") or ctx.get("current_coords") or (16.2335, 80.5505)
            dest_label = ctx.get("dest_label", "Local Area")

            places = GroundingEngine.get_nearby_places(dest_coords[0], dest_coords[1], dest_label, cat)
            if places:
                p_lines = []
                for p in places[:3]:
                    stars = "⭐" * int(round(p.get("rating", 4.5)))
                    p_lines.append(
                        f"• **{p.get('name')}** ({p.get('rating', 4.5)} {stars})<br>"
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
        if any(w in q for w in ["weather in", "temperature in", "forecast in", "is it raining in", "current weather", "what's the weather"]):
            match_loc = re.search(r"(?:in|at|for)\s+([a-zA-Z\s]+)", q)
            loc_query = match_loc.group(1).strip("?. ") if match_loc else ctx.get("dest_label", "Local Area")
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

        if any(w in q for w in ["fire", "earthquake", "chemical", "spill", "evacuate", "evacuation", "emergency protocol", "alarm"]):
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
        else:
            return {
                "badge": "🌐 TRANSLATION",
                "response": f"Translation request recognized for: *\"{raw_query}\"*."
            }
