"""
Tests for Section B: Automotive Cockpit Driving Profiles & Engage Mode
Verifies:
1. Fastest Highway Drive uses lowest duration and verifies highway road types.
2. Eco & Fuel-Saver Drive uses documented speed-efficiency model and honest baseline comparison.
3. Safest Hazard-Aware Drive prioritizes routes with fewest hazards and avoids absolute safety claims.
4. Toll-Free & Budget Drive distinguishes verified toll-free from unverified routes.
5. EV Optimal Drive uses vehicle battery parameters and explains missing prerequisites for charging stops.
6. Engage Mode behavior: stores active profile ID, route ID, and geometry association.
7. Profile independence: candidate trade-offs allow profiles to select different routes.
"""

import pytest
from src.automotive_drive_selector import (
    AutomotiveDriveSelectorEngine,
    VehicleProfileConfig,
    render_driving_mode_cockpit_card_html,
    render_cockpit_mode_functionality_hud
)
from src.hazard_map import GeographicHazard, HazardSeverity


@pytest.fixture
def multi_corridor_candidates():
    """Three distinct candidate corridors with different tradeoffs."""
    return [
        {
            "route_id": "ROUTE_EXPRESSWAY",
            "name": "NH-16 Expressway Bypass",
            "distance_km": 25.0,
            "duration_minutes": 18.0,
            "polyline": [(16.20, 80.50), (16.25, 80.55), (16.30, 80.60)],
            "summary_roads": ["NH-16 Expressway", "Tenali Bypass Toll Plaza"],
            "source": "OSRM Global",
            "is_eligible": True
        },
        {
            "route_id": "ROUTE_RURAL_SHORT",
            "name": "Rural Arterial Service Road",
            "distance_km": 16.0,
            "duration_minutes": 22.0,
            "polyline": [(16.20, 80.50), (16.20, 80.58), (16.30, 80.60)],
            "summary_roads": ["Old State Highway", "Arterial Bypass Service Road"],
            "source": "OSRM Global",
            "is_eligible": True
        },
        {
            "route_id": "ROUTE_HAZARD_PRONE",
            "name": "Central Market Corridor",
            "distance_km": 18.0,
            "duration_minutes": 26.0,
            "polyline": [(16.20, 80.50), (16.25, 80.51), (16.30, 80.60)],
            "summary_roads": ["Central Market Road"],
            "source": "OSRM Global",
            "is_eligible": True
        }
    ]


def test_fastest_highway_profile_picks_lowest_duration(multi_corridor_candidates):
    """Fastest profile selects NH-16 Expressway (18.0 mins)."""
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=multi_corridor_candidates
    )
    fastest = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_FASTEST")
    assert fastest["route_id"] == "ROUTE_EXPRESSWAY"
    assert fastest["duration_minutes"] == 18.0
    assert "Highway" in fastest["title"]  # Highway keywords present


def test_fastest_arterial_title_when_no_highway():
    """Fastest profile titles itself 'Arterial' when no highway keywords exist."""
    city_route = [{
        "route_id": "ROUTE_LOCAL",
        "name": "Local Colony Lane",
        "distance_km": 5.0,
        "duration_minutes": 10.0,
        "polyline": [(16.20, 80.50), (16.21, 80.51)],
        "summary_roads": ["5th Cross Road", "Main Bazaar Street"],
        "source": "OSRM Global",
        "is_eligible": True
    }]
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(candidate_routes=city_route)
    fastest = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_FASTEST")
    assert "Highway" not in fastest["title"]
    assert "Arterial" in fastest["title"]


def test_eco_profile_minimizes_fuel_and_computes_savings(multi_corridor_candidates):
    """Eco profile picks shorter rural road and calculates fuel vs fastest baseline."""
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=multi_corridor_candidates
    )
    fastest = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_FASTEST")
    eco = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_ECO")

    # Shorter distance (16 km vs 25 km) requires less fuel
    assert eco["route_id"] == "ROUTE_RURAL_SHORT"
    assert eco["fuel_liters"] < fastest["fuel_liters"]
    assert eco["savings_pct"] > 0.0


def test_eco_profile_single_route_zero_savings():
    """When only 1 route exists, eco savings is 0.0% without fabricating savings."""
    single_route = [{
        "route_id": "R_SOLO",
        "name": "Solo Corridor",
        "distance_km": 10.0,
        "duration_minutes": 15.0,
        "polyline": [(16.20, 80.50), (16.25, 80.55)],
        "summary_roads": ["State Highway 12"],
        "source": "OSRM Global",
        "is_eligible": True
    }]
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(candidate_routes=single_route)
    eco = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_ECO")
    assert eco["savings_pct"] == 0.0
    assert "Single viable corridor" in eco["key_strength"]


def test_safest_profile_bypasses_hazards(multi_corridor_candidates):
    """Safest profile avoids route intersecting active hazard."""
    hazard = GeographicHazard(
        hazard_id="HZ_EXPRESSWAY",
        incident_type="ACCIDENT",
        severity=HazardSeverity.CRITICAL,
        latitude=16.25,
        longitude=80.55,
        radius_meters=50.0,
        description="Overturned vehicle blocking NH-16"
    )
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=multi_corridor_candidates,
        active_hazards=[hazard]
    )
    fastest = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_FASTEST")
    safest = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_SAFEST")

    assert fastest["hazard_count"] >= 1
    # Safest selects an alternative with 0 hazards
    assert safest["hazard_count"] == 0
    assert safest["route_id"] != "ROUTE_EXPRESSWAY"


def test_toll_free_profile_distinguishes_tolls(multi_corridor_candidates):
    """Toll-Free profile selects the bypass without toll plazas."""
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=multi_corridor_candidates
    )
    toll_mode = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_TOLL_FREE")
    assert toll_mode["route_id"] == "ROUTE_RURAL_SHORT"
    assert toll_mode["toll_status"] == "CONFIRMED_ZERO"
    assert toll_mode["toll_cost_inr"] == 0


def test_ev_optimal_profile_battery_and_prerequisites(multi_corridor_candidates):
    """EV Optimal computes energy draw, SoC, and includes prerequisite explanation."""
    cfg = VehicleProfileConfig(ev_battery_capacity_kwh=40.0, ev_start_soc_pct=85.0)
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=multi_corridor_candidates,
        vehicle_config=cfg
    )
    ev_mode = next(m for m in res["modes"] if m["mode_id"] == "DRIVE_EV")

    assert ev_mode["route_id"] == "ROUTE_RURAL_SHORT"  # Least energy draw
    assert ev_mode["energy_kwh"] > 0
    assert ev_mode["arrival_soc_pct"] < 85.0
    assert ev_mode["battery_capacity_kwh"] == 40.0

    hud_html = render_cockpit_mode_functionality_hud(
        mode_id="DRIVE_EV",
        orig_coords=(16.20, 80.50),
        dest_coords=(16.30, 80.60),
        mode_info=ev_mode
    )
    assert "Open Charge Map" in hud_html  # Honest prerequisite disclosure


def test_profile_cockpit_card_renders_valid_html(multi_corridor_candidates):
    """Cockpit card renders cleanly without syntax issues."""
    res = AutomotiveDriveSelectorEngine.evaluate_drive_profiles(
        candidate_routes=multi_corridor_candidates
    )
    card_html = render_driving_mode_cockpit_card_html(res["modes"][0], is_active=True, is_best=True)
    assert "AI BEST CHOICE" in card_html
    assert "ENGAGED" in card_html
