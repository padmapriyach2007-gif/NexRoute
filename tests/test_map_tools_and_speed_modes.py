"""
Test suite for PATHFINDER Map Toolbar, Nearby-Place Categories,
Vehicle Fleet Cards, and Speed Modes.
"""
import re
from pathlib import Path
import pytest
from src.google_maps_platform import build_google_maps_javascript_html
from src.route_engine import RealWorldRouteEngine, RouteOption, OSRMGlobalRoutingProvider, TravelMode


def get_app_configs():
    app_code = Path("app.py").read_text(encoding="utf-8")
    m1 = re.search(r'(MODES_CONFIG\s*=\s*\{.*?\}\n\s*\})', app_code, re.DOTALL)
    m2 = re.search(r'(SPEED_LIMITS_CONFIG\s*=\s*\{.*?\}\n\s*\})', app_code, re.DOTALL)
    ns = {"TravelMode": TravelMode}
    if m1:
        exec(m1.group(1), ns)
    if m2:
        exec(m2.group(1), ns)
    return ns


def test_map_toolbar_buttons_present():
    """Verify all toolbar controls and hooks are rendered in the HTML."""
    html = build_google_maps_javascript_html(
        center_lat=17.385,
        center_lon=78.486,
        origin_coords=(17.385, 78.486),
        dest_coords=(17.440, 78.348),
        route_polyline=[],
        amenities=[],
        map_type="roadmap"
    )

    # 1. Place Search input and autocomplete dropdown
    assert 'id="pac-input"' in html
    assert 'id="pac-autocomplete-dropdown"' in html
    assert 'window.initUnifiedPlaceSearch' in html

    # 2. My Location
    assert 'id="btn-geolocation"' in html
    assert 'window.locateUserGps()' in html

    # 3. Fit Bounds
    assert 'id="btn-fit-all"' in html
    assert 'window.fitAllMapBounds()' in html

    # 4. Full Screen
    assert 'id="btn-fullscreen"' in html
    assert 'window.toggleFullScreen()' in html

    # 5. Map Details
    assert 'id="btn-open-layers"' in html
    assert 'window.toggleLayersDrawer()' in html


def test_all_eight_nearby_categories_present():
    """Verify all 8 place categories have buttons and search handlers."""
    html = build_google_maps_javascript_html(
        center_lat=17.385,
        center_lon=78.486,
        origin_coords=(17.385, 78.486),
        dest_coords=(17.440, 78.348),
        route_polyline=[],
        amenities=[],
        map_type="roadmap"
    )

    categories = [
        ("HOSPITALS", "Hospitals"),
        ("FUEL", "Fuel/Charging"),
        ("RESTAURANTS", "Restaurants"),
        ("ATMS", "ATM / Banking"),
        ("POLICE", "Police/Rescue"),
        ("HOTELS", "Hotels"),
        ("SHELTERS", "Shelters"),
        ("MALLS", "Shopping Malls"),
    ]

    for cat_key, cat_label in categories:
        assert f'data-filter="{cat_key}"' in html, f"Missing category filter for {cat_key}"
        assert f"window.triggerCategorySearch('{cat_key}')" in html, f"Missing click trigger for {cat_key}"
        assert cat_label in html, f"Missing label {cat_label}"

    # Category results panel markup
    assert 'id="gmap-category-panel"' in html
    assert 'id="cat-panel-title"' in html
    assert 'id="cat-panel-count"' in html
    assert 'id="cat-panel-body"' in html
    assert 'id="cat-panel-subfilters"' in html
    assert 'window.clearActiveCategory()' in html
    assert 'window.setFuelSubfilter' in html


