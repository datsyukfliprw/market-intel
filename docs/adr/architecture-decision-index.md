# Architecture Decision Index

**Project:** Project Market Intel\
**Last Updated:** 2026-07-24

------------------------------------------------------------------------

## Purpose

This index provides a single entry point for all Architectural Decision
Records (ADRs). Each ADR captures a significant architectural decision,
its rationale, and its impact on the system.

------------------------------------------------------------------------

  -------------------------------------------------------------------------
  ADR          Title             Status              Summary
  ------------ ----------------- ------------------- ----------------------
  ADR-001      Domain-First      Accepted            The Domain layer is
               Architecture                          the center of the
                                                     architecture.

  ADR-002      Provider          Accepted            External services are
               Abstraction Layer                     accessed through
                                                     abstractions.

  ADR-003      Scoring Engine    Accepted            Scoring is modular,
               Architecture                          deterministic, and
                                                     versioned.

  ADR-004      AI Explanation    Accepted            AI explains decisions
               Boundary                              but never makes them.

  ADR-005      Event Processing  Accepted            Synchronous-first
               Strategy                              architecture with
                                                     event evolution.

  ADR-006      Persistence       Accepted            Repository pattern
               Strategy                              isolates storage from
                                                     business logic.

  ADR-007      Alert Delivery    Accepted            Alert creation is
               Pipeline                              separated from
                                                     delivery mechanisms.

  ADR-008      Strategy Plugin   Accepted            Strategies are
               Architecture                          independent plugins
                                                     behind a common
                                                     interface.

  ADR-009      Configuration &   Accepted            Configuration and
               Feature Flag                          feature flags are
               Strategy                              centralized.

  ADR-010      Observability     Accepted            Logging, metrics,
                                                     tracing, and health
                                                     checks are first-class
                                                     capabilities.

  ADR-011      Security          Accepted            Secure-by-default
               Architecture                          principles apply
                                                     across all layers.

  ADR-012      API Versioning    Accepted            Public APIs evolve
               Strategy                              through explicit
                                                     versioning.

  ADR-013      Scheduling &      Accepted            Scheduling, execution,
               Background Jobs                       and business logic are
                                                     separated.

  ADR-014      Backtesting       Accepted            Historical simulation
               Architecture                          is deterministic and
                                                     isolated.

  ADR-015      Paper Trading     Accepted            Paper trading
               Execution Model                       validates
                                                     recommendations
                                                     without risking
                                                     capital.
  -------------------------------------------------------------------------

------------------------------------------------------------------------

## Reading Order

1.  ADR-001 through ADR-003 establish the architectural foundation.
2.  ADR-004 through ADR-010 define cross-cutting capabilities.
3.  ADR-011 through ADR-013 define platform-wide operational policies.
4.  ADR-014 and ADR-015 define validation and simulated execution.

------------------------------------------------------------------------

## Maintenance

When a significant architectural decision is made:

1.  Create a new ADR.
2.  Assign the next sequential number.
3.  Update this index.
4.  Cross-reference related ADRs where appropriate.

------------------------------------------------------------------------

## Closing Statement

This index is the authoritative catalog of architectural decisions for
Project Market Intel and should remain synchronized with the contents of
the `docs/adr/` directory.
