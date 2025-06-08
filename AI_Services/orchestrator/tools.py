import os
import httpx
import logging
import json
from typing import Type, Dict, Any, List, Optional
from pydantic import BaseModel, Field, ValidationError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, RetryError

from langchain.tools import BaseTool
import google.generativeai as genai

# Assuming schemas.py is in the same directory
from .schemas import (
    EmbedRequest, EmbedResponse,
    RetrieveResponse,
    GenerateRequest, GenerateResponse,
    ScoreRequest, ScoreResponse,
    SuggestExternalResponse # SuggestExternalRequest is defined in this file for Gemini tool
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Environment Variables --- #
EMBEDDING_SERVICE_URL = os.getenv("EMBEDDING_SERVICE_URL")
GENERATION_SERVICE_URL = os.getenv("GENERATION_SERVICE_URL") # This service now also handles retrieval
SCORING_SERVICE_URL = os.getenv("SCORING_SERVICE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not all([EMBEDDING_SERVICE_URL, GENERATION_SERVICE_URL, SCORING_SERVICE_URL]):
    logger.warning("One or more critical service URLs (Embedding, Generator, Scoring) are not set. Tools may not function correctly.")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found. Suggestion tool will not work.")

# --- Retry Logic --- #
def async_retry_logic(attempts=2, wait_seconds=1):
    return retry(
        stop=stop_after_attempt(attempts),
        wait=wait_fixed(wait_seconds),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError, ValueError, json.JSONDecodeError)),
        reraise=True
    )

async def _make_async_http_request(method: str, url: str, json_payload: Optional[Dict] = None, params: Optional[Dict] = None, timeout: float = 10.0) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        try:
            logger.debug(f"Making {method} request to {url} with payload: {json_payload} and params: {params}")
            response = await client.request(method, url, json=json_payload, params=params, timeout=timeout)
            response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses
            return response.json()
        except httpx.HTTPStatusError as e:
            # Enhanced logging for HTTPStatusError
            error_message = f"HTTP error {e.response.status_code} for {method} {url}: {e.response.text}"
            logger.error(error_message)
            raise ValueError(f"Service call failed with status {e.response.status_code}. Details: {e.response.text}") from e
        except httpx.RequestError as e:
            logger.error(f"Request error for {method} {url}: {e}")
            raise ValueError(f"Service call failed due to a request error: {e}") from e
        except json.JSONDecodeError as e:
            # It's useful to see what was returned if it's not JSON
            raw_response_text = "<not available>"
            if 'response' in locals() and hasattr(response, 'text'):
                raw_response_text = response.text
            logger.error(f"Failed to decode JSON response from {method} {url}. Raw response: '{raw_response_text}'. Error: {e}")
            raise ValueError(f"Service call returned invalid JSON. Raw response: '{raw_response_text}'. Error: {e}") from e

# --- Tool Input Schemas (Pydantic models for LangChain tool arguments) --- #
class EmbedToolInput(BaseModel):
    job_description: str = Field(description="The job description text to embed.")

class RetrieveToolInput(BaseModel):
    user_id: str = Field(description="The user ID for whom to retrieve resume chunks.")
    # The agent's prompt will guide it to use the output of embed_tool (e.g., embedding_id or the embedding itself)
    # This input schema only defines what the tool *directly* accepts as arguments.
    # If the embedding_id needs to be passed, it should be part of the URL or query params handled by the tool logic.
    # For this example, we assume /retrieve/{user_id} and the embedding context is handled via agent memory or subsequent tool inputs.

class GenerateToolInput(BaseModel):
    user_id: str = Field(description="The user ID.")
    job_description: str = Field(description="The target job description text.")
    retrieved_chunks: Optional[List[str]] = Field(None, description="Relevant resume chunks retrieved by retrieve_tool.")

class ScoreToolInput(BaseModel):
    generated_bullets: List[str] = Field(description="Generated resume bullets from generate_tool.")
    job_description: str = Field(description="The target job description text.")

class SuggestToolInput(BaseModel):
    job_description: str = Field(description="The target job description text.")
    current_bullets: List[str] = Field(description="Current resume bullets that were scored.")
    match_score: float = Field(description="Current match score of the bullets (output of score_tool).")

# --- LangChain Tools --- #

