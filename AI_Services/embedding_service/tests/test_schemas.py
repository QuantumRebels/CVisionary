import pytest
from pydantic import ValidationError
import sys
import os

# Add parent directory of 'tests' to path to find 'schemas'
# This assumes 'tests' is a subdirectory of 'embedding_service'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import (
    EmbedRequest,
    EmbedResponse,
    IndexResponse,
    RetrieveRequest,
    ChunkItem,
    RetrieveResponse
)

# --- Test EmbedRequest ---
def test_embed_request_success():
    data = {"text": "This is a valid text."}
    req = EmbedRequest(**data)
    assert req.text == data["text"]

def test_embed_request_invalid_text_empty():
    with pytest.raises(ValidationError) as excinfo:
        EmbedRequest(text="") # min_length=1
    # Check if the specific error related to min_length is present
    assert any(e['type'] == 'string_too_short' and e['ctx'].get('min_length') == 1 for e in excinfo.value.errors())

def test_embed_request_missing_text():
    with pytest.raises(ValidationError) as excinfo:
        EmbedRequest() # text is required
    assert any(e['type'] == 'missing' and e['loc'] == ('text',) for e in excinfo.value.errors())


# --- Test EmbedResponse ---
def test_embed_response_success():
    data = {"embedding": [0.1] * 384}
    res = EmbedResponse(**data)
    assert res.embedding == data["embedding"]

def test_embed_response_missing_embedding():
    with pytest.raises(ValidationError):
        EmbedResponse()

def test_embed_response_invalid_embedding_type():
    with pytest.raises(ValidationError):
        EmbedResponse(embedding="not a list")


# --- Test IndexResponse ---
def test_index_response_success():
    data = {"status": "indexed", "num_chunks": 10}
    res = IndexResponse(**data)
    assert res.status == data["status"]
    assert res.num_chunks == data["num_chunks"]

def test_index_response_invalid_num_chunks_negative():
    with pytest.raises(ValidationError) as excinfo:
        IndexResponse(status="indexed", num_chunks=-1) # ge=0
    assert any(e['type'] == 'greater_than_equal' and e['ctx'].get('ge') == 0 for e in excinfo.value.errors())

def test_index_response_missing_fields():
    with pytest.raises(ValidationError):
        IndexResponse(status="indexed") # num_chunks missing
    with pytest.raises(ValidationError):
        IndexResponse(num_chunks=5) # status missing


# --- Test RetrieveRequest ---
def test_retrieve_request_success():
    data = {"query_embedding": [0.1] * 384, "top_k": 5}
    req = RetrieveRequest(**data)
    assert req.query_embedding == data["query_embedding"]
    assert req.top_k == data["top_k"]

def test_retrieve_request_default_top_k():
    data = {"query_embedding": [0.1] * 384}
    req = RetrieveRequest(**data)
    assert req.top_k == 5 # Default value

def test_retrieve_request_invalid_embedding_length_short():
    with pytest.raises(ValidationError) as excinfo:
        RetrieveRequest(query_embedding=[0.1] * 100, top_k=5) # min_items=384
    assert any(e['type'] == 'too_short' and e['ctx'].get('min_length') == 384 for e in excinfo.value.errors())

def test_retrieve_request_invalid_embedding_length_long():
    with pytest.raises(ValidationError) as excinfo:
        RetrieveRequest(query_embedding=[0.1] * 400, top_k=5) # max_items=384
    assert any(e['type'] == 'too_long' and e['ctx'].get('max_length') == 384 for e in excinfo.value.errors())

def test_retrieve_request_invalid_top_k_low():
    with pytest.raises(ValidationError) as excinfo:
        RetrieveRequest(query_embedding=[0.1] * 384, top_k=0) # ge=1
    assert any(e['type'] == 'greater_than_equal' and e['ctx'].get('ge') == 1 for e in excinfo.value.errors())

def test_retrieve_request_invalid_top_k_high():
    with pytest.raises(ValidationError) as excinfo:
        RetrieveRequest(query_embedding=[0.1] * 384, top_k=101) # le=100
    assert any(e['type'] == 'less_than_equal' and e['ctx'].get('le') == 100 for e in excinfo.value.errors())


# --- Test ChunkItem ---
def test_chunk_item_success():
    data = {
        "chunk_id": "id123",
        "user_id": "user456",
        "source_type": "experience",
        "source_id": "exp789",
        "text": "This is chunk text.",
        "score": 0.95
    }
    item = ChunkItem(**data)
    for key, value in data.items():
        assert getattr(item, key) == value

def test_chunk_item_missing_required_field():
    data = {
        "user_id": "user456",
        "source_type": "experience",
        "source_id": "exp789",
        "text": "This is chunk text.",
        "score": 0.95
    } # Missing chunk_id
    with pytest.raises(ValidationError):
        ChunkItem(**data)

def test_chunk_item_invalid_score_type():
    data = {
        "chunk_id": "id123",
        "user_id": "user456",
        "source_type": "experience",
        "source_id": "exp789",
        "text": "This is chunk text.",
        "score": "not_a_float"
    }
    with pytest.raises(ValidationError):
        ChunkItem(**data)


# --- Test RetrieveResponse ---
def test_retrieve_response_success():
    chunk_data = {
        "chunk_id": "id123", "user_id": "user456", "source_type": "experience",
        "source_id": "exp789", "text": "This is chunk text.", "score": 0.95
    }
    data = {"results": [ChunkItem(**chunk_data)]}
    res = RetrieveResponse(**data)
    assert len(res.results) == 1
    assert isinstance(res.results[0], ChunkItem)
    assert res.results[0].chunk_id == chunk_data["chunk_id"]

def test_retrieve_response_empty_results():
    data = {"results": []}
    res = RetrieveResponse(**data)
    assert len(res.results) == 0

def test_retrieve_response_invalid_results_type():
    with pytest.raises(ValidationError):
        RetrieveResponse(results="not_a_list")

def test_retrieve_response_invalid_item_in_results():
    with pytest.raises(ValidationError):
        RetrieveResponse(results=[{"not_a_chunk_item": True}])
