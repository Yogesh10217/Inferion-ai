# Canary Deployment Runbook

## 1. Step Progression
1. **0% (Pre-flight)**: Deploy canary container instance. Verify health probes.
2. **5% Traffic**: Route 5% live traffic. Monitor error rate & latency SLA for 5 minutes.
3. **10% Traffic**: Route 10% traffic. Monitor dependency metrics.
4. **25% Traffic**: Route 25% traffic. Perform smoke test checks.
5. **50% Traffic**: Route 50% traffic. Verify database latency.
6. **100% Traffic**: Complete promotion to full release.

## 2. Automatic Rollback Triggers
- Error rate > 1.0%
- p95 latency > 500ms
- Probe health contract failure
- Artifact digest mismatch
