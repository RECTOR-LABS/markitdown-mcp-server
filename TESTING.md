# End-to-End Testing Guide - Markitdown MCP Server

This guide shows you how to test the Actor as a real user would experience it.

---

## Test Flow Overview

```
1. Start Actor → 2. Test MCP Endpoint → 3. Test Document Conversion → 4. Test with Claude Desktop
```

---

## Test 1: Start the Actor Locally

**Start the MCP server in standby mode:**

```bash
apify run
```

**Expected Output:**
```
✅ Local development detected - auto-enabling standby mode
✅ Starting Markitdown MCP Server on port 3001...
✅ MCP Server initialized with convert_to_markdown tool
✅ Uvicorn running on http://0.0.0.0:3001
```

**Verify it's running:**
```bash
# In another terminal
curl http://localhost:3001/health
```

---

## Test 2: Test MCP Protocol (List Available Tools)

**Test MCP endpoint to discover available tools:**

```bash
# Test MCP initialization
curl -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "serverInfo": {
      "name": "Markitdown MCP Server",
      "version": "..."
    }
  }
}
```

**List available tools:**

```bash
curl -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

**Expected Response:**
```json
{
  "tools": [
    {
      "name": "convert_to_markdown_tool",
      "description": "Convert documents (PDF, DOCX, PPTX, XLSX, images, etc.) to clean Markdown...",
      "inputSchema": {
        "type": "object",
        "properties": {
          "file_url": { "type": "string" },
          "file_base64": { "type": "string" }
        }
      }
    }
  ]
}
```

---

## Test 3: Test Document Conversion

### Test 3A: Convert from URL (PDF)

**Test with a public PDF:**

```bash
curl -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "convert_to_markdown_tool",
      "arguments": {
        "file_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
      }
    }
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Dummy PDF file\n\n..."
      }
    ]
  }
}
```

### Test 3B: Convert HTML to Markdown

```bash
curl -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "convert_to_markdown_tool",
      "arguments": {
        "file_url": "https://example.com"
      }
    }
  }'
```

### Test 3C: Convert from Base64

**Create a test file and convert:**

```bash
# Create a simple text file
echo "# Test Document\n\nThis is a test." > test.txt

# Convert to base64
BASE64_CONTENT=$(base64 < test.txt)

# Test conversion
curl -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 5,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"convert_to_markdown_tool\",
      \"arguments\": {
        \"file_base64\": \"$BASE64_CONTENT\"
      }
    }
  }"
```

---

## Test 4: Test with Real MCP Client (Claude Desktop)

### Step 1: Configure Claude Desktop

**Edit your MCP config:**

```bash
# macOS
code ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Or create if doesn't exist
mkdir -p ~/Library/Application\ Support/Claude
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "markitdown-local": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://localhost:3001/mcp"
      ]
    }
  }
}
EOF
```

### Step 2: Restart Claude Desktop

1. Quit Claude Desktop completely
2. Restart Claude Desktop
3. Look for MCP server connection indicator

### Step 3: Test in Claude Desktop

**Open Claude Desktop and ask:**

```
Can you list your available tools?
```

**Expected:** You should see `convert_to_markdown_tool` in the list.

**Test document conversion:**

```
Please convert this PDF to markdown:
https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf
```

**Expected:** Claude should use the tool and return the Markdown content.

---

## Test 5: Test Different File Formats

**Create a test script:**

```bash
cat > test_formats.sh << 'EOF'
#!/bin/bash

MCP_ENDPOINT="http://localhost:3001/mcp"

test_conversion() {
  local url=$1
  local format=$2

  echo "Testing $format conversion..."

  curl -s -X POST $MCP_ENDPOINT \
    -H "Content-Type: application/json" \
    -d "{
      \"jsonrpc\": \"2.0\",
      \"id\": 1,
      \"method\": \"tools/call\",
      \"params\": {
        \"name\": \"convert_to_markdown_tool\",
        \"arguments\": {
          \"file_url\": \"$url\"
        }
      }
    }" | jq -r '.result.content[0].text' | head -20

  echo "---"
}

