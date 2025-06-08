import os
import logging
import json
from typing import Dict, List, Any, Optional, Tuple

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage # SystemMessage not directly used in prompt but good for context
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.pydantic_v1 import BaseModel, Field # For agent output parsing if needed

# Assuming tools.py and schemas.py are in the same directory
from .tools import get_all_tools, BaseTool
from .schemas import OrchestrateResponse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Environment Variables --- #
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MATCH_THRESHOLD = float(os.getenv("MATCH_THRESHOLD", "0.75"))
AGENT_LLM_MODEL = os.getenv("AGENT_LLM_MODEL", "gpt-4o") # Using a more capable model for agent tasks
AGENT_LLM_TEMPERATURE = float(os.getenv("AGENT_LLM_TEMPERATURE", "0.0")) # Low temp for deterministic planning
AGENT_MEMORY_WINDOW_K = int(os.getenv("AGENT_MEMORY_WINDOW_K", "5")) # Number of past interactions to remember

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not found. Orchestrator agent will not function.")
    # raise ValueError("OPENAI_API_KEY not found.") # Or handle more gracefully

# --- Agent System Prompt --- #
# This prompt guides the agent's planning and tool usage.
# It explicitly mentions the expected output structure of each tool.

SYSTEM_PROMPT_TEMPLATE = f"""
You are an expert resume tailoring assistant. Your primary goal is to help the user optimize their resume for a specific job description by generating tailored bullets and providing suggestions.
You operate by following a precise sequence of tool calls.

User will provide: `user_id` and `job_description`.
Your final output MUST be a JSON-formatted string that can be parsed into the OrchestrateResponse schema:
{{
  "bullets": ["bullet1", "bullet2", ...],
  "match_score": 0.XX,
  "suggestions": ["suggestion1", "suggestion2", ...] (This list can be empty if no suggestions are generated)
}}

Available Tools: {{tool_names}}
Tool Specifications (Pay close attention to their inputs and outputs!):
# Note: embed_tool and retrieve_tool are available but not used in the main flow
# as the Generator Service handles its own embedding and retrieval internally.

- `generate_tool`:
    - This is the primary tool to start the resume tailoring process.
    - The Generator Service, when called by this tool, internally handles embedding the job description and retrieving relevant resume chunks before generating the bullets.
    - Input: `user_id` (str), `job_description` (str). The `retrieved_chunks` parameter is available but not actively used by the agent in this simplified plan.
    - Output: A dictionary e.g., `{{"bullets": ["generated bullet 1", "generated bullet 2"], "raw_prompt": "..."}}`. `raw_prompt` is optional. If `bullets` is empty, this is an issue.

- `score_tool`:
    - Input: `generated_bullets` (List[str]), `job_description` (str).
    - Output: A dictionary e.g., `{{"score": 0.85, "missing_keywords": ["skill1"], "suggestions": ["scoring service suggestion"]}}`. `missing_keywords` and `suggestions` from the scoring service are optional.

- `suggest_tool`:
    - Input: `job_description` (str), `current_bullets` (List[str]), `match_score` (float).
    - Output: A dictionary e.g., `{{"suggestions": ["suggestion 1", "suggestion 2"]}}`.

Follow this precise plan:

1.  **Generate Resume Bullets**:
    *   Thought: I need to generate resume bullets using the `user_id` and the `job_description`. The Generator Service will handle all necessary data retrieval internally.
    *   Action: Call `generate_tool` with `user_id` and `job_description`.
    *   Observation: Receive the generated bullets (e.g., `{{"bullets": ["bullet X", "bullet Y"], "raw_prompt": "..."}}`).

2.  **Score Generated Bullets**:
    *   Thought: I need to score the `generated_bullets` (from step 1) against the `job_description`.
    *   Action: Call `score_tool` with `generated_bullets` (from step 1) and `job_description`.
    *   Observation: Receive the match score and potentially other feedback (e.g., `{{"score": 0.78, "missing_keywords": [], "suggestions": []}}`). Store all parts of this response.

3.  **Conditionally Generate Suggestions**:
    *   Thought: I need to check if the `match_score` (from step 2) is below the defined threshold of {MATCH_THRESHOLD}.
    *   If `match_score < {MATCH_THRESHOLD}`:
        *   Thought: The score is low. I need to generate improvement suggestions.
        *   Action: Call `suggest_tool` with `job_description`, `generated_bullets` (from step 1), and `match_score` (from step 2).
        *   Observation: Receive suggestions (e.g., `{{"suggestions": ["suggestion A", "suggestion B"]}}`).
    *   If `match_score >= {MATCH_THRESHOLD}`:
        *   Thought: The score is good. No suggestions are needed. The suggestions list will be empty.

4.  **Formulate Final Response**:
    *   Thought: I have all the necessary components: `generated_bullets` (from step 1), `match_score` (from step 2), potentially `missing_keywords` and `suggestions` from `score_tool` (step 2), and `suggestions` from `suggest_tool` (step 3, if triggered). I need to assemble them into the final JSON output structure. Suggestions from `score_tool` and `suggest_tool` should be combined if both exist.
    *   Action: Construct the JSON string. The `suggestions` field in the final output should combine suggestions from `score_tool` (if any) and `suggest_tool` (if any and if step 3 was executed). `missing_keywords` from `score_tool` are valuable but are not directly part of the `OrchestrateResponse`'s top-level `suggestions` field; they are usually part of the `score_tool`'s direct output which the agent uses for decision making or could be logged. For the final response, focus on the `suggestions` that are actionable advice for the user.
        `{{"bullets": <list_of_bullets_from_step_1>, "match_score": <score_from_step_2>, "suggestions": <combined_list_of_suggestions_from_score_tool_and_suggest_tool_or_empty_list>}}`
    *   This JSON string is your final answer. Do not add any conversational text around it.

Error Handling:
- If any tool call fails even after retries (as handled by the tool's internal logic), or returns an empty/unexpected result that prevents the next step (e.g., `generate_tool` returns no bullets), you should try to describe the problem in your final output if possible, but still adhere to the JSON structure. For example, bullets might be an empty list and score 0, with a suggestion indicating the failure. However, the tools themselves have retry logic. Your main job is to follow the plan.

Memory:
- You have access to chat history. Use it to understand context if the user makes follow-up requests like "tweak this bullet", but for the initial `/orchestrate` call, strictly follow the plan above.
"""

