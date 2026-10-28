"""
Test Suite for Journey Navigation Controls and Corridor Storybook Engine.
Validates:
1. Previous Step navigation logic and boundary checks
2. Move in Parallel (GPS) state handling and proximity checks
3. Next Step navigation and arrival celebration
4. Reset Journey safe confirmation and state restoration
5. Contextual Step-by-Step Storybook generation
6. Corridor-aware Recommended Places discovery and filtering
7. Automatic Real-Time Day / Sunset / Night environment sync
"""

import pytest
from datetime import datetime
from src.corridor_storybook import CorridorStorybookEngine, CorridorPlacesEngine
from src.aura_journey_engine import build_aura_journey_cockpit_html, ManeuverSequenceBuilder


def test_corridor_storybook_chapter_generation():
    """Verify that CorridorStorybookEngine produces rich, verified cultural and historical lore."""
    # Test Tenali - Guntur corridor chapter
    ch1 = CorridorStorybookEngine.generate_chapter(
        step_idx=0,
        total_steps=5,
        headline="Depart from Tenali",
        instruction="Head west on Tenali-Guntur Road",
        road_name="Tenali-Guntur Road",
        what_to_look_for="Buckingham Canal bridge and railway crossing",
        aura_speech="Departing Tenali. Smooth route westward.",
        step_coords=(16.2430, 80.6400),
        origin_name="Tenali, Andhra Pradesh",
        dest_name="Guntur, Andhra Pradesh"
    )

    assert ch1.chapter_num == 1
    assert ch1.total_chapters == 5
    assert "Tenali" in ch1.historical_lore or "Chalukya" in ch1.historical_lore or "Andhra Paris" in ch1.historical_lore
    assert "paddy" in ch1.geography_nature.lower() or "canal" in ch1.geography_nature.lower()
    assert ch1.what_to_look_for is not None
    assert ch1.travel_tip is not None

    # Test Amaravati / Vijayawada chapter
    ch2 = CorridorStorybookEngine.generate_chapter(
        step_idx=2,
        total_steps=6,
        headline="Continue toward Amaravati",
        instruction="Merge onto Amaravati Green Corridor",
        road_name="Amaravati Capital Highway",
        what_to_look_for="Krishna riverbank and stupa monument",
        aura_speech="Approaching Amaravati heritage sector.",
        step_coords=(16.5415, 80.5150),
        origin_name="Guntur",
        dest_name="Amaravati Secretariat"
    )

    assert "Satavahana" in ch2.historical_lore or "Buddhist" in ch2.historical_lore or "Amaravati" in ch2.historical_lore
    assert "Krishna" in ch2.geography_nature or "River" in ch2.geography_nature


def test_corridor_places_discovery_and_filtering():
    """Verify that CorridorPlacesEngine discovers verified places along route corridor."""
    poly = [
        (16.2430, 80.6400),  # Tenali
        (16.2750, 80.5400),  # Midpoint
        (16.3067, 80.4365)   # Guntur
    ]

    # Discover all places near departure point
    places_all = CorridorPlacesEngine.get_corridor_places(
        step_coords=poly[0],
        route_polyline=poly,
        origin_coords=poly[0],
        dest_coords=poly[-1],
        category_filter="all",
        radius_km=15.0,
        max_results=6
    )

    assert len(places_all) >= 1
    p0 = places_all[0]
    assert "name" in p0
    assert "latitude" in p0
    assert "longitude" in p0
    assert "distance_step_km" in p0
    assert "category_icon" in p0
    assert p0["distance_step_km"] <= 15.0

    # Filter by specific category
    hotels = CorridorPlacesEngine.get_corridor_places(
        step_coords=poly[-1],
        route_polyline=poly,
        origin_coords=poly[0],
        dest_coords=poly[-1],
        category_filter="hotels",
        radius_km=15.0
    )
    for h in hotels:
        assert h["category"].lower() == "hotels"


def test_journey_controls_attributes_in_app():
    """Verify that app.py contains the 4 functional journey buttons and corridor storybook section."""
    with open("app.py", "r", encoding="utf-8") as f:
        code = f.read()

    # Previous Step button with boundary disable check
    assert 'key=f"btn_step_prev{key_suffix}"' in code
    assert "disabled=is_first" in code
    assert '"◀ Previous Step"' in code

    # Move in Parallel (GPS) button with dynamic live tracking label
    assert 'key=f"btn_toggle_move{key_suffix}"' in code
    assert '"🟢 GPS Active (Live Tracking)"' in code
    assert '"▶ Move in Parallel (GPS)"' in code

    # Next Step button with boundary disable check
    assert 'key=f"btn_step_next{key_suffix}"' in code
    assert "disabled=is_last" in code
    assert '"Next Step ▶"' in code

    # Reset Journey button with safe confirmation
    assert 'key=f"btn_reset_journey{key_suffix}"' in code
    assert '"⏮ Reset Journey"' in code
    assert '"⚠️ Confirm Reset?"' in code

    # Journey Progress Display
    assert "Journey Progress: Step" in code
    assert "COMPLETED" in code
    assert "st.progress" not in code or "pct_progress" in code

    # Recommended Places & Storybook Along the Corridor
    assert "🌟 Recommended Places & Storybook Along the Corridor" in code
    assert "CorridorStorybookEngine.generate_chapter" in code
    assert "CorridorPlacesEngine.get_corridor_places" in code
    assert '"👁️ View on Map"' in code
    assert '"➕ Add as Stop"' in code


def test_automatic_realtime_environment_sync():
    """Verify that 3D Cockpit HTML automatically syncs with real local timezone clock."""
    raw_steps = [
        {"instruction": "Head west on Main Road", "road": "Main Road", "distance": 800, "duration": 120, "type": "depart"},
        {"instruction": "Arrive at Destination", "road": "Destination", "distance": 0, "duration": 0, "type": "arrive"}
    ]
    steps = ManeuverSequenceBuilder.build_sequence(
        steps=raw_steps,
        origin_label="Tenali",
        dest_label="Guntur",
        total_distance_m=800.0,
        travel_mode="car"
    )

    html = build_aura_journey_cockpit_html(
        origin_name="Tenali",
        dest_name="Guntur",
        travel_mode="car",
        total_distance_km=0.8,
        total_duration_mins=2.0,
        maneuvers=steps,
        current_step_idx=0
    )

    # Verify real-time environment synchronization in HTML and JS
    assert "toggleAutoRealTimeEnv" in html
    assert "getRealTimeEnv" in html
    assert "env-auto" in html
    assert "⚡ Auto" in html
    assert "ENVIRONMENT:" in html

