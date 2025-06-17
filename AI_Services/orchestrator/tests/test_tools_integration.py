import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import Response, Request
from datetime import datetime

from tools import ToolBox

# Mock responses from downstream services
MOCK_RETRIEVAL_RESPONSE = {
    "results": [{
        "chunk_id": "c1", "user_id": "u1", "index_namespace": "profile",
        "section_id": None, "source_type": "experience", "source_id": "0",
        "text": "Context text.", "score": 0.9, "created_at": datetime.utcnow().isoformat()
    }]
}
MOCK_GENERATION_RESPONSE = {
    "generated_text": '{"summary": "Generated summary."}',
    "raw_prompt": "prompt", "retrieval_mode": "section", "section_id": "summary"
}
MOCK_SCORE_RESPONSE = {"match_score": 0.85, "missing_keywords": ["Python", "FastAPI"]}
MOCK_SUGGESTION_RESPONSE = {"suggestions": ["Add Python to your skills."]}

@pytest.fixture
def mock_http_client():
    """Fixture for a mock HTTP client with async post method."""
    client = MagicMock()
    client.post = AsyncMock()
    return client

@pytest.fixture
def toolbox(mock_http_client):
    """Fixture for the ToolBox instance."""
    return ToolBox(client=mock_http_client)

@pytest.mark.asyncio
async def test_retrieve_context_tool(toolbox, mock_http_client):
    """Tests the retrieve tool calls the correct endpoint."""
    mock_http_client.post.return_value = Response(200, json=MOCK_RETRIEVAL_RESPONSE, request=Request("POST", ""))
    
    # FIX: Use correct patch path
    with patch("tools.get_session_context", return_value={"user_id": "u1", "job_description": "jd1"}):
        result = await toolbox.retrieve_context_tool.ainvoke({"session_id": "s1", "section_id": "experience"})
    
    mock_http_client.post.assert_called_once()
    assert "/retrieve/section" in mock_http_client.post.call_args[0][0]
    assert "Context text." in result

@pytest.mark.asyncio
async def test_score_resume_text_tool(toolbox, mock_http_client):
    """Tests the scoring tool returns a formatted string."""
    mock_http_client.post.return_value = Response(200, json=MOCK_SCORE_RESPONSE, request=Request("POST", ""))

    with patch("tools.get_session_context", return_value={"job_description": "jd1"}):
        result = await toolbox.score_resume_text_tool.ainvoke({"session_id": "s1", "resume_text": "text"})
        
    assert "Match Score = 0.85" in result
    assert "['Python', 'FastAPI']" in result

@pytest.mark.asyncio
async def test_get_full_resume_text_tool():
    """Tests that the full resume text is formatted correctly."""
    toolbox = ToolBox(client=MagicMock())
    mock_context = {
        "resume_state": {
            "summary": "A great summary.",
            "skills": ["Python", "SQL"],
            "experience": ["Worked at a place."]
        }
    }
    with patch("tools.get_session_context", return_value=mock_context):
        result = toolbox.get_full_resume_text_tool.invoke({"session_id": "s1"})

    assert "--- SUMMARY ---" in result
    assert "A great summary." in result
    assert "--- SKILLS ---" in result
    assert "Python" in result
    assert "SQL" in result
    assert "--- EXPERIENCE ---" in result
    assert "Worked at a place." in result

def test_update_resume_in_memory_tool_single_section():
    """Tests updating a single section in the resume state."""
    toolbox = ToolBox(client=MagicMock())
    mock_context = {"resume_state": {"summary": "old summary"}}
    
    with patch("tools.get_session_context", return_value=mock_context):
        with patch("tools.update_session_context") as mock_update:
            result = toolbox.update_resume_in_memory_tool.invoke({
                "session_id": "s1",
                "section_id": "summary",
                "new_content_json": '{"summary": "new summary"}'
            })

    assert result == "Successfully updated section 'summary'."
    mock_update.assert_called_once()
    updated_context = mock_update.call_args[0][1]
    assert updated_context["resume_state"]["summary"] == "new summary"

def test_update_resume_in_memory_tool_full_resume():
    """Tests updating the full resume state from a multi-key JSON."""
    toolbox = ToolBox(client=MagicMock())
    mock_context = {"resume_state": {}}
    full_resume_json = '{"summary": "A new summary.", "skills": ["new skill"]}'

    with patch("tools.get_session_context", return_value=mock_context):
        with patch("tools.update_session_context") as mock_update:
            result = toolbox.update_resume_in_memory_tool.invoke({
                "session_id": "s1",
                "new_content_json": full_resume_json
            })
    
    assert "Successfully updated the full resume" in result
    mock_update.assert_called_once()
    updated_context = mock_update.call_args[0][1]
    assert updated_context["resume_state"]["summary"] == "A new summary."
    assert updated_context["resume_state"]["skills"] == ["new skill"]