"""
Unit tests for Emergency Radar UI module.
"""

import pytest
from src.emergency_radar_ui import (
    generate_google_maps_directions_url,
    filter_facilities_by_category,
    get_facility_status_badge
)
from src.emergency_service import EmergencyFacility, FacilityCategory


def test_google_maps_directions_url():
    url = generate_google_maps_directions_url(
        origin_lat=16.3067,
        origin_lon=80.4365,
        dest_lat=16.2335,
        dest_lon=80.5505
    )
    assert "https://www.google.com/maps/dir/?api=1" in url
    assert "origin=16.306700%2C80.436500" in url
    assert "destination=16.233500%2C80.550500" in url
    assert "travelmode=driving" in url


def test_filter_facilities_by_category():
    facs = [
        EmergencyFacility(
            facility_id="f1",
            name="General Hospital",
            category=FacilityCategory.MEDICAL,
            facility_type="Hospital",
            latitude=16.3,
            longitude=80.4,
            has_emergency_department=True
        ),
        EmergencyFacility(
            facility_id="f2",
            name="Police Station",
            category=FacilityCategory.EMERGENCY_ASSISTANCE,
            facility_type="Police Station",
            latitude=16.31,
            longitude=80.41
        ),
        EmergencyFacility(
            facility_id="f3",
            name="Cyclone Shelter",
            category=FacilityCategory.SAFE_SHELTER,
            facility_type="Disaster Shelter",
            latitude=16.32,
            longitude=80.42,
            is_officially_designated_shelter=True
        )
    ]

    all_facs = filter_facilities_by_category(facs, "ALL")
    assert len(all_facs) == 3

    med_facs = filter_facilities_by_category(facs, "MEDICAL")
    assert len(med_facs) == 1
    assert med_facs[0].name == "General Hospital"

    pol_facs = filter_facilities_by_category(facs, "ASSISTANCE")
    assert len(pol_facs) == 1
    assert pol_facs[0].name == "Police Station"

    shelter_facs = filter_facilities_by_category(facs, "SHELTER")
    assert len(shelter_facs) == 1
    assert shelter_facs[0].name == "Cyclone Shelter"


def test_facility_status_badge():
    fac_ed = EmergencyFacility(
        facility_id="f1",
        name="General Hospital",
        category=FacilityCategory.MEDICAL,
        facility_type="Hospital",
        latitude=16.3,
        longitude=80.4,
        has_emergency_department=True
    )
    badge = get_facility_status_badge(fac_ed)
    assert "24/7 VERIFIED EMERGENCY DEPT" in badge

    fac_shelter = EmergencyFacility(
        facility_id="f2",
        name="Cyclone Shelter",
        category=FacilityCategory.SAFE_SHELTER,
        facility_type="Shelter",
        latitude=16.3,
        longitude=80.4,
        is_officially_designated_shelter=True
    )
    badge_shelter = get_facility_status_badge(fac_shelter)
    assert "DESIGNATED SAFE HAVEN" in badge_shelter


def test_google_maps_directions_url_with_avoidances():
    url = generate_google_maps_directions_url(
        origin_lat=16.3067,
        origin_lon=80.4365,
        dest_lat=16.2335,
        dest_lon=80.5505,
        travel_mode="walking",
        avoid_tolls=True,
        avoid_highways=True
    )
    assert "travelmode=walking" in url
    assert "avoid=tolls%2Chighways" in url or "avoid=tolls,highways" in url


def test_google_maps_directions_url_travel_modes():
    url_bike = generate_google_maps_directions_url(16.3, 80.4, 16.2, 80.5, travel_mode="bicycle")
    assert "travelmode=bicycling" in url_bike

    url_bus = generate_google_maps_directions_url(16.3, 80.4, 16.2, 80.5, travel_mode="bus")
    assert "travelmode=transit" in url_bus

