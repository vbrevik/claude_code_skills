# LINDDUN Privacy Threat Framework Reference

LINDDUN is a privacy threat modeling framework developed by KU Leuven for systematically identifying privacy threats in software systems. Each category maps to specific GDPR obligations.

## Categories

### Linking (violates Unlinkability)

**Definition**: Combining separate data items to learn whether they relate to the same individual, without necessarily knowing the individual's identity. Even without direct identifiers, correlation across datasets can reveal personal information.

**GDPR mapping**: Article 5(1)(c) — data minimization; Article 25 — data protection by design.

**Detection questions**:
- Can visitor data from different visits be linked to build a profile?
- Can UNCLASSIFIED and RESTRICTED data be correlated to identify patterns?
- Are there shared identifiers (email, SSN, badge ID) across systems that enable linking?
- Can identity scoring data from different categories be combined to infer sensitive attributes?
- Can diode message metadata (timestamps, sequence numbers) be correlated across classification levels?
- Are pseudonymized datasets re-linkable through quasi-identifiers?

**Project-specific concerns**:
- Visitor records across multiple visits can build a movement profile
- Identity scoring combines data from multiple registers (FREG, NKR, SAP HR) — the combined view is more sensitive than individual records
- Badge IDs may be reused across visits, enabling linking
- NATS message metadata (timestamps, routing keys) could correlate UNCLASSIFIED requests with RESTRICTED decisions
- Company visitor patterns could reveal business relationships

**Mitigations**:
- Use distinct pseudonyms per visit (no persistent visitor ID across visits)
- Minimize data retained after visit completion
- Separate storage of identity verification results from visit records
- Time-limited data retention with automatic purging
- Aggregate reporting instead of individual-level analytics

---

### Identifying (violates Anonymity)

**Definition**: Determining the identity of an individual from supposedly anonymous or pseudonymous data. Re-identification attacks using quasi-identifiers or contextual information.

**GDPR mapping**: Article 25 — data protection by design and by default; Article 89 — safeguards for research/statistics.

**Detection questions**:
- Can anonymous visit statistics be de-anonymized through small group sizes?
- Do audit logs contain enough detail to identify individuals even without direct identifiers?
- Can aggregated reports (e.g., "visitors from company X this month") identify specific people?
- Are there unique attribute combinations that serve as quasi-identifiers?
- Can metadata patterns (visit times, duration, frequency) identify individuals?

**Project-specific concerns**:
- Small facilities may have few visitors — aggregate statistics may identify individuals
- Identity scoring breakdowns could uniquely identify people (combination of ID types is rare)
- Visit patterns (same person visiting weekly) identifiable from anonymized time series
- Company + role + visit purpose may uniquely identify a visitor
- Norwegian national ID numbers (fodselsnummer) in FREG responses

**Mitigations**:
- k-anonymity on any published statistics (minimum group size of 5)
- Suppress or generalize quasi-identifiers in reports
- Differential privacy for analytics queries
- Separate identity verification results from visit analytics
- Time-bucketing to prevent temporal re-identification

---

### Non-repudiation (violates Plausible Deniability)

**Definition**: In privacy context, non-repudiation is a *threat* — it means there exists undeniable proof that an individual performed an action, even when that proof harms the individual's privacy. Unlike security non-repudiation (which is desirable), privacy non-repudiation can be harmful.

**GDPR mapping**: Article 5(1)(c) — data minimization; Article 17 — right to erasure.

**Detection questions**:
- Do audit logs retain proof of individual actions beyond what is legally required?
- Can a visitor deny having visited a classified facility? (Should they be able to?)
- Are digital signatures creating permanent proof of consent that cannot be withdrawn?
- Can log retention be aligned with data minimization requirements?
- Is there irrefutable proof of actions that should be deniable?

