"""
Comprehensive Test Suite for NextRoute Advanced Multilingual AI Travel Copilot.

Tests:
1. Ground-Truth NextRoute Application Knowledge (RAG).
2. General Travel Planning & Budget Estimation.
3. Travel Duration & Distance Calculations.
4. General Travel QA.
5. Multilingual Resolution & Native Script Output (en, te, hi, ta, kn, ml, bn, mr).
6. Multi-turn Follow-up Context Memory.
"""

import pytest
from src.pathfinder_chatbot import PathfinderChatbot
from src.nextroute_knowledge_rag import (
    NextRouteRAGRetriever,
    GeneralTravelPlanningEngine,
    TravelDurationEstimator,
    GeneralTravelQAEngine,
    resolve_target_language
)


@pytest.fixture
def chatbot():
    bot = PathfinderChatbot()
    return bot


def test_language_priority_resolution():
    """Verifies that explicit language query takes 1st priority, then app_lang, then en."""
    # 1st: Explicit query request takes absolute priority
    assert resolve_target_language("How do I save a trip? Answer in Telugu", app_lang="hi") == "te"
    assert resolve_target_language("Tell me in Hindi please", app_lang="en") == "hi"
    assert resolve_target_language("Explain in Tamil", app_lang="te") == "ta"
    assert resolve_target_language("Give this in Kannada", app_lang="en") == "kn"
    assert resolve_target_language("Reply in Malayalam", app_lang="en") == "ml"
    assert resolve_target_language("Answer in Bengali", app_lang="en") == "bn"
    assert resolve_target_language("Explain in Marathi", app_lang="en") == "mr"
    assert resolve_target_language("Can you explain in English?", app_lang="te") == "en"

    # Native script cues
    assert resolve_target_language("తెలుగులో చెప్పండి", app_lang="en") == "te"
    assert resolve_target_language("हिंदी में बताएं", app_lang="en") == "hi"

    # 2nd: Selected application language when no explicit language in query
    assert resolve_target_language("How do I add a stop?", app_lang="te") == "te"
    assert resolve_target_language("How do I add a stop?", app_lang="hi") == "hi"
    assert resolve_target_language("How do I add a stop?", app_lang="ta") == "ta"

    # 3rd: Default fallback is English
    assert resolve_target_language("How do I add a stop?", app_lang=None) == "en"
    assert resolve_target_language("How do I add a stop?", app_lang="") == "en"


def test_nextroute_application_knowledge(chatbot):
    """Ensures chatbot answers NextRoute questions accurately without hallucinating."""
    ctx = {"language": "en"}

    # Shortest route
    r1 = chatbot.answer("How can I find the shortest route in NextRoute?", context=ctx)
    assert "shortest" in r1["response"].lower()
    assert "navigation" in r1["response"].lower()

    # Change vehicle mode
    r2 = chatbot.answer("How do I change vehicle mode?", context=ctx)
    assert "mode" in r2["response"].lower()
    assert ("car" in r2["response"].lower() or "transport" in r2["response"].lower())

    # Save a trip
    r3 = chatbot.answer("Can I save my trip in NextRoute?", context=ctx)
    assert "my trips" in r3["response"].lower() or "save" in r3["response"].lower()

    # Add multiple stops
    r4 = chatbot.answer("How do I add a stop to my route?", context=ctx)
    assert "stop" in r4["response"].lower() or "waypoint" in r4["response"].lower()

    # Avoid tolls
    r5 = chatbot.answer("How does avoid tolls work in NextRoute?", context=ctx)
    assert "toll" in r5["response"].lower()

    # Hotel booking
    r6 = chatbot.answer("Can NextRoute book hotels?", context=ctx)
    assert "hotel" in r6["response"].lower()


def test_multilingual_app_knowledge(chatbot):
    """Ensures application answers render in native script for Telugu and Hindi."""
    ctx_te = {"language": "te"}
    r_te = chatbot.answer("How can I find the shortest route?", context=ctx_te)
    # Check for Telugu script characters
    assert any('\u0c00' <= char <= '\u0c7f' for char in r_te["response"])

    ctx_hi = {"language": "hi"}
    r_hi = chatbot.answer("How do I change vehicle mode?", context=ctx_hi)
    # Check for Devanagari script characters
    assert any('\u0900' <= char <= '\u097f' for char in r_hi["response"])


def test_general_travel_planning(chatbot):
    """Tests day-wise itinerary and budget estimation for popular destinations."""
    ctx = {"language": "en"}

    # 3-day trip to Hyderabad
    r_hyd = chatbot.answer("Plan a 3-day trip to Hyderabad", context=ctx)
    assert "hyderabad" in r_hyd["response"].lower()
    assert "day 1" in r_hyd["response"].lower()
    assert "day 2" in r_hyd["response"].lower()
    assert "day 3" in r_hyd["response"].lower()

    # Trip to Goa budget
    r_goa = chatbot.answer("How much does a 5-day trip to Goa cost?", context=ctx)
    assert "goa" in r_goa["response"].lower()
    assert "₹" in r_goa["response"]
    assert "accommodation" in r_goa["response"].lower() or "stay" in r_goa["response"].lower()

    # Manali within ₹15,000 budget
    r_manali = chatbot.answer("Plan a trip to Manali within ₹15,000", context=ctx)
    assert "manali" in r_manali["response"].lower()
    assert "15,000" in r_manali["response"] or "15000" in r_manali["response"]


def test_travel_duration_estimator(chatbot):
    """Tests realistic road vs train duration calculation between known cities."""
    ctx = {"language": "en"}
    r_dur = chatbot.answer("How long does it take from Vijayawada to Hyderabad?", context=ctx)
    assert "vijayawada" in r_dur["response"].lower()
    assert "hyderabad" in r_dur["response"].lower()
    assert "driving" in r_dur["response"].lower() or "car" in r_dur["response"].lower()
    assert "train" in r_dur["response"].lower()


def test_general_travel_qa(chatbot):
    """Tests general travel queries like documents, money saving, transit, and sights."""
    ctx = {"language": "en"}

    r_doc = chatbot.answer("What documents are needed for international travel?", context=ctx)
    assert "passport" in r_doc["response"].lower()
    assert "visa" in r_doc["response"].lower()

    r_save = chatbot.answer("How to save money while traveling?", context=ctx)
    assert "advance" in r_save["response"].lower() or "transport" in r_save["response"].lower()

    r_taj = chatbot.answer("How much time is enough to visit the Taj Mahal?", context=ctx)
    assert "2" in r_taj["response"] and "3" in r_taj["response"]


def test_multi_turn_context_memory(chatbot):
    """Tests multi-turn context awareness (destination persistence, budget follow-up, language switch)."""
    ctx = {"language": "en"}

    # Turn 1: Destination planning
    r1 = chatbot.answer("Plan a trip to Goa", context=ctx)
    assert "goa" in r1["response"].lower()

    # Turn 2: Follow-up cost query without naming Goa
    r2 = chatbot.answer("What will it cost?", context=ctx)
    assert "goa" in r2["response"].lower()
    assert "₹" in r2["response"]

    # Turn 3: Budget reduction follow-up
    r3 = chatbot.answer("Make it cheaper", context=ctx)
    assert "goa" in r3["response"].lower()
    assert "budget" in r3["response"].lower() or "hostel" in r3["response"].lower() or "cheaper" in r3["response"].lower()

    # Turn 4: Language switch to Telugu
    r4 = chatbot.answer("Answer in Telugu", context=ctx)
    assert any('\u0c00' <= char <= '\u0c7f' for char in r4["response"])
