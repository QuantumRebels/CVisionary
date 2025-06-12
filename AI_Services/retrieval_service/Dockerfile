# CVisionary Retrieval Service Dockerfile
# Production-ready container for Python 3.11 FastAPI service

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for httpx and potential future needs
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose service port
EXPOSE 8002

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Environment variables documentation
# EMBEDDING_SERVICE_URL - Required: Base URL of the Embedding Service
# DEFAULT_TOP_K - Optional: Default number of chunks to retrieve (default: 5)
# LOG_LEVEL - Optional: Logging level INFO or DEBUG (default: INFO)

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "1"]