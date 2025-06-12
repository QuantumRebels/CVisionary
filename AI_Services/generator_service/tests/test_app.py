# tests/test_app.py

import json
from unittest.mock import AsyncMock, MagicMock
from httpx import Response, Request, HTTPStatusError

# Mock data for the Retrieval Service response
MOCK_RETRIEVAL_RESPONSE = {
    "results": [
        {
            "chunk_id": "c1", "user_id": "u1", "index_namespace": "profile",
            "section_id": None, "source_type": "experience", "source_id": "0",
            "text": "Led a team of developers.", "score": 0.9,
            "created_at": "2023-01-01T12:00:00Z"
        }
    ]
}

# Mock data for the Gemini API response
MOCK_GEMINI_RESPONSE = {
    "candidates": [{
        "content": {
            "parts": [{
                "text": json.dumps({"summary": "This is the generated summary."})
            }]
        }
    }]
}

# FIX: Helper to create valid mock responses
def create_mock_response(status_code, json_data=None, text_data=None):
    """Creates an httpx.Response with a mock request object."""
    request = Request(method="POST", url="http://mock-url")
    return Response(status_code, json=json_data, text=text_data, request=request)


def test_health_check(test_client):
    """Tests the /health endpoint."""
    client, _ = test_client
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "generator-service"}

def test_generate_full_resume_happy_path(test_client):
    """Tests the full generation endpoint with successful downstream calls."""
    client, mock_http_client = test_client

    # Arrange: Mock the sequence of HTTP calls using the helper
    mock_http_client.post.side_effect = [
        create_mock_response(200, json_data=MOCK_RETRIEVAL_RESPONSE),
        create_mock_response(200, json_data=MOCK_GEMINI_RESPONSE),
    ]

    # Act
    response = client.post(
        "/generate/full",
        json={"user_id": "u1", "job_description": "A great job"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["retrieval_mode"] == "full"
    assert '"summary": "This is the generated summary."' in data["generated_text"]
    assert "RELEVANT CONTEXT FROM USER'S PROFILE" in data["raw_prompt"]

    # Verify that the correct services were called
    assert mock_http_client.post.call_count == 2
    retrieval_call = mock_http_client.post.call_args_list[0]
    gemini_call = mock_http_client.post.call_args_list[1]
    assert "retrieve/full" in retrieval_call.args[0]
    assert "generativelanguage.googleapis.com" in gemini_call.args[0]

def test_generate_section_happy_path(test_client):
    """Tests the section generation endpoint with successful downstream calls."""
    client, mock_http_client = test_client
    mock_http_client.post.side_effect = [
        create_mock_response(200, json_data=MOCK_RETRIEVAL_RESPONSE),
        create_mock_response(200, json_data=MOCK_GEMINI_RESPONSE),
    ]

    response = client.post(
        "/generate/section",
        json={
            "user_id": "u1",
            "section_id": "summary",
            "job_description": "A great job",
            "existing_text": "Old summary"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["retrieval_mode"] == "section"
    assert data["section_id"] == "summary"
    assert "CURRENT SECTION CONTENT" in data["raw_prompt"]
    assert "Old summary" in data["raw_prompt"]

def test_retrieval_service_failure(test_client):
    """Tests how the service handles a failure from the Retrieval Service."""
    client, mock_http_client = test_client
    # Arrange: Mock the Retrieval Service call to fail
    mock_response = create_mock_response(500, text_data="Internal Server Error")
    mock_http_client.post.side_effect = HTTPStatusError(
        "Server Error", request=mock_response.request, response=mock_response
    )

    # Act
    response = client.post(
        "/generate/full",
        json={"user_id": "u1", "job_description": "A great job"}
    )

    # Assert
    assert response.status_code == 502 # Bad Gateway
    # FIX: Check for the actual error message from the app's exception handler
    assert "Failed to process request due to a downstream service error" in response.json()["detail"]
    mock_http_client.post.assert_called_once()

def test_llm_service_failure(test_client):
    """Tests how the service handles a failure from the Gemini API."""
    client, mock_http_client = test_client
    # Arrange: Retrieval succeeds, but Gemini fails
    mock_gemini_response = create_mock_response(500, text_data="Internal Server Error")
    mock_http_client.post.side_effect = [
        create_mock_response(200, json_data=MOCK_RETRIEVAL_RESPONSE),
        HTTPStatusError("Server Error", request=mock_gemini_response.request, response=mock_gemini_response)
    ]

    # Act
    response = client.post(
        "/generate/full",
        json={"user_id": "u1", "job_description": "A great job"}
    )

    # Assert
    assert response.status_code == 502 # Bad Gateway
    assert "Failed to process request" in response.json()["detail"]
    assert mock_http_client.post.call_count == 2

def test_llm_returns_invalid_json(test_client):
    """Tests the case where the LLM returns a non-JSON string when it should have."""
    client, mock_http_client = test_client
    # Arrange: Gemini returns a plain string, not the requested JSON
    invalid_gemini_response = {
        "candidates": [{"content": {"parts": [{"text": "Oops, I forgot to use JSON."}]}}]
    }
    mock_http_client.post.side_effect = [
        create_mock_response(200, json_data=MOCK_RETRIEVAL_RESPONSE),
        create_mock_response(200, json_data=invalid_gemini_response),
    ]

    # Act
    response = client.post(
        "/generate/full",
        json={"user_id": "u1", "job_description": "A great job"}
    )

    # Assert
    assert response.status_code == 502 # Bad Gateway
    assert "LLM failed to generate valid JSON output" in response.json()["detail"]