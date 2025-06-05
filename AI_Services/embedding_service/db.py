import sqlite3
import numpy as np
from typing import List, Optional, Tuple
from datetime import datetime
import os

DB_PATH = "embeddings.db"

def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory for easier data access"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """
    Initialize database tables if they don't exist.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                last_indexed_at TEXT NOT NULL
            )
        """)
        
        # Create chunks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_id TEXT NOT NULL,
                text TEXT NOT NULL,
                embedding BLOB NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Create index on user_id for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_user_id ON chunks (user_id)
        """)
        
        conn.commit()
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def store_chunk(chunk_id: str, user_id: str, source_type: str, source_id: str, 
                text: str, embedding_bytes: bytes) -> None:
    """
    Store a chunk with its embedding in the database.
    
    Args:
        chunk_id: Unique identifier for the chunk
        user_id: User identifier
        source_type: Type of source (e.g., 'experience', 'project', 'skills')
        source_id: Identifier within the source type
        text: The actual text content
        embedding_bytes: Serialized embedding vector as bytes
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO chunks 
            (chunk_id, user_id, source_type, source_id, text, embedding)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chunk_id, user_id, source_type, source_id, text, embedding_bytes))
        conn.commit()
    except Exception as e:
        print(f"Error storing chunk {chunk_id}: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def get_all_chunks() -> List[Tuple[str, str, str, str, str, bytes]]:
    """
    Retrieve all chunks from the database.
    
    Returns:
        List of (chunk_id, user_id, source_type, source_id, text, embedding_blob) tuples
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT chunk_id, user_id, source_type, source_id, text, embedding
            FROM chunks
            ORDER BY user_id, source_type, source_id
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching all chunks: {e}")
        return []
    finally:
        conn.close()

def get_chunk_by_id(chunk_id: str) -> Optional[Tuple[str, str, str, str, str, bytes]]:
    """
    Retrieve a single chunk by its ID.
    
    Args:
        chunk_id: Unique chunk identifier
        
    Returns:
        Tuple of (chunk_id, user_id, source_type, source_id, text, embedding_blob) or None
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT chunk_id, user_id, source_type, source_id, text, embedding
            FROM chunks
            WHERE chunk_id = ?
        """, (chunk_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching chunk {chunk_id}: {e}")
        return None
    finally:
        conn.close()

def mark_user_indexed(user_id: str) -> None:
    """
    Mark a user as indexed with current timestamp.
    
    Args:
        user_id: User identifier
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        current_time = datetime.now().isoformat()
        cursor.execute("""
            INSERT OR REPLACE INTO users (user_id, last_indexed_at)
            VALUES (?, ?)
        """, (user_id, current_time))
        conn.commit()
    except Exception as e:
        print(f"Error marking user {user_id} as indexed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def get_user_chunks(user_id: str) -> List[Tuple[str, str, str, str, str, bytes]]:
    """
    Get all chunks for a specific user.
    
    Args:
        user_id: User identifier
        
    Returns:
        List of (chunk_id, user_id, source_type, source_id, text, embedding_blob) tuples
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT chunk_id, user_id, source_type, source_id, text, embedding
            FROM chunks
            WHERE user_id = ?
            ORDER BY source_type, source_id
        """, (user_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching chunks for user {user_id}: {e}")
        return []
    finally:
        conn.close()