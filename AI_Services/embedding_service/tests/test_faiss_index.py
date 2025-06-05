import pytest
import numpy as np
import faiss
from unittest.mock import patch

from faiss_index import (
    build_index_from_db, add_to_index, search, user_indices
)

class TestFaissIndex:
    
    def test_build_index_from_db_empty(self):
        """Test building index from empty database"""
        build_index_from_db([])
        assert len(user_indices) == 0
    
    def test_build_index_from_db_single_user(self, sample_embedding):
        """Test building index for single user with multiple chunks"""
        embedding_blob = sample_embedding.tobytes()
        
        chunks = [
            ("chunk_1", "user_1", "experience", "0", "Text 1", embedding_blob),
            ("chunk_2", "user_1", "project", "0", "Text 2", embedding_blob),
        ]
        
        build_index_from_db(chunks)
        
        assert len(user_indices) == 1
        assert "user_1" in user_indices
        
        index, id_to_chunk_id = user_indices["user_1"]
        assert isinstance(index, faiss.IndexFlatIP)
        assert index.ntotal == 2
        assert len(id_to_chunk_id) == 2
        assert 0 in id_to_chunk_id
        assert 1 in id_to_chunk_id
    
    def test_build_index_from_db_multiple_users(self, sample_embedding):
        """Test building indices for multiple users"""
        embedding_blob = sample_embedding.tobytes()
        
        chunks = [
            ("chunk_1", "user_1", "experience", "0", "Text 1", embedding_blob),
            ("chunk_2", "user_2", "experience", "0", "Text 2", embedding_blob),
            ("chunk_3", "user_1", "project", "0", "Text 3", embedding_blob),
        ]
        
        build_index_from_db(chunks)
        
        assert len(user_indices) == 2
        assert "user_1" in user_indices
        assert "user_2" in user_indices
        
        # Check user_1 has 2 chunks
        index_1, id_to_chunk_id_1 = user_indices["user_1"]
        assert index_1.ntotal == 2
        assert len(id_to_chunk_id_1) == 2
        
        # Check user_2 has 1 chunk
        index_2, id_to_chunk_id_2 = user_indices["user_2"]
        assert index_2.ntotal == 1
        assert len(id_to_chunk_id_2) == 1
    
    def test_add_to_index_new_user(self, sample_embedding):
        """Test adding embedding for new user"""
        user_id = "new_user"
        chunk_id = "chunk_1"
        
        add_to_index(user_id, chunk_id, sample_embedding)
        
        assert user_id in user_indices
        index, id_to_chunk_id = user_indices[user_id]
        assert index.ntotal == 1
        assert 0 in id_to_chunk_id
        assert id_to_chunk_id[0] == chunk_id
    
    def test_add_to_index_existing_user(self, sample_embedding):
        """Test adding embedding for existing user"""
        user_id = "existing_user"
        
        # Add first embedding
        add_to_index(user_id, "chunk_1", sample_embedding)
        
        # Add second embedding
        embedding_2 = np.random.randn(384).astype(np.float32)
        embedding_2 = embedding_2 / np.linalg.norm(embedding_2)
        add_to_index(user_id, "chunk_2", embedding_2)
        
        index, id_to_chunk_id = user_indices[user_id]
        assert index.ntotal == 2
        assert len(id_to_chunk_id) == 2
        assert id_to_chunk_id[0] == "chunk_1"
        assert id_to_chunk_id[1] == "chunk_2"
    
    def test_search_user_not_found(self, sample_embedding):
        """Test searching for non-existent user"""
        chunk_ids, scores = search("nonexistent_user", sample_embedding, 5)
        assert chunk_ids == []
        assert scores == []
    
    def test_search_empty_index(self, sample_embedding):
        """Test searching in empty index"""
        user_id = "empty_user"
        # Create empty index
        user_indices[user_id] = (faiss.IndexFlatIP(384), {})
        
        chunk_ids, scores = search(user_id, sample_embedding, 5)
        assert chunk_ids == []
        assert scores == []
    
    def test_search_success(self, sample_embedding):
        """Test successful search"""
        user_id = "test_user"
        
        # Add some embeddings
        embedding_1 = np.random.randn(384).astype(np.float32)
        embedding_1 = embedding_1 / np.linalg.norm(embedding_1)
        embedding_2 = np.random.randn(384).astype(np.float32)
        embedding_2 = embedding_2 / np.linalg.norm(embedding_2)
        
        add_to_index(user_id, "chunk_1", embedding_1)
        add_to_index(user_id, "chunk_2", embedding_2)
        
        # Search with one of the embeddings (should return exact match)
        chunk_ids, scores = search(user_id, embedding_1, 2)
        
        assert len(chunk_ids) == 2
        assert len(scores) == 2
        assert "chunk_1" in chunk_ids
        assert "chunk_2" in chunk_ids
        
        # First result should be the exact match with highest score
        first_chunk_index = chunk_ids.index("chunk_1")
        assert scores[first_chunk_index] > scores[1 - first_chunk_index]
    
    def test_search_top_k_limit(self, sample_embedding):
        """Test search respects top_k limit"""
        user_id = "test_user"
        
        # Add 5 embeddings
        for i in range(5):
            embedding = np.random.randn(384).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)
            add_to_index(user_id, f"chunk_{i}", embedding)
        
        # Search with top_k=3
        chunk_ids, scores = search(user_id, sample_embedding, 3)
        
        assert len(chunk_ids) == 3
        assert len(scores) == 3
    
    def test_search_top_k_exceeds_available(self, sample_embedding):
        """Test search when top_k exceeds available chunks"""
        user_id = "test_user"
        
        # Add only 2 embeddings
        for i in range(2):
            embedding = np.random.randn(384).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)
            add_to_index(user_id, f"chunk_{i}", embedding)
        
        # Search with top_k=5 (more than available)
        chunk_ids, scores = search(user_id, sample_embedding, 5)
        
        # Should return only available chunks
        assert len(chunk_ids) == 2
        assert len(scores) == 2
    
    def test_embedding_dimension_consistency(self):
        """Test that all operations use 384-dimensional embeddings"""
        user_id = "test_user"
        
        # Try to add wrong-dimensional embedding
        wrong_embedding = np.random.randn(256).astype(np.float32)
        
        with pytest.raises(Exception):
            add_to_index(user_id, "chunk_1", wrong_embedding)