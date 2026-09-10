# Operational Runbooks

## Overview
This runbook provides guidance for operating the Inferion AI in Kubernetes production environments.

## Incident Procedures
1. **Gateway Pod Crashes / CrashLoopBackOff**
   - Check pod logs: `kubectl logs -l app.kubernetes.io/component=gateway -n default`
   - Inspect memory limits & OOMKilled flags: `kubectl describe pod -l app.kubernetes.io/component=gateway`

2. **High Latency Alerts (>2.5s)**
   - Check provider health metrics: `GET /v1/routing/metrics`
   - Scale out HPA replica count manually if needed: `kubectl scale deployment/llm-engine-gateway --replicas=10`

3. **Scheduler Failures**
   - Verify Lease lock ownership: `kubectl get lease llm-scheduler-lease`
   - Restart scheduler instance: `kubectl rollout restart deployment/llm-engine-scheduler`
