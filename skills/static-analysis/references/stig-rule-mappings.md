# STIG Rule Mappings

V-ID to semgrep rule mapping. Each rule is in `assets/semgrep-rules/<category>.yaml`.

## auth

| V-ID | CAT | Semgrep Rule ID | Description |
|------|-----|-----------------|-------------|
| V-222425 | I | stig-auth-no-bypass | Auth check bypassed or skipped conditionally |
| V-222432 | I | stig-auth-no-lockout | Login without rate limiting or lockout |
| V-222542 | I | stig-auth-plaintext-password | Password stored in plaintext or reversible encoding |
| V-222543 | I | stig-auth-password-in-url | Password transmitted via URL parameter |
| V-222536 | I | stig-auth-weak-password-length | Password length validation below 15 characters |

## session-management

| V-ID | CAT | Semgrep Rule ID | Description |
|------|-----|-----------------|-------------|
| V-222577 | I | stig-session-id-exposure | Session ID in URL, log output, or HTML |
| V-222581 | I | stig-session-url-embedded | Session ID in URL query or path |
| V-222578 | I | stig-session-no-invalidate | Logout without session invalidation |

## input-validation

| V-ID | CAT | Semgrep Rule ID | Description |
|------|-----|-----------------|-------------|
| V-222606 | I | stig-input-no-validate | User input used without validation |
| V-222609 | I | stig-input-no-size-limit | Request body without size limit |
| V-222605 | II | stig-input-path-traversal | Path traversal patterns (../ in file operations) |

## injection

| V-ID | CAT | Semgrep Rule ID | Description |
|------|-----|-----------------|-------------|
| V-222602 | I | stig-injection-xss | innerHTML or unsafe HTML insertion with user input |
| V-222603 | I | stig-injection-no-csrf | State-changing endpoint without CSRF protection |
| V-222604 | I | stig-injection-command | OS command execution with user-controlled input |
| V-222607 | I | stig-injection-sql | SQL string concatenation with user input |
| V-222608 | I | stig-injection-xxe | XML parsing without disabling external entities |

## error-handling

| V-ID | CAT | Semgrep Rule ID | Description |
|------|-----|-----------------|-------------|
| V-222610 | II | stig-error-stack-leak | Stack trace or internal path in error response |
| V-222585 | I | stig-error-fail-open | Error handler defaults to allow/permissive state |

## cryptography

| V-ID | CAT | Semgrep Rule ID | Description |
|------|-----|-----------------|-------------|
| V-222571 | I | stig-crypto-weak-hash | MD5 or SHA1 used for security purposes |
| V-222570 | I | stig-crypto-weak-sign | Weak algorithm for signing (MD5, SHA1) |

## configuration

| V-ID | CAT | Semgrep Rule ID | Description |
|------|-----|-----------------|-------------|
| V-222642 | I | stig-config-hardcoded-secret | Hardcoded password, API key, or secret in source |

## audit-logging

| V-ID | CAT | Semgrep Rule ID | Description |
|------|-----|-----------------|-------------|
| V-222485 | I | stig-audit-no-error-handling | Audit logging call without error handling |
