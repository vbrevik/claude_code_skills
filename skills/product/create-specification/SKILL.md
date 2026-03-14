---
name: create-specification
description: "Use after feature breakdown to create AI-optimized technical specifications with numbered requirements, data contracts, test strategy, and Given-When-Then acceptance criteria."
---

# Create Specification

Your goal is to create a new specification file for the given feature or component.

The specification file must define the requirements, constraints, and interfaces for the solution components in a manner that is clear, unambiguous, and structured for effective use by Generative AIs. Follow established documentation standards and ensure the content is machine-readable and self-contained.

## Best Practices for AI-Ready Specifications

- Use precise, explicit, and unambiguous language.
- Clearly distinguish between requirements, constraints, and recommendations.
- Use structured formatting (headings, lists, tables) for easy parsing.
- Avoid idioms, metaphors, or context-dependent references.
- Define all acronyms and domain-specific terms.
- Include examples and edge cases where applicable.
- Ensure the document is self-contained and does not rely on external context.

## Output

The specification should be saved in the project's `/spec/` directory and named: `spec-[a-z0-9-]+.md`, where the name should be descriptive of the specification's content and starting with the high-level purpose, which is one of [schema, tool, data, infrastructure, process, architecture, or design].

## Specification Template

All specifications must follow this structure:

```markdown
---
title: [Concise Title Describing the Specification's Focus]
version: [e.g., 1.0]
date_created: [YYYY-MM-DD]
last_updated: [YYYY-MM-DD]
owner: [Team/Individual responsible]
tags: [e.g., infrastructure, process, design, app]
---

# Introduction

[A short concise introduction to the specification and the goal it is intended to achieve.]

## 1. Purpose & Scope

[Clear description of the specification's purpose, scope, intended audience, and assumptions.]

## 2. Definitions

[All acronyms, abbreviations, and domain-specific terms used in this specification.]

## 3. Requirements, Constraints & Guidelines

[Explicitly list all requirements, constraints, rules, and guidelines.]

- **REQ-001**: Requirement 1
- **SEC-001**: Security Requirement 1
- **CON-001**: Constraint 1
- **GUD-001**: Guideline 1
- **PAT-001**: Pattern to follow 1

## 4. Interfaces & Data Contracts

[Interfaces, APIs, data contracts, or integration points. Use tables or code blocks for schemas.]

## 5. Acceptance Criteria

[Clear, testable acceptance criteria for each requirement.]

- **AC-001**: Given [context], When [action], Then [expected outcome]
- **AC-002**: The system shall [specific behavior] when [condition]

## 6. Test Automation Strategy

[Testing approach, frameworks, and automation requirements.]

- **Test Levels**: Unit, Integration, End-to-End
- **Test Data Management**: [approach for test data]
- **CI/CD Integration**: [automated testing pipeline]
- **Coverage Requirements**: [minimum thresholds]
- **Performance Testing**: [load and performance approach]

## 7. Rationale & Context

[Reasoning behind the requirements and design decisions.]

## 8. Dependencies & External Integrations

### External Systems
- **EXT-001**: [External system] - [Purpose and integration type]

### Third-Party Services
- **SVC-001**: [Service] - [Required capabilities and SLA]

### Infrastructure Dependencies
- **INF-001**: [Infrastructure component] - [Requirements]

### Data Dependencies
- **DAT-001**: [External data source] - [Format, frequency, access]

### Technology Platform Dependencies
- **PLT-001**: [Platform/runtime] - [Version constraints and rationale]

### Compliance Dependencies
- **COM-001**: [Regulatory requirement] - [Impact on implementation]

**Note**: Focus on architectural and business dependencies, not specific package implementations.

## 9. Examples & Edge Cases

[Code snippets or data examples demonstrating correct application, including edge cases.]

## 10. Validation Criteria

[Criteria or tests that must be satisfied for compliance with this specification.]

## 11. Related Specifications / Further Reading

[Links to related specs and external documentation.]
```
