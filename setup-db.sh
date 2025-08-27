#!/bin/bash

# Sandbox Platform - Database Setup Script
# Sets up PostgreSQL database and runs all migrations

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

# Check if PostgreSQL is running
check_postgres() {
    log_info "Checking PostgreSQL connection..."
    
    if command -v psql >/dev/null 2>&1; then
        if psql -h localhost -U sandbox_user -d postgres -c "SELECT 1;" >/dev/null 2>&1; then
            log_success "PostgreSQL is running and accessible"
            return 0
        fi
    fi
    
    log_warning "PostgreSQL not accessible. Starting with Docker..."
    return 1
}

# Start PostgreSQL with Docker
start_postgres_docker() {
    log_info "Starting PostgreSQL with Docker..."
    
    # Check if container already exists
    if docker ps -a --format "table {{.Names}}" | grep -q "^sandbox-postgres$"; then
        log_info "PostgreSQL container exists, starting it..."
        docker start sandbox-postgres
    else
        log_info "Creating new PostgreSQL container..."
        docker run -d \
            --name sandbox-postgres \
            -e POSTGRES_USER=sandbox_user \
            -e POSTGRES_PASSWORD=sandbox_password \
            -e POSTGRES_DB=sandbox_platform \
            -p 5432:5432 \
            postgres:14
    fi
    
    # Wait for PostgreSQL to be ready
    log_info "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if psql -h localhost -U sandbox_user -d postgres -c "SELECT 1;" >/dev/null 2>&1; then
            log_success "PostgreSQL is ready!"
            return 0
        fi
        sleep 1
    done
    
    log_error "PostgreSQL failed to start"
    return 1
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Install psycopg2 for database operations
    if ! python -c "import psycopg2" >/dev/null 2>&1; then
        log_info "Installing psycopg2-binary..."
        pip install psycopg2-binary
    fi
    
    # Install PyYAML for configuration
    if ! python -c "import yaml" >/dev/null 2>&1; then
        log_info "Installing PyYAML..."
        pip install PyYAML
    fi
    
    log_success "Dependencies installed"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Set environment variables
    export ENVIRONMENT=${ENVIRONMENT:-development}
    export DB_PASSWORD=${DB_PASSWORD:-sandbox_password}
    
    # Run the migration script
    python migrate-db.py
    
    if [ $? -eq 0 ]; then
        log_success "Database migrations completed successfully"
        return 0
    else
        log_error "Database migrations failed"
        return 1
    fi
}

# Main setup function
main() {
    log_info "🗄️  Sandbox Platform - Database Setup"
    echo "=================================================="
    
    # Install dependencies
    install_dependencies
    
    # Check PostgreSQL or start with Docker
    if ! check_postgres; then
        if ! start_postgres_docker; then
            log_error "Failed to start PostgreSQL"
            exit 1
        fi
    fi
    
    # Run migrations
    if run_migrations; then
        log_success "Database setup completed successfully!"
        echo ""
        log_info "📋 Database Information:"
        log_info "   Host: localhost:5432"
        log_info "   Database: sandbox_platform"
        log_info "   User: sandbox_user"
        log_info "   Tables: Prefixed by service (auth_, config_, nin_, etc.)"
        echo ""
        log_info "🚀 You can now start your services!"
    else
        log_error "Database setup failed"
        exit 1
    fi
}

# Run main function
main "$@"