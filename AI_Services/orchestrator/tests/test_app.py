import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# FIX: Use consistent and correct patch paths
@patch('app.create_agent_executor')
@patch('app.get_session_context')
@patch('app.initialize_session_context')
def test_chat_endpoint_new_session(mock_init_context, mock_get_context, mock_create_agent, test_client):
    """
    Tests the chat endpoint for a new session, ensuring context is initialized
    and the agent is called correctly.
    """
    # Arrange
    client, mock_toolbox = test_client
    
    # Mock the agent executor's behavior
    mock_executor = MagicMock()
    mock_executor.ainvoke = AsyncMock(return_value={"output": "Hello from the agent!"})
    mock_create_agent.return_value = mock_executor
    
    # Simulate first call returning no context, second call (after init) returning context
    mock_get_context.side_effect = [None, {"resume_state": {"summary": "new"}}]

    # Act
    response = client.post(
        "/v1/chat",
        json={
            "session_id": "new-session",
            "user_message": "Let's start.",
            "user_id": "u1",
            "job_description": "A great job."
        }
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["agent_response"] == "Hello from the agent!"
    assert data["resume_state"] == {"summary": "new"}
    
    # Verify mocks were called correctly
    mock_init_context.assert_called_once_with("new-session", "u1", "A great job.")
    mock_create_agent.assert_called_once_with(mock_toolbox, "new-session")
    mock_executor.ainvoke.assert_called_once_with({"input": "Let's start."})

# FIX: Use correct patch path
@patch('app.get_session_context')
def test_chat_endpoint_new_session_missing_data(mock_get_context, test_client):
    """
    Tests that a 400 Bad Request is returned for a new session if user_id
    or job_description is missing.
    """
    # Arrange
    client, _ = test_client
    mock_get_context.return_value = None  # Simulate a new session

    # Test with missing user_id
    response1 = client.post(
        "/v1/chat",
        json={
            "session_id": "new-session-1",
            "user_message": "Let's start.",
            "job_description": "A job"
        }
    )
    
    # Test with missing job_description
    response2 = client.post(
        "/v1/chat",
        json={
            "session_id": "new-session-2",
            "user_message": "Let's start.",
            "user_id": "user-123"
        }
    )
    
    # Test with both missing
    response3 = client.post(
        "/v1/chat",
        json={
            "session_id": "new-session-3",
            "user_message": "Let's start."
        }
    )
    
    # Assert all cases return 400
    for response in [response1, response2, response3]:
        assert response.status_code == 400
        assert "user_id` and `job_description` are required" in response.json()["detail"]