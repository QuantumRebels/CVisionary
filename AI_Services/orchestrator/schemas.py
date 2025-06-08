from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class OrchestrateRequest(BaseModel):
    user_id: str
    job_description: str

class OrchestrateResponse(BaseModel):
    bullets: List[str]
    match_score: float
    suggestions: List[str]

# --- Schemas for internal tool interactions (examples) ---

class EmbedRequest(BaseModel):
    text: str

class EmbedResponse(BaseModel):
    # The actual structure depends on your Embedding Service
    # It could be a direct embedding or an ID to the stored embedding
    embedding: List[float] = Field(default_factory=list) # Example: [0.1, 0.2, ...]
    embedding_id: str = Field(default="") # Example: "emb_123xyz"

class RetrieveResponse(BaseModel):
    # Structure from your Retrieval Service
    chunks: List[str]
    # Potentially other metadata like source_documents, etc.

class GenerateToolInput(BaseModel):
    user_id: str = Field(..., description="The user ID.")
    job_description: str = Field(..., description="The target job description text.")
    # retrieved_chunks is optional as the downstream generator service might not use it directly.
    retrieved_chunks: Optional[List[str]] = Field(None, description="(Optional) Relevant resume chunks. May not be used by the generation service if its API doesn't support it.")

# Schema for the actual request payload to the Generator Service's /generate endpoint
class GenerateServiceRequest(BaseModel):
    job_description: str = Field(..., description="The target job description text.")
    # jd_embedding_id: Optional[str] = None 

class GenerateResponse(BaseModel):
    bullets: List[str] = Field(..., description="List of generated resume bullet points.")
    # Assuming the generator service might also return a raw_prompt, keeping it optional.
    raw_prompt: Optional[str] = Field(None, description="The raw prompt used for generation, if available.")

class ScoreRequest(BaseModel):
    generated_bullets: List[str]
    job_description: str
    # Potentially also user_id or jd_embedding_id if needed by Scoring Service

class ScoreResponse(BaseModel):
    score: float = Field(..., alias="match_score", description="The calculated match score between bullets and job description.")
    missing_keywords: Optional[List[str]] = Field(None, description="List of important keywords missing from the bullets.")
    suggestions: Optional[List[str]] = Field(None, description="Specific suggestions from the scoring service to improve the bullets.")

    class Config:
        populate_by_name = True # Allows using 'score' if 'match_score' is not in response, and vice-versa for input.

class SuggestExternalRequest(BaseModel):
    job_description: str
    current_bullets: List[str]
    match_score: float

class SuggestExternalResponse(BaseModel):
    suggestions: List[str]
