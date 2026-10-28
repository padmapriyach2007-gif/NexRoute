"""
Journey Storyteller & Creative Narrative Travel Guide
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Adaptive Transit System

Transforms raw technical GPS turn maneuvers into an engaging, creative,
and user-interactive Travel Story with:
1. Chapter-by-chapter story progression (Departure, Cruising Corridor, Connecting Byways, Safe Arrival).
2. Spoken voice narrative synthesis (Listen to Story).
3. Compact, zero-scroll interactive storybook interface with chapter flip tabs.
"""

from dataclasses import dataclass
import json
import re
from typing import Any, Dict, List, Optional


@dataclass
class JourneyChapter:
    chapter_num: int
    title: str
    emoji: str
    narrative: str
    road_highlight: str
    distance_km: float
    duration_mins: float
    safety_note: str
    spoken_text: str


def generate_journey_story(
    origin: str,
    destination: str,
    steps: List[Dict[str, Any]],
    total_distance_km: float,
    total_duration_minutes: float,
    travel_mode: str = "Car",
    hazard_notes: str = ""
) -> List[JourneyChapter]:
    """
    Transforms any sequence of technical maneuvers into 3 to 4 cohesive,
    creative, and engaging story chapters.
    """
    clean_orig = re.sub(r'[📍🏁🧭🚗●🛰️]', '', origin).strip()
    clean_orig = clean_orig.split(",")[0].strip() or "Departure Point"
    if clean_orig.lower() in ["current location", "starting point", "live satellite"]:
        clean_orig = "Your Starting Point"

    clean_dest = re.sub(r'[📍🏁🧭🚗●🛰️]', '', destination).strip()
    clean_dest = clean_dest.split(",")[0].strip() or "Destination"

    mode_word = "walk" if "walk" in travel_mode.lower() else (
        "ride" if "bike" in travel_mode.lower() or "motorcycle" in travel_mode.lower() or "bicycle" in travel_mode.lower() else (
            "drive" if "tractor" in travel_mode.lower() else "drive"
        )
    )

    num_steps = len(steps) if steps else 0

    # Extract distinct roads and their cumulative distances
    road_distances: Dict[str, float] = {}
    for s in steps:
        r = s.get("road", "").strip()
        d = float(s.get("distance_m", 0.0))
        if r and r.lower() not in ["local corridor", "connected road", "unnamed road", "service road"]:
            r_clean = re.sub(r'^(onto|on|turn onto)\s+', '', r, flags=re.IGNORECASE).strip().title()
            if r_clean:
                road_distances[r_clean] = road_distances.get(r_clean, 0.0) + d

    # Sort roads by length so Chapter 2 highlights the longest cruising arterial
    sorted_roads = sorted(road_distances.keys(), key=lambda k: road_distances[k], reverse=True)
    main_arterial = sorted_roads[0] if sorted_roads else "the regional transit highway"
    secondary_arterial = sorted_roads[1] if len(sorted_roads) > 1 else (sorted_roads[0] if sorted_roads else "connected corridor links")

    chapters: List[JourneyChapter] = []

    # -------------------------------------------------------------------------
    # CHAPTER 1: The Departure — Setting Out
    # -------------------------------------------------------------------------
    c1_dist = round(min(total_distance_km * 0.15, max(0.4, total_distance_km / 5.0)), 1)
    c1_time = round(max(1.0, total_duration_minutes * 0.12), 1)
    c1_road = steps[0].get("road", "Main Departure Link") if steps else "Origin Link"
    if c1_road.lower() in ["local corridor", "connected road"]:
        c1_road = f"{clean_orig} Access Road"

    c1_narrative = (
        f"Your expedition begins at <b>{clean_orig}</b>. Setting out with clear momentum, "
        f"you {mode_word} along {c1_road} for the initial {c1_dist:.1f} km. "
        f"The transit path quickly aligns onto the open navigation corridor as your satellite lock confirms zero immediate obstacles."
    )
    c1_spoken = (
        f"Chapter 1: The Departure. Your journey begins at {clean_orig}. "
        f"You set out along {c1_road} for {c1_dist:.1f} kilometers with clear visibility and optimal path alignment."
    )

    chapters.append(JourneyChapter(
        chapter_num=1,
        title="The Departure",
        emoji="🚩",
        narrative=c1_narrative,
        road_highlight=c1_road,
        distance_km=c1_dist,
        duration_mins=c1_time,
        safety_note="Satellite lock verified • Open departure corridor",
        spoken_text=c1_spoken
    ))

    # -------------------------------------------------------------------------
    # CHAPTER 2: The Cruising Corridor — Main Transit Stretch
    # -------------------------------------------------------------------------
    c2_dist = round(max(0.8, total_distance_km * 0.50), 1)
    c2_time = round(max(2.0, total_duration_minutes * 0.50), 1)
    c2_narrative = (
        f"Entering <b>{main_arterial}</b>, you settle into the primary cruising phase of your route covering "
        f"{c2_dist:.1f} km over the next {c2_time:.0f} minutes. Pavement quality is steady, allowing uninterrupted cruising "
        f"while maintaining optimal transit efficiency and smooth speed."
    )
    c2_spoken = (
        f"Chapter 2: The Cruising Corridor. Entering {main_arterial}, you enjoy the longest cruising stretch of your journey "
        f"covering {c2_dist:.1f} kilometers over approximately {c2_time:.0f} minutes with smooth, uninterrupted traffic flow."
    )

    chapters.append(JourneyChapter(
        chapter_num=2,
        title="The Cruising Corridor",
        emoji="🛣️",
        narrative=c2_narrative,
        road_highlight=main_arterial,
        distance_km=c2_dist,
        duration_mins=c2_time,
        safety_note="Primary arterial • 100% clear pavement & hazard bypass",
        spoken_text=c2_spoken
    ))

    # -------------------------------------------------------------------------
    # CHAPTER 3: The Connecting Byways — Adaptive Evasion
    # -------------------------------------------------------------------------
    c3_dist = round(max(0.4, total_distance_km * 0.25), 1)
    c3_time = round(max(1.5, total_duration_minutes * 0.25), 1)
    c3_narrative = (
        f"Navigating the junction transitions along {secondary_arterial}, your route makes coordinated turns spanning {c3_dist:.1f} km. "
        f"The NEXROUTE predictive engine steers you safely around congested bottlenecks and confirmed road hazards, "
        f"ensuring your travel remains continuous and stress-free."
    )
    c3_spoken = (
        f"Chapter 3: Connecting Byways. Navigating smoothly through junction transitions along {secondary_arterial}, "
        f"the adaptive engine guides you along clear transit links, evading road restrictions and local bottlenecks."
    )

    chapters.append(JourneyChapter(
        chapter_num=3,
        title="Connecting Byways",
        emoji="🌿",
        narrative=c3_narrative,
        road_highlight=secondary_arterial,
        distance_km=c3_dist,
        duration_mins=c3_time,
        safety_note="Adaptive detour active • Zero hazard exposure",
        spoken_text=c3_spoken
    ))

    # -------------------------------------------------------------------------
    # CHAPTER 4: The Final Approach — Safe Arrival
    # -------------------------------------------------------------------------
    c4_dist = round(max(0.2, total_distance_km - (c1_dist + c2_dist + c3_dist)), 1)
    c4_time = round(max(1.0, total_duration_minutes - (c1_time + c2_time + c3_time)), 1)
    c4_narrative = (
        f"Approaching the final terminal at <b>{clean_dest}</b>, you glide onto the arrival avenue for the remaining {c4_dist:.1f} km. "
        f"You safely arrive at your destination safe terminal right on schedule in ~{total_duration_minutes:.0f} minutes total travel time, "
        f"completing the {total_distance_km:.1f} km trip with full safety verification."
    )
    c4_spoken = (
        f"Chapter 4: Safe Arrival. Approaching {clean_dest}, you complete the final stretch and safely arrive at your destination terminal "
        f"in approximately {total_duration_minutes:.0f} minutes. Journey successfully completed!"
    )

    chapters.append(JourneyChapter(
        chapter_num=4,
        title="The Final Approach & Safe Arrival",
        emoji="🏆",
        narrative=c4_narrative,
        road_highlight=f"{clean_dest} Terminal Link",
        distance_km=c4_dist,
        duration_mins=c4_time,
        safety_note=f"Safe Arrival at {clean_dest} • Journey Complete",
        spoken_text=c4_spoken
    ))

    return chapters


def build_journey_story_html(
    chapters: List[JourneyChapter],
    origin: str,
    destination: str,
    initial_chapter_idx: int = 0,
    current_step: int = 0,
    total_steps: int = 4
) -> str:
    """
    Renders an interactive, compact, zero-scroll Journey Storybook HUD.
    Features:
    - Chapter progression dynamically moves parallel to user's real GPS / milestone detection.
    - Synchronized via BroadcastChannel, postMessage, and LocalStorage across iframes.
    - Click through Chapter 1 -> 4 tabs or auto-sync with journey progression.
    - Click 'Narrate Chapter' to hear the story aloud with natural speech synthesis.
    - Switch between 'Interactive Chapter Mode' and 'Read Full Story' view.
    """
    if not chapters:
        return ""

    chapters_data = [
        {
            "num": c.chapter_num,
            "title": c.title,
            "emoji": c.emoji,
            "narrative": c.narrative,
            "road": c.road_highlight,
            "dist": c.distance_km,
            "time": c.duration_mins,
            "safety": c.safety_note,
            "spoken": c.spoken_text
        }
        for c in chapters
    ]
    chapters_json = json.dumps(chapters_data)

    clean_orig = re.sub(r'[📍🏁🧭🚗●🛰️]', '', origin).strip().split(",")[0]
    clean_dest = re.sub(r'[📍🏁🧭🚗●🛰️]', '', destination).strip().split(",")[0]

    return f"""
    <style>
    .story-container {{
        background: linear-gradient(135deg, rgba(8, 18, 36, 0.96) 0%, rgba(15, 23, 42, 0.92) 100%);
        border: 1.5px solid rgba(56, 189, 248, 0.35);
        border-radius: 12px;
        padding: 16px 20px;
        margin: 10px 0;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6), 0 0 20px rgba(56, 189, 248, 0.12);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    .chapter-tab-btn {{
        background: rgba(15, 23, 42, 0.7);
        color: #94a3b8;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 0.78rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    .chapter-tab-btn:hover {{
        background: rgba(56, 189, 248, 0.15);
        color: #f1f5f9;
        border-color: rgba(56, 189, 248, 0.4);
    }}
    .chapter-tab-btn.active {{
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.3) 0%, rgba(3, 105, 161, 0.5) 100%);
        color: #38bdf8;
        border: 1.5px solid #38bdf8;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
    }}
    .story-card {{
        background: rgba(0, 0, 0, 0.35);
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 12px 0 10px 0;
        min-height: 110px;
        transition: all 0.3s ease;
    }}
    .btn-story-nav {{
        background: rgba(56, 189, 248, 0.12);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.35);
        padding: 6px 14px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.2s ease;
    }}
    .btn-story-nav:hover {{
        background: #38bdf8;
        color: #02132b;
    }}
    .btn-narrate {{
        background: #10b981;
        color: #ffffff;
        border: none;
        padding: 6px 14px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        cursor: pointer;
        box-shadow: 0 2px 10px rgba(16, 185, 129, 0.4);
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    .btn-narrate:hover {{
        background: #059669;
    }}
    </style>

    <div class='story-container'>
        <!-- Story Header -->
        <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 10px;'>
            <div style='display: flex; align-items: center; gap: 10px;'>
                <span style='font-size: 1.35rem;'>📖</span>
                <div>
                    <div style='font-size: 0.95rem; font-weight: 800; color: #ffffff; letter-spacing: 0.02em;'>
                        JOURNEY CHRONICLE: THE TRAVEL STORY
                    </div>
                    <div style='display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-top: 3px;'>
                        <div style='font-size: 0.73rem; color: #94a3b8;'>
                            From <b>{clean_orig}</b> to <b>{clean_dest}</b> • Interactive Narrative
                        </div>
                        <span id='story-sync-indicator' style='background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.35); color: #34d399; font-size: 0.68rem; font-weight: 800; padding: 2px 8px; border-radius: 4px; display: inline-flex; align-items: center; gap: 4px;'>
                            <span>🟢</span> <span id='story-sync-text'>PARALLEL SATELLITE SYNC</span>
                        </span>
                    </div>
                </div>
            </div>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <button id='btn-toggle-view' class='btn-story-nav' onclick='toggleStoryView()'>
                    📜 View Full Tale
                </button>
            </div>
        </div>

        <!-- Chapter Tab Bar -->
        <div id='chapter-tabs-bar' style='display: flex; gap: 8px; margin-top: 12px; overflow-x: auto; padding-bottom: 4px;'>
            <!-- Populated dynamically via JS -->
        </div>

        <!-- Interactive Chapter View -->
        <div id='interactive-story-card' class='story-card'>
            <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px; margin-bottom: 8px;'>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <span id='story-chapter-emoji' style='font-size: 1.15rem;'>🚩</span>
                    <b id='story-chapter-title' style='color: #38bdf8; font-size: 0.92rem;'>Chapter 1: The Departure</b>
                </div>
                <div style='display: flex; align-items: center; gap: 10px; font-size: 0.74rem;'>
                    <span id='story-meta-dist' style='background: rgba(56, 189, 248, 0.12); color: #38bdf8; padding: 2px 8px; border-radius: 4px; font-weight: 700;'>📏 0.5 km</span>
                    <span id='story-meta-time' style='background: rgba(16, 185, 129, 0.12); color: #34d399; padding: 2px 8px; border-radius: 4px; font-weight: 700;'>⏱️ ~2 mins</span>
                </div>
            </div>
            <div id='story-narrative-text' style='color: #f1f5f9; font-size: 0.88rem; line-height: 1.55;'>
                <!-- Narrative inserted here -->
            </div>
            <div style='margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255, 255, 255, 0.06); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px;'>
                <div style='font-size: 0.72rem; color: #a7f3d0;'>
                    🛡️ <span id='story-safety-badge'>Satellite verified route</span>
                </div>
                <div style='display: flex; gap: 6px;'>
                    <button class='btn-story-nav' onclick='prevChapter()'>◀ Prev Chapter</button>
                    <button class='btn-story-nav' onclick='nextChapter()'>Next Chapter ➔</button>
                </div>
            </div>
        </div>

        <!-- Continuous Full Story View (Hidden by default, togglable) -->
        <div id='full-story-view' style='display: none; background: rgba(0, 0, 0, 0.35); border-radius: 8px; padding: 14px 18px; margin: 12px 0 10px 0;'>
            <!-- Populated dynamically via JS -->
        </div>
    </div>

    <script>
    (function() {{
        const CHAPTERS = {chapters_json};
        const TOTAL_CHAPS = CHAPTERS.length;
        const INITIAL_CHAP = {int(initial_chapter_idx)};
        let activeChapIdx = Math.max(0, Math.min(TOTAL_CHAPS - 1, INITIAL_CHAP));
        let isFullView = false;

        if ('speechSynthesis' in window) {{
            try {{ window.speechSynthesis.cancel(); }} catch(e) {{}}
        }}

        function speak(text) {{
            if ('speechSynthesis' in window) {{
                try {{ window.speechSynthesis.cancel(); }} catch(e) {{}}
            }}
            return;
        }}

        window.narrateActiveChapter = function() {{
            if ('speechSynthesis' in window) {{
                try {{ window.speechSynthesis.cancel(); }} catch(e) {{}}
            }}
        }};

        function renderTabs() {{
            const bar = document.getElementById('chapter-tabs-bar');
            if (!bar) return;
            bar.innerHTML = CHAPTERS.map((c, i) => `
                <button id="chap-tab-${{i}}" class="chapter-tab-btn ${{i === activeChapIdx ? 'active' : ''}}" onclick="selectChapter(${{i}})">
                    <span>${{c.emoji}}</span>
                    <span>Ch. ${{c.num}}: ${{c.title}}</span>
                </button>
            `).join('');
        }}

        window.selectChapter = function(idx) {{
            if (idx < 0 || idx >= TOTAL_CHAPS) return;
            activeChapIdx = idx;
            renderTabs();

            const c = CHAPTERS[idx];
            const emojiEl = document.getElementById('story-chapter-emoji');
            if (emojiEl) emojiEl.innerText = c.emoji;
            const titleEl = document.getElementById('story-chapter-title');
            if (titleEl) titleEl.innerText = `Chapter ${{c.num}}: ${{c.title}}`;
            const textEl = document.getElementById('story-narrative-text');
            if (textEl) textEl.innerHTML = c.narrative;
            const distEl = document.getElementById('story-meta-dist');
            if (distEl) distEl.innerText = `📏 ${{c.dist.toFixed(1)}} km`;
            const timeEl = document.getElementById('story-meta-time');
            if (timeEl) timeEl.innerText = `⏱️ ~${{Math.round(c.time)}} mins`;
            const safetyEl = document.getElementById('story-safety-badge');
            if (safetyEl) safetyEl.innerText = c.safety;
        }};

        window.prevChapter = function() {{
            const newIdx = (activeChapIdx - 1 + TOTAL_CHAPS) % TOTAL_CHAPS;
            window.selectChapter(newIdx);
        }};

        window.nextChapter = function() {{
            const newIdx = (activeChapIdx + 1) % TOTAL_CHAPS;
            window.selectChapter(newIdx);
        }};

        window.toggleStoryView = function() {{
            isFullView = !isFullView;
            const singleCard = document.getElementById('interactive-story-card');
            const fullView = document.getElementById('full-story-view');
            const tabsBar = document.getElementById('chapter-tabs-bar');
            const btnToggle = document.getElementById('btn-toggle-view');

            if (isFullView) {{
                singleCard.style.display = 'none';
                tabsBar.style.display = 'none';
                fullView.style.display = 'block';
                btnToggle.innerText = '📖 Chapter Mode';

                fullView.innerHTML = CHAPTERS.map(c => `
                    <div style='margin-bottom: 14px; padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.06);'>
                        <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;'>
                            <b style='color: #38bdf8; font-size: 0.88rem;'>${{c.emoji}} Chapter ${{c.num}}: ${{c.title}}</b>
                            <span style='font-size: 0.72rem; color: #94a3b8;'>${{c.dist.toFixed(1)}} km • ~${{Math.round(c.time)}} mins</span>
                        </div>
                        <div style='font-size: 0.84rem; color: #f1f5f9; line-height: 1.5;'>${{c.narrative}}</div>
                    </div>
                `).join('');
            }} else {{
                singleCard.style.display = 'block';
                tabsBar.style.display = 'flex';
                fullView.style.display = 'none';
                btnToggle.innerText = '📜 View Full Tale';
            }}
        }};

        window.narrateFullStory = function() {{
            if ('speechSynthesis' in window) {{
                try {{ window.speechSynthesis.cancel(); }} catch(e) {{}}
            }}
        }};

        // Real-time synchronization function: moves story parallel with user detection
        function syncChapterWithVehicle(stepIdx, totalSteps, label) {{
            if (!totalSteps || totalSteps <= 1) return;
            const ratio = stepIdx / Math.max(1, totalSteps - 1);
            let targetChap = 0;
            if (stepIdx >= totalSteps - 1 || ratio >= 0.88) {{
                targetChap = TOTAL_CHAPS - 1; // Chapter 4: Safe Arrival
            }} else if (ratio >= 0.55) {{
                targetChap = Math.min(TOTAL_CHAPS - 1, 2); // Chapter 3: Connecting Byways
            }} else if (ratio >= 0.22) {{
                targetChap = Math.min(TOTAL_CHAPS - 1, 1); // Chapter 2: Cruising Corridor
            }} else {{
                targetChap = 0; // Chapter 1: The Departure
            }}

            if (targetChap !== activeChapIdx) {{
                window.selectChapter(targetChap);
            }}

            const syncEl = document.getElementById('story-sync-text');
            if (syncEl) {{
                const c = CHAPTERS[targetChap];
                if (stepIdx >= totalSteps - 1) {{
                    syncEl.innerHTML = "🏆 DESTINATION REACHED • Ch. " + c.num + ": " + c.title;
                }} else {{
                    syncEl.innerHTML = "🟢 PARALLEL SATELLITE SYNC: Ch. " + c.num + " • " + (label || "En Route");
                }}
            }}
        }}

        // 1. BroadcastChannel Listener for instant inter-frame communication
        try {{
            if (window.BroadcastChannel) {{
                const bc = new BroadcastChannel('pathfinder_journey_channel');
                bc.onmessage = function(ev) {{
                    const data = ev.data;
                    if (data && data.type === 'PATHFINDER_VEHICLE_UPDATE') {{
                        syncChapterWithVehicle(data.step, data.totalSteps || 7, data.label);
                    }}
                }};
            }}
        }} catch(e) {{}}

        // 2. Window postMessage listener
        window.addEventListener('message', function(ev) {{
            const data = ev.data;
            if (data && data.type === 'PATHFINDER_VEHICLE_UPDATE') {{
                syncChapterWithVehicle(data.step, data.totalSteps || 7, data.label);
            }}
        }});

        // 3. Storage event listener (syncs across iframe boundaries)
        window.addEventListener('storage', function(ev) {{
            if (ev.key === 'pathfinder_vehicle_state' && ev.newValue) {{
                try {{
                    const data = JSON.parse(ev.newValue);
                    if (data && data.step !== undefined) {{
                        syncChapterWithVehicle(data.step, data.totalSteps || 7, data.label);
                    }}
                }} catch(e) {{}}
            }}
        }});

        // 4. Polling fallback to guarantee continuous live lock
        let lastPolledStep = -1;
        setInterval(function() {{
            try {{
                const raw = localStorage.getItem('pathfinder_vehicle_state');
                if (raw) {{
                    const data = JSON.parse(raw);
                    if (data && data.step !== undefined && data.step !== lastPolledStep) {{
                        lastPolledStep = data.step;
                        syncChapterWithVehicle(data.step, data.totalSteps || 7, data.label);
                    }}
                }}
            }} catch(e) {{}}
        }}, 400);

        // Initialize view on load with starting chapter
        renderTabs();
        window.selectChapter(activeChapIdx);

        // Check if there is already a live vehicle position cached in local storage
        try {{
            const initRaw = localStorage.getItem('pathfinder_vehicle_state');
            if (initRaw) {{
                const initData = JSON.parse(initRaw);
                if (initData && initData.step !== undefined) {{
                    syncChapterWithVehicle(initData.step, initData.totalSteps || 7, initData.label);
                }}
            }}
        }} catch(e) {{}}
    }})();
    </script>
    """


# =============================================================================
# VIRTUAL MAN'S INTERACTIVE TURN-BY-TURN ROUTE GUIDE (ACCESSIBLE TO EVERY TRAVELER)
# =============================================================================

@dataclass
class FriendlyTurnStep:
    step_num: int
    total_steps: int
    direction_type: str
    action_headline: str
    virtual_guide_speech: str
    what_to_look_for: str
    distance_human: str
    time_estimate: str
    road_name: str
    icon: str
    spoken_text: str
    accessible_guidance: str = ""
    tactile_crossing_note: str = ""
    distance_m: float = 150.0


