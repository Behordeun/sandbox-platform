#!/bin/bash

# Platform Services - Development Setup Script
# This script sets up the complete development environment

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

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --infrastructure-only    Start only infrastructure services"
    echo "  --services-only         Start only platform services"
    echo "  --help                  Show this help message"
    echo ""
    echo "Default: Start infrastructure first, then platform services"
}

# Parse command line arguments
INFRASTRUCTURE_ONLY=false
SERVICES_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --infrastructure-only)
            INFRASTRUCTURE_ONLY=true
            shift
            ;;
        --services-only)
            SERVICES_ONLY=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            log_warning "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

log_info "Setting up development environment..."

# Start infrastructure services
if [ "$SERVICES_ONLY" = false ]; then
    log_info "Starting infrastructure services..."
    ./start-infrastructure.sh
    echo ""
fi

# Start platform services
if [ "$INFRASTRUCTURE_ONLY" = false ]; then
    log_info "Starting platform services..."
    ./start-all.sh
    echo ""
fi

log_success "Development environment setup complete!"
echo ""
log_info "Quick Commands:"
echo "  Stop all services:     ./stop-all.sh"
echo "  Stop infrastructure:   ./stop-infrastructure.sh"
echo "  View logs:            tail -f logs/*.log"
echo "  API Gateway:          http://127.0.0.1:8080/docs"
echo "  Auth Service:         http://127.0.0.1:8000/docs"