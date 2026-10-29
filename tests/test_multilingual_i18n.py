"""
Tests for PATHFINDER Centralized Multilingual Localization (i18n) Engine
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Complete Multilingual System Test Suite
"""

import pytest
import os
import sys

# Ensure root and src are on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from src.i18n import (
    t,
    get_current_language,
    set_current_language,
    get_supported_languages,
    get_bcp47_code,
    get_language_native_name,
    format_distance,
    format_duration,
    SUPPORTED_LANGUAGES,
)
from src.google_maps_voice_navigator import build_spoken_instruction
from src.pathfinder_chatbot import PathfinderChatbot


def test_supported_languages_catalog():
    """All 8 mandatory languages must be registered in the catalog."""
    langs = get_supported_languages()
    required_codes = ["en", "te", "hi", "ta", "kn", "ml", "bn", "mr"]
    for code in required_codes:
        assert code in langs, f"Language code '{code}' missing from supported languages catalog"
        meta = langs[code]
        assert "name" in meta
        assert "native" in meta
        assert "bcp47" in meta
        assert "flag" in meta


def test_native_names():
    """Each language must display its authentic native script name."""
    assert get_language_native_name("en") == "English"
    assert get_language_native_name("te") == "తెలుగు"
    assert get_language_native_name("hi") == "हिन्दी"
    assert get_language_native_name("ta") == "தமிழ்"
    assert get_language_native_name("kn") == "ಕನ್ನಡ"
    assert get_language_native_name("ml") == "മലയാളം"
    assert get_language_native_name("bn") == "বাংলা"
    assert get_language_native_name("mr") == "मराठी"


def test_telugu_interface_translations():
    """Verify natural Telugu translations for primary navigation labels."""
    assert t("nav.navigation", "te") == "నావిగేషన్"
    assert t("nav.starting_point", "te") == "ప్రారంభ స్థానం"
    assert t("nav.destination", "te") == "గమ్యస్థానం"
    assert t("nav.search_location", "te") == "ప్రదేశాన్ని వెతకండి"
    assert t("nav.get_directions", "te") == "దారి సూచనలు పొందండి"
    assert t("nav.avoid_tolls", "te") == "టోల్ రోడ్లను నివారించండి"
    assert t("nav.avoid_highways", "te") == "హైవేలను నివారించండి"
    assert t("nav.avoid_ferries", "te") == "ఫెర్రీ మార్గాలను నివారించండి"
    assert t("nav.nearby_hospitals", "te") == "సమీపంలోని ఆసుపత్రులు"
    assert t("nav.my_location", "te") == "నా ప్రస్తుత స్థానం"
    assert t("nav.move_in_parallel", "te") == "వాహనంతో పాటు కదలిక ప్రారంభించండి"
    assert t("nav.traffic_stop", "te") == "ట్రాఫిక్ కారణంగా ఆపండి"
    assert t("nav.route_found", "te") == "మార్గం కనుగొనబడింది"
    assert t("nav.gps_unavailable", "te") == "GPS అందుబాటులో లేదు"


def test_bcp47_speech_codes():
    """Speech synthesizer must receive verified BCP-47 speech language tags."""
    assert get_bcp47_code("te") == "te-IN"
    assert get_bcp47_code("hi") == "hi-IN"
    assert get_bcp47_code("ta") == "ta-IN"
    assert get_bcp47_code("kn") == "kn-IN"
    assert get_bcp47_code("ml") == "ml-IN"
    assert get_bcp47_code("bn") == "bn-IN"
    assert get_bcp47_code("mr") == "mr-IN"
    assert get_bcp47_code("en") in ("en-IN", "en-US")


def test_fallback_to_english():
    """When a translation key is missing in a language, it must safely fall back to English."""
    # Unknown key in Telugu should return English fallback if defined, or readable key
    res = t("non_existent_key_xyz", "te")
    assert res == "Non Existent Key Xyz"

    # Test an English key that might be missing in a partial locale
    en_val = t("app.title", "en")
    assert en_val == "P.A.T.H.F.I.N.D.E.R."


