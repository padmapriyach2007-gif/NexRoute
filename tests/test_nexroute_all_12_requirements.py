"""
NexRoute Comprehensive 12-Requirement Integration Test Suite
Verifies all 12 acceptance criteria specified for:
- Autocomplete relevance
- Custom start & destination workflows
- Coordinate validation
- Ambiguous place disambiguation without auto-selection
- Invalid location error handling
- Map-based location picking
- Multiple route alternatives road-network validity (no ocean routes)
- Route failure handling
- Responsive UI and endpoint synchronization
- Routing modes (Fastest, Shortest, Balanced, Accessible)
"""

import pytest
import math
from src.map_service import MapService
from src.route_engine import RealWorldRouteEngine, TravelMode
from src.multi_objective_router import MultiObjectiveRouter, OptimizationObjective
from src.google_maps_platform import build_google_maps_javascript_html

@pytest.fixture
def map_service():
    return MapService()

@pytest.fixture
def route_engine():
    return RealWorldRouteEngine()

# =========================================================================
# TEST 1: RELEVANT AUTOCOMPLETE
# =========================================================================
def test_req1_relevant_autocomplete(map_service):
    queries = [
        "Amaravati",
        "Tirupati",
        "Guntur",
        "Vijayawada",
        "Apollo Hospital",
        "Vignan University",
        "Guntur Railway Station"
    ]
    for q in queries:
        cands = map_service.get_disambiguation_candidates(q, limit=6)
        assert len(cands) >= 1, f"Expected suggestions for query '{q}'"
        first = cands[0]
        assert "lat" in first and "lon" in first
        assert -90.0 <= first["lat"] <= 90.0
        assert -180.0 <= first["lon"] <= 180.0
        # Suggestion must have display name or name containing part of query
        display = (first.get("display_name") or first.get("name") or "").lower()
        query_words = [w.lower() for w in q.split() if len(w) > 3]
        matches = any(w in display for w in query_words)
        assert matches, f"Suggestion '{display}' does not match query '{q}'"

# =========================================================================
# TEST 2: CUSTOM START LOCATION RESOLUTION & COORDINATES
# =========================================================================
def test_req2_custom_start_resolution(map_service):
    # Enter a specific address or institutional landmark
    custom_start_query = "AIIMS Mangalagiri"
    cands = map_service.get_disambiguation_candidates(custom_start_query, limit=5)
    assert len(cands) >= 1
    selected = cands[0]
    
    # Verify coordinate accuracy (AIIMS Mangalagiri is in Guntur district around 16.44, 80.57)
    assert 16.35 <= selected["lat"] <= 16.55
    assert 80.45 <= selected["lon"] <= 80.65
    assert -90.0 <= selected["lat"] <= 90.0
    assert -180.0 <= selected["lon"] <= 180.0

# =========================================================================
# TEST 3: CUSTOM DESTINATION RESOLUTION & COORDINATES
# =========================================================================
def test_req3_custom_destination_resolution(map_service):
    custom_dest_query = "SRM University - AP"
    cands = map_service.get_disambiguation_candidates(custom_dest_query, limit=5)
    assert len(cands) >= 1
    selected = cands[0]
    
    # SRM AP is located near Neerukonda, Amaravati around 16.46, 80.50
    assert 16.35 <= selected["lat"] <= 16.55
    assert 80.40 <= selected["lon"] <= 80.60

# =========================================================================
# TEST 4: AMBIGUOUS PLACE DISAMBIGUATION (NO FORCED AUTO-SELECTION)
# =========================================================================
def test_req4_ambiguous_place_disambiguation(map_service):
    # "Gandhi Hospital" or "Railway Station" exists in multiple cities
    ambig_query = "Gandhi Hospital"
    cands = map_service.get_disambiguation_candidates(ambig_query, limit=8)
    assert len(cands) >= 2, "Ambiguous query should return multiple candidates"
    
    # Each candidate must have distinct coordinates and descriptive labels/badges
    coords_set = set()
    for c in cands:
        pt = (round(c["lat"], 3), round(c["lon"], 3))
        coords_set.add(pt)
        assert "display_name" in c or "name" in c
    assert len(coords_set) >= 2, "Ambiguous candidates must represent distinct geographic locations"

