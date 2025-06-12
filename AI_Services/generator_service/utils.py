"""
Utility functions for orchestrating calls to the Retrieval Service.
"""
import logging
from typing import List
import httpx
from .schemas import ChunkItem

logger = logging.getLogger(__name__)


async def retrieve_full_context(
    client: httpx.AsyncClient, 
    user_id: str, 
    job_description: str, 
    top_k: int
) -> List[ChunkItem]:
    """
    Retrieve full context from the Retrieval Service for complete resume generation.
    
    Args:
        client: Shared HTTP client
        user_id: User identifier
        job_description: Job description for context matching
        top_k: Number of top chunks to retrieve
        
    Returns:
        List of ChunkItem objects containing relevant context
        
    Raises:
        httpx.HTTPError: If the retrieval service call fails
    """
    import os
    
    retrieval_url = os.getenv("RETRIEVAL_SERVICE_URL", "http://localhost:8001")
    endpoint = f"{retrieval_url}/retrieve/full"
    
    payload = {
        "user_id": user_id,
        "job_description": job_description,
        "top_k": top_k
    }
    
    logger.info(f"Retrieving full context for user {user_id} with top_k={top_k}")
    
    try:
        response = await client.post(endpoint, json=payload)
        response.raise_for_status()
        
        chunks_data = response.json()
        chunks = [ChunkItem(**chunk) for chunk in chunks_data]
        
        logger.info(f"Successfully retrieved {len(chunks)} chunks for full context")
        return chunks
        
    except httpx.HTTPError as e:
        logger.error(f"Failed to retrieve full context: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during full context retrieval: {e}")
        raise


async def retrieve_section_context(
    client: httpx.AsyncClient,
    user_id: str,
    section_id: str,
    job_description: str,
    top_k: int
) -> List[ChunkItem]:
    """
    Retrieve section-specific context from the Retrieval Service.
    
    Args:
        client: Shared HTTP client
        user_id: User identifier
        section_id: ID of the specific section
        job_description: Job description for context matching
        top_k: Number of top chunks to retrieve
        
    Returns:
        List of ChunkItem objects containing relevant context
        
    Raises:
        httpx.HTTPError: If the retrieval service call fails
    """
    import os
    
    retrieval_url = os.getenv("RETRIEVAL_SERVICE_URL", "http://localhost:8001")
    endpoint = f"{retrieval_url}/retrieve/section"
    
    payload = {
        "user_id": user_id,
        "section_id": section_id,
        "job_description": job_description,
        "top_k": top_k
    }
    
    logger.info(f"Retrieving section context for user {user_id}, section {section_id}")
    
    try:
        response = await client.post(endpoint, json=payload)
        response.raise_for_status()
        
        chunks_data = response.json()
        chunks = [ChunkItem(**chunk) for chunk in chunks_data]
        
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
    
    Args:
        chunks: List of ChunkItem objects from retrieval service
        
    Returns:
        Formatted context string ready for inclusion in prompts
    """
    if not chunks:
        return "No relevant context found."
    
    formatted_sections = []
    
    # Group chunks by source type for better organization
    profile_chunks = [c for c in chunks if c.source_type == "profile"]
    section_chunks = [c for c in chunks if c.source_type == "section"]
    
    # Format profile chunks
    if profile_chunks:
        formatted_sections.append("--- CONTEXT FROM PROFESSIONAL PROFILE ---")
        for i, chunk in enumerate(profile_chunks, 1):
            source_label = f"Experience #{i}" if "experience" in chunk.section_id.lower() else f"Profile Section: {chunk.section_id}"
            formatted_sections.append(f"Source: {source_label}")
            formatted_sections.append(f"Content: {chunk.text.strip()}")
            formatted_sections.append("")  # Empty line for readability
    
    # Format section chunks
    if section_chunks:
        for chunk in section_chunks:
            formatted_sections.append(f"--- CONTEXT FROM USER-EDITED SECTION ({chunk.section_id}) ---")
            formatted_sections.append(f"Source: Section '{chunk.section_id}'")
            formatted_sections.append(f"Content: {chunk.text.strip()}")
            formatted_sections.append("")  # Empty line for readability
    
    return "\n".join(formatted_sections).strip()