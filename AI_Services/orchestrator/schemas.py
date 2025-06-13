# schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    """Request model for the main chat endpoint."""
    session_id: str = Field(..., description="A unique identifier for the user's session.")
    user_message: str = Field(..., description="The user's message or instruction to the agent.")
    # Optional fields to initialize or update the session
    user_id: Optional[str] = Field(None, description="The user's ID, required for the first message in a session.")
    job_description: Optional[str] = Field(None, description="The job description, required for the first message.")

class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""
    agent_response: str = Field(..., description="The natural language response from the agent.")
    session_id: str = Field(..., description="The session identifier.")
    # We can add more structured data here in the future, e.g., the full resume state
    resume_state: Optional[Dict[str, Any]] = Field(None, description="The current state of the resume being built.")

class HealthResponse(BaseModel):
    """Response model for the health check endpoint."""
    status: str = Field(..., description="Overall health status of the service.")
    service: str = Field(..., description="The name of the service.")
    redis_connected: bool = Field(..., description="Indicates if the connection to Redis is successful.")