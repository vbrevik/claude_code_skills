# API Fuzz Output Formats

## Pipeline JSON Format

Compatible with `/static-analysis`, `/sca`, `/container-security`, and `/stig-compliance` pipeline.

```json
{
  "tool": "api-fuzz",
  "scope": "http://localhost:3210",
  "timestamp": "2026-03-13T10:00:00Z",
  "findings": [
    {
      "id": "AF-001",
      "rule_id": "auth-bypass",
      "v_id": "V-222425",
      "cat": "I",
      "category": "authentication",
      "endpoint": "POST /api/mutation",
      "method": "POST",
      "severity": "HIGH",
      "message": "Endpoint accessible without authentication token",
      "response_code": 200,
      "snippet": "Response returned data without auth header"
    }
  ],
  "summary": {
    "total": 5,
    "endpoints_tested": 24,
    "by_cat": {"I": 2, "II": 2, "III": 1},
    "by_category": {"authentication": 2, "injection": 1, "disclosure": 1, "headers": 1}
  }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `tool` | string | Always `"api-fuzz"` |
| `scope` | string | Base URL that was tested |
| `timestamp` | string | ISO 8601 UTC timestamp of scan |
| `findings` | array | List of vulnerability findings |
| `findings[].id` | string | Sequential ID (`AF-001`, `AF-002`, ...) |
| `findings[].rule_id` | string | Test category ID (e.g., `auth-bypass`, `sql-injection`) |
| `findings[].v_id` | string | DISA STIG V-ID (e.g., `V-222425`) |
| `findings[].cat` | string | `"I"`, `"II"`, or `"III"` based on STIG CAT level |
| `findings[].category` | string | Broad category (e.g., `authentication`, `injection`, `disclosure`) |
| `findings[].endpoint` | string | `"METHOD /path"` format |
| `findings[].method` | string | HTTP method (`GET`, `POST`, `PUT`, `DELETE`, etc.) |
| `findings[].severity` | string | `HIGH`, `MEDIUM`, or `LOW` |
| `findings[].message` | string | Human-readable finding description |
| `findings[].response_code` | integer | HTTP response code from the probe |
| `findings[].snippet` | string | Truncated request/response detail (max 200 chars) |
| `summary.total` | integer | Total number of unique findings |
| `summary.endpoints_tested` | integer | Number of endpoints probed |
| `summary.by_cat` | object | Count of findings by STIG CAT level |
| `summary.by_category` | object | Count of findings by broad category |

## Human-Readable Table Format

Default output for terminal viewing:

```
API Fuzz Scan (http://localhost:3210): 5 findings (2 HIGH, 2 MEDIUM, 1 LOW)

  HIGH     auth-bypass            POST /api/mutation                  V-222425 (CAT I)     Endpoint accessible without authentication token
  HIGH     sql-injection          POST /api/query                     V-222578 (CAT I)     SQL error indicator in response to injection payload
  MEDIUM   missing-header-xcto    GET /                               V-222543 (CAT II)    Missing X-Content-Type-Options header
  MEDIUM   cors-wildcard          POST /api/mutation                  V-222596 (CAT II)    CORS allows all origins
  LOW      tech-disclosure        POST /api/query                     V-222602 (CAT III)   Error response discloses technology stack

Summary: 2 CAT I (block release), 2 CAT II (fix in maintenance cycle), 1 CAT III (track)
```

## OFFAT Native Output

When OFFAT is available, it produces its own JSON format with `results` array. The `offat_to_findings.py` script converts this to the pipeline format above.

Key OFFAT fields mapped:

| OFFAT Field | Pipeline Field |
|-------------|---------------|
| `test_name` | `message` |
| `url` / `endpoint` | `endpoint` |
| `method` / `http_method` | `method` |
| `severity` | `severity` (normalized to HIGH/MEDIUM/LOW) |
| `response_status_code` | `response_code` |
| `response_body` | `snippet` (truncated to 200 chars) |
| `result` | Used to filter: only `fail`/`vulnerable` results become findings |

## Curl Fallback Output

The curl-based fallback in `run_fuzz.sh` produces the same pipeline JSON format directly, with an additional `mode` field:

```json
{
  "tool": "api-fuzz",
  "scope": "http://localhost:3210",
  "mode": "curl-fallback",
  "timestamp": "...",
  "findings": [...],
  "summary": {...}
}
```

The `mode` field is used by `offat_to_findings.py` to auto-detect the input format.
