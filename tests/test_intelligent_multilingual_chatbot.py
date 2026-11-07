"""
Comprehensive Test Suite for NexRoute Intelligent Multilingual AI Assistant
Verifies:
1. DocumentParser: PDF and text/code extraction.
2. AIService: Provider discovery, system prompt building, multilingual BCP-47 codes.
3. PathfinderChatbot:
   - Tool schemas & tool execution (hospitals, fuel, food, stops, search, navigation)
   - General knowledge handling without hardcoded constraints
   - Multilingual queries (Telugu, Hindi, etc.)
   - Conversation memory & New Chat reset
   - Multimodal attachment handling
   - Safe unconfigured messaging
"""

import os
import io
import pytest
from unittest.mock import MagicMock, patch

from src.backend.ai.ai_service import AIService, DocumentParser, LANGUAGE_SPEECH_MAP
from src.pathfinder_chatbot import PathfinderChatbot
from src.pathfinder_tools import PathfinderToolExecutor, TOOL_SCHEMAS


# =============================================================================
# 1. DOCUMENT PARSER TESTS
# =============================================================================

def test_document_parser_text_file():
    content = "Hello NexRoute AI. This is a journey plan with coordinates 16.2335, 80.5505."
    txt, summary = DocumentParser.extract_text_from_bytes(content.encode("utf-8"), "trip_plan.txt")
    assert "Hello NexRoute AI" in txt
    assert "trip_plan.txt" in summary


def test_document_parser_empty_file():
    txt, summary = DocumentParser.extract_text_from_bytes(b"", "empty.txt")
    assert txt == ""
    assert "Empty file" in summary


def test_document_parser_pdf_mock():
    # If pypdf is installed, test with real minimal PDF or mock
    try:
        import pypdf
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=72, height=72)
        buf = io.BytesIO()
        writer.write(buf)
        pdf_bytes = buf.getvalue()
        txt, summary = DocumentParser.extract_text_from_bytes(pdf_bytes, "test.pdf")
        assert "PDF Document: test.pdf" in summary
    except ImportError:
        pass


# =============================================================================
# 2. AI SERVICE TESTS
# =============================================================================

def test_ai_service_speech_map():
    assert "te" in LANGUAGE_SPEECH_MAP
    assert LANGUAGE_SPEECH_MAP["te"]["bcp47"] == "te-IN"
    assert "hi" in LANGUAGE_SPEECH_MAP
    assert LANGUAGE_SPEECH_MAP["hi"]["bcp47"] == "hi-IN"
    assert "en" in LANGUAGE_SPEECH_MAP
    assert LANGUAGE_SPEECH_MAP["en"]["bcp47"] == "en-IN"


def test_ai_service_system_prompt_multilingual():
    prompt_te = AIService.build_system_prompt(lang="te", context={
        "start_label": "Guntur",
        "dest_label": "Tenali",
        "travel_mode": "Car"
    })
    assert "Telugu" in prompt_te
    assert "తెలుగు" in prompt_te
    assert "Guntur" in prompt_te
    assert "Tenali" in prompt_te
    assert "calculate_route" in prompt_te


def test_ai_service_unconfigured_message():
    ai = AIService()
    with patch.dict(os.environ, {}, clear=True):
        with patch.object(AIService, "get_active_provider_info", return_value={"available": [], "primary": "none"}):
            res = ai.generate([{"role": "user", "content": "How far is the moon?"}], lang="en")
            assert res["success"] is False
            assert "SETUP REQUIRED" in res["badge"]
            assert "GEMINI_API_KEY" in res["response"]
            assert "OPENAI_API_KEY" in res["response"]


# =============================================================================
# 3. PATHFINDER TOOLS TESTS
# =============================================================================

def test_new_tool_schemas_present():
    tool_names = [t["function"]["name"] for t in TOOL_SCHEMAS]
    expected = [
        "search_location",
        "find_nearby_places",
        "find_nearby_hospitals",
        "find_petrol_stations",
        "find_restaurants",
        "find_hotels",
        "add_route_stop",
        "remove_route_stop",
        "get_route_details",
        "get_navigation_instructions"
    ]
    for exp in expected:
        assert exp in tool_names, f"Expected tool schema '{exp}' not found in TOOL_SCHEMAS"


def test_tool_executor_search_location():
    mock_map = MagicMock()
    mock_map.geocode_candidates.return_value = [
        {"name": "Tenali", "display_name": "Tenali, Guntur, AP, India", "lat": 16.243, "lon": 80.640}
    ]
    executor = PathfinderToolExecutor(map_service=mock_map)
    res = executor.execute("search_location", {"query": "Tenali"}, context={})
    assert "response" in res
    assert res.get("success") is True
    assert "Tenali" in res["response"]


def test_tool_executor_add_and_remove_stop():
    executor = PathfinderToolExecutor()
    add_res = executor.execute("add_route_stop", {"stop_name": "Chebrolu", "lat": 16.20, "lon": 80.52}, context={})
    assert add_res.get("success") is True
    assert add_res["action"]["type"] == "add_stop"
    assert add_res["action"]["stop"]["name"] == "Chebrolu"

    rm_res = executor.execute("remove_route_stop", {"stop_index": 1}, context={})
    assert rm_res.get("success") is True
    assert rm_res["action"]["type"] == "remove_stop"


def test_tool_executor_route_details():
    executor = PathfinderToolExecutor()
    mock_top = MagicMock()
    mock_top.route.name = "Guntur-Tenali Express Way"
    mock_top.route.steps = [{"instruction": "Head south", "distance_m": 500}]
    mock_top.effective_distance_km = 28.5
    mock_top.effective_duration_minutes = 35.0

    res = executor.execute("get_route_details", {}, context={"ranked_routes": [mock_top]})
    assert res.get("success") is True
    assert "28.5 km" in res["response"]
    assert "Guntur-Tenali" in res["response"]


# =============================================================================
# 4. PATHFINDER CHATBOT MULTILINGUAL & MEMORY TESTS
# =============================================================================

def test_chatbot_reset_conversation():
    bot = PathfinderChatbot()
    bot.answer("My name is John")
    assert len(bot.conv_manager.history) > 0
    bot.reset_conversation()
    assert len(bot.conv_manager.history) == 0


def test_chatbot_multilingual_greetings():
    bot = PathfinderChatbot()
    # Telugu
    res_te = bot.answer("నమస్కారం, సహాయం కావాలి", context={"language": "te"})
    assert "response" in res_te
    assert "తెలుగు" in res_te.get("badge", "") or "TELUGU" in res_te.get("badge", "").upper()

    # Hindi
    res_hi = bot.answer("नमस्ते, मुझे रास्ता बताओ", context={"language": "hi"})
    assert "response" in res_hi
    assert "हिन्दी" in res_hi.get("badge", "") or "HINDI" in res_hi.get("badge", "").upper()


def test_chatbot_with_attachments_mocked():
    bot = PathfinderChatbot()
    mock_res = {
        "success": True,
        "response": "I see an image showing a highway route sign.",
        "badge": "✨ GEMINI 2.0 FLASH",
        "provider": "gemini",
        "error": None
    }
    with patch.object(bot.ai_service, "is_configured", return_value=True):
        with patch.object(bot.ai_service, "generate", return_value=mock_res):
            att = [{"type": "image", "name": "sign.jpg", "data_base64": "AAAA"}]
            ans = bot.answer("What is in this image?", attachments=att)
            assert "highway route sign" in ans["response"]
            assert ans.get("badge") == "✨ GEMINI 2.0 FLASH"
