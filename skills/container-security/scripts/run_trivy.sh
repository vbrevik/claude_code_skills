#!/usr/bin/env bash
# run_trivy.sh - Run Trivy scanner against Dockerfiles, K8s manifests, and images
# Usage: run_trivy.sh <project-root> <output-json> [mode]
#   mode: "all" (default), "docker", "k8s", "image:<name>"

set -euo pipefail

PROJECT_ROOT="${1:-.}"
OUTPUT="${2:-/tmp/container-scan.json}"
MODE="${3:-all}"

# Check trivy availability
if ! command -v trivy &>/dev/null; then
    echo '{"error": "trivy not installed", "fallback": true}' > "$OUTPUT"
    echo "ERROR: trivy is not installed. Use the fallback scanner instead." >&2
    echo "Install: brew install trivy (macOS) or see references/tools-setup.md" >&2
    exit 1
fi

RESULTS_DIR=$(mktemp -d)
SCAN_COUNT=0

scan_config() {
    local path="$1"
    local label="$2"
    local outfile="${RESULTS_DIR}/config_${SCAN_COUNT}.json"
    SCAN_COUNT=$((SCAN_COUNT + 1))

    echo "Scanning config: ${label}" >&2
    trivy config \
        --format json \
        --severity CRITICAL,HIGH,MEDIUM,LOW \
        --quiet \
        "$path" > "$outfile" 2>/dev/null || true
}

scan_image() {
    local image="$1"
    local outfile="${RESULTS_DIR}/image_${SCAN_COUNT}.json"
    SCAN_COUNT=$((SCAN_COUNT + 1))

    echo "Scanning image: ${image}" >&2
    trivy image \
        --format json \
        --severity CRITICAL,HIGH,MEDIUM,LOW \
        --quiet \
        "$image" > "$outfile" 2>/dev/null || true
}

# Image mode
if [[ "$MODE" == image:* ]]; then
    IMAGE_NAME="${MODE#image:}"
    scan_image "$IMAGE_NAME"
else
    # Scan Dockerfiles
    if [[ "$MODE" == "all" || "$MODE" == "docker" ]]; then
        while IFS= read -r -d '' dockerfile; do
            # Skip .worktrees, node_modules, .git
            case "$dockerfile" in
                */.worktrees/*|*/node_modules/*|*/.git/*) continue ;;
            esac
            scan_config "$dockerfile" "$dockerfile"
        done < <(find "$PROJECT_ROOT" -name "Dockerfile*" -print0 2>/dev/null)

        # Scan docker-compose files
        while IFS= read -r -d '' composefile; do
            case "$composefile" in
                */.worktrees/*|*/node_modules/*|*/.git/*) continue ;;
            esac
            scan_config "$composefile" "$composefile"
        done < <(find "$PROJECT_ROOT" \( -name "docker-compose*.yml" -o -name "docker-compose*.yaml" \) -print0 2>/dev/null)
    fi

    # Scan K8s manifests
    if [[ "$MODE" == "all" || "$MODE" == "k8s" ]]; then
        if [ -d "${PROJECT_ROOT}/k8s" ]; then
            scan_config "${PROJECT_ROOT}/k8s" "k8s/"
        fi

        # Also scan any other directories with K8s manifests
        while IFS= read -r -d '' yamlfile; do
            case "$yamlfile" in
                */.worktrees/*|*/node_modules/*|*/.git/*|*/k8s/*) continue ;;
            esac
            # Check if it looks like a K8s manifest
            if head -20 "$yamlfile" 2>/dev/null | grep -q "apiVersion:"; then
                scan_config "$yamlfile" "$yamlfile"
            fi
        done < <(find "$PROJECT_ROOT" \( -name "*.yaml" -o -name "*.yml" \) -not -path "*/k8s/*" -print0 2>/dev/null)
    fi
fi

# Merge all result files into one
echo "Merging ${SCAN_COUNT} scan results..." >&2
python3 -c "
import json, glob, sys, os

results = []
for f in sorted(glob.glob(os.path.join('${RESULTS_DIR}', '*.json'))):
    try:
        with open(f) as fh:
            data = json.load(fh)
            if isinstance(data, dict) and 'Results' in data:
                results.extend(data['Results'])
            elif isinstance(data, list):
                results.extend(data)
    except (json.JSONDecodeError, KeyError):
        pass

output = {'Results': results, 'scan_count': ${SCAN_COUNT}}
with open('${OUTPUT}', 'w') as out:
    json.dump(output, out, indent=2)

print(f'Wrote {len(results)} result sets to ${OUTPUT}', file=sys.stderr)
" 2>&1

# Cleanup
rm -rf "$RESULTS_DIR"

echo "Trivy scan complete: ${OUTPUT}" >&2
