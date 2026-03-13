#!/usr/bin/env bash
# Generate SBOM in CycloneDX JSON format
# Usage: run_sbom.sh <project-path> <output-file>
#
# Uses Syft if available, falls back to parsing package-lock.json
set -euo pipefail

PROJECT_PATH="${1:?Usage: run_sbom.sh <project-path> <output-file>}"
OUTPUT="${2:?Usage: run_sbom.sh <project-path> <output-file>}"

if ! [ -d "$PROJECT_PATH" ]; then
  echo "ERROR: Project path not found: $PROJECT_PATH" >&2
  exit 1
fi

# Resolve to absolute path
PROJECT_PATH="$(cd "$PROJECT_PATH" && pwd)"

if command -v syft &>/dev/null; then
  echo "Using Syft for SBOM generation..."
  echo "  Project: $PROJECT_PATH"
  echo "  Output:  $OUTPUT"

  syft scan "dir:${PROJECT_PATH}" -o "cyclonedx-json=${OUTPUT}" 2>/dev/null

  echo "Done. SBOM written to $OUTPUT"
else
  echo "Syft not available. Falling back to package-lock.json parser..."

  LOCKFILE="$PROJECT_PATH/package-lock.json"
  if [ ! -f "$LOCKFILE" ]; then
    echo "ERROR: No package-lock.json found at $PROJECT_PATH" >&2
    echo "Install Syft for non-npm projects: brew install syft" >&2
    exit 1
  fi

  # Get project name from package.json if available
  PROJ_NAME="unknown"
  if [ -f "$PROJECT_PATH/package.json" ]; then
    PROJ_NAME=$(python3 -c "import json; print(json.load(open('$PROJECT_PATH/package.json')).get('name', 'unknown'))" 2>/dev/null || echo "unknown")
  fi

  # Parse package-lock.json into CycloneDX format using Python
  python3 - "$LOCKFILE" "$OUTPUT" "$PROJ_NAME" <<'PYEOF'
import json
import sys

lockfile_path = sys.argv[1]
output_path = sys.argv[2]
project_name = sys.argv[3]

with open(lockfile_path) as f:
    lockdata = json.load(f)

components = []
packages = lockdata.get("packages", {})

for pkg_path, pkg_info in packages.items():
    # Skip the root package
    if not pkg_path:
        continue

    # Extract package name from the path
    # node_modules/express or node_modules/@scope/name
    parts = pkg_path.split("node_modules/")
    if len(parts) < 2:
        continue
    name = parts[-1]

    version = pkg_info.get("version", "unknown")

    component = {
        "type": "library",
        "name": name,
        "version": version,
        "purl": f"pkg:npm/{name}@{version}",
    }

    # Add license if available
    license_val = pkg_info.get("license")
    if license_val and isinstance(license_val, str):
        component["licenses"] = [{"license": {"id": license_val}}]

    components.append(component)

sbom = {
    "bomFormat": "CycloneDX",
    "specVersion": "1.5",
    "version": 1,
    "metadata": {
        "component": {
            "name": project_name,
            "type": "application",
        },
        "tools": [{"name": "sca-fallback", "version": "1.0.0"}],
    },
    "components": components,
}

with open(output_path, "w") as f:
    json.dump(sbom, f, indent=2)

print(f"Fallback SBOM generated: {len(components)} components")
PYEOF

  echo "Done. SBOM written to $OUTPUT"
fi
