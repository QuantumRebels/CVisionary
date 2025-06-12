# test_faiss_index.py

import numpy as np
from unittest.mock import MagicMock
import faiss_index

# Mock sqlite3.Row to behave like a dictionary
class MockRow(dict):
    def __init__(self, *args, **kwargs):
        super(MockRow, self).__init__(*args, **kwargs)
        self.__dict__ = self


def test_build_and_search_index():
    """Test building a FAISS index from mock DB rows and searching it."""
    # Arrange
    faiss_index.user_indices.clear()
    # FIX: Use 384-dimensional vectors
    vec1 = (np.random.rand(384) - 0.5).astype(np.float32)
    vec1 /= np.linalg.norm(vec1)  # Normalize
    vec2 = (np.random.rand(384) - 0.5).astype(np.float32)
    vec2 /= np.linalg.norm(vec2)  # Normalize

    mock_rows = [
        MockRow(
            chunk_id="c1",
            user_id="u1",
            index_namespace="profile",
            embedding=vec1.tobytes(),
        ),
        MockRow(
            chunk_id="c2",
            user_id="u1",
            index_namespace="profile",
            embedding=vec2.tobytes(),
        ),
    ]

    # Act: Build
    faiss_index.build_index_from_db(mock_rows)

    # Assert: Build
    assert "u1" in faiss_index.user_indices
    assert "profile" in faiss_index.user_indices["u1"]
    index, _ = faiss_index.user_indices["u1"]["profile"]
    assert index.ntotal == 2

    # Act: Search with a query vector very close to vec1
    query_vec = (vec1 + (np.random.rand(384) - 0.5) * 0.01).astype(np.float32)
    chunk_ids, scores = faiss_index.search("u1", "profile", query_vec, top_k=1)

    # Assert: Search
    assert len(chunk_ids) == 1
    assert chunk_ids[0] == "c1"
    assert scores[0] > 0.9


def test_rebuild_index(monkeypatch):
    """Test rebuilding an index for a specific user/namespace."""
    # Arrange
    faiss_index.user_indices.clear()
    # FIX: Use a 384-dimensional vector
    vec1 = (np.random.rand(384) - 0.5).astype(np.float32)
    mock_rows = [
        MockRow(
            chunk_id="c1",
            user_id="u1",
            index_namespace="profile",
            embedding=vec1.tobytes(),
        )
    ]

    # Mock the DB call
    mock_get_chunks = MagicMock(return_value=mock_rows)
    monkeypatch.setattr(faiss_index, "get_user_chunks_by_namespace", mock_get_chunks)

    # Act
    faiss_index.rebuild_index_for_user_namespace("u1", "profile")

    # Assert
    mock_get_chunks.assert_called_once_with("u1", "profile")
    assert "u1" in faiss_index.user_indices
    index, id_map = faiss_index.user_indices["u1"]["profile"]
    assert index.ntotal == 1
    assert id_map[0] == "c1"


def test_delete_index():
    """Test deleting an index from the global dictionary."""
    # Arrange
    faiss_index.user_indices = {
        "u1": {"profile": (None, None), "resume_sections": (None, None)}
    }

    # Act: Delete a namespace
    faiss_index.delete_user_index("u1", "profile")
    # Assert
    assert "profile" not in faiss_index.user_indices["u1"]
    assert "resume_sections" in faiss_index.user_indices["u1"]

    # Act: Delete the whole user
    faiss_index.delete_user_index("u1")
    # Assert
    assert "u1" not in faiss_index.user_indices