import os
import logging
import re
from typing import List
import httpx

logger = logging.getLogger(__name__)

def _build_suggestion_prompt(skills: str) -> str:
    return f"""You are a helpful career coach. A candidate's resume is missing the following important skills: {skills}.
Provide 3 concise, actionable suggestions on how they could better showcase these skills. For each suggestion, start with a verb.
Example response:
- Incorporate a project that utilized AWS S3.
- Add 'Docker' to your skills section.
"""

def _parse_suggestions(response_text: str) -> List[str]:
    if not response_text:
        return []
    suggestions = re.findall(r'^[•*-]\s*(.*)|^\d+\.\s*(.*)', response_text, re.MULTILINE)
    cleaned_suggestions = [s[0] or s[1] for s in suggestions if (s[0] or s[1]).strip()]
    if not cleaned_suggestions and response_text.strip():
        return [line.strip() for line in response_text.strip().split('\n') if line.strip()]
    return cleaned_suggestions[:3]

async def generate_suggestions(client: httpx.AsyncClient, missing_keywords: List[str]) -> List[str]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not missing_keywords:
        return []
    try:
        prompt = _build_suggestion_prompt(", ".join(missing_keywords[:5]))
        api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        response = await client.post(f"{api_url}?key={api_key}", json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        return _parse_suggestions(generated_text)
    except Exception as e:
        logger.error(f"Failed to generate suggestions: {e}")
        return []