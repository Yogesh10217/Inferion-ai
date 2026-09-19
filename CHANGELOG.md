# 📝 Changelog

All notable changes to **Inferion AI** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Production Next.js 15 Admin Dashboard (`/dashboard`) — Overview, Routing Tracer, Agent Sandbox, RAG Visualizer, FinOps Analytics
- Enhanced Grafana dashboard bundles for inference latency, routing decisions, and per-tenant spend
- Helm chart stable release to ArtifactHub

---

## [0.9.0-beta] — 2026-09-15

> **v0.9.0-beta** is the first public pre-release. It represents a complete, production-grade backend platform with 94+ modules and 1,800+ automated tests. All core systems are operational.

### Added — Core Platform
- **FastAPI Core Engine**: 94+ submodules, 50+ API endpoint groups, full async request lifecycle
- **9-Stage Intelligent Routing Engine**: Capability filter → Rule evaluation → Policy evaluation → Health check → Weighted scoring → Provider ranking → Selection → Failover → Decision trace
- **Enterprise Multi-Tenancy**: Organization → Workspace → User hierarchy with complete resource isolation
- **JWT & API Key Auth**: `sk_...` scoped API keys, JWT login flow, and RBAC role enforcement
- **Redis Token Bucket Rate Limiting**: Per-tenant, per-workspace, and per-user quotas enforced at middleware layer
- **Hard Budget Enforcement**: Real-time cost tracking with configurable hard limits per workspace

### Added — Agent Framework
- **4 Planning Strategies**: ZeroShot (direct), ReAct (iterative reasoning + tools), PlanExecute (multi-step DAG), TreeOfThought (multi-path exploration)
- **Human-in-the-Loop Approvals**: Configurable approval gates per tool type (e.g., require human approval before `shell` execution)
- **Multi-Agent Team Coordination**: Supervisor, consensus voting, and peer-to-peer coordination modes
- **Tool Registry**: Built-in tools — `calculator`, `python`, `shell`, `rest_api`, `knowledge_search`

### Added — Memory Platform (6 Tiers)
- **Working Memory**: Execution scratchpad for planner state and in-flight tool outputs
- **Conversation Memory**: Multi-turn message history with token budget management
- **Semantic Memory**: Vector-indexed learned facts, preferences, and domain knowledge
- **Profile Memory**: User behavioral patterns, coding style, and communication preferences
- **Session Memory**: Active task/project context with configurable TTL auto-expiry
- **Episodic Memory**: Historical agent run log enabling experience-based recall and pattern reuse
- Composite ranking score formula combining recency, relevance, and frequency signals

### Added — Knowledge & RAG Platform
- **Full Ingestion Pipeline**: Document parsing → chunking → embedding → vector store indexing
- **Hybrid Search**: Dense vector similarity + BM25 sparse retrieval with score fusion
- **Cross-Encoder Reranking**: Secondary rerank pass for precision improvement
- **Citation Tracking**: Source attribution maintained through the full retrieval pipeline
- **Vector Store Adapters**: Pinecone, Milvus, Qdrant, FAISS (local/offline)

### Added — Observability Stack
- **Prometheus Metrics Export**: `/metrics` endpoint with per-route, per-provider, per-tenant counters and histograms
- **OpenTelemetry Distributed Tracing**: 5 exporters — Console, OTLP HTTP, OTLP gRPC, Jaeger, Zipkin
- **Pre-built Grafana Dashboards**: Inference latency, routing decision breakdown, error rates

### Added — Event Platform
- **19 Built-in Webhook Event Types**: request lifecycle, agent events, budget alerts, provisioning events, and more
- **HMAC-SHA256 Signed Payloads**: Cryptographic signature verification on every outgoing webhook
- **Dead-Letter Queues**: Automatic retry with exponential backoff; failed events parked for replay
- **Event Replay**: Re-deliver historical events to new or updated webhook endpoints

### Added — Plugin Framework
- **7-State Plugin Lifecycle**: `unloaded → loading → loaded → enabling → enabled → disabling → disabled`
- **10 Lifecycle Hooks**: `on_load`, `on_enable`, `on_disable`, `on_unload`, `on_request`, `on_response`, `on_error`, `on_model_select`, `on_token_count`, `on_audit`
- **Hot-Reload Support**: Plugins reloaded without server restart

### Added — SDKs & CLI
- **Python SDK**: Typed client covering all platform APIs
- **TypeScript SDK**: Node.js and browser-compatible client
- **Go SDK**: Idiomatic Go client with context propagation
- **Java SDK**: Maven-compatible client library
- **Python CLI**: 34-domain command-line interface (`inferion routing decide`, `inferion agents run`, etc.)

### Added — Infrastructure
- **Dockerfile**: Multi-stage build with non-root user and health check
- **Docker Compose**: Full stack — app + Ollama + Prometheus + Grafana + Redis
- **Helm Chart** (`deploy/helm/llm-engine`): HPA, PodDisruptionBudget, Vault secret mappings
- **Alembic Migrations**: Database schema versioning for PostgreSQL
- **GitHub Actions CI/CD**: 11 workflows — CI, CD, Docker build, Helm lint, K8s validate, security scan, SBOM, SDK publish, release

### Added — Testing
- **1,800+ Automated Tests**: Unit, integration, platform simulation, and production-scenario tests
- **69 Top-Level Test Modules**: Mirror every backend domain module
- **Load Testing Suite**: Locust (`FastHttpUser`) and K6 configurations for 10,000+ RPS sustained throughput

### Changed
- Unified middleware stack for consistent tracing and observability across all request paths
- Hardened CORS policies for production security — explicit allowlist replaces wildcard origins

---

## [0.5.0-alpha] — 2026-08

> Internal milestone. Core routing and auth established.

### Added
- Initial FastAPI application skeleton with async lifespan management
- OpenAI-compatible `/v1/chat/completions` endpoint
- Provider adapters: OpenAI, Ollama (local), Anthropic, AWS Bedrock, Azure OpenAI, Gemini, Cohere, Mistral
- Basic capability-based provider selection (Stage 1 routing)
- JWT authentication middleware
- Redis-backed rate limiting (token bucket algorithm)
- Prometheus `/metrics` endpoint
- Docker Compose with Ollama side-car

---

## [0.2.0-alpha] — 2026-07

> Internal milestone. Project scaffolding and architecture design.

### Added
- Repository scaffolding: `app/`, `tests/`, `docs/`, `deploy/` layout
- `pyproject.toml` with Hatchling build system and dev dependency groups
- Ruff + Black code formatting with pre-commit hooks
- Initial GitHub Actions CI skeleton (Python 3.10, 3.11, 3.12 matrix)
- MIT License and initial README
- Core Pydantic schemas for `InferenceRequest` and `InferenceResponse`
- `InferenceService` with provider factory pattern

---

## [0.1.0-alpha] — 2026-06

> Project inception. Architecture designed, repository initialized.

### Added
- Initial repository creation
- Architecture decision records: 9-stage routing design, 6-tier memory model, plugin lifecycle state machine
- Dependency selection: FastAPI, SQLAlchemy (async), Pydantic v2, OpenTelemetry
