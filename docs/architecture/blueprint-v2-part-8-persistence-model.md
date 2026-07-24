# Blueprint v2 (Part 8): Persistence Model

**Project:** Project Market Intel

------------------------------------------------------------------------

# Purpose

This chapter defines how domain objects are persisted while preserving
the architectural boundary between the Domain and Infrastructure layers.
Persistence is an implementation detail; the business model remains
independent of storage technology.

------------------------------------------------------------------------

# Architectural Principles

-   The Domain never depends on the database.
-   Repository interfaces live in the Domain.
-   Repository implementations live in Infrastructure.
-   Transactions are owned by the Application layer.
-   Persistence models are implementation details.

------------------------------------------------------------------------

# Aggregate Persistence

Each aggregate is loaded and saved as a consistency boundary.

Primary aggregates include:

-   Recommendation
-   Portfolio
-   Strategy
-   Scan Run
-   Alert

Repositories are responsible for reconstructing aggregates from
persistent storage.

------------------------------------------------------------------------

# Repository Responsibilities

Repositories:

-   Load aggregates
-   Save aggregates
-   Query domain objects
-   Translate between domain and persistence models

Repositories must not contain business rules.

------------------------------------------------------------------------

# Transaction Boundaries

Application Services:

-   Begin transactions
-   Coordinate multiple repositories
-   Commit successful operations
-   Roll back failed operations

The Domain is unaware of transaction management.

------------------------------------------------------------------------

# Persistence Mapping

``` text
Domain Entity
      │
      ▼
Repository Interface
      │
      ▼
Repository Implementation
      │
      ▼
ORM / SQL
      │
      ▼
Database
```

Mapping logic remains confined to Infrastructure.

------------------------------------------------------------------------

# Schema Evolution

Database changes must:

-   Be version controlled
-   Use migrations
-   Preserve historical integrity
-   Be reversible whenever practical

Production schema changes should never bypass migration tooling.

------------------------------------------------------------------------

# Historical Data

Historical records such as:

-   Market data
-   Recommendations
-   Paper trades
-   Scan results

should be treated as append-only whenever practical to preserve
reproducibility and auditability.

------------------------------------------------------------------------

# Performance Considerations

Optimization techniques may include:

-   Read models
-   Database indexes
-   Query projections
-   Caching
-   Batch operations

Performance optimizations must not leak into the Domain model.

------------------------------------------------------------------------

# Related Documents

-   Domain Model Overview
-   ADR-006 Persistence Strategy
-   ADR-014 Backtesting Architecture
-   ADR-015 Paper Trading Execution Model

------------------------------------------------------------------------

# Next Sections

-   Provider Architecture
-   AI Integration
-   Strategy Plugin System