class EmbeddingServiceTool(BaseTool):
    name = "embed_tool"
    description = "Calls the Embedding Service to get an embedding for a given text (e.g., job description). Input: job_description (str). Output: A dictionary containing 'embedding' (List[float]) and/or 'embedding_id' (str)."
    args_schema: Type[BaseModel] = EmbedToolInput

    @async_retry_logic()
    async def _arun(self, job_description: str) -> Dict[str, Any]:
        if not EMBEDDING_SERVICE_URL:
            raise ValueError("EMBEDDING_SERVICE_URL is not configured.")
        logger.info(f"EMBED_TOOL: Embedding job description (first 50 chars): {job_description[:50]}...")
        payload = EmbedRequest(text=job_description).model_dump()
        response_data = await _make_async_http_request("POST", EMBEDDING_SERVICE_URL, json_payload=payload)
        try:
            parsed_response = EmbedResponse(**response_data)
        except ValidationError as e:
            logger.error(f"EMBED_TOOL: Error validating response from Embedding Service: {e}. Data: {response_data}")
            raise ValueError(f"Invalid response structure from Embedding Service: {e}") from e
        logger.info(f"EMBED_TOOL: Successfully embedded. Embedding ID: {parsed_response.embedding_id}, Dim: {len(parsed_response.embedding) if parsed_response.embedding else 'N/A'}")
        return parsed_response.model_dump()

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("This tool does not support synchronous execution.")

class RetrievalServiceTool(BaseTool):
    name = "retrieve_tool"
    description = "Calls the Generator Service's retrieval endpoint to get relevant resume chunks for a user. Input: user_id (str). The job description context (e.g., embedding_id from embed_tool) might be passed as a query parameter if the service supports it. Output: A dictionary containing 'chunks' (List[str])."
    args_schema: Type[BaseModel] = RetrieveToolInput

    @async_retry_logic()
    async def _arun(self, user_id: str, **kwargs: Any) -> Dict[str, Any]: # kwargs can capture jd_embedding_id
        if not GENERATION_SERVICE_URL:
            raise ValueError("GENERATION_SERVICE_URL (for retrieval) is not configured.")
        logger.info(f"RETRIEVE_TOOL: Retrieving chunks for user_id: {user_id} via Generator Service.")
        
        # Assuming GENERATOR_SERVICE_URL is the base (e.g., http://localhost:8001/)
        # and retrieval is at a subpath like /retrieve/{user_id}
        # If GENERATOR_SERVICE_URL already includes a path, adjust accordingly.
        base_url = GENERATION_SERVICE_URL.rstrip('/')
        # It's safer to ensure there's one slash, not zero or two.
        if not base_url.endswith('/'):
            base_url += '/'
        # Construct the specific retrieval endpoint. This assumes a convention.
        # The user mentioned 'generator_service is responsible for both retrieval and generation'.
        # We need to assume an endpoint structure here, e.g., /retrieve on the generator service.
        url = f"{base_url}retrieve/{user_id}" 

        query_params = {}
        if 'jd_embedding_id' in kwargs and kwargs['jd_embedding_id']:
             query_params['jd_embedding_id'] = kwargs['jd_embedding_id']
        
        response_data = await _make_async_http_request("GET", url, params=query_params if query_params else None)
        try:
            parsed_response = RetrieveResponse(**response_data)
        except ValidationError as e:
            logger.error(f"RETRIEVE_TOOL: Error validating response from Generator Service (retrieval endpoint): {e}. Data: {response_data}")
            raise ValueError(f"Invalid response structure from Generator Service (retrieval): {e}") from e
        if not parsed_response.chunks:
            logger.warning(f"RETRIEVE_TOOL: No chunks retrieved for user_id {user_id}. This might be expected or an issue.")
        logger.info(f"RETRIEVE_TOOL: Successfully retrieved {len(parsed_response.chunks)} chunks.")
        return parsed_response.model_dump()

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("This tool does not support synchronous execution.")

