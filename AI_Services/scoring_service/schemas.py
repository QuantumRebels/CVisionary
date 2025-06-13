# schemas.py

from pydantic import BaseModel, Field
from typing import List

# --- /score endpoint schemas ---

class ScoreRequest(BaseModel):
    job_description: str = Field(..., description="Job description text to match against.", min_length=1)
    resume_text: str = Field(..., description="Resume text content to score.", min_length=1)

class ScoreResponse(BaseModel):
    match_score: float = Field(..., description="Semantic similarity score between 0 and 1.", ge=0.0, le=1.0)
    missing_keywords: List[str] = Field(..., description="List of important keywords from the job description that are missing from the resume.")

# --- /suggest endpoint schemas ---

class SuggestionRequest(BaseModel):
    missing_keywords: List[str] = Field(..., description="A list of keywords to generate suggestions for.", min_items=1)

class SuggestionResponse(BaseModel):
    suggestions: List[str] = Field(..., description="A list of actionable suggestions for improving the resume based on the missing keywords.")

# --- Health check schema ---

class HealthResponse(BaseModel):
    status: str
    service: str