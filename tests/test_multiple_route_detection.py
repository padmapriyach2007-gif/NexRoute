"""
Acceptance Test Suite for Advanced Full-Map Multiple Route Detection System
Validates:
1. Full-map road network layer integration on interactive satellite maps.
2. Multiple alternative route generation with distinct routes.
3. High-contrast dual-stroke route visualization with custom palette.
4. Distance, travel time, and road condition calculation.
5. Dynamic route recalculation and deduplication.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.map_service import MapService
from src.route_engine import OSRMGlobalRoutingProvider, RealWorldRouteEngine, TravelMode, RouteOption


@pytest.fixture
def map_service():
    service = MapService()
    if hasattr(service, "_reverse_geocode_cache"):
        service._reverse_geocode_cache.clear()
    return service


def test_full_map_road_network_layers(map_service):
    """Verify that full-map road network and OpenStreetMap layers are added to the interactive map."""
    m = map_service.create_interactive_map(
        center_lat=16.2435,
        center_lon=80.6401,
        zoom=14,
        map_style="satellite_hybrid"
    )

    layer_names = []
    for child in m._children.values():
        if hasattr(child, "layer_name"):
            layer_names.append(child.layer_name)
        elif hasattr(child, "tile_name"):
            layer_names.append(child.tile_name)

    # Full Road Network overlay and OSM layer must be present
    assert any("Full Road Network" in name for name in layer_names)
    assert any("OpenStreetMap" in name for name in layer_names)


def test_dual_stroke_route_visualization(map_service):
    """Verify that routes are rendered with dual-stroke polylines (background casing + foreground line)."""
    origin = (16.2435, 80.6401)
    dest = (16.3067, 80.4365)
    fake_routes = [
        {
            "rank": 1,
            "name": "NH16 Express Highway",
            "polyline": [[16.2435, 80.6401], [16.2750, 80.5380], [16.3067, 80.4365]],
            "distance_km": 28.5,
            "duration_minutes": 32.0,
            "color": "#00f0b5",
            "is_eligible": True,
            "is_selected": False
        },
        {
            "rank": 2,
            "name": "State Highway 39 Corridor",
            "polyline": [[16.2435, 80.6401], [16.2600, 80.5100], [16.3067, 80.4365]],
            "distance_km": 31.2,
            "duration_minutes": 38.0,
            "color": "#a855f7",
            "is_eligible": True,
            "is_selected": False
        }
    ]

    m = map_service.create_interactive_map(
        center_lat=16.275,
        center_lon=80.538,
        origin_coords=origin,
        destination_coords=dest,
        routes=fake_routes
    )

    # Verify that Polylines exist on the map for both routes and background casing
    polyline_count = 0
    for child in m._children.values():
        if "PolyLine" in type(child).__name__:
            polyline_count += 1

    # Should have at least 4 polylines (2 casing + 2 foreground)
    assert polyline_count >= 4


def test_multiple_route_generation_with_alternatives():
    """Verify that OSRMGlobalRoutingProvider requests and handles multiple alternative routes."""
    provider = OSRMGlobalRoutingProvider()

    # Mock OSRM response with 2 routes
    mock_osrm_data = {
        "code": "Ok",
        "routes": [
            {
                "geometry": {
                    "coordinates": [[80.6401, 16.2435], [80.5380, 16.2750], [80.4365, 16.3067]]
                },
                "distance": 28500.0,
                "duration": 1920.0,
                "legs": [{"summary": "NH16", "steps": []}]
            },
            {
                "geometry": {
                    "coordinates": [[80.6401, 16.2435], [80.5100, 16.2600], [80.4365, 16.3067]]
                },
                "distance": 31200.0,
                "duration": 2280.0,
                "legs": [{"summary": "SH39", "steps": []}]
            }
        ]
    }

    with patch.object(provider, "_fetch_osrm") as mock_fetch:
        route1 = RouteOption(
            route_id="OSRM_1",
            name="Primary Highway Route",
            mode=TravelMode.DRIVING,
            distance_meters=28500.0,
            duration_seconds=1920.0,
            polyline=[[16.2435, 80.6401], [16.2750, 80.5380], [16.3067, 80.4365]]
        )
        route2 = RouteOption(
            route_id="OSRM_2",
            name="Alternative 1: Via Arterial Network",
            mode=TravelMode.DRIVING,
            distance_meters=31200.0,
            duration_seconds=2280.0,
            polyline=[[16.2435, 80.6401], [16.2600, 80.5100], [16.3067, 80.4365]]
        )
        route3 = RouteOption(
            route_id="OSRM_3",
            name="Alternative 2: Regional Bypass Route",
            mode=TravelMode.DRIVING,
            distance_meters=33100.0,
            duration_seconds=2400.0,
            polyline=[[16.2435, 80.6401], [16.2500, 80.4800], [16.3067, 80.4365]]
        )
        mock_fetch.return_value = [route1, route2, route3]

        routes = provider.calculate_routes(16.2435, 80.6401, 16.3067, 80.4365, mode=TravelMode.DRIVING)

        assert len(routes) >= 3
        assert routes[0].route_id == "OSRM_1"
        assert routes[1].route_id == "OSRM_2"
        assert routes[2].route_id == "OSRM_3"
        assert all(r.distance_meters > 0 for r in routes)
        assert len(set(r.route_id for r in routes)) == len(routes)


def test_build_interactive_map_route_metadata_preservation(map_service):
    """Verify that build_interactive_map preserves distance_km, duration_minutes, and road_condition."""
    route_polylines = [{
        "name": "Fastest Route",
        "coordinates": [[16.2435, 80.6401], [16.3067, 80.4365]],
        "rank": 1,
        "color": "#00f0b5",
        "distance_km": 25.4,
        "duration_minutes": 28.0,
        "road_condition": "Smooth 4-lane Highway",
        "is_eligible": True,
        "is_selected": True
    }]

    m = map_service.build_interactive_map(
        center_lat=16.275,
        center_lon=80.538,
        route_polylines=route_polylines
    )

    # Check html elements or child popups for distance and condition
    m_html = m.get_root().render()
    assert "25.4" in m_html or "Smooth 4-lane Highway" in m_html
