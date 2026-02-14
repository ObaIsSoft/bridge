#!/bin/bash
# set -e (Disabled to allow partial failures)

BASE_URL="http://localhost:8000/api/v1"
TARGET_URL="https://obafemiadebayo.vercel.app"
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}🔍 Starting End-to-End Verification for: ${TARGET_URL}${NC}"

# 1. Health Check
echo -e "\n1️⃣  Checking System Health..."
curl -s "${BASE_URL}/health" | python3 -m json.tool

# 2. Analyze URL (Schema Discovery)
echo -e "\n2️⃣  Analyzing Target URL (Schema Discovery)..."
ANALYSIS=$(curl -s -X POST "${BASE_URL}/bridges/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${TARGET_URL}\"}")
echo $ANALYSIS | python3 -m json.tool

# 3. Create Bridge
echo -e "\n3️⃣  Creating Bridge..."
BRIDGE_RESP=$(curl -s -X POST "${BASE_URL}/bridges" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Obafemi Portfolio\",
    \"domain\": \"obafemiadebayo.vercel.app\",
    \"target_url\": \"${TARGET_URL}\",
    \"extraction_schema\": {}
  }")
BRIDGE_ID=$(echo $BRIDGE_RESP | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo -e "   ✅ Bridge Created: ${BRIDGE_ID}"

# 4. Analyze Permissions (Ethical Moat)
# The permissions are fetched when getting the bridge details
echo -e "\n4️⃣  Verifying Ethical Moat (Permissions)..."
sleep 2 # Give DB a moment if async
BRIDGE_DETAILS=$(curl -s "${BASE_URL}/bridges/${BRIDGE_ID}")
echo $BRIDGE_DETAILS | python3 -m json.tool

# 5. Check Dashboard Stats
echo -e "\n5️⃣  Checking Dashboard Stats..."
curl -s "${BASE_URL}/bridges/stats" | python3 -m json.tool

echo -e "\n${GREEN}✅ Verification Complete!${NC}"
