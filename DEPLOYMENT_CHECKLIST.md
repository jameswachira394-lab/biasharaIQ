# 🚀 Quick Deployment Checklist

Use this checklist to deploy BiasharaIQ to production.

---

## Pre-Deployment (5 min)

- [ ] All secrets are generated or obtained
- [ ] GitHub repository is up to date
- [ ] Local `.env` file has production URLs
- [ ] No hardcoded credentials in code
- [ ] All tests pass locally

---

## Backend Deployment (Render) - 10 min

### Create Service
- [ ] Login to https://render.com
- [ ] Click "New +" → "Web Service"
- [ ] Connect GitHub repository
- [ ] Select `main` branch
- [ ] Set service name: `biasharaiq-api`

### Configure
- [ ] Environment: Python 3.11
- [ ] Region: Frankfurt
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `gunicorn main:app --workers=4 --worker-class=uvicorn.workers.UvicornWorker --bind=0.0.0.0:$PORT`

### Environment Variables
```
ENVIRONMENT=production
SECRET_KEY=[COPY FROM .env]
ANTHROPIC_API_KEY=[GET FROM console.anthropic.com]
MPESA_CONSUMER_KEY=[GET FROM developer.safaricom.co.ke]
MPESA_CONSUMER_SECRET=[GET FROM developer.safaricom.co.ke]
MPESA_CALLBACK_URL=https://biasharaiq.onrender.com/payments/callback
MPESA_ENVIRONMENT=sandbox
CORS_ORIGINS=https://biashara-iq.vercel.app,https://biasharaiq.onrender.com
LOG_LEVEL=INFO
```

- [ ] Copy all env vars from .env
- [ ] Click "Create Web Service"
- [ ] Wait for deployment (2-5 min)

### Verify Backend
- [ ] Check deployment completed (green checkmark)
- [ ] Visit https://biasharaiq.onrender.com/health
- [ ] Response shows: `{"status": "healthy", "database": "connected"}`

---

## Database Setup (Render PostgreSQL) - 5 min

### Create Database
- [ ] In Render dashboard, click "New +" → "PostgreSQL"
- [ ] Name: `biasharaiq-db`
- [ ] Region: Frankfurt
- [ ] Plan: Free
- [ ] Click "Create"

### Link to Backend
- [ ] Render automatically injects `DATABASE_URL`
- [ ] Redeploy backend (click button)

### Initialize Schema
```bash
# After backend is deployed, run:
cd backend
psql "postgresql://..." -f schema.sql
python seed_demo.py  # Optional: load demo data
```

- [ ] Database schema created
- [ ] (Optional) Demo data loaded

---

## Frontend Deployment (Vercel) - 5 min

### Create Project
- [ ] Login to https://vercel.com
- [ ] Click "Add New..." → "Project"
- [ ] Import from Git → Select your GitHub repo

### Configure
- [ ] Framework: Next.js
- [ ] Root Directory: `./frontend`
- [ ] Build: `npm run build`
- [ ] Output: `.next`

### Environment Variables
```
NEXT_PUBLIC_API_URL=https://biasharaiq.onrender.com
NEXT_PUBLIC_APP_NAME=BiasharaIQ
NODE_ENV=production
```

- [ ] Add env vars
- [ ] Click "Deploy"
- [ ] Wait for deployment (1-3 min)

### Verify Frontend
- [ ] Click deployment URL
- [ ] [ ] Dashboard loads without errors
- [ ] [ ] Navigation works
- [ ] [ ] Check browser console (no CORS errors)
- [ ] [ ] Network tab shows API calls to backend

---

## Update CORS Origins - 2 min

Once you have final URLs:

- [ ] Get Vercel frontend URL (e.g., `https://biashara-iq.vercel.app`)
- [ ] In Render backend settings, update `CORS_ORIGINS` env var
- [ ] Format: `https://domain1.com,https://domain2.com`
- [ ] Redeploy backend

---

## M-Pesa Integration - 10 min

### Sandbox Setup (Testing)
- [ ] Create account at https://developer.safaricom.co.ke/
- [ ] Create new app under "Sandbox"
- [ ] Copy `Client ID` → `MPESA_CONSUMER_KEY`
- [ ] Copy `Client Secret` → `MPESA_CONSUMER_SECRET`
- [ ] Add to Render env vars
- [ ] Redeploy backend

### Test Payment
```bash
curl -X POST https://biasharaiq.onrender.com/payments/initiate \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "254712345678",
    "amount": 100
  }'
```

- [ ] Response contains `checkout_id`
- [ ] No errors in Render logs

### Production Setup (LATER - when ready)
- [ ] Complete Safaricom verification
- [ ] Request production credentials
- [ ] Update `MPESA_CONSUMER_KEY` and `MPESA_CONSUMER_SECRET`
- [ ] Set `MPESA_ENVIRONMENT=production`
- [ ] Thoroughly test before going live

---

## Final Verification - 5 min

### Health Checks
```bash
# Backend health
curl https://biasharaiq.onrender.com/health

# Frontend (browser)
https://biashara-iq.vercel.app

# Database (from backend logs)
Check for "Database initialized successfully"

# API Docs (for testing)
https://biasharaiq.onrender.com/docs
```

- [ ] Backend returns healthy status
- [ ] Frontend loads
- [ ] All navigation works
- [ ] No console errors

### Test Key Features
- [ ] Can access login page
- [ ] Can register (if enabled)
- [ ] Can view dashboard
- [ ] API calls work (Network tab)
- [ ] Payment initiation works (if testing M-Pesa)

---

## Monitoring Setup - 5 min

- [ ] Set up Render alerts (optional):
  - Go to Service → Settings → Alerts
  - Add notification email
  
- [ ] Monitor logs regularly:
  - Render: Services → Logs
  - Vercel: Deployments → Logs

---

## Troubleshooting Quick Links

| Issue | Link |
|-------|------|
| Backend won't deploy | Check Render logs |
| Frontend CORS errors | Verify `NEXT_PUBLIC_API_URL` |
| Database connection failed | Check `DATABASE_URL` env var |
| M-Pesa sandbox fails | Verify credentials at Daraja |

---

## Post-Deployment

### Day 1
- [ ] Monitor for errors
- [ ] Test all major user flows
- [ ] Check database is backing up

### Week 1
- [ ] Review logs for any issues
- [ ] Test mobile responsiveness
- [ ] Get user feedback

### Before Going Live with Payments
- [ ] Get M-Pesa production credentials
- [ ] Test full payment flow end-to-end
- [ ] Set up error monitoring/alerts
- [ ] Create incident response plan

---

**Last Updated**: May 2026  
**Estimated Total Time**: ~45 minutes  
**Status**: Ready to Deploy ✅
