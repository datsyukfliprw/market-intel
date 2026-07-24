# Maintenance Window Guide

## Purpose

Provide a repeatable process for planned production maintenance with
minimal customer impact.

## Maintenance Lifecycle

1.  Plan
2.  Assess risk
3.  Notify stakeholders
4.  Verify backups
5.  Execute maintenance
6.  Validate services
7.  Close maintenance
8.  Review outcomes

## Pre-Window Checklist

-   Change approved
-   Rollback tested
-   Backups verified
-   Monitoring enabled
-   Incident bridge available
-   Customer notice published

## Execution Checklist

-   Freeze deployments
-   Capture baseline metrics
-   Execute changes
-   Validate health endpoints
-   Review dashboards
-   Remove freeze

## Post-Window Review

-   Success criteria met
-   Documentation updated
-   Follow-up work created

``` mermaid
flowchart LR
A[Plan]-->B[Notify]
B-->C[Execute]
C-->D[Validate]
D-->E[Close]
```
