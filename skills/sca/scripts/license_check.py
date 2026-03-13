#!/usr/bin/env python3
"""Parse CycloneDX SBOM and audit dependency licenses for government procurement.

Usage:
    python3 license_check.py <sbom.json> [--json]

Flags GPL, AGPL, LGPL and unknown licenses for review.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

# License classification for government procurement
LICENSE_FLAGS = {
    # Copyleft — procurement concern
    "GPL-2.0-only": "WARNING",
    "GPL-2.0-or-later": "WARNING",
    "GPL-3.0-only": "WARNING",
    "GPL-3.0-or-later": "WARNING",
    "GPL-2.0": "WARNING",
    "GPL-3.0": "WARNING",
    # Network copyleft — likely incompatible
    "AGPL-3.0-only": "WARNING",
    "AGPL-3.0-or-later": "WARNING",
    "AGPL-3.0": "WARNING",
    # Weak copyleft — usually acceptable
    "LGPL-2.1-only": "INFO",
    "LGPL-2.1-or-later": "INFO",
    "LGPL-3.0-only": "INFO",
    "LGPL-3.0-or-later": "INFO",
    "LGPL-2.1": "INFO",
    "LGPL-3.0": "INFO",
    # MPL — file-level copyleft, generally acceptable
    "MPL-2.0": "INFO",
    # Permissive — no issues
    "MIT": "OK",
    "Apache-2.0": "OK",
    "BSD-2-Clause": "OK",
    "BSD-3-Clause": "OK",
    "ISC": "OK",
    "Unlicense": "OK",
    "0BSD": "OK",
    "CC0-1.0": "OK",
    "BlueOak-1.0.0": "OK",
    "Python-2.0": "OK",
    "Zlib": "OK",
}


def extract_licenses(sbom: dict) -> list[dict]:
    """Extract license info from CycloneDX SBOM components."""
    results = []
    components = sbom.get("components", [])

    for comp in components:
        name = comp.get("name", "unknown")
        version = comp.get("version", "unknown")
        licenses_data = comp.get("licenses", [])

        license_ids = []
        for lic_entry in licenses_data:
            lic = lic_entry.get("license", {})
            lic_id = lic.get("id")
            lic_name = lic.get("name")
            if lic_id:
                license_ids.append(lic_id)
            elif lic_name:
                license_ids.append(lic_name)

        if not license_ids:
            license_ids = ["UNKNOWN"]

        for lic_id in license_ids:
            flag = LICENSE_FLAGS.get(lic_id, "WARNING" if lic_id == "UNKNOWN" else "OK")
            # Check partial matches for variants
            if flag == "OK" and lic_id not in LICENSE_FLAGS:
                lic_upper = lic_id.upper()
                if "GPL" in lic_upper and "LGPL" not in lic_upper:
                    flag = "WARNING"
                elif "AGPL" in lic_upper:
                    flag = "WARNING"
                elif "LGPL" in lic_upper:
                    flag = "INFO"

            results.append({
                "package": name,
                "version": version,
                "license": lic_id,
                "flag": flag,
            })

    return results


def print_summary(results: list[dict]) -> None:
    """Print license audit summary."""
    if not results:
        print("License Audit: 0 dependencies scanned (SBOM has no license data)")
        return

    # Group by license
    by_license: dict[str, list[str]] = defaultdict(list)
    for r in results:
        by_license[r["license"]].append(f"{r['package']}@{r['version']}")

    # Determine flag for each license group
    license_flags: dict[str, str] = {}
    for lic_id in by_license:
        flag = LICENSE_FLAGS.get(lic_id, "OK")
        if lic_id == "UNKNOWN":
            flag = "WARNING"
        elif lic_id not in LICENSE_FLAGS:
            lic_upper = lic_id.upper()
            if "GPL" in lic_upper and "LGPL" not in lic_upper:
                flag = "WARNING"
            elif "AGPL" in lic_upper:
                flag = "WARNING"
            elif "LGPL" in lic_upper:
                flag = "INFO"
        license_flags[lic_id] = flag

    total = len(results)
    print(f"License Audit: {total} dependencies scanned\n")

    # Sort: OK first, then INFO, then WARNING
    flag_order = {"OK": 0, "INFO": 1, "WARNING": 2}
    sorted_licenses = sorted(by_license.keys(), key=lambda x: (flag_order.get(license_flags[x], 9), x))

    for lic_id in sorted_licenses:
        pkgs = by_license[lic_id]
        flag = license_flags[lic_id]
        pkg_count = f"{len(pkgs)} package{'s' if len(pkgs) != 1 else ''}"

        if flag != "OK":
            # Show package names for flagged licenses
            pkg_names = ", ".join(pkgs[:5])
            if len(pkgs) > 5:
                pkg_names += f", ... (+{len(pkgs) - 5} more)"
            print(f"  {flag:<10s} {lic_id:<25s} {pkg_count}: {pkg_names}")
        else:
            print(f"  {flag:<10s} {lic_id:<25s} {pkg_count}")

    # Summary
    warnings = sum(1 for lic in license_flags.values() if lic == "WARNING")
    infos = sum(1 for lic in license_flags.values() if lic == "INFO")
    total_flags = warnings + infos
    if total_flags:
        print(f"\nFlags: {total_flags} ({warnings} WARNING, {infos} INFO)")
    else:
        print("\nFlags: 0 — all licenses permissive")


def print_json(results: list[dict]) -> None:
    """Print JSON license report."""
    output = {
        "tool": "sca-license-check",
        "scope": "project",
        "total_dependencies": len(results),
        "flagged": [r for r in results if r["flag"] != "OK"],
        "summary": {},
    }

    # Count by flag
    for r in results:
        flag = r["flag"]
        output["summary"][flag] = output["summary"].get(flag, 0) + 1

    print(json.dumps(output, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Usage: license_check.py <sbom.json> [--json]", file=sys.stderr)
        sys.exit(1)

    sbom_path = sys.argv[1]
    json_mode = "--json" in sys.argv

    if not Path(sbom_path).exists():
        print(f"SBOM file not found: {sbom_path}", file=sys.stderr)
        sys.exit(1)

    with open(sbom_path) as f:
        sbom = json.load(f)

    # Verify it's CycloneDX format
    if sbom.get("bomFormat") != "CycloneDX":
        print("WARNING: File does not appear to be CycloneDX format", file=sys.stderr)

    results = extract_licenses(sbom)

    if json_mode:
        print_json(results)
    else:
        print_summary(results)


if __name__ == "__main__":
    main()
