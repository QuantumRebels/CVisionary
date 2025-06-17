# app.py

from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
import httpx
import uuid
import numpy as np
from typing import List
from dotenv import load_dotenv
load_dotenv()

from .model import load_model, embed_text
from .faiss_index import (
    build_index_from_db,
    search,
    rebuild_index_for_user_namespace,
    delete_user_index,
)
from .db import (
    init_db,
    store_chunk,
    get_all_chunks,
    get_chunk_by_id,
    mark_user_indexed,
    delete_user_chunks,
    delete_chunks_by_section_id,
)
from .schemas import (
    EmbedRequest,
    EmbedResponse,
    IndexProfileResponse,
    RetrieveRequest,
    RetrieveResponse,
    ChunkItem,
    IndexSectionRequest,
    IndexSectionResponse,
    DeleteSectionResponse,
)
from .chunking import chunk_text, extract_text_fields

# This will be managed by the lifespan context and dependency injection
http_client: httpx.AsyncClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup and clean up on shutdown."""
    global http_client
    # Initialize DB, load model
    init_db()
    load_model()

    # Build FAISS indices from existing DB
    all_chunks = get_all_chunks()
    build_index_from_db(all_chunks)

    # Initialize HTTP client
    http_client = httpx.AsyncClient()

    print(f"Initialized embedding service with {len(all_chunks)} existing chunks")
    yield
    # Clean up resources
    await http_client.aclose()
    print("Embedding service shut down.")


app = FastAPI(
    title="CVisionary Embedding Service", version="1.1.0", lifespan=lifespan
)

# --- Dependency ---
async def get_http_client() -> httpx.AsyncClient:
    """Dependency to provide the global http_client."""
    return http_client


# --- Endpoints ---


@app.post(
    "/index/profile/{user_id}", response_model=IndexProfileResponse, tags=["Indexing"]
)
async def index_user_profile(
    user_id: str, client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    DESTRUCTIVE. Fetches a user's full profile, deletes all previous profile
    embeddings for that user, and creates new ones.
    """
    try:
        # Delete old profile data first for idempotency
        delete_user_chunks(user_id, namespace="profile")
        delete_user_index(user_id, namespace="profile")

        response = await client.get(f"http://localhost:5000/profile/{user_id}")
        response.raise_for_status()  # Raises HTTPError for 4xx/5xx responses

        profile_data = response.json()
        text_fields = extract_text_fields(profile_data)

        total_chunks = 0
        for source_type, source_id, text in text_fields:
            chunks = chunk_text(text)
            for chunk_text_content in chunks:
                chunk_id = str(uuid.uuid4())
                embedding_vector = embed_text(chunk_text_content)
                embedding_bytes = embedding_vector.tobytes()

                store_chunk(
                    chunk_id,
                    user_id,
                    "profile",
                    None,
                    source_type,
                    source_id,
                    chunk_text_content,
                    embedding_bytes,
                )
                total_chunks += 1

        # Rebuild the FAISS index for the 'profile' namespace from scratch
        if total_chunks > 0:
            rebuild_index_for_user_namespace(user_id, "profile")

        mark_user_indexed(user_id)
        return IndexProfileResponse(
            status=f"Profile for user {user_id} re-indexed successfully",
            num_chunks=total_chunks,
        )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, detail=f"Failed to fetch profile from backend: {str(e)}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Backend service returned an error: {e.response.text}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during indexing: {str(e)}")


@app.post(
    "/index/{user_id}/section", response_model=IndexSectionResponse, tags=["Indexing"]
)
async def index_resume_section(user_id: str, request: IndexSectionRequest):
    """
    Adds or updates embeddings for a specific resume section.
    This is the primary endpoint for handling user-edited text. It deletes any
    old chunks with the same section_id before creating new ones.
    """
    try:
        # Delete old chunks for this section to ensure an update, not an addition
        delete_chunks_by_section_id(user_id, request.section_id)

        chunks = chunk_text(request.text)
        new_chunk_ids = []
        for i, chunk_text_content in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            embedding_vector = embed_text(chunk_text_content)

            store_chunk(
                chunk_id=chunk_id,
                user_id=user_id,
                namespace="resume_sections",
                section_id=request.section_id,
                source_type="user_edited",
                source_id=str(i),
                text=chunk_text_content,
                embedding_bytes=embedding_vector.tobytes(),
            )
            new_chunk_ids.append(chunk_id)

        # After DB changes, rebuild the relevant FAISS index to ensure consistency
        rebuild_index_for_user_namespace(user_id, "resume_sections")

        return IndexSectionResponse(
            status=f"Section {request.section_id} indexed successfully.",
            section_id=request.section_id,
            chunk_ids=new_chunk_ids,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing section: {str(e)}")


@app.delete(
    "/index/{user_id}/section/{section_id}",
    response_model=DeleteSectionResponse,
    tags=["Indexing"],
)
async def delete_resume_section(user_id: str, section_id: str):
    """Deletes all embeddings associated with a specific resume section_id."""
    try:
        deleted_count = delete_chunks_by_section_id(user_id, section_id)
        if deleted_count > 0:
            rebuild_index_for_user_namespace(user_id, "resume_sections")

        return DeleteSectionResponse(
            status=f"Deleted {deleted_count} chunks for section {section_id}.",
            section_id=section_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting section: {str(e)}"
        )


@app.post("/retrieve/{user_id}", response_model=RetrieveResponse, tags=["Retrieval"])
async def retrieve_similar_chunks(user_id: str, request: RetrieveRequest):
    """
    Retrieve top-k chunks for a user based on a query. Can be filtered
    by index namespace and a list of section_ids.
    """
    try:
        query_vec = np.array(request.query_embedding, dtype=np.float32)
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec /= norm

        chunk_ids, scores = search(
            user_id, request.index_namespace, query_vec, request.top_k
        )

        results = []
        for chunk_id, score in zip(chunk_ids, scores):
            chunk_data = get_chunk_by_id(chunk_id)
            if not chunk_data:
                continue

            # Post-filter by section_id if a filter is provided
            if (
                request.filter_by_section_ids
                and chunk_data["section_id"] not in request.filter_by_section_ids
            ):
                continue

            results.append(
                ChunkItem(
                    chunk_id=chunk_data["chunk_id"],
                    user_id=chunk_data["user_id"],
                    index_namespace=chunk_data["index_namespace"],
                    section_id=chunk_data["section_id"],
                    source_type=chunk_data["source_type"],
                    source_id=chunk_data["source_id"],
                    text=chunk_data["text"],
                    score=float(score),
                    created_at=chunk_data["created_at"],
                )
            )

        return RetrieveResponse(results=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during retrieval: {str(e)}")


@app.post("/embed", response_model=EmbedResponse, tags=["Utilities"])
async def embed_text_endpoint(request: EmbedRequest):
    """Generate a normalized embedding for arbitrary text."""
    try:
        embedding_vector = embed_text(request.text)
        return EmbedResponse(embedding=embedding_vector.tolist())
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating embedding: {str(e)}"
        )


@app.get("/health", tags=["Utilities"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "embedding_service"}