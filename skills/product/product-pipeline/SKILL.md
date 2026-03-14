---
name: product-pipeline
description: "Use when the user says 'product pipeline', 'full PRD', 'PRD pipeline', or wants to go from idea to technical spec. Orchestrates prd-writer → breakdown-feature-prd → create-specification in sequence."
user-invokable: true
---

# Product Pipeline: Idea → PRD → Feature Breakdown → Technical Spec

Orchestrate the full product documentation pipeline. Each stage builds on the previous output.

## Pipeline Stages

```
Stage 1: /prd-writer          → Product Requirements Document
Stage 2: /breakdown-feature-prd → Per-feature mini-PRDs
Stage 3: /create-specification  → Technical specs per feature
```

## How to Run

### Stage 1 — PRD (the "what and why")

Invoke the `prd-writer` skill. This produces the master PRD with:
- Problem statement, personas, solution overview
- MoSCoW-prioritized feature list
- User stories grouped by epic
- Success metrics and technical constraints

**Checkpoint**: Present the PRD to the user. Ask: "Ready to break this down into feature PRDs?"

### Stage 2 — Feature Breakdown (the "scope per feature")

For each **Must Have** and **Should Have** feature from the PRD's MoSCoW table, invoke the `breakdown-feature-prd` skill. This produces per-feature documents with:
- Feature-specific problem/solution/impact
- Functional and non-functional requirements
- Per-feature acceptance criteria (Given/When/Then)
- Explicit out-of-scope boundaries

Save each to: `docs/ways-of-work/plan/{epic-name}/{feature-name}/prd.md`

**Checkpoint**: Present the feature breakdown list. Ask: "Which features should I write technical specs for?"

### Stage 3 — Technical Specification (the "how")

For each selected feature, invoke the `create-specification` skill. This produces AI-ready specs with:
- Numbered requirements (REQ-001, SEC-001, CON-001)
- Interfaces and data contracts
- Test automation strategy
- Dependencies and integration points
- Validation criteria

Save each to: `spec/spec-{purpose}-{feature-name}.md`

## Output Summary

At the end, present a table:

| Document | Path | Status |
|----------|------|--------|
| Master PRD | `docs/prd.md` | Done |
| Feature: [name] PRD | `docs/ways-of-work/plan/...` | Done |
| Feature: [name] Spec | `spec/spec-...` | Done |
| ... | ... | ... |

## Partial Runs

The user can enter at any stage:
- "I already have a PRD" → skip to Stage 2
- "I have feature PRDs" → skip to Stage 3
- "Just the PRD for now" → stop after Stage 1
