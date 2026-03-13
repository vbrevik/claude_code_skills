#!/usr/bin/env bash
# run_kubescape.sh - Run Kubescape NSA framework scan against K8s manifests
# Usage: run_kubescape.sh <k8s-dir> <output-json>

set -euo pipefail

K8S_DIR="${1:-.}"
OUTPUT="${2:-/tmp/kubescape-scan.json}"

# Check kubescape availability
if ! command -v kubescape &>/dev/null; then
    echo '{"error": "kubescape not installed", "fallback": true}' > "$OUTPUT"
    echo "ERROR: kubescape is not installed. Trivy and fallback scanner cover most checks." >&2
    echo "Install: curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | bash" >&2
    exit 1
fi

if [ ! -d "$K8S_DIR" ]; then
    echo "ERROR: Directory not found: ${K8S_DIR}" >&2
    exit 1
fi

echo "Running Kubescape NSA framework scan on: ${K8S_DIR}" >&2

kubescape scan framework nsa \
    --format json \
    --output "$OUTPUT" \
    "$K8S_DIR" 2>&1 || {
    echo "WARNING: Kubescape scan encountered errors. Partial results may be in ${OUTPUT}" >&2
}

if [ -f "$OUTPUT" ]; then
    echo "Kubescape scan complete: ${OUTPUT}" >&2
else
    echo '{"error": "kubescape produced no output"}' > "$OUTPUT"
    echo "WARNING: Kubescape produced no output" >&2
fi
