heheuhe# BiasharaIQ – Financial Intelligence Platform

BiasharaIQ is a financial intelligence system built for Kenyan micro, small, and medium enterprises (SMEs). It combines transaction tracking, AI-assisted categorization, M-Pesa payment integration, analytics, and a mobile-ready user experience.

---

## ✅ What This Project Does

- Tracks business transactions, income, and expenses
- Automates categorization using Google GenAI / Gemini
- Supports M-Pesa payment flows and callback handling
- Provides analytics, dashboards, and insights
- Includes a web app and an Android-capable mobile app via Capacitor
- Is designed for deployment on AWS ECS/RDS with Terraform and Docker

---

## 🏗️ Architecture Overview

BiasharaIQ is built with a decoupled frontend and backend:

1. **Frontend**
   - Next.js 14, React 18, Tailwind CSS
   - Recharts for visualization
   - Capacitor-powered Android mobile packaging
   - React client communicates with the backend over REST

2. **Backend**
   - Python FastAPI
   - SQLAlchemy ORM for PostgreSQL
   - AI services powered by Google GenAI / Gemini
   - M-Pesa integration for payments and transaction imports

3. **Database**
   - PostgreSQL stores users, transactions, subscriptions, uploads, and insights

---

## 📁 Project Structure

```text
biasharaIQ/
├── backend/              # FastAPI backend service
│   ├── core/             # config, authentication, database setup
│   ├── middleware/       # request guards, auth, subscription checks
│   ├── models/           # SQLAlchemy ORM models and DB helpers
│   ├── routes/           # API endpoint definitions
│   ├── services/         # AI, payments, insights, parsing, and business logic
│   ├── requirements.txt  # backend dependencies
│   ├── Dockerfile
│   └── Dockerfile.prod
├── frontend/             # Next.js frontend app and Capacitor mobile wrapper
│   ├── src/              # application pages and components
│   ├── android/          # Capacitor Android app project
│   ├── package.json
│   └── next.config.js
├── terraform/            # AWS infrastructure as code
├── docker-compose.yml    # local development orchestration
├── setup-dev.ps1         # Windows development setup script
├── build-mobile.ps1      # Android build helper
├── setup_mpesa.py        # M-Pesa setup helper
└── verify-deployment.ps1 # deployment validation script
```

---

## 🧰 Tech Stack

- Frontend: Next.js, React, Tailwind CSS, Recharts, Capacitor
- Backend: Python, FastAPI, SQLAlchemy
- Database: PostgreSQL
- AI: Google GenAI / Gemini with rule-based fallback
- Payments: M-Pesa integration
- Deployment: Docker, Docker Compose, Terraform, AWS ECS/RDS
- Scripting: PowerShell and Bash utilities

---

## 🚀 Local Development

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm
- Docker (optional)
- `.env` configuration with local settings and API keys

### Run Backend

```bash
cd backend
python -m venv .venv
# PowerShell
.\.venv\Scripts\Activate.ps1
# Bash
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Run Frontend

```bash
cd frontend
npm install
npm run dev
```

### API Documentation

Once the backend is running, open:

`http://localhost:8000/docs`

---

## 📦 Mobile App

The frontend supports Capacitor and can be built for Android using the included `android/` project.

From `frontend/`:

```bash
npm run build:mobile
```

Or use the provided PowerShell helper:

```powershell
./build-mobile.ps1
```

---

## 💡 Important Scripts

- `setup-dev.ps1` / `setup-dev.sh` — prepare local development environment
- `docker-compose.yml` — run backend and frontend together in containers
- `setup_mpesa.py` — M-Pesa setup helper
- `health_check.ps1` / `health_check.sh` — service health checks
- `verify-deployment.ps1` / `verify-deployment.sh` — deployment validation

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes
4. Push the branch and open a pull request

---

## 📌 Notes

- This repository currently uses Google GenAI / Gemini for AI transaction categorization.
- M-Pesa support is configured through keys in the backend environment and sandbox settings.
- Terraform is included for AWS ECS/RDS deployment automation.

---

## 📄 License

See `LICENSE` if present in the repository.
