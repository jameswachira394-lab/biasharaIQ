# BiasharaIQ – Financial Intelligence Platform

A financial intelligence + decision system for real-world small businesses in Kenya.

---

## Windows Quick Start

### Step 1 – Install PostgreSQL
Download and install from: https://www.postgresql.org/download/windows/
- Remember the password you set for the `postgres` user
- Make sure to check "Add to PATH" during install

### Step 2 – Create the database
Open **psql** (installed with PostgreSQL) or pgAdmin, then run:
```sql
CREATE DATABASE biasharaiq;
```

### Step 3 – Backend setup
```powershell
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install psycopg2 first (pre-built binary, no compilation needed)
pip install psycopg2-binary --only-binary :all:

# Install remaining packages
pip install -r requirements.txt

# Copy and edit environment file
copy .env.example .env
notepad .env
```

Edit `.env` with your values:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost/biasharaiq
SECRET_KEY=any-random-string-at-least-32-characters-long
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
```

### Step 4 – Set up the database schema
```powershell
# Still in the backend folder with venv active
psql -U postgres -d biasharaiq -f schema.sql
```

### Step 5 – Start the backend
```powershell
uvicorn main:app --reload --port 8000
```
✅ API running at http://localhost:8000
✅ API docs at http://localhost:8000/docs

### Step 6 – Frontend setup (new terminal)
```powershell
cd frontend
npm install
copy .env.example .env.local
```
Edit `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```
Then:
```powershell
npm run dev
```
✅ App running at http://localhost:3000

### Step 7 – Load demo data (optional)
```powershell
cd backend
venv\Scripts\activate
python seed_demo.py
```
Login with: `demo@biasharaiq.com` / `demo1234`

---

## Mac/Linux Quick Start

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install psycopg2-binary -r requirements.txt

cp .env.example .env   # edit with your values
createdb biasharaiq
psql biasharaiq < schema.sql
uvicorn main:app --reload --port 8000 &

cd ../frontend
npm install && cp .env.example .env.local
npm run dev
```

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
