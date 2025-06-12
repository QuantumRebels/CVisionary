# AI_Services/retrieval_service/tests/conftest.py

import pytest
import os
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

from fastapi.testclient import TestClient
import httpx

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables BEFORE importing the app
os.environ["EMBEDDING_SERVICE_URL"] = "http://mock-embedding-service:8000"
os.environ["DEFAULT_TOP_K"] = "5"

# Now import the app and its dependencies
from app import app, get_http_client

# --- Sample Data for Mocks ---

USER_ID = "test-user-123"
SECTION_ID = "section-abc-456"
SAMPLE_EMBEDDING = [0.01] * 384

# A sample response from the embedding service's /retrieve endpoint
MOCK_EMBEDDING_SERVICE_RESPONSE = {
    "results": [
        {
            "chunk_id": "chunk-1",
            "user_id": USER_ID,
            "index_namespace": "profile",
            "section_id": None,
            "source_type": "experience",
            "source_id": "0",
            "text": "Led a team of engineers.",
            "score": 0.95,
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "chunk_id": "chunk-2",
            "user_id": USER_ID,
            "index_namespace": "profile",
            "section_id": None,
            "source_type": "project",
            "source_id": "1",
            "text": "Developed a Python application.",
            "score": 0.91,
            "created_at": datetime.utcnow().isoformat(),
        },
    ]
}

# A sample response from the embedding service's /embed endpoint
MOCK_EMBED_RESPONSE = {"embedding": SAMPLE_EMBEDDING}


@pytest.fixture(scope="function")
def test_client_and_mock():
    """
    Fixture to create a test client with a mocked httpx.AsyncClient.
    This ensures no real network calls are made.
    """
    # 1. Create a mock for the httpx.AsyncClient
    mock_http_client = MagicMock(spec=httpx.AsyncClient)
    # The `request` method is what httpx.AsyncClient uses under the hood
    mock_http_client.request = AsyncMock()

    # 2. Override the dependency in the FastAPI app
    # Any part of the app that calls `get_http_client` will get our mock.
    app.dependency_overrides[get_http_client] = lambda: mock_http_client

    # 3. Yield the test client and the mock client for use in tests
    with TestClient(app) as client:
        yield client, mock_http_client

    # 4. Teardown: Clear the dependency override after the test
    app.dependency_overrides.clear()