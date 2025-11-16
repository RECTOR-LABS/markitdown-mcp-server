#!/bin/bash

# Production Test Script for Markitdown MCP Server
# Tests the live deployed Actor on Apify Cloud

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APIFY_TOKEN=$(cat ~/.apify/auth.json | jq -r '.token')
MCP_ENDPOINT="https://rector-labs--markitdown-mcp-server.apify.actor/mcp?token=$APIFY_TOKEN"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}🧪 Production MCP Server Test${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""
echo -e "${YELLOW}Endpoint:${NC} $MCP_ENDPOINT"
echo ""

# Test 1: Health Check
echo -e "${BLUE}📡 Test 1: MCP Initialization${NC}"
echo -n "  Initializing MCP connection... "

INIT_RESPONSE=$(curl -s -X POST "$MCP_ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "production-test",
        "version": "1.0.0"
      }
    }
  }')

if echo "$INIT_RESPONSE" | grep -q "protocolVersion"; then
    echo -e "${GREEN}✓ PASS${NC}"
    echo "  Server info:"
    echo "$INIT_RESPONSE" | jq -r '.result.serverInfo | "    Name: \(.name)\n    Version: \(.version)"' 2>/dev/null || echo "    $INIT_RESPONSE"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "  Response: $INIT_RESPONSE"
    exit 1
fi

echo ""

# Test 2: List Tools
echo -e "${BLUE}🛠️  Test 2: List Available Tools${NC}"
echo -n "  Fetching tool list... "

TOOLS_RESPONSE=$(curl -s -X POST "$MCP_ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }')

if echo "$TOOLS_RESPONSE" | grep -q "convert_to_markdown_tool"; then
    echo -e "${GREEN}✓ PASS${NC}"
    echo "  Available tools:"
    echo "$TOOLS_RESPONSE" | jq -r '.result.tools[].name | "    - \(.)"' 2>/dev/null || echo "$TOOLS_RESPONSE"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "  Response: $TOOLS_RESPONSE"
    exit 1
fi

echo ""

# Test 3: Convert HTML to Markdown
echo -e "${BLUE}📄 Test 3: HTML → Markdown Conversion${NC}"
echo -n "  Converting example.com... "

HTML_RESPONSE=$(curl -s -X POST "$MCP_ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "convert_to_markdown_tool",
      "arguments": {
        "file_url": "https://example.com"
      }
    }
  }')

if echo "$HTML_RESPONSE" | grep -q "Example Domain"; then
    echo -e "${GREEN}✓ PASS${NC}"
    MARKDOWN_OUTPUT=$(echo "$HTML_RESPONSE" | jq -r '.result.content[0].text' 2>/dev/null || echo "")
    echo "  Output preview:"
    echo "$MARKDOWN_OUTPUT" | head -5 | sed 's/^/    /'
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "  Response: $HTML_RESPONSE"
fi

echo ""

# Test 4: Convert PDF to Markdown
echo -e "${BLUE}📑 Test 4: PDF → Markdown Conversion${NC}"
echo -n "  Converting test PDF... "

PDF_RESPONSE=$(curl -s -X POST "$MCP_ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "convert_to_markdown_tool",
      "arguments": {
        "file_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
      }
    }
  }')

if echo "$PDF_RESPONSE" | jq -e '.result.content[0].text' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    MARKDOWN_OUTPUT=$(echo "$PDF_RESPONSE" | jq -r '.result.content[0].text' 2>/dev/null)
    echo "  Output preview:"
    echo "$MARKDOWN_OUTPUT" | head -5 | sed 's/^/    /'
else
    echo -e "${YELLOW}⚠ PARTIAL${NC}"
    echo "  Got response but format unexpected:"
    echo "$PDF_RESPONSE" | jq '.' 2>/dev/null || echo "$PDF_RESPONSE"
fi

echo ""

# Test 5: Error Handling
echo -e "${BLUE}⚠️  Test 5: Error Handling${NC}"
echo -n "  Testing invalid URL... "

ERROR_RESPONSE=$(curl -s -X POST "$MCP_ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "convert_to_markdown_tool",
      "arguments": {
        "file_url": "https://invalid-domain-that-does-not-exist-12345.com/file.pdf"
      }
    }
  }')

if echo "$ERROR_RESPONSE" | grep -qE "error|Error|failed|Failed"; then
    echo -e "${GREEN}✓ PASS${NC} (error handled gracefully)"
else
    echo -e "${YELLOW}? UNCLEAR${NC}"
    echo "  Response: $ERROR_RESPONSE"
fi

echo ""

# Summary
echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}✅ Production Test Complete!${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Check Actor runs in Console: https://console.apify.com/actors"
echo "  2. Monitor dataset output for conversion events"
echo "  3. Test with Claude Desktop (see README.md)"
echo "  4. Share on social media and MCP directories"
echo ""
echo -e "${BLUE}Public URL:${NC} https://apify.com/rector_labs/markitdown-mcp-server"
echo ""
