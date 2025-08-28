# AI Service Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Copy root .env file for centralized configuration
COPY ../../.env ./.env

# Create non-root user for AI service
RUN adduser --disabled-password --gecos '' aiuser && chown -R aiuser:aiuser /app
USER aiuser

# Expose AI service port
EXPOSE 8002

# Health check for AI service
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Run the AI service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]