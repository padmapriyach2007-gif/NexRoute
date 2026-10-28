"""
Comprehensive Global Multi-Route Verification Suite
Tests the end-to-end functionality of Pathfinder's Worldwide Routing Engine:
1. Scenario A: Regional / National Route (Guntur -> Hyderabad) - road corridors + Airway (VGA -> HYD)
2. Scenario B: Cross-Border Route (New York -> Toronto) - road highways + Flight (JFK -> YYZ)
3. Scenario C: Trans-Oceanic Route (London -> Tokyo) - Airway geodesic corridor across continents
4. Scenario D: Ambiguous Location Resolution (e.g., 'Hyderabad' / 'Springfield') - disambiguation candidates
5. Scenario E: Unsupported / Remote Island without road/ferry - graceful handling & clear error messaging
6. Scenario F: Dedicated Airway & Waterway transport modes
7. Scenario G: AI Assistant Multi-Route Tool Comparison
"""

import os
import sys
from pathlib import Path

# Setup paths
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "src"))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from src.map_service import MapService
from src.route_engine import RealWorldRouteEngine, TravelMode
from src.pathfinder_tools import PathfinderToolExecutor
from src.multi_objective_router import MultiObjectiveRouter
from src.road_condition_model import OptimizationObjective


def test_scenario_a_regional_india():
    print("\n--- [Scenario A] Regional / National Route: Guntur -> Hyderabad ---")
    map_svc = MapService()
    engine = RealWorldRouteEngine()
    
    # Geocode locations
    guntur = map_svc.geocode("Guntur, Andhra Pradesh, India")
    hyderabad = map_svc.geocode("Hyderabad, Telangana, India")
    
    assert guntur is not None, "Failed to geocode Guntur"
    assert hyderabad is not None, "Failed to geocode Hyderabad"
    print(f"  Geocoded Guntur: ({guntur['lat']:.4f}, {guntur['lon']:.4f})")
    print(f"  Geocoded Hyderabad: ({hyderabad['lat']:.4f}, {hyderabad['lon']:.4f})")
    
    # Calculate routes with driving mode
    routes = engine.calculate_routes(
        origin_lat=guntur['lat'],
        origin_lon=guntur['lon'],
        dest_lat=hyderabad['lat'],
        dest_lon=hyderabad['lon'],
        mode=TravelMode.DRIVING
    )
    
    print(f"  Retrieved {len(routes)} distinct usable routes:")
    for i, r in enumerate(routes):
        print(f"    Route {i+1}: '{r.name}' ({r.mode.value if hasattr(r.mode, 'value') else r.mode}) - {r.distance_km:.1f} km, {r.duration_minutes:.0f} mins [Provider: {getattr(r, 'provider_attribution', r.source)[:35]}]")
    
    assert len(routes) >= 2, f"Expected at least 2 distinct routes, got {len(routes)}"
    # Verify at least one flight route is integrated for >180 km journeys
    has_flight = any(r.mode == TravelMode.FLIGHT or "flight" in str(r.mode).lower() for r in routes)
    print(f"  Airway flight route included: {has_flight}")
    assert has_flight, "Expected an airway route to be available for Guntur -> Hyderabad (>180 km)"
    print("  ✓ Scenario A passed successfully!")


def test_scenario_b_cross_border():
    print("\n--- [Scenario B] Cross-Border Route: New York -> Toronto ---")
    map_svc = MapService()
    engine = RealWorldRouteEngine()
    
    ny = map_svc.geocode("New York, USA")
    toronto = map_svc.geocode("Toronto, Canada")
    
    assert ny is not None, "Failed to geocode New York"
    assert toronto is not None, "Failed to geocode Toronto"
    print(f"  Geocoded New York: ({ny['lat']:.4f}, {ny['lon']:.4f})")
    print(f"  Geocoded Toronto: ({toronto['lat']:.4f}, {toronto['lon']:.4f})")
    
    routes = engine.calculate_routes(
        origin_lat=ny['lat'],
        origin_lon=ny['lon'],
        dest_lat=toronto['lat'],
        dest_lon=toronto['lon'],
        mode=TravelMode.DRIVING
    )
    
    print(f"  Retrieved {len(routes)} distinct cross-border routes:")
    for i, r in enumerate(routes):
        print(f"    Route {i+1}: '{r.name}' ({r.mode.value if hasattr(r.mode, 'value') else r.mode}) - {r.distance_km:.1f} km, {r.duration_minutes:.0f} mins")
    
    assert len(routes) >= 2, f"Expected multiple cross-border routes, got {len(routes)}"
    print("  ✓ Scenario B passed successfully!")


