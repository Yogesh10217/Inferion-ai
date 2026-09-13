# Post-Incident Review & Report Standard

## Overview

After resolving P1 or P2 incidents, a Post-Incident Review (PIR) report must be generated using `PostIncidentReportGenerator`.

## Report Schema

- Incident Metadata (ID, Severity, Service)
- Root Cause & Impact
- Timeline (Deterministic log of state transitions)
- Secrets Sanitization (All text processed via `SecretsSanitizer`)
- Lessons Learned & Action Items
