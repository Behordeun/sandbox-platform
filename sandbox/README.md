# 🏗️ DPI Sandbox Services

**Nigerian Digital Public Infrastructure services for startup integration.**

## 📋 Available Services

### **🆔 NIN Service** (Port 8005)
- Nigerian National Identity Number verification
- Real-time validation via Dojah API
- Status tracking and lookup capabilities

### **🏦 BVN Service** (Port 8006)
- Bank Verification Number validation
- Financial identity verification
- Secure data handling and privacy protection

### **📱 SMS Service** (Port 8003)
- Nigerian mobile network SMS delivery
- Support for all major networks (MTN, Airtel, Glo, 9mobile)
- OTP and notification messaging

### **🤖 AI Service** (Port 8002)
- Nigerian-context content generation
- Localized AI responses and recommendations
- Financial and business content optimization

## 🚀 Quick Start

```bash
# Start all sandbox services
cd sandbox/nin && uvicorn app.main:app --reload --port 8005
cd sandbox/bvn && uvicorn app.main:app --reload --port 8006
cd sandbox/sms && uvicorn app.main:app --reload --port 8003
cd sandbox/ai && uvicorn app.main:app --reload --port 8002
```

## 🔗 Access via API Gateway

All services are accessible through the API Gateway at `http://localhost:8080`:

```bash
# NIN verification
POST /api/v1/nin/verify

# BVN verification  
POST /api/v1/bvn/verify

# SMS sending
POST /api/v1/sms/send

# AI content generation
POST /api/v1/ai/generate
```

---

**Nigerian DPI services for startup innovation** 🇳🇬