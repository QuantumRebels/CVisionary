# test_app.py

import numpy as np
# FIX: Import `Request` from httpx
from httpx import Response, Request, RequestError, HTTPStatusError
from unittest.mock import AsyncMock

from conftest import SAMPLE_EMBEDDING_384D, SAMPLE_PROFILE_DATA

# Use the 384d sample embedding
SAMPLE_EMBEDDING = SAMPLE_EMBEDDING_384D
USER_ID = "test-user-123"
SECTION_ID = "test-section-abc"


def test_health_check(test_client):
    """Test the health check endpoint."""
    client, _ = test_client
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "embedding_service"}


def test_embed_endpoint(test_client):
    """Test the /embed endpoint for generating embeddings."""
    client, _ = test_client
    response = client.post("/embed", json={"text": "Hello world"})
    assert response.status_code == 200
    data = response.json()
    assert "embedding" in data
    assert len(data["embedding"]) == 384
    # Check if it's normalized
    norm = np.linalg.norm(data["embedding"])
    assert np.isclose(norm, 1.0)


def test_index_profile_happy_path(test_client):
    """Test successful indexing of a full user profile."""
    client, mock_http_client = test_client

    # FIX: httpx.Response needs a `request` object to be able to call `raise_for_status`.
    mock_request = Request(method="GET", url=f"http://localhost:5000/profile/{USER_ID}")
    mock_response = Response(
        status_code=200,
        json=SAMPLE_PROFILE_DATA,
        request=mock_request
    )
    mock_http_client.get = AsyncMock(return_value=mock_response)

    # Act
    response = client.post(f"/index/profile/{USER_ID}")

    # Debug output
    print("Response status:", response.status_code)
    print("Response body:", response.text)

    # Assert the response
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.text}"

    # Verify the response structure
    response_data = response.json()
    assert "status" in response_data, f"Response missing 'status' field: {response_data}"
    assert "num_chunks" in response_data, f"Response missing 'num_chunks' field: {response_data}"

    # Verify the mock was called correctly
    expected_url = f"http://localhost:5000/profile/{USER_ID}"
    mock_http_client.get.assert_called_once_with(expected_url)


def test_index_profile_reindexing_is_idempotent(test_client):
    """Test that re-indexing deletes old data before adding new data."""
    client, mock_http_client = test_client

    # FIX: Apply the same fix here.
    mock_request = Request(method="GET", url=f"http://localhost:5000/profile/{USER_ID}")
    mock_response = Response(
        status_code=200,
        json=SAMPLE_PROFILE_DATA,
        request=mock_request
    )
    mock_http_client.get = AsyncMock(return_value=mock_response)

    # Act: Index twice
    response1 = client.post(f"/index/profile/{USER_ID}")
    response2 = client.post(f"/index/profile/{USER_ID}")

    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 200
    # The number of chunks should be the same, not doubled
    assert response1.json()["num_chunks"] == response2.json()["num_chunks"]


def test_index_profile_backend_not_found(test_client):
    """Test handling of a 404 error from the backend profile service."""
    client, mock_http_client = test_client
    # Arrange: Mock the external API to raise an HTTPStatusError
    mock_response = Response(status_code=404, request=AsyncMock())
    mock_http_client.get = AsyncMock(
        side_effect=HTTPStatusError(
            "Not Found", request=mock_response.request, response=mock_response
        )
    )

    # Act
    response = client.post(f"/index/profile/{USER_ID}")

    # Assert
    assert response.status_code == 404


def test_index_and_delete_section(test_client):
    """Test the full lifecycle of a resume section: create, then delete."""
    client, _ = test_client
    section_text = "This is a custom resume bullet point."

    # 1. Index the section
    index_response = client.post(
        f"/index/{USER_ID}/section",
        json={"section_id": SECTION_ID, "text": section_text},
    )
    assert index_response.status_code == 200
    index_data = index_response.json()
    assert index_data["section_id"] == SECTION_ID
    assert len(index_data["chunk_ids"]) == 1

    # 2. Delete the section
    delete_response = client.delete(f"/index/{USER_ID}/section/{SECTION_ID}")
    assert delete_response.status_code == 200
    delete_data = delete_response.json()
    assert delete_data["status"] == f"Deleted 1 chunks for section {SECTION_ID}."
    assert delete_data["section_id"] == SECTION_ID

    # 3. Verify it's gone by trying to retrieve it (should be empty)
    retrieve_response = client.post(
        f"/retrieve/{USER_ID}",
        json={"query_embedding": SAMPLE_EMBEDDING, "index_namespace": "resume_sections"},
    )
    assert retrieve_response.status_code == 200
    assert retrieve_response.json()["results"] == []


def test_full_retrieval_flow(test_client):
    """Test the /retrieve endpoint with different namespaces and filters."""
    client, mock_http_client = test_client
    # Arrange: Mock a successful profile fetch
    # FIX: Apply the same fix here.
    mock_request = Request(method="GET", url=f"http://localhost:5000/profile/{USER_ID}")
    mock_response = Response(
        status_code=200,
        json=SAMPLE_PROFILE_DATA,
        request=mock_request
    )
    mock_http_client.get = AsyncMock(return_value=mock_response)

    # 1. Index profile and two sections
    profile_index_response = client.post(f"/index/profile/{USER_ID}")
    assert profile_index_response.status_code == 200 # First, ensure this passes

    client.post(
        f"/index/{USER_ID}/section",
        json={"section_id": "section-1", "text": "Text for section one."},
    )
    client.post(
        f"/index/{USER_ID}/section",
        json={"section_id": "section-2", "text": "Text for section two."},
    )

    # 2. Retrieve from 'profile' namespace
    response_profile = client.post(
        f"/retrieve/{USER_ID}",
        json={"query_embedding": SAMPLE_EMBEDDING, "index_namespace": "profile"},
    )
    assert response_profile.status_code == 200
    results_profile = response_profile.json()["results"]
    assert len(results_profile) > 0
    assert all(r["index_namespace"] == "profile" for r in results_profile)

    # 3. Retrieve from 'resume_sections' namespace
    response_sections = client.post(
        f"/retrieve/{USER_ID}",
        json={"query_embedding": SAMPLE_EMBEDDING, "index_namespace": "resume_sections"},
    )
    assert response_sections.status_code == 200
    results_sections = response_sections.json()["results"]
    assert len(results_sections) == 2
    assert all(r["index_namespace"] == "resume_sections" for r in results_sections)

    # 4. Retrieve with a section_id filter
    response_filtered = client.post(
        f"/retrieve/{USER_ID}",
        json={
            "query_embedding": SAMPLE_EMBEDDING,
            "index_namespace": "resume_sections",
            "filter_by_section_ids": ["section-1"],
        },
    )
    assert response_filtered.status_code == 200
    results_filtered = response_filtered.json()["results"]
    assert len(results_filtered) == 1
    assert results_filtered[0]["section_id"] == "section-1"


def test_retrieve_invalid_embedding_dimension(test_client):
    """Test that retrieval fails with a 422 if embedding has wrong dimension."""
    client, _ = test_client
    invalid_embedding = [0.1, 0.2, 0.3]
    response = client.post(
        f"/retrieve/{USER_ID}", json={"query_embedding": invalid_embedding}
    )
    assert response.status_code == 422  # Unprocessable Entity