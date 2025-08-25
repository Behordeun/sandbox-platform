# 🚀 Sandbox API Gateway - Your Gateway to Nigerian DPI Services

**The single entry point to all Nigerian Digital Public Infrastructure (DPI) services.** This API Gateway is specifically designed for Nigerian developers and startups to easily access identity verification, SMS, AI, and other essential services through one unified interface.

## 🎯 What is the API Gateway?

Think of the API Gateway as the **front door** to all DPI services. Instead of connecting to multiple services individually, you connect to one gateway that:
- **Routes your requests** to the right service (NIN, BVN, SMS, AI, etc.)
- **Handles authentication** so you don't need to manage tokens for each service
- **Monitors usage** and provides analytics on your API consumption
- **Protects against abuse** with built-in rate limiting and security
- **Provides consistent responses** across all services

## ✨ Key Features for Nigerian Developers

### 🔐 **Unified Authentication**
- Single JWT token works across all services
- Nigerian phone number validation (+234 format)
- OAuth2 support for enterprise applications

### 🇳🇬 **Nigerian DPI Services**
- **NIN Verification**: Verify National Identity Numbers
- **BVN Verification**: Validate Bank Verification Numbers  
- **SMS Services**: Send messages to Nigerian phone numbers
- **AI Services**: Content generation and data analysis
- **IVR Services**: Interactive Voice Response systems

### 📊 **Built-in Analytics**
- Track your API usage patterns
- Monitor service performance
- Security event detection
- User engagement metrics

### 🛡️ **Enterprise Security**
- Rate limiting (100 requests/minute by default)
- Request logging and audit trails
- Circuit breaker for service reliability
- CORS protection for web applications

## 🚀 Quick Start Guide (5 Minutes)

### Step 1: Start the Gateway
```bash
# From the sandbox-platform root directory
cd services/api-gateway

# Install dependencies
pip install -r requirements.txt

# Start the gateway
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Step 2: Verify It's Running
```bash
# Check gateway health
curl http://localhost:8080/health

# Expected response:
{
  "status": "healthy",
  "service": "Sandbox API Gateway",
  "version": "1.0.0"
}
```

### Step 3: Explore the API Documentation
Open your browser and go to: **http://localhost:8080/docs**

This interactive documentation shows all available endpoints and lets you test them directly!

### Step 4: Get Your First Token
```bash
# Register a new user
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@fintech.ng",
    "username": "dev_user",
    "password": "SecurePass123",
    "first_name": "Developer",
    "last_name": "User",
    "phone_number": "+2348012345678"
  }'

# Login to get your access token
curl -X POST http://localhost:8080/api/v1/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "developer@fintech.ng",
    "password": "SecurePass123"
  }'
```

### Step 5: Make Your First API Call
```bash
# Use the access_token from the login response
export TOKEN="your-access-token-here"

# Get your user information
curl -X GET http://localhost:8080/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

🎉 **Congratulations!** You've successfully connected to the API Gateway!

## 📚 Complete API Reference

### 🔑 Authentication Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `POST` | `/api/v1/auth/register` | Create new user account | None |
| `POST` | `/api/v1/auth/login/json` | Login with email/username | None |
| `GET` | `/api/v1/auth/me` | Get current user info | Bearer Token |
| `POST` | `/api/v1/auth/logout` | Logout and invalidate token | Bearer Token |

### 🇳🇬 Nigerian Identity Services

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `POST` | `/api/v1/nin/verify` | Verify NIN with Doja API | Bearer Token |
| `POST` | `/api/v1/bvn/verify` | Verify BVN with Doja API | Bearer Token |
| `GET` | `/api/v1/nin/status/{nin}` | Check NIN verification status | Bearer Token |
| `GET` | `/api/v1/bvn/status/{bvn}` | Check BVN verification status | Bearer Token |

### 📱 SMS Services

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `POST` | `/api/v1/sms/send` | Send SMS to Nigerian numbers | Bearer Token |
| `GET` | `/api/v1/sms/status/{message_id}` | Check SMS delivery status | Bearer Token |

### 🤖 AI Services

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `POST` | `/api/v1/ai/generate` | Generate content with AI | Bearer Token |
| `POST` | `/api/v1/ai/analyze` | Analyze data with AI | Bearer Token |

### 📊 Monitoring & Health

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `GET` | `/health` | Gateway health check | None |
| `GET` | `/api/v1/services/health` | All services health | None |
| `GET` | `/metrics` | Prometheus metrics | None |

## 💡 Real-World Examples

### Example 1: Verify a Nigerian NIN
```bash
curl -X POST http://localhost:8080/api/v1/nin/verify \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nin": "12345678901"
  }'

# Response:
{
  "status": "verified",
  "nin": "12345678901",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-01",
  "verification_id": "ver_123456"
}
```

