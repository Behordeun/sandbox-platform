#!/bin/bash

# Sandbox Platform Destruction Script
# WARNING: This will completely destroy the sandbox platform and all data

set -e

echo "🚨 DANGER: Sandbox Platform Destruction Script"
echo "=============================================="
echo ""
echo "This will:"
echo "  • Stop all running services"
echo "  • Kill all processes"
echo "  • Remove all containers"
echo "  • Delete all volumes and data"
echo "  • Clean up logs and temporary files"
echo ""

# Confirmation prompt
read -p "Are you sure you want to DESTROY the entire sandbox? (type 'DESTROY' to confirm): " confirmation
if [ "$confirmation" != "DESTROY" ]; then
    echo "❌ Destruction cancelled"
    exit 1
fi

echo ""
echo "🔥 Starting sandbox destruction..."

# Stop all Python services
echo "[INFO] Stopping all Python services..."
pkill -f "uvicorn.*sandbox" 2>/dev/null || echo "No Python services running"
pkill -f "python.*sandbox" 2>/dev/null || echo "No Python processes running"

# Kill processes on specific ports
echo "[INFO] Killing processes on service ports..."
for port in 8000 8001 8002 8003 8004 8005 8006 8007 8080; do
    lsof -ti :$port | xargs kill -9 2>/dev/null || echo "Port $port is free"
done

# Stop and remove Docker containers
echo "[INFO] Stopping and removing Docker containers..."
docker stop sandbox-postgres sandbox-redis 2>/dev/null || echo "No containers to stop"
docker rm sandbox-postgres sandbox-redis 2>/dev/null || echo "No containers to remove"

# Remove Docker volumes
echo "[INFO] Removing Docker volumes..."
docker volume rm sandbox-platform_postgres_data 2>/dev/null || echo "No postgres volume"
docker volume rm sandbox-platform_redis_data 2>/dev/null || echo "No redis volume"
docker volume rm sandbox-platform_prometheus_data 2>/dev/null || echo "No prometheus volume"
docker volume rm sandbox-platform_grafana_data 2>/dev/null || echo "No grafana volume"

# Clean up logs
echo "[INFO] Cleaning up logs..."
rm -rf logs/*.log logs/*.pid 2>/dev/null || echo "No logs to clean"

# Clean up Python cache
echo "[INFO] Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || echo "No Python cache"
find . -name "*.pyc" -delete 2>/dev/null || echo "No .pyc files"

# Clean up virtual environment
echo "[INFO] Removing virtual environment..."
rm -rf .venv 2>/dev/null || echo "No virtual environment"

# Clean up temporary files
echo "[INFO] Cleaning temporary files..."
rm -rf /tmp/auth-test*.log 2>/dev/null || echo "No temp files"

# Remove symlinks
echo "[INFO] Removing configuration symlinks..."
rm -f deployment/docker-compose/.env 2>/dev/null || echo "No symlinks"

echo ""
echo "💀 Sandbox Platform DESTROYED successfully!"
echo ""
echo "To rebuild the platform:"
echo "  1. Run: ./scripts/start-sandbox.sh"
echo "  2. Or: ./scripts/start-dev.sh"
echo ""