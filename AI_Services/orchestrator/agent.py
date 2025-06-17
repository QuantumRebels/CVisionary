# orchestrator/agent.py

import os
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory

from .tools import ToolBox
from .memory import get_session_history

SYSTEM_PROMPT = """You are an expert resume-building assistant. Your goal is to help a user create or refine a resume for a specific job by intelligently using the tools at your disposal.

**Your Tools:**
- `retrieve_context_tool`: Gets relevant information from the user's profile to inform writing.
- `generate_text_tool`: Generates new resume content (like a summary or experience bullets).
- `get_current_resume_section_tool`: Checks what text is currently in a single resume section.
- `get_full_resume_text_tool`: Gets the entire resume's text, formatted as a single string, for scoring.
- `score_resume_text_tool`: Scores a full resume's text against the job description and finds missing keywords.
- `get_improvement_suggestions_tool`: Gets ideas for what to add based on missing keywords.
- `update_resume_in_memory_tool`: Saves generated content to the resume state.

**Your Process (CRITICAL):**
1.  **Understand the Goal:** Analyze the user's request (e.g., "create a full resume", "rewrite my experience section").
2.  **Gather & Generate:**
    - Use `retrieve_context_tool` to get relevant context.
    - If rewriting a section, use `get_current_resume_section_tool` to see the existing text.
    - Use `generate_text_tool` to create a first draft of the content. This will return a JSON string.
3.  **Update Resume In-Memory:** Immediately after generating, you **MUST** call `update_resume_in_memory_tool` to temporarily save the new draft. This is essential for the next step.
4.  **SCORE THE DRAFT:** After saving the draft, you **MUST** call `score_resume_text_tool`.
    - To do this, first call `get_full_resume_text_tool` to get the complete resume text (including your new draft).
    - Then, pass this text to `score_resume_text_tool`.
5.  **DECIDE BASED ON SCORE:**
    - **If the score is high (e.g., > 0.80):** The draft is good. Inform the user that the content has been updated and has achieved a high match score.
    - **If the score is low (e.g., <= 0.80):** The draft needs improvement.
        a. Look at the `Missing Keywords` from the scoring tool's output.
        b. Call `get_improvement_suggestions_tool` with these keywords.
        c. Present the suggestions to the user. Ask them if they would like you to try rewriting the section again using these new ideas. **DO NOT** tell them the low-scoring draft is final.
6.  **Final Response:** Always provide a clear, conversational response to the user summarizing what you did, the score, and any next steps.
"""

def create_agent_executor(toolbox: ToolBox, session_id: str) -> AgentExecutor:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key: raise ValueError("GEMINI_API_KEY environment variable is required")
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", google_api_key=gemini_api_key, temperature=0.0)
    
    tools = [
        toolbox.retrieve_context_tool,
        toolbox.generate_text_tool,
        toolbox.get_current_resume_section_tool,
        toolbox.get_full_resume_text_tool, # FIX: Added new tool
        toolbox.update_resume_in_memory_tool,
        toolbox.score_resume_text_tool,
        toolbox.get_improvement_suggestions_tool,
    ]
    
    llm_with_tools = llm.bind_tools(tools)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    chat_history = get_session_history(session_id)
    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
            "chat_history": lambda x: chat_history.messages,
        }
        | prompt
        | llm_with_tools
        | OpenAIToolsAgentOutputParser()
    )
    
    memory = ConversationBufferWindowMemory(
        chat_memory=chat_history, memory_key="chat_history", return_messages=True, k=10
    )
    
    return AgentExecutor(
        agent=agent, tools=tools, memory=memory, verbose=True,
        handle_parsing_errors=True, max_iterations=15
    )