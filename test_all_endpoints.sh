#!/bin/bash

# Test all API endpoints
# Usage: ./test_all_endpoints.sh

BASE_URL="http://localhost:8000"
USER_ID="0x1aea8cf0dfe13ed3025910c88f7356935d76536c"

echo "=========================================="
echo "Testing All API Endpoints"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -n "Testing: $description ... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
    elif [ "$method" = "POST" ]; then
        if [ -n "$data" ]; then
            response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
                -H "Content-Type: application/json" \
                -d "$data")
        else
            response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint")
        fi
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL$endpoint")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ OK (${http_code})${NC}"
        return 0
    elif [ "$http_code" -ge 400 ] && [ "$http_code" -lt 500 ]; then
        echo -e "${YELLOW}⚠ Client Error (${http_code})${NC}"
        echo "  Response: $(echo "$body" | head -c 100)"
        return 1
    else
        echo -e "${RED}✗ Server Error (${http_code})${NC}"
        echo "  Response: $(echo "$body" | head -c 100)"
        return 1
    fi
}

# Test Users API
echo "=== Users API ==="
test_endpoint "GET" "/users/profile/$USER_ID" "" "Get user profile"
test_endpoint "POST" "/users/profile" "{\"user_id\":\"$USER_ID\",\"name\":\"Test User\",\"email\":\"test@example.com\",\"salary_monthly\":5000.0}" "Create user profile (may fail if exists)"

# Test Goals API
echo ""
echo "=== Goals API ==="
GOAL_DATA="{\"user_id\":\"$USER_ID\",\"name\":\"Test Goal\",\"target_amount\":10000.0,\"target_date\":\"2025-12-31\",\"current_savings\":1000.0,\"priority\":\"high\"}"
test_endpoint "POST" "/goals/" "$GOAL_DATA" "Create goal"
test_endpoint "GET" "/goals/$USER_ID" "" "List user goals"

# Test Finance API
echo ""
echo "=== Finance API ==="
test_endpoint "GET" "/finance/dashboard/$USER_ID?period=month" "" "Get finance dashboard"
test_endpoint "GET" "/finance/insights/$USER_ID" "" "Get insights"
test_endpoint "GET" "/finance/health-score/$USER_ID" "" "Get health score"
test_endpoint "GET" "/finance/predictions/$USER_ID" "" "Get predictions"
test_endpoint "GET" "/finance/budget-recommendations/$USER_ID" "" "Get budget recommendations"

# Test Gamification API
echo ""
echo "=== Gamification API ==="
test_endpoint "GET" "/gamification/stats/$USER_ID" "" "Get user stats"
test_endpoint "GET" "/gamification/leaderboard?limit=10" "" "Get leaderboard"
test_endpoint "GET" "/gamification/badges/$USER_ID" "" "Get user badges"
test_endpoint "POST" "/gamification/daily-login/$USER_ID" "" "Record daily login"

# Test Family API
echo ""
echo "=== Family API ==="
test_endpoint "GET" "/family/user/$USER_ID/families" "" "Get user families"

# Test Social API
echo ""
echo "=== Social API ==="
test_endpoint "GET" "/social/$USER_ID/percentile?period=month" "" "Get user percentile"
test_endpoint "GET" "/social/insights/$USER_ID?period=month" "" "Get social insights"

# Test Reports API
echo ""
echo "=== Reports API ==="
test_endpoint "POST" "/reports/generate/$USER_ID?period=month" "" "Generate report"
test_endpoint "GET" "/reports/$USER_ID/history?limit=10" "" "Get report history"

# Test Subscriptions API
echo ""
echo "=== Subscriptions API ==="
test_endpoint "GET" "/subscriptions/$USER_ID" "" "Get subscriptions"
test_endpoint "GET" "/subscriptions/$USER_ID/unused" "" "Get unused subscriptions"

# Test Reminders API
echo ""
echo "=== Reminders API ==="
test_endpoint "GET" "/reminders/$USER_ID" "" "Get reminders"
test_endpoint "GET" "/patterns/$USER_ID" "" "Get patterns"

# Test Voice API
echo ""
echo "=== Voice API ==="
test_endpoint "GET" "/voice/supported-formats" "" "Get supported formats"

# Test Email API
echo ""
echo "=== Email API ==="
test_endpoint "GET" "/email/example" "" "Get example email"

# Test Audit API
echo ""
echo "=== Audit API ==="
test_endpoint "GET" "/audit/user/$USER_ID/audits?limit=10" "" "Get user audits"
test_endpoint "GET" "/audit/user/$USER_ID/stats" "" "Get user audit stats"

echo ""
echo "=========================================="
echo "Testing Complete"
echo "=========================================="


