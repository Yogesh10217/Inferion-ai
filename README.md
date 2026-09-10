<div align="center">

<br/>

```
██╗     ██╗     ███╗   ███╗    ██╗███╗   ██╗███████╗███████╗██████╗ ███████╗███╗   ██╗ ██████╗███████╗
██║     ██║     ████╗ ████║    ██║████╗  ██║██╔════╝██╔════╝██╔══██╗██╔════╝████╗  ██║██╔════╝██╔════╝
██║     ██║     ██╔████╔██║    ██║██╔██╗ ██║█████╗  █████╗  ██████╔╝█████╗  ██╔██╗ ██║██║     █████╗  
██║     ██║     ██║╚██╔╝██║    ██║██║╚██╗██║██╔══╝  ██╔══╝  ██╔══██╗██╔══╝  ██║╚██╗██║██║     ██╔══╝  
███████╗███████╗██║ ╚═╝ ██║    ██║██║ ╚████║██║     ███████╗██║  ██║███████╗██║ ╚████║╚██████╗███████╗
╚══════╝╚══════╝╚═╝     ╚═╝    ╚═╝╚═╝  ╚═══╝╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝╚══════╝
                                                                                               ENGINE ⚡
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
[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/OnHighEngineer/llm-inference-engine/actions)

<br/>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-features">Features</a> •
  <a href="#-api-reference">API Reference</a> •
  <a href="#-vs-alternatives">Comparison</a> •
  <a href="#-documentation">Docs</a>
</p>

<br/>

> **⚡ One platform. Infinite scale. Zero vendor lock-in.**  
> Route AI traffic intelligently, run autonomous agents, store enterprise memory, enforce compliance — all from a single self-hosted API that's 100% OpenAI-compatible.

</div>

---

## 🧠 What Is This?

Most teams hit a wall when scaling AI in production:

- 💸 **Runaway costs** — everyone calls GPT-4 even for simple tasks
- 🔒 **No access control** — a single leaked API key = game over
- 📊 **Zero visibility** — you have no idea who's using what
- 🔀 **Vendor lock-in** — OpenAI goes down, your product goes down
- 🤖 **LLMs just answer** — they can't actually *do things* for you

**LLM Inference Engine solves all of this.**

It's an **enterprise-grade AI gateway and autonomous agent platform** that sits between your apps and every AI model in the world — adding intelligent routing, multi-tenancy, billing, compliance, RAG, memory, and full autonomous agent execution.

```
Your App  ──►  LLM Inference Engine  ──►  OpenAI
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
git clone https://github.com/OnHighEngineer/llm-inference-engine.git
cd llm-inference-engine

# Setup
python -m venv .venv && .venv\Scripts\activate   # Windows
# source .venv/bin/activate                       # Linux/macOS

pip install -r requirements.txt

# Configure
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
                        │              LLM INFERENCE ENGINE                       │
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

---

## 🚀 Features

### 🔀 Intelligent 9-Stage Routing Engine
Route every request to the optimal provider automatically — no manual configuration needed.

```
Request → Capability Filter → Rule Evaluation → Policy Evaluation → Health Check
        → Weighted Scoring → Provider Ranking → Selection → Failover → Decision
```

- **Cost-optimized**: Automatically prefer cheaper models for simple tasks
- **Latency-optimized**: Route to the fastest healthy provider
- **Custom policies**: Define your own scoring weights per organization
- **Circuit breaker**: Automatically skip degraded providers
- **Full trace**: Every routing decision is explained and logged

```bash
# Simulate a routing decision and see the full explanation trace
POST /v1/routing/decide
{
  "model": "gpt-4o-mini",
  "required_capabilities": ["streaming", "function_calling"]
}
```

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
- Admin, Developer, Viewer roles at both Org and Workspace scope

---

### 🤖 Enterprise Agent Framework

Go beyond chat. Give your AI the ability to **actually do things**.

```python
# Create an agent that can browse the web, write code, and execute it
agent = client.agents.create(
    agent_id="dev_assistant",
    planner_strategy="react",       # ZeroShot | ReAct | PlanExecute | TreeOfThought
    tools=["calculator", "python", "shell", "rest_api", "knowledge_search"],
    budget={"max_tokens": 50000, "max_cost_usd": 2.00},
    require_approval_for=["shell"]  # Human-in-the-loop for dangerous actions
)

result = client.agents.run("dev_assistant", 
    prompt="Find all failing tests in the project, fix them, and run pytest to verify"
)
```

