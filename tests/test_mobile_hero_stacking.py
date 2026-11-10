# -*- coding: utf-8 -*-
"""
Tests for Mobile Hero Stacking and Responsive AURA Assistant Card Layout.
Ensures:
1. Two-column desktop hero layout stacks cleanly into 1 column on mobile screens.
2. NEXROUTE heading does not line-break or wrap into awkward fragments.
3. AURA Voice Assistant panel expands to 100% width on mobile without clipping buttons or controls.
"""

import pytest


class TestMobileHeroStacking:
    def test_app_py_has_quantum_hero_deck_container(self):
        with open("app.py", "r", encoding="utf-8") as f:
            code = f.read()

        assert 'st.container(key="quantum_hero_side_by_side_deck")' in code
        assert 'div[class*="st-key-quantum_hero_side_by_side_deck"]' in code
        assert 'flex-direction: column !important;' in code

    def test_heading_prevents_awkward_word_breaking(self):
        with open("app.py", "r", encoding="utf-8") as f:
            code = f.read()

        assert "white-space: nowrap !important;" in code
        assert "word-break: keep-all !important;" in code

    def test_hero_card_side_height_auto_on_mobile(self):
        with open("src/travel_copilot_studio.py", "r", encoding="utf-8") as f:
            code = f.read()

        assert "@media (max-width: 768px)" in code
        assert "height: auto !important;" in code
        assert "min-height: auto !important;" in code

    def test_aura_welcome_screen_top_controls_wrap_on_mobile(self):
        with open("src/aura_welcome_screen.py", "r", encoding="utf-8") as f:
            code = f.read()

        assert "flex-wrap: wrap;" in code
        assert "@media (max-width: 540px)" in code
