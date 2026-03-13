---
name: stig-compliance
description: "DISA ASD STIG compliance checks for development. Guard mode injects STIG constraints into prompt contracts before implementation. Review mode verifies compliance post-implementation with inline findings, per-check reports, and cumulative tracker updates. Invoke with /stig-compliance, /stig-compliance guard, or /stig-compliance review [categories]."
---

# STIG Compliance

Integrate DISA ASD STIG compliance into the development workflow. Two modes: guard (pre-implementation) and review (post-implementation).

## Mode Detection

- `/stig-compliance` — if currently building a prompt contract, run guard mode; otherwise run review mode
- `/stig-compliance guard` — force guard mode
- `/stig-compliance review` — force review mode on git diff
- `/stig-compliance review auth,crypto` — review with manual category override
- `/stig-compliance review --full` — full project baseline (category-by-category, warns about duration first)

## Mode 1: Guard (Pre-Implementation)

Inject relevant STIG constraints before code is written.

### Process

1. Read the current task description or prompt contract being built
2. Auto-detect applicable categories:
   - Read `references/asd-stig-controls.md`
   - Match task description keywords against `<!-- Trigger patterns: ... -->` in each category heading
   - If manual categories provided (e.g., `guard auth,crypto`), use those instead
3. For each matched category, pull all V-controls from the reference file
4. Output a STIG Constraints section for the developer to review:

```
## STIG Constraints (auto-detected: auth, session-management)
- V-222577 (CAT I): Application must enforce approved authorizations for logical access
- V-222596 (CAT II): Application must not expose session IDs in URLs or error messages
- V-222609 (CAT II): Application must destroy session IDs upon user logout
```

5. Present to developer — they can accept, modify, or dismiss
6. If accepted, append below the CONSTRAINTS section of the prompt contract (as a separate section, not merged into Always/Ask First/Never tiers)

**This mode is advisory.** No enforcement.

## Mode 2: Review (Post-Implementation)

Verify compliance and produce documentation after code changes.

### Process

1. **Identify scope:**
   - Default: `git diff` (staged + unstaged changes)
   - `--full`: all files matching project overlay patterns (or `src/` + `templates/` by default), processed category-by-category with incremental output. Warn user about expected duration before starting.
   - Manual file list if provided

2. **Load applicable controls:**
   - Same auto-detect logic as guard mode, but scan actual code patterns in changed files
   - Manual override (`review auth,crypto`) narrows scope
   - Read project overlay (`.claude/rules/stig-profile.md`) if it exists for framework-specific pattern mappings

3. **Review each applicable control** against the code semantically. Assign status:
   - **PASS** — code satisfies the control, with brief evidence
   - **FAIL** — violation found, with specific file:line reference and remediation
   - **N/A** — control doesn't apply to the changed code
   - **MANUAL** — requires human judgement (state what needs verification)

4. **Output three artifacts:**

### Output A: Inline Chat Summary

```
STIG Review: 3 passed, 1 failed, 2 N/A, 1 manual

FAIL   V-222602  Error messages reveal internal paths  src/errors.rs:45
MANUAL V-222541  Verify data classification level      src/handlers/export.rs
```

Show only FAIL and MANUAL in the table. Summarize PASS and N/A as counts.

### Output B: Per-Check Report

Write to `docs/compliance/reports/YYYY-MM-DD-<topic>.md` where topic = comma-joined detected categories (e.g., `2026-03-12-auth-session.md`). If file exists, append `-2` suffix.

Format:

```markdown
# STIG Compliance Report — [categories]

**Date**: YYYY-MM-DD
**Scope**: [git diff | full scan | manual file list]
**Controls checked**: N
**Result**: X passed, Y failed, Z N/A, W manual

## Findings

### FAIL: V-XXXXXX — [Title] (CAT [I/II/III])
**File**: path/to/file.rs:line
**Finding**: [Description of the violation]
**Remediation**: [How to fix it]

### PASS: V-XXXXXX — [Title] (CAT [I/II/III])
**Evidence**: [Brief description of how the code satisfies this control]

### MANUAL: V-XXXXXX — [Title] (CAT [I/II/III])
**Requires**: [What human judgement is needed]
```

### Output C: Cumulative Tracker Update

Update `docs/compliance/stig-status.md`. Create the file if it doesn't exist. Structure by category with markdown tables:

```markdown
# STIG Compliance Status

**Last updated**: YYYY-MM-DD
**Controls tracked**: N (X passed, Y failed, Z not assessed)

## auth
| V-ID | Title | CAT | Status | Last Checked | Evidence/Notes |
|------|-------|-----|--------|--------------|----------------|
| V-222577 | Enforce approved authorizations | I | PASS | 2026-03-12 | require_permission() in all handlers |
```

Rules:
- New controls: add row with current status
- Existing controls: update Status, Last Checked, and Evidence/Notes
- Controls never reviewed: show as `NOT ASSESSED` with `—` for date and notes

## Project Overlay

If `.claude/rules/stig-profile.md` exists, read it for:
- **Stack info**: language, framework, ORM — informs which patterns to look for
- **Pattern mappings**: maps abstract STIG concepts to project-specific code (e.g., "permission check" → `require_permission(&session, "code")?`)
- **Excluded controls**: V-IDs marked as not applicable with reason — skip these during review

Without an overlay, the skill works with generic guidance.

## Web Fallback

When a V-ID is referenced that isn't in `references/asd-stig-controls.md`:

1. Search the web for its description and check procedure
2. If web search is unavailable, report as "UNKNOWN — not in local reference, web lookup unavailable" and move on
3. If found, ask the user before appending to the reference file
4. Appended entries are tagged with `Source: web-lookup, YYYY-MM-DD`

## Key Principles

- **Advisory, not blocking** — never prevent commits or fail builds
- **Semantic review** — understand code intent, don't just regex match
- **Incremental** — tracker builds over time, no upfront full-scan required
- **Extensible** — designed to add Web Server, PostgreSQL, Container STIGs later
