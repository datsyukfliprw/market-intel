# Blueprint v2 (Part 2): System Context & Bounded Contexts

**Project:** Project Market Intel

------------------------------------------------------------------------

# System Context

Project Market Intel sits at the center of several external systems
while protecting the Domain layer from implementation details.

``` text
             Market Data Providers
                     │
                     ▼
            Project Market Intel
          ┌──────────────────────┐
          │   Domain Core         │
          │ Recommendation Engine │
          └──────────────────────┘
           ▲     ▲      ▲      ▲
           │     │      │      │
      AI Providers  Users  Notifications  Storage
```

External systems communicate through infrastructure adapters and never
directly with domain logic.

------------------------------------------------------------------------

# Primary Actors

## Investors

Receive recommendations, alerts, paper trading results, and historical
analysis.

## Administrators

Manage providers, monitor system health, configure strategies, and
review operational metrics.

## External Providers

Supply market data, AI capabilities, notifications, and other
infrastructure services.

------------------------------------------------------------------------

# Bounded Contexts

## Market Data

Responsibilities:

-   Retrieve market information
-   Normalize provider responses
-   Validate incoming data
-   Publish domain-ready market objects

Owns:

-   Symbols
-   Quotes
-   Historical candles
-   Provider synchronization

------------------------------------------------------------------------

## Recommendation Engine

Responsibilities:

-   Execute strategies
-   Evaluate signals
-   Produce deterministic recommendations
-   Record supporting evidence

Owns:

-   Strategy execution
-   Scores
-   Recommendations

------------------------------------------------------------------------

## Strategy Management

Responsibilities:

-   Register strategies
-   Version strategies
-   Validate compatibility
-   Execute plugin lifecycle

Owns:

-   Strategy metadata
-   Plugin registration
-   Strategy capabilities

------------------------------------------------------------------------

## Portfolio Simulation

Responsibilities:

-   Execute paper trades
-   Track portfolios
-   Calculate returns
-   Maintain simulated positions

Owns:

-   Portfolios
-   Orders
-   Trades
-   Positions

------------------------------------------------------------------------

## Alerting

Responsibilities:

-   Create alerts
-   Apply user preferences
-   Dispatch notifications
-   Track delivery status

Owns:

-   Alert definitions
-   Delivery attempts
-   Notification channels

------------------------------------------------------------------------

## AI Explanation

Responsibilities:

-   Explain recommendations
-   Summarize evidence
-   Produce educational insights

Never owns business decisions.

------------------------------------------------------------------------

# Context Relationships

Market Data feeds the Recommendation Engine.

Recommendation Engine produces Recommendations.

Recommendations drive:

-   Alerting
-   AI Explanation
-   Paper Trading

Portfolio Simulation consumes Recommendations but never modifies them.

------------------------------------------------------------------------

# Boundary Rules

-   Each bounded context owns its own business concepts.
-   Communication occurs through well-defined interfaces.
-   Internal implementation details remain private.
-   Dependencies flow toward the Domain layer.

------------------------------------------------------------------------

# Next Sections

Upcoming Blueprint chapters:

-   Container Architecture
-   Component Architecture
-   Request Lifecycle
-   Recommendation Pipeline
-   Deployment Architecture
