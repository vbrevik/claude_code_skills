#!/usr/bin/env bash
# Run nuclei with bundled STIG-mapped templates against a target URL
# Usage: run_scan.sh <target-url> <templates-dir> [output-file]
#
# Examples:
#   run_scan.sh http://localhost:5173 ./assets/nuclei-templates/
#   run_scan.sh http://localhost:3000 ./assets/nuclei-templates/ /tmp/dast-findings.jsonl

set -euo pipefail

TARGET="${1:?Usage: run_scan.sh <target-url> <templates-dir> [output-file]}"
TEMPLATES_DIR="${2:?Usage: run_scan.sh <target-url> <templates-dir> [output-file]}"
OUTPUT="${3:-/tmp/nuclei-stig-findings.jsonl}"

# Safety check: warn if target is not localhost
if [[ "$TARGET" != *"localhost"* && "$TARGET" != *"127.0.0.1"* && "$TARGET" != *"0.0.0.0"* ]]; then
  echo "WARNING: Target is not localhost. Ensure you have authorization to scan: $TARGET" >&2
  echo "Continuing in 3 seconds... (Ctrl+C to cancel)" >&2
  sleep 3
fi

# Check target is reachable
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$TARGET" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "000" ]; then
  echo "ERROR: Target unreachable: $TARGET" >&2
  echo '[]' > "$OUTPUT"
  exit 1
fi

if ! command -v nuclei &>/dev/null; then
  echo "WARNING: nuclei not found. Falling back to curl-based header checks." >&2
  echo "Install with: brew install nuclei (macOS) or go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest" >&2

  # Curl fallback: check critical headers
  echo "Running curl fallback checks against $TARGET..."
  HEADERS=$(curl -sI "$TARGET" 2>/dev/null)

  # Write simplified JSONL output for the parser
  > "$OUTPUT"

  check_header() {
    local header_name="$1"
    local template_id="$2"
    local message="$3"
    if ! echo "$HEADERS" | grep -qi "$header_name"; then
      echo "{\"template-id\":\"$template_id\",\"info\":{\"severity\":\"high\"},\"matched-at\":\"$TARGET\",\"matcher-name\":\"missing\",\"extracted-results\":[\"$message\"]}" >> "$OUTPUT"
    fi
  }

  check_header "content-security-policy" "stig-header-no-csp" "Missing Content-Security-Policy header"
  check_header "strict-transport-security" "stig-header-no-hsts" "Missing Strict-Transport-Security header"
  check_header "x-frame-options" "stig-header-no-xframe" "Missing X-Frame-Options header"
  check_header "x-content-type-options" "stig-header-no-xcontent" "Missing X-Content-Type-Options header"

  # Check for leaky headers
  if echo "$HEADERS" | grep -qi "x-powered-by"; then
    echo "{\"template-id\":\"stig-info-powered-by\",\"info\":{\"severity\":\"info\"},\"matched-at\":\"$TARGET\",\"matcher-name\":\"present\",\"extracted-results\":[\"X-Powered-By header present\"]}" >> "$OUTPUT"
  fi
  if echo "$HEADERS" | grep -qi "^server:"; then
    SERVER_VAL=$(echo "$HEADERS" | grep -i "^server:" | head -1 | tr -d '\r')
    echo "{\"template-id\":\"stig-info-server-header\",\"info\":{\"severity\":\"info\"},\"matched-at\":\"$TARGET\",\"matcher-name\":\"present\",\"extracted-results\":[\"$SERVER_VAL\"]}" >> "$OUTPUT"
  fi

  # Check cookies
  if echo "$HEADERS" | grep -qi "set-cookie"; then
    COOKIES=$(echo "$HEADERS" | grep -i "set-cookie" | tr -d '\r')
    if ! echo "$COOKIES" | grep -qi "httponly"; then
      echo "{\"template-id\":\"stig-cookie-no-httponly\",\"info\":{\"severity\":\"high\"},\"matched-at\":\"$TARGET\",\"matcher-name\":\"missing\",\"extracted-results\":[\"Session cookie missing HttpOnly flag\"]}" >> "$OUTPUT"
    fi
    if ! echo "$COOKIES" | grep -qi "secure"; then
      echo "{\"template-id\":\"stig-cookie-no-secure\",\"info\":{\"severity\":\"high\"},\"matched-at\":\"$TARGET\",\"matcher-name\":\"missing\",\"extracted-results\":[\"Session cookie missing Secure flag\"]}" >> "$OUTPUT"
    fi
    if ! echo "$COOKIES" | grep -qi "samesite"; then
      echo "{\"template-id\":\"stig-cookie-no-samesite\",\"info\":{\"severity\":\"high\"},\"matched-at\":\"$TARGET\",\"matcher-name\":\"missing\",\"extracted-results\":[\"Session cookie missing SameSite attribute\"]}" >> "$OUTPUT"
    fi
  fi

  FINDING_COUNT=$(wc -l < "$OUTPUT" | tr -d ' ')
  echo "Done (curl fallback). $FINDING_COUNT checks written to $OUTPUT"
  exit 0
fi

echo "Running nuclei DAST scan..."
echo "  Target: $TARGET"
echo "  Templates: $TEMPLATES_DIR"
echo "  Output: $OUTPUT"

nuclei \
  -u "$TARGET" \
  -t "$TEMPLATES_DIR" \
  -jsonl \
  -o "$OUTPUT" \
  -duc \
  -silent 2>/dev/null || true

echo "Done. Results written to $OUTPUT"
