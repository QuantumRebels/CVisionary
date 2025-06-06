from pydantic import BaseModel, Field
from typing import List

class ScoreRequest(BaseModel):
    """
    Request model for resume scoring endpoint
    """
    job_description: str = Field(
        ...,
        description="Job description text to match against",
        min_length=1,
        max_length=50000
    )
    resume_text: str = Field(
        ...,
        description="Resume text content to score",
        min_length=1,
        max_length=50000
    )
    
    class Config:
        schema_extra = {
            "example": {
                "job_description": "We are looking for a Python developer with experience in Django, REST APIs, and AWS cloud services. The ideal candidate should have knowledge of Docker, Kubernetes, and CI/CD pipelines.",
                "resume_text": "Software Engineer with 3 years of experience in Python development. Proficient in Django framework and building REST APIs. Experience with MySQL databases and Git version control."
            }
        }

class ScoreResponse(BaseModel):
    """
    Response model for resume scoring endpoint
    """
    match_score: float = Field(
        ...,
        description="Match score between 0 and 1, where 1 is perfect match",
        ge=0.0,
        le=1.0
    )
    missing_keywords: List[str] = Field(
        ...,
        description="List of required skills/keywords missing from the resume"
    )
    suggestions: List[str] = Field(
        ...,
        description="List of AI-generated suggestions for improving the resume"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "match_score": 0.65,
                "missing_keywords": ["AWS", "Docker", "Kubernetes"],
                "suggestions": [
                    "Add AWS certification or cloud project experience to demonstrate cloud skills",
                    "Include Docker containerization examples from personal or work projects",
                    "Mention Kubernetes orchestration experience or online course completion"
                ]
            }
        }