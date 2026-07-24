# ADR-013: Scheduling & Background Jobs

**ADR ID:** ADR-013

**Status:** Accepted

**Date:** 2026-07-24

------------------------------------------------------------------------

# Problem Statement

Project Market Intel performs recurring and long-running operations such
as market scans, data synchronization, alert delivery, AI explanation
generation, and maintenance tasks. These workloads should not block
interactive user requests or tightly couple execution timing to business
logic.

------------------------------------------------------------------------

# Decision

The platform will separate **job scheduling**, **job execution**, and
**business logic** into distinct architectural responsibilities.

Business services remain unaware of when or how jobs are scheduled.

------------------------------------------------------------------------

# Goals

-   Support recurring and on-demand execution
-   Prevent long-running work from blocking API requests
-   Enable horizontal scaling of workers
-   Ensure reliable retries
-   Keep scheduling independent of domain logic

------------------------------------------------------------------------

# Architectural Principles

-   Schedulers trigger jobs.
-   Workers execute jobs.
-   Application services orchestrate business workflows.
-   Domain services contain business rules.
-   Jobs are stateless whenever practical.

------------------------------------------------------------------------

# Job Categories

Recurring jobs:

-   Market scans
-   Provider synchronization
-   Data cleanup
-   Indicator precomputation
-   Health verification

Triggered jobs:

-   AI explanation generation
-   Alert delivery
-   Report generation
-   Backtesting requests
-   Portfolio recalculation

------------------------------------------------------------------------

# Reliability Rules

-   Jobs must be idempotent whenever possible.
-   Failures are logged with correlation IDs.
-   Retries use configurable policies.
-   Permanent failures are surfaced for operator review.
-   Jobs should support graceful cancellation when appropriate.

------------------------------------------------------------------------

# Alternatives Considered

## Synchronous Execution

Rejected because it reduces responsiveness and limits scalability.

## Dedicated Scheduling & Worker Architecture

Accepted because it separates timing concerns from business logic and
supports future growth.

------------------------------------------------------------------------

# Tradeoffs

## Benefits

-   Improved responsiveness
-   Independent scaling
-   Better fault isolation
-   Predictable scheduling

## Costs

-   Additional operational components
-   Queue and worker management
-   More deployment complexity

------------------------------------------------------------------------

# Future Evolution

Future enhancements may include:

-   Distributed job queues
-   Priority scheduling
-   Workflow orchestration
-   Scheduled dependency graphs
-   Multi-region worker execution

------------------------------------------------------------------------

# Related Documents

-   Blueprint
-   Architecture
-   ADR-005 Event Processing Strategy
-   ADR-006 Persistence Strategy
-   ADR-010 Observability (Logging, Metrics & Tracing)
-   ADR-012 API Versioning Strategy

------------------------------------------------------------------------

# Closing Statement

Scheduling determines **when** work begins. Workers determine **where**
it runs. The domain determines **what** work is performed.
