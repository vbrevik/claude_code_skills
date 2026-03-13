#!/usr/bin/env python3
"""Parse nuclei JSONL output into structured findings with V-ID tags.

Usage:
    python3 nuclei_to_findings.py <jsonl-file> [--json]

Output (default): Human-readable findings table
Output (--json):  JSON for pipeline consumption by /stig-compliance
"""

import json
import sys
from pathlib import Path

# Template ID to V-ID mapping (must match assets/nuclei-templates/*.yaml)
TEMPLATE_VID_MAP = {
    # security-headers
    "stig-header-no-csp": ("V-222602", "I", "security-headers"),
    "stig-header-no-xframe": ("V-222602", "I", "security-headers"),
    "stig-header-no-xcontent": ("V-222602", "I", "security-headers"),
    "stig-header-no-hsts": ("V-222596", "II", "security-headers"),
    # tls-config
    "stig-tls-version": ("V-222596", "II", "tls-config"),
    "stig-tls-no-encryption": ("V-222597", "I", "tls-config"),
    # session-cookies
    "stig-cookie-no-httponly": ("V-222577", "I", "session-cookies"),
    "stig-cookie-no-secure": ("V-222577", "I", "session-cookies"),
    "stig-cookie-no-samesite": ("V-222577", "I", "session-cookies"),
    # error-disclosure
    "stig-error-stack-trace": ("V-222610", "II", "error-disclosure"),
    "stig-error-debug-mode": ("V-222610", "II", "error-disclosure"),
    # info-exposure
    "stig-info-server-header": ("V-222610", "II", "info-exposure"),
    "stig-info-powered-by": ("V-222610", "II", "info-exposure"),
}


def parse_jsonl(jsonl_path: str) -> list[dict]:
    """Parse nuclei JSONL output and return structured findings."""
    findings = []

    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                result = json.loads(line)
            except json.JSONDecodeError:
                continue

            template_id = result.get("template-id", "unknown")
            vid_info = TEMPLATE_VID_MAP.get(template_id, (None, None, None))
            v_id, cat, category = vid_info

            matched_at = result.get("matched-at", "unknown")
            info = result.get("info", {})
            severity_raw = info.get("severity", "info")
            severity = "ERROR" if severity_raw in ("critical", "high") else "WARNING"

            # Build message from extracted results or info
            extracted = result.get("extracted-results", [])
            message = extracted[0] if extracted else info.get("name", template_id)

            findings.append({
                "rule_id": template_id,
                "v_id": v_id,
                "cat": cat,
                "category": category,
                "file": matched_at,
                "line": 0,
                "message": message,
                "severity": severity,
                "snippet": "",
            })

    return findings


def print_table(findings: list[dict]) -> None:
    """Print human-readable findings summary."""
    if not findings:
        print("DAST Scan: 0 findings")
        return

    mapped = [f for f in findings if f["v_id"]]
    unmapped = [f for f in findings if not f["v_id"]]

    print(f"DAST Scan: {len(mapped)} findings, {len(unmapped)} unmapped\n")

    for f in sorted(mapped, key=lambda x: (x["cat"] or "Z", x["rule_id"])):
        label = "FINDING" if f["severity"] == "ERROR" else "INFO"
        vid = f"{f['v_id']} (CAT {f['cat']})" if f["v_id"] else "no-mapping"
        print(f"  {label:8s} {f['rule_id']:<28s} {vid:<20s} {f['message']}")

    for f in unmapped:
        print(f"  {'INFO':8s} {f['rule_id']:<28s} {'unmapped':<20s} {f['message']}")


def print_json(findings: list[dict]) -> None:
    """Print JSON for pipeline consumption."""
    target = findings[0]["file"] if findings else "unknown"
    output = {
        "tool": "nuclei",
        "target": target,
        "scope": "dast",
        "findings": findings,
    }
    print(json.dumps(output, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Usage: nuclei_to_findings.py <jsonl-file> [--json]", file=sys.stderr)
        sys.exit(1)

    jsonl_path = sys.argv[1]
    json_mode = "--json" in sys.argv

    if not Path(jsonl_path).exists():
        print(f"JSONL file not found: {jsonl_path}", file=sys.stderr)
        sys.exit(1)

    findings = parse_jsonl(jsonl_path)

    if json_mode:
        print_json(findings)
    else:
        print_table(findings)


if __name__ == "__main__":
    main()
