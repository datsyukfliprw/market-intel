# Engineering Principles

**Project:** Project Market Intel

------------------------------------------------------------------------

# Purpose

These principles guide engineering decisions across the project. When
two valid implementations exist, prefer the one that best aligns with
these principles.

------------------------------------------------------------------------

# 1. Optimize for Maintainability

Code is read far more often than it is written.

Favor clarity over cleverness.

------------------------------------------------------------------------

# 2. Domain Before Technology

Business concepts should shape the architecture.

Frameworks and libraries are implementation details.

------------------------------------------------------------------------

# 3. Leave It Better

Every change should improve the codebase, even if only slightly.

Reduce duplication, improve names, simplify logic, or add tests when
practical.

------------------------------------------------------------------------

# 4. Explicit Over Implicit

Avoid hidden behavior and surprising side effects.

Prefer code that is obvious to the next engineer.

------------------------------------------------------------------------

# 5. Single Responsibility

Modules, classes, and functions should each have one primary reason to
change.

------------------------------------------------------------------------

# 6. Composition Over Inheritance

Favor composing small, focused components rather than deep inheritance
trees.

------------------------------------------------------------------------

# 7. Stable Interfaces

Design interfaces to remain stable while implementations evolve.

------------------------------------------------------------------------

# 8. Small, Reversible Changes

Prefer incremental improvements over risky rewrites.

Large architectural changes require an Architecture Gate.

------------------------------------------------------------------------

# 9. Test Behavior

Tests should validate business behavior, not internal implementation
details.

------------------------------------------------------------------------

# 10. Make Failures Clear

Fail fast, provide meaningful errors, and avoid silent failures.

------------------------------------------------------------------------

# 11. Keep the Domain Pure

Business logic must remain independent of databases, HTTP, AI providers,
and UI frameworks.

------------------------------------------------------------------------

# 12. Document Decisions

Significant architectural decisions belong in an ADR.

Temporary reasoning belongs in pull requests, not permanent
documentation.

------------------------------------------------------------------------

# Code Review Checklist

-   Correctness
-   Simplicity
-   Readability
-   Naming
-   Separation of concerns
-   Testability
-   Architectural consistency
-   Future maintainability

------------------------------------------------------------------------

# Closing Principle

Every engineering decision should increase the project's long-term
quality, not merely satisfy today's requirement.