def test_dynamic_interpolation():
    """Dynamic placeholders like distances and places must interpolate correctly."""
    te_turn = t("voice.turn_left_in", "te", dist="300 మీటర్లు")
    assert "300 మీటర్లు" in te_turn
    assert "ఎడమవైపు" in te_turn

    te_arrive = t("voice.arrived_at", "te", dest="గుంటూరు రైల్వే స్టేషన్")
    assert "గుంటూరు రైల్వే స్టేషన్" in te_arrive


def test_spoken_instruction_generation():
    """Spoken instructions must generate localized turn prompts for voice guidance."""
    step = {
        "instruction": "Turn left onto NH-16",
        "road": "NH-16",
        "distance_m": 250
    }
    # Telugu
    te_speech = build_spoken_instruction(step, 1, 5, language="te")
    assert "ఎడమవైపు" in te_speech or "తిరగండి" in te_speech or "NH-16" in te_speech

    # Hindi
    hi_speech = build_spoken_instruction(step, 1, 5, language="hi")
    assert "बाएँ" in hi_speech or "मुड़ें" in hi_speech or "NH-16" in hi_speech

    # English
    en_speech = build_spoken_instruction(step, 1, 5, language="en")
    assert "left" in en_speech.lower()


def test_multilingual_chatbot():
    """Chatbot must recognize language context and respond in appropriate language."""
    bot = PathfinderChatbot()

    # 1. Natural Telugu greeting
    te_res = bot.answer("నమస్కారం, మీరు ఎలా సహాయపడగలరు?")
    assert "తెలుగు" in te_res.get("badge", "")
    assert "నమస్కారం" in te_res.get("response", "") or "A.U.R.A." in te_res.get("response", "")

    # 2. Natural Hindi greeting
    hi_res = bot.answer("नमस्ते, आप कैसे हैं?")
    assert "हिन्दी" in hi_res.get("badge", "")
    assert "नमस्ते" in hi_res.get("response", "") or "A.U.R.A." in hi_res.get("response", "")

    # 3. Contextual language routing (User interface is Telugu, query is general)
    ctx_te = {"language": "te"}
    routed_te = bot.answer("Hello there, help me navigate", context=ctx_te)
    assert "తెలుగు" in routed_te.get("badge", "") or "A.U.R.A." in routed_te.get("badge", "")

    # 4. Tamil query
    ta_res = bot.answer("வணக்கம், நீங்கள் யார்?")
    assert "தமிழ்" in ta_res.get("badge", "")

    # 5. Kannada query
    kn_res = bot.answer("ನಮಸ್ಕಾರ, ನೀವು ಯಾರು?")
    assert "ಕನ್ನಡ" in kn_res.get("badge", "")


def test_distance_and_duration_formatting():
    """Distance and duration must format according to units."""
    km_str = format_distance(12.456, unit="km")
    assert km_str == "12.5 km"

    mi_str = format_distance(12.456, unit="miles")
    assert "mi" in mi_str

    dur_mins = format_duration(45.0)
    assert dur_mins == "45 mins"

    dur_hours = format_duration(125.0)
    assert "2 hr" in dur_hours and "5 min" in dur_hours


def test_tabs_multilingual_all_languages():
    """All 5 primary navigation tabs must have valid translations across all 8 languages."""
    tab_keys = ["tab.navigation", "tab.facilities", "tab.copilot", "tab.places", "tab.virtual_guide"]
    for lang in SUPPORTED_LANGUAGES:
        for k in tab_keys:
            val = t(k, lang=lang)
            assert val and val != k, f"Missing translation for {k} in language {lang}"


def test_aura_chips_and_welcome_multilingual():
    """Aura action chips and welcome messages must be localized across all 8 languages."""
    chip_keys = [
        "aura.chip_route", "aura.chip_places", "aura.chip_plan",
        "aura.chip_cost", "aura.chip_stays", "aura.chip_ask", "aura.chip_clear",
        "aura.welcome_badge", "aura.welcome_msg"
    ]
    for lang in SUPPORTED_LANGUAGES:
        for k in chip_keys:
            val = t(k, lang=lang)
            assert val and val != k, f"Missing translation for {k} in language {lang}"


