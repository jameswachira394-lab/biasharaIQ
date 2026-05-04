# BiasharaIQ Deployment Guide

## Architecture Overview

- **Frontend**: Vercel (Next.js)
  - URL: https://biashara-f43hbl3il-veritys-projects-965ff306.vercel.app
  
- **Backend API**: Render (Python/FastAPI)
  - URL: https://biasharaiq.onrender.com
  - Database: PostgreSQL
  
- **Communication**: Frontend → Render API at `https://biasharaiq.onrender.com`

---

## Environment Configuration

### Frontend (Vercel) - `vercel.json`

```json
{
  "env": {
    "NEXT_PUBLIC_API_URL": "https://biasharaiq.onrender.com",
    "NODE_ENV": "production"
  }
}
```

### Backend (Render) - `render.yaml`

Key environment variables:
- `ENVIRONMENT`: `production`
- `CORS_ORIGINS`: `https://biashara-f43hbl3il-veritys-projects-965ff306.vercel.app,https://biasharaiq.onrender.com`
- `FRONTEND_URL`: `https://biashara-f43hbl3il-veritys-projects-965ff306.vercel.app`
- `SECRET_KEY`: Auto-generated (store securely)
- `DATABASE_URL`: Connected from Render PostgreSQL database

---

## Deployment Steps

### 1. Deploy Backend to Render

1. Push code to GitHub
2. Connect repository to Render
3. Select `render.yaml` as the build configuration
4. Render will automatically:
   - Install Python dependencies from `requirements.txt`
   - Build Docker image with `Dockerfile.prod`
   - Deploy on `https://biasharaiq.onrender.com`
   - Configure PostgreSQL database
   - Set environment variables

**Verify**:
```bash
curl https://biasharaiq.onrender.com/health
```

### 2. Deploy Frontend to Vercel

1. Push code to GitHub
2. Connect repository to Vercel
3. Configure environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL`: `https://biasharaiq.onrender.com`
   - `NEXT_PUBLIC_APP_NAME`: `BiasharaIQ`

4. Deploy frontend
5. Vercel automatically builds and deploys

**Verify**:
```bash
curl https://biashara-f43hbl3il-veritys-projects-965ff306.vercel.app
```

---

## CORS Configuration

### Backend (FastAPI)

The backend accepts requests from:
- `https://biashara-f43hbl3il-veritys-projects-965ff306.vercel.app` (Vercel frontend)
- `https://biasharaiq.onrender.com` (Backend itself, for testing)

Configured in `render.yaml`:
```yaml
CORS_ORIGINS: https://biashara-f43hbl3il-veritys-projects-965ff306.vercel.app,https://biasharaiq.onrender.com
```

### Frontend (Next.js)

Makes requests to: `https://biasharaiq.onrender.com`

Configured in:
- `vercel.json`: `NEXT_PUBLIC_API_URL`
- `frontend/.env`: `NEXT_PUBLIC_API_URL=https://biasharaiq.onrender.com`

---

## API Communication Flow

1. **Frontend** → Makes request to `/api/auth/login`
2. **Next.js Rewrite** → Routes to `https://biasharaiq.onrender.com/auth/login`
3. **Backend** → Validates CORS origin, processes request
4. **Backend** → Returns response to frontend
5. **Frontend** → Handles auth token in localStorage

---

## Health Check

Both services have health check endpoints:

**Backend**:
```bash
curl https://biasharaiq.onrender.com/health
# Response: { "status": "healthy", "database": "connected", ... }
```

**Frontend**:
```bash
curl https://biashara-f43hbl3il-veritys-projects-965ff306.vercel.app
# Returns Next.js homepage
```

---

## Database

- **Provider**: Render PostgreSQL (free tier)
- **Connection**: Automatically configured by Render from `DATABASE_URL`
- **Schema**: Applied on first deployment from `backend/schema.sql`

---

## Environment Files

### Production (.env)
```
ENVIRONMENT=production
CORS_ORIGINS=https://biashara-f43hbl3il-veritys-projects-965ff306.vercel.app,https://biasharaiq.onrender.com
FRONTEND_URL=https://biashara-f43hbl3il-veritys-projects-965ff306.vercel.app
LOG_LEVEL=INFO
```

### Development (.env.local - local only)
```
ENVIRONMENT=development
NEXT_PUBLIC_API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

## Troubleshooting

### CORS Errors

If frontend gets CORS error:
1. Check `CORS_ORIGINS` in `render.yaml`
2. Verify frontend URL is listed
3. Backend must be running
4. Check browser DevTools → Network tab

### API Not Responding

1. Check backend health: `curl https://biasharaiq.onrender.com/health`
2. Check Render dashboard for errors
3. Verify database connection: `render.yaml` → `DATABASE_URL`

### Frontend Not Connecting

1. Check `NEXT_PUBLIC_API_URL` in `vercel.json`
2. Verify backend URL is accessible
3. Check Vercel deployment logs
4. Clear browser cache: `Ctrl+Shift+Delete`

---

## Monitoring

- **Render Dashboard**: Monitor API uptime, logs, database
- **Vercel Dashboard**: Monitor frontend performance, deployments
- **Health Endpoint**: `/health` endpoint checks database connectivity

---

## Rollback Plan

1. Revert commit in GitHub
2. Render/Vercel auto-redeploy from latest commit
3. Manual rollback: Use Render/Vercel deployment history

---

## Security Checklist

- ✅ CORS configured to specific origins (not `*`)
- ✅ Security headers added (X-Frame-Options, Strict-Transport-Security, etc.)
- ✅ HTTPS enforced (Render/Vercel provide SSL)
- ✅ Environment variables for sensitive data (API keys, secrets)
- ✅ Non-root user in Docker (Dockerfile.prod)
- ✅ Production logging (INFO level, no debug info)
- ✅ Database connection pool optimized
- ✅ JWT token expiration (7 days)

---

## Performance Optimization

- **Frontend**: CDN via Vercel (edge caching)
- **Backend**: Gunicorn with 4 workers (Dockerfile.prod)
- **Database**: Connection pooling (25 connections max)
- **CORS**: Pre-flight request caching (max_age=3600)

