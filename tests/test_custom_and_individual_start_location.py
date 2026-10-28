import pytest
import re
from src.map_service import MapService

def test_detect_user_network_location():
    # Verify that detect_user_network_location detects real device/IP coordinates
    from app import detect_user_network_location
    loc = detect_user_network_location()
    assert isinstance(loc, dict)
    assert "lat" in loc and "lon" in loc
    assert -90.0 <= loc["lat"] <= 90.0
    assert -180.0 <= loc["lon"] <= 180.0
    assert "label" in loc
    assert len(loc["label"]) > 0

def test_custom_start_location_geocoding():
    map_service = MapService()
    
    # Test city custom start
    cands_hyd = map_service.geocode_candidates("Hyderabad", limit=3)
    assert len(cands_hyd) >= 1
    assert any("hyderabad" in c.get("name", "").lower() or "hyderabad" in c.get("display_name", "").lower() for c in cands_hyd)

    # Test landmark custom start
    cands_vignan = map_service.geocode_candidates("Vignan University", limit=3)
    assert len(cands_vignan) >= 1
    assert any("vignan" in c.get("name", "").lower() or "vignan" in c.get("display_name", "").lower() for c in cands_vignan)

def test_custom_start_direct_coordinate_parsing():
    map_service = MapService()
    
    # Coordinates in Hyderabad
    coord_cands = map_service.geocode_candidates("17.3850, 78.4867")
    assert len(coord_cands) == 1
    assert abs(coord_cands[0]["lat"] - 17.3850) < 0.001
    assert abs(coord_cands[0]["lon"] - 78.4867) < 0.001

    # Coordinates in Vijayawada
    coord_cands_vja = map_service.geocode_candidates("16.5062, 80.6480")
    assert len(coord_cands_vja) == 1
    assert abs(coord_cands_vja[0]["lat"] - 16.5062) < 0.001
    assert abs(coord_cands_vja[0]["lon"] - 80.6480) < 0.001

def test_current_location_dynamic_origin():
    map_service = MapService()
    user_pos = (12.9716, 77.5946) # Bangalore
    res = map_service.geocode_candidates("my location", origin_coords=user_pos)
    assert len(res) == 1
    assert abs(res[0]["lat"] - user_pos[0]) < 0.001
    assert abs(res[0]["lon"] - user_pos[1]) < 0.001
