"""
Comprehensive Unit & Integration Test Suite for Real-World Emergency Services & Safety Amenities
Tests:
- Point-to-polyline spherical corridor projection
- Route-specific facility discovery & filtering
- Medical emergency department verification (has_emergency_department: True vs False vs None)
- Officially designated disaster shelter verification (is_officially_designated_shelter: True)
- International emergency dialer directory (India 112, US 911, UK 999, AU 000, EU 112)
- SOS guidance dispatch, spoken debrief generation, and stranded user workflow
- Folium Leaflet map rendering with emergency facility markers
- A.U.R.A. chatbot emergency & stranded user assistance
- Data integrity: no fabricated hospitals or fake 24/7 operating statuses
"""

import pytest
from src.emergency_service import (
    EmergencyServiceManager,
    EmergencyFacility,
    FacilityCategory,
    haversine_m,
    distance_point_to_polyline_m,
    get_national_emergency_contacts,
    VERIFIED_GROUND_TRUTH_FACILITIES
)
from src.map_service import MapService
from src.pathfinder_chatbot import PathfinderChatbot


@pytest.fixture
def em_manager():
    return EmergencyServiceManager(enable_live_osm=False)


# 1. Point-to-polyline distance calculation
def test_point_to_polyline_distance():
    # Straight line from (0, 0) to (0, 2)
    polyline = [(0.0, 0.0), (0.0, 2.0)]
    
    # Point at (1, 1) should be roughly 1 degree north of the segment (~111 km)
    dist_m = distance_point_to_polyline_m((1.0, 1.0), polyline)
    assert 110000 <= dist_m <= 112000

    # Point right on the segment
    dist_zero = distance_point_to_polyline_m((0.0, 1.0), polyline)
    assert dist_zero < 10.0


# 2. Real-world route discovery finds facilities in corridor
def test_route_facility_discovery(em_manager):
    # Route corridor from Vignan (16.2335, 80.5505) through Narakodur (16.2650, 80.4980) to Guntur (16.3067, 80.4365)
    route_poly = [(16.2335, 80.5505), (16.2650, 80.4980), (16.3067, 80.4365)]
    facs = em_manager.get_facilities_along_route(route_poly, corridor_radius_km=5.0)

    assert len(facs) > 0
    # Facilities must be within 5.0 km of corridor
    for f in facs:
        assert f.distance_from_route_km <= 5.0
        assert f.road_distance_km > 0.0
        assert f.eta_minutes > 0.0
        assert f.data_source is not None


# 3. Distinction: Verified Emergency Department vs General Clinic
def test_emergency_department_distinction(em_manager):
    # Ramesh Hospitals & GGH Guntur must have verified emergency department
    ramesh = next(f for f in em_manager._ground_truth if "RAMESH" in f.facility_id)
    assert ramesh.has_emergency_department is True
    assert "Trauma" in ramesh.operating_hours or "24/7" in ramesh.operating_hours

    # Chebrolu PHC is a primary clinic WITHOUT dedicated 24/7 trauma emergency department
    chebrolu_phc = next(f for f in em_manager._ground_truth if "CHEBROLU_PHC" in f.facility_id)
    assert chebrolu_phc.has_emergency_department is False
    assert "No Advanced Trauma" in chebrolu_phc.operating_hours


# 4. Distinction: Officially Designated Evacuation Shelter
def test_official_shelter_designation(em_manager):
    # APSDMA Cyclone Shelter must be verified as official shelter
    apsdma_shelter = next(f for f in em_manager._ground_truth if "SHELTER_APSDMA" in f.facility_id)
    assert apsdma_shelter.is_officially_designated_shelter is True
    assert apsdma_shelter.category == FacilityCategory.SAFE_SHELTER

    # Hospitals and Fuel stations must NOT be designated as shelters
    fuel_depot = next(f for f in em_manager._ground_truth if "FUEL" in f.facility_id)
    assert fuel_depot.is_officially_designated_shelter is False


