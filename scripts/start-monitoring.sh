#!/bin/bash

echo "🚀 Starting Sandbox Platform Monitoring Stack..."

cd deployment/monitoring

# Start Prometheus and Grafana
docker-compose up -d

echo "✅ Monitoring stack started!"
echo ""
echo "📊 Access URLs:"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana:    http://localhost:3001"
echo ""
echo "⏳ Wait 30 seconds for services to initialize, then access Grafana"