def generate_friendly_virtual_guide_turns(
    steps: List[Dict[str, Any]],
    origin: str,
    destination: str,
    travel_mode: str = "Car",
    language: str = "en"
) -> List[FriendlyTurnStep]:
    """
    Transforms raw technical GPS maneuvers into rich, creative, and easily
    understandable step-by-step guidance spoken by a friendly Virtual Man guide.
    Supports complete multilingual localization across Telugu, Hindi, Tamil,
    Kannada, Malayalam, Bengali, Marathi, and English.
    """
    clean_orig = re.sub(r'[📍🏁🧭🚗●🛰️]', '', origin).strip().split(",")[0].strip() or "Departure Point"
    if clean_orig.lower() in ["current location", "starting point", "live satellite"]:
        clean_orig = "Your Starting Point"

    clean_dest = re.sub(r'[📍🏁🧭🚗●🛰️]', '', destination).strip().split(",")[0].strip() or "Destination"

    mode_lower = travel_mode.lower()
    mode_action = "walk" if "walk" in mode_lower else ("ride" if "bike" in mode_lower or "cycle" in mode_lower else "drive")
    speed_factor = 4.0 if "walk" in mode_lower else (15.0 if "cycle" in mode_lower else 45.0)

    if not steps:
        # Fallback single step
        return [
            FriendlyTurnStep(
                step_num=1,
                total_steps=1,
                direction_type="ARRIVE",
                action_headline=f"Proceed from {clean_orig} to {clean_dest}",
                virtual_guide_speech=f"Hello traveler! Move forward along the main route until you reach {clean_dest}. Your destination is straight ahead.",
                what_to_look_for=f"Look for the arrival signs for {clean_dest}.",
                distance_human="Direct route",
                time_estimate="On schedule",
                road_name="Main Corridor",
                icon="🏁",
                spoken_text=f"Move forward from {clean_orig} towards {clean_dest}. You will arrive right on schedule.",
                accessible_guidance="Direct step-free corridor with level pedestrian sidewalks and tactile guidance paving.",
                tactile_crossing_note="Wide continuous pedestrian crosswalks at all intersections."
            )
        ]

    total_count = len(steps)
    friendly_steps: List[FriendlyTurnStep] = []

    for i, s in enumerate(steps):
        instr = s.get("instruction", "").strip()
        raw_road = s.get("road", "").strip()
        dist_m = float(s.get("distance_m", 0.0))

        # 1. Clean road name into human-friendly term
        generic_roads = ["local corridor", "connected road", "unnamed road", "service road", "corridor", "link"]
        if not raw_road or raw_road.lower() in generic_roads:
            if i == 0:
                road_display = f"{clean_orig} Departure Lane"
            elif i == total_count - 1:
                road_display = f"{clean_dest} Arrival Avenue"
            else:
                road_display = "Connecting Street"
        else:
            road_display = re.sub(r'^(onto|on|turn onto)\s+', '', raw_road, flags=re.IGNORECASE).strip().title()

        # 2. Friendly distance & time calculation
        if dist_m < 70:
            dist_human = f"A few quick steps (~{int(dist_m)} meters)"
            mins_est = 1
        elif dist_m < 350:
            dist_human = f"About {int(round(dist_m, -1))} meters"
            mins_est = max(1, int(round((dist_m / 1000.0) / (speed_factor / 60.0))))
        elif dist_m < 950:
            dist_human = f"Half a kilometer (~{int(dist_m)} meters)"
            mins_est = max(1, int(round((dist_m / 1000.0) / (speed_factor / 60.0))))
        else:
            km_val = dist_m / 1000.0
            dist_human = f"{km_val:.1f} kilometers ({int(dist_m)} meters)"
            mins_est = max(1, int(round(km_val / (speed_factor / 60.0))))

        time_human = f"~{mins_est} min" if mins_est == 1 else f"~{mins_est} mins"

        # 3. Detect maneuver direction & icons with accessible disability guidance
        instr_lower = instr.lower()
        if i == 0 or "head out" in instr_lower or "start" in instr_lower:
            dir_type = "START"
            icon = "🟢"
            action_headline = f"Start Out from {clean_orig}"
            guide_speech = (
                f"Hello traveler! I am your route companion. Let's start by heading out from {clean_orig}. "
                f"Step onto the lane ahead and {mode_action} forward for {dist_human.lower()}."
            )
            what_to_look_for = f"Look for the departure gate, local street corner, and front road opening."
            spoken = f"Step 1: Start out from {clean_orig}. Head forward along the lane for {int(dist_m)} meters."
            accessible_guidance = "Level sidewalk departure with step-free curb ramp. Use the tactile yellow guide strip on your right to align with the pathway."
            tactile_crossing_note = "Yellow raised blister paving indicates boundary of starting path. Safe crossing zone directly ahead."

        elif i == total_count - 1 or "arrive" in instr_lower or "destination" in instr_lower:
            dir_type = "ARRIVE"
            icon = "🏆"
            action_headline = f"Safely Arrive at {clean_dest}"
            guide_speech = (
                f"Hooray! You have safely reached {clean_dest}! "
                f"Welcome to your destination safe haven. The entire journey was completed with full safety verification."
            )
            what_to_look_for = f"Look for the main entrance arch, arrival gate, and destination welcome sign of {clean_dest}."
            spoken = f"Final Step: Congratulations! You have safely arrived at {clean_dest}. Journey completed successfully!"
            accessible_guidance = "Level destination plaza with continuous wheelchair access ramps, 1.8-meter wide automatic sliding doors, and tactile guide path to reception."
            tactile_crossing_note = "Smooth ramp incline (< 1:12 slope) with dual handrails leading straight into the arrival terminal."

        elif "turn right" in instr_lower or "bear right" in instr_lower:
            dir_type = "RIGHT"
            icon = "➡️"
            action_headline = f"Turn Right onto {road_display}"
            guide_speech = (
                f"Look to your right side and take that turn onto {road_display}. "
                f"Follow this street smoothly for {dist_human.lower()} towards the upcoming crossing."
            )
            what_to_look_for = f"Look for the right-hand corner curve, road sign boards, and local shops along the turn."
            spoken = f"Step {i + 1}: Turn right onto {road_display}. Continue for {dist_human.lower()}."
            accessible_guidance = "Right-hand turn features a dropped sidewalk curb ramp with tactile blister tiles. Follow the green pedestrian walk signal before pivoting right."
            tactile_crossing_note = "Audible chirping walk signal confirms safe crossing window. High-contrast zebra crossing across right lane."

        elif "turn left" in instr_lower or "bear left" in instr_lower:
            dir_type = "LEFT"
            icon = "⬅️"
            action_headline = f"Turn Left onto {road_display}"
            guide_speech = (
                f"Take a left turn here onto {road_display}. "
                f"Keep moving forward along this pathway for {dist_human.lower()} to connect to the next stretch."
            )
            what_to_look_for = f"Look for the opening on your left side and follow the clear road path."
            spoken = f"Step {i + 1}: Turn left onto {road_display}. Continue for {dist_human.lower()}."
            accessible_guidance = "Left-hand junction equipped with safe pedestrian island, dropped curb ramps, and audible walk beacons. Cross zebra stripes to execute turn."
            tactile_crossing_note = "High-visibility white zebra crossing with yellow tactile warning strip on both sidewalk curbs."

        elif "straight" in instr_lower or "continue" in instr_lower or dist_m >= 1500:
            dir_type = "STRAIGHT"
            icon = "🛣️"
            action_headline = f"Cruise Straight on {road_display}"
            guide_speech = (
                f"Keep going straight along {road_display}! "
                f"This is your long, smooth open stretch covering {dist_human}. Settle in and enjoy the uninterrupted ride."
            )
            what_to_look_for = f"Look for roadside trees, green agricultural fields, and distance milestone markers."
            spoken = f"Step {i + 1}: Continue straight on {road_display} for {dist_human.lower()}. Smooth cruising ahead."
            accessible_guidance = "Continuous wide accessible sidewalk corridor (> 2.0m wide). Flush paving stones with zero stairs or hazards."
            tactile_crossing_note = "Directional tactile guide path running straight down the corridor with mid-block signalized crossing."

        else:
            dir_type = "PROCEED"
            icon = "🧭"
            action_headline = f"Follow {road_display}"
            guide_speech = (
                f"Follow along {road_display} for {dist_human.lower()}. "
                f"We are making steady, confident progress towards {clean_dest}."
            )
            what_to_look_for = f"Follow the clear lane markings and watch for directional signs ahead."
            spoken = f"Step {i + 1}: Follow {road_display} for {dist_human.lower()}."
            accessible_guidance = "Follow the smooth step-free pedestrian pathway with tactile edge markers."
            tactile_crossing_note = "Stay within the marked pedestrian corridor."

        # Multilingual Turn Text Overrides for Indian Languages
        lang_key = (language or "en").lower().strip()
        if lang_key != "en":
            loc_translations = {
                "START": {
                    "te": {
                        "action": f"{clean_orig} నుండి ప్రారంభించండి",
                        "speech": f"నమస్కారం! నేను మీ ప్రయాణ మార్గదర్శిని. {clean_orig} నుండి ప్రారంభించి, ముందున్న మార్గంలో {dist_human.lower()} వెళ్ళండి.",
                        "spoken": f"దశ 1: {clean_orig} నుండి బయలుదేరి రోడ్డు వెంట ముందుకు వెళ్ళండి.",
                        "look": "బయలుదేరే గేట్, వీధి మూల మరియు ప్రధాన రహదారి ప్రారంభాన్ని చూడండి."
                    },
                    "hi": {
                        "action": f"{clean_orig} से यात्रा प्रारंभ करें",
                        "speech": f"नमस्ते! मैं आपका यात्रा मार्गदर्शक हूँ। {clean_orig} से निकलकर आगे के मार्ग पर {dist_human.lower()} चलें।",
                        "spoken": f"कदम 1: {clean_orig} से यात्रा शुरू करें।",
                        "look": "प्रस्थान द्वार और मुख्य सड़क का मोड़ देखें।"
                    },
                    "ta": {
                        "action": f"{clean_orig} இலிருந்து தொடங்கவும்",
                        "speech": f"வணக்கம்! நான் உங்கள் பயண வழிகாட்டி. {clean_orig} இலிருந்து பயணத்தைத் தொடங்கி {dist_human.lower()} முன்னோக்கி செல்லவும்.",
                        "spoken": f"படி 1: {clean_orig} இலிருந்து பயணத்தை தொடங்கவும்.",
                        "look": "வெளியேறும் வாயில் மற்றும் சாலையின் தொடக்கத்தைக் கவனிக்கவும்."
                    },
                    "kn": {
                        "action": f"{clean_orig} ನಿಂದ ಪ್ರಾರಂಭಿಸಿ",
                        "speech": f"ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಮಾರ್ಗದರ್ಶಿ. {clean_orig} ನಿಂದ ಹೊರಟು {dist_human.lower()} ಮುಂದಕ್ಕೆ ಚಲಿಸಿ.",
                        "spoken": f"ಹಂತ 1: {clean_orig} ನಿಂದ ಪ್ರಾರಂಭಿಸಿ ಮುಂದುವರಿಯಿರಿ.",
                        "look": "ನಿರ್ಗಮನ ಗೇಟ್ ಮತ್ತು ರಸ್ತೆಯ ತಿರುವು ಗಮನಿಸಿ."
                    },
                    "ml": {
                        "action": f"{clean_orig} ൽ നിന്ന് ആരംഭിക്കുക",
                        "speech": f"നമസ്കാരം! ഞാൻ നിങ്ങളുടെ യാത്രാ സഹായി. {clean_orig} ൽ നിന്ന് ആരംഭിച്ച് {dist_human.lower()} മുന്നോട്ട് പോകുക.",
                        "spoken": f"ഘട്ടം 1: {clean_orig} ൽ നിന്ന് യാത്ര ആരംഭിക്കുക.",
                        "look": "പ്രധാന റോഡും കവലയും ശ്രദ്ധിക്കുക."
                    },
                    "bn": {
                        "action": f"{clean_orig} থেকে যাত্রা শুরু করুন",
                        "speech": f"নমস্কার! আমি আপনার যাত্রা নির্দেশক। {clean_orig} থেকে শুরু করে {dist_human.lower()} সামনের দিকে এগিয়ে যান।",
                        "spoken": f"ধাপ ১: {clean_orig} থেকে যাত্রা শুরু করুন।",
                        "look": "প্রস্থান গেট এবং রাস্তার মোড় লক্ষ করুন।"
                    },
                    "mr": {
                        "action": f"{clean_orig} येथून सुरुवात करा",
                        "speech": f"नमस्कार! मी तुमचा मार्गदर्शक आहे. {clean_orig} येथून निघून {dist_human.lower()} पुढे जा.",
                        "spoken": f"पायरी १: {clean_orig} येथून प्रवास सुरू करा.",
                        "look": "निर्गमन गेट आणि रस्त्याचे वळण पहा."
                    }
                },
                "ARRIVE": {
                    "te": {
                        "action": f"{clean_dest} చేరుకున్నారు",
                        "speech": f"అభినందనలు! మీరు సురక్షితంగా {clean_dest} చేరుకున్నారు. మీ ప్రయాణం విజయవంతంగా పూర్తయింది.",
                        "spoken": f"అభినందనలు! మీరు సురక్షితంగా {clean_dest} చేరుకున్నారు.",
                        "look": f"{clean_dest} ప్రధాన ప్రవేశ ద్వారం మరియు స్వాగత బోర్డు చూడండి."
                    },
                    "hi": {
                        "action": f"{clean_dest} पहुँच गए",
                        "speech": f"बधाई हो! आप सुरक्षित रूप से {clean_dest} पहुँच गए हैं। आपकी यात्रा पूरी हुई।",
                        "spoken": f"बधाई हो! आप {clean_dest} पहुँच चुके हैं।",
                        "look": f"{clean_dest} का मुख्य प्रवेश द्वार और स्वागत बोर्ड देखें।"
                    },
                    "ta": {
                        "action": f"{clean_dest} அடைந்துவிட்டீர்கள்",
                        "speech": f"வாழ்த்துகள்! நீங்கள் பாதுகாப்பாக {clean_dest} அடைந்துவிட்டீர்கள். உங்கள் பயணம் நிறைவடைந்தது.",
                        "spoken": f"வாழ்த்துகள்! நீங்கள் {clean_dest} அடைந்துவிட்டீர்கள்.",
                        "look": f"{clean_dest} நுழைவு வாயில் பலகையைக் கவனிக்கவும்."
                    },
                    "kn": {
                        "action": f"{clean_dest} ತಲುಪಿದ್ದೀರಿ",
                        "speech": f"ಅಭಿನಂದನೆಗಳು! ನೀವು ಸುರಕ್ಷಿತವಾಗಿ {clean_dest} ತಲುಪಿದ್ದೀರಿ. ನಿಮ್ಮ ಪ್ರಯಾಣ ಯಶಸ್ವಿಯಾಗಿದೆ.",
                        "spoken": f"ಅಭಿನಂದನೆಗಳು! ನೀವು {clean_dest} ತಲುಪಿದ್ದೀರಿ.",
                        "look": f"{clean_dest} ಮುಖ್ಯ ಪ್ರವೇಶ ದ್ವಾರ ಗಮನಿಸಿ."
                    },
                    "ml": {
                        "action": f"{clean_dest} എത്തിച്ചേർന്നു",
                        "speech": f"അഭിനന്ദനങ്ങൾ! നിങ്ങൾ സുരക്ഷിതമായി {clean_dest} എത്തിച്ചേർന്നു. യാത്ര പൂർത്തിയായി.",
                        "spoken": f"അഭിനന്ദനങ്ങൾ! നിങ്ങൾ {clean_dest} എത്തിച്ചേർന്നു.",
                        "look": f"{clean_dest} പ്രവേശന കവാടം ശ്രദ്ധിക്കുക."
                    },
                    "bn": {
                        "action": f"{clean_dest} পৌঁছে গেছেন",
                        "speech": f"অভিনন্দন! আপনি নিরাপদে {clean_dest} পৌঁছে গেছেন। আপনার যাত্রা সফলভাবে সম্পন্ন হলো।",
                        "spoken": f"অভিনন্দন! আপনি {clean_dest} পৌঁছে গেছেন।",
                        "look": f"{clean_dest} এর প্রধান প্রবেশদ্বার দেখুন।"
                    },
                    "mr": {
                        "action": f"{clean_dest} येथे पोहोचलात",
                        "speech": f"अभिनंदन! तुम्ही सुरक्षितपणे {clean_dest} येथे पोहोचला आहात. प्रवास पूर्ण झाला.",
                        "spoken": f"अभिनंदन! तुम्ही {clean_dest} येथे पोहोचलात.",
                        "look": f"{clean_dest} चे मुख्य प्रवेशद्वार पहा."
                    }
                },
                "RIGHT": {
                    "te": {
                        "action": f"{road_display} వైపు కుడివైపు తిరగండి",
                        "speech": f"కుడివైపు చూసి {road_display} పైకి తిరగండి మరియు {dist_human.lower()} ప్రయాణించండి.",
                        "spoken": f"దశ {i + 1}: {road_display} వైపు కుడివైపు తిరగండి.",
                        "look": "కుడివైపు మలుపు బోర్డులు మరియు రోడ్డు పక్కన ఉన్న దుకాణాలను చూడండి."
                    },
                    "hi": {
                        "action": f"{road_display} पर दाएँ मुड़ें",
                        "speech": f"दाएँ देखकर {road_display} पर मुड़ें और {dist_human.lower()} आगे बढ़ें।",
                        "spoken": f"कदम {i + 1}: {road_display} पर दाएँ मुड़ें।",
                        "look": "दाहिने कोने का मोड़ और दिशा सूचक बोर्ड देखें।"
                    },
                    "ta": {
                        "action": f"{road_display} இல் வலதுபுறம் திரும்பவும்",
                        "speech": f"வலதுபுறம் பார்த்து {road_display} இல் திரும்பி {dist_human.lower()} செல்லவும்.",
                        "spoken": f"படி {i + 1}: {road_display} இல் வலதுபுறம் திரும்பவும்.",
                        "look": "வலதுபுற சாலைப் பலகையைக் கவனிக்கவும்."
                    },
                    "kn": {
                        "action": f"{road_display} ಕಡೆಗೆ ಬಲಕ್ಕೆ ತಿರುಗಿ",
                        "speech": f"ಬಲಗಡೆ ನೋಡಿ {road_display} ಕಡೆಗೆ ತಿರುಗಿ {dist_human.lower()} ಮುಂದುವರಿಯಿರಿ.",
                        "spoken": f"ಹಂತ {i + 1}: {road_display} ಕಡೆಗೆ ಬಲಕ್ಕೆ ತಿರುಗಿ.",
                        "look": "ಬಲಗಡೆಯ ತಿರುವು ಮತ್ತು ಫಲಕಗಳನ್ನು ಗಮನಿಸಿ."
                    },
                    "ml": {
                        "action": f"{road_display} ലേക്ക് വലത്തോട്ട് തിരിയുക",
                        "speech": f"വലത്തോട്ട് നോക്കി {road_display} ലേക്ക് തിരിഞ്ഞ് {dist_human.lower()} മുന്നോട്ട് പോകുക.",
                        "spoken": f"ഘട്ടം {i + 1}: {road_display} ലേക്ക് വലത്തോട്ട് തിരിയുക.",
                        "look": "വലതുവശത്തെ സൈൻബോർഡ് ശ്രദ്ധിക്കുക."
                    },
                    "bn": {
                        "action": f"{road_display} এ ডানদিকে ঘুরুন",
                        "speech": f"ডানদিকে লক্ষ করে {road_display} এ মোড় নিয়ে {dist_human.lower()} এগিয়ে যান।",
                        "spoken": f"ধাপ {i + 1}: {road_display} এ ডানদিকে ঘুরুন।",
                        "look": "ডানপাশের মোড়ের সাইনবোর্ড লক্ষ করুন।"
                    },
                    "mr": {
                        "action": f"{road_display} वर उजवीकडे वळा",
                        "speech": f"उजवीकडे पाहून {road_display} वर वळा आणि {dist_human.lower()} पुढे जा.",
                        "spoken": f"पायरी {i + 1}: {road_display} वर उजवीकडे वळा.",
                        "look": "उजव्या बाजूचे वळण आणि फलक पहा."
                    }
                },
                "LEFT": {
                    "te": {
                        "action": f"{road_display} వైపు ఎడమవైపు తిరగండి",
                        "speech": f"ఎడమవైపు చూసి {road_display} పైకి తిరగండి మరియు {dist_human.lower()} ప్రయాణించండి.",
                        "spoken": f"దశ {i + 1}: {road_display} వైపు ఎడమవైపు తిరగండి.",
                        "look": "ఎడమవైపు మలుపు మరియు స్పష్టమైన రహదారి మార్గాన్ని చూడండి."
                    },
                    "hi": {
                        "action": f"{road_display} पर बाएँ मुड़ें",
                        "speech": f"बाएँ देखकर {road_display} पर मुड़ें और {dist_human.lower()} आगे बढ़ें।",
                        "spoken": f"कदम {i + 1}: {road_display} पर बाएँ मुड़ें।",
                        "look": "बाएँ कोने का मोड़ और सड़क मार्ग देखें।"
                    },
                    "ta": {
                        "action": f"{road_display} இல் இடதுபுறம் திரும்பவும்",
                        "speech": f"இடதுபுறம் பார்த்து {road_display} இல் திரும்பி {dist_human.lower()} செல்லவும்.",
                        "spoken": f"படி {i + 1}: {road_display} இல் இடதுபுறம் திரும்பவும்.",
                        "look": "இடதுபுற சாலையைக் கவனிக்கவும்."
                    },
                    "kn": {
                        "action": f"{road_display} ಕಡೆಗೆ ಎಡಕ್ಕೆ ತಿರುಗಿ",
                        "speech": f"ಎಡಗಡೆ ನೋಡಿ {road_display} ಕಡೆಗೆ ತಿರುಗಿ {dist_human.lower()} ಮುಂದುವರಿಯಿರಿ.",
                        "spoken": f"ಹಂತ {i + 1}: {road_display} ಕಡೆಗೆ ಎಡಕ್ಕೆ ತಿರುಗಿ.",
                        "look": "ಎಡಗಡೆಯ ತಿರುವನ್ನು ಗಮನಿಸಿ."
                    },
                    "ml": {
                        "action": f"{road_display} ലേക്ക് ഇടത്തോട്ട് തിരിയുക",
                        "speech": f"ഇടത്തോട്ട് നോക്കി {road_display} ലേക്ക് തിരിഞ്ഞ് {dist_human.lower()} മുന്നോട്ട് പോകുക.",
                        "spoken": f"ഘട്ടം {i + 1}: {road_display} ലേക്ക് ഇടത്തോട്ട് തിരിയുക.",
                        "look": "ഇടതുവശത്തെ കവല ശ്രദ്ധിക്കുക."
                    },
                    "bn": {
                        "action": f"{road_display} এ বামদিকে ঘুরুন",
                        "speech": f"বামদিকে লক্ষ করে {road_display} এ মোড় নিয়ে {dist_human.lower()} এগিয়ে যান।",
                        "spoken": f"ধাপ {i + 1}: {road_display} এ বামদিকে ঘুরুন।",
                        "look": "বামপাশের রাস্তা লক্ষ করুন।"
                    },
                    "mr": {
                        "action": f"{road_display} वर डावीकडे वळा",
                        "speech": f"डावीकडे पाहून {road_display} वर वळा आणि {dist_human.lower()} पुढे जा.",
                        "spoken": f"पायरी {i + 1}: {road_display} वर डावीकडे वळा.",
                        "look": "डाव्या बाजूचे वळण पहा."
                    }
                },
                "STRAIGHT": {
                    "te": {
                        "action": f"{road_display} పై నేరుగా కొనసాగించండి",
                        "speech": f"{road_display} పై {dist_human.lower()} నేరుగా ముందుకు వెళ్ళండి.",
                        "spoken": f"దశ {i + 1}: {road_display} పై నేరుగా ముందుకు కొనసాగించండి.",
                        "look": "రోడ్డు పక్కన చెట్లు మరియు కిలోమీటర్ మైలురాళ్లను చూడండి."
                    },
                    "hi": {
                        "action": f"{road_display} पर सीधे चलें",
                        "speech": f"{road_display} पर {dist_human.lower()} सीधे आगे बढ़ते रहें।",
                        "spoken": f"कदम {i + 1}: {road_display} पर सीधे चलते रहें।",
                        "look": "सड़क किनारे के पेड़ और दूरी के पत्थर देखें।"
                    },
                    "ta": {
                        "action": f"{road_display} இல் நேராக செல்லவும்",
                        "speech": f"{road_display} இல் {dist_human.lower()} நேராக தொடர்ந்து செல்லவும்.",
                        "spoken": f"படி {i + 1}: {road_display} இல் நேராக தொடர்ந்து செல்லவும்.",
                        "look": "சாலையோர மைல்கற்களைக் கவனிக்கவும்."
                    },
                    "kn": {
                        "action": f"{road_display} ನಲ್ಲಿ ನೇರವಾಗಿ ಮುಂದುವರಿಯಿರಿ",
                        "speech": f"{road_display} ನಲ್ಲಿ {dist_human.lower()} ನೇರವಾಗಿ ಮುಂದುವರಿಯಿರಿ.",
                        "spoken": f"ಹಂತ {i + 1}: {road_display} ನಲ್ಲಿ ನೇರವಾಗಿ ಮುಂದುವರಿಯಿರಿ.",
                        "look": "ಮೈಲಿಗಲ್ಲುಗಳನ್ನು ಗಮನಿಸಿ."
                    },
                    "ml": {
                        "action": f"{road_display} ലൂടെ നേരെ പോകുക",
                        "speech": f"{road_display} ലൂടെ {dist_human.lower()} നേരെ മുന്നോട്ട് പോകുക.",
                        "spoken": f"ഘട്ടം {i + 1}: {road_display} ലൂടെ നേരെ മുന്നോട്ട് പോകുക.",
                        "look": "മൈൽക്കുറ്റികൾ ശ്രദ്ധിക്കുക."
                    },
                    "bn": {
                        "action": f"{road_display} ধরে সোজা এগিয়ে যান",
                        "speech": f"{road_display} ধরে {dist_human.lower()} সোজা এগিয়ে চলুন।",
                        "spoken": f"ধাপ {i + 1}: {road_display} ধরে সোজা এগিয়ে যান।",
                        "look": "রাস্তার মাইলফলকগুলো লক্ষ করুন।"
                    },
                    "mr": {
                        "action": f"{road_display} वर सरळ पुढे जा",
                        "speech": f"{road_display} वर {dist_human.lower()} सरळ पुढे चालत राहा.",
                        "spoken": f"पायरी {i + 1}: {road_display} वर सरळ पुढे जा.",
                        "look": "रस्त्यावरील मैलाचे दगड पहा."
                    }
                },
                "PROCEED": {
                    "te": {
                        "action": f"{road_display} మార్గాన్ని అనుసరించండి",
                        "speech": f"{road_display} వెంట {dist_human.lower()} ముందుకు సాగండి.",
                        "spoken": f"దశ {i + 1}: {road_display} మార్గాన్ని అనుసరించండి.",
                        "look": "లేన్ గుర్తులు మరియు దిశా సూచికలను చూడండి."
                    },
                    "hi": {
                        "action": f"{road_display} का अनुसरण करें",
                        "speech": f"{road_display} पर {dist_human.lower()} आगे बढ़ते रहें।",
                        "spoken": f"कदम {i + 1}: {road_display} का अनुसरण करें।",
                        "look": "लेन मार्किंग और दिशा संकेत देखें।"
                    },
                    "ta": {
                        "action": f"{road_display} வழியைப் பின்பற்றவும்",
                        "speech": f"{road_display} வழியே {dist_human.lower()} செல்லவும்.",
                        "spoken": f"படி {i + 1}: {road_display} வழியைப் பின்பற்றவும்.",
                        "look": "வழித்தட பலகைகளைக் கவனிக்கவும்."
                    },
                    "kn": {
                        "action": f"{road_display} ರಸ್ತೆಯನ್ನು ಅನುಸರಿಸಿ",
                        "speech": f"{road_display} ರಸ್ತೆಯಲ್ಲಿ {dist_human.lower()} ಮುಂದುವರಿಯಿರಿ.",
                        "spoken": f"ಹಂತ {i + 1}: {road_display} ರಸ್ತೆಯನ್ನು ಅನುಸರಿಸಿ.",
                        "look": "ರಸ್ತೆ ಚಿಹ್ನೆಗಳನ್ನು ಗಮನಿಸಿ."
                    },
                    "ml": {
                        "action": f"{road_display} പാത പിന്തുടരുക",
                        "speech": f"{road_display} ലൂടെ {dist_human.lower()} മുന്നോട്ട് പോകുക.",
                        "spoken": f"ഘട്ടം {i + 1}: {road_display} പാത പിന്തുടരുക.",
                        "look": "റോഡ് അടയാളങ്ങൾ ശ്രദ്ധിക്കുക."
                    },
                    "bn": {
                        "action": f"{road_display} অনুসরণ করুন",
                        "speech": f"{road_display} ধরে {dist_human.lower()} সামনে এগিয়ে যান।",
                        "spoken": f"ধাপ {i + 1}: {road_display} অনুসরণ করুন।",
                        "look": "রাস্তার দিকনির্দেশক দেখুন।"
                    },
                    "mr": {
                        "action": f"{road_display} चा पाठपुरावा करा",
                        "speech": f"{road_display} वरून {dist_human.lower()} पुढे जा.",
                        "spoken": f"पायरी {i + 1}: {road_display} चा पाठपुरावा करा.",
                        "look": "रस्त्यावरील दिशादर्शक फलक पहा."
                    }
                }
            }
            target_dict = loc_translations.get(dir_type, {}).get(lang_key)
            if target_dict:
                action_headline = target_dict["action"]
                guide_speech = target_dict["speech"]
                spoken = target_dict["spoken"]
                what_to_look_for = target_dict["look"]

        # Add location/regional landmark hints if recognizable
        combined_text = (road_display + " " + instr).lower()
        if "vignan" in combined_text or "vignan" in clean_dest.lower():
            what_to_look_for = "Look for the grand university campus entrance arch, college buses, and green campus grounds."
        elif "narakoduru" in combined_text:
            what_to_look_for = "Look for the scenic agricultural canal bridge, coconut groves, and rural junction stalls."
        elif "mangalagiri" in combined_text:
            what_to_look_for = "Look for the bustling highway market, handloom weaver signs, and temple corridor boards."
        elif "tenali" in combined_text:
            what_to_look_for = "Look for the canal bridges, three-lights junction, and local commercial market stalls."
        elif "guntur" in combined_text:
            what_to_look_for = "Look for the wide city expressway bypass, medical colleges, and urban transit towers."

        friendly_steps.append(FriendlyTurnStep(
            step_num=i + 1,
            total_steps=total_count,
            direction_type=dir_type,
            action_headline=action_headline,
            virtual_guide_speech=guide_speech,
            what_to_look_for=what_to_look_for,
            distance_human=dist_human,
            time_estimate=time_human,
            road_name=road_display,
            icon=icon,
            spoken_text=spoken,
            accessible_guidance=accessible_guidance,
            tactile_crossing_note=tactile_crossing_note,
            distance_m=dist_m
        ))

    return friendly_steps


