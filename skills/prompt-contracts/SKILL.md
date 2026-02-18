---
name: prompt-contracts
description: Use when about to write a prompt for Claude Code to implement a feature, build a component, fix a bug, or make any non-trivial code change. Replaces vague natural-language requests with structured 4-component contracts that eliminate ambiguity and prevent wrong-direction work.
---

# Prompt Contracts

## Overview

A Prompt Contract replaces vague prompts ("add user settings page") with structured, enforceable specifications. Four components define what success looks like, what's off-limits, what shape the output takes, and what counts as failure.

**Core principle:** 60 seconds of structured thinking prevents 60 minutes of wrong-direction work.

## When to Use

- Before any non-trivial implementation prompt
- When a task touches multiple files or has architectural choices
- When you've been burned by Claude building the wrong thing
- When working with agent teams or subagents that need consistent output

**Skip for:** Single-line fixes, typo corrections, simple renames.

## The 4 Components

### 1. GOAL - What "Done" Looks Like

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

**Test:** Can you verify the goal in under 60 seconds when Claude finishes? If not, sharpen it.

### 2. CONSTRAINTS - Hard Boundaries

Non-negotiable rules that prevent stack drift and unwanted decisions.

```
CONSTRAINTS:
- Use Actix-web handlers, never raw hyper
- SQLite via rusqlite, no ORM
- All mutations require CSRF validation
- No new dependencies without asking first
- Max 150 lines per function
```

**Permanent constraints** belong in `CLAUDE.md` (stack, patterns, hard rules). Per-task constraints go in the prompt.

### 3. FORMAT - Exact Output Structure

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

### 4. FAILURE CONDITIONS - What "Bad" Looks Like

The secret weapon. Defining what breaks the contract gives Claude a negative target.

```
FAILURE CONDITIONS:
- Uses useState for data that should be in the database
- Any component exceeds 150 lines
- Missing loading and error states
- Missing TypeScript types on any function parameter
- Hardcoded values that should be in config
- No audit logging on mutations
```

**Why this works:** Claude doesn't have to guess what "good" means when you've already told it what "bad" looks like.

## The Session Handshake

Start every Claude Code session with a constraint confirmation:

```
Read CLAUDE.md and confirm you understand the project constraints
before doing anything.
```

This forces Claude to echo back the constraints before writing code. Think of it as a pre-flight checklist.

## Complete Example

```
Build the /dashboard page.

GOAL: Display user's active projects with real-time updates.
First meaningful paint under 1 second. User can create, archive,
and rename projects inline.

CONSTRAINTS: Use server components by default. Client components
only when interactivity required. No polling, use database queries.
Auth check via session helpers. Redirect to /login if unauthenticated.
Max 150 lines per component file.

FORMAT: Page handler in src/handlers/dashboard.rs. Template in
templates/dashboard.html. Model queries in src/models/project/queries.rs.
Types in src/models/project/types.rs. Tailwind only for styling.

FAILURE CONDITIONS:
- Any file exceeds 150 lines
- Fetches data that could be server-rendered
- Uses any UI library besides Tailwind utilities
- Missing loading and error states
- Missing type annotations on function parameters
- No permission check before data access
```

## Quick Reference

| Component | Question It Answers | Test |
|-----------|-------------------|------|
| GOAL | What does "done" look like? | Can I verify in <60s? |
| CONSTRAINTS | What's off-limits? | Would violation break the project? |
| FORMAT | What shape is the output? | Can I point to exact files? |
| FAILURE CONDITIONS | What counts as broken? | Is each condition binary yes/no? |

## Layering Strategy

| Layer | Where | Scope |
|-------|-------|-------|
| Stack + hard rules | `CLAUDE.md` | Every session, permanent |
| Task constraints | Prompt contract | This task only |
| Failure conditions | Prompt contract | This task only |

## Common Mistakes

**Writing a novel:** Contracts should be concise. If your prompt contract is longer than the code you expect, you've over-specified. Aim for 60 seconds to write.

**Vague goals:** "Make it responsive" is a horoscope. "Works on 320px-1440px viewport, no horizontal scroll, touch targets 44px minimum" is a contract.

**Missing failure conditions:** This is the component most people skip and the one that helps most. Even one failure condition dramatically improves output.

**Forgetting the handshake:** Without confirming CLAUDE.md at session start, Claude may drift from your stack choices.

**Over-constraining simple tasks:** A typo fix doesn't need a 4-component contract. Match formality to complexity.
