import pytest
from unittest.mock import patch, MagicMock
import torch

from scoring_service.model_inference import ModelInference

@patch('scoring_service.model_inference.SentenceTransformer')
def test_model_loading(mock_sentence_transformer):
    model_inference = ModelInference()
    model_inference.load_model()
    mock_sentence_transformer.assert_called_with(
        "anass1209/resume-job-matcher-all-MiniLM-L6-v2",
        device=model_inference.device
    )

@patch('scoring_service.model_inference.util.cos_sim')
def test_compute_match_score_logic(mock_cos_sim):
    model_inference = ModelInference()
    mock_model = MagicMock()
    mock_model.encode.return_value = [torch.tensor([1.0]), torch.tensor([2.0])]
    model_inference.model = mock_model
    
    mock_cos_sim.return_value = torch.tensor([[0.5]])

    score = model_inference.compute_match_score("jd", "resume")

    assert score == 0.75