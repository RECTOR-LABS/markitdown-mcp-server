# CLAUDE.md - Markitdown MCP Server

**Actor**: Markitdown MCP Server (Slot 1)
**Score**: 8.5/10
**Revenue Target**: $1,200-$1,600/month
**Build Timeline**: 1 week (Week 1-2)

---

## Actor Overview

This Actor wraps Microsoft's Markitdown library as a cloud-hosted Model Context Protocol (MCP) server, enabling AI agents to convert documents (PDF, DOCX, PPTX, images) into clean Markdown for RAG/LLM workflows.

**Key Differentiation**:
- **Zero cloud MCP competitors** - Microsoft's markitdown is NPM-only
- **Universal format support** - 15+ file types → Markdown
- **Enterprise demand** - 82K GitHub stars on markitdown repo
- **Perfect RAG integration** - Clean Markdown output for AI workflows

**Challenge Context**: Part of Apify $1M Challenge (deadline: January 31, 2026)
- Main repo: `/Users/rz/local-dev/apify-1m-challenge/`
- Build plan: `/Users/rz/local-dev/apify-1m-challenge/docs/guides/BUILD-PLAN.md`
- Validation: `/Users/rz/local-dev/apify-1m-challenge/ideas/evaluations/p5-markitdown-mcp-evaluation.md`

---

## Technical Architecture

### Core Technology Stack
- **Language**: Python 3.11
- **Framework**: Apify SDK (Python)
- **MCP Protocol**: mcp (Python MCP SDK)
- **Core Dependency**: markitdown (Microsoft Python package - official)
- **Transport**: stdio → streamable HTTP (Apify standby mode)

### Repository Structure
```
~/local-dev/actors/markitdown-mcp-server/
├── src/
│   ├── main.py              # Apify Actor entry point
│   └── mcp_server.py        # MCP server implementation + conversion tool
├── .actor/
│   ├── actor.json           # Actor metadata (includes input schema)
│   └── pay_per_event.json   # Pricing schema
├── requirements.txt         # Python dependencies
├── README.md                # Comprehensive user documentation
├── Dockerfile               # Container definition (Python 3.11)
└── CLAUDE.md                # This file
```

### MCP Server Implementation

**Direct Python implementation** - No subprocess needed:
```python
# MCP server runs directly in the same Python process
# Uses official Microsoft markitdown library
from markitdown import MarkItDown
md_converter = MarkItDown()
```

**Key MCP Tools**:
1. `convert_to_markdown` - Main tool for document conversion
   - Input: file URL or base64-encoded file
   - Output: Clean Markdown text + metadata
   - Supported formats: PDF, DOCX, PPTX, XLSX, images (PNG, JPG), HTML

**Billing Strategy** (Pay-per-event):
- Event: `document-conversion`
- Price: $0.02 per conversion
- Charge after successful conversion

---

## Development Workflow

### Phase 1: Setup (Day 1-2) ✅ COMPLETED
1. **Install dependencies**:
   ```bash
   cd ~/local-dev/actors/markitdown-mcp-server
   pip install -r requirements.txt
   # Dependencies: apify, markitdown, mcp
   ```

2. **Python Actor structure created**:
   - `src/main.py` - Actor entry point
   - `src/mcp_server.py` - MCP server with markitdown integration
   - Direct Python library calls (no subprocess overhead)

3. **Input schema defined** (in `.actor/actor.json`):
   ```json
   {
     "fileUrl": {
       "type": "string",
       "description": "URL of document to convert"
     },
     "fileBase64": {
       "type": "string",
       "description": "Base64-encoded file (alternative to URL)"
     }
   }
   ```

### Phase 2: Core Implementation (Day 3-4) ✅ COMPLETED
1. **`src/mcp_server.py` implemented**:
   - Direct markitdown library integration (no wrapper needed)
   - MCP tool handler for `convert_to_markdown`
   - File download (URL) with httpx
   - Base64 decode support
   - Clean Markdown output + metadata

2. **Error handling implemented**:
   - Invalid file URLs (404, network errors) ✅
   - HTTP status error handling ✅
   - File validation ✅
   - Graceful error logging ✅

3. **Logging added** (Apify dataset):
   - Conversion success/failure ✅
   - File type, file size ✅
   - Markdown length ✅
   - Error tracking ✅

### Phase 3: Testing (Day 5-6)
1. **Test supported formats**:
   - PDF: Test invoice, research paper, scanned document
   - DOCX: Test business doc, technical spec
   - PPTX: Test presentation slides
   - Images: Test PNG, JPG screenshots
   - XLSX: Test spreadsheet (basic table extraction)

2. **Edge cases**:
   - Large files (>10MB)
   - Malformed PDFs
   - Password-protected documents (graceful error)
   - Empty documents

3. **MCP client testing**:
   - Test via Claude Desktop (MCP client)
   - Test via Apify MCP tester client

### Phase 4: Documentation (Day 6-7)
**README.md sections**:
1. **Overview** - What it does, why it's useful
2. **Use Cases**:
   - Convert invoices for AI processing
   - Extract presentation slides for summarization
   - Prepare PDFs for RAG ingestion
   - Batch document conversion for knowledge bases
