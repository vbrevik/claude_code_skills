# Threat Model Output Formats

## Pipeline JSON Format

The primary output format for integration with `/stig-compliance` and the security skills pipeline.

```json
{
  "tool": "threat-model",
  "framework": "STRIDE+LINDDUN",
  "timestamp": "2026-03-13T10:00:00Z",
  "target": "/path/to/project",
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

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `tool` | string | Always `"threat-model"` |
| `framework` | string | `"STRIDE"`, `"LINDDUN"`, or `"STRIDE+LINDDUN"` depending on invocation |
| `timestamp` | string | ISO 8601 timestamp of analysis |
| `target` | string | Project path or specific file/directory analyzed |
| `findings` | array | List of threat findings |
| `summary` | object | Aggregated statistics |

### Finding Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique finding ID (`TM-NNN`, sequential) |
| `framework` | string | `"STRIDE"` or `"LINDDUN"` |
| `category` | string | Threat category (e.g., `"Spoofing"`, `"Linking"`) |
| `stig_vid` | string or null | STIG V-ID mapping (null for LINDDUN categories without STIG equivalent) |
| `cat` | string | `"I"`, `"II"`, or `"III"` |
| `component` | string | Affected component, service, or data flow |
| `threat` | string | Concise threat description |
| `likelihood` | number | 1-5 likelihood score |
| `impact` | number | 1-5 impact score |
| `risk_score` | number | likelihood x impact (1-25) |
| `severity` | string | `"CRITICAL"`, `"HIGH"`, `"MEDIUM"`, or `"LOW"` |
| `mitigations_present` | array | Existing controls that partially address the threat |
| `mitigations_missing` | array | Controls that should be implemented |
| `recommendation` | string | Specific remediation guidance |
| `code_pointers` | array | File paths and line numbers relevant to the threat (may be empty for architecture-level findings) |

### Summary Fields

| Field | Type | Description |
|-------|------|-------------|
| `total_threats` | number | Total number of findings |
| `by_framework` | object | Count per framework (`STRIDE`, `LINDDUN`) |
| `by_cat` | object | Count per CAT level (`I`, `II`, `III`) |
| `risk_matrix` | object | Count per severity (`critical`, `high`, `medium`, `low`) |

## Human-Readable Table Format

Default terminal output for quick review:

```
Threat Model Analysis: 12 findings (STRIDE: 8, LINDDUN: 4)

STRIDE Findings:
  CAT I   TM-001  Spoofing     V-222425  Diode Gateway: XML envelope spoofing         Risk: 15 HIGH
  CAT I   TM-002  EoP          V-222425  Visit State Machine: state bypass             Risk: 20 CRITICAL
  CAT II  TM-003  Tampering    V-222578  Portal API: missing input validation          Risk: 12 MEDIUM
  CAT II  TM-004  Tampering    V-222536  NATS Messages: unsigned envelopes             Risk: 10 MEDIUM
  CAT II  TM-005  Repudiation  V-222610  Badge Issuance: incomplete audit trail        Risk:  8 MEDIUM
  CAT II  TM-006  InfoDisc     V-222602  Error Responses: stack traces in production   Risk:  9 MEDIUM
  CAT II  TM-007  DoS          V-222549  Outbox Table: unbounded queue growth           Risk: 10 MEDIUM
  CAT III TM-008  Repudiation  V-222610  Diode Messages: no end-to-end correlation     Risk:  6 LOW

LINDDUN Findings:
  CAT I   TM-009  DataDisc     V-222642  Visitor PII: unencrypted at rest              Risk: 16 HIGH
  CAT II  TM-010  Unawareness  —         Portal: insufficient privacy notice           Risk: 12 MEDIUM
  CAT II  TM-011  NonCompl     V-222610  Register Lookups: no DPIA conducted           Risk: 10 MEDIUM
  CAT III TM-012  Linking      V-222642  Badge IDs: persistent cross-visit linking     Risk:  6 LOW

Summary: 2 CAT I (block deployment), 6 CAT II (maintenance cycle), 4 CAT III (track)
Risk: 2 CRITICAL, 2 HIGH, 6 MEDIUM, 2 LOW
```

## Risk Matrix Visualization

Included in the markdown report output:

```
                        IMPACT
              1       2       3       4       5
         +-------+-------+-------+-------+-------+
    5    |       |       |  MED  | HIGH  | CRIT  |
         +-------+-------+-------+-------+-------+
    4    |       |  MED  |  MED  | HIGH  | CRIT  |
L        +-------+-------+-------+-------+-------+
I   3    |       |  LOW  |  MED  | HIGH  | HIGH  |
K        +-------+-------+-------+-------+-------+
E   2    |  LOW  |  LOW  |  LOW  |  MED  |  MED  |
L        +-------+-------+-------+-------+-------+
I   1    |  LOW  |  LOW  |  LOW  |  LOW  |  LOW  |
H        +-------+-------+-------+-------+-------+
O
O
D
```

## Compatibility

The pipeline JSON format is designed to be consumed by:
- `/stig-compliance review` — as design-level evidence with `Source: threat-model (semantic)`
- `/stig-compliance report` — threat findings appear in the design review section
- Direct JSON processing — standard structure for custom reporting

The `stig_vid` and `cat` fields ensure compatibility with the shared finding schema used by `/static-analysis`, `/sca`, `/container-security`, and `/dast`.