class GenerationServiceTool(BaseTool):
    name = "generate_tool"
    description = "Calls the Generator Service's generation endpoint to create tailored resume bullets. Input: user_id (str), job_description (str), and optionally retrieved_chunks (List[str]). Output: A dictionary containing 'bullets' (List[str]) and optionally 'raw_prompt'."
    args_schema: Type[BaseModel] = GenerateToolInput # Uses GenerateToolInput for agent interaction

    @async_retry_logic()
    async def _arun(self, user_id: str, job_description: str, retrieved_chunks: Optional[List[str]] = None) -> Dict[str, Any]:
        if not GENERATION_SERVICE_URL:
            raise ValueError("GENERATION_SERVICE_URL is not configured.")
        
        num_chunks = len(retrieved_chunks) if retrieved_chunks else 0
        logger.info(f"GENERATE_TOOL: Generating bullets for user_id: {user_id} using job_description. {num_chunks} retrieved_chunks provided.")

        if retrieved_chunks:
            logger.warning("GENERATE_TOOL: 'retrieved_chunks' were provided to the tool, but the current Generator Service API (POST /generate/{user_id} with {'job_description': ...}) does not directly accept them. They will be ignored in the direct API call.")

        # Payload for the actual service call, as per GenerateServiceRequest
        service_payload = GenerateRequest(job_description=job_description).model_dump()

        # URL: POST /generate/{user_id}
        base_url = GENERATION_SERVICE_URL.rstrip('/')
        if not base_url.endswith('/'):
            base_url += '/'
        url = f"{base_url}generate/{user_id}" 

        response_data = await _make_async_http_request("POST", url, json_payload=service_payload)
        try:
            parsed_response = GenerateResponse(**response_data)
        except ValidationError as e:
            logger.error(f"GENERATE_TOOL: Error validating response from Generation Service: {e}. Data: {response_data}")
            raise ValueError(f"Invalid response structure from Generation Service: {e}") from e
        if not parsed_response.bullets:
            logger.warning(f"GENERATE_TOOL: No bullets generated for user_id {user_id}.")
        logger.info(f"GENERATE_TOOL: Successfully generated {len(parsed_response.bullets)} bullets.")
        return parsed_response.model_dump()

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("This tool does not support synchronous execution.")

class ScoringServiceTool(BaseTool):
    name = "score_tool"
    description = "Calls the Scoring Service to evaluate generated resume bullets against a job description. Input: generated_bullets (List[str]), job_description (str). Output: A dictionary containing 'score' (float), and optionally 'missing_keywords' and 'suggestions'."
    args_schema: Type[BaseModel] = ScoreToolInput # Agent uses this for input

    @async_retry_logic()
    async def _arun(self, generated_bullets: List[str], job_description: str) -> Dict[str, Any]:
        if not SCORING_SERVICE_URL:
            raise ValueError("SCORING_SERVICE_URL is not configured.")
        if not generated_bullets:
            logger.warning("SCORE_TOOL: No generated bullets provided. Returning a score of 0.0 and no suggestions.")
            return ScoreResponse(score=0.0, missing_keywords=[], suggestions=[]).model_dump()

        logger.info(f"SCORE_TOOL: Scoring {len(generated_bullets)} bullets against job description.")
        
        # Format payload for the scoring service: {"job_description": "...", "resume_text": "..."}
        resume_text = "\n".join(generated_bullets)
        service_payload = {
            "job_description": job_description,
            "resume_text": resume_text
        }

        # Assuming SCORING_SERVICE_URL is the full path to the score endpoint (e.g., http://localhost:8003/score)
        url = SCORING_SERVICE_URL 
        response_data = await _make_async_http_request("POST", url, json_payload=service_payload)
        try:
            # Use Pydantic's populate_by_name to handle 'score' or 'match_score' from response
            parsed_response = ScoreResponse.model_validate(response_data)
        except ValidationError as e:
            logger.error(f"SCORE_TOOL: Error validating response from Scoring Service: {e}. Data: {response_data}")
            raise ValueError(f"Invalid response structure from Scoring Service: {e}") from e
        logger.info(f"SCORE_TOOL: Successfully scored bullets. Score: {parsed_response.score}, Missing Keywords: {parsed_response.missing_keywords}, Suggestions: {parsed_response.suggestions}")
        return parsed_response.model_dump(by_alias=True) # Ensure 'match_score' is used if aliased

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("This tool does not support synchronous execution.")