# Store chat history in memory (simple in-memory store for this example)
# For a production system, you'd use a persistent store like Redis, a database, etc.
chat_memory_store = {}

def get_session_history(session_id: str, user_id: str): # user_id added for potential namespacing
    if session_id not in chat_memory_store:
        # Initialize with a system message if desired, or keep it clean
        chat_memory_store[session_id] = ConversationBufferWindowMemory(
            k=AGENT_MEMORY_WINDOW_K,
            memory_key="chat_history",
            input_key="input", # Key for the human's input to the agent
            output_key="output", # Key for the agent's output
            return_messages=True
        )
    return chat_memory_store[session_id]

# Global agent executor instance
_agent_executor: Optional[AgentExecutor] = None

def get_orchestrator_agent_executor() -> AgentExecutor:
    global _agent_executor
    if _agent_executor is not None:
        return _agent_executor

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set. Cannot initialize agent.")

    llm = ChatOpenAI(
        model=AGENT_LLM_MODEL,
        temperature=AGENT_LLM_TEMPERATURE,
        openai_api_key=OPENAI_API_KEY
    )
    tools = get_all_tools()
    tool_names = ", ".join([tool.name for tool in tools])

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT_TEMPLATE.format(tool_names=tool_names, MATCH_THRESHOLD=MATCH_THRESHOLD)),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

    _agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True, # Logs thoughts, actions, observations
        handle_parsing_errors="Please output a valid JSON-formatted string as described in the initial plan.", # Custom message or True
        return_intermediate_steps=True, # Useful for logging/debugging
        max_iterations=10 # Prevent runaway agents
    )
    logger.info("Orchestrator AgentExecutor initialized.")
    return _agent_executor


