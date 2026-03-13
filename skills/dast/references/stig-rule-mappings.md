# STIG Rule Mappings — DAST

Nuclei template to V-ID mapping. Templates in `assets/nuclei-templates/`.

## security-headers

| V-ID | CAT | Template ID | Description |
|------|-----|-------------|-------------|
| V-222602 | I | stig-header-no-csp | Missing Content-Security-Policy header |
| V-222602 | I | stig-header-no-xframe | Missing X-Frame-Options header |
| V-222602 | I | stig-header-no-xcontent | Missing X-Content-Type-Options header |
| V-222596 | II | stig-header-no-hsts | Missing Strict-Transport-Security header |

## tls-config

| V-ID | CAT | Template ID | Description |
|------|-----|-------------|-------------|
| V-222596 | II | stig-tls-version | TLS version below 1.2 |
| V-222597 | I | stig-tls-no-encryption | HTTP (plaintext) accessible |

## session-cookies

| V-ID | CAT | Template ID | Description |
|------|-----|-------------|-------------|
| V-222577 | I | stig-cookie-no-httponly | Session cookie missing HttpOnly flag |
| V-222577 | I | stig-cookie-no-secure | Session cookie missing Secure flag |
| V-222577 | I | stig-cookie-no-samesite | Session cookie missing SameSite attribute |

## error-disclosure

| V-ID | CAT | Template ID | Description |
|------|-----|-------------|-------------|
| V-222610 | II | stig-error-stack-trace | Stack trace in error response |
| V-222610 | II | stig-error-debug-mode | Debug mode enabled in production |

## info-exposure

| V-ID | CAT | Template ID | Description |
|------|-----|-------------|-------------|
| V-222610 | II | stig-info-server-header | Server header exposes technology/version |
| V-222610 | II | stig-info-powered-by | X-Powered-By header present |

## Overlap with /static-analysis

Some V-IDs appear in both SAST and DAST mappings. This is intentional:
- **V-222602** (XSS): SAST checks code patterns, DAST checks response headers
- **V-222577** (session exposure): SAST checks code patterns, DAST checks cookie flags
- **V-222610** (error disclosure): SAST checks error handler code, DAST checks actual responses
- **V-222596** (transmission security): SAST checks TLS config code, DAST checks actual TLS

In the unified STIG report, both sources are listed for the same V-ID.
