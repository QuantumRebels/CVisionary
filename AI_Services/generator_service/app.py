# app.py

"""
FastAPI application for the Generator Service.
"""
import json
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    FullGenerateRequest,
    SectionGenerateRequest,
    GenerateResponse,
    HealthResponse,
)
from utils import (
    retrieve_full_context,
    retrieve_section_context,
    format_context_for_prompt,
)
from prompt_templates import FULL_RESUME_TEMPLATE, SECTION_REWRITE_TEMPLATE
from llm_client import invoke_gemini, LLMError

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global HTTP client for sharing across requests
http_client: httpx.AsyncClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage the lifecycle of the shared HTTP client."""
    global http_client
    logger.info("Starting up Generator Service")
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(60.0),
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    )
    yield
    logger.info("Shutting down Generator Service")
    await http_client.aclose()


app = FastAPI(
    title="Generator Service",
    description="AI-powered resume generation service",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_http_client() -> httpx.AsyncClient:
    """Dependency to provide the shared HTTP client."""
    return http_client


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", service="generator-service")


@app.post("/generate/full", response_model=GenerateResponse)
async def generate_full_resume(
    request: FullGenerateRequest, client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Generate a complete resume from scratch based on user profile and job description.
    """
    logger.info(f"Full resume generation request for user {request.user_id}")
    try:
        top_k = request.top_k or int(os.getenv("DEFAULT_TOP_K", "7"))
        
        chunks = await retrieve_full_context(
            client, request.user_id, request.job_description, top_k
        )
        profile_context = format_context_for_prompt(chunks)
        
        prompt = FULL_RESUME_TEMPLATE.render(
            job_description=request.job_description, profile_context=profile_context
        )
        
        generated_text = await invoke_gemini(client, prompt)
        
        # FIX: Ensure the generated text is a valid JSON string before returning
        try:
            json.loads(generated_text)
        except json.JSONDecodeError:
            logger.error(f"LLM did not return valid JSON. Raw output: {generated_text}")
            raise LLMError("LLM failed to generate valid JSON output.")

        return GenerateResponse(
            generated_text=generated_text,
            raw_prompt=prompt,
            retrieval_mode="full",
        )
        
    except (httpx.HTTPError, LLMError) as e:
        logger.error(f"Downstream service error during full generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to process request due to a downstream service error: {e}",
        )
    except Exception as e:
        logger.error(f"Unexpected error in full generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal error occurred.",
        )


@app.post("/generate/section", response_model=GenerateResponse)
async def generate_section(
    request: SectionGenerateRequest, client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Generate or rewrite a specific section of a resume.
    """
    logger.info(f"Section generation for user {request.user_id}, section {request.section_id}")
    try:
        top_k = request.top_k or int(os.getenv("DEFAULT_TOP_K", "7"))
        
        chunks = await retrieve_section_context(
            client, request.user_id, request.section_id, request.job_description, top_k
        )
        relevant_context = format_context_for_prompt(chunks)
        
        prompt = SECTION_REWRITE_TEMPLATE.render(
            job_description=request.job_description,
            section_id=request.section_id,
            existing_text=request.existing_text or "",
            relevant_context=relevant_context,
        )
        
        generated_text = await invoke_gemini(client, prompt)

        try:
            json.loads(generated_text)
        except json.JSONDecodeError:
            logger.error(f"LLM did not return valid JSON. Raw output: {generated_text}")
            raise LLMError("LLM failed to generate valid JSON output.")

        return GenerateResponse(
            generated_text=generated_text,
            raw_prompt=prompt,
            retrieval_mode="section",
            section_id=request.section_id,
        )

    except (httpx.HTTPError, LLMError) as e:
        logger.error(f"Downstream service error during section generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to process request due to a downstream service error: {e}",
        )
    except Exception as e:
        logger.error(f"Unexpected error in section generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal error occurred.",
        )