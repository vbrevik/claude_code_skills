---
name: systems-thinking
description: Use when designing features, planning architecture, or making structural decisions. Analyzes feedback loops, leverage points, unintended consequences, and system boundaries before committing to an approach. Prevents narrow local fixes that create systemic problems.
---

# Systems Thinking

## Overview

Apply systems thinking before committing to any design or architectural decision. The goal is to see the whole system — not just the component you're changing — and anticipate how your intervention will ripple through feedback loops, boundaries, and stakeholder mental models.

**Core principle:** Every intervention in a system changes the system. Understand how before you act.

This skill is grounded in Donella Meadows' *Thinking in Systems* framework: stocks, flows, feedback loops, delays, and leverage points.

## When to Use

- Designing a new feature that touches multiple modules
- Planning architecture or data model changes
- Making decisions that constrain future options (schema, API contracts, permission models)
- When a proposed fix feels too simple for the problem's complexity
- When you notice yourself solving a symptom rather than a cause
- When a change has organizational or workflow implications beyond code

## When NOT to Use

- Single-line fixes, typo corrections, simple renames
- Pure implementation work where the design is already decided
- Tasks with no structural or cross-cutting implications

## The Process

### Step 1: Identify the System Boundary

Before solving anything, name the system you're operating in.

Ask:
- **What is the system?** (e.g., "the ToR governance workflow", not "the database")
- **What's inside the boundary?** (components, actors, data flows you can change)
- **What's outside?** (external dependencies, user behavior, organizational constraints you cannot change)
- **What enters and exits?** (inputs, outputs, side effects that cross the boundary)

Write this down in 2-3 sentences. If you can't define the boundary, you don't understand the problem yet.

### Step 2: Map Stocks and Flows

Identify the key **stocks** (things that accumulate) and **flows** (rates of change) in the system.

Software stocks include:
- Data that accumulates (entities, logs, warnings, queue depth)
- State that persists (user sessions, configuration, permissions)
- Technical debt and complexity (coupling between modules)
- User trust and adoption (harder to measure, but real)

Software flows include:
- Rate of data creation/deletion
- Request throughput
- Rate of configuration change
- Developer velocity in a module

Ask: **If I change this flow, what stock overflows or drains?**

### Step 3: Trace Feedback Loops

Every non-trivial system has feedback. Find it.

**Reinforcing loops** (R): Change amplifies itself.
- More warnings → users ignore warnings → more unread warnings → system loses trust → warnings become useless
- More features → more complexity → slower development → pressure to cut corners → more bugs → more features to fix bugs

**Balancing loops** (B): Change triggers a counterforce.
- Queue grows → backpressure triggers cleanup → queue shrinks
- Permissions too restrictive → users request exceptions → admin burden grows → permissions loosened

For each loop, ask:
- **What's the delay?** (Delays in feedback loops cause oscillation and overshoot)
- **Is the loop currently dominant or dormant?**
- **Will my change strengthen or weaken this loop?**

### Step 4: Check for System Archetypes

Scan for these common patterns (from Meadows/Senge). If one matches, the intervention strategy is known:

| Archetype | Pattern | Symptom | Leverage |
|-----------|---------|---------|----------|
| **Fixes that Fail** | Quick fix creates side effects that recreate the problem | Same bug keeps returning in different forms | Address the root cause, not the symptom |
| **Shifting the Burden** | Symptomatic fix undermines the fundamental solution | Growing dependency on workarounds | Strengthen the fundamental solution; weaken the addiction to the quick fix |
| **Limits to Growth** | Reinforcing growth hits a constraint | Performance degrades as scale increases | Remove or relax the constraint before it binds |
| **Eroding Goals** | Pressure to lower standards to close the gap | "Good enough" keeps getting worse | Hold the standard; fix the process, not the target |
| **Escalation** | Two actors each respond to the other's actions | Arms race of complexity between modules | Negotiate a ceiling; introduce a shared constraint |
| **Success to the Successful** | Winner gets more resources, loser gets fewer | One module gets all the attention, others rot | Equalize access to resources; watch for allocation bias |
| **Tragedy of the Commons** | Shared resource overused because costs are distributed | Shared database, shared CI pipeline, shared admin time | Make costs visible to the actors who incur them |

### Step 5: Find Leverage Points

Meadows ranked twelve leverage points from least to most effective. For software design, the most actionable are:

**Low leverage** (easy but weak):
- Constants, parameters, buffer sizes (config values, timeouts)
- Adjusting flows (rate limits, batch sizes)

**Medium leverage** (structural):
- Information flows — who sees what, when (making hidden state visible)
- Rules of the system (permissions, validation, constraints)
- Structure of the system (module boundaries, data model relationships)

**High leverage** (paradigm-shifting):
- The goals of the system (what "success" means — redefining metrics)
- The power to change the system structure (who can modify rules)
- The mindset/paradigm out of which the system arises (questioning assumptions)

**Ask:** Where am I intervening on this ladder? Can I move one rung higher?

### Step 6: Anticipate Unintended Consequences

Before finalizing, run these checks:

1. **Who else touches this?** List every actor (user role, background job, external API, other developer) that interacts with the component you're changing.
2. **What breaks if this succeeds?** Imagine your change works perfectly. What downstream assumption is now violated?
3. **What breaks if this is adopted widely?** If every similar problem gets solved this way, what accumulates?
4. **Where's the delay?** If the negative consequence is delayed (e.g., technical debt, data growth, user confusion), it will be invisible during review but real at scale.
5. **What's the rollback story?** If this change has to be undone, what's the blast radius?

### Step 7: State Your Intervention Hypothesis

Write one paragraph:

> "The system currently behaves like [description]. I believe this is caused by [feedback loop / structural issue]. My intervention is to [specific change] at the level of [leverage point type]. I expect this will [intended effect]. The risk is [unintended consequence], which I'll mitigate by [safeguard]."

This is your design rationale. Include it in the plan or design doc.

## Output Format

When applying systems thinking to a task, produce a brief section (not a separate document — inline in your plan or design) with:

1. **System boundary** (2-3 sentences)
2. **Key feedback loops** (1-3 loops, one line each, labeled R or B)
3. **Archetype match** (if any — name it, don't force it)
4. **Leverage point** (where you're intervening and why)
5. **Intervention hypothesis** (the paragraph from Step 7)

Keep it concise. Systems thinking is a lens, not a ceremony. If the analysis is longer than the implementation plan, you've over-applied it.

## Anti-Patterns

| Trap | What it looks like | Fix |
|------|-------------------|-----|
| **Analysis paralysis** | Mapping every conceivable loop before touching code | Time-box to 5 minutes. If no loops are obvious, the system may genuinely be simple. |
| **Diagram worship** | Drawing elaborate causal loop diagrams that nobody reads | Words over diagrams. Name the loops, don't draw them. |
| **Everything is connected** | Refusing to set a boundary because "it all matters" | Decide what's outside your boundary. You can't change everything. |
| **Leverage point snobbery** | Rejecting a practical low-leverage fix because a higher one exists | The best leverage point you can actually implement beats the ideal one you can't. |
| **Ignoring the obvious** | Spending time on systemic analysis when the bug is a typo | Use judgment. Not every problem is systemic. |

## Integration with Other Skills

- **Before brainstorming**: Systems thinking identifies the constraints and loops that brainstorming must respect
- **Before prompt contracts**: The intervention hypothesis informs the GOAL and FAILURE CONDITIONS
- **Before writing plans**: The leverage point analysis determines where to focus implementation effort
- **During debugging**: Ask "is this a symptom or a cause?" before fixing
