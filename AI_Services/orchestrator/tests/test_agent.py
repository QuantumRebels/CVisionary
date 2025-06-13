# tests/test_agent.py

import json
import pytest
from unittest import mock
from unittest.mock import MagicMock, AsyncMock, patch

from agent import create_agent_executor
from tools import ToolBox
from langchain_core.tools import StructuredTool
from langchain_community.chat_message_histories import RedisChatMessageHistory

@pytest.fixture
def mock_toolbox():
    """Fixture to create a toolbox with mocked tools that pass LangChain's type checks."""
    # This toolbox instance is just a container for the mocks.
    toolbox = MagicMock(spec=ToolBox)

    # Create mocks for each tool that are spec'd as StructuredTool to pass isinstance checks.
    # The agent also requires the 'name' and 'return_direct' attributes to be present.
    # The mock itself is made callable by the agent, so we set a return_value on the mock object.
    
    def create_mock_tool(name, return_value):
        mock_tool = MagicMock(spec=StructuredTool, return_value=return_value)
        mock_tool.name = name
        mock_tool.return_direct = False  # Add the required return_direct attribute
        return mock_tool
    
    # Create mock tools with proper attributes and arun method
    def create_mock_tool_with_arun(name, return_value):
        mock_tool = MagicMock(spec=StructuredTool, return_value=return_value)
        mock_tool.name = name
        mock_tool.return_direct = False
        mock_tool.arun = AsyncMock(return_value=return_value)
        return mock_tool
    
    # Create mock tools
    mock_retrieve = create_mock_tool_with_arun(
        'retrieve_context_tool', 
        "Retrieved context about Python experience."
    )
    
    mock_generate = create_mock_tool_with_arun(
        'generate_text_tool', 
        '{"experience": ["New bullet point."]}'
    )
    
    mock_get_section = create_mock_tool_with_arun(
        'get_current_resume_section_tool', 
        "Old bullet point."
    )
    
    mock_update_resume = create_mock_tool_with_arun(
        'update_resume_in_memory_tool', 
        "Successfully updated section 'experience'."
    )

    toolbox.retrieve_context_tool = mock_retrieve
    toolbox.generate_text_tool = mock_generate
    toolbox.get_current_resume_section_tool = mock_get_section
    toolbox.update_resume_in_memory_tool = mock_update_resume
    
    return toolbox

@patch('agent.ChatGoogleGenerativeAI')
@patch('agent.get_session_history')
def test_agent_creation(mock_get_history, mock_chat_llm, mock_toolbox):
    """Tests that the agent executor is created successfully."""
    # Create a proper mock for chat history that passes isinstance checks
    mock_chat_history = MagicMock(spec=RedisChatMessageHistory)
    mock_chat_history.messages = []
    mock_get_history.return_value = mock_chat_history
    
    # Mock the chat model
    mock_chat_instance = MagicMock()
    mock_chat_llm.return_value = mock_chat_instance
    
    agent_executor = create_agent_executor(toolbox=mock_toolbox, session_id="s1")
    
    assert agent_executor is not None
    assert len(agent_executor.tools) == 4
    mock_get_history.assert_called_with("s1")

@pytest.mark.asyncio
@patch('agent.ChatGoogleGenerativeAI')
@patch('agent.get_session_history')
async def test_agent_rewrite_section_flow(mock_get_history, mock_chat_llm, mock_toolbox):
    """
    Conceptually tests the agent's decision-making flow for a section rewrite.
    """
    # Create a proper mock for chat history that handles both sync and async access
    mock_chat_history = MagicMock(spec=RedisChatMessageHistory)
    mock_chat_history.messages = []  # For sync memory loading
    mock_chat_history.aget_messages = AsyncMock(return_value=[]) # For async memory loading
    mock_get_history.return_value = mock_chat_history
    
    # Create a mock class that will be returned by bind_tools()
    class MockBoundLLM:
        def __init__(self):
            self.responses = []
        
        async def ainvoke(self, input_data, **kwargs):
            return self.responses.pop(0)
        
        # Make the mock callable
        async def __call__(self, *args, **kwargs):
            return await self.ainvoke(*args, **kwargs)
        
        # Add proper code object to pass inspection
        __code__ = (lambda *args, **kwargs: None).__code__

    # Set up the mock LLM
    mock_llm_instance = MagicMock()
    mock_chat_llm.return_value = mock_llm_instance
    
    # Create our mock bound LLM
    mock_bound_llm = MockBoundLLM()
    mock_llm_instance.bind_tools.return_value = mock_bound_llm

    # Mock the tool calls as expected by OpenAIToolsAgentOutputParser
    def create_tool_message(tool_name, tool_args):
        return {
            "tool_calls": [{
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(tool_args)
                }
            }]
        }
    
    import json
    from langchain_core.messages import AIMessage
    from langchain_core.agents import AgentFinish
    
    # Configure test responses
    mock_bound_llm.responses = [
        AIMessage(
            content="",
            additional_kwargs=create_tool_message(
                "get_current_resume_section_tool",
                {"session_id": "s1", "section_id": "experience"}
            )
        ),
        AIMessage(
            content="",
            additional_kwargs=create_tool_message(
                "retrieve_context_tool",
                {"session_id": "s1", "section_id": "experience"}
            )
        ),
        AIMessage(
            content="",
            additional_kwargs=create_tool_message(
                "generate_text_tool",
                {"session_id": "s1", "section_id": "experience", "existing_text": "Old bullet point."}
            )
        ),
        AIMessage(
            content="",
            additional_kwargs=create_tool_message(
                "update_resume_in_memory_tool",
                {"session_id": "s1", "section_id": "experience", "new_content_json": '{"experience": ["New bullet point."]}'}
            )
        ),
        AIMessage(
            content="I have successfully rewritten the experience section for you.",
            additional_kwargs={"tool_calls": []}
        ),
    ]

    agent_executor = create_agent_executor(toolbox=mock_toolbox, session_id="s1")
    result = await agent_executor.ainvoke({"input": "Please rewrite my experience section."})

    assert "I have successfully rewritten" in result["output"]
    
    # Verify the tool calls via arun method
    mock_toolbox.get_current_resume_section_tool.arun.assert_called_once_with(
        {"session_id": "s1", "section_id": "experience"},
        verbose=True,
        color=mock.ANY,  # Allow any color value
        callbacks=mock.ANY
    )
    mock_toolbox.retrieve_context_tool.arun.assert_called_once_with(
        {"session_id": "s1", "section_id": "experience"},
        verbose=True,
        color=mock.ANY,  # Allow any color value
        callbacks=mock.ANY
    )
    mock_toolbox.generate_text_tool.arun.assert_called_once_with(
        {
            "session_id": "s1",
            "section_id": "experience",
            "existing_text": "Old bullet point."
        },
        verbose=True,
        color=mock.ANY,  # Allow any color value
        callbacks=mock.ANY
    )
    mock_toolbox.update_resume_in_memory_tool.arun.assert_called_once_with(
        {
            "session_id": "s1",
            "section_id": "experience",
            "new_content_json": '{"experience": ["New bullet point."]}'
        },
        verbose=True,
        color=mock.ANY,  # Allow any color value
        callbacks=mock.ANY
    )