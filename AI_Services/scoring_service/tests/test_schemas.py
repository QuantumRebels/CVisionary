import pytest
from pydantic import ValidationError

from scoring_service.schemas import (
    ScoreRequest,
    ScoreResponse,
    SuggestionRequest,
)

def test_score_request_validation():
    ScoreRequest(job_description="jd", resume_text="resume")
    with pytest.raises(ValidationError):
        ScoreRequest(job_description="", resume_text="resume")

def test_score_response_validation():
    ScoreResponse(match_score=0.75, missing_keywords=["AWS"])
    with pytest.raises(ValidationError):
        ScoreResponse(match_score=-0.1, missing_keywords=[])
    with pytest.raises(ValidationError):
        ScoreResponse(match_score=1.1, missing_keywords=[])

def test_suggestion_request_validation():
    SuggestionRequest(missing_keywords=["Docker"])
    with pytest.raises(ValidationError):
        SuggestionRequest(missing_keywords=[])