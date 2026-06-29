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
│   ├── core/                   # Core configuration and DB setup
│   ├── middleware/             # Middleware (JWT, CORS, etc.)
│   ├── models/                 # SQLAlchemy ORM models
│   ├── routes/                 # API Endpoints
│   ├── services/               # Core logic (Financial Engine, AI, M-Pesa)
│   ├── migrate_to_aws.py       # AWS RDS migration scripts
│   ├── Dockerfile / .prod      # Docker build configurations
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/                    # Next.js app source
│   ├── android/                # Capacitor Android App build context
│   ├── Dockerfile              # Docker build configuration
│   └── vercel.json             # Vercel deployment config
├── terraform/                  # Terraform IaC for AWS ECS/RDS
├── docker-compose.yml          # Local multi-container orchestration
├── biasharaiq-debug.apk        # Compiled Android APK
├── render.yaml                 # Render configuration
├── setup_mpesa.py              # M-Pesa integration setup
├── validate_mpesa.py           # M-Pesa validation testing
├── build-mobile.*              # Mobile build scripts (sh/ps1)
├── health_check.*              # Health check scripts (sh/ps1)
├── setup-dev.*                 # Dev setup scripts (sh/ps1)
└── verify-deployment.*         # Deployment verification (sh/ps1)
```

## 🛠️ Tech Stacks
- **Frontend**: Next.js 14, React 18, Tailwind CSS, Recharts, Capacitor (for Android)
- **Backend**: Python FastAPI
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Auth**: JWT (bcrypt password hashing)
- **AI**: Anthropic Claude API (claude-sonnet-4)
- **Payments**: M-Pesa API integration
- **Infrastructure**: AWS (ECR/ECS/RDS), Terraform, Docker Compose
- **Scripting**: Bash and PowerShell utilities for cross-platform support

---

## 🏭 Production Deployment

BiasharaIQ is deployed using a modern cloud infrastructure, leveraging Amazon Web Services (AWS) for high availability, security, and scalability.

### Deployment Architecture

*   **Frontend 🌍 (AWS ECR / ECS)**
    *   The Next.js frontend is containerized and its image is stored in **AWS ECR (Elastic Container Registry)**.
    *   It is deployed and orchestrated via **AWS ECS (Elastic Container Service)**.
    *   Connects to the backend securely within the AWS environment or via a load balancer.
*   **Backend ⚙️ (AWS ECR / ECS)**
    *   The FastAPI Python application is containerized and pushed to **AWS ECR**.
    *   Runs as a scalable web service on **AWS ECS**, typically using AWS Fargate for serverless compute.
    *   Handles M-Pesa callbacks and API requests from the frontend and mobile app.
*   **Database 🗄️ (AWS RDS)**
    *   The PostgreSQL database is hosted on **AWS RDS (Relational Database Service)**.
    *   Configured for automated backups, multi-AZ deployment (optional for production), and high performance.
    *   The backend securely connects to the RDS instance within the AWS Virtual Private Cloud (VPC).



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
- Decoupled cloud infrastructure (AWS ECR/ECS + RDS)
- Docker Compose for multi-container orchestration
- Kubernetes manifests available
- Load balancer ready
- Configurable pool sizes

*(Deployment documentation is being integrated into Terraform states and setup scripts)*

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

*(Note: Extended documentation is currently being ported)*
- API documentation is available locally via Swagger UI (`http://localhost:8000/docs`).
- See scripts like `setup-dev.ps1` and `verify-deployment.sh` for infrastructure reference.

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
