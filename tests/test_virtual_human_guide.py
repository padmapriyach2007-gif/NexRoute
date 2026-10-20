"""
Automated Test Suite for Always-Visible Human Virtual Guide & Floating Speech Bubbles
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Human-Centric Navigation System

Verifies:
1. Always-visible rendering without dropdown menus or expanders.
2. Realistic human anatomy rendering (cranium, hair, blinking eyes, jacket, sneakers).
3. Natural skeletal animation states (idle, walk, turn, jump, point, arrive).
4. Synchronized route traversal & honest GPS/demo separation.
5. Floating thought/speech bubbles with directional pointer tail.
6. Automatic message dismissal with reading-length duration and rerun deduplication.
7. Centralized navigation event triggers.
8. Responsive layout & minimize/restore toggle (defaulting to visible).
"""

import json
import pytest
from src.virtual_human_guide import (
    HumanGuideState,
    GuideEventType,
    GuideSpeechMessage,
    VirtualHumanGuideController,
    build_always_visible_virtual_guide_html
)


# =============================================================================
# 1. ALWAYS-VISIBLE RENDERING & MINIMIZE CONTROL TESTS
# =============================================================================

def test_guide_renders_always_visible_by_default():
    html = build_always_visible_virtual_guide_html(
        origin_name="Vignan University",
        dest_name="Tenali Junction",
        travel_mode="walking",
        total_distance_m=1200.0,
        current_speed_kmh=4.5
    )
    # Must NOT contain expander or dropdown wrappers
    assert "<details" not in html
    assert "stExpander" not in html
    # Must contain root card and default visible state
    assert 'id="virtual-human-guide-root"' in html
    assert 'class="virtual-human-guide-card"' in html
    assert "guide-minimized" not in html
    # Must have minimize/restore toggle defaulting to minimize action
    assert 'id="btn-guide-toggle-minimize"' in html
    assert "_ Minimize" in html


def test_guide_initializes_with_minimized_parameter():
    html = build_always_visible_virtual_guide_html(
        origin_name="Campus Gate",
        dest_name="Library",
        is_minimized=True
    )
    assert "guide-minimized" in html
    assert "□ Restore" in html


# =============================================================================
# 2. REALISTIC HUMAN ANATOMY & RENDERING ARTIFACT TESTS
# =============================================================================

def test_realistic_human_canvas_and_features():
    html = build_always_visible_virtual_guide_html(
        origin_name="Station",
        dest_name="Terminal"
    )
    # High-resolution 2x retina canvas viewport
    assert 'id="human-guide-canvas"' in html
    assert 'width="280"' in html
    assert 'height="380"' in html

    # Human anatomical rendering keywords in JavaScript renderer
    assert "Cranium" in html or "ellipse(0, 0, 20, 24" in html
    assert "brown hair" in html or "#382216" in html
    assert "Hair fringe" in html or "quadraticCurveTo" in html
    assert "Friendly Approaching Smile" in html or "arc(0, 7, 6" in html
    assert "Navigator technical jacket" in html or "#0284c7" in html
    assert "White collar & zipper line" in html or "#f8fafc" in html
    assert "Glowing Compass Chest Pin" in html or "#38bdf8" in html
    assert "Backpack" in html or "#d97706" in html
    assert "Dark tailored jogger" in html or "#1e293b" in html
    assert "Two-tone Campus Sneaker" in html or "#2563eb" in html
    assert "Sole crisp white" in html or "#ffffff" in html


def test_procedural_eye_blinking():
    html = build_always_visible_virtual_guide_html(
        origin_name="A",
        dest_name="B"
    )
    # Eye blinking timing logic (blinks every ~3.5s for 140ms)
    assert "blinkPhase" in html
    assert "isBlinking" in html
    assert "140" in html


# =============================================================================
# 3. NATURAL SKELETAL ANIMATIONS & STATE TRANSITIONS
# =============================================================================

def test_animation_states_and_functions():
    html = build_always_visible_virtual_guide_html(
        origin_name="A",
        dest_name="B"
    )
    # All 6 core motion states implemented in JS controller
    assert "HumanGuideState" in html
    assert "IDLE" in html
    assert "WALKING" in html
    assert "TURNING_LEFT" in html
    assert "TURNING_RIGHT" in html
    assert "JUMPING" in html
    assert "POINTING" in html
    assert "ARRIVED" in html

    # Motion mechanics: alternating leg swing & arm counter-swing
    assert "leftLegAngle" in html
    assert "rightLegAngle" in html
    assert "leftKneeFlex" in html
    assert "rightKneeFlex" in html
    assert "leftArmAngle" in html
    assert "rightArmAngle" in html

    # Jump physics: parabolic vertical apex and landing compression
    assert "jumpOffset" in html
    assert "jumpPhase" in html

    # Turn coordinate rotation
    assert "turnAngle" in html


# =============================================================================
# 4. FLOATING SPEECH BUBBLES WITH DIRECTED THOUGHT TAIL
# =============================================================================

