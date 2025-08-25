# 💬 Two-Way SMS Service - Interactive SMS Communication

**Enable bidirectional SMS conversations with Nigerian customers.** Perfect for customer support, surveys, interactive campaigns, and automated SMS workflows.

## 🎯 What is Two-Way SMS?

Two-Way SMS allows customers to send messages to your system and receive automated responses. Essential for:
- **Customer Support**: SMS-based help desk
- **Surveys & Polls**: Interactive data collection
- **Order Tracking**: Status updates via SMS
- **Appointment Management**: SMS booking and reminders
- **Interactive Campaigns**: Engaging marketing flows

## ✨ Key Features

### 💬 **Bidirectional Communication**
- Receive SMS from customers
- Send automated responses
- Conversation threading
- Context-aware replies

### 🤖 **Smart Automation**
- Keyword-based responses
- Workflow automation
- AI-powered replies
- Escalation to human agents

### 📊 **Analytics & Insights**
- Conversation analytics
- Response time tracking
- Customer satisfaction metrics
- Campaign performance data

## 🚀 Quick Start (3 Minutes)

### Step 1: Setup Environment
```bash
# Navigate to Two-Way SMS service directory
cd sandbox/two-way-sms

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start Service
```bash
# Start the service
uvicorn app.main:app --reload --port 8007
```

### Step 3: Test It Works
```bash
# Check service health
curl http://localhost:8007/health

# Expected response:
{
  "status": "healthy",
  "service": "Two-Way SMS Service"
}
```

## 📚 API Reference

### Core Endpoints

| Method | Endpoint | Description | Use Case |
|--------|----------|-------------|----------|
| `POST` | `/api/v1/two-way-sms/webhook` | Receive incoming SMS | Handle customer messages |
| `POST` | `/api/v1/two-way-sms/send-reply` | Send response | Reply to customers |
| `POST` | `/api/v1/two-way-sms/create-workflow` | Create SMS workflow | Automate responses |
| `GET` | `/api/v1/two-way-sms/conversations` | List conversations | View chat history |
| `GET` | `/health` | Service health check | Monitoring |

## 💡 Real-World Examples

### Example 1: Handle Incoming Customer SMS
```bash
# Webhook endpoint receives incoming SMS
curl -X POST http://localhost:8007/api/v1/two-way-sms/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+2348012345678",
    "to": "+2341234567890",
    "message": "BALANCE",
    "message_id": "msg_incoming_123",
    "timestamp": "2025-08-25T20:45:30Z"
  }'
```

### Response Example
```json
{
  "status": "processed",
  "conversation_id": "conv_789012",
  "auto_reply": {
    "message": "Your account balance is ₦25,450.00. Reply HELP for more options.",
    "sent": true,
    "message_id": "msg_reply_456"
  },
  "workflow_triggered": "banking_keywords"
}
```

### Example 2: Create Interactive Survey Workflow
```bash
curl -X POST http://localhost:8080/api/v1/two-way-sms/create-workflow \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Satisfaction Survey",
    "trigger_keyword": "SURVEY",
    "steps": [
      {
        "step": 1,
        "message": "Thank you for choosing our service! How would you rate your experience? Reply 1-5 (1=Poor, 5=Excellent)",
        "expected_input": "number",
        "validation": "range:1-5"
      },
      {
        "step": 2,
        "message": "What can we improve? Reply with your suggestions or SKIP to finish.",
        "expected_input": "text",
        "optional": true
      },
      {
        "step": 3,
        "message": "Thank you for your feedback! We appreciate your input.",
        "final_step": true
      }
    ]
  }'
```

### Example 3: Send Manual Reply
```bash
curl -X POST http://localhost:8080/api/v1/two-way-sms/send-reply \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_789012",
    "to": "+2348012345678",
    "message": "Hello! A customer service agent will assist you shortly. Your ticket number is #CS001234.",
    "agent_id": "agent_001"
  }'
```

### Response Example
```json
{
  "status": "sent",
  "message_id": "msg_reply_789",
  "conversation_id": "conv_789012",
  "to": "+2348012345678",
  "cost": 4.50,
  "timestamp": "2025-08-25T20:46:00Z"
}
```

## 🔧 Configuration

### Environment Variables
```env
# Service Configuration
APP_NAME=Two-Way SMS Service
APP_VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=8007

# SMS Provider Configuration
SMS_PROVIDER=termii                   # termii, twilio, infobip
SMS_API_KEY=your-sms-api-key         # Provider API key
SMS_WEBHOOK_URL=https://yourdomain.com/webhook  # Your webhook URL
SMS_SENDER_ID=YourBrand              # Your brand sender ID

# AI Configuration (for smart replies)
ENABLE_AI_REPLIES=true               # Enable AI-powered responses
AI_API_KEY=your-ai-api-key          # AI provider key
AI_MODEL=gpt-3.5-turbo              # AI model for responses

# Database Configuration
DATABASE_URL=postgresql://user:pass@host:5432/twoway_sms

# Auth Service URL
AUTH_SERVICE_URL=http://auth-service:8000
```

## 🛠️ Development & Testing

### Setting Up Webhooks
```bash
# Configure your SMS provider webhook URL
# Point to: https://yourdomain.com/api/v1/two-way-sms/webhook

# For local testing, use ngrok
ngrok http 8007
# Use the ngrok URL as your webhook endpoint
```

### Testing Workflows
```bash
# Test keyword response
curl -X POST http://localhost:8007/api/v1/two-way-sms/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+2348012345678",
    "message": "HELP",
    "test_mode": true
  }'
```

## 🤝 Integration Examples

### Python Integration
```python
import requests

def create_support_workflow(token: str):
    workflow = {
        "name": "Customer Support",
        "trigger_keywords": ["HELP", "SUPPORT", "ISSUE"],
        "steps": [
            {
                "step": 1,
                "message": "Hi! I'm here to help. What issue are you experiencing? Reply:\n1 - Account issues\n2 - Payment problems\n3 - Technical support\n4 - Speak to agent",
                "expected_input": "number",
                "validation": "range:1-4"
            }
        ]
    }
    
    response = requests.post(
        "http://localhost:8080/api/v1/two-way-sms/create-workflow",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=workflow
    )
    return response.json()

# Usage
result = create_support_workflow("your-jwt-token")
print(f"Support workflow created: {result['workflow_id']}")
```

### Webhook Handler Example
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_sms_webhook():
    data = request.json
    from_number = data['from']
    message = data['message'].upper()
    
    # Custom business logic
    if 'BALANCE' in message:
        # Integrate with your banking system
        balance = get_account_balance(from_number)
        reply = f"Your balance is ₦{balance:,.2f}"
    elif 'HELP' in message:
        reply = "Reply BALANCE for balance, HISTORY for transactions, AGENT for support"
    else:
        reply = "Thank you for your message. Reply HELP for options."
    
    # Send reply through Two-Way SMS service
    send_reply(from_number, reply)
    
    return jsonify({"status": "processed"})
```

---

**Ready to have conversations with your Nigerian customers?** This Two-Way SMS service enables rich, interactive communication through SMS.

*Connecting businesses and customers through SMS* 💬🇳🇬