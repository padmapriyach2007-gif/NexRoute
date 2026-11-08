"""
Tests for AURA - JARVIS AI Copilot Persistent Voice Session,
Smart Session Toggle, Voice Activity Detection, and Intelligent Voice Interruption.
"""

import pytest
from src.aura_voice_hud import render_jarvis_chatbot_hud_html
from src.aura_command_dispatcher import (
    AuraGlobalCommandDispatcher,
    AuraCommandType,
    AuraExecutionResult
)


def test_persistent_voice_hud_html_controls():
    """Verify that the smart session toggle, end session button, and state badges exist in the HTML."""
    html = render_jarvis_chatbot_hud_html(
        current_lang="en",
        bot_logo_uri="https://example.com/logo.png",
        auto_greeting_text="Good morning, Boss! Welcome to NextRoute. How can I help you?",
        last_response_text="",
        key_prefix="popover_window",
        voice_enabled=True,
        continuous_mode=True
    )
    # Smart Session Toggle button
    assert "btnSessionToggle" in html
    assert "togglePersistentVoiceSession" in html
    assert "START AURA" in html

    # End Session Button
    assert "btnEndSession" in html
    assert "endVoiceSession" in html

    # Status Badge and Waveform
    assert "jarvisStatusBadge" in html
    assert "AURA OFFLINE" in html
    assert "auraJarvisWaveform" in html

    # Persistent State Management
    assert "aura_persistent_voice_state" in html
    assert "setSessionState" in html

    # Intelligent Interruption & VAD
    assert "vadTimeoutMs" in html
    assert "onspeechstart" in html
    assert "stopJarvisSpeech" in html


def test_voice_command_pause_assistant():
    """Verify natural voice command 'pause the assistant' pauses the session."""
    cmd = AuraGlobalCommandDispatcher.parse_and_dispatch("Pause the assistant", {})
    assert cmd.command_type == AuraCommandType.VOICE_CONTROL
    assert cmd.action_name == "pause_voice_session"
    assert cmd.ui_updates.get("aura_voice_session_state") == "PAUSED"
    assert "paused" in cmd.text_response.lower()


def test_voice_command_resume_assistant():
    """Verify natural voice command 'resume listening' resumes the session."""
    cmd = AuraGlobalCommandDispatcher.parse_and_dispatch("Resume listening", {})
    assert cmd.command_type == AuraCommandType.VOICE_CONTROL
    assert cmd.action_name == "resume_voice_session"
    assert cmd.ui_updates.get("aura_voice_session_state") == "LISTENING"
    assert "resumed" in cmd.text_response.lower()


def test_voice_command_end_session():
    """Verify voice command 'end session' or 'aura offline' terminates the session."""
    cmd = AuraGlobalCommandDispatcher.parse_and_dispatch("End voice session", {})
    assert cmd.command_type == AuraCommandType.VOICE_CONTROL
    assert cmd.action_name == "end_voice_session"
    assert cmd.ui_updates.get("aura_voice_session_state") == "STOPPED"


def test_voice_command_vehicle_mode_switching():
    """Verify voice commands change the transportation mode dynamically."""
    cmd_bike = AuraGlobalCommandDispatcher.parse_and_dispatch("Change vehicle mode to bicycle", {})
    assert cmd_bike.command_type == AuraCommandType.ROUTE_ACTION
    assert cmd_bike.action_name == "switch_vehicle_mode"
    assert cmd_bike.ui_updates.get("selected_travel_mode") == "BICYCLE"
    assert cmd_bike.ui_updates.get("routes_generated") is True

    cmd_car = AuraGlobalCommandDispatcher.parse_and_dispatch("Switch mode to car", {})
    assert cmd_car.ui_updates.get("selected_travel_mode") == "CAR"


def test_voice_command_show_alternative_routes():
    """Verify voice command 'show alternative routes' triggers route alternatives."""
    cmd = AuraGlobalCommandDispatcher.parse_and_dispatch("Show me alternative routes", {})
    assert cmd.command_type == AuraCommandType.ROUTE_ACTION
    assert cmd.action_name == "show_alternative_routes"
    assert cmd.ui_updates.get("active_objective") == "all"
    assert cmd.ui_updates.get("routes_generated") is True


def test_voice_command_stop_navigation():
    """Verify voice command 'stop navigation' prompts or clears active trip."""
    cmd = AuraGlobalCommandDispatcher.parse_and_dispatch("Stop navigation", {})
    assert cmd.command_type == AuraCommandType.ROUTE_ACTION
    assert cmd.action_name == "confirm_clear_trip"
    assert cmd.requires_confirmation is True

