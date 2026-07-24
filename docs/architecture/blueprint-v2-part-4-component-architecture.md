# Blueprint v2 (Part 4): Component Architecture

**Project:** Project Market Intel

------------------------------------------------------------------------

# Purpose

This section decomposes each architectural container into its major
internal components and defines the allowed dependencies between them.
Components should have a single, well-defined responsibility and
communicate only through stable interfaces.

------------------------------------------------------------------------

# API Server Components

## API Controllers

Responsibilities:

-   Receive HTTP requests
-   Validate request structure
-   Return HTTP responses
-   Map DTOs to application requests

Controllers contain no business logic.

### Application Services

Responsibilities:

-   Coordinate use cases
-   Manage transactions
-   Publish domain events
-   Call repositories through interfaces

------------------------------------------------------------------------

# Domain Core Components

## Recommendation Engine

Produces deterministic recommendations from validated market data.

## Strategy Engine

Discovers, validates, and executes strategy plugins.

## Scoring Engine

Aggregates evidence into normalized scores.

## Portfolio Engine

Maintains paper trading portfolios and position calculations.

## Domain Event Publisher

Emits business events without knowing how they are consumed.

------------------------------------------------------------------------

# Infrastructure Components

## Repository Implementations

Translate between domain models and persistence models.

## Provider Adapters

Communicate with:

-   Market data providers
-   AI providers
-   Notification providers

## Scheduler

Starts recurring application workflows.

## Worker Executor

Runs asynchronous jobs and background tasks.

------------------------------------------------------------------------

# Presentation Components

-   Dashboard
-   Scanner
-   Recommendation Viewer
-   Portfolio Viewer
-   Alert Center
-   Administration

Presentation components communicate only with public API endpoints.

------------------------------------------------------------------------

# Dependency Rules

Allowed:

Presentation → API

API → Application

Application → Domain

Infrastructure → External Systems

Repositories → Database

Forbidden:

-   Presentation → Database
-   Domain → Infrastructure
-   Domain → HTTP
-   Domain → ORM
-   Domain → AI Provider
-   Domain → Notification Provider

------------------------------------------------------------------------

# Component Diagram

``` text
Presentation
      │
      ▼
API Controllers
      │
      ▼
Application Services
      │
      ▼
+-------------------------------+
| Recommendation Engine         |
| Strategy Engine               |
| Scoring Engine                |
| Portfolio Engine              |
| Domain Events                 |
+-------------------------------+
      │
      ▼
Repositories / Provider Adapters
      │
      ▼
Infrastructure
```

------------------------------------------------------------------------

# Design Principles

-   Single responsibility
-   Explicit dependencies
-   Stable interfaces
-   Replaceable implementations
-   High cohesion
-   Low coupling

------------------------------------------------------------------------

# Next Sections

-   Request Lifecycle
-   Recommendation Pipeline
-   Domain Model Overview
-   Persistence Model
