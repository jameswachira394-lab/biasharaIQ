@echo off
cd backend
call venv\Scripts\activate.bat
python -m uvicorn main:app --reload --port 8000
pause
