#!/bin/bash

# Sandbox Platform - Centralized Startup Script
# Starts all services, sandbox components, and infrastructure

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

# Configuration
ENVIRONMENT=${ENVIRONMENT:-development}
SETUP_DB=${SETUP_DB:-true}
START_INFRASTRUCTURE=${START_INFRASTRUCTURE:-true}

# Service definitions
declare -A SERVICES=(
    ["auth-service"]="services/auth-service:8000"
    ["api-gateway"]="services/api-gateway:8080"
    ["config-service"]="config:8001"
    ["nin-service"]="sandbox/nin:8005"
    ["bvn-service"]="sandbox/bvn:8006"
    ["sms-service"]="sandbox/sms:8003"
    ["ai-service"]="sandbox/ai:8002"
)

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1
    fi
    return 0
}

# Function to start infrastructure
start_infrastructure() {
    log_info "Starting infrastructure services..."
    
    # Start PostgreSQL
    if ! docker ps --format "table {{.Names}}" | grep -q "^sandbox-postgres$"; then
        log_info "Starting PostgreSQL..."
        docker run -d \
            --name sandbox-postgres \
            -e POSTGRES_USER=sandbox_user \
            -e POSTGRES_PASSWORD=sandbox_password \
            -e POSTGRES_DB=sandbox_platform \
            -p 5432:5432 \
            postgres:14
        
        # Wait for PostgreSQL to be ready
        log_info "Waiting for PostgreSQL to be ready..."
        for i in {1..30}; do
            if psql -h localhost -U sandbox_user -d postgres -c "SELECT 1;" >/dev/null 2>&1; then
                break
            fi
            sleep 1
        done
    else
        log_info "PostgreSQL already running"
    fi
    
    # Start Redis
    if ! docker ps --format "table {{.Names}}" | grep -q "^sandbox-redis$"; then
        log_info "Starting Redis..."
        docker run -d \
            --name sandbox-redis \
            -p 6379:6379 \
            redis:7-alpine
    else
        log_info "Redis already running"
    fi
    
    log_success "Infrastructure services started"
}

# Function to setup database
setup_database() {
    if [ "$SETUP_DB" = "true" ]; then
        log_info "Setting up database..."
        if [ -f "./setup-db.sh" ]; then
            ./setup-db.sh
        else
            log_warning "setup-db.sh not found, skipping database setup"
        fi
    fi
}

# Function to install dependencies for a service
install_dependencies() {
    local service_path=$1
    local service_name=$2
    
    if [ -f "$service_path/requirements.txt" ]; then
        log_info "Installing dependencies for $service_name..."
        cd "$service_path"
        pip install -r requirements.txt >/dev/null 2>&1
        cd - >/dev/null
    fi
}

# Function to start a service
start_service() {
    local service_name=$1
    local service_info=$2
    local service_path=$(echo $service_info | cut -d: -f1)
    local service_port=$(echo $service_info | cut -d: -f2)
    
    log_info "Starting $service_name on port $service_port..."
    
    # Check if service directory exists
    if [ ! -d "$service_path" ]; then
        log_error "Service directory not found: $service_path"
        return 1
    fi
    
    # Check if port is available
    if ! check_port $service_port; then
        log_warning "Port $service_port is already in use, skipping $service_name"
        return 0
    fi
    
    # Install dependencies
    install_dependencies "$service_path" "$service_name"
    
    # Start service in background
    cd "$service_path"
    
    # Create logs directory if it doesn't exist
    mkdir -p ../../logs
    
    # Start service with uvicorn
    nohup uvicorn app.main:app \
        --host 0.0.0.0 \
        --port $service_port \
        --reload \
        > "../../logs/${service_name}.log" 2>&1 &
    
    local pid=$!
    echo $pid > "../../logs/${service_name}.pid"
    
    cd - >/dev/null
    
    # Wait a moment and check if service started
    sleep 2
    if kill -0 $pid 2>/dev/null; then
        log_success "$service_name started successfully (PID: $pid)"
    else
        log_error "$service_name failed to start"
        return 1
    fi
}

# Function to check service health
check_services() {
    log_info "Checking service health..."
    
    for service_name in "${!SERVICES[@]}"; do
        local service_info=${SERVICES[$service_name]}
        local service_port=$(echo $service_info | cut -d: -f2)
        
        if curl -s "http://localhost:$service_port/health" >/dev/null 2>&1; then
            log_success "$service_name is healthy"
        else
            log_warning "$service_name health check failed"
        fi
    done
}

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --no-db              Skip database setup"
    echo "  --no-infrastructure  Skip infrastructure startup"
    echo "  --check-only         Only check service health"
    echo "  --stop               Stop all services"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  ENVIRONMENT          Set environment (default: development)"
    echo "  SETUP_DB            Setup database (default: true)"
    echo "  START_INFRASTRUCTURE Start infrastructure (default: true)"
}

# Function to stop all services
stop_services() {
    log_info "Stopping all services..."
    
    # Stop application services
    for service_name in "${!SERVICES[@]}"; do
        local pid_file="logs/${service_name}.pid"
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if kill -0 $pid 2>/dev/null; then
                log_info "Stopping $service_name (PID: $pid)..."
                kill $pid
                rm -f "$pid_file"
            fi
        fi
    done
    
    # Stop infrastructure
    log_info "Stopping infrastructure..."
    docker stop sandbox-postgres sandbox-redis 2>/dev/null || true
    
    log_success "All services stopped"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-db)
            SETUP_DB=false
            shift
            ;;
        --no-infrastructure)
            START_INFRASTRUCTURE=false
            shift
            ;;
        --check-only)
            check_services
            exit 0
            ;;
        --stop)
            stop_services
            exit 0
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    log_info "🚀 Starting Sandbox Platform..."
    log_info "Environment: $ENVIRONMENT"
    echo "=================================================="
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        log_warning ".env file not found. Copying from template..."
        if [ -f ".env.template" ]; then
            cp .env.template .env
            log_info "Please edit .env file with your actual values"
        else
            log_error ".env.template not found. Please create .env file manually"
            exit 1
        fi
    fi
    
    # Export environment variables
    export ENVIRONMENT
    set -a
    source .env
    set +a
    
    # Start infrastructure
    if [ "$START_INFRASTRUCTURE" = "true" ]; then
        start_infrastructure
    fi
    
    # Setup database
    setup_database
    
    # Create logs directory
    mkdir -p logs
    
    # Start all services
    log_info "Starting application services..."
    for service_name in "${!SERVICES[@]}"; do
        start_service "$service_name" "${SERVICES[$service_name]}"
    done
    
    # Wait a moment for services to fully start
    sleep 5
    
    # Check service health
    check_services
    
    # Display summary
    echo ""
    log_success "🎉 Sandbox Platform started successfully!"
    echo ""
    log_info "📋 Service URLs:"
    for service_name in "${!SERVICES[@]}"; do
        local service_info=${SERVICES[$service_name]}
        local service_port=$(echo $service_info | cut -d: -f2)
        log_info "   $service_name: http://localhost:$service_port"
    done
    
    echo ""
    log_info "📊 API Documentation:"
    log_info "   API Gateway: http://localhost:8080/docs"
    log_info "   Auth Service: http://localhost:8000/docs"
    
    echo ""
    log_info "📝 Logs: ./logs/"
    log_info "🛑 To stop: ./start-sandbox.sh --stop"
    
    echo ""
    log_info "🚀 Platform is ready for development!"
}

# Run main function
main "$@"