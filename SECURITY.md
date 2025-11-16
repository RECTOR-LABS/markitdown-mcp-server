# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Security Features

This Actor implements multiple layers of security protection:

### 1. **SSRF (Server-Side Request Forgery) Protection**
- Blocks requests to private IP ranges (10.x.x.x, 192.168.x.x, 172.16-31.x.x)
- Blocks localhost (127.0.0.1, ::1)
- Blocks cloud metadata endpoints (169.254.169.254)
- Whitelist-based URL scheme validation (http/https only)
- DNS resolution validation before download

### 2. **Denial of Service Protection**
- File size limits: 100MB maximum
- Request timeouts: 60 seconds total, 10 seconds connect
- Streaming downloads (prevents memory exhaustion)
- Base64 input size validation

### 3. **Input Validation**
- Content-Type validation (whitelist-based)
- Base64 encoding validation
- URL format validation
- File extension verification via Content-Type headers

### 4. **Container Security**
- Non-root user execution (appuser)
- Minimal attack surface (.dockerignore excludes sensitive files)
- No secrets in image
- Python 3.11 with latest security patches

### 5. **Error Handling**
- Generic error messages (no information disclosure)
- Detailed logging for debugging (server-side only)
- Security event logging for monitoring

### 6. **HTTP Security Headers**
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Content-Security-Policy: default-src 'self'
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: restrictive

### 7. **Secure File Handling**
- Secure temporary directory creation
- Random file naming (prevents path traversal)
- Automatic cleanup (prevents disk exhaustion)
- No race conditions in temp file handling

## Known Vulnerabilities

### ⚠️ GHSA-f83h-ghpp-7wcc (pdfminer.six)
- **Component**: pdfminer.six (dependency of markitdown)
- **Severity**: High (CVSS 7.8)
- **Issue**: Insecure pickle deserialization in CMap loading
- **Status**: **No fix available yet** (as of Nov 2025)
- **Mitigation**:
  - Monitor upstream for security updates
  - Run in isolated container environment
  - Avoid untrusted CMAP_PATH directories
- **Impact**: Limited in cloud environment with proper container isolation

## Reporting a Vulnerability

If you discover a security vulnerability, please follow responsible disclosure:

1. **DO NOT** open a public GitHub issue
2. Email security details to: [Your security contact email]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

You can expect:
- Initial response within 48 hours
- Status update within 7 days
- Fix timeline communicated within 14 days

## Security Testing

Run security tests locally:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run security test suite
pytest tests/test_security.py -v

# Run dependency vulnerability scan
pip install pip-audit
pip-audit -r requirements.txt --strict

# Run container security scan
docker build -t markitdown-mcp-server:test .
docker run --rm aquasec/trivy image markitdown-mcp-server:test
```

## Security Best Practices for Users

When deploying this Actor:

1. **Network Isolation**: Deploy behind a firewall or VPC
2. **Rate Limiting**: Implement API gateway rate limiting
3. **Monitoring**: Set up alerts for security events:
   - `security_blocked_ssrf`
   - `security_blocked_file_size`
   - `security_blocked_content_type`
4. **Regular Updates**: Keep dependencies updated via `pip-audit`
5. **Access Control**: Restrict Actor access via Apify API tokens
6. **Logging**: Enable Apify dataset logging for audit trails

## Compliance

This Actor follows:
- **OWASP Top 10 2021** security guidelines
- **CWE Top 25** vulnerability mitigation
- **NIST Cybersecurity Framework** principles

## Security Changelog

### Version 0.1.0 (November 2025)
- ✅ Fixed CVE-2025-11849 (mammoth directory traversal)
- ✅ Implemented SSRF protection
- ✅ Added file size limits and timeouts
- ✅ Implemented secure temp file handling
- ✅ Added HTTP security headers
- ✅ Added Content-Type validation
- ✅ Sanitized error messages
- ✅ Non-root container execution
- ⚠️ Known issue: GHSA-f83h-ghpp-7wcc (pdfminer.six) - no fix available

## Contact

For security concerns: [Your contact information]

For general issues: https://github.com/[your-repo]/issues

---

**Last Updated**: November 16, 2025
