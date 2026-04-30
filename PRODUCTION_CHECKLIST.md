# Production Setup Checklist

## Pre-Deployment (Complete before going live)

### Infrastructure
- [ ] Decide on hosting platform (Docker Compose, Kubernetes, AWS, Render, etc.)
- [ ] Provision server/cluster resources
- [ ] Set up networking and security groups
- [ ] Obtain SSL/TLS certificates
- [ ] Configure reverse proxy (nginx/Traefik)

### Secrets & Configuration
- [ ] Generate SECRET_KEY: `openssl rand -hex 32`
- [ ] Generate JWT_SECRET: `openssl rand -hex 32`
- [ ] Obtain ANTHROPIC_API_KEY
- [ ] Obtain GEMINI_API_KEY (if needed)
- [ ] Create production .env file (never commit!)
- [ ] Verify CORS_ORIGINS whitelist (no wildcards)

### Database
- [ ] Set up PostgreSQL 16+ (or managed service like RDS, Aurora)
- [ ] Configure automated backups
- [ ] Test backup/restore procedure
- [ ] Set up replication (if high-availability needed)
- [ ] Initialize schema: `psql $DATABASE_URL < backend/schema.sql`

### Monitoring & Logging
- [ ] Set up log aggregation (CloudWatch, ELK, Datadog, etc.)
- [ ] Configure Sentry for error tracking
- [ ] Set up performance monitoring (New Relic, DataDog, etc.)
- [ ] Create alert rules for failures
- [ ] Set up health check monitoring

### Security
- [ ] Enable HTTPS only
- [ ] Configure rate limiting
- [ ] Set up WAF (if applicable)
- [ ] Review and harden security group rules
- [ ] Enable database encryption
- [ ] Set up secrets management (Vault, AWS Secrets Manager)
- [ ] Run security audit

### Performance
- [ ] Configure database connection pooling
- [ ] Set up CDN for static assets
- [ ] Enable caching headers
- [ ] Configure load balancer
- [ ] Performance test under expected load

### Deployment
- [ ] Set up CI/CD pipeline (GitHub Actions, GitLab CI, etc.)
- [ ] Test deployment process in staging
- [ ] Document rollback procedure
- [ ] Create deployment runbook

---

## Deployment Day

### Pre-Deployment
- [ ] Create database backup
- [ ] Verify all environment variables are set
- [ ] Run health checks: `./health_check.sh`
- [ ] Test database connectivity
- [ ] Test API endpoints manually
- [ ] Verify SSL certificates

### During Deployment
- [ ] Deploy backend: `docker-compose -f docker-compose.prod.yml up -d backend`
- [ ] Deploy frontend: `docker-compose -f docker-compose.prod.yml up -d frontend`
- [ ] Monitor logs for errors
- [ ] Run smoke tests
- [ ] Verify monitoring dashboards

### Post-Deployment
- [ ] [ ] Verify all services are healthy
- [ ] Run health check script
- [ ] Test API endpoints: `/health`, `/docs`
- [ ] Check monitoring dashboards
- [ ] Verify database connectivity
- [ ] Test authentication flow
- [ ] Review error logs

---

## Post-Deployment

### Day 1
- [ ] Monitor error tracking dashboard
- [ ] Monitor performance metrics
- [ ] Check database connection pool usage
- [ ] Verify scheduled backups are running
- [ ] Test SMS/email notifications (if applicable)

### Week 1
- [ ] Review performance trends
- [ ] Optimize slow queries if needed
- [ ] Fine-tune connection pool settings
- [ ] Collect user feedback
- [ ] Document any issues encountered

### Ongoing
- [ ] Daily: Check error tracking and logs
- [ ] Weekly: Review performance metrics
- [ ] Monthly: Analyze database growth
- [ ] Monthly: Test backup/restore
- [ ] Quarterly: Security review
- [ ] Quarterly: Database maintenance

---

## Rollback Procedure

If issues occur and you need to rollback:

```bash
# Stop current deployment
docker-compose -f docker-compose.prod.yml down

# Restore database backup
psql $DATABASE_URL < /backups/biasharaiq-YYYYMMDD.sql.gz

# Deploy previous version
docker-compose -f docker-compose.prod.yml up -d

# Verify
./health_check.sh $PRODUCTION_URL
```

---

## Environment Variables Reference

```bash
# Copy to .env and fill in production values

# Environment
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:password@host/biasharaiq
DB_POOL_SIZE=25
DB_MAX_OVERFLOW=15

# Security
SECRET_KEY=<32-char-hex>
JWT_SECRET=<32-char-hex>

# API Keys
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...

# CORS
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Logging
LOG_LEVEL=INFO

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Optional: Sentry
SENTRY_DSN=https://...@sentry.io/...
```

---

## Key Production URLs

After deployment, verify these URLs work:

- Frontend: `https://yourdomain.com`
- API Root: `https://api.yourdomain.com`
- Health Check: `https://api.yourdomain.com/health`
- API Docs: `https://api.yourdomain.com/docs` (disable in production if desired)
- Auth Login: `POST https://api.yourdomain.com/auth/login`

---

## Support & Troubleshooting

See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md#troubleshooting) for detailed troubleshooting.

For issues:
1. Check health endpoint: `curl https://api.yourdomain.com/health`
2. Review error logs: `docker-compose logs -f backend`
3. Check database: `psql $DATABASE_URL -c "SELECT 1;"`
4. Check Sentry: https://sentry.io (for error tracking)

---

**Last Updated**: April 2024  
**Version**: 1.0.0
