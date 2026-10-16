"""
Automated Pytest Suite for Real-World GPS Navigation, Hazard Intersections,
Safety Route Filtering, and Notification Tracking.
"""

import pytest
from src.map_service import MapService
from src.location_service import LocationService, LocationSource, LocationPermissionStatus
from src.hazard_map import HazardMap, GeographicHazard, HazardSeverity, haversine_distance_m
from src.route_engine import RealWorldRouteEngine, TravelMode
from src.safety_route_filter import SafetyRouteFilter, RouteSafetyStatus
from src.notification_service import NotificationService, NotificationDeliveryStatus, NotificationPriority


def test_haversine_distance_calculation():
    # Distance between Vignan University (16.2335, 80.5505) and Guntur (16.3067, 80.4365) is approx 14.6 km
    dist_m = haversine_distance_m(16.2335, 80.5505, 16.3067, 80.4365)
    assert 14000 < dist_m < 15500


def test_map_service_geocoding_cache():
    map_srv = MapService()
    coords = map_srv.geocode("Vignan University")
    assert coords is not None
    assert coords["lat"] == 16.2335
    assert coords["lon"] == 80.5505


def test_location_service_permission_and_stale_detection():
    loc_srv = LocationService()
    # Default without permission -> simulated or manual
    reading, status = loc_srv.get_effective_location()
    assert reading.source == LocationSource.SIMULATED

    # Set manual pin drop (works without permission)
    manual_reading = loc_srv.set_manual_location(16.2500, 80.5000, label="User Pin")
    assert manual_reading.source == LocationSource.MANUAL_PIN
    assert loc_srv.get_effective_location()[0].coordinates == (16.2500, 80.5000)

    # Permission Granted GPS
    loc_srv.set_permission(LocationPermissionStatus.GRANTED)
    gps_reading = loc_srv.update_gps_location(16.2335, 80.5505, accuracy_m=8.5)
    assert gps_reading.is_accurate_enough(20.0) is True
    assert gps_reading.is_stale() is False


def test_multi_route_generation():
    engine = RealWorldRouteEngine()
    routes = engine.calculate_routes(16.2335, 80.5505, 16.3067, 80.4365, mode=TravelMode.DRIVING)
    assert len(routes) >= 2  # Returns primary + alternative corridors
    assert all(r.distance_km > 0 for r in routes)
    assert all(len(r.polyline) >= 2 for r in routes)


def test_hazard_spatial_collision_and_safety_filtering():
    hazard_map = HazardMap()
    engine = RealWorldRouteEngine()
    safety_filter = SafetyRouteFilter(hazard_map)

    # Generate 3 corridors
    routes = engine.calculate_routes(16.2335, 80.5505, 16.3067, 80.4365, mode=TravelMode.DRIVING)
    assert len(routes) >= 2

    # Initially all routes are eligible
    eval_initial = safety_filter.evaluate_candidate_routes(routes)
    assert all(r.is_eligible for r in eval_initial)

    # Inject hazard directly intersecting Route 1 (Primary Route)
    target_route = routes[0]
    mid_point = target_route.polyline[len(target_route.polyline) // 2]
    hazard = GeographicHazard(
        hazard_id="HAZ_001",
        incident_type="FIRE_DETECTED",
        severity=HazardSeverity.CRITICAL,
        latitude=mid_point[0],
        longitude=mid_point[1],
        radius_meters=300.0,
        description="Tanker explosion blocking main corridor",
        affected_road_name="Campus Main Avenue"
    )
    hazard_map.add_hazard(hazard)

    # Re-evaluate routes
    eval_after_hazard = safety_filter.evaluate_candidate_routes(routes)
    
    # Route 1 must now be excluded with ROUTE_CONTAINS_CONFIRMED_HAZARD
    r1_eval = next(e for e in eval_after_hazard if e.route.route_id == target_route.route_id)
    assert r1_eval.is_eligible is False
    assert r1_eval.status == RouteSafetyStatus.ROUTE_CONTAINS_CONFIRMED_HAZARD
    assert len(r1_eval.rejection_reasons) > 0

    # At least one bypass corridor (Route 2 or 3) must remain eligible
    eligible_bypasses = [e for e in eval_after_hazard if e.is_eligible]
    assert len(eligible_bypasses) >= 1


def test_all_routes_blocked_returns_no_verified_route():
    hazard_map = HazardMap()
    engine = RealWorldRouteEngine()
    safety_filter = SafetyRouteFilter(hazard_map)

    routes = engine.calculate_routes(16.2335, 80.5505, 16.3067, 80.4365, mode=TravelMode.DRIVING)

    # Block every single corridor
    for idx, r in enumerate(routes):
        pt = r.polyline[len(r.polyline) // 2]
        h = GeographicHazard(
            hazard_id=f"BLOCK_{idx}",
            incident_type="FLOOD_REPORTED",
            severity=HazardSeverity.HIGH,
            latitude=pt[0],
            longitude=pt[1],
            radius_meters=500.0,
            description="Severe flash flood"
        )
        hazard_map.add_hazard(h)

    evaluated = safety_filter.evaluate_candidate_routes(routes)
    assert all(e.is_eligible is False for e in evaluated)
    assert not any(e.is_eligible for e in evaluated)


def test_notification_delivery_lifecycle():
    notif_srv = NotificationService()
    notif_srv.register_device("user_101", "fcm_test_token_abc")

    payload = notif_srv.send_emergency_alert(
        target_user_id="user_101",
        title="EVACUATION ALERT",
        body="Hazard detected on corridor.",
        incident_type="FIRE_DETECTED",
        priority=NotificationPriority.EMERGENCY_OVERRIDE
    )

    assert payload.status in (NotificationDeliveryStatus.SIMULATED, NotificationDeliveryStatus.SUBMISSION_ACCEPTED)
    assert payload.target_user_id == "user_101"

    # User acknowledges notification
    ack_res = notif_srv.acknowledge_notification(payload.notification_id)
    assert ack_res is True
    assert payload.status == NotificationDeliveryStatus.USER_ACKNOWLEDGED
