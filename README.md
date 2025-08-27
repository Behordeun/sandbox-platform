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
# Edit .env with your API keys and secrets

# Setup database and create admin users
./scripts/setup-db.sh
./scripts/create-admin-user.py

# Start entire sandbox platform
./scripts/start-sandbox.sh
```

### Test Your Setup

```bash
# Generate Nigerian test data
./scripts/mock-data.py

# Test DPI APIs
./scripts/test-dpi-apis.sh

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

```mermaid
%%{init: { 'theme': 'default', 'themeVariables': { 'background': '#ffffff' } }}%%
graph TB
    %% External Users and Systems
    subgraph "🌍 External Systems"
        STARTUPS[("🚀 Nigerian Startups<br/>(9 Closed Access)")]
        ADMIN[("👨‍💼 Platform Admin")]
        DOJAH[("🔍 Dojah API<br/>(NIN/BVN Verification)")]
        SMS_PROVIDER[("📱 SMS Provider<br/>(Nigerian Networks)")]
        AI_PROVIDER[("🤖 AI Provider<br/>(Nigerian Context)")]
    end

    %% API Gateway Layer
    subgraph "🌐 API Gateway Layer"
        GATEWAY["🚪 API Gateway<br/>:8080<br/>• Request Routing<br/>• Rate Limiting<br/>• Circuit Breaking<br/>• Authentication"]
    end

    %% Platform Services
    subgraph "🏗️ Platform Services"
        AUTH["🔐 Auth Service<br/>:8000<br/>• OAuth2/JWT<br/>• Admin User Mgmt<br/>• Session Management"]
        CONFIG["⚙️ Config Service<br/>:8001<br/>• Centralized Config<br/>• Environment Mgmt<br/>• Encryption"]
        HEALTH["💚 Health Service<br/>• Service Monitoring<br/>• Health Checks<br/>• Status Reporting"]
    end

    %% DPI Sandbox Services
    subgraph "🇳🇬 DPI Sandbox Services"
        NIN["🆔 NIN Service<br/>:8005<br/>• Identity Verification<br/>• Dojah Integration<br/>• Status Tracking"]
        BVN["🏦 BVN Service<br/>:8006<br/>• Bank Verification<br/>• Financial Identity<br/>• Validation"]
        SMS_SVC["📲 SMS Service<br/>:8003<br/>• Nigerian Numbers<br/>• OTP Generation<br/>• Notifications"]
        AI_SVC["🧠 AI Service<br/>:8002<br/>• Nigerian Context<br/>• Content Generation<br/>• Language Processing"]
        IVR["📞 IVR Service<br/>• Voice Interactions<br/>• Call Routing<br/>• USSD Integration"]
        TWO_WAY_SMS["💬 Two-Way SMS<br/>• Interactive SMS<br/>• Response Handling<br/>• Conversation Flow"]
    end

    %% Data Layer
    subgraph "💾 Data Stores"
        POSTGRES[("🐘 PostgreSQL<br/>Primary Database<br/>• User Management<br/>• Service Data<br/>• Audit Logs")]
        MONGO[("🍃 MongoDB<br/>Document Store<br/>• Flexible Schemas<br/>• JSON Documents<br/>• Analytics Data")]
        REDIS[("🔴 Redis<br/>Cache & Sessions<br/>• JWT Tokens<br/>• Rate Limiting<br/>• Temporary Data")]
    end

    %% Configuration & Deployment
    subgraph "📋 Configuration & Deployment"
        ENV_CONFIG[("📄 .env<br/>Centralized Config<br/>• All Service Settings<br/>• API Keys<br/>• Database URLs")]
        YAML_CONFIG[("📝 YAML Configs<br/>• Environment Overrides<br/>• Service Settings<br/>• Feature Flags")]
        DOCKER[("🐳 Docker<br/>Containerization<br/>• Service Images<br/>• Development<br/>• Production")]
        K8S[("☸️ Kubernetes<br/>Orchestration<br/>• Auto-scaling<br/>• Load Balancing<br/>• Health Monitoring")]
    end

    %% Monitoring & Logging
    subgraph "📊 Monitoring & Analytics"
        PROMETHEUS[("📈 Prometheus<br/>Metrics Collection<br/>• Service Metrics<br/>• Performance Data<br/>• Alerts")]
        GRAFANA[("📊 Grafana<br/>Visualization<br/>• Dashboards<br/>• Real-time Monitoring<br/>• Analytics")]
        LOGS[("📋 Structured Logs<br/>• User Activity<br/>• API Access<br/>• Security Events<br/>• Service Health")]
    end

    %% Scripts & Automation
    subgraph "🔧 Automation & Scripts"
        SETUP_SCRIPTS[("⚡ Setup Scripts<br/>• Database Setup<br/>• Admin User Creation<br/>• Platform Startup")]
        DEPLOY_SCRIPTS[("🚀 Deployment<br/>• Image Building<br/>• Helm Charts<br/>• Environment Deploy")]
        TEST_SCRIPTS[("🧪 Testing<br/>• API Testing<br/>• Mock Data<br/>• Health Checks")]
    end

    %% User Flow Connections
    STARTUPS --> GATEWAY
    ADMIN --> GATEWAY
    
    %% Gateway Routing
    GATEWAY --> AUTH
    GATEWAY --> NIN
    GATEWAY --> BVN
    GATEWAY --> SMS_SVC
    GATEWAY --> AI_SVC
    GATEWAY --> IVR
    GATEWAY --> TWO_WAY_SMS

    %% Service Dependencies
    AUTH --> POSTGRES
    AUTH --> REDIS
    CONFIG --> YAML_CONFIG
    CONFIG --> ENV_CONFIG
    
    %% DPI Service Connections
    NIN --> DOJAH
    NIN --> POSTGRES
    BVN --> DOJAH
    BVN --> POSTGRES
    SMS_SVC --> SMS_PROVIDER
    SMS_SVC --> POSTGRES
    AI_SVC --> AI_PROVIDER
    AI_SVC --> MONGO
    IVR --> POSTGRES
    TWO_WAY_SMS --> SMS_PROVIDER
    TWO_WAY_SMS --> POSTGRES

    %% Configuration Flow
    ENV_CONFIG --> AUTH
    ENV_CONFIG --> NIN
    ENV_CONFIG --> BVN
    ENV_CONFIG --> SMS_SVC
    ENV_CONFIG --> AI_SVC
    YAML_CONFIG --> CONFIG

    %% Monitoring Connections
    AUTH --> PROMETHEUS
    GATEWAY --> PROMETHEUS
    NIN --> PROMETHEUS
    BVN --> PROMETHEUS
    SMS_SVC --> PROMETHEUS
    AI_SVC --> PROMETHEUS
    PROMETHEUS --> GRAFANA
    
    %% Logging Flow
    AUTH --> LOGS
    GATEWAY --> LOGS
    NIN --> LOGS
    BVN --> LOGS
    SMS_SVC --> LOGS
    AI_SVC --> LOGS

    %% Deployment Flow
    DOCKER --> K8S
    SETUP_SCRIPTS --> POSTGRES
    SETUP_SCRIPTS --> REDIS
    DEPLOY_SCRIPTS --> K8S
    TEST_SCRIPTS --> GATEWAY

    %% Health Monitoring
    HEALTH --> AUTH
    HEALTH --> NIN
    HEALTH --> BVN
    HEALTH --> SMS_SVC
    HEALTH --> AI_SVC
    HEALTH --> POSTGRES
    HEALTH --> REDIS

    %% Light Background Styling
    classDef external fill:#ffffff,stroke:#2196f3,stroke-width:2px,color:#1565c0
    classDef platform fill:#ffffff,stroke:#9c27b0,stroke-width:2px,color:#7b1fa2
    classDef dpi fill:#ffffff,stroke:#4caf50,stroke-width:2px,color:#388e3c
    classDef data fill:#ffffff,stroke:#ff9800,stroke-width:2px,color:#f57c00
    classDef config fill:#ffffff,stroke:#e91e63,stroke-width:2px,color:#c2185b
    classDef monitor fill:#ffffff,stroke:#8bc34a,stroke-width:2px,color:#689f38
    classDef scripts fill:#ffffff,stroke:#00bcd4,stroke-width:2px,color:#0097a7

    class STARTUPS,ADMIN,DOJAH,SMS_PROVIDER,AI_PROVIDER external
    class GATEWAY,AUTH,CONFIG,HEALTH platform
    class NIN,BVN,SMS_SVC,AI_SVC,IVR,TWO_WAY_SMS dpi
    class POSTGRES,MONGO,REDIS data
    class ENV_CONFIG,YAML_CONFIG,DOCKER,K8S config
    class PROMETHEUS,GRAFANA,LOGS monitor
    class SETUP_SCRIPTS,DEPLOY_SCRIPTS,TEST_SCRIPTS scripts
```

