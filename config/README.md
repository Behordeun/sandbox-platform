# ⚙️ Configuration Management

**Centralized configuration with .env file priority and optional YAML overlays.**

## 📁 Structure

```
config/
├── config_loader.py          # YAML configuration loader utility
├── environments/
│   ├── development.yaml      # Development YAML overrides (optional)
│   ├── staging.yaml         # Staging YAML overrides (optional)
│   └── production.yaml      # Production YAML overrides (optional)
├── app/core/
│   ├── config.py            # Direct .env configuration
│   └── yaml_config.py       # YAML + .env hybrid configuration
└── README.md
```

## 🔧 Configuration Architecture

### Primary: Centralized .env File
**All services read from the root `.env` file as the single source of truth.**

```bash
# Root .env file (PRIMARY configuration)
DATABASE_URL=postgresql://postgres:password@localhost:5432/sandbox_platform
JWT_SECRET_KEY=your-secret-key
DOJAH_API_KEY=your-dojah-key
SMS_API_KEY=your-sms-key
```

### Dual Configuration Support

#### Option 1: Direct .env Configuration (Recommended)
```python
# services/auth-service/app/core/config.py
from app.core.config import settings

# Directly reads from root .env file
print(settings.database_url)  # From DATABASE_URL
print(settings.jwt_secret_key)  # From JWT_SECRET_KEY
```

#### Option 2: YAML + .env Hybrid Configuration
```python
# services/auth-service/app/core/yaml_config.py
from app.core.yaml_config import settings

# Reads YAML config with .env fallback/override
# Environment variables ALWAYS take priority
print(settings.database_url)  # .env overrides YAML
```

### Environment Variable Priority
```python
# Priority order (highest to lowest):
# 1. Environment variables from .env file
# 2. YAML configuration values
# 3. Default values in code

# Example:
database_url = os.getenv("DATABASE_URL") or yaml_config.get("database_url") or "default_url"
```

## 🎯 Key Features

- **✅ Single Source of Truth**: Root .env file for all services
- **✅ Environment Variable Priority**: .env values override YAML configuration
- **✅ Automatic Fallbacks**: Services work without YAML files
- **✅ Dual Configuration Support**: Both config.py and yaml_config.py available
- **✅ Centralized Management**: One file to manage across environments
- **✅ No Configuration Drift**: Consistent settings across all services
- **✅ Easy Deployment**: Single .env file for production

## 🚀 Recent Updates

- **Fixed Import Paths**: All yaml_config files now properly import config_loader
- **Added Fallback Mechanisms**: Services work even without YAML configuration
- **Centralized Environment Loading**: All services read from root .env file
- **Environment Variable Priority**: .env values always override YAML configuration
- **Robust Error Handling**: Graceful fallbacks when config_loader is unavailable

---

**Single .env file, dual configuration support, environment variable priority** ⚙️