# Domain Dictionary

**Project:** Project Market Intel (Placeholder Name)

------------------------------------------------------------------------

# Purpose

The Domain Dictionary defines the business language of Project Market
Intel.

Every domain term has one authoritative meaning. If implementation and
this document disagree, implementation should be reviewed.

------------------------------------------------------------------------

# Template

Each domain includes:

-   Definition
-   Responsibilities
-   Does Not Own
-   Relationships
-   Lifecycle
-   Invariants
-   Future Evolution

------------------------------------------------------------------------

# Instrument

## Definition

A tradable financial asset known to the platform.

Examples include stocks, ETFs, ADRs, and future asset classes.

## Responsibilities

-   Identity
-   Symbol
-   Exchange
-   Metadata

## Does Not Own

-   Prices
-   Technical indicators
-   Recommendations

## Relationships

Owns zero or more:

-   Market Snapshots
-   Historical Bars
-   Recommendations

## Lifecycle

Created once. Rarely modified. Never deleted.

## Invariants

-   Unique symbol
-   Valid exchange
-   Stable identity

------------------------------------------------------------------------

# Market Snapshot

## Definition

A point-in-time observation of market data.

## Responsibilities

-   OHLC
-   Volume
-   Provider
-   Observation timestamp

## Does Not Own

-   Indicators
-   Scores
-   Recommendations

## Invariants

-   Immutable
-   Positive prices
-   Unique observation per provider/time

------------------------------------------------------------------------

# Historical Bar

## Definition

An immutable historical trading interval.

## Responsibilities

-   OHLC
-   Volume
-   Interval

## Invariants

-   Append-only
-   Never edited in place

------------------------------------------------------------------------

# Technical Snapshot

## Definition

A deterministic calculation derived from historical market data.

## Responsibilities

-   RSI
-   EMA
-   ATR
-   MACD
-   Other indicators

## Does Not Own

Raw market prices.

------------------------------------------------------------------------

# Fundamental Snapshot

## Definition

A point-in-time collection of company fundamentals.

Examples:

-   Market Cap
-   Revenue
-   EPS
-   P/E

------------------------------------------------------------------------

# Scan Run

## Definition

A single execution of a scanning strategy.

## Responsibilities

-   Execution metadata
-   Status
-   Produced candidates

## Lifecycle

PENDING → RUNNING → COMPLETED or FAILED

------------------------------------------------------------------------

# Scan Candidate

## Definition

A security identified during a Scan Run for further evaluation.

## Responsibilities

-   Instrument reference
-   Supporting evidence
-   Rank

------------------------------------------------------------------------

# Score Result

## Definition

The normalized quantitative score assigned to a candidate.

## Responsibilities

-   Component scores
-   Composite score
-   Version

------------------------------------------------------------------------

# Strategy

## Definition

A reusable set of rules used to evaluate market evidence.

Strategies evaluate.

They do not retrieve data.

------------------------------------------------------------------------

# Strategy Evaluation

## Definition

The recorded outcome of executing a Strategy.

Contains:

-   Rule outcomes
-   Supporting evidence
-   Final decision

------------------------------------------------------------------------

# Recommendation

## Definition

A historical recommendation produced from evidence.

Recommendations are immutable.

------------------------------------------------------------------------

# Recommendation Outcome

## Definition

The measured real-world performance of a Recommendation.

Purpose:

Evaluate system quality over time.

------------------------------------------------------------------------

# Alert

## Definition

A user notification generated from predefined conditions.

Alerts communicate.

They do not analyze.

------------------------------------------------------------------------

# Paper Position

## Definition

A simulated investment position used for paper trading.

Purpose:

Measure strategy performance without risking capital.

------------------------------------------------------------------------

# Provider

## Definition

An adapter responsible for communicating with external services.

Examples:

-   Market data provider
-   AI provider
-   News provider

Providers never contain business rules.

------------------------------------------------------------------------

# Closing Principle

Every business term in Project Market Intel shall have one and only one
authoritative definition.

New concepts should be added here before they become part of the
implementation.
