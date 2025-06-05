import pytest
import numpy as np
from unittest.mock import Mock, patch

from model import load_model, embed_text, _model

class TestModel:
    
    def test_load_model_success(self):
        """Test successful model loading"""
        with patch('model.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model
            
            result = load_model()
            
            assert result == mock_model
            mock_st.assert_called_once_with("all-MiniLM-L6-v2")
            mock_model.get_sentence_embedding_dimension.assert_called_once()
    
    def test_load_model_custom_name(self):
        """Test loading model with custom name"""
        with patch('model.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model
            
            custom_model_name = "custom-model-name"
            result = load_model(custom_model_name)
            
            mock_st.assert_called_once_with(custom_model_name)
    
    def test_load_model_singleton(self):
        """Test that load_model returns the same instance on multiple calls"""
        with patch('model.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model
            
            result1 = load_model()
            result2 = load_model()
            
            assert result1 == result2
            # SentenceTransformer should only be called once due to singleton pattern
            mock_st.assert_called_once()
    
    def test_embed_text_success(self):
        """Test successful text embedding"""
        with patch('model.SentenceTransformer') as mock_st:
            # Create a mock embedding (not normalized)
            mock_embedding = np.array([3.0, 4.0, 0.0] + [0.0] * 381, dtype=np.float32)
            
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_model.encode.return_value = mock_embedding
            mock_st.return_value = mock_model
            
            # Load model first
            load_model()
            
            text = "This is a test sentence."
            result = embed_text(text)
            
            # Verify the embedding is normalized
            assert isinstance(result, np.ndarray)
            assert result.dtype == np.float32
            assert len(result) == 384
            
            # Check normalization (should be unit vector)
            norm = np.linalg.norm(result)
            assert abs(norm - 1.0) < 1e-6
            
            # Verify model.encode was called correctly
            mock_model.encode.assert_called_once_with(text, convert_to_numpy=True)
    
    def test_embed_text_zero_vector(self):
        """Test embedding with zero vector (edge case)"""
        with patch('model.SentenceTransformer') as mock_st:
            # Create a zero vector
            mock_embedding = np.zeros(384, dtype=np.float32)
            
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_model.encode.return_value = mock_embedding
            mock_st.return_value = mock_model
            
            # Load model first
            load_model()
            
            result = embed_text("test")
            
            # Zero vector should remain zero after normalization attempt
            assert np.allclose(result, np.zeros(384))
    
    def test_embed_text_model_not_loaded(self):
        """Test embedding when model is not loaded"""
        # Ensure model is not loaded
        import model
        model._model = None
        
        with pytest.raises(RuntimeError, match="Model not loaded"):
            embed_text("test text")
    
    def test_embed_text_normalization(self):
        """Test that embeddings are properly normalized"""
        with patch('model.SentenceTransformer') as mock_st:
            # Create a non-unit vector
            mock_embedding = np.array([1.0, 2.0, 3.0] + [0.0] * 381, dtype=np.float32)
            expected_norm = np.linalg.norm(mock_embedding)
            
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_model.encode.return_value = mock_embedding
            mock_st.return_value = mock_model
            
            load_model()
            result = embed_text("test")
            
            # Check that result is normalized
            assert abs(np.linalg.norm(result) - 1.0) < 1e-6
            
            # Check that the direction is preserved
            expected_normalized = mock_embedding / expected_norm
            assert np.allclose(result, expected_normalized)