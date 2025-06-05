import pytest
import sqlite3
import numpy as np
from datetime import datetime

from db import (
    init_db, store_chunk, get_all_chunks, get_chunk_by_id, 
    mark_user_indexed, get_user_chunks, get_connection
)

class TestDatabase:
    
    def test_init_db_creates_tables(self, temp_db):
        """Test that init_db creates the required tables"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert cursor.fetchone() is not None
        
        # Check chunks table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chunks'")
        assert cursor.fetchone() is not None
        
        # Check index exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_chunks_user_id'")
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_store_chunk(self, temp_db, sample_embedding):
        """Test storing a chunk in the database"""
        chunk_id = "test_chunk_1"
        user_id = "test_user"
        source_type = "experience"
        source_id = "0"
        text = "This is a test chunk of text."
        embedding_bytes = sample_embedding.tobytes()
        
        store_chunk(chunk_id, user_id, source_type, source_id, text, embedding_bytes)
        
        # Verify the chunk was stored
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chunks WHERE chunk_id = ?", (chunk_id,))
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row['chunk_id'] == chunk_id
        assert row['user_id'] == user_id
        assert row['source_type'] == source_type
        assert row['source_id'] == source_id
        assert row['text'] == text
        assert row['embedding'] == embedding_bytes
    
    def test_get_chunk_by_id(self, temp_db, sample_embedding):
        """Test retrieving a chunk by ID"""
        chunk_id = "test_chunk_2"
        user_id = "test_user"
        source_type = "project"
        source_id = "1"
        text = "Another test chunk."
        embedding_bytes = sample_embedding.tobytes()
        
        # Store the chunk
        store_chunk(chunk_id, user_id, source_type, source_id, text, embedding_bytes)
        
        # Retrieve the chunk
        result = get_chunk_by_id(chunk_id)
        
        assert result is not None
        assert result[0] == chunk_id
        assert result[1] == user_id
        assert result[2] == source_type
        assert result[3] == source_id
        assert result[4] == text
        assert result[5] == embedding_bytes
    
    def test_get_chunk_by_id_not_found(self, temp_db):
        """Test retrieving a non-existent chunk"""
        result = get_chunk_by_id("nonexistent_chunk")
        assert result is None
    
    def test_get_all_chunks(self, temp_db, sample_embedding):
        """Test retrieving all chunks"""
        # Store multiple chunks
        chunks_data = [
            ("chunk_1", "user_1", "experience", "0", "Text 1", sample_embedding.tobytes()),
            ("chunk_2", "user_1", "project", "0", "Text 2", sample_embedding.tobytes()),
            ("chunk_3", "user_2", "skills", "0", "Text 3", sample_embedding.tobytes()),
        ]
        
        for chunk_data in chunks_data:
            store_chunk(*chunk_data)
        
        # Retrieve all chunks
        all_chunks = get_all_chunks()
        
        assert len(all_chunks) == 3
        
        # Verify the chunks are returned in the correct order (by user_id, source_type, source_id)
        chunk_ids = [chunk[0] for chunk in all_chunks]
        assert "chunk_1" in chunk_ids
        assert "chunk_2" in chunk_ids
        assert "chunk_3" in chunk_ids
    
    def test_get_user_chunks(self, temp_db, sample_embedding):
        """Test retrieving chunks for a specific user"""
        # Store chunks for different users
        store_chunk("chunk_1", "user_1", "experience", "0", "User 1 text", sample_embedding.tobytes())
        store_chunk("chunk_2", "user_1", "project", "0", "User 1 project", sample_embedding.tobytes())
        store_chunk("chunk_3", "user_2", "experience", "0", "User 2 text", sample_embedding.tobytes())
        
        # Get chunks for user_1
        user_1_chunks = get_user_chunks("user_1")
        assert len(user_1_chunks) == 2
        
        chunk_ids = [chunk[0] for chunk in user_1_chunks]
        assert "chunk_1" in chunk_ids
        assert "chunk_2" in chunk_ids
        assert "chunk_3" not in chunk_ids
        
        # Get chunks for user_2
        user_2_chunks = get_user_chunks("user_2")
        assert len(user_2_chunks) == 1
        assert user_2_chunks[0][0] == "chunk_3"
    
    def test_mark_user_indexed(self, temp_db):
        """Test marking a user as indexed"""
        user_id = "test_user"
        
        mark_user_indexed(user_id)
        
        # Verify the user was marked as indexed
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row['user_id'] == user_id
        assert row['last_indexed_at'] is not None
        
        # Verify the timestamp is recent (within last minute)
        indexed_time = datetime.fromisoformat(row['last_indexed_at'])
        time_diff = datetime.now() - indexed_time
        assert time_diff.total_seconds() < 60
    
    def test_mark_user_indexed_update(self, temp_db):
        """Test updating an existing user's indexed timestamp"""
        user_id = "test_user"
        
        # Mark user as indexed first time
        mark_user_indexed(user_id)
        
        # Get the first timestamp
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT last_indexed_at FROM users WHERE user_id = ?", (user_id,))
        first_timestamp = cursor.fetchone()['last_indexed_at']
        conn.close()
        
        # Wait a moment and mark again
        import time
        time.sleep(0.1)
        mark_user_indexed(user_id)
        
        # Get the second timestamp
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT last_indexed_at FROM users WHERE user_id = ?", (user_id,))
        second_timestamp = cursor.fetchone()['last_indexed_at']
        conn.close()
        
        # Verify the timestamp was updated
        assert second_timestamp != first_timestamp
        assert second_timestamp > first_timestamp