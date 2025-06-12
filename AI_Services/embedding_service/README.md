# CVisionary Embedding Service

This is a high-performance FastAPI microservice designed to generate, store, and retrieve vector embeddings for user profile data. It serves as a foundational component for semantic search, content recommendation, and other AI-powered features.

The service uses a powerful combination of technologies:
- **FastAPI:** For the high-performance, asynchronous web framework.
- **Sentence Transformers:** For state-of-the-art text embedding generation.
- **FAISS (Facebook AI Similarity Search):** For extremely fast, in-memory vector similarity searches.
- **SQLite:** For persistent storage of chunk metadata and embeddings, ensuring data durability.
- **Pydantic:** For robust data validation and clear API schema definitions.

## Core Concepts

Before using the API, it's crucial to understand a few key design principles of this service.

### 1. Hybrid Storage Model
The service uses two storage systems for different purposes:
- **SQLite (`embeddings.db`):** This is the **source of truth**. All text chunks, metadata, and embedding vectors are stored here permanently. This ensures that if the service restarts, no data is lost.
- **In-Memory FAISS Index:** This is a **high-speed cache** for the embedding vectors. On startup, the service reads all embeddings from SQLite and loads them into FAISS indices in RAM. This allows for millisecond-latency similarity searches, which would be too slow to perform directly on the database.

### 2. Namespaced Indices
To distinguish between different types of content, embeddings are stored in **namespaces**. Each user has their own set of indices, which are further divided into two main namespaces:

- `profile`: This namespace contains embeddings generated from a full, automated scan of a user's profile (experience, skills, projects, etc.). This data is considered relatively static.
- `resume_sections`: This namespace is specifically for embeddings generated from user-edited text, such as a custom resume bullet point or a rephrased project description. This data is dynamic and managed on a per-section basis.

This separation allows retrieval calls to target the correct set of embeddings—for example, searching for general profile context versus searching only within user-edited content.

### 3. Idempotent and Atomic Operations
The indexing endpoints are designed to be **idempotent**, meaning you can call them multiple times with the same input and get the same result without creating duplicate data.

- **Full Profile Indexing (`/index/profile/{user_id}`):** This is a **destructive** operation. It first deletes all existing chunks and the FAISS index for the user's `profile` namespace before creating new ones. This ensures the profile is always up-to-date.
- **Section Indexing (`/index/{user_id}/section`):** This is an "upsert" (update or insert) operation. It first deletes any existing chunks matching the provided `section_id` and then creates new ones. This is achieved by rebuilding the user's `resume_sections` FAISS index from the database after every change, guaranteeing consistency.

### 4. Text Chunking
Long text fields (like job descriptions) are automatically split into smaller, semantically coherent chunks of about 150 words. This is done using `nltk` to respect sentence boundaries, which improves the quality and relevance of search results.

## Getting Started

### Prerequisites
- Python 3.11+
- A virtual environment tool (e.g., `venv`, `conda`)

### Local Setup
1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: The first time you run the application, it may download the `nltk` 'punkt' tokenizer data.*

4.  **Run the service:**
    ```bash
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload
    ```
    The service will now be running at `http://localhost:8000`.

5.  **Access the API Documentation:**
    Navigate to `http://localhost:8000/docs` in your browser to see the interactive Swagger UI documentation.

## API Documentation

### Indexing Endpoints

#### 1. Index a Full User Profile
This endpoint fetches a user's profile from an external service, chunks the text, generates embeddings, and stores them in the `profile` namespace. **This is a destructive operation that replaces all previous profile data for the user.**

- **Endpoint:** `POST /index/profile/{user_id}`
- **Description:** Re-indexes the entire user profile.
- **cURL Example:**
  ```bash
  curl -X POST "http://localhost:8000/index/profile/user-123"
  ```
- **Success Response (200 OK):**
  ```json
  {
    "status": "Profile for user user-123 re-indexed successfully",
    "num_chunks": 25
  }
  ```

#### 2. Index a Resume Section
This endpoint adds or updates the embeddings for a specific, user-edited piece of text (e.g., a resume bullet). It uses a `section_id` to uniquely identify the content.

- **Endpoint:** `POST /index/{user_id}/section`
- **Description:** Adds or updates a specific section.
- **cURL Example:**
  ```bash
  curl -X POST "http://localhost:8000/index/user-123/section" \
  -H "Content-Type: application/json" \
  -d '{
    "section_id": "exp-bullet-45",
    "text": "Engineered a real-time data processing pipeline using Kafka and Flink, reducing analytics latency by 90%."
  }'
  ```
