#!/bin/bash

echo "🚀 Migrating to new sandbox platform structure..."

# Create new directory structure
echo "📁 Creating new directory structure..."
mkdir -p sandbox/{ai,sms,ivr,nin,bvn,two-way-sms,data-stores/{postgres,mongo}}
mkdir -p services/{rate-limiter,health-service,logging,monitoring,redis}
mkdir -p config

# Move existing services
echo "📦 Moving existing services..."
if [ -d "services/config-service" ]; then
    mv services/config-service/* config/ 2>/dev/null || true
    rmdir services/config-service 2>/dev/null || true
fi

if [ -d "services/sms" ]; then
    mv services/sms/* sandbox/sms/ 2>/dev/null || true
    rmdir services/sms 2>/dev/null || true
fi

echo "✅ Migration completed!"
echo "📋 New structure:"
echo "   /sandbox     → main offerings (ai, sms, ivr, nin, bvn, two-way-sms, data-stores)"
echo "   /services    → platform maintenance (auth, gateway, rate-limiter, health, logging, monitoring, redis)"
echo "   /config      → centralized configuration"
echo "   /deployment  → deployment configurations"

echo ""
echo "🔧 Next steps:"
echo "1. Update your docker-compose files to reflect new paths"
echo "2. Update Kubernetes manifests and Helm charts"
echo "3. Update CI/CD pipelines"
echo "4. Test all services with new structure"