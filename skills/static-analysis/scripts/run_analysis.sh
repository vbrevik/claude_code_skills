#!/usr/bin/env bash
# Run semgrep with bundled STIG-mapped rules and output SARIF
# Usage: run_analysis.sh "<space-separated file list or directory>" <rules-dir> [output-file]
#
# Examples:
#   run_analysis.sh "src/auth.ts src/api.ts" ./assets/semgrep-rules/
#   run_analysis.sh "src/" ./assets/semgrep-rules/ /tmp/findings.sarif
#   run_analysis.sh "$(git diff --name-only)" ./assets/semgrep-rules/

set -euo pipefail

TARGETS="${1:-.}"
RULES_DIR="${2:?Usage: run_analysis.sh <targets> <rules-dir> [output-file]}"
OUTPUT="${3:-/tmp/semgrep-stig-findings.sarif}"

if ! command -v semgrep &>/dev/null; then
  echo "ERROR: semgrep not found. Install with: brew install semgrep (macOS) or pip install semgrep (Linux)" >&2
  exit 1
fi

if [ ! -d "$RULES_DIR" ]; then
  echo "ERROR: Rules directory not found: $RULES_DIR" >&2
  exit 1
fi

# Filter targets to only existing files/directories
VALID_TARGETS=""
for target in $TARGETS; do
  if [ -e "$target" ]; then
    VALID_TARGETS="$VALID_TARGETS $target"
  fi
done

if [ -z "$VALID_TARGETS" ]; then
  echo "No valid targets found. Nothing to scan." >&2
  echo '{"runs":[{"results":[]}]}' > "$OUTPUT"
  exit 0
fi

echo "Running semgrep with STIG rules..."
echo "  Rules: $RULES_DIR"
echo "  Targets: $VALID_TARGETS"
echo "  Output: $OUTPUT"

semgrep \
  --config "$RULES_DIR" \
  --sarif \
  --output "$OUTPUT" \
  --no-git-ignore \
  --quiet \
  $VALID_TARGETS 2>/dev/null || true

echo "Done. Results written to $OUTPUT"
