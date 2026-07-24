# Dependency Governance Guide

**Project:** Project Market Intel

## Purpose

This guide establishes the policies for evaluating, approving,
maintaining, updating, and retiring third-party dependencies. Its goal
is to minimize security risk, reduce technical debt, and ensure
long-term maintainability.

------------------------------------------------------------------------

# Governance Principles

-   Every dependency must provide measurable value.
-   Fewer dependencies are preferred.
-   Actively maintained projects are favored.
-   Security takes precedence over convenience.
-   Every dependency has an owner.

------------------------------------------------------------------------

# Dependency Categories

## Runtime Dependencies

Libraries required for production execution.

Examples: - FastAPI - SQLAlchemy - Pydantic - httpx

## Development Dependencies

Used only during development.

Examples: - pytest - mypy - Ruff - Pre-commit

## Infrastructure Dependencies

Services and tooling supporting deployments.

Examples: - PostgreSQL - Redis - Docker - GitHub Actions

------------------------------------------------------------------------

# Evaluation Criteria

Before introducing a dependency, evaluate:

-   Project maturity
-   Maintenance activity
-   Community adoption
-   Documentation quality
-   Security history
-   License compatibility
-   Performance impact
-   Alternatives considered

Every new dependency should be justified in the associated ADR or pull
request.

------------------------------------------------------------------------

# Versioning Policy

-   Prefer stable releases.
-   Pin direct dependencies.
-   Avoid floating major versions.
-   Upgrade regularly in planned maintenance windows.

Critical security updates take precedence over feature work.

------------------------------------------------------------------------

# Security Requirements

Dependencies must:

-   Be scanned for known vulnerabilities.
-   Come from trusted sources.
-   Avoid abandoned projects.
-   Minimize transitive dependency count.

High-risk vulnerabilities should be remediated immediately.

------------------------------------------------------------------------

# Licensing

Approved licenses include:

-   MIT
-   Apache-2.0
-   BSD

Licenses requiring source disclosure or imposing unacceptable commercial
restrictions require legal review.

------------------------------------------------------------------------

# Upgrade Process

1.  Review release notes.
2.  Evaluate breaking changes.
3.  Update dependency.
4.  Execute automated tests.
5.  Verify production behavior.
6.  Document significant changes.

------------------------------------------------------------------------

# Deprecation & Removal

Remove dependencies when:

-   No longer used.
-   Project is abandoned.
-   Security risk outweighs value.
-   Superior alternative exists.

Retirement should include migration guidance.

------------------------------------------------------------------------

# Ownership

Each dependency should identify:

-   Technical owner
-   Purpose
-   Date introduced
-   Current version
-   Upgrade cadence

------------------------------------------------------------------------

# Related Documents

-   Coding Standards Guide
-   Security Hardening Guide
-   Configuration Reference
-   Infrastructure Runbook
-   Engineering Principles
