# Payment Initiation Failure - Diagnostic Guide

## Problem
Payment initiation fails with "Authentication failed" or returns error from M-Pesa API.

## Root Cause
The M-Pesa service requires Safaricom Daraja API credentials that are currently **not configured**.

### Missing Configuration:
- `MPESA_CONSUMER_KEY` - Empty ❌
- `MPESA_CONSUMER_SECRET` - Empty ❌
- `MPESA_CALLBACK_URL` - Not set for your deployment ❌
- `MPESA_SHORTCODE` - Has placeholder value
- `MPESA_PASSKEY` - Has test value

## How Payment Flow Works

```
Frontend (Initiate Payment)
         ↓
Backend /payments/initiate (auth required)
         ↓
MpesaService.initiate_stk_push()
         ↓
1. Get OAuth Token (requires CONSUMER_KEY + CONSUMER_SECRET) ← FAILS HERE
2. Format phone number
3. Create STK Push request
4. Send to Safaricom API
5. Return CheckoutRequestID to frontend
         ↓
Frontend shows STK prompt to user
         ↓
User enters M-Pesa PIN
         ↓
M-Pesa calls back to CALLBACK_URL
         ↓
Update payment status in database
```

## Solution: Setup M-Pesa Integration

### Step 1: Get Daraja API Credentials
1. Go to https://developer.safaricom.co.ke/
2. Create/Login to your developer account
3. Create a new app:
   - App Name: "BiasharaIQ" (or similar)
   - App Type: "Web Application"
4. Once created, you'll get:
   - **Consumer Key** (copy this)
   - **Consumer Secret** (copy this)

### Step 2: Get Your Shortcode & Passkey
- For **Sandbox (Testing)**:
  - Shortcode: `174379`
  - Passkey: `bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919`
  
- For **Production**:
  - You'll get these from Safaricom when you go live

### Step 3: Setup Callback URL
The callback URL is where M-Pesa sends the payment result.

**For Local Development (sandbox):**
```
http://localhost:8000/payments/callback
```

**For Production (Render/deployed):**
```
https://your-api-domain.com/payments/callback
```

### Step 4: Configure Environment Variables

Create/Update `backend/.env`:
```env
# M-Pesa Daraja API Credentials
MPESA_CONSUMER_KEY=your_consumer_key_from_developer_portal
MPESA_CONSUMER_SECRET=your_consumer_secret_from_developer_portal
MPESA_SHORTCODE=174379
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
MPESA_CALLBACK_URL=https://your-api-domain.com/payments/callback
MPESA_ENVIRONMENT=sandbox

# Other existing config
DATABASE_URL=postgresql://biasharaiq_user:HNGUx7rn1527Utk6SAFtEffp7tUrI85z@dpg-d7p4gi5ckfvc73f23k20-a.oregon-postgres.render.com/biasharaiq
SECRET_KEY=dev-secret-key-change-in-production-min-32-chars
ENVIRONMENT=development
```

### Step 5: Restart Backend
```bash
# Stop current backend
Ctrl+C

# Restart
python main.py
```

## Testing the Fix

### Option 1: Use the test script
```bash
python test_mpesa_integration.py
```

### Option 2: Manual test with curl
```bash
# 1. Register a test user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "business_name": "Test Business",
    "owner_name": "Test Owner"
  }'

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
# Copy the access_token

# 3. Initiate payment (replace TOKEN with access_token)
curl -X POST http://localhost:8000/payments/initiate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "phone": "254708374149",
    "amount": 1
  }'
```

Expected successful response:
```json
{
  "checkout_id": "ws_CO_28062025136500",
  "message": "Success. Request accepted for processing"
}
```

## Troubleshooting

### Error: "Authentication failed"
- ✓ Check MPESA_CONSUMER_KEY is not empty
- ✓ Check MPESA_CONSUMER_SECRET is not empty
- ✓ Check credentials are from the correct Safaricom developer account
- ✓ Restart backend after updating .env

### Error: "Invalid shortcode"
- ✓ For sandbox, use: `174379`
- ✓ For production, use your registered shortcode

### Error: "Invalid callback URL"
- ✓ Make sure MPESA_CALLBACK_URL is set correctly
- ✓ For production, must be HTTPS (not HTTP)
- ✓ For sandbox, HTTP is OK

### Payment appears pending forever
- ✓ Check callback URL is accessible by M-Pesa
- ✓ Check backend logs for callback errors
- ✓ Verify MPESA_CALLBACK_URL matches where M-Pesa should POST

### Error: "CheckoutRequestID not in response"
- ✓ Verify Daraja API credentials are correct
- ✓ Check if Safaricom API status page shows issues
- ✓ Ensure you're using sandbox for testing

## Current Code Issues Requiring Configuration

### File: `backend/core/config.py`
```python
# These values are currently empty and MUST be configured:
MPESA_CONSUMER_KEY: str = os.getenv("MPESA_CONSUMER_KEY", "")
MPESA_CONSUMER_SECRET: str = os.getenv("MPESA_CONSUMER_SECRET", "")
```

### File: `backend/services/mpesa.py`
Line 28-29: If credentials are empty, this will fail:
```python
def get_access_token(self) -> Optional[str]:
    # Fails silently if CONSUMER_KEY or CONSUMER_SECRET are empty
```

## Quick Checklist
- [ ] Created Safaricom Daraja developer account
- [ ] Got Consumer Key & Consumer Secret
- [ ] Set MPESA_CONSUMER_KEY in .env
- [ ] Set MPESA_CONSUMER_SECRET in .env
- [ ] Set MPESA_CALLBACK_URL in .env (correct domain)
- [ ] Set MPESA_ENVIRONMENT=sandbox for testing
- [ ] Restarted backend
- [ ] Tested with `test_mpesa_integration.py`

## Links
- Safaricom Developer Portal: https://developer.safaricom.co.ke/
- M-Pesa API Documentation: https://developer.safaricom.co.ke/apis
- Daraja API Guide: https://developer.safaricom.co.ke/docs/daraja/
