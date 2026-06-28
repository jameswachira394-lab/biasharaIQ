# BiasharaIQ – Financial Intelligence Platform

A financial intelligence + decision system for real-world small businesses in Kenya.

---



## 🏛️ System Architectures

BiasharaIQ follows a modern decoupled architecture separating the client-side presentation layer from the API-driven backend and databases.
It is auto-deployed into AWS ECS using Terraform.

### Logical Architecture

1.  **Frontend (Next.js + React + Tailwind CSS)**
    *   Handles the user interface, routing, and client-side state.
    *   Communicates with the backend via RESTful APIs.
    *   Deployed as a static or server-rendered application.
    *   *Mobile App*: Wrapped via Capacitor to build the Android application.

2.  **Backend (Python + FastAPI)**
    *   Serves as the core logic handler, authenticating users and managing transactions.
    *   Interfaces with the database using SQLAlchemy ORM.
    *   Integrates with external services like Anthropic's Claude AI for financial insights and M-Pesa for payment integrations.

3.  **Database (PostgreSQL)**
    *   Relational database storing user profiles, transaction records, and cached AI insights.
    *   Ensures data integrity and handles complex queries for reporting.

### Directory Structure

```text
biasharaiq/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── schema.sql              # PostgreSQL schema
│   ├── seed_demo.py            # Demo data (90 days)
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment template
│   ├── middleware/auth.py      # JWT authentication
│   ├── models/                 # SQLAlchemy ORM models & DB connection
│   ├── routes/                 # API Endpoints (Auth, Transactions, etc.)
│   └── services/               # Core Logic (Financial Engine, AI Agent, M-Pesa)
├── frontend/
│   └── src/
│       ├── app/                # Next.js pages
│       ├── components/         # Reusable UI components
│       ├── hooks/              # Data fetching hooks
│       ├── utils/              # API client, formatting
│       └── context/            # Auth state
├── android/                    # Capacitor Android App build context
├── biasharaiq-debug.apk        # Compiled Android APK
├── setup_mpesa.py              # M-Pesa integration setup
└── render.yaml                 # Render infrastructure-as-code deployments
```

## 🛠️ Tech Stacks
- **Frontend**: Next.js 14, React 18, Tailwind CSS, Recharts, Capacitor (for Android)
- **Backend**: Python FastAPI
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Auth**: JWT (bcrypt password hashing)
- **AI**: Anthropic Claude API (claude-sonnet-4)
- **Payments**: M-Pesa API integration

---

## 🏭 Production Deployment

BiasharaIQ is deployed using a distributed modern cloud infrastructure, leveraging Vercel, Render, and AWS for high availability and scalability.

### Deployment Architecture

*   **Frontend 🌍 (Vercel)**
    *   The Next.js frontend is deployed to **Vercel** for optimal edge-caching and fast content delivery.
    *   Connects to the backend via the `NEXT_PUBLIC_API_URL` environment variable.
*   **Backend ⚙️ (Render)**
    *   The FastAPI Python application runs as a Web Service on **Render**.
    *   Configured to scale horizontally, running behind Render's load balancer.
    *   Handles M-Pesa callbacks and API requests from the Vercel frontend and mobile app.
*   **Database 🗄️ (AWS RDS)**
    *   The PostgreSQL database is hosted on **Amazon Web Services (AWS) RDS**.
    *   Configured for automated backups, multi-AZ deployment (optional for production), and high performance.
    *   The backend on Render connects to the AWS RDS instance securely.

### One-Command Docker Deployment (Local / Self-hosted)

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
- Decoupled cloud infrastructure (Vercel + Render + AWS RDS)
- Docker Compose for multi-container orchestration
- Kubernetes manifests available
- Load balancer ready
- Configurable pool sizes

### Deployment Guides

- **Docker Compose** (Self-hosted): [PRODUCTION_DEPLOYMENT.md](docs/PRODUCTION_DEPLOYMENT.md#option-a-docker-compose-self-hosted)
- **Kubernetes**: [PRODUCTION_DEPLOYMENT.md](docs/PRODUCTION_DEPLOYMENT.md#option-b-kubernetes)
- **Render.com** (Free Tier): [render.yaml](render.yaml)
- **AWS via Terraform**: The system is deployed through the internal developer platform into AWS ECS using the Terraform CLI.
- **Vercel / Render / AWS Architecture**: Refer to the architectural configuration above.

### Mobile App Build (Capacitor)

To build the Android APK using Capacitor, run the provided scripts from the project root:

```bash
# Windows
.\build-mobile.ps1

# Linux / macOS
./build-mobile.sh
```

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
