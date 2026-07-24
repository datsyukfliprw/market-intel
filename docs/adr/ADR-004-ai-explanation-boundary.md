# ADR-004: AI Explanation Boundary

**ADR ID:** ADR-004

**Status:** Accepted

**Date:** 2026-07-24

------------------------------------------------------------------------

# Problem Statement

Artificial intelligence can summarize and explain complex information,
but large language models are probabilistic systems. If AI is allowed to
generate trading decisions or calculate technical indicators, the
platform loses determinism, reproducibility, and auditability.

------------------------------------------------------------------------

# Decision

Artificial intelligence is responsible for explaining decisions, **not
making them**.

Every recommendation must be produced by deterministic business logic
before an AI model is invoked.

------------------------------------------------------------------------

# Goals

-   Preserve deterministic recommendations
-   Improve transparency
-   Allow AI providers to be replaced
-   Maintain reproducible historical results
-   Prevent hallucinated trading logic

------------------------------------------------------------------------

# Responsibilities of AI

AI may:

-   Explain recommendations
-   Summarize market conditions
-   Describe strengths and weaknesses
-   Rewrite technical language for different audiences
-   Generate educational content

AI must **not**:

-   Calculate indicators
-   Produce scores
-   Decide whether to buy or sell
-   Modify historical data
-   Override business rules

------------------------------------------------------------------------

# Information Flow

``` text
Market Data
      │
      ▼
Indicators
      │
      ▼
Scoring Engine
      │
      ▼
Strategy Evaluation
      │
      ▼
Recommendation
      │
      ▼
AI Explanation
      │
      ▼
User
```

AI is always the final explanatory layer.

------------------------------------------------------------------------

# Alternatives Considered

## AI-Centric Decision Making

Rejected because recommendations would become non-deterministic and
difficult to audit.

## Deterministic Engine + AI Explanation

Accepted because it separates business logic from natural-language
generation.

------------------------------------------------------------------------

# Tradeoffs

## Benefits

-   Reproducible recommendations
-   Easier testing
-   Better regulatory readiness
-   Clear separation of responsibilities
-   Freedom to swap AI providers

## Costs

-   Additional orchestration layer
-   Two-step recommendation pipeline

------------------------------------------------------------------------

# Consequences

Historical recommendations remain valid even if AI models improve or
change.

Future AI integrations should consume structured domain objects rather
than raw market feeds.

------------------------------------------------------------------------

# Related Documents

-   Blueprint
-   Architecture
-   Engineering Principles
-   ADR-001 Domain-First Architecture
-   ADR-002 Provider Abstraction Layer
-   ADR-003 Scoring Engine Architecture

------------------------------------------------------------------------

# Closing Statement

AI enhances understanding. It never replaces the deterministic reasoning
at the heart of Project Market Intel.
