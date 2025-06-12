# test_model.py

import numpy as np
from model import load_model, embed_text

def test_model_loading_and_embedding():
    """Test that the model loads and produces a valid, normalized embedding."""
    # Act
    model = load_model()
    embedding = embed_text("This is a test sentence.")

    # Assert
    assert model is not None
    assert isinstance(embedding, np.ndarray)
    assert embedding.dtype == np.float32
    assert embedding.shape == (384,)
    
    # Check for normalization
    norm = np.linalg.norm(embedding)
    assert np.isclose(norm, 1.0, atol=1e-6)

    # Test singleton behavior
    model2 = load_model()
    assert model is model2