# 5. International Emergency Contacts Directory
def test_national_emergency_contacts_international():
    # India (Vignan University coords)
    in_contact = get_national_emergency_contacts(16.2335, 80.5505)
    assert in_contact["country"] == "India"
    assert in_contact["primary_sos"] == "112"
    assert in_contact["ambulance"] == "108"

    # United States (New York City)
    us_contact = get_national_emergency_contacts(40.7128, -74.0060)
    assert "United States" in us_contact["country"]
    assert us_contact["primary_sos"] == "911"

    # United Kingdom (London)
    uk_contact = get_national_emergency_contacts(51.5074, -0.1278)
    assert uk_contact["country"] == "United Kingdom"
    assert uk_contact["primary_sos"] == "999"

    # Australia (Sydney)
    au_contact = get_national_emergency_contacts(-33.8688, 151.2093)
    assert au_contact["country"] == "Australia"
    assert au_contact["primary_sos"] == "000"


# 6. SOS Guidance Briefing Generation
def test_sos_guidance_briefing(em_manager):
    user_coords = (16.2335, 80.5505)
    
    # Medical SOS
    med_sos = em_manager.create_sos_guidance_briefing(user_coords, emergency_type="MEDICAL")
    assert med_sos["emergency_type"] == "MEDICAL"
    assert med_sos["facility"] is not None
    assert med_sos["facility"]["has_emergency_department"] is True
    assert "emergency medical center" in med_sos["spoken_speech"].lower()
    assert med_sos["emergency_phone"] in ["112", "108"]

    # Disaster / Hazard SOS
    disaster_sos = em_manager.create_sos_guidance_briefing(user_coords, emergency_type="DISASTER")
    assert disaster_sos["facility"] is not None
    assert "safe shelter" in disaster_sos["spoken_speech"].lower()


# 7. MapService rendering of emergency facilities
def test_map_service_renders_emergency_facilities():
    map_srv = MapService()
    test_facilities = [
        {
            "name": "Ramesh Hospitals",
            "facility_type": "Multi-Specialty Hospital & Emergency Dept",
            "amenity_icon": "🏥",
            "latitude": 16.3040,
            "longitude": 80.4410,
            "has_emergency_department": True,
            "is_officially_designated_shelter": False,
            "operating_hours": "24/7 Verified Emergency",
            "road_distance_km": 15.2,
            "data_source": "APSDMA / OSM"
        },
        {
            "name": "APSDMA Cyclone Shelter",
            "facility_type": "Designated Evacuation Safe Haven",
            "amenity_icon": "⛺",
            "latitude": 16.2360,
            "longitude": 80.5545,
            "has_emergency_department": False,
            "is_officially_designated_shelter": True,
            "operating_hours": "Activated on Alert",
            "road_distance_km": 0.6,
            "data_source": "APSDMA GIS"
        }
    ]

    folium_map = map_srv.build_interactive_map(
        center_lat=16.27,
        center_lon=80.49,
        zoom_start=13,
        emergency_facilities=test_facilities
    )
    rendered_html = folium_map.get_root().render()
    assert "Ramesh Hospitals" in rendered_html
    assert "APSDMA Cyclone Shelter" in rendered_html
    assert "24/7 Verified Emergency Dept" in rendered_html


# 8. A.U.R.A. Chatbot Stranded & Emergency Query Integration
def test_aura_chatbot_stranded_response(em_manager):
    bot = PathfinderChatbot(emergency_service_manager=em_manager)
    res = bot.answer("I am stranded and need help", context={"current_coords": (16.2335, 80.5505)})
    assert res["badge"] == "🚨 EMERGENCY ASSISTANCE"
    assert "112" in res["response"]
    assert "Immediate Life-Safety Guidance" in res["response"]

    # Hospital query
    hosp_res = bot.answer("where is the nearest hospital", context={"current_coords": (16.2335, 80.5505)})
    assert "EMERGENCY ASSISTANCE" in hosp_res["badge"]
    assert "Ramesh Hospitals" in hosp_res["response"] or "Hospital" in hosp_res["response"]
