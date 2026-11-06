import pytest
from src.map_service import MapService


def test_map_service_reverse_geocode_cache_and_precision():
    service = MapService()
    
    # 1. Test coordinate precision preservation
    lat, lon = 16.24014, 80.55918
    res = service.reverse_geocode_details(lat, lon)
    assert res is not None
    assert "lat" in res and "lon" in res
    assert abs(res["lat"] - lat) < 1e-4
    assert abs(res["lon"] - lon) < 1e-4
    assert "display_name" in res
    assert len(res["display_name"]) > 0

    # 2. Test in-memory cache hit
    res_cached = service.reverse_geocode_details(lat, lon)
    assert res_cached == res


def test_map_service_unmapped_remote_coords():
    service = MapService()
    # A remote point in the desert/ocean
    lat, lon = 24.12345, 68.54321
    res = service.reverse_geocode_details(lat, lon)
    assert res is not None
    assert abs(res["lat"] - lat) < 1e-4
    assert abs(res["lon"] - lon) < 1e-4
    # The coordinate must not be arbitrarily snapped to a faraway city
    assert f"{lat:.4f}" in res["display_name"] or len(res["name"]) > 0


def test_map_service_pin_code_geocoding():
    service = MapService()
    # Test PIN code geocoding
    candidates = service.geocode_candidates("522213", limit=3)
    assert len(candidates) > 0
    top = candidates[0]
    assert "lat" in top and "lon" in top
    assert -90.0 <= top["lat"] <= 90.0
    assert -180.0 <= top["lon"] <= 180.0


def test_cloud_server_ip_location_filtering():
    from app import detect_user_network_location
    
    # Cloud hosting datacenter locations (e.g. Oregon AWS 45.5999, -121.1871)
    # Must never be returned as user's origin
    loc = detect_user_network_location()
    if loc is not None:
        c_lat = loc["lat"]
        c_lon = loc["lon"]
        # Must not be US AWS / GCP server datacenter
        is_us_server = (c_lat > 25.0 and c_lon < -50.0) or (abs(c_lat - 45.5999) < 2.0 and abs(c_lon - (-121.1871)) < 2.0)
        assert not is_us_server, f"Server IP location was not filtered: {loc}"
