# STRIDE Threat Framework Reference

STRIDE is a threat classification model developed by Microsoft for identifying security threats in software systems. Each category represents a violation of a desirable security property.

## Categories

### Spoofing (violates Authentication)

**Definition**: Pretending to be someone or something other than yourself. An attacker assumes the identity of a legitimate user, service, or component.

**Detection questions**:
- Can an unauthenticated user access protected endpoints?
- Can one service impersonate another without mutual authentication?
- Are API keys, tokens, or certificates validated on every request?
- Can session tokens be stolen or predicted?
- Is there mutual TLS between services in the trust boundary?
- Can OIDC tokens be forged or replayed across realms?
- Are WebSocket connections authenticated after the initial handshake?

**Examples in web/API context**:
- Forged JWT tokens accepted without signature verification
- OIDC redirect URI manipulation (open redirect to token theft)
- Missing CSRF protection on state-changing endpoints
- Service-to-service calls without mTLS or API key validation
- WebSocket hijacking via missing origin validation

**Common mitigations**:
- Multi-factor authentication for privileged operations
- OAuth 2.0 / OIDC with proper token validation (issuer, audience, expiry)
- Mutual TLS for service-to-service communication
- CSRF tokens for browser-based state changes
- Certificate pinning for critical connections

**Project-specific patterns** (visitor-mock):
- Keycloak OIDC realms (ID-porten, Mil Feide) — verify token issuer and audience per realm
- Convex backend authentication — ensure auth is checked on every query/mutation
- NATS message authentication — verify publisher identity on diode gateway
- Diode XML envelopes — can envelopes be injected on the NATS channel?
- Cross-classification boundary — can UNCLASSIFIED side spoof RESTRICTED-side identity?

**STIG mappings**: V-222425 (authentication), V-222543 (encrypted transmission)

---

### Tampering (violates Integrity)

**Definition**: Modifying data or code without authorization. An attacker changes data in transit, at rest, or in processing.

**Detection questions**:
- Can request parameters be modified to access unauthorized data?
- Is data integrity verified end-to-end across trust boundaries?
- Can database records be modified through injection attacks?
- Are message envelopes signed and verified?
- Can configuration files be modified at runtime?
- Is there integrity verification on code/artifacts deployed?

**Examples in web/API context**:
- SQL/NoSQL injection via unsanitized inputs
- XML/JSON injection in API payloads
- Parameter tampering (changing IDs in URLs/bodies to access other records)
- Man-in-the-middle modification of API responses
- Prototype pollution in JavaScript objects
- Mass assignment vulnerabilities (extra fields in request bodies)

**Common mitigations**:
- Input validation and sanitization on all external inputs
- Parameterized queries (or ORM-based data access)
- HMAC or digital signatures on messages crossing trust boundaries
- Content Security Policy headers
- Subresource integrity for loaded scripts
- Schema validation for API payloads (Zod, JSON Schema)

**Project-specific patterns**:
- Convex mutation inputs — are all mutation arguments validated with `v.object()` schemas?
- XML diode envelopes — are envelopes signed? Can XML be tampered in transit through NATS?
- Register verification responses — can FREG/NKR responses be modified between service and Convex?
- Identity scoring inputs — can score components be manipulated to achieve higher access tiers?
- Visit state machine — can state transitions be forced out of order?

**STIG mappings**: V-222536 (data integrity), V-222578 (input validation)

---

### Repudiation (violates Non-repudiation)

**Definition**: Claiming to not have performed an action. An attacker (or legitimate user) denies performing a security-relevant action without the system being able to prove otherwise.

**Detection questions**:
- Are all security-relevant actions logged with actor identity?
- Can audit logs be modified or deleted?
- Are timestamps from a trusted source (not client-provided)?
- Is there sufficient detail to reconstruct what happened?
- Are failed authentication attempts logged?
- Can administrative actions be performed without audit trail?

**Examples in web/API context**:
- No audit logging on privilege changes or data access
- Client-controlled timestamps in audit records
- Audit logs stored in same database as application data (can be wiped together)
- Missing correlation IDs across distributed systems
- No logging of denied authorization attempts