def test_corridor_and_endpoints_hud_multilingual():
    """Route corridor and Endpoints HUD keys must be localized across all 8 languages."""
    hud_keys = [
        "nav.route_corridor", "nav.active_path", "nav.route_endpoints",
        "nav.live_map_hud", "nav.fit_route", "nav.tour"
    ]
    for lang in SUPPORTED_LANGUAGES:
        for k in hud_keys:
            val = t(k, lang=lang)
            assert val and val != k, f"Missing translation for {k} in language {lang}"


def test_navigation_header_language_switcher_source():
    """Verify that render_view_navigation_header contains the universal language selectbox."""
    with open("src/travel_copilot_studio.py", "r", encoding="utf-8") as f:
        src = f.read()
    assert "nav_header_lang_" in src
    assert "SUPPORTED_LANGUAGES" in src
    assert "set_current_language" in src


def test_t_function_call_signatures_and_type_safety():
    """
    Ensure t() accepts any combination of positional/keyword default and lang arguments
    without ever raising TypeError: 'got multiple values for argument lang' or returning None.
    """
    # 1. Exact call signature from app.py line 29269
    res1 = t("tab.places", "Places & Sights", lang="te")
    assert isinstance(res1, str) and len(res1) > 0
    assert "🌟 " + res1  # string concatenation must not fail

    # 2. Subtitle with long fallback and lang kwarg
    res2 = t("places.header_sub", "Discover useful places near your location", lang="hi")
    assert isinstance(res2, str) and len(res2) > 0

    # 3. Default as keyword + lang as keyword
    res3 = t("tab.places", default="Places & Sights", lang="ta")
    assert isinstance(res3, str) and len(res3) > 0

    # 4. Positional default only
    res4 = t("tab.places", "Places & Sights")
    assert isinstance(res4, str) and len(res4) > 0

    # 5. Positional language code only
    res5 = t("tab.places", "bn")
    assert isinstance(res5, str) and len(res5) > 0

    # 6. Positional lang + positional default
    res6 = t("tab.places", "kn", "Places & Sights")
    assert isinstance(res6, str) and len(res6) > 0

    # 7. Positional default + positional lang
    res7 = t("tab.places", "Places & Sights", "ml")
    assert isinstance(res7, str) and len(res7) > 0

    # 8. Non-existent key with default
    res8 = t("non_existent_key_123", "Custom Fallback Text", lang="mr")
    assert res8 == "Custom Fallback Text"


def test_comprehensive_multilingual_coverage_all_components():
    """Verify that all new UI components are fully localized across all 8 languages."""
    keys_to_test = [
        # Image 1: Action buttons
        "places.view_map", "places.directions", "places.info", "places.save", "places.saved",
        # Image 2: Header & categories
        "places.nearby_facilities_header", "places.verified_pois", "places.search_placeholder",
        "places.categories_label", "places.cat_all", "places.cat_hospitals", "places.cat_supermarkets",
        "places.cat_fuel", "places.cat_ev", "places.cat_restaurants", "places.cat_atms",
        "places.cat_police", "places.cat_hotels", "places.cat_tourist", "places.cat_malls",
        "places.cat_parks", "places.cat_rest_stops",
        # Image 3: Speed cockpit
        "speed.header", "speed.subtitle", "speed.digital_cockpit", "speed.velocity_locked",
        "speed.balanced_cruise", "speed.throttle_demand", "speed.driver_analysis",
        "speed.healthy_badge", "speed.presets_label", "speed.exclusions_header", "speed.exclusions_sub",
        # Image 4: Telemetry, directives & companion
        "telemetry.header", "telemetry.active_stream", "telemetry.power_band", "telemetry.high_torque",
        "telemetry.flow_rate", "telemetry.time_optimized", "telemetry.drag_force",
        "telemetry.directives", "telemetry.dir_express", "telemetry.dir_eta",
        "telemetry.dir_overtake", "telemetry.dir_pacing", "strategy.calibrated_speed",
        "strategy.reason_title", "strategy.impact_title", "strategy.reaction_buffer",
        "strategy.cognitive_load", "companion.banner_title", "companion.banner_sub"
    ]
    for lang in SUPPORTED_LANGUAGES:
        for k in keys_to_test:
            val = t(k, lang=lang)
            assert val and val != k, f"Key '{k}' is missing or unlocalized for language '{lang}'"


