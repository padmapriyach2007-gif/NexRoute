# -*- coding: utf-8 -*-
"""
Tests for comprehensive mobile responsiveness across all smartphone form factors.
"""

import pytest
from src.aura_welcome_screen import render_aura_welcome_hud
from src.aura_journey_engine import build_aura_journey_cockpit_html, AuraManeuverStep


def test_aura_welcome_screen_mobile_css():
    html = render_aura_welcome_hud(current_lang="en")
    # Verify mobile breakpoints exist in welcome screen CSS
    assert "@media (max-width: 820px)" in html
    assert "@media (max-width: 540px)" in html
    assert "@media (max-width: 375px)" in html
    # Verify mobile grid for orbital modules
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in html
    # Verify touch-action manipulation for fast mobile tap
    assert "touch-action: manipulation" in html


def test_aura_journey_engine_mobile_css():
    step = AuraManeuverStep(
        step_num=1,
        total_steps=1,
        direction_type="straight",
        headline="Start Out",
        instruction="Head north",
        spoken_text="Head north",
        aura_speech="Let's go",
        road_name="Main St",
        distance_m=100.0,
        distance_human="100 m",
        time_estimate="1 min",
        icon="🚗",
    )
    html = build_aura_journey_cockpit_html(
        origin_name="Start",
        dest_name="Dest",
        travel_mode="car",
        total_distance_km=1.0,
        total_duration_mins=2.0,
        maneuvers=[step],
        current_step_idx=0,
        lang="en",
    )
    # Verify mobile responsive styles exist in journey engine
    assert "@media (max-width: 768px)" in html
    assert "@media (max-width: 375px)" in html
    # Verify swipeable vehicle selector carousel on mobile
    assert "-webkit-overflow-scrolling: touch" in html
    # Verify compact clamp scene height
    assert "clamp(200px, 34vh, 280px)" in html


def test_app_mobile_meta_and_css():
    with open("app.py", "r", encoding="utf-8") as f:
        app_code = f.read()

    # Verify mobile viewport meta tag
    assert "width=device-width, initial-scale=1, maximum-scale=5.0, viewport-fit=cover" in app_code
    # Verify theme-color and apple-mobile-web-app-capable
    assert "apple-mobile-web-app-capable" in app_code
    assert "theme-color" in app_code
    # Verify touch manipulation and iOS zoom prevention
    assert "touch-action: manipulation !important" in app_code
    assert "font-size: 16px !important" in app_code

