# Development Workflow

**Project:** Project Market Intel

------------------------------------------------------------------------

# Purpose

This document defines the standard engineering workflow used throughout
the project. Every feature, architectural change, and milestone follows
this process.

------------------------------------------------------------------------

# Team Roles

## Product Owner (Jay)

Responsibilities:

-   Define vision and priorities
-   Approve milestones
-   Accept or reject architectural direction
-   Approve completed work

------------------------------------------------------------------------

## Chief Software Architect (ChatGPT)

Responsibilities:

-   Design long-term architecture
-   Protect architectural integrity
-   Write milestone specifications
-   Produce Architecture Gates
-   Review implementations
-   Prevent unnecessary technical debt

------------------------------------------------------------------------

## Lead Software Engineer (Devin)

Responsibilities:

-   Implement approved specifications
-   Write production-ready code
-   Create tests
-   Verify implementation
-   Document implementation decisions

------------------------------------------------------------------------

# Standard Workflow

1.  Product Owner selects the next milestone.
2.  Chief Software Architect evaluates architectural impact.
3.  If required, an Architecture Gate is opened.
4.  Milestone Specification is written and approved.
5.  Lead Software Engineer implements the milestone.
6.  Implementation is verified by the engineer.
7.  Architectural Review is completed.
8.  Blocking issues are resolved.
9.  Definition of Done is verified.
10. Changes are committed and pushed.

------------------------------------------------------------------------

# Architecture Gates

An Architecture Gate is required when work changes:

-   Domain models
-   System boundaries
-   Persistence strategy
-   Public APIs
-   Provider interfaces
-   Dependency direction
-   Major architectural patterns

Implementation pauses until the design is approved.

------------------------------------------------------------------------

# Architectural Review

Every implementation is reviewed using three sections:

## Blocking Issues

Problems that must be resolved before merge.

## Recommended Improvements

Enhancements that improve maintainability but do not block progress.

## Future Enhancements

Ideas intentionally deferred to later milestones.

------------------------------------------------------------------------

# Definition of Done

Every milestone must satisfy the project's Definition of Done before
completion.

------------------------------------------------------------------------

# Architecture Decision Records

Significant architectural decisions require an ADR.

Each ADR should explain:

-   Why the decision exists
-   Alternatives considered
-   Tradeoffs
-   Risks
-   Long-term consequences

------------------------------------------------------------------------

# Git Workflow

Each completed milestone should:

-   Build successfully
-   Pass tests
-   Include documentation updates
-   Be committed with meaningful messages
-   Leave the default branch releasable

------------------------------------------------------------------------

# Escalation Rules

If implementation conflicts with the approved architecture:

1.  Pause implementation.
2.  Open an Architecture Gate.
3.  Review alternatives.
4.  Update documentation if direction changes.
5.  Resume implementation only after approval.

------------------------------------------------------------------------

# Continuous Improvement

After every milestone, ask:

-   Did we improve the architecture?
-   Did we reduce complexity?
-   Did we document important decisions?
-   Did we leave the project better than we found it?

------------------------------------------------------------------------

# Closing Principle

The workflow exists to produce maintainable software, preserve
architectural integrity, and enable steady long-term progress.
