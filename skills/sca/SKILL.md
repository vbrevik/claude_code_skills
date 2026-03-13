---
name: sca
description: Software Composition Analysis — scan project dependencies for known vulnerabilities (CVEs) and generate Software Bill of Materials (SBOM). Uses Syft for SBOM generation and Grype for vulnerability matching. Falls back to npm audit when Syft/Grype unavailable. Produces STIG V-ID-tagged findings for /stig-compliance pipeline. Use when (1) auditing dependency security, (2) generating SBOM for compliance, (3) checking for vulnerable transitive dependencies, (4) license compliance for government procurement. Works air-gapped with pre-downloaded vulnerability database.
---

# Software Composition Analysis (SCA)

Dependency vulnerability scanning and SBOM generation with STIG pipeline integration.

## Invocation

- `/sca` — full scan: generate SBOM, scan for CVEs, report findings
- `/sca --sbom-only` — generate SBOM without vulnerability scan
- `/sca --licenses` — include license audit for government procurement compliance
- `/sca --json` — output pipeline JSON (for /stig-compliance consumption)

## Prerequisites

Check tool availability before scanning:

```bash
which syft && syft version || echo "syft not available"
which grype && grype version || echo "grype not available"
which npm && npm --version || echo "npm not available"
```

- **Preferred**: Syft (SBOM) + Grype (CVE scan) — full transitive dependency analysis
- **Fallback**: npm audit — npm projects only, limited to direct/transitive npm deps
- See `references/tools-setup.md` for installation instructions

## Scan Workflow

### Step 1: Generate SBOM

Run the SBOM generation script:

```bash
bash ~/.claude/skills/sca/scripts/run_sbom.sh <project-path> <output-sbom.json>
```

- Uses Syft if available: produces CycloneDX JSON with all transitive dependencies
- Falls back to parsing package-lock.json if Syft unavailable
- Output: CycloneDX JSON SBOM

### Step 2: Scan for Vulnerabilities

Skip this step if `--sbom-only` was requested.

```bash
bash ~/.claude/skills/sca/scripts/run_vuln_scan.sh <sbom.json> <output-vulns.json>
```

- Uses Grype if available: matches SBOM against CVE database
- Falls back to `npm audit --json` if Grype unavailable
- Output: vulnerability JSON (Grype format or npm audit format)

### Step 3: Convert to Pipeline Findings

```bash
python3 ~/.claude/skills/sca/scripts/grype_to_findings.py <vulns.json> [--json] [--npm-audit]
```

- Maps CVE severities to V-222551 (STIG automated vulnerability scanning rule)
- `--json` for pipeline output, default is human-readable table
- `--npm-audit` flag when input is npm audit JSON instead of Grype JSON

### Step 4: License Audit (if --licenses)

```bash
python3 ~/.claude/skills/sca/scripts/license_check.py <sbom.json>
```

- Flags GPL, AGPL, LGPL licenses for government procurement review
- Advisory only (no STIG V-ID, but relevant for compliance)

## Output Format

### Human-Readable (default)

```
SCA Vulnerability Scan: 3 findings

  CRITICAL  CVE-2024-1234   lodash@4.17.20       V-222551 (CAT I)    Fix: 4.17.21
  HIGH      CVE-2024-5678   express@4.18.0       V-222551 (CAT I)    Fix: 4.18.2
  MEDIUM    CVE-2024-9012   ws@8.0.0             V-222551 (CAT II)   Fix: 8.0.1
```

### Pipeline JSON (--json)

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
      "message": "Prototype Pollution in lodash",
      "file": "package-lock.json"
    }
  ]
}
```

See `references/output-formats.md` for full format documentation.

## STIG Integration

All CVE findings map to **V-222551** with CAT level based on severity:

| CVE Severity | STIG CAT | Action |
|-------------|----------|--------|
| Critical | CAT I | Must fix before deployment |
| High | CAT I | Must fix before deployment |
| Medium | CAT II | Fix within maintenance cycle |
| Low | CAT III | Track and remediate |

See `references/stig-rule-mappings.md` for full mapping details.

## Pipeline Integration with /stig-compliance

The JSON output from `grype_to_findings.py --json` feeds directly into `/stig-compliance review` as pipeline evidence. The findings array uses the same schema as `/static-analysis` output.

```bash
# Full pipeline: SBOM -> CVE scan -> findings
bash ~/.claude/skills/sca/scripts/run_sbom.sh . /tmp/sbom.json
bash ~/.claude/skills/sca/scripts/run_vuln_scan.sh /tmp/sbom.json /tmp/vuln-scan.json
python3 ~/.claude/skills/sca/scripts/grype_to_findings.py /tmp/vuln-scan.json --json > /tmp/sca-findings.json
```

## Air-Gap Operation

For RESTRICTED environments without internet access:

1. Pre-download Grype vulnerability database on connected machine
2. Transfer DB file via approved media
3. Configure `~/.claude/skills/sca/assets/grype-config.yaml` with `db.auto-update: false`
4. Point `GRYPE_DB_CACHE_DIR` to the pre-downloaded database location

See `references/tools-setup.md` for detailed air-gap setup.

## Limitations

- npm audit fallback only covers npm ecosystem (no Go, Python, Rust deps)
- SBOM from package-lock.json fallback may miss non-npm dependencies
- License check requires CycloneDX SBOM (Syft-generated preferred)
- Air-gap mode requires periodic manual DB updates
