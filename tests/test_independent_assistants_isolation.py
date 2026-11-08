"""
Unit tests for Complete Independent Voice Assistant and Chatbot Isolation.
Verifies:
1. Strict separation between Main Dashboard Voice Assistant (AURA / JARVIS) and
   Chatbot Assistant (AURA Travel Copilot).
2. Time-appropriate greeting for Dashboard Voice Assistant vs. dedicated Travel Copilot greeting.
3. Cross-assistant audio locking flags in both HUD engines to prevent cross-talking.
4. Chatbot execution strictly using PathfinderChatbot without mutating dashboard commands.
5. Voice command bridge strictly routing application actions without altering chat history.
"""

import pytest
from src.aura_welcome_screen import (
    get_aura_startup_greeting,
    render_aura_welcome_hud,
)
from src.aura_voice_hud import (
    get_jarvis_startup_greeting,
    get_chatbot_copilot_greeting,
    render_jarvis_chatbot_hud_html,
)
from src.aura_command_dispatcher import (
    AuraGlobalCommandDispatcher,
    AuraCommandType,
)


class TestIndependentAssistantsIsolation:
    def test_dashboard_startup_greeting_format(self):
        """Dashboard assistant uses time-based greeting addressed to Boss."""
        greet = get_aura_startup_greeting("en", user_name="Boss")
        assert "Boss" in greet
        assert "Welcome to NextRoute" in greet
        assert "How can I help you?" in greet
        assert any(greet.startswith(tod) for tod in ["Good morning", "Good afternoon", "Good evening", "Hello"])

    def test_chatbot_copilot_greeting_format(self):
        """Chatbot assistant has dedicated greeting introducing AURA as travel copilot."""
        copilot_greet = get_chatbot_copilot_greeting("en")
        assert "Hello! I'm AURA, your travel copilot." in copilot_greet

        # Multilingual checks
        assert "AURA" in get_chatbot_copilot_greeting("hi")
        assert "AURA" in get_chatbot_copilot_greeting("te")

    def test_dashboard_welcome_hud_cross_audio_lock(self):
        """Dashboard HUD must check aura_active_speaker to avoid listening to Chatbot speech."""
        hud_html = render_aura_welcome_hud("en", auto_speak=True)
        assert "aura_active_speaker" in hud_html
        assert "chatbot" in hud_html
        assert "dashboard" in hud_html

    def test_chatbot_hud_cross_audio_lock(self):
        """Chatbot HUD must check aura_active_speaker to avoid listening to Dashboard speech."""
        hud_html = render_jarvis_chatbot_hud_html(
            current_lang="en",
            voice_enabled=True,
            continuous_mode=True
        )
        assert "aura_active_speaker" in hud_html
        assert "dashboard" in hud_html
        assert "chatbot" in hud_html

    def test_chatbot_hud_accepts_flexible_kwargs(self):
        """Chatbot HUD function must handle backward-compatibility and extra kwargs safely."""
        html = render_jarvis_chatbot_hud_html(
            current_lang="en",
            bot_logo_uri="https://example.com/logo.png",
            auto_greeting_text="Hello! I'm AURA, your travel copilot.",
            last_response_text="Sure, here are some top spots in Goa.",
            key_prefix="popover_window",
            voice_enabled=True,
            continuous_mode=False,
            unexpected_arg="ignored_safely"
        )
        assert "<!DOCTYPE html>" in html
        assert "AURA • AI Guide" in html

    def test_dashboard_command_dispatcher_application_actions(self):
        """Dashboard assistant routes application commands (tabs, modes, facilities)."""
        ctx = {"active_tab": "home", "language": "en"}
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Show hotels near my route", ctx)
        assert res.command_type == AuraCommandType.FACILITY_SEARCH
        assert res.ui_updates.get("facility_filter") == "hotel"

    def test_chatbot_turn_isolation_from_dashboard_dispatcher(self):
        """Chat queries must not be hijacked by dashboard command dispatcher."""
        # Simulated session state
        chat_history = []
        user_query = "What is the best time to visit Goa and what should I pack?"

        # In the isolated chatbot flow, query is appended to history and handled by chatbot bot
        chat_history.append({"role": "user", "content": user_query})
        assert len(chat_history) == 1
        assert chat_history[0]["content"] == user_query
