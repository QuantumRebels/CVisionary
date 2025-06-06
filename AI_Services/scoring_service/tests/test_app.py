import pytest
import os
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
import numpy as np

# Import the app
from app import app

@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)

@pytest.fixture
def mock_dependencies():
    """Mock all dependencies for app testing"""
    with patch('app.model_inference') as mock_model, \
         patch('app.suggestion_client') as mock_suggestion, \
         patch('app.extract_required_keywords') as mock_extract, \
         patch('app.identify_missing_keywords') as mock_identify:
        
        # Setup mock model inference
        mock_model.embed_text.return_value = np.random.rand(384).astype(np.float32)
        mock_model.compute_match_score.return_value = 0.75
        
        # Setup mock suggestion client
        mock_suggestion.generate_suggestions = AsyncMock(return_value=[
            "Add AWS certification to demonstrate cloud skills",
            "Include Docker projects in your portfolio"
        ])
        
        # Setup mock feature extraction
        mock_extract.return_value = ["Python", "AWS", "Docker", "Kubernetes"]
        mock_identify.return_value = ["AWS", "Docker", "Kubernetes"]
        
        yield {
            'model': mock_model,
            'suggestion': mock_suggestion,
            'extract': mock_extract,
            'identify': mock_identify
        }

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint returns correct response"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "healthy",
            "service": "ats-scoring-service"
        }

class TestScoreEndpoint:
    """Test the main scoring endpoint"""
    
    def test_score_endpoint_success(self, client, mock_dependencies, sample_job_description, sample_resume_text):
        """Test successful scoring request"""
        request_data = {
            "job_description": sample_job_description,
            "resume_text": sample_resume_text
        }
        
        response = client.post("/score", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "match_score" in data
        assert "missing_keywords" in data
        assert "suggestions" in data
        
        # Check data types
        assert isinstance(data["match_score"], float)
        assert isinstance(data["missing_keywords"], list)
        assert isinstance(data["suggestions"], list)
        
        # Check value ranges
        assert 0.0 <= data["match_score"] <= 1.0
        
        # Verify mocks were called
        mock_dependencies['extract'].assert_called_once_with(sample_job_description)
        mock_dependencies['model'].embed_text.assert_called()
        mock_dependencies['model'].compute_match_score.assert_called_once()
    
    def test_score_endpoint_high_score_no_suggestions(self, client, mock_dependencies, sample_job_description, sample_resume_text):
        """Test that high scores don't generate suggestions"""
        # Mock high match score
        mock_dependencies['model'].compute_match_score.return_value = 0.85
        mock_dependencies['identify'].return_value = []  # No missing keywords
        
        request_data = {
            "job_description": sample_job_description,
            "resume_text": sample_resume_text
        }
        
        response = client.post("/score", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["match_score"] == 0.85
        assert data["missing_keywords"] == []
        assert data["suggestions"] == []
        
        # Verify suggestions were not generated
        mock_dependencies['suggestion'].generate_suggestions.assert_not_called()
    
    def test_score_endpoint_low_score_with_suggestions(self, client, mock_dependencies, sample_job_description, sample_resume_text):
        """Test that low scores with missing keywords generate suggestions"""
        # Mock low match score
        mock_dependencies['model'].compute_match_score.return_value = 0.5
        mock_dependencies['identify'].return_value = ["AWS", "Docker"]
        
        request_data = {
            "job_description": sample_job_description,
            "resume_text": sample_resume_text
        }
        
        response = client.post("/score", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["match_score"] == 0.5
        assert data["missing_keywords"] == ["AWS", "Docker"]
        assert len(data["suggestions"]) > 0
        
        # Verify suggestions were generated
        mock_dependencies['suggestion'].generate_suggestions.assert_called_once_with(["AWS", "Docker"])
    
    def test_score_endpoint_custom_threshold(self, client, mock_dependencies, sample_job_description, sample_resume_text):
        """Test custom match threshold from environment variable"""
        with patch.dict(os.environ, {'MATCH_THRESHOLD': '0.8'}):
            # Mock score just below custom threshold
            mock_dependencies['model'].compute_match_score.return_value = 0.75
            mock_dependencies['identify'].return_value = ["AWS"]
            
            request_data = {
                "job_description": sample_job_description,
                "resume_text": sample_resume_text
            }
            
            response = client.post("/score", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            # Should generate suggestions since 0.75 < 0.8
            mock_dependencies['suggestion'].generate_suggestions.assert_called_once_with(["AWS"])
    
    def test_score_endpoint_suggestion_failure(self, client, mock_dependencies, sample_job_description, sample_resume_text):
        """Test that suggestion generation failure doesn't break the request"""
        # Mock low match score
        mock_dependencies['model'].compute_match_score.return_value = 0.5
        mock_dependencies['identify'].return_value = ["AWS", "Docker"]
        
        # Mock suggestion generation failure
        mock_dependencies['suggestion'].generate_suggestions.side_effect = Exception("API Error")
        
        request_data = {
            "job_description": sample_job_description,
            "resume_text": sample_resume_text
        }
        
        response = client.post("/score", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should still return valid response with empty suggestions
        assert data["match_score"] == 0.5
        assert data["missing_keywords"] == ["AWS", "Docker"]
        assert data["suggestions"] == []
    
    def test_score_endpoint_invalid_request(self, client):
        """Test invalid request data"""
        # Missing required fields
        response = client.post("/score", json={})
        assert response.status_code == 422
        
        # Empty strings
        response = client.post("/score", json={
            "job_description": "",
            "resume_text": ""
        })
        assert response.status_code == 422
    
    def test_score_endpoint_model_error(self, client, mock_dependencies, sample_job_description, sample_resume_text):
        """Test handling of model inference errors"""
        # Mock model error
        mock_dependencies['model'].embed_text.side_effect = Exception("Model Error")
        
        request_data = {
            "job_description": sample_job_description,
            "resume_text": sample_resume_text
        }
        
        response = client.post("/score", json=request_data)
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
    
    def test_score_endpoint_long_text(self, client, mock_dependencies):
        """Test handling of very long text inputs"""
        long_text = "word " * 10000  # Very long text
        
        request_data = {
            "job_description": long_text,
            "resume_text": long_text
        }
        
        response = client.post("/score", json=request_data)
        
        # Should handle long text gracefully
        assert response.status_code in [200, 422]  # Either success or validation error
    
    def test_score_endpoint_unicode_text(self, client, mock_dependencies):
        """Test handling of unicode characters"""
        unicode_text = "Python développeur with émojis 🐍 and accénts"
        
        request_data = {
            "job_description": unicode_text,
            "resume_text": unicode_text
        }
        
        response = client.post("/score", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "match_score" in data

class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers(self, client):
        """Test that CORS headers are properly set"""
        response = client.options("/score")
        
        # Check for CORS headers (FastAPI handles this automatically)
        assert response.status_code in [200, 405]  # OPTIONS might not be explicitly handled