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

```plain text
config/
├── config.yaml              # Base configuration for all services
├── environments/
│   ├── development.yaml     # Development overrides
│   ├── staging.yaml         # Staging overrides
│   └── production.yaml      # Production overrides
├── config_loader.py         # Python configuration loader
└── README.md               # This file
```

1. **Setup environment**:

   ```bash
   cd config-service
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the service**:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the service**:

   - API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### Docker Deployment

### 1. **Set Environment**

```bash
export ENVIRONMENT=development  # or staging, production
```

### 2. **Set Required Environment Variables**

```bash
# Copy template and fill in values
cp .env.template .env

### Configuration Management

- `POST /api/v1/configs` - Create new configuration
- `GET /api/v1/configs` - List all configurations (with filtering)
- `GET /api/v1/configs/{id}` - Get specific configuration
- `PUT /api/v1/configs/{id}` - Update configuration
- `DELETE /api/v1/configs/{id}` - Delete configuration

### Configuration Data

- `GET /api/v1/configs/{id}/data` - Get configuration data
- `GET /api/v1/configs/{id}/data?key=value` - Get specific key

### Versioning

- `GET /api/v1/configs/{id}/history` - Get version history
- `GET /api/v1/configs/{id}/diff?version1=1&version2=2` - Compare versions

### Status Management

- `PATCH /api/v1/configs/{id}/status` - Update configuration status

### System

- `GET /health` - Health check
- `GET /docs` - API documentation

## Configuration Model

### Basic Configuration

```json
{
  "name": "database-config",
  "description": "Database connection settings",
  "config_type": "database",
  "environment": "production",
  "tags": ["database", "postgres"],
  "data": {
    "host": "db.example.com",
    "port": 5432,
    "database": "myapp",
    "username": "dbuser",
    "password": "secret123",
    "ssl_mode": "require"
  },
  "format": "json",
  "encrypt_sensitive": true,
  "sensitive_keys": ["password"]
}
```

### Configuration Types

- `application` - Application-specific settings
- `database` - Database connection configurations
- `cache` - Caching service configurations
- `messaging` - Message queue configurations
- `security` - Security-related settings
- `monitoring` - Monitoring and logging configurations
- `custom` - Custom configuration types

## Storage Backends

### Memory Storage (Default)

- Fast access
- No persistence
- Good for development

```env
CONFIG_STORAGE_TYPE=memory
```

### Redis Storage

- Persistent storage
- High performance
- Distributed access

```env
CONFIG_STORAGE_TYPE=redis
REDIS_URL=redis://localhost:6379/0
```

### File Storage

- File-based persistence
- Simple backup/restore
- Good for single-instance deployments

```env
CONFIG_STORAGE_TYPE=file
CONFIG_FILE_PATH=/app/configs
```

## Security Features

### Encryption

Sensitive configuration values are automatically encrypted:

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

### Environment Filtering

```bash
# Get all production configurations
curl "http://localhost:8000/api/v1/configs?environment=production"

# Get database configs for staging
curl "http://localhost:8000/api/v1/configs?environment=staging&config_type=database"
```

## Configuration Versioning

### Version History

Every configuration change creates a new version:

```json
{
  "config_id": "uuid",
  "versions": [
    {
      "version": 1,
      "data": {...},
      "created_at": "2024-01-01T00:00:00Z",
      "created_by": "user@example.com"
    }
  ]
}
```

### Configuration Diff

Compare any two versions:

```bash
curl "http://localhost:8000/api/v1/configs/{id}/diff?version1=1&version2=2"
```

Response:

```json
{
  "added": {"new_key": "new_value"},
  "removed": {"old_key": "old_value"},
  "modified": {
    "changed_key": {
      "old": "old_value",
      "new": "new_value"
    }
  }
}
```

## Usage Examples

### Create Database Configuration

```bash
curl -X POST "http://localhost:8000/api/v1/configs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "postgres-prod",
    "description": "Production PostgreSQL configuration",
    "config_type": "database",
    "environment": "production",
    "data": {
      "host": "prod-db.example.com",
      "port": 5432,
      "database": "myapp_prod",
      "username": "prod_user",
      "password": "super_secret_password"
    },
    "encrypt_sensitive": true
  }'
```

### Get Configuration Data

```bash
# Get all data
curl "http://localhost:8000/api/v1/configs/{id}/data"

# Get specific key
curl "http://localhost:8000/api/v1/configs/{id}/data?key=host"
```

### Update Configuration

```bash
curl -X PUT "http://localhost:8000/api/v1/configs/{id}" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "host": "new-db.example.com",
      "port": 5432
    }
  }'
```

## Integration

### Application Integration

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

Response:

```json
{
  "status": "healthy",
  "service": "Sandbox Config Service",
  "version": "1.0.0",
  "storage_type": "redis",
  "versioning_enabled": true
}
```

## 🔍 Troubleshooting

The service provides metrics for:

- Configuration read/write operations
- Storage backend performance
- Encryption/decryption operations
- Version history size

## Development

### Project Structure

```plain text
app/
├── api/v1/          # API endpoints
├── core/            # Core utilities and configuration
├── models/          # Pydantic models
├── services/        # Business logic services
└── main.py         # FastAPI application
```

### Adding New Storage Backend

1. **Implement ConfigStorage interface**:

   ```python
   class NewStorage(ConfigStorage):
       async def get(self, config_id: str) -> Optional[Dict[str, Any]]:
           # Implementation
           pass
   ```

2. **Update ConfigManager**:

   ```python
   def _create_storage(self, suffix: str = "") -> ConfigStorage:
       if storage_type == "new_backend":
           return NewStorage()
   ```

### Testing

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

This project is licensed under the MIT License.
