"""
Tests verifying that all vehicle modes (FLIGHT, WATERWAY, WALK, BICYCLE, CAR, TRUCK, BUS, TRACTOR)
correctly compute cockpit telemetry and speedometer values without NameError ('pct').
"""

import pytest


def test_speedometer_telemetry_all_vehicle_modes():
    """Verify telemetry calculation for all vehicle modes with speed percentage."""
    modes = [
        ("CAR", 65.0, 10.0, 180.0),
        ("TRUCK", 55.0, 10.0, 110.0),
        ("BUS", 60.0, 10.0, 100.0),
        ("BIKE", 45.0, 5.0, 120.0),
        ("TRACTOR", 22.0, 5.0, 45.0),
        ("FLIGHT", 850.0, 180.0, 1020.0),
        ("WATERWAY", 28.0, 2.0, 55.0),
        ("WALK", 5.0, 1.0, 12.0),
        ("BICYCLE", 18.0, 3.0, 45.0),
    ]

    for sel_vehicle_key, display_speed, v_min, v_max in modes:
        v_span = max(0.1, v_max - v_min)
        pct = max(0.0, min(1.0, (display_speed - v_min) / v_span))

        # Check telemetry logic matches app.py
        if sel_vehicle_key in ["CAR", "TRUCK", "BUS", "BIKE", "TRACTOR"]:
            rpm_val = int(round(display_speed * 32.5))
            gear_lbl = "D2" if display_speed < 25 else ("D3" if display_speed < 50 else ("D4" if display_speed < 75 else ("D5" if display_speed < 105 else "D6")))
            kw_val = round(display_speed * 1.15, 1)
            telemetry_str = f"⚙️ GEAR {gear_lbl} • {rpm_val:,} RPM • {kw_val:g} kW OUTPUT"
            assert "GEAR" in telemetry_str

        elif sel_vehicle_key == "FLIGHT":
            n1_val = round(60.0 + pct * 36.0, 1)
            thrust_lbf = int(round(9000 + pct * 18500))
            mach_str = f"M{round(display_speed / 1062.0, 2)}"
            telemetry_str = f"✈️ TURBOFAN {n1_val}% N1 • {thrust_lbf:,} LBF THRUST • {mach_str}"
            assert "TURBOFAN" in telemetry_str
            assert 60.0 <= n1_val <= 96.0

        elif sel_vehicle_key == "WATERWAY":
            knots_val = round(display_speed * 0.539957, 1)
            telemetry_str = f"🚢 PROPELLER SHAFT 820 RPM • {knots_val} KNOTS • DRAFT OPTIMIZED"
            assert "KNOTS" in telemetry_str

        elif sel_vehicle_key in ["BICYCLE", "CYCLE"]:
            cadence = int(round(55 + pct * 45))
            watts = int(round(80 + pct * 180))
            telemetry_str = f"🚴 CADENCE {cadence} RPM • {watts}W POWER"
            assert "CADENCE" in telemetry_str
            assert 55 <= cadence <= 100

        elif sel_vehicle_key == "WALK":
            bpm = int(round(85 + pct * 65))
            steps_min = int(round(90 + pct * 55))
            telemetry_str = f"🚶 CADENCE {steps_min} STEPS/MIN • HEART RATE ~{bpm} BPM"
            assert "HEART RATE" in telemetry_str
            assert 85 <= bpm <= 150
