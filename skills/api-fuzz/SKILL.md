---
name: api-fuzz
description: >
  Dynamic API security testing using OWASP OFFAT. Fuzzes API endpoints for auth bypass, input injection,
  schema violations, and information disclosure. Falls back to curl-based probe testing when OFFAT is
  unavailable. Produces STIG V-ID-tagged findings for /stig-compliance pipeline. Use when
  (1) testing API endpoints for auth boundary gaps, (2) validating input validation/sanitization,
  (3) checking error handling for information disclosure, (4) before deploying API changes.
  Requires running target server. Works air-gapped.
---

# API Fuzz Skill

Dynamic API security testing with OWASP OFFAT and curl-based fallback probes.

## Invocation

- `/api-fuzz <base-url>` -- fuzz all discovered endpoints
- `/api-fuzz <base-url> --spec <openapi.json>` -- fuzz endpoints from OpenAPI spec
- `/api-fuzz <base-url> --auth-only` -- test authentication/authorization bypasses only
- `/api-fuzz <base-url> --injection` -- test injection vulnerabilities only

## How It Works

### 1. Discover endpoints

If OpenAPI spec provided, parse it. Otherwise, scan code for route definitions (Convex function exports, Hono routes). List discovered endpoints.

### 2. Run OFFAT (if available)

```bash
bash ~/.claude/skills/api-fuzz/scripts/run_fuzz.sh <base-url> [openapi-spec] /tmp/api-fuzz-results.json
```

OFFAT performs:
- Authentication bypass attempts (missing/invalid/expired tokens)
- SQL injection payloads
- XSS payload injection
- SSRF path traversal
- Mass assignment/parameter pollution
- Schema violation (wrong types, overflow values, missing required fields)
- Broken Object Level Authorization (BOLA/IDOR)

### 3. Fallback (curl-based probes)

When OFFAT is unavailable, Claude generates and executes targeted curl commands testing:
- Unauthenticated access to protected endpoints
- Common injection patterns in query params and bodies
- Error response information disclosure
- CORS misconfiguration
- Missing security headers
- Rate limiting absence

### 4. Parse results

```bash
python3 ~/.claude/skills/api-fuzz/scripts/offat_to_findings.py /tmp/api-fuzz-results.json --json
```

### 5. Map to STIG V-IDs

All findings are tagged with DISA STIG V-IDs for pipeline integration:

| Test Category | V-ID | CAT | Description |
|--------------|------|-----|-------------|
| Auth bypass | V-222425 | I | Authentication required for all endpoints |
| Authorization (BOLA) | V-222425 | I | Object-level authorization |
| SQL injection | V-222578 | I | Input validation -- SQL |
| XSS | V-222577 | I | Input validation -- scripts |
| SSRF/path traversal | V-222604 | I | URL access restriction |
| Error disclosure | V-222602 | II | Error information leakage |
| Input validation | V-222606 | II | Input character restriction |
| Missing security headers | V-222543 | II | Transport security |
| CORS misconfiguration | V-222596 | II | Cross-origin policy |
| Rate limiting | V-222549 | II | Resource exhaustion |

See `references/stig-rule-mappings.md` for the complete mapping table.

### 6. Output format

Findings are emitted as pipeline-compatible JSON:

```json
{
  "tool": "api-fuzz",
  "scope": "<base-url>",
  "timestamp": "2026-03-13T10:00:00Z",
  "findings": [
    {
      "id": "AF-001",
      "rule_id": "auth-bypass",
      "v_id": "V-222425",
      "cat": "I",
      "category": "authentication",
      "endpoint": "POST /api/visits",
      "method": "POST",
      "severity": "HIGH",
      "message": "Endpoint accessible without authentication token",
      "request": "POST /api/visits HTTP/1.1\nHost: localhost:3210",
      "response_code": 200,
      "snippet": "Response returned visit data without auth header"
    }
  ],
  "summary": {
    "total": 5,
    "endpoints_tested": 24,
    "by_cat": {"I": 2, "II": 2, "III": 1},
    "by_category": {"authentication": 2, "injection": 1, "disclosure": 1, "headers": 1}
  }
}
```

## Integration with /stig-compliance

Output feeds into `/stig-compliance review` as dynamic evidence. Source attribution: `Source: offat (dynamic)`.

## Prerequisites

- **Required**: Running target server (e.g. `npm run dev:convex-unclass`)
- **Optional**: OFFAT (`pip install offat`) -- full fuzzing capability
- **Fallback**: curl (present on all systems) -- targeted probe testing
- **Optional**: OpenAPI spec file for comprehensive endpoint coverage

See `references/offat-setup.md` for installation instructions including air-gapped setup.
