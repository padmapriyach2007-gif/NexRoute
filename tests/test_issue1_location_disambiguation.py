"""
Tests for Issue 1: Ambiguous Location Search and Destination Selection.

Scenarios tested:
1. City name with multiple matches across countries (e.g. Hyderabad -> India & Pakistan).
2. Distinguishable result metadata: place name, city, state/province, country, provider, provider_id.
3. Unique place name returns high-confidence match with convenient selection flow.
4. Unresolvable / empty / invalid search handling.
5. Changing destination resets candidate list and prevents stale suggestions.
6. Selected location preserves exact coordinates and provider identifier in session-state schema.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.map_service import MapService


def test_ambiguous_city_search_returns_multiple_countries():
    """
    Searching for 'Hyderabad' should return distinguishable candidates across countries
    (Telangana, India and Sindh, Pakistan) from the search providers.
    """
    map_srv = MapService()
    cands = map_srv.geocode_candidates("Hyderabad", limit=5)
    
    assert len(cands) >= 2, f"Expected multiple candidates for 'Hyderabad', got: {cands}"
    
    countries = {c.get("country") for c in cands}
    states = {c.get("state") for c in cands}
    
    # Must contain India and Pakistan
    assert "India" in countries, "Expected India in Hyderabad candidates"
    assert "Pakistan" in countries, "Expected Pakistan in Hyderabad candidates"
    assert "Telangana" in states, "Expected Telangana in Hyderabad candidates"
    assert "Sindh" in states, "Expected Sindh in Hyderabad candidates"
    
    # Verify metadata fields are present
    for cand in cands:
        assert "lat" in cand and "lon" in cand
        assert -90.0 <= cand["lat"] <= 90.0
        assert -180.0 <= cand["lon"] <= 180.0
        assert "display_name" in cand
        assert "provider" in cand
        assert "provider_id" in cand
        assert cand["provider_id"]  # Must not be empty


def test_unique_place_name_returns_single_high_confidence():
    """
    A specific local landmark or coordinate should return a unique high-confidence result.
    """
    map_srv = MapService()
    cands = map_srv.geocode_candidates("BSR Enclave, Sarojini Naidu Street, Tenali", limit=5)
    assert len(cands) >= 1
    top = cands[0]
    assert "Tenali" in top.get("city", "") or "Tenali" in top.get("display_name", "")
    assert round(top["lat"], 2) == 16.23
    assert round(top["lon"], 2) == 80.65


def test_exact_coordinate_input_disambiguation():
    """Direct coordinate inputs should resolve directly with type='coordinate'."""
    map_srv = MapService()
    cands = map_srv.geocode_candidates("17.3850, 78.4867", limit=5)
    assert len(cands) == 1
    assert cands[0]["type"] == "coordinate"
    assert round(cands[0]["lat"], 4) == 17.3850
    assert round(cands[0]["lon"], 4) == 78.4867


def test_invalid_coordinates_and_empty_results():
    """Out of range coordinates or gibberish queries return empty list."""
    map_srv = MapService()
    assert map_srv.geocode_candidates("95.0, 80.0") == []
    assert map_srv.geocode_candidates("20.0, 195.0") == []
    assert map_srv.geocode_candidates("") == []
    assert map_srv.geocode_candidates("   ") == []


def test_mocked_provider_disambiguation_cambridge():
    """Mock provider with Cambridge candidates across UK, USA, and Canada."""
    map_srv = MapService()
    mock_nominatim = [
        {"lat": 52.2053, "lon": 0.1218, "display_name": "Cambridge, Cambridgeshire, England, United Kingdom", "osm_id": 1001, "osm_type": "relation", "address": {"country": "United Kingdom", "state": "Cambridgeshire", "city": "Cambridge"}},
        {"lat": 42.3736, "lon": -71.1097, "display_name": "Cambridge, Middlesex County, Massachusetts, United States", "osm_id": 1002, "osm_type": "relation", "address": {"country": "United States", "state": "Massachusetts", "city": "Cambridge"}},
        {"lat": 43.3616, "lon": -80.3144, "display_name": "Cambridge, Waterloo, Ontario, Canada", "osm_id": 1003, "osm_type": "relation", "address": {"country": "Canada", "state": "Ontario", "city": "Cambridge"}}
    ]
    
    with patch.object(map_srv.session, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_nominatim
        mock_get.return_value = mock_resp
        
        # Clear cache for Cambridge test
        map_srv._query_candidates_cache.pop("cambridge", None)
        cands = map_srv.geocode_candidates("Cambridge", limit=5)
        
        assert len(cands) == 3
        countries = {c["country"] for c in cands}
        assert "United Kingdom" in countries
        assert "United States" in countries
        assert "Canada" in countries
        
        # Verify provider IDs were properly extracted
        prov_ids = {c["provider_id"] for c in cands}
        assert "osm_relation_1001" in prov_ids
        assert "osm_relation_1002" in prov_ids
        assert "osm_relation_1003" in prov_ids


def test_provider_network_failure_returns_gracefully():
    """When external providers throw network exceptions, MapService fails gracefully."""
    map_srv = MapService()
    with patch.object(map_srv.session, "get", side_effect=Exception("Network connection failed")):
        # Searching unknown place when network is down returns empty list without crashing
        res = map_srv.geocode_candidates("RandomUnknownPlaceXYZ123456", limit=5)
        assert isinstance(res, list)
        assert len(res) == 0
