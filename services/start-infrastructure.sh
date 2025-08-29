#!/bin/bash

# Platform Services - Start Infrastructure Script
# This script starts infrastructure services (databases, redis) using Docker

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    log_warning "Docker is not running. Please start Docker and try again."
    exit 1
fi

log_info "Starting infrastructure services..."

# Start PostgreSQL
log_info "Starting PostgreSQL..."
docker run -d \
  --name sandbox-postgres \
  -e POSTGRES_DB=sandbox_db \
  -e POSTGRES_USER=sandbox_user \
  -e POSTGRES_PASSWORD=sandbox_password \
  -p 5432:5432 \
  postgres:16 || log_warning "PostgreSQL container may already be running"

# Start Redis
log_info "Starting Redis..."
docker run -d \
  --name sandbox-redis \
  -p 6379:6379 \
  redis:7-alpine || log_warning "Redis container may already be running"

# Start MongoDB
log_info "Starting MongoDB..."
docker run -d \
  --name sandbox-mongo \
  -e MONGO_INITDB_ROOT_USERNAME=sandbox_user \
  -e MONGO_INITDB_ROOT_PASSWORD=sandbox_password \
  -e MONGO_INITDB_DATABASE=sandbox_db \
  -p 27017:27017 \
  mongo:6 || log_warning "MongoDB container may already be running"

# Wait for services to be ready
log_info "Waiting for services to be ready..."
sleep 10

log_success "Infrastructure services started!"
echo ""
log_info "Infrastructure Status:"
echo "PostgreSQL:  127.0.0.1:5432 (sandbox_user/sandbox_password)"
echo "Redis:       127.0.0.1:6379"
echo "MongoDB:     127.0.0.1:27017 (sandbox_user/sandbox_password)"
