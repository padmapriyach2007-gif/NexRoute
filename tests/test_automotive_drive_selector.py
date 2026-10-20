"""
Tests for Automotive Cockpit Drive Selector & AI Strategy Engine in P.A.T.H.F.I.N.D.E.R.
Validates:
1. Distance and duration consistency across all 5 profiles.
2. Mathematically correct average speed calculations: v = d / t.
3. Documented ICE fuel and EV energy consumption models.
4. Savings percentage calculation against Fastest Highway baseline.
5. Toll cost handling: verified tolls vs confirmed zero vs unverified.
6. Hazard detection: buffer intersections, threat summaries, avoiding unverified 100% claims.
7. Profile objective ranking & candidate route association.
8. AI verdict formulation and consistency.
9. Engage Mode selection flow, route synchronization, and map highlighting logic.
10. Data-quality audit and calculation details rendering.
11. Invalid input, zero duration, and failure handling.
"""

import pytest
from src.automotive_drive_selector import (
    AutomotiveDriveSelectorEngine,
    VehicleProfileConfig,
    render_driving_mode_cockpit_card_html,
    render_cockpit_mode_functionality_hud,
    render_profile_calculation_details_html
)
from src.hazard_map import GeographicHazard, HazardSeverity
from src.road_condition_model import RoadRestriction, RestrictionType


@pytest.fixture
def candidate_routes_fixture():
    """Three genuinely distinct candidate corridors for testing."""
    return [
        {
            "route_id": "PRIMARY_ARTERIAL",
            "name": "NH-16 Express Arterial",
            "distance_km": 20.0,
            "duration_minutes": 15.0,  # Fastest: 80 km/h avg
            "polyline": [(16.2335, 80.5505), (16.2400, 80.5600), (16.2500, 80.5700)],
            "summary_roads": ["NH-16 Expressway", "National Highway Toll"],
            "source": "OSRM (OpenStreetMap Global)",
            "is_eligible": True
        },
        {
            "route_id": "ECO_SHORTER_CORRIDOR",
            "name": "State Highway 39 Eco Corridor",
            "distance_km": 16.0,
            "duration_minutes": 18.0,  # Slower but shorter & fuel-efficient: 53.3 km/h
            "polyline": [(16.2335, 80.5505), (16.2370, 80.5550), (16.2500, 80.5700)],
            "summary_roads": ["SH-39", "Service Bypass"],
            "source": "OSRM (OpenStreetMap Global)",
            "is_eligible": True
        },
        {
            "route_id": "TOLL_FREE_BYPASS",
            "name": "Rural Arterial Toll-Free Bypass",
            "distance_km": 18.5,
            "duration_minutes": 22.0,  # Confirmed zero toll
            "polyline": [(16.2335, 80.5505), (16.2310, 80.5580), (16.2500, 80.5700)],
            "summary_roads": ["Old State Arterial", "Village Bypass Road"],
            "source": "Autonomous Road Graph Model",
            "is_eligible": True
        }
    ]


# =========================================================================
# 1. Distance & Duration Consistency
# =========================================================================
def test_distance_and_duration_consistency(candidate_routes_fixture):
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=candidate_routes_fixture
    )
    modes = res["modes"]
    assert len(modes) == 5

    for m in modes:
        # Distance and duration must correspond to a valid candidate route
        assert m["distance_km"] in [20.0, 16.0, 18.5]
        assert m["duration_minutes"] in [15.0, 18.0, 22.0]
        # Distance must be positive and in kilometers
        assert m["distance_km"] > 0
        assert m["duration_minutes"] > 0


# =========================================================================
# 2. Average Speed Calculations
# =========================================================================
def test_average_speed_calculation(candidate_routes_fixture):
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=candidate_routes_fixture
    )
    for m in res["modes"]:
        # Average speed = Distance (km) / Duration (hours)
        expected_speed = round(m["distance_km"] / (m["duration_minutes"] / 60.0), 1)
        assert m["speed_avg_kmh"] == expected_speed

    # Fastest profile must reflect 20 km / 0.25 h = 80 km/h
    fastest = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_FASTEST")
    assert fastest["speed_avg_kmh"] == 80.0


# =========================================================================
# 3. Documented Fuel and EV Energy Models
# =========================================================================
def test_fuel_and_ev_energy_calculations(candidate_routes_fixture):
    config = VehicleProfileConfig(
        ice_base_liters_per_km=0.070,
        ev_base_kwh_per_km=0.150,
        ev_battery_capacity_kwh=40.0,
        ev_start_soc_pct=90.0
    )
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=candidate_routes_fixture,
        vehicle_config=config
    )
    for m in res["modes"]:
        # Fuel must be non-negative
        assert m["fuel_liters"] >= 0.0
        # EV profile must have 0.0 fuel liters
        if m["mode_id"] == "DRIVE_EV":
            assert m["fuel_liters"] == 0.0
            assert m["energy_kwh"] > 0.0
            assert m["battery_used_pct"] > 0.0
            assert m["arrival_soc_pct"] == round(90.0 - m["battery_used_pct"], 1)
        else:
            assert m["fuel_liters"] > 0.0


