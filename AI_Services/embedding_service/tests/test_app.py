import pytest
import json
import numpy as np
from unittest.mock import patch, Mock, call
from fastapi.testclient import TestClient
import requests

# Import after adding parent directory to path
from app import chunk_text, extract_text_fields, lifespan # app is imported locally in fixtures
from schemas import ChunkItem

class TestApp:
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

class TestChunkText:
    
    def test_chunk_text_empty_input(self):
        """Test chunking empty or whitespace-only text"""
        assert chunk_text("") == []
        assert chunk_text("   ") == []
        assert chunk_text(None) == [] 
    
    def test_chunk_text_short_text(self):
        """Test chunking text shorter than max_words"""
        text = "This is a short sentence."
        result = chunk_text(text, max_words=150)
        assert len(result) == 1
        assert result[0] == text
    
    def test_chunk_text_long_text(self):
        """Test chunking long text"""
        sentences = [
            "This is the first sentence.",
            "This is the second sentence with more words to make it longer.",
            "Here is another sentence that continues the text.",
            "And finally, this is the last sentence in our test text."
        ]
        text = " ".join(sentences)
        result = chunk_text(text, max_words=15)
        assert len(result) > 1
        for chunk in result:
            assert chunk.endswith('.')
    
    def test_chunk_text_sentence_boundaries(self):
        """Test that chunks respect sentence boundaries"""
        text = "Short sentence. This is a much longer sentence with many words that exceeds our limit. Another short one."
        result = chunk_text(text, max_words=10)
        for chunk in result:
            assert chunk.strip().endswith(('.', '!', '?'))

class TestExtractTextFields:
    
    def test_extract_text_fields_complete_profile(self, sample_profile_data):
        """Test extracting text fields from complete profile"""
        result = extract_text_fields(sample_profile_data)
        source_types = [item[0] for item in result]
        assert 'experience' in source_types
        assert 'project' in source_types
        assert 'skills' in source_types
        assert 'summary' in source_types
        assert 'bio' in source_types
        experience_items = [item for item in result if item[0] == 'experience']
        assert len(experience_items) == 2
    
    def test_extract_text_fields_partial_profile(self):
        """Test extracting from profile with missing fields"""
        partial_profile = {
            "experience": [
                {"title": "Engineer", "description": "Did engineering work."}
            ]
        }
        result = extract_text_fields(partial_profile)
        assert len(result) == 1
        assert result[0][0] == 'experience'
        assert result[0][2] == "Did engineering work."
    
    def test_extract_text_fields_empty_profile(self):
        """Test extracting from empty profile"""
        result = extract_text_fields({})
        assert result == []
    
    def test_extract_text_fields_skills_list(self):
        """Test extracting skills as list"""
        profile = {"skills": ["Python", "JavaScript", "Docker"]}
        result = extract_text_fields(profile)
        assert len(result) == 1
        assert result[0][0] == 'skills'
        assert result[0][2] == "Python, JavaScript, Docker"
    
    def test_extract_text_fields_skills_string(self):
        """Test extracting skills as string"""
        profile = {"skills": "Python, JavaScript, Docker"}
        result = extract_text_fields(profile)
        assert len(result) == 1
        assert result[0][0] == 'skills'
        assert result[0][2] == "Python, JavaScript, Docker"

