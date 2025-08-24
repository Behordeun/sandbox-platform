#!/bin/bash

# Platform Services - Stop Infrastructure Script
# This script stops infrastructure services (databases, redis)

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to stop and remove container
stop_container() {
    local container_name=$1
    
    if docker ps -q -f name="$container_name" | grep -q .; then
        log_info "Stopping $container_name..."
        docker stop "$container_name" > /dev/null
        docker rm "$container_name" > /dev/null
        log_success "$container_name stopped and removed"
    else
        log_error "$container_name not running"
    fi
}

log_info "Stopping infrastructure services..."

# Stop infrastructure containers
stop_container "sandbox-postgres"
stop_container "sandbox-redis"
stop_container "sandbox-mongo"

log_success "All infrastructure services stopped!"

# Clean up volumes if requested
if [ "$1" = "--clean-volumes" ]; then
    log_info "Cleaning up Docker volumes..."
    docker volume prune -f > /dev/null 2>&1
    log_success "Docker volumes cleaned"
fi