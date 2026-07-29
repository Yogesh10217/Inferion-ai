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

The project consists of several core subsystems that work together to provide a robust, multi-tenant inference platform:

- **Tenant Isolation**: A multi-tenant architecture with robust `TenantMiddleware` separating Organizations, Workspaces, Memberships, and Roles. Supports scoped API keys and context propagation down to the lowest service layer.
- **Quotas & Rate Limiting**: Extensible, multi-level limits (User, API Key, Workspace, Organization) backed by Redis algorithms (Fixed Window, Token Bucket, Sliding Window Log) ensuring reliable throughput. Usage tracking is detached from inference paths via high-performance, async `UsageEventEmitter`.
- **Billing & Subscriptions**: Subscription plans referencing reusable pricing models and quota policies. `CostCalculator` translates usage directly to structured invoices, while `BudgetMiddleware` enforces soft and hard organizational spend limits dynamically with customizable alert thresholds.
- **Routing & Failover**: An intelligent `RequestRouter` dynamically distributes traffic across multiple LLM providers based on custom load balancing strategies and robust fallback/failover mechanics. 
- **Batching & Scheduling**: Advanced `RequestScheduler` aggregates asynchronous incoming queries into grouped workloads optimized for the provider's capabilities.
- **Cache**: Fast exact-match caching reduces latency and prevents redundant queries.
- **Streaming**: Full SSE implementation supporting real-time token stream delivery for supported models.

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

## 🔒 Authentication & Authorization (Phase 3.1 & 3.2)

The engine now supports a full RBAC-based multi-tenant authentication system:

- **Optional Auth**: Set `AUTH_ENABLED=false` (default) for local dev without auth, or `AUTH_ENABLED=true` for production.
- **Database Backend**: Uses async SQLAlchemy (defaults to SQLite, compatible with PostgreSQL).
- **JWT & API Keys**: Support for JWT Bearer Tokens (with refresh tokens) and revocable API Keys (`sk_...`).
- **First-class Multi-Tenancy**: Users belong to Organizations. Resources (like API keys) are strictly isolated.
- **Workspaces**: Optional subdivisions within an organization for more granular resource management.
- **Dynamic RBAC**: Built-in roles (Admin, Developer, Viewer) scoped at both the Organization and Workspace levels.
- **Admin Bootstrapping**: Create the initial admin user and default organization using the CLI bootstrap script:
  ```bash
  python app/cli/bootstrap.py --username admin --email admin@example.com --password <your_admin_password>
  ```

### Tenant Resolution
When authenticating via JWT (e.g., UI), the active tenant is resolved via the `X-Organization-Id` and `X-Workspace-Id` headers.
API Keys are strongly bound to a specific Organization (and optionally a Workspace) upon creation, completely overriding any headers provided by the client to ensure security.

### API Key Management
Once authenticated (e.g. via `/v1/auth/login` passing `X-Organization-Id`), users can generate their own API keys via `POST /v1/auth/api-keys`. These keys can be passed as a standard Bearer token (`Authorization: Bearer sk_...`).

---

## 🚦 Quotas, Rate Limiting & Usage (Phase 3.3)

A robust, hierarchical system manages API abuse and tracks usage seamlessly without impacting core inference paths.

- **Rate Limiting**: Configurable limits (sliding window, token bucket, fixed window) to prevent immediate traffic spikes.
- **Quota Policies**: Configurable limits (requests per day, tokens per day) mapped strictly to Organizations, Workspaces, API Keys, and Users.
- **Hierarchical Evaluation**: Limits are evaluated top-down: `Organization → Workspace → API Key → User`. The request stops immediately at the first violation.
- **Concurrency Control**: Prevents resource starvation by issuing decaying "leases" for currently executing requests.
- **Multi-Backend**: Uses Redis (Lua scripts) for high-performance atomic increments, with a local Memory fallback circuit-breaker when Redis is down.
- **Async Usage Collection**: Usage events (token counts, durations, status codes) are emitted asynchronously avoiding latency overhead in the critical path.

---

## 💰 Billing, Subscriptions & Budgets (Phase 3.4)

A fully integrated billing ecosystem converts metered usage into structured invoices while preventing overspend.

