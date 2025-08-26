#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="https://zalo.truongvinhkhuong.io.vn"
LOCAL_URL="http://localhost:8001"

echo -e "${BLUE}🧪 Testing Zalo Webhook Endpoints${NC}"
echo "=================================="

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"
    local data="${4:-}"
    local headers="${5:-}"
    
    echo -e "\n${YELLOW}Testing: $name${NC}"
    echo "URL: $url"
    echo "Method: $method"
    
    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        echo "Data: $data"
    fi
    
    # Test local endpoint first
    echo -e "\n${BLUE}Local Test:${NC}"
    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        if [ -n "$headers" ]; then
            curl -s -X POST "$LOCAL_URL$url" -H "$headers" -d "$data" | head -5
        else
            curl -s -X POST "$LOCAL_URL$url" -d "$data" | head -5
        fi
    else
        curl -s "$LOCAL_URL$url" | head -5
    fi
    
    # Test production endpoint
    echo -e "\n${BLUE}Production Test:${NC}"
    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        if [ -n "$headers" ]; then
            curl -s -X POST "$BASE_URL$url" -H "$headers" -d "$data" | head -5
        else
            curl -s -X POST "$BASE_URL$url" -d "$data" | head -5
        fi
    else
        curl -s "$BASE_URL$url" | head -5
    fi
    
    echo -e "\n${GREEN}✓ Completed${NC}"
    echo "----------------------------------"
}

# Test 1: Health Check
test_endpoint "Health Check" "/health"

# Test 2: Dashboard (Root)
test_endpoint "Dashboard" "/"

# Test 3: Events List
test_endpoint "Events List" "/events"

# Test 4: Webhook Verification (GET)
test_endpoint "Webhook Verification" "/webhook?hub_challenge=test123&hub_verify_token=test_token"

# Test 5: Webhook POST (simulate event)
test_endpoint "Webhook POST" "/webhook" "POST" '{"event_name":"test_event","user_id":"test_user"}' "Content-Type: application/json"

echo -e "\n${GREEN}🎉 All endpoint tests completed!${NC}"
echo -e "\n${BLUE}Summary:${NC}"
echo "- Dashboard: $BASE_URL/"
echo "- Health Check: $BASE_URL/health"
echo "- Events: $BASE_URL/events"
echo "- Webhook: $BASE_URL/webhook"
echo -e "\n${YELLOW}Note:${NC} Some endpoints may return 404 or error responses if not properly configured."
echo "This is normal for webhook verification without proper tokens."
