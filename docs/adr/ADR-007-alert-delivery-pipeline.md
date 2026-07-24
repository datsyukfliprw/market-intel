# ADR-007: Alert Delivery Pipeline

**ADR ID:** ADR-007

**Status:** Accepted

**Date:** 2026-07-24

------------------------------------------------------------------------

# Problem Statement

Project Market Intel must notify users when meaningful market events
occur without delaying core business workflows. Alert delivery should
remain reliable, scalable, and independent of the recommendation engine.

------------------------------------------------------------------------

# Decision

Alert generation and alert delivery are separate responsibilities.

The Domain determines **that** an alert should exist.

Infrastructure determines **how** it is delivered.

------------------------------------------------------------------------

# Goals

-   Reliable notification delivery
-   Multiple notification channels
-   Minimal coupling
-   Retry support
-   User-configurable preferences

------------------------------------------------------------------------

# Alert Lifecycle

1.  Domain detects a qualifying condition.
2.  An Alert domain object is created.
3.  Delivery is requested.
4.  Infrastructure selects one or more channels.
5.  Delivery status is recorded.

------------------------------------------------------------------------

# Supported Channels

Initial:

-   In-app notifications
-   Email

Future:

-   SMS
-   Push notifications
-   Discord
-   Slack
-   Webhooks

------------------------------------------------------------------------

# Rules

-   Alert generation is deterministic.
-   Delivery failures never invalidate business transactions.
-   Delivery attempts are logged.
-   Duplicate alerts should be avoided when practical.
-   User preferences determine eligible channels.

------------------------------------------------------------------------

# Failure Handling

If delivery fails:

-   Record the failure.
-   Retry according to policy.
-   Escalate repeated failures.
-   Preserve the original alert.

------------------------------------------------------------------------

# Alternatives Considered

## Direct Notification Calls

Rejected because business workflows become coupled to delivery
infrastructure.

## Dedicated Alert Pipeline

Accepted because it separates business intent from communication
mechanics.

------------------------------------------------------------------------

# Tradeoffs

## Benefits

-   Easier channel expansion
-   Better reliability
-   Clear ownership boundaries
-   Independent scaling

## Costs

-   Additional orchestration
-   Delivery tracking infrastructure

------------------------------------------------------------------------

# Future Evolution

Alert delivery may migrate to background workers and event-driven
processing without changing domain behavior.

------------------------------------------------------------------------

# Related Documents

-   Blueprint
-   Architecture
-   ADR-002 Provider Abstraction Layer
-   ADR-005 Event Processing Strategy
-   ADR-006 Persistence Strategy

------------------------------------------------------------------------

# Closing Statement

The business decides **when** users should be informed. Infrastructure
decides **how** that information reaches them.
