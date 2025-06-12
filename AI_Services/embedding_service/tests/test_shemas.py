# test_schemas.py

import pytest
from pydantic import ValidationError
from datetime import datetime

from schemas import (
    EmbedRequest,
    IndexSectionRequest,
    RetrieveRequest,
    ChunkItem,
    IndexNamespace
)

def test_embed_request_schema():
    """Test validation for EmbedRequest."""
    # Happy path
    req = EmbedRequest(text="some valid text")
    assert req.text == "some valid text"

    # Unhappy path
    with pytest.raises(ValidationError):
        EmbedRequest(text="") # min_length=1

    with pytest.raises(ValidationError):
        EmbedRequest(text=None)

def test_index_section_request_schema():
    """Test validation for IndexSectionRequest."""
    # Happy path
    req = IndexSectionRequest(section_id="sec-1", text="some text")
    assert req.section_id == "sec-1"

    # Unhappy path
    with pytest.raises(ValidationError):
        IndexSectionRequest(section_id="sec-1", text="") # min_length=1

    with pytest.raises(ValidationError):
        IndexSectionRequest(section_id="", text="some text") # section_id is required

def test_retrieve_request_schema():
    """Test validation for RetrieveRequest."""
    valid_embedding = [0.0] * 384

    # Happy path with defaults
    req = RetrieveRequest(query_embedding=valid_embedding)
    assert req.top_k == 5
    assert req.index_namespace == "profile"
    assert req.filter_by_section_ids is None

    # Happy path with custom values
    req = RetrieveRequest(
        query_embedding=valid_embedding,
        top_k=10,
        index_namespace="resume_sections",
        filter_by_section_ids=["s1", "s2"]
    )
    assert req.top_k == 10
    assert req.index_namespace == "resume_sections"

    # Unhappy paths
    with pytest.raises(ValidationError, match="List should have at least 384 items"):
        RetrieveRequest(query_embedding=[0.0] * 100)

    with pytest.raises(ValidationError, match="List should have at most 384 items"):
        RetrieveRequest(query_embedding=[0.0] * 400)

    with pytest.raises(ValidationError, match="Input should be greater than or equal to 1"):
        RetrieveRequest(query_embedding=valid_embedding, top_k=0)

    with pytest.raises(ValidationError, match="Input should be less than or equal to 100"):
        RetrieveRequest(query_embedding=valid_embedding, top_k=101)

    with pytest.raises(ValidationError):
        RetrieveRequest(query_embedding=valid_embedding, index_namespace="invalid_namespace")

def test_chunk_item_schema():
    """Test the output schema for ChunkItem."""
    # This schema is for output, so we mainly test creation
    now = datetime.utcnow()
    item = ChunkItem(
        chunk_id="c1",
        user_id="u1",
        index_namespace="profile",
        section_id=None,
        source_type="experience",
        source_id="0",
        text="some text",
        score=0.99,
        created_at=now
    )
    assert item.score == 0.99
    assert item.created_at == now