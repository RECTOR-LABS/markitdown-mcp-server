# Markitdown MCP Server ⚡

> **Convert any document to AI-ready Markdown in seconds**
> Cloud-hosted Model Context Protocol server powered by Microsoft's Markitdown

[![Apify Platform](https://img.shields.io/badge/Built%20on-Apify-00ADD8?style=flat-square)](https://apify.com)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](https://www.python.org)
[![MCP Protocol](https://img.shields.io/badge/MCP-Compatible-green?style=flat-square)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

## 🎯 What is This?

**Markitdown MCP Server** is a cloud-hosted service that converts documents into clean, AI-optimized Markdown. Built on [Microsoft's Markitdown library](https://github.com/microsoft/markitdown) (82k+ ⭐), it eliminates the need for local Python installations and provides instant, scalable document conversion through the Model Context Protocol.

Perfect for **RAG pipelines**, **knowledge bases**, **AI agents**, and **document processing workflows**.

---

## ✨ Key Features

### 🚀 **Universal Format Support**
Convert **29+ file formats** to clean Markdown:
- **Documents**: PDF, DOCX, PPTX, XLSX
- **Images**: PNG, JPG, GIF (with OCR)
- **Web**: HTML, XML
- **Audio**: MP3, WAV (with transcription)
- **Archives**: ZIP (extract and convert contents)
- And many more!

### ☁️ **Zero Setup Required**
- No Python installation needed
- No dependency management
- No local configuration
- Just call the API and get Markdown

### 🎭 **MCP Native**
- First-class Model Context Protocol support
- Works seamlessly with Claude Desktop, Cursor, Aider
- AI agents can discover and use it automatically

### ⚡ **Lightning Fast**
- Direct Python library integration (no subprocess overhead)
- Typical conversion: **< 3 seconds**
- Cloud-scale infrastructure via Apify

### 💰 **Pay-Per-Use**
- $0.01 per Actor start
- $0.02 per document conversion
- No subscriptions, no minimums

---

## 🎬 Quick Start

### For AI Users (Claude Desktop)

1. **Add to MCP Configuration**

Create or edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://YOUR_ACTOR_URL.apify.actor/mcp",
        "--header",
        "Authorization: Bearer YOUR_APIFY_TOKEN"
      ]
    }
  }
}
```

2. **Restart Claude Desktop**

3. **Convert Documents**

Simply ask Claude:
```
"Convert this PDF to markdown: https://example.com/document.pdf"
```

Claude will automatically use the Markitdown tool!

---

### For Developers (API)

#### Direct HTTP Request

```bash
curl -X POST https://api.apify.com/v2/acts/YOUR_USERNAME~markitdown-mcp-server/runs \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fileUrl": "https://example.com/document.pdf"
  }'
```

#### Python Example

```python
from apify_client import ApifyClient

client = ApifyClient('YOUR_API_TOKEN')
run = client.actor('YOUR_USERNAME/markitdown-mcp-server').call(
    run_input={
        'fileUrl': 'https://example.com/document.pdf'
    }
)

# Get markdown output
for item in client.dataset(run['defaultDatasetId']).iterate_items():
    print(item['markdown'])
```

#### JavaScript/TypeScript Example

```typescript
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: 'YOUR_API_TOKEN' });

const run = await client.actor('YOUR_USERNAME/markitdown-mcp-server').call({
  fileUrl: 'https://example.com/document.pdf'
});

