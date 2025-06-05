from pydantic import BaseModel, Field
from typing import List, Optional

class EmbedRequest(BaseModel):
    """Request model for embedding text"""
    text: str = Field(..., description="Text to embed", min_length=1)

class EmbedResponse(BaseModel):
    """Response model for text embedding"""
    embedding: List[float] = Field(..., description="384-dimensional embedding vector")

class IndexResponse(BaseModel):
    """Response model for indexing operation"""
    status: str = Field(..., description="Status of indexing operation")
    num_chunks: int = Field(..., description="Number of chunks processed", ge=0)

class RetrieveRequest(BaseModel):
    """Request model for similarity search"""
    query_embedding: List[float] = Field(..., description="Query embedding vector", min_length=384, max_length=384) # Pydantic v2 uses min_length/max_length for lists
    top_k: int = Field(default=5, description="Number of top results to return", ge=1, le=100)

class ChunkItem(BaseModel):
    """Individual chunk item in search results"""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    user_id: str = Field(..., description="User identifier")
    source_type: str = Field(..., description="Type of source (experience, project, skills, etc.)")
    source_id: str = Field(..., description="Source identifier within type")
    text: str = Field(..., description="Chunk text content")
    score: float = Field(..., description="Similarity score")

class RetrieveResponse(BaseModel):
    """Response model for similarity search"""
    results: List[ChunkItem] = Field(..., description="List of similar chunks")