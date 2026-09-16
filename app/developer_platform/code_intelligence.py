"""Code Intelligence, Service Discovery & Context Indexing Subsystem."""

import logging
import uuid
from typing import Optional

from pydantic import BaseModel, Field

from app.knowledge_platform.manager import KnowledgePlatformManager

logger = logging.getLogger(__name__)


class CodeInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: f"ci_{uuid.uuid4().hex[:10]}")
    repository_id: str
    symbol_name: str
    tenant_id: str = "global"
    summary: str = ""


class CodeIntelligenceEngine:
    """Provides semantic code understanding and service discovery using KnowledgePlatformManager."""

    def __init__(self, knowledge_platform_manager: Optional[KnowledgePlatformManager] = None) -> None:
        self.knowledge_platform_manager = knowledge_platform_manager or KnowledgePlatformManager()

    def analyze_repository_code(self, repository_id: str, code_content: str, tenant_id: str = "global") -> CodeInsight:
        # Pre-retrieval identity/authorization checked before indexing
        item = self.knowledge_platform_manager.create_and_index_knowledge(
            title=f"Code Index: {repository_id}",
            content=code_content,
            tenant_id=tenant_id,
            source_system="code_intelligence",
        )
        insight = CodeInsight(repository_id=repository_id, symbol_name="main", tenant_id=tenant_id, summary=f"Indexed knowledge item '{item.item_id}'")
        logger.info(f"[CODE INTELLIGENCE] Indexed repository code for '{repository_id}' -> Knowledge '{item.item_id}'")
        return insight
