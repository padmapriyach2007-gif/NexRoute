# -*- coding: utf-8 -*-
"""
Tests for Mobile Responsiveness, Layout, and Mobile Bottom Navigation Bar.
Verifies touch optimization, multi-language support, responsive CSS rules,
and desktop invisibility.
"""

import pytest
from src.mobile_bottom_nav import render_mobile_bottom_navigation_bar, MOBILE_NAV_TRANSLATIONS
from src.google_maps_platform import build_google_maps_javascript_html


class TestMobileBottomNav:
    def test_all_five_views_present(self):
        html = render_mobile_bottom_navigation_bar(current_view="dashboard", lang="en")
        assert "id=\"nexroute-mobile-bottom-nav\"" in html
        assert "?view=dashboard" in html
        assert "?view=map_nav" in html
        assert "?view=copilot_studio" in html
        assert "?view=places" in html
        assert "?view=virtual_guide" in html

    def test_active_tab_highlighting(self):
        # Dashboard active
        html_dash = render_mobile_bottom_navigation_bar(current_view="dashboard", lang="en")
        assert 'href="?view=dashboard" target="_top" class="mobile-nav-item active"' in html_dash
        assert 'href="?view=map_nav" target="_top" class="mobile-nav-item"' in html_dash

        # Map active (including aliases)
        for map_alias in ["map_nav", "map", "nav", "navigation"]:
            html_map = render_mobile_bottom_navigation_bar(current_view=map_alias, lang="en")
            assert 'href="?view=map_nav" target="_top" class="mobile-nav-item active"' in html_map

        # Trips / Copilot active
        for studio_alias in ["copilot_studio", "copilot", "studio"]:
            html_studio = render_mobile_bottom_navigation_bar(current_view=studio_alias, lang="en")
            assert 'href="?view=copilot_studio" target="_top" class="mobile-nav-item active"' in html_studio

        # Places active
        for places_alias in ["places", "sights"]:
            html_places = render_mobile_bottom_navigation_bar(current_view=places_alias, lang="en")
            assert 'href="?view=places" target="_top" class="mobile-nav-item active"' in html_places

        # Virtual Guide active
        for guide_alias in ["virtual_guide", "guide"]:
            html_guide = render_mobile_bottom_navigation_bar(current_view=guide_alias, lang="en")
            assert 'href="?view=virtual_guide" target="_top" class="mobile-nav-item active"' in html_guide

    def test_multilingual_labels_for_all_eight_languages(self):
        expected_langs = ["en", "te", "hi", "ta", "kn", "ml", "bn", "mr"]
        for lang in expected_langs:
            assert lang in MOBILE_NAV_TRANSLATIONS
            labels = MOBILE_NAV_TRANSLATIONS[lang]
            html = render_mobile_bottom_navigation_bar(current_view="dashboard", lang=lang)
            for key in ["home", "map", "trips", "places", "guide"]:
                assert labels[key] in html

    def test_telugu_and_hindi_specific_content(self):
        html_te = render_mobile_bottom_navigation_bar(current_view="map_nav", lang="te")
        assert "హోమ్" in html_te
        assert "మ్యాప్" in html_te
        assert "ప్రదేశాలు" in html_te

        html_hi = render_mobile_bottom_navigation_bar(current_view="virtual_guide", lang="hi")
        assert "होम" in html_hi
        assert "मैप" in html_hi
        assert "गाइड" in html_hi

    def test_desktop_invisibility_css_rules(self):
        html = render_mobile_bottom_navigation_bar(current_view="dashboard", lang="en")
        # Hidden on desktop (> 768px)
        assert "@media (min-width: 769px)" in html
        assert "display: none !important" in html
        assert "visibility: hidden !important" in html

    def test_mobile_dock_css_rules(self):
        html = render_mobile_bottom_navigation_bar(current_view="dashboard", lang="en")
        # Visible on mobile (<= 768px)
        assert "@media (max-width: 768px)" in html
        assert "position: fixed !important" in html
        assert "bottom: 0 !important" in html
        assert "env(safe-area-inset-bottom, 0px)" in html
        assert "z-index: 9999999 !important" in html
        # Touch target minimum 48px
        assert "min-height: 48px !important" in html

    def test_touch_and_accessibility_attributes(self):
        html = render_mobile_bottom_navigation_bar(current_view="dashboard", lang="en")
        assert 'role="tab"' in html
        assert 'aria-selected="true"' in html
        assert 'aria-selected="false"' in html
        assert 'aria-label="Mobile Navigation Bar"' in html
        assert 'target="_top"' in html


class TestGoogleMapsMobileLayout:
    def test_google_maps_mobile_css_toolbar(self):
        sample_routes = [{
            "summary": "Primary Route",
            "distance_km": 10.5,
            "duration_mins": 15,
            "color": "#00f0b5",
            "overview_polyline": "abc_polyline"
        }]
        html = build_google_maps_javascript_html(16.25, 80.63, routes=sample_routes)
        # Check that mobile media query exists in map HTML
        assert "@media (max-width: 768px)" in html
        assert ".gmap-toolbar" in html
        assert ".gmap-search-wrapper" in html
        assert ".gmap-filter-bar" in html
