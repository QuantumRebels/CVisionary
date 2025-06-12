"""
Client for interacting with the Google Gemini API.
"""
import json
import logging
import os
from typing import Any, Dict
import httpx

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    pass


async def invoke_gemini(client: httpx.AsyncClient, prompt: str) -> str:
    """
    Invoke the Google Gemini API with the given prompt.
    
    Args:
        client: Shared HTTP client for making requests
        prompt: The prompt to send to the Gemini API
        
    Returns:
        Generated text content from Gemini
        
    Raises:
        LLMError: If the API call fails or response is malformed
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise LLMError("GEMINI_API_KEY environment variable is not set")
    
    # Gemini API configuration
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "2048"))
    
    # Construct the Gemini API URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    # Prepare the request payload
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
            "responseMimeType": "text/plain"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    logger.info(f"Invoking Gemini API with model {model}")
    
    try:
        response = await client.post(
            url,
            json=payload,
            headers=headers,
            timeout=30.0
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        # Parse the Gemini response format
        if "candidates" not in response_data:
            raise LLMError("Invalid response format: missing 'candidates' field")
        
        candidates = response_data["candidates"]
        if not candidates:
            raise LLMError("No candidates returned from Gemini API")
        
        candidate = candidates[0]
        if "content" not in candidate:
            raise LLMError("Invalid candidate format: missing 'content' field")
        
        content = candidate["content"]
        if "parts" not in content:
            raise LLMError("Invalid content format: missing 'parts' field")
        
        parts = content["parts"]
        if not parts:
            raise LLMError("No parts returned in content")
        
        # Extract the generated text
        generated_text = parts[0].get("text", "")
        if not generated_text:
            raise LLMError("Empty text returned from Gemini API")
        
        logger.info("Successfully generated content from Gemini API")
        return generated_text.strip()
        
    except httpx.HTTPStatusError as e:
        error_msg = f"Gemini API returned status {e.response.status_code}"
        try:
            error_detail = e.response.json()
            error_msg += f": {error_detail}"
        except:
            error_msg += f": {e.response.text}"
        
        logger.error(f"Gemini API error: {error_msg}")
        raise LLMError(error_msg)
        
    except httpx.RequestError as e:
        error_msg = f"Failed to connect to Gemini API: {e}"
        logger.error(error_msg)
        raise LLMError(error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error calling Gemini API: {e}"
        logger.error(error_msg)
        raise LLMError(error_msg)