# BiasharaIQ - Production Integration & Deployment Guide

## Overview

This guide covers deploying BiasharaIQ to production with security, scalability, and reliability in mind.

---

## Pre-Deployment Checklist

- [ ] All environment variables configured
- [ ] Database backups tested
- [ ] SSL certificates obtained
- [ ] API keys generated and secured
- [ ] Database connection pooling configured
- [ ] CORS origins whitelisted (no wildcards)
- [ ] Logging configured
- [ ] Error tracking set up (Sentry)
- [ ] Health checks verified
- [ ] Load balancer configured (if needed)

---

## Environment Setup

### 1. Generate Secure Keys

```bash
# Linux/Mac
openssl rand -hex 32

# Windows PowerShell
[convert]::ToHexString((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

### 2. Create Production Environment File

Copy `.env.example` to `.env` and set production values:

```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@db-host/biasharaiq
SECRET_KEY=<generated-32-char-hex>
JWT_SECRET=<generated-32-char-hex>
ANTHROPIC_API_KEY=sk-ant-...
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
LOG_LEVEL=INFO
```

⚠️ **Never commit .env files to version control**

---

## Deployment Options

### Option A: Docker Compose (Self-Hosted)

#### Prerequisites
- Docker & Docker Compose installed
- PostgreSQL 16+ or let Docker manage it
- SSL certificates

#### Steps

1. **Clone repository**
   ```bash
   git clone https://github.com/yourusername/biasharaiq.git
   cd biasharaiq
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

3. **Create production directories**
   ```bash
   mkdir -p logs backups
   sudo chown -R 1000:1000 logs backups pgdata
   ```

4. **Start services**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

5. **Verify deployment**
   ```bash
   # Check status
   docker-compose -f docker-compose.prod.yml ps
   
   # View logs
   docker-compose -f docker-compose.prod.yml logs -f backend
   
   # Health check
   curl http://localhost:8000/health
   ```

6. **Database migration** (if needed)
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend \
     python -c "from models.database import engine; from models.models import Base; Base.metadata.create_all(bind=engine)"
   ```

---

### Option B: Kubernetes

#### Prerequisites
- Kubernetes cluster (EKS, GKE, AKS, etc.)
- kubectl configured
- Container registry (ECR, GCR, etc.)

#### Quick Setup

1. **Build and push images**
   ```bash
   docker build -f backend/Dockerfile.prod -t yourregistry/biasharaiq-api:latest backend/
   docker build -f frontend/Dockerfile -t yourregistry/biasharaiq-web:latest frontend/
   docker push yourregistry/biasharaiq-api:latest
   docker push yourregistry/biasharaiq-web:latest
   ```

2. **Create Kubernetes manifests** (save as `k8s/deployment.yaml`)
   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: biasharaiq-config
   data:
     ENVIRONMENT: "production"
     LOG_LEVEL: "INFO"
   ---
   apiVersion: v1
   kind: Secret
   metadata:
     name: biasharaiq-secrets
   type: Opaque
   stringData:
     DATABASE_URL: "postgresql://user:password@postgres:5432/biasharaiq"
     SECRET_KEY: "your-generated-key"
     JWT_SECRET: "your-jwt-secret"
     ANTHROPIC_API_KEY: "sk-ant-..."
     CORS_ORIGINS: "https://yourdomain.com"
   ---
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: biasharaiq-api
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: biasharaiq-api
     template:
       metadata:
         labels:
           app: biasharaiq-api
       spec:
         containers:
         - name: api
           image: yourregistry/biasharaiq-api:latest
           ports:
           - containerPort: 8000
           envFrom:
           - configMapRef:
               name: biasharaiq-config
           - secretRef:
               name: biasharaiq-secrets
           livenessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 30
             periodSeconds: 10
           readinessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 10
             periodSeconds: 5
           resources:
             requests:
               memory: "256Mi"
               cpu: "250m"
             limits:
               memory: "512Mi"
               cpu: "500m"
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: biasharaiq-api-service
   spec:
     type: LoadBalancer
     selector:
       app: biasharaiq-api
     ports:
     - protocol: TCP
       port: 80
       targetPort: 8000
   ```

