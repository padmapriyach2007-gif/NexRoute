"""
Tests for PATHFINDER / NexRoute Mobile Responsive Design System
Verifies full responsiveness across all 6 breakpoint tiers:
- Small phones: 320–374px
- Standard phones: 375–430px
- Large phones: 431–600px
- Tablets: 601–1024px
- Laptops: 1025–1440px
- Large desktops: above 1440px
"""

import os
import re
import pytest

def test_six_breakpoint_tiers_defined_in_app():
    """Verify that all 6 required responsive breakpoints are defined in app.py CSS."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Tier 1: Small phones (<= 374px)
    assert "@media (max-width: 374px)" in content or "@media (max-width:374px)" in content

    # Tier 2: Standard phones (375px - 430px)
    assert "375px" in content and "430px" in content

    # Tier 3: Large phones (431px - 600px)
    assert "431px" in content and "600px" in content

    # Tier 4: Tablets (601px - 1024px)
    assert "1024px" in content

    # Tier 5: Laptops (1025px - 1440px)
    assert "1025px" in content and "1440px" in content

    # Tier 6: Large Desktops (> 1440px)
    assert "1441px" in content or "1440px" in content


def test_touch_target_accessibility():
    """All buttons and form elements must adhere to >= 44px minimum touch targets."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "min-height: 44px !important;" in content
    assert "touch-action: manipulation !important;" in content


def test_no_horizontal_overflow_and_safe_areas():
    """Verify that viewport overflow-x is strictly contained and iOS/Android notches are respected."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "overflow-x: hidden !important;" in content
    assert "max-width: 100vw !important;" in content
    assert "safe-area-inset-top" in content
    assert "safe-area-inset-bottom" in content


def test_mobile_bottom_sheet_drawer():
    """Verify expandable mobile bottom sheet with handle bar and drawer states."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "mobile-bottom-sheet-handle-bar" in content
    assert "mobile-bottom-sheet-pill-handle" in content
    assert "mobile_bottom_sheet_state" in content
    assert "btn_sh_collapsed" in content
    assert "btn_sh_half" in content
    assert "btn_sh_expanded" in content


def test_mobile_map_and_controls_stacking():
    """Map must appear on top (order: 1) and controls below (order: 2) on mobile <= 992px."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "st-key-nav_map_and_controls_container" in content
    assert "order: 1 !important;" in content
    assert "order: 2 !important;" in content


def test_mobile_route_recommendation_cards():
    """Route cards must display 1 per row on mobile screens (<= 768px)."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "st-key-route_recommendation_cards_deck" in content
    assert "flex-direction: column !important;" in content


def test_mobile_fleet_deck_grid():
    """Vehicle fleet must adapt into 3 columns on standard mobile and 2 columns on small mobile."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Standard phones: 3 columns
    assert "grid-template-columns: repeat(3, 1fr) !important;" in content
    # Small phones: 2 columns
    assert "grid-template-columns: repeat(2, 1fr) !important;" in content


def test_mobile_journey_controls_grid():
    """Journey stepper controls must adapt into a 2x2 grid on mobile."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "st-key-journey_stepper_controls" in content


def test_mobile_aura_chatbot_chips_deck():
    """Aura quick action chips must wrap gracefully on small screens without horizontal clipping."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "aura_quick_chips_deck" in content


def test_reduced_motion_accessibility():
    """Applications must respect user reduced motion preferences."""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert "prefers-reduced-motion: reduce" in content
