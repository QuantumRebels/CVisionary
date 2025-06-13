# orchestrator_service/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# --- Public API Schemas ---

class ChatRequest(BaseModel):
    """
    Request model for the main chat endpoint.
    This is the primary input to the Orchestrator Agent.
    """
    session_id: str = Field(
        ...,
        description="A unique identifier for the user's session. This ID is used to maintain conversation history and state.",
        min_length=1
    )
    user_message: str = Field(
        ...,
        description="The user's message or instruction to the agent (e.g., 'Create a resume for this job', 'Rewrite my experience section').",
        min_length=1
    )
    
    # These fields are only required for the *first* message in a new session
    # to initialize the agent's context.
    user_id: Optional[str] = Field(
        None,
        description="The user's ID. Required only for the first message in a new session."
    )
    job_description: Optional[str] = Field(
        None,
        description="The full job description. Required only for the first message in a new session."
    )

class ChatResponse(BaseModel):
    """
    Response model for the chat endpoint.
    This is the primary output from the Orchestrator Agent.
    """
    agent_response: str = Field(
        ...,
        description="The natural language response from the agent to the user."
    )
    session_id: str = Field(
        ...,
        description="The session identifier, returned for client-side state management."
    )
    resume_state: Optional[Dict[str, Any]] = Field(
        None,
        description="The current state of the resume being built, returned after each turn for the client to display."
    )

class HealthResponse(BaseModel):
    """
    Response model for the health check endpoint.
    """
    status: str = Field(..., description="Overall health status of the service.")
    service: str = Field(..., description="The name of the service.")
    redis_connected: bool = Field(..., description="Indicates if the connection to Redis is successful.")


# --- Internal Schemas (for validating responses from other services) ---

class ChunkItem(BaseModel):
    """
    Internal model to validate a chunk item received from the Retrieval Service.
    Must match the schema in the Retrieval Service.
    """
    chunk_id: str
    user_id: str
    index_namespace: str
    section_id: Optional[str]
    source_type: str
    source_id: str
    text: str
    score: float
    created_at: datetime

class RetrieveResponse(BaseModel):
    """
    Internal model to validate the full response from the Retrieval Service.
    """
    results: List[ChunkItem]

class GenerateResponse(BaseModel):
    """
    Internal model to validate the full response from the Generation Service.
    """
    generated_text: str
    raw_prompt: str
    retrieval_mode: str
    section_id: Optional[str] = None