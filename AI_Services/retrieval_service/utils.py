# utils.py

"""
CVisionary Retrieval Service - Utility Functions

This module provides HTTP client utilities for interfacing with the Embedding Service.
Handles embedding generation, profile chunk retrieval, and section-specific retrieval
with comprehensive error handling and retry logic.
"""

import asyncio
import logging
import os
import time
from typing import List, Dict, Any, Optional

import httpx
from fastapi import HTTPException

from schemas import ChunkItem

# Configure logger
logger = logging.getLogger(__name__)

# Retry configuration
RETRY_DELAY = 1.0  # seconds
MAX_RETRIES = 1


async def embed_text(client: httpx.AsyncClient, job_description: str) -> List[float]:
    """
    Generate embedding vector for job description text via Embedding Service.
    """
    embedding_service_url = os.getenv("EMBEDDING_SERVICE_URL")
    if not embedding_service_url:
        raise HTTPException(status_code=500, detail="Embedding service URL not configured")

    url = f"{embedding_service_url.rstrip('/')}/embed"
    payload = {"text": job_description}
    logger.debug(f"[RETRIEVAL] embed_text: POST {url}")

    try:
        response = await _make_request_with_retry(client, "POST", url, json=payload)
        if "embedding" not in response:
            raise HTTPException(status_code=502, detail="Invalid response format from embedding service")
        return response["embedding"]
    except Exception as e:
        logger.error(f"[RETRIEVAL] embed_text failed: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Failed to generate embedding: {e}")


async def retrieve_profile_chunks(
    client: httpx.AsyncClient, user_id: str, embedding: List[float], top_k: int
) -> List[ChunkItem]:
    """
    Retrieve relevant profile chunks for full resume context.
    """
    embedding_service_url = os.getenv("EMBEDDING_SERVICE_URL")
    if not embedding_service_url:
        raise HTTPException(status_code=500, detail="Embedding service URL not configured")

    url = f"{embedding_service_url.rstrip('/')}/retrieve/{user_id}"
    # FIX: Be explicit about the namespace for robustness
    payload = {
        "query_embedding": embedding,
        "top_k": top_k,
        "index_namespace": "profile",
    }
    logger.debug(f"[RETRIEVAL] retrieve_profile_chunks: POST {url}")

    try:
        response = await _make_request_with_retry(client, "POST", url, json=payload)
        return _parse_chunks_response(response, user_id)
    except Exception as e:
        logger.error(f"[RETRIEVAL] retrieve_profile_chunks failed: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Failed to retrieve profile chunks: {e}")


async def retrieve_section_chunks(
    client: httpx.AsyncClient,
    user_id: str,
    section_id: str,
    embedding: List[float],
    top_k: int,
) -> List[ChunkItem]:
    """
    Retrieve relevant chunks for specific resume section editing.
    """
    embedding_service_url = os.getenv("EMBEDDING_SERVICE_URL")
    if not embedding_service_url:
        raise HTTPException(status_code=500, detail="Embedding service URL not configured")

    url = f"{embedding_service_url.rstrip('/')}/retrieve/{user_id}"
    # FIX: Use the correct payload structure for section filtering
    payload = {
        "query_embedding": embedding,
        "top_k": top_k,
        "index_namespace": "resume_sections",
        "filter_by_section_ids": [section_id],
    }
    logger.debug(f"[RETRIEVAL] retrieve_section_chunks: POST {url}")

    try:
        response = await _make_request_with_retry(client, "POST", url, json=payload)
        return _parse_chunks_response(response, user_id, section_id)
    except Exception as e:
        logger.error(f"[RETRIEVAL] retrieve_section_chunks failed: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Failed to retrieve section chunks: {e}")


async def _make_request_with_retry(
    client: httpx.AsyncClient, method: str, url: str, **kwargs
) -> Dict[str, Any]:
    """
    Make HTTP request with retry logic for transient failures.
    """
    last_exception = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            if attempt > 0:
                logger.debug(f"[RETRIEVAL] Retry attempt {attempt} for {method} {url}")
                await asyncio.sleep(RETRY_DELAY)

            response = await client.request(method, url, **kwargs)
            response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses
            return response.json()

        except httpx.HTTPStatusError as e:
            # Handle specific status codes
            if e.response.status_code == 404:
                error_detail = "User not found or no chunks available"
                raise HTTPException(status_code=404, detail=error_detail) from e
            elif e.response.status_code >= 500:
                # Server errors are retry-eligible
                error_msg = f"Embedding service server error: {e.response.status_code}"
                logger.warning(f"[RETRIEVAL] Server error (attempt {attempt + 1}): {error_msg}")
                last_exception = HTTPException(status_code=502, detail=error_msg)
                continue
            else:
                # Other client errors (4xx) are not retried
                error_msg = f"Embedding service client error: {e.response.text}"
                raise HTTPException(status_code=502, detail=error_msg) from e

        except (httpx.TimeoutException, httpx.ConnectError) as e:
            error_msg = f"Network error connecting to embedding service: {type(e).__name__}"
            logger.warning(f"[RETRIEVAL] Network error (attempt {attempt + 1}): {error_msg}")
            last_exception = HTTPException(status_code=502, detail=error_msg)
            continue

    raise last_exception or HTTPException(status_code=502, detail="Failed to connect to embedding service after retries")


def _parse_chunks_response(
    response: Dict[str, Any], user_id: str, section_id: Optional[str] = None
) -> List[ChunkItem]:
    """
    Parse chunks response from Embedding Service into ChunkItem objects.
    """
    if "results" not in response or not isinstance(response["results"], list):
        raise HTTPException(status_code=502, detail="Invalid response format from embedding service: missing 'results' list")

    chunks = []
    for chunk_data in response["results"]:
        try:
            chunk = ChunkItem(**chunk_data)
            if chunk.user_id != user_id:
                logger.warning(f"[RETRIEVAL] User ID mismatch: expected {user_id}, got {chunk.user_id}")
                continue
            chunks.append(chunk)
        except Exception as e:
            logger.warning(f"[RETRIEVAL] Failed to parse chunk: {e}. Data: {chunk_data}")
            continue

    logger.debug(f"[RETRIEVAL] Parsed {len(chunks)} valid chunks from {len(response['results'])} total")
    return chunks