**Agent Lifecycle:**
```
User Prompt → Context Assembly → Knowledge Retrieval → Planning
→ Tool Selection → Approval Gate → Tool Execution → Observation
→ Reflection → Memory Update → Checkpoint → Final Response
```

**4 Planning Strategies:**
| Strategy | Best For |
|---|---|
| **ZeroShot** | Simple, direct tasks |
| **ReAct** | Iterative reasoning with tool use |
| **Plan-Execute** | Complex multi-step workflows |
| **Tree of Thought** | Exploring multiple solution paths |

---

### 🧠 Enterprise Memory Platform — 6 Tiers

Your AI remembers everything across sessions, users, and time.

```python
# Store a memory
client.memory.create(content="User prefers concise Python code with type hints")

# Semantic search across all memory
results = client.memory.search("What coding style does this user prefer?")
# → Returns ranked memories with composite scoring
```

**Memory Tiers:**

| Tier | What It Stores |
|---|---|
| 🔴 **Working** | Current execution scratchpad (planner state, tool outputs) |
| 🟠 **Conversation** | Multi-turn message history with token budgeting |
| 🟡 **Semantic** | Learned facts, preferences, domain knowledge (vector-indexed) |
| 🟢 **Profile** | User preferences, coding patterns, communication style |
| 🔵 **Session** | Active project/task context with auto-expiry |
| 🟣 **Episodic** | Historical agent/workflow runs for experience-based recall |

**Composite Ranking Formula:**
$$\text{Score} = (0.4 \times \text{Similarity}) + (0.2 \times \text{Recency}) + (0.2 \times \text{Importance}) + (0.2 \times \text{Confidence})$$

---

### 📚 Knowledge & RAG Platform

Turn any document collection into a searchable AI knowledge base.

```python
# Index documents
client.knowledge.ingest(
    documents=["report.pdf", "manual.docx", "data.csv"],
    embedding_model="text-embedding-3-large",
    chunk_size=512
)

# Hybrid semantic + keyword search
results = client.knowledge.search(
    query="What were the Q3 revenue figures?",
    top_k=5,
    rerank=True  # Cross-encoder reranking for precision
)
```

**Pipeline:** Document Parsing → Chunking → Embedding → Vector Store → Hybrid Search → Reranking → Context Assembly → Citation Tracking

**Supported Vector Stores:** Pinecone · Milvus · Qdrant · FAISS (local)

---

### ⚡ Workflow Engine

Define complex multi-step AI pipelines as code.

```python
workflow = {
    "name": "Research & Report",
    "nodes": [
        {"id": "search",    "type": "knowledge_search", "query": "{input}"},
        {"id": "analyze",   "type": "llm",   "prompt": "Analyze: {search}"},
        {"id": "approval",  "type": "human", "message": "Review before publishing?"},
        {"id": "publish",   "type": "tool",  "tool": "send_email", "depends_on": ["approval"]}
    ]
}
```

- **DAG-based execution** — parallel branches, conditional edges
- **Checkpoint & Recovery** — resume from any failed step
- **Human approval gates** — require sign-off before critical actions
- **Reusable templates** — build once, run anywhere

---

### 🛡️ Resilience & Reliability

```python
# Automatic failover: OpenAI → Ollama → Anthropic
# Circuit breaker trips after 5 failures in 60 seconds
# Exponential backoff retry (1s → 2s → 4s → 8s)
# Bulkhead isolation: provider failures don't cascade
# Timeout enforcement: no request hangs forever
```

---

### 💰 Billing, FinOps & Budget Control

```
Request comes in
     ↓
Budget Middleware checks:  Is org spend < hard_limit?
     ↓ NO  → 429 blocked instantly
     ↓ YES
Rate Limiter checks:       Is request rate within quota?
     ↓ NO  → 429 rate limited
     ↓ YES
Request proceeds → Usage tracked → Invoice updated → Forecasting updated
```

- Per-tenant, per-model, per-provider cost attribution
- Subscription plans with quota inheritance
- Automated invoicing with line items
- Cost anomaly detection and alerts
- Chargeback reports for internal billing

---

### 📡 Event Platform & Webhooks

React to everything that happens in real-time.

**19 built-in event types:**

```
inference.completed    inference.failed       streaming.started
organization.created   organization.suspended workspace.created
user.created           user.disabled          api_key.created
api_key.revoked        subscription.changed   budget.warning
budget.exceeded        invoice.generated      provider.healthy
provider.unhealthy     system.startup         system.shutdown
```

