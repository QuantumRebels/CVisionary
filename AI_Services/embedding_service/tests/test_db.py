# test_db.py

import pytest
import sqlite3
import numpy as np
from datetime import datetime

import db

@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    """Fixture to provide an initialized, temporary database for each test."""
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db, "DB_PATH", str(db_path))
    db.init_db()
    return db_path

def test_init_db(isolated_db):
    """Test if database and tables are created correctly."""
    conn = sqlite3.connect(isolated_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chunks'")
    assert cursor.fetchone() is not None
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    assert cursor.fetchone() is not None
    conn.close()

def test_store_and_get_chunk(isolated_db):
    """Test storing a chunk and retrieving it by ID."""
    # Arrange
    chunk_id = "chunk-1"
    user_id = "user-1"
    embedding = np.array([0.1, 0.2], dtype=np.float32)

    # Act
    db.store_chunk(
        chunk_id=chunk_id, user_id=user_id, namespace="profile", section_id=None,
        source_type="summary", source_id="0", text="some text",
        embedding_bytes=embedding.tobytes()
    )
    retrieved_chunk = db.get_chunk_by_id(chunk_id)

    # Assert
    assert retrieved_chunk is not None
    assert retrieved_chunk["chunk_id"] == chunk_id
    assert retrieved_chunk["user_id"] == user_id
    assert retrieved_chunk["text"] == "some text"
    retrieved_embedding = np.frombuffer(retrieved_chunk["embedding"], dtype=np.float32)
    assert np.array_equal(embedding, retrieved_embedding)
    assert "created_at" in retrieved_chunk.keys()

def test_delete_logic(isolated_db):
    """Test the correctness of deletion functions."""
    # Arrange: Store chunks for different users, namespaces, and sections
    db.store_chunk("c1", "u1", "profile", None, "t", "i", "txt", b"")
    db.store_chunk("c2", "u1", "resume_sections", "s1", "t", "i", "txt", b"")
    db.store_chunk("c3", "u1", "resume_sections", "s2", "t", "i", "txt", b"")
    db.store_chunk("c4", "u2", "profile", None, "t", "i", "txt", b"")

    # Act 1: Delete a specific section
    deleted_count = db.delete_chunks_by_section_id("u1", "s1")
    # Assert 1
    assert deleted_count == 1
    assert db.get_chunk_by_id("c2") is None
    assert db.get_chunk_by_id("c3") is not None # s2 should remain

    # Act 2: Delete a whole namespace for a user
    deleted_count = db.delete_user_chunks("u1", "profile")
    # Assert 2
    assert deleted_count == 1
    assert db.get_chunk_by_id("c1") is None
    assert db.get_chunk_by_id("c4") is not None # u2 should remain

def test_get_user_chunks_by_namespace(isolated_db):
    """Test fetching chunks filtered by user and namespace."""
    # Arrange
    db.store_chunk("c1", "u1", "profile", None, "t", "i", "txt", b"")
    db.store_chunk("c2", "u1", "resume_sections", "s1", "t", "i", "txt", b"")

    # Act
    profile_chunks = db.get_user_chunks_by_namespace("u1", "profile")
    section_chunks = db.get_user_chunks_by_namespace("u1", "resume_sections")

    # Assert
    assert len(profile_chunks) == 1
    assert profile_chunks[0]["chunk_id"] == "c1"
    assert len(section_chunks) == 1
    assert section_chunks[0]["chunk_id"] == "c2"