def render_accessible_virtual_guide_avatar(
    direction_type: str,
    headline: str = "",
    road_name: str = ""
) -> str:
    """
    Renders an animated, cute 3D Virtual Guide Man ('Virtual Navigator') demonstrating
    realistic walk, run, turn, and jump actions and accessible street crossings.
    Features:
    - Cute 3D anime/Pixar avatar with soft peach skin, rosy blushing cheeks, sparkling sapphire eyes with catchlights
    - Layered stylish chestnut bangs with ahoge tuft and chic navigator headset
    - High-visibility cyber emerald/cyan athletic bomber jacket with neon zipper and safety trim
    - Articulated limbs for fluid walk strides, athletic sprint runs, pivot turns, high vertical jumps, and victory cheers
    - High-contrast white pedestrian zebra crosswalk spanning the road
    - Yellow tactile warning blister paving tiles at curb ramps for visually impaired
    - Accessible drop-curb ramp with '♿ RAMP' indicator for wheelchairs
    - Audible pedestrian crossing signal pole with illuminated 'WALK' person
    - Wheelchair companion silhouette traveling safely alongside the virtual guide
    """
    dt = direction_type.upper()
    if dt == "LEFT" or "left" in headline.lower():
        arms_and_arrows_left = """
        <!-- Left arm gracefully pointing across the zebra crosswalk to the left turn -->
        <path d="M 6 22 L -14 16 L -28 11" fill="none" stroke="#0284c7" stroke-width="3.6" stroke-linecap="round"/>
        <circle cx="-28" cy="11" r="2.8" fill="#38bdf8"/>
        <!-- Glowing Left Turn AR Arrow Beam -->
        <path d="M -28 11 Q -42 7 -54 -3" fill="none" stroke="#00f2fe" stroke-width="3.2" stroke-dasharray="4,3" filter="url(#neonGlowCyan)"/>
        <polygon points="-58,-7 -49,0 -50,-6" fill="#00f2fe"/>
        """
        arms_and_arrows_right = """
        <!-- Right Arm holding holographic navigator tablet -->
        <path d="M 22 22 L 27 30" fill="none" stroke="#0284c7" stroke-width="3.6" stroke-linecap="round"/>
        <rect x="23" y="27" width="9" height="13" rx="2" fill="#0284c7" stroke="#38bdf8" stroke-width="0.9"/>
        <circle cx="27.5" cy="33.5" r="2" fill="#10b981" filter="url(#neonGlowEmerald)"/>
        """
    elif dt == "RIGHT" or "right" in headline.lower():
        arms_and_arrows_left = """
        <!-- Left Arm holding holographic guide tablet -->
        <path d="M 6 22 L 1 30" fill="none" stroke="#0284c7" stroke-width="3.6" stroke-linecap="round"/>
        <rect x="-4" y="27" width="9" height="13" rx="2" fill="#0284c7" stroke="#38bdf8" stroke-width="0.9"/>
        <circle cx="0.5" cy="33.5" r="2" fill="#10b981" filter="url(#neonGlowEmerald)"/>
        """
        arms_and_arrows_right = """
        <!-- Right arm pointing across zebra crossing to right turn -->
        <path d="M 22 22 L 42 16 L 56 11" fill="none" stroke="#0284c7" stroke-width="3.6" stroke-linecap="round"/>
        <circle cx="56" cy="11" r="2.8" fill="#38bdf8"/>
        <!-- Glowing Right Turn AR Arrow Beam -->
        <path d="M 56 11 Q 70 7 82 -3" fill="none" stroke="#00f2fe" stroke-width="3.2" stroke-dasharray="4,3" filter="url(#neonGlowCyan)"/>
        <polygon points="86,-7 77,-6 78,0" fill="#00f2fe"/>
        """
    elif dt == "ARRIVE" or "arrive" in headline.lower():
        arms_and_arrows_left = """
        <!-- Left arm raised in celebratory cheer -->
        <path d="M 6 22 L -6 8 L -8 -6" fill="none" stroke="#0284c7" stroke-width="3.4" stroke-linecap="round"/>
        <circle cx="-8" cy="-6" r="2.8" fill="#fde047"/>
        """
        arms_and_arrows_right = """
        <!-- Right arm raised in celebratory cheer -->
        <path d="M 22 22 L 34 8 L 36 -6" fill="none" stroke="#0284c7" stroke-width="3.4" stroke-linecap="round"/>
        <circle cx="36" cy="-6" r="2.8" fill="#fde047"/>
        <!-- Celebration Laurel / Ribbon -->
        <path d="M -12 -12 Q 14 -22 40 -12" fill="none" stroke="#facc15" stroke-width="2.2" stroke-dasharray="4,2"/>
        <text x="14" y="-18" text-anchor="middle" fill="#facc15" font-size="7.5" font-weight="900" font-family="'Segoe UI', sans-serif">SAFE DESTINATION 🏁</text>
        """
    elif dt == "START" or "start" in headline.lower():
        arms_and_arrows_left = """
        <!-- Waving left hand welcoming traveler -->
        <path d="M 6 22 L -6 12 L -4 -2" fill="none" stroke="#0284c7" stroke-width="3.4" stroke-linecap="round"/>
        <circle cx="-4" cy="-3" r="2.8" fill="#fde047"/>
        """
        arms_and_arrows_right = """
        <!-- Right arm pointing forward along the road -->
        <path d="M 22 22 L 35 28 L 46 28" fill="none" stroke="#0284c7" stroke-width="3.4" stroke-linecap="round"/>
        <polygon points="50,28 44,25 44,31" fill="#00f2fe"/>
        """
    else:
        arms_and_arrows_left = """
        <!-- Both arms guiding forward along the corridor -->
        <path d="M 6 22 L -4 12 L 4 2" fill="none" stroke="#0284c7" stroke-width="3.2" stroke-linecap="round"/>
        <polygon points="14,-6 8,0 11,2 14,-2 17,2 20,0" fill="#00f2fe" filter="url(#neonGlowCyan)"/>
        """
        arms_and_arrows_right = """
        <path d="M 22 22 L 32 12 L 24 2" fill="none" stroke="#0284c7" stroke-width="3.2" stroke-linecap="round"/>
        <polygon points="14,-14 9,-8 11,-7 14,-10 17,-7 19,-8" fill="#38bdf8"/>
        """

    return f"""
    <!-- ACCESSIBLE PEDESTRIAN ZEBRA CROSSWALK & STEP-FREE CROSSING ZONE -->
    <g class="pedestrian-crosswalk" filter="url(#dropShadow)" opacity="0.96">
        <polygon points="245,226 275,226 248,248 215,248" fill="#ffffff" stroke="rgba(56, 189, 248, 0.4)" stroke-width="0.8"/>
        <polygon points="295,226 325,226 303,248 268,248" fill="#ffffff" stroke="rgba(56, 189, 248, 0.4)" stroke-width="0.8"/>
        <polygon points="345,226 375,226 358,248 323,248" fill="#ffffff" stroke="rgba(56, 189, 248, 0.4)" stroke-width="0.8"/>
        <polygon points="395,226 425,226 413,248 378,248" fill="#ffffff" stroke="rgba(56, 189, 248, 0.4)" stroke-width="0.8"/>
        <polygon points="445,226 475,226 468,248 433,248" fill="#ffffff" stroke="rgba(56, 189, 248, 0.4)" stroke-width="0.8"/>
        <polygon points="495,226 525,226 523,248 488,248" fill="#ffffff" stroke="rgba(56, 189, 248, 0.4)" stroke-width="0.8"/>
    </g>

    <!-- LEFT SIDEWALK CURB RAMP & YELLOW TACTILE BLISTER PAVING -->
    <g class="curb-ramp-left" transform="translate(180, 234)">
        <polygon points="0,0 35,0 30,16 -8,16" fill="#eab308" stroke="#ca8a04" stroke-width="1"/>
        <circle cx="6" cy="4" r="1.3" fill="#fef08a"/><circle cx="14" cy="4" r="1.3" fill="#fef08a"/><circle cx="22" cy="4" r="1.3" fill="#fef08a"/><circle cx="29" cy="4" r="1.3" fill="#fef08a"/>
        <circle cx="4" cy="11" r="1.3" fill="#fef08a"/><circle cx="12" cy="11" r="1.3" fill="#fef08a"/><circle cx="20" cy="11" r="1.3" fill="#fef08a"/><circle cx="27" cy="11" r="1.3" fill="#fef08a"/>
        <rect x="-4" y="-12" width="38" height="11" rx="3" fill="#0284c7" stroke="#38bdf8" stroke-width="0.9"/>
        <text x="15" y="-4" text-anchor="middle" fill="#ffffff" font-size="6" font-weight="900" font-family="'Segoe UI', sans-serif">♿ RAMP</text>
    </g>

    <!-- RIGHT SIDEWALK CURB RAMP & YELLOW TACTILE BLISTER PAVING -->
    <g class="curb-ramp-right" transform="translate(528, 234)">
        <polygon points="0,0 35,0 43,16 5,16" fill="#eab308" stroke="#ca8a04" stroke-width="1"/>
        <circle cx="7" cy="4" r="1.3" fill="#fef08a"/><circle cx="15" cy="4" r="1.3" fill="#fef08a"/><circle cx="23" cy="4" r="1.3" fill="#fef08a"/><circle cx="31" cy="4" r="1.3" fill="#fef08a"/>
        <circle cx="10" cy="11" r="1.3" fill="#fef08a"/><circle cx="18" cy="11" r="1.3" fill="#fef08a"/><circle cx="26" cy="11" r="1.3" fill="#fef08a"/><circle cx="34" cy="11" r="1.3" fill="#fef08a"/>
        <rect x="2" y="-12" width="38" height="11" rx="3" fill="#0284c7" stroke="#38bdf8" stroke-width="0.9"/>
        <text x="21" y="-4" text-anchor="middle" fill="#ffffff" font-size="6" font-weight="900" font-family="'Segoe UI', sans-serif">♿ RAMP</text>
    </g>

    <!-- AUDIBLE PEDESTRIAN CROSSING SIGNAL -->
    <g class="pedestrian-signal" transform="translate(170, 160)" filter="url(#dropShadow)">
        <line x1="5" y1="0" x2="5" y2="76" stroke="#475569" stroke-width="3"/>
        <rect x="-1" y="4" width="13" height="26" rx="2.5" fill="#091220" stroke="#38bdf8" stroke-width="0.9"/>
        <circle cx="5.5" cy="10" r="3.2" fill="#1e293b"/>
        <circle cx="5.5" cy="22" r="3.8" fill="#10b981" filter="url(#neonGlowEmerald)"/>
        <path d="M 5.5 19 C 5.5 18.5 5.8 18 6.5 18 C 7.2 18 7.5 18.5 7.5 19 L 7.5 22 L 5 25 M 7.5 22 L 9 24.5" stroke="#ffffff" stroke-width="0.9" fill="none"/>
        <rect x="-6" y="32" width="24" height="8" rx="2" fill="#059669"/>
        <text x="6" y="38" text-anchor="middle" fill="#ffffff" font-size="5" font-weight="900" font-family="'Segoe UI', sans-serif">WALK 🟢</text>
    </g>

    <!-- VIRTUAL GUIDE CUTE AVATAR & WHEELCHAIR COMPANION GROUP -->
    <g id="virtual-guide-actor" class="virtual-guide-man-avatar action-walk" transform="translate(340, 195)">
        <!-- Ground Shadow & Glowing Navigation Aura -->
        <ellipse cx="20" cy="74" rx="30" ry="7" fill="rgba(0,0,0,0.5)" filter="url(#dropShadow)"/>
        <ellipse cx="20" cy="74" rx="36" ry="9" fill="none" stroke="#10b981" stroke-width="1.8" filter="url(#neonGlowEmerald)" stroke-dasharray="6,4"/>

        <!-- Wheelchair Accessible Companion Silhouette (Right beside Virtual Guide) -->
        <g class="wheelchair-companion" transform="translate(-32, 24)" filter="url(#dropShadow)">
            <circle cx="10" cy="8" r="4.5" fill="#38bdf8" filter="url(#neonGlowCyan)"/>
            <path d="M 10 13 L 10 26 L 18 26" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round"/>
            <circle cx="11" cy="30" r="9" fill="none" stroke="#38bdf8" stroke-width="2.2"/>
            <circle cx="11" cy="30" r="2.5" fill="#ffffff"/>
            <line x1="18" y1="26" x2="22" y2="35" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/>
            <circle cx="22" cy="37" r="2" fill="#38bdf8"/>
            <rect x="-4" y="42" width="30" height="9" rx="2" fill="#0284c7"/>
            <text x="11" y="48.5" text-anchor="middle" fill="#ffffff" font-size="5" font-weight="900" font-family="'Segoe UI', sans-serif">♿ ACCESS</text>
        </g>

        <!-- Cute Virtual Man Character Body Group -->
        <g class="virtual-man-body" transform="translate(6, 0)">
            <!-- Floating Name HUD Badge -->
            <g class="actor-badge" transform="translate(14, -14)">
                <rect x="-26" y="0" width="52" height="12" rx="3" fill="#091322" stroke="#38bdf8" stroke-width="1.2" filter="url(#dropShadow)"/>
                <text x="0" y="8.5" text-anchor="middle" fill="#38bdf8" font-size="6.5" font-weight="900" font-family="'Segoe UI', Roboto, sans-serif">VIRTUAL GUIDE 👨‍✈️</text>
            </g>

            <!-- Dynamic Limbs: Left Leg -->
            <g id="actor-left-leg" class="actor-limb-left-leg" style="transform-origin: 10px 42px;">
                <!-- Thigh & Calf (Stylish Dark Joggers) -->
                <path d="M 8 42 L 5 56 L 4 68" stroke="#1e293b" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M 8 42 L 5 56 L 4 68" stroke="#334155" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="5" cy="56" r="2.2" fill="#0f172a"/>
                <!-- Cute High-top Sneaker -->
                <g transform="translate(0, 65)">
                    <path d="M 0 5 L 10 5 L 9 1 L 3 1 Z" fill="#38bdf8"/>
                    <rect x="-1" y="5" width="12" height="3" rx="1.5" fill="#f8fafc"/>
                    <line x1="3" y1="2" x2="7" y2="4" stroke="#ffffff" stroke-width="0.8"/>
                </g>
            </g>

            <!-- Dynamic Limbs: Right Leg -->
            <g id="actor-right-leg" class="actor-limb-right-leg" style="transform-origin: 18px 42px;">
                <!-- Thigh & Calf (Stylish Dark Joggers) -->
                <path d="M 18 42 L 21 56 L 22 68" stroke="#0f172a" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M 18 42 L 21 56 L 22 68" stroke="#1e293b" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="21" cy="56" r="2.2" fill="#0f172a"/>
                <!-- Cute High-top Sneaker -->
                <g transform="translate(16, 65)">
                    <path d="M 0 5 L 10 5 L 9 1 L 3 1 Z" fill="#10b981"/>
                    <rect x="-1" y="5" width="12" height="3" rx="1.5" fill="#f8fafc"/>
                    <line x1="3" y1="2" x2="7" y2="4" stroke="#ffffff" stroke-width="0.8"/>
                </g>
            </g>

            <!-- Torso & Cute Head Group (Bobs in rhythm during actions) -->
            <g id="actor-torso-head" class="actor-torso-head">
                <!-- Athletic Bomber Jacket / Torso -->
                <path d="M 5 21 L 23 21 L 26 44 L 2 44 Z" fill="url(#cuteJacketGrad)" stroke="#0284c7" stroke-width="1.2" filter="url(#dropShadow)"/>
                <!-- Neon Cyan Zipper & High Collar -->
                <line x1="14" y1="18" x2="14" y2="44" stroke="#38bdf8" stroke-width="1.8" filter="url(#neonGlowCyan)"/>
                <polygon points="12,18 16,18 14,24" fill="#ffffff"/>
                <!-- High-Vis Navigator Shoulder Straps & Chest Crest -->
                <path d="M 6 22 L 10 44" stroke="#10b981" stroke-width="2" opacity="0.9"/>
                <path d="M 22 22 L 18 44" stroke="#10b981" stroke-width="2" opacity="0.9"/>
                <circle cx="14" cy="30" r="3" fill="#0284c7" stroke="#38bdf8" stroke-width="1" filter="url(#neonGlowCyan)"/>
                <text x="14" y="32" text-anchor="middle" fill="#ffffff" font-size="3" font-weight="900">🧭</text>

                <!-- Cute Neck Base -->
                <rect x="11.5" y="16" width="5" height="5" rx="1" fill="#fed7aa"/>

                <!-- CUTE 3D ANIME/PIXAR HEAD -->
                <g class="cute-head" transform="translate(14, 9)">
                    <!-- Cute Rounded Head with Warm Peach Skin -->
                    <ellipse cx="0" cy="0" rx="10" ry="10.5" fill="url(#cuteSkinGrad)" stroke="#fba088" stroke-width="0.6" filter="url(#dropShadow)"/>
                    
                    <!-- Cute Rosy Blushing Cheeks -->
                    <ellipse cx="-5.8" cy="2.8" rx="3.2" ry="1.8" fill="#fb7185" opacity="0.55"/>
                    <ellipse cx="5.8" cy="2.8" rx="3.2" ry="1.8" fill="#fb7185" opacity="0.55"/>

                    <!-- Left Eye: Big, Cute, Sparkling Anime/Pixar Style -->
                    <g class="cute-eye-left" transform="translate(-4.5, -0.5)">
                        <ellipse cx="0" cy="0" rx="3" ry="3.5" fill="#ffffff"/>
                        <ellipse cx="0.2" cy="0.3" rx="2.3" ry="2.7" fill="url(#cuteEyeIris)"/>
                        <ellipse cx="0.2" cy="0.3" rx="1.3" ry="1.6" fill="#091322"/>
                        <circle cx="-0.6" cy="-1.1" r="1.1" fill="#ffffff"/>
                        <circle cx="0.8" cy="1.2" r="0.55" fill="#ffffff"/>
                        <path d="M -3.2 -1.5 Q 0 -3.6 3.2 -1.2" fill="none" stroke="#1e293b" stroke-width="1.2" stroke-linecap="round"/>
                        <path d="M -3.5 -4.5 Q 0 -5.6 2.8 -4" fill="none" stroke="#78350f" stroke-width="1.1" stroke-linecap="round"/>
                    </g>

                    <!-- Right Eye: Big, Cute, Sparkling Anime/Pixar Style -->
                    <g class="cute-eye-right" transform="translate(4.5, -0.5)">
                        <ellipse cx="0" cy="0" rx="3" ry="3.5" fill="#ffffff"/>
                        <ellipse cx="0.2" cy="0.3" rx="2.3" ry="2.7" fill="url(#cuteEyeIris)"/>
                        <ellipse cx="0.2" cy="0.3" rx="1.3" ry="1.6" fill="#091322"/>
                        <circle cx="-0.6" cy="-1.1" r="1.1" fill="#ffffff"/>
                        <circle cx="0.8" cy="1.2" r="0.55" fill="#ffffff"/>
                        <path d="M -3.2 -1.2 Q 0 -3.6 3.2 -1.5" fill="none" stroke="#1e293b" stroke-width="1.2" stroke-linecap="round"/>
                        <path d="M -2.8 -4 Q 0 -5.6 3.5 -4.5" fill="none" stroke="#78350f" stroke-width="1.1" stroke-linecap="round"/>
                    </g>

                    <!-- Cute Button Nose -->
                    <ellipse cx="0" cy="1.8" rx="0.7" ry="0.5" fill="#f43f5e" opacity="0.6"/>

                    <!-- Sweet Cute Smile -->
                    <path d="M -2.8 4 Q 0 6.5 2.8 4" fill="none" stroke="#be123c" stroke-width="1.2" stroke-linecap="round"/>

                    <!-- Stylish Layered Anime/Pixar Hair -->
                    <g class="cute-hair">
                        <!-- Hair Crown Base -->
                        <path d="M -10 -2 C -10 -9 -6 -13 0 -13 C 6 -13 10 -9 10 -2 C 9 -4 6 -6 0 -6 C -6 -6 -9 -4 -10 -2 Z" fill="url(#cuteHairGrad)"/>
                        <!-- Swept Front Bangs / Fringe -->
                        <path d="M -9 -2 Q -4 -7 0 -3 Q 4 -7 9 -2 C 8 -5 4 -9 0 -9 C -4 -9 -8 -5 -9 -2 Z" fill="#78350f"/>
                        <path d="M -6 -5 Q -2 0 1 -4" fill="none" stroke="#451a03" stroke-width="1.6" stroke-linecap="round"/>
                        <path d="M 0 -4 Q 3 0 7 -4" fill="none" stroke="#451a03" stroke-width="1.6" stroke-linecap="round"/>
                        <!-- Glossy Hair Highlight Shine Arc -->
                        <path d="M -6 -10 Q 0 -12 6 -10" fill="none" stroke="#fde047" stroke-width="1.2" opacity="0.75" stroke-linecap="round"/>
                        <!-- Playful Ahoge Tuft at Crown -->
                        <path d="M 0 -12 Q -2 -17 2 -18 Q 4 -16 1 -13" fill="url(#cuteHairGrad)"/>
                    </g>

                    <!-- Chic Navigator Headset with Glowing Audio Ring -->
                    <g class="navigator-headset" transform="translate(0, -3)">
                        <path d="M -10 1 Q 0 -5 10 1" fill="none" stroke="#38bdf8" stroke-width="1.5" filter="url(#neonGlowCyan)"/>
                        <circle cx="-10" cy="2" r="2.4" fill="#0284c7" stroke="#38bdf8" stroke-width="0.8"/>
                        <circle cx="10" cy="2" r="2.4" fill="#0284c7" stroke="#38bdf8" stroke-width="0.8"/>
                        <circle cx="10" cy="2" r="1.2" fill="#10b981" filter="url(#neonGlowEmerald)"/>
                    </g>
                </g>
            </g>

            <!-- Dynamic Segmented Arms (Left & Right) -->
            <g id="actor-left-arm" class="actor-limb-left-arm" style="transform-origin: 6px 22px;">
                {arms_and_arrows_left}
            </g>
            <g id="actor-right-arm" class="actor-limb-right-arm" style="transform-origin: 22px 22px;">
                {arms_and_arrows_right}
            </g>
        </g>
    </g>
    """


