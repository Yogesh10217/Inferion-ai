class BillingTracker:
    def __init__(self):
        self.embedding_tokens = 0
        self.retrieval_calls = 0
        self.vector_storage_bytes = 0
        self.reranking_requests = 0
        self.ingestion_jobs = 0
        self.indexing_duration_seconds = 0.0

    def track_embedding_tokens(self, tokens: int):
        self.embedding_tokens += tokens

    def track_retrieval_call(self):
        self.retrieval_calls += 1

    def track_vector_storage(self, size_bytes: int):
        self.vector_storage_bytes += size_bytes

    def track_reranking_request(self):
        self.reranking_requests += 1

    def track_ingestion_job(self):
        self.ingestion_jobs += 1

    def track_indexing_duration(self, duration: float):
        self.indexing_duration_seconds += duration


tracker = BillingTracker()
