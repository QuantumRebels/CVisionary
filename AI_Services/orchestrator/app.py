# app.py

import os
from contextlib import asynccontextmanager
import httpx
import redis
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .schemas import ChatRequest, ChatResponse, HealthResponse
from .agent import create_agent_executor
from .tools import ToolBox
from .memory import get_session_context, initialize_session_context

# Global variable for the toolbox
toolbox: ToolBox = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    global toolbox
    
    # Startup
    http_client = httpx.AsyncClient(timeout=60.0)
    toolbox = ToolBox(client=http_client)
    
    # Check Redis connection on startup
    try:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        redis_client = redis.from_url(redis_url)
        redis_client.ping()
        print("Successfully connected to Redis.")
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
    
    yield
    
    # Shutdown
    await http_client.aclose()

app = FastAPI(
    title="Orchestrator Agent Service",
    description="AI-powered resume building orchestrator",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Main chat endpoint for interactive resume building."""
    try:
        # Check if session exists, if not, initialize it
        session_context = get_session_context(request.session_id)
        if not session_context:
            if not request.user_id or not request.job_description:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="For a new session, `user_id` and `job_description` are required."
                )
            session_context = initialize_session_context(
                request.session_id, request.user_id, request.job_description
            )

        agent_executor = create_agent_executor(toolbox, request.session_id)
        
        response = await agent_executor.ainvoke({"input": request.user_message})
        
        agent_response = response.get("output", "I'm sorry, I couldn't process your request.")
        
        # Get the latest resume state to return to the client
        final_context = get_session_context(request.session_id)
        
        return ChatResponse(
            agent_response=agent_response,
            session_id=request.session_id,
            resume_state=final_context.get("resume_state", {})
        )
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")

@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint that verifies Redis connectivity."""
    try:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        r = redis.from_url(redis_url)
        r.ping()
        return HealthResponse(status="healthy", service="orchestrator-service", redis_connected=True)
    except Exception as e:
        return HealthResponse(status="unhealthy", service="orchestrator-service", redis_connected=False)