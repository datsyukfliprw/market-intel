# Data Flow Handbook

**Project:** Project Market Intel

## Purpose

This handbook documents how data moves through the platform, who owns it
at each stage, how it is transformed, and where it is persisted. It
complements the Sequence Diagram Handbook by focusing on data ownership
rather than execution order.

------------------------------------------------------------------------

# Guiding Principles

-   Every datum has a single source of truth.
-   Domain objects are the canonical representation of business
    concepts.
-   External payloads are normalized before entering the Domain.
-   Transformations are explicit and traceable.
-   Derived data is reproducible from persisted inputs whenever
    practical.

------------------------------------------------------------------------

# Flow 1: Market Data

``` text
Market Data Provider
        │
        ▼
Provider Adapter
        │
        ▼
Normalization Layer
        │
        ▼
Domain Market Snapshot
        │
        ▼
Indicator Engine
```

Ownership:

-   Provider Adapter owns protocol translation.
-   Normalization Layer owns canonical formatting.
-   Domain owns normalized market objects.

------------------------------------------------------------------------

# Flow 2: Recommendation Pipeline

``` text
Indicators
    │
    ▼
Strategy Plugin
    │
    ▼
Recommendation Candidate
    │
    ▼
Scoring Engine
    │
    ▼
Recommendation Aggregate
    │
    ▼
Repository
```

Transformations:

-   Raw indicators become signals.
-   Signals become recommendation candidates.
-   Candidates become persisted recommendations.

------------------------------------------------------------------------

# Flow 3: AI Explanation

``` text
Recommendation Aggregate
        │
        ▼
Context Builder
        │
        ▼
AI Provider
        │
        ▼
Structured Explanation
        │
        ▼
Presentation Layer
```

Only immutable recommendation data is supplied to AI.

------------------------------------------------------------------------

# Flow 4: Alerts

``` text
Recommendation Published
        │
        ▼
Alert Rules
        │
        ▼
Alert Event
        │
        ▼
Notification Provider
        │
        ▼
User
```

Alert delivery never modifies the originating recommendation.

------------------------------------------------------------------------

# Persistence Map

Persisted:

-   Recommendations
-   Scan runs
-   Portfolios
-   Paper trades
-   Alerts
-   Configuration

Transient:

-   Provider payloads
-   Request DTOs
-   Queue messages
-   Cached market data

------------------------------------------------------------------------

# Traceability

Every persisted recommendation should be traceable to:

-   Source market data
-   Strategy version
-   Indicator snapshot
-   Confidence score
-   Execution timestamp

------------------------------------------------------------------------

# Related Documents

-   Blueprint v2 Parts 6--12
-   Sequence Diagram Handbook
-   ADR-002 Provider Abstraction
-   ADR-003 Scoring Engine
-   ADR-006 Persistence Strategy
