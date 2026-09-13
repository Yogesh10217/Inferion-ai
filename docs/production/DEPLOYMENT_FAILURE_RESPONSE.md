# Deployment Failure Response Policy

## 1. Failure Mapping & Escalation
- `CONFIGURATION_FAILURE`: Rollback required. State -> FAILED -> ROLLBACK_REQUIRED.
- `DEPLOYMENT_ARTIFACT_MISMATCH`: Rollback required. Halt execution immediately.
- `HEALTH_REGRESSION` / `TRAFFIC_DEGRADATION`: Stop progressive delivery step and revert router.
- `SECURITY_POLICY_VIOLATION`: Immediate halt and secret canary rotation.
- `SMOKE_TEST_FAILURE`: Immediate rollback to previous immutable image digest.
