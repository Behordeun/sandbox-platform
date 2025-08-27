# 🗄️ Database Architecture & Migration Guide

**Consolidated PostgreSQL database with service-specific table prefixes for the Sandbox Platform.**

## 🎯 Database Architecture

### **Single Database Design**
- **Database Name**: `sandbox_platform`
- **Engine**: PostgreSQL 14+
- **Architecture**: Single database with table prefixes for service isolation

### **Table Prefixes by Service**
```yaml
Table Prefixes:
  auth_service: "auth_"          # auth_users, auth_oauth_clients, auth_oauth_tokens
  config_service: "config_"      # config_settings, config_versions
  nin_service: "nin_"            # nin_verifications, nin_cache
  bvn_service: "bvn_"            # bvn_verifications, bvn_cache
  sms_service: "sms_"            # sms_messages, sms_logs
  ai_service: "ai_"              # ai_requests, ai_responses
  ivr_service: "ivr_"            # ivr_calls, ivr_sessions
  two_way_sms_service: "twoway_sms_"  # twoway_sms_conversations
```

## 🚀 Quick Database Setup

### **One-Command Setup**
```bash
# Complete database setup with migrations
./setup-db.sh
```

### **Manual Setup**
```bash
# 1. Start PostgreSQL
docker run -d \
  --name sandbox-postgres \
  -e POSTGRES_USER=sandbox_user \
  -e POSTGRES_PASSWORD=sandbox_password \
  -e POSTGRES_DB=sandbox_platform \
  -p 5432:5432 \
  postgres:14

# 2. Run migrations
python migrate-db.py
```

## 🔧 Configuration

### **Database Connection**
```yaml
# config.yaml
database:
  url: "postgresql://sandbox_user:${DB_PASSWORD}@localhost:5432/sandbox_platform"
  pool_size: 20
  max_overflow: 40
  table_prefixes:
    auth_service: "auth_"
    # ... other services
```

### **Environment Variables**
```env
# .env (root file)
DATABASE_URL=postgresql://sandbox_user:sandbox_password@localhost:5432/sandbox_platform
DB_PASSWORD=sandbox_password
```

## 📊 Migration System

### **Centralized Migrations**
- **Script**: `migrate-db.py` - Handles all service migrations
- **Setup**: `setup-db.sh` - Complete database setup
- **Individual**: Each service can run migrations independently

### **Migration Commands**
```bash
# Run all migrations
python migrate-db.py

# Individual service migration
cd services/auth-service
alembic upgrade head
```

## 🛡️ Benefits

### **Operational Benefits**
- **Single database** to manage and backup
- **Shared connection pooling** for better resource utilization
- **Centralized monitoring** and maintenance
- **Simplified deployment** with one database instance

### **Development Benefits**
- **Consistent environment** across dev/staging/prod
- **Easy local setup** with single database
- **Cross-service queries** possible when needed
- **Unified migration system**

### **Cost Benefits**
- **Lower infrastructure costs** - one database instance
- **Reduced maintenance overhead**
- **Better resource utilization**

## 🔍 Table Structure Examples

### **Auth Service Tables**
```sql
-- Users table with auth_ prefix
CREATE TABLE auth_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    nin_verified BOOLEAN DEFAULT FALSE,
    bvn_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- OAuth clients table
CREATE TABLE auth_oauth_clients (
    id SERIAL PRIMARY KEY,
    client_id VARCHAR(255) UNIQUE NOT NULL,
    client_secret VARCHAR(255) NOT NULL,
    client_name VARCHAR(255) NOT NULL
);
```

### **NIN Service Tables**
```sql
-- NIN verifications with nin_ prefix
CREATE TABLE nin_verifications (
    id SERIAL PRIMARY KEY,
    nin VARCHAR(11) NOT NULL,
    user_id INTEGER,
    verification_status VARCHAR(50),
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🚀 Production Deployment

### **Environment-Specific Settings**
```bash
# Development
export ENVIRONMENT=development
export DB_PASSWORD=sandbox_password

# Production
export ENVIRONMENT=production
export DB_PASSWORD=secure-production-password
```

### **Backup & Recovery**
```bash
# Backup entire platform database
pg_dump -h localhost -U sandbox_user sandbox_platform > backup.sql

# Restore
psql -h localhost -U sandbox_user sandbox_platform < backup.sql
```

## 🔍 Monitoring

### **Database Health**
```bash
# Check database connection
psql -h localhost -U sandbox_user -d sandbox_platform -c "SELECT 1;"

# Check table sizes
psql -h localhost -U sandbox_user -d sandbox_platform -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

### **Connection Monitoring**
```sql
-- Active connections by service (based on application_name)
SELECT application_name, count(*) 
FROM pg_stat_activity 
WHERE state = 'active' 
GROUP BY application_name;
```

---

**Ready to manage your consolidated database?** This architecture provides the foundation for scalable, maintainable data management across the entire Sandbox Platform.

*One database, many services, infinite possibilities* 🗄️🇳🇬