# STIG Threat Mappings

## STRIDE to STIG V-ID Mappings

Complete mapping from STRIDE threat categories to DISA STIG V-IDs (Application Security and Development STIG V5R3).

### Spoofing

| Threat Pattern | V-ID | CAT | Typical Finding |
|---------------|------|-----|-----------------|
| Missing authentication on endpoint | V-222425 | I | API endpoint accessible without authentication |
| Weak authentication mechanism | V-222425 | I | Password-only auth on privileged operations |
| Missing mutual authentication (service-to-service) | V-222543 | I | Inter-service calls without mTLS or API key |
| Session token prediction/theft | V-222425 | I | Predictable session identifiers |
| OIDC token replay | V-222425 | I | No nonce/timestamp validation on OIDC tokens |
| Missing CSRF protection | V-222425 | II | State-changing requests without CSRF tokens |
| Certificate validation bypass | V-222543 | I | TLS certificate not validated |

### Tampering

| Threat Pattern | V-ID | CAT | Typical Finding |
|---------------|------|-----|-----------------|
| SQL/NoSQL injection | V-222578 | I | User input concatenated into queries |
| XML injection | V-222578 | I | Unvalidated XML in diode envelopes |
| Missing input validation | V-222578 | II | API accepts arbitrary input without schema validation |
| Parameter tampering (IDOR) | V-222536 | II | Object IDs in URLs not verified against user context |
| Missing message integrity | V-222536 | II | Messages crossing trust boundaries without HMAC/signature |
| Prototype pollution | V-222578 | II | JavaScript object manipulation via `__proto__` |
| Mass assignment | V-222578 | II | Extra fields in request body accepted by mutation |

### Repudiation

| Threat Pattern | V-ID | CAT | Typical Finding |
|---------------|------|-----|-----------------|
| Missing audit logging | V-222610 | II | Security-relevant action not logged |
| Insufficient audit detail | V-222610 | II | Audit log missing actor identity or timestamp |
| Mutable audit logs | V-222610 | I | Audit records can be modified or deleted |
| Missing failed auth logging | V-222610 | II | Failed login attempts not recorded |
| No correlation across services | V-222610 | III | Distributed actions cannot be traced end-to-end |
| Client-controlled timestamps | V-222610 | II | Audit timestamps from untrusted source |

### Information Disclosure

| Threat Pattern | V-ID | CAT | Typical Finding |
|---------------|------|-----|-----------------|
| Stack trace in error response | V-222602 | II | Production errors include stack trace |
| Verbose error messages | V-222602 | II | Error reveals database schema or internal paths |
| Hardcoded credentials | V-222642 | I | API keys or passwords in source code |
| Credentials in logs | V-222642 | I | Tokens or passwords written to log files |
| PII in error messages | V-222602 | II | Personal data included in error responses |
| Missing encryption at rest | V-222642 | II | Sensitive data stored unencrypted |
| Missing encryption in transit | V-222543 | I | Data transmitted without TLS |
| CORS misconfiguration | V-222602 | II | Overly permissive CORS allowing data exfiltration |

### Denial of Service

| Threat Pattern | V-ID | CAT | Typical Finding |
|---------------|------|-----|-----------------|
| No rate limiting | V-222549 | II | API endpoint accepts unlimited requests |
| Unbounded resource consumption | V-222549 | II | No limits on upload size, query depth, or pagination |
| Missing timeouts | V-222549 | II | External service calls without timeout |
| Queue flooding | V-222549 | II | Message queue accepts unlimited messages |
| ReDoS vulnerability | V-222549 | II | Regex pattern vulnerable to catastrophic backtracking |
| XML bomb / billion laughs | V-222549 | I | XML parser vulnerable to entity expansion |
| No circuit breaker | V-222549 | III | Cascading failure when dependency is unavailable |

### Elevation of Privilege

| Threat Pattern | V-ID | CAT | Typical Finding |
|---------------|------|-----|-----------------|
| Missing authorization check | V-222425 | I | Endpoint lacks role/permission verification |
| Broken function-level auth | V-222425 | I | Admin functions accessible to regular users |
| ABAC policy bypass | V-222425 | I | Policy can be circumvented by crafted attributes |
| State machine bypass | V-222425 | I | Visit state can be advanced without required approvals |
| Cross-classification access | V-222425 | I | UNCLASSIFIED code accessing RESTRICTED operations |
| Path traversal | V-222425 | II | File system access beyond intended scope |
| Insecure deserialization | V-222425 | I | Untrusted data deserialized to gain code execution |

## LINDDUN to STIG V-ID Mappings

LINDDUN threats map to STIG V-IDs where applicable. Some privacy threats do not have direct STIG equivalents and are tracked as GDPR compliance findings.

| LINDDUN Category | V-ID | CAT | Typical Finding |
|-----------------|------|-----|-----------------|
| Linking (data correlation) | V-222642 | II | Persistent identifiers enable cross-dataset linking |
| Identifying (re-identification) | V-222642 | II | Quasi-identifiers enable de-anonymization |
| Non-repudiation (unwanted proof) | V-222610 | III | Excessive audit retention creating privacy risk |
| Detecting (behavior detection) | V-222642 | III | Metadata patterns reveal user behavior |
| Data Disclosure (PII leak) | V-222642 | I | Personal data exposed to unauthorized parties |
| Unawareness (no transparency) | — | II | No STIG V-ID; GDPR Art. 13/14 finding |
| Non-compliance (regulatory) | V-222610 | II | Processing without valid legal basis |

## Risk Score to CAT Mapping

| Risk Score (Likelihood x Impact) | CAT Level | Severity Label | Remediation |
|---------------------------------|-----------|---------------|-------------|
| 20-25 | CAT I | CRITICAL | Immediate remediation required |
| 15-19 | CAT I | HIGH | Must fix before deployment |
| 8-14 | CAT II | MEDIUM | Fix within maintenance cycle |
| 4-7 | CAT III | LOW | Track and remediate |
| 1-3 | CAT III | LOW | Accept or track |

## Pipeline Integration

### Finding Schema for /stig-compliance

```json
{
  "id": "TM-NNN",
  "framework": "STRIDE|LINDDUN",
  "category": "<threat-category>",
  "stig_vid": "V-NNNNNN",
  "cat": "I|II|III",
  "component": "<affected-component>",
  "threat": "<threat-description>",
  "likelihood": 1-5,
  "impact": 1-5,
  "risk_score": 1-25,
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "mitigations_present": ["<existing-control>"],
  "mitigations_missing": ["<missing-control>"],
  "recommendation": "<remediation-guidance>",
  "code_pointers": ["<file:line>"]
}
```

### Source Attribution

When threat model findings are consumed by `/stig-compliance review`, they are attributed as:

```
Source: threat-model (semantic)
```

This distinguishes them from tool-based findings (e.g., `Source: semgrep (static)`, `Source: grype (sca)`).