- HMAC-SHA256 signed payloads for security
- Dual-secret rotation (no downtime during rotation)
- Exponential backoff retries → Dead Letter Queue → Manual replay

---

### 🔭 Observability Stack

Full visibility across every request, provider, and cost center.

```bash
docker compose up -d  # Grafana + Prometheus auto-provisioned
```

**Pre-built dashboards for:**
- 📊 System overview & request rates
- ⚡ Provider latency & health
- 💰 Cost tracking per tenant/model
- 🤖 Agent execution metrics
- 🧠 Memory usage analytics
- 🔀 Routing decision stats

**OpenTelemetry Distributed Tracing:**
```
HTTP POST /v1/chat/completions  (Root Span)
  └── routing.decision          (Child Span)
  └── inference.execution       (Child Span)
       └── plugin.metrics_logger (Child Span)
  └── db.query                  (Child Span)
```

Exporters: **Console · OTLP HTTP · OTLP gRPC · Jaeger · Zipkin**

---

### 🧩 Plugin Framework

Extend the platform without touching core code.

```python
# manifest.json
{
  "id": "my_plugin",
  "version": "1.0.0",
  "permissions": [{"action": "events.publish", "resource": "*"}]
}

# plugin.py
class MyPlugin(BasePlugin):
    async def on_after_inference(self, ctx, response):
        await ctx.events.publish("custom.metric", {"tokens": response.usage.total_tokens})
        return response  # optionally modify the response
```

**10 lifecycle hooks:** `on_startup` · `on_before_request` · `on_after_request` · `on_before_inference` · `on_after_inference` · `on_provider_selected` · `on_provider_failed` · and more

**7 plugin states:** DISCOVERED → LOADED → INITIALIZED → ENABLED → RUNNING → DISABLED → UNLOADED

---

### 🏛️ Compliance Platform

Built-in support for major regulatory frameworks.

| Framework | Status |
|---|---|
| **SOC 2 Type II** | ✅ Controls mapping, evidence collection, continuous monitoring |
| **GDPR** | ✅ Consent management, data retention, right to erasure |
| **HIPAA** | ✅ PHI handling controls, audit trails |
| **ISO 27001** | ✅ Information security controls |

- Automated evidence collection and attestations
- Finding management and remediation workflows
- Real-time compliance posture scoring
- Immutable audit log for every control-plane action

---

### 🤝 Multi-Agent Coordination

Deploy teams of AI agents that collaborate, negotiate, and hand off work.

```python
team = client.teams.create(
    name="Research Team",
    agents=[
        {"id": "researcher", "role": "lead",     "tools": ["web_search", "knowledge_search"]},
        {"id": "analyst",    "role": "worker",   "tools": ["calculator", "python"]},
        {"id": "writer",     "role": "reporter", "tools": ["document_writer"]}
    ],
    coordination="supervisor"  # supervisor | consensus | peer-to-peer
)

result = client.teams.run("Research Team",
    task="Research quantum computing trends and write an executive summary"
)
```

**Coordination patterns:** Supervisor-Worker · Peer-to-Peer · Consensus Voting · Agent Negotiation · Task Delegation · Context Handoff

---

### ⚙️ MLOps Platform

Full model lifecycle management baked in.

- **Model Registry** — versioned artifact storage with metadata
- **A/B Experiments** — traffic splitting between model versions
- **Drift Detection** — automatic alerts when model behavior changes
- **Progressive Delivery** — canary and blue-green deployments
- **Prompt Management** — versioned prompt templates with rollback
- **Automated Rollback** — trigger on metric thresholds

---

## 🔌 API Reference

### Core Inference
```http
POST   /v1/chat/completions      # Chat (streaming & non-streaming)
GET    /v1/models                # List available models
GET    /v1/health                # Health status
GET    /v1/ready                 # Readiness probe
GET    /v1/live                  # Liveness probe
```

### Auth & Identity
```http
POST   /v1/auth/login            # Get JWT token
POST   /v1/auth/refresh          # Refresh token
POST   /v1/auth/api-keys         # Create API key
GET    /v1/auth/api-keys         # List API keys
DELETE /v1/auth/api-keys/{id}    # Revoke API key
```

