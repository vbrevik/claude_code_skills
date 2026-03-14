---
name: container-security
description: >
  Scan container images, Dockerfiles, docker-compose files, and Kubernetes manifests for security
  misconfigurations and vulnerabilities. Uses Trivy for image/IaC scanning and Kubescape for K8s
  policy compliance. Falls back to regex-based Dockerfile and K8s YAML analysis when tools are
  unavailable. Produces STIG V-ID-tagged findings for /stig-compliance pipeline. Use when
  (1) reviewing Docker or K8s configuration changes, (2) scanning container images for OS-level CVEs,
  (3) validating K8s RBAC and NetworkPolicy configuration, (4) before deployment. Works air-gapped
  with pre-downloaded vulnerability database.
---

# Container Security Skill

Scans Dockerfiles, docker-compose files, Kubernetes manifests, and container images for security misconfigurations and vulnerabilities.

## Invocation

- `/container-security` -- scan all Docker and K8s files in the project
- `/container-security docker` -- scan Dockerfiles and docker-compose files only
- `/container-security k8s` -- scan Kubernetes manifests only
- `/container-security image <name>` -- scan a built container image by name

## How It Works

### 1. Discover files

Find all relevant files in the project:
- `Dockerfile*` (any Dockerfile variant)
- `docker-compose*.yml` / `docker-compose*.yaml`
- `*.yaml` / `*.yml` in `k8s/` directories or containing K8s `apiVersion:` fields

Exclude `.worktrees/`, `node_modules/`, `.git/` directories.

### 2. Run scanners

Check tool availability and run the appropriate scanner:

```bash
# Check tools
which trivy && TRIVY=1 || TRIVY=0
which kubescape && KUBESCAPE=1 || KUBESCAPE=0
```

**If Trivy is available:**
```bash
bash ~/.claude/skills/container-security/scripts/run_trivy.sh <project-root> /tmp/container-scan.json
python3 ~/.claude/skills/container-security/scripts/trivy_to_findings.py /tmp/container-scan.json --json
```

**If Kubescape is available (K8s mode):**
```bash
bash ~/.claude/skills/container-security/scripts/run_kubescape.sh <k8s-dir> /tmp/kubescape-scan.json
```

**Fallback (no tools installed):**
```bash
python3 ~/.claude/skills/container-security/scripts/dockerfile_fallback.py <project-root>
```

### 3. Map to STIG V-IDs

All findings are tagged with DISA STIG V-IDs for pipeline integration:

| Check | V-ID | CAT |
|-------|------|-----|
| Running as root | V-222548 | II |
| No resource limits | V-222549 | II |
| No health check | V-222549 | III |
| Privileged container | V-222548 | I |
| No NetworkPolicy | V-222545 | II |
| No TLS/HTTPS | V-222543 | I |
| Hardcoded secrets in env | V-222642 | I |
| Latest tag used | V-222548 | II |
| No read-only rootfs | V-222548 | II |
| Base image CVEs | V-222551 | varies |

See `references/stig-rule-mappings.md` for the complete mapping table.

### 4. Output format

Findings are emitted as pipeline-compatible JSON:

```json
{
  "tool": "container-security",
  "timestamp": "2026-03-13T10:00:00Z",
  "target": "/path/to/project",
  "findings": [
    {
      "id": "CS-001",
      "stig_vid": "V-222548",
      "cat": "II",
      "title": "Container runs as root",
      "file": "packages/mocks/Dockerfile",
      "line": null,
      "severity": "MEDIUM",
      "description": "No USER instruction found. Container will run as root.",
      "remediation": "Add a USER instruction to run as a non-root user."
    }
  ],
  "summary": {
    "total": 5,
    "by_cat": {"I": 1, "II": 3, "III": 1},
    "by_severity": {"HIGH": 1, "MEDIUM": 3, "LOW": 1}
  }
}
```

## Prerequisites

- **Required:** Python 3.8+ (for fallback scanner and output formatting)
- **Optional:** Trivy (`brew install trivy` or binary install) -- IaC and image scanning
- **Optional:** Kubescape (`curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | bash`) -- K8s policy compliance
- **Optional:** Docker -- required only for image scanning mode

See `references/tools-setup.md` for installation instructions including air-gapped setup.

## Integration with /stig-compliance

Output JSON is compatible with the `/stig-compliance` pipeline. Findings can be merged with `/static-analysis` and `/dast` results for a unified compliance view.
