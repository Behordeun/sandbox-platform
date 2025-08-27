# 🚀 Startup Access Guide - DPI Sandbox Platform

**Quick guide for Nigerian startups to access and use the DPI Sandbox Platform.**

## 🎯 Overview

The DPI Sandbox Platform is a **closed-house sandbox** designed for **9 selected Nigerian startups** to test and integrate with Digital Public Infrastructure services including NIN verification, BVN verification, SMS services, and AI capabilities.

## 🔐 Getting Access

### **Step 1: Request Account**
- **Contact**: admin@dpi-sandbox.ng
- **Include**: Company name, developer details, use case
- **Wait**: Admin will create your account and send credentials

### **Step 2: Receive Credentials**
You'll receive an email with:
- **Username/Email**: Your login identifier
- **Temporary Password**: Change after first login
- **API Documentation**: Links to get started

### **Step 3: First Login**
```bash
# Login to get access token
curl -X POST http://localhost:8000/api/v1/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "your-email@startup.ng",
    "password": "your-temporary-password"
  }'

# Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## 🛠️ Available Services

### **🆔 NIN Verification**
```bash
# Verify Nigerian National Identity Number
curl -X POST http://localhost:8080/api/v1/nin/verify \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nin": "12345678901"}'
```

### **🏦 BVN Verification**
```bash
# Verify Bank Verification Number
curl -X POST http://localhost:8080/api/v1/bvn/verify \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"bvn": "12345678901"}'
```

### **📱 SMS Services**
```bash
# Send SMS to Nigerian numbers
curl -X POST http://localhost:8080/api/v1/sms/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+2348012345678",
    "message": "Your OTP is 123456"
  }'
```

### **🤖 AI Services**
```bash
# Generate Nigerian-context content
curl -X POST http://localhost:8080/api/v1/ai/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Generate a welcome message for Nigerian fintech users",
    "context": "nigerian_fintech"
  }'
```

## 📚 API Documentation

### **Interactive Documentation**
- **API Gateway**: http://localhost:8080/docs
- **Auth Service**: http://localhost:8000/docs

### **Key Endpoints**
```bash
# Authentication
POST /api/v1/auth/login/json    # Login with JSON
POST /api/v1/auth/logout        # Logout
GET  /api/v1/auth/me           # Get user info

# Identity Services
POST /api/v1/nin/verify        # NIN verification
POST /api/v1/bvn/verify        # BVN verification

# Communication
POST /api/v1/sms/send          # Send SMS
POST /api/v1/ai/generate       # AI content generation
```

## 🔄 Development Workflow

### **1. Authentication**
```javascript
// Login and store token
const response = await fetch('http://localhost:8000/api/v1/auth/login/json', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    identifier: 'your-email@startup.ng',
    password: 'your-password'
  })
});

const { access_token } = await response.json();
localStorage.setItem('token', access_token);
```

### **2. API Calls**
```javascript
// Use token for API calls
const apiCall = async (endpoint, data) => {
  const token = localStorage.getItem('token');
  
  const response = await fetch(`http://localhost:8080${endpoint}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  
  return await response.json();
};

// Verify NIN
const ninResult = await apiCall('/api/v1/nin/verify', {
  nin: '12345678901'
});
```

### **3. Logout**
```javascript
// Logout and clear token
await fetch('http://localhost:8000/api/v1/auth/logout', {
  method: 'POST'
});
localStorage.removeItem('token');
```

## 🧪 Testing & Examples

### **Test Data**
```bash
# Get test examples
curl http://localhost:8080/api/v1/examples/nin
curl http://localhost:8080/api/v1/examples/sms
curl http://localhost:8080/api/v1/examples/bvn
```

### **Mock Nigerian Data**
- **Test NINs**: Use sandbox NIN numbers for testing
- **Test Phone Numbers**: +234801234567X format
- **Test BVNs**: Use sandbox BVN numbers

## 🚨 Important Notes

### **Security**
- **Never share credentials** with other startups
- **Use HTTPS** in production
- **Store tokens securely** (not in localStorage for production)
- **Logout when done** to invalidate tokens

### **Rate Limits**
- **100 requests per minute** per startup
- **Contact admin** if you need higher limits
- **Monitor usage** to avoid hitting limits

### **Support**
- **Technical Issues**: admin@dpi-sandbox.ng
- **API Questions**: Check documentation first
- **Account Issues**: Contact admin directly

## 📊 Monitoring

### **Check Your Usage**
```bash
# Get your user info
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/auth/me
```

### **Service Health**
```bash
# Check if services are running
curl http://localhost:8080/health
curl http://localhost:8000/health
```

## 🎉 Success Checklist

- [ ] Received account credentials from admin
- [ ] Successfully logged in and got access token
- [ ] Tested NIN verification with sample data
- [ ] Tested BVN verification with sample data
- [ ] Sent test SMS to Nigerian number
- [ ] Generated AI content with Nigerian context
- [ ] Implemented proper logout in your application
- [ ] Ready to integrate with your startup's application

---

**Ready to build with Nigerian DPI?** You now have access to the most comprehensive sandbox for Nigerian Digital Public Infrastructure services.

*Built for Nigerian startups, by Nigerian developers* 🇳🇬