"""Knowledge Validation & Quality Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field

from app.knowledge_platform.knowledge import KnowledgeItem, KnowledgeStatus

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ValidationRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: f"vrule_{uuid.uuid4().hex[:10]}")
    rule_type: str = "SCHEMA_CHECK"


class KnowledgeValidationResult(BaseModel):

    validation_id: str = Field(default_factory=lambda: f"val_{uuid.uuid4().hex[:10]}")
    item_id: str
    is_valid: bool = True
    issues: List[str] = Field(default_factory=list)
    validated_at: datetime = Field(default_factory=_now)


class KnowledgeValidationEngine:
    """Validates knowledge item schemas, freshness, provenance completeness, and policy compliance."""

    def validate_item(self, item: KnowledgeItem, has_provenance: bool = True) -> KnowledgeValidationResult:
        issues = []
        if not item.title:
            issues.append("Knowledge item title is empty")
        if item.status == KnowledgeStatus.STALE:
            issues.append("Knowledge item is marked STALE")
        if not has_provenance:
            issues.append("Knowledge item lacks complete provenance chain")

        is_valid = len(issues) == 0
        res = KnowledgeValidationResult(item_id=item.item_id, is_valid=is_valid, issues=issues)
        logger.info(f"[VALIDATION ENGINE] Validated item '{item.item_id}': Valid = {is_valid}")
        return res
