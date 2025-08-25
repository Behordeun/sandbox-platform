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
# Build the gateway image
docker build -t sandbox-api-gateway:1.0.0 .

# Run with Docker
docker run -p 8080:8080 \
  -e JWT_SECRET_KEY="your-production-secret" \
  -e REDIS_URL="redis://redis:6379/0" \
  sandbox-api-gateway:1.0.0
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

Open your browser and go to: [http://localhost:8080/docs](http://localhost:8080/docs)

This interactive documentation shows all available endpoints and lets you test them directly!

### Step 4: Get Your First Token

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

- **Interactive API Docs**: [http://localhost:8080/docs](http://localhost:8080/docs)
- **Health Dashboard**: [http://localhost:8080/api/v1/services/health](http://localhost:8080/api/v1/services/health)
- **Metrics**: [http://localhost:8080/metrics](http://localhost:8080/metrics)

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

- 📧 **Email**: [support@sandbox-platform.ng](mail-to:support@sandbox-platform.ng)
- 💬 **Slack**: #api-gateway-support
- 🐛 **Issues**: Create an issue in the repository
- 📖 **Documentation**: Check `/docs` endpoint for latest API reference

---

### Project Structure

```plain text
app/
├── api/v1/          # API endpoints
├── core/            # Core utilities and configuration
├── middleware/      # Custom middleware
├── services/        # Business logic services
└── main.py         # FastAPI application
```

### Adding New Services

1. **Update configuration**:

   ```python
   # In app/core/config.py
   services["new_service"] = ServiceConfig(
       name="new-service",
       url="http://new-service:8000",
       health_path="/health"
   )
   ```

2. **Add routing**:

   ```python
   # In app/api/v1/gateway.py
   @router.api_route("/new/{path:path}", methods=["GET", "POST"])
   async def proxy_new_service(request: Request, path: str):
       return await proxy_service.proxy_request(request, "new_service", f"/{path}")
   ```

### Testing

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

- **Interactive API Docs**: [http://localhost:8080/docs](http://localhost:8080/docs)
- **Health Dashboard**: [http://localhost:8080/api/v1/services/health](http://localhost:8080/api/v1/services/health)
- **Metrics**: [http://localhost:8080/metrics](http://localhost:8080/metrics)

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

- 📧 **Email**: [support@sandbox-platform.ng](mail-to:support@sandbox-platform.ng)
- 💬 **Slack**: #api-gateway-support
- 🐛 **Issues**: Create an issue in the repository
- 📖 **Documentation**: Check `/docs` endpoint for latest API reference

---

**Ready to build the next big Nigerian fintech or digital service? The API Gateway is your starting point!**

## Built with ❤️ for Nigerian developers and startups
