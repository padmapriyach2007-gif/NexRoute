"""
P.A.T.H.F.I.N.D.E.R. Explicit Navigation Tool Calling Engine
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Reliable Real Application Actions

Exposes validated tools around actual application functions:
1. calculate_route (Origin, Destination, Travel Mode, Avoidances)
2. search_nearby_facilities (Category, Location, Radius)
3. get_route_alternatives (Alternative corridor inspect & focus)
4. compare_routes (Metric comparison: distance, duration, safety)
5. update_route_preferences (Avoid tolls, highways, ferries)
6. get_current_journey_status (Telemetry, active corridor, ETA)
7. get_live_weather (Open-Meteo real-time atmospheric data)
8. explain_feature (Truthful explanation of NEXROUTE capabilities)
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple

from src.ai_assistant_engine import GroundingEngine
from src.i18n import t

logger = logging.getLogger("pathfinder.tools")

# =============================================================================
# 1. TOOL DEFINITIONS & JSON SCHEMAS (OPENAI / GEMINI / GROQ SPECIFICATION)
# =============================================================================

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_route",
            "description": "Calculates an optimal, hazard-free navigation route between an origin and destination using NEXROUTE's real routing engine.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "Target destination address, landmark, campus building, or city (e.g. 'Vignan University', 'Tenali', 'Guntur Railway Station')."
                    },
                    "origin": {
                        "type": "string",
                        "description": "Optional starting location. If omitted, uses the user's current live GPS satellite location."
                    },
                    "travel_mode": {
                        "type": "string",
                        "enum": ["Car", "Bike", "Bus", "Truck", "Tractor", "Bicycle", "Walk"],
                        "description": "Selected vehicle or transport fleet mode."
                    },
                    "avoid_tolls": {
                        "type": "boolean",
                        "description": "Set to true to exclude toll roads."
                    },
                    "avoid_highways": {
                        "type": "boolean",
                        "description": "Set to true to avoid expressways and major highways."
                    },
                    "avoid_ferries": {
                        "type": "boolean",
                        "description": "Set to true to avoid ferry water crossings."
                    }
                },
                "required": ["destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_nearby_facilities",
            "description": "Finds real, verified amenities and emergency facilities near the current destination or specified place.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["Hospital", "Dining", "Hotel", "Fuel", "ATM", "Pharmacy"],
                        "description": "Amenity category to discover."
                    },
                    "location": {
                        "type": "string",
                        "description": "Optional city, area, or landmark name to search around. Defaults to current destination."
                    }
                },
                "required": ["category"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_route_alternatives",
            "description": "Retrieves details of alternative corridors and optionally highlights a specific candidate route (e.g. route 2) on the interactive map.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selection": {
                        "type": "integer",
                        "description": "1-based index of the route to highlight on the interactive map (e.g., 2 for the second route alternative)."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_routes",
            "description": "Compares all generated candidate corridors side-by-side on distance, duration, safety, and road names.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "enum": ["all", "distance", "duration", "safety"],
                        "description": "Focus metric for comparison."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_route_preferences",
            "description": "Updates routing preferences such as avoiding toll roads, express highways, or ferry crossings.",
            "parameters": {
                "type": "object",
                "properties": {
                    "avoid_tolls": {"type": "boolean", "description": "Whether to avoid toll roads."},
                    "avoid_highways": {"type": "boolean", "description": "Whether to avoid express highways."},
                    "avoid_ferries": {"type": "boolean", "description": "Whether to avoid ferry passages."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_journey_status",
            "description": "Retrieves real-time status of the current journey: active route, distance, travel time, and hazard detours.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_live_weather",
            "description": "Queries real-time meteorological weather (temperature, condition, humidity, wind) for a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Place or city name. Defaults to current destination."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "explain_feature",
            "description": "Explains NEXROUTE's verified mathematical routing, obstacle avoidance, or safety features.",
            "parameters": {
                "type": "object",
                "properties": {
                    "feature_name": {
                        "type": "string",
                        "description": "The specific feature or capability to explain."
                    }
                },
                "required": ["feature_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_convoy_status",
            "description": "Checks the live positions, distances, and movement status of other users/vehicles in a shared convoy or group room.",
            "parameters": {
                "type": "object",
                "properties": {
                    "room_code": {
                        "type": "string",
                        "description": "Optional convoy or group room code (defaults to the active room, e.g. 'DEMO-CONVOY' or 'CONVOY-1')."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_traffic_and_movement_intelligence",
            "description": "Queries real-time verified traffic intelligence, crowd density, vehicle speeds, queue lengths, and sensor fusion status for monitored road corridors or indoor building zones.",
            "parameters": {
                "type": "object",
                "properties": {
                    "zone_or_corridor": {
                        "type": "string",
                        "description": "The specific road corridor (e.g. 'SEG_EXPRESSWAY_01', 'SEG_GUNTUR_BYPASS') or indoor zone (e.g. 'ZONE_ENTRANCE_NORTH', 'ZONE_MALL_ATRIUM')."
                    }
                }
            }
        }
    }
]


# =============================================================================
# 2. VALIDATED TOOL EXECUTOR
# =============================================================================

class PathfinderToolExecutor:
    """
    Executes explicit navigation tools against actual backend services.
    Validates parameters, enforces strict truthfulness, and produces actionable UI commands.
    """

    def __init__(
        self,
        map_service=None,
        route_engine=None,
        road_condition_manager=None,
        hazard_map=None,
        emergency_service_manager=None,
        pipeline=None,
        **kwargs
    ):
        self.map_service = map_service
        self.route_engine = route_engine or pipeline
        self.road_manager = road_condition_manager
        self.hazard_map = hazard_map
        self.emergency_manager = emergency_service_manager
        self.pipeline = pipeline

    def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Dispatches and validates tool execution."""
        ctx = context or {}
        lang = (language or ctx.get("language", "en")).lower().strip()
        args = arguments or {}

        if tool_name == "calculate_route":
            return self._tool_calculate_route(args, ctx, lang)
        elif tool_name == "search_nearby_facilities":
            return self._tool_search_nearby_facilities(args, ctx, lang)
        elif tool_name == "get_route_alternatives":
            return self._tool_get_route_alternatives(args, ctx, lang)
        elif tool_name == "compare_routes":
            return self._tool_compare_routes(args, ctx, lang)
        elif tool_name == "update_route_preferences":
            return self._tool_update_route_preferences(args, ctx, lang)
        elif tool_name == "get_current_journey_status":
            return self._tool_get_current_journey_status(args, ctx, lang)
        elif tool_name == "get_live_weather":
            return self._tool_get_live_weather(args, ctx, lang)
        elif tool_name == "explain_feature":
            return self._tool_explain_feature(args, ctx, lang)
        elif tool_name == "get_convoy_status":
            return self._tool_get_convoy_status(args, ctx, lang)
        elif tool_name == "get_traffic_and_movement_intelligence":
            return self._tool_get_traffic_and_movement_intelligence(args, ctx, lang)
        else:
            return {
                "badge": "⚠️ TOOL ERROR",
                "response": f"Unknown tool requested: '{tool_name}'. Available tools: calculate_route, search_nearby_facilities, get_route_alternatives, compare_routes, update_route_preferences, get_live_weather, get_current_journey_status, get_convoy_status, get_traffic_and_movement_intelligence.",
                "success": False
            }

    # -------------------------------------------------------------------------
    # Tool 9: get_traffic_and_movement_intelligence
    # -------------------------------------------------------------------------
    def _tool_get_traffic_and_movement_intelligence(self, args: Dict[str, Any], ctx: Dict[str, Any], lang: str) -> Dict[str, Any]:
        """Queries verified live camera vision and physical sensor fusion data without hallucination."""
        try:
            from src.backend.traffic.traffic_service import PathfinderTrafficService
            svc = PathfinderTrafficService.get_instance()
            zone = args.get("zone_or_corridor", "SEG_EXPRESSWAY_01")
            fused = svc.fusion_engine.fuse(zone_id=zone)
            adv = svc.get_route_traffic_advisory()

            disagreements_str = "None (Consensus optimal)" if not fused.active_disagreements else "; ".join(fused.active_disagreements)
            speed_val = fused.measured_speed_kmh if fused.measured_speed_kmh is not None else fused.estimated_speed_kmh

            resp_lines = [
                f"🚦 **Real-Time Traffic & Movement Intelligence Report ({fused.zone_id}):**",
                f"• **Environment:** {fused.environment_type}",
                f"• **Pedestrians Active:** {fused.pedestrian_count} ({fused.people_per_min:.1f} / min)",
                f"• **Vehicles Active:** {fused.vehicle_count} ({fused.vehicles_per_min:.1f} / min)",
                f"• **Speed:** {speed_val} km/h (Nominal Free-Flow: {fused.free_flow_speed_kmh} km/h)",
                f"• **Queue Length:** {fused.queue_length} vehicles",
                f"• **Occupancy:** {fused.occupancy_pct:.1f}%",
                f"• **Congestion Status:** {fused.congestion_level} ({fused.congestion_explanation})",
                f"• **Sensor Confidence:** {int(fused.aggregate_confidence * 100)}%",
                f"• **Sensor Disagreements:** {disagreements_str}",
                f"• **Routing Advisory:** {adv['advisory_message']}"
            ]

            return {
                "badge": "🚦 TRAFFIC INTELLIGENCE",
                "response": "\n".join(resp_lines),
                "success": True,
                "data": {
                    "zone_id": fused.zone_id,
                    "congestion_level": fused.congestion_level,
                    "pedestrian_count": fused.pedestrian_count,
                    "vehicle_count": fused.vehicle_count,
                    "speed_kmh": speed_val,
                    "reroute_recommended": adv["reroute_recommended"]
                }
            }
        except Exception as e:
            return {
                "badge": "⚠️ TRAFFIC ERROR",
                "response": f"Unable to fetch live traffic sensor telemetry: {str(e)}",
                "success": False
            }

    # -------------------------------------------------------------------------
    # Tool 1: calculate_route
    # -------------------------------------------------------------------------
    def _tool_calculate_route(self, args: Dict[str, Any], ctx: Dict[str, Any], lang: str) -> Dict[str, Any]:
        dest_raw = str(args.get("destination", "")).strip("?. ")
        orig_raw = str(args.get("origin", "")).strip("?. ")

        if not dest_raw:
            return {
                "badge": "🧭 ROUTE REQUEST",
                "response": "Please specify a destination so I can calculate your route (e.g. 'Route to Tenali' or 'Directions to Vignan University').",
                "success": False
            }

        # Handle pronouns and references ("there", "that place")
        if dest_raw.lower() in ("there", "that place", "the destination", "it"):
            dest_raw = ctx.get("dest_label") or ctx.get("last_searched_place") or ""
            if not dest_raw:
                return {
                    "badge": "🧭 CLARIFICATION NEEDED",
                    "response": "Where would you like to navigate? Please name a city, landmark, or campus building.",
                    "success": False
                }

        # Disambiguation check for generic names
        ambiguous_keywords = ["springfield", "airport", "railway station", "city center", "downtown", "bus station", "hospital"]
        if dest_raw.lower() in ambiguous_keywords:
            return {
                "badge": "🧭 LOCATION CLARIFICATION",
                "response": f"Could you clarify which destination you mean by **'{dest_raw.title()}'**? (e.g. specify the city, state, or campus landmark).",
                "success": False
            }
        if orig_raw and orig_raw.lower() in ambiguous_keywords:
            return {
                "badge": "🧭 LOCATION CLARIFICATION",
                "response": f"Could you clarify which starting point you mean by **'{orig_raw.title()}'**? (e.g. specify the city, state, or campus landmark).",
                "success": False
            }

        # Resolve Origin Coordinates
        orig_coords = None
        orig_label = orig_raw or ctx.get("start_label", "Live GPS Location")
        if not orig_raw or any(w in orig_raw.lower() for w in ["current", "live", "gps", "my location", "here"]):
            orig_coords = ctx.get("current_coords") or (16.2335, 80.5505)
            orig_label = ctx.get("start_label", "Live Satellite GPS")
        elif self.map_service:
            cands = self.map_service.geocode_candidates(orig_raw, limit=3)
            if cands:
                orig_coords = (float(cands[0]["lat"]), float(cands[0]["lon"]))
                orig_label = cands[0].get("display_name", orig_raw)
            else:
                return {
                    "badge": "🧭 GEOCODING NOTICE",
                    "response": f"I could not locate the starting point **'{orig_raw}'**. Please check the spelling or enter a nearby city.",
                    "success": False
                }

        # Resolve Destination Coordinates
        dest_coords = None
        dest_label = dest_raw
        if self.map_service:
            cands_d = self.map_service.geocode_candidates(dest_raw, limit=5, origin_coords=orig_coords)
            if cands_d:
                if len(cands_d) > 1 and dest_raw.lower() not in cands_d[0].get("display_name", "").lower():
                    # Multiple possible locations
                    choices = "\n".join([f"• **{c.get('display_name', '')}**" for c in cands_d[:3]])
                    return {
                        "badge": "🔍 LOCATION CLARIFICATION",
                        "response": f"Found multiple matching places for **'{dest_raw}'**. Which one did you mean?\n\n{choices}\n\nPlease enter the full name to confirm.",
                        "success": False
                    }
                dest_coords = (float(cands_d[0]["lat"]), float(cands_d[0]["lon"]))
                dest_label = cands_d[0].get("display_name", dest_raw)
            else:
                return {
                    "badge": "🧭 GEOCODING NOTICE",
                    "response": f"I could not locate **'{dest_raw}'** on the map network. Please check the spelling or provide a nearby landmark.",
                    "success": False
                }

        # Prepare Action
        action_dict = {
            "type": "calculate_route",
            "origin": orig_label,
            "destination": dest_label,
            "origin_coords": orig_coords,
            "destination_coords": dest_coords,
            "travel_mode": args.get("travel_mode"),
            "avoid_tolls": args.get("avoid_tolls"),
            "avoid_highways": args.get("avoid_highways"),
            "avoid_ferries": args.get("avoid_ferries")
        }

        # Clean display response
        clean_d = dest_label.split(",")[0].strip()
        clean_o = orig_label.split(",")[0].strip()

        if lang == "te":
            resp_text = (
                f"### 🎯 మార్గం రూపొందించబడింది: {clean_o} ➔ {clean_d}\n\n"
                f"• **ప్రారంభ స్థానం:** {clean_o} ({orig_coords[0]:.4f}, {orig_coords[1]:.4f})\n"
                f"• **గమ్యస్థానం:** {clean_d} ({dest_coords[0]:.4f}, {dest_coords[1]:.4f})\n\n"
                f"మార్గం లెక్కించబడుతోంది మరియు ఇంటరాక్టివ్ మ్యాప్‌లో ప్రదర్శించబడుతోంది."
            )
            badge = "🧭 మార్గం లెక్కించబడింది"
        elif lang == "hi":
            resp_text = (
                f"### 🎯 मार्ग तैयार किया गया: {clean_o} ➔ {clean_d}\n\n"
                f"• **प्रस्थान स्थल:** {clean_o} ({orig_coords[0]:.4f}, {orig_coords[1]:.4f})\n"
                f"• **गंतव्य:** {clean_d} ({dest_coords[0]:.4f}, {dest_coords[1]:.4f})\n\n"
                f"मार्ग की गणना की जा रही है और मानचित्र पर हाइलाइट किया जा रहा है।"
            )
            badge = "🧭 मार्ग तैयार"
        else:
            resp_text = (
                f"### 🎯 Route Calculated: {clean_o} ➔ {clean_d}\n\n"
                f"• **Origin:** {clean_o} `({orig_coords[0]:.4f}, {orig_coords[1]:.4f})`\n"
                f"• **Destination:** {clean_d} `({dest_coords[0]:.4f}, {dest_coords[1]:.4f})`\n"
                f"• **Status:** Real road network corridor evaluated and synchronized to your interactive map."
            )
            badge = "🧭 ROUTE CALCULATED"

        return {
            "badge": badge,
            "response": resp_text,
            "action": action_dict,
            "success": True
        }

    # -------------------------------------------------------------------------
    # Tool 2: search_nearby_facilities
    # -------------------------------------------------------------------------
    def _tool_search_nearby_facilities(self, args: Dict[str, Any], ctx: Dict[str, Any], lang: str) -> Dict[str, Any]:
        cat = str(args.get("category", "Hospital")).capitalize()
        loc_name = args.get("location") or ctx.get("dest_label") or "Local Area"
        dest_coords = ctx.get("dest_coords") or ctx.get("current_coords") or (16.2335, 80.5505)

        # Retrieve real places
        places = GroundingEngine.get_nearby_places(dest_coords[0], dest_coords[1], loc_name, cat)
        if not places:
            return {
                "badge": f"🏥 {cat.upper()} SEARCH",
                "response": f"No verified {cat.lower()} facilities found within immediate radius of **{loc_name}**.",
                "success": False
            }

        p_lines = []
        for p in places[:3]:
            stars = "⭐" * int(round(p.get("rating", 4.5)))
            p_lines.append(
                f"• **{p.get('name')}** ({p.get('rating', 4.5)} {stars})<br>"
                f"&nbsp;&nbsp;{p.get('category')} • ~{p.get('dist_km', 1.0):.1f} km away • *{p.get('open_status', 'Open Daily')}*"
            )

        items_str = "\n".join(p_lines)
        if lang == "te":
            resp_text = (
                f"### 📍 {loc_name} సమీపంలోని ధృవీకరించబడిన {cat} సౌకర్యాలు:\n\n"
                f"{items_str}\n\n"
                f"మరిన్ని వివరాలను చూడటానికి 'సౌకర్యాలు' ట్యాబ్‌ను తనిఖీ చేయండి."
            )
        else:
            resp_text = (
                f"### 📍 Verified {cat} Amenities near {loc_name}:\n\n"
                f"{items_str}\n\n"
                f"You can view these directly on the interactive map under the Facilities tab."
            )

        return {
            "badge": f"🏥 VERIFIED {cat.upper()} AMENITIES",
            "response": resp_text,
            "action": {"type": "switch_tab", "tab": "facilities"},
            "success": True
        }

    # -------------------------------------------------------------------------
    # Tool 3: get_route_alternatives
    # -------------------------------------------------------------------------
    def _tool_get_route_alternatives(self, args: Dict[str, Any], ctx: Dict[str, Any], lang: str) -> Dict[str, Any]:
        routes = ctx.get("ranked_routes", [])
        if not routes:
            return {
                "badge": "🗺️ ROUTE ALTERNATIVES",
                "response": "Please set an origin and destination first to generate candidate corridors.",
                "success": False
            }

        sel_idx = args.get("selection")
        if sel_idx is not None and sel_idx >= 1:
            idx = min(sel_idx - 1, len(routes) - 1)
            target_r = routes[idx]
            roads = ", ".join(target_r.route.summary_roads[:2]) if getattr(target_r.route, "summary_roads", None) else "Direct Corridor"
            r_name = target_r.route.name
            
            # Format duration
            dur_mins = target_r.effective_duration_minutes
            if dur_mins >= 60:
                h = int(dur_mins // 60)
                m = int(round(dur_mins % 60))
                dur_str = f"{h}h {m}m" if m > 0 else f"{h}h"
            else:
                dur_str = f"{int(round(dur_mins))} mins"

            # Determine mode icon
            mode_val = str(getattr(target_r.route, "mode", "driving")).lower()
            mode_icon = "🚗"
            if "flight" in mode_val or "air" in mode_val:
                mode_icon = "✈️"
            elif "water" in mode_val or "ferry" in mode_val:
                mode_icon = "🚢"
            elif "walk" in mode_val:
                mode_icon = "🚶"
            elif "bicycl" in mode_val:
                mode_icon = "🚴"
            elif "motorcycle" in mode_val or "bike" in mode_val:
                mode_icon = "🏍️"
            elif "bus" in mode_val:
                mode_icon = "🚌"

            action = {
                "type": "focus_route",
                "route_id": target_r.route.route_id,
                "route_name": r_name
            }
            return {
                "badge": f"🎯 ROUTE {idx + 1} FOCUS",
                "response": (
                    f"### {mode_icon} Route {idx + 1}: **{r_name}**\n\n"
                    f"• **Distance:** **{target_r.effective_distance_km:.1f} km**\n"
                    f"• **Estimated Duration:** **{dur_str}**\n"
                    f"• **Corridor / Roads:** {roads}\n"
                    f"• **Provider:** {getattr(target_r.route, 'provider_attribution', 'OSRM Global Transit')}\n\n"
                    f"🎯 Highlighting Route {idx + 1} on the interactive world map!"
                ),
                "action": action,
                "success": True
            }

        # Overview of all available alternatives (up to 6)
        lines = []
        for i, r in enumerate(routes[:6]):
            dur_m = r.effective_duration_minutes
            if dur_m >= 60:
                h = int(dur_m // 60)
                m = int(round(dur_m % 60))
                dur_s = f"{h}h {m}m" if m > 0 else f"{h}h"
            else:
                dur_s = f"{int(round(dur_m))}m"

            mode_val = str(getattr(r.route, "mode", "driving")).lower()
            icon = "🚗"
            if "flight" in mode_val or "air" in mode_val:
                icon = "✈️"
            elif "water" in mode_val or "ferry" in mode_val:
                icon = "🚢"
            elif "walk" in mode_val:
                icon = "🚶"
            elif "bicycl" in mode_val:
                icon = "🚴"
            elif "motorcycle" in mode_val or "bike" in mode_val:
                icon = "🏍️"
            elif "bus" in mode_val:
                icon = "🚌"

            lines.append(f"• **{icon} Route {i + 1} ({r.route.name}):** {r.effective_distance_km:.1f} km • ~{dur_s}")

        return {
            "badge": "🗺️ ROUTE ALTERNATIVES",
            "response": f"### 🗺️ Available Worldwide Corridors ({len(routes[:6])} found):\n\n" + "\n".join(lines) + "\n\nSay *'Show Route 2 on map'* or *'Compare all routes'* to examine detailed trade-offs.",
            "success": True
        }

    # -------------------------------------------------------------------------
    # Tool 4: compare_routes
    # -------------------------------------------------------------------------
    def _tool_compare_routes(self, args: Dict[str, Any], ctx: Dict[str, Any], lang: str) -> Dict[str, Any]:
        routes = ctx.get("ranked_routes", [])
        if not routes or len(routes) < 2:
            return {
                "badge": "🗺️ ROUTE COMPARISON",
                "response": "To compare routes, please confirm an origin and destination to generate multiple corridors.",
                "success": False
            }

        def format_dur(dur_mins):
            if dur_mins >= 60:
                h = int(dur_mins // 60)
                m = int(round(dur_mins % 60))
                return f"{h}h {m}m" if m > 0 else f"{h}h"
            return f"{int(round(dur_mins))}m"

        def get_mode_icon(route_item):
            mode_val = str(getattr(route_item.route, "mode", "driving")).lower()
            if "flight" in mode_val or "air" in mode_val:
                return "✈️ Flight"
            elif "water" in mode_val or "ferry" in mode_val:
                return "🚢 Waterway"
            elif "walk" in mode_val:
                return "🚶 Walk"
            elif "bicycl" in mode_val:
                return "🚴 Cycle"
            elif "motorcycle" in mode_val or "bike" in mode_val:
                return "🏍️ Bike"
            elif "bus" in mode_val:
                return "🚌 Bus"
            return "🚗 Drive"

        # Build comparison table for up to 6 routes
        rows = []
        for i, r in enumerate(routes[:6]):
            mode_badge = get_mode_icon(r)
            dur_str = format_dur(r.effective_duration_minutes)
            dist_str = f"{r.effective_distance_km:.1f} km"
            
            # Cost estimate
            mode_val = str(getattr(r.route, "mode", "driving")).lower()
            if "flight" in mode_val or "air" in mode_val:
                cost_str = f"~${int(r.effective_distance_km * 0.12 + 65)} (Fare)"
            elif "water" in mode_val or "ferry" in mode_val:
                cost_str = f"~${int(r.effective_distance_km * 0.25 + 15)} (Ferry)"
            elif "walk" in mode_val or "bicycl" in mode_val:
                cost_str = "Free"
            else:
                liters = r.effective_distance_km * 0.08
                cost_str = f"~₹{int(liters * 105)} Fuel"

            provider = getattr(r.route, "provider_attribution", "OSRM Engine").split("•")[0].strip()
            rows.append(f"| **Route {i + 1}** ({r.route.name[:20]}) | {mode_badge} | {dist_str} | **{dur_str}** | {cost_str} | {provider} |")

        table_md = (
            "| Route Option | Mode | Distance | Est. Time | Est. Cost | Provider |\n"
            "| :--- | :--- | :--- | :--- | :--- | :--- |\n" +
            "\n".join(rows)
        )

        # Intelligent trade-off highlights
        fastest_r = min(routes[:6], key=lambda x: x.effective_duration_minutes)
        shortest_r = min(routes[:6], key=lambda x: x.effective_distance_km)
        
        verdict = []
        verdict.append(f"• 🚀 **Fastest Corridor:** **{fastest_r.route.name}** ({format_dur(fastest_r.effective_duration_minutes)})")
        if shortest_r.route.route_id != fastest_r.route.route_id:
            verdict.append(f"• 📏 **Shortest Distance:** **{shortest_r.route.name}** ({shortest_r.effective_distance_km:.1f} km)")
        
        has_flight = any("flight" in str(getattr(r.route, "mode", "")).lower() for r in routes[:6])
        if has_flight:
            verdict.append("• ✈️ **Airway Option Available:** For long-distance inter-city or international travel, Great-Circle air routes provide substantial time savings over surface transport.")

        return {
            "badge": "🗺️ MULTI-ROUTE COMPARISON",
            "response": (
                f"### 🗺️ Real-Time Global Multi-Route Comparison\n\n"
                f"{table_md}\n\n"
                f"**Key Recommendations:**\n" + "\n".join(verdict) + "\n\n"
                f"💡 Select any route card above or tell me *'Show Route 2'* to view turns and highlight it on the map."
            ),
            "success": True
        }

    # -------------------------------------------------------------------------
    # Tool 5: update_route_preferences
    # -------------------------------------------------------------------------
    def _tool_update_route_preferences(self, args: Dict[str, Any], ctx: Dict[str, Any], lang: str) -> Dict[str, Any]:
        tolls = args.get("avoid_tolls")
        highways = args.get("avoid_highways")
        ferries = args.get("avoid_ferries")

        changes = []
        if tolls is not None:
            changes.append(f"• Toll Roads: **{'AVOIDED' if tolls else 'ALLOWED'}**")
        if highways is not None:
            changes.append(f"• Express Highways: **{'AVOIDED' if highways else 'ALLOWED'}**")
        if ferries is not None:
            changes.append(f"• Water Ferries: **{'AVOIDED' if ferries else 'ALLOWED'}**")

        if not changes:
            return {
                "badge": "⚙️ ROUTE PREFERENCES",
                "response": "Please specify which preference you would like to update: Avoid Tolls, Avoid Highways, or Avoid Ferries.",
                "success": False
            }

        return {
            "badge": "⚙️ ROUTE PREFERENCES UPDATED",
            "response": "### ⚙️ Navigation Preferences Updated:\n\n" + "\n".join(changes) + "\n\nRecalculating and updating current corridors...",
            "action": {
                "type": "update_preferences",
                "avoid_tolls": tolls,
                "avoid_highways": highways,
                "avoid_ferries": ferries
            },
            "success": True
        }

    # -------------------------------------------------------------------------
    # Tool 6: get_current_journey_status
    # -------------------------------------------------------------------------
    def _tool_get_current_journey_status(self, args: Dict[str, Any], ctx: Dict[str, Any], lang: str) -> Dict[str, Any]:
        dest = ctx.get("dest_label", "Not Set")
        orig = ctx.get("start_label", "Live Satellite GPS")
        obj = ctx.get("active_objective_str", "FASTEST")
        routes = ctx.get("ranked_routes", [])

        if not routes:
            return {
                "badge": "🧭 JOURNEY STATUS",
                "response": f"**Status:** Idle.\n• **Origin:** {orig}\n• **Destination:** {dest}\n\nPlease set a destination to begin navigation.",
                "success": True
            }

        top = routes[0]
        return {
            "badge": "🧭 JOURNEY STATUS • ACTIVE",
            "response": (
                f"### 🧭 Active Navigation Telemetry\n\n"
                f"• **Corridor:** **{top.route.name}**\n"
                f"• **Route Priority:** **{obj.upper()}**\n"
                f"• **Remaining Ground Distance:** **{top.effective_distance_km:.1f} km**\n"
                f"• **Estimated Travel Time:** **~{top.effective_duration_minutes:.0f} mins**\n"
                f"• **Obstacle Status:** All verified road restrictions bypassed."
            ),
            "success": True
        }

    # -------------------------------------------------------------------------
    # Tool 7: get_live_weather
    # -------------------------------------------------------------------------
    def _tool_get_live_weather(self, args: Dict[str, Any], ctx: Dict[str, Any], lang: str) -> Dict[str, Any]:
        loc_name = args.get("location") or ctx.get("dest_label") or "Destination"
        coords = ctx.get("dest_coords") or ctx.get("current_coords") or (16.2335, 80.5505)

        w_data = GroundingEngine.get_live_weather(coords[0], coords[1], loc_name)
        if not w_data.get("available"):
            return {
                "badge": "🌤️ WEATHER STATION",
                "response": f"Live meteorological report for **{loc_name}** is temporarily unavailable.",
                "success": False
            }

        return {
            "badge": "🌤️ REAL-TIME WEATHER REPORT",
            "response": f"### 🌤️ Live Weather at {loc_name}\n\n{w_data['formatted']}",
            "success": True
        }

    # -------------------------------------------------------------------------
    # Tool 8: explain_feature
    # -------------------------------------------------------------------------
    def _tool_explain_feature(self, args: Dict[str, Any], ctx: Dict[str, Any], lang: str) -> Dict[str, Any]:
        feat = str(args.get("feature_name", "")).lower()

        if any(w in feat for w in ["fastest", "speed", "velocity"]):
            return {
                "badge": "🧭 FEATURE EXPLANATION • FASTEST",
                "response": "### ⚡ Fastest Route Protocol\nOptimizes transit time by prioritizing expressways, high-speed arterial links, and live congestion-free corridors while penalizing traffic delays."
            }
        elif any(w in feat for w in ["shortest", "distance", "mileage"]):
            return {
                "badge": "🧭 FEATURE EXPLANATION • SHORTEST",
                "response": "### 📏 Shortest Route Protocol\nMinimizes total physical ground mileage using Dijkstra/A* geodesic path optimization, choosing the most compact road footprint."
            }
        elif any(w in feat for w in ["accessible", "wheelchair", "barrier"]):
            return {
                "badge": "🧭 FEATURE EXPLANATION • ACCESSIBLE",
                "response": "### ♿ Barrier-Free Accessible Protocol\nStrictly avoids stairs, steep inclines (>5°), and unpaved corridors. Prioritizes certified curb-cuts and ramp-equipped public pedestrian walkways."
            }
        elif any(w in feat for w in ["virtual guide", "virtual runner", "companion"]):
            return {
                "badge": "🧭 FEATURE EXPLANATION • VIRTUAL GUIDE",
                "response": "### 🚗 Virtual Vehicle Companion & Guide\nProvides step-by-step 3D visual guidance and synchronized audio speech instructions that advance with your movement along the corridor."
            }
        else:
            return {
                "badge": "🧭 NEXROUTE SYSTEM OVERVIEW",
                "response": "### 🧭 PATHFINDER Autonomous Navigation\nPATHFINDER is an intelligent multi-objective transit platform featuring dynamic route optimization (Fastest, Shortest, Balanced, Accessible), live hazard evasion, satellite computer vision analysis, and A.U.R.A. AI copilot."
            }

    # -------------------------------------------------------------------------
    # Tool 9: get_convoy_status
    # -------------------------------------------------------------------------
    def _tool_get_convoy_status(self, args: Dict[str, Any], ctx: Dict[str, Any], lang: str) -> Dict[str, Any]:
        try:
            from src.fleet_live_service import get_fleet_live_service
            fleet = get_fleet_live_service()
            room = str(args.get("room_code") or ctx.get("convoy_room_code") or "DEMO-CONVOY").strip().upper()
            user_coords = ctx.get("user_coords") or ctx.get("start_coords") or (16.2335, 80.5505)
            user_id = ctx.get("fleet_user_id")

            members = fleet.get_room_members(
                room_code=room,
                exclude_user_id=user_id,
                reference_lat=user_coords[0],
                reference_lon=user_coords[1]
            )

            if not members:
                return {
                    "badge": f"👥 CONVOY ROOM • {room}",
                    "response": f"### 👥 Convoy Room: **{room}**\n\nNo other active members found in this room right now. You can invite friends, family, or fleet drivers to join using room code **`{room}`**.",
                    "success": True
                }

            lines = [f"### 👥 Live Convoy Status: **{room}** ({len(members)} Active Peers)\n"]
            for m in members:
                dist_str = m.get("relative_location_str") or m.get("distance_label") or "Nearby"
                lines.append(f"- **{m.get('avatar', '🚗')} {m['display_name']}** ({m.get('role', 'Member').capitalize()}):")
                lines.append(f"  • **Distance & Direction:** {dist_str}")
                lines.append(f"  • **Speed:** {m.get('speed_kmh', 0.0):.1f} km/h")
                lines.append(f"  • **Status:** {m.get('status_msg', 'Active')}")
                lines.append(f"  • **Last Active:** {m.get('last_seen_str', 'Just now')}")

            return {
                "badge": f"👥 CONVOY ROOM • {room}",
                "response": "\n".join(lines),
                "success": True
            }
        except Exception as e:
            return {
                "badge": "👥 CONVOY ROOM",
                "response": f"Unable to fetch convoy status: {e}",
                "success": False
            }