**Project-specific concerns**:
- Audit logs of visit requests create permanent records of intended visits (even cancelled ones)
- Badge issuance logs prove physical presence at a classified facility
- Identity verification records (FREG/NKR lookups) prove the system processed someone's personal data
- Consent records must balance GDPR accountability (Art. 5(2)) with right to erasure (Art. 17)
- Sikkerhetsloven may require retention that conflicts with data minimization

**Mitigations**:
- Define and enforce data retention periods per data category
- Implement right-to-erasure workflow (with exceptions for legal obligations under sikkerhetsloven)
- Minimize audit log detail to what is legally required
- Separate compliance-required logs from operational logs (different retention)
- Document legal basis for each retention period

---

### Detecting (violates Undetectability)

**Definition**: Ability to detect whether a user is performing a particular action, using a service, or being processed by a system, even without knowing the content of their interactions.

**GDPR mapping**: Article 5(1)(c) — data minimization; Article 25 — data protection by design.

**Detection questions**:
- Can network observers detect who is submitting visit requests?
- Do API call patterns reveal whether someone is undergoing security verification?
- Can NATS message timing reveal when a visitor is being processed on the RESTRICTED side?
- Are there observable side effects (emails, notifications) that reveal processing status?
- Can browser fingerprinting or traffic analysis reveal portal usage patterns?

**Project-specific concerns**:
- Diode message timing could reveal when RESTRICTED-side verification is happening
- Notification emails/SMS to sponsors reveal that a specific person is requesting a visit
- Portal traffic patterns from a company's network could reveal visit planning activity
- OnGuard API calls to provision badges are observable events
- Register API call patterns (FREG, NKR) could be monitored to detect who is being verified

**Mitigations**:
- Constant-rate message padding on diode channels (hide real message timing)
- Batch notification delivery instead of real-time per-event
- TLS for all communications (prevent content-based traffic analysis)
- Minimize observable side effects of processing
- Encrypt notification content (not just transport)

---

### Data Disclosure (violates Confidentiality)

**Definition**: Personal data is made available to unauthorized parties through technical failures, misconfigurations, or deliberate attacks. Overlaps with STRIDE Information Disclosure but specifically focused on personal/sensitive data.

**GDPR mapping**: Article 32 — security of processing; Article 33 — breach notification; Article 34 — communication to data subjects.

**Detection questions**:
- Can visitor PII leak through error messages, logs, or debug output?
- Is personal data encrypted at rest in Convex databases?
- Can one sponsor see another sponsor's visitors?
- Are FREG/NKR responses (containing sensitive personal data) properly protected?
- Can personal data leak across the classification boundary via the diode?
- Are database backups encrypted?

**Project-specific concerns**:
- Visitor PII (name, SSN, employer, phone, email) stored in Convex UNCLASSIFIED
- Identity scoring data reveals what ID documents a person possesses
- NKR security clearance data is highly sensitive (RESTRICTED classification)
- Visit history reveals patterns of access to classified facilities
- FREG data (address, family relations, vital status) is personal data under GDPR
- Diode XML envelopes carry PII across classification boundaries

**Mitigations**:
- Field-level encryption for PII at rest
- Access control on all queries returning personal data
- Data classification labels on fields containing PII
- Breach detection and notification procedures (72-hour GDPR requirement)
- Minimize PII in logs and error messages
- Encrypt diode XML envelope payloads (not just transport)

---

### Unawareness (violates Transparency)

**Definition**: Data subjects are not aware of, or do not understand, how their personal data is being collected, processed, stored, and shared. Includes lack of informed consent and inadequate privacy notices.

**GDPR mapping**: Article 13 — information at collection; Article 14 — information from other sources; Article 12 — transparent communication.

**Detection questions**:
- Are visitors informed about all processing activities before submitting data?
- Do visitors know their data will cross a classification boundary via the diode?
- Are visitors informed about register verification (FREG, NKR, SAP HR lookups)?
- Is there clear communication about data retention periods?
- Do visitors understand the identity scoring process and its consequences?
- Are visitors informed about automated decision-making (Art. 22)?

