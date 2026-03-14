#!/usr/bin/env python3
"""Parse OFFAT or curl-probe JSON into structured findings with V-ID tags.

Usage:
    python3 offat_to_findings.py <json-file> [--json] [--curl-mode]

Output (default): Human-readable findings table
Output (--json):  JSON for pipeline consumption by /stig-compliance
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Test category to STIG V-ID mapping
STIG_MAP = {
    "auth-bypass":          {"v_id": "V-222425", "cat": "I",  "description": "Authentication required for all endpoints"},
    "bola":                 {"v_id": "V-222425", "cat": "I",  "description": "Object-level authorization"},
    "sql-injection":        {"v_id": "V-222578", "cat": "I",  "description": "Input validation - SQL"},
    "xss":                  {"v_id": "V-222577", "cat": "I",  "description": "Input validation - scripts"},
    "path-traversal":       {"v_id": "V-222604", "cat": "I",  "description": "URL access restriction"},
    "ssrf":                 {"v_id": "V-222604", "cat": "I",  "description": "URL access restriction"},
    "error-disclosure":     {"v_id": "V-222602", "cat": "II", "description": "Error information leakage"},
    "tech-disclosure":      {"v_id": "V-222602", "cat": "II", "description": "Error information leakage"},
    "input-validation":     {"v_id": "V-222606", "cat": "II", "description": "Input character restriction"},
    "missing-header-xcto":  {"v_id": "V-222543", "cat": "II", "description": "Transport security"},
    "missing-header-xfo":   {"v_id": "V-222543", "cat": "II", "description": "Transport security"},
    "missing-header-hsts":  {"v_id": "V-222543", "cat": "II", "description": "Transport security"},
    "missing-header-csp":   {"v_id": "V-222543", "cat": "II", "description": "Transport security"},
    "cors-wildcard":        {"v_id": "V-222596", "cat": "II", "description": "Cross-origin policy"},
    "cors-reflection":      {"v_id": "V-222596", "cat": "II", "description": "Cross-origin policy"},
    "no-rate-limit":        {"v_id": "V-222549", "cat": "II", "description": "Resource exhaustion"},
    "mass-assignment":      {"v_id": "V-222606", "cat": "II", "description": "Input character restriction"},
    "schema-violation":     {"v_id": "V-222606", "cat": "II", "description": "Input character restriction"},
}

# OFFAT severity normalization
OFFAT_SEVERITY_MAP = {
    "critical": "HIGH",
    "high": "HIGH",
    "medium": "MEDIUM",
    "low": "LOW",
    "info": "LOW",
}

# Severity to CAT fallback
SEVERITY_TO_CAT = {
    "HIGH": "I",
    "MEDIUM": "II",
    "LOW": "III",
}


def classify_offat_finding(result: dict) -> str:
    """Map an OFFAT result to our rule_id taxonomy."""
    name = (result.get("test_name", "") or "").lower()
    status_code = result.get("response_status_code", 0)
    endpoint = (result.get("url", "") or "").lower()

    if "auth" in name or "unauthenticated" in name or "token" in name:
        return "auth-bypass"
    if "bola" in name or "idor" in name or "broken object" in name:
        return "bola"
    if "sql" in name:
        return "sql-injection"
    if "xss" in name or "cross-site scripting" in name:
        return "xss"
    if "ssrf" in name or "server-side request" in name:
        return "ssrf"
    if "traversal" in name or "path" in name or "lfi" in name:
        return "path-traversal"
    if "mass assignment" in name or "parameter pollution" in name:
        return "mass-assignment"
    if "schema" in name or "validation" in name or "type" in name:
        return "schema-violation"
    if "disclosure" in name or "information" in name or "error" in name:
        return "error-disclosure"
    if "cors" in name:
        return "cors-wildcard"
    if "rate" in name or "dos" in name or "throttl" in name:
        return "no-rate-limit"
    if "header" in name:
        return "missing-header-xcto"

    return "input-validation"


def parse_offat(data: dict) -> list[dict]:
    """Parse OFFAT JSON output into structured findings."""
    findings = []
    results = data.get("results", [])
    if not results and isinstance(data, list):
        results = data

    seen = set()
    finding_num = 0

    for result in results:
        # Skip passed tests
        if result.get("result", "").lower() in ("pass", "passed", "safe"):
            continue

        rule_id = classify_offat_finding(result)
        endpoint = result.get("endpoint", result.get("url", "unknown"))
        method = result.get("method", result.get("http_method", "GET")).upper()
        dedup_key = (endpoint, rule_id)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        stig = STIG_MAP.get(rule_id, {"v_id": "V-222606", "cat": "II"})
        severity_raw = (result.get("severity", "medium") or "medium").lower()
        severity = OFFAT_SEVERITY_MAP.get(severity_raw, "MEDIUM")

        finding_num += 1
        findings.append({
            "id": f"AF-{finding_num:03d}",
            "rule_id": rule_id,
            "v_id": stig["v_id"],
            "cat": stig["cat"],
            "category": rule_id.replace("-", " ").split()[0] if "-" in rule_id else rule_id,
            "endpoint": f"{method} {endpoint}",
            "method": method,
            "severity": severity,
            "message": result.get("test_name", result.get("description", f"{rule_id} finding")),
            "response_code": result.get("response_status_code", result.get("status_code", 0)),
            "snippet": (result.get("response_body", "") or "")[:200],
        })

    return findings


def parse_curl_probes(data: dict) -> list[dict]:
    """Parse curl-based probe JSON output into structured findings."""
    findings_raw = data.get("findings", [])
    if not findings_raw and isinstance(data, list):
        findings_raw = data

    findings = []
    seen = set()
    finding_num = 0

    for f in findings_raw:
        rule_id = f.get("rule_id", "input-validation")
        endpoint = f.get("endpoint", "unknown")
        dedup_key = (endpoint, rule_id)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        stig = STIG_MAP.get(rule_id, {"v_id": "V-222606", "cat": "II"})
        severity = f.get("severity", "MEDIUM")

        finding_num += 1
        findings.append({
            "id": f.get("id", f"AF-{finding_num:03d}"),
            "rule_id": rule_id,
            "v_id": stig["v_id"],
            "cat": stig["cat"],
            "category": f.get("category", rule_id.replace("-", " ").split()[0]),
            "endpoint": endpoint,
            "method": f.get("method", "GET"),
            "severity": severity,
            "message": f.get("message", f"{rule_id} finding"),
            "response_code": f.get("response_code", 0),
            "snippet": f.get("snippet", ""),
        })

    return findings


def print_table(findings: list[dict], scope: str) -> None:
    """Print human-readable findings summary."""
    if not findings:
        print("API Fuzz Scan: 0 findings")
        return

    counts = {}
    for f in findings:
        sev = f["severity"]
        counts[sev] = counts.get(sev, 0) + 1

    count_parts = ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
    print(f"API Fuzz Scan ({scope}): {len(findings)} findings ({count_parts})\n")

    cat_order = {"I": 0, "II": 1, "III": 2}
    sorted_findings = sorted(findings, key=lambda x: (cat_order.get(x["cat"], 9), x["endpoint"]))

    for f in sorted_findings:
        vid = f"{f['v_id']} (CAT {f['cat']})"
        print(f"  {f['severity']:<8s} {f['rule_id']:<22s} {f['endpoint']:<35s} {vid:<20s} {f['message'][:60]}")

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


def print_json(findings: list[dict], scope: str, endpoints_tested: int) -> None:
    """Print JSON for pipeline consumption."""
    by_cat: dict[str, int] = {}
    by_category: dict[str, int] = {}
    for f in findings:
        by_cat[f["cat"]] = by_cat.get(f["cat"], 0) + 1
        cat_name = f.get("category", "unknown")
        by_category[cat_name] = by_category.get(cat_name, 0) + 1

    output = {
        "tool": "api-fuzz",
        "scope": scope,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "findings": findings,
        "summary": {
            "total": len(findings),
            "endpoints_tested": endpoints_tested,
            "by_cat": by_cat,
            "by_category": by_category,
        },
    }
    print(json.dumps(output, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Usage: offat_to_findings.py <json-file> [--json] [--curl-mode]", file=sys.stderr)
        sys.exit(1)

    json_path = sys.argv[1]
    json_mode = "--json" in sys.argv
    curl_mode = "--curl-mode" in sys.argv

    if not Path(json_path).exists():
        print(f"File not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    with open(json_path) as f:
        data = json.load(f)

    # Auto-detect format if --curl-mode not specified
    if not curl_mode:
        if isinstance(data, dict) and "mode" in data and data.get("mode") == "curl-fallback":
            curl_mode = True
        elif isinstance(data, dict) and "results" in data:
            curl_mode = False
        elif isinstance(data, dict) and "findings" in data:
            curl_mode = True
        elif isinstance(data, list):
            curl_mode = False

    scope = data.get("scope", "unknown") if isinstance(data, dict) else "unknown"
    endpoints_tested = 0
    if isinstance(data, dict):
        summary = data.get("summary", {})
        endpoints_tested = summary.get("endpoints_tested", 0)

    if curl_mode:
        findings = parse_curl_probes(data)
    else:
        findings = parse_offat(data)

    if json_mode:
        print_json(findings, scope, endpoints_tested)
    else:
        print_table(findings, scope)


if __name__ == "__main__":
    main()
