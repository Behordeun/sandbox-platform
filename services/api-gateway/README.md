# Sandbox API Gateway

A high-performance API Gateway built with FastAPI for the Sandbox Platform. This service provides request routing, authentication, rate limiting, circuit breaking, and monitoring capabilities for all backend services.

## Features

- **Request Routing**: Intelligent routing to backend services
- **Authentication**: JWT token validation and API key authentication
- **Rate Limiting**: Redis-based rate limiting with sliding window
- **Circuit Breaking**: Automatic failure detection and recovery
- **Load Balancing**: Multiple load balancing strategies (round-robin, least connections, random)
- **Health Monitoring**: Continuous health checks for backend services
- **Metrics Collection**: Prometheus metrics for monitoring and alerting
- **Request/Response Logging**: Structured logging for observability
- **CORS Support**: Cross-origin resource sharing configuration
- **Service Discovery**: Dynamic service registration and discovery

## Quick Start

### Local Development

1. **Setup environment**:
   ```bash
   cd api-gateway
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Redis** (for rate limiting):
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

4. **Run the gateway**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
   ```

5. **Access the gateway**:
   - API Documentation: http://localhost:8080/docs
   - Health Check: http://localhost:8080/health
   - Metrics: http://localhost:8080/metrics

### Docker Deployment

```bash
docker build -t your-dockerhub-username/sandbox-api-gateway:1.0.0 .
docker run -p 8080:8080 \
  -e REDIS_URL="redis://redis:6379/0" \
  -e JWT_SECRET_KEY="your-secret-key" \
  your-dockerhub-username/sandbox-api-gateway:1.0.0
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
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
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
# Gateway health
curl http://localhost:8080/health

# All services health
curl http://localhost:8080/api/v1/services/health

# Specific service health
curl http://localhost:8080/api/v1/services/auth/health
```

## Security

### Authentication

The gateway supports two authentication methods:

1. **JWT Tokens**: Bearer tokens in Authorization header
2. **API Keys**: X-API-Key header

### Rate Limiting

Redis-based sliding window rate limiting:

- Default: 100 requests per 60 seconds
- Per user/API key/IP address
- Configurable limits and windows

### CORS

Configurable CORS policies:

- Allowed origins, methods, headers
- Credential support
- Preflight request handling

## Development

### Project Structure

```
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
# Run tests
pytest tests/

# Load testing
hey -n 1000 -c 10 http://localhost:8080/health
```

## Deployment

### Kubernetes

The gateway is designed for Kubernetes deployment with:

- Health checks for liveness/readiness probes
- Graceful shutdown handling
- Resource limits and requests
- Service discovery integration

### Scaling

- Horizontal scaling with multiple replicas
- Stateless design (state in Redis)
- Load balancer friendly
- Circuit breaker per instance

## Troubleshooting

### Common Issues

1. **Service Unavailable (503)**:
   - Check backend service health
   - Verify circuit breaker state
   - Check service configuration

2. **Rate Limited (429)**:
   - Check Redis connectivity
   - Verify rate limit configuration
   - Monitor client request patterns

3. **Authentication Failed (401)**:
   - Verify JWT secret key
   - Check token expiration
   - Validate API key format

### Debugging

```bash
# Check service health
curl http://localhost:8080/api/v1/services/health

# View metrics
curl http://localhost:8080/metrics

# Check logs
docker logs <container-id>
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License.

