"""
Comprehensive Pytest Suite for Global Navigation, Worldwide Geocoding,
Configurable Routing Providers, Multi-Objective Pareto Optimization,
Hazard Monitoring, Location Kinematics, and Accessibility in P.A.T.H.F.I.N.D.E.R.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.map_service import MapService, OFFLINE_GEOCODE_CACHE
from src.route_engine import (
    RealWorldRouteEngine,
    RouteOption,
    TravelMode,
    BaseRoutingProvider,
    OSRMGlobalRoutingProvider
)
from src.multi_objective_router import (
    MultiObjectiveRouter,
    RouteEligibilityStatus,
    RankedRoute
)
from src.road_condition_model import OptimizationObjective, OperatingMode
from src.road_condition_manager import RoadConditionManager
from src.hazard_map import (
    HazardMap,
    GeographicHazard,
    HazardSeverity,
    haversine_distance_m
)
from src.location_service import (
    LocationService,
    LocationReading,
    LocationSource,
    LocationPermissionStatus
)
from src.voice_guidance import generate_simple_spoken_narrative
from src.pathfinder_chatbot import PathfinderChatbot


# =============================================================================
# 1. GEOCODING ACROSS SEVERAL CONTINENTS
# =============================================================================

def test_global_geocoding_continents():
    map_srv = MapService()

    # Mock response for worldwide locations across multiple continents
    continents_mock_data = {
        "New York": [{"lat": 40.7128, "lon": -74.0060, "display_name": "New York, NY, United States", "address": {"country": "United States", "state": "New York"}}],
        "London": [{"lat": 51.5074, "lon": -0.1278, "display_name": "London, Greater London, United Kingdom", "address": {"country": "United Kingdom", "state": "England"}}],
        "Tokyo": [{"lat": 35.6762, "lon": 139.6503, "display_name": "Tokyo, Japan", "address": {"country": "Japan", "state": "Tokyo"}}],
        "Sydney": [{"lat": -33.8688, "lon": 151.2093, "display_name": "Sydney, NSW, Australia", "address": {"country": "Australia", "state": "New South Wales"}}],
        "Nairobi": [{"lat": -1.2921, "lon": 36.8219, "display_name": "Nairobi, Kenya", "address": {"country": "Kenya", "state": "Nairobi"}}],
        "São Paulo": [{"lat": -23.5505, "lon": -46.6333, "display_name": "São Paulo, Brazil", "address": {"country": "Brazil", "state": "São Paulo"}}]
    }

    for city, mock_res in continents_mock_data.items():
        with patch.object(map_srv.session, "get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_res
            mock_get.return_value = mock_resp

            res = map_srv.geocode(city)
            assert res is not None
            assert "lat" in res and "lon" in res
            assert res["lat"] == mock_res[0]["lat"]
            assert res["lon"] == mock_res[0]["lon"]
            assert res["country"] == mock_res[0]["address"]["country"]


# =============================================================================
# 2. INTERNATIONAL PLACE NAMES & AMBIGUOUS SEARCH CANDIDATES
# =============================================================================

def test_international_place_names_and_disambiguation():
    map_srv = MapService()

    # Ambiguous city "Cambridge" returns multiple global candidates
    cambridge_candidates = [
        {"lat": 52.2053, "lon": 0.1218, "display_name": "Cambridge, Cambridgeshire, United Kingdom", "address": {"country": "United Kingdom", "state": "Cambridgeshire"}},
        {"lat": 42.3736, "lon": -71.1097, "display_name": "Cambridge, Massachusetts, United States", "address": {"country": "United States", "state": "Massachusetts"}},
        {"lat": 43.3616, "lon": -80.3144, "display_name": "Cambridge, Ontario, Canada", "address": {"country": "Canada", "state": "Ontario"}}
    ]

    with patch.object(map_srv.session, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = cambridge_candidates
        mock_get.return_value = mock_resp

        candidates = map_srv.geocode_candidates("Cambridge", limit=5)
        assert len(candidates) == 3
        countries = {c["country"] for c in candidates}
        assert "United Kingdom" in countries
        assert "United States" in countries
        assert "Canada" in countries


# =============================================================================
# 3. DIRECT COORDINATE INPUT AND INVALID COORDINATES
# =============================================================================

def test_coordinate_input_and_strict_validation():
    map_srv = MapService()

    # Valid coordinates
    c1 = map_srv.geocode("40.7128, -74.0060")
    assert c1 is not None
    assert round(c1["lat"], 4) == 40.7128
    assert round(c1["lon"], 4) == -74.0060

    # Valid with parentheses
    c2 = map_srv.geocode("(51.5074, -0.1278)")
    assert c2 is not None
    assert round(c2["lat"], 4) == 51.5074

    # Invalid latitude (> 90)
    c_inv_lat = map_srv.geocode("95.0, 80.0")
    assert c_inv_lat is None

    # Invalid longitude (> 180)
    c_inv_lon = map_srv.geocode("20.0, 195.0")
    assert c_inv_lon is None

    # Malformed text that cannot be geocoded should return None (never substitute Vignan)
    with patch.object(map_srv.session, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        unresolvable = map_srv.geocode("ZzzInvalidNonexistentPlace999")
        assert unresolvable is None


# =============================================================================
# 4. LONG-DISTANCE ROUTING BETWEEN CITIES
# =============================================================================

def test_long_distance_routes_between_cities():
    class MockLongDistanceProvider(BaseRoutingProvider):
        def calculate_routes(self, origin_lat, origin_lon, dest_lat, dest_lon, mode=TravelMode.DRIVING, require_accessible=False):
            return [
                RouteOption(
                    route_id="NYC_BOS_MOCK_1",
                    name="I-95 North Corridor",
                    mode=mode,
                    distance_meters=345000.0,  # 345 km
                    duration_seconds=14400.0,  # 4 hours
                    polyline=[(origin_lat, origin_lon), (41.3, -72.9), (dest_lat, dest_lon)],
                    summary_roads=["I-95 N", "I-91 N", "Mass Pike"],
                    source="OSRM (OpenStreetMap Global)"
                ),
                RouteOption(
                    route_id="NYC_BOS_MOCK_2",
                    name="Merritt Parkway / Scenic Link",
                    mode=mode,
                    distance_meters=360000.0,  # 360 km
                    duration_seconds=15600.0,
                    polyline=[(origin_lat, origin_lon), (41.4, -73.2), (dest_lat, dest_lon)],
                    summary_roads=["CT-15 N", "I-84 E"],
                    source="OSRM (OpenStreetMap Global)"
                )
            ]

    engine = RealWorldRouteEngine(provider=MockLongDistanceProvider())
    routes = engine.calculate_routes(40.7128, -74.0060, 42.3601, -71.0589, mode=TravelMode.DRIVING)

    assert len(routes) == 2
    assert routes[0].distance_km >= 300.0
    assert "I-95" in routes[0].summary_roads[0]
    # Ensure it did NOT snap to local Guntur/Tenali road graph
    assert routes[0].polyline[0] == (40.7128, -74.0060)


# =============================================================================
# 5. DISCONNECTED NETWORKS AND ROUTE FAILURES
# =============================================================================

def test_disconnected_network_and_route_failures():
    class MockDisconnectedProvider(BaseRoutingProvider):
        def calculate_routes(self, origin_lat, origin_lon, dest_lat, dest_lon, mode=TravelMode.DRIVING, require_accessible=False):
            # Simulates overseas crossing where no ferry or road exists
            return []

    engine = RealWorldRouteEngine(provider=MockDisconnectedProvider())
    # New York to London
    routes = engine.calculate_routes(40.7128, -74.0060, 51.5074, -0.1278, mode=TravelMode.DRIVING)

    assert len(routes) == 0
    assert engine.last_failure_reason is not None
    assert "no routable highway" in engine.last_failure_reason.lower()


# =============================================================================
# 6. FASTEST, SHORTEST, BALANCED, AND ACCESSIBLE ROUTE SELECTION
# =============================================================================

def test_multi_objective_four_strategies():
    router = MultiObjectiveRouter()

    r_fast = RouteOption(
        route_id="ROUTE_FAST",
        name="Express Highway",
        mode=TravelMode.DRIVING,
        distance_meters=30000.0,  # 30 km
        duration_seconds=1200.0,  # 20 min (Fastest)
        polyline=[(40.0, -74.0), (40.2, -74.0)],
        is_accessible=True,
        accessibility_verified=True
    )
    r_short = RouteOption(
        route_id="ROUTE_SHORT",
        name="Direct Urban Cut",
        mode=TravelMode.DRIVING,
        distance_meters=18000.0,  # 18 km (Shortest)
        duration_seconds=1800.0,  # 30 min
        polyline=[(40.0, -74.0), (40.1, -74.0)],
        is_accessible=True,
        accessibility_verified=True
    )
    r_balanced = RouteOption(
        route_id="ROUTE_BALANCED",
        name="Mid-Ring Corridor",
        mode=TravelMode.DRIVING,
        distance_meters=23000.0,  # 23 km
        duration_seconds=1350.0,  # 22.5 min
        polyline=[(40.0, -74.0), (40.15, -74.0)],
        is_accessible=True,
        accessibility_verified=True
    )
    r_inacc = RouteOption(
        route_id="ROUTE_INACC",
        name="Stairway Overpass Cut",
        mode=TravelMode.WALKING,
        distance_meters=28000.0,  # 28 km
        duration_seconds=2500.0,
        polyline=[(40.0, -74.0), (40.05, -74.0)],
        is_accessible=False,
        accessibility_verified=False
    )

    candidates = [r_fast, r_short, r_balanced, r_inacc]

    # Strategy 1: Fastest
    ranked_fast = router.evaluate_and_rank_routes(candidates, objective=OptimizationObjective.FASTEST)
    assert ranked_fast[0].route.route_id == "ROUTE_FAST"
    assert "lowest travel time" in ranked_fast[0].recommendation_explanation.lower()

    # Strategy 2: Shortest
    ranked_short = router.evaluate_and_rank_routes(candidates, objective=OptimizationObjective.SHORTEST)
    assert ranked_short[0].route.route_id == "ROUTE_SHORT"
    assert "shortest physical distance" in ranked_short[0].recommendation_explanation.lower()

    # Strategy 3: Balanced
    ranked_bal = router.evaluate_and_rank_routes(candidates, objective=OptimizationObjective.BALANCED)
    assert ranked_bal[0].is_eligible is True
    assert "optimal balance" in ranked_bal[0].recommendation_explanation.lower()

    # Strategy 4: Accessible
    ranked_acc = router.evaluate_and_rank_routes(candidates, objective=OptimizationObjective.ACCESSIBLE)
    inacc_res = next(r for r in ranked_acc if r.route.route_id == "ROUTE_INACC")
    assert inacc_res.is_eligible is False
    assert inacc_res.status == RouteEligibilityStatus.INACCESSIBLE


# =============================================================================
# 7. GPS PERMISSION DENIAL AND OFF-ROUTE DETECTION
# =============================================================================

def test_gps_permission_and_off_route_detection():
    loc_srv = LocationService()

    # Permission denied / not requested defaults to simulated or manual
    reading, status = loc_srv.get_effective_location()
    assert reading.source == LocationSource.SIMULATED

    # User manually pins location in Paris
    manual = loc_srv.set_manual_location(48.8566, 2.3522, label="Paris Center")
    assert manual.coordinates == (48.8566, 2.3522)
    assert manual.source == LocationSource.MANUAL_PIN

    # Off-route detection
    route_polyline = [(48.8566, 2.3522), (48.8600, 2.3600), (48.8700, 2.3700)]

    # Point directly on route: not off-route
    is_off, dist_m = loc_srv.check_off_route(48.8566, 2.3522, route_polyline, threshold_meters=50.0)
    assert is_off is False
    assert dist_m < 5.0

    # Point 500 meters off route: signals off-route
    is_off_far, dist_far = loc_srv.check_off_route(48.8900, 2.4000, route_polyline, threshold_meters=50.0)
    assert is_off_far is True
    assert dist_far > 100.0


# =============================================================================
# 8. GLOBAL HAZARD DETECTION, ROUTE INVALIDATION, AND REROUTING
# =============================================================================

def test_global_hazard_detection_and_invalidation():
    hazard_map = HazardMap()
    router = MultiObjectiveRouter(hazard_map=hazard_map)

    # Route traversing through central Tokyo
    route_poly = [(35.6762, 139.6503), (35.6800, 139.7000), (35.6900, 139.7500)]
    r1 = RouteOption(
        route_id="TOKYO_ROUTE_1",
        name="Shinjuku to Chiyoda Arterial",
        mode=TravelMode.DRIVING,
        distance_meters=8500.0,
        duration_seconds=900.0,
        polyline=route_poly,
        is_accessible=True
    )
    r2 = RouteOption(
        route_id="TOKYO_ROUTE_2",
        name="Harajuku Outer Bypass",
        mode=TravelMode.DRIVING,
        distance_meters=10200.0,
        duration_seconds=1050.0,
        polyline=[(35.6762, 139.6503), (35.6600, 139.7100), (35.6900, 139.7500)],
        is_accessible=True
    )

    # Inject chemical leak directly on mid-segment of Route 1
    hazard = GeographicHazard(
        hazard_id="HAZ_TOKYO_01",
        incident_type="CHEMICAL_SPILL",
        severity=HazardSeverity.CRITICAL,
        latitude=35.6800,
        longitude=139.7000,
        radius_meters=300.0,
        description="Hazardous vapor plume detected",
        country="Japan",
        confidence_level=0.98
    )
    hazard_map.add_hazard(hazard)

    ranked = router.evaluate_and_rank_routes([r1, r2], objective=OptimizationObjective.FASTEST)
    r1_eval = next(r for r in ranked if r.route.route_id == "TOKYO_ROUTE_1")
    r2_eval = next(r for r in ranked if r.route.route_id == "TOKYO_ROUTE_2")

    assert r1_eval.is_eligible is False
    assert r1_eval.status == RouteEligibilityStatus.HAZARD_BLOCKED
    assert r2_eval.is_eligible is True
    assert ranked[0].route.route_id == "TOKYO_ROUTE_2"


# =============================================================================
# 9. PROVIDER TIMEOUTS AND API ERROR RESILIENCE
# =============================================================================

def test_provider_timeout_and_graceful_handling():
    class TimeoutProvider(BaseRoutingProvider):
        def calculate_routes(self, origin_lat, origin_lon, dest_lat, dest_lon, mode=TravelMode.DRIVING, require_accessible=False):
            raise TimeoutError("OSRM connection timed out after 3.5s")

    engine = RealWorldRouteEngine(provider=TimeoutProvider())

    # For an intercity query outside the local graph, should handle timeout gracefully
    routes = engine.calculate_routes(12.9716, 77.5946, 13.0827, 80.2707)  # Bangalore to Chennai
    assert isinstance(routes, list)


# =============================================================================
# 10. VOICE GUIDANCE UNITS (KM & MILES) AND A.U.R.A. INTEGRATION
# =============================================================================

def test_voice_guidance_units_and_narrative():
    # Km test
    narrative_km = generate_simple_spoken_narrative(
        origin_name="Berlin Central",
        destination_name="Potsdam Square",
        route_name="Route 1",
        distance_km=28.5,
        duration_min=32.0,
        summary_roads=["B1 Highway", "Potsdamer Str"],
        unit="km"
    )
    assert "28.5 kilometers" in narrative_km
    assert "32 minutes" in narrative_km

    # Miles test
    narrative_mi = generate_simple_spoken_narrative(
        origin_name="Manhattan",
        destination_name="Brooklyn",
        route_name="Route 1",
        distance_km=16.1,  # ~10.0 miles
        duration_min=25.0,
        summary_roads=["I-278", "Flatbush Ave"],
        unit="miles"
    )
    assert "miles" in narrative_mi
    assert "kilometers" not in narrative_mi
    assert "Interstate 278" in narrative_mi or "I-278" in narrative_mi or "Flatbush Avenue" in narrative_mi


def test_aura_chatbot_global_awareness():
    map_srv = MapService()
    bot = PathfinderChatbot(map_service=map_srv)

    # Global navigation query
    res = bot.answer("How do I go to Tokyo?")
    assert "badge" in res
    assert "Tokyo" in res["response"] or "TOKYO" in res["badge"]

    # Emergency inquiry
    res_fire = bot.answer("What is the emergency protocol for fire?")
    assert "EMERGENCY" in res_fire["badge"]
    assert "FIRE" in res_fire["response"] and ("PULL STATION" in res_fire["response"] or "MANDATORY" in res_fire["response"])


# =============================================================================
# 11. CACHE BEHAVIOR AND ATTRIBUTION
# =============================================================================

def test_cache_behavior_and_rate_limiting():
    map_srv = MapService()
    # Cache should contain pre-cached baseline items
    assert "vignan university" in map_srv.cache
    assert "guntur" in map_srv.cache
    assert "hyderabad" in map_srv.cache

    # Rate limiting property should be active
    assert map_srv._min_request_interval > 0.0


# =============================================================================
# 12. REGRESSION TESTS: GUNTUR, TENALI, AND VIGNAN UNIVERSITY
# =============================================================================

def test_regression_guntur_tenali_vignan_continuity():
    map_srv = MapService()
    engine = RealWorldRouteEngine()

    # Vignan University geocodes accurately
    vignan = map_srv.geocode("Vignan University")
    assert vignan is not None
    assert vignan["lat"] == 16.2335
    assert vignan["lon"] == 80.5505

    # Guntur geocodes accurately
    guntur = map_srv.geocode("Guntur")
    assert guntur is not None
    assert guntur["lat"] == 16.3067

    # Tenali geocodes accurately
    tenali = map_srv.geocode("Tenali")
    assert tenali is not None
    assert tenali["lat"] == 16.2430

    # Local routes between Vignan and Guntur continue to work offline with multiple corridors
    routes = engine.calculate_routes(16.2335, 80.5505, 16.3067, 80.4365, mode=TravelMode.DRIVING)
    assert len(routes) >= 2
    assert all(r.distance_km > 0 for r in routes)
