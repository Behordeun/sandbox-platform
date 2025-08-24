#!/bin/bash

# Sandbox Platform - Start All Services Script
# This script starts all sandbox services for local development

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

log_info "Starting all sandbox services..."

# Start services
start_service "ai" 8002
start_service "sms" 8003
start_service "ivr" 8004
start_service "nin" 8005
start_service "bvn" 8006
start_service "two-way-sms" 8007

log_success "All services started!"
log_info "Service logs are available in the logs/ directory"
log_info "To stop all services, run: ./stop-all.sh"

# Display service status
echo ""
log_info "Service Status:"
echo "AI Service:      http://localhost:8002/health"
echo "SMS Service:     http://localhost:8003/health"
echo "IVR Service:     http://localhost:8004/health"
echo "NIN Service:     http://localhost:8005/health"
echo "BVN Service:     http://localhost:8006/health"
echo "Two-Way SMS:     http://localhost:8007/health"
