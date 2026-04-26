# BiashaRaiq - Full Integration Setup Guide

## ✅ Completed
- **Frontend**: Node.js dependencies installed (431 packages)
- **Project Structure**: All files in place

## ⚠️ Backend Issue
The backend dependencies require a C++ compiler to build `pydantic-core` from source on Windows. All Python versions (3.9, 3.13, 3.14) fail without it.

---

## 🚀 Solution - Choose ONE option:

### **Option A: Install Visual Studio Build Tools** (Recommended for local development)

1. Download: https://visualstudio.microsoft.com/downloads/
2. Select **"Visual Studio Build Tools 2022"**
3. Run the installer
4. Choose **"Desktop development with C++"**
5. Complete installation
6. Run:
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

### **Option B: Use Docker** (Best for deployment consistency)

1. Download: https://www.docker.com/products/docker-desktop
2. Install and start Docker
3. Run from project root:
   ```powershell
   cd biasharaiq
   docker-compose up --build
   ```

---

## 📋 Project Structure

```
biasharaiq/
├── backend/              # FastAPI server
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── schema.sql
├── frontend/             # Next.js React app
│   ├── package.json
│   ├── src/
│   └── node_modules/     # ✅ Installed
├── docker-compose.yml    # Ready to use
└── docs/
```

---

## 🔧 Running the Project (After backend setup)

### **Local Development (No Docker)**

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python main.py
# API runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
# App runs on http://localhost:3000
```

### **With Docker**
```powershell
cd biasharaiq
docker-compose up
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Database: localhost:5432
```

---

## 📡 Environment Setup

### Backend (.env already configured)
```env
DATABASE_URL=postgresql://postgres:james8080@localhost/biasharaiq
SECRET_KEY=c8146fcbfe9d8d72ba493d87817f1fabfe9e66ef6e37f74e066bcdb352ae7a2a
ANTHROPIC_API_KEY=sk-900392fe7f6c4e0d89d7e338905b0483
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=100
CORS_ORIGINS=http://localhost:3000
```

### Frontend
- Uses Axios for API calls to `http://localhost:8000`
- Next.js running on port 3000

---

## ✨ Integration Points

### Frontend → Backend Communication
- **Base URL**: `http://localhost:8000`
- **Auth**: JWT tokens via `/auth/login`
- **API Routes**: `/auth`, `/transactions`, `/insights`, `/ai`

### Database
- **Type**: PostgreSQL
- **Connection**: `postgres://postgres:james8080@localhost/biasharaiq`
- **Schema**: Auto-initialized from `backend/schema.sql`

---

## 🎯 Next Steps

1. **Install either Build Tools OR Docker** (see options above)
2. **Install backend dependencies** (once C++ compiler is available)
3. **Start both services** using one of the run commands above
4. **Access the app**: http://localhost:3000

---

## 📞 Troubleshooting

**"link.exe not found"**
→ Install Visual Studio Build Tools with C++ workload

**"docker: command not found"**
→ Install Docker Desktop

**"PostgreSQL connection failed"**
→ Ensure PostgreSQL is running or use Docker Compose

**"npm error Invalid Version"**
→ Already fixed! Frontend installed successfully.

---

## 📚 Additional Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Docker Docs](https://docs.docker.com/)
