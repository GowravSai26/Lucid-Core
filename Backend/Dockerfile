FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency file
COPY Backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY Backend /app/Backend

# Environment variables for FastAPI
ENV PYTHONPATH=/app

# Default command (can be overridden by docker-compose)
CMD ["uvicorn", "Backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
