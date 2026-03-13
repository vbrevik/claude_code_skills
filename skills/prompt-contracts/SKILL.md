---
name: prompt-contracts
description: Use when about to implement a feature, build a component, fix a bug, or make any non-trivial code change. Replaces vague natural-language requests with structured contracts that eliminate ambiguity and prevent wrong-direction work.
---

# Prompt Contracts

## Overview

A Prompt Contract replaces vague prompts ("add user settings page") with structured, enforceable specifications. Five components define what success looks like, why we're doing it, what's off-limits, what shape the output takes, and what counts as failure.

**Core principle:** 60 seconds of structured thinking prevents 60 minutes of wrong-direction work.

## When to Use

- Before any non-trivial implementation task
- When a task touches multiple files or has architectural choices
- When working with agent teams or subagents that need consistent output

**Skip for:** Single-line fixes, typo corrections, simple renames.

## Scaling to Complexity

Not every task needs all 5 components at full detail. Match formality to risk:

| Task complexity | Components needed | Time to write |
|----------------|-------------------|---------------|
| **Small** (single file, clear pattern) | GOAL + CONSTRAINTS (1-2 lines each) | 30 seconds |
| **Medium** (multiple files, some choices) | All 5, concise | 60 seconds |
| **Large** (architectural, cross-cutting) | All 5, detailed + domain context | 2-3 minutes |

**The test:** If you'd be annoyed redoing this task from scratch, it's worth a contract.

## The 5 Components

### 1. GOAL — What "Done" Looks Like

Define the exact success metric. Make it **testable in under a minute**.

```
# BAD (vibe)
Add a subscription system to the app

# GOOD (contract)
GOAL: Implement Stripe subscription management where users can
subscribe to 3 tiers (free/pro/team), upgrade/downgrade instantly,
and see billing status on /settings/billing.
Success = a free user can subscribe to Pro, see the charge on
Stripe dashboard, and access gated features within 5 seconds.
```

**Test:** Can you verify the goal in under 60 seconds when implementation finishes? If not, sharpen it.

### 2. CONTEXT — Why This Matters

The "why" behind the task. Prevents wrong decisions when the implementer faces ambiguous choices.

```
CONTEXT: This replaces the manual billing spreadsheet. Finance needs
automated invoicing by Q2. The Pro tier is our primary revenue driver —
optimize for that conversion path. We expect 80% of users to stay on
free tier.
```

**Why this matters:** Over half of wrong-direction work comes from the implementer making reasonable decisions that conflict with unstated business context. A 2-line context section eliminates entire categories of rework.

**Include when relevant:**
- Business motivation or deadline driving the task
- Which users/personas this serves and how they'll use it
- Related decisions already made that constrain this work
- Known failure modes or pitfalls from past experience in this area

### 3. CONSTRAINTS — Hard Boundaries

Non-negotiable rules using a three-tier system:

```
CONSTRAINTS:
Always:
- Use Convex mutations for all state changes
- Follow existing patterns in adjacent files
- Include TypeScript types on all function parameters

Ask first:
- Adding new dependencies
- Changing schema or database structure
- Modifying shared types in packages/shared

Never:
- Make access decisions on the UNCLASSIFIED side
- Add mock data to production code paths
- Skip error handling on external API calls
```

**Always** = safe to do without asking. **Ask first** = high-impact, needs human review. **Never** = hard stops, no exceptions.

**Permanent constraints** belong in `CLAUDE.md`. Per-task constraints go in the contract.

**STIG compliance:** If the task involves auth, session management, input handling, error handling, cryptography, or logging, consider running `/stig-compliance guard` to inject applicable DISA STIG controls as an additional constraints section.

### 4. FORMAT — Exact Output Structure

Tell Claude exactly what files and shapes to produce.

```
FORMAT:
1. Handler in src/handlers/billing_handlers.rs
2. Model queries in src/models/billing/queries.rs
3. Types in src/models/billing/types.rs
4. Template in templates/billing/settings.html
5. Return type: Result<HttpResponse, AppError>
```

Without this, Claude optimizes for speed over maintainability. You get one 800-line god-function instead of modular code.

