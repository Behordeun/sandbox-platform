# Sandbox Platform

A modular, cloud-native platform designed for Nigerian startups to rapidly prototype and deploy applications. Built with FastAPI microservices, Docker containerization, and Kubernetes orchestration following the DIGIT-Core architecture pattern.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop with Kubernetes enabled
- kubectl and Helm 3.8+
- Python 3.11+ (for local development)

### Local Development
```bash
# Clone the repository
git clone <repository-url>
cd sandbox-platform

# Start infrastructure services
docker-compose -f deployment/docker-compose/docker-compose.dev.yml up -d postgres redis

# Start application services (in separate terminals)
cd services/auth-service && uvicorn app.main:app --reload --port 8000
cd services/config-service && uvicorn app.main:app --reload --port 8001  
cd services/api-gateway && uvicorn app.main:app --reload --port 8080

# Verify setup
curl http://localhost:8080/health
```

### Production Deployment
```bash
# Build and push images
./deployment/scripts/build-images.sh -r your-registry/ -t v1.0.0
./deployment/scripts/push-images.sh -r your-registry/ -t v1.0.0

# Deploy with Helmfile
cd deployment/helmfile
helmfile -e prod apply
```

## 🏗️ Architecture

### Core Services

| Service | Port | Description |
|---------|------|-------------|
| **Auth Service** | 8000 | OAuth2 authentication, JWT tokens, NIN/BVN verification |
| **API Gateway** | 8080 | Request routing, rate limiting, circuit breaking |
| **Config Service** | 8000 | Centralized configuration management with encryption |

### Infrastructure

- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage  
- **Prometheus** - Metrics collection
- **Grafana** - Monitoring dashboards

## 📁 Project Structure

```
sandbox-platform/
├── services/
│   ├── auth-service/          # Authentication & authorization
│   ├── api-gateway/           # API Gateway & routing
│   └── config-service/        # Configuration management
├── deployment/
│   ├── scripts/               # Build & deployment scripts
│   ├── docker-compose/        # Local development setup
│   ├── helmfile/              # Kubernetes deployment
│   └── monitoring/            # Monitoring configuration
└── docs/                      # Documentation
```

## 🔧 Development

### Service Development
Each service is independently developed and deployed:

```bash
# Auth Service
cd services/auth-service
pip install -r requirements.txt
uvicorn app.main:app --reload

# API Gateway  
cd services/api-gateway
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080

# Config Service
cd services/config-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### Docker Development
```bash
# Build all services
./deployment/scripts/build-images.sh

# Run with Docker Compose
docker-compose -f deployment/docker-compose/docker-compose.dev.yml up
```

## 🚢 Deployment

### Environment Configuration

| Environment | Namespace | Replicas | Resources |
|-------------|-----------|----------|-----------|
| Development | sandbox-dev | 1 each | 200m CPU, 256Mi RAM |
| Staging | sandbox-staging | 2 each | 500m CPU, 512Mi RAM |
| Production | sandbox-prod | 3 each | 1000m CPU, 1Gi RAM |

### Helmfile Deployment
```bash
# Development
helmfile -e dev apply

# Staging  
helmfile -e staging apply

# Production
export PROD_POSTGRES_PASSWORD=secure-password
export PROD_REDIS_PASSWORD=secure-password
export JWT_SECRET_KEY=secure-jwt-secret
helmfile -e prod apply
```

### Manual Helm Deployment
```bash
# Install dependencies
helm install postgres bitnami/postgresql --set auth.postgresPassword=postgres123
helm install redis bitnami/redis --set auth.password=redis123

# Install services
helm install auth-service ./services/auth-service/helm/auth-service
helm install config-service ./services/config-service/helm/config-service  
helm install api-gateway ./services/api-gateway/helm/api-gateway
```

## 📊 Monitoring

### Health Checks
- Auth Service: `http://localhost:8000/health`
- API Gateway: `http://localhost:8080/health`  
- Config Service: `http://localhost:8001/health`

### Metrics
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001` (admin/admin123)
- Service Metrics: `http://localhost:8080/metrics`

### Logging
Structured JSON logging with correlation IDs:
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "service": "auth-service",
  "correlation_id": "req-123",
  "message": "User authenticated successfully"
}
```

## 🔒 Security

### Authentication Flow
1. User registers/logs in via Auth Service
2. JWT token issued with user claims
3. API Gateway validates tokens on all requests
4. Services receive authenticated user context

### NIN/BVN Verification
```bash
# Verify Nigerian identity
curl -X POST http://localhost:8000/api/v1/identity/verify-nin-bvn \
  -H "Content-Type: application/json" \
  -d '{"nin": "12345678901", "bvn": "12345678901"}'
