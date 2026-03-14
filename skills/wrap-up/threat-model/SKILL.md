---
name: threat-model
description: >
  Analyze architecture documents, data flows, and code for security threats (STRIDE) and privacy threats
  (LINDDUN/GDPR). Produces threat reports with STIG V-ID mappings and risk register entries. Use when
  (1) reviewing architecture or design docs, (2) before implementing security-sensitive features,
  (3) assessing privacy impact for GDPR compliance, (4) generating risk register entries for compliance audits.
  Fully local — Claude-based analysis, no external API needed.
---

# Threat Model Skill

Analyze architecture documents, data flows, and code for security threats (STRIDE) and privacy threats (LINDDUN). Produces STIG V-ID-tagged findings with risk scores.

## Invocation

- `/threat-model` — full STRIDE + LINDDUN analysis of project
- `/threat-model stride` — security threats only
- `/threat-model linddun` — privacy threats only (GDPR focus)
- `/threat-model <file-or-dir>` — analyze specific architecture doc or code path

## How It Works

### 1. Discover assets

Find all analyzable assets in the project:

- Architecture docs in `docs/architecture/`, `docs/design/`, `docs/plans/`
- Schema files: `convex/schema.ts`, database schemas, API definitions
- Authentication/authorization code: OIDC config, auth middleware, ABAC policies
- Data flow code: diode gateways, message publishers/subscribers, API routes
- Infrastructure config: Docker, Kubernetes, NATS, Keycloak configuration

List all discovered assets before analysis. Group them by:
- **Trust boundaries** (classification levels, network zones, authentication domains)
- **Data flows** (cross-boundary data movement, message channels)
- **Data stores** (databases, caches, outbox/inbox tables)
- **External interfaces** (APIs, OIDC providers, register services)

### 2. STRIDE analysis (per component/data flow)

For each component and data flow, evaluate all six STRIDE categories:

| Category | Question | STIG V-ID | CAT |
|----------|----------|-----------|-----|
| **S**poofing | Can identity be faked? Can a component impersonate another? | V-222425, V-222543 | I |
| **T**ampering | Can data be modified in transit or at rest? Can inputs be crafted maliciously? | V-222536, V-222578 | II |
| **R**epudiation | Can actions be performed without audit trail? Can logs be tampered with? | V-222610 | II |
| **I**nformation Disclosure | Can sensitive data leak via errors, logs, or side channels? | V-222602, V-222642 | I-II |
| **D**enial of Service | Can availability be degraded? Are there resource limits? | V-222549 | II |
| **E**levation of Privilege | Can access controls be bypassed? Can roles be escalated? | V-222425 | I |

See `references/stride-framework.md` for detailed detection questions and mitigations per category.

### 3. LINDDUN analysis (privacy-focused, for GDPR)

For each data flow involving personal data, evaluate all seven LINDDUN categories:

| Category | Question | GDPR Article |
|----------|----------|-------------|
| **L**inking | Can separate datasets be correlated to identify individuals? | Art. 5(1)(c) |
| **I**dentifying | Can pseudonymous or anonymous users be re-identified? | Art. 25 |
| **N**on-repudiation | Is there unwanted proof of user actions that harms privacy? | Art. 5(1)(c) |
| **D**etecting | Can user behavior patterns be detected from metadata? | Art. 5(1)(c) |
| **D**ata Disclosure | Can personal data leak through technical or organizational gaps? | Art. 32 |
| **U**nawareness | Are data subjects unaware of data collection or processing? | Art. 13, 14 |
| **N**on-compliance | Does processing violate GDPR, sikkerhetsloven, or personopplysningsloven? | Art. 6, 9 |

See `references/linddun-framework.md` for detailed detection questions and GDPR mappings.

### 4. Risk scoring

Each identified threat receives a risk score:

- **Likelihood** (1-5): How likely is exploitation given current controls?
  - 1 = Rare (requires insider + multiple failures)
  - 2 = Unlikely (requires significant effort/access)
  - 3 = Possible (known attack patterns exist)
  - 4 = Likely (low barrier, high motivation)
  - 5 = Almost certain (trivially exploitable)

