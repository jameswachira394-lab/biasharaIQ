# BiasharaIQ – Financial Intelligence Platform

A financial intelligence + decision system for real-world small businesses in Kenya.

---


## Architecture

```
biasharaiq/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── schema.sql              # PostgreSQL schema
│   ├── seed_demo.py            # Demo data (90 days)
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment template
│   ├── middleware/auth.py      # JWT authentication
│   ├── models/
│   │   ├── models.py           # SQLAlchemy ORM models
│   │   └── database.py         # DB connection
│   ├── routes/
│   │   ├── auth.py             # Register / Login
│   │   ├── transactions.py     # CRUD transactions
│   │   └── routes.py           # Dashboard, AI, Reports, etc.
│   └── services/
│       ├── financial_engine.py # Profit, cash flow, metrics
│       ├── insights_engine.py  # Rule-based insights
│       └── ai_agent.py         # Claude AI integration
└── frontend/
    └── src/
        ├── app/                # Next.js pages
        │   ├── dashboard/      # Main dashboard
        │   ├── transactions/   # CRUD transactions
        │   ├── insights/       # Financial insights
        │   ├── ai/             # AI chat advisor
        │   ├── reports/        # Charts & reports
        │   └── settings/       # Profile & categories
        ├── components/         # Reusable UI components
        ├── hooks/              # Data fetching hooks
        ├── utils/              # API client, formatting
        └── context/            # Auth state
```

## Tech Stack
- **Frontend**: Next.js 14, React 18, Tailwind CSS, Recharts
- **Backend**: Python FastAPI
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Auth**: JWT (bcrypt password hashing)
- **AI**: Anthropic Claude API (claude-sonnet-4)

---

## 🏭 Production Deployment

### One-Command Docker Deployment

```bash
# Copy environment file and update with production secrets
cp .env.example .env
# Edit .env with your production values

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
curl http://localhost:8000/health

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Production Features Included

✅ **Security**
- CORS whitelist (no wildcards in production)
- Security headers (X-Frame-Options, HSTS, etc.)
- Non-root Docker user
- JWT authentication

✅ **Performance**
- Database connection pooling (configurable)
- Gunicorn + Uvicorn workers
- Optimized Docker images
- Response time monitoring

✅ **Reliability**
- Health checks with database verification
- Automatic restart policies
- Request/response logging
- Error tracking integration (Sentry)
- Database backup strategy

✅ **Scalability**
- Docker Compose for multi-container orchestration
- Kubernetes manifests available
- Load balancer ready
- Configurable pool sizes

### Deployment Guides

- **Docker Compose** (Self-hosted): [PRODUCTION_DEPLOYMENT.md](docs/PRODUCTION_DEPLOYMENT.md#option-a-docker-compose-self-hosted)
- **Kubernetes**: [PRODUCTION_DEPLOYMENT.md](docs/PRODUCTION_DEPLOYMENT.md#option-b-kubernetes)
- **Render.com** (Free Tier): [render.yaml](render.yaml)
- **AWS EC2 + RDS**: [PRODUCTION_DEPLOYMENT.md](docs/PRODUCTION_DEPLOYMENT.md#option-d-aws-ec2--rds)

### Pre-Deployment Checklist

```bash
# Run health checks
./health_check.sh http://localhost:8000  # Linux/Mac
.\health_check.ps1 -EnvironmentUrl "http://localhost:8000"  # Windows
```

See [PRODUCTION_DEPLOYMENT.md](docs/PRODUCTION_DEPLOYMENT.md) for complete deployment guide.

---

## 🛠 Development

### Environment Variables

All environment variables are documented in `.env.example`. Create a `.env` file:

```bash
cp .env.example .env
# Edit with your values
```

### API Documentation

Once running, visit: http://localhost:8000/docs

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests  
cd frontend
npm test
```

---

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Production Deployment](docs/PRODUCTION_DEPLOYMENT.md)
- [Development Deployment](docs/DEPLOYMENT.md)

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit a pull request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙋 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/biasharaiq/issues)
- Documentation: [docs/](docs/)

---

**Version**: 1.0.0  
**Last Updated**: April 2024
