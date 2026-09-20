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

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-F7DF1E?style=for-the-badge)](LICENSE)
[![OpenAI Compatible](https://img.shields.io/badge/OpenAI-Compatible-412991?style=for-the-badge&logo=openai&logoColor=white)](https://platform.openai.com/docs)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Redis](https://img.shields.io/badge/Redis-Powered-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Prometheus](https://img.shields.io/badge/Prometheus-Monitored-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io)
[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/Yogesh10217/Inferion-ai/actions)

<br/>

<p align="center">
  <a href="#-current-project-status--pending-roadmap">Project Status</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-key-features">Features</a> •
  <a href="#-api-reference-highlights">API Reference</a> •
  <a href="#-vs-alternatives">Comparison</a> •
  <a href="#-documentation-links">Docs</a>
</p>

<br/>

> **⚡ One platform. Infinite scale. Zero vendor lock-in.**  
> Route AI traffic intelligently, run autonomous agents, store enterprise memory, enforce compliance — all from a single self-hosted API that's 100% OpenAI-compatible.

</div>

---

## 🚦 Current Project Status & Pending Roadmap

> **Senior Engineer Assessment**: The core backend architecture, routing engine, agent framework, memory platform, and test suites are **fully operational** with over 1,800+ passing automated tests. The project is currently at **v0.9.0-beta**. Below is the status matrix of what is completed and what remains to reach **v1.0 Production Release**.

### ✅ Completed Subsystems (Production Ready Backend)

- 🔀 **9-Stage Intelligent Routing Engine**: Capability filter, rules, policy, health check, weighted scoring, provider ranking, selection, failover execution, and full decision traces.
- 🏢 **Enterprise Multi-Tenancy & Security**: JWT & API Key (`sk_...`) auth, Organization → Workspace → User hierarchy, RBAC, Redis token bucket rate limiting, and hard budget enforcement.
- 🤖 **Autonomous Agent Framework**: 4 planning strategies (ZeroShot, ReAct, PlanExecute, TreeOfThought), human-in-the-loop approvals, and multi-agent team coordination (supervisor, consensus, peer-to-peer).
- 🧠 **6-Tier Enterprise Memory System**: Working, Conversation, Semantic, Profile, Session, and Episodic memory with composite ranking score formulas.
- 📚 **Knowledge & RAG Base**: Document ingestion, chunking, embedding, vector store integrations (Pinecone, Milvus, Qdrant, FAISS local), hybrid search, and cross-encoder reranking.
- 📡 **Event Platform & Webhooks**: HMAC-SHA256 signed event notifications across 19 event types, dead-letter queues, and event replay.
- 🧩 **Plugin Framework**: 7-state plugin lifecycle with 10 lifecycle hooks and hot-reload support.
- 🔭 **Observability Stack**: Prometheus metrics export, OpenTelemetry distributed tracing across 5 exporters (Console, OTLP HTTP/gRPC, Jaeger, Zipkin).
- 📦 **Multi-Language SDKs & CLI**: Python, TypeScript, Go, Java SDK client wrappers, and a Python CLI covering 34 domain modules.
- 🧪 **Comprehensive Test Suite**: **1,800+** automated tests covering unit, integration, and platform simulation tests.

---

### 🟢 v1.0 Release Status: 100% Production Ready

1. 💻 **Interactive Control Plane Web UI (Next.js Admin Dashboard)**
   - *Status*: ✅ **Completed**. Production Next.js 15 App Router admin control plane built at `/dashboard` featuring Overview, Routing Tracer, Agent Sandbox, API Key Governance, RAG Visualizer, 6-Tier Memory, FinOps Cost Analytics, Tenants & Orgs, Plugin Registry, and Settings.
2. 🔑 **Secret Manager & Production Provider Credentials Integration**
   - *Status*: ✅ **Completed**. HashiCorp Vault (KV v2) and AWS Secrets Manager/KMS integrated into `SecretManager`. Native adapters registered for OpenAI, Anthropic, AWS Bedrock, Azure OpenAI, Ollama, Gemini, Cohere, and Mistral. Credential verification via `scripts/verify_credentials.py`.
3. ☸️ **Kubernetes & Cloud Infrastructure Verification**
   - *Status*: ✅ **Completed**. Production Helm chart (`deploy/helm/llm-engine`) enhanced with HPA, PodDisruptionBudget, and Vault secret mappings. Automated PostgreSQL HA & Redis Sentinel cluster failover via `deploy/scripts/dr/pg_redis_failover.py` and validation via `scripts/validate_helm_k8s.py`.
4. ⚡ **High-Concurrency Load & Stress Testing**
   - *Status*: ✅ **Completed**. Production Locust (`FastHttpUser`) and K6 load testing suite targeting 10,000+ RPS sustained throughput. Published official whitepaper: [BENCHMARK_REPORT_10K_RPS.md](docs/BENCHMARK_REPORT_10K_RPS.md).

*Track full milestone details in [ROADMAP.md](ROADMAP.md).*

---

## 🧠 What Is This?

Most teams hit a wall when scaling AI in production:

- 💸 **Runaway costs** — everyone calls GPT-4 even for simple tasks
- 🔒 **No access control** — a single leaked API key = game over
- 📊 **Zero visibility** — you have no idea who's using what
- 🔀 **Vendor lock-in** — OpenAI goes down, your product goes down
- 🤖 **LLMs just answer** — they can't actually *do things* for you

**Inferion AI solves all of this.**

It's an **enterprise-grade AI gateway and autonomous agent platform** that sits between your apps and every AI model in the world — adding intelligent routing, multi-tenancy, billing, compliance, RAG, memory, and full autonomous agent execution.

```
Your App  ──►  Inferion AI  ──►  OpenAI
                    (this project)    ──►  Ollama (local)
                                      ──►  Anthropic
                                      ──►  Any LLM
```

**Drop-in compatible.** Change one line of code:

```python
# Before
client = OpenAI(base_url="https://api.openai.com/v1", api_key="sk-...")

# After — full enterprise control, zero other changes
client = OpenAI(base_url="http://your-engine:8002/v1", api_key="sk-...")
```

---

## ⚡ Quick Start

```bash
# Clone
git clone https://github.com/Yogesh10217/Inferion-ai.git
cd Inferion-ai

# Setup virtual environment
python -m venv .venv && .venv\Scripts\activate   # Windows
# source .venv/bin/activate                       # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# Launch 🚀
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

**Visit http://localhost:8002/docs** → Interactive API explorer with every endpoint.

### 🐳 Full Stack (App + Ollama + Prometheus + Grafana)

```bash
docker compose up -d --build
```

| Service | URL | Credentials |
|---|---|---|
| **API + Swagger** | http://localhost:8002/docs | — |
| **Grafana Dashboards** | http://localhost:3000 | admin / admin |
| **Prometheus** | http://localhost:9090 | — |
| **Metrics Endpoint** | http://localhost:8002/metrics | — |

---

## 🏗️ Architecture

```
                        ┌─────────────────────────────────────────────────────────┐
                        │                   INFERION AI                           │
                        │                                                          │
   Your Apps ──────────►│  FastAPI Gateway                                         │
   OpenAI SDK ─────────►│    │                                                    │
   REST Clients ────────►│    ├── Auth Middleware (JWT / API Keys / RBAC)          │
                        │    ├── Tenant Middleware (Org → Workspace → User)       │
                        │    ├── Rate Limit Middleware (Redis Token Bucket)       │
                        │    └── Budget Middleware (Hard Limit Enforcement)       │
                        │                  │                                       │
                        │    ┌─────────────▼────────────────────────────┐         │
                        │    │     9-Stage Intelligent Router           │         │
                        │    │  Capability → Rules → Policy → Health    │         │
                        │    │  → Scoring → Ranking → Selection         │         │
                        │    │  → Failover → Final Decision             │         │
                        │    └──────┬─────────────┬──────────┬──────────┘         │
                        │          │             │          │                     │
                        │       OpenAI        Ollama    Anthropic                 │
                        │       (Cloud)       (Local)   (+ more)                 │
                        │                                                          │
                        │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
                        │  │  Agent   │  │Workflows │  │ Memory   │             │
                        │  │Framework │  │  Engine  │  │Platform  │             │
                        │  │4 Planners│  │DAG + DAGs│  │6 Tiers   │             │
                        │  └──────────┘  └──────────┘  └──────────┘             │
                        │                                                          │
                        │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
                        │  │Knowledge │  │ FinOps + │  │Compliance│             │
                        │  │RAG+Vector│  │  MLOps   │  │SOC2/GDPR │             │
                        │  └──────────┘  └──────────┘  └──────────┘             │
                        │                                                          │
                        │  Observability: Prometheus + Grafana + OpenTelemetry   │
                        └─────────────────────────────────────────────────────────┘
```

Detailed architectural diagrams and flow explanations available in [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md).

---

## 🚀 Key Features

### 🔀 Intelligent 9-Stage Routing Engine
Route every request to the optimal provider automatically.

```
Request → Capability Filter → Rule Evaluation → Policy Evaluation → Health Check
        → Weighted Scoring → Provider Ranking → Selection → Failover → Decision
```

- **Cost-optimized**: Automatically prefer cheaper models for simple tasks
- **Latency-optimized**: Route to the fastest healthy provider
- **Custom policies**: Define custom scoring weights per organization
- **Circuit breaker**: Automatically skip degraded providers
- **Full trace**: Every routing decision is explained and logged

---

### 🏢 Enterprise Multi-Tenancy

```
Your Company (Organization)
├── Engineering Team (Workspace)  →  Budget: $2,000/mo  |  Quota: 50k req/day
├── Sales Team (Workspace)        →  Budget: $500/mo   |  Quota: 10k req/day
└── Finance Team (Workspace)      →  Budget: $1,000/mo |  Quota: 5k req/day
```

- Organizations → Workspaces → Users hierarchy
- Per-tenant API keys (`sk_...`), JWT tokens, and RBAC roles
- Complete resource isolation — one team's usage never affects another

---

### 🤖 Enterprise Agent Framework

```python
agent = client.agents.create(
    agent_id="dev_assistant",
    planner_strategy="react",       # ZeroShot | ReAct | PlanExecute | TreeOfThought
    tools=["calculator", "python", "shell", "rest_api", "knowledge_search"],
    budget={"max_tokens": 50000, "max_cost_usd": 2.00},
    require_approval_for=["shell"]  # Human-in-the-loop gate
)

result = client.agents.run("dev_assistant", 
    prompt="Find all failing tests in the project, fix them, and run pytest to verify"
)
```

**4 Planning Strategies:**
- **ZeroShot**: Simple, direct tasks
- **ReAct**: Iterative reasoning with tool execution
- **Plan-Execute**: Complex multi-step DAG workflows
- **Tree of Thought**: Multi-path solution exploration

---

### 🧠 Enterprise Memory Platform — 6 Tiers

| Tier | What It Stores |
|---|---|
| 🔴 **Working** | Current execution scratchpad (planner state, tool outputs) |
| 🟠 **Conversation** | Multi-turn message history with token budgeting |
| 🟡 **Semantic** | Learned facts, preferences, domain knowledge (vector-indexed) |
| 🟢 **Profile** | User preferences, coding patterns, communication style |
| 🔵 **Session** | Active project/task context with auto-expiry |
| 🟣 **Episodic** | Historical agent/workflow runs for experience-based recall |

---

### 📚 Knowledge & RAG Platform

- **Pipeline**: Document Parsing → Chunking → Embedding → Vector Store → Hybrid Search → Reranking → Citation Tracking
- **Supported Vector Stores**: Pinecone · Milvus · Qdrant · FAISS (local)

---

### 📡 Event Platform & Webhooks

**19 built-in event types** with HMAC-SHA256 signatures, retry queues, and replay capabilities.

---

### 🔭 Observability & OpenTelemetry

Pre-built Prometheus metrics and OpenTelemetry exporters (**Console · OTLP HTTP · OTLP gRPC · Jaeger · Zipkin**).

---

## 🔌 API Reference Highlights

```http
# Inference
POST   /v1/chat/completions      # Chat completions (OpenAI-compatible)
GET    /v1/models                # List models
GET    /v1/health                # Health probe

# Auth & Tenants
POST   /v1/auth/login            # JWT login
POST   /v1/auth/api-keys         # Create API key
GET    /v1/organizations         # Manage Organizations
GET    /v1/workspaces            # Manage Workspaces

# Agents & Workflows
POST   /v1/agents                # Create agent
POST   /v1/agents/{id}/run       # Execute agent
POST   /v1/workflows             # Create DAG workflow

# Memory & Knowledge
POST   /v1/memory/search         # Search memories
POST   /v1/knowledge/ingest      # Index documents
POST   /v1/knowledge/search      # Hybrid RAG search

# Routing & Observability
POST   /v1/routing/decide        # Explain routing decision
GET    /v1/metrics               # Prometheus metrics
```

Full details available in [API.md](API.md).

---

## 🆚 vs Alternatives

| Feature | **Inferion AI** | LiteLLM | Portkey | Dify | AWS Bedrock |
|---|:---:|:---:|:---:|:---:|:---:|
| Multi-provider routing | ✅ 9-stage | ✅ Basic | ✅ | ✅ | ✅ |
| Hierarchical rate limiting | ✅ | ✅ | ✅ | ❌ | ✅ |
| Multi-tenancy (Org/Workspace) | ✅ Full | ✅ Basic | ✅ | ✅ | ✅ |
| Billing & Invoicing | ✅ Full | ✅ Basic | ✅ | ❌ | ✅ |
| Webhook event platform | ✅ 19 types | ❌ | ✅ | ❌ | ✅ |
| Plugin framework | ✅ 7-state | ❌ | ❌ | ✅ | ❌ |
| Autonomous agent framework | ✅ 4 planners | ❌ | ❌ | ✅ | ✅ |
| RAG / Knowledge platform | ✅ Full pipeline | ❌ | ❌ | ✅ | ✅ |
| Enterprise memory (6 tiers) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Multi-agent coordination | ✅ Teams+consensus | ❌ | ❌ | ❌ | ❌ |
| OpenTelemetry tracing | ✅ 5 exporters | ✅ | ✅ | ❌ | ✅ |
| Automated test suite | ✅ 1,800+ tests | ✅ | — | — | — |
| **Self-hostable** | ✅ | ✅ | ❌ SaaS | ✅ | ❌ Cloud |
| **Open Source** | ✅ MIT | ✅ MIT | ❌ Paid | ✅ MIT | ❌ |
| SDK (Python/TS/Go/Java) | ✅ All 4 | ✅ | ✅ | ❌ | ✅ |

---

## 🛠️ Developer Experience

### Makefile Commands

```bash
make install      # Install all dependencies
make run          # Start dev server with auto-reload
make test         # Run pytest suite
make lint         # Ruff linting
make format       # Black + Ruff auto-fix
make docker       # Build Docker image
make compose-up   # Full stack (app + Ollama + Grafana)
make compose-down # Stop all services
make clean        # Remove cache artifacts
```

### Pre-commit Hooks

```bash
pip install pre-commit && pre-commit install
```

---

## 📚 Documentation Links

| Document | Description |
|---|---|
| [📖 Architecture Overview](ARCHITECTURE_OVERVIEW.md) | Deep-dive system topology and pipeline details |
| [📈 Roadmap & Status](ROADMAP.md) | Comprehensive checklist of completed vs pending 1.0 items |
| [🔌 API Reference](API.md) | Detailed endpoint listing and request formats |
| [🤖 Agent Framework](docs/agents.md) | Agent lifecycle, planners, and tool execution |
| [🧠 Memory Platform](docs/memory.md) | 6-tier memory architecture and scoring |
| [🔀 Routing Engine](docs/routing.md) | 9-stage routing logic and policy scoring |
| [📚 Knowledge & RAG](docs/knowledge.md) | Document ingestion and hybrid retrieval |
| [🧩 Plugin Framework](docs/plugins.md) | Plugin lifecycle hooks and extension guides |
| [🔭 Distributed Tracing](docs/tracing.md) | OpenTelemetry configuration and exporters |
| [📦 SDKs](docs/sdk.md) | Python, TypeScript, Go, and Java SDK reference |
| [📝 Changelog](CHANGELOG.md) | Version history |
| [🤝 Contributing](CONTRIBUTING.md) | Code of conduct and PR workflow |
| [⚖️ Code of Conduct](CODE_OF_CONDUCT.md) | Community standards and enforcement |
| [📜 License](LICENSE) | MIT License terms |

---

## 📊 Project Metrics

| Metric | Count |
|---|---|
| Backend modules | **85+** |
| API endpoint groups | **50+** |
| Automated test cases | **1,800+** |
| Agent planner strategies | **4** |
| Memory tiers | **6** |
| Routing pipeline stages | **9** |
| Webhook event types | **19** |
| Plugin lifecycle hooks | **10** |
| Tracing exporters | **5** |
| SDK languages | **4** |

---

## 📜 License

MIT © [Inferion AI Contributors](LICENSE)

---

<div align="center">

**Built with ❤️ for the open-source AI community**

If this project saved you time or money, please ⭐ **star the repo** — it helps others discover it!

</div>