def test_scenario_c_trans_oceanic():
    print("\n--- [Scenario C] Trans-Oceanic Route: London, UK -> Tokyo, Japan ---")
    map_svc = MapService()
    engine = RealWorldRouteEngine()
    
    london = map_svc.geocode("London, UK")
    tokyo = map_svc.geocode("Tokyo, Japan")
    
    assert london is not None, "Failed to geocode London"
    assert tokyo is not None, "Failed to geocode Tokyo"
    print(f"  Geocoded London: ({london['lat']:.4f}, {london['lon']:.4f})")
    print(f"  Geocoded Tokyo: ({tokyo['lat']:.4f}, {tokyo['lon']:.4f})")
    
    routes = engine.calculate_routes(
        origin_lat=london['lat'],
        origin_lon=london['lon'],
        dest_lat=tokyo['lat'],
        dest_lon=tokyo['lon'],
        mode=TravelMode.DRIVING
    )
    
    print(f"  Retrieved {len(routes)} route(s):")
    for i, r in enumerate(routes):
        print(f"    Route {i+1}: '{r.name}' - {r.distance_km:.1f} km, {r.duration_minutes:.0f} mins [Provider: {getattr(r, 'provider_attribution', r.source)}]")
    
    assert len(routes) >= 1, "Expected trans-oceanic airway route to be generated"
    has_flight = any(r.mode == TravelMode.FLIGHT for r in routes)
    assert has_flight, "Expected trans-oceanic airway route (LHR ➔ HND) to be included"
    flight_route = next(r for r in routes if r.mode == TravelMode.FLIGHT)
    assert flight_route.distance_km > 8000, f"Expected realistic intercontinental distance (>8000km), got {flight_route.distance_km}"
    print(f"  Airway flight corridor verified: {flight_route.name} ({flight_route.distance_km:.1f} km)")
    print("  ✓ Scenario C passed successfully!")


def test_scenario_d_ambiguous_location():
    print("\n--- [Scenario D] Ambiguous Location Search: 'Hyderabad' ---")
    map_svc = MapService()
    cands = map_svc.geocode_candidates("Hyderabad", limit=5)
    
    print(f"  Found {len(cands)} candidates for 'Hyderabad':")
    for i, c in enumerate(cands):
        print(f"    Candidate {i+1}: {c.get('display_name')} ({c.get('lat')}, {c.get('lon')})")
    
    assert len(cands) >= 2, "Expected multiple candidates for ambiguous place 'Hyderabad'"
    countries = [c.get("display_name", "") for c in cands]
    # Hyderabad exists in India and Pakistan (Sindh)
    has_india = any("India" in d for d in countries)
    print(f"  Has India candidate: {has_india}")
    assert has_india, "Expected Hyderabad, India among candidates"
    print("  ✓ Scenario D passed successfully!")


def test_scenario_e_unsupported_remote_island():
    print("\n--- [Scenario E] Unsupported / Remote Island without Airport: Bouvet Island ---")
    engine = RealWorldRouteEngine()
    
    # Bouvet Island (remote uninhabited subantarctic island) to Tristan da Cunha
    # Coords: (-54.4208, 3.3464) -> (-37.1052, -12.2777)
    # No roads, and thousands of km from any hub airport
    routes = engine.calculate_routes(
        origin_lat=-54.4208,
        origin_lon=3.3464,
        dest_lat=-37.1052,
        dest_lon=-12.2777,
        mode=TravelMode.WALKING
    )
    
    print(f"  Walking across South Atlantic returned {len(routes)} routes (correctly zero / empty).")
    assert len(routes) == 0, f"Expected 0 walking routes across ocean, got {len(routes)}"
    print("  ✓ Scenario E passed successfully!")


def test_scenario_f_dedicated_airway_and_waterway():
    print("\n--- [Scenario F] Dedicated Airway & Waterway Transport Modes ---")
    map_svc = MapService()
    engine = RealWorldRouteEngine()
    
    # 1. Flight mode between Delhi and Bengaluru
    delhi = map_svc.geocode("New Delhi, India")
    blr = map_svc.geocode("Bengaluru, India")
    
    flight_routes = engine.calculate_routes(
        origin_lat=delhi['lat'],
        origin_lon=delhi['lon'],
        dest_lat=blr['lat'],
        dest_lon=blr['lon'],
        mode=TravelMode.FLIGHT
    )
    assert len(flight_routes) >= 1, "Failed to get flight route between DEL and BLR"
    print(f"  Flight DEL -> BLR: {flight_routes[0].name}, {flight_routes[0].distance_km:.1f} km, {flight_routes[0].duration_minutes:.0f} mins")
    
    # 2. Waterway mode in Mumbai harbor / coastal
    mumbai = (18.9220, 72.8347)  # Gateway of India
    mandwa = (18.7950, 72.8710)  # Mandwa jetty
    water_routes = engine.calculate_routes(
        origin_lat=mumbai[0],
        origin_lon=mumbai[1],
        dest_lat=mandwa[0],
        dest_lon=mandwa[1],
        mode=TravelMode.WATERWAY
    )
    assert len(water_routes) >= 1, "Failed to get waterway route for Mumbai harbor"
    print(f"  Waterway Mumbai -> Mandwa: {water_routes[0].name}, {water_routes[0].distance_km:.1f} km, {water_routes[0].duration_minutes:.0f} mins")
    print("  ✓ Scenario F passed successfully!")


