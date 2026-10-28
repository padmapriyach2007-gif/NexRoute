"""
Comprehensive Test Suite: Universal Chatbot Answering System
Verifies that A.U.R.A. and PathfinderChatbot accurately and reliably answer
any kind of question: general knowledge, travel planning, mathematics,
science/physics, coding, and live grounded knowledge.
"""

import pytest
from src.pathfinder_chatbot import PathfinderChatbot
from src.map_service import MapService
from src.ai_assistant_engine import GroundingEngine


@pytest.fixture
def bot():
    ms = MapService()
    chatbot = PathfinderChatbot(map_service=ms)
    chatbot.reset_conversation()
    return chatbot


# =============================================================================
# 1. GENERAL KNOWLEDGE & WORLD/STATE GEOGRAPHY
# =============================================================================

def test_capital_of_france(bot):
    res = bot.answer("What is the capital of France?")
    assert "Paris" in res["response"]
    assert "badge" in res


def test_capital_of_germany(bot):
    res = bot.answer("What is the capital of Germany?")
    assert "Berlin" in res["response"]


def test_capital_of_united_states(bot):
    res = bot.answer("What is the capital of USA?")
    assert "Washington, D.C." in res["response"]


def test_capital_of_india(bot):
    res = bot.answer("What is the capital of India?")
    assert "New Delhi" in res["response"]


def test_capital_of_andhra_pradesh(bot):
    res = bot.answer("What is the capital of Andhra Pradesh?")
    assert "Amaravati" in res["response"]


def test_capital_of_karnataka(bot):
    res = bot.answer("What is the capital of Karnataka?")
    assert "Bengaluru" in res["response"] or "Bangalore" in res["response"]


def test_capital_of_japan_exact_compatibility(bot):
    res = bot.answer("What is the capital of Japan?")
    assert "Tokyo" in res["response"]
    assert "Haneda Airport" not in res["response"]


# =============================================================================
# 2. TRAVEL & TRANSIT ADVICE ACROSS DESTINATIONS
# =============================================================================

def test_travel_to_paris(bot):
    res = bot.answer("How do I travel to Paris?")
    assert "Charles de Gaulle" in res["response"] or "CDG" in res["response"]
    assert "Schengen" in res["response"]


def test_travel_to_london(bot):
    res = bot.answer("How to reach London?")
    assert "Heathrow" in res["response"] or "Oyster" in res["response"] or "Tube" in res["response"]


def test_travel_to_new_york(bot):
    res = bot.answer("How do I go to New York?")
    assert "JFK" in res["response"] or "Subway" in res["response"] or "OMNY" in res["response"]


def test_travel_to_dubai(bot):
    res = bot.answer("How to go to Dubai?")
    assert "Burj Khalifa" in res["response"] or "Metro" in res["response"] or "Nol" in res["response"]


def test_travel_to_goa(bot):
    res = bot.answer("How to travel to Goa?")
    assert "MOPA" in res["response"] or "Dabolim" in res["response"] or "Madgaon" in res["response"] or "beaches" in res["response"].lower()


def test_travel_to_tirupati(bot):
    res = bot.answer("How to reach Tirupati?")
    assert "Tirumala" in res["response"] or "Ghat Road" in res["response"] or "TTD" in res["response"]


def test_travel_to_visakhapatnam(bot):
    res = bot.answer("How to go to Visakhapatnam?")
    assert "Beach" in res["response"] or "VTZ" in res["response"] or "Kailasagiri" in res["response"]


# =============================================================================
# 3. TRAVEL EXPERT SYSTEMS (PACKING, BUDGET, SOLO, VISAS, ROAD TRIPS)
# =============================================================================

def test_packing_checklist(bot):
    res = bot.answer("Give me a travel packing checklist")
    assert "passport" in res["response"].lower()
    assert "power bank" in res["response"].lower()
    assert "Roll your clothes" in res["response"] or "packing" in res["response"].lower()


def test_budget_travel_tips(bot):
    res = bot.answer("How to travel on a budget?")
    assert "Shoulder Season" in res["response"] or "budget" in res["response"].lower()
    assert "Public Transit" in res["response"] or "transit" in res["response"].lower()