// Get markdown output
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items[0].markdown);
```

---

## 📚 Supported Formats

### Documents & Spreadsheets
| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Text extraction, OCR support |
| Word | `.docx`, `.doc` | Preserves formatting |
| PowerPoint | `.pptx`, `.ppt` | Slide text extraction |
| Excel | `.xlsx`, `.xls` | Table to Markdown |
| CSV | `.csv` | Table formatting |
| TSV | `.tsv` | Table formatting |

### Images
| Format | Extension | Notes |
|--------|-----------|-------|
| PNG | `.png` | OCR text extraction |
| JPEG | `.jpg`, `.jpeg` | OCR text extraction |
| GIF | `.gif` | OCR text extraction |
| BMP | `.bmp` | OCR text extraction |

### Web & Markup
| Format | Extension | Notes |
|--------|-----------|-------|
| HTML | `.html`, `.htm` | Clean conversion |
| XML | `.xml` | Structured data |
| Markdown | `.md` | Pass-through |

### Audio & Video
| Format | Extension | Notes |
|--------|-----------|-------|
| MP3 | `.mp3` | Speech-to-text transcription |
| WAV | `.wav` | Speech-to-text transcription |
| YouTube | URLs | Transcript extraction |

### Archives
| Format | Extension | Notes |
|--------|-----------|-------|
| ZIP | `.zip` | Extract and convert contents |

---

## 💡 Use Cases

### 🤖 RAG Pipelines
```
PDF Documents → Markitdown → Clean Markdown → Vector DB → LLM
```
Perfect for preparing documents for semantic search and retrieval.

### 📖 Knowledge Base Migration
Convert legacy documentation (PDFs, Word docs) to modern Markdown format for wikis, documentation sites, or content management systems.

### 🎓 Research & Academia
Extract text from research papers, presentations, and datasets for analysis and processing.

### 📊 Data Extraction
Convert invoices, reports, and spreadsheets into structured Markdown for further processing.

### 🔄 Batch Processing
Process hundreds of documents in parallel using Apify's infrastructure.

---

## 🔌 Integrations

### Claude Desktop
```json
{
  "mcpServers": {
    "markitdown": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://YOUR_ACTOR_URL.apify.actor/mcp",
        "--header",
        "Authorization: Bearer YOUR_APIFY_TOKEN"
      ]
    }
  }
}
```

### n8n Workflow
1. Add **Apify** node
2. Select **Markitdown MCP Server** actor
3. Configure file URL input
4. Connect to downstream nodes

### Make.com (Integromat)
1. Add **Apify** module
2. Select actor: `YOUR_USERNAME/markitdown-mcp-server`
3. Map file URL from trigger
4. Use output in next steps

### Zapier
1. Choose **Apify** app
2. Action: **Run Actor**
3. Actor: `markitdown-mcp-server`
4. Map data from previous steps

---

## ⚙️ Configuration

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fileUrl` | string | ✅ (or base64) | URL of the document to convert |
| `fileBase64` | string | ✅ (or URL) | Base64-encoded file content |

**Note**: Provide **either** `fileUrl` **or** `fileBase64`, not both.

### Example Inputs

**URL-based**:
```json
{
  "fileUrl": "https://example.com/document.pdf"
}
```

**Base64-based**:
```json
{
  "fileBase64": "JVBERi0xLjQKJeLjz9MKMyAwIG9iago8PC..."
}
```

---

## 📊 Output Format

The actor outputs clean Markdown text with metadata:

```json
{
  "event": "conversion_success",
  "file_size": 153600,
  "markdown_length": 5234,
  "file_type": ".pdf"
}
```

The Markdown content is returned as the tool response.

---

## 💲 Pricing

### Pay-Per-Event Model

| Event | Price | Description |
|-------|-------|-------------|
| Actor Start | $0.01 | One-time fee per Actor run |
| Document Conversion | $0.02 | Per successful conversion |

### Example Costs

- **Single document**: $0.03 total ($0.01 start + $0.02 conversion)
- **100 documents**: ~$2.10 ($0.01 start + $2.00 conversions)
- **1,000 documents**: ~$20.10 ($0.01 start + $20.00 conversions)

**No subscriptions. No minimums. Pay only for what you use.**

---

## 🚀 Performance

| Metric | Value |
|--------|-------|
| Average conversion time | **< 3 seconds** |
| Small files (< 1MB) | **< 2 seconds** |
| Large files (10MB+) | **< 10 seconds** |
| Concurrent processing | **Unlimited** (cloud-scaled) |
| Uptime | **99.95%** (Apify SLA) |

---

## 🛠️ Advanced Features

### Error Handling

The actor gracefully handles:
- Invalid file URLs (404, network errors)
- Unsupported file formats (clear error messages)
- Corrupted files (validation before processing)
- Large files (automatic timeout handling)

### Logging & Debugging

All conversions are logged with:
- File type and size
- Conversion duration
- Success/failure status
- Error details (if any)

### Custom Options

Coming soon:
- Azure Document Intelligence integration
- OpenAI image description
- Custom OCR settings
- Batch processing mode

---

## 🔒 Security & Privacy

- **No data retention**: Files are processed and immediately deleted
- **Encrypted transport**: All transfers use HTTPS
- **Isolated execution**: Each conversion runs in a sandboxed container
- **No logging of content**: Only metadata is logged
- **GDPR compliant**: Hosted on Apify's secure infrastructure

---

## ❓ FAQ

### **Q: What's the difference between this and running Markitdown locally?**

