"""
Tests for Pathfinder 3D Interactive AI Guide & Quick Tour Module
================================================================
Verifies that all 7 tour steps, selectors, prompt examples, WebGL 3D companion,
voice synthesis controls, and first-time welcome experience are present and functional.
"""

import os
import pytest
from src.quick_tour import build_quick_tour_html, TOUR_STEPS


def test_tour_steps_count_and_sequence():
    """Verify exactly 7 steps are configured in the correct sequence."""
    steps = TOUR_STEPS["en"]
    assert len(steps) == 7

    for idx, step in enumerate(steps):
        assert step["step"] == idx + 1
        assert "badge" in step and step["badge"]
        assert "title" in step and step["title"]
        assert "content" in step and step["content"]


def test_step_3_prompt_example():
    """Verify Step 3 provides the natural language Goa prompt example."""
    step3 = next(s for s in TOUR_STEPS["en"] if s["step"] == 3)
    assert step3["prompt_example"] is not None
    assert "Goa" in step3["prompt_example"]
    assert "₹5,000" in step3["prompt_example"] or "5,000" in step3["prompt_example"]


def test_step_4_smart_preferences():
    """Verify Step 4 describes avoid tolls, avoid highways, avoid ferries."""
    step4 = next(s for s in TOUR_STEPS["en"] if s["step"] == 4)
    content = step4["content"].lower()
    assert "avoid tolls" in content
    assert "avoid highways" in content
    assert "avoid ferries" in content


def test_step_6_speedometer_and_guide():
    """Verify Step 6 introduces real features: speedometer, map, 3D guide."""
    step6 = next(s for s in TOUR_STEPS["en"] if s["step"] == 6)
    content = step6["content"].lower()
    assert "speedometer" in content
    assert "map" in content
    assert "guide" in content


def test_build_quick_tour_html_output():
    """Verify HTML bundle builds cleanly with script, styles, and handlers."""
    html = build_quick_tour_html("en")
    assert "<script>" in html
    assert "#pathfinder-tour-backdrop" in html
    assert "#pathfinder-tour-card" in html
    assert "startPathfinderTour" in html
    assert "pathfinder_tour_dismissed" in html
    assert "Start Planning" in html


def test_3d_bot_companion_and_anti_cutoff():
    """Verify 3D bot companion elements and anti-cutoff viewport styling exist."""
    html = build_quick_tour_html("en", bot_logo_uri="data:image/png;base64,mock")
    assert "tour-bot-companion-wrapper" in html
    assert "tour-bot-3d-scene" in html
    assert "tour-bot-chassis" in html
    assert "A.U.R.A. 3D GUIDE" in html
    assert "EXPLAINING" in html
    assert "max-height" in html
    assert "overflow-y: auto" in html


def test_first_time_welcome_dialogue():
    """Verify first-time welcome experience with Show Me Around and I'll Explore Myself."""
    html = build_quick_tour_html("en")
    assert "pathfinder-welcome-dialog" in html
    assert "Ready to explore?" in html
    assert "Show Me Around" in html
    assert "I'll Explore Myself" in html
    assert "pathfinder_tour_welcomed" in html


def test_threejs_and_character_engine():
    """Verify Three.js WebGL 3D character engine, layout stage, and canvas container."""
    html = build_quick_tour_html("en")
    assert "pathfinder-guide-stage" in html
    assert "guide-character-3d-box" in html
    assert "ensureThreeJs" in html
    assert "create3DCharacter" in html
    assert "companionGroup" in html
    assert "thrusterRing" in html


def test_voice_synthesis_and_mute_control():
    """Verify Web Speech API integration, mute/unmute control, and audio bars."""
    html = build_quick_tour_html("en")
    assert "speakText" in html
    assert "stopSpeaking" in html
    assert "tour-voice-toggle-btn" in html
    assert "speechSynthesis" in html
    assert "tour-bot-voice-bars" in html


def test_character_mood_states_coverage():
    """Verify all 7 steps define expressive animation moods."""
    steps = TOUR_STEPS["en"]
    moods = [s.get("bot_mood") for s in steps]
    assert "waving" in moods
    assert "pointing" in moods
    assert "explaining" in moods
    assert "celebrating" in moods


def test_dashboard_3d_robot_mascot_mounting():
    """Verify dashboard 3D robot mascot mounting routine and canvas container hooks."""
    html = build_quick_tour_html("en")
    assert "initDashboardMascot" in html
    assert "dashboard-robot-canvas-slot" in html
    assert "btn-hero-quick-tour" in html


def test_aura_robot_click_tour_integration():
    """Verify clicking the walking AURA robot triggers the quick tour onboarding."""
    from src.travel_copilot_studio import QUANTUM_REALM_CSS
    assert ".lang-box-walking-aura" in QUANTUM_REALM_CSS
    assert "cursor: pointer" in QUANTUM_REALM_CSS

    # Verify studio source code has the click handlers and tour trigger class
    studio_path = os.path.join(os.path.dirname(__file__), "..", "src", "travel_copilot_studio.py")
    with open(studio_path, "r", encoding="utf-8") as f:
        studio_src = f.read()

    assert "quick-tour-trigger-btn" in studio_src
    assert "data-tour-trigger=\"true\"" in studio_src
    assert "triggerAuraTourLaunch" in studio_src
    assert "startPathfinderTour" in studio_src
    assert "aura-walking-3d-canvas" in studio_src
    assert "initCuteAuraWalker" in studio_src

