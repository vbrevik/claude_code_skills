---
name: measure-effectiveness
description: "Measure human+Claude team effectiveness at end of task. Traces prompt contract requirements against delivered code, scores completion, and logs results. Run after completing a feature, fix, or any task that had a prompt contract."
---

# Measure Effectiveness

Score how well the team translated requirements into working code by tracing each prompt contract item against what was delivered.

## When to Run

- After completing a task that had a prompt contract
- When wrapping up a feature or fix
- When the user invokes `/measure-effectiveness`

## Formula

```
Effectiveness = (Met + 0.5 * Partial) / Total
```

Where each requirement from the prompt contract is classified as Met (1.0), Partial (0.5), or Missed (0.0).

## Process

Follow these steps exactly. Do not skip any step.

### Step 1: Locate the Prompt Contract

Find the prompt contract for the just-completed task. Check in order:

1. **Conversation context** — scan the current conversation for a 4-component contract (GOAL, CONSTRAINTS, FORMAT, FAILURE CONDITIONS)
2. **Plan doc** — check `docs/plans/` for the task's plan containing an embedded contract
3. **Ask** — if no contract is found, ask: "I can't find a prompt contract for this task. Can you paste or describe the requirements?"

If there was genuinely no contract (ad-hoc work), note this and construct requirements from the original user request.

### Step 2: Extract Requirements

Parse each contract component into discrete, numbered requirements:

```
From GOAL:
  1. [requirement from goal]
  2. [requirement from goal]

From CONSTRAINTS:
  3. [constraint that must hold]
  4. [constraint that must hold]

From FORMAT:
  5. [expected output shape]

From FAILURE CONDITIONS:
  6. [thing that must NOT happen → verify it didn't]
  7. [thing that must NOT happen → verify it didn't]
```

Present to the user: **"These are the requirements I'll score against. Correct, or should I adjust?"**

Wait for confirmation before proceeding.

### Step 3: Trace Each Requirement

For each requirement, gather evidence from the delivered code:

- **git diff** of the task's commits (use `git log --oneline` + `git diff` to identify scope)
- **cargo check** output (compiles cleanly?)
- **cargo test** results if relevant
- **File inspection** for template/handler changes

Classify each requirement:

| Classification | Criteria |
|---|---|
| **Met** | Implemented, evidence in code, no known gaps |
| **Partial** | Started but incomplete, has TODOs, or known edge cases unhandled |
| **Missed** | Not addressed in any commit |

Present the scorecard:

```
# Effectiveness Scorecard — [Task Name]

| # | Source | Requirement | Status | Evidence |
|---|--------|-------------|--------|----------|
| 1 | GOAL | ... | Met | commit abc123, handler added |
| 2 | GOAL | ... | Partial | template done, no test |
| 3 | CONSTRAINT | ... | Met | validated in handler |
| ... | | | | |
```

### Step 4: Quick Retrospective

Ask two questions (use AskUserQuestion):

1. **"Was anything delivered that wasn't in the contract?"**
   - Options: No / Yes, intentional scope addition / Yes, unplanned scope creep

2. **"For any Partial or Missed items, what was the root cause?"**
   - Options: Unclear spec / Wrong assumption / Technical blocker / Time constraint / Not applicable

### Step 5: Score and Persist

Calculate the score:

```
Score = (count(Met) + 0.5 * count(Partial)) / total_requirements
```

**Save to claude-mem:**

Use the `save_memory` tool with:
```
text: "EFFECTIVENESS | Task: [name] | Date: [YYYY-MM-DD] | Score: [0.XX] | Met: [n] Partial: [n] Missed: [n] | Total: [n] | Root cause: [notes] | Scope creep: [yes/no]"
project: "im-ctrl-metrics"
title: "Effectiveness: [task name]"
```

**Append to markdown log:**

Append a row to `docs/metrics/effectiveness-log.md`. If the file doesn't exist, create it with the header:

```markdown
# Effectiveness Log

| Date | Task | Total | Met | Partial | Missed | Score | Root Cause | Scope Creep |
|------|------|-------|-----|---------|--------|-------|------------|-------------|
```

Then append the new row.

### Step 6: Report

Present a summary to the user:

```
## Effectiveness: [Score as percentage]

[n] requirements traced from prompt contract
- Met: [n] | Partial: [n] | Missed: [n]

[If score < 0.8]: ⚠ Below 80% threshold. Key gaps: [list missed/partial items]
[If score >= 0.8 and < 1.0]: Good. Minor gaps in: [list partial items]
[If score == 1.0]: ✓ All requirements met.
```

## Interpreting Scores Over Time

| Range | Interpretation |
|-------|---------------|
| 0.90–1.00 | Excellent — contracts are clear, execution is tight |
| 0.75–0.89 | Good — occasional gaps, review contract clarity |
| 0.60–0.74 | Needs attention — recurring misses suggest spec or process issues |
| Below 0.60 | Systemic problem — contracts may be too vague or scope too large |

## What This Skill Does NOT Do

- Does not run tests or builds (that's CI or wrap-up)
- Does not measure efficiency (time, tokens, steps — that's the efficiency skill)
- Does not assign blame — this measures the team, not individuals
