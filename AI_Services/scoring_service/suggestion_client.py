import os
import logging
import httpx
import json
from typing import List
import re

logger = logging.getLogger(__name__)

class SuggestionClient:
    """
    Client for generating suggestions using Google Gemini API
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.api_url = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent")
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
    
    async def generate_suggestions(self, missing_skills: List[str]) -> List[str]:
        """
        Generate up to 3 suggestions for adding missing skills to resume
        
        Args:
            missing_skills: List of missing skills
            
        Returns:
            List of suggestion strings (up to 3)
        """
        if not self.api_key:
            logger.warning("Cannot generate suggestions: GEMINI_API_KEY not configured")
            return []
        
        if not missing_skills:
            return []
        
        try:
            # Build prompt for Gemini
            skills_text = ", ".join(missing_skills[:5])  # Limit to first 5 skills
            prompt = self._build_prompt(skills_text)
            
            # Call Gemini API
            suggestions_text = await self._call_gemini_api(prompt)
            
            # Parse suggestions from response
            suggestions = self._parse_suggestions(suggestions_text)
            
            # Return up to 3 suggestions
            return suggestions[:3]
            
        except Exception as e:
            logger.error(f"Failed to generate suggestions: {str(e)}")
            return []
    
    def _build_prompt(self, skills: str) -> str:
        """
        Build prompt for Gemini API
        
        Args:
            skills: Comma-separated list of missing skills
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a career advisor helping someone improve their resume. The candidate is missing these skills for a job: {skills}

Please provide exactly 3 concise, actionable bullet-point suggestions (maximum 20 words each) on how they can add or demonstrate these skills on their resume. Focus on practical ways to gain experience or showcase existing knowledge.

Format your response as:
• [Suggestion 1]
• [Suggestion 2] 
• [Suggestion 3]

Keep each suggestion under 20 words and focus on actionable advice."""

        return prompt
    
    async def _call_gemini_api(self, prompt: str) -> str:
        """
        Call Gemini API with the given prompt
        
        Args:
            prompt: Input prompt for Gemini
            
        Returns:
            Generated text response
        """
        try:
            # Prepare request payload
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024
                }
            }
            
            headers = {
                "Content-Type": "application/json",
            }
            
            # Make API request
            url = f"{self.api_url}?key={self.api_key}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                
                # Extract text from Gemini response
                if "candidates" in result and len(result["candidates"]) > 0:
                    content = result["candidates"][0].get("content", {})
                    parts = content.get("parts", [])
                    if parts and len(parts) > 0:
                        return parts[0].get("text", "")
                
                logger.warning("No valid response from Gemini API")
                return ""
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Gemini API: {e.response.status_code} - {e.response.text}")
            raise e
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            raise e
    
    def _parse_suggestions(self, suggestions_text: str) -> List[str]:
        """
        Parse suggestions from Gemini response text
        
        Args:
            suggestions_text: Raw text response from Gemini
            
        Returns:
            List of parsed suggestions
        """
        if not suggestions_text:
            return []
        
        try:
            suggestions = []
            lines = suggestions_text.strip().split('\n')

            for line in lines:
                line = line.strip()
                
                if not line:
                    continue

                suggestion_text = None
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    suggestion_text = re.sub(r'^[•\-\*]\s*', '', line).strip()
                elif re.match(r'^\d+\.', line):
                    suggestion_text = re.sub(r'^\d+\.\s*', '', line).strip() # More specific for numbers
                
                if suggestion_text and len(suggestion_text.split()) <= 25:
                    if suggestion_text not in suggestions: # Avoid duplicates from multiple lines
                        suggestions.append(suggestion_text)
        
            # Fallback: if no bullet points were effectively processed and the original text wasn't just empty lines
            if not suggestions and suggestions_text.strip():
                # Split after punctuation, keeping it, then strip it if it's at the very end.
                raw_sentences = re.split(r'(?<=[.!?])\s+', suggestions_text.strip())
                
                for sentence in raw_sentences:
                    sentence = sentence.strip()
                    # Remove common sentence-ending punctuation if it's the very last char of the segment
                    if sentence.endswith(('.', '!', '?')):
                        sentence = sentence[:-1].strip()

                    if sentence and len(sentence.split()) <= 25:
                        if sentence not in suggestions: 
                            suggestions.append(sentence)
        
            return suggestions
            
        except Exception as e:
            logger.error(f"Error parsing suggestions: {str(e)}")
            return []