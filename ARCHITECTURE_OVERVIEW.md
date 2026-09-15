# 🏗️ Inferion AI — Architecture Overview

Inferion AI is an enterprise-grade LLM gateway, routing engine, multi-agent framework, and operational control plane.

---

## 📐 System Topology

```
                               ┌────────────────────────────────────────────────────────┐
                               │                 INFERION AI PLATFORM                   │
                               │                                                        │
   API Clients ───────────────►│  FastAPI Gateway Layer                                 │
   OpenAI SDK ────────────────►│    ├── Auth Middleware (JWT / API Key / RBAC)           │
   Web/Mobile Apps ───────────►│    ├── Tenant Isolation (Org → Workspace → User)        │
                               │    ├── Redis Token Bucket Rate Limiting                │
                               │    └── Budget Enforcement Middleware                   │
                               │                  │                                     │
                               │    ┌─────────────▼──────────────────────────┐          │
                               │    │     9-Stage Intelligent Router         │          │
                               │    │  Capability → Rules → Policy → Health  │          │
                               │    │  → Scoring → Ranking → Selection       │          │
                               │    │  → Failover → Final Decision           │          │
                               │    └──────┬────────────┬────────────┬───────┘          │
                               │           │            │            │                  │
                               │        OpenAI       Ollama      Anthropic /            │
                               │        (Cloud)      (Local)     Custom Model           │
                               │                                                        │
                               │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
                               │  │  Agent   │ │ Workflows│ │ Memory   │ │Knowledge │   │
                               │  │Framework │ │ Engine   │ │Platform  │ │ RAG Base │   │
                               │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
                               │                                                        │
                               │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
                               │  │ Event    │ │ FinOps + │ │Compliance│ │ Multi-   │   │
                               │  │ Platform │ │  MLOps   │ │ Framework│ │ Agent    │   │
                               │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
                               │                                                        │
                               │  Observability: Prometheus + OpenTelemetry + Grafana   │
                               └────────────────────────────────────────────────────────┘
```

---

## 🔀 9-Stage Routing Engine Pipeline

1. **Capability Filter**: Match model features (streaming, function calling, vision, context window).
2. **Rule Evaluation**: Apply custom routing rules configured per tenant.
3. **Policy Evaluation**: Compute cost optimization vs latency prioritization weights.
4. **Health Check**: Circuit breaker validation for active model providers.
5. **Weighted Scoring**: Multi-criteria scoring algorithm based on real-time metrics.
6. **Provider Ranking**: Rank healthy candidates.
7. **Provider Selection**: Select optimal candidate provider.
8. **Failover Execution**: Fallback strategies on upstream provider errors.
9. **Decision Trace**: Explainable trace log stored for audit and analytics.

---

## 🏢 Multi-Tenant Domain Hierarchy

- **Organization**: Top-level entity for billing, root policies, and compliance boundaries.
- **Workspace**: Team-level domain with dedicated quotas, rate limits, and memory isolation.
- **User / Service Account**: Individual caller authenticated via API Key or JWT token.

---

## 🤖 Agent Execution & Planning Engine

Supports 4 Planning Strategies:
- **ZeroShot**: Direct one-step reasoning.
- **ReAct**: Iterative thought-action-observation cycles.
- **Plan-Execute**: Multi-step graph generation followed by node execution.
- **Tree of Thought**: Multi-path exploratory tree search.

---

## 🧠 Memory & Knowledge Subsystems

- **6 Memory Tiers**: Working, Conversation, Semantic, Profile, Session, Episodic.
- **Knowledge Engine**: Document ingestion pipeline supporting vector stores (Pinecone, Milvus, Qdrant, FAISS) with hybrid semantic + keyword search and cross-encoder reranking.
