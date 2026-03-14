---
name: dast
description: Run Dynamic Application Security Testing (DAST) using Nuclei against running web applications. Produces STIG V-ID-tagged findings from runtime behavior (security headers, TLS config, cookie flags, error disclosure, auth endpoints). Feeds into /stig-compliance as a dynamic evidence source alongside /static-analysis (SAST). Use when (1) a dev server is running and you want to verify runtime security posture, (2) /stig-compliance review needs dynamic evidence for controls that cannot be verified statically (headers, TLS, cookie attributes), (3) before deployment to check runtime security configuration. Requires a running target URL.
---

# DAST — Dynamic Application Security Testing

Runtime security scanning using Nuclei with STIG-mapped templates. Complements `/static-analysis` (SAST) by testing what the application actually does at runtime.

## What DAST Catches That SAST Cannot

| Check | SAST (semgrep) | DAST (nuclei) |
|-------|---------------|---------------|
| Missing security headers (CSP, HSTS, X-Frame) | No | Yes |
| TLS misconfiguration | No | Yes |
| Cookie flags (HttpOnly, Secure, SameSite) | Partial | Yes |
| Actual error page disclosure | No | Yes |
| Server version exposure | No | Yes |
| Debug endpoints left enabled | No | Yes |

## Invocation

- `/dast scan <url>` — scan a running application
- `/dast scan http://localhost:5173` — scan the portal dev server
- `/dast scan http://localhost:3000` — scan the OnGuard mock
- `/dast scan --all-dev` — scan all known dev server ports (5173, 3000, 3001, 3002)

## Prerequisites

Nuclei must be installed. See `references/nuclei-setup.md` if needed.

```bash
nuclei --version
```

If unavailable, fall back to `curl`-based header checks (reduced coverage) and note: "nuclei unavailable — using curl fallback, limited to header and TLS checks."

## Scan Workflow

### Process

1. **Confirm target** — always confirm the URL with the user before scanning. Never scan external/production URLs without explicit approval.

2. **Verify target is reachable:**
   ```bash
   curl -s -o /dev/null -w "%{http_code}" <url>
   ```
   If unreachable, report and stop.

3. **Run nuclei:**
   ```bash
   bash <skill-path>/scripts/run_scan.sh <url> <skill-path>/assets/nuclei-templates/
   ```

4. **Parse findings:**
   ```bash
   python3 <skill-path>/scripts/nuclei_to_findings.py <output-file>
   ```

5. **Report** — see `references/output-formats.md`

### Inline Chat Summary

```
DAST Scan: http://localhost:5173 — 3 findings, 1 info

FINDING  stig-header-no-csp        V-222602 (CAT I)   Missing Content-Security-Policy
FINDING  stig-cookie-no-httponly   V-222577 (CAT I)   Session cookie missing HttpOnly flag
FINDING  stig-header-no-hsts      V-222596 (CAT II)  Missing Strict-Transport-Security
INFO     stig-header-server       V-222610 (CAT II)  Server header exposes technology
```

## Pipeline: Feeding into /stig-compliance

When `/stig-compliance review` runs with a live server available:

1. DAST produces runtime findings with V-ID tags
2. Each finding becomes automatic evidence for the matching V-ID:
   - Nuclei hit → STIG control status = FAIL with evidence
   - No hit → control still gets semantic review
3. Report distinguishes source:

```markdown
### FAIL: V-222602 — XSS protection (CAT I)
**Source**: nuclei/stig-header-no-csp (dynamic)
**Target**: http://localhost:5173
**Finding**: No Content-Security-Policy header in response
**Remediation**: Add CSP header: Content-Security-Policy: default-src 'self'; script-src 'self'
```

## Three-Layer Pipeline

```
┌──────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ static-analysis │  │      dast        │  │  stig-compliance │
│ (semgrep/SAST) │  │  (nuclei/DAST)   │  │  (semantic/Claude)│
│ code patterns  │  │ runtime behavior │  │  contextual review│
└──────┬───────┘  └───────┬─────────┘  └────────┬────────┘
       │                  │                      │
       └──────────┬───────┘                      │
                  ▼                               │
        Tool-based evidence                       │
        (deterministic)                           │
                  └───────────────┬───────────────┘
                                 ▼
                    Unified STIG compliance report
                    docs/compliance/reports/
```

## Curl Fallback

When nuclei is unavailable, use curl-based checks for critical headers:

```bash
curl -sI <url> | grep -i "content-security-policy\|strict-transport\|x-frame-options\|x-content-type\|set-cookie"
```

Map results to V-IDs manually:
- Missing CSP → V-222602
- Missing HSTS → V-222596
- Missing X-Frame-Options → V-222602
- Cookie without HttpOnly/Secure → V-222577

Report as `Source: curl-fallback (limited dynamic)` in findings.

## Rule Reference

See `references/stig-rule-mappings.md` for the complete V-ID to nuclei template mapping.

## Project Overlay

Reuses `.claude/rules/stig-profile.md` if it exists:
- Known dev server ports
- Excluded V-IDs skip corresponding templates
- Custom headers that are expected (e.g., internal apps without HSTS)

## Key Principles

- **Advisory, not blocking** — never prevent commits or builds
- **Explicit targets only** — always confirm URL before scanning
- **Localhost only by default** — never scan external URLs without explicit approval
- **Air-gap compatible** — all templates bundled, no network for template updates
- **Pipeline evidence** — findings feed into stig-compliance alongside static-analysis
