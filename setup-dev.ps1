# BiashaRaiq - Development Setup and Start Script
# This PowerShell script sets up and starts the full development environment

param(
    [switch]$Setup,
    [switch]$Start
)

$ErrorActionPreference = "Stop"

function Write-Section {
    param([string]$Text)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Text)
    Write-Host "[✓] $Text" -ForegroundColor Green
}

function Write-Error {
    param([string]$Text)
    Write-Host "[✗] $Text" -ForegroundColor Red
}

Write-Section "BiashaRaiq Integration"

# If no arguments, show help
if (-not $Setup -and -not $Start) {
    Write-Host "Usage: .\setup-dev.ps1 -Setup    # Setup backend & frontend" -ForegroundColor Yellow
    Write-Host "       .\setup-dev.ps1 -Start    # Start both servers" -ForegroundColor Yellow
    Write-Host "       .\setup-dev.ps1 -Setup -Start  # Setup and start" -ForegroundColor Yellow
    exit
}

# Setup phase
if ($Setup) {
    Write-Section "Setting Up Backend"
    
    if (-not (Test-Path "backend\venv")) {
        Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
        python -m venv backend\venv
        Write-Success "Virtual environment created"
    } else {
        Write-Success "Virtual environment already exists"
    }
    
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    & "backend\venv\Scripts\Activate.ps1"
    pip install -r backend\requirements.txt
    Write-Success "Backend dependencies installed"
    
    Write-Section "Setting Up Frontend"
    
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    cd frontend
    npm install
    cd ..
    Write-Success "Frontend dependencies installed"
    
    Write-Section "Setup Complete!"
    Write-Host "Next step: Run '.\setup-dev.ps1 -Start' to start servers" -ForegroundColor Green
}

# Start phase
if ($Start) {
    Write-Section "Checking Prerequisites"
    
    if (-not (Test-Path "backend\venv")) {
        Write-Error "Backend virtual environment not found. Run with -Setup first"
        exit 1
    }
    Write-Success "Backend venv found"
    
    if (-not (Test-Path "frontend\node_modules")) {
        Write-Error "Frontend node_modules not found. Run with -Setup first"
        exit 1
    }
    Write-Success "Frontend node_modules found"
    
    Write-Section "Starting Services"
    Write-Host "Press CTRL+C in either window to stop all services`n" -ForegroundColor Yellow
    
    # Start backend
    Write-Host "Starting Backend..." -ForegroundColor Green
    $backendJob = Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; python main.py" -PassThru -WindowStyle Normal
    
    # Wait a moment
    Start-Sleep -Seconds 2
    
    # Start frontend
    Write-Host "Starting Frontend..." -ForegroundColor Green
    $frontendJob = Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -PassThru -WindowStyle Normal
    
    Write-Section "Services Started"
    Write-Host "Backend:  http://localhost:8000" -ForegroundColor Green
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
    Write-Host "`nPress any key to exit (this will NOT stop the servers)" -ForegroundColor Yellow
    [void][System.Console]::ReadKey($true)
}
