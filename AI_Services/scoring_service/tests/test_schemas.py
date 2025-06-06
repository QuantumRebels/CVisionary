import pytest
from pydantic import ValidationError
from ..schemas import ScoreRequest, ScoreResponse # Adjusted import path

class TestScoreRequest:
    def test_valid_score_request(self):
        data = {
            "job_description": "Need a Python dev.",
            "resume_text": "I am a Python dev."
        }
        req = ScoreRequest(**data)
        assert req.job_description == data["job_description"]
        assert req.resume_text == data["resume_text"]

    def test_score_request_empty_job_description(self):
        with pytest.raises(ValidationError):
            ScoreRequest(job_description="", resume_text="Valid resume")

    def test_score_request_empty_resume_text(self):
        with pytest.raises(ValidationError):
            ScoreRequest(job_description="Valid job desc", resume_text="")

    def test_score_request_job_description_too_long(self):
        with pytest.raises(ValidationError):
            ScoreRequest(job_description="a" * 50001, resume_text="Valid resume")

    def test_score_request_resume_text_too_long(self):
        with pytest.raises(ValidationError):
            ScoreRequest(job_description="Valid job desc", resume_text="a" * 50001)

    def test_score_request_example_is_valid(self):
        example = ScoreRequest.Config.schema_extra["example"]
        req = ScoreRequest(**example)
        assert req.job_description == example["job_description"]
        assert req.resume_text == example["resume_text"]

class TestScoreResponse:
    def test_valid_score_response(self):
        data = {
            "match_score": 0.75,
            "missing_keywords": ["AWS", "Docker"],
            "suggestions": ["Add AWS projects", "Learn Docker"]
        }
        res = ScoreResponse(**data)
        assert res.match_score == data["match_score"]
        assert res.missing_keywords == data["missing_keywords"]
        assert res.suggestions == data["suggestions"]

    def test_score_response_score_too_low(self):
        with pytest.raises(ValidationError):
            ScoreResponse(match_score=-0.1, missing_keywords=[], suggestions=[])

    def test_score_response_score_too_high(self):
        with pytest.raises(ValidationError):
            ScoreResponse(match_score=1.1, missing_keywords=[], suggestions=[])

    def test_score_response_missing_keywords_not_list(self):
        with pytest.raises(ValidationError):
            ScoreResponse(match_score=0.5, missing_keywords="AWS", suggestions=[])

    def test_score_response_suggestions_not_list(self):
        with pytest.raises(ValidationError):
            ScoreResponse(match_score=0.5, missing_keywords=[], suggestions="Learn AWS")

    def test_score_response_example_is_valid(self):
        example = ScoreResponse.Config.schema_extra["example"]
        res = ScoreResponse(**example)
        assert res.match_score == example["match_score"]
        assert res.missing_keywords == example["missing_keywords"]
        assert res.suggestions == example["suggestions"]
