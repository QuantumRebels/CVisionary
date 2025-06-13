# tests/conftest.py

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the main app and the ToolBox
from app import app, get_toolbox
from tools import ToolBox

def pytest_configure():
    """Configure pytest and set environment variables."""
    import os
    os.environ["RETRIEVAL_SERVICE_URL"] = "http://mock-retrieval-service:8000"
    os.environ["GENERATION_SERVICE_URL"] = "http://mock-generator-service:8000"
    os.environ["GEMINI_API_KEY"] = "test-api-key"
    os.environ["REDIS_URL"] = "redis://mock-redis:6379"

@pytest.fixture
def mock_http_client():
    """Provides a mock httpx.AsyncClient."""
    return MagicMock(spec=AsyncClient)

@pytest.fixture
def test_client(mock_http_client, monkeypatch):
    """
    Fixture to create a test client with a mocked ToolBox and Redis.
    """
    # Mock redis to prevent connection errors during app startup and in any module.
    mock_redis_instance = MagicMock()
    mock_redis_instance.ping.return_value = True
    
    # Patch redis in the app lifespan
    monkeypatch.setattr("app.redis.from_url", lambda *args, **kwargs: mock_redis_instance)
    # Patch redis in the memory module to cover all uses (the global client and the history object)
    monkeypatch.setattr("memory.redis.from_url", lambda *args, **kwargs: mock_redis_instance)
    
    # Create a toolbox instance with the mocked client
    mock_toolbox = ToolBox(client=mock_http_client)
    
    # Use FastAPI's dependency override to replace the real toolbox with our mock
    app.dependency_overrides[get_toolbox] = lambda: mock_toolbox
    
    with TestClient(app) as client:
        yield client, mock_toolbox

    # Clean up the override after the test
    app.dependency_overrides.clear()