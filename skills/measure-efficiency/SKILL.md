---
name: measure-efficiency
description: "Measure human+Claude team efficiency at end of task. Computes resource cost per delivered requirement and ideal-vs-actual path ratio, weighted by effectiveness. Run after /measure-effectiveness."
---

# Measure Efficiency

Score how efficiently the team used resources (tokens, steps, time) to deliver working code, weighted by effectiveness so that wrong work is penalized.

## Prerequisites

- `/measure-effectiveness` must have been run first in this session
- The effectiveness scorecard (requirements met, score) must be available in conversation context

## Formulas

### Resource Efficiency (Approach A)

```
Cost_per_req = Work_tokens / Requirements_met
Resource_efficiency = Baseline_cost / Cost_per_req
```

- `Requirements_met` = Met + 0.5 × Partial (from effectiveness score)
- `Baseline_cost` = rolling median of last 10 task measurements
- Clamp to [0, 1.5] to avoid outliers on trivially small tasks
- First 5 measurements: no baseline yet, report raw `Cost_per_req` only

### Path Efficiency (Approach C)

```
Path_efficiency = Ideal_observations / Actual_observations
```

Claude estimates the minimum path after reviewing what was actually done.

### Combined Score

```
Efficiency = ((Resource_efficiency + Path_efficiency) / 2) × Effectiveness_score
```

## Process

Follow these steps exactly. Do not skip any step.

### Step 1: Confirm Effectiveness Score

Check that `/measure-effectiveness` was run in this session. Extract from conversation context:
- Requirements total, met, partial, missed
- Effectiveness score

If not found, tell the user: "Run `/measure-effectiveness` first — I need the requirement scores to weight efficiency."

### Step 2: Collect Resource Data (Hybrid)

**Auto-extract from session context index:**

Scan the session's context observations (the table in the system context with IDs, timestamps, types, Read/Work columns). Extract:

| Metric | How to extract |
|--------|---------------|
| Work tokens | Sum all "Work" values (the 🛠️/🔍/⚖️ numbers) from the session's observations |
| Read tokens | Sum all "Read" values (~NNN numbers) from the session's observations |
| Observation count | Count total observation rows in the session |
| Session start time | Timestamp of first observation |
| Session end time | Current time or timestamp of last observation |

**Ask the user for what can't be auto-extracted:**

Use AskUserQuestion:

1. **"Approximately how many total tokens were consumed this session (input + output)? Check your API dashboard or billing if available."**
   - Options: <50k / 50k–150k / 150k–300k / 300k+ / Unsure (use work tokens as proxy)

2. **"How long did this task take in wall-clock time?"**
   - Options: <15 min / 15–30 min / 30–60 min / 1–2 hours / 2+ hours

### Step 3: Compute Resource Efficiency

Calculate `Cost_per_req`:

```
Requirements_met = Met + 0.5 × Partial
Cost_per_req = Work_tokens / Requirements_met
```

Look up baseline from previous measurements in claude-mem:

```
Search claude-mem for: "EFFICIENCY | " in project "im-ctrl-metrics"
```

If 5+ prior measurements exist:
- Compute baseline = median of prior `Cost_per_req` values
- `Resource_efficiency = clamp(Baseline / Cost_per_req, 0, 1.5)`

If fewer than 5 measurements:
- Report: "Baseline building — need [5 - n] more measurements. Raw cost/req: [value]"
- Set `Resource_efficiency = null` (skip from combined score)

### Step 4: Estimate Ideal Path

Review the session's observations and classify each as:

| Category | Description |
|----------|-------------|
| **Essential** | Directly contributed to a delivered requirement |
| **Necessary exploration** | Research that informed a correct decision |
| **Rework** | Fixing something that was done wrong the first time |
| **Over-research** | Reading/searching beyond what was needed |
| **Tangential** | Work on things not in the requirements |

Count essential + necessary exploration = `Ideal_observations`.
Count all = `Actual_observations`.

```
Path_efficiency = Ideal_observations / Actual_observations
```

Present the breakdown:

```
## Path Analysis

Actual: [n] observations, ~[x]k work tokens
Essential + necessary: [n] observations (~[x]k tokens)
Path efficiency: [0.XX]

Top overheads:
1. [category]: [n] observations — [brief explanation]
2. [category]: [n] observations — [brief explanation]
```

### Step 5: Compute Combined Score

```
If Resource_efficiency is available:
  Efficiency = ((Resource_efficiency + Path_efficiency) / 2) × Effectiveness
Else (baseline building):
  Efficiency = Path_efficiency × Effectiveness
```

### Step 6: Persist

**Save to claude-mem:**

Use the `save_memory` tool:
```
text: "EFFICIENCY | Task: [name] | Date: [YYYY-MM-DD] | Work tokens: [n] | Observations: [n] | Time: [range] | Reqs met: [n] | Cost/req: [n] | Path eff: [0.XX] | Resource eff: [0.XX or 'building'] | Combined: [0.XX] | Effectiveness: [0.XX] | Top overhead: [category]"
project: "im-ctrl-metrics"
title: "Efficiency: [task name]"
```

**Append to markdown log:**

Append a row to `docs/metrics/efficiency-log.md`. If the file doesn't exist, create it with the header:

```markdown
# Efficiency Log

Tracks resource consumption per delivered requirement, weighted by effectiveness.

**Resource Efficiency** = Baseline_cost / Cost_per_requirement (rolling median baseline)
**Path Efficiency** = Ideal_observations / Actual_observations
**Combined** = avg(Resource, Path) × Effectiveness

| Date | Task | Work Tokens | Obs | Time | Reqs Met | Cost/Req | Resource Eff | Path Eff | Combined | Top Overhead |
|------|------|-------------|-----|------|----------|----------|-------------|----------|----------|-------------|
```

Then append the new row.

### Step 7: Report

Present a summary:

```
## Efficiency: [Combined score as percentage]

Resources consumed:
- Work tokens: [n] | Read tokens: [n]
- Observations: [n] | Time: [range]
- Cost per requirement: [n] tokens

Path analysis:
- Essential work: [n]/[n] observations ([path_eff]%)
- Top overhead: [category — explanation]

[If combined >= 0.7]: Good efficiency for this task complexity.
[If combined 0.4–0.69]: Moderate — [top overhead] consumed significant resources.
[If combined < 0.4]: Low efficiency — review [top overhead] patterns across recent tasks.

[If baseline building]: ℹ Baseline needs [5-n] more measurements before Resource Efficiency can be computed.
```

## Interpreting Scores Over Time

| Range | Interpretation |
|-------|---------------|
| 0.70–1.00 | Efficient — direct paths, minimal rework |
| 0.45–0.69 | Moderate — some exploration overhead, review patterns |
| 0.25–0.44 | Inefficient — significant rework or over-research |
| Below 0.25 | Very inefficient — fundamental process issue (unclear specs, wrong assumptions) |

## Tracking Trends

After 10+ measurements, look for patterns in the efficiency log:
- **Declining path efficiency**: specs may be getting vaguer
- **High rework ratio**: implementation-before-understanding pattern
- **High over-research ratio**: exploration not scoped tightly enough
- **Cost/req trending down**: team is getting more efficient (good!)

## What This Skill Does NOT Do

- Does not measure effectiveness (that's `/measure-effectiveness`)
- Does not run tests or builds
- Does not optimize anything — it only measures
- Does not compare across different projects or teams