class GeminiSuggestTool(BaseTool):
    name = "suggest_tool"
    description = "Calls Gemini to generate improvement suggestions for resume bullets if the match score is low. Input: job_description (str), current_bullets (List[str]), match_score (float). Output: A dictionary containing 'suggestions' (List[str])."
    args_schema: Type[BaseModel] = SuggestToolInput

    @async_retry_logic(attempts=2, wait_seconds=3) # Gemini might need slightly more robust retry
    async def _arun(self, job_description: str, current_bullets: List[str], match_score: float) -> Dict[str, Any]:
        logger.info(f"SUGGEST_TOOL: Generating suggestions. Current score: {match_score}.")
        if not GEMINI_API_KEY:
            logger.warning("Gemini API key not configured. Skipping suggestions.")
            return SuggestExternalResponse(suggestions=[]).model_dump()
        
        try:
            # Check if model is available - genai.get_model might not exist or work this way for all versions.
            # It's safer to just try creating the model instance.
            model = genai.GenerativeModel('gemini-1.5-flash-latest') # Or 'gemini-pro'
        except Exception as e:
            logger.error(f"SUGGEST_TOOL: Could not initialize Gemini model: {e}. Ensure API key is valid and model name is correct.")
            return SuggestExternalResponse(suggestions=[]).model_dump()

        bullet_str = "\n- ".join(current_bullets)
        prompt = (
            f"The following resume bullets were generated for the job description below:\n\n"
            f"Job Description:\n{job_description}\n\n"
            f"Current Resume Bullets (achieved a match score of {match_score*100:.1f}%):\n- {bullet_str}\n\n"
            f"The match score is {match_score*100:.1f}%. Please provide 2-3 concise, actionable suggestions to improve these bullets to better match the job description. "
            f"Focus on specific changes, additions, or rephrasing. Frame suggestions as direct advice for editing the bullets."
            f"Output ONLY a valid JSON list of strings, where each string is a suggestion. For example: [\"Rephrase the first bullet to include X skill mentioned in the JD.\", \"Add a quantifiable result to the bullet about project Y.\"]."
        )
        
        try:
            response = await model.generate_content_async(prompt)
            raw_text = response.text
            logger.debug(f"SUGGEST_TOOL: Raw Gemini response: {raw_text}")
            
            # Attempt to parse the response as a JSON list of strings
            try:
                # Try to find JSON list within the text, robustly
                json_start = raw_text.find('[')
                json_end = raw_text.rfind(']')
                if json_start != -1 and json_end != -1 and json_end > json_start:
                    json_str = raw_text[json_start : json_end+1]
                    suggestions_list = json.loads(json_str)
                    if not isinstance(suggestions_list, list) or not all(isinstance(s, str) for s in suggestions_list):
                        raise ValueError("Parsed JSON is not a list of strings.")
                    suggestions = suggestions_list
                else:
                    raise ValueError("No JSON array found in Gemini response.")
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"SUGGEST_TOOL: Could not parse Gemini response as JSON list: '{raw_text}'. Error: {e}. Falling back to line splitting.")
                # Fallback: split by newline, filter, and clean
                suggestions = [s.strip().lstrip('-').strip() for s in raw_text.split('\n') if s.strip() and len(s.strip()) > 10]
                if not suggestions and raw_text.strip(): # If still no suggestions, take the whole text as one
                    suggestions = [raw_text.strip()]

        except Exception as e:
            logger.error(f"SUGGEST_TOOL: Error calling Gemini API or processing response: {e}")
            # Reraise to be caught by tenacity for retry, or fail the tool run
            raise ValueError(f"Gemini API call failed: {e}") from e

        if not suggestions:
            logger.warning("SUGGEST_TOOL: Gemini returned no suggestions or suggestions could not be parsed.")
            return SuggestExternalResponse(suggestions=[]).model_dump()

        logger.info(f"SUGGEST_TOOL: Successfully generated {len(suggestions)} suggestions.")
        return SuggestExternalResponse(suggestions=suggestions).model_dump()

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("This tool does not support synchronous execution.")

def get_all_tools() -> List[BaseTool]:
    tools = [
        EmbeddingServiceTool(), 
        RetrievalServiceTool(), 
        GenerationServiceTool(), 
        ScoringServiceTool(), 
        GeminiSuggestTool()
    ]
    # Verify all tools have necessary URLs if they are HTTP based (except Gemini which uses SDK)
    if not EMBEDDING_SERVICE_URL: logger.error("EmbeddingServiceTool disabled: EMBEDDING_SERVICE_URL not set.")
    # GENERATION_SERVICE_URL is used by both RetrievalServiceTool (for its /retrieve endpoint) and GenerationServiceTool
    if not GENERATION_SERVICE_URL: 
        logger.error("RetrievalServiceTool disabled: GENERATION_SERVICE_URL not set (used for retrieval path).")
        logger.error("GenerationServiceTool disabled: GENERATION_SERVICE_URL not set.")
    if not SCORING_SERVICE_URL: logger.error("ScoringServiceTool disabled: SCORING_SERVICE_URL not set.")
    if not GEMINI_API_KEY: logger.warning("GeminiSuggestTool may not function: GEMINI_API_KEY not set.")
    return tools

# Example of how a tool might be called (for local testing, not part of the class)
async def _test_tool_example():
    # This requires running services and environment variables set.
    # For example, to test the embed tool:
    # os.environ["EMBEDDING_SERVICE_URL"] = "http://localhost:8000/embed" # Your actual service URL
    # embed_tool = EmbeddingServiceTool()
    # try:
    #     result = await embed_tool._arun(job_description="Software engineer with Python and AWS experience.")
    #     print("Test EmbedTool result:", result)
    # except Exception as e:
    #     print(f"Test EmbedTool failed: {e}")
    pass

if __name__ == '__main__':
    # To test a tool, you would need to run an asyncio event loop
    # and have the dependent services running with env vars set.
    # import asyncio
    # asyncio.run(_test_tool_example())
    pass
