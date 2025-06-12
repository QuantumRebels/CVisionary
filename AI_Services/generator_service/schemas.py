# schemas.py

"""
Pydantic models for API request/response schemas.
"""
import os
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class FullGenerateRequest(BaseModel):
    """Request model for full resume generation."""
    user_id: str = Field(..., description="Unique identifier for the user", min_length=1)
    job_description: str = Field(..., description="Job description to tailor resume for", min_length=1)
    top_k: int = Field(
        default_factory=lambda: int(os.getenv("DEFAULT_TOP_K", "7")),
        description="Number of top chunks to retrieve",
        ge=1,
        le=50,
    )


class SectionGenerateRequest(BaseModel):
    """Request model for section-specific resume generation."""
    user_id: str = Field(..., description="Unique identifier for the user", min_length=1)
    section_id: str = Field(..., description="ID of the section to generate/rewrite", min_length=1)
    job_description: str = Field(..., description="Job description to tailor section for", min_length=1)
    existing_text: Optional[str] = Field(None, description="Existing text to enhance/rewrite")
    top_k: int = Field(
        default_factory=lambda: int(os.getenv("DEFAULT_TOP_K", "7")),
        description="Number of top chunks to retrieve",
        ge=1,
        le=50,
    )


class ChunkItem(BaseModel):
    """Model representing a retrieved context chunk from the Retrieval Service."""
    chunk_id: str = Field(..., description="Unique identifier for the chunk")
    user_id: str = Field(..., description="User who owns this chunk")
    index_namespace: str = Field(..., description="Namespace in the vector index ('profile' or 'resume_sections')")
    # FIX: section_id can be None, especially for chunks from the 'profile' namespace.
    section_id: Optional[str] = Field(None, description="Section this chunk belongs to, if applicable")
    source_type: str = Field(..., description="Original source of the text (e.g., 'experience', 'user_edited')")
    source_id: str = Field(..., description="ID of the source document within the source type")
    text: str = Field(..., description="The actual text content")
    score: float = Field(..., description="Relevance score from vector search")
    created_at: datetime = Field(..., description="When this chunk was created")


class GenerateResponse(BaseModel):
    """Response model for generation endpoints."""
    generated_text: str = Field(..., description="The AI-generated content, typically a JSON string")
    raw_prompt: str = Field(..., description="The full prompt sent to the LLM (for debugging)")
    retrieval_mode: str = Field(..., description="Mode used: 'full' or 'section'")
    section_id: Optional[str] = Field(None, description="Section ID for section-specific generation")


class RetrieveResponse(BaseModel):
    """
    Response model for data received from the Retrieval Service.
    This must match the schema defined in the Retrieval Service.
    """
    results: List[ChunkItem] = Field(
        ..., description="List of retrieved chunks ordered by relevance score (descending)"
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")