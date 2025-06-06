import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import torch

from model_inference import ModelInference

class TestModelInference:
    """Test the ModelInference class"""
    
    def test_init(self):
        """Test ModelInference initialization"""
        # Test with default model
        model_inference = ModelInference()
        assert model_inference.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert model_inference.model is None
        
        # Test with custom model
        custom_model = "custom-model-name"
        model_inference = ModelInference(custom_model)
        assert model_inference.model_name == custom_model
    
    @patch('model_inference.SentenceTransformer')
    def test_load_model_success(self, mock_sentence_transformer):
        """Test successful model loading"""
        mock_model = Mock()
        mock_sentence_transformer.return_value = mock_model
        
        model_inference = ModelInference()
        model_inference.load_model()
        
        # Verify model was loaded
        mock_sentence_transformer.assert_called_once_with("sentence-transformers/all-MiniLM-L6-v2")
        assert model_inference.model == mock_model
    
    @patch('model_inference.SentenceTransformer')
    def test_load_model_failure(self, mock_sentence_transformer):
        """Test model loading failure"""
        mock_sentence_transformer.side_effect = Exception("Model loading failed")
        
        model_inference = ModelInference()
        
        with pytest.raises(Exception, match="Model loading failed"):
            model_inference.load_model()
    
    def test_embed_text_model_not_loaded(self):
        """Test embedding text when model is not loaded"""
        model_inference = ModelInference()
        
        with pytest.raises(RuntimeError, match="Model not loaded"):
            model_inference.embed_text("test text")
    
    @patch('model_inference.normalize')
    def test_embed_text_success(self, mock_normalize):
        """Test successful text embedding"""
        # Setup mocks
        mock_model = Mock()
        mock_embedding = np.random.rand(384).astype(np.float32)
        mock_model.encode.return_value = mock_embedding
        
        normalized_embedding = mock_embedding / np.linalg.norm(mock_embedding)
        mock_normalize.return_value = normalized_embedding.reshape(1, -1)
        
        model_inference = ModelInference()
        model_inference.model = mock_model
        
        # Test embedding
        result = model_inference.embed_text("test text")
        
        # Verify calls
        mock_model.encode.assert_called_once_with("test text", convert_to_numpy=True)
        mock_normalize.assert_called_once()
        
        # Verify result
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float32
        assert result.shape == (384,)
    
    def test_embed_text_empty_string(self):
        """Test embedding empty string"""
        mock_model = Mock()
        mock_model.encode.return_value = np.zeros(384).astype(np.float32)
        
        model_inference = ModelInference()
        model_inference.model = mock_model
        
        result = model_inference.embed_text("")
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (384,)
    
    def test_embed_text_long_string(self):
        """Test embedding very long string"""
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(384).astype(np.float32)
        
        model_inference = ModelInference()
        model_inference.model = mock_model
        
        long_text = "word " * 1000  # Very long text
        result = model_inference.embed_text(long_text)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (384,)
    
    def test_embed_text_unicode(self):
        """Test embedding text with unicode characters"""
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(384).astype(np.float32)
        
        model_inference = ModelInference()
        model_inference.model = mock_model
        
        unicode_text = "Python développeur 🐍 with émojis"
        result = model_inference.embed_text(unicode_text)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (384,)
    
    def test_embed_text_encoding_error(self):
        """Test handling of encoding errors"""
        mock_model = Mock()
        mock_model.encode.side_effect = Exception("Encoding failed")
        
        model_inference = ModelInference()
        model_inference.model = mock_model
        
        with pytest.raises(Exception, match="Encoding failed"):
            model_inference.embed_text("test text")
    
    def test_compute_match_score_success(self, sample_embeddings):
        """Test successful match score computation"""
        model_inference = ModelInference()
        embedding1, embedding2 = sample_embeddings
        
        score = model_inference.compute_match_score(embedding1, embedding2)
        
        # Verify result
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    def test_compute_match_score_identical_embeddings(self):
        """Test match score with identical embeddings"""
        model_inference = ModelInference()
        
        # Create identical normalized embeddings
        embedding = np.random.rand(384).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)
        
        score = model_inference.compute_match_score(embedding, embedding)
        
        # Should be close to 1.0 (perfect match after sigmoid)
        assert score > 0.9
    
    def test_compute_match_score_orthogonal_embeddings(self):
        """Test match score with orthogonal embeddings"""
        model_inference = ModelInference()
        
        # Create orthogonal normalized embeddings
        embedding1 = np.zeros(384, dtype=np.float32)
        embedding1[0] = 1.0
        
        embedding2 = np.zeros(384, dtype=np.float32)
        embedding2[1] = 1.0
        
        score = model_inference.compute_match_score(embedding1, embedding2)
        
        # Should be around 0.5 (cosine similarity = 0, sigmoid(0) = 0.5)
        assert 0.4 <= score <= 0.6
    
    def test_compute_match_score_invalid_dimensions(self):
        """Test match score with invalid embedding dimensions"""
        model_inference = ModelInference()
        
        embedding1 = np.random.rand(384).astype(np.float32)
        embedding2 = np.random.rand(256).astype(np.float32)  # Wrong dimension
        
        with pytest.raises(Exception):
            model_inference.compute_match_score(embedding1, embedding2)
    
    def test_compute_match_score_nan_values(self):
        """Test match score with NaN values"""
        model_inference = ModelInference()
        
        embedding1_nan = np.full(384, np.nan, dtype=np.float32)
        embedding2_finite = np.random.rand(384).astype(np.float32)
        
        with pytest.raises(ValueError, match="Input embeddings must be finite numbers."):
            model_inference.compute_match_score(embedding1_nan, embedding2_finite)

        embedding1_finite = np.random.rand(384).astype(np.float32)
        embedding2_nan = np.full(384, np.nan, dtype=np.float32)
        with pytest.raises(ValueError, match="Input embeddings must be finite numbers."):
            model_inference.compute_match_score(embedding1_finite, embedding2_nan)
    
    def test_sigmoid_function(self):
        """Test the sigmoid function"""
        # Test normal values
        assert ModelInference._sigmoid(0) == 0.5
        assert ModelInference._sigmoid(1000) > 0.99  # Should be close to 1
        assert ModelInference._sigmoid(-1000) < 0.01  # Should be close to 0
        
        # Test edge cases
        assert 0 < ModelInference._sigmoid(float('inf')) <= 1
        assert 0 <= ModelInference._sigmoid(float('-inf')) < 1
    
    def test_sigmoid_overflow_protection(self):
        """Test that sigmoid handles overflow properly"""
        # Test very large values
        result = ModelInference._sigmoid(1000)
        assert np.isfinite(result)
        assert 0 <= result <= 1
        
        # Test very small values
        result = ModelInference._sigmoid(-1000)
        assert np.isfinite(result)
        assert 0 <= result <= 1
    
    @patch('model_inference.SentenceTransformer')
    def test_integration_workflow(self, mock_sentence_transformer):
        """Test the complete workflow integration"""
        # Setup mock model
        mock_model = Mock()
        mock_embedding = np.random.rand(384).astype(np.float32)
        mock_model.encode.return_value = mock_embedding
        mock_sentence_transformer.return_value = mock_model
        
        # Initialize and load model
        model_inference = ModelInference()
        model_inference.load_model()
        
        # Test complete workflow
        text1 = "Python developer with Django experience"
        text2 = "Software engineer skilled in Python and web frameworks"
        
        # Generate embeddings
        emb1 = model_inference.embed_text(text1)
        emb2 = model_inference.embed_text(text2)
        
        # Compute match score
        score = model_inference.compute_match_score(emb1, emb2)
        
        # Verify results
        assert isinstance(emb1, np.ndarray)
        assert isinstance(emb2, np.ndarray)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        
        # Verify model was called
        assert mock_model.encode.call_count == 2