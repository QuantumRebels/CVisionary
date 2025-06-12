import sqlite3
from typing import List, Optional, Tuple
from datetime import datetime

DB_PATH = "embeddings.db"

def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory for easier data access"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initialize database tables if they don't exist."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("DROP TABLE IF EXISTS chunks") # For easier dev, remove in prod
        cursor.execute("DROP TABLE IF EXISTS users") # For easier dev, remove in prod
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                last_indexed_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                index_namespace TEXT NOT NULL, -- 'profile' or 'resume_sections'
                section_id TEXT, -- User-defined ID for resume sections
                source_type TEXT NOT NULL,
                source_id TEXT NOT NULL,
                text TEXT NOT NULL,
                embedding BLOB NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_user_id_namespace ON chunks (user_id, index_namespace)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_user_section_id ON chunks (user_id, section_id)")
        
        conn.commit()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def store_chunk(chunk_id: str, user_id: str, namespace: str, section_id: Optional[str],
                source_type: str, source_id: str, text: str, embedding_bytes: bytes) -> None:
    """Store a chunk with its embedding and metadata in the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        current_time = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT OR REPLACE INTO chunks 
            (chunk_id, user_id, index_namespace, section_id, source_type, source_id, text, embedding, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (chunk_id, user_id, namespace, section_id, source_type, source_id, text, embedding_bytes, current_time))
        conn.commit()
    except Exception as e:
        print(f"Error storing chunk {chunk_id}: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def get_all_chunks() -> List[sqlite3.Row]:
    """Retrieve all chunks from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chunks ORDER BY user_id, index_namespace")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching all chunks: {e}")
        return []
    finally:
        conn.close()

def get_chunk_by_id(chunk_id: str) -> Optional[sqlite3.Row]:
    """Retrieve a single chunk by its ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chunks WHERE chunk_id = ?", (chunk_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching chunk {chunk_id}: {e}")
        return None
    finally:
        conn.close()

def get_user_chunks_by_namespace(user_id: str, namespace: str) -> List[sqlite3.Row]:
    """Get all chunks for a specific user and namespace."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM chunks WHERE user_id = ? AND index_namespace = ?",
            (user_id, namespace)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching chunks for user {user_id} in namespace {namespace}: {e}")
        return []
    finally:
        conn.close()

def delete_user_chunks(user_id: str, namespace: str) -> int:
    """Delete all chunks for a user in a specific namespace. Returns number of rows deleted."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chunks WHERE user_id = ? AND index_namespace = ?", (user_id, namespace))
        deleted_rows = cursor.rowcount
        conn.commit()
        return deleted_rows
    except Exception as e:
        print(f"Error deleting chunks for user {user_id} in namespace {namespace}: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def delete_chunks_by_section_id(user_id: str, section_id: str) -> int:
    """Delete all chunks associated with a specific user and section_id. Returns number of rows deleted."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # This will only target 'resume_sections' namespace implicitly
        cursor.execute("DELETE FROM chunks WHERE user_id = ? AND section_id = ?", (user_id, section_id))
        deleted_rows = cursor.rowcount
        conn.commit()
        return deleted_rows
    except Exception as e:
        print(f"Error deleting chunks for section {section_id}: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def mark_user_indexed(user_id: str) -> None:
    """Mark a user as indexed with current timestamp."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        current_time = datetime.utcnow().isoformat()
        cursor.execute("INSERT OR REPLACE INTO users (user_id, last_indexed_at) VALUES (?, ?)", (user_id, current_time))
        conn.commit()
    except Exception as e:
        print(f"Error marking user {user_id} as indexed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()