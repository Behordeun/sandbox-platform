# 📋 Configuration Management

**Centralized YAML-based configuration system for the Sandbox Platform.** This replaces scattered `.env` files with a robust, maintainable configuration structure.

## 🎯 Why YAML Configuration?

### **Benefits Over .env Files:**
- **Hierarchical Structure**: Organize related settings together
- **Environment Overrides**: Easy environment-specific configurations
- **Type Safety**: Better validation and type checking
- **Comments & Documentation**: Self-documenting configuration files
- **Centralized Management**: Single source of truth for all services
- **Version Control Friendly**: Easy to track configuration changes

## 📁 Configuration Structure

```
config/
├── config.yaml              # Base configuration for all services
├── environments/
│   ├── development.yaml     # Development overrides
│   ├── staging.yaml         # Staging overrides
│   └── production.yaml      # Production overrides
├── config_loader.py         # Python configuration loader
└── README.md               # This file
```

## 🚀 Quick Start

### 1. **Set Environment**
```bash
export ENVIRONMENT=development  # or staging, production
```

### 2. **Set Required Environment Variables**
```bash
# Copy template and fill in values
cp .env.template .env

# Edit with your actual credentials
nano .env
```

### 3. **Use in Your Service**
```python
from config.config_loader import get_service_config

# Get configuration for your service
config = get_service_config("auth_service")
print(f"Service running on port: {config['port']}")
```

## 📚 Configuration Files

### **Base Configuration (`config.yaml`)**
Contains default settings for all services:
- Platform-wide settings
- Service definitions with ports and basic config
- Database configurations
- External provider settings (Doja, SMS, AI)
- Logging and monitoring setup
- Nigerian-specific configurations

### **Environment Overrides**
Each environment file overrides base settings:

#### **Development (`environments/development.yaml`)**
- Debug mode enabled
- SQLite database for easy setup
- Sandbox API endpoints
- Relaxed security settings
- Verbose logging

#### **Production (`environments/production.yaml`)**
- Debug mode disabled
- PostgreSQL database
- Live API endpoints
- Strict security settings
- Optimized logging

## 🔧 Using Configuration in Services

### **Python Services**
```python
# In your service's config file
from config.config_loader import get_service_config, get_provider_config

# Get service-specific configuration
service_config = get_service_config("nin_service")
port = service_config.get("port", 8005)

# Get provider configuration
doja_config = get_provider_config("doja")
api_key = doja_config.get("api_key")
```

### **Environment Variable Substitution**
Configuration supports environment variable substitution:
```yaml
providers:
  doja:
    api_key: "${DOJAH_API_KEY}"           # Required env var
    timeout: "${DOJA_TIMEOUT:30}"        # Optional with default
```

## 🏗️ Service Configuration Examples

### **Auth Service Configuration**
```yaml
services:
  auth_service:
    host: "0.0.0.0"
    port: 8000
    debug: false
    jwt:
      secret_key: "${JWT_SECRET_KEY}"
      algorithm: "HS256"
      access_token_expire_minutes: 30
    database:
      url: "postgresql://user:pass@host:5432/db"
```

### **NIN Service Configuration**
```yaml
sandbox:
  nin_service:
    host: "0.0.0.0"
    port: 8005
    debug: false
    cache_ttl: 3600
    doja_integration: true

providers:
  doja:
    base_url: "https://api.dojah.io"
    api_key: "${DOJAH_API_KEY}"
    app_id: "${DOJAH_APP_ID}"
```

## 🔒 Security Best Practices

### **Environment Variables**
- **Never commit** actual credentials to version control
- Use `.env.template` for documentation
- Store sensitive values in environment variables
- Use different credentials for each environment

### **Configuration Security**
```yaml
# ✅ Good - Use environment variables
database:
  password: "${DB_PASSWORD}"

# ❌ Bad - Hardcoded credentials
database:
  password: "hardcoded-password"
```

## 🛠️ Development Workflow

### **Adding New Configuration**
1. **Add to base config** (`config.yaml`)
2. **Add environment overrides** if needed
3. **Update service code** to use new config
4. **Update `.env.template`** with new variables
5. **Test in development** environment

### **Environment-Specific Settings**
```yaml
# Development - relaxed settings
services:
  auth_service:
    debug: true
    jwt:
      access_token_expire_minutes: 60  # Longer for development

# Production - strict settings  
services:
  auth_service:
    debug: false
    jwt:
      access_token_expire_minutes: 15  # Shorter for security
```

## 📊 Configuration Validation

### **Type Checking**
The configuration loader provides type safety:
```python
from config.config_loader import get_service_config

config = get_service_config("auth_service")
port: int = config.get("port", 8000)  # Type-safe access
```

### **Required vs Optional**
```yaml
# Required (will fail if not provided)
jwt:
  secret_key: "${JWT_SECRET_KEY}"

# Optional with default
jwt:
  algorithm: "${JWT_ALGORITHM:HS256}"
```

## 🚀 Deployment

### **Docker Deployment**
```bash
# Set environment in container
docker run -e ENVIRONMENT=production \
           -e JWT_SECRET_KEY=your-secret \
           your-service:latest
```

### **Kubernetes Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: auth-service
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: auth-secrets
              key: jwt-secret
```

## 🔍 Troubleshooting

### **Common Issues**

#### **Configuration Not Loading**
```bash
# Check environment variable
echo $ENVIRONMENT

# Verify config file exists
ls config/environments/development.yaml
```

#### **Environment Variables Not Substituted**
```bash
# Check if environment variable is set
echo $DOJAH_API_KEY

# Verify syntax in YAML (use ${VAR_NAME})
```

#### **Service Can't Find Configuration**
```python
# Check Python path
import sys
sys.path.append("path/to/config")

# Verify config loader import
from config.config_loader import get_service_config
```

## 📞 Support

- **Configuration Issues**: Check this README and examples
- **Environment Setup**: Use `.env.template` as reference
- **Service Integration**: See service-specific `yaml_config.py` files
- **Production Deployment**: Follow security best practices above

---

**Ready to manage configuration like a pro?** This YAML-based system provides the foundation for scalable, maintainable configuration management across the entire Sandbox Platform.

*Centralized configuration for distributed services* ⚙️🇳🇬