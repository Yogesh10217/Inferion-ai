from prometheus_client import Counter, Gauge, Histogram

# Knowledge & Retrieval Metrics
embedding_tokens_total = Counter(
    "llm_engine_knowledge_embedding_tokens_total",
    "Total number of embedding tokens processed"
)

retrieval_calls_total = Counter(
    "llm_engine_knowledge_retrieval_calls_total",
    "Total number of retrieval calls made"
)

vector_storage_bytes = Gauge(
    "llm_engine_knowledge_vector_storage_bytes",
    "Current vector storage size in bytes"
)

reranking_requests_total = Counter(
    "llm_engine_knowledge_reranking_requests_total",
    "Total number of reranking requests made"
)

knowledge_documents_total = Counter(
    "llm_engine_knowledge_documents_total",
    "Total number of knowledge documents processed"
)

knowledge_chunks_total = Counter(
    "llm_engine_knowledge_chunks_total",
    "Total number of knowledge chunks generated"
)

knowledge_index_duration_seconds = Histogram(
    "llm_engine_knowledge_index_duration_seconds",
    "Time spent indexing knowledge documents"
)

knowledge_embedding_latency_seconds = Histogram(
    "llm_engine_knowledge_embedding_latency_seconds",
    "Latency of embedding generation"
)

knowledge_vector_search_latency_seconds = Histogram(
    "llm_engine_knowledge_vector_search_latency_seconds",
    "Latency of vector search operations"
)

knowledge_rerank_latency_seconds = Histogram(
    "llm_engine_knowledge_rerank_latency_seconds",
    "Latency of reranking operations"
)

knowledge_context_build_seconds = Histogram(
    "llm_engine_knowledge_context_build_seconds",
    "Time spent building context"
)

knowledge_cache_hits_total = Counter(
    "llm_engine_knowledge_cache_hits_total",
    "Total number of cache hits for knowledge operations"
)

knowledge_cache_misses_total = Counter(
    "llm_engine_knowledge_cache_misses_total",
    "Total number of cache misses for knowledge operations"
)

knowledge_errors_total = Counter(
    "llm_engine_knowledge_errors_total",
    "Total number of errors during knowledge operations"
)
