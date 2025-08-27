# Sandbox Platform

A modular, cloud-native platform designed for Nigerian startups to rapidly prototype and deploy applications. Built with FastAPI microservices, Docker containerization, and Kubernetes orchestration following the DIGIT-Core architecture pattern.

## 🚀 Quick Start for Nigerian DPI Developers

### Prerequisites

- Docker Desktop (for infrastructure)
- Python 3.11+
- Git

### One-Command Setup

```bash
# Clone the repository
git clone https://github.com/Behordeun/sandbox-platform.git
cd sandbox-platform

# Setup centralized configuration
cp .env.template .env
# Edit .env with your API keys and secrets (single file for all services)

# Set environment
export ENVIRONMENT=development

# Start infrastructure services
docker compose -f deployment/docker-compose/docker-compose.dev.yml up -d postgres redis mongo

# Verify DPI services are ready
./check-services.sh
```

### Test Your Setup

```bash
# Generate Nigerian test data
python mock-data.py

# Test DPI APIs
./test-dpi-apis.sh

# Access API documentation
open http://localhost:8080/docs
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
| **Auth Service**   | 8000 | OAuth2 authentication, JWT tokens, NIN/BVN verification |
| **API Gateway**    | 8080 | Request routing, rate limiting, circuit breaking        |
| **Config Service** | 8000 | Centralized configuration management with encryption    |

### Platform Services

| Service                  | Port | Description                                             |
| ------------------------ | ---- | ------------------------------------------------------- |
| **Auth Service**   | 8000 | OAuth2 authentication, JWT tokens                      |
| **API Gateway**    | 8080 | Request routing, rate limiting, circuit breaking        |
| **Rate Limiter**   | 8008 | Advanced rate limiting and throttling                   |
| **Health Service** | 8009 | Service health monitoring and checks                    |
| **Logging Service**| 8010 | Centralized logging and audit trails                   |
| **Monitoring**     | 8011 | Metrics collection and alerting                         |

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
├── sandbox/                   # Main DPI offerings
│   ├── ai/                    # AI service
│   ├── sms/                   # SMS service
│   ├── ivr/                   # IVR service
│   ├── nin/                   # NIN verification
│   ├── bvn/                   # BVN verification
│   ├── two-way-sms/           # Two-way SMS
│   └── data-stores/           # Database configurations
├── services/                  # Platform services
│   ├── auth-service/          # Authentication & authorization
│   ├── api-gateway/           # API Gateway & routing
│   └── redis/                 # Redis configuration
├── config/                    # Centralized YAML configuration
│   ├── environments/          # Environment-specific configs
│   ├── config_loader.py       # Configuration loader
│   └── README.md             # Configuration documentation
├── deployment/                # Deployment configurations
│   ├── scripts/               # Build & deployment scripts
│   ├── docker-compose/        # Local development setup
│   ├── helmfile/              # Kubernetes deployment
│   └── monitoring/            # Monitoring configuration
├── config.yaml               # Base configuration
├── .env.template             # Environment variables template
└── README.md
```

## 🔧 Development for Nigerian DPI

### Nigerian Data Formats

- **Phone Numbers**: `+234XXXXXXXXXX` or `0XXXXXXXXXX`
- **NIN**: 11-digit National Identity Number
- **BVN**: 11-digit Bank Verification Number

### Quick Development Commands

```bash
# Start all services
./sandbox-start.sh

# Check service health
./check-services.sh

# Test APIs with Nigerian examples
./test-dpi-apis.sh

# Analyze user activity and usage
python analyze-logs.py --all

# Generate mock Nigerian data
python mock-data.py
```

### Individual Service Development

```bash
# Platform Services
cd services/auth-service && uvicorn app.main:app --reload --port 8000
cd services/api-gateway && uvicorn app.main:app --reload --port 8080

# DPI Sandbox Services
cd sandbox/nin && uvicorn app.main:app --reload --port 8005
cd sandbox/bvn && uvicorn app.main:app --reload --port 8006
cd sandbox/sms && uvicorn app.main:app --reload --port 8003
cd sandbox/ai && uvicorn app.main:app --reload --port 8002
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

## 📊 Monitoring & Analytics

### Health Checks

```bash
# Check all DPI services at once
./check-services.sh

# Or check individual services
curl http://localhost:8080/api/v1/dpi/health  # DPI services overview
curl http://localhost:8000/health             # Auth service
curl http://localhost:8005/health             # NIN service
curl http://localhost:8006/health             # BVN service
curl http://localhost:8003/health             # SMS service
```

### User Activity & Usage Analytics

```bash
# Comprehensive log analysis
python analyze-logs.py --all

# User activity patterns
python analyze-logs.py --user-activity

# Security monitoring
python analyze-logs.py --security

