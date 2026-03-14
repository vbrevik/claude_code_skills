---
last-updated: 2026-03-12
stig-version: ASD STIG V5R3
update-cadence: DISA releases quarterly — check for updates each quarter
---

# ASD STIG Controls Reference

## auth
<!-- Trigger patterns: login, password, authentication, authorization, permission, credential, access control, logon, privilege -->

### V-222425 (CAT I)
**Title**: The application must enforce approved authorizations for logical access to information and system resources in accordance with applicable access control policies.
**Check**: Verify authorization checks are performed before granting access to any protected resource. Confirm successful authentication does not automatically grant access to all resources.
**Patterns**: `require_permission`, `get_permissions`, role checks, RBAC/ABAC enforcement, route guards
**Fix**: Implement authorization middleware that validates user permissions against resource requirements before granting access. Never rely on authentication alone.

### V-222426 (CAT I)
**Title**: The application must enforce organization-defined discretionary access control policies over defined subjects and objects.
**Check**: Verify the application enforces DAC policies (e.g., ACLs, RBAC) controlling which users can access which objects.
**Patterns**: Access control lists, role-based checks, resource ownership validation, permission matrices
**Fix**: Implement RBAC or ABAC with explicit permission assignments. Validate object ownership on every access.

### V-222432 (CAT I)
**Title**: The application must enforce the limit of three consecutive invalid logon attempts by a user during a 15-minute time period.
**Check**: Verify account lockout triggers after 3 failed login attempts within 15 minutes. Confirm lockout requires admin intervention to unlock.
**Patterns**: Failed login counters, lockout logic, rate limiting on login endpoints, account status checks
**Fix**: Track failed login attempts per account with timestamps. Lock accounts after 3 failures within 15 minutes. Require admin unlock.

### V-222520 (CAT II)
**Title**: The application must require users to reauthenticate when organization-defined circumstances or situations require reauthentication.
**Check**: Verify the application forces reauthentication for sensitive operations (password change, privilege escalation, after session timeout).
**Patterns**: Session timeout handling, step-up authentication, password confirmation for sensitive actions
**Fix**: Require current password entry before password changes. Force reauthentication after idle timeout or before privilege escalation.

### V-222524 (CAT II)
**Title**: The application must accept Personal Identity Verification (PIV) credentials.
**Check**: Verify the application supports CAC/PIV authentication for DoD users where applicable.
**Patterns**: PKI authentication, certificate-based auth, X.509 validation, client certificate configuration
**Fix**: Configure TLS mutual authentication with support for DoD-issued PIV/CAC certificates.

### V-222530 (CAT I)
**Title**: The application must implement replay-resistant authentication mechanisms for network access to privileged accounts.
**Check**: Verify authentication is protected against replay attacks using nonces, challenges, or PKI.
**Patterns**: CSRF tokens, nonce generation, TLS enforcement, challenge-response protocols
**Fix**: Use TLS for all authentication. Implement CSRF tokens with server-side validation. Use time-limited tokens/nonces.

### V-222531 (CAT I)
**Title**: The application must implement replay-resistant authentication mechanisms for network access to non-privileged accounts.
**Check**: Same as V-222530 but for non-privileged accounts.
**Patterns**: CSRF tokens, nonce generation, TLS enforcement, challenge-response protocols
**Fix**: Apply the same replay-resistant protections to all accounts, not just privileged ones.

### V-222536 (CAT I)
**Title**: The application must enforce a minimum 15-character password length.
**Check**: Verify password validation enforces at least 15 characters.
**Patterns**: Password length validation, form validation, server-side password checks
**Fix**: Validate password length >= 15 characters on the server side before accepting. Enforce in both create and update flows.

### V-222538 (CAT I)
**Title**: The application must enforce password complexity by requiring that at least one upper-case character be used.
**Check**: Verify password complexity rules require uppercase, lowercase, numbers, and special characters.
**Patterns**: Password regex validation, complexity checks in create/update handlers
**Fix**: Enforce password complexity: at least one uppercase, one lowercase, one digit, one special character. Validate server-side.

