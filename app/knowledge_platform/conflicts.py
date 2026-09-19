"""Knowledge Conflict Detection & Governed Resolution Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.knowledge_platform.exceptions import KnowledgeConflictException
from app.knowledge_platform.knowledge import KnowledgeManager, KnowledgeStatus

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ConflictType(str, Enum):
    FACT_CONTRADICTION = "FACT_CONTRADICTION"
    VERSION_CONFLICT = "VERSION_CONFLICT"
    SOURCE_CONFLICT = "SOURCE_CONFLICT"
    TEMPORAL_CONFLICT = "TEMPORAL_CONFLICT"
    POLICY_CONFLICT = "POLICY_CONFLICT"
    AUTHORITY_CONFLICT = "AUTHORITY_CONFLICT"


class ConflictResolutionStrategy(str, Enum):
    SOURCE_AUTHORITY = "SOURCE_AUTHORITY"
    RECENCY = "RECENCY"
    CONFIDENCE = "CONFIDENCE"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    POLICY_RULE = "POLICY_RULE"
    RETAIN_MULTIPLE = "RETAIN_MULTIPLE"


class KnowledgeConflict(BaseModel):
    conflict_id: str = Field(default_factory=lambda: f"cnflct_{uuid.uuid4().hex[:10]}")
    item_a_id: str
    item_b_id: str
    conflict_type: ConflictType = ConflictType.FACT_CONTRADICTION
    tenant_id: str = "global"

    is_resolved: bool = False
    resolution_strategy: Optional[ConflictResolutionStrategy] = None
    resolved_item_id: Optional[str] = None

    detected_at: datetime = Field(default_factory=_now)
    resolved_at: Optional[datetime] = None


class KnowledgeConflictManager:
    """Detects knowledge conflicts, preserves conflicting versions, and applies governed resolution strategies."""

    def __init__(self, knowledge_manager: Optional[KnowledgeManager] = None) -> None:
        self.knowledge_manager = knowledge_manager or KnowledgeManager()
        self._conflicts: Dict[str, KnowledgeConflict] = {}

    def detect_conflict(
        self,
        item_a_id: str,
        item_b_id: str,
        conflict_type: ConflictType = ConflictType.FACT_CONTRADICTION,
        tenant_id: str = "global",
    ) -> KnowledgeConflict:
        cnflct = KnowledgeConflict(
            item_a_id=item_a_id,
            item_b_id=item_b_id,
            conflict_type=conflict_type,
            tenant_id=tenant_id,
        )
        self._conflicts[cnflct.conflict_id] = cnflct
        logger.warning(
            f"[CONFLICT MANAGER] Detected knowledge conflict '{cnflct.conflict_id}' between '{item_a_id}' and '{item_b_id}' ({conflict_type.value})"
        )
        return cnflct

    def resolve_conflict(
        self, conflict_id: str, strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.RECENCY
    ) -> KnowledgeConflict:
        cnflct = self._conflicts.get(conflict_id)
        if not cnflct:
            raise KnowledgeConflictException(conflict_id, "Conflict record not found")

        item_a = self.knowledge_manager.get_item(cnflct.item_a_id)
        item_b = self.knowledge_manager.get_item(cnflct.item_b_id)

        winner_id = cnflct.item_a_id
        if strategy == ConflictResolutionStrategy.RECENCY:
            winner_id = cnflct.item_a_id if item_a.updated_at >= item_b.updated_at else cnflct.item_b_id
        elif strategy == ConflictResolutionStrategy.CONFIDENCE:
            winner_id = cnflct.item_a_id if item_a.confidence_score >= item_b.confidence_score else cnflct.item_b_id

        # Preserve both versions; mark winner ACTIVE and loser SUPERSEDED
        loser_id = cnflct.item_b_id if winner_id == cnflct.item_a_id else cnflct.item_a_id
        self.knowledge_manager.mark_status(winner_id, KnowledgeStatus.ACTIVE)
        self.knowledge_manager.mark_status(loser_id, KnowledgeStatus.SUPERSEDED)

        cnflct.is_resolved = True
        cnflct.resolution_strategy = strategy
        cnflct.resolved_item_id = winner_id
        cnflct.resolved_at = _now()

        logger.info(
            f"[CONFLICT MANAGER] Resolved conflict '{conflict_id}' via strategy {strategy.value}: Winner '{winner_id}'"
        )
        return cnflct

    def list_conflicts(self, tenant_id: Optional[str] = None) -> List[KnowledgeConflict]:
        res = list(self._conflicts.values())
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        return res
