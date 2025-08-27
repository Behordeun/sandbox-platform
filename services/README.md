# 🛠️ Platform Services

**Core infrastructure services for the DPI Sandbox Platform.**

## 📋 Services Overview

### **🔐 Auth Service** (Port 8000)
- OAuth2 authentication and JWT token management
- Admin-only user management for 9 Nigerian startups
- Integration with NIN/BVN verification services

### **🌐 API Gateway** (Port 8080)
- Single entry point for all DPI services
- Request routing, rate limiting, and load balancing
- JWT token validation and service discovery

### **⚙️ Config Service** (Port 8001)
- Centralized configuration management
- Environment-specific settings with encryption
- YAML-based configuration with .env integration

## 🚀 Quick Start

```bash
# Start all platform services
cd services/auth-service && uvicorn app.main:app --reload --port 8000
cd services/api-gateway && uvicorn app.main:app --reload --port 8080
```

## 📚 Documentation

- [Auth Service](auth-service/README.md) - Authentication and user management
- [API Gateway](api-gateway/README.md) - Gateway configuration and routing

---

**Platform services powering Nigerian DPI** 🇳🇬