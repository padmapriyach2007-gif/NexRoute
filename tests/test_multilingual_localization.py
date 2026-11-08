# -*- coding: utf-8 -*-
"""
Tests for Full Multilingual Localization across all 8 supported languages.
Languages: English (en), Telugu (te), Hindi (hi), Tamil (ta), Kannada (kn), Malayalam (ml), Bengali (bn), Marathi (mr).
"""

import pytest
from src.i18n import t, SUPPORTED_LANGUAGES
from src.aura_welcome_screen import render_aura_welcome_hud
from src.aura_journey_engine import build_aura_journey_cockpit_html, AuraManeuverStep


ALL_LANGS = ["en", "te", "hi", "ta", "kn", "ml", "bn", "mr"]


def test_all_8_languages_supported():
    for lang in ALL_LANGS:
        assert lang in SUPPORTED_LANGUAGES, f"{lang} missing from SUPPORTED_LANGUAGES"


@pytest.mark.parametrize("lang", ALL_LANGS)
def test_brand_and_hud_keys_exist_in_all_languages(lang):
    keys = [
        "aura.brand_title",
        "aura.brand_sub",
        "aura.brand_pill",
        "aura.btn_start",
        "aura.btn_pause",
        "aura.btn_resume",
        "aura.btn_end",
        "aura.status_offline",
        "aura.status_listening",
        "aura.status_speaking",
        "aura.status_ready",
        "nav.module_title",
        "nav.module_sub",
        "hotels.module_title",
        "hotels.module_sub",
        "flights.module_title",
        "flights.module_sub",
        "food.module_title",
        "food.module_sub",
        "nav.clear_start",
        "nav.clear_dest",
        "nav.clear_all_locations",
        "nav.swap_locations",
        "nav.pick_start_map",
        "nav.pick_dest_map",
        "nav.focus_start",
        "nav.focus_dest",
        "nav.fit_both",
        "nav.add_stop_expander",
        "cat.dining",
        "cat.fuel",
        "cat.medical",
        "cat.atm",
        "cat.hotel",
        "cat.tourist",
        "guide.prev_step",
        "guide.next_step",
        "guide.travel_vehicle",
        "mode.car",
        "mode.bike",
        "mode.bus",
        "mode.cycle",
        "mode.walk",
    ]
    for key in keys:
        val = t(key, lang=lang)
        assert val != key, f"Missing translation for key '{key}' in lang '{lang}'"
        assert len(val.strip()) > 0


def test_aura_welcome_hud_renders_telugu():
    html = render_aura_welcome_hud(current_lang="te")
    assert "నెక్స్" in html or "నెక్స్‌రూట్" in html
    assert "నావిగేషన్" in html
    assert "హోటళ్ళు" in html
    assert "విమానాలు" in html
    assert "రెస్టారెంట్లు" in html


def test_aura_welcome_hud_renders_hindi():
    html = render_aura_welcome_hud(current_lang="hi")
    assert "नेक्सरूट" in html
    assert "नेविगेशन" in html
    assert "होटल" in html
    assert "उड़ानें" in html
    assert "रेस्टोरेंट" in html


def test_aura_welcome_hud_renders_tamil():
    html = render_aura_welcome_hud(current_lang="ta")
    assert "நெக்ஸ்ரூட்" in html
    assert "வழிகாட்டல்" in html
    assert "விடுதிகள்" in html
    assert "விமானங்கள்" in html
    assert "உணவகங்கள்" in html


def test_journey_copilot_html_renders_multilingual_modes():
    step = AuraManeuverStep(
        step_num=1,
        total_steps=1,
        direction_type="straight",
        headline="Start Out",
        instruction="Head north",
        spoken_text="Head north",
        aura_speech="Let's head north",
        road_name="Main St",
        distance_m=100.0,
        distance_human="100 m",
        time_estimate="1 min",
        icon="🚗",
    )

    # Telugu copilot HTML
    html_te = build_aura_journey_cockpit_html(
        origin_name="Origin",
        dest_name="Destination",
        travel_mode="car",
        total_distance_km=1.0,
        total_duration_mins=2.0,
        maneuvers=[step],
        current_step_idx=0,
        lang="te",
    )
    # Check that Telugu vehicle name "కారు" or toolbar appears
    assert "కారు" in html_te or "ప్రయాణ వాహనం" in html_te

    # Hindi copilot HTML
    html_hi = build_aura_journey_cockpit_html(
        origin_name="Origin",
        dest_name="Destination",
        travel_mode="car",
        total_distance_km=1.0,
        total_duration_mins=2.0,
        maneuvers=[step],
        current_step_idx=0,
        lang="hi",
    )
    assert "कार" in html_hi or "यात्रा वाहन" in html_hi
