# Installation Guide

> **Complete setup instructions for all MCP clients**

This guide covers installation for:
- [Claude Code CLI](#claude-code-cli) (Recommended)
- [Claude Desktop](#claude-desktop)
- [Cursor IDE](#cursor-ide)
- [VS Code](#vs-code)
- [Other MCP Clients](#other-mcp-clients)

---

## Prerequisites

Before installing, you'll need:

1. **Apify Account**: [Sign up for free](https://console.apify.com/sign-up)
2. **Apify API Token**: Get it from [Settings → Integrations](https://console.apify.com/account?tab=integrations)
3. **MCP Client**: Claude Code CLI, Claude Desktop, Cursor, or any MCP-compatible client

**Server URL**:
```
https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest
```

Or using the direct Actor URL:
```
https://rector-labs--markitdown-mcp-server.apify.actor/mcp
```

---

## Claude Code CLI

> **Recommended method** - Native MCP support with OAuth authentication

### Installation

**Method 1: OAuth Authentication (Easiest)**

```bash
# Add the server with HTTP transport
claude mcp add --transport http markitdown \
  https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest

# Authenticate (opens browser for OAuth login)
# In Claude Code, type:
/mcp
```

**Method 2: API Token Authentication**

```bash
# Using Apify API token (no OAuth needed)
claude mcp add --transport http markitdown \
  https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest \
  --header "Authorization: Bearer YOUR_APIFY_TOKEN"
```

### Configuration Scopes

Choose where to store the server configuration:

```bash
# Local (current project only) - DEFAULT
claude mcp add --transport http markitdown --scope local \
  https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest

# Project (shared with team, committed to git)
claude mcp add --transport http markitdown --scope project \
  https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest

# User (all projects on this machine)
claude mcp add --transport http markitdown --scope user \
  https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest
```

### Verification

```bash
# List all configured servers
claude mcp list

# View server details
claude mcp get markitdown

# Check connection status
# In Claude Code, type:
/mcp
```

### Management

```bash
# Remove the server
claude mcp remove markitdown

# Update configuration (remove and re-add)
claude mcp remove markitdown
claude mcp add --transport http markitdown <new-url>
```

### Team Collaboration

**Using Project Scope** (Recommended for teams):

1. Add to project scope:
```bash
claude mcp add --transport http markitdown --scope project \
  https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest \
  --header "Authorization: Bearer ${APIFY_TOKEN}"
```

2. This creates `.mcp.json` in your project root:
```json
{
  "mcpServers": {
    "markitdown": {
      "type": "http",
      "url": "https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest",
      "headers": {
        "Authorization": "Bearer ${APIFY_TOKEN}"
      }
    }
  }
}
```

3. Team members set their own token:
```bash
# macOS/Linux
export APIFY_TOKEN=your_token_here

# Windows (Command Prompt)
set APIFY_TOKEN=your_token_here

# Windows (PowerShell)
$env:APIFY_TOKEN="your_token_here"
```

4. Commit `.mcp.json` to git (tokens stay local via environment variables)

---

## Claude Desktop

> **Classic MCP client** - Manual JSON configuration

### Installation

**Step 1: Locate Configuration File**

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Step 2: Edit Configuration**

Open the file and add:

```json
{
  "mcpServers": {
    "markitdown": {
      "url": "https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest",
      "transport": {
        "type": "http",
        "headers": {
          "Authorization": "Bearer YOUR_APIFY_TOKEN"
        }
      }
    }
  }
}
```

**Using OAuth** (Recommended if available):

```json
{
  "mcpServers": {
    "markitdown": {
      "url": "https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest",
      "transport": {
        "type": "http"
      }
    }
  }
}
```

Then authenticate via Claude Desktop's UI.

**Step 3: Restart Claude Desktop**

Close and reopen Claude Desktop to load the new configuration.

### Verification

In Claude Desktop chat:
```
Can you convert this PDF to markdown: https://example.com/sample.pdf
```

Claude should recognize and use the `convert_to_markdown` tool.

---

## Cursor IDE

> **AI-powered IDE** - UI-based installation with one-click setup

### Method 1: One-Click Installation (If Published)

1. Open **Cursor Settings** → **Features** → **MCP Servers**
2. Search for **"Markitdown"**
3. Click **Install**
4. Click **Enable**
5. Look for green dot (connected status)

### Method 2: Manual Configuration

**Step 1: Enable MCP Servers**

1. Open **Cursor Settings** (Cmd/Ctrl + ,)
2. Navigate to **Cursor Settings** → **MCP Servers**
3. Toggle **Enable MCP Servers** to ON

**Step 2: Add Server**

1. Click **Add new MCP server**
2. Enter configuration:

```json
{
  "name": "markitdown",
  "url": "https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest",
  "type": "http",
  "headers": {
    "Authorization": "Bearer YOUR_APIFY_TOKEN"
  }
}
```

3. Click **Save** and **Enable**

**Step 3: Verify Connection**

- Look for a **green dot** next to "markitdown" (indicates connected)
- Click on the server to view available tools
- You should see `convert_to_markdown` listed

### Verification

In Cursor chat:
```
Use the markitdown tool to convert this document to markdown: https://example.com/sample.pdf
```

### Troubleshooting

**"Server failed to connect"**:
- Verify your Apify API token is correct
- Check that the Actor is deployed and running
- Try removing and re-adding the server

**"Too many tools warning"**:
- Cursor sends only the first 40 tools to the Agent
- If you have many MCP servers, some tools may be unavailable
- Disable unused servers to free up tool slots

---

## VS Code

> **Extensible editor** - Multiple installation methods via extensions

### Prerequisites

Install an MCP extension:
- **"MCP Tools"** (recommended)
- **"Smithery"** (one-click installation support)
- **Other MCP extensions** from VS Code marketplace

### Method 1: GitHub MCP Registry (If Published)

1. Navigate to the [GitHub MCP Registry](https://github.com/topics/mcp-server)
2. Search for "markitdown-mcp-server"
3. Click **Install in VS Code**
4. VS Code opens with pre-filled configuration
5. Confirm installation

### Method 2: Smithery CLI

```bash
# Install Smithery CLI
npm install -g @smithery/cli

# Install the server
smithery install markitdown-mcp-server
```

### Method 3: Manual Configuration

1. Open **VS Code Settings** (Cmd/Ctrl + ,)
2. Search for **"MCP"**
3. Click **Edit in settings.json**
4. Add:

```json
{
  "mcp.servers": {
    "markitdown": {
      "url": "https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest",
      "transport": "http",
      "auth": {
        "type": "bearer",
        "token": "YOUR_APIFY_TOKEN"
      }
    }
  }
}
```

5. Restart VS Code

### Verification

- Check the MCP extension's status bar
- Look for "markitdown" in the connected servers list
- Test by invoking the tool in an AI chat extension

---

## Other MCP Clients

> **Universal configuration** - Works with Windsurf, Zed, Desktop Commander, and more

Most MCP-compatible clients support HTTP transport. Refer to your client's documentation for specific configuration methods.

### General Configuration

**Server URL**:
```
https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest
```

Or using the direct Actor URL:
```
https://rector-labs--markitdown-mcp-server.apify.actor/mcp
```

**Authentication Header**:
```
Authorization: Bearer YOUR_APIFY_TOKEN
```

**Transport Type**: `http` or `https`

### Common Clients

#### Windsurf

Similar to Cursor configuration - check Windsurf docs for MCP setup.

#### Zed Editor

Add to Zed's MCP configuration (usually in `~/.config/zed/mcp.json`):

```json
{
  "servers": {
    "markitdown": {
      "url": "https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest",
      "headers": {
        "Authorization": "Bearer YOUR_APIFY_TOKEN"
      }
    }
  }
}
```

#### Desktop Commander

Refer to Desktop Commander's [MCP setup guide](https://desktopcommander.app/blog/2025/10/28/what-is-an-mcp-server-and-how-it-works-in-plain-english/).

---

## Testing the Connection

After installation, test with a simple conversion:

### In Claude Code CLI / Claude Desktop

```
Convert this PDF to Markdown: https://arxiv.org/pdf/2401.00001.pdf
```

### In Cursor / VS Code

```
Use the markitdown tool to convert this document: https://example.com/sample.pdf
```

### Expected Behavior

The AI assistant should:
1. Recognize the `convert_to_markdown` tool
2. Call the tool with the file URL
3. Return clean Markdown content

---

## Troubleshooting

### "Server failed to connect"

**Causes**:
- Invalid Apify API token
- Incorrect server URL
- Actor not deployed or not in standby mode
- Network/firewall issues

**Solutions**:
1. Verify your Apify API token:
   - Log in to [Apify Console](https://console.apify.com)
   - Go to **Settings → Integrations**
   - Copy a fresh token
2. Check the server URL matches exactly:
   ```
   https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest
   ```
3. Ensure the Actor is deployed and in **standby mode**:
   - Open the Actor in Apify Console
   - Check status shows "Ready" or "Running"
   - Enable standby mode if disabled
4. Test network connectivity:
   ```bash
   curl https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server
   ```

### "Tool not found" or "Tool not recognized"

**Causes**:
- MCP client hasn't loaded the server
- Server is configured but not enabled
- Client cache needs refresh

**Solutions**:
1. Restart your MCP client completely
2. Verify server is enabled (check client settings/status)
3. Run diagnostic commands:
   ```bash
   # Claude Code CLI
   claude mcp list
   claude mcp get markitdown

   # Check connection status
   /mcp
   ```
4. Check server status shows "connected" (green indicator)

### "Conversion timeout" or "Request timeout"

**Causes**:
- Large files (>50MB) take longer to process
- Network latency
- Actor cold start (first request after idle)

**Solutions**:
1. **For large files**: Split into smaller chunks
2. **Increase timeout** (if client allows):
   ```bash
   # Claude Code CLI
   MCP_TIMEOUT=30000 claude
   ```
3. **Wait for warm-up**: First request may take 10-15 seconds (Actor startup)
4. **Retry**: Subsequent requests are much faster (Actor stays warm)

### "Invalid authorization header"

**Causes**:
- Missing API token
- Incorrect header format
- Token expired or revoked

**Solutions**:
1. Verify header format:
   ```
   Authorization: Bearer YOUR_APIFY_TOKEN
   ```
   (Note the space after "Bearer")
2. Generate a new token from Apify Console
3. Update configuration with the new token
4. Restart the MCP client

### "Unsupported file format"

**Causes**:
- File extension not in supported list
- Malformed or corrupted file

**Solutions**:
1. Check [supported formats](README.md#-supported-formats)
2. Convert file to a supported format (e.g., DOCX → PDF)
3. Verify file is not corrupted (open it locally first)
4. Contact support if you need a specific format added

### "File download failed: HTTP 404"

**Causes**:
- Invalid URL
- File requires authentication
- File moved or deleted

**Solutions**:
1. Verify URL is correct and publicly accessible
2. Test URL in browser first
3. If file requires auth, use `fileBase64` instead:
   ```bash
   # Convert file to base64
   base64 document.pdf > document.b64

   # Send base64 content instead of URL
   ```

---

## Advanced Configuration

### Using Environment Variables

Store your Apify token securely in environment variables:

**macOS/Linux** (`~/.bashrc` or `~/.zshrc`):
```bash
export APIFY_TOKEN="your_token_here"
```

**Windows** (System Environment Variables):
```powershell
# PowerShell (persistent)
[System.Environment]::SetEnvironmentVariable('APIFY_TOKEN', 'your_token_here', 'User')
```

Then reference in configuration:
```json
{
  "headers": {
    "Authorization": "Bearer ${APIFY_TOKEN}"
  }
}
```

### Custom Timeout Settings

**Claude Code CLI**:
```bash
# Set timeout to 30 seconds
MCP_TIMEOUT=30000 claude
```

**Cursor IDE**:
Currently no custom timeout support - uses default client timeout.

### Multiple Environments

Use different tokens for dev/staging/production:

```bash
# Development
export APIFY_TOKEN_DEV="dev_token"

# Production
export APIFY_TOKEN_PROD="prod_token"
```

Reference in `.mcp.json`:
```json
{
  "mcpServers": {
    "markitdown-dev": {
      "url": "https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest",
      "headers": {
        "Authorization": "Bearer ${APIFY_TOKEN_DEV}"
      }
    },
    "markitdown-prod": {
      "url": "https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest",
      "headers": {
        "Authorization": "Bearer ${APIFY_TOKEN_PROD}"
      }
    }
  }
}
```

### Enterprise Deployments

For centralized management across teams:

**System-wide Configuration** (requires admin):

- **macOS**: `/Library/Application Support/ClaudeCode/managed-mcp.json`
- **Windows**: `C:\ProgramData\ClaudeCode\managed-mcp.json`
- **Linux**: `/etc/claude-code/managed-mcp.json`

Example:
```json
{
  "mcpServers": {
    "markitdown": {
      "type": "http",
      "url": "https://api.apify.com/v2/acts/rector_labs~markitdown-mcp-server/mcp/latest",
      "headers": {
        "Authorization": "Bearer ${APIFY_TOKEN}"
      }
    }
  }
}
```

**Access Control** (`managed-settings.json`):
```json
{
  "allowedMcpServers": [
    { "serverName": "markitdown" }
  ],
  "deniedMcpServers": [
    { "serverName": "filesystem" }
  ]
}
```

---

## Getting Help

### Documentation
- **MCP Protocol**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Apify MCP Guide**: [docs.apify.com/platform/integrations/mcp](https://docs.apify.com/platform/integrations/mcp)
- **Claude Code Docs**: [code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)

### Support Channels
- 📧 **Email**: support@apify.com
- 💬 **Discord**: [apify.com/discord](https://apify.com/discord)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/RECTOR-LABS/markitdown-mcp-server/issues)

### Community
- ⭐ **Star on GitHub**: [RECTOR-LABS/markitdown-mcp-server](https://github.com/RECTOR-LABS/markitdown-mcp-server)
- 💡 **Feature Requests**: Open a GitHub issue
- 🐦 **Follow Updates**: [@apify](https://twitter.com/apify)

---

## Next Steps

Once installed:
1. ✅ Test the connection with a sample document
2. ✅ Read the [Use Cases](README.md#-use-cases) guide
3. ✅ Explore [Advanced Features](README.md#-advanced-features)
4. ✅ Check [Pricing](README.md#-pricing) for cost planning
5. ✅ Join the [Discord community](https://apify.com/discord) for tips and support

Happy converting! 🚀
