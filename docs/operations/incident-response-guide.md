# Incident Response Guide

## Executive Summary

This guide defines the lifecycle for responding to production incidents
in Project Market Intel.

## Severity Levels

  Level   Description                    Target
  ------- ------------------------------ ----------------
  SEV-1   Complete outage or data loss   Immediate
  SEV-2   Major feature unavailable      15 min
  SEV-3   Minor degradation              Business hours
  SEV-4   Cosmetic or low impact         Backlog

## Lifecycle

1.  Detect
2.  Triage
3.  Assign Incident Commander
4.  Stabilize
5.  Mitigate
6.  Root Cause Analysis
7.  Recovery Validation
8.  Postmortem

## Roles

-   Incident Commander
-   Communications Lead
-   Operations Engineer
-   Domain Expert
-   Scribe

## Communication

-   Single source of truth
-   Timestamp every action
-   Record assumptions separately from facts

## Checklist

-   [ ] Confirm scope
-   [ ] Preserve logs
-   [ ] Pause deployments
-   [ ] Create timeline
-   [ ] Verify customer impact
-   [ ] Monitor recovery
-   [ ] Publish postmortem

## Postmortem Template

-   Timeline
-   Customer impact
-   Root cause
-   Contributing factors
-   Corrective actions
-   Preventive actions

``` mermaid
flowchart LR
A[Alert]-->B[Triage]
B-->C[Mitigate]
C-->D[Recover]
D-->E[RCA]
E-->F[Improvements]
```
