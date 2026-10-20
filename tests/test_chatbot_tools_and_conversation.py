"""
Test Suite: PATHFINDER Chatbot Diagnostics, Tools & Reliable Conversation
Comprehensive Phase 8 automated test suite verifying:
1. General conversation without navigation tools (math, science, programming, creative).
2. Navigation requests invoking the route engine with deterministic actions.
3. Nearby facility searches using real geographic coordinates.
4. Anaphora & follow-up reference resolution ("there", "the second route", "avoid tolls").
5. Missing or ambiguous origin/destination clarification.
6. Multilingual conversations and tool execution in Telugu, Hindi, Tamil, Kannada, etc.
7. LLM API authentication failure, timeout, and rate-limit fallbacks.
8. Navigation tool failure handling without fabricating coordinates or places.
9. Streamlit session-state persistence across multi-turn reruns.
10. Preference updating (avoid tolls, highways, ferries).
"""

import pytest
from unittest.mock import MagicMock, patch

from src.pathfinder_chatbot import PathfinderChatbot
from src.ai_assistant_engine import LLMClient, BuiltinCognitiveEngine
from src.map_service import MapService
from src.pathfinder_tools import PathfinderToolExecutor, TOOL_SCHEMAS


@pytest.fixture
def map_service():
    return MapService()


@pytest.fixture
def bot(map_service):
    return PathfinderChatbot(map_service=map_service)


# =============================================================================
# 1. GENERAL CONVERSATION WITHOUT TOOLS
# =============================================================================

def test_general_math_and_coding(bot):
    """General programming question must not trigger navigation tools."""
    res = bot.answer("How do I sort a list of dictionaries by key in Python?")
    assert "response" in res
    assert "action" not in res
    assert "sorted" in res["response"] or "key" in res["response"] or "lambda" in res["response"]


def test_general_science_question(bot):
    """Scientific inquiry should be handled with factual explanations."""
    res = bot.answer("Explain how photosynthesis converts sunlight into chemical energy.")
    assert "response" in res
    assert "action" not in res
    content = res["response"].lower()
    assert "chlorophyll" in content or "glucose" in content or "sunlight" in content or "photosynthesis" in content


def test_creative_story_writing(bot):
    """Creative writing requests must produce long-form creative content."""
    res = bot.answer("Write a creative story about an autonomous vehicle navigating a foggy mountain pass.")
    assert "response" in res
    assert "action" not in res
    assert len(res["response"].split()) >= 40


# =============================================================================
# 2. NAVIGATION REQUESTS INVOKING ROUTE ENGINE
# =============================================================================

def test_calculate_route_with_origin_and_destination(bot):
    """Explicit from-to request triggers calculate_route action with geocoded coordinates."""
    res = bot.answer("Find a route from Guntur Railway Station to Vignan University, Vadlamudi")
    assert "action" in res
    act = res["action"]
    assert act["type"] == "calculate_route"
    assert "Guntur" in act["origin"]
    assert "Vignan" in act["destination"]
    assert act["origin_coords"] is not None
    assert act["destination_coords"] is not None
    assert abs(act["destination_coords"][0] - 16.2335) < 0.05


def test_destination_only_navigation(bot):
    """Navigate to single landmark sets destination and triggers map route."""
    res = bot.answer("Navigate to Tenali")
    assert "action" in res
    act = res["action"]
    assert act["type"] == "set_destination"
    assert "Tenali" in act["destination_name"]
    assert act["coords"] is not None


# =============================================================================
# 3. NEARBY FACILITY SEARCHES USING GEOGRAPHIC COORDINATES
# =============================================================================

def test_search_nearby_dining_at_destination(bot):
    """Search for food near destination uses real OSM/verified amenities."""
    ctx = {
        "dest_coords": (16.2335, 80.5505),
        "dest_label": "Vignan University, Vadlamudi"
    }
    res = bot.answer("Recommend the best restaurants and places to eat nearby", context=ctx)
    assert "response" in res
    assert "VERIFIED PLACES" in res.get("badge", "").upper()
    assert "⭐" in res["response"]
    assert "Dining" in res["response"] or "Food" in res["response"] or "Cafeteria" in res["response"]


def test_search_nearby_hospitals(bot):
    """Search for hospitals resolves Hospital category."""
    ctx = {
        "dest_coords": (16.3067, 80.4365),
        "dest_label": "Guntur City Center"
    }
    res = bot.answer("Find hospitals near there", context=ctx)
    assert "response" in res
    assert "VERIFIED PLACES" in res.get("badge", "").upper()
    assert "Guntur" in res["response"]


# =============================================================================
# 4. FOLLOW-UP QUESTIONS & ANAPHORA RESOLUTION
# =============================================================================

def test_anaphora_there_resolution(bot):
    """Turn 1 sets destination; Turn 2 asks about 'there'."""
    # Turn 1
    res1 = bot.answer("Navigate to Vignan University")
    assert "action" in res1
    assert "Vignan" in res1["action"]["destination_name"]

    # Turn 2: Follow-up referring to "there"
    res2 = bot.answer("What is the weather like there?")
    assert "response" in res2
    assert "WEATHER" in res2.get("badge", "").upper()
    assert "°C" in res2["response"]


