"""
Tests for Navigation Trust Audit Engine & UI Cards in P.A.T.H.F.I.N.D.E.R.
Covers all 10 required test scenarios:
1. Route generated successfully (Checked).
2. No hazards found in the checked area (NO_HAZARDS_DETECTED).
3. Known hazard intersects route (Warning with clear reason).
4. Hazard data is unavailable (Unable to verify).
5. Routing service is unavailable (Unable to verify).
6. Local graph or cached route usage (accuate provenance & offline mode).
7. User selects a different route (recalculates for new route).
8. Internet connectivity lost (graceful offline handling).
9. Confidence score unavailable/invalid (omitted with explanation).
10. Interface rendering on mobile and desktop (responsive HTML).
"""

import pytest
from datetime import datetime, timezone

from src.navigation_trust_audit import (
    NavigationTrustAuditEngine,
    NavigationTrustAuditResult,
    TrustAuditStatus,
    HazardAuditStatus,
    ConnectivityStatus,
    render_navigation_trust_audit_card_html,
    render_navigation_trust_audit_details_html
)
from src.hazard_map import GeographicHazard, HazardSeverity
from src.road_condition_model import RoadRestriction, RestrictionType
from src.satellite_road_auditor import SatelliteAuditResult


@pytest.fixture
def clean_route():
    """A valid route polyline in Vadlamudi / Guntur corridor with no hazards."""
    return {
        "route_id": "PRIMARY_ARTERIAL",
        "name": "Primary Arterial Route — Recommended",
        "polyline": [
            (16.2335, 80.5505),
            (16.2340, 80.5510),
            (16.2350, 80.5520),
            (16.2360, 80.5530)
        ],
        "distance_km": 0.42,
        "source": "OSRM (OpenStreetMap Global)"
    }


@pytest.fixture
def alternative_route():
    """A different alternative route corridor with different coordinates."""
    return {
        "route_id": "ALT_CORRIDOR_1",
        "name": "Alternative Northern Bypass",
        "polyline": [
            (16.2400, 80.5500),
            (16.2420, 80.5520),
            (16.2440, 80.5540)
        ],
        "distance_km": 0.65,
        "source": "Autonomous Road Graph Model"
    }


# =========================================================================
# Scenario 1: Route is generated successfully (Checked)
# =========================================================================
def test_scenario_1_route_generated_successfully(clean_route):
    audit = NavigationTrustAuditEngine.audit_route(
        route=clean_route,
        active_hazards=[],
        active_restrictions=[],
        hazard_data_available=True,
        is_online=True
    )
    assert audit.status == TrustAuditStatus.CHECKED
    assert audit.status_label == "Checked"
    assert audit.route_id == "PRIMARY_ARTERIAL"
    assert audit.corridor_length_km == 0.42
    assert audit.is_live_routing is True
    assert "Checked: Validated" in audit.status_reason


# =========================================================================
# Scenario 2: No hazards found in the checked area
# =========================================================================
def test_scenario_2_no_hazards_in_checked_area(clean_route):
    # Hazard is far away (> 50 km away in Vijayawada)
    distant_hazard = GeographicHazard(
        hazard_id="HZ_REMOTE",
        incident_type="FLOOD",
        severity=HazardSeverity.HIGH,
        latitude=16.5062,
        longitude=80.6480,
        radius_meters=100.0,
        description="Remote flooding outside corridor"
    )

    audit = NavigationTrustAuditEngine.audit_route(
        route=clean_route,
        active_hazards=[distant_hazard],
        active_restrictions=[],
        hazard_data_available=True
    )
    assert audit.hazard_status == HazardAuditStatus.NO_HAZARDS_DETECTED
    assert audit.hazard_summary == "No hazards detected in checked area"
    assert len(audit.detected_threats) == 0
    assert audit.status == TrustAuditStatus.CHECKED


# =========================================================================
# Scenario 3: Known hazard intersects the route (Warning with clear reason)
# =========================================================================
def test_scenario_3_known_hazard_intersects_route(clean_route):
    # Hazard right on the route polyline at (16.2345, 80.5515)
    intersecting_hazard = GeographicHazard(
        hazard_id="HZ_ON_PATH",
        incident_type="ROAD_DAMAGE",
        severity=HazardSeverity.CRITICAL,
        latitude=16.2345,
        longitude=80.5515,
        radius_meters=30.0,
        description="Water Pipe Rupture & Road Cave-In",
        source="Municipal Emergency Feed"
    )

    audit = NavigationTrustAuditEngine.audit_route(
        route=clean_route,
        active_hazards=[intersecting_hazard],
        active_restrictions=[],
        hazard_data_available=True,
        corridor_buffer_m=40.0
    )
    assert audit.status == TrustAuditStatus.WARNING
    assert audit.status_label == "Warning"
    assert audit.hazard_status == HazardAuditStatus.HAZARDS_DETECTED
    assert len(audit.detected_threats) == 1
    threat = audit.detected_threats[0]
    assert threat["type"] == "HAZARD"
    assert "Water Pipe Rupture" in threat["description"]
    assert threat["distance_m"] < 30.0
    assert "Warning: 1 obstruction(s) reported along corridor" in audit.status_reason


# =========================================================================
# Scenario 4: Hazard data is unavailable (Unable to verify)
# =========================================================================
def test_scenario_4_hazard_data_unavailable(clean_route):
    audit = NavigationTrustAuditEngine.audit_route(
        route=clean_route,
        active_hazards=None,
        active_restrictions=None,
        hazard_data_available=False
    )
    assert audit.status == TrustAuditStatus.UNABLE_TO_VERIFY
    assert audit.status_label == "Unable to verify"
    assert audit.hazard_status == HazardAuditStatus.DATA_UNAVAILABLE
    assert "Hazard data feed is unavailable" in audit.status_reason


