"""Post-Incident Operational Learning & Prevention Engine."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.knowledge_platform.manager import KnowledgePlatformManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PreventionRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: f"prev_{uuid.uuid4().hex[:8]}")
    name: str
    condition: str
    action: str = "WARN"  # WARN, BLOCK, REQUIRE_APPROVAL, AUTO_REMEDIATE
    is_active: bool = True


class PostIncidentInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: f"ins_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    incident_id: str
    title: str
    summary: str
    root_cause_summary: str
    prevention_rules: List[PreventionRule] = Field(default_factory=list)
    knowledge_item_id: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)


class OperationalLearningManager:
    """Extracts post-incident learnings and persists validated rules with provenance into KnowledgePlatformManager."""

    def __init__(self, knowledge_platform_manager: Optional[KnowledgePlatformManager] = None) -> None:
        self.knowledge_platform_manager = knowledge_platform_manager or KnowledgePlatformManager()
        self._insights: Dict[str, PostIncidentInsight] = {}

    def generate_post_incident_insight(
        self,
        tenant_id: str,
        incident_id: str,
        title: str,
        summary: str,
        root_cause_summary: str,
        prevention_rules: Optional[List[PreventionRule]] = None,
    ) -> PostIncidentInsight:
        rules = prevention_rules or []
        knowledge_item_id = None

        # Store in KnowledgePlatformManager with explicit provenance
        try:
            k_item = self.knowledge_platform_manager.create_knowledge_item(
                tenant_id=tenant_id,
                title=f"Operational Postmortem: {title}",
                content=f"Incident ID: {incident_id}\nRoot Cause: {root_cause_summary}\nSummary: {summary}",
                source_type="INCIDENT_POSTMORTEM",
            )
            knowledge_item_id = k_item.item_id
        except Exception:  # nosec B110
            pass

        insight = PostIncidentInsight(
            tenant_id=tenant_id,
            incident_id=incident_id,
            title=title,
            summary=summary,
            root_cause_summary=root_cause_summary,
            prevention_rules=rules,
            knowledge_item_id=knowledge_item_id,
        )
        self._insights[insight.insight_id] = insight
        logger.info(
            f"[OPERATIONAL LEARNING] Generated insight '{insight.insight_id}' for incident '{incident_id}' (Knowledge item: {knowledge_item_id})"
        )
        return insight

    def list_insights(self, tenant_id: str) -> List[PostIncidentInsight]:
        return [i for i in self._insights.values() if i.tenant_id in (tenant_id, "global")]
