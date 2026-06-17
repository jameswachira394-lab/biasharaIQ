<#
.SYNOPSIS
Builds the Next.js frontend and generates an Android APK via Capacitor.

.DESCRIPTION
This script navigates to the frontend directory, installs dependencies, builds the Next.js application, syncs it with Capacitor Android, builds the Android APK, and copies the APK back to the root directory.

.EXAMPLE
.\build-mobile.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🚀 Building BiasharaIQ Mobile App (Android)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check if Android SDK is accessible
try {
    $gradlewPath = ".\frontend\android\gradlew.bat"
    if (-Not (Test-Path $gradlewPath)) {
        Write-Warning "Android project not found. Trying to add android platform..."
        Set-Location "frontend"
        npx cap add android
        Set-Location ".."
    }
} catch {
    Write-Warning "Could not verify Android platform existence."
}

# Navigate to frontend
Set-Location "frontend"

Write-Host "`n[1/4] Installing dependencies..." -ForegroundColor Yellow
npm install

Write-Host "`n[2/4] Building Next.js frontend..." -ForegroundColor Yellow
npm run build:mobile

Write-Host "`n[3/4] Building Android APK via Gradle..." -ForegroundColor Yellow
Set-Location "android"

# Ensure ANDROID_HOME is set for the SDK
$androidSdk = "$env:LOCALAPPDATA\Android\Sdk"
if ((Test-Path $androidSdk) -and (-not $env:ANDROID_HOME)) {
    Write-Host "Setting ANDROID_HOME to $androidSdk" -ForegroundColor Cyan
    $env:ANDROID_HOME = $androidSdk
}

# Workaround for Java 25 unsupported issue: Use Android Studio's bundled JDK if available
$androidStudioJbr = "C:\Program Files\Android\Android Studio\jbr"
if (Test-Path $androidStudioJbr) {
    Write-Host "Using Android Studio bundled JDK to avoid Java version issues..." -ForegroundColor Cyan
    $env:JAVA_HOME = $androidStudioJbr
    .\gradlew.bat assembleDebug "-Dorg.gradle.java.home=$androidStudioJbr"
} else {
    .\gradlew.bat assembleDebug
}

# Navigate back to root
Set-Location "..\.."

Write-Host "`n[4/4] Copying APK to root directory..." -ForegroundColor Yellow
$apkPath = "frontend\android\app\build\outputs\apk\debug\app-debug.apk"

if (Test-Path $apkPath) {
    Copy-Item $apkPath -Destination ".\biasharaiq-debug.apk" -Force
    Write-Host "`n✅ Build Successful! The APK is available at: $(Resolve-Path .\biasharaiq-debug.apk)" -ForegroundColor Green
} else {
    Write-Host "`n❌ Build Failed! Could not find the generated APK at $apkPath." -ForegroundColor Red
}
