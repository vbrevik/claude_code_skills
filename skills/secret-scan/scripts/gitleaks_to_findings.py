#!/usr/bin/env python3
"""Parse gitleaks JSON output into STIG-tagged pipeline findings.

Usage:
    python3 gitleaks_to_findings.py <gitleaks-json> [--json]

    Default: human-readable table
    --json:  pipeline JSON format for /stig-compliance
"""

import json
import sys
import os
from datetime import datetime, timezone

# Map gitleaks rule IDs to STIG V-IDs
RULE_VID_MAP = {
    # V-222642: No embedded authenticators (CAT I)
    "generic-api-key": "V-222642",
    "private-key": "V-222642",
    "aws-access-key-id": "V-222642",
    "aws-secret-access-key": "V-222642",
    "gcp-api-key": "V-222642",
    "gcp-service-account": "V-222642",
    "azure-storage-key": "V-222642",
    "github-pat": "V-222642",
    "github-oauth": "V-222642",
    "github-app-token": "V-222642",
    "github-refresh-token": "V-222642",
    "gitlab-pat": "V-222642",
    "jwt-token": "V-222642",
    "jwt": "V-222642",
    "slack-token": "V-222642",
    "slack-webhook": "V-222642",
    "slack-webhook-url": "V-222642",
    "stripe-api-key": "V-222642",
    "twilio-api-key": "V-222642",
    "sendgrid-api-key": "V-222642",
    "npm-access-token": "V-222642",
    "pypi-upload-token": "V-222642",
    "nuget-api-key": "V-222642",
    "docker-config": "V-222642",
    "heroku-api-key": "V-222642",
    "hashicorp-tf-password": "V-222642",
    "vault-token": "V-222642",
    "vault-service-token": "V-222642",
    "ssh-password": "V-222642",
    "encryption-key": "V-222642",
    "generic-password": "V-222642",
    "generic-secret": "V-222642",
    "generic-token": "V-222642",
    # V-222543: Encrypted credential transmission (CAT I)
    "password-in-url": "V-222543",
    "connection-string": "V-222543",
}

VID_TITLES = {
    "V-222642": "No embedded authenticators in application code",
    "V-222543": "Transmission of credentials over encrypted channels",
}

VID_REMEDIATION = {
    "V-222642": "Move to environment variable or secrets manager",
    "V-222543": "Use connection config with separate credential source",
}


def get_vid(rule_id: str) -> str:
    """Map a gitleaks rule ID to a STIG V-ID. Defaults to V-222642."""
    return RULE_VID_MAP.get(rule_id, "V-222642")


def redact_snippet(match: str, max_len: int = 40) -> str:
    """Partially redact a secret snippet for display."""
    if not match:
        return ""
    # Truncate
    s = match.strip()[:max_len]
    # Redact middle portion if long enough
    if len(s) > 16:
        s = s[:8] + "****" + s[-4:]
    return s


def parse_gitleaks_json(filepath: str) -> list:
    """Parse gitleaks JSON output into normalized findings."""
    with open(filepath, "r") as f:
        raw = json.load(f)

    if not isinstance(raw, list):
        raw = [raw]

    findings = []
    for item in raw:
        rule_id = item.get("RuleID", "unknown")
        v_id = get_vid(rule_id)

        finding = {
            "rule_id": rule_id,
            "v_id": v_id,
            "cat": "I",
            "title": VID_TITLES.get(v_id, "Secret detected"),
            "file": item.get("File", "unknown"),
            "line": item.get("StartLine", 0),
            "commit": item.get("Commit", ""),
            "author": item.get("Author", ""),
            "date": item.get("Date", ""),
            "snippet": redact_snippet(item.get("Match", item.get("Secret", ""))),
            "entropy": item.get("Entropy", 0),
            "remediation": VID_REMEDIATION.get(v_id, "Review and remediate"),
        }
        findings.append(finding)

    return findings


def print_table(findings: list) -> None:
    """Print human-readable findings table."""
    if not findings:
        print("Secret Scan: 0 findings -- no secrets detected")
        return

    print(f"Secret Scan: {len(findings)} finding(s)\n")
    for f in findings:
        snippet = f'"{f["snippet"]}"' if f["snippet"] else ""
        commit = f'  commit:{f["commit"][:7]}' if f["commit"] else ""
        print(
            f'FINDING  {f["rule_id"]:<22} {f["v_id"]} (CAT {f["cat"]})  '
            f'{f["file"]}:{f["line"]}{commit}  {snippet}'
        )


def print_json(findings: list, source_path: str = "", scope: str = "git-history") -> None:
    """Print pipeline JSON format."""
    by_vid = {}
    for f in findings:
        by_vid[f["v_id"]] = by_vid.get(f["v_id"], 0) + 1

    output = {
        "tool": "gitleaks",
        "version": get_gitleaks_version(),
        "scope": scope,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_path": source_path,
        "config": "assets/gitleaks.toml",
        "summary": {
            "total_findings": len(findings),
            "by_cat": {
                "I": sum(1 for f in findings if f["cat"] == "I"),
                "II": sum(1 for f in findings if f["cat"] == "II"),
                "III": sum(1 for f in findings if f["cat"] == "III"),
            },
            "by_vid": by_vid,
        },
        "findings": findings,
    }
    print(json.dumps(output, indent=2))


def get_gitleaks_version() -> str:
    """Try to get gitleaks version."""
    try:
        import subprocess
        result = subprocess.run(
            ["gitleaks", "version"], capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def main():
    if len(sys.argv) < 2:
        print("Usage: gitleaks_to_findings.py <gitleaks-json> [--json]", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    json_mode = "--json" in sys.argv

    if not os.path.exists(filepath):
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    findings = parse_gitleaks_json(filepath)

    if json_mode:
        print_json(findings)
    else:
        print_table(findings)


if __name__ == "__main__":
    main()
