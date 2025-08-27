#!/bin/bash

# Sandbox Platform Development Startup Script

set -e

echo "🚀 Starting Sandbox Platform Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your actual configuration values"
fi

# Start infrastructure services
echo "🐘 Starting PostgreSQL and Redis..."
docker-compose -f deployment/docker-compose/docker-compose.dev.yml up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are healthy
echo "🔍 Checking service health..."
docker-compose -f deployment/docker-compose/docker-compose.dev.yml ps

echo "✅ Infrastructure services started successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Start Auth Service: cd services/auth-service && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000"
echo "2. Start Config Service: cd services/config-service && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8001"
echo "3. Start API Gateway: cd services/api-gateway && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8080"
echo ""
echo "🌐 Access points:"
echo "- API Gateway: http://localhost:8080"
echo "- Auth Service: http://localhost:8000"
echo "- Config Service: http://localhost:8001"
echo "- PostgreSQL: localhost:5432"
echo "- Redis: localhost:6379"