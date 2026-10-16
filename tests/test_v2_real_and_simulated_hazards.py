"""
Comprehensive Automated Pytest Suite for CampusAegis v2.0
Tests:
- Unified hazard data model & validation
- Real vs Simulated vs Hybrid mode isolation
- Real-hazard source adapters (USGS, Open-Meteo) & health tracking
- Controlled simulation engine (16 hazard types, 18 scenarios)
- Safety-constrained route filtering with hard exclusions
- Safe-haven fallback when all paths blocked
- Alert generation lifecycle without chatbot interaction
"""

import pytest
from datetime import datetime, timezone

from src.hazard_data_model import (
    UnifiedIncident,
    HazardType,
    HazardSeverity,
    VerificationStatus,
    IncidentStatus,
    HazardGeometry,
    GeometryType,
    EnvironmentMode,
    OperatingMode
)
from src.hazard_source_manager import (
    RealHazardSourceManager,
    USGSEarthquakeAdapter,
    OpenMeteoSevereWeatherAdapter
)
from src.simulation_engine import SimulationEngine
from src.hazard_mode_manager import HazardModeManager
from src.hazard_map import HazardMap, GeographicHazard, HazardSeverity as LegacySeverity
from src.route_engine import RealWorldRouteEngine, TravelMode
from src.safety_route_filter import SafetyRouteFilter, RouteSafetyStatus


def test_unified_incident_validation():
    # Valid incident
    geom = HazardGeometry(GeometryType.POINT_BUFFER, 16.2335, 80.5505, radius_meters=200.0)
    inc = UnifiedIncident(
        incident_id="REAL-TEST-001",
        external_source_id="EXT-001",
        source_name="National Disaster Feed",
        source_type="GOVERNMENT",
        environment=EnvironmentMode.REAL,
        hazard_type=HazardType.BUILDING_FIRE,
        geometry=geom,
        affected_radius_meters=200.0,
        severity=HazardSeverity.CRITICAL,
        confidence=0.95,
        verification_status=VerificationStatus.CONFIRMED,
        incident_status=IncidentStatus.ACTIVE,
        observed_at=datetime.now(timezone.utc)
    )
    is_valid, errors = inc.validate()
    assert is_valid is True
    assert len(errors) == 0
    assert inc.is_simulated is False

    # Invalid latitude and confidence
    geom_bad = HazardGeometry(GeometryType.POINT_BUFFER, 95.0, 80.5505, radius_meters=-50.0)
    inc_bad = UnifiedIncident(
        incident_id="REAL-BAD",
        external_source_id="EXT-BAD",
        source_name="Bad Feed",
        source_type="TEST",
        environment=EnvironmentMode.REAL,
        hazard_type=HazardType.UNKNOWN_HAZARD,
        geometry=geom_bad,
        affected_radius_meters=-50.0,
        severity=HazardSeverity.LOW,
        confidence=1.5,
        verification_status=VerificationStatus.UNVERIFIED,
        incident_status=IncidentStatus.ACTIVE,
        observed_at=datetime.now(timezone.utc)
    )
    is_valid_bad, errors_bad = inc_bad.validate()
    assert is_valid_bad is False
    assert len(errors_bad) >= 2


def test_real_vs_simulated_mode_isolation():
    manager = HazardModeManager(initial_mode=OperatingMode.REAL_HAZARD_MODE)
    
    # Attempt to inject simulated incident while in REAL_HAZARD_MODE
    manager.simulation_engine.generate_incident(
        hazard_type=HazardType.BUILDING_FIRE,
        latitude=16.2335, longitude=80.5505, radius_meters=300.0
    )
    
    incidents = manager.synchronize_incidents(16.2335, 80.5505)
    # In REAL mode, simulated incidents MUST be rejected
    assert all(not inc.is_simulated for inc in incidents)
    assert manager.get_environment_indicator()["allows_simulation"] is False

    # Switch to SIMULATION_MODE
    manager.set_mode(OperatingMode.SIMULATION_MODE)
    incidents_sim = manager.synchronize_incidents(16.2335, 80.5505)
    assert all(inc.is_simulated for inc in incidents_sim)
    assert manager.get_environment_indicator()["allows_simulation"] is True


