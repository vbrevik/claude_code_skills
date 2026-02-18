---
name: spec-feature
description: Interview-driven feature specification. Use when the user says "I want to build [feature]", "let's plan [feature]", or invokes /spec-feature. Conducts a structured Socratic interview covering technical implementation, edge cases, tradeoffs, and unconsidered concerns — then writes a SPEC.md. Run this BEFORE any implementation work begins.
user-invokable: true
---

Interview the user about their feature idea. Ask questions in focused batches — not all at once. Wait for answers before moving to the next round. The goal is to surface what they haven't thought about, not just confirm what they have.

## Phase 1: Brief

Ask the user to describe the feature in 1-3 sentences if they haven't already. Confirm your understanding with a one-line restatement: "So you want to [X] so that [Y] — is that right?"

Then proceed to the interview.

## Phase 2: Interview (3–4 rounds)

Run rounds sequentially. Tailor questions to this project's architecture (EAV model, Actix-web, Askama, SQLite, warnings system, permissions-via-relations). Skip questions that were already answered in the user's description.

### Round 1: Core Implementation

Ask 3–4 of these (pick the most relevant):

- Does this need a new entity type in the EAV model, or does it compose from existing types?
- What routes are needed? GET to render, POST to act — or something more complex (pagination, search)?
- What permission code(s) should gate this? Existing ones, or new ones that need seeding?
- Should this get a nav item? Which module (Admin, Governance, or standalone)?
- Does this need a new `relation_type` in the ontology? What would it express?

### Round 2: Edge Cases & Errors

Ask 3–4 of these:

- What's the empty state — what does the user see before any data exists?
- What happens if a referenced entity is deleted mid-flow (e.g. role deleted while building)?
- What are the field constraints? (length limits, format, required vs optional)
- Can two users act on the same data concurrently? Is that a problem?
- What's the failure mode if the DB operation fails partway through?

### Round 3: Integration

Ask 3–4 of these:

- What audit events should be logged? (`action.name`, target type, what goes in `details`?)
- Should this trigger any warnings? Under what conditions?
- Does this change what a role's permissions mean? Does it affect the Menu Builder or Role Builder?
- Does any existing feature need to change to accommodate this?
- Does this need a migration, or does the EAV schema absorb it without schema changes?

### Round 4: Hard Questions (the ones they probably haven't considered)

Ask all of these — these are the high-value probes:

1. **Simpler alternative**: Is there a version of this that delivers 80% of the value with a single handler and no new entity types? Why or why not?
2. **Data-driven vs hardcoded**: Could this be driven by the ontology (new entity type) rather than code? What are the tradeoffs?
3. **Access control inversion**: Who should explicitly *not* be able to do this, and is that expressible with the current permission model?
4. **Testability**: Walk me through how you'd write an integration test for the happy path. If it's hard to describe, is the design right?
5. **Rollback**: If this ships and causes problems, what's the rollback? Is it a `DELETE FROM entities WHERE entity_type = 'x'` or does it require a code revert?

## Phase 3: Write SPEC.md

After the interview, synthesize everything into `docs/specs/SPEC-[feature-name].md`. Use this structure:

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

[New entity types, properties, relations needed. "None — uses existing X/Y" is a valid answer.]

### Routes & Handlers

| Method | Path | Handler | Permission |
|--------|------|---------|------------|
| GET | /path | handler_fn | permission.code |
| POST | /path | handler_fn | permission.code |

### Templates

[Which templates to create/modify. Key interactions, form fields, empty states.]

### Integration Points

- **Audit logging**: [events to log, target type, details shape]
- **Warnings**: [conditions that trigger warnings, or "none"]
- **Nav**: [new nav item and parent, or "none"]
- **Permissions**: [new permission codes to seed, or reuse existing]

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

## Phase 4: Handoff

After writing the spec, ask the user: **"Ready to implement? I can invoke the feature-dev skill to build this from the spec."**

If yes, use the `feature-dev:feature-dev` skill and reference the SPEC.md as the source of truth.

## Rules

- **One batch at a time.** Ask 3–4 questions, wait, then continue. Don't dump the whole interview at once.
- **Disagree when warranted.** If the user's answer reveals a problem, say so. This is an interview, not a form.
- **Hard questions are mandatory.** Phase 2 Round 4 questions must all be asked. Don't skip them because the feature "seems simple".
- **Spec is the contract.** Don't start implementation until SPEC.md is written and the user has confirmed it looks right.
- **Out-of-scope is as important as in-scope.** If a scope question wasn't raised, raise it.

ARGUMENTS: Optionally pass the feature description, e.g. `/spec-feature add dark mode toggle to account page`. If no argument is given, ask the user to describe what they want to build.
