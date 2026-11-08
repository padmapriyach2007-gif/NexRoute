"""
Unit tests for NextRoute - AI Voice Flashcard Beside NexRoute Hero Card.
Verifies:
1. Side-by-side arrangement of NexRoute Title Card and AURA Voice Assistant Flashcard.
2. Styling of .qr-hero-card-side with matching 435px height, neon edge glow, and glassmorphic telemetry.
3. Separation of hero title card from the multilingual selection runway and 4 workspace cards.
4. Seamless integration with Streamlit dashboard view.
"""

import pytest
from src.travel_copilot_studio import (
    render_quantum_hero_title_card,
    render_quantum_hero_section,
    QUANTUM_REALM_CSS,
    DASHBOARD_I18N
)


class TestHeroSideBySideLayout:
    def test_quantum_realm_css_contains_side_card_styling(self):
        """QUANTUM_REALM_CSS must contain .qr-hero-card-side styles matching the 435px HUD height."""
        assert ".qr-hero-card-side" in QUANTUM_REALM_CSS
        assert "435px" in QUANTUM_REALM_CSS
        assert "radial-gradient" in QUANTUM_REALM_CSS
        assert "qr-hero-grid-overlay" in QUANTUM_REALM_CSS
        assert "qr-hero-ambient-flare" in QUANTUM_REALM_CSS

    def test_render_quantum_hero_title_card_side_by_side(self, monkeypatch):
        """render_quantum_hero_title_card(side_by_side=True) must output .qr-hero-card-side."""
        rendered_markdown = []

        import streamlit as st
        monkeypatch.setattr(st, "markdown", lambda text, **kwargs: rendered_markdown.append(text))
        monkeypatch.setattr(st, "session_state", {"app_language": "en"})

        render_quantum_hero_title_card(side_by_side=True)

        assert len(rendered_markdown) > 0
        output = rendered_markdown[0]
        assert "qr-hero-card-side" in output
        assert "pathfinder-hero-wrapper" in output
        assert "pathfinder-hero-title" in output
        assert "🧭" in output
        assert "NEXROUTE" in output
        assert "AUTONOMOUS AI TRAVEL & ADAPTIVE NAVIGATION SYSTEM" in output

    def test_render_quantum_hero_title_card_full_width(self, monkeypatch):
        """render_quantum_hero_title_card(side_by_side=False) must output standard wrapper without .qr-hero-card-side."""
        rendered_markdown = []

        import streamlit as st
        monkeypatch.setattr(st, "markdown", lambda text, **kwargs: rendered_markdown.append(text))
        monkeypatch.setattr(st, "session_state", {"app_language": "en"})

        render_quantum_hero_title_card(side_by_side=False)

        assert len(rendered_markdown) > 0
        output = rendered_markdown[0]
        assert "qr-hero-card-side" not in output
        assert "qr-hero-wrapper" in output
        assert "NEXROUTE" in output

    def test_render_quantum_hero_section_without_title(self, monkeypatch):
        """render_quantum_hero_section(include_title=False) renders runway bar & cards without hero title banner."""
        rendered_markdown = []

        import streamlit as st
        monkeypatch.setattr(st, "markdown", lambda text, **kwargs: rendered_markdown.append(text))
        monkeypatch.setattr(st, "session_state", {"app_language": "en"})

        title_rendered = []
        def mock_title_card(*args, **kwargs):
            title_rendered.append(True)

        monkeypatch.setattr("src.travel_copilot_studio.render_quantum_hero_title_card", mock_title_card)
        monkeypatch.setattr("src.travel_copilot_studio.render_main_language_bar", lambda: None)

        render_quantum_hero_section(include_title=False)

        assert len(title_rendered) == 0

    def test_app_py_implements_side_by_side_columns(self):
        """app.py dashboard view must place NexRoute hero card beside AURA Voice HUD using st.columns."""
        with open("app.py", "r", encoding="utf-8") as f:
            app_code = f.read()

        assert "col_hero, col_aura = st.columns([1, 1.35], gap=\"medium\")" in app_code
        assert "render_quantum_hero_title_card(side_by_side=True)" in app_code
        assert "components.html(welcome_hud_html, height=435, scrolling=False)" in app_code
        assert "render_quantum_hero_section(include_title=False)" in app_code
