from pydantic import BaseModel, Field
from typing import List

class GenerateRequest(BaseModel):
    job_description: str = Field(..., description="Full job description text")

class GenerateResponse(BaseModel):
    bullets: List[str] = Field(..., description="List of generated bullet points")
    raw_prompt: str = Field(..., description="The prompt string sent to Gemini")
