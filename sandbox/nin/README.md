# 🇳🇬 NIN Verification Service - Nigerian Identity Verification Made Easy

**Verify Nigerian National Identity Numbers (NIN) instantly using the Dojah API.** This service provides real-time NIN verification for Nigerian fintech, banking, and digital services.

## 🎯 What is NIN Verification?

The National Identity Number (NIN) is Nigeria's unique 11-digit identifier for citizens and legal residents. This service helps you:

- **Verify identity** of your users instantly
- **Prevent fraud** by validating real identities
- **Comply with KYC** requirements for financial services
- **Access official data** from NIMC through Dojah API

## ✨ Key Features

### 🔍 **Real-time Verification**

- Instant NIN validation through Dojah API
- Official NIMC data integration
- Comprehensive identity information

### 🛡️ **Security & Privacy**

- Encrypted data transmission
- Secure API key management
- Privacy-compliant data handling

### 📊 **Usage Tracking**

- Verification attempt logging
- Success/failure analytics
- Cost tracking per verification

## 🚀 Quick Start (3 Minutes)

### Step 1: Setup Environment

```bash
# Navigate to NIN service directory
cd sandbox/nin

# Copy environment template
cp .env.example .env

# Edit .env with your Dojah API credentials
nano .env
```

### Step 2: Configure Dojah API

```env
# Get these from https://dojah.io
DOJAH_API_KEY=your-dojah-api-key
DOJAH_APP_ID=your-dojah-app-id
DOJAH_BASE_URL=https://api.dojah.io
```

### Step 3: Install & Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the service
uvicorn app.main:app --reload --port 8005
```

### Step 4: Test It Works

```bash
# Check service health
curl http://localhost:8005/health

# Expected response:
{
  "status": "healthy",
  "service": "NIN Verification Service"
}
```

## 📚 API Reference

### 🔑 Authentication Required

All endpoints require authentication via the API Gateway or direct JWT token.

### Core Endpoints

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| `POST` | `/api/v1/nin/verify` | Verify NIN with full details | Verify `12345678901` |
| `POST` | `/api/v1/nin/lookup` | Basic NIN lookup | Quick validation |
| `GET` | `/api/v1/nin/status/{nin}` | Check verification status | Status of previous verification |
| `GET` | `/health` | Service health check | No auth required |

## 💡 Real-World Examples

### Example 1: Verify a Customer's NIN

```bash
# Through API Gateway (Recommended)
curl -X POST http://localhost:8080/api/v1/nin/verify \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nin": "12345678901"
  }'

# Direct to service (for testing)
curl -X POST http://localhost:8005/api/v1/nin/verify \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nin": "12345678901"
  }'
```

### Response Example

```json
{
  "status": "verified",
  "nin": "12345678901",
  "data": {
    "first_name": "Adebayo",
    "last_name": "Ogundimu",
    "middle_name": "Tunde",
    "date_of_birth": "1990-05-15",
    "gender": "Male",
    "phone": "+2348012345678",
    "email": "adebayo@example.com",
    "address": "123 Lagos Street, Victoria Island, Lagos",
    "state_of_origin": "Lagos",
    "lga_of_origin": "Lagos Island"
  },
  "verification_id": "ver_nin_123456789",
  "timestamp": "2025-08-25T20:45:30Z",
  "cost": 50.00
}
```

### Example 2: Quick NIN Validation

```bash
curl -X POST http://localhost:8005/api/v1/nin/lookup \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nin": "12345678901"
  }'

# Response:
{
  "status": "valid",
  "nin": "12345678901",
  "exists": true,
  "basic_info": {
    "first_name": "Adebayo",
    "last_name": "Ogundimu"
  }
}
```

### Example 3: Check Verification Status

```bash
curl -X GET http://localhost:8005/api/v1/nin/status/12345678901 \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "nin": "12345678901",
  "last_verified": "2025-08-25T20:45:30Z",
  "verification_count": 3,
  "status": "verified"
}
```

## 🔧 Configuration

### YAML-Based Configuration

This service uses the centralized YAML configuration system. Configuration is automatically loaded from:

- `config.yaml` - Base configuration
- `config/environments/{ENVIRONMENT}.yaml` - Environment-specific overrides
- `.env` - Secrets and API keys only

### Centralized Environment Variables

All services use the **single root .env file**. No service-specific .env files needed:

```env
# All variables are in the root .env file
ENVIRONMENT=development
DATABASE_URL=postgresql://sandbox_user:password@localhost:5432/sandbox_platform
DOJAH_API_KEY=your-dojah-api-key        # Get from Dojah dashboard
DOJAH_APP_ID=your-dojah-app-id          # Your application ID
SMS_API_KEY=your-sms-api-key
AI_API_KEY=your-ai-api-key
# ... all other variables in organized sections
```

### Configuration Structure

Service configuration is defined in `config.yaml`:

```yaml
sandbox:
  nin_service:
    host: "0.0.0.0"
    port: 8005
    debug: false
    cache_ttl: 3600
    doja_integration: true

