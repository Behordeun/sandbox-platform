# 📞 IVR Service - Interactive Voice Response for Nigeria

**Build intelligent voice systems for Nigerian customers.** Create automated phone systems, voice menus, and interactive voice applications supporting Nigerian languages and contexts.

## 🎯 What is IVR?

Interactive Voice Response (IVR) allows customers to interact with your system through voice and keypad inputs. Perfect for:

- **Customer Support**: Automated help systems
- **Banking Services**: Account balance, transaction history
- **Surveys & Feedback**: Voice-based data collection
- **Appointment Booking**: Automated scheduling systems

## ✨ Key Features

### 🇳🇬 **Nigerian Language Support**

- English (Nigerian accent)
- Hausa, Yoruba, Igbo support
- Local context awareness
- Cultural appropriate responses

### 📞 **Voice Capabilities**

- Text-to-speech in Nigerian languages
- Speech recognition
- DTMF (keypad) input handling
- Call routing and forwarding

### 🔧 **Easy Integration**

- RESTful API interface
- Webhook support for call events
- Real-time call monitoring
- Call recording and analytics

## 🚀 Quick Start (3 Minutes)

### Step 1: Setup Environment

```bash
# Navigate to IVR service directory
cd sandbox/ivr

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start Service

```bash
# Start the IVR service
uvicorn app.main:app --reload --port 8004
```

### Step 3: Test It Works

```bash
# Check service health
curl http://localhost:8004/health

# Expected response:
{
  "status": "healthy",
  "service": "IVR Service"
}
```

## 📚 API Reference

### Core Endpoints

| Method | Endpoint | Description | Use Case |
|--------|----------|-------------|----------|
| `POST` | `/api/v1/ivr/create-flow` | Create IVR flow | Build voice menus |
| `POST` | `/api/v1/ivr/handle-call` | Handle incoming call | Process customer calls |
| `GET` | `/api/v1/ivr/call-status/{id}` | Check call status | Monitor call progress |
| `POST` | `/api/v1/ivr/text-to-speech` | Convert text to speech | Generate voice prompts |
| `GET` | `/health` | Service health check | Monitoring |

## 💡 Real-World Examples

### Example 1: Create Banking IVR Flow

```bash
curl -X POST http://localhost:8080/api/v1/ivr/create-flow \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Banking IVR",
    "language": "english_ng",
    "flow": {
      "welcome": {
        "message": "Welcome to First Bank. Press 1 for account balance, 2 for transaction history, 3 for customer service",
        "options": {
          "1": "check_balance",
          "2": "transaction_history", 
          "3": "customer_service"
        }
      },
      "check_balance": {
        "message": "Please enter your account number followed by the hash key",
        "input_type": "account_number",
        "next": "balance_response"
      }
    }
  }'
```

### Example 2: Handle Incoming Call

```bash
curl -X POST http://localhost:8080/api/v1/ivr/handle-call \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "call_123456",
    "from": "+2348012345678",
    "to": "+2341234567890",
    "flow_id": "banking_ivr_001"
  }'
```

### Response Example

```json
{
  "call_id": "call_123456",
  "status": "in_progress",
  "current_step": "welcome",
  "response": {
    "action": "play_message",
    "message": "Welcome to First Bank. Press 1 for account balance...",
    "voice": "nigerian_female",
    "language": "english_ng"
  },
  "next_expected": "dtmf_input"
}
```

## 🔧 Configuration

### Environment Variables

```env
# Service Configuration
APP_NAME=IVR Service
APP_VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=8004

# Voice Provider Configuration
VOICE_PROVIDER=twilio                 # twilio, vonage, local
VOICE_API_KEY=your-voice-api-key     # Provider API key
DEFAULT_VOICE=nigerian_female        # Default voice
DEFAULT_LANGUAGE=english_ng          # Default language

# TTS Configuration
TTS_PROVIDER=google                  # google, amazon, azure
TTS_API_KEY=your-tts-api-key        # TTS provider key

# Auth Service URL
AUTH_SERVICE_URL=http://auth-service:8000
```

## 🤝 Integration Examples

### Python Integration

```python
import requests

def create_ivr_flow(flow_config: dict, token: str):
    response = requests.post(
        "http://localhost:8080/api/v1/ivr/create-flow",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=flow_config
    )
    return response.json()

# Usage
banking_flow = {
    "name": "Customer Service IVR",
    "language": "english_ng",
    "flow": {
        "welcome": {
            "message": "Thank you for calling. How can we help you today?",
            "options": {"1": "support", "2": "sales"}
        }
    }
}

result = create_ivr_flow(banking_flow, "your-jwt-token")
print(f"IVR Flow created: {result['flow_id']}")
```

---

**Ready to build voice experiences for Nigerian customers?** This IVR service provides the foundation for intelligent voice applications.

*Connecting Nigeria through voice* 📞🇳🇬
