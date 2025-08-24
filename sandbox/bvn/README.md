# BVN Verification Service

A FastAPI-based Bank Verification Number (BVN) verification service integrated with Doja API for real-time Nigerian banking identity verification.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Doja API credentials (API Key + App ID)
- Internet connection for API calls

### Local Setup
```bash
# Clone and navigate
cd sandbox/bvn

# Copy environment file
cp .env.example .env

# Edit .env with your Doja credentials
nano .env

# Install dependencies
pip install -r requirements.txt

# Start the service
uvicorn app.main:app --reload --port 8006
```

### Verify Setup
```bash
# Health check
curl http://localhost:8006/health

# API documentation
open http://localhost:8006/docs
```

## 📋 Service Overview

**Port**: 8006  
**Purpose**: Bank Verification Number validation via Doja API  
**Integration**: Doja KYC API for real-time BVN verification  

### Key Features
- Real-time BVN verification with Doja API
- Basic BVN lookup functionality
- Structured response with banking details
- Error handling and timeout management
- Docker containerization support

## 🔧 Configuration

### Environment Variables
```env
# Service Configuration
APP_NAME=BVN Verification Service
APP_VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=8006

# Doja API Configuration (Required)
DOJA_API_KEY=your-doja-api-key
DOJA_APP_ID=your-doja-app-id
DOJA_BASE_URL=https://api.dojah.io

# Auth Service URL
AUTH_SERVICE_URL=http://auth-service:8000
```

