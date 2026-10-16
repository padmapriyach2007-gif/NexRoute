import pytest
from src.game_journey_stepper import extract_journey_game_milestones, build_game_journey_html, clean_place_name


def test_clean_place_name():
    assert clean_place_name("📍 Tenali, Andhra Pradesh") == "Tenali"
    assert clean_place_name("🏁 Vignan University (16.2335, 80.5505)") == "Vignan University"
    assert clean_place_name("📍 Current Location") == "Starting Point"


def test_extract_journey_game_milestones_tenali_to_vignan():
    origin = "Tenali"
    dest = "Vignan University"
    polyline = [
        (16.241, 80.584),  # Tenali
        (16.245, 80.575),  # Angalakuduru area
        (16.255, 80.545),  # Tenali - Narakoduru Road
        (16.236, 80.552),  # Vadlamudi
        (16.233, 80.550)   # Vignan
    ]
    steps = [
        {"instruction": "Head out from Tenali", "road": "Tenali Main Road", "distance_m": 800},
        {"instruction": "Cross Angalakuduru", "road": "Angalakuduru Link", "distance_m": 2500},
        {"instruction": "Turn left onto Tenali - Narakoduru Road", "road": "Tenali - Narakoduru Road", "distance_m": 4500},
        {"instruction": "Arrive at Vignan University", "road": "Campus Avenue", "distance_m": 500}
    ]

    milestones = extract_journey_game_milestones(origin, dest, polyline, steps, total_distance_km=8.3)
    assert len(milestones) >= 3
    assert milestones[0].milestone_type == "START"
    assert "Tenali" in milestones[0].label
    assert milestones[-1].milestone_type == "DESTINATION"
    assert "Vignan" in milestones[-1].label

    # Check intermediate milestones
    intermediate = [m for m in milestones if m.milestone_type == "WAYPOINT"]
    assert len(intermediate) >= 1
    assert any("Angalakuduru" in m.label or "Narakoduru" in m.label for m in intermediate)


def test_build_game_journey_html_renders():
    origin = "Tenali"
    dest = "Vignan University"
    polyline = [(16.241, 80.584), (16.233, 80.550)]
    milestones = extract_journey_game_milestones(origin, dest, polyline, total_distance_km=14.0)
    
    html = build_game_journey_html(milestones, current_step=1, traveler_avatar="boy")
    assert "TRAVEL JOURNEY GAME PROGRESSION" in html
    assert "Tenali" in html
    assert "Vignan University" in html
    assert "speakGameStep" in html


def test_detect_crossed_milestones():
    from src.game_journey_stepper import detect_crossed_milestones
    origin = "Tenali"
    dest = "Vignan University"
    polyline = [
        (16.241, 80.584),  # Tenali
        (16.245, 80.575),  # Angalakuduru
        (16.255, 80.545),  # Narakoduru
        (16.233, 80.550)   # Vignan
    ]
    milestones = extract_journey_game_milestones(origin, dest, polyline, total_distance_km=10.0)

    # 1. User is at start (Tenali)
    step_0, crossed_0, desc_0 = detect_crossed_milestones(
        user_coords=(16.241, 80.584),
        current_step=0,
        milestones=milestones,
        polyline=polyline
    )
    assert step_0 == 0
    assert crossed_0 is None
    assert "Tenali" in desc_0

    # 2. User travels and reaches/crosses Angalakuduru (milestones[1])
    target_m1 = milestones[1]
    step_1, crossed_1, desc_1 = detect_crossed_milestones(
        user_coords=(target_m1.lat, target_m1.lon),
        current_step=0,
        milestones=milestones,
        polyline=polyline
    )
    assert step_1 == 1
    assert crossed_1 is not None
    assert crossed_1.label == target_m1.label
    assert "Crossed" in desc_1

    # 3. User travels further to destination
    final_m = milestones[-1]
    step_final, crossed_final, desc_final = detect_crossed_milestones(
        user_coords=(final_m.lat, final_m.lon),
        current_step=1,
        milestones=milestones,
        polyline=polyline
    )
    assert step_final == len(milestones) - 1
    assert crossed_final is not None
    assert "Arrived at Destination" in desc_final

