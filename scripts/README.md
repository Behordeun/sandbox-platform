# 📜 DPI Sandbox Platform - Scripts Directory

**Complete automation scripts for Nigerian DPI services sandbox.**

## 🚀 Quick Start

```bash
# 1. Setup platform
./scripts/setup-db.sh
./scripts/create-admin-user.py

# 2. Start platform
./scripts/start-sandbox.sh

# 3. Test platform
./scripts/check-services.sh
./scripts/test-dpi-apis.sh
```

## 📋 Core Scripts

### **Database & Setup**

- **`setup-db.sh`** - Complete database setup with migrations
- **`migrate-db.py`** - Database migration manager
- **`create-admin-user.py`** - Create admin users

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

### Database Issues

```bash
docker ps | grep postgres
docker restart sandbox-postgres
```

### Service Issues

```bash
./scripts/check-services.sh
tail -f logs/*.log
```

### Permission Issues

```bash
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

---

**Ready for Nigerian DPI development** 🇳🇬
