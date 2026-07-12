# ⚡ LLM Inference Engine — High-Performance LLM Serving Platform

> A production-grade inference engine for serving large language models at scale — with **continuous batching**, **async streaming**, **multi-model routing**, and **Temporal workflow orchestration** for model lifecycle management.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://reactjs.org)
[![Temporal](https://img.shields.io/badge/Temporal-Workflow-purple)](https://temporal.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-green)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## 🎯 Project Vision

Most developers just call OpenAI's API — this project shows you know how inference *actually works* at scale. This engine provides:

- 🚀 **Async inference serving** with streaming responses (SSE)
- 📦 **Continuous batching** — dynamically group requests for GPU efficiency
- 🔀 **Multi-model routing** — route to the right model based on task, cost, latency
- 🔄 **Model lifecycle management** — load, warm-up, health-check, hot-swap via Temporal
- 📊 **Real-time observability** — token throughput, latency percentiles, GPU utilization
- 🌐 **OpenAI-compatible API** — drop-in replacement for OpenAI API calls

This demonstrates deep understanding of ML serving infrastructure — a **highly valued skill** for remote AI/ML engineering roles.

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                        React Dashboard (UI)                          │
│  Model Registry | Request Monitor | Metrics | Config                │
└───────────────────────────┬──────────────────────────────────────────┘
                            │ REST + SSE
┌───────────────────────────▼──────────────────────────────────────────┐
│                   FastAPI Inference Gateway (Python)                 │
│                                                                      │
│  POST /v1/completions      POST /v1/chat/completions                │
│  POST /v1/embeddings       GET  /v1/models                          │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    Request Router                           │    │
│  │  • Model selection (cost / latency / capability policy)    │    │
│  │  • Rate limiting & quota enforcement                       │    │
│  │  • Auth & API key validation                               │    │
│  └──────────────────────┬──────────────────────────────────────┘    │
│                         │                                            │
│  ┌──────────────────────▼──────────────────────────────────────┐    │
│  │                   Batch Scheduler                           │    │
│  │  • Continuous batching (group arriving requests)           │    │
│  │  • Priority queues                                         │    │
│  │  • Timeout / SLA enforcement                               │    │
│  └──────────────────────┬──────────────────────────────────────┘    │
└───────────────────────────┼──────────────────────────────────────────┘
                            │
     ┌──────────────────────┼──────────────────────┐
     ▼                      ▼                      ▼
┌──────────┐         ┌──────────────┐      ┌──────────────────────────┐
│  OpenAI  │         │   Ollama     │      │  Temporal Workflow Engine │
│  GPT-4o  │         │ (Local LLMs) │      │                          │
│  GPT-3.5 │         │  Llama-3.1   │      │  ModelLifecycleWorkflow  │
└──────────┘         │  Mistral     │      │  ├── LoadModelActivity   │
                     │  Qwen        │      │  ├── WarmupActivity      │
                     └──────────────┘      │  ├── HealthCheckActivity │
                                           │  └── HotSwapActivity     │
                                           │                          │
                                           │  BatchProcessWorkflow    │
                                           │  InferenceMonitorCron    │
                                           └──────────────────────────┘
```

---

## 📁 Project Structure

```
llm-inference-engine/
├── backend/                              # Python backend
│   ├── app/
│   │   ├── main.py                       # FastAPI app entry point
│   │   ├── api/
│   │   │   ├── completions.py            # /v1/completions endpoint
│   │   │   ├── chat.py                   # /v1/chat/completions endpoint
│   │   │   ├── embeddings.py             # /v1/embeddings endpoint
│   │   │   ├── models.py                 # /v1/models registry endpoint
│   │   │   └── health.py                 # Health & readiness probes
│   │   ├── core/
│   │   │   ├── config.py                 # Settings & env vars
│   │   │   ├── router.py                 # Model routing logic
│   │   │   ├── scheduler.py              # Continuous batch scheduler
│   │   │   └── rate_limiter.py           # Token bucket rate limiting
│   │   ├── models/
│   │   │   ├── request.py                # OpenAI-compatible request schemas
│   │   │   ├── response.py               # OpenAI-compatible response schemas
│   │   │   └── registry.py               # Model registry data model
│   │   └── providers/
│   │       ├── base.py                   # Abstract LLM provider interface
│   │       ├── openai_provider.py        # OpenAI API provider
│   │       ├── ollama_provider.py        # Ollama local model provider
│   │       └── gemini_provider.py        # Google Gemini provider
│   ├── temporal/
│   │   ├── workflows/
│   │   │   ├── model_lifecycle.py        # Model load/warm-up/swap workflow
│   │   │   └── inference_monitor.py      # Cron monitoring workflow
│   │   ├── activities/
│   │   │   ├── load_model.py             # Pull & load a model
│   │   │   ├── warmup_model.py           # Run warm-up inference passes
│   │   │   ├── health_check.py           # Provider health check
│   │   │   ├── hot_swap.py               # Hot-swap to a new model version
│   │   │   └── collect_metrics.py        # Collect & push metrics
│   │   └── worker.py
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/                             # React + TypeScript dashboard
│   ├── src/
│   │   ├── components/
│   │   │   ├── ModelRegistry/            # Model cards & status
│   │   │   ├── RequestMonitor/           # Live request stream
│   │   │   ├── MetricsDashboard/         # Throughput, latency, GPU charts
│   │   │   └── Playground/              # Interactive inference playground
│   │   ├── pages/
│   │   └── store/
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── BATCHING_STRATEGY.md
│   ├── MODEL_ROUTING.md
│   └── OPENAI_COMPAT.md
└── README.md
```

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
    model="llama-3.1-8b",   # Route to local Ollama model
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True,
)
```

---

## 🚀 Milestones & Roadmap

### ✅ Phase 1 — Foundation (Weeks 1–2)
- [ ] OpenAI-compatible `/v1/chat/completions` endpoint
- [ ] OpenAI provider integration (proxy mode)
- [ ] Ollama local model provider
- [ ] Basic model registry (in-memory)
- [ ] Server-Sent Events (SSE) streaming

### 🔨 Phase 2 — Temporal + Batching (Weeks 3–4)
- [ ] `ModelLifecycleWorkflow` — load, warm-up, health-check, hot-swap
- [ ] Continuous batch scheduler (group requests by model)
- [ ] Priority queue (urgent vs. background requests)
- [ ] React dashboard — live request monitor and model status
- [ ] Token-level rate limiting

### 🚀 Phase 3 — Routing & Intelligence (Weeks 5–8)
- [ ] Intelligent model routing (cost/latency/capability policy)
- [ ] Fallback routing (if primary model fails, route to backup)
- [ ] Caching layer (exact-match and semantic caching)
- [ ] `/v1/embeddings` endpoint with multi-provider support
- [ ] Latency SLA enforcement

### 🌟 Phase 4 — Production (Weeks 9–12)
- [ ] GPU utilization monitoring via OpenTelemetry
- [ ] Horizontal scaling (multiple workers behind a load balancer)
- [ ] Model version management (A/B testing traffic splits)
- [ ] Cost tracking per API key / team
- [ ] Grafana dashboard template

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Inference Gateway | FastAPI (Python 3.11+) | Async, high-throughput, SSE support |
| Workflow Engine | Temporal | Model lifecycle management, monitoring crons |
| Local LLM Serving | Ollama | Easy local model management (Llama, Mistral, Qwen) |
| OpenAI API | OpenAI Python SDK | Cloud LLM fallback/primary |
| Gemini API | Google Gen AI SDK | Alternative cloud provider |
| Frontend | React 18 + TypeScript + Vite | Modern dashboard |
| Charting | Recharts + Chart.js | Real-time metrics visualization |
| Caching | Redis | Response cache, rate limit counters |
| CI/CD | GitHub Actions | Tests + Docker build on every PR |
| Monitoring | OpenTelemetry + Prometheus + Grafana | Full observability stack |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+, Node.js 20+, Docker + Docker Compose
- (Optional) Ollama installed locally for local model serving

```bash
git clone https://github.com/OnHighEngineer/llm-inference-engine.git
cd llm-inference-engine

# Start infrastructure (Temporal, Redis)
docker-compose up -d

# Backend
cd backend
uv sync
cp .env.example .env   # Add OPENAI_API_KEY, GEMINI_API_KEY
uv run uvicorn app.main:app --reload --port 8002
# Temporal worker (separate terminal)
uv run python temporal/worker.py

# Frontend
cd frontend && npm install && npm run dev
# Open http://localhost:5173

# Test the API
curl http://localhost:8002/v1/models
curl -X POST http://localhost:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hello!"}]}'
```

---

## 📊 Performance Goals

| Metric | Target |
|--------|--------|
| P50 Latency (first token) | < 200ms |
| P99 Latency (first token) | < 1s |
| Throughput (tokens/sec) | > 500 tok/s per GPU |
| Batch efficiency | > 80% GPU utilization |
| Uptime | 99.9% |

---

## 🔗 Related Projects

- [code-pr-reviewer](https://github.com/OnHighEngineer/code-pr-reviewer) — AI PR reviewer powered by this engine
- [agent-memory-harness](https://github.com/OnHighEngineer/agent-memory-harness) — Memory system for AI agents using this engine

---

## 📜 License

MIT — see [LICENSE](LICENSE)
