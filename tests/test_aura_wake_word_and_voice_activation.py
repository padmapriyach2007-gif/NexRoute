# -*- coding: utf-8 -*-
"""
Master Verification Suite for AURA Voice Activation, Auto-Greeting & Wake-Word Detection.
Verifies all 12 Acceptance Criteria:
1. Dynamic Time-Based Greeting generation (Morning, Afternoon, Evening, Night) with AURA persona.
2. Complete 8-Language Localization of Greetings (en, te, hi, ta, kn, ml, bn, mr).
3. 9-State Central Voice State Machine in HTML/JS:
   INITIALIZING, GREETING, WAKE_WORD_STANDBY, LISTENING, SILENCE_DETECTED, PROCESSING, SPEAKING, ERROR, STOPPED.
4. Multilingual Wake-Word Detection ("Hey AURA", "AURA", "Wake up AURA" + Telugu, Hindi, Tamil, Kannada, Malayalam, Bengali, Marathi).
5. Wake-Word extraction and localized acknowledgment phrases ("Yes, Boss?").
6. Intelligent Silence Detection configured to 2.0s (silenceThresholdMs: 2000).
7. Single-Execution Lock preventing duplicate voice command runs.
8. Avatar Stage Animation classes mapped to all states (avatarBreathing, pulseCyanWave, rotateDigitalRings, etc.).
9. Hardware Microphone Permission & Status indicators (ACTIVE, STANDBY, MUTED, DENIED).
10. Strict Architectural Separation: useDashboardVoice() vs useChatbotVoice().
11. Mutex Audio Lock via localStorage ('aura_active_speaker' = 'dashboard' vs 'chatbot').
12. Dashboard Voice Command Bridge (AURA_VOICE_COMMAND_BRIDGE) isolation from chatbot conversation history.
"""

import pytest
from src.aura_welcome_screen import (
    get_aura_startup_greeting,
    render_aura_welcome_hud,
)
from src.aura_voice_hud import render_aura_jarvis_hud_html
from src.i18n import SUPPORTED_LANGUAGES, t


EXACT_8_LANGS = ["en", "te", "hi", "ta", "kn", "ml", "bn", "mr"]


class TestAuraDynamicGreeting:
    @pytest.mark.parametrize("lang", EXACT_8_LANGS)
    def test_greeting_generated_for_all_eight_languages(self, lang):
        greet = get_aura_startup_greeting(lang, user_name="Boss")
        assert greet is not None and len(greet) > 0
        assert "\n" not in greet

    def test_english_time_based_greeting_persona(self):
        en_greet = get_aura_startup_greeting("en", user_name="Boss")
        assert "AURA" in en_greet or "NextRoute" in en_greet
        assert any(t in en_greet for t in ["Good morning", "Good afternoon", "Good evening", "Hello"])
        assert "Boss" in en_greet
        assert "autonomous travel assistant" in en_greet


class TestAuraNineStateStateMachine:
    def test_html_contains_all_nine_states_in_js(self):
        html = render_aura_welcome_hud(current_lang="en", auto_speak=True)
        states = [
            "STATE_INITIALIZING",
            "STATE_GREETING",
            "STATE_WAKE_WORD_STANDBY",
            "STATE_LISTENING",
            "STATE_SILENCE_DETECTED",
            "STATE_PROCESSING",
            "STATE_SPEAKING",
            "STATE_ERROR",
            "STATE_STOPPED",
        ]
        for s in states:
            assert s in html, f"Missing {s} in HUD JavaScript state machine"

    def test_avatar_stage_animation_classes_exist_in_css(self):
        html = render_aura_welcome_hud(current_lang="en")
        assert "state-wake-word-standby" in html
        assert "state-listening" in html
        assert "state-silence-detected" in html
        assert "state-processing" in html
        assert "state-speaking" in html
        assert "avatarBreathing" in html
        assert "pulseCyanWave" in html
        assert "rotateDigitalRings" in html
        assert "voiceWaveModulation" in html


class TestAuraWakeWordDetection:
    def test_js_wake_word_patterns_for_all_eight_languages(self):
        html = render_aura_welcome_hud(current_lang="en")
        assert "isWakeWordPhrase" in html
        assert "extractCommandAfterWakeWord" in html
        # English wake words
        assert "hey\\s+aura" in html or "hey\\s*aura" in html or "hey" in html
        # Telugu: హే ఆరా / ఆరా
        assert "హే" in html and "ఆరా" in html
        # Hindi: हे ऑरा / ऑरा
        assert "हे" in html and "ऑरा" in html
        # Tamil: ஹே ஆரா / ஆரா
        assert "ஹே" in html and "ஆரா" in html
        # Kannada: ಹೇ ಔರಾ / ಔರಾ
        assert "ಹೇ" in html and "ಔರಾ" in html
        # Malayalam: ഹേ ഓറ / ഓറ
        assert "ഹേ" in html and "ഓറ" in html
        # Bengali: হে অরা / অরা
        assert "হে" in html and "অরা" in html
        # Marathi: हे ऑरा / ऑरा
        assert "हे" in html and "ऑरा" in html

    def test_localized_wake_word_acknowledgments_present(self):
        html = render_aura_welcome_hud(current_lang="en")
        assert "wakeWordAcks" in html
        assert "Yes, Boss?" in html
        assert "చెప్పండి బాస్?" in html
        assert "हाँ, बॉस?" in html


