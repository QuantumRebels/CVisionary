import faiss
import numpy as np
from typing import Dict, Tuple, List, Optional
import sqlite3

from .db import get_user_chunks_by_namespace

# Global dictionary to store FAISS indices per user and namespace
# Structure: user_id -> namespace -> (faiss_index, id_to_chunk_id_map)
user_indices: Dict[str, Dict[str, Tuple[faiss.IndexFlatIP, Dict[int, str]]]] = {}

def build_index_from_db(all_rows: List[sqlite3.Row]) -> None:
    """Build FAISS indices from all chunks in database, respecting namespaces."""
    global user_indices
    user_indices.clear()
    
    # Group chunks by user_id and then by namespace
    user_namespace_chunks: Dict[str, Dict[str, List[sqlite3.Row]]] = {}
    for row in all_rows:
        user_id = row['user_id']
        namespace = row['index_namespace']
        
        if user_id not in user_namespace_chunks:
            user_namespace_chunks[user_id] = {}
        if namespace not in user_namespace_chunks[user_id]:
            user_namespace_chunks[user_id][namespace] = []
        user_namespace_chunks[user_id][namespace].append(row)
    
    # Create FAISS index for each user/namespace pair
    for user_id, namespaces in user_namespace_chunks.items():
        if user_id not in user_indices:
            user_indices[user_id] = {}
        for namespace, chunks in namespaces.items():
            _build_single_index(user_id, namespace, chunks)
    
    print(f"Built FAISS indices for {len(user_indices)} users across namespaces.")

def _build_single_index(user_id: str, namespace: str, chunks: List[sqlite3.Row]):
    """Helper to build or rebuild one specific index."""
    dim = 384
    index = faiss.IndexFlatIP(dim)
    id_to_chunk_id = {}
    embeddings = []
    
    for i, chunk_row in enumerate(chunks):
        embedding = np.frombuffer(chunk_row['embedding'], dtype=np.float32)
        embeddings.append(embedding)
        id_to_chunk_id[i] = chunk_row['chunk_id']
        
    if embeddings:
        embeddings_matrix = np.vstack(embeddings)
        index.add(embeddings_matrix)
    
    if user_id not in user_indices:
        user_indices[user_id] = {}
    user_indices[user_id][namespace] = (index, id_to_chunk_id)
    print(f"Built FAISS index for user '{user_id}' namespace '{namespace}' with {len(chunks)} items.")

def rebuild_index_for_user_namespace(user_id: str, namespace: str) -> None:
    """Fetches all chunks for a user/namespace from DB and rebuilds the FAISS index."""
    chunks = get_user_chunks_by_namespace(user_id, namespace)
    _build_single_index(user_id, namespace, chunks)

def add_to_index(user_id: str, namespace: str, chunk_id: str, embedding_vector: np.ndarray) -> None:
    """Add a new embedding vector to a user's namespaced FAISS index."""
    global user_indices
    
    if user_id not in user_indices or namespace not in user_indices[user_id]:
        # Create new index if it doesn't exist
        dim = 384
        index = faiss.IndexFlatIP(dim)
        id_to_chunk_id = {}
        if user_id not in user_indices:
            user_indices[user_id] = {}
        user_indices[user_id][namespace] = (index, id_to_chunk_id)

    index, id_to_chunk_id = user_indices[user_id][namespace]
    
    new_faiss_id = index.ntotal
    index.add(embedding_vector.reshape(1, -1))
    id_to_chunk_id[new_faiss_id] = chunk_id

def search(user_id: str, namespace: str, query_vector: np.ndarray, top_k: int) -> Tuple[List[str], List[float]]:
    """Search for similar embeddings in a user's namespaced FAISS index."""
    global user_indices
    
    if user_id not in user_indices or namespace not in user_indices[user_id]:
        return [], []
    
    index, id_to_chunk_id = user_indices[user_id][namespace]
    
    if index.ntotal == 0:
        return [], []
    
    actual_k = min(top_k, index.ntotal)
    query_matrix = query_vector.reshape(1, -1)
    scores, faiss_ids = index.search(query_matrix, actual_k)
    
    chunk_ids = [id_to_chunk_id[i] for i in faiss_ids[0] if i in id_to_chunk_id]
    similarity_scores = [float(s) for s in scores[0]]
    
    return chunk_ids, similarity_scores

def delete_user_index(user_id: str, namespace: Optional[str] = None):
    """Deletes an index. If namespace is given, deletes only that sub-index."""
    if user_id in user_indices:
        if namespace and namespace in user_indices[user_id]:
            del user_indices[user_id][namespace]
            print(f"Deleted FAISS index for user '{user_id}' namespace '{namespace}'.")
        elif not namespace:
            del user_indices[user_id]
            print(f"Deleted all FAISS indices for user '{user_id}'.")