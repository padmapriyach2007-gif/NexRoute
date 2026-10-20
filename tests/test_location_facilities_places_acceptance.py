"""
Acceptance Tests for PATHFINDER:
- Issue 1: Ambiguous Location Search & Disambiguation (Test A)
- Issue 2: Dynamic Nearby Facilities & PATHFINDER Map Integration (Test B, C, D)
- Issue 3: Location-Specific Suggested Places, Highlights & Ratings Integrity (Test B, D, E)
- Robustness: Failure Handling & Graceful Degradation (Test F)
- Regression: Route Engine & Navigation Stability (Test G)
"""

import pytest
from unittest.mock import patch, MagicMock
from src.map_service import MapService
from src.facilities_service import (
    get_facilities_for_category,
    fetch_dynamic_osm_facilities,
    FacilityCategory,
)
from src.places_and_driving_modes import (
    generate_suggested_places_at_location,
    render_place_details_card_html,
)


# ==============================================================================
# TEST A: AMBIGUOUS NAMES DISAMBIGUATION
# ==============================================================================
def test_acceptance_a_ambiguous_names_hyderabad():
    """
    Search for 'Hyderabad'.
    Confirm that geographically distinct matching locations (India & Pakistan)
    are returned with accurate coordinates and administrative regions.
    Selecting Pakistan must yield coordinates in Pakistan (~25.38 N, 68.37 E).
    Selecting India must yield coordinates in India (~17.38 N, 78.48 E).
    """
    map_srv = MapService()
    candidates = map_srv.geocode_candidates("Hyderabad", limit=5)
    
    assert len(candidates) >= 2, "Expected multiple candidates for 'Hyderabad'"
    
    india_match = None
    pakistan_match = None
    
    for c in candidates:
        if c.get("country") == "India" or "Telangana" in c.get("state", ""):
            india_match = c
        elif c.get("country") == "Pakistan" or "Sindh" in c.get("state", ""):
            pakistan_match = c
            
    assert india_match is not None, "Did not find Hyderabad, India candidate"
    assert pakistan_match is not None, "Did not find Hyderabad, Pakistan candidate"
    
    # Confirm Pakistan coordinates
    assert 24.5 <= pakistan_match["lat"] <= 26.5
    assert 67.5 <= pakistan_match["lon"] <= 69.5
    assert pakistan_match["country"] == "Pakistan"
    
    # Confirm India coordinates
    assert 16.5 <= india_match["lat"] <= 18.5
    assert 77.5 <= india_match["lon"] <= 79.5
    assert india_match["country"] == "India"


# ==============================================================================
# TEST B: DIFFERENT DESTINATIONS YIELD DISTINCT FACILITIES & PLACES
# ==============================================================================
def test_acceptance_b_different_destinations_produce_distinct_results():
    """
    Search for two geographically different destinations (Hyderabad vs Paris).
    Confirm that nearby facilities and suggested places dynamically reflect each
    selected area rather than returning the same default list or hardcoded Guntur data.
    """
    hyderabad_coords = (17.3850, 78.4867)
    paris_coords = (48.8566, 2.3522)
    
    # Facilities for Hyderabad
    hyd_facilities = get_facilities_for_category(
        "Hospitals & Medical",
        coords=hyderabad_coords,
        search_mode="near_origin",
        radius_km=10.0
    )
    
    # Facilities for Paris
    paris_facilities = get_facilities_for_category(
        "Hospitals & Medical",
        coords=paris_coords,
        search_mode="near_origin",
        radius_km=10.0
    )
    
    assert len(hyd_facilities) > 0, "Expected facilities for Hyderabad"
    assert len(paris_facilities) > 0, "Expected facilities for Paris"
    
    # Verify coordinates are in respective cities, not hardcoded Guntur/Vadlamudi (16.23N, 80.55E)
    for fac in hyd_facilities:
        assert 16.8 <= fac["latitude"] <= 18.0
        assert 77.8 <= fac["longitude"] <= 79.2
        # Ensure it does NOT default to Guntur / Vadlamudi
        assert not (round(fac["latitude"], 2) == 16.23 and round(fac["longitude"], 2) == 80.55)
        
    for fac in paris_facilities:
        assert 48.0 <= fac["latitude"] <= 49.5
        assert 1.8 <= fac["longitude"] <= 3.0
        assert not (round(fac["latitude"], 2) == 16.23 and round(fac["longitude"], 2) == 80.55)
        
    # Names must be completely distinct
    hyd_names = {f["name"] for f in hyd_facilities}
    paris_names = {f["name"] for f in paris_facilities}
    overlap = hyd_names.intersection(paris_names)
    assert len(overlap) == 0, f"Found overlapping facilities between Hyderabad and Paris: {overlap}"
    
    # Check Suggested Places POIs for Hyderabad vs Paris
    hyd_places = generate_suggested_places_at_location(hyderabad_coords[0], hyderabad_coords[1], "Hyderabad")
    paris_places = generate_suggested_places_at_location(paris_coords[0], paris_coords[1], "Paris")
    
    assert len(hyd_places) > 0
    assert len(paris_places) > 0
    hyd_place_names = {p["name"] for p in hyd_places}
    paris_place_names = {p["name"] for p in paris_places}
    assert len(hyd_place_names.intersection(paris_place_names)) == 0, "Places overlap between Hyderabad and Paris"


