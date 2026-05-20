# 🚀 Email Verification Testing Guide

## ✅ System Status Check

Your email verification system is now fully configured with:

✓ Gmail SMTP (biasharaiq@gmail.com)  
✓ 6-digit verification codes  
✓ 10-minute code expiry  
✓ Professional HTML emails  
✓ Frontend integration complete  
✓ Resend code functionality  
✓ Error handling & logging  

---

## 📋 Pre-Testing Checklist

- [ ] Backend `.env` has `GMAIL_APP_PASSWORD` set
- [ ] Backend is running (`python main.py`)
- [ ] Frontend is running (`npm run dev`)
- [ ] Database is accessible
- [ ] Test email account ready

---

## 🧪 Test Scenario 1: Full Registration Flow

### Step 1: Start Services
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Step 2: Register New User
1. Open `http://localhost:3000/register`
2. Fill in the form:
   - **Business Name**: `Test Shop`
   - **Owner Name**: `Test User`
   - **Business Type**: `Retail Shop`
   - **Email**: Your actual email address
   - **Phone**: `0712345678`
   - **Password**: `TestPassword123` (8+ characters)
3. Click **"Create Free Account"**

### Step 3: Check Email Verification
- **Expected**: Redirected to `/verify-email?email=your@email.com`
- **In your email**: Check inbox for verification code
- **Backend console**: Should see `[EMAIL SERVICE] ✓ Verification code sent to your@email.com`

### Step 4: Verify Email
1. Copy the 6-digit code from email
2. Paste into the verification page
3. Click **"Verify Email"**
4. **Expected**: Success screen appears
5. **Auto-redirect**: Redirected to `/login` after 2 seconds

### Step 5: Login
1. Email: Your test email
2. Password: `TestPassword123`
3. Click **"Sign In"**
4. **Expected**: Logged in successfully → Dashboard appears

---

## 🧪 Test Scenario 2: Unverified User Cannot Login

### Step 1: Create User But Don't Verify
1. Register another user: `user2@example.com`
2. **Don't** verify the email (close the verification page)

### Step 2: Try to Login
1. Go to `/login`
2. Enter email and password
3. Click **"Sign In"**

### Step 3: Expected Result
```
❌ Error Message:
"Email not verified. Please verify your email first."
```

---

## 🧪 Test Scenario 3: Resend Verification Code

### Step 1: Start Verification Page
1. Go through registration flow
2. On verification page, look for **"Didn't receive the code?"**

### Step 2: Test Resend
1. Click **"Resend Code"** button
2. **Expected**: Button shows `"Resend in 60s"` countdown

### Step 3: Check Email
1. You should receive a **second** verification code
2. **Backend console**: Should see `[EMAIL SERVICE] ✓ Verification code sent...`

### Step 4: Use New Code
1. Enter the new 6-digit code
2. Click **"Verify Email"**
3. **Expected**: Success

---

## 🧪 Test Scenario 4: Invalid Code Handling

### Step 1: Enter Wrong Code
1. On verification page, enter: `000000`
2. Click **"Verify Email"**

### Step 2: Expected Result
```
❌ Error Message:
"Invalid or expired code. Please try again."
```

### Step 3: Code Field Reset
- Code field should clear
- Allow re-entry

---

## 🧪 Test Scenario 5: Code Expiry

### Step 1: Wait for Expiry
1. Register user
2. **Don't verify for 10+ minutes**

### Step 2: Try Expired Code
1. Enter the old code
2. Click **"Verify Email"**

### Step 3: Expected Result
```
❌ Error Message:
"Invalid or expired code. Please try again."
```

### Step 4: Resend & Verify
1. Click **"Resend Code"** to get new code
2. Enter new code
3. **Expected**: Success

---

## 📊 Backend Console Output - What to Look For

### ✅ Successful Email Send
```
[EMAIL SERVICE] ✓ Verification code sent to user@example.com
```

### ✅ Successful Verification
```
[EMAIL SERVICE] ✓ Email verification successful
```

### ⚠️ Authentication Error
```
[EMAIL SERVICE] ✗ Authentication failed. Check GMAIL_APP_PASSWORD in .env
[FALLBACK] Verification code for user@example.com: 123456
```

### ⚠️ Connection Error
```
[EMAIL SERVICE] ✗ SMTP error: Connection refused
[FALLBACK] Verification code for user@example.com: 123456
```

---

## 🔍 API Testing (Using curl or Postman)

### Test 1: Send Verification Code
```bash
curl -X POST http://localhost:8000/auth/send-verification \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'

# Response:
# {
#   "message": "Verification code sent to email",
#   "email": "test@example.com"
# }
```

