# conftest.py

import pytest
import os
from unittest.mock import MagicMock, AsyncMock

from fastapi.testclient import TestClient
from httpx import Response, AsyncClient

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the main app and other modules
from app import app, get_http_client
import db
import faiss_index
import numpy as np

# A sample 384-dimensional embedding for testing
SAMPLE_EMBEDDING_384D = (
    (np.random.rand(384) - 0.5) * 0.1
).tolist()  # Small values, but 384d

# Sample data for mocking
SAMPLE_PROFILE_DATA = {
    "experience": [
        {
            "title": "Software Engineer",
            "description": "Developed a key feature. It was a great success and everyone was happy.",
        }
    ],
    "projects": [
        {
            "name": "Side Project",
            "description": "Built a cool app with Python. It solved a real-world problem.",
        }
    ],
    "skills": ["Python", "FastAPI", "Docker"],
    "summary": "A passionate developer.",
}


@pytest.fixture(scope="function")
def test_client(tmp_path, monkeypatch):
    """
    Fixture to create a test client with an isolated, temporary database.
    This runs for each test function to ensure a clean state.
    """
    # 1. Set up a temporary database for this test run
    db_path = tmp_path / "test_embeddings.db"
    monkeypatch.setattr(db, "DB_PATH", str(db_path))

    # 2. Mock the external profile service client
    mock_http_client = MagicMock(spec=AsyncClient)

    # 3. THIS IS THE KEY: Override the dependency within the app's context
    # This ensures that any part of the app that uses `get_http_client` will get our mock.
    app.dependency_overrides[get_http_client] = lambda: mock_http_client

    # 4. Initialize the database and FAISS indices
    db.init_db()
    faiss_index.user_indices.clear()  # Ensure FAISS is empty

    # 5. Yield the test client and the mock http client
    with TestClient(app) as client:
        yield client, mock_http_client

    # 6. Teardown: Clean up FAISS index and dependency overrides
    faiss_index.user_indices.clear()
    app.dependency_overrides.clear()