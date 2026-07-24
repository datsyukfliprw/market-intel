# Market Intel Project Rules

> **These rules exist to protect the quality, consistency, and long-term maintainability of the project.**

---

# Team Roles

## Product Owner

Responsible for:

- Vision
- Feature prioritization
- Final approval
- Release decisions

## Architect

Responsible for:

- System design
- Technical direction
- Code reviews
- Design consistency
- Long-term maintainability

## Implementation Engineer

Responsible for:

- Feature implementation
- Refactoring
- Testing
- Documentation
- Bug fixes

Implementation should follow the architecture rather than redefine it.

---

# General Principles

- Readability is more important than cleverness.
- Simplicity is preferred over unnecessary abstraction.
- Explicit behavior is preferred over hidden magic.
- Every feature should solve a real problem.
- Every design decision should be explainable.

---

# Architecture Rules

Business logic must never depend on UI code.

Business logic should remain independent of:

- React
- FastAPI
- Database implementation
- AI providers

Core logic should be reusable from tests, scripts, APIs, and future interfaces.

---

# Coding Standards

## Python

- Use Python 3.13+
- Use type hints everywhere.
- Follow PEP 8.
- Prefer descriptive names.
- Avoid global state.
- Keep modules focused.

---

## Functions

Functions should:

- Have one responsibility.
- Be easy to test.
- Avoid unnecessary side effects.
- Return predictable results.

Avoid excessively long functions. If a function becomes difficult to understand, refactor it into smaller pieces.

---

## Classes

Classes should represent meaningful concepts.

Avoid creating classes solely for organizational purposes.

Favor composition over inheritance whenever practical.

---

## Configuration

Never hardcode:

- API keys
- Secrets
- File paths
- Credentials
- URLs that may change

Use configuration files or environment variables.

---

# Documentation

Every public module should include:

- Purpose
- Inputs
- Outputs
- Important assumptions

Complex algorithms should explain _why_ they exist, not just _what_ they do.

---

# Testing

Critical business logic requires automated tests.

Tests should be:

- Independent
- Deterministic
- Fast
- Easy to understand

Bug fixes should include regression tests whenever practical.

---

# Logging

Log meaningful events.

Avoid noisy logs.

Logs should help answer:

- What happened?
- When?
- Why?
- What failed?
- What should happen next?

---

# Error Handling

Errors should:

- Be explicit.
- Include useful context.
- Never silently fail.
- Never expose secrets.

Unexpected failures should degrade gracefully whenever possible.

---

# Git Workflow

- One feature per branch.
- One logical change per pull request.
- Keep commits focused.
- Use descriptive commit messages.

Example commit prefixes:

- feat:
- fix:
- refactor:
- docs:
- test:
- chore:

---

# Pull Requests

A pull request should answer:

- What changed?
- Why?
- How was it tested?
- Are there any known limitations?

Small pull requests are preferred over large ones.

---

# Issue Workflow

Each issue should contain:

- Objective
- Requirements
- Acceptance criteria
- Out-of-scope items (when helpful)
- Links to related documentation

Avoid vague requests such as "Improve scanner."

Prefer precise tasks such as "Add Relative Volume calculation using a configurable lookback period."

---

# AI Usage

AI is an implementation assistant.

AI should not make architectural decisions without review.

AI-generated code must be:

- Reviewed
- Tested
- Understood
- Maintainable

Never merge code solely because it compiles.

---

# Devin Guidelines

When assigning work to Devin:

- Keep tasks focused.
- Reference the relevant documentation.
- Define clear acceptance criteria.
- Prefer incremental improvements.
- Request tests where appropriate.

Devin should optimize for clarity, maintainability, and correctness over clever implementations.

---

# Performance

Optimize only after measuring.

Avoid premature optimization.

When optimization is necessary:

1. Measure.
2. Identify the bottleneck.
3. Improve the bottleneck.
4. Measure again.

---

# Security

Never commit:

- API keys
- Passwords
- Tokens
- Credentials
- Private certificates

Validate external inputs.

Assume external data may be malformed or incomplete.

---

# Explainability

Every important score, recommendation, or decision should be traceable to evidence.

The platform should never require users to trust unexplained outputs.

---

# Definition of Done

A task is complete only when:

- Requirements are met.
- Code is readable.
- Tests pass.
- Documentation is updated.
- No obvious technical debt has been introduced.
- The implementation aligns with the Vision, Manifesto, and Architecture documents.

---

# Final Rule

Whenever there is uncertainty, choose the solution that is easier to understand, easier to test, and easier to maintain.

Future contributors should be able to understand the codebase without needing to guess the original intent.
