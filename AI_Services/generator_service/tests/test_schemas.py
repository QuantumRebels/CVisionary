# tests/test_schemas.py

import pytest
from pydantic import ValidationError
from datetime import datetime

from schemas import (
    FullGenerateRequest,
    SectionGenerateRequest,
    ChunkItem,
)

def test_full_generate_request_validation():
    """Tests validation for the FullGenerateRequest schema."""
    # Happy path
    req = FullGenerateRequest(user_id="u1", job_description="jd")
    assert req.user_id == "u1"

    # Unhappy path (empty strings)
    with pytest.raises(ValidationError):
        FullGenerateRequest(user_id="", job_description="jd")
    with pytest.raises(ValidationError):
        FullGenerateRequest(user_id="u1", job_description="")

def test_section_generate_request_validation():
    """Tests validation for the SectionGenerateRequest schema."""
    # Happy path
    req = SectionGenerateRequest(user_id="u1", section_id="s1", job_description="jd")
    assert req.section_id == "s1"

    # Unhappy path (empty strings)
    with pytest.raises(ValidationError):
        SectionGenerateRequest(user_id="u1", section_id="", job_description="jd")

def test_chunk_item_schema_with_optional_section_id():
    """Ensures ChunkItem can handle a null section_id from the Retrieval Service."""
    # This is a critical test to ensure alignment
    chunk_data = {
        "chunk_id": "c1",
        "user_id": "u1",
        "index_namespace": "profile",
        "section_id": None, # This should be allowed
        "source_type": "experience",
        "source_id": "0",
        "text": "some text",
        "score": 0.9,
        "created_at": datetime.utcnow(),
    }
    try:
        ChunkItem(**chunk_data)
    except ValidationError as e:
        pytest.fail(f"ChunkItem failed to validate with section_id=None: {e}")