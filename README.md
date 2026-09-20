<div align="center">

<br/>

```
██╗███╗   ██╗███████╗███████╗██████╗ ██╗ ██████╗ ███╗   ██╗     █████╗ ██╗
██║████╗  ██║██╔════╝██╔════╝██╔══██╗██║██╔═══██╗████╗  ██║    ██╔══██╗██║
██║██╔██╗ ██║█████╗  █████╗  ██████╔╝██║██║   ██║██╔██╗ ██║    ███████║██║
██║██║╚██╗██║██╔══╝  ██╔══╝  ██╔══██╗██║██║   ██║██║╚██╗██║    ██╔══██║██║
██║██║ ╚████║██║     ███████╗██║  ██║██║╚██████╔╝██║ ╚████║    ██║  ██║██║
╚═╝╚═╝  ╚═══╝╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ╚═╝  ╚═╝╚═╝
                                                                         AI ⚡
```

<h3>The Enterprise AI Platform That Replaces 5 SaaS Tools — Self-Hosted, Open-Source, Free.</h3>

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Version](https://img.shields.io/badge/Version-v1.0.0--GA-22C55E?style=flat-square)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-F7DF1E?style=flat-square)](LICENSE)
[![OpenAI Compatible](https://img.shields.io/badge/OpenAI-Compatible-412991?style=flat-square&logo=openai&logoColor=white)](https://platform.openai.com/docs)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Tests](https://img.shields.io/badge/Tests-1800%2B_passing-22C55E?style=flat-square&logo=pytest&logoColor=white)](tests/)
[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/Yogesh10217/Inferion-ai/actions)

<br/>

[![GitHub stars](https://img.shields.io/github/stars/Yogesh10217/Inferion-ai?style=flat-square)](https://github.com/Yogesh10217/Inferion-ai/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Yogesh10217/Inferion-ai?style=flat-square)](https://github.com/Yogesh10217/Inferion-ai/network/members)
[![GitHub issues](https://img.shields.io/github/issues/Yogesh10217/Inferion-ai?style=flat-square)](https://github.com/Yogesh10217/Inferion-ai/issues)
[![Contributors](https://img.shields.io/github/contributors/Yogesh10217/Inferion-ai?style=flat-square)](https://github.com/Yogesh10217/Inferion-ai/graphs/contributors)

<br/>

**Python**  ·  **FastAPI**  ·  **Docker**  ·  **Redis**  ·  **PostgreSQL**  ·  **TypeScript**  ·  **Go**  ·  **Java**

</div>

---

> [!WARNING]
> **Official sources only.** Install or clone Inferion AI only from the verified repository: [github.com/Yogesh10217/Inferion-ai](https://github.com/Yogesh10217/Inferion-ai). Third-party mirrors or re-uploads are not reviewed by the project and may contain malware.

---

## Inferion AI

Your apps can call LLMs, but Inferion AI gives them a **coordinated enterprise control plane**: it routes requests intelligently to the cheapest healthy provider, enforces team budgets, runs autonomous agents, stores persistent memory, retrieves knowledge from your documents, and keeps a full audit trail — all behind one OpenAI-compatible API.

```
route → authenticate → enforce budget → run agent → recall memory → respond → observe
```

Instead of wiring that together in every project, you deploy it once and every team shares it.

**Optimize the token spend. Persist the context. Control the access.**

Inferion AI is MIT-licensed open source. It works with any OpenAI-compatible client today — Python, TypeScript, Go, Java, cURL — with zero client-side changes.

| Included | Count | What it gives you |
|---|---|---|
| Routing stages | **9 stages** | Capability filter, rules, policy, health, scoring, ranking, selection, failover, decision trace |
| Agent planners | **4 strategies** | ZeroShot, ReAct, Plan-Execute, Tree of Thought |
| Memory tiers | **6 tiers** | Working, Conversation, Semantic, Profile, Session, Episodic |
| Webhook event types | **19 types** | HMAC-SHA256 signed, dead-letter queues, replay |
| Plugin lifecycle hooks | **10 hooks** | Hot-reload, 7-state lifecycle |
| Observability exporters | **5 exporters** | Console, OTLP HTTP, OTLP gRPC, Jaeger, Zipkin |
| SDK languages | **4 languages** | Python, TypeScript, Go, Java |
| Automated tests | **1,800+** | Unit, integration, platform simulation |
| API endpoint groups | **50+** | Inference, agents, memory, knowledge, routing, tenants, billing |

---

## Install & Run Inferion AI

> [!IMPORTANT]
> **Complete Scratch Guide:** For step-by-step setup instructions from scratch, refer to [`SETUP_AND_RUN_GUIDE.md`](SETUP_AND_RUN_GUIDE.md).

### Recommended: Docker full stack

One command brings up the FastAPI Backend Gateway, Next.js Web Control Plane Dashboard, Ollama local model runner, Prometheus metrics, and Grafana dashboards.

```bash
git clone https://github.com/Yogesh10217/Inferion-ai.git
cd Inferion-ai
cp .env.example .env        # then add OPENAI_API_KEY and other provider keys
docker compose up -d --build
```

| Service | URL | Description |
|---|---|---|
| **Web Control Plane Dashboard** | http://localhost:3000/dashboard | Next.js 15 Web App Router Control Plane |
| **API + Swagger UI Docs** | http://localhost:8002/docs | FastAPI Interactive Swagger Explorer |
| **Metrics & Health Endpoint** | http://localhost:8002/metrics | Telemetry & SLA Prometheus Metrics |
| **Grafana Dashboards** | http://localhost:3000 | admin / admin |

### Local Python & Next.js Development Setup

```bash
git clone https://github.com/Yogesh10217/Inferion-ai.git
cd Inferion-ai

# 1. Start Python FastAPI Backend Engine
python -m venv .venv && .venv\Scripts\activate  # (or source .venv/bin/activate on Linux/macOS)
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# 2. Start Next.js Control Plane Web Dashboard (in second terminal)
cd frontend
npm install
npm run dev
```

Visit **http://localhost:3000/dashboard** to access the interactive web dashboard, chat playground, model registry UI, and FinOps analytics.

### Pick one deployment path only

| Path | What it installs | Use when |
|---|---|---|
| `docker compose up` | Full stack — API + Web UI + observability + local model | Production-like local setup |
| `uvicorn` + `npm run dev` | API + Web Dashboard | Active development / debugging |
| `make run` | Same as uvicorn, via Makefile shortcut | Team convention |

Do not run both a manual Python process and Docker Compose pointing at the same ports simultaneously.

> **Install trouble?** Refer to [`SETUP_AND_RUN_GUIDE.md`](SETUP_AND_RUN_GUIDE.md) or open a [GitHub Issue](https://github.com/Yogesh10217/Inferion-ai/issues).

---

## Drop-in Compatible

Change **one line** of code in any existing OpenAI client:

```python
# Before — calling OpenAI directly
client = OpenAI(base_url="https://api.openai.com/v1", api_key="sk-...")

# After — full enterprise control, zero other changes
client = OpenAI(base_url="http://your-inferion:8002/v1", api_key="sk-...")
```

Same for TypeScript, Go, Java, and cURL. No client-side refactoring required.

---

## Start Using Inferion AI

Start with the workflow you need, not the full feature list.

| What you are doing | Start here |
|---|---|
| Calling a model with cost control | `POST /v1/chat/completions` or Web Chat Playground |
| Registering or deleting models visually (UI) | Web UI at `http://localhost:3000/dashboard/routing` → **+ Register New Model** / **Delete (🗑️)** |
| Seeing which provider was chosen and why | `POST /v1/routing/decide` or Live Routing Visualizer |
| Creating a team workspace with a budget | `POST /v1/organizations` → `POST /v1/workspaces` |
| Generating an API key for a teammate | `POST /v1/auth/api-keys` or Web UI at `/dashboard/keys` |
| Running an autonomous agent | `POST /v1/agents` then `POST /v1/agents/{id}/run` |
| Indexing documents for RAG | `POST /v1/knowledge/ingest` |
| Searching your knowledge base | `POST /v1/knowledge/search` |
| Storing and recalling context | `POST /v1/memory/search` |
| Watching live metrics & FinOps costs | Web Dashboard at `http://localhost:3000/dashboard/finops` |
| Setting up pre-commit checks | `pip install pre-commit && pre-commit install` |

---

## Why Inferion AI?

| Without a gateway | With Inferion AI |
|---|---|
| Every team calls GPT-4 regardless of task complexity | Router picks the cheapest model that can handle the task |
| One leaked API key exposes everything | Per-tenant keys with RBAC, budgets, and hard limits |
| No visibility into who spends what | Per-workspace usage, cost, and quota dashboards |
| OpenAI outage = your product outage | Circuit breaker fails over to the next healthy provider |
| LLMs answer but can't act | Autonomous agents with 4 planners and human-in-the-loop gates |
| Context lost between sessions | 6-tier memory persists working state, conversation, and learned facts |
| Model provider changes require app rewrites | One OpenAI-compatible URL to update |

### The full routing flow

```
POST /v1/chat/completions
  +-- Capability Filter      -- does this model support vision / streaming / function calling?
  +-- Rule Evaluation        -- tenant-defined routing rules
  +-- Policy Evaluation      -- cost vs latency weight for this workspace
  +-- Health Check           -- circuit breaker: skip degraded providers
  +-- Weighted Scoring       -- multi-criteria score from real-time metrics
  +-- Provider Ranking       -- sort healthy candidates
  +-- Provider Selection     -- pick optimal provider
  +-- Failover Execution     -- retry on upstream error
  +-- Decision Trace         -- full explainable log stored for audit
```

A result is not just a response. It's a decision trail: which providers were considered, why the winner was chosen, and what the fallback would have been.

---

## Key Features

### 🏢 Multi-Tenancy

```
Your Company (Organization)
├── Engineering  →  Budget: $2,000/mo  |  Quota: 50,000 req/day
├── Sales        →  Budget:   $500/mo  |  Quota: 10,000 req/day
└── Finance      →  Budget: $1,000/mo  |  Quota:  5,000 req/day
```

Per-tenant API keys (`sk_...`), JWT auth, RBAC roles, Redis token-bucket rate limiting, and hard budget enforcement. One team's usage never bleeds into another.

---

### 🤖 Autonomous Agent Framework

```python
agent = client.agents.create(
    agent_id="dev_assistant",
    planner_strategy="react",        # ZeroShot | ReAct | PlanExecute | TreeOfThought
    tools=["python", "shell", "rest_api", "knowledge_search"],
    budget={"max_tokens": 50000, "max_cost_usd": 2.00},
    require_approval_for=["shell"]   # human-in-the-loop gate
)
result = client.agents.run("dev_assistant",
    prompt="Find all failing tests, fix them, and run pytest to verify."
)
```

| Planner | Best for |
|---|---|
| **ZeroShot** | Single-step, direct tasks |
| **ReAct** | Iterative tool use with reasoning steps |
| **Plan-Execute** | Multi-step DAG workflows |
| **Tree of Thought** | Multi-path exploratory problems |

Multi-agent coordination supports supervisor, consensus, and peer-to-peer team topologies.

---

### 🧠 6-Tier Memory Platform

| Tier | Stores |
|---|---|
| 🔴 **Working** | Current execution scratchpad — planner state, tool outputs |
| 🟠 **Conversation** | Multi-turn history with token budgeting |
| 🟡 **Semantic** | Learned facts and domain knowledge (vector-indexed) |
| 🟢 **Profile** | User preferences and communication style |
| 🔵 **Session** | Active task context with auto-expiry |
| 🟣 **Episodic** | Historical agent runs for experience-based recall |

---

### 📚 Knowledge & RAG

**Pipeline:** Parse → Chunk → Embed → Store → Hybrid Search → Rerank → Cite

**Vector stores:** Pinecone · Milvus · Qdrant · FAISS (local, no server needed)

---

### 🔭 Observability

Prometheus metrics export + OpenTelemetry distributed tracing with five exporters: Console, OTLP HTTP, OTLP gRPC, Jaeger, Zipkin. Pre-built Grafana dashboards included in the Docker Compose stack.

---

## API Reference

```http
# Inference (OpenAI-compatible)
POST   /v1/chat/completions         # Chat completions
GET    /v1/models                   # List available models

# Auth & Tenants
POST   /v1/auth/login               # JWT login
POST   /v1/auth/api-keys            # Issue API key
GET    /v1/organizations            # Manage orgs
GET    /v1/workspaces               # Manage workspaces

# Agents & Workflows
POST   /v1/agents                   # Create agent
POST   /v1/agents/{id}/run          # Execute agent
POST   /v1/workflows                # Create DAG workflow

# Memory & Knowledge
POST   /v1/memory/search            # Search memory tiers
POST   /v1/knowledge/ingest         # Index documents
POST   /v1/knowledge/search         # Hybrid RAG search

# Routing & Observability
POST   /v1/routing/decide           # Explain a routing decision
GET    /v1/metrics                  # Prometheus metrics
GET    /v1/health                   # Health probe
```

Full endpoint listing: [API.md](API.md) · Interactive explorer: http://localhost:8002/docs

---

## vs Alternatives

| Feature | **Inferion AI** | LiteLLM | Portkey | Dify | AWS Bedrock |
|---|:---:|:---:|:---:|:---:|:---:|
| Multi-provider routing | ✅ 9-stage | ✅ Basic | ✅ | ✅ | ✅ |
| Autonomous agent framework | ✅ 4 planners | ❌ | ❌ | ✅ | ✅ |
| Enterprise memory (6 tiers) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Multi-agent coordination | ✅ Teams + consensus | ❌ | ❌ | ❌ | ❌ |
| RAG / Knowledge platform | ✅ Full pipeline | ❌ | ❌ | ✅ | ✅ |
| Multi-tenancy (Org/Workspace) | ✅ Full | ✅ Basic | ✅ | ✅ | ✅ |
| Hard budget enforcement | ✅ | ✅ Basic | ✅ | ❌ | ✅ |
| Webhook event platform | ✅ 19 types | ❌ | ✅ | ❌ | ✅ |
| Plugin framework | ✅ 7-state | ❌ | ❌ | ✅ | ❌ |
| OpenTelemetry tracing | ✅ 5 exporters | ✅ | ✅ | ❌ | ✅ |
| Self-hostable | ✅ | ✅ | ❌ SaaS | ✅ | ❌ Cloud |
| Open Source | ✅ MIT | ✅ MIT | ❌ Paid | ✅ MIT | ❌ |
| SDK (Python / TS / Go / Java) | ✅ All 4 | ✅ | ✅ | ❌ | ✅ |
| Test suite | ✅ 1,800+ | ✅ | — | — | — |

---

## Project Status

> **Current release: `v1.0.0-GA Ready`** — 100% Production Ready. Web UI live API wiring, Kubernetes HA validation, 9-stage routing engine, and 1,800+ test suite are fully operational.



| Subsystem | Notes |
|---|---|
| 9-Stage Routing Engine | Capability, rules, policy, health, scoring, ranking, selection, failover, trace |
| Multi-Tenancy & Auth | JWT, API Keys (`sk_...`), RBAC, Redis rate limiting, budget enforcement |
| Agent Framework | 4 planners, human-in-the-loop, supervisor / consensus / peer-to-peer teams |
| 6-Tier Memory | Working, Conversation, Semantic, Profile, Session, Episodic |
| Knowledge & RAG | Pinecone, Milvus, Qdrant, FAISS, hybrid search, cross-encoder reranking |
| Event Platform | 19 event types, HMAC-SHA256, dead-letter queues, replay |
| Plugin Framework | 7-state lifecycle, 10 hooks, hot-reload |
| Observability | Prometheus + OpenTelemetry (5 exporters) + Grafana dashboards |
| SDKs & CLI | Python, TypeScript, Go, Java clients · 34-module Python CLI |
| Secret Manager | HashiCorp Vault KV v2 + AWS Secrets Manager / KMS |
| Web UI Dashboard | Next.js 15 control plane fully wired to backend REST API (`frontend/src/lib/api.ts`) |
| Kubernetes HA | Helm chart (18 manifests), Alembic zero-downtime migrations, PostgreSQL HA & Redis Sentinel |
| Load Testing | 10,000+ RPS via Locust & K6 — see [BENCHMARK_REPORT_10K_RPS.md](docs/BENCHMARK_REPORT_10K_RPS.md) |
| Test Suite | **1,800+ automated tests** — unit, integration, platform simulation |

Full milestone detail: [ROADMAP.md](ROADMAP.md)

---

## Developer Experience

### Makefile

```bash
make install       # Install all dependencies
make run           # Start dev server with auto-reload
make test          # Run the full pytest suite
make lint          # Ruff linting
make format        # Black + Ruff auto-fix
make docker        # Build Docker image
make compose-up    # Full stack (API + Ollama + Grafana)
make compose-down  # Stop all services
make clean         # Remove cache artifacts
```

### Pre-commit hooks

```bash
pip install pre-commit && pre-commit install
```

---

## Platform Support

| Provider | Status | Notes |
|---|---|---|
| OpenAI | ✅ Stable | Full streaming + function calling |
| Anthropic | ✅ Stable | Full streaming |
| AWS Bedrock | ✅ Stable | Via Secrets Manager credential adapter |
| Azure OpenAI | ✅ Stable | Endpoint + deployment name routing |
| Ollama (local) | ✅ Stable | Included in Docker Compose stack |
| Gemini | ✅ Stable | Native adapter registered |
| Cohere | ✅ Stable | Native adapter registered |
| Mistral | ✅ Stable | Native adapter registered |

---

## Security

> [!CAUTION]
> Install Inferion AI only from the official repository: **https://github.com/Yogesh10217/Inferion-ai**. Third-party re-uploads are not reviewed and may contain malware.

- **API Keys**: All tenant keys are hashed at rest; raw values are never stored.
- **HMAC-SHA256 Webhooks**: Every outbound webhook event is signed.
- **Secret Manager**: Provider credentials are fetched from HashiCorp Vault or AWS Secrets Manager at runtime — not stored in the database.
- **Budget Enforcement**: Hard spend limits are enforced before the request reaches any provider.
- **Compliance**: SOC 2 and GDPR evidence exporter scripts included under `scripts/`.

To report a vulnerability, use [GitHub private vulnerability reporting](https://github.com/Yogesh10217/Inferion-ai/security/advisories/new). Do not open a public issue for security reports.

---

## What's Inside

```
Inferion-ai/
├── app/              # FastAPI application — routers, middleware, services, models
├── tests/            # 1,800+ automated tests (unit, integration, simulation)
├── sdk/              # Python, TypeScript, Go, Java client wrappers
├── cli/              # Python CLI covering 34 domain modules
├── frontend/         # Next.js 15 admin control plane (in progress)
├── deploy/           # Helm chart, Terraform modules, Docker configs
├── monitoring/       # Prometheus rules, Grafana dashboard JSON
├── docs/             # Architecture, API, and operational guides
├── scripts/          # Credential verification, compliance evidence, utilities
└── alembic/          # Database migration scripts
```

---

## Documentation

| Document | What it covers |
|---|---|
| [📚 Architecture Overview](ARCHITECTURE_OVERVIEW.md) | System topology, middleware stack, data flows |
| [📊 Roadmap](ROADMAP.md) | Completed vs pending milestones toward v1.0 |
| [🔌 API Reference](API.md) | Full endpoint listing and request formats |
| [Routing Engine](docs/routing.md) | 9-stage logic, policy scoring, decision traces |
| [🤖 Agent Framework](docs/agents.md) | Planners, tool execution, multi-agent teams |
| [🧠 Memory Platform](docs/memory.md) | 6-tier architecture, scoring formulas |
| [📚 Knowledge & RAG](docs/knowledge.md) | Ingestion pipeline, vector store adapters |
| [Plugin Framework](docs/plugins.md) | Lifecycle hooks and extension guide |
| [🔭 Distributed Tracing](docs/tracing.md) | OpenTelemetry exporters and configuration |
| [📦 SDKs](docs/sdk.md) | Python, TypeScript, Go, Java client reference |
| [📊 Benchmark Report](docs/BENCHMARK_REPORT_10K_RPS.md) | 10,000+ RPS load test results |
| [📝 Changelog](CHANGELOG.md) | Version history |
| [🤝 Contributing](CONTRIBUTING.md) | PR workflow and code standards |
| [⚖️ Code of Conduct](CODE_OF_CONDUCT.md) | Community standards |

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for the PR workflow, branch conventions, and how to run the test suite locally before submitting.

---

## License

MIT © [Inferion AI Contributors](LICENSE)

OSS stays free. This repo is MIT-licensed. If you find Inferion AI useful, please ⭐ [star the repo](https://github.com/Yogesh10217/Inferion-ai) — it helps others discover it.

---

<div align="center">

**Built for teams that need real AI infrastructure, not another demo.**

[GitHub](https://github.com/Yogesh10217/Inferion-ai)  ·  [Issues](https://github.com/Yogesh10217/Inferion-ai/issues)  ·  [Changelog](CHANGELOG.md)  ·  [MIT License](LICENSE)

</div>