- **Success Response (200 OK):**
  ```json
  {
    "status": "Section exp-bullet-45 indexed successfully.",
    "section_id": "exp-bullet-45",
    "chunk_ids": ["a1b2c3d4-e5f6-...", "g7h8i9j0-k1l2-..."]
  }
  ```

#### 3. Delete a Resume Section
This endpoint removes all embeddings associated with a specific `section_id`.

- **Endpoint:** `DELETE /index/{user_id}/section/{section_id}`
- **Description:** Deletes all chunks for a given section.
- **cURL Example:**
  ```bash
  curl -X DELETE "http://localhost:8000/index/user-123/section/exp-bullet-45"
  ```
- **Success Response (200 OK):**
  ```json
  {
    "status": "Deleted 2 chunks for section exp-bullet-45.",
    "section_id": "exp-bullet-45"
  }
  ```

### Retrieval Endpoint

#### Retrieve Similar Chunks
This is the main search endpoint. It takes a query embedding and returns the most similar text chunks for a user. It can be configured to search different namespaces and filter by section.

- **Endpoint:** `POST /retrieve/{user_id}`
- **Description:** Searches for similar chunks based on a query embedding.
- **Request Body Fields:**
    - `query_embedding` (required): A 384-dimensional vector.
    - `top_k` (optional, default: 5): The number of results to return.
    - `index_namespace` (optional, default: `"profile"`): Either `"profile"` or `"resume_sections"`.
    - `filter_by_section_ids` (optional): A list of `section_id` strings to restrict the search to.

- **cURL Example 1 (Simple search in profile):**
  ```bash
  curl -X POST "http://localhost:8000/retrieve/user-123" \
  -H "Content-Type: application/json" \
  -d '{
    "query_embedding": [0.01, -0.05, ..., 0.02],
    "top_k": 3
  }'
  ```

- **cURL Example 2 (Filtered search in resume sections):**
  ```bash
  curl -X POST "http://localhost:8000/retrieve/user-123" \
  -H "Content-Type: application/json" \
  -d '{
    "query_embedding": [0.01, -0.05, ..., 0.02],
    "top_k": 2,
    "index_namespace": "resume_sections",
    "filter_by_section_ids": ["exp-bullet-45", "proj-desc-12"]
  }'
  ```

- **Success Response (200 OK):**
  ```json
  {
    "results": [
      {
        "chunk_id": "some-uuid-...",
        "user_id": "user-123",
        "index_namespace": "profile",
        "section_id": null,
        "source_type": "experience",
        "source_id": "0",
        "text": "Led a team of five engineers in the development of a cloud-native SaaS platform...",
        "score": 0.897,
        "created_at": "2023-10-27T10:00:00Z"
      }
    ]
  }
  ```

### Utility Endpoints

- `POST /embed`: Generates a normalized embedding for any given text.
- `GET /health`: A simple health check endpoint.

## Architectural Considerations & Limitations

### Concurrency and Scalability
The current implementation uses a global Python dictionary to hold the in-memory FAISS indices. This design is simple and very fast for a single process.

**CRITICAL:** This means the service **must be deployed as a single-worker process**. Running it with multiple workers (e.g., `uvicorn app:app --workers 4`) will lead to inconsistent state, as each worker would have its own separate, out-of-sync copy of the indices.

For scaling to multiple workers or nodes, the in-memory state would need to be externalized to a dedicated vector database like **Qdrant, Weaviate, or Pinecone**.

### Data Consistency
Consistency between the SQLite database and the in-memory FAISS index is maintained by rebuilding the FAISS index from the database on any write operation (e.g., indexing a section). This is a simple and robust strategy that avoids the complexity of surgical updates to the FAISS index and prevents state drift.

## Running Tests
To ensure the quality and correctness of the service, you can run the test suite.

```bash
pip install -r requirements.txt # Ensure test dependencies are installed
pytest
```

## Project Structure

```
.
├── __init__.py           # Module initializer
├── app.py                # Main FastAPI application, endpoints, and orchestration
├── chunking.py           # Text chunking and extraction logic
├── db.py                 # SQLite database schema and interaction functions
├── faiss_index.py        # In-memory FAISS index management
├── model.py              # Sentence Transformer model loading and embedding generation
├── schemas.py            # Pydantic models for API request/response validation
└── requirements.txt      # Python package dependencies
```