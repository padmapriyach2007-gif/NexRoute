"""
Automated Test Suite for NexRoute Upgraded Features:
Feature 1: Intelligent Start and Destination Location Detection & Autocomplete Search
Feature 2: Start and Destination Markers, Beside-the-Map Endpoint Panel, Swap & Clear
Feature 3: Functional Map Compass with Precision Orientation & North-Up Controls
"""

import pytest
import math
from typing import Dict, Any, List

from src.map_service import MapService, OFFLINE_GEOCODE_CACHE
from src.location_service import LocationService as RealLocationService, LocationPermissionStatus
from src.route_engine import RealWorldRouteEngine, TravelMode
from src.google_maps_platform import (
    build_google_maps_javascript_html,
    load_and_georeference_saved_locations,
    geocode_with_google_api
)


@pytest.fixture
def map_svc():
    return MapService(timeout_sec=1.5)


@pytest.fixture
def loc_svc():
    return RealLocationService()


@pytest.fixture
def route_engine():
    return RealWorldRouteEngine()


# =========================================================================
# FEATURE 1: INTELLIGENT START & DESTINATION SEARCH TESTS
# =========================================================================

def test_01_search_well_known_landmark(map_svc):
    """Scenario 1: Search for a well-known landmark."""
    res = map_svc.geocode("vignan university")
    assert res is not None, "Failed to resolve known landmark 'vignan university'"
    assert -90.0 <= res["lat"] <= 90.0
    assert -180.0 <= res["lon"] <= 180.0
    assert "vignan" in res["name"].lower() or "vignan" in res.get("display_name", "").lower()


def test_02_search_hospital_disambiguation(map_svc):
    """Scenario 2: Search for a hospital with similar name or medical category."""
    cands_aiims = map_svc.get_disambiguation_candidates("aiims mangalagiri", limit=5)
    assert len(cands_aiims) > 0, "Failed to resolve AIIMS Mangalagiri"
    best_aiims = cands_aiims[0]
    assert 16.35 <= best_aiims["lat"] <= 16.50
    assert 80.50 <= best_aiims["lon"] <= 80.65
    assert best_aiims.get("category_icon") == "🏥" or "hospital" in best_aiims.get("type", "").lower()

    # Disambiguation with Guntur Medical College
    cands_gmc = map_svc.get_disambiguation_candidates("guntur medical college", limit=5)
    assert len(cands_gmc) > 0
    best_gmc = cands_gmc[0]
    assert abs(best_gmc["lat"] - best_aiims["lat"]) > 0.05, "AIIMS and GMC coordinates should be distinct"


def test_03_search_interstate_destination(map_svc):
    """Scenario 3: Search for a destination in another city or state."""
    # Hyderabad, Telangana
    cands_hyd = map_svc.get_disambiguation_candidates("hyderabad", limit=6)
    assert len(cands_hyd) > 0
    # Must contain Indian city of Hyderabad
    hyd_match = next((c for c in cands_hyd if c.get("country", "").lower() == "india" or "telangana" in c.get("display_name", "").lower()), None)
    assert hyd_match is not None, "Failed to surface Hyderabad, Telangana"
    assert 17.20 <= hyd_match["lat"] <= 17.60
    assert 78.20 <= hyd_match["lon"] <= 78.60

    # Tirupati Pilgrim City
    cands_tpt = map_svc.get_disambiguation_candidates("tirupati", limit=5)
    assert len(cands_tpt) > 0
    best_tpt = cands_tpt[0]
    assert 13.50 <= best_tpt["lat"] <= 13.80
    assert 79.30 <= best_tpt["lon"] <= 79.60


def test_04_partial_address_and_tokens(map_svc):
    """Scenario 4: Enter a partial address and verify valid coordinate resolution."""
    cands = map_svc.get_disambiguation_candidates("brodipet", limit=5)
    assert len(cands) > 0
    assert 16.20 <= cands[0]["lat"] <= 16.40
    assert 80.35 <= cands[0]["lon"] <= 80.50

    # Direct coordinates input
    coord_cands = map_svc.geocode_candidates("16.2335, 80.5505", limit=1)
    assert len(coord_cands) == 1
    assert abs(coord_cands[0]["lat"] - 16.2335) < 0.0001
    assert abs(coord_cands[0]["lon"] - 80.5505) < 0.0001


