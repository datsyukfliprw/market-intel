# Architecture Index & Cross-Reference

**Project:** Project Market Intel

## Purpose

This document serves as the primary navigation hub for all architecture,
governance, operational, and engineering documentation. It helps
contributors quickly locate authoritative information and prevents
duplicate documentation.

------------------------------------------------------------------------

# Core Architecture

  Document                    Purpose
  --------------------------- ---------------------------------
  README                      Project overview and onboarding
  architecture.md             High-level architecture summary
  blueprint.md                Canonical system architecture
  domain_dictionary.md        Domain terminology
  engineering_principles.md   Engineering philosophy

------------------------------------------------------------------------

# Milestones

  Document                     Purpose
  ---------------------------- ---------------------------
  milestone-spec-template.md   Standard milestone format
  MS-001 Backend Foundation    Backend initialization

------------------------------------------------------------------------

# Architecture Decision Records

ADR-001 through ADR-015 document major architectural decisions.

See: - architecture-decision-index.md

------------------------------------------------------------------------

# Companion Guides

-   Sequence Diagram Handbook
-   Data Flow Handbook
-   API Standards Guide
-   Infrastructure Runbook
-   Architecture Review Checklist
-   Performance & Capacity Planning Guide
-   Coding Standards Guide
-   Database Standards Guide
-   Event Catalog
-   Glossary & Ubiquitous Language Reference
-   Error Catalog & Recovery Guide
-   Operational Metrics Catalog
-   Configuration Reference
-   Dependency Governance Guide
-   Release Management Guide

------------------------------------------------------------------------

# Governance Documents

-   Contributor Guide
-   Development Workflow
-   Definition of Done
-   ADR Template

------------------------------------------------------------------------

# Cross-Reference Matrix

  Topic           Primary Reference          Supporting References
  --------------- -------------------------- ------------------------------------
  System Design   Blueprint                  ADRs, Sequence Handbook
  APIs            API Standards Guide        Blueprint, Event Catalog
  Persistence     Database Standards Guide   Blueprint Part 8
  Operations      Infrastructure Runbook     Metrics Catalog, Error Catalog
  Deployment      Release Management Guide   Configuration Reference
  Security        Blueprint Part 13          Security Hardening Guide (planned)
  Observability   Metrics Catalog            Error Catalog, Runbook

------------------------------------------------------------------------

# Documentation Rules

-   Each topic has one authoritative source.
-   Cross-reference instead of duplicating content.
-   Update this index whenever a new major document is added.
-   Significant architectural changes should reference an ADR.

------------------------------------------------------------------------

# Suggested Reading Paths

## New Contributors

1.  README
2.  Blueprint
3.  Engineering Principles
4.  Contributor Guide
5.  Development Workflow

## Architects

1.  Blueprint
2.  ADR Index
3.  Architecture Review Checklist
4.  Companion Guides

## Operators

1.  Infrastructure Runbook
2.  Configuration Reference
3.  Release Management Guide
4.  Error Catalog
5.  Operational Metrics Catalog

------------------------------------------------------------------------

# Related Documents

This index references the complete Project Market Intel architecture
library and should remain the primary entry point into the
documentation.
