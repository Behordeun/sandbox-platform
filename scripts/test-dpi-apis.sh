#!/bin/bash

echo "🇳🇬 DPI Sandbox API Testing Script"
echo "=================================="

API_BASE="http://localhost:8080"

# Test 1: Health Check
echo "1. Testing DPI Health Status..."
curl -s "$API_BASE/api/v1/dpi/health" | jq '.'

# Test 2: Get Examples
echo -e "\n2. Getting NIN Examples..."
curl -s "$API_BASE/api/v1/examples/nin" | jq '.data'

echo -e "\n3. Getting SMS Examples..."
curl -s "$API_BASE/api/v1/examples/sms" | jq '.data'

# Test 4: Register Test User (with email notification)
echo -e "\n4. Registering Test User (email notification will be sent)..."
TEST_USER='{
  "email": "adebayo.test@dpi.ng",
  "username": "adebayo_dev",
  "password": "TestPass123",
  "first_name": "Adebayo",
  "last_name": "Ogundimu",
  "phone_number": "+2348012345678"
}'

REGISTER_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "$TEST_USER")

echo "$REGISTER_RESPONSE" | jq '.'
echo "📧 Registration confirmation email sent to adebayo.test@dpi.ng"

# Test 5: Login
echo -e "\n5. Testing Login..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"identifier": "adebayo.test@dpi.ng", "password": "TestPass123"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
echo "Access Token: ${TOKEN:0:20}..."

# Test 6: Test NIN Verification (Mock)
if [ "$TOKEN" != "null" ]; then
  echo -e "\n6. Testing NIN Verification..."
  curl -s -X POST "$API_BASE/api/v1/nin/verify" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"nin": "12345678901"}' | jq '.'
fi

# Test 7: Password Reset (with email link)
echo -e "\n7. Testing Password Reset (email link will be sent)..."
curl -s -X POST "$API_BASE/api/v1/auth/password-reset/request" \
  -H "Content-Type: application/json" \
  -d '{"email": "adebayo.test@dpi.ng"}' | jq '.'
echo "📧 Password reset link sent to adebayo.test@dpi.ng"

echo -e "\n✅ DPI API Testing Complete!"
echo "📧 Check your email for registration confirmation and password reset links"