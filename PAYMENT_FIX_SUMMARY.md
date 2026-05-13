# Payment Failure Fix - Summary

## Issue
Payment initiation fails with error like "Authentication failed" or missing API credentials.

## Root Cause
M-Pesa Daraja API credentials (CONSUMER_KEY and CONSUMER_SECRET) are not configured in your `.env` file.

## What I've Done

### 1. **Enhanced Error Messages** ✓
- Updated `backend/services/mpesa.py` to provide clear, actionable error messages
- Added configuration validation on service initialization
- Improved error handling for network issues, invalid credentials, and API errors
- Updated `backend/routes/payments.py` to return detailed error information

### 2. **Created Helper Tools**

#### `setup_mpesa.py` - Configuration Wizard
Interactive setup wizard to configure M-Pesa credentials
```bash
python setup_mpesa.py
```
- Prompts for Consumer Key, Secret, Shortcode, Passkey, Callback URL
- Automatically saves to `.env` file
- Validates input and provides guidance

#### `validate_mpesa.py` - Credential Validator  
Tests M-Pesa credentials without running the backend
```bash
python validate_mpesa.py
```
- Loads `.env` configuration
- Tests OAuth authentication with M-Pesa
- Validates request format
- Suggests next steps if validation fails

#### `PAYMENT_DEBUG.md` - Diagnostic Guide
Comprehensive guide to diagnosing and fixing payment issues

### 3. **Improved Error Handling**
The backend now provides specific error messages:
- "Missing M-Pesa configuration: MPESA_CONSUMER_KEY, ..." 
- "M-Pesa credentials not configured. Set MPESA_CONSUMER_KEY..."
- "Invalid credentials (check MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET)"
- "M-Pesa callback URL not configured..."

## Quick Start - Fix Payment Issues

### Step 1: Configure M-Pesa Credentials
```bash
python setup_mpesa.py
```
This will guide you through:
1. Selecting sandbox or production environment
2. Entering your Safaricom Daraja credentials
3. Setting up callback URL
4. Saving to `.env` file

**You need:**
- Go to https://developer.safaricom.co.ke/
- Create/login to account
- Create a new app → get Consumer Key & Consumer Secret

### Step 2: Validate Configuration
```bash
python validate_mpesa.py
```
This will:
- Check if all required credentials are present
- Test OAuth authentication with Safaricom
- Validate STK Push request format
- Tell you if everything is configured correctly

### Step 3: Restart Backend
```bash
python main.py
```

### Step 4: Test Payment
```bash
python test_mpesa_integration.py
```

## Configuration Reference

### Required Environment Variables
```env
# From Safaricom Developer Portal
MPESA_CONSUMER_KEY=your_key_here
MPESA_CONSUMER_SECRET=your_secret_here

# Standard values
MPESA_SHORTCODE=174379              # (for sandbox)
MPESA_PASSKEY=bfb279f9...           # (for sandbox - given above)

# Your callback endpoint
MPESA_CALLBACK_URL=https://your-domain.com/payments/callback

# Environment
MPESA_ENVIRONMENT=sandbox            # (or "production")
```

### Getting Credentials
1. **Consumer Key & Secret:**
   - Go to https://developer.safaricom.co.ke/
   - Login/Register
   - Create new app
   - Copy credentials

2. **Shortcode & Passkey (Sandbox):**
   - Use provided values above
   - Safaricom provides when you go live

3. **Callback URL:**
   - Sandbox: `http://localhost:8000/payments/callback`
   - Production: `https://your-api-domain.com/payments/callback` (HTTPS required!)

## Testing Payment Flow

### Local Testing (Sandbox)
```bash
# Terminal 1: Start backend
python main.py

# Terminal 2: Run validation
python validate_mpesa.py

# Terminal 3: Run integration test
python test_mpesa_integration.py
```

### Frontend Testing
1. Visit your frontend (http://localhost:3000 or deployed URL)
2. Go to Pricing page
3. Click "Upgrade to Pro"
4. Enter phone number in format: `0708374149` or `254708374149`
5. Amount will be 499 KES by default
6. Click "Pay" - STK prompt should appear on phone

### What to Expect
✓ **Success:** STK prompt appears on phone within 1-2 seconds
✓ **Failure:** Backend returns clear error message in console

## Troubleshooting

### "Authentication failed" error
```
Solution: Check MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET in .env
Run: python validate_mpesa.py
```

### "Invalid credentials" (401 response)
```
Solution: Verify credentials are correct from Safaricom Developer Portal
Check: https://developer.safaricom.co.ke/
```

### "Request timed out"
```
Solution: Network/API issue - M-Pesa API may be slow
Try again after a few minutes
Check: Safaricom API status page
```

### "CheckoutRequestID not in response"
```
Solution: Check M-Pesa API response for error details
Ensure credentials, shortcode, passkey are correct
Verify using: python validate_mpesa.py
```

### "Callback URL not configured"
```
Solution: Set MPESA_CALLBACK_URL in .env
Must be accessible by M-Pesa (HTTPS for production)
```

### Payment appears pending forever
```
Solution: Check if callback URL is reachable by M-Pesa
Check backend logs for callback errors:
python main.py  # Look for "Received M-Pesa callback"
```

## Files Modified

1. **backend/services/mpesa.py**
   - Added `_validate_config()` method
   - Enhanced `get_access_token()` with specific error messages
   - Improved `initiate_stk_push()` error handling
   - Better logging for debugging

2. **backend/routes/payments.py**
   - Enhanced `initiate_payment()` endpoint
   - Better error responses
   - Proper exception handling

## Files Created

1. **setup_mpesa.py** - Interactive setup wizard
2. **validate_mpesa.py** - Credential validator
3. **PAYMENT_DEBUG.md** - Diagnostic guide

## Next Steps

1. **Run setup:**
   ```bash
   python setup_mpesa.py
   ```

2. **Validate configuration:**
   ```bash
   python validate_mpesa.py
   ```

3. **Restart backend** and test

4. **Monitor logs** for any remaining issues

5. **Test from frontend** - should work now!

## Support Resources

- Safaricom Developer Docs: https://developer.safaricom.co.ke/docs/daraja/
- M-Pesa API Reference: https://developer.safaricom.co.ke/apis
- Sandbox Testing: https://sandbox.safaricom.co.ke/
- Test Credentials: Provided by Safaricom when you create app

## Quick Reference Commands

```bash
# Setup credentials
python setup_mpesa.py

# Validate credentials
python validate_mpesa.py

# Start backend
python main.py

# Test integration
python test_mpesa_integration.py

# Check backend logs (Linux/Mac)
tail -f backend.log

# Check backend logs (Windows PowerShell)
Get-Content backend.log -Wait
```

## Architecture Reminder

```
Frontend (Payment Request)
    ↓
Backend /payments/initiate
    ↓
MpesaService.initiate_stk_push()
    ↓
1. get_access_token() ← Uses CONSUMER_KEY + CONSUMER_SECRET
2. Format phone number
3. Create STK Push request
4. Call Safaricom API
    ↓
Safaricom M-Pesa API
    ↓
Returns: CheckoutRequestID
    ↓
Frontend shows to user
    ↓
User enters M-Pesa PIN
    ↓
M-Pesa calls CALLBACK_URL
    ↓
Backend updates payment status
```

---

**Status:** ✓ Ready to test  
**Next Action:** Run `python setup_mpesa.py` to configure credentials
