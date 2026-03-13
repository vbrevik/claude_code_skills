#!/usr/bin/env python3
"""Parse semgrep SARIF output into structured findings with V-ID tags.

Usage:
    python3 sarif_to_findings.py <sarif-file> [--json]

Output (default): Human-readable findings table
Output (--json):  JSON array for pipeline consumption by /stig-compliance
"""

import json
import sys
from pathlib import Path

# Rule ID prefix to V-ID mapping (must match assets/semgrep-rules/*.yaml)
RULE_VID_MAP = {
    "stig-auth-no-bypass": ("V-222425", "I", "auth"),
    "stig-auth-no-lockout": ("V-222432", "I", "auth"),
    "stig-auth-plaintext-password": ("V-222542", "I", "auth"),
    "stig-auth-password-in-url": ("V-222543", "I", "auth"),
    "stig-auth-weak-password-length": ("V-222536", "I", "auth"),
    "stig-session-id-exposure": ("V-222577", "I", "session-management"),
    "stig-session-url-embedded": ("V-222581", "I", "session-management"),
    "stig-session-no-invalidate": ("V-222578", "I", "session-management"),
    "stig-input-no-validate": ("V-222606", "I", "input-validation"),
    "stig-input-no-size-limit": ("V-222609", "I", "input-validation"),
    "stig-input-path-traversal": ("V-222605", "II", "input-validation"),
    "stig-injection-xss": ("V-222602", "I", "injection"),
    "stig-injection-no-csrf": ("V-222603", "I", "injection"),
    "stig-injection-command": ("V-222604", "I", "injection"),
    "stig-injection-sql": ("V-222607", "I", "injection"),
    "stig-injection-xxe": ("V-222608", "I", "injection"),
    "stig-error-stack-leak": ("V-222610", "II", "error-handling"),
    "stig-error-fail-open": ("V-222585", "I", "error-handling"),
    "stig-crypto-weak-hash": ("V-222571", "I", "cryptography"),
    "stig-crypto-weak-sign": ("V-222570", "I", "cryptography"),
    "stig-config-hardcoded-secret": ("V-222642", "I", "configuration"),
    "stig-audit-no-error-handling": ("V-222485", "I", "audit-logging"),
}


def parse_sarif(sarif_path: str) -> list[dict]:
    """Parse SARIF file and return structured findings."""
    with open(sarif_path) as f:
        sarif = json.load(f)

    findings = []
    for run in sarif.get("runs", []):
        for result in run.get("results", []):
            rule_id = result.get("ruleId", "unknown")

            # Strip any prefix (semgrep adds path-based prefixes)
            short_id = rule_id.split(".")[-1] if "." in rule_id else rule_id

            vid_info = RULE_VID_MAP.get(short_id, (None, None, None))
            v_id, cat, category = vid_info

            # Extract location
            locations = result.get("locations", [])
            file_path = "unknown"
            line = 0
            snippet = ""
            if locations:
                phys = locations[0].get("physicalLocation", {})
                artifact = phys.get("artifactLocation", {})
                file_path = artifact.get("uri", "unknown")
                region = phys.get("region", {})
                line = region.get("startLine", 0)
                snippet_obj = region.get("snippet", {})
                snippet = snippet_obj.get("text", "").strip()

            level = result.get("level", "warning")
            message = result.get("message", {}).get("text", "")

            findings.append({
                "rule_id": short_id,
                "v_id": v_id,
                "cat": cat,
                "category": category,
                "file": file_path,
                "line": line,
                "message": message,
                "severity": "ERROR" if level == "error" else "WARNING",
                "snippet": snippet,
            })

    return findings


def print_table(findings: list[dict]) -> None:
    """Print human-readable findings summary."""
    if not findings:
        print("Static Analysis: 0 findings")
        return

    mapped = [f for f in findings if f["v_id"]]
    unmapped = [f for f in findings if not f["v_id"]]

    print(f"Static Analysis: {len(mapped)} findings, {len(unmapped)} unmapped\n")

    for f in sorted(mapped, key=lambda x: (x["cat"] or "Z", x["file"])):
        label = "FINDING" if f["severity"] == "ERROR" else "INFO"
        vid = f"{f['v_id']} (CAT {f['cat']})" if f["v_id"] else "no-mapping"
        print(f"  {label:8s} {f['rule_id']:<32s} {vid:<20s} {f['file']}:{f['line']}")

    for f in unmapped:
        print(f"  {'INFO':8s} {f['rule_id']:<32s} {'unmapped':<20s} {f['file']}:{f['line']}")


def print_json(findings: list[dict]) -> None:
    """Print JSON for pipeline consumption."""
    output = {
        "tool": "semgrep",
        "scope": "manual",
        "findings": findings,
    }
    print(json.dumps(output, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Usage: sarif_to_findings.py <sarif-file> [--json]", file=sys.stderr)
        sys.exit(1)

    sarif_path = sys.argv[1]
    json_mode = "--json" in sys.argv

    if not Path(sarif_path).exists():
        print(f"SARIF file not found: {sarif_path}", file=sys.stderr)
        sys.exit(1)

    findings = parse_sarif(sarif_path)

    if json_mode:
        print_json(findings)
    else:
        print_table(findings)


if __name__ == "__main__":
    main()