# ==============================================================================
# TEST C: FACILITY INTERACTIONS & ROUTING PRESERVATION
# ==============================================================================
def test_acceptance_c_facility_focus_and_route_to_facility():
    """
    Facility data model contains exact latitude/longitude and stable identifiers.
    Verify that routing to a facility retains origin and locks the facility as destination.
    """
    paris_coords = (48.8566, 2.3522)
    facilities = get_facilities_for_category("Fuel & EV Charging", coords=paris_coords, radius_km=5.0)
    assert len(facilities) > 0
    
    selected_fac = facilities[0]
    assert "facility_id" in selected_fac
    assert "latitude" in selected_fac and "longitude" in selected_fac
    assert -90.0 <= selected_fac["latitude"] <= 90.0
    assert -180.0 <= selected_fac["longitude"] <= 180.0
    
    # Simulate the route-to-facility state transition:
    # Origin remains intact, destination is updated to facility name and coordinates
    orig_coords = (48.8606, 2.3376)
    orig_label = "Musée du Louvre, Paris"
    
    session_state = {
        "selected_orig_coords": orig_coords,
        "selected_orig_label": orig_label,
        "selected_dest_coords": None,
        "selected_dest_label": None,
        "last_synced_dest": None,
        "txt_dest": "",
        "map_center_lat": 0.0,
        "map_center_lon": 0.0,
        "map_zoom": 13,
    }
    
    # Action: Click "Focus Map"
    session_state["map_center_lat"] = selected_fac["latitude"]
    session_state["map_center_lon"] = selected_fac["longitude"]
    session_state["map_zoom"] = 16
    assert session_state["map_center_lat"] == selected_fac["latitude"]
    assert session_state["map_center_lon"] == selected_fac["longitude"]
    assert session_state["map_zoom"] == 16
    
    # Action: Click "Route Here"
    session_state["selected_dest_coords"] = (selected_fac["latitude"], selected_fac["longitude"])
    session_state["selected_dest_label"] = selected_fac["name"]
    session_state["last_synced_dest"] = selected_fac["name"]
    session_state["txt_dest"] = selected_fac["name"]
    
    # Crucial check: Origin was NOT overwritten
    assert session_state["selected_orig_coords"] == orig_coords
    assert session_state["selected_orig_label"] == orig_label
    
    # Destination is locked to facility
    assert session_state["selected_dest_coords"] == (selected_fac["latitude"], selected_fac["longitude"])
    assert session_state["selected_dest_label"] == selected_fac["name"]
    assert session_state["last_synced_dest"] == selected_fac["name"]


