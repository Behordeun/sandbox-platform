# 📜 Scripts Directory

**Centralized location for all platform scripts and utilities.**

## 🚀 Platform Management

### **🔧 Setup & Database**
- **`setup-db.sh`** - Complete database setup with migrations
- **`migrate-db.py`** - Centralized database migration script
- **`create-admin-user.py`** - Create initial admin users

### **🏃 Platform Control**
- **`start-sandbox.sh`** - Start entire sandbox platform
- **`stop-sandbox.sh`** - Stop all services and infrastructure
- **`check-services.sh`** - Health check for all services

### **🧪 Development & Testing**
- **`mock-data.py`** - Generate realistic Nigerian test data
- **`test-dpi-apis.sh`** - Test complete DPI workflows
- **`analyze-logs.py`** - Comprehensive log analysis

### **📊 Legacy Scripts**
- **`start-dev.sh`** - Legacy development startup
- **`sandbox-start.sh`** - Legacy sandbox startup
- **`migrate_*.sh`** - Legacy migration scripts

## 📋 Usage Examples

### **Quick Start**
```bash
# Setup platform
./scripts/setup-db.sh
./scripts/create-admin-user.py

# Start platform
./scripts/start-sandbox.sh

# Check health
./scripts/check-services.sh

# Stop platform
./scripts/stop-sandbox.sh
```

### **Development Workflow**
```bash
# Generate test data
./scripts/mock-data.py

# Test APIs
./scripts/test-dpi-apis.sh

# Analyze logs
./scripts/analyze-logs.py --all
```

## 🔧 Script Permissions

All scripts are executable. If you need to make them executable:
```bash
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

---

**Organized scripts for a cleaner codebase** 📜✨