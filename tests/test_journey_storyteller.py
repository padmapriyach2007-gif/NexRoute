import pytest
from src.journey_storyteller import generate_journey_story, build_journey_story_html, JourneyChapter


def test_generate_journey_story():
    origin = "Tenali"
    destination = "Guntur City Center"
    steps = [
        {"instruction": "Head out on Tenali Main Road", "road": "Tenali Main Road", "distance_m": 800},
        {"instruction": "Turn left onto Tenali - Narakoduru Road", "road": "Tenali - Narakoduru Road", "distance_m": 5400},
        {"instruction": "Turn right onto Guntur Bypass", "road": "Guntur Bypass", "distance_m": 3200},
        {"instruction": "Arrive at destination", "road": "City Center Avenue", "distance_m": 400}
    ]

    chapters = generate_journey_story(
        origin=origin,
        destination=destination,
        steps=steps,
        total_distance_km=9.8,
        total_duration_minutes=18.0,
        travel_mode="Car"
    )

    assert len(chapters) == 4
    assert chapters[0].chapter_num == 1
    assert "Departure" in chapters[0].title
    assert "Tenali" in chapters[0].narrative

    assert chapters[1].chapter_num == 2
    assert "Corridor" in chapters[1].title
    assert "Tenali - Narakoduru Road" in chapters[1].narrative

    assert chapters[-1].chapter_num == 4
    assert "Arrival" in chapters[-1].title
    assert "Guntur City Center" in chapters[-1].narrative


def test_build_journey_story_html():
    origin = "Tenali"
    destination = "Guntur City Center"
    steps = [
        {"instruction": "Head out on Tenali Main Road", "road": "Tenali Main Road", "distance_m": 800},
        {"instruction": "Turn left onto Tenali - Narakoduru Road", "road": "Tenali - Narakoduru Road", "distance_m": 5400}
    ]

    chapters = generate_journey_story(
        origin=origin,
        destination=destination,
        steps=steps,
        total_distance_km=6.2,
        total_duration_minutes=12.0
    )

    html = build_journey_story_html(chapters, origin, destination)
    assert "JOURNEY CHRONICLE: THE TRAVEL STORY" in html
    assert "The Departure" in html
    assert "Tenali" in html
    assert "Guntur City Center" in html
    assert "narrateActiveChapter" in html
    assert "PARALLEL SATELLITE SYNC" in html
    assert "syncChapterWithVehicle" in html


def test_build_journey_story_html_parallel_sync_arrival():
    origin = "Tenali"
    destination = "Guntur City Center"
    steps = [{"instruction": "Arrive", "road": "Main Link", "distance_m": 100}]
    chapters = generate_journey_story(origin, destination, steps, 10.0, 15.0)

    # When user is at final step (checkpoint 7 of 7)
    html = build_journey_story_html(chapters, origin, destination, initial_chapter_idx=3, current_step=6, total_steps=7)
    assert "INITIAL_CHAP = 3" in html
    assert "pathfinder_journey_channel" in html
    assert "PATHFINDER_VEHICLE_UPDATE" in html


def test_generate_friendly_virtual_guide_turns():
    from src.journey_storyteller import generate_friendly_virtual_guide_turns, FriendlyTurnStep
    origin = "Tenali Town"
    destination = "Vignan's Foundation for Science"
    steps = [
        {"instruction": "Head out on route corridor", "road": "Local Corridor", "distance_m": 40.0},
        {"instruction": "Turn right onto connected road", "road": "Local Corridor", "distance_m": 100.0},
        {"instruction": "Turn left onto connected road", "road": "Local Corridor", "distance_m": 260.0},
        {"instruction": "Turn right onto Tenali - Mangalagiri Road", "road": "Tenali - Mangalagiri Road", "distance_m": 530.0},
        {"instruction": "Continue straight on Tenali - Narakoduru Road", "road": "Tenali - Narakoduru Road", "distance_m": 10620.0},
        {"instruction": "Arrive at destination (terminal)", "road": "Local Corridor", "distance_m": 0.0}
    ]

    friendly_turns = generate_friendly_virtual_guide_turns(
        steps=steps,
        origin=origin,
        destination=destination,
        travel_mode="Car"
    )

    assert len(friendly_turns) == 6
    assert isinstance(friendly_turns[0], FriendlyTurnStep)

    # 1. Step 1: Start out with warm greeting
    assert friendly_turns[0].direction_type == "START"
    assert "Start Out" in friendly_turns[0].action_headline
    assert "Hello traveler" in friendly_turns[0].virtual_guide_speech
    assert "meters" in friendly_turns[0].distance_human

    # 2. Step 2: Right turn with human advice
    assert friendly_turns[1].direction_type == "RIGHT"
    assert "Turn Right" in friendly_turns[1].action_headline
    assert "right" in friendly_turns[1].virtual_guide_speech.lower()

    # 3. Step 3: Left turn
    assert friendly_turns[2].direction_type == "LEFT"
    assert "Turn Left" in friendly_turns[2].action_headline

    # 4. Step 5: Long cruising stretch on highway with landmark hint
    assert friendly_turns[4].direction_type == "STRAIGHT"
    assert "10.6 kilometers" in friendly_turns[4].distance_human
    assert "straight" in friendly_turns[4].action_headline.lower()

    # 5. Final Step: Safe arrival celebration
    assert friendly_turns[-1].direction_type == "ARRIVE"
    assert "Safely Arrive" in friendly_turns[-1].action_headline
    assert "Hooray" in friendly_turns[-1].virtual_guide_speech


def test_build_virtual_guide_turns_html():
    from src.journey_storyteller import generate_friendly_virtual_guide_turns, build_virtual_guide_turns_html
    origin = "Tenali Town"
    destination = "Vignan's Foundation for Science"
    steps = [
        {"instruction": "Head out on route corridor", "road": "Local Corridor", "distance_m": 40.0},
        {"instruction": "Turn right onto connected road", "road": "Local Corridor", "distance_m": 100.0},
        {"instruction": "Arrive at destination", "road": "Local Corridor", "distance_m": 0.0}
    ]

    friendly_turns = generate_friendly_virtual_guide_turns(steps, origin, destination, "Walk")
    html = build_virtual_guide_turns_html(friendly_turns, origin, destination, "Walk")

    assert "VIRTUAL GUIDE: STEP-BY-STEP FRIENDLY ROUTE STORY" in html
    assert "FOR EVERY TRAVELER • LISTEN & FOLLOW" in html
    assert "speakActiveTurn" in html
    assert "speakAllTurnsInOrder" in html
    assert "WHAT TO LOOK FOR" in html
    assert "YOUR VIRTUAL GUIDE SAYS" in html
    assert "👨‍✈️" in html
    # Accessible Turn & Crossing Assistance for disabled individuals
    assert "ACCESSIBILITY & CROSSING ASSIST" in html
    assert "Move Virtual Guide: Turn & Cross" in html
    assert "animateVirtualGuideDemonstration" in html
    assert "pedestrian-crosswalk" in html
    assert "virtual-guide-actor" in html
    assert "♿ RAMP" in html
    assert friendly_turns[0].accessible_guidance != ""
    assert friendly_turns[0].tactile_crossing_note != ""


