# 📱 SMS Service - Nigerian SMS Messaging Made Simple

**Send SMS messages to Nigerian phone numbers instantly.** Perfect for OTP verification, notifications, marketing campaigns, and customer communication across all Nigerian networks.

## 🎯 What is the SMS Service?

This service enables you to send SMS messages to Nigerian mobile numbers across all networks (MTN, Airtel, Glo, 9mobile). Essential for:
- **OTP Verification**: Secure user authentication
- **Notifications**: Order updates, payment confirmations
- **Marketing**: Promotional campaigns and announcements
- **Alerts**: System notifications and reminders

## ✨ Key Features

### 📲 **Multi-Network Support**
- MTN, Airtel, Glo, 9mobile coverage
- Automatic network detection
- Optimized routing for best delivery

### 🚀 **High Delivery Rates**
- Direct operator connections
- Real-time delivery reports
- Retry mechanisms for failed messages

### 💰 **Cost-Effective**
- Competitive Nigerian SMS rates
- Bulk messaging discounts
- Pay-per-message or monthly plans

### 🔒 **Secure & Reliable**
- Encrypted message transmission
- Delivery confirmation
- Message queuing for high volume

## 🚀 Quick Start (3 Minutes)

### Step 1: Setup Environment
```bash
# Navigate to SMS service directory
cd sandbox/sms

# Copy environment template
cp .env.example .env

# Edit .env with your SMS provider credentials
nano .env
```

### Step 2: Configure SMS Provider
```env
# SMS Provider Configuration (choose one)
SMS_PROVIDER=termii  # or twilio, infobip, etc.
SMS_API_KEY=your-sms-api-key
SMS_SENDER_ID=YourBrand  # Your brand name (max 11 chars)
```

### Step 3: Install & Start
```bash
# Install dependencies
pip install -r requirements.txt

# Start the service
uvicorn app.main:app --reload --port 8003
```

### Step 4: Test It Works
```bash
# Check service health
curl http://localhost:8003/health

# Expected response:
{
  "status": "healthy",
  "service": "SMS Service"
}
```

## 📚 API Reference

### 🔑 Authentication Required
All endpoints require authentication via the API Gateway or direct JWT token.

### Core Endpoints

| Method | Endpoint | Description | Use Case |
|--------|----------|-------------|----------|
| `POST` | `/api/v1/sms/send` | Send single SMS | OTP, notifications |
| `POST` | `/api/v1/sms/send-bulk` | Send bulk SMS | Marketing campaigns |
| `GET` | `/api/v1/sms/status/{message_id}` | Check delivery status | Delivery confirmation |
| `GET` | `/api/v1/sms/balance` | Check SMS balance | Account monitoring |
| `GET` | `/health` | Service health check | System monitoring |

## 💡 Real-World Examples

### Example 1: Send OTP for User Verification
```bash
# Through API Gateway (Recommended)
curl -X POST http://localhost:8080/api/v1/sms/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+2348012345678",
    "message": "Your OTP is 123456. Valid for 5 minutes. Do not share with anyone.",
    "type": "otp"
  }'

# Direct to service (for testing)
curl -X POST http://localhost:8003/api/v1/sms/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+2348012345678",
    "message": "Your OTP is 123456. Valid for 5 minutes.",
    "type": "otp"
  }'
```

### Response Example
```json
{
  "status": "sent",
  "message_id": "msg_sms_789012345",
  "to": "+2348012345678",
  "message": "Your OTP is 123456. Valid for 5 minutes.",
  "network": "MTN",
  "cost": 4.50,
  "units_used": 1,
  "timestamp": "2025-08-25T20:45:30Z",
  "estimated_delivery": "2025-08-25T20:45:35Z"
}
```

### Example 2: Send Payment Confirmation
```bash
curl -X POST http://localhost:8080/api/v1/sms/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+2348012345678",
    "message": "Payment of ₦5,000 received successfully. Transaction ID: TXN123456. Thank you for your business!",
    "type": "notification"
  }'

# Response:
{
  "status": "sent",
  "message_id": "msg_sms_789012346",
  "to": "+2348012345678",
  "network": "Airtel",
  "cost": 4.50,
  "units_used": 1
}
```