- **Subscriptions**: Organizations can subscribe to predefined `SubscriptionPlan`s, seamlessly inheriting quota overrides.
- **Cost Calculation**: Independent pricing rules (per-provider, per-model, input vs output) accurately evaluate costs.
- **Invoicing**: Automatic generation of `Invoice`s and line items (via `InvoiceLineItem`) spanning custom billing cycles.
- **Budgets**: Prevent runaway costs by establishing `warning`, `critical`, and `hard_limit` thresholds evaluated strictly at runtime by a `BudgetMiddleware`.

---

## 🏢 Enterprise Administration Platform (Phase 3.5)

A comprehensive suite for platform operators to manage, audit, and monitor the entire LLM ecosystem.

- **Centralized Management**: Dedicated `/v1/admin/*` endpoints strictly protected by a global `platform_admin` role.
- **Organization Lifecycle**: Support for suspending or archiving rogue or churned organizations instantly.
- **Audit Logging**: Immutable, queryable `AuditEvent`s capturing all control-plane modifications (e.g. role grants, API key rotations).
- **System Health**: Endpoints to introspect internal cache stats, active batch dimensions, database pings, and backend availability.
- **Reporting Jobs**: Framework for asynchronous execution and compilation of high-level usage CSV/JSON exports.

---

## 📡 Event Platform & Webhooks (Phase 3.6)

A production-grade event-driven subsystem for internal event publishing and external webhook delivery decoupled from core inference execution.

### Architecture & Features
- **Abstract EventBus (`IEventBus`)**: Decoupled pub/sub interface allowing seamless backend substitution (Redis, Kafka, NATS, In-Memory).
- **Standardized Event Envelope**: All events use a unified schema containing `event_id`, `event_type`, `version` (schema version), `timestamp`, `organization_id`, `workspace_id`, `actor`, `source`, `correlation_id`, `request_id`, `payload`, and `metadata`.
- **Subscriber Isolation**: Async error boundaries ensure delivery failures to one webhook endpoint never impact other subscribers.
- **Staged Execution Pipeline**: Staged lifecycle `Publish -> Persist -> Queue Delivery -> Delivery Attempt -> Retry -> Dead-Letter`.
- **HMAC-SHA256 Security & Secret Rotation**: Webhooks signed with `HMAC-SHA256`. Supports dual-secret verification (`secret` & `secondary_secret`) for smooth secret rotation and configurable replay protection tolerance windows (`X-Timestamp`).
- **Retry Policy**: Exponential backoff with configurable initial/max intervals, retryable status codes (`[408, 429, 500, 502, 503, 504]`), and randomized jitter.
- **Dead-Letter Queue & Replay**: Failed deliveries beyond max retries route to DLQ. Replaying creates a new `WebhookDelivery` record while preserving original events and audit trails.

### Event Types (19 Total)
- **Inference**: `inference.completed`, `inference.failed`, `streaming.started`, `streaming.finished`
- **Tenancy**: `organization.created`, `organization.suspended`, `workspace.created`
- **Auth**: `user.created`, `user.disabled`, `api_key.created`, `api_key.revoked`
- **Billing**: `subscription.changed`, `budget.warning`, `budget.exceeded`, `invoice.generated`
- **System**: `provider.healthy`, `provider.unhealthy`, `system.startup`, `system.shutdown`

### Admin Webhook Endpoints
- `GET /v1/webhooks` - List webhook endpoints
- `POST /v1/webhooks` - Register new webhook endpoint
- `PATCH /v1/webhooks/{id}` - Update endpoint or secret
- `DELETE /v1/webhooks/{id}` - Delete endpoint
- `GET /v1/webhooks/deliveries` - Query delivery history
- `GET /v1/webhooks/events` - Query event log
- `POST /v1/webhooks/replay/{delivery_id}` - Replay failed delivery

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
| `AUTH_ENABLED` | `false` | Enable/disable authentication |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/engine.db` | DB connection string |
| `JWT_SECRET` | *(string)* | Secret for JWT signing |
| `RATE_LIMITING_ENABLED` | `true` | Enable rate limiting & quotas |
| `RATE_LIMIT_BACKEND` | `redis` | Backend to use (`redis` or `memory`) |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |

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

## Plugin Framework (Phase 4.0)

The LLM Inference Engine now supports an extensible AI Gateway via a production-grade plugin framework. Plugins extend the platform without modifying the core source code. See pp/plugins/examples for reference plugins.

### Plugin Lifecycle
Plugins support the following states: Install, Initialize, Enable, Disable, Uninstall.

### Permission Model
Capability-based permissions (e.g., events.publish) are enforced through a secure PluginContext injected into every plugin.
