# Orchestrator Agent Service

A complete, detailed implementation of the Orchestrator module that serves as the central AI brain for a resume-building assistant.

This is a stateful, AI-powered microservice that acts as the central "brain" for a resume-building assistant. It orchestrates complex tasks by interpreting user requests, managing conversation state, and delegating work to specialized backend services.

## Technology Stack

The service is built on a modern, robust technology stack:

### Core Technologies

* **FastAPI**: High-performance, asynchronous web framework
* **LangChain**: For building and managing the core LLM-powered agent
* **Google Gemini**: Powers the advanced reasoning and tool-using capabilities
* **Redis**: Handles durable and fast session management
* **Pydantic**: Provides robust data validation and API schemas
* **HTTPX**: Enables asynchronous communication with other services

## Architecture Overview

The Orchestrator Service is the central coordinator in a microservices ecosystem. It receives user requests, uses an LLM agent to decide on a course of action, and calls other services to execute specific tasks like data retrieval, content generation, or scoring.

```mermaid
graph TD
    Title["<strong>Orchestrator Service Flow (Agent Logic)</strong>"]
    style Title fill:#222,stroke:#333,stroke-width:2px,color:#fff

    Title --> UserClient["User Client"]

    subgraph Orchestrator Service
        UserClient -- "(1) POST /v1/chat (user_message)" --> AgentReasoning{Agent Reasoning Loop}
        
        AgentReasoning -- "(2) Sends prompt to LLM" --> GeminiAPI["Google Gemini API"]
        GeminiAPI -- "(3) LLM returns a tool-use decision" --> AgentReasoning

        AgentReasoning -- "(4a) DECISION: Use a tool" --> ToolExecution["Execute Chosen Tool"]
        
        subgraph "Available Tools (connect to other services)"
            ToolExecution --> Redis["Redis (get/update state)"]
            ToolExecution --> RetrievalService["Retrieval Service"]
            ToolExecution --> GeneratorService["Generator Service"]
            ToolExecution --> ScoringService["Scoring Service"]
        end
        
        %% The crucial loop back to continue the cycle
        ToolExecution -- "(5) Tool result is fed back for next step" --> AgentReasoning
        
        %% The exit condition of the loop
        AgentReasoning -- "(4b) DECISION: Task is complete" --> FinalResponse["Formulate Final Response"]
        FinalResponse -- "(6) Returns ChatResponse to user" --> UserClient
    end
```

## 🧠 Core Concepts

### 1. The LangChain Agent
The service's intelligence comes from a LangChain agent powered by the `gemini-1.5-pro-latest` model. The agent's behavior is strictly defined by a `SYSTEM_PROMPT` that instructs it to follow a robust "generate -> update -> score -> improve" workflow. This ensures that every piece of generated content is quality-checked before being finalized.

### 2. Stateful Session Management
A conversation about building a resume is inherently stateful. This service uses **Redis** to manage two critical pieces of information for each `session_id`:
- **Conversation History:** A turn-by-turn log of the user and agent messages, managed by `RedisChatMessageHistory`. This gives the agent the context of the ongoing conversation.
- **Session Context:** A JSON object stored in Redis that acts as the **source of truth** for the session. It contains the `user_id`, the target `job_description`, and the `resume_state`—a complete, up-to-date JSON representation of the resume being built.

### 3. The ToolBox
The agent's capabilities are defined by the set of tools it can use. These tools are methods within the `ToolBox` class and are the bridge between the agent's reasoning and the outside world.
- `retrieve_context_tool`: Calls the **Retrieval Service** to find relevant information from the user's professional profile.
- `generate_text_tool`: Calls the **Generator Service** to create new or revised text for a resume section.
- `get_full_resume_text_tool`: Compiles the entire resume from Redis into a single string, which is required for the scoring tool.
- `score_resume_text_tool`: Calls the **Scoring Service** to get a match score and identify missing keywords.
- `get_improvement_suggestions_tool`: Calls the **Scoring Service** to get AI-powered improvement tips if the score is low.
- `update_resume_in_memory_tool`: **A critical step.** The agent uses this tool to save newly generated content back into the `resume_state` in Redis.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- A virtual environment tool (e.g., `venv`, `conda`)
- Access to a running Redis instance.

### Local Setup
1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd orchestrator
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the `orchestrator` directory and populate it with your credentials and service URLs.
    ```env
    # .env
    GEMINI_API_KEY="your-google-api-key"
    REDIS_URL="redis://localhost:6379"

    # URLs for downstream services (ports are defaults)
    GENERATION_SERVICE_URL="http://localhost:8000"
    RETRIEVAL_SERVICE_URL="http://localhost:8002"
    SCORING_SERVICE_URL="http://localhost:8004"
    ```

