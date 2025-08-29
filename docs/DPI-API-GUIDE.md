# 🇳🇬 DPI Sandbox API Guide

## Quick Start for Nigerian Developers

### 1. Authentication
```bash
# Register
curl -X POST http://127.0.0.1:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "adebayo@fintech.ng",
    "username": "adebayo_dev", 
    "password": "SecurePass123",
    "first_name": "Adebayo",
    "last_name": "Ogundimu",
    "phone_number": "+2348012345678"
  }'

# Login
curl -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "adebayo@fintech.ng", "password": "SecurePass123"}'
```

### 2. NIN Verification
```bash
curl -X POST http://127.0.0.1:8080/api/v1/nin/verify \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nin": "12345678901"}'
```

### 3. BVN Verification  
```bash
curl -X POST http://127.0.0.1:8080/api/v1/bvn/verify \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"bvn": "12345678901"}'
```

### 4. SMS Messaging
```bash
curl -X POST http://127.0.0.1:8080/api/v1/sms/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+2348012345678",
    "message": "Your OTP is 123456. Valid for 5 minutes."
  }'
```

## Nigerian Data Formats

### Phone Numbers
- **Format**: `+234XXXXXXXXXX` or `0XXXXXXXXXX`
- **Valid**: `+2348012345678`, `08012345678`
- **Invalid**: `+2347012345678` (wrong prefix)

### NIN (National Identity Number)
- **Format**: 11 digits
- **Example**: `12345678901`

### BVN (Bank Verification Number)
- **Format**: 11 digits  
- **Example**: `12345678901`

## Common Use Cases

### Identity Verification Flow
1. User registers → Verify NIN/BVN
2. Send SMS OTP → Confirm identity
3. Grant access to services

### Financial Services
1. BVN verification for banking
2. SMS alerts for transactions
3. NIN for KYC compliance

### Government Services
1. NIN-based citizen authentication
2. SMS service notifications
3. Digital identity verification

## Error Handling

All APIs return standardized error responses:
```json
{
  "success": false,
  "message": "Email already registered",
  "error_code": "EMAIL_EXISTS",
  "details": {
    "suggestion": "Try logging in or use password reset",
    "login_url": "/api/v1/auth/login"
  }
}
```

## Testing Tools

### Health Check
```bash
curl http://127.0.0.1:8080/api/v1/dpi/health
```

### Generate Test Data
```bash
python mock-data.py
```

### Run API Tests
```bash
./test-dpi-apis.sh
```

### Check All Services
```bash
./check-services.sh
```