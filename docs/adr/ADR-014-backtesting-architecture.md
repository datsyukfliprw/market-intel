# ADR-014: Backtesting Architecture

**ADR ID:** ADR-014

**Status:** Accepted

**Date:** 2026-07-24

------------------------------------------------------------------------

# Problem Statement

Trading strategies should be validated against historical market data
before they are trusted in paper trading or future live execution. The
backtesting system must produce deterministic, repeatable results while
remaining independent from production recommendation workflows.

------------------------------------------------------------------------

# Decision

Backtesting is implemented as a dedicated architectural capability with
clear separation between historical data retrieval, strategy execution,
simulation, and reporting.

Production recommendation services are not reused as the execution
engine for historical simulations.

------------------------------------------------------------------------

# Goals

-   Deterministic replay
-   Repeatable results
-   Comparable strategy versions
-   Performance measurement
-   Separation from production workflows

------------------------------------------------------------------------

# Architectural Principles

-   Historical data is immutable.
-   Strategy code is shared between production and backtesting.
-   Execution context differs from production.
-   Every backtest is versioned.
-   Results are reproducible given identical inputs.

------------------------------------------------------------------------

# Backtesting Pipeline

1.  Select strategy and version.
2.  Load historical market data.
3.  Execute strategy over the selected period.
4.  Simulate order execution.
5.  Calculate performance metrics.
6.  Persist results.
7.  Generate reports.

------------------------------------------------------------------------

# Performance Metrics

Examples include:

-   Total return
-   Win rate
-   Maximum drawdown
-   Sharpe ratio
-   Profit factor
-   Average trade duration

Metrics should be extensible without changing the core execution engine.

------------------------------------------------------------------------

# Reliability Rules

-   Historical datasets are never modified during execution.
-   Strategy inputs are recorded.
-   Randomness is avoided or explicitly seeded.
-   Results include software and strategy versions.

------------------------------------------------------------------------

# Alternatives Considered

## Integrate Backtesting into Production Services

Rejected because production concerns and historical simulation have
different requirements.

## Dedicated Backtesting Architecture

Accepted because it improves reproducibility, testing, and future
scalability.

------------------------------------------------------------------------

# Tradeoffs

## Benefits

-   Trustworthy strategy evaluation
-   Easier regression testing
-   Independent scaling
-   Cleaner architecture

## Costs

-   Additional execution infrastructure
-   Historical data storage requirements

------------------------------------------------------------------------

# Future Evolution

Future enhancements may include:

-   Distributed backtesting
-   Parameter optimization
-   Walk-forward analysis
-   Monte Carlo simulation
-   Portfolio-level simulations

------------------------------------------------------------------------

# Related Documents

-   Blueprint
-   Architecture
-   ADR-003 Scoring Engine Architecture
-   ADR-005 Event Processing Strategy
-   ADR-008 Strategy Plugin Architecture
-   ADR-013 Scheduling & Background Jobs

------------------------------------------------------------------------

# Closing Statement

Backtesting exists to answer one question: "Would this strategy have
behaved as expected?" The architecture should ensure that answer is
trustworthy and reproducible.