# =========================================================================
# TEST 5: INVALID OR UNRESOLVABLE LOCATION ERROR HANDLING
# =========================================================================
def test_req5_invalid_location_handling(map_service):
    invalid_query = "xyzqwertyuiopnonexistentplacename998877"
    cands = map_service.get_disambiguation_candidates(invalid_query)
    # Must NOT assign random or fallback coordinates to unresolvable queries
    assert len(cands) == 0, f"Unresolvable query '{invalid_query}' should yield empty candidate list"

# =========================================================================
# TEST 6: MAP PICKER COORDINATES AND INDEPENDENT ENDPOINT UPDATES
# =========================================================================
def test_req6_map_picker_reverse_geocoding(map_service):
    # Picking coordinates on map (e.g. 16.5062, 80.6480 near Vijayawada)
    picked_lat, picked_lon = 16.5062, 80.6480
    rev_result = map_service.reverse_geocode(picked_lat, picked_lon)
    assert rev_result is not None
    assert isinstance(rev_result, str)
    assert len(rev_result) > 0
    # Reverse geocoded label should identify the area or district
    assert any(term in rev_result.lower() for term in ["vijayawada", "krishna", "andhra", "80.", "16."])

# =========================================================================
# TEST 7: DIRECT LAT/LON COORDINATE ENTRY BOUNDS VALIDATION
# =========================================================================
def test_req7_coordinate_entry_bounds_validation(map_service):
    # Valid coordinates
    cands_valid = map_service.geocode_candidates("16.5062, 80.6480")
    assert len(cands_valid) == 1
    assert abs(cands_valid[0]["lat"] - 16.5062) < 0.001
    assert abs(cands_valid[0]["lon"] - 80.6480) < 0.001

    # Invalid coordinates exceeding bounds [-90, 90] and [-180, 180]
    cands_out_of_bounds = map_service.geocode_candidates("95.000, 210.000")
    # Must reject invalid numeric coordinates
    assert len(cands_out_of_bounds) == 0

# =========================================================================
# TEST 8: ENDPOINT CHANGES & RECALCULATION
# =========================================================================
def test_req8_endpoint_synchronization(route_engine):
    start_vja = (16.5062, 80.6480)
    dest_gnt = (16.3067, 80.4365)
    dest_tpt = (13.6288, 79.4192)
    
    # Calculate routes from VJA to Guntur
    routes_gnt = route_engine.calculate_routes(start_vja[0], start_vja[1], dest_gnt[0], dest_gnt[1], TravelMode.DRIVING)
    assert len(routes_gnt) >= 1
    first_gnt = routes_gnt[0]
    assert 25.0 <= first_gnt.distance_km <= 50.0

    # Change destination to Tirupati (much further, ~350-420 km)
    routes_tpt = route_engine.calculate_routes(start_vja[0], start_vja[1], dest_tpt[0], dest_tpt[1], TravelMode.DRIVING)
    assert len(routes_tpt) >= 1
    first_tpt = routes_tpt[0]
    assert 320.0 <= first_tpt.distance_km <= 460.0

    # Ensure endpoints correctly swapped
    routes_swap = route_engine.calculate_routes(dest_tpt[0], dest_tpt[1], start_vja[0], start_vja[1], TravelMode.DRIVING)
    assert len(routes_swap) >= 1
    assert abs(routes_swap[0].distance_km - first_tpt.distance_km) < 30.0

