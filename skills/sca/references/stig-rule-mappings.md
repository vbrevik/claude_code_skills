# STIG Rule Mappings for SCA Findings

## Primary Rule: V-222551

**Title**: The application must employ automated vulnerability scanning tools.

**Source**: DISA ASD STIG V5R3 — Application Security and Development

All CVE findings from dependency scanning map to V-222551 with CAT level determined by CVE severity.

## Severity to CAT Mapping

| CVE Severity (CVSS) | STIG CAT Level | Remediation Timeline | Notes |
|---------------------|---------------|---------------------|-------|
| Critical (9.0-10.0) | CAT I | Must fix before deployment | Block release |
| High (7.0-8.9) | CAT I | Must fix before deployment | Block release |
| Medium (4.0-6.9) | CAT II | Fix within maintenance cycle | Track in backlog |
| Low (0.1-3.9) | CAT III | Track and remediate | Advisory |
| Negligible/None | — | No action | Informational only |

## npm audit Severity Mapping

npm audit uses its own severity scale. Mapping to STIG CAT:

| npm Severity | STIG CAT Level |
|-------------|---------------|
| critical | CAT I |
| high | CAT I |
| moderate | CAT II |
| low | CAT III |
| info | — (informational) |

## License Findings (Advisory)

License findings do not have a direct STIG V-ID but are relevant for government procurement compliance:

| License Type | Flag Level | Notes |
|-------------|-----------|-------|
| GPL-2.0, GPL-3.0 | WARNING | Copyleft — review for procurement compatibility |
| AGPL-3.0 | WARNING | Network copyleft — likely incompatible with government use |
| LGPL-2.1, LGPL-3.0 | INFO | Weak copyleft — usually acceptable for dynamic linking |
| Proprietary/Unknown | WARNING | Requires legal review |
| MIT, Apache-2.0, BSD | OK | Permissive — no procurement issues |
| ISC, Unlicense, 0BSD | OK | Permissive — no procurement issues |

## Pipeline Integration

When feeding SCA findings into `/stig-compliance`, the JSON output uses:

```json
{
  "rule_id": "<CVE-ID>",
  "v_id": "V-222551",
  "cat": "I|II|III",
  "category": "vulnerability-scanning",
  "package": "<package-name>",
  "installed_version": "<current-version>",
  "fixed_version": "<patched-version or null>",
  "severity": "<Critical|High|Medium|Low>",
  "message": "<CVE description>",
  "file": "package-lock.json"
}
```

This schema is compatible with the `/static-analysis` findings format used by `/stig-compliance review`.