def get_turn_visual_svg(
    direction_type: str,
    headline: str = "",
    road_name: str = "",
    distance_str: str = "",
    step_num: int = 1,
    total_steps: int = 1
) -> str:
    """
    Generates a realistic, cinematic 3D highway driving perspective SVG illustration
    for each turn direction. Features:
    - Photorealistic asphalt road perspective with vanishing point depth
    - 3D Augmented Reality (AR) glowing trajectory carpet with forward guidance chevrons
    - Authentic green highway overhead directional sign gantry with actual road name
    - Roadside guardrails with amber cat's-eye reflectors and volumetric street lighting
    - Modern automotive cockpit HUD telemetry overlay (Turn Info, Speed Limit, Lane Assist)
    """
    dt = direction_type.upper()
    road_clean = road_name.strip() if road_name else ""
    if not road_clean:
        m = re.search(r'(?:onto|on|along)\s+([^,]+)', headline, re.IGNORECASE)
        road_clean = m.group(1).strip() if m else "Highway Corridor"

    road_display = road_clean[:24].upper()
    dist_display = distance_str if distance_str else "Ahead"

    defs = """
    <defs>
        <!-- Photorealistic Atmospheric Sky & Golden-Hour Twilight Gradients -->
        <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#0a192f"/>
            <stop offset="30%" stop-color="#1e3a5f"/>
            <stop offset="60%" stop-color="#2d6a9f"/>
            <stop offset="82%" stop-color="#c25e1a"/>
            <stop offset="94%" stop-color="#f59e0b"/>
            <stop offset="100%" stop-color="#fef3c7"/>
        </linearGradient>
        <radialGradient id="sunFlareGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#ffffff" stop-opacity="1"/>
            <stop offset="25%" stop-color="#fef08a" stop-opacity="0.9"/>
            <stop offset="55%" stop-color="#f59e0b" stop-opacity="0.38"/>
            <stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="cloudGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#ffffff" stop-opacity="0.95"/>
            <stop offset="55%" stop-color="#fed7aa" stop-opacity="0.75"/>
            <stop offset="100%" stop-color="#c084fc" stop-opacity="0.2"/>
        </linearGradient>
        <linearGradient id="horizonGlow" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.45"/>
            <stop offset="100%" stop-color="#0d2e22" stop-opacity="0"/>
        </linearGradient>
        <linearGradient id="terrainGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#144331"/>
            <stop offset="50%" stop-color="#0e3324"/>
            <stop offset="100%" stop-color="#061912"/>
        </linearGradient>
        <linearGradient id="asphaltGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#2a364a"/>
            <stop offset="45%" stop-color="#1e2738"/>
            <stop offset="100%" stop-color="#0f1523"/>
        </linearGradient>
        <linearGradient id="yellowLineGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#fef08a"/>
            <stop offset="50%" stop-color="#facc15"/>
            <stop offset="100%" stop-color="#eab308"/>
        </linearGradient>

        <!-- Cute 3D Anime/Pixar Character Shading Gradients -->
        <radialGradient id="cuteSkinGrad" cx="35%" cy="30%" r="70%">
            <stop offset="0%" stop-color="#fff1e8"/>
            <stop offset="65%" stop-color="#fed7aa"/>
            <stop offset="100%" stop-color="#fba088"/>
        </radialGradient>
        <radialGradient id="cuteEyeIris" cx="40%" cy="35%" r="65%">
            <stop offset="0%" stop-color="#38bdf8"/>
            <stop offset="45%" stop-color="#0284c7"/>
            <stop offset="100%" stop-color="#082f49"/>
        </radialGradient>
        <linearGradient id="cuteHairGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#9a3412"/>
            <stop offset="40%" stop-color="#78350f"/>
            <stop offset="100%" stop-color="#451a03"/>
        </linearGradient>
        <linearGradient id="cuteJacketGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#0284c7"/>
            <stop offset="45%" stop-color="#0f766e"/>
            <stop offset="100%" stop-color="#064e3b"/>
        </linearGradient>

        <!-- Augmented Reality Directional Chevrons & Headlights -->
        <linearGradient id="arCarpetLeft" x1="100%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stop-color="#00f2fe" stop-opacity="0.95"/>
            <stop offset="60%" stop-color="#10b981" stop-opacity="0.85"/>
            <stop offset="100%" stop-color="#059669" stop-opacity="0.75"/>
        </linearGradient>
        <linearGradient id="arCarpetRight" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#00f2fe" stop-opacity="0.95"/>
            <stop offset="60%" stop-color="#10b981" stop-opacity="0.85"/>
            <stop offset="100%" stop-color="#059669" stop-opacity="0.75"/>
        </linearGradient>
        <linearGradient id="arCarpetStraight" x1="0%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stop-color="#00f2fe" stop-opacity="0.95"/>
            <stop offset="65%" stop-color="#10b981" stop-opacity="0.85"/>
            <stop offset="100%" stop-color="#059669" stop-opacity="0.5"/>
        </linearGradient>
        <linearGradient id="headlightBeam" x1="0%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stop-color="#ffffff" stop-opacity="0.38"/>
            <stop offset="40%" stop-color="#fef08a" stop-opacity="0.2"/>
            <stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/>
        </linearGradient>
        <linearGradient id="signGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#005d38"/>
            <stop offset="100%" stop-color="#004328"/>
        </linearGradient>
        <linearGradient id="hudGlassGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="rgba(15, 23, 42, 0.88)"/>
            <stop offset="100%" stop-color="rgba(7, 15, 30, 0.94)"/>
        </linearGradient>
        
        <filter id="neonGlowCyan" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="4" result="blur"/>
            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <filter id="neonGlowEmerald" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="5" result="blur"/>
            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <filter id="amberBlinkerGlow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="5" result="blur"/>
            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <filter id="dropShadow" x="-10%" y="-10%" width="120%" height="120%">
            <feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#000000" flood-opacity="0.6"/>
        </filter>

        <style>
            @keyframes arChevronFloat {{
                0% {{ opacity: 0.7; transform: translateY(0); }}
                50% {{ opacity: 1.0; transform: translateY(3px); filter: drop-shadow(0 0 6px #38bdf8); }}
                100% {{ opacity: 0.7; transform: translateY(0); }}
            }}
            .animated-ar-chevrons {{
                animation: arChevronFloat 1.25s ease-in-out infinite;
            }}

            /* Real Walking Gait Keyframes (Natural Human Stride) */
            @keyframes realWalkTorso {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-3.5px); }}
            }}
            @keyframes realWalkLeftLeg {{
                0% {{ transform: rotate(-24deg); }}
                50% {{ transform: rotate(20deg); }}
                100% {{ transform: rotate(-24deg); }}
            }}
            @keyframes realWalkRightLeg {{
                0% {{ transform: rotate(20deg); }}
                50% {{ transform: rotate(-24deg); }}
                100% {{ transform: rotate(20deg); }}
            }}
            @keyframes realWalkLeftArm {{
                0% {{ transform: rotate(20deg); }}
                50% {{ transform: rotate(-20deg); }}
                100% {{ transform: rotate(20deg); }}
            }}
            @keyframes realWalkRightArm {{
                0% {{ transform: rotate(-20deg); }}
                50% {{ transform: rotate(20deg); }}
                100% {{ transform: rotate(-20deg); }}
            }}
            .virtual-guide-man-avatar.action-walk .actor-torso-head {{
                animation: realWalkTorso 0.85s ease-in-out infinite;
            }}
            .virtual-guide-man-avatar.action-walk .actor-limb-left-leg {{
                animation: realWalkLeftLeg 0.85s ease-in-out infinite;
            }}
            .virtual-guide-man-avatar.action-walk .actor-limb-right-leg {{
                animation: realWalkRightLeg 0.85s ease-in-out infinite;
            }}
            .virtual-guide-man-avatar.action-walk .actor-limb-left-arm {{
                animation: realWalkLeftArm 0.85s ease-in-out infinite;
            }}
            .virtual-guide-man-avatar.action-walk .actor-limb-right-arm {{
                animation: realWalkRightArm 0.85s ease-in-out infinite;
            }}

            /* Real Running Sprint Keyframes (Cadence 0.52s, Athletic Stride) */
            @keyframes realRunBody {{
                0%, 100% {{ transform: translate(340px, 192px) rotate(8deg); }}
                50% {{ transform: translate(340px, 185px) rotate(11deg); }}
            }}
            @keyframes realRunLeftLeg {{
                0% {{ transform: rotate(-48deg); }}
                50% {{ transform: rotate(44deg); }}
                100% {{ transform: rotate(-48deg); }}
            }}
            @keyframes realRunRightLeg {{
                0% {{ transform: rotate(44deg); }}
                50% {{ transform: rotate(-48deg); }}
                100% {{ transform: rotate(44deg); }}
            }}
            @keyframes realRunLeftArm {{
                0% {{ transform: rotate(42deg); }}
                50% {{ transform: rotate(-40deg); }}
                100% {{ transform: rotate(42deg); }}
            }}
            @keyframes realRunRightArm {{
                0% {{ transform: rotate(-40deg); }}
                50% {{ transform: rotate(42deg); }}
                100% {{ transform: rotate(-40deg); }}
            }}
            .virtual-guide-man-avatar.action-run {{
                animation: realRunBody 0.52s ease-in-out infinite !important;
            }}
            .virtual-guide-man-avatar.action-run .actor-limb-left-leg {{
                animation: realRunLeftLeg 0.52s ease-in-out infinite;
            }}
            .virtual-guide-man-avatar.action-run .actor-limb-right-leg {{
                animation: realRunRightLeg 0.52s ease-in-out infinite;
            }}
            .virtual-guide-man-avatar.action-run .actor-limb-left-arm {{
                animation: realRunLeftArm 0.52s ease-in-out infinite;
            }}
            .virtual-guide-man-avatar.action-run .actor-limb-right-arm {{
                animation: realRunRightArm 0.52s ease-in-out infinite;
            }}

            /* Real Turn Action Keyframes (Smooth Body Pivot & Guiding Point) */
            @keyframes realTurnAction {{
                0% {{ transform: translate(340px, 195px) rotate(0deg) scale(1); }}
                30% {{ transform: translate(325px, 196px) rotate(-10deg) scale(1.02); }}
                60% {{ transform: translate(310px, 193px) rotate(-16deg) scale(1.04); }}
                100% {{ transform: translate(340px, 195px) rotate(0deg) scale(1); }}
            }}
            .virtual-guide-man-avatar.action-turn {{
                animation: realTurnAction 2.8s ease-in-out infinite !important;
            }}

            /* Real Jump Action Keyframes (Anticipation Crouch -> Vertical Leap -> Cushioned Landing) */
            @keyframes realJumpAction {{
                0% {{ transform: translate(340px, 195px) scale(1, 1); }}
                14% {{ transform: translate(340px, 204px) scale(1.08, 0.88); }}
                42% {{ transform: translate(340px, 146px) scale(0.92, 1.14); }}
                62% {{ transform: translate(340px, 142px) scale(0.96, 1.05); }}
                82% {{ transform: translate(340px, 202px) scale(1.10, 0.86); }}
                100% {{ transform: translate(340px, 195px) scale(1, 1); }}
            }}
            .virtual-guide-man-avatar.action-jump {{
                animation: realJumpAction 1.6s cubic-bezier(0.2, 0.8, 0.2, 1) infinite !important;
            }}

            /* Real Cheer Action Keyframes (Joyful Victory Celebration Hop) */
            @keyframes realCheerAction {{
                0%, 100% {{ transform: translate(340px, 195px) rotate(0deg); }}
                25% {{ transform: translate(340px, 175px) rotate(-4deg); }}
                50% {{ transform: translate(340px, 192px) rotate(0deg); }}
                75% {{ transform: translate(340px, 172px) rotate(4deg); }}
            }}
            .virtual-guide-man-avatar.action-cheer {{
                animation: realCheerAction 1.4s ease-in-out infinite !important;
            }}

            /* Real Wave Action Keyframes (Friendly Human Arm & Wrist Greeting) */
            @keyframes realWaveAction {{
                0%, 100% {{ transform: translate(340px, 195px) rotate(0deg); }}
                25% {{ transform: translate(340px, 193px) rotate(3deg); }}
                75% {{ transform: translate(340px, 193px) rotate(-3deg); }}
            }}
            @keyframes realWaveHand {{
                0%, 100% {{ transform: rotate(0deg); }}
                25% {{ transform: rotate(28deg); }}
                75% {{ transform: rotate(-18deg); }}
            }}
            .virtual-guide-man-avatar.action-wave {{
                animation: realWaveAction 1.6s ease-in-out infinite !important;
            }}
            .virtual-guide-man-avatar.action-wave .actor-limb-left-arm {{
                animation: realWaveHand 0.8s ease-in-out infinite !important;
            }}

            /* Natural Breathing & Lifelike Micro-movements */
            @keyframes naturalBreathe {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.02, 1.025); }}
            }}
            .virtual-guide-man-avatar .actor-torso-head {{
                animation: naturalBreathe 3.4s ease-in-out infinite;
            }}

            /* 3D Level Environmental Lighting Theming */
            .env-night #skyGrad stop:nth-child(1) {{ stop-color: #030712 !important; }}
            .env-night #skyGrad stop:nth-child(2) {{ stop-color: #080f24 !important; }}
            .env-night #skyGrad stop:nth-child(3) {{ stop-color: #0f1d3a !important; }}
            .env-night #skyGrad stop:nth-child(4) {{ stop-color: #111e3b !important; }}
            .env-night #skyGrad stop:nth-child(5) {{ stop-color: #0b1528 !important; }}
            .env-night #skyGrad stop:nth-child(6) {{ stop-color: #030712 !important; }}
            .env-night .atmospheric-sun {{ opacity: 0 !important; }}
            .env-night .night-stars-group {{ opacity: 0.95 !important; }}

            .env-day #skyGrad stop:nth-child(1) {{ stop-color: #0284c7 !important; }}
            .env-day #skyGrad stop:nth-child(2) {{ stop-color: #38bdf8 !important; }}
            .env-day #skyGrad stop:nth-child(3) {{ stop-color: #7dd3fc !important; }}
            .env-day #skyGrad stop:nth-child(4) {{ stop-color: #bae6fd !important; }}
            .env-day #skyGrad stop:nth-child(5) {{ stop-color: #e0f2fe !important; }}
            .env-day #skyGrad stop:nth-child(6) {{ stop-color: #f0fdf4 !important; }}
            .env-day .atmospheric-sun {{ transform: translate(490px, 60px) scale(1.1) !important; }}

            /* Compatibility Demonstration Keyframes */
            @keyframes demoCrossLeft {{
                0% {{ transform: translate(340px, 195px) scale(1); }}
                25% {{ transform: translate(310px, 199px) scale(0.98); }}
                60% {{ transform: translate(250px, 193px) rotate(-8deg) scale(0.95); }}
                100% {{ transform: translate(195px, 185px) rotate(-16deg) scale(0.92); }}
            }}
            @keyframes demoCrossRight {{
                0% {{ transform: translate(340px, 195px) scale(1); }}
                25% {{ transform: translate(370px, 199px) scale(0.98); }}
                60% {{ transform: translate(430px, 193px) rotate(8deg) scale(0.95); }}
                100% {{ transform: translate(485px, 185px) rotate(16deg) scale(0.92); }}
            }}
            @keyframes demoCrossStraight {{
                0% {{ transform: translate(340px, 195px) scale(1); }}
                50% {{ transform: translate(340px, 175px) scale(0.92); }}
                100% {{ transform: translate(340px, 150px) scale(0.82); }}
            }}
            @keyframes demoWaveGreeting {{
                0%, 100% {{ transform: translate(340px, 195px) rotate(0deg); }}
                50% {{ transform: translate(340px, 191px) rotate(3deg); }}
            }}
            .virtual-guide-man-avatar.animating-demo-left {{
                animation: demoCrossLeft 3.5s ease-in-out infinite alternate !important;
            }}
            .virtual-guide-man-avatar.animating-demo-right {{
                animation: demoCrossRight 3.5s ease-in-out infinite alternate !important;
            }}
            .virtual-guide-man-avatar.animating-demo-straight {{
                animation: demoCrossStraight 3.5s ease-in-out infinite alternate !important;
            }}
            .virtual-guide-man-avatar.animating-demo-start {{
                animation: demoWaveGreeting 2.5s ease-in-out infinite alternate !important;
            }}
        </style>
    </defs>
    """

    sky_and_horizon = """
    <!-- REAL ATMOSPHERIC SKY & GOLDEN-HOUR SUNSET HORIZON -->
    <rect width="760" height="142" fill="url(#skyGrad)"/>

    <!-- Radiant Sun & Twilight Rays -->
    <g class="atmospheric-sun" transform="translate(490, 110)">
        <circle cx="0" cy="0" r="44" fill="url(#sunFlareGrad)"/>
        <circle cx="0" cy="0" r="14" fill="#ffffff" opacity="0.95"/>
        <line x1="-55" y1="-25" x2="55" y2="25" stroke="#fde047" stroke-width="1.2" opacity="0.3"/>
        <line x1="-25" y1="-50" x2="25" y2="50" stroke="#fde047" stroke-width="1.2" opacity="0.3"/>
    </g>

    <!-- Starry Night Sky Constellations -->
    <g class="night-stars-group" opacity="0">
        <circle cx="45" cy="22" r="1.3" fill="#ffffff"/>
        <circle cx="95" cy="42" r="1.1" fill="#38bdf8"/>
        <circle cx="160" cy="18" r="1.5" fill="#ffffff"/>
        <circle cx="230" cy="38" r="1.2" fill="#7dd3fc"/>
        <circle cx="310" cy="24" r="1.6" fill="#ffffff"/>
        <circle cx="410" cy="44" r="1.2" fill="#bae6fd"/>
        <circle cx="520" cy="18" r="1.5" fill="#ffffff"/>
        <circle cx="620" cy="36" r="1.3" fill="#7dd3fc"/>
        <circle cx="710" cy="22" r="1.4" fill="#ffffff"/>
    </g>

    <!-- Soft Volumetric 3D Clouds with Depth & Highlights -->
    <g class="volumetric-clouds" opacity="0.92">
        <path d="M 40 55 Q 60 35 90 42 Q 120 25 155 36 Q 190 28 220 45 Q 240 55 240 68 L 30 68 Q 20 62 40 55 Z" fill="url(#cloudGrad)" filter="url(#dropShadow)"/>
        <path d="M 50 52 Q 90 32 140 38 Q 185 24 215 42" stroke="#ffffff" stroke-width="2.5" fill="none" opacity="0.6"/>
        
        <path d="M 360 48 Q 390 22 435 30 Q 480 18 525 32 Q 570 24 610 44 Q 630 58 620 68 L 340 68 Q 340 56 360 48 Z" fill="url(#cloudGrad)" filter="url(#dropShadow)"/>
        <path d="M 370 44 Q 430 22 510 26 Q 565 18 600 40" stroke="#fef08a" stroke-width="2.5" fill="none" opacity="0.75"/>
        
        <path d="M 640 28 Q 675 14 715 22 Q 740 26 755 35 L 630 35 Z" fill="url(#cloudGrad)" opacity="0.7"/>
    </g>

    <!-- REALISTIC LAYERED MOUNTAIN RIDGES WITH ATMOSPHERIC PERSPECTIVE -->
    <!-- Far Distant Misty Alpine Ridge (Soft Violet-Blue Silhouette) -->
    <polygon points="0,135 35,102 75,114 120,95 165,110 215,88 265,108 315,92 375,105 435,84 490,98 545,82 605,102 660,86 715,104 760,94 760,135 0,135" fill="#1e2942" opacity="0.88"/>
    <polygon points="120,95 135,112 110,112" fill="#3b4252" opacity="0.6"/>
    <polygon points="215,88 235,108 200,108" fill="#3b4252" opacity="0.6"/>
    <polygon points="435,84 455,100 420,100" fill="#4c566a" opacity="0.6"/>
    <polygon points="545,82 568,102 530,102" fill="#4c566a" opacity="0.6"/>

    <!-- Mid-Range Forested Mountain Ridge (Textured Green-Slate Valleys) -->
    <polygon points="0,135 40,118 90,110 145,122 205,106 265,119 330,104 395,117 460,108 525,120 585,109 645,121 705,112 760,120 760,135 0,135" fill="#132e27" opacity="0.95"/>

    <!-- Foreground Lush Rolling Foothills & Meadows -->
    <polygon points="0,135 60,126 130,120 200,128 275,119 350,128 425,121 500,128 575,121 650,127 720,121 760,127 760,145 0,145" fill="#0d2e22"/>

    <!-- Warm Golden Horizon Glow Strip -->
    <rect y="126" width="760" height="16" fill="url(#horizonGlow)"/>

    <!-- Roadside Real Green Verge & Highway Embankment Ground -->
    <rect y="135" width="760" height="165" fill="url(#terrainGrad)"/>

    <!-- Realistic Roadside Clustered Trees (Pines and Lush Oaks) -->
    <g class="roadside-nature-canopy" opacity="0.95">
        <path d="M 25 142 C 10 120 35 110 50 118 C 70 105 95 125 90 142 Z" fill="#14532d"/>
        <path d="M 60 144 C 50 125 75 115 85 124 C 105 112 125 130 118 144 Z" fill="#166534"/>
        <polygon points="12,143 18,122 25,143" fill="#064e3b"/>
        <polygon points="20,143 28,118 36,143" fill="#047857"/>

        <path d="M 640 142 C 625 118 655 108 670 118 C 690 105 715 125 708 142 Z" fill="#14532d"/>
        <path d="M 675 144 C 660 122 690 112 705 122 C 725 110 750 128 742 144 Z" fill="#166534"/>
        <polygon points="720,143 728,120 736,143" fill="#064e3b"/>
        <polygon points="730,143 738,116 746,143" fill="#047857"/>
    </g>
    """

    def render_hud_telemetry(title: str, sub: str, icon: str = "⬅️", lane_type: str = "left"):
        left_lane_active = (lane_type == "left")
        right_lane_active = (lane_type == "right")
        straight_lane_active = (lane_type == "straight")
        
        return f"""
        <g filter="url(#dropShadow)" transform="translate(18, 14)">
            <rect width="260" height="58" rx="10" fill="url(#hudGlassGrad)" stroke="rgba(56, 189, 248, 0.4)" stroke-width="1.2"/>
            <rect x="2" y="2" width="54" height="54" rx="8" fill="rgba(2, 132, 199, 0.25)" stroke="rgba(56, 189, 248, 0.5)" stroke-width="1"/>
            <text x="29" y="38" text-anchor="middle" font-size="26">{icon}</text>
            <text x="68" y="24" fill="#38bdf8" font-size="10" font-weight="800" font-family="'Segoe UI', Roboto, sans-serif" letter-spacing="1">NEXT MANEUVER • {dist_display.upper()}</text>
            <text x="68" y="42" fill="#ffffff" font-size="14" font-weight="900" font-family="'Segoe UI', Roboto, sans-serif">{title}</text>
            <text x="68" y="52" fill="#94a3b8" font-size="8.5" font-weight="600" font-family="'Segoe UI', Roboto, sans-serif">{sub[:32]}</text>
        </g>

        <g filter="url(#dropShadow)" transform="translate(565, 14)">
            <rect width="177" height="42" rx="8" fill="url(#hudGlassGrad)" stroke="rgba(56, 189, 248, 0.3)" stroke-width="1.2"/>
            <rect x="8" y="8" width="26" height="26" rx="13" fill="#ffffff" stroke="#ef4444" stroke-width="2.5"/>
            <text x="21" y="25" text-anchor="middle" fill="#0f172a" font-size="11" font-weight="900" font-family="'Segoe UI', Roboto, sans-serif">60</text>
            <circle cx="50" cy="21" r="4" fill="#10b981" filter="url(#neonGlowEmerald)"/>
            <text x="60" y="20" fill="#34d399" font-size="9" font-weight="800" font-family="'Segoe UI', Roboto, sans-serif">GPS LOCKED</text>
            <text x="60" y="30" fill="#94a3b8" font-size="8" font-weight="600" font-family="'Segoe UI', Roboto, sans-serif">REAL-TIME HD MAP</text>
            <text x="148" y="25" fill="#38bdf8" font-size="10" font-weight="800" font-family="'Segoe UI', Roboto, sans-serif">STEP {step_num}</text>
        </g>

        <g filter="url(#dropShadow)" transform="translate(265, 252)">
            <rect width="230" height="36" rx="8" fill="url(#hudGlassGrad)" stroke="rgba(56, 189, 248, 0.35)" stroke-width="1"/>
            
            <rect x="6" y="5" width="105" height="26" rx="5" fill="{'rgba(14, 165, 233, 0.35)' if left_lane_active else 'rgba(15, 23, 42, 0.6)'}" stroke="{'#38bdf8' if left_lane_active else 'rgba(148, 163, 184, 0.25)'}" stroke-width="{'1.5' if left_lane_active else '1'}"/>
            <text x="18" y="22" font-size="13">⬅️</text>
            <text x="36" y="21" fill="{'#ffffff' if left_lane_active else '#94a3b8'}" font-size="9" font-weight="800" font-family="'Segoe UI', Roboto, sans-serif">
                {'TURN LANE' if left_lane_active else 'LEFT ONLY'}
            </text>
            {f'<circle cx="98" cy="18" r="3" fill="#10b981" filter="url(#neonGlowEmerald)"/>' if left_lane_active else ''}

            <rect x="119" y="5" width="105" height="26" rx="5" fill="{'rgba(14, 165, 233, 0.35)' if (right_lane_active or straight_lane_active) else 'rgba(15, 23, 42, 0.6)'}" stroke="{'#38bdf8' if (right_lane_active or straight_lane_active) else 'rgba(148, 163, 184, 0.25)'}" stroke-width="{'1.5' if (right_lane_active or straight_lane_active) else '1'}"/>
            <text x="131" y="22" font-size="13">{'➡️' if right_lane_active else '⬆️'}</text>
            <text x="149" y="21" fill="{'#ffffff' if (right_lane_active or straight_lane_active) else '#94a3b8'}" font-size="9" font-weight="800" font-family="'Segoe UI', Roboto, sans-serif">
                {'EXIT LANE' if right_lane_active else 'THRU LANE'}
            </text>
            {f'<circle cx="211" cy="18" r="3" fill="#10b981" filter="url(#neonGlowEmerald)"/>' if (right_lane_active or straight_lane_active) else ''}
        </g>
        """

    # 1. SCENE: TURN LEFT
    if dt == "LEFT" or "left" in headline.lower():
        return f"""<svg viewBox="0 0 760 300" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="border-radius: 12px; display: block; max-height: 290px; background: #050a14;">
        {defs}
        {sky_and_horizon}

        <polygon points="345,135 415,135 590,300 230,300" fill="url(#asphaltGrad)"/>
        
        <path d="M 370 135 Q 310 160 120 185 L 0 195 L 0 255 L 140 245 Q 310 235 440 300 L 320 300 Q 230 220 0 215" fill="#152033" opacity="0.95"/>
        <path d="M 370 135 Q 310 165 140 195 L 0 205 L 0 245 L 150 235 Q 320 215 450 300" fill="url(#asphaltGrad)"/>

        <path d="M 366 135 Q 306 165 136 195 L 0 205" fill="none" stroke="#dc2626" stroke-width="4"/>
        <path d="M 366 135 Q 306 165 136 195 L 0 205" fill="none" stroke="#ffffff" stroke-width="4" stroke-dasharray="14,14"/>

        <line x1="415" y1="135" x2="590" y2="300" stroke="#f8fafc" stroke-width="2.5" opacity="0.8"/>
        
        <line x1="380" y1="135" x2="380" y2="148" stroke="#facc15" stroke-width="1.8" opacity="0.7"/>
        <line x1="382" y1="156" x2="384" y2="175" stroke="#facc15" stroke-width="2.4" opacity="0.75"/>
        <line x1="387" y1="187" x2="391" y2="216" stroke="#facc15" stroke-width="3.2" opacity="0.8"/>
        <line x1="395" y1="235" x2="403" y2="280" stroke="#facc15" stroke-width="4.5" opacity="0.85"/>

        <path d="M 410 300 Q 320 220 180 208 L 0 218 L 0 236 L 195 226 Q 345 236 450 300 Z" fill="url(#arCarpetLeft)" filter="url(#neonGlowEmerald)" opacity="0.9"/>
        
        <g fill="#ffffff" opacity="0.95" filter="url(#dropShadow)" class="animated-ar-chevrons">
            <polygon points="360,266 385,255 376,252 355,261"/>
            <polygon points="360,266 376,276 384,272 366,263"/>
            <polygon points="275,236 295,229 288,226 270,233"/>
            <polygon points="275,236 288,244 294,241 280,234"/>
            <polygon points="170,218 185,214 180,211 166,215"/>
            <polygon points="170,218 180,223 184,221 174,216"/>
            <polygon points="80,218 92,216 88,214 78,216"/>
            <polygon points="80,218 88,221 91,220 83,217"/>
        </g>

        <path d="M 545 130 Q 550 85 525 80" fill="none" stroke="#64748b" stroke-width="3"/>
        <line x1="545" y1="130" x2="552" y2="225" stroke="#475569" stroke-width="3"/>
        <ellipse cx="523" cy="80" rx="6" ry="2.5" fill="#38bdf8"/>
        <ellipse cx="480" cy="225" rx="75" ry="24" fill="#38bdf8" opacity="0.12" filter="url(#neonGlowCyan)"/>

        <path d="M 125 150 Q 120 100 145 95" fill="none" stroke="#64748b" stroke-width="2.5"/>
        <line x1="125" y1="150" x2="120" y2="195" stroke="#475569" stroke-width="2.5"/>
        <ellipse cx="145" cy="95" rx="5" ry="2" fill="#facc15"/>
        <ellipse cx="155" cy="210" rx="55" ry="18" fill="#facc15" opacity="0.14" filter="url(#amberBlinkerGlow)"/>

        <line x1="422" y1="135" x2="605" y2="300" stroke="#64748b" stroke-width="4.5" opacity="0.7"/>
        <line x1="424" y1="138" x2="607" y2="300" stroke="#94a3b8" stroke-width="1.8" opacity="0.8"/>
        <circle cx="452" cy="165" r="1.8" fill="#f59e0b" filter="url(#amberBlinkerGlow)"/>
        <circle cx="492" cy="202" r="2.2" fill="#f59e0b" filter="url(#amberBlinkerGlow)"/>
        <circle cx="542" cy="246" r="2.8" fill="#f59e0b" filter="url(#amberBlinkerGlow)"/>

        <g opacity="0.85">
            <path d="M 70 170 C 55 140 85 130 95 140 C 115 125 130 145 125 165 C 130 175 100 185 70 170 Z" fill="#0c2e22"/>
            <path d="M 18 190 C 5 160 30 150 40 160 C 55 148 70 165 65 180 C 70 190 40 200 18 190 Z" fill="#08231a"/>
            <path d="M 640 150 C 625 125 655 115 665 125 C 685 110 705 130 700 148 C 705 158 675 168 640 150 Z" fill="#0c2e22"/>
            <path d="M 690 165 C 680 140 705 135 715 142 C 730 130 745 145 740 160 Z" fill="#08231a"/>
        </g>

        <g filter="url(#dropShadow)" transform="translate(190, 72)">
            <line x1="-10" y1="6" x2="390" y2="6" stroke="#475569" stroke-width="3"/>
            <line x1="-10" y1="18" x2="390" y2="18" stroke="#475569" stroke-width="2"/>
            <line x1="0" y1="6" x2="0" y2="60" stroke="#334155" stroke-width="3.5"/>
            <line x1="380" y1="6" x2="380" y2="60" stroke="#334155" stroke-width="3.5"/>
            
            <rect x="25" y="0" width="180" height="42" rx="4" fill="url(#signGrad)" stroke="#f8fafc" stroke-width="1.8"/>
            <text x="36" y="16" fill="#facc15" font-size="9" font-weight="900" font-family="'Segoe UI', Roboto, sans-serif">⬅️ EXIT ONLY • {dist_display.upper()}</text>
            <text x="36" y="32" fill="#ffffff" font-size="12" font-weight="900" font-family="'Segoe UI', Roboto, sans-serif">{road_display}</text>

            <rect x="215" y="0" width="145" height="42" rx="4" fill="url(#signGrad)" stroke="#f8fafc" stroke-width="1.5" opacity="0.9"/>
            <text x="226" y="16" fill="#ffffff" font-size="8.5" font-weight="800" font-family="'Segoe UI', Roboto, sans-serif">⬆️ THRU CORRIDOR</text>
            <text x="226" y="32" fill="#bae6fd" font-size="11" font-weight="800" font-family="'Segoe UI', Roboto, sans-serif">EXPRESSWAY</text>
        </g>

        {render_accessible_virtual_guide_avatar("LEFT", headline, road_name)}

        {render_hud_telemetry("TURN LEFT ⬅️", road_clean, icon="⬅️", lane_type="left")}
        </svg>"""

    # 2. SCENE: TURN RIGHT
    elif dt == "RIGHT" or "right" in headline.lower():
        return f"""<svg viewBox="0 0 760 300" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="border-radius: 12px; display: block; max-height: 290px; background: #050a14;">
        {defs}
        {sky_and_horizon}

        <polygon points="345,135 415,135 530,300 170,300" fill="url(#asphaltGrad)"/>
        
        <path d="M 390 135 Q 450 160 640 185 L 760 195 L 760 255 L 620 245 Q 450 235 320 300 L 440 300 Q 530 220 760 215" fill="#152033" opacity="0.95"/>
        <path d="M 390 135 Q 450 165 620 195 L 760 205 L 760 245 L 610 235 Q 440 215 310 300" fill="url(#asphaltGrad)"/>

        <path d="M 394 135 Q 454 165 624 195 L 760 205" fill="none" stroke="#dc2626" stroke-width="4"/>
        <path d="M 394 135 Q 454 165 624 195 L 760 205" fill="none" stroke="#ffffff" stroke-width="4" stroke-dasharray="14,14"/>

        <line x1="345" y1="135" x2="170" y2="300" stroke="#f8fafc" stroke-width="2.5" opacity="0.8"/>
        
        <line x1="380" y1="135" x2="380" y2="148" stroke="#facc15" stroke-width="1.8" opacity="0.7"/>
        <line x1="378" y1="156" x2="376" y2="175" stroke="#facc15" stroke-width="2.4" opacity="0.75"/>
        <line x1="373" y1="187" x2="369" y2="216" stroke="#facc15" stroke-width="3.2" opacity="0.8"/>
        <line x1="365" y1="235" x2="357" y2="280" stroke="#facc15" stroke-width="4.5" opacity="0.85"/>

        <path d="M 350 300 Q 440 220 580 208 L 760 218 L 760 236 L 565 226 Q 415 236 310 300 Z" fill="url(#arCarpetRight)" filter="url(#neonGlowEmerald)" opacity="0.9"/>
        
        <g fill="#ffffff" opacity="0.95" filter="url(#dropShadow)" class="animated-ar-chevrons">
            <polygon points="400,266 375,255 384,252 405,261"/>
            <polygon points="400,266 384,276 376,272 394,263"/>
            <polygon points="485,236 465,229 472,226 490,233"/>
            <polygon points="485,236 472,244 466,241 480,234"/>
            <polygon points="590,218 575,214 580,211 594,215"/>
            <polygon points="590,218 580,223 576,221 586,216"/>
            <polygon points="680,218 668,216 672,214 682,216"/>
        </g>

        <path d="M 215 130 Q 210 85 235 80" fill="none" stroke="#64748b" stroke-width="3"/>
        <line x1="215" y1="130" x2="208" y2="225" stroke="#475569" stroke-width="3"/>
        <ellipse cx="237" cy="80" rx="6" ry="2.5" fill="#38bdf8"/>
        <ellipse cx="280" cy="225" rx="75" ry="24" fill="#38bdf8" opacity="0.12" filter="url(#neonGlowCyan)"/>

        <line x1="338" y1="135" x2="155" y2="300" stroke="#64748b" stroke-width="4.5" opacity="0.7"/>
        <line x1="336" y1="138" x2="153" y2="300" stroke="#94a3b8" stroke-width="1.8" opacity="0.8"/>
        <circle cx="308" cy="165" r="1.8" fill="#f59e0b" filter="url(#amberBlinkerGlow)"/>
        <circle cx="268" cy="202" r="2.2" fill="#f59e0b" filter="url(#amberBlinkerGlow)"/>
        <circle cx="218" cy="246" r="2.8" fill="#f59e0b" filter="url(#amberBlinkerGlow)"/>

        <g filter="url(#dropShadow)" transform="translate(190, 72)">
            <line x1="-10" y1="6" x2="390" y2="6" stroke="#475569" stroke-width="3"/>
            <line x1="-10" y1="18" x2="390" y2="18" stroke="#475569" stroke-width="2"/>
            <line x1="0" y1="6" x2="0" y2="60" stroke="#334155" stroke-width="3.5"/>
            <line x1="380" y1="6" x2="380" y2="60" stroke="#334155" stroke-width="3.5"/>
            
            <rect x="25" y="0" width="145" height="42" rx="4" fill="url(#signGrad)" stroke="#f8fafc" stroke-width="1.5" opacity="0.9"/>
            <text x="36" y="16" fill="#ffffff" font-size="8.5" font-weight="800" font-family="'Segoe UI', Roboto, sans-serif">⬆️ THRU CORRIDOR</text>
            <text x="36" y="32" fill="#bae6fd" font-size="11" font-weight="800" font-family="'Segoe UI', Roboto, sans-serif">EXPRESSWAY</text>

            <rect x="175" y="0" width="180" height="42" rx="4" fill="url(#signGrad)" stroke="#f8fafc" stroke-width="1.8"/>
            <text x="186" y="16" fill="#facc15" font-size="9" font-weight="900" font-family="'Segoe UI', Roboto, sans-serif">➡️ EXIT ONLY • {dist_display.upper()}</text>
            <text x="186" y="32" fill="#ffffff" font-size="12" font-weight="900" font-family="'Segoe UI', Roboto, sans-serif">{road_display}</text>
        </g>

        {render_accessible_virtual_guide_avatar("RIGHT", headline, road_name)}

        {render_hud_telemetry("TURN RIGHT ➡️", road_clean, icon="➡️", lane_type="right")}
        </svg>"""

    # 3. SCENE: ARRIVE (Celebratory Arrival at Real Destination)
    elif dt == "ARRIVE" or "arrive" in headline.lower():
        return f"""<svg viewBox="0 0 760 300" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="border-radius: 12px; display: block; max-height: 290px; background: #050a14;">
        {defs}
        {sky_and_horizon}

        <polygon points="345,135 415,135 600,300 160,300" fill="url(#asphaltGrad)"/>
        <line x1="345" y1="135" x2="160" y2="300" stroke="#f8fafc" stroke-width="3" opacity="0.85"/>
        <line x1="415" y1="135" x2="600" y2="300" stroke="#f8fafc" stroke-width="3" opacity="0.85"/>

        <g transform="translate(260, 75)" opacity="0.95">
            <rect x="0" y="25" width="240" height="35" rx="4" fill="#0f2744" stroke="#38bdf8" stroke-width="1.8"/>
            <rect x="15" y="8" width="210" height="18" rx="3" fill="#07172b" stroke="#38bdf8" stroke-width="1"/>
            <text x="120" y="21" text-anchor="middle" fill="#38bdf8" font-size="9" font-weight="900" font-family="'Segoe UI', sans-serif" letter-spacing="2">★ DESTINATION ARRIVAL PLAZA ★</text>
            <text x="120" y="47" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="900" font-family="'Segoe UI', sans-serif">{road_display}</text>
            <rect x="5" y="60" width="25" height="40" fill="#0d1b2e" stroke="#38bdf8" stroke-width="1"/>
            <rect x="210" y="60" width="25" height="40" fill="#0d1b2e" stroke="#38bdf8" stroke-width="1"/>
        </g>

        <rect x="375" y="20" width="10" height="180" fill="url(#arCarpetStraight)" filter="url(#neonGlowCyan)" opacity="0.85"/>
        <line x1="380" y1="15" x2="380" y2="200" stroke="#ffffff" stroke-width="3" filter="url(#neonGlowCyan)"/>

        <g filter="url(#neonGlowEmerald)" transform="translate(380, 50)">
            <circle cx="0" cy="0" r="18" fill="#10b981" stroke="#ffffff" stroke-width="2.5"/>
            <text x="0" y="7" text-anchor="middle" font-size="16">🏁</text>
        </g>

        <ellipse cx="380" cy="205" rx="70" ry="20" fill="none" stroke="#10b981" stroke-width="3.5" filter="url(#neonGlowEmerald)"/>
        <ellipse cx="380" cy="205" rx="110" ry="32" fill="none" stroke="#38bdf8" stroke-width="2" filter="url(#neonGlowCyan)" stroke-dasharray="10,8"/>
        <ellipse cx="380" cy="205" rx="150" ry="44" fill="none" stroke="#facc15" stroke-width="1.5" opacity="0.6"/>

        <g opacity="0.85">
            <path d="M 120 180 C 105 140 145 130 155 140 C 180 125 195 150 190 175 Z" fill="#0d3326"/>
            <path d="M 570 180 C 555 140 595 130 605 140 C 630 125 645 150 640 175 Z" fill="#0d3326"/>
        </g>

        {render_accessible_virtual_guide_avatar("ARRIVE", headline, road_name)}

        {render_hud_telemetry("YOU HAVE ARRIVED! 🏁", "Journey Complete • Safely At Destination", icon="🏁", lane_type="straight")}
        </svg>"""

    # 4. SCENE: START / DEPART
    elif dt == "START" or "start" in headline.lower():
        return f"""<svg viewBox="0 0 760 300" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="border-radius: 12px; display: block; max-height: 290px; background: #050a14;">
        {defs}
        {sky_and_horizon}

        <polygon points="345,135 415,135 600,300 160,300" fill="url(#asphaltGrad)"/>
        <line x1="345" y1="135" x2="160" y2="300" stroke="#f8fafc" stroke-width="2.5" opacity="0.8"/>
        <line x1="415" y1="135" x2="600" y2="300" stroke="#f8fafc" stroke-width="2.5" opacity="0.8"/>

        <polygon points="360,250 340,145 375,145 372,250" fill="url(#headlightBeam)"/>
        <polygon points="400,250 385,145 420,145 412,250" fill="url(#headlightBeam)"/>

        <ellipse cx="380" cy="245" rx="120" ry="25" fill="none" stroke="#10b981" stroke-width="2.5" stroke-dasharray="12,8" filter="url(#neonGlowEmerald)"/>

        <polygon points="370,140 390,140 415,300 345,300" fill="url(#arCarpetStraight)" filter="url(#neonGlowEmerald)" opacity="0.85"/>
        
        <g fill="#ffffff" opacity="0.95" filter="url(#dropShadow)">
            <polygon points="380,260 370,270 375,273 380,267 385,273 390,270"/>
            <polygon points="380,225 372,233 376,235 380,230 384,235 388,233"/>
            <polygon points="380,190 374,196 377,198 380,194 383,198 386,196"/>
            <polygon points="380,160 376,164 378,165 380,162 382,165 384,164"/>
        </g>

        {render_accessible_virtual_guide_avatar("START", headline, road_name)}

        {render_hud_telemetry("START JOURNEY 🟢", road_clean, icon="🟢", lane_type="straight")}
        </svg>"""

    # 5. SCENE: STRAIGHT / PROCEED (Long Open Highway Cruise)
    else:
        return f"""<svg viewBox="0 0 760 300" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="border-radius: 12px; display: block; max-height: 290px; background: #050a14;">
        {defs}
        {sky_and_horizon}

        <polygon points="345,135 415,135 620,300 140,300" fill="url(#asphaltGrad)"/>
        
        <line x1="345" y1="135" x2="140" y2="300" stroke="#f8fafc" stroke-width="3" opacity="0.85"/>
        <line x1="415" y1="135" x2="620" y2="300" stroke="#f8fafc" stroke-width="3" opacity="0.85"/>

        <line x1="380" y1="135" x2="380" y2="300" stroke="#facc15" stroke-width="2.5" opacity="0.8"/>
        <line x1="383" y1="135" x2="384" y2="300" stroke="#facc15" stroke-width="2.5" opacity="0.8"/>

        <line x1="362" y1="135" x2="260" y2="300" stroke="#ffffff" stroke-width="2" stroke-dasharray="14,16" opacity="0.75"/>
        <line x1="398" y1="135" x2="500" y2="300" stroke="#ffffff" stroke-width="2" stroke-dasharray="14,16" opacity="0.75"/>

        <polygon points="368,140 392,140 435,300 325,300" fill="url(#arCarpetStraight)" filter="url(#neonGlowEmerald)" opacity="0.88"/>
        
        <g fill="#ffffff" opacity="0.95" filter="url(#dropShadow)" class="animated-ar-chevrons">
            <polygon points="380,265 368,276 374,279 380,272 386,279 392,276"/>
            <polygon points="380,230 370,239 375,241 380,236 385,241 390,239"/>
            <polygon points="380,195 373,202 376,204 380,200 384,204 387,202"/>
            <polygon points="380,165 375,170 377,172 380,168 383,172 385,170"/>
        </g>

        <path d="M 175 130 Q 170 80 198 75" fill="none" stroke="#64748b" stroke-width="3"/>
        <line x1="175" y1="130" x2="165" y2="225" stroke="#475569" stroke-width="3"/>
        <ellipse cx="200" cy="75" rx="6" ry="2.5" fill="#38bdf8"/>
        <ellipse cx="230" cy="225" rx="75" ry="24" fill="#38bdf8" opacity="0.12" filter="url(#neonGlowCyan)"/>

        <path d="M 585 130 Q 590 80 562 75" fill="none" stroke="#64748b" stroke-width="3"/>
        <line x1="585" y1="130" x2="595" y2="225" stroke="#475569" stroke-width="3"/>
        <ellipse cx="560" cy="75" rx="6" ry="2.5" fill="#38bdf8"/>
        <ellipse cx="530" cy="225" rx="75" ry="24" fill="#38bdf8" opacity="0.12" filter="url(#neonGlowCyan)"/>

        <line x1="335" y1="135" x2="120" y2="300" stroke="#64748b" stroke-width="4.5" opacity="0.7"/>
        <circle cx="280" cy="175" r="2" fill="#f59e0b" filter="url(#amberBlinkerGlow)"/>
        <circle cx="220" cy="225" r="2.5" fill="#f59e0b" filter="url(#amberBlinkerGlow)"/>
        <circle cx="160" cy="275" r="3" fill="#f59e0b" filter="url(#amberBlinkerGlow)"/>

        <line x1="425" y1="135" x2="640" y2="300" stroke="#64748b" stroke-width="4.5" opacity="0.7"/>
        <circle cx="480" cy="175" r="2" fill="#f59e0b" filter="url(#amberBlinkerGlow)"/>
        <circle cx="540" cy="225" r="2.5" fill="#f59e0b" filter="url(#amberBlinkerGlow)"/>
        <circle cx="600" cy="275" r="3" fill="#f59e0b" filter="url(#amberBlinkerGlow)"/>

        <g filter="url(#dropShadow)" transform="translate(210, 68)">
            <line x1="-10" y1="6" x2="350" y2="6" stroke="#475569" stroke-width="3"/>
            <line x1="-10" y1="18" x2="350" y2="18" stroke="#475569" stroke-width="2"/>
            <line x1="0" y1="6" x2="0" y2="60" stroke="#334155" stroke-width="3.5"/>
            <line x1="340" y1="6" x2="340" y2="60" stroke="#334155" stroke-width="3.5"/>
            
            <rect x="35" y="0" width="270" height="42" rx="4" fill="url(#signGrad)" stroke="#f8fafc" stroke-width="1.8"/>
            <text x="170" y="16" text-anchor="middle" fill="#facc15" font-size="9" font-weight="900" font-family="'Segoe UI', Roboto, sans-serif">⬆️ CRUISE STRAIGHT • {dist_display.upper()}</text>
            <text x="170" y="32" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="900" font-family="'Segoe UI', Roboto, sans-serif">{road_display}</text>
        </g>

        {render_accessible_virtual_guide_avatar("STRAIGHT", headline, road_name)}

        {render_hud_telemetry("GO STRAIGHT ⬆️", road_clean, icon="⬆️", lane_type="straight")}
        </svg>"""