### 5. FAILURE CONDITIONS — What "Bad" Looks Like

The secret weapon. Defining what breaks the contract gives Claude a negative target. Use **SHALL NOT** language for clarity.

```
FAILURE CONDITIONS:
- SHALL NOT use useState for data that should be in the database
- SHALL NOT exceed 150 lines in any single file
- SHALL NOT omit loading and error states
- SHALL NOT hardcode values that should be in config
- SHALL NOT skip audit logging on mutations
- SHALL NOT add features not specified in the GOAL
```

**Why this works:** Claude doesn't have to guess what "good" means when you've already told it what "bad" looks like. Even one failure condition dramatically improves output.

**Anti-gold-plating clause:** Always include "SHALL NOT add features not specified in the GOAL" to prevent scope creep.

## Connecting to Tests

When using TDD (superpowers:test-driven-development), the contract's GOAL and FAILURE CONDITIONS translate directly to test cases:

- Each **GOAL success criterion** → at least one test asserting it works
- Each **FAILURE CONDITION** → at least one test asserting it doesn't happen

This means the contract IS your test plan. Write the contract first, derive tests from it, then implement.

## Quick Reference

| Component | Question It Answers | Test | Required? |
|-----------|-------------------|------|-----------|
| GOAL | What does "done" look like? | Can I verify in <60s? | Always |
| CONTEXT | Why are we doing this? | Would a stranger make the right trade-offs? | Medium+ tasks |
| CONSTRAINTS | What's off-limits? | Would violation break the project? | Always (even 1 line) |
| FORMAT | What shape is the output? | Can I point to exact files? | Medium+ tasks |
| FAILURE CONDITIONS | What counts as broken? | Is each condition binary yes/no? | Always (even 1 line) |

## Layering Strategy

| Layer | Where | Scope |
|-------|-------|-------|
| Stack + hard rules | `CLAUDE.md` | Every session, permanent |
| Domain knowledge | `CLAUDE.md` or plan docs | Project-wide |
| Task context + constraints | Prompt contract | This task only |
| Failure conditions | Prompt contract | This task only |

## Complete Example

```
Build the /dashboard page.

GOAL: Display user's active projects with real-time updates.
First meaningful paint under 1 second. User can create, archive,
and rename projects inline.
Success = new user sees empty state, creates a project, sees it
appear without page reload.

CONTEXT: This is the first screen users see after onboarding.
High drop-off rate on current static page. Real-time updates are
the key differentiator vs competitors. Most users have 3-10 projects.

CONSTRAINTS:
Always: Use server components by default. Auth check via session helpers.
Ask first: New dependencies, schema changes.
Never: Client components unless interactivity required. Polling instead
of subscriptions. UI libraries besides Tailwind utilities.

FORMAT: Page handler in src/handlers/dashboard.rs. Template in
templates/dashboard.html. Model queries in src/models/project/queries.rs.
Types in src/models/project/types.rs.

FAILURE CONDITIONS:
- SHALL NOT exceed 150 lines in any file
- SHALL NOT fetch data that could be server-rendered
- SHALL NOT omit loading and error states
- SHALL NOT omit type annotations on function parameters
- SHALL NOT skip permission checks before data access
- SHALL NOT add features beyond create/archive/rename
```

## Common Mistakes

**Writing a novel:** Contracts should be concise. If your contract is longer than the code you expect, you've over-specified. Scale formality to complexity.

**Vague goals:** "Make it responsive" is a horoscope. "Works on 320px-1440px viewport, no horizontal scroll, touch targets 44px minimum" is a contract.

**Missing failure conditions:** The component most people skip and the one that helps most. Even one failure condition dramatically improves output.

**No context:** The implementer will fill in the blanks with assumptions. Two lines of "why" prevents entire categories of rework.

**Over-constraining simple tasks:** A typo fix doesn't need 5 components. A single-file change might just need GOAL + one CONSTRAINT.

**Forgetting anti-gold-plating:** Without "SHALL NOT add unspecified features," Claude will helpfully add error tracking, analytics, logging, and three abstraction layers you didn't ask for.
