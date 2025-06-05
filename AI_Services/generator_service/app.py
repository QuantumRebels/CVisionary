import os
from fastapi import FastAPI, HTTPException, status
import httpx
from schemas import GenerateRequest, GenerateResponse
from utils import extract_keywords, build_rag_prompt
from llm_client import generate_bullets

app = FastAPI(title="CVisionary Generator Service")

# Environment variables
EMBEDDING_SERVICE_URL = os.getenv("EMBEDDING_SERVICE_URL", "http://localhost:8001")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = os.getenv("GEMINI_API_URL", "https://api.gemini.google/v1/generateText")

@app.post("/generate/{user_id}", response_model=GenerateResponse)
async def generate_resume(user_id: str, req: GenerateRequest):
    # 1. Validate GEMINI_API_KEY
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GEMINI_API_KEY environment variable is not set"
        )
    
    try:
        async with httpx.AsyncClient() as client:
            # 2. Embed job description via Embedding Service
            embed_response = await client.post(
                f"{EMBEDDING_SERVICE_URL}/embed",
                json={"text": req.job_description},
                timeout=30.0
            )
            
            if embed_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Embedding service failure"
                )
            
            embed_data = embed_response.json()
            if "embedding" not in embed_data:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Embedding service failure"
                )
            
            embedding = embed_data["embedding"]
            
            # 3. Retrieve chunks via Embedding Service
            retrieve_response = await client.post(
                f"{EMBEDDING_SERVICE_URL}/retrieve/{user_id}",
                json={"query_embedding": embedding, "top_k": 5},
                timeout=30.0
            )
            
            if retrieve_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found or no chunks indexed"
                )
            
            retrieve_data = retrieve_response.json()
            chunks = retrieve_data.get("results", [])
            
            # 4. Extract keywords
            keywords = extract_keywords(req.job_description)
            
            # 5. Build RAG prompt
            prompt = build_rag_prompt(chunks, keywords)
            
            # 6. Call LLM
            bullets = await generate_bullets(prompt)
            
            # 7. Check if bullets are empty or errors occurred
            if not bullets:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to generate bullet points from LLM"
                )
            
            # 8. Return response
            return GenerateResponse(bullets=bullets, raw_prompt=prompt)
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Service communication error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)