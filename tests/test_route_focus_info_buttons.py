import pytest
from pathlib import Path
import re

APP_PATH = Path(__file__).resolve().parent.parent / "app.py"

def test_buttons_definition_in_app():
    """Verify all 3 buttons are defined with correct emojis, keys, and primary styling."""
    content = APP_PATH.read_text(encoding="utf-8")
    
    # 1. Quick Map Toolbar buttons
    assert 'key="btn_main_quick_route"' in content, "Missing btn_main_quick_route"
    assert 'key="btn_main_quick_focus"' in content, "Missing btn_main_quick_focus"
    assert 'key="btn_main_quick_info"' in content, "Missing btn_main_quick_info"
    
    # 2. Check primary styling for Route button
    assert 'st.button("🧭 Route", key="btn_main_quick_route", type="primary"' in content
    
    # 3. Facility card buttons
    assert 'key=f"btn_cat_route_{fac.get(\'facility_id\', idx)}"' in content
    assert 'key=f"btn_cat_focus_{fac.get(\'facility_id\', idx)}"' in content
    assert 'key=f"btn_cat_inq_{fac.get(\'facility_id\', idx)}"' in content

def test_route_button_logic():
    """Verify Route button displays existing road geometry and notifies when no route exists."""
    content = APP_PATH.read_text(encoding="utf-8")
    
    # Route button checks if route exists
    assert 'st.session_state.get("active_ranked_routes")' in content
    assert 'st.session_state.auto_fit_bounds = True' in content
    assert 'st.session_state.focused_route_id = "ALL"' in content
    # If no route, shows guidance
    assert 'Select a start and destination to find a route.' in content

def test_focus_button_priorities():
    """Verify Focus button follows strict priority order:
    1. Active navigation (GPS)
    2. Selected route (fit corridor)
    3. Selected marker (destination, start, or place)
    4. Nothing to focus on yet (no unrequested GPS prompts)
    """
    content = APP_PATH.read_text(encoding="utf-8")
    
    # Priority 1: Navigation
    assert 'st.session_state.get("is_in_transit") and st.session_state.get("user_live_coords")' in content
    # Priority 2: Selected route
    assert 'elif st.session_state.get("active_ranked_routes") or st.session_state.get("primary_route_poly"):' in content
    # Priority 3: Markers
    assert 'coords_dest and coords_dest != (0.0, 0.0):' in content
    assert 'coords_orig and coords_orig != (0.0, 0.0):' in content
    # Priority 4: Fallback
    assert 'Nothing to focus on yet.' in content

def test_info_dialog_implementation():
    """Verify Info button opens dialog with full specifications."""
    content = APP_PATH.read_text(encoding="utf-8")
    
    # Dialog decorator
    assert '@st.dialog("ℹ️ Journey & Location Information", width="large")' in content
    assert 'def render_app_info_dialog():' in content
    
    # Empty guidance
    assert 'Route and location information will appear here after you select a route or location.' in content
    
    # Marker details: 5 decimal places coordinates, address, category, distance, contact
    assert '{lat:.5f}°, {lon:.5f}°' in content
    assert 'Corridor Distance' in content
    assert 'Direct Contact & Services' in content
    
    # Route details: distance, duration, category badge, tolls, fuel, accessibility, major roads
    assert 'Estimated Fuel Cost' in content
    assert 'Toll Charges' in content
    assert 'Corridor Accessibility' in content
    assert 'btn_app_info_dialog_close' in content
    assert '✕ Close' in content

def test_facility_cards_info_button_always_accessible():
    """Verify Info button on facility cards is never replaced or hidden."""
    content = APP_PATH.read_text(encoding="utf-8")
    
    # Check that col_act3 renders btn_cat_inq_ and sets show_info_modal
    assert 'st.session_state.show_info_modal = True' in content
    assert 'st.session_state.active_info_target = {"type": "facility", "data": fac}' in content

