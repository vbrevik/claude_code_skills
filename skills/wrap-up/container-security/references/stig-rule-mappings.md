# STIG Rule Mappings for Container Security

## Dockerfile Checks

| Check ID | Check | V-ID | CAT | Severity | Description |
|----------|-------|------|-----|----------|-------------|
| CS-001 | Running as root | V-222548 | II | MEDIUM | No USER instruction or USER root found |
| CS-002 | Latest tag used | V-222548 | II | MEDIUM | Base image uses :latest or no tag |
| CS-003 | ADD instead of COPY | V-222548 | II | MEDIUM | ADD can fetch remote URLs; prefer COPY |
| CS-004 | No HEALTHCHECK | V-222549 | III | LOW | No HEALTHCHECK instruction found |
| CS-005 | Secrets in ENV/ARG | V-222642 | I | HIGH | PASSWORD, SECRET, KEY, TOKEN in ENV/ARG values |
| CS-006 | EXPOSE all interfaces | V-222545 | II | MEDIUM | Exposing on 0.0.0.0 without restriction |

## Kubernetes Manifest Checks

| Check ID | Check | V-ID | CAT | Severity | Description |
|----------|-------|------|-----|----------|-------------|
| CS-010 | Privileged container | V-222548 | I | CRITICAL | securityContext.privileged: true |
| CS-011 | No resource limits | V-222549 | II | MEDIUM | Missing resources.limits in container spec |
| CS-012 | No resource requests | V-222549 | III | LOW | Missing resources.requests in container spec |
| CS-013 | Run as root | V-222548 | II | MEDIUM | runAsNonRoot not set or runAsUser: 0 |
| CS-014 | No read-only rootfs | V-222548 | II | MEDIUM | readOnlyRootFilesystem not set to true |
| CS-015 | No NetworkPolicy | V-222545 | II | MEDIUM | Namespace has no NetworkPolicy defined |
| CS-016 | Hardcoded secrets | V-222642 | I | HIGH | Password/secret/token values in env |
| CS-017 | No securityContext | V-222548 | II | MEDIUM | Container has no securityContext |
| CS-018 | Host networking | V-222545 | I | HIGH | hostNetwork: true |
| CS-019 | Host PID/IPC | V-222548 | I | HIGH | hostPID or hostIPC: true |
| CS-020 | Latest tag in image | V-222548 | II | MEDIUM | Image uses :latest tag |
| CS-021 | No liveness probe | V-222549 | III | LOW | Missing livenessProbe |
| CS-022 | No readiness probe | V-222549 | III | LOW | Missing readinessProbe |

## Docker Compose Checks

| Check ID | Check | V-ID | CAT | Severity | Description |
|----------|-------|------|-----|----------|-------------|
| CS-030 | Privileged mode | V-222548 | I | CRITICAL | privileged: true in service |
| CS-031 | No resource limits | V-222549 | II | MEDIUM | No deploy.resources.limits |
| CS-032 | Exposed on 0.0.0.0 | V-222545 | II | MEDIUM | Port mapped without host binding |
| CS-033 | Hardcoded secrets | V-222642 | I | HIGH | PASSWORD/SECRET/KEY in environment |
| CS-034 | No health check | V-222549 | III | LOW | No healthcheck defined |
| CS-035 | Latest tag | V-222548 | II | MEDIUM | Image uses :latest tag |
| CS-036 | No TLS config | V-222543 | I | HIGH | HTTP URLs without TLS in environment |

## Trivy Misconfiguration Mapping

| Trivy ID Pattern | V-ID | CAT |
|-----------------|------|-----|
| DS001 (root user) | V-222548 | II |
| DS002 (latest tag) | V-222548 | II |
| DS005 (ADD) | V-222548 | II |
| DS006 (COPY --chown) | V-222548 | III |
| DS026 (no healthcheck) | V-222549 | III |
| KSV001 (privileged) | V-222548 | I |
| KSV003 (capabilities) | V-222548 | II |
| KSV006 (host network) | V-222545 | I |
| KSV009 (host PID) | V-222548 | I |
| KSV011 (resource limits) | V-222549 | II |
| KSV012 (run as root) | V-222548 | II |
| KSV014 (read-only fs) | V-222548 | II |
| KSV021 (no net policy) | V-222545 | II |
| KSV106 (secrets in env) | V-222642 | I |
