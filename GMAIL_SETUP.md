# Gmail Configuration Guide for BiasharaIQ

## Setting Up Gmail SMTP for Email Verification

The email verification system is now configured to use Gmail (biasharaiq@gmail.com) for sending verification codes.

## ✅ Required Setup Steps

### Step 1: Enable 2-Factor Authentication on Gmail

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Click **Security** in the left sidebar
3. Find **2-Step Verification** and enable it
4. Follow the prompts to verify your identity

### Step 2: Create an App Password

Gmail doesn't allow regular passwords for third-party apps. You must use an **App Password**.

1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Select **Mail** and **Windows Computer** (or your OS)
3. Click **Generate**
4. Google will generate a 16-character password (e.g., `abcd efgh ijkl mnop`)
5. **Copy this password** - you'll use it in the next step

### Step 3: Update Your .env File

Add the Gmail app password to your `.env` file:

```env
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

Replace `abcdefghijklmnop` with the actual 16-character password from Step 2 (remove spaces if any).

### Step 4: Verify Configuration

Test the email service:

```bash
# From the backend directory
python -c "from services.email_verification import send_email; send_email('test@example.com', '123456')"
```

You should see:
```
[EMAIL SERVICE] ✓ Verification code sent to test@example.com
```

If you see an error, check:
- ✓ Gmail account has 2FA enabled
- ✓ App password is correctly copied (no spaces)
- ✓ GMAIL_APP_PASSWORD is in .env file
- ✓ Backend process restarted after .env changes

## 📧 Email Configuration

### Sender Email
- **From**: `biasharaiq@gmail.com`
- **Display Name**: BiasharaIQ

### Email Template Features
- ✓ Professional HTML formatting
- ✓ Large, easy-to-read verification code
- ✓ 10-minute expiry notice
- ✓ Spam-folder friendly
- ✓ Mobile-responsive design
- ✓ Plain text fallback

## 🔍 Troubleshooting

### Error: "Authentication failed"
**Solution**: 
- Verify the app password is correct (16 characters)
- Make sure you created the app password (not using regular Gmail password)
- Check that 2FA is enabled on the Gmail account

### Error: "SMTP connection refused"
**Solution**:
- Ensure `smtp.gmail.com:587` is not blocked by firewall
- Check internet connectivity

### Code sent to console instead of email
**Solution**:
- GMAIL_APP_PASSWORD is not set in .env
- Add it and restart the backend server

### Email takes too long to arrive
**Solution**:
- Check spam/promotions folder
- Verify sending succeeded in server logs
- Google may delay first emails from new apps

## 🔒 Security Best Practices

- ✓ Never commit `.env` file to git (already in .gitignore)
- ✓ Use App Passwords, not your main Gmail password
- ✓ Rotate app passwords periodically
- ✓ Create a separate Gmail account for production vs development
- ✓ Monitor Gmail's "App access" logs for suspicious activity

## 📱 Testing Email Verification

### Test via Frontend
1. Go to `http://localhost:3000/register`
2. Fill in registration form with test email
3. Click "Create Free Account"
4. Check your actual email inbox for the verification code
5. Enter code on verification page
6. You should be redirected to login

### Test via API
```bash
# Register a new user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "business_name": "Test Shop",
    "owner_name": "Test User"
  }'

# Code is sent to email automatically

# Verify the code (check email for actual code)
curl -X POST http://localhost:8000/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "code": "123456"
  }'

# Now login should work
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

## 📊 Email Logs

The email service logs to console with these prefixes:

- `[EMAIL SERVICE] ✓` - Email sent successfully
- `[EMAIL SERVICE] ✗` - Email send failed
- `[EMAIL SERVICE] WARNING` - Configuration issue (e.g., missing app password)
- `[FALLBACK]` - Code displayed in console when email fails

Monitor backend logs to verify emails are being sent correctly.

## 🚀 Production Considerations

### For Deployment (Render/Heroku):

1. Add `GMAIL_APP_PASSWORD` to environment variables:
   - Render: Settings → Environment
   - Heroku: `heroku config:set GMAIL_APP_PASSWORD="..."`

2. Ensure the Gmail account can handle your email volume (limit: 500+ emails/day)

3. Consider using a dedicated service account for stability

### Future Enhancements:

- Add email templates with branding
- Support SMS as fallback verification method
- Implement email rate limiting
- Add unsubscribe links for compliance
- Track email delivery metrics

## 📞 Support

If email verification isn't working:

1. Check backend logs for `[EMAIL SERVICE]` messages
2. Verify GMAIL_APP_PASSWORD is set: `echo $GMAIL_APP_PASSWORD`
3. Test SMTP connection manually:
   ```bash
   python -m smtplib -t smtp.gmail.com -p 587 -u biasharaiq@gmail.com
   ```
4. Check Gmail's "Sign-in & security" → "Your devices" for blocked access attempts
