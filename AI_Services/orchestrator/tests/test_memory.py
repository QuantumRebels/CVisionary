import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_redis_client(monkeypatch):
    """Mocks the redis_client in the memory module."""
    mock_client = MagicMock()
    # FIX: Use correct patch path
    monkeypatch.setattr("memory.redis_client", mock_client)
    return mock_client

def test_initialize_session_context(mock_redis_client):
    """Tests creating a new session context."""
    from memory import initialize_session_context
    session_id = "s1"
    user_id = "u1"
    job_description = "jd1"

    initialize_session_context(session_id, user_id, job_description)

    mock_redis_client.set.assert_called_once()
    call_args = mock_redis_client.set.call_args
    assert call_args[0][0] == f"session_context:{session_id}"
    assert '"user_id": "u1"' in call_args[0][1]
    assert '"resume_state": {}' in call_args[0][1]

def test_get_session_context(mock_redis_client):
    """Tests retrieving an existing session context."""
    from memory import get_session_context
    session_id = "s2"
    mock_data = '{"user_id": "u2", "job_description": "jd2", "resume_state": {}}'
    mock_redis_client.get.return_value = mock_data

    context = get_session_context(session_id)

    mock_redis_client.get.assert_called_once_with(f"session_context:{session_id}")
    assert context["user_id"] == "u2"

def test_get_session_context_not_found(mock_redis_client):
    """Tests retrieving a non-existent session context."""
    from memory import get_session_context
    mock_redis_client.get.return_value = None
    context = get_session_context("s3")
    assert context is None