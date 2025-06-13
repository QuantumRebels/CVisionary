# app.py

import os
import logging
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from model_inference import ModelInference
from feature_extractor import extract_required_keywords, identify_missing_keywords
from suggestion_client import generate_suggestions
from schemas import ScoreRequest, ScoreResponse, SuggestionRequest, SuggestionResponse, HealthResponse

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger(__name__)

# --- App State and Lifespan ---
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create a shared httpx client and load the ML model
    app_state["http_client"] = httpx.AsyncClient(timeout=30.0)
    
    logger.info("Initializing scoring model...")
    model_inference = ModelInference()
    model_inference.load_model()
    app_state["model_inference"] = model_inference
    logger.info("Scoring Service started up successfully.")
    
    yield
    
    # Shutdown: Close the client
    await app_state["http_client"].aclose()
    logger.info("Scoring Service shut down.")

app = FastAPI(
    title="CVisionary ATS Scoring Service",
    description="Scores a resume against a job description and provides improvement suggestions.",
    version="1.2.0", # Version bump for new model logic
    lifespan=lifespan
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- Dependencies ---
def get_http_client() -> httpx.AsyncClient:
    return app_state["http_client"]

def get_model_inference() -> ModelInference:
    return app_state["model_inference"]

# --- API Endpoints ---
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {"status": "healthy", "service": "scoring-service"}

@app.post("/score", response_model=ScoreResponse)
async def score_resume(
    request: ScoreRequest,
    model: ModelInference = Depends(get_model_inference)
):
    """
    Scores a resume against a job description by analyzing semantic similarity and keywords.
    """
    try:
        # 1. Compute Semantic Match Score using the specialized local model
        match_score = model.compute_match_score(request.job_description, request.resume_text)
        
        # 2. Perform Keyword Analysis
        required_keywords = extract_required_keywords(request.job_description)
        missing_keywords = identify_missing_keywords(required_keywords, request.resume_text)
        
        logger.info(f"Scoring complete. Score: {match_score:.2f}, Missing Keywords: {len(missing_keywords)}")
        
        return ScoreResponse(
            match_score=round(match_score, 3),
            missing_keywords=missing_keywords
        )
    except Exception as e:
        logger.error(f"Error during scoring process: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred during scoring.")

@app.post("/suggest", response_model=SuggestionResponse)
async def get_suggestions(
    request: SuggestionRequest,
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Generates actionable suggestions based on a list of missing keywords.
    """
    try:
        if not request.missing_keywords:
            return SuggestionResponse(suggestions=[])
            
        suggestions = await generate_suggestions(client, request.missing_keywords)
        
        return SuggestionResponse(suggestions=suggestions)
    except Exception as e:
        logger.error(f"Error during suggestion generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred while generating suggestions.")