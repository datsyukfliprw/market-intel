# Runbook Standards

## Purpose

Standardize operational runbooks.

## Required Sections

-   Purpose
-   Scope
-   Preconditions
-   Required Access
-   Procedure
-   Validation
-   Rollback
-   Escalation
-   References

## Writing Rules

-   One action per step
-   Include expected results
-   Include recovery path
-   Version every runbook

## Template

1.  Verify issue
2.  Gather evidence
3.  Execute change
4.  Validate success
5.  Record outcome

``` mermaid
flowchart LR
A[Problem]-->B[Runbook]
B-->C[Execute]
C-->D[Validate]
D-->E[Close]
```