- **Impact** (1-5): What is the consequence if exploited?
  - 1 = Negligible (no data loss, brief disruption)
  - 2 = Minor (limited data exposure, recoverable)
  - 3 = Moderate (significant data exposure, operational impact)
  - 4 = Major (classified data breach, extended outage)
  - 5 = Critical (national security impact, complete compromise)

- **Risk score** = Likelihood x Impact

- **CAT mapping** from risk score:
  - Risk 15-25: **CAT I** (critical/high — must remediate before deployment)
  - Risk 8-14: **CAT II** (medium — fix within maintenance cycle)
  - Risk 1-7: **CAT III** (low — track and remediate)

- **Severity label**:
  - Risk 20-25: CRITICAL
  - Risk 15-19: HIGH
  - Risk 8-14: MEDIUM
  - Risk 1-7: LOW

### 5. Output format

Produce findings as pipeline-compatible JSON:

```json
{
  "tool": "threat-model",
  "framework": "STRIDE+LINDDUN",
  "timestamp": "2026-03-13T10:00:00Z",
  "target": "<analyzed-scope>",
  "findings": [
    {
      "id": "TM-001",
      "framework": "STRIDE",
      "category": "Spoofing",
      "stig_vid": "V-222425",
      "cat": "I",
      "component": "Diode Gateway",
      "threat": "XML envelope spoofing via crafted NATS messages",
      "likelihood": 3,
      "impact": 5,
      "risk_score": 15,
      "severity": "HIGH",
      "mitigations_present": ["HMAC envelope signing"],
      "mitigations_missing": ["Message origin verification", "Replay detection"],
      "recommendation": "Add source authentication and nonce-based replay prevention",
      "code_pointers": ["packages/diode-gateway/src/publisher.ts:42"]
    }
  ],
  "summary": {
    "total_threats": 12,
    "by_framework": {"STRIDE": 8, "LINDDUN": 4},
    "by_cat": {"I": 3, "II": 6, "III": 3},
    "risk_matrix": {"critical": 2, "high": 4, "medium": 4, "low": 2}
  }
}
```

See `references/output-formats.md` for full field documentation.

### 6. Human-readable report

In addition to JSON, produce a markdown threat report using the template at `assets/threat-report-template.md`. The report includes:

- Executive summary with risk posture overview
- Asset inventory and trust boundary diagram
- STRIDE findings grouped by category with risk scores
- LINDDUN findings grouped by category with GDPR references
- Risk matrix visualization (likelihood x impact)
- Prioritized recommendations
- STIG compliance impact summary

## STIG V-ID Mapping Table

| Threat Category | V-ID | CAT | Description |
|----------------|------|-----|-------------|
| Spoofing (auth bypass) | V-222425 | I | Application must use approved authentication |
| Spoofing (comms) | V-222543 | I | Application must use encrypted transmission |
| Tampering (input) | V-222578 | II | Application must validate all input |
| Tampering (data) | V-222536 | II | Application must protect data integrity |
| Repudiation | V-222610 | II | Application must generate audit records |
| Info Disclosure (errors) | V-222602 | II | Application must not expose error details |
| Info Disclosure (creds) | V-222642 | I | Application must not expose credentials |
| DoS (resources) | V-222549 | II | Application must restrict resource consumption |
| Elevation of Privilege | V-222425 | I | Application must enforce authorization |
| LINDDUN (data disclosure) | V-222642 | I | PII/personal data protection |
| LINDDUN (non-compliance) | V-222610 | II | Compliance audit logging |

See `references/stig-threat-mappings.md` for the complete mapping with finding patterns.

## Integration with /stig-compliance

Output JSON feeds directly into `/stig-compliance review` as design-level evidence. Findings use the pipeline-compatible format with `Source: threat-model (semantic)` attribution.

Threat model findings complement tool-based scans from `/static-analysis`, `/sca`, `/container-security`, and `/dast` by providing architecture-level and design-level threat identification that automated tools cannot detect.

## Limitations

- Analysis is semantic (Claude-based) — not a substitute for automated scanning tools
- Risk scores are qualitative assessments, not quantitative measurements
- LINDDUN analysis requires understanding of data processing purposes (may need DPIA input)
- Threat identification is bounded by the architecture documentation available
- Does not replace formal threat modeling workshops with stakeholders
