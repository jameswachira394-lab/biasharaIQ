# BiasharaIQ - Production Deployment Guide

**Last Updated**: May 2026  
**Status**: Full-stack production integration ready

---

## 📋 Overview

BiasharaIQ is a full-stack financial intelligence platform with:
- **Backend**: FastAPI (Python) on Render.com
- **Frontend**: Next.js (React) on Vercel  
- **Database**: PostgreSQL on Render.com
- **Payments**: M-Pesa integration (Daraja API)
- **AI**: Anthropic Claude integration

---

## 🚀 Production Deployment Checklist

### Phase 1: Pre-Deployment Setup (Local)

#### 1. Environment Configuration
- [x] Database URL configured (Render PostgreSQL)
- [x] Production SECRET_KEY generated
- [x] CORS origins configured
- [x] API keys placeholder added

**Status**: Backend config updated in `.env`

#### 2. Required Credentials (Get these from providers)

```
[ ] ANTHROPIC_API_KEY - Get from https://console.anthropic.com/
[ ] MPESA_CONSUMER_KEY - Get from https://developer.safaricom.co.ke/
[ ] MPESA_CONSUMER_SECRET - Get from https://developer.safaricom.co.ke/
```

---

### Phase 2: Backend Deployment (Render)

#### Setup Instructions:

1. **Connect Repository**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select branch: `main`

2. **Configure Service**
   - Name: `biasharaiq-api`
   - Environment: `Python 3.11`
   - Region: `Frankfurt` (or closest to users)
   - Plan: Start with `Free` tier
   - Build Command: `pip install -r requirements.txt`
   - Start Command: 
     ```
     gunicorn main:app --workers=4 --worker-class=uvicorn.workers.UvicornWorker --bind=0.0.0.0:$PORT
     ```

3. **Environment Variables** (in Render dashboard)
   ```
   ENVIRONMENT=production
   SECRET_KEY=[your-generated-secret-key]
   ANTHROPIC_API_KEY=[your-anthropic-key]
   MPESA_CONSUMER_KEY=[your-mpesa-key]
   MPESA_CONSUMER_SECRET=[your-mpesa-secret]
   MPESA_CALLBACK_URL=https://biasharaiq.onrender.com/payments/callback
   MPESA_ENVIRONMENT=sandbox
   CORS_ORIGINS=https://biashara-iq.vercel.app,https://biasharaiq.onrender.com
   LOG_LEVEL=INFO
   ```

4. **Create PostgreSQL Database** (if not already created)
   - Click "New +" → "PostgreSQL"
   - Name: `biasharaiq-db`
   - Region: `Frankfurt`
   - Plan: `Free`
   - Link to backend service (Render will auto-inject DATABASE_URL)

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (2-5 minutes)
   - Verify: `https://biasharaiq.onrender.com/health`

**Expected Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "production"
}
```

---

### Phase 3: Frontend Deployment (Vercel)

#### Setup Instructions:

1. **Connect Repository**
   - Go to https://vercel.com
   - Click "Add New..." → "Project"
   - Import from Git (GitHub)
   - Select repository

2. **Configure Project**
   - Framework Preset: `Next.js`
   - Root Directory: `./frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

3. **Environment Variables** (in Vercel dashboard)
   ```
   NEXT_PUBLIC_API_URL=https://biasharaiq.onrender.com
   NEXT_PUBLIC_APP_NAME=BiasharaIQ
   NODE_ENV=production
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment (1-3 minutes)
   - Verify frontend loads at your Vercel URL

**Expected**: Dashboard loads, can navigate without errors

---

### Phase 4: Database Initialization

Once backend is deployed on Render:

```bash
# Option A: Using psql from your local machine
psql -h dpg-d7p4gi5ckfvc73f23k20-a.oregon-postgres.render.com \
     -U biasharaiq_user \
     -d biasharaiq \
     -f backend/schema.sql

# Option B: Using Render dashboard
# 1. Go to Render PostgreSQL service dashboard
# 2. Click "Connect" → "Direct Connection"
# 3. Use connection string in your SQL client
# 4. Run schema.sql and seed_demo.py
```

---

### Phase 5: M-Pesa Integration

#### Sandbox Setup (Testing)

1. **Get Credentials**
   - Visit https://developer.safaricom.co.ke/
   - Create/login to account
   - Create an app under Sandbox
   - Copy: `Client ID` (Consumer Key) and `Client Secret` (Consumer Secret)

2. **Configure in Render**
   - Go to backend service settings
   - Add/update environment variables:
     ```
     MPESA_CONSUMER_KEY=your-sandbox-client-id
     MPESA_CONSUMER_SECRET=your-sandbox-client-secret
     MPESA_ENVIRONMENT=sandbox
     MPESA_CALLBACK_URL=https://biasharaiq.onrender.com/payments/callback
     ```

3. **Test Payment Flow**
   ```bash
   curl -X POST https://biasharaiq.onrender.com/payments/initiate \
     -H "Content-Type: application/json" \
     -d '{
       "phone": "254712345678",
       "amount": 499
     }'
   ```

#### Production Setup (Live Payments)

1. **Get Live Credentials**
   - Complete Safaricom verification process
   - Request production credentials
   - Provide business details and website

2. **Update Configuration**
   - Set `MPESA_ENVIRONMENT=production`
   - Update `MPESA_CONSUMER_KEY` and `MPESA_CONSUMER_SECRET`
   - Update `MPESA_CALLBACK_URL` to production domain

3. **Enable Webhook**
   - Configure M-Pesa callback URL in Daraja portal
   - Ensure `/payments/callback` endpoint is live

---

### Phase 6: SSL/TLS & Security

#### Backend (Render)
- ✅ Automatic HTTPS (provided by Render)
- ✅ Security headers configured in `main.py`
- ✅ CORS properly configured

#### Frontend (Vercel)
- ✅ Automatic HTTPS (provided by Vercel)
- ✅ Automatic deploy previews for PRs

#### Database
- ✅ TLS connection string enforced
- ✅ Password protected

---

## 📊 Deployment Architecture

```
┌─────────────────────┐
│   Vercel Hosting    │
│   (Frontend)        │
│  biashara-iq.com    │
└──────────┬──────────┘
           │ (HTTPS)
           ↓
