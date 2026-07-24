# Sequence Diagram Handbook

**Project:** Project Market Intel

## Purpose

This handbook supplements Blueprint v2 by documenting the runtime
interactions between major components. Each sequence diagram focuses on
one business capability and shows ownership boundaries, message flow,
and transaction responsibility.

------------------------------------------------------------------------

# Sequence 1: Recommendation Generation

``` text
Scheduler/API
     │
     ▼
Application Service
     │
     ▼
Market Data Provider
     │
     ▼
Indicator Engine
     │
     ▼
Strategy Plugin
     │
     ▼
Scoring Engine
     │
     ▼
Recommendation Repository
     │
     ▼
Domain Event
```

Key points:

-   The Application Service orchestrates the workflow.
-   Strategy plugins remain deterministic.
-   Persistence occurs only after scoring is complete.

------------------------------------------------------------------------

# Sequence 2: AI Explanation

``` text
Recommendation
      │
      ▼
AI Context Builder
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

Key points:

-   AI never participates in recommendation generation.
-   Failures do not invalidate the recommendation.

------------------------------------------------------------------------

# Sequence 3: Alert Delivery

``` text
Recommendation Published
        │
        ▼
Alert Service
        │
        ▼
Notification Provider
        │
        ▼
User
```

Key points:

-   Alert delivery is asynchronous.
-   Retries occur within the background job system.

------------------------------------------------------------------------

# Sequence 4: Paper Trade Execution

``` text
Recommendation
      │
      ▼
Paper Trading Service
      │
      ▼
Portfolio Aggregate
      │
      ▼
Repository
      │
      ▼
Portfolio Updated Event
```

Key points:

-   Paper trades never invoke brokerage providers.
-   Portfolio invariants are enforced before persistence.

------------------------------------------------------------------------

# Related Documents

-   Blueprint v2 Parts 5, 6, 10, 11, and 12
-   ADR-003 Scoring Engine
-   ADR-007 Alert Delivery
-   ADR-014 Backtesting
-   ADR-015 Paper Trading
