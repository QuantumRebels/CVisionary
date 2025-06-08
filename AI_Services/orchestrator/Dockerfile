# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app

# Set the working directory in the container
WORKDIR ${APP_HOME}

# Install system dependencies (if any were needed, e.g., for certain Python packages)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir to reduce image size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
# This includes app.py, agent.py, tools.py, schemas.py
COPY . .

# Expose the port the app runs on (should match the port in uvicorn.run or .env)
# Defaulting to 8004 as per requirements
EXPOSE 8004

# Define the command to run the application using Uvicorn
# The host 0.0.0.0 makes the app accessible from outside the container
# The port should be configurable via an environment variable if needed, but defaults here
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8004"]
# A better CMD that allows environment variable for port:
# CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8004}
# Assuming app.py is the entry point and 'app' is the FastAPI instance within app.py
# The module is orchestrator.app, and the FastAPI instance is 'app'
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8004"]
