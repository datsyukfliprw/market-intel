# Coding Standards Guide

**Project:** Project Market Intel

## Purpose

This guide defines the coding conventions for Project Market Intel. It
ensures consistency across contributors, AI coding agents, and future
maintainers while reinforcing the architectural principles documented
throughout the project.

------------------------------------------------------------------------

# Core Principles

-   Readability over cleverness.
-   Consistency over personal preference.
-   Explicit is better than implicit.
-   Favor composition over inheritance.
-   Keep business logic inside the Domain.

------------------------------------------------------------------------

# Project Structure

Each module should have a single, well-defined responsibility.

Recommended layers:

-   Presentation
-   Application
-   Domain
-   Infrastructure

Dependencies always point inward.

------------------------------------------------------------------------

# Naming Conventions

Classes: - PascalCase

Functions and variables: - snake_case (Python)

Constants: - UPPER_SNAKE_CASE

Interfaces should describe capabilities rather than implementations.

Examples:

-   RecommendationRepository
-   MarketDataProvider
-   StrategyExecutor

------------------------------------------------------------------------

# Function Design

Functions should:

-   Do one thing well.
-   Remain small and cohesive.
-   Return explicit values.
-   Avoid hidden side effects.

Prefer dependency injection over global state.

------------------------------------------------------------------------

# Error Handling

-   Raise domain-specific exceptions where appropriate.
-   Never silently ignore errors.
-   Log operational failures once.
-   Convert infrastructure errors into application-friendly exceptions.

------------------------------------------------------------------------

# Logging

Logs should be:

-   Structured
-   Actionable
-   Correlated with request IDs
-   Free of secrets and sensitive information

Business events belong in the Domain; operational logs belong in
Infrastructure.

------------------------------------------------------------------------

# Testing Expectations

Every production feature should include:

-   Unit tests
-   Integration tests when applicable
-   Regression tests for resolved defects

Tests should be deterministic and independent.

------------------------------------------------------------------------

# Documentation

Public modules, APIs, and complex algorithms should include concise
documentation explaining intent, assumptions, and constraints.

Architectural changes require corresponding updates to:

-   Blueprint
-   ADRs
-   Relevant handbooks

------------------------------------------------------------------------

# Code Review Checklist

Review for:

-   Architectural alignment
-   Simplicity
-   Naming consistency
-   Test coverage
-   Security implications
-   Documentation updates

------------------------------------------------------------------------

# Related Documents

-   Engineering Principles
-   Contributor Guide
-   Architecture Review Checklist
-   Blueprint v2
