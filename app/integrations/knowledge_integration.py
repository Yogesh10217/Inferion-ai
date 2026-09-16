"""Knowledge Platform Integration Adapter."""

import logging
from typing import Optional

from app.knowledge_platform.manager import KnowledgePlatformManager

logger = logging.getLogger(__name__)


class KnowledgeIntegrationAdapter:
    """Ingests content from external SaaS systems into Knowledge Platform."""

    def __init__(self, knowledge_platform_manager: Optional[KnowledgePlatformManager] = None) -> None:
        self.knowledge_platform_manager = knowledge_platform_manager or KnowledgePlatformManager()

    def ingest_saas_content(self, source_name: str, title: str, content: str, tenant_id: str = "global") -> str:
        item = self.knowledge_platform_manager.create_and_index_knowledge(
            title=title,
            content=content,
            tenant_id=tenant_id,
            source_system=source_name,
        )
        logger.info(f"[KNOWLEDGE INTEGRATION ADAPTER] Ingested SaaS content from '{source_name}' -> Item '{item.item_id}'")
        return item.item_id
