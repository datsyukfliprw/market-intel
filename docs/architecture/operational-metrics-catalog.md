# Operational Metrics Catalog

**Project:** Project Market Intel

## Purpose

This catalog is the authoritative reference for every operational metric
emitted by Project Market Intel. It standardizes metric naming,
ownership, units, alert thresholds, and dashboard usage to ensure
consistent observability across the platform.

------------------------------------------------------------------------

# Metric Design Principles

-   Every metric has a clearly defined owner.
-   Metric names remain stable over time.
-   Labels are bounded and low-cardinality.
-   Metrics support actionable decisions.
-   Business metrics and operational metrics remain distinct.

------------------------------------------------------------------------

# Naming Convention

Recommended format:

`<domain>_<resource>_<measurement>`

Examples:

-   api_request_duration_seconds
-   strategy_execution_duration_seconds
-   scan_runs_completed_total
-   queue_jobs_pending
-   provider_requests_failed_total

------------------------------------------------------------------------

# API Metrics

  Metric                         Unit      Owner   Purpose
  ------------------------------ --------- ------- ---------------------
  api_requests_total             Count     API     Total requests
  api_request_duration_seconds   Seconds   API     Request latency
  api_errors_total               Count     API     Failed requests
  api_active_requests            Count     API     Concurrent workload

------------------------------------------------------------------------

# Background Job Metrics

  Metric                 Unit      Owner
  ---------------------- --------- --------
  jobs_completed_total   Count     Worker
  jobs_failed_total      Count     Worker
  jobs_retry_total       Count     Worker
  job_duration_seconds   Seconds   Worker

------------------------------------------------------------------------

# Strategy Metrics

-   strategy_execution_duration_seconds
-   strategy_execution_total
-   strategy_failures_total
-   recommendation_candidates_total

These metrics measure recommendation pipeline health.

------------------------------------------------------------------------

# Provider Metrics

Track for each provider:

-   Request count
-   Success rate
-   Error rate
-   Timeout count
-   Response latency

Provider labels should identify the provider without exposing sensitive
information.

------------------------------------------------------------------------

# Database Metrics

-   Query duration
-   Connection pool usage
-   Transaction count
-   Lock wait time
-   Migration duration

------------------------------------------------------------------------

# Infrastructure Metrics

Monitor:

-   CPU utilization
-   Memory utilization
-   Disk usage
-   Network throughput
-   Queue depth
-   Cache hit rate

------------------------------------------------------------------------

# Alert Thresholds

Example thresholds:

-   Error rate \> 5%
-   Queue depth above target
-   Provider latency exceeds SLO
-   Database availability degraded
-   Background worker failures increasing

Thresholds should be reviewed periodically.

------------------------------------------------------------------------

# Dashboard Mapping

Primary dashboards:

-   API Health
-   Recommendation Pipeline
-   Background Jobs
-   Provider Health
-   Infrastructure Capacity
-   Security Events

Each metric should appear on at least one operational dashboard.

------------------------------------------------------------------------

# Related Documents

-   Blueprint Part 14: Observability
-   Performance & Capacity Planning Guide
-   Infrastructure Runbook
-   Error Catalog & Recovery Guide
