# AI_Services/retrieval_service/tests/test_app.py

import pytest
from unittest.mock import AsyncMock, MagicMock
import httpx
from fastapi import status

from conftest import (
    USER_ID,
    SECTION_ID,
    MOCK_EMBEDDING_SERVICE_RESPONSE,
    MOCK_EMBED_RESPONSE,
    SAMPLE_EMBEDDING,
)

@pytest.mark.asyncio
async def test_health_check(test_client_and_mock):
    """Test the /health endpoint."""
    client, _ = test_client_and_mock
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok", "service": "retrieval"}


@pytest.mark.asyncio
async def test_retrieve_full_context_happy_path(test_client_and_mock):
    """Test the /retrieve/full endpoint with a valid request."""
    client, mock_http_client = test_client_and_mock

    # Create mock responses
    mock_embed_response = httpx.Response(200, json=MOCK_EMBED_RESPONSE, request=httpx.Request("POST", "http://test/embed"))
    mock_retrieve_response = httpx.Response(200, json=MOCK_EMBEDDING_SERVICE_RESPONSE, request=httpx.Request("POST", f"http://test/retrieve/{USER_ID}"))
    
    # Set up the side effect to return the mock responses in order
    mock_http_client.request.side_effect = [mock_embed_response, mock_retrieve_response]

    # Act
    response = client.post(
        "/retrieve/full",
        json={"user_id": USER_ID, "job_description": "A great job.", "top_k": 2},
    )

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert "results" in response_data
    assert len(response_data["results"]) == 2
    assert response_data["results"][0]["chunk_id"] == "chunk-1"

    # Verify the mock calls
    assert mock_http_client.request.call_count == 2
    
    # Check the /embed call
    embed_call_args = mock_http_client.request.call_args_list[0]
    assert embed_call_args[0][0] == "POST"  # method is first positional arg
    assert str(embed_call_args[0][1]).endswith("/embed")  # URL is second positional arg
    assert embed_call_args[1]["json"] == {"text": "A great job."}

    # Check the /retrieve call
    retrieve_call_args = mock_http_client.request.call_args_list[1]
    assert retrieve_call_args[0][0] == "POST"  # method is first positional arg
    assert str(retrieve_call_args[0][1]).endswith(f"/retrieve/{USER_ID}")  # URL is second positional arg
    assert retrieve_call_args[1]["json"] == {
        "query_embedding": SAMPLE_EMBEDDING,
        "top_k": 2,
        "index_namespace": "profile",
    }


@pytest.mark.asyncio
async def test_retrieve_section_context_happy_path(test_client_and_mock):
    """Test the /retrieve/section endpoint with a valid request."""
    client, mock_http_client = test_client_and_mock

    # Create mock responses
    mock_embed_response = httpx.Response(
        status_code=status.HTTP_200_OK,
        json=MOCK_EMBED_RESPONSE,
        request=httpx.Request("POST", "http://test/embed")
    )
    mock_retrieve_response = httpx.Response(
        status_code=status.HTTP_200_OK,
        json=MOCK_EMBEDDING_SERVICE_RESPONSE,
        request=httpx.Request("POST", f"http://test/retrieve/{USER_ID}")
    )
    
    # Set up the side effect to return the mock responses in order
    mock_http_client.request.side_effect = [mock_embed_response, mock_retrieve_response]

    # Act
    response = client.post(
        "/retrieve/section",
        json={
            "user_id": USER_ID,
            "section_id": SECTION_ID,
            "job_description": "A specific job.",
            "top_k": 3,
        },
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "results" in response_data
    assert len(response_data["results"]) == 2

    # Verify the mock calls
    assert mock_http_client.request.call_count == 2
    
    # Check the /embed call
    embed_call_args = mock_http_client.request.call_args_list[0]
    assert embed_call_args[0][0] == "POST"  # method is first positional arg
    assert str(embed_call_args[0][1]).endswith("/embed")  # URL is second positional arg
    assert embed_call_args[1]["json"] == {"text": "A specific job."}
    
    # Check the /retrieve call
    retrieve_call_args = mock_http_client.request.call_args_list[1]
    assert retrieve_call_args[0][0] == "POST"  # method is first positional arg
    assert str(retrieve_call_args[0][1]).endswith(f"/retrieve/{USER_ID}")  # URL is second positional arg
    assert retrieve_call_args[1]["json"] == {
        "query_embedding": SAMPLE_EMBEDDING,
        "top_k": 3,
        "index_namespace": "resume_sections",
        "filter_by_section_ids": [SECTION_ID],
    }


@pytest.mark.asyncio
async def test_retrieve_full_context_invalid_input(test_client_and_mock):
    """Test that the endpoint returns 400 for empty inputs."""
    client, _ = test_client_and_mock

    response = client.post(
        "/retrieve/full",
        json={"user_id": " ", "job_description": "A great job."},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "user_id and job_description cannot be empty" in response.json()["error"]

    response = client.post(
        "/retrieve/full",
        json={"user_id": USER_ID, "job_description": " "},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "user_id and job_description cannot be empty" in response.json()["error"]


@pytest.mark.asyncio
async def test_retrieve_full_context_embedding_service_fails(test_client_and_mock):
    """Test that a 5xx error from the embedding service is handled gracefully."""
    client, mock_http_client = test_client_and_mock

    # Arrange: Mock the first call (/embed) to fail with a connection error
    mock_http_client.request.side_effect = httpx.ConnectError("Connection failed")

    # Act
    response = client.post(
        "/retrieve/full",
        json={"user_id": USER_ID, "job_description": "A great job."},
    )

    # Assert
    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    assert "Failed to generate embedding" in response.json()["error"]
    # We expect MAX_RETRIES + 1 calls (initial call + retries)
    assert mock_http_client.request.call_count == 2  # 1 initial + 1 retry