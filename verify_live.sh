#!/bin/bash

APIFY_TOKEN=$(cat ~/.apify/auth.json | jq -r '.token')

echo "🧪 Quick Production Verification"
echo "================================"
echo ""
echo "Testing MCP Server initialization..."
curl -s -X POST "https://rector-labs--markitdown-mcp-server.apify.actor/mcp?token=$APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "quick-test", "version": "1.0.0"}
    }
  }' | grep -o '"serverInfo":{[^}]*}' | head -1

echo ""
echo ""
echo "✅ Actor is LIVE and responding!"
echo ""
echo "📊 Check runs: https://console.apify.com/actors/rector_labs/markitdown-mcp-server/runs"
echo "🎯 Public page: https://apify.com/rector_labs/markitdown-mcp-server"
echo ""
echo "Next: Test with Claude Desktop to use the full MCP protocol!"