### V-222542 (CAT I)
**Title**: The application must only store cryptographic representations of passwords.
**Check**: Verify passwords are hashed with an approved algorithm (e.g., Argon2, bcrypt, PBKDF2) and never stored in plaintext.
**Patterns**: `argon2`, `bcrypt`, `pbkdf2`, password hashing in user creation/update, hash verification on login
**Fix**: Use Argon2id (preferred) or bcrypt with appropriate cost factor. Never store plaintext or reversibly-encrypted passwords.

### V-222543 (CAT I)
**Title**: The application must transmit only cryptographically-protected passwords.
**Check**: Verify passwords are never transmitted in cleartext — all login/password forms use HTTPS.
**Patterns**: TLS enforcement, HSTS headers, form action URLs using HTTPS, redirect HTTP to HTTPS
**Fix**: Enforce HTTPS for all endpoints. Set HSTS header. Redirect HTTP to HTTPS. Never send passwords in URL query parameters.

### V-222544 (CAT II)
**Title**: The application must enforce 24 hours/1 day as the minimum password lifetime.
**Check**: Verify users cannot change passwords more than once within 24 hours.
**Patterns**: Password change timestamp tracking, minimum age validation
**Fix**: Track last password change timestamp. Reject password changes within 24 hours of the previous change.

### V-222545 (CAT II)
**Title**: The application must enforce a 60-day maximum password lifetime restriction.
**Check**: Verify passwords expire after 60 days and users are prompted to change them.
**Patterns**: Password expiry checks on login, `password_changed_at` field, expiry notifications
**Fix**: Store password change date. Check on login whether 60 days have elapsed. Force password change if expired.

### V-222546 (CAT II)
**Title**: The application must prohibit password reuse for a minimum of five generations.
**Check**: Verify the application maintains a password history and prevents reuse of the last 5 passwords.
**Patterns**: Password history table, hash comparison against previous passwords
**Fix**: Store hashes of previous 5 passwords. Before accepting a new password, verify it does not match any stored hash.

### V-222547 (CAT II)
**Title**: The application must allow the use of a temporary password for system logons with an immediate change to a permanent password.
**Check**: Verify temporary/initial passwords force an immediate change on first use.
**Patterns**: `force_password_change` flag, first-login redirect, temporary password flow
**Fix**: Set a `must_change_password` flag on account creation or password reset. Redirect to password change form on login if flag is set.

### V-222552 (CAT II)
**Title**: The application must map the authenticated identity to the individual user or group account for PKI-based authentication.
**Check**: Verify PKI-authenticated identities are mapped to application user accounts.
**Patterns**: Certificate subject DN mapping, user lookup by certificate, identity binding
**Fix**: Map certificate subject DN or SAN to a user account in the database. Reject authentication if no mapping exists.


## session-management
<!-- Trigger patterns: session, cookie, session_id, session timeout, idle timeout, logoff, logout, token -->

### V-222577 (CAT I)
**Title**: The application must not expose session IDs.
**Check**: Verify session IDs are not included in URLs, error messages, logs, or HTML source visible to users.
**Patterns**: Session cookie settings, URL parameters, log output, HTML source inspection
**Fix**: Use HTTP-only, Secure cookies for session IDs. Never embed session IDs in URLs or log them. Set `SameSite` attribute.

### V-222578 (CAT I)
**Title**: The application must destroy the session ID value and/or cookie on logoff or browser close.
**Check**: Verify logout handler invalidates the server-side session and clears the session cookie.
**Patterns**: Session invalidation on logout, cookie clearing, `session.purge()`, `session.clear()`
**Fix**: On logout, call `session.purge()` to invalidate server-side state. Clear session cookie. Set cookie max-age to 0 on logout.