### Example 3: Send Bulk Marketing SMS
```bash
curl -X POST http://localhost:8080/api/v1/sms/send-bulk \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": [
      "+2348012345678",
      "+2348087654321",
      "+2348098765432"
    ],
    "message": "🎉 Special offer! Get 20% off your next purchase. Use code SAVE20. Valid until midnight. Shop now!",
    "type": "marketing",
    "sender_id": "YourBrand"
  }'

# Response:
{
  "status": "queued",
  "batch_id": "batch_sms_456789",
  "total_recipients": 3,
  "estimated_cost": 13.50,
  "estimated_delivery": "2025-08-25T20:50:00Z",
  "messages": [
    {
      "message_id": "msg_sms_789012347",
      "to": "+2348012345678",
      "status": "queued"
    },
    {
      "message_id": "msg_sms_789012348", 
      "to": "+2348087654321",
      "status": "queued"
    },
    {
      "message_id": "msg_sms_789012349",
      "to": "+2348098765432",
      "status": "queued"
    }
  ]
}
```

### Example 4: Check Message Delivery Status
```bash
curl -X GET http://localhost:8080/api/v1/sms/status/msg_sms_789012345 \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "message_id": "msg_sms_789012345",
  "status": "delivered",
  "to": "+2348012345678",
  "network": "MTN",
  "sent_at": "2025-08-25T20:45:30Z",
  "delivered_at": "2025-08-25T20:45:33Z",
  "cost": 4.50
}
```

## 🔧 Configuration

### Environment Variables
```env
# Service Configuration
APP_NAME=SMS Service
APP_VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=8003

# SMS Provider Configuration
SMS_PROVIDER=termii                    # termii, twilio, infobip
SMS_API_KEY=your-sms-api-key          # Provider API key
SMS_SENDER_ID=YourBrand               # Default sender ID (max 11 chars)
SMS_BASE_URL=https://api.ng.termii.com # Provider API URL

# Rate Limiting
SMS_RATE_LIMIT=100                    # Messages per minute
SMS_DAILY_LIMIT=10000                 # Messages per day

# Auth Service URL
AUTH_SERVICE_URL=http://auth-service:8000
```

### SMS Provider Setup

