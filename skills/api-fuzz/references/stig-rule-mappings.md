# STIG Rule Mappings for API Fuzz Findings

## Source

DISA ASD STIG V5R3 -- Application Security and Development

## Mapping Table

| Test Category | Rule ID | V-ID | CAT | STIG Title | Rationale |
|--------------|---------|------|-----|------------|-----------|
| Auth bypass | auth-bypass | V-222425 | I | The application must implement approved authorizations for logical access to information and system resources in accordance with applicable access control policies | Unauthenticated access to protected endpoints means authorization controls are absent or bypassable |
| Authorization (BOLA) | bola | V-222425 | I | The application must implement approved authorizations for logical access to information and system resources | Broken Object Level Authorization allows accessing other users' resources by manipulating IDs |
| SQL injection | sql-injection | V-222578 | I | The application must not be subject to input handling vulnerabilities | SQL injection through unvalidated input allows arbitrary database operations |
| XSS | xss | V-222577 | I | The application must not be vulnerable to cross-site scripting (XSS) | Reflected or stored XSS enables session hijacking and data exfiltration |
| SSRF | ssrf | V-222604 | I | The application must not be subject to error handling vulnerabilities | Server-side request forgery enables internal network scanning and data access |
| Path traversal | path-traversal | V-222604 | I | The application must not be subject to error handling vulnerabilities | Path traversal enables reading arbitrary files from the server filesystem |
| Error disclosure | error-disclosure | V-222602 | II | The application must not reveal error messages to unauthorized users that include technical details | Stack traces, internal paths, and debug info in error responses aid attackers |
| Technology disclosure | tech-disclosure | V-222602 | II | The application must not reveal error messages to unauthorized users that include technical details | Framework/technology names in errors help attackers target known vulnerabilities |
| Input validation | input-validation | V-222606 | II | The application must validate all input | Insufficient input validation enables injection and data corruption |
| Mass assignment | mass-assignment | V-222606 | II | The application must validate all input | Accepting unexpected parameters allows privilege escalation |
| Schema violation | schema-violation | V-222606 | II | The application must validate all input | Accepting malformed data indicates insufficient schema validation |
| Missing X-Content-Type-Options | missing-header-xcto | V-222543 | II | The application must implement cryptographic mechanisms to protect the integrity of information | Missing XCTO header allows MIME-type sniffing attacks |
| Missing X-Frame-Options | missing-header-xfo | V-222543 | II | The application must implement cryptographic mechanisms to protect the integrity of information | Missing XFO header allows clickjacking attacks |
| Missing HSTS | missing-header-hsts | V-222543 | II | The application must implement cryptographic mechanisms to protect the integrity of information | Missing HSTS allows SSL stripping attacks |
| Missing CSP | missing-header-csp | V-222543 | II | The application must implement cryptographic mechanisms to protect the integrity of information | Missing CSP allows injection of unauthorized scripts |
| CORS wildcard | cors-wildcard | V-222596 | II | The application must enforce approved authorizations for controlling the flow of information | Wildcard CORS origin allows any site to make authenticated requests |
| CORS reflection | cors-reflection | V-222596 | II | The application must enforce approved authorizations for controlling the flow of information | Reflecting arbitrary origins is equivalent to wildcard and enables CSRF-like attacks |
| Rate limiting | no-rate-limit | V-222549 | II | The application must protect against or limit the effects of denial of service attacks | Absence of rate limiting enables brute force and resource exhaustion attacks |

## CAT Level Definitions

| CAT | Severity | Action Required |
|-----|----------|----------------|
| I | High | Must fix before deployment. Finding indicates a direct path to compromise. |
| II | Medium | Fix within maintenance cycle. Finding aids an attacker or weakens defenses. |
| III | Low | Track and remediate. Finding is informational or low-impact. |

## Pipeline Integration

Findings use the following JSON schema for `/stig-compliance` consumption:

```json
{
  "rule_id": "<test-category-id>",
  "v_id": "V-NNNNNN",
  "cat": "I|II|III",
  "category": "<broad-category>",
  "endpoint": "METHOD /path",
  "method": "GET|POST|...",
  "severity": "HIGH|MEDIUM|LOW",
  "message": "<human-readable description>",
  "response_code": 200,
  "snippet": "<truncated response or request detail>"
}
```

Source attribution in `/stig-compliance` reports: `Source: offat (dynamic)` or `Source: curl-probe (dynamic)`.
