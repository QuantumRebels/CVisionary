# app.py

"""
CVisionary Retrieval Service - FastAPI Application

This service provides context retrieval for resume generation and editing by
interfacing with the enhanced Embedding Service. It supports two main modes:

1. Full resume context - retrieves top-K profile chunks most relevant to job description
2. Section edit context - retrieves chunks specific to a resume section

The service acts as an intermediary between the Generation Service and the
Embedding Service, handling HTTP orchestration and response formatting.

Environment Variables:
- EMBEDDING_SERVICE_URL: Base URL of the Embedding Service (required)
- DEFAULT_TOP_K: Default number of chunks to retrieve (optional, default: 5)
- LOG_LEVEL: Logging level INFO or DEBUG (optional, default: INFO)
"""

import logging
import os
import time
from typing import Dict, Any

import httpx
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from schemas import (
    FullRetrieveRequest,
    SectionRetrieveRequest,
    RetrieveResponse,
    HealthResponse,
)
from utils import embed_text, retrieve_profile_chunks, retrieve_section_chunks

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# App state to hold the shared httpx client
app_state: Dict[str, Any] = {}

# Initialize FastAPI application
app = FastAPI(
    title="CVisionary Retrieval Service",
    description="Context retrieval service for resume generation and editing",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Validate configuration, create a shared HTTP client, and test connectivity.
    """
    logger.info("[RETRIEVAL] Starting CVisionary Retrieval Service")

    # Validate required environment variables
    embedding_service_url = os.getenv("EMBEDDING_SERVICE_URL")
    if not embedding_service_url:
        logger.error(
            "[RETRIEVAL] EMBEDDING_SERVICE_URL environment variable is required"
        )
        raise RuntimeError("EMBEDDING_SERVICE_URL environment variable is required")

    # Validate optional configuration
    default_top_k = os.getenv("DEFAULT_TOP_K", "5")
    try:
        default_top_k_int = int(default_top_k)
        if default_top_k_int < 1 or default_top_k_int > 50:
            raise ValueError("DEFAULT_TOP_K must be between 1 and 50")
    except ValueError as e:
        logger.error(f"[RETRIEVAL] Invalid DEFAULT_TOP_K value '{default_top_k}': {e}")
        raise RuntimeError(f"Invalid DEFAULT_TOP_K value: {e}")

    # Create and store a single, shared httpx.AsyncClient instance
    app_state["http_client"] = httpx.AsyncClient(timeout=30.0)

    # Test connectivity to Embedding Service
    try:
        health_url = f"{embedding_service_url.rstrip('/')}/health"
        response = await app_state["http_client"].get(health_url)
        if response.status_code == 200:
            logger.info(
                f"[RETRIEVAL] Successfully connected to Embedding Service at {embedding_service_url}"
            )
        else:
            logger.warning(
                f"[RETRIEVAL] Embedding Service health check returned {response.status_code}"
            )
    except Exception as e:
        logger.warning(f"[RETRIEVAL] Could not connect to Embedding Service: {e}")

    logger.info("[RETRIEVAL] Service startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanly close the shared HTTP client.
    """
    logger.info("[RETRIEVAL] Shutting down Retrieval Service")
    client: httpx.AsyncClient = app_state.get("http_client")
    if client:
        await client.aclose()
    logger.info("[RETRIEVAL] Shutdown complete")


# --- Dependency ---
async def get_http_client() -> httpx.AsyncClient:
    """Dependency to provide the shared httpx.AsyncClient."""
    return app_state["http_client"]


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and response times."""
    start_time = time.time()
    logger.info(f"[RETRIEVAL] {request.method} {request.url.path} - Request received")
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"[RETRIEVAL] {request.method} {request.url.path} - "
        f"Response {response.status_code} in {duration:.2f}s"
    )
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler for structured error responses."""
    logger.error(
        f"[RETRIEVAL] HTTP Exception: {exc.status_code} - {exc.detail} "
        f"for {request.method} {request.url.path}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(
        f"[RETRIEVAL] Unexpected error: {str(exc)} "
        f"for {request.method} {request.url.path}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url.path),
        },
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for service monitoring."""
    return HealthResponse(status="ok", service="retrieval")


@app.post("/retrieve/full", response_model=RetrieveResponse)
async def retrieve_full_context(
    request: FullRetrieveRequest, client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Retrieve relevant profile chunks for full resume generation.
    """
    logger.info(
        f"[RETRIEVAL] Full context retrieval: user_id={request.user_id}, "
        f"job_desc_len={len(request.job_description)}, top_k={request.top_k}"
    )
    try:
        if not request.user_id.strip() or not request.job_description.strip():
            raise HTTPException(status_code=400, detail="user_id and job_description cannot be empty")

        embedding = await embed_text(client, request.job_description)
        chunks = await retrieve_profile_chunks(
            client, user_id=request.user_id, embedding=embedding, top_k=request.top_k
        )
        logger.info(
            f"[RETRIEVAL] Full context retrieval complete: "
            f"user_id={request.user_id}, retrieved {len(chunks)} chunks"
        )
        return RetrieveResponse(results=chunks)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"[RETRIEVAL] Full context retrieval failed: {str(e)}", exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve full context")


@app.post("/retrieve/section", response_model=RetrieveResponse)
async def retrieve_section_context(
    request: SectionRetrieveRequest, client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Retrieve relevant profile chunks for specific resume section editing.
    """
    logger.info(
        f"[RETRIEVAL] Section context retrieval: user_id={request.user_id}, "
        f"section_id={request.section_id}, top_k={request.top_k}"
    )
    try:
        if not all([s.strip() for s in [request.user_id, request.section_id, request.job_description]]):
            raise HTTPException(status_code=400, detail="user_id, section_id, and job_description cannot be empty")

        embedding = await embed_text(client, request.job_description)
        chunks = await retrieve_section_chunks(
            client,
            user_id=request.user_id,
            section_id=request.section_id,
            embedding=embedding,
            top_k=request.top_k,
        )
        logger.info(
            f"[RETRIEVAL] Section context retrieval complete: "
            f"user_id={request.user_id}, section_id={request.section_id}, "
            f"retrieved {len(chunks)} chunks"
        )
        return RetrieveResponse(results=chunks)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"[RETRIEVAL] Section context retrieval failed: {str(e)}", exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve section context")


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "CVisionary Retrieval Service",
        "version": "1.1.0",
        "description": "Context retrieval service for resume generation and editing",
    }