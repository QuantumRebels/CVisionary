import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_inference import ModelInference
from suggestion_client import SuggestionClient

@pytest.fixture
def mock_model_inference():
    """Mock ModelInference for testing"""
    mock = Mock(spec=ModelInference)
    mock.embed_text.return_value = np.random.rand(384).astype(np.float32)
    mock.compute_match_score.return_value = 0.75
    return mock

@pytest.fixture
def mock_suggestion_client():
    """Mock SuggestionClient for testing"""
    mock = Mock(spec=SuggestionClient)
    mock.generate_suggestions = AsyncMock(return_value=[
        "Add AWS certification to demonstrate cloud skills",
        "Include Docker projects in your portfolio",
        "Complete Kubernetes online course and mention it"
    ])
    return mock

@pytest.fixture
def sample_job_description():
    """Sample job description for testing"""
    return """
    We are looking for a Senior Python Developer with experience in:
    - Python programming and Django framework
    - REST API development and integration
    - AWS cloud services (EC2, S3, Lambda)
    - Docker containerization and Kubernetes orchestration
    - MySQL and PostgreSQL databases
    - Git version control and CI/CD pipelines
    - React.js for frontend development
    
    The ideal candidate should have 3+ years of experience and be familiar with Agile methodologies.
    """

@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing"""
    return """
    John Doe - Software Engineer
    
    Experience:
    - 4 years of Python development experience
    - Built REST APIs using Django and Flask frameworks
    - Worked with MySQL databases and wrote complex SQL queries
    - Used Git for version control in team environments
    - Participated in Agile/Scrum development processes
    
    Skills:
    - Programming: Python, JavaScript, HTML, CSS
    - Databases: MySQL, SQLite
    - Tools: Git, Jira, Postman
    - Frameworks: Django, Flask
    """

@pytest.fixture
def sample_embeddings():
    """Sample normalized embeddings for testing"""
    np.random.seed(42)  # For reproducible tests
    embedding1 = np.random.rand(384).astype(np.float32)
    embedding2 = np.random.rand(384).astype(np.float32)
    
    # Normalize embeddings
    embedding1 = embedding1 / np.linalg.norm(embedding1)
    embedding2 = embedding2 / np.linalg.norm(embedding2)
    
    return embedding1, embedding2

@pytest.fixture
def gemini_api_response():
    """Sample Gemini API response for testing"""
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": """• Add AWS certification or cloud project experience to demonstrate skills
• Include Docker containerization examples from personal projects  
• Mention Kubernetes orchestration experience or online course completion"""
                        }
                    ]
                }
            }
        ]
    }