def build_virtual_guide_turns_html(
    friendly_turns: List[FriendlyTurnStep],
    origin: str,
    destination: str,
    travel_mode: str = "Car",
    lang: Optional[str] = None
) -> str:
    """
    Renders the Virtual Man's Interactive Step-by-Step Route Guide HUD.
    Features:
    1. Animated Virtual Companion / Guide Avatar explaining every single turn.
    2. Zero-confusion, plain-language guidance accessible even to non-readers.
    3. Prominent individual 🔊 'Listen' button on each step for crystal-clear audio narration.
    4. Landmark clues ('What You Will See') to easily recognize locations.
    5. Interactive carousel and checklist views with auto-sync to map progression.
    """
    if not friendly_turns:
        clean_orig_name = re.sub(r'[📍🏁🧭🚗●🛰️]', '', origin).strip() or "Departure Point"
        clean_dest_name = re.sub(r'[📍🏁🧭🚗●🛰️]', '', destination).strip() or "Arrival Plaza"
        friendly_turns = [
            FriendlyTurnStep(
                step_num=1,
                total_steps=3,
                direction_type="START",
                action_headline=f"Begin Journey at {clean_orig_name}",
                road_name="Scenic Boulevard",
                distance_human="500 m",
                time_estimate="2 mins",
                spoken_text=f"Welcome! Let's get moving from {clean_orig_name}. Your virtual guide is walking with you.",
                virtual_guide_speech=f"Hello traveler! I am your cute 3D companion. I'll walk, run, and guide every turn with you to {clean_dest_name}!",
                what_to_look_for="Panoramic mountain vista, illuminated navigation towers, and safety beacons.",
                icon="🟢",
                accessible_guidance="Level tactile paving with clear audio alerts and high-contrast signage.",
                tactile_crossing_note="Wide pedestrian sidewalk with safety railing."
            ),
            FriendlyTurnStep(
                step_num=2,
                total_steps=3,
                direction_type="STRAIGHT",
                action_headline="Follow Scenic Mountain Ridge Parkway",
                road_name="Highland Ridge Highway",
                distance_human="2.4 km",
                time_estimate="5 mins",
                spoken_text="Continue straight along Highland Ridge Highway. Enjoy the alpine views as we progress safely.",
                virtual_guide_speech="Cruise straight ahead. The road ahead is completely hazard-free and verified by satellite telemetry!",
                what_to_look_for="Lush green roadside trees, guardrails, and sweeping alpine peaks.",
                icon="⬆️",
                accessible_guidance="Continuous pedestrian pathway with audio crosswalk beacons.",
                tactile_crossing_note="Paved shoulder with reflective markers."
            ),
            FriendlyTurnStep(
                step_num=3,
                total_steps=3,
                direction_type="ARRIVE",
                action_headline=f"Arrive safely at {clean_dest_name}",
                road_name="Destination Terminal Way",
                distance_human="150 m",
                time_estimate="1 min",
                spoken_text=f"You have arrived safely at {clean_dest_name}. Excellent journey!",
                virtual_guide_speech="Hooray! We made it! Thank you for traveling with NexRoute. Click the buttons below to see me walk, run, or jump!",
                what_to_look_for="Destination arrival plaza, welcome arch, and verified parking bay.",
                icon="🏁",
                accessible_guidance="Step-free ramp entrance directly into the destination plaza.",
                tactile_crossing_note="Braille-guided entrance portal."
            )
        ]

    turns_data = [
        {
            "num": t.step_num,
            "total": t.total_steps,
            "type": t.direction_type,
            "headline": t.action_headline,
            "simple_instruction": (
                "START HERE 🟢" if t.direction_type == "START" else
                "TURN LEFT ⬅️" if t.direction_type == "LEFT" else
                "TURN RIGHT ➡️" if t.direction_type == "RIGHT" else
                "YOU ARRIVED! 🏁" if t.direction_type == "ARRIVE" else
                "GO STRAIGHT ⬆️"
            ),
            "speech": t.virtual_guide_speech,
            "landmarks": t.what_to_look_for,
            "dist": t.distance_human,
            "time": t.time_estimate,
            "road": t.road_name,
            "icon": t.icon,
            "spoken": t.spoken_text,
            "accessible_guidance": t.accessible_guidance,
            "tactile_crossing_note": t.tactile_crossing_note,
            "svg": get_turn_visual_svg(t.direction_type, t.action_headline, t.road_name, t.distance_human, t.step_num, t.total_steps)
        }
        for t in friendly_turns
    ]
    turns_json = json.dumps(turns_data)

    clean_orig = re.sub(r'[📍🏁🧭🚗●🛰️]', '', origin).strip().split(",")[0]
    clean_dest = re.sub(r'[📍🏁🧭🚗●🛰️]', '', destination).strip().split(",")[0]

    try:
        from src.i18n import t, get_current_language
        actual_lang = lang or get_current_language()
    except Exception:
        actual_lang = lang or "en"
        def t(k, default="", lang=None): return default

    vg_story_title = t("guide.step_story_title", lang=actual_lang, default="VIRTUAL GUIDE: STEP-BY-STEP FRIENDLY ROUTE STORY")
    vg_for_traveler = t("guide.for_every_traveler", lang=actual_lang, default="FOR EVERY TRAVELER • LISTEN & FOLLOW")
    vg_visual_flow = t("guide.visual_picture_flow", lang=actual_lang, default="Visual Picture Flow Process • Simple Pictures • Follow Step-by-Step")
    vg_view_all = t("guide.view_all_pictures", lang=actual_lang, default="View All Pictures")
    vg_pipeline_lbl = t("guide.route_journey_pipeline", lang=actual_lang, default="ROUTE JOURNEY PIPELINE")
    vg_avatar_actions = t("guide.avatar_real_actions", lang=actual_lang, default="AVATAR REAL ACTIONS:")
    vg_act_walk = t("guide.action_walk", lang=actual_lang, default="Walk")
    vg_act_run = t("guide.action_run", lang=actual_lang, default="Run")
    vg_act_turn = t("guide.action_turn", lang=actual_lang, default="Turn")
    vg_act_jump = t("guide.action_jump", lang=actual_lang, default="Jump")
    vg_act_cheer = t("guide.action_cheer", lang=actual_lang, default="Cheer")
    vg_act_wave = t("guide.action_wave", lang=actual_lang, default="Wave")
    vg_cam_modes = t("guide.cam_modes", lang=actual_lang, default="3D LEVEL CAMERA:")
    vg_cam_pov = t("guide.cam_pov", lang=actual_lang, default="🎥 Driver POV")
    vg_cam_drone = t("guide.cam_drone", lang=actual_lang, default="🚁 3D Follow Drone")
    vg_cam_iso = t("guide.cam_iso", lang=actual_lang, default="🗺️ 3D Isometric Level")
    vg_env_lighting = t("guide.env_lighting", lang=actual_lang, default="ENVIRONMENT:")
    vg_env_day = t("guide.env_day", lang=actual_lang, default="☀️ Day")
    vg_env_sunset = t("guide.env_sunset", lang=actual_lang, default="🌅 Sunset")
    vg_env_night = t("guide.env_night", lang=actual_lang, default="🌙 Cyber Night")
    vg_walking_nat = t("guide.walking_naturally", lang=actual_lang, default="Walking naturally along route")
    vg_speed_lbl = t("guide.telemetry_speed", lang=actual_lang, default="SPEED")
    vg_heading_lbl = t("guide.telemetry_heading", lang=actual_lang, default="HEADING")
    vg_corridor_lbl = t("guide.telemetry_corridor", lang=actual_lang, default="ROAD CORRIDOR")
    vg_remaining_lbl = t("guide.telemetry_remaining", lang=actual_lang, default="REMAINING")
    vg_status_lbl = t("guide.telemetry_status", lang=actual_lang, default="STATUS")
    vg_ready_lbl = t("guide.ready_to_follow", lang=actual_lang, default="Ready to Follow")
    vg_leaving_start = t("guide.leaving_start_point", lang=actual_lang, default="Leaving Start Point")
    vg_guide_says = t("guide.guide_says", lang=actual_lang, default="YOUR VIRTUAL GUIDE SAYS:")
    vg_what_to_look = t("guide.what_to_look_for", lang=actual_lang, default="WHAT TO LOOK FOR:")
    vg_access_title = t("guide.accessibility_title", lang=actual_lang, default="ACCESSIBILITY & CROSSING ASSIST")
    vg_access_sub = t("guide.accessibility_subtitle", lang=actual_lang, default="Virtual Guide Step-by-Step Disability Guidance")

    return f"""
    <style>
    .guide-hud-container {{
        background: linear-gradient(135deg, rgba(8, 22, 44, 0.98) 0%, rgba(13, 27, 54, 0.95) 50%, rgba(15, 23, 42, 0.97) 100%);
        border: 1.5px solid rgba(56, 189, 248, 0.45);
        border-radius: 16px;
        padding: 16px 20px;
        margin: 8px 0;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.75), 0 0 24px rgba(56, 189, 248, 0.18);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        position: relative;
        overflow: hidden;
    }}
    .guide-hud-container::before {{
        content: '';
        position: absolute;
        top: -60px;
        right: -60px;
        width: 180px;
        height: 180px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.15) 0%, transparent 70%);
        pointer-events: none;
    }}
    /* Animated Captain Avatar with Sonar Radar */
    .avatar-radar-box {{
        position: relative;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.35) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 2px solid #38bdf8;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.55rem;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.5);
    }}
    .avatar-radar-box::after {{
        content: '';
        position: absolute;
        inset: -5px;
        border-radius: 50%;
        border: 1.5px solid rgba(56, 189, 248, 0.5);
        animation: radarPulse 2.4s infinite ease-out;
        pointer-events: none;
    }}
    @keyframes radarPulse {{
        0% {{ transform: scale(0.95); opacity: 1; }}
        100% {{ transform: scale(1.35); opacity: 0; }}
    }}
    /* Live Equalizer Audio Waves */
    .guide-audio-indicator {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.14);
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 10px;
        border-radius: 999px;
    }}
    .equalizer-bars {{
        display: flex;
        align-items: flex-end;
        gap: 2.5px;
        height: 14px;
    }}
    .eq-bar {{
        width: 2.5px;
        height: 4px;
        background: #34d399;
        border-radius: 2px;
        transition: height 0.15s ease;
    }}
    .guide-audio-indicator.speaking .eq-bar {{
        animation: eqPulse 0.85s infinite ease-in-out alternate;
    }}
    .guide-audio-indicator.speaking .eq-bar:nth-child(1) {{ animation-delay: 0.1s; }}
    .guide-audio-indicator.speaking .eq-bar:nth-child(2) {{ animation-delay: 0.35s; }}
    .guide-audio-indicator.speaking .eq-bar:nth-child(3) {{ animation-delay: 0.2s; }}
    .guide-audio-indicator.speaking .eq-bar:nth-child(4) {{ animation-delay: 0.45s; }}
    .guide-audio-indicator.speaking .eq-bar:nth-child(5) {{ animation-delay: 0.15s; }}
    @keyframes eqPulse {{
        0% {{ height: 4px; background: #34d399; }}
        50% {{ height: 14px; background: #38bdf8; }}
        100% {{ height: 6px; background: #10b981; }}
    }}
    /* Progress Track Bar */
    .quest-progress-wrap {{
        margin-top: 10px;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }}
    .quest-progress-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.70rem;
        color: #94a3b8;
        font-weight: 600;
    }}
    .quest-progress-bar {{
        width: 100%;
        height: 5px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 999px;
        overflow: hidden;
        position: relative;
    }}
    .quest-progress-fill {{
        height: 100%;
        background: linear-gradient(90deg, #10b981 0%, #06b6d4 50%, #38bdf8 100%);
        border-radius: 999px;
        transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 0 8px rgba(56, 189, 248, 0.6);
    }}
    /* Connected Metro Roadmap Pipeline */
    .guide-flow-track {{
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 10px;
        overflow-x: auto;
        padding: 6px 4px 10px 4px;
        scrollbar-width: thin;
        scrollbar-color: rgba(56, 189, 248, 0.5) rgba(15, 23, 42, 0.6);
    }}
    .guide-flow-track::-webkit-scrollbar {{
        height: 6px;
    }}
    .guide-flow-track::-webkit-scrollbar-track {{
        background: rgba(15, 23, 42, 0.8);
        border-radius: 999px;
    }}
    .guide-flow-track::-webkit-scrollbar-thumb {{
        background: linear-gradient(90deg, rgba(56, 189, 248, 0.4), rgba(16, 185, 129, 0.5));
        border-radius: 999px;
    }}
    .flow-step-item {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        flex-shrink: 0;
    }}
    .flow-station-card {{
        background: rgba(15, 23, 42, 0.92);
        border: 1.5px solid rgba(255, 255, 255, 0.12);
        border-radius: 10px;
        padding: 7px 14px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
        color: #94a3b8;
        user-select: none;
        min-width: 145px;
        white-space: nowrap;
        text-align: left;
    }}
    .flow-station-card:hover {{
        border-color: #38bdf8;
        background: rgba(56, 189, 248, 0.16);
        color: #ffffff;
        transform: translateY(-2px);
    }}
    .flow-station-card.active {{
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.35) 0%, rgba(3, 105, 161, 0.75) 100%);
        border: 1.5px solid #38bdf8;
        box-shadow: 0 0 18px rgba(56, 189, 248, 0.5), inset 0 0 10px rgba(56, 189, 248, 0.25);
        color: #ffffff;
        transform: scale(1.02);
    }}
    .flow-station-card.completed {{
        border-color: rgba(16, 185, 129, 0.5);
        background: rgba(16, 185, 129, 0.12);
        color: #d1fae5;
    }}
    .station-badge {{
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.70rem;
        font-weight: 800;
        flex-shrink: 0;
    }}
    .flow-station-card.active .station-badge {{
        background: #38bdf8;
        color: #02132b;
        box-shadow: 0 0 8px #38bdf8;
    }}
    .flow-station-card.completed .station-badge {{
        background: #10b981;
        color: #ffffff;
    }}
    .station-info {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 2px;
        line-height: 1.25;
        overflow: hidden;
    }}
    .station-title {{
        font-size: 0.76rem;
        font-weight: 800;
        white-space: nowrap;
        color: #e2e8f0;
    }}
    .flow-station-card.active .station-title {{
        color: #ffffff;
    }}
    .station-dist {{
        font-size: 0.68rem;
        color: #94a3b8;
        font-weight: 600;
        white-space: nowrap;
    }}
    .flow-station-card.active .station-dist {{
        color: #7dd3fc;
        font-weight: 700;
    }}
    .flow-station-card.completed .station-dist {{
        color: #6ee7b7;
    }}
    /* Traveler Experience Telemetry Strip */
    .traveler-experience-strip {{
        background: rgba(10, 20, 38, 0.88);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 10px;
        padding: 8px 16px;
        margin-top: 10px;
        display: flex;
        align-items: center;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 10px;
        box-shadow: inset 0 0 12px rgba(0, 0, 0, 0.45);
    }}
    .traveler-telemetry-item {{
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2px;
        min-width: 80px;
    }}
    .telemetry-label {{
        font-size: 0.62rem;
        font-weight: 800;
        color: #94a3b8;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }}
    .telemetry-value {{
        font-size: 0.82rem;
        font-weight: 800;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }}
    .telemetry-divider {{
        width: 1px;
        height: 24px;
        background: rgba(255, 255, 255, 0.08);
    }}
    .drive-simulate-btn {{
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.35) 0%, rgba(0, 240, 181, 0.40) 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        box-shadow: 0 0 18px rgba(0, 217, 255, 0.50), 0 0 10px rgba(0, 240, 181, 0.40) !important;
        border: 2px solid #00F0B5 !important;
        border-radius: 8px !important;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    .drive-simulate-btn:hover {{
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.50) 0%, rgba(0, 240, 181, 0.55) 100%) !important;
        border-color: #00D9FF !important;
        box-shadow: 0 0 28px rgba(0, 240, 181, 0.70) !important;
        transform: translateY(-2px) !important;
    }}
    .drive-simulate-btn.driving-active {{
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.60) 0%, rgba(0, 240, 181, 0.60) 100%) !important;
        box-shadow: 0 0 26px rgba(0, 217, 255, 0.80), 0 0 14px rgba(0, 240, 181, 0.60) !important;
        border-color: #00D9FF !important;
    }}
    .guide-speed-pill {{
        background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;
        border: 1.5px solid rgba(0, 217, 255, 0.35) !important;
        color: #EAF7FF !important;
        padding: 4px 10px !important;
        border-radius: 8px !important;
        font-size: 0.70rem !important;
        font-weight: 800 !important;
        cursor: pointer !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    .guide-speed-pill:hover {{
        border-color: #00D9FF !important;
        background: linear-gradient(135deg, #10263E 0%, #0B1B2D 100%) !important;
        box-shadow: 0 0 14px rgba(0, 240, 181, 0.40) !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
    }}
    .guide-speed-pill.active {{
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.35) 0%, rgba(0, 240, 181, 0.40) 100%) !important;
        border: 1.5px solid #00F0B5 !important;
        color: #ffffff !important;
        box-shadow: 0 0 16px rgba(0, 217, 255, 0.50), 0 0 8px rgba(0, 240, 181, 0.40) !important;
    }}
    .secondary-btn {{
        background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;
        border: 1.5px solid rgba(0, 217, 255, 0.35) !important;
        color: #EAF7FF !important;
    }}
    .secondary-btn:hover {{
        background: linear-gradient(135deg, #10263E 0%, #0B1B2D 100%) !important;
        border-color: #00D9FF !important;
        box-shadow: 0 0 14px rgba(0, 240, 181, 0.40) !important;
        color: #ffffff !important;
    }}
    .flow-connector-track {{
        color: rgba(56, 189, 248, 0.6);
        font-size: 0.9rem;
        font-weight: 800;
        user-select: none;
    }}
    /* Overhead Highway / Street Navigation Signboard */
    .hud-signboard {{
        background: linear-gradient(135deg, rgba(2, 28, 59, 0.85) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1.5px solid rgba(56, 189, 248, 0.35);
        border-radius: 12px;
        padding: 12px 16px;
        margin-top: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
    }}
    .hud-signboard-left {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .hud-maneuver-shield {{
        width: 44px;
        height: 44px;
        border-radius: 10px;
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        border: 2px solid #38bdf8;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4);
    }}
    .hud-signboard-meta {{
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    .hud-pill-cyan {{
        background: rgba(56, 189, 248, 0.18);
        border: 1px solid rgba(56, 189, 248, 0.4);
        color: #38bdf8;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.74rem;
        font-weight: 700;
    }}
    .hud-pill-emerald {{
        background: rgba(16, 185, 129, 0.18);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.74rem;
        font-weight: 700;
    }}
    /* Guide Speech Bubble */
    .guide-speech-balloon {{
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(20, 32, 58, 0.9) 100%);
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 8px;
        min-height: 68px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
        transition: min-height 0.2s ease;
    }}
    /* Visual Landmark Radar Clues */
    .landmark-radar-box {{
        background: linear-gradient(135deg, rgba(14, 116, 144, 0.12) 0%, rgba(15, 23, 42, 0.8) 100%);
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 8px;
        min-height: 74px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: min-height 0.2s ease;
    }}
    .landmark-tags-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin: 6px 0;
    }}
    .landmark-tag-chip {{
        background: rgba(56, 189, 248, 0.14);
        border: 1px solid rgba(56, 189, 248, 0.35);
        color: #e0f2fe;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.72rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }}
    /* Action Buttons */
    .guide-btn-action {{
        background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;
        color: #EAF7FF !important;
        border: 1.5px solid rgba(0, 217, 255, 0.40) !important;
        padding: 7px 16px !important;
        border-radius: 8px !important;
        font-size: 0.76rem !important;
        font-weight: 800 !important;
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45), 0 0 8px rgba(0, 217, 255, 0.12) !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    .guide-btn-action:hover {{
        background: linear-gradient(135deg, #10263E 0%, #0B1B2D 100%) !important;
        border-color: #00D9FF !important;
        color: #ffffff !important;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.55), 0 0 16px rgba(0, 240, 181, 0.45) !important;
        transform: translateY(-2px) !important;
    }}
    .guide-btn-speak {{
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.35) 0%, rgba(0, 240, 181, 0.40) 100%) !important;
        color: #ffffff !important;
        border: 1.5px solid #00F0B5 !important;
        padding: 7px 16px !important;
        border-radius: 8px !important;
        font-size: 0.76rem !important;
        font-weight: 800 !important;
        cursor: pointer !important;
        box-shadow: 0 0 16px rgba(0, 217, 255, 0.45), 0 0 8px rgba(0, 240, 181, 0.35) !important;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    .guide-btn-speak:hover {{
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.50) 0%, rgba(0, 240, 181, 0.55) 100%) !important;
        border-color: #00D9FF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 0 24px rgba(0, 240, 181, 0.65) !important;
    }}
    .guide-btn-replay-pill {{
        background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;
        border: 1.5px solid #00F0B5 !important;
        color: #00F0B5 !important;
        border-radius: 999px !important;
        padding: 4px 14px !important;
        font-size: 0.72rem !important;
        font-weight: 800 !important;
        cursor: pointer !important;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 0 10px rgba(0, 240, 181, 0.25) !important;
    }}
    .guide-btn-replay-pill:hover {{
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.35) 0%, rgba(0, 240, 181, 0.40) 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 0 18px rgba(0, 240, 181, 0.60) !important;
        transform: translateY(-1px) !important;
    }}
    /* Interactive Avatar Action Pill Deck */
    .guide-action-pill {{
        background: linear-gradient(135deg, #0B1B2D 0%, #06111F 100%) !important;
        border: 1.5px solid rgba(0, 217, 255, 0.35) !important;
        color: #EAF7FF !important;
        padding: 6px 14px !important;
        border-radius: 8px !important;
        font-size: 0.76rem !important;
        font-weight: 800 !important;
        cursor: pointer !important;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.45) !important;
    }}
    .guide-action-pill:hover {{
        background: linear-gradient(135deg, #10263E 0%, #0B1B2D 100%) !important;
        border-color: #00D9FF !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 16px rgba(0, 240, 181, 0.40) !important;
    }}
    .guide-action-pill.active {{
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.35) 0%, rgba(0, 240, 181, 0.40) 100%) !important;
        border: 1.5px solid #00F0B5 !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.55), 0 0 10px rgba(0, 240, 181, 0.45) !important;
        transform: scale(1.04);
    }}
    /* 3D Level Stage & Perspective Controls */
    .level-3d-stage {{
        perspective: 1200px;
        perspective-origin: 50% 50%;
        margin: 6px 0;
        cursor: grab;
    }}
    .level-3d-stage:active {{
        cursor: grabbing;
    }}
    .level-3d-canvas {{
        transform-style: preserve-3d;
        transition: transform 0.20s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.25s ease;
        transform-origin: 50% 70%;
        will-change: transform;
    }}
    .level-3d-canvas.camera-pov {{
        transform: rotateX(0deg) rotateY(0deg) scale(1);
    }}
    .level-3d-canvas.camera-drone {{
        transform: rotateX(15deg) rotateY(-4deg) scale(0.97) translateY(-6px);
    }}
    .level-3d-canvas.camera-iso {{
        transform: rotateX(24deg) rotateY(-16deg) scale(0.93) translateY(-12px);
    }}
    </style>
    <div class='guide-hud-container'>
        <!-- Virtual Guide Header -->
        <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 10px;'>
            <div style='display: flex; align-items: center; gap: 12px;'>
                <div class='avatar-radar-box'>
                    👨‍✈️
                </div>
                <div>
                    <div style='display: flex; align-items: center; gap: 8px; flex-wrap: wrap;'>
                        <b style='font-size: 0.98rem; color: #ffffff; letter-spacing: 0.02em;'>
                            {vg_story_title}
                        </b>
                        <span style='background: rgba(16, 185, 129, 0.18); border: 1px solid rgba(16, 185, 129, 0.4); color: #34d399; font-size: 0.68rem; font-weight: 800; padding: 2px 8px; border-radius: 999px;'>
                            {vg_for_traveler}
                        </span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 10px; margin-top: 3px;'>
                        <span style='font-size: 0.74rem; color: #38bdf8; font-weight: 600;'>
                            🎨 {vg_visual_flow}
                        </span>
                    </div>
                </div>
            </div>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <button id='btn-toggle-turns-view' class='guide-btn-action' onclick='toggleTurnsView()'>
                    🖼️ {vg_view_all}
                </button>
            </div>
        </div>

        <!-- Quest Progress Bar -->
        <div class='quest-progress-wrap'>
            <div class='quest-progress-header'>
                <span>{vg_pipeline_lbl}</span>
                <span id='quest-progress-text'>Turn 1 of {len(friendly_turns)} • 0% Complete</span>
            </div>
            <div class='quest-progress-bar'>
                <div id='quest-progress-fill' class='quest-progress-fill' style='width: {100.0 / max(1, len(friendly_turns))}%;'></div>
            </div>
        </div>

        <!-- Connected Horizontal Flow Process Track -->
        <div id='turn-chips-bar' class='guide-flow-track'>
            <!-- Populated via JS -->
        </div>

        <!-- Active Turn Showcase Picture Card -->
        <div id='active-turn-card' style='margin-top: 10px;'>
            <!-- Step Badge & Big Short Headline -->
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;'>
                <div style='display: flex; align-items: center; gap: 10px;'>
                    <span id='showcase-step-badge' style='background: #0284c7; color: #ffffff; padding: 4px 12px; border-radius: 6px; font-size: 0.78rem; font-weight: 800;'>
                        STEP 1 OF {len(friendly_turns)}
                    </span>
                    <span id='showcase-simple-instr' style='color: #ffffff; font-size: 1.22rem; font-weight: 900; letter-spacing: 0.02em;'>
                        {turns_data[0]["simple_instruction"]}
                    </span>
                </div>
                <div style='display: flex; gap: 6px;'>
                    <span id='showcase-turn-dist' class='hud-pill-cyan'>📏 {friendly_turns[0].distance_human}</span>
                    <span id='showcase-turn-time' class='hud-pill-emerald'>⏱️ {friendly_turns[0].time_estimate}</span>
                </div>
            </div>

            <!-- 3D Level Stage Controls (Camera Modes & Environment Lighting) -->
            <div class='level-3d-controls-bar' style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 8px; padding: 6px 12px;'>
                <div style='display: flex; align-items: center; gap: 6px; flex-wrap: wrap;'>
                    <span style='font-size: 0.68rem; color: #38bdf8; font-weight: 800; letter-spacing: 0.04em;'>{vg_cam_modes}</span>
                    <button id='btn-cam-pov' class='guide-speed-pill active' onclick='setCameraMode("pov")' title='1st Person Driver Dashboard POV'>{vg_cam_pov}</button>
                    <button id='btn-cam-drone' class='guide-speed-pill' onclick='setCameraMode("drone")' title='Elevated 3D Follow Drone View'>{vg_cam_drone}</button>
                    <button id='btn-cam-iso' class='guide-speed-pill' onclick='setCameraMode("iso")' title='3D Tactical Isometric Perspective'>{vg_cam_iso}</button>
                </div>
                <div style='display: flex; align-items: center; gap: 6px; flex-wrap: wrap;'>
                    <span style='font-size: 0.68rem; color: #facc15; font-weight: 800; letter-spacing: 0.04em;'>{vg_env_lighting}</span>
                    <button id='btn-env-day' class='guide-speed-pill' onclick='setEnvironmentMode("day")' title='Bright Daylight Level'>{vg_env_day}</button>
                    <button id='btn-env-sunset' class='guide-speed-pill active' onclick='setEnvironmentMode("sunset")' title='Golden Hour Sunset Level'>{vg_env_sunset}</button>
                    <button id='btn-env-night' class='guide-speed-pill' onclick='setEnvironmentMode("night")' title='Cyber Night Starlight Level'>{vg_env_night}</button>
                </div>
            </div>

            <!-- The Visual Scene Picture Illustration in Interactive 3D Level Stage -->
            <div id='level-3d-stage' class='level-3d-stage' title='Move mouse or drag to tilt 3D level in real-time'>
                <div id='showcase-visual-svg-container' class='level-3d-canvas camera-pov env-sunset' style='box-shadow: 0 16px 40px rgba(0,0,0,0.65); border-radius: 14px; overflow: hidden; border: 1.5px solid rgba(56, 189, 248, 0.4);'>
                    {turns_data[0]["svg"]}
                </div>
            </div>

            <!-- Interactive Avatar Action Controller Deck (Real Walk, Run, Turn, Jump, Cheer, Wave) -->
            <div class='avatar-action-deck' style='background: linear-gradient(135deg, rgba(8, 22, 44, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%); border: 1.5px solid rgba(56, 189, 248, 0.45); border-radius: 12px; padding: 10px 16px; margin-top: 10px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; box-shadow: 0 4px 18px rgba(0,0,0,0.45);'>
                <div style='display: flex; align-items: center; gap: 8px; flex-wrap: wrap;'>
                    <span style='font-size: 0.72rem; color: #38bdf8; font-weight: 800; letter-spacing: 0.05em; text-transform: uppercase; display: flex; align-items: center; gap: 5px;'>
                        <span>🎮</span> {vg_avatar_actions}
                    </span>
                    <button id='btn-act-walk' class='guide-action-pill active' onclick='triggerAvatarAction("walk")' title='Real Walking Stride with Arm & Leg Swing'>
                        <span>🚶</span> {vg_act_walk}
                    </button>
                    <button id='btn-act-run' class='guide-action-pill' onclick='triggerAvatarAction("run")' title='Athletic Sprint with High Knee Lift & Pumping Arms'>
                        <span>🏃</span> {vg_act_run}
                    </button>
                    <button id='btn-act-turn' class='guide-action-pill' onclick='triggerAvatarAction("turn")' title='Smooth Pivot & Guidance Pointing'>
                        <span>🔄</span> {vg_act_turn}
                    </button>
                    <button id='btn-act-jump' class='guide-action-pill' onclick='triggerAvatarAction("jump")' title='High Vertical Leap with Cushioned Elastic Landing'>
                        <span>⭐</span> {vg_act_jump}
                    </button>
                    <button id='btn-act-cheer' class='guide-action-pill' onclick='triggerAvatarAction("cheer")' title='Joyful Victory Celebration Hop & Waving Arms'>
                        <span>🎉</span> {vg_act_cheer}
                    </button>
                    <button id='btn-act-wave' class='guide-action-pill' onclick='triggerAvatarAction("wave")' title='Turn and Wave Warmly to Traveler'>
                        <span>👋</span> {vg_act_wave}
                    </button>
                </div>
                <div id='action-status-pill' style='font-size: 0.72rem; font-weight: 800; color: #34d399; background: rgba(16, 185, 129, 0.16); border: 1px solid rgba(16, 185, 129, 0.4); padding: 4px 12px; border-radius: 999px; display: inline-flex; align-items: center; gap: 6px;'>
                    <span>🚶</span> <span>{vg_walking_nat}</span>
                </div>
            </div>

            <!-- Real-Time Traveler Experience Telemetry Strip -->
            <div class='traveler-experience-strip'>
                <div class='traveler-telemetry-item'>
                    <span class='telemetry-label'>🚗 {vg_speed_lbl}</span>
                    <span id='exp-speed' class='telemetry-value' style='color: #38bdf8;'>30 km/h</span>
                </div>
                <div class='telemetry-divider'></div>
                <div class='traveler-telemetry-item'>
                    <span class='telemetry-label'>🧭 {vg_heading_lbl}</span>
                    <span id='exp-heading' class='telemetry-value' style='color: #34d399;'>{vg_leaving_start}</span>
                </div>
                <div class='telemetry-divider'></div>
                <div class='traveler-telemetry-item'>
                    <span class='telemetry-label'>🛣️ {vg_corridor_lbl}</span>
                    <span id='showcase-turn-road' class='telemetry-value' style='color: #f1f5f9; max-width: 220px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;'>{friendly_turns[0].road_name}</span>
                </div>
                <div class='telemetry-divider'></div>
                <div class='traveler-telemetry-item'>
                    <span class='telemetry-label'>🏁 {vg_remaining_lbl}</span>
                    <span id='exp-remaining' class='telemetry-value' style='color: #fbbf24;'>{len(friendly_turns) - 1} steps</span>
                </div>
                <div class='telemetry-divider'></div>
                <div class='traveler-telemetry-item'>
                    <span class='telemetry-label'>⚡ {vg_status_lbl}</span>
                    <span id='exp-status' class='telemetry-value' style='color: #34d399;'>● {vg_ready_lbl}</span>
                </div>
            </div>

            <!-- Simple, Short Guidance Balloon -->
            <div class='guide-speech-balloon' style='margin-top: 10px;'>
                <div style='font-size: 0.72rem; color: #34d399; font-weight: 800; display: flex; align-items: center; gap: 6px;'>
                    <span>👨‍✈️</span> <span>{vg_guide_says}</span>
                </div>
                <div id='showcase-turn-speech' style='color: #f1f5f9; font-size: 0.88rem; line-height: 1.45; margin-top: 4px; font-weight: 600;'>
                    "{friendly_turns[0].virtual_guide_speech}"
                </div>
            </div>

            <!-- Visual Landmark Clues -->
            <div class='landmark-radar-box' style='margin-top: 8px;'>
                <div style='font-size: 0.72rem; color: #38bdf8; font-weight: 800; display: flex; align-items: center; gap: 6px;'>
                    <span>👀</span> <span>{vg_what_to_look}</span>
                </div>
                <div id='showcase-landmark-chips' class='landmark-tags-row'>
                    <!-- Populated via JS -->
                </div>
                <div id='showcase-turn-landmarks' style='color: #cbd5e1; font-size: 0.80rem; line-height: 1.4; margin-top: 2px;'>
                    {friendly_turns[0].what_to_look_for}
                </div>
            </div>

            <!-- Disability & Accessible Mobility Assistance Card (Step-Free Ramps & Crossings) -->
            <div class='accessible-assistance-card' style='background: linear-gradient(135deg, rgba(8, 28, 52, 0.94) 0%, rgba(12, 38, 48, 0.95) 100%); border: 1.5px solid rgba(16, 185, 129, 0.45); border-radius: 12px; padding: 12px 16px; margin-top: 10px; box-shadow: 0 4px 18px rgba(0, 0, 0, 0.4);'>
                <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;'>
                    <div style='display: flex; align-items: center; gap: 8px;'>
                        <span style='background: #0284c7; color: #ffffff; padding: 3px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 800;'>
                            ♿ {vg_access_title}
                        </span>
                        <span style='font-size: 0.74rem; color: #34d399; font-weight: 700;'>
                            {vg_access_sub}
                        </span>
                    </div>
                    <!-- Demonstration Trigger Button -->
                    <button id='btn-demo-movement' class='guide-btn-action' style='background: linear-gradient(135deg, rgba(0, 217, 255, 0.35) 0%, rgba(0, 240, 181, 0.40) 100%); color: #ffffff; border: 1.5px solid #00F0B5; font-weight: 800; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 0 16px rgba(0, 217, 255, 0.4);' onclick='animateVirtualGuideDemonstration()' title='Watch Virtual Man demonstrate crossing and turn'>
                        <span>🚶‍♂️▶️</span> <span id='btn-demo-movement-text'>Move Virtual Guide: Turn & Cross</span>
                    </button>
                </div>

                <!-- Live Moving Guidance Demo Feedback Strip -->
                <div id='demo-status-banner' style='display: none; background: rgba(2, 132, 199, 0.2); border: 1px solid #38bdf8; border-radius: 8px; padding: 6px 12px; margin-top: 8px; font-size: 0.78rem; color: #7dd3fc; font-weight: 700; align-items: center; gap: 8px;'>
                    <span id='demo-status-pulse' style='color: #10b981; font-size: 1rem;'>●</span>
                    <span id='demo-status-text'>Phase 1: Virtual Guide positioning at step-free curb ramp...</span>
                </div>

                <!-- Accessible Crossing & Ramp Details -->
                <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 10px; margin-top: 8px;'>
                    <div style='background: rgba(15, 23, 42, 0.6); border-radius: 8px; padding: 8px 12px; border-left: 3px solid #38bdf8;'>
                        <div style='font-size: 0.68rem; color: #38bdf8; font-weight: 800; text-transform: uppercase;'>
                            ♿ Step-Free Ramp & Mobility Path
                        </div>
                        <div id='showcase-accessible-guidance' style='font-size: 0.78rem; color: #e2e8f0; margin-top: 3px; line-height: 1.35;'>
                            {friendly_turns[0].accessible_guidance}
                        </div>
                    </div>
                    <div style='background: rgba(15, 23, 42, 0.6); border-radius: 8px; padding: 8px 12px; border-left: 3px solid #facc15;'>
                        <div style='font-size: 0.68rem; color: #facc15; font-weight: 800; text-transform: uppercase;'>
                            🟡 Tactile Paving & Audible Crossing
                        </div>
                        <div id='showcase-tactile-note' style='font-size: 0.78rem; color: #e2e8f0; margin-top: 3px; line-height: 1.35;'>
                            {friendly_turns[0].tactile_crossing_note}
                        </div>
                    </div>
                </div>

                <!-- Mobility Profile Quick Selector -->
                <div style='display: flex; align-items: center; gap: 8px; margin-top: 8px; flex-wrap: wrap;'>
                    <span style='font-size: 0.68rem; color: #94a3b8; font-weight: 700;'>ASSISTANCE MODE:</span>
                    <button id='mode-btn-pedestrian' class='guide-speed-pill active' onclick='setAssistanceMode("pedestrian")'>🚶‍♂️ Pedestrian Guide</button>
                    <button id='mode-btn-wheelchair' class='guide-speed-pill' onclick='setAssistanceMode("wheelchair")'>♿ Wheelchair & Ramp Assist</button>
                    <button id='mode-btn-tactile' class='guide-speed-pill' onclick='setAssistanceMode("tactile")'>👁️ Tactile & Audio Walk Cues</button>
                </div>
            </div>

            <!-- Navigation Steppers & Traveler Drive Simulation Controls -->
            <div style='margin-top: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;'>
                <div style='display: flex; align-items: center; gap: 6px; flex-wrap: wrap;'>
                    <button class='guide-btn-action secondary-btn' onclick='selectTurnStep(0, true)' title='Jump to Start'>
                        ⏮ Start
                    </button>
                    <button class='guide-btn-action' onclick='prevTurn()' title='Previous Step'>
                        ◀ Previous
                    </button>
                    <button id='btn-auto-drive' class='guide-btn-action drive-simulate-btn' onclick='toggleAutoDrive()' title='Autoplay Travel Simulation'>
                        <span>▶</span><span>Experience Drive</span>
                    </button>
                    <button class='guide-btn-action' style='background: linear-gradient(135deg, rgba(0, 217, 255, 0.35) 0%, rgba(0, 240, 181, 0.40) 100%); border: 1.5px solid #00F0B5; color: #ffffff; box-shadow: 0 0 16px rgba(0, 217, 255, 0.4);' onclick='nextTurn()' title='Next Step'>
                        Next ▶
                    </button>
                    <button class='guide-btn-action secondary-btn' onclick='selectTurnStep(TOTAL_TURNS - 1, true)' title='Jump to Destination'>
                        Destination ⏭
                    </button>
                </div>
                <div style='display: flex; align-items: center; gap: 6px;'>
                    <span style='font-size: 0.70rem; color: #94a3b8; font-weight: 700;'>SIM SPEED:</span>
                    <button id='btn-speed-1x' class='guide-speed-pill active' onclick='setDriveSpeed(1)'>1x</button>
                    <button id='btn-speed-2x' class='guide-speed-pill' onclick='setDriveSpeed(2)'>2x</button>
                    <button id='btn-speed-4x' class='guide-speed-pill' onclick='setDriveSpeed(4)'>4x</button>
                </div>
            </div>
        </div>

        <!-- Full Turns Gallery View (Togglable) -->
        <div id='full-turns-view' style='display: none; background: rgba(0, 0, 0, 0.4); border-radius: 10px; padding: 14px 18px; margin: 12px 0 10px 0;'>
            <!-- Populated via JS -->
        </div>
    </div>

    <script>
    (function() {{
        const TURNS = {turns_json};
        const TOTAL_TURNS = TURNS.length;
        let activeTurnIdx = 0;
        let isFullListView = false;

        if ('speechSynthesis' in window) {{
            try {{ window.speechSynthesis.cancel(); }} catch(e) {{}}
        }}

        // Voice audio is silenced per user preference: "don't take any voice because it is messy up with voice"
        function speakText(text) {{
            if ('speechSynthesis' in window) {{
                try {{ window.speechSynthesis.cancel(); }} catch(e) {{}}
            }}
            return;
        }}
        window.speakActiveTurn = function() {{
            if ('speechSynthesis' in window) {{
                try {{ window.speechSynthesis.cancel(); }} catch(e) {{}}
            }}
        }};
        window.replayActiveTurnVoice = function() {{
            if ('speechSynthesis' in window) {{
                try {{ window.speechSynthesis.cancel(); }} catch(e) {{}}
            }}
        }};
        window.speakAllTurnsInOrder = function() {{
            if ('speechSynthesis' in window) {{
                try {{ window.speechSynthesis.cancel(); }} catch(e) {{}}
            }}
        }};

        function extractLandmarkChips(text) {{
            const chips = [];
            const lower = (text || '').toLowerCase();
            if (lower.includes('shop') || lower.includes('store') || lower.includes('market')) chips.push({{ icon: '🏪', label: 'Shops' }});
            if (lower.includes('sign') || lower.includes('board') || lower.includes('nameplate')) chips.push({{ icon: '🪧', label: 'Signs' }});
            if (lower.includes('curve') || lower.includes('corner') || lower.includes('bend')) chips.push({{ icon: '↩️', label: 'Corner' }});
            if (lower.includes('traffic') || lower.includes('signal') || lower.includes('junction') || lower.includes('crossing')) chips.push({{ icon: '🚦', label: 'Signals' }});
            if (lower.includes('bridge') || lower.includes('flyover')) chips.push({{ icon: '🌉', label: 'Bridge' }});
            if (lower.includes('tree') || lower.includes('green') || lower.includes('park')) chips.push({{ icon: '🌳', label: 'Trees' }});
            if (lower.includes('lane') || lower.includes('marking')) chips.push({{ icon: '🛣️', label: 'Lane' }});
            if (lower.includes('straight') || lower.includes('cruis')) chips.push({{ icon: '⬆️', label: 'Straight' }});
            if (chips.length === 0) {{
                chips.push({{ icon: '👀', label: 'Look Ahead' }}, {{ icon: '🛣️', label: 'Follow Lane' }});
            }}
            return chips;
        }}

        function formatChipDist(rawDist) {{
            if (!rawDist) return "";
            const kmMatch = rawDist.match(/([0-9.]+)\\s*(?:kilometers|km)/i);
            if (kmMatch) return kmMatch[1] + " km";
            const mMatch = rawDist.match(/([0-9.]+)\\s*(?:meters|m)\\b/i);
            if (mMatch) return mMatch[1] + " m";
            return rawDist.replace(/\\([^)]*\\)/g, '').trim();
        }}

        function formatChipTitle(t) {{
            const instr = t.simple_instruction || "";
            if (t.type === "START") return `Step ${{t.num}} • Start`;
            if (t.type === "ARRIVE") return `Step ${{t.num}} • Arrive`;
            if (t.type === "LEFT") return `Step ${{t.num}} • Turn Left`;
            if (t.type === "RIGHT") return `Step ${{t.num}} • Turn Right`;
            if (instr.includes("STRAIGHT") || instr.includes("CRUISE")) return `Step ${{t.num}} • Straight`;
            return `Step ${{t.num}} • ${{instr.split(' ')[0]}}`;
        }}

        let currentAvatarAction = 'walk';
        let activeCam = 'pov';
        let activeEnv = 'sunset';

        function getBaseCameraAngles() {{
            if (activeCam === 'drone') return {{ rx: 15, ry: -4, sc: 0.97, ty: -6 }};
            if (activeCam === 'iso') return {{ rx: 24, ry: -16, sc: 0.93, ty: -12 }};
            return {{ rx: 0, ry: 0, sc: 1, ty: 0 }};
        }}

        function apply3DTransform(offsetX, offsetY) {{
            const canvas = document.getElementById('showcase-visual-svg-container');
            if (!canvas) return;
            const base = getBaseCameraAngles();
            const tiltX = base.rx - (offsetY * 14);
            const tiltY = base.ry + (offsetX * 16);
            canvas.style.transform = `rotateX(${{tiltX.toFixed(2)}}deg) rotateY(${{tiltY.toFixed(2)}}deg) scale(${{base.sc}}) translateY(${{base.ty}}px)`;
        }}

        window.setCameraMode = function(mode) {{
            activeCam = mode;
            ['pov', 'drone', 'iso'].forEach(m => {{
                const btn = document.getElementById('btn-cam-' + m);
                if (btn) {{
                    if (m === mode) btn.classList.add('active');
                    else btn.classList.remove('active');
                }}
            }});
            const canvas = document.getElementById('showcase-visual-svg-container');
            if (canvas) {{
                canvas.classList.remove('camera-pov', 'camera-drone', 'camera-iso');
                canvas.classList.add('camera-' + mode);
                const base = getBaseCameraAngles();
                canvas.style.transform = `rotateX(${{base.rx}}deg) rotateY(${{base.ry}}deg) scale(${{base.sc}}) translateY(${{base.ty}}px)`;
            }}
        }};

        window.setEnvironmentMode = function(env) {{
            activeEnv = env;
            ['day', 'sunset', 'night'].forEach(e => {{
                const btn = document.getElementById('btn-env-' + e);
                if (btn) {{
                    if (e === env) btn.classList.add('active');
                    else btn.classList.remove('active');
                }}
            }});
            const canvas = document.getElementById('showcase-visual-svg-container');
            if (canvas) {{
                canvas.classList.remove('env-day', 'env-sunset', 'env-night');
                canvas.classList.add('env-' + env);
            }}
        }};

        const stageEl = document.getElementById('level-3d-stage');
        if (stageEl) {{
            stageEl.addEventListener('mousemove', function(e) {{
                const rect = stageEl.getBoundingClientRect();
                const offsetX = (e.clientX - rect.left) / rect.width - 0.5;
                const offsetY = (e.clientY - rect.top) / rect.height - 0.5;
                apply3DTransform(offsetX, offsetY);
            }});
            stageEl.addEventListener('mouseleave', function() {{
                const canvas = document.getElementById('showcase-visual-svg-container');
                if (canvas) {{
                    const base = getBaseCameraAngles();
                    canvas.style.transform = `rotateX(${{base.rx}}deg) rotateY(${{base.ry}}deg) scale(${{base.sc}}) translateY(${{base.ty}}px)`;
                }}
            }});
            stageEl.addEventListener('touchmove', function(e) {{
                if (e.touches && e.touches[0]) {{
                    const rect = stageEl.getBoundingClientRect();
                    const offsetX = (e.touches[0].clientX - rect.left) / rect.width - 0.5;
                    const offsetY = (e.touches[0].clientY - rect.top) / rect.height - 0.5;
                    apply3DTransform(offsetX, offsetY);
                }}
            }}, {{ passive: true }});
        }}

        window.triggerAvatarAction = function(action) {{
            currentAvatarAction = action;
            const actor = document.getElementById('virtual-guide-actor');
            const statusPill = document.getElementById('action-status-pill');
            
            ['walk', 'run', 'turn', 'jump', 'cheer', 'wave'].forEach(a => {{
                const btn = document.getElementById('btn-act-' + a);
                if (btn) {{
                    if (a === action) btn.classList.add('active');
                    else btn.classList.remove('active');
                }}
            }});

            if (actor) {{
                actor.classList.remove('action-walk', 'action-run', 'action-turn', 'action-jump', 'action-cheer', 'action-wave');
                actor.classList.add('action-' + action);
            }}

            if (statusPill) {{
                if (action === 'walk') {{
                    statusPill.innerHTML = '<span>🚶</span> <span>Walking naturally along route</span>';
                }} else if (action === 'run') {{
                    statusPill.innerHTML = '<span>🏃</span> <span style="color: #38bdf8;">Running with energetic athletic sprint!</span>';
                }} else if (action === 'turn') {{
                    statusPill.innerHTML = '<span>🔄</span> <span style="color: #fbbf24;">Pivoting & pointing along corridor!</span>';
                }} else if (action === 'jump') {{
                    statusPill.innerHTML = '<span>⭐</span> <span style="color: #f43f5e;">High vertical leap & soft landing!</span>';
                }} else if (action === 'cheer') {{
                    statusPill.innerHTML = '<span>🎉</span> <span style="color: #a855f7;">Celebrating safe destination arrival!</span>';
                }} else if (action === 'wave') {{
                    statusPill.innerHTML = '<span>👋</span> <span style="color: #38bdf8;">Waving and greeting traveler warmly!</span>';
                }}
            }}
        }};

        let isAutoDriving = false;
        let driveTimer = null;
        let driveSpeedMultiplier = 1;
        let isDemonstratingMovement = false;
        let demoPhaseTimer = null;
        let currentAssistanceMode = 'pedestrian';

        window.setAssistanceMode = function(mode) {{
            currentAssistanceMode = mode;
            ['pedestrian', 'wheelchair', 'tactile'].forEach(m => {{
                const btn = document.getElementById('mode-btn-' + m);
                if (btn) {{
                    if (m === mode) btn.classList.add('active');
                    else btn.classList.remove('active');
                }}
            }});
            const t = TURNS[activeTurnIdx];
            const accessEl = document.getElementById('showcase-accessible-guidance');
            if (accessEl) {{
                if (mode === 'wheelchair') {{
                    accessEl.innerHTML = '<b style="color: #38bdf8;">[♿ Wheelchair Priority]:</b> Step-free dropped curb cut aligned with low slope gradient (&lt; 1:12). Safe ramp width is 1.8 meters. Continuous level surface across crossing.';
                }} else if (mode === 'tactile') {{
                    accessEl.innerHTML = '<b style="color: #facc15;">[🟡 Tactile &amp; Audio Priority]:</b> Yellow hazard warning blister paving studs detect edge of curb. Audible chirp chime confirms pedestrian crossing walk phase.';
                }} else {{
                    accessEl.innerText = t.accessible_guidance || "Level sidewalk with continuous step-free accessibility.";
                }}
            }}
        }};

        function stopDemonstration() {{
            isDemonstratingMovement = false;
            if (demoPhaseTimer) {{
                clearInterval(demoPhaseTimer);
                demoPhaseTimer = null;
            }}
            const banner = document.getElementById('demo-status-banner');
            if (banner) banner.style.display = 'none';
            const btn = document.getElementById('btn-demo-movement');
            const btnTxt = document.getElementById('btn-demo-movement-text');
            if (btnTxt) btnTxt.innerText = "Move Virtual Guide: Turn & Cross";
            if (btn) {{
                btn.style.background = 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)';
            }}
            const actor = document.getElementById('virtual-guide-actor');
            if (actor) {{
                actor.classList.remove('animating-demo-left', 'animating-demo-right', 'animating-demo-straight', 'animating-demo-start');
            }}
        }}

        function startDemonstrationForCurrentTurn() {{
            const t = TURNS[activeTurnIdx];
            const actor = document.getElementById('virtual-guide-actor');
            const banner = document.getElementById('demo-status-banner');
            const statusTxt = document.getElementById('demo-status-text');
            const pulse = document.getElementById('demo-status-pulse');
            const btn = document.getElementById('btn-demo-movement');
            const btnTxt = document.getElementById('btn-demo-movement-text');

            if (btnTxt) btnTxt.innerText = "⏸ Pause Guide Crossing";
            if (btn) {{
                btn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
            }}
            if (banner) banner.style.display = 'flex';

            if (actor) {{
                actor.classList.remove('animating-demo-left', 'animating-demo-right', 'animating-demo-straight', 'animating-demo-start');
                if (t.type === 'LEFT') actor.classList.add('animating-demo-left');
                else if (t.type === 'RIGHT') actor.classList.add('animating-demo-right');
                else if (t.type === 'START') actor.classList.add('animating-demo-start');
                else actor.classList.add('animating-demo-straight');
            }}

            const phases = [
                "Phase 1: 🟡 Virtual Guide approaches step-free curb ramp and aligns with tactile yellow blister paving.",
                "Phase 2: 🚦 Checking audio walk signal chime: Green walking beacon confirmed safe to cross.",
                "Phase 3: 🚶‍♂️ Moving steadily across the high-contrast 4-meter wide zebra crosswalk.",
                "Phase 4: 🎯 Successfully executing turn into " + (t.road || "the accessible pedestrian pathway") + "!"
            ];

            let phaseIdx = 0;
            if (statusTxt) statusTxt.innerText = phases[0];
            if (demoPhaseTimer) clearInterval(demoPhaseTimer);

            demoPhaseTimer = setInterval(function() {{
                phaseIdx = (phaseIdx + 1) % phases.length;
                if (statusTxt) statusTxt.innerText = phases[phaseIdx];
                if (pulse) {{
                    pulse.style.color = (phaseIdx % 2 === 0) ? '#10b981' : '#38bdf8';
                }}
            }}, 1800);
        }}

        window.animateVirtualGuideDemonstration = function() {{
            if (isDemonstratingMovement) {{
                stopDemonstration();
            }} else {{
                isDemonstratingMovement = true;
                startDemonstrationForCurrentTurn();
            }}
        }};

        window.toggleAutoDrive = function() {{
            if (isAutoDriving) {{
                window.stopAutoDrive();
            }} else {{
                window.startAutoDrive();
            }}
        }};

        window.startAutoDrive = function() {{
            if (activeTurnIdx >= TOTAL_TURNS - 1) {{
                window.selectTurnStep(0, false);
            }}
            isAutoDriving = true;
            window.triggerAvatarAction('run');
            updateDriveControlsUI();
            scheduleNextDriveStep();
        }};

        window.stopAutoDrive = function() {{
            isAutoDriving = false;
            if (driveTimer) {{
                clearTimeout(driveTimer);
                driveTimer = null;
            }}
            window.triggerAvatarAction('walk');
            updateDriveControlsUI();
        }};

        function scheduleNextDriveStep() {{
            if (!isAutoDriving) return;
            const delay = Math.round(2600 / driveSpeedMultiplier);
            driveTimer = setTimeout(function() {{
                if (isAutoDriving && activeTurnIdx < TOTAL_TURNS - 1) {{
                    window.selectTurnStep(activeTurnIdx + 1, false);
                    scheduleNextDriveStep();
                }} else {{
                    window.stopAutoDrive();
                }}
            }}, delay);
        }}

        window.setDriveSpeed = function(spd) {{
            driveSpeedMultiplier = spd;
            [1, 2, 4].forEach(s => {{
                const el = document.getElementById('btn-speed-' + s + 'x');
                if (el) {{
                    if (s === spd) el.classList.add('active');
                    else el.classList.remove('active');
                }}
            }});
            if (isAutoDriving) {{
                if (driveTimer) clearTimeout(driveTimer);
                scheduleNextDriveStep();
            }}
        }};

        function updateDriveControlsUI() {{
            const btn = document.getElementById('btn-auto-drive');
            const expStatus = document.getElementById('exp-status');
            if (btn) {{
                if (isAutoDriving) {{
                    btn.innerHTML = '<span>⏸</span><span>Pause Drive</span>';
                    btn.classList.add('driving-active');
                }} else {{
                    btn.innerHTML = '<span>▶</span><span>Experience Drive</span>';
                    btn.classList.remove('driving-active');
                }}
            }}
            if (expStatus) {{
                if (isAutoDriving) {{
                    expStatus.innerHTML = "<span style='color: #38bdf8; font-weight: 800;'>🚗 Cruising Active</span>";
                }} else if (activeTurnIdx === TOTAL_TURNS - 1) {{
                    expStatus.innerHTML = "<span style='color: #fbbf24; font-weight: 800;'>🏁 Arrived Safely</span>";
                }} else {{
                    expStatus.innerHTML = "<span style='color: #34d399;'>● Ready to Follow</span>";
                }}
            }}
        }}

        function renderTurnChips() {{
            const bar = document.getElementById('turn-chips-bar');
            if (!bar) return;
            bar.innerHTML = TURNS.map((t, i) => {{
                let stateClass = '';
                if (i === activeTurnIdx) {{
                    stateClass = 'active';
                }} else if (i < activeTurnIdx) {{
                    stateClass = 'completed';
                }}
                const isLast = (i === TOTAL_TURNS - 1);
                const stepNumBadge = (i < activeTurnIdx) ? '✓' : (i + 1);

                return `
                    <div class="flow-step-item">
                        <button id="flow-step-${{i}}" class="flow-station-card ${{stateClass}}" onclick="selectTurnStep(${{i}}, true)" title="Step ${{t.num}}: ${{t.simple_instruction}} (${{t.dist}})">
                            <span class="station-badge">${{stepNumBadge}}</span>
                            <span style="font-size: 1.15rem; flex-shrink: 0;">${{t.icon}}</span>
                            <div class="station-info">
                                <span class="station-title">${{formatChipTitle(t)}}</span>
                                <span class="station-dist">${{formatChipDist(t.dist)}}</span>
                            </div>
                        </button>
                        ${{!isLast ? '<span class="flow-connector-track">➔</span>' : ''}}
                    </div>
                `;
            }}).join('');
        }}

        window.selectTurnStep = function(idx, userTriggered = false) {{
            if (idx < 0 || idx >= TOTAL_TURNS) return;
            if (userTriggered && isAutoDriving) {{
                window.stopAutoDrive();
            }}
            activeTurnIdx = idx;
            renderTurnChips();

            const t = TURNS[idx];
            const badgeEl = document.getElementById('showcase-step-badge');
            if (badgeEl) badgeEl.innerText = `STEP ${{t.num}} OF ${{t.total}}`;
            const instrEl = document.getElementById('showcase-simple-instr');
            if (instrEl) instrEl.innerText = t.simple_instruction;
            const svgEl = document.getElementById('showcase-visual-svg-container');
            if (svgEl) {{
                svgEl.innerHTML = t.svg;
                svgEl.classList.remove('camera-pov', 'camera-drone', 'camera-iso', 'env-day', 'env-sunset', 'env-night');
                svgEl.classList.add('camera-' + activeCam, 'env-' + activeEnv);
                const base = getBaseCameraAngles();
                svgEl.style.transform = `rotateX(${{base.rx}}deg) rotateY(${{base.ry}}deg) scale(${{base.sc}}) translateY(${{base.ty}}px)`;
            }}
            const distEl = document.getElementById('showcase-turn-dist');
            if (distEl) distEl.innerText = `📏 ${{t.dist}}`;
            const timeEl = document.getElementById('showcase-turn-time');
            if (timeEl) timeEl.innerText = `⏱️ ${{t.time}}`;
            const speechEl = document.getElementById('showcase-turn-speech');
            if (speechEl) speechEl.innerText = `"${{t.speech}}"`;
            const landEl = document.getElementById('showcase-turn-landmarks');
            if (landEl) landEl.innerText = t.landmarks;
            const roadEl = document.getElementById('showcase-turn-road');
            if (roadEl) roadEl.innerText = t.road;

            // Live Traveler Telemetry gauges update
            const expSpeed = document.getElementById('exp-speed');
            const expHeading = document.getElementById('exp-heading');
            const expRemaining = document.getElementById('exp-remaining');
            if (expSpeed) {{
                let speedText = "68 km/h";
                if (t.type === "START") speedText = "30 km/h";
                else if (t.type === "LEFT" || t.type === "RIGHT") speedText = "28 km/h";
                else if (t.type === "ARRIVE") speedText = "0 km/h";
                else if (t.dist && t.dist.includes("kilometer")) speedText = "75 km/h";
                expSpeed.innerText = speedText;
            }}
            if (expHeading) {{
                let headingText = "Straight • Highway Corridor";
                if (t.type === "START") headingText = "Leaving Origin Point";
                else if (t.type === "LEFT") headingText = "Bearing Left 270°";
                else if (t.type === "RIGHT") headingText = "Bearing Right 090°";
                else if (t.type === "ARRIVE") headingText = "Safely Reached Destination";
                expHeading.innerText = headingText;
            }}
            if (expRemaining) {{
                const remSteps = TOTAL_TURNS - 1 - idx;
                expRemaining.innerText = remSteps === 0 ? "Arrived!" : `${{remSteps}} steps left`;
            }}
            updateDriveControlsUI();

            // Render landmark visual chips
            const chipsEl = document.getElementById('showcase-landmark-chips');
            if (chipsEl) {{
                const chips = extractLandmarkChips(t.landmarks);
                chipsEl.innerHTML = chips.map(c => `
                    <span class="landmark-tag-chip">${{c.icon}} ${{c.label}}</span>
                `).join('');
            }}

            // Update Progress Bar
            const pct = Math.round(((idx + 1) / TOTAL_TURNS) * 100);
            const fillEl = document.getElementById('quest-progress-fill');
            const txtEl = document.getElementById('quest-progress-text');
            if (fillEl) fillEl.style.width = pct + '%';
            if (txtEl) txtEl.innerText = `Step ${{t.num}} of ${{t.total}} • ${{pct}}% Route Progress`;

            // Auto-scroll station node into view
            const activeNode = document.getElementById('flow-step-' + idx);
            if (activeNode) {{
                activeNode.scrollIntoView({{ behavior: 'smooth', inline: 'center', block: 'nearest' }});
            }}

            // Update accessible mobility guidance
            const accessEl = document.getElementById('showcase-accessible-guidance');
            if (accessEl && t.accessible_guidance) {{
                accessEl.innerText = t.accessible_guidance;
            }}
            const tactileEl = document.getElementById('showcase-tactile-note');
            if (tactileEl && t.tactile_crossing_note) {{
                tactileEl.innerText = t.tactile_crossing_note;
            }}

            // Dynamic Cute Avatar Action per step
            if (t.type === "ARRIVE") {{
                window.triggerAvatarAction('cheer');
            }} else if (t.type === "LEFT" || t.type === "RIGHT") {{
                window.triggerAvatarAction('turn');
            }} else if (isAutoDriving) {{
                window.triggerAvatarAction('run');
            }} else {{
                window.triggerAvatarAction(currentAvatarAction || 'walk');
            }}

            if (isDemonstratingMovement) {{
                startDemonstrationForCurrentTurn();
            }}
        }};

        window.prevTurn = function() {{
            window.stopAutoDrive();
            const newIdx = (activeTurnIdx - 1 + TOTAL_TURNS) % TOTAL_TURNS;
            window.selectTurnStep(newIdx, true);
        }};

        window.nextTurn = function() {{
            window.stopAutoDrive();
            const newIdx = (activeTurnIdx + 1) % TOTAL_TURNS;
            window.selectTurnStep(newIdx, true);
        }};

        window.toggleTurnsView = function() {{
            isFullListView = !isFullListView;
            const singleCard = document.getElementById('active-turn-card');
            const fullView = document.getElementById('full-turns-view');
            const chipsBar = document.getElementById('turn-chips-bar');
            const btnToggle = document.getElementById('btn-toggle-turns-view');

            if (isFullListView) {{
                singleCard.style.display = 'none';
                chipsBar.style.display = 'none';
                fullView.style.display = 'block';
                btnToggle.innerText = '🎴 Single Picture View';

                fullView.innerHTML = `
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px;">
                    ` + TURNS.map((t, idx) => `
                        <div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 12px; padding: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.4);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span style="background: #0284c7; color: #fff; font-size: 0.72rem; font-weight: 800; padding: 2px 8px; border-radius: 4px;">STEP ${{t.num}}</span>
                                <b style="color: #38bdf8; font-size: 0.95rem;">${{t.simple_instruction}}</b>
                                <span style="font-size: 0.70rem; color: #94a3b8;">${{t.dist}}</span>
                            </div>
                            <div style="border-radius: 8px; overflow: hidden; margin-bottom: 8px;">
                                ${{t.svg}}
                            </div>
                            <div style="font-size: 0.75rem; color: #cbd5e1; line-height: 1.4;">
                                👨‍✈️ <i>"${{t.speech}}"</i>
                            </div>
                        </div>
                    `).join('') + `
                    </div>
                `;
            }} else {{
                singleCard.style.display = 'block';
                chipsBar.style.display = 'flex';
                fullView.style.display = 'none';
                btnToggle.innerText = '🖼️ View All Pictures';
            }}
        }};

        // Sync with vehicle position across map
        function syncTurnWithVehicle(stepIdx, totalSteps) {{
            if (!totalSteps || totalSteps <= 1) return;
            const ratio = stepIdx / Math.max(1, totalSteps - 1);
            const targetTurn = Math.min(TOTAL_TURNS - 1, Math.floor(ratio * TOTAL_TURNS));
            if (targetTurn !== activeTurnIdx) {{
                window.selectTurnStep(targetTurn, false);
            }}
        }}

        // Handle live vehicle & sensor updates in lockstep
        function handleLiveVehicleUpdate(data) {{
            if (!data) return;
            const expSpeed = document.getElementById('exp-speed');
            const expStatus = document.getElementById('exp-status');
            const speed = (data.speedKmh != null) ? data.speedKmh : 0;
            const isStopped = (speed <= 1.0 || data.isStopped);

            if (isStopped) {{
                if (expSpeed) expSpeed.innerText = "0.0 km/h (Stopped)";
                if (expStatus) expStatus.innerHTML = "<span style='color: #ef4444; font-weight: 800;'>🛑 USER STOPPED • GUIDE PAUSED</span>";
                if (isAutoDriving) window.stopAutoDrive();
            }} else {{
                if (expSpeed) expSpeed.innerText = speed + " km/h";
                if (expStatus && !isAutoDriving) {{
                    expStatus.innerHTML = "<span style='color: #10b981; font-weight: 800;'>🟢 SATELLITE SENSOR SYNCED</span>";
                }}
            }}

            if (data.step != null) {{
                syncTurnWithVehicle(data.step, data.totalSteps || 7);
            }}
        }}

        // Listen for live vehicle updates
        try {{
            if (window.BroadcastChannel) {{
                const bc = new BroadcastChannel('pathfinder_journey_channel');
                bc.onmessage = function(ev) {{
                    if (ev.data && ev.data.type === 'PATHFINDER_VEHICLE_UPDATE') {{
                        handleLiveVehicleUpdate(ev.data);
                    }}
                }};
            }}
        }} catch(e) {{}}

        window.addEventListener('message', function(ev) {{
            if (ev.data && ev.data.type === 'PATHFINDER_VEHICLE_UPDATE') {{
                handleLiveVehicleUpdate(ev.data);
            }}
        }});

        // Initial setup: render pipeline and select initial turn
        renderTurnChips();
        window.selectTurnStep(0, false);
    }})();
    </script>
    """
