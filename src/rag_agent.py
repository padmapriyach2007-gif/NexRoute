import re
from typing import Dict, List, Tuple, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.campus_graph import build_campus_building

# Vignan University Verified SOP Knowledge Repository
VIGNAN_CAMPUS_SOP_DATABASE = [
    {
        "id": "VIGNAN_SOP_CHEM_01",
        "title": "Vignan Protocol: Chemical Reaction & Petroleum Labs Emergency Egress",
        "category": "Chemical Hazard",
        "content": (
            "For exothermic runaway, chemical vapor spills, or flammable solvent fires in Chemical Reaction Engg Lab, "
            "Process Dynamics Lab, or Drilling Fluids Lab: "
            "1. Activate emergency containment isolation manifold immediately. "
            "2. Never use water on Class B organic solvents; deploy dry chemical ABC fire extinguishers. "
            "3. If Chem Block Stairwell A (North) is smoke-compromised, reroute all occupants via Stairwell B (South). "
            "4. Evacuate through North Arterial Avenue directly to Vignan Play Grounds Primary Safe Assembly Area."
        ),
        "protocol_code": "VIGNAN-CHEM-01",
        "mandatory_action": "Cut off HVAC ventilation, isolate gas supply manifolds, and reroute via uncompromised stairwell."
    },
    {
        "id": "VIGNAN_SOP_EVAC_02",
        "title": "Vignan University Crowd Safety & Anti-Stampede Guidelines (NFPA 101)",
        "category": "Crowd Control",
        "content": (
            "During multi-floor evacuations in academic blocks (Chemical Engg, CSE, Civil/Mech, or NTR Library): "
            "Simultaneous mass flight causes fatal crowd crush and bottleneck compression on stairwells and landings. "
            "CampusSphere CSP Staged Scheduling mandates: Floor of incident origin evacuates in Wave 1. "
            "Adjacent floors evacuate in subsequent staged waves. Faculty marshals must regulate stair landing entry rates."
        ),
        "protocol_code": "VIGNAN-CSP-EGRESS",
        "mandatory_action": "Enforce staged floor exit scheduling and deploy crowd control marshals."
    },
    {
        "id": "VIGNAN_SOP_FIRE_03",
        "title": "Vignan Active Smoke Infiltration & Staircase Rerouting Protocol",
        "category": "Structural Egress",
        "content": (
            "When smoke optical sensors detect smoke infiltration in Stairwell A (North), "
            "the northern vertical shaft is flagged as non-traversable. Intelligent route guidance immediately "
            "applies infinite weight penalties and redirects occupants towards Stairwell B (South), "
            "exiting to Central Quadrangle Plaza and Play Grounds."
        ),
        "protocol_code": "VIGNAN-REROUTE-03",
        "mandatory_action": "Flag Stairwell A as blocked in real-time graph and redirect to Stairwell B."
    },
    {
        "id": "VIGNAN_SOP_EEE_04",
        "title": "Vignan Electrical & Computational Laboratories Isolation Protocol",
        "category": "Electrical Safety",
        "content": (
            "For electrical fires, transformer arcing, or power unit thermal events in EEE Power Systems Lab, "
            "Electrical Machines Lab, or CSE Networking/IT Labs: "
            "1. Immediately trip the building sub-station main breaker. "
            "2. Deploy Clean Agent FM-200 or CO2 extinguishers. Maintain 15-meter safety perimeter."
        ),
        "protocol_code": "VIGNAN-ELEC-04",
        "mandatory_action": "Trip wing electrical breaker and initiate Clean Agent FM-200 suppression."
    },
    {
        "id": "VIGNAN_SOP_CIVIL_MECH_05",
        "title": "Vignan Engineering Workshops & Materials Lab Safety Protocol",
        "category": "Mechanical / Materials Safety",
        "content": (
            "For hydraulic fluid spills, engine backfires, or structural debris incidents in IC Engines Lab, "
            "Fluid Mechanics Lab, Concrete Lab, or CNC/Welding Workshops: "
            "1. De-energize heavy rotating machinery and close hydraulic pressure lines. "
            "2. Evacuate personnel through West Avenue to Play Grounds Assembly Area."
        ),
        "protocol_code": "VIGNAN-WORKSHOP-05",
        "mandatory_action": "Shut off main compressor valves and evacuate via West Avenue."
    },
    {
        "id": "VIGNAN_SOP_MED_06",
        "title": "Vignan Health Centre Emergency Triage & Casualty Protocol",
        "category": "Medical Triage",
        "content": (
            "For incidents with injured personnel: "
            "Establish emergency triage operations at University Health Centre and Play Grounds Assembly Zone. "
            "Security wardens must clear the arterial roadway from Vignan Main Gate for incoming municipal ambulances."
        ),
        "protocol_code": "VIGNAN-MED-TRIAGE",
        "mandatory_action": "Establish triage post at University Health Centre & clear Main Gate avenue."
    },
    {
        "id": "VIGNAN_SOP_QUAKE_07",
        "title": "Vignan University Earthquake & Seismic Tremor Response Protocol",
        "category": "Earthquake / Structural",
        "content": (
            "During seismic tremors or structural shaking: "
            "1. DROP, COVER, AND HOLD ON: Take immediate shelter beneath heavy lab benches or load-bearing archways. "
            "2. Protect head and neck; stay clear of exterior glass facades, hanging lights, and tall chemical shelves. "
            "3. DO NOT run outside or rush stairwells during active shaking. "
            "4. Once shaking ceases: Systematically evacuate via unblocked fire stairwells to Vignan Play Grounds Primary Assembly Area. "
            "5. Never use elevators. Watch for fallen electrical wires."
        ),
        "protocol_code": "VIGNAN-EARTHQUAKE-07",
        "mandatory_action": "Drop, Cover, and Hold On; evacuate to Play Grounds open fields only after tremors cease."
    },
    {
        "id": "VIGNAN_SOP_FIRE_GEN_08",
        "title": "Vignan General Structural Fire & Smoke Evacuation Guidelines",
        "category": "Fire & Smoke",
        "content": (
            "In case of general fire alarm or visible smoke: "
            "1. Sound the nearest manual fire pull station immediately. "
            "2. Stay low to the floor: Crawl on hands and knees where breathable air remains cleanest beneath rising toxic smoke. "
            "3. Cover mouth and nose with a damp cloth or garment. "
            "4. Test doors with the back of your hand before turning handles; if warm, do NOT open. "
            "5. Follow CampusAegis green egress vectors towards uncompromised stairwells and exit to ground assembly."
        ),
        "protocol_code": "VIGNAN-FIRE-GEN-08",
        "mandatory_action": "Pull alarm, stay low beneath thermal smoke layer, and proceed to designated ground exits."
    },
    {
        "id": "VIGNAN_SOP_CONTACTS_09",
        "title": "Vignan Emergency Control Room, Medical & Security Contacts Directory",
        "category": "Emergency Contacts",
        "content": (
            "Official 24/7 Vignan Emergency Response Contacts: "
            "• Campus Security Main Control Room: Ext 2200 / +91-863-2344700 (Option 1) "
            "• University Health Centre Emergency Casualty: Ext 2255 / +91-863-2344700 (Option 4) "
            "• Campus Fire Safety Marshal: Ext 2112 / Internal Radio Channel 4 "
            "• Chief Proctor & Hostels Emergency Helpline: Ext 2400 "
            "• Municipal Ambulance / Fire / Police Dispatches: 108 (Ambulance), 101 (Fire), 112 (National Emergency)"
        ),
        "protocol_code": "VIGNAN-EMERGENCY-CONTACTS",
        "mandatory_action": "Contact Campus Security Control Room (Ext 2200) and University Health Centre (Ext 2255)."
    },
    {
        "id": "VIGNAN_SOP_AEGIS_10",
        "title": "CampusAegis Autonomous Defense & Multi-Agent Architecture Overview",
        "category": "System Architecture",
        "content": (
            "CampusAegis is an autonomous indoor emergency guidance and intelligent evacuation system built for Vignan University. "
            "It integrates: "
            "1. Deterministic Multi-Floor A* Egress: Sub-50ms recalculation around real-time smoke and fire hazards. "
            "2. Horn Clause Deductive Engine: Formal mathematical proof verification of NFPA 101 safety guarantees. "
            "3. Anti-Stampede CSP Staged Scheduler: Staggers mass evacuations into phased waves to eliminate crowd bottlenecks. "
            "4. RAG-Powered Safety Assistant: Instant retrieval of verified university emergency SOPs and 97 campus locations."
        ),
        "protocol_code": "CAMPUS-AEGIS-CORE",
        "mandatory_action": "Follow dynamic turn-by-turn routing vectors and phased departure wave directives."
    }
]

