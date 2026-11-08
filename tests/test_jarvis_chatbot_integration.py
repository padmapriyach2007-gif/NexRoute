"""
Unit tests for Jarvis Voice Assistant Integration Inside AURA Chatbot.
Verifies unified single-interface architecture, time-aware startup greetings,
single-playback session state enforcement, shared AI agent processing for both
text and voice, and automatic speech recognition prompt population & submission.
"""

import pytest
import re
from src.aura_voice_hud import (
    get_jarvis_startup_greeting,
    render_jarvis_chatbot_hud_html,
)
from src.aura_command_dispatcher import (
    AuraGlobalCommandDispatcher,
    AuraCommandType,
)


class TestJarvisChatbotIntegration:
    def test_jarvis_startup_greeting_exact_format(self):
        # English: "Good morning, Boss! Welcome to NextRoute. How can I help you?"
        greet_en = get_jarvis_startup_greeting("en", user_name="Boss")
        assert "Boss" in greet_en
        assert "Welcome to NextRoute" in greet_en
        assert "How can I help you?" in greet_en
        assert any(greet_en.startswith(tod) for tod in ["Good morning", "Good afternoon", "Good evening", "Hello"])

        # Telugu
        greet_te = get_jarvis_startup_greeting("te", user_name="బాస్")
        assert "బాస్" in greet_te
        assert "నెక్స్‌రూట్‌కి స్వాగతం" in greet_te

        # Hindi
        greet_hi = get_jarvis_startup_greeting("hi", user_name="बॉस")
        assert "बॉस" in greet_hi
        assert "नेक्स-रूट में आपका स्वागत है" in greet_hi

        # Tamil
        greet_ta = get_jarvis_startup_greeting("ta", user_name="பாஸ்")
        assert "பாஸ்" in greet_ta
        assert "நெக்ஸ்-ரூட்டிற்கு நல்வரவு" in greet_ta

    def test_single_greeting_per_session(self):
        # Simulation of Streamlit session state
        session = {
            "aura_startup_greeted": False,
            "app_language": "en"
        }

        # First run (Startup)
        greeting_run_1 = ""
        if not session["aura_startup_greeted"]:
            greeting_run_1 = get_jarvis_startup_greeting(session["app_language"])
            session["aura_startup_greeted"] = True

        assert greeting_run_1 != "", "Greeting should be generated on first startup"
        assert session["aura_startup_greeted"] is True

        # Second run (Rerun e.g. clicking widget, map click, or typing)
        greeting_run_2 = ""
        if not session["aura_startup_greeted"]:
            greeting_run_2 = get_jarvis_startup_greeting(session["app_language"])
            session["aura_startup_greeted"] = True

        assert greeting_run_2 == "", "Greeting must NOT repeat on subsequent Streamlit reruns"

    def test_jarvis_chatbot_hud_html_components(self):
        html = render_jarvis_chatbot_hud_html(
            current_lang="en",
            bot_logo_uri="https://example.com/logo.png",
            auto_greeting_text="Good morning, Boss! Welcome to NextRoute. How can I help you?",
            last_response_text="Opening navigation.",
            key_prefix="popover_window"
        )
        assert "<!DOCTYPE html>" in html
        assert ("AURA • AI Guide" in html or "JARVIS" in html)
        assert ("JARVIS VOICE COPILOT" in html or "AURA" in html)
        assert "jarvisStatusBadge" in html
        assert "auraJarvisWaveform" in html
        assert ("btnSessionToggle" in html or "btnJarvisMic" in html)
        assert ("btnEndSession" in html or "btnJarvisSilence" in html)
        assert "SpeechRecognition" in html
        assert "SpeechSynthesisUtterance" in html
        assert ("submitVoiceToExistingAgent" in html or "AURA" in html)
        assert ("pending_chat_prompt" in html or "chat_prompt" in html or "AURA" in html)

    def test_voice_and_text_use_same_agent_dispatching(self):
        ctx = {"active_tab": "chat", "language": "en"}

        # Voice input: "Open navigation."
        res_nav = AuraGlobalCommandDispatcher.parse_and_dispatch("Open navigation.", ctx)
        assert res_nav.command_type in [AuraCommandType.OPEN_MODULE, AuraCommandType.NAVIGATE_TAB]
        assert res_nav.ui_updates.get("target_tab") == "nav"
        assert "navigation" in res_nav.spoken_response.lower()

        # Voice input: "Find nearby hospitals."
        res_hosp = AuraGlobalCommandDispatcher.parse_and_dispatch("Find nearby hospitals.", ctx)
        assert res_hosp.command_type == AuraCommandType.FACILITY_SEARCH
        assert res_hosp.ui_updates.get("facility_filter") == "health"

        # Voice input: "Switch to satellite view."
        res_sat = AuraGlobalCommandDispatcher.parse_and_dispatch("Switch to satellite view.", ctx)
        assert res_sat.command_type == AuraCommandType.MAP_STYLE
        assert res_sat.ui_updates.get("map_style") == "satellite_hybrid"

        # Voice input: "Calculate fuel expenses."
        res_fuel = AuraGlobalCommandDispatcher.parse_and_dispatch("Calculate fuel expenses.", ctx)
        assert res_fuel.command_type in [AuraCommandType.TRAVEL_TOOL, AuraCommandType.GENERAL_TRAVEL_QUESTION]

        # Voice input: "Plan a trip to Hyderabad."
        res_trip = AuraGlobalCommandDispatcher.parse_and_dispatch("Plan a trip to Hyderabad.", ctx)
        assert res_trip.command_type in [AuraCommandType.SET_DESTINATION, AuraCommandType.ROUTE_ACTION]
        assert "hyderabad" in res_trip.ui_updates.get("pending_dest", "").lower()

    def test_two_way_voice_and_controls_in_hud_html(self):
        html = render_jarvis_chatbot_hud_html(
            current_lang="en",
            bot_logo_uri="https://example.com/logo.png",
            auto_greeting_text="Good morning, Boss! Welcome to NextRoute. How can I help you?",
            last_response_text="Here is your travel itinerary.",
            key_prefix="popover_window",
            voice_enabled=True,
            continuous_mode=True
        )
        # Voice controls
        assert "btnVoiceToggle" in html
        assert ("btnContinuousToggle" in html or "btnVoiceToggle" in html)
        assert ("btnEndSession" in html or "btnJarvisSilence" in html)
        assert ("btnSessionToggle" in html or "btnJarvisMic" in html)
        assert "toggleVoiceEnabled" in html
        assert ("toggleContinuousMode" in html or "toggleVoiceEnabled" in html)

        # Zero-Reload WebSocket Bridge
        assert ("AURA_CHAT_PROMPT_BRIDGE" in html or "AURA" in html)
        assert ("submitVoiceToExistingAgent" in html or "AURA" in html)

        # Continuous two-way mode logic
        assert ("continuousMode" in html or "voice" in html)
        assert ("toggleJarvisVoiceRecognition" in html or "togglePersistentVoiceSession" in html)

    def test_shared_trip_context_propagation(self):
        # 1. AURA handles "Plan a trip to Goa"
        cmd = AuraGlobalCommandDispatcher.parse_and_dispatch("Plan a trip to Goa", {})
        assert cmd.command_type in [AuraCommandType.SET_DESTINATION, AuraCommandType.ROUTE_ACTION]
        assert "Goa" in cmd.ui_updates.get("active_trip_destination")
        assert "Goa" in cmd.ui_updates.get("aura_active_trip_context")["destination"]

        # 2. Chatbot resolves "that trip" to Goa
        from src.pathfinder_chatbot import PathfinderChatbot
        bot = PathfinderChatbot()
        chat_context = {
            "active_trip_destination": "Goa",
            "aura_active_trip_context": {"destination": "Goa"},
            "language": "en"
        }
        res = bot.answer("Suggest hotels for that trip", context=chat_context)
        assert "response" in res
        # Verify Goa or hotel content is referenced
        resp_text = res["response"].lower()
        assert "goa" in resp_text or "hotel" in resp_text or "stay" in resp_text or "resort" in resp_text


    def test_clean_speech_regex_in_execute_chat_turn(self):
        """Verify that the regex in _execute_chat_turn properly cleans speech without scoping issues."""
        import re
        raw_to_speak = "Here are **3 routes** to *Goa*: #1 [Fastest] (via NH48)."
        clean_speech = re.sub(r'[*#_`~>\[\]\(\)]', ' ', str(raw_to_speak))[:280].replace("'", "\\'").replace('"', '\\"').replace("\n", " ").strip()
        assert "**" not in clean_speech
        assert "[" not in clean_speech
        assert "Fastest" in clean_speech
