# 🔑 Environment Variables Reference

**Quick Reference** for all environment variables needed across the stack.

---

## 📌 Summary Table

| Variable | Required | Where | Source | Example |
|----------|----------|-------|--------|---------|
| `ENVIRONMENT` | ✅ | Backend | Set to "production" | `production` |
| `DATABASE_URL` | ✅ | Backend | Render auto-injects | `postgresql://...` |
| `SECRET_KEY` | ✅ | Backend | Generate fresh | `57802ecfc68...` |
| `ANTHROPIC_API_KEY` | ✅ | Backend | Anthropic Console | `sk-ant-...` |
| `MPESA_CONSUMER_KEY` | ✅ | Backend | M-Pesa Daraja | `Your_Key_Here` |
| `MPESA_CONSUMER_SECRET` | ✅ | Backend | M-Pesa Daraja | `Your_Secret_Here` |
| `MPESA_ENVIRONMENT` | ✅ | Backend | Set to "sandbox" or "production" | `sandbox` |
| `CORS_ORIGINS` | ✅ | Backend | Your URLs | `https://domain.com` |
| `NEXT_PUBLIC_API_URL` | ✅ | Frontend | Backend URL | `https://biasharaiq.onrender.com` |
| `NODE_ENV` | ✅ | Frontend | Set to "production" | `production` |

---

## 🖥️ Backend Environment Variables

### Location
- **Development**: `.env` file in `backend/` folder
- **Production**: Render dashboard → Service settings → Environment

### All Backend Variables

```bash
# ====================
# REQUIRED - Environment & Deployment
# ====================
ENVIRONMENT=production
LOG_LEVEL=INFO

# ====================
# REQUIRED - Security
# ====================
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=57802ecfc68471c613ad1dfa2056a03f035a21cc711c3718e613fdcbe1c6d9af
JWT_SECRET=57802ecfc68471c613ad1dfa2056a03f035a21cc711c3718e613fdcbe1c6d9af

# ====================
# REQUIRED - Database
# ====================
# Render will auto-inject this; otherwise use local PostgreSQL
DATABASE_URL=postgresql://biasharaiq_user:password@host/biasharaiq
DB_POOL_SIZE=25
DB_MAX_OVERFLOW=15

# ====================
# REQUIRED - API URLs
# ====================
FRONTEND_URL=https://biashara-iq.vercel.app
CORS_ORIGINS=https://biashara-iq.vercel.app,https://biasharaiq.onrender.com

# ====================
# REQUIRED - AI Integration
# ====================
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
# Optional:
GEMINI_API_KEY=your-gemini-key-here

# ====================
# REQUIRED - M-Pesa Payment
# ====================
MPESA_CONSUMER_KEY=your-sandbox-consumer-key
MPESA_CONSUMER_SECRET=your-sandbox-consumer-secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
MPESA_CALLBACK_URL=https://biasharaiq.onrender.com/payments/callback
MPESA_ENVIRONMENT=sandbox

# ====================
# OPTIONAL - Monitoring
# ====================
# SENTRY_DSN=https://your-key@sentry.io/project-id
```

---

## 🌐 Frontend Environment Variables

### Location
- **Development**: `frontend/.env.local` file
- **Production**: Vercel dashboard → Project settings → Environment variables

### All Frontend Variables

```bash
# ====================
# REQUIRED
# ====================
NEXT_PUBLIC_API_URL=https://biasharaiq.onrender.com
NEXT_PUBLIC_APP_NAME=BiasharaIQ
NODE_ENV=production

# The NEXT_PUBLIC_ prefix makes these available to browser (public)
# Regular variables without NEXT_PUBLIC_ are backend-only
```

---

## 🚀 Deployment Configuration

### Render Dashboard Setup

**Path**: Services → biasharaiq-api → Settings → Environment

Copy-paste all backend variables:

```
ENVIRONMENT=production
LOG_LEVEL=INFO
SECRET_KEY=[GENERATE NEW]
JWT_SECRET=[GENERATE NEW]
FRONTEND_URL=https://biashara-iq.vercel.app
CORS_ORIGINS=https://biashara-iq.vercel.app,https://biasharaiq.onrender.com
ANTHROPIC_API_KEY=[GET FROM ANTHROPIC]
MPESA_CONSUMER_KEY=[GET FROM M-PESA DARAJA]
MPESA_CONSUMER_SECRET=[GET FROM M-PESA DARAJA]
MPESA_SHORTCODE=174379
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
MPESA_CALLBACK_URL=https://biasharaiq.onrender.com/payments/callback
MPESA_ENVIRONMENT=sandbox
DB_POOL_SIZE=25
DB_MAX_OVERFLOW=15
```

**Note**: `DATABASE_URL` is auto-injected by Render when you link PostgreSQL service.

### Vercel Dashboard Setup

**Path**: Project settings → Environment variables

```
NEXT_PUBLIC_API_URL=https://biasharaiq.onrender.com
NEXT_PUBLIC_APP_NAME=BiasharaIQ
NODE_ENV=production
```

---

## 🔐 How to Get Each Credential

### 1. SECRET_KEY & JWT_SECRET (Generate Fresh)

Generate a new secure key:
```bash
# Option 1: Python
python -c "import secrets; print(secrets.token_hex(32))"

# Option 2: OpenSSL
openssl rand -hex 32

# Option 3: Online (less secure, use for reference only)
# https://www.uuidgenerator.net/
```

Use the same value for both `SECRET_KEY` and `JWT_SECRET` (or generate different ones).

### 2. ANTHROPIC_API_KEY

