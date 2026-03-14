#!/usr/bin/env bash
# run_scan.sh — Wrapper for gitleaks secret scanning with grep fallback
#
# Usage:
#   run_scan.sh <source-path> <config-path> <output-json> [--full|--diff]
#
# Arguments:
#   source-path   Path to the git repository to scan
#   config-path   Path to gitleaks.toml config file
#   output-json   Path to write JSON findings
#   --full        Scan full git history (default)
#   --diff        Scan only latest commit diff

set -euo pipefail

SOURCE_PATH="${1:-.}"
CONFIG_PATH="${2:-}"
OUTPUT_JSON="${3:-/tmp/gitleaks-output.json}"
MODE="${4:---full}"

# Resolve absolute paths
SOURCE_PATH="$(cd "$SOURCE_PATH" && pwd)"

# Check if gitleaks is available
if command -v gitleaks &>/dev/null; then
    GITLEAKS_VERSION="$(gitleaks version 2>/dev/null || echo 'unknown')"
    echo "Using gitleaks ${GITLEAKS_VERSION}"

    # Build command args
    ARGS=(detect --source "$SOURCE_PATH" --report-format json --report-path "$OUTPUT_JSON" --no-banner)

    # Add config if provided and exists
    if [[ -n "$CONFIG_PATH" && -f "$CONFIG_PATH" ]]; then
        ARGS+=(--config "$CONFIG_PATH")
        echo "Config: $CONFIG_PATH"
    fi

    # Set mode
    if [[ "$MODE" == "--diff" ]]; then
        ARGS+=(--log-opts="HEAD~1..HEAD")
        echo "Scope: git-diff (latest commit)"
    else
        echo "Scope: git-history (full)"
    fi

    echo "Scanning: $SOURCE_PATH"
    echo "Output:   $OUTPUT_JSON"
    echo ""

    # gitleaks exits 1 if findings are present, 0 if clean
    if gitleaks "${ARGS[@]}" 2>/dev/null; then
        echo "No secrets detected."
        # Write empty findings array if file wasn't created
        if [[ ! -f "$OUTPUT_JSON" ]]; then
            echo "[]" > "$OUTPUT_JSON"
        fi
    else
        EXIT_CODE=$?
        if [[ $EXIT_CODE -eq 1 && -f "$OUTPUT_JSON" ]]; then
            COUNT=$(python3 -c "import json; print(len(json.load(open('$OUTPUT_JSON'))))" 2>/dev/null || echo "?")
            echo "Findings detected: $COUNT"
        else
            echo "gitleaks exited with code $EXIT_CODE"
            # Ensure output file exists
            if [[ ! -f "$OUTPUT_JSON" ]]; then
                echo "[]" > "$OUTPUT_JSON"
            fi
        fi
    fi
else
    echo "WARNING: gitleaks not found — falling back to grep-based detection"
    echo "Install gitleaks for comprehensive scanning (see references/gitleaks-setup.md)"
    echo ""
    echo "Scope: grep-based pattern scan"
    echo "Scanning: $SOURCE_PATH"
    echo ""

    # Grep-based fallback for common secret patterns
    FINDINGS="[]"
    TEMP_FINDINGS=$(mktemp)
    echo "[" > "$TEMP_FINDINGS"
    FIRST=true

    # Patterns to search for
    declare -a PATTERNS=(
        'password\s*[=:]\s*["\x27][^"\x27]{4,}'
        'api[_-]?key\s*[=:]\s*["\x27][^"\x27]{8,}'
        'secret\s*[=:]\s*["\x27][^"\x27]{8,}'
        'token\s*[=:]\s*["\x27][^"\x27]{8,}'
        'BEGIN\s+(RSA|DSA|EC|PGP)\s+PRIVATE\s+KEY'
        '(postgres|mysql|mongodb)://[^:]+:[^@]+@'
        'AKIA[0-9A-Z]{16}'
        'sk_live_[0-9a-zA-Z]{24,}'
        'ghp_[0-9a-zA-Z]{36}'
        'glpat-[0-9a-zA-Z\-]{20,}'
    )

    declare -a RULE_IDS=(
        "generic-password"
        "generic-api-key"
        "generic-secret"
        "generic-token"
        "private-key"
        "password-in-url"
        "aws-access-key-id"
        "stripe-api-key"
        "github-pat"
        "gitlab-pat"
    )

    for i in "${!PATTERNS[@]}"; do
        PATTERN="${PATTERNS[$i]}"
        RULE_ID="${RULE_IDS[$i]}"

        while IFS=: read -r FILE LINE_NUM MATCH; do
            if [[ -n "$FILE" ]]; then
                # Skip binary files and common non-code files
                case "$FILE" in
                    *.lock|*.min.js|*.map|node_modules/*|.git/*) continue ;;
                esac

                # Truncate match for snippet
                SNIPPET="${MATCH:0:60}"
                SNIPPET="${SNIPPET//\"/\\\"}"

                if [[ "$FIRST" == "true" ]]; then
                    FIRST=false
                else
                    echo "," >> "$TEMP_FINDINGS"
                fi

                cat >> "$TEMP_FINDINGS" <<ENTRY
  {
    "Description": "$RULE_ID match",
    "File": "$FILE",
    "StartLine": $LINE_NUM,
    "RuleID": "$RULE_ID",
    "Match": "$SNIPPET",
    "Entropy": 0,
    "Commit": "",
    "Author": "",
    "Date": ""
  }
ENTRY
            fi
        done < <(grep -rnE "$PATTERN" "$SOURCE_PATH" \
            --include="*.ts" --include="*.js" --include="*.py" --include="*.go" \
            --include="*.java" --include="*.yaml" --include="*.yml" --include="*.json" \
            --include="*.toml" --include="*.env" --include="*.cfg" --include="*.conf" \
            --include="*.properties" --include="*.xml" --include="*.sh" \
            2>/dev/null || true)
    done

    echo "" >> "$TEMP_FINDINGS"
    echo "]" >> "$TEMP_FINDINGS"

    mv "$TEMP_FINDINGS" "$OUTPUT_JSON"
    COUNT=$(python3 -c "import json; print(len(json.load(open('$OUTPUT_JSON'))))" 2>/dev/null || echo "?")
    echo "Grep-based findings: $COUNT"
fi

echo ""
echo "Results written to: $OUTPUT_JSON"
