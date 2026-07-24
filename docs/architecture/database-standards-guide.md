# Database Standards Guide

**Project:** Project Market Intel

## Purpose

This guide establishes standards for database design, schema evolution,
data integrity, and long-term maintainability. It ensures persistence
decisions remain consistent with the architectural principles defined in
the Blueprint and ADRs.

------------------------------------------------------------------------

# Guiding Principles

-   The database supports the Domain, not the reverse.
-   Schema changes are intentional and versioned.
-   Data integrity is preferred over convenience.
-   Normalize by default; denormalize only with measured justification.
-   Every table has a clear ownership boundary.

------------------------------------------------------------------------

# Naming Conventions

Tables: - `snake_case` - Plural nouns where appropriate

Columns: - `snake_case` - Descriptive, unambiguous names

Primary keys: - `id`

Foreign keys: - `<referenced_entity>_id`

Indexes: - `idx_<table>_<column>` - `uq_<table>_<column>` -
`fk_<table>_<column>`

------------------------------------------------------------------------

# Schema Design

Tables should include:

-   Primary key
-   Creation timestamp
-   Update timestamp (when applicable)

Avoid duplicated business data unless justified by performance.

------------------------------------------------------------------------

# Migrations

Requirements:

-   Every schema change uses a migration.
-   Migrations are committed to source control.
-   Migrations are repeatable.
-   Rollback strategy is documented when practical.

Never modify historical migrations after release.

------------------------------------------------------------------------

# Constraints

Use database constraints to enforce:

-   Primary keys
-   Foreign keys
-   Uniqueness
-   Required values
-   Check constraints where appropriate

Business rules remain in the Domain layer.

------------------------------------------------------------------------

# Transactions

-   Transactions are owned by the Application layer.
-   Keep transactions short.
-   Avoid long-running locks.
-   Maintain aggregate consistency.

------------------------------------------------------------------------

# Indexing

Create indexes based on measured query patterns.

Review periodically for:

-   Unused indexes
-   Duplicate indexes
-   Missing indexes
-   Write amplification

------------------------------------------------------------------------

# Auditing & Retention

Persist audit-worthy events for:

-   Configuration changes
-   Administrative actions
-   Strategy versions
-   Recommendation history

Retention policies should balance operational needs with storage costs.

------------------------------------------------------------------------

# Archival

Archive historical data when it is:

-   Rarely queried
-   Large in volume
-   No longer operationally active

Archived data must remain recoverable.

------------------------------------------------------------------------

# Related Documents

-   Blueprint Part 8: Persistence Model
-   Performance & Capacity Planning Guide
-   Infrastructure Runbook
-   ADR-006 Persistence Strategy
