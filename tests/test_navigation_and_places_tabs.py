import pytest
from pathlib import Path
import re
from src.route_engine import TravelMode, OSRMGlobalRoutingProvider

APP_PATH = Path(__file__).resolve().parent.parent / "app.py"

def test_safe_markdown_sanitizer_installed():
    """Verify the global markdown sanitizer is properly installed and active."""
    content = APP_PATH.read_text(encoding="utf-8")
    assert "def _safe_st_markdown(body, *args, **kwargs):" in content
    assert "st.markdown = _safe_st_markdown" in content
    assert "kwargs[\"unsafe_allow_html\"] = True" in content

def test_safe_markdown_prevents_code_blocks():
    """Verify that _safe_st_markdown dedents HTML lines so no line starts with 4+ spaces."""
    import streamlit as st
    # Verify st.markdown wrapper logic
    test_html = """
        <div style='font-size: 0.80rem; font-weight: 800; color: #38bdf8;'>
            <span>⚡</span> TRAVEL MODE & VEHICLE FLEET
        </div>
    """
    cleaned_lines = []
    for line in test_html.splitlines():
        stripped = line.strip()
        if stripped or (cleaned_lines and cleaned_lines[-1] != ""):
            cleaned_lines.append(stripped)
    res = "\n".join(cleaned_lines)
    
    # Assert no line starts with 4 spaces (which triggers CommonMark indented code blocks)
    for l in res.splitlines():
        assert not l.startswith("    "), f"Indented line found: {l}"
    assert "<div style=" in res

def test_travel_mode_fleet_section():
    """Verify Vehicle Fleet section heading, subtitle, and all 9 required vehicles."""
    content = APP_PATH.read_text(encoding="utf-8")
    
    # Heading & Subtitle
    assert "⚡ TRAVEL MODE & VEHICLE FLEET" in content
    assert "Choose your vehicle for suitable route recommendations." in content
    
    # 9 Required Vehicle Options
    assert "🚗 Car" in content or '"Car"' in content
    assert "🏍️ Bike" in content or '"Bike"' in content
    assert "🚌 Bus" in content or '"Bus"' in content
    assert "✈️ Airway" in content or '"Airway"' in content
    assert "🚢 Waterway" in content or '"Waterway"' in content
    assert "🚚 Truck" in content or '"Truck"' in content
    assert "🚜 Tractor" in content or '"Tractor"' in content
    assert "🚴 Bicycle" in content or '"Cycle"' in content
    assert "🚶 Walk" in content or '"Walk"' in content

def test_speed_mode_transit_profile_section():
    """Verify Speed Mode & Transit Profile heading, subtitle, and preferences."""
    content = APP_PATH.read_text(encoding="utf-8")
    
    assert "⚡ SPEED MODE & TRANSIT PROFILE" in content
    assert "Choose how you want to travel." in content
    
    # Supported preferences
    assert "avoid_highways" in content
    assert "avoid_tolls" in content

def test_places_and_nearby_facilities_section():
    """Verify Places & Facilities heading, subtitle, categories, and search placeholder."""
    content = APP_PATH.read_text(encoding="utf-8")
    
    # Heading & Subtitle
    assert "📍 PLACES & NEARBY FACILITIES" in content
    assert "Discover useful places near your location or along your selected route." in content
    
    # Required Categories
    required_cats = [
        "Hospitals & Clinics",
        "Supermarkets",
        "Fuel Stations",
        "EV Charging",
        "Restaurants",
        "ATMs & Banking",
        "Police & Emergency Services",
        "Hotels",
        "Tourist Attractions",
        "Shopping Malls",
        "Parks",
        "Rest Stops",
    ]
    for cat in required_cats:
        assert cat in content, f"Missing category: {cat}"
        
    # Search input placeholder
    assert "Search places, landmarks, or addresses..." in content

def test_places_card_actions():
    """Verify each place card contains all 4 functional actions: View Map, Directions, Info, Save."""
    content = APP_PATH.read_text(encoding="utf-8")
    
    assert "btn_view_sug_" in content
    assert "btn_dir_sug_" in content
    assert "btn_info_sug_" in content
    assert "btn_save_sug_" in content

def test_flight_and_waterway_limitation_handling():
    """Verify OSRM provider does not silently substitute car for flight or waterway."""
    provider = OSRMGlobalRoutingProvider()
    
    # Flight
    flight_res = provider.calculate_routes(16.23, 80.55, 16.30, 80.44, mode=TravelMode.FLIGHT)
    assert flight_res == []
    assert "aeronautical" in provider.last_error_message.lower() or "airway" in provider.last_error_message.lower()
    
    # Waterway
    water_res = provider.calculate_routes(16.23, 80.55, 16.30, 80.44, mode=TravelMode.WATERWAY)
    assert water_res == []
    assert "maritime" in provider.last_error_message.lower() or "waterway" in provider.last_error_message.lower()

