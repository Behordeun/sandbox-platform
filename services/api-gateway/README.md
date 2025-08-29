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

3. **Start Redis** (for rate limiting):

   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

4. **Run the gateway**:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
   ```

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
curl http://127.0.0.1:8080/health

# Expected response:
{
  "status": "healthy",
  "service": "Sandbox API Gateway",
  "version": "1.0.0"
}
```

### Step 3: Explore the API Documentation

Open your browser and go to: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)

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

- **Interactive API Docs**: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)
- **Health Dashboard**: [http://127.0.0.1:8080/api/v1/services/health](http://127.0.0.1:8080/api/v1/services/health)
- **Metrics**: [http://127.0.0.1:8080/metrics](http://127.0.0.1:8080/metrics)

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
curl -I http://127.0.0.1:8080/api/v1/auth/me \
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
  http://127.0.0.1:8080/api/v1/auth/me
```

### Debugging Common Issues

#### 1. **Gateway Returns 503 (Service Unavailable)**

```bash
# Check if backend services are running
curl http://127.0.0.1:8000/health  # Auth service
curl http://127.0.0.1:8005/health  # NIN service

# Check service health through gateway
curl http://127.0.0.1:8080/api/v1/services/health
```

#### 2. **Authentication Fails (401 Unauthorized)**

```bash
# Verify your token is valid
curl -X GET http://127.0.0.1:8080/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN" -v

# Check token expiration
# Tokens expire after 30 minutes by default
```

#### 3. **Rate Limited (429 Too Many Requests)**

```bash
# Wait for rate limit window to reset (60 seconds by default)
# Or contact admin to increase your rate limit

# Check when your rate limit resets
curl -I http://127.0.0.1:8080/api/v1/auth/me \
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

## API Endpoints

### Gateway Routes

- `GET|POST|PUT|DELETE /api/v1/auth/*` - Route to auth service
- `GET|POST|PUT|DELETE /api/v1/sms/*` - Route to SMS service
- `GET|POST|PUT|DELETE /api/v1/llm/*` - Route to LLM service

### Management

- `GET /api/v1/services/health` - Get health of all services
- `GET /api/v1/services/status` - Get detailed service status
- `GET /api/v1/services/{service}/health` - Get specific service health
- `GET /api/v1/services/{service}/metrics` - Get service metrics

### System

- `GET /health` - Gateway health check
- `GET /metrics` - Prometheus metrics
- `GET /docs` - API documentation

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8080` |
| `REDIS_URL` | Redis connection URL | `redis://127.0.0.1:6379/0` |
| `JWT_SECRET_KEY` | JWT secret for token validation | Required |
| `RATE_LIMIT_REQUESTS` | Requests per window | `100` |
| `RATE_LIMIT_WINDOW` | Rate limit window (seconds) | `60` |
| `CIRCUIT_BREAKER_FAILURE_THRESHOLD` | Failures before opening circuit | `5` |
| `METRICS_ENABLED` | Enable Prometheus metrics | `true` |

### Service Configuration

Services are configured in `app/core/config.py`:

```python
services = {
    "auth": ServiceConfig(
        name="auth-service",
        url="http://auth-service:8000",
        health_path="/health"
    ),
    "sms": ServiceConfig(
        name="sms-service", 
        url="http://sms-service:8000",
        health_path="/health"
    )
}
```

## Architecture

### Middleware Stack

1. **CORS Middleware**: Handle cross-origin requests
2. **Metrics Middleware**: Collect Prometheus metrics
3. **Logging Middleware**: Request/response logging
4. **Rate Limit Middleware**: Redis-based rate limiting
5. **Auth Middleware**: JWT/API key authentication

### Circuit Breaker

The gateway implements circuit breaker pattern for each backend service:

- **Closed**: Normal operation, requests pass through
- **Open**: Service is failing, requests are blocked
- **Half-Open**: Testing if service has recovered

### Load Balancing

Supports multiple load balancing strategies:

- **Round Robin**: Distribute requests evenly
- **Least Connections**: Route to least busy instance
- **Random**: Random selection

### Health Monitoring

- Continuous health checks every 30 seconds
- Circuit breaker state tracking
- Service response time monitoring
- Automatic service discovery updates

## Monitoring

### Prometheus Metrics

The gateway exposes the following metrics:

- `api_gateway_requests_total` - Total requests by method/endpoint/status
- `api_gateway_request_duration_seconds` - Request duration histogram
- `api_gateway_active_requests` - Current active requests
- `api_gateway_service_requests_total` - Backend service requests
- `api_gateway_circuit_breaker_state` - Circuit breaker states
- `api_gateway_rate_limit_hits_total` - Rate limit violations

### Health Checks

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

- **Interactive API Docs**: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)
- **Health Dashboard**: [http://127.0.0.1:8080/api/v1/services/health](http://127.0.0.1:8080/api/v1/services/health)
- **Metrics**: [http://127.0.0.1:8080/metrics](http://127.0.0.1:8080/metrics)

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
