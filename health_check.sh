
set -e

ENVIRONMENT_URL="${1:-http://localhost:8000}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
HEALTH_CHECK_FILE="health_check_log.txt"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "==============================================="
echo "BiasharaIQ Production Health Check"
echo "Environment: $ENVIRONMENT_URL"
echo "Timestamp: $TIMESTAMP"
echo "==============================================="
echo ""


check_endpoint() {
    local endpoint=$1
    local name=$2
    
    echo -n "Checking $name... "
    
    if response=$(curl -s -w "\n%{http_code}" "$ENVIRONMENT_URL$endpoint" 2>/dev/null); then
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | head -n-1)
        
        if [ "$http_code" = "200" ] || [ "$http_code" = "307" ]; then
            echo -e "${GREEN}✓ OK (HTTP $http_code)${NC}"
            return 0
        else
            echo -e "${RED}✗ FAILED (HTTP $http_code)${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ ERROR (Connection failed)${NC}"
        return 1
    fi
}

# Function to check database connection
check_database() {
    echo -n "Checking database connection... "
    
    # Make a request to an endpoint that uses the database
    if response=$(curl -s -X GET "$ENVIRONMENT_URL/health" 2>/dev/null); then
        if echo "$response" | grep -q "connected"; then
            echo -e "${GREEN}✓ Connected${NC}"
            return 0
        elif echo "$response" | grep -q "database"; then
            echo -e "${GREEN}✓ Available${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠ Unknown status${NC}"
            return 0
        fi
    else
        echo -e "${RED}✗ ERROR${NC}"
        return 1
    fi
}

# Function to check response time
check_response_time() {
    local endpoint=$1
    local name=$2
    
    echo -n "Checking $name response time... "
    
    if response_time=$(curl -s -o /dev/null -w "%{time_total}" "$ENVIRONMENT_URL$endpoint" 2>/dev/null); then
        response_time_ms=$(echo "$response_time * 1000" | bc | cut -d'.' -f1)
        
        if [ "$response_time_ms" -lt 500 ]; then
            echo -e "${GREEN}✓ ${response_time_ms}ms${NC}"
            return 0
        elif [ "$response_time_ms" -lt 1000 ]; then
            echo -e "${YELLOW}⚠ ${response_time_ms}ms${NC}"
            return 0
        else
            echo -e "${RED}✗ ${response_time_ms}ms (Slow)${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ ERROR${NC}"
        return 1
    fi
}

# Run health checks
FAILED_CHECKS=0

echo "API Endpoints:"
check_endpoint "/" "API Root" || ((FAILED_CHECKS++))
check_endpoint "/health" "Health Check" || ((FAILED_CHECKS++))
check_endpoint "/docs" "API Documentation" || ((FAILED_CHECKS++))

echo ""
echo "Database:"
check_database || ((FAILED_CHECKS++))

echo ""
echo "Performance:"
check_response_time "/" "API Response" || ((FAILED_CHECKS++))
check_response_time "/health" "Health Endpoint" || ((FAILED_CHECKS++))

echo ""
echo "==============================================="
if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}All checks passed ✓${NC}"
    EXIT_CODE=0
else
    echo -e "${RED}$FAILED_CHECKS check(s) failed ✗${NC}"
    EXIT_CODE=1
fi
echo "==============================================="

# Log results
echo "$TIMESTAMP - Checks passed: $((2 - FAILED_CHECKS)), Failed: $FAILED_CHECKS" >> "$HEALTH_CHECK_FILE"

exit $EXIT_CODE
