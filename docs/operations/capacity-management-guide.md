# Capacity Management Guide

## Goals

Predict demand before customers experience degradation.

## Capacity Indicators

-   CPU
-   Memory
-   Disk
-   Network
-   Queue depth
-   Concurrent scans
-   Database growth

## Scaling Strategy

1.  Measure baseline
2.  Forecast growth
3.  Load test
4.  Trigger scaling
5.  Validate

## Threshold Examples

  Metric     Warning   Critical
  -------- --------- ----------
  CPU            70%        90%
  Memory         75%        90%
  Disk           80%        90%

## Quarterly Planning

-   Forecast user growth
-   Estimate storage
-   Review infrastructure cost
-   Retire unused resources

``` mermaid
flowchart TD
A[Forecast]-->B[Test]
B-->C[Scale]
C-->D[Observe]
D-->A
```