def test_floating_speech_bubble_structure_and_tail():
    html = build_always_visible_virtual_guide_html(
        origin_name="Hostel",
        dest_name="Main Auditorium"
    )
    # Speech bubble container
    assert 'id="guide-thought-bubble"' in html
    assert 'class="guide-thought-bubble"' in html

    # Thought / speech tail styling pointing directly toward character's head
    assert ".guide-thought-bubble::before" in html
    assert ".guide-thought-bubble::after" in html
    assert "border-right: 12px solid rgba(56, 189, 248, 0.55)" in html

    # Entrance animation and smooth dismiss styling
    assert "speechBubbleFloatIn" in html
    assert "bubble-dismissed" in html

    # Close button & timer display
    assert 'id="bubble-close-btn"' in html
    assert 'id="bubble-timer-text"' in html
    assert 'id="bubble-message-text"' in html


# =============================================================================
# 5. AUTO-DISMISS DURATION & EVENT-DRIVEN MESSAGING TESTS
# =============================================================================

def test_reading_duration_scaling():
    # Short text: clamped to minimum 4.2 seconds (4200 ms)
    short_dur = VirtualHumanGuideController.compute_speech_duration_ms("Turn left.")
    assert short_dur == 4200

    # Medium text: proportional to character count
    med_text = "Continue straight ahead on the main highway for approximately 850 meters."
    med_dur = VirtualHumanGuideController.compute_speech_duration_ms(med_text)
    assert med_dur == len(med_text) * 75
    assert 4200 <= med_dur <= 8500

    # Long text: clamped to maximum 8.5 seconds (8500 ms)
    long_text = "This is a very detailed navigation advisory indicating that the road ahead is undergoing routine maintenance, so please exercise extra caution."
    long_dur = VirtualHumanGuideController.compute_speech_duration_ms(long_text)
    assert long_dur == 8500


def test_event_driven_message_generation():
    events = [
        GuideEventType.WELCOME,
        GuideEventType.NAVIGATION_STARTED,
        GuideEventType.STRAIGHT_SEGMENT,
        GuideEventType.APPROACHING_TURN,
        GuideEventType.TURN_REQUIRED,
        GuideEventType.ROUTE_CHANGED,
        GuideEventType.OFF_ROUTE,
        GuideEventType.GPS_UNAVAILABLE,
        GuideEventType.APPROACHING_DESTINATION,
        GuideEventType.DESTINATION_REACHED,
    ]

    for ev in events:
        msg = VirtualHumanGuideController.generate_event_message(
            event_type=ev,
            road_name="NH 16",
            next_road="Campus Blvd",
            turn_direction="left",
            distance_m=250.0,
            destination_name="Tech Park"
        )
        assert isinstance(msg, GuideSpeechMessage)
        assert len(msg.headline) > 0
        assert len(msg.body_text) > 0
        assert 4200 <= msg.duration_ms <= 8500
        if ev in (GuideEventType.OFF_ROUTE, GuideEventType.GPS_UNAVAILABLE):
            assert msg.is_warning is True


def test_speech_deduplication_on_rerun():
    html = build_always_visible_virtual_guide_html(
        origin_name="A",
        dest_name="B"
    )
    # Deduplication mechanism storing seen message hashes in sessionStorage
    assert "dismissedMessageCache" in html
    assert "sessionStorage" in html


# =============================================================================
# 6. ROUTE TRACKING & HONEST GPS SEPARATION TESTS
# =============================================================================

def test_honest_gps_status_badge():
    # Simulation mode: explicitly labeled as SIMULATED DEMO GUIDANCE
    sim_html = build_always_visible_virtual_guide_html(
        origin_name="A",
        dest_name="B",
        is_live_gps=False
    )
    assert "SIMULATED DEMO GUIDANCE" in sim_html

    # Live GPS mode: labeled as SATELLITE SENSOR ACTIVE
    gps_html = build_always_visible_virtual_guide_html(
        origin_name="A",
        dest_name="B",
        is_live_gps=True
    )
    assert "SATELLITE SENSOR ACTIVE" in gps_html


def test_route_traversal_with_steps():
    steps = [
        {"instruction": "Head north on Station Rd", "distance_m": 200, "direction_type": "START"},
        {"instruction": "Turn right on Grand Trunk Rd", "distance_m": 600, "direction_type": "RIGHT"},
        {"instruction": "Arrive at Vignan University", "distance_m": 100, "direction_type": "ARRIVE"}
    ]
    polyline = [[16.23, 80.55], [16.24, 80.56], [16.25, 80.57]]

    html = build_always_visible_virtual_guide_html(
        origin_name="Station",
        dest_name="Vignan",
        polyline=polyline,
        steps=steps,
        current_step_idx=1
    )
    assert "Station Rd" in html
    assert "Grand Trunk Rd" in html
    assert "Vignan University" in html
    assert "guide-progress-fill" in html


# =============================================================================
# 7. INTEGRATION CHECK IN APP.PY
# =============================================================================

def test_app_py_has_no_expander_for_companion():
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # The expander dropdown that previously hid the companion must be gone
    assert 'with st.expander("🚶‍♂️ Live Virtual Travel Companion' not in content
    assert 'with st.expander("??? ? Live Virtual Travel Companion' not in content

    # build_always_visible_virtual_guide_html must be imported and used
    assert "build_always_visible_virtual_guide_html" in content
    assert "from src.virtual_human_guide import" in content
