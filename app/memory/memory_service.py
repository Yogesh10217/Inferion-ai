"""
Memory Subsystem Service Layer: Core Business Logic Implementation
"""

from typing import Dict, List, Optional

from app.memory.conversation_memory import ConversationMemory
from app.memory.episodic_memory import EpisodicMemory
from app.memory.memory_analytics import MemoryAnalyticsService
from app.memory.memory_classifier import MemoryClassifier
from app.memory.memory_compressor import MemoryCompressor
from app.memory.memory_extractor import MemoryExtractor
from app.memory.memory_retriever import MemoryRetriever
from app.memory.memory_store import MemoryItemRecord, MemoryStore
from app.memory.memory_summarizer import MemorySummarizer
from app.memory.profile_memory import ProfileMemory
from app.memory.semantic_memory import SemanticMemory
from app.memory.session_memory import SessionMemory
from app.memory.working_memory import WorkingMemory


class MemoryService:
    """Core Memory Service coordinating extraction, classification, storage, retrieval, and compression."""

    def __init__(
        self,
        store: Optional[MemoryStore] = None,
        classifier: Optional[MemoryClassifier] = None,
        extractor: Optional[MemoryExtractor] = None,
        retriever: Optional[MemoryRetriever] = None,
        compressor: Optional[MemoryCompressor] = None,
        summarizer: Optional[MemorySummarizer] = None,
    ):
        self.store = store or MemoryStore()
        self.classifier = classifier or MemoryClassifier()
        self.extractor = extractor or MemoryExtractor()
        self.retriever = retriever or MemoryRetriever()
        self.compressor = compressor or MemoryCompressor()
        self.summarizer = summarizer or MemorySummarizer()
        self.analytics = MemoryAnalyticsService()

        # Tiers
        self.profile_tier = ProfileMemory()
        self.session_tier = SessionMemory()
        self.episodic_tier = EpisodicMemory()
        self.semantic_tier = SemanticMemory()
        self.working_memories: Dict[str, WorkingMemory] = {}
        self.conversation_memories: Dict[str, ConversationMemory] = {}

    def create_memory_entry(
        self,
        content: str,
        organization_id: str = "default_org",
        workspace_id: str = "default_workspace",
        user_id: Optional[str] = None,
        context_hint: Optional[str] = None,
    ) -> MemoryItemRecord:
        cls_result = self.classifier.classify(content, context_hint=context_hint)
        rec = MemoryItemRecord(
            organization_id=organization_id,
            workspace_id=workspace_id,
            user_id=user_id,
            memory_type=cls_result.memory_type,
            content=content,
            metadata=cls_result.metadata,
            importance_score=cls_result.importance_score,
            confidence_score=cls_result.confidence_score,
            retention_policy=cls_result.retention_policy,
        )
        saved = self.store.save(rec)
        self.analytics.record_write()

        # Also store vector representation in retriever's vector store
        query_vector = [0.1] * 16  # default deterministic vector representation
        self.retriever.vector_store.add(
            memory_id=saved.memory_id,
            vector=query_vector,
            payload=saved.to_dict(),
            organization_id=organization_id,
            workspace_id=workspace_id,
        )
        return saved

    def get_memory_entry(self, memory_id: str, organization_id: str) -> MemoryItemRecord:
        self.analytics.record_read()
        return self.store.get(memory_id, organization_id)

    def list_memory_entries(
        self,
        organization_id: str,
        workspace_id: Optional[str] = None,
        memory_type: Optional[str] = None,
    ) -> List[MemoryItemRecord]:
        self.analytics.record_read()
        return self.store.list(organization_id, workspace_id, memory_type)

    def delete_memory_entry(self, memory_id: str, organization_id: str) -> bool:
        self.analytics.record_write()
        self.retriever.vector_store.delete(memory_id)
        return self.store.delete(memory_id, organization_id)

    def archive_memory_entry(self, memory_id: str, organization_id: str) -> MemoryItemRecord:
        self.analytics.record_write()
        return self.store.archive(memory_id, organization_id)

    def search_memory(
        self,
        query: str,
        organization_id: str,
        top_k: int = 10,
    ) -> List[MemoryItemRecord]:
        self.analytics.record_search()
        return self.store.search(query, organization_id, top_k=top_k)

    def get_working_memory(self, execution_id: str) -> WorkingMemory:
        if execution_id not in self.working_memories:
            self.working_memories[execution_id] = WorkingMemory(execution_id)
        return self.working_memories[execution_id]

    def get_conversation_memory(self, session_id: str) -> ConversationMemory:
        if session_id not in self.conversation_memories:
            self.conversation_memories[session_id] = ConversationMemory(session_id)
        return self.conversation_memories[session_id]
