# Operational Certification Standard

## Overview

The `OperationalCertificationEngine` evaluates end-to-end telemetry and issues operational readiness certifications.

## Statuses

- `OPERATIONALLY_READY`: All SLOs met, error budget healthy, zero active incidents.
- `OPERATIONALLY_AT_RISK`: Warning thresholds exceeded or deployment health degraded.
- `OPERATIONALLY_DEGRADED`: SLOs breached or active P1/P2 incidents.
- `NOT_EXECUTED`: Production readiness preserved as unexecuted in pre-prod runs.
