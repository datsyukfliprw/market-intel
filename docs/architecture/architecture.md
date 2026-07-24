# System Architecture

**Project:** Project Market Intel (Placeholder Name)

------------------------------------------------------------------------

# Purpose

This document defines the structural rules for the Project Market Intel
codebase.

The Blueprint answers **what** the system is.

The Domain Dictionary answers **what each business concept means**.

This Architecture document answers **how the codebase is organized to
implement those concepts**.

------------------------------------------------------------------------

# Architectural Style

Project Market Intel follows a modular, domain-centric architecture.

Primary goals:

-   High cohesion
-   Low coupling
-   Replaceable infrastructure
-   Deterministic business logic
-   Testability
-   Long-term maintainability

------------------------------------------------------------------------

# Architectural Layers

``` text
Presentation
    │
Application
    │
Domain
    ▲
Infrastructure
```

## Presentation

Responsibilities:

-   REST APIs
-   CLI
-   Future UI

Must not contain business rules.

------------------------------------------------------------------------

## Application

Coordinates use cases.

Responsibilities:

-   Transactions
-   Workflow orchestration
-   Validation
-   Calling domain services

------------------------------------------------------------------------

## Domain

The heart of the platform.

Contains:

-   Entities
-   Value Objects
-   Domain Services
-   Business Rules
-   Invariants

The Domain layer must never depend on frameworks, databases, ORMs, HTTP,
or providers.

------------------------------------------------------------------------

## Infrastructure

Responsibilities:

-   Database
-   External APIs
-   AI providers
-   Message queues
-   File storage

Infrastructure depends on the Domain---not the reverse.

------------------------------------------------------------------------

# Dependency Rule

Allowed:

Presentation → Application → Domain

Infrastructure → Domain

Forbidden:

-   Domain → Infrastructure
-   Domain → Presentation
-   Repository → HTTP
-   Entity → Database

------------------------------------------------------------------------

# Transaction Ownership

Repositories never own transactions.

Application Services own transactions.

Repositories persist objects.

They do not commit business workflows.

------------------------------------------------------------------------

# Repository Responsibilities

Repositories:

-   Save
-   Update
-   Delete
-   Retrieve

Repositories never:

-   Score securities
-   Evaluate strategies
-   Call AI
-   Perform calculations

------------------------------------------------------------------------

# Service Responsibilities

Application Services:

-   Coordinate workflows
-   Manage transactions
-   Call repositories
-   Call domain services

Domain Services:

-   Implement business rules
-   Evaluate strategies
-   Calculate scores
-   Produce recommendations

------------------------------------------------------------------------

# Domain Entities

Entities should represent business concepts rather than database tables.

Each entity should:

-   Have one identity
-   Protect its invariants
-   Expose meaningful behavior

Avoid anemic models where possible.

------------------------------------------------------------------------

# Error Handling

Business errors belong in the Domain.

Infrastructure failures belong in Infrastructure.

Application Services translate errors between layers.

------------------------------------------------------------------------

# Testing Strategy

Unit Tests

-   Domain
-   Domain Services
-   Value Objects

Integration Tests

-   Repositories
-   Providers
-   Database

End-to-End Tests

-   API
-   Full workflows

Tests should verify behavior rather than implementation details.

------------------------------------------------------------------------

# Naming Conventions

Prefer business language.

Good:

-   Recommendation
-   StrategyEvaluation
-   MarketSnapshot

Avoid infrastructure-driven names in the domain.

------------------------------------------------------------------------

# Dependency Injection

External implementations should be injected behind interfaces.

The Domain should never know which concrete implementation is executing.

------------------------------------------------------------------------

# Architectural Evolution

The architecture is expected to evolve deliberately.

Large structural changes should:

1.  Begin with an Architecture Gate.
2.  Be documented in an ADR.
3.  Be reflected in the Blueprint if they change long-term direction.

------------------------------------------------------------------------

# Closing Principle

The architecture exists to make future change easier.

Every implementation should reduce complexity, strengthen boundaries,
and leave the codebase easier to understand than before.
