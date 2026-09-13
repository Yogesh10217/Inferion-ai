# Progressive Delivery Policy

## 1. Supported Strategies
- `ALL_AT_ONCE`: Direct 100% traffic cutover (Staging/Dev default).
- `ROLLING`: Incremental instance rollout (0% -> 25% -> 50% -> 75% -> 100%).
- `CANARY`: Step-wise traffic promotion (0% -> 5% -> 10% -> 25% -> 50% -> 100%).
- `BLUE_GREEN`: Parallel environment switch with fast fallback.
- `SIMULATION_ONLY`: Dry-run validation without network routing changes.

## 2. Validation Before Step Promotion
Traffic must NOT advance to the next percentage step unless real-time metrics (error rate, p95 latency, health probes) pass validation.
