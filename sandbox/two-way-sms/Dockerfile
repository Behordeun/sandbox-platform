# Two-Way SMS Service Dockerfile
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

# Create non-root user for Two-Way SMS service
RUN adduser --disabled-password --gecos '' twowaysmsuser && chown -R twowaysmsuser:twowaysmsuser /app
USER twowaysmsuser

# Expose Two-Way SMS service port
EXPOSE 8007

# Health check for Two-Way SMS service
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8007/health || exit 1

# Run the Two-Way SMS service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"]