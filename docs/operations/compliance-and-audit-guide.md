# Compliance & Audit Guide

## Purpose

Establish repeatable evidence-based operational compliance.

## Principles

-   Infrastructure as Code
-   Least privilege
-   Immutable audit logs
-   Change approvals
-   Continuous verification

## Audit Domains

-   Access management
-   Secrets management
-   Deployment history
-   Database changes
-   Backup validation
-   Incident records

## Evidence Checklist

-   CI/CD logs
-   Pull requests
-   ADR references
-   Test reports
-   Security scans
-   Release notes

## Quarterly Audit

-   Review privileged accounts
-   Verify backups
-   Restore drill
-   Dependency review
-   Pen test findings
-   Corrective action tracking

``` mermaid
flowchart LR
A[Requirement]-->B[Evidence]
B-->C[Audit]
C-->D[Finding]
D-->E[Remediation]
```
