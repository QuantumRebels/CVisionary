import os
import httpx
from typing import List
import re

async def generate_bullets(prompt: str) -> List[str]:
    # 1. Verify GEMINI_API_KEY non-empty
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    gemini_api_url = os.getenv("GEMINI_API_URL", "https://api.gemini.google/v1/generateText")
    
    if not gemini_api_key:
        return []
    
    # 2. Build payload
    payload = {
        "model": "gemini-pro",
        "prompt": prompt,
        "max_output_tokens": 256,
        "temperature": 0.7
    }
    
    # 3. Send POST to GEMINI_API_URL
    headers = {
        "Authorization": f"Bearer {gemini_api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                gemini_api_url,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            # 4. If status != 200, return []
            if response.status_code != 200:
                return []
            
            # 5. Parse JSON → data["choices"][0]["text"]
            data = response.json()
            if "choices" not in data or len(data["choices"]) == 0:
                return []
            
            generated_text = data["choices"][0].get("text", "")
            
            # 6. Split lines, strip leading "- " or "• ", filter out empty lines
            lines = generated_text.split('\n')
            bullets = []
            
            for line in lines:
                # Strip whitespace
                line = line.strip()
                # Remove leading bullet markers
                line = re.sub(r'^[-•]\s*', '', line)
                # Skip empty lines
                if line:
                    bullets.append(line)
            
            # 7. Return List[str] (limit to reasonable number)
            return bullets[:6]  # Return at most 6 bullets
            
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return []