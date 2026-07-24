# Service Level Objectives Handbook

## Objective

Define measurable reliability targets.

## SLI Catalog

  SLI               Definition
  ----------------- ---------------------------
  Availability      Successful requests/total
  Latency           P95 response time
  Freshness         Market data delay
  Alert Delivery    Successful notifications
  Scanner Success   Completed scans

## Example SLOs

-   API Availability: 99.9%
-   P95 Latency: \<300ms
-   Alert Delivery: 99.5%
-   Scanner Completion: 99%

## Error Budget Policy

If 50% budget consumed: - Increase monitoring. If 100% exhausted: -
Freeze feature work. - Prioritize reliability.

## Review Cadence

Weekly dashboards. Monthly engineering review. Quarterly executive
review.