### Platform Services

| Service                  | Port | Description                                             |
| ------------------------ | ---- | ------------------------------------------------------- |
| **Auth Service**   | 8000 | OAuth2 authentication, JWT tokens                      |
| **API Gateway**    | 8080 | Request routing, rate limiting, circuit breaking        |
| **Config Service** | 8001 | Centralized configuration management                    |

### DPI Services

| Service                  | Port | Description                                             |
| ------------------------ | ---- | ------------------------------------------------------- |
| **NIN Service**    | 8005 | Nigerian Identity Number verification                   |
| **BVN Service**    | 8006 | Bank Verification Number validation                     |
| **SMS Service**    | 8003 | Nigerian SMS messaging and notifications                |
| **AI Service**     | 8002 | Nigerian-context content generation                     |

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
│   ├── logging/               # Rotational logging system
│   └── redis/                 # Redis configuration
├── config/                    # Centralized YAML configuration
│   ├── environments/          # Environment-specific configs
│   ├── config_loader.py       # Configuration loader
│   ├── logging.yaml           # Rotational logging configuration
│   └── README.md             # Configuration documentation
├── deployment/                # Deployment configurations
│   ├── scripts/               # Build & deployment scripts
│   ├── docker-compose/        # Local development setup
│   ├── helmfile/              # Kubernetes deployment
│   └── monitoring/            # Monitoring configuration
├── scripts/                   # Automation scripts
│   ├── log-rotation-manager.py # Log rotation and management
│   ├── setup-db.sh           # Database setup
│   ├── create-admin-user.py   # Admin user creation
│   ├── start-sandbox.sh       # Platform startup
│   └── analyze-logs.py        # Log analysis tools
├── flow_diagrams/             # Architecture diagrams
│   └── dpi_sandbox_architecture.mmd # Complete system architecture
├── config.yaml               # Base configuration
├── .env.template             # Environment variables template
├── Makefile                  # Comprehensive build and deployment commands
└── README.md
```

## 🔧 Development for Nigerian DPI

### Nigerian Data Formats

- **Phone Numbers**: `+234XXXXXXXXXX` or `0XXXXXXXXXX`
- **NIN**: 11-digit National Identity Number
- **BVN**: 11-digit Bank Verification Number

### Quick Development Commands

```bash
# Complete setup and start
make quick-start

