# Production Runtime Certification Framework

## 1. Certification Classification Rules
- `SIMULATION_RUNTIME_VALIDATED`: Issued for simulation adapter execution.
- `CONTAINER_RUNTIME_VALIDATED`: Issued for Docker container execution.
- `LIVE_PRODUCTION_VALIDATED`: Issued ONLY when real cloud infrastructure is connected, deployment executed, health probes validated, smoke tests passed, and traffic metrics validated.
- `NOT_EXECUTED`: Issued when target cloud infrastructure or credentials are missing (`PRODUCTION_RUNTIME_TARGET_NOT_AVAILABLE`).