┌─────────────────────────────────┐
│    Render.com                   │
├─────────────────────────────────┤
│  Backend Service                │
│  - FastAPI (Python)             │
│  - Port: 5000                   │
│  - gunicorn server              │
│  - CORS to Vercel               │
└────────────┬────────────────────┘
             │ (Internal)
             ↓
┌─────────────────────────────────┐
│    PostgreSQL Database          │
│  - Render managed               │
│  - TLS encrypted                │
│  - Automated backups            │
└─────────────────────────────────┘
             
┌─────────────────────────────────┐
│    External Services            │
├─────────────────────────────────┤
│  M-Pesa (Daraja API)            │
│  Anthropic Claude API           │
│  Google Gemini API              │
└─────────────────────────────────┘
```

---

## 🔍 Verification Steps

### 1. Backend Health Check
```bash
curl https://biasharaiq.onrender.com/health
# Expected: {"status": "healthy", "database": "connected"}
```

### 2. Frontend Load Test
```bash
# Visit frontend URL
https://biashara-iq.vercel.app

# Check:
✅ Page loads without errors
✅ Dashboard displays
✅ API calls succeed (check Network tab)
✅ Sidebar and navigation work
```

### 3. Database Connectivity
```bash
# From Render backend logs
tail -f logs

# Look for:
✅ "Database initialized successfully"
✅ No connection errors
```

### 4. M-Pesa Payment Flow (Sandbox)
```bash
# Initiate payment
curl -X POST https://biasharaiq.onrender.com/payments/initiate \
  -H "Content-Type: application/json" \
  -d '{"phone": "254712345678", "amount": 100}'

# Expected:
{
  "checkout_id": "...",
  "message": "Success. Request accepted for processing"
}
```

---

## 🆘 Troubleshooting

### Backend Won't Start
**Symptoms**: Deployment fails, 502 Bad Gateway

**Solution**:
1. Check Render logs: `Services` → `biasharaiq-api` → `Logs`
2. Common issues:
   - Missing DATABASE_URL → Add in Render env vars
   - Missing SECRET_KEY → Generate new one
   - Python version mismatch → Use Python 3.11+

### Frontend Shows "Cannot connect to API"
**Symptoms**: CORS errors in browser console

**Solution**:
1. Verify backend is running: `curl https://biasharaiq.onrender.com/health`
2. Check Vercel env vars have correct `NEXT_PUBLIC_API_URL`
3. Verify CORS_ORIGINS in backend includes Vercel domain

### Database Connection Failed
**Symptoms**: `SQLALCHEMY_ERROR`, database queries fail

**Solution**:
1. Verify DATABASE_URL is correct in Render
2. Check PostgreSQL service is running (not sleeping on free tier)
3. Restart PostgreSQL from Render dashboard

### M-Pesa Sandbox Tests Fail
**Symptoms**: 401 errors, invalid credentials

**Solution**:
1. Verify MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET
2. Check MPESA_ENVIRONMENT is set to "sandbox"
3. Ensure callback URL is accessible: `curl https://biasharaiq.onrender.com/payments/callback`

---

## 📈 Monitoring & Maintenance

### Daily
- Check error logs: Render → Logs
- Monitor API response times
- Check M-Pesa payment success rate

### Weekly
- Review database disk usage (Render)
- Check error rates in logs
- Verify backups are working

### Monthly
- Review and update dependencies
- Audit security settings
- Check cost optimization opportunities

---

## 🔒 Security Checklist

- [x] All secrets in environment variables (not in code)
- [x] HTTPS/TLS enforced
- [x] CORS properly configured
- [x] Security headers added
- [x] Database password protected
- [x] API authentication (JWT) configured
- [x] M-Pesa credentials stored securely
- [ ] Regular security updates
- [ ] Monitoring and alerts configured

---

## 📞 Support

### Render Issues
- Docs: https://render.com/docs
- Status: https://status.render.com
- Support: https://render.com/support

### Vercel Issues
- Docs: https://vercel.com/docs
- Status: https://www.vercel-status.com
- Support: https://vercel.com/support

### M-Pesa Integration
- Docs: https://developer.safaricom.co.ke/
- Test Account: Use sandbox credentials from Daraja portal

---

## 🎯 Next Steps

1. **Immediate**:
   - Add ANTHROPIC_API_KEY to Render
   - Add M-Pesa credentials (sandbox first)
   - Run database initialization

2. **Within 24 hours**:
   - Complete end-to-end testing
   - Test all payment flows
   - Verify AI features work

3. **Before Going Live**:
   - Get M-Pesa production credentials
   - Update all URLs to production domains
   - Set up error monitoring (Sentry optional)
   - Create backup/disaster recovery plan

---

**Version**: 1.0  
**Last Updated**: May 2026  
**Status**: Production Ready ✅
