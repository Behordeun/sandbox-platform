# 🤖 AI Service - Nigerian-Focused AI Content Generation

**Generate content, analyze data, and build intelligent applications with AI tailored for Nigerian contexts.** Perfect for content creation, data analysis, chatbots, and business intelligence.

## 🎯 What is the AI Service?

This service provides AI-powered capabilities specifically optimized for Nigerian businesses and contexts:

- **Content Generation**: Blog posts, marketing copy, business plans
- **Data Analysis**: Extract insights from Nigerian market data
- **Language Processing**: Support for Nigerian English and local contexts
- **Business Intelligence**: Market analysis and trend prediction

## ✨ Key Features

### 🇳🇬 **Nigerian Context Awareness**

- Understanding of Nigerian business environment
- Local market knowledge and trends
- Cultural context in content generation
- Nigerian English language patterns

### 🚀 **Multiple AI Capabilities**

- Text generation and completion
- Data analysis and insights
- Sentiment analysis
- Content summarization
- Question answering

### 💡 **Business-Ready Applications**

- Marketing content creation
- Business plan generation
- Customer service automation
- Market research analysis

## 🚀 Quick Start (3 Minutes)

### Step 1: Setup Environment

```bash
# Navigate to AI service directory
cd sandbox/ai

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start Service

```bash
# Start the AI service
uvicorn app.main:app --reload --port 8002
```

### Step 3: Test It Works

```bash
# Check service health
curl http://localhost:8002/health

# Expected response:
{
  "status": "healthy",
  "service": "AI Service"
}
```

## 📚 API Reference

### Core Endpoints

| Method | Endpoint | Description | Use Case |
|--------|----------|-------------|----------|
| `POST` | `/api/v1/ai/generate` | Generate text content | Blog posts, marketing copy |
| `POST` | `/api/v1/ai/analyze` | Analyze data/text | Market insights, sentiment |
| `POST` | `/api/v1/ai/summarize` | Summarize long content | Document summaries |
| `POST` | `/api/v1/ai/chat` | Conversational AI | Chatbots, Q&A |
| `GET` | `/health` | Service health check | Monitoring |

## 💡 Real-World Examples

### Example 1: Generate Nigerian Business Plan

```bash
curl -X POST http://localhost:8080/api/v1/ai/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a business plan for a Nigerian fintech startup focusing on mobile payments",
    "type": "business_plan",
    "max_tokens": 1000,
    "context": "nigerian_market"
  }'
```

### Response Example

```json
{
  "generated_text": "# Nigerian Fintech Business Plan\n\n## Executive Summary\nOur fintech startup, PayNaija, aims to revolutionize mobile payments across Nigeria by providing seamless, secure, and affordable digital payment solutions...",
  "tokens_used": 987,
  "generation_id": "gen_ai_123456",
  "context_applied": "nigerian_market",
  "timestamp": "2025-08-25T20:45:30Z"
}
```

### Example 2: Analyze Nigerian Market Data

```bash
curl -X POST http://localhost:8080/api/v1/ai/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": "Lagos fintech adoption rate increased 45% in 2024. Mobile banking users grew from 2.1M to 3.8M. Digital payments volume reached ₦12.5 trillion.",
    "analysis_type": "market_trends",
    "focus": "nigerian_fintech"
  }'
```

### Response Example

```json
{
  "analysis": {
    "key_insights": [
      "Strong fintech growth trajectory in Lagos market",
      "81% increase in mobile banking adoption",
      "Significant digital payment volume growth"
    ],
    "trends": [
      "Accelerating digital transformation",
      "Increasing consumer trust in mobile banking",
      "Growing payment digitization"
    ],
    "recommendations": [
      "Focus on Lagos market expansion",
      "Invest in mobile-first solutions",
      "Target underbanked populations"
    ]
  },
  "confidence_score": 0.92,
  "analysis_id": "ana_ai_789012"
}
```

### Example 3: Generate Marketing Content

```bash
curl -X POST http://localhost:8080/api/v1/ai/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a social media post for a Nigerian e-commerce platform launching same-day delivery in Lagos",
    "type": "social_media",
    "tone": "exciting",
    "platform": "instagram"
  }'
```

### Response Example

```json
{
  "generated_text": "🚀 BREAKING: Same-day delivery is now LIVE in Lagos! 📦✨\n\nOrder before 2PM and get your items delivered the same day! From Victoria Island to Ikeja, we've got you covered. 🏃‍♂️💨\n\n#LagosDelivery #SameDayDelivery #NigerianEcommerce #FastDelivery",
  "tokens_used": 45,
  "generation_id": "gen_ai_345678",
  "optimized_for": "instagram"
}
```

## 🔧 Configuration

### Environment Variables

```env
# Service Configuration
APP_NAME=AI Service
APP_VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=8002

# AI Provider Configuration
AI_PROVIDER=openai                    # openai, anthropic, local
AI_API_KEY=your-ai-api-key           # Provider API key
AI_MODEL=gpt-3.5-turbo               # Model to use
AI_MAX_TOKENS=2000                   # Default max tokens

# Nigerian Context
ENABLE_NIGERIAN_CONTEXT=true         # Enable Nigerian-specific optimizations
DEFAULT_CURRENCY=NGN                 # Default currency for financial content
DEFAULT_LOCATION=Nigeria             # Default location context

# Auth Service URL
AUTH_SERVICE_URL=http://auth-service:8000
```

## 🛠️ Development & Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest tests/ -v
```

### Mock Mode for Testing

```bash
# Enable test mode (uses mock responses)
curl -X POST http://localhost:8002/api/v1/ai/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Test prompt",
    "test_mode": true
  }'
```

## 🤝 Integration Examples

### Python Integration

```python
import requests

def generate_content(prompt: str, content_type: str, token: str):
    response = requests.post(
        "http://localhost:8080/api/v1/ai/generate",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "prompt": prompt,
            "type": content_type,
            "context": "nigerian_market"
        }
    )
    return response.json()

# Usage
result = generate_content(
    "Create a marketing email for Nigerian customers",
    "marketing_email",
    "your-jwt-token"
)
print(result['generated_text'])
```

---

**Ready to build intelligent Nigerian applications?** This AI service provides the foundation for smart, context-aware applications.

*Built for Nigerian innovation* 🤖🇳🇬
