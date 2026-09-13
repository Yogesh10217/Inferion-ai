# Production Traffic Validation Policy

## 1. SLA Thresholds
- **Maximum Error Rate**: 0.01 (1.0%)
- **Maximum p95 Latency**: 500.0ms
- **Minimum Success Rate**: 0.99 (99.0%)
- **Probe Health**: `/live`, `/ready`, `/health` must respond HTTP 200.
- **Digest Matching**: `runtime_digest == expected_digest`.

## 2. Threshold Violation Handling
Any SLA violation immediately halts progressive delivery, transitions deployment state to `ROLLBACK_REQUIRED`, and triggers rollback execution.