### V-222579 (CAT II)
**Title**: The application must generate a unique session identifier for each session.
**Check**: Verify each new login generates a fresh session ID. No session fixation vulnerabilities.
**Patterns**: Session regeneration on login, `session.renew()`, unique session ID generation
**Fix**: Generate a new session ID on every successful authentication. Never reuse session IDs. Invalidate pre-authentication session IDs.

### V-222581 (CAT I)
**Title**: Applications must not use URL-embedded session IDs.
**Check**: Verify session IDs are never placed in URLs (query strings or path segments).
**Patterns**: URL inspection for session tokens, cookie-only session transport, URL rewriting disabled
**Fix**: Configure session management to use cookies only. Disable URL-based session tracking. Reject requests with session IDs in URLs.

### V-222582 (CAT I)
**Title**: The application must not re-use or recycle session IDs.
**Check**: Verify session IDs are generated with cryptographic randomness and never recycled.
**Patterns**: Session ID generation using CSPRNG, entropy source checks, session store uniqueness
**Fix**: Use cryptographically secure random number generator for session IDs. Ensure sufficient entropy (128+ bits). Never recycle IDs.

### V-222583 (CAT II)
**Title**: The application must use the Federal Information Processing Standard (FIPS) 140-2 validated cryptographic modules and random number generator if the application implements encryption, key exchange, digital signature, and hash functionality.
**Check**: Verify session tokens and cryptographic operations use FIPS 140-2 validated modules.
**Patterns**: CSPRNG usage, OpenSSL FIPS mode, cryptographic library configuration
**Fix**: Use FIPS-validated cryptographic libraries. Configure OpenSSL in FIPS mode if required. Use `OsRng` or equivalent CSPRNG.


## input-validation
<!-- Trigger patterns: input, validation, sanitize, sanitization, whitelist, allowlist, form, query parameter, user input, request body -->

### V-222606 (CAT I)
**Title**: The application must validate all input.
**Check**: Verify all user-supplied input is validated on the server side (type, length, range, format). Client-side validation alone is insufficient.
**Patterns**: Form validation, type checking, length limits, allowlist validation, `web::Form`, `web::Json` deserialization
**Fix**: Validate all input server-side: check type, length, format, and range. Use allowlist validation where possible. Reject invalid input with clear error messages.

### V-222609 (CAT I)
**Title**: The application must not be subject to input handling vulnerabilities.
**Check**: Verify the application handles malformed, oversized, or unexpected input without crashing or exposing internals.
**Patterns**: Error handling for parse failures, size limits on request bodies, graceful rejection of malformed input
**Fix**: Set request body size limits. Handle all parse/deserialization errors gracefully. Return generic error responses for malformed input.

### V-222612 (CAT I)
**Title**: The application must not be vulnerable to overflow attacks.
**Check**: Verify buffer sizes are checked, integer overflows are prevented, and memory-safe languages or constructs are used.
**Patterns**: Rust memory safety (inherent), bounds checking, integer overflow checks, input length validation
**Fix**: Use memory-safe languages (Rust provides this inherently). Validate input lengths before processing. Use checked arithmetic for integer operations.

### V-222605 (CAT II)
**Title**: The application must protect from canonical representation vulnerabilities.
**Check**: Verify file paths, URLs, and resource identifiers are canonicalized before access control decisions.
**Patterns**: Path traversal prevention, URL normalization, `..` sequence detection, canonicalize file paths
**Fix**: Canonicalize all paths before use. Reject paths containing `..` or encoded traversal sequences. Validate against an allowlist of permitted paths.


## injection
<!-- Trigger patterns: SQL, injection, XSS, cross-site scripting, CSRF, cross-site request forgery, command injection, LDAP injection, XML injection, parameterized, prepared statement -->

