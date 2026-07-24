# ADR-015: Paper Trading Execution Model

**ADR ID:** ADR-015

**Status:** Accepted

**Date:** 2026-07-24

------------------------------------------------------------------------

# Problem Statement

Project Market Intel requires a realistic environment for validating
recommendations under live market conditions without risking real
capital. The paper trading system must simulate order execution,
portfolio management, and performance tracking while remaining isolated
from future brokerage integrations.

------------------------------------------------------------------------

# Decision

Paper trading will be implemented as an independent execution model that
consumes validated recommendations and simulates market activity using
configurable execution rules.

The paper trading subsystem shares domain models with production but
maintains its own execution context and portfolio state.

------------------------------------------------------------------------

# Goals

-   Validate recommendations in real market conditions
-   Simulate realistic order execution
-   Measure strategy performance over time
-   Preserve complete trading history
-   Remain independent of brokerage APIs

------------------------------------------------------------------------

# Architectural Principles

-   Recommendations are inputs, not guarantees.
-   Portfolios are isolated per user or simulation.
-   Every order has a complete lifecycle.
-   Trades are immutable once executed.
-   Portfolio valuation is deterministic from recorded events.

------------------------------------------------------------------------

# Order Lifecycle

1.  Recommendation generated.
2.  User or automation submits paper order.
3.  Order validated.
4.  Fill simulated using execution rules.
5.  Portfolio updated.
6.  Trade recorded.
7.  Performance metrics recalculated.

------------------------------------------------------------------------

# Execution Model

Execution should support configurable assumptions, including:

-   Market orders
-   Limit orders
-   Partial fills (future)
-   Slippage models
-   Transaction costs
-   Market hours validation

Execution rules must be deterministic for identical inputs.

------------------------------------------------------------------------

# Portfolio Management

Each portfolio maintains:

-   Cash balance
-   Open positions
-   Closed positions
-   Unrealized gains/losses
-   Realized gains/losses
-   Transaction history
-   Equity curve

Portfolio calculations derive from recorded trade events rather than
mutable state whenever practical.

------------------------------------------------------------------------

# Performance Metrics

Examples include:

-   Total return
-   Daily return
-   Win rate
-   Maximum drawdown
-   Sharpe ratio
-   Profit factor
-   Average holding period

------------------------------------------------------------------------

# Alternatives Considered

## Integrate with Live Brokerage Immediately

Rejected because strategy validation should occur before real capital is
involved.

## Dedicated Paper Trading Engine

Accepted because it enables safe experimentation, reproducible
evaluation, and future brokerage integration.

------------------------------------------------------------------------

# Tradeoffs

## Benefits

-   Risk-free strategy validation
-   Realistic execution simulation
-   Consistent performance measurement
-   Strong architectural separation

## Costs

-   Additional simulation complexity
-   Ongoing maintenance of execution models

------------------------------------------------------------------------

# Future Evolution

Future enhancements may include:

-   Multi-portfolio support
-   Margin simulation
-   Options and derivatives
-   Corporate action handling
-   Live brokerage adapters
-   Portfolio comparison dashboards

------------------------------------------------------------------------

# Related Documents

-   Blueprint
-   Architecture
-   ADR-003 Scoring Engine Architecture
-   ADR-005 Event Processing Strategy
-   ADR-006 Persistence Strategy
-   ADR-014 Backtesting Architecture

------------------------------------------------------------------------

# Closing Statement

Paper trading bridges the gap between historical validation and
real-world execution, allowing strategies to prove themselves before
capital is ever placed at risk.
