# Deployment Configuration Verification Script (PowerShell)
# Run this to verify all deployment settings are correct

param(
    [switch]$Verbose
)

Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "BiasharaIQ Production Deployment Verification" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""

$checksPasssed = 0
$checksFailed = 0

# Function to check a configuration
function Test-Config {
    param(
        [string]$Name,
        [string]$FilePath,
        [string]$Pattern,
        [string]$Expected = ""
    )
    
    $normalizedPath = $FilePath -replace '\\', '/'
    
    if (Test-Path $FilePath) {
        $content = Get-Content $FilePath -Raw
        
        if ($content -match $Pattern) {
            if ([string]::IsNullOrEmpty($Expected) -or ($content -match $Expected)) {
                Write-Host "[OK] $Name" -ForegroundColor Green
                return $true
            }
            else {
                Write-Host "[FAIL] $Name - Expected: $Expected" -ForegroundColor Red
                if ($Verbose) {
                    Write-Host "  File: $normalizedPath" -ForegroundColor DarkGray
                    Write-Host "  Pattern: $Pattern" -ForegroundColor DarkGray
                }
                return $false
            }
        }
        else {
            Write-Host "[FAIL] $Name - Pattern not found: $Pattern" -ForegroundColor Red
            if ($Verbose) {
                Write-Host "  File: $normalizedPath" -ForegroundColor DarkGray
            }
            return $false
        }
    }
    else {
        Write-Host "[FAIL] $Name - File not found: $FilePath" -ForegroundColor Red
        if ($Verbose) {
            Write-Host "  Expected file: $normalizedPath" -ForegroundColor DarkGray
        }
        return $false
    }
}

Write-Host "Backend Configuration:" -ForegroundColor Cyan
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
if (Test-Config "Config uses env variables" "backend/core/config.py" "os\.getenv") { $checksPasssed++ } else { $checksFailed++ }
if (Test-Config "CORS origins configured" "render.yaml" "CORS_ORIGINS") { $checksPasssed++ } else { $checksFailed++ }
if (Test-Config "Frontend URL configured" "render.yaml" "FRONTEND_URL") { $checksPasssed++ } else { $checksFailed++ }
if (Test-Config "Environment set to production" "render.yaml" "ENVIRONMENT") { $checksPasssed++ } else { $checksFailed++ }
if (Test-Config "Database pool optimized" "render.yaml" "DB_POOL_SIZE") { $checksPasssed++ } else { $checksFailed++ }
Write-Host ""

Write-Host "Frontend Configuration:" -ForegroundColor Cyan
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
if (Test-Config "API URL set correctly" "frontend/vercel.json" "NEXT_PUBLIC_API_URL" "https://biasharaiq\.onrender\.com") { $checksPasssed++ } else { $checksFailed++ }
if (Test-Config "Production Docker image" "frontend/Dockerfile" "NEXT_PUBLIC_API_URL" "https://biasharaiq\.onrender\.com") { $checksPasssed++ } else { $checksFailed++ }
if (Test-Config "Build cache configured" "frontend/vercel.json" "buildCache") { $checksPasssed++ } else { $checksFailed++ }
Write-Host ""

Write-Host "API Configuration:" -ForegroundColor Cyan
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
if (Test-Config "Health check endpoint" "backend/main.py" "health") { $checksPasssed++ } else { $checksFailed++ }
if (Test-Config "Security headers" "backend/main.py" "X-Frame-Options") { $checksPasssed++ } else { $checksFailed++ }
if (Test-Config "Request logging" "backend/main.py" "log_requests") { $checksPasssed++ } else { $checksFailed++ }
if (Test-Config "CORS middleware" "backend/main.py" "CORSMiddleware") { $checksPasssed++ } else { $checksFailed++ }
Write-Host ""

Write-Host "Docker Configuration:" -ForegroundColor Cyan
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
if (Test-Config "Production Dockerfile uses Gunicorn" "backend/Dockerfile.prod" "gunicorn") { $checksPasssed++ } else { $checksFailed++ }
if (Test-Config "Non-root user in Docker" "backend/Dockerfile.prod" "useradd -m -u 1000") { $checksPasssed++ } else { $checksFailed++ }
if (Test-Config "Health check in compose" "docker-compose.prod.yml" "healthcheck") { $checksPasssed++ } else { $checksFailed++ }
Write-Host ""

Write-Host "Environment Files:" -ForegroundColor Cyan
Write-Host "-----------------------------------------------------------" -ForegroundColor Gray
if (Test-Config "Production env example exists" "backend/.env.example" "ENVIRONMENT") { $checksPasssed++ } else { $checksFailed++ }
if (Test-Config "Frontend production env exists" "frontend/.env.production" "NEXT_PUBLIC_API_URL") { $checksPasssed++ } else { $checksFailed++ }
if (Test-Config "Deployment guide exists" "DEPLOYMENT.md" "BiasharaIQ Deployment Guide") { $checksPasssed++ } else { $checksFailed++ }
Write-Host ""

Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "Passed: $checksPasssed" -ForegroundColor Green
Write-Host "Failed: $checksFailed" -ForegroundColor Red
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""

if ($checksFailed -eq 0) {
    Write-Host "[SUCCESS] All deployment configurations verified!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Push code to GitHub: git push" -ForegroundColor White
    Write-Host "2. Set environment variables in Render dashboard:" -ForegroundColor White
    Write-Host "   - SECRET_KEY (auto-generated)" -ForegroundColor DarkGray
    Write-Host "   - ANTHROPIC_API_KEY" -ForegroundColor DarkGray
    Write-Host "   - GEMINI_API_KEY" -ForegroundColor DarkGray
    Write-Host "3. Trigger Render deployment from GitHub" -ForegroundColor White
    Write-Host "4. Verify frontend deployment on Vercel" -ForegroundColor White
    Write-Host "5. Test health endpoint: curl https://biasharaiq.onrender.com/health" -ForegroundColor White
    exit 0
}
else {
    Write-Host "[FAILED] Some configurations need attention!" -ForegroundColor Red
    Write-Host "Please review the failed checks above." -ForegroundColor Red
    if (-not $Verbose) {
        Write-Host "Run with -Verbose flag for more details." -ForegroundColor Yellow
    }
    exit 1
}