# Test various formats (add real URLs)
test_conversion "https://example.com/sample.pdf" "PDF"
test_conversion "https://example.com/sample.docx" "DOCX"
test_conversion "https://example.com" "HTML"

EOF

chmod +x test_formats.sh
./test_formats.sh
```

---

## Test 6: Error Handling

**Test invalid URL:**

```bash
curl -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
      "name": "convert_to_markdown_tool",
      "arguments": {
        "file_url": "https://invalid-url-that-does-not-exist.com/file.pdf"
      }
    }
  }'
```

**Expected:** Should return clear error message about download failure.

**Test missing arguments:**

```bash
curl -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 7,
    "method": "tools/call",
    "params": {
      "name": "convert_to_markdown_tool",
      "arguments": {}
    }
  }'
```

**Expected:** Should return error about missing fileUrl or fileBase64.

---

## Test 7: Performance Testing

**Measure conversion time:**

```bash
time curl -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 8,
    "method": "tools/call",
    "params": {
      "name": "convert_to_markdown_tool",
      "arguments": {
        "file_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
      }
    }
  }'
```

**Expected:** Conversion should complete in < 3 seconds for small files.

---

## Test 8: Check Actor Logs

**View Actor logs during testing:**

```bash
# Logs are shown in the terminal where you ran `apify run`
# Look for:
# - "Downloading file from URL: ..."
# - "Converting file to Markdown (size: X bytes)"
# - "Conversion successful! Markdown length: X chars"
```

**Check dataset output:**

```bash
# After conversions, check stored data
ls -la storage/datasets/default/

# View conversion events
cat storage/datasets/default/*.json | jq
```

**Expected output:**

```json
{
  "event": "conversion_success",
  "file_size": 1234,
  "markdown_length": 567,
  "file_type": ".pdf"
}
```

---

## Test 9: Deploy & Test on Apify Cloud

**Deploy to Apify:**

```bash
apify push
```

**Get your Actor URL from Apify Console:**
```
https://YOUR_USERNAME--markitdown-mcp-server.apify.actor/mcp
```

**Test production endpoint:**

```bash
curl -X POST https://YOUR_USERNAME--markitdown-mcp-server.apify.actor/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_APIFY_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "convert_to_markdown_tool",
      "arguments": {
        "file_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
      }
    }
  }'
```

**Update Claude Desktop to use production:**

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://YOUR_USERNAME--markitdown-mcp-server.apify.actor/mcp",
        "--header",
        "Authorization: Bearer YOUR_APIFY_TOKEN"
      ]
    }
  }
}
```

---

## Troubleshooting

### Server won't start
- Check Python version: `python3 --version` (needs 3.11+)
- Reinstall dependencies: `pip3 install -r requirements.txt`
- Check port 3001 is available: `lsof -i :3001`

### MCP endpoint returns errors
- Verify server is in standby mode
- Check logs for detailed error messages
- Ensure file URL is publicly accessible

### Claude Desktop doesn't see the tool
- Verify MCP config JSON is valid
- Restart Claude Desktop completely
- Check server logs for connection attempts

### Conversion fails
- Check file format is supported
- Verify file URL is accessible (try wget/curl)
- Check file size (>100MB may timeout)

---

## Success Criteria

✅ **Basic Functionality:**
- [ ] Server starts successfully with `apify run`
- [ ] MCP endpoint responds to initialization
- [ ] Tools list includes `convert_to_markdown_tool`

✅ **Document Conversion:**
- [ ] PDF conversion works
- [ ] HTML conversion works
- [ ] Base64 input works
- [ ] Error handling is graceful

✅ **MCP Client Integration:**
- [ ] Claude Desktop recognizes the server
- [ ] Tool calls work from Claude Desktop
- [ ] Markdown output is clean and readable

✅ **Production Deployment:**
- [ ] Actor deploys successfully
- [ ] Production endpoint is accessible
- [ ] Billing events are tracked correctly

---

## Next Steps After Testing

1. **Document any issues** found during testing
2. **Fix bugs** and edge cases
3. **Optimize performance** if conversions are slow
4. **Deploy to Apify** with `apify push`
5. **Publish to Apify Store** for public access

---

**Last Updated:** November 16, 2025
