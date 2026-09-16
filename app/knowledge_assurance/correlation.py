"""Cross-domain knowledge correlation across decisions, incidents, controls, models, and costs."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field


class CorrelationType(str, Enum):
    DECISIONS = "DECISIONS"
    INCIDENTS = "INCIDENTS"
    CONTROLS = "CONTROLS"
    RISKS = "RISKS"
    MODELS = "MODELS"
    DATASETS = "DATASETS"
    OPERATIONS = "OPERATIONS"
    COSTS = "COSTS"


class CorrelationConfidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class CorrelationEvidence(BaseModel):
    reference_id: str
    target_entity_id: str
    target_entity_type: str
    correlation_reason: str


class KnowledgeCorrelation(BaseModel):
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    correlation_type: CorrelationType
    title: str
    summary: str
    correlated_domain: str = "CONTROLS"
    confidence: CorrelationConfidence = CorrelationConfidence.HIGH
    evidence: List[CorrelationEvidence] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeCorrelationManager:
    """Correlates knowledge references across cross-domain entities."""

    def __init__(self) -> None:
        self._correlations: Dict[str, KnowledgeCorrelation] = {}

    def correlate_knowledge(
        self,
        tenant_id: str,
        title: str,
        correlation_type: CorrelationType,
        evidence: List[CorrelationEvidence],
    ) -> KnowledgeCorrelation:
        corr = KnowledgeCorrelation(
            tenant_id=tenant_id,
            correlation_type=correlation_type,
            title=title,
            summary=f"Correlated {len(evidence)} knowledge references with {correlation_type.value}.",
            evidence=evidence,
        )
        self._correlations[corr.correlation_id] = corr
        return corr

    def correlate_resource(
        self,
        tenant_id: str,
        target_resource_id: str,
        resource_domain: str = "GLOBAL",
    ) -> List[KnowledgeCorrelation]:
        domains = ["CONTROLS", "RISKS", "SERVICES"]
        results: List[KnowledgeCorrelation] = []
        for dom in domains:
            corr = KnowledgeCorrelation(
                tenant_id=tenant_id,
                correlation_type=CorrelationType.CONTROLS if dom == "CONTROLS" else CorrelationType.RISKS,
                title=f"Cross-Domain Correlation with {dom}",
                summary=f"Resource '{target_resource_id}' correlated with {dom} domain.",
                correlated_domain=dom,
                evidence=[
                    CorrelationEvidence(
                        reference_id=f"ref-{target_resource_id}",
                        target_entity_id=f"{dom.lower()}-rel-1",
                        target_entity_type=dom,
                        correlation_reason=f"Semantic context match in {dom}",
                    )
                ],
            )
            results.append(corr)
            self._correlations[corr.correlation_id] = corr
        return results

    def list_correlations(self, tenant_id: str) -> List[KnowledgeCorrelation]:
        return [c for c in self._correlations.values() if c.tenant_id == tenant_id]