### V-222602 (CAT I)
**Title**: The application must protect from Cross-Site Scripting (XSS) vulnerabilities.
**Check**: Verify all output is context-appropriately encoded/escaped. No raw user input rendered in HTML.
**Patterns**: Askama auto-escaping (default), `|safe` filter usage audit, `textContent` vs `innerHTML`, Content-Security-Policy header
**Fix**: Use Askama's default HTML escaping for all template variables. Only use `|safe` for pre-sanitized content. Set Content-Security-Policy header. Use `textContent` in JS, never `innerHTML`.

### V-222603 (CAT I)
**Title**: The application must protect from Cross-Site Request Forgery (CSRF) vulnerabilities.
**Check**: Verify all state-changing requests (POST/PUT/DELETE) include and validate a CSRF token.
**Patterns**: `csrf::validate_csrf`, `csrf_token` in forms, `SameSite` cookie attribute, CSRF middleware
**Fix**: Generate unique CSRF tokens per session. Include in all forms as hidden fields. Validate server-side on every mutation. Set `SameSite=Strict` or `Lax` on session cookies.

### V-222604 (CAT I)
**Title**: The application must protect from command injection.
**Check**: Verify user input is never passed directly to OS command execution. No `std::process::Command` with unsanitized input.
**Patterns**: `Command::new()`, `system()`, shell invocation, subprocess calls with user data
**Fix**: Avoid OS command execution with user input. If necessary, use allowlisted commands with parameterized arguments. Never use shell interpolation.

### V-222607 (CAT I)
**Title**: The application must not be vulnerable to SQL Injection.
**Check**: Verify all database queries use parameterized statements. No string concatenation for SQL.
**Patterns**: `sqlx::query!`, `sqlx::query_as!`, `$1` parameters, `bind()` calls, absence of `format!()` in SQL construction
**Fix**: Use sqlx parameterized queries exclusively (`$1`, `$2`, etc.). Never concatenate user input into SQL strings. Use `query!` macros for compile-time verification.

### V-222608 (CAT I)
**Title**: The application must not be vulnerable to XML-oriented attacks.
**Check**: Verify XML parsers disable external entity processing (XXE). Validate XML input against schemas.
**Patterns**: XML parser configuration, DTD processing disabled, external entity resolution disabled
**Fix**: Disable DTD processing and external entity resolution in XML parsers. Validate XML against strict schemas. Prefer JSON over XML where possible.


## error-handling
<!-- Trigger patterns: error, panic, unwrap, expect, error handling, error message, exception, crash, fail, AppError -->

### V-222585 (CAT I)
**Title**: The application must fail to a secure state if system initialization fails, shutdown fails, or aborts fail.
**Check**: Verify the application enters a secure (deny-all) state on failure rather than an open (allow-all) state.
**Patterns**: Panic handlers, graceful shutdown, `AppError` responses (403/404/500 not exposing data), initialization error handling
**Fix**: Implement fail-closed error handling. On unrecoverable errors, deny access rather than defaulting to permissive mode. Configure Actix-web error handlers to return safe responses.

### V-222610 (CAT II)
**Title**: The application must generate error messages that provide information necessary for corrective actions without revealing information that could be exploited by adversaries.
**Check**: Verify error responses to users are generic and do not contain stack traces, SQL errors, internal paths, or version info.
**Patterns**: `AppError::render()`, custom error pages, error response content, debug info suppression
**Fix**: Return generic error messages to users (e.g., "An error occurred"). Log detailed errors server-side only. Never expose stack traces, SQL errors, or filesystem paths in HTTP responses.

### V-222611 (CAT II)
**Title**: The application must reveal error messages only to the ISSO, ISSM, or SA.
**Check**: Verify detailed error information is only accessible to authorized administrators, not regular users.
**Patterns**: Error logging to server logs, admin-only error detail views, role-gated debug endpoints
**Fix**: Log detailed errors to server-side log files accessible only to admins. Display generic messages to users. Consider an admin-only error log viewer with proper access controls.