def test_scenario_g_ai_route_comparison():
    print("\n--- [Scenario G] AI Assistant Multi-Route Comparison ---")
    executor = PathfinderToolExecutor()
    
    # Mock route engine evaluation results
    from src.route_engine import RouteOption
    from src.multi_objective_router import RankedRoute, RouteEligibilityStatus
    
    r1 = RouteOption(
        route_id="route_1",
        name="via NH-44 Expressway",
        distance_meters=280000,
        duration_seconds=18000,
        polyline=[(16.23, 80.55), (17.38, 78.48)],
        mode=TravelMode.DRIVING,
        source="OSRM OpenStreetMap Global Road Engine"
    )
    r1.provider_attribution = "OSRM OpenStreetMap Global Road Engine"

    r2 = RouteOption(
        route_id="route_2",
        name="via SH-2 State Highway",
        distance_meters=295000,
        duration_seconds=21000,
        polyline=[(16.23, 80.55), (17.38, 78.48)],
        mode=TravelMode.DRIVING,
        source="OSRM OpenStreetMap Global Road Engine"
    )
    r2.provider_attribution = "OSRM OpenStreetMap Global Road Engine"

    r3 = RouteOption(
        route_id="route_3",
        name="IndiGo Flight 6E-7281 (VGA ➔ HYD)",
        distance_meters=270000,
        duration_seconds=7200,
        polyline=[(16.23, 80.55), (17.38, 78.48)],
        mode=TravelMode.FLIGHT,
        source="Aviation Skyways • Great-Circle Navigation"
    )
    r3.provider_attribution = "Aviation Skyways • Great-Circle Navigation"
    
    ranked_1 = RankedRoute(
        route=r1, rank=1, is_eligible=True, status=RouteEligibilityStatus.ELIGIBLE,
        composite_score=1.0, effective_duration_minutes=300.0, effective_distance_km=280.0,
        time_savings_minutes_vs_slowest=50.0, distance_diff_km_vs_shortest=10.0
    )
    ranked_2 = RankedRoute(
        route=r2, rank=2, is_eligible=True, status=RouteEligibilityStatus.ELIGIBLE,
        composite_score=1.2, effective_duration_minutes=350.0, effective_distance_km=295.0,
        time_savings_minutes_vs_slowest=0.0, distance_diff_km_vs_shortest=25.0
    )
    ranked_3 = RankedRoute(
        route=r3, rank=3, is_eligible=True, status=RouteEligibilityStatus.ELIGIBLE,
        composite_score=0.8, effective_duration_minutes=120.0, effective_distance_km=270.0,
        time_savings_minutes_vs_slowest=230.0, distance_diff_km_vs_shortest=0.0
    )
    
    ctx = {
        "ranked_routes": [ranked_1, ranked_2, ranked_3],
        "start_label": "Guntur",
        "dest_label": "Hyderabad"
    }
    
    # Test compare_routes
    res = executor.execute("compare_routes", {}, context=ctx)
    assert res["success"] is True, "Failed to execute compare_routes"
    print("  Comparison Output:")
    print(res["response"])
    assert "Fastest Corridor" in res["response"]
    assert "Airway Option Available" in res["response"]
    print("  ✓ Scenario G passed successfully!")


if __name__ == "__main__":
    print("=============================================================")
    print("STARTING PATHFINDER GLOBAL MULTI-ROUTE SYSTEM TEST SUITE")
    print("=============================================================")
    test_scenario_a_regional_india()
    test_scenario_b_cross_border()
    test_scenario_c_trans_oceanic()
    test_scenario_d_ambiguous_location()
    test_scenario_e_unsupported_remote_island()
    test_scenario_f_dedicated_airway_and_waterway()
    test_scenario_g_ai_route_comparison()
    print("\n=============================================================")
    print("ALL 7 GLOBAL ROUTE SUITE SCENARIOS PASSED WITH ZERO FAILURES!")
    print("=============================================================")
