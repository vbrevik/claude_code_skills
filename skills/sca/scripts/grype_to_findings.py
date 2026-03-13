#!/usr/bin/env python3
"""Parse Grype or npm audit JSON into structured findings with V-ID tags.

Usage:
    python3 grype_to_findings.py <json-file> [--json] [--npm-audit]

Output (default): Human-readable findings table
Output (--json):  JSON array for pipeline consumption by /stig-compliance
"""

import json
import sys
from pathlib import Path

# CVE severity to STIG CAT mapping
SEVERITY_CAT_MAP = {
    "Critical": "I",
    "High": "I",
    "Medium": "II",
    "Low": "III",
    "Negligible": None,
    "Unknown": "III",
    # npm audit severities
    "critical": "I",
    "high": "I",
    "moderate": "II",
    "low": "III",
    "info": None,
}

V_ID = "V-222551"  # Automated vulnerability scanning


def parse_grype(data: dict) -> list[dict]:
    """Parse Grype JSON output into structured findings."""
    findings = []
    matches = data.get("matches", [])

    for match in matches:
        vuln = match.get("vulnerability", {})
        artifact = match.get("artifact", {})

        cve_id = vuln.get("id", "unknown")
        severity = vuln.get("severity", "Unknown")
        description = vuln.get("description", "")
        if not description:
            # Try to get from related vulnerabilities
            related = vuln.get("relatedVulnerabilities", [])
            if related:
                description = related[0].get("description", "")

        pkg_name = artifact.get("name", "unknown")
        pkg_version = artifact.get("version", "unknown")

        # Get fixed version
        fixed_version = None
        fix = vuln.get("fix", {})
        if fix:
            versions = fix.get("versions", [])
            if versions:
                fixed_version = versions[0]
            elif fix.get("state") == "not-fixed":
                fixed_version = None

        cat = SEVERITY_CAT_MAP.get(severity)
        if cat is None:
            continue  # Skip negligible/info

        # Truncate description for display
        message = description[:200] if description else f"{severity} vulnerability in {pkg_name}"

        findings.append({
            "rule_id": cve_id,
            "v_id": V_ID,
            "cat": cat,
            "category": "vulnerability-scanning",
            "package": pkg_name,
            "installed_version": pkg_version,
            "fixed_version": fixed_version,
            "severity": severity,
            "message": message,
            "file": "package-lock.json",
        })

    return findings


def parse_npm_audit(data: dict) -> list[dict]:
    """Parse npm audit JSON output into structured findings."""
    findings = []

    # npm audit v2 format (npm 7+)
    vulns = data.get("vulnerabilities", {})
    for pkg_name, vuln_info in vulns.items():
        severity = vuln_info.get("severity", "low")
        cat = SEVERITY_CAT_MAP.get(severity)
        if cat is None:
            continue

        # Normalize severity to title case for consistency
        severity_display = {
            "critical": "Critical",
            "high": "High",
            "moderate": "Medium",
            "low": "Low",
        }.get(severity, severity.title())

        # Get installed version from range
        installed_version = vuln_info.get("range", "unknown")
        # Try to get more specific version
        nodes = vuln_info.get("nodes", [])

        # Get fix info
        fix_available = vuln_info.get("fixAvailable")
        fixed_version = None
        if isinstance(fix_available, dict):
            fixed_version = fix_available.get("version")
        elif isinstance(fix_available, bool) and fix_available:
            fixed_version = "available (run npm audit fix)"

        # Get CVE IDs from via entries
        via_entries = vuln_info.get("via", [])
        cve_ids = []
        messages = []
        for via in via_entries:
            if isinstance(via, dict):
                source = via.get("source")
                url = via.get("url", "")
                title = via.get("title", "")
                if url and "CVE" in url:
                    cve_id = url.split("/")[-1] if "/" in url else url
                    cve_ids.append(cve_id)
                elif source:
                    cve_ids.append(f"GHSA-{source}" if not str(source).startswith("GHSA") else str(source))
                if title:
                    messages.append(title)
            elif isinstance(via, str):
                # Reference to another vulnerability entry
                messages.append(f"Transitive via {via}")

        if not cve_ids:
            cve_ids = [f"npm-vuln-{pkg_name}"]

        message = "; ".join(messages) if messages else f"{severity_display} vulnerability in {pkg_name}"

        for cve_id in cve_ids:
            findings.append({
                "rule_id": str(cve_id),
                "v_id": V_ID,
                "cat": cat,
                "category": "vulnerability-scanning",
                "package": pkg_name,
                "installed_version": installed_version,
                "fixed_version": fixed_version,
                "severity": severity_display,
                "message": message,
                "file": "package-lock.json",
            })

    return findings


def print_table(findings: list[dict]) -> None:
    """Print human-readable findings summary."""
    if not findings:
        print("SCA Vulnerability Scan: 0 findings")
        return

    # Count by severity
    counts = {}
    for f in findings:
        sev = f["severity"]
        counts[sev] = counts.get(sev, 0) + 1

    count_parts = ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
    print(f"SCA Vulnerability Scan: {len(findings)} findings ({count_parts})\n")

    # Sort: CAT I first, then II, then III
    cat_order = {"I": 0, "II": 1, "III": 2}
    sorted_findings = sorted(findings, key=lambda x: (cat_order.get(x["cat"], 9), x["package"]))

    for f in sorted_findings:
        fix = f"Fix: {f['fixed_version']}" if f["fixed_version"] else "No fix available"
        pkg = f"{f['package']}@{f['installed_version']}"
        vid = f"{f['v_id']} (CAT {f['cat']})"
        print(f"  {f['severity']:<10s} {f['rule_id']:<20s} {pkg:<30s} {vid:<20s} {fix}")

    # Summary
    cat_i = sum(1 for f in findings if f["cat"] == "I")
    cat_ii = sum(1 for f in findings if f["cat"] == "II")
    cat_iii = sum(1 for f in findings if f["cat"] == "III")

    parts = []
    if cat_i:
        parts.append(f"{cat_i} CAT I (block release)")
    if cat_ii:
        parts.append(f"{cat_ii} CAT II (fix in maintenance cycle)")
    if cat_iii:
        parts.append(f"{cat_iii} CAT III (track)")

    print(f"\nSummary: {', '.join(parts)}")


def print_json(findings: list[dict], tool_name: str) -> None:
    """Print JSON for pipeline consumption."""
    output = {
        "tool": tool_name,
        "scope": "project",
        "findings": findings,
    }
    print(json.dumps(output, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Usage: grype_to_findings.py <json-file> [--json] [--npm-audit]", file=sys.stderr)
        sys.exit(1)

    json_path = sys.argv[1]
    json_mode = "--json" in sys.argv
    npm_audit_mode = "--npm-audit" in sys.argv

    if not Path(json_path).exists():
        print(f"File not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    with open(json_path) as f:
        data = json.load(f)

    # Auto-detect format if --npm-audit not specified
    if not npm_audit_mode:
        # Grype output has "matches" key, npm audit has "vulnerabilities"
        if "matches" in data:
            npm_audit_mode = False
        elif "vulnerabilities" in data:
            npm_audit_mode = True
        else:
            print("WARNING: Could not detect input format. Trying Grype format.", file=sys.stderr)

    if npm_audit_mode:
        findings = parse_npm_audit(data)
        tool_name = "npm-audit"
    else:
        findings = parse_grype(data)
        tool_name = "grype"

    if json_mode:
        print_json(findings, tool_name)
    else:
        print_table(findings)


if __name__ == "__main__":
    main()
