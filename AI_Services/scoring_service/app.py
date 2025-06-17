import os
import logging
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from .model_inference import ModelInference
from .feature_extractor import extract_required_keywords, identify_missing_keywords
from .suggestion_client import generate_suggestions
from .schemas import ScoreRequest, ScoreResponse, SuggestionRequest, SuggestionResponse, HealthResponse

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger(__name__)

app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    app_state["http_client"] = httpx.AsyncClient(timeout=30.0)
    logger.info("Initializing scoring model...")
    model_inference = ModelInference()
    model_inference.load_model()
    app_state["model_inference"] = model_inference
    logger.info("Scoring Service started up successfully.")
    yield
    await app_state["http_client"].aclose()
    logger.info("Scoring Service shut down.")

app = FastAPI(
    title="CVisionary ATS Scoring Service",
    description="Scores a resume against a job description and provides improvement suggestions.",
    version="1.2.0",
    lifespan=lifespan
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def get_http_client() -> httpx.AsyncClient:
    return app_state["http_client"]

def get_model_inference() -> ModelInference:
    return app_state["model_inference"]

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {"status": "healthy", "service": "scoring-service"}

@app.post("/score", response_model=ScoreResponse)
async def score_resume(
    request: ScoreRequest,
    model: ModelInference = Depends(get_model_inference)
):
    try:
        match_score = model.compute_match_score(request.job_description, request.resume_text)
        required_keywords = extract_required_keywords(request.job_description)
        missing_keywords = identify_missing_keywords(required_keywords, request.resume_text)
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
    try:
        suggestions = await generate_suggestions(client, request.missing_keywords)
        return SuggestionResponse(suggestions=suggestions)
    except Exception as e:
        logger.error(f"Error during suggestion generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred while generating suggestions.")