import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from model_inference import ModelInference
from feature_extractor import extract_required_keywords, identify_missing_keywords
from suggestion_client import SuggestionClient
from schemas import ScoreRequest, ScoreResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for model and suggestion client
model_inference = None
suggestion_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global model_inference, suggestion_client
    
    logger.info("Loading MiniLM model...")
    model_inference = ModelInference()
    model_inference.load_model()
    logger.info("MiniLM model loaded successfully")
    
    # Initialize suggestion client
    suggestion_client = SuggestionClient()
    logger.info("Suggestion client initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="CVisionary ATS Scoring Service",
    description="AI-powered resume scoring and suggestions service",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ats-scoring-service"}

@app.post("/score", response_model=ScoreResponse)
async def score_resume(request: ScoreRequest):
    """
    Score a resume against a job description and provide suggestions
    """
    try:
        # Extract required skills from job description
        required_keywords = extract_required_keywords(request.job_description)
        logger.info(f"Required keywords extracted: {required_keywords}")
        
        # Generate embeddings for both texts
        jd_embedding = model_inference.embed_text(request.job_description)
        resume_embedding = model_inference.embed_text(request.resume_text)
        
        # Compute match score
        match_score = model_inference.compute_match_score(jd_embedding, resume_embedding)
        logger.info(f"Match score computed: {match_score}")
        
        # Identify missing keywords
        missing_keywords = identify_missing_keywords(required_keywords, request.resume_text)
        logger.info(f"Missing keywords: {missing_keywords}")
        
        # Generate suggestions if score is below threshold and there are missing skills
        match_threshold = float(os.getenv("MATCH_THRESHOLD", "0.7"))
        suggestions = []
        
        if match_score < match_threshold and missing_keywords:
            try:
                suggestions = await suggestion_client.generate_suggestions(missing_keywords)
                logger.info(f"Generated {len(suggestions)} suggestions")
            except Exception as e:
                logger.error(f"Failed to generate suggestions: {str(e)}")
                # Continue without suggestions rather than failing the entire request
                suggestions = []
        
        return ScoreResponse(
            match_score=round(match_score, 3),
            missing_keywords=missing_keywords,
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)