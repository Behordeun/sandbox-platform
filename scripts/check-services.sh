#!/bin/bash

echo "🔍 DPI Sandbox Service Health Check"
echo "==================================="

services=(
    "Auth Service:http://127.0.0.1:8000/health"
    "API Gateway:http://127.0.0.1:8080/health"
    "NIN Service:http://127.0.0.1:8005/health"
    "BVN Service:http://127.0.0.1:8006/health"
    "SMS Service:http://127.0.0.1:8003/health"
    "AI Service:http://127.0.0.1:8002/health"
)

all_healthy=true

for service in "${services[@]}"; do
    name=$(echo "$service" | cut -d: -f1)
    url=$(echo "$service" | cut -d: -f2-)
    
    printf "%-15s " "$name:"
    
    if response=$(curl -s -w "%{http_code}" "$url" -o /dev/null); then
        if [ "$response" = "200" ]; then
            echo "✅ Healthy"
        else
            echo "❌ Unhealthy (HTTP $response)"
            all_healthy=false
        fi
    else
        echo "❌ Not responding"
        all_healthy=false
    fi
done

echo ""
if [ "$all_healthy" = true ]; then
    echo "🎉 All DPI services are healthy!"
    echo "🚀 Ready for development: http://127.0.0.1:8080/docs"
else
    echo "⚠️  Some services need attention"
    echo "💡 Run: ./sandbox-start.sh to start missing services"
fi