class LocalRAGAgent:
    def __init__(self):
        self.corpus = VIGNAN_CAMPUS_SOP_DATABASE
        self.documents = [doc["title"] + " " + doc["content"] for doc in self.corpus]
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.doc_vectors = self.vectorizer.fit_transform(self.documents)
        
        # Load all 97+ campus nodes from graph
        self.all_nodes, _ = build_campus_building()

    def retrieve_sop(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.doc_vectors)[0]
        ranked_indices = similarities.argsort()[::-1][:top_k]
        
        results = []
        for idx in ranked_indices:
            score = float(similarities[idx])
            doc = dict(self.corpus[idx])
            doc["similarity_score"] = round(score, 4)
            results.append(doc)
            
        return results

    def detect_vignan_location(self, alert_text: str) -> Optional[Tuple[str, Any]]:
        """
        Scans alert text against ALL 97 Vignan University locations extracted from the tour dropdown.
        Supports:
          1. Direct Navigation Node ID (e.g., 'SEID00000002777' or 'SEID2777')
          2. Virtual Tour Panorama ID (e.g., 'CAoSLEFGMVFpcE4w...')
          3. Internal Node ID (e.g., 'VIG_FOUN_CHAIRMAN_S_ROOM')
          4. Full or substring room/location names
        """
        text_clean = alert_text.strip()
        text_lower = text_clean.lower()
        text_upper = text_clean.upper()

        # 1. Direct Navigation Node ID Matching (e.g., SEID00000002777)
        for nid, node in self.all_nodes.items():
            if node.nav_id and node.nav_id.upper() in text_upper:
                return (nid, node)
            # Support shorthand like SEID2777 or trailing digits
            if node.nav_id and node.nav_id.startswith("SEID0000000"):
                short_code = node.nav_id.replace("SEID0000000", "").upper()
                if f"SEID{short_code}" in text_upper or f"SEID {short_code}" in text_upper:
                    return (nid, node)

        # 2. Virtual Tour Panorama ID Matching (e.g., CAoSLEF...)
        for nid, node in self.all_nodes.items():
            pano = getattr(node, 'pano_id', '')
            if pano and len(pano) > 8 and (pano in text_clean or pano[:20] in text_clean):
                return (nid, node)

        # 3. Direct Internal Node ID Matching (e.g., VIG_FOUN_CHAIRMAN_S_ROOM)
        for nid, node in self.all_nodes.items():
            if nid in text_upper or nid.rstrip('_') in text_upper:
                return (nid, node)

        best_match = None
        best_score = 0

        for nid, node in self.all_nodes.items():
            node_name_lower = node.name.lower()
            
            # Exact match of room name
            if node_name_lower in text_lower:
                score = len(node_name_lower) * 2  # Longer specific names have higher priority
                if score > best_score:
                    best_score = score
                    best_match = (nid, node)
                continue

            # Check individual significant keywords (at least 2 words matching)
            words = [w for w in re.split(r'\W+', node_name_lower) if len(w) > 3 and w not in ["room", "lab", "dept", "hall", "view", "section"]]
            if words:
                matches = sum(1 for w in words if w in text_lower)
                if matches >= 2 or (len(words) == 1 and matches == 1 and words[0] in text_lower):
                    score = matches * 10
                    if score > best_score:
                        best_score = score
                        best_match = (nid, node)

        return best_match

    def parse_incident_alert(self, raw_alert_text: str) -> Dict[str, Any]:
        text_lower = raw_alert_text.lower()
        extracted_facts = set()
        detected_entities = {}

        # 1. Match against all 97 Vignan Locations
        matched = self.detect_vignan_location(raw_alert_text)
        if matched:
            matched_nid, matched_node = matched
            detected_location = f"{matched_node.name} [{matched_node.block}]"
            detected_floor = matched_node.floor
            detected_node_id = matched_nid
            detected_section = matched_node.section
            # Add semantic facts based on block
            if "chemical" in matched_node.block.lower() or "chem" in matched_node.name.lower() or "reaction" in matched_node.name.lower():
                extracted_facts.add("Location(Chem_Lab)")
            elif "cse" in matched_node.block.lower() or "computer" in matched_node.name.lower():
                extracted_facts.add("Location(CSE_Lab)")
            elif "library" in matched_node.block.lower():
                extracted_facts.add("Location(NTR_Library)")
            elif "admin" in matched_node.block.lower():
                extracted_facts.add("Location(Admin_Block)")
            else:
                extracted_facts.add(f"Location({matched_node.section.replace(' ', '_')})")
        else:
            # Fallback default
            detected_location = "Chemical Reaction Engg Lab [Chemical Engineering Block]"
            detected_floor = 2
            detected_node_id = "VIG_ENGI_CHEMICAL_REACTION_ENG"
            detected_section = "Dept of Chemical Engineering"
            extracted_facts.add("Location(Chem_Lab)")

        # 2. Hazard Clues & Smoke
        if any(w in text_lower for w in ["smoke", "fume", "cloud", "smog", "acrid", "choking"]):
            extracted_facts.add("Observed(Smoke)")
            detected_entities["hazard_type"] = "Smoke & Toxic Fumes"

        if any(w in text_lower for w in ["fire", "flame", "blaze", "burning", "sparks"]):
            extracted_facts.add("Observed(Open_Flame)")
            detected_entities["fire_present"] = True

        if any(w in text_lower for w in ["chemical", "solvent", "acid", "ethanol", "reagent", "benzene", "petroleum", "oil"]):
            extracted_facts.add("Chemicals_Present(Volatile_Solvents)")
            detected_entities["chemical_hazard"] = True

        # 3. Stairwell Blockage Detection
        stair_blocked = False
        blocked_stair_id = None
        if any(s in text_lower for s in ["stairwell a", "stair a", "north stair", "smoke in stair"]):
            extracted_facts.add("Observed(Smoke_Infiltration)")
            extracted_facts.add("Stairwell_Status(Stairwell_A)")
            stair_blocked = True
            blocked_stair_id = "CHEM_STAIR_A_F2"
            detected_entities["blocked_shaft"] = "Chem Block Stairwell A (North Landing)"
        elif any(s in text_lower for s in ["stairwell b", "stair b", "south stair"]):
            stair_blocked = True
            blocked_stair_id = "CHEM_STAIR_B_F2"
            detected_entities["blocked_shaft"] = "Chem Block Stairwell B (South Landing)"

        # Trapped Count
        match_trapped = re.search(r'(\d+)\s*(?:students?|people|persons?|occupants?)\s*trapped', text_lower)
        trapped_count = int(match_trapped.group(1)) if match_trapped else 0
        detected_entities["trapped_count"] = trapped_count

        retrieved_sops = self.retrieve_sop(raw_alert_text, top_k=2)

        return {
            "raw_alert": raw_alert_text,
            "detected_node_id": detected_node_id,
            "detected_location": detected_location,
            "detected_section": detected_section,
            "detected_floor": detected_floor,
            "extracted_facts": list(extracted_facts),
            "stair_blocked": stair_blocked,
            "blocked_stair_id": blocked_stair_id,
            "entities": detected_entities,
            "retrieved_sops": retrieved_sops
        }