### V-222586 (CAT II)
**Title**: In the event of a system failure, applications must preserve any information necessary to determine cause of failure and any information necessary to return to operations with least disruption to mission processes.
**Check**: Verify the application logs sufficient detail about errors and failures for post-incident analysis.
**Patterns**: Structured error logging, audit trail preservation, database transaction rollback, crash diagnostics
**Fix**: Log all errors with context (timestamp, user, action, error details). Ensure database transactions roll back cleanly on failure. Preserve log files during restarts.


## information-disclosure
<!-- Trigger patterns: information disclosure, sensitive data, exposure, leak, hidden field, debug, stack trace, version, header, server header -->

### V-222601 (CAT I)
**Title**: The application must not store sensitive information in hidden fields.
**Check**: Verify HTML hidden fields do not contain passwords, session tokens, or other sensitive data.
**Patterns**: `<input type="hidden"`, hidden field content inspection, CSRF tokens (acceptable), sensitive data in forms
**Fix**: Never place passwords, credit card numbers, or session data in hidden form fields. CSRF tokens in hidden fields are acceptable. Use server-side session storage for sensitive state.

### V-222596 (CAT II)
**Title**: The application must protect the confidentiality and integrity of transmitted information.
**Check**: Verify all data in transit is encrypted using TLS 1.2 or higher.
**Patterns**: TLS configuration, HSTS header, `Secure` cookie flag, cleartext transmission checks
**Fix**: Enforce TLS 1.2+ for all connections. Set HSTS header. Mark all cookies as `Secure`. Disable older TLS/SSL versions.

### V-222598 (CAT II)
**Title**: The application must maintain the confidentiality and integrity of information during preparation for transmission.
**Check**: Verify sensitive data is encrypted before being placed in transit buffers or response bodies.
**Patterns**: Response body content, encryption of sensitive fields, data handling before transmission
**Fix**: Encrypt sensitive data fields before including in response payloads. Use TLS for transport. Do not cache sensitive responses.

### V-222599 (CAT II)
**Title**: The application must maintain the confidentiality and integrity of information during reception.
**Check**: Verify received data integrity is validated and sensitive input is handled securely upon arrival.
**Patterns**: Request validation, TLS verification, input integrity checks, HMAC validation
**Fix**: Validate incoming data integrity. Use TLS for all reception. Validate digital signatures or HMACs on sensitive incoming data.

### V-222588 (CAT I)
**Title**: The application must implement approved cryptographic mechanisms to prevent unauthorized modification of organization-defined information at rest on organization-defined information system components.
**Check**: Verify sensitive data at rest is encrypted using approved algorithms (AES-256, etc.).
**Patterns**: Database encryption, file encryption, key management, encrypted configuration values
**Fix**: Encrypt sensitive data at rest using AES-256 or equivalent. Use proper key management. Encrypt database columns containing PII or sensitive data.

### V-222597 (CAT I)
**Title**: The application must implement cryptographic mechanisms to prevent unauthorized disclosure of information and/or detect changes to information during transmission.
**Check**: Verify cryptographic protections (TLS) are used for all data transmission.
**Patterns**: TLS enforcement, certificate validation, HTTPS configuration, encrypted API calls
**Fix**: Use TLS 1.2+ for all network communication. Validate server certificates. Use HSTS. Reject plaintext connections.


## cryptography
<!-- Trigger patterns: crypto, encryption, hash, hashing, TLS, SSL, certificate, FIPS, key, AES, RSA, secret, token -->

### V-222570 (CAT I)
**Title**: The application must utilize FIPS-validated cryptographic modules when signing application components.
**Check**: Verify code signing and component signing use FIPS 140-2 validated modules. No SHA1 or MD5 for signing.
**Patterns**: Code signing configuration, hash algorithms used (SHA-256+), FIPS mode settings
**Fix**: Use SHA-256 or stronger for all signing operations. Ensure cryptographic library is FIPS 140-2 validated. Disable SHA1 and MD5.