providers:
  dojah:
    base_url: "https://api.dojah.io"
    api_key: "${DOJAH_API_KEY}"
    app_id: "${DOJAH_APP_ID}"
    timeout: 30
```

### Getting Dojah API Credentials

1. Visit [https://dojah.io](https://dojah.io)
2. Create an account
3. Navigate to API section
4. Generate API key and App ID
5. Add credentials to the **single root .env file** (no service-specific .env files)

## 📊 Understanding NIN Format

### Valid NIN Format

- **Length**: Exactly 11 digits
- **Format**: `12345678901`
- **No spaces or special characters**

### NIN Validation Rules

```python
# Valid NINs
"12345678901"  ✅
"98765432109"  ✅

# Invalid NINs
"1234567890"   ❌ (10 digits)
"123456789012" ❌ (12 digits)
"1234-567-890" ❌ (contains dashes)
"abcdefghijk"  ❌ (contains letters)
```

## 🛠️ Development & Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest tests/ -v

# Test specific functionality
pytest tests/test_nin_verification.py -v
```

### Mock Data for Testing

```bash
# Use test NINs (these won't charge your Dojah account)
curl -X POST http://localhost:8005/api/v1/nin/verify \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nin": "12345678901",
    "test_mode": true
  }'
```

### Error Handling

```json
// Invalid NIN format
{
  "error": "Invalid NIN format",
  "message": "NIN must be exactly 11 digits",
  "status_code": 400
}

// NIN not found
{
  "error": "NIN not found",
  "message": "No record found for this NIN",
  "status_code": 404
}

// Dojah API error
{
  "error": "Verification failed",
  "message": "Unable to verify NIN at this time",
  "status_code": 503
}
```

## 💰 Cost & Usage

### Dojah API Pricing

- **Per verification**: ₦50 - ₦100 (varies by plan)
- **Monthly plans**: Available for high volume
- **Test mode**: Free for development

### Monitoring Usage

```bash
# Check your verification history
python ../../analyze-logs.py --user-activity | grep nin

# Monitor costs
grep "cost" ../logs/nin.log
```

## 🚀 Production Deployment

### Docker Deployment

```bash
# Build image
docker build -t nin-service:1.0.0 .

# Run container
docker run -p 8005:8005 \
  -e DOJAH_API_KEY="your-api-key" \
  -e DOJAH_APP_ID="your-app-id" \
  nin-service:1.0.0
```

### Environment-Specific Configuration

```bash
# Development
DEBUG=true
DOJAH_BASE_URL=https://sandbox.dojah.io  # Use sandbox for testing

# Production
DEBUG=false
DOJAH_BASE_URL=https://api.dojah.io      # Use live API
```

## 🔍 Troubleshooting

### Common Issues

#### 1. **"Invalid API Key" Error**

```bash
# Check your Dojah credentials
curl -X GET https://api.dojah.io/api/v1/general/account \
  -H "Authorization: $DOJAH_API_KEY" \
  -H "AppId: $DOJAH_APP_ID"
```

#### 2. **Service Unavailable (503)**

```bash
# Check if Dojah API is accessible
curl -I https://api.dojah.io

# Check service logs
tail -f ../logs/nin.log
```

#### 3. **Rate Limiting**

```bash
# Dojah has rate limits - check your plan
# Implement exponential backoff in your application
```

## 🤝 Integration Examples

### Python Integration

```python
import requests

def verify_nin(nin: str, token: str):
    response = requests.post(
        "http://localhost:8080/api/v1/nin/verify",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={"nin": nin}
    )
    return response.json()

# Usage
result = verify_nin("12345678901", "your-jwt-token")
print(f"Verified: {result['data']['first_name']} {result['data']['last_name']}")
```

### JavaScript Integration

```javascript
async function verifyNIN(nin, token) {
    const response = await fetch('http://localhost:8080/api/v1/nin/verify', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nin })
    });
    
    return await response.json();
}

// Usage
const result = await verifyNIN('12345678901', 'your-jwt-token');
console.log(`Verified: ${result.data.first_name} ${result.data.last_name}`);
```

## 📞 Support & Resources

### Getting Help

- **Dojah API Docs**: [https://docs.dojah.io](https://docs.dojah.io)
- **Service Logs**: `tail -f ../logs/nin.log`
- **Health Check**: `curl http://localhost:8005/health`

### Best Practices

1. **Always validate NIN format** before API calls
2. **Handle errors gracefully** - API calls can fail
3. **Cache results** to avoid duplicate charges
4. **Use test mode** during development
5. **Monitor your usage** to control costs

---

**Ready to verify Nigerian identities?** This NIN service integrates seamlessly with your application to provide instant, reliable identity verification for your Nigerian users.

*Built for Nigerian developers, by Nigerian developers* 🇳🇬
