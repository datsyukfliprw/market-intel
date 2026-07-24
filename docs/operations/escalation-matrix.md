# Escalation Matrix

## Purpose

Define who becomes involved as incident severity increases.

  Severity   Primary              Secondary          Executive
  ---------- -------------------- ------------------ -------------------
  SEV-1      Incident Commander   Engineering Lead   CTO/Product Owner
  SEV-2      On-call Engineer     Engineering Lead   Optional
  SEV-3      Feature Owner        Tech Lead          No
  SEV-4      Backlog Owner        Team               No

## Escalation Rules

-   Escalate early when impact is uncertain.
-   Escalate immediately for security or data loss.
-   Never delay escalation waiting for certainty.

## Communication Cadence

-   SEV-1: every 15 minutes
-   SEV-2: every 30 minutes
-   SEV-3: hourly
-   SEV-4: as needed
