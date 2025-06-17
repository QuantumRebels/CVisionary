import pytest
from unittest.mock import MagicMock, AsyncMock
from httpx import Response, Request
from fastapi.testclient import TestClient

from scoring_service.app import app, get_model_inference, get_http_client
from scoring_service.model_inference import ModelInference

@pytest.fixture
def client():
    mock_model_inference = MagicMock(spec=ModelInference)
    mock_model_inference.compute_match_score.return_value = 0.85
    
    mock_http_client = MagicMock()
    mock_gemini_response = {"candidates": [{"content": {"parts": [{"text": "- Suggestion 1"}]}}]}
    mock_http_client.post = AsyncMock(return_value=Response(200, json=mock_gemini_response, request=Request("POST", "")))

    app.dependency_overrides[get_model_inference] = lambda: mock_model_inference
    app.dependency_overrides[get_http_client] = lambda: mock_http_client
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "scoring-service"}

def test_score_endpoint(client):
    response = client.post("/score", json={"job_description": "Python expert.", "resume_text": "I used Python."})
    assert response.status_code == 200
    data = response.json()
    assert data["match_score"] == 0.85
    model_mock = app.dependency_overrides[get_model_inference]()
    model_mock.compute_match_score.assert_called_once()

def test_suggest_endpoint(client):
    response = client.post("/suggest", json={"missing_keywords": ["AWS"]})
    assert response.status_code == 200
    data = response.json()
    assert data["suggestions"] == ["Suggestion 1"]
    client_mock = app.dependency_overrides[get_http_client]()
    client_mock.post.assert_called_once()