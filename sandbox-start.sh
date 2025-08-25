#!/bin/bash

echo "🇳🇬 Starting DPI Sandbox Backend..."

# Start infrastructure
cd services && ./start-infrastructure.sh

# Start platform services
./start-all.sh

# Start sandbox services
cd ../sandbox
if [ -f "start-all.sh" ]; then
    ./start-all.sh
else
    echo "⚠️  Sandbox services startup script not found"
fi

echo "✅ DPI Sandbox Backend Ready!"
echo "🔐 API Gateway: http://localhost:8080/docs"
echo "🆔 NIN Service: http://localhost:8005/docs"
echo "🏦 BVN Service: http://localhost:8006/docs"
echo "📱 SMS Service: http://localhost:8003/docs"
echo "🤖 AI Service: http://localhost:8002/docs"
echo "🔧 Auth Service: http://localhost:8000/docs"
echo ""
echo "🚀 Quick Commands:"
echo "  Health Check: ./check-services.sh"
echo "  API Testing: ./test-dpi-apis.sh"
echo "  Mock Data: python mock-data.py"
echo "  API Guide: cat DPI-API-GUIDE.md"