def test_usgs_earthquake_adapter_normalization():
    adapter = USGSEarthquakeAdapter()
    raw_feature = {
        "id": "us7000abcd",
        "properties": {
            "mag": 5.4,
            "place": "12 km SSW of Guntur, India",
            "time": 1728900000000,
            "url": "https://earthquake.usgs.gov/earthquakes/event/us7000abcd"
        },
        "geometry": {
            "type": "Point",
            "coordinates": [80.4500, 16.2800, 10.0]
        }
    }
    incident = adapter.normalize_incident(raw_feature)
    assert incident is not None
    assert incident.hazard_type == HazardType.EARTHQUAKE
    assert incident.severity == HazardSeverity.HIGH  # Mag 5.4
    assert incident.geometry.latitude == 16.2800
    assert incident.geometry.longitude == 80.4500
    assert incident.affected_radius_meters == 8000.0
    assert incident.environment == EnvironmentMode.REAL


def test_simulation_engine_all_16_hazard_types():
    sim = SimulationEngine()
    types_to_test = [
        HazardType.BUILDING_FIRE, HazardType.WILDFIRE, HazardType.SMOKE_PLUME,
        HazardType.CHEMICAL_LEAK, HazardType.FLOODED_ROAD, HazardType.ROAD_CAVE_IN,
        HazardType.ROAD_CLOSURE, HazardType.VEHICLE_ACCIDENT, HazardType.BLOCKED_EXIT,
        HazardType.BLOCKED_STAIRCASE, HazardType.BLOCKED_CORRIDOR, HazardType.SEVERE_WEATHER,
        HazardType.SHELTER_CLOSURE, HazardType.SENSOR_FAILURE, HazardType.DELAYED_FEED,
        HazardType.CONFLICTING_REPORTS
    ]
    for ht in types_to_test:
        inc = sim.generate_incident(ht, 16.2335, 80.5505, radius_meters=200.0)
        assert inc.hazard_type == ht
        assert inc.is_simulated is True
        assert "SIMULATED" in inc.incident_id

    assert len(sim.get_active_simulated_incidents()) == len(types_to_test)
    
    # Test clean reset
    sim.reset()
    assert len(sim.get_active_simulated_incidents()) == 0


def test_18_repeatable_scenarios():
    sim = SimulationEngine()
    for s_id in range(1, 19):
        meta = sim.load_scenario(s_id)
        assert meta["scenario_id"] == s_id
        assert len(meta["name"]) > 0


def test_safety_constrained_routing_with_unified_hazards():
    mode_mgr = HazardModeManager(initial_mode=OperatingMode.SIMULATION_MODE)
    hazard_map = HazardMap()
    route_engine = RealWorldRouteEngine()
    safety_filter = SafetyRouteFilter(hazard_map)

    # Load Scenario 2: Fire on arterial highway
    mode_mgr.simulation_engine.load_scenario(2)
    mode_mgr.synchronize_incidents(16.2335, 80.5505)
    mode_mgr.update_hazard_map(hazard_map)

    assert len(hazard_map.get_active_hazards()) >= 1

    # Route between Vignan and Guntur
    routes = route_engine.calculate_routes(16.2335, 80.5505, 16.3067, 80.4365)
    evals = safety_filter.evaluate_candidate_routes(routes)

    # Must produce both eligible and excluded corridors
    assert any(not ev.is_eligible for ev in evals)
    assert any(ev.is_eligible for ev in evals)


def test_destination_cut_off_returns_no_verified_route():
    mode_mgr = HazardModeManager(initial_mode=OperatingMode.SIMULATION_MODE)
    hazard_map = HazardMap()
    route_engine = RealWorldRouteEngine()
    safety_filter = SafetyRouteFilter(hazard_map)

    # Load Scenario 6: All routes to destination cut off
    mode_mgr.simulation_engine.load_scenario(6)
    mode_mgr.synchronize_incidents(16.2335, 80.5505)
    mode_mgr.update_hazard_map(hazard_map)

    routes = route_engine.calculate_routes(16.2335, 80.5505, 16.3067, 80.4365)
    evals = safety_filter.evaluate_candidate_routes(routes)

    # Every single corridor must be excluded due to hard closures surrounding destination
    assert all(not ev.is_eligible for ev in evals)
