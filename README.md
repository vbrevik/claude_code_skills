# Claude Code Skills

Custom skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that enforce structured development workflows.

## Skills

### Reasoning & Planning

| Skill | Description |
|-------|-------------|
| [prompt-contracts](skills/prompt-contracts/) | Replaces vague prompts with structured 4-component specs (Goal, Constraints, Format, Failure Conditions) |
| [systems-thinking](skills/systems-thinking/) | Donella Meadows framework for analyzing feedback loops, leverage points, and unintended consequences |
| [spec-feature](skills/spec-feature/) | Socratic interview that surfaces edge cases, integration points, and tradeoffs — then writes a SPEC.md |
| [executing-plans](skills/executing-plans/) | Guides execution of written implementation plans with review checkpoints |
| [retrospective](skills/retrospective/) | Post-implementation reflection on learnings, blockers, and process improvements |
| [context-manager](skills/context-manager/) | Audit and manage CLAUDE.md memory hierarchy, project documentation, and content overlap |

### Session Workflow

| Skill | Description |
|-------|-------------|
| [catch-up](skills/catch-up/) | Start-of-session context loader: reads backlog, git history, build status, then presents a briefing |
| [wrap-up](skills/wrap-up/) | End-of-task routine: verify build, review learnings, update backlog, commit, suggest next task |

### Design & Frontend

| Skill | Description |
|-------|-------------|
| [frontend-design](skills/frontend-design/) | Guides creation of distinctive, production-grade frontend interfaces |
| [shadcn-ui](skills/shadcn-ui/) | Add shadcn/ui components to themed React projects with installation, customization, and recipes |
| [web-design-methodology](skills/web-design-methodology/) | BEM, responsive, accessibility, CSS architecture, spacing systems, dark mode |
| [web-design-patterns](skills/web-design-patterns/) | Design patterns for heroes, cards, CTAs, trust signals, testimonials |

### Security Testing

| Skill | Description |
|-------|-------------|
| [threat-model](skills/threat-model/) | STRIDE and LINDDUN/GDPR threat analysis for architecture documents, data flows, and code |
| [secret-scan](skills/secret-scan/) | Scan git repos for leaked secrets (API keys, passwords, tokens) using gitleaks |
| [static-analysis](skills/static-analysis/) | Deterministic static code analysis using semgrep with STIG-mapped rules |
| [sca](skills/sca/) | Software Composition Analysis — scan dependencies for CVEs and generate SBOMs |
| [container-security](skills/container-security/) | Scan container images, Dockerfiles, and Kubernetes manifests using Trivy and Kubescape |
| [api-fuzz](skills/api-fuzz/) | Dynamic API security testing using OWASP OFFAT for auth bypass, injection, schema violations |
| [dast](skills/dast/) | Dynamic Application Security Testing using Nuclei against running web apps |
| [stig-compliance](skills/stig-compliance/) | DISA ASD STIG compliance checks — guard mode and review mode for development |

### Measurement

| Skill | Description |
|-------|-------------|
| [measure-effectiveness](skills/measure-effectiveness/) | Score prompt contract requirements against delivered code at end of task |
| [measure-efficiency](skills/measure-efficiency/) | Compute resource cost per requirement and ideal-vs-actual path ratio |

## Installation

### Global skills (available in all projects)

Copy skill folders to `~/.claude/skills/`:

```bash
# Install all skills globally
cp -r skills/* ~/.claude/skills/
```

### Project skills (available in a specific project)

Copy skill folders to your project's `.claude/skills/`:

```bash
cp -r skills/catch-up /path/to/project/.claude/skills/
cp -r skills/wrap-up /path/to/project/.claude/skills/
cp -r skills/spec-feature /path/to/project/.claude/skills/
```

## Usage

Invoke by name in Claude Code:

```
/prompt-contracts
/systems-thinking
/threat-model
/secret-scan
/static-analysis
/sca
/container-security
/api-fuzz
/dast
/stig-compliance
/frontend-design
/shadcn-ui
/web-design-methodology
/web-design-patterns
/retrospective
/measure-effectiveness
/measure-efficiency
```

Or reference them in your prompts — Claude Code will detect when a skill applies and invoke it automatically if configured via the `superpowers` plugin.

## Skill Anatomy

Each skill is a `SKILL.md` file (with optional `references/`, `scripts/`, and `assets/` directories) containing YAML frontmatter:

```yaml
---
name: skill-name
description: When to trigger this skill
user_invocable: true  # optional — makes it available as /skill-name
---

# Skill content (instructions for Claude)
```

Some skills also have a standalone `.skill` file for simpler single-file definitions.

## License

MIT