### Organizations & Workspaces
```http
GET    /v1/organizations
POST   /v1/organizations
PATCH  /v1/organizations/{id}/suspend
GET    /v1/workspaces
POST   /v1/workspaces
```

### Agents
```http
POST   /v1/agents                          # Create agent
GET    /v1/agents                          # List agents
POST   /v1/agents/{id}/run                 # Run agent
POST   /v1/agents/sessions/{id}/resume     # Resume / submit approval
POST   /v1/agents/sessions/{id}/cancel     # Cancel execution
GET    /v1/agents/{id}/sessions            # Session history
```

### Memory
```http
POST   /v1/memory                # Store memory
GET    /v1/memory                # List memories
POST   /v1/memory/search         # Semantic search
POST   /v1/memory/compress       # Compress history
GET    /v1/memory/profile        # User profile
PATCH  /v1/memory/profile        # Update profile
GET    /v1/memory/analytics      # Usage analytics
```

### Knowledge / RAG
```http
POST   /v1/knowledge/ingest      # Index documents
POST   /v1/knowledge/search      # Search knowledge base
GET    /v1/knowledge/documents   # List documents
DELETE /v1/knowledge/documents/{id}
```

### Routing
```http
GET    /v1/routing/policies      # List policies
POST   /v1/routing/decide        # Simulate decision (with trace)
GET    /v1/routing/health        # Provider health
GET    /v1/routing/metrics       # Latency & success rates
GET    /v1/routing/rankings      # Provider rankings
```

### Webhooks
```http
GET    /v1/webhooks              # List endpoints
POST   /v1/webhooks              # Register endpoint
PATCH  /v1/webhooks/{id}         # Update / rotate secret
DELETE /v1/webhooks/{id}         # Remove endpoint
GET    /v1/webhooks/deliveries   # Delivery history
POST   /v1/webhooks/replay/{id}  # Replay failed delivery
```

### Plugins
```http
GET    /v1/plugins               # List plugins
POST   /v1/plugins/install       # Install plugin
POST   /v1/plugins/enable/{id}   # Enable
POST   /v1/plugins/disable/{id}  # Disable
POST   /v1/plugins/reload/{id}   # Hot-reload
GET    /v1/plugins/{id}/health   # Plugin diagnostics
```

### Tracing
```http
GET    /v1/tracing/config        # Active config
PUT    /v1/tracing/config        # Update exporter / sampling
GET    /v1/tracing/exporters     # List exporters
POST   /v1/tracing/exporters     # Switch exporter
```

---

## 🆚 vs Alternatives

| Feature | **LLM Inference Engine** | LiteLLM | Portkey | Dify | AWS Bedrock |
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
| Workflow engine (DAG) | ✅ | ❌ | ❌ | ✅ | ✅ |
| Compliance (SOC2/GDPR/HIPAA) | ✅ | ❌ | ❌ | ❌ | ✅ |
| Data governance | ✅ Full | ❌ | ❌ | ❌ | ✅ |
| FinOps platform | ✅ Full | ❌ | ✅ Basic | ❌ | ✅ |
| MLOps (A/B, drift, canary) | ✅ Full | ❌ | ❌ | ❌ | ✅ |
| OpenTelemetry tracing | ✅ 5 exporters | ✅ | ✅ | ❌ | ✅ |
| **Self-hostable** | ✅ | ✅ | ❌ SaaS | ✅ | ❌ Cloud |
| **Open Source** | ✅ MIT | ✅ MIT | ❌ Paid | ✅ MIT | ❌ |
| SDK (Python/TS/Go/Java) | ✅ All 4 | ✅ | ✅ | ❌ | ✅ |

> 💡 **LLM Inference Engine = LiteLLM + Dify + CrewAI + Langfuse + Compliance SaaS** — all in one self-hosted platform.

**Estimated commercial equivalent cost: ~$3,700/month** across 5 separate SaaS tools.  
**This project: $0. Forever.**

---

## 🌍 Real-World Use Cases

<table>
<tr>
<td width="50%">

**🏦 FinTech Company**
- Route sensitive financial queries to private on-prem Ollama
- Route general queries to cheap GPT-4o-mini
- GDPR compliance built-in
- Full audit trail for every AI interaction
- Budget alerts before overspending

</td>
<td width="50%">

**🏥 Healthcare Provider**
- HIPAA compliance controls out-of-the-box
- Separate workspaces for each department
- PHI detection and masking
- Immutable audit logs
- Knowledge base from medical literature