**Project-specific concerns**:
- Portal wizard collects significant PII — is the privacy notice adequate?
- Identity scoring is partially automated — does it constitute automated decision-making under Art. 22?
- Register verification accesses external databases about the visitor — Art. 14 requires notification
- Visitors may not understand that their data is processed on a RESTRICTED system
- Badge provisioning in OnGuard creates records in a physical access control system
- Sponsors receive visitor PII — is the visitor informed about this sharing?

**Mitigations**:
- Comprehensive privacy notice in the portal wizard (before data collection)
- Layered privacy notices (summary + detailed)
- Inform visitors about register verification before it occurs
- Clear explanation of identity scoring methodology and consequences
- Record of processing activities (ROPA) maintained and available
- Data Protection Impact Assessment (DPIA) for high-risk processing

---

### Non-compliance (violates Regulatory Compliance)

**Definition**: Data processing activities violate applicable privacy regulations, including GDPR, national laws (sikkerhetsloven, personopplysningsloven), and sector-specific requirements.

**GDPR mapping**: Article 6 — lawfulness of processing; Article 9 — special categories; Article 35 — DPIA; Article 37 — DPO.

**Detection questions**:
- Is there a valid legal basis for each processing activity (Art. 6)?
- Is security clearance data processed under Art. 9 (special categories)?
- Has a Data Protection Impact Assessment been conducted (Art. 35)?
- Is there a Data Protection Officer appointed (Art. 37)?
- Are data processing agreements in place with all processors?
- Does cross-classification data transfer comply with sikkerhetsloven?
- Are data subject rights (access, rectification, erasure, portability) implementable?

**Project-specific concerns**:
- Legal basis for processing visitor PII — likely Art. 6(1)(e) public task or (f) legitimate interest
- NKR security clearance data may be "special category" under Art. 9 — requires explicit legal basis
- Sikkerhetsloven imposes additional requirements for handling of classified information
- Cross-classification diode transfer needs legal basis analysis
- Identity scoring may constitute profiling under Art. 22
- Register lookups (FREG, NKR) need data processing agreements or legal mandate
- Data retention must comply with both GDPR minimization and sikkerhetsloven archival requirements
- Norwegian Data Protection Authority (Datatilsynet) notification requirements

**Mitigations**:
- Document legal basis for each processing activity in ROPA
- Conduct DPIA for identity scoring and register verification
- Appoint DPO and establish data subject rights procedures
- Data processing agreements with register providers (or legal mandate documentation)
- Regular compliance audits against GDPR and sikkerhetsloven
- Privacy-by-design review for all new features
- Data retention policy aligned with both GDPR and sikkerhetsloven

## Norwegian Regulatory Context

### Sikkerhetsloven (Security Act)
- Governs protection of national security information
- Classification levels: UGRADERT, BEGRENSET, KONFIDENSIELT, HEMMELIG, STRENGT HEMMELIG
- Physical security requirements for classified facilities (visitor management is a control)
- Personnel security clearance requirements (NKR integration)
- May require data retention beyond what GDPR would allow

### Personopplysningsloven (Personal Data Act)
- Norwegian implementation of GDPR
- Datatilsynet is the supervisory authority
- Additional provisions for national identification numbers (fodselsnummer)
- Special rules for processing in the security sector

### GDPR Key Articles for Visitor Management
- **Art. 5** — Processing principles (lawfulness, fairness, transparency, purpose limitation, data minimization, accuracy, storage limitation, integrity/confidentiality, accountability)
- **Art. 6** — Legal basis for processing
- **Art. 9** — Special categories (health, biometric, political opinion — security clearance may touch these)
- **Art. 13/14** — Information to data subjects
- **Art. 22** — Automated decision-making and profiling
- **Art. 25** — Data protection by design and by default
- **Art. 32** — Security of processing
- **Art. 33/34** — Breach notification
- **Art. 35** — Data Protection Impact Assessment
