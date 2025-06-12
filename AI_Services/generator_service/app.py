"""
FastAPI application for the Generator Service.
"""
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    FullGenerateRequest,
    SectionGenerateRequest,
    GenerateResponse,
    HealthResponse
)
from .utils import (
    retrieve_full_context,
    retrieve_section_context,
    format_context_for_prompt
)
from .prompt_templates import FULL_RESUME_TEMPLATE, SECTION_REWRITE_TEMPLATE
from .llm_client import invoke_gemini, LLMError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global HTTP client for sharing across requests
http_client: httpx.AsyncClient = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage the lifecycle of the shared HTTP client."""
    global http_client
    
    # Startup
    logger.info("Starting up Generator Service")
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
    )
    logger.info("HTTP client initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Generator Service")
    if http_client:
        await http_client.aclose()
        logger.info("HTTP client closed")


# Initialize FastAPI app
app = FastAPI(
    title="Generator Service",
    description="AI-powered resume generation service",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_http_client() -> httpx.AsyncClient:
    """Dependency to provide the shared HTTP client."""
    if http_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="HTTP client not initialized"
        )
    return http_client


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="generator-service"
    )


@app.post("/generate/full", response_model=GenerateResponse)
async def generate_full_resume(
    request: FullGenerateRequest,
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Generate a complete resume from scratch based on user profile and job description.
    """
    logger.info(f"Full resume generation request for user {request.user_id}")
    
    try:
        # Get default top_k if not provided
        top_k = request.top_k or int(os.getenv("DEFAULT_TOP_K", "7"))
        
        # Retrieve context from the Retrieval Service
        try:
            chunks = await retrieve_full_context(
                client, 
                request.user_id, 
                request.job_description, 
                top_k
            )
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to retrieve context from Retrieval Service"
            )
        
        # Format context for the prompt
        profile_context = format_context_for_prompt(chunks)
        
        # Build the prompt using the template
        prompt = FULL_RESUME_TEMPLATE.render(
            job_description=request.job_description,
            profile_context=profile_context
        )
        
        # Generate content using Gemini
        try:
            generated_text = await invoke_gemini(client, prompt)
        except LLMError as e:
            logger.error(f"LLM generation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to generate content from LLM service"
            )
        
        logger.info(f"Successfully generated full resume for user {request.user_id}")
        
        return GenerateResponse(
            generated_text=generated_text,
            raw_prompt=prompt,
            retrieval_mode="full",
            section_id=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in full generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during resume generation"
        )


@app.post("/generate/section", response_model=GenerateResponse)
async def generate_section(
    request: SectionGenerateRequest,
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Generate or rewrite a specific section of a resume.
    """
    logger.info(f"Section generation request for user {request.user_id}, section {request.section_id}")
    
    try:
        # Get default top_k if not provided
        top_k = request.top_k or int(os.getenv("DEFAULT_TOP_K", "7"))
        
        # Retrieve section-specific context
        try:
            chunks = await retrieve_section_context(
                client,
                request.user_id,
                request.section_id,
                request.job_description,
                top_k
            )
        except Exception as e:
            logger.error(f"Failed to retrieve section context: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to retrieve context from Retrieval Service"
            )
        
        # Format context for the prompt
        relevant_context = format_context_for_prompt(chunks)
        
        # Build the prompt using the section template
        prompt = SECTION_REWRITE_TEMPLATE.render(
            job_description=request.job_description,
            section_id=request.section_id,
            existing_text=request.existing_text or "",
            relevant_context=relevant_context
        )
        
        # Generate content using Gemini
        try:
            generated_text = await invoke_gemini(client, prompt)
        except LLMError as e:
            logger.error(f"LLM generation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to generate content from LLM service"
            )
        
        logger.info(f"Successfully generated section {request.section_id} for user {request.user_id}")
        
        return GenerateResponse(
            generated_text=generated_text,
            raw_prompt=prompt,
            retrieval_mode="section",
            section_id=request.section_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in section generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during section generation"
        )