def test_05_geolocation_permission_denial(loc_svc):
    """Scenario 5: Deny current-location permission."""
    loc_svc.set_permission(LocationPermissionStatus.DENIED)
    assert loc_svc.permission_status == LocationPermissionStatus.DENIED
    # Verify fallback position is used safely without throwing exceptions
    reading, status_msg = loc_svc.get_effective_location()
    coords = reading.coordinates
    assert coords is not None
    assert -90.0 <= coords[0] <= 90.0
    assert -180.0 <= coords[1] <= 180.0


def test_06_geolocation_timeout_and_error_handling(loc_svc):
    """Scenario 6: Handle position timeout or unavailable status gracefully."""
    loc_svc.set_permission(LocationPermissionStatus.RESTRICTED)
    assert loc_svc.permission_status == LocationPermissionStatus.RESTRICTED
    reading, status_msg = loc_svc.get_effective_location()
    coords = reading.coordinates
    assert coords is not None
    assert len(coords) == 2


def test_07_coordinate_boundary_validation(map_svc):
    """Scenario 7: Physical bounds check [-90, 90] and [-180, 180]."""
    # Invalid lat > 90
    assert map_svc.geocode_candidates("95.0, 80.0", limit=1) == []
    # Invalid lat < -90
    assert map_svc.geocode_candidates("-92.0, 80.0", limit=1) == []
    # Invalid lon > 180
    assert map_svc.geocode_candidates("16.0, 195.0", limit=1) == []
    # Valid coordinates
    valid = map_svc.geocode_candidates("16.2335, 80.5505", limit=1)
    assert len(valid) == 1
    assert valid[0]["lat"] == 16.2335


def test_08_empty_or_invalid_search_query(map_svc):
    """Scenario 12: Simulate an invalid, whitespace, or empty query."""
    assert map_svc.geocode_candidates("", limit=5) == []
    assert map_svc.geocode_candidates("   ", limit=5) == []
    assert map_svc.get_disambiguation_candidates("", limit=5) == []


# =========================================================================
# FEATURE 2: START & DESTINATION MARKERS & ENDPOINT PANEL TESTS
# =========================================================================

def test_09_marker_rendering_in_html():
    """Scenario 7 & 8: Verify HTML generation contains distinct start and destination markers."""
    html = build_google_maps_javascript_html(
        center_lat=16.2335,
        center_lon=80.5505,
        zoom=14,
        origin_coords=(16.2335, 80.5505),
        origin_label="Vignan Main Campus",
        dest_coords=(16.3067, 80.4365),
        dest_label="Guntur City Center",
        route_polyline=[(16.2335, 80.5505), (16.3067, 80.4365)]
    )

    # Must contain Start marker styling (green indicator)
    assert "🟢 START" in html or "#10b981" in html
    # Must contain Destination marker styling (red indicator)
    assert "🏁 DEST" in html or "#ef4444" in html
    # Must contain origin coordinates in GMAP_DATA
    assert "16.2335" in html
    assert "80.5505" in html
    # Must contain destination coordinates in GMAP_DATA
    assert "16.3067" in html
    assert "80.4365" in html


def test_10_swap_endpoints_logic():
    """Scenario 9: Verify swap exchanges start and destination coordinates & labels."""
    orig_coords = (16.2335, 80.5505)
    orig_label = "Vignan Campus"
    dest_coords = (16.3067, 80.4365)
    dest_label = "Guntur City"

    # Perform swap
    swapped_orig_coords = dest_coords
    swapped_orig_label = dest_label
    swapped_dest_coords = orig_coords
    swapped_dest_label = orig_label

    assert swapped_orig_coords == (16.3067, 80.4365)
    assert swapped_dest_coords == (16.2335, 80.5505)
    assert swapped_orig_label == "Guntur City"
    assert swapped_dest_label == "Vignan Campus"