# Start all services
make dev

# Check service health
make health

# Test APIs with Nigerian examples
make test

# Generate mock Nigerian data
make mock-data

# Rotate and manage logs
make rotate-logs

# View log statistics
make log-stats

# Analyze user activity and usage
make analyze-logs
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

### Makefile Deployment

```bash
# Development
make deploy-dev

# Staging
make deploy-staging

# Production (with safety prompts)
make deploy-prod

# Check deployment status
make k8s-status

# View Kubernetes logs
make k8s-logs
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
# Check all services with Makefile
make health

# Show overall system status
make status

# Or check individual services
curl http://localhost:8080/api/v1/dpi/health  # DPI services overview
curl http://localhost:8000/health             # Auth service
curl http://localhost:8005/health             # NIN service
curl http://localhost:8006/health             # BVN service
curl http://localhost:8003/health             # SMS service
```

### Log Management & Analytics

```bash
# Comprehensive log analysis
make analyze-logs

# Security event analysis
make analyze-logs-security

# API performance analysis
make analyze-logs-performance

# Log rotation and cleanup
make rotate-logs
make log-cleanup

# View log statistics
make log-stats

# Real-time monitoring
make logs
make logs-security
```

### Rotational & Persistent Logging System

Advanced logging system with automatic rotation, compression, and long-term persistence for continuous auditing:

