# Output Formats

## Inline Chat Summary (Default)

Human-readable table shown directly in conversation:

```
Secret Scan: <count> findings (gitleaks 8.x)

FINDING  <rule-id>          <v-id> (<cat>)    <file>:<line>    "<snippet>"
FINDING  <rule-id>          <v-id> (<cat>)    <file>:<line>    "<snippet>"
```

Snippets are truncated to 40 characters with sensitive content partially redacted.

If no findings:
```
Secret Scan: 0 findings (gitleaks 8.x) -- no secrets detected
```

## Pipeline JSON Format (--json)

Structured output for consumption by `/stig-compliance`:

```json
{
  "tool": "gitleaks",
  "version": "8.30.0",
  "scope": "git-history | git-diff | manual",
  "timestamp": "2026-03-13T10:00:00Z",
  "source_path": "/path/to/repo",
  "config": "assets/gitleaks.toml",
  "summary": {
    "total_findings": 2,
    "by_cat": { "I": 2, "II": 0, "III": 0 },
    "by_vid": { "V-222642": 1, "V-222543": 1 }
  },
  "findings": [
    {
      "rule_id": "generic-api-key",
      "v_id": "V-222642",
      "cat": "I",
      "title": "No embedded authenticators in application code",
      "file": "src/config.ts",
      "line": 12,
      "commit": "abc1234",
      "author": "dev@example.com",
      "date": "2026-03-10",
      "snippet": "X-API-Key = sk_live_****",
      "entropy": 4.2,
      "remediation": "Move to environment variable or secrets manager"
    },
    {
      "rule_id": "password-in-url",
      "v_id": "V-222543",
      "cat": "I",
      "title": "Transmission of credentials over encrypted channels",
      "file": "src/db.ts",
      "line": 8,
      "commit": "def5678",
      "author": "dev@example.com",
      "date": "2026-03-11",
      "snippet": "postgres://user:****@host/db",
      "entropy": 3.8,
      "remediation": "Use connection config with separate credential source"
    }
  ]
}
```

### Field Reference

| Field | Type | Description |
|---|---|---|
| `tool` | string | Always `"gitleaks"` |
| `version` | string | gitleaks version used |
| `scope` | string | `"git-history"`, `"git-diff"`, or `"manual"` |
| `timestamp` | string | ISO 8601 scan time |
| `source_path` | string | Repository root scanned |
| `config` | string | Config file used |
| `summary.total_findings` | number | Total finding count |
| `summary.by_cat` | object | Counts by STIG category |
| `summary.by_vid` | object | Counts by V-ID |
| `findings[].rule_id` | string | gitleaks rule that matched |
| `findings[].v_id` | string | Mapped STIG V-ID |
| `findings[].cat` | string | STIG category (I, II, III) |
| `findings[].file` | string | File path (relative to repo root) |
| `findings[].line` | number | Line number |
| `findings[].commit` | string | Git commit SHA (if from history scan) |
| `findings[].author` | string | Commit author (if from history scan) |
| `findings[].snippet` | string | Partially redacted match context |
| `findings[].entropy` | number | Shannon entropy of the matched secret |
| `findings[].remediation` | string | Suggested fix |