class TestEndpoints:
    USER_ID = "test_user_123"

    @pytest.fixture
    def client(self, temp_db): # Ensure temp_db runs before app initialization
        from app import app as fastapi_app # Local import to use patched DB_PATH
        return TestClient(fastapi_app)

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "embedding_service"

    @patch('app.mark_user_indexed')
    @patch('app.add_to_index')
    @patch('app.store_chunk')
    @patch('app.embed_text') 
    @patch('app.requests.get') 
    def test_index_user_success(self, mock_requests_get_api, mock_app_embed_text, 
                                mock_store_chunk, mock_add_to_index, mock_mark_user_indexed,
                                client, sample_profile_data, sample_embedding):
        """Test successful user indexing"""
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.json.return_value = sample_profile_data
        mock_requests_get_api.return_value = mock_api_response
        
        mock_app_embed_text.return_value = sample_embedding
        
        response = client.post(f"/index/{self.USER_ID}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "indexed"
        assert data["num_chunks"] > 0 
        
        mock_requests_get_api.assert_called_once_with(f"http://localhost:5000/profile/{self.USER_ID}")
        assert mock_app_embed_text.call_count >= 1 
        assert mock_store_chunk.call_count == mock_app_embed_text.call_count
        assert mock_add_to_index.call_count == mock_app_embed_text.call_count
        mock_mark_user_indexed.assert_called_once_with(self.USER_ID)

    @patch('app.requests.get')
    def test_index_user_profile_not_found(self, mock_requests_get_api, client):
        """Test indexing when user profile is not found (404)"""
        mock_api_response = Mock()
        mock_api_response.status_code = 404
        mock_requests_get_api.return_value = mock_api_response
        
        response = client.post(f"/index/{self.USER_ID}")
        
        assert response.status_code == 404
        assert response.json()["detail"] == f"User profile not found for user_id: {self.USER_ID}"

    @patch('app.requests.get')
    def test_index_user_profile_api_error(self, mock_requests_get_api, client):
        """Test indexing when profile API call fails"""
        mock_requests_get_api.side_effect = requests.exceptions.RequestException("API down")
        
        response = client.post(f"/index/{self.USER_ID}")
        
        assert response.status_code == 500
        assert "Failed to fetch profile from backend" in response.json()["detail"]

    @patch('app.requests.get')
    @patch('app.extract_text_fields') 
    def test_index_user_no_text_fields(self, mock_extract_text, mock_requests_get_api, client, sample_profile_data):
        """Test indexing when profile has no extractable text fields"""
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.json.return_value = sample_profile_data 
        mock_requests_get_api.return_value = mock_api_response
        
        mock_extract_text.return_value = [] 
        
        response = client.post(f"/index/{self.USER_ID}")
        
        assert response.status_code == 200 
        data = response.json()
        assert data["status"] == "indexed"
        assert data["num_chunks"] == 0

    @patch('app.requests.get')
    @patch('app.embed_text')
    def test_index_user_embedding_error(self, mock_app_embed_text, mock_requests_get_api, client, sample_profile_data):
        """Test indexing failure due to error in embed_text"""
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.json.return_value = sample_profile_data
        mock_requests_get_api.return_value = mock_api_response
        
        mock_app_embed_text.side_effect = Exception("Embedding failed")
        
        response = client.post(f"/index/{self.USER_ID}")
        
        assert response.status_code == 500
        assert "Error during indexing: Embedding failed" in response.json()["detail"]

    @patch('app.embed_text') 
    def test_embed_text_endpoint_success(self, mock_app_embed_text, client, sample_embedding):
        """Test successful text embedding via /embed endpoint"""
        mock_app_embed_text.return_value = sample_embedding
        text_to_embed = "This is a test sentence."
        
        response = client.post("/embed", json={"text": text_to_embed})
        
        assert response.status_code == 200
        data = response.json()
        assert data["embedding"] == sample_embedding.tolist()
        mock_app_embed_text.assert_called_once_with(text_to_embed)

    def test_embed_text_endpoint_empty_input(self, client):
        """Test /embed endpoint with empty text (Pydantic validation)"""
        response = client.post("/embed", json={"text": ""})
        assert response.status_code == 422 

    @patch('app.embed_text')
    def test_embed_text_endpoint_internal_error(self, mock_app_embed_text, client):
        """Test /embed endpoint failure due to internal embedding error"""
        mock_app_embed_text.side_effect = Exception("Model error")
        
        response = client.post("/embed", json={"text": "Some text"})
        
        assert response.status_code == 500
        assert "Error generating embedding: Model error" in response.json()["detail"]

    @patch('app.search') 
    @patch('app.get_chunk_by_id') 
    def test_retrieve_chunks_success(self, mock_db_get_chunk, mock_faiss_search, client, sample_embedding):
        """Test successful retrieval of similar chunks"""
        query_embedding = sample_embedding.tolist()
        top_k = 3
        mock_chunk_ids = ["chunk1", "chunk2"]
        mock_scores = [0.9, 0.8]
        mock_faiss_search.return_value = (mock_chunk_ids, mock_scores)
        
        def get_chunk_side_effect(chunk_id):
            if chunk_id == "chunk1":
                return ("chunk1", self.USER_ID, "experience", "0", "Text for chunk1", b'emb1')
            if chunk_id == "chunk2":
                return ("chunk2", self.USER_ID, "project", "1", "Text for chunk2", b'emb2')
            return None
        mock_db_get_chunk.side_effect = get_chunk_side_effect
        
        response = client.post(f"/retrieve/{self.USER_ID}", json={
            "query_embedding": query_embedding,
            "top_k": top_k
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2
        assert data["results"][0]["chunk_id"] == "chunk1"
        assert data["results"][0]["score"] == 0.9
        assert data["results"][1]["chunk_id"] == "chunk2"
        assert data["results"][1]["score"] == 0.8
        
        mock_faiss_search.assert_called_once()
        args, _ = mock_faiss_search.call_args
        assert args[0] == self.USER_ID
        assert np.array_equal(args[1], np.array(query_embedding, dtype=np.float32) / np.linalg.norm(np.array(query_embedding, dtype=np.float32)))
        assert args[2] == top_k
        
        expected_db_calls = [call("chunk1"), call("chunk2")]
        mock_db_get_chunk.assert_has_calls(expected_db_calls, any_order=True)

    @patch('app.search')
    def test_retrieve_user_not_in_faiss(self, mock_faiss_search, client, sample_embedding):
        """Test retrieval when user has no FAISS index (e.g., search returns empty)"""
        mock_faiss_search.return_value = ([], []) 
        
        response = client.post(f"/retrieve/{self.USER_ID}", json={
            "query_embedding": sample_embedding.tolist(),
            "top_k": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 0

    def test_retrieve_invalid_embedding_dimension(self, client):
        """Test retrieval with query embedding of invalid dimension (app check)"""
        invalid_embedding = [0.1] * 100 
        response = client.post(f"/retrieve/{self.USER_ID}", json={
            "query_embedding": invalid_embedding,
            "top_k": 5
        })
        assert response.status_code == 422 # Pydantic validation for min_length/max_length on list

    def test_retrieve_invalid_embedding_dimension_pydantic(self, client):
        """Test retrieval with query embedding of invalid dimension (Pydantic validation)"""
        # Test with too few items
        response_short = client.post(f"/retrieve/{self.USER_ID}", json={
            "query_embedding": [0.1] * 10, # Less than min_items=384
            "top_k": 5
        })
        assert response_short.status_code == 422

        # Test with too many items
        response_long = client.post(f"/retrieve/{self.USER_ID}", json={
            "query_embedding": [0.1] * 400, # More than max_items=384
            "top_k": 5
        })
        assert response_long.status_code == 422

    def test_retrieve_invalid_top_k(self, client, sample_embedding):
        """Test retrieval with invalid top_k values (Pydantic validation)"""
        # Test top_k too low
        response_low = client.post(f"/retrieve/{self.USER_ID}", json={
            "query_embedding": sample_embedding.tolist(),
            "top_k": 0 # Less than ge=1
        })
        assert response_low.status_code == 422

        # Test top_k too high
        response_high = client.post(f"/retrieve/{self.USER_ID}", json={
            "query_embedding": sample_embedding.tolist(),
            "top_k": 200 # More than le=100
        })
        assert response_high.status_code == 422

    @patch('app.search')
    @patch('app.get_chunk_by_id')
    def test_retrieve_faiss_id_not_in_db(self, mock_db_get_chunk, mock_faiss_search, client, sample_embedding):
        """Test retrieval when a chunk_id from FAISS is not found in DB"""
        mock_faiss_search.return_value = (["existing_chunk", "missing_chunk"], [0.9, 0.8])
        
        def get_chunk_side_effect(chunk_id):
            if chunk_id == "existing_chunk":
                return ("existing_chunk", self.USER_ID, "type", "id", "text", b'emb')
            return None 
        mock_db_get_chunk.side_effect = get_chunk_side_effect
        
        response = client.post(f"/retrieve/{self.USER_ID}", json={
            "query_embedding": sample_embedding.tolist(), "top_k": 2
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1 # Only the existing_chunk should be returned
        assert data["results"][0]["chunk_id"] == "existing_chunk"

    @patch('app.search')
    def test_retrieve_internal_error_faiss(self, mock_faiss_search, client, sample_embedding):
        """Test retrieval failure due to FAISS search error"""
        mock_faiss_search.side_effect = Exception("FAISS exploded")
        response = client.post(f"/retrieve/{self.USER_ID}", json={
            "query_embedding": sample_embedding.tolist(), "top_k": 5
        })
        assert response.status_code == 500
        assert "Error during retrieval: FAISS exploded" in response.json()["detail"]

    @patch('app.search')
    @patch('app.get_chunk_by_id')
    def test_retrieve_internal_error_db(self, mock_db_get_chunk, mock_faiss_search, client, sample_embedding):
        """Test retrieval failure due to DB get_chunk_by_id error"""
        mock_faiss_search.return_value = (["some_chunk"], [0.9])
        mock_db_get_chunk.side_effect = Exception("DB connection lost")
        
        response = client.post(f"/retrieve/{self.USER_ID}", json={
            "query_embedding": sample_embedding.tolist(), "top_k": 1
        })
        assert response.status_code == 500
        assert "Error during retrieval: DB connection lost" in response.json()["detail"]