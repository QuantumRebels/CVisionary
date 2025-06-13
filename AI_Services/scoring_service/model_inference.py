# model_inference.py

import logging
from sentence_transformers import SentenceTransformer, util
import torch

logger = logging.getLogger(__name__)

class ModelInference:
    """
    Handles the resume-job-matcher model loading and scoring.
    """
    def __init__(self, model_name: str = "anass1209/resume-job-matcher-all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

    def load_model(self):
        """Loads the specialized scoring model from Hugging Face."""
        try:
            logger.info(f"Loading specialized scoring model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info("Scoring model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load scoring model: {str(e)}")
            raise

    def compute_match_score(self, job_description: str, resume_text: str) -> float:
        """
        Computes a match score using the fine-tuned bi-encoder model.
        This model is trained to produce embeddings where the cosine similarity
        is a meaningful indicator of resume-job fit.
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # The model creates embeddings for both texts simultaneously
            embeddings = self.model.encode(
                [job_description, resume_text],
                convert_to_tensor=True,
                device=self.device
            )
            
            # Compute cosine similarity between the two embeddings
            cosine_score = util.cos_sim(embeddings[0], embeddings[1])
            
            # The score is a tensor, get the float value
            score = cosine_score.item()
            
            # Scale the score from [-1, 1] to [0, 1] for a more intuitive result
            # A score of 0.5 means no correlation, > 0.5 is a good match.
            scaled_score = (score + 1) / 2
            
            return scaled_score

        except Exception as e:
            logger.error(f"Failed to compute match score with the model: {e}")
            raise