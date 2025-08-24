# Sandbox Services

The sandbox directory contains the core business offerings of the Sandbox Platform - specialized microservices designed for Nigerian startups to rapidly prototype and deploy applications.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional)
- Doja API credentials (for NIN/BVN services)

### Start All Services
```bash
# From sandbox directory
./start-all.sh

# Or individually
cd ai && uvicorn app.main:app --reload --port 8002
cd sms && uvicorn app.main:app --reload --port 8003
cd ivr && uvicorn app.main:app --reload --port 8004
cd nin && uvicorn app.main:app --reload --port 8005
cd bvn && uvicorn app.main:app --reload --port 8006
cd two-way-sms && uvicorn app.main:app --reload --port 8007
```

## 📋 Services Overview

| Service | Port | Description | Status |
|---------|------|-------------|--------|
| **AI Service** | 8002 | Content generation & data analysis | ✅ Active |
| **SMS Service** | 8003 | SMS messaging & notifications | ✅ Active |
| **IVR Service** | 8004 | Interactive Voice Response | 🚧 Development |
| **NIN Service** | 8005 | Nigerian Identity Number verification | ✅ Active |
| **BVN Service** | 8006 | Bank Verification Number validation | ✅ Active |
| **Two-Way SMS** | 8007 | Bidirectional SMS communication | 🚧 Development |

## 🔧 Service Details

### AI Service (Port 8002)
**Purpose**: AI-powered content generation and data analysis

**Endpoints**:
- `POST /api/v1/generate` - Generate AI content
- `POST /api/v1/analyze` - Analyze data with AI
- `GET /health` - Health check

**Setup**:
```bash
cd ai
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

### SMS Service (Port 8003)
**Purpose**: SMS messaging and notification system

**Features**:
- Send SMS messages
- Delivery status tracking
- Bulk messaging support

**Setup**: See [SMS Service README](sms/README.md)

### IVR Service (Port 8004)
**Purpose**: Interactive Voice Response system

**Endpoints**:
- `POST /api/v1/call` - Initiate IVR call
- `GET /api/v1/menu` - Get IVR menu configuration

**Setup**:
```bash
cd ivr
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8004
```

### NIN Service (Port 8005)
**Purpose**: Nigerian Identity Number verification via Doja API

**Endpoints**:
- `POST /api/v1/verify` - Full NIN verification
- `POST /api/v1/lookup` - Basic NIN lookup
- `GET /api/v1/status/{nin}` - Get verification status

**Configuration**:
```env
DOJA_API_KEY=your-doja-api-key
DOJA_APP_ID=your-doja-app-id
DOJA_BASE_URL=https://api.dojah.io
```

**Setup**:
```bash
cd nin
cp .env.example .env
# Edit .env with your Doja credentials
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8005
```

### BVN Service (Port 8006)
**Purpose**: Bank Verification Number validation via Doja API

**Endpoints**:
- `POST /api/v1/verify` - Full BVN verification
- `POST /api/v1/lookup` - Basic BVN lookup
- `GET /api/v1/status/{bvn}` - Get verification status

**Configuration**:
```env
DOJA_API_KEY=your-doja-api-key
DOJA_APP_ID=your-doja-app-id
DOJA_BASE_URL=https://api.dojah.io
```

**Setup**:
```bash
cd bvn
cp .env.example .env
# Edit .env with your Doja credentials
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8006
```

### Two-Way SMS Service (Port 8007)
**Purpose**: Bidirectional SMS communication

**Endpoints**:
- `POST /api/v1/send` - Send SMS
- `POST /api/v1/receive` - Receive SMS webhook

**Setup**:
```bash
cd two-way-sms
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8007
```

## 🗄️ Data Stores

### PostgreSQL
**Purpose**: Primary relational database for structured data

**Configuration**:
```bash
# Located in data-stores/postgres/
docker run -d \
  --name sandbox-postgres \
  -e POSTGRES_DB=sandbox_db \
  -e POSTGRES_USER=sandbox_user \
  -e POSTGRES_PASSWORD=sandbox_password \
  -p 5432:5432 \
  -v ./data-stores/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql \
  postgres:14