```

### Configuration Encryption
Sensitive configuration values are automatically encrypted:
```json
{
  "database_password": {
    "_encrypted": true,
    "_value": "gAAAAABh..."
  }
}
```

## 🔧 Configuration

### Environment Variables

#### Auth Service
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
JWT_SECRET_KEY=your-secret-key
DOJA_API_KEY=your-doja-api-key
```

#### API Gateway
```env
AUTH_SERVICE_URL=http://auth-service:8000
REDIS_URL=redis://redis:6379/0
RATE_LIMIT_REQUESTS=100
```

#### Config Service
```env
CONFIG_STORAGE_TYPE=redis
ENCRYPTION_KEY=your-encryption-key
VERSIONING_ENABLED=true
```

## 🧪 Testing

### Unit Tests
```bash
# Run tests for all services
cd services/auth-service && pytest
cd services/api-gateway && pytest  
cd services/config-service && pytest
```

### Integration Tests
```bash
# Start test environment
docker-compose -f deployment/docker-compose/docker-compose.dev.yml up -d

# Run integration tests
pytest tests/integration/
```

### Load Testing
```bash
# Install k6
brew install k6

# Run load tests
k6 run tests/load/auth-service.js
k6 run tests/load/api-gateway.js
```

## 📚 API Documentation

### Interactive Documentation
- Auth Service: `http://localhost:8000/docs`
- API Gateway: `http://localhost:8080/docs`
- Config Service: `http://localhost:8001/docs`

### Key Endpoints

#### Authentication
```bash
# Register user
POST /api/v1/auth/register

# Login
POST /api/v1/auth/login

# Get user info
GET /api/v1/auth/me
```

#### Configuration
```bash
# Create config
POST /api/v1/configs

# Get config
GET /api/v1/configs/{id}

# Update config  
PUT /api/v1/configs/{id}
```

#### Gateway
```bash
# Route to auth service
GET /api/v1/auth/*

# Route to config service
GET /api/v1/configs/*

# Service health
GET /api/v1/services/health
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run tests: `pytest`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open Pull Request

### Code Standards
- Python: Black formatting, flake8 linting, mypy type checking
- Docker: Multi-stage builds, non-root users, health checks
- Kubernetes: Resource limits, security contexts, probes

### Release Process
1. Update version numbers
2. Create release branch
3. Build and test images
4. Deploy to staging
5. Run integration tests
6. Deploy to production
7. Tag release

## 📖 Documentation

- [Deployment Guide](deployment/README.md) - Comprehensive deployment instructions
- [Auth Service](services/auth-service/README.md) - Authentication service details
- [API Gateway](services/api-gateway/README.md) - Gateway configuration and usage
- [Config Service](services/config-service/README.md) - Configuration management
- [Architecture Design](docs/architecture.md) - System architecture overview

## 🐛 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
kubectl logs -f deployment/auth-service

# Check resources
kubectl describe pod <pod-name>

# Check configuration
kubectl get configmap
kubectl get secret
```

#### Database Connection Issues
```bash
# Test database connectivity
kubectl run postgres-client --image=postgres:14 -it --rm --restart=Never -- \
  psql -h postgres -U postgres -d sandbox
```

#### Gateway Routing Issues
```bash
# Check service discovery
kubectl get endpoints

# Test service connectivity
kubectl run debug --image=busybox -it --rm --restart=Never -- \
  nslookup auth-service.sandbox-dev.svc.cluster.local
```

### Performance Issues
```bash
# Check resource usage
kubectl top pods
kubectl top nodes

# Check HPA status
kubectl get hpa
kubectl describe hpa auth-service-hpa
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [DIGIT-Core](https://github.com/egovernments/DIGIT-DevOps) - Architecture inspiration
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Kubernetes](https://kubernetes.io/) - Container orchestration
- [Helm](https://helm.sh/) - Kubernetes package manager

## 📞 Support

- 📧 Email: support@sandbox.example.com
- 💬 Slack: #sandbox-platform
- 📖 Wiki: [Internal Documentation](https://wiki.sandbox.example.com)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/sandbox-platform/issues)

---

**Built with ❤️ for Nigerian startups**

