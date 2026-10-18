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


def test_virtual_runner_process_banner_checkmarks():
    origin = "Place A"
    dest = "Place B"
    polyline = [
        (16.241, 80.584),  # Place A
        (16.245, 80.575),  # Place I
        (16.255, 80.545),  # Place J
        (16.236, 80.552),  # Place K
        (16.233, 80.550)   # Place B
    ]
    milestones = extract_journey_game_milestones(origin, dest, polyline, total_distance_km=15.0)
    assert len(milestones) >= 3

    # When user is at step 1 (Place I crossed Place A):
    html = build_game_journey_html(milestones, current_step=1, traveler_avatar="runner")
    assert "VIRTUAL RUNNER & ROUTE PROCESS BANNER" in html
    assert "runnerStride" in html
    assert "checkmarkPop" in html
    assert "🏃‍♂️" in html
    assert "CHECKED ✅" in html
    assert "RUNNING HERE 🏃‍♂️" in html
    # Verify voice guidance mentions the virtual boy standing/running and stop crossing shoutout
    assert any("virtual boy" in m.voice_announcement.lower() or "runner" in m.voice_announcement.lower() for m in milestones)
    assert any("he crossed stop" in m.voice_announcement.lower() for m in milestones)


def test_mode_adaptive_speed_and_virtual_boy_walk():
    origin = "Tenali"
    dest = "Vignan University"
    polyline = [(16.241, 80.584), (16.233, 80.550)]
    milestones = extract_journey_game_milestones(origin, dest, polyline, total_distance_km=14.0)

    # 1. Test WALK mode: Virtual Boy Walking at 4.8 km/h
    walk_html = build_game_journey_html(milestones, current_step=0, traveler_avatar="walk")
    assert "Virtual Boy Walking" in walk_html
    assert "4.8" in walk_html
    assert "🚶‍♂️" in walk_html
    assert "WALKING HERE 🚶‍♂️" in walk_html

    # 2. Test CAR mode: Fast driving at 55 km/h
    car_html = build_game_journey_html(milestones, current_step=0, traveler_avatar="car")
    assert "Virtual Car Companion" in car_html
    assert "55" in car_html
    assert "🚗" in car_html
    assert "DRIVING HERE 🚗" in car_html


def test_round_trip_return_journey_and_voice_shoutouts():
    origin = "Tenali"
    dest = "Vignan University"
    polyline = [(16.241, 80.584), (16.233, 80.550)]
    milestones = extract_journey_game_milestones(origin, dest, polyline, total_distance_km=14.0)

    html = build_game_journey_html(milestones, current_step=0, traveler_avatar="boy")
    # Verify return journey logic & functions
    assert "startReturnJourney" in html
    assert "scheduleNextReturnTransitStep" in html
    assert "executeReturnStep" in html
    assert "Return Trip" in html
    # Verify stop crossing AI voice announcements
    assert "You and the virtual companion have crossed Stop" in html
    assert "Safe return completed" in html


def test_create_return_milestones_symmetrical_order():
    from src.game_journey_stepper import create_return_milestones
    origin = "Tenali"
    dest = "Guntur City Center"
    polyline = [
        (16.241, 80.584),  # Tenali
        (16.245, 80.575),  # Stop 1
        (16.255, 80.545),  # Stop 2
        (16.306, 80.436)   # Guntur
    ]
    fwd_milestones = extract_journey_game_milestones(origin, dest, polyline, total_distance_km=25.0)
    ret_milestones = create_return_milestones(fwd_milestones)

    # 1. Total counts must be equal
    assert len(ret_milestones) == len(fwd_milestones)

    # 2. Return milestone 0 must be the goal destination
    assert ret_milestones[0].milestone_type == "START"
    assert "Guntur" in ret_milestones[0].label
    assert ret_milestones[0].distance_from_start_km == 0.0

    # 3. Final return milestone must be the initial start origin
    assert ret_milestones[-1].milestone_type == "DESTINATION"
    assert "Tenali" in ret_milestones[-1].label
    assert ret_milestones[-1].distance_from_start_km == fwd_milestones[-1].distance_from_start_km

    # 4. Voice announcements reflect return journey in the exact same way
    assert "Starting return journey" in ret_milestones[0].voice_announcement or "return start point" in ret_milestones[0].voice_announcement
    assert "return journey" in ret_milestones[1].voice_announcement
    assert "initial destination" in ret_milestones[-1].voice_announcement


