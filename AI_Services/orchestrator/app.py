import logging
import os
import uuid
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import httpx

# Assuming agent.py and schemas.py are in the same directory
from .schemas import OrchestrateRequest, OrchestrateResponse
from .agent import run_orchestration_agent, get_orchestrator_agent_executor # To initialize on startup

# Load environment variables from .env file
load_dotenv() # Looks for .env in the current directory or parent directories

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Orchestrator Agent Service",
    description="Provides an endpoint to orchestrate resume tailoring tasks using a LangChain agent.",
    version="0.1.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Orchestrator service starting up...")
    # Initialize the agent executor on startup to preload models, etc.
    # This can help reduce latency on the first request.
    try:
        get_orchestrator_agent_executor() # This will initialize the global agent if not already done
        logger.info("LangChain agent executor initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize LangChain agent executor on startup: {e}", exc_info=True)
        # Depending on severity, you might want to prevent startup or handle gracefully

@app.post("/orchestrate", response_model=OrchestrateResponse)
async def orchestrate_resume_task(
    request_data: OrchestrateRequest = Body(...)
):
    """
    Receives a user ID and job description, then orchestrates a series of AI tasks 
    (embed, retrieve, generate, score, suggest) to produce tailored resume bullets 
    and improvement suggestions.
    """
    user_id = request_data.user_id
    job_description = request_data.job_description
    session_id = str(uuid.uuid4()) # Generate a unique session ID for each request for memory management

    logger.info(f"Received orchestration request for user_id: {user_id}, session_id: {session_id}")

    if not user_id or not job_description:
        logger.warning("Missing user_id or job_description in request.")
        raise HTTPException(status_code=400, detail="user_id and job_description are required.")

    try:
        # Call the agent runner function from agent.py
        result = await run_orchestration_agent(
            user_id=user_id,
            job_description=job_description,
            session_id=session_id
        )
        logger.info(f"Orchestration successful for user_id: {user_id}, session_id: {session_id}. Score: {result.match_score}")
        return result
    except Exception as e:
        logger.error(f"Unhandled error during orchestration for user_id {user_id}, session_id {session_id}: {e}", exc_info=True)
        # Return a 500 error with a generic message or specific details if safe
        # The OrchestrateResponse schema allows suggestions to carry error messages
        error_response_content = {
            "bullets": [],
            "match_score": 0.0,
            "suggestions": [f"An internal server error occurred: {str(e)}."]
        }
        return JSONResponse(status_code=500, content=error_response_content)

@app.get("/health", status_code=200)
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "message": "Orchestrator Agent Service is running."}

@app.get("/config", summary="Check Configuration and Dependent Service Connectivity")
async def check_config():
    """Checks the current configuration and attempts to connect to dependent services' health endpoints."""
    services_to_check = {
        "embedding_service": EMBEDDING_SERVICE_URL,
        "generation_service": GENERATION_SERVICE_URL,
        "scoring_service": SCORING_SERVICE_URL
    }
    
    status_report = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in services_to_check.items():
            if not url:
                status_report[name] = {"status": "misconfigured", "url": None, "error": "URL not set in environment variables."}
                logger.warning(f"Configuration check: {name} URL is not set.")
                continue
            
            health_url = f"{url.rstrip('/')}/health"
            try:
                logger.info(f"Checking health of {name} at {health_url}")
                resp = await client.get(health_url)
                if resp.status_code == 200:
                    status_report[name] = {"status": "reachable", "url": url, "health_check_url": health_url, "response_status": resp.status_code}
                else:
                    status_report[name] = {"status": f"unexpected_status", "url": url, "health_check_url": health_url, "response_status": resp.status_code, "response_text": resp.text[:200]}
                    logger.warning(f"Configuration check: {name} at {health_url} returned status {resp.status_code}")
            except httpx.TimeoutException:
                status_report[name] = {"status": "timeout", "url": url, "health_check_url": health_url, "error": "Request timed out."}
                logger.error(f"Configuration check: Timeout connecting to {name} at {health_url}")
            except httpx.RequestError as e:
                status_report[name] = {"status": "error", "url": url, "health_check_url": health_url, "error": str(e)}
                logger.error(f"Configuration check: Error connecting to {name} at {health_url}: {e}")
            except Exception as e:
                status_report[name] = {"status": "unknown_error", "url": url, "health_check_url": health_url, "error": str(e)}
                logger.error(f"Configuration check: Unknown error for {name} at {health_url}: {e}")

    all_reachable = all(s.get("status") == "reachable" for s in status_report.values() if s.get("url"))
    overall_status = "healthy" if all_reachable else "degraded"
    
    return {
        "overall_status": overall_status,
        "services": status_report,
        "message": "Configuration and connectivity check complete. Ensure all services are reachable for full functionality."
    }

# To run this app (example, usually done with uvicorn command directly):
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("ORCHESTRATOR_PORT", "8004"))
    uvicorn.run(app, host="0.0.0.0", port=port)
