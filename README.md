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
git clone https://github.com/Behordeun/sandbox-platform.git

cd sandbox-platform

# Start infrastructure services
docker compose -f deployment/docker-compose/docker-compose.dev.yml up -d postgres redis mongo

# Start platform services (in separate terminals)
cd services/auth-service && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000
cd config && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8001
cd services/api-gateway && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8080

# Start sandbox services
cd sandbox/ai && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8002
cd sandbox/sms && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8003
cd sandbox/nin && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8005
cd sandbox/bvn && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8006

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

### Sandbox Offerings

| Service                  | Port | Description                                             |
| ------------------------ | ---- | ------------------------------------------------------- |
| **AI Service**     | 8002 | AI content generation and data analysis                |
| **SMS Service**    | 8003 | SMS messaging and notifications                         |
| **IVR Service**    | 8004 | Interactive Voice Response system                       |
| **NIN Service**    | 8005 | Nigerian Identity Number verification                   |
| **BVN Service**    | 8006 | Bank Verification Number validation                     |
| **Two-Way SMS**    | 8007 | Bidirectional SMS communication                         |

### Platform Services

| Service                  | Port | Description                                             |
| ------------------------ | ---- | ------------------------------------------------------- |
| **Auth Service**   | 8000 | OAuth2 authentication, JWT tokens                      |
| **API Gateway**    | 8080 | Request routing, rate limiting, circuit breaking        |
| **Rate Limiter**   | 8008 | Advanced rate limiting and throttling                   |
| **Health Service** | 8009 | Service health monitoring and checks                    |
| **Logging Service**| 8010 | Centralized logging and audit trails                   |
| **Monitoring**     | 8011 | Metrics collection and alerting                         |

### Data Stores

- **PostgreSQL** - Primary relational database
- **MongoDB** - Document database for flexible schemas
- **Redis** - Caching and session storage

### Centralized Configuration

- **Config** - Centralized configuration management with encryption

## 📁 Project Structure

```plain
sandbox-platform/
├── sandbox/                   # Main offerings
│   ├── ai/                    # AI service
│   ├── sms/                   # SMS service
│   ├── ivr/                   # IVR service
│   ├── nin/                   # NIN verification
│   ├── bvn/                   # BVN verification
│   ├── two-way-sms/           # Two-way SMS
│   └── data-stores/           # Database configurations
│       ├── postgres/          # PostgreSQL setup
│       └── mongo/             # MongoDB setup
├── services/                  # Platform maintenance
│   ├── auth-service/          # Authentication & authorization
│   ├── api-gateway/           # API Gateway & routing
│   ├── rate-limiter/          # Rate limiting service
│   ├── health-service/        # Health monitoring
│   ├── logging/               # Logging service
│   ├── monitoring/            # Monitoring service
│   └── redis/                 # Redis configuration
├── config/                    # Centralized configuration
├── deployment/                # Deployment configurations
│   ├── scripts/               # Build & deployment scripts
│   ├── docker-compose/        # Local development setup
│   ├── helmfile/              # Kubernetes deployment
│   └── monitoring/            # Monitoring configuration
├── README.md
└── .env.example
```

## 🔧 Development

### Service Development

Each service is independently developed and deployed:

```bash
# Platform Services
cd services/auth-service && uvicorn app.main:app --reload --port 8000
cd services/api-gateway && uvicorn app.main:app --reload --port 8080
cd config && uvicorn app.main:app --reload --port 8001

# Sandbox Services
cd sandbox/ai && uvicorn app.main:app --reload --port 8002
cd sandbox/sms && uvicorn app.main:app --reload --port 8003
cd sandbox/ivr && uvicorn app.main:app --reload --port 8004
cd sandbox/nin && uvicorn app.main:app --reload --port 8005
cd sandbox/bvn && uvicorn app.main:app --reload --port 8006
cd sandbox/two-way-sms && uvicorn app.main:app --reload --port 8007
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

| Environment | Namespace       | Replicas | Resources           |
| ----------- | --------------- | -------- | ------------------- |
| Development | sandbox-dev     | 1 each   | 200m CPU, 256Mi RAM |
| Staging     | sandbox-staging | 2 each   | 500m CPU, 512Mi RAM |
| Production  | sandbox-prod    | 3 each   | 1000m CPU, 1Gi RAM  |

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

## 🔐 Auth Service Features

### Core Capabilities
- **OAuth2 Authorization Server**: Full OAuth2 authorization code flow
- **JWT Token Management**: Secure token generation, validation, and refresh
- **User Management**: Registration, authentication, and profile management
- **Integration with Identity Services**: Connects to dedicated NIN/BVN sandbox services
- **OpenID Connect**: Discovery endpoints and JWKS support
- **Multi-login Support**: OAuth2 and JSON-based authentication

### Database Schema
- **Users Table**: User accounts with hashed passwords and profile data
- **OAuth Clients**: Registered OAuth2 client applications
- **OAuth Tokens**: Access tokens, refresh tokens, and authorization codes
- **Alembic Migrations**: Database version control and schema management

### Security Features
- **Bcrypt Password Hashing**: Secure password storage
- **JWT Signing**: Configurable secret keys and algorithms
- **Identity Privacy**: NIN/BVN data hashing for privacy protection
- **CORS Protection**: Configurable cross-origin policies
- **Input Validation**: Pydantic models for request/response validation

### Integration Points
- **API Gateway**: Token validation for all platform services
- **NIN/BVN Services**: Dedicated sandbox services for identity verification
- **PostgreSQL**: Primary data storage
- **Redis**: Session and token caching (via API Gateway)

## 🔒 Security

### Authentication Flow

#### OAuth2 Authentication
1. **Client Registration**: OAuth2 clients register via `/api/v1/oauth2/clients`
2. **Authorization**: Users authorize via `/api/v1/oauth2/authorize`
3. **Token Exchange**: Authorization codes exchanged for JWT tokens at `/api/v1/oauth2/token`
4. **API Access**: Access tokens validated by API Gateway for all service requests
5. **Token Refresh**: Refresh tokens used to obtain new access tokens

#### User Authentication
1. **Registration**: Users register via `/api/v1/auth/register`
2. **Login**: Multiple login methods:
   - OAuth2 compatible: `/api/v1/auth/login`
   - JSON payload: `/api/v1/auth/login/json`
3. **User Info**: Access user data via `/api/v1/auth/userinfo` or `/api/v1/auth/me`

#### Identity Verification
1. **NIN Verification**: Dedicated NIN service at `/api/v1/nin/verify`
2. **BVN Verification**: Dedicated BVN service at `/api/v1/bvn/verify`
3. **Doja API Integration**: Real-time verification through Doja API
4. **Status Tracking**: Monitor verification status via respective service endpoints
5. **Enhanced Access**: Verified users receive additional platform privileges

### NIN/BVN Verification

```bash
# Verify NIN (Full verification with Dojah API)
curl -X POST http://localhost:8080/api/v1/nin/verify \
  -H "Content-Type: application/json" \
  -d '{"nin": "12345678901"}'

