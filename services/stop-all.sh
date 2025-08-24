#!/bin/bash

# Platform Services - Stop All Services Script
# This script stops all running platform maintenance services

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

# Function to stop a service
stop_service() {
    local service_name=$1
    
    if [ -f "logs/${service_name}.pid" ]; then
        local pid=$(cat "logs/${service_name}.pid")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            log_success "$service_name stopped (PID: $pid)"
        else
            log_error "$service_name process not found (PID: $pid)"
        fi
        rm -f "logs/${service_name}.pid"
    else
        log_error "No PID file found for $service_name"
    fi
}

log_info "Stopping all platform services..."

# Stop platform services
stop_service "auth-service"
stop_service "api-gateway"
stop_service "rate-limiter"
stop_service "health-service"
stop_service "logging"
stop_service "monitoring"

log_success "All platform services stopped!"

# Clean up logs if requested
if [ "$1" = "--clean-logs" ]; then
    log_info "Cleaning up log files..."
    rm -f logs/*.log
    log_success "Log files cleaned"
fi