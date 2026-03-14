# Output Formats

## Inline Chat Summary

```
DAST Scan: <target-url> — N findings, M info

FINDING  <template-id>          <V-ID> (<CAT>)  <description>
INFO     <template-id>          <V-ID> (<CAT>)  <description>
```

- FINDING = confirmed security issue
- INFO = informational (e.g., server header disclosure — may be acceptable)

## Pipeline Evidence Format

Compatible with `/static-analysis` pipeline format for `/stig-compliance`:

```json
{
  "tool": "nuclei",
  "version": "<nuclei-version>",
  "target": "<scanned-url>",
  "scope": "dast",
  "findings": [
    {
      "rule_id": "stig-header-no-csp",
      "v_id": "V-222602",
      "cat": "I",
      "category": "security-headers",
      "file": "http://localhost:5173",
      "line": 0,
      "message": "No Content-Security-Policy header in HTTP response",
      "severity": "ERROR",
      "snippet": "HTTP/1.1 200 OK\nContent-Type: text/html\n[no CSP header]"
    }
  ]
}
```

Note: `file` field contains the URL (not a file path) and `line` is always 0 for DAST findings.

## STIG Report Integration

In the compliance report (`docs/compliance/reports/`), DAST findings appear as:

```markdown
### FAIL: V-222596 — Protect confidentiality of transmitted info (CAT II)
**Source**: nuclei/stig-header-no-hsts (dynamic)
**Target**: http://localhost:5173
**Finding**: No Strict-Transport-Security header in response
**Remediation**: Add HSTS header: Strict-Transport-Security: max-age=31536000; includeSubDomains
```

Controls verified dynamically with no findings:

```markdown
### PASS: V-222577 — Do not expose session IDs (CAT I)
**Source**: nuclei/stig-cookie-httponly (dynamic)
**Evidence**: All Set-Cookie headers include HttpOnly and Secure flags
```
