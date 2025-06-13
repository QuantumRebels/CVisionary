# suggestion_client.py

import os
import logging
import re
from typing import List
import httpx

logger = logging.getLogger(__name__)

def _build_suggestion_prompt(skills: str) -> str:
    """Builds the prompt for the Gemini API."""
    return f"""You are a helpful career coach. A candidate's resume is missing the following important skills required by a job description: {skills}.

Provide 3 concise and actionable suggestions on how they could better showcase these skills. For each suggestion, start with a verb. Frame them as advice.

Example response:
- Incorporate a project that utilized AWS S3 and Lambda to demonstrate cloud experience.
- Add 'Docker' and 'Kubernetes' to your skills section to pass automated screening.
- Detail your experience with REST API design in your previous role as a backend developer.
"""

def _parse_suggestions(response_text: str) -> List[str]:
    """Parses the bulleted list from the LLM's response."""
    if not response_text:
        return []
    
    # Find all lines starting with a bullet point or number
    suggestions = re.findall(r'^[•*-]\s*(.*)|^\d+\.\s*(.*)', response_text, re.MULTILINE)
    # The findall returns tuples, so we need to flatten and filter them
    cleaned_suggestions = [s[0] or s[1] for s in suggestions if (s[0] or s[1]).strip()]
    
    if not cleaned_suggestions and response_text.strip():
        # Fallback for non-bulleted text
        return [line.strip() for line in response_text.strip().split('\n') if line.strip()]

    return cleaned_suggestions[:3] # Return max 3 suggestions

async def generate_suggestions(client: httpx.AsyncClient, missing_keywords: List[str]) -> List[str]:
    """Generates resume improvement suggestions using the Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("Cannot generate suggestions: GEMINI_API_KEY is not configured.")
        return []
    if not missing_keywords:
        return []

    try:
        skills_text = ", ".join(missing_keywords[:5])
        prompt = _build_suggestion_prompt(skills_text)
        
        api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        
        response = await client.post(f"{api_url}?key={api_key}", json=payload, headers=headers)
        response.raise_for_status()
        
        response_data = response.json()
        generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        
        suggestions = _parse_suggestions(generated_text)
        logger.info(f"Generated {len(suggestions)} suggestions.")
        return suggestions

    except (KeyError, IndexError) as e:
        logger.error(f"Failed to parse Gemini response: {e}")
        return []
    except Exception as e:
        logger.error(f"Failed to generate suggestions: {e}")
        return []