### V-222571 (CAT I)
**Title**: The application must utilize FIPS-validated cryptographic modules when generating cryptographic hashes.
**Check**: Verify all cryptographic hash operations use FIPS-validated modules and approved algorithms.
**Patterns**: Hash function usage, `sha2`, `sha3`, Argon2 for passwords, no MD5/SHA1 for security purposes
**Fix**: Use SHA-256/SHA-384/SHA-512 for integrity checks. Use Argon2id for password hashing. Never use MD5 or SHA1 for security-relevant operations.

### V-222555 (CAT I)
**Title**: The application must use mechanisms meeting the requirements of applicable federal laws, Executive Orders, directives, policies, regulations, standards, and guidance for authentication to a cryptographic module.
**Check**: Verify cryptographic module authentication meets FIPS 140-2 requirements.
**Patterns**: FIPS mode configuration, cryptographic library versions, module authentication
**Fix**: Use FIPS 140-2 validated cryptographic modules. Enable FIPS mode in OpenSSL or equivalent library. Document cryptographic module compliance.

### V-222573 (CAT II)
**Title**: Applications making SAML assertions must use FIPS-approved random numbers in the generation of SessionIndex in the SAML element AuthnStatement.
**Check**: Verify SAML implementations use CSPRNG for session index generation.
**Patterns**: SAML configuration, random number generation for tokens, CSPRNG usage
**Fix**: Use FIPS-approved CSPRNG for all SAML session index generation. Ensure sufficient entropy in generated values.

### V-222553 (CAT II)
**Title**: The application, for PKI-based authentication, must implement a local cache of revocation data to support path discovery and validation in case of the inability to access revocation information via the network.
**Check**: Verify CRL or OCSP response caching is implemented for PKI authentication.
**Patterns**: CRL caching, OCSP stapling, certificate revocation checking, offline validation
**Fix**: Implement CRL caching with periodic updates. Configure OCSP stapling. Ensure certificate validation works when revocation servers are temporarily unavailable.


## audit-logging
<!-- Trigger patterns: audit, log, logging, audit trail, audit record, audit event, syslog, event log, accountability, traceability -->

### V-222474 (CAT II)
**Title**: The application must produce audit records containing enough information to establish which component, feature, or function of the application triggered the audit event.
**Check**: Verify audit log entries include: source component, action performed, target resource, timestamp, and user identity.
**Patterns**: `audit::log()` calls, structured log entries, audit record fields, `serde_json::json!` audit details
**Fix**: Include in every audit record: timestamp, user ID, action name, target type, target ID, and structured details. Use `audit::log(&pool, user_id, action, target_type, target_id, details)`.

### V-222475 (CAT II)
**Title**: The application must produce audit records containing information to establish the outcome of the events.
**Check**: Verify audit records indicate whether the action succeeded or failed.
**Patterns**: Success/failure indicators in audit logs, error logging alongside audit events
**Fix**: Include success/failure status in audit record details. Log both successful and failed operations (especially auth failures).

### V-222483 (CAT II)
**Title**: The application must provide an immediate warning to the SA and ISSO when allocated audit record storage volume reaches 75% of repository maximum audit record storage capacity.
**Check**: Verify audit log storage monitoring is in place with alerts at 75% capacity.
**Patterns**: Log rotation configuration, storage monitoring, alerting integration
**Fix**: Implement log storage monitoring. Alert administrators when log storage reaches 75% capacity. Configure log rotation to prevent storage exhaustion.

### V-222485 (CAT I)
**Title**: The application must alert the ISSO and SA (at a minimum) in the event of an audit processing failure.
**Check**: Verify the application detects audit logging failures and alerts administrators.
**Patterns**: Error handling around `audit::log()` calls, logging system health checks, fallback logging
**Fix**: Wrap audit logging in error handling that alerts administrators on failure. Implement fallback logging (e.g., stderr) if primary audit system fails.