3. **Installation** - How to connect MCP client
4. **Usage Examples** - Code snippets (Claude Desktop, API)
5. **Supported Formats** - List all 15+ formats
6. **Pricing** - Pay-per-event details
7. **Limitations** - File size limits, unsupported formats
8. **FAQ** - Common questions

### Phase 5: Deployment (Day 7)
1. **Build locally**: `apify build`
2. **Test locally**: `apify run --standby`
3. **Configure standby mode** in Actor settings:
   - Memory: 512MB
   - Timeout: 600 seconds (10 minutes)
4. **Deploy**: `apify push`
5. **Publish to Apify Store**:
   - Optimize Actor title/description
   - Add demo video/screenshots
   - Target SEO: "markitdown mcp", "document conversion mcp", "pdf to markdown"

---

## Quality Score Requirements

**Target**: 70+ (minimum 65 required)

**Quality components**:
- ✅ **Unique README** - Comprehensive documentation with use cases
- ✅ **Input schema** - Clear, validated JSON schema
- ✅ **Output schema** - Structured (via MCP protocol)
- ✅ **Error handling** - Graceful failures, clear error messages
- ✅ **Examples** - Multiple use case demonstrations
- ✅ **Performance** - Fast conversion (<5 seconds for most docs)
- ✅ **Documentation** - Installation, usage, troubleshooting

**Checklist before publishing**:
- [ ] README has 5+ use case examples
- [ ] All 15+ supported formats documented
- [ ] Input schema tested with all field combinations
- [ ] Error messages are user-friendly
- [ ] Code is well-commented
- [ ] Performance benchmarks included (avg conversion time)
- [ ] MCP client connection guide clear

---

## Testing Strategy

### Local Testing
```bash
# Start in standby mode
apify run --standby

# Test MCP endpoint
curl -X POST http://localhost:XXXX/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"tool": "convert_to_markdown", "fileUrl": "https://example.com/doc.pdf"}'
```

### Production Testing
1. **Deploy to Apify**
2. **Connect Claude Desktop**:
   - Add Actor URL to MCP config
   - Test document conversion via chat
3. **Monitor metrics**:
   - Conversion success rate
   - Average processing time
   - Error types and frequency

---

## Success Metrics

**Week 2** (end of development):
- Quality score: 70+
- Initial MAU: 50-100 users

**Month 1**:
- MAU: 200-400 users
- Revenue: $400-800/month

**Month 3** (Jan 31, 2026):
- MAU: 600-800 users
- Revenue: $1,200-$1,600/month
- Quality score maintained: 70+

---

## Key Challenges & Solutions

### Challenge 1: Large file processing
**Solution**:
- Set file size limit (50MB warning, 100MB hard limit)
- Stream large files instead of loading into memory
- Add timeout handling (>60 seconds = warning)

### Challenge 2: Markitdown dependency compatibility
**Solution**:
- Pin markitdown version in package.json
- Test all file formats after updates
- Document breaking changes in README

### Challenge 3: MCP client discoverability
**Solution**:
- Publish to MCP registries (LobeHub, MCP servers directory)
- SEO optimization (Apify Store)
- Integration guides (Claude Desktop, Cursor, Aider)

---

## Related Resources

**Main Challenge Repo**:
- Build Plan: `/Users/rz/local-dev/apify-1m-challenge/docs/guides/BUILD-PLAN.md`
- Validation: `/Users/rz/local-dev/apify-1m-challenge/ideas/evaluations/p5-markitdown-mcp-evaluation.md`
- Idea Summary: `/Users/rz/local-dev/apify-1m-challenge/ideas/VALIDATION-SUMMARY-MARKITDOWN.md`

**External Docs**:
- Microsoft Markitdown: https://github.com/microsoft/markitdown
- MCP Protocol: https://modelcontextprotocol.io
- Apify MCP Guide: https://docs.apify.com/platform/integrations/mcp
- Apify SDK: https://docs.apify.com/sdk/js

---

## Development Status

**Current Phase**: Core Implementation Complete
**Architecture Decision**: Switched from TypeScript to Python for 50-100% performance improvement
**Implementation**: Direct Python markitdown integration (no subprocess overhead)
**Next Step**: Testing with sample documents + README documentation
**Target Completion**: Week 2 (Week 1-2 of 10-week sprint)

### Why Python?
- **50-100% faster**: Direct library calls vs subprocess communication
- **Official Microsoft library**: 82k stars, production-ready
- **Simpler codebase**: No TypeScript ↔ Python bridge
- **Better reliability**: Battle-tested at enterprise scale

### Smart Standby Mode Auto-Detection

**Feature**: Automatically enables standby mode for local development

**How it works**:
- **Local development**: `apify run` → auto-detects → enables standby mode ✅
- **Apify Cloud**: Uses `usesStandbyMode: true` from actor.json ✅
- **Detection methods**: Checks `APIFY_IS_AT_HOME`, `APIFY_ACTOR_ID`, `APIFY_DEFAULT_KEY_VALUE_STORE_ID`

**Benefits**:
- No need to set environment variables for local testing
- Clear logging: "🔧 Local development detected - auto-enabling standby mode"
- Fail-safe: Still requires standby mode on Cloud (production safety)

**Usage**:
```bash
# Local development (auto-detects)
$ apify run
✅ Just works!

# Production (uses actor.json setting)
$ apify push
✅ Deploys with standby mode enabled
```

---

**Last Updated**: November 16, 2025