### Doja API Setup
1. Sign up at [Doja.io](https://dojah.io)
2. Get your API Key and App ID from dashboard
3. Add credentials to `.env` file
4. Test connection with verification endpoint

## 📚 API Endpoints

### Core Endpoints

#### POST /api/v1/verify
**Purpose**: Full BVN verification with Doja API

**Request**:
```json
{
  "bvn": "12345678901"
}
```

**Response**:
```json
{
  "bvn_verified": true,
  "verification_data": {
    "first_name": "John",
    "last_name": "Doe",
    "middle_name": "Smith",
    "date_of_birth": "1990-01-01",
    "gender": "Male",
    "phone_number": "08012345678",
    "email": "john.doe@email.com",
    "address": "123 Main Street, Lagos",
    "state_of_origin": "Lagos",
    "lga_of_origin": "Lagos Island",
    "bvn": "12345678901",
    "enrollment_bank": "First Bank",
    "enrollment_branch": "Victoria Island",
    "watch_listed": "No"
  },
  "message": "BVN verified successfully"
}
```

#### POST /api/v1/lookup
**Purpose**: Basic BVN lookup

**Request**:
```json
{
  "bvn": "12345678901"
}
```

**Response**: Same as verify endpoint

#### GET /api/v1/status/{bvn}
**Purpose**: Get BVN verification status

**Response**:
```json
{
  "message": "BVN 12345678901 status check",
  "bvn": "12345678901"
}
```

#### GET /health
**Purpose**: Service health check

**Response**:
```json
{
  "status": "healthy",
  "service": "bvn-service"
}
```

## 🧪 Testing

### Manual Testing
```bash
# Test BVN verification
curl -X POST http://localhost:8006/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"bvn": "12345678901"}'

# Test basic lookup
curl -X POST http://localhost:8006/api/v1/lookup \
  -H "Content-Type: application/json" \
  -d '{"bvn": "12345678901"}'

# Check status
curl http://localhost:8006/api/v1/status/12345678901

# Health check
curl http://localhost:8006/health
```

### Via API Gateway
```bash
# Get auth token first
TOKEN=$(curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}' \
  | jq -r '.access_token')

# Use token for BVN verification
curl -X POST http://localhost:8080/api/v1/bvn/verify \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"bvn": "12345678901"}'
```

### Python Testing
```python
import httpx

async def test_bvn_verification():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8006/api/v1/verify",
            json={"bvn": "12345678901"}
        )
        print(response.json())

# Run test
import asyncio
asyncio.run(test_bvn_verification())
```

## 🐳 Docker Deployment

### Build Image
```bash
# Build BVN service image
docker build -t sandbox-bvn:latest .

# Run container
docker run -d \
  --name bvn-service \
  -p 8006:8006 \
  -e DOJA_API_KEY=your-api-key \
  -e DOJA_APP_ID=your-app-id \
  sandbox-bvn:latest
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  bvn-service:
    build: .
    ports:
      - "8006:8006"
    environment:
      - DOJA_API_KEY=${DOJA_API_KEY}
      - DOJA_APP_ID=${DOJA_APP_ID}
      - DEBUG=false
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8006/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🏗️ Architecture

### Project Structure
```
bvn/
├── app/
│   ├── api/v1/
│   │   └── router.py          # API endpoints
│   ├── core/
│   │   └── config.py          # Configuration
│   ├── schemas/
│   │   └── bvn.py            # Pydantic models
│   ├── services/
│   │   └── verification.py    # Doja API integration
│   └── main.py               # FastAPI application
├── .env.example              # Environment template
├── Dockerfile               # Container configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Data Flow
1. **Request**: Client sends BVN to `/api/v1/verify`
2. **Validation**: Pydantic validates BVN format (11 digits)
3. **API Call**: Service calls Doja API with credentials
4. **Processing**: Response parsed and structured
5. **Response**: Formatted data returned to client

### Integration Points
- **Doja API**: External BVN verification service
- **API Gateway**: Routes requests with authentication
- **Auth Service**: Provides user context (if needed)

## 🔒 Security

### Input Validation
- BVN must be exactly 11 digits
- Only numeric characters allowed
- Request size limits enforced

### API Security
- Doja API key secured in environment variables
- HTTPS required for production
- Rate limiting via API Gateway
- Request/response logging

### Data Privacy
- BVN data not stored locally
- Verification results can be cached temporarily
- Sensitive data masked in logs

## 📊 Monitoring

### Health Monitoring
```bash
# Service health
curl http://localhost:8006/health

# Detailed status via API Gateway
curl http://localhost:8080/api/v1/services/bvn/health
```

### Logging
```bash
# View logs (Docker)
docker logs bvn-service

# View logs (local)
tail -f ../logs/bvn.log
```

### Metrics
- Request count and response times
- Success/failure rates
- Doja API response times
- Error categorization

## 🔧 Troubleshooting

### Common Issues

**Service Won't Start**:
```bash
# Check port availability
netstat -tulpn | grep :8006

# Verify environment variables
cat .env | grep DOJA

# Check dependencies
pip install -r requirements.txt
```

**Doja API Errors**:
```bash
# Test API credentials
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "AppId: YOUR_APP_ID" \
     https://api.dojah.io/api/v1/general/docs

# Check API limits
# Login to Doja dashboard to verify usage
```

**BVN Validation Fails**:
- Ensure BVN is exactly 11 digits
- Check for leading/trailing spaces
- Verify BVN exists in Nigerian banking system

**Connection Timeouts**:
- Check internet connectivity
- Verify Doja API status
- Increase timeout in configuration

### Error Codes
- `400`: Invalid BVN format
- `401`: Invalid Doja API credentials
- `500`: Doja API service error
- `503`: Service unavailable
- `504`: Request timeout

## 🚀 Development

### Adding Features
1. **New Endpoints**: Add to `app/api/v1/router.py`
2. **Validation**: Update schemas in `app/schemas/bvn.py`
3. **Business Logic**: Extend `app/services/verification.py`
4. **Configuration**: Add to `app/core/config.py`

### Testing
```bash
# Run tests
pytest tests/

# Code quality
black app/
flake8 app/
mypy app/
```

### Contributing
1. Fork repository
2. Create feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

## 📖 References

- [Doja API Documentation](https://docs.dojah.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Nigerian BVN System](https://www.nibss-plc.com.ng/bvn/)
- [API Gateway Integration](../../services/api-gateway/README.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

---

**Built for Nigerian fintech innovation** 🇳🇬