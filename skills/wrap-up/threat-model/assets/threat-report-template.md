# Threat Model Report: [PROJECT NAME]

**Date**: [YYYY-MM-DD]
**Analyst**: Claude Code (threat-model skill)
**Framework**: STRIDE + LINDDUN
**Scope**: [Full project | Specific component/document]

---

## Executive Summary

[1-3 paragraph overview of findings. Include total threat count, breakdown by severity, and top-priority items requiring immediate attention.]

**Risk posture**: [CRITICAL | HIGH | MEDIUM | LOW] — based on highest-severity unmitigated threat.

| Metric | Count |
|--------|-------|
| Total threats identified | [N] |
| CAT I (must fix before deployment) | [N] |
| CAT II (fix in maintenance cycle) | [N] |
| CAT III (track and remediate) | [N] |
| STRIDE findings | [N] |
| LINDDUN findings | [N] |

---

## Scope and Assets Analyzed

### Documents Reviewed

| Document | Path | Content |
|----------|------|---------|
| [Doc name] | [path] | [Brief description] |

### Components in Scope

| Component | Type | Trust Boundary | Classification |
|-----------|------|---------------|---------------|
| [Component] | [Backend/Frontend/Gateway/Service] | [Boundary] | [UNCLASSIFIED/RESTRICTED] |

### Trust Boundaries Identified

1. **[Boundary name]** — [Description, e.g., "Classification boundary between UNCLASSIFIED and RESTRICTED via data diode"]
2. **[Boundary name]** — [Description]

### Data Flows Analyzed

| Flow | Source | Destination | Data | Classification |
|------|--------|-------------|------|---------------|
| [Flow name] | [Source] | [Dest] | [Data types] | [Level] |

---

## STRIDE Findings

### Spoofing

| ID | Component | Threat | Risk | CAT | V-ID |
|----|-----------|--------|------|-----|------|
| [TM-NNN] | [Component] | [Threat description] | [Score] [Severity] | [CAT] | [V-ID] |

**Details**:

#### [TM-NNN]: [Threat title]

- **Component**: [Affected component]
- **Threat**: [Detailed threat description]
- **Likelihood**: [1-5] — [Justification]
- **Impact**: [1-5] — [Justification]
- **Risk score**: [N] ([SEVERITY])
- **STIG V-ID**: [V-NNNNNN] (CAT [I/II/III])
- **Existing mitigations**: [List of controls already in place]
- **Missing mitigations**: [List of controls that should be added]
- **Recommendation**: [Specific remediation guidance]
- **Code pointers**: [File paths and line numbers, if applicable]

---

### Tampering

[Same format as Spoofing section]

---

### Repudiation

[Same format as Spoofing section]

---

### Information Disclosure

[Same format as Spoofing section]

---

### Denial of Service

[Same format as Spoofing section]

---

### Elevation of Privilege

[Same format as Spoofing section]

---

## LINDDUN Findings

### Linking

[Same detail format as STRIDE findings, with GDPR article references added]

---

### Identifying

[Same format]

---

### Non-repudiation (Privacy)

[Same format]

---

### Detecting

[Same format]

---

### Data Disclosure (Privacy)

[Same format]

---

### Unawareness

[Same format]

---

### Non-compliance

[Same format]

---

## Risk Matrix

```
                        IMPACT
              1       2       3       4       5
         +-------+-------+-------+-------+-------+
    5    |       |       |       |       |       |
         +-------+-------+-------+-------+-------+
    4    |       |       |       |       |       |
L        +-------+-------+-------+-------+-------+
I   3    |       |       |       |       |       |
K        +-------+-------+-------+-------+-------+
E   2    |       |       |       |       |       |
L        +-------+-------+-------+-------+-------+
I   1    |       |       |       |       |       |
H        +-------+-------+-------+-------+-------+
O
O        [Place finding IDs in the appropriate cells]
D
```

**Heat map**:
- Cells with risk 15-25: CAT I (must remediate)
- Cells with risk 8-14: CAT II (maintenance cycle)
- Cells with risk 1-7: CAT III (track)

---

## Recommendations

Prioritized by risk score (highest first).

### Priority 1 — CAT I (Must Fix Before Deployment)

1. **[TM-NNN]**: [Recommendation] — Risk [Score] [SEVERITY]
   - **Effort**: [Low/Medium/High]
   - **Component**: [Affected component]

### Priority 2 — CAT II (Fix in Maintenance Cycle)

1. **[TM-NNN]**: [Recommendation] — Risk [Score] [SEVERITY]
   - **Effort**: [Low/Medium/High]
   - **Component**: [Affected component]

### Priority 3 — CAT III (Track and Remediate)

1. **[TM-NNN]**: [Recommendation] — Risk [Score] [SEVERITY]

---

## STIG Compliance Impact

Summary of how threat model findings affect STIG compliance posture:

| V-ID | Finding Count | Highest CAT | Status |
|------|--------------|-------------|--------|
| [V-NNNNNN] | [N] | [CAT] | [Open/Partially Mitigated/Mitigated] |

### New V-ID Findings

[List any V-IDs that were not previously identified by automated tools but surfaced through threat modeling.]

### Design-Level Evidence

These findings provide design-level evidence for `/stig-compliance review` with attribution `Source: threat-model (semantic)`. They complement tool-based findings from:
- `/static-analysis` — code-level findings
- `/sca` — dependency vulnerability findings
- `/container-security` — container/infrastructure findings
- `/dast` — runtime/dynamic findings

---

## Appendix: Methodology

### Threat Modeling Approach

This analysis uses two complementary frameworks:

1. **STRIDE** (Microsoft) — Security threat classification covering Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege. Applied per component and per data flow.

2. **LINDDUN** (KU Leuven) — Privacy threat classification covering Linking, Identifying, Non-repudiation, Detecting, Data Disclosure, Unawareness, and Non-compliance. Applied to data flows involving personal data, with GDPR article mappings.

### Risk Scoring

- **Likelihood** (1-5): Probability of exploitation considering existing controls, attacker capability, and attack surface exposure.
- **Impact** (1-5): Consequence severity considering data sensitivity, regulatory requirements, and operational criticality.
- **Risk score**: Likelihood x Impact (1-25).
- **CAT mapping**: Risk 15-25 = CAT I, Risk 8-14 = CAT II, Risk 1-7 = CAT III.

### STIG Mapping

Findings are mapped to DISA Application Security and Development STIG V5R3 V-IDs where applicable. See `references/stig-threat-mappings.md` for the complete mapping table.

### Limitations

- This is a semantic analysis performed by Claude — it identifies threats based on architecture documentation and code review, not automated scanning.
- Risk scores are qualitative assessments based on available information.
- The analysis is bounded by the documentation and code provided; undocumented components or hidden data flows may harbor additional threats.
- LINDDUN analysis may require additional input from Data Protection Officer or legal counsel for definitive GDPR compliance determination.
- This analysis does not replace formal threat modeling workshops with stakeholders.

### References

- Microsoft STRIDE: https://docs.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats
- LINDDUN: https://linddun.org/
- DISA STIG: https://public.cyber.mil/stigs/
- GDPR: https://gdpr-info.eu/
- Sikkerhetsloven: https://lovdata.no/dokument/NL/lov/2018-06-01-24
- Personopplysningsloven: https://lovdata.no/dokument/NL/lov/2018-06-15-38