### Example 2: Send SMS to Nigerian Number
```bash
curl -X POST http://localhost:8080/api/v1/sms/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+2348012345678",
    "message": "Your OTP is 123456. Valid for 5 minutes."
  }'

# Response:
{
  "status": "sent",
  "message_id": "msg_789012",
  "to": "+2348012345678",
  "cost": 0.05
}
```

### Example 3: Generate Content with AI
```bash
curl -X POST http://localhost:8080/api/v1/ai/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a business plan for a Nigerian fintech startup",
    "max_tokens": 500
  }'

# Response:
{
  "generated_text": "Executive Summary: Our fintech startup...",
  "tokens_used": 487,
  "generation_id": "gen_345678"
}
```

## 🔧 Configuration & Environment Setup

### Environment Variables

Create a `.env` file in the `services/api-gateway` directory:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8080
DEBUG=false

# Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-here
AUTH_SERVICE_URL=http://localhost:8000

# Redis (for rate limiting and caching)
REDIS_URL=redis://localhost:6379/0

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Service URLs
NIN_SERVICE_URL=http://localhost:8005
BVN_SERVICE_URL=http://localhost:8006
SMS_SERVICE_URL=http://localhost:8003
AI_SERVICE_URL=http://localhost:8002

# CORS Settings
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true
```

### Required Dependencies

The gateway requires these services to be running:
- **Auth Service** (port 8000) - For user authentication
- **Redis** (port 6379) - For rate limiting and caching
- **Backend Services** - NIN (8005), BVN (8006), SMS (8003), AI (8002)

## 📊 Monitoring Your Usage

### View Your API Activity
```bash
# Analyze your usage patterns
python ../../analyze-logs.py --user-activity

# Monitor real-time access
tail -f ../logs/api_access.log

# Check security events
python ../../analyze-logs.py --security
```

### Understanding Rate Limits
- **Default Limit**: 100 requests per minute per user
- **Rate Limit Headers**: Check `X-RateLimit-Remaining` in responses
- **429 Status Code**: Indicates you've hit the rate limit

```bash
# Check your current rate limit status
curl -I http://localhost:8080/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Look for these headers:
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 95
# X-RateLimit-Reset: 1640995200
```

## 🛠️ Development & Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest httpx

# Run the test suite
pytest tests/

# Run specific test categories
pytest tests/test_auth.py -v
pytest tests/test_routing.py -v
```

### Load Testing
```bash
# Install hey (HTTP load testing tool)
brew install hey  # macOS
# or
sudo apt install hey  # Ubuntu

# Test gateway performance
hey -n 1000 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/v1/auth/me
```

### Debugging Common Issues

#### 1. **Gateway Returns 503 (Service Unavailable)**
```bash
# Check if backend services are running
curl http://localhost:8000/health  # Auth service
curl http://localhost:8005/health  # NIN service

# Check service health through gateway
curl http://localhost:8080/api/v1/services/health
```

#### 2. **Authentication Fails (401 Unauthorized)**
```bash
# Verify your token is valid
curl -X GET http://localhost:8080/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN" -v

# Check token expiration
# Tokens expire after 30 minutes by default
```

#### 3. **Rate Limited (429 Too Many Requests)**
```bash
# Wait for rate limit window to reset (60 seconds by default)
# Or contact admin to increase your rate limit

# Check when your rate limit resets
curl -I http://localhost:8080/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

## 🚀 Production Deployment

### Docker Deployment
```bash
# Build the gateway image
docker build -t sandbox-api-gateway:1.0.0 .

# Run with Docker
docker run -p 8080:8080 \
  -e JWT_SECRET_KEY="your-production-secret" \
  -e REDIS_URL="redis://redis:6379/0" \
  sandbox-api-gateway:1.0.0
```

### Kubernetes Deployment
```bash
# Deploy with Helm
cd helm/api-gateway
helm install api-gateway . \
  --set secrets.jwtSecretKey="your-production-secret" \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=api.yourdomain.com
```

## 🤝 Getting Help

### Resources
- **Interactive API Docs**: http://localhost:8080/docs
- **Health Dashboard**: http://localhost:8080/api/v1/services/health
- **Metrics**: http://localhost:8080/metrics

### Common Questions

**Q: Can I use the gateway without authentication?**
A: Some endpoints like `/health` and `/docs` are public, but all DPI services require authentication.

**Q: How do I increase my rate limit?**
A: Contact your platform administrator or modify the `RATE_LIMIT_REQUESTS` environment variable.

**Q: Can I use API keys instead of JWT tokens?**
A: Yes! Pass your API key in the `X-API-Key` header instead of the Authorization header.

**Q: How do I monitor my API usage?**
A: Use the built-in analytics: `python ../../analyze-logs.py --user-activity`

### Support
- 📧 **Email**: support@sandbox-platform.ng
- 💬 **Slack**: #api-gateway-support
- 🐛 **Issues**: Create an issue in the repository
- 📖 **Documentation**: Check `/docs` endpoint for latest API reference

---

**Built with ❤️ for Nigerian developers and startups**

*Ready to build the next big Nigerian fintech or digital service? The API Gateway is your starting point!*