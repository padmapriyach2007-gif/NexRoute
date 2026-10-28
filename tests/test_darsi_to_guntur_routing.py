"""
Comprehensive verification test for Smart Location Selection & Accurate Multi-Route Recommendations.
Scenario:
- Start: Darsi Town, Andhra Pradesh, India (~15.77, 79.68)
- Destination: Guntur Junction, Andhra Pradesh, India (~16.30, 80.44)
"""

import pytest
from src.map_service import MapService
from src.route_engine import RealWorldRouteEngine, TravelMode
from src.multi_objective_router import MultiObjectiveRouter, OptimizationObjective
from src.google_maps_platform import build_google_maps_javascript_html


def test_darsi_to_guntur_geocoding():
    ms = MapService()

    # 1. Geocode Start: Darsi Town
    start_cands = ms.geocode_candidates("Darsi Town, Andhra Pradesh, India", limit=5)
    assert len(start_cands) >= 1
    best_start = start_cands[0]
    assert 15.65 <= best_start["lat"] <= 15.85, f"Start lat {best_start['lat']} not near Darsi"
    assert 79.55 <= best_start["lon"] <= 79.80, f"Start lon {best_start['lon']} not near Darsi"

    # 2. Geocode Destination: Guntur Junction
    dest_cands = ms.geocode_candidates("Guntur Junction, Andhra Pradesh, India", limit=5)
    assert len(dest_cands) >= 1
    best_dest = dest_cands[0]
    assert 16.20 <= best_dest["lat"] <= 16.40, f"Dest lat {best_dest['lat']} not near Guntur"
    assert 80.35 <= best_dest["lon"] <= 80.70, f"Dest lon {best_dest['lon']} not near Guntur"


def test_darsi_to_guntur_authentic_routes():
    engine = RealWorldRouteEngine()
    # Darsi to Guntur coordinates
    start_lat, start_lon = 15.7688, 79.6792
    dest_lat, dest_lon = 16.3067, 80.4365

    routes = engine.calculate_routes(start_lat, start_lon, dest_lat, dest_lon, mode=TravelMode.DRIVING)
    assert len(routes) >= 1, "Expected authentic road routes from OSRM"

    primary = routes[0]
    # Check realistic distance and duration along State Highways / NH544D
    assert 100.0 <= primary.distance_km <= 145.0, f"Unexpected distance: {primary.distance_km} km"
    assert 80.0 <= primary.duration_minutes <= 140.0, f"Unexpected duration: {primary.duration_minutes} min"
    assert len(primary.polyline) >= 500, "Route must contain genuine road curve coordinates"
    assert "OSRM" in primary.source or "OpenStreetMap" in primary.source


def test_multi_objective_route_classifications():
    engine = RealWorldRouteEngine()
    start_lat, start_lon = 15.7688, 79.6792
    dest_lat, dest_lon = 16.3067, 80.4365

    routes = engine.calculate_routes(start_lat, start_lon, dest_lat, dest_lon, mode=TravelMode.DRIVING)
    assert len(routes) >= 1

    router = MultiObjectiveRouter()

    # 1. FASTEST
    fastest_ranked = router.evaluate_and_rank_routes(routes, objective=OptimizationObjective.FASTEST)
    assert len(fastest_ranked) == len(routes)
    # The rank 1 route must have the lowest duration among eligible
    min_dur = min(r.effective_duration_minutes for r in fastest_ranked if r.is_eligible)
    assert fastest_ranked[0].effective_duration_minutes == min_dur

    # 2. SHORTEST
    shortest_ranked = router.evaluate_and_rank_routes(routes, objective=OptimizationObjective.SHORTEST)
    min_dist = min(r.effective_distance_km for r in shortest_ranked if r.is_eligible)
    assert shortest_ranked[0].effective_distance_km == min_dist

    # 3. BALANCED (exact normalized formula: 0.5 * T/T_max + 0.5 * D/D_max)
    balanced_ranked = router.evaluate_and_rank_routes(routes, objective=OptimizationObjective.BALANCED)
    max_t = max(r.effective_duration_minutes for r in balanced_ranked if r.is_eligible)
    max_d = max(r.effective_distance_km for r in balanced_ranked if r.is_eligible)
    expected_score = 0.5 * (balanced_ranked[0].effective_duration_minutes / max_t) + 0.5 * (balanced_ranked[0].effective_distance_km / max_d)
    assert abs(balanced_ranked[0].composite_score - expected_score) < 0.05

    # 4. ACCESSIBLE (honest disclaimer when unverified)
    accessible_ranked = router.evaluate_and_rank_routes(routes, objective=OptimizationObjective.ACCESSIBLE, require_accessible=False)
    for r in accessible_ranked:
        if not r.accessibility_verified:
            assert "Accessibility information unavailable." in r.accessibility_notes or "unverified" in r.recommendation_explanation


def test_html_compact_pointers_and_draggability():
    html = build_google_maps_javascript_html(
        center_lat=15.7688,
        center_lon=79.6792,
        zoom=14,
        origin_coords=(15.7688, 79.6792),
        origin_label="Darsi Town, Andhra Pradesh, India",
        dest_coords=(16.3067, 80.4365),
        dest_label="Guntur Junction, Andhra Pradesh, India",
        route_polyline=[(15.7688, 79.6792), (16.3067, 80.4365)],
        map_type="hybrid"
    )

    # 1. Markers are draggable
    assert "draggable: true" in html

    # 2. Dragend listener calls handleMarkerDragEnd
    assert "window.handleMarkerDragEnd" in html

    # 3. Instruction texts are concise
    assert "Tap or drag to set your start." in html
    assert "Tap or drag to set your destination." in html

    # 4. Compact pointer labels
    assert "getCompactPointerLabel" in html
    assert "max-width: 160px" in html



def test_google_satellite_and_hybrid_basemaps():
    html = build_google_maps_javascript_html(
        center_lat=15.7688,
        center_lon=79.6792,
        zoom=14,
        map_type="hybrid"
    )
    # Verify Google Hybrid tile stream
    assert "google.com/vt/lyrs=y" in html
    # Verify Google Pure Satellite tile stream
    assert "google.com/vt/lyrs=s" in html
    # Verify Hybrid basemap card
    assert "maptype-card-hybrid" in html
    assert "maptype-card-satellite" in html
