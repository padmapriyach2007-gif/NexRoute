"""
Unit tests for NextRoute AURA Dashboard - Creative Futuristic Holographic UI Redesign.
Verifies:
1. Complete removal of the rectangular Profile shortcut from the main AURA dashboard.
2. Presence and configuration of the 5 primary holographic travel modules:
   - Navigation (Corridor Routing)
   - My Trips (Itinerary Studio)
   - Hotels (Stays & Resorts)
   - Flights (Air Corridors)
   - Restaurants (Dining & Food)
3. Central Holographic AURA Robot centerpiece with multi-ring reactor, waveform, and transcript.
4. Holographic Orbital Stage with SVG neural energy conduits, animated pulse beams, and reticles.
5. Interactive hover beam highlighting and click dispatching.
6. Mobile & tablet responsive adaptations with zero-overflow layout.
7. Profile page remaining fully accessible through application commands without dashboard card.
"""

import pytest
from src.aura_welcome_screen import render_aura_welcome_hud
from src.aura_command_dispatcher import (
    AuraGlobalCommandDispatcher,
    AuraCommandType,
)


class TestAuraDashboardHolographicRedesign:
    @pytest.fixture
    def hud_html(self):
        return render_aura_welcome_hud(
            current_lang="en",
            auto_speak=True,
            bot_logo_uri="https://example.com/aura_robot.png",
            user_name="Boss"
        )

    def test_profile_shortcut_completely_removed_from_dashboard(self, hud_html):
        """Profile shortcut card must NOT exist in the dashboard markup."""
        # No profile shortcut pod/card or text in the holographic modules
        assert 'class="shortcut-card"' not in hud_html
        assert 'window.dispatchCardNav(\'Go to my profile\'' not in hud_html
        assert '<span class="shortcut-title">Profile</span>' not in hud_html
        assert 'node-profile' not in hud_html

    def test_five_primary_holographic_modules_present(self, hud_html):
        """Dashboard must contain exactly the 5 primary holographic travel modules."""
        # 1. Navigation
        assert "node-nav" in hud_html
        assert "Navigation" in hud_html
        assert "CORRIDOR ROUTING" in hud_html
        assert "window.dispatchCardNav('Open navigation'" in hud_html

        # 2. My Trips
        assert "node-trips" in hud_html
        assert "My Trips" in hud_html
        assert "ITINERARY STUDIO" in hud_html
        assert "window.dispatchCardNav('Show my trips'" in hud_html

        # 3. Hotels
        assert "node-hotels" in hud_html
        assert "Hotels" in hud_html
        assert "STAYS & RESORTS" in hud_html
        assert "window.dispatchCardNav('Show hotels'" in hud_html

        # 4. Flights
        assert "node-flights" in hud_html
        assert "Flights" in hud_html
        assert "AIR CORRIDORS" in hud_html
        assert "window.dispatchCardNav('Open flights'" in hud_html

        # 5. Restaurants
        assert "node-food" in hud_html
        assert "Restaurants" in hud_html
        assert "DINING & FOOD" in hud_html
        assert "window.dispatchCardNav('Show restaurants'" in hud_html

    def test_central_robot_centerpiece_structure(self, hud_html):
        """AURA Robot avatar must be the central centerpiece with multi-ring reactor."""
        assert "aura-center-node" in hud_html
        assert "avatar-stage" in hud_html
        assert "arc-reactor-ring-outer" in hud_html
        assert "telemetry-ring-segments" in hud_html
        assert "arc-reactor-ring-mid" in hud_html
        assert "avatar-core-circle" in hud_html
        assert "greeting-headline" in hud_html
        assert "waveform-container" in hud_html
        assert "auraWaveCanvas" in hud_html
        assert "live-transcript-box" in hud_html
        assert "transcriptBox" in hud_html

    def test_holographic_orbital_svg_and_energy_beams(self, hud_html):
        """Holographic stage must include background SVG with neural energy conduits."""
        assert "holo-orbital-stage" in hud_html
        assert "holo-orbital-svg" in hud_html
        assert "orbital-ring" in hud_html
        assert "orbital-ring-mid" in hud_html
        assert "orbital-ring-outer" in hud_html

        # 5 connecting energy beams
        assert 'id="beam-nav"' in hud_html
        assert 'id="beam-trips"' in hud_html
        assert 'id="beam-hotels"' in hud_html
        assert 'id="beam-flights"' in hud_html
        assert 'id="beam-food"' in hud_html
        assert "energy-conduit-pulse" in hud_html

    def test_interactive_glyph_and_hover_mechanisms(self, hud_html):
        """Modules must feature spinning glyph reticles, status blips, and beam highlighting."""
        assert "holo-glyph-disc" in hud_html
        assert "holo-glyph-reticle" in hud_html
        assert "holo-status-blip" in hud_html
        assert "highlightOrbitalBeam" in hud_html
        assert "window.highlightOrbitalBeam('beam-nav', true)" in hud_html

    def test_responsive_layout_media_queries(self, hud_html):
        """CSS must provide responsive adaptations for tablet and mobile."""
        assert "@media (max-width: 820px)" in hud_html
        assert "@media (max-width: 540px)" in hud_html
        assert "holo-modules-container" in hud_html

    def test_profile_functionality_preserved_in_application(self):
        """Profile page remains fully accessible through voice and application commands."""
        ctx = {"current_view": "dashboard"}
        res = AuraGlobalCommandDispatcher.parse_and_dispatch("Open my profile", ctx)
        assert res.command_type in [AuraCommandType.OPEN_PROFILE, AuraCommandType.NAVIGATE_TAB]
        assert res.ui_updates.get("show_user_profile_modal") is True