```json
{
  "timestamp": "2025-08-25T20:45:30.123Z",
  "service": "nin-service",
  "log_type": "user_activity",
  "user_id": "startup_123",
  "activity": "DPI_NIN_VERIFY",
  "details": {
    "dpi_service": "nin",
    "action": "verify",
    "nin_bvn_hash": "sha256_hash",
    "nigerian_context": true,
    "startup_name": "TechStartup_NG",
    "client_ip": "192.168.1.100",
    "duration_ms": 245.5,
    "success": true
  }
}
```

### Log Categories & Retention

| Category | Size Limit | Retention | Purpose |
|----------|------------|-----------|----------|
| **User Activity** | 50MB | 1 year | Track all user interactions |
| **API Access** | 100MB | 6 months | Monitor API usage patterns |
| **Security Events** | 25MB | 3 years | Security monitoring & forensics |
| **Service Health** | 20MB | 3 months | System performance monitoring |
| **Audit Trail** | 75MB | 7 years | Regulatory compliance |

### Log Management Commands

```bash
# Rotate and compress logs
make rotate-logs

# View log statistics
make log-stats

# Clean up old archives
make log-cleanup

# Analyze security events
make analyze-logs-security

# Monitor API performance
make analyze-logs-performance
```

### Nigerian DPI Compliance

- **NDPR Compliant**: Nigerian Data Protection Regulation compliance
- **PII Protection**: Automatic hashing of NIN/BVN numbers
- **Phone Masking**: Show only last 4 digits of phone numbers
- **7-Year Audit Trail**: Long-term retention for regulatory compliance
- **Startup Tracking**: Monitor API usage by the 9 Nigerian startups

### Analytics Capabilities

- **User Engagement**: Track individual startup activity patterns
- **Service Adoption**: Monitor DPI service usage by startups
- **Peak Hours**: Identify high-traffic periods for capacity planning
- **Security Monitoring**: Real-time detection of suspicious activities
- **Performance Metrics**: API response times and success rates
- **Compliance Reporting**: Generate audit reports for regulatory requirements

### Metrics

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001` (admin/admin123)
- Service Metrics: `http://localhost:8080/metrics`

## 🔐 Security & Authentication

### Admin-Only User Management

- **Closed Sandbox**: Only 9 Nigerian startups have access
- **Admin Control**: Administrators create all user accounts
- **Secure Access**: JWT-based authentication for all API calls
- **Identity Verification**: Integrated NIN/BVN verification services

## 🔒 Security

### Authentication Flow

#### Startup Access (Closed Sandbox)

1. **Account Request**: Startups contact administrators for account creation
2. **Admin Creates Account**: Administrators create accounts via `/api/v1/admin/users`
3. **Credentials Provided**: Startups receive login credentials securely
4. **Login**: Startups login using:
   - OAuth2 compatible: `/api/v1/auth/login`
   - JSON payload: `/api/v1/auth/login/json`
5. **API Access**: Access tokens validated by API Gateway for all service requests
6. **Logout**: Simple logout via `/api/v1/auth/logout`

#### Admin User Management

1. **Create Accounts**: Administrators create startup accounts
2. **Manage Users**: Full user lifecycle management
3. **Reset Passwords**: Admin-controlled password resets
4. **Account Control**: Activate/deactivate accounts as needed