### Test 2: Verify Email with Code
```bash
curl -X POST http://localhost:8000/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "code": "123456"
  }'

# Response:
# {
#   "message": "Email verified successfully"
# }
```

### Test 3: Login (Before Email Verification)
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'

# Response (403):
# {
#   "detail": "Email not verified. Please verify your email first."
# }
```

### Test 4: Login (After Email Verification)
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'

# Response (200):
# {
#   "access_token": "eyJhbGc...",
#   "token_type": "bearer",
#   "user": {
#     "id": 1,
#     "email": "test@example.com",
#     "business_name": "Test Shop",
#     "owner_name": "Test User"
#   }
# }
```

---

## 📈 User Journey Map

```
┌─────────────────────────────────────────────────────────────────┐
│                    REGISTRATION FLOW                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Register Page ──────→ Create Account                             │
│       ↓                      ↓                                     │
│   Fill Form           Backend Creates User                        │
│       ↓                      ↓                                     │
│   Submit ────────────→ Generate Code                              │
│                            ↓                                      │
│                      Send Email (Gmail)                           │
│                            ↓                                      │
│                      is_verified = false                          │
│                            ↓                                      │
│                    Redirect to Verify Page                        │
│                            ↓                                      │
│  Verify Email Page ────→ Receive Email                            │
│       ↓                      ↓                                     │
│   Enter Code          Check Inbox                                 │
│       ↓                      ↓                                     │
│   Submit ────────────→ Verify Code                                │
│                            ↓                                      │
│                      is_verified = true                           │
│                            ↓                                      │
│                    Show Success Screen                            │
│                            ↓                                      │
│  Login Page ──────────→ Auto Redirect                             │
│       ↓                      ↓                                     │
│   Enter Credentials   Can Now Login                               │
│       ↓                      ↓                                     │
│   Submit ────────────→ Auth Successful                            │
│                            ↓                                      │
│  Dashboard ─────────────────┘                                     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Feature Verification Checklist

- [ ] Email received within 30 seconds of registration
- [ ] 6-digit code visible in email
- [ ] Verification page auto-populates email
- [ ] Code input is numeric only, max 6 digits
- [ ] Valid code shows success screen
- [ ] Invalid code shows error message
- [ ] Code clears after failed attempt
- [ ] Resend button has 60-second cooldown
- [ ] Resend sends new code (not same code)
- [ ] Login blocked for unverified emails
- [ ] Login works after verification
- [ ] Email link has proper branding
- [ ] Email renders well on mobile

---

## 🐛 Troubleshooting During Testing

### Problem: "Email not sending"
```
✓ Check backend console for [EMAIL SERVICE] messages
✓ Verify GMAIL_APP_PASSWORD is set in .env
✓ Restart backend after .env changes
✓ Check spam/promotions folder
```

### Problem: "Authentication failed"
```
✓ Verify GMAIL_APP_PASSWORD is correct (16 chars)
✓ Make sure 2FA is enabled on Gmail account
✓ Check app password wasn't expired (regenerate if needed)
```

### Problem: "Code not working"
```
✓ Ensure exactly 6 digits
✓ Check code hasn't expired (10 minute limit)
✓ Try resending for new code
```

### Problem: "Can't login after verification"
```
✓ Check database - is_verified should be True
✓ Verify the same email address was used
✓ Try clearing browser cache/cookies
```

---

## 📞 Success Criteria

Your email verification is working when:

✅ User receives email within 30 seconds  
✅ Code is correct and works  
✅ Invalid codes show proper error  
✅ Unverified users cannot login  
✅ Verified users can login  
✅ Email has professional formatting  
✅ Resend button works with cooldown  
✅ All API endpoints respond correctly  

---

## 🎯 Next Steps After Testing

1. **Deploy to production**
   - Add GMAIL_APP_PASSWORD to Render environment variables
   - Add GMAIL_APP_PASSWORD to Vercel if needed

2. **Monitor first week**
   - Watch backend logs for email failures
   - Check Gmail sending limits
   - Adjust email template if needed

3. **Future enhancements**
   - Add custom email templates
   - Implement password reset flow
   - Add SMS verification as backup

---

## 📞 Support

If testing fails:
1. Check [GMAIL_SETUP.md](GMAIL_SETUP.md) for detailed configuration
2. Review backend console logs for `[EMAIL SERVICE]` messages
3. Verify .env file has correct app password
4. Test via curl before testing UI
5. Check Gmail security logs for blocked access

**Ready to test?** Start with Test Scenario 1! 🚀
