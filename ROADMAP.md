# Project Roadmap

This document outlines the planned future features, integrations, and architectural enhancements for the LLM Inference Engine.

## Phase 1 (Completed Foundation)
- [x] Standardized API contracts compatible with OpenAI specifications.
- [x] Basic in-memory model registry with thread-safe lock management.
- [x] Request router with model prefix-based routing strategies.
- [x] Decoupled service container interface for clean dependency injection.
- [x] Observability layer featuring request metrics tracking and structured JSON logging.
- [x] Centralized error response serialization and mapping rules.

## Phase 2 (Real Integrations & Reliability)
- **Production Backend Connections**:
  - Integrate real HTTP clients (`httpx`) and official SDKs inside `OpenAIProvider`.
  - Connect `OllamaProvider` to actual running local/remote Ollama services.
- **Resilience and Error Handling**:
  - Implement request timeout mechanisms and automatic retries for downstream provider calls.
  - Implement a circuit breaker pattern to prevent overloading degraded providers.
  - Formulate fallback strategies (e.g., if OpenAI fails, automatically route to local Ollama model).

## Phase 3 (Infrastructure Scaling)
- **Persistent Model Registry**:
  - Replace the `InMemoryModelRegistry` with a database repository backing (e.g., PostgreSQL or Redis) to allow dynamic model registration across cluster pods without code redeployment.
- **Enterprise-Grade Middleware**:
  - Introduce an Authentication/Authorization middleware layer checking JWT tokens or API key headers.
  - Add rate-limiting capabilities using a sliding-window token bucket algorithm backed by Redis.
- **Distributed Telemetry**:
  - Wire up Prometheus metrics export endpoint (`/metrics`).
  - Add OpenTelemetry tracing context propagation to trace requests from client apps through to downstream model hosts.

## Phase 4 (Advanced Routing & Optimization)
- **Semantic Caching**:
  - Implement a vector-similarity cache layer. If a user's prompt is semantically close to a cached prompt, return the cached completion to minimize cost and latency.
- **Dynamic Routing Policies**:
  - Create cost-aware routing (prefer cheaper models when sampling/token constraints allow).
  - Implement latency-aware routing (dynamically select the fastest available provider/replica).
