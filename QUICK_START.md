# BiashaRaiq - Quick Start Guide

## Current Status ✅

| Component | Status | Details |
|-----------|--------|---------|
| Frontend Dependencies | ✅ Done | 431 packages installed |
| Backend Dependencies | ⏳ Pending | Blocked - needs C++ compiler |
| Project Structure | ✅ Done | All files in place |
| Database | 📦 Ready | PostgreSQL setup in docker-compose |

---

## 🎯 What You Need To Do NOW

### Step 1: Fix Backend Dependencies

**Choose ONE approach:**

#### Approach A: Install Visual Studio Build Tools (Recommended)
```
1. Download: https://visualstudio.microsoft.com/downloads/
2. Search for "Visual Studio Build Tools 2022"
3. Click "Download"
4. Run installer
5. Check "Desktop development with C++"
6. Click "Install" (takes ~10 minutes)
7. Restart if prompted
8. Done!
```

#### Approach B: Use Docker Instead
```
1. Download: https://www.docker.com/products/docker-desktop
2. Run installer
3. Follow setup prompts
4. Restart computer
5. Docker will handle all dependencies automatically
```

---

## Step 2: Install Backend Dependencies

After completing Step 1, run ONE of these:

### If you chose Visual Studio Build Tools:
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### If you chose Docker:
```powershell
cd biasharaiq  # Go to docker-compose.yml location
docker-compose up --build
```

---

## 🚀 Step 3: Run the Project

### Local Development (after Step 2A):

**Terminal 1:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```
→ Backend runs on `http://localhost:8000`

**Terminal 2:**
```powershell
cd frontend
npm run dev
```
→ Frontend runs on `http://localhost:3000`

### With Docker (after Step 2B):
```powershell
cd biasharaiq
docker-compose up
```
→ Both run automatically!

---

## 📱 Access Points

| Service | URL | What to expect |
|---------|-----|----------------|
| Frontend | http://localhost:3000 | React/Next.js dashboard |
| Backend API | http://localhost:8000 | FastAPI with docs |
| API Docs | http://localhost:8000/docs | Interactive Swagger UI |
| Database | localhost:5432 | PostgreSQL (if running local DB) |

---

## ✨ Project Capabilities

- **Authentication**: JWT-based login system
- **Transactions**: Track financial transactions
- **AI Agent**: Powered by Anthropic Claude
- **Insights**: Financial analysis & reporting
- **Real-time Dashboard**: Charts and metrics
- **API**: RESTful backend with Uvicorn

---

## 🔧 Helpful Scripts

Two helper scripts have been created:

### Windows Batch (simple):
```powershell
.\start-dev.bat
# Opens two terminal windows, runs both servers
```

### PowerShell (advanced):
```powershell
.\setup-dev.ps1 -Setup    # Install everything
.\setup-dev.ps1 -Start    # Start both servers
.\setup-dev.ps1 -Setup -Start  # Do both
```

---

## ❓ FAQ

**Q: Which option should I choose (Build Tools vs Docker)?**
A: 
- Build Tools: If you want to develop locally with direct Python
- Docker: If you want exact production environment + easier setup

**Q: The build tools download is huge, will it take long?**
A: Yes, ~3-5GB, but only needed once.

**Q: Can I skip this and just use frontend?**
A: No - frontend makes API calls to backend. Both are needed.

**Q: I already have PostgreSQL running locally?**
A: Update `DATABASE_URL` in `backend/.env` if using different credentials.

**Q: Do I need to run database setup?**
A: With Docker: Automatic. Without Docker: Check `backend/schema.sql`

---

## 📞 Support

If you get stuck:

1. **"linker link.exe not found"** → Install Build Tools
2. **"docker: command not found"** → Install Docker Desktop  
3. **"Cannot connect to PostgreSQL"** → Make sure DB is running
4. **"npm error Invalid Version"** → Already fixed! ✓
5. **Port 3000/8000 already in use** → Close other apps using those ports

---

## 🎓 Next: After Integration

Once everything is running, you can:
- Add new transactions via UI
- Test AI agent features
- View financial insights
- Customize dashboard layouts
- Deploy to production (see DEPLOYMENT.md)

**Start with Step 1 above! 👆**