### V-222487 (CAT II)
**Title**: The application must provide the capability to centrally review and analyze audit records from multiple components within the system.
**Check**: Verify audit records can be queried, filtered, and reviewed through a central interface.
**Patterns**: Audit log viewer UI, log aggregation, searchable audit table, export capabilities
**Fix**: Implement an admin-accessible audit log viewer with filtering by date, user, action, and target. Support log export for external analysis.

### V-222489 (CAT II)
**Title**: The application must provide an audit reduction capability that supports on-demand reporting requirements.
**Check**: Verify the application can generate audit reports filtered by criteria (date range, user, event type).
**Patterns**: Report generation endpoints, filtered audit queries, CSV/PDF export
**Fix**: Implement audit reporting with filters: date range, user, action type, target. Provide export functionality for compliance reporting.


## configuration
<!-- Trigger patterns: configuration, config, environment variable, deployment, hardening, server header, debug mode, default account, default password, secrets management -->

### V-222642 (CAT I)
**Title**: The application must not contain embedded authentication data.
**Check**: Verify no hardcoded passwords, API keys, or credentials exist in source code or configuration files checked into version control.
**Patterns**: Hardcoded strings in source, `.env` files in git, API keys in code, default passwords in source
**Fix**: Use environment variables or a secrets manager for all credentials. Never commit credentials to source control. Audit code for hardcoded secrets. Use `.env.example` with placeholder values.

### V-222643 (CAT II)
**Title**: The application must have the capability to mark sensitive/classified output when required.
**Check**: Verify the application can label output with appropriate sensitivity markings when handling classified data.
**Patterns**: Classification banners, sensitivity labels, output marking in templates
**Fix**: Implement classification banners/labels in UI when handling sensitive data. Include sensitivity markings in printed/exported output.

### V-222645 (CAT II)
**Title**: Application files must be cryptographically hashed prior to deploying to DoD operational networks.
**Check**: Verify application binaries and deployment artifacts have integrity verification (checksums/signatures).
**Patterns**: Build artifact checksums, SHA-256 hashes of binaries, signed releases, deployment verification
**Fix**: Generate SHA-256 checksums for all deployment artifacts. Verify checksums before deployment. Sign release artifacts with approved keys.

### V-222646 (CAT II)
**Title**: At least one tester must be designated to test for security flaws in addition to functional testing.
**Check**: Verify security testing is part of the development process, not just functional testing.
**Patterns**: Security test files, penetration test records, SAST/DAST tool integration, security-focused test cases
**Fix**: Designate security testers. Include security-focused test cases (auth bypass, injection, XSS). Integrate SAST tools (clippy lints, cargo-audit). Run DAST scans periodically.

### V-222647 (CAT II)
**Title**: Test procedures must be created and at least annually executed to ensure system initialization, shutdown, and aborts are configured to verify the system remains in a secure state.
**Check**: Verify tests exist for startup, shutdown, and abort scenarios to confirm the system fails securely.
**Patterns**: Integration tests for startup/shutdown, graceful shutdown tests, init failure tests
**Fix**: Create tests that verify: (1) application starts in secure state, (2) graceful shutdown preserves data integrity, (3) aborted processes do not leave system in insecure state. Execute annually at minimum.

### V-222653 (CAT II)
**Title**: The application development team must follow a set of coding standards.
**Check**: Verify a coding standard is documented and enforced (e.g., via linters, code review).
**Patterns**: `cargo clippy` configuration, `.rustfmt.toml`, code review process, CLAUDE.md coding rules
**Fix**: Document and enforce coding standards. Use automated linters (clippy, rustfmt). Enforce via CI/CD pipeline and code review. Reference standards in project documentation.

### V-222615 (CAT II)
**Title**: The application performing organization-defined security functions must verify correct operation of security functions.
**Check**: Verify security mechanisms (auth, access control, crypto) are tested for correct operation.
**Patterns**: Security function tests, auth tests, permission tests, crypto validation tests
**Fix**: Write tests verifying: authentication works correctly, authorization denies unauthorized access, cryptographic operations produce expected results, session management behaves properly.
