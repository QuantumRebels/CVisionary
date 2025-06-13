# tests/test_app.py

import pytest
from unittest.mock import patch, MagicMock, AsyncMock, ANY

AGENT_EXECUTOR_PATH = "app.create_agent_executor"

def test_chat_endpoint_new_session(test_client):
    """Tests the chat endpoint for a new session, requiring user_id and jd."""
    client, mock_toolbox = test_client

    mock_executor = MagicMock()
    mock_executor.ainvoke = AsyncMock(return_value={"output": "Hello! I'm ready to build your resume."})
    
    with patch(AGENT_EXECUTOR_PATH, return_value=mock_executor) as mock_create_agent:
        # Mock the memory functions to simulate a new session
        with patch("memory.get_session_context", side_effect=[None, {"resume_state": {}}]) as mock_get_context:
            with patch("app.initialize_session_context") as mock_init_context:
                
                response = client.post(
                    "/v1/chat",
                    json={
                        "session_id": "new-session",
                        "user_message": "Let's start.",
                        "user_id": "u1",
                        "job_description": "A great job."
                    }
                )

    assert response.status_code == 200
    data = response.json()
    assert data["agent_response"] == "Hello! I'm ready to build your resume."
    assert data["resume_state"] == {} # Check for the new field
    # Assert that the function was called with the correct keyword arguments.
    # Use ANY to avoid matching the specific mock_toolbox instance.
    mock_create_agent.assert_called_with(toolbox=ANY, session_id="new-session")
    mock_init_context.assert_called_once()

def test_chat_endpoint_new_session_missing_data(test_client):
    """Tests that a new session fails without user_id and jd."""
    client, _ = test_client
    
    # Mock get_session_context to return None to simulate a new session
    with patch("memory.get_session_context", return_value=None):
        # Test missing user_id and job_description
        response = client.post(
            "/v1/chat",
            json={
                "session_id": "new-session", 
                "user_message": "Let's start."
                # Missing user_id and job_description
            }
        )
        
        # The endpoint should return 400 with a specific error message
        assert response.status_code == 400
        assert "user_id` and `job_description` are required" in response.json()["detail"]
        
        # Test with empty user_id and job_description
        response = client.post(
            "/v1/chat",
            json={
                "session_id": "new-session-2", 
                "user_message": "Let's start.",
                "user_id": "",
                "job_description": ""
            }
        )
        
        # The endpoint should return 400 with a specific error message
        assert response.status_code == 400
        assert "user_id` and `job_description` are required" in response.json()["detail"]