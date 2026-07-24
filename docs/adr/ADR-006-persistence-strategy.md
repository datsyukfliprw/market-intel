# ADR-006: Persistence Strategy

**ADR ID:** ADR-006

**Status:** Accepted

**Date:** 2026-07-24

------------------------------------------------------------------------

# Problem Statement

Project Market Intel must preserve historical market observations,
recommendations, scoring results, and system activity while remaining
flexible enough to evolve its storage technologies over time.

The persistence strategy must support reproducibility, auditability, and
long-term maintainability.

------------------------------------------------------------------------

# Decision

The platform will treat persistence as an infrastructure concern behind
repository interfaces.

The Domain layer owns business concepts.

Repositories own persistence operations.

Database implementations remain replaceable.

------------------------------------------------------------------------

# Goals

-   Preserve historical accuracy
-   Support deterministic replay
-   Minimize coupling to storage technology
-   Enable future database evolution
-   Keep business logic storage-agnostic

------------------------------------------------------------------------

# Principles

-   Domain objects are independent of ORM models.
-   Repositories translate between persistence and domain models.
-   Historical records are append-only whenever practical.
-   Migrations are version controlled.
-   Schema evolution is deliberate and reversible.

------------------------------------------------------------------------

# Data Categories

## Reference Data

Examples:

-   Instruments
-   Exchanges
-   Calendars

Rarely changes.

## Operational Data

Examples:

-   Scan Runs
-   Recommendations
-   Alerts
-   Paper Trades

Created continuously.

## Historical Data

Examples:

-   OHLC bars
-   Indicator snapshots
-   Scoring history

Never silently rewritten.

------------------------------------------------------------------------

# Transaction Rules

-   Application Services define transaction boundaries.
-   Repositories participate in transactions.
-   Business logic never opens database connections directly.

------------------------------------------------------------------------

# Alternatives Considered

## Active Record

Rejected because it couples business logic to persistence.

## Repository Pattern

Accepted because it preserves clean architectural boundaries.

------------------------------------------------------------------------

# Tradeoffs

## Benefits

-   Easier testing
-   Replaceable databases
-   Cleaner domain model
-   Better separation of concerns

## Costs

-   Additional mapping layer
-   More implementation code

------------------------------------------------------------------------

# Future Evolution

The architecture should support migration from SQLite to PostgreSQL or
other storage technologies with minimal impact on the Domain layer.

Read models, caching layers, and analytics databases may be introduced
independently when justified.

------------------------------------------------------------------------

# Related Documents

-   Blueprint
-   Architecture
-   Domain Dictionary
-   ADR-001 Domain-First Architecture
-   ADR-002 Provider Abstraction Layer
-   ADR-005 Event Processing Strategy

------------------------------------------------------------------------

# Closing Statement

Data is one of the project's most valuable assets. The persistence
strategy should protect its integrity while allowing storage technology
to evolve independently.