**A:** This is a **cloud-hosted** service with:
- ✅ No Python installation required
- ✅ No dependency management
- ✅ Automatic scaling for batch processing
- ✅ MCP integration for AI agents
- ✅ 99.95% uptime guarantee
- ✅ Pay-per-use (no server costs)

### **Q: Can I convert password-protected PDFs?**

**A:** Not currently. Password-protected documents will return an error. Remove protection before conversion.

### **Q: What's the maximum file size?**

**A:** **100 MB hard limit**. Files over 50 MB may take longer to process. For larger files, consider splitting them first.

### **Q: Does it work with scanned PDFs (images)?**

**A:** Yes! OCR (Optical Character Recognition) is supported for image-based PDFs and image files.

### **Q: Can I use this in production?**

**A:** Absolutely! The actor runs on Apify's production infrastructure with 99.95% uptime SLA.

### **Q: How accurate is the Markdown output?**

**A:** Markitdown preserves:
- ✅ Headings and structure
- ✅ **Bold** and *italic* formatting
- ✅ Lists (ordered and unordered)
- ✅ Tables
- ✅ Links
- ✅ Code blocks

Complex layouts may need manual review.

### **Q: Can I convert multiple files at once?**

**A:** Yes! Run multiple Actor instances in parallel, or use batch mode (contact for enterprise pricing).

---

## 🐛 Troubleshooting

### "File download failed: HTTP 404"

**Cause**: The URL is invalid or the file doesn't exist.

**Solution**:
- Verify the URL is correct and publicly accessible
- Ensure the file hasn't been deleted or moved
- Check for authentication requirements

### "Unsupported file format"

**Cause**: The file extension is not in the supported formats list.

**Solution**:
- Check the [Supported Formats](#-supported-formats) section
- Convert the file to a supported format first
- Contact support if you need a specific format added

### "Conversion timeout"

**Cause**: The file is too large or complex.

**Solution**:
- Split large files into smaller chunks
- Simplify complex documents
- Increase timeout (contact support for enterprise plans)

### "Invalid base64 content"

**Cause**: The base64 string is malformed or incomplete.

**Solution**:
- Verify base64 encoding is correct
- Ensure no truncation occurred during transfer
- Use `fileUrl` instead if possible

---

## 📖 Documentation

- **MCP Protocol**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Microsoft Markitdown**: [github.com/microsoft/markitdown](https://github.com/microsoft/markitdown)
- **Apify Platform**: [docs.apify.com](https://docs.apify.com)
- **Python SDK**: [docs.apify.com/sdk/python](https://docs.apify.com/sdk/python)

---

## 🤝 Support

### Need Help?

- 📧 **Email**: support@apify.com
- 💬 **Discord**: [apify.com/discord](https://apify.com/discord)
- 📚 **Documentation**: [docs.apify.com](https://docs.apify.com)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/RECTOR-LABS/markitdown-mcp-server/issues)

### Community

- ⭐ **Star on GitHub**: [RECTOR-LABS/markitdown-mcp-server](https://github.com/RECTOR-LABS/markitdown-mcp-server)
- 🐦 **Follow Updates**: [@apify](https://twitter.com/apify)
- 💡 **Feature Requests**: Open a GitHub issue

---

## 🚀 Get Started Now

### Deploy to Apify

1. **Log in to Apify**

```bash
apify login
```

2. **Deploy the Actor**

```bash
apify push
```

3. **Enable Standby Mode**

Go to Actor settings and enable standby mode.

4. **Get Your Actor URL**

Your MCP endpoint will be: `https://YOUR_USERNAME--markitdown-mcp-server.apify.actor/mcp`

5. **Connect AI Agents**

Add the endpoint to Claude Desktop, Cursor, or your favorite MCP client!

---

## 📜 License

This project is built on:
- **Microsoft Markitdown**: MIT License
- **Apify SDK**: Apache 2.0 License
- **MCP SDK**: MIT License

Actor code: MIT License

---

## 🙏 Credits

Built with:
- [Microsoft Markitdown](https://github.com/microsoft/markitdown) - Document conversion library (82k+ ⭐)
- [Apify Platform](https://apify.com) - Serverless cloud infrastructure
- [MCP Protocol](https://modelcontextprotocol.io) - AI agent integration standard

---

<p align="center">
  Made with ❤️ for the AI developer community
</p>

<p align="center">
  <a href="https://apify.com">Powered by Apify</a> •
  <a href="https://modelcontextprotocol.io">MCP Protocol</a> •
  <a href="https://github.com/microsoft/markitdown">Microsoft Markitdown</a>
</p>
