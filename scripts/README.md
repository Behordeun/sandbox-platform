# 📜 DPI Sandbox Platform - Scripts Directory

**Complete automation scripts for Nigerian DPI services sandbox.**

## 🚀 Quick Start

```bash
# 1. Start platform (sets up DB, runs migrations, verifies schema)
./scripts/start-sandbox.sh

# 2. Test platform
./scripts/check-services.sh
./scripts/test-dpi-apis.sh
```

## 📋 Core Scripts

### **Database & Setup**

- **`setup-db.sh`** - Database setup with migrations and privilege fixes
- **`migrate-db.py`** - Database migration manager (with fallback table creation)
- **`create-admin-user.py`** - Create admin users
 - **`verify-auth-db.py`** - Verifies presence of critical auth tables and FKs

### **Platform Control**

- **`start-sandbox.sh`** - Start entire platform
- **`stop-sandbox.sh`** - Stop all services
- **`check-services.sh`** - Health check all services

### **Development & Testing**

- **`mock-data.py`** - Generate Nigerian test data
- **`test-dpi-apis.sh`** - Test DPI APIs
- **`analyze-logs.py`** - Log analysis tool

## 🔧 Script Details

### setup-db.sh

**Purpose**: One-command database setup

```bash
./scripts/setup-db.sh
```

- Starts PostgreSQL with Docker
- Creates sandbox_platform database
- Runs migrations with table prefixes
- Installs Python dependencies

### start-sandbox.sh

**Purpose**: Start entire platform

```bash
./scripts/start-sandbox.sh

# Options:
./scripts/start-sandbox.sh --no-db
./scripts/start-sandbox.sh --check-only
```

- Validates .env configuration
- Starts infrastructure (PostgreSQL, Redis)
- Ensures DB readiness (`PGPASSWORD`), runs Alembic for auth, falls back to direct table creation if needed
- Verifies schema (`scripts/verify-auth-db.py`)
- Starts all services (auth, gateway, sandbox services)
- Performs health checks

### create-admin-user.py

**Purpose**: Create admin users

```bash
./scripts/create-admin-user.py
```

- Creates [admin@dpi-sandbox.ng](email-to:admin@dpi-sandbox.ng)
- Sets up platform administrators
- Required for startup account creation

### test-dpi-apis.sh

**Purpose**: Test complete DPI workflows

```bash
./scripts/test-dpi-apis.sh
```

- Tests admin login and user creation
- Tests NIN/BVN verification
- Tests SMS services
- Tests authentication flow

## 🔄 Development Workflow

### For Administrators

```bash
# Setup
cp .env.template .env
./scripts/setup-db.sh
./scripts/create-admin-user.py

# Start
./scripts/start-sandbox.sh

# Monitor
./scripts/check-services.sh
./scripts/analyze-logs.py --all
```

### For Developers

```bash
# Test
./scripts/mock-data.py
./scripts/test-dpi-apis.sh

# Monitor
./scripts/check-services.sh
```

## 🛠️ Dependencies

- Docker Desktop
- Python 3.11+
- PostgreSQL client tools
- curl

## 🚨 Troubleshooting

### Configuration Issues

```bash
# Test configuration loading
cd services/auth-service
python3 -c "from app.core.config import settings; print('✅ Config OK')"

# Check environment variables
grep DATABASE_URL .env
echo $DATABASE_URL
```

### Database Issues

```bash
# Check database connection
psql postgresql://sandbox_user:sandbox_password@127.0.0.1:5432/sandbox_platform -c "SELECT 1;"

# Restart database
docker ps | grep postgres
docker restart sandbox-postgres
```

### Service Issues

```bash
# Check service health
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8080/health

# Check logs
tail -f logs/auth-service.log
tail -f logs/api-gateway.log
```

### Import/Module Issues

```bash
# Test imports
cd services/auth-service
python3 -c "import sys; sys.path.append('.'); from app.core.config import settings; print('✅ Imports OK')"
```

## 🚀 Recent Updates

- **✅ Fixed Configuration Issues**: All services now use centralized .env file
- **✅ Resolved Import Errors**: Fixed module import paths across all services  
- **✅ Database Connectivity**: Updated to use correct PostgreSQL credentials
- **✅ Migration System**: Fixed alembic migrations with python3 -m alembic
- **✅ Soft Delete**: Auth tables use soft-delete; cleanup jobs avoid hard deletes
- **✅ Case-Insensitive Uniqueness**: Active users unique by email/username (case-insensitive, partial indexes)
- **✅ Service Health**: All services now start successfully
- **✅ Dual Config Support**: Both config.py and yaml_config.py work properly

---

**Ready for Nigerian DPI development** 🇳🇬
