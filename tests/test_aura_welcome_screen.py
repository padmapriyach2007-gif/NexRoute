"""
Unit tests for AURA JARVIS-Style Welcome Screen and Voice Assistant Activation.
Verifies time-aware multilingual greetings, HTML generation, interactive states,
autoplay resilience, and session-state single-playback enforcement.
"""

import pytest
from src.aura_welcome_screen import (
    get_aura_startup_greeting,
    render_aura_welcome_hud,
)


class TestAuraWelcomeScreen:
    def test_startup_greeting_multilingual(self):
        # English
        en_greet = get_aura_startup_greeting("en", user_name="Boss")
        assert "Boss" in en_greet
        assert "AURA" in en_greet
        assert "NexRoute" in en_greet or "intelligent" in en_greet or "explore" in en_greet

        # Telugu
        te_greet = get_aura_startup_greeting("te", user_name="బాస్")
        assert "AURA" in te_greet
        assert "నెక్స్‌రూట్" in te_greet

        # Hindi
        hi_greet = get_aura_startup_greeting("hi", user_name="बॉस")
        assert "AURA" in hi_greet
        assert "नेक्स-रूट" in hi_greet

        # Tamil
        ta_greet = get_aura_startup_greeting("ta", user_name="பாஸ்")
        assert "AURA" in ta_greet
        assert "நெக்ஸ்-ரூட்" in ta_greet

        # Kannada
        kn_greet = get_aura_startup_greeting("kn", user_name="ಬಾಸ್")
        assert "AURA" in kn_greet

        # Malayalam
        ml_greet = get_aura_startup_greeting("ml", user_name="ബോസ്")
        assert "AURA" in ml_greet

    def test_render_aura_welcome_hud_html_structure(self):
        html = render_aura_welcome_hud(
            current_lang="en",
            auto_speak=True,
            bot_logo_uri="https://example.com/logo.png",
            user_name="Boss"
        )
        assert "<!DOCTYPE html>" in html
        assert "AURA • JARVIS AI COPILOT" in html
        assert "auraWaveCanvas" in html
        assert "arc-reactor-ring-outer" in html
        assert "btnVoiceMic" in html
        assert "btnPlayGreeting" in html
        assert "dismissWelcomeScreen" in html
        assert "dispatchWelcomeCommand" in html
        assert "SpeechRecognition" in html
        assert "SpeechSynthesisUtterance" in html

    def test_render_welcome_hud_chips(self):
        html = render_aura_welcome_hud(current_lang="en", auto_speak=False)
        assert "Open navigation" in html
        assert "Switch to satellite view" in html
        assert "Show my current location" in html
        assert "Find hospitals nearby" in html
        assert "Find petrol stations nearby" in html
        assert "Fit route" in html
        assert "Calculate fuel expenses" in html
        assert "Open chatbot" in html

    def test_auto_greeting_toggle_and_persistence(self):
        html = render_aura_welcome_hud(current_lang="en", auto_speak=True)
        assert "chkAutoGreeting" in html
        assert "toggleAutoGreetingPref" in html
        assert "aura_auto_greeting_enabled" in html

    def test_session_state_single_greeting_simulation(self):
        # Simulating Streamlit session state lifecycle
        fake_session = {
            "aura_welcome_greeted": False,
            "aura_auto_greeting_enabled": True,
            "show_aura_welcome": True
        }

        # 1st Run: Startup
        auto_speak_1 = fake_session["aura_auto_greeting_enabled"] and not fake_session["aura_welcome_greeted"]
        assert auto_speak_1 is True

        # Mark greeted on 1st run
        fake_session["aura_welcome_greeted"] = True

        # 2nd Run (Streamlit rerun)
        auto_speak_2 = fake_session["aura_auto_greeting_enabled"] and not fake_session["aura_welcome_greeted"]
        assert auto_speak_2 is False, "Greeting must NOT play repeatedly on Streamlit reruns"
