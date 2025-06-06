import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize
import logging

logger = logging.getLogger(__name__)

class ModelInference:
    """
    Handles MiniLM model loading and inference for text embeddings
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        
    def load_model(self):
        """Load the MiniLM model"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise e
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate L2-normalized embedding for input text
        
        Args:
            text: Input text to embed
            
        Returns:
            L2-normalized 384-dimensional numpy array
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # L2 normalize the embedding
            embedding_normalized = normalize(embedding.reshape(1, -1), norm='l2')[0]
            
            return embedding_normalized.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise e
    
    def compute_match_score(self, jd_embedding: np.ndarray, resume_embedding: np.ndarray) -> float:
        """
        Compute match score between job description and resume embeddings
        
        Args:
            jd_embedding: Job description embedding (L2-normalized)
            resume_embedding: Resume embedding (L2-normalized)
            
        Returns:
            Match score between 0 and 1 (sigmoid of cosine similarity)
        """
        try:
            if not np.all(np.isfinite(jd_embedding)) or \
               not np.all(np.isfinite(resume_embedding)):
                logger.error("Input embeddings contain NaN or Inf values.")
                raise ValueError("Input embeddings must be finite numbers.")

            # Compute cosine similarity (dot product since vectors are normalized)
            cosine_similarity = np.dot(jd_embedding, resume_embedding)

            if not np.isfinite(cosine_similarity):
                logger.error(f"Cosine similarity is NaN or Inf: {cosine_similarity}")
                raise ValueError("Cosine similarity calculation resulted in NaN or Inf.")
            
            # Apply sigmoid function to get score in [0, 1]
            # Using a steeper sigmoid with scaling factor
            match_score = self._sigmoid(cosine_similarity * 5.0)
            
            return float(match_score)

        except ValueError as ve: # Re-raise ValueError explicitly
            logger.error(f"ValueError in compute_match_score: {str(ve)}")
            raise ve
        except Exception as e:
            logger.error(f"Failed to compute match score: {str(e)}")
            raise RuntimeError(f"An unexpected error occurred during match score computation: {str(e)}") from e
    
    @staticmethod
    def _sigmoid(x: float) -> float:
        """
        Sigmoid activation function
        
        Args:
            x: Input value
            
        Returns:
            Sigmoid output between 0 and 1
        """
        # Clamp input to prevent overflow
        x = np.clip(x, -500, 500)
        return 1 / (1 + np.exp(-x))