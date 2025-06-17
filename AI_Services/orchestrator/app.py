# orchestrator/app.py

import os
from contextlib import asynccontextmanager
import httpx
import redis
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()

from .schemas import ChatRequest, ChatResponse, HealthResponse
from .agent import create_agent_executor
from .tools import ToolBox
from .memory import get_session_context, initialize_session_context

toolbox: ToolBox = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global toolbox
    http_client = httpx.AsyncClient(timeout=60.0)
    toolbox = ToolBox(client=http_client)
    yield
    await http_client.aclose()

app = FastAPI(title="Orchestrator Agent Service", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def get_toolbox() -> ToolBox:
    return toolbox

@app.post("/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, box: ToolBox = Depends(get_toolbox)) -> ChatResponse:
    # First validate the request for new sessions
    session_context = get_session_context(request.session_id)
    if not session_context and (not request.user_id or not request.job_description):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="For a new session, `user_id` and `job_description` are required."
        )
    
    try:
        # Initialize context for new sessions
        if not session_context:
            initialize_session_context(request.session_id, request.user_id, request.job_description)

        # Process the chat message
        agent_executor = create_agent_executor(box, request.session_id)
        response = await agent_executor.ainvoke({"input": request.user_message})
        
        # Get the final context to include in the response
        final_context = get_session_context(request.session_id)
        
        return ChatResponse(
            agent_response=response.get("output", "I'm sorry, I couldn't process your request."),
            session_id=request.session_id,
            resume_state=final_context.get("resume_state", {}) if final_context else {}
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the full error for debugging
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request."
        )

@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    try:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        r = redis.from_url(redis_url)
        r.ping()
        return HealthResponse(status="healthy", service="orchestrator-service", redis_connected=True)
    except Exception:
        return HealthResponse(status="unhealthy", service="orchestrator-service", redis_connected=False)