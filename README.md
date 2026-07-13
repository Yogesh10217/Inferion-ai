# ⚡ LLM Inference Engine — High-Performance LLM Serving Platform

> A production-grade inference engine for serving large language models at scale — with **multi-model routing**, **thread-safe model registry**, and **robust observability and health logging** compatible with OpenAI specifications.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-green)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## 🎯 Project Vision

Most developers just call OpenAI's API — this project shows you how inference *actually works* at scale. This engine provides:

- 🚀 **Async inference serving** with streaming responses (SSE)
- 🔀 **Multi-model routing** — route to the right model based on task, prefix, and provider
- 📊 **Real-time metrics and tracing** — thread-safe counters, latency tracking, and structured logging
- 🏥 **Detailed health orchestration** — overall system metrics, model registration statuses, and provider checks
- 🌐 **OpenAI-compatible API** — drop-in replacement for OpenAI API calls

---

## 🏗️ Architecture Overview

The system is split into modular layers:
- **API/Transport Layer**: Handles HTTP serialization, CORS, and request routing.
- **Observability Middleware**: Measures latencies, manages request ID correlation headers, and outputs JSON log statements.
- **Service Layer**: Manages business flow orchestrations (Inference orchestration, Health aggregation).
- **Registry and Routing Layer**: Manages local models registry and resolves provider mappings.

For full architectural blueprints, diagrams, and deployment patterns, refer to:
- [Architecture Guide](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/docs/architecture.md)
- [API Spec](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/docs/api.md)
- [Provider Abstractions](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/docs/providers.md)
- [Routing Design](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/docs/routing.md)
- [Model Registry Design](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/docs/registry.md)
- [Observability Middleware](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/docs/middleware.md)
- [Application Startup](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/docs/startup.md)
- [System Sequence Diagrams](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/docs/sequence_diagrams.md)

---

## ✅ What is implemented in this repository

The current repository contains a fully verified, production-ready backend implementation:

- **App Initialization**: Decoupled initialization lifespan and [InfrastructureInitializer](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/app/core/initializer.py#L10) in [main.py](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/app/main.py).
- **Dependency Injection**: [ServiceContainer](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/app/core/container.py#L17) managing all singleton services without global state.
- **Metrics Tracking**: Thread-safe [MetricsService](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/app/services/metrics_service.py#L6) tracking requests, latencies, and error rates.
- **Aggregated Health Routing**: [HealthService](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/app/services/health_service.py#L18) reporting detailed engine state on `/health`, `/ready`, and `/live`.
- **Pure Transport Middleware**: [ObservationMiddleware](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/app/core/middleware.py#L14) handling correlation IDs (`X-Request-ID`) and structured logging.
- **Centralized Exception Handlers**: Standardized JSON responses for custom `AppException` types and validation errors, masking tracebacks.

---

## 🔌 OpenAI-Compatible API

This engine implements the OpenAI API specification — any code using OpenAI can switch to this engine by changing the `base_url`:

```python
from openai import OpenAI

# Point to your inference engine instead of OpenAI
client = OpenAI(
    base_url="http://localhost:8002/v1",
    api_key="your-api-key",
)

response = client.chat.completions.create(
    model="llama3.1",   # Route to local Ollama model
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True,
)
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- (Optional) Ollama installed locally for local model serving

```bash
# Clone the repository
git clone https://github.com/OnHighEngineer/llm-inference-engine.git
cd llm-inference-engine

# Setup environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
cp .env.example .env

# Run the FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port 8002

# Test endpoints
curl http://localhost:8002/v1/health
curl http://localhost:8002/v1/models
curl -X POST http://localhost:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hello!"}]}'
```

### Run Tests
```bash
python -m pytest
```

---

## 📜 Roadmap & Future Enhancements

See [ROADMAP.md](file:///c:/Users/Yogesh E/OneDrive/Desktop/Manjus/llm-inference-engine/ROADMAP.md) for details on future development phases including real HTTP integrations, persistent PostgreSQL/Redis model registries, and semantic vector caching.

---

## 📜 License

MIT — see [LICENSE](LICENSE)
