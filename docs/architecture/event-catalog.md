# Event Catalog

**Project:** Project Market Intel

## Purpose

This catalog defines every significant event produced and consumed
within Project Market Intel. It provides a shared contract for
asynchronous workflows, auditability, and future distributed services.

------------------------------------------------------------------------

# Event Design Principles

-   Events describe facts that have already occurred.
-   Event names use the past tense.
-   Events are immutable once published.
-   Consumers are loosely coupled to producers.
-   Every event is versioned.

------------------------------------------------------------------------

# Standard Event Envelope

Every event should include:

-   Event ID
-   Event type
-   Event version
-   Occurred timestamp (UTC)
-   Correlation ID
-   Causation ID
-   Producer
-   Payload

------------------------------------------------------------------------

# Domain Events

## RecommendationPublished

Producer: - Recommendation Service

Consumers: - Alert Service - AI Explanation Service - Analytics

Purpose: Signals that a recommendation is complete and available.

------------------------------------------------------------------------

## ScanCompleted

Producer: - Scan Service

Consumers: - Recommendation Pipeline - Metrics - Audit Logging

Purpose: Indicates a market scan has finished.

------------------------------------------------------------------------

## PaperTradeExecuted

Producer: - Paper Trading Service

Consumers: - Portfolio Service - Analytics

Purpose: Records a simulated trade execution.

------------------------------------------------------------------------

## AlertTriggered

Producer: - Alert Service

Consumers: - Notification Service - Audit Log

Purpose: Represents a user notification request.

------------------------------------------------------------------------

# Integration Events

Examples:

-   ProviderHealthChanged
-   AIExplanationGenerated
-   NotificationDelivered
-   NotificationFailed

Integration events communicate with external systems while remaining
separate from domain events.

------------------------------------------------------------------------

# Versioning

Rules:

-   Additive payload changes increment the minor version.
-   Breaking changes require a new major version.
-   Consumers should tolerate unknown fields where practical.

------------------------------------------------------------------------

# Delivery Guarantees

-   At-least-once delivery by default.
-   Consumers must be idempotent.
-   Ordering is guaranteed only within a single aggregate when
    supported.

------------------------------------------------------------------------

# Related Documents

-   Blueprint Part 12: Background Jobs & Scheduling
-   Sequence Diagram Handbook
-   Data Flow Handbook
-   ADR-007 Alert Delivery
