# Blueprint v2 (Part 5): Request Lifecycle

**Project:** Project Market Intel

------------------------------------------------------------------------

# Purpose

This chapter defines the canonical lifecycle of a request through
Project Market Intel. Every feature should follow this flow unless an
Architectural Decision Record explicitly documents an exception.

------------------------------------------------------------------------

# End-to-End Flow

``` text
User
 │
 ▼
Presentation (Web / Mobile)
 │
 ▼
API Controller
 │
 ▼
Application Service
 │
 ▼
Domain Services
 │
 ├──────────────► Domain Events
 ▼
Repository Interfaces
 │
 ▼
Repository Implementations
 │
 ▼
Database / External Providers
 │
 ▲
 └────────────── Result
 │
 ▼
Application Service
 │
 ▼
API Response
 │
 ▼
Presentation
```

------------------------------------------------------------------------

# Step 1: Presentation

Responsibilities:

-   Collect user input
-   Perform basic client-side validation
-   Display loading, success, and error states

Presentation never performs business calculations.

------------------------------------------------------------------------

# Step 2: API Controller

Responsibilities:

-   Authenticate requests
-   Validate DTOs
-   Translate HTTP concepts into application requests
-   Return standardized responses

Controllers contain no business rules.

------------------------------------------------------------------------

# Step 3: Application Service

Responsibilities:

-   Execute a use case
-   Define transaction boundaries
-   Coordinate repositories and domain services
-   Publish domain events

Application services orchestrate. They do not decide business policy.

------------------------------------------------------------------------

# Step 4: Domain Layer

Responsibilities:

-   Enforce business rules
-   Evaluate strategies
-   Generate recommendations
-   Validate invariants
-   Produce domain events

The Domain layer has no knowledge of HTTP, databases, ORMs, or AI
providers.

------------------------------------------------------------------------

# Step 5: Persistence & Providers

Infrastructure responsibilities:

-   Persist domain state
-   Retrieve market data
-   Call external services
-   Send notifications
-   Invoke AI providers

Infrastructure translates between external systems and domain models.

------------------------------------------------------------------------

# Step 6: Response Construction

Application Services:

-   Map domain objects to response DTOs
-   Record telemetry
-   Complete transactions
-   Return results to controllers

Controllers serialize the final response.

------------------------------------------------------------------------

# Error Handling

Errors are handled at the appropriate layer:

-   Presentation: input feedback
-   API: request validation and HTTP status codes
-   Application: workflow failures
-   Domain: business rule violations
-   Infrastructure: provider, network, and persistence failures

Each layer handles only the errors it owns.

------------------------------------------------------------------------

# Design Rules

-   Every request has a single orchestration point.
-   Business logic exists only in the Domain.
-   Dependencies always point inward.
-   External failures never leak infrastructure details into the Domain.

------------------------------------------------------------------------

# Related Documents

-   Component Architecture
-   ADR-001 Domain-First Architecture
-   ADR-005 Event Processing Strategy
-   ADR-006 Persistence Strategy

------------------------------------------------------------------------

# Next Sections

-   Recommendation Pipeline
-   Domain Model Overview
-   Persistence Model
