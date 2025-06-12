# tests/test_llm_client.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import Response, HTTPStatusError, Request

from llm_client import invoke_gemini, LLMError

# FIX: Helper to create valid mock responses
def create_mock_response(status_code, json_data=None, text_data=None):
    """Creates an httpx.Response with a mock request object."""
    request = Request(method="POST", url="http://mock-url")
    return Response(status_code, json=json_data, text=text_data, request=request)

@pytest.mark.asyncio
async def test_invoke_gemini_happy_path(monkeypatch):
    """Tests a successful call to the Gemini API."""
    # Arrange
    # FIX: Set the environment variable for this test
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_response_data = {
        "candidates": [{"content": {"parts": [{"text": "Generated text"}]}}]
    }
    mock_client.post = AsyncMock(return_value=create_mock_response(200, json_data=mock_response_data))

    # Act
    result = await invoke_gemini(mock_client, "test prompt")

    # Assert
    assert result == "Generated text"
    mock_client.post.assert_called_once()
    called_with_json = mock_client.post.call_args.kwargs['json']
    assert called_with_json['generationConfig']['responseMimeType'] == 'application/json'

@pytest.mark.asyncio
async def test_invoke_gemini_api_key_missing(monkeypatch):
    """Tests that LLMError is raised if the API key is not set."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(LLMError, match="GEMINI_API_KEY environment variable is not set"):
        await invoke_gemini(MagicMock(), "test prompt")

@pytest.mark.asyncio
async def test_invoke_gemini_http_error(monkeypatch):
    """Tests handling of an HTTP error from the Gemini API."""
    # FIX: Set the environment variable for this test
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_response = create_mock_response(500, json_data={"error": "Internal Server Error"})
    mock_client.post = AsyncMock(side_effect=HTTPStatusError(
        "Server Error", request=mock_response.request, response=mock_response
    ))

    with pytest.raises(LLMError, match="Gemini API request failed"):
        await invoke_gemini(mock_client, "test prompt")

@pytest.mark.asyncio
async def test_invoke_gemini_malformed_response(monkeypatch):
    """Tests handling of a response from Gemini that is missing expected fields."""
    # FIX: Set the environment variable for this test
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    mock_client = MagicMock()
    # Malformed response (missing 'candidates')
    mock_client.post = AsyncMock(return_value=create_mock_response(200, json_data={"error": "bad format"}))

    with pytest.raises(LLMError, match="Failed to parse Gemini response"):
        await invoke_gemini(mock_client, "test prompt")