5.  **Run the service:**
    The orchestrator service runs on port 8080 by default to avoid conflicts.
    ```bash
    uvicorn app:app --host 0.0.0.0 --port 8080 --reload
    ```
    The service will now be running at `http://localhost:8080`.

## 📚 API Documentation

### Chat Endpoint

#### `POST /v1/chat`
This is the main endpoint for all user interactions with the agent. It's stateful and relies on a `session_id`.

- **Description:** Sends a user message to the agent and receives a conversational response and the updated resume state.
- **Note:** The `user_id` and `job_description` fields are **required for the first message** of a new session to initialize the context. They can be omitted for all subsequent messages in that session.

- **cURL Example (New Session):**
  ```bash
  curl -X POST "http://localhost:8080/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-xyz-789",
    "user_message": "Help me create a resume for this job.",
    "user_id": "user-123",
    "job_description": "We are seeking a Senior Python Developer with experience in FastAPI and cloud services..."
  }'
  ```

- **cURL Example (Follow-up Message):**
  ```bash
  curl -X POST "http://localhost:8080/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-xyz-789",
    "user_message": "Great, now rewrite my summary section."
  }'
  ```

- **Success Response (`ChatResponse`):**
  ```json
  {
    "agent_response": "I've drafted a new summary for you. It scores 0.85 against the job description. I've saved this update to your resume.",
    "session_id": "session-xyz-789",
    "resume_state": {
      "summary": "A highly motivated Senior Python Developer with 8 years of experience...",
      "experience": [
        {
          "title": "Lead Developer",
          "company": "Tech Solutions Inc.",
          "duties": ["..."]
        }
      ]
    }
  }
  ```

### Utility Endpoints

- `GET /health`: A simple health check endpoint that verifies the service is running and can connect to Redis.

## 🔄 Agent Logic Flow: An Example

To understand the service's behavior, consider a user asking: *"Rewrite my experience section."*

1.  **User Request**: `POST /v1/chat` with the user's message.
2.  **Agent Invocation**: The `chat_endpoint` invokes the agent.
3.  **Agent Reasoning (Step 1)**: The agent determines it needs context.
4.  **Tool Call (1)**: It calls `retrieve_context_tool(section_id='experience')`. This triggers an HTTP request to the **Retrieval Service**.
5.  **Agent Reasoning (Step 2)**: The agent now has context and needs to generate the new text.
6.  **Tool Call (2)**: It calls `generate_text_tool(section_id='experience', ...)`. This triggers an HTTP request to the **Generator Service**.
7.  **Agent Reasoning (Step 3)**: The generation was successful. The `SYSTEM_PROMPT` requires the agent to save and score its work.
8.  **Tool Call (3)**: It calls `update_resume_in_memory_tool(section_id='experience', ...)`. This updates the `resume_state` in Redis.
9.  **Agent Reasoning (Step 4)**: The draft is saved. Now, to score it, the agent needs the full resume text.
10. **Tool Call (4)**: It calls `get_full_resume_text_tool()`, which assembles the complete resume from Redis.
11. **Tool Call (5)**: It calls `score_resume_text_tool()` with the full text, triggering a call to the **Scoring Service**.
12. **Agent Reasoning (Step 5)**: The agent analyzes the score. If it's low, it might call `get_improvement_suggestions_tool()`. If high, it proceeds.
13. **Final Response**: The agent formulates a user-friendly message confirming the action and the score, then returns it along with the complete, updated `resume_state`.

## ⚙️ External Dependencies

This service is designed to work as part of a larger system and has several key external dependencies:

- **Redis**: A running Redis instance is **required** for session management.
- **Retrieval Service**: A separate microservice responsible for semantic search. Must be accessible at the URL defined by `RETRIEVAL_SERVICE_URL`.
- **Generator Service**: A separate microservice responsible for high-quality text generation. Must be accessible at the URL defined by `GENERATION_SERVICE_URL`.
- **Scoring Service**: A separate microservice for resume scoring and analysis. Must be accessible at the URL defined by `SCORING_SERVICE_URL`.
- **Google Cloud / Gemini API**: Requires a valid `GEMINI_API_KEY` for the agent's core LLM to function.

## 📁 Project Structure

```
orchestrator/
├── __init__.py           # Module initializer
├── agent.py              # Agent definition, including the main system prompt
├── app.py                # Main FastAPI application, endpoints, and lifecycle
├── memory.py             # Functions for interacting with Redis session state
├── README.md             # This documentation
├── requirements.txt      # Python package dependencies
├── schemas.py            # Pydantic models for API and internal validation
└── tools.py              # The ToolBox class defining all agent capabilities
```