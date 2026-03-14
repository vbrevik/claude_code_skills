#!/usr/bin/env bash
# Scan SBOM for vulnerabilities
# Usage: run_vuln_scan.sh <sbom-file> <output-file> [project-path]
#
# Uses Grype if available, falls back to npm audit
set -euo pipefail

SBOM_FILE="${1:?Usage: run_vuln_scan.sh <sbom-file> <output-file> [project-path]}"
OUTPUT="${2:?Usage: run_vuln_scan.sh <sbom-file> <output-file> [project-path]}"
PROJECT_PATH="${3:-.}"

if [ ! -f "$SBOM_FILE" ]; then
  echo "ERROR: SBOM file not found: $SBOM_FILE" >&2
  exit 1
fi

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
GRYPE_CONFIG="$SKILL_DIR/assets/grype-config.yaml"

if command -v grype &>/dev/null; then
  echo "Using Grype for vulnerability scanning..."
  echo "  SBOM:   $SBOM_FILE"
  echo "  Output: $OUTPUT"

  GRYPE_ARGS=("sbom:${SBOM_FILE}" "-o" "json")

  if [ -f "$GRYPE_CONFIG" ]; then
    GRYPE_ARGS+=("-c" "$GRYPE_CONFIG")
    echo "  Config: $GRYPE_CONFIG"
  fi

  grype "${GRYPE_ARGS[@]}" > "$OUTPUT" 2>/dev/null

  echo "Done. Vulnerability scan written to $OUTPUT"
else
  echo "Grype not available. Falling back to npm audit..."

  # Find project path — try to locate package.json
  if [ ! -f "$PROJECT_PATH/package.json" ]; then
    # Try to extract project path from SBOM metadata
    DETECTED_PATH=$(python3 -c "
import json, sys
with open('$SBOM_FILE') as f:
    sbom = json.load(f)
meta = sbom.get('metadata', {}).get('component', {})
print(meta.get('name', '.'))
" 2>/dev/null || echo ".")
    echo "  Note: Using project path '$PROJECT_PATH' for npm audit"
  fi

  if [ -f "$PROJECT_PATH/package.json" ]; then
    echo "  Project: $PROJECT_PATH"
    echo "  Output:  $OUTPUT"

    # Run npm audit from the project directory
    (cd "$PROJECT_PATH" && npm audit --json > "$OUTPUT" 2>/dev/null) || true

    # Check if output was created and has content
    if [ -s "$OUTPUT" ]; then
      echo "Done. npm audit results written to $OUTPUT"
      echo "  Note: Use --npm-audit flag with grype_to_findings.py to parse this format"
    else
      echo "npm audit produced no output. Creating empty result."
      echo '{"vulnerabilities":{}}' > "$OUTPUT"
    fi
  else
    echo "ERROR: No package.json found. Cannot run npm audit fallback." >&2
    echo "Install Grype for non-npm projects: brew install grype" >&2
    echo '{"vulnerabilities":{}}' > "$OUTPUT"
    exit 1
  fi
fi
