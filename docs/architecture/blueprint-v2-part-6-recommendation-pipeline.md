# Blueprint v2 (Part 6): Recommendation Pipeline

**Project:** Project Market Intel

------------------------------------------------------------------------

# Purpose

The Recommendation Pipeline is the primary business workflow of Project
Market Intel. It transforms raw market information into deterministic,
explainable recommendations through a series of well-defined stages.
Each stage has a single responsibility and produces structured outputs
for the next stage.

------------------------------------------------------------------------

# Pipeline Overview

``` text
Market Data
    │
    ▼
Data Normalization
    │
    ▼
Indicator Calculation
    │
    ▼
Strategy Selection
    │
    ▼
Strategy Execution
    │
    ▼
Scoring Engine
    │
    ▼
Recommendation Generation
    │
    ├────────────► Domain Events
    │
    ├────────────► AI Explanation
    │
    ├────────────► Alert Pipeline
    │
    └────────────► Paper Trading
```

------------------------------------------------------------------------

# Stage 1: Market Data Acquisition

Responsibilities:

-   Retrieve quotes
-   Retrieve historical candles
-   Validate provider responses
-   Detect missing or invalid data

Output:

-   Normalized market data objects

------------------------------------------------------------------------

# Stage 2: Data Normalization

Responsibilities:

-   Standardize provider formats
-   Normalize timestamps
-   Convert provider-specific identifiers
-   Validate completeness

The remainder of the pipeline operates only on normalized domain
objects.

------------------------------------------------------------------------

# Stage 3: Indicator Calculation

Responsibilities:

-   Compute technical indicators
-   Cache reusable calculations
-   Validate calculation integrity

Examples:

-   Moving averages
-   RSI
-   MACD
-   ATR
-   Volume indicators

Indicator calculations remain deterministic.

------------------------------------------------------------------------

# Stage 4: Strategy Selection

Responsibilities:

-   Identify eligible strategies
-   Validate compatibility
-   Select strategy versions
-   Configure execution context

Strategies never retrieve data directly.

------------------------------------------------------------------------

# Stage 5: Strategy Execution

Responsibilities:

-   Evaluate market evidence
-   Produce structured findings
-   Return recommendation candidates
-   Supply supporting evidence

Each strategy executes independently.

------------------------------------------------------------------------

# Stage 6: Scoring Engine

Responsibilities:

-   Aggregate evidence
-   Weight signals
-   Produce normalized confidence scores
-   Record scoring explanations

Scoring remains deterministic and versioned.

------------------------------------------------------------------------

# Stage 7: Recommendation Generation

Responsibilities:

-   Create Recommendation domain objects
-   Record supporting evidence
-   Publish domain events
-   Persist recommendations

Recommendations become immutable records.

------------------------------------------------------------------------

# Downstream Consumers

After a recommendation is generated, downstream systems may:

-   Generate AI explanations
-   Deliver alerts
-   Execute paper trades
-   Produce analytics
-   Trigger background workflows

These consumers never modify the recommendation itself.

------------------------------------------------------------------------

# Design Principles

-   Every stage has one responsibility.
-   Pipeline stages are independently testable.
-   Intermediate outputs are explicit.
-   Deterministic processing is preserved throughout.
-   AI participates only after recommendation generation.

------------------------------------------------------------------------

# Related Documents

-   Request Lifecycle
-   ADR-003 Scoring Engine Architecture
-   ADR-004 AI Explanation Boundary
-   ADR-008 Strategy Plugin Architecture
-   ADR-014 Backtesting Architecture
-   ADR-015 Paper Trading Execution Model

------------------------------------------------------------------------

# Next Sections

-   Domain Model Overview
-   Persistence Model
-   Provider Architecture
