# Contributor Guide

**Project:** Project Market Intel

------------------------------------------------------------------------

# Welcome

Welcome to Project Market Intel.

This guide explains how contributors are expected to work within the
project. It is intended to promote consistency, maintainability, and
long-term architectural integrity.

Before contributing, read the following documents:

-   Constitution
-   Engineering Principles
-   Development Workflow
-   Definition of Done
-   Architecture
-   Blueprint
-   Domain Dictionary

These documents define the project's engineering standards.

------------------------------------------------------------------------

# Engineering Philosophy

Contributors are expected to:

-   Prioritize maintainability.
-   Protect architectural boundaries.
-   Improve the codebase with every change.
-   Favor clarity over cleverness.
-   Write software for future engineers.

------------------------------------------------------------------------

# Before Writing Code

Every feature should begin with:

1.  A clearly defined milestone.
2.  Architectural review (if required).
3.  Approved Milestone Specification.

Do not implement speculative features.

------------------------------------------------------------------------

# Branch Strategy

Recommended branch names:

-   feature/`<name>`{=html}
-   fix/`<name>`{=html}
-   refactor/`<name>`{=html}
-   docs/`<name>`{=html}
-   experiment/`<name>`{=html}

Keep branches focused on a single objective.

------------------------------------------------------------------------

# Commit Messages

Prefer concise, descriptive commits.

Examples:

-   feat: add recommendation repository
-   fix: correct scoring calculation
-   refactor: simplify strategy evaluation
-   docs: expand architecture blueprint
-   test: add repository integration tests

------------------------------------------------------------------------

# Coding Standards

Contributors should:

-   Use domain language.
-   Keep functions focused.
-   Avoid unnecessary abstraction.
-   Prefer composition.
-   Write self-documenting code.

------------------------------------------------------------------------

# Documentation

Documentation is part of every milestone.

Update documentation whenever architecture, workflows, or public
behavior changes.

------------------------------------------------------------------------

# Testing

Every contribution should include appropriate verification.

Possible test types:

-   Unit
-   Integration
-   API
-   End-to-End
-   Manual verification

All automated tests should pass before merge.

------------------------------------------------------------------------

# Architectural Changes

If a contribution affects:

-   Domain boundaries
-   Dependency direction
-   Persistence
-   Provider interfaces
-   Public APIs

Open an Architecture Gate before implementation.

Major architectural decisions require an ADR.

------------------------------------------------------------------------

# Pull Requests

A pull request should include:

-   Purpose
-   Summary of changes
-   Testing performed
-   Documentation updates
-   Known limitations

------------------------------------------------------------------------

# Code Reviews

Reviews focus on:

-   Correctness
-   Maintainability
-   Readability
-   Architectural consistency
-   Test coverage
-   Future impact

Feedback should improve the software, not criticize the contributor.

------------------------------------------------------------------------

# Continuous Improvement

Every contributor should ask:

-   Is this easier to understand?
-   Is duplication reduced?
-   Are boundaries clearer?
-   Does this follow the Engineering Principles?

------------------------------------------------------------------------

# Closing Principle

Every contribution should leave Project Market Intel stronger than it
was before.
