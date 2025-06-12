# CVisionary Retrieval Service

This is a high-performance FastAPI microservice designed to act as an intelligent intermediary for context retrieval. It orchestrates calls to the **CVisionary Embedding Service** to fetch semantically relevant text chunks, which are then used by upstream services (like a Generation Service) to build or edit resumes.

The service is built with a focus on robustness, observability, and clear separation of concerns.

- **FastAPI:** For the high-performance, asynchronous web framework.
- **Pydantic:** For robust data validation and clear API schema definitions.
- **HTTPX:** For efficient, asynchronous communication with downstream microservices.
- **Structured Logging:** For clear, machine-parsable logs essential for monitoring and debugging in a distributed environment.

## Core Functionality

The Retrieval Service provides two primary functionalities:

1.  **Full Context Retrieval:** Given a user ID and a target job description, it fetches the most relevant text chunks from the user's entire profile. This is ideal for generating a new resume from scratch.

2.  **Section-Specific Context Retrieval:** Given a user ID, a specific resume `section_id`, and a job description, it fetches relevant chunks that are explicitly filtered to that section. This is used when a user wants to edit or get suggestions for a single bullet point or section of their resume.

### Architectural Role

This service sits between a client (e.g., a Generation Service or a frontend application) and the Embedding Service. Its main responsibilities are:

-   **Abstraction:** It hides the complexity of the Embedding Service's API (e.g., knowing which `index_namespace` to query). The client only needs to specify *what* it wants (full context or section context), not *how* to get it.
-   **Orchestration:** It performs a two-step call to the Embedding Service: first to generate a vector embedding for the job description, and second to use that embedding to retrieve similar chunks.
-   **Resilience:** It implements retry logic with exponential backoff for transient network or server errors when communicating with the Embedding Service, making the overall system more robust.
-   **Validation:** It enforces strict input and output schemas, ensuring data integrity.



## Getting Started

### Prerequisites

-   Python 3.11+
-   A running instance of the **CVisionary Embedding Service**.

### Local Setup

1.  **Clone the repository and navigate to the service directory:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>/AI_Services/retrieval_service
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

4.  **Configure Environment Variables:**
    Create a `.env` file in the `retrieval_service` directory or set the following environment variables in your shell:

    ```env
    # REQUIRED: The full URL of the running Embedding Service
    EMBEDDING_SERVICE_URL="http://localhost:8001"

    # OPTIONAL: The default number of chunks to retrieve if not specified in the request
    DEFAULT_TOP_K="5"

    # OPTIONAL: Set to "DEBUG" for more verbose logging
    LOG_LEVEL="INFO"
    ```
    *Note: You may need to install `python-dotenv` (`pip install python-dotenv`) and add code to your `app.py` to load the `.env` file if you choose that method.*

5.  **Run the service:**
    ```bash
    uvicorn app:app --host 0.0.0.0 --port 8002 --reload
    ```
    The service will now be running at `http://localhost:8002`.

6.  **Access the API Documentation:**
    Navigate to `http://localhost:8002/docs` in your browser to see the interactive Swagger UI documentation.

## API Documentation

### Endpoints

#### 1. Retrieve Full Resume Context

Fetches the most relevant chunks from a user's entire profile based on a job description.

-   **Endpoint:** `POST /retrieve/full`
-   **Description:** Ideal for generating a new resume. It queries the `profile` namespace in the Embedding Service.
-   **cURL Example:**
    ```bash
    curl -X POST "http://localhost:8002/retrieve/full" \
    -H "Content-Type: application/json" \
    -d '{
      "user_id": "user-123",
      "job_description": "We are looking for a senior software engineer with experience in Python, FastAPI, and cloud-native technologies to lead our new platform team.",
      "top_k": 5
    }'
    ```

#### 2. Retrieve Section-Specific Context

Fetches the most relevant chunks filtered by a specific `section_id`.

-   **Endpoint:** `POST /retrieve/section`
-   **Description:** Ideal for editing or getting suggestions for a specific resume bullet. It queries the `resume_sections` namespace in the Embedding Service.
-   **cURL Example:**
    ```bash
    curl -X POST "http://localhost:8002/retrieve/section" \
    -H "Content-Type: application/json" \
    -d '{
      "user_id": "user-123",
      "section_id": "exp-bullet-45",
      "job_description": "We need someone who can engineer real-time data processing pipelines.",
      "top_k": 3
    }'
    ```

-   **Success Response (200 OK for both endpoints):**
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

-   `GET /health`: A simple health check endpoint for service monitoring. Returns `{"status": "ok", "service": "retrieval"}`.
-   `GET /`: Root endpoint with basic service information.

## Error Handling

The service provides structured JSON error responses.

-   **400 Bad Request:** The request body is invalid (e.g., empty `user_id`).
-   **404 Not Found:** The requested user or resource does not exist in the Embedding Service.
-   **422 Unprocessable Entity:** The request body is syntactically correct but semantically invalid (e.g., `top_k` is out of range).
-   **502 Bad Gateway:** The Retrieval Service could not get a valid response from the downstream Embedding Service after retries.
-   **500 Internal Server Error:** An unexpected error occurred within the Retrieval Service itself.

**Example Error Response:**
```json
{
  "error": "Failed to retrieve full context",
  "status_code": 502,
  "path": "/retrieve/full"
}
```

## Running Tests

The service includes a comprehensive suite of unit tests that mock downstream dependencies.

1.  **Install test dependencies:**
    ```bash
    pip install pytest pytest-asyncio
    ```

2.  **Run the test suite from the project root directory:**
    ```bash
    pytest AI_Services/retrieval_service/
    ```

## Project Structure

```
AI_Services/retrieval_service/
├── app.py                # Main FastAPI application, endpoints, and lifecycle events
├── schemas.py            # Pydantic models for API request/response validation
├── utils.py              # Logic for communicating with the Embedding Service
├── requirements.txt      # Python package dependencies
├── README.md             # This file
└── tests/                # Unit tests for the service
    ├── __init__.py
    ├── conftest.py       # Pytest fixtures and test setup
    ├── test_app.py       # Tests for the API endpoints
    ├── test_schemas.py   # Tests for the Pydantic models
    └── test_utils.py     # Tests for the utility functions
```