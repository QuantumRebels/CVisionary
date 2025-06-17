import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import Response, Request

from scoring_service.suggestion_client import generate_suggestions, _parse_suggestions

@pytest.mark.asyncio
async def test_generate_suggestions_happy_path():
    mock_http_client = MagicMock()
    mock_gemini_response = {
        "candidates": [{"content": {"parts": [{"text": "- Suggestion 1\n- Suggestion 2"}]}}]
    }
    mock_http_client.post = AsyncMock(return_value=Response(200, json=mock_gemini_response, request=Request("POST", "")))
    
    suggestions = await generate_suggestions(mock_http_client, ["Python", "AWS"])

    assert suggestions == ["Suggestion 1", "Suggestion 2"]

def test_parse_suggestions():
    text_bullets = "• Suggestion A\n* Suggestion B"
    assert _parse_suggestions(text_bullets) == ["Suggestion A", "Suggestion B"]