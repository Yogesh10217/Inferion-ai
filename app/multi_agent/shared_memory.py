"""
Team-Wide Shared Memory Integration Layer (Phase 5.3 Integration)
"""

import logging
from typing import Dict, Any, List, Optional
from app.memory.memory_service import MemoryService, MemoryItemRecord

logger = logging.getLogger(__name__)


class SharedMemoryManager:
    """Provides team-wide access to Working, Conversation, Semantic, and Episodic Memories."""

    def __init__(self, memory_service: Optional[MemoryService] = None):
        self.memory_service = memory_service or MemoryService()

    def store_team_memory(
        self,
        content: str,
        tenant_id: str,
        organization_id: str,
        workspace_id: str,
        team_id: str,
        author_id: str,
        context_hint: Optional[str] = None,
    ) -> MemoryItemRecord:
        """Store a team memory item in Phase 5.3 Memory Service."""
        rec = self.memory_service.create_memory_entry(
            content=f"[Team: {team_id}] [Author: {author_id}] {content}",
            organization_id=organization_id,
            workspace_id=workspace_id,
            user_id=author_id,
            context_hint=context_hint or f"team_{team_id}",
        )
        logger.info(f"[SHARED MEMORY STORE] Saved team memory entry '{rec.memory_id}' for team '{team_id}'")
        return rec

    def list_team_memories(
        self,
        organization_id: str,
        workspace_id: str,
        team_id: str,
    ) -> List[MemoryItemRecord]:
        """List team memories scoped to organization and workspace."""
        entries = self.memory_service.list_memory_entries(organization_id=organization_id, workspace_id=workspace_id)
        # Filter for team tag
        team_tag = f"[Team: {team_id}]"
        return [e for e in entries if team_tag in e.content]
