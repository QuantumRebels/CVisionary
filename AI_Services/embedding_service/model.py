from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Optional

# Global model instance
_model: Optional[SentenceTransformer] = None

def load_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """
    Load the sentence transformer model. Called once during startup.
    """
    global _model
    if _model is None:
        print(f"Loading sentence transformer model: {model_name}")
        _model = SentenceTransformer(model_name)
        print(f"Model loaded successfully. Embedding dimension: {_model.get_sentence_embedding_dimension()}")
    return _model

def embed_text(text: str) -> np.ndarray:
    """
    Generate normalized embedding vector for input text.
    
    Args:
        text: Input text to embed
        
    Returns:
        Normalized 384-dimensional float32 numpy array
    """
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    
    # Generate embedding
    embedding = _model.encode(text, convert_to_numpy=True)
    
    # Ensure float32 type
    embedding = embedding.astype(np.float32)
    
    # Normalize embedding vector to unit length
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    
    return embedding