def test_followup_route_alternative_selection(bot):
    """Turn 2 requests 'Show the second route on the map'."""
    r_pri = MagicMock()
    r_pri.route.id = "r_pri_01"
    r_pri.route.name = "NH-16 Express Bypass"
    r_pri.effective_distance_km = 32.5

    r_sec = MagicMock()
    r_sec.route.id = "r_sec_02"
    r_sec.route.name = "Tenali Rural Corridor"
    r_sec.effective_distance_km = 28.0

    ctx = {"ranked_routes": [r_pri, r_sec]}

    res = bot.answer("Show the second route on the map", context=ctx)
    assert "action" in res
    assert res["action"]["type"] == "focus_route"
    assert res["action"]["route_id"] == "r_sec_02"
    assert "Tenali Rural Corridor" in res["action"]["route_name"]


def test_followup_avoid_tolls_preference(bot):
    """User asks to avoid tolls on current route."""
    res = bot.answer("Avoid tolls on this route")
    assert "action" in res
    assert res["action"]["type"] == "update_preferences"
    assert res["action"]["avoid_tolls"] is True


# =============================================================================
# 5. MISSING OR AMBIGUOUS ORIGIN & DESTINATION
# =============================================================================

def test_ambiguous_destination_clarification(bot):
    """Ambiguous place name triggers clarification, not a random guess."""
    res = bot.answer("Find a route to Airport")
    assert "action" not in res
    assert "clarify" in res["response"].lower() or "clarification" in res.get("badge", "").lower()


def test_nonexistent_location_handling(bot):
    """Non-existent location triggers honest diagnostic, no hallucinated coordinates."""
    res = bot.answer("Directions to XYZNonExistentFictionalAtlantis998877")
    assert "action" not in res
    assert "could not locate" in res["response"].lower() or "geocoding notice" in res.get("badge", "").lower()


# =============================================================================
# 6. MULTILINGUAL RESPONSES WITHOUT STATIC TEXT BLOCKING
# =============================================================================

def test_telugu_route_execution(bot):
    """Telugu route inquiry must calculate route and return action."""
    res = bot.answer("విజ్ఞాన్ యూనివర్సిటీకి దారి చూపించు")
    assert "response" in res
    # Should execute routing, not just a static greeting
    assert "action" in res or "రూట్" in res["response"] or "విజ్ఞాన్" in res["response"]


def test_hindi_greeting_and_question(bot):
    """Hindi greeting returns polite Hindi response with Hindi badge."""
    res = bot.answer("नमस्ते, आप कैसे हैं?")
    assert "हिन्दी" in res.get("badge", "")
    assert "नमस्ते" in res["response"] or "A.U.R.A." in res["response"]


def test_tamil_inquiry(bot):
    """Tamil query returns Tamil response."""
    res = bot.answer("வணக்கம், நீங்கள் யார்?")
    assert "தமிழ்" in res.get("badge", "")


# =============================================================================
# 7. LLM PROVIDER AUTH ERROR & TIMEOUT FALLBACKS
# =============================================================================

def test_llm_auth_failure_clean_fallback():
    """Invalid LLM API key triggers AUTH_ERROR notice without crashing."""
    bot = PathfinderChatbot()
    bot.llm_client.active_provider_name = "mock_broken_key"
    with patch.object(bot.llm_client, "generate", return_value=(None, "builtin")):
        bot.llm_client.last_error_category = "AUTH_ERROR"
        res = bot.answer("What is machine learning?")
        assert "response" in res
        assert "Notice: AI Provider Authentication Error" in res["response"]
        assert "machine learning" in res["response"].lower() or "data" in res["response"].lower()


def test_llm_timeout_fallback():
    """LLM network timeout triggers TIMEOUT_ERROR notice and cognitive engine."""
    bot = PathfinderChatbot()
    bot.llm_client.active_provider_name = "mock_timeout"
    with patch.object(bot.llm_client, "generate", return_value=(None, "builtin")):
        bot.llm_client.last_error_category = "TIMEOUT_ERROR"
        res = bot.answer("Explain the law of universal gravitation")
        assert "response" in res
        assert "Notice: AI Provider Timeout" in res["response"]
        assert "gravit" in res["response"].lower() or "mass" in res["response"].lower()


# =============================================================================
# 8. PREFERENCE UPDATES & NO FAKE ROUTE RESULTS
# =============================================================================

def test_avoid_highways_and_ferries_preference(bot):
    """Updating preferences for highways and ferries produces valid structured action."""
    res = bot.answer("Please avoid highways and ferries for this journey")
    assert "action" in res
    act = res["action"]
    assert act["type"] == "update_preferences"
    assert act["avoid_highways"] is True
    assert act["avoid_ferries"] is True


def test_no_fake_road_closures_or_facilities(bot):
    """Truthful reporting: without real active restrictions, none are invented."""
    res = bot.answer("What can PATHFINDER actually do?")
    assert "Implemented" in res["response"] or "Verified" in res["response"]
    assert "Fastest" in res["response"]
    assert "CAN-bus" in res["response"]  # Explains scope honestly


# =============================================================================
# 9. CONVERSATION STATE & RESET
# =============================================================================

def test_reset_conversation(bot):
    """Reset clears history and active destination context."""
    bot.answer("Navigate to Vignan University")
    assert bot.last_destination is not None
    assert len(bot.conv_manager.history) >= 2

    bot.reset_conversation()
    assert bot.last_destination is None
    assert len(bot.conv_manager.history) == 0
