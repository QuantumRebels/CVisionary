# tests/conftest.py

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the main app and the dependency getter
from app import app, get_http_client

@pytest.fixture(scope="function")
def test_client(monkeypatch):
    """
    Fixture to create a test client and a mock for the shared httpx.AsyncClient.
    """
    # 1. Set required environment variables for the tests
    monkeypatch.setenv("RETRIEVAL_SERVICE_URL", "http://mock-retrieval-service:8000")
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    # 2. Create a mock for the httpx.AsyncClient
    mock_http_client = MagicMock(spec=AsyncClient)

    # 3. Use FastAPI's dependency override to replace the real client with our mock
    app.dependency_overrides[get_http_client] = lambda: mock_http_client

    # 4. Yield the client and the mock for use in tests
    with TestClient(app) as client:
        yield client, mock_http_client

    # 5. Clean up the override after the test is done
    app.dependency_overrides.clear()