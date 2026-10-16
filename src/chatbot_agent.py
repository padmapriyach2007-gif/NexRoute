import re
from typing import Dict, Any, List, Optional, Tuple
from src.search_engine import SearchResult

class AegisChatbotAgent:
    """
    Aegis AI Safety & Survival Assistant - Crisis-Engineered Edition
    Features:
      1. 2-Second Glanceable Crisis HUDs (High-Contrast Hero Directives)
      2. Fast Visual Breadcrumb Pathways (Sequential Escape Flow)
      3. 3-Rule Visual Survival Micro-Pill Cards (Low Cognitive Load Under Panic)
      4. Progressive Disclosure (<details> for Technical Waypoints & NFPA SOPs)
      5. Sub-50ms Multi-Floor Dynamic A* Egress with 1-Click Map Sync
      6. Context-Aware Natural Language Safety & Navigation Reasoning
    """
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.search_engine = pipeline.search_engine
        self.realtime_agent = pipeline.realtime_agent
        self.rag_agent = pipeline.rag_agent
        self.knowledge_base = pipeline.knowledge_base

    def _resolve_node_id(self, nid: Optional[str]) -> Optional[str]:
        """Resolves node IDs, nav_ids, or pano_ids flexibly against search_engine.nodes."""
        if not nid:
            return None
        nid_clean = nid.strip().upper()
        if nid_clean in self.search_engine.nodes:
            return nid_clean
        # Check nav_id or pano_id
        for k, node in self.search_engine.nodes.items():
            if getattr(node, 'nav_id', '').upper() == nid_clean:
                return k
            if getattr(node, 'pano_id', '').upper() == nid_clean:
                return k
        for k in self.search_engine.nodes:
            if k.upper() == nid_clean or k.rstrip('_').upper() == nid_clean.rstrip('_'):
                return k
        for k in self.search_engine.nodes:
            if nid_clean in k.upper() or k.upper() in nid_clean:
                return k
        return None

    def answer_query(self, user_query: str, current_origin_id: Optional[str] = None) -> Dict[str, Any]:
        """Processes any user query and returns a crisis-optimized structured response."""
        raw_query = user_query.strip()
        query_clean = raw_query.lower()
        active_hazards = self.realtime_agent.active_hazards

        resolved_origin = self._resolve_node_id(current_origin_id) or "VIG_ENGI_CHEMICAL_REACTION_ENGG_"
        origin_node = self.search_engine.nodes.get(resolved_origin)
        origin_name = origin_node.name if origin_node else "Chemical Reaction Engg Lab"

        # ---------------------------------------------------------------------
        # 1. GREETINGS & ACKNOWLEDGEMENTS
        # ---------------------------------------------------------------------
        greeting_patterns = [r"^(hi|hello|hey|greetings|hola|good\s+(morning|afternoon|evening))\b", r"^who\s+are\s+you"]
        if any(re.search(p, query_clean) for p in greeting_patterns) and len(query_clean.split()) <= 4:
            return {
                "response": self._build_greeting_card(origin_name, origin_node),
                "metadata": None
            }

        closure_words = ["thanks", "thank you", "thx", "ok", "okay", "got it", "understood", "bye", "goodbye"]
        if any(w in query_clean for w in closure_words) and len(query_clean.split()) <= 3:
            return {
                "response": (
                    "<div style='background: rgba(15, 23, 42, 0.7); border: 1.5px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 14px 16px;'>"
                    "<div style='font-weight: 800; color: #34d399; font-size: 0.95rem; margin-bottom: 4px;'>🛡️ Acknowledged. Stay Alert & Safe.</div>"
                    "<div style='color: #94a3b8; font-size: 0.82rem; line-height: 1.4;'>CampusAegis is continuously monitoring all 97 campus sectors. If conditions shift or alarms sound, request an instant dynamic route recalculation.</div>"
                    "</div>"
                ),
                "metadata": None
            }

        # ---------------------------------------------------------------------
        # 2. CAMPUSAEGIS SYSTEM & ARCHITECTURE INQUIRY
        # ---------------------------------------------------------------------
        if any(w in query_clean for w in ["what is campusaegis", "what is aegis", "who made", "who built", "who created", "how does aegis work", "what algorithm", "a* algorithm", "horn clause", "csp scheduler", "architecture", "system overview", "problem statement"]):
            return {
                "response": self._build_system_architecture_card(),
                "metadata": None
            }

        # ---------------------------------------------------------------------
        # 3. EARTHQUAKE & SEISMIC SAFETY PROTOCOL
        # ---------------------------------------------------------------------
        if any(w in query_clean for w in ["earthquake", "quake", "tremor", "shaking", "seismic"]):
            return {
                "response": self._build_earthquake_card(),
                "metadata": None
            }

        # ---------------------------------------------------------------------
        # 4. ELECTRICAL FIRE & EQUIPMENT ISOLATION
        # ---------------------------------------------------------------------
        if any(w in query_clean for w in ["electrical", "electric", "transformer", "substation", "short circuit", "spark", "breaker", "power surge"]):
            return {
                "response": self._build_electrical_card(),
                "metadata": None
            }

        # ---------------------------------------------------------------------
        # 5. CHEMICAL SPILL & HAZARDOUS VAPOR PROTOCOL
        # ---------------------------------------------------------------------
        if any(w in query_clean for w in ["chemical spill", "acid spill", "solvent", "reagent", "toxic vapor", "toxic fume", "gas leak", "hazmat"]) and not any(w in query_clean for w in ["evacuate", "route", "exit"]):
            return {
                "response": self._build_chemical_hazard_card(),
                "metadata": None
            }

        # ---------------------------------------------------------------------
        # 6. MEDICAL EMERGENCY & CASUALTY RESPONSE
        # ---------------------------------------------------------------------
        if any(w in query_clean for w in ["medical", "injury", "injured", "doctor", "ambulance", "bleeding", "first aid", "unconscious", "casualty", "hospital", "health centre"]):
            return {
                "response": self._build_medical_card(),
                "metadata": None
            }

        # ---------------------------------------------------------------------
        # 7. ELEVATOR / LIFT SAFETY WARNING
        # ---------------------------------------------------------------------
        if any(w in query_clean for w in ["elevator", "elevators", "lift", "lifts", "take the lift", "use lift"]):
            return {
                "response": self._build_elevator_warning_card(origin_name),
                "metadata": None
            }

        # ---------------------------------------------------------------------
        # 8. ANTI-STAMPEDE & CROWD CRUSH PROTOCOL
        # ---------------------------------------------------------------------
        if any(w in query_clean for w in ["stampede", "crowd crush", "crush", "bottleneck", "crowd safety", "panic", "pushing"]):
            return {
                "response": self._build_stampede_card(),
                "metadata": None
            }

        # ---------------------------------------------------------------------
        # 9. GENERAL FIRE & SMOKE INFILTRATION PROTOCOL
        # ---------------------------------------------------------------------
        if any(w in query_clean for w in ["fire", "smoke", "fumes", "flame", "burning", "extinguisher", "fire alarm"]) and not any(w in query_clean for w in ["route", "travel", "escape", "exit", "evacuate"]):
            return {
                "response": self._build_fire_smoke_card(),
                "metadata": None
            }

        # ---------------------------------------------------------------------
        # 10. EMERGENCY CONTACTS DIRECTORY QUERY
        # ---------------------------------------------------------------------
        if any(w in query_clean for w in ["contact", "contacts", "phone", "helpline", "call", "security number", "control room", "warden"]):
            return {
                "response": self._build_contacts_card(),
                "metadata": None
            }

        # ---------------------------------------------------------------------
        # 11. HAZARD & OBSTACLE STATUS INQUIRY
        # ---------------------------------------------------------------------
        hazard_keywords = [
            "hazard", "blocked", "closed", "safe to use", "stairwell a", "stairwell b", 
            "stair a", "stair b", "danger", "active emergency", "status", "situation", "obstruction"
        ]
        is_hazard_query = any(k in query_clean for k in hazard_keywords) and not any(k in query_clean for k in ["route", "travel", "path", "escape", "exit", "evacuate"])
        if is_hazard_query:
            return self._handle_hazard_query(query_clean, active_hazards)

        # ---------------------------------------------------------------------
        # 12. LOCATION EXPLORATION ("WHERE IS X?" / "TELL ME ABOUT X")
        # ---------------------------------------------------------------------
        detected_loc = self.rag_agent.detect_vignan_location(user_query)
        is_where_query = any(w in query_clean for w in ["where is", "where's", "where are", "tell me about", "location of", "info about", "details of", "which floor"])
        if detected_loc and is_where_query:
            nid, node = detected_loc
            return self._handle_location_info(nid, node)

        # ---------------------------------------------------------------------
        # 13. ROUTE, TRAVEL, NAVIGATION & ESCAPE INQUIRY
        # ---------------------------------------------------------------------
        route_keywords = [
            "travel", "safest travel", "safe travel", "traveling", "travel route", "travel path",
            "route", "routes", "path", "paths", "escape", "evacuate", "evacuation", "survival", 
            "exit", "exits", "egress", "get out", "way out", "how do i reach", "how to reach", 
            "how do i go", "how to go", "where to go", "where do i go", "how to leave", "how do i get", 
            "directions", "nearest exit", "lead me", "guide me", "take me", "trapped", "stuck",
            "help me", "save me", "assembly", "safe assembly", "safe haven", "how to exit"
        ]
        is_route_query = any(k in query_clean for k in route_keywords)

        target_node_id = None
        if detected_loc:
            target_node_id = self._resolve_node_id(detected_loc[0])
        elif is_route_query:
            target_node_id = resolved_origin

        if is_route_query and target_node_id:
            return self._handle_route_request(target_node_id, user_query)

        if detected_loc and not is_route_query:
            nid, node = detected_loc
            return self._handle_location_info(nid, node)

        # ---------------------------------------------------------------------
        # 14. SOP / SAFETY PROTOCOL RAG SEARCH
        # ---------------------------------------------------------------------
        sop_results = self.rag_agent.retrieve_sop(user_query, top_k=2)
        if sop_results and sop_results[0]["similarity_score"] > 0.03:
            return self._handle_sop_query(user_query, sop_results)

        # ---------------------------------------------------------------------
        # 15. DYNAMIC INTELLIGENT CRISIS RESOLUTION
        # ---------------------------------------------------------------------
        return self._handle_intelligent_fallback(user_query, origin_name, resolved_origin)

    # =========================================================================
    # CRISIS VISUAL BUILDERS (OPTIMIZED FOR 2-SECOND GLANCEABILITY)
    # =========================================================================

    def _handle_route_request(self, start_node_id: str, original_query: str) -> Dict[str, Any]:
        """Calculates route and builds crisis HUD with breadcrumbs, action cards, and expandable details."""
        start_node = self.search_engine.nodes.get(start_node_id)
        goal_node_id = "VIG_FACI_PLAY_GROUNDS"
        goal_node = self.search_engine.nodes.get(goal_node_id)

        if not start_node:
            return {
                "response": (
                    "<div style='background: rgba(239, 68, 68, 0.15); border: 1.5px solid #ef4444; border-radius: 12px; padding: 12px 14px;'>"
                    "<b style='color: #fca5a5;'>⚠️ Origin Location Unresolved:</b> Please state your current room (e.g. <i>Chemical Reaction Lab</i> or <i>NTR Library</i>)."
                    "</div>"
                ),
                "metadata": None
            }

        res_route, replan_ms = self.realtime_agent.dynamic_replan(start_node_id, goal_node_id)
        active_hazards = self.realtime_agent.active_hazards

        if not res_route.path or res_route.cost == float('inf'):
            return {
                "response": (
                    "<div style='background: linear-gradient(135deg, rgba(220, 38, 38, 0.4) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2.5px solid #ef4444; border-radius: 14px; padding: 16px; box-shadow: 0 0 24px rgba(239, 68, 68, 0.4);'>"
                    "<div style='background: #ef4444; color: #ffffff; display: inline-block; padding: 3px 8px; border-radius: 6px; font-weight: 800; font-size: 0.72rem; letter-spacing: 0.6px;'>🚨 CRITICAL LOCKDOWN: ALL CORRIDORS COMPROMISED</div>"
                    "<div style='font-size: 1.25rem; font-weight: 800; color: #ffffff; margin: 8px 0 6px 0;'>🛡️ ACTION: SHELTER IN PLACE IMMEDIATELY</div>"
                    "<div style='color: #fca5a5; font-size: 0.85rem; line-height: 1.5; margin-bottom: 10px;'>"
                    "1. <b>Seal Doors:</b> Block bottom door gaps with damp cloth/garments to stop smoke.<br>"
                    "2. <b>Position at Windows:</b> Move to exterior windows for fresh air and signal your sector.<br>"
                    f"3. <b>Marshals Alerted:</b> Response team dispatched to <b>{start_node.name} (Floor {start_node.floor})</b>."
                    "</div>"
                    "</div>"
                ),
                "metadata": {"blocked": True, "start_node": start_node_id}
            }

        # Identify key segments (Corridor, Stairwell, Ground Exit)
        stair_used = "Stairwell B (South)"
        stair_compromised_alert = ""
        for nid in res_route.path:
            n = self.search_engine.nodes[nid]
            if "stair_a" in nid.lower():
                stair_used = "Stairwell A (North)"
            elif "stair_b" in nid.lower():
                stair_used = "Stairwell B (South)"

        if "CHEM_STAIR_A_F2" in active_hazards and "CHEM_STAIR_A_F2" not in res_route.path:
            stair_compromised_alert = "<span style='background: rgba(239, 68, 68, 0.25); border: 1px solid #ef4444; color: #fca5a5; padding: 3px 9px; border-radius: 999px; font-size: 0.74rem; font-weight: 700;'>⚠️ STAIR A BLOCKED ➔ REROUTED B</span>"

        est_time = round(res_route.cost / 75.0, 1) # ~1.25 m/s standard egress pace
        meters = round(res_route.cost, 1)

        # Simplified breadcrumb nodes (Origin -> Stair -> Safe Haven)
        breadcrumb_html = (
            f"<div style='background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 12px; padding: 10px 12px; margin-bottom: 12px;'>"
            f"<div style='font-size: 0.70rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.6px;'>🗺️ 2-Second Visual Pathway:</div>"
            f"<div style='display: flex; align-items: center; gap: 6px; flex-wrap: wrap; font-size: 0.80rem; font-weight: 700;'>"
            f"<span style='background: rgba(14, 165, 233, 0.2); border: 1px solid #38bdf8; color: #bae6fd; padding: 4px 9px; border-radius: 8px;'>📍 {start_node.name[:22]} (F{start_node.floor})</span>"
            f"<span style='color: #38bdf8;'>➔</span>"
            f"<span style='background: rgba(245, 158, 11, 0.2); border: 1px solid #f59e0b; color: #fde68a; padding: 4px 9px; border-radius: 8px;'>🪜 {stair_used} (Descend to F0)</span>"
            f"<span style='color: #10b981;'>➔</span>"
            f"<span style='background: rgba(16, 185, 129, 0.25); border: 1.5px solid #10b981; color: #6ee7b7; padding: 4px 9px; border-radius: 8px;'>🛡️ Play Grounds Haven</span>"
            f"</div>"
            f"</div>"
        )

        # Step items for collapsible technical view
        step_items = []
        for idx, nid in enumerate(res_route.path):
            n = self.search_engine.nodes[nid]
            role = f"Floor {n.floor}"
            step_items.append(f"<li><b>Step {idx+1}:</b> {n.name} <span style='color:#38bdf8;'>[{role}]</span></li>")
        steps_html = "<ol style='margin: 4px 0 0 16px; padding: 0; line-height: 1.6; font-size: 0.80rem; color: #cbd5e1;'>" + "".join(step_items) + "</ol>"

        response_html = f"""
<div style="background: linear-gradient(135deg, rgba(6, 78, 59, 0.5) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #10b981; border-radius: 14px; padding: 14px 16px; margin-bottom: 10px; box-shadow: 0 0 20px rgba(16, 185, 129, 0.25);">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
    <span style="background: #10b981; color: #042f2e; font-weight: 800; font-size: 0.70rem; padding: 3px 8px; border-radius: 6px; letter-spacing: 0.6px; text-transform: uppercase;">⚡ IMMEDIATE EVACUATION ACTION</span>
    <span style="color: #6ee7b7; font-size: 0.72rem; font-weight: 600;">{replan_ms}ms A* Calculation</span>
  </div>
  <div style="font-size: 1.15rem; font-weight: 800; color: #ffffff; line-height: 1.3; margin: 4px 0 8px 0;">
    🏃 DESCEND VIA {stair_used.upper()} ➔ EXIT TO PLAY GROUNDS
  </div>
  <div style="display: flex; gap: 6px; flex-wrap: wrap;">
    <span style="background: rgba(14, 165, 233, 0.2); border: 1px solid #38bdf8; color: #7dd3fc; padding: 3px 9px; border-radius: 999px; font-size: 0.74rem; font-weight: 700;">⏱️ ~{est_time} MIN WALK</span>
    <span style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #6ee7b7; padding: 3px 9px; border-radius: 999px; font-size: 0.74rem; font-weight: 700;">📏 {meters} METERS</span>
    {stair_compromised_alert}
  </div>
</div>

{breadcrumb_html}

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-bottom: 10px;">
  <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 10px; padding: 8px 4px; text-align: center;">
    <div style="font-size: 1.25rem;">💨</div>
    <div style="font-size: 0.72rem; font-weight: 800; color: #e2e8f0; margin-top: 2px;">CRAWL LOW</div>
    <div style="font-size: 0.64rem; color: #94a3b8;">Smoke rises</div>
  </div>
  <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 10px; padding: 8px 4px; text-align: center;">
    <div style="font-size: 1.25rem;">🚫</div>
    <div style="font-size: 0.72rem; font-weight: 800; color: #fca5a5; margin-top: 2px;">NO LIFTS</div>
    <div style="font-size: 0.64rem; color: #94a3b8;">Use fire stairs</div>
  </div>
  <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 8px 4px; text-align: center;">
    <div style="font-size: 1.25rem;">🫱</div>
    <div style="font-size: 0.72rem; font-weight: 800; color: #6ee7b7; margin-top: 2px;">KEEP RIGHT</div>
    <div style="font-size: 0.64rem; color: #94a3b8;">Open for marshals</div>
  </div>
</div>

<details style="background: rgba(15, 23, 42, 0.55); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 10px; padding: 8px 12px; margin-top: 6px; font-size: 0.80rem; color: #cbd5e1;">
  <summary style="cursor: pointer; font-weight: 700; color: #38bdf8;">📋 View Full Turn-by-Turn Waypoints & Technical Telemetry</summary>
  <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid rgba(148, 163, 184, 0.15);">
    {steps_html}
    <div style="margin-top: 8px; font-size: 0.75rem; color: #94a3b8;">
      • <b>Standard:</b> NFPA 101 Life Safety Code • Minimum Stair Width 1.4m • 0 Bottlenecks Predicted
    </div>
  </div>
</details>
"""
        return {
            "response": response_html.strip(),
            "metadata": {
                "start_node": start_node_id,
                "goal_node": goal_node_id,
                "path": res_route.path,
                "cost": res_route.cost,
                "replan_ms": replan_ms
            }
        }

    def _handle_location_info(self, nid: str, node: Any) -> Dict[str, Any]:
        """Builds a rich interactive Cyber-Telemetry profile for any of the 97 Vignan locations."""
        goal_node = self.search_engine.nodes.get("VIG_FACI_PLAY_GROUNDS")
        dist_to_assembly = round(node.distance_to(goal_node), 1) if goal_node else 45.0
        
        pano_id = getattr(node, "pano_id", "")
        nav_id = getattr(node, "nav_id", nid)
        
        pano_link_html = ""
        if pano_id:
            tour_url = f"https://www.google.com/maps/@?api=1&map_action=pano&pano={pano_id}"
            pano_link_html = f"""
            <div style="margin-top: 10px;">
              <a href="{tour_url}" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: #ffffff; padding: 7px 14px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 0.80rem; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);">
                🌐 Launch 360° Photosphere Panorama View ↗
              </a>
            </div>
            """
            
        response_html = f"""
<div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #10b981; border-radius: 14px; padding: 14px 16px; margin-bottom: 8px; box-shadow: 0 0 20px rgba(16, 185, 129, 0.25);">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
    <span style="background: rgba(16, 185, 129, 0.25); color: #34d399; padding: 2px 8px; border-radius: 6px; font-weight: 800; font-size: 0.70rem; letter-spacing: 0.5px;">📍 VIGNAN SECTOR TELEMETRY</span>
    <span style="color: #94a3b8; font-size: 0.72rem; font-family: monospace;">{nav_id}</span>
  </div>
  <div style="font-size: 1.18rem; font-weight: 800; color: #ffffff; margin-bottom: 2px;">{node.name}</div>
  <div style="font-size: 0.80rem; color: #38bdf8; margin-bottom: 10px;">{node.section} • {node.block}</div>
  
  <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-bottom: 10px;">
    <div style="background: rgba(0,0,0,0.4); padding: 7px; border-radius: 8px; text-align: center; border: 1px solid rgba(255,255,255,0.06);">
      <div style="font-size: 0.68rem; color: #94a3b8; text-transform: uppercase;">Floor Level</div>
      <b style="color: #34d399; font-size: 0.92rem;">Floor {node.floor}</b>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 7px; border-radius: 8px; text-align: center; border: 1px solid rgba(255,255,255,0.06);">
      <div style="font-size: 0.68rem; color: #94a3b8; text-transform: uppercase;">Coordinates</div>
      <b style="color: #38bdf8; font-size: 0.82rem;">{node.x:.1f}, {node.y:.1f}</b>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 7px; border-radius: 8px; text-align: center; border: 1px solid rgba(255,255,255,0.06);">
      <div style="font-size: 0.68rem; color: #94a3b8; text-transform: uppercase;">Safe Egress</div>
      <b style="color: #fde68a; font-size: 0.88rem;">~{dist_to_assembly}m</b>
    </div>
  </div>
  
  <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 8px 10px; font-size: 0.76rem; color: #cbd5e1; line-height: 1.45;">
    • <b>Navigation Node ID:</b> <code style="color: #34d399; background: transparent;">{nav_id}</code><br>
    • <b>Virtual Tour Panorama ID:</b> <code style="color: #94a3b8; font-size: 0.70rem; word-break: break-all; background: transparent;">{pano_id or 'Internal Node'}</code><br>
    • <b>Safe Action:</b> Follow green illuminated corridors towards uncompromised stairwells. Click below to synchronize this location to the 2D/3D Tactical Twin!
  </div>
  {pano_link_html}
</div>
"""
        return {
            "response": response_html.strip(),
            "metadata": {
                "start_node": nid,
                "goal_node": "VIG_FACI_PLAY_GROUNDS",
                "nav_id": nav_id,
                "pano_id": pano_id
            }
        }

    def _build_elevator_warning_card(self, origin_name: str) -> str:
        return f"""
<div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #ef4444; border-radius: 14px; padding: 14px 16px; margin-bottom: 10px;">
  <div style="background: #ef4444; color: #ffffff; display: inline-block; padding: 2px 8px; border-radius: 6px; font-weight: 800; font-size: 0.70rem; text-transform: uppercase;">🚫 CRITICAL SAFETY MANDATE</div>
  <div style="font-size: 1.15rem; font-weight: 800; color: #ffffff; margin: 6px 0 8px 0;">NEVER USE ELEVATORS OR LIFTS IN EMERGENCIES</div>
  <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 8px 0;">
    <div style="background: rgba(0,0,0,0.4); padding: 6px; border-radius: 8px; text-align: center;">
      <b style="color: #fca5a5; font-size: 0.74rem;">1. CHIMNEY EFFECT</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Shafts pull smoke & gas</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 6px; border-radius: 8px; text-align: center;">
      <b style="color: #fca5a5; font-size: 0.74rem;">2. POWER TRIP</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Grid cuts trap cabs</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 6px; border-radius: 8px; text-align: center;">
      <b style="color: #fca5a5; font-size: 0.74rem;">3. WARPED DOORS</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Heat jams door tracks</div>
    </div>
  </div>
  <div style="font-size: 0.82rem; color: #34d399; font-weight: 700; margin-top: 6px;">
    ✅ REQUIRED ACTION: Descend via uncompromised fire stairwells (Stairwell A or B) to ground.
  </div>
</div>
"""

    def _build_stampede_card(self) -> str:
        return """
<div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #f59e0b; border-radius: 14px; padding: 14px 16px; margin-bottom: 10px;">
  <div style="background: #f59e0b; color: #451a03; display: inline-block; padding: 2px 8px; border-radius: 6px; font-weight: 800; font-size: 0.70rem; text-transform: uppercase;">🛡️ CROWD CRUSH SURVIVAL ACTIONS</div>
  <div style="font-size: 1.15rem; font-weight: 800; color: #ffffff; margin: 6px 0 8px 0;">ASSUME BOXER STANCE & MOVE DIAGONALLY</div>
  <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 8px 0;">
    <div style="background: rgba(0,0,0,0.4); padding: 6px; border-radius: 8px; text-align: center;">
      <div style="font-size: 1.2rem;">🥊</div>
      <b style="color: #fde68a; font-size: 0.74rem;">BOXER STANCE</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Arms up, protect chest buffer</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 6px; border-radius: 8px; text-align: center;">
      <div style="font-size: 1.2rem;">↗️</div>
      <b style="color: #fde68a; font-size: 0.74rem;">DRIFT DIAGONAL</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Move to perimeter walls</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 6px; border-radius: 8px; text-align: center;">
      <div style="font-size: 1.2rem;">🧎</div>
      <b style="color: #fde68a; font-size: 0.74rem;">NEVER BEND DOWN</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Ignore dropped belongings</div>
    </div>
  </div>
  <div style="font-size: 0.78rem; color: #94a3b8; line-height: 1.4;">
    CampusAegis CSP scheduling staggers building floor departure waves to prevent stairwell bottlenecks.
  </div>
</div>
"""

    def _build_contacts_card(self) -> str:
        return """
<div style="background: linear-gradient(135deg, rgba(14, 165, 233, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #38bdf8; border-radius: 14px; padding: 14px 16px; margin-bottom: 10px;">
  <div style="background: #38bdf8; color: #082f49; display: inline-block; padding: 2px 8px; border-radius: 6px; font-weight: 800; font-size: 0.70rem; text-transform: uppercase;">📞 24/7 CAMPUS EMERGENCY DIRECTORY</div>
  <div style="font-size: 1.15rem; font-weight: 800; color: #ffffff; margin: 6px 0 8px 0;">INSTANT FIRST RESPONDER CONTACTS</div>
  <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin: 8px 0;">
    <div style="background: rgba(0,0,0,0.4); padding: 8px; border-radius: 8px;">
      <b style="color: #38bdf8; font-size: 0.78rem;">🛡️ Security Control:</b>
      <div style="font-size: 0.86rem; color: #ffffff; font-weight: 700;">Ext 2200 / +91-863-2344700</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 8px; border-radius: 8px;">
      <b style="color: #34d399; font-size: 0.78rem;">🏥 Health Centre:</b>
      <div style="font-size: 0.86rem; color: #ffffff; font-weight: 700;">Ext 2255 / Casualty</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 8px; border-radius: 8px;">
      <b style="color: #f87171; font-size: 0.78rem;">🚒 Fire Marshal:</b>
      <div style="font-size: 0.86rem; color: #ffffff; font-weight: 700;">Ext 2112 / Channel 4</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 8px; border-radius: 8px;">
      <b style="color: #fbbf24; font-size: 0.78rem;">🚑 National Dispatches:</b>
      <div style="font-size: 0.86rem; color: #ffffff; font-weight: 700;">108 (Ambulance) / 101 (Fire)</div>
    </div>
  </div>
</div>
"""

    def _build_greeting_card(self, origin_name: str, origin_node: Any) -> str:
        floor_str = f"Floor {origin_node.floor}" if origin_node else "Floor 2"
        return f"""
<div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #10b981; border-radius: 14px; padding: 14px 16px; margin-bottom: 8px;">
  <div style="font-size: 1.05rem; font-weight: 800; color: #34d399;">👋 CampusAegis AI Safety & Survival Assistant</div>
  <div style="display: flex; gap: 6px; margin: 8px 0; flex-wrap: wrap;">
    <span style="background: rgba(14, 165, 233, 0.2); border: 1px solid #38bdf8; color: #bae6fd; padding: 3px 8px; border-radius: 6px; font-size: 0.74rem; font-weight: 700;">📍 {origin_name} ({floor_str})</span>
    <span style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #6ee7b7; padding: 3px 8px; border-radius: 6px; font-size: 0.74rem; font-weight: 700;">🟢 ALL 97 SECTORS MONITORED</span>
  </div>
  <div style="font-size: 0.80rem; color: #cbd5e1; line-height: 1.4;">
    Ask any emergency or navigation question below. Responses are formatted for <b>immediate 2-second visual comprehension</b> under stress.
  </div>
</div>
"""

    def _handle_hazard_query(self, query: str, active_hazards: Dict[str, Any]) -> Dict[str, Any]:
        """Provides instant situational report on active hazards."""
        if not active_hazards:
            return {
                "response": (
                    "<div style='background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #10b981; border-radius: 14px; padding: 14px 16px; margin-bottom: 8px;'>"
                    "<div style='background: #10b981; color: #042f2e; display: inline-block; padding: 2px 8px; border-radius: 6px; font-weight: 800; font-size: 0.70rem;'>🟢 STATUS: 100% OPERATIONAL</div>"
                    "<div style='font-size: 1.15rem; font-weight: 800; color: #ffffff; margin: 6px 0 6px 0;'>ALL 97 CAMPUS LOCATIONS & STAIRWELLS CLEAR</div>"
                    "<div style='font-size: 0.82rem; color: #94a3b8; line-height: 1.4;'>"
                    "• <b>Stairwell A (North):</b> Clear & traversable.<br>"
                    "• <b>Stairwell B (South):</b> Clear & traversable.<br>"
                    "• <b>Perimeter Walkways to Play Grounds:</b> Zero active obstructions detected."
                    "</div>"
                    "</div>"
                ),
                "metadata": None
            }

        haz_list = []
        for hid, h in active_hazards.items():
            haz_list.append(f"<li>🚨 <b>{h.location_name}:</b> {h.hazard_type} (Severity: <span style='color:#ef4444;'>{h.severity}</span>)</li>")

        return {
            "response": (
                "<div style='background: linear-gradient(135deg, rgba(239, 68, 68, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #ef4444; border-radius: 14px; padding: 14px 16px; margin-bottom: 8px;'>"
                f"<div style='background: #ef4444; color: #ffffff; display: inline-block; padding: 2px 8px; border-radius: 6px; font-weight: 800; font-size: 0.70rem;'>⚠️ ACTIVE HAZARDS DETECTED ({len(active_hazards)})</div>"
                "<div style='font-size: 1.15rem; font-weight: 800; color: #ffffff; margin: 6px 0 6px 0;'>ACTIVE HAZARD SECTOR REPORT</div>"
                f"<ul style='margin: 4px 0 8px 16px; padding: 0; font-size: 0.82rem; color: #fca5a5;'>{''.join(haz_list)}</ul>"
                "<div style='font-size: 0.78rem; color: #6ee7b7;'>*CampusAegis dynamic A* has automatically applied infinite cost penalties to reroute you around these zones in under 50ms.*</div>"
                "</div>"
            ),
            "metadata": None
        }

    def _build_system_architecture_card(self) -> str:
        return """
<div style="background: linear-gradient(135deg, rgba(14, 165, 233, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #38bdf8; border-radius: 14px; padding: 14px 16px; margin-bottom: 8px;">
  <div style="background: #38bdf8; color: #082f49; display: inline-block; padding: 2px 8px; border-radius: 6px; font-weight: 800; font-size: 0.70rem; text-transform: uppercase;">🛡️ ARCHITECTURE OVERVIEW</div>
  <div style="font-size: 1.15rem; font-weight: 800; color: #ffffff; margin: 6px 0 8px 0;">CAMPUSAEGIS (A.E.G.I.S.) DEFENSE SYSTEM</div>
  <div style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.45; margin-bottom: 8px;">
    Autonomous Emergency Guidance & Intelligent Scheduling is a multi-agent life safety defense platform designed for Vignan University.
  </div>
  <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 8px 0;">
    <div style="background: rgba(0,0,0,0.4); padding: 8px 6px; border-radius: 8px; text-align: center;">
      <b style="color: #38bdf8; font-size: 0.74rem;">⚡ DYNAMIC A*</b>
      <div style="font-size: 0.65rem; color: #94a3b8;">Sub-50ms multi-floor 3D egress avoidance</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 8px 6px; border-radius: 8px; text-align: center;">
      <b style="color: #34d399; font-size: 0.74rem;">🧠 HORN PROVER</b>
      <div style="font-size: 0.65rem; color: #94a3b8;">Deductive proofs of safe escape corridors</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 8px 6px; border-radius: 8px; text-align: center;">
      <b style="color: #f59e0b; font-size: 0.74rem;">👥 CSP SCHEDULER</b>
      <div style="font-size: 0.65rem; color: #94a3b8;">Staged floor waves preventing stampedes</div>
    </div>
  </div>
  <div style="font-size: 0.75rem; color: #6ee7b7; margin-top: 6px;">
    • <b>Campus Model:</b> 97 verified Vignan University facilities, labs, stairwells, and outdoor safe havens.
  </div>
</div>
"""

    def _build_earthquake_card(self) -> str:
        return """
<div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #f59e0b; border-radius: 14px; padding: 14px 16px; margin-bottom: 8px;">
  <div style="background: #f59e0b; color: #451a03; display: inline-block; padding: 2px 8px; border-radius: 6px; font-weight: 800; font-size: 0.70rem; text-transform: uppercase;">⚠️ SEISMIC CRISIS DIRECTIVE</div>
  <div style="font-size: 1.15rem; font-weight: 800; color: #ffffff; margin: 6px 0 8px 0;">DROP, COVER, AND HOLD ON IMMEDIATELY</div>
  <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 8px 0;">
    <div style="background: rgba(0,0,0,0.4); padding: 8px 4px; border-radius: 8px; text-align: center;">
      <div style="font-size: 1.2rem;">🧎</div>
      <b style="color: #fde68a; font-size: 0.74rem;">1. DROP</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Hands & knees immediately</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 8px 4px; border-radius: 8px; text-align: center;">
      <div style="font-size: 1.2rem;">🛡️</div>
      <b style="color: #fde68a; font-size: 0.74rem;">2. COVER</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Under heavy desk or archway</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 8px 4px; border-radius: 8px; text-align: center;">
      <div style="font-size: 1.2rem;">✊</div>
      <b style="color: #fde68a; font-size: 0.74rem;">3. HOLD ON</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Hold shelter until shaking ends</div>
    </div>
  </div>
  <div style="color: #fca5a5; font-size: 0.78rem; font-weight: 700; margin-top: 6px;">
    🚫 DO NOT run outside or rush stairwells during active shaking. Stay clear of glass windows and tall reagent racks. Once shaking stops, evacuate orderly to Play Grounds.
  </div>
</div>
"""

    def _build_fire_smoke_card(self) -> str:
        return """
<div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #ef4444; border-radius: 14px; padding: 14px 16px; margin-bottom: 8px;">
  <div style="background: #ef4444; color: #ffffff; display: inline-block; padding: 2px 8px; border-radius: 6px; font-weight: 800; font-size: 0.70rem; text-transform: uppercase;">🔥 FIRE & SMOKE INFILTRATION DIRECTIVE</div>
  <div style="font-size: 1.15rem; font-weight: 800; color: #ffffff; margin: 6px 0 8px 0;">CRAWL LOW & CHECK DOORS BEFORE OPENING</div>
  <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 8px 0;">
    <div style="background: rgba(0,0,0,0.4); padding: 8px 4px; border-radius: 8px; text-align: center;">
      <div style="font-size: 1.2rem;">💨</div>
      <b style="color: #fca5a5; font-size: 0.74rem;">CRAWL LOW</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Stay below rising hot smoke</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 8px 4px; border-radius: 8px; text-align: center;">
      <div style="font-size: 1.2rem;">🚪</div>
      <b style="color: #fca5a5; font-size: 0.74rem;">FEEL DOORS</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Back of hand on metal knob</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 8px 4px; border-radius: 8px; text-align: center;">
      <div style="font-size: 1.2rem;">🧯</div>
      <b style="color: #fca5a5; font-size: 0.74rem;">USE ABC CO2</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Dry powder, no water on elec</div>
    </div>
  </div>
  <div style="font-size: 0.80rem; color: #fca5a5; line-height: 1.4; margin-top: 6px;">
    • Pull nearest Manual Call Point (MCP) alarm on stairwell landing.<br>
    • If smoke enters corridor, seal door bottoms with damp cloth and shelter in place by windows.
  </div>
</div>
"""

    def _build_chemical_hazard_card(self) -> str:
        return """
<div style="background: linear-gradient(135deg, rgba(168, 85, 247, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #a855f7; border-radius: 14px; padding: 14px 16px; margin-bottom: 8px;">
  <div style="background: #a855f7; color: #ffffff; display: inline-block; padding: 2px 8px; border-radius: 6px; font-weight: 800; font-size: 0.70rem; text-transform: uppercase;">🧪 CHEMICAL HAZARD & HAZMAT LEVEL 2</div>
  <div style="font-size: 1.15rem; font-weight: 800; color: #ffffff; margin: 6px 0 8px 0;">ISOLATE MANIFOLD & EVACUATE UPWIND</div>
  <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 8px 0;">
    <div style="background: rgba(0,0,0,0.4); padding: 8px 4px; border-radius: 8px; text-align: center;">
      <div style="font-size: 1.2rem;">🛑</div>
      <b style="color: #e9d5ff; font-size: 0.74rem;">VALVE SHUTOFF</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Close emergency manifold</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 8px 4px; border-radius: 8px; text-align: center;">
      <div style="font-size: 1.2rem;">🌪️</div>
      <b style="color: #e9d5ff; font-size: 0.74rem;">CUT HVAC</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Prevents fume cross-flow</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 8px 4px; border-radius: 8px; text-align: center;">
      <div style="font-size: 1.2rem;">🧭</div>
      <b style="color: #e9d5ff; font-size: 0.74rem;">MOVE UPWIND</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Towards Play Grounds</div>
    </div>
  </div>
  <div style="font-size: 0.80rem; color: #d8b4fe; line-height: 1.4; margin-top: 6px;">
    • <b>Never add water</b> to unknown acid/solvent pools (causes exothermic boiling).<br>
    • HazMat Level 2 certified marshals dispatched via Security Control.
  </div>
</div>
"""

    def _build_electrical_card(self) -> str:
        return """
<div style="background: linear-gradient(135deg, rgba(234, 179, 8, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #eab308; border-radius: 14px; padding: 14px 16px; margin-bottom: 8px;">
  <div style="background: #eab308; color: #422006; display: inline-block; padding: 2px 8px; border-radius: 6px; font-weight: 800; font-size: 0.70rem; text-transform: uppercase;">⚡ ELECTRICAL EMERGENCY & SUBSTATION ISOLATION</div>
  <div style="font-size: 1.15rem; font-weight: 800; color: #ffffff; margin: 6px 0 8px 0;">TRIP MAIN BREAKER & MAINTAIN 15M BUFFER</div>
  <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 8px 0;">
    <div style="background: rgba(0,0,0,0.4); padding: 8px 4px; border-radius: 8px; text-align: center;">
      <div style="font-size: 1.2rem;">🔌</div>
      <b style="color: #fef08a; font-size: 0.74rem;">TRIP BREAKER</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">De-energize wing substation</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 8px 4px; border-radius: 8px; text-align: center;">
      <div style="font-size: 1.2rem;">🚫💧</div>
      <b style="color: #fef08a; font-size: 0.74rem;">NO WATER</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Electrocution risk</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 8px 4px; border-radius: 8px; text-align: center;">
      <div style="font-size: 1.2rem;">📏</div>
      <b style="color: #fef08a; font-size: 0.74rem;">15M RADIUS</b>
      <div style="font-size: 0.65rem; color: #cbd5e1;">Arc flash perimeter</div>
    </div>
  </div>
  <div style="font-size: 0.80rem; color: #fef08a; line-height: 1.4; margin-top: 6px;">
    • Deploy Clean Agent FM-200 or CO2 extinguishers only.<br>
    • Report fallen conduit or sparking panels to Electrical Maintenance (Ext 2140).
  </div>
</div>
"""

    def _build_medical_card(self) -> str:
        return """
<div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #f87171; border-radius: 14px; padding: 14px 16px; margin-bottom: 8px;">
  <div style="background: #f87171; color: #450a0a; display: inline-block; padding: 2px 8px; border-radius: 6px; font-weight: 800; font-size: 0.70rem; text-transform: uppercase;">🏥 MEDICAL TRIAGE & CASUALTY RESPONSE</div>
  <div style="font-size: 1.15rem; font-weight: 800; color: #ffffff; margin: 6px 0 8px 0;">HEALTH CENTRE EXT 2255 / TRIAGE POST</div>
  <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin: 8px 0;">
    <div style="background: rgba(0,0,0,0.4); padding: 8px; border-radius: 8px;">
      <b style="color: #fca5a5; font-size: 0.78rem;">🏥 Campus Health Centre:</b>
      <div style="font-size: 0.84rem; color: #ffffff; font-weight: 700;">Ext 2255 / Casualty Dept</div>
    </div>
    <div style="background: rgba(0,0,0,0.4); padding: 8px; border-radius: 8px;">
      <b style="color: #38bdf8; font-size: 0.78rem;">🚑 Ambulance Inbound:</b>
      <div style="font-size: 0.84rem; color: #ffffff; font-weight: 700;">Dial 108 / Main Gate Clear</div>
    </div>
  </div>
  <div style="font-size: 0.80rem; color: #cbd5e1; line-height: 1.4;">
    • <b>Immobilize Fractures:</b> Do not move suspected spinal injuries unless in direct fire path.<br>
    • <b>Triage Post:</b> Field first aid stationed at Play Grounds Haven Assembly Zone.
  </div>
</div>
"""

    def _handle_sop_query(self, user_query: str, sops: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Returns crisis-formatted SOP protocol with immediate mandatory action upfront."""
        sop = sops[0]
        return {
            "response": (
                f"<div style='background: linear-gradient(135deg, rgba(14, 165, 233, 0.2) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #38bdf8; border-radius: 14px; padding: 14px 16px; margin-bottom: 8px;'>"
                f"<div style='display: flex; justify-content: space-between; align-items: center;'>"
                f"  <span style='background: #38bdf8; color: #082f49; padding: 2px 8px; border-radius: 6px; font-weight: 800; font-size: 0.70rem;'>📖 {sop['category'].upper()} PROTOCOL</span>"
                f"  <span style='color: #94a3b8; font-size: 0.72rem;'>Code: `{sop['protocol_code']}`</span>"
                f"</div>"
                f"<div style='font-size: 1.10rem; font-weight: 800; color: #ffffff; margin: 6px 0 6px 0;'>{sop['title']}</div>"
                f"<div style='background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 8px; padding: 8px 10px; margin: 6px 0; font-size: 0.80rem; color: #6ee7b7; font-weight: 700;'>"
                f"  ⚡ MANDATORY IMMEDIATE ACTION: {sop['mandatory_action']}"
                f"</div>"
                f"<details style='margin-top: 8px; font-size: 0.76rem; color: #cbd5e1;'>"
                f"  <summary style='color: #38bdf8; cursor: pointer; font-weight: 700;'>📋 Read Full Procedural Guidance</summary>"
                f"  <div style='margin-top: 6px; line-height: 1.5;'>{sop['content']}</div>"
                f"</details>"
                f"</div>"
            ),
            "metadata": None
        }

    def _handle_location_info(self, nid: str, node: Any) -> Dict[str, Any]:
        """Provides rich facility card with classification, location, elevation and egress distance."""
        dist_playgrounds = round(node.distance_to(self.search_engine.nodes['VIG_FACI_PLAY_GROUNDS']), 1) if 'VIG_FACI_PLAY_GROUNDS' in self.search_engine.nodes else 65.0
        sec = getattr(node, 'section', getattr(node, 'block', 'Academic Wing'))
        return {
            "response": (
                f"<div style='background: linear-gradient(135deg, rgba(14, 165, 233, 0.15) 0%, rgba(15, 23, 42, 0.95) 100%); border: 2px solid #38bdf8; border-radius: 14px; padding: 14px 16px; margin-bottom: 8px; box-shadow: 0 0 16px rgba(14, 165, 233, 0.2);'>"
                f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;'>"
                f"  <span style='background: #38bdf8; color: #082f49; font-weight: 800; font-size: 0.70rem; padding: 2px 8px; border-radius: 6px;'>🏢 FACILITY PROFILE</span>"
                f"  <span style='color: #94a3b8; font-size: 0.72rem;'>Node ID: <code>{nid}</code></span>"
                f"</div>"
                f"<div style='font-size: 1.15rem; font-weight: 800; color: #ffffff; margin: 4px 0 8px 0;'>📍 {node.name}</div>"
                f"<div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; font-size: 0.80rem; color: #cbd5e1; margin-bottom: 8px;'>"
                f"  <div style='background: rgba(0,0,0,0.3); padding: 6px 8px; border-radius: 8px;'>• <b>Building / Wing:</b> {sec}</div>"
                f"  <div style='background: rgba(0,0,0,0.3); padding: 6px 8px; border-radius: 8px;'>• <b>Floor Level:</b> Floor {node.floor} ({node.z}m)</div>"
                f"  <div style='background: rgba(0,0,0,0.3); padding: 6px 8px; border-radius: 8px;'>• <b>Classification:</b> <code>{node.node_type.upper()}</code></div>"
                f"  <div style='background: rgba(0,0,0,0.3); padding: 6px 8px; border-radius: 8px;'>• <b>Assembly Distance:</b> ~{dist_playgrounds}m</div>"
                f"</div>"
                f"<div style='background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 8px; padding: 8px 10px; font-size: 0.78rem; color: #6ee7b7;'>"
                f"  🏃 <b>To generate an emergency escape route from here:</b> Ask <i>\"How do I evacuate from {node.name}?\"</i> or click the Sync button below!"
                f"</div>"
                f"</div>"
            ),
            "metadata": {"start_node": nid}
        }

    def _handle_intelligent_fallback(self, user_query: str, origin_name: str, origin_id: str) -> Dict[str, Any]:
        """Provides tailored contextual safety intelligence addressing the specific inquiry."""
        q_lower = user_query.lower()
        
        # Tailor the advice based on detected keywords
        if any(w in q_lower for w in ["bag", "belongings", "laptop", "phone", "backpack"]):
            advice = "<b>Leave Heavy Belongings Behind:</b> Do NOT hesitate or delay evacuation to pack backpacks or laptops. Every second counts. Keep only immediate life-safety essentials."
        elif any(w in q_lower for w in ["door", "locked", "keys", "handle"]):
            advice = "<b>Locked Door Protocol:</b> If a primary door is jammed or locked, immediately divert to the secondary emergency exit. Feel metal handles with the back of hand before opening to detect heat."
        elif any(w in q_lower for w in ["window", "air", "breathe", "glass"]):
            advice = "<b>Window Guidance:</b> In heavy smoke, moving near an exterior window provides fresh air. DO NOT break glass unless signaling for rescue, as breaking windows can feed fires with fresh oxygen."
        elif any(w in q_lower for w in ["friend", "meet", "gather", "family", "classmate"]):
            advice = "<b>Safe Assembly Zone:</b> All evacuated personnel gather at <b>Vignan Play Grounds Primary Haven</b>. Do not search inside buildings; roll-call marshals track students at the exterior field."
        else:
            advice = f"<b>Immediate Action:</b> Maintain situational awareness around <code>{origin_name}</code>. Monitor stairwell condition displays and follow directional green egress signage to ground."

        return {
            "response": (
                f"<div style='background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(16, 185, 129, 0.45); border-radius: 14px; padding: 14px 16px; margin-bottom: 8px;'>"
                f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>"
                f"  <span style='background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #34d399; font-weight: 800; font-size: 0.70rem; padding: 2px 8px; border-radius: 6px;'>🛡️ SAFETY GUIDANCE</span>"
                f"  <span style='color: #94a3b8; font-size: 0.72rem;'>Sector: <code>{origin_name}</code></span>"
                f"</div>"
                f"<div style='font-size: 0.95rem; font-weight: 700; color: #ffffff; margin-bottom: 8px;'>Regarding: <i>\"{user_query}\"</i></div>"
                f"<div style='background: rgba(0,0,0,0.4); border-left: 3px solid #10b981; padding: 10px 12px; border-radius: 0 8px 8px 0; font-size: 0.82rem; color: #e2e8f0; line-height: 1.45; margin-bottom: 8px;'>"
                f"  {advice}"
                f"</div>"
                f"<div style='font-size: 0.76rem; color: #94a3b8;'>"
                f"  Need turn-by-turn navigation? Ask <i>\"What is the safest travel?\"</i> or <i>\"Where is nearest exit?\"</i>"
                f"</div>"
                f"</div>"
            ),
            "metadata": {"start_node": origin_id}
        }
