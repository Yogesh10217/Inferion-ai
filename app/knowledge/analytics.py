from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class UsageEvent(BaseModel):
    """Event model to represent platform usage for analytics."""

    event_type: str = Field(..., description="Type of event (e.g., query, retrieve, click)")
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalyticsReport(BaseModel):
    """Structure for aggregated analytics and usage tracking."""

    most_searched_docs: List[str] = Field(default_factory=list)
    most_cited_chunks: List[str] = Field(default_factory=list)
    average_retrieval_latency_ms: float = 0.0
    search_failures: int = 0
    top_users: List[str] = Field(default_factory=list)


class AnalyticsTracker:
    """Service to track usage metrics and generate analytics reports."""

    def __init__(self):
        # In-memory storage for mock implementation
        self.events: List[UsageEvent] = []

    async def track_query(self, user_id: str, query: str, latency_ms: float, success: bool):
        event = UsageEvent(
            event_type="query", user_id=user_id, metadata={"query": query, "latency_ms": latency_ms, "success": success}
        )
        self.events.append(event)

    async def track_citation(self, user_id: str, chunk_id: str, document_id: str):
        event = UsageEvent(
            event_type="citation", user_id=user_id, metadata={"chunk_id": chunk_id, "document_id": document_id}
        )
        self.events.append(event)

    async def generate_report(self) -> AnalyticsReport:
        """
        Generate analytics report from tracked usage events.
        """
        # Mock logic
        report = AnalyticsReport(
            most_searched_docs=["doc_a", "doc_c"],
            most_cited_chunks=["chunk_1", "chunk_5"],
            average_retrieval_latency_ms=115.4,
            search_failures=1,
            top_users=["user_123", "user_456"],
        )
        return report


# Singleton instance for app use
analytics_tracker = AnalyticsTracker()