1. Go to https://console.anthropic.com/
2. Sign in or create account
3. Click "API Keys" in sidebar
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-`)
6. Add to Render environment variables

### 3. M-Pesa Credentials (Daraja)

**For Sandbox (Testing)**:

1. Go to https://developer.safaricom.co.ke/
2. Create account or sign in
3. Click "My Apps" → "Create New App"
4. Give it a name (e.g., "BiasharaIQ")
5. Choose "Sandbox" environment
6. Copy:
   - **Client ID** → `MPESA_CONSUMER_KEY`
   - **Client Secret** → `MPESA_CONSUMER_SECRET`
7. Add to Render environment variables
8. Test with `/payments/initiate` endpoint

**For Production (Live)**:
- Complete business verification with Safaricom
- Request production credentials
- Get live Consumer Key and Secret
- Update environment variables
- Set `MPESA_ENVIRONMENT=production`

**M-Pesa Shortcode & Passkey** (Already set):
- Shortcode: `174379` (Safaricom test shortcode)
- Passkey: `bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919`

These are standard test values. When moving to production, you'll get your own.

### 4. Database URL

Automatically injected by Render when you create PostgreSQL service.

Format: `postgresql://user:password@host:port/database`

Example:
```
postgresql://biasharaiq_user:HNGUx7rn1527Utk6SAFtEffp7tUrI85z@dpg-d7p4gi5ckfvc73f23k20-a.oregon-postgres.render.com/biasharaiq
```

---

## ✅ Verification Checklist

### Before Deploying

- [ ] `SECRET_KEY` generated (64 characters)
- [ ] `JWT_SECRET` generated (64 characters)
- [ ] `ANTHROPIC_API_KEY` obtained from Anthropic Console
- [ ] `MPESA_CONSUMER_KEY` obtained from M-Pesa Daraja
- [ ] `MPESA_CONSUMER_SECRET` obtained from M-Pesa Daraja
- [ ] `FRONTEND_URL` matches Vercel deployment URL
- [ ] `CORS_ORIGINS` includes Vercel URL
- [ ] `NEXT_PUBLIC_API_URL` set to backend URL
- [ ] `.env` file NOT committed to Git (.gitignore should exclude it)
- [ ] All secrets in Render environment variables (not in code)

### After Deployment

```bash
# Test backend health
curl https://biasharaiq.onrender.com/health
# Expected: {"status": "healthy", "database": "connected"}

# Test API docs
curl https://biasharaiq.onrender.com/docs
# Expected: Swagger UI page loads

# Test M-Pesa integration
curl -X POST https://biasharaiq.onrender.com/payments/initiate \
  -H "Content-Type: application/json" \
  -d '{"phone": "254712345678", "amount": 100}'
# Expected: {"checkout_id": "...", "message": "Success..."}
```

---

## 🚨 Troubleshooting

### "Invalid DATABASE_URL"
- [ ] Check Render PostgreSQL service is created
- [ ] Verify Render injected DATABASE_URL
- [ ] If manual: format should be `postgresql://user:pass@host/db`

### "CORS Error in Frontend"
- [ ] Check `CORS_ORIGINS` includes your Vercel domain exactly
- [ ] Verify no trailing slashes in domain
- [ ] Redeploy backend after changing CORS_ORIGINS
- [ ] Clear browser cache

### "M-Pesa 401 Unauthorized"
- [ ] Verify `MPESA_CONSUMER_KEY` and `MPESA_CONSUMER_SECRET`
- [ ] Check they're from Daraja (not another service)
- [ ] Verify `MPESA_ENVIRONMENT=sandbox` for testing
- [ ] Check credentials in Render dashboard updated correctly

### "Can't find .env file in Docker"
- [ ] Don't add .env to Docker image
- [ ] Use Render/Vercel environment variables instead
- [ ] .env is only for local development

### "Secret expires / Token invalid"
- [ ] Verify `SECRET_KEY` and `JWT_SECRET` are set
- [ ] Check `ACCESS_TOKEN_EXPIRE_MINUTES=10080` (7 days)
- [ ] Restart backend service if changed

---

## 📝 Environment Variables by Component

### Backend Routes
All routes can access environment variables:
```python
from core.config import settings

print(settings.ENVIRONMENT)  # "production"
print(settings.MPESA_CONSUMER_KEY)  # Your M-Pesa key
```

### Frontend
Only `NEXT_PUBLIC_` variables are accessible in browser:
```javascript
const apiUrl = process.env.NEXT_PUBLIC_API_URL;
const appName = process.env.NEXT_PUBLIC_APP_NAME;
// Regular env vars are not accessible in browser
```

### Docker Containers
- Render/Vercel automatically injects environment variables
- Inside containers, code reads them like normal env vars
- No need to manually pass them to Docker

---

## 🔗 Related Files

- `.env` - Local development variables
- `.env.example` - Template with all available variables
- `backend/core/config.py` - Backend settings validation
- `render.yaml` - Render deployment configuration
- `frontend/vercel.json` - Vercel deployment configuration

---

## 📞 Need Help?

### Quick Reference
- [Anthropic Console](https://console.anthropic.com/)
- [M-Pesa Daraja](https://developer.safaricom.co.ke/)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Vercel Environment Variables](https://vercel.com/docs/environment-variables)

### Documentation
- See `PRODUCTION_DEPLOYMENT.md` for full deployment guide
- See `DEPLOYMENT_CHECKLIST.md` for quick setup steps

---

**Last Updated**: May 2026  
**Version**: 1.0  
**Status**: ✅ Complete
