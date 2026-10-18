"""
Unit tests for Google Maps Features and Next-Gen Loophole Resolver Module.
"""

import pytest
from src.google_maps_features import (
    get_google_maps_app_url,
    get_google_maps_loopholes_data,
    build_google_maps_toolbar_html,
    build_loopholes_deck_html
)


def test_get_google_maps_app_url():
    url = get_google_maps_app_url(
        origin_lat=16.3067,
        origin_lon=80.4365,
        dest_lat=16.2335,
        dest_lon=80.5505,
        travel_mode="driving",
        avoid_tolls=True,
        avoid_highways=True
    )
    assert "https://www.google.com/maps/dir/?api=1" in url
    assert "origin=16.306700%2C80.436500" in url
    assert "destination=16.233500%2C80.550500" in url
    assert "avoid=tolls%2Chighways" in url or "avoid=tolls,highways" in url


def test_get_google_maps_loopholes_data():
    loopholes = get_google_maps_loopholes_data()
    assert len(loopholes) == 5
    ids = [item["id"] for item in loopholes]
    assert "hazard_flood" in ids
    assert "accessibility" in ids
    assert "fleet_blindness" in ids
    assert "cellular_blackout" in ids
    assert "emergency_isolation" in ids

    for item in loopholes:
        assert "title" in item
        assert "google_maps_gap" in item
        assert "pathfinder_solution" in item
        assert "metric" in item


def test_build_google_maps_toolbar_html():
    html = build_google_maps_toolbar_html(
        app_url="https://www.google.com/maps/dir/?api=1",
        active_style="satellite_hybrid",
        avoid_tolls=True,
        avoid_highways=False,
        avoid_ferries=False
    )
    assert "GOOGLE MAPS SUITE" in html
    assert "Open in Official Google Maps App" in html
    assert "Avoid Tolls" in html


def test_build_loopholes_deck_html():
    loopholes = get_google_maps_loopholes_data()
    html = build_loopholes_deck_html(loopholes)
    assert "THE NEXT STEP OF GOOGLE MAPS" in html
    assert "Blind Disaster & Flood Routing" in html
    assert "Inaccessible Pedestrian Steps" in html
    assert "Vehicle & Fleet Disregard" in html
    assert "Total Cellular Blackout" in html
    assert "Emergency Isolation" in html
