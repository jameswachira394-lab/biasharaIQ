# BiasharaIQ Deployment Guide

## Option A – Docker (Recommended for self-hosting)

```bash
# 1. Clone the repo
git clone https://github.com/yourname/biasharaiq.git && cd biasharaiq

# 2. Create a .env file in the project root
cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
ANTHROPIC_API_KEY=sk-ant-...
EOF

# 3. Start all services
docker compose up -d

# 4. Visit http://localhost:3000
```

---

## Option B – Vercel + Render (Cloud, Free Tier)

### Backend → Render.com

1. Push the repo to GitHub
2. Go to https://render.com → New → Web Service
3. Connect your repo, set **Root Directory** to `backend`
4. Set runtime: **Python 3.11**
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Add environment variables:
   - `SECRET_KEY` = (generate with `openssl rand -hex 32`)
   - `ANTHROPIC_API_KEY` = your key
   - `DATABASE_URL` = (from Render PostgreSQL database)
   - `CORS_ORIGINS` = `https://your-app.vercel.app`
8. Also create a **Render PostgreSQL** database and link it

### After backend is live, run DB migrations:
```bash
# Via Render shell or locally with DATABASE_URL set:
psql $DATABASE_URL < backend/schema.sql
```

### Frontend → Vercel

1. Go to https://vercel.com → New Project
2. Import your GitHub repo
3. Set **Root Directory** to `frontend`
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://your-backend.onrender.com`
5. Deploy

---

## Option C – Manual VPS (Ubuntu 22+)

### Install dependencies
```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv nodejs npm postgresql
sudo npm install -g pm2
```

### Backend
```bash
cd /var/www/biasharaiq/backend
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env  # fill in values

# Create DB
sudo -u postgres createdb biasharaiq
psql -U postgres biasharaiq < schema.sql

# Start with PM2
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name biasharaiq-api
pm2 save
```

### Frontend
```bash
cd /var/www/biasharaiq/frontend
cp .env.example .env.local && nano .env.local
npm install && npm run build
pm2 start "npm run start -- --port 3000" --name biasharaiq-web
pm2 save
```

### Nginx reverse proxy (optional)
```nginx
server {
    server_name biasharaiq.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
    }
}
```

---

## Seed Demo Data

After deployment, optionally seed demo data:
```bash
cd backend
python seed_demo.py
# Login: demo@biasharaiq.com / demo1234
```

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `SECRET_KEY` | ✅ | JWT signing secret (32+ chars) |
| `ANTHROPIC_API_KEY` | ✅ | Enables AI Advisor feature |
| `CORS_ORIGINS` | ✅ | Comma-separated allowed origins |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | Default: 10080 (7 days) |
