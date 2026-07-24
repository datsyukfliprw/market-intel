# API Standards Guide

**Project:** Project Market Intel

## Purpose

This guide establishes the conventions for designing, implementing,
documenting, and evolving every API exposed by Project Market Intel. A
consistent API improves developer experience, simplifies integrations,
and reduces long-term maintenance.

------------------------------------------------------------------------

# Guiding Principles

-   APIs are resource-oriented.
-   Contracts are versioned.
-   Responses are predictable.
-   Errors are actionable.
-   Backward compatibility is preserved whenever practical.

------------------------------------------------------------------------

# URL Conventions

Use plural nouns for collections.

Examples:

-   `/api/v1/recommendations`
-   `/api/v1/scan-runs`
-   `/api/v1/alerts`
-   `/api/v1/paper-trades`

Avoid verbs in endpoint names.

------------------------------------------------------------------------

# HTTP Methods

-   `GET` - Retrieve resources
-   `POST` - Create resources
-   `PUT` - Replace resources
-   `PATCH` - Partial updates
-   `DELETE` - Remove resources

Methods should remain idempotent where defined by HTTP semantics.

------------------------------------------------------------------------

# Standard Response Format

Successful responses should include:

-   `data`
-   `meta`
-   `links` (when applicable)

Example:

``` json
{
  "data": {},
  "meta": {},
  "links": {}
}
```

------------------------------------------------------------------------

# Error Format

Errors should contain:

-   Error code
-   Human-readable message
-   Optional details
-   Correlation ID

Example:

``` json
{
  "error": {
    "code": "provider_timeout",
    "message": "Market data provider timed out.",
    "correlation_id": "..."
  }
}
```

------------------------------------------------------------------------

# Pagination

Collection endpoints should support:

-   `limit`
-   `offset` or cursor
-   Sorting
-   Filtering

Responses should include pagination metadata.

------------------------------------------------------------------------

# Versioning

-   Major versions appear in the URL (`/v1/`).
-   Breaking changes require a new major version.
-   Non-breaking additions may occur within the same version.

------------------------------------------------------------------------

# Authentication

Protected endpoints require authenticated requests.

Support may include:

-   OAuth 2.0 / OpenID Connect
-   API tokens
-   Service credentials

Authorization is enforced separately from authentication.

------------------------------------------------------------------------

# Idempotency

Creation endpoints supporting retries should accept idempotency keys to
prevent duplicate operations.

------------------------------------------------------------------------

# Documentation

Every endpoint should include:

-   Purpose
-   Request schema
-   Response schema
-   Error responses
-   Authentication requirements
-   Example requests and responses

OpenAPI should be the canonical API specification.

------------------------------------------------------------------------

# Related Documents

-   Blueprint v2 Part 13: Security Model
-   Blueprint v2 Part 15: Deployment Architecture
-   Contributor Guide
-   Engineering Principles
