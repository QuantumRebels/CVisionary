# schemas.py

"""
CVisionary Retrieval Service - Pydantic Schemas

This module defines the request and response models for the Retrieval Service.
"""

import os
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class FullRetrieveRequest(BaseModel):
    """
    Request model for full resume context retrieval.
    """
    user_id: str = Field(..., description="User identifier for profile lookup", min_length=1)
    job_description: str = Field(..., description="Job posting text for relevance matching", min_length=1)
    top_k: int = Field(
        default_factory=lambda: int(os.getenv("DEFAULT_TOP_K", "5")),
        description="Number of chunks to retrieve",
        ge=1,
        le=50,
    )


class SectionRetrieveRequest(BaseModel):
    """
    Request model for section-specific context retrieval.
    """
    user_id: str = Field(..., description="User identifier for profile lookup", min_length=1)
    section_id: str = Field(..., description="Resume section identifier", min_length=1)
    job_description: str = Field(..., description="Job posting text for relevance matching", min_length=1)
    top_k: int = Field(
        default_factory=lambda: int(os.getenv("DEFAULT_TOP_K", "5")),
        description="Number of chunks to retrieve",
        ge=1,
        le=50,
    )


class ChunkItem(BaseModel):
    """
    Model representing a retrieved chunk item from the Embedding Service.
    This schema is aligned with the Embedding Service's ChunkItem response.
    """
    chunk_id: str = Field(..., description="Unique chunk identifier")
    user_id: str = Field(..., description="Owner of the chunk")
    # FIX: Add missing fields to match the source
    index_namespace: str = Field(..., description="The namespace this chunk belongs to ('profile' or 'resume_sections')")
    section_id: Optional[str] = Field(None, description="Identifier for a specific resume section, if applicable")
    source_type: str = Field(..., description="Type of source document (e.g., 'experience', 'user_edited')")
    source_id: str = Field(..., description="Source document identifier")
    text: str = Field(..., description="Actual chunk content text")
    score: float = Field(..., description="Relevance score from embedding similarity")
    created_at: datetime = Field(..., description="Timestamp of when the chunk was created/updated")


class RetrieveResponse(BaseModel):
    """
    Response model for both full and section retrieval requests.
    """
    results: List[ChunkItem] = Field(
        ..., description="List of retrieved chunks ordered by relevance score (descending)"
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service health status")
    service: str = Field(default="retrieval", description="Service name")