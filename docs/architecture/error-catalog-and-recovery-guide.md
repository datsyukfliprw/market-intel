# Error Catalog & Recovery Guide

**Project:** Project Market Intel

## Purpose

This guide defines the standard error taxonomy, recovery strategies,
logging expectations, and user-facing behavior for Project Market Intel.
It ensures errors are handled consistently across the platform and
provides operational guidance for diagnosing and resolving failures.

------------------------------------------------------------------------

# Error Handling Principles

-   Fail fast with clear diagnostics.
-   Preserve system integrity over partial success.
-   Classify errors consistently.
-   Separate user-facing messages from internal diagnostics.
-   Every recoverable failure has a documented recovery path.

------------------------------------------------------------------------

# Error Categories

## Domain Errors

Examples:

-   InvalidStrategyConfiguration
-   RecommendationInvariantViolation
-   PortfolioConstraintViolation

Characteristics:

-   Business rule violations
-   Never retried automatically
-   Returned as validation or domain failures

------------------------------------------------------------------------

## Application Errors

Examples:

-   MissingDependency
-   InvalidWorkflowState
-   TransactionFailed

Characteristics:

-   Workflow orchestration failures
-   May require operator investigation

------------------------------------------------------------------------

## Infrastructure Errors

Examples:

-   DatabaseUnavailable
-   QueueUnavailable
-   CacheUnavailable

Characteristics:

-   Usually transient
-   Eligible for retry according to policy

------------------------------------------------------------------------

## Provider Errors

Examples:

-   MarketDataTimeout
-   AIRateLimited
-   NotificationDeliveryFailed

Characteristics:

-   External dependency failures
-   Wrapped by provider adapters
-   Never exposed directly to the Domain

------------------------------------------------------------------------

# Severity Levels

-   INFO: Expected operational event
-   WARNING: Recoverable issue
-   ERROR: Request or job failure
-   CRITICAL: Immediate operational action required

Severity determines alerting behavior, not business importance.

------------------------------------------------------------------------

# Retry Policy

Automatically retry only transient failures:

-   Network interruption
-   Provider timeout
-   Temporary rate limit

Do not retry:

-   Validation failures
-   Authentication failures
-   Domain invariant violations

Use exponential backoff with configurable limits.

------------------------------------------------------------------------

# User-Facing Errors

Responses should include:

-   Friendly message
-   Stable error code
-   Correlation ID
-   Suggested next action (when applicable)

Internal implementation details must never be exposed.

------------------------------------------------------------------------

# Logging Requirements

Every error log should contain:

-   Timestamp (UTC)
-   Correlation ID
-   Error category
-   Severity
-   Service name
-   Operation
-   Stack trace (where appropriate)

Sensitive data must be redacted.

------------------------------------------------------------------------

# Recovery Procedures

  Category           Automatic Recovery         Manual Recovery
  ------------------ -------------------------- -----------------------------
  Provider Timeout   Retry                      Verify provider health
  Database Failure   Fail over (if available)   Restore service
  Queue Failure      Restart worker             Repair queue infrastructure
  Domain Error       None                       Correct business input

------------------------------------------------------------------------

# Related Documents

-   API Standards Guide
-   Infrastructure Runbook
-   Event Catalog
-   Blueprint Part 13: Security Model
-   Blueprint Part 14: Observability
