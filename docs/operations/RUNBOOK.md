# 🛠️ Operational SRE Runbook — Inferion AI Platform

---

## 1. Executive Summary & Core SLA Targets

| Metric | Target SLA / SLO | Warning Threshold | Critical Threshold |
|---|---|---|---|
| **API Availability** | 99.9% uptime | < 99.5% over 5m | < 99.0% over 5m |
| **P95 Request Latency** | < 2,000 ms | > 1,500 ms for 1m | > 3,000 ms for 1m |
| **Scheduler Queue Depth** | < 10 requests | > 20 requests | > 50 requests |
| **Provider Failure Rate** | < 0.1% | > 1.0% | > 5.0% |

---

## 2. Emergency Incident Triage & Decision Tree

```
                                  [ ALERT FIRED ]
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
          [ High Latency / Errors ]                  [ Pod Crash / OOM ]
                   │                                           │
         ┌─────────┴─────────┐                       ┌─────────┴─────────┐
         ▼                   ▼                       ▼                   ▼
  [ Provider Down? ]  [ Queue Backlog? ]      [ Memory Exhausted? ] [ DB / Redis Down? ]
         │                   │                       │                   │
  Circuit Breaker     Scale HPA / Worker      Increase Memory      Check DB Conn Pool
  Switch Provider     Restart Pods            Limits & Restart     Verify Redis Health
```

---

## 3. Detailed Incident Playbooks

### Playbook 1: Provider Outage or Circuit Breaker Tripped (`ProviderUnhealthy`, `HighProviderLatency`)
1. **Symptoms**: HTTP 503 or 504 errors, high provider response latency, logs show `CircuitBreakerOpenException`.
2. **Immediate Diagnostics**:
   ```bash
   # Check active provider health and circuit status
   curl -s http://localhost:8002/v1/health | jq .
   # Query Prometheus circuit status
   curl -s 'http://localhost:9090/api/v1/query?query=llm_engine_inference_provider_active_instances'
   ```
3. **Remediation**:
   - Check if external API provider (e.g. OpenAI, Ollama) is operational.
   - Force traffic shift to secondary provider via Failover Policy:
     ```bash
     curl -X POST http://localhost:8002/v1/admin/providers/failover -H "Content-Type: application/json" -d '{"primary": "openai", "fallback": "ollama"}'
     ```
   - Reset circuit breaker if provider has recovered:
     ```bash
     curl -X POST http://localhost:8002/v1/admin/circuit-breaker/reset?provider_id=openai
     ```

---

### Playbook 2: High Scheduler Queue Depth / Backlog (`QueueDepthHigh`, `SchedulerBacklogSustained`)
1. **Symptoms**: Slow request responses, growing queue metrics, queue depth > 50.
2. **Immediate Diagnostics**:
   ```bash
   kubectl logs -l app=llm-engine --tail=100 -n llm-engine | grep "RequestScheduler"
   ```
3. **Remediation**:
   - Scale out API gateway and worker pods:
     ```bash
     kubectl scale deployment/llm-engine-app --replicas=10 -n llm-engine
     kubectl scale deployment/llm-engine-worker --replicas=5 -n llm-engine
     ```
   - Inspect Dead-Letter Queue (DLQ) if stalled requests accumulate:
     ```bash
     curl -s http://localhost:8002/v1/admin/dlq | jq .
     ```

---

### Playbook 3: Gateway Pod CrashLoopBackOff / OOMKilled
1. **Symptoms**: Pod status `CrashLoopBackOff`, OOMKilled events.
2. **Diagnostics**:
   ```bash
   kubectl describe pod -l app=llm-engine -n llm-engine | grep -E "Exit Code|OOMKilled|Terminated"
   kubectl logs -l app=llm-engine -n llm-engine --previous
   ```
3. **Remediation**:
   - Increase memory request/limit in deployment:
     ```bash
     kubectl set resources deployment/llm-engine-app -n llm-engine -c=app --limits=memory=4Gi --requests=memory=1Gi
     ```
   - Restart deployment:
     ```bash
     kubectl rollout restart deployment/llm-engine-app -n llm-engine
     ```

---

## 4. Escalation Paths & Contacts

1. **L1 On-Call Engineer**: Primary responder for all firing alerts (Slack `#alerts-llm-engine`).
2. **L2 Infrastructure / SRE Lead**: Escalation target if incident unresolved within 15 minutes.
3. **L3 Core Engine Developer**: Escalation target for data corruption, consensus failure, or severe bugs.
