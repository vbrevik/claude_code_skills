---
name: spec-feature
description: Interview-driven feature specification. Use when the user says "I want to build [feature]", "let's plan [feature]", or invokes /spec-feature. Conducts a structured Socratic interview covering technical implementation, edge cases, tradeoffs, and unconsidered concerns — then writes a spec. Run this BEFORE any implementation work begins.
user-invokable: true
---

Interview the user about their feature idea. Ask questions in focused batches — not all at once. Wait for answers before moving to the next round. The goal is to surface what they haven't thought about, not just confirm what they have.

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, or take any implementation action until you have written the spec and the user has approved it. This applies to EVERY feature regardless of perceived simplicity.
</HARD-GATE>

## Phase 0: Project Context

Before starting the interview, explore the project:
- Check files, docs, recent commits, CLAUDE.md, architecture
- Identify the tech stack, patterns, data model, and conventions in use
- Use this context to tailor your interview questions to what actually matters for THIS codebase

## Phase 1: Brief

Ask the user to describe the feature in 1-3 sentences if they haven't already. Confirm your understanding with a one-line restatement: "So you want to [X] so that [Y] — is that right?"

Then proceed to the interview.

## Phase 2: Interview (3–4 rounds)

Run rounds sequentially. Tailor questions to this project's architecture, stack, and patterns (discovered in Phase 0). Skip questions that were already answered in the user's description.

### Round 1: Core Implementation

Ask 3–4 of these (pick the most relevant for the project's stack):

- What new data structures, models, or schema changes are needed — or does this compose from what exists?
- What routes/endpoints/commands are needed? What are the inputs and outputs?
- What permissions or authorization rules should gate this?
- Where does this fit in the existing UI/CLI/API surface? New page, new section, extension of existing?
- Does this introduce a new concept to the domain model, or reuse existing ones?

### Round 2: Edge Cases & Errors

Ask 3–4 of these:

- What's the empty state — what does the user see before any data exists?
- What happens if a referenced resource is deleted or modified mid-flow?
- What are the field constraints? (length limits, format, required vs optional)
- Can two users act on the same data concurrently? Is that a problem?
- What's the failure mode if an operation fails partway through?

### Round 3: Integration

Ask 3–4 of these:

- What events should be logged or tracked?
- Does this affect existing features — do any need to change to accommodate this?
- Does this need a database migration, or does the existing schema absorb it?
- What external services or dependencies does this touch?
- Does this affect the build, deploy, or test pipeline?

### Round 4: Hard Questions (the ones they probably haven't considered)

Ask all of these — these are the high-value probes:

1. **Simpler alternative**: Is there a version of this that delivers 80% of the value with significantly less complexity? Why or why not?
2. **Data-driven vs hardcoded**: Could any part of this be configuration-driven rather than code-driven? What are the tradeoffs?
3. **Access control inversion**: Who should explicitly *not* be able to do this, and is that expressible with the current auth model?
4. **Testability**: Walk me through how you'd write a test for the happy path. If it's hard to describe, is the design right?
5. **Rollback**: If this ships and causes problems, what's the rollback? Data deletion, code revert, feature flag, or something harder?

## Phase 3: Write Spec

After the interview, synthesize everything into `docs/superpowers/specs/YYYY-MM-DD-<feature-name>-design.md`. Use this structure:

```markdown
# Feature Spec: [Feature Name]

_Date: [today] | Status: Draft_

## Summary

[1–2 sentences: what this does and why]

## Context & Motivation

[What problem this solves; what would happen without it]

## In Scope

- [explicit deliverables]

## Out of Scope

- [explicit non-goals — things the user considered and ruled out]

## Technical Design

### Data Model

[New types, schemas, models needed. "None — uses existing X/Y" is a valid answer.]

### Routes / Endpoints / Commands

| Method | Path | Handler | Auth |
|--------|------|---------|------|
| ... | ... | ... | ... |

### UI / Templates / Components

[What to create/modify. Key interactions, form fields, empty states.]

### Integration Points

- **Logging/Events**: [what to track, or "none"]
- **External services**: [what this touches, or "none"]
- **Navigation/Discovery**: [how users find this feature]
- **Permissions**: [new permission rules, or reuse existing]

## Edge Cases & Error Handling

- [Each edge case from the interview, with the agreed handling]

## Testing Plan

- [ ] Happy path: [scenario]
- [ ] Empty state: [scenario]
- [ ] Error case: [scenario]
- [ ] Permission denial: [scenario]

## Tradeoffs & Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| [topic] | [what was chosen] | [why] |

## Open Questions

- [Anything unresolved — must be resolved before implementation begins]
```

Commit the spec to git after writing it.

## Phase 4: Spec Review

After writing and committing the spec:

1. Ask the user to review the spec file before proceeding
2. If they request changes, make them
3. Only proceed once the user approves

> "Spec written and committed to `<path>`. Please review it and let me know if you want to make any changes before we move to implementation planning."

## Phase 5: Handoff

After the user approves the spec, invoke the `superpowers:writing-plans` skill to create a detailed implementation plan from the spec. Do NOT invoke any other skill — writing-plans is the next step.

## Rules

- **One batch at a time.** Ask 3–4 questions, wait, then continue. Don't dump the whole interview at once.
- **Disagree when warranted.** If the user's answer reveals a problem, say so. This is an interview, not a form.
- **Hard questions are mandatory.** Round 4 questions must all be asked. Don't skip them because the feature "seems simple".
- **Spec is the contract.** Don't start implementation until the spec is written and the user has confirmed it.
- **Out-of-scope is as important as in-scope.** If a scope question wasn't raised, raise it.
- **YAGNI ruthlessly.** Push back on unnecessary complexity. Propose the simplest thing that works.

ARGUMENTS: Optionally pass the feature description, e.g. `/spec-feature add dark mode toggle to account page`. If no argument is given, ask the user to describe what they want to build.