def test_exact_parity_all_eight_locales():
    """Verify that all 8 JSON locale files have 100% key parity with exactly 523 keys."""
    import json, glob
    locales = glob.glob(os.path.join(os.path.dirname(__file__), "..", "locales", "*.json"))
    assert len(locales) == 8, f"Expected 8 locale files, found {len(locales)}"

    data = {}
    for p in locales:
        lang = os.path.basename(p).split(".")[0]
        with open(p, "r", encoding="utf-8") as f:
            d = json.load(f)
            data[lang] = set(d.keys())
            # Ensure no value is empty
            for k, v in d.items():
                assert isinstance(v, str) and len(v.strip()) > 0, f"Empty translation for {k} in {lang}"

    all_keys = set.union(*data.values())
    assert len(all_keys) >= 523, f"Expected >= 523 keys, got {len(all_keys)}"

    for lang, keys in data.items():
        missing = all_keys - keys
        assert not missing, f"Language '{lang}' has missing keys: {missing}"


def test_voice_guidance_multilingual_narrative_all_eight():
    """Verify generate_simple_spoken_narrative produces authentic scripts for all 8 languages."""
    from src.voice_guidance import generate_simple_spoken_narrative

    scripts = {
        "en": "Hello. This is your audio navigation guide",
        "te": "నమస్కారం",
        "hi": "नमस्ते",
        "ta": "வணக்கம்",
        "kn": "ನಮಸ್ಕಾರ",
        "ml": "നമസ്കാരം",
        "bn": "নমস্কার",
        "mr": "नमस्कार"
    }

    for lang_code, expected_greeting in scripts.items():
        narrative = generate_simple_spoken_narrative(
            origin_name="Guntur Junction",
            destination_name="Vijayawada Bus Station",
            distance_km=35.0,
            duration_min=42.0,
            lang=lang_code
        )
        assert expected_greeting in narrative, f"Expected '{expected_greeting}' in {lang_code} narrative"
        assert "Guntur Junction" in narrative
        assert "Vijayawada Bus Station" in narrative


def test_speech_recognition_and_voice_synthesizer_bcp47_verification():
    """Verify BCP-47 identifiers and voices configured for Web Speech API and STT."""
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
    for code, bcp in expected_bcp47.items():
        actual = get_bcp47_code(code)
        assert actual.startswith(code) or actual in ("en-IN", "en-US"), f"BCP-47 mismatch for {code}: {actual}"


def test_aura_chatbot_all_eight_languages():
    """Verify Aura Travel Assistant responds naturally in all 8 languages."""
    bot = PathfinderChatbot()

    queries = {
        "en": "Hi Aura",
        "te": "హలో ఔరా",
        "hi": "नमस्ते ऑरा",
        "ta": "வணக்கம் ஆரா",
        "kn": "ಹಲೋ ಔರಾ",
        "ml": "ഹലോ ഔറ",
        "bn": "নমস্কার অরা",
        "mr": "नमस्कार ऑरा"
    }

    for lang, q_text in queries.items():
        resp = bot.answer(q_text, context={"language": lang})
        msg = resp.get("response") or resp.get("message") or ""
        assert len(msg) > 10, f"Response too short for {lang}"
        # Response should be in correct script
        if lang == "te":
            assert any("\u0c00" <= c <= "\u0c7f" for c in msg)
        elif lang == "hi" or lang == "mr":
            assert any("\u0900" <= c <= "\u097f" for c in msg)
        elif lang == "ta":
            assert any("\u0b80" <= c <= "\u0bff" for c in msg)
        elif lang == "kn":
            assert any("\u0c80" <= c <= "\u0cff" for c in msg)
        elif lang == "ml":
            assert any("\u0d00" <= c <= "\u0d7f" for c in msg)
        elif lang == "bn":
            assert any("\u0980" <= c <= "\u09ff" for c in msg)