# Real-time monitoring
tail -f services/logs/user_activity.log
tail -f services/logs/api_access.log
```

### Rich Logging System

Comprehensive user activity tracking with structured JSON logging:

```json
{
  "timestamp": "2025-08-25 20:45:30",
  "user_id": "123",
  "auth_method": "jwt_token",
  "method": "POST",
  "path": "/api/v1/nin/verify",
  "service": "nin-service",
  "status_code": 200,
  "duration_ms": 245.5,
  "client_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "activity_type": "identity_verification",
  "success": true
}
```

### Log Categories

- **User Activity**: `services/logs/user_activity.log` - All user interactions
- **API Access**: `services/logs/api_access.log` - Gateway access patterns
- **Security Events**: `services/logs/security_events.log` - Authentication & security
- **Service Health**: `services/logs/service_health.log` - System monitoring

### Analytics Capabilities

- **User Engagement**: Track individual user activity patterns
- **Service Popularity**: Monitor which services are most used
- **Peak Hours**: Identify high-traffic periods
- **Security Monitoring**: Detect suspicious activities
- **Performance Metrics**: Response times and success rates

### Metrics

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001` (admin/admin123)
- Service Metrics: `http://localhost:8080/metrics`

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
3. **Dojah API Integration**: Real-time verification through Dojah API
4. **Status Tracking**: Monitor verification status via respective service endpoints
5. **Enhanced Access**: Verified users receive additional platform privileges

### Nigerian Identity Verification

```bash
# Get examples and test data
curl http://localhost:8080/api/v1/examples/nin
curl http://localhost:8080/api/v1/examples/sms

# Verify NIN with authentication
curl -X POST http://localhost:8080/api/v1/nin/verify \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nin": "12345678901"}'

# Verify BVN with authentication
curl -X POST http://localhost:8080/api/v1/bvn/verify \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"bvn": "12345678901"}'

# Send SMS to Nigerian number
curl -X POST http://localhost:8080/api/v1/sms/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"to": "+2348012345678", "message": "Your OTP is 123456"}'
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

### Hybrid Configuration System

The platform uses a hybrid approach combining YAML configuration with centralized environment variables:

```plain text
config.yaml                    # Base configuration for all services
config/environments/
├── development.yaml          # Environment-specific overrides
├── staging.yaml             # Staging overrides
└── production.yaml          # Production overrides
.env                         # Single centralized environment file
.env.template               # Template for all environment variables
```

### Environment Setup

```bash
# Copy template and customize (single file for all services)
cp .env.template .env

# Edit the centralized .env file with your actual values
nano .env

# All services automatically use the centralized configuration
```

### Centralized Environment Variables (.env)

The platform uses a **single comprehensive .env file** organized into sections:

```env
# =============================================================================
# ENVIRONMENT SETTINGS
# =============================================================================
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
# Single PostgreSQL database for all services
DATABASE_URL=postgresql://sandbox_user:password@localhost:5432/sandbox_platform
DB_PASSWORD=your-database-password
REDIS_URL=redis://localhost:6379/0

# =============================================================================
# SECURITY & AUTHENTICATION
# =============================================================================
JWT_SECRET_KEY=your-super-secret-jwt-key
CONFIG_ENCRYPTION_KEY=your-config-encryption-key

# =============================================================================
# EXTERNAL API PROVIDERS
# =============================================================================
DOJAH_API_KEY=your-dojah-api-key
DOJAH_APP_ID=your-dojah-app-id
SMS_API_KEY=your-sms-api-key
AI_API_KEY=your-ai-api-key

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# ... and more organized sections
```

### Configuration Benefits

- **Single Source of Truth**: One .env file for all services
- **No Configuration Drift**: Consistent settings across services
- **Organized Structure**: Well-documented sections and comments
- **Easy Deployment**: Single file to manage in production
- **Better Security**: Centralized secret management
- **YAML + ENV Hybrid**: Structure from YAML, secrets from environment

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

### Quick Reference for Nigerian Developers

- [Database Guide](DATABASE.md) - Consolidated PostgreSQL database architecture
- [Configuration Guide](config/README.md) - YAML + centralized .env configuration
- [Database Setup](setup-db.sh) - One-command database setup and migrations
- [DPI API Guide](DPI-API-GUIDE.md) - Complete API reference with Nigerian examples
- [Mock Data Generator](mock-data.py) - Generate realistic Nigerian test data
- [API Testing Script](test-dpi-apis.sh) - Test complete DPI workflows
- [Service Health Checker](check-services.sh) - Monitor all services

### Detailed Documentation

- [Configuration Management](config/README.md) - YAML-based configuration system
- [Deployment Guide](deployment/README.md) - Comprehensive deployment instructions
- [Auth Service](services/auth-service/README.md) - OAuth2, JWT, and password management
- [API Gateway](services/api-gateway/README.md) - Gateway configuration and usage
- [Sandbox Services](sandbox/README.md) - DPI services overview

### Service-Specific Documentation

- **Auth Service**: OAuth2 flows, Nigerian phone validation, JWT management
- **API Gateway**: Request routing, rate limiting, DPI health monitoring
- **NIN Service**: Nigerian Identity Number verification via Dojah API
- **BVN Service**: Bank Verification Number validation
- **SMS Service**: Nigerian SMS messaging and notifications
- **AI Service**: Content generation and data analysis

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
