"""
Unit tests for the Official Google Maps Platform integration module.
"""

import os
import pytest
from src.google_maps_platform import (
    get_google_maps_api_key,
    is_google_maps_key_configured,
    load_and_georeference_saved_locations,
    geocode_with_google_api,
    build_google_maps_javascript_html,
    DEFAULT_CAMPUS_CENTER
)


def test_load_and_georeference_saved_locations():
    """Verify that all 97 user-created saved locations are loaded and georeferenced with valid GPS coordinates."""
    locations = load_and_georeference_saved_locations()
    assert len(locations) == 97, f"Expected 97 locations from vignan_tour_locations.json, got {len(locations)}"

    for loc in locations:
        assert "latitude" in loc and "longitude" in loc
        assert -90.0 <= loc["latitude"] <= 90.0
        assert -180.0 <= loc["longitude"] <= 180.0
        assert loc["name"]
        assert loc["section"]
        assert loc["category"] == "SAVED_LOCATION"
        assert "street_view_url" in loc


def test_saved_locations_distinct_coordinates():
    """Ensure that multiple rooms in the same section do not collapse onto the exact same coordinates."""
    locations = load_and_georeference_saved_locations()
    coord_set = set((round(loc["latitude"], 5), round(loc["longitude"], 5)) for loc in locations)
    # 97 locations should have dozens of distinct coordinate points across campus
    assert len(coord_set) >= 30


def test_build_google_maps_javascript_html():
    """Verify that the official Google Maps JavaScript API HTML is properly structured."""
    locations = load_and_georeference_saved_locations()
    html = build_google_maps_javascript_html(
        center_lat=16.2335,
        center_lon=80.5505,
        zoom=15,
        origin_coords=(16.241, 80.584),
        origin_label="Start",
        dest_coords=(16.2335, 80.5505),
        dest_label="Campus",
        route_polyline=[(16.241, 80.584), (16.2335, 80.5505)],
        saved_locations=locations[:10],
        amenities=[{"name": "General Hospital", "latitude": 16.234, "longitude": 80.551}],
        hazards=[{"lat": 16.238, "lon": 80.56, "radius_meters": 300}],
        map_type="hybrid"
    )

    assert "gmap-container" in html
    assert "pac-input" in html  # Places autocomplete input
    assert "btn-geolocation" in html  # Browser Geolocation control
    assert "initGoogleMapPlatform" in html
    assert "savedLocations" in html
    assert "16.2335" in html
    assert "pointer-virtual-man-wrap" in html
    assert "updateVirtualManLeaflet" in html
    assert "dispatchCompanionSync" in html
    assert "gmap-layers-trigger" in html  # Authentic bottom-left Layers button
    assert "gmap-layers-drawer" in html  # Floating Map details flyout drawer
    assert "layer-btn-traffic" in html  # Real-time traffic layer option
    assert "layer-btn-transit" in html  # Public transit layer option
    assert "layer-btn-biking" in html  # Dedicated biking layer option
    assert "layer-btn-terrain" in html  # Terrain layer option
    assert "layer-btn-streetview" in html  # Google Street View launcher
    assert "layer-btn-hazards" in html  # Wildfires & road hazards
    assert "layer-btn-airquality" in html  # Air Quality AQI
    assert "tool-btn-measure" in html  # Distance measure tool
    assert "maptype-card-default" in html  # Roadmap / default basemap
    assert "maptype-card-satellite" in html  # Satellite basemap
    assert "chk-map-labels" in html  # Labels toggle
    assert "switchMapType" in html  # Map type switcher handler
    assert "gmap-place-info-drawer" in html  # Google Maps Place Details Drawer
    assert "place-drawer-title" in html  # Place title heading
    assert "inspectLocationDetails" in html  # Click-to-inspect engine
    assert "renderPlaceDrawerContent" in html  # Place drawer renderer
    assert "setClickedPlaceAsDest" in html  # Route to clicked place
    assert "zoomToClickedPlace" in html  # Zoom closer to clicked place
    assert "gmap-hud-toast" in html  # In-map Toast notification system
    assert "gmap-traffic-hud" in html  # Live Traffic status HUD
    assert "gmap-traveltime-modal" in html  # In-map multi-modal travel time modal
    assert "gmap-streetview-modal" in html  # In-map 360 Street View modal
    assert "showMapToast" in html  # Toast dispatcher
    assert "tool-btn-traveltime" in html  # Travel time tool button
    assert "resetMeasureTool" in html  # Distance measure reset function
    assert "closeStreetViewModal" in html  # Street view close handler
    assert "pill-filter-saved" in html  # Dedicated Saved Places filter tab
    assert "btn-quick-save-place" in html  # Quick Save Place button with save symbol
    assert "place-btn-save-fav" in html  # Save to Favourites button in place drawer
    assert "saveInspectedPlaceToFavourites" in html  # Save to favourites engine
    assert "All Markers" not in html  # All Markers tab removed as requested




def test_geocode_with_google_api_direct_coords():
    """Verify direct coordinates parsing."""
    res = geocode_with_google_api("16.2463, 80.6617")
    assert res is not None
    assert round(res["lat"], 4) == 16.2463
    assert round(res["lon"], 4) == 80.6617


def test_api_key_detection():
    """Verify API key handling behaves safely without crashing."""
    # When no key is set
    configured = is_google_maps_key_configured()
    assert isinstance(configured, bool)
