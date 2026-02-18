# Claude Code Skills

Custom skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that enforce structured development workflows.

## Skills

### Reasoning & Planning

| Skill | Scope | Description |
|-------|-------|-------------|
| [prompt-contracts](skills/prompt-contracts/) | Global | Replaces vague prompts with structured 4-component specs (Goal, Constraints, Format, Failure Conditions) |
| [systems-thinking](skills/systems-thinking/) | Global | Donella Meadows framework for analyzing feedback loops, leverage points, and unintended consequences before architectural decisions |
| [spec-feature](skills/spec-feature/) | Project | Socratic interview that surfaces edge cases, integration points, and tradeoffs — then writes a SPEC.md |

### Session Workflow

| Skill | Scope | Description |
|-------|-------|-------------|
| [catch-up](skills/catch-up/) | Project | Start-of-session context loader: reads backlog, git history, build status, then presents a concise briefing |
| [wrap-up](skills/wrap-up/) | Project | End-of-task routine: verify build, review learnings, update backlog, commit, suggest next task |

### Design

| Skill | Scope | Description |
|-------|-------|-------------|
| [frontend-design](skills/frontend-design/) | Global | Guides creation of distinctive, production-grade frontend interfaces that avoid generic AI aesthetics |

## Installation

### Global skills (available in all projects)

Copy the skill folder to `~/.claude/skills/`:

```bash
cp -r skills/prompt-contracts ~/.claude/skills/
cp -r skills/systems-thinking ~/.claude/skills/
cp -r skills/frontend-design ~/.claude/skills/
```

### Project skills (available in a specific project)

Copy the skill folder to your project's `.claude/skills/`:

```bash
cp -r skills/catch-up /path/to/project/.claude/skills/
cp -r skills/wrap-up /path/to/project/.claude/skills/
cp -r skills/spec-feature /path/to/project/.claude/skills/
```

### Install all

```bash
# Global
cp -r skills/{prompt-contracts,systems-thinking,frontend-design} ~/.claude/skills/

# Project (adjust path)
cp -r skills/{catch-up,wrap-up,spec-feature} /path/to/project/.claude/skills/
```

## Usage

Invoke by name in Claude Code:

```
/prompt-contracts
/systems-thinking
/catch-up
/wrap-up
/spec-feature
```

Or reference them in your prompts — Claude Code will detect when a skill applies and invoke it automatically if configured via the `superpowers` plugin.

## Skill Anatomy

Each skill is a single `SKILL.md` file with YAML frontmatter:

```yaml
---
name: skill-name
description: When to trigger this skill
user_invocable: true  # optional — makes it available as /skill-name
---

# Skill content (instructions for Claude)
```

## Customization

These skills were developed for a Rust/Actix-web/Askama/SQLite project but the reasoning and workflow skills (`prompt-contracts`, `systems-thinking`, `catch-up`, `wrap-up`) are stack-agnostic. Adapt the project-specific references (cargo, BACKLOG.md paths, etc.) to your stack.

## License

MIT
