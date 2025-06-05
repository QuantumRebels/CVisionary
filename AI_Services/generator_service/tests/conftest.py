# conftest.py

import os
import sys
import pytest
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock, AsyncMock
import importlib # <<< ADDED

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly after adding parent to path
from schemas import GenerateRequest, GenerateResponse
# NOTE: It's generally better to import 'app' inside fixtures that need it,
# especially if it needs to be reloaded.

@pytest.fixture
def sample_job_description() -> str:
    """Sample job description for testing"""
    return """
    We are looking for a Senior Python Developer with 5+ years of experience.
    Must have expertise in FastAPI, Docker, and cloud platforms like AWS.
    Experience with machine learning and data processing is a plus.
    """.strip()


@pytest.fixture
def sample_generate_request(sample_job_description: str) -> Dict[str, Any]:
    """Sample generate request payload"""
    return {"job_description": sample_job_description}


@pytest.fixture
def sample_generate_response() -> Dict[str, Any]:
    """Sample generate response"""
    return {
        "bullets": [
            "5+ years of experience in Python development with FastAPI expertise",
            "Strong knowledge of containerization using Docker",
            "Experience with cloud platforms, particularly AWS"
        ],
        "raw_prompt": "Generated prompt would be here..."
    }


@pytest.fixture
def mock_llm_response() -> List[str]:
    """Mock LLM response"""
    return [
        "5+ years of experience in Python development with FastAPI expertise",
        "Strong knowledge of containerization using Docker",
        "Experience with cloud platforms, particularly AWS"
    ]


@pytest.fixture
def mock_embedding_service_response() -> Dict[str, Any]:
    """Mock embedding service response"""
    return {
        "embedding": [0.1] * 384,  # Mock 384-dimensional embedding
        "status": "success"
    }


@pytest.fixture
def mock_retrieve_service_response() -> Dict[str, Any]:
    """Mock retrieve service response"""
    return {
        "results": [
            {
                "chunk_id": "1",
                "user_id": "test_user",
                "source_type": "resume",
                "source_id": "resume1",
                "text": "Python developer with 5 years experience in FastAPI and AWS",
                "score": 0.9
            },
            {
                "chunk_id": "2",
                "user_id": "test_user",
                "source_type": "project",
                "source_id": "project1",
                "text": "Built scalable microservices using Docker and Kubernetes",
                "score": 0.85
            }
        ]
    }


@pytest.fixture(autouse=True)
def mock_environment_variables():
    """Mock environment variables for testing.
    This autouse fixture ensures os.environ is patched before each test run.
    """
    with patch.dict('os.environ', {
        'GEMINI_API_KEY': 'test-api-key',
        'EMBEDDING_SERVICE_URL': 'http://localhost:8001',
        'GEMINI_API_URL': 'https://api.gemini.google/v1/generateText'
    }):
        yield


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient"""
    with patch('httpx.AsyncClient') as mock_client: # This patches httpx.AsyncClient globally
        yield mock_client


@pytest.fixture
def test_client():
    """Create test client for FastAPI app.
    Reloads the app module to ensure it picks up patched environment variables.
    """
    from fastapi.testclient import TestClient
    # We need to import the app module itself to reload it
    import app as app_module 
    importlib.reload(app_module)
    return TestClient(app_module.app)


@pytest.fixture(autouse=True)
def clear_caches():
    """Clear any caches before each test"""
    # Clear any module-level caches here if needed
    yield