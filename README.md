# BiasharaIQ – Financial Intelligence Platform for Kenyan SMEs

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-000000.svg)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED.svg)](https://www.docker.com/)
[![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC.svg)](https://www.terraform.io/)
[![Kubernetes](https://img.shields.io/badge/Orchestration-Kubernetes-326CE5.svg)](https://kubernetes.io/)

**BiasharaIQ** is a comprehensive, production-grade financial intelligence platform tailored specifically for Kenyan Micro, Small, and Medium Enterprises (SMEs). It combines automated transaction tracking, AI-powered financial categorization and insights using Google Gemini, M-Pesa mobile money integration, document OCR parsing, multi-tier subscription controls, and cross-platform web and Android client access.

---

## 📋 Table of Contents

- [System Architecture](#-system-architecture)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Getting Started & Local Development](#-getting-started--local-development)
  - [Prerequisites](#prerequisites)
  - [Quickstart with Setup Scripts](#quickstart-with-setup-scripts)
  - [Manual Local Setup](#manual-local-setup)
  - [Docker Compose Local Environment](#docker-compose-local-environment)
- [Core Platform Modules](#-core-platform-modules)
  - [1. Backend & REST API](#1-backend--rest-api)
  - [2. Frontend Web Application](#2-frontend-web-application)
  - [3. Mobile Application (Android / Capacitor)](#3-mobile-application-android--capacitor)
  - [4. AI Engine & Insights Service](#4-ai-engine--insights-service)
  - [5. M-Pesa Payment Integration](#5-m-pesa-payment-integration)
  - [6. Document Parsing & Transaction Uploads](#6-document-parsing--transaction-uploads)
  - [7. Authentication & Subscription Guards](#7-authentication--subscription-guards)
- [Database Management & Migration](#-database-management--migration)
- [DevOps, Infrastructure & Deployment](#-devops-infrastructure--deployment)
  - [AWS Deployment via Terraform](#aws-deployment-via-terraform)
  - [Kubernetes & Helm Deployment](#kubernetes--helm-deployment)
  - [GitOps with ArgoCD](#gitops-with-argocd)
  - [PaaS Deployment (Render)](#paas-deployment-render)
  - [Monitoring & Observability](#monitoring--observability)
- [Operational & Utility Scripts](#-operational--utility-scripts)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🏗️ System Architecture

BiasharaIQ is designed following a decoupled, microservice-ready client-server architecture with cloud-native deployment paths:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                     CLIENT LAYER                                       │
│                                                                                        │
│     Next.js 14 Web Application                        Capacitor Android Native App      │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ HTTPS / REST API / JSON
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   APPLICATION LAYER                                    │
│                                                                                        │
│                                  FastAPI Gateway / App                                 │
│                                           │                                            │
│   ┌───────────────┬───────────────────────┼──────────────────────┬─────────────────┐   │
│   │               │                       │                      │                 │   │
│ Auth & JWT    Transactions            M-Pesa Express         AI Categorizer     Uploads│   │
│ & Subscriptions   & Analytics             & Payments             & Assistant Engine & OCR │   │
│   │               │                       │                      │                 │   │
└───┼───────────────┼───────────────────────┼──────────────────────┼─────────────────┼───┘
    │               │                       │                      │                 │
    └───────────────┴───────────┬───────────┴──────────────────────┴─────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PERSISTENCE LAYER                                    │
│                                                                                        │
│                                PostgreSQL Database                                     │
│                     (Users, Transactions, Subscriptions, Uploads)                      │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                EXTERNAL INTEGRATIONS                                   │
│                                                                                        │
│   • Safaricom Daraja M-Pesa API  (STK Push, C2B/B2C, Callbacks)                        │
│   • Google GenAI / Gemini API    (AI Categorization, Intent Analysis, Advisory Agent)  │
│   • Cloud Storage (S3/Cloudinary) (Receipt & Document Attachments)                     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

- **Transaction Management**: Record, view, filter, export, and categorize income and expenses with multi-currency support.
- **AI-Powered Financial Intelligence**:
  - Automatic transaction categorization using Google Gemini AI with fallback rules.
  - Contextual AI financial advisor and intent classifier for conversational query responses.
  - Automated business insights generator analyzing spending, revenue trends, and cash flow alerts.
- **M-Pesa Payment Integration**:
  - M-Pesa Express (STK Push) for subscription payments and customer transactions.
  - Asynchronous webhook/callback processing with transaction status verification.
- **Document & Statement Parsing**: Upload bank statements, M-Pesa statements, receipts, and invoices (PDF, CSV, Excel, Images) with automated OCR extraction.
- **Subscription & Tier Management**: Tiered subscription levels (Free, Standard, Premium) enforced through custom middleware guards.
- **Multi-Platform Access**: Responsive Next.js web portal and Capacitor-wrapped native Android APK.
- **Comprehensive Infrastructure Automation**: Production-ready IaC with Terraform, Kubernetes manifests, Helm charts, ArgoCD GitOps, and Prometheus/Grafana monitoring.

---

## 🧰 Tech Stack

| Category | Technologies |
|---|---|
| **Frontend** | Next.js 14, React 18, Tailwind CSS, Recharts, Lucide Icons, Axios |
| **Mobile** | Capacitor 5, Android SDK, Gradle |
| **Backend** | Python 3.10+, FastAPI, Pydantic, SQLAlchemy ORM, Uvicorn, PyJWT, Passlib (Argon2 / Bcrypt) |
| **Database** | PostgreSQL (Production/Dev), SQLite (Fallback/Testing), Redis (Caching/Sessions) |
| **AI / ML** | Google GenAI SDK (`google-genai`), Gemini 1.5/2.0 Models, Custom Prompt & Fallback Engines |
| **Integrations** | Safaricom Daraja M-Pesa API (STK Push), SMTP Email Verification |
| **DevOps & Cloud** | Docker, Docker Compose, Terraform, AWS (ECS Fargate, RDS, ALB, ECR, Secrets Manager, CloudWatch), Kubernetes, Helm, ArgoCD, Render |
| **Observability** | Prometheus, Grafana, CloudWatch Metrics & Logs |
| **Scripting** | PowerShell, Bash, Python |

---

## 📁 Project Directory Structure

```text
biasharaIQ/
├── backend/                  # FastAPI Application Server
│   ├── core/                 # App configuration, DB session, authentication utilities
│   ├── middleware/           # Subscription guards & auth middleware
│   ├── models/               # SQLAlchemy models & schema definitions
│   ├── routes/               # API endpoints (auth, transactions, payments, subscriptions, uploads)
│   ├── services/             # Business logic (AI categorizer, AI agent, document parser, M-Pesa, insights)
│   ├── scripts/              # Migration and DB utility scripts
│   ├── schema.sql            # Base PostgreSQL schema definition
│   ├── Dockerfile            # Development Dockerfile
│   ├── Dockerfile.prod       # Production Dockerfile
│   └── requirements.txt      # Python package dependencies
├── frontend/                 # Next.js Web App & Capacitor Mobile Shell
│   ├── src/                  # App routes, components, contexts, hooks, utilities
│   │   ├── app/              # Next.js App Router (dashboard, transactions, ai, insights, import, etc.)
│   │   ├── components/       # Shared UI components & charts
│   │   └── context/          # React Context providers (AuthContext, etc.)
│   ├── android/              # Capacitor Android Studio project files
│   ├── next.config.js        # Next.js configuration
│   └── package.json          # Node dependencies & npm build scripts
├── infra/                    # Infrastructure as Code & Deployment Configuration
│   ├── terraform/            # AWS Terraform infrastructure modules (VPC, ECS, RDS, ALB, ECR, IAM, Secrets)
│   ├── k8s/                  # Native Kubernetes manifests
│   ├── helm/                 # Helm chart specifications
│   ├── argocd/               # ArgoCD GitOps application definition
│   └── monitoring/           # Prometheus configuration & Grafana/CloudWatch dashboards
├── k8s/                      # Root Kubernetes manifests & Kustomize configuration
├── docs/                     # Architecture & UML documentation
│   ├── BiasharaIQ_Detailed_UML_Architecture.md
│   └── project-url-diagrams.md
├── scripts/                  # Security & maintenance helper scripts (secret scanners, redact)
├── docker-compose.yml        # Multi-container local orchestration (Backend + Frontend + Postgres)
├── render.yaml               # Render Cloud PaaS service definition
├── setup-dev.sh / .ps1       # Environment bootstrap scripts
├── build-mobile.sh / .ps1    # Capacitor Android APK build scripts
├── health_check.sh / .ps1    # Platform health-check scripts
├── verify-deployment.sh / .ps1 # Deployment verification scripts
├── setup_mpesa.py            # M-Pesa setup & sandbox utility
└── README.md                 # Project documentation
```

---

## 🚀 Getting Started & Local Development

### Prerequisites

Ensure you have the following installed on your machine:
- **Python**: 3.10 or higher
- **Node.js**: 18.x or 20.x
- **npm**: 9.x or higher
- **Docker & Docker Compose** (optional, for containerized run)
- **PostgreSQL** (optional, SQLite can be used for quick local dev)
- **Android Studio & Java JDK 17** (optional, for mobile APK builds)

---

### Quickstart with Setup Scripts

Automated bootstrap scripts are provided for Linux/macOS (`.sh`) and Windows (`.ps1`):

#### On Linux / macOS:
```bash
chmod +x setup-dev.sh
./setup-dev.sh
```

#### On Windows (PowerShell):
```powershell
.\setup-dev.ps1
```

These scripts will:
1. Verify prerequisite runtimes (Python, Node.js).
2. Create and activate a Python virtual environment (`.venv`).
3. Install backend dependencies from `backend/requirements.txt`.
4. Install frontend packages from `frontend/package.json`.
5. Copy template environment configurations if `.env` does not exist.

---

### Manual Local Setup

#### 1. Environment Configuration
Copy the `.env` template or set up backend environment variables:
```bash
cp .env.example .env   # Or create .env with required keys
```

Key environment variables:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/biasharaiq

# JWT Authentication
SECRET_KEY=your-super-secret-jwt-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI Configuration
GEMINI_API_KEY=your-google-gemini-api-key

# M-Pesa Configuration (Sandbox or Production)
MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_PASSKEY=your_passkey
MPESA_SHORTCODE=174379
MPESA_CALLBACK_URL=https://your-domain.com/api/v1/payments/callback
```

#### 2. Start Backend Service
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run database seed (optional for demo data)
python seed_demo.py

# Start Uvicorn development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger OpenAPI Docs: `http://localhost:8000/docs`
- Redoc API Docs: `http://localhost:8000/redoc`

#### 3. Start Frontend Service
```bash
cd frontend
npm install
npm run dev
```
- Web Application URL: `http://localhost:3000`

---

### Docker Compose Local Environment

To spin up the complete application stack (Frontend, Backend, and PostgreSQL database) with a single command:

```bash
docker-compose up --build
```

Services exposed:
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **PostgreSQL**: `localhost:5432`

To tear down the containers:
```bash
docker-compose down -v
```

---

## 🧩 Core Platform Modules

### 1. Backend & REST API
Built with **FastAPI**, providing high performance, auto-generated OpenAPI documentation, and asynchronous request handling.
- Auth endpoints (`/api/v1/auth`): Registration, Login, Token Refresh, Password Reset, Email Verification.
- Transactions (`/api/v1/transactions`): CRUD operations, category filtering, search, bulk updates, AI auto-categorization triggers.
- Subscriptions (`/api/v1/subscriptions`): Current tier checks, plan upgrades, subscription history.
- Payments (`/api/v1/payments`): Initiate M-Pesa STK push, query transaction status, receive webhooks.
- Document Uploads (`/api/v1/uploads`): Multi-format parser for bank & M-Pesa statements, OCR extraction, transaction importing.
- AI & Insights (`/api/v1/ai`): Conversational AI assistant query handler, spending anomaly detection, cash flow projections.

### 2. Frontend Web Application
Built with **Next.js 14 (App Router)** and **Tailwind CSS**.
- Interactive Dashboards with Recharts (Income vs Expenses, Cash Flow, Category Breakdown).
- Smart Transaction Table with filtering, pagination, and manual/AI editing.
- Document Upload Center with drag-and-drop file upload and parsed data review interface.
- Conversational AI Assistant page for real-time business financial advice.
- Pricing & Subscription management page with M-Pesa checkout flow.

### 3. Mobile Application (Android / Capacitor)
BiasharaIQ includes a mobile wrapper configured with **Capacitor**, enabling native Android builds from the Next.js frontend base.

To build the Android APK:

#### Using helper scripts:
```bash
# On Linux / macOS
chmod +x build-mobile.sh
./build-mobile.sh

# On Windows
.\build-mobile.ps1
```

#### Manual Capacitor CLI Workflow:
```bash
cd frontend
npm run build:mobile
npx cap copy android
npx cap open android
```
The output APK is compiled under `frontend/android/app/build/outputs/apk/debug/app-debug.apk` (or top-level build artifacts).

---

### 4. AI Engine & Insights Service
Located in `backend/services/`, the AI subsystem powers intelligent data processing:
- **AI Categorizer** (`ai_categorizer.py`): Categorizes raw transaction descriptions into standard expense/income taxonomy using Gemini 1.5/2.0 API with a robust heuristic rule-based fallback system.
- **Intent Classifier** (`intent_classifier.py`): Classifies financial user queries (e.g., revenue analysis, expense reduction, forecasting) to optimize AI agent responses.
- **Context Builder** (`context_builder.py`): Assembles real-time business metrics into condensed prompt context for accurate, context-aware financial advice.
- **AI Agent** (`ai_agent.py`): Conversational agent delivering actionable business advice tailored for Kenyan enterprise contexts.
- **Financial & Insights Engine** (`financial_engine.py`, `insights_engine.py`): Calculates burn rate, run rate, top spending categories, and cash flow risk alerts.

---

### 5. M-Pesa Payment Integration
Integrated with Safaricom Daraja API (`backend/services/mpesa.py` and `setup_mpesa.py`):
- **STK Push (Lipan a M-Pesa Online)**: Prompts user's mobile phone for PIN to complete subscription or bill payments.
- **Callback Processing**: Asynchronous endpoint to receive payment validation and completion confirmations from Safaricom.
- **Sandbox Testing Helper**: Use `python setup_mpesa.py` to test and register M-Pesa URLs or generate API tokens.

---

### 6. Document Parsing & Transaction Uploads
Located in `backend/services/document_parser.py`:
- Parses PDF bank statements, M-Pesa PDF/CSV statements, Excel spreadsheets (`.xlsx`, `.xls`), and image receipts (`.png`, `.jpg`).
- Uses regex patterns and AI OCR extraction to pull date, description, reference code, amount, and transaction type.
- Allows users to review, edit, and approve extracted records before saving to the primary database.

---

### 7. Authentication & Subscription Guards
- **Security**: JWT tokens passed via Authorization headers (`Bearer <token>`). Passwords hashed with Argon2 / Bcrypt.
- **Subscription Guards** (`backend/middleware/subscription_guard.py`): Protects premium features (e.g., advanced AI insights, unlimited uploads) based on user's active tier (Free, Standard, Premium).

---

## 🗄️ Database Management & Migration

The system uses **PostgreSQL** in production and supports SQLite for lightweight local testing.

### Useful Database Commands:

```bash
cd backend

# Seed database with sample SME transactions and user accounts
python seed_demo.py

# Reset database schema and recreate tables
python reset_db.py

# Run migration to AWS RDS PostgreSQL instance
python migrate_to_aws.py

# Normalize subscription plan ENUM values
python scripts/normalize_plan_enum.py
```

---

## ☁️ DevOps, Infrastructure & Deployment

### AWS Deployment via Terraform
Production AWS infrastructure is managed using Terraform in `infra/terraform/`.

Modules included:
- **Networking**: VPC, Public/Private Subnets, Internet Gateway, NAT Gateways, Route Tables.
- **ECS Fargate**: Containerized cluster execution for backend and frontend services.
- **RDS PostgreSQL**: Managed relational database with multi-AZ capability.
- **ALB**: Application Load Balancer with HTTPS SSL termination and path routing.
- **ECR**: Elastic Container Registry repositories for application images.
- **IAM & Secrets Manager**: Security policies, execution roles, and secret storage.
- **Monitoring & CloudWatch**: Centralized log groups, metrics, and alarm triggers.

To deploy AWS infrastructure:
```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

---

### Kubernetes & Helm Deployment
Kubernetes manifests and Helm charts are available in `k8s/`, `infra/k8s/`, and `infra/helm/`.

Deploy via `kubectl` or `kustomize`:
```bash
# Apply namespace, secrets, and volume claims
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/persistent-volume-claims.yaml

# Deploy database, cache, backend, and frontend
kubectl apply -k k8s/
```

Deploy via Helm:
```bash
helm upgrade --install biasharaiq infra/helm/ -f infra/helm/values.yaml
```

---

### GitOps with ArgoCD
Continuous deployment can be managed with ArgoCD using `infra/argocd/application.yaml`.

```bash
kubectl apply -f infra/argocd/application.yaml
```

---

### PaaS Deployment (Render)
For rapid PaaS deployment, `render.yaml` defines blue-green service specs for:
- FastAPI backend Web Service
- Next.js frontend Web Service
- Managed PostgreSQL database

---

### Monitoring & Observability
- **Prometheus Configuration**: Located at `infra/monitoring/prometheus.yml`.
- **Grafana / CloudWatch Dashboards**: ECS and application metric definitions in `infra/monitoring/dashboards/ecs-dashboard.json`.

---

## 🛠️ Operational & Utility Scripts

| Script | Purpose |
|---|---|
| `setup-dev.sh` / `setup-dev.ps1` | Bootstraps local environment, venv, and npm dependencies |
| `build-mobile.sh` / `build-mobile.ps1` | Builds production frontend assets and packages Android APK |
| `health_check.sh` / `health_check.ps1` | Verifies health of backend, database, and frontend services |
| `verify-deployment.sh` / `verify-deployment.ps1` | Validates active deployment URLs, API responses, and database connectivity |
| `setup_mpesa.py` | Configures M-Pesa sandbox keys, token generation, and URL registration |
| `scripts/find_secrets.py` | Scans codebase for accidentally committed API keys or credentials |
| `scripts/redact_secrets.py` | Sanitizes sensitive information from configuration logs |

To run health check:
```bash
./health_check.sh
# or PowerShell:
.\health_check.ps1
```

To verify a deployment:
```bash
./verify-deployment.sh -Url "https://your-api-domain.com"
```

---

## 📚 Documentation

Detailed system documentation and UML diagrams can be found in the `docs/` folder:
- [BiasharaIQ Detailed UML Architecture](docs/BiasharaIQ_Detailed_UML_Architecture.md): Complete class diagrams, sequence flows, database schemas, and deployment topologies.
- [Project URL & Service Diagrams](docs/project-url-diagrams.md): Visual topology maps and environment endpoint listings.

---

## 🤝 Contributing

1. Fork the repository.
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.
