"""
Test Suite: A.U.R.A. Complete Chatbot Intelligence & Reliability Suite
Acceptance Criteria Verification covering all 18 required scenarios:

1. "What is artificial intelligence?"
2. "Write a funny story about a robot."
3. "What is the capital of Japan?"
4. "Explain machine learning in simple words."
5. "Give me five creative final-year project ideas."
6. "What can PATHFINDER actually do?"
7. "Find a route from Guntur Railway Station to Vignan University, Vadlamudi."
8. "Which of these routes is shortest?"
9. "Show the second route on the map."
10. "What about the other alternative?"
11. An ambiguous location requiring clarification.
12. A misspelled question ("whut is artifical inteligence?").
13. A general question containing a travel-related keyword ("What is the rule of the road in philosophy?").
14. An AI provider authentication failure (401 error -> AUTH_ERROR, clean fallback).
15. A rate-limit or timeout error (429/timeout -> RATE_LIMIT_ERROR / TIMEOUT_ERROR, diagnostic).
16. A navigation-tool failure (unresolvable place -> honest diagnostic without fake data).
17. A missing API configuration (clear diagnostic, no pretending).
18. A conversation follow-up that depends on previous messages.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.pathfinder_chatbot import PathfinderChatbot
from src.ai_assistant_engine import LLMClient, BuiltinCognitiveEngine
from src.map_service import MapService


@pytest.fixture
def map_service():
    return MapService()


@pytest.fixture
def bot(map_service):
    return PathfinderChatbot(map_service=map_service)


# =============================================================================
# SCENARIO 1: General Knowledge - What is artificial intelligence?
# =============================================================================
def test_scenario_01_what_is_artificial_intelligence(bot):
    res = bot.answer("What is artificial intelligence?")
    assert "response" in res
    assert "badge" in res
    content = res["response"].lower()
    assert "artificial intelligence" in content or "ai" in content
    assert "machine learning" in content or "reasoning" in content or "deep learning" in content


# =============================================================================
# SCENARIO 2: Creative Writing - Write a funny story about a robot
# =============================================================================
def test_scenario_02_funny_story_about_a_robot(bot):
    res = bot.answer("Write a funny story about a robot.")
    assert "response" in res
    assert "CREATIVE" in res.get("badge", "").upper() or "STORY" in res.get("badge", "").upper()
    assert len(res["response"].split()) >= 40
    # Checks that it didn't trigger navigation
    assert "action" not in res


# =============================================================================
# SCENARIO 3: Direct Factual Knowledge - What is the capital of Japan?
# Must directly answer Tokyo without triggering a flight/transit guide
# =============================================================================
def test_scenario_03_capital_of_japan(bot):
    res = bot.answer("What is the capital of Japan?")
    assert "response" in res
    assert "Tokyo" in res["response"]
    # Verify it is not a flight guide or transit ticket template
    assert "Haneda Airport" not in res["response"]
    assert "action" not in res


# =============================================================================
# SCENARIO 4: Educational Simplification - Explain machine learning in simple words
# =============================================================================
def test_scenario_04_machine_learning_simple_words(bot):
    res = bot.answer("Explain machine learning in simple words.")
    assert "response" in res
    content = res["response"].lower()
    assert "machine learning" in content
    assert "learn" in content or "apple" in content or "examples" in content


# =============================================================================
# SCENARIO 5: Creative Brainstorming - Five creative final-year project ideas
# =============================================================================
def test_scenario_05_five_creative_final_year_project_ideas(bot):
    res = bot.answer("Give me five creative final-year project ideas.")
    assert "response" in res
    assert "PROJECT" in res.get("badge", "").upper() or "IDEAS" in res.get("badge", "").upper()
    # Must list 5 distinct items
    for num in ["1.", "2.", "3.", "4.", "5."]:
        assert num in res["response"]


# =============================================================================
# SCENARIO 6: Application Capabilities - What can PATHFINDER actually do?
# Must distinguish implemented features from planned/unsupported features
# =============================================================================
def test_scenario_06_what_can_pathfinder_actually_do(bot):
    res = bot.answer("What can PATHFINDER actually do?")
    assert "response" in res
    content = res["response"]
    assert "Multi-Objective" in content or "Fastest" in content
    assert "Hazard" in content or "Obstacle" in content or "NH-16" in content
    assert "Implemented" in content or "Verified" in content
    assert "Planned" in content or "External" in content


# =============================================================================
# SCENARIO 7: Real Navigation Routing - Find a route from Guntur to Vignan University
# =============================================================================
def test_scenario_07_find_route_from_guntur_to_vignan_university(bot):
    res = bot.answer("Find a route from Guntur Railway Station to Vignan University, Vadlamudi.")
    assert "action" in res
    assert res["action"]["type"] == "calculate_route"
    assert "Guntur" in res["action"]["origin"]
    assert "Vignan" in res["action"]["destination"]
    assert len(res["action"]["origin_coords"]) == 2
    assert len(res["action"]["destination_coords"]) == 2


# =============================================================================
# SCENARIO 8: Route Comparison from Context - Which of these routes is shortest?
# =============================================================================
def test_scenario_08_which_of_these_routes_is_shortest(bot):
    r1 = MagicMock()
    r1.route.name = "Primary Arterial Corridor"
    r1.effective_distance_km = 34.2
    r1.effective_duration_minutes = 45.0

    r2 = MagicMock()
    r2.route.name = "Direct Rural Bypass"
    r2.effective_distance_km = 29.8
    r2.effective_duration_minutes = 50.0

    ctx = {"ranked_routes": [r1, r2]}
    res = bot.answer("Which of these routes is shortest?", context=ctx)
    assert "response" in res
    assert "SHORTEST" in res.get("badge", "").upper() or "Shortest" in res["response"]
    assert "Direct Rural Bypass" in res["response"]
    assert "29.8 km" in res["response"]


# =============================================================================
# SCENARIO 9: Map Synchronization Action - Show the second route on the map
# =============================================================================
def test_scenario_09_show_the_second_route_on_the_map(bot):
    r1 = MagicMock()
    r1.route.id = "route_alpha_0"
    r1.route.name = "Expressway Route"
    r1.effective_distance_km = 30.0

    r2 = MagicMock()
    r2.route.id = "route_beta_1"
    r2.route.name = "Scenic Bypass Route"
    r2.effective_distance_km = 33.5

    ctx = {"ranked_routes": [r1, r2]}
    res = bot.answer("Show the second route on the map.", context=ctx)
    assert "action" in res
    assert res["action"]["type"] == "focus_route"
    assert res["action"]["route_id"] == "route_beta_1"
    assert "Scenic Bypass Route" in res["action"]["route_name"]


# =============================================================================
# SCENARIO 10: Alternative Route Details - What about the other alternative?
# =============================================================================
def test_scenario_10_what_about_the_other_alternative(bot):
    r1 = MagicMock()
    r1.route.name = "Main Expressway"
    r1.route.summary_roads = ["NH-16 Express"]
    r1.effective_distance_km = 28.0
    r1.effective_duration_minutes = 35.0

    r2 = MagicMock()
    r2.route.name = "Rural Secondary Bypass"
    r2.route.summary_roads = ["SH-48 Link Road"]
    r2.effective_distance_km = 32.0
    r2.effective_duration_minutes = 42.0

    ctx = {"ranked_routes": [r1, r2]}
    res = bot.answer("What about the other alternative?", context=ctx)
    assert "response" in res
    assert "Rural Secondary Bypass" in res["response"]
    assert "32.0 km" in res["response"]


# =============================================================================
# SCENARIO 11: Ambiguous Location Clarification
# =============================================================================
def test_scenario_11_ambiguous_location_clarification(bot):
    res = bot.answer("Find a route to Springfield.")
    assert "response" in res
    assert "CLARIFICATION" in res.get("badge", "").upper() or "clarify" in res["response"].lower()
    # Must NOT invent fake coordinates
    assert "action" not in res or res.get("action") is None


# =============================================================================
# SCENARIO 12: Misspelled Question Handling
# =============================================================================
def test_scenario_12_misspelled_question(bot):
    res = bot.answer("whut is artifical inteligence?")
    assert "response" in res
    content = res["response"].lower()
    assert "artificial intelligence" in content
    assert "machine learning" in content or "computer science" in content


# =============================================================================
# SCENARIO 13: General Question Containing Travel-Related Keyword
# e.g., "What is the rule of the road in philosophy?"
# Must NOT trigger navigation or map action
# =============================================================================
def test_scenario_13_general_question_with_travel_keyword(bot):
    res = bot.answer("What is the rule of the road in philosophy?")
    assert "response" in res
    content = res["response"]
    assert "A.G. Gardiner" in content or "liberty" in content.lower() or "freedom" in content.lower()
    # Must NOT execute a navigation tool
    assert "action" not in res


# =============================================================================
# SCENARIO 14: AI Provider Authentication Failure
# =============================================================================
def test_scenario_14_ai_provider_authentication_failure():
    client = LLMClient()
    cat = client._classify_error("Error 401: Unauthorized Invalid API Key", status_code=401)
    assert cat == "AUTH_ERROR"

    # Test that chatbot handles AUTH_ERROR gracefully without crashing
    bot = PathfinderChatbot()
    bot.llm_client.active_provider_name = "mock_failing_provider"
    with patch.object(bot.llm_client, "generate", return_value=(None, "builtin")):
        bot.llm_client.last_error_category = "AUTH_ERROR"
        res = bot.answer("Explain quantum computing")
        assert "response" in res
        assert "Notice: AI Provider Authentication Error" in res["response"]


# =============================================================================
# SCENARIO 15: AI Provider Rate-Limit or Timeout Error
# =============================================================================
def test_scenario_15_rate_limit_or_timeout_error():
    client = LLMClient()
    rate_cat = client._classify_error("Error 429: Rate limit quota exceeded", status_code=429)
    assert rate_cat == "RATE_LIMIT_ERROR"

    timeout_cat = client._classify_error("Deadline exceeded: Request timed out", status_code=504)
    assert timeout_cat == "TIMEOUT_ERROR"

    # Test chatbot with rate-limit
    bot = PathfinderChatbot()
    bot.llm_client.active_provider_name = "mock_rate_limited"
    with patch.object(bot.llm_client, "generate", return_value=(None, "builtin")):
        bot.llm_client.last_error_category = "RATE_LIMIT_ERROR"
        res = bot.answer("Tell me about photosynthesis")
        assert "Notice: AI Provider Rate Limit" in res["response"]


# =============================================================================
# SCENARIO 16: Navigation Tool Failure (Nonexistent Place)
# Must report failure honestly and NOT invent coordinates
# =============================================================================
def test_scenario_16_navigation_tool_failure_nonexistent_location(bot):
    res = bot.answer("Find a route to NonExistentFictionalLocation9999XYZ")
    assert "response" in res
    assert "could not locate" in res["response"].lower() or "geocoding notice" in res.get("badge", "").lower()
    assert "action" not in res


# =============================================================================
# SCENARIO 17: Missing API Configuration
# Must show diagnostic message without pretending external AI is active
# =============================================================================
def test_scenario_17_missing_api_configuration():
    bot = PathfinderChatbot()
    # Force builtin mode
    bot.llm_client.active_provider_name = "builtin"
    res = bot.answer("Is external AI connected?")
    assert "response" in res
    assert "Built-in Cognitive Reasoning Engine" in res["response"]
    assert "GEMINI_API_KEY" in res["response"] or "OPENAI_API_KEY" in res["response"]


# =============================================================================
# SCENARIO 18: Multi-Turn Conversation Follow-Up Dependency
# Turn 1: Find a route to Vignan University
# Turn 2: Which alternative is shortest?
# Turn 3: Show that one on the map
# =============================================================================
def test_scenario_18_conversation_followup_dependency(bot):
    # Turn 1
    res1 = bot.answer("Find a route to Vignan University")
    assert "action" in res1
    assert res1["action"]["type"] == "set_destination"

    # Prepare context with 2 ranked routes generated from Turn 1
    r_fast = MagicMock()
    r_fast.route.id = "route_fast_01"
    r_fast.route.name = "NH-16 Velocity Route"
    r_fast.effective_distance_km = 33.0
    r_fast.effective_duration_minutes = 38.0

    r_short = MagicMock()
    r_short.route.id = "route_short_02"
    r_short.route.name = "Vadlamudi Local Route"
    r_short.effective_distance_km = 27.5
    r_short.effective_duration_minutes = 46.0

    ctx = {"ranked_routes": [r_fast, r_short]}

    # Turn 2: Follow-up question referring to the routes
    res2 = bot.answer("Which of these routes is shortest?", context=ctx)
    assert "response" in res2
    assert "Vadlamudi Local Route" in res2["response"]
    assert "27.5 km" in res2["response"]

    # Turn 3: Follow-up command referring to "that one"
    res3 = bot.answer("Show that one on the map", context=ctx)
    assert "action" in res3
    assert res3["action"]["type"] == "focus_route"
    # Should resolve "that one" to the shortest route
    assert res3["action"]["route_id"] == "route_short_02"
    assert "Vadlamudi Local Route" in res3["action"]["route_name"]
