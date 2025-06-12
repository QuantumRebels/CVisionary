# utils.py

"""
Utility functions for orchestrating calls to the Retrieval Service.
"""
import logging
import os
from typing import List
import httpx
from schemas import ChunkItem, RetrieveResponse

logger = logging.getLogger(__name__)


async def retrieve_full_context(
    client: httpx.AsyncClient, user_id: str, job_description: str, top_k: int
) -> List[ChunkItem]:
    """
    Retrieve full context from the Retrieval Service for complete resume generation.
    """
    # FIX: Use the correct default port for the Retrieval Service
    retrieval_url = os.getenv("RETRIEVAL_SERVICE_URL", "http://localhost:8000")
    endpoint = f"{retrieval_url.rstrip('/')}/retrieve/full"
    
    payload = {
        "user_id": user_id,
        "job_description": job_description,
        "top_k": top_k
    }
    
    logger.info(f"Retrieving full context for user {user_id} with top_k={top_k}")
    
    try:
        response = await client.post(endpoint, json=payload, timeout=30.0)
        response.raise_for_status()
        
        # Use the Pydantic model for robust parsing
        retrieved_data = RetrieveResponse(**response.json())
        chunks = retrieved_data.results
        
        logger.info(f"Successfully retrieved {len(chunks)} chunks for full context")
        return chunks
        
    except httpx.HTTPError as e:
        logger.error(f"Failed to retrieve full context: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during full context retrieval: {e}")
        raise


async def retrieve_section_context(
    client: httpx.AsyncClient, user_id: str, section_id: str, job_description: str, top_k: int
) -> List[ChunkItem]:
    """
    Retrieve section-specific context from the Retrieval Service.
    """
    # FIX: Use the correct default port for the Retrieval Service
    retrieval_url = os.getenv("RETRIEVAL_SERVICE_URL", "http://localhost:8000")
    endpoint = f"{retrieval_url.rstrip('/')}/retrieve/section"
    
    payload = {
        "user_id": user_id,
        "section_id": section_id,
        "job_description": job_description,
        "top_k": top_k
    }
    
    logger.info(f"Retrieving section context for user {user_id}, section {section_id}")
    
    try:
        response = await client.post(endpoint, json=payload, timeout=30.0)
        response.raise_for_status()
        
        retrieved_data = RetrieveResponse(**response.json())
        chunks = retrieved_data.results
        
        logger.info(f"Successfully retrieved {len(chunks)} chunks for section context")
        return chunks
        
    except httpx.HTTPError as e:
        logger.error(f"Failed to retrieve section context: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during section context retrieval: {e}")
        raise


def format_context_for_prompt(chunks: List[ChunkItem]) -> str:
    """
    Format retrieved chunks into a human-readable context string for the LLM.
    """
    if not chunks:
        return "No relevant context found."
    
    formatted_sections = []
    
    # FIX: Group chunks by the correct field: `index_namespace`
    profile_chunks = [c for c in chunks if c.index_namespace == "profile"]
    section_chunks = [c for c in chunks if c.index_namespace == "resume_sections"]
    
    if profile_chunks:
        formatted_sections.append("--- CONTEXT FROM PROFESSIONAL PROFILE ---")
        for chunk in profile_chunks:
            # FIX: Safely handle section_id which can be None
            source_label = f"Source: Profile section '{chunk.source_type}'"
            formatted_sections.append(source_label)
            formatted_sections.append(f"Content: {chunk.text.strip()}")
            formatted_sections.append("")
    
    if section_chunks:
        formatted_sections.append("--- CONTEXT FROM OTHER USER-EDITED SECTIONS ---")
        for chunk in section_chunks:
            source_label = f"Source: User-edited section '{chunk.section_id}'"
            formatted_sections.append(source_label)
            formatted_sections.append(f"Content: {chunk.text.strip()}")
            formatted_sections.append("")
    
    return "\n".join(formatted_sections).strip()