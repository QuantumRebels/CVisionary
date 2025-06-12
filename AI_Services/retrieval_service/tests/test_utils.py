# AI_Services/retrieval_service/tests/test_utils.py

import pytest
import httpx
from unittest.mock import AsyncMock
from fastapi import HTTPException

from utils import (
    embed_text,
    retrieve_profile_chunks,
    retrieve_section_chunks,
    _make_request_with_retry,
)
from schemas import ChunkItem
from conftest import (
    USER_ID,
    SECTION_ID,
    SAMPLE_EMBEDDING,
    MOCK_EMBED_RESPONSE,
    MOCK_EMBEDDING_SERVICE_RESPONSE,
)

# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio


async def test_embed_text_success(monkeypatch):
    """Test successful text embedding."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.request = AsyncMock(
        return_value=httpx.Response(200, json=MOCK_EMBED_RESPONSE, request=httpx.Request("POST", ""))
    )
    monkeypatch.setenv("EMBEDDING_SERVICE_URL", "http://fake-url")

    embedding = await embed_text(mock_client, "some text")

    assert embedding == SAMPLE_EMBEDDING
    mock_client.request.assert_called_once()


async def test_retrieve_profile_chunks_success(monkeypatch):
    """Test successful retrieval of profile chunks."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.request = AsyncMock(
        return_value=httpx.Response(200, json=MOCK_EMBEDDING_SERVICE_RESPONSE, request=httpx.Request("POST", ""))
    )
    monkeypatch.setenv("EMBEDDING_SERVICE_URL", "http://fake-url")

    chunks = await retrieve_profile_chunks(mock_client, USER_ID, SAMPLE_EMBEDDING, 5)

    assert len(chunks) == 2
    assert isinstance(chunks[0], ChunkItem)
    assert chunks[0].chunk_id == "chunk-1"


async def test_retrieve_section_chunks_success(monkeypatch):
    """Test successful retrieval of section-specific chunks."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.request = AsyncMock(
        return_value=httpx.Response(200, json=MOCK_EMBEDDING_SERVICE_RESPONSE, request=httpx.Request("POST", ""))
    )
    monkeypatch.setenv("EMBEDDING_SERVICE_URL", "http://fake-url")

    chunks = await retrieve_section_chunks(
        mock_client, USER_ID, SECTION_ID, SAMPLE_EMBEDDING, 5
    )

    assert len(chunks) == 2
    # Verify the payload sent to the mock
    call_args = mock_client.request.call_args
    assert call_args.kwargs["json"]["index_namespace"] == "resume_sections"
    assert call_args.kwargs["json"]["filter_by_section_ids"] == [SECTION_ID]


async def test_make_request_with_retry_logic():
    """Test the retry mechanism for 5xx errors."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    # Simulate a server error on the first call, then success
    mock_client.request.side_effect = [
        httpx.HTTPStatusError("Server Error", request=httpx.Request("POST", ""), response=httpx.Response(500)),
        httpx.Response(200, json={"status": "ok"}, request=httpx.Request("POST", "")),
    ]

    response = await _make_request_with_retry(mock_client, "POST", "http://fake-url")

    assert response == {"status": "ok"}
    assert mock_client.request.call_count == 2


async def test_make_request_fails_after_retries():
    """Test that the request fails after all retries are exhausted."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    # Simulate persistent server errors
    mock_client.request.side_effect = httpx.HTTPStatusError(
        "Server Error", request=httpx.Request("POST", ""), response=httpx.Response(503)
    )

    with pytest.raises(HTTPException) as exc_info:
        await _make_request_with_retry(mock_client, "POST", "http://fake-url")

    # MAX_RETRIES is 1, so 1 initial call + 1 retry = 2 calls
    assert mock_client.request.call_count == 2
    assert exc_info.value.status_code == 502
    assert "Embedding service server error: 503" in str(exc_info.value.detail)


async def test_make_request_no_retry_on_4xx():
    """Test that client errors (4xx) are not retried."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.request.side_effect = httpx.HTTPStatusError(
        "Not Found", request=httpx.Request("POST", ""), response=httpx.Response(404)
    )

    with pytest.raises(HTTPException) as exc_info:
        await _make_request_with_retry(mock_client, "POST", "http://fake-url")

    assert exc_info.value.status_code == 404
    assert "User not found or no chunks available" in str(exc_info.value.detail)
    assert mock_client.request.call_count == 1