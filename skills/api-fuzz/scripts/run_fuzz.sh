#!/usr/bin/env bash
# Run API fuzz testing with OFFAT or curl-based fallback
# Usage: run_fuzz.sh <base-url> [openapi-spec] <output-file>
#
# Uses OFFAT if available, falls back to curl-based probe suite
set -euo pipefail

# Parse arguments
if [ $# -lt 2 ]; then
  echo "Usage: run_fuzz.sh <base-url> [openapi-spec] <output-file>" >&2
  echo "  <base-url>     Target API base URL (e.g., http://localhost:3210)" >&2
  echo "  [openapi-spec] Optional path to OpenAPI spec file" >&2
  echo "  <output-file>  Path for JSON output" >&2
  exit 1
fi

BASE_URL="${1}"
if [ $# -eq 3 ]; then
  SPEC_FILE="${2}"
  OUTPUT="${3}"
elif [ $# -eq 2 ]; then
  SPEC_FILE=""
  OUTPUT="${2}"
else
  echo "ERROR: Invalid number of arguments" >&2
  exit 1
fi

# Validate URL format
if ! echo "$BASE_URL" | grep -qE '^https?://'; then
  echo "ERROR: Invalid URL format. Must start with http:// or https://" >&2
  exit 1
fi

# Strip trailing slash from base URL
BASE_URL="${BASE_URL%/}"

# Validate spec file if provided
if [ -n "$SPEC_FILE" ] && [ ! -f "$SPEC_FILE" ]; then
  echo "ERROR: OpenAPI spec file not found: $SPEC_FILE" >&2
  exit 1
fi

# Check if target is reachable
echo "Checking target connectivity: $BASE_URL"
if ! curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$BASE_URL" >/dev/null 2>&1; then
  echo "WARNING: Target $BASE_URL may not be reachable. Continuing anyway..." >&2
fi

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CURL_TIMEOUT=5

# ============================================================================
# OFFAT mode
# ============================================================================
if command -v offat &>/dev/null; then
  echo "Using OWASP OFFAT for API fuzzing..."
  echo "  Target: $BASE_URL"
  echo "  Output: $OUTPUT"

  OFFAT_ARGS=()

  if [ -n "$SPEC_FILE" ]; then
    echo "  Spec:   $SPEC_FILE"
    OFFAT_ARGS+=("-f" "$SPEC_FILE")
  fi

  OFFAT_ARGS+=("-o" "$OUTPUT")

  offat "${OFFAT_ARGS[@]}" 2>/dev/null || {
    echo "WARNING: OFFAT failed. Falling back to curl-based probes..." >&2
    # Fall through to curl mode
    OFFAT_FAILED=1
  }

  if [ "${OFFAT_FAILED:-0}" -eq 0 ]; then
    echo "Done. OFFAT results written to $OUTPUT"
    exit 0
  fi
fi

# ============================================================================
# Curl-based fallback probe suite
# ============================================================================
echo "Using curl-based probe suite (OFFAT not available)..."
echo "  Target: $BASE_URL"
echo "  Output: $OUTPUT"

# Temporary file for collecting probe results
PROBE_RESULTS=$(mktemp /tmp/api-fuzz-probes.XXXXXX)
echo "[]" > "$PROBE_RESULTS"

# Counter for finding IDs
FINDING_NUM=0

# Helper: add a finding to the results array
add_finding() {
  local rule_id="$1"
  local category="$2"
  local endpoint="$3"
  local method="$4"
  local severity="$5"
  local message="$6"
  local response_code="$7"
  local snippet="$8"

  FINDING_NUM=$((FINDING_NUM + 1))
  local fid
  fid=$(printf "AF-%03d" "$FINDING_NUM")

  python3 -c "
import json, sys
with open('$PROBE_RESULTS') as f:
    findings = json.load(f)
findings.append({
    'id': '$fid',
    'rule_id': '$rule_id',
    'category': '$category',
    'endpoint': '$method $endpoint',
    'method': '$method',
    'severity': '$severity',
    'message': '$message',
    'response_code': int('$response_code') if '$response_code'.isdigit() else 0,
    'snippet': '$snippet'
})
with open('$PROBE_RESULTS', 'w') as f:
    json.dump(findings, f)
" 2>/dev/null || true
}

# --- Common endpoints to probe (Convex HTTP endpoints) ---
ENDPOINTS=(
  "GET /"
  "GET /api"
  "POST /api/query"
  "POST /api/mutation"
  "POST /api/action"
  "GET /api/health"
  "GET /.well-known/openid-configuration"
  "GET /version"
)

# If spec file provided, extract endpoints from it
if [ -n "$SPEC_FILE" ]; then
  SPEC_ENDPOINTS=$(python3 -c "
import json, yaml, sys
try:
    with open('$SPEC_FILE') as f:
        content = f.read()
    try:
        spec = json.loads(content)
    except json.JSONDecodeError:
        spec = yaml.safe_load(content)
    paths = spec.get('paths', {})
    for path, methods in paths.items():
        for method in methods:
            if method.upper() in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH'):
                print(f'{method.upper()} {path}')
except Exception as e:
    print(f'# Failed to parse spec: {e}', file=sys.stderr)
" 2>/dev/null || echo "")

  if [ -n "$SPEC_ENDPOINTS" ]; then
    while IFS= read -r line; do
      ENDPOINTS+=("$line")
    done <<< "$SPEC_ENDPOINTS"
  fi
fi

ENDPOINTS_TESTED=0

echo ""
echo "=== Auth Bypass Tests ==="
for ep in "${ENDPOINTS[@]}"; do
  METHOD=$(echo "$ep" | cut -d' ' -f1)
  PATH_PART=$(echo "$ep" | cut -d' ' -f2-)
  URL="${BASE_URL}${PATH_PART}"
  ENDPOINTS_TESTED=$((ENDPOINTS_TESTED + 1))

  # Test without auth header
  HTTP_CODE=$(curl -s -o /tmp/api-fuzz-response.txt -w "%{http_code}" \
    --connect-timeout "$CURL_TIMEOUT" --max-time "$CURL_TIMEOUT" \
    -X "$METHOD" \
    -H "Content-Type: application/json" \
    "$URL" 2>/dev/null || echo "000")

  if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    RESPONSE_BODY=$(head -c 200 /tmp/api-fuzz-response.txt 2>/dev/null || echo "")
    add_finding "auth-bypass" "authentication" "$PATH_PART" "$METHOD" "HIGH" \
      "Endpoint accessible without authentication token (HTTP $HTTP_CODE)" \
      "$HTTP_CODE" "No auth header sent, got $HTTP_CODE response"
  fi

  # Test with invalid auth token
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    --connect-timeout "$CURL_TIMEOUT" --max-time "$CURL_TIMEOUT" \
    -X "$METHOD" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer invalid-token-12345" \
    "$URL" 2>/dev/null || echo "000")

  if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    add_finding "auth-bypass" "authentication" "$PATH_PART" "$METHOD" "HIGH" \
      "Endpoint accepts invalid bearer token (HTTP $HTTP_CODE)" \
      "$HTTP_CODE" "Sent invalid bearer token, got $HTTP_CODE response"
  fi
done

echo "=== Injection Tests ==="
INJECTION_PAYLOADS=(
  "' OR 1=1--"
  "'; DROP TABLE users;--"
  "<script>alert(1)</script>"
  "<img src=x onerror=alert(1)>"
  "../../../etc/passwd"
  "..\\..\\..\\windows\\system32\\config\\sam"
  "{{7*7}}"
  "\${7*7}"
)

for ep in "${ENDPOINTS[@]}"; do
  METHOD=$(echo "$ep" | cut -d' ' -f1)
  PATH_PART=$(echo "$ep" | cut -d' ' -f2-)
  URL="${BASE_URL}${PATH_PART}"

  if [ "$METHOD" = "POST" ] || [ "$METHOD" = "PUT" ] || [ "$METHOD" = "PATCH" ]; then
    for payload in "${INJECTION_PAYLOADS[@]}"; do
      # Send injection payload in JSON body
      BODY="{\"input\": \"$payload\"}"
      HTTP_CODE=$(curl -s -o /tmp/api-fuzz-response.txt -w "%{http_code}" \
        --connect-timeout "$CURL_TIMEOUT" --max-time "$CURL_TIMEOUT" \
        -X "$METHOD" \
        -H "Content-Type: application/json" \
        -d "$BODY" \
        "$URL" 2>/dev/null || echo "000")

      RESPONSE_BODY=$(cat /tmp/api-fuzz-response.txt 2>/dev/null || echo "")

      # Check if payload is reflected in response (XSS indicator)
      if echo "$RESPONSE_BODY" | grep -qF "$payload" 2>/dev/null; then
        if echo "$payload" | grep -q "script\|onerror\|img" 2>/dev/null; then
          add_finding "xss" "injection" "$PATH_PART" "$METHOD" "HIGH" \
            "XSS payload reflected in response" \
            "$HTTP_CODE" "Payload reflected: ${payload:0:50}"
        fi
      fi

      # Check for SQL error indicators
      if echo "$RESPONSE_BODY" | grep -qiE "sql|syntax|mysql|postgresql|sqlite|oracle|ORA-" 2>/dev/null; then
        add_finding "sql-injection" "injection" "$PATH_PART" "$METHOD" "HIGH" \
          "SQL error indicator in response to injection payload" \
          "$HTTP_CODE" "SQL-related text in response body"
      fi

      # Check for path traversal success indicators
      if echo "$RESPONSE_BODY" | grep -qE "root:|\\[boot loader\\]|\\[extensions\\]" 2>/dev/null; then
        add_finding "path-traversal" "injection" "$PATH_PART" "$METHOD" "HIGH" \
          "Path traversal may have succeeded" \
          "$HTTP_CODE" "System file content detected in response"
      fi
    done
  fi

  # Test injection in query parameters (for all methods)
  for payload in "' OR 1=1--" "<script>alert(1)</script>" "../../../etc/passwd"; do
    ENCODED_PAYLOAD=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$payload'))" 2>/dev/null || echo "$payload")
    HTTP_CODE=$(curl -s -o /tmp/api-fuzz-response.txt -w "%{http_code}" \
      --connect-timeout "$CURL_TIMEOUT" --max-time "$CURL_TIMEOUT" \
      -X "$METHOD" \
      "${URL}?q=${ENCODED_PAYLOAD}" 2>/dev/null || echo "000")

    RESPONSE_BODY=$(cat /tmp/api-fuzz-response.txt 2>/dev/null || echo "")
    if echo "$RESPONSE_BODY" | grep -qF "$payload" 2>/dev/null; then
      add_finding "xss" "injection" "${PATH_PART}?q=..." "$METHOD" "HIGH" \
        "Injection payload reflected in query parameter response" \
        "$HTTP_CODE" "Query param injection reflected"
    fi
  done
done

echo "=== Security Headers Tests ==="
FIRST_URL="${BASE_URL}/"
HEADERS=$(curl -s -I --connect-timeout "$CURL_TIMEOUT" --max-time "$CURL_TIMEOUT" "$FIRST_URL" 2>/dev/null || echo "")

if [ -n "$HEADERS" ]; then
  ENDPOINTS_TESTED=$((ENDPOINTS_TESTED + 1))

  if ! echo "$HEADERS" | grep -qi "X-Content-Type-Options" 2>/dev/null; then
    add_finding "missing-header-xcto" "headers" "/" "GET" "MEDIUM" \
      "Missing X-Content-Type-Options header" \
      "200" "Header X-Content-Type-Options not present"
  fi

  if ! echo "$HEADERS" | grep -qi "X-Frame-Options" 2>/dev/null; then
    add_finding "missing-header-xfo" "headers" "/" "GET" "MEDIUM" \
      "Missing X-Frame-Options header" \
      "200" "Header X-Frame-Options not present"
  fi

  if ! echo "$HEADERS" | grep -qi "Strict-Transport-Security" 2>/dev/null; then
    add_finding "missing-header-hsts" "headers" "/" "GET" "MEDIUM" \
      "Missing Strict-Transport-Security header" \
      "200" "Header Strict-Transport-Security not present"
  fi

  if ! echo "$HEADERS" | grep -qi "Content-Security-Policy" 2>/dev/null; then
    add_finding "missing-header-csp" "headers" "/" "GET" "MEDIUM" \
      "Missing Content-Security-Policy header" \
      "200" "Header Content-Security-Policy not present"
  fi
fi

echo "=== CORS Tests ==="
for ep in "${ENDPOINTS[@]}"; do
  METHOD=$(echo "$ep" | cut -d' ' -f1)
  PATH_PART=$(echo "$ep" | cut -d' ' -f2-)
  URL="${BASE_URL}${PATH_PART}"

  CORS_RESPONSE=$(curl -s -I --connect-timeout "$CURL_TIMEOUT" --max-time "$CURL_TIMEOUT" \
    -H "Origin: https://evil.example.com" \
    -X OPTIONS \
    "$URL" 2>/dev/null || echo "")

  if echo "$CORS_RESPONSE" | grep -qi "Access-Control-Allow-Origin: \*" 2>/dev/null; then
    add_finding "cors-wildcard" "cors" "$PATH_PART" "OPTIONS" "MEDIUM" \
      "CORS allows all origins (Access-Control-Allow-Origin: *)" \
      "200" "Wildcard CORS origin detected"
  elif echo "$CORS_RESPONSE" | grep -qi "Access-Control-Allow-Origin: https://evil.example.com" 2>/dev/null; then
    add_finding "cors-reflection" "cors" "$PATH_PART" "OPTIONS" "HIGH" \
      "CORS reflects arbitrary Origin header" \
      "200" "Origin reflection: evil.example.com accepted"
  fi
done

echo "=== Error Disclosure Tests ==="
for ep in "${ENDPOINTS[@]}"; do
  METHOD=$(echo "$ep" | cut -d' ' -f1)
  PATH_PART=$(echo "$ep" | cut -d' ' -f2-)
  URL="${BASE_URL}${PATH_PART}"

  # Send malformed request to trigger error
  HTTP_CODE=$(curl -s -o /tmp/api-fuzz-response.txt -w "%{http_code}" \
    --connect-timeout "$CURL_TIMEOUT" --max-time "$CURL_TIMEOUT" \
    -X "$METHOD" \
    -H "Content-Type: application/json" \
    -d "{invalid json" \
    "$URL" 2>/dev/null || echo "000")

  RESPONSE_BODY=$(cat /tmp/api-fuzz-response.txt 2>/dev/null || echo "")

  # Check for stack trace / internal details disclosure
  if echo "$RESPONSE_BODY" | grep -qEi "stack trace|traceback|at .+\(.+:[0-9]+\)|node_modules|internal/" 2>/dev/null; then
    add_finding "error-disclosure" "disclosure" "$PATH_PART" "$METHOD" "MEDIUM" \
      "Error response contains stack trace or internal details" \
      "$HTTP_CODE" "Stack trace or internal paths found in error response"
  fi

  # Check for technology disclosure in error
  if echo "$RESPONSE_BODY" | grep -qEi "express|convex|next\.js|django|flask|laravel|spring" 2>/dev/null; then
    add_finding "tech-disclosure" "disclosure" "$PATH_PART" "$METHOD" "LOW" \
      "Error response discloses technology stack" \
      "$HTTP_CODE" "Technology name found in error response"
  fi
done

echo "=== Rate Limiting Tests ==="
RATE_URL="${BASE_URL}$(echo "${ENDPOINTS[0]}" | cut -d' ' -f2-)"
RATE_METHOD=$(echo "${ENDPOINTS[0]}" | cut -d' ' -f1)
ALL_200=true
for i in $(seq 1 20); do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    --connect-timeout "$CURL_TIMEOUT" --max-time "$CURL_TIMEOUT" \
    -X "$RATE_METHOD" \
    "$RATE_URL" 2>/dev/null || echo "000")
  if [ "$HTTP_CODE" = "429" ]; then
    ALL_200=false
    break
  fi
done

if [ "$ALL_200" = true ]; then
  FIRST_EP_PATH=$(echo "${ENDPOINTS[0]}" | cut -d' ' -f2-)
  add_finding "no-rate-limit" "rate-limiting" "$FIRST_EP_PATH" "$RATE_METHOD" "MEDIUM" \
    "No rate limiting detected after 20 rapid requests" \
    "200" "20 consecutive requests returned 200, no 429 response"
fi

# ============================================================================
# Assemble final output
# ============================================================================
echo ""
echo "Assembling results..."

python3 -c "
import json
from datetime import datetime, timezone

with open('$PROBE_RESULTS') as f:
    findings = json.load(f)

# Deduplicate: same endpoint + same rule_id = one finding
seen = set()
deduped = []
for f in findings:
    key = (f['endpoint'], f['rule_id'])
    if key not in seen:
        seen.add(key)
        deduped.append(f)

# Build summary
by_cat = {}
by_category = {}
for f in deduped:
    # Map severity to cat for summary
    sev = f.get('severity', 'MEDIUM')
    cat = {'HIGH': 'I', 'MEDIUM': 'II', 'LOW': 'III'}.get(sev, 'II')
    by_cat[cat] = by_cat.get(cat, 0) + 1
    cat_name = f.get('category', 'unknown')
    by_category[cat_name] = by_category.get(cat_name, 0) + 1

output = {
    'tool': 'api-fuzz',
    'scope': '$BASE_URL',
    'mode': 'curl-fallback',
    'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'findings': deduped,
    'summary': {
        'total': len(deduped),
        'endpoints_tested': $ENDPOINTS_TESTED,
        'by_cat': by_cat,
        'by_category': by_category,
    }
}

with open('$OUTPUT', 'w') as f:
    json.dump(output, f, indent=2)

print(f'Done. {len(deduped)} findings written to $OUTPUT')
" 2>/dev/null

# Cleanup
rm -f "$PROBE_RESULTS" /tmp/api-fuzz-response.txt
