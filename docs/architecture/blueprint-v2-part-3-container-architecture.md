# Blueprint v2 (Part 3): Container Architecture

**Project:** Project Market Intel

------------------------------------------------------------------------

# Purpose

This section defines the deployable containers that make up Project
Market Intel and the responsibilities assigned to each. Containers are
logical deployable units that communicate through stable interfaces
while preserving the Domain-First architecture.

------------------------------------------------------------------------

# Container Overview

``` text
                    +----------------------+
                    |   Web / Mobile UI    |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |      API Server      |
                    | Application Layer    |
                    +----------+-----------+
                               |
        +----------------------+----------------------+
        |                      |                      |
        v                      v                      v
+---------------+      +---------------+      +---------------+
| Background    |      | AI Adapter    |      | Alert Service |
| Workers       |      |               |      |               |
+-------+-------+      +-------+-------+      +-------+-------+
        |                      |                      |
        +----------+-----------+-----------+----------+
                   |                       |
                   v                       v
           +----------------------+   +------------------+
           |  Domain Core         |   | Persistence      |
           | Business Rules       |   | (Repositories)   |
           +----------+-----------+   +---------+--------+
                      |                         |
                      +------------+------------+
                                   |
                                   v
                           +---------------+
                           |   Database    |
                           +---------------+
```

------------------------------------------------------------------------

# Containers

## Presentation Container

Responsibilities:

-   Render user interface
-   Collect user input
-   Display recommendations
-   Visualize portfolios and analytics

Does not contain business rules.

------------------------------------------------------------------------

## API Server

Responsibilities:

-   Request validation
-   Authentication
-   Application orchestration
-   Transaction boundaries
-   DTO mapping

Communicates with the Domain through Application Services.

------------------------------------------------------------------------

## Domain Core

Responsibilities:

-   Business rules
-   Strategy execution
-   Recommendation generation
-   Portfolio logic
-   Domain events

This is the architectural center of the platform.

------------------------------------------------------------------------

## Background Workers

Responsibilities:

-   Market scans
-   AI explanation generation
-   Alert delivery
-   Backtesting
-   Maintenance jobs

Workers execute application workflows without exposing HTTP endpoints.

------------------------------------------------------------------------

## AI Adapter

Responsibilities:

-   Translate domain objects into AI prompts
-   Invoke AI providers
-   Parse responses
-   Return explanations

Never makes business decisions.

------------------------------------------------------------------------

## Alert Service

Responsibilities:

-   Dispatch notifications
-   Apply user delivery preferences
-   Retry failed deliveries
-   Record delivery status

------------------------------------------------------------------------

## Persistence Layer

Responsibilities:

-   Repository implementations
-   ORM mapping
-   Database transactions
-   Query optimization

The Domain never depends directly on persistence technology.

------------------------------------------------------------------------

# Communication Rules

-   Presentation communicates only with the API.
-   API communicates with Application Services.
-   Application Services coordinate Domain operations.
-   Infrastructure communicates outward to external systems.
-   Dependencies always point toward the Domain.

------------------------------------------------------------------------

# Deployment Evolution

Initial deployment may combine several containers into a single
application process.

As demand grows, containers may be deployed independently without
changing architectural boundaries.

------------------------------------------------------------------------

# Next Sections

-   Component Architecture
-   Request Lifecycle
-   Recommendation Pipeline
-   Deployment Architecture
