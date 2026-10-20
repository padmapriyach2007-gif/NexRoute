"""
Unit tests for Satellite Road Auditor module.
"""

import pytest
from src.satellite_road_auditor import SatelliteRoadAuditor, SatelliteAuditResult


def test_satellite_road_auditor_empty_polyline():
    auditor = SatelliteRoadAuditor(enable_live_osm=False)
    res = auditor.audit_route_corridor([])
    assert res.is_clear is True
    assert res.status == "NOMINAL_CLEAR"
    assert res.real_blockages_count == 0
    assert res.real_hazards_count == 0


def test_satellite_road_auditor_nominal_clear_route():
    auditor = SatelliteRoadAuditor(enable_live_osm=False)
    # Tenali to Vignan corridor
    polyline = [(16.241, 80.584), (16.245, 80.575), (16.233, 80.550)]
    res = auditor.audit_route_corridor(polyline)
    assert res.is_clear is True
    assert res.status == "NOMINAL_CLEAR"
    assert res.real_blockages_count == 0
    assert res.real_hazards_count == 0
    assert "clear of reported physical blockages" in res.corridor_summary.lower()


def test_distance_to_polyline():
    auditor = SatelliteRoadAuditor(enable_live_osm=False)
    # Horizontal segment along latitude 16.0 from lon 80.0 to 80.2
    polyline = [(16.0, 80.0), (16.0, 80.2)]
    # Point directly on line
    dist_on = auditor._distance_to_polyline_m((16.0, 80.1), polyline)
    assert dist_on < 1.0

    # Point 0.001 deg north (~111 meters)
    dist_off = auditor._distance_to_polyline_m((16.001, 80.1), polyline)
    assert 105.0 < dist_off < 120.0