**Common mitigations**:
- Comprehensive audit logging with server-side timestamps
- Append-only audit log storage (separate from application data)
- Digital signatures on audit entries
- Correlation IDs across distributed transactions
- Log forwarding to a SIEM (Splunk in this project's case)
- Separate audit log per classification level

**Project-specific patterns**:
- Convex audit tables — are mutations logged with actor identity from auth token?
- Diode message processing — is there audit trail for messages crossing classification boundaries?
- Visit state transitions — is every state change recorded with who/when/why?
- Badge issuance — is OnGuard badge provisioning logged independently?
- Register queries — are FREG/NKR lookups logged for compliance?
- ABAC policy decisions — are deny decisions logged with policy context?

**STIG mappings**: V-222610 (audit logging)

---

### Information Disclosure (violates Confidentiality)

**Definition**: Exposing information to unauthorized parties. Data leaks through error messages, side channels, unauthorized access, or insufficient protection.

**Detection questions**:
- Do error responses include stack traces, internal paths, or database details?
- Are credentials, API keys, or tokens logged or exposed in responses?
- Can one user access another user's data through IDOR?
- Is PII encrypted at rest and in transit?
- Are debug endpoints or verbose logging enabled in production?
- Can classification-level data leak across the diode boundary?

**Examples in web/API context**:
- Stack traces in production error responses
- Verbose error messages revealing database schema
- API responses including fields the user is not authorized to see
- Credentials in URL query parameters (logged by proxies/CDNs)
- CORS misconfiguration allowing cross-origin data access
- Timing attacks revealing existence of resources

**Common mitigations**:
- Generic error messages in production (detailed logging server-side only)
- Field-level authorization on API responses
- Encryption at rest (AES-256) and in transit (TLS 1.2+)
- Secrets management (never hardcode credentials)
- CORS allowlist configuration
- Rate limiting to prevent enumeration

**Project-specific patterns**:
- Convex query authorization — do queries filter results by the authenticated user's permissions?
- Error responses from register services — do FREG/NKR errors leak classified information?
- XML diode envelopes — can RESTRICTED data leak to UNCLASSIFIED side via error paths?
- Identity scoring details — are scoring breakdowns exposed to visitors who should not see them?
- Visitor PII — is personal data (name, SSN, employer) encrypted at rest in Convex?
- NATS message content — are messages encrypted on the wire between diode components?

**STIG mappings**: V-222602 (error information), V-222642 (credential exposure)

---

### Denial of Service (violates Availability)

**Definition**: Making a system unavailable or degraded. An attacker exhausts resources, crashes services, or disrupts operations.

**Detection questions**:
- Are there rate limits on API endpoints?
- Can a single user consume excessive resources (CPU, memory, storage)?
- Are there timeouts on external service calls?
- Can the message queue be flooded?
- Is there circuit-breaking for dependent services?
- Can the diode outbox table grow unbounded?

**Examples in web/API context**:
- No rate limiting on authentication endpoints (brute force)
- Unbounded file uploads consuming disk space
- ReDoS via crafted regex inputs
- Slow loris attacks on HTTP connections
- Queue flooding in message broker systems
- Recursive/deeply nested JSON payloads consuming CPU

**Common mitigations**:
- Rate limiting per user/IP/endpoint
- Request size limits and timeouts
- Circuit breakers for external dependencies
- Resource quotas (CPU, memory, connections)
- Queue depth limits with backpressure
- Health checks and auto-restart policies
- Graceful degradation when dependencies are unavailable

**Project-specific patterns**:
- Convex query/mutation rate limits — are there per-user limits?
- NATS message queue depth — can the diode outbox overflow?
- Register service timeouts — what happens if FREG/NKR is unresponsive?
- Portal wizard submissions — can a visitor submit unlimited requests?
- XML parsing — are there protections against XML bomb / billion laughs?
- Diode delay proxy — can latency simulation be exploited?

**STIG mappings**: V-222549 (resource limits)

---

### Elevation of Privilege (violates Authorization)

**Definition**: Gaining capabilities beyond what is authorized. An attacker escalates from a lower privilege level to a higher one.

**Detection questions**:
- Can a regular user access admin endpoints?
- Can a visitor modify their own visit state (bypass approval)?
- Are authorization checks performed on every request (not just at login)?
- Can ABAC policies be bypassed by crafting specific attribute values?
- Is there privilege separation between classification levels?
- Can the UNCLASSIFIED side make access decisions that should be RESTRICTED-only?

**Examples in web/API context**:
- Missing authorization checks on API endpoints (BOLA/IDOR)
- Role manipulation via JWT claim modification
- Path traversal to access restricted resources
- GraphQL/Convex query depth exploitation
- Mass assignment adding admin role to user profile
- Broken function-level authorization (accessing admin functions)

**Common mitigations**:
- Role-Based Access Control (RBAC) or Attribute-Based Access Control (ABAC)
- Authorization checks on every mutation/query (not just routes)
- Principle of least privilege for service accounts
- Separate admin interfaces from user-facing applications
- Input validation preventing role/privilege claim injection
- Security boundary enforcement (classification levels)

**Project-specific patterns**:
- ABAC policy enforcement — are all mutations checked against ABAC policies?
- Visit state machine — can a visitor or sponsor bypass the security officer approval step?
- Badge provisioning — can badges be issued without completing all verification steps?
- Classification boundary — can UNCLASSIFIED code trigger RESTRICTED operations?
- Convex function access — are internal helper functions exposed as public endpoints?
- Guard/Security UI — are role-specific actions enforced server-side, not just UI-hidden?

**STIG mappings**: V-222425 (authorization)
