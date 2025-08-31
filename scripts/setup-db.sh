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

# Resolve DB connection parameters from environment or defaults
PG_HOST=${PG_HOST:-127.0.0.1}
PG_PORT=${PG_PORT:-5432}
# Require explicit credentials; do not hardcode
PG_USER=${POSTGRES_USER:?POSTGRES_USER is required}
PG_PASSWORD=${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}
PG_DB=${POSTGRES_DB:?POSTGRES_DB is required}

# Check if PostgreSQL is running
check_postgres() {
    log_info "Checking PostgreSQL connection..."
    
    if command -v psql >/dev/null 2>&1; then
        if PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d postgres -c "SELECT 1;" >/dev/null 2>&1; then
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
            -e POSTGRES_USER="$PG_USER" \
            -e POSTGRES_PASSWORD="$PG_PASSWORD" \
            -e POSTGRES_DB="$PG_DB" \
            -p 5432:5432 \
            postgres:16
    fi
    
    # Wait for PostgreSQL to be ready
    log_info "Waiting for PostgreSQL to be ready..."
    for i in {1..60}; do
        if PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -c "SELECT 1;" >/dev/null 2>&1; then
            log_success "PostgreSQL is ready!"
            return 0
        fi
        sleep 1
    done
    
    log_error "PostgreSQL failed to start"
    return 1
}

# Ensure the current DB/Schema privileges allow running migrations as $PG_USER
ensure_privileges() {
    log_info "Ensuring database ownership and privileges for $PG_USER..."
    # Try to elevate role (harmless if already superuser)
    PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d postgres -v ON_ERROR_STOP=0 -c \
        "ALTER ROLE \"$PG_USER\" SUPERUSER CREATEDB CREATEROLE;" >/dev/null 2>&1 || true

    # Set DB and schema ownership to $PG_USER where possible
    PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d postgres -v ON_ERROR_STOP=0 -c \
        "ALTER DATABASE \"$PG_DB\" OWNER TO \"$PG_USER\";" >/dev/null 2>&1 || true
    PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=0 -c \
        "ALTER SCHEMA public OWNER TO \"$PG_USER\";" >/dev/null 2>&1 || true

    # Grant broad privileges to avoid permission issues during dev
    PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=0 -c \
        "GRANT ALL PRIVILEGES ON SCHEMA public TO \"$PG_USER\";" >/dev/null 2>&1 || true
    PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=0 -c \
        "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \"$PG_USER\";" >/dev/null 2>&1 || true
    PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=0 -c \
        "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO \"$PG_USER\";" >/dev/null 2>&1 || true
    PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=0 -c \
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO \"$PG_USER\";" >/dev/null 2>&1 || true
    PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=0 -c \
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO \"$PG_USER\";" >/dev/null 2>&1 || true

    # Fix alembic_version ownership if it already exists
    PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -tAc \
        "SELECT to_regclass('public.alembic_version') IS NOT NULL;" | grep -q t && \
        PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -v ON_ERROR_STOP=0 -c \
        "ALTER TABLE IF EXISTS public.alembic_version OWNER TO \"$PG_USER\"; GRANT ALL ON public.alembic_version TO \"$PG_USER\";" >/dev/null 2>&1 || true

    log_success "Privileges ensured for $PG_USER"
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

    # Ensure Alembic is available for migrations
    if ! python -c "import alembic" >/dev/null 2>&1; then
        log_info "Installing Alembic..."
        pip install alembic
    fi

    # If service requirements file exists, install to align versions
    if [ -f "services/auth-service/requirements.txt" ]; then
        log_info "Installing auth-service requirements (includes Alembic)..."
        pip install -r services/auth-service/requirements.txt || true
    fi
    
    log_success "Dependencies installed"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Set environment variables
    export ENVIRONMENT=${ENVIRONMENT:-development}
    # DB_PASSWORD intentionally not defaulted; use POSTGRES_PASSWORD if needed
    export DB_PASSWORD=${DB_PASSWORD:-$PG_PASSWORD}
    
    # Run the migration script
    python "$(dirname "$0")/migrate-db.py"
    
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
    # Ensure DB privileges before migrations
    ensure_privileges
    
    # Run migrations
    if run_migrations; then
        # Create service tables
        log_info "Creating service tables..."
        if [ -f "scripts/create-service-tables.py" ]; then
            python3 scripts/create-service-tables.py
            log_success "Service tables created successfully"
        else
            log_warning "create-service-tables.py not found, skipping service table creation"
        fi
        
        log_success "Database setup completed successfully!"
        echo ""
        log_info "📋 Database Information:"
        log_info "   Host: ${PG_HOST}:${PG_PORT}"
        log_info "   Database: ${PG_DB}"
        log_info "   User: ${PG_USER}"
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
