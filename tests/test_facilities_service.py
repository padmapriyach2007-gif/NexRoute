"""
Unit tests for Facilities & Amenity Discovery Service.
Verifies all amenity categories:
- Restaurants
- Petrol / Fuel
- Hotels
- Emergency
- ATM / Banking
- Shopping Malls
- Hospital Clinics
- Custom Location Search
"""

import pytest
from src.facilities_service import (
    get_facilities_for_category,
    resolve_custom_search_facility,
    CATEGORY_CONFIG,
    FacilityCategory,
    haversine_km
)


def test_category_config_contains_all_requested_categories():
    assert FacilityCategory.RESTAURANTS in CATEGORY_CONFIG
    assert FacilityCategory.PETROL in CATEGORY_CONFIG
    assert FacilityCategory.HOTELS in CATEGORY_CONFIG
    assert FacilityCategory.EMERGENCY in CATEGORY_CONFIG
    assert FacilityCategory.ATM in CATEGORY_CONFIG
    assert FacilityCategory.SHOPPING_MALLS in CATEGORY_CONFIG
    assert FacilityCategory.HOSPITAL_CLINICS in CATEGORY_CONFIG
    assert FacilityCategory.CUSTOM_SEARCH in CATEGORY_CONFIG


def test_get_restaurants_facilities():
    polyline = [(16.241, 80.584), (16.233, 80.550)]
    facs = get_facilities_for_category("restaurants", polyline=polyline, origin_coords=(16.241, 80.584))
    assert len(facs) >= 2
    for f in facs:
        assert f["category"] == FacilityCategory.RESTAURANTS
        assert "🍽️" in f["amenity_icon"]
        assert f["road_distance_km"] >= 0.0
        assert f["latitude"] is not None
        assert f["longitude"] is not None


def test_get_petrol_facilities():
    polyline = [(16.241, 80.584), (16.233, 80.550)]
    facs = get_facilities_for_category("petrol", polyline=polyline, origin_coords=(16.241, 80.584))
    assert len(facs) >= 2
    assert any("Indian Oil" in f["name"] or "HPCL" in f["name"] or "BPCL" in f["name"] for f in facs)
    assert all(f["category"] == FacilityCategory.PETROL for f in facs)


def test_get_hotels_facilities():
    facs = get_facilities_for_category("hotels", origin_coords=(16.241, 80.584))
    assert len(facs) >= 2
    assert any("Hotel" in f["name"] or "Lodge" in f["name"] for f in facs)
    assert all(f["category"] == FacilityCategory.HOTELS for f in facs)


def test_get_emergency_facilities():
    facs = get_facilities_for_category("emergency", origin_coords=(16.241, 80.584))
    assert len(facs) >= 2
    assert any("Police" in f["name"] or "Fire" in f["name"] for f in facs)
    assert all(f["category"] == FacilityCategory.EMERGENCY for f in facs)


def test_get_atm_facilities():
    facs = get_facilities_for_category("atm", origin_coords=(16.241, 80.584))
    assert len(facs) >= 2
    assert any("SBI" in f["name"] or "HDFC" in f["name"] or "ICICI" in f["name"] for f in facs)
    assert all(f["category"] == FacilityCategory.ATM for f in facs)


def test_get_shopping_malls():
    facs = get_facilities_for_category("shopping_malls", origin_coords=(16.241, 80.584))
    assert len(facs) >= 2
    assert any("Mall" in f["name"] or "Superstore" in f["name"] or "DMart" in f["name"] for f in facs)
    assert all(f["category"] == FacilityCategory.SHOPPING_MALLS for f in facs)


def test_get_hospital_clinics():
    facs = get_facilities_for_category("hospital_clinics", origin_coords=(16.241, 80.584))
    assert len(facs) >= 2
    assert any("Hospital" in f["name"] or "Clinic" in f["name"] for f in facs)
    assert all(f["category"] == FacilityCategory.HOSPITAL_CLINICS for f in facs)


def test_resolve_custom_search_coordinates():
    origin = (16.241, 80.584)
    res = resolve_custom_search_facility("16.3000, 80.4500", origin_coords=origin)
    assert res is not None
    assert res["category"] == FacilityCategory.CUSTOM_SEARCH
    assert abs(res["latitude"] - 16.3000) < 0.001
    assert abs(res["longitude"] - 80.4500) < 0.001
    assert res["road_distance_km"] > 0.0


def test_resolve_custom_search_place_name():
    origin = (16.241, 80.584)
    res = resolve_custom_search_facility("Tenali Railway Station", origin_coords=origin)
    assert res is not None
    assert res["category"] == FacilityCategory.CUSTOM_SEARCH
    assert "Tenali" in res["name"]
    assert res["latitude"] is not None
    assert res["longitude"] is not None


def test_worldwide_facilities_discovery_ranjole():
    # Ranjole coordinates (Bidar region / Karnataka, user's uploaded location)
    ranjole_coords = (17.8105, 77.5321)
    
    # Test all facilities
    all_facs = get_facilities_for_category("🌐 All Facilities", origin_coords=ranjole_coords)
    assert len(all_facs) >= 8
    # Proximity check: all generated facilities must be within 5 km of Ranjole
    for f in all_facs:
        dist = haversine_km(ranjole_coords[0], ranjole_coords[1], f["latitude"], f["longitude"])
        assert dist <= 5.0
        assert f["road_distance_km"] > 0.0

    # Test individual categories in Ranjole
    hospitals = get_facilities_for_category("🏥 Hospitals", origin_coords=ranjole_coords)
    assert len(hospitals) >= 3
    assert all(h["category"] == FacilityCategory.HOSPITAL_CLINICS for h in hospitals)

    fuel = get_facilities_for_category("⛽ Fuel/Charging", origin_coords=ranjole_coords)
    assert len(fuel) >= 3
    assert all(f["category"] == FacilityCategory.PETROL for f in fuel)

    restaurants = get_facilities_for_category("🍽️ Restaurants", origin_coords=ranjole_coords)
    assert len(restaurants) >= 3
    assert all(r["category"] == FacilityCategory.RESTAURANTS for r in restaurants)


def test_worldwide_facilities_discovery_global_city():
    # Test worldwide support in New York City
    nyc_coords = (40.7128, -74.0060)
    malls = get_facilities_for_category("🛍️ Shopping Malls", origin_coords=nyc_coords)
    assert len(malls) >= 2
    for m in malls:
        dist = haversine_km(nyc_coords[0], nyc_coords[1], m["latitude"], m["longitude"])
        assert dist <= 5.0
        assert m["category"] == FacilityCategory.SHOPPING_MALLS

