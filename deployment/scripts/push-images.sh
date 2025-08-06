#!/bin/bash

# Sandbox Platform - Push Docker Images Script
# This script pushes all service Docker images to the registry

set -e

# Configuration
DOCKER_REGISTRY=${DOCKER_REGISTRY:-""}
IMAGE_TAG=${IMAGE_TAG:-"latest"}

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

# Function to push a service image
push_service() {
    local service_name=$1
    local image_name="${DOCKER_REGISTRY}sandbox-${service_name}"
    
    log_info "Pushing ${service_name} image..."
    
    # Check if image exists locally
    if ! docker images "${image_name}:${IMAGE_TAG}" --format "table {{.Repository}}:{{.Tag}}" | grep -q "${image_name}:${IMAGE_TAG}"; then
        log_error "Image ${image_name}:${IMAGE_TAG} not found locally. Please build it first."
        return 1
    fi
    
    # Push the tagged image
    docker push "${image_name}:${IMAGE_TAG}"
    
    if [ $? -eq 0 ]; then
        log_success "Successfully pushed ${image_name}:${IMAGE_TAG}"
        
        # Also push latest tag if not already latest
        if [ "${IMAGE_TAG}" != "latest" ]; then
            docker push "${image_name}:latest"
            log_success "Successfully pushed ${image_name}:latest"
        fi
    else
        log_error "Failed to push ${image_name}:${IMAGE_TAG}"
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
    echo "  -s, --service SERVICE     Push specific service only"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Services:"
    echo "  auth-service             Authentication service"
    echo "  api-gateway              API Gateway service"
    echo "  config-service           Configuration service"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Push all services with default settings"
    echo "  $0 -r myregistry/ -t v1.0.0         # Push with custom registry and tag"
    echo "  $0 -s auth-service                   # Push only auth service"
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

log_info "Starting Docker image push process..."
log_info "Registry: ${DOCKER_REGISTRY:-"(Docker Hub)"}"
log_info "Tag: ${IMAGE_TAG}"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    log_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if user is logged in to Docker registry
if ! docker info | grep -q "Username:"; then
    log_warning "You may not be logged in to Docker registry."
    log_info "Run 'docker login' if push fails."
fi

# Define services to push
SERVICES=("auth-service" "api-gateway" "config-service")

# Push specific service or all services
if [ -n "${SPECIFIC_SERVICE}" ]; then
    if [[ ! " ${SERVICES[@]} " =~ " ${SPECIFIC_SERVICE} " ]]; then
        log_error "Unknown service: ${SPECIFIC_SERVICE}"
        log_info "Available services: ${SERVICES[@]}"
        exit 1
    fi
    
    log_info "Pushing specific service: ${SPECIFIC_SERVICE}"
    push_service "${SPECIFIC_SERVICE}"
else
    log_info "Pushing all services..."
    
    # Push all services
    for service in "${SERVICES[@]}"; do
        push_service "${service}"
        echo ""
    done
fi

# Display summary
log_success "Push process completed!"
log_info "Pushed images:"
for service in "${SERVICES[@]}"; do
    if [ -n "${SPECIFIC_SERVICE}" ] && [ "${service}" != "${SPECIFIC_SERVICE}" ]; then
        continue
    fi
    
    image_name="${DOCKER_REGISTRY}sandbox-${service}:${IMAGE_TAG}"
    log_success "  ${image_name}"
    
    if [ "${IMAGE_TAG}" != "latest" ]; then
        log_success "  ${DOCKER_REGISTRY}sandbox-${service}:latest"
    fi
done

