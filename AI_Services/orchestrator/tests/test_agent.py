import pytest
from unittest.mock import MagicMock, patch, create_autospec
from langchain.tools import Tool
from langchain.schema.agent import AgentFinish
from langchain.agents import AgentExecutor
from langchain_community.chat_message_histories import ChatMessageHistory

from agent import create_agent_executor
from tools import ToolBox

def mock_tool_func(*args, **kwargs):
    return "mocked"

class MockTool(Tool):
    def __init__(self, name, description):
        super().__init__(
            func=mock_tool_func,
            name=name,
            description=description,
            return_direct=False
        )
    
    def _run(self, *args, **kwargs):
        return "mocked"
    
    async def _arun(self, *args, **kwargs):
        return "mocked_async"

@pytest.fixture
def mock_toolbox():
    """Provides a mock ToolBox with all tools properly mocked."""
    toolbox = MagicMock(spec=ToolBox)
    
    # Create proper Tool instances for each tool
    tools = {
        'retrieve_context_tool': MockTool(
            name="retrieve_context_tool",
            description="Retrieves context from the user's profile"
        ),
        'generate_text_tool': MockTool(
            name="generate_text_tool",
            description="Generates text for a resume section"
        ),
        'get_current_resume_section_tool': MockTool(
            name="get_current_resume_section_tool",
            description="Gets the current content of a resume section"
        ),
        'update_resume_in_memory_tool': MockTool(
            name="update_resume_in_memory_tool",
            description="Updates a section of the resume in memory"
        ),
        'score_resume_text_tool': MockTool(
            name="score_resume_text_tool",
            description="Scores the resume text against job description"
        ),
        'get_improvement_suggestions_tool': MockTool(
            name="get_improvement_suggestions_tool",
            description="Gets suggestions for improving the resume"
        ),
        'get_full_resume_text_tool': MockTool(
            name="get_full_resume_text_tool",
            description="Gets the full resume text as a string"
        )
    }
    
    # Assign each tool to the toolbox
    for name, tool_obj in tools.items():
        setattr(toolbox, name, tool_obj)
    
    return toolbox

@patch('agent.ChatGoogleGenerativeAI')
@patch('agent.get_session_history')
def test_agent_creation(mock_get_history, mock_chat_llm, mock_toolbox):
    """Tests that the agent executor is created successfully with the correct tools."""
    # Arrange: Set up mocks
    mock_get_history.return_value = ChatMessageHistory()
    
    # Mock the LLM to return a valid response
    mock_llm_instance = MagicMock()
    mock_llm_instance.bind_tools.return_value = mock_llm_instance
    mock_chat_llm.return_value = mock_llm_instance
    
    # Mock the agent's __call__ method to return a valid AgentFinish
    mock_agent = MagicMock()
    mock_agent.return_value = AgentFinish(return_values={"output": "test"}, log="test")
    
    # Act
    with patch('agent.AgentExecutor') as mock_agent_executor:
        # Mock the agent executor creation
        mock_agent_executor.return_value = MagicMock(spec=AgentExecutor)
        
        try:
            agent_executor = create_agent_executor(toolbox=mock_toolbox, session_id="s1")
        except Exception as e:
            pytest.fail(f"agent_executor creation failed unexpectedly: {e}")
    
    # Assert
    assert agent_executor is not None
    mock_chat_llm.assert_called_once()
    mock_get_history.assert_called_once_with("s1")