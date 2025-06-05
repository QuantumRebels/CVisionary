import pytest
from pydantic import ValidationError
from schemas import GenerateRequest, GenerateResponse


class TestGenerateRequest:
    def test_valid_request(self):
        """Test valid GenerateRequest creation."""
        request = GenerateRequest(job_description="Software Engineer role requiring Python and AWS")
        assert request.job_description == "Software Engineer role requiring Python and AWS"
    
    def test_missing_job_description(self):
        """Test GenerateRequest fails without job_description."""
        with pytest.raises(ValidationError):
            GenerateRequest()
    
    def test_empty_job_description(self):
        """Test GenerateRequest with empty job_description."""
        request = GenerateRequest(job_description="")
        assert request.job_description == ""
    
    def test_long_job_description(self):
        """Test GenerateRequest with very long job_description."""
        long_text = "A" * 10000
        request = GenerateRequest(job_description=long_text)
        assert request.job_description == long_text


class TestGenerateResponse:
    def test_valid_response(self):
        """Test valid GenerateResponse creation."""
        bullets = ["Bullet 1", "Bullet 2", "Bullet 3"]
        prompt = "Test prompt"
        response = GenerateResponse(bullets=bullets, raw_prompt=prompt)
        assert response.bullets == bullets
        assert response.raw_prompt == prompt
    
    def test_empty_bullets(self):
        """Test GenerateResponse with empty bullets list."""
        response = GenerateResponse(bullets=[], raw_prompt="Test prompt")
        assert response.bullets == []
        assert response.raw_prompt == "Test prompt"
    
    def test_missing_bullets(self):
        """Test GenerateResponse fails without bullets."""
        with pytest.raises(ValidationError):
            GenerateResponse(raw_prompt="Test prompt")
    
    def test_missing_raw_prompt(self):
        """Test GenerateResponse fails without raw_prompt."""
        with pytest.raises(ValidationError):
            GenerateResponse(bullets=["Bullet 1"])
    
    def test_invalid_bullets_type(self):
        """Test GenerateResponse fails with non-list bullets."""
        with pytest.raises(ValidationError):
            GenerateResponse(bullets="Not a list", raw_prompt="Test prompt")