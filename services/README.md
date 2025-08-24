# Platform Services

The services directory contains platform maintenance services that support the core sandbox offerings - authentication, API gateway, monitoring, and other infrastructure components.

## 🚀 Quick Start for DPI Development

### One-Command Setup

```bash
# From project root - starts everything
./sandbox-start.sh
```

### Individual Commands

```bash
# Infrastructure only (databases & Redis)
./start-infrastructure.sh
./stop-infrastructure.sh

# Platform services only
./start-all.sh
./stop-all.sh

# Health monitoring
./check-services.sh

# Clean shutdown
./stop-all.sh --clean-logs
./stop-infrastructure.sh --clean-volumes
```

## 📋 Services Overview

| Service | Port | Description | Status |
|---------|------|-------------|--------|
| **Auth Service** | 8000 | OAuth2 authentication & JWT tokens | ✅ Active |
| **API Gateway** | 8080 | Request routing & rate limiting | ✅ Active |
| **Rate Limiter** | 8008 | Advanced rate limiting service | 🚧 Development |
| **Health Service** | 8009 | Service health monitoring | 🚧 Development |
| **Logging** | 8010 | Centralized logging service | 🚧 Development |
| **Monitoring** | 8011 | Metrics collection & alerting | 🚧 Development |

## 🗄️ Infrastructure Services

| Service | Port | Credentials |
|---------|------|-------------|
| **PostgreSQL** | 5432 | sandbox_user/sandbox_password |
| **Redis** | 6379 | No authentication |
| **MongoDB** | 27017 | sandbox_user/sandbox_password |

## 🔧 Management Scripts

### `dev-setup.sh`

Complete development environment setup

```bash
./dev-setup.sh                    # Full setup
./dev-setup.sh --infrastructure-only  # Infrastructure only
./dev-setup.sh --services-only       # Services only
```

### `start-all.sh`

Start all platform services

- Installs dependencies automatically
- Runs services in background
- Creates PID files for management
- Generates service logs

### `stop-all.sh`

Stop all platform services

```bash
./stop-all.sh                # Stop services
./stop-all.sh --clean-logs   # Stop and clean logs
```

### `start-infrastructure.sh`

Start infrastructure with Docker

- PostgreSQL database
- Redis cache
- MongoDB document store

### `stop-infrastructure.sh`

Stop infrastructure services

```bash
./stop-infrastructure.sh              # Stop containers
./stop-infrastructure.sh --clean-volumes  # Stop and clean volumes
```

## 📊 Monitoring

### Service Health

```bash
# Check all DPI services at once
./check-services.sh

# Check DPI-specific services
curl http://localhost:8080/api/v1/dpi/health

# Individual service checks
curl http://localhost:8000/health  # Auth
curl http://localhost:8080/health  # Gateway
curl http://localhost:8005/health  # NIN
curl http://localhost:8006/health  # BVN
curl http://localhost:8003/health  # SMS
```

### Logs

```bash
# View all logs
tail -f logs/*.log

# Specific service
tail -f logs/auth-service.log
tail -f logs/api-gateway.log
```

### Process Management

```bash
# Check running services
ps aux | grep uvicorn

# View PID files
ls -la logs/*.pid
```

## 🔧 Development

### Adding New Services

1. Create service directory in `services/`
2. Add to `start-all.sh` and `stop-all.sh`
3. Update port assignments
4. Add health check endpoint

### Environment Setup

Each service uses `.env` files for configuration:

```bash
# Copy environment templates
cd auth-service && cp .env.example .env
cd api-gateway && cp .env.example .env
```

### Database Migrations

```bash
# Auth service migrations
cd auth-service
alembic upgrade head
```

## 🐳 Docker Alternative

### Using Docker Compose

```bash
# From project root
docker-compose -f deployment/docker-compose/docker-compose.dev.yml up services
```

### Individual Service Containers

```bash
# Build and run auth service
cd auth-service
docker build -t sandbox-auth:latest .
docker run -p 8000:8000 sandbox-auth:latest
```

## 🔧 Troubleshooting

### Common Issues

**Port Already in Use**:

```bash
# Find process using port
lsof -i :8000
kill -9 <PID>
```

**Service Won't Start**:

```bash
# Check logs
cat logs/auth-service.log

# Check dependencies
cd auth-service && pip install -r requirements.txt
```

**Database Connection Issues**:

```bash
# Test PostgreSQL
psql -h localhost -U sandbox_user -d sandbox_db

# Test Redis
redis-cli ping

# Test MongoDB
mongo mongodb://sandbox_user:sandbox_password@localhost:27017/sandbox_db
```

### Clean Reset

```bash
# Stop everything and clean up
./stop-all.sh --clean-logs
./stop-infrastructure.sh --clean-volumes

# Restart fresh
./dev-setup.sh
```

## 📚 Documentation

- [Auth Service](auth-service/README.md) - OAuth2 & JWT authentication
- [API Gateway](api-gateway/README.md) - Request routing & rate limiting
- [Deployment Guide](../deployment/README.md) - Production deployment
- [Sandbox Services](../sandbox/README.md) - Core business offerings

---

## Platform services for Nigerian startup innovation 🇳🇬
