import pytest
import tempfile
import os
import sqlite3
import numpy as np
from typing import Generator, Dict, Any
from unittest.mock import Mock, patch
import sys
import shutil

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import init_db, get_connection, DB_PATH
from model import load_model
from faiss_index import user_indices

@pytest.fixture
def temp_db() -> Generator[str, None, None]:
    """Create a temporary database for testing"""
    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.db')
    os.close(temp_fd)
    
    # Patch the DB_PATH
    original_db_path = DB_PATH
    import db
    db.DB_PATH = temp_path
    
    # Initialize the test database
    init_db()
    
    yield temp_path
    
    # Cleanup
    db.DB_PATH = original_db_path
    if os.path.exists(temp_path):
        os.unlink(temp_path)

@pytest.fixture
def sample_profile_data() -> Dict[str, Any]:
    """Sample profile data for testing"""
    return {
        "user_id": "test_user_123",
        "name": "John Doe",
        "email": "john@example.com",
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "description": "Led development of microservices architecture. Implemented CI/CD pipelines and mentored junior developers. Worked extensively with Python, Docker, and Kubernetes to build scalable applications."
            },
            {
                "title": "Software Developer",
                "company": "StartupXYZ",
                "description": "Built web applications using React and Node.js. Developed RESTful APIs and integrated third-party services. Participated in agile development process."
            }
        ],
        "projects": [
            {
                "name": "E-commerce Platform",
                "description": "Developed a full-stack e-commerce platform with payment integration, inventory management, and user authentication. Used React for frontend and Python Django for backend."
            }
        ],
        "skills": ["Python", "JavaScript", "Docker", "Kubernetes", "React", "Django", "PostgreSQL"],
        "summary": "Experienced software engineer with 5+ years in full-stack development. Passionate about building scalable applications and mentoring team members.",
        "bio": "John is a dedicated software engineer who loves solving complex problems and learning new technologies."
    }

@pytest.fixture
def sample_embedding() -> np.ndarray:
    """Generate a sample normalized embedding vector"""
    # Create random 384-dimensional vector
    vector = np.random.randn(384).astype(np.float32)
    # Normalize to unit length
    vector = vector / np.linalg.norm(vector)
    return vector

@pytest.fixture(autouse=True)
def clear_global_state():
    """Clear global state before each test"""
    # Clear FAISS indices
    user_indices.clear()
    
    # Clear model cache
    import model
    model._model = None
    
    yield
    
    # Cleanup after test
    user_indices.clear()
    model._model = None

@pytest.fixture
def mock_requests_get():
    """Mock requests.get for API calls"""
    with patch('requests.get') as mock_get:
        yield mock_get