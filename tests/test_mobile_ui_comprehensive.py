# -*- coding: utf-8 -*-
"""
Tests for Complete Mobile Responsive UI Fix and Optimization in NexRoute.
Verifies:
1. Text clipping prevention, responsive typography, and multilingual support across all 8 languages.
2. Card and container boundaries, zero horizontal overflow, consistent borders and padding.
3. Tab navigation ribbon (horizontal swipe, no wrapping, active highlight), bottom navigation dock.
4. Button responsiveness, touch targets (>= 44px), input field iOS zoom prevention (16px).
5. Google Maps floating header auto-flow (toolbar + filter bar without overlap).
"""

import pytest
from src.mobile_bottom_nav import render_mobile_bottom_navigation_bar, MOBILE_NAV_TRANSLATIONS
from src.google_maps_platform import build_google_maps_javascript_html
from src.i18n import SUPPORTED_LANGUAGES, t


class TestMobileTextTypographyAndMultilingual:
    def test_text_overflow_and_word_break_rules_in_app_css(self):
        with open("app.py", "r", encoding="utf-8") as f:
            css = f.read()

        # Word-break and overflow-wrap prevention rules
        assert "word-break: break-word !important;" in css
        assert "overflow-wrap: break-word !important;" in css

    def test_heading_responsive_clamp_scales(self):
        with open("app.py", "r", encoding="utf-8") as f:
            css = f.read()

        assert "clamp(" in css
        assert "h1, .qr-hero-heading" in css

    def test_button_text_wrapping_prevents_clipping(self):
        with open("app.py", "r", encoding="utf-8") as f:
            css = f.read()

        # Buttons must wrap text gracefully on small screens instead of single-line truncation
        assert "white-space: normal !important;" in css
        assert "min-height: 44px !important;" in css

    def test_multilingual_font_family_support_all_8_languages(self):
        with open("app.py", "r", encoding="utf-8") as f:
            css = f.read()

        for script in ["Telugu", "Devanagari", "Tamil", "Kannada", "Malayalam", "Bengali"]:
            assert f"Noto Sans {script}" in css


class TestMobileBordersAndContainerBoundaries:
    def test_root_viewport_overflow_contained(self):
        with open("app.py", "r", encoding="utf-8") as f:
            css = f.read()

        assert "overflow-x: hidden !important;" in css
        assert "max-width: 100vw !important;" in css
        assert "box-sizing: border-box !important;" in css

    def test_column_flex_min_width_zero(self):
        with open("app.py", "r", encoding="utf-8") as f:
            css = f.read()

        # Crucial for preventing flex children from stretching outside parent viewport
        assert "div[data-testid=\"stColumn\"] {" in css
        assert "min-width: 0 !important;" in css

    def test_safe_area_insets_respected(self):
        with open("app.py", "r", encoding="utf-8") as f:
            css = f.read()

        assert "env(safe-area-inset-top" in css
        assert "env(safe-area-inset-bottom" in css
        assert "env(safe-area-inset-left" in css
        assert "env(safe-area-inset-right" in css


class TestMobileTabsAndNavigation:
    def test_tablist_horizontal_scroll_ribbon(self):
        with open("app.py", "r", encoding="utf-8") as f:
            css = f.read()

        assert "div[data-testid=\"stTabs\"] [role=\"tablist\"]" in css
        assert "overflow-x: auto !important;" in css
        assert "flex-wrap: nowrap !important;" in css
        assert "scrollbar-width: none !important;" in css

    def test_tab_touch_targets_and_highlighting(self):
        with open("app.py", "r", encoding="utf-8") as f:
            css = f.read()

        assert "div[data-testid=\"stTabs\"] [role=\"tab\"]" in css
        assert "div[data-testid=\"stTabs\"] [role=\"tab\"][aria-selected=\"true\"]" in css

    def test_mobile_bottom_nav_touch_targets_and_insets(self):
        html = render_mobile_bottom_navigation_bar(current_view="dashboard", lang="en")
        assert "min-height: 48px !important;" in html
        assert "env(safe-area-inset-bottom, 0px)" in html
        assert "z-index: 9999999 !important;" in html


class TestMobileButtonsAndInputs:
    def test_ios_input_zoom_prevention_16px(self):
        with open("app.py", "r", encoding="utf-8") as f:
            css = f.read()

        assert "font-size: 16px !important;" in css
        assert "div[data-testid=\"stTextInput\"] input" in css
        assert "div[data-testid=\"stSelectbox\"] select" in css

    def test_touch_action_manipulation_on_interactive_elements(self):
        with open("app.py", "r", encoding="utf-8") as f:
            css = f.read()

        assert "touch-action: manipulation !important;" in css
        assert "-webkit-tap-highlight-color: transparent !important;" in css


class TestGoogleMapsMobileHeaderFlow:
    def test_google_maps_floating_header_structure(self):
        html = build_google_maps_javascript_html(16.50, 80.64)
        # Floating header wraps both toolbar and filter bar
        assert "class=\"gmap-floating-header\"" in html
        assert "class=\"gmap-toolbar\"" in html
        assert "class=\"gmap-filter-bar\"" in html

    def test_google_maps_mobile_css_compass_and_drawers(self):
        html = build_google_maps_javascript_html(16.50, 80.64)
        assert "@media (max-width: 768px)" in html
        assert ".gmap-floating-header" in html
        assert ".gmap-compass-container" in html
        assert ".gmap-layers-drawer" in html
        assert ".gmap-place-drawer" in html

