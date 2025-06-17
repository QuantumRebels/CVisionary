# orchestrator/tools.py

import json
import os
from typing import Optional, List
import httpx
from langchain.tools import tool
from pydantic import ValidationError

from .memory import get_session_context, update_session_context
from .schemas import RetrieveResponse, GenerateResponse, ScoreResponse, SuggestionResponse

# FIX: Corrected the default ports for downstream services
SCORING_SERVICE_URL = os.getenv("SCORING_SERVICE_URL", "http://scoring-service:8004")
RETRIEVAL_SERVICE_URL = os.getenv("RETRIEVAL_SERVICE_URL", "http://retrieval-service:8002")
GENERATION_SERVICE_URL = os.getenv("GENERATION_SERVICE_URL", "http://generator-service:8000")

def format_context_for_prompt(chunks: List) -> str:
    """Formats retrieved chunks into a human-readable context string."""
    if not chunks:
        return "No relevant context was found from the user's profile."
    formatted_strings = [f"- From {c.index_namespace} ({c.source_type}): {c.text.strip()}" for c in chunks]
    return "\n".join(formatted_strings)

class ToolBox:
    """A container for agent tools that shares the HTTP client."""
    def __init__(self, client: httpx.AsyncClient):
        self.http_client = client
        # Bind instance methods to LangChain's tool decorator
        self.retrieve_context_tool = tool(self._retrieve_context_tool)
        self.generate_text_tool = tool(self._generate_text_tool)
        self.get_current_resume_section_tool = tool(self._get_current_resume_section_tool)
        self.update_resume_in_memory_tool = tool(self._update_resume_in_memory_tool)
        self.score_resume_text_tool = tool(self._score_resume_text_tool)
        self.get_improvement_suggestions_tool = tool(self._get_improvement_suggestions_tool)
        # FIX: Added new tool to the toolbox
        self.get_full_resume_text_tool = tool(self._get_full_resume_text_tool)

    async def _retrieve_context_tool(self, session_id: str, section_id: Optional[str] = None) -> str:
        """Use this tool to get relevant context from the user's profile. If rewriting a section, provide `section_id`. For a full resume, omit `section_id`."""
        context = get_session_context(session_id)
        if not context: return "Error: Session not found."
        payload = {"user_id": context["user_id"], "job_description": context["job_description"]}
        endpoint = f"{RETRIEVAL_SERVICE_URL.rstrip('/')}/retrieve/{'full' if not section_id else 'section'}"
        if section_id: payload["section_id"] = section_id
        try:
            response = await self.http_client.post(endpoint, json=payload)
            response.raise_for_status()
            return format_context_for_prompt(RetrieveResponse(**response.json()).results)
        except Exception as e: return f"Error retrieving context: {e}"

    async def _generate_text_tool(self, session_id: str, section_id: Optional[str] = None, existing_text: Optional[str] = None) -> str:
        """Use this to generate new resume text. For a section, provide `section_id` and `existing_text`. For a full resume, omit these. Returns a JSON string."""
        context = get_session_context(session_id)
        if not context: return "Error: Session not found."
        payload = {"user_id": context["user_id"], "job_description": context["job_description"]}
        endpoint = f"{GENERATION_SERVICE_URL.rstrip('/')}/generate/{'full' if not section_id else 'section'}"
        if section_id: payload.update({"section_id": section_id, "existing_text": existing_text})
        try:
            response = await self.http_client.post(endpoint, json=payload)
            response.raise_for_status()
            return GenerateResponse(**response.json()).generated_text
        except Exception as e: return f"Error generating text: {e}"

    def _get_current_resume_section_tool(self, session_id: str, section_id: str) -> str:
        """Use this to get the current text of a single resume section before rewriting it."""
        context = get_session_context(session_id)
        if not context: return "Error: Session not found."
        section_content = context.get("resume_state", {}).get(section_id)
        return json.dumps(section_content) if section_content else f"Section '{section_id}' is empty."
    
    # FIX: Added new tool to get the full resume text for scoring
    def _get_full_resume_text_tool(self, session_id: str) -> str:
        """Use this to get the entire current resume as a single formatted string, which is required for scoring."""
        context = get_session_context(session_id)
        if not context or not context.get("resume_state"):
            return "Error: Resume is currently empty."
        
        resume_state = context["resume_state"]
        text_parts = []
        for section, content in resume_state.items():
            text_parts.append(f"--- {section.upper()} ---")
            if isinstance(content, list):
                # Handle list content like experience bullets or skills
                for item in content:
                    text_parts.append(str(item))
            else:
                text_parts.append(str(content))
            text_parts.append("") # Add a blank line for readability
        
        return "\n".join(text_parts).strip()

    # FIX: Enhanced tool to handle both full resume and single section updates
    def _update_resume_in_memory_tool(self, session_id: str, new_content_json: str, section_id: Optional[str] = None) -> str:
        """Use this to save generated content. For a single section, provide `section_id`. For a full resume, omit `section_id`. The `new_content_json` must be the JSON string from `generate_text_tool`."""
        context = get_session_context(session_id)
        if not context: return "Error: Session not found."
        try:
            new_content = json.loads(new_content_json)
            
            if section_id:
                # Update a single section. The generated JSON should have one key matching the section_id.
                if section_id not in new_content:
                    return f"Error: Generated content does not contain the expected section '{section_id}'."
                context["resume_state"][section_id] = new_content[section_id]
                update_session_context(session_id, context)
                return f"Successfully updated section '{section_id}'."
            else:
                # Update the full resume from a multi-key object (e.g., from full generation)
                context["resume_state"].update(new_content)
                update_session_context(session_id, context)
                return f"Successfully updated the full resume with sections: {', '.join(new_content.keys())}."
        except Exception as e: return f"Error updating resume: Invalid JSON or structure. Details: {e}"

    async def _score_resume_text_tool(self, session_id: str, resume_text: str) -> str:
        """Use this tool AFTER generating text to evaluate how well it matches the job description. It provides a quality score and identifies missing keywords."""
        context = get_session_context(session_id)
        if not context: return "Error: Session not found."
        endpoint = f"{SCORING_SERVICE_URL.rstrip('/')}/score"
        payload = {"job_description": context["job_description"], "resume_text": resume_text}
        try:
            response = await self.http_client.post(endpoint, json=payload)
            response.raise_for_status()
            score_data = ScoreResponse(**response.json())
            return f"Scoring Result: Match Score = {score_data.match_score:.2f}, Missing Keywords = {score_data.missing_keywords}"
        except Exception as e: return f"Error scoring text: {e}"

    async def _get_improvement_suggestions_tool(self, missing_keywords: List[str]) -> str:
        """Use this tool if a score is low to get actionable suggestions for improvement based on a list of missing keywords."""
        if not missing_keywords: return "No missing keywords provided."
        endpoint = f"{SCORING_SERVICE_URL.rstrip('/')}/suggest"
        payload = {"missing_keywords": missing_keywords}
        try:
            response = await self.http_client.post(endpoint, json=payload)
            response.raise_for_status()
            suggestions = SuggestionResponse(**response.json()).suggestions
            if not suggestions: return "No specific suggestions were generated."
            return "Here are some suggestions for improvement:\n- " + "\n- ".join(suggestions)
        except Exception as e: return f"Error getting suggestions: {e}"