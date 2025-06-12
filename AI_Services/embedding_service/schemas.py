from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

# Literal type for controlled vocabulary
IndexNamespace = Literal["profile", "resume_sections"]

class EmbedRequest(BaseModel):
    """Request model for embedding text"""
    text: str = Field(..., description="Text to embed", min_length=1)

class EmbedResponse(BaseModel):
    """Response model for text embedding"""
    embedding: List[float] = Field(..., description="384-dimensional embedding vector")

class IndexProfileResponse(BaseModel):
    """Response model for full profile indexing operation"""
    status: str = Field(..., description="Status of indexing operation")
    num_chunks: int = Field(..., description="Number of chunks processed for the profile", ge=0)

class IndexSectionRequest(BaseModel):
    """Request model to index a single resume section/bullet."""
    section_id: str = Field(..., description="A unique identifier for the resume section or bullet being indexed.")
    text: str = Field(..., description="The text content of the section.", min_length=1)

class IndexSectionResponse(BaseModel):
    """Response model for section indexing operation"""
    status: str = Field(..., description="Status of the section indexing operation.")
    section_id: str = Field(..., description="The unique identifier for the processed section.")
    chunk_ids: List[str] = Field(..., description="List of new chunk IDs created for this section.")

class DeleteSectionResponse(BaseModel):
    """Response model for deleting a section."""
    status: str = Field(..., description="Status of the deletion operation.")
    section_id: str = Field(..., description="The unique identifier of the deleted section.")


class RetrieveRequest(BaseModel):
    """Request model for similarity search"""
    query_embedding: List[float] = Field(..., description="Query embedding vector", min_length=384, max_length=384)
    top_k: int = Field(default=5, description="Number of top results to return", ge=1, le=100)
    index_namespace: IndexNamespace = Field(default="profile", description="The index to search: 'profile' for general data or 'resume_sections' for user-edited chunks.")
    filter_by_section_ids: Optional[List[str]] = Field(default=None, description="Optional list of section_ids to filter results. Primarily for the 'resume_sections' namespace.")

class ChunkItem(BaseModel):
    """Individual chunk item in search results"""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    user_id: str = Field(..., description="User identifier")
    index_namespace: str = Field(..., description="The namespace this chunk belongs to ('profile' or 'resume_sections').")
    section_id: Optional[str] = Field(default=None, description="Identifier for a specific resume section, if applicable.")
    source_type: str = Field(..., description="Original source type (e.g., 'experience', 'user_edited').")
    source_id: str = Field(..., description="Original source identifier within type.")
    text: str = Field(..., description="Chunk text content")
    score: float = Field(..., description="Similarity score")
    created_at: datetime = Field(..., description="Timestamp of when the chunk was created/updated.")


class RetrieveResponse(BaseModel):
    """Response model for similarity search"""
    results: List[ChunkItem] = Field(..., description="List of similar chunks")