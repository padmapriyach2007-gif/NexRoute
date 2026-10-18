"""
Unit tests for Suggested Places, Driving Travel Modes Comparison & Google Maps Place Details.
"""

import pytest
from src.places_and_driving_modes import (
    generate_suggested_places_at_location,
    compare_driving_travel_modes,
    render_place_details_card_html
)


def test_generate_suggested_places_at_location():
    places = generate_suggested_places_at_location(17.8105, 77.5321, "Ranjole")
    assert len(places) >= 5
    for p in places:
        assert p["name"]
        assert p["category"]
        assert p["rating"] >= 4.0
        assert p["reviews_count"] > 100
        assert p["open_status"]
        assert "https://www.google.com/maps/search/?api=1" in p["google_maps_url"]
        assert "https://www.google.com/maps/dir/?api=1" in p["directions_url"]
        assert abs(p["latitude"] - 17.8105) < 0.1
        assert abs(p["longitude"] - 77.5321) < 0.1


def test_compare_driving_travel_modes_picks_best():
    # Long highway route without hazards -> Fastest should win
    res = compare_driving_travel_modes(distance_km=45.0, base_duration_mins=40.0, has_hazards_on_fastest=False)
    assert res["best_mode_id"] == "DRIVE_FASTEST"
    assert len(res["modes"]) == 5
    assert any(m["is_best"] for m in res["modes"])

    # Route with active hazards -> Safest must win autonomously
    res_hazards = compare_driving_travel_modes(distance_km=45.0, base_duration_mins=40.0, has_hazards_on_fastest=True)
    assert res_hazards["best_mode_id"] == "DRIVE_SAFEST"
    best_m = next(m for m in res_hazards["modes"] if m["is_best"])
    assert best_m["safety_score"] == 100

    # Short city trip (< 12 km) -> Eco fuel-saver should win
    res_short = compare_driving_travel_modes(distance_km=6.0, base_duration_mins=12.0, has_hazards_on_fastest=False)
    assert res_short["best_mode_id"] == "DRIVE_ECO"


def test_render_place_details_card_html():
    place = {
        "name": "Heritage Cafe & Bakery",
        "category": "Cafe",
        "icon": "☕",
        "rating": 4.9,
        "reviews_count": 850,
        "tag": "TOP SPOT",
        "tag_color": "#38bdf8",
        "distance_km": 1.2,
        "eta_minutes": 3,
        "open_status": "Open Now",
        "description": "Artisanal bakery and lounge.",
        "phone": "+91 800 111 222",
        "address": "Main High Street",
        "latitude": 17.81,
        "longitude": 77.53,
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=Heritage+Cafe",
        "directions_url": "https://www.google.com/maps/dir/?api=1&destination=17.81,77.53",
        "highlights": ["Outdoor Seating", "WiFi"]
    }
    html = render_place_details_card_html(place)
    assert "Heritage Cafe & Bakery" in html
    assert "application-map-viewport" in html
    assert "★ 4.9" in html
    assert "View on In-App Map" in html
