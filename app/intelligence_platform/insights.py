"""Structured Evidence-Backed Insights Engine."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.intelligence_platform.context import IntelligenceContext, ContextEvidence
from app.intelligence_platform.exceptions import IntelligenceException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class InsightType(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    SECURITY = "SECURITY"
    COST = "COST"
    PERFORMANCE = "PERFORMANCE"
    QUALITY = "QUALITY"
    RELIABILITY = "RELIABILITY"
    COMPLIANCE = "COMPLIANCE"
    GOVERNANCE = "GOVERNANCE"
    PRODUCTIVITY = "PRODUCTIVITY"
    CUSTOMER_EXPERIENCE = "CUSTOMER_EXPERIENCE"
    MODEL_BEHAVIOR = "MODEL_BEHAVIOR"
    RESOURCE_UTILIZATION = "RESOURCE_UTILIZATION"


class InsightSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class InsightStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INVESTIGATING = "INVESTIGATING"
    MITIGATED = "MITIGATED"
    CLOSED = "CLOSED"


class InsightEvidence(BaseModel):
    evidence_id: str
    source: str
    summary: str
    confidence_score: float = 0.90


class Insight(BaseModel):
    insight_id: str = Field(default_factory=lambda: f"ins_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    insight_type: InsightType
    severity: InsightSeverity = InsightSeverity.MEDIUM
    status: InsightStatus = InsightStatus.ACTIVE
    observation: str
    recommended_next_step: str
    confidence: float = 0.90
    impact_score: float = 0.50
    affected_resources: List[str] = Field(default_factory=list)
    evidences: List[InsightEvidence] = Field(default_factory=list)
    provenance_source: str = "InsightManager"
    created_at: datetime = Field(default_factory=_now)


class InsightManager:
    """Generates evidence-backed structured insights."""

    def __init__(self) -> None:
        self._insights: Dict[str, Insight] = {}

    def generate_insight_from_context(
        self,
        tenant_id: str,
        insight_type: InsightType,
        observation: str,
        recommended_next_step: str,
        context: IntelligenceContext,
        severity: InsightSeverity = InsightSeverity.MEDIUM,
        impact_score: float = 0.50,
    ) -> Insight:
        if not context.evidences and not context.signals:
            raise IntelligenceException("Cannot generate insight without underlying context evidence.")

        insight_evidences = [
            InsightEvidence(
                evidence_id=ev.evidence_id,
                source=ev.source.value,
                summary=ev.title,
                confidence_score=ev.relevance_score,
            )
            for ev in context.evidences
        ]

        affected = [context.primary_resource_id] if context.primary_resource_id else []

        ins = Insight(
            tenant_id=tenant_id,
            insight_type=insight_type,
            severity=severity,
            observation=observation,
            recommended_next_step=recommended_next_step,
            impact_score=impact_score,
            affected_resources=affected,
            evidences=insight_evidences,
        )

        self._insights[ins.insight_id] = ins
        logger.info(f"[INSIGHT MANAGER] Generated {insight_type.value} insight '{ins.insight_id}' for tenant '{tenant_id}'")
        return ins

    def get_insight(self, insight_id: str, tenant_id: str) -> Insight:
        ins = self._insights.get(insight_id)
        if not ins or ins.tenant_id != tenant_id:
            raise IntelligenceException(f"Insight '{insight_id}' not found for tenant '{tenant_id}'.")
        return ins

    def list_insights(self, tenant_id: str, insight_type: Optional[InsightType] = None) -> List[Insight]:
        res = [i for i in self._insights.values() if i.tenant_id == tenant_id]
        if insight_type:
            res = [i for i in res if i.insight_type == insight_type]
        return res