```

### MongoDB
**Purpose**: Document database for flexible schemas

**Configuration**:
```bash
# Located in data-stores/mongo/
docker run -d \
  --name sandbox-mongo \
  -e MONGO_INITDB_ROOT_USERNAME=sandbox_user \
  -e MONGO_INITDB_ROOT_PASSWORD=sandbox_password \
  -e MONGO_INITDB_DATABASE=sandbox_db \
  -p 27017:27017 \
  -v ./data-stores/mongo/init.js:/docker-entrypoint-initdb.d/init.js \
  mongo:6
```

## 🐳 Docker Deployment

### Build All Services
```bash
# Build individual services
docker build -t sandbox-ai:latest ./ai
docker build -t sandbox-nin:latest ./nin
docker build -t sandbox-bvn:latest ./bvn

# Or use the build script
../deployment/scripts/build-images.sh -s sandbox
```

### Run with Docker Compose
```bash
# From project root
docker-compose -f deployment/docker-compose/docker-compose.dev.yml up sandbox-services
```

## 🔐 Security & Authentication

### API Access
All sandbox services are accessed through the API Gateway with authentication:

```bash
# Get auth token first
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token to access sandbox services
curl -X POST http://localhost:8080/api/v1/nin/verify \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nin": "12345678901"}'
```

### Environment Variables
Each service requires specific environment variables. Copy `.env.example` to `.env` in each service directory and configure:

**Common Variables**:
```env
DEBUG=false
HOST=0.0.0.0
PORT=8xxx
```

**Identity Services (NIN/BVN)**:
```env
DOJA_API_KEY=your-doja-api-key
DOJA_APP_ID=your-doja-app-id
DOJA_BASE_URL=https://api.dojah.io
```

## 🧪 Testing

### Health Checks
```bash
# Check all services
curl http://localhost:8002/health  # AI
curl http://localhost:8003/health  # SMS
curl http://localhost:8004/health  # IVR
curl http://localhost:8005/health  # NIN
curl http://localhost:8006/health  # BVN
curl http://localhost:8007/health  # Two-Way SMS
```

### API Testing
```bash
# Test NIN verification
curl -X POST http://localhost:8005/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"nin": "12345678901"}'

# Test BVN verification
curl -X POST http://localhost:8006/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"bvn": "12345678901"}'
```

## 📊 Monitoring

### Service Status
```bash
# Via API Gateway
curl http://localhost:8080/api/v1/services/health

# Individual service metrics
curl http://localhost:8005/metrics  # If metrics enabled
```

### Logs
```bash
# Docker logs
docker logs sandbox-nin
docker logs sandbox-bvn

# Local development
tail -f nin/logs/app.log
tail -f bvn/logs/app.log
```

## 🚀 Development

### Adding New Services
1. Create service directory: `mkdir new-service`
2. Copy template structure from existing service
3. Update `app/main.py` with service-specific logic
4. Add to API Gateway routing
5. Update this README

### Service Template Structure
```
new-service/
├── app/
│   ├── api/v1/
│   │   └── router.py
│   ├── core/
│   │   └── config.py
│   ├── schemas/
│   ├── services/
│   └── main.py
├── .env.example
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🔧 Troubleshooting

### Common Issues

**Service Won't Start**:
```bash
# Check port availability
netstat -tulpn | grep :8005

# Check environment variables
cat .env

# Check dependencies
pip install -r requirements.txt
```

**Doja API Issues**:
```bash
# Verify credentials
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "AppId: YOUR_APP_ID" \
     https://api.dojah.io/api/v1/general/docs

# Check API limits and usage
```

**Database Connection**:
```bash
# Test PostgreSQL
psql -h localhost -U sandbox_user -d sandbox_db

# Test MongoDB
mongo mongodb://sandbox_user:sandbox_password@localhost:27017/sandbox_db
```

## 📚 Documentation

- [API Gateway Integration](../services/api-gateway/README.md)
- [Authentication Setup](../services/auth-service/README.md)
- [Deployment Guide](../deployment/README.md)
- [Doja API Documentation](https://docs.dojah.io/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-sandbox-service`
3. Add your service following the template structure
4. Update this README with service details
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

**Built with ❤️ for Nigerian startups**