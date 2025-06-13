# orchestrator_service/tools.py

import json
import os
from typing import Optional, List
import httpx
from langchain.tools import tool
from pydantic import ValidationError

from memory import get_session_context, update_session_context
from schemas import ChunkItem, RetrieveResponse, GenerateResponse

# Corrected default ports
RETRIEVAL_SERVICE_URL = os.getenv("RETRIEVAL_SERVICE_URL", "http://retrieval-service:8000")
GENERATION_SERVICE_URL = os.getenv("GENERATION_SERVICE_URL", "http://generator-service:8000")

def format_context_for_prompt(chunks: List[ChunkItem]) -> str:
    """Formats retrieved chunks into a human-readable context string for the LLM."""
    if not chunks:
        return "No relevant context was found from the user's profile."
    
    formatted_strings = []
    for chunk in chunks:
        namespace = chunk.index_namespace
        source_type = chunk.source_type
        text = chunk.text.strip()
        if namespace == "profile":
            formatted_strings.append(f"- From Profile ({source_type}): {text}")
        elif namespace == "resume_sections":
            formatted_strings.append(f"- From another resume section ('{chunk.section_id}'): {text}")
    return "\n".join(formatted_strings)

class ToolBox:
    """A container for agent tools that shares the HTTP client."""
    def __init__(self, client: httpx.AsyncClient):
        self.http_client = client

        # Create tool objects from the internal, bound methods.
        # This correctly handles the 'self' argument for the tools.
        self.retrieve_context_tool = tool(self._retrieve_context_tool)
        self.generate_text_tool = tool(self._generate_text_tool)
        self.get_current_resume_section_tool = tool(self._get_current_resume_section_tool)
        self.update_resume_in_memory_tool = tool(self._update_resume_in_memory_tool)

    async def _retrieve_context_tool(self, session_id: str, section_id: Optional[str] = None) -> str:
        """Use this tool to get relevant context from the user's professional profile. If you are rewriting a specific section of the resume, you MUST provide the `section_id`."""
        context = get_session_context(session_id)
        if not context:
            return "Error: Session not found. The user must provide a user_id and job_description first."

        user_id = context["user_id"]
        job_description = context["job_description"]

        if section_id:
            endpoint = f"{RETRIEVAL_SERVICE_URL.rstrip('/')}/retrieve/section"
            payload = {"user_id": user_id, "job_description": job_description, "section_id": section_id}
        else:
            endpoint = f"{RETRIEVAL_SERVICE_URL.rstrip('/')}/retrieve/full"
            payload = {"user_id": user_id, "job_description": job_description}
        
        try:
            response = await self.http_client.post(endpoint, json=payload)
            response.raise_for_status()
            # Use Pydantic model for robust parsing and validation
            retrieved_data = RetrieveResponse(**response.json())
            return format_context_for_prompt(retrieved_data.results)
        except ValidationError as e:
            return f"Error: Retrieval service returned invalid data. Details: {e}"
        except Exception as e:
            return f"Error retrieving context: {str(e)}"

    async def _generate_text_tool(self, session_id: str, section_id: Optional[str] = None, existing_text: Optional[str] = None) -> str:
        """Use this tool to generate new resume text using an AI model. If you are rewriting a specific section, you MUST provide the `section_id` and the `existing_text` from the current resume."""
        context = get_session_context(session_id)
        if not context:
            return "Error: Session not found."

        user_id = context["user_id"]
        job_description = context["job_description"]

        if section_id:
            endpoint = f"{GENERATION_SERVICE_URL.rstrip('/')}/generate/section"
            payload = {"user_id": user_id, "job_description": job_description, "section_id": section_id, "existing_text": existing_text}
        else:
            endpoint = f"{GENERATION_SERVICE_URL.rstrip('/')}/generate/full"
            payload = {"user_id": user_id, "job_description": job_description}
        
        try:
            response = await self.http_client.post(endpoint, json=payload)
            response.raise_for_status()
            # Use Pydantic model for robust parsing
            result = GenerateResponse(**response.json())
            return result.generated_text
        except ValidationError as e:
            return f"Error: Generation service returned invalid data. Details: {e}"
        except Exception as e:
            return f"Error generating text: {str(e)}"

    def _get_current_resume_section_tool(self, session_id: str, section_id: str) -> str:
        """Use this tool to get the current text of a specific section of the resume you are working on. This is useful to get the `existing_text` before calling the `generate_text_tool`."""
        context = get_session_context(session_id)
        if not context:
            return "Error: Session not found."
        
        resume_state = context.get("resume_state", {})
        section_content = resume_state.get(section_id)
        
        if section_content:
            return json.dumps(section_content)
        return f"Section '{section_id}' is currently empty."

    def _update_resume_in_memory_tool(self, session_id: str, section_id: str, new_content_json: str) -> str:
        """After you have successfully generated new text for a section using `generate_text_tool`, you MUST use this tool to save the new text into the resume. The `new_content_json` argument must be the exact JSON string returned by the `generate_text_tool`."""
        context = get_session_context(session_id)
        if not context:
            return "Error: Session not found."
        
        try:
            new_content = json.loads(new_content_json)
            
            if section_id not in new_content and len(new_content) != 1:
                 return f"Error: The generated content JSON should contain a single key that matches the section_id '{section_id}'."
            
            # Handle cases where the key might be different but there's only one
            key_from_llm = list(new_content.keys())[0]
            context["resume_state"][section_id] = new_content[key_from_llm]
            
            update_session_context(session_id, context)
            
            return f"Successfully updated section '{section_id}' in the resume."
        except json.JSONDecodeError:
            return "Error: The provided `new_content_json` was not valid JSON."
        except Exception as e:
            return f"Error updating resume section: {str(e)}"