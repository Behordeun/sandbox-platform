# API Gateway Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies for API Gateway
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

# Create non-root user for API Gateway
RUN adduser --disabled-password --gecos '' gatewayuser && chown -R gatewayuser:gatewayuser /app
USER gatewayuser

# Expose API Gateway port
EXPOSE 8080

# Health check for API Gateway
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://127.0.0.1:8080/health || exit 1

# Run the API Gateway
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
