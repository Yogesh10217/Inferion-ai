"""Knowledge Freshness & Data Fabric CDC Event Integration Subsystem."""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.knowledge_platform.knowledge import KnowledgeManager, KnowledgeStatus

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class StalenessReason(str, Enum):
    STALE_SOURCE = "STALE_SOURCE"
    OUTDATED_VERSION = "OUTDATED_VERSION"
    SOURCE_CHANGED = "SOURCE_CHANGED"
    SCHEMA_CHANGED = "SCHEMA_CHANGED"
    CONTRADICTORY_INFORMATION = "CONTRADICTORY_INFORMATION"
    EXPIRED_INFORMATION = "EXPIRED_INFORMATION"


class KnowledgeFreshness(BaseModel):
    item_id: str
    is_stale: bool = False
    last_evaluated_at: datetime = Field(default_factory=_now)


class StalenessPolicy(BaseModel):
    policy_name: str = "DEFAULT"
    max_age_days: int = 30


class FreshnessEvaluator:

    """Evaluates knowledge staleness and handles Data Fabric CDC events by marking items STALE."""

    def __init__(self, knowledge_manager: Optional[KnowledgeManager] = None) -> None:
        self.knowledge_manager = knowledge_manager or KnowledgeManager()

    def process_cdc_event(self, source_id: str, tenant_id: str = "global", reason: StalenessReason = StalenessReason.SOURCE_CHANGED) -> List[str]:
        items = self.knowledge_manager.list_items(tenant_id)
        stale_item_ids = []

        for item in items:
            if item.source_id == source_id:
                self.knowledge_manager.mark_status(item.item_id, KnowledgeStatus.STALE)
                stale_item_ids.append(item.item_id)
                logger.warning(f"[FRESHNESS EVALUATOR] Marked knowledge item '{item.item_id}' as STALE due to CDC event on source '{source_id}' ({reason.value})")

        return stale_item_ids
