import pytest
from src.pathfinder_chatbot import PathfinderChatbot
from src.aura_assistant_handlers import AuraIntentType, AuraIntentClassifier

@pytest.fixture
def bot():
    b = PathfinderChatbot()
    b.reset_conversation()
    return b

def test_greeting(bot):
    res = bot.answer("Hello Aura!")
    assert res and "response" in res
    assert "Aura" in res["response"] or "A.U.R.A." in res["response"] or "travel assistant" in res["response"]
    assert "route" in res["response"].lower() or "help" in res["response"].lower()

def test_how_are_you(bot):
    res = bot.answer("How are you today?")
    assert res and "response" in res
    assert any(w in res["response"].lower() for w in ["great", "good", "doing", "ready", "assist"])

def test_who_are_you(bot):
    res = bot.answer("Who are you?")
    assert res and "response" in res
    assert "Aura" in res["response"] or "A.U.R.A." in res["response"]
    assert "travel" in res["response"].lower() or "route" in res["response"].lower()

def test_what_can_you_do(bot):
    res = bot.answer("What can you do?")
    assert res and "response" in res
    # Must list capabilities
    resp = res["response"].lower()
    assert "navigation" in resp or "route" in resp or "trips" in resp
    assert "speed" in resp or "tolls" in resp or "places" in resp or "travel" in resp

def test_pack_for_3day_trip(bot):
    res = bot.answer("What should I pack for a 3-day road trip?")
    assert res and "response" in res
    resp = res["response"].lower()
    assert "pack" in resp or "essentials" in resp or "kit" in resp
    assert "clothes" in resp or "charg" in resp or "medic" in resp or "documents" in resp

def test_avoid_getting_lost(bot):
    res = bot.answer("How can I avoid getting lost while travelling?")
    assert res and "response" in res
    resp = res["response"].lower()
    assert "offline" in resp or "map" in resp
    assert "pin" in resp or "landmark" in resp or "card" in resp

def test_bus_and_train_difference(bot):
    res = bot.answer("What is the difference between travelling by bus and train?")
    assert res and "response" in res
    resp = res["response"].lower()
    assert "train" in resp and "bus" in resp
    assert "comfort" in resp or "room" in resp or "berth" in resp or "traffic" in resp

def test_fastest_vs_shortest_conceptual(bot):
    res = bot.answer("Explain the difference between fastest route and shortest route.")
    assert res and "response" in res
    resp = res["response"].lower()
    assert "fastest" in resp and "shortest" in resp
    assert "time" in resp
    assert "distance" in resp or "kilometers" in resp

def test_route_options_vijayawada_to_hyderabad(bot):
    res = bot.answer("I want to travel from Vijayawada to Hyderabad. What are my options?")
    assert res and "response" in res
    resp = res["response"].lower()
    assert "vijayawada" in resp and "hyderabad" in resp
    assert "nh65" in resp or "km" in resp or "route" in resp

def test_halfway_restaurants(bot):
    bot.conv_manager.current_origin = "Vijayawada"
    bot.conv_manager.current_destination = "Hyderabad"
    res = bot.answer("Find restaurants halfway between Vijayawada and Hyderabad.")
    assert res and "response" in res
    resp = res["response"].lower()
    assert "suryapet" in resp
    assert "7 food court" in resp or "grand" in resp or "minerva" in resp or "highway" in resp

def test_ev_fast_chargers(bot):
    res = bot.answer("Where are the nearest EV fast chargers?")
    assert res and "response" in res
    resp = res["response"].lower()
    assert "tata" in resp or "ccs2" in resp or "kw" in resp or "charger" in resp

def test_24_7_hospital(bot):
    res = bot.answer("Find a 24/7 hospital nearby.")
    assert res and "response" in res
    resp = res["response"].lower()
    assert "hospital" in resp or "emergency" in resp or "aiims" in resp or "108" in resp

def test_estimate_fuel_cost(bot):
    bot.conv_manager.current_origin = "Vijayawada"
    bot.conv_manager.current_destination = "Hyderabad"
    res = bot.answer("Estimate my fuel cost for this journey.")
    assert res and "response" in res
    resp = res["response"].lower()
    assert "fuel" in resp or "petrol" in resp
    assert "₹" in res["response"] or "rs" in resp

def test_translate_to_telugu(bot):
    res = bot.answer("Can you translate this sentence into Telugu: 'Where is the nearest petrol station?'")
    assert res and "response" in res
    assert "పెట్రోల్" in res["response"] or "Daggarloni" in res["response"]

def test_ai_simple_terms(bot):
    res = bot.answer("What is artificial intelligence in simple terms?")
    assert res and "response" in res
    resp = res["response"].lower()
    assert "intelligence" in resp or "learn" in resp or "data" in resp
    assert "task" in resp or "smart" in resp

def test_araku_itinerary(bot):
    res = bot.answer("Plan a 2-day weekend trip from Vijayawada to Araku Valley.")
    assert res and "response" in res
    resp = res["response"].lower()
    assert "day 1" in resp and "day 2" in resp
    assert "borra" in resp or "coffee" in resp or "chaparai" in resp or "caves" in resp

def test_multiturn_flow(bot):
    # Step 1: User indicates destination
    r1 = bot.answer("I want to travel to Hyderabad.")
    assert r1 and "response" in r1
    assert "hyderabad" in r1["response"].lower() or bot.conv_manager.current_destination == "Hyderabad"
    assert bot.conv_manager.pending_question in ["origin_and_mode", "origin", "travel_mode"]

    # Step 2: User provides origin and mode
    r2 = bot.answer("From Vijayawada by car.")
    assert r2 and "response" in r2
    assert "vijayawada" in r2["response"].lower()
    assert "hyderabad" in r2["response"].lower()
    assert bot.conv_manager.current_origin == "Vijayawada"
    assert bot.conv_manager.travel_mode == "car"
    assert bot.conv_manager.pending_question == "route_choice"

    # Step 3: User confirms route choice
    r3 = bot.answer("Show me the fastest.")
    assert r3 and "response" in r3
    assert "fastest" in r3["response"].lower() or "route 1" in r3["response"].lower()
    assert r3.get("action", {}).get("type") == "calculate_route"

    # Step 4: User asks for halfway restaurant without repeating start/dest
    r4 = bot.answer("Find a restaurant halfway.")
    assert r4 and "response" in r4
    assert "suryapet" in r4["response"].lower()

    # Step 5: User asks for fuel cost estimation based on active context
    r5 = bot.answer("Estimate my fuel cost.")
    assert r5 and "response" in r5
    assert "petrol" in r5["response"].lower()
    assert "₹" in r5["response"]
