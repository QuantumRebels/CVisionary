import logging
from sentence_transformers import SentenceTransformer, util
import torch

logger = logging.getLogger(__name__)

class ModelInference:
    def __init__(self, model_name: str = "anass1209/resume-job-matcher-all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

    def load_model(self):
        try:
            logger.info(f"Loading specialized scoring model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info("Scoring model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load scoring model: {str(e)}")
            raise

    def compute_match_score(self, job_description: str, resume_text: str) -> float:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            embeddings = self.model.encode(
                [job_description, resume_text],
                convert_to_tensor=True,
                device=self.device
            )
            cosine_score = util.cos_sim(embeddings[0], embeddings[1])
            score = cosine_score.item()
            scaled_score = (score + 1) / 2
            return scaled_score
        except Exception as e:
            logger.error(f"Failed to compute match score with the model: {e}")
            raise