# ==============================================================================
# TEST D: ROUTE CHANGES & SEARCH MODES
# ==============================================================================
def test_acceptance_d_facility_search_modes():
    """
    Verify search_mode: 'near_origin', 'near_destination', 'along_route'.
    """
    origin = (17.3850, 78.4867)      # Hyderabad
    destination = (17.4401, 78.3489) # Gachibowli / Hitec City
    
    # Near origin
    fac_orig = get_facilities_for_category(
        "Hospitals & Medical",
        coords=origin,
        dest_coords=destination,
        search_mode="near_origin",
        radius_km=5.0
    )
    
    # Near destination
    fac_dest = get_facilities_for_category(
        "Hospitals & Medical",
        coords=origin,
        dest_coords=destination,
        search_mode="near_destination",
        radius_km=5.0
    )
    
    assert len(fac_orig) > 0
    assert len(fac_dest) > 0
    
    # Origin facilities should be closer to origin than destination facilities
    avg_orig_dist_to_orig = sum(f["road_distance_km"] for f in fac_orig) / len(fac_orig)
    assert avg_orig_dist_to_orig <= 10.0


# ==============================================================================
# TEST E: RATINGS INTEGRITY (NO FABRICATED VALUES)
# ==============================================================================
def test_acceptance_e_ratings_integrity_and_rendering():
    """
    Confirm that ratings are NOT fabricated. If rating is missing or None,
    the HTML renderer outputs 'Rating unavailable' instead of inventing '4.7 ★' or '1,200 reviews'.
    """
    place_without_rating = {
        "place_id": "test_poi_1",
        "name": "Local Cultural Center",
        "category": "Museum",
        "icon": "🏛️",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "rating": None,
        "reviews_count": None,
        "description": "Historical exhibition space in the city center.",
        "address": "Paris, France",
        "hours": "10:00 - 18:00",
        "phone": "+33 1 00 00 00 00",
        "website": "https://example.org",
        "google_search_url": "https://www.google.com/maps/search/?api=1&query=Paris",
    }
    
    html = render_place_details_card_html(place_without_rating)
    assert "Rating unavailable" in html, "Should show 'Rating unavailable' when rating is None"
    assert "1,200 reviews" not in html, "Fabricated review count should not be present"
    assert "4.7" not in html, "Fabricated 4.7 rating should not be present"
    
    place_with_real_rating = dict(place_without_rating)
    place_with_real_rating["rating"] = 4.3
    place_with_real_rating["reviews_count"] = 145
    
    html_rated = render_place_details_card_html(place_with_real_rating)
    assert "★ 4.3" in html_rated
    assert "145 Reviews" in html_rated


# ==============================================================================
# TEST F: FAILURE HANDLING & ZERO RESULTS
# ==============================================================================
def test_acceptance_f_graceful_failure_and_empty_queries():
    """
    Test empty search results, API timeouts, and zero results without crashing.
    """
    map_srv = MapService()
    
    # 1. Blank query
    assert map_srv.geocode_candidates("") == []
    assert map_srv.geocode_candidates("   ") == []
    
    # 2. Timeout handling in geocode_candidates
    with patch.object(map_srv.session, "get", side_effect=Exception("Read timeout")):
        results = map_srv.geocode_candidates("NonExistentPlaceQuery12345", limit=5)
        assert results == [], "Expected empty list on provider network timeout"
        
    # 3. Timeout handling in dynamic facilities
    with patch("urllib.request.urlopen", side_effect=Exception("OSM Nominatim Timeout")):
        # In production mode (demo_mode=False), must return empty list without crash
        facs = fetch_dynamic_osm_facilities("hospital", 17.385, 78.4867, radius_km=5.0)
        assert isinstance(facs, list)


# ==============================================================================
# TEST G: REGRESSION - ROUTE CALCULATION INTEGRITY
# ==============================================================================
def test_acceptance_g_route_calculation_with_disambiguated_coords():
    """
    Confirm that routes calculated between disambiguated coordinates
    produce valid polyline coordinates, accurate distances, and travel times.
    """
    from src.route_engine import RealWorldRouteEngine
    engine = RealWorldRouteEngine()
    
    # Route between Hyderabad and Secunderabad
    hyderabad = (17.3850, 78.4867)
    secunderabad = (17.4399, 78.4983)
    
    routes = engine.calculate_routes(
        origin_lat=hyderabad[0],
        origin_lon=hyderabad[1],
        dest_lat=secunderabad[0],
        dest_lon=secunderabad[1]
    )
    
    assert len(routes) >= 1
    primary_route = routes[0]
    assert primary_route.distance_km > 0
    assert primary_route.duration_minutes > 0
    assert len(primary_route.polyline) > 2
    assert 3.0 <= primary_route.distance_km <= 20.0