3. **Deploy**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   ```

---

### Option C: Render.com (Recommended for Free Tier)

Already configured in `render.yaml`. Follow the Deployment.md file for details.

---

### Option D: AWS (EC2 + RDS)

#### Backend on EC2

1. **Launch EC2 instance**
   - Ubuntu 22.04 LTS
   - t3.small or larger
   - Security group: Allow 8000 from ALB

2. **Install dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3.11 python3.11-venv git curl
   ```

3. **Deploy app**
   ```bash
   cd /opt
   git clone https://github.com/yourusername/biasharaiq.git
   cd biasharaiq/backend
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with production values
   ```

4. **Use Systemd for auto-start**
   ```bash
   sudo tee /etc/systemd/system/biasharaiq.service << EOF
   [Unit]
   Description=BiasharaIQ API
   After=network.target
   
   [Service]
   Type=notify
   User=biasharaiq
   WorkingDirectory=/opt/biasharaiq/backend
   Environment="PATH=/opt/biasharaiq/backend/venv/bin"
   ExecStart=/opt/biasharaiq/backend/venv/bin/gunicorn main:app --workers=4 --worker-class=uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   EOF
   
   sudo systemctl enable biasharaiq
   sudo systemctl start biasharaiq
   ```

#### Database on RDS

1. **Create RDS instance**
   - Engine: PostgreSQL 16
   - Instance class: db.t3.micro or larger
   - Multi-AZ for production
   - Enable automated backups

2. **Initialize database**
   ```bash
   psql "postgresql://user:password@endpoint:5432/biasharaiq" < backend/schema.sql
   ```

---

## Post-Deployment

### 1. Verify Health

```bash
# API health
curl https://api.yourdomain.com/health

# Database check
curl https://api.yourdomain.com/health | jq '.database'
```

### 2. Set Up Monitoring

- **Logs**: Docker logs, CloudWatch, or ELK stack
- **Errors**: Sentry (already configured)
- **Metrics**: Prometheus + Grafana

### 3. Backup Strategy

```bash
# Daily database backup
0 2 * * * pg_dump "postgresql://..." | gzip > /backups/biasharaiq-$(date +\%Y\%m\%d).sql.gz
```

### 4. SSL/HTTPS

```bash
# Using Certbot with Let's Encrypt
sudo certbot certonly --standalone -d api.yourdomain.com
```

Configure reverse proxy (nginx/Traefik) to handle SSL termination.

---

## Production Checklist - Final

- [ ] CORS configured without wildcards
- [ ] Database connections pooled
- [ ] Logging enabled and monitored
- [ ] Error tracking active (Sentry)
- [ ] SSL certificates valid
- [ ] Backups automated
- [ ] Health checks passing
- [ ] Load balancer/reverse proxy working
- [ ] API rate limiting configured (if needed)
- [ ] Secrets not in version control
- [ ] Documentation updated
- [ ] Monitoring alerts configured

---

## Troubleshooting

### API won't start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Verify env vars
docker-compose -f docker-compose.prod.yml exec backend env | grep -i database
```

### Database connection failed
```bash
# Test connection
psql "postgresql://user:password@host/biasharaiq" -c "SELECT 1;"

# Check pool settings
echo "Current connections: SELECT count(*) FROM pg_stat_activity;"
```

### CORS errors
```bash
# Verify CORS origins in .env
docker-compose -f docker-compose.prod.yml exec backend printenv | grep CORS
```

---

## Support & Resources

- GitHub Issues: https://github.com/yourusername/biasharaiq/issues
- FastAPI Docs: https://fastapi.tiangolo.com
- Next.js Deployment: https://nextjs.org/docs/deployment
- PostgreSQL Docs: https://www.postgresql.org/docs

---

**Last Updated**: April 2024
**Version**: 1.0.0
