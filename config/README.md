# Sandbox Config Service

A centralized configuration management service built with FastAPI for the Sandbox Platform. This service provides secure storage, versioning, and management of application configurations across different environments.

## Features

- **Centralized Configuration**: Store and manage all application configurations in one place
- **Environment Management**: Support for multiple environments (development, staging, production)
- **Encryption**: Automatic encryption of sensitive configuration values
- **Versioning**: Track configuration changes with full version history
- **Multiple Storage Backends**: Support for memory, Redis, and file-based storage
- **Configuration Diff**: Compare different versions of configurations
- **Hot Reload**: Dynamic configuration updates without service restarts
- **REST API**: Full REST API for configuration management
- **Type Safety**: Pydantic models for configuration validation

## Quick Start

### Local Development

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

```bash
docker build -t your-dockerhub-username/sandbox-config-service:1.0.0 .
docker run -p 8000:8000 \
  -e CONFIG_STORAGE_TYPE="redis" \
  -e REDIS_URL="redis://redis:6379/0" \
  -e ENCRYPTION_KEY="your-secure-encryption-key" \
  your-dockerhub-username/sandbox-config-service:1.0.0
```

## API Endpoints

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
# Automatically encrypted keys
sensitive_keys = [
    'password', 'secret', 'key', 'token', 'api_key',
    'private_key', 'certificate', 'credential'
]
```

### Custom Sensitive Keys

```json
{
  "encrypt_sensitive": true,
  "sensitive_keys": ["custom_secret", "api_token"]
}
```

## Environment Management

### Supported Environments

- `development` - Development environment
- `staging` - Staging environment  
- `production` - Production environment

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

```python
import httpx

class ConfigClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def get_config(self, config_id: str) -> dict:
        response = await self.client.get(f"{self.base_url}/api/v1/configs/{config_id}/data")
        return response.json()
    
    async def get_config_value(self, config_id: str, key: str):
        response = await self.client.get(
            f"{self.base_url}/api/v1/configs/{config_id}/data",
            params={"key": key}
        )
        return response.json()["value"]

# Usage
config_client = ConfigClient("http://config-service:8000")
db_config = await config_client.get_config("postgres-prod")
```

### Environment Variables

```python
import os
from config_client import ConfigClient

# Fallback to environment variables
def get_config_value(config_id: str, key: str, env_var: str = None):
    try:
        return config_client.get_config_value(config_id, key)
    except:
        return os.getenv(env_var) if env_var else None

db_host = get_config_value("postgres-prod", "host", "DB_HOST")
```

## Monitoring

### Health Checks

```bash
curl http://localhost:8000/health
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

### Metrics

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

```bash
# Run tests
pytest tests/

# Test with different storage backends
CONFIG_STORAGE_TYPE=memory pytest tests/
CONFIG_STORAGE_TYPE=redis pytest tests/
```

## Deployment

### Kubernetes

The service is designed for Kubernetes deployment with:

- ConfigMaps for non-sensitive configuration
- Secrets for encryption keys
- Persistent volumes for file storage
- Health checks for liveness/readiness

### High Availability

- Stateless design (state in storage backend)
- Redis clustering for distributed storage
- Load balancer friendly
- Graceful shutdown handling

## Best Practices

### Configuration Organization

1. **Use descriptive names**: `postgres-prod-primary` vs `db1`
2. **Consistent environments**: Use standard environment names
3. **Meaningful tags**: Tag configurations for easy filtering
4. **Version descriptions**: Add change summaries to versions

### Security

1. **Encrypt sensitive data**: Always encrypt passwords, keys, tokens
2. **Use strong encryption keys**: Generate secure encryption keys
3. **Rotate keys regularly**: Implement key rotation procedures
4. **Audit access**: Monitor configuration access patterns

### Performance

1. **Use appropriate storage**: Redis for high-performance, file for simplicity
2. **Cache frequently accessed configs**: Implement client-side caching
3. **Limit version history**: Configure appropriate max_versions
4. **Monitor storage size**: Track configuration storage growth

## Troubleshooting

### Common Issues

1. **Configuration not found (404)**:
   - Verify configuration ID
   - Check environment filters
   - Ensure configuration exists

2. **Decryption failed**:
   - Verify encryption key
   - Check if value was encrypted
   - Ensure key hasn't changed

3. **Storage connection failed**:
   - Check Redis/storage connectivity
   - Verify connection credentials
   - Monitor storage backend health

### Debugging

```bash
# Check service health
curl http://localhost:8000/health

# List all configurations
curl http://localhost:8000/api/v1/configs

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
