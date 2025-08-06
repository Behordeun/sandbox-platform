#!/bin/bash

# Sandbox Platform - Build Docker Images Script
# This script builds all service Docker images with proper tagging

set -e

# Configuration
DOCKER_REGISTRY=${DOCKER_REGISTRY:-""}
IMAGE_TAG=${IMAGE_TAG:-"latest"}
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Function to build a service image
build_service() {
    local service_name=$1
    local service_path=$2
    local image_name="${DOCKER_REGISTRY}sandbox-${service_name}"
    
    log_info "Building ${service_name} image..."
    
    # Check if Dockerfile exists
    if [ ! -f "${service_path}/Dockerfile" ]; then
        log_error "Dockerfile not found in ${service_path}"
        return 1
    fi
    
    # Build the image
    docker build \
        --build-arg BUILD_DATE="${BUILD_DATE}" \
        --build-arg GIT_COMMIT="${GIT_COMMIT}" \
        --tag "${image_name}:${IMAGE_TAG}" \
        --tag "${image_name}:latest" \
        "${service_path}"
    
    if [ $? -eq 0 ]; then
        log_success "Successfully built ${image_name}:${IMAGE_TAG}"
        
        # Show image size
        local image_size=$(docker images "${image_name}:${IMAGE_TAG}" --format "table {{.Size}}" | tail -n 1)
        log_info "Image size: ${image_size}"
    else
        log_error "Failed to build ${image_name}:${IMAGE_TAG}"
        return 1
    fi
}

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -r, --registry REGISTRY    Docker registry prefix (default: empty)"
    echo "  -t, --tag TAG             Image tag (default: latest)"
    echo "  -s, --service SERVICE     Build specific service only"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Services:"
    echo "  auth-service             Authentication service"
    echo "  api-gateway              API Gateway service"
    echo "  config-service           Configuration service"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Build all services with default settings"
    echo "  $0 -r myregistry/ -t v1.0.0         # Build with custom registry and tag"
    echo "  $0 -s auth-service                   # Build only auth service"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--registry)
            DOCKER_REGISTRY="$2/"
            shift 2
            ;;
        -t|--tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        -s|--service)
            SPECIFIC_SERVICE="$2"
            shift 2
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

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"

log_info "Starting Docker image build process..."
log_info "Registry: ${DOCKER_REGISTRY:-"(none)"}"
log_info "Tag: ${IMAGE_TAG}"
log_info "Build Date: ${BUILD_DATE}"
log_info "Git Commit: ${GIT_COMMIT}"
log_info "Project Root: ${PROJECT_ROOT}"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    log_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Define services to build
declare -A SERVICES=(
    ["auth-service"]="${PROJECT_ROOT}/services/auth-service"
    ["api-gateway"]="${PROJECT_ROOT}/services/api-gateway"
    ["config-service"]="${PROJECT_ROOT}/services/config-service"
)

# Build specific service or all services
if [ -n "${SPECIFIC_SERVICE}" ]; then
    if [ -z "${SERVICES[${SPECIFIC_SERVICE}]}" ]; then
        log_error "Unknown service: ${SPECIFIC_SERVICE}"
        log_info "Available services: ${!SERVICES[@]}"
        exit 1
    fi
    
    log_info "Building specific service: ${SPECIFIC_SERVICE}"
    build_service "${SPECIFIC_SERVICE}" "${SERVICES[${SPECIFIC_SERVICE}]}"
else
    log_info "Building all services..."
    
    # Build all services
    for service in "${!SERVICES[@]}"; do
        build_service "${service}" "${SERVICES[${service}]}"
        echo ""
    done
fi

# Display summary
log_success "Build process completed!"
log_info "Built images:"
for service in "${!SERVICES[@]}"; do
    if [ -n "${SPECIFIC_SERVICE}" ] && [ "${service}" != "${SPECIFIC_SERVICE}" ]; then
        continue
    fi
    
    image_name="${DOCKER_REGISTRY}sandbox-${service}:${IMAGE_TAG}"
    if docker images "${image_name}" --format "table {{.Repository}}:{{.Tag}}" | grep -q "${image_name}"; then
        log_success "  ${image_name}"
    fi
done

log_info "To push images to registry, run: ./push-images.sh"

