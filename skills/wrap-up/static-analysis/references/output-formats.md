# Output Formats

## Inline Chat Summary

Show after running review mode. Only show FINDINGs — summarize clean results as counts.

```
Static Analysis: N findings, M info

FINDING  <rule-id>          <V-ID> (<CAT>)  <file>:<line>
FINDING  <rule-id>          <V-ID> (<CAT>)  <file>:<line>
INFO     <rule-id>          <V-ID> (<CAT>)  <file>:<line>  [may be false positive]
```

- FINDING = high-confidence match
- INFO = pattern match that may be intentional (e.g., `innerHTML` in a sanitizer)

## Pipeline Evidence Format

When feeding into `/stig-compliance review`, structure findings as:

```json
{
  "tool": "semgrep",
  "version": "<semgrep-version>",
  "scope": "git-diff | full | manual",
  "findings": [
    {
      "rule_id": "stig-auth-no-bypass",
      "v_id": "V-222425",
      "cat": "I",
      "category": "auth",
      "file": "src/auth.ts",
      "line": 45,
      "message": "Authentication check bypassed via early return",
      "severity": "ERROR",
      "snippet": "if (skipAuth) return next();"
    }
  ]
}
```

## STIG Report Integration

In the STIG compliance report (`docs/compliance/reports/`), tool-based findings appear as:

```markdown
### FAIL: V-222425 — Enforce approved authorizations (CAT I)
**Source**: semgrep/stig-auth-no-bypass (deterministic)
**File**: src/auth.ts:45
**Finding**: Authentication check bypassed via early return
**Snippet**: `if (skipAuth) return next();`
**Remediation**: Remove bypass condition. All requests must pass through authorization checks.
```

Controls with no semgrep findings but reviewed semantically:

```markdown
### PASS: V-222474 — Audit records contain component info (CAT II)
**Source**: semantic review (Claude)
**Evidence**: All audit::log calls include component, action, and target fields
```
