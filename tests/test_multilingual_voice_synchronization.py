"""
Comprehensive Test Suite for NextRoute Multilingual Voice Architecture.

Tests:
1. Multilingual Voice Capability Map across all 8 languages (en, te, hi, ta, kn, ml, bn, mr).
2. Main Dashboard Startup Greetings (time-based & multilingual).
3. Chatbot Dedicated Greetings (multilingual).
4. Speech Recognition BCP-47 Tag Synchronization.
5. Multilingual AI Response Generation (native scripts).
6. Non-English Speech Synthesis Fallback Safety (no cross-language mangling).
7. Zero-Interference Independence & Audio Mutex Lock.
"""

import pytest
from src.multilingual_voice_config import (
    MULTILINGUAL_VOICE_CAPABILITY_MAP,
    get_supported_language_codes,
    get_voice_capability,
    get_bcp47_code_for_voice,
    get_preferred_voice_keywords
)
from src.aura_welcome_screen import get_aura_startup_greeting, render_aura_welcome_hud
from src.aura_voice_hud import get_chatbot_copilot_greeting, render_jarvis_chatbot_hud_html
from src.pathfinder_chatbot import PathfinderChatbot
from src.nextroute_knowledge_rag import resolve_target_language


ALL_8_LANGUAGES = ["en", "te", "hi", "ta", "kn", "ml", "bn", "mr"]


def test_multilingual_voice_capability_map_completeness():
    """Verifies that all 8 languages have full capability entries."""
    supported = get_supported_language_codes()
    for lang in ALL_8_LANGUAGES:
        assert lang in supported
        cap = get_voice_capability(lang)
        assert cap is not None
        assert cap["speech_recognition_supported"] is True
        assert cap["speech_synthesis_supported"] is True
        assert cap["bcp47"].endswith("-IN")
        assert len(cap["preferred_voices"]) > 0
        assert len(cap["voice_search_keywords"]) > 0
        assert "fallback_behavior" in cap


def test_dashboard_startup_greetings_all_languages():
    """Verifies time-appropriate dashboard greetings for all 8 languages."""
    for lang in ALL_8_LANGUAGES:
        greeting = get_aura_startup_greeting(lang=lang, user_name="Boss")
        assert "Boss" in greeting or "బాస్" in greeting or "बॉस" in greeting or "பாஸ்" in greeting or "ಬಾಸ್" in greeting or "ബോസ്" in greeting or "বস" in greeting
        # Non-English greetings must contain native characters
        if lang == "te":
            assert any('\u0c00' <= c <= '\u0c7f' for c in greeting)
        elif lang == "hi" or lang == "mr":
            assert any('\u0900' <= c <= '\u097f' for c in greeting)
        elif lang == "ta":
            assert any('\u0b80' <= c <= '\u0bff' for c in greeting)
        elif lang == "kn":
            assert any('\u0c80' <= c <= '\u0cff' for c in greeting)
        elif lang == "ml":
            assert any('\u0d00' <= c <= '\u0d7f' for c in greeting)
        elif lang == "bn":
            assert any('\u0980' <= c <= '\u09ff' for c in greeting)


def test_chatbot_copilot_greetings_all_languages():
    """Verifies dedicated chatbot greetings for all 8 languages."""
    for lang in ALL_8_LANGUAGES:
        cg = get_chatbot_copilot_greeting(lang=lang)
        assert "AURA" in cg or "ऑरा" in cg
        if lang == "en":
            assert "Hello! I'm AURA, your travel copilot. What would you like to know today?" in cg
        elif lang == "te":
            assert "మీ ట్రావెల్ కోపైలట్" in cg
        elif lang == "hi":
            assert "ट्रैवल कोपायलट" in cg
        elif lang == "ta":
            assert "பயணக் கோபிலட்" in cg
        elif lang == "kn":
            assert "ಪ್ರಯಾಣ ಸಹಾಯಕ" in cg
        elif lang == "ml":
            assert "ട്രാവൽ കോപൈലറ്റ്" in cg
        elif lang == "bn":
            assert "ভ্রমণ সহকারী" in cg
        elif lang == "mr":
            assert "ट्रॅव्हल को-पायलट" in cg


def test_speech_recognition_bcp47_sync():
    """Verifies each language maps to the standard BCP-47 recognition code."""
    expected_bcp47 = {
        "en": "en-IN",
        "te": "te-IN",
        "hi": "hi-IN",
        "ta": "ta-IN",
        "kn": "kn-IN",
        "ml": "ml-IN",
        "bn": "bn-IN",
        "mr": "mr-IN"
    }
    for lang, bcp in expected_bcp47.items():
        assert get_bcp47_code_for_voice(lang) == bcp


def test_dashboard_hud_html_multilingual():
    """Verifies dashboard HUD HTML renders with correct language code and BCP-47 tag."""
    for lang in ALL_8_LANGUAGES:
        html = render_aura_welcome_hud(current_lang=lang, auto_speak=True, user_name="Boss")
        assert f'<html lang="{lang}">' in html
        expected_bcp = get_bcp47_code_for_voice(lang)
        assert expected_bcp in html
        # Verifies presence of smart silence configuration
        assert "extendedSilenceMs" in html
        assert "silenceThresholdMs" in html


def test_chatbot_hud_html_multilingual():
    """Verifies chatbot HUD HTML renders with correct language code and BCP-47 tag."""
    for lang in ALL_8_LANGUAGES:
        html = render_jarvis_chatbot_hud_html(
            current_lang=lang,
            auto_greeting_text=get_chatbot_copilot_greeting(lang),
            last_response_text="",
            key_prefix="test"
        )
        assert f'<html lang="{lang}">' in html
        expected_bcp = get_bcp47_code_for_voice(lang)
        assert expected_bcp in html
        # Verifies presence of smart silence configuration & audio isolation
        assert "aura_active_speaker" in html
        assert "extendedSilenceMs" in html


def test_chatbot_ai_multilingual_responses():
    """Verifies chatbot generates native language responses across all languages."""
    bot = PathfinderChatbot()

    # 1. Telugu Context
    r_te = bot.answer("How do I change vehicle mode?", context={"language": "te"})
    assert any('\u0c00' <= c <= '\u0c7f' for c in r_te["response"])

    # 2. Hindi Context
    r_hi = bot.answer("How do I change vehicle mode?", context={"language": "hi"})
    assert any('\u0900' <= c <= '\u097f' for c in r_hi["response"])

    # 3. Explicit Query Override (app lang=en, user asks in Telugu)
    r_override = bot.answer("Plan a trip to Goa. Answer in Telugu", context={"language": "en"})
    assert any('\u0c00' <= c <= '\u0c7f' for c in r_override["response"])


def test_voice_assistants_audio_isolation_scripts():
    """Verifies audio mutex tags prevent overlapping speech output and duplicate mic capture."""
    w_html = render_aura_welcome_hud(current_lang="en")
    c_html = render_jarvis_chatbot_hud_html(current_lang="en")

    # Dashboard sets dashboard speaker and checks for chatbot speaker
    assert "localStorage.setItem('aura_active_speaker', 'dashboard')" in w_html
    assert "localStorage.getItem('aura_active_speaker') === 'chatbot'" in w_html

    # Chatbot sets chatbot speaker and checks for dashboard speaker
    assert "localStorage.setItem('aura_active_speaker', 'chatbot')" in c_html
    assert "localStorage.getItem('aura_active_speaker') === 'dashboard'" in c_html
