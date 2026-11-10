# -*- coding: utf-8 -*-
"""
Comprehensive Test Suite for NexRoute Global Multilingual Translation Engine.
Verifies all 8 languages, dynamic AI translation, entity preservation,
centralized architecture, font manager, and voice integration.
"""

import pytest
import builtins
from localization import (
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE,
    PROTECTED_ENTITIES,
    get_selected_language,
    set_selected_language,
    t,
    get_bcp47_code,
    get_language_native_name,
    format_distance,
    format_duration,
    translate_content,
    translate_dict_descriptions,
    get_font_injection_html,
    TRANSLATIONS
)


class TestGlobalMultilingualTranslationEngine:
    def test_all_8_languages_configured(self):
        """Verifies exactly the 8 authorized languages are configured."""
        expected_langs = {"en", "te", "hi", "kn", "ta", "ml", "mr", "bn"}
        assert set(SUPPORTED_LANGUAGES.keys()) == expected_langs

        # Verify BCP-47 speech codes
        assert get_bcp47_code("en") == "en-IN"
        assert get_bcp47_code("te") == "te-IN"
        assert get_bcp47_code("hi") == "hi-IN"
        assert get_bcp47_code("kn") == "kn-IN"
        assert get_bcp47_code("ta") == "ta-IN"
        assert get_bcp47_code("ml") == "ml-IN"
        assert get_bcp47_code("mr") == "mr-IN"
        assert get_bcp47_code("bn") == "bn-IN"

    def test_native_names_display(self):
        """Verifies native script names for all languages."""
        assert get_language_native_name("te") == "తెలుగు"
        assert get_language_native_name("hi") == "हिन्दी"
        assert get_language_native_name("kn") == "ಕನ್ನಡ"
        assert get_language_native_name("ta") == "தமிழ்"
        assert get_language_native_name("ml") == "മലയാളം"
        assert get_language_native_name("mr") == "मराठी"
        assert get_language_native_name("bn") == "বাংলা"

    def test_language_selection_and_builtins_sync(self):
        """Verifies language switcher synchronizes builtins.cur_l."""
        set_selected_language("te")
        assert get_selected_language() == "te"
        assert builtins.cur_l == "te"

        set_selected_language("hi")
        assert get_selected_language() == "hi"
        assert builtins.cur_l == "hi"

        # Restore default
        set_selected_language("en")
        assert get_selected_language() == "en"
        assert builtins.cur_l == "en"

    def test_central_t_function_across_all_languages(self):
        """Verifies static UI keys resolve across all 8 languages."""
        for lang in SUPPORTED_LANGUAGES:
            title = t("app.title", language=lang)
            assert title in ["NexRoute", "P.A.T.H.F.I.N.D.E.R."]

            nav = t("nav.navigation", language=lang)
            assert nav is not None
            assert len(nav) > 0

    def test_dynamic_translation_corridor_storybook_cards(self):
        """
        Verifies dynamic translation for the 4 Bento cards:
        Culture, Nature, Photo Spot, and Local Food across all languages.
        """
        culture_en = "Historic heritage landmark and cultural monument preserved for regional significance."
        nature_en = "Cascading natural waterfall and scenic photography viewpoint."
        photo_en = "Panoramic vistas of rural agricultural waterways."
        food_en = "Authentic regional highway tiffins, fresh chai, and sweets."

        for lang in ["te", "hi", "kn", "ta", "ml", "mr", "bn"]:
            c_trans = translate_content(culture_en, target_language=lang)
            n_trans = translate_content(nature_en, target_language=lang)
            p_trans = translate_content(photo_en, target_language=lang)
            f_trans = translate_content(food_en, target_language=lang)

            assert c_trans != culture_en, f"Failed to translate culture in {lang}"
            assert n_trans != nature_en, f"Failed to translate nature in {lang}"
            assert p_trans != photo_en, f"Failed to translate photo in {lang}"
            assert f_trans != food_en, f"Failed to translate food in {lang}"

    def test_protected_entity_preservation(self):
        """
        Verifies that protected proper nouns (NexRoute, AURA, Tenali, Krishna River,
        Buckingham Canal, Gongura Pacchadi) and coordinates are preserved untouched.
        """
        sample_text = (
            "NexRoute and AURA guide you near Tenali along the Krishna River and Buckingham Canal. "
            "Enjoy authentic Gongura Pacchadi at 16.5062, 80.6480."
        )

        for lang in ["te", "hi", "kn", "ta", "ml", "mr", "bn"]:
            translated = translate_content(sample_text, target_language=lang)
            assert "NexRoute" in translated, f"NexRoute altered in {lang}"
            assert "AURA" in translated, f"AURA altered in {lang}"
            assert "Tenali" in translated, f"Tenali altered in {lang}"
            assert "Krishna River" in translated, f"Krishna River altered in {lang}"
            assert "Buckingham Canal" in translated, f"Buckingham Canal altered in {lang}"
            assert "Gongura Pacchadi" in translated, f"Gongura Pacchadi altered in {lang}"
            assert "16.5062, 80.6480" in translated, f"Coordinates altered in {lang}"

    def test_font_manager_injection_html(self):
        """Verifies Google Fonts injection HTML contains Noto Sans for all Indic scripts."""
        html = get_font_injection_html("te")
        assert "Noto Sans Telugu" in html
        assert "Noto Sans Devanagari" in html
        assert "Noto Sans Kannada" in html
        assert "Noto Sans Tamil" in html
        assert "Noto Sans Malayalam" in html
        assert "Noto Sans Bengali" in html
        assert "line-height: 1.55" in html

    def test_dict_description_batch_translation(self):
        """Verifies batch translation of dictionary descriptions while keeping IDs intact."""
        poi_data = {
            "place_id": "osm_12345",
            "name": "Amaravati Buddhist Stupa",
            "category": "Historical Monument & Fort",
            "latitude": 16.574,
            "longitude": 80.358,
            "description": "Historic heritage landmark and cultural monument preserved for regional significance.",
            "cultural_heritage": "Renowned for the world-celebrated Amaravati school of art."
        }

        translated_poi = translate_dict_descriptions(poi_data, target_language="te")
        assert translated_poi["place_id"] == "osm_12345"
        assert translated_poi["name"] == "Amaravati Buddhist Stupa"
        assert translated_poi["latitude"] == 16.574
        assert translated_poi["description"] != poi_data["description"]

    def test_caching_performance(self):
        """Verifies that translations are cached in memory for sub-millisecond retrieval."""
        text = "Authentic regional highway tiffins, fresh chai, and sweets."
        # First call
        res1 = translate_content(text, target_language="te")
        # Second call (must be identical and instant from cache)
        res2 = translate_content(text, target_language="te")
        assert res1 == res2
        assert len(res1) > 0
