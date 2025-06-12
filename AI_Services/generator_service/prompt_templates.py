# generator_service/schemas.py
"""
Pydantic models for API request/response schemas.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class FullGenerateRequest(BaseModel):
    """Request model for full resume generation."""
    user_id: str = Field(..., description="Unique identifier for the user")
    job_description: str = Field(..., description="Job description to tailor resume for")
    top_k: Optional[int] = Field(None, description="Number of top chunks to retrieve")


class SectionGenerateRequest(BaseModel):
    """Request model for section-specific resume generation."""
    user_id: str = Field(..., description="Unique identifier for the user")
    section_id: str = Field(..., description="ID of the section to generate/rewrite")
    job_description: str = Field(..., description="Job description to tailor section for")
    existing_text: Optional[str] = Field(None, description="Existing text to enhance/rewrite")
    top_k: Optional[int] = Field(None, description="Number of top chunks to retrieve")


class ChunkItem(BaseModel):
    """Model representing a retrieved context chunk from the Retrieval Service."""
    chunk_id: str = Field(..., description="Unique identifier for the chunk")
    user_id: str = Field(..., description="User who owns this chunk")
    index_namespace: str = Field(..., description="Namespace in the vector index")
    section_id: str = Field(..., description="Section this chunk belongs to")
    source_type: str = Field(..., description="Type of source (e.g., 'profile', 'section')")
    source_id: str = Field(..., description="ID of the source document")
    text: str = Field(..., description="The actual text content")
    score: float = Field(..., description="Relevance score from vector search")
    created_at: datetime = Field(..., description="When this chunk was created")


class GenerateResponse(BaseModel):
    """Response model for generation endpoints."""
    generated_text: str = Field(..., description="The AI-generated content")
    raw_prompt: str = Field(..., description="The full prompt sent to the LLM (for debugging)")
    retrieval_mode: str = Field(..., description="Mode used: 'full' or 'section'")
    section_id: Optional[str] = Field(None, description="Section ID for section-specific generation")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")


# generator_service/utils.py
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


# generator_service/prompt_templates.py
"""
Jinja2 templates for LLM prompt engineering.
"""
from jinja2 import Template

# Template for full resume generation
FULL_RESUME_TEMPLATE = Template("""
You are an expert resume writer with years of experience crafting compelling resumes that get interviews. Your task is to create a complete, professional resume based on the user's profile information and the specific job they're applying for.

JOB DESCRIPTION:
{{ job_description }}

RELEVANT CONTEXT FROM USER'S PROFILE:
{{ profile_context }}

INSTRUCTIONS:
1. Analyze the job description carefully to understand the key requirements, skills, and qualifications sought
2. Use the provided context to create a tailored resume that highlights the most relevant experience and skills
3. Write in a professional, action-oriented tone using strong action verbs
4. Quantify achievements where possible using the context provided
5. Ensure the resume is ATS-friendly and keyword-optimized for the target role
6. Structure the content logically and ensure it flows well

OUTPUT FORMAT:
Return your response as a valid JSON object with the following structure:
{
    "summary": "A compelling professional summary (2-3 sentences)",
    "experience": [
        "• First experience bullet point with quantified achievement",
        "• Second experience bullet point highlighting relevant skills",
        "• Continue with more relevant experience bullets..."
    ],
    "skills": [
        "Relevant technical skill 1",
        "Relevant technical skill 2",
        "Continue with more relevant skills..."
    ],
    "education": [
        "• Educational background bullet point",
        "• Additional education/certification if relevant"
    ],
    "achievements": [
        "• Notable achievement or project relevant to the role",
        "• Another significant accomplishment"
    ]
}

Ensure the JSON is properly formatted and contains only the generated content. Focus on making each section compelling and directly relevant to the target job.
""")

# Template for section-specific rewriting
SECTION_REWRITE_TEMPLATE = Template("""
You are an expert resume writer specializing in optimizing specific resume sections. Your task is to rewrite and enhance the "{{ section_id }}" section of a resume to better align with a specific job opportunity.

JOB DESCRIPTION:
{{ job_description }}

SECTION TO REWRITE: {{ section_id }}

{% if existing_text %}
CURRENT SECTION CONTENT:
{{ existing_text }}
{% endif %}

RELEVANT CONTEXT:
{{ relevant_context }}

INSTRUCTIONS:
1. Focus exclusively on the "{{ section_id }}" section
2. Analyze the job description to understand what employers are looking for in this specific section
3. Use the provided context and existing content to create an enhanced version
4. Ensure the rewritten section is:
   - Highly relevant to the target job
   - Uses appropriate keywords from the job description
   - Maintains professional tone and formatting
   - Quantifies achievements where possible
   - Uses strong action verbs and compelling language

{% if section_id == "experience" %}
5. For experience sections, focus on:
   - Leading with strong action verbs
   - Quantifying impact and results
   - Highlighting relevant technologies and methodologies
   - Demonstrating progression and growth
{% elif section_id == "skills" %}
5. For skills sections, focus on:
   - Prioritizing skills mentioned in the job description
   - Grouping related skills logically
   - Including both technical and soft skills as relevant
   - Avoiding outdated or irrelevant skills
{% elif section_id == "summary" %}
5. For summary sections, focus on:
   - Creating a compelling opening statement
   - Highlighting years of experience and key expertise
   - Mentioning 2-3 most relevant achievements
   - Aligning with the job title and requirements
{% endif %}

OUTPUT FORMAT:
Return your response as a valid JSON object with a single key matching the section name:
{
    "{{ section_id }}": [
        "• Enhanced bullet point 1 with relevant details",
        "• Enhanced bullet point 2 with quantified results",
        "• Continue with more enhanced content..."
    ]
}

If the section should be a string rather than a list (like summary), format it as:
{
    "{{ section_id }}": "Enhanced section content as a cohesive paragraph or statement"
}

Focus on quality over quantity - make every word count and ensure maximum relevance to the target role.
""")
