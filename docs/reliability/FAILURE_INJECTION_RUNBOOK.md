# Failure Injection Runbook

## Safety Guardrails
1. **Container Allowlist Safety**: Container failure injection is strictly restricted to explicitly allowlisted test containers (`sim-container-01`, `test-container-01`). Arbitrary Docker containers, host volumes, or host networks are never targeted.
2. **Production Authorization Guard**: Production chaos execution requires ALL 7 conditions (Target Config, Human Auth, Release Auth, Target Identity, Artifact Digest, Experiment Auth, `auto_execution_blocked` Override). If any condition is missing, status remains `PRODUCTION_CHAOS_EXECUTION = NOT_EXECUTED`.
3. **Mandatory Auto Execution Blocking**: Destructive recovery recommendations enforce `auto_execution_blocked = True`.
