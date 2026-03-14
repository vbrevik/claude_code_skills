# Output Formats

## Pipeline JSON Format

All container-security tools produce findings in this standard format, compatible with the `/stig-compliance` pipeline.

### Top-level structure

```json
{
  "tool": "container-security",
  "timestamp": "2026-03-13T10:00:00Z",
  "target": "/path/to/project",
  "scanner": "trivy|fallback",
  "findings": [ ... ],
  "summary": {
    "total": 12,
    "by_cat": {"I": 2, "II": 7, "III": 3},
    "by_severity": {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 6, "LOW": 3}
  }
}
```

### Finding object

```json
{
  "id": "CS-001",
  "stig_vid": "V-222548",
  "cat": "II",
  "title": "Container runs as root",
  "file": "packages/mocks/Dockerfile",
  "line": 1,
  "severity": "MEDIUM",
  "description": "No USER instruction found. Container will run as root by default.",
  "remediation": "Add USER <non-root-user> instruction after installing dependencies.",
  "source": "dockerfile-check"
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Check ID from stig-rule-mappings.md |
| `stig_vid` | string | yes | DISA STIG V-ID |
| `cat` | string | yes | CAT I, II, or III |
| `title` | string | yes | Short finding title |
| `file` | string | yes | Relative path to the file |
| `line` | int/null | no | Line number if applicable |
| `severity` | string | yes | CRITICAL, HIGH, MEDIUM, or LOW |
| `description` | string | yes | Detailed description |
| `remediation` | string | no | How to fix |
| `source` | string | yes | Scanner source identifier |

### Severity to CAT Mapping

| Severity | CAT |
|----------|-----|
| CRITICAL | I |
| HIGH | I |
| MEDIUM | II |
| LOW | III |
