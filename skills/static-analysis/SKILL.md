---
name: static-analysis
description: Run deterministic static code analysis using semgrep with STIG-mapped rules. Produces findings tagged with DISA STIG V-IDs that feed into /stig-compliance as pipeline evidence. Use when (1) building a prompt contract that involves security-sensitive code (guard mode injects tool constraints), (2) reviewing code changes for security issues (review mode runs semgrep), (3) /stig-compliance review needs deterministic evidence before semantic review. Supports any language semgrep supports (TypeScript, Python, Go, Java, C/C++, etc.). Works air-gapped with bundled rules.
---

# Static Analysis

Deterministic security analysis using semgrep with STIG-mapped rules. Integrates as a pipeline stage into `/stig-compliance`.

## Mode Detection

- `/static-analysis` — if building a prompt contract, guard mode; otherwise review mode
- `/static-analysis guard` — force guard mode
- `/static-analysis review` — review `git diff` scope
- `/static-analysis review --full` — full project scan (warn about duration first)
- `/static-analysis review path/to/file.ts` — review specific files

## Prerequisites

Semgrep must be installed. See `references/semgrep-setup.md` if needed.

```bash
semgrep --version
```

If unavailable, fall back to semantic analysis only and note: "semgrep unavailable — findings are semantic-only, not deterministic."

## Mode 1: Guard (Pre-Implementation)

Inject tool constraints before code is written.

### Process

1. Read task description or prompt contract being built
2. Auto-detect applicable STIG categories from task keywords (same trigger patterns as `/stig-compliance` — see `<!-- Trigger patterns -->` in the STIG controls reference)
3. For each matched category, list semgrep rules from `references/stig-rule-mappings.md`
4. Output:

```
## Static Analysis Constraints (auto-detected: auth, error-handling)
Tool: semgrep with bundled STIG rules
Rules that will run:
- stig-auth-no-bypass (V-222425 CAT I): No authentication bypass patterns
- stig-config-hardcoded-secret (V-222642 CAT I): No embedded credentials
- stig-error-stack-leak (V-222610 CAT II): Error responses must not leak internals
```

5. Developer accepts, modifies, or dismisses
6. If accepted, append below CONSTRAINTS in the prompt contract

## Mode 2: Review (Post-Implementation)

Run semgrep and produce findings for `/stig-compliance`.

### Process

1. **Determine scope:**
   - Default: `git diff --name-only` (staged + unstaged)
   - `--full`: all source files
   - Specific files if provided

2. **Run semgrep:**
   ```bash
   bash <skill-path>/scripts/run_analysis.sh "<file-list>" <skill-path>/assets/semgrep-rules/
   ```

3. **Parse findings:**
   ```bash
   python3 <skill-path>/scripts/sarif_to_findings.py <sarif-output-file>
   ```

4. **Report** — see `references/output-formats.md`

### Inline Chat Summary

```
Static Analysis: 2 findings, 1 info

FINDING  stig-auth-no-bypass     V-222425 (CAT I)   src/auth.ts:45
FINDING  stig-error-stack-leak   V-222610 (CAT II)  src/errors.ts:12
INFO     stig-input-no-validate  V-222606 (CAT I)   src/api.ts:30  [may be false positive]
```

## Pipeline: Feeding into /stig-compliance

When `/stig-compliance review` runs, it should invoke `/static-analysis review` first:

1. Static analysis produces deterministic findings with V-ID tags
2. Each finding becomes automatic evidence for the matching V-ID:
   - Semgrep hit → STIG control status = FAIL with file:line evidence
   - No hit → control still gets semantic review
3. Report distinguishes tool-based vs semantic findings:

```markdown
### FAIL: V-222610 — Error messages reveal internals (CAT II)
**Source**: semgrep/stig-error-stack-leak (deterministic)
**File**: src/errors.ts:12
**Finding**: Stack trace included in error response body
**Remediation**: Return generic error; log details server-side only
```

## Rule Reference

See `references/stig-rule-mappings.md` for the complete V-ID to semgrep rule mapping table.

## Project Overlay

Reuses `.claude/rules/stig-profile.md` if it exists (same as `/stig-compliance`):
- Stack info narrows which rule files to run
- Excluded V-IDs skip corresponding rules
- Custom pattern mappings inform false-positive filtering

## Key Principles

- **Advisory, not blocking** — never prevent commits or builds
- **Deterministic first** — semgrep findings are reproducible, not opinions
- **Pipeline, not replacement** — supplements semantic analysis in stig-compliance
- **Air-gap compatible** — all rules bundled, no network at runtime
- **Stack-agnostic** — rules cover patterns across all semgrep-supported languages
