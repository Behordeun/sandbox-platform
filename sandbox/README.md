# 🇳🇬 Sandbox Services - Nigerian Digital Public Infrastructure

**The complete suite of Nigerian DPI services for developers and startups.** Everything you need to build world-class digital services for the Nigerian market.

## 🎯 What are Sandbox Services?

These are production-ready microservices that provide essential digital infrastructure capabilities for Nigerian businesses:

- **Identity Verification** - NIN and BVN verification
- **Communication** - SMS and voice services  
- **Intelligence** - AI-powered content and analysis
- **Data Storage** - Reliable database solutions

## 🏗️ Service Architecture

```plain text
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (Port 8080)                  │
│                 Single Entry Point for All Services         │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──────┐ ┌────▼────┐ ┌─────▼─────┐
│   Identity   │ │  Comms  │ │    AI     │
│   Services   │ │Services │ │ Services  │
└──────────────┘ └─────────┘ └───────────┘
│              │ │         │ │           │
│ NIN (8005)   │ │SMS(8003)│ │ AI (8002) │
│ BVN (8006)   │ │IVR(8004)│ │           │
│              │ │2Way(8007)│ │           │
└──────────────┘ └─────────┘ └───────────┘
```

## 🚀 Quick Start (All Services)

### Option 1: Start Everything at Once

```bash
# From sandbox-platform root directory
./sandbox-start.sh

# This starts all services automatically:
# - AI Service (8002)
# - SMS Service (8003) 
# - IVR Service (8004)
# - NIN Service (8005)
# - BVN Service (8006)
# - Two-Way SMS (8007)
```

### Option 2: Start Individual Services

```bash
# Navigate to sandbox directory
cd sandbox

# Start specific services
./start-all.sh

# Or start individually
cd nin && uvicorn app.main:app --port 8005 &
cd bvn && uvicorn app.main:app --port 8006 &
cd sms && uvicorn app.main:app --port 8003 &
```

### Verify All Services

```bash
# Check all services health
./check-services.sh

# Or check through API Gateway
curl http://localhost:8080/api/v1/services/health
```

## 📋 Service Overview

| Service | Port | Purpose | Key Features |
|---------|------|---------|--------------|
| **🆔 NIN Service** | 8005 | Nigerian Identity Verification | Real-time NIN validation, NIMC integration |
| **🏦 BVN Service** | 8006 | Banking Identity Verification | BVN validation, CBN compliance |
| **📱 SMS Service** | 8003 | SMS Messaging | Multi-network SMS, OTP delivery |
| **📞 IVR Service** | 8004 | Voice Response Systems | Interactive voice menus, Nigerian languages |
| **💬 Two-Way SMS** | 8007 | Interactive SMS | Bidirectional SMS, automated workflows |
| **🤖 AI Service** | 8002 | Content & Analysis | Nigerian-context AI, business intelligence |

## 🔧 Configuration

### Environment Setup

Each service has its own `.env.example` file. Copy and configure:

```bash
# For each service
cd service-directory
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Common Configuration

```env
# Dojah API (for NIN/BVN services)
DOJAH_API_KEY=your-dojah-api-key
DOJAH_APP_ID=your-dojah-app-id

# SMS Provider (for SMS services)
SMS_API_KEY=your-sms-api-key
SMS_SENDER_ID=YourBrand

# AI Provider (for AI service)
AI_API_KEY=your-ai-api-key
AI_MODEL=gpt-3.5-turbo
```

## 💡 Usage Examples

### Complete User Onboarding Flow

```bash
# 1. Register user
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "phone": "+2348012345678", ...}'

# 2. Send OTP for verification
curl -X POST http://localhost:8080/api/v1/sms/send \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"to": "+2348012345678", "message": "Your OTP: 123456"}'

# 3. Verify NIN
curl -X POST http://localhost:8080/api/v1/nin/verify \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"nin": "12345678901"}'

# 4. Verify BVN
curl -X POST http://localhost:8080/api/v1/bvn/verify \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"bvn": "12345678901"}'
```

### AI-Powered Customer Service

```bash
# Generate customer response
curl -X POST http://localhost:8080/api/v1/ai/generate \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "prompt": "Customer complaint about delayed transaction",
    "type": "customer_service_response",
    "context": "nigerian_banking"
  }'
```

## 📊 Monitoring & Analytics

### Service Health Monitoring

```bash
# Check all services
curl http://localhost:8080/api/v1/services/health

# Individual service health
curl http://localhost:8005/health  # NIN
curl http://localhost:8006/health  # BVN
curl http://localhost:8003/health  # SMS
```

### Usage Analytics

```bash
# Analyze service usage
python ../analyze-logs.py --all

# Service-specific analytics
python ../analyze-logs.py --user-activity | grep nin
python ../analyze-logs.py --user-activity | grep bvn
python ../analyze-logs.py --user-activity | grep sms
```

### Real-time Monitoring

```bash
# Monitor live activity
tail -f logs/nin.log
tail -f logs/bvn.log
tail -f logs/sms.log
tail -f logs/ai.log
```

## 🛠️ Development

### Running Tests

```bash
# Test all services
for service in nin bvn sms ai ivr two-way-sms; do
  cd $service && pytest tests/ -v && cd ..
done
```

### Adding New Services

1. Create service directory: `mkdir new-service`
2. Follow the existing service structure
3. Add to `start-all.sh` script
4. Update API Gateway routing
5. Add health check endpoint

### Service Dependencies

```bash
# Required for all services
pip install fastapi uvicorn pydantic

# Service-specific dependencies
# NIN/BVN: requests (for Dojah API)
# SMS: requests (for SMS providers)
# AI: openai anthropic (for AI providers)
```

## 🚀 Production Deployment

### Docker Deployment

```bash
# Build all service images
for service in nin bvn sms ai ivr two-way-sms; do
  cd $service && docker build -t sandbox-$service:1.0.0 . && cd ..
done

# Run with Docker Compose
docker-compose -f ../deployment/docker-compose/docker-compose.prod.yml up
```

### Kubernetes Deployment

```bash
# Deploy all services
cd ../deployment/helmfile
helmfile -e prod apply
```

## 📞 Support & Resources

### Service Documentation

- **[NIN Service](nin/README.md)** - Nigerian Identity Number verification
- **[BVN Service](bvn/README.md)** - Bank Verification Number validation
- **[SMS Service](sms/README.md)** - SMS messaging and notifications
- **[AI Service](ai/README.md)** - AI content generation and analysis
- **[IVR Service](ivr/README.md)** - Interactive Voice Response systems
- **[Two-Way SMS](two-way-sms/README.md)** - Bidirectional SMS communication

### Getting Help

- **Health Checks**: Each service has `/health` endpoint
- **API Documentation**: Each service has `/docs` endpoint
- **Logs**: Check `logs/` directory for service-specific logs
- **Monitoring**: Use `../analyze-logs.py` for usage analytics

### Best Practices

1. **Always authenticate** through the API Gateway
2. **Handle errors gracefully** - services can fail
3. **Monitor usage and costs** - especially for external APIs
4. **Use test modes** during development
5. **Cache results** where appropriate to reduce costs
6. **Follow Nigerian data protection** guidelines (NDPR)

---

**Ready to build the next generation of Nigerian digital services?** These sandbox services provide everything you need to create world-class applications for the Nigerian market.

*Powering Nigerian digital transformation* 🚀🇳🇬
