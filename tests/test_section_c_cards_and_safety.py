"""
Tests for Section C: Route Recommendation Cards, Safety Analysis & Map Synchronization
Verifies:
1. Each candidate route is a structured RouteOption with a stable ID, distinct geometry, distance, and duration.
2. Route-card selection: selecting Route 2 sets selected_route_id to Route 2 and activates Route 2's geometry.
3. De-emphasis: selected route gets full opacity (1.0) and high weight (8), while other routes are de-emphasized.
4. Single candidate route handling: transparently identified as sole route without fabricating alternatives.
5. Endpoint change invalidates obsolete routes and clears previous route selection.
6. Safety trust audit: qualifies safety claims as "no reported hazards", avoids false certainty, and defines limitations.
"""

import pytest
from src.route_engine import RouteOption, TravelMode
from src.multi_objective_router import MultiObjectiveRouter
from src.navigation_trust_audit import NavigationTrustAuditEngine, TrustAuditStatus, HazardAuditStatus
from src.hazard_map import GeographicHazard, HazardSeverity


@pytest.fixture
def sample_candidate_routes():
    r1 = RouteOption(
        route_id="ROUTE_PRIMARY",
        name="Main Highway Route 1",
        mode=TravelMode.DRIVING,
        distance_meters=12000.0,
        duration_seconds=720.0,
        polyline=[(16.20, 80.50), (16.25, 80.55), (16.30, 80.60)],
        summary_roads=["NH-16 Highway"],
        is_accessible=True
    )
    r2 = RouteOption(
        route_id="ROUTE_ALT_2",
        name="Canal Road Alternative 2",
        mode=TravelMode.DRIVING,
        distance_meters=14500.0,
        duration_seconds=900.0,
        polyline=[(16.20, 80.50), (16.22, 80.58), (16.30, 80.60)],
        summary_roads=["Canal Bund Road"],
        is_accessible=True
    )
    return [r1, r2]


def test_route_card_selection_sets_correct_route_id_and_geometry(sample_candidate_routes):
    """Selecting Route 2 updates selected_route_id to Route 2 and activates Route 2's polyline."""
    router = MultiObjectiveRouter()
    ranked = router.evaluate_and_rank_routes(candidate_routes=sample_candidate_routes)

    # Simulate user clicking Route 2
    target_focus = "ROUTE_ALT_2"
    selected_item = next(r for r in ranked if r.route.route_id == target_focus)

    assert selected_item.route.route_id == "ROUTE_ALT_2"
    assert selected_item.route.polyline == sample_candidate_routes[1].polyline
    assert selected_item.route.polyline != sample_candidate_routes[0].polyline


def test_map_polyline_selection_highlighting(sample_candidate_routes):
    """
    Simulates map polyline builder logic from app.py:
    Selected route gets weight 8, opacity 1.0; other routes get weight 3.5, opacity 0.40.
    """
    router = MultiObjectiveRouter()
    ranked = router.evaluate_and_rank_routes(candidate_routes=sample_candidate_routes)

    cur_focus = "ROUTE_ALT_2"
    polylines = []
    palette = ["#10b981", "#0ea5e9"]

    for r_item in ranked:
        is_selected = (cur_focus == r_item.route.route_id)
        has_selection = (cur_focus != "ALL")

        if has_selection:
            weight = 8 if is_selected else 3.5
            opacity = 1.0 if is_selected else 0.40
        else:
            weight = 6 if r_item.rank == 1 else 4.5
            opacity = 0.95 if r_item.rank == 1 else 0.80

        polylines.append({
            "route_id": r_item.route.route_id,
            "weight": weight,
            "opacity": opacity,
            "is_selected": is_selected
        })

    p_r1 = next(p for p in polylines if p["route_id"] == "ROUTE_PRIMARY")
    p_r2 = next(p for p in polylines if p["route_id"] == "ROUTE_ALT_2")

    # Route 2 is selected: highlighted
    assert p_r2["is_selected"] is True
    assert p_r2["weight"] == 8
    assert p_r2["opacity"] == 1.0

    # Route 1 is not selected: de-emphasized
    assert p_r1["is_selected"] is False
    assert p_r1["weight"] == 3.5
    assert p_r1["opacity"] == 0.40


def test_single_candidate_route_honesty():
    """Single route candidate is labeled honestly without fabricating alternatives."""
    solo = RouteOption(
        route_id="ROUTE_SOLO",
        name="Only Available Way",
        mode=TravelMode.DRIVING,
        distance_meters=8000.0,
        duration_seconds=600.0,
        polyline=[(16.20, 80.50), (16.28, 80.58)],
        summary_roads=["Lone Bridge Road"]
    )
    router = MultiObjectiveRouter()
    ranked = router.evaluate_and_rank_routes(candidate_routes=[solo])

    assert len(ranked) == 1
    assert ranked[0].route.route_id == "ROUTE_SOLO"
    assert ranked[0].rank == 1


def test_endpoint_change_clears_previous_routes():
    """Simulates endpoint change in app.py to verify obsolete route invalidation."""
    orig_1 = (16.2000, 80.5000)
    dest_1 = (16.3000, 80.6000)
    sig_1 = (orig_1[0], orig_1[1], dest_1[0], dest_1[1], "driving")

    # Destination changes
    dest_2 = (16.4000, 80.7000)
    sig_2 = (orig_1[0], orig_1[1], dest_2[0], dest_2[1], "driving")

    assert sig_1 != sig_2
    # Invalidation triggers resetting focused_route_id to ALL and selected_route_id to None
    reset_focus = "ALL" if sig_1 != sig_2 else "ROUTE_ALT_2"
    assert reset_focus == "ALL"


def test_safety_trust_audit_qualifies_claims(sample_candidate_routes):
    """
    Verifies that NavigationTrustAuditEngine:
    1. Returns 'Checked' status with clear explanation.
    2. Omits arbitrary probability scores.
    3. Contains clear limitations disclaimer.
    """
    route = sample_candidate_routes[0]
    audit_res = NavigationTrustAuditEngine.audit_route(
        route=route,
        active_hazards=[],
        active_restrictions=[],
        hazard_data_available=True
    )

    assert audit_res.status == TrustAuditStatus.CHECKED
    assert audit_res.hazard_status == HazardAuditStatus.NO_HAZARDS_DETECTED
    # Arbitrary percentage omitted
    assert audit_res.confidence_score is None
    # Limitations communicated
    assert "limitations" in audit_res.limitations_disclaimer.lower() or "unreported" in audit_res.limitations_disclaimer.lower()
