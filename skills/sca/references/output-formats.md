# SCA Output Formats

## Pipeline JSON Format

Compatible with `/static-analysis` and `/stig-compliance` pipeline.

```json
{
  "tool": "grype",
  "scope": "project",
  "findings": [
    {
      "rule_id": "CVE-2024-1234",
      "v_id": "V-222551",
      "cat": "I",
      "category": "vulnerability-scanning",
      "package": "lodash",
      "installed_version": "4.17.20",
      "fixed_version": "4.17.21",
      "severity": "Critical",
      "message": "Prototype Pollution in lodash allows...",
      "file": "package-lock.json"
    }
  ]
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `tool` | string | `"grype"` or `"npm-audit"` depending on scanner used |
| `scope` | string | `"project"` for full scan |
| `findings` | array | List of vulnerability findings |
| `findings[].rule_id` | string | CVE identifier (e.g., `CVE-2024-1234`) or GHSA ID |
| `findings[].v_id` | string | Always `"V-222551"` for SCA findings |
| `findings[].cat` | string | `"I"`, `"II"`, or `"III"` based on CVE severity |
| `findings[].category` | string | Always `"vulnerability-scanning"` |
| `findings[].package` | string | Affected package name |
| `findings[].installed_version` | string | Currently installed version |
| `findings[].fixed_version` | string or null | Version with fix, or null if no fix available |
| `findings[].severity` | string | `Critical`, `High`, `Medium`, `Low` |
| `findings[].message` | string | Vulnerability description |
| `findings[].file` | string | Manifest file where dependency is declared |

## SBOM Output Format (CycloneDX JSON)

Syft generates CycloneDX 1.5 JSON. Key structure:

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "version": 1,
  "metadata": {
    "component": {
      "name": "visitor-mock",
      "type": "application"
    }
  },
  "components": [
    {
      "type": "library",
      "name": "express",
      "version": "4.18.2",
      "purl": "pkg:npm/express@4.18.2",
      "licenses": [
        { "license": { "id": "MIT" } }
      ]
    }
  ]
}
```

### Fallback SBOM (from package-lock.json)

When Syft is unavailable, the fallback script generates a simplified CycloneDX JSON:

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "version": 1,
  "metadata": {
    "component": {
      "name": "<project-name>",
      "type": "application"
    },
    "tools": [{ "name": "sca-fallback", "version": "1.0.0" }]
  },
  "components": [
    {
      "type": "library",
      "name": "express",
      "version": "4.18.2",
      "purl": "pkg:npm/express@4.18.2"
    }
  ]
}
```

Note: Fallback SBOM does not include license information (use Syft for license audit).

## License Report Format

```
License Audit: 245 dependencies scanned

  OK       MIT                  187 packages
  OK       Apache-2.0            23 packages
  OK       ISC                   18 packages
  OK       BSD-2-Clause           8 packages
  OK       BSD-3-Clause           5 packages
  WARNING  GPL-2.0                2 packages: node-sass, ...
  WARNING  AGPL-3.0               1 package: mongo-driver
  INFO     LGPL-2.1               1 package: libxml2

Flags: 3 (2 WARNING, 1 INFO)
```

## Human-Readable Table Format

Default output for terminal viewing:

```
SCA Vulnerability Scan: 5 findings (2 Critical, 1 High, 2 Medium)

  CRITICAL  CVE-2024-1234   lodash@4.17.20       V-222551 (CAT I)    Fix: 4.17.21
  CRITICAL  CVE-2024-2345   tar@6.1.0            V-222551 (CAT I)    Fix: 6.1.15
  HIGH      CVE-2024-5678   express@4.18.0       V-222551 (CAT I)    Fix: 4.18.2
  MEDIUM    CVE-2024-9012   ws@8.0.0             V-222551 (CAT II)   Fix: 8.0.1
  MEDIUM    CVE-2024-3456   semver@7.3.0         V-222551 (CAT II)   Fix: 7.5.2

Summary: 3 CAT I (block release), 2 CAT II (fix in maintenance cycle)
```
