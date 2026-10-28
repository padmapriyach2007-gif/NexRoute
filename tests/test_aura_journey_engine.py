import pytest
from src.aura_journey_engine import (
    AuraJourneyStage,
    AuraPose,
    AuraManeuverStep,
    AuraPoseAssetManager,
    AuraSpeechGenerator,
    ManeuverSequenceBuilder,
    build_aura_journey_cockpit_html
)

def test_aura_speech_generation():
    # Test speech generation for each stage
    welcome_msg, welcome_pose = AuraSpeechGenerator.get_speech_for_stage(AuraJourneyStage.WELCOME)
    assert "Aura" in welcome_msg
    assert welcome_pose in (AuraPose.WAVING, AuraPose.WELCOME)

    start_guidance, start_pose = AuraSpeechGenerator.get_speech_for_stage(AuraJourneyStage.START_INPUT)
    assert "starting" in start_guidance.lower()
    assert start_pose == AuraPose.POINTING

    dest_guidance, dest_pose = AuraSpeechGenerator.get_speech_for_stage(AuraJourneyStage.DEST_INPUT)
    assert "destination" in dest_guidance.lower()
    assert dest_pose == AuraPose.POINTING

    arrived_msg, arrived_pose = AuraSpeechGenerator.get_speech_for_stage(AuraJourneyStage.ARRIVED)
    assert "made it" in arrived_msg.lower() or "destination" in arrived_msg.lower()
    assert arrived_pose == AuraPose.EXCITED

    off_route_msg, off_route_pose = AuraSpeechGenerator.get_speech_for_stage(AuraJourneyStage.OFF_ROUTE)
    assert "off the planned route" in off_route_msg.lower()
    assert off_route_pose == AuraPose.THINKING

def test_aura_pose_asset_manager():
    # Test that poses are loaded and return valid data or fallback URIs
    poses = AuraPoseAssetManager.load_poses()
    assert isinstance(poses, dict)
    
    for pose in AuraPose:
        uri = AuraPoseAssetManager.get_pose_uri(pose)
        assert isinstance(uri, str)

def test_maneuver_sequence_builder_from_raw():
    raw_maneuvers = [
        {"instruction": "Head northeast on MG Road", "road": "MG Road", "distance": 450, "duration": 60, "type": "depart"},
        {"instruction": "Turn left onto Brigade Road", "road": "Brigade Road", "distance": 1200, "duration": 180, "type": "turn-left"},
        {"instruction": "At roundabout, take 2nd exit onto Residency Road", "road": "Residency Road", "distance": 800, "duration": 120, "type": "roundabout", "exit": 2},
        {"instruction": "Keep right toward Richmond Circle", "road": "Richmond Circle", "distance": 600, "duration": 90, "type": "keep-right"},
        {"instruction": "You have arrived at your destination", "road": "Destination", "distance": 0, "duration": 0, "type": "arrive"}
    ]
    
    steps = ManeuverSequenceBuilder.build_sequence(
        steps=raw_maneuvers,
        origin_label="MG Road Metro Station",
        dest_label="Richmond Circle",
        total_distance_m=3050.0,
        travel_mode="car"
    )
    
    assert len(steps) == 5
    assert steps[0].direction_type == "START"
    assert steps[1].direction_type == "TURN_LEFT"
    assert steps[2].direction_type == "ROUNDABOUT"
    assert steps[2].roundabout_exit == 2
    assert steps[3].direction_type == "KEEP_RIGHT"
    assert steps[4].direction_type == "ARRIVE"
    
    for i, s in enumerate(steps):
        assert s.step_num == i + 1
        assert s.total_steps == 5
        assert s.road_name is not None
        assert s.distance_human is not None
        assert s.headline is not None

def test_maneuver_sequence_builder_fallback():
    # When empty list provided, builds realistic multi-step corridor
    steps = ManeuverSequenceBuilder.build_sequence(
        steps=[],
        origin_label="Indiranagar 100ft Road",
        dest_label="Koramangala Sony World Signal",
        total_distance_m=6800.0,
        travel_mode="car"
    )
    assert len(steps) >= 3
    assert steps[0].direction_type == "START"
    assert steps[-1].direction_type == "ARRIVE"
    assert "Indiranagar" in steps[0].headline
    assert "Koramangala" in steps[-1].headline

def test_build_aura_journey_cockpit_html():
    raw_maneuvers = [
        {"instruction": "Head northeast on MG Road", "road": "MG Road", "distance": 500, "duration": 60, "type": "depart"},
        {"instruction": "Turn right onto Church Street", "road": "Church Street", "distance": 1200, "duration": 150, "type": "turn-right"},
        {"instruction": "Arrive at destination", "road": "Destination", "distance": 0, "duration": 0, "type": "arrive"}
    ]
    steps = ManeuverSequenceBuilder.build_sequence(
        steps=raw_maneuvers,
        origin_label="MG Road",
        dest_label="Church Street",
        total_distance_m=1700.0,
        travel_mode="walking"
    )
    
    html = build_aura_journey_cockpit_html(
        origin_name="MG Road",
        dest_name="Church Street",
        travel_mode="walking",
        total_distance_km=1.7,
        total_duration_mins=22.0,
        maneuvers=steps,
        current_step_idx=0,
        aura_stage="NAVIGATING"
    )
    
    assert "aura-journey-root" in html
    assert "Route Journey Pipeline" in html
    assert "View All Pictures" in html
    assert "MG Road" in html
    assert "Church Street" in html
    assert "3D Follow Drone" in html
    assert "Driver POV" in html
    assert "3D Isometric" in html
    assert "Aura" in html
    assert "AURA ACTIONS:" in html
    assert "ENVIRONMENT:" in html
