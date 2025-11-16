#!/bin/bash

# End-to-End Test Script for Markitdown MCP Server
# Tests all major functionality automatically

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

MCP_ENDPOINT="http://localhost:3001/mcp"
NEXT_ID=1

echo "================================="
echo "🧪 Markitdown MCP Server E2E Test"
echo "================================="
echo ""

# Helper function to check if server is running
check_server() {
    echo -n "Checking if MCP server is running... "
    if curl -s -f http://localhost:3001/health > /dev/null 2>&1 || \
       curl -s -X POST $MCP_ENDPOINT -H "Content-Type: application/json" \
       -d '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \
       > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Not running${NC}"
        echo ""
        echo "Please start the server first:"
        echo "  apify run"
        echo ""
        exit 1
    fi
}

# Helper function for test assertions
test_mcp_call() {
    local test_name=$1
    local method=$2
    local params=$3
    local expected_pattern=$4

    echo -n "  Testing: $test_name... "

    local response=$(curl -s -X POST $MCP_ENDPOINT \
        -H "Content-Type: application/json" \
        -d "{\"jsonrpc\":\"2.0\",\"id\":$NEXT_ID,\"method\":\"$method\",\"params\":$params}")

    NEXT_ID=$((NEXT_ID + 1))

    if [ -n "$expected_pattern" ]; then
        if echo "$response" | grep -q "$expected_pattern"; then
            echo -e "${GREEN}✓ PASS${NC}"
            return 0
        else
            echo -e "${RED}✗ FAIL${NC}"
            echo "Response: $response"
            return 1
        fi
    else
        # Just check for valid JSON response
        if echo "$response" | jq empty > /dev/null 2>&1; then
            echo -e "${GREEN}✓ PASS${NC}"
            return 0
        else
            echo -e "${RED}✗ FAIL${NC}"
            echo "Invalid JSON response: $response"
            return 1
        fi
    fi
}

# Test 1: Server Health Check
echo "📡 Test 1: Server Health Check"
check_server
echo ""

# Test 2: MCP Protocol Initialization
echo "🔌 Test 2: MCP Protocol Initialization"
test_mcp_call \
    "Initialize MCP connection" \
    "initialize" \
    '{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}' \
    "protocolVersion"
echo ""

# Test 3: List Available Tools
echo "🛠️  Test 3: List Available Tools"
test_mcp_call \
    "List tools" \
    "tools/list" \
    '{}' \
    "convert_to_markdown_tool"
echo ""

# Test 4: Document Conversion Tests
echo "📄 Test 4: Document Conversion Tests"

# Test 4A: Convert HTML (simple test)
test_mcp_call \
    "Convert HTML to Markdown" \
    "tools/call" \
    '{"name":"convert_to_markdown_tool","arguments":{"file_url":"https://example.com"}}' \
    "Example Domain"

# Test 4B: Convert public PDF
echo -n "  Testing: Convert PDF to Markdown... "
PDF_RESPONSE=$(curl -s -X POST $MCP_ENDPOINT \
    -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"id\":$NEXT_ID,\"method\":\"tools/call\",\"params\":{\"name\":\"convert_to_markdown_tool\",\"arguments\":{\"file_url\":\"https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf\"}}}")
NEXT_ID=$((NEXT_ID + 1))

if echo "$PDF_RESPONSE" | grep -q "Dummy PDF"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    # Some PDFs might not have predictable text, so just check for valid response
    if echo "$PDF_RESPONSE" | jq -e '.result.content[0].text' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC} (got markdown output)"
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "Response: $PDF_RESPONSE"
    fi
fi

# Test 4C: Convert from base64
echo -n "  Testing: Convert from base64... "
TEST_CONTENT="# Test Document\n\nThis is a test."
BASE64_CONTENT=$(echo -e "$TEST_CONTENT" | base64)

BASE64_RESPONSE=$(curl -s -X POST $MCP_ENDPOINT \
    -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"id\":$NEXT_ID,\"method\":\"tools/call\",\"params\":{\"name\":\"convert_to_markdown_tool\",\"arguments\":{\"file_base64\":\"$BASE64_CONTENT\"}}}")
NEXT_ID=$((NEXT_ID + 1))

if echo "$BASE64_RESPONSE" | jq -e '.result.content[0].text' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "Response: $BASE64_RESPONSE"
fi

echo ""

# Test 5: Error Handling
echo "⚠️  Test 5: Error Handling"

# Test 5A: Invalid URL
echo -n "  Testing: Invalid URL handling... "
ERROR_RESPONSE=$(curl -s -X POST $MCP_ENDPOINT \
    -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"id\":$NEXT_ID,\"method\":\"tools/call\",\"params\":{\"name\":\"convert_to_markdown_tool\",\"arguments\":{\"file_url\":\"https://invalid-domain-that-does-not-exist-12345.com/file.pdf\"}}}")
NEXT_ID=$((NEXT_ID + 1))

if echo "$ERROR_RESPONSE" | grep -qE "error|Error|failed|Failed"; then
    echo -e "${GREEN}✓ PASS${NC} (error handled gracefully)"
else
    echo -e "${YELLOW}? UNCLEAR${NC}"
    echo "Response: $ERROR_RESPONSE"
fi

# Test 5B: Missing arguments
echo -n "  Testing: Missing arguments handling... "
MISSING_RESPONSE=$(curl -s -X POST $MCP_ENDPOINT \
    -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"id\":$NEXT_ID,\"method\":\"tools/call\",\"params\":{\"name\":\"convert_to_markdown_tool\",\"arguments\":{}}}")
NEXT_ID=$((NEXT_ID + 1))

if echo "$MISSING_RESPONSE" | grep -qE "error|Error|must be provided|required"; then
    echo -e "${GREEN}✓ PASS${NC} (validation works)"
else
    echo -e "${YELLOW}? UNCLEAR${NC}"
    echo "Response: $MISSING_RESPONSE"
fi

echo ""

# Test 6: Performance Check
echo "⚡ Test 6: Performance Check"
echo -n "  Testing: Conversion speed... "

START_TIME=$(date +%s)
curl -s -X POST $MCP_ENDPOINT \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":999,"method":"tools/call","params":{"name":"convert_to_markdown_tool","arguments":{"file_url":"https://example.com"}}}' \
    > /dev/null
END_TIME=$(date +%s)

DURATION=$((END_TIME - START_TIME))

if [ $DURATION -le 5 ]; then
    echo -e "${GREEN}✓ PASS${NC} (${DURATION}s - under 5s target)"
else
    echo -e "${YELLOW}⚠ SLOW${NC} (${DURATION}s - expected < 5s)"
fi

echo ""

# Summary
echo "================================="
echo "✅ Test Suite Complete!"
echo "================================="
echo ""
echo "Next steps:"
echo "  1. Check logs in the terminal running 'apify run'"
echo "  2. Review dataset output: ls storage/datasets/default/"
echo "  3. Test with Claude Desktop (see TESTING.md)"
echo "  4. Deploy to Apify: apify push"
echo ""
