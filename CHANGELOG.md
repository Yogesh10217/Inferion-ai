# Changelog

All notable changes to the **LLM Inference Engine** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-07-21

### 🚀 Summary
Initial production-grade release of the **LLM Inference Serving Platform** — providing OpenAI-compatible chat completion endpoints, dynamic multi-model routing, thread-safe metrics/registry, production-ready Server-Sent Events (SSE) streaming support, and containerized deployment pipelines.

---

### 🌟 Added Features
- **OpenAI-Compatible Chat Endpoint**: `POST /v1/chat/completions` supporting non-streaming and streaming inference requests.
- **Model Registry & Catalog**: `GET /v1/models` returning registered model metadata compatible with OpenAI specs.
- **Health Aggregation**: Endpoint suite (`/v1/health`, `/v1/ready`, `/v1/live`) reporting system state, model counts, and readiness metrics.
- **Provider Integrations**:
  - `OpenAIProvider`: HTTP streaming support for OpenAI cloud backends via `httpx`.
  - `OllamaProvider`: HTTP streaming support for local/remote Ollama servers via `httpx`.
  - Offline simulation fallbacks when no API keys are provided for offline development and testing.

### 🏗️ Architecture Improvements
- **Decoupled Application Lifespan**: Structured startup and shutdown event management via `lifespan` in `app/main.py`.
- **Dependency Injection**: Centralized `ServiceContainer` managing singletons for settings, registry, router, metrics, and health without global state.
- **Streaming Manager**: Introduced `StreamingManager` to intermediate between `InferenceService` and `BaseProvider`, enabling future timeout, cancellation, and heartbeat hooks without breaking public API contracts.
- **Model-Based Request Routing**: Strategy-pattern `RequestRouter` resolving model requests to appropriate provider instances.

### ⚡ Streaming Support
- **Server-Sent Events (SSE)**: Full compliance with OpenAI SSE streaming specification (`data: {...}` and `data: [DONE]`).
- **Heartbeat-Ready SSE Formatting**: Standardized `format_sse_event` helper supporting comment (`: keep-alive`) and custom event formatting without modifying provider streaming interfaces.
- **Normalized Response Chunks**: `BaseProvider.stream()` yields provider-agnostic `InferenceResponse` chunks.

### 📊 Observability
- **Thread-Safe Metrics**: `MetricsService` using `threading.RLock` to track request count, latency averages, and error counters across concurrent requests.
- **Observation Middleware**: `ObservationMiddleware` managing correlation IDs (`X-Request-ID`), request/response logging, and metrics recording.

### 🛠️ Infrastructure & Developer Experience
- **Multi-stage Dockerfile**: Pinned `python:3.11.9-slim` multi-stage build running as non-root user `appuser` (UID 10001) with healthcheck configuration.
- **Docker Compose**: `docker-compose.yml` service definitions for `app` and pinned `ollama/ollama:0.1.48`, with bridge networking, named volumes, and documented placeholders for Redis, Prometheus, and Grafana.
- **CI/CD Pipeline**: GitHub Actions workflow (`ci.yml`) matrix-testing Python `3.10` and `3.11`, dependency caching, formatting (`black`), linting (`ruff`), dependency security audit (`pip-audit`), and Docker build verification.
- **Pre-commit Hooks**: `.pre-commit-config.yaml` configured with Ruff, Black, trailing-whitespace, and end-of-file-fixer.
- **Makefile Automation**: Targets for `install`, `run`, `test`, `lint`, `format`, `docker`, `compose-up`, `compose-down`, and `clean`.

### 🧪 Testing
- Full automated test suite (56 tests) in `pytest` covering health endpoints, model registry, request routing, provider factory, schemas, observability, and full SSE streaming workflows (cancellation, chunk ordering, HTTP errors, connection timeouts).

---

## GitHub Release Description (v0.1.0)

```markdown
# ⚡ LLM Inference Engine v0.1.0 Release

We are excited to announce the **v0.1.0 release** of the LLM Inference Engine!

### Highlights
- 🚀 **OpenAI-Compatible Serving API**: Drop-in API replacement for OpenAI chat completions and model listings.
- 🌊 **Production-Ready SSE Streaming**: Real-time token streaming for OpenAI and Ollama backends via Server-Sent Events.
- 🔀 **Dynamic Multi-Model Routing**: Extensible request routing strategy connecting models to cloud or local providers.
- 📊 **Real-time Observability & Health**: Thread-safe latency tracking, structured JSON logs, correlation IDs (`X-Request-ID`), and health endpoints (`/v1/health`, `/v1/ready`, `/v1/live`).
- 🐳 **Production Docker & Compose**: Multi-stage, non-root Docker container pinned to `python:3.11.9-slim` and `docker-compose.yml` with Ollama.
- 🛡️ **CI/CD & Code Quality**: Matrix CI tests (Python 3.10 & 3.11), Ruff linting, Black formatting check, `pip-audit` security scan, and Pre-commit integration.

### Quick Start
```bash
git clone https://github.com/OnHighEngineer/llm-inference-engine.git
cd llm-inference-engine
cp .env.example .env
make install
make run
```
```