</td>
</tr>
<tr>
<td width="50%">

**🚀 SaaS Startup**
- One platform for all customers (multi-tenant)
- Per-customer billing and quotas
- Webhooks notify your app on every AI event
- Plugin marketplace for extensibility
- Usage-based pricing automation

</td>
<td width="50%">

**🏢 Enterprise IT**
- SSO integration
- Role-based access (Admin/Dev/Viewer)
- Cost chargeback by team
- Compliance reporting for auditors
- MLOps for model governance

</td>
</tr>
</table>

---

## ⚙️ Configuration

```env
# Server
PORT=8002
HOST=0.0.0.0
ENVIRONMENT=development

# Providers
OPENAI_API_KEY=sk-...
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-4o-mini

# Auth (set true for production)
AUTH_ENABLED=false
JWT_SECRET=your-secret-key
DATABASE_URL=sqlite+aiosqlite:///./data/engine.db

# Rate Limiting
RATE_LIMITING_ENABLED=true
RATE_LIMIT_BACKEND=redis
REDIS_URL=redis://localhost:6379/0

# Observability
PROMETHEUS_ENABLED=true
LOG_LEVEL=INFO
```

---

## 🛠️ Developer Experience

### Makefile Commands

```bash
make install      # Install all dependencies
make run          # Start dev server with auto-reload
make test         # Run pytest suite (56+ tests)
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
# Automatically runs: Ruff lint → Black format → whitespace fix on every commit
```

### Testing

```bash
pytest -v                                    # All tests
pytest --cov=app --cov-report=term-missing   # With coverage
pytest tests/test_health.py -v               # Specific file
```

---

## 📚 Documentation

| Doc | Description |
|---|---|
| [📖 Architecture Overview](ARCHITECTURE_OVERVIEW.md) | System design and component details |
| [🤖 Agent Framework](docs/agents.md) | Agent lifecycle, planners, tools |
| [🧠 Memory Platform](docs/memory.md) | 6-tier memory system |
| [🔀 Routing Engine](docs/routing.md) | 9-stage routing pipeline |
| [📚 Knowledge & RAG](docs/knowledge.md) | Document ingestion and retrieval |
| [🧩 Plugin Framework](docs/plugins.md) | Building and deploying plugins |
| [🔭 Distributed Tracing](docs/tracing.md) | OpenTelemetry setup |
| [📦 SDKs](docs/sdk.md) | Python, TypeScript, Go SDK guides |
| [🚨 Runbook](docs/operations/RUNBOOK.md) | Operational runbook |
| [🔒 Security Hardening](docs/operations/SECURITY_HARDENING.md) | Production security guide |
| [♻️ Disaster Recovery](docs/operations/DISASTER_RECOVERY.md) | DR procedures |
| [📈 Roadmap](ROADMAP.md) | Upcoming features |
| [📝 Changelog](CHANGELOG.md) | Version history |

---

## 🤝 Contributing

Contributions are welcome and appreciated!

```bash
# Fork → Clone → Branch
git checkout -b feature/your-feature-name

# Make changes, add tests
pytest -v

# Commit (pre-commit hooks run automatically)
git commit -m "feat: add your feature"

# Push and open a PR
git push origin feature/your-feature-name
```

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for our code of conduct and contribution guidelines.

---

## 📊 Project Stats

| Metric | Count |
|---|---|
| Backend modules | **85** |
| API endpoint groups | **50+** |
| Agent planner strategies | **4** |
| Memory tiers | **6** |
| Routing pipeline stages | **9** |
| Webhook event types | **19** |
| Plugin lifecycle hooks | **10** |
| Tracing exporters | **5** |
| SDK languages | **4** |
| Compliance frameworks | **4** |
| Automated tests | **56+** |

---

## 📜 License

MIT © [LLM Inference Engine Contributors](LICENSE)

---

<div align="center">

**Built with ❤️ for the open-source AI community**

If this project saved you time or money, please ⭐ **star the repo** — it helps others discover it!

<br/>

[![Star History](https://img.shields.io/github/stars/OnHighEngineer/llm-inference-engine?style=social)](https://github.com/OnHighEngineer/llm-inference-engine)
[![Fork](https://img.shields.io/github/forks/OnHighEngineer/llm-inference-engine?style=social)](https://github.com/OnHighEngineer/llm-inference-engine/fork)

<br/>

*"Most developers just call OpenAI's API — this is how inference actually works at scale."*

</div>