def test_vehicle_cards_speed_labels_removed():
    """Verify vehicle fleet cards no longer contain hardcoded speed strings."""
    configs = get_app_configs()
    modes_config = configs["MODES_CONFIG"]
    expected_vehicles = ["CAR", "BIKE", "BUS", "TRUCK", "TRACTOR", "BICYCLE", "WALK"]
    for v in expected_vehicles:
        assert v in modes_config, f"Vehicle {v} must be present in MODES_CONFIG"
        # Speed key must NOT be present under vehicle config
        assert "speed" not in modes_config[v], f"Fixed speed must be removed from vehicle config for {v}"
        assert "icon" in modes_config[v]
        assert "name" in modes_config[v]


def test_speed_limits_config_validity():
    """Verify dynamic speed limits config covers all vehicle types with sensible bounds."""
    configs = get_app_configs()
    speed_limits_config = configs["SPEED_LIMITS_CONFIG"]
    expected_vehicles = ["CAR", "BIKE", "BUS", "TRUCK", "TRACTOR", "BICYCLE", "WALK"]
    for v in expected_vehicles:
        assert v in speed_limits_config, f"{v} missing in SPEED_LIMITS_CONFIG"
        cfg = speed_limits_config[v]
        assert cfg["min"] < cfg["max"]
        assert cfg["min"] <= cfg["default"] <= cfg["max"]

    # Non-motorized vehicles should have realistic human pacing limits
    assert speed_limits_config["WALK"]["max"] <= 15
    assert speed_limits_config["BICYCLE"]["max"] <= 40
    # Heavy vehicles must be appropriately restricted
    assert speed_limits_config["TRACTOR"]["max"] <= 45
    assert speed_limits_config["TRUCK"]["max"] <= 100


def test_route_engine_speed_modes_integration():
    """Verify speed modes and custom speeds are received and processed by RealWorldRouteEngine."""
    engine = RealWorldRouteEngine()
    coords = (17.3850, 78.4867, 17.4401, 78.3489)

    # 1. Normal Mode
    routes_normal = engine.calculate_routes(*coords, mode=TravelMode.DRIVING, speed_mode="normal")
    assert len(routes_normal) > 0
    assert routes_normal[0].speed_mode == "normal"
    assert "Standard transit profile" in routes_normal[0].speed_mode_note

    # 2. Eco Mode
    routes_eco = engine.calculate_routes(*coords, mode=TravelMode.DRIVING, speed_mode="eco")
    assert len(routes_eco) > 0
    assert routes_eco[0].speed_mode == "eco"
    assert "Eco mode selected" in routes_eco[0].speed_mode_note or "Eco-optimized profile" in routes_eco[0].speed_mode_note

    # 3. Fast Mode
    routes_fast = engine.calculate_routes(*coords, mode=TravelMode.DRIVING, speed_mode="fast")
    assert len(routes_fast) > 0
    assert routes_fast[0].speed_mode == "fast"
    assert "Fast mode selected" in routes_fast[0].speed_mode_note or "Fast profile" in routes_fast[0].speed_mode_note

    # 4. Custom Speed Mode
    routes_custom = engine.calculate_routes(*coords, mode=TravelMode.DRIVING, speed_mode="custom", custom_speed_kmh=65.0)
    assert len(routes_custom) > 0
    assert routes_custom[0].speed_mode == "custom"
    assert routes_custom[0].custom_speed_kmh == 65.0
    assert "65 km/h" in routes_custom[0].speed_mode_note

    # Route Option to_dict() must include all speed metadata
    route_dict = routes_custom[0].to_dict()
    assert route_dict["speed_mode"] == "custom"
    assert route_dict["custom_speed_kmh"] == 65.0
    assert "speed_mode_note" in route_dict


def test_no_fake_speeds_or_fabricated_durations():
    """Verify provider calculated duration is honestly preserved when OSRM routing is returned."""
    provider = OSRMGlobalRoutingProvider()
    routes = provider.calculate_routes(17.3850, 78.4867, 17.4401, 78.3489, mode=TravelMode.DRIVING, speed_mode="eco")
    if routes:
        # Provider duration must match duration_seconds and not be fabricated
        assert routes[0].provider_duration_seconds == routes[0].duration_seconds
        assert routes[0].speed_mode == "eco"
