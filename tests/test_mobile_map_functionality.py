# -*- coding: utf-8 -*-
"""
Tests for Mobile Map Implementation, GPS Precision, Touch Interactions,
Turn-by-Turn Navigation HUD, and cur_l Global Availability.
"""

import pytest
import builtins
import re
from src.google_maps_platform import build_google_maps_javascript_html
from src.i18n import SUPPORTED_LANGUAGES, t, set_current_language


class TestMobileMapFunctionality:
    def test_cur_l_always_in_builtins(self):
        """Verifies cur_l is available in builtins without raising NameError."""
        assert hasattr(builtins, "cur_l")
        assert builtins.cur_l in SUPPORTED_LANGUAGES

    def test_set_current_language_updates_builtins_cur_l(self):
        """Verifies changing language updates builtins.cur_l."""
        set_current_language("te")
        assert builtins.cur_l == "te"
        set_current_language("en")
        assert builtins.cur_l == "en"

    def test_mobile_map_touch_options(self):
        """Verifies Leaflet map is initialized with full mobile touch options."""
        html = build_google_maps_javascript_html(
            center_lat=16.3067,
            center_lon=80.4365,
            zoom=14,
            origin_coords=(16.3067, 80.4365),
            dest_coords=(16.5062, 80.6480)
        )
        assert "tap: true" in html
        assert "touchZoom: true" in html
        assert "doubleClickZoom: true" in html
        assert "dragging: true" in html
        assert "tapTolerance: 15" in html

    def test_mobile_map_resize_observer_and_orientation(self):
        """Verifies dynamic map size invalidation on resize and orientation change."""
        html = build_google_maps_javascript_html(
            center_lat=16.3067,
            center_lon=80.4365,
            zoom=14
        )
        assert "orientationchange" in html
        assert "ResizeObserver" in html
        assert "lMap.invalidateSize()" in html

    def test_high_accuracy_gps_and_error_handling(self):
        """Verifies browser GPS uses high accuracy and user-friendly error messages."""
        html = build_google_maps_javascript_html(
            center_lat=16.3067,
            center_lon=80.4365,
            zoom=14
        )
        assert "enableHighAccuracy: true" in html
        assert "timeout: 15000" in html
        assert "maximumAge: 0" in html
        assert "Location access was denied" in html
        assert "Position unavailable" in html
        assert "GPS request timed out" in html

    def test_compact_mobile_toolbar_buttons(self):
        """Verifies compact mobile toolbar buttons and touch target sizes."""
        html = build_google_maps_javascript_html(
            center_lat=16.3067,
            center_lon=80.4365,
            zoom=14
        )
        assert "gmap-btn-text-short" in html
        assert "gmap-btn-text-full" in html
        assert "📍 GPS" in html
        assert "🎯 Fit" in html

    def test_responsive_map_css_in_app_py(self):
        """Verifies app.py contains responsive CSS rules for map iframes on mobile."""
        with open("app.py", "r", encoding="utf-8") as f:
            code = f.read()

        assert "div[data-testid=\"stCustomComponentV1\"] iframe[title*=\"st.iframe\"]" in code
        assert "height: 485px !important;" in code or "height: 440px !important;" in code
        assert "max-height: 68vh !important;" in code or "max-height: 62vh !important;" in code
        assert "@media (max-width: 900px) and (orientation: landscape)" in code

    def test_turn_by_turn_hud_in_app_py(self):
        """Verifies turn-by-turn HUD code is integrated into app.py."""
        with open("app.py", "r", encoding="utf-8") as f:
            code = f.read()

        assert "generate_friendly_virtual_guide_turns" in code
        assert "btn_mobile_nav_prev" in code
        assert "btn_mobile_nav_next" in code
        assert "btn_mobile_nav_stop" in code
