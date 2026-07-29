# Intelligent Routing Engine

The **Intelligent Routing Engine** dynamically selects optimal model providers based on capabilities, health, cost, latency, weighted policies, and organization rules.

---

## 9-Stage Decision Pipeline

Every routing decision passes through the following sequential pipeline:

```
          [ Routing Request ]
                   │
                   ▼
     1. Capability Filtering
                   │
                   ▼
       2. Rule Evaluation
                   │
                   ▼
      3. Policy Evaluation
                   │
                   ▼
      4. Health Evaluation
                   │
                   ▼
      5. Weighted Scoring
                   │
                   ▼
      6. Provider Ranking
                   │
                   ▼
     7. Provider Selection
                   │
                   ▼
        8. Failover Check
                   │
                   ▼
       9. Final Decision
```

### Stage Details
1. **Capability Filtering**: Filters candidates to providers supporting all required features (`chat`, `streaming`, `vision`, `embeddings`, `function_calling`, `tools`).
2. **Rule Evaluation**: Checks priority-ordered deterministic rules (e.g., enterprise tier overrides, cost constraints, provider exclusions).
3. **Policy Evaluation**: Selects the active `RoutingPolicy` for the request based on organization overrides or defaults.
4. **Health Evaluation**: Inspects live health metrics and suppresses unhealthy providers.
5. **Weighted Scoring**: Computes normalized scores (0.0 to 1.0) using policy weights (`health`, `latency`, `cost`, `success_rate`, `capability_match`, `org_policy`).
6. **Provider Ranking**: Sorts remaining providers in descending order of composite score.
7. **Provider Selector**: Chooses top candidate, filtering out tripped circuit breakers or failed attempts.
8. **Failover Check**: Generates fallback sequences if primary choice degrades mid-flight.
9. **Final Decision**: Records step-by-step trace explanations in `RoutingContext` and returns the target provider ID.

---

## Policy Configuration & Weights

Policies govern how providers are scored.

### Default Policies
- **`default`**: Balanced scoring (`health: 35%`, `latency: 25%`, `cost: 15%`, `success_rate: 15%`, `capability_match: 5%`, `org_policy: 5%`).
- **`latency_optimized`**: Prioritizes lowest latency (`latency: 50%`, `health: 30%`, `success_rate: 10%`).
- **`cost_optimized`**: Prioritizes lowest cost (`cost: 50%`, `health: 30%`, `latency: 10%`).

---

## Admin API Endpoints

- `GET /v1/routing/policies`: List active policies.
- `POST /v1/routing/policies`: Create custom policy.
- `PATCH /v1/routing/policies/{id}`: Update policy weights or priorities.
- `DELETE /v1/routing/policies/{id}`: Delete a policy.
- `GET /v1/routing/rankings`: Get provider rankings for a policy.
- `GET /v1/routing/cache`: View cache hit/miss statistics.
- `POST /v1/routing/cache/invalidate`: Flush routing decision caches.
- `GET /v1/routing/metrics`: Get provider latency and success metrics.
- `GET /v1/routing/capabilities`: View registered provider capabilities.
- `GET /v1/routing/health`: Inspect routing engine health status.
- `POST /v1/routing/decide`: Simulate routing decision and retrieve full explanation trace.
