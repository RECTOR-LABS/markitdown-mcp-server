# Deploy & Test Guide - Markitdown MCP Server on Apify Cloud

This guide shows you how to deploy to Apify Cloud and test using Apify's MCP infrastructure.

---

## 🚀 Step 1: Deploy to Apify Cloud

### Build and Deploy

```bash
# Make sure you're logged in
apify login

# Deploy the Actor
apify push
```

**Expected Output:**
```
Building Actor...
Uploading files...
Actor deployed successfully!
Actor URL: https://console.apify.com/actors/YOUR_ACTOR_ID
```

---

## 🔧 Step 2: Configure Standby Mode on Apify

After deployment, you need to enable standby mode:

### Option A: Via Apify Console (Web UI)

1. Go to: https://console.apify.com/actors
2. Find your **markitdown-mcp-server** Actor
3. Click on the Actor
4. Go to **Settings** tab
5. Scroll to **Standby mode** section
6. Enable **"Run in standby mode"**
7. Set:
   - **Memory**: 512 MB
   - **Timeout**: 600 seconds (10 minutes)
8. Click **Save**

### Option B: Via actor.json (Already configured)

Your `.actor/actor.json` already has:
```json
{
  "usesStandbyMode": true
}
```

But you still need to enable it in Console settings to activate it.

---

## 🌐 Step 3: Get Your MCP Endpoint URL

After enabling standby mode:

### Find Your Actor Username

```bash
# Get your Apify username
cat ~/.apify/auth.json | jq -r '.username'
```

**Your username:** `rector_labs`

### Your MCP Endpoint URL will be:

```
https://rector-labs--markitdown-mcp-server.apify.actor/mcp
```

**Format:**
```
https://{username}--{actor-name}.apify.actor/mcp
```

---

## 🧪 Step 4: Test the Deployed Actor

### Method 1: Using Apify MCP Test Client

Apify provides an official MCP test client. Install it:

```bash
npm install -g @apify/mcp-client
```

**Test your endpoint:**

```bash
apify-mcp-client \
  --url "https://rector-labs--markitdown-mcp-server.apify.actor/mcp" \
  --token "YOUR_APIFY_TOKEN"
```

This will:
1. Connect to your MCP server
2. List available tools
3. Let you test tool calls interactively

### Method 2: Using curl (HTTP API)

**Get your Apify token:**

```bash
cat ~/.apify/auth.json | jq -r '.token'
```

**Your token:** `YOUR_APIFY_TOKEN`

**Test MCP initialization:**

```bash
curl -X POST "https://rector-labs--markitdown-mcp-server.apify.actor/mcp" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_APIFY_TOKEN" \
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

**Expected response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "serverInfo": {
      "name": "Markitdown MCP Server",
      "version": "..."
    }
  }
}
```

**List available tools:**

```bash
curl -X POST "https://rector-labs--markitdown-mcp-server.apify.actor/mcp" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_APIFY_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

**Test document conversion:**

```bash
curl -X POST "https://rector-labs--markitdown-mcp-server.apify.actor/mcp" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_APIFY_TOKEN" \
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
  }' | jq -r '.result.content[0].text'
```

**Expected:** PDF content as clean Markdown

### Method 3: Using npx mcp-remote (No Install Needed)

```bash
npx -y mcp-remote \
  "https://rector-labs--markitdown-mcp-server.apify.actor/mcp" \
  --header "Authorization: Bearer YOUR_APIFY_TOKEN"
```

This will:
- Connect to your MCP server
- Show available tools
- Let you test interactively

---

## 🤖 Step 5: Test with Claude Desktop (Production)

### Configure Claude Desktop

Edit your Claude Desktop MCP config:

```bash
# macOS
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Add this configuration:**

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://rector-labs--markitdown-mcp-server.apify.actor/mcp",
        "--header",
        "Authorization: Bearer YOUR_APIFY_TOKEN"
      ]
    }
  }
}
```

**Restart Claude Desktop** and test:

```
Can you list your available tools?
```

You should see `convert_to_markdown_tool`.

**Test conversion:**

```
Please convert this PDF to markdown:
https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf
```

---

## 📊 Step 6: Monitor Actor Performance

### View Actor Runs

Go to Apify Console:
```
https://console.apify.com/actors/YOUR_ACTOR_ID/runs
```

You'll see:
- Active runs (standby mode keeps it running)
- Request logs
- Resource usage (memory, CPU)
- Billing events

### Check Logs

```bash
# View latest run logs
apify actor call YOUR_USERNAME/markitdown-mcp-server --logs
```

Or in Console:
1. Go to Actor runs
2. Click on latest run
3. View **Logs** tab

### Check Dataset Output

Your conversion events are stored in datasets:

```bash
# List datasets
apify datasets list

