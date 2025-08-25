#!/bin/bash

# Platform Services - Start All Services Script
# This script starts all platform maintenance services for local development

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

# Function to start a service
start_service() {
    local service_name=$1
    local port=$2
    
    if [ -d "$service_name" ]; then
        log_info "Starting $service_name on port $port..."
        cd "$service_name"
        
        # Check if requirements.txt exists and install dependencies
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt > /dev/null 2>&1
        fi
        
        # Start the service in background
        uvicorn app.main:app --reload --port "$port" > "../logs/${service_name}.log" 2>&1 &
        echo $! > "../logs/${service_name}.pid"
        
        cd ..
        log_success "$service_name started on port $port (PID: $(cat logs/${service_name}.pid))"
    else
        log_warning "$service_name directory not found, skipping..."
    fi
}

# Create logs directory
mkdir -p logs

log_info "Starting all platform services..."

# Start platform services
start_service "auth-service" 8000
start_service "api-gateway" 8080
start_service "rate-limiter" 8008
start_service "health-service" 8009
start_service "logging" 8010
start_service "monitoring" 8011

log_success "All platform services started!"
log_info "Service logs are available in the logs/ directory"
log_info "To stop all services, run: ./stop-all.sh"

# Display service status
echo ""
log_info "Platform Service Status:"
echo "Auth Service:      http://localhost:8000/health"
echo "API Gateway:       http://localhost:8080/health"
echo "Rate Limiter:      http://localhost:8008/health"
echo "Health Service:    http://localhost:8009/health"
echo "Logging Service:   http://localhost:8010/health"
echo "Monitoring:        http://localhost:8011/health"