def test_solo_travel_safety(bot):
    res = bot.answer("Tips for solo travel safety")
    assert "Location Sharing" in res["response"] or "Emergency" in res["response"] or "safe" in res["response"].lower()


def test_international_travel_documents(bot):
    res = bot.answer("What documents do I need for international travel?")
    assert "6 months" in res["response"] or "6-month" in res["response"].lower()
    assert "Visa" in res["response"] or "Insurance" in res["response"]


def test_road_trip_pre_departure_checklist(bot):
    res = bot.answer("Road trip vehicle inspection checklist")
    assert "Tires" in res["response"] or "Fluids" in res["response"] or "Brakes" in res["response"]


# =============================================================================
# 4. SCIENCE, AERODYNAMICS & PHYSICS
# =============================================================================

def test_how_airplanes_fly(bot):
    res = bot.answer("How do airplanes fly?")
    assert "Lift" in res["response"]
    assert "Bernoulli" in res["response"] or "Newton" in res["response"]
    assert "Thrust" in res["response"]


def test_how_gps_works(bot):
    res = bot.answer("How does GPS work?")
    assert "Trilateration" in res["response"]
    assert "Satellite" in res["response"] or "atomic clock" in res["response"].lower()


def test_speed_of_light(bot):
    res = bot.answer("What is the speed of light?")
    assert "299,792,458" in res["response"] or "300,000" in res["response"]


def test_speed_of_sound(bot):
    res = bot.answer("What is the speed of sound?")
    assert "343" in res["response"] or "Mach 1" in res["response"]


def test_acceleration_due_to_gravity(bot):
    res = bot.answer("What is the acceleration due to gravity on Earth?")
    assert "9.8" in res["response"]


def test_dna_structure(bot):
    res = bot.answer("What is the structure of DNA?")
    assert "Double Helix" in res["response"] or "double helix" in res["response"]
    assert "Adenine" in res["response"] or "Thymine" in res["response"]


def test_inventor_of_telephone(bot):
    res = bot.answer("Who invented the telephone?")
    assert "Alexander Graham Bell" in res["response"]


def test_inventor_of_world_wide_web(bot):
    res = bot.answer("Who invented the World Wide Web?")
    assert "Tim Berners-Lee" in res["response"]


# =============================================================================
# 5. MATHEMATICS & UNIT CONVERSIONS
# =============================================================================

def test_linear_equation_solver(bot):
    res = bot.answer("Solve 2x + 4 = 10")
    assert "x = 3" in res["response"]


def test_linear_equation_solver_subtraction(bot):
    res = bot.answer("Solve 3x - 5 = 16")
    assert "x = 7" in res["response"]


def test_percentage_calculation(bot):
    res = bot.answer("What is 15% of 200?")
    assert "30" in res["response"]


def test_unit_conversion_km_to_miles(bot):
    res = bot.answer("Convert 100 km to miles")
    assert "62.137" in res["response"] or "miles" in res["response"]


def test_unit_conversion_celsius_to_fahrenheit(bot):
    res = bot.answer("Convert 100 C to Fahrenheit")
    assert "212" in res["response"]


# =============================================================================
# 6. COMPUTER SCIENCE & CODING HELPERS
# =============================================================================

def test_reverse_a_string_in_python(bot):
    res = bot.answer("How to reverse a string in python?")
    assert "[::-1]" in res["response"]


def test_palindrome_check_python(bot):
    res = bot.answer("How to check palindrome in python?")
    assert "is_palindrome" in res["response"] or "[::-1]" in res["response"]


def test_fibonacci_sequence_python(bot):
    res = bot.answer("Show me fibonacci in python")
    assert "fibonacci" in res["response"].lower()
    assert "seq" in res["response"] or "append" in res["response"]


def test_http_vs_https(bot):
    res = bot.answer("What is the difference between http and https?")
    assert "TLS" in res["response"] or "SSL" in res["response"]
    assert "443" in res["response"]
