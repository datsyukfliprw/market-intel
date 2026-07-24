# Architecture Review Checklist

**Project:** Project Market Intel

## Purpose

This checklist provides a consistent framework for reviewing pull
requests, architectural proposals, milestones, and major features. It
helps ensure every change aligns with the project's architectural
principles before it is merged.

------------------------------------------------------------------------

# 1. Domain Integrity

-   [ ] Does the change preserve Domain boundaries?
-   [ ] Is business logic located in the Domain rather than
    Infrastructure or Presentation?
-   [ ] Are new concepts expressed using the Domain Dictionary?
-   [ ] Are aggregate invariants maintained?

------------------------------------------------------------------------

# 2. Architecture

-   [ ] Does the implementation follow the Blueprint?
-   [ ] Are dependencies directed inward?
-   [ ] Are interfaces preferred over concrete implementations?
-   [ ] Does the change avoid unnecessary coupling?

------------------------------------------------------------------------

# 3. API Design

-   [ ] Are endpoints resource-oriented?
-   [ ] Are response formats consistent?
-   [ ] Are errors standardized?
-   [ ] Is versioning respected?

------------------------------------------------------------------------

# 4. Persistence

-   [ ] Are repositories responsible only for persistence?
-   [ ] Are transactions owned by the Application layer?
-   [ ] Are schema changes implemented through migrations?
-   [ ] Is historical data preserved appropriately?

------------------------------------------------------------------------

# 5. Security

-   [ ] Are secrets managed securely?
-   [ ] Are authentication and authorization handled correctly?
-   [ ] Is sensitive information excluded from logs?
-   [ ] Are inputs validated?

------------------------------------------------------------------------

# 6. Observability

-   [ ] Are logs structured?
-   [ ] Are important metrics emitted?
-   [ ] Are traces propagated?
-   [ ] Are health checks updated when necessary?

------------------------------------------------------------------------

# 7. Testing

-   [ ] Are unit tests included?
-   [ ] Are integration tests updated?
-   [ ] Has a regression test been added for bug fixes?
-   [ ] Do all CI quality gates pass?

------------------------------------------------------------------------

# 8. Operational Readiness

-   [ ] Is deployment documentation updated?
-   [ ] Are feature flags considered where appropriate?
-   [ ] Are rollback procedures understood?
-   [ ] Are monitoring and alerting impacts evaluated?

------------------------------------------------------------------------

# 9. Documentation

-   [ ] Are ADRs updated if architectural decisions changed?
-   [ ] Is the Blueprint still accurate?
-   [ ] Are API documents updated?
-   [ ] Is user-facing documentation affected?

------------------------------------------------------------------------

# Review Outcome

The reviewer should classify the change as:

-   Approved
-   Approved with Recommendations
-   Changes Requested
-   Blocked

Every review should include rationale for significant architectural
feedback.

------------------------------------------------------------------------

# Related Documents

-   Blueprint v2
-   Engineering Principles
-   Definition of Done
-   Contributor Guide
-   ADR Index
