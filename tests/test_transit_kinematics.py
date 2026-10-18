import datetime
import pytest
from src.transit_kinematics import (
    calculate_transit_kinematics,
    render_transit_kinematics_hud_html,
    VEHICLE_KINEMATIC_PROFILES
)


def test_calculate_transit_kinematics_car():
    now_dt = datetime.datetime(2026, 10, 18, 9, 0, 0)
    kin = calculate_transit_kinematics(
        mode_key="CAR",
        distance_km=150.0,
        departure_offset_minutes=0,
        now_dt=now_dt
    )
    assert kin.mode_key == "CAR"
    assert kin.speed_kmh == 75.0
    assert kin.duration_minutes == 120.0
    assert kin.duration_formatted == "2h 0m"
    assert kin.departure_time_str == "09:00 AM"
    assert kin.eta_time_str == "11:00 AM"
    assert kin.eta_day_offset_str == ""


def test_calculate_transit_kinematics_modes_speed_accuracy():
    dist_km = 60.0
    # Bike at 60 km/h = 1 hour = 60 mins
    bike_kin = calculate_transit_kinematics("BIKE", dist_km)
    assert bike_kin.speed_kmh == 60.0
    assert round(bike_kin.duration_minutes, 1) == 60.0

    # Tractor at 22 km/h
    trac_kin = calculate_transit_kinematics("TRACTOR", dist_km)
    assert trac_kin.speed_kmh == 22.0
    assert trac_kin.duration_minutes > 150.0

    # Walk at 4.8 km/h
    walk_kin = calculate_transit_kinematics("WALK", dist_km)
    assert walk_kin.speed_kmh == 4.8
    assert round(walk_kin.duration_minutes) == 750


def test_calculate_transit_kinematics_day_rollover():
    # 300 km walk at 4.8 km/h = 62.5 hours (> 2 days)
    now_dt = datetime.datetime(2026, 10, 18, 8, 0, 0)
    kin = calculate_transit_kinematics("WALK", 300.0, now_dt=now_dt)
    assert kin.eta_day_offset_str in ["+2 days", "+3 days"]
    html = render_transit_kinematics_hud_html(kin)
    assert "TRANSIT KINEMATICS" in html
    assert "Pedestrian Walkway" in html


def test_calculate_transit_kinematics_timezones():
    """Verify timezones produce accurate real-time local hours and abbreviations."""
    # Test with UTC
    kin_utc = calculate_transit_kinematics(
        mode_key="CAR",
        distance_km=75.0,
        timezone_name="UTC"
    )
    assert kin_utc.timezone_abbr == "UTC"
    assert "UTC" in kin_utc.timezone_name

    # Test with Asia/Kolkata (IST)
    kin_ist = calculate_transit_kinematics(
        mode_key="CAR",
        distance_km=75.0,
        timezone_name="Asia/Kolkata"
    )
    assert kin_ist.timezone_abbr == "IST"
    assert "India" in kin_ist.timezone_label

    # Test with New York (EST/EDT)
    kin_ny = calculate_transit_kinematics(
        mode_key="CAR",
        distance_km=75.0,
        timezone_name="America/New_York"
    )
    assert kin_ny.timezone_abbr in ["EST", "EDT"]

    # Render HTML HUD with timezone badges
    html = render_transit_kinematics_hud_html(kin_ist)
    assert "IST" in html
    assert "Live Satellite Clock" in html
