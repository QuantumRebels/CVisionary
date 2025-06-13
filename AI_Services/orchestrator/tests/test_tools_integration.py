# tests/test_tools_integration.py

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from httpx import Response, Request
from datetime import datetime

# Import from the correct local path
from tools import ToolBox

MOCK_RETRIEVAL_RESPONSE = {
    "results": [{
        "chunk_id": "c1", "user_id": "u1", "index_namespace": "profile",
        "section_id": None, "source_type": "experience", "source_id": "0",
        "text": "Context text.", "score": 0.9, "created_at": datetime.utcnow().isoformat()
    }]
}
MOCK_GENERATION_RESPONSE = {
    "generated_text": '{"summary": "Generated summary."}',
    "raw_prompt": "prompt",
    "retrieval_mode": "section",
    "section_id": "summary"
}

@pytest.mark.asyncio
async def test_retrieve_context_tool_full_mode(monkeypatch):
    """Tests the retrieve tool in full mode."""
    mock_http_client = MagicMock()
    mock_http_client.post = AsyncMock(return_value=Response(200, json=MOCK_RETRIEVAL_RESPONSE, request=Request("POST", "")))
    toolbox = ToolBox(client=mock_http_client)

    # Mock the dependency using monkeypatch
    mock_get_context = MagicMock(return_value={"user_id": "u1", "job_description": "jd1"})
    monkeypatch.setattr("tools.get_session_context", mock_get_context)

    # FIX: Use .ainvoke with a dict for LangChain tool calls
    result = await toolbox.retrieve_context_tool.ainvoke({"session_id": "s1"})

    mock_http_client.post.assert_called_once()
    assert "Context text." in result

@pytest.mark.asyncio
async def test_generate_text_tool_section_mode(monkeypatch):
    """Tests the generate tool in section mode."""
    mock_http_client = MagicMock()
    mock_http_client.post = AsyncMock(return_value=Response(200, json=MOCK_GENERATION_RESPONSE, request=Request("POST", "")))
    toolbox = ToolBox(client=mock_http_client)

    mock_get_context = MagicMock(return_value={"user_id": "u1", "job_description": "jd1"})
    monkeypatch.setattr("tools.get_session_context", mock_get_context)

    # FIX: Use .ainvoke with a dict for LangChain tool calls
    result = await toolbox.generate_text_tool.ainvoke({
        "session_id": "s1",
        "section_id": "summary",
        "existing_text": "old"
    })

    mock_http_client.post.assert_called_once()
    assert result == '{"summary": "Generated summary."}'