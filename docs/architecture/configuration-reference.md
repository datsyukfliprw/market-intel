# Configuration Reference

**Project:** Project Market Intel

## Purpose

This document is the authoritative reference for all runtime
configuration within Project Market Intel. It defines configuration
sources, naming conventions, ownership, defaults, validation, and
operational guidance.

------------------------------------------------------------------------

# Configuration Principles

-   Configuration belongs outside application code.
-   Sensible defaults are provided where appropriate.
-   Secrets are never committed to source control.
-   Every configuration option is documented.
-   Invalid configuration prevents application startup.

------------------------------------------------------------------------

# Configuration Sources (Highest to Lowest Priority)

1.  Environment variables
2.  Secret manager / deployment platform
3.  Environment-specific configuration files
4.  Application defaults

------------------------------------------------------------------------

# Environment Variable Naming

Use uppercase snake case.

Examples:

-   DATABASE_URL
-   OPENAI_API_KEY
-   ALPACA_API_KEY
-   REDIS_URL
-   LOG_LEVEL
-   APP_ENVIRONMENT

Group related variables using prefixes where practical.

------------------------------------------------------------------------

# Application Settings

## Runtime

-   APP_ENVIRONMENT
-   APP_NAME
-   APP_VERSION
-   LOG_LEVEL

## Database

-   DATABASE_URL
-   DATABASE_POOL_SIZE
-   DATABASE_TIMEOUT

## Cache

-   REDIS_URL
-   CACHE_TTL_SECONDS

## Background Jobs

-   JOB_POLL_INTERVAL_SECONDS
-   MAX_CONCURRENT_JOBS
-   RETRY_LIMIT

## AI Providers

-   OPENAI_API_KEY
-   AI_MODEL
-   AI_TIMEOUT_SECONDS
-   AI_MAX_TOKENS

## Market Data Providers

-   POLYGON_API_KEY
-   FINNHUB_API_KEY
-   ALPACA_API_KEY

------------------------------------------------------------------------

# Feature Flags

Feature flags enable controlled rollout without redeployment.

Examples:

-   ENABLE_PAPER_TRADING
-   ENABLE_AI_EXPLANATIONS
-   ENABLE_EXPERIMENTAL_STRATEGIES

Flags should default to disabled unless explicitly approved.

------------------------------------------------------------------------

# Validation Rules

At startup:

-   Required values must exist.
-   Numeric ranges are validated.
-   URLs are validated.
-   Enum values are checked.
-   Secrets are never logged.

------------------------------------------------------------------------

# Secret Management

Secrets include:

-   API keys
-   Tokens
-   Passwords
-   Certificates

Guidelines:

-   Store in a secrets manager when available.
-   Rotate periodically.
-   Never expose through logs or metrics.

------------------------------------------------------------------------

# Environment Profiles

Supported profiles:

-   Development
-   Testing
-   Staging
-   Production

Each profile should minimize configuration drift.

------------------------------------------------------------------------

# Change Management

Configuration changes should:

1.  Be reviewed.
2.  Be documented.
3.  Be version controlled where applicable.
4.  Include rollback instructions.

------------------------------------------------------------------------

# Related Documents

-   Infrastructure Runbook
-   Security Guide
-   Deployment Architecture
-   Blueprint Part 15: Deployment
