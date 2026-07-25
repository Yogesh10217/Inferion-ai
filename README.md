# ⚡ LLM Inference Engine — High-Performance LLM Serving Platform

> A production-grade inference engine for serving large language models at scale — with **multi-model routing**, **thread-safe model registry**, **SSE streaming**, and **robust observability** compatible with the OpenAI API specification.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-green)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://img.shields.io/badge/CI-GitHub_Actions-brightgreen?logo=github)](https://github.com/OnHighEngineer/llm-inference-engine/actions)

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
- **Streaming Manager**: Intermediary between InferenceService and providers for streaming lifecycle management.
- **Registry and Routing Layer**: Manages local models registry and resolves provider mappings.

## Observability Stack

The Inference Engine includes a full Prometheus and Grafana observability stack with pre-provisioned dashboards for the internal metrics.

Start the full stack using docker compose:
```bash
docker compose up -d
```

### Accessing the Monitoring Tools
- **Grafana**: `http://localhost:3000` (Default credentials: admin/admin)
- **Prometheus**: `http://localhost:9090`
- **Application Metrics Endpoint**: `http://localhost:8002/metrics`

The Grafana instance automatically provisions a folder called "LLM Inference Engine" containing pre-built dashboards for System Overview, Provider Latency, Batching metrics, Cache hits/misses, Scheduler queues, and more.

## Documentation

Full architectural documentation can be found in `ARCHITECTURE.md` and `ARCHITECTURE_OVERVIEW.md`.

For full architectural blueprints, diagrams, and deployment patterns, refer to the [docs/](docs/) directory.

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- (Optional) [Ollama](https://ollama.com) installed locally for local model serving
- (Optional) Docker & Docker Compose for containerized deployment

### Local Development

```bash
# Clone the repository
git clone https://github.com/OnHighEngineer/llm-inference-engine.git
cd llm-inference-engine

# Setup environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
make install
# Or manually:
# pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env to add your OPENAI_API_KEY if desired

# Run the FastAPI application
make run
# Or manually:
# uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### Docker Deployment

```bash
# Build and start all services (app + Ollama)
make compose-up
# Or manually:
# docker compose up -d --build

# Stop all services
make compose-down

# Build Docker image only
make docker
```

The `docker-compose.yml` includes:
- **app**: The inference engine on port `8002`
- **ollama**: Local Ollama server on port `11434`
- Commented placeholders for Redis, Prometheus, and Grafana (ready for Phase 2)

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

# Non-streaming request
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

### Streaming Example (SSE)

```python
# Streaming request — tokens arrive in real-time via Server-Sent Events
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)
```

### curl Examples

```bash
# Health check
curl http://localhost:8002/v1/health

# List models
curl http://localhost:8002/v1/models

# Non-streaming chat completion
curl -X POST http://localhost:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hello!"}]}'

# Streaming chat completion
curl -N -X POST http://localhost:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hello!"}], "stream": true}'
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `LLM Inference Engine` | Application display name |
| `APP_VERSION` | `0.1.0` | Semantic version |
| `ENVIRONMENT` | `development` | Runtime environment |
| `DEBUG` | `false` | Enable debug mode |
| `HOST` | `0.0.0.0` | Server bind host |
| `PORT` | `8002` | Server bind port |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `API_PREFIX` | `/v1` | API route prefix |
| `OPENAI_API_KEY` | *(empty)* | OpenAI API key (leave empty for simulated responses) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server endpoint |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |
| `DEFAULT_PROVIDER` | `openai` | Default provider for routing |
| `DEFAULT_MODEL` | `gpt-4o-mini` | Default model for inference |

See [.env.example](.env.example) for a ready-to-use template.

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=term-missing
```

---

## 🛠️ Developer Experience

### Makefile Commands

| Command | Description |
|---|---|
| `make install` | Install all dependencies (runtime + dev) |
| `make run` | Start FastAPI dev server with auto-reload |
| `make test` | Run pytest test suite |
| `make lint` | Run Ruff linter |
| `make format` | Format code with Black + Ruff auto-fix |
| `make docker` | Build local Docker image |
| `make compose-up` | Start services via Docker Compose |
| `make compose-down` | Stop Docker Compose services |
| `make clean` | Remove cache files and build artifacts |

### Pre-commit Hooks

```bash
# Install pre-commit hooks (one-time setup)
pip install pre-commit
pre-commit install

# Hooks run automatically on git commit:
# - Ruff (linting + auto-fix)
# - Black (formatting)
# - trailing-whitespace fixer
# - end-of-file fixer
```

---

## 📜 Roadmap & Future Enhancements

See [ROADMAP.md](ROADMAP.md) for details on future development phases including real HTTP integrations, persistent PostgreSQL/Redis model registries, and semantic vector caching.

---

## 📜 License

MIT — see [LICENSE](LICENSE)
