# Knowledge & Retrieval Platform

The Phase 5.0 Knowledge & Retrieval platform introduces robust RAG (Retrieval-Augmented Generation) capabilities to the LLM Inference Engine.

## Architecture
The platform is built on a highly modular and decoupled architecture, separating ingestion, storage, retrieval, and inference injection.

### Pipeline
The ingestion pipeline processes documents through several stages:
1. Document Parsing
2. Chunking
3. Embedding Generation
4. Vector Storage

### Profiles
Retrieval Profiles allow users to define domain-specific configurations, such as chunk sizes, embedding models, and reranking strategies.

### Query Rewriting
Before executing a search, queries can be rewritten using LLMs to expand terms, fix typos, or decompose complex queries for better retrieval performance.

### Context Builder
The Context Builder is responsible for assembling retrieved documents into the LLM prompt, ensuring it respects token limits and optimally formats the context for the specific model.

### Vector Stores
The platform supports multiple Vector Store abstractions, enabling integration with providers like Pinecone, Milvus, Qdrant, or local Faiss.

## SDK and CLI
- **SDK**: Use `KnowledgeClient` in the Python SDK to programmatically index documents and search.
- **CLI**: The `llm-engine knowledge` commands allow operators to trigger indexing and execute searches directly from the terminal.
