# -*- coding: utf-8 -*-
"""
Master Verification Suite for Complete 8-Language Multilingual Support in NexRoute.
Verifies:
1. Exact 8 Supported Languages (en, te, hi, ta, kn, ml, bn, mr) with native names and BCP-47 speech codes.
2. Translation completeness in locales/ JSON dictionaries and fallback chain to English.
3. Spoken voice navigation turn announcements for all 8 languages.
4. Voice guidance audio narratives for all 8 languages.
5. AURA command dispatcher responses for all 8 languages.
6. AI Assistant Engine cognitive reasoner across all 8 languages.
7. Mobile bottom navigation bar translations across all 8 languages.
"""

import pytest
from src.i18n import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, t, get_bcp47_code, get_language_native_name
from src.google_maps_voice_navigator import build_spoken_instruction
from src.voice_guidance import generate_simple_spoken_narrative
from src.aura_command_dispatcher import AuraGlobalCommandDispatcher
from src.ai_assistant_engine import BuiltinCognitiveEngine
from src.mobile_bottom_nav import render_mobile_bottom_navigation_bar, MOBILE_NAV_TRANSLATIONS


EXACT_8_LANGUAGES = ["en", "te", "hi", "ta", "kn", "ml", "bn", "mr"]

EXPECTED_NATIVES = {
    "en": "English",
    "te": "తెలుగు",
    "hi": "हिन्दी",
    "ta": "தமிழ்",
    "kn": "ಕನ್ನಡ",
    "ml": "മലയാളം",
    "bn": "বাংলা",
    "mr": "मराठी",
}

EXPECTED_BCP47 = {
    "en": "en-IN",
    "te": "te-IN",
    "hi": "hi-IN",
    "ta": "ta-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "bn": "bn-IN",
    "mr": "mr-IN",
}


class TestSupportedLanguagesConfiguration:
    def test_exact_eight_languages(self):
        """Must strictly match the 8 languages specified in the prompt and README."""
        assert sorted(list(SUPPORTED_LANGUAGES.keys())) == sorted(EXACT_8_LANGUAGES)

    @pytest.mark.parametrize("lang_code", EXACT_8_LANGUAGES)
    def test_native_script_and_bcp47(self, lang_code):
        meta = SUPPORTED_LANGUAGES[lang_code]
        assert meta["native"] == EXPECTED_NATIVES[lang_code]
        assert get_language_native_name(lang_code) == EXPECTED_NATIVES[lang_code]
        assert get_bcp47_code(lang_code) == EXPECTED_BCP47[lang_code]


class TestTranslationDictionariesAndFallbacks:
    @pytest.mark.parametrize("lang_code", EXACT_8_LANGUAGES)
    def test_core_ui_keys_translated(self, lang_code):
        core_keys = [
            "tab.navigation",
            "tab.virtual_guide",
            "tab.places",
            "nav.starting_point",
            "nav.destination",
            "cat.hospital",
            "cat.supermarket",
            "cat.fuel",
            "cat.atm",
            "nav.mins"
        ]
        for k in core_keys:
            val = t(k, lang=lang_code)
            assert val is not None and val != ""
            assert val != k

    def test_english_fallback_mechanism(self):
        # A nonexistent key should gracefully fall back to default or humanized key without error
        res = t("nonexistent.fake_sample_key", default="Safe Fallback", lang="te")
        assert res == "Safe Fallback"

        res_no_default = t("nonexistent.safety_corridor", lang="hi")
        assert res_no_default == "Safety Corridor"


class TestVoiceNavigationMultilingual:
    @pytest.mark.parametrize("lang_code", EXACT_8_LANGUAGES)
    def test_spoken_turn_announcements_in_all_eight_languages(self, lang_code):
        mock_step = {
            "instruction": "Turn left on Main Road",
            "road": "Main Road",
            "distance_m": 450.0
        }
        mock_next = {
            "instruction": "Proceed straight",
            "road": "NH 16",
            "distance_m": 1200.0
        }

        announcement = build_spoken_instruction(mock_step, mock_next, is_first=True, is_last=False, language=lang_code)
        assert announcement is not None and len(announcement) > 0
        assert "Main Road" in announcement

    @pytest.mark.parametrize("lang_code", EXACT_8_LANGUAGES)
    def test_spoken_narrative_in_all_eight_languages(self, lang_code):
        narrative = generate_simple_spoken_narrative(
            origin_name="Guntur Railway Station",
            destination_name="Vijayawada Bus Station",
            distance_km=32.5,
            duration_min=45.0,
            lang=lang_code
        )
        assert narrative is not None and len(narrative) > 0
        assert "Guntur Railway Station" in narrative
        assert "Vijayawada Bus Station" in narrative


class TestAuraVoiceOSMultilingual:
    @pytest.mark.parametrize("lang_code", EXACT_8_LANGUAGES)
    def test_aura_command_responses_for_all_eight_languages(self, lang_code):
        templates = AuraGlobalCommandDispatcher.RESPONSES[lang_code]
        assert "welcome" in templates
        assert "nav_opened" in templates
        assert "dest_cleared" in templates
        assert "vehicle_switched" in templates

        # Test dispatching a welcome command
        result = AuraGlobalCommandDispatcher.parse_and_dispatch("hello aura", lang=lang_code)
        assert result.spoken_response == templates["welcome"]
        assert templates["welcome"] in result.text_response


class TestAiAssistantMultilingualReasoning:
    @pytest.mark.parametrize("lang_code", EXACT_8_LANGUAGES)
    def test_cognitive_engine_reasoning_in_all_eight_languages(self, lang_code):
        engine = BuiltinCognitiveEngine()
        res = engine.reason(
            query="explain quantum navigation",
            context={"language": lang_code}
        )
        assert "response" in res
        assert len(res["response"]) > 0
        r_text = res["response"].lower()
        assert "quantum" in r_text or "వివరణ" in r_text or "व्याख्या" in r_text or "விளக்கம்" in r_text or "ವಿವರಣೆ" in r_text or "വിവരണം" in r_text or "ব্যাখ্যা" in r_text or "स्पष्टीकरण" in r_text


class TestMobileBottomNavMultilingual:
    @pytest.mark.parametrize("lang_code", EXACT_8_LANGUAGES)
    def test_mobile_nav_items_for_all_eight_languages(self, lang_code):
        assert lang_code in MOBILE_NAV_TRANSLATIONS
        html = render_mobile_bottom_navigation_bar(current_view="dashboard", lang=lang_code)
        labels = MOBILE_NAV_TRANSLATIONS[lang_code]
        for key in ["home", "map", "trips", "places", "guide"]:
            assert labels[key] in html
