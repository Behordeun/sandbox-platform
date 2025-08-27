# ⚙️ Configuration Management

**Centralized YAML configuration with environment variable integration.**

## 📁 Structure

```
config/
├── config_loader.py          # Configuration loader utility
├── environments/
│   ├── development.yaml      # Development overrides
│   ├── staging.yaml         # Staging overrides
│   └── production.yaml      # Production overrides
└── README.md
```

## 🔧 Usage

### Load Configuration
```python
from config_loader import get_config, get_service_config

# Get full configuration
config = get_config("development")

# Get service-specific configuration
auth_config = get_service_config("auth_service", "development")
```

### Environment Variables
Configuration supports environment variable substitution:

```yaml
database:
  url: "${DATABASE_URL}"
  password: "${DB_PASSWORD:default_password}"
```

## 🎯 Key Features

- **Environment-specific overrides**
- **Automatic environment variable substitution**
- **Service-specific configuration sections**
- **Configuration caching for performance**
- **Deep merge of configuration layers**

---

**Centralized configuration for all services** ⚙️