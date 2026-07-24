# ADR-005: Event Processing Strategy

**ADR ID:** ADR-005

**Status:** Accepted

**Date:** 2026-07-24

------------------------------------------------------------------------

# Problem Statement

Project Market Intel will execute scans, scoring, alerts, paper trading,
and AI explanations. Some work must complete immediately while other
tasks can occur later without blocking the user.

A consistent event processing strategy is required to support growth
without introducing unnecessary complexity.

------------------------------------------------------------------------

# Decision

The platform will adopt a **synchronous-first, event-ready**
architecture.

Business operations execute synchronously by default. Long-running or
non-critical work is represented as domain events so it can move to
asynchronous processing when scale requires.

------------------------------------------------------------------------

# Goals

-   Keep the initial architecture simple
-   Avoid premature distributed systems
-   Support future background processing
-   Ensure deterministic business workflows
-   Make asynchronous migration incremental

------------------------------------------------------------------------

# Event Categories

Core event types include:

-   ScanCompleted
-   RecommendationCreated
-   AlertTriggered
-   PaperTradeExecuted
-   AIExplanationRequested
-   ProviderUnavailable

Events describe something that has already happened.

------------------------------------------------------------------------

# Processing Rules

-   Critical business workflows complete synchronously.
-   Notifications and AI explanations may execute asynchronously.
-   Events are immutable.
-   Events include timestamps and version information.
-   Event handlers should be idempotent whenever practical.

------------------------------------------------------------------------

# Failure Handling

If an event handler fails:

1.  Record the failure.
2.  Retry when appropriate.
3.  Prevent duplicate side effects.
4.  Never corrupt completed business transactions.

------------------------------------------------------------------------

# Alternatives Considered

## Fully Synchronous

Rejected because future scalability would require significant
refactoring.

## Event-Driven From Day One

Rejected because operational complexity outweighs current needs.

## Synchronous Core with Event Evolution

Accepted because it balances simplicity with long-term flexibility.

------------------------------------------------------------------------

# Tradeoffs

## Benefits

-   Simple initial implementation
-   Clear migration path
-   Better scalability
-   Easier testing
-   Reduced operational burden

## Costs

-   Future event infrastructure still required
-   Some orchestration logic remains synchronous initially

------------------------------------------------------------------------

# Future Evolution

When justified, event handlers may migrate to:

-   Background workers
-   Message queues
-   Event streaming platforms

This migration should not require changes to the Domain layer.

------------------------------------------------------------------------

# Related Documents

-   Blueprint
-   Architecture
-   ADR-001 Domain-First Architecture
-   ADR-002 Provider Abstraction Layer
-   ADR-003 Scoring Engine Architecture
-   ADR-004 AI Explanation Boundary

------------------------------------------------------------------------

# Closing Statement

Architecture should evolve with demand. Complexity should be introduced
only when it solves a demonstrated problem.