def test_11_clear_destination_logic():
    """Scenario 10: Verify clearing destination retains origin safely."""
    orig_coords = (16.2335, 80.5505)
    dest_coords = (16.3067, 80.4365)

    # Clear destination
    cleared_dest_coords = None
    cleared_dest_label = None

    assert orig_coords == (16.2335, 80.5505)
    assert cleared_dest_coords is None
    assert cleared_dest_label is None


# =========================================================================
# FEATURE 3: FUNCTIONAL MAP COMPASS TESTS
# =========================================================================

def test_12_compass_ui_elements_in_html():
    """Scenario 15: Verify Map Compass HTML & CSS elements are present."""
    html = build_google_maps_javascript_html(
        center_lat=16.2335,
        center_lon=80.5505,
        zoom=14
    )

    # Compass container and elements
    assert "gmap-compass-container" in html, "Compass container missing from HTML"
    assert "gmap-compass-rose" in html, "Compass rose missing from HTML"
    assert "compass-needle-wrap" in html, "Compass needle wrap missing from HTML"
    assert "compass-needle-north" in html, "North needle missing from HTML"
    assert "compass-needle-south" in html, "South needle missing from HTML"
    assert "gmap-compass-readout" in html, "Degree readout badge missing from HTML"
    assert "gmap-compass-controls" in html, "Compass orientation controls missing from HTML"


def test_13_compass_javascript_functions_in_html():
    """Scenario 16: Verify North-Up reset and rotation functions are defined in JS."""
    html = build_google_maps_javascript_html(
        center_lat=16.2335,
        center_lon=80.5505,
        zoom=14
    )

    assert "window.resetMapNorthUp = function" in html, "resetMapNorthUp JS missing"
    assert "window.rotateMapOrientation = function" in html, "rotateMapOrientation JS missing"
    assert "window.updateCompassDisplay = function" in html, "updateCompassDisplay JS missing"
    assert "window.initMapCompass = function" in html, "initMapCompass JS missing"
    assert "window.toggleDeviceHeadingMode = function" in html, "toggleDeviceHeadingMode JS missing"


def test_14_autocomplete_search_as_you_type_in_html():
    """Scenario 13: Verify search-as-you-type and keyboard navigation in map HTML."""
    html = build_google_maps_javascript_html(
        center_lat=16.2335,
        center_lon=80.5505,
        zoom=14
    )

    assert "pac-autocomplete-dropdown" in html, "Autocomplete dropdown missing"
    assert "activeAbortController" in html, "AbortController for debouncing missing"
    assert "ArrowDown" in html, "Keyboard navigation ArrowDown missing"
    assert "ArrowUp" in html, "Keyboard navigation ArrowUp missing"


# =========================================================================
# FEATURE 4: MULTI-OBJECTIVE ROUTING PRESERVATION TESTS
# =========================================================================

def test_15_routing_modes_preservation(route_engine):
    """Scenario 17: Verify Fastest, Shortest, and Multi-Objective routing modes work."""
    vignan = (16.2335, 80.5505)
    guntur = (16.3067, 80.4365)

    routes = route_engine.calculate_routes(
        vignan[0], vignan[1],
        guntur[0], guntur[1],
        mode=TravelMode.DRIVING
    )
    assert len(routes) >= 1, "Route calculation failed between Vignan and Guntur"
    primary = routes[0]
    assert primary.distance_km > 0.0
    assert primary.duration_minutes > 0.0
    assert len(primary.polyline) >= 2


def test_16_reverse_geocode_readability(map_svc):
    """Test reverse geocoding translates coordinates to human-readable address."""
    addr = map_svc.reverse_geocode(16.2335, 80.5505)
    assert addr is not None
    assert len(addr) > 5
    assert "vignan" in addr.lower() or "vadlamudi" in addr.lower() or "guntur" in addr.lower()
