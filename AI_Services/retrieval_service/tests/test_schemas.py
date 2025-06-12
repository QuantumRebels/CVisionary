# AI_Services/retrieval_service/tests/test_schemas.py

import pytest
from pydantic import ValidationError
from datetime import datetime

from schemas import (
    FullRetrieveRequest,
    SectionRetrieveRequest,
    ChunkItem,
    RetrieveResponse,
)

def test_full_retrieve_request_validation():
    """Test validation for FullRetrieveRequest."""
    # Happy path
    req = FullRetrieveRequest(user_id="u1", job_description="jd1")
    assert req.top_k == 5  # Checks default

    # Unhappy paths
    with pytest.raises(ValidationError):
        FullRetrieveRequest(user_id="", job_description="jd1")

    with pytest.raises(ValidationError):
        FullRetrieveRequest(user_id="u1", job_description="jd1", top_k=100)


def test_section_retrieve_request_validation():
    """Test validation for SectionRetrieveRequest."""
    # Happy path
    req = SectionRetrieveRequest(user_id="u1", section_id="s1", job_description="jd1")
    assert req.section_id == "s1"

    # Unhappy path
    with pytest.raises(ValidationError):
        SectionRetrieveRequest(user_id="u1", section_id="", job_description="jd1")


def test_chunk_item_parsing():
    """Test that ChunkItem can parse a valid dictionary."""
    data = {
        "chunk_id": "c1",
        "user_id": "u1",
        "index_namespace": "profile",
        "section_id": None,
        "source_type": "experience",
        "source_id": "0",
        "text": "some text",
        "score": 0.99,
        "created_at": datetime.utcnow().isoformat(),
    }
    item = ChunkItem(**data)
    assert item.chunk_id == "c1"
    assert item.score == 0.99


def test_retrieve_response_parsing():
    """Test that RetrieveResponse can parse a list of valid chunks."""
    data = {
        "results": [
            {
                "chunk_id": "c1",
                "user_id": "u1",
                "index_namespace": "profile",
                "section_id": None,
                "source_type": "experience",
                "source_id": "0",
                "text": "some text",
                "score": 0.99,
                "created_at": datetime.utcnow().isoformat(),
            }
        ]
    }
    response = RetrieveResponse(**data)
    assert len(response.results) == 1
    assert isinstance(response.results[0], ChunkItem)