#### Option 1: Termii (Recommended for Nigeria)
1. Visit [https://termii.com](https://termii.com)
2. Create account and complete verification
3. Get API key from dashboard
4. Add credits to your account
5. Configure sender ID

#### Option 2: Twilio
1. Visit [https://twilio.com](https://twilio.com)
2. Create account and get Account SID & Auth Token
3. Purchase Nigerian phone number
4. Configure webhook URLs

## 📱 Nigerian Phone Number Format

### Supported Formats
```python
# International format (Recommended)
"+2348012345678"  ✅
"+2348087654321"  ✅

# Local format (Auto-converted)
"08012345678"     ✅ → "+2348012345678"
"07087654321"     ✅ → "+2347087654321"

# Invalid formats
"8012345678"      ❌ (missing leading zero)
"2348012345678"   ❌ (missing plus sign)
"+234801234567"   ❌ (too short)
```

### Network Detection
```json
{
  "+2348012345678": "MTN",
  "+2348087654321": "Airtel", 
  "+2348098765432": "Glo",
  "+2349012345678": "9mobile"
}
```

## 💰 SMS Pricing & Costs

### Typical Nigerian SMS Rates
- **Local SMS**: ₦3.50 - ₦5.00 per message
- **Bulk SMS**: ₦2.50 - ₦4.00 per message (volume discounts)
- **OTP SMS**: ₦4.00 - ₦6.00 per message (higher priority)

### Cost Optimization Tips
1. **Use bulk endpoints** for multiple recipients
2. **Optimize message length** (160 chars = 1 unit)
3. **Choose appropriate message type** (marketing vs transactional)
4. **Monitor delivery rates** by network
5. **Use sender ID** for brand recognition

## 🛠️ Development & Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest tests/ -v

# Test SMS sending specifically
pytest tests/test_sms_sending.py -v
```

### Mock Mode for Testing
```bash
# Enable test mode (won't send real SMS)
curl -X POST http://localhost:8003/api/v1/sms/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+2348012345678",
    "message": "Test message",
    "test_mode": true
  }'
```

### Error Handling
```json
// Invalid phone number
{
  "error": "Invalid phone number",
  "message": "Phone number must be in +234XXXXXXXXXX format",
  "status_code": 400
}

// Message too long
{
  "error": "Message too long",
  "message": "Message exceeds 1600 characters limit",
  "status_code": 400
}

// Insufficient balance
{
  "error": "Insufficient balance",
  "message": "Not enough SMS credits to send message",
  "status_code": 402
}

// Network error
{
  "error": "Delivery failed",
  "message": "Unable to deliver message to recipient",
  "status_code": 503
}
```

## 🚀 Production Deployment

### Docker Deployment
```bash
# Build image
docker build -t sms-service:1.0.0 .

# Run container
docker run -p 8003:8003 \
  -e SMS_API_KEY="your-api-key" \
  -e SMS_SENDER_ID="YourBrand" \
  sms-service:1.0.0
```

### Environment-Specific Configuration
```bash
# Development
DEBUG=true
SMS_RATE_LIMIT=10        # Lower limits for testing

# Production  
DEBUG=false
SMS_RATE_LIMIT=1000      # Higher limits for production
SMS_DAILY_LIMIT=100000   # Production daily limits
```

## 🔍 Troubleshooting

### Common Issues

#### 1. **Messages Not Delivering**
```bash
# Check SMS provider balance
curl -X GET http://localhost:8003/api/v1/sms/balance \
  -H "Authorization: Bearer $TOKEN"

# Check message status
curl -X GET http://localhost:8003/api/v1/sms/status/msg_id \
  -H "Authorization: Bearer $TOKEN"
```

#### 2. **Invalid Sender ID**
```bash
# Sender ID rules:
# - Max 11 characters
# - Alphanumeric only
# - No spaces or special characters
# - Must be registered with provider
```

#### 3. **High Costs**
```bash
# Monitor message length (160 chars = 1 unit)
# Use bulk endpoints for multiple recipients
# Choose appropriate message priority
```

## 🤝 Integration Examples

### Python Integration
```python
import requests

def send_otp(phone: str, otp: str, token: str):
    response = requests.post(
        "http://localhost:8080/api/v1/sms/send",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "to": phone,
            "message": f"Your OTP is {otp}. Valid for 5 minutes. Do not share.",
            "type": "otp"
        }
    )
    return response.json()

# Usage
result = send_otp("+2348012345678", "123456", "your-jwt-token")
if result['status'] == 'sent':
    print(f"OTP sent to {result['to']}, Message ID: {result['message_id']}")
```

### JavaScript Integration
```javascript
async function sendSMS(to, message, token, type = 'notification') {
    try {
        const response = await fetch('http://localhost:8080/api/v1/sms/send', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ to, message, type })
        });
        
        const result = await response.json();
        return { success: true, data: result };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Usage
const result = await sendSMS(
    '+2348012345678', 
    'Your order has been confirmed!', 
    'your-jwt-token'
);

if (result.success) {
    console.log(`SMS sent: ${result.data.message_id}`);
}
```

## 📞 Support & Resources

### Getting Help
- **Provider Docs**: Check your SMS provider documentation
- **Service Logs**: `tail -f ../logs/sms.log`
- **Health Check**: `curl http://localhost:8003/health`
- **Balance Check**: Use `/api/v1/sms/balance` endpoint

### Best Practices
1. **Validate phone numbers** before sending
2. **Use appropriate message types** (OTP, notification, marketing)
3. **Monitor delivery rates** and costs
4. **Implement retry logic** for failed messages
5. **Respect opt-out requests** for marketing messages
6. **Keep messages concise** to minimize costs
7. **Use test mode** during development

### Compliance & Regulations
- **NCC Guidelines**: Follow Nigerian Communications Commission rules
- **Opt-out Mechanisms**: Include unsubscribe options for marketing
- **Data Protection**: Follow NDPR for customer phone numbers
- **Sender ID Registration**: Register your brand with providers

---

**Ready to connect with your Nigerian customers?** This SMS service provides reliable, cost-effective messaging across all Nigerian networks.

*Trusted by Nigerian businesses for customer communication* 📱🇳🇬