# Blueprint v2 (Part 7): Domain Model Overview

**Project:** Project Market Intel

------------------------------------------------------------------------

# Purpose

The Domain Model defines the business concepts at the heart of Project
Market Intel. It establishes the ubiquitous language used throughout the
codebase and documentation while remaining independent of frameworks,
databases, and external services.

------------------------------------------------------------------------

# Domain Design Principles

-   Business rules live in the Domain.
-   Domain objects are persistence-agnostic.
-   Entities model identity over time.
-   Value Objects model immutable concepts.
-   Aggregates protect consistency boundaries.
-   Repositories abstract persistence.

------------------------------------------------------------------------

# Core Aggregates

## Recommendation

Owns:

-   Recommendation ID
-   Strategy Version
-   Confidence Score
-   Supporting Evidence
-   Recommendation Status

Invariant:

A published recommendation is immutable.

------------------------------------------------------------------------

## Portfolio

Owns:

-   Cash Balance
-   Open Positions
-   Closed Positions
-   Trade History

Invariant:

Portfolio value is derived from recorded events.

------------------------------------------------------------------------

## Strategy

Owns:

-   Strategy Metadata
-   Version
-   Configuration
-   Supported Asset Classes

Invariant:

A strategy executes deterministically for identical inputs.

------------------------------------------------------------------------

# Entities

Examples:

-   Recommendation
-   Portfolio
-   Position
-   Order
-   Trade
-   Scan Run
-   Alert

Entities have stable identity.

------------------------------------------------------------------------

# Value Objects

Examples:

-   Symbol
-   Money
-   Price
-   Quantity
-   Time Range
-   Confidence Score
-   Risk Rating

Value Objects are immutable and compared by value.

------------------------------------------------------------------------

# Domain Services

Major services include:

-   Recommendation Service
-   Strategy Executor
-   Scoring Service
-   Portfolio Valuation Service
-   Risk Evaluation Service

Domain services encapsulate business logic that does not naturally
belong to a single entity.

------------------------------------------------------------------------

# Repository Interfaces

Repository contracts include:

-   RecommendationRepository
-   PortfolioRepository
-   StrategyRepository
-   ScanRunRepository
-   AlertRepository

Only interfaces exist in the Domain.

------------------------------------------------------------------------

# Domain Events

Representative events:

-   RecommendationCreated
-   ScanCompleted
-   AlertTriggered
-   OrderExecuted
-   PortfolioUpdated

Events describe completed business facts.

------------------------------------------------------------------------

# Dependency Rules

The Domain depends on:

-   Nothing external

Everything else depends on the Domain.

------------------------------------------------------------------------

# Related Documents

-   Domain Dictionary
-   Component Architecture
-   ADR-001 Domain-First Architecture
-   ADR-003 Scoring Engine Architecture
-   ADR-006 Persistence Strategy

------------------------------------------------------------------------

# Next Sections

-   Persistence Model
-   Provider Architecture
-   AI Integration
