@echo off
REM BiashaRaiq - Start Development Servers
REM This script starts both frontend and backend for local development

setlocal enabledelayedexpansion

echo.
echo ====================================
echo   BiashaRaiq - Development Setup
echo ====================================
echo.

REM Check if backend venv exists
if not exist "backend\venv\" (
    echo [ERROR] Backend virtual environment not found!
    echo.
    echo Please run setup first:
    echo   cd backend
    echo   python -m venv venv
    echo   .\venv\Scripts\Activate.ps1
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Check if frontend node_modules exists
if not exist "frontend\node_modules\" (
    echo [ERROR] Frontend node_modules not found!
    echo.
    echo Please run setup first:
    echo   cd frontend
    echo   npm install
    echo.
    pause
    exit /b 1
)

echo [✓] Backend venv found
echo [✓] Frontend node_modules found
echo.
echo Starting services...
echo.
echo Press CTRL+C in any terminal to stop services
echo.

REM Create separate terminal windows for each service
start "BiashaRaiq Backend" cmd /k "cd backend & .\venv\Scripts\activate.bat & python main.py"
timeout /t 2 /nobreak
start "BiashaRaiq Frontend" cmd /k "cd frontend & npm run dev"

echo.
echo ====================================
echo Services starting...
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo ====================================
echo.

pause
