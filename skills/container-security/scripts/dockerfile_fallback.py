#!/usr/bin/env python3
"""Regex-based Dockerfile, K8s YAML, and docker-compose security checker.

Fallback scanner for when Trivy/Kubescape are not installed.
Checks for common security misconfigurations and outputs pipeline-compatible JSON.

Usage:
    python3 dockerfile_fallback.py <project-root> [--json] [--mode docker|k8s|all]
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

EXCLUDE_DIRS = {".worktrees", "node_modules", ".git", "__pycache__", ".next", "dist"}

# Secret-like patterns in env values
SECRET_PATTERNS = re.compile(
    r"(PASSWORD|SECRET|TOKEN|API_KEY|PRIVATE_KEY|CREDENTIALS)\s*[:=]\s*['\"]?(?![\s'\"]*(admin|changeme|example|test|demo|placeholder|\$\{))[^\s'\"]+",
    re.IGNORECASE,
)

# HTTP URLs (non-TLS)
HTTP_URL_PATTERN = re.compile(r"http://(?!localhost|127\.0\.0\.1|host\.docker\.internal)")


def should_skip(path: str) -> bool:
    parts = Path(path).parts
    return any(p in EXCLUDE_DIRS for p in parts)


def find_files(root: str, mode: str = "all") -> dict[str, list[str]]:
    """Find Dockerfiles, docker-compose, and K8s manifests."""
    files = {"dockerfiles": [], "compose": [], "k8s": []}

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        for fname in filenames:
            full = os.path.join(dirpath, fname)

            if mode in ("all", "docker"):
                if fname.startswith("Dockerfile"):
                    files["dockerfiles"].append(full)
                if re.match(r"docker-compose.*\.(yml|yaml)$", fname):
                    files["compose"].append(full)

            if mode in ("all", "k8s"):
                if fname.endswith((".yaml", ".yml")) and "k8s" in dirpath.split(os.sep):
                    files["k8s"].append(full)

    return files


# ---------------------------------------------------------------------------
# Dockerfile checks
# ---------------------------------------------------------------------------

def check_dockerfile(filepath: str, project_root: str) -> list[dict]:
    findings = []
    rel = os.path.relpath(filepath, project_root)

    try:
        with open(filepath) as f:
            content = f.read()
            lines = content.splitlines()
    except (OSError, UnicodeDecodeError):
        return findings

    # CS-001: No USER instruction (runs as root)
    has_user = False
    user_is_root = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.upper().startswith("USER "):
            has_user = True
            user_val = stripped.split(None, 1)[1].strip() if len(stripped.split(None, 1)) > 1 else ""
            if user_val in ("root", "0"):
                user_is_root = True
                findings.append({
                    "id": "CS-001",
                    "stig_vid": "V-222548",
                    "cat": "II",
                    "title": "Container runs as root",
                    "file": rel,
                    "line": i + 1,
                    "severity": "MEDIUM",
                    "description": "USER instruction explicitly sets root user.",
                    "remediation": "Change to a non-root user: USER appuser",
                    "source": "dockerfile-check",
                })

    if not has_user:
        findings.append({
            "id": "CS-001",
            "stig_vid": "V-222548",
            "cat": "II",
            "title": "Container runs as root",
            "file": rel,
            "line": None,
            "severity": "MEDIUM",
            "description": "No USER instruction found. Container will run as root by default.",
            "remediation": "Add USER <non-root-user> after installing dependencies.",
            "source": "dockerfile-check",
        })

    # CS-002: Latest tag or no tag on FROM
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.upper().startswith("FROM "):
            image_ref = stripped.split()[1] if len(stripped.split()) > 1 else ""
            # Skip scratch and build aliases
            if image_ref in ("scratch",):
                continue
            if image_ref.endswith(":latest") or (":" not in image_ref and "@" not in image_ref):
                findings.append({
                    "id": "CS-002",
                    "stig_vid": "V-222548",
                    "cat": "II",
                    "title": "Base image uses latest/untagged",
                    "file": rel,
                    "line": i + 1,
                    "severity": "MEDIUM",
                    "description": f"FROM {image_ref} uses latest or no tag. Pin to a specific version.",
                    "remediation": "Pin the base image to a specific version tag or digest.",
                    "source": "dockerfile-check",
                })

    # CS-003: ADD instead of COPY
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.upper().startswith("ADD ") and not stripped.startswith("ADD --chown"):
            # ADD is ok for .tar.gz extraction, check if it looks like a URL or tar
            args = stripped.split(None, 1)[1] if len(stripped.split(None, 1)) > 1 else ""
            if "http://" in args or "https://" in args:
                findings.append({
                    "id": "CS-003",
                    "stig_vid": "V-222548",
                    "cat": "II",
                    "title": "ADD fetches remote URL",
                    "file": rel,
                    "line": i + 1,
                    "severity": "MEDIUM",
                    "description": "ADD with URL can introduce unverified content. Use COPY + curl/wget instead.",
                    "remediation": "Replace ADD with RUN curl/wget + COPY for remote files.",
                    "source": "dockerfile-check",
                })

    # CS-004: No HEALTHCHECK
    if "HEALTHCHECK" not in content.upper():
        # Only flag single-stage or final-stage Dockerfiles
        from_count = sum(1 for l in lines if l.strip().upper().startswith("FROM "))
        # For multi-stage, only flag if final stage has no HEALTHCHECK
        findings.append({
            "id": "CS-004",
            "stig_vid": "V-222549",
            "cat": "III",
            "title": "No HEALTHCHECK defined",
            "file": rel,
            "line": None,
            "severity": "LOW",
            "description": "No HEALTHCHECK instruction. Container health cannot be monitored.",
            "remediation": "Add HEALTHCHECK CMD curl -f http://localhost:<port>/health || exit 1",
            "source": "dockerfile-check",
        })

    # CS-005: Secrets in ENV/ARG
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.upper().startswith(("ENV ", "ARG ")):
            if SECRET_PATTERNS.search(stripped):
                findings.append({
                    "id": "CS-005",
                    "stig_vid": "V-222642",
                    "cat": "I",
                    "title": "Potential secret in ENV/ARG",
                    "file": rel,
                    "line": i + 1,
                    "severity": "HIGH",
                    "description": "ENV/ARG instruction may contain a secret value. Use build secrets or runtime injection.",
                    "remediation": "Use Docker build secrets (--mount=type=secret) or runtime environment variables.",
                    "source": "dockerfile-check",
                })

    return findings


# ---------------------------------------------------------------------------
# Kubernetes manifest checks
# ---------------------------------------------------------------------------

def check_k8s_manifest(filepath: str, project_root: str) -> list[dict]:
    findings = []
    rel = os.path.relpath(filepath, project_root)

    try:
        with open(filepath) as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return findings

    # Split multi-document YAML
    docs = content.split("\n---")

    for doc in docs:
        lines = doc.splitlines()

        # Detect if this is a workload (Deployment, StatefulSet, DaemonSet, Pod, Job)
        is_workload = bool(re.search(r"kind:\s*(Deployment|StatefulSet|DaemonSet|Pod|Job|CronJob)", doc))

        if not is_workload:
            continue

        # Extract resource name for better reporting
        name_match = re.search(r"^\s*name:\s*(\S+)", doc, re.MULTILINE)
        resource_name = name_match.group(1) if name_match else "unknown"

        # CS-010: Privileged container
        if re.search(r"privileged:\s*true", doc):
            findings.append({
                "id": "CS-010",
                "stig_vid": "V-222548",
                "cat": "I",
                "title": f"Privileged container: {resource_name}",
                "file": rel,
                "line": _find_line(lines, r"privileged:\s*true"),
                "severity": "CRITICAL",
                "description": "Container runs in privileged mode with full host access.",
                "remediation": "Remove privileged: true. Use specific capabilities if needed.",
                "source": "k8s-check",
            })

        # CS-011/012: Resource limits/requests
        containers = re.findall(r"containers:\s*\n((?:\s+- .*\n|\s+\w.*\n)*)", doc)
        if containers:
            container_block = containers[0]
            if "limits:" not in container_block and "limits:" not in doc.split("containers:")[1] if "containers:" in doc else True:
                findings.append({
                    "id": "CS-011",
                    "stig_vid": "V-222549",
                    "cat": "II",
                    "title": f"No resource limits: {resource_name}",
                    "file": rel,
                    "line": None,
                    "severity": "MEDIUM",
                    "description": "Container has no resource limits. Can consume unbounded resources.",
                    "remediation": "Add resources.limits.cpu and resources.limits.memory.",
                    "source": "k8s-check",
                })

        # CS-013: runAsNonRoot not set
        if "runAsNonRoot: true" not in doc and "runAsUser:" not in doc:
            findings.append({
                "id": "CS-013",
                "stig_vid": "V-222548",
                "cat": "II",
                "title": f"May run as root: {resource_name}",
                "file": rel,
                "line": None,
                "severity": "MEDIUM",
                "description": "Neither runAsNonRoot nor runAsUser set. Container may run as root.",
                "remediation": "Add securityContext.runAsNonRoot: true or runAsUser: <non-zero>.",
                "source": "k8s-check",
            })

        # CS-014: No read-only root filesystem
        if "readOnlyRootFilesystem: true" not in doc:
            findings.append({
                "id": "CS-014",
                "stig_vid": "V-222548",
                "cat": "II",
                "title": f"Writable root filesystem: {resource_name}",
                "file": rel,
                "line": None,
                "severity": "MEDIUM",
                "description": "readOnlyRootFilesystem not set. Container filesystem is writable.",
                "remediation": "Add securityContext.readOnlyRootFilesystem: true. Use emptyDir for writable paths.",
                "source": "k8s-check",
            })

        # CS-016: Hardcoded secrets in env
        for i, line in enumerate(lines):
            if SECRET_PATTERNS.search(line):
                findings.append({
                    "id": "CS-016",
                    "stig_vid": "V-222642",
                    "cat": "I",
                    "title": f"Hardcoded secret: {resource_name}",
                    "file": rel,
                    "line": i + 1,
                    "severity": "HIGH",
                    "description": "Possible hardcoded secret in environment variable.",
                    "remediation": "Use Kubernetes Secrets or external secret management.",
                    "source": "k8s-check",
                })

        # CS-017: No securityContext at all
        if "securityContext:" not in doc:
            findings.append({
                "id": "CS-017",
                "stig_vid": "V-222548",
                "cat": "II",
                "title": f"No securityContext: {resource_name}",
                "file": rel,
                "line": None,
                "severity": "MEDIUM",
                "description": "No securityContext defined on pod or container.",
                "remediation": "Add securityContext with runAsNonRoot, readOnlyRootFilesystem, etc.",
                "source": "k8s-check",
            })

        # CS-018: Host networking
        if re.search(r"hostNetwork:\s*true", doc):
            findings.append({
                "id": "CS-018",
                "stig_vid": "V-222545",
                "cat": "I",
                "title": f"Host network enabled: {resource_name}",
                "file": rel,
                "line": _find_line(lines, r"hostNetwork:\s*true"),
                "severity": "HIGH",
                "description": "Pod uses host network namespace.",
                "remediation": "Remove hostNetwork: true. Use Services and NetworkPolicies instead.",
                "source": "k8s-check",
            })

        # CS-019: Host PID/IPC
        for pattern, label in [("hostPID", "Host PID"), ("hostIPC", "Host IPC")]:
            if re.search(rf"{pattern}:\s*true", doc):
                findings.append({
                    "id": "CS-019",
                    "stig_vid": "V-222548",
                    "cat": "I",
                    "title": f"{label} enabled: {resource_name}",
                    "file": rel,
                    "line": _find_line(lines, rf"{pattern}:\s*true"),
                    "severity": "HIGH",
                    "description": f"Pod uses host {label} namespace.",
                    "remediation": f"Remove {pattern}: true.",
                    "source": "k8s-check",
                })

        # CS-020: Latest tag in image
        for i, line in enumerate(lines):
            img_match = re.search(r"image:\s*(\S+)", line)
            if img_match:
                img = img_match.group(1).strip('"').strip("'")
                if img.endswith(":latest") or (":" not in img and "@" not in img and "/" in img):
                    findings.append({
                        "id": "CS-020",
                        "stig_vid": "V-222548",
                        "cat": "II",
                        "title": f"Latest tag: {resource_name}",
                        "file": rel,
                        "line": i + 1,
                        "severity": "MEDIUM",
                        "description": f"Image {img} uses latest or no tag.",
                        "remediation": "Pin to a specific image version tag or digest.",
                        "source": "k8s-check",
                    })

        # CS-021/022: No liveness/readiness probe
        if "livenessProbe:" not in doc:
            findings.append({
                "id": "CS-021",
                "stig_vid": "V-222549",
                "cat": "III",
                "title": f"No liveness probe: {resource_name}",
                "file": rel,
                "line": None,
                "severity": "LOW",
                "description": "No livenessProbe defined. Kubernetes cannot detect hangs.",
                "remediation": "Add livenessProbe with httpGet, tcpSocket, or exec check.",
                "source": "k8s-check",
            })

        if "readinessProbe:" not in doc:
            findings.append({
                "id": "CS-022",
                "stig_vid": "V-222549",
                "cat": "III",
                "title": f"No readiness probe: {resource_name}",
                "file": rel,
                "line": None,
                "severity": "LOW",
                "description": "No readinessProbe defined. Traffic may route to unready pods.",
                "remediation": "Add readinessProbe with httpGet, tcpSocket, or exec check.",
                "source": "k8s-check",
            })

    return findings


def check_k8s_network_policies(k8s_files: list[str], project_root: str) -> list[dict]:
    """Check if namespaces have NetworkPolicies."""
    findings = []
    namespaces = set()
    has_netpol = set()

    for filepath in k8s_files:
        try:
            with open(filepath) as f:
                content = f.read()
        except (OSError, UnicodeDecodeError):
            continue

        # Collect namespaces from all manifests
        for ns in re.findall(r"namespace:\s*(\S+)", content):
            namespaces.add(ns)

        # Check for NetworkPolicy resources
        if "kind: NetworkPolicy" in content:
            for ns in re.findall(r"namespace:\s*(\S+)", content):
                has_netpol.add(ns)

    for ns in namespaces - has_netpol:
        # Check if there's a separate network-policies file that covers it
        pass  # We already track has_netpol across all files

    missing = namespaces - has_netpol
    if missing:
        for ns in sorted(missing):
            findings.append({
                "id": "CS-015",
                "stig_vid": "V-222545",
                "cat": "II",
                "title": f"No NetworkPolicy for namespace: {ns}",
                "file": "k8s/",
                "line": None,
                "severity": "MEDIUM",
                "description": f"Namespace '{ns}' has no NetworkPolicy. All traffic is allowed by default.",
                "remediation": f"Add a NetworkPolicy to restrict ingress/egress for namespace '{ns}'.",
                "source": "k8s-check",
            })

    return findings


# ---------------------------------------------------------------------------
# Docker Compose checks
# ---------------------------------------------------------------------------

def check_docker_compose(filepath: str, project_root: str) -> list[dict]:
    findings = []
    rel = os.path.relpath(filepath, project_root)

    try:
        with open(filepath) as f:
            content = f.read()
            lines = content.splitlines()
    except (OSError, UnicodeDecodeError):
        return findings

    # CS-030: Privileged mode
    if re.search(r"privileged:\s*true", content):
        findings.append({
            "id": "CS-030",
            "stig_vid": "V-222548",
            "cat": "I",
            "title": "Privileged container in compose",
            "file": rel,
            "line": _find_line(lines, r"privileged:\s*true"),
            "severity": "CRITICAL",
            "description": "Service runs in privileged mode.",
            "remediation": "Remove privileged: true.",
            "source": "compose-check",
        })

    # CS-031: No resource limits (deploy.resources.limits)
    # In compose v3+, resource limits are under deploy.resources
    services = re.findall(r"^\s{2}(\w[\w-]*):\s*$", content, re.MULTILINE)
    for svc in services:
        # Extract the service block (rough heuristic)
        svc_pattern = rf"^\s{{2}}{re.escape(svc)}:\s*\n((?:\s{{4,}}.*\n)*)"
        svc_match = re.search(svc_pattern, content, re.MULTILINE)
        if svc_match:
            svc_block = svc_match.group(1)
            if "limits:" not in svc_block and "mem_limit" not in svc_block:
                findings.append({
                    "id": "CS-031",
                    "stig_vid": "V-222549",
                    "cat": "II",
                    "title": f"No resource limits: {svc}",
                    "file": rel,
                    "line": None,
                    "severity": "MEDIUM",
                    "description": f"Service '{svc}' has no resource limits defined.",
                    "remediation": f"Add deploy.resources.limits or mem_limit/cpus for service '{svc}'.",
                    "source": "compose-check",
                })

    # CS-032: Exposed on 0.0.0.0 (ports without host binding)
    for i, line in enumerate(lines):
        # Match port mappings like "8080:8080" (no host IP = binds to 0.0.0.0)
        port_match = re.match(r'\s+-\s+"?(\d+):(\d+)"?', line)
        if port_match:
            findings.append({
                "id": "CS-032",
                "stig_vid": "V-222545",
                "cat": "II",
                "title": f"Port exposed on all interfaces",
                "file": rel,
                "line": i + 1,
                "severity": "MEDIUM",
                "description": f"Port {port_match.group(1)} mapped without host IP restriction (binds to 0.0.0.0).",
                "remediation": "Bind to 127.0.0.1: \"127.0.0.1:PORT:PORT\" for local-only access.",
                "source": "compose-check",
            })

    # CS-033: Hardcoded secrets in environment
    for i, line in enumerate(lines):
        if re.search(r"^\s+(KEYCLOAK_ADMIN_PASSWORD|PASSWORD|SECRET|TOKEN|API_KEY):", line, re.IGNORECASE):
            # Check if the value looks like a real secret (not a placeholder)
            val_match = re.search(r":\s*['\"]?(.+?)['\"]?\s*$", line)
            if val_match:
                val = val_match.group(1).strip()
                if val and val not in ("", "changeme", "example", "test", "demo") and not val.startswith("${"):
                    findings.append({
                        "id": "CS-033",
                        "stig_vid": "V-222642",
                        "cat": "I",
                        "title": "Hardcoded secret in compose",
                        "file": rel,
                        "line": i + 1,
                        "severity": "HIGH",
                        "description": "Potential secret hardcoded in docker-compose environment.",
                        "remediation": "Use .env file, Docker secrets, or environment variable substitution.",
                        "source": "compose-check",
                    })

    # CS-034: No healthcheck
    if "healthcheck:" not in content:
        findings.append({
            "id": "CS-034",
            "stig_vid": "V-222549",
            "cat": "III",
            "title": "No healthcheck in compose",
            "file": rel,
            "line": None,
            "severity": "LOW",
            "description": "No healthcheck defined for any service.",
            "remediation": "Add healthcheck configuration to services.",
            "source": "compose-check",
        })

    # CS-035: Latest tag in images
    for i, line in enumerate(lines):
        img_match = re.match(r"\s+image:\s*(\S+)", line)
        if img_match:
            img = img_match.group(1).strip('"').strip("'")
            if img.endswith(":latest"):
                findings.append({
                    "id": "CS-035",
                    "stig_vid": "V-222548",
                    "cat": "II",
                    "title": f"Latest tag: {img}",
                    "file": rel,
                    "line": i + 1,
                    "severity": "MEDIUM",
                    "description": f"Image {img} uses :latest tag.",
                    "remediation": "Pin to a specific version tag.",
                    "source": "compose-check",
                })

    # CS-036: HTTP URLs without TLS in environment
    for i, line in enumerate(lines):
        if HTTP_URL_PATTERN.search(line):
            findings.append({
                "id": "CS-036",
                "stig_vid": "V-222543",
                "cat": "I",
                "title": "Non-TLS URL in environment",
                "file": rel,
                "line": i + 1,
                "severity": "HIGH",
                "description": "HTTP URL without TLS found in service configuration.",
                "remediation": "Use HTTPS URLs for all external service connections.",
                "source": "compose-check",
            })

    return findings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_line(lines: list[str], pattern: str) -> int | None:
    """Find the first line matching a pattern (1-indexed)."""
    for i, line in enumerate(lines):
        if re.search(pattern, line):
            return i + 1
    return None


def build_output(findings: list[dict], target: str) -> dict:
    by_cat = {"I": 0, "II": 0, "III": 0}
    by_severity: dict[str, int] = {}

    for f in findings:
        cat = f.get("cat", "II")
        by_cat[cat] = by_cat.get(cat, 0) + 1
        sev = f.get("severity", "MEDIUM")
        by_severity[sev] = by_severity.get(sev, 0) + 1

    return {
        "tool": "container-security",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": target,
        "scanner": "fallback",
        "findings": findings,
        "summary": {
            "total": len(findings),
            "by_cat": by_cat,
            "by_severity": by_severity,
        },
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: dockerfile_fallback.py <project-root> [--json] [--mode docker|k8s|all]", file=sys.stderr)
        sys.exit(1)

    project_root = sys.argv[1]
    json_mode = "--json" in sys.argv
    mode = "all"
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1]

    if not os.path.isdir(project_root):
        print(f"ERROR: Not a directory: {project_root}", file=sys.stderr)
        sys.exit(1)

    files = find_files(project_root, mode)
    all_findings: list[dict] = []

    # Check Dockerfiles
    for df in files["dockerfiles"]:
        all_findings.extend(check_dockerfile(df, project_root))

    # Check docker-compose files
    for cf in files["compose"]:
        all_findings.extend(check_docker_compose(cf, project_root))

    # Check K8s manifests
    for kf in files["k8s"]:
        all_findings.extend(check_k8s_manifest(kf, project_root))

    # Cross-file: NetworkPolicy coverage
    if files["k8s"]:
        all_findings.extend(check_k8s_network_policies(files["k8s"], project_root))

    output = build_output(all_findings, project_root)

    if json_mode:
        print(json.dumps(output, indent=2))
    else:
        print(f"\n=== Container Security Scan (Fallback) ===")
        print(f"Scanned: {len(files['dockerfiles'])} Dockerfiles, "
              f"{len(files['compose'])} compose files, "
              f"{len(files['k8s'])} K8s manifests")
        print(f"Total findings: {output['summary']['total']}")
        print(f"  CAT I:   {output['summary']['by_cat']['I']}")
        print(f"  CAT II:  {output['summary']['by_cat']['II']}")
        print(f"  CAT III: {output['summary']['by_cat']['III']}")
        print()

        # Group by file
        by_file: dict[str, list[dict]] = {}
        for f in all_findings:
            by_file.setdefault(f["file"], []).append(f)

        for filepath, file_findings in sorted(by_file.items()):
            print(f"  {filepath}")
            for f in file_findings:
                marker = "!!!" if f["cat"] == "I" else " ! " if f["cat"] == "II" else "   "
                line_info = f"L{f['line']}" if f.get("line") else "   "
                print(f"    [{marker}] {f['stig_vid']} {line_info:>5s} | {f['severity']:8s} | {f['title']}")
            print()


if __name__ == "__main__":
    main()
