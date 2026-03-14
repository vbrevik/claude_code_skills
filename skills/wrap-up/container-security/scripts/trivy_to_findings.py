#!/usr/bin/env python3
"""Parse Trivy JSON output into standard pipeline findings format.

Usage:
    python3 trivy_to_findings.py <trivy-output.json> [--json]
"""

import json
import sys
from datetime import datetime, timezone

# Map Trivy misconfiguration IDs to STIG V-IDs
TRIVY_TO_STIG = {
    "DS001": {"vid": "V-222548", "cat": "II", "title": "Container runs as root"},
    "DS002": {"vid": "V-222548", "cat": "II", "title": "Base image uses latest tag"},
    "DS005": {"vid": "V-222548", "cat": "II", "title": "ADD used instead of COPY"},
    "DS006": {"vid": "V-222548", "cat": "III", "title": "COPY --chown flag used"},
    "DS026": {"vid": "V-222549", "cat": "III", "title": "No HEALTHCHECK defined"},
    "KSV001": {"vid": "V-222548", "cat": "I", "title": "Privileged container"},
    "KSV003": {"vid": "V-222548", "cat": "II", "title": "Excessive capabilities"},
    "KSV006": {"vid": "V-222545", "cat": "I", "title": "Host network enabled"},
    "KSV009": {"vid": "V-222548", "cat": "I", "title": "Host PID namespace"},
    "KSV011": {"vid": "V-222549", "cat": "II", "title": "No CPU limits set"},
    "KSV012": {"vid": "V-222548", "cat": "II", "title": "Runs as root user"},
    "KSV014": {"vid": "V-222548", "cat": "II", "title": "No read-only root filesystem"},
    "KSV021": {"vid": "V-222545", "cat": "II", "title": "No network policy"},
    "KSV106": {"vid": "V-222642", "cat": "I", "title": "Secrets in environment variables"},
}

SEVERITY_TO_CAT = {
    "CRITICAL": "I",
    "HIGH": "I",
    "MEDIUM": "II",
    "LOW": "III",
}


def parse_trivy_results(data: dict) -> list[dict]:
    """Parse Trivy JSON results into pipeline findings."""
    findings = []
    results = data.get("Results", [])

    for result in results:
        target = result.get("Target", "unknown")

        # Misconfigurations (Dockerfile, K8s, compose)
        for misconf in result.get("Misconfigurations", []):
            misconf_id = misconf.get("ID", "")
            severity = misconf.get("Severity", "MEDIUM").upper()

            # Look up STIG mapping
            stig = TRIVY_TO_STIG.get(misconf_id, {})
            vid = stig.get("vid", "V-222548")
            cat = stig.get("cat", SEVERITY_TO_CAT.get(severity, "II"))

            findings.append({
                "id": f"CS-T-{misconf_id}",
                "stig_vid": vid,
                "cat": cat,
                "title": misconf.get("Title", stig.get("title", misconf_id)),
                "file": target,
                "line": misconf.get("CauseMetadata", {}).get("StartLine"),
                "severity": severity,
                "description": misconf.get("Description", ""),
                "remediation": misconf.get("Resolution", ""),
                "source": "trivy-config",
            })

        # Vulnerabilities (image scanning)
        for vuln in result.get("Vulnerabilities", []):
            severity = vuln.get("Severity", "MEDIUM").upper()
            findings.append({
                "id": f"CS-V-{vuln.get('VulnerabilityID', 'unknown')}",
                "stig_vid": "V-222551",
                "cat": SEVERITY_TO_CAT.get(severity, "II"),
                "title": f"{vuln.get('VulnerabilityID', '')}: {vuln.get('PkgName', '')}",
                "file": target,
                "line": None,
                "severity": severity,
                "description": vuln.get("Description", ""),
                "remediation": f"Update {vuln.get('PkgName', '')} from {vuln.get('InstalledVersion', '')} to {vuln.get('FixedVersion', 'latest')}",
                "source": "trivy-image",
            })

    return findings


def build_output(findings: list[dict], target: str) -> dict:
    """Build the standard pipeline output."""
    by_cat = {"I": 0, "II": 0, "III": 0}
    by_severity = {}

    for f in findings:
        cat = f.get("cat", "II")
        by_cat[cat] = by_cat.get(cat, 0) + 1
        sev = f.get("severity", "MEDIUM")
        by_severity[sev] = by_severity.get(sev, 0) + 1

    return {
        "tool": "container-security",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": target,
        "scanner": "trivy",
        "findings": findings,
        "summary": {
            "total": len(findings),
            "by_cat": by_cat,
            "by_severity": by_severity,
        },
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: trivy_to_findings.py <trivy-output.json> [--json]", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    json_mode = "--json" in sys.argv

    with open(input_path) as f:
        data = json.load(f)

    if "error" in data:
        print(f"Trivy error: {data['error']}", file=sys.stderr)
        sys.exit(1)

    findings = parse_trivy_results(data)
    output = build_output(findings, input_path)

    if json_mode:
        print(json.dumps(output, indent=2))
    else:
        # Human-readable summary
        print(f"\n=== Container Security Scan (Trivy) ===")
        print(f"Total findings: {output['summary']['total']}")
        print(f"  CAT I:   {output['summary']['by_cat']['I']}")
        print(f"  CAT II:  {output['summary']['by_cat']['II']}")
        print(f"  CAT III: {output['summary']['by_cat']['III']}")
        print()

        for f in findings:
            marker = "!!!" if f["cat"] == "I" else " ! " if f["cat"] == "II" else "   "
            print(f"  [{marker}] {f['stig_vid']} | {f['severity']:8s} | {f['file']}")
            print(f"         {f['title']}")
            if f.get("remediation"):
                print(f"         Fix: {f['remediation']}")
            print()


if __name__ == "__main__":
    main()
