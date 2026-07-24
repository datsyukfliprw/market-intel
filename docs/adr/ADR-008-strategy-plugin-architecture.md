# ADR-008: Strategy Plugin Architecture

**ADR ID:** ADR-008

**Status:** Accepted

**Date:** 2026-07-24

------------------------------------------------------------------------

# Problem Statement

Project Market Intel will support multiple trading and screening
strategies. New strategies should be introduced without modifying the
core recommendation engine or affecting existing strategies.

------------------------------------------------------------------------

# Decision

Strategies will be implemented as independent plugins that conform to a
common strategy interface.

The application discovers and executes strategies through the interface
rather than concrete implementations.

------------------------------------------------------------------------

# Goals

-   Independent strategy development
-   Minimal coupling
-   Safe experimentation
-   Versioned strategies
-   Parallel execution support

------------------------------------------------------------------------

# Strategy Responsibilities

A strategy may:

-   Evaluate market evidence
-   Produce a recommendation
-   Return supporting evidence
-   Emit standardized results

A strategy must not:

-   Retrieve market data directly
-   Persist data
-   Send alerts
-   Call AI providers

------------------------------------------------------------------------

# Lifecycle

1.  Strategy is registered.
2.  Inputs are validated.
3.  Strategy evaluates evidence.
4.  Standardized results are returned.
5.  Recommendation pipeline continues.

------------------------------------------------------------------------

# Interface Principles

Every strategy should expose:

-   Identifier
-   Version
-   Display name
-   Supported asset classes
-   Evaluation entry point

Strategies communicate only through domain models.

------------------------------------------------------------------------

# Alternatives Considered

## Embedded Business Logic

Rejected because every new strategy would require modifying the core
engine.

## Plugin Architecture

Accepted because it supports extensibility while preserving
architectural boundaries.

------------------------------------------------------------------------

# Tradeoffs

## Benefits

-   Easy experimentation
-   Cleaner ownership
-   Independent testing
-   Incremental deployment
-   Future marketplace potential

## Costs

-   Registration infrastructure
-   Interface maintenance
-   Version compatibility management

------------------------------------------------------------------------

# Future Evolution

Future capabilities may include:

-   User-selectable strategies
-   Strategy composition
-   Parameterized strategies
-   Community-developed plugins
-   Backtesting across strategy versions

------------------------------------------------------------------------

# Related Documents

-   Blueprint
-   Architecture
-   Domain Dictionary
-   ADR-001 Domain-First Architecture
-   ADR-003 Scoring Engine Architecture
-   ADR-005 Event Processing Strategy

------------------------------------------------------------------------

# Closing Statement

The platform should grow by adding new strategies, not by increasing the
complexity of existing ones.
