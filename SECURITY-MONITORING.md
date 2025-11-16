# Security Monitoring Guide

## Overview

This guide provides instructions for monitoring security events and maintaining the security posture of the Markitdown MCP Server.

## Dependency Monitoring

### Automated CI/CD Scanning

The `.github/workflows/security.yml` workflow automatically:
- Scans dependencies weekly (Sundays at 2 AM UTC)
- Runs on every push and pull request
- Generates security reports as GitHub artifacts
- Fails build on critical vulnerabilities

### Manual Scanning

Run dependency scans locally:

```bash
# Install pip-audit
pip install pip-audit

# Scan for vulnerabilities
pip-audit -r requirements.txt --format=json

# Strict mode (fail on any vulnerability)
pip-audit -r requirements.txt --strict
```

### Monitoring pdfminer.six CVE (GHSA-f83h-ghpp-7wcc)

**Current Status**: No fix available

**Action Items**:
1. Subscribe to GitHub Security Advisories: https://github.com/pdfminer/pdfminer.six/security/advisories
2. Check weekly for updates:
   ```bash
   pip index versions pdfminer.six
   ```
3. Review release notes for security patches
4. When fix is available, update `requirements.txt`:
   ```
   # Add explicit version constraint for security fix
   pdfminer.six>=XXXX  # Version with CVE fix
   ```

## Security Event Logging

### Event Types to Monitor

The Actor logs security events to Apify datasets:

1. **`security_blocked_ssrf`** - SSRF attack attempt
   ```json
   {
     "event": "security_blocked_ssrf",
     "url": "http://169.254.169.254/...",
     "ip": "10.0.0.1",
     "timestamp": "2025-11-16T..."
   }
   ```

2. **`security_blocked_file_size`** - File size limit exceeded
   ```json
   {
     "event": "security_blocked_file_size",
     "url": "https://evil.com/huge.pdf",
     "size_attempted": 200000000,
     "max_size": 100000000
   }
   ```

3. **`security_blocked_base64_size`** - Base64 input too large
   ```json
   {
     "event": "security_blocked_base64_size",
     "size_attempted": 150000000,
     "max_size": 100000000
   }
   ```

4. **`security_blocked_content_type`** - Invalid Content-Type
   ```json
   {
     "event": "security_blocked_content_type",
     "url": "https://evil.com/malware.exe",
     "content_type": "application/x-msdownload"
   }
   ```

### Setting Up Alerts

#### Option 1: Apify Webhooks

Configure webhooks in Apify Console to trigger on security events:

```javascript
// Webhook filter for security events
if (data.event && data.event.startsWith('security_blocked_')) {
  // Send alert to Slack/Email/PagerDuty
  notifySecurityTeam(data);
}
```

#### Option 2: Log Aggregation (SIEM)

Export Apify dataset logs to SIEM tools:
- Datadog
- Splunk
- Elastic Stack (ELK)
- AWS CloudWatch

Example Datadog alert query:
```
event:security_blocked_ssrf OR event:security_blocked_file_size
```

## Metrics to Track

### Security Metrics

1. **SSRF Attempts**
   - Count of `security_blocked_ssrf` events
   - Alert threshold: > 10 per hour

2. **File Size Violations**
   - Count of `security_blocked_file_size` events
   - Alert threshold: > 50 per hour

3. **Failed Conversions**
   - Count of `conversion_error` events
   - Alert threshold: > 100 per hour

4. **Timeout Events**
   - Count of timeout errors
   - Alert threshold: > 20 per hour

### Apify Dataset Query Examples

```javascript
// Count SSRF attempts in last 24 hours
{
  "event": "security_blocked_ssrf",
  "timestamp": { "$gte": "2025-11-15T00:00:00Z" }
}

// Find repeated attackers
db.events.aggregate([
  { $match: { event: "security_blocked_ssrf" } },
  { $group: { _id: "$ip", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 }
])
```

## Container Security

### Regular Scans

Run Trivy scans weekly:

```bash
# Build image
docker build -t markitdown-mcp-server:latest .

# Scan for vulnerabilities
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image \
  --severity HIGH,CRITICAL \
  markitdown-mcp-server:latest
```

### Image Signing (Optional)

For production deployments, consider signing images:

```bash
# Using Docker Content Trust
export DOCKER_CONTENT_TRUST=1
docker push your-registry/markitdown-mcp-server:latest
```

## Incident Response

### Security Event Response Playbook

#### 1. SSRF Attack Detected

**Indicators**:
- Multiple `security_blocked_ssrf` events from same IP
- Attempts to access cloud metadata endpoints

**Actions**:
1. Review logs for source IP
2. Block IP at firewall/API gateway level
3. Check if any SSRF attempts succeeded (review conversion_success logs)
4. Verify SSRF protection is functioning correctly
5. Document incident

#### 2. Excessive File Size Attempts

**Indicators**:
- Repeated `security_blocked_file_size` events
- Potential DoS attack

**Actions**:
1. Identify source IP/user
2. Implement rate limiting at API gateway
3. Review if file size limits are appropriate
4. Consider temporary IP blocking

#### 3. Dependency Vulnerability

**Indicators**:
- CI/CD security scan fails
- New CVE announced for dependency

**Actions**:
1. Assess severity and exploitability
2. Check for available fixes
3. Update dependency if patch available
4. If no patch: assess risk and implement compensating controls
5. Document in SECURITY.md

## Compliance and Auditing

### Audit Log Retention

Configure Apify dataset retention:
- **Security events**: 90 days minimum
- **Conversion logs**: 30 days
- **Error logs**: 60 days

### Regular Security Reviews

Schedule quarterly reviews:
- [ ] Dependency vulnerability scan
- [ ] Container security scan
- [ ] Code security analysis (Bandit)
- [ ] Review security event logs
- [ ] Test SSRF protection
- [ ] Verify file size limits
- [ ] Check timeout configurations
- [ ] Review error messages for information leakage

### Compliance Checklist

- [ ] OWASP Top 10 compliance verified
- [ ] CWE Top 25 mitigations in place
- [ ] Security headers configured
- [ ] SSRF protection tested
- [ ] DoS protections tested
- [ ] Error handling reviewed
- [ ] Container runs as non-root
- [ ] Secrets excluded from image
- [ ] Security documentation up to date

## Emergency Contacts

### Security Incident

- **Primary**: [Your security team email]
- **Escalation**: [Manager/CTO email]
- **Apify Support**: support@apify.com

### CVE Reporting

- **Upstream (markitdown)**: https://github.com/microsoft/markitdown/security
- **Upstream (pdfminer.six)**: https://github.com/pdfminer/pdfminer.six/security

## Tools and Resources

### Security Tools
- `pip-audit`: Dependency vulnerability scanning
- `trivy`: Container vulnerability scanning
- `bandit`: Python code security analysis
- `safety`: Alternative dependency scanner

### Security Resources
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- CWE Top 25: https://cwe.mitre.org/top25/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework

---

**Last Updated**: November 16, 2025
**Next Review**: February 16, 2026
