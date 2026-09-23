"""Knowledge Core & Organizational Intelligence Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.knowledge_platform.exceptions import KnowledgeNotFoundException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class KnowledgeType(str, Enum):
    DOCUMENT = "DOCUMENT"
    RECORD = "RECORD"
    FACT = "FACT"
    ENTITY = "ENTITY"
    RELATIONSHIP = "RELATIONSHIP"
    POLICY = "POLICY"
    PROCEDURE = "PROCEDURE"
    CONVERSATION = "CONVERSATION"
    WORKFLOW = "WORKFLOW"
    DECISION = "DECISION"
    EVENT = "EVENT"
    MEMORY = "MEMORY"
    INSIGHT = "INSIGHT"
    CUSTOM = "CUSTOM"


class KnowledgeStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    INGESTING = "INGESTING"
    ACTIVE = "ACTIVE"
    STALE = "STALE"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"


class KnowledgeSource(BaseModel):
    source_id: str = Field(default_factory=lambda: f"ksrc_{uuid.uuid4().hex[:10]}")
    name: str
    source_type: str = "DataFabric"
    tenant_id: str = "global"
    is_active: bool = True
    created_at: datetime = Field(default_factory=_now)


class KnowledgeVersion(BaseModel):
    version_id: str = Field(default_factory=lambda: f"kver_{uuid.uuid4().hex[:10]}")
    version_number: int = 1
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)


class KnowledgeItem(BaseModel):
    item_id: str = Field(default_factory=lambda: f"kitem_{uuid.uuid4().hex[:10]}")
    title: str
    knowledge_type: KnowledgeType = KnowledgeType.DOCUMENT
    status: KnowledgeStatus = KnowledgeStatus.ACTIVE
    tenant_id: str = "global"

    source_id: str = "src_default"
    confidence_score: float = 1.0
    classification: str = "INTERNAL"  # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED, SECRET

    current_version: KnowledgeVersion
    history: List[KnowledgeVersion] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)

    @property
    def content(self) -> str:
        return self.current_version.content


class KnowledgeManager:
    """Manages organizational knowledge items, controlled versioning, freshness status, and classification metadata."""

    def __init__(self) -> None:
        self._items: Dict[str, KnowledgeItem] = {}

    def create_knowledge_item(
        self,
        title: str,
        content: str,
        knowledge_type: KnowledgeType = KnowledgeType.DOCUMENT,
        tenant_id: str = "global",
        classification: str = "INTERNAL",
        confidence_score: float = 1.0,
        source_id: str = "src_default",
    ) -> KnowledgeItem:
        ver = KnowledgeVersion(version_number=1, content=content)
        item = KnowledgeItem(
            title=title,
            knowledge_type=knowledge_type,
            tenant_id=tenant_id,
            classification=classification,
            confidence_score=confidence_score,
            source_id=source_id,
            current_version=ver,
            history=[ver],
        )
        self._items[item.item_id] = item
        logger.info(
            f"[KNOWLEDGE MANAGER] Created knowledge item '{item.item_id}' ('{title}', {knowledge_type.value}) for tenant '{tenant_id}'"
        )
        return item

    def update_version(
        self, item_id: str, new_content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> KnowledgeItem:
        item = self.get_item(item_id)
        next_ver_num = len(item.history) + 1
        new_ver = KnowledgeVersion(version_number=next_ver_num, content=new_content, metadata=metadata or {})

        item.current_version = new_ver
        item.history.append(new_ver)
        item.updated_at = _now()
        logger.info(f"[KNOWLEDGE MANAGER] Updated knowledge item '{item_id}' -> Version {next_ver_num}")
        return item

    def mark_status(self, item_id: str, new_status: KnowledgeStatus) -> KnowledgeItem:
        item = self.get_item(item_id)
        item.status = new_status
        item.updated_at = _now()
        logger.info(f"[KNOWLEDGE MANAGER] Knowledge item '{item_id}' status updated -> {new_status.value}")
        return item

    def get_item(self, item_id: str) -> KnowledgeItem:
        item = self._items.get(item_id)
        if not item or item.status == KnowledgeStatus.DELETED:
            raise KnowledgeNotFoundException(item_id)
        return item

    def list_items(self, tenant_id: Optional[str] = None) -> List[KnowledgeItem]:
        res = [i for i in self._items.values() if i.status != KnowledgeStatus.DELETED]
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        return res