def test_goal_to_start_direction_switcher_html():
    origin = "Tenali"
    dest = "Guntur"
    polyline = [(16.241, 80.584), (16.306, 80.436)]
    milestones = extract_journey_game_milestones(origin, dest, polyline, total_distance_km=25.0)

    html = build_game_journey_html(milestones, current_step=0, traveler_avatar="car")
    # Verify direction switcher pills
    assert "btn-dir-forward" in html
    assert "btn-dir-return" in html
    assert "setJourneyDirection" in html
    assert "Start ➔ Goal" in html
    assert "Goal ➔ Start" in html
    # Verify both milestone sets are serialized for seamless client-side switching
    assert "FORWARD_MILESTONES" in html
    assert "RETURN_MILESTONES" in html
    assert "renderTrackNodes" in html


def test_real_user_sensor_lockstep_and_traffic_stop():
    origin = "Hyderabad"
    dest = "Tenali Junction"
    polyline = [(17.385, 78.486), (16.233, 80.648)]
    milestones = extract_journey_game_milestones(origin, dest, polyline, total_distance_km=300.0)

    html = build_game_journey_html(milestones, current_step=0, traveler_avatar="car")
    # 1. Verify simulation and sensor interaction controls
    assert "simulateTrafficStop" in html
    assert "simulateUserMoving" in html
    assert "simulateCrossNextStop" in html
    assert "Traffic Stop (0 km/h)" in html
    assert "Move in Parallel" in html
    assert "Cross Next Stop" in html
    # 2. Verify traffic stopped state displays
    assert "STOPPED IN TRAFFIC" in html
    assert "USER STOPPED (0.0 km/h)" in html
    # 3. Verify cross-component sensor command listener
    assert "PATHFINDER_SENSOR_COMMAND" in html


def test_real_place_names_between_start_and_destination_instead_of_corridor():
    """
    Direct regression test ensuring place names between start and end are real geographic
    landmarks/localities (e.g. Vadlamudi, Angalakuduru, Sangam Jagarlamudi, Chenchupet)
    and NEVER generic 'Corridor', 'Waypoint Corridor', or 'Corridor Checkpoint'.
    """
    origin = "📍 Current Location"
    dest = "Tenali Junction"
    # Polyline from Vignan/Vadlamudi to Tenali Junction
    polyline = [
        (16.2335, 80.5505),  # Starting point near Vignan
        (16.2385, 80.5420),  # Vadlamudi Hub
        (16.2350, 80.5050),  # Sangam Jagarlamudi
        (16.2280, 80.6220),  # Angalakuduru
        (16.2450, 80.6350),  # Chenchupet
        (16.2395, 80.6465)   # Tenali Junction
    ]
    # Simulate steps that have generic or corridor road names
    steps = [
        {"step_num": 1, "instruction": "Head out on main road", "road": "Local Corridor", "distance_m": 1200},
        {"step_num": 2, "instruction": "Continue straight on road", "road": "Corridor", "distance_m": 3500},
        {"step_num": 3, "instruction": "Follow connected road", "road": "Connected Road", "distance_m": 3000},
        {"step_num": 4, "instruction": "Turn right onto Angalakuduru Link", "road": "Angalakuduru Link", "distance_m": 2000},
        {"step_num": 5, "instruction": "Arrive at Tenali Junction", "road": "Station Road", "distance_m": 500}
    ]

    milestones = extract_journey_game_milestones(origin, dest, polyline, steps=steps, total_distance_km=10.2)

    assert len(milestones) >= 4
    assert milestones[0].label == "Starting Point"
    assert milestones[-1].label == "Tenali Junction"

    # Strictly verify NO milestone contains "corridor"
    for m in milestones:
        assert "corridor" not in m.label.lower(), f"Milestone label '{m.label}' must not contain 'corridor'"
        assert "waypoint corridor" not in m.label.lower()
        assert "corridor checkpoint" not in m.label.lower()

    # Verify that intermediate waypoints have real geographic place names
    intermediate_labels = [m.label for m in milestones[1:-1]]
    assert len(intermediate_labels) >= 2
    # Should resolve to real localities like Angalakuduru, Vadlamudi, Sangam Jagarlamudi, Chenchupet
    recognized_localities = {"Angalakuduru", "Vadlamudi Hub", "Vadlamudi Center", "Sangam Jagarlamudi", "Chenchupet", "Narakoduru Junction", "Morrispet", "Tenali Market"}
    matches = [label for label in intermediate_labels if any(rec in label for rec in recognized_localities)]
    assert len(matches) >= 2, f"Expected real locality matches in {intermediate_labels}"

    # Also verify the rendered HTML track displays these real place names
    html = build_game_journey_html(milestones, current_step=0, traveler_avatar="car")
    assert "Waypoint Corridor" not in html
    assert "Corridor Checkpoint" not in html
    for match in matches:
        assert match in html