# Basic NIN lookup
curl -X POST http://localhost:8080/api/v1/nin/lookup \
  -H "Content-Type: application/json" \
  -d '{"nin": "12345678901"}'

# Verify BVN (Full verification with Dojah API)
curl -X POST http://localhost:8080/api/v1/bvn/verify \
  -H "Content-Type: application/json" \
  -d '{"bvn": "12345678901"}'

# Basic BVN lookup
curl -X POST http://localhost:8080/api/v1/bvn/lookup \
  -H "Content-Type: application/json" \
  -d '{"bvn": "12345678901"}'
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
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# JWT Configuration
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OAuth2 Configuration
OAUTH2_ISSUER_URL=http://localhost:8000
OAUTH2_JWKS_URI=http://localhost:8000/.well-known/jwks.json

# Identity Verification
DOJA_API_KEY=your-doja-api-key
DOJA_BASE_URL=https://api.dojah.io

# CORS Configuration
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true

# Application Settings
APP_NAME=Sandbox Auth Service
APP_VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=8000
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
# User Management
POST /api/v1/auth/register          # User registration
POST /api/v1/auth/login             # OAuth2 compatible login
POST /api/v1/auth/login/json        # JSON payload login
GET  /api/v1/auth/userinfo          # Get user information
GET  /api/v1/auth/me                # Get current user

# OAuth2 Endpoints
GET  /api/v1/oauth2/authorize       # OAuth2 authorization
POST /api/v1/oauth2/token           # Token exchange
POST /api/v1/oauth2/clients         # Create OAuth2 client
GET  /api/v1/oauth2/clients/{id}    # Get OAuth2 client

# Identity Verification (Sandbox Services)
POST /api/v1/nin/verify                 # Verify NIN with Dojah API
POST /api/v1/nin/lookup                 # Basic NIN lookup
GET  /api/v1/nin/status/{nin}           # Get NIN status
POST /api/v1/bvn/verify                 # Verify BVN with Dojah API
POST /api/v1/bvn/lookup                 # Basic BVN lookup
GET  /api/v1/bvn/status/{bvn}           # Get BVN status

# System Endpoints
GET  /health                             # Health check
GET  /.well-known/openid_configuration   # OpenID Connect discovery
GET  /.well-known/jwks.json             # JSON Web Key Set
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
- [Auth Service](services/auth-service/README.md) - OAuth2, JWT, and NIN/BVN verification
- [API Gateway](services/api-gateway/README.md) - Gateway configuration and usage
- [Config Service](config/README.md) - Centralized configuration management
- [Architecture Design](docs/architecture.md) - System architecture overview

### Service-Specific Documentation
- **Auth Service**: OAuth2 flows, identity verification, JWT management
- **API Gateway**: Request routing, rate limiting, circuit breaking
- **Config Service**: Encrypted configuration, versioning, environment management
- **Sandbox Services**: AI, SMS, IVR, NIN, BVN, Two-Way SMS capabilities

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

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

- [DIGIT-Core](https://github.com/egovernments/DIGIT-DevOps) - Architecture inspiration
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Kubernetes](https://kubernetes.io/) - Container orchestration
- [Helm](https://helm.sh/) - Kubernetes package manager

## 📞 Support

- 📧 Email: [support@sandbox.example.com](mailto:support@sandbox.example.com)
- 💬 Slack: #sandbox-platform
- 📖 Wiki: [Internal Documentation](https://wiki.sandbox.example.com)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/sandbox-platform/issues)

---

### Built with ❤️ for Nigerian startups
