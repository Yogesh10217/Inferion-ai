# Reliability Certification Policy

## Decision States
- `RELIABILITY_CERTIFIED`: All reliability checks, chaos simulations, and audit integrity passed.
- `RELIABILITY_CERTIFIED_WITH_WARNINGS`: Non-critical warnings present.
- `RELIABILITY_MANUAL_REVIEW_REQUIRED`: Manual intervention required.
- `RELIABILITY_AT_RISK`: Reliability score < 75.0.
- `RELIABILITY_BLOCKED`: Critical failure or audit tampering detected.
- `RELIABILITY_NOT_EXECUTED`: Pipeline unexecuted.

## Token
Issued token: `PHASE_5_70_RELIABILITY_RESILIENCE_CERTIFIED`
