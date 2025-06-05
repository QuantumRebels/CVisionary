import faiss
import numpy as np
from typing import Dict, Tuple, List, Optional

# Global dictionary to store FAISS indices per user
# Structure: user_id -> (faiss_index, id_to_chunk_id_map)
user_indices: Dict[str, Tuple[faiss.IndexFlatIP, Dict[int, str]]] = {}

def build_index_from_db(all_rows: List[tuple]) -> None:
    """
    Build FAISS indices from all chunks in database.
    Called once during startup.
    
    Args:
        all_rows: List of (chunk_id, user_id, source_type, source_id, text, embedding_blob) tuples
    """
    global user_indices
    user_indices.clear()
    
    # Group chunks by user_id
    user_chunks: Dict[str, List[tuple]] = {}
    for row in all_rows:
        chunk_id, user_id, source_type, source_id, text, embedding_blob = row
        if user_id not in user_chunks:
            user_chunks[user_id] = []
        user_chunks[user_id].append(row)
    
    # Create FAISS index for each user
    for user_id, chunks in user_chunks.items():
        if not chunks:
            continue
            
        # Create FAISS index with inner product (cosine similarity for normalized vectors)
        dim = 384  # Embedding dimension
        index = faiss.IndexFlatIP(dim)
        
        # Create mapping from FAISS row ID to chunk ID
        id_to_chunk_id = {}
        
        # Add all embeddings to the index
        embeddings = []
        for i, (chunk_id, _, _, _, _, embedding_blob) in enumerate(chunks):
            # Convert blob back to numpy array
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            embeddings.append(embedding)
            id_to_chunk_id[i] = chunk_id
        
        # Add embeddings to FAISS index
        if embeddings:
            embeddings_matrix = np.vstack(embeddings)
            index.add(embeddings_matrix)
        
        user_indices[user_id] = (index, id_to_chunk_id)
    
    print(f"Built FAISS indices for {len(user_indices)} users")

def add_to_index(user_id: str, chunk_id: str, embedding_vector: np.ndarray) -> None:
    """
    Add a new embedding vector to the user's FAISS index.
    
    Args:
        user_id: User identifier
        chunk_id: Unique chunk identifier
        embedding_vector: Normalized 384-dimensional embedding vector
    """
    global user_indices
    
    if user_id not in user_indices:
        # Create new index for this user
        dim = 384
        index = faiss.IndexFlatIP(dim)
        id_to_chunk_id = {}
        user_indices[user_id] = (index, id_to_chunk_id)
    else:
        index, id_to_chunk_id = user_indices[user_id]
    
    # Add embedding to index
    embedding_matrix = embedding_vector.reshape(1, -1)
    index.add(embedding_matrix)
    
    # Update mapping (new vector gets the next available ID)
    new_faiss_id = index.ntotal - 1  # FAISS IDs are 0-indexed
    id_to_chunk_id[new_faiss_id] = chunk_id

def search(user_id: str, query_vector: np.ndarray, top_k: int) -> Tuple[List[str], List[float]]:
    """
    Search for similar embeddings in the user's FAISS index.
    
    Args:
        user_id: User identifier
        query_vector: Normalized query embedding vector
        top_k: Number of top results to return
        
    Returns:
        Tuple of (chunk_ids, similarity_scores)
    """
    global user_indices
    
    if user_id not in user_indices:
        return [], []
    
    index, id_to_chunk_id = user_indices[user_id]
    
    if index.ntotal == 0:
        return [], []
    
    # Limit top_k to available chunks
    actual_k = min(top_k, index.ntotal)
    
    # Search in FAISS index
    query_matrix = query_vector.reshape(1, -1)
    scores, faiss_ids = index.search(query_matrix, actual_k)
    
    # Convert FAISS IDs to chunk IDs
    chunk_ids = []
    similarity_scores = []
    
    for i in range(actual_k):
        faiss_id = faiss_ids[0][i]
        if faiss_id in id_to_chunk_id:
            chunk_ids.append(id_to_chunk_id[faiss_id])
            similarity_scores.append(scores[0][i])
    
    return chunk_ids, similarity_scores