async def run_orchestration_agent(
    user_id: str,
    job_description: str,
    session_id: str = "default_session" # A session ID for managing memory
) -> OrchestrateResponse:
    """
    Runs the orchestration agent to process the job description and user ID.
    """
    agent_executor_with_history = RunnableWithMessageHistory(
        get_orchestrator_agent_executor(),
        lambda s_id: get_session_history(s_id, user_id), # Pass user_id for potential namespacing in get_session_history
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    # The input to the agent should be a single string or a dictionary matching the prompt's input variables
    # The system prompt expects user_id and job_description to be available,
    # but the direct input to the agent via `invoke` is typically a single "input" field.
    # We'll format the input string to contain this information for the LLM to parse.
    agent_input = f"User ID: {user_id}\\nJob Description: {job_description}"

    logger.info(f"Running orchestration agent for user_id: {user_id}, session_id: {session_id}")
    
    final_response_dict = {
        "bullets": [],
        "match_score": 0.0,
        "suggestions": []
    }

    try:
        # The agent's output should be the JSON string as instructed in the system prompt.
        # Intermediate steps are for logging.
        response = await agent_executor_with_history.ainvoke(
            {"input": agent_input},
            config={"configurable": {"session_id": session_id, "user_id": user_id}} # Pass user_id here too
        )
        
        # response['output'] should be the final JSON string from the agent
        agent_final_output_str = response.get("output")
        logger.info(f"Agent raw output string: {agent_final_output_str}")

        if not agent_final_output_str:
            raise ValueError("Agent returned an empty final output.")

        # Parse the JSON string output from the agent
        try:
            parsed_output = json.loads(agent_final_output_str)
            final_response_dict["bullets"] = parsed_output.get("bullets", [])
            # The agent's output for 'match_score' should come from the 'score' field of the score_tool's output.
            # The 'suggestions' in the final response should be what the agent decided to put there based on its plan (combining score_tool suggestions and suggest_tool suggestions).
            final_response_dict["match_score"] = parsed_output.get("match_score", parsed_output.get("score", 0.0)) # Accommodate if agent uses 'score'
            final_response_dict["suggestions"] = parsed_output.get("suggestions", [])
            
            # Validate with Pydantic model
            # OrchestrateResponse expects 'match_score', not 'score'.
            # Ensure the keys in final_response_dict match OrchestrateResponse fields.
            validated_data = {
                "bullets": final_response_dict["bullets"],
                "match_score": final_response_dict["match_score"],
                "suggestions": final_response_dict["suggestions"]
            }
            orchestrate_response = OrchestrateResponse(**validated_data)
            logger.info(f"Agent successfully processed request for user_id: {user_id}. Score: {orchestrate_response.match_score}")
            return orchestrate_response

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse agent's final JSON output: {agent_final_output_str}. Error: {e}")
            # Fallback or error response
            final_response_dict["suggestions"].append(f"Error: Agent output was not valid JSON. Details: {e}")
            return OrchestrateResponse(**final_response_dict) # Return with error in suggestions
        except Exception as e: # Catch Pydantic validation or other errors
            logger.error(f"Error processing agent's structured output: {e}. Output was: {agent_final_output_str}")
            final_response_dict["suggestions"].append(f"Error: Could not process agent output. Details: {e}")
            return OrchestrateResponse(**final_response_dict)


    except Exception as e:
        logger.error(f"Error during agent execution for user_id {user_id}: {e}", exc_info=True)
        # Log intermediate steps if available in 'e' or if caught differently
        # For now, return a generic error response via the OrchestrateResponse schema
        final_response_dict["suggestions"].append(f"Critical agent error: {str(e)}")
        return OrchestrateResponse(**final_response_dict)

if __name__ == '__main__':
    # Example of how to run (requires services and .env file with API keys)
    # Ensure environment variables like OPENAI_API_KEY, MATCH_THRESHOLD, and service URLs are set.
    # You would also need the other services (embedding, retrieval, etc.) running.
    
    # Example:
    # os.environ['OPENAI_API_KEY'] = "your_key_here"
    # os.environ['MATCH_THRESHOLD'] = "0.7"
    # os.environ['EMBEDDING_SERVICE_URL'] = "http://localhost:8000/embed" # Placeholder
    # os.environ['RETRIEVAL_SERVICE_URL'] = "http://localhost:8001/retrieve" # Placeholder
    # os.environ['GENERATION_SERVICE_URL'] = "http://localhost:8002/generate" # Placeholder
    # os.environ['SCORING_SERVICE_URL'] = "http://localhost:8003/score" # Placeholder
    # os.environ['GEMINI_API_KEY'] = "your_gemini_key_here" # Placeholder

    # async def main():
    #     test_user_id = "test_user_123"
    #     test_jd = "We are looking for a skilled Python developer with experience in FastAPI and Docker. The ideal candidate should be proficient in building scalable microservices and have a strong understanding of RESTful APIs. Experience with LangChain and AI agent development is a plus."
    #     test_session_id = "session_test_abc"
        
    #     print(f"Attempting to run agent for user: {test_user_id}, session: {test_session_id}")
    #     response = await run_orchestration_agent(test_user_id, test_jd, test_session_id)
    #     print("\\n--- Orchestrator Response ---")
    #     print(f"Bullets: {response.bullets}")
    #     print(f"Match Score: {response.match_score}")
    #     print(f"Suggestions: {response.suggestions}")

    # import asyncio
    # if OPENAI_API_KEY: # Only run if key is present
    #    asyncio.run(main())
    # else:
    #    print("Skipping agent run example as OPENAI_API_KEY is not set.")
    pass