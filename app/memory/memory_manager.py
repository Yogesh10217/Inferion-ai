"""
High-Level Memory Manager Orchestrator Subsystem
"""

from typing import Any, Dict, List, Optional

from app.memory.memory_context import MemoryContext
from app.memory.memory_service import MemoryService
from app.memory.memory_store import MemoryItemRecord


class MemoryManager:
    """Enterprise Memory Platform Coordinator Interface."""

    def __init__(self, service: Optional[MemoryService] = None):
        self.service = service or MemoryService()

    def create_memory(
        self,
        content: str,
        organization_id: str = "default_org",
        workspace_id: str = "default_workspace",
        user_id: Optional[str] = None,
        context_hint: Optional[str] = None,
    ) -> MemoryItemRecord:
        return self.service.create_memory_entry(
            content=content,
            organization_id=organization_id,
            workspace_id=workspace_id,
            user_id=user_id,
            context_hint=context_hint,
        )

    def get_memory(self, memory_id: str, organization_id: str = "default_org") -> MemoryItemRecord:
        return self.service.get_memory_entry(memory_id, organization_id)

    def list_memories(
        self,
        organization_id: str = "default_org",
        workspace_id: Optional[str] = None,
        memory_type: Optional[str] = None,
    ) -> List[MemoryItemRecord]:
        return self.service.list_memory_entries(organization_id, workspace_id, memory_type)

    def delete_memory(self, memory_id: str, organization_id: str = "default_org") -> bool:
        return self.service.delete_memory_entry(memory_id, organization_id)

    def archive_memory(self, memory_id: str, organization_id: str = "default_org") -> MemoryItemRecord:
        return self.service.archive_memory_entry(memory_id, organization_id)

    def search_memories(
        self,
        query: str,
        organization_id: str = "default_org",
        top_k: int = 10,
    ) -> List[MemoryItemRecord]:
        return self.service.search_memory(query, organization_id, top_k=top_k)

    def get_profile(self, user_id: str) -> Dict[str, Any]:
        return self.service.profile_tier.get_profile(user_id).to_dict()

    def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.service.profile_tier.update_profile(user_id, profile_data).to_dict()

    def assemble_context(
        self,
        user_id: str,
        session_id: str,
        query: Optional[str] = None,
        organization_id: str = "default_org",
    ) -> MemoryContext:
        """Assembles prompt memory context across all six memory tiers."""
        profile = self.get_profile(user_id)
        conv = self.service.get_conversation_memory(session_id).retrieve_context()
        facts = [f.to_dict() for f in self.service.semantic_tier.search(query or "", top_k=5)]
        sess = self.service.session_tier.recover_session(session_id)
        episodes = [ep.to_dict() for ep in self.service.episodic_tier.search_episodes(query or "", top_k=3)]

        return MemoryContext(
            working_memory={},
            conversation_summary=conv.get("summary"),
            conversation_messages=conv.get("messages", []),
            semantic_facts=facts,
            user_profile=profile,
            session_context=sess,
            relevant_episodes=episodes,
        )

    def get_analytics(self) -> Dict[str, Any]:
        return self.service.analytics.get_analytics()