# Get latest dataset items
apify dataset get-items YOUR_DATASET_ID
```

**Expected output:**

```json
[
  {
    "event": "conversion_success",
    "file_size": 1234,
    "markdown_length": 567,
    "file_type": ".pdf"
  }
]
```

---

## 💰 Step 7: Verify Billing Events

### Check Pay-Per-Event Charges

Go to Console:
```
https://console.apify.com/actors/YOUR_ACTOR_ID/billing
```

You should see:
- **actor-start**: $0.01 per Actor start
- **document-conversion**: $0.02 per conversion

**Note:** On FREE tier, you might see a warning about pay-per-event pricing not being active. This is expected - billing will work once published to Store.

---

## 🔍 Step 8: Test Different Scenarios

### Test 1: PDF Conversion

```bash
curl -X POST "https://rector-labs--markitdown-mcp-server.apify.actor/mcp" \
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
  }' | jq
```

### Test 2: HTML Conversion

```bash
curl -X POST "https://rector-labs--markitdown-mcp-server.apify.actor/mcp" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_APIFY_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "convert_to_markdown_tool",
      "arguments": {
        "file_url": "https://example.com"
      }
    }
  }' | jq -r '.result.content[0].text'
```

### Test 3: Error Handling

```bash
curl -X POST "https://rector-labs--markitdown-mcp-server.apify.actor/mcp" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_APIFY_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "convert_to_markdown_tool",
      "arguments": {
        "file_url": "https://invalid-url.com/file.pdf"
      }
    }
  }' | jq
```

---

## 🚨 Troubleshooting

### Issue: "Actor not found"

**Cause:** Actor URL is incorrect or not published yet.

**Fix:**
1. Check your username: `cat ~/.apify/auth.json | jq -r '.username'`
2. Verify URL format: `https://{username}--{actor-name}.apify.actor/mcp`
3. Make sure Actor is deployed: `apify push`

### Issue: "403 Forbidden"

**Cause:** Missing or invalid Apify token.

**Fix:**
1. Get your token: `cat ~/.apify/auth.json | jq -r '.token'`
2. Add to request: `-H "Authorization: Bearer YOUR_TOKEN"`

### Issue: "500 Internal Server Error"

**Cause:** Actor crashed or standby mode not enabled.

**Fix:**
1. Check Actor logs in Console
2. Verify standby mode is enabled in Settings
3. Check memory limit (needs at least 512MB)

### Issue: "Timeout"

**Cause:** Large file or slow conversion.

**Fix:**
1. Increase timeout in Actor settings (default: 600s)
2. Test with smaller files first
3. Check file is publicly accessible

### Issue: "Billing events not showing"

**Cause:** FREE tier doesn't support pay-per-event yet.

**Fix:**
- This is expected on FREE tier
- Billing will activate once Actor is published to Store
- You can still test all functionality

---

## ✅ Success Checklist

After deployment and testing, verify:

- [ ] Actor deployed successfully (`apify push`)
- [ ] Standby mode enabled in Console
- [ ] MCP endpoint URL accessible
- [ ] MCP initialization works (curl test)
- [ ] Tools list returns `convert_to_markdown_tool`
- [ ] PDF conversion works
- [ ] HTML conversion works
- [ ] Error handling is graceful
- [ ] Claude Desktop can connect
- [ ] Conversion from Claude Desktop works
- [ ] Logs show successful conversions
- [ ] Dataset contains conversion events

---

## 📈 Next Steps After Testing

Once all tests pass:

1. **Optimize Actor listing** for Apify Store
2. **Add screenshots/demo** video
3. **Publish to Apify Store**
4. **Share on Twitter/LinkedIn** to attract users
5. **Monitor usage and revenue**
6. **Iterate based on user feedback**

---

## 🔗 Quick Links

- **Your Actor Console**: https://console.apify.com/actors
- **Your MCP Endpoint**: https://rector-labs--markitdown-mcp-server.apify.actor/mcp
- **Your Apify Token**: `YOUR_APIFY_TOKEN`
- **Apify MCP Docs**: https://docs.apify.com/platform/integrations/mcp

---

**Last Updated:** November 16, 2025
