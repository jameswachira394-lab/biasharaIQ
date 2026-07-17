# Production Health Check & Monitoring Script (PowerShell)
# Usage: .\health_check.ps1 -EnvironmentUrl "http://localhost:8000"

param(
    [string]$EnvironmentUrl = "http://localhost:8000",
    [int]$TimeoutSeconds = 10
)

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$healthCheckLog = "health_check_log.txt"
$failedChecks = 0

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "BiasharaIQ Production Health Check" -ForegroundColor Cyan
Write-Host "Environment: $EnvironmentUrl" -ForegroundColor Cyan
Write-Host "Timestamp: $timestamp" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Function to check endpoint
function Check-Endpoint {
    param(
        [string]$Endpoint,
        [string]$Name
    )
    
    Write-Host -NoNewline "Checking $Name... "
    
    try {
        $response = Invoke-WebRequest -Uri "$EnvironmentUrl$Endpoint" -TimeoutSec $TimeoutSeconds -ErrorAction Stop
        
        if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 307) {
            Write-Host "✓ OK (HTTP $($response.StatusCode))" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "✗ FAILED: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to check database connection
function Check-Database {
    Write-Host -NoNewline "Checking database connection... "
    
    try {
        $response = Invoke-WebRequest -Uri "$EnvironmentUrl/health" -TimeoutSec $TimeoutSeconds -ErrorAction Stop
        $content = $response.Content | ConvertFrom-Json
        
        if ($content.database -eq "connected" -or $response.StatusCode -eq 200) {
            Write-Host "✓ Connected" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "✗ ERROR" -ForegroundColor Red
        return $false
    }
}

# Function to check response time
function Check-ResponseTime {
    param(
        [string]$Endpoint,
        [string]$Name
    )
    
    Write-Host -NoNewline "Checking $Name response time... "
    
    try {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-WebRequest -Uri "$EnvironmentUrl$Endpoint" -TimeoutSec $TimeoutSeconds -ErrorAction Stop
        $stopwatch.Stop()
        
        $responseTimeMs = $stopwatch.ElapsedMilliseconds
        
        if ($responseTimeMs -lt 500) {
            Write-Host "✓ ${responseTimeMs}ms" -ForegroundColor Green
            return $true
        }
        elseif ($responseTimeMs -lt 1000) {
            Write-Host "⚠ ${responseTimeMs}ms" -ForegroundColor Yellow
            return $true
        }
        else {
            Write-Host "✗ ${responseTimeMs}ms (Slow)" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "✗ ERROR" -ForegroundColor Red
        return $false
    }
}

# Run health checks
Write-Host "API Endpoints:" -ForegroundColor Cyan
if (-not (Check-Endpoint "/" "API Root")) { $failedChecks++ }
if (-not (Check-Endpoint "/health" "Health Check")) { $failedChecks++ }
if (-not (Check-Endpoint "/docs" "API Documentation")) { $failedChecks++ }

Write-Host ""
Write-Host "Database:" -ForegroundColor Cyan
if (-not (Check-Database)) { $failedChecks++ }

Write-Host ""
Write-Host "Performance:" -ForegroundColor Cyan
if (-not (Check-ResponseTime "/" "API Response")) { $failedChecks++ }
if (-not (Check-ResponseTime "/health" "Health Endpoint")) { $failedChecks++ }

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
if ($failedChecks -eq 0) {
    Write-Host "All checks passed ✓" -ForegroundColor Green
    $exitCode = 0
}
else {
    Write-Host "$failedChecks check(s) failed ✗" -ForegroundColor Red
    $exitCode = 1
}
Write-Host "===============================================" -ForegroundColor Cyan

# Log results
$logEntry = "$timestamp - Checks passed: $((6 - $failedChecks)), Failed: $failedChecks"
Add-Content -Path $healthCheckLog -Value $logEntry

exit $exitCode
