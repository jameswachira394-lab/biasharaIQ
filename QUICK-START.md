# 🚀 Quick Start: Production Deployment

## 30-Second Overview

Your app is configured to deploy on:
- **Frontend**: Vercel
- **Backend**: Render  
- **Database**: Render PostgreSQL

All you need to do is connect GitHub and set a few environment variables.

---

## ⚡ 5-Minute Setup

### Step 1: Verify Configuration (1 min)
```powershell
.\verify-deployment.ps1 -Verbose
```
✅ All checks should pass

### Step 2: Push to GitHub (1 min)
```bash
git add .
git commit -m "Configure production deployment"
git push
```

### Step 3: Deploy Backend on Render (2 min)

1. Go to https://render.com → Dashboard
2. New → Web Service
3. Connect GitHub repository
4. In build settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app --workers=4 --worker-class=uvicorn.workers.UvicornWorker --bind=0.0.0.0:$PORT`
5. In environment variables:
   - `ANTHROPIC_API_KEY`: *(your key)*
   - `GEMINI_API_KEY`: *(your key)*
   - Other vars auto-set from `render.yaml`
6. Click Deploy
7. Wait ~3-5 minutes for deployment

### Step 4: Deploy Frontend on Vercel (1 min)

1. Go to https://vercel.com → Dashboard
2. New Project → Import GitHub repo
3. Environment Variables:
   - `NEXT_PUBLIC_API_URL`: `https://biasharaiq.onrender.com`
   - `NEXT_PUBLIC_APP_NAME`: `BiasharaIQ`
4. Deploy
5. Wait ~1-2 minutes

### Step 5: Test Everything (Ongoing)

```bash
# Backend health check
curl https://biasharaiq.onrender.com/health

# Frontend access
open https://biashara-f43hbl3il-veritys-projects-965ff306.vercel.app

# Test login flow in browser
```

---

## 📋 What's Configured

### Backend (`render.yaml`)
- ✅ Python 3.11 environment
- ✅ PostgreSQL database
- ✅ Gunicorn server (4 workers)
- ✅ CORS restricted to Vercel URL
- ✅ Security headers enabled
- ✅ Health check endpoint
- ✅ Logging configured
- ✅ Database pooling optimized

### Frontend (`vercel.json` + `frontend/.env.production`)
- ✅ Next.js build optimized
- ✅ API URL set to Render backend
- ✅ Environment variables set
- ✅ Build caching enabled
- ✅ Edge regions configured

### Security
- ✅ HTTPS enforced
- ✅ CORS origins restricted (no `*`)
- ✅ API keys in environment (not committed)
- ✅ JWT tokens with 7-day expiration
- ✅ Security headers on all responses
- ✅ Database credentials secured

---

## 🔗 Your URLs

| Service | URL |
|---------|-----|
| Frontend | https://biashara-f43hbl3il-veritys-projects-965ff306.vercel.app |
| Backend API | https://biasharaiq.onrender.com |
| API Docs | https://biasharaiq.onrender.com/docs *(dev only)* |
| Health Check | https://biasharaiq.onrender.com/health |

---

## ❌ If Something Goes Wrong

### Frontend won't connect to backend
1. Check `NEXT_PUBLIC_API_URL` in Vercel dashboard
2. Verify backend health: `curl https://biasharaiq.onrender.com/health`
3. Check browser DevTools → Network tab for CORS errors

### Backend won't start
1. Check Render deployment logs
2. Verify PostgreSQL database is running
3. Check environment variables are set

### Database connection fails
1. Verify `DATABASE_URL` in Render dashboard
2. Check database exists: `biasharaiq-db`
3. Check credentials in PostgreSQL

---

## 📊 Monitoring

**Render Dashboard**
- View logs: https://dashboard.render.com
- Check uptime and resource usage
- Monitor database connections

**Vercel Dashboard**
- View deployment logs: https://vercel.com/dashboard
- Check edge function performance
- Monitor error reporting

**Health Endpoint**
```bash
# Check backend health anytime
curl https://biasharaiq.onrender.com/health

# Should return:
# {
#   "status": "healthy",
#   "timestamp": "2026-05-04T12:00:00.000000",
#   "environment": "production",
#   "database": "connected"
# }
```

---

## 🎯 Next Phase

Once deployed and tested:

1. **Monitor Performance**
   - Check response times
   - Monitor database connections
   - Review error logs

2. **Scale if Needed**
   - Render: Upgrade plan for more resources
   - Vercel: Already using global CDN

3. **Add Monitoring**
   - Set up alerts on Render/Vercel
   - Monitor key metrics
   - Set error thresholds

4. **Continuous Deployment**
   - Every `git push` auto-deploys
   - No manual steps needed
   - Rollback: Use deployment history

---

## 📝 Files You Modified

- ✅ `backend/core/config.py` - Environment variables
- ✅ `render.yaml` - Production configuration
- ✅ `frontend/vercel.json` - Vercel settings
- ✅ `frontend/next.config.js` - API rewrites
- ✅ `.env` - Production environment

See `DEPLOYMENT.md` for full details.

---

**Status**: Ready for production deployment ✅
