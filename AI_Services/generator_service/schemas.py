"""
Pydantic models for API request/response schemas.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class FullGenerateRequest(BaseModel):
    """Request model for full resume generation."""
    user_id: str = Field(..., description="Unique identifier for the user")
    job_description: str = Field(..., description="Job description to tailor resume for")
    top_k: Optional[int] = Field(None, description="Number of top chunks to retrieve")


class SectionGenerateRequest(BaseModel):
    """Request model for section-specific resume generation."""
    user_id: str = Field(..., description="Unique identifier for the user")
    section_id: str = Field(..., description="ID of the section to generate/rewrite")
    job_description: str = Field(..., description="Job description to tailor section for")
    existing_text: Optional[str] = Field(None, description="Existing text to enhance/rewrite")
    top_k: Optional[int] = Field(None, description="Number of top chunks to retrieve")


class ChunkItem(BaseModel):
    """Model representing a retrieved context chunk from the Retrieval Service."""
    chunk_id: str = Field(..., description="Unique identifier for the chunk")
    user_id: str = Field(..., description="User who owns this chunk")
    index_namespace: str = Field(..., description="Namespace in the vector index")
    section_id: str = Field(..., description="Section this chunk belongs to")
    source_type: str = Field(..., description="Type of source (e.g., 'profile', 'section')")
    source_id: str = Field(..., description="ID of the source document")
    text: str = Field(..., description="The actual text content")
    score: float = Field(..., description="Relevance score from vector search")
    created_at: datetime = Field(..., description="When this chunk was created")


class GenerateResponse(BaseModel):
    """Response model for generation endpoints."""
    generated_text: str = Field(..., description="The AI-generated content")
    raw_prompt: str = Field(..., description="The full prompt sent to the LLM (for debugging)")
    retrieval_mode: str = Field(..., description="Mode used: 'full' or 'section'")
    section_id: Optional[str] = Field(None, description="Section ID for section-specific generation")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")