#!/bin/bash

# Sandbox Platform - Stop Script
# Stops all running services and infrastructure

set -e

# Colors for output
RED='\033[0;31m'
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

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Service definitions
declare -A SERVICES=(
    ["auth-service"]="8000"
    ["api-gateway"]="8080"
    ["config-service"]="8001"
    ["nin-service"]="8005"
    ["bvn-service"]="8006"
    ["sms-service"]="8003"
    ["ai-service"]="8002"
)

# Function to stop services
stop_services() {
    log_info "Stopping application services..."
    
    # Stop services by PID files
    for service_name in "${!SERVICES[@]}"; do
        local pid_file="logs/${service_name}.pid"
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if kill -0 $pid 2>/dev/null; then
                log_info "Stopping $service_name (PID: $pid)..."
                kill $pid
                rm -f "$pid_file"
                log_success "$service_name stopped"
            else
                log_warning "$service_name was not running"
                rm -f "$pid_file"
            fi
        else
            # Try to kill by port
            local port=${SERVICES[$service_name]}
            local pid=$(lsof -ti:$port 2>/dev/null || true)
            if [ -n "$pid" ]; then
                log_info "Stopping $service_name on port $port (PID: $pid)..."
                kill $pid
                log_success "$service_name stopped"
            fi
        fi
    done
}

# Function to stop infrastructure
stop_infrastructure() {
    log_info "Stopping infrastructure services..."
    
    # Stop Docker containers
    if docker ps --format "table {{.Names}}" | grep -q "^sandbox-postgres$"; then
        log_info "Stopping PostgreSQL..."
        docker stop sandbox-postgres
        log_success "PostgreSQL stopped"
    fi
    
    if docker ps --format "table {{.Names}}" | grep -q "^sandbox-redis$"; then
        log_info "Stopping Redis..."
        docker stop sandbox-redis
        log_success "Redis stopped"
    fi
}

# Main execution
main() {
    log_info "🛑 Stopping Sandbox Platform..."
    echo "=================================================="
    
    # Stop application services
    stop_services
    
    # Stop infrastructure
    stop_infrastructure
    
    # Clean up log files if requested
    if [ "$1" = "--clean" ]; then
        log_info "Cleaning up log files..."
        rm -rf logs/*.log
        log_success "Log files cleaned"
    fi
    
    log_success "🎉 Sandbox Platform stopped successfully!"
    
    if [ "$1" != "--clean" ]; then
        log_info "💡 Use --clean flag to remove log files"
    fi
}

# Run main function
main "$@"