# Glossary & Ubiquitous Language Reference

**Project:** Project Market Intel

## Purpose

This reference defines the canonical vocabulary for Project Market
Intel. Every contributor, architect, AI coding agent, API, and document
should use these terms consistently to reduce ambiguity and maintain a
shared understanding of the system.

------------------------------------------------------------------------

# Guiding Principles

-   One concept has one preferred name.
-   Business terms take precedence over technical jargon.
-   Definitions evolve through ADRs and architecture reviews.
-   Avoid synonyms for established domain concepts.

------------------------------------------------------------------------

# Core Business Terms

## Recommendation

A persisted investment insight produced by the Recommendation Pipeline
after strategy execution and scoring.

## Scan Run

A single execution of the market scanning process.

## Strategy

A deterministic algorithm that evaluates normalized market data and
produces recommendation candidates.

## Strategy Plugin

A deployable implementation of the Strategy contract that can be
discovered and executed without modifying the core engine.

## Confidence Score

A normalized measure describing the strength of a recommendation
according to the Scoring Engine.

------------------------------------------------------------------------

# Domain Concepts

## Aggregate

A consistency boundary that protects related business rules.

## Entity

An object defined primarily by its identity over time.

## Value Object

An immutable object defined entirely by its values.

## Domain Event

A record of a completed business fact.

## Repository

An abstraction responsible for loading and persisting aggregates.

------------------------------------------------------------------------

# Application Concepts

## Application Service

Coordinates workflows, transactions, repositories, and external services
without containing core business rules.

## Provider Adapter

Translates external APIs into canonical domain models.

## AI Context Builder

Constructs structured inputs for AI providers using immutable domain
data.

------------------------------------------------------------------------

# Operational Terms

## Health Check

A diagnostic endpoint reporting runtime readiness or liveness.

## Background Worker

A process that executes asynchronous jobs independently of user
requests.

## Correlation ID

A unique identifier used to trace a request across components.

## Feature Flag

A runtime-controlled switch used to enable or disable functionality.

------------------------------------------------------------------------

# Documentation Terms

## Blueprint

The primary architectural handbook describing the system's design.

## ADR

Architecture Decision Record documenting significant technical
decisions.

## Runbook

Operational procedures for deploying and maintaining the platform.

## Companion Handbook

A specialized document expanding on a specific architectural topic.

------------------------------------------------------------------------

# Governance

When introducing new terminology:

1.  Verify the concept does not already exist.
2.  Prefer extending existing vocabulary.
3.  Update this glossary.
4.  Update affected documentation and ADRs.

------------------------------------------------------------------------

# Related Documents

-   Domain Dictionary
-   Blueprint v2
-   Architecture Decision Records
-   Engineering Principles
-   Architecture Review Checklist
