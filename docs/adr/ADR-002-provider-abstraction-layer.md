# ADR-002: Provider Abstraction Layer

**ADR ID:** ADR-002

**Status:** Accepted

**Date:** 2026-07-24

------------------------------------------------------------------------

# Problem Statement

Project Market Intel depends on external services for market data, news,
AI, and notifications. These providers will evolve over time and may
need to be replaced.

Without a stable abstraction, business logic becomes tightly coupled to
vendor-specific APIs.

------------------------------------------------------------------------

# Decision

All third-party integrations will be implemented behind provider
interfaces.

The Domain and Application layers communicate only with provider
contracts, never with vendor SDKs or HTTP clients directly.

Concrete implementations belong exclusively to the Infrastructure layer.

------------------------------------------------------------------------

# Goals

-   Replace providers with minimal code changes
-   Simplify testing with mock implementations
-   Isolate vendor failures
-   Prevent vendor-specific logic from leaking into the domain

------------------------------------------------------------------------

# Provider Categories

-   Market Data
-   News
-   AI / LLM
-   Notifications
-   Authentication
-   Storage

Each category exposes a well-defined interface.

------------------------------------------------------------------------

# Rules

-   Providers never contain business rules.
-   Providers translate external models into domain models.
-   Providers may retry requests and handle transport concerns.
-   Providers must expose consistent error contracts.

------------------------------------------------------------------------

# Alternatives Considered

## Direct Vendor SDK Usage

Rejected due to high coupling.

## Shared Generic Wrapper

Rejected because different providers have different capabilities.

## Interface Per Capability

Accepted because it preserves flexibility while keeping dependencies
explicit.

------------------------------------------------------------------------

# Tradeoffs

## Benefits

-   Easier provider replacement
-   Better testing
-   Cleaner architecture
-   Reduced vendor lock-in

## Costs

-   Additional interfaces
-   More implementation files
-   Slight upfront complexity

------------------------------------------------------------------------

# Consequences

Future providers should require only a new Infrastructure implementation
while leaving Domain logic unchanged.

------------------------------------------------------------------------

# Related Documents

-   Blueprint
-   Architecture
-   Engineering Principles
-   ADR-001 Domain-First Architecture

------------------------------------------------------------------------

# Closing Statement

Infrastructure should adapt to the domain. The domain should never adapt
to infrastructure.
