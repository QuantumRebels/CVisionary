# memory.py

import json
import os
from typing import Dict, Any, Optional
import redis
from langchain_community.chat_message_histories import RedisChatMessageHistory

# Initialize Redis client from environment variable
redis_url = os.getenv("REDIS_URL", "redis://redis:6379")

def get_redis_client():
    """Get Redis client with proper error handling"""
    try:
        return redis.from_url(redis_url, decode_responses=True)
    except redis.exceptions.ConnectionError:
        # Return a dummy client that fails gracefully
        class DummyRedis:
            def get(self, *args, **kwargs):
                return None
            def set(self, *args, **kwargs):
                pass
            def ping(self):
                raise redis.exceptions.ConnectionError("Dummy client")
        return DummyRedis()

redis_client = get_redis_client()

def get_session_history(session_id: str) -> RedisChatMessageHistory:
    """Get a Redis-backed chat message history object for a given session."""
    return RedisChatMessageHistory(session_id=session_id, url=redis_url)

def get_session_context(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve the full context for a session (user_id, jd, resume_state)."""
    key = f"session_context:{session_id}"
    try:
        data = redis_client.get(key)
    except Exception:
        return None
        
    if data:
        return json.loads(data)
    return None

def update_session_context(session_id: str, context_data: Dict[str, Any]) -> None:
    """Save the full session context to Redis."""
    key = f"session_context:{session_id}"
    try:
        redis_client.set(key, json.dumps(context_data))
    except Exception:
        pass

def initialize_session_context(session_id: str, user_id: str, job_description: str) -> Dict[str, Any]:
    """Create a new session context if one doesn't exist."""
    context = {
        "user_id": user_id,
        "job_description": job_description,
        "resume_state": {} # Start with an empty resume
    }
    update_session_context(session_id, context)
    return context