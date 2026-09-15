# 📝 Changelog

All notable changes to **Inferion AI** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.9.0-beta] - 2026-09-15

### Added
- **FastAPI Core Engine**: Complete implementation of 94+ submodules and 50+ API endpoint groups.
- **Intelligent Routing**: 9-stage routing engine with capability matching, weighted scoring, and failover.
- **Enterprise Multi-Tenancy**: Organization, Workspace, User isolation with JWT auth and Redis token bucket rate limiting.
- **Agent Orchestration**: 4 planning strategies (ZeroShot, ReAct, PlanExecute, TreeOfThought) and human-in-the-loop approvals.
- **6-Tier Memory System**: Working, Conversation, Semantic, Profile, Session, Episodic memory layers.
- **Knowledge Base & RAG**: Hybrid search pipeline with multi-vector store adapters (Pinecone, Qdrant, Milvus, FAISS).
- **Event Platform**: 19 webhook event types, signed payload verification, and dead-letter queues.
- **Plugin Framework**: 7-state lifecycle with hot-reloading capability.
- **Multi-Language SDKs**: Client libraries generated/structured for Python, TypeScript, Go, and Java.
- **Test Suite**: 1,800+ unit and integration test cases.

### Changed
- Refactored middleware stack for unified tracing and observability.
- Hardened CORS policies for production security.
