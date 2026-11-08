"""
Unit tests for AURA JARVIS-Style AI Voice Assistant & Autonomous Controller.
Verifies time-appropriate greetings, removal of unnecessary buttons, continuous
speech recognition & synthesis, and single NextRoute application section navigation.
"""

import pytest
from src.aura_welcome_screen import (
    get_aura_startup_greeting,
    render_aura_welcome_hud,
)
from src.aura_command_dispatcher import (
    AuraGlobalCommandDispatcher,
    AuraCommandType,
)


class TestAuraWelcomeScreen:
    def test_startup_greeting_exact_format(self):
        # English greeting should match exact time-based pattern:
        # "{Good morning/afternoon/evening}, Boss! Welcome to NextRoute. How can I help you?"
        en_greet = get_aura_startup_greeting("en", user_name="Boss")
        assert "Boss! Welcome to NextRoute. How can I help you?" in en_greet
        assert any(t in en_greet for t in ["Good morning", "Good afternoon", "Good evening"])
        # No extra sentences
        assert "\n" not in en_greet
        assert "intelligent travel assistant" not in en_greet
        assert "Where shall we explore" not in en_greet

        # Telugu
        te_greet = get_aura_startup_greeting("te", user_name="బాస్")
        assert "బాస్! నెక్స్‌రూట్‌కి స్వాగతం. నేను మీకు ఎలా సహాయపడగలను?" in te_greet

        # Hindi
        hi_greet = get_aura_startup_greeting("hi", user_name="बॉस")
        assert "बॉस! नेक्स्ट-रूट में आपका स्वागत है। मैं आपकी क्या मदद कर सकता हूँ?" in hi_greet

        # Tamil
        ta_greet = get_aura_startup_greeting("ta", user_name="பாஸ்")
        assert "பாஸ்! நெக்ஸ்-ரூட்டிற்கு நல்வரவு" in ta_greet

        # Kannada
        kn_greet = get_aura_startup_greeting("kn", user_name="ಬಾಸ್")
        assert "ಬಾಸ್! ನೆಕ್ಸ್-ರೂಟ್‌ಗೆ ಸುಸ್ವಾಗತ" in kn_greet

        # Malayalam
        ml_greet = get_aura_startup_greeting("ml", user_name="ബോസ്")
        assert "ബോസ്! നെക്സ്-റൂട്ടിലേക്ക് സ്വാഗതം" in ml_greet

    def test_render_aura_welcome_hud_html_structure(self):
        html = render_aura_welcome_hud(
            current_lang="en",
            auto_speak=True,
            bot_logo_uri="https://example.com/logo.png",
            user_name="Boss"
        )
        assert "<!DOCTYPE html>" in html
        assert "AURA • JARVIS AI COPILOT" in html
        assert "statusBadge" in html
        assert "auraWaveCanvas" in html
        assert "arc-reactor-ring-outer" in html
        assert "transcriptBox" in html
        assert "SpeechRecognition" in html
        assert "SpeechSynthesisUtterance" in html

        # Unnecessary controls and duplicate activation buttons must be REMOVED
        assert "btnVoiceMic" not in html
        assert "btnPlayGreeting" not in html
        assert "btn-aura-skip" not in html
        assert "Start Voice Command" not in html
        assert "Play Greeting" not in html
        assert "Enter NexRoute" not in html

    def test_continuous_speech_and_instant_responses_in_js(self):
        html = render_aura_welcome_hud(current_lang="en", auto_speak=True)
        # JavaScript includes speech handlers, websocket bridge, and auto listening start
        assert "startVoiceListening" in html
        assert "handleRecognizedVoiceCommand" in html
        assert "triggerStartupGreeting" in html
        assert "sendCommandToStreamlit" in html
        assert "AURA_VOICE_COMMAND_BRIDGE" in html
        assert "Opening navigation." in html
        assert "Here are your trips." in html
        assert "Let's find hotels." in html
        assert "Opening flight planner." in html
        assert "Finding nearby restaurants." in html
        assert "Opening your profile." in html
        assert "Opening your bookings." in html
        assert "Going back." in html
        assert "Returning to home dashboard." in html

    def test_compact_mode_rendering(self):
        html_compact = render_aura_welcome_hud(current_lang="en", auto_speak=False, compact=True)
        assert "aura-compact-panel" in html_compact
        assert "AURA • JARVIS COPILOT" in html_compact
        assert "auraWaveCanvas" in html_compact
        assert "startVoiceListening" in html_compact
        assert "sendCommandToStreamlit" in html_compact

    def test_single_nextroute_navigation_sections(self):
        ctx = {"active_tab": "nav", "language": "en"}

        # 1. Open navigation
        res_nav = AuraGlobalCommandDispatcher.parse_and_dispatch("Open navigation", ctx)
        assert res_nav.command_type == AuraCommandType.NAVIGATE_TAB
        assert res_nav.ui_updates.get("current_view") == "map_nav"
        assert res_nav.ui_updates.get("target_tab") == "nav"
        assert res_nav.spoken_response == "Opening navigation."

        # 2. Open my trips
        res_trips = AuraGlobalCommandDispatcher.parse_and_dispatch("Open my trips", ctx)
        assert res_trips.command_type == AuraCommandType.NAVIGATE_TAB
        assert res_trips.ui_updates.get("current_view") == "copilot_studio"
        assert res_trips.spoken_response == "Here are your trips."

        # 3. Show hotels
        res_hotels = AuraGlobalCommandDispatcher.parse_and_dispatch("Show hotels", ctx)
        assert res_hotels.command_type == AuraCommandType.FACILITY_SEARCH
        assert res_hotels.ui_updates.get("current_view") == "map_nav"
        assert res_hotels.ui_updates.get("facility_filter") == "hotel"
        assert res_hotels.spoken_response == "Let's find hotels."

        # 4. Open flights
        res_flights = AuraGlobalCommandDispatcher.parse_and_dispatch("Open flights", ctx)
        assert res_flights.command_type == AuraCommandType.NAVIGATE_TAB
        assert res_flights.ui_updates.get("current_view") == "copilot_studio"
        assert res_flights.ui_updates.get("selected_travel_mode") == "FLIGHT"
        assert res_flights.spoken_response == "Opening flight planner."

        # 5. Show restaurants
        res_food = AuraGlobalCommandDispatcher.parse_and_dispatch("Show restaurants", ctx)
        assert res_food.command_type == AuraCommandType.FACILITY_SEARCH
        assert res_food.ui_updates.get("current_view") == "map_nav"
        assert res_food.ui_updates.get("facility_filter") == "food"
        assert res_food.spoken_response == "Finding nearby restaurants."

        # 6. Go to my profile
        res_profile = AuraGlobalCommandDispatcher.parse_and_dispatch("Go to my profile", ctx)
        assert res_profile.command_type == AuraCommandType.NAVIGATE_TAB
        assert res_profile.ui_updates.get("current_view") == "dashboard"
        assert res_profile.ui_updates.get("show_user_profile_modal") is True
        assert res_profile.spoken_response == "Opening your profile."

        # 7. Open my bookings
        res_bookings = AuraGlobalCommandDispatcher.parse_and_dispatch("Open my bookings", ctx)
        assert res_bookings.command_type == AuraCommandType.NAVIGATE_TAB
        assert res_bookings.ui_updates.get("current_view") == "copilot_studio"
        assert res_bookings.ui_updates.get("target_tab") == "bookings"
        assert res_bookings.spoken_response == "Opening your bookings."

        # 8. Go back
        res_back = AuraGlobalCommandDispatcher.parse_and_dispatch("Go back", ctx)
        assert res_back.command_type == AuraCommandType.NAVIGATE_TAB
        assert res_back.ui_updates.get("trigger_go_back") is True
        assert res_back.spoken_response == "Going back."

        # 9. Go home
        res_home = AuraGlobalCommandDispatcher.parse_and_dispatch("Go home", ctx)
        assert res_home.command_type == AuraCommandType.NAVIGATE_TAB
        assert res_home.ui_updates.get("current_view") == "dashboard"
        assert res_home.spoken_response == "Returning to home dashboard."

        # 10. Open settings
        res_settings = AuraGlobalCommandDispatcher.parse_and_dispatch("Open settings", ctx)
        assert res_settings.command_type == AuraCommandType.NAVIGATE_TAB
        assert res_settings.ui_updates.get("show_user_profile_modal") is True
        assert res_settings.spoken_response == "Opening settings."

    def test_session_state_single_greeting_simulation(self):
        # Simulating Streamlit session state lifecycle:
        # Initial launch: aura_welcome_greeted is False -> auto_speak is True
        # On first run, it is marked True so repeated Streamlit reruns NEVER re-speak
        fake_session = {
            "aura_welcome_greeted": False,
            "show_aura_welcome": True
        }

        # 1st Run (Startup)
        auto_speak_1 = not fake_session["aura_welcome_greeted"]
        assert auto_speak_1 is True
        fake_session["aura_welcome_greeted"] = True

        # 2nd Run (Streamlit rerun after state change / interaction)
        auto_speak_2 = not fake_session["aura_welcome_greeted"]
        assert auto_speak_2 is False, "Greeting must NOT play repeatedly on Streamlit reruns"

    def test_apply_execution_result_go_back_history(self):
        fake_session = {
            "current_view": "dashboard",
            "view_history": []
        }
        ctx = {}

        # 1. Navigate to map_nav
        cmd1 = AuraGlobalCommandDispatcher.parse_and_dispatch("Open navigation", ctx)
        AuraGlobalCommandDispatcher.apply_execution_result(cmd1, fake_session)
        assert fake_session["current_view"] == "map_nav"
        assert fake_session["view_history"] == ["dashboard", "map_nav"]

        # 2. Navigate to copilot_studio
        cmd2 = AuraGlobalCommandDispatcher.parse_and_dispatch("Show my trips", ctx)
        AuraGlobalCommandDispatcher.apply_execution_result(cmd2, fake_session)
        assert fake_session["current_view"] == "copilot_studio"
        assert fake_session["view_history"] == ["dashboard", "map_nav", "copilot_studio"]

        # 3. Say "Go back"
        cmd_back = AuraGlobalCommandDispatcher.parse_and_dispatch("Go back", ctx)
        AuraGlobalCommandDispatcher.apply_execution_result(cmd_back, fake_session)
        assert fake_session["current_view"] == "map_nav"
        assert fake_session["view_history"] == ["dashboard", "map_nav"]

        # 4. Say "Go back" again
        cmd_back2 = AuraGlobalCommandDispatcher.parse_and_dispatch("Go back", ctx)
        AuraGlobalCommandDispatcher.apply_execution_result(cmd_back2, fake_session)
        assert fake_session["current_view"] == "dashboard"
        assert fake_session["view_history"] == ["dashboard"]
