# agent.py

import os
import json
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory

from .tools import ToolBox
from .memory import get_session_history

# A more robust prompt designed for tool calling agents.
SYSTEM_PROMPT = """You are an expert resume-building assistant. Your goal is to help a user create or refine a resume for a specific job by intelligently using the tools at your disposal.

**Your Process:**
1.  **Understand the Goal:** Analyze the user's message and the conversation history to understand their intent (e.g., create a full resume, rewrite a section).
2.  **Gather Information:**
    - If you need to know what's already in a resume section, use `get_current_resume_section_tool`.
    - To get relevant information from the user's broader profile, use `retrieve_context_tool`.
3.  **Generate Content:** Once you have the necessary information, use `generate_text_tool` to create the new resume content.
4.  **Save Your Work:** After generating content for a section, you **MUST** save it using `update_resume_in_memory_tool`. This is critical for keeping the resume up-to-date for future edits.
5.  **Respond to the User:** Formulate a helpful, conversational response to the user, confirming what you've done.

**Important Rules:**
- Do not make up information. Only use the information provided by your tools.
- Always confirm that you have updated the resume in memory after a generation step.
- If a tool returns an error, inform the user about the problem gracefully.
"""

def create_agent_executor(toolbox: ToolBox, session_id: str) -> AgentExecutor:
    """Create and configure a LangChain agent executor for resume building."""
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", google_api_key=gemini_api_key, temperature=0.0)
    
    tools = [
        toolbox.retrieve_context_tool,
        toolbox.generate_text_tool,
        toolbox.get_current_resume_section_tool,
        toolbox.update_resume_in_memory_tool,
    ]
    
    # Bind the tools to the LLM for tool-calling
    llm_with_tools = llm.bind_tools(tools)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | llm_with_tools
        | OpenAIToolsAgentOutputParser()
    )
    
    memory = ConversationBufferMemory(
        chat_memory=get_session_history(session_id),
        memory_key="chat_history",
        return_messages=True
    )
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors="Please try again, paying close attention to the required output format.",
        max_iterations=10
    )
    
    return agent_executor