# =========================================================================
# Scenario 5: Routing service is unavailable
# =========================================================================
def test_scenario_5_routing_service_unavailable():
    # Null route
    audit_none = NavigationTrustAuditEngine.audit_route(route=None)
    assert audit_none.status == TrustAuditStatus.UNABLE_TO_VERIFY
    assert "No route data available" in audit_none.status_reason

    # Empty geometry
    audit_empty = NavigationTrustAuditEngine.audit_route(route={"route_id": "EMPTY", "polyline": []})
    assert audit_empty.status == TrustAuditStatus.UNABLE_TO_VERIFY
    assert "insufficient coordinates" in audit_empty.status_reason


# =========================================================================
# Scenario 6: Local graph or cached route usage
# =========================================================================
def test_scenario_6_local_graph_or_cached_route():
    # Offline cached OSRM route
    cached_route = {
        "route_id": "CACHED_OSRM",
        "name": "Cached Highway Path",
        "polyline": [(16.2335, 80.5505), (16.2360, 80.5530)],
        "distance_km": 0.45,
        "source": "OSRM (OpenStreetMap Global)"
    }
    audit_cached = NavigationTrustAuditEngine.audit_route(
        route=cached_route,
        is_online=False,
        hazard_data_available=True
    )
    assert audit_cached.route_source_type == "CACHED"
    assert "Cached" in audit_cached.route_provider
    assert audit_cached.connectivity == ConnectivityStatus.OFFLINE_LOCAL

    # Local graph model
    local_route = {
        "route_id": "LOCAL_GRAPH",
        "name": "Campus Internal Corridor",
        "polyline": [(16.2335, 80.5505), (16.2360, 80.5530)],
        "distance_km": 0.45,
        "source": "Autonomous Road Graph Model"
    }
    audit_local = NavigationTrustAuditEngine.audit_route(
        route=local_route,
        is_online=False,
        hazard_data_available=True
    )
    assert audit_local.route_source_type == "LOCAL_GRAPH"
    assert audit_local.connectivity == ConnectivityStatus.OFFLINE_LOCAL


# =========================================================================
# Scenario 7: User selects a different route
# =========================================================================
def test_scenario_7_user_selects_different_route(clean_route, alternative_route):
    # Place a hazard only on the alternative route
    alt_hazard = GeographicHazard(
        hazard_id="HZ_ALT_ONLY",
        incident_type="CONSTRUCTION",
        severity=HazardSeverity.MEDIUM,
        latitude=16.2420,
        longitude=80.5520,
        radius_meters=40.0,
        description="Paving Works on Northern Bypass"
    )

    # 1. Audit Primary Route (clear)
    audit_primary = NavigationTrustAuditEngine.audit_route(
        route=clean_route,
        active_hazards=[alt_hazard],
        active_restrictions=[],
        hazard_data_available=True
    )
    assert audit_primary.route_id == "PRIMARY_ARTERIAL"
    assert audit_primary.status == TrustAuditStatus.CHECKED
    assert len(audit_primary.detected_threats) == 0

    # 2. User selects Alternative Route (warning triggered for new route)
    audit_alt = NavigationTrustAuditEngine.audit_route(
        route=alternative_route,
        active_hazards=[alt_hazard],
        active_restrictions=[],
        hazard_data_available=True
    )
    assert audit_alt.route_id == "ALT_CORRIDOR_1"
    assert audit_alt.status == TrustAuditStatus.WARNING
    assert len(audit_alt.detected_threats) == 1
    assert "Paving Works" in audit_alt.detected_threats[0]["description"]


# =========================================================================
# Scenario 8: Internet connectivity lost
# =========================================================================
def test_scenario_8_internet_connectivity_lost(clean_route):
    audit = NavigationTrustAuditEngine.audit_route(
        route=clean_route,
        is_online=False,
        hazard_data_available=True
    )
    assert audit.connectivity == ConnectivityStatus.OFFLINE_LOCAL
    assert "Offline" in audit.connectivity_label
    assert audit.route_source_type == "CACHED"


# =========================================================================
# Scenario 9: Confidence score unavailable or invalid
# =========================================================================
def test_scenario_9_confidence_score_handling(clean_route):
    audit = NavigationTrustAuditEngine.audit_route(route=clean_route)
    # Must NOT invent arbitrary percentage numbers (e.g. 98.5%)
    assert audit.confidence_score is None
    assert "Numeric confidence percentage is omitted" in audit.confidence_score_explanation
    assert "arbitrary probability" in audit.confidence_score_explanation


# =========================================================================
# Scenario 10: Interface rendering on mobile and desktop
# =========================================================================
def test_scenario_10_interface_rendering(clean_route):
    audit = NavigationTrustAuditEngine.audit_route(route=clean_route)

    # Compact Card HTML
    card_html = render_navigation_trust_audit_card_html(audit)
    assert "Navigation Trust Audit" in card_html
    assert "Checked" in card_html
    assert "grid-template-columns: repeat(auto-fit, minmax(130px, 1fr))" in card_html
    assert audit.route_name in card_html

    # Technical Details HTML
    details_html = render_navigation_trust_audit_details_html(audit)
    assert "Corridor Safety Buffer" in details_html
    assert "Confidence Score Integrity Note" in details_html
    assert "Operational Disclaimer" in details_html
    assert "±40 meters" in details_html
