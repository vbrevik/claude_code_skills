---
name: secret-scan
description: Scan git repositories for leaked secrets (API keys, passwords, tokens, certificates) using gitleaks. Detects secrets in git history and current code. Produces STIG V-ID-tagged findings that feed into /stig-compliance as pipeline evidence. Use when (1) reviewing code changes for accidental secret commits, (2) auditing git history for previously committed secrets, (3) /stig-compliance review needs secret detection evidence. Works air-gapped.
---

# Secret Scan

Security scanning for leaked secrets using gitleaks. Integrates as a pipeline stage into `/stig-compliance`.

## Invocation

- `/secret-scan` — scan `git diff` (latest commit)
- `/secret-scan --full` — scan full git history
- `/secret-scan path/to/file.ts` — scan specific files or directories

## Prerequisites

Gitleaks must be installed. See `references/gitleaks-setup.md` if needed.

```bash
gitleaks version
```

If unavailable, the scan falls back to grep-based pattern detection and notes: "gitleaks unavailable — findings are grep-based, not comprehensive."

## Scan Workflow

### 1. Determine Scope

| Invocation | Scope | gitleaks flag |
|---|---|---|
| `/secret-scan` | Latest commit diff | `--log-opts="HEAD~1..HEAD"` |
| `/secret-scan --full` | Full git history | (default detect) |
| `/secret-scan <path>` | Specific path | `--no-git` on path |

### 2. Run Scan

```bash
bash <skill-path>/scripts/run_scan.sh <source-path> <skill-path>/assets/gitleaks.toml <output-json> [--full|--diff]
```

The script:
1. Checks gitleaks availability
2. Runs gitleaks with the custom config from `assets/gitleaks.toml`
3. Outputs JSON findings to the specified path
4. Falls back to grep-based detection if gitleaks is unavailable

### 3. Parse Findings

```bash
python3 <skill-path>/scripts/gitleaks_to_findings.py <output-json> [--json]
```

- Default: human-readable table for inline chat
- `--json`: pipeline JSON format for `/stig-compliance`

### 4. Report

#### Inline Chat Summary

```
Secret Scan: 3 findings (gitleaks 8.x)

FINDING  generic-api-key    V-222642 (CAT I)   src/config.ts:12      "X-API-Key = sk_live_..."
FINDING  private-key        V-222642 (CAT I)   deploy/cert.pem:1     "-----BEGIN RSA PRIVATE KEY-----"
FINDING  password-in-url    V-222543 (CAT I)   src/db.ts:8           "postgres://user:pass@..."
```

If no findings:

```
Secret Scan: 0 findings (gitleaks 8.x) -- no secrets detected
```

## STIG V-ID Mapping

All secret detection findings map to two primary STIG controls:

| V-ID | CAT | Title | Trigger |
|---|---|---|---|
| V-222642 | I | No embedded authenticators in application code | API keys, tokens, private keys, passwords in source |
| V-222543 | I | Transmission of credentials over encrypted channels | Passwords in URLs, connection strings with credentials |

See `references/stig-rule-mappings.md` for the complete rule-to-V-ID mapping.

## Pipeline: Feeding into /stig-compliance

When `/stig-compliance review` runs, it should invoke `/secret-scan` first:

1. Secret scan produces findings with V-ID tags
2. Each finding becomes automatic evidence for the matching V-ID:
   - gitleaks hit -> STIG control status = FAIL with file:line evidence
   - No hit -> control still gets semantic review
3. Report distinguishes tool-based vs semantic findings:

```markdown
### FAIL: V-222642 — Embedded authenticators in application code (CAT I)
**Source**: gitleaks/generic-api-key (deterministic)
**File**: src/config.ts:12
**Finding**: API key literal found in source code
**Remediation**: Move to environment variable or secrets manager
```

## Output Format

See `references/output-formats.md` for the pipeline JSON schema, matching the format used by `/static-analysis` and `/dast`.

## Project Overlay

Reuses `.claude/rules/stig-profile.md` if it exists (same as `/stig-compliance`):
- Excluded V-IDs skip corresponding findings
- Custom allowlist paths suppress known test fixtures

## Key Principles

- **Advisory, not blocking** — never prevent commits or builds
- **Deterministic first** — gitleaks findings are reproducible, not opinions
- **Pipeline, not replacement** — supplements semantic analysis in stig-compliance
- **Air-gap compatible** — custom config bundled, no network at runtime
- **History-aware** — can scan full git history, not just working tree
