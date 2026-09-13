# Incident Response Runbook

## Overview

This runbook specifies the operational lifecycle, state transitions, and severity classifications for incidents.

## Incident Severities

- `P1`: Critical platform outage (Total service unavailability).
- `P2`: Major service degradation (High error rate or severe latency).
- `P3`: Partial degradation (Minor feature impairment).
- `P4`: Minor operational issue (Non-impacting anomaly).

## Incident State Machine

The state machine enforces 11 deterministic states:

```
NOT_DETECTED -> DETECTED -> TRIAGING -> CONFIRMED -> INVESTIGATING -> MITIGATING -> RECOVERING -> MONITORING -> RESOLVED -> POST_INCIDENT_REVIEW_REQUIRED -> CLOSED
```

Any attempt to transition along invalid paths (e.g. `NOT_DETECTED` -> `RESOLVED`) raises an `IllegalStateTransitionError`.