# =========================================================================
# 4. Savings Percentage against Fastest Baseline
# =========================================================================
def test_savings_percentage_calculation(candidate_routes_fixture):
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=candidate_routes_fixture
    )
    fastest = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_FASTEST")
    eco = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_ECO")
    ev = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_EV")

    # Baseline has 0% savings against itself
    assert fastest["savings_pct"] == 0.0

    # Eco savings formula: ((baseline_fuel - eco_fuel) / baseline_fuel) * 100
    expected_eco_savings = round(((fastest["fuel_liters"] - eco["fuel_liters"]) / fastest["fuel_liters"]) * 100.0, 1)
    assert abs(eco["savings_pct"] - expected_eco_savings) <= 0.2
    assert eco["savings_pct"] > 0.0  # Eco saves fuel

    # EV saves 100% petrol fuel
    assert ev["savings_pct"] == 100.0


# =========================================================================
# 5. Toll Cost Handling
# =========================================================================
def test_toll_cost_handling(candidate_routes_fixture):
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=candidate_routes_fixture
    )
    fastest = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_FASTEST")
    toll_free = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_TOLL_FREE")

    # Fastest uses NH-16 -> Identified toll
    assert fastest["toll_status"] == "IDENTIFIED_TOLL"
    assert fastest["toll_cost_inr"] == 85

    # Toll free route uses bypass -> Confirmed zero
    assert toll_free["toll_status"] == "CONFIRMED_ZERO"
    assert toll_free["toll_cost_inr"] == 0
    assert "₹0 FASTag toll" in toll_free["key_strength"]


# =========================================================================
# 6. Hazard Detection & Objective Ranking
# =========================================================================
def test_hazard_detection_and_safest_profile(candidate_routes_fixture):
    # Place a hazard intersecting the fastest route at (16.2400, 80.5600)
    hazard = GeographicHazard(
        hazard_id="HZ_EXPRESSWAY",
        incident_type="CONSTRUCTION",
        severity=HazardSeverity.HIGH,
        latitude=16.2400,
        longitude=80.5600,
        radius_meters=30.0,
        description="NH-16 Flyover Resurfacing & Lane Closure"
    )

    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=candidate_routes_fixture,
        active_hazards=[hazard]
    )
    fastest = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_FASTEST")
    safest = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_SAFEST")

    assert fastest["hazard_count"] >= 1
    assert "Warning" in fastest["safety_rating"]

    # Safest profile selects an alternative corridor avoiding this hazard
    assert safest["hazard_count"] == 0
    assert "Clear (0 Hazards)" in safest["safety_rating"]

    # AI Verdict must autonomously recommend Safest Drive
    assert res["best_mode_id"] == "DRIVE_SAFEST"
    assert "Safest Hazard-Aware Drive recommended" in res["best_reason"]


# =========================================================================
# 7. Route Selection & Engage Mode Synchronization
# =========================================================================
def test_engage_mode_route_association(candidate_routes_fixture):
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=candidate_routes_fixture
    )
    # Every profile must have an assigned route_id from the candidates
    valid_ids = {r["route_id"] for r in candidate_routes_fixture}
    for m in res["modes"]:
        assert m["route_id"] in valid_ids


# =========================================================================
# 8. Data-Quality Audit & Calculation Details Rendering
# =========================================================================
def test_calculation_details_rendering(candidate_routes_fixture):
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=candidate_routes_fixture
    )
    for m in res["modes"]:
        details_html = render_profile_calculation_details_html(m)
        assert "Statistical Provenance" in details_html
        assert m["route_id"] in details_html
        assert "Speed Formula" in details_html


# =========================================================================
# 9. UI Card Rendering
# =========================================================================
def test_cockpit_card_and_hud_rendering(candidate_routes_fixture):
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=candidate_routes_fixture
    )
    for m in res["modes"]:
        card_html = render_driving_mode_cockpit_card_html(m, is_active=True, is_best=m["is_best"])
        assert "SPEED PROFILE" in card_html
        assert "HAZARD STATUS" in card_html
        assert str(m["duration_minutes"]) in card_html
        assert str(m["distance_km"]) in card_html

    # Live HUD
    hud_html = render_cockpit_mode_functionality_hud(
        mode_id="DRIVE_FASTEST",
        orig_coords=(16.2335, 80.5505),
        dest_coords=(16.2500, 80.5700),
        mode_info=res["modes"][0]
    )
    assert "Fastest Highway Drive Mode Active" in hud_html


# =========================================================================
# 10. Robustness & Failure Handling (Zero Duration, Empty Routes)
# =========================================================================
def test_failure_handling_and_zero_inputs():
    # Empty candidate routes -> must gracefully fall back to default corridor
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=[],
        default_distance_km=10.0,
        default_duration_mins=12.0
    )
    assert len(res["modes"]) == 5
    assert res["best_mode_id"] in ["DRIVE_FASTEST", "DRIVE_ECO", "DRIVE_SAFEST", "DRIVE_TOLL_FREE", "DRIVE_EV"]

    # Candidate with near-zero duration -> must not divide by zero
    zero_dur_routes = [{
        "route_id": "ZERO_DUR",
        "name": "Zero Duration Corridor",
        "distance_km": 5.0,
        "duration_minutes": 0.0,
        "polyline": []
    }]
    res_zero = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=zero_dur_routes
    )
    assert len(res_zero["modes"]) == 5
    for m in res_zero["modes"]:
        assert m["speed_avg_kmh"] > 0