#### Identity Verification

1. **NIN Verification**: Dedicated NIN service at `/api/v1/nin/verify`
2. **BVN Verification**: Dedicated BVN service at `/api/v1/bvn/verify`
3. **Dojah API Integration**: Real-time verification through Dojah API
4. **Status Tracking**: Monitor verification status via respective service endpoints

### Startup Access Examples

```bash
# Login to get access token
curl -X POST http://localhost:8000/api/v1/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"identifier": "startup@company.ng", "password": "your-password"}'

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

# Logout when done
curl -X POST http://localhost:8000/api/v1/auth/logout
```

### Admin User Management

```bash
# Admin login
curl -X POST http://localhost:8000/api/v1/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"identifier": "admin@dpi-sandbox.ng", "password": "admin-password"}'

# Create startup account
curl -X POST http://localhost:8000/api/v1/admin/users \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "startup@company.ng",
    "username": "startup_dev",
    "password": "TempPass123",
    "first_name": "Startup",
    "last_name": "Developer"
  }'

# List all users
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:8000/api/v1/admin/users

# Reset user password
curl -X POST http://localhost:8000/api/v1/admin/users/1/reset-password \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_password": "NewPass123"}'
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

#### Authentication (Startup Access)

```bash
# User Authentication
POST /api/v1/auth/login             # OAuth2 compatible login
POST /api/v1/auth/login/json        # JSON payload login
POST /api/v1/auth/logout            # Logout
GET  /api/v1/auth/me                # Get current user

# Admin User Management (Admin Only)
POST /api/v1/admin/users            # Create user account
GET  /api/v1/admin/users            # List all users
GET  /api/v1/admin/users/{id}       # Get user by ID
PUT  /api/v1/admin/users/{id}       # Update user
DELETE /api/v1/admin/users/{id}     # Delete user
POST /api/v1/admin/users/{id}/activate      # Activate account
POST /api/v1/admin/users/{id}/deactivate    # Deactivate account
POST /api/v1/admin/users/{id}/reset-password # Reset password

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

### Quick Reference for Nigerian Startups

- [Database Guide](docs/DATABASE.md) - Consolidated PostgreSQL database architecture
- [Configuration Guide](config/README.md) - YAML + centralized .env configuration
- [Scripts Directory](scripts/README.md) - All platform scripts and utilities
- [Database Setup](scripts/setup-db.sh) - One-command database setup and migrations
- [Admin User Setup](scripts/create-admin-user.py) - Create initial admin accounts
- [Platform Startup](scripts/start-sandbox.sh) - Start entire sandbox platform
- [DPI API Guide](docs/DPI-API-GUIDE.md) - Complete API reference with Nigerian examples
- [Mock Data Generator](scripts/mock-data.py) - Generate realistic Nigerian test data
- [API Testing Script](scripts/test-dpi-apis.sh) - Test complete DPI workflows
- [Service Health Checker](scripts/check-services.sh) - Monitor all services
- [Startup Guide](docs/STARTUP-GUIDE.md) - Startup Access Guide

### Detailed Documentation

- [Configuration Management](config/README.md) - YAML-based configuration system
- [Deployment Guide](deployment/README.md) - Comprehensive deployment instructions
- [Auth Service](services/auth-service/README.md) - OAuth2, JWT, and password management
- [API Gateway](services/api-gateway/README.md) - Gateway configuration and usage
- [Sandbox Services](sandbox/README.md) - DPI services overview

### Service-Specific Documentation

- **Auth Service**: OAuth2 flows, admin-only user management, JWT tokens
- **API Gateway**: Request routing, rate limiting, service discovery
- **NIN Service**: Nigerian Identity Number verification via Dojah API
- **BVN Service**: Bank Verification Number validation
- **SMS Service**: Nigerian SMS messaging and notifications
- **AI Service**: Nigerian-context content generation

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