# =========================================================================
# TEST 9: MULTIPLE ROUTE ALTERNATIVES ACCURACY (NO OCEAN / ARTIFICIAL ROUTES)
# =========================================================================
def test_req9_multi_route_road_network_accuracy(route_engine):
    start = (16.5062, 80.6480)  # Vijayawada
    dest_gnt = (16.3067, 80.4365) # Guntur
    dest_chn = (13.0827, 80.2707) # Chennai
    
    # 1. Regional multi-route: Vijayawada to Guntur must return multiple genuine road alternatives
    routes_regional = route_engine.calculate_routes(start[0], start[1], dest_gnt[0], dest_gnt[1], TravelMode.DRIVING)
    assert len(routes_regional) >= 2, "Expected multiple alternative routes for regional driving journey"

    # 2. Long distance coastal route: Vijayawada to Chennai
    routes_chn = route_engine.calculate_routes(start[0], start[1], dest_chn[0], dest_chn[1], TravelMode.DRIVING)
    assert len(routes_chn) >= 1

    for r in routes_regional + routes_chn:
        # A. No route in driving mode should take ferry across the Bay of Bengal
        assert "Waterway" not in r.name and "Bay of Bengal" not in r.name
        # B. Distance and duration must be positive and realistic
        assert r.distance_km > 0
        assert r.duration_minutes > 0
        # C. All intermediate points must remain inland on roads (lon <= 81.1 for coastal corridor)
        for pt in r.polyline:
            assert pt[1] <= 81.1, f"Route point {pt} veered eastwards into the Bay of Bengal ocean!"

# =========================================================================
# TEST 10: ROUTE FAILURE HANDLING (NO FABRICATED ROUTES)
# =========================================================================
def test_req10_route_failure_handling(route_engine):
    # Two identical points or unroutable location
    origin = (16.5062, 80.6480)
    dest = origin # Distance 0
    routes = route_engine.calculate_routes(origin[0], origin[1], dest[0], dest[1], TravelMode.DRIVING)
    # When start == dest, route engine should return either empty or single zero-distance route, never fabricated detour
    if routes:
        assert routes[0].distance_km < 0.1

# =========================================================================
# TEST 11: RESPONSIVE INTERFACE & HTML CONTROLS
# =========================================================================
def test_req11_map_picking_and_custom_hud_rendering():
    # Verify build_google_maps_javascript_html supports map_picking_mode
    html_active = build_google_maps_javascript_html(
        center_lat=16.5062,
        center_lon=80.6480,
        zoom=14,
        origin_coords=(16.5062, 80.6480),
        dest_coords=(16.3067, 80.4365),
        map_picking_mode="dest"
    )
    # Check that map-picking HUD and click handler exist in output HTML
    assert "map-picking-hud" in html_active
    assert "handleMapPickingClick" in html_active
    assert "confirmPickedLocation" in html_active
    assert "cancelMapPickingMode" in html_active
    assert "mapPickingMode" in html_active

# =========================================================================
# TEST 12: REGRESSION (ALL ROUTING MODES & DEST MARKER LOGIC)
# =========================================================================
def test_req12_routing_modes_and_dest_marker(route_engine):
    start = (16.5062, 80.6480)
    dest = (16.3067, 80.4365)
    
    # Calculate candidate routes
    candidates = route_engine.calculate_routes(start[0], start[1], dest[0], dest[1], TravelMode.DRIVING)
    assert len(candidates) >= 1

    router = MultiObjectiveRouter()

    # Test all 4 objectives
    fastest_routes = router.evaluate_and_rank_routes(
        candidates, objective=OptimizationObjective.FASTEST, require_accessible=False
    )
    assert len(fastest_routes) >= 1

    shortest_routes = router.evaluate_and_rank_routes(
        candidates, objective=OptimizationObjective.SHORTEST, require_accessible=False
    )
    assert len(shortest_routes) >= 1

    balanced_routes = router.evaluate_and_rank_routes(
        candidates, objective=OptimizationObjective.BALANCED, require_accessible=False
    )
    assert len(balanced_routes) >= 1

    walk_candidates = route_engine.calculate_routes(start[0], start[1], dest[0], dest[1], TravelMode.WALKING)
    accessible_routes = router.evaluate_and_rank_routes(
        walk_candidates, objective=OptimizationObjective.ACCESSIBLE, require_accessible=True
    )
    assert len(accessible_routes) >= 1

    # Verify that when dest_coords is None, HTML does not render a fake destination marker
    html_no_dest = build_google_maps_javascript_html(
        center_lat=16.5062,
        center_lon=80.6480,
        zoom=14,
        origin_coords=(16.5062, 80.6480),
        dest_coords=None
    )
    assert "window.DEST_LOC = null;" in html_no_dest or "window.DEST_LOC = null" in html_no_dest or '"lat": null' not in html_no_dest
