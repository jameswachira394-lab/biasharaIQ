#!/bin/bash

# Deployment Configuration Verification Script
# Run this to verify all deployment settings are correct

set -e

echo "═══════════════════════════════════════════════════════════"
echo "BiasharaIQ Production Deployment Verification"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to check a configuration
check_config() {
    local name=$1
    local file=$2
    local pattern=$3
    local expected=$4
    
    if grep -q "$pattern" "$file" 2>/dev/null; then
        if [ -z "$expected" ] || grep -q "$expected" "$file" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} $name"
            ((CHECKS_PASSED++))
        else
            echo -e "${RED}✗${NC} $name - Expected: $expected"
            ((CHECKS_FAILED++))
        fi
    else
        echo -e "${RED}✗${NC} $name - Pattern not found: $pattern"
        ((CHECKS_FAILED++))
    fi
}

echo "Backend Configuration:"
echo "─────────────────────────────────────────────────────────"
check_config "Config uses env variables" "backend/core/config.py" "os.getenv"
check_config "CORS origins configured" "render.yaml" "CORS_ORIGINS"
check_config "Frontend URL configured" "render.yaml" "FRONTEND_URL"
check_config "Environment set to production" "render.yaml" "ENVIRONMENT: production"
check_config "Database pool optimized" "render.yaml" "DB_POOL_SIZE: 25"
echo ""

echo "Frontend Configuration:"
echo "─────────────────────────────────────────────────────────"
check_config "API URL set correctly" "frontend/vercel.json" "NEXT_PUBLIC_API_URL" "https://biasharaiq.onrender.com"
check_config "Production Docker image" "frontend/Dockerfile" "NEXT_PUBLIC_API_URL" "https://biasharaiq.onrender.com"
check_config "Build cache configured" "frontend/vercel.json" "buildCache"
echo ""

echo "API Configuration:"
echo "─────────────────────────────────────────────────────────"
check_config "Health check endpoint" "backend/main.py" "@app.get(\"/health\")"
check_config "Security headers" "backend/main.py" "X-Frame-Options"
check_config "Request logging" "backend/main.py" "log_requests"
check_config "CORS middleware" "backend/main.py" "CORSMiddleware"
echo ""

echo "Docker Configuration:"
echo "─────────────────────────────────────────────────────────"
check_config "Production Dockerfile uses Gunicorn" "backend/Dockerfile.prod" "gunicorn"
check_config "Non-root user in Docker" "backend/Dockerfile.prod" "useradd -m -u 1000"
check_config "Health check in compose" "docker-compose.prod.yml" "healthcheck"
echo ""

echo "Environment Files:"
echo "─────────────────────────────────────────────────────────"
check_config "Production env example exists" "backend/.env.example" "ENVIRONMENT"
check_config "Frontend production env exists" "frontend/.env.production" "NEXT_PUBLIC_API_URL"
check_config "Deployment guide exists" "DEPLOYMENT.md" "BiasharaIQ Deployment Guide"
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "Summary:"
echo -e "${GREEN}Passed: $CHECKS_PASSED${NC}"
echo -e "${RED}Failed: $CHECKS_FAILED${NC}"
echo "═══════════════════════════════════════════════════════════"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All deployment configurations verified!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Push code to GitHub: git push"
    echo "2. Set environment variables in Render dashboard:"
    echo "   - SECRET_KEY (auto-generated)"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - GEMINI_API_KEY"
    echo "3. Trigger Render deployment from GitHub"
    echo "4. Verify frontend deployment on Vercel"
    echo "5. Test health endpoint: curl https://biasharaiq.onrender.com/health"
    exit 0
else
    echo -e "${RED}✗ Some configurations need attention!${NC}"
    echo "Please review the failed checks above."
    exit 1
fi
