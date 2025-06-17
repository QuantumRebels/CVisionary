import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
import os
import sys

# This allows tests to be run from the project root (e.g., `pytest orchestrator/tests`)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, get_toolbox
from tools import ToolBox

@pytest.fixture(scope="function", autouse=True)
def set_test_environment(monkeypatch):
    """Sets environment variables for the duration of a test function."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
    monkeypatch.setenv("REDIS_URL", "redis://mock-redis:6379")
    # FIX: Use correct default ports for downstream services
    monkeypatch.setenv("GENERATION_SERVICE_URL", "http://mock-generator:8000")
    monkeypatch.setenv("RETRIEVAL_SERVICE_URL", "http://mock-retrieval:8002")
    monkeypatch.setenv("SCORING_SERVICE_URL", "http://mock-scoring:8004")

@pytest.fixture
def mock_http_client():
    """Provides a mock httpx.AsyncClient."""
    return MagicMock(spec=AsyncClient)

@pytest.fixture
def test_client(mock_http_client, monkeypatch):
    """
    Provides a configured test client for the FastAPI app.
    Mocks Redis and the ToolBox dependency.
    """
    # Mock the Redis client used by the memory module
    mock_redis_client = MagicMock()
    monkeypatch.setattr("orchestrator.memory.redis_client", mock_redis_client)
    
    # Create a mock ToolBox and override the app's dependency
    mock_toolbox = ToolBox(client=mock_http_client)
    app.dependency_overrides[get_toolbox] = lambda: mock_toolbox
    
    # Yield the test client and the toolbox for assertions
    with TestClient(app) as client:
        yield client, mock_toolbox

    # Clean up dependency overrides after the test
    app.dependency_overrides.clear()