class TestIntelligentSilenceDetection:
    def test_silence_threshold_configured_to_two_seconds(self):
        html = render_aura_welcome_hud(current_lang="en")
        assert "silenceThresholdMs: 2000" in html
        assert "executeFinalCommand" in html
        assert "commandDispatchLock" in html

    def test_extended_silence_timeout_handled(self):
        html = render_aura_welcome_hud(current_lang="en")
        assert "resetExtendedSilenceTimer" in html
        assert "extendedSilenceTimer" in html


class TestHardwareMicrophoneTelemetry:
    def test_mic_status_pill_markup_present(self):
        html = render_aura_welcome_hud(current_lang="en")
        assert "micStatusIndicator" in html
        assert "micStatusText" in html
        assert "mic-status-pill" in html
        assert "setMicStatus" in html

    @pytest.mark.parametrize("lang", EXACT_8_LANGS)
    def test_mic_localized_tokens_exist(self, lang):
        assert t("aura.mic_active", lang=lang) != ""
        assert t("aura.mic_standby", lang=lang) != ""
        assert t("aura.mic_muted", lang=lang) != ""
        assert t("aura.mic_denied", lang=lang) != ""


class TestVoiceSeparationAndIsolation:
    def test_dashboard_voice_controller_exposed(self):
        html = render_aura_welcome_hud(current_lang="en")
        assert "window.useDashboardVoice" in html
        assert "type: 'dashboard_voice'" in html
        assert "AURA_VOICE_COMMAND_BRIDGE" in html

    def test_chatbot_voice_controller_exposed(self):
        chat_html = render_aura_jarvis_hud_html(current_lang="en")
        assert "window.useChatbotVoice" in chat_html
        assert "type: 'chatbot_voice'" in chat_html
        assert "AURA_CHAT_PROMPT_BRIDGE" in chat_html

    def test_dashboard_independent_states_and_handlers(self):
        html = render_aura_welcome_hud(current_lang="en")
        # Separate states
        assert "dashboardIsListening" in html
        assert "dashboardTranscript" in html
        assert "dashboardVoiceActive" in html
        assert "dashboardRecognition" in html
        assert "dashboardSpeechOutput" in html
        # Separate handlers
        assert "startDashboardVoice" in html
        assert "stopDashboardVoice" in html
        assert "handleDashboardTranscript" in html
        assert "handleDashboardVoiceError" in html
        assert "speakDashboardVoice" in html

    def test_chatbot_independent_states_and_handlers(self):
        from src.aura_voice_hud import render_jarvis_chatbot_hud_html
        chat_html = render_jarvis_chatbot_hud_html(current_lang="en")
        # Separate states
        assert "chatbotIsListening" in chat_html
        assert "chatbotTranscript" in chat_html
        assert "chatbotVoiceActive" in chat_html
        assert "chatbotRecognition" in chat_html
        assert "chatbotSpeechOutput" in chat_html
        # Separate handlers
        assert "startChatbotVoice" in chat_html
        assert "stopChatbotVoice" in chat_html
        assert "handleChatbotTranscript" in chat_html
        assert "handleChatbotVoiceError" in chat_html
        assert "speakChatbotVoice" in chat_html

    def test_dashboard_command_dispatcher_never_delegates_to_chat_turn(self):
        from src.aura_command_dispatcher import AuraGlobalCommandDispatcher
        # Any arbitrary query on the dashboard should not push to chatbot message handler
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Tell me about Vijayawada", {})
        assert "pending_chat_prompt" not in res.ui_updates
        assert "delegate_to_chat_turn" != res.action_name

    def test_mutual_exclusion_audio_lock_present(self):
        dash_html = render_aura_welcome_hud(current_lang="en")
        chat_html = render_aura_jarvis_hud_html(current_lang="en")
        # Dashboard checks if chatbot is speaking
        assert "aura_active_speaker" in dash_html
        # Chatbot checks if dashboard is speaking
        assert "aura_active_speaker" in chat_html

    def test_cleanup_listeners_registered_in_both_interfaces(self):
        dash_html = render_aura_welcome_hud(current_lang="en")
        from src.aura_voice_hud import render_jarvis_chatbot_hud_html
        chat_html = render_jarvis_chatbot_hud_html(current_lang="en")
        assert "beforeunload" in dash_html and "pagehide" in dash_html
        assert "beforeunload" in chat_html and "pagehide" in chat_html


class TestAutoplayAndVisibilityRecovery:
    def test_autoplay_unlock_listeners_registered(self):
        html = render_aura_welcome_hud(current_lang="en")
        assert "unlockAudioOnFirstInteraction" in html

    def test_tab_visibility_change_handled(self):
        html = render_aura_welcome_hud(current_lang="en")
        assert "visibilitychange" in html

