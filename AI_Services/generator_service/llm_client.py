# llm_client.py

"""
Client for interacting with the Google Gemini API.
"""
import logging
import os
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
        Generated text content from Gemini, expected to be a JSON string.
        
    Raises:
        LLMError: If the API call fails or response is malformed
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise LLMError("GEMINI_API_KEY environment variable is not set")
    
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    temperature = float(os.getenv("GENERATION_TEMPERATURE", "0.7"))
    max_tokens = int(os.getenv("GENERATION_MAX_TOKENS", "2048"))
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    # FIX: Request JSON output from the Gemini API
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
            "responseMimeType": "application/json",
        },
    }
    
    headers = {"Content-Type": "application/json"}
    
    logger.info(f"Invoking Gemini API with model {model}")
    
    try:
        response = await client.post(url, json=payload, headers=headers, timeout=60.0)
        response.raise_for_status()
        response_data = response.json()
        
        # Standard Gemini response parsing
        generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        
        logger.info("Successfully generated content from Gemini API")
        return generated_text.strip()
        
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        error_msg = f"Gemini API request failed: {e}"
        try:
            error_detail = e.response.json()
            error_msg += f" | Details: {error_detail}"
        except:
            pass
        logger.error(error_msg)
        raise LLMError(error_msg) from e
        
    except (KeyError, IndexError) as e:
        error_msg = f"Failed to parse Gemini response: {e}. Response: {response_data}"
        logger.error(error_msg)
        raise LLMError(error_msg) from e