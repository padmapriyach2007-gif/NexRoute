"""
Acceptance Test Suite for Precise Location Detection in NexRoute Maps
Validates:
1. Exact coordinate preservation (6 decimal places, ~0.1m precision).
2. Elimination of road-snapping (origin coordinates maintained separately from routing polylines).
3. Discrimination of small locations: Railway Station vs Railway Track Corridor vs Shop vs Hospital vs Open Land.
4. Accuracy tier assignment: 'Exact point', 'Nearby address', 'Approximate locality'.
5. Micro-spatial deduplication preserving closely clustered landmarks.
6. Pending click coordinates visualization on interactive Folium maps.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.map_service import MapService


@pytest.fixture
def map_service():
    service = MapService()
    # Clear any memory cache for isolated test execution
    if hasattr(service, "_reverse_geocode_cache"):
        service._reverse_geocode_cache.clear()
    return service


def test_railway_station_identification(map_service):
    """Test that a railway station is accurately identified with 'Exact point' precision."""
    mock_nominatim = {
        "place_id": 101,
        "category": "railway",
        "type": "station",
        "name": "Tenali Junction Railway Station",
        "display_name": "Tenali Junction Railway Station, Station Road, Tenali, Guntur, Andhra Pradesh, 522201, India",
        "address": {
            "railway": "Tenali Junction Railway Station",
            "road": "Station Road",
            "town": "Tenali",
            "state_district": "Guntur",
            "state": "Andhra Pradesh",
            "postcode": "522201",
            "country": "India"
        }
    }

    with patch.object(map_service.session, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_nominatim
        mock_get.return_value = mock_resp

        res = map_service.reverse_geocode_details(16.243521, 80.640134, zoom=18)

        assert "Tenali Junction Railway Station" in res["place_name"]
        assert res["accuracy_level"] == "Exact point"
        assert res["accuracy_badge"] == "🎯 Exact Point"
        assert res["category"] in ("railway", "railway_station")
        assert res["category_icon"] == "🚆"
        assert res["lat"] == 16.243521
        assert res["lon"] == 80.640134


def test_railway_track_corridor_not_main_road(map_service):
    """Test that clicking on a railway track identifies it as a track corridor, NOT a nearby road."""
    mock_nominatim = {
        "place_id": 102,
        "category": "railway",
        "type": "rail",
        "name": "",  # Tracks typically have no commercial name
        "display_name": "South Central Railway Track, Tenali, Guntur, Andhra Pradesh, India",
        "address": {
            "railway": "rail",
            "road": "Guntur-Tenali Main Road",  # Nearby road that should NOT override track identity
            "town": "Tenali",
            "state": "Andhra Pradesh",
            "country": "India"
        }
    }

    with patch.object(map_service.session, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_nominatim
        mock_get.return_value = mock_resp

        res = map_service.reverse_geocode_details(16.241100, 80.645200, zoom=18)

        assert "Railway Track" in res["place_name"]
        assert res["category_icon"] == "🛤️"
        assert "Guntur-Tenali Main Road" not in res["place_name"]  # Ensure not misidentified as the road


def test_commercial_retail_shop_precision(map_service):
    """Test that an individual retail shop is identified with exact point accuracy."""
    mock_nominatim = {
        "place_id": 103,
        "category": "shop",
        "type": "convenience",
        "name": "Sri Lakshmi Kirana & General Store",
        "display_name": "Sri Lakshmi Kirana & General Store, Market Street, Tenali, Andhra Pradesh, India",
        "address": {
            "shop": "Sri Lakshmi Kirana & General Store",
            "road": "Market Street",
            "town": "Tenali",
            "state": "Andhra Pradesh",
            "country": "India"
        }
    }

    with patch.object(map_service.session, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_nominatim
        mock_get.return_value = mock_resp

        res = map_service.reverse_geocode_details(16.242301, 80.638920, zoom=18)

        assert res["place_name"] == "Sri Lakshmi Kirana & General Store"
        assert res["accuracy_level"] == "Exact point"
        assert res["category"] in ("shop", "retail")
        assert res["category_icon"] == "🏪"


def test_hospital_healthcare_precision(map_service):
    """Test that a hospital or healthcare amenity is correctly identified."""
    mock_nominatim = {
        "place_id": 104,
        "category": "amenity",
        "type": "hospital",
        "name": "Tenali Area Hospital",
        "display_name": "Tenali Area Hospital, Hospital Road, Tenali, Andhra Pradesh, 522201, India",
        "address": {
            "hospital": "Tenali Area Hospital",
            "road": "Hospital Road",
            "town": "Tenali",
            "state": "Andhra Pradesh",
            "postcode": "522201",
            "country": "India"
        }
    }

    with patch.object(map_service.session, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_nominatim
        mock_get.return_value = mock_resp

        res = map_service.reverse_geocode_details(16.239800, 80.642100, zoom=18)

        assert res["place_name"] == "Tenali Area Hospital"
        assert res["accuracy_level"] == "Exact point"
        assert res["category_icon"] == "🏥"


def test_open_unmapped_land_no_hallucination(map_service):
    """Test that unmapped open land returns physical coordinates and does NOT invent a business."""
    with patch.object(map_service.session, "get") as mock_get:
        # Simulate Nominatim returning 404 or empty
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        res = map_service.reverse_geocode_details(16.210543, 80.690876, zoom=18)

        assert res["accuracy_level"] == "Approximate locality"
        assert res["accuracy_badge"] == "🌐 Approximate Locality"
        assert "16.21054" in res["formatted_address"]
        assert "80.69088" in res["formatted_address"] or "80.69087" in res["formatted_address"]


def test_no_road_snapping_in_interactive_map(map_service):
    """Verify that start vehicle marker in create_interactive_map remains at origin_coords and does not snap to route polyline."""
    origin = (16.243500, 80.640100)
    dest = (16.250000, 80.650000)
    # Route with snapped first waypoint 50 meters away
    snapped_first_waypoint = [16.243950, 80.640550]
    fake_routes = [{
        "rank": 1,
        "is_eligible": True,
        "polyline": [snapped_first_waypoint, [16.245000, 80.642000], [16.250000, 80.650000]]
    }]

    m = map_service.create_interactive_map(
        center_lat=16.245,
        center_lon=80.645,
        origin_coords=origin,
        destination_coords=dest,
        routes=fake_routes
    )

    # Search children in the map to verify marker location matches exact origin
    marker_locations = []
    for child in m._children.values():
        if hasattr(child, "location") and child.location:
            marker_locations.append(tuple(round(x, 6) for x in child.location))

    # The exact origin MUST be present as a marker location
    assert (round(origin[0], 6), round(origin[1], 6)) in marker_locations
    # The snapped road waypoint must NOT be the origin marker location
    assert (round(snapped_first_waypoint[0], 6), round(snapped_first_waypoint[1], 6)) not in marker_locations


def test_pending_click_coords_rendered(map_service):
    """Verify that pending_click_coords are accepted and rendered as a pending marker on the map."""
    pending_coords = (16.247812, 80.643219)

    m = map_service.build_interactive_map(
        center_lat=16.245,
        center_lon=80.645,
        pending_click_coords=pending_coords
    )

    marker_locations = []
    for child in m._children.values():
        if hasattr(child, "location") and child.location:
            marker_locations.append(tuple(round(x, 6) for x in child.location))

    assert (round(pending_coords[0], 6), round(pending_coords[1], 6)) in marker_locations


def test_micro_spatial_deduplication_preserves_nearby_landmarks(map_service):
    """Verify that distinct landmarks within 100 meters in the same locality are not dropped by geocode_candidates."""
    nominatim_results = [
        {
            "display_name": "Tenali Railway Station, Station Road, Tenali, Andhra Pradesh",
            "lat": "16.243500",
            "lon": "80.640100",
            "importance": 0.85,
            "address": {"town": "Tenali", "railway": "Tenali Railway Station"}
        },
        {
            "display_name": "Tenali RTC Bus Station, Main Road, Tenali, Andhra Pradesh",
            "lat": "16.244200",
            "lon": "80.640800",
            "importance": 0.80,
            "address": {"town": "Tenali", "bus_station": "Tenali RTC Bus Station"}
        },
        {
            "display_name": "Sita Ram Mandir, Market Street, Tenali, Andhra Pradesh",
            "lat": "16.243800",
            "lon": "80.640400",
            "importance": 0.75,
            "address": {"town": "Tenali", "place_of_worship": "Sita Ram Mandir"}
        },
        {
            "display_name": "Tenali Railway Station, Station Road, Tenali, Andhra Pradesh",
            "lat": "16.243505",
            "lon": "80.640105",
            "importance": 0.70,
            "address": {"town": "Tenali", "railway": "Tenali Railway Station"}
        }
    ]

    map_service.cache = {}

    with patch.object(map_service.session, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = nominatim_results
        mock_get.return_value = mock_resp

        results = map_service.geocode_candidates("Tenali Station", limit=5)
        result_names = [r["name"] for r in results]

        assert "Tenali Railway Station" in result_names
        assert "Tenali RTC Bus Station" in result_names
        assert "Sita Ram Mandir" in result_names
        # Duplicate instance should be filtered
        assert result_names.count("Tenali Railway Station") == 1
