from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
import requests
import uuid
import re
from typing import List
import nltk
import numpy as np

from model import load_model, embed_text
from faiss_index import build_index_from_db, add_to_index, search, user_indices
from db import init_db, store_chunk, get_all_chunks, get_chunk_by_id, mark_user_indexed
from schemas import EmbedRequest, EmbedResponse, IndexResponse, RetrieveRequest, RetrieveResponse, ChunkItem

# Download NLTK punkt tokenizer data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and FAISS indices on startup"""
    # Initialize database
    init_db()
    
    # Load sentence transformer model
    load_model()
    
    # Build FAISS indices from existing database
    all_chunks = get_all_chunks()
    build_index_from_db(all_chunks)
    
    print(f"Initialized embedding service with {len(all_chunks)} existing chunks")
    yield

app = FastAPI(title="CVisionary Embedding Service", version="1.0.0", lifespan=lifespan)

def chunk_text(text: str, max_words: int = 150) -> List[str]:
    """
    Split text into chunks of approximately max_words words each.
    Uses sentence boundaries to avoid cutting sentences in half.
    """
    if not text or not text.strip():
        return []
    
    # Tokenize into sentences
    sentences = nltk.sent_tokenize(text)
    
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for sentence in sentences:
        sentence_words = len(sentence.split())
        
        # If adding this sentence would exceed max_words, start a new chunk
        if current_word_count + sentence_words > max_words and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_word_count = sentence_words
        else:
            current_chunk.append(sentence)
            current_word_count += sentence_words
    
    # Add the last chunk if it has content
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def extract_text_fields(profile_data: dict) -> List[tuple]:
    """
    Extract text fields from profile JSON and return list of (source_type, source_id, text) tuples
    """
    text_fields = []
    
    # Extract experience descriptions
    if 'experience' in profile_data:
        for i, exp in enumerate(profile_data['experience']):
            if 'description' in exp and exp['description']:
                text_fields.append(('experience', str(i), exp['description']))
    
    # Extract project descriptions
    if 'projects' in profile_data:
        for i, project in enumerate(profile_data['projects']):
            if 'description' in project and project['description']:
                text_fields.append(('project', str(i), project['description']))
    
    # Extract skills as a combined text
    if 'skills' in profile_data and profile_data['skills']:
        if isinstance(profile_data['skills'], list):
            skills_text = ', '.join(str(skill) for skill in profile_data['skills'])
        else:
            skills_text = str(profile_data['skills'])
        text_fields.append(('skills', '0', skills_text))
    
    # Extract summary/bio if present
    if 'summary' in profile_data and profile_data['summary']:
        text_fields.append(('summary', '0', profile_data['summary']))
    if 'bio' in profile_data and profile_data['bio']:
        text_fields.append(('bio', '0', profile_data['bio']))
    
    return text_fields

@app.post("/index/{user_id}", response_model=IndexResponse)
async def index_user_profile(user_id: str):
    """
    Fetch user profile from backend, chunk text fields, generate embeddings,
    and store in database and FAISS index.
    """
    try:
        # Fetch profile from backend API
        response = requests.get(f"http://localhost:5000/profile/{user_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail=f"User profile not found for user_id: {user_id}")
        
        profile_data = response.json()
        
        # Extract text fields from profile
        text_fields = extract_text_fields(profile_data)
        
        total_chunks = 0
        
        for source_type, source_id, text in text_fields:
            # Split text into chunks
            chunks = chunk_text(text)
            
            for chunk_text_content in chunks:
                # Generate unique chunk ID
                chunk_id = str(uuid.uuid4())
                
                # Generate embedding for chunk
                embedding_vector = embed_text(chunk_text_content)
                
                # Store in database
                embedding_bytes = embedding_vector.tobytes()
                store_chunk(chunk_id, user_id, source_type, source_id, chunk_text_content, embedding_bytes)
                
                # Add to FAISS index
                add_to_index(user_id, chunk_id, embedding_vector)
                
                total_chunks += 1
        
        # Mark user as indexed
        mark_user_indexed(user_id)
        
        return IndexResponse(status="indexed", num_chunks=total_chunks)
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile from backend: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during indexing: {str(e)}")

@app.post("/embed", response_model=EmbedResponse)
async def embed_text_endpoint(request: EmbedRequest):
    """
    Generate embedding for arbitrary text.
    """
    try:
        embedding_vector = embed_text(request.text)
        return EmbedResponse(embedding=embedding_vector.tolist())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")

@app.post("/retrieve/{user_id}", response_model=RetrieveResponse)
async def retrieve_similar_chunks(user_id: str, request: RetrieveRequest):
    """
    Retrieve top-k most similar chunks for a user based on query embedding.
    """
    try:
        # Validate embedding dimension
        if len(request.query_embedding) != 384:
            raise HTTPException(status_code=400, detail="Query embedding must be 384-dimensional")
        
        # Convert to numpy array and normalize
        query_vec = np.array(request.query_embedding, dtype=np.float32)
        query_vec = query_vec / np.linalg.norm(query_vec)
        
        # Search in FAISS index
        chunk_ids, scores = search(user_id, query_vec, request.top_k)
        
        # Fetch chunk details from database
        results = []
        for chunk_id, score in zip(chunk_ids, scores):
            chunk_data = get_chunk_by_id(chunk_id)
            if chunk_data:
                chunk_id_db, user_id_db, source_type, source_id, text, _ = chunk_data
                results.append(ChunkItem(
                    chunk_id=chunk_id_db,
                    user_id=user_id_db,
                    source_type=source_type,
                    source_id=source_id,
                    text=text,
                    score=float(score)
                ))
        
        return RetrieveResponse(results=results)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during retrieval: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "embedding_service"}