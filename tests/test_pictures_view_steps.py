import pytest
from src.journey_storyteller import FriendlyTurnStep, generate_friendly_virtual_guide_turns
from src.aura_journey_engine import ManeuverSequenceBuilder, build_aura_journey_cockpit_html
from src.virtual_companion_ui import build_virtual_companion_hud_html


def test_pictures_view_step_unification():
    raw_steps = [
        {"instruction": "Head northeast on Main Road", "road": "Main Road", "distance_m": 150, "type": "depart"},
        {"instruction": "Turn left onto Goshamahal Road", "road": "Goshamahal Road", "distance_m": 300, "type": "turn-left"},
        {"instruction": "Turn right onto Dhoolpet Road", "road": "Dhoolpet Road", "distance_m": 450, "type": "turn-right"},
        {"instruction": "Follow Bedarwadi Road", "road": "Bedarwadi Road", "distance_m": 600, "type": "continue"},
        {"instruction": "Arrive safely at Sri Sanjeevini Poly Clinic", "road": "Sri Sanjeevini Poly Clinic", "distance_m": 0, "type": "arrive"}
    ]

    friendly = generate_friendly_virtual_guide_turns(
        steps=raw_steps,
        origin="Current Location (Hyderabad)",
        destination="Sri Sanjeevini Poly Clinic",
        travel_mode="Car"
    )

    assert len(friendly) == 5
    assert friendly[0].direction_type == "START"
    assert friendly[1].direction_type == "LEFT"
    assert friendly[2].direction_type == "RIGHT"
    assert friendly[4].direction_type == "ARRIVE"

    # Verify ManeuverSequenceBuilder consumes friendly steps and preserves exact 1st pic maneuvers
    maneuvers = ManeuverSequenceBuilder.build_sequence(
        steps=friendly,
        origin_label="Current Location (Hyderabad)",
        dest_label="Sri Sanjeevini Poly Clinic",
        total_distance_m=1500.0,
        travel_mode="car"
    )

    assert len(maneuvers) == 5
    assert maneuvers[0].direction_type == "START"
    assert maneuvers[1].direction_type == "TURN_LEFT"
    assert "Turn Left" in maneuvers[1].headline
    assert maneuvers[2].direction_type == "TURN_RIGHT"
    assert "Turn Right" in maneuvers[2].headline
    assert maneuvers[4].direction_type == "ARRIVE"


def test_pictures_view_html_rendering():
    raw_steps = [
        {"instruction": "Depart from Current Location", "road": "Main Road", "distance_m": 150, "type": "depart"},
        {"instruction": "Turn left onto Goshamahal Road", "road": "Goshamahal Road", "distance_m": 300, "type": "turn-left"},
        {"instruction": "Arrive at destination", "road": "Clinic", "distance_m": 0, "type": "arrive"}
    ]
    friendly = generate_friendly_virtual_guide_turns(
        steps=raw_steps,
        origin="Current Location",
        destination="Clinic"
    )
    maneuvers = ManeuverSequenceBuilder.build_sequence(
        steps=friendly,
        origin_label="Current Location",
        dest_label="Clinic",
        total_distance_m=450.0
    )

    cockpit_html = build_aura_journey_cockpit_html(
        origin_name="Current Location",
        dest_name="Clinic",
        travel_mode="car",
        total_distance_km=0.45,
        total_duration_mins=2.0,
        maneuvers=maneuvers
    )
    assert "step-picture-frame" in cockpit_html
    assert "getScenicStepSvg" in cockpit_html
    assert "pipeline-step-card" in cockpit_html

    hud_html = build_virtual_companion_hud_html(
        session_id="SESS_TEST_PIC_VIEW",
        origin_name="Current Location",
        dest_name="Clinic",
        travel_mode="car",
        steps=friendly
    )
    assert "step-picture-frame" in hud_html
    assert "getScenicStepSvg" in hud_html
    assert "timeline-step-card" in hud_html
