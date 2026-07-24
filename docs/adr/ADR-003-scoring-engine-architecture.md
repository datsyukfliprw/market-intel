# ADR-003: Scoring Engine Architecture

**ADR ID:** ADR-003

**Status:** Accepted

**Date:** 2026-07-24

------------------------------------------------------------------------

# Problem Statement

Project Market Intel must evaluate securities using multiple independent
signals while remaining transparent, testable, and easy to evolve.

A single monolithic scoring algorithm would become difficult to
understand, extend, and validate.

------------------------------------------------------------------------

# Decision

The scoring engine will be composed of independent scoring components.

Each component evaluates one aspect of market evidence and produces a
normalized score.

A coordinator combines component scores into a final composite score.

------------------------------------------------------------------------

# Goals

-   Modular scoring
-   Explainable results
-   Easy experimentation
-   Independent testing
-   Versioned scoring logic

------------------------------------------------------------------------

# Scoring Components

Potential components include:

-   Trend Score
-   Momentum Score
-   Volume Score
-   Volatility Score
-   Relative Strength Score
-   Fundamental Score
-   Risk Score
-   Liquidity Score

Each component owns only its own calculation.

------------------------------------------------------------------------

# Rules

-   Components do not communicate with one another.
-   Components are deterministic.
-   Inputs are immutable.
-   Outputs are normalized.
-   Composite scoring performs aggregation only.

------------------------------------------------------------------------

# Versioning

Every scoring configuration receives a version identifier.

Historical recommendations retain the scoring version that produced them
to ensure reproducibility.

------------------------------------------------------------------------

# Alternatives Considered

## One Large Algorithm

Rejected due to complexity and poor maintainability.

## Independent Component Architecture

Accepted because it improves extensibility, testing, and transparency.

------------------------------------------------------------------------

# Tradeoffs

## Benefits

-   Easier maintenance
-   Clear ownership
-   Better testing
-   Explainable recommendations
-   Incremental improvements

## Costs

-   More classes/modules
-   Coordination layer required

------------------------------------------------------------------------

# Consequences

New scoring ideas should be implemented as additional components rather
than modifying unrelated calculations.

Composite weighting changes should preserve backward compatibility
through versioning.

------------------------------------------------------------------------

# Related Documents

-   Blueprint
-   Architecture
-   Domain Dictionary
-   ADR-001 Domain-First Architecture
-   ADR-002 Provider Abstraction Layer

------------------------------------------------------------------------

# Closing Statement

A scoring engine should evolve by adding well-defined knowledge, not by
increasing complexity within a single algorithm.
